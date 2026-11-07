# Astra C7 — the retained protocol evidence breaks the “missing screen-create client” premise

Read-only post-boot65 consultation. This document is the only intentional repository write. No experiment, boot, guest action, build, installation, or git operation was performed. Inspection used existing files, ordinary shell searches, in-memory log decoding, and the installed LLVM ELF tools; these are not REA-tool Evidence records.

## Decision

**Do not load `hmi-controller` again. The best-supported screen owner is the compositor-side IVI layout in `ivi-shell.so`, with `ivi-controller.so` constructing/announcing per-client screen resources—not an unidentified stock client issuing `ivi_controller.screen_create`.**

There is a material contradiction in the supplied interpretation of boot65:

- The zero-count `ivi-place` output is real, but the retained boot65 compositor log also contains **`ivi_controller.screen(7, new id …)` and nonzero layer/surface announcements**.
- The retained vendor-derived protocol has **no `screen_create` request**. It has three controller requests: `commit_changes`, `layer_create`, and `surface_create`; `screen` is a **server event**.
- The inspected extracted `ivi-controller.so` has no `create_screen` symbol in its symbol inventory. It does have `init_ivi_shell` and `bind_ivi_controller`, whose code supplies the screen path described below.

Thus the next cheap diagnostic is **an offline protocol-direction/artifact-identity audit**, not a hunt premised on an already-established client opcode. Much of that audit can already be answered from retained evidence. Preserve the successful explicit DRM selection; do not undo the AppLauncher vendor-byte revert.

## Evidence ledger and limits

Required documents read in full:

- **[K39]** `docs/kernel/39-drm-boots-ivi-has-zero-screens.md`.
- **[K38]** `docs/kernel/38-hmi-controller-is-ivi-module-init-fails-no-screens.md`.
- **[V56]** `docs/vm/56-endgame-runbook.md`.
- **[C6]** `docs/planning/astra-c6.md`.

Additional evidence actually inspected:

- **[K37]** `docs/kernel/37-revert-restored-surface-config-key-dead.md`; **[C5]** `docs/planning/astra-c5.md`.
- **[B58/B65]** relevant markers in `work/vm/kbuild/boot58-hmi.log` and `boot65-final.log`.
- **[W58/W65]** `work/vm/kbuild/ws/runs/1793931162561454000/exported-weston.bin` and `1793944643111075000/exported-weston.bin`; matching `dbg-out.txt` base64 blocks decoded in memory.
- **[P]** `tools/uk_fw/ias_backend_soft/ivi-controller.xml` (global interface/provenance), `ivi-controller-protocol.c` (complete generated tables), and `ivi_place.c` (registry binding and list-only path).
- **[F]** `work/vm/kbuild/ws/partimg-build/final-run.sh`, complete. The current `hmi-run.sh` was also read, but its `[hmi2]` prefix shows it is not an immutable copy of boot58's `[hmi]` script.
- **[ELF]** extracted binaries under `work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/weston/`: symbol inventory and focused disassembly of `ivi-controller.so` and `ivi-shell.so`.
- **[WM]** retained `work/tmp/iviwm.dis`, `controller_module_init` at `0x10e20`, especially `0x10f1d–0x10fba`. This retained disassembly was not independently matched to deployed bytes.
- **[REF]** `work/weston-source-1.10/full/ivi-shell/ivi-layout.c`, `create_screen` at lines 252–286 and the located call from `ivi_layout_init_with_compositor`. Reference source is explanatory, not proof of exact vendor source identity.

Extracted ELF SHA-256 identities:

| Artifact | SHA-256 |
|---|---|
| `ivi-controller.so` | `0cf0e54e3305582505f0a9cbb9afe6995944a799fea89bad0bfc99f7113b8c80` |
| `ivi-shell.so` | `8b57db4baa1f35a1a08cffc6de221101a92b37528123d7250c774db03a3b7697` |
| `ivi-window-manager.so` | `e1ce4d479f1fb84cc44d2faebad748206bdf3003b48a9ccf90e76da17a553bd0` |

These are **extracted-image identities**, not newly measured hashes of boot65's loaded files. A different deployed build remains a branch to check, not an excuse to ignore the retained runtime events.

The base64 block in each `dbg-out.txt` decodes exactly to its corresponding `exported-weston.bin`. W58 is 277,341 bytes, SHA-256 `8e8f9dba6d1d58ad6ce5af3bab721a818073c8d746ace94e35664e9abbea26fb`; W65 is 229,663 bytes, SHA-256 `2cd466d8372e1460632aee3be0e064377f38bcc5de6923803ebca45c732543d8`. Their declared BEGIN lengths are smaller (234,468 and 227,371). [F] measures length before streaming a still-growing log, which can explain the mismatch; the export is not an atomic snapshot. Exact decode equality establishes export provenance, not PID ownership or absence after the capture ended.

