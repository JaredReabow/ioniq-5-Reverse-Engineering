"use strict";

const loginView = document.querySelector("#login");
const consoleView = document.querySelector("#console");
const loginForm = document.querySelector("#login-form");
const passwordInput = document.querySelector("#password");
const loginButton = document.querySelector("#login-button");
const loginError = document.querySelector("#login-error");
const connectionLabel = document.querySelector("#connection");
const reconnectButton = document.querySelector("#reconnect");
const logoutButton = document.querySelector("#logout");
const terminalElement = document.querySelector("#terminal");
const terminalInput = document.querySelector("#terminal-input");
const decoder = new TextDecoder();

class SafeTerminal {
  constructor() {
    this.columns = 100;
    this.rows = 30;
    this.cursorRow = 0;
    this.cursorColumn = 0;
    this.lines = Array.from({ length: this.rows }, () => []);
    this.escape = "";
    this.state = "text";
  }

  resize(columns, rows) {
    const nextLines = Array.from({ length: rows }, (_, row) =>
      (this.lines[row] || []).slice(0, columns)
    );
    this.columns = columns;
    this.rows = rows;
    this.lines = nextLines;
    this.cursorRow = Math.min(this.cursorRow, rows - 1);
    this.cursorColumn = Math.min(this.cursorColumn, columns - 1);
    this.render();
  }

  line() {
    while (this.lines.length <= this.cursorRow) this.lines.push([]);
    return this.lines[this.cursorRow];
  }

  advance() {
    this.cursorColumn += 1;
    if (this.cursorColumn >= this.columns) {
      this.cursorColumn = 0;
      this.newline();
    }
  }

  newline() {
    this.cursorRow += 1;
    if (this.cursorRow >= this.rows) {
      this.lines.shift();
      this.lines.push([]);
      this.cursorRow = this.rows - 1;
    }
  }

  csi(sequence) {
    const final = sequence.slice(-1);
    const raw = sequence.slice(0, -1).replace(/^[?>!]/, "");
    const values = raw.split(";").map((value) => Number.parseInt(value, 10));
    const first = Number.isFinite(values[0]) ? values[0] : 1;
    switch (final) {
      case "A": this.cursorRow = Math.max(0, this.cursorRow - first); break;
      case "B": this.cursorRow = Math.min(this.rows - 1, this.cursorRow + first); break;
      case "C": this.cursorColumn = Math.min(this.columns - 1, this.cursorColumn + first); break;
      case "D": this.cursorColumn = Math.max(0, this.cursorColumn - first); break;
      case "G": this.cursorColumn = Math.max(0, Math.min(this.columns - 1, first - 1)); break;
      case "H":
      case "f": {
        const row = Number.isFinite(values[0]) ? values[0] : 1;
        const column = Number.isFinite(values[1]) ? values[1] : 1;
        this.cursorRow = Math.max(0, Math.min(this.rows - 1, row - 1));
        this.cursorColumn = Math.max(0, Math.min(this.columns - 1, column - 1));
        break;
      }
      case "J":
        if (first === 2 || raw === "" || raw === "3") {
          this.lines = Array.from({ length: this.rows }, () => []);
          this.cursorRow = 0;
          this.cursorColumn = 0;
        }
        break;
      case "K":
        this.line().splice(this.cursorColumn);
        break;
      default:
        break;
    }
  }

  consume(character) {
    if (this.state === "escape") {
      if (character === "[") {
        this.state = "csi";
        this.escape = "";
      } else if (character === "]") {
        this.state = "osc";
      } else {
        this.state = "text";
      }
      return;
    }
    if (this.state === "csi") {
      this.escape += character;
      if (/[@-~]/.test(character)) {
        this.csi(this.escape);
        this.state = "text";
        this.escape = "";
      }
      return;
    }
    if (this.state === "osc") {
      this.escape += character;
      if (character === "\u0007" || this.escape.endsWith("\u001b\\")) {
        this.state = "text";
        this.escape = "";
      }
      return;
    }
    if (character === "\u001b") {
      this.state = "escape";
      return;
    }
    if (character === "\r") {
      this.cursorColumn = 0;
      return;
    }
    if (character === "\n") {
      this.newline();
      return;
    }
    if (character === "\b") {
      this.cursorColumn = Math.max(0, this.cursorColumn - 1);
      return;
    }
    if (character === "\t") {
      const next = (Math.floor(this.cursorColumn / 8) + 1) * 8;
      while (this.cursorColumn < Math.max(next, 1)) {
        this.line()[this.cursorColumn] = " ";
        this.cursorColumn += 1;
      }
      return;
    }
    const code = character.codePointAt(0);
    if (code < 32 || code === 127) return;
    const line = this.line();
    while (line.length < this.cursorColumn) line.push(" ");
    line[this.cursorColumn] = character;
    this.advance();
  }

  write(text) {
    for (const character of text) this.consume(character);
    this.render();
  }

  render() {
    terminalElement.textContent = this.lines
      .map((line) => line.join("").replace(/\s+$/u, ""))
      .join("\n");
  }
}

const terminal = new SafeTerminal();
let csrf = "";
let socket = null;
let socketGeneration = 0;

function setView(authenticated) {
  loginView.classList.toggle("hidden", authenticated);
  consoleView.classList.toggle("hidden", !authenticated);
}

function connection(text, online) {
  connectionLabel.textContent = text;
  connectionLabel.classList.toggle("online", online);
}

