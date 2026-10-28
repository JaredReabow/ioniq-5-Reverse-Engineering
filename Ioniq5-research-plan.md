# IONIQ 5 (NE1) confidential reverse-engineering plan

Status: T6 Australian baseline plus active UK-origin/European addendum.
Revision: 3, 2026-10-19.
Vehicle: UK-origin 2021 Hyundai IONIQ 5, NE platform, Daybreak Blue; Australian
package retained as region-transition comparison evidence.
Confidentiality: private research. Do not publish, redistribute, or send to a
third party.

This plan integrates the accepted T1-T5 and T7 research with the newly accepted
T2 official-package analysis. It is a research and evidence plan. It documents
system architecture, interfaces, evidence, risks, and the conditions under which
later work could be considered. It does not contain operational instructions for
vehicle entry, immobilizer or keyless-entry defeat, credential replay, safety
control disablement, USB media writing, firmware flashing, or vehicle actuation.

The original T1-T7/T6 body below is preserved as the accepted Australian
comparison baseline. The active vehicle was subsequently corrected to a
UK-origin 2021 car. Its vehicle-family-correct official package is European
`NE_E.EUR.S5W_L.001.001.260128`. Current exact-build evidence is recorded in:

- `evidence/eu-package-acquisition.md`;
- `evidence/eu-kernel-decompilation.md`;
- `evidence/eu-root-sideload-applicability.md`; and
- `evidence/eu-aus-transition.md`; and
- `evidence/eu-custom-firmware-feasibility.md`.

Those addenda supersede Australian-market assumptions when selecting firmware
for this car. They do not retroactively rewrite the provenance or decisions of
the accepted Australian comparison work.

## European completion addendum

This addendum is the controlling integration for the active UK-origin vehicle.
The Australian material in sections 1–15 remains a frozen comparison baseline;
where it describes the active car as Australian, an incomplete European
download, or T1–T7 as the complete dependency set, this addendum supersedes it.

### Accepted European artifacts

| Artifact | Task | Accepted finding | SHA-256 |
|---|---|---|---|
| `evidence/eu-package-acquisition.md` | T8 | Correct EU `260128` package; 35/35 sizes and CRC-32 values, three MD5 sidecars, complete inventory | `18fbd20de3da75349f4adde245989c3441c67b4ca0af81d148e8cb047889e7b9` |
| `evidence/eu-kernel-decompilation.md` | T9 | x86-64 Linux 4.1.27, 64,923 symbols, reproducible Ghidra 12.1.4 trust/hardening analysis | `54ee1d5e77dafedf0b9444410db6f60656d9114b7c86fa98765f023a6885f7bc` |
| `evidence/eu-root-sideload-applicability.md` | T10 | Published-method applicability; no demonstrated exact-build stock-to-root path | `05d96384b639401ddae066fcb562c759ed8be0e5a6f0c0069297efedbaff94d8` |
| `evidence/eu-custom-firmware-feasibility.md` | T10 | Defensive five-layer feasibility and audit-surface analysis | `954ab62b5533410c7ab9b0984f4fff622f0e8e2bf31bccc2b0379f86b39c8a88` |
| `evidence/eu-aus-transition.md` | T11 | Complete region-transition feasibility decision | `3e1e90266ea84b8991fdbf8be93054825730d4668eb1cac7048b113b4adecc8c` |
| `evidence/eu-package-metadata/eu-aus-comparison.json` | T11 | Durable 32-row common-path hash matrix plus four region-only paths per package | `023d32723e30316e20ade461ba88fa5fdc44dc57b5c2682a5eff99f18472bf96` |

T8–T11 were independently reviewed and accepted on 2026-10-19 after the
reviewer required and verified reproducible scripts, corrected completed-
manifest identity, published-source bindings, plaintext-rootfs wording and a
durable full EU/AUS matrix. T6 now depends on T1–T5 and T7–T11.

### R12–R16 traceability

| Requirement | Accepted evidence | Integrated decision |
|---|---|---|
| R12: correct UK-origin vehicle scope and official European package | T8 | The vehicle-family-correct source is `NE_E.EUR.S5W_L.001.001.260128`, model code `101489`; the Australian package is comparison-only. |
| R13: exact European OS, kernel, CPU, hardening and trust model | T9 | ELF64 x86-64 Linux `4.1.27-abl`, systemd/ext4, SMACK, and kernel OEM-signature/keystore paths are exact-build observations. |
| R14: published root and native application-loading applicability | T10 | Native Linux/Qt/systemd deployment is plausible only after privileged execution; no inspected source establishes a complete stock-to-root chain on `260128`. |
| R15: safe EU/AUS transition feasibility | T11 | Of 32 common paths, 6 are identical, 19 equal-size but byte-different, and 7 differ in size and bytes; cross-region installation is not established as safe. |
| R16: preserve Kona work | Git-scope harness and repository status | Ioniq integration owns only `Ioniq5-*`, `evidence/eu-*`, its ledger records, tests/tools and explicit review artifacts; `kona_research/**` and root history/changelog remain unstaged. |

### Completed-package and feasibility status

The EU package is complete: every manifest payload matches its declared size
and signed CRC-32, the map and both voice archives match their sidecars, and
the sorted 36-file SHA-256 inventory digest is
`f06752ea7cbf296ef7d7d7482f5ba96a3349161fc7ad0d60b36b042f62ef5b51`.
The encrypted rootfs, AppNavi, GUI and policy envelopes are present but their
plaintext contents remain unavailable; availability of the envelope is not
equivalent to access to its service, SMACK or application metadata.

Custom application feasibility has five independently relevant layers:
payload-envelope handling, userland update/version/region policy, kernel OEM
signature verification, bootloader/container acceptance, and runtime
systemd/UID/capability/SMACK policy. Current evidence does not establish that
modifying one component satisfies the other layers. Research therefore remains
static and defensive: function-level comparison, legitimate plaintext recovery,
offline parser/policy harnesses, and a benign native prototype for an isolated
replica. It does not authorize or supply a zero-day, signing bypass, crafted
update, privileged payload, flashable modified image, or live vehicle procedure.

EU-to-AUS conversion is a separate problem from privileged application access.
Combining them would multiply uncertainty across modem/carrier/eCall,
telematics, navigation licensing, region coding, boot policy and recovery.
Neither proceeds to vehicle use without the existing Gate 4 recovery evidence
and isolated bench validation.

---

## 0. Scope, authority, and reading rules

The owner has authorised confidential reverse-engineering research on this
vehicle. That authority covers reading, documenting, and analysing the owner's
own property and the official software published for it. It does not silently
extend to actions that change vehicle state, create intrusion capability, or
weaken a safety function. Those actions require a separate, itemised decision
based on evidence, not merely the existence of a research goal.

Three rules apply throughout:

1. Evidence before method. No method is treated as applicable to this car until
   the installed software and hardware are observed and the method's
   preconditions are met.
2. Read-only before state-changing. Every phase begins with the least invasive
   evidence that can answer the question.
3. Unknown is a result. An unresolved question is recorded as unknown, never
   filled in by inference from a sibling market or platform.

