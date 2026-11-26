"""Serialized, bounded serial bridge to the workbench's private VM shell.

Only fixed operations are exposed. Browser input never becomes a shell
fragment: mailbox lines are validated before being encoded for transfer.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import math
import os
import platform
import re
import stat
import struct
import threading
import time
import uuid
import zlib
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Optional


_INPUT = re.compile(r"seq [1-9][0-9]{0,9} (?:click [0-9]+ [0-9]+|cclick [0-9]+ [0-9]+ [1-9][0-9]{0,19}|(?:drag|pdrag) [0-9]+ [0-9]+ [0-9]+ [0-9]+|key [0-9]{1,3})\n")
_SIM = re.compile(r"[A-Za-z0-9_-]{1,32} (?:GET (?:debug_count|parking_status)|SET (?:debug_count [0-9]{1,3}|parking_status [01]))\n")
_MAX_REPLY = 24 * 1024 * 1024
_MAX_CAPTURE = 4 * 1024 * 1024
_MAX_ENCODED = 4 * ((_MAX_CAPTURE + 2) // 3)
_CAPTURE_TOKEN = re.compile(r"^[0-9a-f]{32}$")
_READY_MAX_BYTES = 65536
_READY_MAX_LINE = 4096
_REASON11_SNAPSHOT_STATES = (
    "ok", "unavailable", "scan_unowned", "log_identity_or_bounds",
    "prefix_mismatch", "read_failed", "line_check_failed",
    "newline_check_failed", "byte_check_failed",
)
_REASON11_NATIVE_PHASES = (
    "no_ordered_chain", "handler_entry", "confirm_show", "draw_start",
    "valid_model", "draw_finish", "native_return",
)
_REASON11_DISPATCH_CLASSES = (
    "reply", "dbus_no_reply", "dbus_service_unknown", "dbus_access_denied",
    "wrapper_timeout", "empty_reply", "other_error",
)
_STANDBY_FAILURE_PATH = "/tmp/workbench-launch.failure"
_STANDBY_FAILURE_MAX_BYTES = 64
_STANDBY_FAILURE_STAGES = (
    "clock", "deadline", "duplicate_clear", "duplicate_registration", "loading_pid",
    "loading_timeout", "log_changed", "log_hash", "log_identity_or_size", "log_parse",
    "log_read", "log_recheck", "log_rewritten", "log_short_read", "log_stat",
    "owner_changed", "owner_query", "owner_recheck", "ping_invalid", "ping_oversize",
    "process", "standby_exited",
)
_STANDBY_MARKER = b"WB_STANDBY_"
_IVI_FRAME_LIMIT = 8 * 1024 * 1024


def vm_guest_dbus_timeouts(*, system: Optional[str] = None, machine: Optional[str] = None,
                           slow_tcg: Optional[bool] = None) -> tuple[int, int]:
    """Select the bounded foreground-reply window for the active emulation path."""
    if slow_tcg is None:
        slow_tcg = os.environ.get("GEN5W_SLOW_TCG") == "1"
    architecture = (machine or platform.machine()).lower()
    host_system = system or platform.system()
    # The only measured known-positive 0.4.8 Linux ARM64 reply was 3,961 ms:
    # a 39 ms margin is shorter than ordinary TCG scheduling jitter.
    if slow_tcg or (host_system == "Linux" and architecture in ("aarch64", "arm64")):
        return 12000, 15
    return 4000, 5


_SLOW_TCG = os.environ.get("GEN5W_SLOW_TCG") == "1"
VM_IVI_TRANSFER_COMPRESSED = _SLOW_TCG
VM_IVI_TRANSFER_TIMEOUT_SECONDS = 180 if _SLOW_TCG else 120
VM_IVI_SETUP_DEADLINE_MS = 60000 if _SLOW_TCG else 10000
VM_IVI_CAPTURE_DEADLINE_MS = 60000 if _SLOW_TCG else 30000
# ARM64 TCG can take longer than fifteen seconds to publish a receipt and more
# than twenty seconds to complete both bounded log scans afterward. The regular
# profile keeps thirty-second phase limits. WSL1 opts into a sixty-second profile
# because its syscall translation layer adds another overhead boundary.
VM_IVI_VERIFICATION_DEADLINE_MS = 60000 if _SLOW_TCG else 30000
VM_DBUS_REPLY_TIMEOUT_MS, VM_DBUS_WRAPPER_TIMEOUT_SECONDS = vm_guest_dbus_timeouts(
    slow_tcg=_SLOW_TCG)
_DBUS_HEADER = rb"method return[^\r\n]{0,512}\n"
_SERIAL_IRQ_WARNING = re.compile(
    rb"\[\s*[0-9]+\.[0-9]+\] (?:serial8250: too much work for irq4|"
    rb"serial8250_interrupt: [0-9]+ callbacks suppressed|"
    rb"random: dbus-uuidgen urandom read with [0-9]+ bits of entropy available|"
    rb"random: nonblocking pool is initialized)\r?\n")
# This observed warning can split a screenshot record at any byte. Keep its
# normalization capture-only: acquisition and IVI parsers share the IRQ filter.
_CAPTURE_HRTIMER_WARNING = re.compile(
    rb"\[[ \t]*[0-9]+\.[0-9]+\] hrtimer: interrupt took [0-9]+ ns\r?\n")
_DLT_CONFIRM_ENVELOPE = (
    r"^[0-9][0-9][0-9][0-9]/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01]) "
    r"([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9][.][0-9][0-9][0-9][0-9][0-9][0-9] "
    r"+[0-9]+ [0-9][0-9][0-9] MANG STAN STAN log info V 1 "
    r"[[]VM_OBSERVE_CONFIRM geometry [^][]+[]]$"
)


def vm_guest_probe_output_png(output: bytes, width: int, height: int, fmt: int) -> bytes:
    """Convert tightly packed little-endian Pixman output to a straight-alpha PNG."""
    if (type(width) is not int or type(height) is not int or not 0 < width <= 4096 or
            not 0 < height <= 2160 or type(fmt) is not int or fmt not in (0x20020888, 0x20028888) or
            not isinstance(output, bytes) or width * height * 4 > _IVI_FRAME_LIMIT or
            len(output) != width * height * 4):
        raise ValueError("invalid probe output dimensions, format or length")
    rows = bytearray(height * (1 + width * 4))
    for y in range(height):
        src, dst = y * width * 4, y * (width * 4 + 1) + 1
        for x in range(width):
            b, g, r, a = output[src + x * 4:src + x * 4 + 4]
            if fmt == 0x20020888:
                a = 255
            else:
                if max(r, g, b) > a:
                    raise ValueError("invalid premultiplied probe output")
                if a:
                    r, g, b = ((c * 255 + a // 2) // a for c in (r, g, b))
                else:
                    r = g = b = 0
            rows[dst + x * 4:dst + x * 4 + 4] = bytes((r, g, b, a))
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", binascii.crc32(kind + payload) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


class GuestStandbyError(RuntimeError):
    """A terminal HMI startup stage from the allowlisted guest receipt."""

    def __init__(self, stage: str):
        if stage not in _STANDBY_FAILURE_STAGES:
            raise ValueError("invalid standby failure stage")
        self.stage = stage
        super().__init__(f"Gen5W HMI startup failed ({stage}).")


def vm_guest_parse_standby_readiness(data: bytes, token: str) -> None:
    """Require one complete current readiness record or raise a terminal error."""
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token):
        raise ValueError("invalid standby readiness token")
    if not isinstance(data, bytes) or len(data) > _READY_MAX_BYTES:
        raise ValueError("standby readiness response exceeds limit")
    marker = _STANDBY_MARKER + token.encode("ascii")
    normalized = data.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        raise ValueError("invalid standby readiness line ending")
    lines = normalized.split(b"\n")
    if any(len(line) > _READY_MAX_LINE for line in lines):
        raise ValueError("standby readiness line exceeds limit")
    if lines[-1] and _STANDBY_MARKER in lines[-1]:
        raise ValueError("truncated standby readiness record")
    # Ignore complete unrelated serial lines. Any standby protocol marker
    # claims a terminal record and must match this transaction.
    if lines[-1]:
        raise ValueError("incomplete standby response line")
    records = [line for line in lines[:-1] if _STANDBY_MARKER in line]
    if records == [marker + b" READY"]:
        return
    for stage in _STANDBY_FAILURE_STAGES:
        if records == [marker + b" FAIL " + stage.encode("ascii")]:
            raise GuestStandbyError(stage)
    raise ValueError("missing, duplicate or invalid standby readiness record")


def vm_guest_parse_ivi_frame(data: bytes, token: str, *, compressed: bool = False) -> tuple:
    """Validate a nonce-bound private pixel snapshot and both payload digests.

    A valid snapshot is not a Confirm-screen or physical-device assertion. The
    client must obey the Wayland busy-buffer contract for a coherent source.
    """
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token):
        raise ValueError("invalid IVI frame token")
    if not isinstance(data, bytes) or len(data) > _MAX_REPLY:
        raise ValueError("invalid IVI frame response size")
    data = _SERIAL_IRQ_WARNING.sub(b"", data).replace(b"\r\n", b"\n")
    prefix = ("WB_IVI_" + token + " ").encode()
    rows = [line for line in data.splitlines() if line.startswith(prefix)]
    if len(rows) != 5:
        raise ValueError("missing or duplicate IVI frame markers")
    metadata = rows[0][len(prefix):].split()
    if (len(metadata) not in (23, 32) or metadata[0:2] != [b"META", b"OK"] or
        not all(re.fullmatch(rb"[1-9][0-9]{0,19}", v) for v in metadata[2:6]) or
        not all(re.fullmatch(rb"0x[0-9a-f]{1,16}", v) for v in metadata[6:8]) or
        not all(re.fullmatch(rb"[1-9][0-9]{0,9}", v) for v in metadata[8:16]) or
        not all(re.fullmatch(rb"-?(?:0|[1-9][0-9]{0,9})", v) and -2147483648 <= int(v) <= 2147483647 for v in metadata[16:22]) or
        metadata[-1] != b"END"):
        raise ValueError("invalid IVI frame metadata")
    pid, start, sequence, timestamp = map(int, metadata[2:6])
    sw, sh, sf, sn, ow, oh, of, on = map(int, metadata[8:16])
    geometry = list(map(int, metadata[16:20])); output_origin = list(map(int, metadata[20:22]))
    if (sw > 4096 or sh > 2160 or (ow, oh) != (1920, 720) or
        sf not in (0x20028888, 0x20020888) or of not in (0x20028888, 0x20020888) or
        sn != sw * sh * 4 or on != ow * oh * 4 or sn > _IVI_FRAME_LIMIT or on > _IVI_FRAME_LIMIT):
        raise ValueError("invalid IVI frame dimensions or format")
    source_boundary = b"SOURCE_GZIP BEGIN" if compressed else b"SOURCE BEGIN"
    output_boundary = b"OUTPUT_GZIP BEGIN" if compressed else b"OUTPUT BEGIN"
    if (rows[1][len(prefix):] != source_boundary or rows[3][len(prefix):] != output_boundary or
        not re.fullmatch(rb"SOURCE_END [0-9a-f]{64}", rows[2][len(prefix):]) or
        not re.fullmatch(rb"OUTPUT_END [0-9a-f]{64}", rows[4][len(prefix):])):
        raise ValueError("invalid IVI frame boundary")
    try:
        parts = data.split(prefix)
        if len(parts) != 6:
            raise ValueError("ambiguous IVI frame markers")
        source_start = parts[2].split(b"\n", 1)[1]
        output_start = parts[4].split(b"\n", 1)[1]
        source_encoded = base64.b64decode(b"".join(source_start.split()), validate=True)
        output_encoded = base64.b64decode(b"".join(output_start.split()), validate=True)
        if compressed:
            def bounded_gunzip(payload: bytes, limit: int) -> bytes:
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                decoded = decoder.decompress(payload, limit + 1)
                if len(decoded) <= limit:
                    decoded += decoder.flush(limit + 1 - len(decoded))
                if (len(decoded) > limit or decoder.unconsumed_tail or
                        decoder.unused_data or not decoder.eof):
                    raise ValueError("invalid compressed IVI frame payload")
                return decoded
            source = bounded_gunzip(source_encoded, sn)
            output = bounded_gunzip(output_encoded, on)
        else:
            source, output = source_encoded, output_encoded
        source_hash = rows[2][len(prefix):].split()[1]
        output_hash = rows[4][len(prefix):].split()[1]
        if (len(source) != sn or len(output) != on or not re.fullmatch(rb"[0-9a-f]{64}", source_hash) or
            not re.fullmatch(rb"[0-9a-f]{64}", output_hash) or
            hashlib.sha256(source).hexdigest().encode() != source_hash or
            hashlib.sha256(output).hexdigest().encode() != output_hash):
            raise ValueError("IVI frame size or digest mismatch")
    except (IndexError, OSError, EOFError, binascii.Error) as exc:
        raise ValueError("invalid IVI frame payload") from exc
    receipt = {"pid": pid, "starttime": start, "sequence": sequence, "monotonic_ms": timestamp,
               "surface_identity": metadata[6].decode(), "output_identity": metadata[7].decode(),
               "surface_destination": geometry, "output_origin": output_origin,
               "source": {"width": sw, "height": sh, "format": sf, "sha256": source_hash.decode()},
               "output": {"width": ow, "height": oh, "format": of, "sha256": output_hash.decode()},
               "limitation": "Source coherence assumes a protocol-compliant Wayland client; same callback does not establish Confirm content or physical behavior."}
    if len(metadata) == 32:
        extra = metadata[22:31]
        if (not all(re.fullmatch(rb"[1-9][0-9]{0,19}", extra[i]) for i in (0, 1, 2, 5, 8)) or
                not all(re.fullmatch(rb"0x[0-9a-f]{1,16}", extra[i]) for i in (3, 4)) or
                not all(re.fullmatch(rb"[0-9a-f]{64}", extra[i]) for i in (6, 7))):
            raise ValueError("invalid IVI baseline metadata")
        receipt["baseline"] = {"time": int(extra[0]), "size": int(extra[1]), "format": int(extra[2]),
                               "buffer": extra[3].decode(), "selected_buffer": extra[4].decode(),
                               "observations": int(extra[5]), "sha256": extra[6].decode(), "ack_sha": extra[7].decode(),
                               "observation_start": int(extra[8])}
    return receipt, source, output


def vm_guest_ivi_frame_command(token: str) -> str:
    """Request one fixed, owner-bound pixel diagnostic in the isolated guest."""
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token):
        raise ValueError("invalid IVI frame token")
    command = r'''(
BB=/bin/busybox
set -o pipefail
umask 077
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr) || exit 1
identity() {
  own=$($BB timeout 1 /usr/bin/dbus-send --session --print-reply --reply-timeout=750 --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner string:com.lge.hkmc.avn.appfunc.AppStandbyClock 2>/dev/null | $BB head -c 1025) || return 1
  [ "${#own}" -le 1024 ] || return 1
  owner_now=$(printf '%s\n' "$own" | $BB awk 'NR==1 {if($0 !~ /^method return /) exit 1;next} NR==2 {if($0 !~ /^   string ":[0-9]+[.][0-9]+"$/) exit 1;gsub(/^   string "|"$/," ");gsub(/ /,"");v=$0;next} {exit 1} END {if(NR!=2 || v=="") exit 1;print v}') || return 1
  reply=$($BB timeout 1 /usr/bin/dbus-send --session --print-reply --reply-timeout=750 --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetConnectionUnixProcessID "string:$owner_now" 2>/dev/null | $BB head -c 1025) || return 1
  [ "${#reply}" -le 1024 ] || return 1
  pid_now=$(printf '%s\n' "$reply" | $BB awk 'NR==1 {if($0 !~ /^method return /) exit 1;next} NR==2 {if($0 !~ /^   uint32 [1-9][0-9]*$/) exit 1;v=$2;next} {exit 1} END {if(NR!=2 || v=="" || v+0>2147483647) exit 1;print v}') || return 1
  kill -0 "$pid_now" 2>/dev/null
}
identity || exit 1
owner=$owner_now; pid=$pid_now
start=$($BB sed 's/^.*) //' "/proc/$pid/stat" | $BB awk '{print $20}') || exit 1
case "$start" in ''|*[!0-9]*) exit 1;; esac
d=/tmp/vm-ivi-frame-probe
[ -d "$d" ] && [ ! -L "$d" ] && [ "$($BB stat -c '%u:%a' "$d")" = 0:700 ] || exit 1
for f in request request.tmp receipt receipt.tmp source.raw output.raw; do [ ! -e "$d/$f" ] && [ ! -L "$d/$f" ] || exit 1; done
(set -C; printf '__TOKEN__ %s %s\n' "$pid" "$start" > "$d/request.tmp") || exit 1
$BB mv "$d/request.tmp" "$d/request" || exit 1
n=0; while [ "$n" -lt 15 ] && [ ! -e "$d/receipt" ]; do $BB sleep 1; n=$((n+1)); done
[ -f "$d/receipt" ] && [ ! -L "$d/receipt" ] && [ "$($BB wc -c < "$d/receipt")" -le 512 ] || exit 1
line=$($BB cat "$d/receipt") || exit 1
case "$line" in "__TOKEN__ OK $pid $start "*) ;; *) exit 1;; esac
identity && [ "$owner" = "$owner_now" ] && [ "$pid" = "$pid_now" ] || exit 1
for f in source.raw output.raw; do [ -f "$d/$f" ] && [ ! -L "$d/$f" ] && [ "$($BB stat -c '%u:%a' "$d/$f")" = 0:600 ] && [ "$($BB wc -c < "$d/$f")" -le 8388608 ] || exit 1; done
source_hash=$($BB sha256sum "$d/source.raw" | $BB cut -d ' ' -f1) || exit 1
output_hash=$($BB sha256sum "$d/output.raw" | $BB cut -d ' ' -f1) || exit 1
printf '\nWB_IVI___TOKEN__ META %s END\n' "${line#* }"
printf 'WB_IVI___TOKEN__ SOURCE BEGIN\n'; $BB base64 "$d/source.raw" || exit 1
printf 'WB_IVI___TOKEN__ SOURCE_END %s\n' "$source_hash"
printf 'WB_IVI___TOKEN__ OUTPUT BEGIN\n'; $BB base64 "$d/output.raw" || exit 1
printf 'WB_IVI___TOKEN__ OUTPUT_END %s\n' "$output_hash"
)'''
    return command.replace("__TOKEN__", token)


def vm_guest_ivi_frame_export_command(token: str, owner: str, pid: int, start: int,
                                      receipt_hash: str, *, compressed: bool = False) -> str:
    """Export an already captured probe after its original acquisition deadline."""
    if (not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token) or
            not isinstance(owner, str) or not re.fullmatch(r":[0-9]+[.][0-9]+", owner) or
            type(pid) is not int or not 1 <= pid <= 2147483647 or type(start) is not int or start <= 0 or
            not isinstance(receipt_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", receipt_hash)):
        raise ValueError("invalid IVI frame export binding")
    original = vm_guest_ivi_frame_command(token)
    before, rest = original.split("identity || exit 1\nowner=$owner_now; pid=$pid_now\n", 1)
    tail = rest[rest.index('line=$($BB cat "$d/receipt")'):]
    if compressed:
        tail = tail.replace(
            f"printf 'WB_IVI_{token} SOURCE BEGIN\\n'; $BB base64 \"$d/source.raw\" || exit 1",
            f"printf 'WB_IVI_{token} SOURCE_GZIP BEGIN\\n'; "
            "$BB gzip -c \"$d/source.raw\" | $BB base64 || exit 1",
        ).replace(
            f"printf 'WB_IVI_{token} OUTPUT BEGIN\\n'; $BB base64 \"$d/output.raw\" || exit 1",
            f"printf 'WB_IVI_{token} OUTPUT_GZIP BEGIN\\n'; "
            "$BB gzip -c \"$d/output.raw\" | $BB base64 || exit 1",
        )
    checks = (f'identity || exit 1\nowner={owner}; pid={pid}; start={start}\n'
              '[ "$owner" = "$owner_now" ] && [ "$pid" = "$pid_now" ] || exit 1\n'
              'd=/tmp/vm-ivi-frame-probe\n'
              '[ -d "$d" ] && [ ! -L "$d" ] && [ "$($BB stat -c \'%u:%a\' "$d")" = 0:700 ] || exit 1\n'
              '[ -f "$d/receipt" ] && [ ! -L "$d/receipt" ] && [ "$($BB stat -c \'%u:%a\' "$d/receipt")" = 0:600 ] && [ "$($BB wc -c < "$d/receipt")" -le 512 ] || exit 1\n'
              f'[ "$($BB sha256sum "$d/receipt" | $BB cut -d " " -f1)" = {receipt_hash} ] || exit 1\n')
    return before + checks + tail


def vm_guest_probe_failure_command(token: str, pid: int, start: int, epoch: int, deadline: int) -> str:
    """Read only a bounded, nonce-bound receipt and private-file inventory."""
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token) or type(pid) is not int or not 1 <= pid <= 2147483647 or type(start) is not int or start <= 0 or type(epoch) is not int or epoch <= 0 or type(deadline) is not int or deadline != epoch + VM_IVI_CAPTURE_DEADLINE_MS - 1:
        raise ValueError("invalid failure evidence binding")
    return r'''(
BB=/bin/busybox
d=/tmp/vm-ivi-frame-probe
[ -d "$d" ] && [ ! -L "$d" ] && [ "$($BB stat -c '%u:%a' "$d")" = 0:700 ] || exit 1
[ -f "$d/request" ] && [ ! -L "$d/request" ] && [ "$($BB stat -c '%u:%a' "$d/request")" = 0:600 ] && [ "$($BB wc -c < "$d/request")" -le 160 ] || exit 1
$BB awk -v n='__TOKEN__' -v p='__PID__' -v s='__START__' -v e='__EPOCH__' -v d='__DEADLINE__' 'NR!=1 || NF!=5 || $1!=n || $2 ""!=p "" || $3 ""!=s "" || $4 ""!=e "" || $5 ""!=d "" {exit 1} END {if(NR!=1) exit 1}' "$d/request" || exit 1
printf 'WB_FAIL___TOKEN__ BEGIN\n'
for f in receipt source.raw output.raw; do
  if [ -f "$d/$f" ] && [ ! -L "$d/$f" ] && [ "$($BB stat -c '%u:%a' "$d/$f")" = 0:600 ]; then
    size=$($BB wc -c < "$d/$f" | $BB awk '{print $1}') || exit 1
    case "$size" in ''|*[!0-9]*) exit 1;; esac
    [ "$size" -le 8388608 ] || exit 1
    printf 'WB_FAIL___TOKEN__ ITEM %s %s\n' "$f" "$size"
  fi
done
if [ -f "$d/receipt" ] && [ ! -L "$d/receipt" ] && [ "$($BB stat -c '%u:%a' "$d/receipt")" = 0:600 ]; then
  [ "$($BB wc -c < "$d/receipt")" -le 512 ] || exit 1
  $BB awk -v n='__TOKEN__' -v p='__PID__' -v s='__START__' 'NR!=1 || (NF!=22 && NF!=31) || $1!=n || ($2!="OK" && $2!="FAIL") || $3!=p || $4!=s {exit 1} END {if(NR!=1) exit 1}' "$d/receipt" || exit 1
  printf 'WB_FAIL___TOKEN__ RECEIPT '; $BB base64 "$d/receipt" | $BB tr -d '\n'; printf '\n'
fi
printf 'WB_FAIL___TOKEN__ END\n'
)'''.replace('__TOKEN__', token).replace('__PID__', str(pid)).replace('__START__', str(start)).replace('__EPOCH__', str(epoch)).replace('__DEADLINE__', str(deadline))


def vm_guest_parse_probe_failure(data: bytes, token: str, pid: int, start: int, arm: int, deadline: int) -> dict:
    """Accept only one exact LF-framed receipt and canonical inventory."""
    if (not isinstance(data, bytes) or len(data) > 4096 or not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token) or
            type(pid) is not int or not 1 <= pid <= 2147483647 or type(start) is not int or start <= 0 or
            type(arm) is not int or type(deadline) is not int or not 0 < arm < deadline):
        raise ValueError("invalid failure evidence")
    prefix = ('WB_FAIL_' + token + ' ').encode()
    if not data.endswith(b'\n'):
        raise ValueError("truncated failure evidence")
    if b'\r' in data:
        raise ValueError("noncanonical failure evidence")
    raw_lines = data[:-1].split(b'\n')
    if any(not line.startswith(prefix) for line in raw_lines):
        raise ValueError("unexpected failure evidence")
    lines = [line[len(prefix):] for line in raw_lines]
    if len(lines) < 2 or lines[0] != b'BEGIN' or lines[-1] != b'END':
        raise ValueError("incomplete failure evidence")
    inventory, receipt = {}, None
    record_order = {b'receipt': 0, b'source.raw': 1, b'output.raw': 2}
    last_order = -1
    for line in lines[1:-1]:
        match = re.fullmatch(rb'ITEM (receipt|source[.]raw|output[.]raw) (0|[1-9][0-9]{0,7})', line)
        if match:
            name_raw, size = match.group(1), int(match.group(2))
            name = name_raw.decode()
            order = record_order[name_raw]
            if name in inventory or order <= last_order or size > 8388608:
                raise ValueError("invalid inventory")
            inventory[name] = size
            last_order = order
        elif re.fullmatch(rb'RECEIPT [A-Za-z0-9+/]+={0,2}', line) and receipt is None and last_order < 3:
            try: receipt = base64.b64decode(line[8:], validate=True)
            except (ValueError, binascii.Error) as exc: raise ValueError("invalid receipt encoding") from exc
            last_order = 3
        else: raise ValueError("invalid failure evidence record")
    probe_failure = None
    if receipt is not None:
        fields = receipt[:-1].split(b' ') if receipt.endswith(b'\n') else []
        if (len(receipt) > 512 or not receipt.endswith(b'\n') or len(fields) not in (22, 31) or
                any(not field for field in fields) or b'\r' in receipt or
                fields[:4] not in ([token.encode(), b'OK', str(pid).encode(), str(start).encode()], [token.encode(), b'FAIL', str(pid).encode(), str(start).encode()]) or
                any(not re.fullmatch(rb'[0-9]+', fields[i]) for i in (4, 5, *range(8, 16))) or
                any(not re.fullmatch(rb'(?:0x[0-9a-f]+|\(nil\))', fields[i]) for i in (6, 7)) or
                any(not re.fullmatch(rb'-?[0-9]+', fields[i]) for i in range(16, 22)) or inventory.get('receipt') != len(receipt)):
            raise ValueError("invalid failure receipt identity")
        if fields[1] == b'OK' and not arm <= int(fields[5]) < deadline:
            raise ValueError("failure receipt capture outside arm window")
        if fields[1] == b'FAIL':
            # FAIL receipts reuse the six geometry fields for a versioned,
            # numeric producer diagnostic. Keep the raw receipt for backward
            # compatibility, but also persist the validated fields so a
            # private failure record can be understood without decoding it.
            if len(fields) != 22:
                raise ValueError("invalid failure diagnostic length")
            code, observe, callbacks, unchanged, elapsed, schema = map(int, fields[16:22])
            labels = {
                0: "unknown", 1: "timeout", 2: "output_gone", 3: "epoch_changed",
                4: "clock", 5: "go_invalid", 6: "baseline_io", 7: "owner_changed",
                8: "frame_check", 9: "output_io", 10: "initial_layout",
            }
            if (schema != 1 or code not in labels or observe not in (0, 1) or
                    not 0 <= unchanged <= callbacks <= 1000000 or
                    not 0 <= elapsed <= 9999999):
                raise ValueError("invalid failure diagnostic fields")
            probe_failure = {"schema": schema, "code": code, "name": labels[code],
                             "observation_enabled": bool(observe),
                             "frame_callbacks": callbacks,
                             "unchanged_comparisons": unchanged,
                             "elapsed_ms": elapsed}
    result = {"qualification": "UNQUALIFIED", "inventory": inventory,
              "receipt": receipt.decode('ascii') if receipt is not None else None,
              "receipt_status": fields[1].decode('ascii') if receipt is not None else "absent"}
    if probe_failure is not None:
        result["probe_failure"] = probe_failure
    return result


def vm_guest_standby_readiness_command(token: str) -> str:
    """Build the fixed bounded probe for this readiness transaction."""
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token):
        raise ValueError("invalid standby readiness token")
    # Base64 lets the shell compare exact bytes, including the final LF and
    # any embedded NUL. Each branch emits a literal allowlisted label only.
    stages = []
    for stage in _STANDBY_FAILURE_STAGES:
        encoded = base64.b64encode((stage + "\n").encode("ascii")).decode("ascii")
        stages.append(f"{encoded}) stage={stage} ;;")
    terminal_status = base64.b64encode(b"25\n").decode("ascii")
    return (f"(receipt={_STANDBY_FAILURE_PATH}; status_file=/tmp/workbench-launch.status; "
            "launch_log=/tmp/workbench-launch.log; "
            "wb_encode_prefix() { (set -o pipefail; /bin/busybox timeout 1 /bin/busybox head "
            "-c \"$1\" \"$2\" | /bin/busybox base64) 2>/dev/null; }; "
            "n=0; while test \"$n\" -lt 310; do "
            "if test -e \"$status_file\"; then "
            "status=$(/bin/busybox cat \"$status_file\") || exit 1; "
            "if test \"$status\" = 0; then "
            "test ! -e \"$receipt\" && test ! -L \"$receipt\" || exit 1; "
            "/bin/busybox grep -q '^WORKBENCH_STANDBY_PREREQUISITES_READY$' \"$launch_log\" 2>/dev/null || exit 1; "
            f"printf '\\nWB_STANDBY_{token} READY\\n'; exit 0; fi; "
            "test \"$status\" = 25 && test -f \"$status_file\" && test ! -L \"$status_file\" || exit 1; "
            "status_bytes=$(wb_encode_prefix 4 \"$status_file\") || exit 1; "
            f"test \"$status_bytes\" = {terminal_status} || exit 1; "
            "test -f \"$receipt\" && test ! -L \"$receipt\" || exit 1; "
            "receipt_stat=$(/bin/busybox stat -c '%d:%i:%s:%a:%h' \"$receipt\" 2>/dev/null) || exit 1; "
            "case \"$receipt_stat\" in *:600:1) ;; *) exit 1 ;; esac; "
            f"encoded=$(wb_encode_prefix {_STANDBY_FAILURE_MAX_BYTES + 1} \"$receipt\") || exit 1; "
            "test ! -L \"$receipt\" && test \"$(/bin/busybox stat -c '%d:%i:%s:%a:%h' \"$receipt\" 2>/dev/null)\" = \"$receipt_stat\" || exit 1; "
            f"case \"$encoded\" in {' '.join(stages)} *) exit 1 ;; esac; "
            "test -f \"$launch_log\" && test ! -L \"$launch_log\" || exit 1; "
            "/bin/busybox timeout 1 /bin/busybox grep -q '^WORKBENCH_STANDBY_PREREQUISITES_READY$' \"$launch_log\" 2>/dev/null; "
            "test \"$?\" = 1 || exit 1; "
            f"printf '\\nWB_STANDBY_{token} FAIL %s\\n' \"$stage\"; exit 0; fi; "
            "n=$((n+1)); /bin/busybox sleep 1; done; exit 1)")


def vm_guest_parse_confirm_geometry(data: bytes) -> dict:
    """Parse one observational QML record; reject ambiguous or unsafe geometry."""
    if not isinstance(data, bytes) or len(data) > 4096:
        raise ValueError("invalid Confirm observation size")
    try:
        tokens = data.decode("ascii").strip().split()
        expected = (("root", 4), ("bg", 4), ("txt", 4),
                    ("buttonLocal", 4), ("buttonRoot", 2),
                    ("enabled", 1), ("modelEnableBtn", 1), ("visible", 1),
                    ("wide", 1), ("dimmed", 1), ("driving", 1), ("calling", 1))
        if tokens[:2] != ["VM_OBSERVE_CONFIRM", "geometry"]:
            raise ValueError("missing Confirm geometry record")
        pos, parsed = 2, {}
        for key, count in expected:
            if pos >= len(tokens) or tokens[pos] != key:
                raise ValueError("malformed Confirm geometry fields")
            values = tokens[pos + 1:pos + 1 + count]
            if len(values) != count:
                raise ValueError("incomplete Confirm geometry")
            if key in ("root", "bg", "txt", "buttonLocal", "buttonRoot"):
                values = [float(value) for value in values]
                if not all(math.isfinite(value) for value in values):
                    raise ValueError("non-finite Confirm geometry")
                parsed[key] = values
            elif key == "modelEnableBtn":
                if values[0] not in ("0", "1"):
                    raise ValueError("invalid Confirm model enable value")
                parsed[key] = int(values[0])
            else:
                if values[0] not in ("true", "false"):
                    raise ValueError("invalid Confirm boolean")
                parsed[key] = values[0] == "true"
            pos += count + 1
        if pos != len(tokens):
            raise ValueError("ambiguous Confirm geometry")
        x, y = parsed["buttonRoot"]
        width, height = parsed["buttonLocal"][2:]
        if (parsed["root"] != [0.0, 0.0, 1920.0, 720.0] or width <= 0 or height <= 0
                or x < 0 or y < 0 or x + width > 1920 or y + height > 720):
            raise ValueError("Confirm geometry outside guest display")
        parsed["buttonRoot"] = [x, y, width, height]
        return parsed
    except (UnicodeError, IndexError, OverflowError) as exc:
        raise ValueError("invalid Confirm geometry record") from exc


class GuestAcquisitionError(RuntimeError):
    """A failed one-shot acquisition with its validated completed stages."""

    def __init__(self, stage: str, records: list, trace: bytes = b""):
        super().__init__("foreground acquisition failed: " + stage)
        self.stage, self.records, self.trace = stage, records, trace
        self.failure_detail = ""

    def __str__(self) -> str:
        detail = getattr(self, "failure_detail", "")
        return super().__str__() + (" (" + detail + ")" if detail else "")


def _vm_guest_reason11_call(detail: bytes, elapsed: int) -> dict:
    """Validate bounded transport evidence without retaining D-Bus error text."""
    match = re.fullmatch(
        rb"rc=([0-9]{1,3}) class=(" + b"|".join(item.encode() for item in _REASON11_DISPATCH_CLASSES) +
        rb") bytes=([0-9]{1,4})(?: clipped=(true|false))? "
        rb"duration_ms=([0-9]{1,6}|unavailable)", detail)
    if match is None:
        raise ValueError("invalid reason-11 dispatch evidence")
    result, response_bytes = match.group(2).decode(), int(match.group(3))
    clipped = (match.group(4) or b"false") == b"true"
    duration_raw = match.group(5)
    duration_ms = duration_raw.decode() if duration_raw == b"unavailable" else int(duration_raw)
    return_code = int(match.group(1))
    if (return_code > 255 or response_bytes > 1025 or clipped != (response_bytes == 1025) or
            (duration_ms != "unavailable" and duration_ms > elapsed) or
            (result == "reply" and return_code != 0) or
            (result == "wrapper_timeout" and return_code not in (124, 143)) or
            (result in ("dbus_no_reply", "dbus_service_unknown", "dbus_access_denied", "other_error") and
             return_code == 0)):
        raise ValueError("invalid reason-11 dispatch result")
    return {"exit_code": return_code, "result": result, "response_bytes": response_bytes,
            "clipped": clipped, "duration_ms": duration_ms}


def _vm_guest_reason11_failure_detail(dispatch: dict, diagnostic: Optional[dict] = None) -> str:
    """Describe one validated dispatch result in a short operator-facing message."""
    labels = {
        "dbus_no_reply": "D-Bus NoReply",
        "dbus_service_unknown": "D-Bus service disappeared",
        "dbus_access_denied": "D-Bus access denied",
        "wrapper_timeout": "D-Bus wrapper timed out",
        "empty_reply": "D-Bus returned no bytes",
        "other_error": "D-Bus transport failed",
        "reply": "D-Bus reply failed validation",
    }
    detail = labels[dispatch["result"]]
    if dispatch["duration_ms"] == "unavailable":
        detail += " after unavailable timing"
    else:
        detail += f" after {dispatch['duration_ms']} ms"
    if dispatch["result"] == "other_error":
        detail += f" (exit {dispatch['exit_code']})"
    if diagnostic is not None:
        stable = (diagnostic["owner"] == diagnostic["current_owner"] and
                  diagnostic["pid"] == diagnostic["current_pid"] and
                  diagnostic["starttime"] == diagnostic["current_starttime"])
        detail += "; service identity unchanged" if stable else "; service identity changed or unavailable"
    return detail


def _vm_guest_reason11_failure_diagnostic(error: GuestAcquisitionError) -> dict:
    """Retain validated dispatch evidence even when the DLT snapshot is unavailable."""
    diagnostic = getattr(error, "reason11_diagnostic", None)
    if not isinstance(diagnostic, dict):
        diagnostic = {"qualification": "UNQUALIFIED", "snapshot": "unavailable"}
    else:
        diagnostic = dict(diagnostic)
    dispatch = getattr(error, "reason11_dispatch", None)
    if isinstance(dispatch, dict):
        diagnostic["dispatch"] = dict(dispatch)
    return diagnostic


def vm_guest_validate_probe_arm(begin: dict, detail: bytes, elapsed: int) -> dict:
    """Bind an arm to the validated owner and monotonic acquisition epoch."""
    if not re.fullmatch(rb"pid=[1-9][0-9]* start=[1-9][0-9]* epoch=[1-9][0-9]* arm=[1-9][0-9]* deadline=[1-9][0-9]*", detail):
        raise ValueError("invalid IVI probe arm")
    values = {key: int(value) for key, value in (item.split("=", 1) for item in detail.decode('ascii').split())}
    if (begin['owner'] == 'unknown' or values['pid'] != begin['pid'] or values['pid'] > 2147483647 or
            values['deadline'] != values['epoch'] + VM_IVI_CAPTURE_DEADLINE_MS - 1 or not values['epoch'] <= values['arm'] < values['deadline'] or
            abs(values['arm'] - values['epoch'] - elapsed) > 20):
        raise ValueError("IVI probe epoch or identity mismatch")
    return values


def _vm_guest_verification_timings(samples: list[bytes], records: list) -> None:
    """Attach bounded, optional elapsed measurements to the admitted receipt."""
    bound = next((row for row in records if row["stage"] == "RECEIPT_BOUND"), None)
    arm = next((row for row in records if row["stage"] == "PROBE_ARM"), None)
    if (bound is None or arm is None or len(samples) != 1 or
            records[-1]["stage"] not in ("OK", "FAIL")):
        return
    epoch = vm_guest_validate_probe_arm(records[0], arm["detail"].encode("ascii"),
                                       arm["elapsed_ms"])["epoch"]
    identity = ("owner_query", "owner_parse", "pid_query", "pid_parse", "identity_check", "process_start")
    scan = ("boundary_stat", "boundary_prefix", "boundary_prior", "boundary_copy", "boundary_restat",
            "boundary_hash", "cache_precheck", "suffix_check", "cache_pair_hash", "cache_commit")
    expected = [(phase, operation) for phase, operations in (
        ("identity", identity), ("output", ("initial_stat", "digest", "final_stat")),
        ("identity_recheck", identity), ("scan_1", scan),
        ("identity_final", identity), ("scan_2", scan),
    ) for operation in ("begin", *operations)]
    fields = samples[0].split(b" ")
    if len(fields) > len(expected):
        return
    rows = []
    previous = bound["elapsed_ms"] - 1
    for field, (phase, operation) in zip(fields, expected):
        label, _, stamp = field.partition(b"=")
        if label != f"{phase}.{operation}".encode() or not re.fullmatch(rb"[0-9]{1,12}\.[0-9]{1,3}", stamp):
            return
        whole, fraction = stamp.split(b".")
        elapsed = int(whole) * 1000 + int(fraction.ljust(3, b"0")) - epoch
        if not max(0, previous) <= elapsed <= records[-1]["elapsed_ms"] + 1:
            return
        if operation != "begin":
            rows.append({"phase": phase, "operation": operation, "elapsed_ms": elapsed,
                         "duration_ms": elapsed - previous})
        previous = elapsed
    if rows:
        bound["verification_timings"] = rows


def vm_guest_parse_acquisition(data: bytes, token: str, *, ivi_probe: bool = False) -> tuple:
    """Validate ordered token records and retain a failure's completed stages."""
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token):
        raise ValueError("invalid acquisition token")
    if not isinstance(data, bytes) or len(data) > _MAX_REPLY:
        raise ValueError("invalid acquisition transcript size")
    marker = ("WB_ACQ_" + token).encode()
    trace_marker = ("WB_TRACE_" + token).encode()
    reason_marker = ("WB_REASON11_" + token).encode()
    reason_prefix_marker = ("WB_REASON11_PREFIX_" + token).encode()
    reason_phase_marker = ("WB_REASON11_PHASE_" + token).encode()
    timing_marker = ("WB_VERIFY_" + token + " ").encode()
    timing_samples = []
    reason_phase_records = []
    records, trace, reason_snapshot_records, reason_prefix_records, trace_invalid = [], [], [], [], False
    reason_call_records = []
    reason_call_dispatch = None
    normalized = _SERIAL_IRQ_WARNING.sub(b"", data).replace(b"\r\n", b"\n")
    if not normalized.endswith(b"\n"):
        last_line = normalized.split(b"\n")[-1]
        if ivi_probe and last_line.startswith(timing_marker):
            timing_samples.append(b"invalid")
        elif ivi_probe and last_line.startswith(reason_phase_marker + b" "):
            # The optional channel checks its own line ending below.
            pass
        elif marker in last_line:
            raise ValueError("truncated acquisition record")
        elif trace_marker in last_line:
            trace_invalid = True
    at_lf_boundary = True
    for physical_line in normalized.splitlines(keepends=True):
        starts_at_lf = at_lf_boundary
        at_lf_boundary = physical_line.endswith(b"\n")
        line = physical_line.rstrip(b"\r\n")
        if ivi_probe and line.startswith(timing_marker):
            if len(timing_samples) < 2:
                timing_samples.append(line[len(timing_marker):] if len(line) <= 4096 else b"invalid")
            # Even rejected timing metadata belongs only to the optional channel.
            continue
        if ivi_probe and reason_phase_marker in line:
            dedicated_phase_line = line.startswith(reason_phase_marker + b" ")
            if len(reason_phase_records) < 2:
                call_position = (len(records) == 5 and
                                 records[-1].startswith(b"REASON11_CALL ") and
                                 records[-2].startswith(b"REASON11_SENT "))
                valid_position = ((len(records) == 4 or call_position) and
                                  len(reason_snapshot_records) == 1 and
                                  starts_at_lf and at_lf_boundary)
                reason_phase_records.append(line[len(reason_phase_marker) + 1:]
                                            if dedicated_phase_line and valid_position and len(line) <= 128 else b"invalid")
            if dedicated_phase_line:
                continue
        if reason_prefix_marker in line:
            reason_prefix_records.append(line[len(reason_prefix_marker) + 1:] if line.startswith(reason_prefix_marker + b" ") and len(line) <= 512 else b"invalid")
        elif reason_marker in line:
            reason_snapshot_records.append(line[len(reason_marker) + 1:] if line.startswith(reason_marker + b" ") and len(line) <= 512 else b"invalid")
        if trace_marker in line:
            if not line.startswith(trace_marker + b" ") or len(line) > 128:
                trace_invalid = True
            else:
                trace.append(line[len(trace_marker) + 1:])
        if marker in line:
            if not line.startswith(marker + b" ") or len(line) > 4096:
                raise ValueError("malformed acquisition record")
            records.append(line[len(marker) + 1:])
    if not records or not re.fullmatch(rb"BEGIN owner=(?::[0-9]+[.][0-9]+|unknown) pid=(?:[1-9][0-9]*|0)", records[0]):
        raise ValueError("missing acquisition begin")
    order = ["BEGIN", "REASON11_SENT", "REASON11_ACK", "IVI_SENT", "IVI_ACK", "NATIVE", "MODEL", "CAPTURE_START", "VISIBILITY", "CAPTURE_DONE", "OK"]
    # The schema marker makes timing mandatory for newly generated probe
    # transcripts while retaining explicit read compatibility with old evidence.
    verify_phases = ("VERIFY_IDENTITY", "VERIFY_OUTPUT", "VERIFY_IDENTITY_RECHECK",
                     "VERIFY_LOG_SCAN_1", "VERIFY_IDENTITY_FINAL", "VERIFY_LOG_SCAN_2")
    timing_start = (f"VERIFY_START [0-9]{{1,5}} capture_deadline={VM_IVI_CAPTURE_DEADLINE_MS} "
                    f"verification_deadline={VM_IVI_VERIFICATION_DEADLINE_MS} timing_schema=1").encode()
    timed_probe = ivi_probe and any(re.fullmatch(timing_start, row) for row in records)
    if ivi_probe:
        order = ["BEGIN", "PROBE_ARM", "BASELINE", "REASON11_SENT", "REASON11_ACK", "OBSERVE", "IVI_SENT", "IVI_ACK", "NATIVE", "MODEL", "VERIFY_START", "RECEIPT_BOUND", "VISIBILITY", "PROBE_CAPTURE", "VERIFY_DONE", "OK"]
        if timed_probe:
            order[12:12] = verify_phases
    decoded, model, last_ms = [], None, -1
    for index, record in enumerate(records):
        if index == 0:
            fields = record.decode("ascii").split()
            decoded.append({"stage": "BEGIN", "owner": fields[1][6:], "pid": int(fields[2][4:])})
            continue
        parts = record.split(b" ", 2)
        try:
            name = parts[0].decode("ascii")
        except UnicodeError as exc:
            raise ValueError("invalid acquisition stage") from exc
        if name == "FAIL":
            if index != len(records) - 1 or any(row.get("stage") == "OK" for row in decoded) or len(parts) != 3:
                raise ValueError("invalid acquisition failure")
            legacy_failure = re.fullmatch(
                rb"[a-z0-9_]{1,32} cutoff=(?:10000|15000|20000|30000|60000) diagnostic_ms=[0-9]{1,7}", parts[2])
            native_timeout = re.fullmatch(
                rb"native_timeout native_marker=(timeout_handler|clock_engine_timeout|confirm_sk_pressed) "
                rb"marker_offset=([0-9]{1,7}) cutoff=(?:10000|15000|20000|30000|60000) diagnostic_ms=[0-9]{1,7}", parts[2])
            if ((legacy_failure is None and native_timeout is None) or
                    (native_timeout is not None and int(native_timeout.group(2)) > 1048575)):
                raise ValueError("invalid acquisition failure")
            verified = ivi_probe and any(row.get("stage") == "VERIFY_START" for row in decoded)
            probe_armed = ivi_probe and any(row.get("stage") == "PROBE_ARM" for row in decoded)
            expected_cutoff = (VM_IVI_VERIFICATION_DEADLINE_MS if verified else
                               VM_IVI_CAPTURE_DEADLINE_MS if probe_armed else VM_IVI_SETUP_DEADLINE_MS)
            if b"cutoff=" + str(expected_cutoff).encode() not in parts[2]:
                raise ValueError("invalid acquisition failure cutoff")
        elif name == "REASON11_CALL":
            if not decoded or decoded[-1].get("stage") != "REASON11_SENT":
                raise ValueError("invalid reason-11 dispatch ordering")
        else:
            dispatched = sum(row.get("stage") == "REASON11_CALL" for row in decoded)
            expected_index = index - dispatched
            if expected_index >= len(order) or name != order[expected_index]:
                raise ValueError("duplicate or out-of-order acquisition stage")
        if len(parts) < 2 or not re.fullmatch(rb"[0-9]{1,5}", parts[1]):
            raise ValueError("invalid acquisition elapsed time")
        elapsed = int(parts[1])
        verify_stage = ivi_probe and name in ("RECEIPT_BOUND", "VISIBILITY", "PROBE_CAPTURE", "VERIFY_DONE", "OK", *verify_phases)
        elapsed_limit = (VM_IVI_VERIFICATION_DEADLINE_MS if verify_stage else
                         VM_IVI_CAPTURE_DEADLINE_MS if ivi_probe else VM_IVI_SETUP_DEADLINE_MS)
        if elapsed < last_ms or (name not in ("FAIL", "CAPTURE_RETURN", "REASON11_CALL") and
                                 elapsed >= elapsed_limit):
            raise ValueError("invalid acquisition deadline or ordering")
        last_ms = elapsed
        extra = parts[2] if len(parts) == 3 else b""
        if name == "REASON11_ACK" and not re.fullmatch(rb"sender=:[0-9]+[.][0-9]+ dest=:[0-9]+[.][0-9]+ reply_serial=[1-9][0-9]*", extra):
            raise ValueError("invalid reason-11 acknowledgement")
        if name == "REASON11_CALL":
            reason_call_dispatch = _vm_guest_reason11_call(extra, elapsed)
            reason_call_records.append(extra)
        if (name == "REASON11_ACK" and reason_call_dispatch is not None and
                reason_call_dispatch["result"] == "reply" and reason_call_dispatch["clipped"]):
            raise ValueError("clipped reason-11 acknowledgement")
        if name == "IVI_ACK" and extra != b"status=0 ack=IVI_FG_REQUEST_SENT":
            raise ValueError("invalid IVI acknowledgement")
        if name == "NATIVE" and not re.fullmatch(rb"entry=[0-9]+ show=[0-9]+ draw_start=[0-9]+ model=[0-9]+ draw_end=[0-9]+ native_return=[0-9]+ timestamps=(?:[0-9:.]+,){5}[0-9:.]+", extra):
            raise ValueError("invalid native sequence metadata")
        if name == "NATIVE":
            offsets = [int(field.split(b"=")[1]) for field in extra.split()[:6]]
            if any(a >= b for a, b in zip(offsets, offsets[1:])):
                raise ValueError("native sequence offsets are out of order")
        if name == "VISIBILITY" and not re.fullmatch(rb"button_hidden=[0-9]{1,5}", extra):
            raise ValueError("invalid button visibility evidence")
        if name == "PROBE_ARM":
            vm_guest_validate_probe_arm(decoded[0], extra, elapsed)
        if name == "BASELINE" and not re.fullmatch(rb"time=[1-9][0-9]{0,19} size=[1-9][0-9]{0,7} format=(?:537004168|537036936) buffer=0x[0-9a-f]{1,16} surface=0x[0-9a-f]{1,16} output=0x[0-9a-f]{1,16} sha256=[0-9a-f]{64} ack_sha=[0-9a-f]{64}", extra):
            raise ValueError("invalid IVI baseline")
        if ivi_probe and name == "REASON11_SENT" and not re.fullmatch(rb"monotonic=[1-9][0-9]{0,19}", extra):
            raise ValueError("invalid reason-11 dispatch time")
        if name == "OBSERVE" and not re.fullmatch(rb"monotonic=[1-9][0-9]{0,19}", extra):
            raise ValueError("invalid observation start time")
        expected_verify_extra = (f"capture_deadline={VM_IVI_CAPTURE_DEADLINE_MS} "
                                 f"verification_deadline={VM_IVI_VERIFICATION_DEADLINE_MS}" +
                                 (" timing_schema=1" if timed_probe else "")).encode()
        if name in ("VERIFY_START", "VERIFY_DONE") and extra != expected_verify_extra:
            raise ValueError("invalid verification deadline")
        if name == "RECEIPT_BOUND" and not re.fullmatch(rb"capture=[1-9][0-9]{0,19}", extra):
            raise ValueError("invalid bound receipt time")
        if name == "PROBE_CAPTURE" and not re.fullmatch(rb"capture=[1-9][0-9]{0,19} sequence=1 width=1920 height=720 format=(?:537004168|537036936) size=5529600 sha256=[0-9a-f]{64} receipt_sha=[0-9a-f]{64} baseline_time=[1-9][0-9]{0,19} baseline_size=[1-9][0-9]{0,7} baseline_format=(?:537004168|537036936) baseline_buffer=0x[0-9a-f]{1,16} selected_buffer=0x[0-9a-f]{1,16} observations=[1-9][0-9]{0,2} baseline_sha=[0-9a-f]{64} ack_sha=[0-9a-f]{64} observation_start=[1-9][0-9]{0,19} mode=source-content-change", extra):
            raise ValueError("invalid IVI probe capture")
        if name == "MODEL":
            model = vm_guest_parse_confirm_geometry(extra)
        elif name == "CAPTURE_DONE":
            if not re.fullmatch(rb"size=[1-9][0-9]{0,7} sha256=[0-9a-f]{64}", extra):
                raise ValueError("invalid capture metadata")
        elif name not in ("REASON11_CALL", "REASON11_ACK", "IVI_ACK", "NATIVE", "VISIBILITY", "FAIL", "PROBE_ARM", "BASELINE", "OBSERVE", "PROBE_CAPTURE", "VERIFY_START", "RECEIPT_BOUND", "VERIFY_DONE") and not (ivi_probe and name == "REASON11_SENT") and extra:
            raise ValueError("unexpected acquisition stage fields")
        decoded.append({"stage": name, "elapsed_ms": elapsed, "detail": extra.decode("ascii", errors="strict")})
        if name == "FAIL":
            if int(extra.rsplit(b"=", 1)[1]) < elapsed:
                raise ValueError("invalid failure diagnostic completion time")
            if trace_invalid:
                if extra.decode().split()[0] != "reason11":
                    raise ValueError("malformed acquisition trace")
                trace, reason_snapshot_records, reason_prefix_records = [], [], []
            try:
                raw_trace = base64.b64decode(b"".join(trace), validate=True) if trace else b""
            except (ValueError, binascii.Error) as exc:
                if extra.decode().split()[0] != "reason11":
                    raise ValueError("invalid acquisition failure trace") from exc
                raw_trace, reason_snapshot_records, reason_prefix_records = b"", [], []
            if len(raw_trace) > 1048576:
                if extra.decode().split()[0] != "reason11":
                    raise ValueError("acquisition failure trace exceeds limit")
                raw_trace, reason_snapshot_records, reason_prefix_records = b"", [], []
            if timed_probe:
                _vm_guest_verification_timings(timing_samples, decoded)
            error = GuestAcquisitionError(extra.decode().split()[0], decoded, raw_trace)
            dispatch = None
            if reason_call_records:
                call_rows = [row for row in decoded if row.get("stage") == "REASON11_CALL"]
                if len(call_rows) != 1:
                    raise ValueError("invalid reason-11 dispatch evidence")
                dispatch = reason_call_dispatch
                if error.stage == "reason11":
                    error.reason11_dispatch = dispatch
                    error.failure_detail = _vm_guest_reason11_failure_detail(dispatch)
            if reason_snapshot_records or reason_prefix_records:
                states = b"|".join(value.encode("ascii") for value in _REASON11_SNAPSHOT_STATES)
                snapshot_record = reason_snapshot_records[0] if len(reason_snapshot_records) == 1 else None
                prefix_record = reason_prefix_records[0] if len(reason_prefix_records) == 1 else None
                diagnostic_records = reason_snapshot_records + reason_prefix_records
                match = (re.fullmatch(rb"epoch=([0-9]{1,16}) owner=(:[0-9]+[.][0-9]+) pid=([1-9][0-9]*) start=([0-9]+) current_owner=(:[0-9]+[.][0-9]+|unknown) current_pid=([0-9]+) current_start=([0-9]+) snapshot=(" + states + rb")", snapshot_record)
                         if error.stage == "reason11" and snapshot_record is not None and
                         len(reason_prefix_records) <= 1 and
                         not any(b"\n" in value or b"\r" in value for value in diagnostic_records)
                         else None)
                if match:
                    epoch, owner, pid, start, current_owner, current_pid, current_start, snapshot = match.groups()
                    valid = (owner.decode() == decoded[0]["owner"] and int(pid) == decoded[0]["pid"] and
                        0 < int(epoch) and 0 < int(start) and int(pid) <= 2147483647 and int(current_pid) <= 2147483647 and
                        (snapshot == b"ok" or not raw_trace) and len(raw_trace) <= 262144 and
                        len(raw_trace.splitlines()) <= 2048 and all(len(line) <= 4096 for line in raw_trace.splitlines()))
                    complete_prefix = {
                        "evidence": "insufficient_evidence",
                        "handler_entry_observation": "insufficient_evidence",
                        "draw_progress_observation": "insufficient_evidence",
                        "record_count": 0,
                        "absence_not_proven": True,
                    }
                    if prefix_record is not None:
                        prefix_states = rb"(?:observed|not_observed_in_complete_prefix|insufficient_evidence)"
                        prefix = re.fullmatch(
                            rb"evidence=(complete_prefix|insufficient_evidence) handler_entry=" + prefix_states +
                            rb" draw_progress=" + prefix_states + rb" records=([0-9]{1,4})",
                            prefix_record)
                        if prefix is None or int(prefix.group(2)) > 2048 or snapshot != b"newline_check_failed":
                            valid = False
                        elif valid:
                            fields = prefix_record.split()
                            observations = [fields[1].split(b"=", 1)[1], fields[2].split(b"=", 1)[1]]
                            count = int(prefix.group(2))
                            if prefix.group(1) == b"complete_prefix" and b"insufficient_evidence" not in observations:
                                complete_prefix = {
                                    "evidence": "complete_prefix",
                                    "handler_entry_observation": observations[0].decode(),
                                    "draw_progress_observation": observations[1].decode(),
                                    "record_count": count,
                                    "absence_not_proven": True,
                                }
                            elif (prefix.group(1) != b"insufficient_evidence" or count != 0 or
                                  observations != [b"insufficient_evidence", b"insufficient_evidence"]):
                                valid = False
                    if valid:
                        error.reason11_diagnostic = {"qualification": "UNQUALIFIED", "epoch_ms": int(epoch),
                            "owner": owner.decode(), "pid": int(pid), "starttime": int(start),
                            "current_owner": current_owner.decode(), "current_pid": int(current_pid),
                            "current_starttime": int(current_start), "snapshot": snapshot.decode(),
                            "trace_base64": base64.b64encode(raw_trace).decode(),
                            "complete_prefix": complete_prefix}
                        if dispatch is not None:
                            error.reason11_diagnostic["dispatch"] = dispatch
                            error.failure_detail = _vm_guest_reason11_failure_detail(
                                dispatch, error.reason11_diagnostic)
                        stages = [row["stage"] for row in decoded]
                        if (ivi_probe and reason_phase_records and
                                stages in (
                                    ["BEGIN", "PROBE_ARM", "BASELINE", "REASON11_SENT", "FAIL"],
                                    ["BEGIN", "PROBE_ARM", "BASELINE", "REASON11_SENT",
                                     "REASON11_CALL", "FAIL"],
                                )):
                            native_phase = "unavailable"
                            arm = dict(field.split("=", 1) for field in decoded[1]["detail"].split())
                            if (len(reason_phase_records) == 1 and
                                    owner == current_owner and pid == current_pid and start == current_start and
                                    int(arm["start"]) == int(start) and int(arm["epoch"]) == int(epoch) and
                                    (snapshot == b"ok" or complete_prefix["evidence"] == "complete_prefix")):
                                native_phase = next((phase for phase in _REASON11_NATIVE_PHASES
                                                     if reason_phase_records[0] == b"phase=" + phase.encode()), "unavailable")
                            error.reason11_diagnostic["native_phase"] = native_phase
            raise error
    if len(records) != len(order) + len(reason_call_records) or model is None:
        raise ValueError("incomplete acquisition transcript")
    if trace_invalid:
        raise ValueError("malformed acquisition trace")
    if ivi_probe and (not model["enabled"] or model["modelEnableBtn"] != 1 or not model["visible"] or
                      model["dimmed"] or model["driving"] or model["calling"]):
        raise ValueError("IVI acquisition model is restricted")
    frame = b""
    if not ivi_probe:
        frame = vm_guest_decode_capture(data, token)
        expected = next(row for row in decoded if row["stage"] == "CAPTURE_DONE")["detail"].split()
        if int(expected[0][5:]) != len(frame) or expected[1][7:] != hashlib.sha256(frame).hexdigest():
            raise ValueError("capture metadata does not match frame")
    if ivi_probe:
        arm = next(row for row in decoded if row["stage"] == "PROBE_ARM")
        capture = next(row for row in decoded if row["stage"] == "PROBE_CAPTURE")
        values = vm_guest_validate_probe_arm(decoded[0], arm["detail"].encode('ascii'), arm["elapsed_ms"])
        cap = dict(item.split("=", 1) for item in capture["detail"].split())
        baseline = dict(item.split("=", 1) for item in next(row for row in decoded if row["stage"] == "BASELINE")["detail"].split())
        reason_row = next(row for row in decoded if row["stage"] == "REASON11_SENT")
        reason_ms = int(reason_row["detail"].split("=", 1)[1])
        ack_row = next(row for row in decoded if row["stage"] == "REASON11_ACK")
        observe_row = next(row for row in decoded if row["stage"] == "OBSERVE")
        observe_ms = int(observe_row["detail"].split("=", 1)[1])
        bound = next(row for row in decoded if row["stage"] == "RECEIPT_BOUND")
        epoch, at, deadline, taken = values["epoch"], values["arm"], values["deadline"], int(cap["capture"])
        ack = f"{token} {values['pid']} {values['start']} {baseline['time']} {baseline['size']} {baseline['format']} {baseline['buffer']} {baseline['surface']} {baseline['output']} {baseline['sha256']}\n".encode()
        if (not epoch <= int(baseline['time']) <= reason_ms <= observe_ms <= taken < deadline or
                observe_ms < epoch + ack_row['elapsed_ms'] or abs(observe_ms - epoch - observe_row['elapsed_ms']) > 20 or
                int(cap['observation_start']) != observe_ms or int(bound['detail'].split('=', 1)[1]) != taken or
                abs(reason_ms - epoch - reason_row['elapsed_ms']) > 20 or taken > epoch + bound["elapsed_ms"] + 20 or
                int(baseline['size']) > _IVI_FRAME_LIMIT or int(cap['observations']) > 100 or
                hashlib.sha256(ack).hexdigest() != baseline['ack_sha'] or
                any(cap[k] != baseline[v] for k, v in (("baseline_time", "time"), ("baseline_size", "size"), ("baseline_format", "format"), ("baseline_buffer", "buffer"), ("baseline_sha", "sha256"), ("ack_sha", "ack_sha")))):
            raise ValueError("IVI probe epoch or identity mismatch")
        if timed_probe:
            _vm_guest_verification_timings(timing_samples, decoded)
    return model, frame, decoded


