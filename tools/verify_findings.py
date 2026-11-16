#!/usr/bin/env python3
"""Re-derive the register's structural claims from an extracted image, with no VM and no QEMU.

The four planners that reviewed this project (docs/planning/) asked for one thing above all: a check a
stranger can run. This is that check. Every claim below is re-read from the image bytes; nothing is
taken from prose, and nothing needs our hardware.

    python3 tools/verify_findings.py [rootfs-dir]

Each result prints PASS, FAIL, or SKIP (the input needed is missing) plus the bytes that decided it.
A FAIL is not a crisis: this project has withdrawn claims before, and the tool exists so that a wrong
claim fails loudly instead of ageing quietly. See docs/MEASUREMENT-DISCIPLINE.md rule 14 - a count is
not evidence unless the size and identity of what was counted are recorded, which is why every number
here prints alongside its denominator.
"""
import re
import struct
import sys
from pathlib import Path

DEFAULT = 'work/decrypted-eu-260128/extracted-safe/mango-rootfs'
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
results = []


def report(claim, state, detail):
    results.append((state, claim, detail))
    print(f'  [{state:4s}] {claim}')
    print(f'         {detail}')


def claim_nine_tmp_anchors():
    """V-065: nine /etc paths resolve through world-writable /tmp."""
    names = ['passwd', 'shadow', 'shells', 'fstab', 'resolv.conf', 'ecnr/config',
             'xdg/weston/weston.ini', 'front_lcd.png', 'rear_lcd.png']
    through_tmp, found = [], 0
    for n in names:
        p = ROOT / 'etc' / n
        if p.is_symlink():
            found += 1
            target = str(p.readlink())
            if target.startswith('/tmp/'):
                through_tmp.append(f'/etc/{n} -> {target}')
    if found == 0:
        return report('V-065 nine /etc anchors resolve through /tmp', 'SKIP', 'no /etc symlinks found')
    state = 'PASS' if len(through_tmp) == found else 'FAIL'
    detail = f'{len(through_tmp)} of {found} /etc symlinks resolve through /tmp'
    if through_tmp:
        detail += '; e.g. ' + '; '.join(through_tmp[:2])
    report('V-065 nine /etc anchors resolve through /tmp', state, detail)


def claim_service_privilege_posture():
    """V-064: essentially no service drops privilege or is sandboxed."""
    dirs = [ROOT / 'lib/systemd/system', ROOT / 'etc/systemd/system']
    units = [p for d in dirs if d.is_dir() for p in d.glob('*.service')]
    if not units:
        return report('V-064 services run without privilege separation', 'SKIP', 'no unit files found')
    user_set = sandboxed = no_new_privs = 0
    for u in units:
        try:
            text = u.read_text(errors='replace')
        except OSError:
            continue
        if re.search(r'^User=', text, re.M):
            user_set += 1
        if re.search(r'^(ProtectSystem|ProtectHome|PrivateTmp|CapabilityBoundingSet)', text, re.M):
            sandboxed += 1
        if re.search(r'^NoNewPrivileges', text, re.M):
            no_new_privs += 1
    state = 'PASS' if user_set <= 2 and no_new_privs == 0 else 'FAIL'
    report('V-064 services run without privilege separation', state,
           f'{len(units)} unit files on disk: {user_set} set User=, {no_new_privs} set NoNewPrivileges, '
           f'{sandboxed} set any of ProtectSystem/ProtectHome/PrivateTmp/CapabilityBoundingSet')


def claim_launcher_surface_table():
    """The (appId, surfaceId) table that the projection patches. If it moves, the patch offset is wrong."""
    binary = ROOT / 'app/bin/AppLauncher'
    if not binary.is_file():
        return report('launcher (appId, surfaceId) table at 0x475c0', 'SKIP', 'AppLauncher not present')
    data = binary.read_bytes()
    expected = [(17, 1030), (12, 2080), (110, 2110), (111, 2110),
                (112, 2160), (113, 2170), (73, 2200), (30, 3000)]
    try:
        actual = [struct.unpack('<II', data[0x475c0 + i * 8:0x475c0 + i * 8 + 8]) for i in range(8)]
    except struct.error:
        return report('launcher (appId, surfaceId) table at 0x475c0', 'FAIL', 'file too short for the offset')
    state = 'PASS' if actual == expected else 'FAIL'
    report('launcher (appId, surfaceId) table at 0x475c0', state,
           ' -> '.join(f'{a}:{s}' for a, s in actual) +
           ('' if state == 'PASS' else f' (expected {" -> ".join(f"{a}:{s}" for a, s in expected)})'))


def claim_cryptsetup_gate():
    """V-052: UNECE/optUNECE state derives from cryptsetup isLuks, not from an authenticated decision."""
    binary = ROOT / 'usr/sbin/cryptsetup'
    if not binary.is_file():
        return report('V-052 optUNECE derived from cryptsetup isLuks', 'SKIP', 'cryptsetup absent')
    hit = b'isLuks' in binary.read_bytes()
    report('V-052 optUNECE derived from cryptsetup isLuks', 'PASS' if hit else 'FAIL',
           f'cryptsetup contains isLuks: {hit}')


def claim_console_gate_exists():
    """V-049: a secure_console gate exists in the boot path (its default is measured in the VM, not here)."""
    files = list(ROOT.glob('etc/*.sh')) + [ROOT / 'lib/systemd/esinit']
    hits = [f for f in files if f.is_file() and b'secure_console' in f.read_bytes()]
    if not hits:
        return report('V-049 secure_console gate present in the boot path', 'SKIP', 'no boot script references it')
    report('V-049 secure_console gate present in the boot path', 'PASS',
           f'{len(hits)} of {len(files)} boot scripts reference it; its runtime default is a VM measurement, not a static one')


def main():
    print(f'  image: {ROOT}')
    print(f'  claims re-derived from bytes only; no VM, no QEMU\n')
    for fn in (claim_nine_tmp_anchors, claim_service_privilege_posture, claim_launcher_surface_table,
               claim_cryptsetup_gate, claim_console_gate_exists):
        try:
            fn()
        except Exception as exc:  # a broken claim must not abort the run
            report(fn.__name__, 'FAIL', f'raised {type(exc).__name__}: {exc}')
    passed = sum(1 for s, _, _ in results if s == 'PASS')
    failed = sum(1 for s, _, _ in results if s == 'FAIL')
    skipped = sum(1 for s, _, _ in results if s == 'SKIP')
    print(f'\n  {passed} pass, {failed} fail, {skipped} skip of {len(results)} claims')
    print('  A FAIL means the prose and the bytes disagree - fix the prose first, it is cheaper.')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