Absolute local filesystem paths, account names, vehicle identifiers, and
personal data are deliberately omitted from this document. The raw package,
captures, dumps, extracted research trees, and vehicle-specific evidence may be
retained in the private repository after deliberate staging review; see section 10.

---

## 1. Frozen evidence baseline and hash bindings

This plan is bound to the following accepted artifacts. Hashes are SHA-256 of
the complete files at the time of T6 integration. The integrated harness
re-verifies them; if any accepted artifact changes, this plan must be revised
and re-reviewed rather than silently inheriting a new meaning.

| ID | Task | State | Path | SHA-256 |
|---|---|---|---|---|
| ART-T1 | T1 | accepted | `evidence/identity-and-official-updates.md` | `80d73d8855f2220957e398d6f64469361325454c674284b2e261ad19e2d187be` |
| ART-T2 | T2 | accepted | `evidence/official-package-static.md` | `4b02a0799a4d74b934d4c0ea36f6e8d64027e942cc60b94096418e7243435b94` |
| ART-T2-INVENTORY | T2 | accepted | `evidence/package-metadata/official-package-inventory.txt` | `79fd056f9c4daaa32f77d369b22220de2a0dba52d9b0fbe82d0e36955342b361` |
| ART-T2-META | T2 | accepted | `evidence/package-metadata/official-metadata-inventory.txt` | `c9eca4949934249b59ff093d8da1dba47cee2cd284ed4834c9856e435827d089` |
| ART-T2-INSTALLER | T2 | accepted | `evidence/package-metadata/installer-identity.txt` | `914a88c97e556af8d2329bfd6b04a4fb705485dd94de2f02feddb82fd9b13719` |
| ART-T3 | T3 | accepted | `evidence/community-entry-methods.md` | `22aa60b1146d5af0c121dff2dcdaecd346d3e049bd2ea18ea6f463a75165ae32` |
| ART-T4 | T4 | accepted | `evidence/passive-runtime-and-hardware.md` | `5766622656779b84cc190638eb5344db0d11c0ab2495b3ae208ece3c1689e00f` |
| ART-T5 | T5 | accepted | `evidence/vehicle-network-boundaries.md` | `1b789bfef4c9c1b4e7ed65bfb6c9f3dfc615bb37b9f0fb9abf312b459f3b6861` |
| ART-T7 | T7 | accepted | `evidence/hmg-nemesis-compatibility.md` | `87295ef408c539a7d45cef43449947397cf3c124db2874ed4bfe2c74a37212a1` |

T6's dependency edges are T1, T2, T3, T4, T5, and T7, as recorded in the
ledger. This integration is valid only while each dependency remains in the
accepted state at the hash shown above.

Acceptance records that matter to this integration:

- T2 was accepted by an independent `gpt-6-sol` review on 2026-10-19 after the
  reviewer reproduced the 36-file inventory, the sorted-tree digest, all 35
  manifest size and CRC records, both front-key CRC-32/MPEG-2 values, the three
  MD5 values, and the ZIP/gzip format checks.
- T7 was accepted on 2026-10-19 after one provenance-only correction. Its
  review records that ASTRA-G5-02 is satisfied within T7 scope by Gate 4 and
  recommendation 4, with the T6 handoff left open.
- T3, T4, and T5 were accepted by Council generation 10 against frozen review
  batch 8 (section 12).

Key claim anchors in the frozen artifacts:

| Claim area | Anchor |
|---|---|
| Published Australian identity | `evidence/identity-and-official-updates.md:10-43` |
| Owner-visible version readback | `evidence/identity-and-official-updates.md:67-90` |
| Updater compatibility and no-revert statement | `evidence/identity-and-official-updates.md:91-116` |
| Package acquisition and updater flow | `evidence/official-package-static.md:48-99` |
| Exact descriptor and manifest verification | `evidence/official-package-static.md:100-134` |
| Front-key checksum family | `evidence/official-package-static.md:135-157` |
| Map, voice, and IPK containers | `evidence/official-package-static.md:158-261` |
| Opaque envelopes | `evidence/official-package-static.md:262-305` |
| Package trust limits | `evidence/official-package-static.md:306-328` |
| Package observed/inferred/unknown register | `evidence/official-package-static.md:329-371` |
| Package handling boundary | `evidence/official-package-static.md:447-457` |
| Method matrix | `evidence/community-entry-methods.md:87-107` |
| AU applicability and unknowns | `evidence/community-entry-methods.md:576-629` |
| Unresolved method issues | `evidence/community-entry-methods.md:706-732` |
| Route matrix with restoration and risk columns | `evidence/passive-runtime-and-hardware.md:91-113` |
| Staged plan and stop conditions | `evidence/passive-runtime-and-hardware.md:859-954` |
| Redaction and confidentiality rules | `evidence/passive-runtime-and-hardware.md:1028-1084` |
| Trust zones | `evidence/vehicle-network-boundaries.md:95-188` |
| Subsystem register | `evidence/vehicle-network-boundaries.md:189-209` |
| Network domains | `evidence/vehicle-network-boundaries.md:405-416` |
| Vulnerability and trust implications | `evidence/vehicle-network-boundaries.md:417-468` |
| NEMESIS compatibility conclusion | `evidence/hmg-nemesis-compatibility.md:19-43` |
| Compatibility decomposition | `evidence/hmg-nemesis-compatibility.md:121-143` |
| Gate 4 decision tree | `evidence/hmg-nemesis-compatibility.md:223-279` |
| Recovery limitations | `evidence/hmg-nemesis-compatibility.md:280-300` |
| Recommendation to the programme | `evidence/hmg-nemesis-compatibility.md:301-315` |

Task states in `research-ledger.json` are the coordination record. This plan
does not rewrite them; T6 state transitions and any ledger mutation remain
coordinator-owned.

---

## 2. Requirement traceability

Every requirement in the ledger is traced to accepted evidence and to where
this plan discharges it.

