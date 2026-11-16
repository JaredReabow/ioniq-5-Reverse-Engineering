# C2: measure the manager, not another standby frame

## Evidence boundary and verdict

This is a consultation, not a run. Only the six requested documents were read for repository evidence. No experiments, git operations, or other repository writes were performed. References:

- **[K31]** `docs/kernel/31-warm-survives-registration-name-unowned.md`
- **[K32]** `docs/kernel/32-close-test-negative.md`
- **[V52]** `docs/vm/52-the-one-number-that-decides-it.md`
- **[Agreed]** `docs/planning/AGREED-NEXT-STEPS.md`
- **[Postrun]** `docs/planning/astra-postrun.md`
- **[Trust]** `docs/trust-anchors-in-writable-runtime-paths.md`

**The last run did not test address equality. It compared two absences. Do not spend another boot doing that.** It did establish that the early manual manager start failed to produce ownership on the checked bus; without startup output or connected-bus identity, it did not establish why. [K32]

Warm + authentic labelling has produced survival at 60 seconds with no recorded PHEV denial. Both recent runs still report duplicates. Do not describe the current warm instance as necessarily killed by that duplicate: those same excerpts say it survived. Cold startup loses the measured 39.8-second deadline; warm startup historically takes 1.17–8.13 seconds. These are reasons to freeze warmth and labelling, not reopen timer tuning. [K31; K32; V52]

The brief supplies the static identification of the vendor registration interface and its argument names. These six documents do not reproduce that recovery or define the numeric `result` contract, especially deregistration. Treat those details as supplied premises, not independently verified ABI evidence. Likewise, **unowned on the queried bus is measured; a stale/wrong address causing it is not**. [Trust]'s final section presents that causal connection too confidently in light of [K32].

## 1. The next run: exactly three ordered captures

The following timing limits are proposed experiment budgets, not vendor constants. Use guest monotonic time for event intervals and a host monotonic watchdog for a stalled guest. Give startup **300 guest seconds, capped at 30 host minutes**. Poll process/ownership state every **one guest second**; retain continuous logs and bus events between polls. Every command has a **five-host-second** deadline and records timeout separately from a valid negative reply.

### Before boot: qualify the collection path

Prepare collection in the projection launch scripts, **before** launcher/manager execution—not by attaching after their interesting output has disappeared. Retain launcher stdout/stderr (including `/tmp/applauncher-stdio.log` where applicable), manager stdout/stderr, service/journal output if used, kernel output, process lifecycle, and bus traffic. Do not add a process-wide preload or change vendor code. The existing receipt principle is mandatory: run ID, binary/instrument identities, active changes, labels, start/end markers, command status/stderr and loss/truncation accounting. Preserve raw output before grep. [Postrun §§3–4; Agreed §4.2]

A capture wrapper must emit a pre-exec marker through the actual stdout and stderr destinations, record the resulting PID/start time, and retain exit status/signal. Verify any child-specific descriptor redirection rather than assuming launcher stderr includes manager stderr. An empty manager stream is meaningful only when descriptor continuity and process lifetime are established; it is not permission to invent a startup error. If this cannot be arranged, **do not boot the diagnostic attempt**. [K32; Postrun §3]

### Capture 1 — startup, both bus identities, and manager ownership

Start collectors before launching the vendor stack. Preserve the normal launcher-driven app-id-2 start; **do not manually start a second manager at +10 seconds**. Record:

1. Creation/replacement times, exact address contents, symlink status, owner, mode and inode for `/tmp/session_appmgr` and `/tmp/session_appmgr.env`; record the bus producer's command, environment and output. Treat the two files as separate objects, not interchangeable spellings. [Trust, final section]
2. Launcher and manager exec/exit events, executable, arguments, PID **and start time**, parent, UID, actual SMACK label, environment address, and stdout/stderr from first instruction observable by the wrapper. Detect every incarnation, not just the final `pgrep` match. [K32; Postrun §3]
3. As soon as each relevant bus exists, collect ownership changes and relevant method calls, returns and errors. Qualify bus monitoring using a harmless test client's private test-name acquisition/release and a known daemon method call; verify these appear in the retained trace. Do not use the real registration name for this control. Missing wire events are interpretable only after this control passes. [Postrun §§2–3]
4. **Only after both real processes have appeared**, snapshot their addresses together, retaining the preceding timeline. Query each distinct reachable address explicitly, not the probe shell's implicit `--session`: daemon `GetId`, `NameHasOwner` for `com.lge.avn.appmanager.registration`, and, if owned, `GetNameOwner` plus owner PID/UID. Associate launcher and manager unique connections with their PIDs as well. Environment strings alone do not prove where a binary actually connected: [Trust] documents direct file readers. Equivalent address strings are not required if daemon identity is the same.
5. Correlate manager connections and `RequestName` calls with replies/errors and subsequent ownership. Keep tracing through capture 2. If no ownership appears, retain at least **60 guest seconds after manager exec**, within the startup budget; if the manager exits earlier, retain its exit and output instead. Do not claim a startup cause from silence alone. [K32; Postrun §§1–3]

**Every null has a defined answer:**

| Observation | Permitted conclusion |
| --- | --- |
| No launcher or no manager by the startup deadline | That process never became observable in the declared window; identify the last launch/service transition. Address comparison is NOT MEASURED. |
| Manager execs then exits | Startup failed before sustained service; report exact exit/output and any bus activity. |
| Different connected daemon IDs | Split-bus topology is measured. Which producer/reader supplied each address is the next causal check. |
| Same connected bus; `RequestName` rejected or errors | Name acquisition failed with the retained concrete reply/error. |
| Same bus; manager stays alive; qualified trace contains no request | Manager did not request this name during the bounded observation window. Its startup/registration path, not address inequality, is now the question. |
| Name belongs to another PID | Identify the competing owner; do not silently replace it. |
| Required logger/monitor fails | INSTRUMENT FAILURE, not a vendor negative; retain the failing receipt and stop this attempt. |

This cannot guarantee that the vendor explains itself. It does guarantee that “nothing happened” becomes a bounded process/connection/request result—or an explicit failed instrument—not another false address match. [K32; Postrun §3]

### Capture 2 — one managed warm registration transaction

After capture 1 establishes the topology, let the cold instance be the recorded pre-warm. Record its actual lifecycle rather than killing by a guessed elapsed time. Request **one** warm relaunch through the launcher's interface, as in [V52]. If the cold instance never exits, use a documented launcher stop if available and record it; otherwise end this phase as blocked rather than quietly substituting an ad-hoc kill. No restart loop and no stand-in in this diagnostic run.

From before the launch request until **60 guest seconds after registration**, retain:

- app 11 PID/start time and label; launch request and response;
- registration destination, path, interface, member, typed arguments, sender unique name/PID, message serial and correlated reply serial/error;
- any launcher notification/callback and the ordering of `[TIMEOUT]`, `[REGISTERED]`, duplicate error, finish/exit and power-on events;
- daemon ownership at the announce, not only at boot;
- app stderr and kernel denials/crash records throughout. [V52; K31; Postrun §§1–4]

Set a **60-guest-second post-launch deadline** for a registration outcome, then record failure and the still-live/dead process state. If the name remains unowned, one observed announce/error plus its launcher consequence is enough; repeating warm launches cannot teach anything. If capture 1 never obtains the required processes, emit capture 2 as **BLOCKED_BY_STARTUP**, with the causal receipt. [K32; Agreed §5]

### Capture 3 — power-on, attributable surface, and machine-checked layout

With the same warm PID identified and alive, capture the pre-power state, issue **one** `set_power_on_status` using the established contract, and retain the call result and delivery evidence. A successful shell exit alone is not proof the application consumed the transition. Observe for **30 guest seconds**, then take a second identity/surface/layout sample at registration +60 seconds, or later if needed to preserve the full power-on observation window. [K31; K32]

Collect launcher surface assignment, compositor surface inventory, client ownership, visibility/layer/geometry, and frame presentation/buffer evidence for that surface. Save raw pixels as supporting data, not as the verdict. When registration is still broken, this is a bounded negative control; when the app never existed, emit **BLOCKED_BY_STARTUP** instead of a meaningless screenshot. [Agreed §1; K32]

The screen verdict is the predicate below. A 129,844-byte image, a live PID, or an arbitrary non-black frame never passes it. [K31; K32; Agreed §1]

