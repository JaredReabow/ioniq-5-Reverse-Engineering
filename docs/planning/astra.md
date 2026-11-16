# Independent plan: stabilize one home-screen instance, then prove security boundaries

Prepared 2026-11-06. **Planning only:** no experiments, builds, or code changes were performed. This document is the only output changed. All future actions below are proposals, not results.

## Evidence and precedence

Sources read, in the requested order:

- **[S]** `docs/CURRENT-STATE.md`, lines 1–120.
- **[D]** `docs/vm/45-backend-is-forced-not-chosen.md`, complete; §§54–65 supersede its earlier timeout explanations.
- **[K]** `docs/kernel/25-registration-warm-fast-but-still-killed.md`, complete.
- **[C]** `docs/vm/47-what-the-display-ceiling-blocks.md`, complete, including corrections.
- **[R]** `docs/root-access-paths.md`, complete.
- **[M]** `docs/REMEDIATION-REPORT.md`, complete, including tiers and cross-reference table.

References below point to these files, not to independent inspection of their underlying binaries or logs. Recommendations and hypotheses are explicitly distinguished from reported measurements.

The usable baseline is rebuilt Linux 4.1.27, bochs DRM, native 1920×720, vendor init/rootfs, vendor DRM backend, a serving compositor, and a composited standby presentation. It is **not** the stock kernel or IAS graphics path. The source-tree and nonexistent virtio-GPU recommendations in the older notes are superseded. [D §§16–24, 47–50; C updates 1–5]

Two cautions materially change this plan:

1. Warm registration does not establish survival: 1–8 s registration is followed by SIGTERM. A 15 s PID-stability gate was insufficient. [K; D §§37–40, 64–65]
2. A screenshot does not identify its application. The capture is output-wide; surface 2080 is also assigned to AppCamera, and `STR_CAMERA_ALERT2` was previously attributed specifically to its translations. Treat the reported standby baseline as progress, but prove the client/PID/surface association before calling the next frame “home.” [S, resource-model correction; D §§45, 48–51]

## 1. Critical path to a laid-out home screen

The target is **one identified AppHomeScreen instance displaying Battery and Range widgets at 1920×720 and remaining alive through settling and interaction**. Placeholder values are acceptable for this milestone. Real data is a separate acceptance gate. [S §0; D §§26–27]

1. **Measurement — freeze the successful baseline and preserve its evidence.**
   Smallest version: record the kernel, launcher, input module and compositor configuration identities; retain full launcher and Weston logs plus one actual PNG per run. Confirm socket, client connection, native mode and app-specific surface ownership, in that order. Do not add a CAN preload or invoke placement during baseline establishment. Do not interpret an absent error until its producer has actually run. [S opening warning; D §§8, 19–24, 42–51]

2. **Vendor-binary patch — retain only the justified surface-table substitution; remove the failed timing experiment.**
   Smallest retained change in `/app/bin/AppLauncher`, **file offset `0x475e8`**:
   `71 00 00 00 7a 08 00 00` → `0b 00 00 00 20 08 00 00`, replacing **113→2170** with **11→2080**. Trade: app 113 loses its mapping, and 2080 is shared with Camera; absence of app 113 from recorded logs is not proof it is unnecessary in every workflow. Keep Camera out of this scoped home-screen test and verify ownership rather than trusting the number. Do not extend the eight-entry table into the following string. [D §§45–48]

   Restore the original bytes at **file offset `0x18270`**, `be 30 75 00 00` → `be 10 27 00 00`, if the frozen image contains that experimental patch. Trade: the original 10 s interval returns, so any unrelated benefit of extending that timer disappears; the measured registration deadline was unaffected by this patch. Require exact preimage verification and retain the previously tested image as a control. No further vendor patch is justified by the present evidence. In particular, **the computed 45 s timer has no established patch offset in these reads**; I will not invent one. [D §§54–61; K, Files]

3. **Measurement — attribute the warm kill before changing policy.**
   Smallest version: first read the already-retained launcher window `21:40:33`–`21:40:57`, preserving context before and after it. If it does not establish the causal chain, conduct the single bounded attribution experiment in §2. Require sender, decision path and timer/request provenance, not just another SIGTERM timestamp. [D §65; K]

4. **Projection-side fix — launch warm and satisfy the specific missing contract.**
   Smallest version: let the existing service group settle and request a warm launch through the existing launcher interface; use the measured fast registration rather than trying more vCPUs or enlarging a guessed timer. Then repair only the dependency identified in step 3: for example, supply a missing lifecycle response from the stand-in **if that is what the trace proves**. Prefer the genuine request/response sequence to a global forged `preload_complete_status(true)` or blanket watchdog suppression. If the cause is stale launcher bookkeeping with no usable external reset, stop and specify the actual callsite/offset and semantic trade before proposing a new binary patch. This plan contains no speculative watchdog patch. [D §§33–38, 63–65; K]

