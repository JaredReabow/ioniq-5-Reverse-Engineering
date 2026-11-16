# Handoff: one single-frame run through the shader/trace hook

Both independent reviewers (Opus 4.7, Astra) recommended handing this to the thread that owns the
authentic-HMI bring-up rather than starting a competing chain here. This is the run contract.

## What the hook is

`tools/uk_fw/ias_backend_soft/gl_draw_trace.c`, built to `gl-draw-trace.so` (see below). It is an
`/etc/ld.so.preload` interposer, which is the only mechanism that reaches launcher-spawned processes
because the vendor launcher rebuilds its children's environment.

Build:
```
work/toolchains/zig-macos-aarch64-0.13.0/zig cc -target x86_64-linux-gnu -shared -fPIC -O1 \
  -o tools/uk_fw/ias_backend_soft/gl-draw-trace.so \
  tools/uk_fw/ias_backend_soft/gl_draw_trace.c -ldl
```

## What it writes

| path | meaning |
|---|---|
| `/tmp/gl-draw-trace.active` | `loaded pid=<n>` — the library was loaded by this process |
| `/tmp/gl-draw-trace.calls` | one line per `glShaderSource`, with `gs_v_texcoord` / `gs_a_texcoord` / `gs_u_texture` / `qt_texcoord` and the dead flags kept for continuity |
| `/tmp/gl-draw.log` | `texture dumped <wxh> texid=<n> fmt=<n> type=<n> has_content=<yes|NO-UNIFORM> luma_min= luma_max= row_length= alignment=[ STRIDE-MISMATCH]`, plus `drawE … prog=<n> tex0=<n> tex1=<n>` |
| `/tmp/tex-<n>.ppm` | the dumped upload |

## What is proven and what is not

Proven, with a **synthetic driver only** (`tools/uk_fw/guest/gl_shader_probe.c`):

- liveness — the constructor fires and the call log distinguishes "never loaded" from "loaded but GL
  never entered" from "reached, needle absent";
- measured stride — `glPixelStorei` is intercepted, the dump uses the real `GL_UNPACK_ROW_LENGTH`, and
  `STRIDE-MISMATCH` is emitted when row length ≠ width;
- upload↔draw correlation — an upload reports `texid=7` and the draw that consumed it reports
  `prog=42 tex0=7`.

**Not proven:** any of this against the authentic HMI. In particular, the correlation was only shown
for a single-texture, unit-0, no-FBO case. GL Studio may use framebuffer objects with multiple colour
attachments, texture units above 0, or rebind between upload and draw. If a draw shows `tex0=0` for a
textured draw, the tracking did not reach the target and **no correlation may be claimed** — report
the limitation rather than inferring a texture.

Also: the `gs_a_texcoord` key rests on the inference that the linked vertex stage uses `a_texCoord`
(the shipped kcei `.glsl` files are effectively fragment-only; the vertex side comes from
`libglstudio_ES20_release.a`). If that inference is wrong, "reached, needle absent" will mis-fire.

## Minimum chain for ONE frame

Needed:

1. weston + swrast giving a working EGL/GLES2 context — non-negotiable, the hook sits on `gl*` symbols;
2. enough of the partitioned rootfs to exec the kcei host and `dlopen` its runtime deps, with the
   `.glsl` files resolvable at their shipped paths;
3. one GL Studio effect driven to its first `glDrawElements` / `glDrawArrays`. **A single frame is
   enough.**

Explicitly **not** on the critical path for one frame: CAN simulation, Qt scene composition, vehicle
chrome and panels, audio, connectivity, input, boot-to-login polish, animation timing. Anything that
only matters for a *usable* HMI is deferrable for this experiment.

## Decision matrix — read this, not the screenshots

Take one frame with an identifiable effect from `app/bin/kcei/` and fill in:

| observation | conclusion |
|---|---|
| no `/tmp/gl-draw-trace.active` | hook not loaded; **no conclusion possible** |
| `.active` but no `.calls` lines | loaded, GL never entered; **no conclusion possible** |
| `.calls` lines but `gs_*` all `no` | reached, but the effect-program hypothesis is unconfirmed; check the attribute-name inference above |
| `texture dumped … has_content=NO-UNIFORM` | the dump captured nothing — **this is not "a clean texture"** (this exact mistake was made with `22-uploaded-texture-is-clean`) |
| `… STRIDE-MISMATCH` | the producer uploaded with row length ≠ width; stride hypothesis is live |
| `drawE … tex0=0` | correlation failed; **do not attribute any texture** |
| dumped texture (matching the draw's `texid`) already shows the diagonal stripes | the shear is on the **producer/upload** side |
| dumped texture clean but the output frame sheared | the shear arises during **sampling or downstream**; then check the `resolution` uniform and the effect's in-shader coordinate maths |

Reject a blank screenshot or an all-black dump as evidence of either a fix or a clean source. Two
earlier results in this repository (`21-flipu-removes-shear`, `22-uploaded-texture-is-clean`) are void
for exactly that reason.

## What this run would and would not settle

It settles **which side of the GL boundary** the corruption is on: producer/upload versus
sampling/downstream. It would **not** by itself distinguish among the three surviving mechanisms on
the sampling side (wrong row length, a `resolution` uniform disagreeing with the real texture size,
in-shader coordinate arithmetic). Treat the result as narrowing, not as a diagnosis.
