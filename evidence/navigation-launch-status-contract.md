# Navigation launch-status contract — bounded continuation

Date: 2026-10-26. Static review of **existing saved disassembly**, not a new guest execution or a completed integration fix.

## Question

Why does the recorded AppLauncher-owned AppNavi emit status `5` despite engine initialization and surface creation, and what produces manager `window[0]`?

## Evidence inspected

`work/vm/vendor-userspace-260128/appnavi-SendToAppLauncherNaviLaunchedToExcute.asm`, function `CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()` at `0x2c08ab0`. Runtime context remains the latest completed run cited in the top of `HANDOVER.md`.

## Direct observations from the saved listing

1. At `0x2c08ada`, the function checks static `alreadySendSignal` at `0x7e715c1`. If set, it branches to `0x2c09098`, logs and returns through the common epilogue. Otherwise it sets that flag at `0x2c08b23` **before** constructing/sending the notifications.
2. Before the signal, the function constructs a D-Bus interface and invokes a method with an integer QVariant `30` (`0x2c08ca7`). Exact service/interface/method names are not decoded by this saved listing and should not be guessed.
3. It then constructs a D-Bus signal (`QDBusMessage::createSignal` at `0x2c08e10`). At `0x2c08e31`, it loads literal **5** into the integer QVariant constructor argument, appends that QVariant, and sends the message on the session bus at `0x2c08e67`.
4. In the listed normal control flow between the initial one-shot gate and that send, there is no conditional selecting a different integer from an engine result, persistence value or current window ID. Later camera/persistence/layout processing begins **after** this send.
5. The listing captures the boolean result of `send`, but the already-set one-shot flag is not visibly cleared on send failure in this function.

## Inference and limits

The value `5` is **hard-coded for this particular notification path**, not calculated from an engine return code inside this function. Treating it as a newly propagated map-engine error is therefore unsupported. This does not establish that it means success: the exact message identity, enum meaning, alternate notification paths and caller selection still need recovery.

Moving the startup deadline alone would not change that literal when execution still reaches this function. That is consistent with the preceding runtime deadline-control experiment, not a fresh runtime proof.

The one-shot behavior makes startup ordering and first invocation important. It is not, by itself, a vulnerability or justification for modifying the flag.

**`window[0]` remains unexplained.** The listed signal appends one integer; it does not establish whether manager window state derives from this signal, the preceding method call, a separate surface registration, or default/internal state. Do not assume Wayland surface `3000` is the missing D-Bus window argument.

## Follow-up: exact message identity recovered

A read-only ELF64 section-mapping pass resolved the referenced NUL-terminated
strings against original recovered AppNavi, SHA-256
`62d6e0b3119b99b3fe322ec3bbe03366e9f71ed40dc18b0323d2a9da0e7fa1a3`.
Raw addresses, offsets and byte values are retained in
`work/vm/vendor-userspace-260128/appnavi-notification-strings.json`.

| Virtual address | String / role in listed constructors |
|---|---|
| `0x5fbde8e` | `com.lge.avn.applauncher` — method destination service |
| `0x5fbdea6` | `/Inform` — method object path |
| `0x5fbd5d0` | `com.lge.avn.applauncher.inform` — method interface |
| `0x5fbdeae` | `launched` — preceding method name, integer argument 30 |
| `0x5fa88e8` | `/navigation_map` — signal object path |
| `0x5fbd5f0` | `com.lge.hkmc.avn.appnavi.naviboot` — signal interface |
| `0x5fbdeb7` | `SendNaviBootFail` — signal member, integer argument 5 |

Thus this function first calls launcher `launched(30)`, then emits the explicitly
named `SendNaviBootFail(5)` signal. Launcher process registration and navigation
boot-status notification are separate messages. The name is now byte-backed,
but the meaning of enum 5 and why this caller path is selected remain unresolved.
Earlier references to undecoded message names describe the initial saved-listing
review only and are superseded by this follow-up.

Matching receiver artifact located (not yet analyzed):
`work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/ApplicationManager`.
The authentic launcher is adjacent as `AppLauncher`.

## Receiver artifact triage

ApplicationManager SHA-256:
`5d71539f61a3982b8aac6132a2de14c083fa9ac129792bae750a526ebd771cbc`.
Ordinary symbol inspection reports no symbols; dynamic symbol search returns no
matching handler names. Literal-byte mapping found:

- `SendNaviBootFail`: `0x31a280`, `0x31b1fd`;
- `notifyNaviLaunched`: `0x31a292`, `0x31c6ff`, `0x32bb7b`;
- `com.lge.hkmc.avn.appnavi.naviboot`: `0x31b1b8`.

These addresses equal file offsets for these particular section mappings only.
They are **string locations, not handler entry points or proven cross-references**.
Retained bytes/context:
`work/vm/vendor-userspace-260128/manager-notification-string-locations.json`.

REA provider inspection found no configured Ghidra install directory, no Hopper
launcher, and no configured IDA route in this invocation. No configuration was
changed or new software installed. Continue with available LLVM disassembly /
Qt metadata or an existing project-local Ghidra installation after establishing
its path; lack of REA provider configuration does not mean analysis is impossible.

## Receiver control-flow result — window is a separately latched byte

LLVM disassembly of the identified ApplicationManager is retained as
`work/vm/vendor-userspace-260128/applicationmanager-disassembly.asm`; bounded
extracts are `manager-navi-boot-connect.asm`,
`manager-notify-navi-launched-candidate.asm`, and
`manager-navi-window-setter-candidate.asm` in the same directory. LLVM's nearby
exported-symbol-plus-large-offset labels do **not** name these stripped functions.

