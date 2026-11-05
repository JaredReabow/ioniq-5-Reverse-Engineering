# The protocol exchange, from the compositor's own trace

Date: 2026-11-05. Server-side `WAYLAND_DEBUG=1` added to the **projection's own** compositor wrapper
(`/usr/bin/weston`, our file - no vendor binary was modified). One application instance, log 501,987 bytes.

## The exchange

```
1328 [112302.725] wl_registry@2.bind(13, "ivi_window_manager", 1, new id [unknown]@3)
1329 [112302.874] wl_display@1.sync(new id wl_callback@4)
1330 [112302.932]  -> wl_callback@4.done(0)
1331 [112302.966]  -> wl_display@1.delete_id(4)
1332 [114126.508] wl_compositor@4.create_surface(new id wl_surface@17)
1333 [114126.793] ivi_controller@13.surface_create(0, new id ivi_controller_surface@19)
1334 [114127.611] wl_surface@17.set_buffer_transform(0)
1335 [114130.410] wl_surface@17.commit()
1336 [114130.578]  -> wl_display@1.error(wl_display@1, 0, "invalid object 19")
```

## What this says, plainly

1. **The client is the application**, and it binds **`ivi_window_manager`** - not `ivi_application`. In this
   product the *application* is also the window manager for its own surface, which is consistent with the vendor
   architecture this project reconstructed (`ivi_wm` / `ivi_place` clients, V-046).
2. It asks **`ivi_controller`** (bound as id 13) to create a surface, and **allocates the new object id itself:
   `ivi_controller_surface@19`**.
3. **The compositor then errors**: `invalid object 19`. It does not know object 19 - so whatever
   `surface_create` created (or failed to create) on the server side did not correspond to id 19 in the
   server's object space.
4. **The failure is not timing, not permission, and not our placement tool.** It is the **third message in the
   surface-creation sequence**, and it happens with a single instance, no preload, and no `ivi-wm` call.

## The hypothesis this creates, and it is checkable

`invalid object 19` on a client-allocated id for a **server-created** object is the signature of a
**client/compositor protocol or library mismatch**: the client library is allocating an id the compositor's
protocol implementation does not accept as a server object.

This project has **injected libraries into this image** (the Debian software renderer, the software-GL stack under
`/opt/software-egl18`, the pixman shim), and the vendor's compositor itself differs from upstream by `0x18` bytes
(`vendor-abi.patch`, recorded earlier). So the thing to check is concrete:

**Which `libwayland-client` does the application load, and is it the vendor's own or one of ours?**

If the app is resolving `libwayland-client.so.0` to a library we injected rather than the vendor's, the id and
interface handling can differ exactly this way - and the fix would be to make the vendor's library win the
resolution, which is a one-line change to a path we control.

## Next, in order, cheapest first

1. **Static:** list every `libwayland-client*` / `libwayland-server*` in the image and in `/opt/software-egl18`,
   compare the vendor's shipped one against anything injected, and check the application's `DT_NEEDED` and
   RPATH for which it will actually resolve.
2. **Runtime:** `LDD`-equivalent inside the guest for the running process (`/proc/<pid>/maps`), which settles it
   with one read and no new instrument.

**Not established:** which library is loaded. **Established:** the failure is the surface-creation call returning
an object the compositor rejects, with no instrument of ours involved.

---

## 3. The library-mismatch idea weakens, and what replaces it

The cheap static check first, before any more boots:

```
/usr/lib/libwayland-client.so.0.3.0        the vendor's, the only one in the image
/opt/software-egl18/lib/                   no wayland libraries at all
AppHomeScreen DT_NEEDED                    libQt5Quick.so.5, libQt5Qml.so.5  (no direct libwayland)
/usr/lib/qt5/plugins/platforms/            libqwayland-egl.so, libqwayland-generic.so
```

**So there is exactly one `libwayland-client` and we did not inject it.** The application does not link Wayland
directly either - it goes through **Qt's Wayland platform plugin**, which is what actually speaks the protocol.

`ivi-controller.xml` is **not shipped** in the image, so the protocol definition cannot be read from the vendor's
own files; the interface exists only as compiled code in the compositor module and in whatever client library the
plugin carries.

## 4. What that leaves, stated without guessing

The traced client binds `ivi_window_manager` and calls `ivi_controller.surface_create`, then the compositor
reports an object it does not know. Two readings remain:

1. **The Qt Wayland plugin in this image is vendor-patched** to act as an IVI controller (which would explain the
   `ivi_window_manager` binding from an *application*), and the compositor's `ivi-controller` module rejects the
   surface it creates.
2. **The plugin's protocol version differs from the compositor module's** - the vendor's compositor already
   differs from upstream by `0x18` bytes (`vendor-abi.patch`), and a mismatched version is exactly how a
   client-allocated id ends up unknown to the server.

