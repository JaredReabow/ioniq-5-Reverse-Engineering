# HANDOVER — IONIQ 5 Gen5W research

Updated **2026-10-27**. The recovered authentic Hyundai/LG launcher chain now
passes the standby/profile-confirm gate and visibly foregrounds authentic
`AppHomeScreen` in the local VM. Authentic AppNavi map pixels still render
separately. The remaining integration goal is stable Home↔Navigation operation,
followed by stateful service/CAN/persistence reconstruction.

## Public VM source record

The authored guest helpers and experiment scripts are copied under `vm/repro/`;
bounded output summaries and two inspected screenshots are under `vm/evidence/`.
Original `work/vm/` references below name local generated artifacts; see
`vm/README.md` for the published mapping and excluded disk images,
recovered vendor binaries, raw logs and core dumps. Older dated sections
remain historical evidence and may have been superseded by later findings.

## Navigation and VM findings

Bounded static continuation: `evidence/navigation-launch-status-contract.md`
records that the saved launch-status function sends literal `5` under a one-shot
gate rather than calculating it from the engine result. Exact strings are now
resolved: launcher `launched(30)` precedes a separate AppNavi
`com.lge.hkmc.avn.appnavi.naviboot.SendNaviBootFail(5)` signal at
`/navigation_map`. Enum semantics and the producer of manager window `0` remain
unresolved. Receiver disassembly now identifies `window` as a separately latched
byte at receiver +0x20, gating downstream status handling. The adjacent vendor
`naviWindoeCreate` path updates it and replays cached status. Next trace its
caller at `0x19108d`, not patch the flag or substitute surface ID 3000. That
caller is now identified as the BG-info path. Latest retained DLT positively
shows AppNavi **FG** delivery, but zero BG-info diagnostic matches; the latch
remains zero. Its pending global initially equals `0xffffffff`, not zero. Next
trace initial configure lifecycle. Original compositor classification is now
recovered: **any positive dimension selects FG; BG requires both dimensions
non-positive**. Therefore changing 1926×753 to 1920×720 would not fix this
branch. Current image compositor and shell modules match recovered originals.
Shell size cache starts 0/0 and suppresses unchanged configure calls, so an
initial zero-size surface does not automatically emit BG. Next compare a retained
positive BG lifecycle against AppNavi hide/unmap behavior; do not synthesize BG
or force the latch. Current-image/path hashes are not historical memory digests.
Constructor wiring now confirms AppNavi's callback is the same Qt object's
`visibleChanged(bool)`. Recovered QtWayland hide code has a conditional null-buffer
commit; the recovered EGL client plugin's virtual discriminator returns 1 and
skips it. Verify guest library/plugin identity and selected backend before
proposing a scoped hide adapter. This is static evidence, not a proven fix.
See the Navigation contract note for addresses, hashed correlation and limits.

## Newly supplied community leads

`evidence/community-chat-leads.md` reconciles the owner's summary of two Linux
channels with existing research. These are attributed chat reports, not newly
validated methods. Most importantly: decryption is not update acceptance;
`CV_E...220721` is an unverified different-model lead, not an IONIQ rollback
candidate; historical download availability is model/region dependent. Native
userspace recovery is already solved here, so physical AppNavi entry is not a VM
prerequisite. Exact xcrypt/updater-format or hardware-contract artifacts would be
more useful than repeating first-entry research.

## Latest bounded stack/caller capture

A new VM-only ptrace observer captured 64 readable stack words at the Camera
fault in a 43.7-second snapshot run, then re-delivered SIGSEGV. It identifies a
real memcpy call in vendor EGL `dri2_wl_swrast_put_image2`. Width-derived stride
is cached before `swrast_update_buffers`, which can change width; captured
stride/count registers are -4. This is a strong ordering/invalid-size lead, not
yet measured memcpy-entry arguments or a completed fix.

Complete archive SHA-256:
`e0884a3c11582ed2b986db28f2673b7fde9297a1871f2633ad13672b2dfdeaae`.
Source: `tools/uk_fw/guest/ptrace_crash_observe.c`; build, run, bounded disassembly
and summary under `navigation-contract-audit/` in the current VM workspace.
Guest negative tests, real fault capture and all 168 repository tests pass; base
image rehashed unchanged. No independent model review was available.

