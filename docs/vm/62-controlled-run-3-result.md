# Controlled run 3 — result: the narrow claim is satisfied, and the Home UI did not render

Date: 2026-11-08. Run `1794057967702206000`, workspace `work/vm/kbuild/ws-run63` (fresh CoW clone).
Driver committed at `90e2e3e` (sha256 `c11c5e4e…`). Artifacts in
`evidence/controlled-run-3-2026-11-08/`. Specification: `docs/vm/61-controlled-run-2-spec.md`.

This is the first run in which the frozen harness produced a completed export transaction. It is also
the first run with a working display channel. Together they give a result that is more informative
than either alone — and it is not the result the phrase "registration present" might suggest.

## The export channel — the narrow claim is satisfied

```
RECEIPT v2 id=interval-r3-t0c15142
SELF path=/interval-capture.sh algo=sha256 digest=13b5920a…0663
HARNESS run=interval-r3 manifest=/interval-manifest.txt
        helper_sha256=13b5920a…0663 driver=/interval-run.sh driver_sha256=c11c5e4e…94bf
TARGET app=AppHomeScreen binding=pinned_pid_and_starttime pid=2456 starttime=10820
CAPTURE bytes=157860 digest=5fcc7770…9111 first_ts=2889571.396 last_ts=3035159.825
SNAPSHOT_CLOSED bytes=157860 decoded=157860 match=yes
EXPORT_WRITTEN bytes=210480 channel=/dev/ttyS3
OUTCOME CAPTURED bytes=157860 … pid=2456 starttime=10820
```

The frozen verifier, run against the retained receipt and the decoded payload:

```
REGISTRATION_PRESENT marker matched 'create_hmi_client\([^)]*"AppHomeScreen"' inside a closed,
identified capture (precursor at 93845 ms)
```

**What this licenses, and nothing more** (`docs/planning/astra-c11.md`): the retained payload contains
the specified structured marker, its received byte count and digest match the completed capture
transaction, the manifest's **named driver file** matched the committed driver (`c11c5e4e…`), and the
supplied process identity passed the helper's checks around copying.

**What it does not license:** persistence, rendering, interactivity, driver execution, or generation
attribution. Nor does it revive the boot58/boot65 comparison.

## The display channel — the Home UI did not render

Three captures at `+10 s`, `+60 s` and `+110 s` after first sight, all via
`/usr/libexec/weston-screenshooter`, all 129,844 bytes, all valid 1920×720 PNGs.

**All three are byte-identical** (`sha256 2746aad2…`).

What the image shows: a **KIA wordmark centred on black** at 1920×720 — the boot splash. Not a Home
screen, not a widget layout, not a standby clock.

So the visible compositor output was the same still frame at a point where the app process was alive
(`+10 s`) and at two points where it was dead (`+60 s`, `+110 s`). The frame did not change when the
app died, which is consistent with it not being app-drawn content.

This is the most useful thing this run establishes: **an `AppHomeScreen` registration marker can be
present in the compositor's protocol stream while the visible output is still the boot splash.** The
two facts are compatible, and only the second answers "is the authentic Home screen up".

## Runtime channel

```
GEN n=1 pid=2456 starttime=10820 observed_at_cs=10869
SAMPLE n=1..6 … alive=yes same_generation=yes
SAMPLE n=7..24 … starttime=none alive=no
PERSISTENCE_RESULT samples=24 alive=6 of=24 interval_s=120
EXPORT_SCHEDULE attempted=1 at_s=30 rc=0
DRIVER_DONE generations=1 … final_cs=26807
```

The process was alive from ~108.7 s, survived to at least the export at `+30 s`, and was gone by the
sample after that. Alive 6 of 24 samples.

## Conclusions, per the table fixed before launch

| Claim | Status |
|---|---|
| Marker present in a closed, identified capture | **YES** — narrow claim satisfied |
| Home **persisted** across the interval | **NO** — process alive 6/24; and the display never changed |
| Home **rendered** | **NO** — the visible frame is the KIA boot splash at all three points |
| **Interactive** | **UNRESOLVED** — not attempted |
| Why the process exited | **not established** |

The combination is coherent rather than contradictory: the app registers with the compositor, does not
draw anything the compositor is displaying, and exits. What is not established is *why*, and this run
deliberately does not speculate.

## A cross-run observation worth recording, not explaining

The lifetime of the `AppHomeScreen` process after first sight varied across three runs:
~66 s (run 1), ~20 s (run 2), ~30 s (run 3). The value is not stable. That variance is a fact about
these three runs; no cause is claimed, and the earlier launcher-timeout hypothesis remains a candidate.

## What this run fixed that run 2 could not

Run 2's display captures all returned `no_file`, including while the process was alive. The cause was
the working directory: the driver runs from `/` (started by an init script), and the shooter writes
`wayland-screenshot.png` relative to `$PWD`. Running it from `/tmp`, checking both candidate paths, and
recording the shooter's own exit status fixed it — `shooter_rc=0 path=/tmp/wayland-screenshot.png` at
all three points in run 3.

## What the next run should test, and the one thing it must not

The open question is now sharply posed: **why does a registered app's surface not reach the visible
output?** Candidate areas include layer/screen placement in the IVI shell, the splash layer remaining
above the app surface, and the app exiting before it commits a frame. Choosing between them needs a
protocol-side observation synchronised with a frame, not more display captures of the same splash.

What the next run must not do: treat a fourth capture of the KIA splash as evidence about the Home
screen, or treat `REGISTRATION_PRESENT` as having answered the rendering question. This run shows
exactly why those two claims are different.
