# Next-step decisions: three independent reviews

Brief frozen as `docs/agent-work/next-steps-brief.md` (commit `84f4b12`). Three reviewers were given
the identical brief and asked to decide independently, without sight of each other's answers.

| reviewer | outcome |
|---|---|
| Astra (`gpt-6-astra`) | complete |
| Daybreak Blue (`gpt-daybreak-blue-latest`) | complete |
| Opus (`claude-subscription/claude-opus-5-5`) | **unavailable** — `502`, "Opus 4.8's safeguards flagged this message" |

Opus is recorded as a capability limit, not worked around. Rewording to evade a vendor's cyber
safeguard would be the wrong move, and the finding stands without it.

## Where they agreed (treat as settled)

1. **Abandon root-password cracking.** Both, independently. Dropbear is `-s` (pubkey only) and the
   private key is absent (§6); engineer mode is already physically reachable and root (§5), so the
   Unix password buys nothing unless a password-authenticated consumer is first demonstrated.
2. **Abandon kernel/boot-image replacement.** §7 — ABL enforces IAS signatures; the wrong trust
   boundary.
3. **VM graphics work is not a prerequisite.** Both, explicitly. Neither home-screen rendering,
   navigation compositing, nor GL is needed for either recommended path. Astra: the recommended
   static work proceeds now; Daybreak Blue: the only VM state needed is a deterministic **headless
   service harness**.
4. **A two-stage chain beats demanding one bug do both jobs.** Both proposed the same alternative
   framing unprompted: `removable-media parser → unprivileged code execution → local
   /tmp/iAp2Socket → UID-0 service`. This matters because the VM **cannot** reproduce the USB gadget
   stack (`lge_usb_adapter` oopses in `sbi_apl_commit`), so any route requiring physical iAP2
   delivery is untestable here; a media-parser entry does not need it.
5. **Do not promote static flow to runtime reachability.** Both. A closed provenance slice retires a
   route; it does not open one.

## Where they disagreed (the useful part)

**Astra's single highest-value action:** trace the boot/rootfs update object from verification to its
final install-side open, including every intervening copy — a bounded, byte-anchored static
investigation. Rationale: §1 establishes path-based verification but **not** that externally
replaceable bytes reach installation, and that gap is the difference between a plausible entry route
and none. Cheapest resolution is a backward slice from the consumer's actual `open`, not an
assumption that `activeResourcePath` names the boot image. Verdict options are explicit:
exclusive on-unit copy ⇒ reject the swap; medium read after check ⇒ retain as structurally viable,
not demonstrated; any mount alias or runtime-dependent source ⇒ **UNKNOWN**.

**Daybreak Blue's single highest-value action:** convert the §4 corruption into a bounded
exploitability verdict — exact overwrite offset, length, attacker-controlled bytes, allocation
adjacency, repeatability — then a harmless control-flow proof (redirect to a noncanonical sentinel,
not a payload). Rationale: it is the only primitive **already demonstrated to corrupt memory at
runtime**, in a UID-0 process. A negative result is equally valuable: it retires the project's
strongest current primitive.

Both are defensible. They differ on whether the binding constraint is *provenance* or *primitive
quality*.

## Adopted plan

Ordered so that each step either closes an ambiguity or retires a hypothesis, and none depends on
the untestable gadget path.

**Step 1 — Astra's static provenance trace.** Fully within reach, needs no VM, answers the question
that decides whether the USB-swap technique exists for this build at all. Deliverable: for each of
the three privileged `%s` sinks (§2), a backward slice through object construction, USB enumeration,
XML/FOTA fields, and both guards, bound to instruction ranges; plus the boot/rootfs consumer's actual
`open` argument and every copy/rename between verify and use. Output: one of Astra's three verdicts.

**Step 2 — Daybreak Blue's `system()` oracle, if and only if step 1 leaves a candidate.** Stage an
otherwise genuine package whose relevant pathname carries an **inert marker**, and intercept
`system()` with the preload mechanism **already proven working this session** to record the command
without executing it. Observation of the marker at the sink proves runtime reachability with no
payload and no signature bypass. If the updater cannot be driven headless in the VM, the answer is
**UNKNOWN**, and a stable headless AppUpgrade invocation becomes the blocker — stated, not guessed.

**Step 3 — corruption geometry (cheap, parallel, instrument already proven).** A batch of
clean-reset replays recording allocation addresses, fault sites and frame counts, to establish
whether the §4 abort reproduces with identical geometry. Daybreak Blue is right that repeatability
is currently **UNKNOWN** and that this gates any exploitability claim.

**Step 4 — the two-stage framing, only after 1–3.** Re-derive the `id3.so` APIC arithmetic from our
own bytes (our plugin is a *different build* — `0665fe83…` vs upstream `0067c7e9…`, so the
public finding cannot be imported), and settle the admission question both reviewers raised:
**mode 0777 does not establish SMACK permission to connect**. Astra's phrasing is the precise one —
a benign connection test *in the relevant security context* is required, not a DAC-mode argument.

## What each reviewer said to stop doing

- Astra: stop re-running iAP2 to reconfirm the same abort; further work must explain the corrupting
  operation or attacker control, not produce an equivalent trace.
- Daybreak Blue: same conclusion from the other direction — the next iAP2 work must be a
  geometry/control characterisation, not another crash.
- Both: no more effort on `SrcFullPath` (already refuted for our build, §"Ambiguous").

## Bounds

Reviews only. No payload, no signature bypass, no flash, no device. Both reviewers were told the
constraints and both respected them; Daybreak Blue additionally noted that its recommended
control-flow proof is a sentinel redirect, not an exploit.
