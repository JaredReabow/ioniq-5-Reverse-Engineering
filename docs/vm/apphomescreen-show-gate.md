# AppHomeScreen — what gates `QWindow::show()` (static analysis)

Target: `work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/AppHomeScreen`
(ELF64 x86‑64, stripped, Qt 5.4.1, full `DT_NEEDED` on libQt5Quick/Gui/Qml/DBus, headless-safe
copy of the app also present under `.../mango-rootfs/app/share/AppHomeScreen/`).
Read-only analysis. No QEMU was run. QML/vendor-library evidence below is read-only.

Confidence labels: **[A]** verified in more than one independent way, **[B]** single strong
evidence, **[C]** inference / speculation.

---

## 0. Method (how addresses were turned into vendor names)

1. `.rela.plt` gives all 843 imported Qt entry points and their PLT stubs; `objdump -d` prints the
   mangled import name at every `call`. That is how the Qt call sites below were found.
2. The binary is stripped but **every function still has an `.eh_frame` FDE**. Parsing `.eh_frame`
   (9 687 FDEs, offsets 0x28060 … 0xc42dc0, contiguous inside `.text`) gives exact function
   `[start,end)` ranges, so any instruction address can be mapped to its enclosing function. **[A]**
3. The vendor logging macro embeds `__PRETTY_FUNCTION__`-style literals in `.rodata`
   (253 of the form `void AppHomeEngine::…`). Each function that logs contains exactly one
   `lea reg,[rip+…]` pointing at its own signature string, so scanning `lea` operands per function
   recovers 1 714 vendor symbol names with no guessing. Example: `0x7a7800` contains
   `lea … # 0xc57c20` → literal `"void AppHomeEngine::slotReqLoadWidget()"`. **[A]**
4. Confirmation of the naming rule: the function that contains
   `# 0xc5ad80` → `"int AppHomeEngine::inter_show_window_fg(int, int, int, int, int, bool)"` is
   entered with 6 integer/bool args in exactly the order the log line prints
   (`appid / reason / plane / avmode / command / temporal`) and returns the 3rd argument — which is
   exactly what the D‑Bus interface XML declares as `response_plan`. **[A]**

---

## 1. Answer in one paragraph

`QWidget` is not used at all; the app is `QQuickView`-based. The binary imports **only two**
`QWindow` visibility entry points — `QWindow::show()` and `QWindow::hide()` (no
`QWindow::setVisible`) — and `QWindow::show()` has exactly **three** call sites in **two**
functions:

* `AppHomeEngine::slotReqLoadWidget()` — `0x7a7a15` (the *real* boot path),
* an unnamed helper `0x7ef480` reached only from
  `AppHomeEngine::inter_show_window_fg(…)` — `0x7ef4d8` and `0x7ef668` (the D‑Bus `show_window_fg`
  path).

The boot path is gated by a single one-byte flag `this+0x229` (`m_isLoadedHomeWidget`) and, upstream
of it, by the fact that the **HomeScreen main QML component must actually be instantiated**: the only
thing in the whole system that emits `AppHomeModel::requestLoadWidget()` is a
`Component.onCompleted` block inside `QHMI_HomeScreenMain_Wide.qml` /
`QHMI_HomeScreenMain_Advanced.qml`. If that component is never created, `slotReqLoadWidget()` is
never called and no window is ever shown — which matches every measurement you have, including
"scene graph builds textures" (the scene graph exists and is polished, but is never exposed).

Second, independent finding: after `show()` the app tags the surface through the vendor IVI‑shell
integration, and that integration **blocks the calling thread** until the HMI service answers a
surface‑id request. That is a second, downstream gate that can swallow `show()` even when the app
asks for it. Both gates are described below with the exact strings.

---

## 2. The three `show()` call sites

