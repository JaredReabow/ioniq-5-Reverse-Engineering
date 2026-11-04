# Authentic HMI: `esinit → weston` now brings up a working compositor

This records the result of the fidelity task: the **authentic** boot path — vendor kernel → `/lib/systemd/esinit`
(the MICOM SPI gate opened by a stand-in) → esinit's own `/usr/bin/weston --tty=1` — now reaches multi-user **and**
leaves a live compositor on a wayland socket, on which a frame can be captured and a surface placed through the
vendor `ivi_window_manager` interface. The work lives in a CoW clone `work/vm/stockhmi`; the other workspaces are
untouched.

**Result: yes, the authentic path renders.** Measured in `work/vm/stockhmi/runs/1793797955485966000`
(`--init /init-authentic-hmi.sh`):

```
[auth-hmi] WAYLAND_SOCKET_UP after 2s
[auth-hmi] CAPTURE_pre-place  bytes=129844 magic=89504e470d0a1a0a sample_nonzero=70/512
[auth-hmi] IVI_WM id=30000 rc=0 out=[... bound ivi_window_manager ... set_surface_layout(30000, 0, 0, 1920, 720) ... ]
[   97.325780] systemd[1]: Reached target Multi-User System.
[auth-hmi] MONITOR_END alive_through=160s pidof=[763]
[auth-hmi] CRASH_FILE=absent
[auth-hmi] CAPTURE_final    bytes=129844 magic=89504e470d0a1a0a sample_nonzero=70/512
```

- **Multi-user** is reached at 97.3 s.
- **The compositor is alive** through the whole 160 s monitor window (well past multi-user); `/tmp/weston.crash`
  is absent and `pidof weston.real` returns 763 at the end.
- **A frame is captured** by `/usr/libexec/weston-screenshooter`. The magic bytes are `89 50 4e 47 0d 0a 1a 0a`
  — a **PNG** (`\x89PNG\r\n\x1a\n`), **not** PPM. The shipped screenshooter calls `cairo_surface_write_to_png`
  (see below), so the task's "(writes PPM)" parenthetical is wrong for this binary; the instruction that matters —
  *check the magic, not the extension* — is followed literally.
- **A surface is placed** with `/usr/bin/ivi-wm` (surface ids 30000 and 1001), exit 0: the client binds
  `ivi_window_manager`, its `set_surface_layout`/`set_surface_visible`/`request_fg` requests round-trip, proving the
  vendor ivi interface is reachable and answerable on the authentic path.

---

## The config installed

`esinit` derives `LCD_TYPE` from `/sys/module/micom/parameters/lcd_type`. On this projection the driver reports
`LCD TYPE: 3`, which falls through esinit's `if/elif/else` to `LCD_TYPE="1920"`, so the selected variant is
`weston_1920.ini` (confirmed from the boot log and `esinit` lines 92–106). `install_westonPngLogo.sh` then links
`/tmp/weston.ini -> /etc/xdg/weston/weston_1920.ini`, which is what weston reads through
`/etc/xdg/weston/weston.ini -> /tmp/weston.ini`.

The installed `/etc/xdg/weston/weston_1920.ini` is the shipped file with exactly three edits:

```ini
[core]
shell=ivi-shell.so
idle-time=0                      # added (projection-only): keep the headless backend repainting for capture
backend=headless-backend.so      # was backend=ias-backend.so  (the software stand-in for the DRM backend)

[ivi-shell]
ivi-module=ivi-window-manager.so,ivi-controller.so
ivi-shell-user-interface=/usr/libexec/weston-ivi-shell-user-interface
                                # path restored: the shipped /usr/lib/weston/... path does not exist in the image;
                                # the binary ships at /usr/libexec/ (changelog §2.80.0)
cursor-theme=default
cursor-size=32
base-layer-id=1000
workspace-background-layer-id=2000
workspace-layer-id=3000
application-layer-id=4000
transition-duration=300
background-image=/usr/share/weston/background.png
background-id=1001
panel-image=/usr/share/weston/panel.png
panel-id=1002
tiling-image=/usr/share/weston/tiling.png
tiling-id=1003
sidebyside-image=/usr/share/weston/sidebyside.png
sidebyside-id=1004
fullscreen-image=/usr/share/weston/fullscreen.png
fullscreen-id=1005
random-image=/usr/share/weston/random.png
random-id=1006
home-image=/usr/share/weston/home.png
home-id=1007
workspace-background-color=0x99000000
workspace-background-id=2001

[output]
name=HDMI1
mode=1920x720

[output]
name=HDMI2
mode=mode=1280x720
```

Everything downstream of the backend line is the shipped text: the `ivi-shell.so` shell, the vendor
`ivi-window-manager.so` + `ivi-controller.so` module list, the layer ids, the image ids and both `[output]`
sections (both inert under the headless backend, which ignores `[output]` and sizes its single output from
`--width`/`--height`). `backend=headless-backend.so` is the vendor's **own** headless backend, already shipped in
`/usr/lib/weston/` — so the backend substitution uses a shipped vendor module, not an injected one.

