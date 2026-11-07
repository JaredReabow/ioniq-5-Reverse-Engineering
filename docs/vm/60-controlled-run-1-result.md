# Controlled run 1 — result

Date: 2026-11-08. Run `1794056221676329000`, workspace `work/vm/kbuild/ws-run61` (CoW clone).
Specification: `docs/vm/59-controlled-run-spec.md`. Artifacts retained in
`evidence/controlled-run-1-2026-11-08/`.

This is the first controlled run under the retained driver. It has a **mixed result**: the runtime
channel produced a real measurement; the export channel failed closed and therefore licenses no
conclusion about registration.

## What was fixed before this run

Two defects from the first attempt (`1794055821491663000`) were found and fixed first:

1. **An init script runs before `/proc` is mounted.** The driver's very first clock read failed with
   `/interval-run.sh: line 86: /proc/uptime: No such file or directory` and it exited 3 before doing
   anything. It now waits for the clock source.
2. **`ttyS2` is a vendor getty console.** A login prompt landed in the export file. Export moved to
   the pristine `ttyS3`; runtime stays on `ttyS2`, where the `[irun]` prefix makes the lines
   identifiable despite the getty.
3. `DIAG_CMD` now emits `IONIQ_VM_USERSPACE_READY`, without which `vm_boot` never sends the command.

A third change was needed for the run to proceed at all: the SDHCI gdb patch (`-S`, RSP) never
completed, and `vm_boot` caps that socket at 30 s, so two attempts died at 30.28 s with no
`patch.json`. The guest had nevertheless mounted `mmcblk0p16` and reached systemd, so this run was
launched with `--no-compat` **explicitly**, and that choice is recorded here rather than assumed.

## Runtime channel — measured

```
[irun] DRIVER version=1 ... persist_s=120 sample_s=5 settle_s=20 sandbox=no
[irun] DRIVER fixed_before_launch=yes t0_cs=459
[irun] PHASE wait_socket
[irun] PHASE socket_up waited_s=0
[irun] GEN n=1 pid=2318 starttime=9042 observed_at_cs=9089
[irun] SAMPLE n=1..11 ... alive=yes same_generation=yes      (at_cs 9601 .. 15149)
[irun] SAMPLE n=12..24 ... starttime=none alive=no             (at_cs 15692 .. 21961)
[irun] PERSISTENCE_RESULT samples=24 alive=11 of=24 interval_s=120
[irun] DRIVER_DONE generations=1 final_generation_pid=2318 starttime=9042 final_cs=24593
```

Measured facts:

| Quantity | Value |
|---|---|
| driver start | 4.59 s (`t0_cs=459`) |
| AppHomeScreen generation first observed | **90.89 s** (`pid 2318`, `starttime 9042`) |
| alive samples | **11 of 24** (last alive 151.49 s) |
| first dead sample | **156.92 s** |
| persistence interval | 120 s (fixed before launch, not tuned) |
| generations observed | 1 |

So: **one AppHomeScreen process appeared at ~91 s and was gone by ~157 s.** It did not survive the
fixed 120 s observation interval; it was alive for roughly the first 60 s of it.

## Export channel — failed closed, by design

```
RECEIPT v2 id=interval-r1-t0c24509
SELF path=/interval-capture.sh algo=sha256 digest=13b5920a…0663
HARNESS run=interval-r1 manifest=/interval-manifest.txt manifest_sha256=870ec702…
        helper_sha256=13b5920a…0663 driver=/interval-run.sh driver_sha256=b8e762c2…3d52
TARGET app=AppHomeScreen binding=pinned_pid_and_starttime pid=2318 starttime=9042
OUTCOME BINDING_FAILED phase=start reason=pid_not_running pid=2318
```

The manifest's `driver_sha256` is `b8e762c2…`, which is the committed driver at `70ad2bc`. The helper
verified its own digest and the driver's bytes inside the guest, then refused to capture because the
process it had been told to bind to no longer existed.

Running the frozen verifier against this receipt:

```
RECEIPT_INCOMPLETE receipt's terminal outcome is 'BINDING_FAILED phase=start reason=pid_not_running pid=2318',
                   not a completed capture
```

That is the correct verdict. The instrument did not produce a false positive, and it did not silently
degrade into a negative.

## Conclusions, per the table fixed before launch

| Claim | Status |
|---|---|
| Export: marker present in a closed capture | **UNRESOLVED** — the instrument failed (`BINDING_FAILED`); per the pre-committed table this yields *no conclusion about Home* |
| Does authentic Home **register** | **UNRESOLVED** — no marker evidence exists; the process existing is not a registration |
| Does the AppHomeScreen **process persist** across the interval | **NO** — it was gone by ~157 s of a 120 s interval that began at ~91 s |
| Is authentic Home **rendered** | **UNRESOLVED** — no display recording was captured in this run |
| Is it **interactive** | **UNRESOLVED** — not attempted |

The one conclusion this run supports is a statement about a *process*, not about the UI: a process
named `AppHomeScreen` with `(pid 2318, starttime 9042)` existed at ~91 s and had exited by ~157 s.

It does **not** establish why it exited. The historic launcher-timeout explanation (`docs/kernel/22`,
`docs/kernel/24`) is a candidate, not a finding, and this run adds no evidence for or against it
beyond the two timestamps.

## Open anomaly — recorded, not explained away

`socket_up waited_s=0` at `t0_cs=459` (4.59 s). The compositor cannot have been listening that early,
and `debugfs -R "stat /run/user/root/wayland-0"` on the staged `p5.img` reports *File not found*, so
there is no leftover socket in the image to explain it.

The most likely reading is that the wait gate is **ineffective** — `[ -S "$SOCKET" ]` returned true,
or the loop exited early, when the path did not exist. If so, the driver does not actually sequence
itself after compositor start; in this run the *generation wait* is what did the sequencing, since the
first process was found at 90.89 s.

This is unresolved and is not a licence to re-tune anything. What it means for interpretation is
narrow and stated: the socket gate in this run proves nothing.

## Host-side caveat

There is no `result.json` for this run: the host-side invocation was interrupted by the operator tool's
own time limit after the guest work had already finished (`DRIVER_DONE`, `OUTCOME COMPLETED` and the
export receipt are all present). The guest did not time out. This is a host harness artefact and is
recorded rather than papered over.

## What the next run needs

1. Capture the display. The spec requires continuous display recording and this run produced none,
   which is why "rendered" is unresolved.
2. Decide the export timing question **without retro-fitting**: the fixed `PERSIST_S=120` plus
   `SETTLE_S=20` places the export ~140 s after first sight of the process, and this run shows the
   process dies at ~66 s. A future run that wants a marker must say so in its own spec, with its own
   pre-commitment — it may not shorten this one's values after seeing this result.
3. Resolve the `waited_s=0` anomaly before trusting the socket gate.
4. The `--no-compat` choice needs justification on its own evidence, not merely because the patch
   timed out.
