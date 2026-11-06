# C3 — keep the transaction, prove the second arrival

## Scope and corrected baseline

Read-only consultation; the only write is this file. No git, experiments, binary analysis, or changes to probes were performed. Repository sources actually read:

- **[K33]** `docs/kernel/33-unowned-name-was-instrument-error.md`
- **[K31]** `docs/kernel/31-warm-survives-registration-name-unowned.md`
- **[V53]** `docs/vm/53-the-qualified-run.md`
- **[C2]** `docs/planning/astra-c2.md`
- **[Agreed]** `docs/planning/AGREED-NEXT-STEPS.md`
- **[Postrun]** `docs/planning/astra-postrun.md`
- **[Probe]** `work/vm/kbuild/ws/partimg-build/qualified.sh`

K33 supersedes the unowned-name diagnosis in K31, V53 and C2: **the bus name is `com.lge.hyundai.avn.appmanager`; `com.lge.avn.appmanager.registration` is its interface.** Matching manager/launcher addresses refute the proposed wrong-bus explanation for that run. The retained wire excerpt proves a deregistration call concerning **app 12, AppCamera**, not successful home registration or the identity of either app-11 notification. [K33]

The 266 ms separation, duplicate report and warm survival at 60 s remain observations; K31 deliberately omitted power-on. Do not combine an earlier duplicate-guard termination and the warm survivor into a claim that this particular surviving PID was killed. [K31; C2, evidence boundary] The supplied signatures and `com.lge.avn.applauncher.inform.launched` are briefing premises; these files do not establish their full result semantics. All procedures below are **proposed**, not tested capabilities.

## 1. Next run: retention is a launch prerequisite

**One unchanged-handshake run, with a host-retained evidence volume and verified export; no adapter, timeout tuning, manual second manager, or duplicate-guard bypass.** Preserve warm launch and authentic labelling. Keep the launcher responsible for app-id-2 startup. [K31; V53; C2 §§1–2]

### Exact storage and transport contract

Use one collision-resistant run ID, `R`, chosen by the host before boot. Proposed paths:

| Location | Role |
|---|---|
| Host `work/vm/kbuild/evidence/R/evidence.raw` | Dedicated writable guest evidence disk, outside the disposable root image; never delete with the guest |
| Guest `/evidence/R/` | Mount on that disk; **not** a directory falling back onto the ephemeral root |
| Host `work/vm/kbuild/evidence/R/serial-evidence.raw` | Unabridged byte capture of the guest `/dev/ttyS2` evidence channel |
| Host `work/vm/kbuild/evidence/R/retained/` | Decoded, hash-verified files used for analysis |
| Host `work/vm/kbuild/evidence/R/receipt.json` | Completeness verdict and manifest digest; written by the host verifier |

The existing probe already exports the launcher log as base64 through `/dev/ttyS2`; it does **not** export the monitor log. Extend that transport rather than treating a console preview as evidence. The host capture endpoint and disk attachment are preparation requirements, not capabilities established by these documents. If either cannot be provisioned and qualified, do not start the vendor attempt. [Probe]

