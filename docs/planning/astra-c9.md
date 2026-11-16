# Astra C9 — REJECT: the guest script bounds the payload, it does not establish a snapshot

Read-only review, 2026-11-08, of `tools/uk_fw/guest/interval-capture.sh` only.
Reviewed at commit `38069e6`. No file was written by the consultation; no QEMU, no git.

The review was scoped to the guest script alone, with Opus 4.7 reviewing the verifier in parallel
and deliberately not shared, so the two findings are independent.

## Verdict

**REJECT.** Astra's summary sentence is the finding:

> The script bounds the encoded payload's length. It does **not** establish an immutable snapshot,
> retain the driving harness, or bind the observation to the intended launch generation.

That is correct, and it matters because the script's own header claims all three.

## Blocking defects

### 1. "Closed snapshot" is five independent reads of a mutable pathname

Lines 184, 190, 195–198, 206–213 each independently open `$LOG`: size, digest, first timestamp,
last timestamp, payload. Nothing establishes that the five reads see the same inode or content.

Counterexample Astra gives: `wc` measures file A at 100,000 bytes; rotation replaces the pathname
with file B of at least the same size before the digest read; every later read describes B's first
100,000 bytes; the round-trip length matches, the digest matches the payload, and `SNAPSHOT_CLOSED`
is emitted even though the measured object was A.

Also unenforced: in-place overwrite or truncate-then-regrow changes content without changing length.
Application output still in the writer's buffer is not in the file, so a byte-count check says
nothing about whether the final event was flushed.

The decoded-length comparison proves only that local base64 decodes to the expected count. It does
not prove content identity, atomicity, provenance or completeness.

**Fix:** acquire the object **once**, then derive size, digest, timestamps and export from those
same bytes. Astra is explicit that holding one descriptor protects against pathname replacement but
**not** against in-place overwrite; and that copying once, without producer coordination or a real
snapshot facility, is not atomic either.

### 2. `--generation N` names an enumeration slot, not a launch generation

`GEN_N` counts currently observed instances in `pidof` output order. A process that exits is
silently skipped, so every later index shifts. An exited cold process is absent entirely, so a
surviving warm process becomes "generation 1" regardless of its true launch number.

The emitted `(pid, starttime)` identifies the process selected *after* an ambiguous lookup. It does
not establish that it is the process the caller meant.

**Fix:** the launch driver assigns the semantic generation and records the exact PID and start time
at launch; the capture takes that tuple as input and rejects a mismatch. Do not resolve a semantic
generation through a fresh `pidof` enumeration.

### 3. The binding is optional and never re-checked at capture time

Omitting `--generation` produces `binding=name_only` and the script still exits 0. **Precondition 4
is therefore not mandatory**, which contradicts the receipt's own claim.

Worse, after discovery the script waits and captures without re-reading the selected process. A
process can exit during the settle interval and be replaced, and the receipt will still say
`binding=pinned_pid_and_starttime`.

**Fix:** require the launcher-supplied tuple; re-validate at the observation boundaries; treat a
disappeared or changed tuple as invalidating the binding.

### 4. Hashing this helper does not retain the harness that drove the run

This is the finding that most directly defeats the purpose of the work. The script hashes itself and
emits a path. That does not retain the driver responsible for launches, sleeps, kills and relaunches.

> A future unretained `[hmi]` driver could invoke this helper. The receipt would contain a perfectly
> valid helper hash while the actual experiment-driving program remained unrecoverable. That repeats
> boot58's central failure.

Also a pathname race: hashing `$0` does not prove the pathname still refers to the bytes the shell
began executing.

**Fix:** make execution conditional on a frozen, retained run package containing the actual driver
*and* the capture helper, with SHA-256 identities and invocation/configuration recorded in a run
manifest, and have the receipt reference that manifest. Precondition 1 was written as "probe script
frozen and hashed into result.json"; the implementation silently weakened that to "the helper hashes
itself".

### 5. A failed export can still produce `SNAPSHOT_CLOSED` and exit 0

Line 202 suppresses write failure with `>> "$OUT" 2>/dev/null || true`. Line 206 then verifies the
**in-memory** `$B64`, not the bytes written. Meanwhile `emit()` silently redirects to stdout on
output failure, which can split the receipt and payload across channels.

So a failed or partial write can be followed by `SNAPSHOT_CLOSED … match=yes` and exit 0.

**Fix:** open the intended channel once, fail on write error, do not silently switch channels, and
distinguish "local snapshot validated" from "transport complete".

### 6. The clock helper fabricates timestamps on failure and samples twice per marker

Line 69 substitutes `0` when uptime cannot be read, which makes `off_c` negative on a later failure
and meaningless on an initial one. Line 164 takes separate samples for `t_mono` and `off_c`, so the
two fields need not describe the same instant.

Astra reproduced the `centi()` format dependency independently:

| Input | Then-current | Correct |
|---|---:|---:|
| `1000.00` | 100000 | 100000 |
| `0.05` | 5 | 5 |
| `0.5` | 5 | 50 |
| `1000` | 1000 | 100000 |

It notes 4.1.27 normally emits two decimals, so this is a format dependency rather than a daily
failure — see the note below, where the same defect was found and fixed before this review landed.

**Fix:** fail on unreadable or malformed clock input; read once per marker and derive both fields
from that sample; check for backwards movement.

### 7. A fixed sleep is not evidence the observation reached its endpoint

The comment claiming the settle delay captures "after the last interesting event" is false: 20 s
after the helper starts is not an application milestone or a flush acknowledgement. And
`sleep … || break` turns a failed delay into an *earlier* capture, silently shortening the window.

**Fix:** fail on a failed delay; define the required endpoint against the intended generation and a
documented anchor; record an unreached endpoint as incomplete observation.

## Confirmed correct, so it is not "fixed" into a bug

Astra explicitly checked the `stat` field arithmetic and confirmed it:

> At line 123, removing `pid (comm) ` leaves original field 3 as field 1; original field 22 is
> therefore `$20`. Greedy `sed 's/.*) //'` handles spaces and embedded parentheses in ordinary
> `comm` values. Do **not** "fix" this to `$22`.

`AppHomeScreen` is under the 15-byte `comm` limit.

## Verdict on the self-identity gate

**Keep the fail-closed exit.** Astra's reasoning, adopted:

> "Measure and label unidentifiable" creates a plausible-looking capture that can later be detached
> from its warning and treated as qualified evidence. That makes the next truncated-instrument
> mistake more likely.

But the gate is *insufficient* as implemented — it establishes a digest of a pathname, not retained
identity of the complete driving harness. Strengthen it; do not remove it.

## The one fix that matters most

> **Acquire one immutable, producer-bounded log artifact, then derive every capture field and the
> export from those exact bytes.**

## Note on the clock defect

The `centi()` defects Astra lists (items 5 and 6) were found independently in this same session and
fixed at commit `81a1201`, *before* this review landed, with six regression tests that extract and
exercise the real `centi()` from the script rather than a copy. Astra reviewed `38069e6`. Its other
findings stand unchanged.