| Req | Requirement | Accepted evidence | How this plan discharges it | Residual limit |
|---|---|---|---|---|
| R1 | Exact infotainment family and region-specific firmware likely fitted to a 2021 Australian IONIQ 5 | T1 identity table; T2 exact package descriptor | Section 3 separates the published Australian identity from the unread installed build and records the exact official package | Installed software and hardware revision are not yet observed on the car |
| R2 | Catalog distinct reverse-engineering paths with evidence, prerequisites, reversibility, risks, and applicability | T3 method matrix M1-M14; T4 route matrix; T7 compatibility decomposition | Section 5 condenses the catalogue; section 6 carries risk and unknown columns; section 8 orders the routes | Most recovery claims remain author statements; none is proven on this car |
| R3 | Practical staged plan beginning with passive and recoverable evidence acquisition | T4 staged plan and stop conditions | Section 8 defines Phases 0-8 with exit criteria, each starting passive | Later phases are gated and optional, not scheduled work |
| R4 | Architectural relevance of immobilizer, keyless entry, gateways, CAN, diagnostics, and safety controllers without operational bypass instructions | T5 subsystem register, trust zones, and vulnerability implications | Section 6 covers every named subsystem at architecture level; section 7 records trust boundaries | Gateway filter policy, key crypto, and ASIL allocation are not public |
| R5 | Parallelism workflow with independent workers and separate reviewer acceptance | `research-ledger.json`; Council generation 10 | Section 12 records the acceptance structure and the frozen package | This artifact is reviewed separately from the research workers |
| R6 | History and changelog plus local Git version history | Git configuration; this revision | `Ioniq5-HISTORY.md` and `Ioniq5-CHANGELOG.md` are dedicated Ioniq documents; section 10 defines Git scope | Commit and push are the coordinator's A-T6-2 action |
| R7 | Treat every vehicle subsystem as researchable, including smart key, immobilizer, gateways, telematics, CAN domains, diagnostics, ADAS, and safety controllers | T5 subsystem register | Section 6 enumerates all named subsystems, including body, cluster, HVAC, camera/audio, VCU, BMS/HV, and charging | Some subsystems have no public NE1-specific topology |
| R8 | Confidential research; no public release and no framing as theft instructions | This plan; privacy rules | Sections 0, 10, and 11 set confidentiality and non-actuation boundaries; the private repository may retain raw research evidence while live credentials remain excluded | Confidentiality depends on repository and operator discipline |
| R9 | Create and use a private GitHub repository named Ioniq-5 | Ledger checkpoint; `gitscope` harness | Section 10 defines the explicit `ioniq` destination and staged-scope rules | Visibility and push verification are part of A-T6-2 |
| R10 | Extensive non-duplicative Parallelism and a Grok/Astra/Fable Council with truthful DeepSeek replacements | Council review batch 8 record | Section 12 records the three seats, their true models, and the labelled substitutions | Native Grok and Fable routes were unavailable for generation 10 |
| R11 | Install and run Hyundai Navigation Updater, download the official Australian 2021-23 IONIQ 5 package, and stop before USB or vehicle use | T2 acquisition section and installer metadata | Section 3.3 records the package identity, the read-only boundary, and the absence of USB or vehicle action | The updater's vendor signature remains invalid on the host; package acceptance by the car is unproven |

---

## 3. Identity baseline

### 3.1 Published Australian family

Hyundai Australia's official update table publishes the 2021-23 IONIQ 5 (NE1,
pre-facelift) as:

| Field | Published value | Status |
|---|---|---|
| Head-unit family | Standard Gen5W Navigation | Observed |
| Model name | `NEAE.S5BLN.AAU` | Observed |
| Software | `NE_E.AUS.S5W_L.001.001.260319` | Observed |
| Map | `AUS.19.41.47.011.611.0` | Observed |
| Update medium | USB; Hyundai recommends a 32 GB drive formatted exFAT | Observed |

The `S5W_L` token places the published family on the LG Linux stack. That is a
publication-level inference supported by the platform classification in T3, not
an observation of this car's installed build. The Australian model suffix
(`AAU`) differs from the European suffix (`AEU`); European packages must not be
cross-loaded.

The Australian September 2021 specification documents a smart-key,
push-button-start EV with an engine immobilizer, a 12.3-inch touchscreen with
satellite navigation, a BOSE external amplifier, Integrated Electric Booster
brakes, rack-mounted Motor Driven Power Steering, ESC, a PTC heater, CCS2
charging, and a 72.6 kWh / 653 V battery. Those are exact Australian
launch-spec statements. They establish features, not network topology or
security policy.

### 3.2 Installed build remains unknown

The car's own version screen is the installed truth. The published table can
differ from the car because of dealer updates, staged OTA, regional variation,
or a replaced head unit. Until Phase 1 records the car's Software, Firmware,
NAV APP, Map, and Model fields, every method in section 5 remains conditional.

### 3.3 Exact official package identity

The official macOS Navigation Updater acquired the Australian package for the
`2021-23 IONIQ 5`, Standard-class Gen5W. The package tree is retained locally
outside Git.

| Property | Observation |
|---|---|
| Package files | 36 |
| Total bytes | 9,514,830,930 (8.861 GiB) |
| Manifest payload records | 35 |
| Declared payload bytes | 9,514,828,145 |
| Manifest verification | 35/35 sizes and IEEE/zlib CRC-32 values match |
| Sorted-tree SHA-256 | `bc3013e5fc1499612cec76777aa736e0973a0b8a337c6619aace9af5a4d9652a` |
| Software identity | `NE_E.AUS.S5W_L.001.001.260319` |
| Map MD5 | `6b0b80623b56581cae994b49c02660ce` (declared and observed) |
| AU voice-resource MD5 | `8fa479c97e752b43c907c7838a7856ed` (declared and observed) |
| EU voice-resource MD5 | `6303095ad812cef04e245a5d0aa9ac08` (declared and observed) |
| Front-key checksums | Both match as CRC-32/MPEG-2 |

The package contains five text descriptors, two front-key blobs, three ordinary
archives, six plaintext IPK boot/kernel containers, nineteen high-entropy
opaque envelopes, and one empty sentinel. The Australian map is a valid PKZIP
archive with 374 entries; both `mango-vr_fixed.tar.gz` files are valid gzip/tar
streams.

The six `*_sub` IPK containers expose an x86-64 Linux 4.1.27-abl kernel, an
eMMC root on `/dev/mmcblk0p3`, ext4, systemd with `esinit`, Intel i915 graphics,
a 1920 x 720 panel mode, and `console=ttyS2`. Those are static package facts,
not evidence that the image was booted or accepted.

The nineteen opaque envelopes are consistent with a proprietary encoded or
encrypted layer. No cipher, key, nonce, authentication mode, or trailer
semantics are established. No decryption was attempted.

The installed updater identifies as `com.hyundai.update`, version
`261.015.0.215`, with a 67,950,208-byte main executable whose SHA-256 is
`7b63734d60ca42648e81fcf12a9518c46077859554c050e2134dc27120e0f37c`. The
bundle still fails vendor signature verification on the host. That affects
local client trust; it does not change the package bytes or their internally
verified manifest.

No USB medium was written, no package was inserted into the car, and no vehicle
action occurred.

---

## 4. Evidence labels and mutation levels

Every statement in this plan is labelled or scoped by one of three claim
classes:

- **OBS**: directly observed in an accepted artifact, official document, or
  owner-visible screen.
- **INF**: reasoned from cited evidence but not directly observed for this
  exact Australian vehicle.
- **UNK**: not established by the reviewed evidence.

Evidence tiers follow T5: exact Australian NE1; NE1 family with market
qualification; sibling Hyundai/Kia platform; corporate design and standards.
A statement does not move up a tier because it is repeated.

Mutation levels follow T3:

| Level | Meaning |
|---|---|
| L0 | Read-only analysis on a PC; no vehicle state change |
| L1 | Settings or state change in the head-unit UI; no persistent code |
| L2 | Code execution or a session on the head unit; not persistent across a stock reflash |
| L3 | Persistent modification of the system, root filesystem, or an installed application |
| L4 | Replacement of boot, system, or recovery images, or full custom firmware |