- At `0x27de14`/`0x27de29`, code constructs the exact signal member and interface.
  `QDBusConnection::connect` at `0x27de7d` uses slot string at `0x31a291`,
  decoded as `1notifyNaviLaunched(int)` (the leading `1` is Qt slot syntax).
  This confirms the subscription's slot identity, not yet its complete metaobject mapping.
- A routine beginning `0x287e70` formats the exact runtime diagnostic
  `EventFlow2 <-- notifyNaviLaunched[%1] window[%2]` from string `0x31c6f0`.
  It saves the incoming integer, reads **one byte from receiver +0x20** at
  `0x287e89`, and formats that byte as `window[%2]`. It stores incoming status
  at receiver +0x1c (`0x287f21`).
- After obtaining another object, it exits the downstream dispatch if that object
  is null **or receiver +0x20 is zero** (`0x287f3f`–`0x287f44`). Only after that
  gate does it compare status with `5` and perform further processing. Thus the
  observed `window[0]` has a concrete gate consistent with no transition; its
  relationship to actual composed surfaces remains to be recovered.
- The adjacent routine at `0x288070` logs the exact string
  `ApplicationSignalListener::naviWindoeCreate a_nStatus [%1]` (vendor spelling).
  At `0x288115` it stores its incoming low byte at receiver +0x20 and calls the
  above routine with cached status from +0x1c (`0x288112`–`0x28811c`).
- A direct call to this window setter exists at `0x19108d`; tracing that caller
  is the next producer question. Another call to the status routine occurs at
  `0x2e2c16`, potentially useful for confirming Qt dispatch mapping.

**Revised bounded conclusion:** manager `window[0]` is not a second argument
supplied by AppNavi's one-integer boot signal and is not directly an IVI surface
ID in this routine. It is a separately stored byte updated by a window-create
notification path. There is no basis to change it to surface ID 3000 or force it
true. Recover and satisfy the authentic window-create producer contract instead.
Status `5` still has distinct handling once the window gate clears; its complete
enum interpretation is not yet established. No runtime transition is newly proven.

## Window producer narrowed to background-information callback

Following direct caller `0x19108d` reaches a routine beginning `0x190c70`
whose exact diagnostic string at `0x2ffa08` is:
`slotNotifyBGInfo surface_id:%1 display:%2 app_id %3`.
The input surface ID is saved from `esi`, display from `edx`, and app-ID QString
from `rcx`. Thus the original hypothesis of a generic status argument is refined:
the earlier routine consumes a background/window-information event.

The route to `naviWindoeCreate(1)` includes a nontrivial predicate:

- `0x190e81` calls helper `0x2052e0` with the incoming display and app-ID string.
  That helper searches a list using the display field and delegates string
  matching to `0x205730`; the exact matcher semantics still need inspection.
- If that helper succeeds and global `0x5c5028` is nonzero, code at `0x191200`
  tests whether the incoming app-ID contains exact case-sensitive `AppNavi`
  (literal at `0x302df7`). If either prerequisite fails, that branch leaves the
  notification predicate false.
- A true predicate reaches `0x191080`, obtains the listener, and calls the
  window setter with literal `1`; it then clears global `0x5c5028` at `0x191092`.
  The global's initializer, writers and intended semantics remain unknown.
- A direct caller into the BG callback exists at `0x2d6611`; this should identify
  its Qt/IVI event origin. Do not assume that surface creation alone delivers it.

The latest host-log text searched did not expose these diagnostic strings; this
bounded absence does not establish that the callback never ran (guest archived
DLT/log coverage still needs inspection). Next inspect helper `0x205730`, writers
of `0x5c5028`, and caller `0x2d6611`, then correlate retained guest evidence for
BG callback display/app identity. No predicate or global was modified.

## Matched predicates and retained-runtime correlation

The inner matcher at `0x205730` compares list entries with `QString::operator==`
(call at `0x20576e`), not substring matching. The enclosing helper selects a
record by **display equality**, then tests exact app-ID membership in its string
list. This is separate from the later `AppNavi` substring check.

Global `0x5c5028` maps to file offset `0x3c5028` with initial 32-bit value
`0xffffffff` (nonzero). The same initial value occurs at adjacent per-application
gates `0x5c5020`, `0x5c5024`, and `0x5c502c`. A bounded search of direct annotated
references in the saved disassembly found only its read and post-notification
clear; this does not exhaust indirect stores. There is no basis yet to blame an
initially zero gate.

The **complete retained latest-run DLT log** was scanned for exact diagnostic
substrings (123,763 lines, SHA-256
`02fa2f7268f574184745739afaa8a3e5e4db61c3b7093f70991e9e93d7a0d972`).
Raw results:
`work/vm/vendor-userspace-260128/navigation-window-event-correlation.json`.

- `slotNotifyBGInfo`: **0**; `send_BG_info`: **0**;
- `slotNotifyFGInfo`: **6**; `send_FG_info`: **11**;
- `naviWindoeCreate`: **0**; `notifyNaviLaunched`: **1**.

Positive chain for AppNavi:

1. Compositor logs `wm_window_created` for surface 3000, `AID(AppNavi)`, at
   `00:04:02.048`, with dimensions **1926×753**.
2. It emits **FG**, not BG, information for AppNavi (`send_FG_info`, DLT line
   44809); ApplicationManager positively logs `slotNotifyFGInfo surface_id:3000
   display:1 app_id AppNavi` (line 44818).
3. At `00:04:02.198`, manager logs `notifyNaviLaunched[5] window[0]` (line 44905).

Thus this is not simply a missing app identity or a wholly missing compositor
notification: an authentic AppNavi **FG callback demonstrably arrives**, while the
identified window-created latch is updated through the **BG callback** path.
The retained log does not prove lossless collection or absence of every unlogged
BG event. Earlier partial host-log searches are superseded by this explicit
retained-DLT scan.

