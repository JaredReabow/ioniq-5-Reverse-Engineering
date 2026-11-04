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

## Resolved: the parameter is writable, and the driver overwrites it

Measured on the partitioned image with `init=/init` (which allows commands), with the cmdline token still applied:

```
-rw-r--r-- 1 0 root 4096 Jan  1 00:00 /sys/module/micom/parameters/spi_validation
VALUE=0
AFTER_WRITE=1
```

Three facts, and together they close the question:

1. **It is writable** (`-rw-r--r--`), so it is not a read-only status field.
2. **It reads 0 despite `micom.spi_validation=1` on the command line**, so the assignment is either not applied or is overwritten during
   probe - and since the second explanation in this document was "weston started and died", that is now excluded as the *primary* cause:
   esinit never saw a 1.
3. **Writing 1 from userspace sticks** (`AFTER_WRITE=1`).

So the gate cannot be opened from the kernel command line, and cannot be opened from userspace either, because `esinit` **is** the first
userspace and its poll runs before any service exists to write the parameter. The only place to interpose is **between the kernel and
esinit** - a wrapper `init` that forces the value and then `exec`s esinit.

That wrapper is written: `tools/uk_fw/guest/init-esinit-spi.sh`. It forces the parameter to 1 for ten seconds in the background and then
execs `/lib/systemd/esinit`. It is a **projection-only stand-in for the MICOM handshake** and is labelled as such in the file; it is not
part of the shipped system and must never be described as though it were.

Installing it requires writing one file into the active-root partition `p5` of the 36 GiB image. That is 8 GiB out and 8 GiB back with
`debugfs`, and it was **not** done here: it is a slow operation for a fidelity improvement, because the vendor interface already runs in
the projection through the research-init chain (`/run-chain23.sh` plus `ivi-wm` placement), which is how the clean renders and the touch
proof were produced. The honest summary is that the SPI gate is **understood and drivable**, and driving it is optional work for making the
*systemd-managed* HMI faithful rather than for making the UI appear.

## Correction, and an unresolved point (2026-11-04, after CHANGELOG 4.41.0)

Two attempts were made to drive the gate from a wrapper `init`, and neither settles the question. The record of both, because the second one
undoes the certainty of the first correction:

1. **Wrapper without a sysfs mount — fails, provably.** As `init` it runs before `esinit` mounts `/sys`, so its write fails:
   `/init-esinit-spi.sh: line 15: /sys/module/micom/parameters/spi_validation: No such file or directory`. With the guard
   `if [ -f /sys/module/micom/parameters/spi_validation ]` false and `/tmp/spi_validation_NOK` already touched, `esinit` should take the
   `SPI NOK` branch.
2. **Wrapper that mounts `/sys` first — writes successfully, outcome still ambiguous.** The wrapper's own error disappears, so the parameter
   existed and its write landed. But neither run produced the decision lines (`[esinit] micom SPI info is OK` / `SPI NOK`), because those go
   through `/dev/kmsg`, which is not reliably present at that point in boot. Both the broken and the fixed run contain
   `random: weston urandom read` at ~6.5 s, and **no unit in the image starts weston** — so that line cannot by itself distinguish the branches,
   which is precisely the mistake made in 4.34.0.

A first attempt to log the parameter's **early** value from the wrapper also failed to produce output (writing to `/dev/console` produced
nothing, with or without a `devtmpfs` mount), so the most useful quantity — what the parameter reads *before* `esinit` looks — is still
unmeasured.

### The two candidate explanations, both consistent with the evidence

- **The parameter's initial value is 1**, and the driver writes 0 later when the handshake fails. Then `esinit` always takes the OK branch, the
  wrapper is unnecessary, and the correct statement is that the gate is open by default during boot - which would make 4.34.0 accidentally right
  and 4.41.0's correction wrong.
- **The parameter is created with value 0 and the OK branch is never taken**, in which case the wrapper must be installed *and* must mount
  `/sys`, which the corrected script now does - but the branch it produces has not been observed.

### The measurement that decides it