## 1. Reconcile the cycle: distinguish three kinds of screen creation

### A. Layout screens are compositor objects

In the extracted `ivi-shell.so`, **`ivi_layout_init_with_compositor` at `0x8210`** walks the compositor list rooted at offset `0x1e8`, allocates `0x70`-byte records, assigns incrementing screen IDs, stores the output pointer, and inserts the records into the layout screen list (`0x82b3–0x8357`). This matches the reference `create_screen(ec)` loop over `ec->output_list`. [ELF, REF]

Consequently, absence of an `output_created` symbol in **`ivi-window-manager.so`** does not establish absence of output-to-screen initialization: it searches the wrong component and excludes neither an initial output-list walk nor an inlined implementation. Outputs already existing when IVI initializes are exactly what this loop consumes. A hotplug-listener hypothesis is not needed to explain initial creation.

### B. Controller screen wrappers are also server-side

In `ivi-controller.so`:

1. `controller_module_init` (`0x4d40`) calls `init_ivi_shell` (`0x7310`).
2. `init_ivi_shell`, `0x7363–0x73d6`, walks the compositor output list, allocates controller-side screen records, saves output pointers, and calls `ivi_extension_get_screen_from_id` to associate the existing layout screen.
3. `bind_ivi_controller` (`0x70c0`) walks those records. At `0x7168–0x717e`, it calls **`wl_resource_find_for_client`** on the output resources and skips a screen if that client has no matching output resource.
4. Otherwise it creates an `ivi_controller_screen` resource (`0x7191`), obtains the client's output-resource ID (`0x71cf–0x71d2`), and posts event **opcode 0** (`0x71d7–0x71e4`): `ivi_controller.screen`.

This is not a client `screen_create` request. It is server-side resource construction on a controller bind, conditioned on the client already binding the corresponding `wl_output`. In particular, the event's `7` must not automatically be treated as layout screen index 7; the disassembly obtains it from that client's output resource. [ELF, P]

### C. The zero-list observer is not a layout census

[P] shows two independent problems:

- `ivi_place.c:503–525` binds only `ivi_controller`, not `wl_output`. For the inspected server, that alone can suppress its screen announcement.
- `ivi_place.c:795–835` prints and exits after the initial registry roundtrip, without a post-bind roundtrip. This can miss layer/surface announcements too, as C5 already warned.

Exit 0 certifies the tool's list-only completion, not that all server events were received. Two identical invocations do not fix either defect. Deployment identity of the observer still needs verification.

More decisively, **W65 lines 368–380** show a controller bind followed by:

```text
ivi_controller@11.screen(7, new id ivi_controller_screen@4278190080)
ivi_controller@11.layer(107)
ivi_controller@11.layer(112)
ivi_controller@11.layer(111)
ivi_controller@11.layer(104)
ivi_controller@11.layer(113)
ivi_controller@11.layer(102)
ivi_controller@11.layer(110)
ivi_controller@11.layer(10)
ivi_controller@11.surface(100)
ivi_controller@11.surface(1)
```

Surface 30000 follows at line 381. The decoded W65 stream has 25 screen-announcement matches; these are repeated client announcements, **not 25 distinct screens**. W58 has the same class of event. This refutes a run-wide “IVI has no screens/layers” interpretation while leaving presentation and the four configured 1000/2000/3000/4000 layers unresolved. Those four keys are not proven to instantiate anything, but neither does the invalid list prove all layout objects absent.

### So which stock client is likely responsible?

**For the inspected build, none is needed to create the underlying screens.** The stock compositor shell/layout is the likely owner; the controller supplies protocol handles to clients that bind outputs. AppLauncher or a vendor window-management library might own later layout policy, but naming either as a `screen_create` caller would currently invent a request absent from the protocol.

If a *different, deployed* binary truly has that request, the first candidates would be the stock system layout/session-management client and its linked library—inspect `/app/bin/AppLauncher`, its wrapper/dependencies, vendor window-management or ILM libraries, then `/usr/libexec/weston-ivi-shell-user-interface`. This is a conditional search order, not evidence that any of them calls it. Require an actual request-table entry, a reachable client marshal call with the matching opcode, and stock startup/configuration evidence linking the caller to the image. Merely shipping the demo UI or finding the string `ivi_controller` does not establish ownership.

## 2. Home missing in boot65 versus boot58: ranked explanations

