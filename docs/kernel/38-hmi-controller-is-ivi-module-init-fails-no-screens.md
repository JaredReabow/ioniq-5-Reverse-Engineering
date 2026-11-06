# The hmi-controller is an ivi-module (not a core module); it now loads but its init fails — the ivi-layout has no screens

Date: 2026-11-06. Loading `/usr/lib/weston/hmi-controller.so` — the component that reads
`ivi-shell-user-interface` and owns `hmi_controller_home` / `layout_mode` / `UI_ready`.

## Step 1 — `modules=` is the wrong mechanism

With `modules=/weston-vm-input.so,/usr/lib/weston/hmi-controller.so`:

```
Loading module '/usr/lib/weston/hmi-controller.so'
Failed to lookup init function: … undefined symbol: module_init
```

`hmi-controller.so` exports **`controller_module_init`**, not `module_init`. That is the ivi-module
entry point: `ivi-window-manager.so` and `ivi-controller.so` export the same symbol, and they are loaded
via `ivi-module=`, not `modules=`. The core `modules=` list (which loads `module_init`) is only for
weston's own helpers such as `/weston-vm-input.so`.

## Step 2 — `ivi-module=` loads it, but init fails

With `ivi-module=ivi-window-manager.so,ivi-controller.so,hmi-controller.so`:

```
Loading module '/usr/lib/weston/hmi-controller.so'
Failed to initialize hmi-controller
ivi-shell: Initialization of controller module fails
```

The module now loads (no symbol error) but `hmi_controller_create` returns failure. Disassembly of
`controller_module_init` shows it reads the `[ivi-shell]` keys (`ivi-launcher`, `workspace-id`,
`layout_surface`, `base-layer-id-offset`, `surface-id-offset`, …) and then calls `create_layer` several
times, checking a layer count after each. The failure is consistent with the invariant observed in every
prior run: `ivi_place` reports **0 layers / 0 surfaces / 0 screens**, even though the drm output
`Virtual-1` exists. The hmi-controller cannot build the home layout against a layout with no screens, and
that is the next question.

## Files

- `work/vm/kbuild/boot62-diag.log` — the run with the full compositor log.
- `work/vm/kbuild/ws/partimg-build/weston.ini.final` — the config (now correct `ivi-module=` placement).
- the binary: `/usr/lib/weston/hmi-controller.so` (183,720 B), dumped to
  `work/vm/kbuild/ws/partimg-build/` as `hmi-controller.so` for static work.