Track as **I-001** in `Ioniq5-VULNERABILITIES.md`: mixed vendor-EGL/project-Mesa
VM compatibility is a material precondition; stock-device exploitability is not
established. Next capture before/after update dimensions and copy-entry arguments,
then design a checked VM adaptation. Do not patch libc or force Navigation state.

## Prior focused core capture

A 44.83-second snapshot-only early-startup experiment captured an 80 KiB AppCamera
ELF core with eight thread-register notes. The faulting vector store writes
**64 bytes below a writable mapping**, confirmed by SIGSEGV/SEGV_MAPERR and core
program headers. Early-client decoration value is verified as `1`. Original
caller/copy length remains unknown; the core stores no fault-thread stack bytes.
This is not yet a vendor vulnerability or a Navigation fix.

Complete archive SHA-256:
`10fbb21b674ab1795c5e2b52d4e04ad47611f8674c4ac5ed43d283322c24987c`.
See `evidence/navigation-launch-status-contract.md` and
`navigation-contract-audit/early-core-summary.json` under the current VM workspace.
Base image rehashed unchanged. Next capture bounded stack/caller context at the
fault rather than repeat the whole failed Navigation sequence.

## Prior negative environment control — 2026-10-27

A single-variable decoration-unset control completed as a harness but failed
before authentic agreement/Navigation: repeated Camera/Standby crashes, no
AppNavi launch, manager 0/0, all screenshots splash. It did not verify child
value `1` or geometry. **Do not adopt the unset change.** It existed only in
snapshot guest `/tmp`; the base image rehashed unchanged. Archive SHA-256:
`648b5d30c169b2e4adaa2e8cf069742fd5b3d779b0ef1d6d7e63fead7f6910e9`.
See `evidence/navigation-launch-status-contract.md` for evidence and gaps.
Do not repeat a full navigation run before diagnosing early-client failure;
keep the original working baseline and separate hide-path investigation intact.

## Prior observational backend run — 2026-10-27

A new snapshot-only run completed without timeout and captured 26 AppNavi process
maps. The original launcher-owned process loads the exact analyzed QtWayland
client and EGL graphics plugin. It also inherits
`QT_WAYLAND_DISABLE_WINDOWDECORATION=1:1` and loads the decoration plugin; parser
impact remains unverified. No hide fix or synthetic notification was applied.

Authentic Home visibly rendered before Navigation, but the manager again followed
`11/11 → 35/11 → 11/11`, with FG delivery and `notifyNaviLaunched[5] window[0]`.
**The final return capture is black**, despite manager state 11/11; this run does
not reproduce visible Home restoration. The older positive Home evidence below
remains valid within its original run. Raw Wayland null-buffer requests were not
captured; setting WAYLAND_DEBUG alone did not establish that coverage.

Complete archive SHA-256:
`6019ec6e42cacce8a41fdc79c7dd9705487efdc0a53b741313e6b5b7aad01d84`.
Artifacts and full evidence: `navigation-contract-audit/` beneath
`work/vm/vendor-userspace-260128/`, and
`evidence/navigation-launch-status-contract.md`.
Base rootfs rehashed unchanged; 168 tests pass. Next capture genuine hide/null-
attach execution without changing behavior, and resolve the duplicated decoration
environment independently. Full Home↔Navigation acceptance remains open.

## Prior Home→Navigation integration finding

A launcher-local `execve` interposer now adds the EGL shim only to the original,
signature-checked `/navi/Bin/AppNavi`; it does not directly start a duplicate
navigation process and does not propagate the preload to other vendor clients.
In the latest completed run, the original AppLauncher-owned PID `908`:

- passed AppLauncher's signature check and remained its registered AppID `30`
  process;
- reached `### Navi Engine Init Success ###` and selected the expected logical
  `Samples: 2` config through the executable-scoped zero-MSAA translation;
- created parent surface `3000` with `AID(AppNavi)` and child surface `4903`;
- stayed alive through all four Navigation observations after the launcher-local
  shim suppressed only AppLauncher's slow-TCG `SIGTERM` liveness action.

