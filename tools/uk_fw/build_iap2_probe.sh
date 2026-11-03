#!/bin/bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SRC_DIR/../.." && pwd)"

echo "Building iAP2 socket admission probe..."
cd "$SRC_DIR"

# Build the probe
gcc -Wall -Wextra -O2 -std=c11 \
    -o iap2_socket_admission_probe \
    iap2_socket_admission_probe.c \
    -lcap

echo "Built: $SRC_DIR/iap2_socket_admission_probe"

# Copy to vendor userspace for VM testing
VENDOR_US="$PROJECT_ROOT/work/vm/vendor-userspace-260128"
if [[ -d "$VENDOR_US" ]]; then
    cp iap2_socket_admission_probe "$VENDOR_US/"
    echo "Copied to: $VENDOR_US/iap2_socket_admission_probe"
fi

# Also copy to bootable workspace
BOOTABLE="$PROJECT_ROOT/work/vm/bootable"
if [[ -d "$BOOTABLE" ]]; then
    cp iap2_socket_admission_probe "$BOOTABLE/"
    echo "Copied to: $BOOTABLE/iap2_socket_admission_probe"
fi

echo "Done."