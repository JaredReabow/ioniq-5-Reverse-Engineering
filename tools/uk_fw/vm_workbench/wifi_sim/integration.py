"""Pin-checked and fail-closed preparation primitives for guest Wi-Fi simulation.

These functions alone do not start a VM or authorize interaction. The caller
must own a fresh snapshot guest and bind its lifecycle to the simulator.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess

SIM_SOURCE_SHA256 = '665cc468a2e7a790c04a22f64b22a7a1b85c5dc736bee59172b6745a6cbafccc'
SIM_TARGET_SHA256 = 'aebf68556283050d94b985ef056a6953cacd5b67ad4ce781f484d31eb39bf1fb'
PAGE_SHA256 = 'f74154c8dce3507764044bc718b74aeecfeb353a18779ca4fea9f8be6f6bf2b7'
ADVANCED_SHA256 = 'c3ff55aa81dbd12bf2bb624599e13833426405abfd71b93e92bb9359a29c93f6'
PAYLOAD_SHA256 = '981e4001c515eba24b56b5c74a89733a9a4bc7bfb175d358e7a3156f9c81e854'
BANNER_SHA256 = '740cd1fabb96d4dbb1db52627f4f94e81807575a8e9eb793bea8d50d2293a4a1'


def wifi_sim_checked_bytes(path: Path, expected: str) -> bytes:
    """Read a regular artifact once and refuse an unexpected SHA-256."""
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError('simulation artifact must be a regular, non-symlink file')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('simulation artifact hash mismatch: ' + path.name)
    return data


def wifi_sim_build_target(source: Path, output: Path, compiler: Path) -> None:
    """Build the reviewed Linux target and require the independently tested pin."""
    wifi_sim_checked_bytes(source, SIM_SOURCE_SHA256)
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError('simulation target output already exists')
    subprocess.run([str(compiler), '-std=c11', '-Os', '-static', '-s', '-Wall',
                    '-Wextra', '-Werror', str(source), '-o', str(output)], check=True)
    wifi_sim_checked_bytes(output, SIM_TARGET_SHA256)


def wifi_sim_prepare_page(page_data: bytes, banner_patch: bytes) -> bytes:
    """Derive the VM-only page, with HTTP-only status and no home-file reads."""
    if hashlib.sha256(page_data).hexdigest() != PAGE_SHA256:
        raise ValueError('unexpected source Wi-Fi page')
    if hashlib.sha256(banner_patch).hexdigest() != BANNER_SHA256:
        raise ValueError('unexpected simulation banner patch')
    text = page_data.decode('utf-8')
    anchor = '    signal closed()\n'
    if text.count(anchor) != 1:
        raise ValueError('ambiguous page banner insertion')
    additions = [line[1:] for line in banner_patch.decode('utf-8').splitlines()
                 if line.startswith('+') and not line.startswith('+++')]
    text = text.replace(anchor, anchor + '\n'.join(additions) + '\n', 1)
    start = text.index('    function refreshFromFile() {')
    end = text.index('    function post(path, done) {', start)
    text = text[:start] + '''    // VM-only: use exclusively the isolated simulator's loopback status.
    function refreshFromFile() { refresh() }
    function refresh() {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return
            if (xhr.status === 200) { try { applyStatus(JSON.parse(xhr.responseText)) } catch (e) { serviceOk = false } }
            else serviceOk = false
        }
        xhr.open("GET", daemonBase + "/status")
        xhr.send()
    }

''' + text[end:]
    start = text.index('    function refreshHome() {')
    end = text.index('    function refreshConsole() {', start)
    text = text[:start] + '    // VM-only: do not consume real home-event files.\n    function refreshHome() { }\n\n' + text[end:]
    if ('file:///rw_data/wifi/status.json' in text or 'file:///rw_data/wifi/home.json' in text
            or text.count('SIMULATED - NO RADIO') != 1):
        raise ValueError('simulation page isolation failed')
    return text.encode('utf-8')


def wifi_sim_prepare_advanced(advanced_data: bytes) -> bytes:
    """Open the simulated page without sending any input to the guest."""
    if hashlib.sha256(advanced_data).hexdigest() != ADVANCED_SHA256:
        raise ValueError('unexpected source Home page')
    text = advanced_data.decode('utf-8')
    anchor = '    WifiPage {\n        id: wifiPage\n'
    if text.count(anchor) != 1:
        raise ValueError('ambiguous WifiPage insertion')
    timer = '''        // VM-only: direct entry allows a banner check before pointer input.
        Timer { interval: 3000; running: true; repeat: true; onTriggered: { if (!wifiPage.atOtherApp && !wifiPage.visible) { wifiPage.open(); stop() } } }
'''
    return text.replace(anchor, anchor + timer, 1).encode('utf-8')


def wifi_sim_verify_listener(proc_text: str, fd_links: list[str], expected_exe: str,
                             observed_exe: str) -> str:
    """Require exactly one IPv4 loopback listener, owned by the expected process."""
    if observed_exe != expected_exe or expected_exe != '/tmp/wifi-sim':
        raise ValueError('unexpected simulator process')
    rows = []
    for line in proc_text.splitlines():
        fields = line.split()
        if len(fields) >= 10 and fields[3] == '0A' and fields[1].endswith(':1F9A'):
            rows.append((fields[1], fields[9]))
    if len(rows) != 1 or rows[0][0] != '0100007F:1F9A':
        raise ValueError('simulator listener is missing or ambiguous')
    inode = rows[0][1]
    if not inode.isdecimal() or 'socket:[' + inode + ']' not in fd_links:
        raise ValueError('listener is not owned by simulator')
    return inode


def wifi_sim_require_fresh_opt_in(enabled: bool, workspace, diagnostics: bool) -> None:
    """Require an explicit new-workspace-only simulation selection."""
    if not enabled or workspace is not None or diagnostics:
        raise ValueError('Wi-Fi simulation requires an explicit flag, new workspace, and no diagnostic mode')


def wifi_sim_validate_status(status: dict) -> None:
    """Accept only the explicit synthetic status published by the target fixture."""
    if not isinstance(status, dict) or status.get('simulated') is not True or status.get('build_id') != 'SIMULATED':
        raise ValueError('loopback service is not the simulated fixture')
    if 'SIMULATED' not in str(status.get('message', '')):
        raise ValueError('simulation message missing')
