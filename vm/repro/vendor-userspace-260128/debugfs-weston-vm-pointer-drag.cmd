rm /weston-vm-input.so
write work/vm/vendor-userspace-260128/weston-vm-input-build/weston-vm-input.so /weston-vm-input.so
sif /weston-vm-input.so mode 0100755
rm /hmi-input-probe.sh
write work/vm/vendor-userspace-260128/hmi-input-probe.sh /hmi-input-probe.sh
sif /hmi-input-probe.sh mode 0100755
