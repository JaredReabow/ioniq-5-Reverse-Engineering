# C4 — finish the home screen, not the registration investigation

## Verdict and evidence boundary

Read-only consultation; no VM runs, experiments, git operations or vendor changes. This note is the only repository write. **Registration and the authentic exec label are closed for the measured warm-start recipe.** They are not contingent on eliminating a duplicate. K34 records `App::home` twice and warm PID 2516 registering followed immediately by `ClearTimeoutLoading : 11, PID : 2516`, without a preceding timeout. The cold PID 2331 is a separate incarnation. V55 establishes that duplicates are survivable. **No frame was captured in K34.** Therefore neither a failed layout nor a successful one is measured in that run. [K34; V55]

Do not carry forward V52's claim that the duplicate guard caused the kill, or C2's requirement that duplicates be absent. Retain V52's useful timing measurements and managed warm-start recipe. Nor does survival alone close gates 2–6: V54 defines consumption, post-power survival, ownership, layout and interaction as separate questions. [V52; V55; V54]

References used below (paths are relative to the repository):

- **K34:** `docs/kernel/34-label-measured-warm-registers-in-time.md`
- **V55:** `docs/vm/55-the-duplicate-is-not-the-killer.md`
- **V54:** `docs/vm/54-retention-correlation-and-the-seven-gates.md`
- **V52:** `docs/vm/52-the-one-number-that-decides-it.md`
- **K27 / K28:** `docs/kernel/27-segv-is-phev-smack-denial.md`; `docs/kernel/28-phev-denial-gone-frame-still-standby.md` — use their patch/label records, not their superseded duplicate causality or image attribution.
- **K01 / K09 / K11:** `docs/kernel/01-build.md`; `docs/kernel/09-vm-input-fix-result.md`; `docs/kernel/11-1920x720-capture-saved.md`
- **State §power:** `docs/CURRENT-STATE.md`, section “Why the home layout did not appear…” — API/slot inventory only, not its historical “resolved” verdict.
- **Data:** `docs/vehdata/01-battery-range-data-path.md`, especially §§1–3 and 9.
- **Injection:** `docs/vehdata/02-partb-injection-attempt.md`
- **C2:** `docs/planning/astra-c2.md`, §3 acceptance proposal.
- **Astra §1.2:** `docs/planning/astra.md`, original surface-table bytes and displaced mapping only; its 2080 recommendation is superseded.
- **Interact / Rebuild:** `docs/vm/interacting-with-the-vm.md`; `docs/vm/reproducing-the-authentic-image.md`
- **Public:** `vm/README.md`; `PUBLIC-RELEASE.md`.
- **Injector / Runner:** `tools/uk_fw/vm_partimg/inject-stockui.sh`; `tools/uk_fw/vm_partimg/run-byhand.py`.
- **README:** `README.md`, opening and VM status sections.

Proposals below are acceptance contracts, not claims that the necessary instrumentation already exists. Historical notes conflict; the latest retained-line result wins on registration, and no historical size-based frame label is used as ground truth.

## 1. Gate 2 — the observable must be inside the receiving app

### What is already identifiable

The documented manager contract is:

```
destination: com.lge.hyundai.avn.appmanager
path:        /Information
interface:   com.lge.avn.appmanager.info
method:      set_power_on_status(int on, int position)
signal:      power_status(int status)
app slot:    slotPowerStatus(int)
```

The method is addressed to **ApplicationManager**, not directly to PID 2516. Saying it was “sent to the warm instance” is sequencing shorthand, not delivery evidence. The getter can return `1` before and after the setter. A method return proves manager acceptance; a monitored `power_status(1)` proves manager emission; neither proves that the warm Home receiver executed. [State §power; Interact §3; Data §3; Injection]

**No existing literal launcher/app/compositor log line in the material read is demonstrated to prove this consumption.** `START DRAW`, registration, a global preload flag, a new buffer, or a day-theme change is insufficient individually. In particular, drawing/model-construction messages already occur during startup in K09. This is a bounded evidence gap, not a claim that the binary contains no useful logging. [K09; K34; C2]

