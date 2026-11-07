# The interval-capture harness: making the boot58/boot65 defects unrepresentable

Date: 2026-11-08. Implements the five preconditions in
`docs/kernel/42-boot58-harness-not-retained.md`. No QEMU was run to produce this document; the
harness is testable on the host and is verified there.

## Why this exists

Two runs of the same configuration produced incomparable compositor captures, and the comparison
could not be repaired afterwards because of three defects:

1. the probe script that drove the run holding the only positive was **never retained**, so its
   timing, poll structure and relaunch logic are unrecoverable;
2. the compositor log was exported by measuring a size and then **streaming a still-growing file**,
   so the export exceeded its own declared length — one registration landed 19,494 bytes past the
   bound the script had just measured, and only 112 ms before the capture ended;
3. the capture was bound with `pidof <appname>`, which can select a **different process
   generation** than the one under observation; one run saw three generations and captured against
   a pid matching neither its cold nor its warm record.

Each is a property of the instrument, not of the system under test. So the fix is an instrument
that cannot express them.

## The five preconditions, and where each is enforced

| # | Precondition | Enforced by |
|---|---|---|
| 1 | Harness identity recorded | `interval-capture.sh` emits `SELF path=… algo=sha256 digest=…`, or `algo=none` and exits 3 **before measuring anything** |
| 2 | Marker carries monotonic time *and* driver offset | every `MARK` line carries both `t_mono=` and `off_c=` |
| 3 | Export is a closed snapshot | size measured, then `head -c "$SZ"` feeds the encoder, then the export is decoded and compared to `$SZ`; mismatch exits 4 |
| 4 | Capture bound to a named generation | `GEN n=… pid=… starttime=…` from `/proc/<pid>/stat` field 22, and `TARGET … binding=pinned_pid_and_starttime` or the explicit `binding=name_only` |
| 5 | Per-cause null | `verify_interval_capture.py`, which refuses to report a negative unless the window provably reaches the milestone |

The split matters. The guest script **does not judge its own capture**. Deciding "the window was
too short" from inside the capture is exactly how a truncated instrument becomes a confident
negative, so judgement lives on the host where the harness identity, the generation binding and
the window can all be seen at once.

## Outcome vocabulary

`verify_interval_capture.py` prints exactly one outcome:

| Outcome | Exit | Meaning |
|---|---|---|
| `HARNESS_MISMATCH` | 20 | identity or generation binding unproven — the run cannot be attributed to a script |
| `SNAPSHOT_NOT_CLOSED` | 21 | export did not round-trip to the measured size |
| `CAPTURE_TRUNCATED` | 11 | window provably ends before the milestone offset |
| `REGISTRATION_ABSENT` | 10 | window provably reaches the milestone and the marker is absent |
| `REGISTRATION_PRESENT` | 0 | marker found in a closed, identified capture |

Gate order is deliberate: harness identity is checked before presence, so a marker found through an
unidentifiable harness is still `HARNESS_MISMATCH` rather than a pass.

## The decisive test, mechanised

The verifier's rules reproduce the two real runs as regression cases:

- **boot58 shape** — window 186,509 ms, marker present at a 186,397 ms offset → `REGISTRATION_PRESENT`
- **boot65 shape** — window 163,703 ms against the same 186,397 ms offset → `CAPTURE_TRUNCATED`,
  with the reason stating the 22,694 ms shortfall

`tests/test_verify_interval_capture.py::TestRealRunReproduction` asserts both. If a future edit
loosens the truncation rule, that test fails.

## A unit trap found while building this

The protocol stamps look like `[824313.371]`. The whole part is **already milliseconds** and the
three decimals are sub-millisecond resolution. Reading the whole part as seconds rescales every
verdict by 1000×. The first draft of the verifier did exactly that and would have reported a
51-hour window. The conversion is now explicit and carries its cross-check in a docstring, and two
tests pin it.

## Verification performed

Host-side only; nothing was run in the guest.

```
$ bash tools/check_all.sh
=== interval capture: closed-snapshot and per-cause-null guarantees ===
  Ran 25 tests in 1.409s
  OK
```

