# Astra C5 — validate the observer before changing the surface ID

Read-only post-run consultation. No experiments, builds, guest actions, or git operations performed; this document is the only write. References below identify files actually read; proposed measurements are not reported results.

## Bottom line

**Do not make 1010 → 2170 the next decisive test with the present monitors frozen.** The listing tool has a concrete synchronization defect, the probe does not implement PID-to-surface attribution, and the retained run changes Home PID between power-on and Gate 5. Keep Gate 2's ApplicationManager consumption result, but do not promote this Gate 5 null into proof that Home never creates a surface. [E, L, P]

The strongest new finding is projection-side: `ivi_place --list` binds `ivi_controller` inside its registry callback, but prints its inventory and disconnects after only the initial registry roundtrip. That roundtrip's sync request precedes the bind generated while dispatching registry events; its completion does **not** guarantee receipt of the bind's screen/layer/surface announcements. A second, post-bind roundtrip is required before treating those counts as an inventory. This is a source-level defect capable of producing the observed all-zero result, not a demonstrated explanation of this particular deployed executable: verify the staged binary's provenance before calling it the runtime cause. [P, §§registry_global, roundtrip_timeout, main]

## Evidence key

- **[K35]** `docs/kernel/35-gate2-closed-gate5-no-surface.md` — reported Gate 2/5 results and stronger causal conclusion.
- **[V56]** `docs/vm/56-endgame-runbook.md` — required PID/start-time identity chain and five-term `HOME_FRAME` predicate.
- **[K34]** `docs/kernel/34-label-measured-warm-registers-in-time.md` — measured `App::home`, warm PID 2516 registering in time in boot55.
- **[V55]** `docs/vm/55-the-duplicate-is-not-the-killer.md` — duplicates survivable; healthy historical Home registration.
- **[E]** `work/vm/kbuild/ws/partimg-build/endgame.sh` — actual Gate 5 implementation.
- **[L]** `work/vm/kbuild/boot56-end.log`, especially lines 971–1008 — retained run excerpt.
- **[P]** `tools/uk_fw/ias_backend_soft/ivi_place.c`, especially lines 440–603 and 795–839 — announcement callbacks, registry bind, sync, list-only exit; introductory comments also distinguish ID namespaces.
- **[U]** `work/weston-source-1.10/full/clients/ivi-shell-user-interface.c`, lines 916–940, 1120–1170, 1283–1316 — reference implementation of shell widget creation and offset.
- **[H]** `work/weston-source-1.10/full/ivi-shell/hmi-controller.c`, lines 925–1009 — matching reference background/panel lookup arithmetic.
- **[I]** `work/vm/kbuild/ws/partimg-build/weston_1920.ini.drm` — staged configuration, shell widget IDs and modules; not proof of the runtime-selected file.
- **[X]** `work/weston-source-1.10/full/protocol/ivi-application.xml` — reference distinction between a `wl_surface`, its IVI role/ID, and collision/role errors.
- **[A]** `docs/planning/AGREED-NEXT-STEPS.md` — withdrawn Camera-derived compositing claim, vendor table, projection-first and stopping discipline.
- **[K27]** `docs/kernel/27-segv-is-phev-smack-denial.md` — 1010 patch, unreconciled 1005, label denial, reverted deadline edit.
- **[K21]** `docs/kernel/21-standby-persists-preload-race-remains.md` — earlier duplicate-2080 history and unstable PID chain; ownership conclusions superseded by [A].
- **[B]** `work/vm/kbuild/ws/partimg-build/both-halves.sh` — earlier selector, placement, timing and capture implementation.
- **[T]** `docs/vm/45-backend-is-forced-not-chosen.md`, §§45–46 — table offsets and launcher environment caveat; historical causal claims are not adopted here.
- **[Q]** `tools/uk_fw/ias_backend_soft/qt_env_shim.c` and `setenv_surface_id_shim.c` — historical research instruments and their documented environment/forced-ID hypotheses, not proof they are currently loaded.
- **[C]** `docs/CURRENT-STATE.md`, opening sections — reported underscore string and current interpretation; historical warnings about placement and preload instruments.

## 1. The single decisive experiment

### Replace the numeric swap with one PID-bound surface-boundary audit at 1010

**Question:** Does the surviving, labelled, timely-registered Home process create a core Wayland surface; does it request an IVI association; and what happens to that request and its buffers?

This is a proposed experiment, not work performed in this consultation:

