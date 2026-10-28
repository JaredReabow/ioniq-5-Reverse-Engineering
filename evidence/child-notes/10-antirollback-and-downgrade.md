# Anti-rollback and downgrade feasibility — Standard Gen5W (`S5W_L`, x86-64 Linux)

- Task: anti-rollback / downgrade investigation
- Subject unit: Hyundai/Kia Standard Gen5W, Linux x86-64, build `NE_E.EUR.S5W_L.001.001.260128` (2026-01-28)
- Method: public GitLab/GitHub issue trackers, wikis and READMEs of the
  `g4933` "Gen5 Wide-Open" (`wideopen`) project family; NVD records for the
  CVE-2023-2624x Chimaera set; local prior-art notes in this workspace.
- Constraints honoured: research and analysis only. No exploit code, no
  procedure for modifying a signed package, no device contact. Where a public
  document states a mechanism (e.g. "swap `.lge.upgrade.xml`"), it is reported
  as a *documented finding*, not reproduced as instructions.

## Executive summary

1. The Gen5W_L anti-rollback control is a **single userland version-string
   comparison** performed by `AppSetup` after decrypting the package's
   `.lge.upgrade.xml` with `DecryptToPipe`. The public `wideopen` wiki states
   the gate verbatim: *"It will read the version from the file and then begin
   an upgrade given the version is greater than or equal to the current version
   of the HU."*
2. The check is **per-package, not per-file**. Individual payload archives carry
   CRC-32 entries in the plaintext `.ver` manifest (no version gating and no
   signature), so the manifest's version string is the only rollback gate.
3. The project's own `navi_extended` README documents a **downgrade method that
   works without forging anything**: download an *older* official (still
   encrypted) package, but replace its `.lge.upgrade.xml` with the one from the
   *latest* official package for the same vehicle. The manifest is not
   cryptographically bound to the payload at install time, so the newer version
   string passes the `>=` check while the older payload is written to the
   inactive slot.
4. Consequently a **signed (encrypted) but older official package is installable**
   on the Linux `S5W_L` path, provided it is paired with a same-vehicle
   newer manifest. The Android `Gen5W` sibling is *not* affected the same way:
   its `update_info` is RSA-signed and binds the package (GitLab issue #3 shows
   edited payloads are rejected even with corrected `.ver` CRCs).
5. Once `disableEncryptionUpdate` is present (post-exploit), `AppUpgrade`
   stops decrypting payloads **but still performs the version check via a
   plaintext `.lge.upgrade.xml`** — so the version string becomes fully
   attacker-controlled, making equal-version and "downgrade" installs trivial.