**The single measurement that distinguishes them, and it needs no new instrument:** read
`/proc/<pid>/maps` of the running application and see which Wayland plugin and which `libwayland-client` it has
mapped, and from which path. If it maps something other than the vendor's `/usr/lib/libwayland-client.so.0.3.0`,
reading #2 is live; if it maps the vendor's, the plugin's use of `ivi_controller` is the thing to examine next.

**Not established:** which of the two. **Established:** the failure is the third message of surface creation, with
one application instance, no preload, no placement tool, and only vendor libraries in the image.

---

## 5. Correction: the traced client is probably **not** the application

`/proc/<pid>/maps` of the running application came back **empty of any wayland entry** (`R1_MAPS_N=0`), which is
more likely a **SMACK restriction on reading another domain's maps** than a real absence. So the runtime check
failed, and the static check was run instead - with a result that contradicts my own attribution.

```
libqwayland-generic.so   10,200 bytes    zero occurrences of ivi_controller / ivi_window_manager / ivi_application
libqwayland-egl.so       63,480 bytes    zero occurrences of the same
```

**Neither Qt Wayland plugin contains a single `ivi_` protocol string.** They cannot bind `ivi_window_manager` or
call `ivi_controller.surface_create`, because those interfaces are not in them at all.

**Therefore the client in the compositor trace is not the application.** Something else in the projection binds
`ivi_window_manager` and creates surfaces through `ivi_controller`, and it produced the `invalid object 19` I have
been attributing to `AppHomeScreen` for the last three entries.

The candidates are the vendor's own shell-side clients - `/usr/libexec/weston-ivi-shell-user-interface`
(present in the image but named at a different path by the ini), `weston-desktop-shell`, or the vendor's
`ivi-window-manager` interaction - and the trace alone cannot say which, because weston 1.10's protocol trace
does not name clients.

## 6. What is still true, and what has changed

**Still true and valuable:** there is a real, reproducible protocol failure - a surface created through
`ivi_controller` whose object id the compositor then does not know - and it is visible in the compositor's own
trace, with no instrument of ours in the path. **Wayland protocol debug on the compositor works** and produced a
four-line diagnosis of *a* client, which is a capability this project did not have before tonight.

**Changed:** it is **not established** that this failure belongs to the application, and the entries above that
attributed it to `AppHomeScreen` are wrong on that point. The application's own death - `wl_display@1: error 0:
invalid object 19` in *its* log - may be the same server error delivered to it, or a different one; the log line
is identical, which is exactly why I assumed it was the sender.

**The next measurement must identify the client:** start the compositor trace and record **when** the
`ivi_window_manager` bind appears relative to the application's first log line. Before the app starts, it is a
shell-side client and the application is a victim; after, it is the application and my earlier reading stands.

---

## 7. The ordering test: the surface creator is a startup client, not the application

One run, comparing **line numbers** in the compositor log - which is append-only, so line order *is* time order -
against a marker taken the instant the application first appeared:

```
O1_FIRSTAPP_PID=2536   MARKERLINE=1430        <- the app exists from this line onward
O1_BIND_LINES=[60 85 145]                     <- ivi_window_manager binds
O1_SURF_LINES=[1108 1128 1358]                <- ivi_controller surface_create calls
O1_INVALID_LINES=[1629]                       <- the invalid-object error
O1_TOTAL=1670
```

**The `ivi_window_manager` binds are at lines 60, 85 and 145 - the application does not exist until line 1430.**
So the client that binds the window-manager interface at start-up is **not the application**, and my previous
correction stands on measurement rather than on the absence of a string.

The surface creations at 1108-1358 are also **before** the application appears. The `invalid object` error at
1629 is **after** it, so that one could belong to the application - **the error the application logs may be one
it received, sent to whoever was still holding a surface id from the earlier activity.**

## 8. What this means, and what to do next

- **A start-up client binds `ivi_window_manager` within the first ~150 lines of the compositor log**, i.e. in the
  first seconds of compositor life, long before any application. That is the component to identify.
- The candidates are the shell-side clients in the image: `/usr/libexec/weston-ivi-shell-user-interface`
  (present, but named at a path the ini gets wrong), `/usr/libexec/weston-desktop-shell`, and the vendor's
  `ivi-window-manager.so` interaction.
- **The next read is four lines of context**, not another theory: dump **lines 40-80** of `/tmp/weston-real.log`,
  where a `launching ...` line should sit immediately before the first bind at line 60. That names the client
  from the compositor's own words.

**Established by measurement:** the start-up client is not the application; the application's error is at minimum
partly a consequence of earlier surface activity by something else.
