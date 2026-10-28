# Published Gen5W and Ioniq 5 infotainment software-entry methods

Task T3 (research), requirement R2. Confidential, owner-authorized research;
local only. No credentials, passcodes, key material, payloads, or step-by-step
vehicle procedures are reproduced here. The purpose is engineering assessment:
what entry surfaces exist, what each author actually demonstrated, what is
required, what was claimed about recovery, and what still applies on
2026-10-18.

Access date for every URL below: 2026-10-18 (UTC). Publication or last-edit
dates are stated where the source exposes them; "unknown" means the source did
not expose a date and no reliable third-party date was found.

---

## 1. Bottom line

1. "Gen5W" is not one software stack. The published record uses the name for at
   least two distinct families:

   - `S5W_M`: Mobis, Android 4.4, wide screen. Menaco states this directly
     (source S29).
   - `S5W_L`: LG, Linux (ccOS/Qt-QML), wide screen. Menaco states this directly
     (source S29); the Linux Gen5W literature and tooling described in S3, S4,
     S8, and S11 matches this family, using an on-device decryption component
     and an installer rather than the Android package format.

2. Published entry methods divide the same way. The Android Gen5W methods
   (update-component validation gap, debugging transport, DSP OTA helper) are
   documented against Android Gen5W units (S1, S2, S9);
   Menaco maps that Android branch to `S5W_M` (S29). The Linux Gen5W methods
   (navigation-application replacement, update decryption, root-filesystem
   patching, network-shell component) are documented against `S5W_L`/mango
   units (S3-S6, S11).

3. T1's accepted identity result establishes the published Australian 2021-23
   IONIQ 5 (NE1) family as Standard Gen5W, model `NEAE.S5BLN.AAU`, current
   published software `NE_E.AUS.S5W_L.001.001.260319` (S30). The `S5W_L`
   token and Menaco's classification place that published family on the LG
   Linux stack; early European owner reports of `S5W_L` builds are consistent
   (S24, S25). This is publication-level identity only: the user's installed
   software, hardware revision, and patch state remain unobserved.

4. Evidence quality is uneven. The strongest public work is peer-reviewed and
   CVE-backed but version-specific (Gen5W_L 211214, Chimaera: S7, S12). The
   most detailed repositories are community work with device logs and released
   artifacts (S1, S2, S3). One 2026 repository is documentation of an
   intended chain rather than a demonstrated car exploit (S11 explicitly
   validates only a synthetic dry run).

5. No credible public evidence was found for unauthenticated network entry,
   a Gen5W WebView/browser remote exploit, or OTA-server compromise. Every
   published chain requires local physical access (USB and/or engineering
   mode) and, for code execution, a prior trust failure in the update or
   navigation path.

---

## 2. Terminology and evidence labels

Evidence strength:

- **A**: peer-reviewed paper and/or vendor-independent CVE record, with a
  named affected version.
- **B**: primary author repository with device-specific artifacts, logs, or a
  released package, but no independent replication.
- **C**: repository or documentation without device validation, or a
  single-source technical claim.
- **D**: forum, Reddit, or commercial claim; anecdotal until corroborated.

Mutation level:

- **L0**: read-only analysis on a PC; no vehicle state change.
- **L1**: settings/state change in the head unit UI; no persistent code.
- **L2**: code execution or a session on the head unit; not persistent across
  a stock reflash/update.
- **L3**: persistent modification of `/system`, the root filesystem, or an
  installed application.
- **L4**: replacement of boot/system/recovery images or a full custom
  firmware.

Claim tags used in the profiles: **[OBS]** observed in a cited source,
**[INF]** inference from cited facts, **[UNK]** unresolved.

---

## 3. Method matrix

| ID | Method | Primary source (type) | Date | Platform | Version / region scope | Prerequisites | Evidence | Mutation | Recovery claim | Status 2026-10-18 |
|---|---|---|---|---|---|---|---|---|---|---|
| M1 | Official updater download plus offline package parsing (`nudl`) | S16 blog, S17 tool (secondary + repository) | 2026-10-15 | Gen5, Gen5W, ccNC | EU Kia EV6 MY22 `CV_E.EUR.S5W_L.001.001.260128`; Hyundai Ioniq 5 named as same procedure | PC, 32 GB+ USB, exFAT, ~25 GB download | B/C | L0 | n/a | Current; official payloads still encrypted. EV6 EU layout is an analogy, not an observed AU package (T2 pending) |
| M2 | Engineering / dealer / service mode | S10 secondary reference, S11 repository analysis | 2026-10-01 page; 2026-06-30 analysis | `S5W_L`, `S5W_M`, D2V, ccNC | EUR builds incl. 250604, 251204, 260128; other regions vary | Vehicle UI access; model- and build-specific gesture; rotating passcode | B / C | L1 | None needed; settings-only | Partial: entry works on some builds; `S5W_L` MASS_PRODUCT reportedly gated by a separate SOP check |
| M3 | Android Gen5W update-component validation gap | S2 repository (Helloyunho); S1 integration write-up (cantcs) | Utils repo created 2023-03-17; integration README date unknown | `S5W_M` Android 4.4.2 | US 2023 Palisade named; pre-/post-October 2023 split | PC, vendor-specified removable media, official firmware; vendor update acceptance surface | B | L3 | Vendor firmware recovery; later builds reportedly differ | UI-agent check tightened October 2023; another update stage reported weaker; platform mismatch for published AU S5W_L family |
| M4 | Android Gen5W debugging transport and persistent-privilege outcomes | S1 repository | Unknown | `S5W_M` Android 4.4.2 | Older Telechips generation for the session-scoped claim; newer generation named by S9 for AVNT | PC, local debugging transport, vendor debugging support | B | L2-L4 | Vendor-defined restore; brick risk | Chipset-specific; no Ioniq 5 confirmation; platform mismatch for published AU S5W_L family |
| M5 | Linux Gen5W navigation-application replacement | S3 repository | 2022-02-14 | `S5W_L` Linux/mango | Older unpatched navigation application; EU units | Engineering mode, removable media with official update, physical access | B | L3 | "Reinstall your OS"; official update overwrites the modification | Platform-matched to published AU S5W_L family; author reports newer builds hide the update page and suggests a downgrade, unverified on AU 260319 |
| M6 | Linux Gen5W OTA decryption and patched rootfs persistence | S4, S5 repositories; S11 analysis | 2022-02-14 / 2026-06-30 | `S5W_L` Linux/mango | `S5W_L` builds incl. 251204/260128 | Device-extracted decryptor and key; decrypted rootfs; prior M5 execution | B / C | L3-L4 | Persists across official OTA via unencrypted-update flag | Active tooling; S11's validation is synthetic, not a car run |
| M7 | Linux Gen5W Wi-Fi + SSH session | S6 repository | 2022-02-24 | `S5W_L` Linux | Session-based; no fixed version | Prior M5 replacement execution; network credentials | C | L2 | None; session only | Repository exists; session steps marked TBA |
| M8 | Chimaera academic exploit against Gen5W_L | S7 paper; S12 CVEs | 2024-05-08 paper; CVEs 2023-04-27 | Gen5W_L (LGE) | `AE_E_PE_EUR.S5W_L001.001.211214`; EUR | Offline RE + head unit; patched installers | A | L4 | Not stated | CVEs published; fixed-build status unknown |
| M9 | NEMESIS DSP OTA helper root | S9 repository; S18 announcement | 2026-09-27 announcement | Gen5W AVNT, Android 4.4.2, TCC803x | Kia EV6 2022-24; firmware 260507 exercised | Engineering mode, removable media, DSP update page | B | L3 | Supported wipe; stock system image flash | Released; tested on 260507; platform mismatch for published AU S5W_L family |
| M10 | Gen5 (iAVN) engineering-surface and unauthenticated service weaknesses | S19 paper; S20 CVE | 2022-05-25 paper; CVE 2020-02-03 | Gen5 iAVN Android 4.2.2 | Kia CEED `CD.EUR.SOP.003.30.180703`; other Gen5 builds | Engineering surface; application installation; reachable system service | A | L3 | Not stated | Historical; not Gen5W |
| M11 | Gen5 offline package modification and vendor recovery deployment | S21 blog, S22 repository | 2022-08-12 | Gen5 Android | Hyundai Tucson 2020 EU; cross-region flash noted | Official update archive, offline analysis tooling, vendor recovery capability | B | L4 | Vendor recovery deployment; brick risk | Historical; not Gen5W |
| M12 | D-Audio2V update-archive protection and offline image analysis | S23 blog | 2022-05-22 | D-Audio2V (not Gen5W) | 2021 Hyundai Ioniq SEL, US | Vendor published source; protected update archive | B | L4 | Waited for an official update | Historical; not Gen5W |
| M13 | Commercial Gen5W customware / localization | S29 vendor page | Page current 2026 | `S5W_M` primarily; `S5W_L` listed | KOR/USA/MES S5W_M; `S5W_L` regional | Purchase; compatibility check | C | L3 | Vendor warranty | Commercial, not published RE |
| M14 | ccNC root claims | S18, S27, S28 anecdotes | 2025-2026 | ccNC (Tegra X2, Linux/Qt) | Builds before Dec 2025 | USB file; engineering/dealer mode | D | L3 | Head-unit replacement | Separate platform; patched; not Gen5W |