def _vm_guest_cache_scanner(script: str) -> str:
    """Cache completed log records while retaining the full boundary hashes.

    The parent shell anchors each state inode and digest across substitutions.
    AWK reads the bounded state as data; it never evaluates persisted text.
    Incomplete lines stay outside the admitted cursor and are reparsed later.
    """
    begin = script.index('check_lines() {')
    end = script.index('\n[ ! -e "$scan" ]', begin)
    original = script[begin:end]
    policy_start = original.index('    function validmodel(')
    policy_end = original.index('    {if(NR>8192)')
    policy = original[policy_start:policy_end]
    decision = original.split('if(bad!="") print "FAIL " bad;', 1)[1]
    decision = 'if(bad!="") print "FAIL " bad;' + decision.split("' \"$scan\"", 1)[0]
    # Keep the policy and READY formatting byte-for-byte. Only record iteration
    # and state transport change; the boundary still admits every prior byte.
    decision = decision.removesuffix('}')
    cached = r'''scan_cache_cleanup() {
  for cache_path in "$cache" "$cache_next"; do
    cache_want=$cache_id; [ "$cache_path" != "$cache_next" ] || cache_want=$cache_next_id
    [ -n "$cache_want" ] && [ ! -L "$cache_path" ] && [ -f "$cache_path" ] || continue
    cache_seen=$($BB stat -c '%d:%i' "$cache_path") || continue
    [ "$cache_seen" != "$cache_want" ] || $BB rm -f "$cache_path"
  done
}
scan_cache_stat() {
  [ -f "$1" ] && [ ! -L "$1" ] || return 1
  cache_stat=$($BB stat -c '%d:%i:%s:%u:%a:%h' "$1") || return 1
  scan_cache_stat_fields
}
scan_cache_stat_fields() {
  cache_identity=${cache_stat%:*:*:*:*}; cache_meta=${cache_stat#"$cache_identity":}
  cache_bytes=${cache_meta%%:*}
  case "$cache_bytes" in ''|*[!0-9]*) return 1;; esac
  [ "$cache_bytes" -le 8192 ] && [ "$cache_meta" = "$cache_bytes:0:600:1" ]
}
scan_cache_pair() {
  [ -f "$cache" ] && [ ! -L "$cache" ] && [ -f "$cache_next" ] && [ ! -L "$cache_next" ] || return 1
  stats=$($BB stat -c '%d:%i:%s:%u:%a:%h' "$cache" "$cache_next") || return 1
  scan_split_pair "$stats" || return 1
  cache_stat=$scan_first
  scan_cache_stat_fields && [ "$cache_identity" = "$cache_id" ] || return 1
  cache_current_bytes=$cache_bytes
  cache_stat=$scan_second
  scan_cache_stat_fields && [ "$cache_identity" = "$cache_next_id" ]
}
scan_cache_init() {
  for cache_path in "$cache" "$cache_next"; do
    [ ! -e "$cache_path" ] && [ ! -L "$cache_path" ] || return 1
    (umask 077; set -C; : > "$cache_path") 2>/dev/null || return 1
    cache_seen=$($BB stat -c '%d:%i' "$cache_path") || return 1
    if [ "$cache_path" = "$cache" ]; then cache_id=$cache_seen; else cache_next_id=$cache_seen; fi
    scan_cache_stat "$cache_path" || return 1
  done
  # The empty first state is accepted only by this acquisition's first scan.
  cache_hash=$($BB sha256sum "$cache") || return 1
  cache_hash=${cache_hash%% *}; cache_cursor=0; cache_started=0
}
check_lines() {
  complete=0
  [ "$size" -eq "$base" ] || [ "$($BB tail -c 1 "$scan" | $BB wc -l)" -eq 0 ] || complete=1
  scan_cache_pair || return 1
  current_digest=$($BB sha256sum "$cache") || return 1
  [ "${current_digest%% *}" = "$cache_hash" ] || return 1
  [ "$cache_cursor" -le "$((size-base))" ] || return 1
  # Feed only bytes following the previously completed record. State is a
  # separate file so arbitrary model text can never become an AWK assignment.
  (set -o pipefail; $BB tail -c +"$((cache_cursor+1))" "$scan" | LC_ALL=C $BB awk \
    -v re='__PATTERN__' -v complete="$complete" -v partial="$partial" -v base="$base" \
    -v state="$cache" -v nextstate="$cache_next" -v token='__TOKEN__' \
    -v identity="$base_id" -v expected_cursor="$cache_cursor" -v started="$cache_started" \
    -v capture_ms="${capture_ms:-0}" '
__POLICY__
    function uint(s, maximum) {return s ~ /^(0|[1-9][0-9]*)$/ && s+0<=maximum}
    function state_fail() {invalid=1;exit 2}
    function loadstate( i) {
      if(!started) {if(state_rows) state_fail(); n=0;lines=0;phase=0;hidden=0;return}
      if(state_rows!=22 || saved[1]!=token || saved[2]!=base || saved[3]!=identity || saved[4]!=partial ||
         !uint(saved[5],1048576) || saved[5]!=expected_cursor || !uint(saved[6],8192) ||
         !uint(saved[7],6) || !uint(saved[8],8192) || length(saved[9])>4096 || saved[10]!="") state_fail()
      n=saved[5]+0;lines=saved[6]+0;phase=saved[7]+0;hidden=saved[8]+0;model=saved[9]
      if((n==0)!=(lines==0) || lines>n || (phase<4 && model!="") || (phase>=4 && !validmodel(model))) state_fail()
      for(i=1;i<=6;i++) {
        offsets[i]=saved[9+2*i];stamps[i]=saved[10+2*i]
        if(!uint(offsets[i],base+n) || (i>phase && (offsets[i]!=0 || stamps[i]!="")) ||
           (i<=phase && (offsets[i]<base || offsets[i]>=base+n || stamps[i]!~/^[0-9:.]+$/ ||
             (i>1 && offsets[i]<=offsets[i-1])))) state_fail()
      }
    }
    FILENAME==state {if(++state_rows>22 || length($0)>4096) state_fail();saved[state_rows]=$0;next}
    {
      if(!loaded) {loadstate();loaded=1}
      records++;startpos=n;n+=length($0)+1
      if(lines+records>8192) {bad="line_limit";exit}
      sub(/\r$/, "")
      if(records>1 && !(partial && lines+records==2)) check(prev,prev_start)
      prev=$0;prev_start=startpos
    }
    END {
      if(invalid) exit 2
      if(!loaded) {loadstate();loaded=1}
      if(complete && records && !(partial && lines+records==1)) check(prev,prev_start)
      # The final incomplete record was counted for the same limit precedence
      # as a full scan, but is never persisted as parsed policy state.
      if(records && !complete) {n=prev_start;records--}
      __DECISION__
      if(bad!="") exit
      print token > nextstate;printf "%.0f\n",base >> nextstate;print identity >> nextstate;print partial >> nextstate
      printf "%.0f\n",n >> nextstate;print lines+records >> nextstate;print phase+0 >> nextstate;print hidden+0 >> nextstate
      print model >> nextstate;print "" >> nextstate
      for(i=1;i<=6;i++) {printf "%.0f\n",offsets[i]+0 >> nextstate;print stamps[i] >> nextstate}
      if(close(nextstate)!=0) exit 2
    }' "$cache" -) || return 1
}
scan_result() {
  # Run in the parent shell: these anchors must survive command substitution.
  scan_cache_stat "$cache" && [ "$cache_identity" = "$cache_id" ] || return 1
  cache_before=$cache_bytes
  result=$(check_lines)
  cache_scan_status=$?
  # A policy rejection remains authoritative when its early exit gives the
  # suffix reader SIGPIPE. READY/PENDING require both pipeline stages to finish
  # successfully, so a short/failed reader can never reuse an earlier READY.
  case "$result" in FAIL\ *) return 0;; READY\ *|PENDING) [ "$cache_scan_status" -eq 0 ] || return 1;; *) return 1;; esac
  scan_cache_pair && [ "$cache_current_bytes" = "$cache_before" ] && [ "$cache_bytes" -gt 0 ] || return 1
  digests=$($BB sha256sum "$cache" "$cache_next") || return 1
  scan_split_pair "$digests" || return 1
  [ "$scan_first" = "$cache_hash  $cache" ] || return 1
  cache_next_hash=${scan_second%% *}
  [ "$scan_second" = "$cache_next_hash  $cache_next" ] || return 1
  case "$cache_next_hash" in ''|*[!0-9a-f]*) return 1;; esac
  [ "${#cache_next_hash}" -eq 64 ] || return 1
  # Recheck the scratch inode after reading both hashes, before committing
  # any bytes to the current cache.
  scan_cache_stat "$cache_next" && [ "$cache_identity" = "$cache_next_id" ] || return 1
  # Commit into the original inode. An interrupted or short write cannot match
  # the expected digest on this scan or on a later invocation.
  $BB cat "$cache_next" > "$cache" || return 1
  scan_cache_stat "$cache" && [ "$cache_identity" = "$cache_id" ] || return 1
  current_digest=$($BB sha256sum "$cache") || return 1
  [ "${current_digest%% *}" = "$cache_next_hash" ] || return 1
  cache_hash=$cache_next_hash
  # The fifth record is the cursor in the just-verified state. Keep the
  # anchor update in this shell and avoid a separate reader process.
  {
    for cache_header in token base identity partial; do IFS= read -r cache_unused || return 1; done
    IFS= read -r cache_cursor || return 1
  } < "$cache"
  case "$cache_cursor" in ''|*[!0-9]*) return 1;; esac
  [ "$cache_cursor" -le "$((size-base))" ] || return 1
  cache_started=1
}'''
    cached = cached.replace('__POLICY__', policy).replace('__DECISION__', decision)
    script = script[:begin] + cached + script[end:]
    script = script.replace('scan_owned=0', 'scan_owned=0\ncache=/tmp/wb-acq-__TOKEN__.state\ncache_next=/tmp/wb-acq-__TOKEN__.next\ncache_id=\ncache_next_id=', 1)
    script = script.replace('  [ "$scan_owned" != 1 ] || $BB rm -f "$scan"',
                            '  scan_cache_cleanup\n  [ "$scan_owned" != 1 ] || $BB rm -f "$scan"', 1)
    script = script.replace('last_size=$base; last_hash=empty',
                            'last_size=$base; last_hash=empty\ntrap \'scan_cache_cleanup\' 0\nscan_cache_init || fail log_preflight', 1)
    script = script.replace('result=$(check_lines) || fail log_parse', 'scan_result || fail log_parse')
    script = script.replace('$BB rm -f "$scan"\n)', 'scan_cache_cleanup\n$BB rm -f "$scan"\n)')
    return script