1. Repair only the projection-side observation path: complete a post-bind roundtrip, report errors/timeouts separately from empty results, and validate the inventory against a contemporaneously known live surface on the same compositor/socket. Do not use a historical log entry as that positive control. Obtain client credentials and the actual core-surface/role association rather than infer ownership from numeric IDs. The current tool has no such ownership fields. [P, V56]
2. Prefer inspecting the already-running guest first: a corrected live inventory may immediately find Home, avoiding even an app restart. To establish **absence of creation**, however, the observation must cover creation, not just attach after it: observe one warm launch from before its connection through power-on and the persistence interval, keeping ID 1010, launch mechanism, label, libraries, configuration and power-on sequence fixed. Use projection-side compositor diagnostics or a supported debugger/protocol observation route; do not silently substitute a standalone launch or global preload shim. [E, V56, Q]
3. Record one chain: executable + PID/start time → `wl_client` credentials/socket → `wl_compositor.create_surface` → IVI `surface_create` request and actual ID → accept/error/destroy → attach/commit → layer/output presentation. Include unroled/non-IVI surfaces and all Home connections; a filtered IVI inventory alone cannot prove no core surface. Observe creation/destruction over time rather than grep a cumulative log. [V56, X, E]
4. Keep the D-Bus monitor; verify timely registration and label for **that same process**, and verify its continuity through the power event and ten-second persistence check. Abort causal interpretation on replacement, incomplete tracing, protocol errors in the observer, or failure to enumerate the positive control. [V56, K34, L]

**Pre-committed interpretation:**

| Result | What it establishes, and what it does not |
|---|---|
| Home already has a core/IVI surface, possibly under another ID | “No surface” was an inventory/identity failure. Follow the actual mapping; an unlisted or transformed surface is not evidence of an invalid requested ID. |
| Home requests IVI creation and the server rejects it for a recorded collision/policy/role reason | Creation was attempted; classify the specific rejection. Only an ID-specific reason supports an ID-validity diagnosis. |
| Home has a core surface but never requests an IVI role | A client integration/role-selection boundary, not proof that the app creates no surface. |
| Home has an accepted IVI surface but no new non-null buffer commit | Surface creation works; the next boundary is rendering/commit, not ID allocation. |
| Home commits a new buffer but it is not presented | Investigate projection placement/visibility/output routing with that proven identity; this is the branch in which “draws where nothing reads” becomes supportable. |
| Complete observation from launch sees no Home `create_surface`, with correct connection/process coverage | Home creates no compositor surface **during this measured warm configuration and interval**. This does not prove an inherent app limitation or explain the upstream reason it never requests one. |
| Process changes, the control is missing, or coverage starts late | Inconclusive; do not turn observer failure or a snapshot into a no-creation finding. |

This is one boundary-localization experiment, not an ID sweep. If the existing session cannot support complete observation without a compositor restart, retain that limitation rather than spend a boot on another uninstrumented screenshot.

### Why the proposed 2170 swap is useful but not decisive as stated

2170 is a better collision-avoidance candidate than Camera's 2080, but its presence in a launcher table is **not** evidence of a compositor whitelist, nor proof that it is free in every live namespace. [A, T, X]

- **A PID-attributed Home surface appears only after changing to 2170:** consistent with ID-dependent behavior in this configuration, provided actual child input, mapping and lifecycle are verified. It does not alone distinguish allocation rejection, shell policy, client branching or timing, and does not establish `HOME_FRAME`.
- **No surface appears in the same existing lists:** establishes only another listing null. It cannot distinguish “no creation request” from rejection, transformation, hidden/unroled surfaces or the observer defect.
- **A request for 2170 is observed and rejected:** diagnoses that request's failure; it does not establish that 1010 was invalid.
- **An unrelated surface appears, or Home's PID changes:** not evidence for the hypothesis.

If an ID substitution is subsequently justified, prefer a verified per-Home projection launch-environment assignment that survives the launcher's environment construction. Do not use the historical unconditional `getenv`/`setenv` shims as a global fix: they force a common ID and can change other clients. [T, Q]

**Vendor patch ledger, if that fallback is chosen:** existing AppLauncher row at file offset **`0x475e8`** is `0b 00 00 00 f2 03 00 00` (11→1010); change only the little-endian surface word at **`0x475ec`** from `f2 03 00 00` to `7a 08 00 00` (11→2170). The original row was `71 00 00 00 7a 08 00 00` (113→2170): app 113 remains displaced, and its absence in prior runs does not make this free space. Verify artifact bytes before applying; leave the reverted deadline at **`0x18270`** untouched, do not extend the table, and never restore the Camera collision. No patch is made or recommended before the observer audit. [K27, T, A]

## 2. What `surface_id_offset` most plausibly means

**Best supported reading: a stride for the shell UI's own per-screen widgets, not a universal application-ID remapper.** In the available Weston 1.10 reference source, `surface_id_offset` is a struct field loaded from the configuration key **`surface-id-offset`**, default **10**; background and panel IDs are computed as `base_id + screen_index * offset`, then passed to `ivi_application_surface_create`. The companion HMI controller looks up exactly those computed IDs. [U, H]

The reference's 1002 panel, 1005 fullscreen button, and other 100x IDs also occur explicitly in the staged configuration. Consequently 1005 is not, by itself, evidence of Home remapping; nor do the irregular vendor table values 1030/2080/2110/2160/2170/2200/3000 reveal one arithmetic transformation. [U, I, T]