### Add this exact diagnostic contract, at these two points

Prefer a projection-side, non-mutating trace of the existing app handler/state path. Resolve the real symbol containing `slotPowerStatus(int)` against the exact AppHomeScreen build first; the read documents give the slot name, **not an executable address or a proven logging facility**. Do not invent an offset or install a process-wide preload.

1. **Receiver entry:** record PID/start time, guest-monotonic time, argument `1`, and a local event sequence when the warm process actually enters `slotPowerStatus(int)`.
2. **After the handler applies the event:** record the actual disposition at the branch that accepts power-on and activates/requests the home presentation. If work is queued, record the queued continuation executing, not just enqueue success. Record a rejected/not-ready/no-op outcome separately. “Already on” only passes if the actual app presentation state is already home-active, not because the manager getter says `1`.

Suggested new records, explicitly **not existing vendor messages**:

```
HOME_POWER_RX pid=P start=S seq=N arg=1 mono=T
HOME_POWER_APPLIED pid=P start=S seq=N disposition=home-active mono=T2
# alternatives: disposition=deferred | rejected | no-op-standby
```

These should go to retained app diagnostic stderr, or a clearly separated app trace stream. A projection trace collector may produce them from observed handler/state execution; it must not synthesize them from `dbus-send` success. If external tracing is unavailable, the next preparation is a diagnostic-only logging overlay at the recovered receiver and home-activation continuation. Its exact insertion sites must be recovered before implementation; a wrapper around the **sender** cannot provide this evidence. No vendor byte patch is authorized or specified here because no verified receiver offset is available. [State §power; C2 capture/receipt discipline]

**Gate-2 pass:** for the same warm `(PID, /proc start time)`, the retained manager emission is followed by `HOME_POWER_RX(arg=1)` and `HOME_POWER_APPLIED(disposition=home-active)`, without an intervening restart. Arm the trace before the single setter call, retain all power events in the interval, and correlate event ordering rather than assuming two clocks agree. If several indistinguishable broadcasts occur, do not attribute one application event to a particular setter serial without further evidence. Gate 2 proves app-side application of the event, not completed widget geometry. [V54; proposal]

## 2. Gate 5 — a machine predicate, not a PNG-size category

**Choose a source-bound UI-state predicate plus compositor presentation evidence.** It avoids inventing OCR/entropy thresholds from two wrongly attributed pictures. A stranger should be able to evaluate the following Boolean contract from exported records:

```
HOME_FRAME = identity && home_tree && geometry && presentation && persistence
```

### Required inputs and rules