---

## 4. Method profiles

### M1. Official updater and offline package analysis

**What it establishes.** Hyundai's official path is a PC updater that selects
a model and region, downloads a multi-gigabyte package, and writes it to USB;
the vehicle then validates and installs it from the Settings version screen
(S13, S14). The Australian guide names "Standard Gen5W Navigation" explicitly
and uses the Settings > General > Version info/Update path (S13).

**2026 Linux precedent.** Neukirchen documents `nudl`, a third-party Linux
client that lists and downloads the same official payloads (S16, S17). His EV6
MY22 example resolves to `CV_E.EUR.S5W_L.001.001.260128`, a `S5W_L` build, and
the USB root contains `.lge.upgrade.xml`, `.whatsnew.tar.gz`, `AppUpgrade`,
`<model>.ver`, and `HU/`. He notes that the contents are encrypted and that
the car re-checks integrity before installation.

**Why it matters for T3.** This is the L0 baseline: package acquisition and
static structure can be studied without touching the car. It also shows that
the official channel is still live for Gen5W in 2026; the July 2026 European
infotainment notice is on Hyundai's home page (S15).

**Evidence grade: B/C.** Official vendor documentation supports the existence
of the updater and its vehicle-side install screen, but this report reserves A
for peer-reviewed or CVE-backed work. The claim that the EV6 EU package layout
and encryption behaviour describe the Australian Ioniq 5 rests on an
explanatory blog plus a third-party downloader, so the method row is graded
B/C. The EV6 EU layout is an analogy until T2 observes the AU `260319`
package; T1 confirms the family identity but explicitly did not download or
inspect a package (S30).

**Media and map parsers.** The Linux Gen5W packages expose a substantial
static-analysis surface that is not itself a code-execution entry: laralbir
documents HERE HAF map containers, a SQLite speed-limit database, voice
resource archives, and unencrypted Renesas RL78 front-panel firmware (S8).
Those artifacts matter for understanding the unit and for validating a package
offline, but no public source shows a media or map parser being used to gain
code execution on Gen5W.

**Limit.** Downloading and parsing does not yield plaintext on `S5W_L`; the
payloads remain encrypted (S16). Decryption requires device-derived material
(M6) or a vulnerability in the decryptor (M8).

### M2. Engineering, dealer, and service modes

**What is claimed.** Oviradio's September 2026 update catalogues entry
gestures and rotating passcodes for ccNC, Standard Gen5W `S5W`, and D2V, and
distinguishes dealer mode from full engineering mode (S10). laralbir's June
2026 analysis adds a code-level distinction for `S5W_L`: the engineering-mode
QML checks a `checkSOPVersion()` gate before the PIN keypad, and a
`MASS_PRODUCT` build never satisfies it; the document claims firmware older
than November 2021 lacks that gate (S11, `docs/engineering_mode.md`).

**Observed menu content.** The Android-family engineering mode is reported to
expose test menus, a debugging-connection option, platform settings, and an
application list (S10). The Linux `S5W_L` engineering UI is Qt/QML and includes
a navigation configuration page relevant to M5 (S3, S11).

**Assessment.** Engineering mode is a real, repeatedly documented surface, but
it is not a uniform capability. Gesture, passcode, and gating differ by
platform, model, and build; passcodes rotate and old values stop working
(S10; forum reports). It grants L1 access only. It is a prerequisite for M5
and M9; M6 depends on prior M5 execution. The M3 entry itself uses the
vendor's ordinary update acceptance surface rather than engineering mode (S1),
and the sources describe engineering mode for that method only as an optional
later-stage surface. It is also not a prerequisite for M8, which starts from
offline firmware analysis.

**Unresolved.** The laralbir SOP-gate claim is single-source and conflicts with
Oviradio's claim that current Gen5W passcodes work on 250604/251204/260128
(S10 vs S11). The two may describe different menus (dealer vs full engineering)
or different variants. No primary vendor document resolves it.

