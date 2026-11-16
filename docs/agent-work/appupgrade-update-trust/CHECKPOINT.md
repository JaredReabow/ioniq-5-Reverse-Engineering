# AppUpgrade update-trust checkpoint

Date: 2026-11-01

## Completed

- Added strict read-only embedded-ELF inspection/extraction in
  `tools/uk_fw/embedded_elf.py` with synthetic tests.
- Replaced broad updater carvings with exact SCOMO and FUMO structural extents.
- Reconstructed the outer wrapper:
  - exact case-sensitive `-un:1` selects SCOMO;
  - all other sets, including `-un:0`, select FUMO;
  - all application arguments except item zero are forwarded to the child;
  - copy/chmod/XML-copy and child status results are not propagated;
  - the wrapper exits `1` on its normal path.
- Reconstructed AppLauncher argument flow:
  - dynamic app processes call the global/model option builder at `0x34510`;
  - the resulting list is stored at `AppProcess+0x60` and passed to
    `QProcess::start`;
  - the embedded NE/EUR row contains `-un:0`;
  - exact `-un:1` plus app ID 311 conditionally substitutes AppScomoDM for
    AppDMClient.
- Reconstructed marker startup semantics:
  - FUMO byte VA `0x6d20b4` starts at `1`; marker existence writes `0`;
  - SCOMO MASS_PRODUCT/PENETRATION startup explicitly ignores the marker.
- Excluded AppSetup as the descriptor parser; it initiates the app-ID-300
  transition.
- Reconstructed AppScomoDM `launchAppUpgrade` and its direct helpers:
  - one first `S5W_SYSTEM_*_*_*.zip` iterator result and stricter filename-shape validation;
  - pre-verification extraction of `AppUpgrade` and `.lge.upgrade.xml`;
  - exact-zero public-key-backed verification of both extracted files;
  - CryptoService versus old `DecryptToPIPE` AppUpgrade decryption;
  - plain XML copy, ELF/executable check, final copy/chmod, and app-ID-300 launch;
  - legacy layout rejection and weak subprocess/error propagation.
- Identified V-020 in the stock BusyBox `unzip` provider after correcting a VM-
  helper provenance error: exact method 8 reaches CVE-2015-9261's unfixed
  `huft_build` `v+n` bound before member authentication; method 12 is rejected.
  Added a data-free bound model and focused tests.
