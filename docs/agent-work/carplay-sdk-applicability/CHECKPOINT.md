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
- Bound recovered AirPlay HTTP/plist architecture and the FDE-bounded HTTP
  delegate containing inlined `_requestProcessSetupPlist` at
  `0xf3d1..0x11a3b`, size `0x266a`, SHA-256
  `fccea004635853ec3d685f24815e548a227bf8f65853f5e025e4115cda0cfc10`,
  including four binary-plist parse sites and five dictionary-type-check sites.
  Its direct calls contain bounded text writers but no direct
  `memcpy`/`strcpy`/`sprintf`/`strcat`-style unbounded copy; deeper callees remain
  open.
- Traced HTTP message body `+0x518` and length `+0x530` through call site
  `0x10032` to exact `libCoreUtils.so` `CFBinaryPlistV0CreateWithData`, then to
  the dictionary type check.
- Bound the inlined setup encryption-key path at `0x103c3..0x10580`, exact
  `CFGetData`, `CFDictionaryGetData`, `MFiSAP_Decrypt`, and `AES_CTR_Update`
  bodies. The path retrieves `ekey` with no maximum, forwards its full length to
  a 16-byte stack key buffer, and passes no destination capacity, establishing
  an exact unbounded stack write.
- Matched that recovered mechanism to a later public third-party
  CVE-2025-24132 crash report while retaining the absence of Apple/Oligo
  function confirmation, fixed bytes, runtime delivery, and exploitation.
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
- size: `25,029` bytes
- file SHA-256: `d6a835f08a4a79966434d4d0309bbe040cd443cfcff0087b96a341106238f03d`
- canonical SHA-256: `5b1a4d141b2a8a16bfc8f759291186b1e7495bc2f13b576a441225097b425bd3`

## Validation

- focused static audit: `4 passed`;
- combined CarPlay/static-state focus: `37 passed, 20 subtests passed in 3.43s`;
- canonical: `1074 passed, 352357 subtests passed in 174.10s (0:02:54)`;
- canonical log SHA-256:
  `fc46638764d0a4c7890aa1bb68e6d6a138f85cce20263843be2e6d43febbf9a2`;
- `py_compile`: passed;
- normal-versus-UTF-16 stdout identity: passed, both outputs matched the
  accepted artifact SHA-256;
- `git diff --check`: passed for the six path-limited deliverables.

## Boundaries

- The recovered memory-safety mechanism is exact, and a third party attributes
  the matching mechanism to CVE-2025-24132; vendor-confirmed function identity
  and affected-versus-fixed bytes remain unavailable.
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
3. Trace setup `ekey` route/authentication preconditions and seek lawful fixed
   R18.1 bytes without constructing protocol inputs.
4. Partition the remaining `_requestProcessSetupPlist` branches and audit type
   checks, integer conversions, and stack/heap destinations.
5. Trace setup-dictionary consumers of the UTF-16 wrap/truncation result; the
   direct converter OOB hypothesis is now excluded.
6. Audit remaining AirPlay HTTP/TLV handlers and fixed-stack copy sites.
7. Seek a lawful post-R18.1 binary comparator; do not infer version lineage.
8. Add these exact files and passive unit/module/interface facts to the future
   disconnected bench capture if not already covered.

## Delegation

The requested Fable route remains blocked by its non-v2 native-subagent catalog
entry. Attempts to use the exposed child tool hit its mutually exclusive argument
validation. No alternate provider was silently substituted and no paid probe was
run.
