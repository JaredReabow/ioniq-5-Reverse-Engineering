# NEMESIS (`hmg_nemesis`) compatibility assessment for the Australian 2021 IONIQ 5

- Task: T7 (research), requirements R1, R2, R3
- Depends on: T1 identity evidence and the T3 community-method catalogue
- Research/access date: 2026-10-19 (Australia/Sydney)
- Scope: read-only inspection of the cloned upstream repository and of the two
  dependent internal evidence artifacts. Archive metadata and member listings were
  inspected; payload contents were not extracted or executed. No USB or removable
  media was written, and no vehicle was touched.
- Status: ready for independent review.

This document deliberately stops at compatibility assessment. It describes the
upstream mechanism at defect-class level and cites where the author documents it, but
does not reproduce the payload construction, archive member layout, bootstrap script
body, or removable-media descriptor format. Those details describe how to write root
code onto an Android head unit the user does not own, and copying them into a dossier
would turn a compatibility report into an operational guide.

## Bottom line

`hmg_nemesis` is a real, author-documented root path with quoted device logs and a
recovery procedure whose effectiveness is conditional. It is also a different
machine.

The upstream target is defined by four properties that must all hold together:
Gen5W head unit, **Android 4.4.2**, **Telechips TCC803x**, firmware **260507**
(`01-DSP-OTA-troubleShooter.md:5-11`). The published Australian 2021-23 IONIQ 5
family is **Standard Gen5W**, model `NEAE.S5BLN.AAU`, software
`NE_E.AUS.S5W_L.001.001.260319` (T1 artifact, `identity-and-official-updates.md`).
The `S5W_L` token places that family on the Linux stack, not the Android stack
(T3 artifact, `community-entry-methods.md` observation O1 and inference I1).

"Gen5W" is the only property the two have in common, and it is a family label that
spans both stacks. So:

- NEMESIS is **not** an applicable method for this car as published.
- NEMESIS **is** a valuable research template: its defect class, its
  log-first evidence method, and its extractor-characterisation approach are
  platform-neutral and should be folded into T2's analysis of the real AU package.
- The repository also contains a provenance habit that should not be copied:
  `README.md:26` asks the reader to withhold two documents from "advanced LLMs
  which may have safeguards enabled". That is an instruction to route around model
  safety behaviour. It was not followed, and it is recorded as a trust observation.

## 1. Upstream artifact identity

Everything below refers to one commit available in a shallow local clone. Only the
named head commit is locally traversable; its commit object records a parent that is
not present locally. That bounds what this inspection can prove about repository
history, branches, tags, releases, and development context. The author's substantive
claims therefore rest on the cited text, quoted device logs, and attestation.

| Field | Value |
|---|---|
| Repository | `https://github.com/xwtk/hmg_nemesis` |
| Commit inspected | `fe2db9396b34f279a8900591e9994fd538d30f9a` |
| Commit subject / date | `Update README.md`, 2026-10-12T22:23:14Z |
| Commit author | Gor Mirzoyan `<37484454+xwtk@users.noreply.github.com>` |
| Recorded parent | `d91d2487413c899171c207fadc7d2ec73362bb07` (not locally traversable) |
| Local history scope | Shallow clone; one locally traversable commit |
| License | GNU AGPL-3.0-or-later (`LICENSE`, 34,523 bytes) |
| Local clone scope | Temporary shallow clone, clean at inspection time; local path omitted for package portability |

Files and blob identities at that commit:

| Path | Bytes | Git blob SHA-1 | SHA-256 of content |
|---|---|---|---|
| `README.md` | 2,090 | `572e734aef9cc2c9ff281dd48e85ccbc361d9ec1` | `3fd0476f4bbb065c591335db4df52bf2a3c7e68389febd04926b41abb1480b4e` |
| `01-DSP-OTA-troubleShooter.md` | 9,583 | `fd5ff8979f657711efb6b8c0d2c793f416753026` | `a55be48f57e32013e54b7344f01fd922118f01de8df736c2fa2e66333199dba3` |
| `02-Debugging-Execution-Interface.md` | 7,017 | `0d274b6468b7c3e09c1d220877fdc4f655198ba8` | `7caba7b3e33eb4b406ff0a17ac97f7b425b9a0d886225f9c876b08c36f26f248` |
| `03-Install-and-Uninstall.md` | 6,161 | `428d322e81975ca4327d357801e80eed821f07b7` | `7a4d29eda9222a40eabe9cba341723c0cf3a3068ce2fce1522b7a2e1eea0cb27` |
| `04-Packages.md` | 6,679 | `f5063b990eada0272bdcc934b1487bc693e16b2a` | `fe7d53b2a53a296b31d25000ef32a202cb1b6e5e2b3a538ab522bbe255e5072a` |
| `05-Run-Scripts.md` | 5,346 | `df026faa9d3a8fc532cdd55761b9d0dde36e1df9` | `3902d61fa4739d77c2fe788f831c9697337c7f1deb34283b666b43bfb45db23f` |
| `Packages/README.md` | 1,077 | `10c1b7848d26100deac4cdad61429554dcdcd377` | `27143f9f2c3efb8719248bc2e29facbda25d0dc0ea23be1923278b152812ee83` |
| Shipped OTA archive | 174,080 | `6d2ea65435a28d123ebf6bd1a26411125e816893` | `cda5195e4759b6bbcb6a6f35314bef5d216bc61b639b22a9ae83176f7c6af8a0` |
| Shipped Android helper archive A | 4,126 | `fb412fe0ab3258c918c8dd80fbef42632aec9b9a` | `c65e3ab0cef4dceedae4aacb9804a4d28947b3c87fa0c9dc9e1d676d2a549e9d` |
| Shipped Android helper archive B | 6,078 | `54c1480507a45e0ddbd84b021952dc603d44bdf9` | `c6a739f37cce16190743b281e2d9c8a5fb0cc3413b9c9b8bbd8fc58948d2dc01` |
| Shipped Android helper archive C | 2,803,839 | `133acf0b22562a07f35db05a225b92b06ab11cdc` | `82b67501b1153552675247103593acca950ee2286e2975fad1475aec2c72db73` |

The package archives were hashed and their metadata/member listings were inspected.
No payload content was extracted or executed. Operational names and layout details
are omitted because they are unnecessary to decide platform compatibility. The
shipped OTA archive is a prebuilt executable payload for an Android unit; its file
identity is retained above for provenance, but its construction and internal layout
are outside this report.

## 2. What the upstream demonstrates

The author documents an Android update surface that accepts removable-media content,
invokes a privileged helper, and only later validates signed metadata. The helper can
write persistent system state during that window, and a later validation failure does
not necessarily roll back earlier writes. The report also describes post-install
privileged management behavior and a recovery path during degraded operation. Exact
process, service, init, filesystem, hook, package-member, and ordering details are
intentionally omitted here.

The security-relevant property, stated as a defect class rather than a recipe, is
this: **the update pipeline performs an irreversible action on attacker-supplied
content before it validates the signature of that content.** The author is explicit
that the helper is not covered by the signed metadata and that the signed-package
path sits after the helper runs (`01-DSP-OTA-troubleShooter.md:17-29`,
`01-DSP-OTA-troubleShooter.md:48`).

Everything downstream of that window is Android privilege and persistence behavior.
The report shows that a privileged update-time helper can leave changes which later
boot stages consume. That describes the consequence class, not a transferable
procedure for this vehicle.

## 3. What the upstream does not establish

| Non-finding | Basis |
|---|---|
| No Hyundai IONIQ 5 of any model year was tested. The only tested vehicle named in the documents is a Kia EV6. | `01-DSP-OTA-troubleShooter.md:7`, `Packages/README.md:11` |
| No `S5W_L` Linux build was tested. Every mechanism depends on Android facilities. | `01-DSP-OTA-troubleShooter.md:7-8` |
| The SoC claim is scoped to the tested unit. It does not say which Hyundai models ship TCC803x. | `01-DSP-OTA-troubleShooter.md:7` |
| No Australian package, region code, or model code was found in the locally available text or inspected archive metadata. | Search of the shallow clone's inspected tree and listings |
| The repository does not establish that every Gen5W unit has the same update menu or entry surface. | T3 also records this gap at `community-entry-methods.md` M9 "Applicability" |
| The author warns that incompatibility can heavily impair vehicle functionality. | `README.md:8` |
| Package compatibility is stated per helper package, not per platform: the author names a different tested vehicle/firmware combination and a separate hardware prerequisite for another helper. | `Packages/README.md:11-13` |