### M3. Android Gen5W update-component validation gap

**Structure (category level).** The Android Gen5W package is a set of
top-level archives plus a hash list and an RSA signature over that list. The
hash list is obfuscated rather than cryptographically protected in isolation.
The navigation payload is encrypted with material the community recovered from
the update agent, and the update replaces the navigation application component
(S1, S2). Container and member names are not reproduced here.

**Trust failure.** The sources report that the UI-side update agent did not
consistently bind the RSA-signed hash list to every archive it consumed, so an
archive inconsistent with the signed manifest could pass validation in at
least one stage of the update flow (S1, S2). The October 2023 UI-agent builds
added a check that rejected that inconsistency, but the sources report a
different update stage as weaker afterwards and describe the two build
generations as behaving differently (S1). This catalogue records the trust
failure and its date boundary; the differing acceptance behaviour is not
described here.

**Consequence.** Code supplied in place of a signed component runs with that
component's privileges when the application starts (S1, S2). This is L3
because the installed application payload on the unit is replaced.

**Prerequisites (category level).** Physical access, a PC, vendor-specified
removable media, an official firmware package, and a build whose update agent
accepts a payload inconsistent with its signed manifest (S1).

**Risks and recovery uncertainty.** Vendor firmware recovery is the reported
route (S1). No independent validation exists on an Ioniq 5, and the source
does not establish that this recovery returns the unit to a clean stock state.

**Applicability.** `S5W_M` only. It does not describe the `S5W_L` Linux update
format or the LG decryptor. No Ioniq 5 run is documented in these sources.

### M4. Android Gen5W debugging transport and persistent-privilege outcomes

**What it establishes (category level).** The published work describes a
second and separable weakness in the same unit family: the unit exposes an
unauthenticated debugging interface that the authors reach without credentials,
and the work distinguishes privilege that ends with the session from privilege
that survives a restart (S1). The NEMESIS technical record identifies the
current Gen5W AVNT target as a different Telechips generation (S9), so the
older claims do not automatically transfer. Transport details, tool names, and
the mechanism used for persistence are not reproduced here.

**Availability side effect.** The sources report that the unit's local
host-side functions become unavailable while the debugging interface is
engaged (S1). This is a recovery and availability constraint, not a security
claim.

**Assessment.** B-level, device-tested by the author, but chipset-specific and
not replicated on an Ioniq 5. The persistent-privilege stage carries an
explicit brick risk in the source (S1).

### M5. Linux Gen5W navigation-application replacement

**Chain structure (category level).** The g4933 project substitutes a
community-built navigation component for the vendor navigation application
through an engineering-mode update page that consumes a package from removable
media (S3). The published design gives that component script execution from
the update media, and the vendor navigation application is then patched to
invoke the replacement and continue normal navigation (S3). This section
records only the trust boundary and its consequences: it deliberately omits
the menu path, component names, media layout, and the order of modification
steps.

**Prerequisites and gating.** Removable media formatted as the vendor update
path requires, official update files, engineering-mode access, and an older
navigation application that still exposes the update page. The repository's
author reports that newer builds show the feature as unavailable and suggests
installing an older build as a workaround (S3). That is the author's reported
workaround, not a verified path on the Australian `260319` family; Hyundai
Australia's updater also states that official updates cannot be reverted
(S30), so downgrade feasibility is unresolved.

**Recovery claims.** The author states that reinstalling the operating system
removes the modification and that a subsequent official update overwrites it
(S3). The source does not define what that reinstall means at the partition
level, so recovery is not proven to be a clean stock restore.

**Applicability.** Platform-matched to the published Australian `S5W_L`
family (S30). The same design is the published route to device-derived
decryption material used by M6; no key material or capture method is
reproduced. Whether the car's installed build exposes the navigation-update
page and accepts the replacement is unobserved.

### M6. Linux Gen5W OTA decryption and rootfs patching

**Chain structure (category level).** The `wideopen`/`gen5w` group publishes a
decryption component that consumes material extracted from the unit, plus a
patcher for the installed root filesystem (S4, S5). The patcher relies on a
persistent configuration flag that causes the vendor installer to accept an
update without encryption; the repository states this explicitly (S5). That is
a durable trust failure: once the flag exists, the update path no longer
requires encrypted payloads. Component names, file names, flag identifiers,
and the procedure that obtains the unit material are not reproduced here.

**Persistence.** Because the patched root filesystem is installed through the
normal update path, the modification can survive later OTA updates; the source
presents this as the intended benefit (S5). laralbir's analysis describes the
same chain at the same category level (S11).

