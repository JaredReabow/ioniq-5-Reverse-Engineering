# The boot58 probe script is not retained, so the AppHomeScreen difference is not attributable

Date: 2026-11-08. Offline audit, no QEMU. This is the audit Astra C8 asked for
(`docs/planning/astra-c8.md`, answer 1). Its result is a **stop**, not a discovery of cause.

## What the audit was supposed to decide

Astra's discriminating question: *did boot65 observe the equivalent launch generation through the
equivalent milestone at which boot58 registered Home?* If the needed launcher records or clock anchors
were not retained, the instruction was to identify that exact gap and stop the offline pass.

That is what happened.

## Finding 1 — the two runs were driven by different probe programs

The retained logs carry different log prefixes, and the prefix identifies the driver:

| Run | Prefix in retained log | Occurrences |
|---|---|---:|
| boot58 (`boot58-hmi.log`) | `[hmi]` | 18 |
| boot65 (`boot65-final.log`) | `[final]` | 24 |

`[final]` is `final-run.sh`, which is retained. `[hmi]` is **no staged script**:

```
$ grep -hn 'log() { echo' work/vm/kbuild/ws/partimg-build/*.sh
  ... [hmi2] ... [final] ... [apps-check] ... [lay] ... [end] ...
$ grep -ln 'echo "\[hmi\] ' work/vm/kbuild/ws/partimg-build/*.sh
  NONE
```

The nearest match, `hmi-run.sh`, emits `[hmi2]`, not `[hmi]`. Astra had already flagged this from the
`[hmi2]` prefix.

### Search coverage for the missing driver

The absence was then attacked at every plausible location, not just the staged-script directory:

| Location searched | Result |
|---|---|
| All `log() { echo` definitions in `work/vm/kbuild/ws/partimg-build/*.sh` | `[hmi2]`, `[final]`, `[apps-check]`, `[lay]`, `[end]`, `[diag]`, `[both]`, `[close]`, `[preload]`, `[q]`, `[read]`, `[smp]`, `[stable]`, `[warm]`, `[appcrash]`, `[poweron]` — **no `[hmi]`** |
| Whole tree, `*.sh`/`*.py`/`*.c`, for the literal prefix | none |
| `git log --all -S'[hmi] '` across all branches | **no commit ever contained it** |
| All 15 retained `init-authentic-hmi.sh` copies | none contains a driver: `COLD_PID=0`, no log prefix |
| All 8 retained `weston-auth-check.sh` copies | all emit `[auth-hmi]`; `COLD_PID=0` in every one |
| boot58's own `command.json` | names `init=/init-authentic-hmi.sh`, which launches `/weston-auth-check.sh` (the `[auth-hmi]` script) |

The init-script chain is therefore intact and retained; what is missing is the **guest-side probe that
produced the `[hmi]` lines**. It was staged into the image for that run and never copied back, or was
overwritten by the later `[hmi2]` derivative. Either way it is unrecoverable from this repository.

**So boot58's driving script is not retained at all.** Only its log survives. Its sleep offsets, poll
structure, relaunch logic and pre-commitments cannot be read from any file in the repository, and no
git history exists to recover them from.

## Finding 2 — the two drivers differ in the logic that produces the observation

Even comparing the retained `final-run.sh` (boot65) against the retained `hmi-run.sh` (`[hmi2]`, a
derivative of boot58's driver, not boot58's driver), the differences are material to the question:

| Behaviour | `hmi-run.sh` (`[hmi2]`) | `final-run.sh` (`[final]`, boot65) |
|---|---|---|
| Waits for the HMI controller client (`pgrep -f ivi-shell-user-interface`, 40 s poll) | yes | no |
| Backend/compositor-init text gates | no | yes |
| `ivi_place` inventory + `HAS_1000..4000` | via `IVI_LIST` only | yes |
| `GATE2_POWER_STATUS` consumption check | yes | no |
| Pre-commitment header naming nulls | yes | different header |
| Log retention comment | "contains the hmi-controller module's stderr" | "retain the full weston log" |

Observed milestones also differ, consistent with different drivers:

| Marker | boot58 (`[hmi]`) | boot65 (`[final]`) |
|---|---:|---:|
| Cold PID | 2268 at **+75 s** | 2374 at **+85 s** |
| Cold killed | at **+145 s** (now 2667) | at **+125 s** (now 2546) |
| Warm relaunch marker present | **no** | yes (`WARM_RELAUNCH_SENT`) |
| Warm PID | 2667 | 2546 |
| Capture PID | 2667 | **2677** |
| PID generations observed | 2268 → 2667 (stable) | 2374 → 2546 → 2677 |