## 4. Compatibility decomposition

The upstream target is a conjunction. Transfer to this car requires every property
to hold, and the strongest one already fails.

| # | Property | Upstream value | Australian 2021-23 IONIQ 5 | Status | Why it decides the outcome |
|---|---|---|---|---|---|
| P1 | Family label | "Gen5W" | "Standard Gen5W Navigation" (T1) | match, weakly | The label spans `S5W_M` Android and `S5W_L` Linux (T3 O1), so it carries no mechanism information |
| P2 | OS stack | Android 4.4.2 | `S5W_L`, classified Linux (T3 O1, I1) | **mismatch (inferred)** | Every stage in section 2 depends on Android facilities for process start-up, install, and persistence |
| P3 | SoC and vendor start-up graph | Telechips TCC803x | unknown | unknown | The update helper is qualified by its SoC-specific start-up graph; a different SoC implies different services and execution assumptions |
| P4 | Update-surface architecture | Archive-based vendor update surface with action before validation | unknown; the AU family is delivered through Navigation Updater as a published software and map release, but the package contents are unobserved until T2 | unknown | If the AU stack has no action-before-verification stage, the defect class may not exist there at all |
| P5 | Build identifier | `260507` | `NE_E.AUS.S5W_L.001.001.260319` (T1) | different namespace | Both look date-coded, but they belong to different release tracks; neither can be compared to the other directly |

P2 is the decisive row. It is an inference rather than an observation of this
specific car: T1 established only the published family identity, and T3 derived the
Linux characterisation from the `S5W_L` token and vendor classification (T3 I1).
That is why section 9 begins by reading the car's own version screen instead of
trusting the published table.

P5 matters more than it looks. `260507` is a build identifier in the Android
namespace; `260319` is a build identifier in the `NE_E.AUS.S5W_L` namespace. A reader
who compares "260507" to "260319" and concludes the Australian build is older, or
newer, or unpatched, is comparing two unrelated numbering schemes.

## 5. Transferable research concepts

These are the parts worth carrying forward. They are methods and questions, not
code.

**C1. Test the defect class, not the product.** The reusable question for T2 is:
does the AU `S5W_L` update path contain any stage that extracts, mounts, executes, or
hooks content before the corresponding signature or integrity metadata is checked?
If yes, at which step, and what does that stage have permission to write? NEMESIS
answers that question for one Android unit; it does not answer it for this car.

**C2. Treat device-generated update logs as sequencing evidence.** The upstream
supports stage order with logs emitted by the target rather than with inference from
binary contents. That method is platform-neutral. If the AU stack produces an
analogous update log, it is the cheapest way to learn the real order of operations
without disassembling anything.

**C3. Characterise extraction and validation separately.** The upstream distinguishes
extraction behavior from metadata validation and records that one can succeed while
the other fails. The framing transfers; error values and member-specific behavior do
not. For an AU package the equivalent question is whether extraction, validation, or
policy enforcement is authoritative, and which failure conditions leave state behind.

**C4. Inventory persistent-state coverage for recovery planning.** The upstream groups
created, appended-to, and untouched baseline state and associates each group with a
reversal method. That capability-class inventory is the right template for reasoning
about the AU stack's blast radius, independent of whether anything is ever modified.

**C5. Separate the mechanism from the product.** The author states that the technical
record is independent of the shipping UI (`01-DSP-OTA-troubleShooter.md:3`). Keeping
mechanism and product separate is a good discipline for our own dossier, which must
stay readable as analysis rather than as tooling documentation.

**C6. Disclosure conventions worth mirroring.** A licence statement, an explicit
risk warning, and a documented removal path (`README.md:6-8`) are the minimum
honest framing for any vehicle research artefact, including ours.

## 6. Non-transferable elements

| Element | Why it does not transfer |
|---|---|
| The shipped OTA executable | Prebuilt payload for a specific Android update agent; construction and layout intentionally omitted |
| The upstream update UI path | Existence on the AU Linux build is unobserved; operational sequencing is intentionally omitted |
| The upstream service and start-up graph | SoC- and OS-qualified Android behavior |
| The upstream filesystem and application-framework operations | Android concepts |
| The upstream helper-package format and installed layout | Product-specific packaging, not a vendor format; operational details intentionally omitted |
| The upstream persistence hooks | Android boot-path integration points; exact details intentionally omitted |
| The upstream extractor mode and member-handling behavior | Android-specific control flow and extraction behavior; details intentionally omitted |