1. **Identity:** the launcher app-11 record, actual executable identity and PID/start time match the compositor's client credentials. Record the chain `process → wl_client → wl_surface → IVI ID`. The chosen ID is unique among live surfaces. Do not substitute `QT_WAYLAND_SET_SURFACE_ID=1010` for this chain, and do not simply select the first ID other than 2080. Resolve the recorded 1010/1005 discrepancy. If the shell's existing inventory lacks client credentials, add projection-side compositor logging of client PID/UID at surface creation and IVI association. [K27; V54]
2. **Home tree:** export the live, active Home layout subtree, not merely construction messages. For the documented EV/wide variant, the source anchor is `app/share/AppHomeScreen/qml_eco3.0/HomeScreen/Screen_HomeScreen_Widget_Advanced.qml`, which instantiates `component/QButtonBatteryHomeItemEco3.qml` when `_isEV && _isWideScr`. Its Battery and Range value items are `value_battery` and `range_value`. Require both to belong to the active Home subtree, with effective ancestor visibility true, effective opacity greater than zero and positive painted bounds. `---` is acceptable: those placeholders are explicitly defined by the source bindings. QML ids are not necessarily QObject `objectName`s; the exporter must resolve them in their QML context, not assume a generic object-name query will work. [Data §1]
3. **Geometry:** freeze, before the acceptance run, a manifest from that exact shipped layout variant: source hashes, active variant conditions, the two items' expected scene-space regions/relationship and the Home menu/control region. Export their actual bounds after layout/polish; require bounds in their declared regions, the declared relative placement, and no unintended clipping. At the compositor, require output **1920×720**, with an explicit surface-source-to-output-destination transform. Do not require the app buffer itself to be 1920×720: earlier app surfaces were 1926×753. A 1920×720 PNG alone establishes none of this. [Data §§1,3; K11; C2 §3]
4. **Presentation:** the mapped, visible, non-occluded app-11 surface must contribute a **new buffer after the home-active event and after this layout snapshot** to the captured output. Correlate the layout generation/render commit to a compositor presentation/repaint record and then the capture. A UI tree without a matching presented buffer proves only in-memory layout; a `wl_surface.commit` without visible output contribution proves only a submission. Export buffer/frame sequence and layer, clipping, visibility and destination rectangle. Instrument the projection compositor if its logs do not expose these facts. [V54; C2 §3; proposal]
5. **Persistence:** repeat the same predicate after 60 guest seconds with the same process identity and no intervening exit. This is a proposed stability criterion, not a vendor timing constant. A duplicate registration warning by itself does **not** fail it. [K34; V55; proposal]

**Preparation still missing:** this consultation has read the Data mapping, not the shipped QML or an exported live tree. The exact region manifest, active-variant verification, tree exporter and layout-to-buffer correlation are not established by the read evidence. Prepare them before claiming a machine verdict. If the actual variant differs, derive its manifest from its shipped source rather than forcing eco3.0. Until then the strongest permissible verdict is **ATTRIBUTED HOME BUFFER PRESENTED; LAYOUT UNVERIFIED**. [Data; C2]

A pixel-based implementation can replace the tree check, but must freeze source-derived Battery/Range/menu templates, spatial regions and thresholds beforehand, and pass camera/background negative controls. Absence of `STR_CAMERA_ALERT2`, reduced black coverage, a changed hash, entropy or PNG byte count is not a positive classifier. The source-bound predicate above is the preferred completion route; it does not need live CAN values. [C2; Data; K11]

## 3. Remaining blockers, ranked — hypotheses, not another diagnosis by summary

| Rank | Candidate | Why it ranks here | Cheapest discriminating check |
|---|---|---|---|
| **1** | **The warm Home surface is not the surface being selected/placed on the output.** | This has concrete unresolved evidence: launcher assignment 1010 versus reported compositor ID 1005, plus the earlier 2080 collision. The newest run captured no frame, so it may already render correctly and only lack attribution/presentation proof. [K27; K34; V54] | While the surviving warm instance is alive, take **one PID-bound compositor inventory**: client credentials, wl_surface/IVI mapping, last buffer, layer, visibility, source/destination rectangles and occlusion. If its buffer exists but is hidden/unplaced, place that proven surface through the existing projection placement path. If ownership is absent from the inventory, add that log field first; another screenshot is not the check. |
| **2** | Power-on reaches the manager but the app has not applied it, e.g. receiver readiness/queued-state ordering. | Setter acceptance and getters have previously been misleading; no same-instance receiver evidence exists in K34. Readiness is a hypothesis, not a new wrong-bus assertion. [Data §3; Injection; K34] | Observe the two gate-2 receiver/application records for one call. RX absent versus RX present/APPLIED absent selects transport/subscription versus app state handling. |
| **3** | App-side layout dependency or geometry failure after successful consumption. | Earlier records include PHEV access trouble and SQLite table errors, but the authentic label is now measured and the old denial is not a current diagnosis. [K27; K28; K09; K34] | Read warm-instance stderr/kernel output spanning the applied event and export the Home subtree. A concrete failed resource/schema/denial or inactive layout branch is the next ticket; blanket permissive SMACK is not. |

