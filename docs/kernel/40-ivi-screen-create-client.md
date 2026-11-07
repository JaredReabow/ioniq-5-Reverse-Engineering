# Static attribution: no named client creates the ivi screen, and no launcher starts the shell UI

Date: 2026-11-06. Static-only follow-up to boot65 (doc 39). No QEMU. Four tasks, four answers.

## Task 1 — no client `screen_create`; compositor-side initialization identified

Searched the extracted rootfs (`p5.img`) for the client-side ivi-controller protocol and for launchers of
`/usr/libexec/weston-ivi-shell-user-interface`. Byte offsets → block → `debugfs icheck/ncheck`:

| reference to `weston-ivi-shell-user-interface` | file |
|---|---|
| inode 56884 | `/etc/xdg/weston/weston_1920.ini` (config) |
| inode 56882 | `/etc/xdg/weston/weston.ini` (config) |
| inode 56883 | `/etc/xdg/weston/weston_1280.ini` (config) |
| inode 57903/57908/57916 | `/rw_data/var/lib/rpm/{Basenames,Filepaths,Packages}` (RPM metadata only) |
| inode 241033 | `/usr/libexec/weston-ivi-shell-user-interface` (the binary itself) |
| inode 241031 | `/usr/libexec` (directory entry) |

**No script, unit, or systemd service launches the shell UI.** The only references are config files and
RPM install metadata.

Client-side protocol (strings, per ELF):

| ELF | `ivi_controller_interface` | `screen_create` | `ivi_hmi_controller_interface` |
|---|---|---|---|
| `/usr/bin/ivi-place` (73,088 B, our tool) | 2 | 0 | — |
| `/usr/libexec/weston-ivi-shell-user-interface` (215,480 B) | 0 | 0 | 2 |
| `/usr/bin/ivi-wm` | 0 | 0 | — |
| `/app/bin/{AppHomeScreen,AppLauncher,AppEURadio,AppCamera}` | 0 | 0 | — |
| `/app/bin/ApplicationManager` | 0 | 0 | `ivi_hmi_requester` + `request_id` |
| `/usr/lib/weston/ivi-controller.so` (server) | `ivi_controller_*_interface` | **0** (has `layer_create`,`surface_create`, `create_screen` fn, `controller_screen_*`) | — |

`ivi-place` uses the ivi-controller protocol **only to list** (no `screen_create` marshal). The shell UI
uses the **HMI-controller** interface, not the ivi-controller protocol. The ivi-controller protocol has
**no client screen-create request**. Astra c7's static follow-up attributes initial layout-screen creation
to `ivi-shell.so`'s compositor-output initialization path, while `ivi-controller.so` creates per-client
controller resources during bind. The absence of an output-created listener in `ivi-window-manager.so` is
not evidence against this path; it examines the wrong component and does not exclude an initial output-list
walk. **No named client ELF creates the screen; no named launcher for the shell UI was found.**

## Task 2 — AppLauncher identity confirmed, not inferred

On-image `/app/bin/AppLauncher` sha256 = `c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268`,
`cmp` → **byte-identical** to `AppLauncher.vendor.bin`. Exact identity, not "untouched" by assumption.

## Task 3 — boot58 config == boot65 config (one post-hoc delta)

`diff weston.ini.final weston.ini.known-good` → exactly one line:
`ivi-module=…,hmi-controller.so` → `ivi-module=ivi-window-manager.so,ivi-controller.so`. That `hmi-controller.so`
was added to the **local file after boot58** (during boot61), so the image config that boot58 actually ran
was identical to boot65's known-good config. No other delta.

## Task 4 — boot58/boot65 AppHomeScreen attribution remains unresolved

The preliminary raw-log summary gives these counts, but Astra c7 flagged the summary-regex and launch/PID correlation as not yet audited. Treat the table as a lead, not a final attribution:

| | boot58 | boot65 |
|---|---|---|
| `ivi_hmi_requester` | 128 | 112 |
| `request_id("QTAPP")` | 9 | 14 |
| `create_hmi_client` | 12 | 13 |
| `"AppHomeScreen"` | **1** (`1006`) | **0** |

