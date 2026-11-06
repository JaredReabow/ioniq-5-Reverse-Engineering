# The revert restored AppHomeScreen's surface; the config key is dead and the controller still does not run

Date: 2026-11-06. Two changes, frozen otherwise: (1) surface-id patch reverted to vendor bytes
`71 00 00 00 7a 08 00 00` (113→2170); (2) `ivi-shell-user-interface=/usr/libexec/weston-ivi-shell-user-interface`
written into `/etc/xdg/weston/weston.ini` (the file weston actually reads).

## Result 1 — the revert worked: AppHomeScreen now has a surface

```
ivi_hmi_receiver@19.receive_id(1006)
ivi_application@17.surface_create(1006, wl_surface@15, new id ivi_surface@20)
create_hmi_client(1, 1006, "AppHomeScreen")
```

`identity` is satisfied for the first time: the home screen registers its own surface (id 1006) via the
normal `ivi_hmi_requester` flow (`request_id("QTAPP")` → `receive_id(1006)` → `surface_create` →
`create_hmi_client`). Removing `QT_WAYLAND_SET_SURFACE_ID` (the revert) is what allowed this — the patched
id was **suppressing** surface creation, not enabling it. That confirms the revert over the substitution.

## Result 2 — the config key is dead: the controller still does not run

`pgrep -f ivi-shell-user-interface` → empty, no `launching` line in the weston log, no
`ivi_hmi_controller_*` symbol anywhere. Static check of every loaded component:

```
ivi-shell.so, ivi-window-manager.so, ivi-controller.so, weston.real:
  "ivi-module" present, but NO "user-interface"/"ivi-shell-user-interface" string.
```

None of the loaded modules (nor the compositor core) reads the `ivi-shell-user-interface` config key, so
pointing it at the correct path launches nothing. The `ivi_hmi_requester` interface itself lives in
`ivi-window-manager.so` (that is how apps get ids), but the *home-layout controller* that consumes it is a
separate client whose actual launcher is still unknown.

## Result 3 — the frame is unchanged

`CAP bytes=129844` — the same background. `identity` is now true (surface 1006) but `home_tree` is still
absent: without the controller there is no home layout, so `HOME_FRAME` fails on `home_tree`.

## Files

- `work/vm/kbuild/boot58-hmi.log` — the run.
- `work/vm/kbuild/ws/partimg-build/AppLauncher.vendor.bin` — reverted bytes (sha256
  `c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268`).
- `work/vm/kbuild/ws/partimg-build/weston.ini.final` — the config written to `weston.ini`.
- the weston log was exported to the run's `dbg-out.txt`; decoded to
  `work/vm/kbuild/ws/runs/1793931162561454000/exported-weston.bin`.
