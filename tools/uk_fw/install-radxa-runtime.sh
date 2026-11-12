#!/bin/bash
# Update the existing installation in place. This never rebuilds or writes an SD image.
set -euo pipefail
if [[ $EUID -ne 0 || $# -ne 1 ]]; then
    printf 'usage: sudo %s <desktop-user>\n' "$0" >&2
    exit 2
fi
source_dir=$(cd -- "$(dirname -- "$0")" && pwd -P)
base=/opt/ioniq5-update
service_state=$(systemctl show ioniq-update-media.service --property=ActiveState --value)
case "$service_state" in
    inactive|failed) ;;
    *) printf 'Preserving active controller (%s); stop the update before changing its runtime.\n' "$service_state" >&2; exit 2 ;;
esac
for name in radxa_usb.py radxa_update_media.sh radxa_dashboard.py WEB_UI_radxa_dashboard.html install-radxa-dashboard.sh; do
    [[ -f "$source_dir/$name" && ! -L "$source_dir/$name" ]] || {
        printf 'Missing runtime source: %s\n' "$name" >&2; exit 2;
    }
done
[[ -f "$base/config/serve-plan.json" ]] || {
    printf 'Existing prepared media configuration is missing.\n' >&2; exit 2;
}
python3 -m py_compile "$source_dir/radxa_usb.py" "$source_dir/radxa_dashboard.py"
bash -n "$source_dir/radxa_update_media.sh" "$source_dir/install-radxa-dashboard.sh"
backup="$base/runtime-backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"
install -d -m 0700 "$backup"
cp -a "$base/tools/uk_fw/radxa_usb.py" "$backup/radxa_usb.py"
cp -a /usr/local/sbin/ioniq-update-media "$backup/ioniq-update-media"
install -m 0644 "$source_dir/radxa_usb.py" "$base/tools/uk_fw/radxa_usb.py"
install -m 0755 "$source_dir/radxa_update_media.sh" /usr/local/sbin/ioniq-update-media
chmod 0755 "$source_dir/install-radxa-dashboard.sh"
bash "$source_dir/install-radxa-dashboard.sh" "$1"
printf 'Runtime 1.2.1 installed. Previous runtime retained at %s\n' "$backup"
printf 'Run ioniq-update-media prepare once after changing selected firmware. Later boots reuse it.\n'
printf 'No reboot, firmware arming, SD image write or vehicle update was performed.\n'