Do **not** rank missing CAN values as the leading cause of an absent layout. The source explicitly supports Battery/Range placeholders; CAN transport is missing functionality, not demonstrated evidence that the widget tree cannot lay out. [Data §§1,9]

This ranking is operational: settle the cheapest concrete ambiguity first. It does not assert that rank 1 is a confirmed defect. If identity and presentation pass, move immediately to rank 2; do not spend another run changing surface IDs speculatively.

## 4. Gate 7 — the minimum stranger's runbook and today's blockers

**There is not yet a validated end-to-end runbook for a laid-out home screen on this warm-labelled DRM configuration.** K34 did not capture one. Gate 7 needs two clean reproductions of gates 1–6, not a reuse of the current warm guest. The following is the minimum release contract, not a claim that the commands already form one working automation script. [K34; V54]

### Required recipe

1. **Acquire/build inputs.** Specify the official EU 260128 package identity, lawful local acquisition, extraction procedure, hashes, toolchain and package versions. Build the 17-partition image and active root p5. Publish authored source/config deltas and build commands, not vendor binaries or private data. Pin Mesa/software-GL dependencies rather than “same vintage.” [Public; Rebuild §§1–2]
2. **Build the current DRM projection, not the historical headless one.** Include the reconciled 4.1.27 configuration, MICOM/board parameter stand-ins, bochs 1920×720 mode addition, corrected deferred-seat input module, `drm-backend.so`, `Virtual-1`, vendor shell path, and software GL. Record full hashes and the exact QEMU command, CPU/memory allocation and init path. K01 explicitly says the rebuilt kernel is upstream-based with compatibility changes, **not the shipped vendor kernel**. [K01; K09; K11]
3. **Stage all launch prerequisites before boot.** Apply `/sbin/chsmack -e "App::home" /app/bin/AppHomeScreen`, create the documented PHEV directory through the established setup, retain real launcher/manager, and install the verified non-colliding surface mapping. Keep vendor timeout values. Record active patches and labels in a manifest. [K27; K28; K34]
4. **Qualify evidence retention before starting the stack.** Host run ID, host-readable/export-tested storage, full launcher and app stderr, kernel output, relevant bus events and compositor state. Log process start times and a shared clock marker. Account for snapshot mode: guest writes alone are not persistent evidence. K11 demonstrates ttyS3 can be MAC-denied and ttyS2 worked; verify the selected export rather than assuming any serial channel is usable. [V54; Interact §7; K11]
5. **Boot and deliberately warm once.** At least the documented four-vCPU configuration; wait on actual readiness, not fixed sleeps. Record the cold attempt and its lifecycle. Once it exits, request one managed relaunch on the verified launcher bus:

   ```sh
   dbus-send --session --dest=com.lge.avn.applauncher /com/lge/avn/applauncher \
     com.lge.avn.applauncher.request.launch int32:11 string:AppHomeScreen string:/app/bin
   ```

   `--session` assumes the shell has the verified application bus environment; publish how it is obtained. Require live `App::home` and raw warm `[REGISTERED] → ClearTimeoutLoading` for that PID with no preceding timeout for that incarnation. If cold does not exit, stop or use a separately documented managed-stop operation; do not invent a kill loop. [V52; K34; C2]
6. **Apply power and attribute presentation.** Arm receiver tracing, establish the warm identity, call the documented `/Information` setter once, then evaluate gates 2–5 above. Persist the original logs and frame, not just a Boolean or grep summary. [State §power; V54]
7. **Prove one interaction.** Before sending input, declare one actual visible Home menu action and its expected destination/return state from the selected build. Derive coordinates from its bounds, not a guessed centre click. Require focus PID equal to Home, application-side input evidence, the predicted transition and a successful return. `VM_INPUT_CLICK_ACCEPTED` or focus on `weston.real` is not completion. Then repeat from the immutable base plus declared warm-up, in a fresh guest. [Interact §§4,6; V54]

