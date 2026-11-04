#!/bin/sh
# MICOM SPI stand-in for the projection.
#
# The vendor MICOM driver only reports spi_validation=1 when the real MICOM answers over the platform
# bus; under QEMU nothing answers, so the driver leaves it at 0 (measured: writable -rw-r--r--, value 0
# even when `micom.spi_validation=1` is passed on the kernel command line, because probe overwrites it).
# esinit's gate is a three-second poll of that file at boot, before any userspace service exists to
# write it, so the only place to stand in for the handshake is between the kernel and esinit.
#
# This wrapper forces the parameter to 1 in a background loop for the first ten seconds and then hands
# control to the authentic init. It is a projection-only adaptor standing in for hardware; it is NOT
# part of the shipped system and must never be described as such.
( i=0
  while [ $i -lt 100 ]; do
    echo 1 > /sys/module/micom/parameters/spi_validation 2>/dev/null
    /bin/busybox sleep 0.1 2>/dev/null || sleep 1
    i=$((i+1))
  done ) &
exec /lib/systemd/esinit
