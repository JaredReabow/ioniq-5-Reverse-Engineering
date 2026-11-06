# FROZEN BRIEF 5 — next best steps, after closing the instrument gap

Supersedes earlier briefs where they conflict. Frozen 2026-11-06.

## State

**A. The Block-1 instrument gap is closed.** Three things it previously could not do, now proven in
the guest with a synthetic driver:

- liveness: `/tmp/gl-draw-trace.active`, and per-call `/tmp/gl-draw-trace.calls` reporting
  `gs_v_texcoord` / `gs_a_texcoord` / `gs_u_texture` / `qt_texcoord`, so "never loaded", "loaded but
  GL never entered" and "reached, needle absent" are separable.
- real stride: `glPixelStorei` is intercepted, the dump uses the measured `GL_UNPACK_ROW_LENGTH`, and
  logs `row_length` / `alignment` plus `STRIDE-MISMATCH` when row length ≠ width.
- draw-to-texture correlation: active unit, per-unit binding and current program are stamped on both
  the upload record and the draw record. Measured: an upload reports `texid=7`, and the draw that
  consumed it reports `prog=42 tex0=7`.

**B. Content-dependence is answered.** `19-stripes-…png`: diagonal ≈45°, content-carrying stripes
confined to the effect region, chrome/text/panels crisp. Coordinate-addressing class — not fixed
hardware pitch, and *not* specifically stride, since wrong row length, a `resolution` uniform that
disagrees with the texture size, and in-shader coordinate maths (§C) all fit.

**C. The real shader corpus is GL Studio.** `app/bin/kcei/*.glsl` (amoeba, galaxy, galaxy_haze,
blur, eco, genesis + alternates), DiSTI GL Studio; `v_texCoord` / `u_texture` appear in the shipped
`.glsl`, and `a_texCoord` comes from `libglstudio_ES20_release.a` (so the attribute name is an
inference about the linked vertex stage, not proof). Several effects compute coords in-shader.

**D. Two prior results are void.** `21-flipu-removes-shear` is a blank frame, and flipu's needle
exists in no vendor binary. `22-uploaded-texture-is-clean` is all black.

**E. Unchanged:** no physical device (shared QEMU VM); no payloads / flashing / operational signature
bypass; the guest cannot reproduce the USB gadget stack. The updater verify-vs-staging question (§F
of brief 4) is still AMBIGUOUS and untouched for three runs.

## The question

1. **Single highest-value next action.** One recommendation, VM side or security side, with reasoning.
   Note the tension explicitly: the instrument is now ready, but running it needs the authentic HMI
   chain, which is the *other thread's* active area and needs weston + swrast + the partitioned image
   to stay up long enough to draw. Is the right move (a) take that chain on and run the hook pass,
   (b) hand the instrument to the other thread with a precise run recipe, or (c) do something else
   entirely, including the dormant security-side question.
2. If (a), what is the **minimum** chain needed just to get one effect draw through the hook — i.e.
   which of the five blockers is genuinely on the critical path for a *single frame*, as opposed to
   for a usable HMI?
3. What should be abandoned now?
4. Anything in A-E you think is wrong or over-claimed?

Cite §A-§E. Be decisive. Under 650 words. No preamble.