This plan authorises no work above L1 on the vehicle, and L1 work is restricted
to reading owner-visible screens without pressing Update, Default, or
dealer/service actions. Phases 6 and 7 concern a spare bench unit, never the
car, and their mutation level is assessed separately.

### 4.1 Key claims register

The register makes the separation explicit at the level of individual claims.
It is not a substitute for the full registers in the frozen artifacts.

| ID | Class | Claim | Basis |
|---|---|---|---|
| O1 | OBS | Hyundai Australia publishes the 2021-23 IONIQ 5 as Standard Gen5W, model `NEAE.S5BLN.AAU`, software `NE_E.AUS.S5W_L.001.001.260319`, map `AUS.19.41.47.011.611.0` | T1 identity table |
| O2 | OBS | The official package contains 36 files and 9,514,830,930 bytes, with 35 manifest payload records | T2 bottom line |
| O3 | OBS | All 35 manifest sizes and IEEE/zlib CRC-32 values match | T2 descriptor section |
| O4 | OBS | The Australian map is a valid PKZIP with 374 entries; both fixed voice resources are valid gzip/tar streams; their MD5 values match | T2 plaintext containers |
| O5 | OBS | Both front-key binaries match their declared CRC-32/MPEG-2 values | T2 front-key section |
| O6 | OBS | Six `*_sub` files are plaintext IPK containers exposing an x86-64 Linux 4.1.27 kernel, eMMC, ext4, systemd, and i915 strings | T2 IPK section |
| O7 | OBS | Nineteen files are high-entropy opaque envelopes with no plaintext archive signature at the implied offset | T2 opaque section |
| O8 | OBS | The updater identifies as `com.hyundai.update` version `261.015.0.215`; its bundle fails vendor signature verification on the host | T2 acquisition and trust sections |
| O9 | OBS | No USB medium was written and no vehicle action occurred | T2 handling boundary |
| O10 | OBS | The Australian launch specification lists smart key, push-button start, immobilizer, 12.3-inch touchscreen, BOSE amplifier, IEB, ESC, R-MDPS, PTC, CCS2, and a 72.6 kWh / 653 V battery | T5 bottom line and source S1 |
| O11 | OBS | Diagnostic-vendor coverage lists the Ioniq 5 under security-gateway secured access | T5 gateway section |
| O12 | OBS | Hyundai UK documents an Ioniq 5 key-emulation weakness and a hardware-plus-software upgrade | T5 smart-key section |
| O13 | OBS | Australian ICCU and SCU recalls show software-mediated loss of motive power and park-pawl failure | T5 vulnerability implications |
| O14 | OBS | `hmg_nemesis` targets Android 4.4.2, Telechips TCC803x, firmware 260507 | T7 compatibility decomposition |
| O15 | OBS | Council generation 10 accepted frozen batch 8 with three COMPLETE seats and C1-C6 passing | Council packet and ledger review records |
| I1 | INF | The published Australian `S5W_L` family is on the Linux stack, not the Android `S5W_M` branch | T3 observations O1-O3 and inference I1 |
| I2 | INF | The `260319` suffix likely encodes the 19 March 2026 build date | T2 descriptor and kernel timestamp |
| I3 | INF | The opaque envelopes likely use a vendor encoding or encryption layer | T2 opaque section |
| I4 | INF | NEMESIS is not an applicable method for this car as published | T7 compatibility decomposition |
| I5 | INF | The AVN can reach other vehicle domains only if the NE1 gateway forwards its traffic; this is plausible but unproven | T5 trust and data-flow analysis |
| I6 | INF | Engineering mode is a prerequisite for several Linux-family methods, but neither its reachability nor its gating is established here | T3 inference I3 and unresolved issues |
| I7 | INF | The package carries a complete component set (map, navigation, GUI, root filesystem, modem, boot), but full-versus-delta status is not established | T2 observed/inferred/unknown |
| U1 | UNK | The car's installed software, firmware, NAV APP, map, and model | T1 installed-build caveat |
| U2 | UNK | Head-unit part number, hardware revision, SoC, RAM, storage, and radio configuration | T4 and T5 identity sections |
| U3 | UNK | Envelope format, keys, nonce/IV handling, authentication mode, and trailer semantics | T2 remaining gaps |
| U4 | UNK | Package-level signing or attestation outside the opaque envelopes | T2 integrity and trust |
| U5 | UNK | Whether the package is full or delta relative to a prior build | T2 remaining gaps |
| U6 | UNK | NE1 gateway filter policy and AVN-to-gateway transport | T5 gateway section |
| U7 | UNK | Telematics fitment on this 2021 Australian car | T5 telematics section |
| U8 | UNK | Engineering-mode reachability and gating on the installed build | T3 unresolved issues |
| U9 | UNK | Installed-build patch state relative to the 2023 Gen5W_L CVEs | T3 unresolved issues |
| U10 | UNK | Recovery routes and their persistent-state coverage for this exact variant | T7 Gate 4 and recovery limitations |
| U11 | UNK | Whether the vehicle accepts the downloaded package | T2 remaining gaps |
| U12 | UNK | Wi-Fi hardware presence and enablement | T5 network domains |
| U13 | UNK | Australian applicability of the UK keyless weakness | T5 smart-key section |

---

## 5. Method landscape

The published record does not describe one "Gen5W" stack. It describes at least
an Android `S5W_M` branch and a Linux `S5W_L` branch. The published Australian
family is `S5W_L`. The catalogue below is for orientation; it is not a set of
procedures.

| ID | Method family | Platform scope | Evidence grade | Mutation | Applicability to this car |
|---|---|---|---|---|---|
| M1 | Official updater download plus offline package parsing | Gen5, Gen5W, ccNC | B/C | L0 | The download and read-only parsing route has been executed for the AU package; the encrypted-envelope layer remains unparsed |
| M2 | Engineering, dealer, and service modes | `S5W_L`, `S5W_M`, D2V, ccNC | B/C | L1 | Reachability and gating unknown on the installed build; not reproduced |
| M3 | Android Gen5W update-component validation gap | `S5W_M` Android 4.4.2 | B | L3 | Platform mismatch unless the installed hardware is shown to differ |
| M4 | Android Gen5W debugging transport and persistent-privilege outcomes | `S5W_M` Android, older and newer generations | B | L2-L4 | Chipset-specific; no Ioniq 5 confirmation; platform mismatch |
| M5 | Linux Gen5W navigation-application replacement | `S5W_L` Linux/mango | B | L3 | Platform-matched family; version, page availability, patch state, and recovery unproven |
| M6 | Linux Gen5W OTA decryption and patched rootfs persistence | `S5W_L` Linux/mango | B/C | L3-L4 | Platform-matched family; device-extracted material and a prior execution path are prerequisites; not applicable as a first step |
| M7 | Linux Gen5W Wi-Fi and SSH session | `S5W_L` Linux | C | L2 | Session-only claim; repository steps are incomplete; unknown on AU hardware |
| M8 | Chimaera peer-reviewed Gen5W_L exploit | Gen5W_L, build 211214, EUR | A | L4 | Family-level relevance; version-specific and not tested on NE1 |
| M9 | NEMESIS DSP OTA helper root | Gen5W Android 4.4.2, TCC803x, build 260507 | B | L3 | Not applicable as published; platform mismatch (see T7) |
| M10 | Gen5 iAVN engineering surface | Gen5 Android 4.2.2 | A | L3 | Historical, different generation |
| M11 | Gen5 offline package modification and vendor recovery | Gen5 Android | B | L4 | Historical, different generation |
| M12 | D-Audio2V update-archive protection | D-Audio2V | B | L4 | Different platform |
| M13 | Commercial Gen5W customware | `S5W_M` primarily, `S5W_L` listed | C | L3 | Commercial service, not published research; excluded |
| M14 | ccNC root claims | ccNC, Tegra X2 | D | L3 | Different platform, patched, not applicable |