## 2. Stand-in verdict: reject plausible success; permit a bounded adapter

**No to “return plausible results and see the screen.” Conditional yes to a separately labelled, narrow projection adapter after the vendor-startup run.** A name owner is not necessarily an implementation of the lifecycle contract. The earlier consultation specifically requires recovered completion semantics, not an invented ACK. [Postrun §§1–4]

Before implementing it, recover the exact signatures, result values, duplicate/not-found behaviour, and required callbacks/signals from the vendor caller/callee evidence. The supplied five argument names do not supply those semantics. If these remain unknown, the adapter must report unsupported/error rather than success. A display obtained through speculative replies is a **stand-in-assisted rendering experiment**, not proof that the vendor manager works.

The adapter must:

- Acquire the registration name without replacement or queueing to take over later; refuse to start if the real owner exists. Make its identity visible in every receipt.
- Keep real, sender-bound registration state. Return success only after the documented operation and completion actually occurred. Handle deregistration and client disconnect according to recovered semantics, not by always returning zero.
- Reject unsupported methods, malformed registrations, conflicting live identities, and cross-client deregistration. Log accepted calls as well as rejected ones, with serials and completion. If a validation rule is a projection restriction rather than vendor behaviour, label it as such.
- **Never fake** app liveness, successful vendor registration, preload completion, power state consumption, layout completion, surface ownership, absence of a crash/SMACK denial, or security authorisation. Do not manufacture a “home ready” signal just to satisfy the screen test.
- Remain a separate opt-in process, not a global preload, launcher duplicate-guard bypass, or compositor intervention. Keep vendor-only and assisted results separate. [Postrun §§2–4; Agreed §§2–4]

Prefer fixing a demonstrated projection ordering/address defect and running the real manager. **No vendor patch is recommended.** The read documents supply no duplicate-guard/name-acquisition patch offset. Any future proposal must give binary identity, exact file offset and original/replacement bytes, and state its semantic trade. Bypassing the duplicate guard sacrifices real duplicate detection; extending the deadline changes lifecycle timing without explaining an unowned name. An unknown offset is a reason not to patch, not an invitation to guess. [Postrun §4; Agreed §4.3; V52]

## 3. “We actually got the laid-out screen”: an executable acceptance predicate

Require **all** of the following, with retained machine-readable inputs:

1. **Identity:** the launcher assigns app 11 the selected non-colliding surface ID (the agreed candidate is 1010); that ID exists exactly once, and the compositor client is tied to the same AppHomeScreen PID/start time. An environment variable alone is not ownership proof. The prior `11 -> 2080` collision with camera app 12 explicitly invalidated earlier display claims. [Agreed §1]
2. **Presentation:** that surface is mapped, nonzero-sized, visible on the intended output/layer, and contributes a newly presented buffer after the delivered power-on transition. Another surface covering it, or only a committed offscreen buffer, fails the display criterion. [Agreed §1; K32]
3. **Home-layout content:** before the run, freeze a machine-checkable manifest of at least two home-specific UI elements and their spatial relationship, grounded in the actual home assets/layout. Check them in the attributed surface pixels by template matching/OCR with predeclared thresholds, or in a trustworthy exported UI tree plus presented-buffer evidence. Include standby and camera as negative controls; `STR_CAMERA_ALERT2` is an explicit rejection marker but its absence is not a positive home test. Do not learn the expected answer from the run being judged. [Agreed §1; K31; K32]
4. **Persistence:** the same identity, presentation and home-layout predicate hold at the later sample, with no intervening duplicate error, app restart or PHEV denial in qualified captures. [V52; K31]

**These documents do not provide the home-element manifest, pixel thresholds, or proof of an available UI-tree export.** That preparation is a prerequisite, not something this note pretends already exists. Until it is available, report **ATTRIBUTED HOME SURFACE PRESENTED; LAYOUT UNVERIFIED**, never “home screen works.” Likewise report layout success and registration health separately if either fails. This is stricter than a PNG inspection precisely because the project has already withdrawn a camera-derived claim. [Agreed §1]

## 4. Security: share the evidence plumbing, not the success criterion