Static analysis also identified AppNavi's exact startup deadline. In
`NimoExSLApplicationLinux::onInitializeDone()` at `0x33b48be`, elapsed startup
is compared with `0x59d7` (22,999 ms). If `g_firstTimeHideByWM` is already true
or elapsed time exceeds that threshold, the code invokes
`SendToAppLauncherNaviLaunchedToExcute()`. An exact-build, sentinel-gated,
executable-scoped runtime adaptation changed only that immediate to 180,000 ms
in memory; the signed executable on disk remains unchanged. The latest run
proved the guard and PIE-base calculation: AppNavi logged
`STARTUP_DEADLINE_22999_TO_180000_MS`, completed initialization at 106,464 ms
without taking the timeout branch, created surface `3000`, and only then entered
the launch-status function after the authentic first-window event.

That ordering control did **not** complete Navigation. The launch-status path
still emitted `SendNaviBootFail(5)` and ApplicationManager logged
`notifyNaviLaunched[5] window[0]`; manager state remained current/drawing
`35/11`, and all bounded Navigation captures continued to show authentic Home.
The return request restored manager state `11/11` and visible Home. Thus the
remaining blocker is now narrower than process startup or surface creation:
recover why the launch notification carries status `5` and window `0`, and what
contract advances `APP_NAVI_LOADING` (`35`) to `APP_NAVI` (`30`). Do not patch
or fabricate that callback.

Latest completed evidence:

- runner SHA-256
  `906e734012a9a9cac35aed2e9258674215b407a93cdce9e58024a2f78bf8dd9f`;
- host log SHA-256
  `de9977d671cb203f918d878f939777c1eea330bad90dd2ca0643b6ba57c60021`;
- complete archive SHA-256
  `a0e2100ca5a0eb72426db6179c88a27e34abe5928d8a364ce9f14d0e9bfd52b8`;
- state sequence `11/11 → 35/11 → 11/11`;
- current rootfs SHA-256
  `4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f`.

The immediately preceding targeted-preload run is useful partial evidence for
AppLauncher-owned surface creation, but its 570-second host timeout interrupted
the archive stream. It is explicitly retained as partial evidence and must not
be cited as a complete archive.

## Latest standby/input and Home finding

Global two-thread llvmpipe permits the delayed authentic Confirm flow that
softpipe starved. The latest bounded run corroborates the gate semantically and
then reaches visible Home:

- the injected pointer remains focused on authentic `AppStandbyClock`, and its
  transformed coordinate `(822.5625, 658.875)` lies inside the enabled Confirm
  control at `x=471..1179`, `y=621..699`;
- authentic logs show `confirmSkPressed()`, `onPressedButton`, `onReleased`, and
  `HANDLER_CONFIRMSCREEN_BUTTON_CONFIRM_CLICKED`;
- standby status changes from `14` to `12`;
- ApplicationManager explicitly reports
  `is_standby_agree_pressed standbyStatus[12] result[1]`;
- both display-exception checks clear:
  `DisplayExceptionFilter a_nMask[66] ret=[0]` and mask `161` `ret=[0]`;
- the handler's intermediate AppID `35` is now dynamically named
  `APP_NAVI_LOADING`, not an unknown setup/profile application;
- ApplicationManager then selects current AppID `11`, requests
  `requestShow AppId[APP_HOME][11]`, receives the authentic Home response
  `ret[1]`, and later records current and drawing application `11`;
- IVI creates run-specific Home surface `1001`, foregrounds it, and the final
  1920×720 capture visibly shows the authentic Home vehicle/battery/media page.

The immediate D-Bus transition out value remains `255`. It can no longer be
classified as rejection by itself: the same request proceeds asynchronously
through current AppID `11`, Home `ret[1]`, drawing AppID `11`, IVI foreground,
and visible composition. Use the downstream state and response chain, not the
immediate integer alone, to classify the transition.

Two explicit VM compatibility adaptations remain material. First, global
`llvmpipe` with two worker threads lets Qt dispatch the queued gesture. Second,
a bounded 55-second `SIGSTOP` of **ApplicationManager only**, after it has sent
authentic `requestShow(APP_HOME)`, prevents its production four-second liveness
watchdog from killing Home while x86 TCG software rendering creates the first
frame. No alive reply, agreement state, handler invocation, application ID, or
Home frame is fabricated. AppStandbyClock and AppHomeScreen binaries remain
unmodified; observational/sizing QML overlays, the 120-second AppLauncher timer,
and the zero-MSAA AppNavi compatibility copy are still non-production VM
adaptations.

Primary positive evidence:

- runner SHA-256
  `25a2ee9726d160c03b52c8dc3c5a76aaba33dd57d7d4be7ecba6f9b2f34485ae`;