The strongest public security research (M8) is peer-reviewed, CVE-backed, and
version-specific. The most detailed repositories (M3-M9) are community work
with device logs or released artifacts but limited independent replication. No
credible public evidence was found for unauthenticated network entry, a Gen5W
browser/WebView remote exploit, or OTA-server compromise. Every published chain
requires local physical access and, for code execution, a prior trust failure
in the update or navigation path.

---

## 6. Vehicle subsystem register

This register covers every subsystem named by R4 and R7, plus the adjacent
subsystems needed to reason about them. "Established" means published or
official evidence, not a claim about this specific car beyond its published
family. "Boundary" states what this programme will not do.

| Subsystem | Role | What is established | Status | Research question | Boundary |
|---|---|---|---|---|---|
| Infotainment / AVN | HMI, navigation, media, phone projection, vehicle settings, camera display, update client | Published AU model and software; 12.3-inch display, Bluetooth, USB, CarPlay/Android Auto; Linux `S5W_L` family inference | Observed AU identity; installed build unknown | Exact installed OS build, patch state, AVN-to-gateway transport, Wi-Fi state | No exploitation, no code execution, no update installation |
| Instrument cluster | Driver display, warnings, ADAS and powertrain status | 12.3-inch colour cluster; sibling evidence places cluster on a multimedia bus | Observed feature; transport inferred | Exact NE1 transport and integrity checking | No display spoofing, no cluster modification |
| Smart key and keyless entry | Passive entry, locking, remote start, RSPA, charge-door control | Australian smart key with push-button start; 0.7-1.0 m door proximity and 10 m remote-start ranges; UK Ioniq 5 key-emulation weakness and Hyundai upgrade | Observed features; UK issue observed; AU applicability unknown | AU key generation, receiver allocation, protocol, whether AU cars are affected | No key emulation, relay, replay, or entry procedure |
| Immobilizer and start authorization | Coding check, start enable, brake/P/start preconditions | Australian immobilizer; key must be inside; start preconditions documented; IBU/BCM participates in start logic | Observed features; crypto and module allocation unknown | Which module hosts the receiver and immobilizer; whether entry and start share a trust anchor | No immobilizer defeat, no start bypass, no credential or code extraction |
| Body controller (IBU/BCM), locks, alarm | Locks, windows, lighting, wipers, alarm, start preconditions | NE1 fuse list names IBU and ICU; Hyundai IBU/BCM campaign exists but excludes IONIQ 5; AU alarm and immobilizer listed | Observed components; bus split inferred | IBU versus BCM packaging; LIN actuator map; gateway integration | No lock/alarm manipulation, no body actuation |
| Central and security gateway | Route and filter CAN, CAN-FD, Ethernet, LIN; authorize diagnostic special functions | Diagnostic-vendor coverage lists Ioniq 5 security-gateway secured access; Hyundai patents describe certificate-based and MAC-verified routing | Presence inferred from independent vendor evidence; filter policy unknown | Physical packaging, routing table, whether AVN-originated frames reach body/chassis/powertrain | No gateway bypass, no filter-rule probing on a live car |
| CAN and in-vehicle network domains | Transport between subsystems | Community labels ECAN/MCAN/BCAN; sibling research uses M/B/C bus terms; CAN 2.0 frames carry no sender authentication field | Protocol property observed; NE1 segmentation inferred/unknown | Exact bus names, speeds, CAN-FD assignment, Ethernet and LIN use | No frame injection, no live bus probing in this programme |
| OBD / DLC diagnostics | DTCs, live data, actuator tests, routines, programming | DLC in NE1 fuse list; ISO 15765-4 and ISO 14229; security gateway gates special functions | Standards observed; service matrix unknown | Which services are allowed unauthenticated; diagnostic reach per domain | No actuator tests, no coding, no DTC clearing, no live diagnostic session without separate approval |
| Telematics / TCU / CCU / Bluelink / eCall | Cellular connectivity, remote status and commands, eCall, remote diagnostics, OTA | AU Bluelink service architecture and privacy notice; AU 2021 specification omits Bluelink; AU launch history and a 2023 dealer statement conflict with fitment assumptions | Service design observed; 2021-22 AU fitment unresolved | Whether a TCU/CCU is fitted; SIM/eCall activation; remote-command allowlist | No account access, no remote command, no cellular interception |
| ADAS sensing and ECUs | Camera, radar, ultrasonic sensing, fusion, FCA/LKA/SCC/HDA/RSPA | AU SmartSense features and sensor counts; Munro teardown shows separate ADAS driving and parking ECUs; manuals document sensor roles | Features observed; sensor transport and request path inferred | Whether ADAS requests go directly to IEB/MDPS or through VCU; ASIL decomposition | No sensor spoofing, no ADAS actuation, no calibration changes |
| Braking, steering, and chassis safety controllers | IEB/ESC/ABS/EBD/EPB, R-MDPS, stability control | AU specification lists IEB, ESC, ABS, EBD, EPB, R-MDPS; fuse list names IEB and MDPS | Hardware observed; bus and arbitration inferred | ASIL levels, actuator arbitration, cyber monitoring of the chassis bus | No brake or steering actuation, no safety-control disablement |
| VCU and drivetrain | Torque, regen, drive mode, power distribution, start linkage | E-GMP VCU role; AU motor and battery specification; NE1 fuse list; driveshaft recall | Functions observed; topology inferred | Torque arbitration, VCU/ADAS/ESC authority split, campaign history | No torque request, no drive-mode or powertrain manipulation |
| BMS, high voltage, and charging | Cell monitoring, SOC/SOH, contactors, isolation, thermal management, AC/DC charging, V2L | AU 72.6 kWh / 653 V pack, CCS2, V2L; ICCU/VCMS roles; ICCU recall and TSB; HV emergency-response guide | Components observed; contactor and charging-auth details unknown | BMS/VCU/ICCU arbitration, Plug & Charge support, contactor control path | No HV work, no contactor operation, no charging manipulation |
| HVAC | Climate, PTC heater, defog, preconditioning | AU dual-zone climate, PTC heater, auto defog; VCU climate role; fuse list | Features observed; LIN and heat-pump fitment unknown | Actuator bus, remote-climate allowlist, battery thermal role | No climate actuation, no remote preconditioning |
| Camera and audio | Rear/surround/blind-spot cameras, amplifier, speakers, microphone | AU SVM, BVM, rear-view monitor, BOSE amplifier; fuse list; teardown imagery | Features observed; transport unknown | Camera physical layer, microphone retention, amp bus | No camera or microphone access, no audio injection |
| USB, Bluetooth, and phone projection | User media, pairing, CarPlay/Android Auto | AU specification; updater uses USB media for official updates | Features observed; USB role and internal filesystem unknown | Descriptor behaviour, projection protocol, persistent pairing/index state | No update-bearing media, no permission grants, no personal phone data |
| Update and software supply chain | Official package acquisition, verification, installation, recovery | Official updater and package identity; internal CRC/MD5 consistency; opaque envelopes; vendor no-revert statement | Package observed; signing chain and acceptance unproven | Package-level signature, envelope scheme, full-versus-delta status, vehicle acceptance | No USB write, no flashing, no installation, no downgrade attempt |