**Next hypothesis to test:** compositor FG/BG classification and event routing,
including whether the unexpected 1926×753 geometry contributes. Do not treat the
geometry as causal without tracing the compositor's classification predicate.
The harness already exports `QT_WAYLAND_DISABLE_WINDOWDECORATION=1`, so blindly
adding that variable is not a new fix. Original compositor modules are available
under recovered rootfs `/usr/lib/weston/`, including `ivi-window-manager.so`.

## Compositor FG/BG branch recovered

Original recovered `/usr/lib/weston/ivi-window-manager.so` and its `/app/lib/`
copy are byte-identical, SHA-256
`e1ce4d479f1fb84cc44d2faebad748206bdf3003b48a9ccf90e76da17a553bd0`.
Saved LLVM listing:
`work/vm/vendor-userspace-260128/ivi-window-manager-disassembly.asm`.

The local callback at `0xf8e0` (registered through layout-interface offset +0x28
at `0x10fec`) contains the `wm_window_created` diagnostic. It is **not** the
exported `app_surface_created` function at `0xf720`; LLVM's nearest-symbol
labels must not be mistaken for function identity.

At its final notification selection:

```text
0xfab1: load signed width  from surface-properties +0x68
0xfab7: test width
0xfab9: if width > 0 -> send_FG_info at 0xfac6
0xfabb: load signed height from surface-properties +0x6c
0xfabe: test height
0xfac0: if height <= 0 -> send_BG_info at 0xfd90
         otherwise       send_FG_info at 0xfac6
```

**Observed rule:** BG requires **both width and height non-positive**; any
positive dimension selects FG. It does not compare with 1920×720. Consequently,
merely correcting the observed 1926×753 size to 1920×720 would still select FG
at this branch. Decorations are not a supported explanation for this particular
FG/BG choice, although geometry could matter elsewhere.

This rule is consistent with the retained positive FG delivery. The unresolved
contract is now whether the expected vendor startup includes an earlier
zero-sized configure notification, how the producer transitions hidden surfaces,
and whether the VM's current launch/render lifecycle omits that phase. Preserve
natural state ordering: do not send a fake BG event or change live properties
just to satisfy the manager latch.

Next inspect the layout API callback registration (+0x28), the initial
create/configure lifecycle and the matching Qt/IVI client behavior. Also confirm
that the guest loaded the same compositor module bytes before applying the
static rule as exact guest provenance.

## Current image provenance check and analysis checkpoint

Read-only `debugfs` extraction of **both current image paths**
`/usr/lib/weston/ivi-window-manager.so` and `/app/lib/weston/ivi-window-manager.so`
produced the same digest as the original recovered module:
`e1ce4d479f1fb84cc44d2faebad748206bdf3003b48a9ccf90e76da17a553bd0`.
Copies are retained under
`work/vm/vendor-userspace-260128/navigation-contract-audit/guest-{usr,app}-ivi-window-manager.so`.
The latest retained Weston log positively records loading
`/usr/lib/weston/ivi-window-manager.so` at `00:00:05.118`. This corroborates the
path and current image bytes; it is not a historical in-process memory digest.
No `debugfs -w` or guest image mutation was used.

A subsequent shell-module disassembly command and a bounded follow-up command
both timed out at 15 seconds. Completion of the shell disassembly/string scan
is **not** claimed; any generated listing is unverified/possibly partial.
Do not repeat the commands blindly. Check host/process responsiveness and file
completion before resuming the initial-configure investigation. The notification
hypothesis remains unresolved; no VM run should be started until host health
and outstanding-process state are established.

## 2026-10-27 recovery: shell suppresses an unchanged initial zero size

Host command execution recovered; a process snapshot showed no matching QEMU or
LLVM disassembly worker. The retained shell listing was usable for bounded
function reads and fresh bounded disassembly extracts completed. Earlier timeout
warnings remain historical, not a continuing claim that the host is unavailable.

The current image's `/usr/lib/weston/ivi-shell.so` was extracted read-only and
matches the recovered original SHA-256
`8b57db4baa1f35a1a08cffc6de221101a92b37528123d7250c774db03a3b7697`.
Extracts under `navigation-contract-audit/`:
`guest-ivi-shell.so`, `shell-create-initial-size.asm`, and
`shell-configure-size-cache.asm`.

- `application_surface_create` allocates zeroed shell-surface state and explicitly
  initializes its cached width/height (+0x3c/+0x40) to **0/0** at
  `0x9f96`/`0x9f9e`. No configure callback is invoked directly in the reviewed
  create function.
- `ivi_shell_surface_configure` reads actual Weston surface dimensions (+0x68/
  +0x6c), compares them with the cached values, and **returns without calling
  layout configure when both are unchanged** (`0x9c4c`–`0x9c5a`).
- Only a size change updates the cache and calls `ivi_layout_surface_configure`
  (`0x9c5c`–`0x9c66`).

This refines, rather than confirms, the initial-zero hypothesis: a newly created
surface remaining at 0×0 does **not automatically produce** a BG callback through
this shell path. A later genuine transition from nonzero size to zero could pass
the cache check, but target behavior must be observed before relying on it.
The absence of an initial BG event is therefore not yet proof of a missing driver
or shell defect, and injecting one would not reproduce the reviewed create path.

**Resume action:** compare a retained positive BG event (e.g. the older camera/
standby run) with its preceding surface configure/buffer transitions, and trace
AppNavi's real hide/unmap lifecycle. Check whether a null-buffer commit reaches
the shell with changed size, and whether the normal lifecycle differs under the
current VM render/launcher adaptations. No image edits are justified yet.

