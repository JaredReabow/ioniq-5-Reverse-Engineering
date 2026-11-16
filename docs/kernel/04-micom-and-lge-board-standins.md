# The `micom` parameter stand-in (and the `lge_board` gap it does not cover)

Date: 2026-11-06. Rebuilding from the stock tarball drops the vendor's `micom` and `lge_board` drivers
(their source is not in `linux-4.1.27`). This documents what each absence does to the authentic boot,
and the projection-only `micom` stand-in added to `work/vm/kbuild/micom.c`.

## Why `micom` is load-bearing

The vendor's own `/lib/systemd/esinit` gates the entire display stack on one module parameter:

```sh
touch /tmp/spi_validation_NOK                      # esinit line 25
if [ -f /sys/module/micom/parameters/spi_validation ]; then
    while true; do
        spi_validation="$(cat /sys/module/micom/parameters/spi_validation)"
        if [ "$spi_validation" = "1" ]; then … rm /tmp/spi_validation_NOK; break; fi
        …
    done
fi
…
if [ -e /tmp/spi_validation_NOK ]; then echo "SPI NOK" > kmsg &
else (/usr/bin/weston --tty=1; touch /tmp/weston.crash) > /dev/kmsg 2>&1 & fi
```

Without the micom driver there is no `/sys/module/micom/parameters/spi_validation`, so `NOK` is never
removed and **weston is never started**. Measured on the first authentic boot of the stock kernel:
`100` occurrences of
`/init-authentic-hmi.sh: line 20: /sys/module/micom/parameters/spi_validation: No such file or directory`,
plus the unguarded reads `cat: /sys/module/micom/parameters/car_type: No such file or directory` (and
`optNSport`, `product_id`, `optUNECE`).

## The stand-in

`work/vm/kbuild/micom.c` is a trivial built-in driver whose `KBUILD_MODNAME` is `micom`, so its
`module_param` entries appear under exactly the path esinit reads. The only parameter that matters is
`spi_validation`, which defaults to **1** (open); the rest (`oem_type=1` KMC, `lcd_type=3` → 1920,
`car_type`, `optNSport`, `product_id`, `optUNECE`, …) are provided so the unguarded reads stop
erroring. It registers no device and does nothing but print:

```
micom: projection stand-in (spi_validation=1 lcd_type=3 oem_type=1)
```

It is wired in with a one-line `obj-y += micom.o` in `drivers/misc/Makefile` (in `kernel.patch`). It is a
**projection-only stand-in for the MICOM SPI handshake**, the same role as the existing
`/init-authentic-hmi.sh` write-loop — the difference is that this stand-in creates the parameter file the
loop was previously writing into, instead of assuming the vendor driver created it. No vendor binary is
modified; `esinit` itself is untouched.

With it in place, the authentic path proceeds: SPI gate open → weston starts → `[apps-check]
WAYLAND_SOCKET_UP` and a PNG capture.

## What the stand-in does *not* restore, stated rather than discovered

- **`can0` is gone.** The real micom driver is also the CAN bus interface
  (`CONFIG_LGE_EXTENDED_CAN_ID`, `CONFIG_LGE_MULTIPLE_CAN_INTERFACE`). The stand-in provides the
  *parameter* that opens the SPI gate; it does not provide a CAN device. The widget-value work
  (Battery/Range from `can0` frames) is therefore not served by this kernel.
- **The `lge_board` module is still absent.** esinit's FDE script
  `/etc/fsck_rw_partitions_v2_fde.sh` reads `/sys/module/lge_board/parameters/lge_mnt_st`, which a
  vendor ext4 patch sets during mount. Without it the script mis-branches and reformats `p9`/`p10`
  (`[eMMC] Filesystem(/dev/mmcblk0p9) fsck recover failed ... force recoverstart[12]`). This is benign
  only because the guest disk is `snapshot=on`; a plain parameter stand-in would *not* fix it, because
  `lge_mnt_st` must track the *mount result*, not a constant. That is a documented gap, not a fixed one.
- **`CONFIG_KEYSTORE*`, `CONFIG_SECURE_BOOT`, `CONFIG_RPMB`, `CONFIG_ABL_*`** remain absent; the boot
  proceeds without them in this projection.

## Files

- `work/vm/kbuild/micom.c` — the stand-in source.
- `work/vm/kbuild/kernel.patch` — the `drivers/misc/Makefile` line that compiles it in.