---

## The instruments, and why each is labelled projection-only

Nothing in the shipped system is patched. Four projection-only pieces make the authentic call run under QEMU, all
written into `p5` and recorded in `prepare.json` `guest_additions`:

1. **`/usr/bin/weston` — a wrapper script** (the authentic binary is preserved unchanged at
   `/usr/bin/weston.real`). It is the interposition point for the three substitutions esinit cannot provide, and
   it records its argv for evidence:

   ```
   weston-wrap: argv=[--tty=1]
   weston-wrap: HOME=[/etc/xdg/weston] XDG_RUNTIME_DIR=[/run/user/root]
   weston-wrap: GALLIUM_DRIVER=[] LD_LIBRARY_PATH=[]
   weston-wrap: exec=/usr/bin/weston.real --use-pixman --width=1920 --height=720
   ```

   - **Software-GL environment** (`GALLIUM_DRIVER=softpipe`, `LIBGL_ALWAYS_SOFTWARE=1`,
     `LIBGL_DRIVERS_PATH=/opt/software-egl18/dri`,
     `LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib`).
     The vehicle's `ias-backend.so` gets its GL from the Intel GPU; QEMU has none, so these point at the injected
     softpipe/swrast stack. esinit itself exports only `HOME=/etc/xdg/weston` and `XDG_RUNTIME_DIR=/run/user/root`.
   - **`LD_PRELOAD=/usr/lib/weston/pixman-solid-shim.so`** — the decisive fix (below).
   - **`--tty=1` stripping** and **`--use-pixman --width=1920 --height=720` addition** (below).

2. **`/usr/lib/weston/pixman-solid-shim.so`** — `tools/uk_fw/ias_backend_soft/pixman_solid_shim.c`, preloaded into
   weston only. See "the real blocker" below. It resolves one symbol (`pixman_image_create_solid_fill`) ahead of
   libpixman; no vendor binary is modified.

3. **`/init-authentic-hmi.sh`** — the init wrapper. It forces `/sys/module/micom/parameters/spi_validation=1` in a
   background loop (the same stand-in as `tools/uk_fw/guest/init-esinit-spi.sh`), launches
   `/weston-auth-check.sh`, and `exec`s the authentic `/lib/systemd/esinit`. Projection-only stand-in for the MICOM
   SPI handshake.

4. **`/weston-auth-check.sh`** — the verification monitor that produced the evidence lines above. Projection-only.

Also placed (required by the task, and harmless when not selected): `/usr/lib/weston/ias-backend-soft.so`
(`tools/uk_fw/ias_backend_soft/ias-backend-soft.so`), our software stand-in for `ias-backend.so`;
`/usr/bin/ivi-wm` and `/usr/bin/ivi-place` (our ivi clients); and `/opt/software-egl18/{lib,dri}` (the softpipe/LLVM
software-GL stack for GL clients). The backend actually selected is the **shipped** `headless-backend.so`.

---

## The two command-line facts the task asked about, precisely

### `--tty=1` conflicts with the headless backend — yes, and here is the exact mechanism

`esinit` runs `/usr/bin/weston --tty=1` (no `--config`). In this weston build `--tty` is **not** a core option; it is
declared only by the DRM/fbdev backend option tables. The headless backend's table is
`{width, height, use-pixman, transform}` — no `tty`. weston's `main()` therefore finishes loading modules with
`--tty=1` still in `argv`, reaches

```c
for (i = 1; i < argc; i++)
    weston_log("fatal: unhandled option: %s\n", argv[i]);
if (argc > 1)
    goto out;
```

and exits with `fatal: unhandled option: --tty=1`. The wrapper strips `--tty*` and execs
`weston.real --use-pixman --width=1920 --height=720`. The `--width`/`--height` are required because the headless
backend defaults to 1024×640 and reads size only from those two options (it ignores `[output] mode=`).

### The real blocker was not `--tty`, and not the missing rear image

With `--use-pixman` and the shipped ivi config, the authentic weston aborted at
`pixman-renderer.c:277 composite_clipped: Assertion 'src_format' failed` (exit 133, signal 6). This is the known
vendor pixman defect the research tree already diagnosed (§2.46.0–§2.52.0, §2.81.0): the vendor ivi-shell draws its
own solid-colour layer/screen backgrounds through `pixman_image_create_solid_fill()`, a solid-fill image has **no
format**, and `composite_clipped()` asserts on `src_format == NULL`. On the vehicle the GL renderer is used, so the
pixman path is never taken; under QEMU `--use-pixman` is the only renderer, so the defect fires.

`pixman-solid-shim.so` fixes it without touching a binary: it replaces `pixman_image_create_solid_fill()` with one
that returns a 1×1 ARGB32 bits image, so the fill has a real format and the assertion is satisfied.

