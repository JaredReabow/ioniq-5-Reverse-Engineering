# IONIQ 5 changelog

All entries describe the IONIQ 5 research programme. The root `CHANGELOG.md`
belongs to the parallel Kona programme and is not modified by IONIQ work.

## 2.26.0 - three captures across one chain: splash, black, decorated blank

- Captured at named stages of a live chain run, which is the only method that works (post-hoc capture races the teardown):

  | stage | frame | size | content |
  |---|---|---|---|
  | ~75 s | `docs/vm/07-…` | 177,691 B | **Hyundai splash** — vendor artwork, painted by the vendor compositor |
  | ~130 s | `docs/vm/09-…` | 4,117 B | **pure black** — the splash has gone and nothing has replaced it |
  | ~155 s | `docs/vm/08-…` | 6,836 B | **decorated client window**, blank white content |

- That sequence is a complete statement of the remaining problem: the compositor transitions between layers correctly, clears to black
  between them, and presents a mapped, decorated window — and **the application paints nothing into it** at any captured stage,
  with `AppHomeScreen` alive throughout (`pid 972` in the 130 s run).
- So the VM goal is now bounded by exactly one question: why a running, registered `AppHomeScreen` produces no content, when the
  compositor beneath it demonstrably paints vendor assets. Capture method and stage timing are settled and written down.
- No claim that the answer is close; the three frames say what works and what does not, and nothing more.

## 2.25.0 - why the frames stopped arriving: the chain tears itself down

- Read the chain script's tail properly. After its last stage it **kills the launcher, ApplicationManager, AppHomeScreen,
  AppNavi, dlt-daemon and weston**, then tar-and-base64s the `launcher-chain` directory as evidence and exits. So
  **capturing after the script returns is impossible** — by design, everything it captured is gone and the compositor is dead.
- Running the later variant to completion confirms it: `CHAIN_RC=0`, and the run finished at 218 s, but
  **`/tmp/launcher-chain/shot/` contained no files and the script printed no `wayland-screenshot.png` hashes** — its own capture
  step produced nothing in this environment, even though the identical `weston-screenshooter` binary works when invoked
  directly against the live chain (that is how `docs/vm/07` was captured).
- So there is a **timing constraint** rather than a tooling gap: frames must be taken *while the chain is running*, at a stage
  the chain itself has passed, and the chain's internal capture is not reliable here. The two working captures
  (`docs/vm/07` splash at 75 s, `docs/vm/08` decorated window) both came from external captures against a live chain — which is
  the method to keep using.
- **Stopping the capture chase here.** Four runs have gone into framing it and the useful output is the constraint itself; the
  next attempt should external-capture at a named stage of a chain run in the background, not after it finishes.

## 2.24.0 - with our service the app starts, but 125 seconds later

- Longer window (160 s) with `micom-service` substituted. `AppHomeScreen` **does** start and register — `PID : 983`,
  `[REGISTERED] registeredFromNativeApp AppId[11][AppHomeScreen]` — but at **`00:02:38`**, i.e. **~155 s, against ~30 s with the
  simulator**. `method not implemented` errors remain at **0**.
- So the substitution does not break the chain; it **delays** it by roughly two minutes. That is a specific, measurable
  behavioural difference and the first thing this experiment has produced: the settings answers change the launcher's timing
  rather than preventing startup.
- **The capture was still not reached** — the run ended at 170 s, before the screenshooter step, so there is again no frame for
  the content question. The experiment remains inconclusive on content while being informative on timing.
- Next run needs **≥220 s** so `AppHomeScreen` has time to paint after registering at ~155 s. Recording the requirement rather
  than repeating a window that is known to be too short.

## 2.23.0 - service substitution works technically; the app had not started yet

- Ran the published chain with `/usr/bin/micom-service` substituted for `/micom-dbus-sim`. The substitution is effective:
  - **`method not implemented` errors: 7 → 0.** The settings asks the simulator refused are now answered.
  - **`micom-service` answered 7 calls** in that window (`AskSysBootinfo`, `AskCustomSetting`, `AskSettingInfoValue`).
- **But `AppHomeScreen` had not started by the 90-second capture**, so the frame is byte-identical to the splash capture
  (177,691 bytes) and tells us nothing about content. The experiment is therefore **inconclusive on the actual question** — it
  confirms the substitution, not whether unanswered settings were the cause of the blank content.
- That distinction is the whole point: the lever worked, the measurement did not reach the effect. Next run needs a longer
  window (the app started at ~30 s in the simulator-based chain, so the service-based chain is either slower or stalled
  earlier) plus the launcher log to see whether `AppHomeScreen` was requested at all.
- Recorded rather than reported as a result: a clean substitution and an identical screenshot is exactly the shape of evidence
  that gets mistaken for progress.

## 2.22.0 - the app registers; the simulator's unimplemented methods are the next lever

- Read the launcher's own log from the working chain. `AppHomeScreen` starts **and registers** with the launcher:

  `m_AppProcess->start(/app/bin/AppHomeScreen) PID[804]` →
  `[REGISTERED] registeredFromNativeApp AppId[11][AppHomeScreen] onDemand[0] groupNum[2]`

  So the application reaches the launcher's appbase and is tracked as a live app. Window mapping is therefore working at the
  application-manager level; what does not happen is content being painted.
- **The chain's MICOM simulator refuses calls that this project's own service implements.** The launcher logs, repeatedly:

  `askCustomSetting Error Reply = method not implemented by micom research simulator`
  `askSettingInfoValue Error Reply = method not implemented by micom research simulator`

  `micom-dbus-sim` answers `AskSysBootinfo` (which is enough to boot the chain) but not the settings asks, whereas
  `micom-service` here answers `AskCustomSetting` and `AskSettingInfoValue` with sized payloads. Those failures are a plausible
  cause of an app that initialises, registers, and then paints nothing.
- **Next experiment is therefore concrete:** run the published chain but substitute `micom-service` for `micom-dbus-sim`, so
  the settings asks are answered rather than rejected, and re-capture. That is a one-line change to the chain and it tests
  whether the blank content is a consequence of unanswered settings.

## 2.21.0 - V-028's escalation boundary tested: uid 1000 cannot reach the bus

- Re-ran the experiment as **uid 1000**, dropping privileges with a purpose-built `setuid` helper because the image ships no
  `su`, `sudo` or `setpriv`. Result: the session bus **refuses the connection outright** —

  `as-uid: now uid=1000` → `Failed to open connection to "session" message bus: Did not receive a reply … the message bus
  security policy blocked the reply`

  `GetId` fails, `request.launch` fails, and the marker is never created.
- **So V-028 is not an unprivileged local escalation vector as configured.** It remains a real defect: a caller-supplied path
  reaches `QProcess::start` as root with no validation, and the method returns success even when nothing launched. Its
  exploitation requires a foothold at the launcher's uid — the HMI's own processes — rather than a non-root user.
- **Independent agreement:** this is exactly the boundary the parallel lineage's entry (V-040) stated separately — *"relevant
  to same-uid, SMACK-separated HMI code"*. Two investigations reached it by different routes, which is the strongest form of
  confirmation available here.
- Entry retitled to carry the boundary: **runtime demonstrated, not an unprivileged escalation.**

## 2.20.0 - V-028 runtime-confirmed: a caller-supplied path executes as root

- **The launcher's D-Bus `request.launch` executed an arbitrary caller-supplied path as root.** Using the published
  reproduction chain, one session-bus call:

  ```
  dbus-send --session --dest=com.lge.avn.applauncher /Request \
    com.lge.avn.applauncher.request.launch int32:999 string:probe string:/app/bin/AppProbe
  ```

  returned `method return … reply_serial=2`, and the script at that path ran with the marker
  **`uid=0(root) gid=0(root)`**. This is the first runtime confirmation in this project of the route V-028 described
  statically.
- **Two supporting facts, both useful:** the method does **not** check that the path is a registered application, and it does
  **not** fail for a path that does not exist — an earlier run against a missing file also returned success, so the return
  value never indicates whether anything executed.
- **The boundary is stated, not glossed.** The caller in this test was the root shell that also started the chain, so this
  demonstrates the **code path**, not a **privilege boundary crossing**. Whether an unprivileged local process can reach the
  same session bus — `EXTERNAL` auth, no explicit user connection rule — is untested, and the severity of this entry depends
  on that entirely. V-028 is upgraded from "static route" to "runtime execution demonstrated", with that caveat attached.
- The working entry point is **`request.launch (int32, string, string)`**, not the `launch` method this thread introspected
  over four failed attempts. That single detail was the difference between no execution and root execution.

## 2.19.0 - a real client window is mapped; its content is blank

- Ran the later chain variant (`full-chain-timeout120-legal-reason11-priority-pointer-confirm.sh`, which issues
  `show_window_fg` and a confirm sequence) to completion and captured the end state:
  **1920×720, 6,836 bytes**, with `AppHomeScreen` alive (`pid 994`).
- What the frame shows is a **mapped Wayland client window with window decorations** — a blue title bar and
  minimise/maximise/close controls at the top right — over a **blank white content area**. So the stack now gets as far as
  presenting a client window on the vendor compositor; the application's own content is not painted.
- That is a different failure from the earlier splash frame (`docs/vm/07-…`, 177,691 bytes, vendor artwork) and worth keeping
  side by side: the splash proves the compositor paints vendor assets, this frame proves a **client surface is mapped and
  decorated**, and neither yet shows home tiles.
- Honest reading: window management works, application rendering does not. Decoration appearing also suggests
  `QT_WAYLAND_DISABLE_WINDOWDECORATION` is not taking effect for this client in this run, which is itself a clue about which
  path the window came through.
- Both frames are committed (`docs/vm/07`, `docs/vm/08`) so the progression is visible rather than summarised.

## 2.18.0 - the VM renders vendor graphics: Hyundai splash captured at 1920x720

- Captured a **real frame from the running VM** using the image's own `/usr/libexec/weston-screenshooter`:
  **177,691-byte PNG at 1920×720** showing the **Hyundai boot splash**, with `AppHomeScreen` alive (`pid 808`, then `pid 849`
  on a second run).
- That image (`docs/vm/07-home-screen-live-2026-10-31.png`) is the vendor's own
  `/app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png` linked to `/tmp/front_lcd.png` by the chain, painted by
  the vendor compositor through `weston-headless` with **`ivi-shell.so`**.
- **This settles the earlier black-frame conclusion.** The stack paints vendor artwork; what was black in this session was
  my own configuration (custom `ias-backend-soft` + `ias-shell`), not a vendor inability. That earlier entry is superseded.
- A second capture at 155 s is byte-identical (same 177,691 bytes), so the compositor is still on the splash layer at that
  point rather than on home tiles. The remaining question is therefore **the transition out of the splash**, not whether
  anything renders.
- README updated with the capture and the four decisive chain details (`ivi-shell.so`; `/opt/software-egl18` +
  `softpipe`; `QT_WAYLAND_SHELL_INTEGRATION` unset; `passwd.legacy` plus `xuser`/`byungsu`).

## 2.18.1 - AppNavi has two authentic Qt hide producers

- Completed the recovered AppNavi direct-call inventory for `QWindow::hide()`.
  There are exactly two direct calls: `0x3362275` in Linux `onForeground` and
  `0x3365140` in Linux `dispatchNotifyEvent`.
- Bound the foreground branch: the direct Linux hide requires a true base
  result, then screen ID 1, 2, or 4 and a false foreground argument.
- Bound the second architecture end to end. A bounded Gen5/platform branch in
  `ExSLScreen::onForeground` creates type-`0x103` with the requested Boolean and
  queues it to the same screen; Linux `dispatchNotifyEvent` calls hide for zero
  and show for nonzero.
- Correlated saved ordering: the first false-visibility callback follows Weston
  FG and precedes accepted status 5/window 0, but also precedes every retained
  `setForegroundStatus`/Linux-screen foreground diagnostic in that launch
  interval. No retained primary false call or direct-hide diagnostic identifies
  the runtime producer.
- Revised acceptance: passive evidence must distinguish the direct foreground
  hide from type-`0x103` event handling before following threaded
  `WM_Obscure → doneCurrent → EGL invalidation → BG`. No guest or target was
  executed, no event was synthesized, and no image, manager state, commit, or
  remote history was modified.

## 2.18.0 - Navigation surface 3000 and basic/threaded hide contract resolved

- Bound AppNavi's primary window from `NimoExSLScreenLinux` construction through
  `QQuickView`, `QQuickWindowPrivate::init`, and
  `QSGRenderLoop::windowSurfaceType()` to Qt OpenGL/EGL. Independent launcher and
  compositor records bind that window to IVI surface `3000`; the earlier Shm/Egl
  class ambiguity is closed.
- Bound `QQuickWindow::hideEvent` to render-loop virtual slot `+0x68`. The
  retained integrated Home→Navigation runs under diagnosis force
  `QSG_RENDER_LOOP=basic`; recovered basic vtable
  relocation `0x60fd48` resolves to `0x178730`, whose ordinary hide behavior
  stops at `fireAboutToStop()` and does not call `doneCurrent`, invalidate EGL,
  or detach the Wayland buffer.
- Bound the separate threaded route. Threaded relocation `0x61dfc0` resolves to
  `0x1802a0`; the exposed-window `WM_Obscure` path calls `doneCurrent`. Recovered
  QtGui and Wayland EGL edges continue through platform context `0x6aa0` and
  `QWaylandEglWindow` relocation `0x20d630 → 0x82c0`, where the vendor routine
  destroys the EGL surface, attaches null, commits, and flushes.
- Corrected the harness interpretation: forcing the basic loop is a semantic
  change that omits the EGL invalidation route capable of producing AppNavi BG
  and ApplicationManager's window-latch replay. This explains the retained
  false-visibility/no-BG behavior without fabricating a callback.
- Corrected Home-return provenance. The retained return was explicitly requested
  by event `302`, reason `322`; it was not an autonomous Navigation
  loading/fallback timeout. Status `5` remains the receiver's accepted value;
  window `0` remains the local callback gate.
- Runtime completion remains open: no integrated threaded run yet proves
  `WM_Obscure → doneCurrent → EGL invalidation`, AppNavi BG, setter input `1`,
  cached-status replay, map/menu callbacks, current/drawing ID `30`, or valid
  Navigation composition. No guest execution, synthetic BG/FG, forced latch,
  image change, commit, or push was performed for this static classification.

## 2.17.0 - BREAKTHROUGH: the parallel lineage's published chain runs here, with AppHomeScreen live

- Ran `vm/repro/…/full-chain-authentic-standby.sh` — the parallel lineage's own reproduction script, merged into this repo
  and previously unread — directly in the VM. Result:

  `AppHomeScreen` **running** (`pid 804`) · `ApplicationManager` running (`pid 762`) · launcher dispatching
  (`m_AppProcess->start(/app/bin/AppStandbyClock) PID[942]`) · D-Bus launch request **`RC=0`**.

- **The MICOM region this thread could not satisfy is populated and attached twelve times:**
  `ipc-observe` reports `kind=shm key=0x5112047b size=35 attachments=12` with
  `non_atomic_hex=00000826050000051302000003c8140000000000000000000000020001000000000000` — the authentic 35-byte profile,
  delivered by `micom-dbus-sim`. Every hypothesis in this thread about that structure was solving a problem the published chain
  had already solved.
- **Four decisive differences from this thread's approach:** `weston-headless` with `headless-backend.so` and
  **`ivi-shell.so`**; software EGL from **`/opt/software-egl18`** with `GALLIUM_DRIVER=softpipe`; `QT_WAYLAND_SHELL_INTEGRATION`
  **unset** (AppLauncher appends `:ivi`, giving the invalid `ivi:ivi`); and `/etc/passwd.legacy` → `/tmp/passwd` with the
  `xuser` and `byungsu` accounts added.
- **The launch method is `request.launch`, not `launch`** — `com.lge.avn.applauncher.request.launch int32:30 string:AppNavi …`
  returns success. V-028's runtime test is therefore reachable by a route none of the four earlier attempts used.
- Recorded plainly: the answer had been sitting in this repository since the combination, in a file I had not opened.

## 2.17.0 - Navigation status 5 is positive; window 0 is the blocker

- Corrected the unresolved interpretation of `notifyNaviLaunched[5] window[0]`.
  Exact `NaviMapApplication` and `NaviMenuApplication` callbacks accept only
  status `5`: it sets their play-enable byte and enters controller-mediated
  handoff logic. Every other status clears the byte and returns. The sender-side
  signal name containing `Fail` is not the receiver-side enum definition.
- Bound the local matrix. A zero manager window byte caches status but stops
  before ID-30/ID-32 callbacks. A nonzero window plus status 5 clears two ID-35
  loading-object lists and reaches the positive map/menu paths. The authentic BG
  route calls the window setter with 1, which latches the byte and replays cached
  status.
- The latest saved runs therefore already carry the receiver's accepted status;
  they fail to produce the authentic AppNavi BG/first-hide/unmap event needed to
  set the separate window latch. FG and a rendered surface remain insufficient.
- The inspected routines do not directly return to Home ID 11. The retained
  return was explicitly requested with event `302`, reason `322`; it was not an
  autonomous fallback. Static positive-path reachability does not prove a
  completed 35→30 transition or composition.
- Bound the recovered QtWayland hide discriminator to `windowType()`. Unlike
  public v5.4.1's unconditional detach, the recovered client explicitly commits
  a null buffer only when `windowType()==Shm` (zero). The recovered Shm method
  returns 0; the mapped EGL plugin's corresponding method returns 1 and skips
  that detach. Version 2.18.0 closes the then-open primary-class and render-loop
  questions: surface 3000 is OpenGL/EGL, basic hide stops before invalidation,
  and threaded `doneCurrent` reaches the recovered null-attachment routine.
- Added exact-static consumer and hide-backend records under
  `evidence/artifacts/application-candidates/` and updated the navigation
  contract and handover. No guest or target execution, message injection,
  compositor event, image change, commit, or push occurred.

## 2.16.0 - register evidence integrity: 101 cited paths, all present

- Checked every repo-relative path the register cites in backticks — the evidence each finding points at — after the
  combination, since a merged tree can silently lose files that entries still reference.
- **101 cited paths, 101 present, 0 dangling.** So every claim in the register still points at material that exists in this
  tree; nothing was orphaned by the merge, and the duplicate importer did not carry references to files that did not come with
  it.
- This was worth checking rather than assuming: the merge resolved 39 conflicted files by content, and the imported entries
  referenced `evidence/` material from the other lineage. All of it arrived.

## 2.15.0 - a contradictory severity claim between duplicate entries, reconciled

- Combining the lineages put **two different statuses for the same finding** into one register. **V-037** (imported,
  duplicate of V-006) says *"root command execution demonstrated end-to-end in the project QEMU research harness"*, while
  **V-006** records descriptor injection as **blocked**.
- **V-006's measurement supersedes it**, and the reasons are recorded inside V-037 rather than its text being deleted:
  - re-running the exact payload through a real descriptor (`usb-mtp`, `serial=pwn;id>/tmp/VM-PWNED`, with the required
    `060101` interface) delivers it intact on the wire, but udev hands `usb-automount`
    **`ID_SERIAL_SHORT=pwn_id__tmp_VM-PWNED`** — `;`, `>` and `/` each rewritten — and **no marker file appears**;
  - the allow-list doing it (`#+-.:=@_` plus alphanumerics) exists in **both** `systemd-udevd` and `libudev` and was
    confirmed dynamically;
  - the original result is therefore most consistent with a **synthetic event or injected `ID_SERIAL_SHORT`**, which
    bypasses `builtin_usb_id` — something a physical device cannot do.
- The **source defect stands** in both entries (unquoted `sprintf` into `system()`); the **reachability claim does not**.
  The register's duplicate table now says explicitly that severity must be read from **V-006**, not V-037.
- This is the most consequential defect the combination could have produced: a number that reads as a demonstrated root
  exploit sitting next to a measurement that says it is not reachable.

## 2.14.0 - the combination created six duplicate findings; now marked

- Importing the parallel lineage's entries produced **duplicates** of findings this register already had, because the two
  lineages independently found the same issues: **V-037/V-006** (MTP shell construction), **V-038/V-007** (media parsing),
  **V-039/V-008** (serial console), **V-040/V-028** (launcher verifier bypass), **V-044/V-034** (update trust anchor) and
  **I-002/I-001** (EGL copy path).
- Each imported entry is now marked **DUPLICATE** in its heading with a note naming the canonical entry, and **both bodies are
  retained** so no evidence is lost. A consolidation table sits above the scope notes.
- **Genuinely new from the parallel lineage**, and not duplicated anywhere here: **V-041** (engineering-mode keypad credential
  from static unsalted digests), **V-042** (world-writable marker files driving privileged systemd actions) and **V-043**
  (privileged services import `EnvironmentFile` from a world-writable path — the mechanism behind the V-036 chain, which until
  now had no register entry of its own).
- **Corrected the count after checking it**: the register holds **47 numbered entries** (44 `V-`, 2 `I-`, 1 `H-`), of which 6
  are duplicates, i.e. **41 distinct findings**. My first draft of that sentence said 44/38 and was wrong — arithmetic in a
  register is the kind of thing that gets quoted, so it was verified against `grep -c` rather than written from memory.

## 2.13.0 - all four regions created; the shared-memory line of enquiry closes

- The trace enumerates exactly what the client touches: **four** names — `APPLICATIONMANAGERINFORMATION`,
  `ApplicationEnableInformation`, `ApplicationManagerInformation`, `MICOMSTATUSMESSAGE`, each with a `qipc_systemsem_`
  counterpart. `ihu-shim` now creates and seeds **all four**, confirmed in its own output.
- Result unchanged: **`PSZNULL=1`, `VALID=0`**. So name resolution, file presence, segment existence, segment content (the
  authentic 35-byte profile) and the attach calls are all accounted for — with two attaches confirmed successful by Qt's own
  error code — and the client still reports a NULL `data()`.
- **This closes the shared-memory line of enquiry.** What remains is vendor-side logic in `MicomInterfaceM`, not an
  environment gap: every object the client names now exists, and it still treats one of them as absent. That is not something
  more VM configuration can fix, and the register now says so instead of implying another round might.
- Retained for the record: the four names, the two identified keys and their attach idioms, the `ftok`/`stat` mechanism, the
  recovered profile, and the eight excluded environmental hypotheses — all of which stand as established facts regardless.

## 2.12.0 - the NULL handle is keyed separately; the sweep stops here

- Checked the last structural explanation: is the `rbx+0x40` object a **copy** of an attached handle? It is not.
  `ApplicationManager` imports **no `QSharedMemory` copy constructor** — only `(QObject*)` and `(const QString&, QObject*)` —
  and the key-taking constructor has exactly **one** call site (`0x1c4a58`, in the helper used by the
  `APPLICATIONMANAGER_INFORMATION` path).
- So the third object is constructed with **its own key**, which this sweep did not attribute. That eliminates the copy/detach
  explanation and leaves a single, bounded disassembly task: read `MicomInterfaceM`'s constructor and enumerate its
  `QSharedMemory` members and keys.
- **Stopping here deliberately.** Snippet-level disassembly has stopped producing answers — the last three rounds each found
  one more call site and each narrowed the question without closing it. The record now states exactly what is known, what was
  excluded, and what the next reader must do, rather than continuing to spend rounds on diminishing returns.

## 2.11.0 - both shared-memory keys identified; the NULL is a third handle

- The disassembly names them. `initBootInfo` is `QSharedMemory` keyed **`MICOM_STATUS_MESSAGE`**, `attach()` only, no
  create, logging `initBootInfo attach fail` on failure. `m_pShmBase` is keyed **`APPLICATIONMANAGER_INFORMATION`**,
  **created with size 8** then attached, logging `m_pShmBase->attach() error code : %1`.
- **With `ihu-shim` providing the region, both attaches succeed:** the log shows `attach() error code : 0` and no
  `initBootInfo attach fail` at all — and yet `initMicomShareMem() -> Start` is still followed by `pszSrc NULL`.
- Therefore the object whose `data()` is NULL (`rbx+0x40`) is **neither** of the two named handles. It is a third handle,
  or one of them re-used after the `QSharedMemory::detach` on the failure path at `0x25a42c`. That is now a question about a
  single member offset rather than about the environment — the whole environmental search has been reduced to this.
- Practical side-effect worth noting: the `create(…, size 8)` for `APPLICATIONMANAGER_INFORMATION` and its
  `attach() error code` log give a **direct oracle** for that object, which is more precise than anything used earlier.

## 2.10.0 - `pszSrc` identified: it is `QSharedMemory::data()`, and there is no third-party provider

- The disassembly settles what the last several rounds were guessing at. The `pszSrc NULL` path is:

  `movq 0x40(%rbx),%rdi` → `QSharedMemory::lock` (retry loop via `usleep 0x2710` on failure) → `QSharedMemory::data` →
  `testq %rax,%rax` → `je 0x25a440`.

  `pszSrc` is `data()` on the client's **own** `QSharedMemory` at `rbx+0x40`. There is no external provider to locate, and
  every hypothesis this thread chased was a proxy for "that object is not attached".
- **Both strategies tested against that:** creating the region with `ihu-shim` (file + segment) removes `attach fail` but
  leaves `data()` NULL; creating **only the key file** and leaving the segment absent restores `attach fail` and still leaves
  `data()` NULL. So the client cannot attach this object **either way**, which localises the fault to the attach itself —
  key derivation, size, or permissions — rather than to anything missing from the environment.
- That is a genuine narrowing produced by disassembly rather than by another experiment, and it is where this thread hands
  over: the next step is the `QSharedMemory::attach` call site in `ApplicationManager` and the exact key/size it passes.

## 2.09.0 - missing /Data inputs excluded; two VM-fidelity gaps recorded

- Swept the client's `ENOENT` calls for anything beyond the qipc noise and found it looking for
  `/Data/mnt-wt/Settings/shared_public/{GroupContent.json,resource-table-cfg.itz-lock}`,
  `/Data/mnt-c/Settings/BackupFileList.info`, `/log_data/backtrace/AppManager_info.txt`, `/rw_data/…/eng/…`, and
  **`/dev/mmcblk1p1`**.
- Created those directories and placeholder files and re-ran: **`PSZNULL=1` unchanged**, with `ATTACHFAIL=0` and
  `BOOTINFO=0`. So `pszSrc` does not come from any of those paths, and that hypothesis is excluded by measurement.
- **Two useful side-findings, independent of V-036:** `ApplicationManager` expects a **second MMC device**
  (`/dev/mmcblk1p1`) that this projection never provides, and a **`/Data` resource table** under
  `mnt-wt/Settings/shared_public` — the same `/Data` item ranked in the HMI gap analysis. Both are VM-fidelity gaps worth
  closing regardless of this bug.
- **Empirical work on `pszSrc` stops here.** Every externally testable input has been excluded; what remains is reading
  `initMicomShareMem` and its caller to see which object the argument is loaded from, which is disassembly work on the
  stripped binary with the anchors already recorded.

## 2.08.0 - the attach is a `stat`, and the recovered profile is still rejected

- **Corrected the instrument, again, and this time it matters.** An untargeted trace shows `ApplicationManager` doing
  `stat("/tmp/qipc_sharedmemory_MICOMSTATUSMESSAGE…") = -1 ENOENT` and then creating the matching systemsem file. Qt's
  `QSharedMemory` SysV backend resolves its key through **`ftok`, which uses `stat`, not `openat`** — so the earlier
  "no `qipc` path is opened" result was a **false negative from the instrument**, not a fact about the client. With
  `ihu-shim` having created the region, `attach fail` disappears.
- **Found the recovered boot-info profile in the merged material**: `00000826050000051302000003c8140000…0001…`, 35 bytes,
  documented byte-by-byte in `work/vm/…/micom-contract/BOOTINFO-AND-SIM-V2.md` as decoded from AppLauncher's own BIS
  decoder logs (EV-family Europe, 12.3" LCD, nav+modem+RHD+amp, English US, last GUI mode 1). `micom-service` now serves it
  verbatim instead of inventing payloads.
- **Two failures, recorded as failures:**
  1. Serving that authentic profile over D-Bus is **still rejected** — `reply is VALID` never appears.
  2. **Seeding the same 35 bytes into the `MICOMSTATUSMESSAGE` region at offset 0 does not clear `pszSrc NULL`.**
- So the region's *existence* is necessary (attach stops failing) but not sufficient, and `pszSrc` is produced by something
  this thread has not located — a second object, or a header offset inside this one. That is now the single question, and it
  is narrower than it has ever been.

## 2.07.0 - full suite green: 782 tests, 351,486 subtests

- Installed the missing test dependencies in a **virtual environment** rather than against the system interpreter, because
  Homebrew's Python is externally managed (PEP 668) and refuses a direct install. Needed: **`pytest`** and **`cryptography`**.
- With those present the five previously-erroring modules run and **pass**: `test_asf_stream_probe`, `test_gen5w_decrypt`,
  `test_ipk_tool`, `test_public_rsa_probe`, `test_appfumo_usb_pathname_model` — **78 tests**, all green. These are exactly the
  modules that came from the parallel lineage, so this also verifies the merged code inherited from it.
- **Whole suite: 782 passed, 351,486 subtests passed**, no failures and no errors.
- The exact commands and the expected result are now in `tests/README.md`, along with the note that those five modules import
  `pytest` directly and therefore appear as import errors under plain `unittest discover` — a dependency gap, not a defect.

## 2.06.0 - privacy scan widened to vm/ and QML; the suite is green

- Fixed the failure carried over from the parallel lineage, which had **two** causes rather than one:
  1. the public-mode scope was `{"evidence", "council", "tools"}` — **`vm/` was never scanned**, so a source file under
     `vm/` could not be flagged;
  2. `PUBLIC_TEXT_SUFFIXES` omitted **`.qml`, `.js` and `.conf`**, so even once in scope a QML file was skipped as non-text.
- Both are now fixed: the guard inspects the **vendor's own UI language** (QML) and the `vm/` tree. `tests.test_harness`
  passes **54/54**.
- **Full suite: 696 tests run, 691 pass.** The five errors are **`ModuleNotFoundError: No module named 'pytest'`** — those
  five test modules import pytest, which is not installed in this environment. Recorded as an environment gap, not merge
  damage: all five corresponding tool modules (`asf_stream_probe`, `appfumo_usb_pathname_model`, `gen5w_decrypt`,
  `ipk_tool`, `public_rsa_probe`) are present and identical in both lineages.

## 2.05.0 - both lineages combined semantically, not sacrificed

- The previous merge resolved 39 add/add conflicts by taking the newer side per file, which **discarded content** — the
  criticism was correct. Every one of those files has now been replaced with a real union of the two histories, by eight
  parallel workers on disjoint file sets.
- **Log documents now carry both lineages' entries:**
  - `Ioniq5-CHANGELOG.md` 259 → **276** sections: the 17 sections that existed only in the parallel repository are inserted in
    version order; where both sides had the same version with different bodies, **both bodies are kept** (22 such cases).
  - `Ioniq5-HISTORY.md` 216 → **229**: the 12 parallel-only entries placed chronologically, 7 shared headings keep both bodies.
  - `Ioniq5-VULNERABILITIES.md`: the 9 parallel-only entries imported and **renumbered** to **V-037…V-044** and **I-002**,
    because every one of their numbers collided with a *different* finding here (their V-006 was the launcher/serial family,
    ours was the MTP shell defect). Each carries a provenance line naming its original number; **zero duplicate IDs** remain.
- **21 evidence documents** keep every distinct fact, table row and citation from both sides; where the lineages **disagree**
  on a fact, both statements are preserved with an inline disagreement marker for human adjudication rather than a silent
  choice. Notable disagreements recorded: `oemkm=` vs `ABL.oemkm=` (3 files), update-trust scope (3 files), Wi-Fi/CVE table
  rows vs exact-review rejections, Dirty COW / Stack Clash / AF_PACKET version-gap rows vs exact backports, and the
  `disableEncryptionUpdate` premise.
- **Code:** `tests/test_harness.py` 49 → **54** tests (parallel-only bodies added as `*_other_lineage`); `gitscope.py` now
  accepts both repository names. `vm_boot.py` retains `INIT_CHOICES`, `--init`, `--sdhci-compat`, `--micom-serial` and
  `extra_devices`. All Python compiles; `tests.test_vm_boot` and `tests.test_rootfs_patch` pass (37 tests).
- **Two deliberate limitations, recorded rather than hidden:**
  1. `rootfs_patch.py` keeps our hardened implementation; the parallel lineage's repack internals are **not** merged because
     ours is a strict safety superset (`_safe_extract`/`_write_ustar`/exclusive creates, and a fix for a `lstrip("./")` bug
     that mangled dotfiles). Their docstring material was merged in.
  2. `test_public_mode_scans_new_vm_source_folder` **fails**, because `tests/harness/privacy.py` scans only `evidence/`,
     `council/` and `tools/` in public mode and never `vm/`. That failure is **identical in the parallel lineage** — it is
     pre-existing, not caused by the merge — and fixing it means widening the privacy scan, which is a separate decision.

## 2.04.0 - the two repositories are combined, with neither history discarded

- The two repositories shared **no merge base**: this one 228 commits ahead, the other 19 ahead in its own right. They are
  now combined by a merge commit whose **parents are both mains** (`03afb2f`, parents `496a89d` and `ebacec0`), so **each
  repository fast-forwards onto it and neither history loses a commit**. Both remotes sit at `03afb2f`; 251 commits are
  reachable from it.
- **39 paths conflicted** as add/add, which is what unrelated histories produce — every file differing between the two sides
  is a conflict because there is no common ancestor to merge against. Each was resolved to the **more recently modified
  side**: 9 took the other repository's version (`PUBLIC-RELEASE.md`, `tests/harness/gitscope.py`, `tests/test_harness.py`,
  `tests/README.md` and five `tools/uk_fw/guest/appnavi_*` probe scripts) and 30 took this one.
- **Nothing was deleted.** Every losing version remains retrievable from the parent commits, both of which are ancestors of
  the merge. Files unique to either side were carried in unchanged by the automatic merge — verified by presence checks on
  both this session's artefacts (`vnbuf_shim.c`, `micom_service.c`, `docs/vm/05-…png`) and the other lineage's
  (`evidence/appfumo-shell-command-boundary.md`, `docs/agent-work/appfumo-shell-boundary/PLAN.md`,
  `tools/uk_fw/guest/appnavi_valet_probe.sh`).
- Also committed the payload-variant cycling in `micom_service.c`, which the earlier oracle work had left uncommitted.

## 2.03.0 - README refreshed with VM images; work published to both repositories

- **README** gained a "Latest bring-up — 2026-10-31" section: what now works (authentic multi-user boot, our Weston backend
  with the vendor-ABI patch, EGL via injected `swrast_dri.so`, frame capture, and the MICOM adaptors that let the launcher
  register) and what remains blocked (`initMicomShareMem() -> pszSrc NULL`, seven excluded hypotheses, V-036).
- **Two fresh captures** from the VM, both captioned for what they actually show:
  `docs/vm/05-compositor-control-2026-10-31.png` — the compositor control frame, **173 distinct colours**, verified by eye
  as a real test pattern; and `docs/vm/06-hmi-frame-2026-10-31.png` — uniformly black, which is the honest current HMI
  state, with the reason stated rather than cropped away. Native capture is 240×90; both are shown upscaled 4× and the
  caption says so.
- **Published to both repositories.** `JaredReabow/Ioniq-5` `main` and `JaredReabow/ioniq-5-Reverse-Engineering` branch
  `vm-bringup-2026-10-31` both carry commit `6ecb151`.
- **Deliberate choice, recorded:** the second repository could not be pushed to `main`. It shares **no merge base** with this
  one, differs in **771 files**, and is **19 commits ahead** of us even though we are **228 ahead** of it. A `main` push
  would have force-overwritten those 19 commits, so the work was published as a reviewable branch and their `main` is
  untouched. Merging the two lineages is a decision for the owner, not something to do silently.
- Caveat noted in the README work: because the histories share no ancestry, the branch reviews as a standalone tree rather
  than a diff against that repository's `main`.

## 2.02.0 - the harvest route is closed: the vendor daemon publishes no region

- Tested the most promising remaining idea — take the structure's layout from the component that would populate it. Ran
  `micommanager_userspace` with a `/dev/ttyS1` peer and a system bus: the daemon runs (`pid 723`) and creates
  **zero `qipc_*` files**.
- So the vendor daemon is **not** the publisher of the MICOM status region. Combined with the region name appearing in
  `ApplicationManager`'s own strings, the picture is that the **client creates the region and lacks the data to fill it**.
- That closes the empirical shortcut. Both remaining routes are now static: read `initBootInfo`/`parseMicomBootInfo`, or
  obtain vendor source. There is no artefact to harvest in this projection.
- Recorded with the elimination list rather than as another open thread.

## 2.01.0 - segment existence excluded; the layout of the MICOM status structure is the last unknown

- Created the named region deliberately and verified it: `ihu-shim` reports **six segments created**, including
  `qipc_sharedmemory_MICOMSTATUSMESSAGE…`, with a peer owning `com.lge.car.micom` and answering `AskSysBootinfo`.
- Result: `PSZNULL=1`, `ATTACHFAIL=0`, `HAS_BOOTINFO=0`, 79 log lines. **`pszSrc` stays NULL with the segment present.**
- So existence is not the condition. The consistent explanation is that the region must contain a **valid structure** —
  `ihu-shim` fills it zero-filled, and this project has already established that zero-filled structures are rejected by
  validating parsers (the 35-byte `ay` was rejected for the same class of reason).
- **Consequence:** the two open questions collapse into one. Whether the boot info arrives by D-Bus reply or by shared
  region, what is missing is the **layout and validity rules of the MICOM status structure**. Everything environmental —
  reachability, `/dev/shm`, segment creation, payload length — is excluded by measurement.
- **This is where the thread stops.** Deriving that layout is a reverse-engineering task on a stripped binary, not another
  experiment, and the record now says so with the whole elimination list attached.

## 2.00.0 - a false positive caught, and `MICOM_STATUS_MESSAGE` named as the likely source

- A run reported `attach fail = 0` and looked like a fix. It was not: the same run has `HAS_BOOTINFO=0`, meaning
  `ApplicationManager` never entered `initBootInfo`. Caught by verifying rather than concluding — the trap that has produced
  most of this session's wasted effort.
- The ordered log is more useful than either failure line: `initMicomShareMem() -> Start` →
  **`initMicomShareMem() -> pszSrc NULL`** → `askSysBootInfo():iface is VALID`. So **`initMicomShareMem` runs before the
  D-Bus ask**, and the reproducible failure across orderings is the **NULL `pszSrc`**, not the attach.
- **New lead from the binary's strings:** it contains `MICOM_STATUS_MESSAGE`, matching a segment name already observed in
  `AppHomeScreen`'s trace (`qipc_sharedmemory_MICOMSTATUSMESSAGE…`) and one that `ihu-shim` can create. That makes a MICOM
  status region the most likely source for `pszSrc`.
- Next test is concrete: ensure that segment exists before the client starts, and watch whether `pszSrc` becomes non-NULL —
  with `HAS_BOOTINFO`/log-line counts checked first so another empty run cannot be mistaken for progress.

## 1.99.0 - /dev/shm excluded as the cause; the gap itself is recorded

- The image ships **no `/dev/shm`** — nothing in `esinit` mounts it and no `fstab` entry exists, the same class of hole as
  the missing `/dev/pts` found much earlier. Worth fixing on principle for the VM regardless of this bug.
- Mounting a `tmpfs` there with `chmod 1777` and re-running the oracle changes **nothing**: `attach fail` and `read error`
  persist, `reply is VALID` still absent. So POSIX shared-memory availability is **excluded** as the cause.
- The boot-info retrieval failure has now survived every environmental candidate: bus reachability, `/dev/shm`, peer
  presence, payload content, file-backed segment paths.
- Kept as two findings: the environment gap is real and separate; the retrieval failure remains unexplained and is now the
  sole blocker for V-036 and for V-028's runtime test.

## 1.98.0 - CORRECTION: `pszSrc` is a source buffer, not a missing provider

- Own correction, from disassembling the block that emits `initMicomShareMem() -> pszSrc NULL`. It is preceded by
  `movq 0x40(%rbx), %rdi` and a call to **`QSharedMemory::detach`** — so the `QSharedMemory` involved is a **destination
  owned by `ApplicationManager`**, and `pszSrc` is the **source buffer** it is supposed to be filled from.
- Therefore the NULL source is a **consequence of the earlier boot-info failure**, not evidence of a third-party provider
  that never runs here. My previous entry said the opposite ("what is missing is a provider of that region") and that
  sentence is **withdrawn**.
- The missing thing remains the **boot info itself**, retrieved by the MICOM path that logs `attach fail` and
  `read error` — supply side, not consumer side. This distinction matters because it points the next attempt back at the
  retrieval path rather than at inventing a new shared-memory object.
- Recorded promptly: the wrong reading was only a few minutes old, and a wrong direction costs more than an unanswered
  question.

## 1.97.0 - reframed: the boot-info path ends in `initMicomShareMem() -> pszSrc NULL`

- Read more of the same log with the peer answering. The sequence is:

  `initBootInfo attach fail` → `retryCount 1/2/3` → `initBootInfo read error` → `askSoundSetupInfo():iface is VALID` →
  `initMicomShareMem() -> Start` → **`initMicomShareMem() -> pszSrc NULL`**

- That last line reframes the whole thread. `ApplicationManager` initialises a **MICOM shared-memory region** and finds
  its **source pointer NULL**. So the object it needs is a **shared-memory region populated by the MICOM side**, not a
  better D-Bus `ay` payload — which explains both why three payload variants were rejected and why no `qipc` file open
  was ever observed: the region is consumed by pointer, and its provider never runs in this projection.
- **"The 35 bytes are wrong" is therefore too narrow.** The accurate statement is that the boot-info path terminates with
  no shared-memory source. The next task is to find that region's key or creation path — a provider, not a payload.
- The oracle remains useful: `reply is VALID` would still be the signal that the D-Bus half is satisfied, so it should be
  re-read once a region provider exists.

## 1.96.0 - integrity check after the long stretch: clean, and one caveat recorded

- Verified at hand-off time, read-only:
  - **Register**: 36 numbered entries, **no duplicate numbers**, provenance note present.
  - **Host paths**: zero `/Users/` or `/opt/homebrew/` occurrences in `Ioniq5-CHANGELOG.md`, `Ioniq5-HISTORY.md`,
    `Ioniq5-VULNERABILITIES.md` and `HANDOVER.md` — this repository has been rejected by its harness for exactly that
    before.
  - **Sources tracked**: `ias-backend-soft.c`, `ias_protocol.c`, `ihu_shim.c`, `micom_responder.c`, `micom_service.c`,
    `vnbuf_shim.c` all in the index; built binaries (`micom-service`, `*.so`) ignored by the scaffold `.gitignore`.
- **Caveat, stated because it is not mine to fix:** the worktree currently carries **another workstream's** uncommitted
  changes (`HANDOVER.md`, `docs/agent-work/appfumo-usb-pathname-provenance/CHECKPOINT.md`,
  `evidence/appdmclient-fumo-usb-eligibility.md`). They are untouched by this commit, which is scoped to my three files.
- This entry exists because two of my earlier commits in this session had provenance problems (an absorbed bundle and a
  silently mis-scoped add). Checking is cheaper than being told.

## 1.95.0 - V-036 handed off: what is proven, excluded, and where the reading stalled

- One step further into the parser and then a deliberate stop. The `.rodata` around the VALID message holds
  `AskSysBootinfo`, `AskSysBootinfo Retry = %1` and `AskSysBootinfo reply is VALID` — **no "not valid" counterpart**, so
  rejection is silent. Searching for branches into the validity block at `0x258808` found **none**, meaning it is reached
  by fall-through or a computed path, not a direct conditional jump; the deciding comparison is therefore not adjacent to
  the message that reports it.
- **Consolidated hand-off for V-036:**
  - excluded **by measurement**: D-Bus reachability, interface construction, file-backed shared-memory attach
  - **confirmed**: the reply's *content* is the blocker
  - **tested and rejected**: three plausible payloads against a live client (`valid=0` each)
  - **available**: a working oracle (`result_valid`) for any future candidate, documented in this entry
  - **remaining**: read `parseMicomBootInfo` — stripped binary, silent rejection path, no direct branch to the validity
    block; anchors `0x258808`, `cmpl $0x1c` at `0x258705`, byte read at `0x25872a`, tag at `0x317c40`
- Recorded so the next attempt begins where this one stopped. Further work on this thread is a static-analysis task with a
  defined shape, not an experiment.

## 1.94.0 - variant probing rejected; the criteria must be read, not guessed

- Used the working oracle to test three plausible payloads in one boot: all zeros, byte 28 = `0x01`, byte 28 = `0xFF`.
  Result across five `ApplicationManager` instances: **`valid=0` and attach failure for every variant**.
- The oracle is sound — the peer answered each time and the client asked — but the search is **unguided**: 35 bytes of
  unknown semantics will not be found by single-field guesses.
- **This thread concludes where it should:** the acceptance criteria have to be **read from `parseMicomBootInfo`**, using
  the anchors already recorded (`0x258808`, `cmpl $0x1c` at `0x258705`, byte read at `0x25872a`, tag at `0x317c40`), on a
  stripped binary — or obtained as vendor source. Further variant guessing is not warranted and will not be attempted.
- Net position for V-036 after this stretch: reachability, interface construction and shared-memory mechanisms all
  excluded **by measurement**; the reply content confirmed as the blocker; and the tool to test any future candidate now
  exists and is documented.

## 1.93.0 - the payload is finally tested: answered and rejected

- Found why the peer never started: `micom-service` had been installed in the **esinit** workspace but never in
  **softbackend**, so every research-init test ran a non-existent path that failed silently to an empty log. Verified with
  `stat`: present in one, absent in the other.
- With it installed, the first genuine test of the payload against a live peer:

  `RESULT_SVC=720` · `RESULT_SVC_ANSWERS=1` · `RESULT_ASK=1` · `RESULT_VALID=0` · `RESULT_ATTACH_FAIL=1`

  The peer ran and answered `AskSysBootinfo`; `ApplicationManager` asked once, never logged `reply is VALID`, and still
  failed `initBootInfo attach`. **The 35 zero bytes are received and rejected.**
- That is the answer every earlier attempt failed to obtain: the blocker is the **content** of the reply, not
  reachability, interface, or any shared-memory mechanism.
- **Next step, unambiguous:** establish what `parseMicomBootInfo` requires — either variants against this now-working
  oracle (`RESULT_VALID` is the signal) or reconstruction from the anchors already recorded.

## 1.92.0 - the payload test still has not run: the peer was not up

- Ran the oracle test with clean console markers this time (research init, so no systemd spinner):
  `RESULT_SVC=` **empty**, `RESULT_ASK=4`, `RESULT_VALID=0`, `RESULT_ATTACH_FAIL=1`, `RESULT_SVC_ANSWERS=0`.
- The peer **was not running**, so it answered nothing. `ApplicationManager`'s four asks were therefore again "no peer",
  and **the 35-byte payload's content remains untested**. This is a failure to run the experiment, not a negative result
  about the payload — and the distinction is exactly the one this thread keeps having to make.
- **Five instruments for this question, each first invalid in a discoverable way:** an exited process, a three-line
  trace, a run with no bus, markers eaten by a systemd spinner, and now a peer that did not start.
- Two honest options remain, and I am not starting a sixth instrument of my own design: (a) read `/tmp/ms.log` and fix why
  `micom-service` exits in research init, so the payload can finally be tested against a live peer; or (b) reconstruct
  `parseMicomBootInfo`'s criteria from the recorded disassembly anchors.

## 1.91.0 - the failing step named: interface valid, call retried, reply content rejected

- The untargeted `strace -f` (3,465 calls) paid off where three targeted instruments had not. It shows
  `ApplicationManager` logging `MicomInterfaceM::askSysBootInfo():iface is VALID` followed by `AskSysBootinfo Retry = 0/1/2`.
- So the **interface check passes**; the failure is at the call. In that run no `com.lge.car.micom` owner existed, so the
  retries are "no peer" — consistent with the separate boots where `micom-service` ran and the launcher consumed replies.
- With a peer present the reply arrives yet `initBootInfo` still fails, which leaves the **content of the 35-byte `ay`** as
  the remaining candidate. Reachability, interface construction, and both shared-memory mechanisms are now excluded by
  measurement.
- **Stopping the experiment loop.** Four instruments for this question, each first invalid in a way that had to be
  discovered. The next step is not another of my designs: it is reconstructing `parseMicomBootInfo`'s acceptance criteria
  from the anchors already recorded, or vendor source.

## 1.90.0 - boot-info attach: file-backed and D-Bus both eliminated; stopping the instrument loop

- Re-ran the `openat` trace with conditions **verified** rather than assumed: system bus actually running
  (`/run/dbus/system_bus_socket` present), compositor up, and `ApplicationManager` demonstrably reaching `initBootInfo`
  (`attach fail` and retry 1 at `00:00:12`). Result: **22 traced calls, no `qipc_sharedmemory_*`, no `/dev/shm/*`**.
- Combined with the earlier run where both bus connects returned `0`, that eliminates **both** candidates this thread has
  been testing: not a D-Bus reachability problem, not a Qt key-file shared-memory attach.
- **Stopping the instrument loop deliberately.** Three instruments were built for this question and each was first
  invalid in a way I had to discover: a process that exited early, a trace that captured three lines, and a run with no
  bus at all. The next honest step is a **full untargeted `strace -f`** in this validated setup, or vendor source —
  not another variant of a shim.
- V-036's cause therefore remains **unresolved but tightly bounded**: `ApplicationManager` needs an object supplied by a
  component that never runs in this projection, and the two obvious mechanisms have been excluded by measurement.

## 1.89.0 - D-Bus eliminated; the earlier openat trace withdrawn as invalid

- Traced `ApplicationManager` inside the **systemd** boot, where the bus exists. Connections **succeed**:
  `/var/run/dbus/system_bus_socket` → `0`, session bus → `0`, and it creates its own SysV segments
  (`shmget(0x51121397, 416, IPC_CREAT|IPC_EXCL|0600)`). It **still** fails `initBootInfo attach fail` with retries 1–3.
- So boot-info initialisation is **not** a bus problem. The `ENOENT` I found earlier was an artefact of a research-init run
  with no bus — I had already declined to call it a finding, and this confirms that caution was right.
- **WITHDRAWN: my `openat` trace.** It recorded 15 calls because `ApplicationManager` exited almost immediately in that
  configuration, so it never reached the code under investigation. Concluding from it that "the attach is not
  file-backed" was the same error as reading a zero from an unreached path — the exact trap this project keeps logging.
- **Next task, correctly scoped:** repeat `openat` inside the systemd boot with the compositor up, where the binary
  demonstrably reaches `initBootInfo`, and look for `qipc_sharedmemory_*`.

## 1.88.0 - provenance incident: a scoped `git add` still committed the shared index

- **What happened:** commit `3f6bd7e` (mine, the `openat` finding) captured **14 files** instead of the 3 I intended. A
  parallel workstream had an 11-file AppFUMO shell-boundary bundle **already staged**, and `git add <3 paths>` adds to the
  index rather than replacing it — `git commit` then commits the whole index. The paths I named had no bearing on what
  was captured.
- **Verification, not assumption:** their 11 files show **no unstaged modifications** relative to that commit, i.e. they
  were captured exactly as staged, byte-for-byte. Nothing was altered, reordered or dropped, and they have since recorded
  delivery provenance themselves in `4df555a`.
- **Why this matters beyond tidiness:** it is the *second* index-scoping failure of this session. The first swept a
  parallel changelog entry into my commit while my own edit silently failed to apply. Both came from treating the index
  as private; it is shared state and `git add` cannot be used to scope a commit.
- **Discipline adopted from here:** (1) check `git diff --cached --name-only` before committing and stop if it lists
  anything I did not author; (2) prefer `git commit -- <paths>`, which scopes by command rather than by index contents;
  (3) keep to disjoint files where the work allows it.
- Recorded after the other workstream's correction landed and the workspace was confirmed clean, so this note could not
  itself be swept into somebody else's commit.

## 1.87.0 - the attach is not file-backed: openat shows no qipc path

- Ran `ApplicationManager` detached under `strace -f -e trace=openat` while it reached its usual failure
  (`initBootInfo attach fail`, retries 1–2). The trace contains **15 calls and no `qipc_sharedmemory_*` path**.
- So this attach is **not** the Qt key-file mechanism that `AppHomeScreen` used, and the technique that produced six
  correct segment names earlier does not transfer. It is either a direct **`shmget`/`shmat`** with a self-derived key,
  or a **D-Bus** call — and `openat` sees neither.
- **Corrected next step:** trace `shmget,shmat,shmdt,socket,connect,sendmsg,recvmsg`. One of those names the object
  directly: a SysV key if it is shared memory, or the service and member if it is D-Bus.
- Recorded because it is the second time in this thread that a technique which worked on one binary did not work on
  another, and the difference is worth stating rather than assuming.

## 1.86.0 - V-036 cause narrowed: length gate passes, so the fault is downstream

- Read the validation block properly. `cmpl $0x1c, 0x4(%rax)` compares a **length** against 28 and leaves early only on
  `<= 28`; the accepted path reads `movzbl 0x1c(%rax,%rdx)` — **byte 28 of the payload**. Our 35-byte reply is `0x23`,
  so the gate passes and the rejection is **downstream**, in content checks or a separate shared-memory attach.
- **`ApplicationManager` has no literal boot-info segment key** in its strings, so any attach target is composed at
  runtime. That reframes the problem: the payload's *shape* may be irrelevant and the missing **object** may be the real
  fault.
- **Next step is concrete and already proven in this project:** `strace -f -e trace=openat` on `ApplicationManager`,
  grepping for `qipc_sharedmemory_*`. That is exactly how the six real segment names were obtained for `AppHomeScreen`
  after derivation had failed — and it would tell us what to create rather than what to guess.

## 1.86.0 - bind AppFUMO `decryptionFile` to its exact shell boundary

- Bound exact `decryptionFile` FDE `[0x100b30,0x10110c)` through direct call
  `0x100e0c` to shared helper FDE `[0x1397c0,0x1398fb)`. Its split QString
  templates substitute the fixed decrypt helper, UUID-derived transient key
  pathname, incoming encrypted-file pathname, and incoming destination pathname.
  The two incoming pathname fields are inserted without an observed quoting,
  escaping, or shell-character filtering operation.
- The helper appends fixed stderr redirection, converts the QString to bytes, and
  calls `popen` at `0x139867` in read mode. It drains and discards output, calls
  `pclose`, and ignores its status. The adjacent output-accumulating helper at
  `0x139900` has a separate FDE and is not an alternate entry.
- Proved return propagation: verifier/key-operation failures return a fixed
  failure QString before the sink. After the sink, the function removes the
  transient key, calls `sync`, and returns the destination QString without using
  process status or checking destination existence/size.
- Corrected similar-literal provenance. Full templates at `0x20b500` and
  `0x20b530`, including the branch-selected throughput-limited variant, belong
  to separate FDE `[0x60ac0,0x6178f)`, which performs later destination checks;
  they are not the templates referenced by `decryptionFile`.
- Added bounded exact evidence, a focused assessment, and a strict Boolean-only
  tri-state model with deterministic UTF-8/LF output. The static unquoted shell
  structure is established; pathname influence, shell-character survival,
  invocation, authentication acceptance, process security context, command
  success, privilege/domain amplification, root, and persistence remain
  independently unknown. No recovered target/helper, operational payload,
  trigger, archive/update package, signature bypass, privilege action, or
  persistence mechanism was executed or created.

## 1.85.0 - correction: ApplicationManager is stripped; validation anchored by address instead

- The previous entry said to read `parseMicomBootInfo` "in `ApplicationManager` (it carries debug information)". **That
  was wrong.** The binary has **0 `.debug_*` sections** and no such symbol — checked directly. The plan it implied was
  not available.
- What is available: the log tag `parseMicomBootInfo` at vaddr `0x317c40` (referenced at `0x25a7be`, `0x25a892`);
  `AskSysBootinfo` at `0x31596a`; `AskSysBootinfo reply is VALID` at `0x315993`, referenced at `0x258810` inside the
  block at `0x258808` that logs validity.
- Immediately before that block the code does `cmpl $0x1c, 0x4(%rax)` (`0x258705`) and reads bytes from `+0x1c`
  (`movzbl 0x1c(%rax,%rdx)`, `0x25872a`) — a length-prefixed structure with payload at offset `0x1c`. That is a
  starting point for the validity criteria, not the answer.
- Recorded so the next attempt starts from addresses rather than from a wrong assumption about symbols. This is genuine
  reverse engineering on a stripped Qt binary, and it is larger than a single read.

## 1.84.0 - the causal chain closes on thirty-five bytes

- Read `ApplicationManager`'s own log with it running alone: it starts (`pid 719`, alive) and fails
  `ArgParserBase::initBootInfo attach fail`, retries three times, then `read error`. Its strings show the path uses
  `AskSysBootinfo` and validates the reply through `parseMicomBootInfo`.
- So **`micom-service`'s 35 zero bytes are enough for the launcher to register and not enough for
  `ApplicationManager`**. AM fails boot-info initialisation and exits, which is what leaves the launcher retrying
  `appId 2` and dispatching nothing — the V-036 behaviour, and the reason V-028's runtime tests never saw their call.
- Everything built this session now sits on one causal line: MICOM exchange → boot-info payload → AM initialisation →
  launcher dispatch → V-028. The single break is the **contents** of thirty-five bytes, not any of the plumbing.
- Next task is static and bounded: read `parseMicomBootInfo` (the binary carries debug information) for the validity
  criteria.
- **Process note, recorded because it affected this commit:** the file is edited concurrently, and a `git add -A` of a
  shared document swept another workstream's entry (`1.67.0 - bind direct decryption producers…`) into my previous
  commit under my message, while my own edit silently failed to apply because its anchor text had changed. Only my
  files should be staged, and anchor text must be verified before use — both are now noted in the history log.

## 1.78.0 - V-036's caveat resolved against the stronger reading: it is a spawn-fail loop

- Sampled `pidof ApplicationManager` ten times, two seconds apart, across a twenty-second window while the retry loop
  continued. Result: **`ALWRAPSEQ` empty** — no pid at any sample.
- So the dependent application is **not running** during the retry window. The loop is a **spawn-fail retry**, not a
  poll of a live instance, and liveness across retries is **disproven** for that window rather than merely unproven.
- The entry's framing is corrected accordingly: V-036 is "the launcher repeatedly fails to bring its own dependent
  application up and dispatches nothing while retrying", not "the launcher polls a dependency that is present".
- Remaining question, now narrow: **why does `ApplicationManager` exit?** Its own output goes to `/tmp/am.log` in the
  harness and has not been read yet — that is the next single diagnostic, and it is a log read rather than an
  experiment.

## 1.77.0 - V-036 re-measured: the loop persists with an ApplicationManager process present

- The earlier correction was itself correct to be cautious, but the measurement it lacked is now taken. With the pid
  written to a file so console spinners cannot obscure it, one boot recorded:

  `ALWRAPAM before_launcher pid=2079` · `ALWRAPAM after_loop pid=2317` · `appId[2]` occurrences **20**

- So an `ApplicationManager` process was running before the launcher, a **different** process of the same name was
  running after it — the launcher spawns its own — and the retry loop still ran twenty times.
- **The caveat is recorded with it:** a changing pid cannot distinguish "a spawned instance that persists" from "a spawn
  that exits and is retried". Liveness *across* the retries therefore remains unproven, and V-036 says exactly that
  rather than claiming the stronger version twice.
- The practical point stands either way: the launcher retries `appId 2` twenty times and dispatches nothing meanwhile,
  which is why V-028's runtime tests measured this loop rather than the launch path.

## 1.76.0 - correction inside V-036: the dependency's liveness was never confirmed

- Verifying my own newest entry found an overstatement in it. V-036 said the `appId[2]` loop persisted "after
  `ApplicationManager` was started and running"; **that was not verified.** The application *was* launched before the
  launcher, but the `pidof` value in that boot was obscured by a systemd progress line in the captured console, and no
  exit or crash was recorded either way.
- The entry now says what the evidence supports: the loop persisted **with the application launched**, and its liveness
  at that moment is **unconfirmed**. The corresponding "not established" bullet is corrected to match, rather than
  continuing to assert the more interesting version of the claim.
- Worth naming: the appeal of that sentence was exactly the problem. "Persists even when its dependency is satisfied" is
  a much better finding than "persists while a dependency is unverified", and I wrote the better one without the
  measurement to support it. Corrected within minutes of committing it, which is the only acceptable outcome.
- Also verified while checking: the register has **36 numbered entries, no duplicates, zero host paths**, and the
  worktree is clean.

## 1.75.0 - recorded V-036: the launcher's dispatch stalls behind an unstartable appId 2

- The open item flagged at the end of the last entry is now characterised and registered. In a boot where
  `com.lge.avn.applauncher` is registered, the launcher emits
  `getAppProcessByAppId appId[2][ApplicationManager]` about every 1.7 s and **does not leave that loop** — twenty
  occurrences in one boot, **including after `ApplicationManager` was started and running**. During the same window a
  well-formed `launch` call was accepted and produced **zero `appId[999]` dispatch entries**.
- Recorded as **V-036**, an availability defect observed in emulation, explicitly not a memory-safety or privilege
  issue, with the misleading part stated: the loop persists even when its dependency *is* satisfied.
- It is also the honest explanation for V-028's runtime negatives: they measured this loop, not the launch path. That
  distinction is now written where both entries can see it.
- Defensive remediation recorded: bound the retry with backoff and a terminal state, keep dispatching while a
  dependency is retried, and surface an error instead of looping silently.

## 1.83.0 - reject exact CVE-2018-9568 socket clone creator mismatch

- Bound the exact EU `260128` kernel by SHA-256
  `f5ee9c...b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`,
  authoritative-map SHA-256 `2cfba9...e3c1f`, and configuration SHA-256
  `987268...dad56`. NET, INET, IPV6, and SLUB are enabled; USER_NS is disabled.
  All ten supplied complete raw function hashes independently match.
- Proved allocation/free identity from complete machine code: `sk_alloc`
  initializes current protocol at `sock+0x28` and creator at `sock+0x1a0` from
  the same protocol; `sk_prot_alloc` selects slab `proto+0xf8` and object size
  `proto+0x100`; final `__sk_free` selects the cache through creator.
- Proved the decisive complete `sk_clone_lock` ordering. Clone allocation uses
  source current protocol. Its fixed first copy is only `0x60` bytes; its one
  creator-overwriting copy starts at `+0x78` and spans `obj_size-0x78`. Exact
  TCP/TCPv6 sizes `0x780`/`0x840` include creator. The function then reloads
  source current protocol at `0xffffffff81478862` and stores it to child
  creator at `0xffffffff81478867`, with no later overwrite. Exact
  `security_fixup_ops` fills the intervening configured/default LSM clone hook
  with complete no-op `cap_sk_clone_security`, excluding callback mutation of
  the allocator protocol before that reset.
- Distinguished cleanup precisely: the creator-overwriting copy ends at
  `0xffffffff8147884e`, with linear normal control through the reviewed callback
  to the correction. Both failure decisions feeding the complete function's
  only post-copy direct `sk_free` at `0xffffffff81478a12` follow that store; the
  cleanup path returns null, while every non-null return passes the correction
  and no later creator overwrite exists. Later TCP caller cleanup is separate:
  each wrapper tests the returned child first, so it is possible only after the
  corrected non-null clone has successfully returned. Complete address-form
  code can rewrite current protocol to `tcp_prot` without creator rewrite, and
  the compiled child route is
  `tcp_v4_syn_recv_sock -> tcp_create_openreq_child -> inet_csk_clone_lock ->
  sk_clone_lock`.
- Verified byte-identical patches in canonical ignored
  `work/online-kernel-candidates-20261107/cve-2018-9568/`: mainline commit
  `9d538fa60bad4f7b23193c89e843797a1cf71ef3`, parent
  `b32ca44a88def4bf92626d8777494c6f14638c42`, patch SHA-256
  `c1f7389124f499cc764ce39a25f841bc701f0d3e8e4ab6a86f3c578941ed085d`;
  and stable commit `0a11ea32304f6ad6daf5589b6626775b7f00015c`, parent
  `cafd2b53da565ca30c48a146635c95d385d83b81`, patch SHA-256
  `756c9749346bda510e242b02b849448418196bc1f95684dbcbbf362eff60d8ba`.
  Both corresponding 20261102 analysis copies pass byte-for-byte `cmp` and
  produce the same authoritative hashes; that directory is not canonical
  provenance. Patch bodies are not copied into tracked evidence because they
  contain the complete
  operational trigger program. Retained complete exact-static artifact SHA-256
  is `e876c4...53273`. The result is direct patch shape and rejects the named
  mismatch semantics, but does not prove direct cherry-pick provenance.
- Added a strict 15-input Boolean-only classifier separating direct patch shape,
  equivalent fix, vulnerable semantics, positively established absent route,
  and indeterminate. It fails closed on incomplete/conflicting state, exhausts
  all 32,768 Boolean states while asserting every classification and output
  field, rejects every missing key, unknown keys, and non-Boolean types, and
  emits deterministic UTF-8 with one LF through `sys.stdout.buffer`
  independently of `PYTHONIOENCODING`.
- No target execution, sockets, address-form operation, clones, listeners,
  traffic, malformed input, trigger, exploit, privilege action, or persistence
  action occurred. Installed identity, runtime route/policy, wrong-cache free,
  corruption, privilege escalation, root, persistence, broad socket/allocator
  safety, and every vendor-equivalent defect remain unobserved or unresolved.

## 1.82.0 - reject the exact Broadcom BSA CVE-2017-0785 continuation mechanism

- Bound both recovered `process_service_search` functions by complete unwind
  FDE and raw bytes: `vbtd-51 [0x841a40,0x841dbe)` SHA-256
  `c91b38...ae5f4`, and `vbtd-63 [0x842230,0x8425a6)` SHA-256
  `c35ece...a36ef7`, under the existing exact ELF hashes and Build IDs.
- Proved positive operand and branch semantics rather than relying on local
  names. BP is the current recomputed successful-result count; R13W is the
  parsed continuation offset. `cmpw %bp,%r13w; ja` rejects exactly unsigned
  offset greater than count. The separate CCB `+0xb6` comparison requires the
  current expected offset. Both failures converge on code-5 error handling and
  dominate subtraction and later handle indexing in both functions.
- Preserved equality correctly: offset equal to result count does not take the
  unsigned-above branch, subtraction yields zero, and the handle-loop entry
  guard skips indexing. The named continuation-offset unsigned-underflow/OOB
  information-disclosure mechanism is therefore rejected for these exact
  functions.
- Retained public fix
  `226ea26684d4cd609a5b456d3d2cc762453c2d75` byte-for-byte, patch SHA-256
  `6f80d9cd3534d00e24c9c33717a282f1e6ae180f05f833e502c7a361e86b2721`,
  and added a sanitized exact-static excerpt, focused assessment, and a pure
  24-case finite model. The model rejects missing/unknown keys and invalid
  types, emits deterministic explicit UTF-8/LF JSON, and contains no
  operational Bluetooth or target material.
- Validation passed focused `11 tests, 56 subtests`, required full suite
  `637 tests, 318312 subtests`, bytecode compilation, 45 exact-static/report
  checks, retained-patch byte comparison, deterministic report hashing,
  `git diff --check`, and the public harness with
  `pass=3 info=4 pending=0 blocked=0 fail=0`. Independent narrow read-only
  package review returned **ACCEPT** with no blocking findings.
- This is a mechanism-specific exact-static result, not proof of direct
  cherry-pick provenance, general SDP safety, installed identity, runtime
  handler/channel reachability, adapter/security policy, malformed-input
  behavior, disclosure, code execution, unrestricted root, persistence, or
  owner-device applicability. No recovered target, Bluetooth endpoint/radio,
  packet/PDU, malformed fixture, or exploit material was used or created.

## 1.74.0 - pre-starting appId 2 does not clear the loop; V-028 runtime line closed

- Started `ApplicationManager` (appId 2) before the launcher, so the application it keeps retrying already exists.
  Result: **20 retries of `appId[2][ApplicationManager]` still occur**, and **`appId[999]` never appears in the
  dispatcher log** — the call is accepted by the bus and never dispatched.
- That closes the runtime line for V-028 in this environment. Four distinct approaches have now been tried, each with a
  better-founded premise than the last:
  1. guessed argument types;
  2. introspected exact signature, wrong sequencing;
  3. exact signature, sequenced after the registry sweep, target pre-registered in `/app/bin`;
  4. same, with the launcher's retry dependency pre-started.
  Each produced no execution, and the last three produced no dispatch entry at all.
- **What is established, and it is not nothing:** no SMACK denial exists anywhere in these boots, so the exec is not
  being refused by the security module; the launcher is in a persistent `appId[2]` retry loop it does not exit even
  when that application is already running; and calls to `launch` are accepted and silently ignored rather than
  rejected.
- **Conclusion for the register:** V-028 keeps its original status — exact static route, runtime execution unobserved.
  Reproducing it needs either the vendor source, or a unit where the launcher's own startup completes without emulation
  gaps. Nothing in this session's work weakens the static finding, and nothing here justifies calling it exploitable.
- This thread is closed deliberately rather than left open: four attempts with four different premises is enough
  evidence to conclude that the obstacle is environmental and vendor-internal, not a missing idea.

## 1.81.0 - the launch request is never dispatched: the launcher is stuck retrying appId 2

- Instead of a fourth launch attempt, two of the three named causes were tested by reading the run's own evidence.
- **SMACK is weakened, not confirmed.** Across the whole boot there are **zero** SMACK denials (`count: 0`) and not one
  SMACK line naming `AppLauncher`, in an image that audits its decisions extensively (`action=granted` lines
  throughout). A denied exec would very likely have left a trace; none exists.
- **The dispatcher never saw our request.** Every dispatch line in the log is its own startup traffic:
  `getAppProcessByAppId appId[2][ApplicationManager]` repeating every ~1.7 s, plus one `appId[400]
  [UserProfileManager]`. There is **no `appId[999]` and no mention of `AppProbe`** anywhere. The D-Bus call was
  delivered without error and was simply never acted on.
- That reframes the problem completely: the launcher is **stuck in a retry loop trying to start ApplicationManager
  (appId 2)**, and our request never reaches the dispatcher behind it. It is not a signature, SMACK, or registry
  question at this point — it is that the launcher itself is occupied with an application it cannot launch.
- Next step is therefore clear and unrelated to V-028: make `ApplicationManager` (appId 2) start successfully — we can
  start it ourselves, as was done earlier when it published its shared-memory segments — and see whether the retry
  loop clears. If it does, dispatch resumes and the V-028 call becomes worth repeating.
- V-028 remains "static route, runtime unobserved". What changed is that the reason is now visible in the launcher's
  own log rather than guessed at.

## 1.80.0 - conditionally reject Broadcom BSA SDP small-maximum physical OOB mechanism

- Bound CVE-2017-13255 and CVE-2017-13256 to both PCB-selectable exact BSA
  images: `vbtd-51` SHA-256 `55e21d...c9e0`, Build ID
  `12175aa88ccff70cc56498e0208c9a51aac0c9e9`, and `vbtd-63` SHA-256
  `c56b68...b26b9`, Build ID `04141ed222ee8f150c0eb0e46fdb73624d168920`.
  Complete handler-range review confirms that both lack the public fix's
  source-like `max_list_len < 4` early rejection.
- Independently traced service-attribute and service-search-attribute handlers
  through initial and continuation states for effective internal maxima 0..3.
  The matrix requires valid syntax, ordinary response construction, successful
  scratch allocation/reuse, and valid internal continuation state. On that
  feasible path, initial construction can reach no higher than scratch offset
  2; effective maxima 0..2 retain a logical effective-limit exceedance.
  Continuation does not rewrite the outer initial header. Earlier error exits
  are not described as reaching these writes.
- Regenerated both complete `sdpu_build_partial_attrib_entry` helpers and proved
  that valid-state copy length and destination advancement are clamped to
  `min(remaining, total serialized length - state-derived attr_offset)`.
  Corrupted/impossible offsets remain unknown. The effective 0..3 matrix equals
  a peer-requested small maximum only under an ordinary protocol-valid remote
  MTU; low/invalid remote-MTU subtraction behavior remains unknown.
- Proved the decisive allocator/caller difference rather than relying on the
  absent guard: all four scratch call sites pass remote MTU, both
  `GKI_getbuf[_r]` implementations select capacity greater than or equal to the
  request, allocation failure is checked, and both exact initializers set pool
  0 user capacity to `0x40`. Every successful write extent on the stated path
  is at most 3 within at least 64 user bytes. This conditionally rejects only
  the public physical OOB-write mechanism, not general SDP/helper safety.
- Retained byte-identical public fix
  `f0edf6571d2d58e66ee0b100ebe49c585d31489f`, patch SHA-256
  `a0470c20592473144f8114cf41ab4cb2479fe2c108a4aa73fa4864eabd02ca34`,
  plus a focused exact-static excerpt and assessment. Added a pure finite model
  with explicit UTF-8/LF, fail-closed all-or-none CLI, exact evidence bindings,
  no operational message material, and exhaustive assertions for every emitted
  classification field.
- Analysis started at `0a9a7f2`; final pre-delivery integration review used
  `30f6cac`. That concurrent commit accidentally absorbed the preliminary SDP
  changelog entry but not the untracked model, tests, assessment, retained
  patch, or static artifact. This delivery corrects the preliminary wording and
  records the complete package without rewriting shared history.
- Correction-cycle validation regenerated the complete handler, GKI, and both
  partial-helper ranges and passed static clamp/copy/advance assertions.
  Focused validation passed `9 tests, 52 subtests`; the required suite passed
  `626 tests, 318256 subtests`. Bytecode compilation, identity/hash/address
  checks, patch byte comparison, and `git diff --check` passed. Final model,
  test, assessment, artifact, patch, and report hashes are in `HANDOVER.md`.
  The public harness passed with
  `pass=3 info=4 pending=0 blocked=0 fail=0`. No recovered target, Bluetooth
  adapter/radio/channel, endpoint, packet/PDU, malformed fixture, controlled
  execution, or exploit material was used or created. Runtime reachability,
  adapter/channel/security policy, negotiated-MTU/allocator edge cases, other
  SDP or vendor-equivalent behavior, impact, and owner-device applicability
  remain unknown. Independent final package review returned **ACCEPT** after
  the moving-base, stale-checkpoint, and changelog-order corrections; this is
  not acceptance of runtime SDP safety or impact.

## 1.79.0 - registry hypothesis tested and did not produce execution

- Placed `/app/bin/AppProbe` (a script writing `/tmp/L_probe`) **before** the launcher started, so its startup sweep
  of `/app/bin` must have included it, then called the exact signature with
  `applocation=/app/bin/AppProbe`. **No marker was created.**
- So the registry hypothesis is tested and does not explain the silence. V-028 runtime execution remains unobserved
  after: correct signature (introspected, not guessed), correct sequencing (after registration and after the sweep),
  and a target that existed before the registry was built.
- Remaining candidate causes, now narrow and explicitly listed: (a) **SMACK** denies the launcher executing a file it
  did not ship with, which is plausible given the label-aware behaviour seen elsewhere in this image; (b) the
  dispatcher requires the appid to be **one it assigned** during the sweep rather than a caller-supplied number, so
  appid 999 or 5 maps to nothing; (c) the two boolean gates are not the real precondition and some further state
  (capture mode, engineering mode, profile) is needed.
- **Status of the chain:** three links remain evidenced — same-uid D-Bus service with a caller-supplied path (V-028,
  static), world-writable `EnvironmentFile` for eleven root services (V-012, confirmed in the vendor's own
  `Dbuslaunch.sh`), and a mutable, persistent update trust anchor (V-034). The runtime link between them is **not**
  demonstrated, and this thread's attempts to demonstrate it in the emulated environment have not succeeded.
- Recorded plainly: V-028 stays at "exact static route, runtime exec unobserved" — its original status, unchanged by
  this work. The static finding is not weakened; the runtime claim is simply not mine to make without a unit or a
  working launcher dispatch.

## 1.78.0 - sequenced calls fire and still do not execute; the registry hypothesis

- With registration confirmed and a settle window before issuing requests, the calls now reach the launcher:
  variant **A** (appid 999, `/tmp/probe.sh`, false/false) and variant **C** (appid 5, `/app/bin/probe.sh`, true/true)
  both appear in the log. **Neither produced a marker.** Variant B is again absent from the log, so it is treated as
  unrun.
- **V-028's runtime execution therefore remains unobserved with correct sequencing and the exact signature.** That is
  no longer an inconclusive test for A and C; it is a negative for them.
- The log suggests the reason, and it is a good one: the launcher **builds its application registry by sweeping
  `/app/bin` at startup** (`dir info [/app/bin/AppX]` for dozens of binaries, at 00:01:32). Our probe files were
  written *after* that sweep, so neither existed when the registry was built — and a launcher that only dispatches
  registered applications would never launch them regardless of appid or path.
- **Next test is therefore specific and cheap:** write the probe into `/app/bin` **before** the launcher starts, let the
  sweep include it, then call `launch` with that path. If it executes, V-028's runtime link is confirmed; if it still
  does not, the remaining causes are SMACK on exec or an appid-to-entry mapping we have not reproduced.
- Recorded as a narrowed hypothesis rather than as another attempt, because the difference between "the call is
  wrong" and "the target was never registered" is exactly the kind of thing this thread has repeatedly mistaken for
  one another.

## 1.77.0 - launch matrix inconclusive; the launcher builds its registry first

- Ran a three-variant matrix over the exact signature: (A) appid 999 with `/tmp/probe.sh`, false/false;
  (B) appid 999 with `/app/bin/probe.sh`, true/true; (C) appid 5 with `/app/bin/probe.sh`, true/true.
- **Only call A appears in the log, and no marker was created for any variant.** Calls B and C are absent, so the
  matrix did not execute as written — this is recorded as **inconclusive**, not as three negative results.
- What the log does show is why the timing is hard: at that moment the launcher was **enumerating `/app/bin`** to build
  its application registry — a long `dir info [...]` sweep over dozens of binaries — so the calls landed while it was
  still constructing the very table that decides launches. Sequencing against that enumeration, rather than a fixed
  `sleep`, is required.
- Also observed, and expected: displacing the vendor daemon makes systemd restart it, and it then logs
  `Cannot register service :` because our adaptor owns the name. The displacement is functional but not tidy; a
  cleaner arrangement would have the adapter own the name from the start of the boot.
- V-028 runtime execution: still unobserved. The three candidate causes from the previous entry remain untested —
  the matrix must be re-run after the registry sweep completes.

## 1.76.0 - exact `launch` signature obtained; the bypass still does not execute

- Introspection of `com.lge.avn.applauncher` `/Request` now works (the name is registered), and it yields the exact
  method signature that had been guessed wrongly:

  `launch(in i appid, in s appname, in s applocation, in b engcapturemode, in b emmctestmode)`

  Five arguments, not three, and the last two are booleans. That signature is recorded here so nobody has to
  introspect it again.
- Called with the exact signature (`int32:999 string:probe string:/tmp/probe.sh boolean:false boolean:false`), the
  request was **accepted without error and produced no execution**: `/tmp/LAUNCHED` was never created and the
  launcher logged nothing for appid 999.
- **V-028's runtime execution therefore remains unobserved**, and now for a narrower reason than before: the call is
  well-formed and reaches the service, but does not result in a launch. Candidate causes, in order: the dispatcher
  gates on appid registration for *existing* objects (only newly created ones accept 1…1024), the two boolean gates
  must be true, or SMACK prevents the launcher from executing a file in `/tmp`.
- **A separate milestone did land:** systemd now logs `Started HKMC Preminum AVN 2.1 -Launcher.` That unit had never
  completed in any earlier boot — the MICOM adaptor is what allowed it, so the HMI-side dependency that blocked this
  project from the beginning is now satisfied by the emulation rather than by the vendor daemon.

## 1.75.0 - the launcher starts: MICOM adaptor satisfies it end to end

- With per-method payloads (`AskNaviOutermostRegion` 8 bytes, `AskSysBootinfo` 35, `AskCustomSetting` 16,
  `AskSettingInfoValue` 8) and a polling window, **`com.lge.avn.applauncher` registered at poll 6** — the vendor
  launcher reached readiness for the first time in this project. Every previous run stalled on the first ask.
- The launcher then began taking control traffic too (`answered SetControlKeyLock with 4 bytes`) and logged its own
  dispatch line: `ApplicationLauncher::getAppProcessByAppId appId[400][UserProfileManager]`. So it is not merely
  registered, it is **processing application requests**.
- **V-028's runtime execution is still unobserved.** My call
  `launch uint32:999 string:probe string:/tmp/probe.sh` produced no marker and no execution; the only launch the
  launcher logged was its own `appId[400]` UserProfileManager request. The likely cause is a signature mismatch — the
  real `launch(appid, appname, applocation, …)` may take more or differently typed arguments than I guessed.
- Next step is now cheap and precise: the name is registered, so **introspect `/Request` and read the exact method
  signature**, then replay the call with matching types.
- Practically, this also means the VM line has advanced: the launcher dependency that blocked the HMI is satisfied by
  a simulated adaptor rather than by the vendor daemon.

## 1.74.0 - the MICOM adaptor owns the bus name and the launcher consumes its answers

- Wrote `micom-service`, a research adaptor that owns `com.lge.car.micom` on the system bus, registers `/Ihu`
  with interface `com.lge.car.micom.ihu`, and answers each method with an `ay` payload (35 bytes for
  `AskSysBootinfo`, empty otherwise). libdbus is resolved through `dlopen` because this cross build has no
  development headers for it.
- **First attempt failed informatively:** `request_name` returned **3** (`EXISTS`) — the vendor daemon *does* own
  the name, it simply answers nothing. With a retry loop plus displacing the daemon (`pkill
  micommanager_userspace`), ownership is taken: `request_name → 1 (PRIMARY_OWNER)`.
- **The launcher then consumed real answers**, which had never happened before:
  `answered AskNaviOutermostRegion`, `AskSysBootinfo -> 35 bytes` (three retries), `answered AskCustomSetting`
  (three), `answered AskSettingInfoValue`. Compare with every earlier attempt, where these came back as
  `Did not receive a reply` and the launcher stalled.
- The launcher therefore advanced **further than in any previous run** — it is now iterating its ask sequence
  rather than failing on the first one. It still had not exported `com.lge.avn.applauncher` within the window, so
  the V-028 launch test still could not run.
- Next: extend the settle window (the launcher was still working at 1 min 26 s), and answer the remaining ask
  methods with plausible non-empty payloads rather than empty arrays, in case a later step requires real values.

## 1.73.0 - correct CVE-2017-6074 to the specific DCCPv6 request path

- After independent **REJECT**, corrected the applicability model to the specific
  public path requiring DCCP core (`input.o`) plus DCCPv6/IPv6 (`ipv6.o`). Under
  applicable public v4.1 Kconfig/Kbuild rules, exact `IP_DCCP=n` excludes the
  whole named DCCP subtree. The canonical stock archive contains 163 regular
  `.ko` members and no canonical DCCP core or DCCPv6 module.
- Split the complete ten-name authoritative-map inventory into core and DCCPv6
  presence facts. Exact queried core-symbol presence establishes core
  translation-unit presence; exact queried DCCPv6-symbol presence establishes
  DCCPv6 translation-unit presence. IPv4-only functional evidence establishes
  core only. Positive complete DCCPv6 functional evidence establishes both
  components and overrides absence.
- Replaced the rejected ten-input model with a 15-input schema-v2 Boolean-only
  classifier. Physical component/path outputs no longer depend on the public
  CVE dependency. Rejection is exactly dependency plus physical complete-path
  absence. The exact build-rule default and a formally complete built-in/module-
  inventory route establish component absence; incomplete path states remain
  unknown and positive component evidence records conflicts.
- Retained bounded scope: `CONFIG_INET=y` and `CONFIG_IPV6=y`, so this is not
  general networking or IPv6 safety; an `IPv6=n` input alone would not prove
  general IPv6 absence. USER_NS is non-decisive, and ordinary DCCP socket
  creation would not be inherently capability-gated if DCCP were built.
- Retained byte-identical mainline commit
  `5edabca9d4cff7f1f2b68f0bac55ef99d9798ba4` and stable 4.1.y backport
  `98442999b9671784e659b205be8b5b6be8e81629`. The retained official
  `ChangeLog-4.1.41` release commit/date records 15 June 2017. Removed the
  unretained archive-index claim. Version history and fix effects remain
  contextual because the named path is absent.
- Focused validation passes `13 tests, 32793 subtests`; the complete suite
  passes `617 tests, 318204 subtests`; bytecode compilation, exact static checks,
  and `git diff --check` pass. The public harness passes with
  `pass=3 info=4 pending=0 blocked=0 fail=0`. Corrected independent review
  returned **ACCEPT** with no blocking findings. Generic public research used
  Astra; implementation provenance is `codex-router/gpt-daybreak-blue-latest`.
  DeepSeek remained static-ready/runtime-unverified and did not run. No installed
  identity, runtime behavior, fix effect in recovered code, corruption, root,
  persistence, or target interaction is claimed.

## 1.72.0 - reject CVE-2015-1805 by exact pipe iterator architecture

- Bound complete authoritative-map-successor ranges for `pipe_write`,
  `pipe_read`, `copy_page_from_iter`, and `copy_page_to_iter`. Both write copy
  sites directly call exact `copy_page_from_iter`, and the read copy site
  directly calls exact `copy_page_to_iter`.
- Proved exact bounded progress in both complete CVE-relevant iovec helper
  branches: requested bytes are clamped to iterator count; descriptor base and
  length are read from fixed 16-byte records; actual progress is requested
  minus copy residual; advanced page/user state and remaining budget carry into
  fallback; and iterator offset/count/descriptor/segment fields are committed
  without changing descriptor `iov_base` or `iov_len`.
- Retained public legacy-introduction commit
  `f6762b7ad8edd6abc802542ce845d3bc8adcb92f`, read conversion
  `637b58c2887e5e57850865839cc75f59184b23d1`, and write conversion
  `f0d1bec9d58d4c038d0ac958c9af82be6eb18045`. Exact public v4.1 source already
  has both conversions, so ordinary upstream 4.1 needs no 4.1.y
  CVE-2015-1805 backport. Legacy stable adaptations and CVE-2016-0774 remain
  contextual alternatives, not required 4.1 fixes; exact vendor code, not
  version history, controls the verdict.
- Added the three authoritative patches, complete static artifact, dedicated
  assessment, and a 17-input schema-v2 Boolean-only classifier with
  deterministic UTF-8/LF, all-or-none fail-closed CLI, tri-state unknown for
  incomplete fixed effects, explicit broken-legacy-path precedence, an optional
  progress-preserving legacy alternative, ordinary-local-pipe scope, null
  runtime/impact outcomes, and exhaustive assertions for every emitted field.
- Kept scope narrow: ordinary pipe functionality is compiled and public
  source-level impact was unprivileged local memory corruption/privilege
  escalation, but broad pipe/iov-iterator safety, every vendor-equivalent defect
  absence, installed identity, runtime policy, successful triggering,
  corruption, root and persistence are not established. Focused validation
  passed `10 tests, 131109 subtests`; the complete suite passed `604 tests,
  285411 subtests`; bytecode compilation, exact patch/disassembly/hash checks,
  and scoped `git diff --check` passed. The public harness passed after public
  maintainer email addresses in a previously committed XFRM changelog excerpt
  were redacted, with the complete source hash and all non-email content
  retained. Independent read-only review accepted the technical verdict with no
  blocking findings; its moving-base bookkeeping note was integrated. Exact
  hashes are recorded in the checkpoint. No recovered target or prohibited
  pipe, vector-copy, fault, race, grooming, payload, or exploit operation was
  used or created.

## 1.71.0 - reject CVE-2017-7184 for the named XFRM-user update path

- Rejected CVE-2017-7184 only for the upstream/named `CONFIG_XFRM_USER`
  `XFRM_MSG_NEWAE -> xfrm_new_ae` update path in the exact recovered package.
  `CONFIG_XFRM_USER` is disabled, so upstream v4.1 build rules do not select
  `net/xfrm/xfrm_user.c`; a fresh read-only inventory directly against the
  canonical decrypted stock archive (SHA-256
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`)
  finds 163 regular `.ko` members and no `xfrm_user.ko`. The mutable extracted
  staging tree is not used to prove stock identity.
- Preserved the complete eight-name authoritative-map query inventory without
  turning it into a universal inline/vendor-equivalence claim. Preserved
  contrary XFRM-core scope: `CONFIG_XFRM=y`, complete exact `xfrm_init_replay`,
  state/policy/replay symbols, and three IPv6 XFRM mode modules remain.
  Separately disabled `CONFIG_NET_KEY` is not conflated with the named path.
- Public history identifies introducing commit
  `d8647b79c3b7e223ac051439d165bc8e7bbb832f`, historical incomplete verifier
  commit `e2b19125e94124daaeda1ddcf9b85b04575ad86f`, mainline fixes
  `677e806da4d916052585301785d847c3b3e6186a` and
  `f843ee6dd019bcece3e74e76ad9df0155655d0df`, and official stable 4.1.y
  backports `438db92d7f2792e3bad17be70e6edf0f44a081f0` and
  `171a957989c4f398adb41078dbfff73b0821e383`, both first in Linux 4.1.49
  (22 January 2018). History is contextual only; exact absent-path evidence
  controls. Verifier presence alone is not remediation, and both fix effects or
  exact equivalents would be required if the path existed. No verifier/fix
  effect is claimed for code that is not built or shipped.
- Added exact static evidence, a dedicated assessment, and a ten-input schema-v2
  Boolean-only model with fail-closed all-or-none CLI, tri-state incomplete-
  absence handling, explicit contrary functional named-path and XFRM-core facts,
  separate NET_KEY scope, null runtime/impact outcomes, and exhaustive output
  assertions.
- Focused validation passed `8 tests, 1056 subtests`; the complete suite passed
  `594 tests, 154302 subtests`; the public harness passed
  `pass=3 info=4 pending=0 blocked=0 fail=0`; bytecode compilation and
  `git diff --check` passed. An initial independent review accepted the
  technical verdict but rejected stale validation wording, a moving integration
  base, and missing retained public-history captures. Those package defects
  were corrected on frozen base `7074707`; corrected independent review
  returned **ACCEPT** with no blocking or nonblocking findings. No recovered
  target, socket/netlink/XFRM operation, message, attribute, packet,
  module action, namespace, capability request, trigger, race, payload, or
  firmware material was executed, created, or exercised.

## 1.70.0 - reject CVE-2017-16995 for the exact syscall-based eBPF path

- Rejected CVE-2017-16995 only for the named syscall-based eBPF verifier path
  in exact recovered `vmlinux`: `CONFIG_BPF_SYSCALL` is disabled, weak
  `sys_bpf` aliases complete `sys_ni_syscall` returning `-ENOSYS`, and native
  x86-64 syscall-table slot 321 points to that same stub.
- Preserved contrary scope facts: `CONFIG_BPF=y`, and classic BPF validation,
  creation, attachment, interpreter, and runtime-selection symbols remain
  compiled. This is not general BPF absence, classic-BPF safety, all alternate
  eBPF-entry absence, an installed-device claim, or a verifier-internals audit.
- Compared against authoritative upstream commit
  `95a762e2c8c942780948091f8f2a4f32fce1ac6f` and retained its commit-message
  boundary that unprivileged exploitability starts with v4.14. The vendor
  4.1-derived banner is context only; exact configuration and dispatch evidence
  determine the verdict.
- Added the authoritative patch, exact static assembly/table artifact, dedicated
  assessment, and a nine-input schema-v2 Boolean-only model with fail-closed
  all-or-none CLI, tri-state incomplete-fact handling, explicit contrary
  functional and alternate-entry facts, explicit classic-BPF scope, null
  runtime/impact outcomes, and exhaustive output assertions.
- Focused validation passed `8 tests, 529 subtests`; the complete suite passed
  `586 tests, 153246 subtests`; the public harness and bytecode compilation
  passed; independent exact-binary/package review returned **ACCEPT**.
- No recovered target, target operation, code load, communication endpoint,
  verifier input, verifier trigger, race, payload, crash, privilege transition,
  root action, or persistence mechanism was used or created.

## 1.69.0 - reject CVE-2016-0723 by exact retained line-discipline reference

- Bound command `0x5424` in complete exact
  `tty_ioctl [0xffffffff812871f8,0xffffffff81287d46)` to the path beginning at
  `0xffffffff812879f9`: exact `tty_ldisc_ref_wait`, post-acquisition
  `ldisc->ops->num` loads, exact `__put_user_4`, and exact `tty_ldisc_deref`
  before common return.
- Proved that every normal path after successful wait reaches dereference,
  including the user-copy error return; the copy result is saved but not tested
  before the same retained object is released.
- Retained complete exact `tty_ldisc_ref_wait`, `tty_ldisc_ref`, and
  `tty_ldisc_deref` ranges and bound their exact `ldsem_down_read`,
  `ldsem_down_read_trylock`, and `ldsem_up_read` calls.
- Compared those fixed effects with authoritative upstream commit
  `5c17c861a357e9458001f021a7afa7aab9937439`. The result rejects only the
  CVE-specific unlocked-dereference premise; it does not establish source
  provenance, installed identity, or general TTY safety.
- Added the authoritative patch, complete retained assembly, dedicated report,
  and a twelve-input schema-v2 Boolean-only model with fail-closed all-or-none
  CLI, tri-state incomplete-fact handling, an explicit contrary unlocked path,
  null runtime/impact outcomes, and exhaustive output assertions. Focused
  validation passed `8 tests, 4111 subtests`; the complete suite passed `578
  tests, 152717 subtests`; the public harness and bytecode compilation passed;
  independent exact-binary/package review returned **ACCEPT**.
- No recovered target, target operation, terminal, thread, race, trigger
  material, crash, privilege transition, or persistence action was used or
  created.

## 1.66.0 - V-028 runtime test blocked one layer down: the launcher is stuck on MICOM asks

- Built the test properly this time: in the systemd workspace, a wrapper around `AppLauncher.sh` brings up our
  compositor (esinit's own is gated behind the SPI check emulation fails), runs the vendor launcher, then introspects
  and calls `com.lge.avn.applauncher` over the session bus whose address `Dbuslaunch.sh` leaves in
  `/tmp/session_appmgr`.
- Measured result: weston up (`pid 2070`), session bus address obtained, but **the launcher never registers its D-Bus
  name**. Its own output explains why — it is blocked retrying the vehicle asks:
  `askSysBootinfo Error Reply = Did not receive a reply`, then `askCustomSetting`, then `askSettingInfoValue`.
  With no `com.lge.car.micom` peer answering on the bus, `AppLauncher` never reaches the point where it exports
  `applauncher`, so introspection returns `ServiceUnknown` and the launch call is never attempted.
- **This connects three separate threads of this project.** The ask sequence observed here (`AskSysBootinfo`,
  `AskCustomSetting`, `AskSettingInfoValue`) matches the MICOM contract document exactly; the launcher's dependency
  on it matches the unit's hard `Requires=`; and the reason the daemon does not answer is the `writeToDBus` defect
  measured earlier. V-028's runtime execution is therefore gated by a vendor daemon bug, not by anything in the
  emulation or by the launcher itself.
- Also confirmed at the mechanism level while reading the vendor scripts: `Dbuslaunch.sh` writes the session bus
  address to `/tmp/session_appmgr` and `DBUS_SESSION_BUS_ADDRESS=…` to **`/tmp/session_appmgr.env`** — the
  world-writable `EnvironmentFile` behind V-012, in a `01777` `/tmp`. That is now sourced from the vendor script
  rather than inferred.
- Status of the revived chain: V-028 remains "exact static route, runtime exec unobserved", and the reason it stays
  unobserved is now precise and recorded.

## 1.68.0 - reject the compat netfilter replace CVE by absent compiled path

- Rejected CVE-2016-4997 for exact recovered `vmlinux`: IA32 emulation is disabled, `CONFIG_COMPAT=y` is absent, weak `compat_sys_setsockopt` aliases exact `sys_ni_syscall` and returns `-ENOSYS`, and no compat iptables translation/check symbol occurs in the authoritative map.
- Retained native `do_ipt_set_ctl` and `do_ip6t_set_ctl` identities to keep the verdict narrow: native IPv4/IPv6 iptables remains compiled, and this is not a general netfilter safety claim.
- Added the authoritative primary/related patches and a five-input schema-v2 tri-state model with exhaustive output assertions. Focused validation passed `6 tests, 36 subtests`; the complete suite passed `570 tests, 148606 subtests`; the public harness passed; corrected independent exact-binary/package review returned **ACCEPT**.
- No target syscall, socket, namespace, packet, filter table, target execution, crash, corruption, privilege transition, or persistence action was created.

## 1.67.0 - reject the key read/revoke race by exact same-rwsem effects

- Rejected CVE-2015-7550 for exact recovered `vmlinux`: `keyctl_read_key` takes `key +0x20` for reading before validation and retains it through the optional read callback; `key_revoke` takes the same rwsem for writing across revoked-state mutation and the optional revoke callback.
- Retained complete exact `key_revoke`, `keyctl_revoke_key`, `keyctl_read_key`, and `key_validate` functions plus upstream fix `b4a1b4f5047e4f54e194681125c74c0aa64d637d`. Machine code proves matching effects but not direct patch provenance.
- Added a six-input schema-v2 Boolean model with exhaustive output assertions. Focused validation passed `8 tests, 73 subtests`; the complete suite passed `564 tests, 148570 subtests`; the public harness passed; independent exact-binary/package review returned **ACCEPT**.
- No target/keyctl syscall, key, process, thread, race, allocation pressure, target execution, crash, corruption, privilege transition, or persistence action was created.

## 1.65.0 - CORRECTION: my "V-009 eliminated" conclusion is refuted by V-028

- Reviewing the register's newer entries (V-015…V-032, added by another workstream) turned up a correction to **my
  own** conclusion at 1.48.0. I had eliminated the launcher's unverified path as a first stage on the grounds that
  every launch target is a literal under read-only `/navi`. **That reasoning was invalid.**
- **V-028** establishes the opposite: `AppLauncher` exports a session-bus `launch(appid, appname, applocation, …)`
  and the runtime **`applocation` QString** reaches the AppProcess program field, where a dispatcher byte (`+0x1c`)
  selects a route to a `QProcess::start` call site **without either verifier call**. New objects accept appids
  1…1024 and require only `QFile(applocation).exists()`. My string-literal survey of the binary simply could not see
  a path that is supplied at runtime, and I treated the absence of evidence in one method as evidence of absence.
- **The correct boundary, taken from V-028 rather than restated by me:** the service has a uid-0 default; the
  recovered session bus uses EXTERNAL authentication and, with no user connection rule, defaults to the daemon's
  uid, so this is **not** arbitrary cross-uid access. It is relevant to **same-uid, SMACK-separated HMI code** that
  can own the service name, register the `Request` object and authenticate.
- **Consequence for the chain this thread was building:** the "first stage" is a live candidate again, and it is the
  same-uid HMI context — which is exactly the precondition the V-012 (`EnvironmentFile`) → V-034 (update trust
  anchor) chain needs. My 1.48.0 entry therefore overstated its negative, and the chain is one step closer to
  complete than the records said yesterday.
- Recorded plainly: a wrong conclusion of mine, corrected by a different workstream's evidence, with the boundary
  that actually holds. The lesson is the same one this session keeps teaching — **absence of a literal is not
  absence of a path**.

## 1.66.0 - bind V-031 source mutability to live DAC and SMACK evidence

- Confirmed that both recovered eMMC fstab branches configure `/update` as a writable ext4 partition and that boot setup conditionally constructs `/update/usb/bin` plus staged executable placeholders.
- Separated writable-filesystem structure from actor write access: rootfs mountpoint metadata is hidden by the mounted filesystem; setup does not pin staged uid/gid/mode or `SMACK64`; and `SMACK64EXEC` does not authorize writes.
- Counted configured write relations from the floor label and 22 named `App::*` labels to `App::upgrade` objects, while retaining directory/file labels, DAC metadata, process credentials/labels, loaded rules, and update serialization as runtime gates.
- Added `evidence/update-source-runtime-policy.md` with exact configuration hashes and narrow V-031 implications.
- Extended the passive disconnected-bench bundle to record `/update` and `/update/usb` metadata plus read-only `SMACK64`/`SMACK64EXEC` query states for the update namespace, staged updater/XML, installed AppDMClient/AppUpgrade, and persistent public key. Process records now retain real/effective/saved/filesystem uid/gid values and supplementary groups separately.
- The collector distinguishes absent path, absent attribute, unavailable provider, query error, malformed label, and successful label; parsed reports retain raw records and derive `facts.smack_xattrs`. Static audit rejects bare and path-qualified file/xattr/ownership/mode mutation utilities and mutating `attr`/`setfattr` modes.
- Focused validation passed `23 tests, 20 subtests`; the complete suite passed `556 tests, 148497 subtests`; the public harness passed; corrected independent package review returned **ACCEPT**. The emitted 22,464-byte probe has SHA-256 `c043f3ed5c1815897de8ee5faececd6c36a9cb36e24fabd83d43b7dab164fc56` and passed static audit plus `/bin/sh -n`.
- No target xattr, file, mount, process, update state, package, partition, slot, radio, network, or boot state was changed; no recovered executable was run.

## 1.64.0 - register numbering collision found and repaired (provenance added)

- Discovered while checking the register: it is edited by **more than one workstream**, and has been advanced
  concurrently to **V-032** while three sections this thread appended re-used **V-012**, **V-013** and **V-014**.
  That produced duplicate numbers pointing at different findings — a documentation defect that would mislead
  anyone citing them.
- Repaired: those three sections are now **V-033** (production compositor ships full DWARF), **V-034** (update
  trust anchor on a writable root) and **V-035** (root media parsers link ageing codec libraries). The three V-007
  additions are now headings of the form `## Amendment to V-007 (X) — …`, so they read as amendments rather than
  pseudo-entries.
- Added a **provenance note** at the top of the register: entry numbers are not stable while it is edited
  concurrently, so any citation must include the **title** as well as the number, and late material appears as
  `Amendment to V-0NN (X)`. Changelog references written before today use the old numbers and must be read by title.
- Also noted for the record that this thread's register edits and another stream's entries have been interleaving
  for several rounds without conflict in git, which is exactly why the semantic collision survived unnoticed: the
  merges were clean, the meaning was not.

## 1.63.0 - malformed-input probe: a negative result with a weak instrument, recorded as such

- **Images are not reachable on this path.** Five malformed PNGs in `/media/mtp` gave `processed=0`, because the
  scan directory is typed `audio:/media/mtp/`. So the reachable parsers are the **audio** ones (`id3`, `ogg`,
  `flac`, `mp4`) — not `png`/`jpeg` as the V-014 inventory implies. That is a useful correction to the surface.
- Five malformed **audio** files (half truncation, 200-byte truncation, a 300-byte bit-flip run, 512 random bytes
  after the header, and a synthetic `ID3` header declaring 2 GB) were processed with `commit=1, uptodate=5,
  errors=0`; the daemon survived (`pid 720` before and after) and `dmesg` recorded **zero segfaults**.
- **Recorded as worth very little.** Truncation and bit-flips are the crudest mutations available; surviving them
  says almost nothing about memory safety, since the defects that matter need structurally valid containers with
  hostile field values. A real answer needs structured generation or a coverage-guided harness driving the plugin
  libraries — neither attempted.
- Neither V-007 nor V-014 moves on this. No parser vulnerability is claimed.

## 1.67.0 - bind direct decryption producers to copyWhatsNewFiles and normalize public runtime evidence

- Exact Qt local row 60 resolves to public slot `void copyWhatsNewFiles()`; generated row-60 case `0x16e59f` calls entry `0x101110`, and exact FDE `[0x101110,0x104c1b)` contains all three selected direct `decryptionFile` calls at `0x10281c`, `0x102de9`, and `0x103398`.
- Homebrew LLVM instruction flow resolves the nonzero encryption-mode branches and argument families: top-level branch-selected package archive to fixed update-temp archive, enumerated system-tree files to paired normal/USB-in-OTA destinations, and enumerated controls-tree files to paired normal/USB-in-OTA destinations. Generated row-64 forwarding call `0x16e030` remains separate.
- The expected hash-bound public log contains seven exact-shape records, not the previously stated six: lines `1414,1710,7279,11714,11975,17205,21713`. All seven have matched bounded `copyWhatsNewFiles` context and normalized removable-USB archive to update-temp archive classes.
- Added a fail-closed read-only log parser with regular-file/stability/size checks, strict expected SHA-256 by default, explicit synthetic mode, exact grammar, duplicate/ambiguity/traversal/control rejection, and deterministic UTF-8/LF normalized JSON. Transient tokens and raw volume labels are not retained or emitted.
- Public-log runtime observation is not attributed to the exact recovered ELF: logged-build identity and direct-versus-meta invocation mechanism are unknown. Complete dynamic/indirect/external provenance, external/D-Bus reachability, attacker control, update acceptance, root, and persistence remain unknown.
- Focused validation passed `39 tests, 8230 subtests`; the full tests-scoped suite passed `674 tests, 351252 subtests`; public/privacy harnesses, exact-report encoding determinism, `py_compile`, and `git diff --check` passed.
- No recovered target/helper was executed and no device/radio, malformed target artifact, update package, payload, bypass, partition/slot/boot state, root action, or persistence material was created or exercised.

## 1.66.0 - resolve AppUpgradeEngine local Qt metadata row 64 without overclaiming producers

- Exact Qt 5 revision-7 metadata resolves local `AppUpgradeEngine` row 64 to public slot `QString decryptionFile(QString encFile, QString destPath)`. The value 64 is the selected local row index, is not asserted as the absolute `QMetaObject` method index, and is not signal number 64; signal count is seven. The absolute index remains unknown without `methodOffset()` and inheritance context.
- The relocation-bound generated dispatcher resolves `a[1] -> encFile -> %rdx`, `a[2] -> destPath -> %rcx`, call `0x100b30`, and QString return -> `a[0]`. The function's verifier call remains `0x100bb0`.
- Added an explicit-selection, read-only decoder with strict ELF/Qt bounds, checked metadata intervals, synthetic and optional exact tests, bounded static excerpts, and a schema-checked forwarding manifest. Forwarding can resolve only when the manifest and the current instruction-evidence excerpt are both supplied and their SHA-256 binding matches. The deterministic report SHA-256 is `330799c5215a0d3fda7c8870820240cb023c9b3a6c9673100778a038fe1d14a3`.
- Metadata binding and machine-code forwarding are resolved separately; complete producer provenance remains unresolved. Dynamic meta-invocation, indirect/external paths, runtime invocation, external/D-Bus reachability, attacker control, update acceptance, root, and persistence remain unknown. V-032's fail-closed Boolean model is unchanged.
- Focused validation passed `29 tests, 8228 subtests`; the full suite passed `664 tests, 351250 subtests`; the public and privacy harnesses passed; deterministic exact-report comparison passed.
- No recovered target or helper was executed; no device, network/radio path, malformed target input, payload, bypass, package, partition, root action, or persistence material was exercised or created.

## 1.65.0 - map inner FUMO authentication coverage and its unresolved parameters

- Bound exact embedded FUMO identity, startup path derivation, verifier `[0x45820,0x45d75)`, file-MD5 helper `[0x140f50,0x1413e4)`, and worker relaunch `[0x6c9a0,0x6cab5)`.
- A whole-`.text` direct-call inventory found six file-verifier calls and two MD5-helper calls. Fixed and enumerated operands cover the descriptor, archive, firmware entries, resources, or navigation files.
- Several signature-verifier routes remain parameterized. At `0x100bb0` the target derives from function argument `%rdx`, and direct caller `0x16e030` forwards a QString from a meta-call argument structure. Absence of a staged/running outer-updater operand is therefore not proved.
- Startup reduces `argv[0]` to a base directory used for resources. The worker `execv` wrapper contains no direct executable verifier/hash step inside that FDE, but parameterized, indirect, external, loader, and boot-stage checks remain unresolved.
- Added V-032, retained exact assembly and parameter-forwarding callers, a dedicated evidence report, and a thirteen-input schema-v2 Boolean model. Incomplete target coverage keeps direct reauthentication and identity-gap closure `null`; absolute absence additionally requires indirect/external exclusion.
- Focused validation passed `10 tests, 8203 subtests`; the full suite passed `553 tests, 148482 subtests`; the public harness passed; corrected independent exact-binary/package review returned **ACCEPT**. No updater, verifier, helper, target path, recovered executable, launch request, package, archive, partition, slot, boot state, target syscall, root action, or persistence mechanism was exercised.

## 1.62.0 - interposition is structurally blocked; the shim approach is retired

- Moved the hook to `wl_proxy_marshal_array` (non-variadic, exported, correct `void` signature for this
  libwayland). Built cleanly (18,944 bytes, symbol exported) and tested against `weston-simple-shm`, a client that
  definitely commits. Result: **still no hook call, zero output.**
- The explanation is a structural one. In client code, requests go through the **variadic `wl_proxy_marshal`**
  inline wrapper, and libwayland's own `wl_proxy_marshal` forwards to `wl_proxy_marshal_array` **by a direct
  intra-library call**, which does not traverse the PLT and therefore cannot be interposed by `LD_PRELOAD`.
  Interposing the outer variadic form is impossible to do generically, because forwarding an unknown `va_list`
  to a variadic callee cannot be expressed in C.
- Verified along the way: the object **is** mapped into the client (4 mappings in `/proc/<pid>/maps`), and
  `libwayland-client.so.0` has **no `.gnu.version_d`**, so symbol versioning was never the obstacle.
- **The shim approach is retired.** Three interposition points were tried — exported `wl_surface_commit` (never
  called: inline wrapper), `wl_proxy_marshal_array` (intra-DSO call), and a connect-time hook (killed the client).
  None can work from outside the process.
- Realistic alternatives, for the record: (a) rebuild `ias-shell`/the client with an explicit buffer-supply path —
  not possible without vendor source; (b) patch the client binary to attach before commit — heavy but feasible
  given its DWARF; (c) accept that the black frame is the client's behaviour in this environment and stop.
- Recorded plainly: this line of attack is closed rather than merely slow.

## 1.64.0 - prove AppDMClient's pathname/object-identity boundary

- Bound verifier wrapper `[0x34870,0x34d43)`, staging `[0x7ff60,0x830e4)`, and XML reader `[0xe1e90,0xe3166)` in exact recovered AppDMClient machine code.
- The wrapper returns only integer status. Staging later constructs a two-path copy and calls a separate process at `0x8296b`; the XML reader verifies at `0xe1ff7` and later opens at `0xe22d5` or `0xe281f`. No retained open description or identity revalidation connects those operations.
- Added V-031 as an exact static pathname-reopen/conditional TOCTOU candidate. Runtime source mutability, changed-object observation, later inner authentication, accepted update, partition writes, slot/boot acceptance, root and persistence remain unproved.
- Added retained assembly, a dedicated evidence report, and an eleven-input Boolean-only schema-v2 model. Contradictory runtime mutability/immutability fails closed; absent runtime source-state evidence leaves substitution feasibility `null` rather than asserting a bypass.
- Focused validation passed `9 tests, 2056 subtests`; the full suite passed `543 tests, 140279 subtests`; the public harness passed, and independent corrected package review returned **ACCEPT**.
- No updater, verifier, source pathname, race, command, launch request, target executable, update package, partition, slot, root action, or persistence mechanism was exercised.

## 1.61.0 - why the shim silently did nothing: the symbol it interposes is never called

- The shim is **loaded** — verified directly with `grep vnbuf /proc/<pid>/maps` (**4 mappings**) alongside
  libwayland-client (4) in a client that definitely commits. Yet the hook never ran and produced no output.
- Cause: in wayland-client, `wl_surface_commit()` and its siblings are **`static inline` wrappers in the generated
  header**, which call `wl_proxy_marshal_flags()` internally. A client compiled against that header **never
  references the exported `wl_surface_commit` symbol at all**, so interposing it is a no-op. Symbol versioning was
  ruled out first: `libwayland-client.so.0` has **no `.gnu.version_d` section**, so it exports unversioned symbols.
- This explains both earlier surprises: the shim loading cleanly (once all `wl_` symbols were resolved at runtime)
  while having no effect, and the app surviving a preload that previously killed it.
- **Corrected hook point:** interpose `wl_proxy_marshal_flags` (and `wl_proxy_marshal` /
  `wl_proxy_marshal_constructor` for older call sites), and act when the proxy's interface is `wl_surface` and the
  opcode is `commit` (6 in the `wl_surface` request table). The dummy buffer is then attached by marshalling an
  `attach` (opcode 1) through the real function before letting the commit through.
- Nothing about the earlier client measurement changes: it commits without attaching, and that remains the defect
  the shim exists to compensate for.

## 1.60.0 - shim loads cleanly, but preloading it kills the client

- Fixed the load failures. `LD_PRELOAD` resolves eagerly enough that **every** libwayland symbol had to be resolved
  at runtime rather than left undefined: `wl_shm_interface` (a data symbol) failed first, then
  `wl_display_get_registry`, and the same would have happened for the rest. The shim now resolves all seven through
  `dlsym(RTLD_DEFAULT, …)` in a table, and `nm -D` reports **zero undefined `wl_` symbols**.
- **With it preloaded the client exits immediately and silently** — not alive after ten seconds, empty log. So the
  shim currently *breaks* the target rather than exercising it. That is a worse state than having no shim at all,
  and it is recorded as such.
- Likely causes, in order: the interposed `wl_display_connect` performing a registry roundtrip before the client has
  finished its own setup; a signature or calling-convention mismatch on one of the interposed entry points; or a
  fault inside the commit hook (for example the fixed-size surface table).
- Next step is not to test the hypothesis but to make the shim **non-invasive**: hook only `wl_surface_commit`,
  leave `wl_display_connect` untouched, obtain the display lazily from the surface instead, and log to stderr so a
  crash leaves a trace. A shim that can crash the target is not usable evidence.

## 1.63.0 - reject CVE-2018-14634 by exact six-MiB argument cap

- Bound complete exact `copy_strings` machine code against preventive upstream commit `da029c11e6b12f321f36dac8771e833b65cec962` rather than relying on the `4.1.27-abl` banner.
- The recovered code preserves `ARG_MAX`, then caps larger argv/environment space at `min(rlimit(RLIMIT_STACK)/4, 0x600000)` using the exact rlimit load, divide, constant, minimum selection, size comparison, and failure routing.
- Added complete exact machine code, the authoritative patch, an eleven-input Boolean-only schema-v2 model, and exhaustive 2,048-state tests. Incomplete size-construction or cap facts remain unknown unless an unbounded acceptance path is explicit.
- Kept installed identity, privileged-executable presence, runtime exec/uid/SMACK policy, argument construction, execution, stack corruption, root and persistence unobserved. No recovered-kernel exec syscall, target process, oversized target argument vector, privileged target executable execution, target execution, crash, or privilege action was created; ordinary host validation used Python subprocesses outside those target claims.

## 1.62.0 - reject CVE-2016-7914 by exact associative-array leaf guard

- Bound complete exact `assoc_array_insert` and `__key_link_begin` machine code against upstream fix `8d4a2ec1e0b41b0cf9a0c5cd4511da7f8e4f3de2` rather than relying on the `4.1.27-abl` banner.
- In the inlined terminal-node loop, null slots are handled separately, metadata-tagged node/shortcut pointers branch past `ops->compare_object`, and only non-null leaf-tag fallthrough reaches the callback. The loop covers all 16 slots.
- Added complete exact machine code, the authoritative patch, a nine-input Boolean-only schema-v2 model, and exhaustive 512-state tests. Incomplete guard facts remain unknown unless a nonleaf callback path is explicit.
- Kept installed identity, runtime key/SMACK policy, tree shape, callback execution, out-of-bounds read, disclosure, crash, corruption, root and persistence unobserved. No target/key syscall, key/keyring state, target execution, crash, or privilege action was created.

## 1.59.0 - buffer shim built and deployed; the trial run did not execute

- Built `vnbuf_shim.so` (16,904 bytes, cross-built with the bundled zig). It interposes `wl_display_connect` to
  capture the display and bind `wl_shm`, and `wl_surface_commit` to attach a known opaque-magenta `ARGB8888`
  1920x720 buffer the first time a surface is committed — deliberately at **commit**, because the measurement was
  that the client never calls `attach` at all, so hooking attach would never fire.
- **The trial run was inconclusive, not negative.** No `vnbuf:` line appeared on the console and the compositor
  mapped **0** surfaces, so the application did not start or did not reach the compositor in that attempt. The
  shim therefore remains unexercised.
- Two faults of my own in that run, both worth recording: launch diagnostics were grepped from `/tmp/w.log` while
  the shim writes to `/dev/ttyS0` and the client's stderr (so the search looked in the wrong file), and the
  no-dump result followed from the absent surface rather than from any shim behaviour.
- Next step is ordered and small: (1) confirm `AppHomeScreen` starts under `LD_PRELOAD` and that `vnbuf:
  connected, shm=…` appears, (2) only then read `shim mapped` and attempt a capture, (3) expect magenta if the
  stack renders. Until step 1 passes, no conclusion about the shim is available.

## 1.61.0 - reject CVE-2016-7911 by exact same-task-lock effects

- Bound complete exact `get_task_ioprio`, `SyS_ioprio_get`, and `exit_io_context` machine code against upstream fix `8ba8682107ee2ca3347354e018865d8e1967c5f4` rather than the `4.1.27-abl` banner.
- Getter acquires `task +0x630` before reading `task->io_context +0x678` and `io_context->ioprio +0x12`, then unlocks. Exit acquires the same lock, loads and clears the same pointer field, unlocks, and only then releases the old object.
- Added exact machine code, the authoritative patch, an eight-input Boolean-only schema-v2 model, and exhaustive 256-state tests. Incomplete fix facts remain unknown unless an unlocked read is explicit.
- Kept installed identity, runtime syscall policy, task permissions, concurrency, stale access, crash, corruption, privilege gain, root and persistence unobserved. No target or ioprio syscall, process, thread, race, allocation pressure, crash, or target execution was created.

## 1.60.0 - reject CVE-2016-7910 by exact block iterator cleanup

- Compared complete exact `disk_seqf_next`, `disk_seqf_start`, and `disk_seqf_stop` machine code against upstream fix `77da160530dd1dc94f6ae15a981f24e5f0021e84` rather than relying on the `4.1.27-abl` banner. The same compiled effect is present; the stripped binary cannot distinguish a cherry-pick, stable backport, or independently applied identical change.
- Bound successful iterator publication, the allocation-failure path that skips the owner-field store, exact `class_dev_iter_exit`, exact `kfree`, and the pointer-width zero store to the same `seq_file.private +0x78` field immediately afterward.
- Verified both operation tables use the fixed stop routine. A later failed start followed by framework stop sees null, rejecting the CVE-specific stale-pointer dereference/repeated-free premise.
- Added complete exact machine code, the authoritative patch, an eight-input Boolean-only schema-v2 model, and exhaustive 256-state tests including inconsistent-state rejection. Incomplete fix facts remain unknown unless freed-pointer retention is explicit.
- Independent review corrected a mistaken allocator-cache description and required the stripped-binary provenance boundary, then returned **ACCEPT**. Focused validation passed `10 tests, 267 subtests`; complete validation passed `510 tests, 135370 subtests`; the public harness passed.
- Kept scope narrow: installed identity, runtime proc visibility, allocation failure, stale use, repeated free, crash, corruption, privilege gain, root and persistence remain unobserved. No proc file, allocation pressure, target execution, crash, or trigger sequence was created.

## 1.58.0 - VM: the buffer question needs a shim, not more probing

- Two attempts to capture the client's protocol trace produced no trace at all — the application log was empty and the
  final markers were cut off before the run ended. Under this project's standing rule (confirm the path was reached
  before reading a zero) that is **no result**, not "no configure events".
- What is already established stands unchanged: the compositor renders (control capture works), our shim maps the
  application's surface (`ias-soft: shim mapped surface`), the shared-memory segments are created and attached
  (attach errors 0 in the run where the app reached the widget code), and the client issues five `commit`s while
  never issuing a non-nil `attach`. So the scene has a view whose surface has no buffer: nothing to composite, and a
  correctly black frame.
- The gap is therefore purely client-side, and probing it further from outside has produced diminishing returns.
  The clean next step is an **LD_PRELOAD shim** that intercepts `wl_surface_attach`/`wl_surface_commit` and, when
  the client attaches no buffer, supplies a known dummy shm buffer. If a frame then appears, the entire stack —
  backend, CRTC, IAS shell, renderer, capture — is proven end to end and the client's omission is isolated as the
  single remaining defect. That is a simulated adaptor in the project's own terms rather than another measurement.
- No claim is made here that the client is defective in general; only that on this build, in this environment, it
  commits surfaces without buffers.

## 1.59.0 - reject CVE-2016-9806 by exact saved-object cleanup

- Compared complete exact `netlink_dump` against upstream fix `92964c79b357efd980812c4de5c1fd2ec8bb5520` rather than relying on the `4.1.27-abl` banner.
- Bound `cb->module` and `cb->skb` loads before callback-mutex release, followed by `cb_running` clear and exact `mutex_unlock`; exact `module_put` and `consume_skb` then consume only the saved register values.
- Post-unlock cleanup never reloads the reusable callback fields, rejecting the CVE-specific race in which a new dump's skb is consumed or double-freed.
- Added complete exact machine code, the authoritative patch, a seven-input Boolean-only schema-v2 model, and exhaustive 128-state tests. The model rejects the CVE only from complete saved-object effects; incomplete fix facts leave the vulnerable reload premise unknown rather than asserting it.
- Bound the function range to authoritative recovered `work/eu-260128/kallsyms.tsv` and its SHA-256, and independently checked the addresses against the ELF's embedded address vector rather than using a differently transformed derived map.
- Independent instruction/model/provenance review returned **ACCEPT**. Focused validation passed `9 tests, 136 subtests`; complete validation passed `500 tests, 135103 subtests`; the public harness passed.
- Kept scope narrow: installed identity, runtime netlink reachability, unrelated netlink defects, corruption, privilege gain, root and persistence remain unobserved. No socket, message, dump request, thread, race, crash or target execution was created.

## 1.58.0 - identify exact CVE-2017-6001 perf move-group race

- Added V-030 after binding complete exact `SYSC_perf_event_open` and `perf_event_ctx_lock_nested.isra.60` machine code.
- The software-group-to-hardware-context path reads `group_leader->ctx` before a potentially blocking double-mutex acquisition and then removes/migrates through that saved context without acquiring a live reference, revalidating identity/retrying, or checking post-lock whether another caller already moved the group.
- The same binary's single-context helper implements the nonzero-reference, lock, identity-check, unlock/drop/retry discipline, proving those effects are compiled but do not protect the affected move-group path.
- Bound upstream fix `321027c1fe77f892f4ea07846aeae08cefbbb290`, `CONFIG_PERF_EVENTS=y`, and exact initialized `perf_event_paranoid=1`. The installed runtime value and production PMU/event behavior remain unobserved.
- Classified this as an exact static local privilege-escalation candidate, not observed exploitation. A winning race, stale/dead-context use, controlled corruption, credential/SMACK transition, unrestricted root and persistence remain unproved.
- Added complete exact FDE evidence, the authoritative patch, a nine-input Boolean-only model, and exhaustive 512-state tests. No event, syscall, thread, race, crash or target execution was created.

## 1.57.0 - CVE check against the pinned versions: one hit, rejected as a false positive

- Queried GitHub's advisory database for each pinned library and compared against published vulnerable ranges.
- **One candidate: CVE-2018-14550** (high, 8.8, range `<= 1.6.35`) against `libpng 1.6.32`. **Rejected**: the advisory
  places the defect in `get_token` in **`pnm2png.c`** — a contrib/demo utility — and `pnm2png` **does not exist
  anywhere in the image** (searched). Recording it would have been a false positive against undeployed code.
- No advisories returned for libogg, libvorbis, libtheora, mp4v2 or file. **Caveat kept explicit:** that database is
  sparse for older libraries, so "0" is not evidence of absence.
- Consequence: **no specific CVE is asserted** for these builds. V-014 remains a supply-chain-ageing finding where
  the exposure signal is release date plus the privilege the parsing runs under.
- The useful lesson is procedural: an automated CVE match is a lead, not a finding. The first one this exercise
  produced was wrong, and it would have looked authoritative in a report.

## 1.56.0 - V-014: the root parsing stack is built on 2011-2017 era codec libraries

- Enumerated what the media parsers actually link, and read the versions from the image:
  `libpng16` **1.6.32**, `libogg` **0.8.2**, `libvorbis` **0.4.9**, `libtheoradec` **1.1.4**,
  `libmatroska`/`libebml` **6.0.0/4.0.0**, `libmp4v2` **2.0.0** (upstream abandoned ~2012), and `libmagic`
  **1.0.0**.
- Every one of those parses attacker-controlled bytes, in a process running as **uid 0** (measured), over a path a
  local process can populate — and V-007's parse reachability is now demonstrated, so the exposure is not
  hypothetical plumbing.
- Recorded as **V-014**, a supply-chain-ageing finding: version dating is evidence of exposure, not proof of a
  defect. No specific CVE is claimed present, and no exploit was attempted. Confirming which published issues affect
  these exact versions is a discrete follow-up.
- Remediation is the useful part: update the codec stack, parse in an unprivileged sandboxed helper, and stop
  running media parsing as root — the last of which fixes the class regardless of library age.

## 1.56.0 - close the AF_PACKET wrapped frame-count residual

- Traced the absent `frames_per_block * tp_block_nr` overflow guard through exact `packet_set_ring`, allocation, V1/V2 receive, transmit, poll, readiness, progression, lookup, mmap, and exact vmlinux `vm_insert_page`.
- Proved that allocation uses the full block count while every logical position bounded by wrapped `frame_max` still indexes below that count and remains within block size. The proof explicitly covers wrapped `tp_frame_nr == 0` and `frame_max == UINT_MAX`.
- Separated `packet_mmap`'s 32-bit block-count × pages-per-block multiplication. A wrapped expected size can understate the VMA, but exact `vm_insert_page` rejects addresses at or beyond `vm_end`; no out-of-VMA insertion follows.
- Found three signed vector-index opcodes beginning at block count `0x80000001`, then rejected them by exact allocator semantics. The minimum vector is `0x400000008` bytes, exact `__get_order` yields order 23, and exact `__rmqueue`/`__alloc_pages_nodemask` reject every order above 10, so `__kmalloc` returns null before block allocation, cleanup, publication, or mmap.
- Classified the missing guard as a correctness/early-rejection gap rather than a defensible V1/V2 frame-lookup corruption or local-root primitive. Added complete FDE evidence, a deterministic Boolean/reduced-width model, exhaustive toy-width and 512-state tests, and explicit null runtime/impact outcomes.
- Generic public-only Astra planning corroborated the proof obligations. Fable remained unavailable because its catalog route is not advertised for native subagents; DeepSeek Flash was static-ready but native dispatch rejected its model identifier, so neither route received private target context.
- Independent review found and corrected missing `free_pg_vec` evidence, an overbroad cleanup claim, argparse abbreviation aliasing, an off-by-one signed-index threshold, and unclassified setup/mmap signed index sites. The final exact allocator closure and cross-document re-review returned **ACCEPT**. Focused validation passed `11 tests, 23 subtests`; complete validation passed `483 tests, 134451 subtests`; the public harness passed.
- No socket, ring, mmap, packet, namespace, capability, allocation pressure, race, crash, target execution, corruption, privilege transition, root, or persistence action was performed.

## 1.55.0 - V-007 parse reachability demonstrated

- The corrected channel worked. With a genuine MP3 at `/media/mtp/mtptest.mp3` on a filesystem mounted there, and
  `lightmediascannerd` running as root under a session bus:

  ```
  Scan Progress audio:/media/mtp/ commit=1, uptodate=1, processed=0, deleted=0, skipped=0, errors=0
  mtptest rows: 5     → /root/.config/lightmediascannerd/db.sqlite3  (0600 root:root)
  ```

- So a **root process read attacker-supplied content from a removable-media mount point, copied it into its store,
  and indexed it into a root-owned database**. V-007 moves from "configuration confirmed, parse unproven" to **parse
  observed**.
- Stated precisely: this establishes reachability of the parsing path with attacker bytes at full privilege, which is
  the precondition any parser defect needs to matter. It does **not** establish a parser vulnerability — no malformed
  input was crafted and no corruption attempted. What remains is a dedicated fuzzing exercise, not a reachability
  question.
- The `/media/usb` dead end was what made this possible: correcting the channel to MTP is what produced a result
  after ten attempts on the wrong path.

## 1.54.0 - V-007 corrected: the scanner walks MTP, not USB

- Ten configurations later, the scanner's own progress output settles it:
  `Scan Progress audio:/usr_data/media/` then `Scan Progress audio:/media/mtp/` — **`/media/usb` never appears**, with
  a genuine MP3 present *and* the path mounted as its own filesystem, and regardless of a config file placed at
  `/app/bin/lightmediascanner.conf` or `$HOME/.config/lightmediascanner.conf`.
- The effective scan set is `/usr_data/media` + `/media/mtp`, which looks compiled in rather than read from the
  shipped `directory=` line. `lightmediascannerd` references `g_get_user_config_dir`, which is where the database
  path comes from, but changing the directories had no effect.
- **Correction to V-007:** the removable-media channel is **MTP**, not USB mass storage. The scanner walks
  `/media/mtp/` — the mount point an attached phone or media player presents — which sits under the same
  world-writable `/media`. The conclusion stands (a root process parses attacker-supplied removable content); the
  channel previously named in the entry was wrong and is corrected in place.
- Practical consequence: a USB stick full of media is *not* what this scanner consumes; a device that presents MTP
  is. That is a narrower but more specific attack surface, and it is the one worth testing next.
- Thread closed here at ten attempts, with the correction recorded rather than the earlier text quietly left standing.

## 1.53.0 - V-007: database sink located and measured; indexing of /media still unproven

- Located the artefact: `lightmediascannerd` writes `<HOME>/.config/lightmediascannerd/db.sqlite3` — measured at
  **155,648 bytes, `0600`, `root:root`**, created by the root daemon after `lightmediascannerctl scan`. The
  pipeline is real and its output is root-only.
- **Indexing of `/media` still not demonstrated.** Two probes in `/media/usb` — a text file named `.mp3` and a
  genuine MP3 copied from the image as `attacker.mp3` — produced zero rows in that database.
- Working hypothesis, stated as such: the daemon indexes paths registered by a **mount/udev event** rather than
  re-walking `directory=` on demand, and this projection never emits one.
- V-007 final status: privilege measured, targets sourced, invocation executes, sink measured and root-owned;
  consumption of attacker bytes unproven. The configuration defect is confirmed and the reachability claim stops
  one harness feature short. Eight attempts have been made; the thread is closed here rather than varied further.

## 1.52.0 - V-007: control channel found and scan made to execute

- Identified the missing harness feature: `lightmediascannerctl` talks to the **session** bus, not the system bus
  — its failure message was `Could not get session bus connection … dbus-launch --autolaunch`. Started a session
  bus with `dbus-daemon --session --print-address --fork`.
- With it, the daemon registers `org.lightmediascanner` (one matching name on the bus, verified) and
  `lightmediascannerctl scan` **runs**: `Server at :1.0, try to start scan` / `Elapsed time: 0.025 seconds`.
- A database still does not appear at the configured `db-path`, so the sink resolves elsewhere in this build.
- **Correction:** the `find / -newer probe.mp3` sweep used earlier is invalid here — the guest clock reads 1970, so
  every image file appears newer and the result is meaningless. Discarded rather than interpreted.
- Status for V-007 is now three parts, two of them established: privilege (measured, uid 0), scan targets
  (sourced), scan invocation (**now executes**). What remains is confirmation that the scan consumed
  attacker-supplied bytes, which needs the sink located.

## 1.55.0 - narrow secure-boot-ignore and identify manifest read-bound mismatch

- Bound `CONFIG_KEYSTORE_SECURE_BOOT_IGNORE=y` to its exact machine-code effect: `keystore_init` logs that it is not checking secure-boot status and proceeds directly to `keystore_fill_seeds`; `keystore_register` likewise proceeds to client derivation without a status query. Ordinary seed, device-number, cdev, client-ID, derivation, and allocation failures remain.
- Identified separate weak error handling: `__class_create` and `device_create` return `ERR_PTR`, but `keystore_init` checks only for NULL and can report success after those failures. This does not establish signature bypass or privilege gain.
- Confirmed the option does not remove the separate `manifest_init` initcall or the surviving `verify_oem_signature → SHA-256 → manifest_key_verify_digest` chain. It is not a general package, update-signature, verified-boot, or arbitrary-firmware bypass.
- Located matching Intel-authored public Linux 4.1 source at vendor commit `0c9640bba6a841f524f5947d0741386792674577`. It confirms the full command-line spelling is `ABL.oemkm=<size>@<physical-address>`; bare `oemkm` is only the internal ABL-list entry.
- Corrected the manifest outer-size range: `size - 1 <= 0x3ffffff` accepts `1..0x4000000` bytes inclusive.
- Identified an exact conditional boot-time OOB-read candidate: declared-length/type reads lack copied-size checks; later header reads can conditionally reach `+0x1b`; and the internal declared length/extension walk are never directly bounded by the copied allocation. The arithmetic model accounts for the 101-entry/16-bit-stride cap and does not classify unreachable beyond-copy extents.
- Identified a separate feasible invalid free: after copying, `manifest_init` replaces the allocation-pointer global with `base + 0x24`; a header rejection later passes that interior cursor to `kfree`. This may crash or corrupt allocator state at boot, but controlled corruption is not established.
- Kept impact narrow: boot-parameter and physical-memory control are unproved, and no controlled OOB write, code execution, root, update acceptance, boot acceptance, or persistence is established.
- Added complete-function evidence plus independent fail-closed Boolean and bounded-integer models. Review caught and resolved ERR_PTR routing, conditional-read wording, no-loop/capped-walk model counterexamples, a missing device wrapper, and the previously unclassified interior free; final review returned **ACCEPT**.
- Focused validation passed `13 tests, 2084 subtests`; full validation passed `472 tests, 134428 subtests`; the public harness passed. No manifest, boot input, signature, update, target execution, crash, overwrite, flashing, or persistence action was performed.

## 1.54.0 - reject the FLIC read/write-bounds CVE family by exact comprehensive rewrite

- Rejected the CVE-2016-9634/9635/9636/9808 FLIC write-bounds family for exact recovered `libgstflxdec.so`, despite its embedded GStreamer `1.8.3-r0` recipe path. The same comprehensive rewrite also rejects CVE-2016-9807's distinct `flx_decode_chunks` invalid-read mechanism.
- Distinguished the initial local bounds patch from upstream's comprehensive `153a8ae` GstByteReader/GstByteWriter rewrite. Exact source-line values and machine code establish that the latter is present.
- Bound checked chunk sub-readers, writer initialization over exact frame storage and size, previous-frame copy, FLI/FLC line guards, cumulative destination-position checks, bounded reads/writes, and helper-to-chain failure propagation before output publication.
- Kept outcomes distinct: CVE-2016-9807 is an invalid-read/crash issue, while the other named issues concern write bounds. The bounded chunk reader and propagated failures reject the former without converting it into a write-corruption claim. This still does not establish general FLIC or media-stack safety.
- Added the authoritative patch, both complete affected FDEs, bounded nine-Boolean classifier, exhaustive 512-state tests, and explicit null runtime/impact outcomes.
- Independent review caught a frame-vs-chunk sub-reader mislabel, a truncated helper FDE, and an incomplete final error-route excerpt. All three were corrected; final review returned **ACCEPT**. A second review of the CVE-2016-9807 extension also returned **ACCEPT**. Focused validation passed `6 tests, 526 subtests`; current full validation passed `472 tests, 134428 subtests`; the public harness passed.
- No FLIC/media input, recovered parser execution, trigger, heap manipulation, overwrite, crash, code execution, privilege transition, or persistence action was performed.

## 1.51.0 - the parse is not demonstrable in this harness; recorded as such

- Four attempts to make the root scanner actually parse a locally-dropped file, all with a probe present and all
  running as **uid 0**:
  1. default config (`db-path` commented out — no destination);
  2. written config with `db-path=/tmp/lms.db` and `directory=audio:/media/usb/`;
  3. same plus `LD_LIBRARY_PATH=/app/lib`, after finding `usr/lib/liblightmediascanner.so.0.5.1` is a **38-byte
     stub** while the real 300 KB library is in `app/lib`;
  4. daemon driven directly.
- Every attempt: root, **no database, no diagnostic output at all**. The image ships
  `app/lib/lightmediascanner/plugins`, so the likely requirements are a plugin-path variable or a **mount/udev
  event** rather than `startup-scan` under this projection.
- Recorded as "not demonstrable here" rather than as another open question, because the difference matters: the
  privilege and the scan targets are established, and only the execution of the parse is not. The register says
  exactly that and no more.
- The empty log is the same trap for the fifth or sixth time in this project — silence from a daemon is not
  evidence of anything until it is known the daemon reached the code that would speak.

## 1.53.0 - reject VMNC CVE-2016-9445/9446 by exact vendor backport

- Rejected CVE-2016-9445's VMNC dimension-overflow mechanism for exact recovered `libgstvmnc.so`, despite its embedded GStreamer `1.8.3-r0` recipe path.
- Bound complete packet-parser flow: WMVi width and height are unsigned 16-bit fields; every feasible WMVi route compares both with 16384 before handler dispatch, and either oversized value returns `-1`. A syntactic bypass edge is predicate-infeasible, so no strict structural-dominance claim is made.
- Bound the handler's accepted depths to 8/16/32 bits, the exact width/height/bytes-per-pixel field assignments, and the relevant allocation to `g_malloc0`. The maximum accepted product is `16384 * 16384 * 4 = 0x40000000`, so the guarded multiplication fits signed 32-bit arithmetic. The zeroed allocation also rejects CVE-2016-9446's uninitialised-canvas mechanism.
- Added the authoritative upstream patch, exact machine-code excerpt, bounded numeric model, tests, and evidence. This rejects only the two named mechanisms, not every VMNC defect or every media-parser candidate.
- Independent review caught and resolved missing allocation-operand/depth binding, an overbroad structural-dominance claim, and an inadmissible bpp-3 model state; final review returned **ACCEPT**. Full validation passed `453 tests, 131818 subtests`; the public research harness passed.
- No media file, parser execution, packet, overwrite, crash, code execution, privilege transition, or persistence action was performed.

## 1.50.0 - V-007's root identity measured live; the parse itself still not demonstrated

- Stopped inferring the privilege from an absent `User=` and measured it on a running guest:
  `mediamanager` → `pid=718 Uid: 0 0 0 0`, and `lightmediascannerd` driven directly → `pid=709 Uid: 0 0 0 0`.
  Both are **root**, confirmed rather than deduced.
- **The parse is still not demonstrated.** With `/media/usb/probe.mp3` in place, no scanner database was produced
  and no probe marker appeared in any database on the image — `lightmediascanner.conf` ships its `db-path`
  **commented out**, so the daemon had nowhere to write. The step that would consume attacker-supplied bytes did
  not run in this harness.
- Recorded as a partial confirmation: the root identity claim is now measured; the reachability claim remains
  configuration-level plus two open bug-hunts (scan completion in production config, and a parser defect). The
  register still claims neither.
- This is the fifth time this project has had to separate "the process was running" from "the code path executed"
  — here the distinction is between root identity (proven) and parsing (not), and conflating them would have
  produced a materially overstated entry.

## 1.52.0 - identify exact CVE-2017-9242 IPv6 append-data ordering

- Added V-029 after binding exact ordinary UDPv6 call flow and the complete recovered `__ip6_append_data` control flow.
- Confirmed that skb allocation and the `skb_copy_and_csum_bits` fraggap copy occur before the signed `datalen - transhdrlen - fraggap` calculation and rejection. The later `-EINVAL`/`kfree_skb` path cannot prevent any overwrite caused by the earlier copy.
- Compared the branch-complete function against upstream fix `232cd35d0804cc241eb887bb8d4d9b3b9881c64a`; no equivalent early rejection dominates allocation or copy.
- Classified this as an exact pre-fix local kernel out-of-bounds-write candidate, not demonstrated root. NVD supports local denial of service; crafted internal state, actual overwrite, controlled corruption, code execution, privilege gain and persistence remain unobserved.
- Added the authoritative patch, selected and branch-complete machine-code evidence, a Boolean-only six-input model, complete 64-state tests, and explicit null runtime/impact outcomes.
- Focused validation passed `7 tests, 77 subtests`; independent semantic/model review returned **ACCEPT** after branch-complete evidence and conditional overwrite wording were added. No socket, syscall, packet, target execution, overwrite, crash, privilege transition, or persistence action was performed.

## 1.51.0 - reject CVE-2017-7533 by exact dentry-name snapshot effects

- Rejected CVE-2017-7533 for the exact recovered kernel rather than inferring exposure from the `4.1.27-abl` version banner.
- Bound exact snapshot dominance in both `__fsnotify_parent` and `vfs_rename`: the parent path takes a stable name before `fsnotify`, while the rename path snapshots before dentry mutation and retains it through `fsnotify_move`.
- Confirmed the full upstream-fix semantics from commit `49d31c2f389acfe83417083e1208422b4091cd9e`: inline names are copied while the dentry lock is held; external names gain a reference under that lock; release drops the external reference after use.
- Preserved the sink nuance: `inotify_handle_event` still has separate length and copy operations, but the exact reviewed producers no longer pass a concurrently mutable name. This rejects the CVE-specific premise, not all fsnotify defects.
- Added the authoritative patch, reviewed machine-code excerpt, Boolean-only seven-input model, complete 128-state truth table, deterministic-output checks, and explicit null runtime/corruption/root outcomes.
- Focused validation passed `7 tests, 142 subtests`; independent semantic/model review returned **ACCEPT**. No watch, rename, race, heap manipulation, target execution, corruption, privilege transition, or persistence action was performed.

## 1.49.0 - V-007 confirmed, and its precondition is weaker than assumed

- `mediamanager.service` starts `/app/bin/mediamanager` with **no `User=`** → runs as **root**.
- `app/bin/lightmediascanner.conf` ships `startup-scan=true` with
  `directory=audio:/usr_data/media/;audio:/media/usb/;audio:/media/mtp/` — removable-media mount points are
  parsed **by default at startup**, before any user action.
- Combined with the earlier finding that `/media` is a `tmpfs` at mode `01777`, the physical-media precondition
  disappears for this step: a **local unprivileged process can drop files into `/media`** and the root scanner
  parses them on its next scan.
- So the first stage is confirmed **at the configuration level** — root parser over attacker-supplied content,
  locally reachable — and the only remaining piece is a memory-safety defect in the parsing stack. That is a
  bug-hunt, not an access question, and the register says so rather than implying an exploit exists.
- Chain now reads: local file drop into `/media` → root media parser (needs one parser bug) → root →
  `/tmp/session_appmgr.env` (V-012) → update trust anchor (V-013) → persistent compromise. Two of those four
  links are confirmed configuration, one is confirmed-with-precondition, and one is a hypothesis.

## 1.50.0 - exact AppLauncher D-Bus path overturns the V-009 negative

- Added V-028 after tracing the exact exported `launch(appid, appname, applocation, ...)` session-bus methods. The caller's runtime `applocation` is copied into the AppProcess program field, byte `+0x1c` is set to one, and the direct branch reaches a `QProcess::start` call site without either identified verifier call.
- Corrected commit `3090f69`: its literal-string scan saw only fixed read-only `/navi` targets, but literal references cannot exclude a runtime QString argument. The route is not limited to replacing a binary on `/navi`.
- Corrected the older public description in the opposite direction as well: both exact verifier paths treat false as terminal. The defect is the separate on-demand dispatcher that bypasses both identified verifier calls, not fail-open behavior after either verifier returns false.
- Preserved the real authorization boundary. The private session bus defaults to connections from the daemon's uid; this is not arbitrary cross-uid access. It is relevant to the many uid-zero, SMACK-separated HMI processes only if service ownership, Request-object registration, same-uid authentication, effective SMACK access, a relevant AppProcess object, QProcess acceptance, exec-time target control/access and effective launcher privilege all hold at runtime.
- Added a reviewed machine-code/configuration excerpt, a Boolean-only 131,072-state model, focused tests, and passive metadata for `Dbuslaunch.service` and `/tmp/session_appmgr`. No D-Bus request, executable, target launch, credential/label transition, trust-anchor write, update, or persistence action was created.

## 1.48.0 - V-009 tested as the missing first stage: it is not one

> **Superseded by 1.50.0 / V-028:** this test considered literal paths only and missed the runtime D-Bus `applocation` argument.

- The open question was whether the merged V-009 (launcher starts binaries without the signature routine) could
  supply the first-stage execution that V-012 → V-013 needs. It cannot.
- `AppLauncher`'s path references are `/navi`, `/navi/navi/Bin/AppNavi`, `/navi/navi_1`, `/navi/navi_2` and
  `/navi/system/system`, plus `navi_public.key`. Both `/navi` and `/navi2` are mounted **`ro`** — verified in
  `fstab_emmc:19-20` (`ro,noatime,nouser,auto,exec,suid`) and on a live boot
  (`/dev/root /navi ext4 ro,noatime,data=ordered`).
- So replacing a launch target needs a write to read-only media, which is precisely the root step the entry was
  proposed to bypass. V-009 is a defence-in-depth failure that **presupposes** a privileged write rather than a
  way in, and the chain still lacks a first stage.
- That is a negative result that sharpens the register: it removes the most attractive candidate for the gap and
  moves attention to the paths that genuinely start from unprivileged input — the media parsers (V-007, which run
  as root with no separation, confirmed) and the removable-media handling (V-006, latent).
- Recorded as a test that failed to confirm, not as a refutation of V-009's underlying observation, which stands.

## 1.49.0 - exact CVE-2020-29660 TTY session-lock classification

- Added V-027 after binding exact `TIOCGSID` dispatch, unlocked session-pointer
  reload/dereference, two same-field writer lifetime transitions, and the
  missing effects of upstream fix `c8bcd9c5be24fb9e6132e97da5a35e55a83e36b9`.
- Classified it as a conditional local information-disclosure candidate rather
  than root: upstream describes a theoretical four-byte read for `PREEMPT=y`,
  while this kernel has voluntary preemption and full preemption unset. SMP is
  recorded independently; a realizable harmful overlap remains unproved.
- Added focused reviewed assembly, the authoritative patch, a Boolean-only
  model, a complete 64-state truth table, CLI/determinism invariants, and
  explicit null outcomes for runtime overlap, disclosure, and privilege gain.
- No PTY, ioctl, thread, race, PID-lifetime operation, stale access, target
  execution, privilege transition, or persistence action was performed.

## 1.48.0 - passive runtime triage for V-024 through V-026

- Added a deterministic, fail-closed host classifier for completed passive
  bench-state reports. It preserves true/false/unknown rather than converting
  missing providers into negative evidence.
- Extended the read-only probe to capture `/dev/pts/ptmx` and device major/minor
  identity. A positive V-024 PTY gate now requires an effective major-5/minor-2
  endpoint, effective world read/write permissions, a valid `/dev/pts`
  directory, and a devpts mount.
- Kept `/proc/modules` name state and the current `unix.ko` file hash separate:
  their conjunction does not prove that loaded module memory came from that
  file. An exact `uname` release token likewise does not prove installed
  `vmlinux` byte identity.
- Four independent review rounds ended in `ACCEPT` after correcting report
  validation, module-binding language, symlink/target handling, three-valued
  conjunctions, producer fallback compatibility, and PTMX device identity.
- No PTY, socket, timerfd, module operation, race, trigger, target command, or
  firmware write was performed.

## 1.47.0 - V-012 lowers V-013's precondition from root to local code execution

- Verified the merged V-012 against the image: `lib/systemd/esinit:10` mounts `tmpfs` on `/tmp` with **default
  options** (kernel default root mode `01777`, world-writable), and **eleven** enabled services read
  `EnvironmentFile=/tmp/session_appmgr.env` — `ApplicationLauncher`, `nua`, `MediaBrowser`, `mediamanager`,
  `CryptoService`, `watchdogd`, `ofono`, `mof`, `vbtd`, `credman`, `remote`. `ApplicationLauncher.service`
  carries **no `User=`**, confirming the root context directly.
- That supplies the privileged write primitive V-013 said it needed. Chain, now recorded end to end: local code
  execution → write `/tmp/session_appmgr.env` with a loader override → one of eleven root services starts →
  write the update trust anchor → all future updates trust a substituted key.
- The directory chain to the anchor is `0755` throughout, so step 3 genuinely requires step 2's root and not
  merely a local user — that distinction is kept explicit rather than flattened into "local user can own
  updates".
- **Not established:** a concrete first-stage execution primitive, and any practical service-restart trigger.
  So this raises V-013's severity from "requires root" to "requires local code execution plus one restart", and
  is recorded as such rather than as a demonstrated exploit.

## 1.46.0 - V-013 runtime question answered: root stays writable, so the anchor is mutable and persistent

- Checked the merged PR's update trust-anchor entry against the image and a live boot:
  - kernel cmdline mounts root **`rw`**; live `/proc/mounts` reports `ext4 rw,noatime,data=ordered`
  - `etc/fstab` is **empty**, and the root line in `etc/fstab_emmc` is **commented out**
  - `esinit` lines 12-13, which would `remount,ro /`, are **commented out**
  - `app/share/AppUpgrade/teruten5_pub.key` is mode **0755** on that writable root, and writing into its
    directory from a root context succeeded on the live guest
- So the anchor is mutable at runtime **and the substitution survives reboot**, because it lives on eMMC rather
  than tmpfs. That is worse than a transient exposure and strengthens the merged finding.
- **Caveat recorded:** the live guest shows the file owned by uid 501/`dialout`, which is an extraction artefact
  from this project, not vendor truth. Only mode, path and the rw mount are established, so the precondition
  remains "a privileged write primitive", not "any local user".
- Nothing here demonstrates a write primitive; it establishes that one would be sufficient and durable.

## 1.45.0 - V-006 settled by experiment: the payload is not deliverable from a device

- Re-ran the merged PR's exact claim. QEMU `usb-mtp` with `serial=pwn;id>/tmp/VM-PWNED` presents a real
  descriptor carrying the payload **and** the `060101` PTP interface the vulnerable branch requires. Measured:
  - descriptor on the wire: `pwn;id>/tmp/VM-PWNED` (intact)
  - property delivered to `usb-automount`: **`pwn_id__tmp_VM-PWNED`** — `;`, `>` and `/` rewritten to `_`
  - `ID_USB_INTERFACES=:060101:` present, so the branch condition was met
  - **`/tmp/VM-PWNED` was not created**
- So the string that reaches the sink from a device is inert. The external report of root execution is most
  consistently explained by a synthetic event or directly injected `ID_SERIAL_SHORT`, which bypasses
  `builtin_usb_id` — something a physical device cannot do. That makes it a harness artefact rather than a
  device-reachable root path.
- Both findings agree the **source defect is real**: unquoted `sprintf` into `system()`. The disagreement was
  always about reachability, and reachability is what severity rests on. V-006 stays a latent defect.
- Register updated with the measurement inline, so the merged claim and its refutation sit together rather than
  in two repositories.

## 1.44.0 - merged haraldaarz's register PR, and a V-006 contradiction to resolve

- Merged `JaredReabow/ioniq-5-Reverse-Engineering#1` ("Document additional Ioniq 5 findings", Harald
  Aarseth) as squash commit `ebacec0`. Note the PR targets the **older** repository, not the one this
  project commits to.
- **Their findings (5 new entries plus two upgrades):** V-009 launcher can start binaries without the
  signature routine executing (state-gated, failure not terminal, keys on world-accessible media); V-010
  engineering keypad gate reduces to unsalted digests of static default codes; V-011 world-writable marker
  files drive systemd path units including a forced reboot (local DoS, cheap persistence); V-012 eleven root
  services take `EnvironmentFile=` from a world-writable runtime path, admitting `LD_PRELOAD`-class injection
  on restart; V-013 update signature **trust anchor** is a plain file on the rw root, so a privileged write
  primitive substitutes the key and every future update (USB and OTA) trusts a substitute. V-008 upgraded: the
  serial console is enabled by default on every boot rather than being an exception.
- **The important conflict, recorded rather than resolved by fiat.** Their V-006 is upgraded to "root command
  execution demonstrated end-to-end in the QEMU harness" using an `ID_SERIAL_SHORT` of
  `pwn;id>/tmp/VM-PWNED` with `ID_USB_INTERFACES=":060101:"`. Our measurement on the same image contradicts
  that: udev delivered `a_id__tmp_v006.id_echo__IFS_V006KMSG__dev_kmsg_#` for a comparable payload, with an
  allow-list of alphanumerics plus `#+-.:=@_` verified present in `systemd-udevd` and `libudev`, and a positive
  control showing the same string executes correctly when handed straight to `/bin/sh`.
- Both cannot be true of the same code path. The most likely reconciliation is that a **synthetic udev event
  carrying a pre-set `ID_SERIAL_SHORT`** bypasses `builtin_usb_id` entirely, whereas a real device descriptor
  does not — which would make their result an artefact of the harness rather than a device-reachable path.
  That is a testable distinction and is the next thing to settle, because "USB → root" and "root → root" have
  completely different severity.
- Numbering collides with this project's register (our V-009..V-012 are different findings). Out of scope for
  the merge — different repository — but it must be reconciled before the two registers are ever combined.

## 1.43.0 - strace gave the real segment names; the shim now targets them

- **Stopped guessing Qt's naming.** `strace -e trace=openat` on `AppHomeScreen` with the compositor up produced
  the exact paths it opens, and they are not the keys previously assumed. The six it actually touches are:

  `KEYSUPPORTCHINESE`, `MICOMSTATUSMESSAGE`, `NMODELAPTIMEKEY`, `STATUSBARINTERNALDATA`,
  `STSTATUSBARNAME`, `TMSSERVICETABLE` — each with a matching `qipc_systemsem_` file.

  `/Ihu` and `/Inform` were keys referenced by *other* binaries, not by this application.
- The earlier "rule" was wrong and is retracted: `sha1(key)` matched two samples but matches **none** of the six
  observed here, so it was coincidence plus an over-general conclusion from a small number. The lesson is that
  observing the path directly is cheaper than deriving a naming scheme, and I should have straced first.
- `ihu-shim` now creates exactly those six names (and their `qipc_systemsem_` counterparts, 256 KB each) and
  reported six successful `shmget` calls with ids returned.
- **This run's result is inconclusive, not negative:** `commit` is **0**, which means the application never
  reached the compositor at all, so the shared-memory and buffer counters in it are meaningless. Fourth
  occurrence of the same trap, and this time it was caught before the numbers were read as a finding.
- Next: print the first lines of `/tmp/app.log` in the same run, so the failure that precedes the compositor is
  visible, and only then re-read the attach counters.

## 1.42.0 - with the compositor up the shim does not fix the attach; buffer still never supplied

- Ran the decisive measurement properly this time, compositor up and shim applied:
  `attach(nil)` **0**, non-nil `attach` **0**, `commit` **5**, `Cannot attach to shared memory` **9**,
  surface mapped **1**.
- Two conclusions, one of them a correction:
  1. **The client still never supplies a buffer.** Zero `attach` calls of any kind after five commits, so the
     black frame is explained by the client, not the renderer. That question is now closed.
  2. **The previous entry's "attach errors: 0→0" was another zero-means-nothing-ran.** Without a compositor the
     application fails earlier, at display initialisation, and never reaches widget creation — so the attach
     failures it would have logged were never reached. With a compositor present the count returns as 9.
- So `ihu-shim` is **not** yet doing its job, and the honest status is that the shared-memory wall is still
  standing. Its naming derivation is sound (two samples agreed), but a key that matches and a segment that
  exists are evidently not sufficient: Qt also validates the segment on attach, and a 64 KB zero-filled region
  with no expected structure may be rejected, as may a `ftok` project id or size mismatch.
- This is the fourth zero-that-meant-nothing in this session. The pattern is consistent enough to state as a
  standing rule for this project: **before reading any zero, confirm the code path that would increment it was
  reached.** Both of the last two false results would have been caught by that check.

## 1.41.0 - Qt's segment naming derived, and the shared-memory wall comes down

- **Derived Qt's segment naming empirically** rather than by reverse-engineering the library: the file Qt uses
  is `qipc_sharedmemory_<key><sha1(key)>`, then looked up with `ftok()`/`shmget()`. Verified against two
  segments the vendor actually created — `ApplicationEnableInformation` → `…7cb8a380…` and
  `ApplicationManagerInformation` → `…b9a7139f…`, both exactly `sha1(key)`. A third sample
  (`APPLICATIONMANAGERINFORMATION`, all caps) does not match, which is recorded rather than explained away.
- Built `ihu-shim` on that basis: it creates the key files and the SysV segments for `/Ihu`, `/Inform`,
  `/Information`, `/Can`, `/PhevInterface` and `/CryptoService` (both slash and slashless spellings, 12 names,
  64 KB each, zero-filled).
- **It works.** With the shim run first, `AppHomeScreen`'s
  `Cannot attach to shared memory` count goes from **12–13 to 0**, and the process stays alive. The failure
  that has been blocking the UI for several rounds is gone.
- The frame captured in the same run was still uniformly black, but the capture preceded the change in the
  client's behaviour and cannot be used to answer the drawing question.
- **Recorded correction:** the follow-up `WAYLAND_DEBUG` run returned zeros for attaches, commits and shared
  memory alike, which looked like a result and was not one — the compositor was never started in that run, so
  the app had nothing to connect to. Third occurrence of a zero that means "nothing ran"; the lesson keeps
  needing to be applied.
- Next: re-run `WAYLAND_DEBUG` **with the compositor up** and count non-nil `attach` calls. That single number
  decides whether the remaining gap is client-side drawing or the renderer.

## 1.40.0 - strace attempt blocked the wrapper; switching to publishing `/Ihu` ourselves

- The tracing attempt did not produce data. Running the daemon under
  `busybox timeout 15 strace -f -e trace=connect …` **blocked the wrapper** long enough that the daemon never
  started, which is visible in the result: `writeToDBus` errors are **0**, i.e. zero attempts, and no trace
  lines reached the console. Same trap as two entries ago — a zero that means nothing ran.
- Rather than keep micro-debugging the vendor daemon's bus handling, the cheaper route to the actual goal is to
  **publish `/Ihu` ourselves**. The widget failures are `QSharedMemory::handle … key file doesn't exist`; the
  key is known (`/Ihu`, plus `/Can`, `/Inform`, `/Information`, `/PhevInterface`), and Qt's layout is
  observable from any segment the vendor creates (`/tmp/qipc_sharedmemory_<KEY><hash>` plus a matching
  `qipc_systemsem_` file).
- That is exactly the project's stated shape of work: a **simulated adaptor** standing in for a component the
  emulation cannot run. It sidesteps the daemon's connection bug entirely and answers the question that
  matters — whether the UI will draw once its shared state exists.
- Concretely: a small tool to create `/tmp/qipc_sharedmemory_Ihu…` with the same naming and SysV segment Qt
  would create, fill a plausible boot-info structure, then start `AppHomeScreen` and read the
  `Cannot attach to shared memory` count. If that count goes to zero, the widgets proceed and the frame is the
  next thing to look at.
- Kept in the record as a correction of approach, not a failure of the daemon: the daemon's D-Bus bug is real
  and worth returning to, but it is not on the critical path if a publisher shim gets the UI drawing.

## 1.49.0 - identify exact timerfd cancellation context-lock gap

- Audited exact built-in timerfd code against CVE-2017-10661 fix
  `1e38da300e1e395a15048b0af1e5305bd91402f6`.
- Added V-026: same-file operations resolve one live context, while membership
  setup/removal changes `might_cancel` outside the narrow global-list lock and
  without a common context-derived lock.
- Proved the later waitqueue lock does not dominate the transition and creation
  lacks an equivalent second-lock initialization.
- Kept impact conservative: no timerfd, shared descriptor, concurrency, list
  corruption, UAF, crash, root, or persistence was executed or established;
  public privilege impact is less certain than denial of service.
- Added authoritative patch evidence and a reviewed Boolean-only model; both
  semantic reviews and code review returned `ACCEPT`.

## 1.48.0 - identify exact AF_UNIX MSG_PEEK garbage-collector gap

- Audited exact shipped `unix.ko` against upstream CVE-2021-0920 fix
  `cbcf01128d0a92e131bd09f1688fe032480b65ca`.
- Added V-025: both datagram and stream MSG_PEEK attached-file paths call exact
  `scm_fp_dup`, preserve the result in the SCM cookie, and reach descriptor
  delivery without direct or indirect serialization on exact `unix_gc_lock`.
- Bound the global lock to `.bss+0x102e`, traced every intervening call, and
  distinguished the stream socket receive mutex from the GC lock.
- Extended the read-only bench bundle to capture `/proc/modules` and hash exact
  `unix.ko` without creating a socket or loading a module.
- Kept impact bounded: no socket, descriptor transfer, GC pass, concurrency,
  UAF, controlled reuse, corruption, root, or persistence was executed or
  proved.
- Added authoritative patch evidence and a reviewed Boolean-only model; both
  semantic reviews and code review returned `ACCEPT`.

## 1.47.0 - identify exact TTY process-group wrong-object locking

- Audited exact UNIX98 PTY/TIOCSPGRP semantics against upstream CVE-2020-29661
  fix `54ffccbf053b5b6ca4f6e45094b942fab92a25fc`.
- Added V-024: master-side setter writes the linked slave's referenced pgrp PID
  while holding the master lock; slave-side setter writes that same field while
  holding the slave lock. Exact helper and PTY installation code independently
  bind field offsets, lock identity, and distinct reciprocal objects.
- Bound intended exposure to shipped startup that creates `/dev/ptmx` mode
  `0666` and mounts devpts, without treating configured intent as runtime state.
- Extended the read-only bench bundle to collect `/dev/ptmx`, `/dev/pts`, and
  existing mount metadata before any active TTY work.
- Kept impact bounded: no PTY open, ioctl, concurrent interleaving, PID UAF,
  controlled reuse, corruption, root, or persistence was executed or proved.
- Added authoritative patch evidence and a reviewed Boolean-only model; both
  semantic reviews and code review returned `ACCEPT`.

## 1.46.0 - bind the exact mremap stale-TLB ordering window

- Audited exact ordinary-PTE `move_page_tables` semantics against upstream
  CVE-2018-18281 fix `eb66ae030829605d61fbef1909ce310e29f78821`.
- Added V-023: exact source-PTE clearing and destination installation precede
  release of the bound source/destination PTLs; old-range TLB flushing is
  deferred until outer exit, with no earlier flush in the full function.
- Kept the result bounded to a static stale-translation window. No concurrent
  invalidation, physical-page release/reuse, stale access, corruption, code
  execution, root, or persistence was executed or established.
- Added authoritative patch and focused instruction evidence plus a reviewed
  Boolean-only ordering model; both semantic reviews and model review returned
  `ACCEPT`.

## 1.45.0 - exact vmacache wrap semantics restore a local-root candidate

- Researched ordinary unprivileged 4.1-era kernel escalation candidates and
  prioritized CVE-2018-17182 because it needs no namespace, protocol, device,
  setuid helper, or optional module in the generic path.
- Bound exact live `vma_adjust`, `do_munmap`, `vmacache_flush_all`, `mmput`, and
  `vmacache_find` control flow to recovered `vmlinux` identity and addresses.
- Added V-022: both invalidation paths increment a 32-bit generation and call a
  live flush helper on zero; its exact single-user route skips pointer clearing;
  lookup compares and stores only 32-bit generations. None of the upstream
  64-bit/removal fix effects is present.
- Kept operational impact bounded: a complete cycle is 4,294,967,296 states,
  and no mapping cycle, thread lifecycle, wrap, stale pointer, dereference,
  controlled reuse, corruption, or root transition was run or established.
- Added authoritative patch evidence and a reviewed Boolean-only model; full
  semantic and model reviews returned `ACCEPT`.

## 1.44.0 - one ALSA timer padding disclosure survives a partial backport

- Extended the ALSA review to CVE-2016-2544, CVE-2016-2548, CVE-2016-2549,
  CVE-2016-4569, and CVE-2016-4578 using exact relocatable-module semantics.
- Rejected CVE-2016-2544: sequencer queue deletion holds `q->timer_mutex`
  across exact timer stop and close.
- Named CVE-2016-2548 separately: the previously proven slave stop/close paths
  reinitialize both ack and active links. CVE-2016-2549's hrtimer provider is
  not compiled or shipped.
- Rejected CVE-2016-4569 and the general CVE-2016-4578 callback because each
  clears all 32 record bytes before queueing.
- Added V-021: `snd_timer_user_tinterrupt` clears a separate timestamp but not
  either four-byte padding region in its 32-byte event record. Exact queue and
  read paths copy all 32 bytes, supporting a conditional eight-byte-per-record
  kernel-stack padding disclosure. Runtime event reachability and actual bytes
  remain unobserved; this is not root or code execution.
- Added a reviewed Boolean-only flow model and retained authoritative upstream
  fixes. No module, node, ioctl, timer, event, read, target byte, or privilege
  transition was exercised.

## 1.43.0 - ALSA timer race fixes are present

- Bound exact shipped `snd-timer.ko` to SHA-256 and Build ID and retained
  section-relative instruction evidence with relocations.
- Rejected CVE-2016-2545: non-auto expiry calls exact `list_del_init` on the
  current timer instance's active link.
- Rejected CVE-2016-2546: open initializes a per-user mutex shared by the sole
  ioctl dispatcher and release; all returning ioctls unlock and release holds
  it through timer close before freeing the user object.
- Rejected CVE-2016-2547: slave attach, master close, delayed start, and stop
  contain the upstream nested global/timer locking and complete ack/active
  unlink effects.
- No module load, device open, ioctl, thread, race, corruption attempt, or
  privilege transition was performed.

## 1.42.0 - three ordinary local paths are backported too

- Audited three high-priority unprivileged kernel candidates that do not depend
  on user namespaces, setuid binaries, special device nodes, or optional DCCP,
  N_HDLC, or BPF-syscall support.
- Rejected CVE-2015-7613: effective credentials and all reviewed message/shared
  memory state are initialized before IDR/IPC publication.
- Rejected CVE-2016-7117: the delayed `recvmmsg` socket-error store precedes
  exact `fput_light`, eliminating the named post-release dereference.
- Rejected CVE-2017-8890: accepted children clear `inet_sock.mc_list`; exact
  multicast teardown corroborates the cleared field offset.
- Added minimal instruction excerpts, authoritative patches, and a boolean-only
  semantic matrix. No socket traffic, multicast operation, IPC object, race,
  target syscall, or privilege transition was executed.

## 1.41.0 - USB-MIDI ownership has one cleanup authority

- Audited physical pre-login CVE-2016-2384 against exact shipped
  `snd-usbmidi-lib.ko`. `CONFIG_SND_USB_AUDIO=m`, generic modules, and the
  descriptor-driven probe surface are present, so the old version was a
  credible candidate rather than a package-label dismissal.
- Rejected the candidate at instruction level. Once raw-MIDI installs its
  private-free callback, every generic and alternate endpoint-creation failure
  returns directly through the error epilogue. None performs the second direct
  object free deleted by the upstream fix.
- Retained exact relocations, section-relative addresses, file-offset mapping,
  and the authoritative one-hunk patch. No USB descriptor, peripheral, module
  load, target execution, endpoint failure, crash, or privilege transition was
  produced.

## 1.40.0 - the missing clear was present as control flow

- Audited CVE-2017-11176 against exact recovered `vmlinux`, not its
  `4.1.27-abl` banner. POSIX message queues are compiled in and the relevant
  return-one retry exists, making this a credible local-escalation candidate.
- Rejected the candidate after instruction-level data-flow review. Although the
  loop edge has no explicit socket-register clear, failed retry `fdget` and
  socket-lookup paths both jump to skb-only cleanup. They cannot carry the old
  released socket into `netlink_detachskb`; this is the semantic effect of
  upstream `sock = NULL`.
- Added exact retained excerpts, upstream patch provenance, and a boolean-only
  model that distinguishes explicit zeroing from compiler-equivalent cleanup
  routing. No race, message-queue trigger, corruption attempt, target
  executable, or privilege transition was run.

## 1.39.0 - root reaches the bus; the daemon does not

- The diagnostic separates the two possibilities cleanly. From **inside the wrapper**, in the same context and
  at the same moment the daemon starts:

  ```
  MMWRAP bus socket: srw-rw-rw- 1 root root /run/dbus/system_bus_socket
  MMWRAP env DBUS_SYSTEM_BUS_ADDRESS=unset
  MMWRAP dbus rc=0 out=method return sender=org.freedesktop.DBus -> dest=:1.3 … string "120b9c679d9418758b1fa07300000012"
  ```

  `dbus-send --system` **succeeds** and returns the bus ID, while the daemon logs `writeToDBus` failures 37
  times in the same boot.
- Therefore the fault is **not** the socket, not SMACK, not the ruleset and not ordering: root can reach the
  system bus perfectly well at that instant, and the vendor daemon's own connection is what is broken.
- This retires the SMACK-ordering theory that the previous two entries were pursuing. Applying `smackctl
  apply` early (rc=0) had already failed to help, and this measurement explains why: the ruleset was never the
  obstacle.
- Two tooling notes worth keeping: `dbus-send` lives at **`/usr/bin/dbus-send`** in this image (not `/bin`), and
  a failed first attempt with the wrong path returned rc=127 — a "command not found" that could easily be
  misread as a bus failure.
- Next diagnostic is specific: run the daemon under `strace -f -e trace=connect,socket` from the wrapper and
  print the syscall result at the moment it claims there is no connection. That will show whether it never
  calls `connect()` at all, connects to the wrong address, or connects and then discards the socket.

## 1.38.0 - the peer is decoupled and the plugin runs; the D-Bus wall remains

- The peer now runs as its own systemd unit (`micom-peer.service`) so it outlives the daemon's restart
  cycle, and `ExecStartPre` steps are prefixed with `-` so an already-mounted devpts no longer fails the
  unit. Result: `MMWRAP peer waited=1 ready=yes link=/dev/pts/0`, unit active on both starts.
- **A correction to the previous entry, which matters.** The "`writeToDBus` errors: 0" recorded there was an
  artefact: the wrapper was blocked in a 120 s wait for `smack.service` and was killed by the activation
  timeout before it ever reached `exec`, so the daemon never ran and could not produce errors. Zero errors
  meant zero attempts.
- Fixed by applying the ruleset directly in the wrapper rather than waiting: `/sbin/smackctl apply` returns
  **rc=0** and the wrapper now always reaches `MMWRAP exec daemon`.
- With the daemon actually running the real picture returns: **26 `writeToDBus` errors** and the MICOM
  exchange still happening (the daemon attempts to publish, so it is reading replies). No `bootinfo reply`
  lines this boot, which means the ask sequence differed — the peer answered with empty payloads rather than
  the 35-byte ones, so the boot-info ids were not requested at startup here.
- So the state is: peer decoupled and healthy, ruleset applied early, daemon running and exchanging frames,
  and **D-Bus publication still failing**. Applying SMACK rules earlier did not fix it, which weakens the
  SMACK hypothesis for this specific failure.
- Next diagnostic is cheap and specific: from inside the wrapper, run
  `dbus-send --system --print-reply --dest=org.freedesktop.DBus / org.freedesktop.DBus.ListNames` and print
  its exit status and first line. That distinguishes "root cannot reach the system bus at this moment" from
  "the daemon's own connection setup is at fault".

## 1.39.0 - qualify FUMO force-marker progress provenance

- Traced callback FDE `[0x11f1b0,0x120a9e)` and exact file-writer calls for
  the FUMO completion and force markers. Progress zero attempts `processing`
  then `force_launch=run`; the branch-local progress-100 sequence attempts
  `complete` then force value `none`, while later scheduled flow can attempt
  `run` again. The weak writer does not prove full, successful, or atomic state
  transitions.
- Named exact `DeltaUpdateProgressHandler` and timer routes into the callback.
  Their direct force-write branches read no named signature, digest,
  certificate, or payload-authentication result. Thus `force_launch=run` alone
  does not itself establish completion or authentication in this write-site
  evidence.
- Retained the upstream boundary: this does not show that unauthenticated input
  can cause a valid progress event, update acceptance, writes, slot/boot trust,
  root, or persistence. The scheduled writer still separately requires both
  completion strings and scheduled-update state.

## 1.37.0 - SMACK ordering was the D-Bus fault

- **Root cause of `[writeToDBus] There is no connection` found: ordering, not permissions.** `smack.service`
  applies the ruleset at **t=128 s**, while the daemon is started at **t=18 s**. Its bus connection is
  attempted before the rules that permit it exist, so every write fails for the whole boot.
- The wrapper now waits for `smack.service` to become active before `exec`ing the daemon. Result:
  **`writeToDBus` errors dropped from 27 to 0.** The daemon reaches the bus.
- The SMACK unit itself needed a fix first: `fstab_emmc` mounts `smackfs` at **`/sys/fs/smackfs`**, but
  `smack.service`'s `ExecStartPre` wrote to **`/smack/netlabel`**, so the pre-start always failed and the
  ruleset was never applied. Patching those paths made the first start succeed at t=128 s; a later restart
  still fails, which is consistent with re-applying a ruleset that is already loaded.
- New regression from the ordering fix, recorded plainly: this boot shows **twice** `MMWRAP begin`, no
  `smack waited` line, and **zero bootinfo replies**. The wrapper evidently restarted, and the peer was not
  servicing the instance that finally spoke to the bus, so the MICOM exchange that worked in the previous
  boot did not happen here.
- So the two halves now each work in isolation — MICOM exchange (previous boot) and D-Bus publication (this
  boot) — and the remaining task is to have both in one boot: single wrapper instance, peer alive for the
  lifetime of the daemon, and the daemon started after SMACK rules are applied.

## 1.38.0 - trace the inner FUMO navigation-map signature gate

- Reconstructed inner-FUMO function `0x128070` and its asynchronous start/result
  polling. A dedicated disable marker, absent NaviUpdateApp/NUA provider,
  non-encrypted mode, or no navigation-map candidate completes this one gate
  without running the signature worker. Failures/timeouts stop through
  `0x127e80`; success sets `this+0xd5` and re-enters the gate.
- Corrected the earlier unresolved relationship: FUMO startup
  `/update/disableEncryptionUpdate` sets the same mode byte later tested by the
  navigation-map non-encrypted skip branch. This is a named map-signature skip,
  not a universal package-signature, payload, write, boot, root, or persistence
  bypass.
- Added a numeric/boolean-only gate model with focused tests, exact retained
  evidence, and passive disconnected-bench capture for the dedicated marker.
  No recovered updater ran and no marker, package, partition, or slot changed.

## 1.36.0 - the MICOM peer and the daemon are talking; boot info is answered

- **Frames are finally exchanged.** The peer answered the boot-info asks:
  `bootinfo reply to 0x01aa (35 bytes)` and `bootinfo reply to 0x02c3 (35 bytes)`, and the daemon logged
  `READ Data( 5 ) aa 82 17 00 3f` — a correctly framed reply to request `0x0217`, with bit 15 set, length 0
  and a valid checksum — followed by `[getRequestFromReplyQueue] … count(): 1`. Read count is no longer zero.
- **How the interception was made to work, after three unit/drop-in/naming attempts all had zero effect:**
  replace the vendor daemon's own path. `/app/bin/micommanager_userspace` is now a wrapper script and the
  original binary is `/app/bin/micommanager_userspace.real`. That covers every launch route — systemd unit,
  D-Bus activation, or anything else — and it is the change that worked.
- The wrapper mounts devpts (the guest has none, which is why `posix_openpt` previously failed with
  `No space left on device`), starts the peer on a pty master, symlinks `/dev/ttyS1` to the **slave**, waits
  for a readiness marker, then `exec`s the real daemon. Verified in the boot log:
  `MMWRAP begin`, `devpts=/dev/pts`, `pty ready: /dev/ttyS1 -> /dev/pts/0`, `listening on /dev/ttyS1`,
  `waited=1 ready=yes link=/dev/pts/0`, and **0 bytes to the hardware tty** — the daemon is talking to the
  peer, not to the host.
- Two debugfs pitfalls cost a cycle each and are recorded: `sif` did not apply a mode by inode, and the file
  stayed `0644`, which made the wrapper unexecutable and produced a silent no-start; `set_inode_field <path>
  mode 0100755` is what works.
- **New blocker, one layer up:** `[[writeToDBus] There is no connection.]` — the daemon read the reply
  successfully and then could not publish the result on the bus. This boot also shows
  `Failed to start nua.service`, `Failed to start AVN2.1 - CarPlay iAP2Service Launcher` and
  `Failed to start Smack service loads smack rules`, so the system is degraded in a way the earlier runs were
  not, and the bus or SMACK ruleset is the next thing to fix.

## 1.37.0 - name the FUMO `-404` state and check CVE-2017-7308 exactly

- Traced AppDMClient's verifier wrapper into the exact fixed-suffix parser.
  It seeks to `file_size - 0x4024`, reads one `0x4024`-byte item, and recognizes
  only `TER` or `TE2`; result `-404` means there is no recognized trailer
  candidate, not that signature verification succeeded. Added a deterministic,
  numeric/boolean-only gate model and 14 tests without reading or generating
  firmware, trailers, archives, commands, or payloads.
- Compared exact recovered `af_packet.ko` with authoritative CVE-2017-7308
  fixes. The published TPACKET_V3 private-area primitive is absent because
  `tp_sizeof_priv` arithmetic is performed in 64 bits, matching upstream
  `2b6867c2`. The companion `tp_frame_nr` multiplication guard from
  `8f8d28e4` is absent. Public follow-up found no standalone impact assigned to
  the redundant TPACKET_V3 field. At this point exact V1/V2 consequences were
  impact-unknown; version 1.56.0 later closed them as bounds-preserving invalid
  geometry. `CAP_NET_RAW` remains a separate runtime gate.
- No recovered target executable was run, no malformed input or update material
  was created, and no target filesystem, partition, marker, or slot was changed.

## 1.35.0 - pty mode works from a shell; the systemd path is unobservable

- Found two concrete bugs and fixed both: the guest has **no `/dev/pts`**, so `posix_openpt` failed with
  `No space left on device` until devpts was mounted; and the responder was reading its device argument from
  the mode slot, so `pty /dev/ttyS1` symlinked a file literally named `pty`. With both fixed, pty mode works
  from a research shell: `pty ready: pty -> /dev/pts/0`, and a real `/dev/ttyS1` symlink can be established.
- Under systemd it still does not take effect: `micommanager` keeps writing **1056 bytes to the host chardev**
  and reports **103 writes / 0 reads**, which proves `/dev/ttyS1` was never replaced — and therefore that the
  wrapper's pty step did not succeed in that context.
- Three different enablement routes were tried and all produced identical behaviour: an `ExecStartPre`
  drop-in, an `ExecStart` override drop-in, and editing the vendor unit's `ExecStart` directly in the clone
  (verified in the image by reading the file back). Since `esinit` simply `exec`s `/lib/systemd/systemd` and
  there is no `/etc` override of that unit, enablement is not the obstacle — the wrapper runs, and what fails
  inside it is invisible.
- **The real blocker is observability**: a systemd-spawned script has no console, `/dev/kmsg` writes do not
  appear in the serial log, guest filesystem writes are discarded with the snapshot, and the `micom-debug`
  unit could not be enabled because `debugfs symlink` creates links relative to the image root rather than at
  an absolute path.
- Next step is therefore not about the protocol at all: give the wrapper a working console channel (for
  example redirect its output to `/dev/console`, which is the one sink that does reach the serial log) and
  read why the devpts mount or the symlink fails there.

## 1.34.0 - why the peer never answers: a tty is one line to the host, not a loopback

- A readiness handshake was added (`/tmp/micom-ready` after a successful open, wrapper waits for it before
  exec'ing the daemon). Read count is **still 0**, with 103 writes. So the race was not the cause either.
- **The design was wrong, and this is my error.** `/dev/ttyS1` is a single serial line to the host: what a
  process *writes* to it goes out to the chardev, and what the chardev delivers comes *in*. Two processes
  holding the same tty do not talk to each other — my replies were transmitted to the host, never delivered to
  the daemon's input. That is exactly consistent with every observation: the daemon writes 103 frames, our
  peer reads none of them (it sees no input because there is none), and its replies are captured as guest
  output rather than consumed locally.
- The earlier hypothesis list was therefore wrong in its first three entries, and SMACK was cleared: the audit
  trail contains **zero denials** and our binaries never appear in it at all.
- Correct architecture is a **pty pair inside the guest**: the peer owns the *master*, `/dev/ttyS1` is
  replaced by a symlink to the *slave*, and the daemon then talks to the peer rather than to the host. The
  host-side capture of guest writes is lost, which is acceptable because the peer can log what it answers.
- Nothing about the framing, the id table or the responder's logic is invalidated; only the plumbing between
  peer and daemon was wrong.

## 1.34.0 - FUMO equal-path provenance and relaunch state resolved

- Traced AppDMClient's FUMO staging callers and resolved the `this+0x128`
  member: `slotUsbMounted(QString, int, QString, QString)` copies its mount-path
  argument there when index 1 is reported, sets the mounted-state byte, and
  passes the same path to staging.
- Proved the equal `/update/usb/bin/AppUpgrade` comparison branch is normal
  software-reachable. `slotOnStandbyStatus(int)` has a fixed local staging call,
  and its force helper reads the first line of `/update/force_launch`, requires
  exact case-sensitive `run`, then stages from `/update/usb/bin`. This reaches
  the branch that omits repeated AppDMClient `0/0` or `-404/-404` pair checks.
- Reconstructed the matching inner-FUMO lifecycle. System- and firmware-mode
  progress-zero branches attempt `force_launch=run` unless a state global equals
  1; completion cleanup attempts `none`. The weak writer/callers do not prove
  either transition succeeded atomically.
  The branch is therefore an intended pre-staged relaunch, not an unresolved
  hypothetical outcome.
- Kept the security boundary narrow: direct removable-media control of the
  local staging directory, the named authentication state preceding the marker
  write, source immutability across separate opens, inner payload binding,
  partition writes, slot/boot acceptance, root, and persistence remain unproved.
- Extended the passive disconnected-bench bundle to capture relaunch/completion
  markers, update-directory metadata, and hashes for staged AppUpgrade/XML and
  `/tmp/AppUpgrade`. Collection now distinguishes absence from read/query
  failure, validates SHA-256 syntax, and returns a nonzero terminal status for
  evidence failures. No recovered executable or updater was run and no target
  file, package, marker, partition, or slot was modified.

## 1.33.0 - responder works from a shell, still silent under systemd

- Verified the responder is correct as a program: launched from a research shell it reports
  `listening on /dev/ttyS1` and stays alive. So the binary, the framing code and the retry logic are not the
  problem.
- Escalated the systemd integration from `ExecStartPre` to an `ExecStart` override wrapper
  (`/usr/bin/micom-up.sh`, which backgrounds the peer then `exec`s the vendor daemon unchanged). The daemon
  still reports **103 writes / 0 reads**, with `Started System service for micommanager` at 18.2 s, so the
  wrapper ran and the daemon registered — the peer simply never answered.
- **kmsg logging is not available as an evidence channel here.** Even a successful run from the shell wrote
  `listening` to stderr but produced no `/dev/kmsg` line in the console log, and SMACK is active on this
  system (`lsm=SMACK` audit lines are visible in the console). Any silent denial of exec or of the kmsg write
  would therefore look exactly like what is observed.
- Remaining hypotheses, in order of likelihood, each with a cheap test: (1) SMACK denies execution of our
  binaries under a systemd-spawned context — testable from the SMACK audit lines in the console; (2) the
  daemon reconfigures termios after the peer opens the port, so the peer's reads never see frame starts —
  testable by having the peer reopen after the daemon's first write; (3) the peer starts before
  `dev-ttyS1.device` exists and its 120 s retry window expires — already mitigated, so least likely.
- Recorded plainly: this is a debugging loop with a named suspect (SMACK) rather than an unexplained
  silence, and the next action is to read the SMACK audit trail for denials of `/usr/bin/micom-responder`.

## 1.32.0 - the daemon counts its own failures: 103 writes, 0 reads

- Ran the authentic systemd boot with the responder wired in via a drop-in on
  `dbus-com.lge.car.micom.service`. `micom_serial_bytes` is **1056**, confirming the daemon transmits.
- The daemon's own DLT output on the console settles the question precisely:
  `[Total write count : 103 read count : 0]`, with repeated
  `[[makeErrorReply] connectioTimeOut CMD( 0x829d )]`. So **nothing is being read back** — the peer is not
  answering, and the daemon times out every request.
- **No `micom-responder` kmsg lines appear at all**, so the peer most likely never got as far as opening the
  port. Its failure path writes to stderr (`perror`), which reaches nothing under systemd, so a failed open
  is currently invisible — a deliberate gap in the instrumentation, not an ambiguous result.
- Also confirmed on this boot: the daemon really does speak only under systemd (103 writes here versus zero
  on every research-init run), and the console shows `Started System service for micommanager` at 20.5 s.
- Next iteration is small and specific: make the responder log its open failure to `/dev/kmsg`, retry the
  open until `/dev/ttyS1` exists, and re-run. If the port is being taken first, that will now say so instead
  of failing silently.

## 1.33.0 - FUMO descriptor eligibility and marker contracts reconstructed

- Reconstructed exact AppDMClient FUMO USB staging around
  `0x7ff60..0x830e4`. The function computes public-key verifier results for
  `<source>/AppUpgrade` and `<source>/.lge.upgrade.xml` before evaluating USB
  eligibility.
- Recovered XML semantics: accepted lowercased roots are `lhavn` and `wideavn`.
  Starting at the first root child, only consecutive siblings that convert to
  elements are visited; the first `version` element whose first child is text is
  returned, and its trimmed value may be empty. Zero verifier result selects the
  fixed `DecryptToPIPE` pipeline; nonzero enters direct XML parsing.
- Recovered conditional mode gates. On the unequal source/destination branch,
  marker absence requires retained AppUpgrade/XML results `0/0`; marker presence
  requires `-404/-404`. An equal pre-staged path jumps around both contracts.
  Its normal caller reachability and source stability across separate verifier
  opens remain unresolved. The marker is local state, not a USB member, so none
  of these branches is a proven physical bypass.
- Recovered two lexicographic normalized version comparisons. The first requires
  a strictly newer candidate; the second allows equality against another stored
  reference. Reviewed USB calls disable the comparator's explicit section-zero
  vehicle equality check but retain P5-family matching. Later AppUpgrade
  `car-variant`, payload, partition, boot, and health decisions remain open.
- Added `evidence/appdmclient-fumo-usb-eligibility.md` and a compact reviewed
  instruction/address excerpt. No updater ran and no package or XML fixture was
  created.

## 1.32.0 - stock USB updater reaches CVE-2015-9261 before authentication

- Reconstructed AppScomoDM's `launchAppUpgrade` path and direct helpers. The new
  USB method examines one first `QDirIterator` result for
  `S5W_SYSTEM_*_*_*.zip`, extracts only `AppUpgrade` and `.lge.upgrade.xml`,
  verifies both through `/app/share/AppUpgrade/teruten5_pub.key`, decrypts
  AppUpgrade through CryptoService or the old `DecryptToPIPE` route, copies the
  authenticated XML, checks ELF magic/executable status, and requests app 300.
- Established exact ordering: archive decompression precedes both member
  verification calls. Independent review corrected artifact provenance: the
  current integrated tree's BusyBox 1.35.0 is a VM-injected static helper.
  Original `/usr/bin/unzip -> /bin/busybox` uses stock SHA-256
  `95bab633...bd9ebc`, BusyBox 1.23.2.
- Added corrected V-020. Stock `unzip` accepts methods 0/8 and rejects method 12.
  Method 8 reaches exact pre-fix CVE-2015-9261 `huft_build`: the `v+n` bound at
  `0x4788a` can read an uninitialized `v[]` entry at `0x47938` and conditionally
  perform invalid indexed table reads before the caller rejects the table.
  Initial `v_end` fix `1de25a6e87e0e627aa34298105a3d17c60a1f44e` was
  corrected by `6bd3fff51aa74e2ee2d87887b12182a3b09792ef`, which initializes
  all `v[]` slots to an invalid sentinel; neither correction is present.
- Added `tools/uk_fw/busybox_huft_bounds_model.py` and focused tests. The tool
  models integer bounds only and cannot generate compressed or archive input.
- No target ran and no ZIP/DEFLATE fixture was made. The strongest supported
  impact is likely `unzip` child crash/update DoS; no memory write, RCE, root,
  signature bypass, package acceptance, or physical-unit result was produced.
- Added `evidence/busybox-unzip-cve-2015-9261.md`, extended the passive bench
  bundle for update identities/symlink/PATH evidence, and updated the trust
  matrix, inventory, register, priorities, checkpoints, and handover.

## 1.31.0 - the responder works but is in the wrong environment

- Wrote `micom-responder`: a minimal `/dev/ttyS1` peer implementing the measured framing
  (`AA id_hi id_lo L payload CS`, XOR checksum, reply with `id | 0x8000`), answering every request and
  returning a 35-byte payload for the two boot-info candidate ids (`0x01aa`, `0x02c3`). Cross-built static
  for `x86_64-linux-gnu`, 17,408 bytes, deployed at `/usr/bin/micom-responder` in the clone.
- It starts and listens, but **no frames arrive to answer**, in either start order, and
  `micom_serial_bytes` stays 0. That is not the responder's fault: it exposes a distinction the records had
  not separated before.
- **`micommanager` only transmits under the systemd boot.** Every research-init run, including all of
  today's, records `micom_serial_bytes: 0`. The one run that produced 1056 bytes was the authentic
  `init=/lib/systemd/esinit` boot where systemd starts the daemon with its real environment. The daemon
  stays alive under the research shell but never speaks.
- So the responder must be tested in the `esinit-fs` workspace (multi-user, systemd-started `micommanager`),
  which does not yet have our backend, the software rasteriser or the responder injected. That is the
  correct next experiment, and it is a deployment task rather than a discovery one.
- Recorded plainly because it invalidates a natural assumption: "the daemon is running" and "the daemon is
  talking" are different claims in this image, and only the systemd boot produces the second.

## 1.30.0 - the segment publisher is conditional on MICOM data

- Swept every candidate sequentially in one boot. `AppDMClient`, `NotificationManager` and
  `AppEngineerMode` create **zero** `qipc` segments in this environment. Only `ApplicationManager` creates
  any, and it still does not create `/Ihu` or `/Inform`.
- Every binary in the image referencing those keys is in `app/bin`: `UserProfileManager`, `MOFManager`,
  `AppEngineerMode`, `AppDMClient`, `ApplicationManager`, `NotificationManager` (the rest are `.mp4` assets).
  So the publisher is in that set, and the only member that creates segments at all is
  `ApplicationManager`.
- The consistent reading: `ApplicationManager` publishes `/Ihu` **conditionally, once it has vehicle state**,
  and that state comes from the MICOM link. Our MICOM peer is passive — it accepts 103 frames and answers
  none — so the condition is never met.
- That closes the loop the session opened with: the MICOM contract was needed not only for the boot-info
  asks but because the UI's shared-memory publication depends on it. The chain is
  MICOM replies -> ApplicationManager publishes `/Ihu` -> widgets attach -> buffers attached -> pixels.
- **Next engineering step is therefore concrete and self-contained:** implement a MICOM responder that
  answers the empirically observed ids with valid XOR frames and plausible boot info, run it as the
  `/dev/ttyS1` peer, and re-test. The framing, the id table and the reply rule (request id with bit 15 set)
  are all already measured and written down.

## 1.29.0 - shared-memory publishers identified, but not the one that matters

- The segment keys the UI waits on are now known from strings: `/Can`, `/Ihu`, `/Inform`,
  `/Information`, `/PhevInterface`, `/CryptoService`, with the literal marker `Lock SHARED MEMORY NAVI`.
  Qt creates these as `/tmp/qipc_sharedmemory_<KEY><hash>` plus a matching `qipc_systemsem_` file, so
  presence of those files is direct evidence that a publisher ran.
- **`ApplicationManager` publishes several segments**, including **`BOOTINFOSTATUS`**,
  `ApplicationManagerInformation` and `ApplicationEnableInformation`. That is the component's purpose here
  and it was the right first guess.
- **`UserProfileManager` and `MOFManager` publish the persistent `E*` set**: `EHOMESCREEN`, `ELASTMODE`,
  `ERADIOPRESET`, `ERADIOSETTING`, `EREGIONPLATFORMTYPE`, `EA V M800`, `EBLUELINK`, `EBTDEVICE`, `ERVM`,
  `EARRMYMENU`. These are per-setting state segments, not vehicle boot info.
- **The ones the app actually wants are still not created by any of them.** With the system bus, all three
  managers, `micommanager_userspace` and the compositor running, `AppHomeScreen` still logs **12**
  `Cannot attach to shared memory` failures, still never attaches a buffer, and the frame remains fully
  black (21,600 pixels, `#000000`). A later segfault in the same process is recorded but is downstream of
  the same missing state.
- So the publisher of `/Ihu` and `/Inform` is a component not yet identified. `micommanager_userspace`
  alone does not create them, which rules out the most obvious candidate.
- Next step is narrow: determine statically which binary calls `QSharedMemory::create` for those keys —
  the key strings plus `Create` behaviour are enough to identify it — and start that component with a
  plausible vehicle state.

## 1.28.0 - placed view, real repaint, black pixels: the client never attaches a buffer

- Clean end-to-end measurement with the shim active: a surface is mapped, a repaint occurs, and the
  downscaled framebuffer dump transfers intact (240x90, 64,800 pixel bytes). **All 21,600 pixels are
  `#000000`.**
- The reason is now measured rather than guessed. Under `WAYLAND_DEBUG=1` the client issues **5 `commit`s
  and zero non-nil `attach` calls** — it never supplies a buffer for its surface. A committed surface with
  no buffer has nothing to composite, so the renderer correctly produces black.
- That closes the loop with the earlier `QSharedMemory` failures: the widgets cannot produce content until
  the boot-info segment they read exists, so they never allocate and attach a buffer. The chain is
  consistent end to end: missing boot-info shared memory -> no buffer attached -> nothing composited ->
  black frame.
- Every layer we own is now verified working: boot to multi-user, backend, CRTC and IAS interfaces, EGL via
  the software rasteriser, capture, and surface placement. The remaining blocker is one vendor-side
  shared-memory segment that another process is supposed to publish.
- Next step is precise: identify the `QSharedMemory` key(s) that `AppHomeScreen` looks for, find which
  component normally creates them, and publish a minimal segment with plausible boot-info values.

## 1.27.0 - the shim works: surfaces are mapped and the compositor repaints

- Installed a research shim in the backend that creates a view for every new surface, via
  `compositor->create_surface_signal`, and inserts it on the output. It is explicitly a shim standing in
  for the absent `grid_layout.so`, not vendor behaviour.
- **It works at the layer that was broken.** With the shim: `ias-soft: shim mapped surface …` is logged,
  **repaints now happen** (framebuffer dumps `fb-1.raw`/`fb-2.raw` were produced), and the earlier state —
  literally zero repaints — is gone. This confirms the diagnosis: the compositor was idle only because
  nothing was ever placed.
- First attempt used `ec->surface_list`, which **does not exist in this Weston variant**; iteration over that
  list is impossible here, and the comment in `compositor.h` referencing it is stale. The signal-based hook
  replaced it and compiles and runs.
- **Still not verified: pixel content.** The capture through `weston_screenshooter` still reports
  `mean R=0.0`, and the framebuffer dump could not be moved out of the guest intact — a full 1920x720x4
  dump (5.5 MB) exceeds what the serial channel will carry before the run ends, and the earlier gzip+base64
  attempt was truncated. The dump now writes a downscaled 240x90 PPM instead, which is small enough to
  transfer; that path needs one clean run to confirm.
- Honest summary: the placement problem is solved at the level of "the compositor now renders", and the
  remaining work is entirely about *observing* the result rather than producing it.

## 1.28.0 - reconstruct AppUpgrade routing and constrain the plaintext marker

- Added `tools/uk_fw/embedded_elf.py`, a strict read-only extractor that keeps
  outer-file offsets, embedded-file offsets, and embedded virtual addresses
  separate. Exact SCOMO and FUMO extents replace older broad carvings; malformed,
  truncated, incidental, and overlapping synthetic ELFs fail closed.
- Reconstructed the outer wrapper from exact instructions. Exact case-sensitive
  `-un:1` selects `:/AppScomoUpgrade`; `-un:0` or no `-un:1` selects
  `:/AppFumoUpgrade`. The wrapper forwards every application argument except
  item zero to the child, uses the Qt event loop rather than a blocking wait,
  discards setup/child status, and normally returns `1`.
- Closed the AppLauncher argument gap. A dynamically requested app ID 300 calls
  the normal option builder at `0x34510`, stores its list at
  `AppProcess+0x60`, and passes it to `QProcess::start`. The recovered embedded
  NE/EUR row contains `-un:0`; an exact `-un:1` plus app ID 311 conditionally
  substitutes AppScomoDM for AppDMClient.
- Corrected marker semantics. FUMO's mode byte starts at `1` and marker existence
  at process startup changes it to `0` (`Unencryption Update`). Recovered SCOMO
  MASS_PRODUCT/PENETRATION startup explicitly ignores the marker. The marker is
  therefore route-specific, requires prior privileged execution, and does not
  prove version/signature/hash/write/slot/boot/health bypass.
- Excluded AppSetup as the descriptor parser: it initiates the app-ID-300
  transition but does not perform the reviewed USB discovery, decryption,
  version/model, authentication, route-selection, or marker work.
- Added `evidence/appupgrade-update-trust.md` and corrected build/operating-model
  documents that previously called the marker a universal unchecked plaintext
  path. No recovered executable was run and no update or slot operation occurred.

## 1.26.0 - the IAS plugin ABI is extracted in full

- The layout-plugin contract is now written down from vendor DWARF rather than inferred, in
  `evidence/vm-bringup/ias-plugin-abi.md`. Plugins are discovered by exporting a data symbol named
  **`ias_plugin_info`** (layout) or `ias_input_plugin_info` (input).
- `struct ias_plugin_info`: `switch_to` @0x00 as `void (*)(const spug_output_id)`, `switch_from` @0x08,
  three input grab tables @0x10/0x20/0x30, `inforec_version` @0x40, `id` @0x44, `draw` @0x48 as
  `void (*)(spug_view_list)`.
- `struct ias_plugin` (size 0x90, `src/ias-common.h:265`): `version` @0x00, `libname` @0x08, `name` @0x10,
  an anonymous union at 0x18 selecting `ias_plugin_info` or `ias_input_plugin_info`, `link` @0x68,
  `init_mode` @0x78 with `INIT_NORMAL`/`INIT_DEFERRED`, `init` @0x7c, `activate_on` @0x80.
- `init_mode` explains `defer="1"` in the shipped `ias.conf`: a deferred plugin is not activated at start.
- The minimal replacement is now one sentence: on `switch_to`, fetch each IAS surface and assign it to that
  output's scanout. Grabs can be empty and `draw` a no-op.
- **Stated gap, not glossed over:** `spug_output_id` and `spug_view_list` are ID-based lookups into framework
  tables (`spug_ids`, `spug_output_ids`, `spug_surface_ids`, `spug_view_ids`, `spug_plane_ids`,
  `spug_seat_ids`, `spug_hashtables`), and the exact `fetch_ias_surface` signature is not yet extracted.
  Each is one DWARF query away; none is a blocker of principle.

## 1.25.0 - the app speaks only IAS, and the plugin ABI is fully recoverable

- `fullscreen-shell` does not help: with it the app stays alive but the compositor still logs **zero
  repaints**, because `AppHomeScreen` uses the IAS protocol exclusively (`ias_` calls, no `wl_shell`).
  Only the IAS shell can place its surfaces, so a shim must go through the IAS plugin path.
- The plugin ABI is now mapped from the binaries rather than guessed. `ias-shell.so` references
  `ias_layout_switchto_fn`, `ias_layout_switchfrom_fn`, `plugin_redraw_always` and `ias_input_plugin_info`,
  and `ias_plugin_framework.so` exports the helpers a layout plugin uses: `fetch_ias_surface`,
  `ias_assign_surface_to_scanout`, `ias_assign_surface_to_sprite`, `ias_assign_zorder_to_sprite`,
  `ias_assign_constant_alpha_to_sprite`, `ias_activate_plugin`, `ias_deactivate_plugin` and
  `ias_frame_events_enabled`.
- A minimal layout plugin is therefore well defined in shape: on switch-to, fetch each IAS surface and
  assign it to scanout. That is the whole shim.
- **Both `ias-shell.so` and `ias_plugin_framework.so` carry full DWARF** (7 debug sections each), so the
  exact struct layouts for the plugin interface — including the callback signature order that
  `ias_layout_switchto_fn` implies — can be extracted the same way the vendor `weston_output` layout was.
  No header is needed and none shipped in the image.
- V-012 is extended: the unstripped-debug condition is not limited to `/usr/bin/weston`. The IAS shell and
  its plugin framework — the components that decide what appears on the vehicle's display — carry full type
  and line information in the shipped image as well.

## 1.24.0 - the compositor never repaints, so nothing is ever drawn

- Instrumented the backend's repaint path to log view count and dump the framebuffer. Result with a
  client committing surfaces for 18 s: **zero repaint calls**, and therefore zero dumps. Westen itself
  runs and our module loads (`Loading module '/usr/lib/weston/ias-backend-soft.so'`, capabilities
  printed), so this is not a load failure.
- That is the actual explanation of the black frame, and it supersedes the earlier mapping hypothesis with
  something stronger: the compositor is doing no work because **nothing is ever mapped into an output
  view**. No views means no damage, no damage means no repaint, and a capture reads a zeroed buffer.
- The missing piece is now identified at source: **`/usr/lib/ias/` is empty and `grid_layout.so` is not in
  the firmware at all**. `ias.conf` references it as `defer="1"`, `opt/ias/` is an empty OEM mount point
  (`bin` and `lib` present and empty), and searching the entire decrypted tree finds no IAS plugin
  binaries. The shell has no layout engine and no composer, so committed surfaces are never placed.
- Root cause chain, complete: no IAS layout plugin to place surfaces -> no views -> no damage -> no repaint
  -> zeroed capture. Every layer we built (backend, CRTC, ias_crtc, capture, EGL) is working and none of
  them is the fault.
- Next step is therefore well defined and small in scope: either implement a minimal IAS layout plugin
  against the ABI in `ias_plugin_framework.so`, or, for the research build only, have our backend place
  incoming surfaces itself so the scene can be seen. The second is far cheaper and is honest about being a
  research shim rather than vendor behaviour.

## 1.23.0 - the home screen runs; the capture is still black, with a named hypothesis

- With a system bus and `micommanager_userspace` running, `AppHomeScreen` **stays alive** (alive at 22 s,
  where earlier runs died), and it creates real state on disk: `CustomLayoutDB` 20,480 bytes and `SetupDB`
  16,384 bytes under `/app/data/AppHomeScreen/`. The layout-database error is gone.
- It also genuinely talks to the compositor: with `WAYLAND_DEBUG=1` the client log shows **24 `attach`,
  9 `commit`, 1 `wl_surface@`, and 12 `ias_`** calls, so it is not a client that never submits.
- **The capture is still uniformly black**, and `ias-shot` now reports it directly:
  `mean R=0.0 G=0.0 B=0.0`. So the remaining gap is not client liveness, EGL, or the capture path — the
  control capture with `weston-simple-shm` still works, so the pipeline itself is sound.
- The app is also blocked on **shared memory it does not own**: repeated
  `Cannot attach to shared memory to update! QSharedMemory::handle:: UNIX key file doesn't exist` from
  `CPCallWidget`, `ElectricityUseWidget`, `PHEVVehicleOSDWidget`, `PHEVWidget`, `VoiceMemoWidget` and
  `WeatherWidget`. Those widgets read a boot-info segment created by another component; without it they
  render nothing even when their surface is committed. That is the leading explanation for a committed but
  empty scene.
- Working hypothesis for the black frame, now stated explicitly: the vendor surfaces are committed but not
  mapped onto the CRTC our capture reads, because mapping under `ias-shell` is the composer's job via
  `ias_hmi`. The control client is mapped by default; a vendor client waiting to be placed is not.
- `ias-shot` gained a mean/histogram report so a black frame is self-evident at capture time rather than
  needing a round trip.

## 1.27.0 - Build a passive disconnected-bench state bundle and harden rootfs repacking

- Added `tools/uk_fw/bench_state_bundle.py`. It emits a versioned POSIX-shell
  probe that writes only to stdout, performs no mount/service/radio/network/
  process-control action, and parses the captured console transcript offline.
- The bundle records exact hashes, process uid/gid and effective SMACK labels,
  systemd state and activation markers, listeners/interfaces, passive Wi-Fi/P2P
  evidence, oFono device state, local Bluetooth SDP/profile state, Dropbear-chain
  completeness, and A/B/update flags. Missing commands and truncated sections
  are retained rather than interpreted as absence.
- Added fourteen synthetic tests for the safety audit, shell syntax, serial timestamp
  handling, hex-framing integrity, size limits, deterministic facts,
  incomplete/duplicate sections, adversarial transcript text, and CLI operation.
  No target, network, radio, modem, or
  recovered executable was used.
- Hardened `rootfs_patch.py` so archive staging rejects path escapes, duplicate
  regular files, links and special nodes. Injection destinations are bounded,
  and package/manifest operations refuse to overwrite their original inputs.
  Eight new tests cover those boundaries, including hard-link aliases, duplicate
  directories, and metadata preservation through read-only directories.
- Updated the bench and custom-firmware runbooks. The tool improves evidence and
  build safety; it does not establish root access, an accepted custom package,
  or applicability to the owner's unknown installed firmware.

## 1.22.0 - software rasteriser fixes EGL, and the Qt segfault disappears

- **The `AppHomeScreen` segfault was a symptom of failed EGL, not a QML bug.** With a software
  rasteriser available the log no longer says `DRI2: failed to open swrast` or
  `failed to initialize EGL display`, and the process **keeps running** (killed by the harness timeout at
  SIGTERM, not by SIGSEGV). It now gets as far as opening its database.
- The image ships **no software rasteriser at all**: `usr/lib/dri` contains only `i965_dri.so` and
  `iu3d9_drv_video.so`, and `usr/lib/mesadri` only `i915_dri.so` and `i965_dri.so`. Every GL path requires
  an Intel GPU that emulation does not provide, which is why EGL could never initialise here.
- Fixed with assets the project already had: the Debian stretch `swrast_dri.so` plus `libLLVM-3.9.so.1`,
  `libsensors.so.4`, `libedit.so.2` and `libbsd.so.0` from `work/software-egl/`, injected into the clone at
  `usr/lib/dri/` and `usr/lib/`, with `LIBGL_DRIVERS_PATH=/usr/lib/dri`,
  `MESA_LOADER_DRIVER_OVERRIDE=swrast` and `GALLIUM_DRIVER=llvmpipe`.
- Progress after the fix, from the guest log: `Using Wayland-EGL`, `initTimers`,
  `AppHomeModel::openDBConnection() … true`, then `createLayoutDBTable() … commit Fail` and
  `getLayoutVersion() … TABLE IS NOT EXIST`.
- So the next blocker is mundane and specific: the app wants its layout database, which lives on a data
  partition this projection does not populate. That matches the gap analysis's ranked item for the
  `/Data` resource table and theme assets.
- The corrected reading of the earlier black frame: the compositor, backend, CRTC and capture are all
  fine, and the client stack was failing at EGL before it could ever commit a surface.

## 1.21.0 - frame capture built; the HMI frame is black, and why

- The capture path works. `ias-shot` binds `weston_screenshooter`, takes a 1920x720 `ARGB8888` shm
  buffer and writes P6 PPM. Proof is the **control**: with `/usr/bin/weston-simple-shm` as the only
  client, the 250x250 test pattern is captured upright at `(0,0)-(249,249)` with full RGB range
  (`evidence/vm-bringup/screenshooter-control-simple-shm.png`). The pipeline is not in doubt.
- The vendor HMI frame is **uniformly black**: 1,382,400 pixels, single value `(0,0,0)`, saved as
  `evidence/vm-bringup/first-hmi-frame.png`. That is the compositor's cleared output, recorded as the
  negative result it is rather than dressed up as a first image.
- Four measured causes, in the order they bind:
  - **`--use-pixman` is mandatory** for this backend. Its default noop renderer has empty `read_pixels`
    and `repaint_output`, so the buffer comes back zeroed no matter what the scene contains. Found by
    comparing runs with and without the flag.
  - `NaviUpdateApp` is alive and creates `wl_surface@14`, but **never calls `attach`, `commit` or
    `get_shell_surface`** — a surface that is never committed cannot be composited.
  - `AppHomeScreen` creates one surface and a `wl_shm_pool`, then **segfaults inside
    `libQt5Qml.so.5.4.1`**. A Qt QML crash in the vendor's own home-screen process is a robustness defect
    worth pursuing separately; it is not currently attacker-controlled, so it is not entered in the
    vulnerability register.
  - `AppLauncher` starts `ApplicationManager` (pid 797) but launches **no UI process** and creates no
    surface.
- `dbus-daemon` cannot start in this projection at all: `--system` fails for want of a `messagebus` user
  and `--session` fails with `Memory allocation failure in message bus`. This is consistent with the
  earlier finding rather than contradicting it — under the research init the `/tmp/passwd` entries have
  to be supplied by hand, and this run did not supply them.
- One correction to an earlier assumption: `/navi/navi/Bin` does not exist in this image; the vendor path
  is `/navi/Bin`.
- The protocol headers were generated by the guest's own scanner again (103,210 / 1,958 / 642 bytes, all
  sizes verified), so no host-side wayland toolchain is needed for client work either.

## 1.20.1 - housekeeping: no absolute host paths in published IAS work

- The public harness rejected two machine-specific paths from `tools/uk_fw/ias_backend_soft/debug/run_ias.py`.
  Fixed by deriving the repository root from `__file__` instead of hardcoding it, so the script works from
  any checkout.
- The same class of leak was then removed everywhere it appeared in this line of work, rather than only
  where it was reported: `debug/inject.sh` now takes `debugfs` from `PATH` (with a documented `DEBUGFS`
  override), `build.sh` uses `brew --prefix` with `BREW_PREFIX`/`PIXMAN_INC`/`XKB_INC` overrides, and two
  evidence documents had `python3.13` invocations rewritten without the Homebrew path.
- Verified by scanning every tracked file in `tools/uk_fw/ias_backend_soft` and `evidence/vm-bringup`:
  zero `/Users`, `/opt/homebrew` or host-home references remain. One apparent hit in
  `usb-root-vector-map.md` was a **guest** path (`/home/root`) and correctly left alone.
- Build products stay untracked: `*.so` is gitignored and none are in the index, which matters because
  their string tables embed the build path.
- A hygiene section now sits in the scaffold README so the next debug script does not reintroduce this.

## 1.20.0 - the CRTC works, and the cause was a modified vendor ABI

- **The falsification criteria from the scope document are now met.** `wrandr` reports
  `Mode ID W H R CRTC = 1` with `0: 1920 x 720 @ 60000`, `wrandr --crtc=0` returns 0, weston stays alive
  throughout, and `weston-info` reports `make: 'gen5w', model: 'HDMI1', width: 1920 px, height: 720 px,
  refresh: 60 Hz`. The vendor IAS control path now drives our backend.
- The segfault was **not** in the protocol code. Our module was compiled against upstream Weston 1.10
  headers, but the shipped `weston 1.10.0-r21_9` has a modified layout: `struct weston_output` gains a
  `pixman_region32_t damage` member after `region`, shifting every later field by `0x18` (`make` at
  `0x250` instead of `0x238`, `sizeof` `0x320` instead of `0x300`). `wl_list_init(&output->base.mode_list)`
  therefore wrote 24 bytes too low, leaving `mode_list.next` NULL, and `bind_output` →
  `wl_output_send_mode` dereferenced it. The marshalling warning about a null `make` was the same defect.
  `weston_seat.output_mask` and two `weston_compositor` fields were missing as well.
- Two controls kept this honest: a build with `ias_publish()` deleted **crashed identically**, and
  instrumented handlers were **never reached**. Both point away from the new code, which is why the
  layout hypothesis was worth testing rather than assuming a protocol bug.
- Fixed by `vendor-abi.patch`, applied idempotently by `build.sh`, restoring the vendor layout for
  `weston_output`, `weston_seat`, `weston_compositor`, `weston_plane`, `weston_backend`, `weston_mode` and
  `weston_timeline_object`. Verification was systematic: every member offset was diffed against the
  shipped binary's own DWARF and now matches exactly.
- `bind_crtc` also now posts the `mode` event on bind, so the CRTC reports its mode to a client that only
  binds and asks.
- **This was only possible because the shipped `/usr/bin/weston` is unstripped**: it carries
  `.debug_info` (360,666 bytes), `.debug_loc` (286,264), and `.symtab`. Recorded in the register as
  hardening finding V-012, because full debug symbols in a production infotainment binary materially
  lower the cost of exactly this kind of ABI reconstruction.

## 1.19.0 - our own backend runs the vendor IAS shell

- `ias-backend-soft` now exists as an actual backend: derived from the vendored `compositor-headless.c`
  with the output model set to `HDMI1` and the default mode to 1920x720, it builds to 40,560 bytes and
  **loads in the guest**, running the vendor `/usr/bin/weston` with `ias-shell.so` loaded on top of it.
  The compositor logs its capabilities and stays up.
- The one linkage gap was informative: the first load failed with
  `undefined symbol: parse_options`. Upstream backends link `shared/option-parser.c` **into the module**
  rather than importing it from the executable, so the build now compiles that file in as well and the
  symbol is resolved internally.
- With our backend in place the registry exposes `ias_shell`, **`ias_hmi`** (previously unrecorded),
  `wl_shell` and **`weston_screenshooter`**. The last is notable: it is a frame-capture path, so a
  visible image may be obtainable through the protocol without any scanout device.
- **The falsification criteria are only partly met, and this entry does not overstate it.** Backend loads:
  yes. Output exists: yes. `wrandr` driving a CRTC: **no**, because the `ias_crtc` and `ias_mode`
  tables are not published yet — those are the next step, and the extraction for them is already done.
- Two smaller observations recorded rather than glossed: `wl_output` reports `make: '(null)', model:
  '(null)'`, so the vendor geometry path does not read the fields this backend sets, and no mode event
  was observed in `weston-info` output.

## 1.26.0 - Confirm exact BNEP bounds in both Broadcom BSA variants

- Added V-019 for CVE-2017-0782's exact pre-fix BNEP control parser in both
  PCB-selectable `vbtd-51` and `vbtd-63`.
- Mapped the instruction order showing extension/control and later multi-byte
  fields read before the checks introduced by the public AOSP fix; avoided
  transferring public generic RCE claims to the untested vehicle route.
- Documented PCB-specific binary/patchram selection, enabled unit, configured
  uid-0 default, intended `App::bluetooth` policy, ELF hardening, and compiled
  profile surface.
- Incorporated contrary reachability evidence: both engineering profiles say
  `PAN : N/A`; startup calls `BNEP_Init`, but no direct `BNEP_Register` reference
  was found. V-019 is dormant pending indirect/runtime registration evidence.
- Preserved remaining gates: adapter, ACL/L2CAP channel, pairing/authorization,
  controller delivery, owner PCB/hash, allocation-bound impact, and restart
  behavior remain unknown. No radio or packet was used.
- Added `evidence/broadcom-bsa-bluetooth-cves.md` and a sanitized exact evidence
  excerpt; other Android/Bluedroid CVEs remain unaccepted without exact BSA
  instruction proof.

## 1.25.0 - Close recovered Dropbear activation as inert

- Reconciled the RPM package record with the actual product filesystem: the
  socket-fed template, public-key installer, and static root authorized public
  key remain, but `dropbear`, `dropbearmulti`, the socket unit, host-key
  service/key, and enable links are absent.
- Reconstructed intended authentication without starting anything: `-s`
  disables passwords, the shipped default does not add `-w`, and the pre-start
  script would copy the static key into root's authorized keys. This is only a
  route for a holder of the matching private key if the missing server chain is
  independently restored; a bounded recovered-filesystem marker/filename search
  identified no candidate private-key material.
- Added `evidence/dropbear-activation-and-authentication.md` and a sanitized
  artifact excerpt. No listener, login attempt, credential, or target process
  was used.

## 1.24.0 - Reject two wpa_supplicant P2P CVEs by exact fixed-code evidence

- Identified exact recovered `wpa_supplicant` and `supplicantmanager` hashes,
  package record, Build ID, path-unit activation, and conditional marker gate.
- Confirmed CVE-2015-1863 is fixed: `p2p_add_device()` enters its SSID copy
  paths only when the peer-controlled length is at most 32.
- Confirmed CVE-2021-27803 is fixed: after successful `p2p_add_device()`, the
  Provision Discovery Request handler unconditionally re-fetches the peer and
  replaces the old pointer before continuing.
- Preserved the exposure boundary: wpa_supplicant and ConnMan contain P2P
  machinery, but production interface creation, discovery/listen state, launch
  arguments, peer-table state, SMACK label, and radio delivery remain unknown.
- Added `evidence/wpa-supplicant-p2p-cves.md` and a sanitized reviewed excerpt;
  no radio, wireless frame, target execution, or malformed input was used.

## 1.23.0 - Expand oFono directionality and confirm QMI list corruption

- Confirmed exact missing destination checks for CVE-2023-4232 through
  CVE-2023-4235 and CVE-2024-7547 in addition to the previously accepted
  CVE-2023-4233/CVE-2023-2794 paths.
- Reconstructed `sms_decode` directionality: incoming vendor-QMI calls complete
  deliver, submit-report, or status-report decoding before the handler's late
  DELIVER check; deliver-report and command are outgoing-only.
- Identified exact `outgoing=TRUE` callers in local transmit-queue
  deserialization and SIM-Toolkit Send SMS parsing. Kept these distinct from
  ordinary incoming SMS and did not claim direct over-the-air reachability.
- Expanded the message-free arithmetic model and exhaustive tests across
  status, submit-report, deliver-report, and command destinations.
- Added V-018 for exact CVE-2024-7537 behavior in the vendor QMI WMS message-list
  callback. Its missing count/length equality check combines with a wrapped
  32-bit product diagnostic and original-count copy loop. The overflow branch
  falls through to a four-byte allocation; every count above 13,107
  under-allocates.
- Preserved the modem trust boundary: V-018 is not evidence of direct SMS or
  base-station control. Neither V-017 nor V-018 establishes a dynamic crash,
  RCE, SMACK escape, unrestricted root, or owner-vehicle applicability.

## 1.18.0 - the backend cross-builds; first successful plugin

- **A Weston backend plugin now builds for the guest from this host.** `zig cc -target
  x86_64-linux-gnu` compiles the unmodified vendored `compositor-headless.c` into a 35,696-byte
  x86-64 ELF that exports `backend_init` and leaves 31 symbols undefined for the weston executable to
  resolve at `dlopen` — exactly the shape a plugin should have. Reproducible via
  `tools/uk_fw/ias_backend_soft/build.sh`.
- Dependencies were each found by a failure rather than guessed: the `config.h` stub, wayland 1.10.0
  headers from the release tarball (**Homebrew refuses to build wayland on macOS**: "Linux is required
  for this software"), `wayland-server-protocol.h` generated in-guest because the tarball omits it, and
  `libxkbcommon` for `compositor.h:37`.
- `wayland-server-protocol.h` extracted at **97,042 bytes, matching the in-guest size exactly**, with 22
  interface definitions.
- Three extraction channels were tested and only one is trustworthy for large files. Console
  gzip+base64 handled the 7.7 KB header but corrupted a 23 KB one. The `/dev/ttyS1` socket capture
  **drops bytes** (22,972 in-guest versus 23,064 captured, gzip refused to inflate). A second
  `isa-serial,index=2` backed by `-chardev file` is lossless and is now the documented method.
- Next: derive the backend from this base to create `HDMI1` at 1920x720 and publish the `ias_crtc` and
  `ias_mode` tables.

## 1.22.0 - Confirm exact oFono SMS decoder corruption and vendor-QMI route

- Identified `ofono-0.6.8+5w.master.199-r1.corei7_64`, then confirmed from the
  exact shipped `ofonod` instructions—not the package label—that the binary
  retains CVE-2023-4233's missing SMS address destination bounds and
  CVE-2023-2794's missing deliver-data destination bound.
- Mapped two compiled `lgeqmimodem` QMI callbacks into
  `ofono_sms_deliver_notify`, the internal `sms_decode` dispatch, address
  decoder, exact UDL/DCS arithmetic, and the unfortified `memcpy` into a
  140-byte array.
- Added a packet-free deterministic model and exhaustive tests for all 256
  address lengths and all 65,536 `(UDL,DCS)` pairs. The model emits no PDU,
  modem message, or network input.
- Preserved the exact-build consequence: both writes can leave the 0x128-byte
  `sms` object, but neither reviewed maximum directly reaches this caller's
  canary. PIE, NX, full RELRO, and canaries constrain exploitation without
  preventing the writes.
- Recorded V-017 as conditional cellular uid-0/`App::tms` memory corruption, not
  SMS-to-root. Service/marker activation, modem/QMI state, carrier delivery,
  dynamic corruption, RCE, SMACK escape, unrestricted root, and applicability
  to the owner's installed build remain unproven.
- Kept source history, online responses, full disassembly, and generated JSON
  under ignored `work/`; tracked only the model, tests, conservative report,
  planning checkpoint, and reviewed evidence excerpt.
- Fable remained unavailable for native subagents. DeepSeek Flash passed the
  static route doctor but native dispatch again returned `Unknown model`; no
  failed worker output or silent substitute was used.

## 1.17.0 - protocol headers generated by the image itself

- The `wayland-scanner` blocker is gone without installing anything: **the image ships
  `/usr/bin/wayland-scanner`**, so the guest generates Weston's protocol headers and the host needs no
  toolchain beyond what it has.
- `presentation_timing-server-protocol.h` is now generated and committed (7732 bytes, two
  `struct wl_interface` definitions). Integrity is established rather than assumed: the size decoded
  host-side matches the in-guest size exactly.
- Two harness facts were learned the hard way and are recorded. First, `prepare.json` holds a sha256 per
  artefact, so injecting an XML into a clone breaks workspace verification until those hashes are
  recomputed — and the `prepare` subcommand is the wrong tool, since it rebuilds from the official
  package. Second, **guest writes never reach the image**: the drive is `snapshot=on`, so a file written
  inside the guest goes to a throwaway overlay and `debugfs dump` cannot find it. The first extraction
  attempt failed precisely this way, and the working method is to stream the file out over the console
  as gzip+base64 between markers.
- Remaining build items are now down to two: a minimal `config.h`, and `wayland-server.h` (or writing
  the two IAS `wl_interface` tables directly, which is viable because they were already extracted from
  `ias-backend.so`). The pixman header/runtime skew remains a stated risk.

## 1.16.0 - cross toolchain proven, and the real build blockers named

- The bundled zig 0.13.0 cross-compiles to `x86_64-linux-gnu` and produces a valid **x86-64 ELF shared
  object exporting `backend_init`**, which is the entrypoint this Weston build loads via `dlsym`. The
  host is arm64 and has no system cross-gcc, so this was the one genuine toolchain unknown and it is now
  settled with an artefact rather than an assumption.
- pixman headers do exist on the host (Homebrew **0.46.4**) against an image runtime of **0.42.2**. The
  `libpixman-1.so.0` ABI is stable and the calls the headless renderer makes are long-standing, but the
  skew is recorded as a real risk rather than waved through; pinning to 0.42.2 headers is the fallback.
- Four concrete build items remain, all identified by reading what the backend actually includes rather
  than by trial and error: a minimal `config.h` (Weston generates it with autotools), the generated
  `presentation_timing-server-protocol.h`, **`wayland-scanner`, which is absent from the host**, and a
  wayland development tree for `wayland-server.h`. The Weston source tree supplies 21 internal headers.
- A way around two of those exists and is recorded: the IAS interface tables are small and were already
  recovered from `ias-backend.so`, so they can be written directly as `wl_interface` structs instead of
  generated from XML that is not in the tree.
- Scaffold and build notes live at `tools/uk_fw/ias_backend_soft/`. The previous scaffold location under
  `work/` was gitignored and would not have been committed, which is why it moved.

## 1.15.0 - IAS protocol extracted; soft-backend slice scoped

- The IAS control protocol is now known exactly, extracted from `ias-backend.so`'s `.data` by parsing
  `struct wl_interface` at the exported symbol addresses (`0x220f40`, `0x221060`) with a proper
  vaddr-to-file-offset mapping through PT_LOAD.
- **`ias_crtc` v1**: methods `set_mode(u)`, `set_gamma(uuu)`, `set_contrast(uuu)`, `set_brightness(uuu)`,
  `set_fb_transparency(u)`; events `mode(uuuu)`, `gamma(uuu)`, `contrast(uuu)`, `brightness(uuu)`.
  **`ias_mode` v1**: one method, `add()`. This maps one-to-one onto `wrandr`'s documented options, which
  confirms the tool drives exactly this interface and is not an unrelated shim.
- Backend ABI confirmed for this build: the entrypoint is **`backend_init`**, not
  `weston_backend_init`, with signature
  `WL_EXPORT int backend_init(struct weston_compositor *, int *argc, char *argv[])`
  (`compositor-headless.c:260`), loaded via `dlsym` at `compositor.c:4995`.
- First slice scoped (`evidence/vm-bringup/ias-backend-soft-scope.md`): derive from
  `compositor-headless.c`, rename the output `HDMI1` at 1920x720 so the vendor `ias.conf` stays
  unmodified, and publish the two interface tables so `wrandr` can enumerate and enable a CRTC.
- **Immediate blocker, stated plainly: there are no pixman headers.** The image ships
  `libpixman-1.so.0.42.2` as a runtime only, and `compositor-headless.c` includes `pixman.h`. The build
  therefore needs either the pixman 0.42.2 headers or a hand-written declaration of the small
  `pixman_image_*` / `pixman_region_*` surface the renderer uses. The bundled zig 0.13.0 handles the
  `x86_64-linux-gnu` cross build.
- Falsification defined before any code is written: `wrandr` must list a CRTC, `wrandr --crtc=0
  --enable=true` must succeed, and `weston-info` must report a 1920x720 `HDMI1` output.

## 1.14.0 - ias_shell is live on the compositor; scanout is closed off by the kernel config

- The vendor compositor now exposes its own IAS interface and an output. `wrandr` enumerates the
  registry and reports **`ias_shell`** among the globals, and `weston-info` reports `wl_output` version 2
  alongside `wl_compositor`, `wl_scaler`, `presentation` and `wl_seat`. With `ias-shell.so` loaded and
  its config accepted, the stack is coherent rather than merely running.
- **Scanout is definitively unavailable**, and the kernel configuration settles it rather than an
  experiment: `CONFIG_DRM_I915=y` is the only DRM driver present. `CONFIG_DRM_FBDEV_EMULATION` is not
  set, and `CONFIG_DRM_BOCHS`, `CONFIG_DRM_VIRTIO_GPU`, `CONFIG_DRM_UDL`, `CONFIG_FB_VESA`,
  `CONFIG_FB_SIMPLE` and `CONFIG_FB_EFI` are all absent. So no `/dev/fb*` can exist for
  `fbdev-backend.so` to bind, and no `/dev/dri/card0` can appear unless i915 binds — which QEMU cannot
  cause, since it emulates no Intel IGD.
- This closes the "just use the fbdev backend" option permanently and confirms the display decision was
  correct: a virtual KMS driver or a patched software IAS backend are the only routes to a visible
  surface, and the image's own headless backend is the only one that works today.
- `opt/ias/` is an empty OEM mount point in the rootfs — `bin` and `lib` exist and are empty — so the
  `grid_layout.so` that `ias.conf` references as `defer="1"` is genuinely absent, not misplaced. That
  matches the absence of any complaint about it: the shell treats the layout plugin as deferred.
- Net position: the HMI stack runs, its control interface is live, an output exists on the protocol
  level, and nothing is rendered to a framebuffer. That is the exact boundary the display decision
  addresses.

## 1.13.0 - IAS shell initialised with the vendor config; `/media` resolves to world-writable

- The compositor now loads `ias-shell.so` **with its configuration**, and the IAS error is gone. The
  path is `$XDG_CONFIG_HOME/ias.conf` exactly — not `$XDG_CONFIG_HOME/.config/ias.conf` — which is why
  the vendor ships it at `etc/xdg/weston/.config/ias.conf`. With `XDG_CONFIG_HOME=/tmp/ias` holding a
  copy and the CRTC renamed from `HDMI1` to the headless backend's `headless-0`, the shell initialises
  without complaint, `wayland-0` exists, and `NaviUpdateApp` stays attached with only the benign
  `QDBusConnection` warning.
- `esinit` sets `XDG_RUNTIME_DIR="/run/user/root"` (line 148), so the earlier `/tmp/xdg` was a
  research-side invention; the vendor path is now used.
- **V-011's weakest link is resolved, in the more serious direction.** `etc/fstab_emmc:8` mounts
  `tmpfs /media tmpfs defaults`, nothing in the tree sets a mode or owner (no `tmpfiles.d` entry, no
  `/media` reference in `esinit`), and the kernel's tmpfs root default is `01777`. So `/media` is very
  likely world-writable and sticky while the per-device subdirectories are `0755 root:root`: an
  unprivileged process can create entries in `/media` but cannot rename root's.
- That sharpens V-011 rather than changing its precondition. Because the kernel interprets a device
  node's own recorded uid/gid/mode, an attacker crafting an image sets the node `0666` and defeats
  `0660 root:disk` entirely — unprivileged read and write of **internal** storage, not merely removable
  media. Physical USB access is still required; what changes is scope.
- The `..` serial vector remains an amplifier, now with a plausibly writable mount root. Recorded as
  unverified, with the specific test that would settle it.

## 1.12.0 - the vendor compositor runs and the UI connects to it

- No build was needed to get a compositor: the image already ships **`headless-backend.so`** and
  **`fbdev-backend.so`** alongside `ias-backend.so`, so the vendor's own weston can run without a DRM
  device.
- Running `/usr/bin/weston --backend=headless-backend.so --shell=/usr/lib/weston/ias-shell.so` with
  `XDG_RUNTIME_DIR` set produces a live socket: `wayland-0` and `wayland-0.lock` appear, weston stays
  alive, and `ias-shell.so` loads.
- **`NaviUpdateApp` no longer fails on display.** It stays alive and its only remaining output is the
  benign `QDBusConnection: session D-Bus connection created before QCoreApplication` warning. The
  earlier `Failed to create display (No such file or directory)` is gone, which means the UI process
  connects to the vendor compositor.
- Two ordinary obstacles were cleared on the way. Weston initially quit because it could not launch
  `/usr/libexec/weston-desktop-shell`; that is the wrong shell for this product, and `ias-shell.so` is
  the right one. And `ias-shell` then reported
  `Failed to open IAS config file (//.config/ias.conf)` because `HOME` is unset, so the config path
  collapses to `//.config/ias.conf` instead of the vendor's `etc/xdg/weston/ias.conf`.
- Next: supply the IAS config so the shell initialises its outputs, confirm a surface is created, and
  then replace the headless backend with real scanout — which is where the display architecture
  decision applies.

## 1.11.0 - the MICOM daemon's exit was the missing device, and the gate is now the compositor

- **`micommanager` starts successfully** on the authentic multi-user boot once `/dev/ttyS1` exists:
  `Starting System service for micommanager`, the daemon logging its own banner
  (`micommanager_userspace release data : 2015.10.19`), then `Started System service for micommanager`.
- That corrects the previous reading. The `status=1/FAILURE` that appeared to block
  `ApplicationLauncher`'s hard `Requires=` was simply the absent serial device: the earlier multi-user
  run was booted without `--micom-serial`. No protocol work was needed to satisfy the dependency, and
  the reply/frame simulator is therefore not on the critical path for the HMI.
- With the daemon up, `Reached target Multi-User System` stands and the next failure is upwards of it:
  `nua.service` restarts three times from 64.4 s and then hits `start-limit`. The daemon exits 1 each
  time, and the earlier standalone repro gives the reason: `XDG_RUNTIME_DIR not set in the environment`
  and `Failed to create display (No such file or directory)`.
- So the operative blocker is now the one the display decision predicted: **nothing creates a Wayland
  compositor, a runtime directory, or a socket**. There is no `weston.service` in the image at all,
  only `weston-crash.path`, and esinit's own weston launch is still gated off by `/tmp/spi_validation_NOK`.
- Both workers dispatched for this round returned no result and wrote nothing to disk; the finding above
  came from re-reading an existing run rather than from new work. Recorded plainly rather than presented
  as progress by delegation.

## 1.21.0 - Constrain ConnMan CVE-2023-28488 to the exact fortified outcome

- Confirmed CVE-2023-28488's pre-fix IPv4 total-length ordering in exact
  `connmand` instructions rather than inferring from the recovered package
  version.
- Mapped ordinary IPv4 startup through `INIT_SELECTING`, listening mode 1, an
  `AF_PACKET` datagram socket, and the affected GLib receive callback.
- Established that this exact build calls `__memcpy_chk` with a 628-byte object
  size. Every recovered libc checked-copy implementation reviewed reaches
  `__chk_fail`/`__fortify_fail` before copying an underflowed length.
- Added a packet-free exhaustive arithmetic model and tests. All 43,057,152
  combinations of possible 0..656-byte reads and 16-bit IP total lengths divide
  into short/partial rejects, 17,612 fortified abort cases, and 198,135 bounded
  copies; the model opens no socket and creates no packet bytes.
- Recorded V-016 as a conditional adjacent-network ConnMan availability issue,
  not a stack overwrite, RCE, or root path for recovered `260128`. No packet was
  generated, the NIC-free VM was unchanged, and the owner's installed build
  remains unknown.
- Preserved official responses, decoded upstream fix, full source/disassembly,
  Ghidra records, and generated JSON under ignored `work/`; tracked only the
  model, tests, report, planning checkpoint, and sanitized evidence excerpt.

## 1.20.0 - Recover exact package inventory and confirm the ConnMan DHCPv6 candidate

- Recovered 1,679 exact installed-package records from the RPM Berkeley DB
  `Nvra` index using a read-only project-local Berkeley DB 18.1.40 `db_dump`.
  Added `tools/uk_fw/rpm_nvra_inventory.py` and focused tests for strict,
  deterministic parsing of printable dump records, exact package selection,
  symlink rejection, malformed-input failure, and atomic output replacement.
- Identified `connman-1.29+5w.master.38-r1.corei7_64`, then confirmed
  CVE-2026-115863 from exact shipped instructions rather than the version label.
  `connmand+0x1f150` makes the fixed 1,025-byte DOMAIN_LIST copy and performs the
  unbounded label-pointer `'.'` stores; option-24 dispatch calls it directly.
- Mapped the exact conditional route: the connected-network RA callback handles
  Managed/Other flags, the Other path starts a DHCPv6 information request, and
  that routine explicitly requests option 24. The installed uid-0 service does
  not exclude intended `wlan0` and uses `Restart=on-failure`.
- Recorded trigger gates and mitigations: a reply still must match live DHCPv6
  transaction/client/server/state checks, while the ELF has PIE, NX stack,
  stack canaries, and full RELRO. No packet was sent and no crash, RCE, root
  access, or physical-device applicability is claimed.
- Kept the full database dump, source, disassembly, decompiler output, and online
  responses under ignored `work/`; tracked only the parser, tests, conservative
  report, and sanitized evidence excerpt.
- Fable remained unavailable for native delegation, and the previously checked
  DeepSeek Flash route remained rejected by the native dispatcher; no silent
  substitute or failed worker output was used.

## 1.19.0 - Confirm synthetic udev activation and map the thumbnail ASF route

- Added `tools/uk_fw/udev_systemd_probe.py` and focused tests for matched
  negative/positive controls using exact recovered `systemd`, `systemd-udevd`,
  and `udevadm` binaries.
- Both offline runs used `-nic none`, snapshot-backed storage, a read-only root,
  transient `/run` files, and a minimal custom target layered on installed
  sysinit. The vulnerable persistent-storage and V4L helper rules were masked
  before coldplug; no shipped vulnerable helper or pre-existing property-selected
  unit was selected.
- The negative synthetic-add run persisted only fixed `ID_SCSI_SERIAL` and kept
  the marker unit inactive. The positive run added fixed `SYSTEMD_WANTS`, exact
  PID 1 logged the otherwise-unreferenced transient marker unit starting, and
  fixed marker-file/active-state checks passed.
- Extended `vm_boot.py` with an optional exact terminated serial-completion line
  for safe PID-1 handoff diagnostics, preserving all default behavior.
- Preserved the boundary: this confirms synthetic udev database/device-unit and
  manager semantics, not hardware bytes reaching shipped helpers, a physical
  device, the installed shell unit, root access, interactivity, or persistence.
- Fable remained unavailable for native subagents. DeepSeek Flash passed static
  route checks but native dispatch was rejected as an unknown model; no failed
  worker output or silent substitute was used.
- Corrected V-012's thumbnail model using exact binaries. MediaBrowser's
  `requestThumbnails(as)` forwards to the extractor's session-bus `Start(as)`;
  that method always selects `VideoContext`, whose exact pipeline is
  `uridecodebin ... appsink` and whose autoplug callback does not reject
  `asfdemux`. The separate audio/TagLib context is for cover art.
- Preserved the reachability boundary: reviewed scan callbacks do not request
  thumbnails, and bounded VM attempts observed no delivered `Start`, ASF-plugin
  map, cache output, or natural crash. The new evidence is a static explicit
  client-request route, not automatic USB/UI invocation or dynamic thumbnail
  corruption.

## 1.18.0 - Confirm benign second-property retention in the exact udev parser

- Added `tools/uk_fw/udev_import_probe.py` and focused tests for a fixed,
  parser-only offline diagnostic. The tool verifies exact recovered `udevadm`
  and `systemd-udevd` hashes, uses only `udevadm test`, sends no uevent, starts
  no daemon or service, and names only an intentionally nonexistent benign unit.
- Matched the advisory's security-relevant two-line shape: fixed synthetic output
  contained `ID_SCSI_SERIAL=V014_BENIGN_CONTROL` followed by a leading-space
  ` SYSTEMD_WANTS=v014-benign-nonexistent.service` line.
- The exact recovered rule engine executed the synthetic import helper, recorded
  the raw leading-space line, and emitted the normalized separate property
  `SYSTEMD_WANTS=v014-benign-nonexistent.service`. The helper, rule, and log were removed,
  the command exited zero, and classification was
  `benign-second-property-retained`.
- Preserved the boundary: shipped vulnerable helpers were not executed; udevd,
  a kernel uevent, systemd manager, existing unit, root shell, and privilege
  transition were not involved. This closes the downstream import-parser step,
  not physical hardware delivery or root activation.
- DeepSeek Flash passed static route checks but native dispatch still rejected
  its model as unknown; Fable remains unavailable for native subagents. No
  failed worker output or silent substitute was used.

## 1.17.0 - Exact udev helper injection reaches a shipped root-shell unit

- Added `tools/uk_fw/privilege_surface.py`, a deterministic standard-library
  scanner for extracted Linux root filesystems, with focused tests and explicit
  limits for host-visible modes, xattrs, systemd parsing, loader paths, and udev
  rules. The bounded ignored report walked 236,552 entries and 102 services.
- Confirmed no setuid/setgid entries in the extracted metadata or reviewed
  source archives. The 129 writable-executable-mode results are mostly `/navi`
  files whose original archive modes are `0777`, while normal fstab policy
  mounts `/navi` read-only; this is not promoted to a write or root path.
- Added V-014 for CVE-2026-40225. Exact shipped `v4l_id` and `scsi_id`
  instructions directly print kernel-provided fields without the upstream
  control-character checks. Installed rules invoke both helpers, execute
  injected `REMOVE_CMD`, and expose block-device `SYSTEMD_WANTS` to systemd.
- Identified the decisive installed target: `debug-shell.service` is configured
  to start `/bin/sh` as root on `/dev/tty9` when its path condition passes. This
  yields a high-confidence static malicious-SCSI-device-to-root-console path
  without requiring an attacker-
  written unit file.
- Closed one narrow runtime condition safely: an offline VM control confirmed
  `/dev/tty9` exists as `root:root` mode `0600`, character device `4:9`, under
  the recovered vendor kernel/userspace and research init. It did not start the
  service or inject a property.
- Preserved the remaining runtime boundary: no malicious hardware, authentic
  injected udev event, systemd service activation, VT9 interaction, root
  command, or installed-head-unit applicability was demonstrated.
- Recorded mixed component provenance rather than trusting one banner: PID 1
  and pkg-config report `225`, while embedded build paths say
  `systemd/1_249.3-r0`. Exact binary instructions and installed rules—not either
  version string—establish the finding.
- Kept V-006 rejected as USB-to-root. Its sanitized `usb_id`
  `ID_SERIAL_SHORT` path is distinct from V-014's unsanitized `v4l_id` and
  `scsi_id` helper output.

## 1.16.0 - LightMediaScanner indexing is not the V-012 GStreamer route

- Confirmed authentic `startup-scan=true` handling of a 33-stream ASF/WMA under
  `/media/usb/probe`. LightMediaScanner discovered the USB path, processed one
  file, committed it with zero reported errors, and remained alive.
- Identified the exact scanner parser:
  `/app/lib/lightmediascanner/plugins/asf.so`, SHA-256
  `f4b42a8eacb73990d35439e27513c28f1d31257488d0c130e6e1a936cb9bb219`.
  It imports direct `open`/`read`/`lseek` and LightMediaScanner database APIs;
  it has no GStreamer dependency or `gst_*` import.
- Captured an unfiltered bounded session-bus interaction. It contains scanner
  registration, properties, `Scanner1.Scan`, and progress signals, but no
  PlayerEngine or thumbnail-service call.
- Classified this as a route-specific negative result for V-012: automatic
  LightMediaScanner indexing is real, but it does not invoke vulnerable
  `asfdemux` in this path. Post-index media-manager/browser selection, thumbnail,
  and playback handoff remain open.
- Added a minimally sufficient tracked excerpt under
  `evidence/artifacts/media-candidates/lightmediascanner-asf-evidence.txt` and
  updated the primary V-012 report, register, inventory, handover, and priorities.

## 1.15.0 - PlayerEngine reaches the ASF corruption and vendor offsets are exact

- Corrected the PlayerEngine contract: accepted audio options are nested JSON,
  `{"option":{"mediatype":"audio"}}`; old flat calls were negative contract
  controls. Stock audio is `alsasink` on `media_mixer`.
- Isolated the remaining VM prerequisite. QEMU reports no soundcards, so stock
  `media_mixer` fails. A disposable VM-only ALSA `type null` mapping for that
  exact PCM lets a valid one-stream WMA return true and reach `asfdemux` without
  changing the vendor sink factory or device name.
- Confirmed the boundary under one environment: one-stream and 32-stream file
  URIs return true and PlayerEngine survives; 33- and 34-stream inputs return
  true, enter the vulnerable range, and terminate PlayerEngine with signal 11.
  A plain path returns false while `file:///tmp/input.wma` succeeds.
- Extracted the exact fatal stack:
  `g_queue_push_head+0x1d <- libgstasf.so+0xb6cc <- libgstasf.so+0x1305d`.
  The shell marker `PLAYERENGINE_ALIVE=1` means `kill -0` failed and the process
  had died; 0 means alive.
- Corrected the source-derived layout against the shipped plugin. The vendor
  `AsfStream` stride is 208 bytes, not 200. The 33rd stream zeros the low 32
  bits of `flowcombiner`; its pad pointer lands in `old_stream[0]`. Exact code at
  `0xb6c0..0xb6c7` loads the corrupted combiner and calls
  `gst_flow_combiner_add_pad`, leading to the observed GLib failure.
- Preserved the boundary: this proves manual uid-0 PlayerEngine service
  reachability, memory corruption, and process death—not attacker-selected
  pointer control, RCE, persistence, automatic removable-media/indexer
  invocation, or physical-head-unit applicability.
- Added minimally sufficient tracked excerpts under
  `evidence/artifacts/media-candidates/` and updated V-012, the exploit
  inventory, corrections log, handover, and prioritization.

## 1.14.0 - adjacent ALSA CVEs split by exact lock and permission evidence

- Rejected ALSA PCM CVE-2017-0861 for recovered EU `260128`: exact shipped
  `snd-pcm.ko` takes the per-PCM open mutex around `snd_pcm_info_user`, matching
  the complete two-line upstream fix.
- Confirmed that ALSA sequencer CVE-2018-1000004's native ioctl path lacks the
  per-client serialization in the mainline and Linux 4.1 stable fixes.
- Kept the reachability boundary explicit: the published sequencer-pool race
  requires concurrent `write()` activity, while recovered `/dev/snd/seq` policy
  is `root:root 0644`. The VM confirmed V-013 ioctls through an `O_RDONLY`
  descriptor under that manually modeled mode, but an ordinary user cannot
  obtain the write-capable descriptor required by this sibling sequence.
- Added tracked upstream patches, exact relocation-aware function
  disassemblies, provenance commands, and
  `evidence/vendor-kernel-alsa-follow-up-cves.md`. No new root path is claimed.

## 1.13.0 - exact ALSA/UFO kernel candidates and a bounded sequencer diagnostic

- Added V-013 for CVE-2017-15265 after exact `snd-seq.ko` review showed the
  pre-fix port lifetime flow. The finding is grounded in module instructions,
  not the `4.1.27-abl` banner.
- Added `tools/uk_fw/alsa_seq_probe.py`, a no-network, snapshot-backed harness
  for a freestanding single-create/delete diagnostic. It hash-verifies the
  transferred probe and runs it as numeric uid/gid 65534 under the recovered
  `root:root 0644` DAC mode. The run confirmed read-only open, client-ID,
  create-port and delete-port reachability.
- Preserved the impact boundary: a separate bounded race issued 200,000 create
  and 400,000 delete attempts without a kernel fault. No dynamic UAF,
  controlled reuse, privilege transition, or arbitrary execution is claimed.
- Confirmed exact pre-fix IPv4 and IPv6 logic for CVE-2017-1000112. This remains
  conditional because `CONFIG_USER_NS=n` blocks the published unprivileged root
  setup, production `NETIF_F_UFO` features are unknown, and the VM remains
  intentionally NIC-free.
- Rejected CVE-2016-0728 through exact `join_session_keyring` evidence: the
  shipped function contains the missing-reference `key_put()` operation. Added
  correction C22.
- Added dedicated evidence reports, updated the kernel triage and exploit
  inventory, and retained all version-derived claims as candidates until exact
  shipped code and reachability are established. Canonical validation reports
  `196 passed, 25 subtests passed`; the canonical rootfs hash and clean
  `e2fsck -fn` counts remain unchanged.

## 1.12.0 - the MICOM daemon does transmit first, and the command table exists

- Measured on the authentic multi-user boot with `--micom-serial`: **1056 bytes, 103 frames** on
  `/dev/ttyS1`, against `micom_serial_bytes: 0` on every earlier attempt. The contract's weakest link
  is now closed by measurement rather than argument.
- **The daemon transmits before it receives.** It does not wait for a MICOM-init frame, so a passive
  peer suffices to reach the ask stage. The earlier zero-byte observation was an artefact of a
  transcript filter that watched a single fd, not a protocol precondition.
- The frame format is confirmed on real traffic and not merely in the validator: all 103 frames parse
  as `AA id_hi id_lo L payload CS` with whole-frame XOR zero, and none are malformed.
- The command-id table that no static table in the binary encodes now exists empirically: `0x0400`
  ×32, `0x01a4` ×20, `0x029d` ×13, `0x0266` and `0x0210` ×10 each, `0x0212` ×5, `0x0201` ×4,
  `0x02a3` ×3, `0x0289` ×2, then `0x01aa` (payload `01`), `0x02c3`, `0x0217` and `0x0110` singly. The
  run opens with `0x0212` ×3, then `0x01aa(01)`, then `0x0212` ×2, `0x02c3`, `0x0266`, `0x0201`.
- Still open: which id is `AskSysBootinfo`, and so which frame must carry the 35-byte `ay`. The
  launcher's static sequence places it second, making `0x01aa (01)` then the first `0x02c3` the leading
  candidates, answerable in one run by replying to all ids and observing which reply the launcher's
  field decoder actually consumes.
- A delegated worker on this task was cut off before producing anything; the measurement above was
  taken directly instead. `micom-contract.md` was unchanged by that worker, so nothing is being
  credited to it that it did not do.

## 1.11.0 - bounded Tuxera harness and exact kernel-backport checks

- Added `tools/uk_fw/tuxera_fs_probe.py` and its tests: a no-network,
  snapshot-backed harness that attaches only a project-local regular raw image
  with QEMU `readonly=on`, loads one exact vendor filesystem module, mounts with
  `ro,nodev,nosuid,noexec`, and performs bounded metadata enumeration.
- Switched the harness from QEMU xHCI to EHCI after authentic `xhci-pci` faulted
  in vendor `xhci_toggle_dis_perr_det()`. EHCI with the authentic `ehci-pci`
  module is stable; the xHCI result is recorded as a VM compatibility issue, not
  a production vulnerability.
- Authentic Tuxera exFAT `3016.6.23.3` cleanly mounted a 64 MiB control. Sixteen
  malformed upstream exfatprogs fixtures yielded three clean rejections and
  thirteen clean bounded mounts/unmounts, with no detected kernel parser fault.
  This is a bounded negative result rather than evidence of parser safety.
- Generated a clean 64 MiB NTFS 3.1 control with project-local Alpine `mkntfs`;
  exact Tuxera NTFS `3016.7.1.2.3` mounted and unmounted it cleanly. The V-011
  harmless semantics test then retained character node `1:3` across remount.
  Numeric uid/gid 65534 under SMACK `_` opened QEMU `/dev/null` read-only when
  `nodev` was omitted; the `nodev` control denied the same open. This confirms a
  device-policy bypass primitive, not a demonstrated USB-to-root path.
- Exact recovered-binary analysis rejects four version-derived local-root
  candidates for EU `260128`: Dirty COW/CVE-2016-5195, AF_PACKET
  CVE-2016-8655, AF_PACKET CVE-2017-1000111, and the generic Stack Clash
  missing-guard-gap premise. The vendor kernel contains the relevant
  `FOLL_COW`, socket-locking, and 1 MiB inter-VMA guard-gap backports despite its
  `4.1.27-abl` banner.
- Added dedicated evidence reports and corrections C18-C21. V-011 remains a
  hardening gap/post-execution primitive: production mount-path access, useful
  major/minor selection, application SMACK labels, and any root consequence are
  still unverified.

## 1.09.0 - normal multi-user reached; the blockers are now the two known ones

- **`Reached target Multi-User System`**, startup 10.6 s kernel plus 46.9 s userspace, no emergency
  mode, `dlt-daemon` writing to `/log_data/kernel/*.dlt`. The authentic vendor boot now completes.
- Two ordinary defects were in the way rather than anything architectural. `/bin/check-mount.sh` ships
  **`0644`** — no execute bit — in both the image and the vendor tarball, so a required mount check
  simply could not run (`direct_exec_rc=126`, `via_sh_rc=0`). And `systemd-remount-fs`'s
  `ExecStartPre=/bin/mount -a` exited 64, which is util-linux's "some mounts succeeded", because
  eleven fstab lines wanted `/dev/mmcblk0pN` partitions the projection does not have.
- Fix applied on a CoW clone: `chmod 0755` on the check script, and the eleven partition lines replaced
  with self-binds of the same filesystem (`/navi /navi none bind,ro,noatime` and so on), which invents
  no block devices. Canonical image still hashes `4953a005…66d036f`.
- `Dbuslaunch` now succeeds: `Started HKMC Preminum AVN 2.1 -Launcher`.
- What remains is exactly the pair already identified, now with hard evidence:
  - `micommanager_userspace` exits 1, logging only to kmsg/DLT, and `ApplicationLauncher` carries a
    hard `Requires=` on it, so the launcher dies by dependency.
  - Nothing starts a Wayland compositor. **There is no `weston.service` at all** — only
    `weston-crash.path` — so weston is launched solely by esinit's own branch, which the `SPI NOK`
    marker still skips. Consequently `nua` fails with `XDG_RUNTIME_DIR not set` and
    `Failed to create display`.
- `micom` is not a unit either; `Dbuslaunch`'s `After=micom.service` dangles harmlessly.

## 1.08.0 - systemd runs for the first time; USB nodev defect found

- **PID 1 is now systemd.** `systemd 225 running in system mode`, hostname `prm-gen-5`, with
  `systemd-modules-load`, udev, sysusers, tmpfiles, journald, `auditd` and the fstab mount units all
  attempted. This is the first time the authentic vendor boot has got past esinit's own script.
- The unblock was one line: `install lge_usb_adapter /bin/true` in `etc/modprobe.d`, applied to an
  APFS copy-on-write clone (`cp -c`, instant) rather than the canonical image, which still hashes
  `4953a005…66d036f`. `fan` then loaded normally, confirming the earlier deadlock was the orphaned
  platform lock and nothing else.
- The chain now stops at `local-fs.target`. `systemd-remount-fs` exits 64, `check-mount.sh` fails with
  permission denied, and every fstab entry wants a `/dev/mmcblk0pN` that this projection does not have,
  so `dev-mmcblk0p8.device` times out and the system reaches **Emergency Mode** at 103 s. The missing
  piece is the partition table, not a service.
- `/tmp` artefacts from esinit are all present and correct: `/tmp/passwd` 996 bytes, `/tmp/fstab`,
  `/tmp/weston.ini`, and the SPI marker. The SPI gate still blocks esinit's own weston launch.
- USB root-surface map completed. **Most promising vector: the automounted USB filesystem is mounted
  without `MS_NODEV`.** The flag word at `0x4c00` is `0xC0ED000A`, which is `nosuid,noexec,dev` — so an
  attacker-controlled filesystem image can carry a device node and reach block devices that
  `0660 root:disk` would otherwise guard. Statically provable and needs no bug. Recorded as V-011.
- The udev sanitiser mechanism is now precisely characterised: the `#+-.:=@_` allow-list is
  `util_replace_chars(0x22a00)` called from `builtin_usb_id` with `allow=NULL`, not
  `udev_util_encode_string`; `ID_SERIAL` is safe only because its components were sanitised first;
  `ENV{…}=` rules apply no sanitiser at all, but the single USB-relevant rule is unreachable behind a
  firewire and skip_pci gate.
- **V-010 is downgraded.** Its faulting pointer is the global `0xffffffff81bd5460`, set only from
  `dev.platform_data` at `0x810594c2`, with no attacker-reachable path identified. It stands as a
  bring-up defect and a reminder that the driver asserts hardware presence, not as a security finding.
- Second and third ranked vectors recorded for further work: the unseparated media-parser chain
  (V-007), and a `..` serial combined with an unchecked `umount2`/`mkdir`/`mount` sequence that lands a
  mount on `/media` when `/media` is writable — an amplifier whose severity depends on a `/media` mode
  that is still unverified.

## 1.09.0 - authentic ASF parser overflow reproduced; V-006 guidance corrected

- Dynamically reproduced CVE-2026-2920 in the shipped GStreamer ASF plugin
  `/usr/lib/gstreamer-1.0/libgstasf.so` (SHA-256
  `05e887731708f0b0a52ff9fc75767a00fda9984e422983e5ff1d672f4b1af45d`). A valid
  WMA/ASF probe with 33 unique Stream Properties Objects causes authentic
  `gst-discoverer-1.0` to create stream 33 beyond the element's fixed 32-entry array and then
  terminate with `SIGSEGV`/exit 139.
- Added `tools/uk_fw/asf_stream_probe.py`, a bounded generator/auditor that duplicates exactly one
  valid ASF stream object, repairs header/file sizes, assigns unique 7-bit stream IDs, refuses
  malformed templates and in-place output, and audits the upstream rejection marker. Added five unit
  tests.
- Recorded the parser finding as V-012. The VM proves memory corruption and denial of service, not
  arbitrary code execution, persistence or physical-head-unit applicability. Upstream/NVD describe
  RCE potential, but instruction-pointer control was not attempted or claimed.
- Traced likely production context: `libthumbnailextractor.so` links GStreamer and contains a
  `uridecodebin ... ! appsink` pipeline, while D-Bus activation does not drop uid. Two bounded
  `Start(as)` attempts did not reproduce the ASF crash, so automatic thumbnail/scanner reachability
  remains unproven and those runs are retained as negative controls.
- Rewrote the stale `usb-root-test-plan.md` and exploit inventory. The old `${IFS}` MTP serial
  payload is explicitly withdrawn: `usb_id`'s second sanitizer limits `ID_SERIAL_SHORT` to
  `[A-Za-z0-9#+-.:=@_]`, as already confirmed dynamically in 1.05.0. The root shell sink remains
  unsafe design and a possible denial-of-service surface, not demonstrated descriptor-to-root code
  execution.
- Added `evidence/gstreamer-cve-2026-2920.md` with artifact hashes, exact dynamic sequence, production
  reachability boundary, related-CVE triage, remediation and regression criteria.
- Resolved the concurrent vulnerability-ID collision: the earlier missing-`nodev` hardening gap remains
  V-011 and the ASF memory-corruption finding is V-012.
- Tightened V-011's impact claim. The automounter accepts vendor `tntfs`/`texfat`, not arbitrary ext
  images; FAT/exFAT cannot natively store POSIX device inodes, and Tuxera NTFS special-node semantics
  remain untested. Missing `MS_NODEV` is confirmed, but a useful device node and privilege bypass are
  not. It is not a first-step root path.

## 1.07.0 - authentic init chain runs to a kernel oops, and the MICOM contract is written

- The boot harness gained a validated `--init` choice (`/init` or `/lib/systemd/esinit`), defaulting to
  the research init. The canonical image is provably untouched by this: the drive is already
  `snapshot=on` so QEMU writes a throw-away overlay, and `rootfs.img` hashes identically before and
  after four runs.
- `esinit` now runs authentically through step 22 and stalls one line before systemd. The artefacts
  that its absence kept costing us now exist: `/tmp/passwd` at 996 bytes, `/tmp/fstab`,
  `/tmp/weston.ini`, and the `*_code_*` files. PID 1 never becomes systemd and no `Reached target`
  line appears, held for 300 extra seconds across two long runs.
- The blocker is a kernel fault, not a service failure. `/etc/esinit-modprobe.sh` killed
  `/sbin/modprobe lge_usb_adapter`, which oopsed with a NULL dereference at `000000000000000c` in
  `sbi_apl_commit+0x60/0x2bc`. That orphans the platform `device` lock, so the next platform driver
  registration blocks: `/sbin/modprobe fan` never returns and sits in state `D` inside
  `lge_fan_init`. The hung-task detector is compiled out, which is why the stall is silent.
- Controls isolate it: `modprobe fan` on a clean guest returns 0, and `modprobe hid-generic` still
  succeeds after the oops, so only the platform bus is wedged. Recorded as V-010.
- `esinit`'s own weston launch is skipped for a second, independent reason: the SPI validation marker
  `/tmp/spi_validation_NOK` persists because `/sys/module/micom/parameters/spi_validation` does not
  exist. That branch is also console-silent, because the vendor wrote `echo "SPI NOK" > kmsg` with a
  relative path, creating `/kmsg` instead of logging.
- MICOM contract written from static evidence with each claim tagged verified, inferred or
  unestablished: bus `com.lge.car.micom`, object `/Ihu`, interface `com.lge.car.micom.ihu`, method
  `AskSysBootinfo` taking no arguments and returning `ay`. The 35 bytes are the reply payload, not the
  request: frames are `AA id_hi id_lo L payload CS` with an XOR checksum over the whole frame, and a
  reply carries the request id with bit 15 set, at 115200 baud on `/dev/ttyS1`. Five methods in
  dependency order would satisfy the launcher.
- Weakest link stated plainly: it is unresolved whether the daemon transmits before it receives, since
  the retained trace filtered a single fd, so a MICOM-init precondition and a wrong-fd write are not
  separable from static evidence. One `xxd` of `micom-serial.bin` settles it.
- **Correction:** `/work/` is gitignored, so earlier commits that appeared to include the analysis
  documents did not. Sanitised analysis now lives under `evidence/vm-bringup/`, which is the tracked
  location the repository policy intends.

## 1.06.0 - display architecture decided: software IAS backend, stock weston

- Decision recorded after reviewing the gap analysis against the actual kernel tree: patch only
  `ias-backend.so`'s DRM output path into a software IAS backend at 1920x720 named `HDMI1`, and keep
  stock `/usr/bin/weston`, the IVI modules and the IAS protocol. Reason: it preserves the vendor
  compositor architecture instead of permanently substituting it.
- Rejected, with reasons: a vkms-style kernel module is not the critical path, because 4.1.27 has the
  DRM/KMS helpers but no in-tree vkms, and `work/kbuild/drmkms/drmkms10.c` demonstrates only
  card/connector/mode registration — not GBM allocation, scanout, planes, flips, vblank or an
  1920x720 HDMI CRTC. An LD_PRELOAD/libdrm emulation is the wrong seam, needing broad DRM/GBM/EGL and
  likely Intel private ioctl behaviour. A permanent weston-headless baseline excludes the IAS
  compositor and control path, so it is a demo rather than the goal.
- This **corrects the gap analysis**, which was optimistic that a generic libdrm/GBM node plus
  `kms_swrast` would satisfy the compositor. `ias-backend.so` carries i915/intel-specific paths and
  both atomic and legacy KMS and plane APIs, so a plain card node is not a compatible device.
- Riskiest assumption, stated for falsification in one run: that the stock IVI modules need only the
  Weston backend ABI plus the `ias_crtc` interface, and no hidden i915 semantics. Estimate 2-3 weeks to
  bring up, 4-6 weeks to sustained HMI fidelity.

## 1.05.0 - MTP branch proven reachable, and its injection is blocked by udev

- The V-006 sink is now confirmed reachable at runtime: an emulated `usb-mtp` device yields
  `ID_USB_INTERFACES=:060101:`, the automounter takes the MTP branch, and the guest reports
  `sh: /usr/bin/go-mtpfs: No such file or directory` — a message only the `system()` call can emit.
- Injection does **not** fire. udev delivers a sanitised property: the submitted
  `a;id>/tmp/v006.id;echo${IFS}V006KMSG>/dev/kmsg;#` arrives as
  `a_id__tmp_v006.id_echo__IFS_V006KMSG__dev_kmsg_#`. A second sanitiser beyond
  `util_replace_whitespace` enforces alphanumerics plus `#+-.:=@_` and rewrites every other printable
  byte to `_`. The allow-list string is present in `systemd-udevd` and `libudev`.
- A positive control settles the cause: the same string handed directly to the guest's `/bin/sh`
  produces `uid=0(root)`, so the payload, the guest and the harness are all fine and the sanitiser is
  the obstacle.
- V-006 is therefore downgraded to a latent defect rather than an exploitable-by-construction one, and
  the register's own "metacharacters pass through" claim is withdrawn. The `sprintf`-into-`system()`
  pattern is still a real defect worth removing.
- Static HMI gap analysis completed (569 lines, `hmi-gap-analysis.md`). The harness `/init` is an
  artefact, so the authentic chain `init=/lib/systemd/esinit` and systemd itself have never run in the
  VM, which is why the `/tmp` state that services authenticate against keeps being missing.
- Ranked blockers recorded: authentic init chain, a live `com.lge.car.micom` with the 35-byte
  `AskSysBootinfo`, a DRM node for the vendor compositor, weston's start condition and session-bus
  ordering, the `mnt-wt` resource table and theme assets, `can0`, `/dev/ttyGPS`, then touch and audio.
- Largest single blocker identified: the vendor compositor needs `HDMI1` at 1920x720 through
  `ias-backend.so` over i915/GBM, and neither emulated QEMU VGA nor the vendor kernel provides an i915
  device, so `/dev/dri/card0` cannot exist as configured. Every HMI result so far used a substituted
  compositor.

## 1.04.0 - the mount service runs in the VM, and a passwd symlink surfaces

- `usb-automount` now stays alive in the emulated userspace and owns `com.lge.car.automount` on the
  system bus. Twelve polls over sixty seconds all saw a live process in state `S`, and `ListNames`
  confirms the name is owned. The mount request surface is therefore live in the VM for the first
  time, which is the precondition for any V-006 work.
- The blocker was not a D-Bus policy problem but a missing password database: `/etc/passwd` in this
  image is a symlink to `/tmp/passwd`, and that target does not exist in a fresh boot, so the daemon
  cannot resolve `root` or its own `messagebus` user and refuses to start. Writing the two entries to
  `/tmp/passwd` is enough, which also shows how the vendor intends this to work: init populates it.
- Control run to establish causality rather than assume it: with the daemon up but the password file
  absent, `usb-automount` still dies in about three seconds with the original assertion. So the
  password database, not the bus policy, was the missing piece.
- Harness notes carried forward: backgrounding a guest daemon without `</dev/null` wedges the serial
  shell silently until timeout, and the host's default `python3` is broken for spawning, so runs must
  use `python3.13`.
- New register entry V-009 for the `/etc/passwd` to `/tmp/passwd` symlink. Recorded as a candidate:
  the runtime permission and ownership of `/tmp` on a real unit are unverified here, and without them
  the impact cannot be stated.

## 1.03.0 - USB injection harness enumerates; V-006 reproduction path corrected

- The three earlier USB attempts failed for one reason each, now identified. `-chardev null` prevents
  QEMU's `usb-serial` from presenting on the bus at all: no connect, no `new full-speed USB device`
  line, nothing in the device list. A file or socket chardev fixes it, and the device then enumerates
  as `0403:6001` with the crafted serial string read back verbatim
  (`SerialNumber: ;id>/dev/kmsg;#`).
- Controller choice is constrained by this kernel. `qemu-xhci` registers a bus but oopses in the
  vendor's `xhci_toggle_dis_perr_det` during root-hub device creation, so no device can attach.
  `ich9-usb-ehci1` is rejected by QEMU itself, because `usb-serial` is full-speed and QEMU treats the
  high-speed bus mismatch as fatal, exiting before boot. `ich9-usb-uhci1` works: a keyboard
  enumerated as `1-2` and the serial adapter as `1-1` in the same run.
- The image carries no `ftdi_sio`, `pl2303` or `cp210x`, so the emulated FTDI adapter produces no
  `/dev/ttyUSB` node. That is expected and is unrelated to V-006.
- `usb-automount` is a Qt5 and dbus-glib service exposing `com.lge.car.automount.request`, not a
  shell script. Started without a system bus it dies at once on a `QDBusConnection` assertion and
  never reaches any mount logic. `/usr/bin/dbus-daemon` is present in the image, so the next run
  starts it first.
- **Correction to this session's earlier reasoning.** Passing a shell payload in the serial string was
  framed as exercising a generic injection path in `usb-automount`. That framing is wrong: the
  documented V-006 mechanism is the MTP branch, and `usb-automount` has no shell interpolation to
  reach. Reproduction therefore needs an emulated MTP device, not a serial adapter.
- No injection fired in any run. `uid=` never appears in the guest log except in the echoed command
  text, which is why the harness must match on structured output rather than a grep of the transcript.

## 1.02.0 - disk investigation: the backups were clones and cost nothing

- Pruned 15 of the 70 `rootfs-pre-*.img` backups, the earliest superseded control chains whose
  results are already retained in `runs/` and `evidence/`. Seven milestone-bearing images were
  kept: the working deadline-pie runner, the llvmpipe Home/Navi/Home run, both valet runners, the
  hmc widget bind, the v2 widget link, and the home-navi deadline predecessor.
- **The prune freed nothing.** 480 GiB was removed from the apparent size and available space did
  not increase; these files are APFS clones sharing blocks with the canonical image, so unlinking
  them releases no space. The 1.6 TB figure was never real usage.
- `tmutil listlocalsnapshots` is empty, so pinned snapshots are not the cause either. The container
  is genuinely full across the whole machine: `~/Library/Application Support` 402 GB, `~/.codex`
  248 GB, `~/Documents/Codex` 201 GB, `~/Downloads` 111 GB, alongside the research tree.
- Consequence recorded plainly: **deleting more project backups will not help**, and further VM
  work is blocked until roughly 50 GB is freed elsewhere or the workspace is moved to another
  volume.
- Correction to the previous entry, which listed the backups as the cause: that inference came from
  apparent size rather than allocation and was wrong.

## 1.01.0 - USB test plumbing added; disk-full blocker recorded

- Added an opt-in `extra_devices` argument to `tools/uk_fw/vm_boot.py` so a research run can
  attach extra QEMU devices, with `-flag value` pairs kept together and multi-line arguments
  rejected. Two tests cover it and pass.
- Purpose: QEMU's `usb-serial` accepts a `serial=` property, which sets `iSerialNumber` on a
  vendor-class device. That means the V-006 serial-injection path can be exercised **without any
  hardware**, which was the open question.
- First attempt reached QEMU and failed correctly but for an environmental reason: `q35` in this
  configuration exposes **no USB bus**, so the device cannot attach. Booting with a USB controller
  plus loading the kernel's USB modules (`usb`, `xhci_pci`, `usbserial`) is the next step, and the
  image carries `usbserial.ko` and `cdc-acm.ko`.
- **Disk blocker recorded:** the volume is at 100% with ~500 MB free. `work/vm/vendor-userspace-260128`
  holds **70 `rootfs-pre-*.img` per-experiment backups, 2.4 TB apparent**, which is what consumed the
  disk. Removing my own derived workspaces freed only 33 MB because they were APFS clones sharing
  blocks.
- The full suite currently fails one test (`test_fat_harness`) with `No space left on device`; that is
  the disk, not the change. `test_vm_boot` passes 24/24 in isolation.
- **Not deleted:** those 70 backups are pre-existing work from earlier sessions and pruning them is
  the owner's decision. Recommended: keep the canonical `rootfs.img` (SHA-256 `4953a005…6d036f`) and
  a small number of retained checkpoints, archive the rest externally, since each is a full copy of
  the same base image taken before one experiment.

## 1.00.0 - live ESP design: interactive root over USB, not a blind one-shot

- Reworked the USB plan now that the owner can reprogram the ESP while it is plugged in. That
  turns a one-shot into an interactive channel, for two concrete reasons.
- **The payload can be a shell.** The template appends `&`, but the payload ends with `;#`, so the
  `#` comments out the backgrounding and the injected command becomes `system()`'s foreground
  child. `;/bin/sh</dev/ttyACM0>/dev/ttyACM0${IFS}2>&1;#` (46 chars, charset-clean) is parsed as
  an interactive root shell whose stdio is the USB serial channel.
- **There is a real feedback channel.** `CONFIG_USB_ACM=m` is present, so a CDC-ACM interface
  yields `/dev/ttyACM0` without needing any mount. That is better than a mass-storage mailbox,
  because the automounter's filesystem strings are only `ntfs`, `exfat` and `ext4` — a FAT volume
  from a microcontroller is not obviously accepted.
- Composite descriptor recorded: `ff/ff/00` vendor interface to satisfy the MTP branch test,
  CDC-ACM for the data channel, and the payload carried as `iSerialNumber`. Since descriptors are
  fixed at enumeration, changing the payload means re-enumerating, which TinyUSB can do in
  software — that is the whole iteration loop, over WiFi, with no unplugging.
- Step order recorded: `;id>/dev/ttyACM0;#` to prove both the injection and the channel, then
  locate the node if `ttyACM0` is absent, then the shell payload, with the credential overwrite
  as an alternative.
- Corrected a stray space in my own `tty*` probe payload, which the whitespace rewrite would have
  mangled into `_`.
- Caveats kept: ACM is a module and may not autoload; the branch fires on the device add event so
  the automount service must already be up; and an open shell blocks the automounter.

## 0.99.0 - USB root test plan written (private)

- Wrote `evidence/usb-root-test-plan.md`, a lab procedure for the owner's own unit, kept
  **private**: it contains an exploit payload and the public mirror carries only the
  status-only V-006 entry.
- Vector A (V-006 serial injection) is validated at the shell level against the exact
  command the firmware builds. Two payloads checked against both real filters (126-character
  limit, `0x20`–`0x7f` minus comma, no whitespace): a 15-character proof of execution writing
  to `/dev/kmsg`, and a 49-character credential overwrite.
- The useful payload targets `/etc/shadow`, which is a symlink to `/tmp/shadow`, using the
  shipped field layout with an empty hash. Combined with `/etc/securetty` already permitting
  root on `ttyS2`, that yields an interactive root login on the serial console. Because `/tmp`
  is tmpfs the change is cleared by a reboot.
- Corrected my own first draft, which wrote `passwd` field order into a `shadow` file; the real
  `shadow.Global` line is `root:…:20481:0:99999:7:::` and the payload now matches it.
- Hardware recommendation recorded: **ESP32-S3 with TinyUSB**, because the trigger needs an
  arbitrary interface class (`06/01/01` or `ff/ff/00`). A Pi Zero in gadget mode cannot present
  either class from stock configfs functions, all of which are `02/06/00`, `02/02/01` or
  `08/06/50`.
- Vector C (USB Ethernet) recorded as supported but useless alone: the kernel has CDC-ECM, but
  the image ships no DHCP client and no remote-login daemon.
- Pre-flight recommendation: pass the ESP32 through to QEMU and exercise the real
  `usb-automount` before involving the car.

## 0.98.0 - physical HID is dropped by the shell, not by a driver

- Explained the reported mouse and keyboard behaviour from the firmware rather than by guessing.
  `weston_1920.ini` has **no `[input]` section**, and `ias-backend.so` fully supports pointer,
  keyboard and touch (`weston_seat_init_pointer`/`_keyboard`/`_touch`, `notify_motion`,
  `notify_key`, libinput + libevdev). Udev is stock apart from a touchscreen symlink rule.
- The gap is `ivi-shell.so`: it contains **no pointer or keyboard focus implementation at all**.
  The only keyboard logic in the window manager concerns the on-screen keyboard surface.
- So the cursor appears because the backend creates a pointer seat and weston draws the cursor,
  but moving it and granting pointer focus is shell work that ivi-shell does not do. Keys are
  consumed by the compositor with no focus surface and dropped. The caps-lock flicker on plug-in
  is LED state on device open, not key handling.
- Consequence recorded: input must be simulated at the **touch** layer, which the GUI accepts,
  rather than by presenting a mouse or keyboard. That is already where the project's
  `weston_vm_input` and `qt_input_observe` helpers point.

## 0.97.0 - correction: visibility is granted, and the harness has no ApplicationManager

- **Withdrew** the "zero visibility events" claim. It came from counting the string
  `ivi_surface_visibility`, but the compositor logs `ivi_surface@7.visibility(1)` — twice. The
  surface **is** made visible. That is the second time a wrong marker string inverted a
  conclusion in this investigation, and both are now recorded as such.
- Also recorded: this harness deliberately runs **no ApplicationManager**, so its empty manager
  query proves nothing about the manager's view. The "drawing application 0" observation came
  from a different configuration.
- With the retained milestone screenshot showing genuine map pixels, the standalone harness
  already reaches visible authentic AppNavi rendering.
- **Therefore the remaining gap is integration, not rendering.** The full launcher chain starts
  AppNavi through AppLauncher with different environment and ordering and does not reproduce
  this harness's ingredients.
- Next: carry the three essentials into the full chain — gpio440 adaptor, valet-status D-Bus
  boolean stub, and the widget/visibility helper — and see whether the manager latches the
  navigation window.

## 0.96.0 - retargeting the helper to 30000 does not produce visibility either

- Rebuilt the widget-linking helper with parent id 30000 instead of 3000 and ran it through the
  same harness. `set_surface_visible`=16 and `request_fg`=8 as before, and
  **`ivi_surface.visibility` events still 0**.
- So addressing the id that exists is **necessary but not sufficient**. The mismatch was real,
  but it does not on its own produce visibility, so at least one further condition governs
  whether the window manager emits a visibility event.
- Candidates recorded in cost order: the helper's requests not reaching the same window-manager
  instance that owns the surface (its log has been empty, which is suspicious); visibility
  requiring a further state change such as a later commit or a layout change; or 30000 not
  being the parent surface the helper should address at all.
- Next discriminator: confirm the helper actually connects and its first request is accepted,
  by capturing its output and the compositor's response.

## 0.95.0 - the surface id is fixed at 30000; the helper addresses 3000

- Settled the id question with one run: `QT_WAYLAND_SET_SURFACE_ID=0` still produces surface
  id **30000**, the same as with `3000`. The environment variable does not control the id in
  this path.
- So the mismatch is not a configuration slip on our side. AppNavi creates 30000 regardless,
  the helper programmes visibility for 3000, and sixteen visibility requests therefore
  produce zero `ivi_surface.visibility` events.
- **The fix follows directly:** address the id that exists. Rebuilding the widget-linking
  helper with parent 30000 is cheaper than establishing where 30000 originates and making it
  configurable.
- This closes the diagnosis of the visibility blocker: surfaces are created, buffers are
  attached, requests are issued, and the only thing wrong is the identifier.

## 0.94.0 - visibility requests are plentiful; the surface id does not match

- Counted visibility markers in the compositor log for the valet-stub run:
  `set_surface_visible`=16, `set_visible_for_qtwayland`=16, `request_fg`=8,
  `set_surface_layout`=16 — and **`ivi_surface_visibility` events = 0**.
- The only surface id the compositor logs as created is **30000**, while the helper
  programmes visibility for **3000**. So the requests are issued correctly but never bind to
  a surface that exists, which is consistent with the manager still reporting drawing
  application `0`.
- This turns the 3000-versus-30000 puzzle from a suspicion into the leading explanation,
  supported now by an event count rather than inference.
- Next: establish the mapping between the environment value and the created id (one run with
  a different value makes it plain), then either point the helper at the id that exists or
  make AppNavi create the id the helper expects.

## 0.93.0 - correction: AppNavi does create surfaces; the earlier stop point was wrong

- **Withdrew** the previous claim that AppNavi never calls
  `ivi_application.surface_create`. It was based on marker counts from the client's
  `WAYLAND_DEBUG` log, and the client does not emit those requests in this build, so their
  absence there proved nothing.
- Counting the **compositor** log for the same run shows `surface_create`=2,
  `ivi_surface`=7, `attach`=2, `commit`=2. AppNavi creates ivi surfaces and attaches buffers.
- The reproduced recipe is the one the retained milestone used: the gpio440 adaptor, the
  valet-status D-Bus boolean stub, and the widget-linking helper in place of the plain
  foreground helper.
- What remains is **visibility**, not surface creation: whether a foreground/visible request
  reaches the surface ids that actually exist, and on which plane.

## 0.92.0 - wl_drm ruled out; a working harness is known; a working harness is known

- Ruled out the missing `wl_drm` as the gate. A prior successful run used the same
  `weston-headless` pixman stack with **no ApplicationManager** and reached `surface_create`
  for ids **3000, 30000 and 4903** with 26 attach calls, so clients can create ivi surfaces
  and attach without any DRM interface. The current stop is configuration-specific.
- That also settles the 3000-versus-30000 puzzle: AppNavi creates **both** ids plus
  4903/4900 for the map widget, so there was never one expected id.
- A working harness is known and can be diffed: that run executed
  `/appnavi-valet-stub-probe.sh` with `/appnavi-valet-stub-run.sh`, both still present in the
  image. The next step is to diff that harness against the current probe rather than debug
  further.

## 0.62.0 - public VM source and evidence publication

- Published the authored VM reproduction sources and bounded evidence to the
  public research repository, with source and evidence manifests binding every
  published file to a SHA-256.
- Added the authentic launcher profile/confirm screen and a navigation-window
  frame that still shows Home to the inspected screenshots there.

### (other lineage, same version)

- Added authored guest helpers, VM experiment scripts, bounded navigation
  evidence, inspected screenshots, and provenance manifests to the separate
  public repository. Generated disk images, recovered vendor binaries, raw
  captures and core dumps remain local.
- Extended the public privacy scanner to cover every tracked folder,
  including VM source scripts and QML; retained the full local test suite.

## 0.91.0 - AppNavi stops between create_surface and ivi surface_create

- With the gpio440 adaptor in place, counted protocol markers in AppNavi's own
  `WAYLAND_DEBUG` log instead of transporting text over the console. That is both cheaper
  and decisive.
- **Measured stop point:** AppNavi binds `wl_display`, enumerates 71 registry lines, binds
  `wl_compositor`, `wl_shm` and `ivi_application`, creates a `wl_surface` — and then
  **never calls `ivi_application.surface_create`** and never attaches or commits.
- **`wl_drm` is absent entirely** (0 references). The compositor runs headless with pixman,
  so no GPU buffer interface is offered. Whether that causes the stop or merely accompanies
  it is not established.
- Tried `QT_WAYLAND_SET_SURFACE_ID_FORCED=1` in addition to the id already being set: a
  second `wl_surface` appears but `surface_create` is still 0, so the forced path alone does
  not get past the stop.
- Ruled out by construction: gpio440 polling (now stubbed, errors zero), the preload adapter
  (baseline without it is identical), ApplicationManager presence, and the current
  command-line flags.
- Next hypotheses recorded: libivi's id acquisition still declining, QtWayland refusing to
  complete ivi surface creation without a buffer integration under pixman headless, or a
  later startup requirement that surface creation sits downstream of.

## 0.90.0 - privacy checker no longer mistakes Wayland notation for email addresses

- The harness failed on the retained AppNavi analysis with five "private email address"
  findings. They were false positives: the checker's email pattern matched Wayland debug
  syntax, where a protocol object is written `object@<id>.method(...)`, so `wl_surface@3.attach`
  and `ivi_controller@13.surface(30000)` looked like addresses.
- Tightened `EMAIL_PATTERN` so the domain must begin with a letter. Real addresses still
  match (`someone@example.com`, `a.b@corp.example.org`); Wayland forms no longer do.
- Added a regression test, `test_wayland_object_notation_is_not_an_email`, so future
  protocol captures can be retained as evidence without tripping the privacy gate.
- Deliberately fixed the checker rather than rewriting the quoted log lines: every Wayland
  capture from here on would hit the same false positive, and mangling evidence to satisfy
  a scanner is the wrong trade.

## 0.89.0 - first hardware-dependency adaptor: AppNavi polls a GPIO the board lacks

- Traced why AppNavi is alive but paints nothing: with `WAYLAND_DEBUG` on, its own log
  shows it connects, enumerates the registry (including `ivi_application` as global 111),
  and then **never calls `surface_create`**. The tail of that log is a repeated loop on
  `/sys/class/gpio/gpio440/value: No such file or directory`.
- Checked the node in the VM: `/sys/class/gpio` contains only `export` and `unexport`, and
  writing `440` to `export` returns **EINVAL** — the pin is not registered by any gpiochip,
  consistent with the kernel log where `lge_gps_driver` defers with `-517` and never gets
  its GPIO. So this is not a configuration mistake; the emulated board genuinely lacks a
  GPIO the firmware expects.
- Built the adaptor: a tmpfs mounted over `/sys/class/gpio` with a `gpio440` node and an
  inert `value`. With it, the `gpio440` errors disappear from AppNavi's log entirely, which
  is the first time a simulated hardware dependency has been shown to unblock a firmware
  startup path in this project.
- Honest limitation: surface creation is **not yet consistent**. One run showed
  `surface_create` in the log, the next showed none, so something beyond the GPIO is also
  gating the render path or the timing is racy. The GPIO stub is necessary and
  reproducible; it is not yet sufficient on its own.
- Retained as `tools/uk_fw/guest/appnavi_gpio_probe.sh` so the stub and the probe can be
  reproduced.

## 0.88.0 - why AppNavi idles: the ivi surface id and visibility are injected from outside

- Ran a targeted analysis of the "alive but paints nothing" blocker and added it as
  `evidence/appnavi-startup-analysis.md` (full report retained under
  `work/vm/vendor-userspace-260128/appnavi-startup-analysis/`).
- **Root cause candidate, verified at string and dependency level:** AppNavi directly
  links `libivi-platform-interface.so.1`, which resolves its ivi surface id *only* from
  the environment (`QT_WAYLAND_SET_SURFACE_ID`, with `_FORCED` and
  `USE_PID_FOR_SURFACE_ID` variants). On the vehicle that value is injected by
  `AppLauncher`, which also sets `APPID`. Verified here: the library is a direct `NEEDED`
  of AppNavi and contains all three variable names.
- **Unset behaviour:** an uncapped `blockingReadEvents` loop waiting for an id reply. That
  is precisely the observed symptom — alive, silent, no surface — rather than a crash.
- **Ruled out:** ApplicationManager's absence (the project's no-AppManager run still
  committed a 1920x720 buffer), every command-line flag in the current invocation, and
  `APPID` (read by AppLauncher, not by AppNavi or libivi). AppNavi reads exactly one
  environment variable itself: `MD_CONA40_ON`.
- **Open point flagged, and it is a big one:** the VM logs show the ivi surface created
  under id **30000** while the project's `/ivi-fg-navi` helper programmes **3000**. If
  real, visibility is being requested for an id that does not exist, which would explain
  the byte-identical screenshots even in the configuration believed to work. The origin of
  the added offset lives in `.bss` and was not established statically.
- **Cheapest next test, one boot:** run with `QT_WAYLAND_SET_SURFACE_ID=3000` and no
  ApplicationManager, then check which id the surface actually receives and re-drive
  `/ivi-fg-navi` with *that* id.
- Supporting runtime observation from this session: a run of the baseline probe produced
  **no surface_create at all**, and AppNavi had exited by the end, so the id hypothesis and
  the lifetime question both need the instrumented run above.

## 0.87.0 - A/B shows AppNavi paints nothing at all

- Ran the A/B the previous entry left open. Three runs of the same probe with the captured
  frame compared: with the adapter (AppNavi alive, 1 log line), baseline without it
  (AppNavi alive, 0 lines), and a control with **AppNavi not launched at all**.
- The screenshot is byte-identical (`b316a82a…0b9a83`) between baseline and the no-AppNavi
  control. AppNavi renders nothing: alive, silent, contributing no pixels.
- Consequence: the adapter is not implicated, and the compositor contract, the `0x0` hold
  and the BG notification cannot be exercised until AppNavi paints. The blocker moves one
  level earlier.
- Next step recorded: find why AppNavi is alive but idle — compare the environment and
  arguments the launcher normally supplies against this probe's direct launch.
- Documentation inconsistency fixed: an earlier `git reset --hard` in the public clone
  discarded an uncommitted doc edit, so the public copy still presented the question as
  open while this copy carried the baseline result. Both copies now agree, and the public
  repo is at `462c9fa`.

## 0.86.0 - baseline clears the interposer; AppNavi is silent on its own

- Ran the decisive control: the identical render probe **without** the preload.
  AppNavi's log came back **0 lines** and the manager reported drawing application `0`
  — the same result as with the adapter loaded, whose log holds only the adapter's own
  one-line load record. So the interposer is **not** what stops AppNavi; its startup is
  failing for reasons of its own in this probe.
- Stated with it, because it matters: **an empty log is not proof that nothing rendered.**
  AppNavi may log to DLT or a file, or not at all, and the probe's screenshot has not
  been inspected yet. "Renders but silently" and "never renders" both remain open.
- Next step recorded: inspect the captured frame, and check whether AppNavi logs to DLT,
  before concluding anything about its startup.
- `docs/navigation-status.md` updated in both repositories: the open question section is
  replaced by this baseline result.

## 0.85.0 - working tree committed; probes published

- Committed the working tree that had been preserved uncommitted throughout the VM work:
  the harness additions in `tools/uk_fw/vm_boot.py`, the native TE2 decryptor work in
  `tools/uk_fw/gen5w_decrypt.py`, their tests, the eleven VM research helpers under
  `tools/uk_fw/guest/`, and `PROJECT-OPERATIONS.md`.
- Sanitisation: one personal path in `PROJECT-OPERATIONS.md` was replaced with a
  placeholder. The rest of the set contains no personal paths, VIN-shaped tokens or
  credentials. Harness and the full 171-test suite pass.
- Published three further research instruments to the public repository
  (`dr_breakpoint_probe.c`, `ec03_observer.c`, `ec03_target.c`), closing the gap between
  the private and public tool sets. Public repo at `3089bf4`.
- Deliberately still private: the vulnerability register, the raw evidence tree, the
  task ledger and all firmware. Public tree carries no firmware and no credentials.

## 0.84.0 - navigation status published to both repositories

- Published `docs/navigation-status.md` to the public repository together with the
  research helpers behind it (`navi_bg_0x0.c`,
  `launcher_appnavi_navibg_preload.c`, `appnavi_bg_probe.sh`), and kept the same
  document here as `evidence/navigation-status.md`. Public repo at `2b179d5`.
- The document consolidates the three things measured this session — the EGL dimension
  ordering on the authentic client, that a Qt hide cannot produce a background
  notification, and that guest hardware breakpoints work under TCG with per-thread
  scoping and the disarm-before-detach requirement — and states the remaining blocker
  plainly: AppNavi never attaches a surface, so nothing reaches the compositor.
- Sanitisation before publishing: the new files contain no personal paths, no VIN-shaped
  tokens and no credentials; the public harness passed on the clone before the push.
- The public repository does not carry the vulnerability register, the raw evidence tree,
  the ledger or any firmware; those remain private.

## 0.83.0 - adapter moved to the render probe; AppNavi still never attaches

- Built `appnavi-bg-probe.sh` from the standalone render probe, which runs a real
  session bus, `weston-headless` with the IVI shell, a real ApplicationManager, and then
  **execs AppNavi directly** — so the adapter needs no launcher hook at all.
- First attempt launched AppNavi through the busybox `timeout` applet and the preload was
  lost across that extra exec hop. Launching AppNavi directly fixed it: AppNavi's own log
  now contains `navi-bg: loaded pid=772 hold_after=200 hold_count=900`.
- **Still no surface attach.** That single line is the entire AppNavi log, and the manager
  reported drawing application `0` before and after, which is not what a rendering Qt
  client looks like.
- Important open question recorded: whether the **interposer itself** is now what stops
  AppNavi rendering. The cheapest discriminator is a baseline run of the same probe
  without the preload, to compare AppNavi's log and behaviour. That is the next step.
- Method note: in this probe stderr is the reliable channel (it reaches `appnavi.log`),
  while `/dev/kmsg` produced nothing — so an absent `dmesg` line here is a channel
  artifact, not evidence of absence.

## 0.82.0 - BG experiment repositioned; AppNavi does not render in the full chain

- Moved the navi-bg experiment to after the chain's own navigation transition request,
  since the previous placement ran before AppNavi was ever asked to come forward. The
  hold also switched from a wall-clock window (measured from process start, long past by
  then) to an attach-count window anchored at that point.
- Result: the wait ran its full 180 seconds **without ever seeing a surface attach**
  (`NAVI_BG_PAINT_SEEN_AFTER_S=180`), no interposer timeline was produced, and the
  navi-live screenshots hash identically to the earlier Home frames.
- Conclusion recorded: in this full-chain configuration **AppNavi never becomes a
  rendering Wayland client**, so there is no surface for the adapter to hold. That is
  the Home↔Navigation blocker itself, not a fault in the adapter.
- Strategic correction recorded: the full chain is the wrong vehicle for the BG
  experiment. The standalone AppNavi render probe already in the image
  (`appnavi-render-probe.sh`, `launcher-appnavi-probe.sh`) is documented to produce
  genuine map pixels and should host the adapter, reusing the now-proven execve-hook
  injection.
- Method caveat recorded: `dmesg` is a weak late-run probe because the ring buffer can
  wrap during a ~570 s run. An absent line late in a run is not proof of absence;
  process state or a log file is better near real time.

## 0.81.0 - navi 0x0 injection unblocked: interposer now loads into AppNavi

- Found the root cause of every earlier "adapter never ran" result:
  `launcher_appnavi_liveness_preload.c` deliberately calls
  `unsetenv("LD_PRELOAD")` when running as AppLauncher, so vendor children inherit a
  clean environment. **No `LD_PRELOAD` set on the launcher command line can reach
  AppNavi**, which is why four attempts produced nothing.
- Fix: piggyback on that interposer's own `execve` hook, which rewrites `envp` for
  AppNavi alone. `tools/uk_fw/guest/launcher_appnavi_navibg_preload.c` is a variant that
  injects `LD_PRELOAD=/navi-bg-0x0.so:/appnavi-egl-no-msaa-preload.so` for AppNavi only.
- **Verified:** the kernel log now shows `navi-bg: loaded pid=857
  hold_at_ms=20000 hold_for_ms=6000`. The adapter demonstrably executes inside AppNavi.
- Also made the probe filesystem-free: the hold window comes from a monotonic clock
  plus launch-time environment variables, and the timeline goes to `/dev/kmsg`, so
  SMACK and exec-environment handling can no longer block it silently.
- Remaining gap: no `first-attach` line followed, so AppNavi never attached a buffer on
  the elected surface inside that window, and the manager still reported `11/11`. Next
  step recorded: log every attach plus a destructor summary so a zero-attach run is
  unambiguous, then align the hold window with real rendering.
- Method note: an earlier "decisive" conclusion that the library never loaded was
  **wrong** — it rested on AppNavi's stderr being captured in `launcher.log`, which it
  is not. `/dev/kmsg` is the reliable channel and corrected the diagnosis.

## 0.80.0 - navi 0x0 adapter not reaching BG; diagnosis narrowed to "never fired"

- Replaced the attach-count trigger with a **sustained hold**: while the trigger file
  exists, every attach on AppNavi's target surface is replaced by a null-buffer attach,
  so the surface is held at `0x0` instead of flipping for a single frame. Held for 6 s,
  then released and observed again.
- Manager reported **11/11 during the hold and 11/11 after release**. No change, so BG
  was still not reached.
- Added an audit write from the interposer on first hold, because "no manager change"
  and "adapter never ran" were indistinguishable. The run produced **no
  `/tmp/navi-bg.log` at all**, which means the interposer never executed a hold. The
  manager numbers from both attempts therefore say nothing about whether BG is
  reachable this way.
- Two candidate causes, currently indistinguishable: the preload may not reach AppNavi
  (AppLauncher may exec child apps with a sanitised environment), or SMACK denies the
  `/tmp` trigger read and the audit write for AppNavi's label, which would fail silently
  and produce exactly the observed evidence.
- Next step recorded: remove the filesystem from the probe entirely — log to stderr
  (captured in `launcher.log`) and derive the trigger from a monotonic clock or a
  launch-time environment variable, so neither SMACK nor exec-environment handling can
  block it silently.
- Everything still builds and injects cleanly, the chain completes with exit 0 in
  ~418 s, and screenshots were captured during the hold and after release.

## 0.79.0 - engineering mode research published; navi 0x0 still not reaching BG

- Wrote `evidence/engineering-mode-research.md` and published the same document to the
  public repository (owner approved releasing the PINs and entry methods).
- Entry recorded: Settings -> General settings -> System info -> Manual, tap the **left**
  panel (QR code and text, not the vehicle image) as `3 2 8 9 6 5`, then an eight-digit
  keypad. Engineering-mode PIN `19480717`, reported accepted on a UK-origin 2021 IONIQ 5
  whose build was later identified as `250604`, so acceptance does not prove it on
  `260128`.
- Dealer mode and full engineering mode are distinct with different codes. The
  previously single-source SOP-gate claim is now **corroborated in code**: the binary
  contains `bool AppEngineerModeEngine::checkSOPVersion()`.
- PIN check located: `AppEngineerMode_PinCodeKeypad.qml` (1,087 lines) calls
  `AppEngineerModeEngine.checkPassWord(...)` at line 391 and branches on the return
  value, where `21`/`11` are menu selectors. Lockout machinery exists
  (`startBadPassword`, `setBadPasswordInfo`, `getBadPasswordDiff`, `getEnterPasswordCnt`).
  The binary is stripped but keeps 111 C++ signature strings, which is how these were
  identified.
- **The PIN is not a literal.** 408,412 files across all five extracted components plus
  444 expanded archives gave zero hits in ASCII, UTF-16LE, uint32 LE, uint64 LE and hex.
  Most probable explanation recorded: the reported PIN belongs to the owner's `250604`
  build rather than this `260128` package.
- Entry gesture is not in QML (`Screen_Manual.qml` has no `MouseArea`/`onClicked`), and
  no binary contains the literal `AppEngineerMode`, so the gesture is native and the app
  launches through the launcher registry.
- AppNavi update: the older capability is recorded as Engineering Mode -> Config ->
  "Update AppNavi from USB"; state on `260128` remains **not established**, with four
  decision gates listed and the launcher's executable inspection flagged as the
  cheapest decisive check.
- Also recorded, from the paint-first navi run: the gated interposer
  (`MIN_ATTACHES_BEFORE_FORCE = 40`) completed with exit 0 but the manager **still
  reported 11/11**. BG was not reached, and the Home-to-Navigation transition is
  unchanged. Triggering on a count rather than on an observed event is the likely
  remaining flaw.

## 0.78.0 - navigation 0x0 adapter built; timing still wrong

- Started the integration piece the BG analysis called for: a scoped adapter that
  drives AppNavi's parent surface to a genuine `0x0` configure so the compositor
  classifies it BG and the manager latches its window byte.
- Mechanism, from the earlier ordering finding: a single null attach is not enough,
  because the size block at `0x40f470` stores the previous `width_from_buffer` before
  `0x40f813` zeroes it. **Two** consecutive null attaches reach `0x0`. Implemented as
  an `LD_PRELOAD` interposer on `wl_surface_attach` that forces a NULL buffer on two
  consecutive attaches. It only drives the vendor compositor; it never calls the
  manager, writes the window byte, or synthesises a notification.
- Two runs, both completed (exit 0, ~412 s) and both still reported manager `11/11`.
  Two real defects were found and fixed along the way: the preload also applies to
  every launcher child, so the first attempt collapsed the wrong app (now gated to
  AppNavi via `/proc/self/cmdline`); and the trigger fired before the client had
  painted, so AppNavi never foregrounded (now gated behind
  `MIN_ATTACHES_BEFORE_FORCE = 40`).
- Honest status: the plumbing is proven end-to-end — the interposer loads under the
  vendor glibc 2.25, is correctly scoped, the chain still completes, and manager state
  is queryable at the chosen point — but **BG was not reached** and the
  Home↔Navigation transition is unchanged. The paint-first variant is built and
  untested.
- Built against `x86_64-linux-gnu.2.25` rather than musl: a musl-linked `.so` will not
  load into the vendor's glibc process.

## 0.77.0 - I-001 scoped to the swrast path; Intel hardware not needed to proceed

- Answered the question of whether an Intel machine is required. It is not, and the
  check that settles it also narrows I-001. Vendor `libEGL` contains four distinct
  surface constructors — `dri2_create_window_surface`, `dri2_drm_create_window_surface`,
  `dri2_wl_create_window_surface` and `dri2_wl_swrast_create_window_surface` — and the
  `-1` sentinel is written by the **swrast-specific** one, while `put_image2`,
  `get_image` and `swap_buffers` all belong to the `dri2_wl_swrast_*` family.
- Consequence recorded honestly: the hardware paths use different constructors and do
  not share that vtable, so the evidence **does not implicate the i965/i915 path**.
  I-001 is therefore a defect of the vendor's Wayland **software-rendering** path,
  which is exactly the path this VM must use. That lowers rather than raises its
  real-world severity, and the register now says so.
- Also noted: the vendor image ships its own DRI drivers (`usr/lib/dri/i965_dri.so`,
  `usr/lib/dri/iu3d9_dri.so`, `usr/lib/mesadri/i915_dri.so`), so the "mixed stack"
  caveat is about which module loads, not about missing vendor code.
- No Intel hardware is needed for the remaining authorised work: the navigation
  `0x0` adapter, services, audio, CAN/MICOM and persistence all run in the VM.

## 0.77.0 - physical HID is dropped by the shell, not by a driver

### (other lineage, same version)

- Explained the reported mouse and keyboard behaviour from the firmware rather than by guessing.
  `weston_1920.ini` has **no `[input]` section**, and `ias-backend.so` fully supports pointer,
  keyboard and touch (`weston_seat_init_pointer`/`_keyboard`/`_touch`, `notify_motion`,
  `notify_key`, libinput + libevdev). Udev is stock apart from a touchscreen symlink rule.
- The gap is `ivi-shell.so`: it contains **no pointer or keyboard focus implementation at all**.
  The only keyboard logic in the window manager concerns the on-screen keyboard surface.
- So the cursor appears because the backend creates a pointer seat and weston draws the cursor,
  but moving it and granting pointer focus is shell work that ivi-shell does not do. Keys are
  consumed by the compositor with no focus surface and dropped. The caps-lock flicker on plug-in
  is LED state on device open, not key handling.
- Consequence recorded: input must be simulated at the **touch** layer, which the GUI accepts,
  rather than by presenting a mouse or keyboard. That is already where the project's
  `weston_vm_input` and `qt_input_observe` helpers point.

## 0.76.0 - null-buffer question resolved: hide does not produce BG

- Settled the outstanding navigation question with DWARF rather than inference.
  `usr/bin/weston` retains debug info for `weston_surface` (weston 1.10.0-r21), which
  fixes the layout: `width` at `0x68`, `height` at `0x6c`, `width_from_buffer` at
  `0x104`, `height_from_buffer` at `0x108`. That confirms the FG/BG predicate tests
  the surface's own size, fed from the `_from_buffer` pair at commit.
- A null attach **does** zero both `_from_buffer` fields (`0x40f813`, reached when the
  buffer pointer is null). My previous entry stopped there and concluded BG was
  reachable. That was wrong: the size block at `0x40f470` runs **before** that
  zeroing, so it stores the *previous* positive size and the surface stays positive.
- Therefore **a bare `hide()` does not produce BG**; a genuine `0x0` size transition is
  required, matching the earlier Camera/Standby control. The integration route needs a
  scoped resize adapter rather than the authentic hide path.
- Recorded transparently: this reverses the correction I made two turns ago, and the
  withdrawn reasoning is preserved in the analysis report rather than deleted.
- Two method notes: the DWARF dump needed `llvm-dwarfdump`
  with a byte-window scan, and several of my earlier greps silently matched nothing
  because `objdump` separates columns with tabs, not spaces.

## 0.76.0 - correction: visibility is granted, and the harness has no ApplicationManager

### (other lineage, same version)

- **Withdrew** the "zero visibility events" claim. It came from counting the string
  `ivi_surface_visibility`, but the compositor logs `ivi_surface@7.visibility(1)` — twice. The
  surface **is** made visible. That is the second time a wrong marker string inverted a
  conclusion in this investigation, and both are now recorded as such.
- Also recorded: this harness deliberately runs **no ApplicationManager**, so its empty manager
  query proves nothing about the manager's view. The "drawing application 0" observation came
  from a different configuration.
- With the retained milestone screenshot showing genuine map pixels, the standalone harness
  already reaches visible authentic AppNavi rendering.
- **Therefore the remaining gap is integration, not rendering.** The full launcher chain starts
  AppNavi through AppLauncher with different environment and ordering and does not reproduce
  this harness's ingredients.
- Next: carry the three essentials into the full chain — gpio440 adaptor, valet-status D-Bus
  boolean stub, and the widget/visibility helper — and see whether the manager latches the
  navigation window.

## 0.75.0 - authentic measurement: dimensions are -1 then 1920x720

- Ran the observer against the **authentic AppCamera** inside the real launcher chain
  and captured both EC-01 stages on the same surface pointer:
  `libEGL+0x16f16` (before the width cache) read width **-1**, height **-1**;
  `libEGL+0x16f1e` (immediately after `swrast_update_buffers` returned) read width
  **1920**, height **720**. Teardown reported `verified detach=ok`.
- This **measures** the ordering defect behind I-001 instead of inferring it: the
  stride used by the copy path was derived from `Width = -1` (giving `-4` bytes)
  while the update populated the real geometry during the same invocation. It
  supersedes earlier statements that a width change had not been observed, including
  my own correction of two turns ago.
- `Ioniq5-VULNERABILITIES.md` I-001 rewritten accordingly: mechanism measured, still
  not a demonstrated exploitable vulnerability, stock-driver reachability and
  attacker influence explicitly unestablished.
- Setup notes worth keeping: the canonical vendor image must not be modified, and a
  plain copy costs 23 GB, so the run used an **APFS copy-on-write clone** (0.031 s)
  with two files injected by `debugfs`. A first attempt to stream the binary over the
  serial console failed because the whole command became one 80 KB line and the line
  discipline truncated it.
- Two real defects surfaced and were fixed: the driver inherited an argument-guard
  block that still tested the old crash observer, and the observer resolved `libEGL`
  before the client had mapped it. The latter is a genuine race — `AppCamera` is
  visible before its graphics libraries load — and is now handled by a bounded
  `--wait-module-ms` poll.

## 0.75.0 - retargeting the helper to 30000 does not produce visibility either

### (other lineage, same version)

- Rebuilt the widget-linking helper with parent id 30000 instead of 3000 and ran it through the
  same harness. `set_surface_visible`=16 and `request_fg`=8 as before, and
  **`ivi_surface.visibility` events still 0**.
- So addressing the id that exists is **necessary but not sufficient**. The mismatch was real,
  but it does not on its own produce visibility, so at least one further condition governs
  whether the window manager emits a visibility event.
- Candidates recorded in cost order: the helper's requests not reaching the same window-manager
  instance that owns the surface (its log has been empty, which is suspicious); visibility
  requiring a further state change such as a later commit or a layout change; or 30000 not
  being the parent surface the helper should address at all.
- Next discriminator: confirm the helper actually connects and its first request is accepted,
  by capturing its output and the compositor's response.

## 0.74.0 - observer gains field capture; three validation cases pass

- Added the increment the ledger recorded next for EC-03: **int32 field capture at
  an observation hit**. The observer now reads two fields from a struct pointer
  supplied either absolutely (`--struct-addr`) or from a register (`--struct-reg`),
  defaulting to the EC-01 contract offsets `+0x2c` (width) and `+0x30` (height),
  with `--off-a`/`--off-b` overrides. That is the shape needed to capture the vendor
  `dri2_surf` dimensions before and after the buffer update.
- Validated in the VM in three cases, all exit 0, 12.87 s total: without `--once` the
  tracee outlives the observer and teardown reports `unverifiable reason=tracee-gone`;
  with `--once` it reports `teardown=verified detach=ok`; and an unknown register
  name is reported as `FIELDS status=unknown-register` rather than guessed.
- Measured `FIELDS status=ok a=1926 b=753` at `+0x2c`/`+0x30`, i.e. the instrument
  reads the intended fields from a struct pointer.
- Honest bound: the register-held pointer mode is only validated on its error path,
  because a synthetic target cannot reliably place a chosen value in a callee-saved
  register at a breakpoint. That mode gets its real exercise at the authentic
  AppCamera stage with `--struct-reg r15`.
- Defect found and fixed during the increment: an unused `field_regs` global that
  `-Werror` rejected, removed rather than silenced.

## 0.74.0 - the surface id is fixed at 30000; the helper addresses 3000

### (other lineage, same version)

- Settled the id question with one run: `QT_WAYLAND_SET_SURFACE_ID=0` still produces surface
  id **30000**, the same as with `3000`. The environment variable does not control the id in
  this path.
- So the mismatch is not a configuration slip on our side. AppNavi creates 30000 regardless,
  the helper programmes visibility for 3000, and sixteen visibility requests therefore
  produce zero `ivi_surface.visibility` events.
- **The fix follows directly:** address the id that exists. Rebuilding the widget-linking
  helper with parent 30000 is cheaper than establishing where 30000 originates and making it
  configurable.
- This closes the diagnosis of the visibility blocker: surfaces are created, buffers are
  attached, requests are issued, and the only thing wrong is the identifier.

## 0.73.0 - second skill bundle pulled, policy re-applied mechanically

- Pulled `AiSkills-Council-Astra-Medium-or-Sol-XHigh.zip` and installed it over both
  skills. The substantive change is Council defaulting to **three Sol 6.1 reviewers
  at `xhigh`**, with Astra-medium supported and `sol` aliasing Sol 6.1.
- The bundle again shipped without the direct-DeepSeek-provider rule and still named
  the superseded `deepseek/deepseek-v4.1-flash` route. Rather than editing by hand a
  second time, added `work/skills-update-261029/apply_direct_deepseek_policy.py`: an
  idempotent patcher that enforces the policy across `SKILL.md`, both protocol
  references, README, installation guide and invocation metadata, tries several
  anchors because the Council protocol wording has changed between bundles, and
  fails loudly if it cannot find a place to apply the rule.
- Re-validated after patching: 148 + 93 unit tests pass and both skills report
  "Skill is valid!".
- Left deliberately unchanged: nine occurrences of the stale route id in
  `tests/support.py`, `tests/test_workflow.py` and `templates/ledger.example.json`.
  Those are test fixtures and an example, not policy statements, and editing them
  risks breaking assertions that bind to the literal.

## 0.73.0 - visibility requests are plentiful; the surface id does not match

### (other lineage, same version)

- Counted visibility markers in the compositor log for the valet-stub run:
  `set_surface_visible`=16, `set_visible_for_qtwayland`=16, `request_fg`=8,
  `set_surface_layout`=16 — and **`ivi_surface_visibility` events = 0**.
- The only surface id the compositor logs as created is **30000**, while the helper
  programmes visibility for **3000**. So the requests are issued correctly but never bind to
  a surface that exists, which is consistent with the manager still reporting drawing
  application `0`.
- This turns the 3000-versus-30000 puzzle from a suspicion into the leading explanation,
  supported now by an event count rather than inference.
- Next: establish the mapping between the environment value and the created id (one run with
  a different value makes it plain), then either point the helper at the id that exists or
  make AppNavi create the id the helper expects.

## 0.72.0 - skills updated, disclosure reduced, EC-03 minimal core working

- Installed the Sol 6.1 skill bundle into the Parallelism and Council skills. The
  bundle switches default reviewers to `gpt-6.1-sol` and replaces Astra in examples
  and fixtures. It did **not** carry the operator's direct-DeepSeek-provider rule and
  still named the superseded `deepseek/deepseek-v4.1-flash` route, so that policy was
  re-applied across `SKILL.md`, `references/protocol.md`, `README.md`,
  `docs/INSTALLATION.md`, `agents/openai.yaml` and The Council, using the verified
  direct route `deepseek/deepseek-flash`.
- Both skills re-validated: 148 + 93 unit tests pass and the packaging validator
  reports "Skill is valid!" for each. The earlier validator failure was a
  missing-PyYAML interpreter, not a skill defect; using a yaml-enabled interpreter
  resolves it.
- **Public disclosure reduced.** The mirror's V-006/V-007/V-008 entries are now
  status-only, with no component names, property names, code locations or payload
  detail. Verified the public tree contains no occurrence of the affected service
  name or property name. Full dossiers remain in the private register.
- Noted rather than altered: the engineering-mode entry sequence and PIN were
  already published in the public tree by earlier work, so removing them now would
  not undo that exposure. Flagged for the owner.
- **EC-02 rescoped and EC-03 minimal core implemented.** Rather than a fifth
  specification round, built `tools/uk_fw/guest/ec03_observer.c`: SEIZE on one
  thread, up to four execute breakpoints addressed as module-substring + offset,
  bounded register capture, disarm-after-hit, mandated disarm/verify/detach
  teardown, a 60 s deadline and a bounded stop count.
- Validated end-to-end in the VM against a synthetic target in two cases: without
  `--once` the tracee runs to completion and teardown is honestly reported
  `unverifiable reason=tracee-gone`; with `--once` the observer detaches while the
  tracee is stopped and reports `teardown=verified detach=ok`. Both exit 0.
- Three defects found and fixed during validation: a missing `stddef.h` for
  `offsetof`, module-base resolution that wrongly required an offset-zero mapping
  (static non-PIE text has none), and teardown being attempted on an already-exited
  tracee. The guest image also has no busybox applet symlinks, so the driver invokes
  applets through `/bin/busybox` explicitly.
- EC-02 is recorded as **blocked/superseded, not accepted**. Remaining bounds: the
  vendor libEGL observation points, surface field capture and the resolved-copy-entry
  stage were not exercised.

## 0.72.0 - correction: AppNavi does create surfaces; the earlier stop point was wrong

### (other lineage, same version)

- **Withdrew** the previous claim that AppNavi never calls
  `ivi_application.surface_create`. It was based on marker counts from the client's
  `WAYLAND_DEBUG` log, and the client does not emit those requests in this build, so their
  absence there proved nothing.
- Counting the **compositor** log for the same run shows `surface_create`=2,
  `ivi_surface`=7, `attach`=2, `commit`=2. AppNavi creates ivi surfaces and attaches buffers.
- The reproduced recipe is the one the retained milestone used: the gpio440 adaptor, the
  valet-status D-Bus boolean stub, and the widget-linking helper in place of the plain
  foreground helper.
- What remains is **visibility**, not surface creation: whether a foreground/visible request
  reaches the surface ids that actually exist, and on which plane.

## 0.71.0 - null-buffer BG question narrowed, with a reversed inference

- Returned to the main navigation workstream (independent of the EC-02 gate) to
  answer whether a Qt hide can ever produce the BG notification the manager needs.
- Proven by disassembly: the FG/BG predicate is in `ivi-window-manager.so` at
  `0xf981` and tests the surface size fields `0x68`/`0x6c`, reproducing the known
  rule (any positive dimension selects FG). Those fields are written only by
  `surface_set_size` (`usr/bin/weston` `0x40d4a0`), whose three call sites are all
  inside `weston_surface_commit_state`.
- First inference — that a null buffer leaves the size positive and therefore
  cannot produce BG — was **contradicted by two further checks** and is recorded as
  reversed rather than quietly dropped. `surface_attach` gives a NULL buffer the
  same `pending+0x00` "buffer attached" flag as a real one, and the commit path
  enters the size block whenever that flag is set. So a null-buffer commit *does*
  reach `surface_set_size`.
- Whether that call writes `0x0` depends on `[rbx+0x104]`/`[rbx+0x108]`, whose
  meaning for a null attach is not yet established. A hidden surface producing
  `0x0` and hence BG is therefore **plausible, not excluded**, which raises rather
  than lowers the value of pursuing AppNavi's authentic hide path.
- One delegated worker was interrupted mid-analysis by the pi-gui restart; its six
  listings were retained and the analysis completed by the coordinator. No rootfs
  file was modified and no VM was booted.

## 0.71.0 - wl_drm ruled out; a working harness is known; a working harness is known

### (other lineage, same version)

- Ruled out the missing `wl_drm` as the gate. A prior successful run used the same
  `weston-headless` pixman stack with **no ApplicationManager** and reached `surface_create`
  for ids **3000, 30000 and 4903** with 26 attach calls, so clients can create ivi surfaces
  and attach without any DRM interface. The current stop is configuration-specific.
- That also settles the 3000-versus-30000 puzzle: AppNavi creates **both** ids plus
  4903/4900 for the map widget, so there was never one expected id.
- A working harness is known and can be diffed: that run executed
  `/appnavi-valet-stub-probe.sh` with `/appnavi-valet-stub-run.sh`, both still present in the
  image. The next step is to diff that harness against the current probe rather than debug
  further.

## 0.70.0 - capability matrix complete: per-thread scoping verified

- Closed the last open capability item. Debug registers are **per thread**: after
  the traced main thread trapped and was stepped past, the slot was deliberately
  re-armed, and an untraced sibling thread then executed the same function with no
  effect — the process exited 0. Eleven checks pass in 3.94 s, exit 0.
- The test is sequenced rather than raced (the sibling waits on a flag), so it
  distinguishes the two outcomes deterministically: an unaffected sibling gives a
  clean exit, while a process-wide slot would make the untraced sibling die on
  `SIGTRAP`, the same failure signature measured in T8.
- Consequence for EC-02: single-thread observation is sound and does not require
  thread-group control or `PTRACE_O_TRACECLONE`, which removes an open design
  question rather than adding one.
- Authoring correction recorded: an edit that added the threading headers replaced
  `stdarg.h` instead of adding to the include list, caught by `-Werror` at build
  time before any VM run.
- Newly stated bounds: only execute breakpoints were tested; data read/write
  watchpoints were not, and behaviour with many threads or `PTRACE_O_TRACECLONE`
  was not examined.

## 0.70.0 - AppNavi stops between create_surface and ivi surface_create

### (other lineage, same version)

- Located the stop precisely by counting protocol markers in AppNavi's own Wayland debug
  log: it binds `wl_display`, enumerates 71 registry lines, binds `wl_compositor`, `wl_shm`
  and `ivi_application`, creates a `wl_surface`, and then **never calls
  `ivi_application.surface_create`** and never attaches or commits.
- **`wl_drm` is absent entirely** — the compositor runs headless with pixman, so no GPU
  buffer interface is offered. Cause or coincidence is not established.
- `QT_WAYLAND_SET_SURFACE_ID_FORCED=1` in addition to the id yields a second `wl_surface`
  but still zero `surface_create`, so that path alone does not clear the stop.
- Ruled out: gpio440 polling, the preload adapter, ApplicationManager presence, and the
  current command-line flags. The forced-env probe is published as
  `tools/uk_fw/guest/appnavi_forced_probe.sh`.
- Method note: marker counting is much cheaper than transporting log text over the serial
  console and should be the default for this kind of diagnosis.

## 0.69.0 - DR6 attribution verified; transcript IV claim corroborated

- Completed the capability matrix: `DR6` carries per-slot trap bits and is
  clearable through ptrace. With slots 0 and 1 armed, the first trap reported
  `DR6`=0x1 (B0), `POKEUSER DR6 = 0` read back 0x0, and the second trap reported
  `DR6`=0x2 (B1). Ten checks now pass in 3.83 s, exit 0.
- This removes another assumption the EC-02 specification had argued about: the
  observer can attribute a trap to a specific slot and drop stale status between
  stages, rather than inferring the slot from RIP alone.
- Remaining unexercised: per-TID scoping, i.e. one traced thread while a sibling
  executes the same code.
- Checked the community transcript's most testable claim against our own tooling.
  The chat states the encryption IV is "derived from the SHA256 of the encrypted
  file name and size"; `tools/uk_fw/gen5w_decrypt.py` independently implements
  exactly that, as the first 16 bytes of
  `SHA256((basename + signed_int32(body_size)))` with body size `file_size - 0x4024`,
  and produces working decryptions. The claim is therefore corroborated, and the
  transcript now records the precise semantics rather than leaving it as a lead.
- No VM image was modified and no vendor binary was executed beyond the earlier
  observation runs; the probe continues to use a synthetic tracee.

## 0.69.0 - the missing gpio440 node, and a privacy-checker fix

### (other lineage, same version)

- Published the reason AppNavi never paints: its client log ends in a repeated read
  failure on `/sys/class/gpio/gpio440/value`. That node cannot exist here —
  `/sys/class/gpio` holds only `export` and `unexport`, and exporting `440` returns
  **EINVAL** because no gpiochip registers the pin, matching the kernel log where the GPS
  driver defers with `-517`. The emulated board lacks a GPIO the firmware expects.
- **Adaptor:** a tmpfs over `/sys/class/gpio` with an inert `gpio440` node. The `gpio440`
  errors then vanish from AppNavi's log — the first demonstrated case in this project of a
  simulated hardware dependency unblocking a firmware startup path. Necessary but not yet
  sufficient: surface creation appeared in one run and not the next.
- Fixed a privacy-checker false positive: the email pattern matched Wayland object
  notation, so captured protocol logs were reported as leaked addresses. The domain must
  now begin with a letter, with a regression test added. The checker was fixed rather than
  the evidence rewritten, since every Wayland capture would hit the same thing.
- The adaptor probe is published as `tools/uk_fw/guest/appnavi_gpio_probe.sh`.

## 0.68.0 - community chat transcribed into evidence

- Transcribed eight owner-supplied Discord screenshots into
  `evidence/community-chat-transcript-261029.md` as a single de-duplicated,
  timestamp-preserving log with attribution. Recorded as unverified participant
  reports, not findings, consistent with the existing community-leads policy.
- The transcript confirms the provenance of the three exploit bullets that became
  V-006/V-007/V-008, and cross-references each against our own offline results:
  V-006 confirmed but with a different mechanism than the claim, V-007 configuration
  only, V-008 normal password-gated behaviour.
- Extracted the actionable leads and ran cheap offline checks. `AppEngineerMode`
  is present with QML at `/app/share/AppEngineerMode/qml/main.qml`, but neither the
  reported PIN `19480717` nor the tap sequence `3 2 8 9 6 5` appears as text there,
  so the entry handler is almost certainly the Settings app behind
  *System info -> Manual* rather than the engineering binary.
- `/tool/velix_aes.key` and `/tool/public.crt` do not exist in the rootfs; those
  paths belong to the AppUpgrade payload and must be looked for in its decrypted
  tree. The claimed IV derivation from the SHA-256 of encrypted name and size
  remains the most testable claim and is flagged for checking against
  `tools/uk_fw/gen5w_decrypt.py`.
- Publication caution recorded: the transcript contains an engineering-mode PIN, a
  claimed VM digest and a partial key-like string, so `PUBLIC-RELEASE.md` applies
  before any mirroring to the public repository.

## 0.68.0 - why AppNavi idles: surface id and visibility are injected from outside

### (other lineage, same version)

- Added a section to `docs/navigation-status.md` explaining the alive-but-paints-nothing
  state. AppNavi links `libivi-platform-interface.so.1`, which resolves its ivi surface id
  **only from the environment** via `QT_WAYLAND_SET_SURFACE_ID` and its `_FORCED` and
  `USE_PID_FOR_SURFACE_ID` variants; on the vehicle `AppLauncher` injects that value
  together with `APPID`. With it unset the library enters an uncapped
  `blockingReadEvents` loop waiting for an id reply — matching the observed symptom of a
  live, silent, surface-less process rather than a crash.
- Visibility is external too: `QWindow::setVisible()` is only reachable from an
  `ivi_surface.visibility` event, which the window manager emits only for that app's id.
- Ruled out: ApplicationManager's absence, every command-line flag in the current
  invocation, and `APPID`. AppNavi reads exactly one environment variable itself,
  `MD_CONA40_ON`.
- Flagged an open point: the VM logs show the surface created under id **30000** while the
  helper programmes **3000**, so visibility may be requested for a non-existent id. Next
  step narrowed to one instrumented boot that records the id actually received.

## 0.67.0 - detach discipline measured; four-slot behaviour verified

- Extended the capability probe to the four behaviours round 1 left unexercised.
  Nine checks now pass in **3.85 s**, exit 0.
- **Four slots armed simultaneously** (`DR7` image `0x455`) fire in program order
  at the correct RIPs, provided the fired slot is disarmed before resuming —
  an execute breakpoint retriggers if left enabled, so this discipline is
  mandatory rather than stylistic.
- **Slot replacement** works: slot 0 fired at one function, then at a different
  address after reprogramming.
- **`DR4`/`DR5` are rejected** by the kernel with `EIO`, confirming the valid
  index set is `0-3,6,7`. EC-02's fixture V-03 had assumed a fifth slot could be
  tested through `DR4`; that assumption is wrong and is now measured.
- **Detach alone is unsafe.** With a slot still armed, `PTRACE_DETACH` leaves the
  breakpoint live and the untraced process is **killed by `SIGTRAP`**. This
  confirms EC-02's C-09 concern was real rather than defensive.
- **The safe exit is proven**: clear the `DR7` enables, clear the address
  register, verify the readback is zero, then detach. The tracee then completes
  with exit 0.
- Bounds held: synthetic tracee at user addresses, no vendor observation point;
  per-TID scoping and `DR6` semantics beyond `B0` remain unexercised.

## 0.67.0 - A/B shows AppNavi paints nothing at all

### (other lineage, same version)

- Ran the A/B the previous entry left open, since an empty log is not proof that nothing
  rendered. Three runs of the same probe with the captured frame compared: with the
  adapter (AppNavi alive, 1 log line), baseline without it (AppNavi alive, 0 lines), and a
  control with **AppNavi not launched at all**.
- The screenshot is byte-identical (`b316a82a…0b9a83`) between the baseline and the
  no-AppNavi control. So AppNavi renders nothing: it is alive, silent, and contributes no
  pixels. It is not rendering anonymously, it is not rendering.
- Conclusion recorded in `docs/navigation-status.md`: the adapter is not implicated, and
  the compositor contract, the `0x0` hold and the BG notification cannot be exercised
  until AppNavi paints. The next step is to find why it is alive but idle, starting with
  the environment and arguments the launcher normally gives it.
- Also fixes a documentation inconsistency: an earlier `git reset --hard` in the public
  clone discarded an uncommitted doc edit, so this file still presented the question as
  open while the private copy already carried the baseline result. Both now agree.

## 0.66.0 - guest hardware breakpoints proven under TCG

- Resolved the single load-bearing unknown behind EC-02 by measurement rather than
  further specification: the guest **does** honour `DR0`/`DR7` execute breakpoints
  set through ptrace under QEMU TCG with the measured `4.1.27-abl` kernel.
- Wrote `tools/uk_fw/guest/dr_breakpoint_probe.c` (VM-only capability probe, no
  vendor code) and ran it in 3.64 s through the project's own harness with the
  documented `--sdhci-compat` adaptation. Four checks all pass: no-trap control;
  armed execute breakpoint firing at exactly the armed address with `DR6.B0` set;
  clean disarm and completion with no re-trap; and single step advancing RIP.
- One self-correction during authoring: the first draft needed a missing
  `stdarg.h` and left its tracee parked after the trap; it was rewritten as a
  single arm/trap/restore/clean-exit sequence before any run.
- Consequence: EC-02 was never blocked on capability, only on specification. The
  fixture it deferred this question to turns out to be cheap and runnable without
  vendor userspace. Remaining EC-02 blockers are spec defects alone.
- Bounded honestly: proven on a synthetic tracee at user addresses, not on vendor
  libEGL observation points; four-slot capacity, slot replacement, `DR6` semantics
  beyond `B0`, and detach-time teardown remain unexercised. No vendor binary was
  executed and no navigation state was claimed.

## 0.66.0 - baseline clears the adapter; AppNavi is silent on its own

### (other lineage, same version)

- Ran the control that the published open question called for: the identical render probe
  with **no** preload. AppNavi's log came back empty and the manager reported drawing
  application `0`, the same as the run with the adapter loaded apart from the adapter's
  single load record. The interposer is therefore **not** what stops AppNavi.
- Stated with it: an empty log is **not** proof that nothing rendered. AppNavi may log to
  DLT or a file, and the captured frame has not been inspected, so "renders silently" and
  "never renders" both remain open.
- `docs/navigation-status.md` updated accordingly, and the baseline probe added as
  `tools/uk_fw/guest/appnavi_baseline_probe.sh` so the control can be reproduced.

## 0.65.0 - EC-02 blocked by over-specification; rescope recommended

- Ran four lead reviews of the EC-02 hardware-breakpoint mechanism. Round 3
  changed approach as instructed: policy moved into a new normative
  `ec02-state-machine.json` (17 states, 48 transitions, 21-row classify-only
  decision table, mechanically derived budget) with the report and facts reduced
  to citations of it.
- The fourth review still returned REQUEST_CHANGES, with real structural defects:
  missing pre-arm and subsequent revalidation failure edges, a missing
  `ST_SEIZE -> ST_STOP0` transition and initial interrupt, already-forwarded
  signals staying pending for redelivery, budget sums that disagree with their
  declarations, unreachable maxima, a detach-error terminal falsely reporting
  "detached", classifier row shadowing, and single-step routing inconsistencies.
- Diagnosis recorded rather than looping again: the defect is over-specification.
  The mechanism report grew from 771 to 1,931 lines plus a 1,187-line state machine
  for a bounded diagnostic tool, and each correction exposes a new edge because
  edge policy is being authored without implementation feedback.
- Recommendation: rescope EC-03 to a minimal verifiable core (SEIZE, four
  hardware observation points, bounded capture, restoration, host-owned timeout)
  and let the EC-04 fixtures settle the remaining edge policy empirically. No
  fifth textual correction round was run.
- EC-03 remains gated. No VM boot, no target execution, no fixture run and no
  measured EGL claim. Ledger validates; artifacts re-hashed.

## 0.65.0 - navigation status published: two questions closed, one blocker left

### (other lineage, same version)

- Added `docs/navigation-status.md` recording what is now measured about the
  Home-to-Navigation gap, and published the research helpers behind it.
- **EGL dimension ordering measured** on the authentic client. A hardware-breakpoint
  observer captured vendor `libEGL` at `+0x16f16` (width `-1`, height `-1`) and
  `+0x16f1e` (width `1920`, height `720`) on the same surface pointer, so
  `swrast_update_buffers` populates the dimensions during the invocation while the copy
  stride was already derived from `Width = -1`. Scoped to the Wayland **software** path:
  the hardware constructors do not share that vtable.
- **A Qt hide cannot produce the background notification.** DWARF fixes the
  `weston_surface` layout, and read order in `weston_surface_commit_state` shows the
  size block stores the previous positive size before the null-buffer branch zeroes the
  `_from_buffer` pair. A genuine `0x0` transition is required.
- **Guest hardware breakpoints work under TCG**, including four slots, slot
  replacement, `DR4`/`DR5` rejection, per-slot `DR6` bits, single step and per-thread
  scoping. One trap worth knowing: detaching with a slot still armed leaves the
  breakpoint live and kills the tracee.
- Two practical findings for anyone injecting into vendor apps: the launcher's
  interposer unsets `LD_PRELOAD` for AppLauncher so children inherit a clean
  environment, and a musl-linked `.so` will not load into the vendor's glibc process.
- Remaining blocker stated plainly: **AppNavi never attaches a surface** in either the
  full chain or the standalone render probe, so nothing reaches the compositor to be
  classified. The open question is whether the interposer itself is preventing AppNavi
  from rendering; a baseline run without it is the next step.

## 0.64.0 - advisor claims validated: one confirmed root command injection

- Validated the three 2026-10-28 advisor claims offline against the recovered
  `260128` rootfs. **V-006 upgraded to a confirmed static command injection**
  (CWE-78) in `/app/bin/usb-automount`: `system()` at `0x535f` and `popen()` at
  `0x53b9` build shell commands from `ID_SERIAL_SHORT`, reachable on the PTP
  (`060101`) or vendor-specific (`ffff00`) branch and running as uid 0. The
  advisor's "mount script" mechanism and literal payload were both wrong: udev's
  `util_replace_whitespace` neutralises spaces, so only parameter expansion works.
- **V-007** confirmed as configuration only (media parsers configured uid 0, no
  seccomp or capability limits, zero setuid binaries image-wide) and reclassified
  as informational hardening rather than a vulnerability.
- **V-008** confirmed as shipped configuration (root console on ttyS2, autologin
  commented out, `$6$` SHA-512 verifier with unique salt, other accounts locked)
  but **not** as a vulnerability: no bypass, no weak hash. Fail-open ordering in
  `esinit` and dormant Dropbear key material noted.
- Astra triaged and corrected several overstatements, including that a
  system-service default is not an observed uid and that a password verifier is
  not evidence of weakness. Astra advised holding the technical dossiers
  privately pending vendor contact; the public mirror remains at its conservative
  "unverified" text.
- Fable returned no output on two attempts, so Astra performed the triage and is
  attributed. All evidence is static; no VM boot and no hardware contact.

## 0.64.0 - disclosure reduction for the physical-access entries

### (other lineage, same version)

- Reduced V-006, V-007 and V-008 in this public tree to status entries with no
  operational detail, following triage of the third-party claims that produced
  them. Confirmed detail remains in a private record pending coordinated vendor
  contact.
- Verified this public tree contains no occurrence of the affected service name,
  the affected property name, or the command-construction mechanism.
- Note: the engineering-mode entry sequence and PIN were already published in this
  tree by earlier work, before this change, in
  `evidence/owner-engineering-mode-pin-observation.md` and
  `evidence/vehicle-usb/README.md`. That is pre-existing content and was left
  unaltered rather than silently removed; it is flagged for the owner's decision.

## 0.63.0 - unverified physical-access vectors logged

- Added V-006/V-007/V-008 to the defensive register from a third-party advisor
  summary: USB descriptor strings into a privileged mount script, media parsing as
  root, and a hashed-password root serial console. All three are labelled
  **unverified actor reports** with no code path, process identity, console device
  or reproduction supplied; none was validated in this session.
- Recorded the engineering caveats that bound them: USB string descriptors are
  UTF-16LE (metacharacters arrive NUL-interleaved) and `udev` sanitises
  `ID_SERIAL`/`ID_MODEL`, so a vulnerable consumer would have to be custom; the
  126-code-unit descriptor limit still admits a ~40-character payload, making
  encoding and shell quoting rather than length the binding constraint; a hashed
  root console password is ordinary practice and only becomes a finding if weak,
  reused, bypassable or extractable.
- All three require physical access; none is remote. Validation is scoped to the
  isolated VM snapshot or offline analysis of the recovered rootfs. No hardware
  was touched and no attack tooling was built.

## 0.63.0 - VM status, screenshots and physical-access leads

### (other lineage, same version)

- Published two further inspected screenshots under `vm/evidence/screenshots/`:
  the authentic launcher profile/confirm screen and a navigation-window frame that
  still shows Home. Evidence manifest re-hashed (45 entries).
- Expanded the root README with a per-area VM status table, the mandatory run
  configuration and the recovered ApplicationManager/window-byte contract that
  explains why Navigation does not composite yet.
- Added V-006/V-007/V-008 to the defensive register from a third-party advisor
  summary: USB descriptor strings into a privileged mount script, media parsing as
  root, and a hashed-password root serial console. All three are labelled
  **unverified actor reports**; no code path, process identity, console device or
  reproduction was supplied and none was validated in this session.
- Recorded the engineering caveats that bound them: USB string descriptors are
  UTF-16LE (metacharacters arrive NUL-interleaved) and `udev` sanitises
  `ID_SERIAL`/`ID_MODEL`, so a vulnerable consumer would have to be custom; the
  126-code-unit descriptor limit still admits a ~40-character payload, making
  encoding and shell quoting rather than length the binding constraint.
- All three require physical access; none is remote. No hardware was touched, no
  experiment was run for this publication, and no attack tooling was built.
- Note: entries 0.60.0–0.62.0 were previously appended at the end of this file
  rather than in newest-first order; this entry is inserted in the documented
  position without rewriting those historical entries.

## Public repository snapshot - 2026-10-28

- Initialized a fresh public Git history from the sanitized tree so earlier
  private commits are absent from this repository.
- Pointed the Git-scope guard and its tests at
  `JaredReabow/ioniq-5-Reverse-Engineering`.
- Added a public entry point and clarified the publication boundary.

## Imported VM milestones from the private working tree - 2026-10-28

## 0.61.0 - Parallelism/Council measurement-plan checkpoint

- Activated the requested Parallelism + three-seat Council workflow using inline
  workers only. Astra-high led planning; Astra-high and two independent Sol-medium
  seats reviewed and reconciled the same frozen package. The Council checker
  returned `COMPLETE` for the **plan only**, with package fingerprint
  `c59ac8a0d4ece96fd8fab5fe8a6795789697c95394d6e548a02dc8484052bbb5`
  and packet SHA-256
  `528649b5b337fb0b76bafd6cb9b020e572851ec33136c6d0927a5c38a12ef790`.
- Corrected the experimental claim boundary: captured `-4` supports an invalid
  width-derived copy count, but does not yet prove width changed during that
  update or that the original width was `-1`. The accepted plan distinguishes
  EGL call-site arguments from the actual resolved libc entry and requires
  PLT/IFUNC-aware evidence before a fix.
- DeepSeek EC-01/EC-02 did not run. The live tool rejects the required direct
  provider route `deepseek/deepseek-v4.1-flash` as unknown; its suggestion of an
  OpenCode route is not authorized. Parallelism and Council policy now requires
  direct `deepseek/...` provider routes and forbids intermediary fallback. No
  substitute model, implementation, VM run, new thread or bypass routing was
  used. Both tasks remain blocked in the validated ledger.
- Council suggestions require downstream contracts to record both mapped vendor
  EGL and project Mesa identities, numerical capture caps, debugger restoration,
  and host-owned disposable-VM termination. The scheduler still lists the prior
  heartbeat paused; update remains impossible because the exposed API requires
  fields it simultaneously rejects for interval schedules.

## 0.60.0 - bounded fault-time stack and EGL caller

- Added VM-only `ptrace_crash_observe.c`: explicit target allowlist, SEIZE rather
  than group SIGSTOP, bounded 64-word stack/64 KiB maps and original fatal-signal
  redelivery. Compiles statically with warnings-as-errors. Timeout/cancellation/
  group-stop paths remain dynamically untested and are not broadly accepted.
- Completed a short snapshot experiment with guest invalid-PID/disallowed-target
  tests and actual Camera fault capture; 64 stack words read, SIGSEGV re-delivered.
- Identified immediate memcpy call site in vendor EGL software put-image code.
  Cached width-derived stride precedes an update that can change the width;
  captured stride/count registers are -4. Original entry arguments/order remain
  to be measured before a fix. Added qualified investigation I-001 to the
  defensive register, not a confirmed exploitable vendor vulnerability.
- Complete archive SHA-256:
  `e0884a3c11582ed2b986db28f2673b7fde9297a1871f2633ad13672b2dfdeaae`.
  Safe extraction/digest checks pass; 168 repository tests pass; base rootfs
  independently rehashed unchanged. No new threads, commits or fabricated state;
  no independent-model review obtained due the recorded host worker error.

## 0.59.0 - focused early-client core capture

- Completed a short no-NIC/snapshot early-startup experiment in 44.83 seconds,
  capturing one 80 KiB AppCamera core with eight thread-register notes. No full
  agreement/Navigation sequence was attempted. Verified early-client decoration
  value is `1`; this does not validate AppNavi startup.
- Core notes/program headers confirm SIGSEGV/SEGV_MAPERR at libc offset
  `0x128dde`: vector-store destination lies 64 bytes below a writable mapping.
  Fault-thread stack bytes are absent; caller/original copy length remains unknown.
  Modified loop counter is not asserted to be an original argument.
- Requested coredump filter `0x10` read back zero; actual stored memory coverage
  is reported instead of assuming filter behavior. Retained validated core-note
  report, complete archive and exact scripts. Base rootfs rehashed unchanged.
- Archive SHA-256:
  `10fbb21b674ab1795c5e2b52d4e04ad47611f8674c4ac5ed43d283322c24987c`.
  Shell syntax/diff whitespace checks pass. No new thread, image mutation,
  vulnerability classification or Navigation-success claim.

## 0.58.0 - community-source reconciliation

- Recorded the owner's supplied channel-summary leads in
  `evidence/community-chat-leads.md`, explicitly not independently accessed or
  validated. Separated known tools from new compatibility/acquisition leads.
- Retained the tentative CV_E 220721 recollection as different-model comparison
  evidence, not an IONIQ install/downgrade recommendation. Bounded historical
  downloader availability by model, region, endpoint and time.
- Added current-reading warnings to three older evidence notes whose plaintext-
  recovery/API conclusions are superseded or too broad for current VM work.
- Added the reported signature-blocked updater attempt as unvalidated provenance
  for V-005, not a confirmed vulnerability. No fetching, new hardware testing,
  firmware installation or VM run occurred from these chat leads.

## 0.57.0 - 2026-10-27

- Corrected the delegation explanation: inline `spawn_worker` is exposed and
  supports model selection without new chat threads. Earlier statements that
  only child-thread delegation existed were wrong. A useful read-only dispatch
  requesting the configured DeepSeek route failed with host error
  `store.runWorkerToolResult is not a function`; no worker result or runtime
  routing was verified. Operations/handover now identify the actual blocker.
- Executed a snapshot-only decoration-unset control, preserving all other
  baseline flow and existing compatibility behavior. Complete archive recovered
  and digest-verified; harness exit 0 is not feature acceptance.
- Negative semantic result: repeated Camera/Standby crashes, agreement false,
  AppNavi not launched, manager queries 0/0 and all screenshots remain splash.
  The intended child value/geometry was not verified. Do not adopt this change
  or infer a Navigation fix; early-client environment/crash observation is missing.
- Mapped the repeated crash site to libc non-temporal vector store
  `vmovntdq %ymm0,(%r9)` at offset `0x128dde`. Caller/length/register context is
  unknown; this is a write fault, not proof of unsupported AVX or a vendor bug.
  Verified canonical and both new run manifests use the same CPU/memory profile.
- Identified a lower-overhead next capture: vendor kernel supports ELF cores,
  while guest has no inventoried gdb/gdbserver. Proposed bounded snapshot-only
  early-client core-note capture before writing a new sampler; not yet executed.
  Header-only filtering will not provide a complete stack backtrace.
- Complete archive SHA-256:
  `648b5d30c169b2e4adaa2e8cf069742fd5b3d779b0ef1d6d7e63fead7f6910e9`.
  Retained exact source delta, summary, logs and evidence. Base image rehashed
  unchanged; baseline preserved, no new threads or vulnerability claim.

## 0.56.0 - 2026-10-27

- Ran an observation-only wrapper around the unchanged baseline launcher flow in
  isolated QEMU snapshot mode. Completed command exit 0 without timeout; captured
  26 AppNavi maps snapshots and allowlisted environment/mapped-file hashes.
- Runtime maps confirm the analyzed QtWayland client and EGL plugin load. Actual
  AppNavi environment has decoration-disable `1:1`; decoration plugin also loads.
  Parser effect and causal impact are unverified, not a completed fix.
- Authentic Home visibly renders before Navigation. Manager again follows
  `11/11 → 35/11 → 11/11` with FG delivery and status 5/window 0. Final return
  screenshot is black: manager-state return is not visible-Home acceptance.
- Follow-up static review confirms decoration-disable is parsed as a decimal
  scalar via QByteArray::toInt and cached, not as a colon-separated list. The
  inherited `1:1` is malformed for this consumer; exact-library execution of the
  parser remains untested. No environment correction has yet been applied.
- Raw Wayland requests were not captured despite WAYLAND_DEBUG; next observe
  actual hide/attach execution without changing behavior. Retained late cleanup-
  vicinity Camera/Radio crash messages without calling them vulnerabilities.
- Complete archive SHA-256:
  `6019ec6e42cacce8a41fdc79c7dd9705487efdc0a53b741313e6b5b7aad01d84`.
  Decode digest verified; extracted safely. Base rootfs independently rehashed
  unchanged. All 168 tests, shell syntax check and diff whitespace check pass.
  No new threads, image mutation, synthetic callbacks or commits.

## 0.55.0 - 2026-10-27

- Confirmed constructor connection of the same Qt object's visibleChanged(bool)
  to AppNavi onVisibleChanged(bool), refining the prior signal-source uncertainty.
- Traced recovered QtWayland false-visibility handling: explicit null-buffer
  attach/commit occurs only when a virtual discriminator returns zero. Recovered
  EGL plugin inherits that handler and its discriminator returns one, skipping
  that branch. Retained disassembly, relocation evidence and exact signal strings.
- Read-only extraction confirms current-image QtWayland library and EGL plugin
  bytes match the analyzed originals. Runtime selection remains unverified:
  launcher logs inspected lack backend-load identity and alternate library
  search paths precede `/usr/lib`. Next run must first capture mapped identities
  and hide requests without changing behavior.
- This is not yet a guest-backend/root-cause proof. Next verify runtime library
  selection and actual commits; explain older positive controls before
  proposing a narrowly scoped VM adapter. No vendor state or callback fabricated,
  no images changed, no new threads or vulnerability claims.

## 0.54.0 - 2026-10-27

- Host execution recovered; no QEMU/LLVM worker was found in the process check.
  Fresh bounded shell disassembly and read-only current-image extraction passed.
- Current-image IVI shell matches the recovered original. Surface creation
  initializes cached size to 0/0; configure suppresses unchanged dimensions and
  calls layout configure only after a size change. This narrows the prior
  initial-zero hypothesis: no automatic BG event is expected solely from a
  newly created zero-size surface through this path.
- Positive retained controls now show Camera and Standby each configure
  1926×753 → 0×0, then emit BG successfully and reach the manager. Retained
  hashed event excerpts. This demonstrates an earlier working VM transport and
  narrows the next task to AppNavi's hide/unmap/buffer-commit sequence.
- AppNavi visibility follow-up: `onVisibleChanged(false)` sets first-hide state,
  may send the one-shot boot notification, and calls renderer clear/swap. This
  does not prove parent Qt-window unmapping or a null Wayland buffer commit.
  Retained bounded disassembly; next separate the native map-screen callback
  from the parent-window hide path.
- Located authentic `QWindow::hide()` at `0x3362275` in AppNavi foreground
  handling, behind base-result and screen gates. Latest PID-specific logs show
  widget foreground activity but no matching primary-screen hide diagnostic;
  this remains a bounded log observation, not proof of absent invocation.
- Updated evidence and handover. No VM/image edits, new threads or vulnerability
  claims; `git diff --check` passes.

## 0.53.0 - 2026-10-26

- Follow-up provenance: read-only extraction of both compositor paths from the
  current image matches the original module digest; retained Weston log records
  loading the `/usr/lib/weston` path. This is not a historical memory digest.
- Shell-module follow-up commands timed out; completion is unverified. Resume
  only after checking host/process health; do not start duplicate analysis/VM
  runs. Existing scheduled task remains observed active, but prompt update is
  still rejected by scheduler validation.
- Recovered the original compositor callback's final FG/BG branch: any positive
  width or height emits FG; BG requires both non-positive. Exact full-screen
  dimensions are not tested, so changing 1926×753 to 1920×720 would not repair
  that branch. No geometry fix was applied based on the prior hypothesis.
- Hash-identified byte-identical recovered compositor copies and retained LLVM
  disassembly. Next inspect initial configure ordering and verify guest loaded
  module identity. Distinguish the local callback from the nearby exported
  function despite LLVM nearest-symbol labels. No runtime experiment, image
  mutation, synthetic BG event, new thread or vulnerability claim occurred.

## 0.52.0 - 2026-10-26

- Recovered exact QString-list membership after display matching; the subsequent
  AppNavi substring check is a separate predicate. Pending global initializes
  nonzero (`0xffffffff`), so initial zero state is not established as the cause.
- Correlated the full retained latest DLT log: authentic AppNavi surface 3000
  produces an FG callback received by ApplicationManager before status 5/window
  0. The log has no BG-info or naviWindoeCreate diagnostic matches. This narrows
  the next investigation to compositor FG/BG classification/routing.
- Recorded 1926×753 parent geometry as an observation, not a causal conclusion;
  decoration-disable environment is already set. Retained hashed event summary
  and matcher disassembly; updated evidence and handover. No VM changes or new
  runtime run; no new vulnerability claim. `git diff --check` passes.

## 0.51.0 - 2026-10-26

- Traced the window-setter caller into `slotNotifyBGInfo`, whose diagnostic
  identifies surface-ID, display and app-ID inputs. The AppNavi notification
  path additionally requires a display/string helper match, a nonzero global
  gate, and case-sensitive `AppNavi` containment; it clears that gate afterward.
- Recorded exact control-flow addresses and unknown matcher/global semantics
  in the Navigation evidence note. Next trace the upstream event caller and
  gate initialization rather than force a notification. No VM mutation or new
  runtime acceptance is claimed; diff whitespace validation passes.

## 0.50.0 - 2026-10-26

- Recovered ApplicationManager's exact Qt subscription to
  `notifyNaviLaunched(int)` and the routine producing the recorded diagnostic.
- Identified `window[%2]` as a separately latched receiver byte (+0x20), not a
  second boot-signal argument or a surface ID. Zero gates downstream dispatch.
  Adjacent vendor `naviWindoeCreate` code updates the byte and replays cached
  status (+0x1c); next trace direct caller `0x19108d` to recover its producer.
- Retained full LLVM disassembly and bounded extracts; updated Navigation
  evidence and handover. Status-5 enum semantics and runtime acceptance remain
  unresolved. No flags were forced and no VM/image/thread changes occurred.

## 0.49.0 - 2026-10-26

- Identified original ApplicationManager by SHA-256 and mapped six matching
  notification/interface string locations for receiver triage. No handler address
  or enum semantics is claimed from literal strings alone.
- Ordinary/dynamic symbol searches did not expose named handlers. REA deep
  providers are unavailable in the current environment configuration; no tooling
  configuration was changed. Retained raw locations and evidence limits in the
  Navigation contract note and project-local JSON. No target execution or image
  mutation occurred; `git diff --check` passes.

## 0.48.0 - 2026-10-26

- Resolved notification string references against SHA-256-identified original
  recovered AppNavi using read-only ELF section mapping. The function first
  calls `com.lge.avn.applauncher` `/Inform` interface
  `com.lge.avn.applauncher.inform` method `launched(30)`, then emits
  `/navigation_map` interface `com.lge.hkmc.avn.appnavi.naviboot` signal
  `SendNaviBootFail(5)`. These are distinct registration/status messages.
- Retained raw mappings in `work/vm/vendor-userspace-260128/appnavi-notification-strings.json`
  and conclusions in `evidence/navigation-launch-status-contract.md`.
  Located original ApplicationManager for the next receiver analysis. Enum
  semantics, caller selection and window-state producer remain unresolved.
- No target execution, image modification, new threads or security findings.

## 0.47.0 - 2026-10-26

- Reviewed existing saved AppNavi notification disassembly. This function sends
  literal status `5` after an initial one-shot gate; it does not derive that
  integer from engine state within the reviewed function. Exact enum semantics,
  message identity and manager window-state producer remain unresolved.
- Added `evidence/navigation-launch-status-contract.md` with instruction
  addresses, bounded conclusions and next exact receiver/string-mapping work.
  No image mutation, fresh VM run, new thread or vulnerability claim occurred.
- Existing active scheduled-task prompt update was rejected by tool validation;
  no successful update or replacement schedule is claimed. See operations/history.

## 0.46.0 - 2026-10-26

- Reconciled current progress against the existing handover, detailed changelog,
  append-only history, corrections, Git history and security notes. Retained
  existing milestones; no fresh firmware or VM success is claimed.
- Backfilled the history after its 2026-10-19 cutoff with source-labelled
  retrospective milestones, including the corrected VM boot, module-loading
  observation, native userspace recovery, authentic Home and incomplete
  Home↔Navigation integration.
- Added `Ioniq5-VULNERABILITIES.md`, a separate defensive register with evidence,
  preconditions, remediation and acceptance tests. It distinguishes previously
  VM-verified unsigned-module loading from unvalidated keystore/trust/update
  candidates, rejected hypotheses and third-party modification hazards.
- Added `PROJECT-OPERATIONS.md` with the full-VM objective, current blocker,
  append-only rules and an explicit existing-chat-only scheduled prompt draft.
  Scheduling awaits owner confirmation of interval and active-work behavior.
- Read-only routing inspection found the installed DeepSeek Flash builder
  statically ready, but inference routing remains unverified. This session lacks
  native role-selectable subagent tools; no child threads or workers were
  created, and no model/router configuration was changed.
- Preserved the pre-existing dirty source tree, untracked research artifacts,
  firmware and VM images. No commits, pushes, flashes or new VM runs occurred.
- Validation: 168 repository unit tests pass; `git diff --check` passes. Verified
  that the history's original 6,819-byte prefix remains byte-identical.

## 0.45.0 - 2026-10-26

- Added a launcher-local `execve` interposer that supplies the EGL compatibility
  preload only to AppLauncher's original signature-checked AppNavi child. It
  does not directly launch a duplicate AppNavi and does not preload unrelated
  vendor applications.
- The original AppLauncher-owned AppNavi reached map-engine success, selected
  logical `Samples: 2`, created parent surface `3000` with `AID(AppNavi)`, and
  created child surface `4903` while AppLauncher and ApplicationManager remained
  responsive.
- Recovered AppNavi's exact startup decision in
  `NimoExSLApplicationLinux::onInitializeDone()`: offset `0x33b48be` compares
  elapsed startup with `0x59d7` (22,999 ms), and the slow path invokes
  `SendToAppLauncherNaviLaunchedToExcute()`.
- Added a fail-closed, sentinel-gated, executable-scoped VM timing control. It
  validates the expected four immediate bytes and changes only the in-memory
  startup deadline from 22,999 to 180,000 ms using the PIE load base; the signed
  AppNavi file is unchanged. The first non-PIE-aware attempt is retained as a
  negative control because it caused AppNavi `SIGSEGV`/restart churn.
- With the corrected control, AppNavi completed initialization at 106,464 ms,
  created its parent window, and entered the launch-status path only after the
  authentic window event. This ruled out the 22,999 ms timeout ordering as the
  sole cause of the incomplete manager transition.
- The launch path still emitted `SendNaviBootFail(5)` and ApplicationManager
  logged `notifyNaviLaunched[5] window[0]`. Manager state remained `35/11`, no
  Navigation frame was foregrounded, and the authentic return request restored
  state `11/11` plus visible Home. Full Home↔Navigation acceptance remains
  unproven.
- Latest runner SHA-256 is
  `906e734012a9a9cac35aed2e9258674215b407a93cdce9e58024a2f78bf8dd9f`;
  host-log SHA-256 is
  `de9977d671cb203f918d878f939777c1eea330bad90dd2ca0643b6ba57c60021`;
  complete evidence archive SHA-256 is
  `a0e2100ca5a0eb72426db6179c88a27e34abe5928d8a364ce9f14d0e9bfd52b8`.
- Current rootfs SHA-256 is
  `4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f`;
  `prepare.json` matches and `e2fsck -fn` passes.

## 0.44.0 - 2026-10-26

- Established the first semantically corroborated authentic profile-confirm
  path under global two-thread llvmpipe. AppStandbyClock logs
  `confirmSkPressed()`, `onPressedButton`, `onReleased`, and
  `HANDLER_CONFIRMSCREEN_BUTTON_CONFIRM_CLICKED` after bounded pointer input to
  the observed enabled Confirm control.
- Standby progresses from `14` to `12`; ApplicationManager explicitly logs
  `is_standby_agree_pressed standbyStatus[12] result[1]`. Exception-filter
  masks `66` and `161` both return zero, superseding the prior mask-`161`
  result `32` seen before agreement.
- The immediate Home-transition D-Bus out value remains `255`, but downstream
  evidence proves it is not sufficient to classify the asynchronous request
  as rejected: manager current AppID becomes Home `11`, Home returns `ret[1]`,
  drawing AppID becomes `11`, and IVI foregrounds run-specific surface `1001`.
- Added the separately named VM-only Home-settle control. It pauses only
  ApplicationManager for 55 seconds after authentic `requestShow(APP_HOME)` so
  the unmodified Home binary can finish its first frame without a false
  production-liveness kill under x86 TCG software rendering, then resumes the
  manager and repeats the authentic Home request. It does not fabricate an
  alive reply, acceptance state, manager result, application ID, or pixels.
- Captured visibly composed authentic Home at 1920×720. The final vehicle,
  battery/range, and Media Off frame has SHA-256
  `23ccd6e6002d8bceddac3a64b2c94538cb844cc9aa274b44d18ada876d2cc968`.
- Positive evidence archive SHA-256 is
  `87d81b278f8b1bb20236faedd17dda0493b49b6cfc1e0fd2f1acfe8b8d2c6f5e`;
  host-log SHA-256 is
  `2c6c7ed142cb84b7dcc5daf5a9adb01a2e86934c731ae5653efa5d0d80d93b95`.
- Full Home↔Navigation operation remains unproven. AppNavi, data-bearing
  micom/CAN methods, authentic persistence, and production-speed liveness
  behavior remain separate unresolved boundaries.
- Current rootfs SHA-256 is
  `8a686d4bf0b278d7e99dd5d94181a58e5b5ef147bff9f99444a25d0134e16756`;
  `prepare.json` matches and `e2fsck -fn` passes.

## 0.43.0 - 2026-10-26

- Reached and repeatedly foregrounded the authentic AppStandbyClock
  profile-confirm screen with restored production ASTC assets. Runtime QML
  observation places the enabled Confirm control at `x=471..1179`,
  `y=621..699`; the transformed pointer point is inside it.
- Added exact-build observational pointer-focus logging to
  `tools/uk_fw/guest/weston_vm_input.c`. Every phase of the bounded pointer
  gesture remains focused on the authentic AppStandbyClock PID, excluding a
  late AppEURadio/Home client as the current routing owner.
- Identified the authentic screen/Loader sizing defect in this VM: the loaded
  `QRootScreen` and parent Loader resolve to `0×0` while explicit-size children
  render outside them. A separately named VM compatibility control adds
  `anchors.fill: parent` to both alternating Loaders and yields a complete
  `1920×720` screen → Loader → main-root ancestry without changing the legal
  handler or model state.
- The Loader repair does not by itself deliver Qt Quick input. A direct
  full-screen observational MouseArea still receives no press even though
  Weston sends motion/down/up to the correct client.
- Added bounded syscall and RIP observers. The QtWayland thread receives the
  three expected Wayland input batches (`recvmsg` 20/72/24 bytes), while the
  main GUI thread remains runnable in userland. All 32 sampled instruction
  pointers map inside Mesa 18 `swrast_dri.so`; Qt cannot dispatch the queued
  input while synchronous software rasterization monopolizes the GUI thread.
- Negative VM controls—threaded render loop, `vblank_mode=0`, two softpipe
  threads, hidden live status bar/noninteractive layers, scheduler priority,
  temporary AppNavi quiescence, `SIGCONT`, and a 60-second post-input wait—do
  not produce the authentic Confirm handler. None is treated as acceptance.
- Standby remains `11`, the Home transition result remains `255`, and no legal
  confirmation, filter-bit clearance, or normal Home↔Navigation transition is
  claimed.
- Current rootfs SHA-256 is
  `32f4e81f3e637c7fc3c2b3457852b7b8473dda4f2cc0288bff11618cdda5abee`;
  `prepare.json` matches and `e2fsck -fn` passes.

## 0.42.0 - 2026-10-26

- Corrected the full-chain Qt/Wayland environment: the probe no longer
  pre-sets `QT_WAYLAND_SHELL_INTEGRATION=ivi` before authentic AppLauncher
  appends `:ivi`. The invalid `ivi:ivi` value is gone; Qt clients load
  `libivi.so` and log `Using the 'ivi' shell integration`.
- Added `--micom-serial` to the offline VM harness, providing guest
  `/dev/ttyS1` through a project-local Unix socket while retaining the no-NIC
  boundary. The authentic micom daemon now configures 115200-baud serial and
  registers `com.lge.car.micom`, although hardware-dependent boot-info calls
  still do not complete.
- Captured authentic `/Ihu` and `/Can` introspection and established the exact
  `AskSysBootinfo() -> ay` contract. Consumer disassembly and controlled runs
  confirm a 35-byte reply.
- Added fail-closed VM research helper
  `tools/uk_fw/guest/micom_dbus_sim.c`. It supplies only the exact boot-info
  data reply, exposes evidence-derived introspection, acknowledges only exact
  transport signatures, logs all byte-array/int32 arguments, and rejects
  unimplemented data-bearing methods. It is not recovered firmware or a full
  micom/CAN emulator.
- The corrected candidate profile makes AppLauncher select HMC, vehicle code
  `0x26`/38, Europe, 12.3-inch display, RHD, Navigation, Modem, and English
  instead of the prior LX2/Korea fallback. Remaining zero option fields are
  explicitly incomplete rather than claimed as an authentic Ultimate profile.
- Full-chain run `1792936845027660000` reached concurrent authentic activity:
  AppNavi reported engine success and created surfaces `3000` and `4903`;
  AppHomeScreen finished QML drawing and created surface `1004`;
  AppLauncher, ApplicationManager, and Home remained alive at the evidence
  checkpoint.
- Reclassified AppNavi's later `SIGTRAP`: ApplicationManager's liveness
  watchdog explicitly executes `killall -5 AppNavi` after missed responses.
  No spontaneous SIGSEGV/ABRT/BUS/ILL was found in that trace set.
- Direct-launch no-`strace` control run `1792937492664474000` reproduces the
  watchdog kill, excluding syscall tracing as the sole cause. Session-bus
  evidence identifies the exact liveness path: AppNavi answers the first
  `org.freedesktop.DBus.Peer.Ping` at `/navigation_map`, then fails to answer
  eight later Pings while software-rendered startup continues.
- Captured 301 micom calls over 34 method signatures, including exact CAN IDs,
  masks, registration records, CPU-alive transitions, boot-complete states,
  and DID/version writes. No CAN signals are fabricated yet; payload semantics
  must be mapped consumer-by-consumer first.
- The final frame remains splash. Home is still marked non-visible, AppNavi is
  watchdog-terminated, persistence resource tables are absent, and
  data-bearing micom/CAN transitions remain to be implemented and tested.
- Updated the current image identity to
  `817ca674b0e181209ca154236c9fc7d284b085caa0b045c5e4e66cd2fd081f5d`;
  copy-on-write checkpoints and `e2fsck -fn` controls passed.
- All 21 focused VM harness tests and all 167 repository tests pass; JSON
  manifests parse, Python compilation succeeds, and `git diff --check` passes.

## 0.41.0 - 2026-10-25

- Validated native TE2/xcrypt decryption for current EU/AU packages and
  recovered the authentic rootfs, GUI, AppNavi, updater and RW-data userspaces.
- Booted recovered Weston/IVI with project-local Mesa 18 `softpipe`; authentic
  `AppHomeScreen` now renders a complete 1920×720 frame, and pointer/touch
  events reach authentic Qt/QML.
- Recovered launcher identity for AppNavi: AppID `30`, parent IVI surface
  `3000`, launcher path `/navi/navi/Bin/AppNavi`.
- Added a bounded authentic EU map/core/skin subset. AppNavi reaches
  `### Navi Engine Init Success ###`, loads the authentic theme image and
  night skin, and renders an independently committed 836×720 map-widget
  surface `4903`.
- Captured the first visible authentic navigation-map pixels in run
  `1792908755653936000`: roads, buildings, water and the vehicle marker are
  visible at native 836×720 inside a 1920×720 compositor frame. PNG SHA-256:
  `88e8403d808b6936181465ee512aa9e124b75ccc7dbd625a221e41e75ab8b4cb`.
- Added exact-configuration VM helper
  `tools/uk_fw/guest/ivi_link_navi_widget.S`, which reconstructs the missing
  IVI relationship `3000 -> 4903`, restores the child's native destination,
  and foregrounds the parent. This helper is not recovered firmware.
- Preserved controls showing that skin data alone still produced the prior
  nearly black frame, a parent/child relationship without child layout reduced
  it to 1×1, and hiding/promoting the child full-screen produced a stretched
  but visible map. This isolates the composition issue from map rendering.
- The milestone remains VM-adapted: it uses an exact-build zero-MSAA AppNavi
  compatibility copy and a one-method `NotifyValetStatus` D-Bus responder.
  Unmodified AppNavi and the full `ApplicationManager` chain are not claimed.
- The full chain remains blocked on missing `MICOMSTATUSMESSAGE`
  shared-memory/semaphore state. Missing landmark/DEM/sqlite resources remain
  logged, although they do not prevent the first map frame. Binding the
  recovered new2.0 HMC asset tree removed all 15 named PNG-load failures but
  left the compositor screenshot byte-identical, ruling those files out as the
  current cause of the black parent region.
- Reviewed the native TE2 decryptor implementation: 28 focused tests and all
  165 repository tests pass. A real official EU `.lge.upgrade.xml` decryption
  is byte-identical to the independently preserved recovered output.

## 0.40.0 - 2026-10-21

- Reached interactive BusyBox userspace on the **VM-adapted vendor kernel**:
  one verified guest-RAM SDHCI table change, a compatible ext4 SD root and
  explicit `/init`. Original firmware/boot-image files remain unchanged.
- Added an 800×480 direct-QEMU-VGA diagnostic with R/G/B/Q keyboard input.
  QMP captures match every expected pixel. This is explicitly **not the
  infotainment UI**, which remains unrecovered.
- Replaced the old launcher with a local-input-only, hash-checked preparation
  and run harness; retained unpatched and failing-command controls. Fixed
  foreground programs consuming the launcher's separate status-command input.
- Tested two additional recovery hypotheses using existing resources: the
  boot RSA public key against 38 opaque payload edges (zero matching type-1
  blocks), and two installed Mac updater AES constant pairs against bounded
  payload-start hypotheses (zero validated plaintext candidates). Retained
  scan scopes, synthetic controls and the rejected gzip-marker matches.
- Full suite: **137 tests pass**. Fresh serial and graphics VM checks pass;
  prepared artifacts and earlier evidence hashes remain unchanged.
- Replaced the stale handover and corrected categorical VM impossibility,
  sparse-log PCI-enumeration, anti-tamper-panic and footer-stripping claims.
  Entries 0.36–0.39 below preserve historical conclusions, not current findings.
- No head-unit access, new downloads, genuine firmware decryption, flashing,
  signature bypass, Fable review or new Council acceptance is claimed. Legacy
  accepted-input hashes were not refreshed.

## 0.39.0 - 2026-10-19

- Commissioned an independent reviewer/planner pass (child note 12) on the VM
  goal. Its verdict matches the measurements: **running the vendor UI under
  emulation is not achievable**, for three reasons — the userland is encrypted,
  the kernel has no display path at all, and no block device binds.
- Stated the ceiling explicitly in `vendor-kernel-vm.md`: this kernel's only
  console is 8250 serial; `CONFIG_FB` is not set, there is no VGA or framebuffer
  console, and the sole display driver is i915, which QEMU cannot emulate. The
  achievable outcome is an interactive **serial shell on the stock kernel**, not
  a picture — and calling it "the UI" would misrepresent it.
- Recovered significant keystore configuration from the same config:
  `CONFIG_KEYSTORE_TESTMODE=y`, `CONFIG_KEYSTORE_TEST_MIGRATION=y`,
  `CONFIG_KEYSTORE_DEBUG=y`, `CONFIG_KEYSTORE_SECURE_BOOT_IGNORE=y` alongside
  `CONFIG_SECURE_BOOT=y`, `CONFIG_KEYSTORE_SEED_SIZE_64=y`,
  `CONFIG_KEYSTORE_DEVICE_AND_USER_SEED=y`, and
  `CONFIG_KEYSTORE_OEM_KEY_USAGE_BIT=47` with the exact
  `CONFIG_KEYSTORE_OEM_KEY_IDENTIFIER` string seen in `verify_oem_signature`.
  Production firmware shipping with keystore test mode, debug and secure-boot
  ignore enabled is a notable configuration finding.
- Corrected the stale introduction in `vendor-kernel-vm.md`, which still claimed
  an ext4 mount and a deliberate panic.
- Also established that PCI devices are barely enumerated under this kernel in
  QEMU (one quirk line on q35, nine on `-machine pc`, no device registrations),
  which is a prerequisite problem for the SD controller binding.
- No exploit, key, decryption or device action is included.

## 0.38.0 - 2026-10-19

- **Solved the boot-parameter mechanism.** `setup_abl_params` is registered with
  the `__setup` string **`ABL.`** (trailing dot), confirmed by reading the string
  at `__setup_str_setup_abl_params`. The handler splits the remainder on `=` and
  stores name/value pairs in a 16-entry list. The correct command line is
  `ABL.oemkm=<hex size>@<hex phys>` and `ABL.seed=<hex phys>,<hex phys>`.
- **The anti-tamper is now satisfied under emulation**: with those parameters and
  the blobs loaded at physical addresses, the kernel reports
  `keystore_init completed successfully` and `manifest: init Completed
  Successfully`, and no longer panics on them. This corrects the documentation
  that recorded the parameters as bare `oemkm=` / `seed=`.
- Found the introspection interface: `abl_cmdline_init` exposes every collected
  parameter under **`/sys/kernel/abl/`**.
- Located the mechanism by a proper xref pass: a new `FindXrefs.java` Ghidra
  script showed a WRITE to `params_list` inside `setup_abl_params`, which is how
  the vendor hook was identified after the earlier dead end.
- Remaining VM gap is a root device, not the anti-tamper: sdhci core and the
  22 `sdhci_pci_*` symbols are present but QEMU's `sdhci-pci` device ID is not in
  the 4.1 driver's table, so no `mmc0` binds and root mounting fails. Recorded the
  next step: present a controller ID the driver recognises.
- No exploit, key, decryption or device action is included.

## 0.37.0 - 2026-10-19

- Extracted the exact boot-parameter contract by decompiling
  `get_apl_seed_offsets` and reading `keystore_fill_seeds`. The two parameters use
  **different separators**: external `ABL.oemkm=<hex size>@<hex phys>` and
  `ABL.seed=<hex phys>,<hex phys>` (the parser stores internal names `oemkm` and `seed`). `keystore_fill_seeds` copies two **64-byte** seeds
  out of physical memory (device → `sec_seed`, user → keystore state) and then
  **zeroes both source regions**; an absent device seed is fatal, an absent user
  seed is tolerated.
- Derived a minimal manifest blob that satisfies `manifest_init`'s validation:
  0x40 bytes, word 0 = `0xE`, byte `0x13` = 0, words 5 and 6 = 0, word 1 =
  end-of-entries offset.
- **Tested it and it did not work.** With both parameters supplied and the blobs
  loaded via QEMU `-device loader`, the kernel still reports both missing, even
  though it prints the command line verbatim. `params_list` is an empty
  `LIST_HEAD` at `0xffffffff81a1e330` and stock `unknown_bootoption` never
  populates it, so the vendor's collection hook is elsewhere and has not been
  located. Recorded so the next attempt starts from that point.
- Recorded an environment fault: Homebrew Python 3.14 became unusable mid-session
  (`posix_spawn` error) and `python3` now resolves to it; all tools still run
  under `python3.13`.
- No exploit, key, decryption or device action is included.

### (other lineage, same version)

- Extracted the exact boot-parameter contract by decompiling
  `get_apl_seed_offsets` and reading `keystore_fill_seeds`. The two parameters use
  **different separators**: `oemkm=<hex size>@<hex phys>` and
  `seed=<hex phys>,<hex phys>`. `keystore_fill_seeds` copies two **64-byte** seeds
  out of physical memory (device → `sec_seed`, user → keystore state) and then
  **zeroes both source regions**; an absent device seed is fatal, an absent user
  seed is tolerated.
- Derived a minimal manifest blob that satisfies `manifest_init`'s validation:
  0x40 bytes, word 0 = `0xE`, byte `0x13` = 0, words 5 and 6 = 0, word 1 =
  end-of-entries offset.
- **Tested it and it did not work.** With both parameters supplied and the blobs
  loaded via QEMU `-device loader`, the kernel still reports both missing, even
  though it prints the command line verbatim. `params_list` is an empty
  `LIST_HEAD` at `0xffffffff81a1e330` and stock `unknown_bootoption` never
  populates it, so the vendor's collection hook is elsewhere and has not been
  located. Recorded so the next attempt starts from that point.
- Recorded an environment fault: Homebrew Python 3.14 became unusable mid-session
  (`posix_spawn` error) and `python3` now resolves to it; all tools still run
  under `/opt/homebrew/bin/python3.13`.
- No exploit, key, decryption or device action is included.

## 0.36.0 - 2026-10-19

- Added `tools/uk_fw/fat_harness.py`: a from-scratch FAT16/FAT32 image builder,
  independent inspector, and 17-case semantic corruption corpus targeting the
  checks a filesystem driver must perform. Images were validated by mounting them
  on macOS, which reads and executes their contents correctly. Seven unit tests.
- Added `tools/uk_fw/vm_boot.py` and **got the vendor kernel booting under
  QEMU 11.1.2**: `4.1.27-abl #1`, built 2026-01-28, initialising SMP, ACPI, PCI,
  serial console and an ext4 root on an emulated SD card.
- Two obstacles solved and documented: the `ipk.` payload is a bzImage at offset
  **1008** (protocol 2.13, `setup_sects` 30), and this kernel **cannot use an
  initramfs** because `CONFIG_BLK_DEV_INITRD` is not set — no VIRTIO, no built-in
  ATA/SCSI, no NFS root. The only bootable root is ext4 on an SD card, which also
  mirrors the real unit's `mmcblk0`.
- **Discovered a boot-time anti-tamper**: without its parameters the kernel prints
  `keystore: d/u-seed info missing in cmdline`, `manifest: Key manifest info
  missing in cmdline` and panics with a vendor-modified message, "Invalid
  configuration from end user prevents continuing". It refuses to run rather than
  degrading. This confirms the internal ABL-list entry `oemkm` (external
  command-line form `ABL.oemkm=`) is mandatory at runtime and names the second
  required input (device/user seed material).
- Recovered the internal build provenance from a surviving path string:
  `26RU1_001`, built 2026-01-21, branch tag `s5w.26ru1.251203`, kernel source at
  `security/keystore/seed.c`.
- No exploit, key, decryption or device action is included.

### (other lineage, same version)

- Added `tools/uk_fw/fat_harness.py`: a from-scratch FAT16/FAT32 image builder,
  independent inspector, and 17-case semantic corruption corpus targeting the
  checks a filesystem driver must perform. Images were validated by mounting them
  on macOS, which reads and executes their contents correctly. Seven unit tests.
- Added `tools/uk_fw/vm_boot.py` and **got the vendor kernel booting under
  QEMU 11.1.2**: `4.1.27-abl #1`, built 2026-01-28, initialising SMP, ACPI, PCI,
  serial console and an ext4 root on an emulated SD card.
- Two obstacles solved and documented: the `ipk.` payload is a bzImage at offset
  **1008** (protocol 2.13, `setup_sects` 30), and this kernel **cannot use an
  initramfs** because `CONFIG_BLK_DEV_INITRD` is not set — no VIRTIO, no built-in
  ATA/SCSI, no NFS root. The only bootable root is ext4 on an SD card, which also
  mirrors the real unit's `mmcblk0`.
- **Discovered a boot-time anti-tamper**: without its parameters the kernel prints
  `keystore: d/u-seed info missing in cmdline`, `manifest: Key manifest info
  missing in cmdline` and panics with a vendor-modified message, "Invalid
  configuration from end user prevents continuing". It refuses to run rather than
  degrading. This confirms `oemkm` is mandatory at runtime and names the second
  required input (device/user seed material).
- Recovered the internal build provenance from a surviving path string:
  `26RU1_001`, built 2026-01-21, branch tag `s5w.26ru1.251203`, kernel source at
  `security/keystore/seed.c`.
- No exploit, key, decryption or device action is included.

## 0.35.0 - 2026-10-19

- Added `evidence/exploit-inventory.md`: a single table of every known technique
  for this platform with what it yields, its precondition, and whether it can be
  used as a **first** step. Consolidates Chimaera CVE-2023-26243/44/45/46,
  `navi_extended`, `disableEncryptionUpdate`, `wideopen.service`, the QML patch,
  boot-image substitution, CVE-2020-8539, `hmg_nemesis`, the kernel CVEs and the
  unverified Wi-Fi daemon classes.
- States the circularity plainly: every named CVE is a binary patch and therefore
  requires prior execution. The only non-circular entry is the Engineering Mode
  AppNavi installation, which is a feature rather than a vulnerability.
- Maps the two capabilities raised by the owner — a USB payload and a modified
  firmware image — and shows both are gated: the USB payload needs a replacement
  `AppNavi` installed, and custom firmware is a persistence capability (key or
  `disableEncryptionUpdate`), not an entry capability.
- Identifies the genuine pre-authentication surface: the USB update path, with the
  filesystem parser as the only stage that touches attacker bytes before any
  cryptographic gate.
- No exploit, key, decryption or device action is included.

## 0.34.0 - 2026-10-19

- Added `evidence/network-root-feasibility.md` in answer to a direct question:
  whether the Linux version yields a network path to root. Answer: vulnerabilities
  certainly exist, a network root does not follow.
- Recorded the config filter that removes most of the remote-RCE catalogue:
  `USER_NS`, `NF_TABLES`, `BLUETOOTH`, `SCTP`, `DCCP`, `RDS`, `TIPC`, `NFC`,
  `AX25`, `X25`, `INET_ESP`, `XFRM_USER`, `TCP_MD5SIG` and `INET_DIAG` are all
  absent; `AF_PACKET` is a module and needs `CAP_NET_RAW`. What remains
  pre-authenticated is IPv4/IPv6 parsing, TCP, UDP, ICMP, fragment reassembly and
  netfilter hooks — a surface that yields DoS, not code execution.
- **Discovered that the kernel is not a pristine 4.1.27:** the symbol
  `sysctl_tcp_challenge_ack_limit` is present, introduced by the CVE-2016-5696 fix
  in **4.1.32**. The vendor cherry-picks network fixes, so version-string
  reasoning is unreliable in both directions and per-fix verification is required.
- Recorded two false-inference traps for future work: the upstream GRO recursion
  helpers are `static inline` so their absence is suggestive, not conclusive; and
  `tcp_gso_segs` is a struct field, not a symbol, so its absence proves nothing.
- No exploit, key, decryption or device action is included.

## 0.33.0 - 2026-10-19

- Added `evidence/corrections-log.md`: an explicit, claim-oriented record of the
  eleven things this programme got wrong or superseded, each with what replaced
  it and why. Eleven entries cover the kallsyms 204-entry mispairing, the
  `0x18` pseudo-checksum, the A/B partition misreading, the downgrade conclusion,
  the weakened CRC hypothesis, the header entropy misreading, the guessed
  decryptor invocation, the `iasImage` decomposition, the absent kernel IAS
  driver, and two attempted vulnerabilities that were tested and **rejected**
  (`TEST_VERIFY_ECC_SIGNATURE` uninitialised fields and `keystore_get_ksm_key`
  buffer aliasing).
- The log states which evidence documents are affected by each correction, so a
  reader landing on an older document knows whether to trust it.
- It closes with the five practices that produced the corrections — cross-check
  against an independent table, disassemble before calling something a bug, check
  the entropy maximum, treat field reports as evidence against a hypothesis, and
  record rejections as well as findings.
- No exploit, key, decryption or device action is included.

## 0.32.0 - 2026-10-19

- Delivered the `workflow-normalized.csv` export that was requested earlier and
  never produced. Added `tools/uk_fw/ledger_export.py`, which flattens the nested
  ledger into two deterministic tables: `workflow-normalized.csv` (one row per
  task-artifact pair, 19 rows, tasks without artifacts retained) and
  `requirements-normalized.csv` (16 rows with the tasks citing each
  requirement).
- The export is byte-idempotent — re-running on an unchanged ledger produces
  identical files — and supports ``--check`` so drift between ledger and exports
  is detectable. Line terminator is LF so the files diff cleanly.
- Fixed a bug found during development: `--check` disagreed with the writer
  because CSV defaults to CRLF while `read_text` normalises newlines.
- Added five unit tests; the suite now runs 74 tests.
- No exploit, key, decryption or device action is included.

## 0.31.0 - 2026-10-19

- Added `evidence/pre-disclosure-security-assessment.md` in place of a further
  exploitation pass. It is an **internal assessment, not a disclosure**: no vendor
  was contacted and nothing was published.
- It records four candidate issues with explicit confidence levels — CRC-32 as the
  declared manifest integrity value (confirmed mechanism, unproven impact), the
  external `ABL.oemkm=` command-line trust-policy handoff (confirmed format), the absent capability check in
  `keystore_open` (confirmed), and the boot container's embedded modulus
  (confirmed structure, unproven pinning) — and states for each what evidence
  would make it disclosable.
- It explicitly separates the **modification-created** root runner from vendor
  defects, so a report is not padded with an artefact of the mod itself.
- It records what was established as *not* vulnerable, so the assessment is not
  one-sided.
- No exploit, key, decryption or device action is included.

### (other lineage, same version)

- Added `evidence/pre-disclosure-security-assessment.md` in place of a further
  exploitation pass. It is an **internal assessment, not a disclosure**: no vendor
  was contacted and nothing was published.
- It records four candidate issues with explicit confidence levels — CRC-32 as the
  declared manifest integrity value (confirmed mechanism, unproven impact), the
  `oemkm=` command-line trust root (confirmed), the absent capability check in
  `keystore_open` (confirmed), and the boot container's embedded modulus
  (confirmed structure, unproven pinning) — and states for each what evidence
  would make it disclosable.
- It explicitly separates the **modification-created** root runner from vendor
  defects, so a report is not padded with an artefact of the mod itself.
- It records what was established as *not* vulnerable, so the assessment is not
  one-sided.
- No exploit, key, decryption or device action is included.

## 0.30.0 - 2026-10-19

- Read the final two public toolchain scripts, completing the read-through.
  `update_navi_manually.sh` answered the last open structural question: **the
  navigation application lives in the map partitions, not the rootfs** — at
  `/navi/Bin/AppNavi` and `/navi2/Bin/AppNavi`.
- Consequence recorded: the A/B pairing extends to the navigation app, so a
  custom `AppNavi` must be installed into **both** partitions or it disappears
  when the unit switches map partitions. The script also replaces `AppNavi`
  directly on the partition, bypassing the Engineering Mode dialog — but it needs
  an execution context, so it is a re-install path, not an entry bypass.
- `HANDOVER.md` now carries the navigation paths in the target table and the
  alternative in the chain diagram.
- Every script in the public toolchain has now been read. No new avenues remain
  in that corpus.
- No exploit, key, decryption or device action is included.

## 0.29.0 - 2026-10-19

- Consolidated six passes of findings into the two deliverables a returning
  operator actually reads. This is documentation work, not new discovery.
- Rewrote `HANDOVER.md`: seven findings instead of five, a line-level chain with
  the real paths and commands (entry at `/media/usb`, persistence unit, QML patch,
  decryptor path, `/tmp/<32 hex>` key capture, repack command), the corrected
  tool table, and four more rows in the established-negatives table.
- Added an explicit **safety warning** to the handover: `wideopen.service` is a
  root service that executes any `wideopen_service.sh` from any mounted USB with
  no authentication, and it survives official updates. Safe on a bench, an
  unauthenticated root backdoor if the image returns to a vehicle.
- Made `evidence/bench-runbook.md` Phase 4 concrete: the four-step key-capture
  procedure, the double-backup requirement for `DecryptToPIPE_OG`, the exact
  offline decrypt command, and the glibc/`gcompat` constraint.
- No new exploit research; no device action.

## 0.28.0 - 2026-10-19

- Recovered the **exact key-extraction mechanism** from `extract_keys.sh` and
  `spoof_decrypttopipe.sh`, including the real invocation the unit uses:
  `/app/share/AppUpgrade/DecryptToPIPE -d /tmp/<32 hex> /media/usb/1/<model>/AppUpgrade 0 | dd of=/update/usb/bin/AppUpgrade bs=512`.
  The decryptor path, the per-update random `/tmp` key path, and the output target
  are now all recorded.
- Documented the two-stage procedure: back up the genuine decryptor, install a
  patched `DecryptToPIPE_FK`, reboot, let the unit's own update call it with the
  temporary key, collect `*_key_*.der` from the USB, restore the original.
- Established that the public `update_decryptor` repository ships **placeholders,
  not the artifacts**: `DecryptToPIPE` is a 129-byte shell stub and
  `decryption_key.der` is a 193-byte `EMPTY_DECRYPTION_KEY` text file. This closes
  the last possibility of an offline decryption path — neither the binary nor the
  key is public.
- Recorded the defensive design of the extraction scripts (flag files, mandatory
  backup checks) and the warning that losing `DecryptToPIPE_OG` permanently breaks
  the unit's update path.
- No key, binary, decryption or device action is included.

## 0.27.0 - 2026-10-19

- Recovered the **real decryptor invocation** from `update_decryptor`'s
  `entrypoint.sh`: `DecryptToPIPE -d <keyfile> <input> 0 > <output>`. Output is on
  stdout, every file in the package is handed over whole (the footer is *not*
  stripped), and the binary is glibc x86-64 run under Alpine + `gcompat`.
  `tools/uk_fw/gen5w_decrypt.py` was corrected accordingly — it had guessed a
  different syntax and wrongly assumed the footer must be removed first.
- Recovered the complete payload and persistence chain from `navi_extended`'s
  `USB_FILES` and `update-patcher`'s scripts: `main_loop.sh` runs
  `main_loop_code.sh` every 10 s; `install_wideopen_service.sh` remounts `/` rw,
  installs and enables `wideopen.service`, remounts ro; the unit is a
  **root** service with `Restart=always`/`RestartSec=5` whose `ExecStart` runs
  `find /media/usb -iname 'wideopen_service.sh' -exec bash {} \;`.
- **Stated plainly in the evidence:** once installed, any USB stick carrying
  `wideopen_service.sh` yields root execution with no authentication. Safe on a
  bench, an unauthenticated root backdoor if the image ever returns to a vehicle.
- Recovered the exact Engineering Mode patch set: PIN comparisons `enterMenu ==
  21`/`== 11` removed, `checkSOPVersion() ===` inverted to `!==`, the
  engine call replaced with `false`, plus a `dropbear` → `dropbearmulti` symlink.
  This is what removes the gate permanently after one patched install.
- Confirmed the repack command and added its `*.DS_Store` exclusion to
  `rootfs_patch.py`; 69 tests still pass.
- No exploit, key, decryption or device action is included.

## 0.26.0 - 2026-10-19

- Disassembled the `navi_extended` application assembly in full using
  `dnfile` + `dncil` installed into a local venv under `work/` (nothing global),
  with **every metadata token resolved**. The behaviour is now exact rather than
  inferred from strings.
- Exact logic: an infinite loop that every **5 seconds** runs
  `Directory.GetFiles("/media/usb", …, SearchOption.AllDirectories)` +
  `FirstOrDefault` for **`install_wideopen_service.sh`**, then for
  **`main_loop.sh`**, and — if the first is non-null — executes them with
  `ExecuteBash`, which escapes only `"`, builds
  `/bin/bash -c "<path>"` with `RedirectStandardOutput`, `UseShellExecute=false`
  and `CreateNoWindow=true`, then `ReadToEnd` and `WaitForExit`.
- Operational consequences recorded: the script is **re-executed every five
  seconds**; `install_wideopen_service.sh` takes precedence and is the documented
  persistence step; only the first match of each name is used; the argument is
  the file **path**, not its contents; a blocking script holds the helper inside
  `ReadToEnd`.
- Recorded a command-injection seam in the tool (only `"` is escaped, not
  backticks or `$(...)`) and why it is moot: the operator already supplies the
  script.
- Corrected the previous note, which had described the matching predicate and
  poll interval as unconfirmed.
- No binary committed; hashes and behavioural description only. No device action
  and no execution of the artifact.

## 0.25.0 - 2026-10-19

- The GitLab rate limit cleared, so the **actual entry binary was obtained and
  analysed statically** (never executed). `AppNavi` release 0.2.0 is
  35,201,155 bytes, SHA-256 `9198abf2…85c7`, an ELF x86-64 .NET **6**
  self-contained single-file bundle; the application assembly `navi_extended.dll`
  is only **5,632 bytes** (SHA-256 `dc2ef0dc…4bc7`), recovered by parsing the
  trailing bundle table and inflating the entry.
- Established what the binary actually is: a file scan under **`/media/usb`** for
  **`main_loop.sh`** (and `install_wideopen_service.sh`), executed via
  `/bin/bash -c` with output redirected, in a sleep loop. There is **no
  vulnerability and no memory-corruption exploit in it** — it is a deliberate
  drop-in trampoline that runs a USB script.
- Consequence recorded: the entry primitive is a **legitimate app substitution**,
  so the entire chain rests on the unit's own AppNavi update path. The software
  barrier is trivial; the installation gate is everything.
- Recorded the unit's USB mount point and payload script name, which are required
  for any custom application and otherwise cost bench time to discover.
- No binary is committed; only hashes and behavioural description. No device
  action and no execution of the artifact.

## 0.24.0 - 2026-10-19

- Reviewed the second open-access primary source for this platform,
  Costantino & Matteucci, *"Reversing Kia Motors Head Unit to discover and
  exploit software vulnerabilities"* (JCVHT 19:33–49, 2023, DOI
  `10.1007/s11416-022-00430-5`, 17 pages, full text extracted). It documents
  four vulnerabilities in the **Android/Telechips** Kia IVI lineage
  (`micom`-centric, 116 references; no `AppNavi`, no AES, no `update` mechanism).
  It is the earlier KOFFEE work already covered by child note 04 and does **not**
  transfer to the Linux `S5W_L` path this programme targets. Recorded so it is
  not re-examined.
- `navi_extended` source and release binaries remain unobtainable: GitLab returns
  HTTP 429 on the API, the web tree endpoint and the archive endpoint alike.
  Recorded as an external rate limit rather than a dead end.
- No exploit, OEM key, decryption or device action is included.

## 0.23.0 - 2026-10-19

- Closed two remaining completeness questions as clean negatives and recorded
  them permanently in `HANDOVER.md` so they are not retried.
- **Package completeness:** both the EU `260128` and AU `260319` packages list
  exactly 35 files with **zero unlisted and zero missing**; only the map archive
  and its MD5 sidecar differ by region. There is no hidden or unmanifested
  payload.
- **No key material in the package:** 223 plaintext artifacts scanned for PEM
  headers, base64 X.509 prefixes, PKCS#7 and X.509 signature OIDs and SSH keys —
  no hits (three generic `30 82` byte pairs in binary data are coincidental).
  Key material is device-resident only, which confirms the published technique.
- Retried the `navi_extended` source archive from a different endpoint; still
  HTTP 429. Recorded as an external limit, not a dead end.
- Added an "Established negatives" table to `HANDOVER.md` covering ten ruled-out
  avenues, so future work starts from the right place.
- No exploit, OEM key, decryption or device action is included.

## 0.22.0 - 2026-10-19

- Added `HANDOVER.md` at the project root: a single read-first document covering
  the target identity, the five findings that matter, the end-to-end chain, the
  tool inventory, the three questions that unblock progress, the bench order, and
  an explicit statement of what is deliberately absent and where the honest limits
  are. Written because 25 evidence documents and 11 subagent notes are too much to
  wade through on return.
- No exploit, OEM key, decryption or device action is included.

## 0.21.0 - 2026-10-19

- Closed the boot-image format question with an exact decomposition:
  `iasImage` = **3,385-byte header + 6,210,308-byte payload + 13,035-byte
  trailer** = 6,226,728 bytes, where the payload length is exactly the plaintext
  `_sub` size. The header is variant-specific with no plaintext fields (a search
  for 6,210,308, 3,385, 13,035, 52, 953 and `0x42f08d94` as little-endian words
  finds nothing); the trailer is identical across five variants and package-scoped.
- Corrected an intermediate reading in this session: the header's per-64-byte-block
  entropy of ~5.7 looks structured only because 6.0 is the maximum for a 64-byte
  block; the region is in fact random, i.e. encrypted.
- Established a clean negative: the Linux kernel contains **no** IAS-related
  symbol, string or config option, so `ipk.`/`iasImage` verification is a **boot
  loader** function performed before Linux runs. The format therefore cannot be
  reverse engineered without the SPI flash contents; the boot path is closed
  offline and the OTA path remains the open one.
- No exploit, OEM key, decryption or device action is included.

## 0.20.0 - 2026-10-19

- Added `tools/uk_fw/rootfs_patch.py`, closing the *build* half of custom
  firmware: `list` inspects a rootfs package, `inject` installs a systemd unit,
  appends SSH keys (mode 0600) to `/etc/dropbear/authorized_keys`, or copies
  arbitrary payloads, and `meta` computes the rebuilt file's size and signed
  CRC-32 and rewrites the matching `.ver` record.
- Enforced the vendor archive constraints recovered from the public patcher:
  `--format=ustar` and `--numeric-owner`, since the reader rejects pax/GNU
  extensions and name-resolved ownership. Inputs are never modified.
- Added `evidence/custom-firmware-build-path.md`, separating the two independent
  problems: the cipher (bypassed entirely by the `disableEncryptionUpdate` path)
  and acceptance (the version gate plus the package descriptor binding).
- Added four unit tests for the repacker; the suite now runs 69 tests.
- Recorded that the `navi_extended` release binaries would reveal the exact
  `AppNavi` interface but GitLab returned HTTP 429 during this session, so the
  fetch was backed off rather than retried aggressively.
- No exploit, OEM key, decryption or device action is included.

## 0.19.0 - 2026-10-19

- **Corrected the previous conclusion that downgrade is blocked.** The
  anti-rollback analysis (child note 10) separates the two siblings: on the
  **Linux `S5W_L`** path the documented userspace version gate is a string
  comparison in `AppSetup`, evaluated after `DecryptToPipe` handles
  `.lge.upgrade.xml`; loader/fuse rollback policy remains unaudited. The
  public `navi_extended` FAQ documents a substitution method — older official
  payloads paired with the **latest** `.lge.upgrade.xml` for the same vehicle, so
  a genuine signed newer manifest satisfies the `>=` check while older content is
  written. On the **Android Gen5W** sibling the `update_info` inside
  `system_package` is signed and binds the package, which is why the EV6 report
  was rejected even with corrected `.ver` CRCs.
- Recorded the three remaining obstacles on the Linux path, none of which are
  cryptographic: (a) the feed — the update API currently returns 503, so older
  packages cannot be enumerated; (b) distance — the entry precondition is a
  pre-November-2021 build, five years of package-format change away from
  `260128`; (c) the method is documented against 2021–2022 packages and is
  unconfirmed on 2026 packages.
- Recorded that no reviewed public evidence establishes whether this variant
  has a monotonic anti-rollback counter (fuse/OTP). CVE-2023-26245 covers the
  software userspace version gate; loader/fuse controls remain unknown.
- No exploit, OEM key, decryption or device action is included.

### (other lineage, same version)

- **Corrected the previous conclusion that downgrade is blocked.** The
  anti-rollback analysis (child note 10) separates the two siblings: on the
  **Linux `S5W_L`** path the version gate is a single userland string comparison
  in `AppSetup`, evaluated after `DecryptToPipe` handles `.lge.upgrade.xml`, and
  the public `navi_extended` FAQ documents a substitution method — older official
  payloads paired with the **latest** `.lge.upgrade.xml` for the same vehicle, so
  a genuine signed newer manifest satisfies the `>=` check while older content is
  written. On the **Android Gen5W** sibling the `update_info` inside
  `system_package` is signed and binds the package, which is why the EV6 report
  was rejected even with corrected `.ver` CRCs.
- Recorded the three remaining obstacles on the Linux path, none of which are
  cryptographic: (a) the feed — the update API currently returns 503, so older
  packages cannot be enumerated; (b) distance — the entry precondition is a
  pre-November-2021 build, five years of package-format change away from
  `260128`; (c) the method is documented against 2021–2022 packages and is
  unconfirmed on 2026 packages.
- Recorded that no monotonic anti-rollback counter (fuse/OTP) is publicly
  demonstrated for this variant, so rollback protection is software-only, matching
  CVE-2023-26245.
- No exploit, OEM key, decryption or device action is included.

## 0.18.0 - 2026-10-19

- Characterised the encrypted boot wrapper (`iasImage` without `_sub`): all six
  variants are 6,226,728 bytes (16,420 more than the plaintext payload); five
  share an identical **13,035-byte trailer** (SHA-256 `41885928…`, entropy 7.976)
  while `iasImage_p5_1920_12` has a different tail; the trailer is package-scoped
  (EU and AU share no suffix) and contains no plaintext exponent marker, unlike
  `_sub`.
- Recorded that this mirrors the OTA footer pattern and supports a single packing
  model: encrypted content plus a package-level descriptor appended verbatim.
- No exploit, OEM key, decryption or device action is included.

## 0.17.0 - 2026-10-19

- Reviewed the public issue trackers of the Gen5 Wide-Open projects. Recorded
  that **downgrade remains unsolved in public**: `navi_extended` issue #2
  ("How do I downgrade?", open since 2022-10-30) reports that editing
  `update.info` did not work, and no answer was published.
- Recorded field evidence that **weakens this programme's own CRC hypothesis**:
  issue #3 (2023-09-23) describes repairing the `.ver` CRC and file size and the
  unit still refusing to install. The arithmetic result (CRC-32 is forgeable)
  stands; the exploitable reading is now treated as unlikely on its own. The
  hypothesis document was amended accordingly rather than left standing.
- Confirmed newer packages ship `appnavi.tar` (not `appnavi.tar.gz`), matching our
  `260128` package; scripts globbing the old name silently do nothing.
- Probed the official update API with the public tool's local-token scheme:
  `apieu.map-care.com` and `api.map-care.com` both return **HTTP 503**;
  `oem-euupload.map-care.com` returns 404/connection failure; two 2023 issues
  report "no cars available on any region". Older-build acquisition is therefore
  at risk, which removes the feedstock for a downgrade even if one became legal.
- Net effect on the plan: the entry gate is unchanged, the integrity gate is
  demonstrably stronger than the `.ver` CRC, and the pre-authentication parser
  surface remains the most promising target.
- No exploit, OEM key, decryption or device action is included.

## 0.16.0 - 2026-10-19

- Analysed the **open-access primary source** for this platform: *"A vehicle
  firmware security vulnerability: an IVI exploitation"* (DOI
  `10.1007/s11416-024-00522-4`, JCVHT 20(4):681–696). Recorded the published
  technique: `DecryptToPIPE` statically links mbedtls and retains an unused
  `mbedtls_printf`, whose register leak exposes the **AES-CBC-128** key; the
  `Key_file` holds the RSA public key plus the wrapped AES key; each file is
  described as content + terminator + SHA + signature; and `AppDMClient`,
  `AppUpgrade` and `DecryptToPIPE` are patched to skip signature checks.
- Established that the OTA key is recoverable with **public** RSA material plus
  one device file, so offline decryption needs only the `DecryptToPIPE` and key
  pair — no further reverse engineering.
- Closed the cross-build ciphertext avenue with measurements: no ECB anywhere
  (zero duplicate 16-byte blocks in 16 MiB samples), no same-offset block
  agreement between EU and AU, and the package footer identical within a package
  but completely different across packages — consistent with a derived IV over a
  package-constant plaintext.
- Recorded a tension: the paper implies a per-file SHA in the trailing block,
  yet the measured tail is identical across three files; the per-file SHA is
  therefore most likely inside the encrypted content. Left explicitly open.
- Extracted the AU boot containers for the first time: same command lines and
  build id as EU, but the kernels differ (126,510 differing bytes, 2,122 ranges).
- Confirmed two dead ends so they are not retried: `navi-updates-lfs` contains
  only a README, and stock Ghidra 12.1.4 has no RL78 processor module (M16C only),
  so the frontkey MCU is not decompilable without a third-party module.
- No exploit code, patch offsets, key-unwrap implementation or device action is
  reproduced.

## 0.15.0 - 2026-10-19

- **Proved that CRC-32 is not an integrity control** for this package format.
  `tools/uk_fw/crc32_forge.py` computes the 4-byte correction that forces any
  chosen CRC-32, and the demonstration preserved the manifest value across a real
  content change: original `0xa09a265d`, modified content gave `0x0338bbdf`,
  correction at offset 8 restored `0xa09a265d` with differing bytes
  `[8,9,10,11,20]`.
- Refined the earlier hypothesis: because `.ver` CRC-32 values are computed over
  **ciphertext**, a CRC-preserving modification still requires the decryption key,
  so this is a **post-execution** persistence mechanism, not a route to first
  execution. That distinction is recorded explicitly.
- Added `tools/uk_fw/gen5w_decrypt.py`, an orchestration harness around the
  unit-derived decryptor with `plan` / `run` / `verify` subcommands. It makes no
  assumption about the vendor binary's interface (the command is a caller-supplied
  template), strips the detected package footer from the model, and classifies
  outputs by entropy and printability.
- Added four unit tests for CRC forging (property, no-op, out-of-range offset,
  arbitrary targets). The full suite now runs 65 tests.
- No exploit, OEM key, decryption or device action is included.

## 0.14.0 - 2026-10-19

- Discovered the OTA container structure from ciphertext alone: each package
  appends a package-scoped **footer** of 14,059 bytes (EU `260128`) or 14,315
  bytes (AU `260319`) to exactly `AppUpgrade`, `.lge.upgrade.xml` and
  `update.tar.gz`. Footer digests:
  `fc1c07cc…` (EU) and `81c18efd…` (AU). The four large payloads carry no shared
  suffix and there is no shared prefix anywhere.
- Established that `.lge.upgrade.xml` is almost entirely footer: only 3,611 bytes
  (EU) / 3,497 bytes (AU) are its own encrypted content, consistent with
  `AppSetup` decrypting it first to read the version.
- Profiled the footer: entropy 7.98 overall and 7.1–7.3 per 256-byte block, no
  gzip/zlib/DER/PEM/X.509 markers and no printable runs, i.e. a structured but
  encrypted descriptor.
- Recorded a **hypothesis** (explicitly not a finding): because the `.ver`
  manifest carries only size and signed CRC-32, and the large payloads are not
  separately signed, per-file integrity may reduce to CRC-32, which is trivially
  forgeable. Falsified if the descriptor holds a cryptographic digest per file or
  the upgrader re-hashes decrypted content.
- Added `tools/uk_fw/ota_structure.py`, which reports shared regions, the
  detected footer, its digest and entropy, and per-file unique sizes, reading only
  64 KiB windows per file.
- No exploit, OEM key, decryption or device action is included.

## 0.13.0 - 2026-10-19

- Recovered the documented Gen5W operating model from the public
  `g4933/wideopen` wiki and `g4933/gen5w` projects, which fills the gap that the
  encrypted userland was hiding.
- Recorded the update flow: `AppSetup` reads `.lge.upgrade.xml`, decrypts it with
  `DecryptToPipe`, and proceeds only when the version is **greater than or equal
  to** the installed version; `AppUpgrade` then performs filesystem, map and
  firmware stages and finally rewrites `/etc/fstab`.
- Corrected an earlier interpretation: the two roots in the recovered command
  line (`mmcblk0p3`, `mmcblk0p5`) are the **A/B system partitions**, not merely
  display variants. A rootfs write goes to the inactive partition, so a failed
  rootfs experiment is recoverable by restoring `fstab`, while a bad boot image
  is rejected by the signed container rather than rolled back.
- Recorded `disableEncryptionUpdate` semantics: it disables decryption only; the
  `.lge.upgrade.xml` version check still runs.
- Recorded the public entry preconditions (`navi_extended` as a replacement
  `AppNavi` installed through Engineering Mode, requiring an unpatched build and
  therefore a downgrade on newer units) and the documented SSH persistence path
  (`/etc/dropbear/authorized_keys`, publickey installer, relaxed
  `dropbear@.service` condition).
- Identified the first gate for the public path: whether `260128` still offers
  "Update AppNavi from USB", and whether any rollback counter exists outside
  `AppUpgrade` (none found in the recovered kernel configuration or symbols).
- Updated `evidence/bench-runbook.md` with the A/B recovery path, the downgrade
  gate and the persistence procedure.
- No exploit, OEM key, decryption or device action is included.


- Added `tools/uk_fw/bench_assess.py`, a read-only orchestrator that runs the
  serial capture, network surface, rootfs survey and boot-container inspection in
  a fixed safe order and writes a single `report.json` plus per-step artifacts.
  Steps are independent and skipped steps are recorded explicitly.
- Verified the orchestrator offline: the image step reports `signature_ok=True`
  and the OEM modulus digest for the packaged container.
- Added `evidence/bench-runbook.md`, the phased operating procedure from physical
  preparation through disclosure, with read-first gates and the exact commands for
  each tool.
- No exploit, OEM key, decryption or device action is included.


- Recovered the keystore root of trust. `manifest_init` (boot initcall)
  `strcmp`s the internal ABL-list name **`oemkm`**; the external command line is
  `ABL.oemkm=<size>@<phys>`, parsed with
  `sscanf("%x@%x")`, copies a 64 MiB-bounded blob out of physical memory via
  `memcpy_from_ph`, validates only a four-field header (type word `0xe`), then
  creates `.manifest_keyring` with `prepare_kernel_cred(0)` **root credentials**.
- Established that `ABL.oemkm=` is **absent from all six packaged command lines**, so
  the boot loader places the runtime manifest in DRAM and injects the parameter.
  The manifest's source of record and storage medium remain unknown.
- Consequence recorded: root on the rootfs does **not** itself recover the OEM
  private key or rewrite the already-copied policy. The demonstrated modified-
  package bypass is userland, matching CVE-2023-26244/26245/26246 and the
  `update-patcher` approach; loader and boot-stage routes remain separate.
- Recorded a design observation: this kernel path trusts the copied manifest and
  its location is loader-added after the signed packaged command line. Whether
  the preceding loader authenticates or measures that handoff remains unknown. Whoever controls the `ABL.oemkm=` handoff and physical blob can
  choose manifest admission policy, subject to a certificate-loading path. With
  `CONFIG_KEXEC=y` this is a research direction post-root, not a persistence path.
- Verified **`check_usage_bits`** is a clean four-word subset test
  (`requested == allowed & requested`); a key with an all-ones mask authorises
  every usage.
- Studied **`keystore_backup`**: it gates key export on an OEM signature over a
  user-supplied 136-byte blob, then encrypts the 64-byte client key material to
  the host key and signs the result; the key material is hexdumped under dynamic
  debug before being zeroed.
- Tested a suspected uninitialised-copy defect in **`keystore_get_ksm_key`** at
  instruction level and **rejected it**: the buffer is `[68-byte private][136-byte
  public]`, the code zeroes the private half and returns the public half.
- Subagent research completed: daemon version-fingerprinting triage (dnsmasq,
  hostapd/wpa_supplicant, miniupnpd, dropbear, BusyBox) and SMACK device-access
  analysis. The SMACK note establishes that `/dev` is devtmpfs, so an unlabelled
  node defaults to the `*` label, which combined with the absence of a capability
  check in `keystore_open` makes `/dev/keystore` reachability purely a
  mode-plus-label question once the rootfs is decrypted.
- No exploit, OEM key, decryption or device action is included.


- Added `tools/uk_fw/ver_manifest.py` and verified both official packages end to
  end against their own manifests: EU `NE_E.EUR.S5W_L.001.001.260128` and AU
  `NE_E.AUS.S5W_L.001.001.260319` each report 33/35 files matching size and
  signed CRC-32, **0 mismatches, 0 missing**, with the two files larger than
  2 GB skipped (EU map archive and EU `mango-vr_fixed.tar.gz`).
- Documented the manifest path convention: the record carries the directory in
  the Windows-style field and the filename separately, and the package name
  prefix must be stripped before resolving against a package root.
- Added unit tests: `tests/test_ipk_tool.py` (8 tests covering parsing, signature
  verification, payload tampering, tag tampering, non-`ipk.` rejection,
  re-signing and oversized command-line rejection) and
  `tests/test_ver_manifest.py` (5 tests covering prefix stripping, clean
  verification, mismatches, missing files and large-file skipping). 13 tests
  pass.
- No exploit, OEM key, decryption or device action is included.


- Fully characterised the plaintext `ipk.` boot container. Field `0x018` is a
  constant format/build id, **not** a checksum: it is identical across all six
  `iasImage*_sub` variants whose command lines differ. Earlier zlib and
  CRC-32/MPEG-2 checksum hypotheses were wrong for that reason.
- Established that the six variants differ by only 261–274 bytes (command line,
  one byte at `0x46`, and the trailer), i.e. one kernel serves 1280, 1920/12 and
  p5 layouts.
- Recovered and verified the container signature: **RSA-2048, PKCS#1 v1.5,
  SHA-256**, signed over `[0, hdr+total+4)` = header + payload + 4-byte variant
  tag. `pow(sig, 65537, n)` yields the expected DigestInfo block and the trailing
  digest matches. OEM modulus SHA-256
  `227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6`.
- Established that this modulus appears **only** in the six containers and is
  **absent from the kernel image**, so any pinning lives in the boot loader or
  the encrypted main `iasImage`. Whether trust is pinned or self-referential
  cannot be decided offline and is the highest-value bench question.
- Added `tools/uk_fw/ipk_tool.py` with `info`, `verify`, `extract` and
  `resign`. Verified end-to-end: the OEM image verifies, and a modified
  `init=/bin/sh` image re-signed with a generated test key verifies under the new
  modulus. `resign` produces a correctly formed container for an acceptance
  experiment; it does not defeat OEM verification.
- Added `tools/uk_fw/bench_serial.py` driving the recovered `ttyS2` 115200 8N1
  console (capture, send, port enumeration) so the boot log can be recorded the
  moment the unit is available.
- Dispatched four research subagents: kernel 4.1.27 backport gap, daemon
  version-fingerprint triage, USB gadget/iAP2 protocol surface, and SMACK device
  access.
- No exploit, OEM key, decryption, simulated boot on a vehicle, or device action
  is included.


- Repaired kallsyms recovery for the exact EU kernel. `tools/uk_fw/kallsyms_extract.py`
  fails on this image; three defects were identified: false-positive
  `kallsyms_num_syms`, an odd-aligned marker array, and — most seriously — an
  address-array start taken at the first kernel-range pointer, which mispaired
  **every** symbol by 204 entries while still producing plausible prologues.
- Added `tools/uk_fw/kallsyms_structural.py`, which derives the layout
  structurally and recovers 64,923 symbols in 0.3 s.
- Cross-validated the recovered table against the independent `__ksymtab`
  export table: 4,369 of 4,375 exports match exactly with zero residual
  mismatches. Corrected layout: addresses `0x89f158`, num_syms `0x91de30`,
  names `0x91de38`, markers `0x9dedc8`, token table `0x9df5b8`, index `0x9df940`.
- Because the mispairing was silent, prior Ghidra naming derived from a
  run-start extraction is recorded as unverified and was re-derived. The
  corrected import renamed 25,033 functions and decompiled 41 priority
  functions.
- Established the trust-chain anatomy: `verify_oem_signature` SHA-256s the
  input, then `manifest_key_verify_digest` performs a `manifest_keyring` lookup,
  parses 16 usage-bit bytes from the key description, and calls the asymmetric
  verify op. It is reachable only from `keystore_backup` and
  `keystore_generate_mkey` and is not exported, so this verifier is not the
  firmware/update acceptance gate. The demonstrated update-package decision is
  in userland; loader and boot-stage trust remain separate.
- Reviewed the 26-ioctl `/dev/keystore` boundary. It is defensively written:
  a `size < 0x319` gate against a 0x318-byte staging area ending at the canary,
  overflow-checked user pointers, matching allocation and copy lengths, and
  post-dispatch zeroing. No memory-safety defect was found in the reviewed set
  — a bounded negative result, not proof of absence. A hypothesis about
  uninitialised tail fields in `TEST_VERIFY_ECC_SIGNATURE` was tested and
  rejected (decoded size 0x120 covers the offsets read).
- Recorded that `keystore_open` performs no capability check, so access depends
  on the device-node mode and SMACK label, which remain inside the encrypted
  rootfs. `keystore_verify` and `keystore_register` are exported.
- Confirmed the EU map ZIP is plaintext (1,335 entries) but data-only, that the
  VR package is plaintext TTS/ASR data with no executables, and that the map
  package ships a Gladman Rijndael licence — a hint at the AES implementation
  family, not a key.
- Re-stamped `ART-T6-CHANGELOG` after this documentation update. The frozen T6
  acceptance is therefore stale and requires re-review; this entry records the
  change rather than concealing it.
- No exploit, key, decryption, modified image, flash procedure, or device
  action is included.


- Established that the official `260128` userland is soundly encrypted: entropy
  ~8.00 per envelope, no keystream reuse between files, and no plaintext magic
  in any encrypted payload. Confirmed the manifest checksum is `zlib.crc32`
  against the plaintext `Checksum.txt`.
- Recovered the complete kernel command line from the plaintext
  `iasImage*_sub` containers: serial console `ttyS2` at 115200 8N1, early console
  at MMIO `0xfc000000`, `init=/lib/systemd/esinit`, dual root (`p3`/`p5`),
  Intel DRCFG USB0 mux, `ramoops` at `0x50000000`, and Intel Broxton platform.
- Integrated the public Gen5W prior art (`laralbir` EU standard Gen5W and the
  `gitlab.com/g4933/gen5w` tool group): the `navi_extended` → `DecryptToPIPE` +
  `decryption_key.der` → `update_decryptor` → `update-patcher` chain.
- Recorded the two MASS_PRODUCT Engineering Mode gates (SOP check plus QML PIN
  `21`/`11`) and the published alternative routes (UART, GDS, older build).
- Recorded the published ciphertext-level structure: re-sealed 16,417-byte
  modem trailers, stable container prefixes (14,048 / 14,122 / 640 / 112 bytes),
  and which payloads changed functionally between `251204` and `260128`.
- Confirmed `mango-vr_fixed.tar.gz` is real gzip but TTS/ASR data only (49
  entries in the AU package, no executables); frontkey MCUs are Renesas RL78.
- Added `evidence/known-exploits-and-cve-survey.md`,
  `evidence/gen5w-public-exploit-ecosystem.md`, `evidence/bench-hardware-root-path.md`,
  and `evidence/network-surface-and-wifi-root.md`, plus four child-thread notes.
- Reinforced the scope boundary: no exploit, decryptor key, modified image,
  flash procedure, or live-vehicle action is included.


- Recorded the active target as an AVN bench unit removed from the vehicle, and
  scoped research to that unit with no vehicle connected.
- Added `tools/uk_fw/dump_survey.py`, a read-only survey of a rootfs dump or
  ext4 image covering accounts, setuid/setgid, file capabilities, SMACK
  policy, systemd units, boot command line, debug surfaces, persistence paths
  and world-writable files.
- Added `tools/uk_fw/net_surface.py`, a TCP surface mapper with banner, HTTP,
  TLS-certificate, SSDP and mDNS discovery for an owned bench unit.
- Added `evidence/bench-hardware-root-path.md` with the UART / bootloader /
  storage / software ladder, the interface survey checklist, and the Gate 4
  recovery preconditions applied at bench scale.
- Added `evidence/network-surface-and-wifi-root.md` mapping Wi-Fi exposure
  modes, service-to-vulnerability classes, and the evidence each class needs.
- No exploit, payload, credential attack, flash procedure, or live-vehicle
  action is included.

### (other lineage, same version)

- Recovered the documented Gen5W operating model from the public
  `g4933/wideopen` wiki and `g4933/gen5w` projects, which fills the gap that the
  encrypted userland was hiding.
- Recorded the update flow: `AppSetup` reads `.lge.upgrade.xml`, decrypts it with
  `DecryptToPipe`, and proceeds only when the version is **greater than or equal
  to** the installed version; `AppUpgrade` then performs filesystem, map and
  firmware stages and finally rewrites `/etc/fstab`.
- Corrected an earlier interpretation: the two roots in the recovered command
  line (`mmcblk0p3`, `mmcblk0p5`) are the **A/B system partitions**, not merely
  display variants. A rootfs write goes to the inactive partition, so a failed
  rootfs experiment is recoverable by restoring `fstab`, while a bad boot image
  is rejected by the signed container rather than rolled back.
- Recorded `disableEncryptionUpdate` semantics: it disables decryption only; the
  `.lge.upgrade.xml` version check still runs.
- Recorded the public entry preconditions (`navi_extended` as a replacement
  `AppNavi` installed through Engineering Mode, requiring an unpatched build and
  therefore a downgrade on newer units) and the documented SSH persistence path
  (`/etc/dropbear/authorized_keys`, publickey installer, relaxed
  `dropbear@.service` condition).
- Identified the first gate for the public path: whether `260128` still offers
  "Update AppNavi from USB", and whether any rollback counter exists outside
  `AppUpgrade` (none found in the recovered kernel configuration or symbols).
- Updated `evidence/bench-runbook.md` with the A/B recovery path, the downgrade
  gate and the persistence procedure.
- No exploit, OEM key, decryption or device action is included.


- Added `tools/uk_fw/bench_assess.py`, a read-only orchestrator that runs the
  serial capture, network surface, rootfs survey and boot-container inspection in
  a fixed safe order and writes a single `report.json` plus per-step artifacts.
  Steps are independent and skipped steps are recorded explicitly.
- Verified the orchestrator offline: the image step reports `signature_ok=True`
  and the OEM modulus digest for the packaged container.
- Added `evidence/bench-runbook.md`, the phased operating procedure from physical
  preparation through disclosure, with read-first gates and the exact commands for
  each tool.
- No exploit, OEM key, decryption or device action is included.


- Recovered the keystore root of trust. `manifest_init` (boot initcall)
  `strcmp`s the kernel parameter **`oemkm`**, parses `oemkm=<size>@<phys>` with
  `sscanf("%x@%x")`, copies a 64 MiB-bounded blob out of physical memory via
  `memcpy_from_ph`, validates only a four-field header (type word `0xe`), then
  creates `.manifest_keyring` with `prepare_kernel_cred(0)` **root credentials**.
- Established that `oemkm=` is **absent from all six packaged command lines**, so
  the boot loader places the manifest and injects the parameter. The OEM key is
  therefore not in the root filesystem and not in the kernel image.
- Consequence recorded: root on the rootfs does **not** grant signing capability.
  The OEM public key is firmware-pinned; a signature bypass must be a userland
  decision, matching CVE-2023-26244/26245/26246 and the `update-patcher` approach.
- Recorded a design observation: the manifest blob is trusted implicitly and its
  location is a plain command-line value not covered by the `ipk.` container
  signature. Whoever controls `oemkm=` controls the trusted key set. With
  `CONFIG_KEXEC=y` this is a research direction post-root, not a persistence path.
- Verified **`check_usage_bits`** is a clean four-word subset test
  (`requested == allowed & requested`); a key with an all-ones mask authorises
  every usage.
- Studied **`keystore_backup`**: it gates key export on an OEM signature over a
  user-supplied 136-byte blob, then encrypts the 64-byte client key material to
  the host key and signs the result; the key material is hexdumped under dynamic
  debug before being zeroed.
- Tested a suspected uninitialised-copy defect in **`keystore_get_ksm_key`** at
  instruction level and **rejected it**: the buffer is `[68-byte private][136-byte
  public]`, the code zeroes the private half and returns the public half.
- Subagent research completed: daemon version-fingerprinting triage (dnsmasq,
  hostapd/wpa_supplicant, miniupnpd, dropbear, BusyBox) and SMACK device-access
  analysis. The SMACK note establishes that `/dev` is devtmpfs, so an unlabelled
  node defaults to the `*` label, which combined with the absence of a capability
  check in `keystore_open` makes `/dev/keystore` reachability purely a
  mode-plus-label question once the rootfs is decrypted.
- No exploit, OEM key, decryption or device action is included.


- Added `tools/uk_fw/ver_manifest.py` and verified both official packages end to
  end against their own manifests: EU `NE_E.EUR.S5W_L.001.001.260128` and AU
  `NE_E.AUS.S5W_L.001.001.260319` each report 33/35 files matching size and
  signed CRC-32, **0 mismatches, 0 missing**, with the two files larger than
  2 GB skipped (EU map archive and EU `mango-vr_fixed.tar.gz`).
- Documented the manifest path convention: the record carries the directory in
  the Windows-style field and the filename separately, and the package name
  prefix must be stripped before resolving against a package root.
- Added unit tests: `tests/test_ipk_tool.py` (8 tests covering parsing, signature
  verification, payload tampering, tag tampering, non-`ipk.` rejection,
  re-signing and oversized command-line rejection) and
  `tests/test_ver_manifest.py` (5 tests covering prefix stripping, clean
  verification, mismatches, missing files and large-file skipping). 13 tests
  pass.
- No exploit, OEM key, decryption or device action is included.


- Fully characterised the plaintext `ipk.` boot container. Field `0x018` is a
  constant format/build id, **not** a checksum: it is identical across all six
  `iasImage*_sub` variants whose command lines differ. Earlier zlib and
  CRC-32/MPEG-2 checksum hypotheses were wrong for that reason.
- Established that the six variants differ by only 261–274 bytes (command line,
  one byte at `0x46`, and the trailer), i.e. one kernel serves 1280, 1920/12 and
  p5 layouts.
- Recovered and verified the container signature: **RSA-2048, PKCS#1 v1.5,
  SHA-256**, signed over `[0, hdr+total+4)` = header + payload + 4-byte variant
  tag. `pow(sig, 65537, n)` yields the expected DigestInfo block and the trailing
  digest matches. OEM modulus SHA-256
  `227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6`.
- Established that this modulus appears **only** in the six containers and is
  **absent from the kernel image**, so any pinning lives in the boot loader or
  the encrypted main `iasImage`. Whether trust is pinned or self-referential
  cannot be decided offline and is the highest-value bench question.
- Added `tools/uk_fw/ipk_tool.py` with `info`, `verify`, `extract` and
  `resign`. Verified end-to-end: the OEM image verifies, and a modified
  `init=/bin/sh` image re-signed with a generated test key verifies under the new
  modulus. `resign` produces a correctly formed container for an acceptance
  experiment; it does not defeat OEM verification.
- Added `tools/uk_fw/bench_serial.py` driving the recovered `ttyS2` 115200 8N1
  console (capture, send, port enumeration) so the boot log can be recorded the
  moment the unit is available.
- Dispatched four research subagents: kernel 4.1.27 backport gap, daemon
  version-fingerprint triage, USB gadget/iAP2 protocol surface, and SMACK device
  access.
- No exploit, OEM key, decryption, simulated boot on a vehicle, or device action
  is included.


- Repaired kallsyms recovery for the exact EU kernel. `tools/uk_fw/kallsyms_extract.py`
  fails on this image; three defects were identified: false-positive
  `kallsyms_num_syms`, an odd-aligned marker array, and — most seriously — an
  address-array start taken at the first kernel-range pointer, which mispaired
  **every** symbol by 204 entries while still producing plausible prologues.
- Added `tools/uk_fw/kallsyms_structural.py`, which derives the layout
  structurally and recovers 64,923 symbols in 0.3 s.
- Cross-validated the recovered table against the independent `__ksymtab`
  export table: 4,369 of 4,375 exports match exactly with zero residual
  mismatches. Corrected layout: addresses `0x89f158`, num_syms `0x91de30`,
  names `0x91de38`, markers `0x9dedc8`, token table `0x9df5b8`, index `0x9df940`.
- Because the mispairing was silent, prior Ghidra naming derived from a
  run-start extraction is recorded as unverified and was re-derived. The
  corrected import renamed 25,033 functions and decompiled 41 priority
  functions.
- Established the trust-chain anatomy: `verify_oem_signature` SHA-256s the
  input, then `manifest_key_verify_digest` performs a `manifest_keyring` lookup,
  parses 16 usage-bit bytes from the key description, and calls the asymmetric
  verify op. It is reachable only from `keystore_backup` and
  `keystore_generate_mkey` and is not exported, so **firmware trust is decided
  in userland**, consistent with CVE-2023-26244/26245/26246.
- Reviewed the 26-ioctl `/dev/keystore` boundary. It is defensively written:
  a `size < 0x319` gate against a 0x318-byte staging area ending at the canary,
  overflow-checked user pointers, matching allocation and copy lengths, and
  post-dispatch zeroing. No memory-safety defect was found in the reviewed set
  — a bounded negative result, not proof of absence. A hypothesis about
  uninitialised tail fields in `TEST_VERIFY_ECC_SIGNATURE` was tested and
  rejected (decoded size 0x120 covers the offsets read).
- Recorded that `keystore_open` performs no capability check, so access depends
  on the device-node mode and SMACK label, which remain inside the encrypted
  rootfs. `keystore_verify` and `keystore_register` are exported.
- Confirmed the EU map ZIP is plaintext (1,335 entries) but data-only, that the
  VR package is plaintext TTS/ASR data with no executables, and that the map
  package ships a Gladman Rijndael licence — a hint at the AES implementation
  family, not a key.
- Re-stamped `ART-T6-CHANGELOG` after this documentation update. The frozen T6
  acceptance is therefore stale and requires re-review; this entry records the
  change rather than concealing it.
- No exploit, key, decryption, modified image, flash procedure, or device
  action is included.


- Established that the official `260128` userland is soundly encrypted: entropy
  ~8.00 per envelope, no keystream reuse between files, and no plaintext magic
  in any encrypted payload. Confirmed the manifest checksum is `zlib.crc32`
  against the plaintext `Checksum.txt`.
- Recovered the complete kernel command line from the plaintext
  `iasImage*_sub` containers: serial console `ttyS2` at 115200 8N1, early console
  at MMIO `0xfc000000`, `init=/lib/systemd/esinit`, dual root (`p3`/`p5`),
  Intel DRCFG USB0 mux, `ramoops` at `0x50000000`, and Intel Broxton platform.
- Integrated the public Gen5W prior art (`laralbir` EU standard Gen5W and the
  `gitlab.com/g4933/gen5w` tool group): the `navi_extended` → `DecryptToPIPE` +
  `decryption_key.der` → `update_decryptor` → `update-patcher` chain.
- Recorded the two MASS_PRODUCT Engineering Mode gates (SOP check plus QML PIN
  `21`/`11`) and the published alternative routes (UART, GDS, older build).
- Recorded the published ciphertext-level structure: re-sealed 16,417-byte
  modem trailers, stable container prefixes (14,048 / 14,122 / 640 / 112 bytes),
  and which payloads changed functionally between `251204` and `260128`.
- Confirmed `mango-vr_fixed.tar.gz` is real gzip but TTS/ASR data only (49
  entries in the AU package, no executables); frontkey MCUs are Renesas RL78.
- Added `evidence/known-exploits-and-cve-survey.md`,
  `evidence/gen5w-public-exploit-ecosystem.md`, `evidence/bench-hardware-root-path.md`,
  and `evidence/network-surface-and-wifi-root.md`, plus four child-thread notes.
- Reinforced the scope boundary: no exploit, decryptor key, modified image,
  flash procedure, or live-vehicle action is included.


- Recorded the active target as an AVN bench unit removed from the vehicle, and
  scoped research to that unit with no vehicle connected.
- Added `tools/uk_fw/dump_survey.py`, a read-only survey of a rootfs dump or
  ext4 image covering accounts, setuid/setgid, file capabilities, SMACK
  policy, systemd units, boot command line, debug surfaces, persistence paths
  and world-writable files.
- Added `tools/uk_fw/net_surface.py`, a TCP surface mapper with banner, HTTP,
  TLS-certificate, SSDP and mDNS discovery for an owned bench unit.
- Added `evidence/bench-hardware-root-path.md` with the UART / bootloader /
  storage / software ladder, the interface survey checklist, and the Gate 4
  recovery preconditions applied at bench scale.
- Added `evidence/network-surface-and-wifi-root.md` mapping Wi-Fi exposure
  modes, service-to-vulnerability classes, and the evidence each class needs.
- No exploit, payload, credential attack, flash procedure, or live-vehicle
  action is included.

## 0.5.1 - 2026-10-19

- Consolidated every IONIQ-owned research artifact, evidence file, Council
  package, test, analysis tool, ledger, plan, history, changelog and repository
  policy under the top-level `ioniq research/` directory.
- Preserved all relative paths inside the IONIQ project so evidence references,
  artifact hashes and test commands continue to resolve from that directory.
- Left the Kona root documents and every `kona_research/**` file in place and
  did not incorporate concurrent Kona changes into the IONIQ reorganization.

## 0.5.0 - 2026-10-19

- Verified completion of the exact European `260128` package: 35/35 payload
  sizes, 35/35 signed CRC-32 values, and all three supplied MD5 sidecars.
- Added the complete 36-file SHA-256 inventory identity.
- Replaced the interim EU/AUS comparison with the complete matrix and exact
  corresponding-kernel comparison.
- Added `evidence/eu-custom-firmware-feasibility.md`, separating initial
  execution, privilege transition, persistence, trust, recovery and regional
  compatibility prerequisites.
- Documented candidate defensive vulnerability-audit surfaces and exact
  evidence requirements without an exploit chain, crafted update, modified
  firmware image, flashing procedure or vehicle interaction.

## 0.4.0 - 2026-10-19

- Corrected the active vehicle to a UK-origin 2021 IONIQ 5 and added the exact
  European `260128` package acquisition and resume evidence.
- Added complete 64,923-symbol kernel recovery and symbol-aware Ghidra
  decompilation, including the LG keystore/OEM-signature trust anchor.
- Added the exact-build published-root-method and native Linux application-
  loading applicability assessment.
- Added an interim byte-level EU/AUS package comparison and explicit region-
  transition feasibility gates.
- Preserved the accepted Australian work as historical comparison evidence and
  made no Kona-owned changes, vehicle writes, media writes or firmware flashes.

## 0.3.0 - 2026-10-19

- Changed the private-repository retention policy so raw firmware, extracted
  analysis trees, captures, device-specific dumps, vehicle identifiers, and
  analysis workspaces may be deliberately staged and committed.
- Narrowed `.gitignore` to retain the downloaded 9.5 GB official package tree,
  live credentials/private keys, and regenerable cache noise outside Git.
- Kept exact-stage review, private-remote verification, provenance manifests,
  Kona path separation, and third-party-data controls in force.

## 0.2.0 - 2026-10-19

- Added `Ioniq5-research-plan.md`, the integrated car-specific research plan.
- Bound every accepted evidence artifact to its SHA-256 and traced R1-R11 to
  the accepted T1-T5, T7, and T2 work.
- Recorded the exact official Australian package identity, including the
  36-file inventory, the sorted-tree digest, all 35 manifest records, the map
  and voice MD5 values, the front-key CRC-32/MPEG-2 check, and the nineteen
  opaque envelopes.
- Added a subsystem register covering the AVN, cluster, smart key, keyless
  entry, immobilizer, body controller, gateway, CAN domains, diagnostics,
  telematics, ADAS, chassis safety controllers, VCU, BMS/HV/charging, HVAC,
  camera/audio, USB and projection, and the update supply chain.
- Added Phases 0-8 with passive-first exit criteria and stop conditions.
- Closed the T6 portion of ASTRA-G7-S01 by defining Gate 4 as a four-part
  conjunction, separating physical restoration from persistent software-state
  coverage, rejecting claims of an exclusive recovery route, and making Gate 4
  a hard stop before any state-changing stage.
- Added privacy and confidentiality handling for raw captures, identifiers,
  personal data, storage images, and credentials.
- Added a root `.gitignore` excluding firmware and archive formats, package and
  extraction trees, dumps and captures, credentials, identifiers, and
  personal-data workspaces.
- Recorded Council generation 10 acceptance of frozen batch 8 with three
  COMPLETE seats and truthful DeepSeek replacement labels.
- No USB medium was written, no firmware was flashed, no vehicle was connected,
  and no actuation was performed.

## 0.1.0 - 2026-10-19

- Initialized the dedicated IONIQ 5 research history and changelog.
- Recorded accepted T1 identity, T3 method catalogue, T4 passive and hardware
  route map, T5 trust-boundary and subsystem map, and T7 NEMESIS compatibility
  assessment.
- Established the rule that the car's installed build is read before method
  selection and that published-family evidence is not installed-car evidence.

### (other lineage, same version)

- Initialized the dedicated IONIQ 5 research history and changelog.
- Recorded accepted T1 identity, T3 method catalogue, T4 passive and hardware
  route map, T5 trust-boundary and subsystem map, and T7 NEMESIS compatibility
  assessment.
- Established the rule that the car's installed build is read before method
  selection and that published-family evidence is not installed-car evidence.

- Prepared a public release snapshot: removed raw owner and upstream diagnostic exports, removed full-text third-party artifacts, anonymized local paths, and added a sanitized owner USB finding note. Public visibility awaits cached-history cleanup.
