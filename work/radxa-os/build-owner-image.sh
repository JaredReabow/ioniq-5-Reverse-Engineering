#!/bin/bash
# Build a verified, expanded Radxa Zero 3W image without writing physical media.
set -euo pipefail

repo=$(git rev-parse --show-toplevel)
source_image="$repo/work/radxa-os/radxa-zero3_bookworm_kde_b1.output_512.img"
output_image=${1:-"$repo/work/radxa-os/radxa-zero3-owner-update-v1.1.0.img"}
case "$output_image" in
    /*) ;;
    *) output_image="$repo/$output_image" ;;
esac
case "$output_image" in
    "$repo"/*) ;;
    *) printf 'Output must stay inside the repository work directory.\n' >&2; exit 2 ;;
esac

partial_image="$output_image.partial"
inner="$repo/work/radxa-os/customize-owner-image-inner.sh"
expected_source=f530b3081332811d63e8250cad744aa032ea7cfcd127897f43d7ae2e6eabb892
expected_baseline=3ddf02a9af81c8d95d06376e565f1998a646249519a201c3f5808ebc16fdb4ef
expected_custom=94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6
expected_plugin=e6013f44e8cb6c37c7b85670b8f2c4093ab1556d4e78997e207340bd62cff28a
expected_radxa_usb=03c897eb12f7cdb372e3eb0292766f944dd53c16888fe544dd18dd6ac313f284
expected_builder_manifest=d608c49edce0e3f42e3146dff457d8cdbc29e462981c05e44d06a2becdfbf1ff

hash_file() {
    shasum -a 256 "$1" | awk '{print $1}'
}

require_hash() {
    local path=$1
    local expected=$2
    local actual
    actual=$(hash_file "$path")
    if [[ "$actual" != "$expected" ]]; then
        printf 'Hash mismatch: %s\n' "$path" >&2
        exit 2
    fi
}

if [[ -e "$output_image" || -e "$partial_image" ]]; then
    printf 'Refusing to overwrite existing output: %s\n' "$output_image" >&2
    exit 2
fi

printf '[1/6] Verifying frozen source and payloads\n'
require_hash "$source_image" "$expected_source"
require_hash "$repo/work/radxa-toctou-build/ioniq5_eu_260128_baseline.img.dmg" "$expected_baseline"
require_hash "$repo/work/radxa-toctou-build/owner_access_v4.0.2_260128.te2" "$expected_custom"
require_hash "$repo/tools/uk_fw/nbdkit_dynamic_media.py" "$expected_plugin"
require_hash "$repo/tools/uk_fw/radxa_usb.py" "$expected_radxa_usb"
require_hash "$repo/work/radxa-toctou-build/owner_access_v4.0.2_260128.te2.manifest.json" "$expected_builder_manifest"

printf '[2/6] Creating isolated image copy\n'
cp -c "$source_image" "$partial_image"
truncate -s 60000000000 "$partial_image"

printf '[3/6] Extending GPT partition 3 while preserving its identity\n'
sgdisk -e "$partial_image" >/dev/null
sgdisk \
    --delete=3 \
    --new=3:679936:0 \
    --typecode=3:EF00 \
    --partition-guid=3:F3ADE4D7-EA80-4A15-A801-91CC51667B06 \
    --change-name=3:primary \
    --attributes=3:set:2 \
    "$partial_image" >/dev/null
sgdisk -v "$partial_image"

wifi_psk_fd=${RADXA_OWNER_WIFI_PSK_FD:-}
if [[ -n "$wifi_psk_fd" ]]; then
    if [[ ! "$wifi_psk_fd" =~ ^[3-9][0-9]*$ ]]; then
        printf 'RADXA_OWNER_WIFI_PSK_FD must name an open descriptor >= 3.\n' >&2
        exit 2
    fi
    if ! IFS= read -r -s wifi_psk <&"$wifi_psk_fd"; then
        printf 'Could not read the Wi-Fi PSK from descriptor %s.\n' "$wifi_psk_fd" >&2
        exit 2
    fi
else
    printf 'Wi-Fi PSK: ' >/dev/tty
    IFS= read -r -s wifi_psk </dev/tty
    printf '\n' >/dev/tty
fi
unset wifi_psk_fd RADXA_OWNER_WIFI_PSK_FD
if (( ${#wifi_psk} < 8 || ${#wifi_psk} > 63 )); then
    unset wifi_psk
    printf 'Wi-Fi PSK must contain 8 to 63 characters.\n' >&2
    exit 2
fi

printf '[4/6] Customizing the expanded root filesystem\n'
relative_partial=${partial_image#"$repo/"}
printf '%s\0' "$wifi_psk" | docker run --rm -i --privileged \
    -v "$repo:/workspace" \
    debian:bookworm-slim \
    bash /workspace/work/radxa-os/customize-owner-image-inner.sh \
    "/workspace/$relative_partial"
unset wifi_psk

printf '[5/6] Publishing completed image\n'
mv "$partial_image" "$output_image"
sync

printf '[6/6] Hashing completed image\n'
shasum -a 256 "$output_image" | tee "$output_image.sha256"
printf 'Built %s\n' "$output_image"