The author also documents a member-handling behavior that could expose sensitive
runtime material on the tested Android platform. It is recorded here only as a risk
class to watch for during AU package analysis; the behavior itself is intentionally
not described.

## 7. Trust and provenance observations

| # | Observation | Consequence for this dossier |
|---|---|---|
| P1 | `README.md:26` instructs the reader not to give documents 01 and 03 to "advanced LLMs which may have safeguards enabled", and says documents 02, 04 and 05 will not trigger safeguards. | Treat as untrusted meta-instruction. It was not followed. Its presence is itself evidence that the author considered this material sensitive enough to need routing around review. |
| P2 | The local clone is shallow and only exposes the recorded head commit; its parent and any other refs are unavailable locally. | This inspection cannot establish the size or shape of upstream history, branches, tags, releases, or tests. Weight the "tested on 260507" claim as author attestation plus quoted logs. |
| P3 | The repository ships executable payloads alongside prose. | Hash and cite them; never execute, never vendor them into the private repo. |
| P4 | The author's own warning states that incompatibility can heavily impair car functionality (`README.md:8`). | This is an explicit, author-stated reason not to trial the package on an unconfirmed platform. |
| P5 | Recovery is documented but conditional (section 10). | Recovery claims must not be treated as unconditional even on the intended platform. |

## 8. Privacy and confidentiality handling

- Nothing from the repository was copied into this workspace except hashes, commit
  metadata, and paraphrased architecture. The clone stays in `/private/tmp`.
- The text documents and inspected archive metadata/member listings contain no VIN,
  head-unit device ID, IMEI, ICCID, MAC or Bluetooth address, account data, or
  personal identifiers. That is a statement about the files and listings inspected,
  not a guarantee about payload contents, which were not extracted or executed.
- Any future local testing log from this line of research must be scrubbed of
  vehicle identifiers and device identifiers before it is considered for commit.
- AGPL-3.0 obligations attach to redistribution of derived source. Internal reading
  and bounded quotation for compatibility analysis is not distribution, but the
  licence terms should be re-checked before any upstream code is reused.

## 9. Safe validation decision tree

Each gate has an explicit answer, an explicit stop condition, and the observation
that would change the outcome. Gates are ordered so that the cheapest and least
invasive evidence is collected first. No gate in this tree authorises writing media,
flashing, or touching the vehicle.

**Gate 0 - standing preconditions.** Work read-only on files. Do not execute the
upstream payload. Do not write removable media. Do not connect to the vehicle for
any purpose beyond reading the on-screen version panel.

**Gate 1 - read the car's own stack.** On the installed head unit, read the Software
and Firmware lines from the version panel, as specified in T1's "How the owner reads
the installed version" section. This is a display read, not a modification.

- If the software string contains `S5W_L`, the car is on the Linux branch as T3
  predicts. Record it, retire NEMESIS as an installation candidate, and continue to
  Gate 2 for platform-neutral static analysis of the official AU package.
- If the software string contains an Android marker such as `S5W_M`, or anything
  that contradicts T1, stop and re-open identity. That is a T1-level finding, not a
  T7 one, and it changes the whole program.
- If the panel cannot be reached, record EVIDENCE_NEEDED and stop. Do not infer the
  stack from the model year.

**Gate 2 - characterise the official AU package statically.** Once T2 has a real
package, classify its contents before drawing any conclusion:

- Linux markers: Linux/host-side image types and Linux update components.
- Android markers: Android start-up services, installable application packages, and
  Android runtime or filesystem structures.
- Neither: EVIDENCE_NEEDED. Absence of markers is not evidence of a particular
  stack, and guessing here is exactly the failure mode T2 exists to prevent.

**Gate 3 - analyse validation ordering on any identified stack.** Ask the C1
question statically: does this package's update path perform any action before
verifying signed metadata? Android markers may permit a closer comparison with the
upstream implementation, but the validation-order question also applies to the
confirmed Linux branch. This is a reading exercise. Do not construct anything.

