# CarPlay/iAP2 exact-static applicability checkpoint

## Completed

- Bound enabled `carplay_iAP2.service`, its enable symlink, normal module-loading
  branch, exact transport module files, configured UID-zero default, and intended
  `App::projection` / `System::iap20` SMACK boundary.
- Bound exact iAP2, AppProjection, CarPlay, and AirPlay binary identities and
  linkage strings.
- Recovered private lineage anchors `CarPlay.LHW.230712.a`, `320.17.6`,
  `CarPlayFramework/0.1.89-189.180620M.38-r8`, and
  `AppleCarPlay_CommunicationPlugin/320.17`.
- Added public comparative records for CVE-2024-23933, CVE-2025-8474,
  CVE-2024-37602, CVE-2025-24132, and CVE-2025-30422 while preserving the lack
  of exact product/byte lineage. Reconciled Apple's termination-focused wording
  with Oligo's researcher classifications: CWE-121 CarPlay RCE for 24132 and
  CWE-190 potential RCE for 30422.
- Bound and reviewed `iAp2MarshalGetBytes`, `iAp2MarshalGetUint32`, and the
  complete internal byte-span helper. The generic decoder rounds safely,
  validates against remaining transaction bytes, advances only after validation,
  and performs no fixed-stack copy.
- Bound recovered AirPlay HTTP/plist architecture and FDE-bounded
  `_requestProcessSetupPlist` at `0xf3d1..0x11a3b`, size `0x266a`, SHA-256
  `fccea004635853ec3d685f24815e548a227bf8f65853f5e025e4115cda0cfc10`,
  including four binary-plist parse sites and five dictionary-type-check sites.
  Its direct calls contain bounded text writers but no direct
  `memcpy`/`strcpy`/`sprintf`/`strcat`-style unbounded copy; deeper callees remain
  open.
- Traced HTTP message body `+0x518` and length `+0x530` through call site
  `0x10032` to exact `libCoreUtils.so` `CFBinaryPlistV0CreateWithData`, then to
  the dictionary type check.
- Bound the wrapper, object reader, reference reader, extended-count reader, and
  sized-integer reader by exact ranges and hashes. The parser contains an exact
  unguarded UTF-16 byte-count doubling at `0x39e89`.
- Traced that candidate through exact `CFStringCreateWithBytes`,
  `utf8_encodelen`, `utf8_encodestr_copy`, and `utf8_encodestr`: signed 32-bit
  narrowing causes high-bit lengths to exit before input reads, while
  nonnegative truncations remain within the parser-checked span. This excludes
  a direct OOB read/copy in this chain; semantic impact, RCE, and CVE-2025-30422
  attribution remain unproved.
- Added deterministic tool, focused tests, report artifact, and evidence prose.

## Artifact

- schema: `ioniq-carplay-sdk-applicability/v1`
- path: `evidence/artifacts/projection-candidates/carplay-sdk-applicability.json`
- size: `19,365` bytes
- file SHA-256: `4fa51c73fc7930aea24fc506d8f5f429c193022e56003ffc41ea45ebf60155ad`
- canonical SHA-256: `44cc84f3494c9794141b62294cb810ae30f2f4abf27325152b7dedadb4651b13`

## Validation

- focused: `4 passed in 0.04s`;
- canonical: `1066 passed, 352357 subtests passed in 163.79s (0:02:43)`;
- canonical log SHA-256:
  `93e617c57d4c849faad2b83ff030f3d4d8427ea4b4cc4dc982cca4bd587be4b2`;
- `py_compile`: passed;
- normal-versus-UTF-16 stdout identity: passed, both outputs matched the
  accepted artifact SHA-256;
- `git diff --check`: passed for the six path-limited deliverables.

## Boundaries

- No exact public CVE match is established.
- No phone, USB, NCM, AirPlay, iAP2, HTTP, TLV, pairing, or media input was sent.
- No service, module, executable, parser, or VM was run.
- No crash, code execution, SMACK escape, unrestricted root, update acceptance,
  flashing, or persistence is demonstrated.
- The user's installed-unit identity remains unknown.

## Next actions

1. Trace all exact callers of `iAp2MarshalGetBytes` to fixed-size or allocated
   destinations.
2. Audit external-accessory, file-transfer, HID, Wi-Fi configuration, and list
   event handlers.
3. Partition `_requestProcessSetupPlist` by route and audit its binary-plist
   branches, type checks, integer conversions, and stack/heap destinations.
4. Trace setup-dictionary consumers of the UTF-16 wrap/truncation result; the
   direct converter OOB hypothesis is now excluded.
5. Audit remaining AirPlay HTTP/TLV handlers and fixed-stack copy sites.
6. Seek a lawful post-R18.1 binary comparator; do not infer version lineage.
7. Add these exact files and passive unit/module/interface facts to the future
   disconnected bench capture if not already covered.

## Delegation

The requested Fable route remains blocked by its non-v2 native-subagent catalog
entry. Attempts to use the exposed child tool hit its mutually exclusive argument
validation. No alternate provider was silently substituted and no paid probe was
run.