## Positive BG control: notification follows nonzero → zero transition

An older retained `full-chain-timeout120-legal-reason11-threaded-pointer-confirm`
DLT log (SHA-256
`042a1d1eadad2d6156ab728c1b33630f43a3f1a12d552722a53e42a8a7169ec1`)
provides positive controls for both AppCamera and AppStandbyClock:

- Camera surface 2080 first configures at **1926×753**, sends FG, then ~80 ms
  later configures at **0×0**, sends BG, and manager logs `slotNotifyBGInfo`.
  Relevant original lines: 4416, 4451, 4489, 4493, 4500.
- Standby surface 1000 likewise first configures at **1926×753**, sends FG,
  then ~40 ms later configures at **0×0**, sends BG, and manager receives it.
  Original lines: 5565, 5603, 5620, 5624, 5631.

Retained 13 selected events with exact line/range provenance in
`navigation-contract-audit/positive-bg-event-control.json`.

This establishes a **working VM notification mechanism** in that earlier run,
consistent with the recovered size-cache and classification rules. It also
shows the decorated initial geometry can coexist with successful later BG
notification. It does not prove identical process/render conditions or that
AppNavi should follow the same lifecycle without tracing its hide operation.

Next compare these positive-control hide/unmap transitions against AppNavi's
`onVisibleChanged(0)` and Wayland buffer attach/detach/commit sequence. Focus on
why AppNavi does not reach a zero-size configure after its first nonzero frame,
not a wholesale replacement of a notification transport already shown working.

## AppNavi visibility callback is not proof of surface unmapping

Bounded disassembly of the original AppNavi is retained in
`navigation-contract-audit/appnavi-visible-changed.asm` and
`navigation-contract-audit/appnavi-clear-screen.asm`.

`NimoExSLScreenLinux::onVisibleChanged(bool)` at `0x335be80`:

- logs the incoming boolean;
- for the primary screen, first false visibility sets `g_firstTimeHideByWM`;
- if `g_NaviLaunched` is already true, invokes the existing one-shot launch
  notification function at `0x335c228`;
- then calls `NimoExSLScreen::clearScreen()` at `0x335bf84`.

The inspected `clearScreen` normal path sets renderer viewport, clears buffers
and swaps rendering buffers (`0x3368480`, `0x336848e`, `0x3368493` onward).
It does **not establish a null Wayland buffer attachment or parent-QWindow hide**.
Virtual calls and downstream implementations remain separate analysis boundaries.
A `visible changed (0)` diagnostic must therefore not be used alone as evidence
that the parent surface was unmapped or configured to 0×0.

Retained latest-run logs positively show `onVisibleChanged(1)` around 00:03:21,
`onVisibleChanged(0)` at 00:04:02.071, and the first-hide diagnostic around
00:04:04.188. This corroborates callback execution without supplying the missing
zero-size parent configure. A later branch compares elapsed time against 49,999
ms, but its downstream purpose has not been recovered; no timing patch is proposed.

Next identify the source/connection of this visibility callback and inspect the
**parent Qt window** hide path separately from native map-screen clear/swap. Then
correlate actual Wayland attach/detach/commit evidence rather than equating an
application visibility boolean with compositor unmapping.

## Explicit Qt hide path located; primary-screen invocation not demonstrated

Retained symbol inventory and bounded function listings under
`navigation-contract-audit/`: `appnavi-symbols.txt`,
`appnavi-create-window.asm`, `appnavi-foreground.asm`, and
`appnavi-base-foreground.asm`.

`NimoExSLScreenLinux::onForeground(bool,bool)` at `0x3361df0` contains a real
`QWindow::hide()` call at **`0x3362275`**. It is reached for a false foreground
request only after the base `NimoExSLScreen::onForeground` returns a true result
and screen-ID branching admits it. The diagnostic immediately preceding the
hide call decodes as `set hide NimoExSLScreen(%d)` (`0x60b812e`). Thus there is
an authentic Qt hide path; it must not be replaced with renderer clear/swap.

A bounded scan of the latest retained DLT for PID 908's `onForeground` diagnostics
shows native widget screen 6 and screens 9/10, but no corresponding primary
screen-1 foreground or `set hide NimoExSLScreen(1)` diagnostic. This is log
coverage, not proof that no such invocation occurred. The creation function also
contains genuine `QWindow::show()` calls for its screen-specific branches.

**Next:** inspect the constructor's Qt signal connections to establish exactly
which signal produces `onVisibleChanged`, and trace primary-screen foreground
requests/base deduplication separately from map-widget screen 6. A Wayland
null-buffer trace remains necessary to determine whether actual Qt hiding is
requested but not delivered, versus no parent hide being requested at all.

## Constructor wiring and QtWayland hide branch — 2026-10-27

Constructor `0x335b080` connects the **same object as sender and receiver**,
using exact strings `2visibleChanged(bool)` → `1onVisibleChanged(bool)` at
`0x335b287` (AutoConnection). Strings and addresses are retained in
`navigation-contract-audit/appnavi-constructor-signal-strings.json`; constructor
listing is `appnavi-screen-constructor.asm`.

This supersedes any suggestion that the callback might be merely an unrelated
internal map-state boolean. It is the QWindow-derived object's actual visibility
signal. It still does not prove platform-level buffer detach/commit.

Recovered `libQt5WaylandClient.so.5.4.1`, SHA-256
`0f2ba91c646ad99f00efde313150179bb5a7dc0a1a2a69bb778cfea3112955c9`,
provides `QWaylandWindow::setVisible(bool)` at `0x63ce0`:

- false path sends an empty expose event and flushes window-system events;
- if the object survives, it calls virtual slot **+0x60** at `0x63dbd`;
- **only a zero return** branches to `attach(nullptr,0,0)` at `0x63ea9` and
  `wl_surface::commit()` at `0x63eb2`;
