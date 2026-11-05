# Post-run judgement

Scope: read-only review of the six requested documents; no experiments or repository changes beyond this note. Citations below use **K29**, **K28**, **V50**, **Agreed**, **Current** (first 120 lines only), and **V46** for those documents respectively. Recommendations and competing explanations are not measurements.

## 1. Next best step

**Choose (c): establish the registration transaction before changing its implementation.** First read the retained launcher/app/stand-in evidence around the duplicate and inspect the existing `RequestRegister` handler and caller contract: who sends it, what reply or callback completes it, and whether two requests actually occurred. K29 establishes one launch before two launcher registration messages; it does not show two D-Bus requests or a missing acknowledgement. Crucially, its `[TIMEOUT]` precedes `[REGISTERED]` by 30 ms and the duplicate by 40 ms. Resolve that ordering before spending a roughly 15-minute boot on an invented acknowledgement. If retained evidence cannot decide, the next boot should be one unchanged-behaviour, instrument-qualified run collecting the transaction and the two missing label/PHEV checks together. This beats a speculative handshake patch, a separate label-only boot, and further timer/backend work: it discriminates causes while closing the actual measurement holes. The agreed plan already puts reading before patching and explicitly retires deadline changes. [K29; K28; Agreed §§2–4]

## 2. The handshake hypothesis is plausible, not established

**K29's title and causal conclusion outrun its excerpt.** One launch and two registration log entries strongly support a single-instance problem. They do not distinguish an application retry from duplicate delivery, two launcher callbacks, or registration racing timeout cleanup. The excerpt does not put sender identity, serial, or even PID on either registration message. “Same instance” is a useful inference; “retried because the stand-in never acked” is another, unproved inference. [K29]

If missing acknowledgement causes a retry, I would expect evidence of:

- The first `RequestRegister` entering the stand-in, with sender/app identity and request serial, and no contract-valid completion before the second request.
- A second request from that same client, rather than a second launcher notification for one request.
- A reason for retrying within **10 ms**: an immediate error/retry path or a documented short timer. A conventional unanswered-call timeout must not simply be assumed to explain this interval.

None is reported in K29. An `UNKNOWN`/error record or a client retry diagnostic would support the story, but their absence is only meaningful with demonstrated logging coverage. V46 is the project's own example: rejection-only logging could not distinguish accepted calls from calls never made. Its later zero-unknown result concerns the measured MICOM traffic, not proof that `ApplicationManager.RequestRegister` is handled or mishandled. [K29; V46 §§1–4]

**Falsifier:** a correlated trace showing the first request's contract-valid completion received by the client before it sends the second request falsifies “no acknowledgement caused this retry.” Alternatively, one wire request producing both launcher registration entries falsifies the claimed client retry mechanism. “Completion” must include whatever callback/signal the recovered contract requires, not just a generic D-Bus method return.

My leading competing explanation to test is **late registration racing the timeout/teardown state machine**, with the duplicate guard rejecting an already-entered registration state rather than policing two live processes. The timeout at `23:03:49.566`, acceptance at `.596`, rejection at `.606`, and termination at `.631` make this at least as credible as an unobserved acknowledgement failure. The excerpt also does not establish whether the timeout or duplicate path actually issued SIGTERM. Inspect that call path and compare a warm launch without a preceding timeout. This is a hypothesis, not a replacement certainty. [K29; Agreed §4.3]

## 3. One structural measurement change

**Make every probe go through a small, fail-closed “measurement receipt” wrapper: no validated receipt, no result.** Not another prose checklist. Extend the existing monitor entry point so a probe has to emit, in one retained text record:

1. **Identity and scope:** boot/run ID, target PID plus start time, monitor and target labels, exact instrument/build identity, and active interventions.
2. **A positive control through the same path:** prove it can read a live target label and a known permitted object before interpreting label/PHEV absence. For interception or tracing, demonstrate the intended hook was actually reached; for a binary change, verify the intended bytes/symbol and activation, rather than merely successful installation.
3. **Completion:** operation exit status and stderr, timestamps, and start/end markers plus counts sufficient to detect truncated capture. Preserve the full raw output before filtering it.

