#!/usr/bin/env python3
"""Serial console helper for the IONIQ 5 Gen5W bench unit.

The kernel command line recovered from the plaintext boot container is:

    console=ttyS2,115200n8
    earlycon=uart8250,mmio32,0xfc000000,115200n8

So the debug console is 115200 8N1 on ``ttyS2``. This tool drives a USB-UART
adapter attached to the board's debug pads and records what the unit prints.

Subcommands
-----------
    list                 enumerate serial ports with USB VID/PID where known
    capture              record everything the unit prints to a timestamped log
    send                 send one line and record the response
    monitor              capture and, if ``--send`` is given, send lines on a timer

Nothing here writes to the unit's storage. It is a read-mostly console: the
``send`` path exists so a bootloader or login prompt can be answered.

Usage
-----
    python3 bench_serial.py list
    python3 bench_serial.py capture --port /dev/tty.usbserial-XXXX -o work/boot.log
    python3 bench_serial.py send --port /dev/tty.usbserial-XXXX "help"
    python3 bench_serial.py capture --port ... --hexdump

If the port is not given, the tool lists candidates and exits rather than
guessing.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

try:
    import serial
    from serial.tools import list_ports
except ImportError:  # pragma: no cover
    print("pyserial is required: python3 -m pip install pyserial", file=sys.stderr)
    raise SystemExit(2)

DEFAULT_BAUD = 115200


def enumerate_ports() -> List[dict]:
    out = []
    for p in list_ports.comports():
        out.append(
            {
                "device": p.device,
                "description": p.description,
                "vid": f"0x{p.vid:04x}" if p.vid is not None else None,
                "pid": f"0x{p.pid:04x}" if p.pid is not None else None,
                "serial": p.serial_number,
            }
        )
    return out


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]


def open_port(port: str, baud: int, timeout: float):
    return serial.Serial(
        port=port,
        baudrate=baud,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
        rtscts=False,
        dsrdtr=False,
        xonxoff=False,
    )


def capture(port: str, baud: int, out: Optional[Path], duration: Optional[float],
            hexdump: bool, quiet: bool) -> int:
    log = open(out, "a", encoding="utf-8") if out else None
    started = time.monotonic()
    buf = b""
    try:
        with open_port(port, baud, 0.2) as ser:
            if not quiet:
                print(f"# capture {port} {baud} 8N1  (Ctrl-C to stop)", file=sys.stderr)
            while True:
                if duration is not None and time.monotonic() - started > duration:
                    break
                chunk = ser.read(4096)
                if not chunk:
                    continue
                buf += chunk
                # Emit complete-ish lines, keep the remainder for next round.
                while b"\n" in buf:
                    line, _, buf = buf.partition(b"\n")
                    text = line.decode("utf-8", "replace").rstrip("\r")
                    stamped = f"[{_stamp()}] {text}"
                    if not quiet:
                        print(stamped)
                    if log:
                        log.write(stamped + "\n")
                        log.flush()
                if hexdump and buf:
                    if not quiet:
                        print(f"[{_stamp()}] HEX {buf.hex()}")
                    if log:
                        log.write(f"[{_stamp()}] HEX {buf.hex()}\n")
                        log.flush()
                    buf = b""
    except KeyboardInterrupt:
        pass
    finally:
        if buf:
            text = buf.decode("utf-8", "replace")
            if not quiet:
                print(f"[{_stamp()}] {text}")
            if log:
                log.write(f"[{_stamp()}] {text}\n")
        if log:
            log.close()
    return 0


def send(port: str, baud: int, line: str, out: Optional[Path], read_for: float) -> int:
    log = open(out, "a", encoding="utf-8") if out else None
    try:
        with open_port(port, baud, 0.2) as ser:
            payload = (line + "\r\n").encode()
            ser.write(payload)
            ser.flush()
            if log:
                log.write(f"[{_stamp()}] TX {line}\n")
            deadline = time.monotonic() + read_for
            buf = b""
            while time.monotonic() < deadline:
                chunk = ser.read(4096)
                if chunk:
                    buf += chunk
            text = buf.decode("utf-8", "replace")
            print(text, end="")
            if log:
                for l in text.splitlines():
                    log.write(f"[{_stamp()}] RX {l}\n")
    finally:
        if log:
            log.close()
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="enumerate serial ports")

    for name, help_text in (("capture", "record console output"),
                            ("send", "send one line and record the reply")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("line", nargs="?", help="line to send (send only)")
        p.add_argument("--port", required=False)
        p.add_argument("--baud", type=int, default=DEFAULT_BAUD)
        p.add_argument("-o", "--out", type=Path, help="append to this log file")
        p.add_argument("--duration", type=float, help="stop after N seconds")
        p.add_argument("--read-for", type=float, default=3.0, help="read window after send")
        p.add_argument("--hexdump", action="store_true")
        p.add_argument("--quiet", action="store_true")

    args = ap.parse_args(argv)

    if args.cmd == "list":
        ports = enumerate_ports()
        if not ports:
            print("no serial ports found")
            return 0
        for p in ports:
            print(f"{p['device']:40} {p['description']}  vid={p['vid']} pid={p['pid']} sn={p['serial']}")
        return 0

    if not args.port:
        ports = enumerate_ports()
        print("no --port given. candidates:", file=sys.stderr)
        for p in ports:
            print(f"  {p['device']:40} {p['description']}", file=sys.stderr)
        return 2

    if args.cmd == "capture":
        return capture(args.port, args.baud, args.out, args.duration, args.hexdump, args.quiet)
    if args.cmd == "send":
        if not args.line:
            print("send requires a line argument", file=sys.stderr)
            return 2
        return send(args.port, args.baud, args.line, args.out, args.read_for)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
