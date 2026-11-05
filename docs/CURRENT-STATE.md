# Current state — what works, what is blocked, what to do next

Written after a long working session so the next person (or the next turn) starts from measured facts rather than a story. Everything below is
either demonstrated in the projection, quoted from the image, or explicitly marked as unmeasured.

---

> **Before trusting anything below**, run `sh tools/check_all.sh`. It verifies the register's numbering and cross-references, that the history log has not been rewritten, and that
> every document reference resolves. The suite exists because three defects survived careful reading.

## 1. The interactive VM: working

| Capability | State | Where it is shown |
| --- | --- | --- |
| Vendor kernel boots | **works** | `boot/bzImage-4.1.27-abl`, `4.1.27-abl #1 SMP Wed Jan 28 16:00:10 KST 2026` |
| Vehicle's own `esinit` runs to Multi-User | **works** | `docs/vm/partitioned-image.md` — local-fs 14.1 s, basic 18.3 s, multi-user 75.9 s |
| Real `systemd-udevd` | **works** | shipped `60-persistent-storage.rules` produce `ID_SERIAL=…` on a plugged USB stick |
| USB hotplug | **works** | `/dev/sda` enumerates, mounts, `scsi_id` reads the serial |
| Authentic compositor renders | **works** | clean frames, no stripes, `docs/vm/25-…`, `docs/vm/31-…` |
| **Touch reaches the app** | **works** | `QWaylandInputDevice::Touch::touch_down/touch_up` in the app's own log, `evidence/vm-bringup/interactive-touch-2026-11-04.log` |
| Engineering mode launches as root | **works** | `appId 301` from `/tmp/app/bin`, uid 0, `getEnterPasswordCnt()` live |
| Engineering mode's *page body* renders | **no — cause now known** | the app **never attaches a buffer**: its whole Wayland trace over 70 s is four `wl_display.delete_id` calls, because it waits for `show_window_fg` from the app manager, which this projection never sends. See `docs/engineering-mode/engineering-paint.md` |
| Vendor compositor started by `esinit`, and it renders | **works** | `docs/vm/authentic-hmi.md` — Multi-User at 97.3 s with `weston.real` alive, 129,844-byte PNG capture, `ivi_wm` placement |
| Vendor HMI processes under the vendor init | **works** | `docs/vm/authentic-hmi-apps.md` — a `com.lge.car.micom` stand-in lets `ApplicationLauncher` start `ApplicationManager` and `AppHomeScreen`; a click reaches a real compositor client |
| Touch on the **vendor** boot path | ✅ a click reaches a real client, `pid=797 uid=0` |
| Applications present a frame | **yes — managed and by hand** | with the software-GL **driver path** restored, `AppHomeScreen` registers, answers introspection and paints a 120,556-byte frame (`docs/vm/authentic-hmi-apps.md` §9). The managed instance paints the vendor interface with its KIA logo (`docs/vm/32-managed-home-screen-kia-logo-authentic-2026-11-05.png`) |

How to drive it: `python3.13 tools/uk_fw/vm_console.py`, then `sh /run-chain23.sh &` and `sh /run-live.sh`. Full instructions:
`docs/VM-RUNBOOK.md`.

## 1b. Why the engineering window stays black — answered

`strace` on the app's stderr (the launcher discards it, but `write(2)` still happens) shows **624 bytes, 12 writes, all of them object-id teardown**:
no `create_surface`, no `attach`, no `commit`, no `damage`. The app never presents a frame because **the app manager is supposed to show the window, not
the app**:

```
<interface name="com.lge.avn.appmanager.appbase">
  <method name="show_window_fg"> reason, plane, avmode, command -> response_plan
```

The app registers itself with `com.lge.avn.appmanager.registration.registration(appid, appname, servicename, objectpath, plane)` and then waits. In this
projection the chain runs `AppLauncher` but not the real `ApplicationManager`, so **nobody calls `show_window_fg`** and the `QWindow` never shows.

Measured on the session bus during a launch: every registration is addressed to **`com.lge.hyundai.avn.appmanager`**, which **nothing owns** - so the
registration is a no-reply call into the void, and the app is never told to show.

Running the real manager is not enough on its own. `docs/engineering-mode/appmanager-micom-replies.md` names what is left: answering the manager's MICOM calls **worked**
(`reply is not VALID` is now zero across a run), and the window still does not paint, for two compounding reasons.

1. The `show_engineermode` trigger lives on the manager's `com.lge.avn.appmanager.appbase` interface, which the manager **does not register** in this projection, so
   there is no D-Bus route to ask it to show engineering mode.
2. The manager's **app-alive watchdog** then removes the unshown app anyway: `AB010512*time*AppEngineerMode-5-hang`, `appTerminateSlot`, deregistration.

## 1c. The authentic HMI runs, paints, and takes clicks