Capture 1 cheaply provides the address-file provenance and connected daemon identities needed for V-058. **It does not prove malicious redirection simply because the display is broken.** [Trust] establishes readers and a writable-path design; [K32] does not establish that the manager reached a different bus. Also, directory mode 1777 alone does not establish that an arbitrary non-root attacker can overwrite an existing root-owned file: file permissions, sticky-directory rules and MAC still require measurement. Do not carry [Trust]'s older unlabelled-process MAC conclusions into this correctly labelled run; [Postrun §6] expressly corrects that reasoning.

Recommended sequencing:

1. Finish and retain the three unmodified-behaviour diagnostic captures first.
2. If they prove an address/order defect, repair projection startup: one known bus, pinned daemon executable, a readiness dependency, no fallback to another bus. Put authoritative address state in a protected directory, use safe creation/opening and reject symlinks, wrong ownership/mode, absent/stale/unreachable endpoints. Metadata checks followed by a separate pathname read leave a race; mode 0600 alone does not solve unsafe replacement. Legacy `/tmp` readers need protected publication/namespace arrangements or remain an explicit limitation. These are proposed improvements to [Trust]'s configuration-first remedy, not demonstrated fixes.
3. Use an **isolated disposable test phase**, after display evidence is sealed, to compare a real original reader with the hardened launch path. Supply a local, inert alternate bus/address and record whether the original reader connects to its distinct daemon ID. Repeat with the hardened path and require explicit refusal **before vendor exec/connection**, then verify valid input still connects to the intended bus. Never redirect the running display stack or counterfeit registration success. Use a private filesystem/mount view if available; otherwise defer this A/B to a disposable restored guest rather than mutate live shared anchors.

The cheap proof is **original consumer follows substituted address / hardened consumer refuses / valid address works**, using the same topology receipt. Bad-mode, symlink, missing and stale-input cases can test robustness without running the whole HMI. A wrapper-only test proves the wrapper, not vendor susceptibility. A root-driven substitution proves routing behaviour, not a non-root exploit; record injector UID/label, file permissions and the allowed threat position separately. If isolation or a genuine reader cannot be obtained cheaply, stop at configuration evidence. [Trust, V-058 and final section; Agreed §§4–5]

Thus display completion and security demonstration get independent verdicts. Neither a working screen nor refusal of an invalid file alone proves the vulnerability or its complete remediation. Root-peer compromise is also not solved by merely making a root-owned file 0600. [Trust, “The same gate keeps appearing”]

## 5. Blocker-specific stopping rule

**Authorize one instrument-qualified vendor diagnostic run, not another open-ended screenshot campaign.** Then apply this decision table:

- **CLOSE the registration blocker** only when the intended vendor owner is identified on the app's actual bus; the warm app's correlated transaction completes before the 39.8-second fallback; there is no duplicate/timeout fallback; and the same labelled app survives through the post-power-on 60-second check. Screen/layout acceptance remains a separate verdict. [V52; K31; K32]
- **CONTINUE once with a targeted projection correction** only if that run names a new, testable mechanism—wrong bus, failed dependency/exec, concrete name-acquisition error, competing owner, or evidenced omitted completion—and states the exact changed variable and expected contrary observation. A cheap retained-log/contract read is allowed before deciding. [Agreed §5; Postrun §§1–4]
- **STOP vendor boot iteration as BLOCKED** if qualified captures show the same unowned-name/duplicate result without a new discriminant. A live manager that never requests the name justifies one bounded startup-path read, not another unchanged launch. If the read cannot name a corrective experiment, stop. [K32; Agreed §5]
- **An instrument failure is not a vendor attempt with a negative outcome.** Repair the exact collection failure and demonstrate its control without another full HMI boot where possible; no full rerun until collection is qualified. [Postrun §3]
- **An assisted screen closes only an explicitly assisted-display milestone.** It never closes the vendor-manager blocker or counts as V-058 evidence. If the adapter requires fabricated lifecycle/layout/security success or unknown result semantics, stop the adapter too. [Postrun §4; Agreed §§1–2]

The continuation ticket must contain a retained evidence pointer, a named mechanism, one change, and a falsifier. **No ticket, no next boot.** Reconfirming survival, absence of the same denial, or another 129,844-byte standby frame is not progress. [K31; K32; Agreed §5]
