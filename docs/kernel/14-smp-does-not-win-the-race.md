# The registration timeout is not bought off by vCPUs — `--smp 6` and `--smp 8` both lose the race

Date: 2026-11-06. Doc 13 showed the vendor launcher deregisters AppHomeScreen ~3 ms after its
registration timeout. The cheap test was to throw vCPUs at it before patching the launcher. Result:
**both `--smp 6` and `--smp 8` still lose the race.**

## The measurement (pid stability is the check, before any pixels)

New order applied: socket → `NAME_OWNED=yes` → the call → **pid stability across two samples (+10 s and
+25 s)** → capture.

| run | name owned | pid +10 s | pid +25 s | `PID_STABLE` | capture |
|---|---|---|---|---|---|
| `--smp 4` (doc 12/13) | +100 s | 2305 | 2481 (by +5 s) | — | 129844 |
| `--smp 6` | +95 s | 2232 | 2484 | **no** | 129844 |
| `--smp 8` | +85 s | 2229 | 2559 | **no** | 129844 |

The deregister+relaunch loop (the pid change) is present at every vCPU count, and every capture is
129,844 bytes (the standby face). The name is owned slightly sooner with more vCPUs (+100 s → +85 s), but
the registration still lands on the wrong side of the launcher's timeout.

## What this means

- The ~3 ms lateness is **not** bought off by vCPU count. It is consistent at 4, 6 and 8 vCPUs, which is
  the signature of a **fixed wall-clock race** (the launcher's timeout fires, then the app's registration
  lands ~3 ms later by a fixed sequence), not of a CPU-starved startup. More vCPUs shrink total boot
  time a little but do not reorder the race.
- **The timeout patch is justified.** A projection-side vCPU change cannot win this; the next step is to
  find the launcher's registration-timeout constant and raise it (or otherwise make the registration
  land inside the window).

## The constant (not yet located — recorded as a gap, not a guess)

The timeout value, its units, and where it lives are **not yet found**. It is in the vendor launcher's
config or binary (`AppLauncher` / the app-manager side that logs `[TIMEOUT] [N Group]`). Until the value
and location are identified, the fix cannot be written; the evidence that it is *needed* is this doc.

## Files

- `work/vm/kbuild/boot39-smp6.log`, `work/vm/kbuild/boot40-smp8.log` — the two runs.
- `work/vm/kbuild/ws/partimg-build/smp-test.sh` — the pid-stability + capture script.
