# Astra C10 — REJECT on revision 2: two of my claims were false

Read-only re-review, 2026-11-08, of `tools/uk_fw/guest/interval-capture.sh` revision 2 at commit
`6e39713`, with the verifier read at its then-current state. No files were written by the
consultation. Astra ran syntax checking and in-memory reproductions only.

Reviewed identities: helper `5e597e57880d761e`, verifier `a278ad68268d821a`.

## Verdict

**REJECT.** Astra's summary:

> The rewrite fixes process selection and several failure paths. It **still does not establish a
> producer-bounded, generation-attributable snapshot**, and **a failed payload export can still take
> the success path**.

Two of this session's own claims were falsified, and both were claims made with confidence:

1. `docs/vm/58` said "no suppressed failures remain" (A5). **False.** The frame write used a brace
   group, which returns only its *last* command's status; a failed `cat` followed by a successful
   `printf` still took the success path.
2. The script header said "An unretained driver can no longer produce a valid receipt" (A4).
   **False.** An unretained driver can invoke the helper while supplying a manifest that names some
   *other* retained, matching driver. Nothing verifies the named driver **ran**.

## Blocker-by-blocker

| # | Status | Astra's reason |
|---|---|---|
| A1 | **PARTIALLY CLOSED** | Downstream reads now use one copied artefact, so the specific inconsistency is fixed. But `cp` is not an atomic snapshot: rotation between the first size measurement and the copy can substitute another file of equal length; in-place rewriting can produce mixed bytes; truncate-then-regrow evades the size check; and buffered application output may never have reached the source. `grew_during_copy=` is narration, not enforcement — any size difference reads as "grew", including shrinkage or a failed after-measurement |
| A2 | **CLOSED** | No executable `pidof` enumeration remains; the tuple is supplied externally and syntactically validated |
| A3 | **PARTIALLY CLOSED** | Mandatory and genuinely checked twice, but there is no post-copy validation, a zombie can still have a readable `stat` with the expected start time, and — decisively — **a shared compositor log has no per-generation tagging**, so both checks can pass while the copied log contains another generation's event. A third check narrows the window; it cannot solve event attribution |
| A4 | **PARTIALLY CLOSED** | The manifest checks are real, but they establish only that the named driver's **bytes existed and matched**. They do not establish that it ran. No invocation/configuration record is required; nothing retains driver or manifest in the evidence package; and the manifest is hashed at one point and re-parsed at another, so mutation can separate the recorded digest from the records actually used. **Boot58's essential failure remains reachable** |
| A5 | **STILL OPEN** | `{ printf; cat; printf; }` returns the last command's status. Astra reproduced it: a failed `cat` followed by a successful `printf` selected the success branch. The encoder pipeline checked only `tr`; the decoder's status was discarded and only output length examined; `SNAPSHOT_CLOSED` is emitted before transmission; and the output path is reopened for every append rather than opened once |
| A6 | **PARTIALLY CLOSED** | The caller refactor is correct and there are no unchecked callers. But the conversion did not reliably report failure, and Astra measured: `.` → success, timestamp `0`; `1.23.4` → success, `123`; failing `cut` → success, `1000`; failing `sed` → success, `0`; a backward clock emitted `off_c=-10` with success. "A failed transformation can still fabricate zero" |

## New defects Astra raised

### 1. The checked export was not actually checked

The brace-group defect above. Astra also notes that even correctly checked writes establish only that
the *local* channel accepted bytes, not that a receiver obtained them; the receiver must validate the
complete frame, decoded byte count and digest. A guest-side decode cannot prove that.

### 2. Receipts had no enforced transaction boundary

`$OUT` is append-only in usage, not write-once in implementation, so an earlier successful receipt can
contaminate a later incomplete one. Astra's verifier check was `any(o.startswith("CAPTURED"))`, which
neither resets at `RECEIPT v2` nor rejects a later failure. It returned `REGISTRATION_PRESENT` for both:

- an old `OUTCOME CAPTURED` followed by a new receipt that never completes;
- a receipt containing `CAPTURED` followed by `EXPORT_FAILED`.

**This retroactively invalidates the `RECEIPT_INCOMPLETE` gate added in commit `b393622`.** That gate
was correct in intent and insufficient in construction, and the review found it within the hour.

## What was fixed in response

| Finding | Fix |
|---|---|
| A5 brace-group status | The frame is written as three separately checked appends. Proven by direct shell comparison: the old form returns 0 with a failing `cat`; the new form returns 6 |
| A5 encoder/decoder status | Encode staged through explicit `head`/`base64`/`tr` steps, each checked. Decode staged to a file, status checked, and the decoded **digest** compared as well as the length |
| A6 fabricated timestamps | Strict input format: digits with at most one dot, no leading dot. `cut`/`sed` statuses checked. Final value must be non-empty and all digits. Verified across seven inputs: `.`, `1.23.4`, `1000.25`, `0.00`, `1234`, `1000.5`, `garbage` |
| New defect 2 (transactions) | The guest emits `RECEIPT v2 id=<run>-t0c<cs>`; the verifier parses only the **last** transaction and requires **exactly one** outcome, which must be the terminal success. Both of Astra's reproductions now return `RECEIPT_INCOMPLETE` |

## What remains open, stated plainly

- **A3's core point is not fixable by this instrument.** A shared compositor log carries no
  per-generation tag. The helper can prove a process with the expected `(pid, starttime)` was alive
  before the copy; it cannot prove the copied bytes belong to that generation's activity. Any claim
  that the capture is "generation-attributed" is false and must not be made.
- **A4's core point is only partly fixable.** A manifest plus digest proves the driver existed and
  matched at hash time. Proving it ran requires the driver itself to emit an invocation record that
  the helper cannot forge — or an external ledger. Until then boot58's failure mode — an unretained
  driver producing a plausible receipt — is narrowed but not closed.
- **A1's atomicity gap** needs producer coordination (flush and stop writes, or an acknowledged
  rotation). The helper does not have that.

## Consequence

The harness is **not qualified**, and the claim that revision 2 closed all six blockers was
overstated. It closed A2 fully, A1/A3/A4/A6 partially, and A5 only after this review found it still
open. The boot78 task stays paused.
