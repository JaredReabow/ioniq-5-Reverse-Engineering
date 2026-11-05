# The PHEV SMACK denial is gone — but the app still does not survive to the laid-out frame

Date: 2026-11-06. The authentic `App::home` exec label was applied to `/app/bin/AppHomeScreen` before
the launcher spawns it, and the PHEV directory was created. The specific denial is fixed; the frame is
still not the layout.

## What was applied

- `/app/bin/AppLauncher.sh` now runs, before launching the launcher:
  `/sbin/chsmack -e "App::home" /app/bin/AppHomeScreen` and
  `mkdir -p /rw_data/app_data/common/AppPhev` — the vendor's own mechanism, the way `smack_setup.sh`
  labels its binaries.
- Surface id remains the corrected `11 -> 1010` (doc 27). The timer shim was removed.

## The checks, in the required order

1. **Label** — `APP_LABEL=[]` (inconclusive: the check ran after the app had been deregistered, so
   `/proc/<pid>/attr/current` was read on a dead pid). Not measured, not passed.
2. **Denial absent** — `COMMONPHEV_DENIALS=0` and `DMESG_SEGV=[]`. **The `object="Data::commonphev"`
   denial is gone.** This is the specific fix's target, and it held.
3. **PHEVDB created** — `PHEV_DIR=[ls: …/AppPhev/: Permission denied]` from the *monitor* (which runs as
   `_`), so this is also not directly measured.
4. **Frame** — `CAP_30s bytes=120448` (a new size, but the standby class, not the laid-out widget frame).

## The honest reading

The `App::home` exec label removed the PHEV denial it was meant to remove (check 2 is the one that
matters, and it is clean). But the app still does not survive to the laid-out frame: the launcher log
shows the same `[REGISTERED ERROR] Already registered` → `notifyAppTerminate […][15]` (SIGTERM)
deregister loop, and other apps keep logging `[ERR CODE:1] App has been Crashed`. So the PHEV denial was
one contributor, not the whole story — the remaining deregister/duplicate loop is still the blocker, and
the label check must be taken while the app is alive to confirm the exec label actually landed.

## Files

- `work/vm/kbuild/boot50-smack.log` — the run.
- `work/vm/kbuild/ws/partimg-build/AppLauncher.sh.smack` — the label + mkdir applied.