The register is deliberately broader than the head unit. The vehicle's safety
and authorization systems are in scope as research subjects, but they are not
targets for actuation or defeat.

---

## 7. Trust boundaries and network domains

The conceptual zones below follow T5. They describe authority, not physical
packaging:

| Zone | Contents | Why it matters |
|---|---|---|
| Z0 external | Cloud, phone, USB media, charging supply, smart-key fob | Untrusted input and key material enter here |
| Z1 telematics | Cellular modem, eCall, remote-command gateway | Separate cloud trust boundary; AU 2021-22 fitment unverified |
| Z2 infotainment | AVN, cluster, camera/audio display | High user-controlled input, low actuation authority |
| Z3 gateway | Routing and authorization between Z2 and vehicle domains | The pivotal boundary |
| Z4 body/comfort | IBU/BCM, locks, alarm, HVAC, start preconditions | Body authority and start logic |
| Z5 chassis/ADAS | IEB/ESC, MDPS, ADAS ECUs | Safety-critical functions |
| Z6 powertrain/HV | VCU, BMS, ICCU, contactors, motor/inverter | High energy and motion authority |

The public record supports a narrow but important conclusion: the head-unit
family has had exploitable firmware and can emit CAN frames on its local
multimedia bus, and the NE1 has a gateway. The record does not establish what
the NE1 gateway forwards. An AVN compromise that stays in Z2 is an
infotainment and privacy event; a crossing into Z4-Z6 would be a body,
availability, or safety event. This programme treats the crossing as unproven.

What would change that conclusion:

- an NE1 service-manual topology showing the AVN's physical bus and the
  gateway routing table;
- a gateway configuration or teardown showing whether AVN-originated frames are
  admitted to body, chassis, or powertrain buses;
- an owner-authorised model-specific test on a 2021-23 Australian NE1;
- a Hyundai security bulletin or CVE mapping the 2023 Gen5W_L fixes to
  `NE_E.AUS.S5W_L.001.001.260319`, plus an installed-build readback.

None of those is present today.

---

## 8. Phased car-specific plan

Each phase has a purpose, a non-actuating action set, outputs, and an exit
criterion. A phase does not begin because the previous phase "mostly" passed;
its exit criterion is either met, or the programme stops and records why.

### Phase 0 - Identity and privacy freeze (no vehicle)

Purpose: create the private evidence workspace and the rules before the first
observation.

Actions:

- Create a private evidence directory outside Git.
- Create a manifest before the first capture, with file name, date, tool,
  purpose, and hash.
- Record the accepted T1 identity and the exact package identity separately
  from anything later read from the car.
- Prepare redaction rules for identifiers, phone names, modem identifiers,
  Bluetooth names, passkeys, locations, and third-party data.
- Confirm the `.gitignore` rules and the explicit `ioniq` push destination.

Outputs: private workspace, manifest, redaction rules, hash log.

Exit E0: the private directory exists, is excluded from Git, and the manifest
has its first entry. No vehicle action has occurred.

### Phase 1 - Installed-build and feature readback (owner-visible only)

Purpose: replace publication-level identity with this car's installed truth.

Actions:

- Park safely. Power the car so the head unit stays awake, as the owner manual
  requires for reading settings.
- Read and photograph the Version info screen: Model, Software version,
  Firmware version, NAV APP, Map version. Redact Device ID from any retained
  image.
- Read the System info and modem-information screens for feature presence.
  Record only whether a field exists; do not retain identifiers.
- Record the visible before state of What's new, memory, and any update notice.
- Do not press Update, Default, dealer/service actions, or any reset.

Outputs: redacted screen captures or transcribed fields; a comparison against
`NE_E.AUS.S5W_L.001.001.260319`; a note of any UI-generated state.

Exit E1: the software tuple is recorded and either matches the published
contract or is explicitly different. If it is different, identity reopens and
later method selection pauses. No installation or reset action was pressed.

### Phase 2 - Official media and static analysis (PC only)

Purpose: characterise the official software without touching the car.

Status: substantially complete for the current `260319` package.

Actions:

- Retain the official package outside Git.
- Re-verify the 36-file inventory, the sorted-tree digest, the 35 manifest
  size and CRC records, the map and voice MD5 values, and the front-key
  CRC-32/MPEG-2 values.
- Classify plaintext containers, opaque envelopes, boot/kernel containers, and
  runtime strings.
- Keep the package read-only: no execution, mounting, decryption, modification,
  or removable-media write.

Outputs: T2 artifact and metadata inventories; an updated claims register.

Exit E2: every package claim is labelled observed, inferred, or unknown; no
USB medium was written; no vehicle was connected.

### Phase 3 - Passive USB and phone-projection observation (optional)

Purpose: establish USB role and projection behaviour without modifying the
head unit.

Actions:

- Use an inline USB protocol analyzer rated for the observed link speed, a
  clean test phone, and a disposable benign media set.
- Capture descriptors and a short connect/disconnect sequence.
- Do not insert update-bearing media. Do not grant contacts or messages
  permissions. Do not pair a personal phone.
- Record the head-unit UI before and after for new media indexes, device
  entries, or projection entries, because those are software-state changes
  even when the electrical connection is passive.

Outputs: redacted descriptor log; a before/after state note.

Exit E3: captures contain no personal data or are quarantined for redaction;
no update was triggered; every new head-unit entry is documented.

### Phase 4 - Passive radio observation (optional, separately authorised)

Purpose: test whether documented Bluetooth or cellular behaviour is observable
without association or injection.

Actions:

- Use a receive-only receiver or an SDR with transmit disabled.
- Monitor only; do not associate, inject, deauthenticate, or impersonate.
- Keep the window short and the channel plan fixed.
- Apply the legal and privacy limits in section 10.

Outputs: a short observation log; a negative result recorded as weak evidence.

Exit E4: no third-party payload or location data leaves the private directory.
A negative RF result does not establish absence of a radio or service.

### Phase 5 - Service documentation and read-only diagnostics

Purpose: obtain documented module and diagnostic context from an authorised
service channel.