The protocol global and the `request_id("QTAPP")` flow are present in **both**. The current count reports more clients in boot65 (including doubled OSD/DM IDs) but no `AppHomeScreen` string. This does **not** yet prove that the application never started or that a surface regression occurred: audit the raw strings and the launch/PID/time window before assigning the difference to app behaviour, a race, or a capture failure. Identical config and AppLauncher bytes exclude those two candidate deltas only; they do not identify the cause.

## Stop condition

Per instruction, no boot. The protocol correction establishes that `screen` is a compositor-to-client event, not a client `screen_create` request; boot65's raw event stream includes a screen and layers. No named client was found that creates a screen, but the absence of such a client is not evidence that no screen exists. Do not add `hmi-controller.so` or change the config without new evidence.

## Files

- `work/vm/kbuild/ws/partimg-build/` — `weston.ini.known-good`, `AppLauncher.vendor.bin`, dumped ELFs.
- run dirs `1793931162561454000` (boot58) and `1793944643111075000` (boot65) — decoded `exported-weston.bin`.

---

## CORRECTION (addendum, post-review — do not erase the above)

Astra c7 supplied a material correction from the retained `ivi-controller.xml` and the raw W65 log.

1. **Protocol direction.** The retained `ivi-controller.xml` has only three *global requests*:
   `commit_changes`, `layer_create`, `surface_create`. `screen` is a **server event** — the compositor
   announces an existing screen to a client; there is no client `screen_create` request. So the correct
   statement is "no client *creates* a screen", **not** "no screen exists".

2. **The W65 raw log contains server-side controller events.** The trace includes a bind followed by events such as:
   ```
   wl_registry@2.bind(15, "ivi_controller", 1, new id [unknown]@11)
    -> ivi_controller@11.screen(7, new id ivi_controller_screen@4278190080)
    -> ivi_controller@11.layer(107) ... ivi_controller@11.layer(10)
    -> ivi_controller@11.surface(100|1|30000|…)
   ```
   Similar bind/event sequences recur in the stream; repeats are not distinct screens. The `screen(7)` argument must not be called a layout-screen ID: the inspected server obtains it from the client's `wl_output` resource. W58 contains the same class of events. The client process for these object IDs has not been established.

3. **`@11` is a connection-local object ID, not a client/process identity.** The protocol logger prints object IDs but the retained lines do not identify which process owns that connection. `ivi_controller_screen@4278190080` is a server-created object ID in that protocol namespace; neither it nor `@11` identifies `ivi_place`.

4. **`ivi_place`'s zero listing is observer-specific, not a system census.** Static inspection of `ivi_place.c` shows it binds `ivi_controller` but not `wl_output`, then reports after its initial registry roundtrip. In the inspected server, controller screen resources are sent only when that client has a matching output resource. Therefore the raw `@11` events cannot be attributed to `ivi_place`; its zero listing and the other client's events are compatible. The retained stream and extracted `ivi-shell.so` support compositor-side output/layout initialization, but they do not provide a complete, process-attributed inventory.

5. **No QEMU was run for this correction** — it is a static re-read of the retained `exported-weston.bin`
   (run `1793944643111075000`) and the protocol XML.

6. **Next step** (not `hmi-controller`, not a config change): use the existing boot58/boot65 process and launch records to correlate protocol connections and surface owners. Astra c7 notes that the boot58 `HOME_CLIENT=[]` summary missed a raw `AppHomeScreen` line because its regex expected the wrong punctuation; a broader search finds no such registration in W65. W65 also assigns numeric surface 1006 to `AppStandbyClock`, so ID reuse is not evidence of a collision. Compare the cold/warm/capture PIDs and time windows before attributing the difference. No boot, no config edit, no inferred race.

*Note on doc39:* its "0 layers / 0 screens" figures are ivi_place-reported and must be read as
observer-specific, not as an established absence — the raw log shows a screen and layers were present.