- host log SHA-256
  `2c6c7ed142cb84b7dcc5daf5a9adb01a2e86934c731ae5653efa5d0d80d93b95`;
- evidence archive SHA-256
  `87d81b278f8b1bb20236faedd17dda0493b49b6cfc1e0fd2f1acfe8b8d2c6f5e`;
- visible final Home screenshot SHA-256
  `23ccd6e6002d8bceddac3a64b2c94538cb844cc9aa274b44d18ada876d2cc968`.

The earlier focus, Loader, QtWayland, and RIP-sampling archives remain the
canonical negative controls explaining why softpipe did not dispatch the
button. Their SHA-256 values are respectively `dbede61e…ac28`,
`4140b3b8…f134`, `c72c487b…3b73`, and `73cda7a0…c08`.

This top section supersedes the older 2026-10-21 continuation retained later in
this file for provenance. See `evidence/corrections-log.md` before quoting older
negative conclusions.

## What currently works

| Milestone | Measured result / boundary |
|---|---|
| Vendor kernel | EU package Linux `4.1.27-abl`, x86-64; not Android; one exact-build PCI-table adaptation occurs **in guest RAM** |
| Firmware recovery | Validated native TE2/xcrypt envelope decryption recovered rootfs, GUI, AppNavi, updater and RW-data userspaces from official EU `260128` packages |
| Authentic home HMI | `AppHomeScreen` renders a completed 1920×720 frame through recovered Weston/IVI and project-local Mesa 18 `softpipe`; pointer and touch reach authentic Qt/QML |
| Authentic launcher identity | `AppLauncher 3` launches AppNavi as AppID `30`, path `/navi/navi/Bin/AppNavi`, parent IVI surface `3000` |
| Navigation engine | A bounded authentic EU map parcel/core subset reaches `### Navi Engine Init Success ###` |
| Visible navigation pixels | Isolated AppNavi renders its authentic 836×720 map-widget surface `4903`; a compositor capture shows roads, water, buildings and the vehicle marker |
| Authentic full chain | VM-only `AskSysBootinfo` makes AppLauncher select HMC / vehicle `0x26` / Europe / RHD / 12.3-inch / English. Authentic Confirm advances status to `12`, agreement predicate to true, filter results to zero, and manager current/drawing AppID to Home `11`; run-specific surface `1001` is visibly foregrounded |
| Qt/Wayland environment | Removing the probe's pre-set shell variable fixes `ivi:ivi`; clients load `libivi.so` and report `Using the 'ivi' shell integration` |
| Remaining boundary | Full Home↔Navigation operation is not yet demonstrated. The latest AppLauncher-owned AppNavi reaches engine/EGL success and surfaces `3000`/`4903`, but `notifyNaviLaunched[5] window[0]` leaves manager state at `35/11`; data-bearing micom/CAN and persistence contracts remain incomplete |

The primary visible-navigation capture is:

- run `1792908755653936000`;
- PNG `1920×720`, with the native `836×720` map widget at `(0,0)` and the
  still-black AppNavi parent region to its right;
- SHA-256
  `88e8403d808b6936181465ee512aa9e124b75ccc7dbd625a221e41e75ab8b4cb`;
- evidence manifest:
  `work/vm/vendor-userspace-260128/ivi-link-navi-widget-build/visible-navigation-milestone.json`.

The capture is genuine AppNavi-rendered map content, but it is not a complete
navigation UI. The VM-only IVI helper reconstructs the missing relationship
`3000 -> 4903`, restores child destination `836×720`, and foregrounds parent
`3000`. Without that relationship, surface `4903` had a `1×1` destination or
sat behind the opaque black parent. The 40 pure-white pixels seen in earlier
black captures are the Weston cursor, not navigation content.

The earlier baseline launcher-chain experiment was run `1792936845027660000`.
A narrow, fail-closed VM simulator supplies the exact 35-byte
`com.lge.car.micom` `/Ihu` `AskSysBootinfo` reply and acknowledges only
introspection-confirmed transport methods; it does not fabricate CAN signals.
AppNavi reaches engine success, parent `3000`, and map child `4903`; Home reaches
`SCREEN_STATE: DRAW FINISHED` and surface `1004`. The final screenshot remains
the splash hash `b316a82a…0b9a83`. The later AppNavi `SIGTRAP` is explained by
ApplicationManager spawning `killall -5 AppNavi` after repeated failed liveness
checks, not by an unexplained spontaneous crash. A direct-launch no-`strace`
control (run `1792937492664474000`) reproduces the same kill: AppNavi answers
its initial D-Bus `Peer.Ping` at `/navigation_map`, then leaves eight later
Pings unanswered. Tracing adds latency but is not the sole cause. Full evidence
and boundaries:
`work/vm/vendor-userspace-260128/micom-contract/BOOTINFO-AND-SIM-V2.md`.

