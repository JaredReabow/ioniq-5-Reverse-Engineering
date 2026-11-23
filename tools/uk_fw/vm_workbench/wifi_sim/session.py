"""Opt-in simulator bootstrap inside a caller-owned no-NIC snapshot guest."""
from __future__ import annotations

import base64
import hashlib
import json
import time
from pathlib import Path

from .integration import (ADVANCED_SHA256, PAGE_SHA256, PAYLOAD_SHA256,
                          SIM_TARGET_SHA256, wifi_sim_checked_bytes,
                          wifi_sim_prepare_advanced, wifi_sim_prepare_page,
                          wifi_sim_validate_status, wifi_sim_verify_listener)
from .loopback_setup import setup_loopback
from .network_inventory import parse_inventory

MANIFEST_SHA256 = '17d802bfbc2d095e88309af26e7782821621c3cbee996bd138d62a8cb4cde3fb'


def wifi_sim_load_assets(directory: Path, banner: Path) -> dict:
    """Read verified private inputs once; they are not committed to Git."""
    directory = Path(directory)
    payload = wifi_sim_checked_bytes(directory / 'payload.tar.gz', PAYLOAD_SHA256)
    manifest_bytes = wifi_sim_checked_bytes(directory / 'payload-hashes.json', MANIFEST_SHA256)
    page = wifi_sim_checked_bytes(directory / 'WifiPage.qml', PAGE_SHA256)
    advanced = wifi_sim_checked_bytes(directory / 'advanced-live.qml', ADVANCED_SHA256)
    banner_bytes = Path(banner).read_bytes()
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict) or len(manifest) != 17:
        raise ValueError('unexpected simulation payload manifest')
    import re
    if not all(isinstance(p, str) and re.fullmatch(r'[A-Za-z0-9_./-]+', p) and not p.startswith('/')
               and '..' not in p and isinstance(h, str) and re.fullmatch(r'[0-9a-f]{64}', h)
               for p, h in manifest.items()):
        raise ValueError('invalid simulation payload paths')
    return {'payload': payload, 'manifest': manifest,
            'page': wifi_sim_prepare_page(page, banner_bytes),
            'advanced': wifi_sim_prepare_advanced(advanced)}


def wifi_sim_transfer(shell, data: bytes, destination: str) -> None:
    """Transfer already-verified bytes to a fixed disposable guest path."""
    if destination not in ('/tmp/wifi-sim-payload.tar.gz', '/tmp/wifi-sim',
            '/app/share/AppHomeScreen/qml_eco3.0/HomeScreen/WifiPage.qml',
            '/app/share/AppHomeScreen/qml_eco3.0/HomeScreen/QHMI_HomeScreenMain_Advanced.qml'):
        raise ValueError('unexpected simulation transfer destination')
    encoded = base64.b64encode(data).decode('ascii')
    tmp = '/tmp/wifi-sim-transfer.b64'
    shell._run(': > ' + tmp)
    for i in range(0, len(encoded), 1024):
        shell._run("printf %s '" + encoded[i:i+1024] + "' >> " + tmp)
    result = shell._run('/bin/busybox base64 -d ' + tmp + ' > ' + destination +
                        ' && /usr/bin/sha256sum ' + destination, timeout=60)
    if hashlib.sha256(data).hexdigest().encode() not in result:
        raise RuntimeError('guest simulation transfer hash mismatch')


def wifi_sim_inventory(shell, _label):
    """Return strictly parsed guest-only interface and route inventory."""
    cmd = "( echo IFACES; /bin/busybox ls -1 /sys/class/net || exit 1; echo FLAGS; /bin/busybox cat /sys/class/net/lo/flags || exit 2; echo ADDRS; /sbin/ip -4 -o addr show dev lo || exit 3; echo ROUTE4; /sbin/ip -4 -o route show table all || exit 4; echo ROUTE6; /sbin/ip -6 -o route show table all || exit 5; echo DONE )"
    return parse_inventory(shell._run(cmd, timeout=12).decode('utf-8', 'strict'))


def wifi_sim_prepare_overlay(shell, assets: dict) -> None:
    """Install only the pinned guest QML before native foreground acquisition."""
    wifi_sim_transfer(shell, assets['payload'], '/tmp/wifi-sim-payload.tar.gz')
    shell._run('/bin/busybox tar -xzf /tmp/wifi-sim-payload.tar.gz -C /', timeout=60)
    checks = shell._run(' && '.join('/usr/bin/sha256sum /' + name for name in sorted(assets['manifest'])), timeout=60).decode('ascii')
    for name, digest in assets['manifest'].items():
        if digest + '  /' + name not in checks:
            raise RuntimeError('guest simulation overlay hash mismatch: ' + name)
    wifi_sim_transfer(shell, assets['page'], '/app/share/AppHomeScreen/qml_eco3.0/HomeScreen/WifiPage.qml')
    wifi_sim_transfer(shell, assets['advanced'], '/app/share/AppHomeScreen/qml_eco3.0/HomeScreen/QHMI_HomeScreenMain_Advanced.qml')