If a control fails, the process dies before sampling, or capture is incomplete, emit **NOT MEASURED** and refuse a pass/fail conclusion. Run the control before the event of interest, not after the app is gone. Qualify each new instrument against an instrument-free baseline, one addition at a time; this is already the explicit rule at the top of Current. A successful read is not proof of non-interference. [Current opening warning; K28 checks 1/3; K29 corrections; V46 method note and §2]

This is cheap because it wraps existing commands rather than adding another tracing subsystem. It would have caught the dead-PID label read, denied directory listing, and accepted-versus-never-called ambiguity before interpretation. It cannot guarantee no future mistake; it makes instrument validity a machine-enforced prerequisite instead of an assumption. The supplied documents directly establish those failures and the preload/placement failures; I do not independently reconstruct the other historical instrument failures listed in the brief.

## 4. Order: qualification, discrimination, then a conditional fix

1. **Read first**, as above. Do not interpret an absent `RequestRegister` log without proving that path is logged.
2. **Qualify the monitor**, using a label verified to permit each required observation—not merely a label called privileged, and not a global SMACK bypass. Sample the app while alive. Confirm the exec label, denial coverage, and app-created `PHEVDB`; preserve **NOT MEASURED** wherever observation remains unavailable. The absent denial is a real result, but not a substitute for the missing positive checks. [K28; V50]
3. **In that same next boot**, collect correlated registration requests/completions and launcher transitions, including cold and warm instances if available. No handshake behaviour change yet if its contract/cause remains unresolved. Instrument setup must not silently change the application's security context. [K29; Current]
4. **Only if the transaction proves an omitted completion**, implement the recovered contract in the projection stand-in, then verify the second request/kill disappears and the correctly attributed home frame survives. If it proves duplicate delivery or stale state, fix that projection-side cause instead. Repeating an arbitrary ACK is not protocol fidelity. [K29 hypothesis; V46 §§5–8]

Thus **(b) is a prerequisite inside the discriminating run, not a separate expedition; (a) is conditional, not today's verdict**. Leave the computed deadline alone. No vendor patch is recommended: none of these six documents supplies a duplicate-guard patch offset or establishes that bypassing it preserves lifecycle semantics. Suppressing the guard would trade away real duplicate detection and could hide timeout/state corruption. An offset and that semantic trade would be mandatory before considering such a patch. [Agreed §§2, 4; K29]

## 5. Stopping rule: closer in knowledge, not yet across the line

Tonight narrows the search: the warm path already clears the deadline, authentic labelling removes the specific PHEV denial, and the registration sequence argues against two concurrent launches. Those are reasons to stop revisiting timer constants and broad display infrastructure, not reasons to declare success. [Agreed §4.3; K28; K29]

**The project is closer to a bounded stopping decision, but the adopted attribution condition is not satisfied.** The missing labels were a projection defect; the two missing checks were instrument defects; the proposed handshake defect is another projection mechanism, still unproved. K29 therefore cannot yet count as attribution to a named mechanism *outside* the project's instruments. Nor do these reports demonstrate the security thread's first configuration remediation. The rule requires both threads, or that another run would merely repeat something measured twice. [Agreed §5; V50; K29]

Allow the cheap causal read and, only for evidence it cannot recover, one explicitly discriminating run. If the proposed next boot merely reconfirms the absent denial or the same duplicate log, do not boot: that is the adopted repetition stop, not progress. Do not extend this into MICOM completeness, vCPU tuning, or another screenshot campaign. [Agreed §§3–5; V46 §6]

## 6. Security correction

The directly affected item is **remediation item 1 associated with V-056**, not the `/tmp` trust-anchor remediation. Revised sentence:

> **Validate and restore intended application exec labels and verify SMACK enforcement under those labels; the earlier “SMACK is permissive at 0” conclusion is not established for correctly labelled vendor applications by the unlabelled projection runs, while the observed PHEV denial and the narrow `App::home` rules demonstrate a functioning restriction on this path—not system-wide policy adequacy.**

V50 supplies the `App::home * → ----t-` rule and named-subject access to `Data::commonphev`; K28 reports the denial disappearing after the authentic label setup. Neither establishes every running subject's label. V-065 remains a priority: correctly labelled consumers still trusting `/etc` anchors through writable `/tmp` is a distinct trust-boundary problem, not repaired by this finding. [V50 “Correction owed to the register” and “The vector that remains”; K28; Agreed §4.4]