### What blocks a stranger today

- **Local artifacts are deliberately excluded.** Public explicitly says the historical repro scripts are not standalone and need locally rebuilt firmware, generated disks and build outputs. K34's raw run and probe live under private/local `work/vm/kbuild/`, not a self-contained public reproduction package. Do not solve this by publishing private raw dumps. [Public; K34]
- **The advertised build recipe is the wrong generation.** Rebuild stages `headless-backend.so`, the older input module and a 2080/camera-derived success check. The current route needs the K09 deferred-seat module, K11 mode change, K28 label setup and K34 warm-start sequencing. Its historical “what you should see” cannot be the acceptance oracle. [Rebuild; K09; K11; K28; K34]
- **The runner is workspace-specific.** Runner binds `WS` to `work/vm/byhand`, reads its kernel at import, derives the expected hash from that local file, and defaults to two CPUs. K01's current `run-kbuild.py` is recorded under `work/vm/kbuild/` with a different workspace and compatibility setting. A stranger needs a parameterized, pinned current runner, not the old command pasted unchanged. [Runner; K01]
- **Staging completeness is not fully enforced.** Injector writes `init-authentic-hmi.sh`, `applauncher-sh-vendor` and four software-GL libraries, but its staged-file preflight list omits those entries. Its later `MISSING` checks print diagnostics rather than uniformly failing. It also assumes a workspace-relative route back to the sync tool. Publish a complete manifest and fail-closed verifier. [Injector]
- **Acceptance instrumentation/data is unfinished.** No demonstrated power-consumption receipt, reconciled 1010/1005 ownership, frozen layout manifest or same-run Home interaction result appears in the latest evidence. README's broad success claims and Interact's `pidof`-as-registration shorthand cannot fill those gaps. [K34; K27; C2; README; Interact]

## 5. What to cut — and what to keep

**Cut from this finish line:** duplicate suppression, another registration manager, preload-complete forgery, timer tuning, MICOM/CAN widget-value emulation, engineering-mode entry, navigation foregrounding, audio, suspend and persistence work. These are either obsolete explanations, separate features, or unnecessary for a Home layout whose source already defines `---`. Keep a harmless Home navigation-and-return action as the interaction acceptance test, not a demand for working vehicle widgets. [V55; V52; Data; V54; README]

**Keep:** real vendor launcher, real ApplicationManager, authentic app label, vendor application/QML, vendor Weston, projection hardware/GL/input adaptations, deliberate warm-up and one explicit power-state stimulus. Keep minimum boot/status stand-ins separate from the still-unbuilt vehicle-data transport; opening the SPI gate is not MICOM/CAN emulation. [K01; K09; Data §§6,9; K34]

**Vendor-patch ledger:** the existing AppLauncher table entry at file offset **`0x475e8`** is `0b 00 00 00 f2 03 00 00` for **11→1010**. Rebuild's earlier expectations are obsolete. Astra §1.2 records the original bytes `71 00 00 00 7a 08 00 00`, identifying the displaced mapping as **113→2170**: the trade is loss of app 113's entry, not “free space.” Prefer a verified per-app projection launch-environment assignment if the launcher can preserve it; that capability is not established here, so retain the documented patch for the scoped run rather than add another untested fix. Do not extend the table or reuse Camera's 2080. K27 records the ineffective deadline edit at **`0x18270`** reverted to the vendor 10-second value; leave it reverted. No further vendor patch is recommended. [K27; Astra §1.2]

**Completion statement to aim for:** “From the declared clean base, the vendor-managed, correctly labelled warm AppHomeScreen consumes power-on; its uniquely attributed surface presents the source-verified Home layout at 1920×720 with placeholder vehicle values; one declared input action and return succeed; a second fresh run reproduces it.” Anything less gets its exact gate status, not another ‘home screen works’ headline. [V54; proposed acceptance contract]