boot65 saw **three** PID generations where boot58 saw two. Its capture PID does not match its own warm
PID. These are not equivalent observations.

## Finding 3 — the export windows differ by an order of magnitude

Re-derived from the retained artefacts:

| Property | boot58 | boot65 |
|---|---:|---:|
| Declared `BEGIN weston` length | 234,468 B | 227,371 B |
| Actual decoded length | 277,341 B | 229,663 B |
| Growth during export | **42,873 B** | **2,292 B** |
| `AppHomeScreen` byte offset | 253,974 | absent |

boot58's registration sits 19,494 B **beyond** its own declared length. Whatever window recorded the
positive was not the window the driver had measured. boot65's window grew 19× less.

## Finding 4 — the one retained-harness alternative never reached the stage under test

`hmi-run.sh` (`[hmi2]`) is a derivative of boot58's driver, so any run it drove is the closest thing to a
replication with a retained harness. Two such runs exist, both shortly after boot58 (13:31 and 13:43):

| Run | Driver log | Reached | `AppHomeScreen` mentions |
|---|---|---|---:|
| `1793931975183356000` (boot59) | `[hmi2]` | `SOCKET_UP after 240s` only | 0 |
| `1793932712081972000` (boot61) | `[hmi2]` | `SOCKET_UP after 240s` only | 0 |

Both have `timeout=true`, `serial_completion_seen=false`, and `elapsed_seconds` of 300.07 and 300.10. They
were the rejected `hmi-controller.so` experiments: the compositor did not reach the stage where any
application registers. **They cannot discriminate the AppHomeScreen question because they never arrived at
it.**

A wider sweep confirms there is no third data point anywhere:

| Sweep | Result |
|---|---|
| All 65 run directories, `exported-weston.bin` present | only 3; only boot58 contains `AppHomeScreen` |
| All run `serial.log` files containing a `[hmi]` marker | boot58 only (18 hits) |
| All run `serial.log` files containing `[hmi2]` | the two runs above, both truncated before the app stage |

So the sole run that produced the positive is the sole run whose driver is unretained, and the only runs
with a retained driver never reached the milestone. That is the complete search space.

## Finding 5 — boot65's stream was 22.7 s too short to have reached the milestone at all

The byte counts in Finding 3 are suggestive but crude, because the two exports have different sizes and
different amounts of non-protocol content. The protocol stream carries its own monotonic millisecond
timestamps, which makes durations comparable **regardless of the different boot clock origins**.

| Run | First event | Last event | Stream duration |
|---|---:|---:|---:|
| boot58 | 637,916 | 824,425 | **186,509 ms** |
| boot65 | 1,233,868 | 1,397,571 | **163,703 ms** |

boot58's `AppHomeScreen` registration is at timestamp 824,313 — that is offset **186,397 ms** from its
stream's first event, or **112 ms before the stream's final event**.

boot65's entire retained stream spans 163,703 ms. **It ends 22,694 ms (22.7 s) before the offset at which
boot58 registered Home.** Had boot65's stream run for the same duration as boot58's, it would have reached
timestamp 1,420,265; it stopped at 1,397,571.

This is stronger than "not attributable". **boot65's retained observation window is structurally too short
to have contained the milestone even if registration had succeeded.** The absence of `AppHomeScreen` from
boot65 is therefore consistent with truncation, and cannot be read as a negative result at all.

The same measurement also shows how fragile boot58's positive is: it arrived 112 ms before its own capture
ended. A slightly slower run would have lost it. That is the margin on which this project's only
AppHomeScreen observation rests.

### The `dbg-out.txt` loophole is closed

`dbg-out.txt` is larger than the decoded export in both runs (543,371 B and 479,860 B), so it is fair to
ask whether the export truncated a longer captured stream that still sits undecoded in `dbg-out.txt`.
It does not:

| Run | Base64 span in `dbg-out.txt` | Expected for declared decoded size | Decoded export |
|---|---:|---:|---:|
| boot58 | 369,793 B | 277,341 B → 369,788 B base64 | 277,341 B |
| boot65 | 306,225 B | 229,663 B → 306,220 B base64 | 229,663 B |

