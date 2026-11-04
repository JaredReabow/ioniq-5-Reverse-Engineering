# Fastest path to a fully working VM

Ordered by cost-to-information, not by importance. Every step below has a falsifiable outcome and names
what would make it fail, so a failed step costs one run rather than a day.

## Sequencing principle

Three tests are cheap enough to run before committing to any larger work, and each can eliminate a whole
category:

1. `GL_CLAMP_TO_EDGE` on non-power-of-two textures (blocker 1) — one interposition, already designed.
2. `request_fg` for AppNavi's surface id (blocker 2) — the same call that already works for the home
   screen; nobody has aimed it at AppNavi.
3. A DRM-capable device for the vendor backend (blocker 5) — QEMU can expose one; if `ias-backend.so`
   binds, GL becomes possible and blocker 5 stops being structural.

If (3) works, everything downstream gets easier and it should be done first for that reason alone.

## Blocker 1 — home-screen image rendering

- **Test A (1 run):** interpose `glTexParameteri`, force `GL_CLAMP_TO_EDGE` for non-POT textures. Success:
  the striped field is replaced by recognisable art. Failure: unchanged.
- **Test B (1 run, only if A fails):** combine clamp with the shader rewrite already built, mapping
  `texCoords` into 0..1 before use (`(u * 0.5) + 0.5`). Success: art appears correctly framed.
- **Test C (if both fail):** the sampler is not honouring wrap state at all under this stack — then the
  workaround is to resample the *texture* to a power of two in the upload interposer and scale the
  coordinates to match. That is larger but fully under our control.
- **Do not** re-test upload formats, alignment, ASTC, or asset trees; all four are measured clear.

## Blocker 2 — home ↔ navigation compositing

- **Test (1 run):** during a chain run, read AppNavi's surface id from the compositor log
  (`Surface id(N), Weston surface W(…), H(…)`) and issue `ivi_wm <id>` — the same `set_surface_layout` /
  `set_surface_visible` / `request_fg` sequence that made the home screen appear.
- If it works, the remaining work is to make whatever normally performs this call do it: the app
  manager's foreground contract, which the DLT log already records (`WINM` lines show
  `request_fg`, plane and layer activity).
- If it does not, read `WINM` in the DLT log for the rejected request and adjust plane/layer arguments
  rather than guessing.

## Blocker 3 — client instability

- `AppNavi` dies in `libQt5Core` at ~55 s and `AppCamera` in `free()+0x14` at ~181 s. Both are crashes in
  a machine with no debugger.
- **Cheapest characterisation (1 run each):** reuse `/etc/ld.so.preload` with an interposer on the
  service that each client dereferences at that moment. The DLT log timestamps the last call before the
  fault, which narrows the target without a debugger.
- **Pragmatic alternative:** the application manager stops siblings when one dies, which is what makes
  windows vanish in long runs. If the projection is meant to demonstrate a working HMI rather than a
  fault-tolerant one, running the chain without the crash-prone clients is a legitimate configuration —
  record which clients are excluded and why.

## Blocker 4 — the service landscape

This is the only blocker that is pure throughput, and it is what the worker agents are for. Each item is
independent, testable in isolation, and follows the MICOM pattern exactly (find the contract in the
shipped interface XML, own the bus name, answer with well-formed replies, verify by observation).

| Adaptor | Contract source | First deliverable |
| --- | --- | --- |
| Audio / MMUS / C-TRACS | `com.lge.car.micom.audio` XML in the vendor binaries; AM/CTRACS interface files in the image | Stub owning the name, answering the audio asks the home screen issues at startup |
| Persistence (deeper) | `org.genivi.persistence.admin` (stub exists) | Key/value storage so clients round-trip state instead of failing |
| Input (touch/keys) | `ivi_window_manager`/`ivi_input_controller` protocols; the input harness already in `vm/repro` | A synthetic touch that presses a home tile and produces a screen change |
| Restart / suspend | systemd units and the MICOM power interfaces | A scripted suspend/resume that does not lose the compositor |

## Blocker 5 — no GL-capable renderer

- **Test (1 run):** boot with a DRM device exposed and start the vendor backend directly:
  `backend=ias-backend.so` with the shipped `weston_1920.ini`. Success: the compositor comes up on the
  vendor's own backend, which is what the vehicle runs, and GL becomes available through it.
- Failure modes and what they mean: no `/dev/dri` node → the VM has no GPU device and the path is closed
  without emulation work; backend fails on an ioctl → the vendor backend needs a specific device the VM
  does not provide, and pixman remains the only renderer, in which case blockers 1–3 must be solved
  *within pixman's tolerances* rather than at the driver level.
- **If this fails, stop treating it as a blocker and treat it as a constraint.** Every workaround built so
  far (clamp forcing, shader rewriting, shader-level coordinate mapping) is a legitimate emulation
  adaptation and belongs in the repository as such.

## What not to do

- Do not re-derive what is already measured clear: asset formats, ASTC, upload alignment/row length/format,
  output geometry, capture tooling, compositor, research backend, Gallium driver.
- Do not build an instrument before the check that proves it reached its target; the last three
  instruments each cost a run to discover they were not being consulted.
- Do not kill `early-background` to clear the screen; that manufactures an artefact.

