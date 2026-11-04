#!/bin/sh
# MICOM SPI stand-in for the projection (corrected).
#
# esinit starts the compositor only when it reads 1 from
#   /sys/module/micom/parameters/spi_validation
# and its guard is `if [ -f ... ]`, so the file must exist when esinit looks. The micom driver is
# built into the kernel (no micom.ko ships) and registers early, but a wrapper installed as `init`
# runs BEFORE esinit mounts sysfs - which is why the first version failed with
#   /init-esinit-spi.sh: line 15: /sys/module/micom/parameters/spi_validation: No such file or directory
# and the gate stayed shut (esinit took its "SPI NOK" branch). See CHANGELOG 4.41.0.
#
# So: mount the pseudo-filesystems first, then wait for the parameter to appear and hold it at 1
# across the window in which esinit polls (it polls up to 10 times, 0.3 s apart).
#
# Projection-only stand-in for hardware. Not part of the shipped system.

mount -t proc   proc   /proc 2>/dev/null
mount -t sysfs  sysfs  /sys  2>/dev/null

P=/sys/module/micom/parameters/spi_validation
i=0
while [ $i -lt 50 ]; do          # up to ~5 s for the driver's parameter to appear
    [ -e "$P" ] && break
    /bin/busybox sleep 0.1 2>/dev/null || sleep 1
    i=$((i+1))
done

if [ -e "$P" ]; then
    echo 1 > "$P" 2>/dev/null
    # keep it at 1 while esinit runs its poll, in case the driver re-writes it during probe
    ( j=0
      while [ $j -lt 100 ]; do
          echo 1 > "$P" 2>/dev/null
          /bin/busybox sleep 0.1 2>/dev/null || sleep 1
          j=$((j+1))
      done ) &
else
    echo "[spi-standin] parameter never appeared: $P" > /dev/kmsg 2>/dev/null
fi

exec /lib/systemd/esinit
