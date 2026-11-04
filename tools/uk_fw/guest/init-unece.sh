#!/bin/sh
# projection-only: force the UNECE parameter to 1 (the "enforcing" branch of smack_setup.sh)
# in addition to the SPI gate, so the SMACK probe runs against an enforcing policy.
mount -t proc proc /proc 2>/dev/null
mount -t sysfs sysfs /sys 2>/dev/null
P=/sys/module/micom/parameters/spi_validation
U=/sys/module/micom/parameters/optUNECE
i=0; while [ $i -lt 50 ]; do [ -e "$P" ] && break; /bin/busybox sleep 0.1 2>/dev/null || sleep 1; i=$((i+1)); done
if [ -e "$P" ]; then
  echo 1 > "$P" 2>/dev/null
  [ -e "$U" ] && echo 1 > "$U" 2>/dev/null
  ( j=0; while [ $j -lt 100 ]; do echo 1 > "$P" 2>/dev/null; [ -e "$U" ] && echo 1 > "$U" 2>/dev/null; /bin/busybox sleep 0.1 2>/dev/null || sleep 1; j=$((j+1)); done ) &
fi
exec /lib/systemd/esinit
