#!/bin/bash
# Install the read-only IONIQ dashboard and its desktop autostart entry.
set -euo pipefail

if [[ ${1:-} == --render-power-config ]]; then
    [[ $# == 2 ]] || exit 2
    /usr/bin/python3 - "$2" <<'PY'
import configparser, os, re
from pathlib import Path
import stat, sys, tempfile
path=Path(sys.argv[1])
if path.is_symlink():
    raise SystemExit('Refusing a symlinked desktop power configuration')
parser=configparser.ConfigParser(interpolation=None)
parser.optionxform=str
parser.SECTCRE=re.compile(r"^\[(?P<header>.+)\]$")
if path.exists():
    if not path.is_file() or path.stat().st_size > 131072:
        raise SystemExit('Unexpected desktop power configuration')
    parser.read(path)
for profile,icon in (('AC','battery-charging'),('Battery','battery-060'),('LowBattery','battery-low')):
    if not parser.has_section(profile):
        parser.add_section(profile)
        parser.set(profile,'icon',icon)
    for action in ('SuspendSession','DPMSControl','DimDisplay'):
        parser.remove_section(profile+']['+action)
fd,name=tempfile.mkstemp(prefix='.power-',dir=path.parent)
try:
    with os.fdopen(fd,'w') as stream:
        parser.write(stream)
        stream.flush(); os.fsync(stream.fileno())
    os.replace(name,path)
finally:
    if os.path.exists(name): os.unlink(name)
PY
    exit 0
fi

if [[ ${1:-} == --render-gdm-config ]]; then
    if (( $# != 3 )); then
        printf 'usage: %s --render-gdm-config <path> <desktop-user>\n' "$0" >&2
        exit 2
    fi
    /usr/bin/python3 - "$2" "$3" <<'PY'
import os
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
user = sys.argv[2]
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", user):
    raise SystemExit("invalid desktop user for GDM configuration")
source = path.read_text(encoding="utf-8")
lines = source.splitlines()

starts = [
    index for index, line in enumerate(lines)
    if re.fullmatch(r"\s*\[daemon\]\s*", line, re.IGNORECASE)
]
if len(starts) > 1:
    raise SystemExit("refusing duplicate [daemon] sections in GDM config")
if not starts:
    if lines and lines[-1].strip():
        lines.append("")
    lines.append("[daemon]")
    section_start = len(lines) - 1
else:
    section_start = starts[0]

section_end = len(lines)
for index in range(section_start + 1, len(lines)):
    if re.fullmatch(r"\s*\[[^]]+\]\s*", lines[index]):
        section_end = index
        break

replacements = {
    "automaticloginenable": "AutomaticLoginEnable=true",
    "automaticlogin": f"AutomaticLogin={user}",
}
seen: set[str] = set()
for index in range(section_start + 1, section_end):
    match = re.match(r"\s*([A-Za-z0-9_.-]+)\s*=", lines[index])
    if not match:
        continue
    key = match.group(1).lower()
    if key in replacements:
        lines[index] = replacements[key]
        seen.add(key)

missing = [value for key, value in replacements.items() if key not in seen]
if missing:
    lines[section_end:section_end] = missing

rendered = "\n".join(lines) + "\n"
temporary = path.with_name(path.name + ".dashboard-new")
if temporary.exists() or temporary.is_symlink():
    raise SystemExit(f"refusing existing temporary file: {temporary}")
temporary.write_text(rendered, encoding="utf-8")
os.chmod(temporary, path.stat().st_mode & 0o777)
os.replace(temporary, path)

check = path.read_text(encoding="utf-8")
for required in ("AutomaticLoginEnable=true", f"AutomaticLogin={user}"):
    if check.count(required) != 1:
        raise SystemExit(f"GDM verification failed for {required}")
PY
    exit 0
fi

usage() {
    printf 'usage: %s <desktop-user> [--no-start]\n' "$0" >&2
}

if (( $# < 1 || $# > 2 )); then
    usage
    exit 2
fi

desktop_user=$1
start_now=1
if (( $# == 2 )); then
    case "$2" in
        --no-start) start_now=0 ;;
        *) usage; exit 2 ;;
    esac
fi

if [[ $EUID -ne 0 ]]; then
    printf 'Run this installer as root (for example with sudo).\n' >&2
    exit 2
fi
if ! id "$desktop_user" >/dev/null 2>&1; then
    printf 'Desktop user does not exist: %s\n' "$desktop_user" >&2
    exit 2
fi
if [[ "$desktop_user" == root ]]; then
    printf 'Chromium must autostart as a non-root desktop user.\n' >&2
    exit 2
fi

desktop_home=$(getent passwd "$desktop_user" | cut -d: -f6)
desktop_group=$(id -gn "$desktop_user")
if [[ -z "$desktop_home" || ! -d "$desktop_home" ]]; then
    printf 'Desktop home directory is unavailable for %s.\n' "$desktop_user" >&2
    exit 2
fi
if [[ ! -x /usr/bin/python3 || ! -x /usr/bin/chromium ]]; then
    printf 'Required /usr/bin/python3 or /usr/bin/chromium is missing.\n' >&2
    exit 2
fi

script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
dashboard_source="$script_dir/radxa_dashboard.py"
web_ui_source="$script_dir/WEB_UI_radxa_dashboard.html"
for source in "$dashboard_source" "$web_ui_source"; do
    if [[ ! -f "$source" ]]; then
        printf 'Missing dashboard source: %s\n' "$source" >&2
        exit 2
    fi
done

install_root=/opt/ioniq5-update/dashboard
unit_path=/etc/systemd/system/ioniq5-radxa-dashboard.service
autostart_dir="$desktop_home/.config/autostart"
autostart_path="$autostart_dir/ioniq5-radxa-dashboard.desktop"
chromium_profile_dir="$desktop_home/.local/share/ioniq5-dashboard-browser"
gdm_config=/etc/gdm3/daemon.conf
dmrc_path="$desktop_home/.dmrc"
stamp=$(date -u +%Y%m%dT%H%M%SZ)-$$

backup_existing() {
    local path=$1
    if [[ -e "$path" || -L "$path" ]]; then
        local destination="$path.backup-$stamp"
        if [[ "$path" == "$autostart_path" ]]; then
            # KDE scans this directory beyond the final .desktop suffix.
            # Keep old launchers outside it so a backup cannot launch twice.
            local backups="$desktop_home/.local/share/ioniq5-dashboard-backups"
            install -d -m 0700 -o "$desktop_user" -g "$desktop_group" "$backups"
            destination="$backups/ioniq5-radxa-dashboard.desktop.backup-$stamp"
        fi
        cp -a -- "$path" "$destination"
        printf 'Preserved %s as %s\n' "$path" "$destination"
    fi
}

install -d -m 0755 "$install_root"
backup_existing "$install_root/radxa_dashboard.py"
backup_existing "$install_root/WEB_UI_radxa_dashboard.html"
install -m 0755 "$dashboard_source" "$install_root/radxa_dashboard.py"
install -m 0644 "$web_ui_source" "$install_root/WEB_UI_radxa_dashboard.html"
configuration_helper="$install_root/configure-dashboard"
backup_existing "$configuration_helper"
# The desktop account cannot traverse a root-private source staging folder.
# Run its config renderer from this installed, readable copy instead.
install -m 0755 "$0" "$configuration_helper"
backup_existing "$install_root/start-dashboard-browser"
cat >"$install_root/start-dashboard-browser" <<EOF
#!/bin/sh
# A dedicated dashboard session keeps visible update progress on its display.
if [ -x /usr/bin/xset ] && [ -n "\$DISPLAY" ]; then
    /usr/bin/xset dpms force on 2>/dev/null || :
    /usr/bin/xset s off -dpms 2>/dev/null || :
fi
exec /usr/bin/chromium --user-data-dir="$chromium_profile_dir" --kiosk --no-first-run --password-store=basic --disable-sync --noerrdialogs --disable-session-crashed-bubble --disable-features=TranslateUI --disable-restore-session-state http://127.0.0.1:8765
EOF
chmod 0755 "$install_root/start-dashboard-browser"

install -d -m 0755 /etc/systemd/system
backup_existing "$unit_path"
cat >"$unit_path.new" <<'EOF'
[Unit]
Description=IONIQ Radxa read-only progress dashboard
Documentation=file:/opt/ioniq5-update/dashboard/WEB_UI_radxa_dashboard.html

[Service]
Type=simple
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=/opt/ioniq5-update/tools/uk_fw
ExecStart=/usr/bin/python3 /opt/ioniq5-update/dashboard/radxa_dashboard.py
Restart=on-failure
RestartSec=1
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=read-only
ProtectControlGroups=yes
ProtectKernelModules=yes
ProtectKernelTunables=yes
RestrictRealtime=yes
LockPersonality=yes
# Read exact identities of the updater's root processes; filesystem and
# kernel write restrictions above remain in force.
CapabilityBoundingSet=CAP_SYS_PTRACE

[Install]
WantedBy=multi-user.target
EOF
chmod 0644 "$unit_path.new"
mv -f -- "$unit_path.new" "$unit_path"

install -d -m 0755 -o "$desktop_user" -g "$desktop_group" "$autostart_dir"
if [[ -L "$chromium_profile_dir" ]]; then
    printf 'Refusing symlinked Chromium profile path: %s\n' "$chromium_profile_dir" >&2
    exit 2
fi
install -d -m 0700 -o "$desktop_user" -g "$desktop_group" "$chromium_profile_dir"
backup_existing "$autostart_path"
cat >"$autostart_path.new" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=IONIQ 5 Update Dashboard
Comment=Read-only Radxa progress dashboard
Exec=/opt/ioniq5-update/dashboard/start-dashboard-browser
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=2
EOF
chown "$desktop_user:$desktop_group" "$autostart_path.new"
chmod 0644 "$autostart_path.new"
mv -f -- "$autostart_path.new" "$autostart_path"
if [[ -x /usr/bin/kwriteconfig5 ]]; then
    backup_existing "$desktop_home/.config/kscreenlockerrc"
    runuser -u "$desktop_user" -- /usr/bin/kwriteconfig5 \
        --file "$desktop_home/.config/kscreenlockerrc" --group Daemon \
        --key Autolock --type bool false
fi
power_config="$desktop_home/.config/powermanagementprofilesrc"
backup_existing "$power_config"
runuser -u "$desktop_user" -- "$configuration_helper" --render-power-config "$power_config"

systemctl daemon-reload
# A dedicated updater must remain awake during a long transfer, including when
# KDE starts its default power-management service after automatic login.
keepawake_unit=/etc/systemd/system/ioniq5-radxa-keepawake.service
backup_existing "$keepawake_unit"
cat >"$keepawake_unit" <<'EOF'
[Unit]
Description=Keep the Radxa updater awake
After=systemd-logind.service
Wants=systemd-logind.service

[Service]
Type=simple
ExecStart=/usr/bin/systemd-inhibit --what=sleep:idle --mode=block --who=IONIQ5-updater --why=Keep-update-media-and-progress-available /usr/bin/sleep infinity
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF
chmod 0644 "$keepawake_unit"
systemctl daemon-reload
systemctl enable --now ioniq5-radxa-keepawake.service
systemctl enable ioniq5-radxa-dashboard.service
if (( start_now )); then
    systemctl restart ioniq5-radxa-dashboard.service
fi

if [[ ! -f "$gdm_config" ]]; then
    printf 'GDM configuration is missing: %s\n' "$gdm_config" >&2
    exit 2
fi
backup_existing "$gdm_config"
"$configuration_helper" --render-gdm-config "$gdm_config" "$desktop_user"

backup_existing "$dmrc_path"
cat >"$dmrc_path.new" <<'EOF'
[Desktop]
Session=plasma
EOF
chown "$desktop_user:$desktop_group" "$dmrc_path.new"
chmod 0644 "$dmrc_path.new"
mv -f -- "$dmrc_path.new" "$dmrc_path"

printf 'Dashboard installed at http://127.0.0.1:8765 for %s.\n' "$desktop_user"
printf 'Chromium autostart: %s\n' "$autostart_path"
printf 'Dedicated Chromium profile preserved at %s; no browser was force-launched.\n' "$chromium_profile_dir"
printf 'GDM autologin configured for %s with session plasma; no display manager restart performed.\n' "$desktop_user"
printf 'No image hashing, preparation, USB arming, firmware flashing, or reboot was performed.\n'
