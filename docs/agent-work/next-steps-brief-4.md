# FROZEN BRIEF 4 — next best steps, after reading the captures

Supersedes earlier briefs where it conflicts. Frozen 2026-11-06.

## Newly measured since brief 3

**A. The real shader corpus is GL Studio, not Qt.** The app ships `app/bin/kcei/*.glsl` — `amoeba`,
`galaxy`, `galaxy_haze`, `blur`, `eco`, `genesis` + alternates, 1,128 lines — built on DiSTI GL Studio
(`libglstudio_ES20_release.a`, `disti::DisplayObject::SetTexCoords`). Naming: `attribute vec2
a_texCoord`, `varying vec2 v_texCoord`, `uniform sampler2D u_texture`, sampling
`text2D(u_texture, v_texCoord)`-style. Distinct from both the dead needles and Qt's `qt_TexCoord`.
Several effects compute coordinates in-shader (`p + vec2(0.5)`, `vec2(radius*cos(angle), …)`), so a
coordinate defect here would be procedural, not a normalised varying.

**B. The content-dependence question is answered.** `19-stripes-…png` is the one real striped frame:
stripes run **diagonally ≈45°, carry content colours** (a blue smear is plainly image content), and
are confined to the effect region, while the title bar, the `STR_CAMERA_ALERT2` text and both side
panels are crisp. Verdict: content-dependent, and in the **stride / coordinate-addressing** class
rather than fixed hardware pitch.

**C. Two prior results are void.** `21-flipu-removes-shear` is a **blank frame** (title bar + cursor
only) — the shear is absent because nothing is drawn. It is also impossible independently: the flipu
rewrite needs `outTexCoords = texCoords.xy;`, which exists in no vendor binary.
`22-uploaded-texture-is-clean` is **all black**, so it never demonstrated a clean texture.

**D. The texture dump is now self-validating.** It logs `has_content=NO-UNIFORM` or `yes` with a luma
range; verified with a uniform and a gradient upload. A black dump can no longer be read as evidence.

**E. Three instruments in this workstream have now had their silence mistaken for a result**
(gl_draw_trace never loaded; its needles never matched; its texture dump could be uniformly black).

**F. Still open:** whether the updater verifies before or after staging to `/update/HU`
(AMBIGUOUS, security side, untouched for two runs).

## Unchanged constraints

No physical device (QEMU VM shared with another thread). Identify and test exploits; no payloads, no
flashing procedures, no operational signature bypass. Guest cannot reproduce the USB gadget stack.

## The question

1. **Single highest-value next action.** One recommendation, VM side or security side, with the
   reasoning that beats the alternatives. In particular: given §B, is the right move now to test the
   stride hypothesis directly, and if so what is the minimum experiment — or is there still an
   identification step missing before any test is meaningful?
2. §B says diagonal and content-carrying. Name the **cheapest observation that would distinguish "the
   producer's texture is sheared" from "the compositor samples it sheared"** — i.e. which side of the
   GL boundary the stride error lives on.
3. What should be abandoned now?
4. Anything in A-F you think is wrong or over-claimed?

Cite §A-§F. Be decisive. Under 700 words. No preamble.