def _vm_guest_instrument_verification(script: str) -> str:
    """Sample shared check boundaries in the probe's post-receipt phase."""
    timing = r'''
verify_phase=
verify_samples=
verify_mark() {
  [ -n "$verify_phase" ] || return 0
  read -r verify_uptime _ </proc/uptime || return 0
  verify_samples="$verify_samples $verify_phase.$1=$verify_uptime"
}
verify_emit() {
  # Flush only after the terminal result, outside the measured checks.
  [ -z "$verify_samples" ] || printf '\nWB_VERIFY___TOKEN__%s\n' "$verify_samples"
}
'''
    script = script.replace("\nnow() {", timing + "\nnow() {", 1)
    # These anchors remain in the parent shell so the samples survive command
    # substitution without adding data to the parser output or applet calls.
    for anchor, operation in (
        ('  [ "${#own}" -le 1024 ] || return 1', "owner_query"),
        ('  [ "${#pid_reply}" -le 1024 ] || return 1', "pid_query"),
        ('  kill -0 "$pid_now" 2>/dev/null', "pid_parse"),
        ('  [ "$ident" = "$base_id" ] && [ "$size" -ge "$last_size" ] && [ "$((size-base))" -le 1048576 ] || return 1', "boundary_stat"),
        ('  [ "$hash" = "$base_hash" ] || return 1', "boundary_prefix"),
        ('  [ "$oldhash" = "$last_hash" ] || return 1', "boundary_prior"),
        ('  stats=$($BB stat -c \'%d:%i:%s\' "$log" "$scan") || return 1', "boundary_copy"),
        ('  [ "${after%:*}" = "$base_id" ] && [ "${after##*:}" -ge "$size" ] || return 1', "boundary_restat"),
        ('  last_size=$size', "boundary_hash"),
        ('  cache_before=$cache_bytes', "cache_precheck"),
        ('  cache_scan_status=$?', "suffix_check"),
        ('  [ "${#cache_next_hash}" -eq 64 ] || return 1', "cache_pair_hash"),
        ('  cache_started=1', "cache_commit"),
    ):
        mark = f"  verify_mark {operation}"
        if operation in ("pid_parse", "boundary_copy"):
            script = script.replace(anchor, mark + "\n" + anchor, 1)
        else:
            script = script.replace(anchor, anchor + "\n" + mark, 1)
    script = script.replace('  pid_reply=$($BB timeout', '  verify_mark owner_parse\n  pid_reply=$($BB timeout', 1)
    script = script.replace('  exit 0\n}\nidentity() {', '  verify_emit\n  exit 0\n}\nidentity() {', 1)
    return script