| # | call site | enclosing function | symbol source |
|---|-----------|--------------------|----------------|
| 1 | `0x7a7a15  callq 0x295f0 <_ZN7QWindow4showEv@plt>` | `0x7a7800`–`0x7a7b72` | `# 0xc57c20` = `"void AppHomeEngine::slotReqLoadWidget()"` |
| 2 | `0x7ef4d8  callq 0x295f0` | `0x7ef480`–`0x7ef6d7` | no signature literal (small helper, likely a `static`/lambda or AI‑obfuscated); **caller** is `inter_show_window_fg` |
| 3 | `0x7ef668  callq 0x295f0` | same `0x7ef480` | same |

`QWindow::hide()` has **one** call site: `0x7eeb43` inside
`0x7ee800`–`0x7ef123` = `"void AppHomeEngine::hideFrontView()"` (`# 0xc5a6c0`).

Relevant imports present (and *absent*): `QQuickView::QQuickView(QWindow*)` `0x2a650`,
`QQuickView::setSource(QUrl)` `0x28c00`, `QQuickView::rootObject/rootContext/engine`,
`QQuickWindow::setPersistentOpenGLContext/setPersistentSceneGraph/setClearBeforeRendering/setColor`,
`QGuiApplication(int&,char**,int)` `0x2b370`, `QGuiApplication::exec()` `0x29b60`,
`QGuiApplication::platformNativeInterface()` `0x29130`. There is **no** `QWidget`, no
`QQuickWindow::show`, no `QQuickItem::setVisible`, no `QWindow::setVisible` import. **[A]**

### The helper `0x7ef480` (`show` + show-event + IVI plane tag)

```
7ef4aa  QQuickWindow::setPersistentOpenGLContext(false)
7ef4b8  QQuickWindow::setPersistentSceneGraph(false)
7ef4c4  call qword <QWindow::isVisible()>       ; rdi = *(this+0xe0)
7ef4d2  jne 0x7ef668                             ; already visible -> show() anyway
7ef4d8  call qword <QWindow::show()>             ; site #2  (rdi = *(this+0xe0))
7ef4ea  QEvent::QEvent(0xd1) ; QCoreApplication::notifyInternal(window,&ev)
7ef517  QGuiApplication::platformNativeInterface()
7ef527  vtbl[0xd0/8](pni, window->handle(), QVariant("1"), QVariant("displayPlane"))   (*)
7ef5b0  … then AppHomeEngine::slotNaviVisibleChanged(false/true, true)
```
`(*)` the two operands are static `QStringData` at `0xc5b2c0` = `"1"` and `0xc5b2e0` =
`"displayPlane"`. **[B]** (member pointer `this+0xe0` is the `QQuickView` throughout: it is
assigned from the `new QQuickView(0)` in the `AppHomeEngine` constructor at `0x7e7103`–`0x7e7108`.)
`"displayPlane"` is implemented by the vendor library `.../usr/lib/libivi-platform-interface.so.1.0.0`
(`IviShellSurface::setProperty`, `ivi_hmi_client::set_display_plane`). **[A]**

The same helper is called from exactly one place in the whole binary:
`0x7efcf5  callq 0x7ef480` inside `inter_show_window_fg`. **[A]**

---

## 3. Path A — the boot path (`slotReqLoadWidget`)

### 3.1 The guard

```
7a7811  movzbl 0x229(%rdi),%r14d          ; load m_isLoadedHomeWidget for the log line
7a794c..  log "m_isLoadedHomeWidget: " true|false        (literal 0xc50982)
7a7962  cmpb $0x0, 0x229(%rbx)
7a7969  je   0x7a79a0                     ; only if NOT yet loaded
7a796b  … return                          ; idempotent early-out
7a79a0  movl $0x20,%edi ; operator new
7a79a5  movb $0x1, 0x229(%rbx)            ; set m_isLoadedHomeWidget = true
7a79ba  QTimer::QTimer(this)
7a79bf  movl $0x36b0,%esi ; QTimer::setInterval(14000)
7a79e3  r8 = 0xc50999 "1slotBindingPlugin()"   (SLOT)
7a79ea  rdx = 0xc50636 "2timeout()"           (SIGNAL)
7a79f5  QObject::connect(timer, SIGNAL, this, SLOT)
7a7a09  QTimer::start()
7a7a0e  movq 0xe0(%rbx),%rdi              ; the QQuickView
7a7a15  callq QWindow::show()             ; ← site #1
7a7a1a  platformNativeInterface() + set "displayPlane"="1" (same pattern as the helper)
```
So: **`this+0x229` (`m_isLoadedHomeWidget`) is a once-only latch, not the gate you are looking
for** — the function shows the window the first time it is called at all. The gate is *whether the
function is ever called*. **[A]**

