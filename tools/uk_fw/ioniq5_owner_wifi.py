#!/usr/bin/env python3
"""Generate an independent IONIQ5 owner Wi-Fi access overlay.

The generated boot service starts a WPA2 access point on the recovered stock
Broadcom radio and a separate Dropbear listener at 10.43.0.1:22. It reuses the
owner key, host key, password hash, and pinned Dropbear binary staged by the
USB-Ethernet module. No forwarding, bridging, or DHCP service is introduced.
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

_BASE = "opt/ioniq-owner"
_WIFI_BASE = f"{_BASE}/wifi"
_VERSION = "1.0.0"
_INTERFACE = "wlan0"
_ADDRESS = "10.43.0.1/24"
_SERVICE = "ioniq5-owner-wifi.service"
_UNIT_FILE = f"etc/systemd/system/{_SERVICE}"
_VENDOR_DROPIN = (
    "etc/systemd/system/supplicantmanager.service.d/"
    "60-ioniq5-owner-wifi.conf"
)
_VENDOR_MARKER = f"{_WIFI_BASE}/vendor-manager-suppressed"
_CONNMAN_CONFIG = "etc/connman/main.conf"
_MODULES_LOAD = "etc/modules-load.d/ioniq5-owner-wifi.conf"
_STARTUP = f"{_BASE}/start-owner-wifi"
_WPA_CONFIG = f"{_WIFI_BASE}/wpa_supplicant.conf"
_SHA512_CRYPT_ERE = (
    r"\$6\$(rounds=[1-9][0-9]{3,8}\$)?"
    r"[./A-Za-z0-9]{1,16}\$[./A-Za-z0-9]{86}"
)


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


def _wifi_passphrase(data: bytes) -> bytes:
    """Validate one WPA passphrase file without admitting control bytes."""
    if data.endswith(b"\r\n"):
        data = data[:-2]
    elif data.endswith(b"\n"):
        data = data[:-1]
    if not 8 <= len(data) <= 63:
        raise ValueError("Wi-Fi passphrase must contain 8 to 63 ASCII bytes")
    if any(byte < 0x20 or byte > 0x7E for byte in data):
        raise ValueError("Wi-Fi passphrase must contain printable ASCII only")
    return data


def _ssid(value: object) -> str:
    """Validate a WPA SSID that can be represented exactly in the config."""
    if not isinstance(value, str):
        raise ValueError("ssid must be a string")
    try:
        encoded = value.encode("ascii")
    except UnicodeError as exc:
        raise ValueError("ssid must contain ASCII only") from exc
    if not 1 <= len(encoded) <= 32:
        raise ValueError("ssid must contain 1 to 32 ASCII bytes")
    if any(byte < 0x20 or byte > 0x7E for byte in encoded):
        raise ValueError("ssid must contain printable ASCII only")
    return value


def _psk(passphrase: bytes, ssid: bytes) -> str:
    """Derive the WPA2 PSK so the generated config contains no passphrase."""
    return hashlib.pbkdf2_hmac(
        "sha1",
        passphrase,
        ssid,
        4096,
        dklen=32,
    ).hex()


def _connman_config(data: bytes | None) -> bytes:
    """Preserve existing ConnMan settings and exclude only the owner AP."""
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
        "General",
        "NetworkInterfaceBlacklist",
        fallback="",
    )
    entries = [value.strip() for value in previous.split(",") if value.strip()]
    if _INTERFACE not in entries:
        entries.append(_INTERFACE)
    parser.set("General", "NetworkInterfaceBlacklist", ",".join(entries))
    output = io.StringIO()
    parser.write(output)
    return output.getvalue().encode("utf-8")


def _wpa_config(ssid: str, passphrase: bytes) -> bytes:
    """Build a WPA2-only AP config with an encoded SSID and derived PSK."""
    encoded_ssid = ssid.encode("ascii")
    return (
        "# Generated IONIQ5 owner AP. This file contains a derived PSK only.\n"
        "ctrl_interface=/run/ioniq5-owner-wifi/supplicant\n"
        "ctrl_interface_group=0\n"
        "ap_scan=2\n"
        "p2p_disabled=1\n"
        "network={\n"
        "    mode=2\n"
        f"    ssid={encoded_ssid.hex()}\n"
        "    frequency=2412\n"
        "    beacon_int=100\n"
        "    key_mgmt=WPA-PSK\n"
        "    proto=RSN\n"
        "    pairwise=CCMP\n"
        "    group=CCMP\n"
        "    auth_alg=OPEN\n"
        f"    psk={_psk(passphrase, encoded_ssid)}\n"
        "}\n"
    ).encode("ascii")


_STARTUP_TEMPLATE = r'''#!/bin/sh
# Own exactly one Wi-Fi AP and one Dropbear process. A failure here has no
# dependency on, and cannot alter, the independently booted Ethernet service.
set -eu
PATH=/opt/ioniq-owner/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077
exec >>/var/log/IONIQ5_OWNER_WIFI.log 2>&1
base=/opt/ioniq-owner
run=/run/ioniq5-owner-wifi
sysroot=/sys
iface=wlan0
control=$run/supplicant
wpapid=$run/wpa_supplicant.pid
sshpid=$run/dropbear.pid
iface_path=
ifindex=
initial_up=
wpa_pid=
ssh_pid=
created_chains=
created_hooks=
address_added=
interface_claimed=

owner_same_interface() {
    [ -n "$iface_path" ] && [ -n "$ifindex" ] || return 1
    current_path=$(readlink -f "$sysroot/class/net/$iface" 2>/dev/null) || return 1
    current_ifindex=$(cat "$sysroot/class/net/$iface/ifindex" 2>/dev/null) || return 1
    [ "$current_path" = "$iface_path" ] && [ "$current_ifindex" = "$ifindex" ]
}

owner_require_metadata() {
    path=$1
    expected=$2
    kind=$3
    [ ! -L "$path" ] || {
        echo "Owner Wi-Fi runtime path rejected: symlink at $path"
        exit 1
    }
    case "$kind" in
        directory) [ -d "$path" ] ;;
        file) [ -f "$path" ] ;;
        *) exit 1 ;;
    esac || {
        echo "Owner Wi-Fi runtime path rejected: wrong type at $path"
        exit 1
    }
    metadata=$(stat -c '%u:%g:%a' "$path") || exit 1
    [ "$metadata" = "0:0:$expected" ] || {
        echo "Owner Wi-Fi runtime path rejected: metadata $metadata at $path"
        exit 1
    }
}

owner_firewall_remove() {
    for item in $created_hooks; do
        tool=${item%%:*}
        direction=${item#*:}
        "$tool" -D "$direction" -j "IONIQ5_WIFI_$direction" 2>/dev/null || :
    done
    for item in $created_chains; do
        tool=${item%%:*}
        direction=${item#*:}
        "$tool" -F "IONIQ5_WIFI_$direction" 2>/dev/null || :
        "$tool" -X "IONIQ5_WIFI_$direction" 2>/dev/null || :
    done
}

owner_cleanup() {
    trap - EXIT INT TERM HUP
    [ -z "$ssh_pid" ] || kill "$ssh_pid" 2>/dev/null || :
    [ -z "$ssh_pid" ] || wait "$ssh_pid" 2>/dev/null || :
    [ -z "$wpa_pid" ] || kill "$wpa_pid" 2>/dev/null || :
    [ -z "$wpa_pid" ] || wait "$wpa_pid" 2>/dev/null || :
    owner_firewall_remove
    # Remove only the two known control sockets before a failed-service retry.
    if [ -d "$control" ] && [ ! -L "$control" ]; then
        rm -f "$control/$iface" "$control/global" 2>/dev/null || :
        rmdir "$control" 2>/dev/null || :
    fi
    if [ -n "$address_added" ] && owner_same_interface; then
        ip addr del 10.43.0.1/24 dev "$iface" 2>/dev/null || :
    fi
    if [ -n "$interface_claimed" ] && owner_same_interface; then
        ip link set "$iface" down 2>/dev/null || :
        # Return the physical interface to the station mode observed at start.
        iw dev "$iface" set type managed 2>/dev/null || :
        if [ "$initial_up" = 1 ]; then
            ip link set "$iface" up 2>/dev/null || :
        fi
    fi
}

trap owner_cleanup EXIT
trap 'exit 0' INT TERM HUP
for command in awk cat chmod chown cp grep iptables ip ip6tables iw kill \
        mkdir modprobe mount pidof readlink rm rmdir sleep stat wpa_cli \
        wpa_supplicant; do
    command -v "$command" >/dev/null || exit 1
done

# Explicit module loading bypasses alias autoload blacklisting while retaining
# the OEM blacklist for unrelated auto-probe paths.
modprobe bcmdhd || {
    echo 'Owner Wi-Fi radio module bcmdhd did not load'
    exit 1
}

wait_count=15
while [ ! -e "$sysroot/class/net/$iface" ] && [ "$wait_count" -gt 0 ]; do
    sleep 1
    wait_count=$((wait_count - 1))
done
if [ ! -e "$sysroot/class/net/$iface" ]; then
    echo 'Owner Wi-Fi interface wlan0 did not appear within 15 seconds'
    exit 1
fi
if [ ! -e "$sysroot/class/net/$iface/phy80211" ]; then
    echo 'Owner Wi-Fi interface wlan0 is not backed by a cfg80211 radio'
    exit 1
fi
iface_path=$(readlink -f "$sysroot/class/net/$iface" 2>/dev/null) || exit 1
case "$iface_path" in "$sysroot"/devices/*) ;; *) echo 'Owner Wi-Fi sysfs path rejected'; exit 1 ;; esac
ifindex=$(cat "$sysroot/class/net/$iface/ifindex")
case "$ifindex" in ''|*[!0-9]*) echo 'Owner Wi-Fi interface index is malformed'; exit 1 ;; esac
owner_same_interface || { echo 'Owner Wi-Fi identity changed during admission'; exit 1; }

if pidof wpa_supplicant >/dev/null 2>&1; then
    echo 'Owner Wi-Fi refused: a pre-existing wpa_supplicant owns the radio'
    exit 1
fi
iw_info=$(iw dev "$iface" info) || {
    echo 'Owner Wi-Fi refused: stock iw cannot inspect wlan0'
    exit 1
}
iface_type=$(printf '%s\n' "$iw_info" | awk '$1 == "type" { print $2; exit }')
if [ "$iface_type" != managed ]; then
    echo "Owner Wi-Fi refused: wlan0 starts in '$iface_type' mode rather than managed"
    exit 1
fi
initial_flags=$(ip -o link show dev "$iface" | awk -F'[<>]' '{ print $2; exit }') || exit 1
case ",$initial_flags," in *,UP,*) initial_up=1 ;; *) initial_up=0 ;; esac

current_addresses=$(ip -4 -o addr show dev "$iface") || exit 1
[ -z "$current_addresses" ] || {
    echo 'Owner Wi-Fi refused: wlan0 already has an IPv4 address'
    exit 1
}
current_routes=$(ip -4 route show exact 10.43.0.0/24) || exit 1
[ -z "$current_routes" ] || {
    echo 'Owner Wi-Fi refused: the IPv4 subnet conflicts with the routing table'
    exit 1
}
for tool in iptables ip6tables; do
    for direction in INPUT OUTPUT FORWARD; do
        if "$tool" -L "IONIQ5_WIFI_$direction" -n >/dev/null 2>&1; then
            echo "Owner Wi-Fi firewall name collision: $tool:$direction"
            exit 1
        fi
    done
done

[ ! -L "$run" ] || {
    echo "Owner Wi-Fi runtime path rejected: symlink at $run"
    exit 1
}
mkdir -p "$run"
chown 0:0 "$run"
chmod 700 "$run"
owner_require_metadata "$run" 700 directory
auth_dir="$run/.ssh"
[ ! -L "$auth_dir" ] || {
    echo "Owner Wi-Fi runtime path rejected: symlink at $auth_dir"
    exit 1
}
mkdir -p "$auth_dir"
chown 0:0 "$auth_dir"
chmod 700 "$auth_dir"
owner_require_metadata "$auth_dir" 700 directory
owner_require_metadata "$base/keys/authorized_keys" 600 file
owner_require_metadata "$base/keys/dropbear_ed25519_host_key" 600 file
owner_require_metadata "$base/keys/owner_password_hash" 600 file
owner_require_metadata "$base/wifi/wpa_supplicant.conf" 600 file
[ ! -L "$auth_dir/authorized_keys" ] || {
    echo "Owner Wi-Fi runtime path rejected: symlink at $auth_dir/authorized_keys"
    exit 1
}
cp "$base/keys/authorized_keys" "$auth_dir/authorized_keys"
chown 0:0 "$auth_dir/authorized_keys"
chmod 600 "$auth_dir/authorized_keys"
owner_require_metadata "$auth_dir/authorized_keys" 600 file

# Password must be enabled. Validate the exact SHA-512 crypt alphabet before
# exposing it only through this service's private passwd mount.
password_hash=$(cat "$base/keys/owner_password_hash")
printf '%s\n' "$password_hash" |
    grep -Eq '^@PASSWORD_HASH_ERE@$' || {
    echo 'Owner Wi-Fi password hash rejected'
    exit 1
}
printf 'root:%s:0:0:Owner:/run/ioniq5-owner-wifi:/bin/sh\n' "$password_hash" > "$run/passwd"
chmod 644 "$run/passwd"
mount --bind "$run/passwd" /etc/passwd
printf '/bin/sh\n' > "$run/shells"
mount --bind "$run/shells" /etc/shells

[ ! -L "$control" ] || {
    echo "Owner Wi-Fi runtime path rejected: symlink at $control"
    exit 1
}
mkdir -p "$control"
chown 0:0 "$control"
chmod 700 "$control"
owner_require_metadata "$control" 700 directory

owner_same_interface || exit 1
interface_claimed=1
ip link set "$iface" down
wpa_supplicant -Dnl80211 -i"$iface" -c "$base/wifi/wpa_supplicant.conf" \
    -C "$control" -P "$wpapid" &
wpa_pid=$!

ap_wait=15
ap_ready=0
while [ "$ap_wait" -gt 0 ]; do
    if ! kill -0 "$wpa_pid" 2>/dev/null; then
        echo 'Owner Wi-Fi wpa_supplicant exited before AP startup'
        exit 1
    fi
    if iw dev "$iface" info 2>/dev/null | grep -Eq '^[[:space:]]*type AP[[:space:]]*$'; then
        if wpa_cli -p "$control" -i "$iface" ping 2>/dev/null | grep -q PONG; then
            ap_ready=1
            break
        fi
    fi
    sleep 1
    ap_wait=$((ap_wait - 1))
done
if [ "$ap_ready" != 1 ]; then
    echo 'Owner Wi-Fi AP did not become ready within 15 seconds'
    exit 1
fi
owner_same_interface || exit 1

ip addr add 10.43.0.1/24 dev "$iface"
address_added=1
owner_same_interface || exit 1
ip link set "$iface" up

for tool in iptables ip6tables; do
    for direction in INPUT OUTPUT FORWARD; do
        "$tool" -N "IONIQ5_WIFI_$direction"
        created_chains="$tool:$direction $created_chains"
    done
done
iptables -A IONIQ5_WIFI_INPUT -i "$iface" -s 10.43.0.0/24 -d 10.43.0.1 \
    -p tcp --dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -A IONIQ5_WIFI_INPUT -i "$iface" -j DROP
iptables -A IONIQ5_WIFI_OUTPUT -o "$iface" -s 10.43.0.1 -d 10.43.0.0/24 \
    -p tcp --sport 22 -m conntrack --ctstate ESTABLISHED -j ACCEPT
iptables -A IONIQ5_WIFI_OUTPUT -o "$iface" -j DROP
iptables -A IONIQ5_WIFI_FORWARD -i "$iface" -j DROP
iptables -A IONIQ5_WIFI_FORWARD -o "$iface" -j DROP
ip6tables -A IONIQ5_WIFI_INPUT -i "$iface" -j DROP
ip6tables -A IONIQ5_WIFI_OUTPUT -o "$iface" -j DROP
ip6tables -A IONIQ5_WIFI_FORWARD -i "$iface" -j DROP
ip6tables -A IONIQ5_WIFI_FORWARD -o "$iface" -j DROP
for tool in iptables ip6tables; do
    for direction in INPUT OUTPUT FORWARD; do
        "$tool" -I "$direction" 1 -j "IONIQ5_WIFI_$direction"
        created_hooks="$tool:$direction $created_hooks"
    done
done

owner_same_interface || exit 1
"$base/bin/dropbear" -F -m -l "$iface" -p 10.43.0.1:22 \
    -D "$auth_dir" -r "$base/keys/dropbear_ed25519_host_key" \
    -P "$sshpid" &
ssh_pid=$!
printf 'IONIQ5_OWNER_WIFI_VERSION=@VERSION@ AP wlan0 10.43.0.1:22 client 10.43.0.2/24\n'

while owner_same_interface &&
        kill -0 "$wpa_pid" 2>/dev/null &&
        kill -0 "$ssh_pid" 2>/dev/null; do
    sleep 2
done
if ! owner_same_interface; then
    echo 'Owner Wi-Fi interface removed or replaced'
    exit 0
fi
if ! kill -0 "$wpa_pid" 2>/dev/null; then
    echo 'Owner Wi-Fi wpa_supplicant exited'
    exit 1
fi
echo 'Owner Wi-Fi Dropbear exited'
exit 1
'''

_UNIT = '''[Unit]
Description=IONIQ5 independent owner Wi-Fi AP and SSH @VERSION@
After=local-fs.target systemd-modules-load.service
Wants=systemd-modules-load.service
StartLimitIntervalSec=30
StartLimitBurst=3

[Service]
Type=simple
User=root
UMask=0077
MountFlags=private
ExecStart=/opt/ioniq-owner/start-owner-wifi
Restart=on-failure
RestartSec=3s
TimeoutStopSec=12s
KillMode=control-group

[Install]
WantedBy=multi-user.target
'''

_VENDOR_DROPIN_CONTENT = '''[Unit]
# The marker is staged by this access build. This condition suppresses only the
# OEM supplicant manager; Ethernet, ConnMan, and other OEM services stay intact.
ConditionPathExists=!@VENDOR_MARKER@
'''


def _manifest(
    files: dict[str, tuple[bytes, int]],
    links: dict[str, str],
    ssid: str,
) -> dict:
    """Return the deterministic owner-Wi-Fi overlay fragment."""
    return {
        "format": 1,
        "fragment": True,
        "module": "owner-wifi",
        "version": _VERSION,
        "transport": "wifi-access-point",
        "ssid": ssid,
        "interface": _INTERFACE,
        "frequency_mhz": 2412,
        "security": "WPA2-PSK-CCMP",
        "ssh_address": "10.43.0.1:22",
        "client_address": "10.43.0.2/24",
        "authentication": ["publickey", "password"],
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
        "channels": {
            "wifi_ap": {
                "interface": _INTERFACE,
                "address": "10.43.0.1/24",
                "ssid": ssid,
                "socket": "10.43.0.1:22",
            },
            "wired_ethernet": {
                "interface": "ownerusb0",
                "address": "10.42.0.1/24",
                "ownership": "separate independently booted service",
            },
        },
        "limitations": [
            "Broadcom AP-mode startup, regulatory behavior, and sustained radio stability require head-unit verification.",
            "The client must statically configure 10.43.0.2/24; this overlay provides no DHCP service.",
            "The shared owner key, host key, password hash, and password-enabled Dropbear build must be merged from the USB-Ethernet module.",
            "A pre-existing wpa_supplicant or non-managed wlan0 interface makes this service fail without changing radio ownership.",
            "Removing the staged vendor-suppression marker and rebooting restores the OEM service condition; supplicantmanager is not globally masked.",
            "Archive every overlay member as root:root; host staging ownership is not target ownership.",
        ],
        "excluded": [
            "Radxa CDC-ECM and USB gadget transport",
            "NAT, IP forwarding, bridging, and DHCP",
            "global OEM account, passwd, shell, or ConnMan replacement",
            "vehicle-control code and hardware action",
        ],
    }


def ioniq5_owner_wifi_generate(*, output: Path, passphrase_file: Path,
                               connman_config: Path | None = None,
                               ssid: str = "IONIQ5-Owner") -> dict:
    """Validate inputs and stage the independent Wi-Fi overlay fragment.

    The output parent must exist. The output and sibling manifest paths must
    both be absent. Secrets are derived into the WPA config and never included
    in output metadata. Target packaging must apply the manifest ownership.
    """
    normalized_ssid = _ssid(ssid)
    passphrase = _wifi_passphrase(
        _read_regular(Path(passphrase_file), 256)
    )
    existing_config = (
        _read_regular(Path(connman_config), 1024 * 1024)
        if connman_config else None
    )
    config = _connman_config(existing_config)
    wpa_config = _wpa_config(normalized_ssid, passphrase)

    output = Path(output)
    if ".." in output.parts or output.name in ("", ".", ".."):
        raise ValueError("unsafe output path")
    output = output.parent.resolve(strict=True) / output.name
    manifest_path = output.with_name(output.name + ".manifest.json")
    if os.path.lexists(output) or os.path.lexists(manifest_path):
        raise ValueError("output or sibling manifest already exists")

    startup = (
        _STARTUP_TEMPLATE
        .replace("@PASSWORD_HASH_ERE@", _SHA512_CRYPT_ERE)
        .replace("@VERSION@", _VERSION)
        .encode("ascii")
    )
    unit = _UNIT.replace("@VERSION@", _VERSION).encode("ascii")
    vendor_dropin = _VENDOR_DROPIN_CONTENT.replace(
        "@VENDOR_MARKER@", "/" + _VENDOR_MARKER
    ).encode("ascii")
    files = {
        _STARTUP: (startup, 0o755),
        _WPA_CONFIG: (wpa_config, 0o600),
        _VENDOR_MARKER: (b"", 0o644),
        _UNIT_FILE: (unit, 0o644),
        _VENDOR_DROPIN: (vendor_dropin, 0o644),
        _CONNMAN_CONFIG: (config, 0o644),
        _MODULES_LOAD: (b"cfg80211\nbcmdhd\n", 0o644),
    }
    links = {
        f"etc/systemd/system/multi-user.target.wants/{_SERVICE}":
            f"../{_SERVICE}",
    }
    manifest = _manifest(files, links, normalized_ssid)

    staging = Path(tempfile.mkdtemp(prefix=".ioniq5-owner-wifi-", dir=output.parent))
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


def ioniq5_owner_wifi_main(argv: list[str] | None = None) -> int:
    """Generate the independent Wi-Fi AP overlay from explicit inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--passphrase-file", type=Path, required=True)
    parser.add_argument("--connman-config", type=Path)
    parser.add_argument("--ssid", default="IONIQ5-Owner")
    args = parser.parse_args(argv)
    try:
        manifest = ioniq5_owner_wifi_generate(
            output=args.output,
            passphrase_file=args.passphrase_file,
            connman_config=args.connman_config,
            ssid=args.ssid,
        )
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, f"overlay rejected: {exc}\n")
    print(
        f"Created Wi-Fi overlay: {args.output} "
        f"ssid={manifest['ssid']} address={manifest['ssh_address']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(ioniq5_owner_wifi_main())