**Limits:** the reported binary string uses an underscore; the reference configuration key uses hyphens, and this source has not been proven identical to the shipped vendor implementation. The string alone neither proves global remapping nor supplies a numeric offset. In particular, do not blindly subtract 1000 or apply the reference's stride to Home. [C, U]

Read to confirm, in this order:

1. The actually loaded Weston configuration and exact `weston-ivi-shell-user-interface` artifact; follow the string's code references into its configuration read, default and callers. Determine whether only shell widget creation consumes it. [I, U provide the concrete comparison targets.]
2. The actual Qt IVI integration/platform-interface path consuming `QT_WAYLAND_SET_SURFACE_ID`, `QT_WAYLAND_SET_SURFACE_ID_FORCED`, and any PID fallback; trace the value through arithmetic/window counters to the protocol request. The historical shim comments identify these as relevant inputs, not a currently verified prerequisite. [Q]
3. The actual server's `ivi_application.surface_create` handler and layout/ID lookup, plus controller enumeration; distinguish requested ID, protocol object ID, core `wl_surface`, and IVI layout ID. [X, P]

There is a separate historical clue: `ivi_place.c`'s introduction reports AppNavi env value 3000 yielding IVI ID 30000. Treat that comment as a lead to a client-side transformation, **not proof of ×10 for Home**, and not proof that the observed 30000 is shell-owned. Neither the Gate 5 grep nor the current listing establishes any of those owners. [P, E]

## 3. What changed, and the cheapest no-boot read

First, **the earlier surface was never reliably attributed to Home**. Its selector took the last logged ID outside a short exclusion list; it did not query client ownership. The repeated 2080s were accumulated log matches, not a simultaneous PID-bound live inventory, and [A] withdrew the Camera-derived compositing claim. Cold versus warm therefore is not yet a before/after regression in Home surface creation. [B, K21, A]

Second, the current retained run contains a more immediate identity discontinuity:

```
WARM_PID=[2397]
POWER_ON_SENT
... power_status int32 1 ...
APP_PID_AT_GATE5=[2561]
CAP ... pid=[2561]
```

This preserves ApplicationManager's Gate 2 receipt, but it does **not** prove that PID 2561 was the same warm instance present when power-on was sent or that it consumed/replayed that state. [E] waits for any PID, not registration; its Gate 5 comment promises identity but never resolves `wl_client` credentials; its screenshot command has no PID selector. The measured label/registration in [K34] belongs to boot55 PID 2516. Accept the reported healthy lifecycle milestone, but do not stitch these different PIDs/runs into the missing same-run identity chain. [L, E, K34, V56]

**Cheapest next work is an offline comparison of retained raw logs and probe/configuration files**, not a boot: reconstruct launch/register/exit and power-event ordering per PID in the earlier and current captures, retaining the exact app-ID delimiter (the old grep also matched AppID 110). Compare actual child environment and loaded IVI/Qt plugins if retained, then stderr for connection, role, buffer and protocol errors; compare placement calls and instrumentation too. [K21, B, E, Q]

If complete tracing really confirms no warm Home surface, plausible differences to discriminate are: early cold/transient window versus later warm hidden/preload state; replacement after power-on with different replay behavior; changed effective IVI environment/plugin path; or the earlier surface belonging solely to Camera. These are hypotheses, not findings. Earlier placement and timing differ in [B] versus [E], and [K27] documents changed ID/label-era conditions; the old short remaining lifetime does not isolate warmth as the cause. Do not regress the working label or resurrect the disproven duplicate-kills hypothesis to recreate that interval. [K34, V55]

## 4. Honest Gate 5 null semantics

**“No Home-owned surface was demonstrated by these probes” is supported; “the app draws where nothing reads” is premature.** The latter asserts rendering as well as failed consumption, neither of which follows from an empty IVI announcement list and an output-wide background capture. A surface can be unlisted because the observer exits before announcements, lacks its role/namespace, uses another mapping, or existed outside the sampled instant; these are alternatives to discriminate, not claims that one occurred. [P, E, X]

The run hit the pre-committed *operational* null. It did not execute [V56]'s promised `pid → wl_surface → ivi_surface` measurement, so the null cannot uniquely name the mechanism asserted in [K35]. Preserve Gate 2 and the healthy warm-registration result while narrowing Gate 5's wording.

## 5. Stopping rule — two sentences

Stop this fault investigation when a validated, PID/start-time-bound observation localizes the failure to no surface request, an explicitly rejected association, no buffer commit, or failed presentation, and the evidence distinguishes that boundary from the observer's own defects. If the bounded audit is inconclusive or another run would merely repeat the same unattributed listing/background capture, stop with the missing identity or coverage explicitly recorded—no further ID roulette, timeout patches, or full boots without a new discriminating observation.