### 3.2 Who calls it, and what emits the trigger

`AppHomeModel::reqLoadWidget()` (`0x707930`, literal `"void AppHomeModel::reqLoadWidget()"` at
`0xc4c4e0`) is the emitter; it is called from exactly one place: `AppHomeModel`'s generated
`qt_static_metacall` at `0xb381f0` (jump table at `0xc9e8c0`, `cmpl $0x101,%edx` → 258 entries), i.e.
it is invoked **dynamically through the meta-object**, not by a C++ `emit`. **[A]**

`AppHomeEngine::applicationStart()` (`0x7fb1c0`) wires it up at `0x7fc177`:

```
7fc169  AppHomeModel::instance()
7fc174  r8 = 0xc528bd "1slotReqLoadWidget()"   (SLOT)
7fc181  rdx = 0xc528d2 "2requestLoadWidget()"  (SIGNAL)
7fc188  QObject::connect(model, SIGNAL, engine, SLOT)
```
**[A]** — literals `"2requestLoadWidget()"` @ `0xc528d2` and `"1slotReqLoadWidget()"` @ `0xc528bd`,
sitting next to `"STR_EV_ELECTRIC_VEHICLE"` and the `"AppHome Init Done"` string (`0xc52927`).

There is **no** `"1reqLoadWidget()"` string anywhere in the binary, i.e. no string-based `connect()`
and no `QMetaObject::invokeMethod(…,"reqLoadWidget")` call. The only remaining caller is QML. **[A]**

### 3.3 The QML that emits it

`AppHomeModel` is exposed to QML: in `AppHomeEngine::initEngine()` (`0x786230`) there is
`setContextProperty(QString("AppHomeModel" /*0xc46260*/), AppHomeModel::instance())` at `0x786324`,
then `QQuickView::setSource(QUrl("/app/share/AppHomeScreen/qml_<variant>/HomeScreen/main.qml"))`
(`"HomeScreen/main.qml"` @ `0xc4facc`; variants `…qml_new2.0/` @ `0xc54dd0`, `…qml_genesis/` @
`0xc54df8`, `…qml_eco3.0/` @ `0xc54e20`). **[A]**

The call is in the QML (this is why no string exists in the ELF):

```
app/share/AppHomeScreen/qml_new2.0/HomeScreen/QHMI_HomeScreenMain_Advanced.qml:534
app/share/AppHomeScreen/qml_new2.0/HomeScreen/QHMI_HomeScreenMain_Wide.qml:271        (…and the
app/share/AppHomeScreen/qml_genesis/…, …/qml_eco3.0/… copies)
    Component.onCompleted: {
        AppHomeModel.screenNotSupportSS = true
        AppHomeModel.reqLoadWidget()        ← window is shown here and nowhere else
```
**[A]** (`grep -rn reqLoadWidget app/share/AppHomeScreen` → 6 hits, all `Component.onCompleted`).

`main.qml` itself does **not** instantiate those components: it has
`Loader { id: loader_1 }`/`loader_2` and a JS function `screen_Transition()` that assigns
`current_loader.sourceComponent = screenNext`. `screenNext` is a *context property*, and
`screen_Transition()` is invoked from C++ by `QMLController::showScreen(QString)` (`0x820900`,
literal `"bool QMLController::showScreen(QString)"` @ `0xc5eb00`):