The boot-image file remains unchanged. Call the running kernel a
**VM-adapted vendor kernel**, not a complete stock-firmware boot. Synthetic
`ABL.oemkm` / `ABL.seed` inputs initialize keystore and manifest subsystems;
they are not recovered device keys or proof of a trust bypass.

## Current constraints

- User-owned UK 2021 IONIQ 5 Ultimate head unit, disconnected from the vehicle.
  **No physical or network access to it is available.** Its installed firmware
  version remains unconfirmed.
- Prefer existing local EU/AU packages, project-local toolchains and saved
  research. Public source/tool research is allowed, but keep downloads and all
  derived artifacts project-local where tooling permits.
- Keep generated files, VM disks, sockets and test temporaries in this project.
  Do not delete anything outside it; preserve unrelated and pre-existing work.
- No flashing, host-root operations, host filesystem mounts, or substitute
  dashboard presented as the vendor UI.
- Fable was requested as reviewer/planner only. Its tested route was unavailable;
  no substitute child is verified as Fable.
- Unit-test results and evidence hashes are **not Council acceptance**. Do not
  refresh legacy accepted-input hashes to manufacture a pass.

## Current navigation continuation

1. The 11 direct authentic `RES/SKIN` files are now injected. Theme image and
   `SIMPLENIGHT.skn` load successfully. Missing
   `VIT_EUR_3D_LANDMARK.hafmma`, `DEM/VIT_AREA_DATA_HM.cad`,
   `StyleKeyId.sqlite`, and `SymbolCode.sqlite` remain logged, but do not stop
   the first visible map frame.
2. Surface `3000` is AppNavi's 1920×720 Qt parent. Surface `4903` is the
   independently rendered 836×720 `Front_Widget` map surface. Wayland traces
   prove `wl_buffer` attach, full damage, and commit on `wl_surface@17`.
3. The isolated no-`ApplicationManager` run omitted the intended IVI hierarchy.
   `tools/uk_fw/guest/ivi_link_navi_widget.S` reconstructs
   `set_parent_child_surface(3000, 4903)` and the native child destination. It
   is exact-configuration VM infrastructure, not recovered firmware.
4. AppLauncher-first startup now creates the 35-byte `MICOMSTATUSMESSAGE`
   segment and avoids the historical repeated eight-second semaphore timeout.
   A consumer-derived `AskSysBootinfo` profile selects NE/Europe correctly.
   Remaining micom work is the data-bearing query/CAN signal contract, not the
   old semaphore symptom; do not reset or pre-create guessed IPC objects.
5. Binding recovered `/system/new_gui/new2.0/hmc/night` over the incomplete
   legacy image tree removed all 15 named `Failed to load image` messages, but
   produced the exact same screenshot hash. Missing image files are therefore
   not the current cause of the black AppNavi parent region; missing service/UI
   state remains the stronger hypothesis.
6. Do not rename `MAP/VIT_EUR_3D_LANDMARK_ASTC.hafmma` to the missing
   `RES/SKIN/VIT_EUR_3D_LANDMARK.hafmma` without tracing the variant selector.

Current ext4 image SHA-256 after the targeted AppNavi preload and guarded
PIE-aware startup-deadline control:
`4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f`.
Every mutation has a copy-on-write checkpoint and `e2fsck -fn` log under
`work/vm/vendor-userspace-260128/`.

## Historical 2026-10-21 VM instructions (superseded for HMI work)

From `/Users/researcher/Documents/ChatGPT/reverse engineering/ioniq research`:

```sh
# Interactive serial research shell
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/bootable --sdhci-compat --interactive --timeout 0

# Windowed diagnostic ONLY; R/G/B change colour, Q returns to the shell
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/graphics --sdhci-compat \
  --display cocoa --cmd /bin/vm-display --interactive --timeout 0

# Automated keyboard and pixel verification
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/graphics --sdhci-compat --graphics-smoke
```