In both cases the base64 block encodes the whole decoded export and nothing further. The extra size of
`dbg-out.txt` is the launcher log and screenshot channel, not withheld protocol stream. **So boot65's
weston capture genuinely ends at protocol timestamp 1,397,571 and there is no unread remainder.**

## Conclusion — not attributable, and that is the result

Three independent confounds separate the two observations:

1. **Different, partly unretained harnesses** with different timing and different relaunch logic.
2. **Materially different capture windows**, one of which demonstrably exceeded its declared bound.
3. **Different launch generations observed**, including a PID change after the warm relaunch marker.

Finding 5 makes this stronger than mere non-attribution: **boot65's stream was 22.7 s too short to have
reached the milestone at all**, so its silence is not even a negative observation. The comparison is not
merely uninformative about cause — it is uninformative about presence.

Any single-cause account of "why AppHomeScreen appears in boot58 and not boot65" is therefore
**unsupported**, including:

- this project's own earlier "registration timing" claim (`docs/kernel/41`, withdrawn as a conclusion);
- a pure capture-truncation account, which is a rival but not an established one;
- a launcher-environment account, likewise unestablished.

The honest statement is: **boot58 registered AppHomeScreen; boot65's retained export does not contain it;
the two observations are not comparable because the harness, the capture window, and the observed launch
generation all differ, and boot58's harness is not retained.**

## What this closes and what it opens

**Closes:** the boot58/boot65 comparison as a source of cause. It cannot be resolved by re-reading these
two runs more carefully — the discriminating artefacts do not exist. Astra's stop condition is met.

**Does not close:** whether AppHomeScreen can register under stock-equivalent conditions. boot58 proves it
*can*, under a harness nobody retained.

**Opens exactly one justified run**, and only with these conditions fixed in advance:

1. The probe script is **frozen and retained**, recorded by SHA-256 in the run's `result.json`, so a future
   audit can never again face an unretained harness.
2. Every marker carries the monotonic wall-clock time **and** the driver's own offset, so alignment does
   not depend on reconstructing sleeps.
3. The compositor log export is a **closed snapshot**: size measured after the final event, with the
   boundary recorded in the run output, so presence/absence cannot be an artefact of streaming a growing
   file.
4. The launched process identity is captured per generation (PID and start time), with the capture
   explicitly bound to a named generation rather than to `pidof`.
5. The null is stated per-cause (`CAPTURE_TRUNCATED` / `HARNESS_MISMATCH` / `REGISTRATION_ABSENT`), so a
   harness or capture fault can never be reported as a confirmed negative.

Condition 5 is the direct lesson of the paused boot78: its null would have converted a capture or harness
artefact into a confident negative.

## Files

- `work/vm/kbuild/boot58-hmi.log`, `work/vm/kbuild/boot65-final.log` — retained driver logs.
- `work/vm/kbuild/ws/runs/1793931162561454000/exported-weston.bin`,
  `work/vm/kbuild/ws/runs/1793944643111075000/exported-weston.bin` — decoded streams.
- `work/vm/kbuild/ws/partimg-build/final-run.sh`, `hmi-run.sh` — retained drivers.
- `docs/planning/astra-c8.md` — the consultation that required this audit.
- `docs/kernel/41-apphomescreen-absent-in-boot65.md` — the corrected presence/absence document.- `docs/vm/58-interval-capture-harness.md` — the harness that implements the five preconditions below.

## Instrument (implemented)

The five preconditions are now implemented and verified on the host, not merely stated:

- `tools/uk_fw/guest/interval-capture.sh` — enforces preconditions 1–4 in the guest and refuses to
  judge its own capture.
- `tools/uk_fw/verify_interval_capture.py` — enforces precondition 5, with the outcome vocabulary
  `HARNESS_MISMATCH` / `SNAPSHOT_NOT_CLOSED` / `CAPTURE_TRUNCATED` / `REGISTRATION_ABSENT` /
  `REGISTRATION_PRESENT`.
- `tests/test_interval_capture_script.py` (9 integration tests) and
  `tests/test_verify_interval_capture.py` (16 tests), wired into `tools/check_all.sh` Stage 8.

The verifier reproduces the two real runs as regression cases: the boot58 shape yields
`REGISTRATION_PRESENT`, the boot65 shape yields `CAPTURE_TRUNCATED` with the 22,694 ms shortfall
named. The instrument has **not** been exercised against the guest yet, and it does not by itself
authorise a run.