```
820b23  QString::fromAscii("screenNext" /*0xc5eab4*/)
820b49  QQmlContext::setContextProperty("screenNext", …)
820d8e  QMetaObject::invokeMethod(rootObject, "screen_Transition", Qt::AutoConnection)
```
**[A]** Callers of `QMLController::showScreen` include `AppManager::recieveMsgData(uint,QVariant)`
(`0x81d920`), i.e. the app only pushes a home screen when it processes an application-manager
message. **[A]**

### 3.4 Therefore the boot gate

```
AppManager message  →  AppManager::recieveMsgData  →  QMLController::showScreen("<main>")
   →  main.qml::screen_Transition()  →  QHMI_HomeScreenMain_*  Component.onCompleted
   →  AppHomeModel::reqLoadWidget()  →  signal requestLoadWidget()
   →  AppHomeEngine::slotReqLoadWidget()  →  QWindow::show()
```
Every arrow is verified except the first, which is verified only up to
`AppManager::recieveMsgData` **[B]**. If the app is started by hand instead of by the application
manager that feeds it, the chain stops at the first arrow — nothing else can show the window.

Corroboration from `main.qml` that the app is *waiting* rather than broken: `main.qml` shows
`loader_3.sourceComponent = AWComponent` asynchronously and displays
`TranslationsModel.STR_HOME_WIDGET_PREPARING` while `loader_3.status != Loader.Ready`, with the
comment `// AW Placeholder for asynchronous booting.` That is a real, intentional "nothing is
visible yet" state.

---

## 4. Path B — the D‑Bus `show_window_fg` path

### 4.1 Call chain

```
D-Bus com.lge.avn.appmanager.appbase.show_window_fg  @  /com/lge/hkmc/avn/appfunc/appInterface
  → AppHomeEngine::qt_static_metacall  (0xb40770; cmpl $0xda,%edx → 219 methods, table 0xca6680)
  → AppHomeEngine::show_window_fg(int,int,int,int)            0x7f7250
       or  show_window_fg(int,int,int,int,int,bool)           0x7f7460
  → AppHomeEngine::inter_show_window_fg(int,int,int,int,int,bool)   0x7ef6e0
  → helper 0x7ef480  (call at 0x7efcf5)  → QWindow::show()   (0x7ef4d8 / 0x7ef668)
```
The exported interface XML is embedded verbatim at `0xd9e84a`:
`<interface name="com.lge.avn.appmanager.appbase">` with
`show_window_fg(reason,plane,avmode,command) -> response_plan`,
`show_window_fg(appid,reason,plane,avmode,command,temporal) -> response_plan`,
`hide_window_bg(reason,plane,avmode,command)`, `notify_event(reason,plane,avmode,command)`,
`swrckey(key,status)`, `faceplatekey(value)`, `faceplatedial`, `ccpdial`. **[A]**

### 4.2 `show_window_fg` wrappers

```
0x7f7250 show_window_fg(a,b,c,d):
  7f726f  cmpb $0x0,0x4e5(this) ; if 0 -> set 1        ; re-entrancy latch, cleared at exit
  7f7297  esi = 0xb                                     ; appid = 11
  7f729c  inter_show_window_fg(this, 0xb, a, b, c, d, temporal=false)
  7f7349  log literal 0xc5ae40 "int AppHomeEngine::show_window_fg(int, int, int, int)" line 0x5cf
```
```
0x7f7460 show_window_fg(appid,reason,plane,avmode,command,temporal):
  7f749d  cmpb $0x0,0x4e5(this) ; if 0 -> set 1
  7f74ad  rsi = *(this+0xb0) ; if (rsi && this->0x4c8) goto 0x7f76b0   ; extra branch
  7f74ef  inter_show_window_fg(this, appid, reason, plane, avmode, command, temporal)
  7f7505  if (*(this+0xb0) && result == 1) goto 0x7f7660              ; special-case on plane==1
```
### 4.3 `inter_show_window_fg` — the prologue and the actual guards