**First separate a broken summary counter from a real difference in retained traces.** [F]'s regex expects `"AppHomeScreen")`, but the actual protocol line has `"AppHomeScreen", new id ivi_hmi_client@21)`. Boot58 itself prints `HOME_CLIENT=[]` at B58 line 1009, despite W58 line 4414 containing the Home registration. The summary grep is therefore not a valid regression test. A broader search of the decoded W65 stream finds no Home registration while finding other named clients; the retained-stream difference remains, with bounded coverage.

Ranked hypotheses after that correction:

1. **Process replacement and observation-window/launch-order differences.** Strongest concrete clue: B65 records cold PID 2374, replacement/warm PID 2546, then capture PID **2677**. B58 records cold PID 2268 and warm/capture PID **2667**. B65 does not preserve one Home identity through power-on and capture. “COLD_KILLED” only means the PID changed/disappeared; “WARM_PID” can select an already-restarted process before the requested launch takes effect. Registration/exit deadlines or changed readiness can explain a missing request in this interval without changing the protocol. [B58/B65, F]
2. **Power/readiness or preload state differs for the surviving instance.** F discards both D-Bus replies/errors and prints `*_SENT` unconditionally; it has no `power_status` monitor. Boot58 had monitor output, though its count alone does not prove consumption by a particular Home instance. V56's Gate 2 contract and same-PID persistence are not re-established for boot65. This can affect whether a window is requested; it is not proof of a power failure.
3. **Effective configuration/environment/plugin or clone-state drift.** Compare the actual wrapper, child environment, library/plugin identities, launch/label settings and deployed AppLauncher hash. C6 records the known-good vendor hash and warns about shims. The supplied fact that launcher bytes were untouched makes renewed patching a lower-ranked cause; it does not prove identical child environment or state. Mutable staged filenames are not historical deployment evidence.
4. **A real IVI association/allocation or application failure.** Promote only with Home-bound `request_id`/`receive_id`, core `create_surface`, IVI request/error/destroy and lifecycle evidence. Numeric 1006 is not an owner: W65 line 3896 assigns it to **AppStandbyClock**, and W58 also used it for StandbyClock before Home. Do not infer a simultaneous collision or restore an ID patch from that reuse.
5. **Missing HMI controller or a globally absent screen caused the regression.** Lowest-ranked: neither run loaded that optional module according to the supplied baseline, W58 created Home without it, and W65 has screen/layer announcements. The common standby screenshot and byte count do not discriminate these causes.

**Cheapest no-boot comparison:** use B58/B65 plus the decoded W58/W65 streams to make one time-ordered table per process/connection: launch, app-11 registration, exit/replacement, power event, `request_id`, `receive_id`, `create_surface`, `ivi_application.surface_create`, `create_hmi_client`, buffer commit and destruction. Use a permissive named-client search, then read context:

```sh
rg -a -n 'AppHomeScreen|request_id|receive_id|create_surface|surface_create|create_hmi_client|protocol error' \
  work/vm/kbuild/ws/runs/{1793931162561454000,1793944643111075000}/exported-weston.bin
rg -a -n 'COLD_PID|COLD_KILLED|WARM_PID|POWER_ON|power_status|CAP bytes|AppHomeScreen' \
  work/vm/kbuild/boot{58-hmi,65-final}.log
```

Do not equate connection-local object numbers across clients or invent missing PID credentials. If retained app stderr, launcher records, effective environment or start times are absent, mark those columns unknown. The comparison can localize a trace difference without claiming the full V56 `HOME_FRAME` predicate.

## 3. Single next diagnostic: finish the offline screen protocol/ownership trace

**Question:** Is `screen_create` really a wire request in the exact deployed build, or has an internal constructor/server event been misclassified? No new boot is justified before this is settled.

Exact targets and read-only commands, using the existing extracted image as the first comparator:

```sh
R=work/decrypted-eu-260128/extracted-safe/mango-rootfs
LLVM_BIN=/path/to/llvm/bin
rg -n 'screen_create|commit_changes|layer_create|surface_create|name="screen"' \
  tools/uk_fw/ias_backend_soft/ivi-controller.xml \
  tools/uk_fw/ias_backend_soft/ivi-controller-protocol.c
"$LLVM_BIN/llvm-readelf" -Ws "$R/usr/lib/weston/ivi-controller.so"
"$LLVM_BIN/llvm-objdump" -s --section=.data.rel.ro "$R/usr/lib/weston/ivi-controller.so"
"$LLVM_BIN/llvm-objdump" -d --no-show-raw-insn \
  --disassemble-symbols=controller_module_init,init_ivi_shell,bind_ivi_controller \
  "$R/usr/lib/weston/ivi-controller.so"
"$LLVM_BIN/llvm-objdump" -d --no-show-raw-insn \
  --disassemble-symbols=ivi_layout_init_with_compositor \
  "$R/usr/lib/weston/ivi-shell.so"
```