async function requestJSON(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  const method = (options.method || "GET").toUpperCase();
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    headers.set("X-Owner-CSRF", csrf);
  }
  const response = await fetch(path, {
    cache: "no-store",
    credentials: "same-origin",
    ...options,
    headers,
  });
  if (!response.ok) {
    const message = (await response.text()).trim();
    throw new Error(message || `HTTP ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function sendInput(text) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(new TextEncoder().encode(text));
  }
}

function terminalSize() {
  const style = getComputedStyle(terminalElement);
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");
  context.font = style.font;
  const characterWidth = Math.max(6, context.measureText("M").width);
  const lineHeight = Math.max(12, Number.parseFloat(style.lineHeight));
  const usableWidth = terminalElement.clientWidth - 2;
  const usableHeight = terminalElement.clientHeight - 2;
  return {
    cols: Math.max(20, Math.min(300, Math.floor(usableWidth / characterWidth))),
    rows: Math.max(5, Math.min(120, Math.floor(usableHeight / lineHeight))),
  };
}

function fitTerminal() {
  const size = terminalSize();
  terminal.resize(size.cols, size.rows);
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "resize", ...size }));
  }
}

function disconnect() {
  socketGeneration += 1;
  if (socket) {
    socket.onclose = null;
    socket.close();
    socket = null;
  }
  connection("disconnected", false);
  reconnectButton.classList.remove("hidden");
}

function connectSocket(ticket) {
  socketGeneration += 1;
  const generation = socketGeneration;
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  connection("connecting", false);
  reconnectButton.classList.add("hidden");
  socket = new WebSocket(
    `${protocol}//${location.host}/terminal`,
    ["owner-terminal.v1", `owner-ticket.${ticket}`]
  );
  socket.binaryType = "arraybuffer";
  socket.onopen = () => {
    if (generation !== socketGeneration) return;
    connection("connected", true);
    fitTerminal();
    terminalInput.focus();
  };
  socket.onmessage = (event) => {
    if (generation !== socketGeneration) return;
    if (event.data instanceof ArrayBuffer) {
      terminal.write(decoder.decode(new Uint8Array(event.data), { stream: true }));
      return;
    }
    try {
      const control = JSON.parse(event.data);
      if (control.type === "error" && typeof control.message === "string") {
        connection(control.message, false);
      }
    } catch (_) {
      disconnect();
    }
  };
  socket.onerror = () => {
    if (generation === socketGeneration) connection("connection error", false);
  };
  socket.onclose = () => {
    if (generation !== socketGeneration) return;
    socket = null;
    connection("disconnected", false);
    reconnectButton.classList.remove("hidden");
  };
}

async function loadStatus() {
  const status = await requestJSON("/api/status");
  csrf = status.csrf || csrf;
  setView(status.authenticated);
  if (status.authenticated) {
    fitTerminal();
    connectSocket(status.ticket);
  } else {
    passwordInput.focus();
  }
  return status;
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginButton.disabled = true;
  loginError.textContent = "";
  try {
    await requestJSON("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: passwordInput.value }),
    });
    passwordInput.value = "";
    await loadStatus();
  } catch (_) {
    loginError.textContent = "Authentication failed.";
    passwordInput.select();
  } finally {
    loginButton.disabled = false;
  }
});

// The browser's default pointer focus runs after pointerdown. Redirect from
// the focus event instead, so mouse clicks and Tab both retain keyboard input.
terminalElement.addEventListener("focus", () => terminalInput.focus());
terminalInput.addEventListener("paste", (event) => {
  event.preventDefault();
  sendInput(event.clipboardData.getData("text"));
});
terminalInput.addEventListener("keydown", (event) => {
  const keySequences = {
    Enter: "\r",
    Backspace: "\u007f",
    Tab: "\t",
    Escape: "\u001b",
    ArrowUp: "\u001b[A",
    ArrowDown: "\u001b[B",
    ArrowRight: "\u001b[C",
    ArrowLeft: "\u001b[D",
    Home: "\u001b[H",
    End: "\u001b[F",
    Delete: "\u001b[3~",
    PageUp: "\u001b[5~",
    PageDown: "\u001b[6~",
  };
  if (event.key === "c" && (event.ctrlKey || event.metaKey) && event.shiftKey) return;
  let output = keySequences[event.key] || "";
  if ((event.ctrlKey || event.metaKey) && event.key.length === 1) {
    output = String.fromCharCode(event.key.toUpperCase().charCodeAt(0) - 64);
  } else if (event.altKey && event.key.length === 1) {
    output = `\u001b${event.key}`;
  } else if (!output && event.key.length === 1 && !event.ctrlKey && !event.metaKey) {
    output = event.key;
  }
  if (output) {
    event.preventDefault();
    sendInput(output);
  }
});
window.addEventListener("resize", fitTerminal);

reconnectButton.addEventListener("click", async () => {
  reconnectButton.disabled = true;
  try {
    await loadStatus();
  } catch (_) {
    connection("status unavailable", false);
  } finally {
    reconnectButton.disabled = false;
  }
});

logoutButton.addEventListener("click", async () => {
  logoutButton.disabled = true;
  try {
    disconnect();
    await requestJSON("/api/logout", { method: "POST" });
  } finally {
    csrf = "";
    setView(false);
    connection("disconnected", false);
    logoutButton.disabled = false;
    await loadStatus().catch(() => {});
  }
});

setInterval(() => {
  if (!consoleView.classList.contains("hidden")) {
    requestJSON("/api/status").then((status) => {
      csrf = status.csrf || csrf;
      if (!status.authenticated) {
        disconnect();
        setView(false);
        passwordInput.focus();
      }
    }).catch(() => connection("link lost", false));
  }
}, 30000);

loadStatus().catch(() => {
  setView(false);
  loginError.textContent = "Console unavailable.";
});