def wifi_sim_start_backend(shell, target: bytes) -> None:
    """Start and verify the synthetic backend only after foreground succeeds."""
    if hashlib.sha256(target).hexdigest() != SIM_TARGET_SHA256:
        raise ValueError('simulator executable hash mismatch')
    setup_loopback(lambda label: wifi_sim_inventory(shell, label),
                   lambda command: shell._run(command, timeout=10))
    wifi_sim_transfer(shell, target, '/tmp/wifi-sim')
    wifi_sim_require_port_free(shell)
    shell._run('(/bin/busybox chmod 755 /tmp/wifi-sim && /bin/busybox mkdir -p /run/ioniq-workbench && /bin/busybox chmod 700 /run/ioniq-workbench && [ ! -e /run/ioniq-workbench/wifi-simulation-enabled ] && printf "I_UNDERSTAND_WIFI_IS_SIMULATED\\n" > /run/ioniq-workbench/wifi-simulation-enabled && /bin/busybox chmod 600 /run/ioniq-workbench/wifi-simulation-enabled && (IONIQ_VM_WIFI_SIM=1 /tmp/wifi-sim --vm-only >/tmp/wifi-sim.log 2>&1 & echo $! >/tmp/wifi-sim.pid))', timeout=15)
    wifi_sim_wait_ready(shell)
    flags, addresses = wifi_sim_inventory(shell, 'backend-ready')
    if not flags & 1 or addresses != ['127.0.0.1/8']:
        raise ValueError('simulation loopback changed during startup')
    wifi_sim_check_listener(shell)


class WifiSimListenerPending(RuntimeError):
    """The owned simulator has not yet created its listener."""


def wifi_sim_read_listeners(shell):
    """Read all guest TCP listeners on the fixed simulation port."""
    raw = shell._run('/bin/busybox cat /proc/net/tcp /proc/net/tcp6', timeout=10).decode('ascii', 'strict')
    rows = []
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) >= 10 and fields[3] == '0A' and fields[1].endswith(':1F9A'):
            rows.append((fields[1], fields[9]))
    return rows


def wifi_sim_require_port_free(shell):
    """Refuse any pre-existing listener, including another loopback daemon."""
    if wifi_sim_read_listeners(shell):
        raise ValueError('simulation port already has a listener')


def wifi_sim_check_listener(shell) -> None:
    """Verify process identity, unique listener, ownership and synthetic status."""
    cmd = '''( p=$(/bin/busybox cat /tmp/wifi-sim.pid); [ -r /proc/$p/stat ] || exit 1; echo EXE=$(/usr/bin/readlink /proc/$p/exe); echo TCP_BEGIN; /bin/busybox cat /proc/net/tcp /proc/net/tcp6; echo TCP_END; echo FDS_BEGIN; for f in /proc/$p/fd/*; do /usr/bin/readlink "$f" 2>/dev/null || true; done; echo FDS_END )'''
    def identity():
        raw = shell._run(cmd, timeout=15).decode('utf-8', 'strict')
        try:
            exe = raw.split('EXE=', 1)[1].splitlines()[0]
            tcp = raw.split('TCP_BEGIN\n', 1)[1].split('TCP_END\n', 1)[0]
            fds = raw.split('FDS_BEGIN\n', 1)[1].split('FDS_END', 1)[0].splitlines()
        except (IndexError, ValueError) as exc:
            raise ValueError('invalid simulator listener evidence') from exc
        rows = []
        for line in tcp.splitlines():
            fields = line.split()
            if len(fields) >= 10 and fields[3] == '0A' and fields[1].endswith(':1F9A'):
                rows.append(fields)
        if not rows:
            raise WifiSimListenerPending('simulator listener not yet present')
        return wifi_sim_verify_listener(tcp, fds, '/tmp/wifi-sim', exe)
    rows = wifi_sim_read_listeners(shell)
    if not rows:
        # Absence is retryable only while the recorded simulator remains alive.
        shell._run('( p=$(/bin/busybox cat /tmp/wifi-sim.pid); [ -r /proc/$p/stat ] )', timeout=10)
        raise WifiSimListenerPending('simulator listener not yet present')
    if len(rows) != 1 or rows[0][0] != '0100007F:1F9A':
        raise ValueError('foreign or ambiguous simulation port listener')
    try:
        inode = identity()
    except RuntimeError as exc:
        raise ValueError('listener present but simulator process unavailable') from exc
    raw = shell._run('/bin/busybox wget -qO- http://127.0.0.1:8090/status', timeout=15)
    wifi_sim_validate_status(json.loads(raw))
    if identity() != inode:
        raise ValueError('simulator listener changed during status read')


def wifi_sim_wait_ready(shell, timeout=5.0, interval=0.1):
    """Retry absence only; reject wrong owners/listeners and time out closed."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            wifi_sim_check_listener(shell)
            return
        except WifiSimListenerPending as exc:
            if time.monotonic() >= deadline:
                raise TimeoutError('simulator listener readiness timed out') from exc
            time.sleep(min(interval, max(0, deadline - time.monotonic())))
