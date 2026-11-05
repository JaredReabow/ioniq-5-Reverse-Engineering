# The 45 s deadline is `QTimer::start(int)` with a computed value — not a literal, not `setInterval`

Date: 2026-11-06. The QTimer shim was extended to log `__builtin_return_address(0)`. It answered the
question the constants could not.

## The decisive line

```
QTMR startInt obj=0x56093f3db310 ms=45000 ret=0x56093d31f320 t_mono=173332 t_real=1793916716332
```

The 45-second deadline is armed with **`QTimer::start(int)`** (the `startInt` hook), **not**
`setInterval`. That is why patching the `setInterval` immediate at `0x18270` (doc 22) did nothing: that
code path never carries 45,000.

## The value is computed, not a literal

`45000 = 0xAFC8`. A search for the raw little-endian immediate `c8 af 00 00` across the whole
`AppLauncher` binary returns **nothing**. So 45,000 is not an instruction immediate anywhere in the
binary — it is a **computed** value (a loaded field, a `45 * 1000` product, or configuration), exactly
the hypothesis the user stated. The three immediates that do reach `QTimer::setInterval`
(`0x2710`/`0x7530`/`0xea60`) are unrelated operational timers.

## The caller, logged but not yet resolved to a source

`ret=0x56093d31f320` is the return address into the caller. `AppLauncher` is a stripped PIE
(`ET_DYN`, text segment file-offset == vaddr, 2 MB-aligned), so the return address maps to approximately
file offset `0x1F320` — but that offset lands mid-instruction in the `[onDemandTerminate]` string-format
routine, so the precise base needs to be resolved (a known-symbol anchor or a runtime `/proc/…/maps`
read) before the disassembly can name the field/product that produces 45. The next precise step is
"which caller arms a 45 s timer at t_mono≈173 s", and the shim already prints the hook (`startInt`) and
the return address needed to answer it.

## What this closes

- The deadline is a **45-second computed interval armed via `start(int)`**, not an unknown, and not a
  `setInterval` immediate. That is a name and a next step, not a mystery.
- The three wrong constants (doc 15's inference, doc 22's `setInterval` site) are now explained: the
  value never passes through a patchable literal.

## Files

- `tools/uk_fw/guest/qtimer_trace.c`, `tools/uk_fw/guest/qtimer-trace.so` — the shim (now with `ret=`).
- `work/vm/kbuild/boot48-ret.log` — the run.
