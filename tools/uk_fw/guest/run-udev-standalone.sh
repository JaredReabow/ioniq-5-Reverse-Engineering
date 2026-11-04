#!/bin/sh
# Start the vendor's systemd-udevd without systemd, so USB hotplug can be observed.
#
# Why this exists: /lib/systemd/esinit never reaches systemd on a single-partition
# clone (it stops at "[FDE] use fstab for non FDE" after recovering eMMC p8-p12),
# so udev has to be started by hand. One trap: /run/udev/control must be created by
# udevd as a socket - pre-creating it as a directory makes udevd fail with
# "error binding udev control socket".
BB=/bin/busybox
M=/lib/modules/4.1.27-abl/kernel
for m in drivers/usb/common/usb-common.ko drivers/usb/core/usbcore.ko drivers/scsi/scsi_mod.ko \
         drivers/scsi/sd_mod.ko drivers/usb/host/uhci-hcd.ko drivers/usb/storage/usb-storage.ko; do
  [ -f "$M/$m" ] && insmod "$M/$m" 2>/dev/null
done
mkdir -p /run/udev/rules.d /run/udev/data /run/udev/links /etc/udev/rules.d
/lib/systemd/systemd-udevd --daemon --debug >/tmp/udevd.log 2>&1
$BB sleep 3
echo "UDEVD_PID=$($BB pidof systemd-udevd)"
/bin/udevadm trigger --action=add --subsystem-match=block 2>&1 | $BB head -2
/bin/udevadm settle --timeout=20 2>&1 | $BB head -2
$BB sleep 2
D=$($BB ls /dev/sd? 2>/dev/null | $BB head -1)
echo "DEV=${D:-none}"
[ -n "$D" ] && /bin/udevadm info --query=property --name=$D 2>&1 | $BB grep -E '^(ID_|DEVPATH|SUBSYSTEM)' | $BB head -12
echo DONE