def _vm_guest_instrument_reason11_phase(script: str) -> str:
    """Bracket the IVI foreground call with optional byte fences for failure evidence."""
    # Use the same IVI native/model policy as the successful scan. The failure
    # pass only changes record selection and emits a fixed phase label.
    scanner = script[script.index("check_lines() {"):]
    policy = scanner[scanner.index("    function validmodel("):scanner.index("    {if(NR>8192)")]
    policy = policy.replace("temporal =  *false/", "temporal =  *false([][:space:]]|$)/", 1)
    functions = r'''# REASON11_PHASE_HELPERS_BEGIN
reason_phase_fence() {
  [ -f "$log" ] && [ ! -L "$log" ] || return 1
  phase_stat=$($BB timeout 1 $BB stat -c '%d:%i:%s' "$log" 2>/dev/null) || return 1
  phase_size=${phase_stat##*:}
  case "$phase_size" in ''|*[!0-9]*) return 1;; esac
  [ "${phase_stat%:*}" = "$base_id" ] && [ "$phase_size" -ge "$base" ] 2>/dev/null &&
    [ "$((phase_size-base))" -le 262144 ] || return 1
  printf '%s\n' "$phase_size"
}
reason_native_phase() {
  [ -n "$reason_send_fence" ] && [ -n "$reason_fail_fence" ] &&
    [ "$reason_fail_fence" -ge "$reason_send_fence" ] &&
    [ "$reason_size" -ge "$reason_fail_fence" ] &&
    [ "$reason_owner:$reason_pid:$reason_current_start" = "$owner:$pid:$reason_start" ] &&
    [ "$proc_start" = "$reason_start" ] || return 1
  # Offsets include the newline byte. Keep one pending record so that a
  # record crossing either fence or lacking a final newline stays excluded.
  LC_ALL=C $BB timeout 2 $BB awk -v re='__PATTERN__' -v base=0 -v partial="$partial" \
    -v lower="$((reason_send_fence-base))" -v upper="$((reason_fail_fence-base))" \
    -v complete="$reason_last" -v bytes="$((reason_size-base))" -v labels='__PHASES__' '
__PHASE_POLICY__
    function admitted() {
      if(!(partial && previous_index==1) && previous_start>=lower && previous_end<=upper)
        check(previous,previous_start)
    }
    {
      if(NR>2048 || length($0)>4096) {invalid=1; exit}
      if(NR>1) admitted()
      previous_start=position; position+=length($0)+1; previous_end=position
      sub(/\r$/, ""); previous=$0; previous_index=NR
    }
    END {
      if(invalid || position-(!complete && NR>0)!=bytes) exit 1
      if(complete && NR) admitted()
      if(bad!="") exit 1
      split(labels,names," "); print names[phase+1]
    }' "$scan"
}
# REASON11_PHASE_HELPERS_END
'''
    script = script.replace("reason_failure_snapshot() {", functions.replace("__PHASE_POLICY__", policy)
                            .replace("__PHASES__", " ".join(_REASON11_NATIVE_PHASES)) +
                            "reason_failure_snapshot() {", 1)
    script = script.replace('    reason_failure_snapshot\n', r'''    # REASON11_PHASE_FAILURE_FENCE_BEGIN
    reason_fail_fence=
    if [ -n "${reason_send_fence:-}" ]; then reason_fail_fence=$(reason_phase_fence) || reason_fail_fence=; fi
    # REASON11_PHASE_FAILURE_FENCE_END
    reason_failure_snapshot
''', 1)
    script = script.replace('    [ "$reason_status" = ok ] || : > "$scan"', r'''    # REASON11_PHASE_SCAN_BEGIN
    reason_phase=unavailable
    if [ "$reason_status" = ok ] || [ "$reason_prefix" = complete_prefix ]; then
      reason_phase=$(reason_native_phase) || reason_phase=unavailable
    fi
    # REASON11_PHASE_SCAN_END
    [ "$reason_status" = ok ] || : > "$scan"''', 1)
    script = script.replace('\n}\nboundary() {', r'''
  # REASON11_PHASE_EMIT_BEGIN
  printf 'WB_REASON11_PHASE___TOKEN__ phase=%s\n' "${reason_phase:-unavailable}"
  # REASON11_PHASE_EMIT_END
}
boundary() {''', 1)
    return script


