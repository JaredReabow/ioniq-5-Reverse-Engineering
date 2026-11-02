# CarPlay/iAP2 exact-static applicability plan

## Objective

Bind the recovered EU `260128` CarPlay/iAP2 attack surface to exact files,
service activation, privilege/SMACK context, SDK lineage strings, ELF mitigation
facts, and public 2024–2025 CarPlay/AirPlay advisories. Produce a deterministic,
offline report that separates an exact physical-input surface from
cross-product/public-version comparisons.

## Non-goals

- No USB, Ethernet, AirPlay, iAP2, or CarPlay traffic.
- No malformed TLV, HTTP, pairing, media, or authentication input.
- No exploit, crash reproducer, shellcode, root transition, persistence, or
  signature bypass.
- No target execution, service startup, module loading, networking, flashing,
  partition writes, or boot changes.
- No claim that Sony, Alpine, Mercedes-Benz, or Apple advisory defects exist in
  the recovered build without byte-level lineage or a matching vulnerable
  mechanism; third-party CVE attribution remains distinct from vendor-confirmed
  function or patch identity.

## Repository evidence

- Enabled `carplay_iAP2.service` launches `/app/bin/iAP2Service-2.0` without a
  `User=` restriction and runs `/etc/iap2_mod.sh` first.
- The script loads the NCM/iAP2 gadget and MFD modules in its normal branch.
- Exact binaries expose `CarPlay.LHW.230712.a` and build paths naming
  `CarPlayFramework/0.1.89-189.180620M.38-r8` and
  `AppleCarPlay_CommunicationPlugin/320.17`.
- Recovered SMACK setup assigns `App::projection` to the service and
  `System::iap20` to `/dev/mfd-iap2`/`/dev/ttyIAP20`.
- Public comparators include ZDI-24-877/CVE-2024-23933,
  ZDI-25-763/CVE-2025-8474, CVE-2024-37602, CVE-2025-24132, and
  CVE-2025-30422. Oligo classifies the latter two as CarPlay RCE/potential RCE
  and names R18.1 as fixed, but its reviewed publication withholds their exact
  routes and implementation details. A later third-party report identifies a
  candidate CVE-2025-24132 mechanism that must be independently byte-checked.
- Exact `libAirPlay.so` contains the HTTP/RTSP-style receiver, plist content
  types/APIs, route markers, and an FDE-bounded HTTP delegate with an inlined
  `_requestProcessSetupPlist` branch for bounded static handler audit.
- Its setup path passes exact HTTP body pointer/length fields to the
  `libCoreUtils.so` binary-plist parser. Parser bounds checks, encryption-key
  handling, and arithmetic candidates must be byte-bound; exact memory-safety
  findings must remain separate from runtime delivery and vendor-confirmed CVE
  identity.

## Deliverables

1. `tools/uk_fw/carplay_sdk_applicability.py`
   - strict no-follow stable reads;
   - exact rootfs-relative path allowlist;
   - strict ELF64 parsing and bounded printable-string extraction;
   - service, enable-link, module-script, SMACK, version-lineage, dependency,
     and mitigation facts;
   - canonical JSON digest and exclusive output creation.
2. `tests/test_carplay_sdk_applicability.py`
   - canonical recovered-input assertions when inputs exist;
   - malformed/symlink/duplicate-output and deterministic-output tests.
3. `evidence/artifacts/projection-candidates/carplay-sdk-applicability.json`
4. `evidence/carplay-iap2-sdk-applicability.md`
5. `docs/agent-work/carplay-sdk-applicability/CHECKPOINT.md`

## Acceptance criteria

- Every exact claim is tied to path, SHA-256, build ID, or literal reviewed
  configuration/string evidence.
- The report may establish exact recovered memory-safety mechanisms, but
  practical phone delivery, authentication state, exploitability, unrestricted
  root, and persistence remain false or unknown.
- Public advisories are recorded as comparators with product and lineage limits.
- Output is independent of locale/stdout encoding and stable across two runs.
- Focused tests, `py_compile`, `git diff --check`, and the canonical pytest suite
  pass.

## Delegation status

The requested Fable named route was checked with the installed Astra routing
doctor. It remains unavailable because `openrouter/claude-fable-5.1` is not
advertised for native subagents (`multi_agent_version` is not `v2`). Native
child dispatch also rejects the exposed argument combinations in this host.
No provider substitution or paid probe is authorized; implementation therefore
continues in the root thread.