5. **Projection-side fix — deliver power-on to the verified live instance, then measure the outcome.**
   Smallest version: after name ownership, successful registration and app-11 surface ownership are established, issue the existing session-bus call to `/Information` on `com.lge.hyundai.avn.appmanager`: `com.lge.avn.appmanager.info.set_power_on_status int32:1 int32:0`. Track that same process identity and surface throughout; a restart invalidates the attempt. The getter reading `1` is not evidence that the event was delivered. Save and inspect frames through the roughly 90–150 s settling window reported on headless; do not assume identical timing on DRM. Acceptance is visible Battery/Range placement, correct client attribution, and survival beyond the observed kill window—not a PNG byte count. [S §0; D §§26–28, 37–40, 51]

   Only after this passes, add input as a separate projection change. The deferred input module allows startup but does not itself prove a seat exists or taps work. Require `VM_INPUT_SEAT_BOUND` and one visible benign UI action; if missing, provision a supported virtual input/seat path rather than altering vendor UI code. Placement, if still necessary, gets its own isolated survival check, not an unconditional call before every capture. [S opening warning; D §§16–18, 39]

## 2. Two terminations: verdict and one decisive experiment

**Working verdict: two termination conditions, but not yet two proven independent implementations.** The cold timeout/duplicate-registration sequence is documented. The warm kill cannot be explained simply as “registration took longer than 45 seconds.” However, a stale group timer, a duplicate-registration flag inherited across relaunches, or a delayed kill request could give one faulty state machine two observable faces. Calling the second condition an independent 24 s watchdog now would repeat the earlier premature timer attribution. [D §§56–65; K]

There is an especially useful alternative clock in [K]: the first two terminations are `21:40:27.199` and `21:40:57.199`, **30 s apart**, whereas the latter is about 23.6 s after registration. This arithmetic suggests testing a periodic or inherited timer, not canonizing “24 s after registration” from one instance. Later lifetime intervals also vary in the reported launch table. This is an inference, not a watchdog identification.

**One decisive experiment: a single cold-to-warm lifecycle attribution capture.** Keep behaviour unchanged and capture the initial timeout and the first warm termination in the same run. Use bounded process/debugger tracing, not a process-wide preload, to record:

- actual SIGTERM sender PID and target process identity;
- sender-side call stack/decision branch and any incoming deregistration request;
- for the relevant Qt timer, object identity, arm/start/stop, interval, caller and callback, associated with the app's launch generation;
- registration and power-state events on the same monotonic timeline.

If both kills originate in the same timeout/duplicate-guard state with an uncancelled old timer or queued request, it is **one mechanism carrying stale state across instances**. If the warm kill comes from a separately armed liveness/state policy or a different supervisor, it is **two**. Sharing the final `kill()` helper proves neither. A sender PID alone is also insufficient. A trace that cannot connect the decision to its timer/request is inconclusive, not definitive. This extends the already successful timer census and the earlier useful userspace trace, without claiming a particular tracing facility is available until checked. [D §§16, 58–61, 65]

**Cost judgment:** reading the retained window is cheapest. The bounded attribution run is more setup than changing one immediate, but cheaper in expected total effort than more vCPU trials, preload-signal guessing or serial timeout patches—all already misleading or unsuccessful. Do not rebuild the kernel merely to obtain a preferred tracer; use available process-level facilities and bound the investigation to these two kills. [D §§31–38, 54–65]

## 3. CAN: ranked routes to real widget values

“Real values” here means the vendor decoder consumes valid raw frames and produces values consistent with recorded vehicle data—not that QEMU has live vehicle telemetry. D-Bus MICOM replies do not feed these widgets. The shipped kernel cannot create its micom CAN interfaces without the absent device/probe path; the replacement generic tree also drops vendor-only micom symbols. [S, transport and ground-truth sections; C update 1]

| Route | Expected cost rank | Stock-fidelity rank | Smallest useful version and limit |
|---|---:|---:|---|
| **Add vcan to the existing rebuilt kernel and replay frames** | **1 — recommended** | **2** | Verify CAN core/raw/vcan support in the actual build, add only what is missing, create a virtual interface named `can0`, and send a small recorded frame set. Keep the vendor CAN consumer unchanged. This preserves the kernel socket API and decoder, not micom transport or physical bus timing. |
| **App-only preload interposition around CAN `connect`/`recv`** | **2 — deceptively small** | **3** | First identify the actual socket/ioctl/bind/connect/read/recv/poll calls; two hooks are not guaranteed sufficient. Scope substitution to known CAN descriptors in AppHomeScreen only. Preserve descriptor ownership, readiness, frame sizes and errors. Never install through `/etc/ld.so.preload`. |
| **Reproduce the SPI/platform/micom device and link** | **3 — major work** | **1, if achieved** | Supply the device/probe and protocol the vendor micom driver expects, on a kernel retaining that driver, then observe its own `can0`. A dummy `can0` name alone is not this route. |

