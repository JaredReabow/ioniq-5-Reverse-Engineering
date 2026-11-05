# The QTimer shim answers it: there is no ~48 s timer — the deadline is not a fixed interval

Date: 2026-11-06. A logging-only `LD_PRELOAD` shim (QTimer::setInterval/start, launcher only) was built
and run. It records every timer the launcher arms, with the interval, the object, and monotonic +
wall-clock milliseconds.

## The shim (sixth instrument, zero behaviour change)

- `tools/uk_fw/guest/qtimer_trace.c` → `tools/uk_fw/guest/qtimer-trace.so` (7,384 B, x86-64, no host
  paths). Intercepts `_ZN6QTimer11setIntervalEi`, `_ZN6QTimer5startEv`, `_ZN6QTimer5startEi`; each
  `dlsym(RTLD_NEXT)`s the real symbol, logs one line to `/dev/ttyS2`, then forwards unchanged.
- Applied **launcher-only**: `/app/bin/AppLauncher.sh` `LD_PRELOAD=/usr/lib/libEGL.so.1:/qtimer-trace.so`.

## The interval census (deadline-scale values only)

```
ms=10000  ×24       ms=5000 ×22       ms=30000 ×17       ms=60000 ×12
ms=120000 ×8        ms=20000 ×4        ms=6000/14000 ×2
ms=9000, 7000, 45000, 40000, 180000, 15000  ×1 each
```

**There is no interval near 48,000 ms.** The only value within range is a single `ms=45000`, and it is
not 48.5 s. Hypothesis 1 (a fourth, ~48 s timer) is refuted.

## What the repeated arming shows

The `30,000 ms` timer is armed **17 times** and the `60,000 ms` timer **12 times**, at rising monotonic
offsets (e.g. 30 s timers at t_mono 59.8 s, 61.4 s, 65.2 s, 68.1 s, 98.8 s, 102.7 s, 103.2 s, 144.4 s).
That is the signature of **hypothesis 3**: a deadline timer that is re-armed by group progress, not a
single fixed timer. The ~48.5 s "deadline" measured in doc 22 is therefore the gap between the last
re-arm and the timeout slot, not any timer's interval.

## What this means for the patch

The `0x18270` patch (10 s → 30 s, doc 22) changed one of the 24 `10,000 ms` sites, but the deregister
deadline is not that timer. The fix is now known to be **at the group level** — the re-arming logic —
not a single immediate. This is the answer the shim exists to give, and it cannot be read from a constant.

## Files

- `tools/uk_fw/guest/qtimer_trace.c`, `tools/uk_fw/guest/qtimer-trace.so` — the shim.
- `work/vm/kbuild/boot47-shim.log` — the run.
