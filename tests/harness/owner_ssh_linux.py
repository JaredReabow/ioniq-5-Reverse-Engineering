#!/usr/bin/env python3
"""Exercise the exact static owner server inside a disposable Linux container.

Run only in the fixture container: this deliberately changes its root account
and '/' permissions to reproduce the OEM authentication conditions. No actual
owner password, host private key, or vehicle connection is used.
"""
from __future__ import annotations

import crypt
import os
from pathlib import Path
import pty
import select
import socket
import subprocess
import sys
import tempfile
import time


def owner_ssh_linux_main() -> None:
    """Require key/password auth, PTY/SCP, and negative credential checks."""
    if not Path("/.dockerenv").exists() or os.environ.get("IONIQ_AUTH_FIXTURE") != "1":
        raise SystemExit("This fixture is restricted to its disposable Docker container")
    binary = Path("/artifact/dropbearmulti")
    temporary = tempfile.TemporaryDirectory(prefix="ioniq-auth-", dir="/run")
    root = Path(temporary.name)
    root.chmod(0o700)
    auth = root / ".ssh"
    auth.mkdir(mode=0o700)
    key = root / "client"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
    (auth / "authorized_keys").write_text(
        "no-port-forwarding,no-agent-forwarding,no-X11-forwarding " + key.with_suffix(".pub").read_text())
    (auth / "authorized_keys").chmod(0o600)
    host = root / "hostkey"
    subprocess.run([str(binary), "dropbearkey", "-t", "ed25519", "-f", str(host)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    password = "Fixture-only-Password-7"
    hashed = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))
    passwd = Path("/etc/passwd")
    lines = passwd.read_text().splitlines()
    passwd.write_text("\n".join(
        f"root:{hashed}:0:0:Owner:{root}:/bin/sh" if line.startswith("root:") else line
        for line in lines) + "\n")
    Path("/etc/shells").write_text("/bin/sh\n")
    os.chmod("/", 0o775)
    scp = Path("/usr/bin/scp")
    scp.rename("/usr/bin/scp-client")
    scp.symlink_to(binary)
    server_link = root / "dropbear"
    server_link.symlink_to(binary)
    log = (root / "server.log").open("wb")
    server = subprocess.Popen([
        str(server_link), "-F", "-m", "-l", "lo", "-p", "127.0.0.1:22222",
        "-D", str(auth), "-r", str(host), "-P", str(root / "server.pid"),
    ], stdout=log, stderr=subprocess.STDOUT)
    base = ["ssh", "-F", "/dev/null", "-p", "22222", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=3",
            "-o", "IdentitiesOnly=yes", "-o", "LogLevel=ERROR"]

    def run(arguments: list[str], *, ok: bool = True, keep_stdin: bool = False) -> subprocess.CompletedProcess:
        if keep_stdin:
            # A real interactive client keeps its input open. Immediate EOF can
            # hang up a PTY before the remote command produces any output.
            process = subprocess.Popen(arguments, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                code = process.wait(timeout=12)
                result = subprocess.CompletedProcess(arguments, code, process.stdout.read(), process.stderr.read())
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=2)
                for stream in (process.stdin, process.stdout, process.stderr):
                    stream.close()
        else:
            result = subprocess.run(arguments, capture_output=True, text=True, timeout=12)
        if (result.returncode == 0) != ok:
            raise AssertionError(f"Unexpected command result {result.returncode}: {result.stderr} {result.stdout}")
        return result

    def password_login(value: str) -> tuple[int, str]:
        master, slave = pty.openpty()

        def controlling_terminal() -> None:
            os.setsid()
            import fcntl
            import termios
            fcntl.ioctl(0, termios.TIOCSCTTY, 0)

        process = subprocess.Popen(base + ["-o", "PubkeyAuthentication=no", "-o",
            "PreferredAuthentications=password", "-o", "NumberOfPasswordPrompts=1",
            "root@127.0.0.1", "printf PASSWORD_OK"], stdin=slave, stdout=slave,
            stderr=slave, preexec_fn=controlling_terminal)
        os.close(slave)
        transcript = b""
        sent = False
        deadline = time.monotonic() + 12
        try:
            while time.monotonic() < deadline:
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    try:
                        data = os.read(master, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    transcript += data
                    if b"password:" in transcript.lower() and not sent:
                        os.write(master, value.encode() + b"\n")
                        sent = True
                if process.poll() is not None:
                    break
            if process.poll() is None:
                process.kill()
                raise AssertionError("Password fixture timed out")
            return process.wait(timeout=2), transcript.decode(errors="replace")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
            os.close(master)

    try:
        deadline = time.monotonic() + 5
        while True:
            try:
                with socket.create_connection(("127.0.0.1", 22222), timeout=0.2):
                    break
            except OSError:
                if server.poll() is not None or time.monotonic() >= deadline:
                    raise AssertionError("Dropbear failed to listen")
                time.sleep(0.05)
        keyed = base + ["-i", str(key), "-o", "BatchMode=yes"]
        assert run(keyed + ["root@127.0.0.1", "printf KEY_OK"]).stdout == "KEY_OK"
        print("PASS existing-home key authentication with / mode 0775", flush=True)
        for value, expected in ((password, True), ("wrong", False), ("", False)):
            code, output = password_login(value)
            assert (code == 0 and "PASSWORD_OK" in output) == expected, "password policy failure"
        print("PASS correct password; wrong and blank passwords rejected", flush=True)
        other = root / "wrongkey"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(other)], check=True)
        run(base + ["-i", str(other), "-o", "BatchMode=yes", "root@127.0.0.1", "true"], ok=False)
        print("PASS unrelated key rejected", flush=True)
        terminal = run(keyed + ["-tt", "root@127.0.0.1", "tty; test -t 0 && printf PTY_OK"], keep_stdin=True)
        assert "PTY_OK" in terminal.stdout
        print("PASS interactive PTY", flush=True)
        # Invoke the distro SCP client retained under a distinct name by the runner.
        original = root / "source.txt"
        original.write_text("owner-scp-roundtrip\n")
        common = ["/usr/bin/scp-client", "-O", "-P", "22222", "-i", str(key),
                  "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                  "-o", "UserKnownHostsFile=/dev/null"]
        run(common + [str(original), f"root@127.0.0.1:{root}/copy.txt"])
        run(common + [f"root@127.0.0.1:{root}/copy.txt", str(root / "returned.txt")])
        assert (root / "returned.txt").read_bytes() == original.read_bytes()
        print("PASS legacy SCP upload and download", flush=True)
        run(keyed + ["-o", "ExitOnForwardFailure=yes", "-N", "-R",
                      "127.0.0.1:22223:127.0.0.1:22222", "root@127.0.0.1"], ok=False)
        print("PASS remote forwarding refused", flush=True)
    finally:
        server.terminate()
        server.wait(timeout=5)
        log.close()
        if sys.exc_info()[0] is not None:
            print((root / "server.log").read_text(errors="replace"), file=sys.stderr)
        temporary.cleanup()


if __name__ == "__main__":
    owner_ssh_linux_main()