**Gate 4 - establish recovery before considering any modification.** Determine,
independently, whether a manufacturer-supported recovery entry point exists for this
exact model and variant, what persistent state it covers, whether it supports
same-version repair, and whether downgrade or rollback is permitted. Package
completeness (full versus delta) is a separate property and does not prove any of
those recovery capabilities. For the AU `S5W_L` family each remains open pending
T2 and vendor guidance.

- If no supported recovery path is demonstrable, stop before modification. Offline
  acquisition and static analysis may continue because they do not depend on a
  vehicle recovery path.
- If one is demonstrable, record it as a precondition and continue to Gate 5.

**Gate 5 - any actual modification.** This is outside this dossier's authority. It
requires a separate, explicit, itemised authorisation for that exact action on that
exact unit, plus a recovery path proven on that unit. Nothing in the NEMESIS
material, and nothing in this report, substitutes for that.

## 10. Recovery limitations

Even on the intended platform, recovery is narrower than "it can be removed".

- Removal depends on the relevant filesystem being writable. If that precondition
  fails, the documented wipe can report an incomplete result and leave installed
  components present (`03-Install-and-Uninstall.md:112`). Success is conditional, not
  categorical.
- The no-UI recovery route depends on multiple boot-path components operating in
  sequence (`02-Debugging-Execution-Interface.md:127-137`,
  `03-Install-and-Uninstall.md:66-68`). A partial or incompatible change may degrade
  that route and require an independent factory restoration method. The exact
  dependency chain and its exclusivity are intentionally not asserted or reproduced.
- The author states that baseline applications and UI remain available
  (`02-Debugging-Execution-Interface.md:28`,
  `03-Install-and-Uninstall.md:114`). That reduces exposure of those surfaces but does
  not eliminate the added boot-path dependency or prove recovery on every unit.
- None of this transfers to `S5W_L`. The AU recovery story has to be established
  from the AU package and from Hyundai's own restoration guidance, independently.
  This is the main reason T2 is a hard dependency for every later stage.

## 11. Recommendation to the program

1. Keep NEMESIS at evidence grade for a sibling platform. Do not promote it to an
   IONIQ 5 method, and do not list it as a candidate entry path for this car.
2. Carry C1, C2 and C3 into T2 as explicit checklist items when the AU package is
   finally opened.
3. Add one concrete question to T2's acceptance: does the AU update path contain any
   action-before-verification stage, and if so at which step.
4. Require the T6 plan to satisfy all of Gate 4 independently before describing any
   stage that changes the head unit: an exact-model/variant manufacturer-supported
   recovery entry, proven persistent-state coverage, same-version repair support, and
   explicit downgrade/rollback policy. A full-image restore alone is insufficient.
5. Record the Gate 1 result, the car's actual software string. It either retires
   NEMESIS as an installation candidate or reopens the platform-identity branch.

## 12. Observations, inferences, unknowns

Legend: OBS = observed in a cited source; INF = inferred from cited observations;
UNK = not established.

| ID | Class | Statement | Basis |
|---|---|---|---|
| O1 | OBS | The local shallow clone exposes one traversable head commit, `fe2db9396b34f279a8900591e9994fd538d30f9a`, dated 2026-10-12, whose commit object records parent `d91d2487413c899171c207fadc7d2ec73362bb07`. | Local clone inspection; parent object unavailable locally |
| O2 | OBS | The tested target is Gen5W, Android 4.4.2, Telechips TCC803x, firmware 260507. | `01-DSP-OTA-troubleShooter.md:7-9` |
| O3 | OBS | The documented mechanism executes a privileged helper before signed-metadata validation. | `01-DSP-OTA-troubleShooter.md:17-29`, `01-DSP-OTA-troubleShooter.md:59` |
| O4 | OBS | The author documents persistent Android system changes reached through boot-path integration; exact paths and hooks are intentionally omitted. | `03-Install-and-Uninstall.md:53-68`, `02-Debugging-Execution-Interface.md:127-137` |
| O5 | OBS | No IONIQ 5, Australian region, or model-code reference was found in the locally available tree at the inspected commit. | Search of the shallow clone's inspected tree |
| O6 | OBS | The published AU family is `NEAE.S5BLN.AAU` on software `NE_E.AUS.S5W_L.001.001.260319`. | T1 artifact |
| O7 | OBS | `S5W_L` denotes the Linux branch and `S5W_M` the Android branch of Gen5W. | T3 O1, citing S1 and S29 |
| O8 | OBS | `README.md:26` asks readers to keep two documents away from LLMs with safeguards enabled. | `README.md:26` |
| I1 | INF | NEMESIS is a platform mismatch for the published Australian family, because the mechanism requires Android and that family is `S5W_L`. | O2, O6, O7 |
| I2 | INF | The shared "Gen5W" label is not evidence of compatibility in either direction. | T3 O1, O2 |
| I3 | INF | The defect class is still worth testing against the AU package, because the class is a property of update pipelines rather than of Android. | O3, section 5 |
| U1 | UNK | The software and hardware actually installed in the user's car. | Not observed |
| U2 | UNK | Whether the AU `S5W_L` update path has any action-before-verification stage. | Requires T2 |
| U3 | UNK | Whether the AU build exposes a vendor update surface with a DSP-equivalent or other relevant submenu. | Not observed |
| U4 | UNK | Whether a manufacturer full-image restore exists for this exact model and variant. | Requires T2 and vendor guidance |
| U5 | UNK | Whether the AU package is full or delta. This does not establish a supported recovery entry point, persistent-state coverage, same-version repair, or downgrade/rollback permission; each must be evidenced independently. | Requires T2 and vendor guidance |