The earlier symptom `Not found rear background image` (from `/usr/bin/early-background`, which loads
`/etc/front_lcd.png` and `/etc/rear_lcd.png`) is **not** the crash; with the solid-fill shim in place weston stays
up while that message is still logged, so it is benign on this single-screen projection.

---

## What now runs, end to end

1. Kernel mounts `p5`, runs `/init-authentic-hmi.sh`.
2. The wrapper init forces `spi_validation=1`, launches the monitor, `exec /lib/systemd/esinit`.
3. esinit takes its **OK** branch and launches `/usr/bin/weston --tty=1`.
4. The `/usr/bin/weston` wrapper records argv, exports the software-GL env, preloads the pixman solid-fill shim,
   strips `--tty=1`, and runs the authentic `weston.real --use-pixman --width=1920 --height=720`.
5. weston reads `/etc/xdg/weston/weston.ini -> /tmp/weston.ini -> weston_1920.ini`, loads
   `headless-backend.so`, `ivi-shell.so`, `ivi-window-manager.so`, `ivi-controller.so`, launches the vendor
   `early-background`, and stays up on `/run/user/root/wayland-0`.
6. systemd reaches **Multi-User System** with the compositor still alive.

Weston's own captured log (authentic binary, verbatim) for the run:

```
Using config file '/etc/xdg/weston/weston.ini'
Loading module '/usr/lib/weston/headless-backend.so'
Compositor capabilities: ... presentation clock: CLOCK_MONOTONIC_RAW ...
Loading module '/usr/lib/weston/ivi-shell.so'
Loading module '/usr/lib/weston/ivi-window-manager.so'
Loading module '/usr/lib/weston/ivi-controller.so'
ivi-controller: No ivi-input-module set
launching '/usr/bin/early-background'
```

(No `composite_clipped` abort; `weston.real` exit is never logged because it is still running.)

---

## What remains different from a vehicle

1. **Backend.** `headless-backend.so` + `--use-pixman` stand in for `ias-backend.so` + the Intel DRM/GPU. No DRM
   device, no KMS, no real HDMI output.
2. **Renderer.** Pixman CPU rendering stands in for the GL renderer. The pixman solid-fill assert is neutralised by
   the `pixman-solid-shim.so` preload rather than by fixing the vendor binary.
3. **MICOM.** The SPI handshake is simulated by the init wrapper; the real MICOM never answers
   (`[lge_lcd_init_func] Micom didn't sent SPI data`).
4. **`lge_usb_adapter` neutralised** (`install lge_usb_adapter /bin/true`), the pre-existing one-line projection fix
   so esinit does not deadlock on non-vendor hardware.
5. **`primary_screen_size` still reports `(0, 0)`.** `ivi_wm`'s `get_primary_screen_size()` reply is
   `primary_screen_size(0, 0)`. That value is published by the real `ias-backend.so` (via its `ias_crtc`/`ias_mode`
   interfaces), which we substitute; the vendor ivi-window-manager does not derive it from the headless output. This
   is the same measured gap as changelog §2.79.0–§2.81.0 and does **not** stop the compositor, the capture, or the
   `ivi_wm` layout/visibility/foreground requests (all round-trip with rc 0).
6. **`/usr/libexec/weston-keyboard` is absent** from the image (the input-method client is retried, then "giving
   up" — benign). `/usr/bin/early-background` logs `Not found rear background image` because this single-screen
   projection has no rear splash; also benign.
7. **No HMI application stack** is launched by the authentic path itself: reaching the home screen still needs the
   launcher/D-Bus/micom-service mesh that the research-init chain brings up separately. This task's scope is the
   compositor on the authentic init path, not the full launcher.

---

## Repro

```sh
# one-time injection (already done into work/vm/stockhmi):
#   edit work/vm/stockhmi/inject/*, then:
#   debugfs -w -f <cmds> work/vm/stockhmi/partimg-build/p5.img   (write inject/ files; rm before overwrite)
#   python3.13 tools/uk_fw/vm_partimg/sync-partition.py work/vm/stockhmi 5

python3.13 tools/uk_fw/vm_partimg/run-stockhmi.py --init /init-authentic-hmi.sh --timeout 230
```

`tools/uk_fw/vm_partimg/run-stockhmi.py` is the same harness override as `run-esinit-spi.py` (vendor kernel hash,
`root=/dev/mmcblk0p5`) pointed at `work/vm/stockhmi`, with `/init-authentic-hmi.sh` added to the init choices.
`tools/uk_fw/vm_partimg/sync-partition.py` copies only the changed 1 MiB chunks of `p5.img` back into `rootfs.img`
so the 36 GiB image is not rewritten (the host APFS volume was nearly full; a full sparse_copy of p5 would need
~5 GiB of fresh blocks).