```
log:  appid = <esi> · reason = <edx> · plane = <ecx> · avmode = <r8d> · command = <r9d> ·
      temporal = <[rsp+8]>                           (literals 0xc47157/0xc47161/0xc4716c/0xc513ce/
                                                      0xc47176/0xc522ad)
7ef8e4  if (appid != this->0xf0) this->0xf0 = appid           ; the "current app id"
7ef8f2  ── together with 0x7ef93f/0x7ef963/0x7ef978/0x7efc50/0x7efcae/0x7efcd6/0x7efcf2 these are
        the *only* blocks every path to show() must traverse (computed by CFG reachability over the
        851 basic blocks of the function; removal of any of them disconnects show()):
7ef8f2  if (!temporal && appid==this->0x1e4) -> neither;  0x168/0xb/0x14/0x15 app-id transitions
7ef93f  this->0x2e3 = 0 ; AppHomeModel::setCurrentAppID(appid) ; if (this->0x1c4) PHEV variant
7ef963  AppHomeModel::0x706430() must be ...           (bool)
7ef978  AppHomeModel::0x6e9670() (bool) with local = (appid == 0xd)
7efc50  QJSValue::property("length").toInt()           (literal "length" @ 0xc4643f)
7efcae  AppHomeModel::setIsAtMediaGate(false) ; requires this->0x2e3 != 0
        else -> 0x7f03b0: checkScrShowingCondition(appid, true)
7efcca  AppHomeEngine::checkScrShowingCondition(appid, false)   (0x7ab810)
7efcd6  QWindow::isVisible()
7efce4  if (isVisible && appid == this->0x1e4)  -> 0x7efe98   ← the ONLY skip of show()
7efcf2  helper 0x7ef480 -> QWindow::show()
```
**[A]** for the structure and the addresses; **[C]** for the semantic names of `this+0x1e4`
(previous app id / previous top screen) and `this+0x2e3`.

Strings referenced from inside `inter_show_window_fg` (all @ `.rodata`, all quoted verbatim) name
the decision inputs it consults: `"HOME_MODEL->getIGNStatus() = "` (`0xc52419`),
`"same screen status. do not reload."` (`0xc55bc8`), `"other app"`-state via `"atOtherApp: "`
(`0xc52353`), `"_currentTopScr: "` (`0xc522ba`), `"previousAppID: "` (`0xc52409`),
`"Other plane"` (`0xc523e4`), `"Keep the previous state"` (`0xc523c1`), `"(nahoon) Back to Setup page
condition!!! : 4 (POWER ON)"` (`0xc55b90`), `"/tmp/GUI_THEME_DAY"` / `"/tmp/GUI_THEME_NIGHT"`
(`0xc522fa`/`0xc5230d`). The presence of `getIGNStatus()` confirms an ignition-state factor in the
reason dispatch. **[B]**

### 4.4 **The D‑Bus return value is not a success flag**

`inter_show_window_fg` has exactly **one** epilogue (`0x7efba6`–`0x7efbd2`) and it ends with

```
7efba6  movl 0x4(%rsp),%eax     ; == the 3rd argument, i.e. `plane`
```
**[A]** Therefore `int32 1` from `show_window_fg(...)` only means **"you passed plane = 1"**; it is
the echo of the `response_plan` out-argument. It carries **no** information about whether the window
was shown. Any reasoning of the form "D‑Bus returned success so the app thinks it showed" is
unsupported by the code.

Two plausible reasons the call still produced no surface, both consistent with the code:
(a) `isVisible()==true && appid == this->0x1e4` at `0x7efce2` → show skipped **[B]**; or
(b) an early exit through `0x7efb78`/`0x7efbaa` **[B]** — note `0x7efb78` is reached by fall-through
for every `appid` that is not `0x1b/0x1f4/0x168/0x170/0x17` *after* the reason dispatch at
`0x7efb3c`–`0x7efb6c`. So the `appid`/`reason`/`plane` triple of your test call determines whether
show is even attempted; `appid` is the interesting knob, not the plane.

---

## 5. `onViewerVisibleChanged` is *not* the show gate

