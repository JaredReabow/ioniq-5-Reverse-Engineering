// Real-browser regression for the local HTTPS recovery-terminal fixture.
// NODE_PATH supplies Playwright; the password is read privately, never logged.
const fs = require("node:fs");
const assert = require("node:assert/strict");
const { chromium } = require("playwright");

async function ownerWebBrowserMain() {
  const base = new URL(process.argv[2]);
  assert.equal(base.protocol, "https:");
  assert.equal(base.hostname, "127.0.0.1", "Only the local test server is allowed");
  const password = fs.readFileSync(process.argv[3], "utf8").replace(/\r?\n$/, "");
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROME_BIN || undefined,
    // The loopback-only fixture uses the retained self-signed certificate;
    // Chrome's WebSocket verifier needs this in addition to the context option.
    args: ["--ignore-certificate-errors"],
  });
  let stage = "loading the login page";
  try {
    const page = await browser.newPage({ ignoreHTTPSErrors: true });
    page.setDefaultTimeout(15000);
    const errors = [];
    const sockets = [];
    page.on("pageerror", error => errors.push(error.message));
    page.on("websocket", socket => {
      const record = { closed: false };
      socket.on("close", () => { record.closed = true; });
      sockets.push(record);
    });
    await page.goto(base.href);
    await page.locator("#password").fill(password);
    await page.locator("#login-button").click();
    stage = "connecting the authenticated PTY";
    await page.locator("#console").waitFor({ state: "visible" });
    await page.waitForFunction(() => document.querySelector("#connection").textContent === "connected");
    await page.locator("#terminal").click();
    assert.equal(await page.evaluate(() => document.activeElement.id), "terminal-input",
      "A normal terminal click must retain keyboard input");
    // Split the marker so echoed input cannot masquerade as shell output.
    await page.keyboard.type("printf '%s%s\\n' OWNER_WEB_ BROWSER_OK");
    await page.keyboard.press("Enter");
    stage = "executing the PTY command";
    await page.waitForFunction(() => document.querySelector("#terminal").textContent.includes("OWNER_WEB_BROWSER_OK"));
    assert.equal(sockets.length, 1);
    const logoutResponse = page.waitForResponse(response =>
      new URL(response.url()).pathname === "/api/logout" && response.request().method() === "POST");
    await page.locator("#logout").click();
    stage = "invalidating the login session";
    assert.equal((await logoutResponse).status(), 204);
    await page.locator("#login").waitFor({ state: "visible" });
    assert.equal(await page.locator("#console").isVisible(), false);
    assert.equal((await (await page.request.get(new URL("/api/status", base).href)).json()).authenticated, false);
    await page.reload();
    await page.locator("#login").waitFor({ state: "visible" });
    assert.equal(await page.locator("#console").isVisible(), false);
    assert.ok(sockets.every(socket => socket.closed), "The old terminal socket must close");
    assert.equal(sockets.length, 1, "Logout must not silently reopen a root terminal");
    assert.deepEqual(errors, []);
    console.log("PASS browser login, PTY command, logout, closed socket, and unauthenticated reload");
  } catch (error) {
    throw new Error(`${stage}: ${error.message}`);
  } finally {
    await browser.close();
  }
}

ownerWebBrowserMain().catch(error => {
  console.error(error.message);
  process.exitCode = 1;
});