## Parallelisation

Blockers 1, 2, 3 and 5 are single-run probes that must be done in sequence by one agent, because they
share the same VM and the same instrument set. Blocker 4 is four independent adaptors and can be built in
parallel by worker agents, each with its own contract source and its own verification run.

## Second opinion (Astra + Fable), and what changed

Both reviewed the five blockers. They **agreed on blocker 5** and disagreed usefully elsewhere. Corrections adopted:

### Blocker 1 — the cause is probably the coordinates, not the wrapping

- Astra: *"NPOT dimensions alone do not establish a driver bug"*, and the leading hypothesis is **UV range/normalisation**, not wrap state. It also warns that **negating `u` is not a
  fix** — it can simply move invalid coordinates onto a clamped edge, which is exactly what the empty frame in §3.22.0 looks like.
- Fable supplies the mechanism to test: the material likely feeds **pixel-space texcoords** intended for `samplerExternalOES`/EGLImage, and on this stack the plain `sampler2D` path is what
  compiles, so `u ≈ 0..1926` under REPEAT gives `frac(u)` stripes — which is why the extent scales with the transform and why flipping the sign changes it.
- **Resulting first test: dump the FRAGMENT shader** (only the vertex shader has been captured so far) and inject `texcoord /= vec2(1926.0, 753.0)` before the sample. Clean image ⇒ confirmed.
  Still striped ⇒ dump the attribute type/stride/normalised flag for that draw. Both are one run each.

### Blocker 2 — the first question is buffer type, not arbitration

- Fable: check whether AppNavi attaches **`wl_drm`/dmabuf** buffers. The pixman renderer **cannot composite dmabuf**, silently — which would explain "renders genuine map pixels into its
  own surface" and "never appears". If dmabuf, force the shm/software path for that client.
- Astra prefers tracing the activation request through appmanager to surface identity, layer, visibility and z-order, and one diagnostic forced promotion to separate arbitration from
  placement. Do the buffer-type check first because it is a single `strace`, and it can end the question before any policy work.

### Blocker 3 — do it now, as instrumentation, not as a fix

- Fable: preload a shim installing `SIGSEGV`/`SIGABRT` handlers that call `backtrace_symbols_fd()` — **a real stack trace with no debugger**, which is the capability this project has
  been missing all week. Add `MALLOC_CHECK_=3` and `GLIBC_TUNABLES=glibc.malloc.tcache_count=0` so the `free()` corruption aborts at the culprit.
- Both suspect the deaths are **symptoms of blocker 4** (a ~55 s service timeout; a double free on a null reply). Cheapest ordering: get the traces, then see whether the service
  adaptors retire them. Astra adds the caveat that `libQt5Core` and `free()+0x14` identify **crash sites, not causes**, and that both crashes should not be assumed to share one defect.

### Blocker 4 — isolation contract (both agree)

- One adaptor per `/opt/adapt/<name>/` with its own shim, unit and config. **Nobody edits shared files**: `/etc/ld.so.preload`, launcher config and unit enablement are generated from a
  manifest by a single integration owner at image build. Astra: one immutable base image plus per-lane overlays and private disks. Fable: develop each adaptor against a captured
  golden/replay log instead of VM boots.
- Staging: **null responder first** (well-formed replies to everything), then fidelity. Order: **persistence → input → audio (C-TRACS/MMUS) → suspend/restart**, integrating one lane per
  run. Fable's bet is that persistence retires blocker 3 on its own.

### Blocker 5 — both call it a trap; do not port virtio-gpu

- Astra: `/dev/dri` does not supply vendor DRM ioctls, buffer layouts, EGL extensions or plane semantics; **full IAS hardware emulation is the schedule trap**. Acceptable variant: an
  ABI-matched headless EGL backend/backport using software GL, or surfaceless EGL — **no virtio-gpu required**.
- Fable: three ports (vendor kernel driver, Mesa driver, host virgl) before learning anything; same conclusion.
- Time-boxed to **2 agents, ~1 day**, and it must prove **EGL init *and* import/render of an actual client buffer** — a standalone GL triangle is not evidence. If not green, pixman is
  final and nothing in blockers 1–4 depends on it.

### Revised order (fastest to all five)

1. **Blocker 3 instrumentation** — signal-handler traces + malloc checking. Half a day, and it makes every later crash diagnosable.
2. **Blocker 1** — fragment shader dump, then UV normalisation test, then attribute dump.
3. **Blocker 2** — dmabuf-vs-shm strace, then one forced promotion.
4. **Blocker 4** — four isolated lanes in parallel, null responder first, integrate in the order above.
5. **Blocker 5** — time-boxed probe at the end, or never.

### Worker allocation (Astra)

8 service · 3 sampling · 3 crash · 2 arbitration · 2 GL · 2 integration/test, with centralised VM-run scheduling and one causal variable per experiment.

### Do not attempt (both, condensed)

Re-proving verified subsystems · blind kernel/Mesa/QEMU replacement · full IAS hardware emulation or a virtio-gpu/virgl port · GPU acceleration as an ASTC cure · software ASTC decode
(pre-transcode assets instead) · blanket success stubs · permanent shader or foreground hacks that hide a defect · building a guest debugger · editing assets or data files to work around
blocker 1.
