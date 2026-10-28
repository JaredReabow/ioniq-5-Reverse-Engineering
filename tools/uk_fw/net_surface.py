#!/usr/bin/env python3
"""Network surface mapper for an owned IONIQ 5 Gen5W bench unit.

Purpose
-------
Map what an AVN exposes over Wi-Fi before any exploit work.  Remote root on
this class of device requires a reachable network-facing service with a bug;
this tool answers "what is reachable" and "what does it say about itself".

It performs, against a single host you own:

  * TCP connect scan over an embedded-device port set;
  * banner capture for text protocols;
  * HTTP/HTTPS fingerprinting (status, Server header, page title);
  * TLS certificate metadata (subject, issuer, validity, SANs);
  * SSDP/UPnP discovery (M-SEARCH);
  * mDNS service discovery (multicast DNS query).

It does not send exploit payloads, does not attempt authentication, and does not
modify the target.  Connect scans and discovery queries only.

Authorisation
-------------
Remote testing is only lawful against equipment you own or are explicitly
authorised to test.  Keep the unit on an isolated AP/VLAN.  The ``--authorised``
flag is required to make that acknowledgement explicit.

Usage
-----
    python3 net_surface.py --target 192.168.1.50 --authorised
    python3 net_surface.py --target 192.168.1.50 --authorised --json out.json
    python3 net_surface.py --target 192.168.1.50 --authorised --ports 1-1024
    python3 net_surface.py --target 192.168.1.50 --authorised --no-discover
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import ssl
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

# Ports that matter on embedded automotive IVI units.  Kept intentionally
# small so a scan is quick and low-noise.
DEFAULT_PORTS = [
    21,    # ftp
    22,    # ssh
    23,    # telnet
    53,    # dns (dnsmasq in AP mode)
    80,    # http
    111,   # rpcbind
    139,   # netbios
    443,   # https
    445,   # smb
    554,   # rtsp (screen mirroring / camera)
    631,   # ipp
    1900,  # ssdp/upnp (udp, probed separately)
    2049,  # nfs
    3000,  # dev web ui
    5000,  # upnp / dev ui
    5353,  # mdns (udp, probed separately)
    7000,  # misc
    8000,  # dev http
    8008,  # chromecast
    8080,  # http alt
    8081,  # http alt
    8443,  # https alt
    8888,  # dev http
    9000,  # php-fpm / dev
    9090,  # web admin
    10000, # webmin-ish
    49152, # upnp dynamic start
    49153,
]

SSDP_ADDR = ("239.255.255.250", 1900)
MDNS_ADDR = ("224.0.0.251", 5353)


def parse_ports(spec: str) -> List[int]:
    ports: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            ports.extend(range(int(lo), int(hi) + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))


def tcp_open(host: str, port: int, timeout: float) -> Optional[float]:
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.monotonic() - start) * 1000.0
    except OSError:
        return None


def grab_banner(host: str, port: int, timeout: float) -> Optional[str]:
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            try:
                data = s.recv(1024)
            except socket.timeout:
                return None
    except OSError:
        return None
    if not data:
        return None
    return data.decode("utf-8", "replace").strip()[:400]


def http_probe(host: str, port: int, timeout: float, tls: bool) -> Dict[str, object]:
    out: Dict[str, object] = {"tls": tls}
    sock: Optional[socket.socket] = None
    try:
        raw = socket.create_connection((host, port), timeout=timeout)
        if tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            raw = ctx.wrap_socket(raw, server_hostname=host)
        sock = raw
        req = (
            f"HEAD / HTTP/1.1\r\nHost: {host}\r\n"
            "User-Agent: ioniq-bench-survey/1.0\r\nConnection: close\r\n\r\n"
        )
        sock.sendall(req.encode())
        buf = b""
        while len(buf) < 8192:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\r\n\r\n" in buf:
                break
    except OSError as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
    finally:
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass

    text = buf.decode("iso-8859-1", "replace")
    head, _, _body = text.partition("\r\n\r\n")
    first = head.splitlines()[0] if head else ""
    m = re.match(r"HTTP/\d\.\d\s+(\d{3})\s*(.*)", first)
    if m:
        out["status"] = int(m.group(1))
        out["reason"] = m.group(2)
    headers: Dict[str, str] = {}
    for line in head.splitlines()[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    for key in ("server", "x-powered-by", "location", "www-authenticate", "content-type"):
        if key in headers:
            out[key] = headers[key]
    return out


def tls_cert(host: str, port: int, timeout: float) -> Optional[Dict[str, object]]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((host, port), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as s:
                der = s.getpeercert(binary_form=True)
                cert = s.getpeercert()
    except OSError:
        return None
    info: Dict[str, object] = {"der_sha256": None}
    if der:
        import hashlib
        info["der_sha256"] = hashlib.sha256(der).hexdigest()
    if cert:
        info["subject"] = cert.get("subject")
        info["issuer"] = cert.get("issuer")
        info["notAfter"] = cert.get("notAfter")
        info["san"] = cert.get("subjectAltName")
    return info


def ssdp_discover(timeout: float) -> List[Dict[str, str]]:
    msg = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: 239.255.255.250:1900\r\n"
        'MAN: "ssdp:discover"\r\n'
        "MX: 2\r\n"
        "ST: ssdp:all\r\n\r\n"
    ).encode()
    found: List[Dict[str, str]] = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.settimeout(timeout)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        s.sendto(msg, SSDP_ADDR)
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                data, addr = s.recvfrom(4096)
            except socket.timeout:
                break
            text = data.decode("iso-8859-1", "replace")
            rec = {"from": f"{addr[0]}:{addr[1]}"}
            for line in text.splitlines()[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    if k.strip().lower() in ("server", "location", "st", "usn"):
                        rec[k.strip().lower()] = v.strip()
            found.append(rec)
    except OSError:
        pass
    return found


def _dns_encode_name(name: str) -> bytes:
    out = b""
    for label in name.rstrip(".").split("."):
        raw = label.encode()
        out += bytes([len(raw)]) + raw
    return out + b"\x00"


def _dns_read_name(data: bytes, off: int) -> Tuple[str, int]:
    labels: List[str] = []
    while off < len(data):
        ln = data[off]
        if ln == 0:
            off += 1
            break
        if ln & 0xC0:  # compression pointer
            off += 2
            break
        labels.append(data[off + 1 : off + 1 + ln].decode("utf-8", "replace"))
        off += 1 + ln
    return ".".join(labels), off


def mdns_query(timeout: float) -> List[Dict[str, object]]:
    """Ask for the DNS-SD service enumeration PTR and record responders."""

    out: List[Dict[str, object]] = []
    qname = "_services._dns-sd._udp.local"
    packet = (
        b"\x00\x00"          # ID
        b"\x00\x00"          # flags: standard query
        b"\x00\x01"          # QDCOUNT
        b"\x00\x00\x00\x00\x00\x00"  # AN/NS/AR
        + _dns_encode_name(qname)
        + b"\x00\x0c\x00\x01"  # PTR, IN
    )
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.settimeout(timeout)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        s.sendto(packet, MDNS_ADDR)
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            try:
                data, addr = s.recvfrom(4096)
            except socket.timeout:
                break
            rec: Dict[str, object] = {"from": addr[0]}
            if len(data) > 12:
                try:
                    name, _ = _dns_read_name(data, 12)
                    if name:
                        rec["qname"] = name
                except (IndexError, UnicodeDecodeError):
                    pass
            out.append(rec)
    except OSError:
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass
    return out


def scan(host: str, ports: List[int], timeout: float, workers: int = 64) -> Dict[int, Dict[str, object]]:
    results: Dict[int, Dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(tcp_open, host, p, timeout): p for p in ports}
        for fut in as_completed(futures):
            port = futures[fut]
            rtt = fut.result()
            if rtt is not None:
                results[port] = {"state": "open", "rtt_ms": round(rtt, 1)}
    return results


def enrich(host: str, results: Dict[int, Dict[str, object]], timeout: float) -> None:
    for port, rec in results.items():
        if port in (80, 8000, 8008, 8080, 8081, 8888, 9000, 9090, 3000, 5000):
            rec["http"] = http_probe(host, port, timeout, tls=False)
        if port in (443, 8443):
            rec["http"] = http_probe(host, port, timeout, tls=True)
            cert = tls_cert(host, port, timeout)
            if cert:
                rec["tls_cert"] = cert
        if port in (21, 22, 23, 25, 110, 143):
            banner = grab_banner(host, port, timeout)
            if banner:
                rec["banner"] = banner


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Map the network surface of an owned IONIQ 5 bench unit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--target", required=True, help="IP address of the unit")
    ap.add_argument("--ports", default=None, help="port spec e.g. 1-1024 or 80,443")
    ap.add_argument("--timeout", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--json", default=None, help="write full result as JSON")
    ap.add_argument("--no-discover", action="store_true", help="skip SSDP/mDNS")
    ap.add_argument(
        "--authorised",
        action="store_true",
        help="acknowledge you own or are authorised to test the target",
    )
    args = ap.parse_args(argv)

    if not args.authorised:
        print(
            "refusing to scan: pass --authorised to confirm you own or are "
            "authorised to test this host (keep it on an isolated AP/VLAN).",
            file=sys.stderr,
        )
        return 2

    ports = parse_ports(args.ports) if args.ports else DEFAULT_PORTS
    started = time.time()
    print(f"# target {args.target}  ports={len(ports)}  timeout={args.timeout}s\n")

    results = scan(args.target, ports, args.timeout, args.workers)
    enrich(args.target, results, args.timeout)

    discovery: Dict[str, object] = {}
    if not args.no_discover:
        discovery["ssdp"] = ssdp_discover(min(args.timeout * 2, 4.0))
        discovery["mdns"] = mdns_query(min(args.timeout, 2.0))

    if not results:
        print("no open TCP ports in the selected set")
    for port in sorted(results):
        rec = results[port]
        detail = ""
        http = rec.get("http") or {}
        if http.get("status"):
            detail = f"  http {http.get('status')} {http.get('reason','')}".rstrip()
            if http.get("server"):
                detail += f"  server={http['server']}"
        elif http.get("error"):
            detail = f"  http error: {http['error']}"
        if rec.get("banner"):
            detail += f"  banner={rec['banner'][:60]!r}"
        if rec.get("tls_cert", {}).get("der_sha256"):
            detail += f"  cert={rec['tls_cert']['der_sha256'][:16]}"
        print(f"  {port:>5}/tcp open  {rec['rtt_ms']:>6}ms{detail}")

    if discovery:
        print("\n## discovery")
        for rec in discovery.get("ssdp", []):
            print(f"  ssdp {rec}")
        for rec in discovery.get("mdns", []):
            print(f"  mdns {rec}")

    elapsed = time.time() - started
    print(f"\n# {len(results)} open  {elapsed:.1f}s")

    if args.json:
        payload = {
            "target": args.target,
            "elapsed_s": round(elapsed, 2),
            "ports": {str(k): v for k, v in sorted(results.items())},
            "discovery": discovery,
        }
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
        print(f"wrote {args.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
