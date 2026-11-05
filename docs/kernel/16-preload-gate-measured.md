# The preload gate is measurable: `ask_preload_complete_status` returns 0 — the manager never saw preload complete

Date: 2026-11-06. Doc 15 reduced the launcher timeout to an internal `preload-complete` deadline and
laid out three options. This is the one measurement that decides between them, run before any patch.

## The call, and the answer

```
[preload] NAME_OWNED=yes at +105s
[preload] APPHOME_PID_0=[2321]
[preload] PRELOAD_BEFORE=[method return … int32 0]     ← before set_power_on
[preload] SET_POWER_SENT
[preload] PID_STABLE=yes pid10=[2505] pid25=[2505]      ← one deregister happened (2321→2505), then stable
[preload] PRELOAD_AFTER=[method return … int32 1]      ← after set_power_on
```

- **Before `set_power_on_status`: `ask_preload_complete_status` returns `int32 0`.** The manager never
  saw the app's preload complete. This is the state the launcher's deadline is waiting on.
- **After the call: it returns `int32 1`** — once the app was deregistered and relaunched (2321→2505),
  the preload flag became complete.

## What it decides

Per the decision rule, **0 means the manager never saw the app's preload** — which matches the app's own
`Can not connect to signal preload_complete_status` line. That selects **option 3**: emitting
`preload_complete_status(true)` on the manager's interface is the smallest substitution (one signal, no
vendor binary touched, and it must be named as a substitution).

## The global-flag caveat, checked

`ask_preload_complete_status` is called with **no arguments** and returns a single `int32` — it is a
**global** flag for the group, not an AppHomeScreen-specific one. The per-component guess
`ask_preload_navi_complete_status` does **not** exist (`Error … No such method`), so the per-component
variant mentioned in doc 15 is not reachable under that name; the global method is the one that gates the
launch group.

## Honest note on the pid

`PID_STABLE=yes` here but `APPHOME_PID_0` is 2321 while `pid10` is 2505 — one deregister+relaunch still
happened between name-owned and +10 s, then the replacement was stable through +25 s. The preload flag
moved 0→1 exactly across that replacement. So the race is still present; this run caught the *after*
state of it, and the before/after pair is what names the fix.

## Files

- `work/vm/kbuild/boot41-preload.log` — the run.
- `work/vm/kbuild/ws/partimg-build/preload-probe.sh` — the probe.
