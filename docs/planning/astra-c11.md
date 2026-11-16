# Astra C11 — QUALIFY FOR THE NARROW CLAIM: freeze the exporter, stop hardening, next session is the run

Decision consultation, 2026-11-08, following two rejections (`docs/planning/astra-c9.md`,
`docs/planning/astra-c10.md`). No file was written by the consultation.

The question put to Astra was not another code review. It was: after two rejections and three
sessions, is this instrument worth more work, and what is the strongest claim it can honestly carry?

## Decision

**QUALIFY FOR THE NARROW CLAIM.** Freeze revision 3 and use it as an **evidence-export tool**, not as
certification of runtime behaviour.

Astra's reasoning, which is the part that ends the loop:

> On your stated premise that revision 3 fixes the concrete defects, none of A1, A3 or A4 blocks the
> narrow claim below. They block stronger interpretations. Another hardening round cannot change that
> distinction.

That is the resolution of the tension this project was stuck in. The three gaps are not defects to be
fixed; they are the boundary between what an exporter can report and what only runtime evidence can
establish.

## The narrow claim

> The retained payload contains the specified structured marker, and its received byte count and
> digest match the completed capture transaction. That transaction records checks that the named
> driver's bytes matched the frozen manifest and that the supplied process identity passed the
> helper's checks around copying; these checks do not establish driver execution, attribution of the
> marker to that process generation, or an atomic or complete record of producer activity.

Astra corrected the draft wording in two places, and both corrections matter:

1. **"exported by a run whose driver bytes matched"** was rejected because it risks identifying the
   checked file as the actual driving program. Use **"whose named driver file matched"**.
2. **"closed snapshot"** is acceptable **only** if explicitly defined as *a fixed exported byte
   sequence*, never as a coherent point-in-time snapshot of the source.

## Sufficient for the next run?

**No — not by itself.** Astra gives two separate reasons:

> A marker in these bytes does not establish the claimed execution or generation. Even an
> unquestionably genuine registration event does not establish persistence, rendering or interaction.
> Boot58's **112 ms** of retained tail after registration is particularly inadequate evidence of
> persistence.

But, crucially, that does not make the run unjustified:

> That does not make the next run uninterpretable or unjustified. It makes this exporter insufficient
> as its sole evidence source.

This is a change in the instrument's **assigned responsibility**, not permission to interpret runs
casually.

## Citation rules (adopted verbatim)

A future reader may cite the narrow claim only when:

1. **The evidence package is retained:** exact driver, helper, manifest and verifier bytes;
   invocation/configuration records; raw receipt; received payload; and verifier result.
2. **The received transaction is validated:** the final transaction is complete, has exactly the
   required terminal success, and its payload's independently checked length and digest agree.
   Guest-side success alone is insufficient.
3. **The marker is identified concretely:** state the structured pattern and its location in the
   retained payload. Report recorded timestamps as recorded timestamps, not proof of source coherence.
4. **The three limitations accompany any runtime interpretation.** A checked process tuple is
   supporting context, not event attribution.
5. **Nulls remain per-cause.** A truncated window remains `CAPTURE_TRUNCATED`, never a confirmed
   negative. Missing or invalid evidence remains its corresponding failure or uncertainty.
6. **Absence remains bounded to the payload.** Even `REGISTRATION_ABSENT` must not become "Home failed
   to register." As `docs/kernel/43` warns, reaching the precursor plus 96,445 ms is not proof of
   reaching Home's registration opportunity, nor of complete logging.

### Sentences that must never be written on this instrument's authority

- "This is a generation-attributed capture."
- "The manifest proves that the driver ran."
- "This is an atomic snapshot of the compositor log."
- "The capture contains all activity during the observation interval."
- "`REGISTRATION_PRESENT` proves that authentic Home persisted."
- "`REGISTRATION_ABSENT` proves that Home did not register."
- "A truncated window confirms absence."
- "The boot58/boot65 comparison is now attributable."

Stronger claims require separately cited evidence that actually establishes them.

## What would have been the wrong approach

> The wrong approach would be continuing to make this exporter responsible for proving execution,
> generation ownership and persistence. **Keep the capture harness; stop treating it as the
> experiment's entire evidentiary basis.**

## Next exact action (adopted)

**Freeze revision 3 without another hardening cycle**, then conduct the single planned run with two
explicitly separate evidence channels:

- **Export evidence** — the retained, validated capture package described above.
- **Runtime evidence** — a retained external execution record tying the run to the frozen launch
  chain, plus continuous display recording and contemporaneous lifecycle observations over a
  persistence interval **fixed before launch**. Record an input and its visible response if claiming
  interactivity.

Reporting rule to set **before launch**: **marker presence is an artifact result; registration,
persistence and interaction are separate runtime conclusions.** If runtime evidence cannot establish
one of them, report that part as **unresolved** — not absent, and not a reason to resume polishing
the exporter.

> The next working session should be the controlled run, not revision 4 of the capture harness.

## Consequence for this project

The instrument loop is closed. Revision 3 is frozen at whatever state it is in, its limits are
recorded above, and further work on it is out of scope unless a specific defect blocks the narrow
claim — which Astra states no remaining defect does.
