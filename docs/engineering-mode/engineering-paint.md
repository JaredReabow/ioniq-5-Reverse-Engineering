# Engineering-mode paint: the app never attaches a buffer

## One-line answer

AppEngineerMode creates an IVI surface (the compositor records `Surface id(1004)` and
sometimes `1006`), but its Wayland client **never attaches a buffer and never commits
anything** to that surface. Its entire protocol trace over 70+ seconds is four
`wl_display.delete_id` calls. The surface stays transparent, so the home screen shows
through it and an injected click finds `NO_CLIENT`. The reason is that the window is
**shown by the application manager, not by the app itself** — the app waits for
`com.lge.avn.appmanager.appbase.show_window_fg`, which this projection never delivers —
so its `QWindow` is never shown and it never presents a frame.

## What the app does with its buffer: nothing

The launcher discards each child's stderr, so the app's own `WAYLAND_DEBUG=1` output is
written to `/dev/null` before it can be read. It still passes through `write(2)`, so I
attached `strace -f -e trace=write -s 400` to the AppEngineerMode PID as soon as
`pidof` returned it. The complete fd-2 traffic of the app over the 70 s settle window
is 624 bytes, 12 writes, and all of it is object-id teardown:

```
1002  write(2, "[134192.324] wl_display@1.delete_id(", 36 <unfinished ...>
1002  write(2, "31", 2 <unfinished ...>
1002  write(2, ")\n", 2 <unfinished ...>
1002  write(2, "[134193.200] wl_display@1.delete_id(", 36 <unfinished ...>
1002  write(2, "32", 2 <unfinished ...>
1002  write(2, ")\n", 2 <unfinished ...>
1002  write(2, "[134194.359] wl_display@1.delete_id(", 36 <unfinished ...>
1002  write(2, "30", 2 <unfinished ...>
1002  write(2, ")\n", 2 <unfinished ...>
1002  write(2, "[134195.879] wl_display@1.delete_id(", 36 <unfinished ...>
1002  write(2, "33", 2 <unfinished ...>
1002  write(2, ")\n", 2 <unfinished ...>
```