These are engineering cost/fidelity judgments based on the absences in [S] and the available-tree correction in [C], not measured implementation estimates. **The preload route has burnt this project before:** the old process-wide shim substituted socketpairs and overrode `close()`, coinciding with fatal Wayland errors and churn. Limiting hooks to `connect`/`recv` does not by itself eliminate descriptor or readiness hazards. Even a correctly app-scoped shim shares a process with Wayland. [S opening warning]

Smallest acceptance sequence for vcan: establish transport reception, then use the documented **`0x2fc`, byte 7 = 119 → 59.5% SOC** observation; do not invent a Range frame. Recover its encoding from retained evidence before replay. Finally require both widget values to change under two coherent input samples, alongside the documented vehicle relationship (for example 65% / 287 km). Dashes and a pre-data 0% / 0 km are not success. Add CAN only after the no-instrument display baseline survives. [S, transport and ground-truth sections]

## 4. From 26 remediation items to a defensible advisory

Keep the 75-entry register as the evidence ledger, but do not publish 26 equally proven exploitation claims. The 26-item count includes **3b**; [M]'s final “13 + 11” tier summary is stale relative to its cross-reference table. Organize the advisory by security boundary, with separate **artifact fact / projected demonstration / unit verification / conditional impact** fields. The report already states that nothing has been tested on a vehicle. [M, cross-reference and scope]

### Demonstrations to prioritize

1. **V-059 / item 7: first priority for an end-to-end entry-path claim.** On authorized, recoverable hardware or an accurately reproduced updater path, show genuine-current bytes passing verification and authentic older bytes being consumed at apply, with source identities, phase timing, resulting partition/version and post-install boot result. Include unchanged-media and rejected-modification controls. The report's separate-read mechanism supports a strong keyless-downgrade hypothesis; it does **not** settle every downstream rollback or boot check. Keep arbitrary-content installation separate: it requires TE2 material absent from the package. Do not call this arbitrary code execution from USB. [M item 7; R routes 1 and 12, §9]

2. **V-069 / item 19: highest-priority persistence/trust-anchor demonstration.** Show SCOMO actually reads the writable CA and uses it for package acceptance, then a benign research-signed navigation payload accepted only after that CA is replaced. A failed-signature control with the original CA is essential. Demonstrate execution/reboot persistence only if that stronger consequence is claimed. State the prerequisite **root or equivalent write access**; this is not an initial foothold. The old display failure no longer justifies abandoning the attempt, but SCOMO startup itself remains unverified on the repaired path. [R route 0; M item 19; C blocked-items table; D §§19–24]

3. **V-071 / item 21: demonstrate fail-open eligibility, not login bypass.** Show the marker/account-shell/agetty chain and compare secure, insecure and missing/unreadable MICOM-state cases. Show the fixed image fails closed while legitimate service mode still works. The missing Dropbear binary and absent private credential must remain explicit: SSH eligibility is not a working SSH server or authenticated root access. [M items 5, 18, 21; R §§1, 8]

4. **Reuse, rather than rediscover, the existing benign demonstrations:** V-048 (replacement verification key), V-051 (caller-selected launch), V-054 (uid-0 account), V-053 (encryption key with wrong-key control). Package their evidence and test the proposed fix. Each requires an explicit starting UID and access conditions. Root-only session-bus access makes V-051 a root-to-root execution primitive, not a local privilege escalation. [M items 2, 8, 9, 11; R §§3–4]

### Disposition of every item

