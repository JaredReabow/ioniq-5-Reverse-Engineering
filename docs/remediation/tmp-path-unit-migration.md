# The `/tmp` path-unit family: the exact migration, and how to verify it

Date: 2026-11-08. **Specified, not applied.** Applying it edits seven systemd path units and the components that create their
markers. It is written as one change because all seven share a single root cause, and fixing them separately would mean seven
images and seven chances to break the boot.

Covers **V-077** (three root scripts sending MICOM CPU-watchdog reset requests), **V-078** (the UNECE/wireless gate),
**V-050** (wireless enablement) and the `/tmp`-marker half of **V-055** and **V-071**.

## The problem, restated exactly

systemd `.path` units activate a service when a file appears. Seven are **enabled**, and every one of them watches a path under
`/tmp`, which is a `1777` tmpfs. So the trigger for each privileged action is a file any local process can create.

| Enabled unit | Marker | Activates | Privilege |
|---|---|---|---|
| `mpauto.path` | `/tmp/AppMPAutoTest/do_mpauto` | `mpauto.service` → `/etc/mpauto.sh` | root; emits a system-bus signal ×10 |
| `ofono.path` | `/tmp/no_isa` | `ofono.service` → `/usr/sbin/ofonod -nd` | root; telephony daemon |
| `remote.path` | `/tmp/no_isa` | `remote.service` → `/app/bin/TmsRemoteApp` | root |
| `pstore-reboot.path` | `/tmp/pstore_saved` | `pstore-reboot.service` → `/etc/pstore-reboot.sh` | root; `SetETCCPUWDTReset 0x06` |
| `spi-validation.path` | `/tmp/spi_validation_NOK` | `spi-validation.service` → `/etc/spi-validation.sh` | root; `SetETCCPUWDTReset 0x01` |
| `supplicantmanager.path` | `/tmp/no_unece` | `supplicantmanager.service` | root; `modprobe cfg80211`, wireless manager |
| `weston-crash.path` | `/tmp/weston.crash` | `weston-crash.service` → `/etc/weston-crash.sh` | root; `SetETCCPUWDTReset 0x00` |

The intent of each marker is sound: these are **boot-state conditions** ("no ISA device", "pstore has a message", "weston
crashed", "this unit is not UNECE"). The mistake is only the *location*. A boot-state condition belongs in a directory that
only root can write.

## The change, counted

**Six distinct markers, watched by seven units** — `/tmp/no_isa` is shared by `ofono.path` and `remote.path`.

**Creators found by literal search in `/etc`, `/app/bin`, `/usr/bin`:**

| Marker | Created by |
|---|---|
| `/tmp/AppMPAutoTest/do_mpauto` | `app/bin/ApplicationManager`, `app/bin/micomanager_userspace`, `app/bin/AppMPAutoTest` |
| `/tmp/no_isa` | `app/bin/AppLauncher` |
| `/tmp/pstore_saved` | `usr/bin/dlt-daemon` |
| `/tmp/no_unece` | `app/bin/AppLauncher` |
| `/tmp/spi_validation_NOK` | **creator not found** — see the coverage limit below |
| `/tmp/weston.crash` | **creator not found** — see the coverage limit below |

**Coverage limit, stated so it is not read as absence.** The search covered `/etc`, `/app/bin` and `/usr/bin` only. A creator in
`/usr/sbin`, `/usr/libexec`, `/lib`, a kernel module, or a path assembled at runtime from string fragments would not have been
seen. The two missing creators are therefore **unlocated, not absent**, and locating them is a prerequisite of the change for
those two markers only — the other five are fully accounted for.

## The migration

**Target:** `/run/state/` — a root-owned `0700` directory on the tmpfs that already exists by design for exactly this kind of
early boot state. Markers become:

```
/run/state/mpauto
/run/state/no_isa
/run/state/pstore_saved
/run/state/spi_validation_nok
/run/state/no_unece
/run/state/weston.crash
```

**Why `/run` and not something else.** The root filesystem is read-only at runtime, so the markers cannot live in `/etc`
(V-065 already records that `/etc` is forced to symlink into `/tmp` for this reason, and the same mistake is why we are here).
`/var` is the read-write partition, but these are boot-scoped conditions that should not survive a reboot, and a stale
`/var` marker would fire a watchdog reset on the next boot. `/run` is tmpfs, cleared at boot, and root-owned.

**Per-unit edit** — the only change to each path unit is the `PathExists=` line:

```ini
[Path]
PathExists=/run/state/weston.crash
Unit=weston-crash.service
```

**Per-creator edit** — each creator must `mkdir -p /run/state` with mode `0700`, owned by root, before writing its marker. For
`dlt-daemon` and the three `AppMPAutoTest`-family binaries that is a code change, not a script edit; for `AppLauncher` it is
the same. Creating the directory with `0700` at first use is sufficient and races safely if two creators do it at once.

**Ordering, which is the one real hazard.** These units carry `DefaultDependencies=no`, and `/run` is mounted by `esinit` very
early. If a unit is evaluated before `/run` exists, `PathExists` is simply false and it stays false until something changes
under `/run` — so a marker written later still fires. That is safe. What is **not** safe is the reverse case: if `/run/state`
were pre-created in the image at build time it would not exist after the tmpfs mount, so the directory **must** be created by
the creator, not baked into the image.

## What must not be done

- **Do not** simply add `ConditionPathIsReadWrite` or a similar guard to the path units. That changes when they fire, not who
  can make them fire, and it would silently stop the watchdog handlers working on a real fault.
- **Do not** move the markers to a subdirectory of `/tmp` with `0700`. `/tmp` is wiped and re-created by `esinit`; a
  root-owned subdirectory would be re-created by whichever component runs first, and the ordering that makes that safe is the
  same ordering this change exists to avoid depending on.
- **Do not** change the payloads. `/etc/mpauto.sh`, `/etc/pstore-reboot.sh`, `/etc/spi-validation.sh` and
  `/etc/weston-crash.sh` are root-owned and unchanged by this migration; the defect is the trigger, not the action.

## Verification, without a vehicle

On a staged image, for each of the six markers:

1. **The unit still fires for root.** As root, `mkdir -p /run/state && : > /run/state/<marker>`, then confirm
   `systemctl status <unit>` shows the service started. This proves the migration did not break the intended path.
2. **The unit does not fire for a non-root writer.** `: > /tmp/<old-marker>` and confirm the service does **not** start.
   This proves the defect is closed.
3. **Boot regression.** Boot the image and confirm the normal boot still reaches multi-user, that no WDT-reset method is sent
   on a healthy boot, and that the wireless daemon's start/no-start behaviour is unchanged for the configured variant.

Step 2 is the finding. Step 3 is the one that matters most, because four of the seven units exist to handle real faults and a
migration that stops them firing on a genuine fault trades one defect for a worse one.

## Status

**Specified, not applied.** Two of the six markers have creators whose location is not established, and step 3 of the
verification needs an image that boots to multi-user — which this projection does. Neither is a reason to apply the other five
early: the value of the change is that all seven markers leave `/tmp` in one step, so a partial application would leave the
family half-closed and hard to reason about.