def vm_guest_acquisition_command(token: str, *, ivi_probe: bool = False) -> str:
    """Construct the single bounded guest foreground/model/capture transaction."""
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token):
        raise ValueError("invalid acquisition token")
    script = r'''(
BB=/bin/busybox
set -o pipefail
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
log=/tmp/launcher-chain/dlt.log
scan=/tmp/wb-acq-__TOKEN__.dlt
start=0
elapsed=0
begun=0
scan_owned=0
failure_cutoff=10000
emit() { printf '\nWB_ACQ___TOKEN__ %s\n' "$*"; }
now() {
  read -r current _ </proc/uptime || return 1
  elapsed=$($BB awk -v a="$start" -v b="$current" 'BEGIN {if(a<0 || b<a) exit 1; printf "%d",int((b-a)*1000)}') || return 1
  case "$elapsed" in ''|*[!0-9]*) return 1;; esac
}
budget() { now && [ "$elapsed" -lt "$failure_cutoff" ] || fail deadline; }
fail() {
  stage=$1
  [ "$begun" = 1 ] || emit 'BEGIN owner=unknown pid=0'
  [ "$start" = 0 ] || now || elapsed=$failure_cutoff
  failure_elapsed=$elapsed
  if [ "$stage" = reason11 ] && [ "${reason_epoch:-0}" -gt 0 ] 2>/dev/null && [ "${reason_start:-0}" -gt 0 ] 2>/dev/null; then
    reason_failure_snapshot
  fi
  if [ "$scan_owned" = 1 ] && [ -f "$scan" ] && [ "$($BB wc -c < "$scan")" -le 1048576 ]; then
    $BB base64 "$scan" | $BB awk '{printf "WB_TRACE___TOKEN__ %s\n",$0}'
  fi
  [ "$scan_owned" != 1 ] || $BB rm -f "$scan"
  [ "$start" = 0 ] || now || elapsed=$failure_elapsed
  emit "FAIL $failure_elapsed $stage cutoff=$failure_cutoff diagnostic_ms=$elapsed"
  exit 0
}
identity() {
  own=$($BB timeout 1 /usr/bin/dbus-send --session --print-reply --reply-timeout=750 --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner string:com.lge.hkmc.avn.appfunc.AppStandbyClock 2>/dev/null | $BB head -c 1025) || return 1
  [ "${#own}" -le 1024 ] || return 1
  owner_now=$(printf '%s\n' "$own" | $BB awk 'NR==1 {if($0 !~ /^method return /) exit 1;next} NR==2 {if($0 !~ /^   string ":[0-9]+[.][0-9]+"$/) exit 1;gsub(/^   string "|"$/,"");v=$0;next} {exit 1} END {if(NR!=2 || v=="") exit 1;print v}') || return 1
  pid_reply=$($BB timeout 1 /usr/bin/dbus-send --session --print-reply --reply-timeout=750 --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetConnectionUnixProcessID "string:$owner_now" 2>/dev/null | $BB head -c 1025) || return 1
  [ "${#pid_reply}" -le 1024 ] || return 1
  pid_now=$(printf '%s\n' "$pid_reply" | $BB awk 'NR==1 {if($0 !~ /^method return /) exit 1;next} NR==2 {if($0 !~ /^   uint32 [1-9][0-9]*$/) exit 1;v=$2;next} {exit 1} END {if(NR!=2 || v=="" || v+0>2147483647) exit 1;print v}') || return 1
  kill -0 "$pid_now" 2>/dev/null
}
process_start() {
  proc_pid=$1
  shift
  # comm may contain spaces and parentheses. Take the fields after the final
  # closing parenthesis and bind the one-line record to its requested PID.
  LC_ALL=C $BB "$@" awk -v pid="$proc_pid" '
    NR != 1 || index($0, pid " (") != 1 {invalid=1; exit 1}
    {
      if (!sub(/^.*\) /, "", $0) || $1 !~ /^[A-Za-z]$/ ||
          $20 !~ /^[1-9][0-9]*$/ || length($20)>20) {invalid=1; exit 1}
      ticks=$20
    }
    END {if (invalid || NR != 1) exit 1; print ticks}' "/proc/$proc_pid/stat"
}
reason_failure_snapshot() {
  # Each operation is independently bounded; a missing, rotated, oversized or
  # malformed append is unavailable evidence, never a reason to retry the call.
  reason_status=unavailable; reason_owner=unknown; reason_pid=0; reason_current_start=0
  if identity; then
    reason_owner=$owner_now; reason_pid=$pid_now
    reason_current_start=$(process_start "$pid_now" timeout 2 "$BB") || reason_current_start=0
  fi
  if [ "$scan_owned" = 1 ]; then
    # Recheck the original inode and prefix; never accept a truncated or replaced log.
    reason_stat=$($BB timeout 2 $BB stat -c '%d:%i:%s' "$log") || reason_stat=invalid
    reason_ident=${reason_stat%:*}; reason_size=${reason_stat##*:}
    case "$reason_size" in ''|*[!0-9]*) reason_size=0;; esac
    if [ "$reason_ident" = "$base_id" ] && [ "$reason_size" -ge "$base" ] && [ "$((reason_size-base))" -le 262144 ]; then
      reason_hash=empty
      if [ "$base_len" -gt 0 ]; then reason_hash=$(set +o pipefail; $BB timeout 2 $BB tail -c +"$base_at" "$log" | $BB head -c "$base_len" | $BB sha256sum) || reason_hash=invalid; fi
      if [ "$reason_hash" = "$base_hash" ] && (set +o pipefail; $BB timeout 2 $BB tail -c +"$((base+1))" "$log" | $BB head -c "$((reason_size-base))" > "$scan"); then
        reason_after=$($BB timeout 2 $BB stat -c '%d:%i:%s' "$log") || reason_after=invalid
        reason_lines=$($BB timeout 2 $BB awk 'length($0)>4096 {bad=1} END {if(NR>2048 || bad) exit 1; print NR}' "$scan") || reason_lines=invalid
        case "$reason_lines" in ''|*[!0-9]*) reason_lines=invalid;; esac
        reason_last=1
        if [ "$reason_size" -gt "$base" ]; then reason_last=$($BB timeout 2 $BB tail -c 1 "$scan" | $BB wc -l) || reason_last=invalid; fi
        if [ "${reason_after%:*}" = "$base_id" ] && [ "${reason_after##*:}" -ge "$reason_size" ] 2>/dev/null && [ "$reason_lines" != invalid ] && [ "$reason_last" -eq 1 ] 2>/dev/null && [ "$($BB timeout 2 $BB wc -c < "$scan")" -eq "$((reason_size-base))" ] 2>/dev/null; then reason_status=ok; fi
      fi
    fi
    # REASON11_COMPLETE_PREFIX_BEGIN
    reason_prefix=insufficient_evidence; reason_handler_entry=insufficient_evidence
    reason_draw_progress=insufficient_evidence; reason_prefix_records=0
    reason_prefix_size=invalid
    if [ "$reason_last" -eq 0 ] 2>/dev/null; then
      reason_prefix_size=$($BB timeout 2 $BB stat -c %s "$scan") || reason_prefix_size=invalid
    fi
    if [ "$reason_last" -eq 0 ] 2>/dev/null && [ "$reason_lines" != invalid ] &&
       [ "${reason_after%:*}" = "$base_id" ] &&
       [ "${reason_after##*:}" -ge "$reason_size" ] 2>/dev/null &&
       [ "$reason_prefix_size" -eq "$((reason_size-base))" ] 2>/dev/null; then
      # The final line is incomplete and is never inspected. Process only
      # earlier records and reuse the reason-11 DLT context policy.
      reason_prefix_result=$($BB timeout 2 $BB awk -v partial="$partial" '
        function context(s) {return s ~ /^[0-9][0-9][0-9][0-9]\/[^ ]+ [0-9:.]+ +[0-9]+ [0-9][0-9][0-9] MANG STAN STAN log info V 1 /}
        function observe(s) {
          if(index(s,"AppStandbyClockEngine::inter_show_window_fg") && index(s,"appid =")) {
            if(!context(s) || s !~ /appid =  *10  *reason =  *11  *plane =  *1  *avmode =  *-1  *command =  *0  *temporal =  *false/) return 2
            handler=1; return 1
          }
          if(index(s,"SCREEN_STATE: START DRAW") || index(s,"SCREEN_STATE: DRAW FINISHED")) {
            if(!context(s)) return 2
            draw=1; return 1
          }
          return 0
        }
        {
          if(seen && !(partial && seen==1)) {records++; sub(/\r$/, "", previous); if(observe(previous)==2) bad=1}
          previous=$0; seen++
        }
        END {
          if(bad) exit 1
          printf "%s %s %d\n",(handler ? "observed" : "not_observed_in_complete_prefix"),(draw ? "observed" : "not_observed_in_complete_prefix"),records
        }' "$scan") || reason_prefix_result=
      case "$reason_prefix_result" in
        "observed observed "*|"observed not_observed_in_complete_prefix "*|"not_observed_in_complete_prefix observed "*|"not_observed_in_complete_prefix not_observed_in_complete_prefix "*)
          set -- $reason_prefix_result
          case "$3" in ''|*[!0-9]*) ;; *) [ "$3" -le 2048 ] 2>/dev/null && {
            reason_prefix=complete_prefix; reason_handler_entry=$1; reason_draw_progress=$2; reason_prefix_records=$3
          };; esac
          ;;
      esac
    fi
    # REASON11_COMPLETE_PREFIX_END
    [ "$reason_status" = ok ] || : > "$scan"
  fi
  # REASON11_SNAPSHOT_CLASSIFY_BEGIN
  if [ "$reason_status" = unavailable ]; then
      if [ "$scan_owned" != 1 ]; then reason_status=scan_unowned
      elif [ "$reason_stat" = invalid ]; then reason_status=read_failed
      elif [ -z "${reason_hash+x}" ]; then reason_status=log_identity_or_bounds
      elif [ "$reason_hash" = invalid ]; then reason_status=read_failed
      elif [ "$reason_hash" != "$base_hash" ]; then reason_status=prefix_mismatch
      elif [ -z "${reason_lines+x}" ]; then reason_status=read_failed
      elif [ "$reason_after" = invalid ]; then reason_status=read_failed
      elif [ "${reason_after%:*}" != "$base_id" ] || ! [ "${reason_after##*:}" -ge "$reason_size" ] 2>/dev/null; then
        reason_status=log_identity_or_bounds
      elif [ "$reason_lines" = invalid ]; then reason_status=line_check_failed
      elif [ "$reason_last" = invalid ]; then reason_status=read_failed
      elif ! [ "$reason_last" -eq 1 ] 2>/dev/null; then reason_status=newline_check_failed
      else reason_status=byte_check_failed
      fi
  fi
  if [ "$reason_status" = newline_check_failed ]; then
    printf 'WB_REASON11_PREFIX___TOKEN__ evidence=%s handler_entry=%s draw_progress=%s records=%s\n' "$reason_prefix" "$reason_handler_entry" "$reason_draw_progress" "$reason_prefix_records"
  fi
  # REASON11_SNAPSHOT_CLASSIFY_END
  printf '\nWB_REASON11___TOKEN__ epoch=%s owner=%s pid=%s start=%s current_owner=%s current_pid=%s current_start=%s snapshot=%s\n' "$reason_epoch" "$owner" "$pid" "$reason_start" "$reason_owner" "$reason_pid" "$reason_current_start" "$reason_status"
}
boundary() {
  stat=$($BB stat -c '%d:%i:%s' "$log") || return 1
  ident=${stat%:*}; size=${stat##*:}
  case "$size" in ''|*[!0-9]*) return 1;; esac
  [ "$ident" = "$base_id" ] && [ "$size" -ge "$last_size" ] && [ "$((size-base))" -le 1048576 ] || return 1
  hash=empty
  if [ "$base_len" -gt 0 ]; then hash=$(set +o pipefail; $BB tail -c +"$base_at" "$log" | $BB head -c "$base_len" | $BB sha256sum) || return 1; fi
  [ "$hash" = "$base_hash" ] || return 1
  oldhash=empty
  if [ "$last_size" -gt "$base" ]; then oldhash=$(set +o pipefail; $BB tail -c +"$((base+1))" "$log" | $BB head -c "$((last_size-base))" | $BB sha256sum) || return 1; fi
  [ "$oldhash" = "$last_hash" ] || return 1
  [ -f "$scan" ] && [ ! -L "$scan" ] || return 1
  if [ "$size" -gt "$base" ]; then (set +o pipefail; $BB tail -c +"$((base+1))" "$log" | $BB head -c "$((size-base))" > "$scan") || return 1; else : > "$scan"; fi
  stats=$($BB stat -c '%d:%i:%s' "$log" "$scan") || return 1
  scan_split_pair "$stats" || return 1
  after=$scan_first
  [ "${scan_second##*:}" -eq "$((size-base))" ] || return 1
  [ "${after%:*}" = "$base_id" ] && [ "${after##*:}" -ge "$size" ] || return 1
  last_hash=empty
  if [ "$size" -gt "$base" ]; then
    last_hash=$($BB sha256sum "$scan") || return 1
    last_hash="${last_hash%% *}  -"
  fi
  last_size=$size
}
scan_split_pair() {
  # Both applets emit one record per fixed path, in argument order.
  scan_lf='
'
  case "$1" in
    *"$scan_lf"*) scan_first=${1%%"$scan_lf"*}; scan_second=${1#*"$scan_lf"};;
    *) return 1;;
  esac
  case "$scan_first:$scan_second" in :*|*:|*"$scan_lf"*) return 1;; esac
}
check_lines() {
  complete=0
  [ "$size" -eq "$base" ] || [ "$($BB tail -c 1 "$scan" | $BB wc -l)" -eq 0 ] || complete=1
  LC_ALL=C $BB awk -v re='__PATTERN__' -v complete="$complete" -v partial="$partial" -v base="$base" \
    -v capture_ms="${capture_ms:-0}" '
    function validmodel(s, n,i,k,j,count,key,v,w,h,x,y) {
      n=split(s,a," "); i=1
      if(a[i++]!="VM_OBSERVE_CONFIRM" || a[i++]!="geometry") return 0
      split("root bg txt buttonLocal buttonRoot",keys," ")
      for(k=1;k<=5;k++) {
        key=keys[k]; if(a[i++]!=key) return 0; count=(k==5 ? 2 : 4)
        for(j=1;j<=count;j++) {
          v=a[i++]; if(v !~ /^-?[0-9]+([.][0-9]+)?$/) return 0
          if(k==1 && ((j<=2 && v+0!=0) || (j==3 && v+0!=1920) || (j==4 && v+0!=720))) return 0
          if(k==4 && j==3) w=v+0; if(k==4 && j==4) h=v+0
          if(k==5 && j==1) x=v+0; if(k==5 && j==2) y=v+0
        }
      }
      split("enabled modelEnableBtn visible wide dimmed driving calling",keys," ")
      for(k=1;k<=7;k++) {
        if(a[i++]!=keys[k]) return 0; v=a[i++]
        if(k==2) {if(v!="0" && v!="1") return 0}
        else if(v!="true" && v!="false") return 0
      }
      return i==n+1 && w>0 && h>0 && x>=0 && y>=0 && x+w<=1920 && y+h<=720
    }
    function timeout_after_capture(s, fields, clock, h, m, sec, milli, micro) {
      # A component timeout is harmless only after a validated frame capture.
      # Require a complete, in-range DLT clock so malformed evidence fails closed.
      if(capture_ms<=0) return 0
      split(s,fields," "); clock=fields[2]
      if(length(clock)!=15 || substr(clock,3,1)!=":" || substr(clock,6,1)!=":" ||
         substr(clock,9,1)!="." || substr(clock,1,2)!~/^[0-9][0-9]$/ ||
         substr(clock,4,2)!~/^[0-9][0-9]$/ || substr(clock,7,2)!~/^[0-9][0-9]$/ ||
         substr(clock,10,6)!~/^[0-9][0-9][0-9][0-9][0-9][0-9]$/) return 0
      h=substr(clock,1,2)+0; m=substr(clock,4,2)+0; sec=substr(clock,7,2)+0
      milli=substr(clock,10,3)+0; micro=substr(clock,13,3)+0
      if(h>23 || m>59 || sec>59) return 0
      return ((h*3600+m*60+sec)*1000+milli)*1000+micro>capture_ms*1000
    }
    function eventmeta(s, startpos, idx, a) {split(s,a," "); offsets[idx]=base+startpos; stamps[idx]=a[2]}
    function check(s, startpos,p,a,ctx,isentry,isshow,isstart,isfinish,isreturn) {
      if(bad!="") return
      if(length(s)>4096) {bad="line_limit";return}
      ctx=(s ~ /^[0-9][0-9][0-9][0-9]\/[^ ]+ [0-9:.]+ +[0-9]+ [0-9][0-9][0-9] MANG STAN STAN log info V 1 /)
      p=index(s,"VM_OBSERVE_CONFIRM geometry")
      isentry=index(s,"AppStandbyClockEngine::inter_show_window_fg") && index(s,"appid =")
      isshow=index(s,"QMLController::showScreen(QString)")
      isstart=index(s,"SCREEN_STATE: START DRAW")
      isfinish=index(s,"SCREEN_STATE: DRAW FINISHED")
      isreturn=index(s,"AppStandbyClockEngine::inter_show_window_fg") && index(s,"return plane =")
      if(!ctx) {if(p || (isentry && index(s,"reason =  11"))) bad="wrong_context";return}
      # Preserve only an allowlisted marker class and its zero-based offset in
      # the bounded appended slice. Raw private log content stays out of the
      # structured diagnostic.
      timeout_pos=index(s,"onTimeout Handler")
      if(timeout_pos && !timeout_after_capture(s)) {bad=sprintf("native_timeout native_marker=timeout_handler marker_offset=%d",startpos+timeout_pos-1);return}
      if(timeout_pos) return
      timeout_pos=index(s,"AppStandbyClockEngine::onTimeoutHandler()")
      if(timeout_pos && !timeout_after_capture(s)) {bad=sprintf("native_timeout native_marker=clock_engine_timeout marker_offset=%d",startpos+timeout_pos-1);return}
      if(timeout_pos) return
      timeout_pos=index(s,"confirmSkPressed()")
      if(timeout_pos && !timeout_after_capture(s)) {bad=sprintf("native_timeout native_marker=confirm_sk_pressed marker_offset=%d",startpos+timeout_pos-1);return}
      if(timeout_pos) return
      if(index(s,"VM_OBSERVE_CONFIRM visibleChanged false")) {hidden++;return}
      if(phase>0 && index(s,"AppStandbyClockModel::setCurrentScreenID(int)") && s !~ / 0[]]$/) {bad="native_screen_changed";return}
      if(p && (s !~ re || !validmodel(substr(s,p,length(s)-p)))) {bad="model_malformed";return}
      if(isentry) {
        if(phase!=0 || s !~ /appid =  *10  *reason =  *11  *plane =  *1  *avmode =  *-1  *command =  *0  *temporal =  *false/) {bad="native_entry";return}
        phase=1;eventmeta(s,startpos,1);return
      }
      if(isshow && phase>0) {
        if(phase!=1 || !index(s,"/app/share/AppStandbyClock/qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml")) {bad="native_show";return}
        phase=2;eventmeta(s,startpos,2);return
      }
      if(isstart && phase>0) {if(phase!=2){bad="native_draw_start";return} phase=3;eventmeta(s,startpos,3);return}
      if(p && phase>0) {
        if(phase!=3) {bad="native_model_order";return}
        model=substr(s,p,length(s)-p)
        if(!index(model,"enabled true modelEnableBtn 1 visible true") || !index(model,"dimmed false driving false calling false")) {bad="model_restricted";return}
        phase=4;eventmeta(s,startpos,4);return
      }
      if(isfinish && phase>0) {if(phase!=4){bad="native_draw_end";return} phase=5;eventmeta(s,startpos,5);return}
      if(isreturn && phase>0) {if(phase!=5 || s !~ /return plane =  *1([^0-9]|$)/){bad="native_return";return} phase=6;eventmeta(s,startpos,6);return}
    }
    {if(NR>8192) {bad="line_limit";exit} startpos=n; n+=length($0)+1; sub(/\r$/, ""); if(NR>1 && !(partial && NR==2)) check(prev,prev_start); prev=$0;prev_start=startpos}
    END {if(complete && NR && !(partial && NR==1)) check(prev,prev_start); if(bad!="") print "FAIL " bad; else if(phase==6) printf "READY entry=%d show=%d draw_start=%d model=%d draw_end=%d native_return=%d timestamps=%s,%s,%s,%s,%s,%s|HIDDEN|%d|MODEL|%s\n",offsets[1],offsets[2],offsets[3],offsets[4],offsets[5],offsets[6],stamps[1],stamps[2],stamps[3],stamps[4],stamps[5],stamps[6],hidden,model; else print "PENDING"}' "$scan"
}
[ ! -e "$scan" ] && [ ! -L "$scan" ] && [ -f "$log" ] && [ ! -L "$log" ] || fail log_preflight
(umask 077; set -C; : > "$scan") 2>/dev/null || fail log_preflight
scan_owned=1
stat=$($BB stat -c '%d:%i:%s' "$log") || fail log_preflight
base_id=${stat%:*}; base=${stat##*:}; case "$base" in ''|*[!0-9]*) fail log_preflight;; esac
base_len=256; [ "$base" -ge 256 ] || base_len=$base; base_at=$((base-base_len+1)); base_hash=empty
if [ "$base_len" -gt 0 ]; then base_hash=$(set +o pipefail; $BB tail -c +"$base_at" "$log" | $BB head -c "$base_len" | $BB sha256sum) || fail log_preflight; fi
partial=0
if [ "$base" -gt 0 ]; then [ "$(set +o pipefail; $BB tail -c +"$base" "$log" | $BB head -c 1 | $BB wc -l)" -eq 1 ] || partial=1; fi
last_size=$base; last_hash=empty
identity || fail owner_preflight
owner=$owner_now; pid=$pid_now
emit "BEGIN owner=$owner pid=$pid"; begun=1
read -r start _ </proc/uptime || fail clock
case "$start" in ''|*[!0-9.]*) fail clock;; esac
reason_epoch=$($BB awk -v v="$start" 'BEGIN {printf "%.0f",v*1000}') || reason_epoch=0
reason_start=$(process_start "$pid" timeout 2 "$BB") || reason_start=0
emit "REASON11_SENT 0"
reason_call_sent_ms=$elapsed
if reply_capture=$(set -o pipefail; $BB timeout __DBUS_WRAPPER_TIMEOUT_SECONDS__ /usr/bin/dbus-send --session --print-reply --reply-timeout=__DBUS_REPLY_TIMEOUT_MS__ --dest=com.lge.hkmc.avn.appfunc.AppStandbyClock /com/lge/hkmc/avn/appfunc/standby com.lge.avn.appmanager.appbase.show_window_fg int32:10 int32:11 int32:1 int32:-1 int32:0 boolean:false 2>&1 | $BB head -c 1025; capture_rc=$?; printf '\001'; exit "$capture_rc"); then
  reason_call_rc=0
else
  reason_call_rc=$?
fi
reply=${reply_capture%?}
reason_reply_bytes=$((${#reply_capture}-1))
if now; then
  reason_call_duration_ms=$((elapsed-reason_call_sent_ms))
else
  elapsed=$reason_call_sent_ms
  reason_call_duration_ms=unavailable
fi
if [ "$reason_call_rc" = 124 ] || [ "$reason_call_rc" = 143 ]; then
  reason_call_class=wrapper_timeout
elif [ "$reason_reply_bytes" -eq 0 ]; then
  reason_call_class=empty_reply
elif (printf '%s\n' "$reply" | $BB grep -q 'org.freedesktop.DBus.Error.NoReply'); then
  reason_call_class=dbus_no_reply
elif (printf '%s\n' "$reply" | $BB grep -q 'org.freedesktop.DBus.Error.ServiceUnknown'); then
  reason_call_class=dbus_service_unknown
elif (printf '%s\n' "$reply" | $BB grep -q 'org.freedesktop.DBus.Error.AccessDenied'); then
  reason_call_class=dbus_access_denied
elif [ "$reason_call_rc" = 0 ] && case "$reply" in method\ return*) true;; *) false;; esac; then
  reason_call_class=reply
else
  reason_call_class=other_error
fi
reason_reply_clipped=false
[ "$reason_reply_bytes" -le 1024 ] || reason_reply_clipped=true
emit "REASON11_CALL $elapsed rc=$reason_call_rc class=$reason_call_class bytes=$reason_reply_bytes clipped=$reason_reply_clipped duration_ms=$reason_call_duration_ms"
case "$reason_call_class" in reply) :;; *) fail reason11;; esac
[ "$reason_reply_bytes" -le 1024 ] || fail reason11
ack=$(printf '%s' "$reply" | $BB awk -v owner="$owner" 'NR==1 {if($0 !~ /^method return sender=:[0-9]+[.][0-9]+ -> dest=:[0-9]+[.][0-9]+ reply_serial=[1-9][0-9]*$/ || index($0,"sender=" owner " ")==0) exit 1; for(i=1;i<=NF;i++) {if($i ~ /^reply_serial=/) serial=$i; if($i ~ /^dest=/) dest=$i} next} NR==2 {if($0 !~ /^[[:space:]]*int32 1[[:space:]]*$/) exit 1;next} {exit 1} END {if(NR!=2 || serial=="" || dest=="") exit 1; print "sender=" owner " " dest " " serial}') || fail reason11_ack
now && [ "$elapsed" -lt 10000 ] || fail deadline
emit "REASON11_ACK $elapsed $ack"
budget
boundary || fail log_changed
budget
emit "IVI_SENT $elapsed"
remaining=$(((10000-elapsed)/1000)); [ "$remaining" -ge 1 ] || fail ivi_budget
[ "$remaining" -le 3 ] || remaining=3
ivi=$($BB timeout "$remaining" /ivi-fg-standby1000 | $BB head -c 1025) || fail ivi
[ "$ivi" = IVI_FG_REQUEST_SENT ] || fail ivi_ack
now && [ "$elapsed" -lt 10000 ] || fail deadline
emit "IVI_ACK $elapsed status=0 ack=IVI_FG_REQUEST_SENT"
while :; do
  now && [ "$elapsed" -lt 10000 ] || fail model_deadline
  identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
  budget
  boundary || fail log_changed
  budget
  result=$(check_lines) || fail log_parse
  budget
  case "$result" in FAIL\ *) fail "${result#FAIL }";; READY\ *) native=${result#READY }; native=${native%%|HIDDEN|*}; model=${result#*|MODEL|}; break;; PENDING) :;; *) fail log_parse;; esac
  $BB sleep 0.2
done
now && [ "$elapsed" -lt 10000 ] || fail deadline
emit "NATIVE $elapsed $native"
emit "MODEL $elapsed $model"
budget
remaining=$(((10000-elapsed)/1000)); [ "$remaining" -ge 1 ] || fail capture_budget
emit "CAPTURE_START $elapsed"
cd /tmp || fail capture
$BB rm -f wayland-screenshot.png
$BB timeout "$remaining" /usr/libexec/weston-screenshooter </dev/null >/tmp/workbench-screenshot.log 2>&1 || fail capture
now && [ "$elapsed" -lt 10000 ] || fail capture_deadline
identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
budget
boundary || fail log_changed
budget
result=$(check_lines) || fail log_parse
budget
case "$result" in FAIL\ *) fail "${result#FAIL }";; esac
now && [ "$elapsed" -lt 10000 ] || fail capture_deadline
length=$($BB wc -c < wayland-screenshot.png | $BB awk '{print $1}'); [ "$length" -gt 0 ] && [ "$length" -le 4194304 ] || fail capture_size
budget
set -- $($BB sha256sum wayland-screenshot.png); digest=$1
budget
identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
budget
boundary || fail log_changed
budget
result=$(check_lines) || fail log_parse
budget
case "$result" in FAIL\ *) fail "${result#FAIL }";; esac
now && [ "$elapsed" -lt 10000 ] || fail capture_deadline
hidden=${result#*|HIDDEN|}; hidden=${hidden%%|MODEL|*}
case "$hidden" in ''|*[!0-9]*) fail log_parse;; esac
emit "VISIBILITY $elapsed button_hidden=$hidden"
emit "CAPTURE_DONE $elapsed size=$length sha256=$digest"
emit "OK $elapsed"
printf 'WB_FRAME___TOKEN__ META %s %s\n' "$length" "$digest"
$BB base64 wayland-screenshot.png | $BB awk '{printf "WB_FRAME___TOKEN__ CHUNK %d %s\n",NR,$0} END {printf "WB_FRAME___TOKEN__ END %d\n",NR}'
$BB rm -f "$scan"
)'''
    if ivi_probe:
        # Re-evaluate the same epoch slice at every existing boundary. Once the
        # selected typed model has been hidden, later visibility notifications
        # alone cannot establish a new ordered native acquisition.
        script = script.replace('scan_owned=0', 'scan_owned=0\nprobe_published=0', 1)
        script = script.replace('  stage=$1\n',
            '  stage=$1\n  if [ "$stage" = probe_state_changed ] && [ "$probe_published" = 1 ]; then stage=unqualified_state_changed; fi\n  if [ "$probe_published" = 1 ]; then $BB rm -f "$d/baseline.raw" "$d/baseline.meta.tmp" "$d/baseline.ack.tmp"; fi\n', 1)
        script = script.replace(
            'if(index(s,"VM_OBSERVE_CONFIRM visibleChanged false")) {hidden++;return}',
            '''if(index(s,"VM_OBSERVE_CONFIRM visibleChanged false")) {hidden++;if(phase>=4) bad="probe_state_changed";return}
      if(phase>=4 && (index(s,"VM_OBSERVE_CONFIRM enabledChanged false") || s ~ /drivingRestriction:[[:space:]]*true/)) {bad="probe_state_changed";return}''', 1)
        script = script.replace(
            'if(phase!=3) {bad="native_model_order";return}\n        model=substr(s,p,length(s)-p)',
            '''if(phase>=4) {
          latest=substr(s,p,length(s)-p)
          if(!index(latest,"enabled true modelEnableBtn 1 visible true") || !index(latest,"dimmed false driving false calling false")) bad="probe_state_changed"
          return
        }
        if(phase!=3) {bad="native_model_order";return}
        model=substr(s,p,length(s)-p)''', 1)
        arm = r'''
identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
proc_start=$(process_start "$pid") || fail probe_identity
epoch_ms=$($BB awk -v v="$start" 'BEGIN {printf "%.0f",v*1000}') || fail probe_clock
    deadline_ms=$((epoch_ms+__CAPTURE_DEADLINE_OFFSET__))
case "$epoch_ms:$deadline_ms" in *[!0-9:]*) fail probe_clock;; esac
d=/tmp/vm-ivi-frame-probe
[ -d "$d" ] && [ ! -L "$d" ] && [ "$($BB stat -c '%u:%a' "$d")" = 0:700 ] || fail probe_directory
for f in request request.tmp receipt receipt.tmp source.raw output.raw baseline.raw baseline.meta baseline.meta.tmp baseline.ack baseline.ack.tmp go go.tmp; do [ ! -e "$d/$f" ] && [ ! -L "$d/$f" ] || fail probe_existing; done
budget
# Derive arm and the emitted elapsed value from this same monotonic sample.
arm_ms=$($BB awk -v v="$current" 'BEGIN {printf "%.0f",v*1000}') || fail probe_clock
case "$arm_ms" in ''|*[!0-9]*) fail probe_clock;; esac
[ "$arm_ms" -ge "$epoch_ms" ] && [ "$arm_ms" -lt "$deadline_ms" ] || fail probe_deadline
umask 077
(set -C; printf '__TOKEN__ %s %s %s %s\n' "$pid" "$proc_start" "$epoch_ms" "$deadline_ms" > "$d/request.tmp") || fail probe_request
$BB mv "$d/request.tmp" "$d/request" || fail probe_request
probe_published=1
failure_cutoff=__CAPTURE_DEADLINE__
emit "PROBE_ARM $elapsed pid=$pid start=$proc_start epoch=$epoch_ms arm=$arm_ms deadline=$deadline_ms"
budget
while [ ! -e "$d/baseline.meta" ]; do
  [ ! -e "$d/receipt" ] || fail baseline_failed
  now && [ "$elapsed" -lt 10000 ] || fail baseline_deadline
  $BB sleep 0.1 || fail baseline_wait
done
[ -f "$d/baseline.meta" ] && [ ! -L "$d/baseline.meta" ] && [ "$($BB stat -c '%u:%a:%h' "$d/baseline.meta")" = 0:600:1 ] && [ "$($BB wc -c < "$d/baseline.meta")" -le 512 ] || fail baseline_meta
baseline_line=$($BB awk -v n='__TOKEN__' -v p="$pid" -v s="$proc_start" 'NR!=1 || NF!=9 || $1!=n || ("x" $2)!=("x" p) || ("x" $3)!=("x" s) || $4 !~ /^[1-9][0-9]*$/ || length($4)>20 || $5 !~ /^[1-9][0-9]*$/ || length($5)>7 || $5>8388608 || $5%4!=0 || $6 !~ /^(537004168|537036936)$/ || $7 !~ /^0x[0-9a-f]+$/ || $8 !~ /^0x[0-9a-f]+$/ || $9 !~ /^0x[0-9a-f]+$/ || length($7)>18 || length($8)>18 || length($9)>18 || $7=="0x0" || $8=="0x0" || $9=="0x0" {exit 1} END {if(NR!=1) exit 1} {print $4,$5,$6,$7,$8,$9}' "$d/baseline.meta") || fail baseline_meta
set -- $baseline_line; [ "$#" -eq 6 ] || fail baseline_meta
baseline_time=$1; baseline_size=$2; baseline_format=$3; baseline_buffer=$4; baseline_surface=$5; baseline_output=$6
[ "$baseline_time" -ge "$epoch_ms" ] && [ "$baseline_time" -lt "$deadline_ms" ] || fail baseline_deadline
[ -f "$d/baseline.raw" ] && [ ! -L "$d/baseline.raw" ] || fail baseline_data
baseline_stat=$($BB stat -c '%d:%i:%s:%u:%a:%h' "$d/baseline.raw") || fail baseline_data
case "$baseline_stat" in *:"$baseline_size":0:600:1) ;; *) fail baseline_data;; esac
set -- $($BB sha256sum "$d/baseline.raw"); baseline_sha=$1
case "$baseline_sha" in *[!0-9a-f]*|'') fail baseline_data;; esac
[ "${#baseline_sha}" -eq 64 ] && [ "$($BB stat -c '%d:%i:%s:%u:%a:%h' "$d/baseline.raw")" = "$baseline_stat" ] || fail baseline_data
$BB rm -f "$d/baseline.raw" || fail baseline_cleanup
[ ! -e "$d/baseline.raw" ] && [ ! -L "$d/baseline.raw" ] || fail baseline_cleanup
(set -C; printf '__TOKEN__ %s %s %s %s %s %s %s %s %s\n' "$pid" "$proc_start" "$baseline_time" "$baseline_size" "$baseline_format" "$baseline_buffer" "$baseline_surface" "$baseline_output" "$baseline_sha" > "$d/baseline.ack.tmp") || fail baseline_ack
$BB ln "$d/baseline.ack.tmp" "$d/baseline.ack" && $BB rm -f "$d/baseline.ack.tmp" || fail baseline_ack
set -- $($BB sha256sum "$d/baseline.ack"); ack_sha=$1
case "$ack_sha" in *[!0-9a-f]*|'') fail baseline_ack;; esac
[ "${#ack_sha}" -eq 64 ] || fail baseline_ack
now && [ "$elapsed" -lt 10000 ] || fail baseline_deadline
emit "BASELINE $elapsed time=$baseline_time size=$baseline_size format=$baseline_format buffer=$baseline_buffer surface=$baseline_surface output=$baseline_output sha256=$baseline_sha ack_sha=$ack_sha"
# REASON11_PHASE_SEND_FENCE_BEGIN
reason_send_fence=$(reason_phase_fence) || reason_send_fence=
# REASON11_PHASE_SEND_FENCE_END
now && [ "$elapsed" -lt 10000 ] || fail probe_deadline
reason_ms=$($BB awk -v v="$current" 'BEGIN {printf "%.0f",v*1000}') || fail probe_clock
[ "$baseline_time" -le "$reason_ms" ] || fail baseline_deadline
'''
        observe = r'''
# The compositor cannot compare/capture until the original service has replied
# and its unique D-Bus owner, PID and process start time have been revalidated.
identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
current_start=$(process_start "$pid") || fail probe_identity
[ "$current_start" = "$proc_start" ] || fail probe_identity
now && [ "$elapsed" -lt 10000 ] || fail probe_deadline
observe_ms=$($BB awk -v v="$current" 'BEGIN {printf "%.0f",v*1000}') || fail probe_clock
[ "$observe_ms" -ge "$reason_ms" ] && [ "$observe_ms" -lt "$deadline_ms" ] || fail probe_deadline
emit "OBSERVE $elapsed monotonic=$observe_ms"
(set -C; printf '__TOKEN__ %s %s %s\n' "$baseline_sha" "$ack_sha" "$observe_ms" > "$d/go.tmp") || fail probe_request
$BB ln "$d/go.tmp" "$d/go" && $BB rm -f "$d/go.tmp" || fail probe_request
budget
'''
        finish = r'''
now && [ "$elapsed" -lt __CAPTURE_DEADLINE__ ] || fail probe_deadline
emit "VERIFY_START $elapsed capture_deadline=__CAPTURE_DEADLINE__ verification_deadline=__VERIFICATION_DEADLINE__ timing_schema=1"
failure_cutoff=__VERIFICATION_DEADLINE__
# Only private verification scratch is written in this phase; no further
# foreground, IVI, probe or input requests are issued.
while [ ! -e "$d/receipt" ]; do
  now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
  $BB sleep 0.1 || fail probe_wait
done
[ -f "$d/receipt" ] && [ ! -L "$d/receipt" ] && [ "$($BB stat -c '%u:%a' "$d/receipt")" = 0:600 ] && [ "$($BB wc -c < "$d/receipt")" -le 512 ] || fail probe_receipt
set -- $($BB sha256sum "$d/receipt"); probe_hash=$1
case "$probe_hash" in *[!0-9a-f]*|'') fail probe_receipt;; esac
[ "${#probe_hash}" -eq 64 ] || fail probe_receipt
probe_line=$($BB awk -v n='__TOKEN__' -v p="$pid" -v s="$proc_start" -v bt="$baseline_time" -v bs="$baseline_size" -v bf="$baseline_format" -v bb="$baseline_buffer" -v su="$baseline_surface" -v ou="$baseline_output" -v bh="$baseline_sha" -v ah="$ack_sha" -v om="$observe_ms" '
  NR!=1 || NF!=31 || $1!=n || $2!="OK" || $3!=p || $4!=s {exit 1}
  $5 !~ /^1$/ || $6 !~ /^[1-9][0-9]*$/ || length($6)>20 || $7 !~ /^0x[0-9a-f]+$/ || $8 !~ /^0x[0-9a-f]+$/ || length($7)>18 || length($8)>18 {exit 1}
  {for(i=9;i<=16;i++) if($i !~ /^[1-9][0-9]*$/ || length($i)>10) exit 1}
  $9 !~ /^[1-9][0-9]*$/ || $10 !~ /^[1-9][0-9]*$/ || $9>4096 || $10>2160 || ($11!=537004168 && $11!=537036936) || $12!=$9*$10*4 || $12>8388608 {exit 1}
  $13!=1920 || $14!=720 || ($15!=537004168 && $15!=537036936) || $16!=5529600 {exit 1}
  $7!=su || $8!=ou || $11!=bf || $12!=bs || $23!=bt || $24!=bs || $25!=bf || $26!=bb || $27 !~ /^0x[0-9a-f]+$/ || $28 !~ /^[1-9][0-9]*$/ || $28>100 || $29!=bh || $30!=ah || ("x" $31)!=("x" om) {exit 1}
  {for(i=17;i<=22;i++) if($i !~ /^-?(0|[1-9][0-9]*)$/ || $i < -2147483648 || $i > 2147483647) exit 1; print $5, $6, $15, $27, $28}
  END {if(NR!=1) exit 1}' "$d/receipt") || fail probe_receipt
set -- $probe_line; [ "$#" -eq 5 ] || fail probe_receipt
probe_sequence=$1; probe_capture=$2; output_format=$3; selected_buffer=$4; observations=$5
[ "$($BB sha256sum "$d/receipt" | $BB cut -d ' ' -f1)" = "$probe_hash" ] || fail probe_receipt
[ "$probe_capture" -ge "$observe_ms" ] && [ "$probe_capture" -lt "$deadline_ms" ] || fail probe_deadline
capture_ms=$probe_capture
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "RECEIPT_BOUND $elapsed capture=$probe_capture"
# Schema-1 records mark completed checks using the same epoch and cutoff.
# The gap before FAIL identifies an interrupted phase without claiming its
# completion; these clock samples never extend the validity window.
# Bind the producer immediately after receipt validation and again after the
# output hash; a transient owner change must not be masked by the hash delay.
verify_phase=identity; verify_mark begin
identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
verify_mark identity_check
current_start=$(process_start "$pid") || fail probe_identity
[ "$current_start" = "$proc_start" ] || fail probe_identity
verify_mark process_start
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail probe_identity_deadline
emit "VERIFY_IDENTITY $elapsed"
verify_phase=output; verify_mark begin
[ -f "$d/output.raw" ] && [ ! -L "$d/output.raw" ] || fail probe_output
output_stat=$($BB stat -c '%d:%i:%s:%u:%a:%h' "$d/output.raw") || fail probe_output
case "$output_stat" in *:5529600:0:600:1) ;; *) fail probe_output;; esac
verify_mark initial_stat
set -- $($BB sha256sum "$d/output.raw"); output_hash=$1
case "$output_hash" in *[!0-9a-f]*|'') fail probe_output;; esac
verify_mark digest
[ "${#output_hash}" -eq 64 ] && [ "$($BB stat -c '%d:%i:%s:%u:%a:%h' "$d/output.raw")" = "$output_stat" ] || fail probe_output
verify_mark final_stat
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail probe_output_deadline
emit "VERIFY_OUTPUT $elapsed"
verify_phase=identity_recheck; verify_mark begin
identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
verify_mark identity_check
current_start=$(process_start "$pid") || fail probe_identity
[ "$current_start" = "$proc_start" ] || fail probe_identity
verify_mark process_start
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "VERIFY_IDENTITY_RECHECK $elapsed"
verify_phase=scan_1; verify_mark begin
boundary || fail log_changed
result=$(check_lines) || fail log_parse
case "$result" in FAIL\ *) fail "${result#FAIL }";; READY\ *) :;; *) fail log_parse;; esac
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "VERIFY_LOG_SCAN_1 $elapsed"
# The post-capture scan may be slow under TCG. Revalidate the same owner,
# PID and start time after the scan, before publishing its historical frame.
verify_phase=identity_final; verify_mark begin
identity && [ "$owner_now" = "$owner" ] && [ "$pid_now" = "$pid" ] || fail owner_changed
verify_mark identity_check
current_start=$(process_start "$pid") || fail probe_identity
[ "$current_start" = "$proc_start" ] || fail probe_identity
verify_mark process_start
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "VERIFY_IDENTITY_FINAL $elapsed"
# The additional owner check takes time; refresh the bounded append-only log
# afterward so a hide or restriction during that check is not overlooked.
verify_phase=scan_2; verify_mark begin
boundary || fail log_changed
result=$(check_lines) || fail log_parse
case "$result" in FAIL\ *) fail "${result#FAIL }";; READY\ *) :;; *) fail log_parse;; esac
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "VERIFY_LOG_SCAN_2 $elapsed"
hidden=${result#*|HIDDEN|}; hidden=${hidden%%|MODEL|*}
case "$hidden" in ''|*[!0-9]*) fail log_parse;; esac
emit "VISIBILITY $elapsed button_hidden=$hidden"
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "PROBE_CAPTURE $elapsed capture=$probe_capture sequence=$probe_sequence width=1920 height=720 format=$output_format size=5529600 sha256=$output_hash receipt_sha=$probe_hash baseline_time=$baseline_time baseline_size=$baseline_size baseline_format=$baseline_format baseline_buffer=$baseline_buffer selected_buffer=$selected_buffer observations=$observations baseline_sha=$baseline_sha ack_sha=$ack_sha observation_start=$observe_ms mode=source-content-change"
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "VERIFY_DONE $elapsed capture_deadline=__CAPTURE_DEADLINE__ verification_deadline=__VERIFICATION_DEADLINE__ timing_schema=1"
now && [ "$elapsed" -lt __VERIFICATION_DEADLINE__ ] || fail verification_deadline
emit "OK $elapsed"
verify_emit
$BB rm -f "$scan"
)'''
        # Establish the baseline before the one foreground request; the normal
        # screenshot transaction is unchanged.
        script = script.replace('emit "REASON11_SENT 0"', arm + '\nemit "REASON11_SENT $elapsed monotonic=$reason_ms"', 1)
        script = script.replace('emit "REASON11_ACK $elapsed $ack"', 'emit "REASON11_ACK $elapsed $ack"\n' + observe, 1)
        # The opt-in probe owns one post-arm capture budget. Pre-arm setup
        # retains its ten-second setup limit; verification separately gets its
        # own read-only completion window.
        script = script.replace('now && [ "$elapsed" -lt 10000 ] || fail ',
                                'now && [ "$elapsed" -lt "$failure_cutoff" ] || fail ')
        # The compositor was already asked to capture. The screenshot command's
        # whole-second timeout does not apply to verification of that receipt.
        screenshot_budget = 'remaining=$(((10000-elapsed)/1000)); [ "$remaining" -ge 1 ] || fail capture_budget'
        script = script[:script.index(screenshot_budget)] + finish
        script = script.replace('remaining=$(((10000-elapsed)/1000))',
                                'remaining=$(((failure_cutoff-elapsed)/1000))', 1)
    if ivi_probe:
        script = _vm_guest_instrument_reason11_phase(script)
    script = _vm_guest_cache_scanner(script)
    if ivi_probe:
        script = _vm_guest_instrument_verification(script)
    return (script.replace("failure_cutoff=10000", f"failure_cutoff={VM_IVI_SETUP_DEADLINE_MS}")
            .replace('[ "$elapsed" -lt 10000 ]', f'[ "$elapsed" -lt {VM_IVI_SETUP_DEADLINE_MS} ]')
            .replace("__CAPTURE_DEADLINE_OFFSET__", str(VM_IVI_CAPTURE_DEADLINE_MS - 1))
            .replace("__CAPTURE_DEADLINE__", str(VM_IVI_CAPTURE_DEADLINE_MS))
            .replace("__VERIFICATION_DEADLINE__", str(VM_IVI_VERIFICATION_DEADLINE_MS))
            .replace("__DBUS_WRAPPER_TIMEOUT_SECONDS__", str(VM_DBUS_WRAPPER_TIMEOUT_SECONDS))
            .replace("__DBUS_REPLY_TIMEOUT_MS__", str(VM_DBUS_REPLY_TIMEOUT_MS))
            .replace("__TOKEN__", token).replace("__PATTERN__", _DLT_CONFIRM_ENVELOPE))