Use `/bin/busybox <applet>` in the minimal shell. Ctrl-C stops the launcher.
QEMU has no NIC, uses a snapshot disk, and exposes only local debug sockets.
Preparation refuses to overwrite existing workspaces. Complete preparation,
controls, exact addresses and hashes: `evidence/vendor-kernel-vm.md`.

The display program bypasses missing framebuffer-driver support by mapping
QEMU VGA PCI resources. **It is not a DRM/EGL/Qt compatibility backend.**
Details and actual screenshots: `evidence/vendor-kernel-graphics.md`.

## Latest local recovery work

Read `evidence/local-ui-recovery.md` and its retained evidence directory.

1. **Boot public-key hypothesis:** all 12 plaintext EU/AU `ipk.` containers
   share one RSA-2048 public key and pass strict signature controls. Scanning
   the first/last 16 KiB of 38 opaque envelopes, at every byte offset and in
   both byte orders, made **2,392,520 RSA attempts and found no valid type-1
   block**. This tests one key, one padding format and recorded edge ranges,
   not every possible wrapped-key location or algorithm.
2. **Installed Mac updater hypothesis:** static inspection of Navigation
   Updater `261.015.0.215` found text/API AES routines and constants. Two
   reconstructed constant pairs were tested against the same 38 files under
   bounded CBC-start/IV hypotheses. Two raw gzip-marker matches were the same
   invalid sample in both packages; reserved flags and zlib rejected them.
   **No validated firmware plaintext was recovered.** Other crypto modes and
   derivations were not exhausted. The updater was not launched or contacted
   online.
3. **Earlier plaintext searches:** full-byte ELF/gzip/tar probing covered
   7,134,873,011 bytes across 14 opaque payloads with no validated candidate.
   Prefixes of 1,571 regular map ZIP members and two distinct plaintext voice
   archives were also inspected. See the graphics evidence for exact bounds.

`new_gui.tar.gz`, `mango-rootfs.tar.gz`, `appnavi.tar` and updater payloads remain
opaque. The publicly saved `DecryptToPIPE` and key files are placeholders.
The older Chimaera work documents a real decryptor/key-file mechanism, but does
not itself establish current-package applicability or supply those artifacts.
High entropy or a failed bounded scan is **not proof of permanent offline
impossibility**.

## Useful local resources

- EU: `/Users/researcher/Downloads/NaU/IONIQ5_EU`, version
  `NE_E.EUR.S5W_L.001.001.260128`, model `101489`.
- AU: `/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU`, version
  `NE_E.AUS.S5W_L.001.001.260319`.
- Supported boot container: EU `HU/images/iasImage_1280_sub`, SHA-256
  `55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0`.
- Kernel, correct symbols and saved Ghidra project: `work/eu-260128/`.
  Use `kallsyms.tsv` / `kallsyms_apply.tsv`, **not** the obsolete mispaired
  `kallsyms_fixed.tsv`. About 70 selected functions were decompiled, not the
  entire kernel.
- Existing static BusyBox: `work/vm/busybox`; QEMU: `/opt/homebrew/bin/qemu-system-x86_64`;
  e2fsprogs and LLVM under `/opt/homebrew/opt/`.
- Harness Python: `/opt/homebrew/bin/python3.13`. Full-test Python:
  `/Users/researcher/.platformio/penv/bin/python3` (includes `cryptography`). Do not
  assume the default Homebrew `python3` works.

```sh
mkdir -p work/test-tmp
TMPDIR="$PWD/work/test-tmp" /Users/researcher/.platformio/penv/bin/python3 \
  -m unittest discover -s tests -p 'test_*.py' -v
```

## Local continuation 2026-10-22: envelope format, module execution, graphics

Verified offline in QEMU against the unmodified vendor kernel `4.1.27-abl`. Artifacts
under `work/ui-recovery/`, `work/kbuild/`, `work/envelope-20261021/`; full runbook in
`work/ui-recovery/SUMMARY-and-runbook.md`. This does **not** unlock the real UI.

- **Envelope format** (all opaque payloads, incl. `iasImage`): `[ciphertext body]
  [0x00][base-255 zero-free footer]`; the footer is package-scoped and decodes to
  uniform ciphertext (no length prefix, not block-aligned). `iasImage` adds a
  14,048-byte (878-block) deterministic prefix. This corrects the earlier
  "3,385 header + payload + 13,035" model (arithmetic, not structure).
