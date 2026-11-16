# Boot65: DRM initializes; ivi_place under-reports the compositor's screen/layer inventory

Date: 2026-11-06. Final qualified run with the known-good config (`weston_1920.ini.drm` base +
`backend=drm-backend.so`, libexec shell-UI path, `ivi-module=ivi-window-manager.so,ivi-controller.so`,
Virtual-1 1920×720). Launcher bytes and hmi-controller module untouched.

## Result

- **Config fix confirmed.** `Loading module '/usr/lib/weston/drm-backend.so'`, `initializing drm backend`,
  `Compositor capabilities`, **0** `ias-backend` / `fatal` lines. The `backend=drm-backend.so` line is
  what makes it boot (omitting it defaults to `ias-backend.so`, which is what killed boot63/64).
- **Observer output only.** `ivi_place --list` printed `0 layers, 0 surfaces, 0 screens`, exit 0, `layer ids: (none)`. The retained Weston stream contains server-side controller screen/layer events, but their connection is not proven to be `ivi_place`; see the correction below and doc 40.
- **Preliminary AppHomeScreen counter only.** `HOME_CLIENT=[]` was generated from a summary; boot58's raw log contains `create_hmi_client(1, 1006, "AppHomeScreen")`. Boot65's process/launch window and counter regex are not yet reconciled, so the summary does not establish an application regression.
- **Frame unchanged** (`129844` bytes, standby).

## Static narrowing (no config change this run)

- `ivi-window-manager.so` exports `create_layer`, `create_layer_with_plane`, `add_screen_info_to_list`,
  `get_screen_info` — it **manages** screens and creates layers, but has **no auto screen creation from
  outputs** (no `output_created` symbol).
- `ivi-controller.so` exports `create_screen`, `controller_screen_destroy`. The retained protocol XML defines
  `screen` as a server event; the protocol has no client `screen_create` request. Do not infer client-side
  screen creation from these symbols.
- `hmi-controller.so` (not loaded, per vendor template) is the only module that reads
  `ivi-shell-user-interface` and calls `create_layer`; in boot62 its init failed with
  `Failed to initialize hmi-controller`.

The original conclusion that no screen existed, that zero layers followed from that, and that a client
`screen_create` request was missing is **withdrawn**. The observed `ivi_place` counts are incomplete observer
output; the retained raw stream shows a screen and layer events. The cause of the zero listing, and the
boot58/boot65 AppHomeScreen summary difference, remain open for static observer and raw-process correlation.

## Files

- `work/vm/kbuild/boot65-final.log` — the run (host stdout).
- run dir `work/vm/kbuild/ws/runs/1793944643111075000/` — `serial.log`, `dbg-out.txt` (raw weston log
  exported as `exported-weston.bin`, 229,663 B), `result.json`.
- `work/vm/kbuild/ws/partimg-build/weston.ini.known-good` — the staged config (923 B, read back identical).
- `work/vm/kbuild/ws/partimg-build/final-run.sh` — the probe.

---

## CORRECTION (addendum — observer error)

The "0 layers, 0 surfaces, 0 screens" in this doc came from `ivi_place --list`, which is an **incomplete
observer**: source inspection shows it binds `ivi_controller` but not `wl_output` and exits after its initial
roundtrip. The raw W65 stream contains server-side screen/layer/surface events, but object IDs such as
`@11` are connection-local and the trace does not establish that this was `ivi_place`. In the inspected
server, a screen event is sent only when the client has a matching `wl_output` resource; its `screen(7)`
argument is not proven to be a layout-screen ID. See doc 40 and Astra c7. The zero listing is
observer-specific and is not evidence of a system-wide absence. The extracted `ivi-shell.so` statically
walks the compositor's existing output list to initialize layout screens, but deployed-image identity and
the complete boot65 object inventory remain bounded by retained evidence.
