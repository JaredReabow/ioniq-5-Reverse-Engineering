# The missing client was the HMI controller, and the id was never the variable

Date: 2026-11-06. Boot57 changed one variable (id `1010` -> `2170`) and returned something better than a result: **a closed branch of work.**

## What the run proved

The full weston log (217,977 B) names every surface, and **`AppHomeScreen` appears zero times**, while seven other applications register normally:

```
create_hmi_client 1000 "AppDMClient"        create_hmi_client 1004 "AppStandbyClock"
create_hmi_client 1001 "AppDMClient"        create_hmi_client 1004 "BluetoothHMI"
create_hmi_client 1002 "AppOSDManager"      create_hmi_client 1005 "AppEURadio"
create_hmi_client 1003 "AppOSDManager"      create_hmi_client 1030 "NotificationManager"
                                            create_hmi_client 2080 "AppCamera"
```

**Two conclusions, both final:**

1. **The surface-id patch was never in the creation path.** Changing `2080` -> `1010` -> `2170` altered nothing, because the application does not call `ivi_application.surface_create` at all. Three patch revisions and three boots went into a variable that does not exist.
2. **`2080` belongs to `AppCamera`**, proven by the compositor's own log rather than inferred from the launcher table. **The frame that started the id chase was the camera's**, and `docs/vm/55`'s suspicion is now measured.

## The missing component, found statically

`/usr/libexec/weston-ivi-shell-user-interface` - 215,480 bytes - is the **HMI controller**, and its symbols say what it does:

```
ivi_hmi_controller_home         ivi_hmi_controller_layout_mode
ivi_hmi_controller_UI_ready     ivi_hmi_controller_interface
ivi_hmi_controller_add_listener ivi_hmi_controller_events
```

**It creates the home layout and signals clients that home is ready.** It is absent from every run's client list. And the reason is already recorded in this project: `weston.ini`'s `ivi-shell-user-interface` path names a location where the binary is not.

**That defect was logged earlier as "real but dormant", dormant because the compositor never reached `wl_display_run` with a working backend.** The drm backend now works, and the idle callback that spawns the shell UI should fire. **So the dormant defect is now live, and it is the only named candidate that explains the measurement exactly**: the app waits for a home-ready signal from a controller that never starts, so it never creates a surface - while every other app, which does not need that signal, does.

## The next run, with the consultations' rulings applied

**Opus 4.7: revert the id patch, do not substitute.** The patch was authored before `surface_id_offset` was known, it is a vendor patch made without understanding the vendor mechanism, and doc 36 proves it is not in the path. Restore the vendor bytes at file offset `0x475e8`:

```
patched now:      0b 00 00 00 f2 03 00 00     (11 -> 1010)
vendor original:  71 00 00 00 7a 08 00 00     (113 -> 2170)
```

**Astra: `surface_id_offset` is a stride for the shell UI's own per-screen widgets**, not a universal app-id remapper - so the id hypothesis was misdirected from the start.

**Then make the controller run**, and capture **its** output. In every previous run this project captured the app's log and the launcher's log but not the log of the component whose absence was the fault - the same mistake as the unretained launcher log, one layer up.

## The readings, pre-committed

| result | meaning |
|---|---|
| controller runs, `AppHomeScreen` gains a surface | the fault was the missing controller; the id patch was never needed; move to gate 5 proper (capture by pid) |
| controller runs, still no surface | the app needs a specific event or plane value from it; its own stdout will name it |
| controller does not run | read its stderr - it is a Wayland client and will say why it could not connect |

**And a note on cost:** three boots were spent on an id that was never in the path, while the component that was missing had been identified as broken in an earlier document and marked dormant. **The lesson is not "look harder" - it is that a defect recorded as dormant must be re-examined whenever the condition that made it dormant changes**, and the kernel rebuild changed exactly that condition.
