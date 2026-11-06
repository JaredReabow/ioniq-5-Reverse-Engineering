# FROZEN BRIEF 3 — next best steps, after the "dead needle" finding

Supersedes brief 2 where it conflicts. Frozen 2026-11-06.

## Newly measured since brief 2

**A. Every `shader-fix-*` variant was dead.** A sweep of the shipped rootfs found `outTexCoords` in
**no vendor binary** — not `/usr/lib`, `/app/lib`, `/app/bin`. `libQt5Quick.so.5.4.1` uses
`qt_Vertex`, `qt_MultiTexCoord0`, `qt_VertexTexCoord`, `tCoord`, `vTex` (attributes) and
`qt_TexCoord0`, `qt_TexCoord`, `sampleCoord`, `sCoordDown/Left` (varyings), sampling as
`texture2D(qt_Texture, qt_TexCoord)` or `texture2D(imageTexture, textureCoords)`.

So the two needles — `outTexCoords = texCoords.xy;` and `texture2D(texture, outTexCoords)` — occur
nowhere. All six variants (`swap`, `flipu`, `tinyuv`, `fragnorm`, `norm`, `flipv`) searched for text
the vendor never emits and could never fire. **No earlier shader result is evidence in either
direction**; the UV-normalisation hypothesis itself is untested, not refuted.

**B. A false negative nearly hid A.** The first sweep ran against `extracted-safe` and returned zero
for `outTexCoords` *and* for `qt_Vertex`. `qt_Vertex` is a Qt built-in, so its absence proved the
search never reached the libraries — `extracted-safe` has no `libQt5Quick`. Re-running against
`extracted-partial-bsdtar` gave `qt_Vertex` ×15. **Which extraction tree a tool is pointed at is a
live correctness hazard in this repo.**

**C. The instrument is repointed and verified.** `/tmp/gl-draw-trace.calls` now carries
`real_qt_tex`, `real_samplecoord`, `real_multitex0`, `real_imagetc` alongside the dead flags. Proven
in the guest against a verbatim Qt-shaped shader: `dead_frag=no dead_vtx=no real_qt_tex=yes
real_multitex0=yes`.

**D. Still open from brief 2:** whether the updater's signature verification runs before or after the
`/update/HU` staging copy (the "continuity of authenticated bytes through use" question). Verdict
remains AMBIGUOUS. Not pursued since.

**E. Still open from brief 1:** the virtual size of the vendor app's own shader set, i.e. the app
is QML and its `ShaderEffect` sources (if any) live in the app tree, not in Qt. Not checked.

## Unchanged constraints

No physical device (QEMU VM shared with another thread). Identify and test exploits; no payloads, no
flashing procedures, no operational signature bypass. Guest cannot reproduce the USB gadget stack.

## The question

1. **Single highest-value next action now.** One recommendation. VM side or security side, and why it
   beats the alternatives. Given §A, is the correct move to rebuild the Block-1 test against a real
   shader, to go static on the app's own shader sources (§E), or to drop Block-1 entirely because the
   artefact may not be a UV problem at all?
2. §A invalidated six variants at once. What is the cheapest way to establish, before building any
   replacement, **whether the striping artefact is even a shader-coordinate problem**? Name the
   discriminating observation.
3. What should be abandoned now?
4. Anything in A-E you think is wrong or over-claimed?

Cite §A-§E. Be decisive. Under 700 words. No preamble.
