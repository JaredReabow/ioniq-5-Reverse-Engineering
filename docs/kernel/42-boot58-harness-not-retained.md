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
`[hmi2]` prefix; this audit confirms there is no `[hmi]` driver anywhere in the staged tree.

**So boot58's driving script is not retained at all.** Only its log survives. Its sleep offsets, poll
structure, relaunch logic and pre-commitments cannot be read from any file in the repository.

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

## Conclusion — not attributable, and that is the result

Three independent confounds separate the two observations:

1. **Different, partly unretained harnesses** with different timing and different relaunch logic.
2. **Materially different capture windows**, one of which demonstrably exceeded its declared bound.
3. **Different launch generations observed**, including a PID change after the warm relaunch marker.

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
- `docs/kernel/41-apphomescreen-absent-in-boot65.md` — the corrected presence/absence document.