Read `/sys/module/micom/parameters/spi_validation` at the earliest possible moment and get the answer somewhere visible. The clean way is a
guest script that runs under `init=/init` (which allows commands) and prints the value immediately, before anything writes it; a timestamped
`/tmp/spi_validation_OK` check afterwards then says which branch `esinit` took. Until that is done, this document does not claim the gate opens.

**Why this is written down rather than resolved by assertion:** 4.34.0 asserted it, and was wrong; 4.41.0 corrected it to "never opened", and that
is not established either. The honest state is one unmeasured value.

## Why none of the diagnostics ever appeared: `> kmsg` is not `/dev/kmsg`

Three entries of this investigation were ambiguous because the branch could not be observed. The reason is a one-word bug in the shipped script:

```sh
if [ -e /tmp/spi_validation_NOK ]; then
        echo "SPI NOK" > kmsg &
else
        (/usr/bin/weston --tty=1; touch /tmp/weston.crash) > /dev/kmsg 2>&1 &
fi
```

`> kmsg` (no leading slash) writes a file called `kmsg` in the init's working directory. **The failure branch never reports anything.** The success
paths do it correctly (`> /dev/kmsg`), which is why the absence of `[esinit] micom SPI info is OK` looked meaningful and the absence of `SPI NOK`
looked like evidence of the other branch. It was evidence of nothing: that message cannot appear.

So the earlier readings - mine, twice - were drawing conclusions from a log line that the code never emits. On a production unit the same typo means a
technician whose display server did not start gets **no `SPI NOK` message in the kernel log to explain it**, which is a support problem independent of
the security work: the failure mode of the most important startup dependency is silently unreportable.

**What is still unmeasured is unchanged**: the value of `/sys/module/micom/parameters/spi_validation` at the instant `esinit` reads it. The difference
now is that the measurement must not rely on `/dev/kmsg` either - it must go to `/dev/console` or a file, from a script with `/dev` mounted, or be
taken from a boot where commands are possible.

## RESOLVED — measured on both sides, with the instrument placed after the decision

The fix for the broken diagnostics was to stop using `/dev/kmsg` and instead append one line to `/etc/install_westonPngLogo.sh`, which
`esinit` calls **after** its SPI block and **before** it chooses between the `SPI NOK` branch and launching weston. The line writes to
`/dev/ttyS0`:

```sh
echo "SPI_STATE ok=$([ -e /tmp/spi_validation_OK ] && echo yes || echo no) \
     nok=$([ -e /tmp/spi_validation_NOK ] && echo yes || echo no) \
     param=$(cat /sys/module/micom/parameters/spi_validation 2>/dev/null)" > /dev/ttyS0
```

Two boots, same image, same instrument, one difference - whether the corrected wrapper `init` ran first:

| boot | measurement | meaning |
| --- | --- | --- |
| `init=/lib/systemd/esinit` | `SPI_STATE ok=no nok=yes param=0` | gate **shut**; `esinit` takes the `SPI NOK` branch and does not start the compositor |
| `init=/init-esinit-spi.sh` | `SPI_STATE ok=yes nok=no param=1` | gate **open**; the stand-in worked, `OK` present, `NOK` removed, parameter reads 1 |

So, finally, on the record:

- **The gate is shut by default.** The parameter reads **0** at the decision point, not 1. Entry 4.34.0's claim that the gate opened by itself was
  wrong, and 4.41.0's correction was right.
- **The corrected wrapper does open it.** `tools/uk_fw/guest/init-esinit-spi.sh` mounts `/sys` (the original failed because an `init` runs before
  `esinit` mounts it), waits for the parameter, forces it to 1 and holds it across the poll window. Measured, not argued.
- **`esinit` then launches `/usr/bin/weston --tty=1`**, which is why `random: weston urandom read` appears in both the shut and open cases: some
  other path invokes the binary even when the gate is shut. That still has no identified source, and it was never evidence of anything.

### The remaining blocker is now unambiguous

With the gate open, boot stalls at `Timers`/`System Initialization` instead of reaching Multi-User. The cause is the compositor itself:
`weston --tty=1` asks for a DRM device the projection does not provide, so it blocks and takes the boot with it. That is exactly the substitution the
worker on `work/vm/stockhmi` is making - a headless/software backend in the `[core]` section of the ini that `esinit`'s own weston will read.
