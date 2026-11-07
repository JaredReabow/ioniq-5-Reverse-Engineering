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

## Progress since the rejection

### Verifier (Opus 4.7's findings) — revision 2, all eight addressed

| Opus finding | Fix |
|---|---|
| `TS_RE` defined and never used | Bounds are re-derived from the log via `TS_RE`; monotonicity asserted; disagreement with the receipt is `HARNESS_MISMATCH` |
| No `--log`/`--receipt` binding | New **gate 0**: the log is re-digested and must equal the receipt's declared `CAPTURE digest` and byte count, else `LOG_RECEIPT_MISMATCH` |
| Bare substring matching | Structured pattern `create_hmi_client\([^)]*"NAME"` by default; tests prove `killed AppHomeScreen`, `/app/bin/AppHomeScreen` and `AppHomeScreenController` do **not** match |
| Absolute offset as the criterion | Replaced by an in-stream **precursor** plus `--milestone-after-precursor-ms`; the absolute offset now has no decision role at all |
| `target_binding` self-attestation | Not fixed. Still string equality on a self-reported field. Requires the guest to emit the pid/starttime evidence block first |
| `errors="replace"` on a binary log | The log is read as bytes and matched with byte patterns |
| Negative `window_ms` | Non-monotonic stamps return `HARNESS_MISMATCH` |
| `_ts_to_ms` fractional truncation | Whole part is milliseconds by definition; documented and cross-checked in `docs/kernel/43` |

Two defects were caught by the tests during the rewrite rather than by review:

1. **The first structured pattern produced a false negative on the only real positive.** Requiring
   `"AppHomeScreen"` immediately before `)` never matches the actual form
   `create_hmi_client(1, 1006, "AppHomeScreen", new id ivi_hmi_client@21)`, which has trailing
   arguments. Against boot58's real log the verifier reported `REGISTRATION_ABSENT` when the truth was
   `REGISTRATION_PRESENT`. Found by running it on the retained log, not on synthetic fixtures.
2. **The absolute offset could still decide the outcome.** A first attempt kept the absolute offset as a fallback when no
   precursor-relative reference was supplied, so an operator could restore the rejected criterion by
   passing one flag. It now has no decision role: without
   `--milestone-after-precursor-ms` the answer is "cannot decide".

Verified end-to-end against both retained logs: boot58 → `REGISTRATION_PRESENT` (exit 0); boot65 →
`CAPTURE_TRUNCATED`, naming the 22,031 ms shortfall (exit 11). 40 tests pass in the full suite.

### Guest script (Astra's findings) — revision 2, RE-REVIEWED AND STILL REJECTED

**Astra C10 (`docs/planning/astra-c10.md`) rejected revision 2, and two of the claims below were
false.** The table is retained because it records what was attempted; the honesty note after it
records what actually closed.

| Blocker | Astra C10 verdict |
|---|---|
| A1 closed snapshot | **PARTIALLY CLOSED** — one artefact for downstream reads, but `cp` is not atomic |
| A2 `pidof` enumeration slot | **CLOSED** |
| A3 binding re-check | **PARTIALLY CLOSED** — a shared log has no per-generation tag, so attribution is not achievable this way |
| A4 harness retention | **PARTIALLY CLOSED** — proves the driver existed and matched; does **not** prove it ran |
| A5 export failure | **STILL OPEN** at the time of review — the brace-group defect below |
| A6 clock/sleep failures | **PARTIALLY CLOSED** — a failed transformation could still fabricate a timestamp |

Two overclaims made in this document were falsified:

1. **"No suppressed failures remain"** was false. The frame write used `{ printf; cat; printf; }`,
   and a brace group returns only its *last* command's status. Astra reproduced a failed `cat`
   followed by a successful `printf` taking the success path, reaching `EXPORT_WRITTEN`,
   `OUTCOME CAPTURED` and exit 0.
2. **"An unretained driver can no longer produce a valid receipt"** was false. An unretained driver
   can invoke the helper while supplying a manifest naming some *other* retained, matching driver.
   Nothing verifies the named driver *ran*.

Both are now corrected in the script header, and both are fixed or narrowed as described under
"Fixes applied after Astra C10" below.

The blocker table that follows is the original revision-2 claim, kept for the record:

| Astra blocker | Fix |
|---|---|
| A1 closed snapshot was several reads of a mutable pathname | The source is read **once** into a private snapshot; size, digest, timestamps and export all derive from that single copy. A short copy is fatal. Concurrent growth is measured before and after and recorded as `SOURCE_BOUNDARY … grew_during_copy=` rather than assumed away |
| A2 `--generation N` was a `pidof` enumeration slot | The enumeration is **removed**. A generation is supplied by the launcher as an exact `(pid, starttime)` pair and is mandatory |
| A3 binding optional and never re-checked | `--expect-pid` and `--expect-starttime` are required arguments; the pair is verified at start **and** immediately before the snapshot; any change aborts |
| A4 self-hash did not retain the driving harness | A frozen run manifest naming `DRIVER` and `HELPER` with SHA-256 is **required**. The script verifies its own digest against the manifest and verifies the driver's bytes still match. An unretained driver can no longer produce a valid receipt |
| A5 failed export could emit `SNAPSHOT_CLOSED` and exit 0 | The payload is staged to a file, decoded and size-checked, then appended with its status checked. `emit()` fails the script on a write error instead of falling back to stdout. No suppressed failures remain |
| A6 clock/sleep failures were silent | A malformed or unreadable `/proc/uptime` aborts (exit 7); a failed `sleep` aborts; one clock sample per marker feeds both fields |

### Integration between the two files

The revision-2 script emits `SELF` and `TARGET` lines in the vocabulary the verifier reads, plus a
`HARNESS` line carrying the manifest and driver identity. This was a real gap: the first draft of
revision 2 emitted `BINDING_REQUESTED` and no `SELF`, which the verifier would have rejected as
`HARNESS_MISMATCH`.

### Defects found by testing rather than by review

1. **A helper `die()` wrote to an undefined exit code and was never called** — removed.
2. **`emit`/`exit` inside a command substitution** only exits the subshell, so a clock failure would
   have been swallowed and the caller would have carried on with an empty timestamp. The clock
   function now returns non-zero and each caller decides.
3. **The `path=` extraction truncated at the first space.** On this project the repository path
   itself contains spaces, so the truncated path resolved to an existing *directory*, passed the
   readability test, and hashed to nothing. The extraction now spans `path=` to ` sha256=`, and an
   empty digest is a hard failure rather than a mismatch message.
4. **A test hardcoded the host's absolute Python interpreter path**, which the sanitisation rule
   forbids in committed content — the path was removed from the test before it was committed.
   Replaced with `sys.executable`.

### End-to-end proof on the real logs

The two files are now exercised **together** against the retained captures, not just against
synthetic fixtures:

| Run | Pipeline result |
|---|---|
| boot58 (`1793931162561454000`) | guest script → receipt → decode → verifier → `REGISTRATION_PRESENT`, exit 0 |
| boot65 (`1793944643111075000`) | guest script → receipt → decode → verifier → `CAPTURE_TRUNCATED`, naming the 22,031 ms shortfall, exit 11 |

47 tests pass in the full suite. This is what caught revision 1's false negative on boot58's only
positive.

### Fixes applied after Astra C10

| Astra finding | Fix | Verified by |
|---|---|---|
| A5 brace-group status | Frame written as three separately checked appends | Direct shell comparison: old form exits 0 with a failing `cat`, new form exits 6 |
| A5 encoder/decoder status | Encode staged through `head`/`base64`/`tr`, each checked; decode staged, status checked, decoded **digest** compared as well as length | Test suite |
| A6 fabricated timestamps | Strict format (digits, at most one dot, no leading dot); `cut`/`sed` statuses checked; final value must be all digits | Seven inputs: `.`, `1.23.4`, `1000.25`, `0.00`, `1234`, `1000.5`, `garbage` → all correct |
| New defect 2: no transaction boundary | Guest emits `RECEIPT v2 id=…`; verifier parses only the **last** transaction and requires **exactly one** outcome, which must be terminal success | Both of Astra's reproductions now return `RECEIPT_INCOMPLETE` |

The transaction fix also retroactively invalidates the `RECEIPT_INCOMPLETE` gate added in commit
`b393622`: that gate used `any(o.startswith("CAPTURED"))`, which accepted a stale terminal line and
accepted `CAPTURED` followed by `EXPORT_FAILED`. The review found it within the hour.

### Status: NOT qualified, and three gaps are not fixable by this instrument

53 tests pass and the pair works end to end on both retained logs. That is not qualification.

- **A3 is not fixable here.** A shared compositor log carries no per-generation tag. The helper can
  prove a process with the expected `(pid, starttime)` was alive around the copy; it cannot prove the
  copied bytes are that generation's activity. No capture from this instrument may be described as
  "generation-attributed".
- **A4 is only partly fixable.** A manifest plus digest proves the driver existed and matched. Proving
  it ran needs an invocation record the helper cannot forge, or an external ledger. Until then
  boot58's failure mode is narrowed, not closed.
- **A1 needs producer coordination.** Flush-and-stop, or an acknowledged rotation. The helper has
  neither.

The boot78 task stays paused. A run remains unjustified.