1. **Qualify persistence and end-to-end transport before releasing the stack.** Verify the mounted device identity and available space; forbid fallback to `/tmp`. Write and fsync a run-specific canary, export it through the actual evidence channel, and have the host verify its length and digest. A prior collector-only qualification must establish recovery from the retained disk independently of guest-root lifetime. Record all statuses and stderr. A PID announcement is not a capture control. [Postrun §3; Probe]
2. **Write raw evidence directly to `/evidence/R/`.** Required files: `dbus-monitor.log`, `dbus-monitor.stderr`, `launcher.raw`, `manager.raw`, `home.raw`, `kernel.raw`, `processes.jsonl`, `ownership.jsonl`, `clock-pairs.jsonl`, `dispatch.jsonl`, `commands.jsonl`, and `receipt.json`. Record target PID plus start time, bus unique names and owner identities, active interventions and executable/instrument hashes. Ensure actual stdout/stderr destinations are captured from process start, including child redirections. If a vendor-fixed `/tmp` destination cannot be redirected projection-side, continuously drain it into this volume, detect rotation/truncation, and declare any uncovered prefix or tail. [C2 §1; Postrun §3]
3. **No restrictive interface-only monitor filter.** Capture all messages on the relevant session bus during the bounded window, including method returns, errors, owner changes and launcher notifications; retain typed payloads. The old interface match can omit replies lacking that interface and the distinct launcher notification interface. Monitor readiness must precede the first relevant vendor connection/launch; gate stack release on readiness rather than merely starting a background PID after finding the address file. [Probe; K33; C2 §1]
4. **Continuous persistence, then orderly sealing.** Use a collector that drains promptly, records errors/drop counters, and periodically fsyncs files; the final seal must flush and fsync every file and directory. Do not claim periodic sync eliminates a crash-tail window. On orderly completion, send a final bus control, allow its reply to be captured, stop collectors gracefully, wait for their exits, and freeze the files before calculating hashes. Preserve logs through registration +60 guest seconds, or 60 seconds after the warm launch if registration never occurs. Use C2's bounded startup/watchdog budgets, recording host-watchdog expiry separately from guest time. [C2 §1]
5. **Export every frozen file, not a grep or `cut`.** Reuse `/dev/ttyS2` with a single channel writer: `BEGIN R path byte_count sha256`, numbered base64 chunks, then `END R path chunk_count`. Export `manifest.json` last, containing every required file's size, SHA-256, record/line count, first/last event time, producer status, controls and loss flags. Console output contains only paths, digests and verdicts. The host must reject missing chunks, duplicate/conflicting indices, decode failures, byte-count/digest mismatches and missing required files. [Proposed repair of Probe's `cut -c1-500`; Postrun §3]
6. **No teardown before host verification.** The host controller verifies the full manifest and writes its receipt before permitting normal VM disposal. On export failure, retry the frozen bytes, not the experiment. On guest crash, retain `evidence.raw` and serial capture; recover the disk offline from a copy, without booting the vendor again. Missing final seal or missing control means `PARTIAL`, even if the disk is recoverable. Never delete the only surviving artifact. [Proposed retention rule; K33; Postrun §3]

**Transport completeness is not capture completeness.** Matching hashes prove the bytes arrived intact; they do not prove the monitor observed everything. Qualify the actual bus path with a private test-name acquire/release and a daemon call/reply **before** vendor release and again after the observation window; retain monitor readiness, exit status, stderr, connection loss and queue/drop diagnostics. An implementation without a way to bound loss cannot support an absolute “no event occurred” claim. [C2 §1; Postrun §3]

### A null must still answer the question

Query `NameHasOwner` and `GetNameOwner` for **`com.lge.hyundai.avn.appmanager`**, on the explicitly selected bus; retain the complete request/reply/error and owner PID/UID mapping. Capture ownership changes, not just one snapshot. [K33; C2 §1, corrected name]

- **Controls/export fail:** `NOT MEASURED — instrument/retention failure`, with the failed step and recoverable evidence pointer; no vendor diagnosis.
- **Manager/home never starts:** `BLOCKED_BY_STARTUP`, with last lifecycle transition and observation window; second notification was not testable.
- **Qualified bus capture has no home registration:** “No app-11 registration observed on this bus in this interval”; the AppCamera deregistration is not a substitute. Handler evidence must decide whether launcher registration was internal or came by another path.
- **One bus notification, two launcher handler entries:** the second entry exists inside the launcher path; this falsifies the simple claim of two observed wire notifications, but does not by itself explain the internal duplication.
- **Two bus notifications, only one attributable handler entry:** wire duplication observed; which one produced the duplicate guard is **unresolved**.
- **Two attributable handler entries:** identify first and second by handler sequence, sender/incarnation, payload and causal predecessor; state whether each came from a bus message, timeout, or other callback.