The managed `AppHomeScreen` - launched by the vehicle's own `esinit` -> systemd -> `ApplicationLauncher` -> `ApplicationManager` - renders on the vendor compositor: **a title bar reading
`STR_CAMERA_ALERT2`, a left panel, and the vendor's own KIA logo** (`docs/vm/32-managed-home-screen-kia-logo-authentic-2026-11-05.png`, 120,561 bytes). A synthetic click reaches a real client at
`pid=797 uid=0`.

**What it does not render is the home screen's content** - no widgets, no icon row, nothing to navigate to. Two independent captures from different workers show the same frame
(`docs/vm/33b-…png`), so this is the application's steady state in the projection and not a timing artefact. The most probable cause is the state the application believes it is in: the home layout
is gated on MICOM power/ACC status, and our stand-in answers the D-Bus queries without driving the power state machine. That is the next thing to supply, and it is a data problem of the same kind as the
six services answered earlier - not a rendering problem.

Two things that mattered and are cheap to get wrong: **`--smp 4` is required** (at two vCPUs the managed app never registers its bus name), and **capture surfaces by identity, not recency** - the
background's surface is created last, so "newest" always returns the splash. Reference sizes: **129,844** background, **120,561** painted application.

## 1d. The engineering-mode gesture does not exist on this build

The About-screen tap that the field describes is **absent**, checked by enumeration rather than by search: three tap counters exist in the entire shipped QML tree and none is near About, and no
shipped binary - including `AppSetup`, which owns the settings screens - contains a gesture, signal or slot that starts engineering mode. Entering it needs an app-manager request for **app id 301**
from a **root** process on the session bus, or a developer path.

## Why the home layout does not appear, and the one call that should fix it (2026-11-05)

The application window paints - title bar, left panel, KIA logo - but the home screen's **content** never lays out. The application's own API says why.

**What the app asks:** `AppHomeEngine::askPowerStatus()`, and the answer comes not from MICOM but from the **application manager**:

```
com.lge.avn.appmanager.info
    method  ask_power_status        ()        -> int status
    method  ask_acc_status          ()        -> int status
    method  ask_ign_status          ()        -> int status
    method  set_power_on_status     (int on, int position)
    signal  power_status            (int status)
```

And the app has slots for exactly those: `slotPowerStatus(int)`, `slotAccStatusChanged()`, `slotIGNStatusChanged()`, plus `onIGNStatusChanged()` and `send_IgnStatus_to_Widget()`.

**So the chain is:** MICOM -> application manager -> `ask_power_status` -> the home layout. Our stand-in owns `com.lge.car.micom` and answers the app's own queries, but it never drives the **manager's** power state, so the manager reports the vehicle as off and the home screen presents its standby branding instead of its widgets.

**The fix is one call, and the API accepts it:**

```sh
dbus-send --session --print-reply --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.set_power_on_status int32:1 int32:0
```

`set_power_on_status(on, position)` is an **incoming** method on the manager's own `info` interface - something in the vehicle is meant to call it, and nothing in our projection does.