```
0x7a2840  void AppHomeEngine::onViewerVisibleChanged(bool)      (literal 0xc583c0)
  7a292b  log line literal 0x30d6 == 12502                       ← matches your log line
  7a2963  prints "value: " true|false  (0xc79672 / 0xc46690 / 0xc798cb)
  7a2997  if (value && this->0xf8 != nullptr) { build QString() + QByteArray() and call 0x777a00 }
```
It contains **no** call into Qt visibility code (it is not one of the three call sites and does not
call `QWindow::show`). It is merely a reactor, connected in `AppHomeEngine::applicationStart()` at
`0x7fb587`:

```
7fb580  AppHomeEngine::applicationStart()
7fb580  rsi = *(this+0xe0)                        ; sender = the QQuickView
7fb587  r8  = 0xc52626 "1onViewerVisibleChanged(bool)"   (SLOT)
7fb58e  rdx = 0xc52644 "2visibleChanged(bool)"           (SIGNAL)
```
**[A]**

Consequences worth using as diagnostics:

* `value: true` can only be produced by `QWindow::show()` succeeding its `setVisible(true)` — so the
  app **did** reach a `show()` at least once. **[B]**
* `value: false` can only be produced by `QWindow::hide()`, whose **only** call site is
  `hideFrontView()`, reached only from `AppHomeEngine::hide_window_bg(int,int,int,int)`
  (`0x7ef130`). So a `value: false` in your log means the D‑Bus method **`hide_window_bg` was
  executed** on that app instance (the app manager, or your own test, called it). **[A]**
* Since `QWindow::setVisible` is not even imported, there is no third way for the flag to move. **[A]**

`onViewerVisibleChanged` therefore tells you what the window *state machine* did, not what gates it.
Reporting "visible true then false" together with "no wl_surface" is internally consistent only if
`show()` and `hide()` both ran; that is the shape of a window that was shown and then dismissed,
not of a window that was never shown.

---

## 6. Second, independent gate *below* `show()` — the IVI surface id (high value)

Everything after `show()` in the app is decoration; the surface is created by QtWayland. The vendor
`.../usr/lib/libivi-platform-interface.so.1.0.0` patches the IVI shell integration and inserts a
blocking step. Verified in that library:

```
IviShellIntegration::createShellSurface(QWaylandWindow*, const QString&)   0x133a0
  133ea  IviShellPrivate::isNeedToGetSurfaceIdFromEnvValue(unsigned&)
  133ef  je 0x13538                     ; env var not set
  1353c  hmiRequester = this+0x18       ; the ivi_hmi_requester to the HMI service
  1354e  QString::fromAscii(0x1b082,5) == "QTAPP"
  1356a  HmiRequesterPrivate::requestId(window, "QTAPP")
  13593  IviShellIntegration::waitForGetSurfaceId(receiver)                0x13340
IviShellIntegration::waitForGetSurfaceId(HmiReceiver *r)                   0x13340
  13360  display->flushRequests()
  13379  while (r->id_at_0x20 == 0)
  13370      display->blockingReadEvents()      ← busy loop, still inside show()
IviShellPrivate::getSurfaceIdFromEnvValue(bool &forced)                    0x13a50
  env names (verified as literals): QT_WAYLAND_SET_SURFACE_ID_FORCED  (0x1b0d8)
                                  QT_WAYLAND_USE_PID_FOR_SURFACE_ID (0x1b100)
                                  QT_WAYLAND_SET_SURFACE_ID         (0x1b122)
  also present in this library:   LGE_QT_WAYLAND_VISIBILITY_CALLBACK_FILTER
```
**[A]** for the code, **[C]** for "this is what is happening in your VM".

