#!/usr/bin/env python3
"""
Test iAP2 socket admission inside the VM using the vm_boot.py infrastructure.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "uk_fw"))
import vm_boot as vb

WS = Path(__file__).resolve().parents[2] / "work/vm/vendor-userspace-260128"

# Script to run inside the VM
VM_SCRIPT = r"""
set -e
cd /workspace

echo "=== VM iAP2 Socket Admission Test ==="
echo "PWD: $(pwd)"
echo "User: $(id)"
echo ""

# Check kernel and SMACK
echo "=== Kernel ==="
uname -a
echo ""

echo "=== SMACK ==="
if [ -d /sys/fs/smackfs ]; then
    echo "SMACKFS mounted"
    cat /sys/fs/smackfs/load 2>/dev/null | head -20
else
    echo "SMACKFS NOT mounted"
fi
echo ""

echo "=== /tmp mount ==="
mount | grep " on /tmp " || echo "/tmp not a separate mount"
echo ""

echo "=== Current process label ==="
cat /proc/self/attr/current 2>/dev/null || echo "Cannot read"
echo ""

# Check for compiled probe
if [ -f ./iap2_socket_admission_probe ]; then
    echo "=== Running admission probe (no connect) ==="
    ./iap2_socket_admission_probe --json
    echo ""
    echo "=== Running admission probe (with connect) ==="
    ./iap2_socket_admission_probe --json --connect
else
    echo "Probe not compiled, compiling now..."
    gcc -Wall -Wextra -O2 -std=c11 -o iap2_socket_admission_probe iap2_socket_admission_probe.c -lcap 2>&1
    if [ $? -eq 0 ]; then
        echo "Compilation successful"
        echo "=== Running admission probe (no connect) ==="
        ./iap2_socket_admission_probe --json
        echo ""
        echo "=== Running admission probe (with connect) ==="
        ./iap2_socket_admission_probe --json --connect
    else
        echo "Compilation failed"
    fi
fi

echo ""
echo "=== Test complete ==="
"""

def main():
    print("Running iAP2 socket admission test in VM...")
    print("Workspace:", WS)
    
    # First check if the probe source is there
    probe_src = WS / "iap2_socket_admission_probe.c"
    if not probe_src.exists():
        print("ERROR: Probe source not found at", probe_src)
        return 1
    
    print("Probe source found, running VM test...")
    
    # Run the test in the VM with vendor userspace init
    rc = vb.run(
        WS,
        compat=True,
        command=VM_SCRIPT,
        timeout=120,
        init="/lib/systemd/esinit",
        memory_mib=1536,
    )
    
    return rc

if __name__ == "__main__":
    sys.exit(main())