**Not yet demonstrated:** my own attempt ran into the harness it was sharing (the clone's own instrumentation completed the run before my probe fired), so the call has not been made and observed. The worker with the working harness has it. If the layout appears after that call, the last named gap in the VM closes; if it does not, the state it is waiting for is something else, and the manager's other `ask_acc_status` / `ask_ign_status` answers are the next thing to read.

## 2. The one blocker for init fidelity

`esinit` starts the compositor only when `/sys/module/micom/parameters/spi_validation` reads 1, and it touches
`/tmp/spi_validation_NOK` unconditionally first. Two attempts to force the value from a wrapper `init` failed to settle which branch runs:

- without mounting `/sys` the write fails (`No such file or directory`) — provable;
- with `/sys` mounted the write lands, but the decision lines go through `/dev/kmsg`, which is not reliably present, and the one log line that
  appears in both the broken and fixed runs (`random: weston urandom read`) cannot distinguish the branches because **no unit in the image
  starts weston**.

**Resolved.** Measured with a probe placed after the decision (`install_westonPngLogo.sh`, writing to `/dev/ttyS0` because the vendor's own failure
branch writes to a stray `kmsg` file):

```
init=/lib/systemd/esinit        SPI_STATE ok=no  nok=yes param=0   -> gate shut, SIP NOK branch, no compositor
init=/init-esinit-spi.sh        SPI_STATE ok=yes nok=no  param=1   -> gate open, stand-in works
```

So the parameter reads **0** at the decision point: the gate is shut by default, and `tools/uk_fw/guest/init-esinit-spi.sh` (which mounts `/sys` before
writing) opens it. With the gate open the boot now stalls at `Timers` because `weston --tty=1` blocks waiting for a DRM device — which is exactly the
backend substitution a worker is making in `work/vm/stockhmi`.

## 3. What is different from a vehicle — the three substitutions

1. **A software backend stands in for `ias-backend.so` and the hardware** (`headless-backend.so` / `ias-backend-soft.so`, `GALLIUM_DRIVER=softpipe`,
   `/opt/software-egl18`).
2. **The MICOM handshake is simulated** — and the simulation currently does not open the gate (§2).
3. **`lge_usb_adapter` is neutralised**, because it oopses on non-vendor hardware, holds the platform-bus lock and deadlocks `esinit` before
   systemd.

Everything else on the boot path is shipped software: kernel, `esinit`, eMMC recovery, fstab, unit set, udev rules, binaries.

## 4. Root access — the register

Seven relevant entries. **Two are demonstrated**, one is captured, three are confirmed from code/config, one is hardware-bounded.

| # | Finding | State |
| --- | --- | --- |
| V-048 | app manager verifies against `/tmp/app_normal.key` | **a binary we signed ran as uid 0** |
| V-049 | root console on ttyS2, gate open by default | **login prompt captured** |
| V-050 | WiFi: real hardware, three software gates | confirmed from modules/firmware/tooling |
| V-051 | manager executes any caller-named path | uid 0 confirmed; session bus is **root-only**, so persistence not escalation |
| V-052 | MAC switched to permissive by a LUKS probe | value measured 0 |
| V-053 | data/log encryption passphrase is `1234` | **opens with `1234`, refuses a wrong one** |
| V-054 | account database symlinked into `/tmp` | **mechanism demonstrated** — a `uid=0` account appended there resolves via NSS; latent only for want of a non-root writer |
| V-055 | compositor config is `/tmp/weston.ini`, names loadable modules | latent; effect waits for the next compositor start |
| V-042 | seven privileged behaviours key on a file existing in `/tmp` | wiring confirmed, trigger observed, **no marker shown starting a service end to end** |
| V-056 | 636 SMACK rules load, applications carry `_` | policy real and loaded; **labelling unverified** (no xattr records in the archive); whether `_` is confined by the rules is unproven |
| V-057 | Tuxera exFAT/NTFS drivers parse auto-mounted media | **candidate** — surface established, no defect found; falsification in progress |
| V-014 | USB property injection → installed root shell | payload is an unauthenticated root shell; injection needs real hardware |

**The unifying argument** is `docs/trust-anchors-in-writable-runtime-paths.md`: six of these are one mistake — a privileged decision resolved from
a writable runtime path — and `docs/vm/` shows `/tmp` is `1777`. That is the document to put in front of a vendor, together with the single
recommendation: **never resolve a security decision from a writable path, and make every such check fail closed.**

## 4b. The leading security finding, in one paragraph

**V-059**: the updater the vehicle runs (FUMO, embedded in `app/bin/AppUpgrade` as a 5.1 MB ELF inside its data) checks the payload with `ionice -c3 md5sum %1` at a site of its own, then
applies it from a **different invocation** - `/app/share/AppUpgrade/DecryptToPIPE -d <src> <offset> 0 | pv -q -L 8m | dd of=<partition> bs=512` - which **opens the payload again**. The TE2 key is
read at apply time; a genuine older package is already encrypted with it, so the version gate and anti-rollback are satisfied against *different bytes* than the ones written. Full measurements:
`evidence/v059-evidence.md`. The one open question is whether that second open hits the removable medium or a staged local copy, and only a runtime observation on a unit settles it.

## 5. Things that were claimed and corrected

Recorded because the corrections are part of the value:

- **4.34.0 → 4.41.0 → 4.42.0**: "the SPI gate opened" → "it never opened (wrapper could not write the path)" → "one unmeasured value decides it".
- **4.24.0**: the engineering page body was *not* fixed by answering its data queries; the screenshots said to show it were the home screen's EV
  page.
- **`19491003` is not the engineer code on this build**; the binary's own two SHA-256 constants identify a different vendor default. Plaintext kept
  out of the public tree per V-041.
- **`lms_asf.so` absent** was wrong — the plugin is `asf.so` and it ships.
- **"USB is not demonstrable"** was wrong — it was the research kernel, not the image; the vendor kernel enumerates USB fine.
- The **capability-stripping hypothesis** for MAC was tested twice and refuted (`CapEff` stayed full even for a correctly `SMACK64EXEC`-labelled
  exec).

## 6. If you have one hour

1. Read `docs/trust-anchors-in-writable-runtime-paths.md` — it is the argument, not the inventory.
2. Run the one measurement in `docs/vm/spi-gate.md` to close the init-fidelity question.
3. On a unit: engineering mode (About-screen gesture, PIN) and record whether `Force Update` / `Encryption Update` appear — that is the only
   no-privilege vector and it is still unconfirmed on hardware.