Actions:

- Request a read-only diagnostic report and VIN-scoped parts identification.
- Explicitly forbid DTC clearing, resets, coding, calibration, and ECU updates
  unless separately authorised in writing for that exact action.
- Treat the report as dealer-supplied evidence, not owner observation.
- Do not copy restricted service-information content outside its licence.

Outputs: a redacted module inventory and part-family record; any DTC history
reported.

Exit E5: the report is understood as a separate evidence tier; no mutating
diagnostic action occurred.

### Phase 6 - Spare or bench unit acquisition

Purpose: obtain hardware evidence without putting the car at risk.

Actions:

- Acquire a matching or plausibly matching head unit.
- Photograph the exterior, label, regulatory marks, and connectors before
  power.
- Record the first-power UI state and any counters or logs before and after
  power-up.
- Do not open the unit yet and do not connect it to the car.

Outputs: label and part-number record; software version of the spare; connector
inventory from exterior inspection only.

Exit E6: the part number and software version are recorded, and the unit has
never been connected to the vehicle.

### Phase 7 - Bench teardown and storage/debug work (optional)

Purpose: study board-level and storage-level architecture on a spare, never on
the car.

Actions:

- Photograph the board before and after each step; use ESD protection and a
  current-limited supply.
- Start with non-destructive external inspection.
- Classify each step separately by physical invasiveness and by restoration
  outlook. Do not assume chip-off is uniformly destructive or that pad access
  is risk-free.
- Treat all storage images and extracted personal data as sensitive.

Outputs: board and component inventory; storage and partition map at the level
the method supports; a restoration assessment per method.

Exit E7: work remains on the spare; every destructive or state-changing step
has a written rationale and an explicit owner decision. The car is untouched.

### Phase 8 - Synthesis and confidential documentation

Purpose: integrate findings without inventing certainty.

Actions:

- Update the claims register with observed, inferred, and unknown entries.
- Record which methods remain inapplicable and why.
- Record any recovery evidence against Gate 4 (section 9).
- Keep raw material outside Git; commit only text summaries, hashes, and
  metadata inventories.

Outputs: revised evidence artifacts, history, and changelog.

Exit E8: every requirement has an evidence pointer; every unresolved question
is still visible; the integrated harness passes; the coordinator reviews the
staged file list.

### Stop conditions for every phase

Stop and record the exact condition if:

- an update, reset, calibration, coding, or DTC-clear prompt appears;
- a step would require disconnecting high-voltage, airbag, or safety systems;
- a capture contains third-party personal data that cannot be redacted;
- a step requires a pinout, probe point, or procedure not covered by an
  authorised source;
- the car would be left in a non-standard or undrivable state;
- the installed software contradicts the published identity and the method
  selection depends on it;
- a recovery claim is being used as if it were proven when it is not.

---

## 9. Gate 4 recovery handoff and ASTRA-G7-S01 closure

### 9.1 The open finding

ASTRA-G7-S01 carries ASTRA-G5-02: earlier recovery wording could be read as
claiming a single exclusive restoration route, and the T6 Gate 4 handoff was
left open. T7 addressed the recovery question within its own scope by adopting
Gate 4 and recommendation 4, and the accepted T4 revision separates physical
restoration from persistent software state. T6 still owes the explicit
handoff, which this section supplies.

### 9.2 Gate 4 is a four-part conjunction

Before any stage that changes head-unit software state is even considered, all
four of the following must be established for this exact model and variant:

1. A manufacturer-supported recovery entry point exists and is usable for this
   exact model and variant.
2. The persistent state that the entry point covers is enumerated and shown to
   cover the state the proposed work would change.
3. Same-version repair is supported, not merely "a later version exists".
4. The downgrade and rollback policy is explicit, including Hyundai
   Australia's published statement that installation cannot be reverted from
   the owner's perspective.

If any part is unknown, Gate 4 is closed. Package completeness (full versus
delta) is a separate property and does not prove any of the four.

### 9.3 Physical restoration and persistent software state are separate claims

Replacing or restoring hardware can return the car to service without restoring
the software state that was changed. Conversely, a software restoration can
leave hardware, counters, or configuration altered. The plan therefore records
two independent columns for every later method:

- physical/electrical restoration outlook;
- persistent software and security-state coverage.

Neither column implies the other. T4's route matrix already separates them; this
plan adopts that separation as a Gate 4 input.

### 9.4 No recovery route is asserted to be exclusive

The reviewed record contains several possible recovery concepts: vendor
service restoration, official update overwrite, spare-part replacement, and
bench re-imaging. None is proven on this car, and this plan does not claim that
any one is the only route. A route is recorded as a hypothesis with an evidence
grade until it is verified on the exact unit. Exclusivity is a claim that would
require its own evidence.

### 9.5 Stop rule

Until Gate 4 is satisfied in full, no phase may write removable media, install
software, patch an image, modify the head unit, or alter vehicle state. Static
analysis, owner-visible readback, and bench work on a spare may continue
because they do not depend on vehicle recovery.

### 9.6 Closure statement within T6 scope

This section resolves the T6 portion of ASTRA-G7-S01 by:

- restating Gate 4 as a conjunction rather than a single restore action;
- separating physical restoration from persistent software-state coverage;
- refusing to assert any recovery route as exclusive or universal;
- stating that a full-image restore alone does not satisfy Gate 4;
- making Gate 4 a hard stop before any state-changing stage.

Ledger mutation is coordinator-owned; this artifact records the disposition, not
a ledger edit.

---

## 10. Privacy, confidentiality, and Git handling

### 10.1 Data classes

| Class | Examples | Storage |
|---|---|---|
| Public source material | Official manuals, public recalls, published research, public package metadata | May be summarised in evidence notes with citations |
| Confidential analysis | This plan, evidence notes, claims registers, Council records | Private Git repository only |
| Raw package material | Downloaded 9.5 GB official package tree | Outside Git; local private storage |
| Extracted research material | Extracted containers, decoded payloads, firmware images | Private Git repository when deliberately staged and provenance-labelled |
| Raw captures | USB traces, RF captures, screen images, diagnostic exports | Private Git repository when deliberately staged and accompanied by a manifest |
| Identifiers | VIN, Device ID, modem identifiers, Bluetooth names, plate, location | Private Git only when required for vehicle-specific provenance; never publish publicly |
| Personal data | Phone names, contacts, messages, paired-device data, third-party images | Minimise and segregate; commit only when explicitly necessary and authorized |
| Credentials and keys | Account credentials, tokens, private keys, key material | Never collected or committed |

### 10.2 Capture and redaction rules

- Redact before sharing or storing a derived image; do not rely on cropping a
  copy that still contains the original.
- Keep raw captures in a clearly labelled directory with a manifest entry and
  review the exact staged set before every push.
- Do not record third-party personal data. If it appears, stop the capture and
  delete it rather than building a redaction pipeline around unnecessary data.
- Storage images are treated as personal data by default, even when the visible
  content appears technical.
- Retain material that answers a recorded research question; label provenance,
  ownership, sensitivity, and any redistribution restrictions in its manifest.