If complete capture lacks the handler attribution needed for the question, report that precise missing discriminant and stop unchanged boots. This replaces V53's too-strong leap from “no captured call” to “projection cannot complete the handshake.” [V53 stopping rules; Postrun §§2–3]

## 2. Correlation: clock conversion supports causality; it does not replace it

**The target is the second registration notification received by the launcher for app 11, not the second line displayed by a monitor.** Bus observation order, callback dispatch order, and buffered log-output order are different observables. Earlier reports already warned that two registration log lines need not mean two requests. [Postrun §§1–2]

Use three linked records:

1. **Clock bridge.** Accept the briefing's guest-monotonic monitor clock as the working premise, but record the monitor build and verify its actual timestamp domain during qualification. A guest helper samples `MONOTONIC_before`, `REALTIME`, `MONOTONIC_after` before release, periodically, and immediately around the registration window and end control. For a sample `(m1,r,m2)`, the realtime-minus-monotonic offset lies in `[r-m2, r-m1]`; include timestamp resolution, intervening drift and detected wall-clock steps. Preserve the raw wall-clock launcher text, its date/timezone and parser assumptions. Mapping is piecewise, never one boot-time offset silently applied across a clock step. [Proposed implementation of C2's correlation requirement]
2. **Wire identity.** Assign each captured message a collector ordinal; retain bus ID, sender unique name, destination, serial, reply serial, object path, interface/member and arguments. Serial numbers are scoped to the sending connection, not a global order. Associate short-lived senders with PID/start time while they are alive. A call/reply edge or an exact message identity gives a stronger correlation than temporal proximity. [C2 §1 capture 2]
3. **Launcher receive/dispatch identity — the decisive record.** Before running, locate the actual registration dispatch entry and the two accepted/duplicate log sites from the vendor artifact; these notes do not supply those addresses. Use a supported external process-local tracepoint/debugger observation, not a global preload or behaviour patch, to record a monotonically increasing handler-entry sequence, guest monotonic time, PID/TID, app ID, predecessor/call site and message identity where available. Trace timeout/internal notification entries too. Link each accepted/duplicate decision to its entry sequence. If multiple threads participate, observe the serialized state update/guard decision as well; unsynchronized timestamps alone cannot establish a total order. [Postrun §§1–4; C2 §1]

The required answer has the form: **“Entry N accepted app 11 from X; entry N+1, caused by message `(bus, sender, serial)` or internal call site Y, reached the registration state check second and was rejected.”** For bus dispatch, preserve an explicit message-to-entry link, not a guessed nearest timestamp. If that identity is unavailable, disjoint calibrated timing bounds can establish temporal separation but cannot invent source attribution.

A wrapper timestamp added when a log line is read is only a delayed receipt timestamp. It cannot prove emission time, and the observed 266 ms wall-clock gap alone cannot prove which source arrived second. If calibrated intervals overlap, wall-clock steps intervene, or handler identity cannot be recovered, publish `ORDER/SOURCE UNRESOLVED`. External tracing can perturb timing: qualify its overhead and mark a duplicate that disappears under tracing as an instrument-sensitive result, not a fix. [K31; Postrun §3]

## 3. Could stock do this too?

**No stock unit means no direct observation of stock execution.** A second projection run, even with untouched vendor binaries, is not a stock baseline. The cheapest useful discriminator is **the provenance and enabling condition of the second handler entry**, using the retained trace plus a narrow read of the shipped caller/callee and startup configuration. [Postrun §§1–2; Agreed §2]

Specifically: does the second entry originate in a projection shim/relaunch/injected notification, or in an original vendor path? If vendor-originated, does that path require a projection-induced timeout, missing service or altered power/preload state, or do the two original notification paths follow necessarily under the same recovered preconditions? Record the producer's executable identity, call site, preceding state and transaction completion. Fix one demonstrated projection cause and require the contrary observation; do not infer origin solely from the receiving vendor binary. [C2 §§2, 5; Postrun §4]