**Evidence limits.** The decryptor cannot ship keys and requires them from the
physical unit (S4). laralbir's 2026 validation is explicitly a synthetic
dry-run: stub decryptor, dummy key, synthetic rootfs, and no real HU. Their own
document says real decrypted rootfs and real keys remain blocked (S11,
`docs/gen5w_exploit_ecosystem.md`, sections "Validacion practica" and "Que
sigue bloqueado").

**Recovery claims.** None are proven beyond reinstalling an official update.
The flag and patched rootfs are persistent; a stock reflash is the only
published removal path, and its completeness is unverified.

### M7. Linux Gen5W Wi-Fi and SSH

**What exists.** The g4933 network-shell component is intended to enable
Wi-Fi and SSH "on a session by session basis" (S6). It requires network
credentials to be supplied when the component is built, and it produces a
removable-media package that is consumed by the already-installed M5
replacement mechanism.

**Evidence limit.** The repository's "How to SSH into your car" section is
marked TBA (S6). This is therefore a credible post-exploitation component, not
a demonstrated standalone SSH entry path. It also requires M5 first.

**Related negative result.** greenluigi's D-Audio2V work found that the
engineering-mode network debugging option did not open a usable port, that a USB
Ethernet adapter only exposed CarPlay/Android Auto services, and that Wi-Fi
access yielded the same limited services (S23). That is not Gen5W, but it is a
useful warning against treating an engineering-menu network toggle as an
entry primitive.

### M8. Chimaera (peer-reviewed Gen5W_L exploit)

**Chain structure.** Costantino, De Vincenzi, and Matteucci analysed a Gen5W_L
unit running `AE_E_PE_EUR.S5W_L001.001.211214` (EUR, LG firmware, Infinity
96560-G7230VC8). They report a `printf` vulnerability in a statically linked
mbedTLS routine inside the decryption binary, which leaks the AES key and IV
from memory (S7; CVE-2023-26243). They then patched the installer components
to bypass signature and version checks (CVE-2023-26244, -26245, -26246) and
installed custom firmware (S7, S12).

**Post-exploitation claim.** The paper states that the resulting control
allows CAN frames to be injected into M-bus, B-bus, and C-bus, for example by
triggering services the way the telematics app does, and that this is possible
through a one-day navigation-application exploit or through custom firmware
(S7). This is a claim in a peer-reviewed paper, not an independently
replicated result in this task.

**Evidence strength.** A: peer-reviewed, named version, four CVEs, and a
public report. The caveats are also explicit: the work targets one LG Gen5W_L
build and the authors say procedures may vary significantly on other IVIs
(S7).

**Engineering-mode scope.** The published Chimaera chain starts from offline
firmware analysis and a modified installation; engineering mode is not part of
its stated prerequisites (S7).

**Current status.** The CVEs were published on 2023-04-27. No vendor patch
matrix or fixed-version statement was found. Whether 2021 Ioniq 5 AU firmware
contains the same decryptor and installer behaviour is unknown.

### M9. NEMESIS DSP OTA helper (2026)

**Chain structure (category level).** NEMESIS targets Gen5W AVNT units with
OTA support, identified in the technical record as Android 4.4.2 on Telechips
TCC803x, with firmware family 260507 exercised (S9). The documented entry is
an engineering-mode DSP update page that consumes an OTA package from
removable media. The update agent extracts an archive and executes an unsigned
helper as uid 0 before it validates the signed OTA metadata, and the source
records a terminal installation error at that stage (S9). The installer then
writes a persistent command-line/management pair and boot-time hooks (S9).
This section omits the menu sequence, archive and member names, error code,
and any ordered bootstrap steps.

**Trust failure.** Execution precedes signature validation, and the helper is
not covered by the signed metadata. The author also notes that the process
runs with init-class root and can remount the system partition read-write
during the OTA window (S9).

**Recovery claims.** The supported removal is the tool's own wipe, which
removes the persistent command-line component, installed app, boot hooks, and
data; a vendor factory image also removes it (S9). The author claims
stock applications, the launcher, and engineering mode are not modified (S9).

**Publication date.** The public announcement is a Reddit post created
2026-09-27T16:12:27Z linking the repository (S18). The repository itself has
no readable creation timestamp through the accessible interfaces; treat
2026-09-27 as the first public evidence date, not necessarily the first commit.

**Applicability.** This is the most current Gen5W root claim, but it targets
Android Gen5W AVNT (Menaco's `S5W_M`). The published Australian family is
`S5W_L` Linux, so NEMESIS is a platform mismatch for that family. It remains
relevant only if the car's installed hardware is shown to differ from the
published family; that is unobserved. The repository's "with OTA update
support" wording also does not establish that an early 2021 vehicle has the
DSP update page.

### M10. Gen5 iAVN (older generation, not Gen5W)

**What it establishes (category level).** Costantino and Matteucci reversed a
Kia CEED Gen5 iAVN running Android 4.2.2 (`CD.EUR.SOP.003.30.180703`). Their
work combines two separable weaknesses: an engineering surface whose gating
was insufficient to prevent installation of a third-party application, and a
system service that accepted commands from that application without adequate
authorization, reaching the unit's microcontroller bus. The result is
CVE-2020-8539 and the accompanying public proof of concept (S19, S20). Menu
paths, package and service names, and the command mechanism are not reproduced
here.

**Why it is in this catalogue.** It is the clearest public example of a
combined "weakly gated application install plus unauthenticated service
command" class in the Hyundai/Kia head-unit lineage. It is also a common
source of confusion: Gen5 is not Gen5W, its Android version and package format
differ, and its engineering-menu behaviour does not transfer.

### M11. Gen5 `gen5fw` (older generation, not Gen5W)

**What it establishes (category level).** Gerganov's Gen5 work is the canonical
precedent for offline modification of a vendor update archive whose modified
result is accepted by the unit's own recovery capability (S21, S22). The
archive's protection was a legacy scheme the author defeated offline; the
modified system exposed the unit's debugging interface and granted elevated
privilege (S21, S22). Archive and member names, the content changed, the
re-protection step, and the recovery procedure are deliberately not
reproduced: they are Gen5-only and are the most commonly misapplied material
in this area.

**Why it is in this catalogue.** It is the canonical precedent for an
offline-modified vendor package accepted by the unit's own recovery
capability, and it shows why Gen5-era material must not be applied to Gen5W.
The Gen5W Android package uses a different container and encryption design
with per-model material (S1).

### M12. D-Audio2V (not Gen5W)

**What it establishes (category level).** greenluigi reversed a 2021 Ioniq SEL
with the non-navigation D-Audio2V unit. The update archive's protection was
defeated offline using material obtainable from the vendor's own published
sources, and an offline-produced firmware image was described (S23). Network
paths were dead ends: the engineering-mode network debugging option opened
nothing usable, a wired network adapter exposed only phone-projection
services, and Wi-Fi yielded the same (S23).

**Why it is in this catalogue.** It is a useful negative control for
"engineering mode exposes a network service" assumptions, and it is a reminder
that an Ioniq badge does not imply Gen5W.

### M13. Commercial customware

Menaco sells Gen5W customware for `S5W_M` Korean/American/Middle East units,
advertising app installation, localization, video-in-motion, and navigation
changes; it also lists `S5W_L` models (S29). This is a commercial L3 service,
not published reverse-engineering evidence. It is included because owners
often encounter it as an alternative to self-research, and because it confirms
that the `S5W_M` Android branch is the one with third-party app installation.

### M14. ccNC (different platform)

The 2025 refresh generation is reported to have moved to ccNC, a different
platform. Public 2026 anecdotes describe a Tegra X2, Linux/Qt stack, a
USB-file root path, and a patch around December 2025 (S18, S27, S28). None of
this applies to Gen5W: the operating system, update format, and recovery
model differ. It is included only to prevent conflation in later planning.

---

## 5. Advisories and CVEs

| CVE | Published | Affected product/version | Claimed weakness | CVSS | Exploit status |
|---|---|---|---|---|---|
| CVE-2020-8539 | 2020-02-03 record | Kia head unit `SOP.003.30.18.0703`, `SOP.005.7.181019`, `SOP.007.1.191209` (Gen5 iAVN) | A head-unit controller daemon accepts unauthorized commands | High (NVD/Rapid7) | Public proof of concept published with the 2022 paper |
| CVE-2023-26243 | 2023-04-27 | Hyundai Gen5W_L `AE_E_PE_EUR.S5W_L001.001.211214` | Memory-handling defect in the decryption component discloses key material | 7.8 | CISA SSVC: proof-of-concept, not automatable, total technical impact |
| CVE-2023-26244 | 2023-04-27 | Same | An update client component can be modified to bypass the digital-signature check applied to update components and their manifest | 7.8 | CISA SSVC: proof-of-concept, not automatable |
| CVE-2023-26245 | 2023-04-27 | Same | An update component can be modified to bypass the version check, allowing any firmware version | 7.8 | CISA SSVC: proof-of-concept, not automatable |
| CVE-2023-26246 | 2023-04-27 | Same | An update component can be modified to bypass the digital-signature check | 7.8 | CISA SSVC: no known exploitation, not automatable |

All four 2023 CVEs were assigned by MITRE and published on 2023-04-27. The
public references point to the CNR-IIT CHIMAERA report and the SOwhat lab
project (S12). No Hyundai or Kia security-advisory page for these CVEs was
found; NVD, MITRE, CISA ADP, GitHub Advisory, ENISA EUVD, and the paper are the
available records.

---

## 6. Contradictions

1. **One name, two stacks.** Community posts say "Gen5W" for Android 4.4.2
   `S5W_M` and for Linux `S5W_L` without always stating which. Cantcs says
   Gen5W can be Android or Linux (S1); Menaco maps `S5W_M` to Mobis Android
   and `S5W_L` to LG Linux (S29). Any claim that "Gen5W is rooted by method X"
   is ambiguous until the firmware string and OS are known.

2. **Whether the update signature check is fixed.** Cantcs says the UI agent
   was fixed in October 2023 but a different update stage was reported to
   remain weaker (S1). The 2024 Chimaera paper describes bypassing the
   installer checks on the 211214 build (S7). NEMESIS in 2026 finds a
   different component (DSP OTA helper) executing before validation (S9).
   These can all be true of different components and builds, but they are
   often summarized as a single "patched/unpatched" claim, which is wrong.

3. **Engineering-mode accessibility.** Oviradio states that current Gen5W
   passcodes work for the 250604, 251204, and 260128 EUR versions (S10).
   laralbir states that `S5W_L` `MASS_PRODUCT` builds since roughly November
   2021 fail a separate SOP check before the PIN pad and cannot enter
   engineering mode without a rootfs patch (S11). Possible explanations:
   different menus (dealer vs full engineering), different variants
   (`S5W_M` vs `S5W_L`), or a single-source error. Unresolved.

4. **"The Linux one has not been hacked."** greenluigi wrote in 2022 that the
   Linux IVI had not been hacked (S23), while the g4933 Linux Gen5W chain was
   created in February 2022 (S3-S6). The statement was probably true for the
   D-Audio2V Linux unit he owned, not for `S5W_L`. This is a scope error, not
   a factual contradiction.

5. **"Unpatched" root claims.** The 2026 NEMESIS announcement and Reddit
   discussion describe the Gen5W root path as currently working (S18). A
   separate ccNC discussion says ccNC was patched around November-December
   2025 and that "all other countries" were fixed earlier (S27). Those
   statements are about ccNC, not Gen5W, but they are frequently mixed
   together. Gen5W's patch state after 260507 is unknown.

6. **Recovery.** The M5 project says "reinstall your OS" (S3); NEMESIS says
   its own wipe plus a vendor factory image removes it (S9); the Gen5 work
   describes vendor recovery deployment (S21, S22). None of these sources
   proves a clean stock restore on a 2021 Ioniq 5, and none defines whether
   the unit's recovery-related state or boot chain was altered.

7. **PIN values.** Laralbir says Standard Gen5W uses a short fixed PIN and
   Premium AVNT uses an eight-digit rotating PIN (S11); Oviradio lists a
   dealer-mode PIN and a rotating set for full engineering mode (S10). They
   may both be right about different menus, but the sources do not reconcile
   the terminology.

8. **Downgrade workaround vs vendor no-revert.** The M5 project's author
   reports that newer builds hide the navigation-update page and suggests a downgrade
   (S3). Hyundai Australia's updater states that after installation it is not
   possible to revert to the previous software version (S30). These may refer
   to different mechanisms (installing an older package versus a supported
   rollback), but no source demonstrates a successful downgrade on the AU
   `260319` family. Unresolved.

---

## 7. Bounded negative searches

These are searches that returned no credible public evidence, not proof of
absence. Queries were run on 2026-10-18 through the research search service;
results were opened where a candidate existed.

1. **Vendor security advisory for the 2023 Gen5W CVEs.** Searches for a
   Hyundai/Kia PSIRT or security-bulletin page referencing CVE-2023-26243,
   -26244, -26245, or -26246 returned only NVD, MITRE, CISA ADP, GitHub
   Advisory, ENISA EUVD, INCIBE, and the CNR-IIT paper. No vendor advisory was
   found.

2. **Gen5W browser/WebView remote exploit.** Searches combining Gen5W with
   browser, WebView, Chromium, or "hidden browser" returned Gen5 (iAVN) and
   D-Audio2V material, plus generic Android WebView documentation. No
   credible Gen5W browser exploit was found. The only browser-reachable
   install surface in the record belongs to Gen5 iAVN (S19).

3. **Unauthenticated Gen5W network entry.** Searches for Gen5W SSH, Telnet,
   Wi-Fi debugging, and open-port scanning returned the g4933 network-shell
   component, which requires prior code execution (S6), and greenluigi's
   negative D-Audio2V results (S23). No unauthenticated network entry was
   found.

4. **Gen5W OTA server or cloud compromise.** No public source was found that
   demonstrates modification of the official update server, a malicious
   official payload, or a server-side compromise. The published chains are
   local-package or local-device attacks.

5. **A 2026 root tool validated on a 2021 Ioniq 5.** NEMESIS is validated on
   an EV6 Gen5W AVNT running firmware 260507 (S9). No source was found that
   demonstrates it on a 2021 Ioniq 5. It targets Android Gen5W AVNT
   (`S5W_M`), which is a platform mismatch for the published Australian
   `S5W_L` family (S30).

6. **Post-2023 CVE for Gen5W.** Bounded searches for later Gen5W CVEs did not
   surface any beyond the 2023 set and unrelated automotive CVEs. This is a
   bounded search, not a statement that no later CVE exists.

7. **A public, complete SSH procedure.** The `wifi-ssh` README stops at "How
   to SSH into your car: TBA" (S6). No public end-to-end Gen5W SSH procedure
   was found; the component exists, the access claim is incomplete.

8. **A public AU `260319` package observation.** Bounded searches did not find
   a public write-up that observes the Australian
   `NE_E.AUS.S5W_L.001.001.260319` package. The Linux layout is inferred from
   EU/mango work (S3-S5, S16) and the AU identity from T1 (S30); T2 has not
   yet observed the actual package.

---

## 8. Applicability to the published Australian family and the user's car

**Published identity (accepted T1 dependency).**

- Hyundai Australia publishes the 2021-23 IONIQ 5 (NE1) as Standard Gen5W,
  model `NEAE.S5BLN.AAU`, current software
  `NE_E.AUS.S5W_L.001.001.260319`, map `AUS.19.41.47.011.611.0` (S30).
- The `S5W_L` token and Menaco's classification put that published family on
  the LG Linux stack; the g4933 and Chimaera chains use matching on-device
  decryption and installer components rather than the Android package format
  (S3-S5, S7, S29).
- This is publication-level identity. T1 did not download a package, inspect
  an image, or observe the car (S30).

**Platform match.**

- M5 (navigation-application replacement), M6 (decryptor/patcher), M7 (post-exploitation
  SSH), and M8 (Chimaera) are platform-matched to the published `S5W_L`
  family. M8 is additionally version-specific to
  `AE_E_PE_EUR.S5W_L001.001.211214`; the AU `260319` build may differ.
- M1's EV6 EU package layout is an analogy, not an observation of the AU
  package. T2 has not yet observed `260319`; do not treat the EV6 layout as
  an AU layout.
- M3, M4, and M9 target Android Gen5W (`S5W_M`) and are a platform mismatch
  for the published `S5W_L` family. They would become relevant only if the
  car's installed hardware is shown to be a different variant.

**The user's car (unobserved).**

- Installed software may differ from `260319` because of dealer, OTA, or
  regional staging; the car's Software line is the installed truth (S30).
- Hardware part number, supplier, and board revision are unknown (S30).
- Engineering-mode reachability, the navigation-update page, an
  unencrypted-update configuration flag, and the installed build's patch state
  are all unobserved.

**Unknowns to close before selecting a method.**

- Installed software version and hardware revision.
- Engineering-mode reachability on the installed build.
- Navigation-update page presence and enablement.
- Presence of an unencrypted-update configuration flag in the installed
  vendor installer.
- Patch state relative to the 2023 CVEs and the 2026 Android release.
- T2's observation of the AU `260319` package layout, decryptor, and
  installer behaviour.
- Whether Hyundai's no-revert rule (S30) blocks the author-reported downgrade
  workaround.

No method in this document is confirmed for the car until its installed
software and hardware are read.

---

## 9. Observations, inference, and unknowns register

| ID | Class | Statement | Basis |
|---|---|---|---|
| O1 | OBS | "Gen5W" covers both `S5W_M` Android and `S5W_L` Linux. | S1, S29 |
| O2 | OBS | 2021 Ioniq 5 units in Europe report `S5W_L` build strings; a 2021 Kona report is consistent with the same branch. | S24-S26 |
| O3 | OBS | Hyundai AU/EU list the Ioniq 5 as Standard Gen5W. | S13, S14, S30 |
| O4 | OBS | The Android Gen5W chain relies on an update-component validation gap in the vendor update agent. | S1, S2 |
| O5 | OBS | The Linux Gen5W chain relies on navigation-application replacement and device-extracted decryption material. | S3, S4 |
| O6 | OBS | Chimaera is peer-reviewed and maps to four 2023 CVEs on build 211214. | S7, S12 |
| O7 | OBS | NEMESIS executes an unsigned DSP OTA helper as root before signature validation on firmware 260507. | S9 |
| O8 | OBS | Official Gen5W updates were still published in July 2026. | S15, S16 |
| O9 | OBS | The published AU 2021-23 IONIQ 5 family is Standard Gen5W, model `NEAE.S5BLN.AAU`, software `NE_E.AUS.S5W_L.001.001.260319`. | S30 |
| I1 | INF | The published AU family is `S5W_L` Linux, so M5/M6/M7/M8 are platform-matched; the car's installed version remains unobserved. | O1-O3, O9, S29, S16 |
| I2 | INF | M3/M4/M9 are a platform mismatch for the published AU `S5W_L` family; they remain relevant only if the installed hardware differs. | O1, O4, O9, S9 |
| I3 | INF | Engineering mode is required for M5 and M9 (and M6 via M5). The M3 entry uses the vendor's ordinary update acceptance surface; the sources describe engineering mode for that method only as an optional later-stage surface. It is also not a prerequisite for M8. | M2, M3, M5, M8, M9 |
| I4 | INF | Recovery claims are weaker than entry claims across the record; none is proven on an Ioniq 5. | M3-M9 |
| U1 | UNK | The user's installed software version and hardware revision; the published AU family is known. | S30 |
| U2 | UNK | Whether engineering mode is reachable on the installed build. | S10 vs S11 |
| U3 | UNK | Whether the navigation-update page exists and is enabled on the installed build. | S3 |
| U4 | UNK | Whether an unencrypted-update configuration flag exists in the installed build's vendor installer. | S5 |
| U5 | UNK | Patch state of the installed build relative to the 2023 CVEs and the 2026 DSP path. | No vendor matrix |
| U6 | UNK | Whether the installed hardware differs from the published `S5W_L` family, which would be the only route to NEMESIS relevance. | S9 only tests EV6 |
| U7 | UNK | Whether T2 confirms the AU `260319` package layout, decryptor, and installer behaviour. | T2 pending |

---

## 10. Sources

All URLs accessed 2026-10-18. Types: P = primary research/paper,
R = primary author repository, A = advisory/CVE record, O = official vendor,
S = secondary/commercial, N = anecdote/forum, I = internal accepted evidence
artifact.

Evidence classes are separated as follows. Primary research: S7, S19.
Primary author repositories: S1-S6, S8, S9, S17, S22. Advisories and CVE
records: S12, S20. Official vendor material: S13-S15. Secondary, commercial,
or explanatory: S10, S16, S23, S29. Anecdotes: S18, S24-S28. Internal
accepted dependency: S30. The method matrix's strength column uses the A-D
scale from section 2, not these type codes.

| ID | Source | Type | Date | URL |
|---|---|---|---|---|
| S1 | cantcs, "Reverse Engineering Hyundai/Kia/Genesis Android-based Gen5W Head-Units" | R | README date unknown; references October 2023 change | https://github.com/cantcs/HKG_Gen5W_ReverseEngineer |
| S2 | Helloyunho, `gen5w-utils` | R | Repository created 2023-03-17 (ecosyste.ms index) | https://github.com/Helloyunho/gen5w-utils |
| S3 | g4933, Linux Gen5W navigation-replacement project | R | Project created 2022-02-14 | https://gitlab.com/g4933/gen5w/navi_extended |
| S4 | g4933, `update_decryptor` | R | Group created 2022-02-14; project date not separately verified | https://gitlab.com/g4933/gen5w/update_decryptor |
| S5 | g4933, root-filesystem patch project | R | Group created 2022-02-14; project date not separately verified | https://gitlab.com/g4933/gen5w/update-patcher |
| S6 | g4933, network-shell component | R | Project created 2022-02-24 | https://gitlab.com/g4933/gen5w/main-loops/wifi-ssh |
| S7 | Costantino, De Vincenzi, Matteucci, "A vehicle firmware security vulnerability: an IVI exploitation" | P | Published 2024-05-08 | https://link.springer.com/article/10.1007/s11416-024-00522-4 |
| S8 | laralbir, "Hyundai/Kia Standard Gen5W navigation firmware" | R | Analysis docs dated 2026-06-30; firmware build 2025-12-04 | https://github.com/laralbir/hyundai-kia-gen5w-navi-firmware |
| S9 | xwtk, `hmg_nemesis` | R | Public announcement 2026-09-27; tested firmware 260507 | https://github.com/xwtk/hmg_nemesis |
| S10 | Oviradio, engineering/dealer mode reference | S | Page dated 2026-10-01; "September 2026 update" | https://www.oviradio.cz/hyundai-kia-radio-engineering-mode-en/ |
| S11 | laralbir, engineering-mode analysis | R | 2026-06-30 | https://raw.githubusercontent.com/laralbir/hyundai-kia-gen5w-navi-firmware/main/docs/engineering_mode.md |
| S12 | CVE records for CVE-2023-26243/-44/-45/-46 | A | Published 2023-04-27 | https://github.com/advisories/GHSA-68w8-q32v-4g44 ; https://raw.githubusercontent.com/cisagov/vulnrichment/develop/2023/26xxx/CVE-2023-26244.json ; https://raw.githubusercontent.com/cisagov/vulnrichment/develop/2023/26xxx/CVE-2023-26245.json ; https://github.com/advisories/GHSA-89xv-gh3p-mrvg |
| S13 | Hyundai Australia, Navigation Updater update guide | O | Copyright 2024; page current | https://update.hyundai.com/AU/EN/updateGuide/04 |
| S14 | Hyundai Europe, Standard Gen5W OTA notice for IONIQ 5 | O | 2022-04-05 | https://update.hyundai.com/EU/EN/updateNoticeView/Y2VEDk |
| S15 | Hyundai Europe, update home page | O | 2026-07-22 notice listed | https://update.hyundai.com/EU/EN/home |
| S16 | H. Neukirchen, "HMG head unit firmware updates on Linux using nudl" | S | 2026-10-15 | https://uni.hi.is/helmut/2026/10/15/hmg-hyundai-kia-genesis-firmware-updates-on-linux-using-nudl-tool/ |
| S17 | chenxiaolong, `nudl` | R | Accessed 2026-10-18 | https://github.com/chenxiaolong/nudl |
| S18 | r/Ioniq5, "Gen5W head unit root tool released" | N | Created 2026-09-27T16:12:27Z | https://www.reddit.com/r/Ioniq5/comments/1wro6yt/gen5w_head_unit_root_tool_released/ |
| S19 | Costantino, Matteucci, "Reversing Kia Motors Head Unit..." | P | Published 2022-05-25 | https://link.springer.com/article/10.1007/s11416-022-00430-5 |
| S20 | CVE-2020-8539 | A | Record 2020-02-03 | https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-8539 |
| S21 | R. Gerganov, "Hacking Hyundai Tucson 2020" | S | 2022-08-12 | https://xakcop.com/post/hyundai-hack/ |
| S22 | rgerganov, `gen5fw` | R | Accessed 2026-10-18 | https://github.com/rgerganov/gen5fw |
| S23 | greenluigi1, "How I Hacked my Car" | S | 2022-05-22 | https://programmingwithstyle.com/posts/howihackedmycar/ |
| S24 | goingelectric.de thread, Ioniq 5 2021 `S5W_L.001.001.210723` | N | 2021 posts | https://www.goingelectric.de/forum/viewtopic.php?amp=true&lang=en&start=260&t=70848 |
| S25 | goingelectric.de thread, `S5W_L.001.001.211029` | N | 2021-11 posts | https://www.goingelectric.de/forum/viewtopic.php?lang=en&p=1722308 |
| S26 | goingelectric.de thread, `S5W_L.001.001.211117` / Kona `S5W_L` | N | 2021-11 posts | https://www.goingelectric.de/forum/viewtopic.php?start=170&t=73115 |
| S27 | r/KiaEV6, CCNC hack thread | N | ~2026-04 (6 months before access) | https://www.reddit.com/r/KiaEV6/comments/1sjy38q/i_too_have_hacked_my_head_unit/ |
| S28 | r/KiaEV6, "EV6 2022-2024 Head Units Root Exploit: hmg_nemesis" | N | ~2026-10 | https://www.reddit.com/r/KiaEV6/comments/1wrnuer/ev6_20222024_head_units_root_exploit_hmg_nemesis/ |
| S29 | Menaco, "GEN5W multimedia update" | S | Page current 2026 | https://menaco.co/gen5w-multimedia-update |
| S30 | T1 accepted identity artifact, "Australian 2021 Hyundai IONIQ 5: identity and official update evidence" | I | 2026-10-18; SHA-256 80d73d8855f2220957e398d6f64469361325454c674284b2e261ad19e2d187be | Live repository: `evidence/identity-and-official-updates.md`; frozen review package: `artifacts/identity-and-official-updates.md` |

---

## 11. Unresolved issues

1. The user's installed software version, hardware revision, and patch state
   remain unobserved. T1's accepted result establishes only the published
   Australian family: `NE_E.AUS.S5W_L.001.001.260319` (S30). Reading the car's
   Software line and hardware is still required.
2. The engineering-mode SOP-gate claim (S11) needs independent corroboration
   or a QML extract from the installed build.
3. No source proves a clean recovery path after the M5 navigation replacement
   or the M6 root-filesystem patch on an Ioniq 5. Recovery claims are author statements, not
   tested restore procedures; the author-reported downgrade workaround (S3)
   also conflicts with the vendor's no-revert statement (S30).
4. The 2023 CVE fixed-version matrix is absent; it is unknown whether AU
   builds after 211214 contain the Chimaera fixes.
5. The 2026 NEMESIS release targets Android Gen5W AVNT (`S5W_M`), a platform
   mismatch for the published AU `S5W_L` family. It would only become relevant
   if the installed hardware is shown to differ; its post-260507 patch state is
   unknown.
6. T2 has not yet observed the AU `260319` package. The EV6 EU layout,
   decryptor, and installer behaviour used in M1/M6 are analogies until that
   observation exists.
7. No public evidence closes the browser/WebView, unauthenticated network, or
   OTA-server questions; these remain bounded negatives rather than proven
   impossibilities.

---

## 12. Revision and integrity

- Revision: 8 (2026-10-19), correction round 7. Provenance-only correction of
  this revision note, applying generation-9 finding DSGR-G9-N2. It corrects
  the attribution recorded here previously: correction round 6 applied the
  generation-8 finding DSV-G8-01 (check C2) and its disposition, and prepared
  revision 7 for generation-9 review. Revision 7 was not itself a
  generation-9 disposition. No method identity, citation, evidence grade,
  platform or version scope, prerequisite class, risk, recovery statement,
  contradiction, bounded negative or applicability statement changed in this
  round.
- Revision: 7 (2026-10-19), correction round 6. Applied the generation-8
  finding DSV-G8-01 (check C2) and its disposition to the T3 method wording,
  preparing revision 7 for generation-9 review. This round's changes, stated
  literally:

  - The M3 matrix prerequisite cell and the M3 profile prerequisite paragraph
    no longer name the Settings screen or a direct host-to-unit connection;
    the profile lists only category-level local prerequisites, and the M3
    structure paragraph says the update replaces the navigation application
    component instead of naming a partition.
  - I3 no longer names the Settings flow and matches the M3 matrix wording.
  - The M3 recovery cell and risks paragraph say "vendor firmware recovery"
    rather than describing an official-firmware reinstall.
  - M4 is retitled "debugging transport and persistent-privilege outcomes" and
    no longer describes a command shell, a boot-image persistence mechanism,
    an earlier-execution dependency, or external restoration of host-side
    functions. It states session-scoped versus restart-surviving privilege as
    an abstract outcome and records that local host-side functions become
    unavailable while the debugging interface is engaged.
  - The M4 matrix row drops the host connection and vendor boot image from its
    prerequisites, uses "vendor-defined restore" as the recovery class, and
    says "session-scoped claim" in place of "temporary-root claim".
  - M11 is retitled "offline package modification and vendor recovery
    deployment". Its matrix prerequisites drop the writable image and the
    recovery-mode install path; its profile and catalogue rationale no longer
    sequence offline modification with recovery installation; its recovery
    cell reads "vendor recovery deployment".
  - M12 is retitled "update-archive protection and offline image analysis".
    Its profile says an offline-produced firmware image was described, and no
    longer says the boot image was reconstructed.
  - M9's recovery paragraph says a vendor factory image rather than a factory
    system image flash; contradiction 6 says vendor recovery deployment and
    refers to the unit's recovery-related state and boot chain without naming
    a recovery partition or reinstall order.

  Method identity at the category level, citations, evidence grade, platform
  and version scope, category prerequisite classes, abstract trust failure,
  consequence class, mutation class, risks, recovery uncertainty,
  contradictions, bounded negatives and applicability were preserved. No
  operational steps or sensitive values were added.
- Revision 6 (2026-10-19), correction round 5. Applied the generation-7
  Council findings ASTRA-G6-01, DSG-G7-01, DSF-G7-01 and DSF-G7-02 to the
  residual bytes that revision 5 described as removed but did not remove.
  This round's changes, stated literally:

  - Section 1's summary of the Android methods now names the update-component
    validation gap instead of a payload hook.
  - M3 is retitled "update-component validation gap". Its trust-failure
    paragraph states the manifest-binding failure and the October 2023
    boundary without describing later-build acceptance behaviour; the
    consequence states only that substituted code runs with the replaced
    component's privileges; the prerequisites and recovery paragraphs drop
    the later-build acceptance description and the secondary device-state
    repairs; the source does not establish a clean stock restore.
  - The M3 matrix row carries matching prerequisites, recovery claim and
    status wording.
  - M4 presents the debugging channel as a second, separable weakness and
    keeps the command-shell, temporary-root and persistent-root outcomes plus
    the externally restored USB-host availability constraint.
  - M10 separates the engineering-surface weakness from the unauthenticated
    service weakness and drops the browser and named-exploit framing.
  - M11 describes a legacy archive-protection scheme and the resulting
    debugging-interface and privileged-shell outcomes without naming the
    scheme or the intermediate privilege mechanics.
  - M12 describes defeated archive protection and offline image
    reconstruction without naming the key source or container format, and
    uses neutral wording for the network negative controls.
  - The M4, M10, M11 and M12 matrix rows were adjusted to match the profile
    wording; the M4 prerequisite cell no longer names debugging drivers.
  - The advisories table no longer names update components, their manifest,
    the decryption routine's key type, or the controller daemon.
  - Contradiction 2 no longer names the stage's archive package;
    contradiction 6 no longer describes a stock boot-image restore.
  - Register entries O4 and I3 and negative-search record 2 were rewritten to
    match the new M3 and M10 wording.

  Method identity, citations, evidence grade, platform and version scope,
  category-level prerequisites, abstract trust failure, consequence, mutation
  class, risks, recovery uncertainty, contradictions, bounded negatives and
  applicability were preserved.
- Revision history: 8 applied DSGR-G9-N2 to this section's provenance wording
  only; 7 applied DSV-G8-01/C2 to M3/M4/M9/M11/M12, the M4 and
  M11 matrix rows and I3; 5 applied ASTRA-G6-01 to M3/M4/M10/M11/M12 and their
  dependants; 4 applied ASTRA-G5-03/DSF-G5-01/DSG-G5-06 to M5/M6/M9; 3
  tightened M3/M2/I3 engineering-mode scope and corrected M1 grading; 2
  reconciled the accepted T1 identity, regraded M1 to B/C, and bounded the M5
  downgrade claim.
- Owner: T3 / community_worker
- Scope: `evidence/community-entry-methods.md` only.
- Artifact path: live repository `evidence/community-entry-methods.md`; frozen
  review package `artifacts/community-entry-methods.md`. Paths inside this
  document are repository-relative, and each dependency is mapped below. No
  absolute path is embedded.
- Accepted dependency: live repository `evidence/identity-and-official-updates.md`;
  frozen review package `artifacts/identity-and-official-updates.md`; both at
  SHA-256 `80d73d8855f2220957e398d6f64469361325454c674284b2e261ad19e2d187be`.
- Excluded by design: passcodes, keys, payloads, commands, frame data, and
  step-by-step vehicle procedures.
- Integrity method: SHA-256 over the exact UTF-8 bytes from the start of this
  file through the last character of the line immediately above this integrity
  line, excluding that line's terminating newline and the final blank line.
  There is no other normalization.
- SHA-256 (body, as defined above): 1f4cbee015752d7153148b04fca433fabebb838d8af55d120ee342a2c641c925