- `tests/test_interval_capture_script.py` — 9 integration tests. Runs the real shell script against
  synthetic logs and asserts: the export never exceeds the measured size; a log that grows during
  capture cannot widen the export; self-identity is recorded; an unhashable harness exits 3 without
  measuring; an unbound capture is labelled `name_only`; a missing requested generation is a
  `HARNESS_MISMATCH`; markers carry both clocks; first/last protocol timestamps are extracted; an
  empty log is refused.
- `tests/test_verify_interval_capture.py` — 16 tests, including the boot58/boot65 reproduction and
  gate-order precedence.

## Also fixed: three checks in `check_all.sh` had never run

Stages 6 and 7 of `tools/check_all.sh` sat **after** an `exit "$rc"`, so `verify_findings.py` and the
`measure.sh` fail-closed self-test were unreachable dead code. They were described as wired in; they
had never executed under that script. Stage 6 also invoked bare `python3`, which is broken on this
host. The summary and exit now come last, and all three stages (6, 7, 8) execute. Their first real
run reports: 5 pass / 0 fail / 0 skip for `verify_findings`, 6 ok / 0 failed for the measure
self-test.

## Files

- `tools/uk_fw/guest/interval-capture.sh` — the guest-side driver.
- `tools/uk_fw/verify_interval_capture.py` — the host-side verifier.
- `tests/test_interval_capture_script.py`, `tests/test_verify_interval_capture.py` — the guarantees.
- `tools/check_all.sh` — Stage 8, plus the unreachable-stage fix.
- `docs/kernel/42-boot58-harness-not-retained.md` — the defect analysis this implements.

## Status

**REJECTED by both reviewers. Not qualified. Do not use this harness to authorise or interpret a
run.**

Astra reviewed the guest script (`docs/planning/astra-c9.md`) and Opus 4.7 reviewed the verifier
(`docs/planning/opus-4-7-c8.md`). Both returned REJECT, on different files, independently.

What survives: the tests pass, the closed-snapshot arithmetic bounds the payload, the `stat` field
arithmetic is correct, and the boot58/boot65 reproduction works. What does not survive is the claim
that the harness establishes what the preconditions require.

| Reviewer | Blocking finding |
|---|---|
| Astra | "Closed snapshot" is five independent reads of a mutable pathname, so rotation or in-place overwrite defeats it |
| Astra | `--generation N` is a `pidof` enumeration slot, not a launch generation, and it shifts when a process exits |
| Astra | The generation binding is optional and never re-checked at capture time, so precondition 4 is not mandatory |
| Astra | **Hashing this helper does not retain the harness that drove the run** — an unretained driver could invoke it and still leave the experiment unrecoverable, repeating boot58 |
| Astra | A failed export can still emit `SNAPSHOT_CLOSED` and exit 0, because verification runs on the in-memory copy |
| Astra | The clock substitutes `0` on failure and samples twice per marker; `sleep` failure silently shortens the window |
| Opus 4.7 | **`TS_RE` is defined and never used**, so the verifier trusts guest-supplied window bounds — the boot65 defect is reproduced inside the verifier |
| Opus 4.7 | The milestone offset is a prior-run constant imposed on a differently-paced run |
| Opus 4.7 | Bare substring matching is unsafe grammar (`AppHomeScreenController`, `/app/bin/AppHomeScreen`, `killed AppHomeScreen`) |
| Opus 4.7 | `target_binding` string equality is self-attestation, not evidence |
| Opus 4.7 | No cross-binding between `--log` and `--receipt` |

Both reviewers independently concluded that `REGISTRATION_ABSENT` cannot be safely reported on an
absolute offset at all, and both required an **in-stream precursor** instead. That precursor has been
measured and is stable: see `docs/kernel/43`.

### Honest statement of what this session got wrong

Precondition 1 was specified as "probe script frozen and hashed into `result.json`". The
implementation weakened that to "this helper hashes itself", which retains nothing about the driver
that launches, sleeps, kills and relaunches. That is the single most consequential gap, because it
leaves boot58's actual failure mode reachable. The self-hash is necessary but nowhere near
sufficient.

Precondition 5 was specified as a per-cause null. The implementation added a regex for re-deriving
timestamps and then never called it, so the null still depended on the instrument telling the truth
about its own window.

The rewrite required is specified in the two review documents. Until it is done and re-reviewed,
this harness is a passing test suite attached to an unproven instrument — which is precisely the
configuration this project has been burned by before.