- nonzero skips that explicit detach/commit branch and may call SHM backing-store
  `hidden()` only if such a backing store exists.

For recovered client graphics plugin
`qt5/plugins/wayland-graphics-integration-client/libwayland-egl.so`, relocation
`0x20d5a8` uses inherited `QWaylandWindow::setVisible`; the same primary vtable's
+0x60 entry (`0x20d598`) resolves to local function `0x80e0`, which **returns 1**.
Thus this plugin's inherited false-visibility path skips the explicit null-buffer
commit. This is an artifact-level control-flow result, not yet proof that the
latest guest uses these exact bytes or this precise instance/vtable.

Retained: `qtwayland-set-visible.asm`, `wayland-egl-relocations.txt`. The virtual
operation's original source name/enum is not assumed from its return value.

**Next acceptance boundary:** verify current guest QtWayland/client-plugin byte
identity and actual selected backend, then observe AppNavi's false-visibility
path and surface commits. Only after that consider a narrowly scoped VM hide
compatibility adapter that responds to an authentic hide request; do not patch
manager state or manufacture a BG signal. Explain why older positive controls
used a different path before treating this as the sole root cause.

## Current guest QtWayland bytes verified; runtime backend still unknown

Read-only `debugfs` extraction from the current image confirms:

| Path | SHA-256 |
|---|---|
| `/usr/lib/libQt5WaylandClient.so.5.4.1` | `0f2ba91c646ad99f00efde313150179bb5a7dc0a1a2a69bb778cfea3112955c9` |
| `/usr/lib/qt5/plugins/wayland-graphics-integration-client/libwayland-egl.so` | `ef0c92395c75c91869dd30883ea944ad131517f2f37c1d7d0b704c8a3bf95c1a` |

Both match the original recovered files analyzed above. Retained copies:
`navigation-contract-audit/guest-Qt5WaylandClient.so` and
`navigation-contract-audit/guest-qt-wayland-egl.so`.

However, the saved latest launcher log does not supply a matching backend-load
record, and the retained evidence directory inspected does not provide an AppNavi
`/proc/PID/maps` snapshot. Runner environment sets `QT_QPA_PLATFORM=wayland`
with library search order `/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:
/usr/lib:...`; that platform setting and software EGL success do **not** by
themselves prove which Qt graphics-integration plugin or library copy was loaded.
The static plugin branch must not yet be described as observed guest execution.

The next bounded VM experiment should be **observational first**: capture the
original launcher-owned AppNavi `/proc/PID/maps`, `/proc/PID/environ` with secrets
excluded, exact mapped Qt/client-plugin identities, and hide-path Wayland requests.
Keep current success/failure controls and do not change hide behavior in that run.
Use retained complete evidence as baseline. No new VM execution occurred for
this provenance check.

## Observational VM run completed — 2026-10-27

A new bounded run used the **existing guest baseline runner unchanged**, wrapped
by `navigation-contract-audit/observe-loaded-backend.sh`. QEMU snapshot mode,
no NIC, 1536 MiB, 900-second host bound; completed command exit 0 without timeout
in 404.87 seconds of harness elapsed time. Existing timing/rendering adaptations
remain in force; no hide adapter or synthetic callback was introduced.

Artifacts under `navigation-contract-audit/`:

- observer SHA-256 `4ddf1fee3a7fcb5b3fc8b0873ab0d5dac625ccfacf45a973bfab6947df279880`;
- `backend-observation-host.log`, SHA-256
  `2e961f8277683f21d40172b9e6c34816c04c28893519c4f1ccb3a82417464085`;
- complete archive `backend-observation-evidence.tar.gz`, SHA-256
  `6019ec6e42cacce8a41fdc79c7dd9705487efdc0a53b741313e6b5b7aad01d84`;
  serial-announced digest independently matches decoded bytes; extracted with
  Python tarfile's data filter;
- `backend-observation-summary.json`: mapped identities, allowlisted environment,
  notification events and manager queries; 26 AppNavi maps snapshots.

**Runtime identity established:** AppNavi maps the analyzed
`/usr/lib/libQt5WaylandClient.so.5.4.1` and
`/usr/lib/qt5/plugins/wayland-graphics-integration-client/libwayland-egl.so`;
selected mapped-file digests match the original artifact digests above. It also
maps `libqwayland-generic.so`, `libivi.so`, `libbradient.so` and project Mesa 18
`swrast_dri.so`. This proves paths and corresponding file identities, not memory
contents, exact virtual-call execution, or lack of preload interposition.

Allowlisted actual environment includes:

```text
QT_QPA_PLATFORM=wayland
QT_WAYLAND_SHELL_INTEGRATION=ivi
QT_WAYLAND_DISABLE_WINDOWDECORATION=1:1
GALLIUM_DRIVER=llvmpipe
QSG_RENDER_LOOP=basic
LD_PRELOAD=/appnavi-egl-no-msaa-preload.so
WAYLAND_DEBUG=1
```

The **duplicated decoration value `1:1`** and mapped decoration plugin are new
runtime observations. A parser consequence is not yet verified. It is a separate
VM environment issue; fixing window dimensions alone still cannot change the
previously recovered any-positive-size FG classification rule.

**Outcome:** authentic Home visibly renders before Navigation (inspected
post-settle screenshot SHA-256
`ce36d57eeab78850d341d7815542ece8aac759277895f316be53b11a1b227bd3`).
Manager state reproduces `11/11 → 35/11 → 11/11`; AppNavi FG event arrives, then
`notifyNaviLaunched[5] window[0]` persists. Importantly, the final return screenshot
is **black**, SHA-256
`413b741283d17224276036a9ad3a67a418d5e0804e563ef900f9d926af3ff44d`.
Do not equate manager return state with visible Home restoration in this run.
This does not supersede older positive visible-Home evidence, but demonstrates
integration/timing variability.

