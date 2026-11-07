# External Gen5W community claims — November 2026

**Purpose:** preserve useful leads from the supplied 4–7 November 2026 conversation transcript without treating community statements as measurements of this project's unit. The transcript is not copied into the repository. Message IDs below identify the source records in the supplied HTML; public GitHub links identify associated source projects.

**Evidence labels:**
- **Local static corroboration** — independently checked against the project's EU `260128` extraction.
- **Community report** — a statement attributed to a contributor; not reproduced or independently verified here.
- **Variant-sensitive** — must not be generalized across Gen5W_L, UNECE/legacy updater families, model years, or regions without matching firmware evidence.

## Claims and validation

| Claim | Source in supplied transcript | Project validation and disposition |
|---|---|---|
| A USB-update TOCTOU has reportedly yielded code execution on a Gen5W_L unit. | Hurtigfyr, message `m1567917840974225429` (2026-11-06 02:05 UTC): “Got code exec through the USB file”; linked source at `CloudPapi/ioniq5-usb-toctou` in `m1567923527733088457`. | **Community report, not locally reproduced.** Our EU `260128` image independently contains a verify-then-apply path in the embedded FUMO updater; the apply stage reopens a source after the verification stage. Whether that source is still the removable medium or a staged local file remains unresolved. Keep V-059's dynamic status external/unreproduced for this exact image. Do not infer affectedness from family name alone. |
| The USB path reportedly enabled persistent debug access / SSH after firmware modification. | Cmarino, `m1568175508376657951` (2026-11-06 19:09 UTC), describes the `/tmp/secure_console_disable` gate and a change to `esinit`; adjacent messages `m1568176122695389316` and `m1568176157478617140` discuss Ethernet and hubs. | **Partially corroborated, effect not validated.** Our extracted `lib/systemd/esinit` contains the marker and the MICOM `secure_console` gate; in this image `secure_console=0` preserves the marker. The project measured a ttyS2 login prompt in QEMU (see `Ioniq5-VULNERABILITIES.md`, V-049 and `evidence/serial-console/`). The active getty requires authentication; the root-autologin line is commented out. The shipped Dropbear unit is a template, and SSH service enablement/access was not demonstrated. The transcript's patch, persistence, and SSH outcome are **not** locally validated; record as a lead for variant-specific source comparison, not as a new confirmed root path. |
| The TOCTOU does not apply to some newer UNECE SCOMO/encrypted-update paths; another tethered vulnerability may exist. | lucy, `m1567997216218550375` (2026-11-06 07:21 UTC), reports TOCTOU would not work for a newer UNECE path; subsequent exchange `m1567998142333325478` refers to an alternative tethered vulnerability. | **Community report; variant boundary unresolved.** No matching IONIQ 5 UNECE image or runtime test was provided in the supplied evidence. Treat the user's newcomer-guide statements about hardware TXE and a zip-slip path as unverified leads, not findings. This project must compare the exact update family and image before transferring V-059. |
| A broad set of non-US/Linux Gen5W_L versions is rooted, supports custom firmware, and has persistent SSH. | nickles1252, `m1567909985902534730` (2026-11-06 01:34 UTC); Hurtigfyr's specific USB code-execution report is above. | **Community report, broad scope unverified.** No vehicle identifiers, exact firmware matrix, raw logs, or independently reproducible procedure accompany the broad assertion in the supplied transcript. Do not publish it as an established affected-version range. |
| IONIQ 5 CAN material may help with authentic widget input and preconditioning. | Tyler H. linked `tylerharvey/Ioniq5_CAN/preconditioning_messages` in `m1567993997727760526` (2026-11-06 07:08 UTC). | The archived source contains CAN logs, parsing material, wiring/guides, and preconditioning notes. Its applicability to this project's exact NE1/MICOM integration and its safety conditions have **not** been validated here. It is a research reference, not a tested adapter or a substitute for retained vehicle-ground-truth logs. |
| The Cerato report and a transcript post claim CVE-2021-3405 affects bundled libebml 1.3.4 and might permit USB `.mkv` code execution. | Cmarino, `m1568279099049508945` (2026-11-07 02:01 UTC), and `coopermarino/2022-cerato-au-jailbreak/exploits/VULNERABILITY_REPORT.md` (linked in `m1568283792467300412`). | **Version-level match locally validated; exploitability/impact not.** Our EU `260128` `/usr/lib/pkgconfig/libebml.pc` says `Version: 1.3.4`; the `matroska.so` plugin and `libmatroska.so.6` declare `NEEDED libebml.so.4`. Upstream NVD describes a heap overflow in `EbmlString::ReadData` / `EbmlUnicodeString::ReadData` before 1.4.2 ([CVE-2021-3405](https://nvd.nist.gov/vuln/detail/CVE-2021-3405)); the installed release is in that version range. The SONAME `.so.4` is an ABI number, not proof of release 4.0.0. NVD's stated impact is availability (CVSS 6.5); the transcript's potential-RCE claim is not established by the CVE record. No backport audit, crafted-file test, parser-path proof, or process-privilege measurement was performed. V-047 remains a candidate.

## Local checks performed against the matching build

- `AppUpgrade` and its embedded FUMO image in the EU `260128` extraction were inspected independently. V-059 records the exact static check/apply evidence and the unresolved source staging question.
- The extracted `/lib/systemd/esinit` was checked around the reported gate: it creates `/tmp/secure_console_disable`, reads `/sys/module/micom/parameters/secure_console`, and removes the marker and `/dev/ttyS2` only when the parameter is `1`. This confirms the *gate exists* in this image; it does not prove that external firmware patches work or that SSH becomes available.
- The extracted `libebml.pc` reports 1.3.4, and `llvm-readelf -d` shows `matroska.so` and `libmatroska.so.6` depend on `libebml.so.4`. NVD's CVE-2021-3405 record gives an affected upstream range before 1.4.2 and describes availability impact; vendor backport status and runtime reachability remain unchecked.
- Existing QEMU evidence of the ttyS2 login prompt is retained at `evidence/serial-console/ttyS2-login-prompt-2026-11-04.log`. It is a projection observation, not a physical-car test.
- No vehicle update, firmware flash, live CAN injection, or new QEMU run was performed to validate these external claims.

## Source and preservation notes

The supplied transcript linked the following distinct GitHub repositories. Relevant source snapshots are preserved as full Git bundles (branches/tags and history, not merely a summary) on the **private `unsanitised` branch** under `unsanitised/upstream-archives/`. This sanitized document does not contain their code. Each bundle has a provenance record, source URL, captured refs, and checksum.

- `CloudPapi/ioniq5-usb-toctou` — update-path research and PoC; V-059 relevance.
- `coopermarino/2022-cerato-au-jailbreak` — related Gen5W_L analysis and test notes; different vehicle/build.
- `tylerharvey/Ioniq5_CAN` — CAN research and preconditioning material.
- `nickles-lee/hkg_SCOURGE` — Linux Gen5W software/firmware research.
- `chenxiaolong/nudl` — navigation-update downloader; related ecosystem/tooling, not an exploit validation source.
- `dibble9012/auto-heat-and-cool-seats`, `KramerTech/gen5-RearDashcam`, `isaacwisdom/iphone-bluetooth-pan-nemesis`, `ntwm787/Auto-DST-Gen5`, `zpoon/gen5w-BatteryWatchdog`, and `eclipseempire/hkmc-chargeport-button` — related Gen5W applications or community projects.
- `raspberrypi/rpi-usb-gadget` — generic USB-gadget utility referenced for research hardware; not vehicle firmware.

At capture time `ntwm787/Auto-DST-Gen5` returned GitHub HTTP 404 and could not be archived. The link and retrieval failure are recorded in the private archive manifest; no substitute or guessed copy was made. The user's own `JaredReabow/ioniq-5-Reverse-Engineering` repository is already maintained separately and was not duplicated.

Some upstream repositories declare no license. Their bundles are retained only in the user's private research repository; they are not relicensed, redistributed through sanitized `main`, or presented as project-owned code. Before publishing or reusing code, check the original repository's license and attribution terms.

## Next evidence that would change status

1. Obtain an exact model/region/firmware matrix and raw before/after logs for any claimed root or SSH result.
2. For V-059, observe on a matching authorized unit whether the apply-time source is the USB-mounted file or a local staged copy; retain full logs and a null result.
3. For the console/SSH report, compare the claimed `esinit` change against the exact target image and verify the actual service graph and authentication path. Do not assume a marker alone creates an SSH listener.
4. Keep UNECE SCOMO/update-path claims separate until the relevant signed/encrypted image and updater are independently examined.
5. For the libebml lead, audit the shipped binary for vendor backports and establish whether removable-media indexing reaches the affected read methods under an identified service identity; do not infer RCE from CVE version range alone.