| Items / register entries | Advisory treatment |
|---|---|
| **7 / V-059; 19 / V-069** | Prioritized end-to-end work above; conditional impact until proved. Split V-068 embedded-key evidence from V-069 CA consumption. |
| **2 / V-054; 8 / V-051; 9 / V-048; 11 / V-053** | Preserve existing demonstrations and exact privilege scope; add fixed-image negative controls. Encryption's actual factory engagement remains a separate unit question. |
| **5 / V-049; 21 / V-071** | Demonstrated console/eligibility plus fail-open configuration; no password bypass. |
| **1 / V-056; 4 / V-052** | Configuration/boot-policy findings with explicit physical-unit validation: archive extraction loses xattrs, and projection labels/partition state do not establish fleet posture. |
| **3 / V-055; 3b / V-058; 6 / V-042; 16 / V-065** | Writable-state trust-boundary family. Report exact ownership, modes, creation races and consumers; avoid four overlapping severity claims. Marker-triggered services are not end-to-end proven. |
| **14 / V-063; 15 / V-064; 22 / V-072** | Policy and least-privilege findings. V-064 is an impact multiplier, not a standalone exploit; mDNS network reachability still needs proof. Prioritize platform hardening without waiting for a parser exploit. |
| **10 / V-014; 18 / V-067; 23 / V-073** | Shipped dangerous capabilities, not demonstrated exposed services. Require actual trigger/listener/interface and authentication evidence before claiming remote access. |
| **12 / V-060; 13 / V-061** | Bound engineering-mode signal reachability by the state gate and lack of a shell-bearing menu. Bound the integrity oracle by root-only session-bus access; neither is a demonstrated foothold. |
| **17 / V-066; 19 / V-068** | File/key configuration facts. Verify the navi read-write window and permissions under the intended attacker UID; establish what embedded keys authenticate before assigning fleet/backend impact. Public keys are not private credentials. |
| **20 / V-070** | Conditional persistent-script execution; preserve the failed trigger test. Do not spend the first advisory cycle proving this lower-priority root-required route. |
| **24 / V-074** | Proven VIN-in-log privacy finding; backend transmission remains unobserved. Redact identifiers from disclosure evidence. |
| **25 / V-075** | Userspace verification gap and bootloader-assessment request, **not** proof secure boot is absent. Destructive boot tests require a recoverable unit and platform participation. |

**Correct a material evidentiary trap before publication:** `/tmp` mode `1777` permits file creation; it does not automatically permit modifying every existing root-owned file or replacing it through the sticky directory. The statements in [R §3] and [M items 2, 16] need actual target modes, ownership, create-before-owner races and a non-root reproduction before becoming escalation claims. A root-performed account append proves the consequence of write access, not that an arbitrary lesser user has that access. This is an independent review judgment from standard filesystem permission semantics applied to the reported evidence.

### What the platform team needs to act

For each fix family, provide the exact firmware identity, affected paths/functions, preconditions and attacker capabilities, evidence hashes and complete excerpts, projection substitutions, bounded impact, reproduction controls, proposed fix owner, and a before/after acceptance test. Keep sensitive credentials and customer identifiers out of the public package. [M scope, verification sections and cross-reference]

Deliver two work queues:

- **Immediate configuration containment:** move generated trust/configuration files into protected directories; invert the console default; remove dormant debug services/credentials; restrict bus writers; pilot least privilege on one low-dependency service before broad rollout. Validate directives against the shipped service-manager version and actual shared-file dependencies rather than assuming every modern hardening directive works here. [M Tier 1, items 10, 18]
- **Release/architecture fixes:** bind verification to the exact installed bytes, anchor keys outside attacker-writable state, provision device credentials, and obtain the bootloader's verification/rollback policy. Merely hashing while irreversibly writing executable content is insufficient unless failed verification prevents activation; protected staging or an inactive verified slot needs an explicit commit rule. [M items 7–9, 19, 25]

The platform team can accept configuration findings without an exploit video. It cannot responsibly accept a downgrade, signature-bypass or remote-root headline without the relevant boundary being crossed and the fixed build refusing the same attempt.

## 5. What I would cut

**Primary cut: full micom/SPI emulation for this milestone.** It has the best theoretical hardware fidelity, but requires recovering device/probe/protocol behaviour and retaining vendor-only kernel support just to supply a few CAN frames. The project already accepts a replacement display device/kernel. vcan preserves the relevant vendor decoder and socket contract at much lower expected cost; pursue micom emulation only for a separately funded hardware-fidelity goal. [S transport section; C update 1]

Also cut from the immediate queue:

- More display-backend switching, virtio-GPU attempts on 4.1.27, vCPU sweeps, and guessed timeout immediates: those premises were already refuted. [D §§16–24, 33, 56–65; C update 5]
- Blanket preload/placement automation and global preload-complete forgery: too much observer interference or hidden lifecycle substitution for too little causal evidence. [S opening warning; D §§35–40]
- Password cracking, blind filesystem mutation and engineering-menu shell hunting as prerequisites for the advisory: the reported work either found no defect, has no demonstrated entry path, or establishes menus rather than execution. The strong trust-boundary findings do not depend on those detours. [R §§1–2, 5–7]
- More vulnerability-count growth before evidence consolidation. Close the two highest-value chains and publish bounded configuration findings; do not turn unmeasured reachability into severity by accumulation. [M scope/cross-reference; R conclusion]
