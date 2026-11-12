#!/usr/bin/env python3
"""Build a fail-closed owner USB-Ethernet SSH overlay.

The target runtime selects one enumerated USB network interface, verifies its
USB identity and allowlisted driver, and exposes owner Dropbear at
10.42.0.1:22. This tool validates a pinned static build and stages files without
executing them. USB enumeration and actual SSH sessions remain target-only
verification items.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import configparser
import hashlib
import io
import ipaddress
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import struct
import subprocess
import tempfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

_BASE = "opt/ioniq-owner"
_SERVICE = "ioniq-owner-ssh.service"
_NETWORK_SERVICE = "ioniq-owner-ethernet.service"
_AUTH_SERVICE = "ioniq-owner-auth.service"
_RULE_FILE = "etc/udev/rules.d/70-ioniq-owner-usb.rules"
_KEY_TYPE = b"ssh-ed25519"
_VERSION = "4.0.1"
_PINNED_BINARY_SHA256 = "722c49d48a435ab47d87df102434edc632b5dce27323c37580b4b4e6aa0cc3d8"
_USB_DRIVERS = {
    "0bda:8152": "r8152", "0bda:8153": "r8152",
    "0b95:7720": "asix", "0b95:772a": "asix", "0b95:772b": "asix",
}
_INTERFACE = "ownerusb0"
_ADDRESS = "10.42.0.1/24"


def _read_regular(path: Path, limit: int) -> bytes:
    """Read one bounded regular input without following a final symlink."""
    if ".." in path.parts:
        raise ValueError("parent traversal is not allowed")
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit:
            raise ValueError("input must be a nonempty, bounded regular file")
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("input exceeds size limit")
    return data


def _validate_binary(data: bytes) -> None:
    """Validate the pinned static Dropbear ELF with the reviewed auth policy."""
    if len(data) < 64 or data[:7] != b"\x7fELF\x02\x01\x01":
        raise ValueError("expected a little-endian ELF64 executable")
    kind, machine, version, entry, phoff = struct.unpack_from("<HHIQQ", data, 16)
    ehsize, phsize, phnum = struct.unpack_from("<HHH", data, 52)
    if (kind not in (2, 3) or machine != 62 or version != 1 or ehsize != 64
            or phsize != 56 or not 0 < phnum <= 1024 or phoff < 64
            or phoff + phsize * phnum > len(data)):
        raise ValueError("invalid x86-64 ELF header or program-header table")
    executable_entry = False
    for pos in range(phoff, phoff + phsize * phnum, phsize):
        ptype, flags, offset, vaddr, _, size, memsize, _ = struct.unpack_from(
            "<IIQQQQQQ", data, pos)
        if offset + size > len(data) or (ptype == 1 and size > memsize):
            raise ValueError("ELF segment is outside the executable")
        if ptype == 3:
            raise ValueError("PT_INTERP is forbidden; supply a static executable")
        if ptype == 2:
            if size % 16:
                raise ValueError("invalid ELF dynamic table")
            tags = [
                struct.unpack_from("<qQ", data, p)[0]
                for p in range(offset, offset + size, 16)
            ]
            if 1 in tags or 0 not in tags:
                raise ValueError("dynamic dependencies are forbidden")
        if ptype == 1 and flags & 1 and vaddr <= entry < vaddr + size:
            executable_entry = True
    if not executable_entry:
        raise ValueError("ELF entry is not in an executable load segment")
    if not re.search(rb"(?:Dropbear v|dropbear_)2026\.94(?=[\x00\r\n ])", data):
        raise ValueError("missing exact Dropbear 2026.94 version evidence")
    if any(name + b"\0" not in data for name in (b"dropbear", b"dropbearkey", b"scp")):
        raise ValueError("missing Dropbear multicall applet evidence")
    if hashlib.sha256(data).hexdigest() != _PINNED_BINARY_SHA256:
        raise ValueError("Dropbear digest does not match the reviewed static access build")


def _password_hash(data: bytes) -> bytes:
    """Admit only a SHA-512 crypt hash, never plaintext or blank credentials."""
    if re.fullmatch(rb"\$6\$(?:rounds=[1-9][0-9]{3,8}\$)?[./A-Za-z0-9]{1,16}\$[./A-Za-z0-9]{86}\n?", data) is None:
        raise ValueError("owner password must be a nonempty SHA-512 crypt hash")
    return data.rstrip(b"\n") + b"\n"


def ioniq5_owner_ssh_provision_password(*, password_file: Path, hash_file: Path,
                                      openssl: str = "openssl") -> None:
    """Create private owner credentials once; refuse replacement of either file.

    Secrets are passed to OpenSSL through stdin, never process arguments or logs.
    Existing credentials must be reused explicitly instead of regenerated.
    """
    password_file, hash_file = Path(password_file), Path(hash_file)
    if password_file.parent.resolve(strict=True) != hash_file.parent.resolve(strict=True):
        raise ValueError("credential files must share one private directory")
    directory = password_file.parent
    if directory.is_symlink() or stat.S_IMODE(directory.stat().st_mode) != 0o700:
        raise ValueError("credential directory must be private mode 0700")
    if any(os.path.lexists(path) for path in (password_file, hash_file)):
        raise ValueError("credential destination already exists; reuse it")
    password = secrets.token_urlsafe(12).encode("ascii")
    result = subprocess.run([openssl, "passwd", "-6", "-stdin"],
                            input=password + b"\n", capture_output=True, check=True)
    hashed = _password_hash(result.stdout)
    created = []
    try:
        for path, data in ((password_file, password + b"\n"), (hash_file, hashed)):
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            created.append(path)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException:
        for path in created:
            path.unlink()
        raise


def _ssh_fields(data: bytes) -> list[bytes]:
    """Decode SSH length-prefixed strings with exact consumption."""
    fields = []
    while data:
        if len(data) < 4:
            raise ValueError("truncated SSH key field")
        length = int.from_bytes(data[:4], "big")
        if length > len(data) - 4:
            raise ValueError("truncated SSH key field")
        fields.append(data[4:4 + length])
        data = data[4 + length:]
    return fields


def _public_key(data: bytes) -> bytes:
    """Validate one Ed25519 key and retain root PTY access without forwarding."""
    try:
        text = data.decode("ascii").strip()
        if any(ord(char) < 32 and char != "\t" for char in text):
            raise ValueError("public key must occupy exactly one line")
        parts = text.split()
        if len(parts) < 2 or parts[0] != "ssh-ed25519":
            raise ValueError("expected one plain Ed25519 OpenSSH public key")
        raw = base64.b64decode(parts[1], validate=True)
        fields = _ssh_fields(raw)
        if len(fields) != 2 or fields[0] != _KEY_TYPE or len(fields[1]) != 32:
            raise ValueError("invalid Ed25519 public key fields")
    except (UnicodeError, binascii.Error) as exc:
        raise ValueError("invalid public key encoding") from exc
    return (b"no-port-forwarding,no-agent-forwarding,no-X11-forwarding "
            + _KEY_TYPE + b" " + base64.b64encode(raw) + b"\n")


def _host_key(data: bytes) -> None:
    """Validate the Dropbear Ed25519 host-key container."""
    fields = _ssh_fields(data)
    if (len(fields) != 2 or fields[0] != _KEY_TYPE or len(fields[1]) != 64
            or not any(fields[1][:32]) or not any(fields[1][32:])):
        raise ValueError("expected one Dropbear Ed25519 host key")
    public = Ed25519PrivateKey.from_private_bytes(fields[1][:32]).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    if public != fields[1][32:]:
        raise ValueError("Dropbear host key public half does not match its private seed")


def ioniq5_owner_ssh_usb_ids() -> tuple[str, ...]:
    """Return exact USB IDs supported by the recovered module aliases."""
    return tuple(sorted(_USB_DRIVERS))


def _network_inputs(usb_ids, interface: str, address: str) -> tuple[str, ...]:
    """Reject unreviewed hardware and network policy before interpolation."""
    if interface != _INTERFACE:
        raise ValueError("the dedicated interface must be ownerusb0")
    try:
        parsed = ipaddress.ip_interface(address)
    except ValueError as exc:
        raise ValueError("invalid owner IPv4 address") from exc
    if str(parsed) != _ADDRESS:
        raise ValueError("the dedicated address must be 10.42.0.1/24")
    if usb_ids is None:
        return ioniq5_owner_ssh_usb_ids()
    if isinstance(usb_ids, (str, bytes)):
        raise ValueError("USB IDs must be a sequence of VID:PID strings")
    try:
        values = tuple(usb_ids)
    except TypeError as exc:
        raise ValueError("USB IDs must be a sequence of VID:PID strings") from exc
    if not values:
        raise ValueError("at least one USB ID is required")
    if any(not isinstance(value, str) or value.lower() not in _USB_DRIVERS for value in values):
        raise ValueError("USB ID is absent from the reviewed target module allowlist")
    return tuple(sorted({value.lower() for value in values}))


def _connman_config(data: bytes | None) -> bytes:
    """Preserve existing settings and exclude only the dedicated owner interface."""
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    if data is not None:
        try:
            parser.read_string(data.decode("utf-8"))
        except (UnicodeError, configparser.Error) as exc:
            raise ValueError("invalid existing ConnMan main.conf") from exc
    if not parser.has_section("General"):
        parser.add_section("General")
    previous = parser.get(
        "General", "NetworkInterfaceBlacklist",
        fallback="",
    )
    entries = [value.strip() for value in previous.split(",") if value.strip()]
    for interface in (_INTERFACE,):
        if interface not in entries:
            entries.append(interface)
    parser.set("General", "NetworkInterfaceBlacklist", ",".join(entries))
    output = io.StringIO()
    parser.write(output)
    return output.getvalue().encode("utf-8")


def _udev_rules(usb_ids: tuple[str, ...]) -> bytes:
    """Claim only exact USB IDs with syntax supported by udev 225."""
    rules = ["# Dedicated owner USB NIC; connect one matching adapter at a time."]
    for value in usb_ids:
        vendor, product = value.split(":")
        rules.append(
            'ACTION=="add", SUBSYSTEM=="net", SUBSYSTEMS=="usb", '
            f'ATTRS{{idVendor}}=="{vendor}", ATTRS{{idProduct}}=="{product}", '
            f'NAME="{_INTERFACE}", TAG+="systemd", ENV{{SYSTEMD_WANTS}}+="{_SERVICE}"')
    return ("\n".join(rules) + "\n").encode("ascii")


_STARTUP = r'''#!/bin/sh
# The service owns one revalidated USB NIC and only the address and rules it creates.
set -eu
PATH=/opt/ioniq-owner/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077
exec >>/var/log/IONIQ5_OWNER_SSH.log 2>&1
base=/opt/ioniq-owner
run=/run/ioniq-owner
sysroot=/sys
iface=
iface_syspath=
device_path=
usb_path=
usb_identity=
driver_path=
driver=
ifindex=
ssh_pid=
created_chains=
created_hooks=
address_added=
interface_claimed=

owner_same_interface() {
    [ -n "$iface" ] && [ -n "$ifindex" ] || return 1
    current_iface=$(readlink -f "$sysroot/class/net/$iface" 2>/dev/null) || return 1
    current_device=$(readlink -f "$sysroot/class/net/$iface/device" 2>/dev/null) || return 1
    current_driver=$(readlink -f "$sysroot/class/net/$iface/device/driver" 2>/dev/null) || return 1
    current_ifindex=$(cat "$sysroot/class/net/$iface/ifindex" 2>/dev/null) || return 1
    current_usb_id=
    if [ -r "$usb_path/idVendor" ] && [ -r "$usb_path/idProduct" ]; then
        current_usb_id="$(cat "$usb_path/idVendor"):$(cat "$usb_path/idProduct")"
    fi
    [ "$current_iface" = "$iface_syspath" ] &&
        [ "$current_device" = "$device_path" ] &&
        [ "$current_driver" = "$driver_path" ] &&
        [ "$current_ifindex" = "$ifindex" ] &&
        [ "$current_usb_id" = "$usb_identity" ]
}

owner_scan_usb_nic() {
    usbnic_count=0
    usbnic_name=
    usbnic_iface_syspath=
    usbnic_device_path=
    usbnic_usb_path=
    usbnic_driver_path=
    usbnic_driver=
    for netlink in "$sysroot"/class/net/ownerusb0; do
        [ -e "$netlink" ] || continue
        [ -e "$netlink/device" ] || continue
        candidate_device=$(readlink -f "$netlink/device" 2>/dev/null) || continue
        case "$candidate_device" in "$sysroot"/devices/*) ;; *) continue ;; esac
        parent=$candidate_device
        candidate_usb_path=
        candidate_usb_identity_path=
        while [ "$parent" != "$sysroot/devices" ] && [ "$parent" != / ]; do
            case "$parent" in "$sysroot"/devices/*) ;; *) break ;; esac
            case "${parent##*/}" in
                usb[0-9]*) candidate_usb_path=$parent ;;
            esac
            if [ -z "$candidate_usb_identity_path" ] &&
                    [ -r "$parent/idVendor" ] && [ -r "$parent/idProduct" ]; then
                candidate_usb_identity_path=$parent
            fi
            parent=${parent%/*}
        done
        [ -n "$candidate_usb_path" ] || continue
        usbnic_count=$((usbnic_count + 1))
        [ "$usbnic_count" -eq 1 ] || continue
        usbnic_name=${netlink##*/}
        usbnic_iface_syspath=$(readlink -f "$netlink" 2>/dev/null) || :
        usbnic_device_path=$candidate_device
        usbnic_usb_path=$candidate_usb_identity_path
        usbnic_driver_path=$(readlink -f "$netlink/device/driver" 2>/dev/null) || :
        usbnic_driver=${usbnic_driver_path##*/}
    done
}

owner_require_metadata() {
    path=$1
    expected=$2
    kind=$3
    [ ! -L "$path" ] || {
        echo "Owner SSH runtime path rejected: symlink at $path"
        exit 1
    }
    case "$kind" in
        directory) [ -d "$path" ] ;;
        file) [ -f "$path" ] ;;
        *) exit 1 ;;
    esac || {
        echo "Owner SSH runtime path rejected: wrong type at $path"
        exit 1
    }
    metadata=$(stat -c '%u:%g:%a' "$path") || exit 1
    [ "$metadata" = "0:0:$expected" ] || {
        echo "Owner SSH runtime path rejected: metadata $metadata at $path"
        exit 1
    }
}

owner_firewall_remove() {
    for item in $created_hooks; do
        tool=${item%%:*}
        direction=${item#*:}
        "$tool" -D "$direction" -j "IONIQ5_OWNER_$direction" 2>/dev/null || :
    done
    for item in $created_chains; do
        tool=${item%%:*}
        direction=${item#*:}
        "$tool" -F "IONIQ5_OWNER_$direction" 2>/dev/null || :
        "$tool" -X "IONIQ5_OWNER_$direction" 2>/dev/null || :
    done
}

owner_cleanup() {
    trap - EXIT INT TERM HUP
    if [ -n "$interface_claimed" ] && owner_same_interface; then
        ip link set "$iface" down 2>/dev/null || :
    fi
    [ -z "$ssh_pid" ] || kill "$ssh_pid" 2>/dev/null || :
    [ -z "$ssh_pid" ] || wait "$ssh_pid" 2>/dev/null || :
    # A reused name can represent a different device. Remove the address only
    # when every captured sysfs, identity, driver and ifindex value still matches.
    if [ -n "$address_added" ] && owner_same_interface; then
        ip addr del 10.42.0.1/24 dev "$iface" 2>/dev/null || :
    fi
    owner_firewall_remove
}

trap owner_cleanup EXIT
trap 'exit 0' INT TERM HUP
for command in ip iptables ip6tables mount readlink cat sleep mkdir chmod chown cp stat; do
    command -v "$command" >/dev/null || exit 1
done

owner_scan_usb_nic
if [ "$usbnic_count" -ne 1 ]; then
    echo 'Owner USB interface rejected: no renamed USB candidate'
    exit 1
fi

iface=$usbnic_name
iface_syspath=$usbnic_iface_syspath
device_path=$usbnic_device_path
usb_path=$usbnic_usb_path
driver_path=$usbnic_driver_path
driver=$usbnic_driver
case "$iface" in
    ownerusb0) ;;
    *) echo 'Owner USB interface rejected: wrong name'; exit 1 ;;
esac
case "$driver" in
    @USB_DRIVERS@) ;;
    *) echo "Owner USB driver rejected: $driver is outside the allowlist"; exit 1 ;;
esac
if [ -z "$usb_path" ] || [ ! -r "$usb_path/idVendor" ] || [ ! -r "$usb_path/idProduct" ]; then
    echo 'Owner USB identity is unavailable'
    exit 1
fi
usb_identity="$(cat "$usb_path/idVendor"):$(cat "$usb_path/idProduct")"
vendor=${usb_identity%:*}
product=${usb_identity#*:}
if [ "${#vendor}" -ne 4 ] || [ "${#product}" -ne 4 ]; then
    echo 'Owner USB identity is malformed'
    exit 1
fi
case "$vendor$product" in
    *[!0-9a-fA-F]*) echo 'Owner USB identity is malformed'; exit 1 ;;
esac
case "$usb_identity:$driver" in
    @USB_DRIVER_PAIRS@) ;;
    *) echo 'Owner USB identity rejected'; exit 1 ;;
esac
ifindex=$(cat "$sysroot/class/net/$iface/ifindex")
case "$ifindex" in ''|*[!0-9]*) echo 'Owner interface index is malformed'; exit 1 ;; esac
owner_same_interface || { echo 'Owner USB identity changed during admission'; exit 1; }

# Refuse any pre-existing address or route collision instead of flushing
# another owner's configuration.
current_addresses=$(ip -4 -o addr show dev "$iface") || exit 1
[ -z "$current_addresses" ] || {
    echo 'Owner USB interface already has an IPv4 address'
    exit 1
}
current_routes=$(ip -4 route show exact 10.42.0.0/24) || exit 1
[ -z "$current_routes" ] || {
    echo 'Owner USB IPv4 subnet conflicts with the existing routing table'
    exit 1
}
for tool in iptables ip6tables; do
    for direction in INPUT OUTPUT FORWARD; do
        if "$tool" -L "IONIQ5_OWNER_$direction" -n >/dev/null 2>&1; then
            echo "Owner firewall name collision: $tool:$direction"
            exit 1
        fi
    done
done

# Dropbear validates the authorized-key path against the account home. Keep the
# authentication directory inside root's private runtime home so an OEM root
# directory that is group-writable cannot invalidate an otherwise correct key.
[ ! -L "$run" ] || {
    echo "Owner SSH runtime path rejected: symlink at $run"
    exit 1
}
mkdir -p "$run"
chown 0:0 "$run"
chmod 700 "$run"
owner_require_metadata "$run" 700 directory
auth_dir="$run/.ssh"
[ ! -L "$auth_dir" ] || {
    echo "Owner SSH runtime path rejected: symlink at $auth_dir"
    exit 1
}
mkdir -p "$auth_dir"
chown 0:0 "$auth_dir"
chmod 700 "$auth_dir"
owner_require_metadata "$auth_dir" 700 directory
owner_require_metadata "$base/keys/authorized_keys" 600 file
[ ! -L "$auth_dir/authorized_keys" ] || {
    echo "Owner SSH runtime path rejected: symlink at $auth_dir/authorized_keys"
    exit 1
}
cp "$base/keys/authorized_keys" "$auth_dir/authorized_keys"
chown 0:0 "$auth_dir/authorized_keys"
chmod 600 "$auth_dir/authorized_keys"
owner_require_metadata "$auth_dir/authorized_keys" 600 file

owner_same_interface || exit 1
interface_claimed=1
ip link set "$iface" down
for tool in iptables ip6tables; do
    for direction in INPUT OUTPUT FORWARD; do
        "$tool" -N "IONIQ5_OWNER_$direction"
        created_chains="$tool:$direction $created_chains"
    done
done

iptables -A IONIQ5_OWNER_INPUT -i "$iface" -s 10.42.0.0/24 -d 10.42.0.1 \
    -p tcp --dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -A IONIQ5_OWNER_INPUT -i "$iface" -j DROP
iptables -A IONIQ5_OWNER_OUTPUT -o "$iface" -s 10.42.0.1 -d 10.42.0.0/24 \
    -p tcp --sport 22 -m conntrack --ctstate ESTABLISHED -j ACCEPT
iptables -A IONIQ5_OWNER_OUTPUT -o "$iface" -j DROP
iptables -A IONIQ5_OWNER_FORWARD -i "$iface" -j DROP
iptables -A IONIQ5_OWNER_FORWARD -o "$iface" -j DROP
ip6tables -A IONIQ5_OWNER_INPUT -i "$iface" -j DROP
ip6tables -A IONIQ5_OWNER_OUTPUT -o "$iface" -j DROP
ip6tables -A IONIQ5_OWNER_FORWARD -i "$iface" -j DROP
ip6tables -A IONIQ5_OWNER_FORWARD -o "$iface" -j DROP

for tool in iptables ip6tables; do
    for direction in INPUT OUTPUT FORWARD; do
        "$tool" -I "$direction" 1 -j "IONIQ5_OWNER_$direction"
        created_hooks="$tool:$direction $created_hooks"
    done
done

# Account overrides stay inside systemd's private mount namespace. The password
# hash is never logged; a '*' explicitly retains key-only mode when requested.
owner_require_metadata "$base/keys/owner_password_hash" 600 file
password_hash=$(cat "$base/keys/owner_password_hash")
case "$password_hash" in
    '$6$'*|'*') ;;
    *) echo 'Owner password hash rejected'; exit 1 ;;
esac
case "$password_hash" in *:*|*'
'*) echo 'Owner password hash rejected'; exit 1 ;; esac
printf 'root:%s:0:0:Owner:/run/ioniq-owner:/bin/sh\n' "$password_hash" > "$run/passwd"
chmod 644 "$run/passwd"
mount --bind "$run/passwd" /etc/passwd
printf '/bin/sh\n' > "$run/shells"
mount --bind "$run/shells" /etc/shells
owner_same_interface || exit 1
ip addr add 10.42.0.1/24 dev "$iface"
address_added=1
owner_same_interface || exit 1
ip link set "$iface" up
# The pinned build supports key OR password; PAM and forwarding are compiled out.
# DISABLE_SYSLOG makes stderr logging automatic in this exact build.
"$base/bin/dropbear" -F -m -l "$iface" -p 10.42.0.1:22 \
    -D "$auth_dir" -r "$base/keys/dropbear_ed25519_host_key" \
    -P "$run/dropbear.pid" &
ssh_pid=$!
printf 'IONIQ5_OWNER_SSH_VERSION=@VERSION@ USB %s 10.42.0.1:22 client 10.42.0.2/24\n' "$iface"
while owner_same_interface && kill -0 "$ssh_pid" 2>/dev/null; do
    sleep 2
done
if owner_same_interface; then
    echo 'Owner SSH exited'
    exit 1
fi
echo 'Owner USB removed'
exit 0
'''

_UNIT = '''[Unit]
Description=IONIQ5 owner USB-Ethernet SSH @VERSION@
BindsTo=sys-subsystem-net-devices-ownerusb0.device
After=local-fs.target sys-subsystem-net-devices-ownerusb0.device
ConditionPathExists=/sys/class/net/ownerusb0

[Service]
Type=simple
User=root
UMask=0077
MountFlags=private
ExecStart=/opt/ioniq-owner/start-owner-ssh
Restart=no
KillMode=control-group
TimeoutStopSec=10s

'''


def _independent_services(startup: str, unit: str, *, web_console: bool) -> dict[str, tuple[bytes, int]]:
    """Separate link lifetime from authentication using the same reviewed policy.

    The combined template remains supported for earlier offline workflows. The
    recovery build derives both scripts from it, so key validation and network
    admission rules have one implementation. Authentication failure cannot
    remove the address or firewall needed by the independent browser console.
    """
    auth_begin = startup.index("# Dropbear validates")
    auth_end = startup.index("\nowner_same_interface || exit 1\ninterface_claimed=1", auth_begin)
    account_begin = startup.index("# Account overrides")
    account_end = startup.index("\nowner_same_interface || exit 1\nip addr add", account_begin)
    server_begin = startup.index("# The pinned build supports")
    server_end = startup.index("\nssh_pid=$!", server_begin) + len("\nssh_pid=$!")
    metadata_begin = startup.index("owner_require_metadata() {")
    metadata_end = startup.index("\nowner_firewall_remove()", metadata_begin)
    auth = (
        "#!/bin/sh\nset -eu\n"
        "PATH=/opt/ioniq-owner/bin:/usr/sbin:/usr/bin:/sbin:/bin\nexport PATH\numask 077\n"
        "exec >>/var/log/IONIQ5_OWNER_AUTH.log 2>&1\n"
        "base=/opt/ioniq-owner\nrun=/run/ioniq-owner\nssh_pid=\n"
        + f"iface={_INTERFACE}\n"
        + "owner_auth_cleanup() {\n    trap - EXIT INT TERM HUP\n"
        '    [ -z "$ssh_pid" ] || kill "$ssh_pid" 2>/dev/null || :\n'
        '    [ -z "$ssh_pid" ] || wait "$ssh_pid" 2>/dev/null || :\n}\n'
        "trap owner_auth_cleanup EXIT\ntrap 'exit 0' INT TERM HUP\n"
        + startup[metadata_begin:metadata_end] + "\n"
        + startup[auth_begin:auth_end] + "\n"
        + startup[account_begin:account_end] + "\n"
        + startup[server_begin:server_end] + "\n"
        + f"printf 'IONIQ5_OWNER_AUTH_VERSION={_VERSION} key-or-password\\n'\n"
        + 'wait "$ssh_pid"\n'
    )
    network = startup
    for fragment in (startup[auth_begin:auth_end], startup[account_begin:account_end],
                     startup[server_begin:server_end]):
        network = network.replace(fragment, "", 1)
    network = network.replace('    [ -z "$ssh_pid" ] || kill "$ssh_pid" 2>/dev/null || :\n', "")
    network = network.replace('    [ -z "$ssh_pid" ] || wait "$ssh_pid" 2>/dev/null || :\n', "")
    network = network.replace("ssh_pid=\n", "")
    network = network.replace('while owner_same_interface && kill -0 "$ssh_pid" 2>/dev/null; do',
                              'while owner_same_interface; do')
    network = network.replace("if owner_same_interface; then\n    echo 'Owner SSH exited'\n    exit 1\nfi\n", "")
    children = _AUTH_SERVICE + (" ioniq-owner-web.service" if web_console else "")
    network = network.replace(
        'ip link set "$iface" up\n',
        'ip link set "$iface" up\n'
        + f"if ! systemctl start --no-block {children}; then\n"
        + "    echo 'Owner Ethernet remains ready; a login service could not be started'\nfi\n", 1)
    if web_console:
        for direction, option, prefix in (("INPUT", "--dport", "-i"), ("OUTPUT", "--sport", "-o")):
            rule_start = network.index(f"iptables -A IONIQ5_OWNER_{direction} {prefix}")
            rule_end = network.index("\n", network.index("\\\n", rule_start) + 2)
            rule = network[rule_start:rule_end]
            network = network[:rule_end] + "\n" + rule.replace(f"{option} 22", f"{option} 8443") + network[rule_end:]
    network_unit = unit.replace("key-only SSH", "Ethernet").replace(
        "USB-Ethernet SSH", "USB-Ethernet link").replace("start-owner-ssh", "start-owner-ethernet")
    auth_unit = f'''[Unit]
Description=IONIQ5 independent key-or-password SSH {_VERSION}
BindsTo={_NETWORK_SERVICE} sys-subsystem-net-devices-ownerusb0.device
After={_NETWORK_SERVICE}

[Service]
Type=simple
User=root
UMask=0077
MountFlags=private
ExecStart=/opt/ioniq-owner/start-owner-ssh
Restart=no
KillMode=control-group
TimeoutStopSec=10s
'''
    return {
        f"{_BASE}/start-owner-ethernet": (network.encode("ascii"), 0o755),
        f"{_BASE}/start-owner-ssh": (auth.encode("ascii"), 0o755),
        f"etc/systemd/system/{_NETWORK_SERVICE}": (network_unit.encode("ascii"), 0o644),
        f"etc/systemd/system/{_AUTH_SERVICE}": (auth_unit.encode("ascii"), 0o644),
    }


def ioniq5_owner_ssh_generate(*, dropbear: Path, public_key: Path, host_key: Path,
                             output: Path, usb_ids: tuple[str, ...] | None = None,
                             interface: str = _INTERFACE, address: str = _ADDRESS,
                             connman_config: Path | None = None,
                             password_hash: Path | None = None,
                             independent_access: bool = False,
                             web_console: bool = False) -> dict:
    """Validate inputs and stage the USB-Ethernet overlay plus manifest.

    Parent must exist. Existing output and manifest paths, including dangling
    links, are rejected. Inputs are never executed. Firmware packaging must
    apply the manifest's root ownership to every staged member.
    """
    if web_console and not independent_access:
        raise ValueError("browser console requires independent network and login services")
    selected_ids = _network_inputs(usb_ids, interface, address)
    output = Path(output)
    if ".." in output.parts or output.name in ("", ".", ".."):
        raise ValueError("unsafe output path")
    output = output.parent.resolve(strict=True) / output.name
    manifest_path = output.with_name(output.name + ".manifest.json")
    if os.path.lexists(output) or os.path.lexists(manifest_path):
        raise ValueError("output or sibling manifest already exists")

    binary = _read_regular(Path(dropbear), 64 * 1024 * 1024)
    public = _read_regular(Path(public_key), 16 * 1024)
    host = _read_regular(Path(host_key), 1024)
    _validate_binary(binary)
    authorized = _public_key(public)
    _host_key(host)
    hashed = _password_hash(_read_regular(Path(password_hash), 256)) if password_hash else b"*\n"
    existing_config = (
        _read_regular(Path(connman_config), 1024 * 1024)
        if connman_config else None
    )
    config = _connman_config(existing_config)
    selected_drivers = sorted({_USB_DRIVERS[value] for value in selected_ids})
    startup = (
        _STARTUP
        .replace("@USB_DRIVER_PAIRS@", "|".join(value + ":" + _USB_DRIVERS[value] for value in selected_ids))
        .replace("@USB_DRIVERS@", "|".join(selected_drivers))
        .replace("@VERSION@", _VERSION)
        .encode("ascii")
    )
    unit = _UNIT.replace("@VERSION@", _VERSION).encode("ascii")
    files = {
        f"{_BASE}/bin/dropbearmulti": (binary, 0o755),
        f"{_BASE}/keys/authorized_keys": (authorized, 0o600),
        f"{_BASE}/keys/dropbear_ed25519_host_key": (host, 0o600),
        f"{_BASE}/keys/owner_password_hash": (hashed, 0o600),
        f"{_BASE}/start-owner-ssh": (startup, 0o755),
        # Dropbear resets login PATH; put the server SCP applet in that path.
        "usr/bin/scp": (b'#!/bin/sh\nexec /opt/ioniq-owner/bin/dropbearmulti scp "$@"\n', 0o755),
        f"etc/systemd/system/{_SERVICE}": (unit, 0o644),
        _RULE_FILE: (_udev_rules(selected_ids), 0o644),
        "etc/connman/main.conf": (config, 0o644),
        "etc/modules-load.d/ioniq-owner-usb.conf": (
            ("\n".join(selected_drivers) + "\n").encode(), 0o644),
    }
    if independent_access:
        files.pop(f"etc/systemd/system/{_SERVICE}")
        files.update(_independent_services(startup.decode("ascii"), unit.decode("ascii"),
                                          web_console=web_console))
        files[_RULE_FILE] = (_udev_rules(selected_ids).replace(_SERVICE.encode(), _NETWORK_SERVICE.encode()), 0o644)
    links = {
        f"{_BASE}/bin/{name}": "dropbearmulti"
        for name in ("dropbear", "dropbearkey", "scp")
    }
    manifest = {
        "format": 2,
        "version": _VERSION,
        "transport": "usb-ethernet",
        "dropbear_version": "2026.94",
        "dropbear_sha256": hashlib.sha256(binary).hexdigest(),
        "authentication": ["publickey", "password"] if password_hash else ["publickey"],
        "independent_access_services": independent_access,
        "browser_console_firewall": web_console,
        "ssh_address": "10.42.0.1:22",
        "client_address": "10.42.0.2/24",
        "interface": interface,
        "usb_ids": list(selected_ids),
        "archive_ownership": {"uid": 0, "gid": 0},
        "files": {
            name: {
                "sha256": hashlib.sha256(data).hexdigest(),
                "mode": oct(mode),
                "uid": 0,
                "gid": 0,
            }
            for name, (data, mode) in sorted(files.items())
        },
        "symlinks": dict(sorted(links.items())),
        "limitations": [
            "Target USB enumeration, driver binding, and live Dropbear behavior require head-unit verification.",
            "The client must statically configure 10.42.0.2/24; the overlay provides no DHCP service.",
            "Archive every overlay member as root:root; host staging ownership is not target ownership.",
        ],
    }

    staging = Path(tempfile.mkdtemp(prefix=".ioniq-owner-", dir=output.parent))
    manifest_created = False
    output_created = False
    try:
        for name, (data, mode) in files.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(mode)
        for name, target in links.items():
            link = staging / name
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(target)
        for directory in sorted(
            (path for path in staging.rglob("*") if path.is_dir()),
            reverse=True,
        ):
            directory.chmod(0o700 if directory == staging / _BASE / "keys" else 0o755)
        staging.chmod(0o700)

        fd = os.open(manifest_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        manifest_created = True
        with os.fdopen(fd, "w") as stream:
            stream.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        output.mkdir(mode=0o700)
        output_created = True
        staging.rename(output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        if output_created:
            try:
                output.rmdir()
            except OSError:
                pass
        if manifest_created:
            try:
                manifest_path.unlink()
            except OSError:
                pass
        raise
    return manifest


def ioniq5_owner_ssh_main(argv: list[str] | None = None) -> int:
    """Generate the USB-Ethernet overlay from explicit artifact inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("dropbear", "public-key", "host-key", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--usb-id", action="append", help="repeatable reviewed VID:PID")
    parser.add_argument("--password-hash", type=Path,
                        help="private SHA-512 crypt hash enabling owner password fallback")
    parser.add_argument("--independent-access", action="store_true")
    parser.add_argument("--web-console", action="store_true", help="allow the independent HTTPS terminal on 8443")
    parser.add_argument(
        "--connman-config",
        type=Path,
        help="existing target main.conf to preserve",
    )
    args = parser.parse_args(argv)
    try:
        ioniq5_owner_ssh_generate(
            dropbear=args.dropbear,
            public_key=args.public_key,
            host_key=args.host_key,
            connman_config=args.connman_config,
            password_hash=args.password_hash,
            independent_access=args.independent_access,
            web_console=args.web_console,
            usb_ids=args.usb_id,
            output=args.output,
        )
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, f"overlay rejected: {exc}\n")
    print(f"Created overlay: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(ioniq5_owner_ssh_main())
