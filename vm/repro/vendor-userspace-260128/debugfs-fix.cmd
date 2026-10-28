rm /bin/busybox
write work/vm/busybox /bin/busybox
sif /bin/busybox mode 0100755
rm /init
write work/vm/vendor-userspace-260128/init.fixed /init
sif /init mode 0100755