No raw `wl_surface@`/null-attach trace appeared in inspected launcher/DLT/host
logs despite `WAYLAND_DEBUG=1`. Actual hide-path detach execution remains
**unobserved**. Next establish where child stderr goes, or add a bounded
observation-only interposer/capture for the genuine setVisible/null-attach path.
Do not implement a hide behavior change on the assumption that protocol tracing
already proved its absence.

Late serial output also contains AppCamera/AppEURadio segmentation-fault messages
near guest cleanup. They are retained, not classified as security bugs or
attributed without a causal trace.

**Validation:** 168 repository tests pass; shell syntax check and
`git diff --check` pass. Post-run base-image SHA-256 independently rehashed to
unchanged `4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f`.
The observer samples and hashes files, so timing overhead is explicitly present.

## Decoration environment parsing recovered

`QWaylandDisplay::supportsWindowDecoration()` at `0x60b90` reads exact
`QT_WAYLAND_DISABLE_WINDOWDECORATION`, passes it to
`QByteArray::toInt(nullptr, 10)` (`0x60c12`–`0x60c21`), caches whether the result
is nonzero, and returns false for decoration support when that disable flag is
nonzero. Retained: `navigation-contract-audit/qtwayland-decoration-check.asm`.

Thus this is a **scalar decimal input**, not a colon-delimited list. The actual
`1:1` inherited value is malformed for the consumer. Standard QByteArray integer
conversion rejects nonnumeric trailing characters and returns zero on failure;
that expected parser result is inference pending an exact-library execution
control, not newly measured execution here. The observed loaded decoration plugin
and decorated Home screenshot are consistent with the disable setting not taking
effect. Parsing is cached on first use, so changing the live environment later
would not reliably fix an already initialized process.

A future single-variable environment control should prevent pre-setting a scalar
that AppLauncher appends, then verify the child receives exactly `1` before Qt
initializes. Do not call that a Navigation fix: even undecorated positive-size
surfaces still select FG, and the actual hide/null-buffer path remains separate.
No environment setting or image was changed during this static parser review.

## Decoration-unset control: negative startup result

The proposed single-variable environment control was executed in QEMU snapshot
mode with the same backend observer. The original baseline source digest was
verified first (`906e734012a9a9cac35aed2e9258674215b407a93cdce9e58024a2f78bf8dd9f`). Only the
pre-set decoration export was replaced with `unset`; files were transferred into
**guest `/tmp`**, not injected into the base image. Exact source delta retained
in `navigation-contract-audit/decoration-control-delta.patch`.

Artifacts under `navigation-contract-audit/`:

- `decoration-control-run.json`: control/observer identities and timing;
- `decoration-control-host.log`, SHA-256
  `9df711936074c3be7b129b8c80b55f1a8a9f102e910d35c4e1c15228499162dc`;
- complete `decoration-control-evidence.tar.gz`, SHA-256
  `648b5d30c169b2e4adaa2e8cf069742fd5b3d779b0ef1d6d7e63fead7f6910e9`;
  decoded digest matches serial announcement; safe extraction completed;
- `decoration-control-summary.json` with explicit semantic-failure classification.

Harness completion: command exit 0, no timeout, 474.71 seconds. **Feature result:
failed before Navigation.** Camera and Standby repeatedly segfault; authentic
agreement remains false. AppNavi never starts (zero observer snapshots), manager
current/drawing queries remain 0/0, and every screenshot has the retained splash
hash `b316a82a1f8f726163c55705d6d6522603cbf9fbb3bb5b85a9d247876e0b9a83`.

This run does **not** verify the intended AppNavi child value `1`, undecorated
geometry, or backend hide behavior. The observer targeted AppNavi and therefore
missed early Camera/Standby environment/load state. Do not call the unset change
a fix or adopt it globally. Repeated crash symptoms are not a demonstrated
security vulnerability; causality/reachability remain uncharacterized.

Base image independently rehashed unchanged at
`4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f`.
Existing working baseline is preserved. No automatic retry is warranted. Next
capture early Qt-client environment and crash context in a focused control,
separately from the primary hide-path investigation; do not repeat the full
Home/Navigation sequence when its initial gate cannot pass.

## Decoration-control crash instruction identified

The repeated early-client crash addresses resolve to recovered libc file offset
`0x128dde`. Original `libc-2.25.so` SHA-256:
`04946077dfd7554a20438ee581367e3995931b26c9ee516ffeeecdc0ee9f331f`.
Bounded listing retained in
`navigation-contract-audit/decoration-crash-libc-site.asm`.

At that location, the instruction is **`vmovntdq %ymm0,(%r9)`**, a non-temporal
vector store, surrounded by a bulk-copy-style loop. LLVM's nearest exported
`__nss_passwd_lookup+offset` label is not a reliable internal function identity.
The guest reports a memory-write fault (error 6), not SIGILL; this does not prove
that AVX is unsupported or that QEMU caused it. Destination mapping, copy length,
caller and register state remain unknown without crash context.

Read-only command-manifest comparison confirms the canonical latest piefix run,
the backend observation run and decoration control all used
`max,vendor=GenuineIntel` and 1536 MiB. Older runs with `-avx2` exist, but must
not be conflated with this canonical baseline. A future CPU-profile control is
an explicit additional variable, not something silently changed with decorations.

Next capture a short early-client crash with call stack/registers and allowlisted
environment, or compare a separately labelled no-AVX2 control if evidence warrants.
Do not repeat the full failed agreement/navigation flow or classify a vendor
memory-safety vulnerability solely from this instruction-level symptom.

