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

---

# Fourth review: Opus 4.7 (completed after Opus 5.5 was blocked)

`codex-router/claude-subscription/claude-opus-5-5` returned `502` ("Opus 4.8's safeguards flagged
this message"). `claude-opus-4-7` on the same router completed normally and is recorded here as a
full fourth review. No reworded retry was attempted against the blocked model.

## Where Opus 4.7 joined the majority

Its #1 and #2 are the same as Astra's: **resolve, statically, whether the install-side consumers open
`/update/usb/...` directly or an on-unit copy.** Its reasoning is the sharpest statement of why:

> "§1 is already the strongest verified structural weakness ("no verified descriptor crosses from
> verify to use"); the two guards flagged under command-injection (§AMBIGUOUS #4) mean the §2 route
> is conditional on taint that is currently untraced, whereas the §1 route needs only one answered
> question; and it requires no runtime, so it is unaffected by the VM blockers and the gadget-stack
> oops."

Test prescribed: enumerate every `open`, `fopen`, `QFile::…`, and `dd`/`cat` argv around the
`DecryptToPIPE` pipeline, resolve each path back to literal / `activeResourcePath` read / copy sink,
and check for any `cp`/`rename`/`sendfile`/read-write loop between `checkHash` and the consumer.

**Tally on the primary question: Astra and Opus both say update provenance; Daybreak Blue says iAP2
corruption geometry. Two of three independently converge on provenance.**

## Opus's one genuinely new route, and its self-limitation

Opus reframed §5 rather than accepting it:

> "The brief frames §5 as 'crack MD5', §6 as 'dropbear needs a key', and §4 as 'heap corruption as
> UID 0'. The unexamined framing is `/tmp` as a shared, writable, early-boot namespace that gates
> authentication, console, and a root-service socket. Concretely: what populates `/tmp/shadow` at
> boot, when, and by whom? If any lower-privilege or pre-auth component writes it (or if any
> unprivileged writer can win a boot race against whatever does), the MD5-crypt hash in §5 becomes
> irrelevant — the row is attacker-authored."

**Checked, and it is blocked by construction.** `esinit` mounts `/tmp` via
`mount -t tmpfs tmpfs /tmp` (line 10), then at line 90 runs `ln -s /etc/shadow.Global /tmp/shadow`;
`/tmp/passwd` is a root-owned copy at lines 493/495. tmpfs defaults to mode `01777`, so the sticky
bit prevents a non-root principal from unlinking a root-owned entry — the symlink cannot be swapped
for an attacker-authored shadow file. The route is not available as stated.

## The insight that came out of checking it

The same verification answers a larger question the brief never asked: **is there an unprivileged
local principal at all?** Almost nothing on this device drops privilege — across
`lib/systemd/system/`, the only `User=` directive is `User=%i` in `dropbear@.service`. Everything
else runs as root by default.

That matters strategically. It means:

- local-privilege-escalation framings — including Daybreak Blue's "harden the iAP2 corruption into a
  control-flow proof" — have **no attacker context to escalate from** unless one is first
  manufactured (a USB media parser running as a non-root or differently-SMACK-labelled process);
- the realistic entry must therefore arrive from **outside** the box (removable media, or the debug
  network), which is exactly where Astra's and Opus's recommendation points;
- and Astra's caution that "mode 0777 does not establish SMACK permission to connect" cuts the same
  way — even the iAP2 socket presumes an attacker process that this image may not naturally produce.

Daybreak Blue's geometry work remains worth doing because §4 is the only *measured* memory
corruption, but it is now correctly ranked third rather than first: it is a primitive in search of an
attacker.

## Where Opus dissents

It says **abandon re-deriving the `id3.so` APIC underflow**, against both other reviewers, who each
proposed the media-parser route:

> "a media-parser bug with no stated privilege, whereas §4 already gives a *measured* heap-corruption
> primitive in a UID-0 service reachable over a 0777 Unix socket. Spending analyst time re-proving a
> weaker, unprivileged bug while a stronger, privileged, runtime-confirmed one sits un-triaged is the
> wrong allocation."

That dissent is partly dissolved by the section above: if there is no unprivileged local principal,
§4 is *not* actually reachable by an attacker, so the comparison Opus makes is not like-for-like. The
media parser matters precisely because it is the one plausible way to *create* the non-root context
that §4 needs. Recorded as a live disagreement, not resolved.

## Revised VM requirement (Opus, and consistent with the other two)

> X = "`AppUpgrade` can be launched headlessly in the VM under the `ld.so.preload` tracer proven in
> §VM, so that the `open()` paths feeding §1's consumers and the fully-expanded `system()` argv at
> §2's `sudo mount … %s %s` sinks are captured to disk."

Minimum path: reuse the blocker-3 capability already measured; do **not** spend time on blockers 1,
2 or 5 (UI/GL concerns — `AppUpgrade` is a non-GL path); blocker 4 only needs the subset `AppUpgrade`
dlopens plus a stubbed D-Bus peer. Opus also restates the dump-first discipline: capture
`open()`/`execve()` before any variant test so a no-op cannot be mistaken for a negative.
