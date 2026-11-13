#!/bin/bash
# Linux-only inner stage for build-owner-image.sh. The Wi-Fi PSK arrives on stdin.
set -euo pipefail

owner_image_version=1.1.1

# BEGIN RADXA_OWNER_FIRST_BOOT_PATCH
radxa_owner_patch_first_boot_config() {
    # Radxa's first-boot recipe disables ssh whenever an HDMI display is
    # attached, even if the image enabled ssh beforehand.  Preserve the
    # vendor's stop/regenerate/start ordering for host keys, but make the final
    # post-regeneration enable unconditional.
    local config=${1:?first-boot config path required}
    local disable_count conditional_count regenerate_count
    local disable_line conditional_line regenerate_line
    local temporary

    if [[ ! -f "$config" || -L "$config" ]]; then
        printf 'Missing regular Radxa first-boot config: %s\n' "$config" >&2
        return 2
    fi
    disable_count=$(grep -c '^disable_service ssh$' "$config" || true)
    conditional_count=$(grep -c '^if headless enable_service ssh$' "$config" || true)
    regenerate_count=$(grep -c '^regenerate_ssh_hostkey$' "$config" || true)
    if [[ "$disable_count" != 1 || "$conditional_count" != 1 || "$regenerate_count" != 1 ]]; then
        printf 'Unexpected Radxa SSH first-boot recipe in %s\n' "$config" >&2
        return 2
    fi

    disable_line=$(grep -n '^disable_service ssh$' "$config" | cut -d: -f1)
    regenerate_line=$(grep -n '^regenerate_ssh_hostkey$' "$config" | cut -d: -f1)
    conditional_line=$(grep -n '^if headless enable_service ssh$' "$config" | cut -d: -f1)
    if (( disable_line >= regenerate_line || regenerate_line >= conditional_line )); then
        printf 'Unexpected Radxa SSH first-boot ordering in %s\n' "$config" >&2
        return 2
    fi

    temporary="${config}.radxa-owner.tmp"
    if [[ -e "$temporary" || -L "$temporary" ]]; then
        printf 'Refusing existing first-boot patch temporary: %s\n' "$temporary" >&2
        return 2
    fi
    cp -p -- "$config" "$temporary"
    if ! sed \
        -e 's/^if headless enable_service ssh$/enable_service ssh/' \
        "$config" >"$temporary"; then
        rm -f -- "$temporary"
        return 2
    fi
    mv -f -- "$temporary" "$config"

    if grep -qxF 'if headless enable_service ssh' "$config" \
        || [[ $(grep -c '^disable_service ssh$' "$config" || true) != 1 ]] \
        || [[ $(grep -c '^enable_service ssh$' "$config" || true) != 1 ]]; then
        printf 'Failed to make Radxa SSH first-boot enablement unconditional\n' >&2
        return 2
    fi
}
# END RADXA_OWNER_FIRST_BOOT_PATCH