- **Boot key inside the envelope:** type-1 public unwrap is a clean negative; type-2
  is the wrong direction (≈1.5e-5 false positives). No offline key.
- **Plaintext resources** (map ZIPs, voice archives) hold map data, fonts, PNGs and
  ASR/TTS models — **no UI/ELF**. `CONFIG_BLK_DEV_INITRD` is unset (no initramfs).
- **Unsigned kernel-module execution works in the stock vendor kernel:** vermagic
  `4.1.27-abl SMP mod_unload`; `MODVERSIONS`/`MODULE_SIG` off. Recipe: build against
  the vendor config, rewrite PLT32→PC32, and shift the `init`/`exit` this_module
  relocations +8 (`struct module` init at 0x130, not 0x128). See
  `work/ui-recovery/SECURITY-FINDING-module-load.md`.
- **Graphics:** a module registers `/dev/dri/card0`, KMS `card0-VGA-1`, **and advertises a
  real 1280x720 mode** with **no Intel GPU** (`drm_mode_probed_add` +
  `drm_mode_connector_list_update`; sysfs iterates `connector->modes` directly, so the
  vendor `funcs->detect` layout mismatch is bypassed). Actual scanout/fbcon still needs
  the vendor's `drm_framebuffer`/CRTC structs.
- **The remaining gate:** the vendor userspace is AES-encrypted in the package; the
  key is `/tmp/<32hex>`, generated on-unit per update by `DecryptToPIPE` (public
  tooling is placeholder-only). On-unit the rootfs/navi are plaintext. Both goals
  (run the real UI; install own apps) need device/rootfs access.

## Next useful work

- **Acquire the plaintext vendor rootfs or the per-update key.** This is now the
  single blocker for both goals. Any read access unblocks it: an engineering-mode
  shell, an `mmcblk0p3`/`p5` + navi dump, or the `/tmp/<32hex>` `DecryptToPIPE` key.
  Runbook (dump → decrypt → boot; key-capture; module path) is in
  `work/ui-recovery/SUMMARY-and-runbook.md`.
- Until then, do not re-probe envelope crypto or DRM struct offsets offline: those
  paths are exhausted (device-gated), as recorded above.
- If genuine application code is recovered, inventory ELF architecture,
  dynamic loader/libraries, launcher/config, services/IPC and display APIs
  **before** trying to execute it in the research VM.
- Keep serial/graphics controls and prepared-image hashes intact. Earlier
  exFAT/archive/XML parser harness work is secondary to the real-UI goal.

## Repository and evidence discipline

The actual Git root is now **this project directory**. Both current remotes,
`ioniq` and `origin`, point to `https://github.com/JaredReabow/Ioniq-5.git`.
Re-query before future integration; the historical parent/Kona layout is stale.
Stage exact reviewed paths, never all of `work/`. No raw firmware, VM disks,
client key bytes or private-key material belong in this continuation's commit.

Primary current notes: `vendor-kernel-vm.md`, `vendor-kernel-graphics.md`,
`local-ui-recovery.md`. Historical exploit, downgrade, partition-map and
trust-pinning claims require their original scope and current-build validation.
No stock-to-root path, authentic payload decryption, bootloader acceptance of a
self-signed image, or hardware flashing has been demonstrated here.

## Public visibility follow-up — 2026-10-28

The sanitized `main` is `ea3fb24fb3af398963ebf17febbef392bb8bd6c3` on the verified `JaredReabow/Ioniq-5` remote. Current remote tree has no owner USB export, upstream raw dump, or frozen Council packet paths; the repository remains private. GitHub still resolves old raw commits `e98e2c8cd1fe477c735907b12c4c0b25976d19c4` and `692eccd380f3a791d800bb6c0ac6dc621af2585a` by SHA. GitHub Support ticket [#4916475](https://help.github.com/ticket/personal/0/4916475) requests server-side cached-view and object cleanup for both. Once GitHub confirms cleanup, verify both old commit IDs no longer resolve, rerun the public harness and unit suite, recheck the explicit remote tree and visibility, then make this same repository public and read back `PUBLIC`. Preserve the existing uncommitted local research and ignored private raw files; do not merge the old Git history into the sanitized branch.
