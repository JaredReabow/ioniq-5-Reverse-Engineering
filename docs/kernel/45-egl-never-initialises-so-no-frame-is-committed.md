# The app never draws because EGL fails to initialise — the layer state is a second, separate gap

Date: 2026-11-08. **Offline only. No QEMU run this turn.** Sources: the retained runtime and export
channels in `evidence/controlled-run-{3,4}-2026-11-08/`, plus static inspection of
`work/decrypted-eu-260128/extracted-safe/mango-rootfs`.

This closes the causal chain that `docs/kernel/44` left at "the surface is hidden and unlayered".

## The chain, in evidence order

1. **The vendor unit launches Qt apps on generic Wayland.** `lib/systemd/system/ApplicationLauncher.service`
   contains `Environment=QT_QPA_PLATFORM=wayland` — not an IVI platform plugin.
2. **The app's own stderr says EGL failed.** In run 3's runtime channel, a staged probe captured:

   ```
   S4_HEAD=[QIODevice::read: device not open|Using Wayland-EGL|
            libEGL warning: DRI2: failed to open swrast (search paths /usr/lib/dri)|
            failed to initialize EGL dis…
   ```

3. **Therefore no buffer is ever supplied.** In the run 3 payload, the app's
   `wl_surface@15.commit()` arrives with **no preceding `attach()`**, while surface 30000 (the shell UI)
   attaches a real 1920×720 `wl_shm` buffer in the ordinary way.
4. **Independently, the layout holds the surface hidden.** `ivi_controller_surface@22` reports
   `visibility(0)`, `layer(nil)`, `source_rectangle(0, 0, 0, 0)` — reported states, per the
   request/event correction in `docs/kernel/44`.
5. **The shell UI is what is on screen.** Surface 30000 is configured 1920×720, receives
   `visibility(1)` and has a buffer. It is the KIA splash captured byte-identically at +10/+60/+110 s.

So the visible outcome of run 3 has **two independent causes**, and only one of them is layout:

| # | Gap | Evidence |
|---|---|---|
| 1 | **EGL never initialises → no frame committed** | `DRI2: failed to open swrast` + `failed to initialize EGL`; commit with no `attach()` |
| 2 | **Layout state never becomes visible/layered** | `visibility(0)`/`layer(nil)` reported; no `visibility(1)` or numeric `layer` in any retained capture |

Gap 1 is the primary one: even if the layout made the surface visible, there would be no pixels to
show.

## Where the layer-management code lives

Only libraries bind the `ivi_controller` global, and the static scan found exactly these:

| Artifact | Role |
|---|---|
| `usr/lib/libilmControl.so.1.3.91` | **IVI Layer Management** control library |
| `usr/lib/libivi-platform-interface.so.1.0.0` | IVI Qt platform interface |
| `usr/lib/libQt5WaylandClient.so.5.4.1` | Qt Wayland client |

and the binaries that pull them in:

| Binary | Note |
|---|---|
| `usr/bin/LayerManagerControl` | the layer-manager control tool |
| `usr/bin/EGLWLMockNavigation` | a vendor demo |

No stock application binary in `/app/bin` or `/usr/bin` itself references the controller glue, which
is consistent with layer management being a library/daemon responsibility rather than an app one.

**Whether the projection runs any layer manager is not established here.** The vendor unit uses generic
`wayland`, so `libivi-platform-interface` may not be engaged for these apps at all. That is a lead, not
a finding.

## A hypothesis this rules out, honestly

The projection's Qt drop-in (`50-vm-gl.conf`) was a candidate for disabling the IVI platform path. It
is not: it sets only `LD_LIBRARY_PATH`, `LIBGL_DRIVERS_PATH`, `LIBGL_ALWAYS_SOFTWARE`,
`GALLIUM_DRIVER` and `LP_NUM_THREADS`, and does **not** touch `QT_QPA_PLATFORM`. The projection is
faithful on that axis.

## The precise contradiction to resolve next

The drop-in sets `LIBGL_DRIVERS_PATH=/opt/software-egl18/dri`, `prepare.json` records
`swrast_dri.so → /usr/lib/dri/swrast_dri.so`, and the runner **still** reports
`failed to open swrast (search paths /usr/lib/dri)`.

So one of these is true, and they are cheap to distinguish offline:

- the file at `/usr/lib/dri/swrast_dri.so` is present but not loadable by the vendor `libEGL` (wrong
  Mesa/ABI build);
- the environment does not reach the app process (the vendor unit's own
  `Environment=LD_LIBRARY_PATH=/app/lib` or `AppLauncher.sh` overrides the drop-in);
- the vendor `libEGL` ignores `LIBGL_DRIVERS_PATH` and uses its own search path, so the staged
  `swrast` in `/opt/software-egl18/dri` is never consulted.

The first is testable against the staged image (file present, `llvm-readelf` SONAME/ABI, needed
symbols against the vendor `libEGL`). The second is testable by reading `AppLauncher.sh` for its own
environment assignments.

## Next exact action

**Resolve the swrast load failure offline, in this order:**

1. Read `AppLauncher.sh` for `LD_LIBRARY_PATH` / `LIBGL_DRIVERS_PATH` / `EGL_` assignments that would
   override the drop-in, and check whether `AppHomeScreen` is exec'd through it.
2. Inspect the staged `/usr/lib/dri/swrast_dri.so` and `/opt/software-egl18/dri/*` against the vendor
   `libEGL`: SONAME, architecture, and whether the vendor EGL's `dlopen` path could ever reach them.

Only after that is a run justified again, and the run's export trigger should be re-anchored to
protocol progress (`docs/vm/63`) rather than wall-clock.