image=${1:?image path required}
IFS= read -r -d '' wifi_psk
if (( ${#wifi_psk} < 8 || ${#wifi_psk} > 63 )); then
    unset wifi_psk
    printf 'Invalid Wi-Fi PSK length.\n' >&2
    exit 2
fi

rootfs=/mnt/radxa-owner-root
partition_start=679936
partition_end=117187466
offset=$((partition_start * 512))
size=$(((partition_end - partition_start + 1) * 512))
loopdev=
mounted=0
binds=()

cleanup() {
    local index
    for (( index=${#binds[@]}-1; index>=0; index-- )); do
        umount -R "${binds[$index]}" 2>/dev/null || true
    done
    if (( mounted )); then
        umount "$rootfs" 2>/dev/null || true
    fi
    if [[ -n "$loopdev" ]]; then
        losetup -d "$loopdev" 2>/dev/null || true
    fi
    unset wifi_psk
}
trap cleanup EXIT INT TERM

mkdir -p "$rootfs"
loopdev=$(losetup --find --show --offset "$offset" --sizelimit "$size" "$image")

printf '  - checking and expanding ext4\n'
e2fsck -f -y "$loopdev"
resize2fs "$loopdev"
mount "$loopdev" "$rootfs"
mounted=1

printf '  - preparing chroot and installing NBD packages\n'
for mountpoint in dev proc sys; do
    mkdir -p "$rootfs/$mountpoint"
done
mount --rbind /dev "$rootfs/dev"
mount --make-rslave "$rootfs/dev"
binds+=("$rootfs/dev")
mount -t proc proc "$rootfs/proc"
binds+=("$rootfs/proc")
mount -t sysfs sysfs "$rootfs/sys"
binds+=("$rootfs/sys")

resolv_kind=absent
resolv_target=
if [[ -L "$rootfs/etc/resolv.conf" ]]; then
    resolv_kind=symlink
    resolv_target=$(readlink "$rootfs/etc/resolv.conf")
elif [[ -e "$rootfs/etc/resolv.conf" ]]; then
    resolv_kind=file
    cp -a "$rootfs/etc/resolv.conf" "$rootfs/etc/resolv.conf.radxa-build-save"
fi
rm -f "$rootfs/etc/resolv.conf"
cp /etc/resolv.conf "$rootfs/etc/resolv.conf"

policy="$rootfs/usr/sbin/policy-rc.d"
policy_saved=0
if [[ -e "$policy" ]]; then
    cp -a "$policy" "$policy.radxa-build-save"
    policy_saved=1
fi
printf '#!/bin/sh\nexit 101\n' >"$policy"
chmod 0755 "$policy"

base="$rootfs/opt/ioniq5-update"
install -d -m 0755 "$base/tools/uk_fw"
install -d -m 0700 "$base/helper-builds"
install -m 0755 /workspace/tools/uk_fw/build-nbdfuse-direct.sh "$base/tools/uk_fw/build-nbdfuse-direct.sh"
install -m 0644 /workspace/tools/uk_fw/ioniq-nbdfuse-direct.patch "$base/tools/uk_fw/ioniq-nbdfuse-direct.patch"
chroot "$rootfs" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get update
chroot "$rootfs" /usr/bin/env DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends nbd-client nbdkit nbdkit-plugin-python \
        fuse3 libfuse3-dev libnbd-dev build-essential pkg-config curl
# Build the pinned helper while the build's resolver is installed. Retain its
# source and license; the finished image never downloads or compiles at boot.
chroot "$rootfs" /bin/bash /opt/ioniq5-update/tools/uk_fw/build-nbdfuse-direct.sh \
    /opt/ioniq5-update/helper-builds/1.14.2-ioniq-direct.1
install -d -m 0755 "$rootfs/usr/local/libexec"
install -m 0755 "$base/helper-builds/1.14.2-ioniq-direct.1/ioniq-nbdfuse-direct" \
    "$rootfs/usr/local/libexec/ioniq-nbdfuse-direct"
chroot "$rootfs" apt-get clean
rm -rf "$rootfs/var/lib/apt/lists"/*

if (( policy_saved )); then
    mv "$policy.radxa-build-save" "$policy"
else
    rm -f "$policy"
fi
rm -f "$rootfs/etc/resolv.conf"
case "$resolv_kind" in
    symlink) ln -s "$resolv_target" "$rootfs/etc/resolv.conf" ;;
    file) mv "$rootfs/etc/resolv.conf.radxa-build-save" "$rootfs/etc/resolv.conf" ;;
esac

printf '  - making owner SSH survive Radxa first boot\n'
radxa_owner_patch_first_boot_config \
    "$rootfs/usr/share/doc/rsetup-config-first-boot/before.txt"
install -d -m 0755 "$rootfs/etc/systemd/system-preset"
cat >"$rootfs/etc/systemd/system-preset/00-ioniq-owner.preset" <<'EOF'
enable ssh.service
disable ioniq-update-media.service
EOF
chmod 0644 "$rootfs/etc/systemd/system-preset/00-ioniq-owner.preset"

printf '  - configuring key-only root SSH and unique host keys\n'
install -d -m 0700 "$rootfs/root/.ssh"
install -m 0600 \
    /workspace/work/radxa-toctou-build/private/ioniq5_owner_ed25519.pub \
    "$rootfs/root/.ssh/authorized_keys"
install -d -m 0755 "$rootfs/etc/ssh/sshd_config.d"
cat >"$rootfs/etc/ssh/sshd_config.d/90-radxa-owner.conf" <<'EOF'
# Owner access: public-key authentication only.
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PermitEmptyPasswords no
AuthenticationMethods publickey
EOF
chmod 0644 "$rootfs/etc/ssh/sshd_config.d/90-radxa-owner.conf"
rm -f "$rootfs"/etc/ssh/ssh_host_*
chroot "$rootfs" ssh-keygen -A
install -d -m 0755 "$rootfs/run/sshd"
chroot "$rootfs" sshd -t
ln -sfn /lib/systemd/system/ssh.service \
    "$rootfs/etc/systemd/system/multi-user.target.wants/ssh.service"

printf '  - installing private NetworkManager Wi-Fi profile\n'
install -d -m 0700 "$rootfs/etc/NetworkManager/system-connections"
wifi_uuid=$(cat /proc/sys/kernel/random/uuid)
wifi_profile="$rootfs/etc/NetworkManager/system-connections/juicy-interwebs.nmconnection"
{
    printf '[connection]\n'
    printf 'id=Juicy Interwebs\n'
    printf 'uuid=%s\n' "$wifi_uuid"
    printf 'type=wifi\n'
    printf 'autoconnect=true\n'
    printf 'autoconnect-priority=100\n\n'
    printf '[wifi]\n'
    printf 'mode=infrastructure\n'
    printf 'ssid=Juicy Interwebs\n\n'
    printf '[wifi-security]\n'
    printf 'key-mgmt=wpa-psk\n'
    printf 'psk=%s\n\n' "$wifi_psk"
    printf '[ipv4]\nmethod=auto\n\n'
    printf '[ipv6]\naddr-gen-mode=stable-privacy\nmethod=auto\n\n'
    printf '[proxy]\n'
} >"$wifi_profile"
chmod 0600 "$wifi_profile"
unset wifi_psk
ln -sfn /lib/systemd/system/NetworkManager.service \
    "$rootfs/etc/systemd/system/multi-user.target.wants/NetworkManager.service"
ln -sfn /lib/systemd/system/avahi-daemon.service \
    "$rootfs/etc/systemd/system/multi-user.target.wants/avahi-daemon.service"

printf 'radxa-ioniq\n' >"$rootfs/etc/hostname"
if grep -qE '^127\.0\.1\.1[[:space:]]' "$rootfs/etc/hosts"; then
    sed -i 's/^127\.0\.1\.1.*/127.0.1.1\tradxa-ioniq/' "$rootfs/etc/hosts"
else
    printf '127.0.1.1\tradxa-ioniq\n' >>"$rootfs/etc/hosts"
fi

printf '  - copying verified update media and controller\n'
base="$rootfs/opt/ioniq5-update"
install -d -m 0755 "$base/tools/uk_fw" "$base/tests" "$base/config" "$base/media"
install -m 0755 /workspace/tools/uk_fw/radxa_usb.py "$base/tools/uk_fw/radxa_usb.py"
install -m 0755 /workspace/tools/uk_fw/nbdkit_dynamic_media.py "$base/tools/uk_fw/nbdkit_dynamic_media.py"
install -m 0644 /workspace/tests/test_radxa_usb.py "$base/tests/test_radxa_usb.py"
install -m 0644 /workspace/tests/test_radxa_usb_fuse.py "$base/tests/test_radxa_usb_fuse.py"
install -m 0644 /workspace/tests/test_nbdkit_dynamic_media.py "$base/tests/test_nbdkit_dynamic_media.py"
cp --sparse=always \
    /workspace/work/radxa-toctou-build/ioniq5_eu_260128_baseline.img.dmg \
    "$base/media/ioniq5-eu-260128-baseline.img"
cp \
    /workspace/work/radxa-toctou-build/owner_access_v4.0.2_260128.te2 \
    "$base/media/owner_access_v4.0.2_260128.te2"
install -m 0644 \
    /workspace/work/radxa-toctou-build/owner_access_v4.0.2_260128.te2.manifest.json \
    "$base/config/owner_access_v4.0.2_260128.te2.manifest.json"

cat >"$base/config/regions.json" <<'EOF'
[
  {
    "off": 5668864,
    "len": 879126179,
    "evil": "/opt/ioniq5-update/media/owner_access_v4.0.2_260128.te2",
    "switch_after_pass": 2,
    "mode": "benign_then_evil"
  }
]
EOF
regions_hash=$(sha256sum "$base/config/regions.json" | awk '{print $1}')
regions_size=$(stat -c %s "$base/config/regions.json")
builder_size=$(stat -c %s "$base/config/owner_access_v4.0.2_260128.te2.manifest.json")

cat >"$base/config/serve-plan.json" <<EOF
{
  "baseline": {
    "path": "/opt/ioniq5-update/media/ioniq5-eu-260128-baseline.img",
    "sha256": "3ddf02a9af81c8d95d06376e565f1998a646249519a201c3f5808ebc16fdb4ef",
    "size": 30064771072
  },
  "plugin": {
    "path": "/opt/ioniq5-update/tools/uk_fw/nbdkit_dynamic_media.py",
    "sha256": "e6013f44e8cb6c37c7b85670b8f2c4093ab1556d4e78997e207340bd62cff28a",
    "size": 18006
  },
  "regions": {
    "path": "/opt/ioniq5-update/config/regions.json",
    "sha256": "$regions_hash",
    "size": $regions_size
  },
  "replacements": [
    {
      "builder_manifest": {
        "path": "/opt/ioniq5-update/config/owner_access_v4.0.2_260128.te2.manifest.json",
        "sha256": "d608c49edce0e3f42e3146dff457d8cdbc29e462981c05e44d06a2becdfbf1ff",
        "size": $builder_size
      },
      "length": 879126179,
      "mode": "benign_then_evil",
      "offset": 5668864,
      "path": "/opt/ioniq5-update/media/owner_access_v4.0.2_260128.te2",
      "sha256": "94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6",
      "size": 879126179,
      "switch_after_pass": 2
    }
  ],
  "schema": "ioniq-radxa-usb-serve-plan/v1"
}
EOF
chmod 0444 "$base/config/serve-plan.json" "$base/config/regions.json"
chmod 0444 "$base/media/ioniq5-eu-260128-baseline.img" \
    "$base/media/owner_access_v4.0.2_260128.te2"

# One implementation serves image creation and in-place upgrades. Power cycles
# reuse its prepared-content cache instead of rebuilding or rehashing media.
install -m 0755 /workspace/tools/uk_fw/radxa_update_media.sh \
    "$rootfs/usr/local/sbin/ioniq-update-media"

cat >"$rootfs/etc/systemd/system/ioniq-update-media.service" <<'EOF'
[Unit]
Description=IONIQ owner dynamic update media
After=local-fs.target
ConditionPathExists=/opt/ioniq5-update/config/serve-plan.json
ConditionPathExists=/run/ioniq5-update/manual-arm

[Service]
Type=notify
NotifyAccess=main
RuntimeDirectory=ioniq5-update
RuntimeDirectoryMode=0755
ExecStartPre=/usr/bin/rm -f /run/ioniq5-update/manual-arm
ExecStart=/usr/local/sbin/ioniq-update-media internal-arm
KillMode=mixed
Restart=no
TimeoutStartSec=infinity
TimeoutStopSec=5min

[Install]
WantedBy=multi-user.target
EOF
chmod 0644 "$rootfs/etc/systemd/system/ioniq-update-media.service"
install -d -m 0755 "$rootfs/etc/ioniq5-update"
rm -f \
    "$rootfs/etc/ioniq5-update/allow-auto-arm" \
    "$rootfs/run/ioniq5-update/manual-arm"

install -d -m 0755 "$rootfs/etc/issue.d"
printf 'IONIQ owner update-media image v%s\n\n' "$owner_image_version" \
    >"$rootfs/etc/issue.d/ioniq-owner.issue"
printf '%s\n' "$owner_image_version" >"$rootfs/etc/ioniq-owner-image-version"
chmod 0644 \
    "$rootfs/etc/issue.d/ioniq-owner.issue" \
    "$rootfs/etc/ioniq-owner-image-version"

cat >"$base/README.txt" <<'EOF'
IONIQ owner update-media image v1.1.1

SSH is key-only as root. The image joins its preconfigured Wi-Fi network and
announces the hostname radxa-ioniq.local through Avahi.

Run these as root:
  ioniq-update-media selftest
  ioniq-update-media verify
  ioniq-update-media inspect
  ioniq-update-media plan
  ioniq-update-media arm
  ioniq-update-media status
  ioniq-update-media teardown

The systemd unit is installed but manual arming is required. The arm command
creates a one-use authorization and waits for the direct-I/O FUSE USB backing
to become ready; boot never exposes USB. Firmware 4.0.2 is prepared once.
EOF
chmod 0444 "$base/README.txt"

printf '  - verifying copied content and installed configuration\n'
printf '%s  %s\n' \
    3ddf02a9af81c8d95d06376e565f1998a646249519a201c3f5808ebc16fdb4ef \
    "$base/media/ioniq5-eu-260128-baseline.img" | sha256sum -c -
printf '%s  %s\n' \
    94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6 \
    "$base/media/owner_access_v4.0.2_260128.te2" | sha256sum -c -
printf '%s  %s\n' \
    e6013f44e8cb6c37c7b85670b8f2c4093ab1556d4e78997e207340bd62cff28a \
    "$base/tools/uk_fw/nbdkit_dynamic_media.py" | sha256sum -c -
chroot "$rootfs" /bin/sh -n /usr/local/sbin/ioniq-update-media
chroot "$rootfs" /usr/local/sbin/ioniq-update-media selftest
chroot "$rootfs" /usr/local/sbin/ioniq-update-media verify
chroot "$rootfs" sshd -T -C user=root,host=radxa-ioniq,addr=127.0.0.1 \
    | grep -E '^(permitrootlogin|pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication|authenticationmethods) '
test "$(stat -c %a "$wifi_profile")" = 600
test "$(stat -c %a "$rootfs/root/.ssh/authorized_keys")" = 600
test ! -e "$rootfs/etc/systemd/system/multi-user.target.wants/ioniq-update-media.service"
test ! -e "$rootfs/etc/ioniq5-update/allow-auto-arm"
test ! -e "$rootfs/run/ioniq5-update/manual-arm"
grep -qxF 'enable ssh.service' \
    "$rootfs/etc/systemd/system-preset/00-ioniq-owner.preset"
grep -qxF 'disable ioniq-update-media.service' \
    "$rootfs/etc/systemd/system-preset/00-ioniq-owner.preset"
grep -qxF 'ConditionPathExists=/opt/ioniq5-update/config/serve-plan.json' \
    "$rootfs/etc/systemd/system/ioniq-update-media.service"
grep -qxF 'ConditionPathExists=/run/ioniq5-update/manual-arm' \
    "$rootfs/etc/systemd/system/ioniq-update-media.service"
grep -qxF 'Type=notify' "$rootfs/etc/systemd/system/ioniq-update-media.service"
grep -qxF 'NotifyAccess=main' "$rootfs/etc/systemd/system/ioniq-update-media.service"
grep -qxF 'KillMode=mixed' "$rootfs/etc/systemd/system/ioniq-update-media.service"
grep -qxF 'Restart=no' "$rootfs/etc/systemd/system/ioniq-update-media.service"
grep -qxF 'TimeoutStartSec=infinity' \
    "$rootfs/etc/systemd/system/ioniq-update-media.service"
! grep -q '^ExecStop=' "$rootfs/etc/systemd/system/ioniq-update-media.service"
! grep -qxF 'if headless enable_service ssh' \
    "$rootfs/usr/share/doc/rsetup-config-first-boot/before.txt"
test "$(grep -c '^disable_service ssh$' \
    "$rootfs/usr/share/doc/rsetup-config-first-boot/before.txt")" = 1
test "$(grep -c '^enable_service ssh$' \
    "$rootfs/usr/share/doc/rsetup-config-first-boot/before.txt")" = 1
test "$(cat "$rootfs/etc/ioniq-owner-image-version")" = "$owner_image_version"

sync
for (( index=${#binds[@]}-1; index>=0; index-- )); do
    umount -R "${binds[$index]}"
done
binds=()
umount "$rootfs"
mounted=0
e2fsck -f -n "$loopdev"
losetup -d "$loopdev"
loopdev=
printf '  - image filesystem verification passed\n'