## Lower-overhead crash capture option established

A bounded inventory found guest `strace`, but no `gdb`/`gdbserver` in the
recovered rootfs; no debugger installation is needed for an initial capture.
Exact vendor configuration enables `CONFIG_ELF_CORE`, `CONFIG_BINFMT_ELF`,
`CONFIG_CORE_DUMP_DEFAULT_ELF_HEADERS`, `CONFIG_COREDUMP` and `CONFIG_PROC_FS`
(`work/eu-260128/kernel.config`, lines 196, 631–636, 3684).

**Proposed focused experiment (not run yet):** in a disposable snapshot, set a
project-guest `/tmp` core pattern, a bounded core-size resource limit, and inherit
`/proc/self/coredump_filter=0x10` before starting the authentic launcher. Capture
only the early startup interval, stop after the first relevant completed core(s)
or a short deadline, then clean up guest processes and archive diagnostic files.
Do not enter the full agreement/navigation sequence. Keep the failed decoration
control's CPU and other settings unchanged for comparability.

The header-only memory filter is intended to preserve ELF core notes (registers,
signal information, thread identities and mapped-file records) while omitting heap
contents. Kernel behavior and notes must be verified from the produced core.
**It will not supply a reliable stack backtrace without stack memory.** Treat
registers and mapping context as the first acceptance boundary; only expand to a
bounded memory/ptrace capture if those leave a concrete gap. Core-size limits can
truncate output, so completeness must be checked, not assumed. Retain cores only
inside the project and do not publish raw process state.

This reuses the stock kernel's capture facility rather than adding a timing-heavy
sampler or installing a debugger. No `/proc` setting has been changed yet.

## Focused early-client core capture completed

A new snapshot-only run used `navigation-contract-audit/capture-early-core.sh`
(SHA-256 `a59d5212173c444c32d65069725d8935312ef9d1520a89892a6e484c110edf45`).
It reuses the failed decoration control's startup prefix, but stops after a
completed early core or a 90-iteration startup bound; no agreement or Navigation
requests occur. Core limit set to 32768 shell blocks; the requested filter was
`0x10`, but its recorded readback was **`00000000`**. Do not assume requested
filter semantics were established. All `/proc` settings were snapshot-local.

Harness command exit 0, no timeout, elapsed **44.83 seconds**. Captured one
AppCamera core, **81,920 bytes**, eight thread status notes, plus signal and
mapped-file notes. Decoder bounds-checked ELF64/x86-64 headers, note payloads and
file ranges; report: `navigation-contract-audit/early-core-summary.json`.
The core's PT_LOAD file sizes total 20,480 bytes; the fault thread's stack segment
has **zero stored bytes**, so no reliable caller/backtrace is available.

Artifacts:

- `early-core-evidence.tar.gz`, SHA-256
  `10fbb21b674ab1795c5e2b52d4e04ad47611f8674c4ac5ed43d283322c24987c`;
  serial-announced digest matched decoded bytes, safe extraction completed;
- `early-core-host.log`, `early-core-run.json`, extracted `early-core-evidence/`;
- early client allowlisted environment positively records
  **`QT_WAYLAND_DISABLE_WINDOWDECORATION=1`** and IVI shell integration.
  This verifies the early-client child value that the full failed run missed,
  but does not verify AppNavi behavior.

Fault thread PID/TID 834:

| Item | Recorded value |
|---|---|
| Signal | SIGSEGV (11), code 1 / SEGV_MAPERR |
| RIP | `0x7f8133258dde`, mapped libc file offset `0x128dde` |
| Fault address / R9 | `0x7f811695efc0` |
| RDI | `0x7f811695f000` |
| Writable destination mapping | `[0x7f811695f000, 0x7f8116ea5000)` |
| RDX inside copy loop | `0xffffffffffffff60` |
| RSI / RCX | `0x82d0678e80` / `0x82d0678dc0`, both in recorded heap mapping |

**Established:** the `vmovntdq` store targets an address **64 bytes below the
writable mapping start** and outside every recorded PT_LOAD memory range. Signal
notes agree with an unmapped-address write. This is more specific than the earlier
bare crash address.

**Not established:** original memcpy/memmove identity/arguments, caller, allocation
provenance, original length, prior corruption, instruction-emulation correctness,
or attacker-controlled reachability. RDX is already modified inside the loop and
must not be relabelled as the caller's original negative length. This remains a
VM compatibility/crash investigation, not a confirmed exploitable vendor defect.

Base image independently rehashed unchanged. Shell syntax and diff whitespace
checks pass; no new full-suite result is asserted. Next obtain a **bounded stack
or caller observation at the fault**, preferably adapting the existing ptrace
sampler rather than dumping the whole anonymous heap. Preserve CPU and environment
controls and do not re-enter the full failed Navigation sequence.

## Bounded fault-time stack capture completed

Implemented `tools/uk_fw/guest/ptrace_crash_observe.c` as a VM-only diagnostic,
compiled statically for x86-64 Linux/musl with project-local Zig and
`-Wall -Wextra -Werror`. Build identity/flags and limits are retained in
`navigation-contract-audit/ptrace-crash-build/build.json`.

The observer permits only an explicit PID >1 resolving to authentic AppCamera or
AppStandbyClock path, uses PTRACE_SEIZE rather than inducing a group SIGSTOP,
captures the selected main thread only, caps the stack at **64 words** and maps
at **64 KiB**, and re-delivers the original fatal signal on detach. It does not
write target registers/memory or suppress the crash. Timeout/cancellation and
external group-stop paths were reviewed but not dynamically tested; this is not
a general production debugger. VM experiment runner is `capture-early-ptrace.sh`.