This cheapest observable can **attribute a projection-generated duplicate** or establish a **vendor-code path capable of producing it**. It cannot prove that a stock unit reaches those preconditions. If both emissions are vendor-owned and depend on timing, stock reproduction remains unknown without an independently sourced stock trace or equivalent validated runtime evidence. The honest outcome can therefore be “vendor-origin duplicate under projection conditions; stock incidence unknown.” Do not turn missing access to stock into either absolution or a vendor fault claim.

## 4. After the duplicate: ordered route to interactive 1920×720

Assuming next run resolves registration, keep that evidence sealed and advance through these separate gates:

1. **Lifecycle closure.** Correct owner, correlated completion, no fallback/duplicate, authentic home label and same warm PID surviving 60 s. Warmth is a measured workaround, not proof that cold boot is finished. [K31; C2 §§1, 5]
2. **Deliver power-on to that instance.** Retain the established `set_power_on_status` transaction and evidence of consumption, not shell success. K31's surviving run explicitly did not send it; standby there does not diagnose rendering. [K31; C2 §1 capture 3]
3. **Survive actual home layout.** Capture home stderr, kernel/denials, lifecycle and any crash at power-on. A historical warm crash occurred during power-on layout; the later no-power survival result does not exercise that phase. Do not reinstate the old PHEV explanation without new evidence. [Agreed §3; K31]
4. **Prove surface ownership and presentation.** App 11 must own a unique noncolliding surface, with a new presented buffer after power-on, visible on the intended layer/output. Verify the candidate ID 1010 rather than assume it is active; the prior 2080 collision and camera-derived frame invalidated earlier claims. [Agreed §1; C2 §3]
5. **Prove home content and geometry.** Verify an actual 1920×720 output and intended surface geometry/crop/scale, then apply a predeclared home-element manifest and negative controls against standby/camera. These read files do not establish the current output dimensions or provide that manifest; this is a preparation dependency, not a completed check. [C2 §3; target dimensions from the brief]
6. **Prove interaction, not just pixels.** Declare one harmless home action and its expected visible transition/return before testing. Retain input coordinates/timestamps, focus/routing to the same home client, resulting surface updates and continued liveness; repeat once to detect a one-frame success. The documents establish no working input path, so input delivery/focus remains an open acceptance gate. [Extension of C2 §3's identity/persistence predicate to the requested interactive milestone]
7. **Repeat from a clean documented start.** Reproduce with the declared warm-up, label, surface and input configuration, and report whether cold startup is still unsupported. Separate projected interaction success from stock fidelity and security findings. [C2 §§3–5]

**Most likely next surprise: the first real power-on/layout transition exposes another resource, state or permission dependency—or a crash—despite the 60-second standby survivor.** This is a forecast, not an observed new failure: K31 withheld that transition, and Agreed §3 records an earlier crash specifically there. Input focus/routing is the next unmeasured gate after presentation, but the supplied evidence gives power-on layout the stronger warning.

Prefer projection-side lifecycle, state delivery, surface mapping and input fixes grounded in a named discrepancy. **No vendor patch is proposed.** Exact duplicate-guard or dispatch patch offsets are **unknown in the files read**; do not invent one. Any later patch ticket must name binary SHA-256, file offset versus runtime address, original/replacement bytes and semantic trade: disabling the guard loses real duplicate protection; extending the deadline changes lifecycle behaviour; changing the surface table changes vendor allocation and requires collision checks. External diagnostic probes likewise need verified symbol/address mappings before use, though they are not a recommended persistent binary patch. [C2 §2; Postrun §4; Agreed §§1–4]

## 5. Two sentences proposed for `docs/MEASUREMENT-DISCIPLINE.md`

> This project twice promoted its own false negatives into vendor-fault claims: comparing absent process addresses did not measure bus equality, and querying an interface string with `NameHasOwner` did not measure ownership of the manager's bus name. Future readers should treat a negative as evidence only within a retained, identity-checked, positively controlled and complete observation window; otherwise the result is NOT MEASURED, and earlier causal claims must be corrected rather than carried forward.

Basis: [C2, opening verdict; V53, convergence; K33, correction]. This consultation does not edit that register.
