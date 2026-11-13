#!/bin/bash
# Installed commands reuse prepared media across boots. Nothing builds at boot.
set -euo pipefail
base=/opt/ioniq5-update
tool="$base/tools/uk_fw/radxa_usb.py"
plan="$base/config/serve-plan.json"
service=ioniq-update-media.service
runtime=/run/ioniq5-update
private=/var/lib/ioniq5-update
cache="$private/validation-cache.json"
manual_marker="$runtime/manual-arm"

radxa_media_kernel_prepare() {
    modprobe fuse
    modprobe libcomposite
    if ! mountpoint -q /sys/kernel/config; then
        mount -t configfs configfs /sys/kernel/config
    fi
}

radxa_media_session_note() {
    # Retain a small boot-aware record even when /run disappears after power loss.
    # This records controller state, never the unobservable car-side flash result.
    python3 - "$private" "$1" <<'PY'
from datetime import datetime, timezone
import json, os
from pathlib import Path
import tempfile, uuid
import stat
import sys
directory=Path(sys.argv[1])
directory.mkdir(mode=0o700, parents=True, exist_ok=True)
info=directory.lstat()
if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
    raise SystemExit('Session directory must be root-owned mode 0700')
boot_id=str(uuid.UUID(Path('/proc/sys/kernel/random/boot_id').read_text().strip()))
value={'schema':'ioniq-radxa-session/v1','boot_id':boot_id,'state':sys.argv[2],
       'updated_at':datetime.now(timezone.utc).isoformat()}
fd,temporary=tempfile.mkstemp(prefix='.session-',dir=directory)
try:
    with os.fdopen(fd,'w') as stream:
        json.dump(value,stream,sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary,directory/'session.json')
    fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)
finally:
    if os.path.exists(temporary): os.unlink(temporary)
PY
}

command=${1:-help}
case "$command" in
    prepare|verify)
        shift
        install -d -m 0700 "$private"
        if [[ "$command" == verify ]]; then
            set -- --force "$@"
        fi
        # Preparation is explicit. Changed content never triggers a long hash
        # implicitly during arming or as a side effect of viewing the dashboard.
        python3 "$tool" prepare --serve-plan "$plan" --validation-cache "$cache" \
            "$@" 2>&1 | tee "$private/prepare.log"
        ;;
    inspect)
        radxa_media_kernel_prepare
        exec python3 "$tool" inspect --backing-kind fuse-direct
        ;;
    selftest)
        cd "$base"
        python3 -m unittest discover -s tests -p 'test_nbdkit_dynamic_media.py' -q
        exec python3 -m unittest discover -s tests -p 'test_radxa_usb.py' -q
        ;;
    plan)
        radxa_media_kernel_prepare
        shift
        exec python3 "$tool" plan --serve-plan "$plan" --validation-cache "$cache" \
            --backing-kind fuse-direct "$@"
        ;;
    arm)
        radxa_media_kernel_prepare
        shift
        if systemctl is-active --quiet "$service"; then
            exec python3 "$tool" status
        fi
        # No compilation, decompression, image generation or content rehash here.
        radxa_media_session_note arm_requested
        install -d -m 0755 "$runtime"
        : >"$manual_marker"
        trap 'rm -f "$manual_marker"' EXIT HUP INT TERM
        systemctl reset-failed "$service" 2>/dev/null || true
        if systemctl start "$service"; then
            rm -f "$manual_marker"
            trap - EXIT HUP INT TERM
            radxa_media_session_note armed
            exec python3 "$tool" status
        fi
        radxa_media_session_note arm_failed
        systemctl --no-pager --full status "$service" >&2 || true
        exit 1
        ;;
    internal-arm)
        radxa_media_kernel_prepare
        shift
        exec python3 "$tool" arm --serve-plan "$plan" --execute --hold \
            --validation-cache "$cache" --backing-kind fuse-direct "$@"
        ;;
    teardown)
        shift
        rm -f "$manual_marker"
        # Cancel systemd first, including a controller still activating.
        systemctl stop "$service"
        python3 "$tool" teardown --execute "$@"
        radxa_media_session_note stopped
        ;;
    status)
        exec python3 "$tool" status
        ;;
    *)
        printf 'usage: %s {prepare|verify|inspect|selftest|plan|arm|teardown|status}\n' "$0" >&2
        exit 2
        ;;
esac