Short snapshot experiment: command exit 0/no timeout, **43.7 seconds** harness
elapsed. Guest invalid-PID and disallowed-executable tests pass. Captured 64
readable stack words and siginfo from AppCamera main thread, then logged
`DETACHED signal_redelivered=11`.

- Complete `early-ptrace-evidence.tar.gz` SHA-256:
  `e0884a3c11582ed2b986db28f2673b7fde9297a1871f2633ad13672b2dfdeaae`;
- host-log SHA-256:
  `45b07d1dd3f87b00cb306e1d56f3253beccbb819eea239df105b7a887daab86a`;
- decoded archive digest matches guest announcement; safe extraction completed;
- `early-ptrace-summary.json` resolves stack pointer candidates against mappings.

### Caller and suspicious width-cache ordering

Top captured stack word resolves to vendor `/usr/lib/libEGL.so.1.0.0`, file
location **`0x16f8e`**. Original recovered and current-image library match
SHA-256 `0c373e50d1a4700c2161628c2a2b61a25a9b5abbcd7bb52ccc763cf5020e3d53`.
Disassembly proves `0x16f8e` immediately follows a real `memcpy@plt` call at
`0x16f89` in **`dri2_wl_swrast_put_image2`**. This supports a concrete immediate
caller rather than interpreting every executable-looking stack word as a frame.
Other stack pointers into project Mesa `swrast_dri.so`, vendor EGL and Qt are
candidates only, not a fully unwound call chain.

The caller derives byte stride from surface field **+0x2c before calling
`swrast_update_buffers`** (`0x16efa`–`0x16f19`). The update routine can write new
values to +0x2c/+0x30 from the native window (`0x16acc`–`0x16ad6`). The subsequent
copy uses the earlier cached width-derived stride rather than reloading it.
Captured R13 and R14 are both **`0xfffffffffffffffc` (-4)**; the caller moves R14
to memcpy's RDX immediately before the call. The expanded inspected libc loop
does not reference R13/R14. This strongly implicates a stale/invalid negative
width-derived copy count, but an entry probe is still needed before claiming the
original arguments or precise initialization sequence are measured.

Retained `egl-crash-caller.asm`, `egl-update-buffers.asm`,
`libc-copy-loop-expanded.asm`, exact mapped library copy and register/stack/maps.
The fault repeats SEGV_MAPERR at an unmapped address 64 bytes before a writable
buffer, consistent with the previous core-only experiment.

**Scope:** vendor EGL is running with a project-supplied Mesa 18 software DRI
module, not a stock Intel-graphics deployment. Invalid initialization/order or
mixed-stack compatibility may be required. Track as **I-001** in the defensive
register, not a confirmed remotely reachable vendor vulnerability.

**Next:** observe the surface width before/after buffer update and the actual
memcpy entry arguments, then choose a fail-closed VM compatibility adaptation
that validates/refetches dimensions. Do not patch libc's copy loop or enable
huge negative-length copying; do not call this the original Navigation root cause.
All 168 repository tests pass; base image independently rehashed unchanged.
Source compile, guest negative tests, live capture and diff checks pass. No
independent model review was obtained due the recorded worker host failure.

## Council-reviewed measurement plan

Parallelism planning and a three-seat Council reviewed the next bounded step.
The accepted artifact is a **plan only** at package fingerprint
`c59ac8a0d4ece96fd8fab5fe8a6795789697c95394d6e548a02dc8484052bbb5`;
Council packet SHA-256 is
`528649b5b337fb0b76bafd6cb9b020e572851ec33136c6d0927a5c38a12ef790`.
The checker rehashed the package and returned `COMPLETE` with all three seats
present. This does not accept an observer, VM run, measured argument set or fix.

The plan corrects a prior shorthand: captured `-4` establishes neither original
width `-1` (32-bit arithmetic may wrap) nor that width changed during the failing
update. A complete observation must correlate raw pre/post surface fields, update
outcome/selected-buffer state, EGL call-site arguments and the actual resolved
copy-entry arguments while accounting for PLT/lazy binding/IFUNC behavior.
Candidate addresses remain conditional on complete binary/byte validation.

Council suggestions, retained for downstream contracts, require recording the
mapped vendor EGL and project Mesa/DRI identities together; explicit numerical
read/map/output caps; debugger-state restoration; and host-owned disposable-VM
termination after timeout or restoration failure. Mixed-stack applicability and
I-001 qualifications remain unchanged.

The requested DeepSeek EC-01/EC-02 research did not execute. Current policy
requires the direct DeepSeek API provider via `deepseek/...`; OpenCode and other
intermediaries are forbidden fallbacks. The live tool rejects
`deepseek/deepseek-v4.1-flash` as unknown. The validated ledger therefore keeps
both tasks blocked. Do not implement or launch the experiment until a supported
direct route is available or the owner explicitly selects another direct model.

## Next exact actions / acceptance

1. **Done:** resolved exact method/signal strings and retained artifact identity and address mapping above.
2. **Partially done:** exact slot subscription and diagnostic routine identified; trace caller `0x19108d` into the window-create setter and confirm the Qt dispatch mapping. Recover the status-5 branch semantics and other message senders.
3. Inspect all callers of this one-shot function and the normal first-window/initialize callback ordering; reuse the existing `appnavi-sendfail-callers-33b49.asm` and `appnavi-sendfail-caller-335c228.asm` before generating new analysis.
4. Only then define a narrowly observed VM run proving the authentic transition `35 → 30`, current/drawing Navigation, valid surface composition and return to Home. No synthetic success notification or patched enum is acceptable evidence.

No firmware/image changes, new processes, child threads, or security findings were produced by this static review.