def vm_guest_parse_debugging_mode(data: bytes) -> int:
    """Parse exactly one byte from a bounded dbus-send method return."""
    if not isinstance(data, bytes) or len(data) > 4096:
        raise ValueError("invalid or oversized D-Bus reply")
    raw = data.replace(b"\r\n", b"\n")
    match = re.fullmatch(_DBUS_HEADER + rb"[ \t]*array of bytes \[[ \t]*\n[ \t]*([0-9a-fA-F]{2})[ \t]*\n[ \t]*\][ \t]*\n?", raw)
    if match:
        return int(match.group(1), 16)
    match = re.fullmatch(_DBUS_HEADER + rb'[ \t]*array of bytes "([\x20-\x7e])"[ \t]*\n?', raw)
    if match:
        return match.group(1)[0]
    if re.fullmatch(_DBUS_HEADER + rb'[ \t]*array of bytes "" \+ \\0[ \t]*\n?', raw):
        return 0
    raise ValueError("D-Bus reply does not contain exactly one byte")


def vm_guest_parse_startup_receipt(data: bytes) -> dict:
    """Validate one fixed simulator-produced first-request receipt."""
    if not isinstance(data, bytes) or len(data) > 512:
        raise ValueError("invalid startup receipt size")
    match = re.fullmatch(rb"WB_IHU_STARTUP 1 sender=(:[0-9]+[.][0-9]+) owner=(:[0-9]+[.][0-9]+) "
                         rb"request=([1-9][0-9]{0,9}) reply=([1-9][0-9]{0,9}) "
                         rb"reply_serial=([1-9][0-9]{0,9}) len=32 byte0=(00|08) tail_zero=31\n", data)
    if not match:
        raise ValueError("malformed or duplicate startup receipt")
    sender, owner, request, reply, correlation, byte0 = match.groups()
    if sender == owner or request != correlation or any(int(v) > 0xffffffff for v in (request, reply, correlation)):
        raise ValueError("startup receipt identity or correlation mismatch")
    return {"sender": sender.decode(), "owner": owner.decode(), "request_serial": int(request),
            "reply_serial": int(reply), "correlation_serial": int(correlation),
            "length": 32, "byte0": int(byte0, 16), "tail_zero": 31}


