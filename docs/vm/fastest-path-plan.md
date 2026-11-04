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