- Reconstructed AppDMClient's separate FUMO USB descriptor path:
  - `<source>/.lge.upgrade.xml`, accepted `lhavn`/`wideavn` roots, and
    consecutive-element traversal for a first-child-text `version` value;
  - encrypted XML versus direct-plaintext parser branches and separate verifier
    opens without a proved immutable snapshot;
  - two normalized lexicographic version comparisons;
  - on unequal source/destination, marker-absent retained-result contract `0/0`
    and marker-present explicit non-encrypted contract `-404/-404`; exact linked
    verifier code now identifies `-404` as no recognized fixed-size `TER`/`TE2`
    trailer, not successful signature verification;
  - equal pre-staged AppUpgrade path skips both contracts; caller reconstruction
    proves intended local `/update/usb/bin` relaunch reachability;
  - `slotUsbMounted` stores the mount-path `QString` at `this+0x128`, while
    standby-status and exact `force_launch=run` workflows provide fixed local
    relaunch paths;
  - inner FUMO progress-zero branches attempt `processing` and then
    `force_launch=run`; the branch-local progress-100 sequence attempts
    `complete` and then `none`, while later scheduled flow can attempt `run`
    again. The weak writer proves neither success nor atomicity. Exact
    `DeltaUpdateProgressHandler` routes now name some callback events, but the
    force value alone does not establish completion/authentication in the
    traced write-site evidence. The additional scheduled branch requires both
    local completion strings plus `isScheduledUpdating`; upstream event
    authentication and source immutability remain unresolved;
  - explicit section-zero vehicle equality disabled at the reviewed USB call
    sites, while P5-family and later target checks remain;
  - added a numeric/boolean-only model for exact trailer classification and
    retained-result pair gates; it emits no update material and never equates
    gate progression with update acceptance;
  - traced the inner FUMO navigation-map signature gate at `0x128070`: its
    dedicated disable marker, missing NaviUpdateApp/NUA provider, non-encrypted
    mode byte, and no-map state all skip that one gate; async start/result
    failures stop through `0x127e80`, while success sets `this+0xd5` and
    re-enters the gate;
  - corrected the mode relationship: FUMO startup
    `/update/disableEncryptionUpdate` sets the same byte later used by the
    navigation-map non-encrypted skip branch. Added a separate numeric-only gate
    model and exact retained evidence without claiming universal signature or
    payload acceptance;
  - completed the AppDMClient caller-side source-identity audit: verifier wrapper
    `[0x34870,0x34d43)` returns integer status only; staging later constructs a
    pathname copy and calls `QProcess::execute` at `0x8296b`; the XML reader
    separately verifies at `0xe1ff7` and later opens at `0xe22d5` or `0xe281f`.
    No retained open description or identity revalidation binds those consumers
    to the verified object. Added exact retained assembly, an eleven-input schema-v2
    model, and exhaustive valid-state tests. Runtime mutability, object mismatch,
    effective indirect/external reauthentication, update acceptance, root, and
    persistence remain unproved. Focused validation passed `9 tests, 2056 subtests`;
    the full suite passed `543 tests, 140279 subtests`; the public harness passed,
    and independent corrected package review returned **ACCEPT**;
  - completed exact embedded FUMO authentication-coverage review. Startup
    `[0x125800,0x126fe4)` derives a resource base directory from `argv[0]`;
    verifier `[0x45820,0x45d75)` has exactly six direct call sites and file-MD5
    helper `[0x140f50,0x1413e4)` has exactly two. Fixed/enumerated operands cover
    the descriptor, archive, firmware entries, resources, and navigation files.
    The metadata-forwarded verifier operand remains incomplete: `0x100bb0`
    receives its target through `%rdx`, while direct caller `0x16e030` forwards
    a QString from a meta-call argument structure. Worker relaunch `[0x6c9a0,0x6cab5)` calls
    `execv` without a direct pre-exec verifier/hash step inside that FDE. Added
    V-032, retained assembly and parameter callers, a thirteen-input schema-v2
    model, and exhaustive Boolean tests. Outer-executable reauthentication stays
    unknown; source mutability, mismatch, bypass, accepted update, root, and
    persistence are also unproved. Focused validation passed `10 tests, 8203
    subtests`; the full suite passed `553 tests, 148482 subtests`; the public
    harness passed; corrected independent exact-binary/package review returned
    **ACCEPT**.
  - resolved the two remaining parameterized direct verifier targets in the exact
    embedded FUMO ELF. Whole-instruction scans prove `0xf359e -> 0x9cbc0` and
    `0x9d4fe -> 0x140030`; no direct call targets upstream FDE `0xf28e0`.
    Calls `0x9d1d2` and `0x140092` receive the same encrypted controller-resource
    source pathname, first directly and then through a QString copy, under one
    of four fixed controller trees. The bounded route excludes running/staged
    updater, descriptor, and general firmware pathname roles. Exact-zero
    verification dominates transformation, but verifier and helper reopen the
    path, helper status is ignored, and only a nonempty destination QString is
    checked; authenticated-byte and final-consumption binding remain unknown.
    Added a strict fail-closed analyzer, 12 focused tests with 6 subtests,
    exact-static/manifest/report artifacts, and public evidence. Focused and
    full suites pass; repository harness and privacy validation pass.
- Wrote `evidence/appupgrade-update-trust.md`,
  `evidence/appdmclient-fumo-usb-eligibility.md`, and corrected the broad
  marker-equals-unchecked-path documentation.

## Safety record

No recovered updater, helper, or target executable was run. No package was
installed. No image, partition, marker, slot, or VM filesystem was modified.
All exact binaries, disassemblies, maps, and extracted ELFs remain ignored under
`work/`.

## Remaining

1. Finish the broader caller-state and cleanup reconstruction around AppScomoDM
   `0xc1860`; the `0xbf260` staging function and direct trust helpers are now
   complete enough for the current route verdict.
2. Name the second stored AppDMClient version reference and numeric boot-state
   values from exact code; trace the XML destination helper.
3. Determine runtime source mutability/immutability. Resolve complete producers
   for the remaining metadata-forwarded verifier route (`0x100bb0`) plus
   indirect/external/loader checks and final payload binding. Continue upstream
   from `DeltaUpdateProgressHandler` to
   determine whether a named authentication state necessarily precedes each
   valid progress event.
4. Continue from the now-named navigation-map signature use into other FUMO
   mode-byte decryption, digest, archive, and write functions; map inner
   AppUpgrade `car-variant`/system-version decisions without inferring that one
   skipped branch removes all trust controls.
5. Reconstruct payload target selection, inactive-slot writing, boot selection,
   userspace health, and mark-good independently.
6. On a disconnected bench, passively capture installed BusyBox/AppScomoDM/
   AppUpgrade hashes, effective `PATH`, runtime uid/SMACK label, selected `-un`
   arguments, relaunch/completion markers, staged `/update/usb/bin` identities,
   and updater state before any active test.

## Validation

Run from the repository root:

```sh
python3 -m pytest -q tests
git diff --check
```