### 10.3 Git scope

Belongs in the private `Ioniq-5` repository:

- this plan, `Ioniq5-HISTORY.md`, `Ioniq5-CHANGELOG.md`, `.gitignore`;
- evidence notes and metadata inventories that contain no raw payload or
  personal data;
- the research ledger, Council packets, and the validation harness;
- text summaries and hashes;
- deliberately reviewed raw firmware, extracted analysis trees, captures,
  device-specific dumps, vehicle identifiers, and temporary analysis material.

Must never be staged:

- the downloaded 9.5 GB `2021_22_IONIQ_5_AU` package tree;
- credentials, tokens, keys, or account material;
- unauthorized third-party personal data;
- `kona_research/**` under an Ioniq commit;
- the Kona-owned root `HISTORY.md` and `CHANGELOG.md`.

The `.gitignore` in this revision excludes only the exact official 9.5 GB
package tree, live credential/private-key material, and regenerable cache noise.
Firmware, archives, extracted trees, captures, dumps, identifiers, and analysis
workspaces are no longer categorically ignored and require deliberate staging.

Push destination: the explicit `ioniq` remote must resolve to the private
`JaredReabow/Ioniq-5` repository, with `remote.pushDefault=ioniq`. The shared
checkout's `origin` remains the Kona repository for Kona fetch and tracking and
must not be used for an Ioniq push. The harness verifies the destination rather
than trusting a mutable default.

---

## 11. Safety and non-actuation boundary

The following are outside this plan's authority, regardless of research value:

- live vehicle entry or any procedure intended to open or start a vehicle
  without its key;
- keyless-entry, immobilizer, or start-authorization defeat;
- credential replay, token extraction, or account access;
- safety-control disablement, including braking, steering, ADAS, HV, or
  contactor functions;
- USB media writing, firmware flashing, installation, downgrade, or rollback;
- vehicle actuation, diagnostic actuator tests, coding, calibration, or DTC
  clearing.

Research may describe why these systems exist, how they are decomposed, what
public evidence shows about their trust boundaries, and what risks follow from
a failure. It does not produce the operational sequence for defeating them.

---

## 12. Council and independent acceptance record

### 12.1 Research acceptance

Council generation 10 reviewed frozen batch 8:

| Property | Value |
|---|---|
| Package | `council/review-batch-8` |
| Frozen-package fingerprint | `9c410e07d2a130c967ac567f5e32788731c909ca2e2c684fc856fc8c3080198b` |
| Council packet SHA-256 | `a9bc3a9d951f97cc4438508cddf6df121a9437de45ae0c06406a3f32508efeb4` |
| Checker outcome | `COMPLETE`; package verified; C1-C6 passed |

Seats and verdicts:

| Seat | Model actually used | Verdict | Note |
|---|---|---|---|
| Astra lead | `gpt-6-astra` | COMPLETE | Native route completed |
| Grok seat | `deepseek/deepseek-v4.1-flash` | COMPLETE | Truthful labelled replacement after native Grok returned HTTP 429; an earlier replacement response was discarded before the clean retry |
| Fable seat | `deepseek/deepseek-v4-flash-vision-exp` | COMPLETE | Truthful labelled replacement after native Fable declined on scope grounds |

The replacements are recorded as replacements. They are not presented as
native Grok or native Fable output. Generation 9 remains rejected history and
does not count toward this acceptance.

### 12.2 T2 acceptance

T2 was accepted separately by an independent `gpt-6-sol` review after the
reviewer reproduced the package inventory and integrity checks. The acceptance
record is in `research-ledger.json`; the artifact hashes are in section 1.

### 12.3 T6 review

This plan, the dedicated history and changelog, and the `.gitignore` address
A-T6-1 and are submitted for independent T6 review. A-T6-2 (staged-content
verification, private-repository verification, commit, and push) remains a
coordinator action after that review.

---

## 13. Open questions and decision points

| ID | Question | Class | What would answer it |
|---|---|---|---|
| Q1 | What software, firmware, NAV APP, map, and model does this car actually run? | UNK | Phase 1 owner-visible readback |
| Q2 | What head-unit part number, SoC, RAM, storage, and radio configuration are fitted? | UNK | Phase 5 parts query, Phase 6 label, Phase 7 board inspection |
| Q3 | What is the opaque envelope format, and is there a package-level signature chain? | UNK | Independent public format documentation or a non-destructive decoder path |
| Q4 | Is this package full or delta relative to a prior build? | UNK | Comparison with an independently obtained prior or dealer build |
| Q5 | Does the NE1 gateway admit AVN-originated frames to body, chassis, or powertrain domains? | UNK | Service topology, gateway configuration, or an authorised model-specific test |
| Q6 | Is telematics fitted to this 2021 Australian car? | UNK | Phase 1 modem information and, if needed, a VIN-scoped dealer query |
| Q7 | Is engineering mode reachable on the installed build, and what gates it? | UNK | Owner-visible or dealer documentation; no entry procedure is to be developed |
| Q8 | What is the installed build's patch state relative to the 2023 Gen5W_L CVEs? | UNK | Vendor build mapping or an authorised inspection |
| Q9 | What recovery routes exist for this exact variant, and what state do they cover? | UNK | Vendor guidance and unit-specific proof; Gate 4 |
| Q10 | Does the vehicle accept the downloaded package? | UNK | Vehicle-side installation, which is outside this plan |
| Q11 | Is Wi-Fi present and enabled on this unit? | UNK | Phase 1/3 observation and hardware evidence |
| Q12 | Does the UK keyless upgrade have an Australian equivalent? | UNK | Australian recall or service-bulletin search, VIN-scoped dealer query |

No decision point above authorises actuation. Each is an evidence question.

---

## 14. Limitations

- The car's installed software and hardware have not been observed.
- The package contains nineteen opaque envelopes whose scheme is unknown.
- Internal CRC and MD5 consistency is not an independent vendor authenticity
  proof.
- The updater bundle fails vendor signature verification on the host. That is a
  local client-trust caveat, not a package-integrity finding.
- The package's full-versus-delta status is unknown.
- No recovery route is proven for this car, and Hyundai Australia states that
  installation cannot be reverted from the owner's perspective.
- NE1 gateway filter policy, key protocol, immobilizer crypto, ASIL allocation,
  and several bus assignments are not public.
- Australian applicability of the UK keyless issue is not established.
- Telematics fitment on a 2021-22 Australian NE1 is unresolved.
- No live vehicle, diagnostic, network, or actuation work was performed for this
  plan.

These limits are part of the result. They are not gaps to be papered over with
sibling-platform assumptions.

---

## 15. Revision and integrity

- Revision 1, 2026-10-19: initial T6 integration. Binds accepted T1-T5 and T7
  plus accepted T2; defines the phased plan, subsystem register, Gate 4
  closure, privacy handling, and Git scope.
- Input hashes are frozen in section 1. Any accepted-input change requires a
  new revision, a re-run of the integrated harness, and re-review.
- This document contains no raw payload, capture, credential, vehicle
  identifier, or personal data.