(`STRACE_RAW_SIZE` was 4 322 801 bytes for the same window; essentially all of that is
the app's DLT logging going to its DLT FIFO fd, not fd 2. `WL_RAW_SIZE` = 624, 12 lines.)

There is **no** `wl_compositor.create_surface`, no `wl_surface.attach`, no
`wl_surface.commit`, no `wl_shm.create_pool`/`create_buffer`, and no
`ivi_share_surface.share_surface_state` in the app's protocol trace. For contrast, the
home screen (which does paint, 17 870-byte frame) carries
`ivi_share_surface@59.share_surface_state(1)` traffic in the same projection
(recorded in the changelog §2.35.0). So this is not a renderer artefact: the engineering
app performs none of the buffer-sharing traffic the painting app performs.

## Which surface is the real one

The app's IVI surfaces appear after the launch as the newest `Surface id(N)` lines in
`/tmp/launcher-chain/weston.log`. The set varies run to run (the launch is flaky):

- run A: `1004`, `1005`, `1006`
- run B: `1004`, `1006`
- run C: `1004` only

All are `Weston surface W(1926), H(753)`. Placing each with `ivi-wm` and capturing:

| surface placed | captured frame | bytes |
| --- | --- | --- |
| `2080` (home, control) | home screen (blue title band) | 17 869–17 876 |
| `1004` | home screen showing through | 14 895–17 875 |
| `1006` | home EV page showing through | 14 896–14 908 |

The engineering surfaces capture **the home screen behind them**, i.e. they are
transparent. The newest post-launch surface (`1006` when present, otherwise `1004`) is
the app's content surface, but the answer to "which is the real one" is moot: **none of
them ever carries a buffer.** The "4 117-byte black frame" in the earlier notes is this
same empty surface captured while the home screen was not the thing showing through; the
black is the workspace background colour (`0xff000000`), not app pixels. (The captured
frames decode to 1920x720 all-black; the "Engineering Mode title bar" description is not
present in the current captures — the title bar belongs to the app's QML and is simply
never painted here.)

## Why it cannot paint in this projection

The app loads and lays out fine — its DLT `qmlLog` shows
`"[main.qml]:  main.qml : Component.onCompleted"`,
`"screen_Transition() : screenNext = QQmlComponent(...)"`,
`"idAppRoot.onWidthChanged : idAppRoot.width 1920"` / `height 720`,
`"AppMain.qml : Component.onCompleted"`, and `"[main.qml]: loader_1.onLoaded"`. So QML is
not the fault and neither are the six data services (those are answered, `Pending Err`
count 0).

The fault is the window-lifecycle handshake. The binary exports a Qt D-Bus
`AppbaseAdaptor`:

```
<interface name="com.lge.avn.appmanager.appbase">
  <method name="show_window_fg">
    <arg direction="in" type="i" name="reason"/>
    <arg direction="in" type="i" name="plane"/>
    <arg direction="in" type="i" name="avmode"/>
    <arg direction="in" type="i" name="command"/>
    <arg direction="out" type="i" name="response_plan"/>
  </method>
  <method name="hide_window_bg"> ... </method>
</interface>
```

and registers itself with the manager via
`com.lge.avn.appmanager.registration.registration(appid, appname, servicename, objectpath, plane)`.
The real ApplicationManager is what calls `show_window_fg` on a launched app; the app
does not show its own window. In this projection the chain runs only `/app/bin/AppLauncher`,
not the full ApplicationManager, and **nobody ever calls `show_window_fg`** on
AppEngineerMode. The app therefore never calls `QWindow::show()`, never enters its scene
graph render loop, and never attaches or shares a frame — matching exactly what the
strace shows (no attach/commit/share, only four object-id teardowns).

Two supporting observations from the same runs:

- The app never takes its well-known bus name. `ListNames` on the session bus shows
  `com.lge.hkmc.avn.appfunc.AppHomeScreen`, `...AppCamera`, `...AppOSDManager`, etc.,
  but **no** `com.lge.hkmc.avn.appfunc.AppEngineerMode`; the app holds only a unique
  `:1.x` name. Delivering the show call to the expected well-known name fails:

  ```
  dbus-send --session --dest=com.lge.hkmc.avn.appfunc.AppEngineerMode \
      /com/lge/hkmc/avn/appfunc/AppEngineerMode \
      com.lge.avn.appmanager.appbase.show_window_fg int32:0 int32:0 int32:0 int32:0
  Error org.freedesktop.DBus.Error.ServiceUnknown:
      The name com.lge.hkmc.avn.appfunc.AppEngineerMode was not provided by any .service files
  ```

  (so the show call must go to the app's unique `:1.x` name, which the real manager
  learns from the `registration` call).

- Forcing the Qt Quick software renderer does **not** help. `QT_QUICK_BACKEND=software`
  was confirmed present in the app's `/proc/<pid>/environ`, and the surfaces still
  captured transparent (1004 -> 14 907 bytes, i.e. the home EV page). The software
  renderer only changes *how* a shown window presents; it does not cause an unshown
  window to present.

## The single change

Deliver the missing show handshake to the app — call
`com.lge.avn.appmanager.appbase.show_window_fg` on AppEngineerMode's **unique** bus name
(`:1.x`, taken from the `sender=` of its `registration` call in
`/tmp/launcher-chain/session-bus.log`), at path `/com/lge/hkmc/avn/appfunc/AppEngineerMode`
or `/com/lge/hkmc/avn/appfunc/engineermode` — after it has registered. Equivalently, run
the real ApplicationManager instead of bare AppLauncher so it performs the handshake. That
is the one missing step between "QML loaded and laid out" and "a buffer attached and
committed"; every other layer (compositor, renderer, placement, capture, touch) is proven
working by the home screen in the same run.

Not yet demonstrated: that this single call is sufficient on its own. The manager's real
show sequence may be `show_window_fg` plus a preceding placement/visibility step. The
negative results are recorded plainly: `QT_QUICK_BACKEND=software` did not paint, and
`show_window_fg` delivered to the well-known name returned `ServiceUnknown` because the
app never owns that name.

## Method notes (so the next run is cheaper)

- The launcher discards child stderr; `LD_PRELOAD` set in the chain's environment did
  not reach the launched app in these runs, but `strace -e trace=write` on the PID did
  and is the reliable way to read `WAYLAND_DEBUG`. The Wayland debug text is written in
  small fragments, so grep the strace output for `write(2,` and reassemble before
  counting.
- `weston-screenshooter` writes `wayland-screenshot.png` to the **current directory**;
  `cd /tmp` first or the file lands at `/wayland-screenshot.png`.
- Surface counts differ between runs (1004 only, 1004+1006, 1004+1005+1006); always
  capture the newest post-launch surface and the home control surface in the same run.

## Attempted fix: deliver `show_window_fg` ourselves — blocked, and it corroborates V-045

The obvious cheap fix is to send the handshake directly. What the app registers, captured verbatim from the session bus:

```
sender=:1.47 -> dest=com.lge.hyundai.avn.appmanager path=/registration
   int32 301                                            appid
   string "AppEngineerMode"                             appname
   string "com.lge.hkmc.avn.appfunc.AppEngineerMode"    servicename
   string "/com/lge/hkmc/avn/appfunc/engineermode"      objectpath
   int32 1                                              plane
```

The live connection was then resolved to the running process - not guessed from the log order, which had already produced one wrong target - by walking every
unique name on the bus and asking `GetConnectionUnixProcessID` until it matched `pidof AppEngineerMode`. That worked: `TARGET=:1.47` for `ENG=1037`.

Delivering the call to that exact connection gave:

| destination | result |
| --- | --- |
| `/com/lge/hkmc/avn/appfunc/engineermode` (what it registered) | `NoReply` |
| `/com/lge/hkmc/avn/appfunc/appInterface` | **object exists, then `NoReply` - and the app's connection disappears** |
| `/com/lge/hkmc/avn/appfunc/AppEngineerMode`, `/` | `ServiceUnknown` |

Read that last column carefully: after the call to `appInterface`, every subsequent path reports **`ServiceUnknown`**, i.e. the process that owned `:1.44` was
gone. Sending `show_window_fg` to `appInterface` **kills the app**, which is exactly the behaviour recorded in **V-045** ("third reproducing call → NoReply,
process gone") and now reproduced with the four-integer signature as well.

**So the cheap route is closed, and it closes it for a good reason:** the app does not serve the handshake at the path it registers, and the interface at
`appInterface` is a call that destroys the caller's peer. The real `ApplicationManager` must be doing something else - most plausibly it is the component
that receives `registration`, remembers `servicename`/`objectpath`, and speaks to the app on the object it *does* export. Running the real manager is
therefore not a nicety; it is the only route to a painted engineering window that does not involve killing the app.

This is also the third independent observation of the V-045 behaviour, which strengthens that entry: the crash is not a fluke of one call signature.

## Attempted fix 2: run the real `ApplicationManager` — it runs, and it says why the window still does not appear

`/app/bin/ApplicationManager` ships (3.9 MB) and the research chain never started it. Started alongside `AppLauncher`, it comes up and does real work — its
log shows the registration events and its own MICOM conversation:

```
APPM_LWP[958]: ApplicationManager::systemUnregistered() service[:1.36]
APPM_LWP[958]: MicomInterfaceM::ADMOffSettingSlot reply is not VALID
APPM_LWP[958]: MicomInterfaceM::AskDebugCntSlot reply is not VALID
```

The engineering application still does not paint: capture is 15,963 bytes, which is the **title bar only** — larger than the 4,117-byte black frame because
the decoration renders, but the body is still empty.

So running the manager is **necessary but not sufficient**, and its log says what is missing: its state machine is driven by MICOM replies, and every one in
this projection comes back `reply is not VALID`. The manager therefore never reaches the point of calling `show_window_fg` on the app — which is consistent
with everything else measured here, and turns the next step from a guess into a specific one:

> **give `ApplicationManager` valid MICOM replies.** The project already has a D-Bus MICOM stand-in (`/eng-data-sim`, built for the engineering app's own
> queries); the manager asks different methods on the same services (`ADMOffSettingSlot`, `AskDebugCntSlot`, and others visible in its log), so the
> admission work is to answer those too and then observe whether the show handshake is finally delivered.

This is the third distinct attempt at the same goal and the first that fails with a **named, actionable reason** rather than "still black".