6. Nothing public demonstrates a *monotonic anti-rollback counter* (fuse/OTP) on
   this variant. Rollback protection is software-only and lives in the update
   application, consistent with CVE-2023-26245 ("modified AppUpgrade … bypass
   the version check … newer, older, or customized").

---

## 1. Findings

### 1.1 What is documented publicly about downgrading Gen5W

Primary sources, in order of weight:

- **`wideopen` wiki — `Software/Update_Process`** (the "Gen5 Wide-Open" project,
  `gitlab.com/g4933/wideopen`). This is the page that supplies the task's quote.
  It describes the vanilla install flow and the A/B mechanics in full (see 1.2).
- **`navi_extended` README — F.A.Q.** (`gitlab.com/g4933/gen5w/navi_extended`).
  The "downgrade your HU" advice:
  > *"My Config menu doesn't have 'Update AppNavi from USB', just 'This feature
  > is currently unavailable' — You will need to downgrade your HU, go over to
  > update_fetcher and use the tool to look for an older update for you HU.
  > Copy all of the downgraded files to your usb for the HU but switch out the
  > `.lge.upgrade.xml` file with a version from the latest update available for
  > your vehicle's headunit. Alternatively, you can also try to swap out all the
  > `navi_eu` folder contents with an older (but not too old!) version, that will
  > also re-enable the option to install the hack."*
  Two independent bypasses are implied: (a) manifest substitution (version gate),
  and (b) `navi_eu`/AppNavi content swap (re-enables the hidden "Update AppNavi
  from USB" option, because that option depends on the AppNavi version).
- **`navi_extended` issue #2 — "[Question] How do I downgrade?"** (2022-10-30).
  Reporter tried editing `update.info`; notes a Korean variant has no
  `.lge.upgrade.xml`. Comments are authentication-gated (401); only the issue
  body is public.
- **`navi_extended` issue #3 — "gen5w standard (Ev6) update_info"**
  (2023-09-23). On the **Android** Gen5W (EV6), a signed `update_info` inside
  `system_package` blocks install when system images change, *even after the
  `.ver` CRC and size are corrected*. This is the control the Linux variant
  lacks at the AppSetup stage.
- **Chimaera / CVE-2023-26245** (NVD, published 2023-04-27). On
  `AE_E_PE_EUR.S5W_L001.001.211214` (2021-12-14), a modified `AppUpgrade`
  "bypass[es] the version check in order to install any firmware version
  (e.g., newer, older, or customized)". CVE-2023-26244 / -26246 are the
  signature-check bypasses in `AppDMClient` / `AppUpgrade`; CVE-2023-26243 is
  the AES key/IV leak from the decryption binary.
- **Hyundai official (owner-facing).** `identity-and-official-updates.md`:
  *"After installation, it is not possible to revert to the previous software
  version."* This is a one-way claim from the manufacturer's perspective; the
  community method above is the public exception.

**Which builds it works on:** the `navi_extended` downgrade/entry advice is
scoped to *"an older, unpatched version"* — i.e. builds where Engineering Mode →
Config still exposes "Update AppNavi from USB" (pre-November-2021 SOP gate, per
`engineering_mode.md`; later `MASS_PRODUCT` builds hide the option). The
manifest-swap downgrade itself is a property of the update pipeline and is not
tied to a single build date; it is described against the 2021–2022-era
`S5W_L`/`S5W` (Linux) packages. The Chimaera version-check bypass is pinned to
`211214`. No public source demonstrates any of this against the January-2026
`260128` build; the local prior art (`eu-custom-firmware-feasibility.md`)
treats `260128` as unverified against the whole Chimaera set.

### 1.2 The update flow (from the `wideopen` wiki) and what it implies

Vanilla process, quoted/paraphrased:

1. On USB insertion `AppSetup` looks for `.lge.upgrade.xml` at the USB root,
   decrypts it with `DecryptToPipe` (a binary *outside* `AppUpgrade`), reads
   the version, and proceeds only if `version >= current`.
2. Host `AppUpgrade` copies the USB `AppUpgrade` to `/update/usb/` and hands
   over control.
3. `AppUpgrade` performs Filesystem / Maps / Firmware stages. Filesystem
   archives are checksummed → decrypted → extracted → **copied to an unbooted
   partition** (A/B). Maps go to `/navi/` or `/navi2/` per
   `/update/activeNaviPath` and `/update/activeResourcePath`; the newly
   installed set is always the path *not* named in those files.
4. On completion it updates `activeNaviPath`/`activeResourcePath`, clears
   `/update/` flags, **updates `/etc/fstab/` to boot the new partition**, and
   reboots. The previous partition and navigation directory are left behind so
   a failed update can be survived.

Implications:

- There are **two independent version-ish gates**: the `.lge.upgrade.xml`
  version string (rollback), and the Engineering-Mode SOP/`checkSOPVersion()`
  gate + AppNavi-version-dependent "Update AppNavi from USB" option (entry).
- The rollback gate is *one* comparison in userland. There is no stated
  monotonic counter, no per-file version check, and no bootloader-side
  anti-rollback in the documented flow.

### 1.3 Structure of the version comparison in `.lge.upgrade.xml`

`.lge.upgrade.xml` is an **encrypted opaque envelope** in the official package
(confirmed locally: near-8-bit entropy, no XML magic; in
`official-package-static.md`). No public plaintext example is indexed
(Sourcegraph code search returns 0 hits for the exact string), so the field
layout below is **inference from public examples and the `.ver` header**, not a
decrypted manifest.

The version identity is carried in two related places:

- `.ver` header (plaintext, verified locally):
  `+|{mapVer}|{SWversion}|{brand}|{packageName}|{mcode}|1`
  e.g. `+|22389|NE_E.AUS.S5W_L.001.001.260319|HM|2021_22_IONIQ_5_AU|1227|1`
  (brand `KM`=Kia, `HM`=Hyundai, `GN`=Genesis; confirmed by
  `Helloyunho/gen5w-utils/parse_ver.py`).
- The full software string, which is the value `AppSetup` reads out of the
  decrypted `.lge.upgrade.xml` and compares.

Software-string grammar (from the known examples):

```
<model>.<region>.<platform>.<major>.<minor>.<YYMMDD>
  NE_E . EUR . S5W_L . 001 . 001 . 260128   ← subject unit (IONIQ 5 EU)
  NE_E . AUS . S5W_L . 001 . 001 . 260319   ← AU sibling
  YB_22 . EUR . S5W_L . 001 . 001 . 251204  ← Kia Rio MY22 EU
  AE_E_PE_EUR . S5W_L001 . 001 . 211214     ← Chimaera target (older, looser punctuation)
```

| Segment | Meaning (inferred) | Rollback role |
|---|---|---|
| `model` | vehicle/model family (`NE_E` IONIQ 5, `YB_22` Rio, `AE_E_PE`…) | identity/gating, not ordering |
| `region` | `EUR`, `AUS`, … | region gating |
| `platform` | `S5W_L` = Standard Gen5W | platform gating |
| `major.minor` | release pair (`001.001`) | ordering |
| `YYMMDD` | build date (260128 = 2026-01-28; matches kernel build string) | ordering — lexicographically sortable |

Ordering hypothesis: the `>=` test is most plausibly a **segmented numeric
compare** (or a plain lexicographic compare that is *accidentally correct*)
over `major.minor.YYMMDD`, with `model.region.platform` acting as
match-prefixes. Because the trailing tokens are fixed-width and
lexicographically monotonic, both readings agree for same-vehicle updates; they
diverge only on cross-region/cross-model strings, which are separately gated.

Region/model gating evidence: the `navi_extended` advice restricts the
substituted manifest to *"the latest update available for your vehicle's
headunit"*, i.e. the manifest must still match the vehicle's region/model —
cross-region manifests are not claimed to work. The `.ver`/manifest carries
`mcode` (`1227` AU IONIQ 5, `1565` Rio, `101489` IONIQ5_EU) and package name, so
model/region mismatch is a second, independent gate.

### 1.4 Attack surface of the `version >= current` check

| # | Scenario | Behaviour / exposure | Basis |
|---|---|---|---|
| 1 | **Equal version** | `>=` admits equality, so re-flashing the *same* build is allowed. Also the primitive behind the "equal/newer manifest + older payload" downgrade: the manifest version only needs to be `>=`, not strictly newer. | `wideopen` wiki wording; `navi_extended` F.A.Q. |
| 2 | **Version-string spoofing (encrypted path)** | Cannot edit the string directly (envelope is encrypted with the per-device key). But substitution of a *genuine newer* `.lge.upgrade.xml` achieves the same effect with no forgery. | `navi_extended` F.A.Q. |
| 3 | **Version-string spoofing (unencrypted path)** | With `disableEncryptionUpdate` present, payloads are plaintext **and the version check still runs via a plaintext `.lge.upgrade.xml`** — the string is fully attacker-controlled; any `>=` value (including fake dates) passes. | `wideopen` wiki "Unencrypted/Custom update process" |
| 4 | **Region mismatch** | Supplying a manifest for a different region is expected to fail the region/model match; not demonstrated publicly as bypassable. | `navi_extended` F.A.Q. scoping; `.ver` region/mcode fields |
| 5 | **Model-code mismatch** | `mcode`/package-name mismatch is a separate gate; a different model's manifest is not claimed to install. | `.ver` header; local AU/EU comparison |
| 6 | **Per-file vs per-package** | Per-package. One root-level `.lge.upgrade.xml`; payload files are only CRC-32'd in the unsigned plaintext `.ver`. No per-file version/rollback check exists. | `wideopen` wiki flow; `.ver` structure |
| 7 | **Manifest↔payload binding** | On the Linux path the manifest is **not** cryptographically bound to the payload at install time (that is exactly why the swap works). On the *Android* Gen5W sibling the `update_info` *is* RSA-signed and binds the package. | `navi_extended` F.A.Q. vs GitLab issue #3 |
| 8 | **Anti-rollback counter** | No public evidence of a monotonic fuse/OTP counter on `S5W_L`; rollback protection is the userland string compare only. | absence in wiki + CVE-2023-26245 wording |
| 9 | **A/B slot state** | Older payload is written to the *inactive* slot and `/etc/fstab` is switched at the end; a failed attempt leaves the previous slot/navi dir, so downgrades are "safe-ish" (recoverable) rather than bricking. | `wideopen` wiki |

### 1.5 Can a signed-but-older official package be installed?

**Yes, on this Linux path — with the manifest-swap primitive.** An older
official package is still encrypted with the device key (so it decrypts
normally), and its payload files are accepted because the version gate reads
only the substituted newer manifest. This is the project's own downgrade
procedure, and it requires no key material and no re-signing.

What would block it:

1. **Manifest↔payload cryptographic binding** (hash/signature over the file
   list) enforced by `AppSetup`. Public evidence says this binding is absent or
   unenforced on `S5W_L` (the Android variant *does* enforce it).
2. **Region/model/mcode mismatch** in the substituted manifest (must still be
   the same vehicle line).
3. **A hard minimum-version floor** (if `AppUpgrade` refused versions below a
   floor regardless of the manifest). Not documented; CVE-2023-26245's
   "older" wording suggests no such floor on the tested build.
4. **Boot-chain anti-rollback / partition signature rejection** after the
   write. The kernel does OEM-key verification (`oemkm`/keystore, see
   `eu-keystore-manifest-root-of-trust.md`) but that verifies signatures of
   boot/update artifacts, not a rollback counter; an *older official* artifact
   is still vendor-signed and should verify.
5. **Entry gating** — irrelevant to the downgrade itself, but relevant to the
   *purpose* of downgrading (reaching "Update AppNavi from USB"): the SOP
   `checkSOPVersion()` gate still applies on newer `MASS_PRODUCT` builds.

Net: downgrade of an official older build is a **version-check bypass, not a
signature bypass**. The signature/crypto chain stays intact; only the version
gating is defeated.

---

## 2. Evidence-capture list (bench unit)

Decisive artifacts that would confirm or refute each point above, without
touching a signed package's integrity.

### 2.1 Files to read

| File | Question it answers |
|---|---|
| Decrypted `.lge.upgrade.xml` (decrypt with device `DecryptToPipe` + `decryption_key.der`, or read the plaintext one in `disableEncryptionUpdate` mode) | **Single most decisive artifact** — reveals the XML field list: is there a version field, a file list, per-file hashes, region/model/mcode, a signature? |
| Diff of two builds' decrypted `.lge.upgrade.xml` (e.g. `251204` vs `260128`) | Which fields change (version only? file list? signature trailer?). Confirms per-package vs per-file binding. |
| `/app/share/AppUpgrade/DecryptToPipe` (and its `DecryptToPipe_FK` helper) | Whether decrypt is a separate binary and whether version parsing happens before/after decrypt. |
| `/app/share/AppUpgrade/AppUpgrade`, `AppSetup`, `AppDMClient` (strings + disassembly) | Locate the `>=` compare, the version-parsing routine, and the region/mcode checks. |
| `/update/` directory — `activeNaviPath`, `activeNaviPath_new`, `activeResourcePath*`, `updateVersionInfo`, `headUnitVersionChanged`, `BKupdateCompleteTime`, `updateCompleteTime` | A/B slot state, which slot is active, and what the updater recorded. |
| `/etc/fstab` (and the pre/post copies) | Confirm the end-of-update slot switch; identify `mmcblk0p3` vs `p5` root selection. |
| `/proc/cmdline` | Confirm `root=` partition and `oemkm=` presence (trust anchor is loader-supplied). |
| Installed version file(s) / build string (e.g. `/etc/*release`, version screen backing file) | The "current version" value that the manifest is compared against. |
| SMACK policy + systemd units for the updater services | Whether the version check could be bypassed by labelling/writes. |

### 2.2 Logs to capture

- **Update-agent log showing the version decision.** Grep for the version
  strings and any accept/reject message (e.g. "current `X`, package `Y`"). This
  proves whether it is a numeric or lexicographic compare and where the region
  check sits relative to it.
- **UART `ttyS2` 115200 8N1 boot log** (already identified in this workspace) —
  bootloader slot selection, any anti-rollback/fuse messages, `oemkm=` injection.
- `dmesg` / journal around an update attempt (especially a deliberately
  equal-version and a deliberately older-version manifest run, if a bench run
  is ever sanctioned).
- Any `OTAUA_FAIL_*`-style or `/update/` error files after a rejected attempt.

### 2.3 Screens to photograph

- **Version info screen** (Model / Software / Firmware / NAV APP / Map / Device
  ID) — the exact installed `NE_E.EUR.S5W_L.001.001.260128` string the check
  compares against.
- **Engineering Mode → Dynamics → Navigation → Config** — whether "Update
  AppNavi from USB" is present or "This feature is currently unavailable"
  (the latter is the documented downgrade trigger).
- Any **"update failed / version" popup** from a manifest/version mismatch run.

### 2.4 What each capture would settle

- Decrypted manifest + diff → settles parts 1.3 and 1.4 rows 6/7 (per-package
  binding and field layout) definitively.
- `AppSetup`/`AppUpgrade` disassembly → settles rows 2/3/4/5 (where the version
  string is parsed, whether region/mcode are compared, and the exact comparison
  operator).
- `/proc/cmdline` + boot log → settles whether any loader-side anti-rollback
  exists beyond the userland check.

---

## Sources

- `wideopen` wiki — "Software/Update_Process" (verbatim update flow + version
  gate + A/B + unencrypted mode):
  https://gitlab.com/g4933/wideopen/-/wikis/Software/Update_Process
- `wideopen` wiki home (project identity, Intel IAS/LGE board):
  https://gitlab.com/g4933/wideopen/-/wikis/home
- `navi_extended` README (downgrade F.A.Q.):
  https://gitlab.com/g4933/gen5w/navi_extended/-/blob/main/README.md
- `navi_extended` issues #2 and #3 (downgrade question; Android `update_info`
  binding): https://gitlab.com/g4933/gen5w/navi_extended/-/issues/2 , /3
- `update_fetcher` README (older-update retrieval):
  https://gitlab.com/g4933/gen5w/update_fetcher/-/blob/main/README.md
- `update-patcher` README (`disableEncryptionUpdate` flag):
  https://gitlab.com/g4933/gen5w/update-patcher/-/blob/main/README.md
- `Helloyunho/gen5w-utils` `parse_ver.py` / `parse_update_info.py` (`.ver`
  header and Android `update.info` formats):
  https://github.com/Helloyunho/gen5w-utils
- NVD CVE-2023-26243 / -26244 / -26245 / -26246 (Chimaera):
  https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2023-26245
  (and siblings)
- Costantino, De Vincenzi, Matteucci, *"A vehicle firmware security
  vulnerability: an IVI exploitation"*, J Comput Virol Hack Tech 20(4):681–696
  (2024), DOI 10.1007/s11416-024-00522-4 (open access; Springer bot-walled from
  this host, abstract via OpenAlex).
- laralbir, `hyundai-kia-gen5w-navi-firmware` (docs/engineering_mode.md,
  docs/gen5w_exploit_ecosystem.md, docs/estructura_ficheros.md):
  https://github.com/laralbir/hyundai-kia-gen5w-navi-firmware
- Local workspace prior art: `evidence/official-package-static.md`,
  `evidence/eu-keystore-manifest-root-of-trust.md`,
  `evidence/eu-custom-firmware-feasibility.md`,
  `evidence/eu-aus-transition.md`,
  `evidence/identity-and-official-updates.md`.

## Unknowns / gaps handed forward

- The decrypted `.lge.upgrade.xml` field layout (no public plaintext example;
  only inferable as above until a bench capture exists).
- Whether the `>=` compare is numeric-segmented or lexicographic, and whether
  region/mcode are checked before or after it.
- Whether any loader/fuse anti-rollback exists independently of the userland
  check (no public evidence; `/proc/cmdline` + boot log would settle it).
- Whether `260128` still contains the `211214` Chimaera version-check bypass
  (unverified; the manifest-swap primitive is independent of that and relies
  only on the documented `>=` semantics).