Resolve `ivi_controller_interface` (`0x20d320`), `ivi_controller_requests` (`0x20d3c0`, 72 bytes/three messages), `ivi_controller_events` (`0x20d360`, 96 bytes/four messages), and `controller_implementation` (`0x20d1c0`) against relocations/strings; do not infer request direction from an exported C symbol. Compare hashes to retained deployed-image manifests or read-only image contents when available; do not mount/write a live image or extract new files in this consultation.

If a different table genuinely supplies `screen_create`, search its stock executable/library set for `ivi_controller`, `screen_create`, `ivi_controller_screen_create`, `wl_registry_bind`, `wl_proxy_marshal`, `wl_proxy_marshal_constructor`, and `wl_proxy_marshal_array_constructor`; also inspect `DT_NEEDED` with `llvm-readelf -d`. Generated wrappers may be inlined, so lack of an exported wrapper symbol is not a negative result. Follow the controller proxy's data flow and **the recovered opcode**, not arbitrary calls with the same integer. Inspect the owning wrapper/unit in `/app/bin`, `/etc/systemd/system`, `/lib/systemd/system`, `/usr/lib/systemd/system`, `/etc/init.d` and `/etc/xdg/weston` for startup order and selected configuration. Missing paths are coverage limits, not proof of a missing stock service.

Decision branches:

- **Tables match the inspected build:** close the nonexistent `screen_create` client search. Attribute initial layout creation to `ivi-shell`; controller handles to its bind path. Before trusting another inventory, verify the deployed observer binds `wl_output` before controller binding and waits for post-bind events. That is an observer correction, not a vendor layout fix.
- **A different deployed request exists and a stock caller is found:** identify the exact startup trigger, output-selection arguments and guard that differs in the VM. Only then propose one test of that guard with unchanged vendor binaries.
- **Request exists, but only demo/research clients call it:** do not label them stock. Record the image/component coverage and stop the stock-owner search pending missing image evidence.
- **No initial screens on a verified different build:** trace its actual `ivi_layout_init_with_compositor`, initial output walk and callback registration timing. A named-symbol absence cannot establish missing functionality.
- **Screen exists, Home remains absent:** close “no screen” as the current blocker and use the offline Home comparison above; do not spend a run creating a second screen/layout.

## 4. Should hmi-controller be added again?

**No, not now.** The vendor template excludes it, K38 demonstrates init failure, and the purported no-screen explanation for that failure is no longer secure. Presence of `ivi-shell-user-interface` parsing establishes that this module can launch that UI, not that the stock application stack requires it. Do not equate demo shell widgets with the application's live QML Home subtree. [K38, K37, C6, V56]

Reconsider only if exact image/startup evidence shows this module is selected for this product, or if a separately authorized non-stock projection explicitly needs its demo policy. First locate the exact failure branch in `controller_module_init`/`hmi_controller_create`, prove compatible layout API/module versions, required screens and configuration, and rule out conflicting existing layers/IDs. The extracted layout and protocol observations make that branch trace more valuable than another blind load.

**Minimal future test, conditional and not performed:** one disposable startup-only comparison against the verified baseline, changing only the IVI-module list to append `hmi-controller.so` (never core `modules=`). Capture the precise init success/failure branch, actual UI launch, synchronized pre/post layout inventory and ID conflicts; no warm-launch loop, power manipulation, placement, ID patches or full UI claim. If its prerequisites cannot exist until after the event loop starts but its init runs synchronously earlier, prove a supported initialization order before testing—adding the module cannot solve that ordering by itself. Stop on the first init failure or conflict and discard the clone.

## 5. Stop condition

Stop the **missing-screen-owner** thread once the exact protocol tables and initialization path are attributed, or once one bounded offline pass over the relevant stock modules, linked candidate clients and startup manifests cannot attribute them. In the latter case report the precise missing artifact/identity/control-flow edge; require new stock evidence before reopening. Do not substitute a synthetic screen-create client, load optional modules, alter surface IDs, extend timeouts or run another full boot to make an unattributed layout appear.

For the evidence presently available, the stronger stop applies: **a screen and layers were announced in boot65, and the inspected stock protocol has no client screen-create request.** Close that premise rather than repair it. The remaining display question is observation correctness and Home's lifecycle/association/presentation, not proven absence of compositor screens.

**Final:** likely owner = `ivi-shell.so`'s compositor-output initialization, with `ivi-controller.so`'s server-side bind resources; next cheap diagnostic = exact deployed protocol/ELF identity plus the already-retained event trace (and the small offline Home lifecycle comparison); load `hmi-controller` = **no**.