Semantics: if none of those environment variables is set, `QWaylandWindow` shows → asks the HMI
service (`ivi_hmi_requester`, app-id `"QTAPP"`) for a surface id → and **blocks the main thread**
until the id arrives. If the app is not being managed by an HMI/IVI service that answers
`request_id`, `show()` never returns; nothing after it (attaching/committing buffers, the
`"displayPlane"` tag, and the app's own post-show log line) ever runs. With one of the variables set,
it calls `HmiRequesterPrivate::reserveId(window, 1, id)` instead and never blocks. Also note the
null‑client path (`0x135c8`/`0x135ca`, id = 0) which does *not* block — so this only bites when a
HMI client is present but unresponsive.

---

## 7. Experiments, cheapest first

**E1 (free) — decide whether `show()` was ever *entered*, from the logs you already have.**
`inter_show_window_fg` logs a line after the `show()` call, at `0x7efdf7`, whose payload begins with
the literal `"----->>>>>"` (`0xc523d9`) plus an int; `slotReqLoadWidget` has no post-show log, but
`onViewerVisibleChanged` (line 12502) fires *inside* `show()`. Cheapest decisive test: re-run and
grep for `----->>>>>` and for `show_window_fg`.
* `----->>>>>` present → `show()` returned normally, the app is not blocked in Qt → the gate is
  upstream (Path A, QML never instantiated).
* absent, but `show_window_fg` entry log present → the call reached the show block and got stuck
  downstream → E4 is your fix.
Cost: one run, no state change.

**E2 (cheapest real change) — satisfy Path A by making the app load the main home screen.**
The D‑Bus method designed for that is **`notify_event(reason, plane, avmode, command)`** on
`com.lge.avn.appmanager.appbase` @ `/com/lge/hkmc/avn/appfunc/appInterface`
(`AppHomeEngine::notify_event` `0x7bf5f0` → `AppManager::recieveMsgData` `0x81d920` →
`QMLController::showScreen` `0x820900`). The reason enum contains `EVT_GOTO_MAIN_HOME_SCREEN`
(name literal `0xcb0460`; the numeric value is generated by the `HMIEVENTS` enum and is *not*
recoverable from the name blob, so sweep a small set of reasons rather than trusting one value) **[C]**.
Sibling methods that reach the same path and are worth the same sweep: `swrckey(key,status)` and
`faceplatekey(value)` (hardware/faceplate key injection — `AppHomeEngine::swrckey(int,int)`
`0x795f20` exists for exactly this).

**E3 — `-gui:` / variant is *not* the show gate, but it is worth knowing which it picked.**
`applicationStart()` selects one of `/app/share/AppHomeScreen/qml_new2.0/` (`0xc54dd0`),
`qml_genesis/` (`0xc54df8`), `qml_eco3.0/` (`0xc54e20`) and `initEngine()` appends
`HomeScreen/main.qml`. All three variants contain `AppHomeModel.reqLoadWidget()` in the same
`Component.onCompleted`, so picking a different `-gui` value cannot by itself make a window appear;
the strings for the `-gui:`/`-sc:`/`-vc:` keys are **not present in this binary at all**, so those
arguments are parsed elsewhere (app manager side) and reach the app only through the chosen QML
directory. Do not spend time sweeping `-gui` hoping for a visible window. **[B]**

**E4 (highest leverage if E1 shows a stall) — remove the IVI surface-id wait.**
Launch `AppHomeScreen` with

```
QT_WAYLAND_SET_SURFACE_ID=<n>        # any small unique int, e.g. 7
# or, if the id must be unique per process:
QT_WAYLAND_USE_PID_FOR_SURFACE_ID=1
```
in its environment (same way the app manager would hand it over). This makes
`isNeedToGetSurfaceIdFromEnvValue()` return true, so `createShellSurface` takes the
`reserveId()` path and `waitForGetSurfaceId()` is never called. If E1 said "stall", this is a
one-line fix; if E1 said "`----->>>>>` present", E4 is unnecessary.

**E5 (only if E2 fails) — check whether the app's own D-Bus queries are answered.**
`applicationStart()` reads a dozen app-manager settings during boot (`"APP_HOME_SCREEN_TYPE"`
`0xc44880`, `"APP_SETTING_VCU_READY"` `0xc44832`, `"APP_PHEV_VCMS_READY"` `0xc44928`,
`"APP_VALET_MODE_ICON_VISIBLE"` `0xc448c3`, `"APP_N_MODE_TEST_ENABLE"` `0xc448df`, …) and registers
`"appInterface"` / `"registerfaceplatekey"` / `"registerswrckey"`. If the service that owns those
settings is missing, the app still reaches `"AppHome Init Done"` (`0xc52927`) but never gets a reason
to push a screen. Verify the *provider* names on the bus, not just that the app itself is reachable.

---

## 8. Address / literal index (for re-checking)

```
AppHomeEngine::slotReqLoadWidget()                0x7a7800   sig 0xc57c20   show @0x7a7a15
AppHomeEngine::slotBindingPlugin()                0x79e130   sig 0xc589e0   (timer target, 14 s)
helper (show + IVI plane tag)                     0x7ef480                  show @0x7ef4d8/0x7ef668
AppHomeEngine::inter_show_window_fg(6 args)       0x7ef6e0   sig 0xc5ad80   calls helper @0x7efcf5
AppHomeEngine::show_window_fg(int,int,int,int)    0x7f7250   sig 0xc5ae40
AppHomeEngine::show_window_fg(…,int,bool)         0x7f7460   sig 0xc5ade0
AppHomeEngine::hide_window_bg(int,int,int,int)    0x7ef130   → hideFrontView 0x7ee800 → hide @0x7eeb43
AppHomeEngine::applicationStart()                 0x7fb1c0   sig 0xc5afc0
AppHomeEngine::initEngine()                       0x786230   sig 0xc5af00
AppHomeEngine::onViewerVisibleChanged(bool)       0x7a2840   sig 0xc583c0  (line 12502)
AppHomeEngine::checkScrShowingCondition(int,bool) 0x7ab810   sig 0xc573a0
AppHomeEngine::showHomeScreenCheckPP(int,b,b)     0x7bcdf0   sig 0xc57780
AppHomeModel::reqLoadWidget()                     0x707930   sig 0xc4c4e0
AppHomeModel::setCurrentAppID(int)                0x708250
AppHomeModel::setIsAtMediaGate(bool)              0x6ee5d0
AppHomeEngine::qt_static_metacall                 0xb40770   (219 methods, 0xca6680)
AppHomeModel::qt_static_metacall                  0xb381f0   (258 methods, 0xc9e8c0)
QMLController::showScreen(QString)                0x820900   sig 0xc5eb00
AppManager::recieveMsgData(uint,QVariant)         0x81d920
main()                                            0x601a0    → ctor 0x7e7080 / applicationStart /
                                                              exec 0x783f80 → QGuiApplication::exec

rodata literals used above
  0xc50982 "m_isLoadedHomeWidget: "      0xc50999 "1slotBindingPlugin()"
  0xc528bd "1slotReqLoadWidget()"        0xc528d2 "2requestLoadWidget()"
  0xc52626 "1onViewerVisibleChanged(bool)"   0xc52644 "2visibleChanged(bool)"
  0xc5b2c0 "1"   0xc5b2e0 "displayPlane"     0xc52927 "AppHome Init Done"
  0xc523d9 "----->>>>>"                  0xc52419 "HOME_MODEL->getIGNStatus() = "
  0xc55bc8 "same screen status. do not reload."    0xc4643f "length"
  0xd9e84a interface XML for com.lge.avn.appmanager.appbase
```

## 9. What is *not* established here

* Which numeric `reason`/`appid` actually drives `inter_show_window_fg` to the show block. The CFG
  proves show() is reachable and lists the blocks every path must cross, but the per-(appid,reason)
  outcome needs either a much larger reading effort or two instrumented runs.
* Whether the `0x7ef480` helper is a vendor `static`/lambda in `AppHomeEngine.cpp` or a copy of
  upstream `QQuickWindow::show()` logic (it has no `__PRETTY_FUNCTION__` literal, unlike every named
  vendor function in this binary, and it is the only such function that calls into Qt windowing).
  **[C]**
* The exact Qt 5.4.1 ordering of `visibleChanged` versus platform-window creation. This matters for
  E1 (`value: true` implies the platform window was fully created, hence no IVI stall); the reading
  above assumes that ordering, so treat the "E1 says stall ⇒ E4" conclusion as conditional. **[C]**
