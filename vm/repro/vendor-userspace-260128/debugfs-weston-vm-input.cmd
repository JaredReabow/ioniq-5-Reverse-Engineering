write work/vm/vendor-userspace-260128/weston-vm-input-build/weston-vm-input.so /weston-vm-input.so
sif /weston-vm-input.so mode 0100755
rm /software-egl-probe.sh
write work/vm/vendor-userspace-260128/software-egl-probe.sh /software-egl-probe.sh
sif /software-egl-probe.sh mode 0100755