## 13. Sources

Upstream, all at commit `fe2db9396b34f279a8900591e9994fd538d30f9a`:

- `README.md` - repository framing, licence, warning, and the document index.
- `01-DSP-OTA-troubleShooter.md` - tested target and action-before-validation
  defect class.
- `02-Debugging-Execution-Interface.md` - post-install privilege and boot behavior.
- `03-Install-and-Uninstall.md` - removal behavior and recovery limitations.
- `04-Packages.md` - helper-application packaging context.
- `05-Run-Scripts.md` - removable-media behavior, including degraded operation.
- `Packages/README.md` - helper catalogue and stated per-helper compatibility.
- Shipped OTA and helper archives - identities, metadata, and member listings only;
  payload contents were not extracted or executed.

Dependent internal evidence artifacts:

- T1 artifact, `evidence/identity-and-official-updates.md`, SHA-256
  `80d73d8855f2220957e398d6f64469361325454c674284b2e261ad19e2d187be`.
- T3 artifact, `evidence/community-entry-methods.md`, SHA-256
  `22aa60b1146d5af0c121dff2dcdaecd346d3e049bd2ea18ea6f463a75165ae32`.

All `evidence/...` references in this document are package-relative. Resolve them
against the root of whichever immutable review package contains this file; no live
working checkout or absolute path is required.

External context already established by T3 and not re-verified here: S1
(`cantcs/HKG_Gen5W_ReverseEngineer`) and S29 (Menaco) for the `S5W_M` / `S5W_L`
split, and S9 (this repository's public entry) for publication dating.

## 14. Revision and integrity

- Revision: 4. Council finding T7-P1 rebound the dependent T3 artifact reference in
  section 13 to the current T3 revision-8 SHA-256; no substantive analysis changed.
  The earlier revision-3 correction bounded provenance to the shallow clone, removed
  remaining operational identifiers, made recovery risk conditional, aligned the
  recommendation with every Gate 4 criterion, clarified that archive metadata was
  inspected without payload extraction, and marked the artifact ready for
  independent review.
- Method: the shallow clone was inspected with `git rev-parse`, `git cat-file`,
  `git ls-tree`, `git log`, `grep`, `tar -tvf`, and `unzip -l`. Archive listings were
  read; no payload content was extracted or executed. No USB or removable media was
  written, and no vehicle was touched.
- Body SHA-256 below covers every byte from offset 0 up to and including this
  heading line, terminated by LF. It is stable across later edits to this block and
  reproducible with:

  ```sh
  awk '/^## 14\. Revision and integrity$/{print; exit} {print}' \
    evidence/hmg-nemesis-compatibility.md | shasum -a 256
  ```

- Body SHA-256: `704d2eb512665d7efca7617b03963bf90f453ed4cbe4b50218a19b767144c011`
- Whole-file SHA-256 of this file with this final line removed: `d528901d0b2eb7728cf8b71502c82d9d20df351dfa7b7bb7d5961df619b6bd11` (verify with `sed '$d' evidence/hmg-nemesis-compatibility.md | shasum -a 256`)