def vm_guest_decode_capture(data: bytes, token: str) -> bytes:
    """Validate one uniquely framed screenshot, ignoring unrelated serial lines.

    Each marked line is authoritative: malformed, duplicated, out-of-order or
    missing records fail closed. A validated checksum binds the complete bytes.
    """
    if not isinstance(token, str) or not _CAPTURE_TOKEN.fullmatch(token):
        raise ValueError("invalid capture token")
    if not isinstance(data, bytes) or len(data) > _MAX_REPLY:
        raise ValueError("capture transcript exceeds limit")
    prefix = ("WB_FRAME_" + token + " ").encode("ascii")
    declared_length = None
    digest = None
    chunks = []
    encoded_size = 0
    finished = False
    # The guest kernel interleaves these observed console warnings within writes.
    # They contain characters excluded from our framed protocol. Removal is
    # safe only because every reconstructed screenshot still passes ordered
    # chunk validation, declared byte length and SHA-256 below.
    normalized = _CAPTURE_HRTIMER_WARNING.sub(b"", _SERIAL_IRQ_WARNING.sub(b"", data))
    for line in normalized.splitlines():
        if not line.startswith(prefix):
            continue
        record = line[len(prefix):]
        if finished:
            raise ValueError("capture contains records after end")
        if record.startswith(b"META "):
            match = re.fullmatch(rb"META ([1-9][0-9]{0,7}) ([0-9a-f]{64})", record)
            if not match or declared_length is not None or chunks:
                raise ValueError("malformed or duplicate capture metadata")
            declared_length = int(match.group(1))
            if declared_length > _MAX_CAPTURE:
                raise ValueError("declared capture size exceeds limit")
            digest = match.group(2).decode("ascii")
        elif record.startswith(b"CHUNK "):
            match = re.fullmatch(rb"CHUNK ([1-9][0-9]{0,6}) ([A-Za-z0-9+/=]{1,76})", record)
            if not match or declared_length is None or int(match.group(1)) != len(chunks) + 1:
                raise ValueError("malformed or out-of-order capture chunk")
            chunk = match.group(2)
            encoded_size += len(chunk)
            if encoded_size > _MAX_ENCODED:
                raise ValueError("encoded capture exceeds limit")
            chunks.append(chunk)
        elif record.startswith(b"END "):
            match = re.fullmatch(rb"END ([1-9][0-9]{0,6})", record)
            if not match or declared_length is None or int(match.group(1)) != len(chunks):
                raise ValueError("capture end or chunk count mismatch")
            finished = True
        else:
            raise ValueError("unknown capture record")
    if not finished or not chunks:
        raise ValueError("incomplete screenshot transfer")
    try:
        raw = base64.b64decode(b"".join(chunks), validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("malformed screenshot encoding") from exc
    if len(raw) != declared_length or hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("screenshot length or checksum mismatch")
    return raw


class GuestShell:
    """Read one owned QEMU's serial output and serialize shell transactions."""

    def __init__(self, process, log_path: Path, event: Callable):
        if process.stdin is None or process.stdout is None:
            raise ValueError("owned QEMU needs piped stdin and stdout")
        self._process, self._event = process, event
        self._condition, self._lock = threading.Condition(), threading.RLock()
        self._buffer = bytearray()
        self._closed = False
        self._quarantined = False
        log_path = Path(log_path)
        dir_fd = os.open(log_path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            parent = os.fstat(dir_fd)
            path_parent = os.lstat(log_path.parent)
            if (not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.geteuid() or
                    stat.S_IMODE(parent.st_mode) != 0o700 or
                    (parent.st_dev, parent.st_ino) != (path_parent.st_dev, path_parent.st_ino)):
                raise PermissionError("serial log directory is not private")
            fd = os.open(log_path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=dir_fd)
            try:
                os.fchmod(fd, 0o600)
                info = os.fstat(fd)
                if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or
                        stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1):
                    raise PermissionError("serial log is not private")
                self._log = os.fdopen(fd, "wb")
            except BaseException:
                os.close(fd)
                raise
        finally:
            os.close(dir_fd)
        self._reader = threading.Thread(target=self._drain, name="workbench-serial", daemon=True)
        self._reader.start()

    def _drain(self):
        try:
            while True:
                chunk = self._process.stdout.read1(65536)
                if not chunk:
                    break
                self._log.write(chunk)
                self._log.flush()
                with self._condition:
                    self._buffer.extend(chunk)
                    if len(self._buffer) > _MAX_REPLY:
                        del self._buffer[:-_MAX_REPLY]
                    self._condition.notify_all()
        finally:
            with self._condition:
                self._closed = True
                self._condition.notify_all()
            self._log.close()

    def wait_ready(self, timeout: float = 180.0) -> None:
        """Wait for the fixed research init's userspace-ready marker."""
        deadline = time.monotonic() + timeout
        with self._condition:
            while b"IONIQ_VENDOR_USERSPACE_READY" not in self._buffer:
                if self._closed:
                    raise EOFError("guest exited before userspace became ready")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("guest userspace readiness timed out")
                self._condition.wait(remaining)
        # Prevent typed command echo from being confused with response markers.
        self._process.stdin.write(b"stty -echo 2>/dev/null\n")
        self._process.stdin.flush()

    def _run(self, command: str, timeout: float = 15.0, *, timing=None,
             lock_timeout=None, quarantine_timeout=False, total_deadline=None) -> bytes:
        """Execute an internally constructed fixed command, not caller text."""
        if not 0 < timeout <= 360:
            raise ValueError("invalid guest transaction timeout")
        token = uuid.uuid4().hex
        start, end = f"WB_BEGIN_{token}", f"WB_END_{token}"
        script = f"printf '\\n{start}\\n'; {command}; wb_rc=$?; printf '\\n{end}:%s\\n' \"$wb_rc\"\n"
        waiting = time.monotonic()
        acquired = self._lock.acquire() if lock_timeout is None else self._lock.acquire(timeout=max(0, lock_timeout))
        if timing is not None:
            timing["lock_wait_s"] = time.monotonic() - waiting
        if not acquired:
            raise TimeoutError("guest serial lock timed out")
        started = time.monotonic()
        try:
            if self._quarantined:
                raise RuntimeError("guest serial channel quarantined after timeout")
            if total_deadline is not None:
                timeout = min(timeout, total_deadline - time.monotonic())
                if timeout <= 0:
                    raise TimeoutError("total diagnostic deadline")
            with self._condition:
                self._buffer.clear()
            self._process.stdin.write(script.encode("ascii"))
            self._process.stdin.flush()
            deadline = time.monotonic() + timeout
            marker = re.compile(rb"(?:\r?\n)" + end.encode() + rb":([0-9]+)\r?\n")
            begin = ("\n" + start + "\n").encode()
            with self._condition:
                while True:
                    raw = bytes(self._buffer).replace(b"\r\n", b"\n")
                    match = marker.search(raw)
                    pos = raw.find(begin)
                    if match and pos >= 0:
                        if int(match.group(1)) != 0:
                            raise RuntimeError("guest operation failed with status " + match.group(1).decode())
                        return raw[pos + len(begin):match.start()]
                    if self._closed:
                        raise EOFError("guest serial channel closed")
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        if quarantine_timeout:
                            self._quarantined = True
                        raise TimeoutError("guest serial transaction timed out")
                    self._condition.wait(remaining)
        finally:
            if timing is not None:
                timing["execution_s"] = time.monotonic() - started
            self._lock.release()

    def launch(self, *, frame_probe: bool = False) -> None:
        """Start the prepared VM-only HMI recipe in the guest background."""
        prefix = "VM_IVI_FRAME_PROBE=1 " if frame_probe else ""
        self._run("(test ! -e /tmp/workbench-launch.status || exit 1; "
                  f"test ! -e {_STANDBY_FAILURE_PATH} && test ! -L {_STANDBY_FAILURE_PATH} || exit 1; "
                  "(" + prefix + "/bin/busybox sh -x /launch-vm-workbench.sh </dev/null >/tmp/workbench-launch.log 2>&1; "
                  "wb_rc=$?; printf '%s\\n' \"$wb_rc\" >/tmp/workbench-launch.status.tmp && "
                  "/bin/busybox mv /tmp/workbench-launch.status.tmp /tmp/workbench-launch.status) &)")

    def observe_ivi_frame(self) -> tuple:
        """Obtain one private raw pixel diagnostic without sending input."""
        token = uuid.uuid4().hex
        raw = self._run(vm_guest_ivi_frame_command(token), timeout=120, quarantine_timeout=True)
        return vm_guest_parse_ivi_frame(raw, token)

    def wait_standby_prerequisites(self) -> None:
        """Wait for the fixed service, Wayland and helper prerequisite marker."""
        token = uuid.uuid4().hex
        raw = self._run(vm_guest_standby_readiness_command(token), timeout=320, quarantine_timeout=True)
        vm_guest_parse_standby_readiness(raw, token)

    def read_startup_receipt(self) -> dict:
        """Read the fixed bounded receipt; never issue a simulator method."""
        raw = self._run("(f=/tmp/eng-data-sim-startup; n=0; while test ! -e \"$f\" && test \"$n\" -lt 30; do "
                        "n=$((n+1)); /bin/busybox sleep 1; done; "
                        "test -f \"$f\" && test ! -L \"$f\" && "
                        "test \"$(/bin/busybox stat -c %a \"$f\")\" = 600 && "
                        "test \"$(/bin/busybox wc -c < \"$f\")\" -le 512 && /bin/busybox cat \"$f\")", timeout=40, quarantine_timeout=True)
        return vm_guest_parse_startup_receipt(raw)

    def foreground_and_capture(self) -> tuple:
        """Obtain a fresh model record and frame in one bounded transaction."""
        token = uuid.uuid4().hex
        started = time.monotonic()
        framed = self._run(vm_guest_acquisition_command(token), timeout=120, quarantine_timeout=True)
        try:
            model, frame, records = vm_guest_parse_acquisition(framed, token)
        except GuestAcquisitionError as exc:
            if exc.stage == "reason11":
                exc.diagnostic = _vm_guest_reason11_failure_diagnostic(exc)
            self._event("foreground", "acquisition_failed", {"stage": exc.stage, "records": exc.records}, "display")
            raise
        except ValueError as exc:
            prefix = ("WB_ACQ_" + token + " ").encode("ascii")
            candidates = [line[len(prefix):].decode("ascii", errors="replace")
                          for line in framed.splitlines() if line.startswith(prefix) and len(line) <= 4096][:10]
            self._event("foreground", "acquisition_invalid", {"reason": str(exc),
                        "unvalidated_records": candidates}, "display")
            raise
        self._event("foreground", "captured", {"records": records, "host_elapsed_s": time.monotonic() - started,
                    "surface_visibility": "requires frame inspection"}, "display")
        return model, frame

    def foreground_and_probe(self) -> tuple:
        """Correlate one native acquisition and a same-window private IVI snapshot.

        The results remain observations: neither a semantic log nor a pixel
        buffer establishes that Confirm appeared on the composed display.
        """
        token = uuid.uuid4().hex
        try:
            framed = self._run(vm_guest_acquisition_command(token, ivi_probe=True),
                               timeout=VM_IVI_TRANSFER_TIMEOUT_SECONDS, quarantine_timeout=True)
        except (OSError, RuntimeError, EOFError, TimeoutError) as exc:
            exc.diagnostic = {"qualification": "UNQUALIFIED", "failure": "acquisition_transport",
                              "probe_status": "unknown", "inventory": {}, "receipt": None}
            raise
        try:
            model, frame, records = vm_guest_parse_acquisition(framed, token, ivi_probe=True)
        except GuestAcquisitionError as exc:
            exc.diagnostic = {"qualification": "UNQUALIFIED", "failure": exc.stage,
                              "probe_status": "unqualified",
                              "records": exc.records, "inventory": {}, "receipt": None}
            if exc.stage == "reason11":
                exc.diagnostic["reason11"] = _vm_guest_reason11_failure_diagnostic(exc)
            arm_row = next((r for r in exc.records if r["stage"] == "PROBE_ARM"), None)
            if arm_row:
                arm = dict(item.split("=", 1) for item in arm_row["detail"].split())
                try:
                    data = self._run(vm_guest_probe_failure_command(token, int(arm["pid"]), int(arm["start"]), int(arm["epoch"]), int(arm["deadline"])), timeout=15, quarantine_timeout=True)
                    exc.diagnostic.update(vm_guest_parse_probe_failure(data, token, int(arm["pid"]), int(arm["start"]), int(arm["arm"]), int(arm["deadline"])))
                except (OSError, ValueError, RuntimeError, EOFError, TimeoutError):
                    exc.diagnostic["inventory_status"] = "unavailable_or_invalid"
            raise
        except ValueError as exc:
            # A malformed transcript cannot safely bind a guest receipt to the
            # acquisition; preserve the failure without trusting its fields.
            exc.diagnostic = {"qualification": "UNQUALIFIED", "failure": "invalid_transcript",
                              "probe_status": "unknown", "inventory": {}, "receipt": None}
            raise
        begin = records[0]
        arm = dict(item.split("=", 1) for item in next(r for r in records if r["stage"] == "PROBE_ARM")["detail"].split())
        captured = dict(item.split("=", 1) for item in next(r for r in records if r["stage"] == "PROBE_CAPTURE")["detail"].split())
        baseline = dict(item.split("=", 1) for item in next(r for r in records if r["stage"] == "BASELINE")["detail"].split())
        raw = self._run(vm_guest_ivi_frame_export_command(
            token, begin["owner"], int(arm["pid"]), int(arm["start"]), captured["receipt_sha"],
            compressed=VM_IVI_TRANSFER_COMPRESSED,
        ), timeout=VM_IVI_TRANSFER_TIMEOUT_SECONDS, quarantine_timeout=True)
        receipt, source, output = vm_guest_parse_ivi_frame(
            raw, token, compressed=VM_IVI_TRANSFER_COMPRESSED)
        if (receipt["pid"] != int(arm["pid"]) or receipt["starttime"] != int(arm["start"]) or
                receipt["monotonic_ms"] != int(captured["capture"]) or receipt["sequence"] != int(captured["sequence"]) or
                receipt["output"]["width"] != int(captured["width"]) or receipt["output"]["height"] != int(captured["height"]) or
                receipt["output"]["format"] != int(captured["format"]) or len(output) != int(captured["size"]) or
                hashlib.sha256(output).hexdigest() != captured["sha256"] or receipt["output"]["sha256"] != captured["sha256"] or
                receipt.get("surface_identity") != baseline["surface"] or receipt.get("output_identity") != baseline["output"] or
                len(source) != int(baseline["size"]) or receipt["source"]["format"] != int(baseline["format"]) or
                hashlib.sha256(source).hexdigest() == baseline["sha256"] or receipt.get("baseline") != {
                    "time": int(baseline["time"]), "size": int(baseline["size"]), "format": int(baseline["format"]),
                    "buffer": baseline["buffer"], "selected_buffer": captured["selected_buffer"],
                    "observations": int(captured["observations"]), "sha256": baseline["sha256"], "ack_sha": baseline["ack_sha"],
                    "observation_start": int(captured["observation_start"])}):
            raise ValueError("IVI exported receipt differs from acquisition")
        frame = vm_guest_probe_output_png(output, receipt["output"]["width"], receipt["output"]["height"], receipt["output"]["format"])
        receipt["acquisition"] = {"owner": begin["owner"], "epoch_ms": int(arm["epoch"]),
                                  "arm_ms": int(arm["arm"]), "deadline_ms": int(arm["deadline"]),
                                  "receipt_sha256": captured["receipt_sha"],
                                  "capture_deadline_elapsed_ms": VM_IVI_CAPTURE_DEADLINE_MS,
                                  "capture_monotonic_ms": int(captured["capture"]),
                                  "verification_deadline_elapsed_ms": VM_IVI_VERIFICATION_DEADLINE_MS,
                                  "verification_completed_elapsed_ms": next(r["elapsed_ms"] for r in records if r["stage"] == "VERIFY_DONE"),
                                  "transfer": "separate host operation after guest verification",
                                  "frame_source": "probe-output", "status": "pixels require independent inspection"}
        model = dict(model)
        model["acquisition_timing"] = {key: receipt["acquisition"][key] for key in (
            "capture_deadline_elapsed_ms", "capture_monotonic_ms", "verification_deadline_elapsed_ms",
            "verification_completed_elapsed_ms", "transfer")}
        return model, frame, receipt, source, output, records

    def diagnostics(self) -> bytes:
        """Read fixed early startup logs from this isolated guest."""
        return self._run("for f in /tmp/workbench-launch.log /tmp/launcher-chain/eng-data-sim.log /tmp/launcher-chain/weston.log /tmp/launcher-chain/launcher.log; do "
                         "printf '\\nWORKBENCH_LOG %s\\n' \"$f\"; test ! -f \"$f\" || /bin/busybox tail -n 60 \"$f\"; done", timeout=15)

    @contextmanager
    def compound_lease(self):
        """Acquire the serial bridge immediately for one bounded compound action."""
        if not self._lock.acquire(blocking=False):
            raise BlockingIOError("guest serial bridge busy")
        try:
            if self._closed or self._quarantined or self._process.poll() is not None:
                raise RuntimeError("guest serial bridge unavailable")
            yield
        finally:
            self._lock.release()

    def is_available(self) -> bool:
        """Report whether the owned serial bridge can still accept work."""
        return not self._closed and not self._quarantined and self._process.poll() is None

    def _publish(self, line: str, name: str, pattern: re.Pattern, *, deadline=None) -> None:
        if not isinstance(line, str) or not pattern.fullmatch(line):
            raise ValueError("invalid guest mailbox command")
        payload = base64.b64encode(line.encode("ascii")).decode("ascii")
        path = "/tmp/" + name
        self._run(f"test ! -e {path} && printf %s {payload} | /bin/busybox base64 -d > {path}.hosttmp && mv {path}.hosttmp {path}",
                  **({} if deadline is None else {"timeout": max(.001, min(1.0, deadline - time.monotonic())),
                      "lock_timeout": 0, "quarantine_timeout": True, "total_deadline": deadline}))

    def publish_input(self, line: str) -> None:
        """Atomically publish one validated Weston input command."""
        self._publish(line, "weston-vm-input", _INPUT)

    def publish_input_bounded(self, line: str, deadline: float, guest_expiry_ms: int) -> bool:
        """Publish one typed mailbox line only while the guest clock is in range."""
        match = re.fullmatch(r"seq [1-9][0-9]{0,9} cclick [0-9]+ [0-9]+ ([1-9][0-9]{0,19})\n", line) if isinstance(line, str) else None
        if not match or type(guest_expiry_ms) is not int or guest_expiry_ms <= 0 or int(match.group(1)) != guest_expiry_ms:
            raise ValueError("invalid bounded input")
        payload = base64.b64encode(line.encode("ascii")).decode("ascii")
        path = "/tmp/weston-vm-input"
        command = (f"test ! -e {path} && test ! -e {path}.hosttmp && "
                   f"printf %s {payload} | /bin/busybox base64 -d > {path}.hosttmp && "
                   "read -r wb_up _ </proc/uptime && "
                   "wb_ms=$(/bin/busybox awk -v v=\"$wb_up\" 'BEGIN {printf \"%.0f\",v*1000}') && "
                   f"if test \"$wb_ms\" -lt {guest_expiry_ms}; then mv {path}.hosttmp {path} && printf PUBLISHED; "
                   f"else /bin/busybox rm -f {path}.hosttmp && printf EXPIRED; fi")
        result = self._run(command, timeout=max(.001, min(1.0, deadline - time.monotonic())),
                           lock_timeout=0, quarantine_timeout=True, total_deadline=deadline)
        if result == b"PUBLISHED": return True
        if result == b"EXPIRED": return False
        raise ValueError("invalid bounded publication result")

    def publish_simulator(self, line: str) -> None:
        """Atomically publish one validated simulator command."""
        self._publish(line, "eng-data-sim-command", _SIM)

    def _read(self, name: str) -> Optional[str]:
        raw = self._run(f"if test -f /tmp/{name}; then /bin/busybox cat /tmp/{name}; fi")
        return raw.decode("ascii", errors="strict") if raw else None

    def read_input(self) -> Optional[str]:
        """Read the complete atomic Weston result file if present."""
        return self._read("weston-vm-input-result")

    def read_simulator(self) -> Optional[str]:
        """Read the complete atomic simulator reply file if present."""
        return self._read("eng-data-sim-reply")

    def observe_debugging_mode(self) -> int:
        """Issue the fixed guest system-bus query and parse its single byte."""
        raw = self._run("/bin/busybox timeout 5 /usr/bin/dbus-send --system --print-reply "
                        "--reply-timeout=3000 --dest=com.lge.car.micom /Ihu "
                        "com.lge.car.micom.ihu.AskDebuggingMode </dev/null 2>/dev/null", timeout=10)
        return vm_guest_parse_debugging_mode(raw)

    def observe_confirm_geometry(self, *, deadline=None) -> dict:
        """Require a new timer record from the fixed log over a bounded probe.

        Record advancement does not prove the surface is foreground; correlate
        it with a separately captured fresh compositor frame.
        """
        # Limit every file read to the original EOF boundary or appended bytes.
        # A boundary digest detects ordinary in-place truncate-and-regrow; no
        # path-based scheme can detect an adversary restoring identical bytes.
        raw = self._run(
            "(set +o pipefail; wb_log=/tmp/launcher-chain/dlt.log; test -f \"$wb_log\" && "
            f"wb_pattern='{_DLT_CONFIRM_ENVELOPE}' && "
            "wb_stat=$(/bin/busybox stat -c '%d:%i:%s' \"$wb_log\") && "
            "IFS=:; set -- $wb_stat; IFS=' '; test \"$#\" -eq 3 || exit 1; "
            "wb_id=$1:$2; wb_before=$3; test \"$wb_before\" -ge 0 || exit 1; "
            "wb_len=256; test \"$wb_before\" -ge 256 || wb_len=$wb_before; "
            "wb_boundary=$((wb_before - wb_len + 1)); "
            "wb_hash=empty; if test \"$wb_len\" -gt 0; then "
            "wb_hash=$(/bin/busybox tail -c +\"$wb_boundary\" \"$wb_log\" | /bin/busybox head -c \"$wb_len\" | /bin/busybox sha256sum) || exit 1; fi; "
            "wb_partial=0; if test \"$wb_before\" -gt 0; then "
            "wb_nl=$(/bin/busybox tail -c +\"$wb_before\" \"$wb_log\" | /bin/busybox head -c 1 | /bin/busybox wc -l) || exit 1; "
            "test \"$wb_nl\" -eq 1 || wb_partial=1; fi && "
            "/bin/busybox sleep 2 && "
            "wb_stat=$(/bin/busybox stat -c '%d:%i:%s' \"$wb_log\") || exit 1; "
            "IFS=:; set -- $wb_stat; IFS=' '; test \"$#\" -eq 3 || exit 1; "
            "test \"$1:$2\" = \"$wb_id\" || exit 1; wb_after=$3; "
            "wb_growth=$((wb_after - wb_before)); test \"$wb_growth\" -gt 0 && test \"$wb_growth\" -le 1048576 || exit 1; "
            "wb_start=$((wb_before + 1)); "
            "wb_bytes=$(/bin/busybox tail -c +\"$wb_start\" \"$wb_log\" | /bin/busybox head -c \"$wb_growth\" | /bin/busybox wc -c) && "
            "test \"$wb_bytes\" -eq \"$wb_growth\" && "
            "wb_endnl=$(/bin/busybox tail -c +\"$wb_after\" \"$wb_log\" | /bin/busybox head -c 1 | /bin/busybox wc -l) && "
            "test \"$wb_endnl\" -eq 0 -o \"$wb_endnl\" -eq 1 && "
            "wb_result=$(/bin/busybox tail -c +\"$wb_start\" \"$wb_log\" | /bin/busybox head -c \"$wb_growth\" | "
            "/bin/busybox awk -v re=\"$wb_pattern\" -v partial=\"$wb_partial\" -v endnl=\"$wb_endnl\" "
            "'function check(s,i,a,p) {if (partial && i==1) return; "
            "p=index(s,\"VM_OBSERVE_CONFIRM geometry\"); if (!p) return; "
            "if (s !~ re) {bad=1; return} split(s,a,\" \"); "
            "if (a[4]+0>255) {bad=1; return} last=substr(s,p,length(s)-p)} "
            "{if (NR>8192) exit 1; if (NR>1) check(prev,NR-1); prev=$0} "
            "END {if (NR>8192) exit 1; if (endnl) check(prev,NR); if (bad || last==\"\") exit 1; print last}') || exit 1; "
            "wb_stat=$(/bin/busybox stat -c '%d:%i:%s' \"$wb_log\") || exit 1; "
            "IFS=:; set -- $wb_stat; IFS=' '; test \"$#\" -eq 3 && test \"$1:$2\" = \"$wb_id\" && test \"$3\" -ge \"$wb_after\" || exit 1; "
            "wb_hash_after=empty; if test \"$wb_len\" -gt 0; then "
            "wb_hash_after=$(/bin/busybox tail -c +\"$wb_boundary\" \"$wb_log\" | /bin/busybox head -c \"$wb_len\" | /bin/busybox sha256sum) || exit 1; fi; "
            "test \"$wb_hash\" = \"$wb_hash_after\" && printf '%s\\n' \"$wb_result\")", timeout=10,
            **({} if deadline is None else {"lock_timeout": 0, "quarantine_timeout": True, "total_deadline": deadline}))
        return vm_guest_parse_confirm_geometry(raw)

    def diagnose_confirm_observation(self) -> dict:
        """Diagnose fixed Confirm log stages without publishing log contents.

        A timed-out guest command quarantines the bridge: it may still execute
        after the host deadline, so no later command may be queued on it.
        """
        total_start, budget = time.monotonic(), 55.0
        result = {"status": "error", "failed_stage": None, "reason": None,
                  "stages": {}, "before": None, "after": None,
                  "before_exists": None, "after_exists": None,
                  "identity_held": None, "size_nonshrinking": None,
                  "new_record": None, "bounded_tail_count": None}
        pattern = _DLT_CONFIRM_ENVELOPE
        log = "/tmp/launcher-chain/dlt.log"

        def stage(name, command, cap=12.0):
            timing = {"lock_wait_s": 0.0, "execution_s": 0.0}
            result["stages"][name] = timing
            remaining = budget - (time.monotonic() - total_start)
            if remaining <= 0:
                raise TimeoutError("total diagnostic deadline")
            return self._run(command, timeout=min(cap, remaining), timing=timing,
                             lock_timeout=remaining, quarantine_timeout=True,
                             total_deadline=total_start + budget).strip()

        def snapshot(name):
            output = stage(name,
                f"wb_log={log}; test -f \"$wb_log\" && "
                "a=$(/bin/busybox stat -c '%d:%i:%s' \"$wb_log\") && "
                f"n=$(/bin/busybox awk -v re='{pattern}' '$0 ~ re && $4+0 <= 255 {{n++}} END {{print n+0}}' \"$wb_log\") && "
                "b=$(/bin/busybox stat -c '%d:%i:%s' \"$wb_log\") && "
                "printf '%s\\n%s\\n%s\\n' \"$a\" \"$n\" \"$b\"")
            match = re.fullmatch(rb"([0-9]+):([0-9]+):([0-9]+)\n([0-9]+)\n([0-9]+):([0-9]+):([0-9]+)", output)
            if not match:
                raise ValueError("invalid fixed snapshot result")
            dev, ino, size, count, dev2, ino2, size2 = map(int, match.groups())
            if (dev, ino) != (dev2, ino2) or size2 < size:
                raise ValueError("log changed during snapshot")
            return {"device": dev, "inode": ino, "size": size2, "count": count}

        checks = (
            ("applet_stat", "test -n \"$(/bin/busybox stat -c '%d:%i:%s' /bin/busybox)\""),
            ("applet_wc", "test \"$(printf abc | /bin/busybox wc -c)\" -eq 3"),
            ("applet_awk", "test \"$(printf '1970/01/01 00:01:11.297223 712970 050 MANG STAN STAN log info V 1 [VM_OBSERVE_CONFIRM geometry x]\\n' | "
                           f"/bin/busybox awk -v re='{pattern}' '$0 ~ re && $4+0 <= 255 {{n++}} END {{print n+0}}')\" -eq 1"),
            ("applet_sleep", "/bin/busybox sleep 1"),
            ("applet_tail", "test \"$(printf abc | /bin/busybox tail -c +2)\" = bc"),
            ("applet_head", "test \"$(printf abc | /bin/busybox head -c 2)\" = ab"),
            ("shell_pipefail", "(set -o pipefail) && (set -o pipefail; false | true; test $? -ne 0)"),
        )
        current = "setup"
        try:
            for current, command in checks:
                if stage(current, command, 6.0):
                    raise ValueError("unexpected applet output")
            current = "before_exists"
            exists = stage(current, f"if test -f {log}; then printf 1; else printf 0; fi", 6.0)
            if exists not in (b"0", b"1"):
                raise ValueError("invalid existence result")
            result["before_exists"] = exists == b"1"
            if not result["before_exists"]:
                raise ValueError("missing log")
            current = "before"
            before = result["before"] = snapshot(current)
            current = "timer_wait"
            if stage(current, "/bin/busybox sleep 2", 8.0):
                raise ValueError("unexpected sleep output")
            current = "after_exists"
            exists = stage(current, f"if test -f {log}; then printf 1; else printf 0; fi", 6.0)
            if exists not in (b"0", b"1"):
                raise ValueError("invalid existence result")
            result["after_exists"] = exists == b"1"
            if not result["after_exists"]:
                raise ValueError("missing log")
            current = "after"
            after = result["after"] = snapshot(current)
            result["identity_held"] = (before["device"], before["inode"]) == (after["device"], after["inode"])
            result["size_nonshrinking"] = after["size"] >= before["size"]
            result["new_record"] = after["count"] > before["count"]
            if not result["identity_held"] or not result["size_nonshrinking"]:
                raise ValueError("log replaced or truncated")
            current = "bounded_tail"
            growth = after["size"] - before["size"]
            if growth > 1048576:
                raise ValueError("appended region exceeds limit")
            # Skip the first line, which may have begun before the baseline.
            output = stage(current, f"(set -o pipefail; /bin/busybox tail -c +{before['size'] + 1} {log} | "
                           f"/bin/busybox head -c 1048577 | /bin/busybox awk -v re='{pattern}' "
                           "'NR > 1 && $0 ~ re && $4+0 <= 255 {n++} END {print n+0}')")
            if not re.fullmatch(rb"[0-9]+", output):
                raise ValueError("invalid bounded count")
            result["bounded_tail_count"] = int(output)
            current = "final_identity"
            final = stage(current, f"/bin/busybox stat -c '%d:%i:%s' {log}")
            match = re.fullmatch(rb"([0-9]+):([0-9]+):([0-9]+)", final)
            if not match:
                raise ValueError("invalid final identity")
            dev, ino, size = map(int, match.groups())
            if (dev, ino) != (after["device"], after["inode"]) or size < after["size"]:
                raise ValueError("log replaced or truncated")
            result["status"] = "completed"
        except (OSError, EOFError, TimeoutError, RuntimeError, ValueError) as exc:
            result["failed_stage"] = current
            result["reason"] = "timeout" if isinstance(exc, TimeoutError) else "stage_failed"
        result["total_s"] = time.monotonic() - total_start
        return result

    def capture(self, *, deadline=None) -> bytes:
        """Capture the actual Weston surface and return its bounded PNG bytes."""
        token = uuid.uuid4().hex
        marker = "WB_FRAME_" + token
        framed = self._run("export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0; "
                            "cd /tmp && /bin/busybox rm -f wayland-screenshot.png && "
                            "/bin/busybox timeout 25 /usr/libexec/weston-screenshooter </dev/null >/tmp/workbench-screenshot.log 2>&1 && "
                            "wb_size=$(/bin/busybox wc -c < wayland-screenshot.png) && "
                            f"test \"$wb_size\" -gt 0 && test \"$wb_size\" -le {_MAX_CAPTURE} && "
                            "set -- $(/bin/busybox sha256sum wayland-screenshot.png) && "
                            f"printf '{marker} META %s %s\\n' \"$wb_size\" \"$1\" && "
                            "/bin/busybox base64 wayland-screenshot.png | "
                            f"/bin/busybox awk '{{printf \"{marker} CHUNK %d %s\\n\", NR, $0}} "
                            f"END {{printf \"{marker} END %d\\n\", NR}}'", timeout=120,
                            **({} if deadline is None else {"lock_timeout": 0, "quarantine_timeout": True, "total_deadline": deadline}))
        return vm_guest_decode_capture(framed, token)

    def capture_timed(self, deadline: float) -> tuple:
        """Capture one PNG and bind it to a guest boottime sample before transfer."""
        token = uuid.uuid4().hex
        marker = "WB_FRAME_" + token
        timed = "WB_TIME_" + token
        framed = self._run("export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0; "
            "cd /tmp && /bin/busybox rm -f wayland-screenshot.png && "
            "/bin/busybox timeout 5 /usr/libexec/weston-screenshooter </dev/null >/tmp/workbench-screenshot.log 2>&1 && "
            "wb_size=$(/bin/busybox wc -c < wayland-screenshot.png) && "
            f"test \"$wb_size\" -gt 0 && test \"$wb_size\" -le {_MAX_CAPTURE} && "
            "set -- $(/bin/busybox sha256sum wayland-screenshot.png) && "
            "read -r wb_up _ </proc/uptime && "
            "wb_ms=$(/bin/busybox awk -v v=\"$wb_up\" 'BEGIN {printf \"%.0f\",v*1000}') && "
            f"printf '{timed} %s\\n{marker} META %s %s\\n' \"$wb_ms\" \"$wb_size\" \"$1\" && "
            "/bin/busybox base64 wayland-screenshot.png | "
            f"/bin/busybox awk '{{printf \"{marker} CHUNK %d %s\\n\", NR, $0}} "
            f"END {{printf \"{marker} END %d\\n\", NR}}'", timeout=6, lock_timeout=0,
            quarantine_timeout=True, total_deadline=deadline)
        matches = [line for line in framed.replace(b"\r\n", b"\n").splitlines() if line.startswith(timed.encode())]
        if len(matches) != 1 or not re.fullmatch(timed.encode() + rb" [1-9][0-9]{0,19}", matches[0]):
            raise ValueError("invalid guest capture time")
        return vm_guest_decode_capture(framed, token), int(matches[0].split()[1])

    def close(self) -> None:
        """Wait briefly for the reader after the owned process has exited."""
        self._reader.join(timeout=5)
