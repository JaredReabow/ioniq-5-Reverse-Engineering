#!/usr/bin/env python3
"""Orchestrate a read-only assessment of the IONIQ 5 bench unit.

Runs the sibling tools in a fixed, safe order and writes one report:

    1. serial capture   (optional, --serial)  -> boot log
    2. network surface  (optional, --host)    -> open ports, banners, TLS
    3. rootfs survey    (optional, --rootfs)  -> accounts, SMACK, units, caps
    4. boot container   (optional, --image)   -> header, command line, signature

Every step is read-only. Nothing here writes to the unit, mounts a filesystem
read-write, or modifies a firmware image. Steps are independent: pass any
combination, and the report records which ran and which were skipped.

Usage
-----
    python3 bench_assess.py --out work/bench --serial /dev/tty.usbserial-1234
    python3 bench_assess.py --out work/bench --host 192.168.1.50 \\
        --image ~/Downloads/NaU/IONIQ5_EU/HU/images/iasImage_1280_sub
    python3 bench_assess.py --out work/bench --rootfs /Volumes/rootfs

Authorisation: the network step only runs against a host you own. Keep the unit
on an isolated AP/VLAN.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent


def run(cmd: List[str], timeout: int = 900) -> Dict[str, object]:
    started = datetime.now(timezone.utc)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-20000:],
            "stderr": proc.stderr[-5000:],
            "duration_s": round((datetime.now(timezone.utc) - started).total_seconds(), 2),
        }
    except subprocess.TimeoutExpired:
        return {"command": cmd, "returncode": None, "error": "timeout", "duration_s": timeout}
    except OSError as exc:
        return {"command": cmd, "returncode": None, "error": f"{type(exc).__name__}: {exc}"}


def step_serial(port: str, out: Path, baud: int, duration: float) -> Dict[str, object]:
    log = out / "boot.log"
    result = run([sys.executable, str(HERE / "bench_serial.py"), "capture",
                  "--port", port, "--baud", str(baud),
                  "--duration", str(duration), "-o", str(log), "--quiet"], timeout=int(duration) + 60)
    result["artifact"] = str(log)
    if log.is_file():
        lines = log.read_text(errors="replace").splitlines()
        result["log_lines"] = len(lines)
        result["tail"] = lines[-15:]
    return result


def step_network(host: str, out: Path) -> Dict[str, object]:
    report = out / "network.json"
    result = run([sys.executable, str(HERE / "net_surface.py"), "--target", host,
                  "--authorised", "--json", str(report)])
    result["artifact"] = str(report)
    if report.is_file():
        data = json.loads(report.read_text())
        result["open_ports"] = sorted(int(p) for p in data.get("ports", {}))
    return result


def step_rootfs(rootfs: Path, out: Path) -> Dict[str, object]:
    report = out / "rootfs.json"
    result = run([sys.executable, str(HERE / "dump_survey.py"), "--root", str(rootfs),
                  "--json", str(report), "--quiet"])
    result["artifact"] = str(report)
    if report.is_file():
        data = json.loads(report.read_text())
        sections = data.get("sections", {})
        accounts = sections.get("accounts", {})
        result["empty_password_accounts"] = [
            a["name"] for a in accounts.get("shadow", []) if a.get("state") == "empty"
        ]
        result["setuid_count"] = len(sections.get("privilege", {}).get("setuid", []))
        result["keystore_node_present"] = "/dev/keystore" in sections.get("debug", {}).get("present", [])
    return result


def step_image(image: Path) -> Dict[str, object]:
    info = run([sys.executable, str(HERE / "ipk_tool.py"), "info", str(image), "--json"])
    verify = run([sys.executable, str(HERE / "ipk_tool.py"), "verify", str(image), "--json"])
    out: Dict[str, object] = {"info": info, "verify": verify,
                              "returncode": verify.get("returncode")}
    try:
        out["parsed"] = json.loads(info["stdout"])  # type: ignore[index]
        verdict = json.loads(verify["stdout"])  # type: ignore[index]
        out["signature_ok"] = verdict.get("ok")
        out["modulus_sha256"] = verdict.get("modulus_sha256")
    except (ValueError, TypeError):
        out["note"] = "could not parse tool output"
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True, help="report directory")
    ap.add_argument("--serial", help="serial port for the ttyS2 console")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--duration", type=float, default=45.0, help="serial capture seconds")
    ap.add_argument("--host", help="unit IP on the isolated network")
    ap.add_argument("--rootfs", type=Path, help="extracted or mounted rootfs")
    ap.add_argument("--image", type=Path, help="boot container to inspect")
    args = ap.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)
    report: Dict[str, object] = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "steps": {},
        "skipped": [],
    }

    if args.serial:
        report["steps"]["serial"] = step_serial(args.serial, args.out, args.baud, args.duration)
    else:
        report["skipped"].append("serial")

    if args.host:
        report["steps"]["network"] = step_network(args.host, args.out)
    else:
        report["skipped"].append("network")

    if args.rootfs:
        report["steps"]["rootfs"] = step_rootfs(args.rootfs, args.out)
    else:
        report["skipped"].append("rootfs")

    if args.image:
        report["steps"]["image"] = step_image(args.image)
    else:
        report["skipped"].append("image")

    path = args.out / "report.json"
    path.write_text(json.dumps(report, indent=2))

    print(f"report: {path}")
    for name, result in report["steps"].items():  # type: ignore[union-attr]
        rc = result.get("returncode")
        extra = ""
        if name == "network":
            extra = f" open={result.get('open_ports')}"
        elif name == "rootfs":
            extra = (f" setuid={result.get('setuid_count')}"
                     f" empty_pw={result.get('empty_password_accounts')}"
                     f" keystore={result.get('keystore_node_present')}")
        elif name == "image":
            extra = f" signature_ok={result.get('signature_ok')}"
        elif name == "serial":
            extra = f" lines={result.get('log_lines')}"
        print(f"  {name:8} rc={rc}{extra}")
    if report["skipped"]:
        print(f"  skipped: {', '.join(report['skipped'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
