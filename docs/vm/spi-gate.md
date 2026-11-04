# Driving the MICOM SPI gate so esinit starts the vendor display server

`esinit` refuses to launch the vendor compositor while `/tmp/spi_validation_NOK` exists:

```sh
spi_validation="$(cat /sys/module/micom/parameters/spi_validation)"
if [ "$spi_validation" = "1" ]; then
        echo -e "[esinit] micom SPI info is OK\n" > /dev/kmsg
        touch /tmp/spi_validation_OK ; rm /tmp/spi_validation_NOK
...
if [ -e /tmp/spi_validation_NOK ]; then
        echo "SPI NOK" > kmsg &
else
        (/usr/bin/weston --tty=1; touch /tmp/weston.crash) > /dev/kmsg 2>&1 &
fi
```

In QEMU the real handshake never happens - `[lge_lcd_init_func] Micom didn't sent SPI data` - so the NOK branch is always taken and the
vendor display server is never started. Since `spi_validation` is a **module parameter**, it can be supplied on the kernel command line
before `esinit` runs, which is what `tools/uk_fw/vm_partimg/run-esinit-spi.py` does on top of the two changes already documented in
`docs/vm/partitioned-image.md` (vendor kernel hash, `root=` moved to the active-root partition).

## Result: the parameter is accepted, the gate did not visibly open

Measured on the partitioned image with `init=/lib/systemd/esinit`:

- the parameter is present on the command line, confirmed by splitting it:

  ```
  root=/dev/mmcblk0p5
  init=/lib/systemd/esinit
  micom.spi_validation=1
  ```

- the MICOM driver is present early enough to matter: `[0.409781] MICOM I> [micom_init] Registering LGE MICOM interface driver`, well
  before esinit reaches the parameter check;
- the boot still reaches `Multi-User System`, and `Weston Process Crash Monitoring` starts;
- **but there is no `[esinit] micom SPI info is OK` line, no `SPI NOK` line, and no weston output of any kind** in the serial log.

So the two candidate explanations remain open, and this note does not pick one:

1. `spi_validation` is a **read-only status** parameter, so the command-line assignment is accepted syntactically but the driver overwrites
   it during probe with its real (0) value before esinit reads it; or
2. the OK branch was taken and `/usr/bin/weston --tty=1` ran and died immediately, with its output not reaching the console through
   `/dev/kmsg` in this configuration.

Both are cheap to separate, and neither is settled here. **The gate mechanism is therefore not demonstrated**, and the next step is an
instrument rather than a guess: a logging wrapper in front of `/usr/bin/weston` (projection-only) that records its exit status and the
first lines of its stderr, plus reading `/sys/module/micom/parameters/spi_validation` from a userspace boot to see what the driver reports
after probe.

## Why this matters for the primary goal

This is the last piece standing between "the vendor userspace boots to multi-user" and "the vendor UI is running". Everything downstream of
it - `weston --tty=1`, the HMI services, `ApplicationLauncher` - is gated by this single value.
