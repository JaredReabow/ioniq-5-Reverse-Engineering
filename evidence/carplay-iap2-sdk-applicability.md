# Recovered CarPlay/iAP2 SDK applicability

Status: exact recovered-image activation and parser-boundary review, with public
cross-product comparators retrieved 2026-11-02. No target execution, USB or
network traffic, malformed input, crash, or root transition.

## Result

EU `260128` contains a real, enabled, configured-UID-zero CarPlay/iAP2 stack and
therefore exposes a higher-priority physical protocol-review surface than a
version-only package lead:

- `multi-user.target.wants/carplay_iAP2.service` points to the recovered service;
- the unit has no `User=` restriction, runs `/etc/iap2_mod.sh`, starts
  `/app/bin/iAP2Service-2.0`, and uses `Restart=always`;
- the normal script branch selects exact shipped `usb_f_ncm.ko`,
  `usb_f_iap2.ko`, and `mfd-iap2.ko` files;
- the service binary names `/dev/mfd-iap2` and links
  `libiAP2AppFramework-2.0.so`;
- `AppProjection` links both `libiAP2AppFramework-2.0.so` and
  `libCarPlayAppFramework.so`, which in turn names `libAirPlay.so` and
  `libAirPlaySupport.so`;
- recovered SMACK configuration assigns the executables `App::projection`, the
  iAP2 device `System::iap20`, and grants `App::projection -> System::iap20`
  read/write access.

This is exact static exposure evidence, not proof that a phone can complete
identification/authentication on the owner's unit or that attacker-selected
bytes reach a vulnerable parser.

## Exact identities and lineage

The deterministic report binds the full reviewed set. Principal identities are:

| Object | SHA-256 |
|---|---|
| `iAP2Service-2.0` | `38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e` |
| `AppProjection` | `8f0096bcc0734d4c9766c15bac54c42f302ed7057182c2573b5ac543913960e3` |
| `libiAP2AppFramework-2.0.so` | `d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120` |
| `libAirPlay.so` | `ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0` |
| `libCoreUtils.so` | `9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae` |
| `libAirPlaySupport.so` | `1e57d807c320999fda35ac08e7e213f6533014f8d68391b1c33b00505b175893` |
| `libCarPlayAppFramework.so` | `e3603e6b0744cf07724cc5cc79ea01ea3d9207d7eaf37c544c7ce26536ecd7a2` |
| `usb_f_iap2.ko` | `13bb79d9d9e991fdb9a950fc4ef8d65491c804a061208acb669ba54683e1e7bd` |
| `mfd-iap2.ko` | `1276cee2d1a2eca5e2c8d5c7f49eb813ffeae6b81ee490ba3abfc176ae2040c4` |

The service embeds `CarPlay.LHW.230712.a`; `libAirPlay.so` embeds the additional
private source-version string `320.17.6`. `libAirPlaySupport.so` contains build
paths naming:

- `CarPlayFramework/0.1.89-189.180620M.38-r8`; and
- `AppleCarPlay_CommunicationPlugin/320.17`.

Those private identifiers are useful comparison anchors. No public mapping was
found from `320.17` to Apple's later public `R18.1` security release, so neither
"affected" nor "fixed" can be inferred from the number alone.

## Generic iAP2 byte decoder is bounded

The first exact decoder review rejects one broad hypothesis. Exported
`iAp2MarshalGetBytes` at `0x21a56..0x21b21` has SHA-256
`601fc208cd6c41eb6926c782dcafcedd47c88785516c98c1290ebcdd2e08ac31`.
It obtains a 32-bit length and calls the internal span helper at
`0x21645..0x2176a`, SHA-256
`98cbc5af41238b006a7497dfce512b59c21b448f616a55ff641597a058303fcf`.
The complete helper:

1. rejects unsigned lengths greater than `0xfffffffc` before alignment;
2. rounds the requested size up to four-byte alignment;
3. compares that aligned size with the marshalling context's remaining byte
   count;
4. advances the data pointer only on the passing branch; and
5. subtracts the same aligned size from the remaining count.

It returns a pointer into the bounded transaction span and performs no copy into
a fixed stack buffer. Consequently this generic byte-string decoder is not the
unchecked fixed-stack copy described by the public Sony/Alpine advisories.
This does **not** clear other iAP2 event handlers, TLV parsers, HTTP/AirPlay
handlers, pairing code, media decoders, or vendor wrappers.

## Exact AirPlay HTTP/plist architecture

The recovered `libAirPlay.so` independently matches the broad protocol
architecture described by Oligo, without yet matching either CVE mechanism. It
contains:

- HTTP receiver/server APIs including `AirPlayReceiverServerHTTP`,
  `HTTPServerCreate`, and `_HTTPServerControl`;
- binary and XML plist content types plus `CFBinaryPlistV0CreateWithData`,
  `CFPropertyListCreateWithData`, and dictionary-type APIs; and
- exact route strings `/auth-setup`, `/command`, `/feedback`, `/info`, `/logs`,
  `/pair-setup`, and `/pair-verify`.

The FDE-bounded request processor identified by its embedded
`_requestProcessSetupPlist` name occupies `0xf3d1..0x11a3b` (`0x266a` bytes),
SHA-256
`fccea004635853ec3d685f24815e548a227bf8f65853f5e025e4115cda0cfc10`.
It has a `0x178`-byte stack frame, loads a stack canary, calls the binary-plist
parser at `0x10032`, `0x107a7`, `0x10b75`, and `0x10e1a`, and reaches
`CFDictionaryGetTypeID` at five reviewed sites. Its direct call inventory has
bounded text writers `TruncateUTF8`, `snprintf`, and `strlcpy`, but no direct
`memcpy`/`strcpy`/`sprintf`/`strcat`-style unbounded copy or concatenation call.
The three direct repeated-memory operations are `rep stosd` structure clears,
not input copies. This narrows the top-level dispatcher itself; it does not clear
the binary-plist parser, dictionary accessors, session methods, or internal
helper callees. These facts make it a concrete next audit boundary; they do not
identify a missing check, attacker-controlled field, CVE route, or exploitable
copy.

At call site `0x10032`, this exact request processor passes the HTTP message's
`+0x518` body pointer and `+0x530` body length to
`CFBinaryPlistV0CreateWithData`, checks the returned error, then verifies that
the decoded object is a dictionary at `0x100a3..0x100b6`. This is a static
request-body-to-parser route. Runtime delivery, route eligibility, and
authentication remain unobserved.

### Recovered binary-plist parser

The parser implementation is in exact `libCoreUtils.so` and is bound by these
FDE ranges:

| Reviewed role | Range | SHA-256 |
|---|---|---|
| `CFStringCreateWithBytes` | `0x299e4..0x29b11` | `fb6c03d8ad313a1dd91026cece624b2ce1529fb6b56b2bcf2f09deee002c161b` |
| sized integer reader | `0x3964b..0x396dd` | `2054c003efe46884944f96f0790084b092a4f8d48c51b923e79d547f74a48c24` |
| extended-count reader | `0x396dd..0x3975d` | `7b2ad966d067e523a2e7caf20a375b74182572be39d6332db8b26cae207e790d` |
| object-reference reader | `0x3975d..0x39867` | `d16bc0d58e25b9415efec660dd96f07f7888729f1b2aa138d312df1a9843b75d` |
| V0 object reader | `0x39a42..0x3a25b` | `311b21c47180959ed11e36874aefd57aa62a6b625e4c2061b2c7b2b15aca12cc` |
| `CFBinaryPlistV0CreateWithData` | `0x3b605..0x3b8fc` | `c03a2284cb4fcc1b8fc71dd44653d9250c74e8149d285efd8b87296527c2e625` |
| `utf8_encodelen` | `0xc356b..0xc36dd` | `8291feddc85ed5bc7ff032a2615aae0f54e4c40c906435e70dc4f8d473369ba2` |
| `utf8_encodestr` | `0xc36dd..0xc39ee` | `c6beb495d5117cebf4e0883fa60ac3fe65fdc3f3409b608d8878d8a9a46effcd` |
| `utf8_encodestr_copy` | `0xc44c9..0xc459e` | `6a51fe798013ec28857712bc2f381f26279c6b620ee5d4258a696ac2bad08cbe` |

The wrapper requires `bplist00`, rejects input-end pointer wrap, restricts
offset and reference widths to 1/2/4/8, requires a nonzero object count and a
top-object index below that count, and bounds the offset table with division
before multiplication. The object reader bounds sized integer reads, ordinary
data/string lengths, and dictionary reference counts against remaining input.

One exact arithmetic candidate remains: the UTF-16 object branch accepts an
extended unsigned count, doubles it at `0x39e89` with `add rdx, rdx`, and does
not test carry before comparing the **wrapped** byte length with remaining
input. It then passes that same wrapped value to `CFStringCreateWithBytes`.
This establishes an unguarded length wrap in the recovered parser, matching the
broad CWE-190 class Oligo assigns CVE-2025-30422.

The first downstream review excludes a direct OOB mechanism for this specific
chain. `CFStringCreateWithBytes` narrows the length to signed 32 bits at
`0x299eb` (`movsxd rsi, edx`). For a high-bit 32-bit result,
`utf8_encodelen` and `utf8_encodestr` logically halve the sign-extended value,
then their signed low-32-bit loop test exits before reading input. For a
nonnegative truncated result, the conversion reads no more than that value,
which cannot exceed the full wrapped length already checked against remaining
input. Thus this path can truncate or produce an empty string, but does not
read/copy beyond the parser-checked span.

No security-relevant use of the resulting truncated string is yet established,
and this instruction is not attributed to CVE-2025-30422. Exact attribution
still requires fixed-version bytes or a separately demonstrated downstream
security effect; other integer paths remain open.

Oligo's generic discussion says AirPlay commonly uses an HTTP/RTSP-like API and
plist payloads, often over port 7000. The recovered markers establish the
HTTP/plist implementation class, but this review did **not** bind a listening
port, runtime interface, authentication state, or phone-to-handler route for
this exact head unit.

## Public comparators

### CVE-2024-23933 / ZDI-24-877

The public advisory describes a physically reachable Apple CarPlay TLV length
that is copied into a fixed stack buffer without adequate validation on the
Sony XAV-AX5500, with code execution in that device's context. It does not name
the function, SDK release, vulnerable bytes, or patch. Different product;
comparative mechanism only.

### CVE-2025-8474 / ZDI-25-763

The Alpine iLX-507 advisory similarly describes physically reachable CarPlay
data copied into a fixed stack buffer and states code execution in root context
on that Alpine product. It provides no function or patch suitable for an exact
match. Different product; comparative mechanism only.

### CVE-2024-37602

Public Mercedes-Benz NTG6 research describes prepared HTTP requests reaching a
CarPlay/AirTunes/AirPlay null dereference and service failure after physical
access to internal Ethernet. The recovered Hyundai stack contains AirPlay HTTP
APIs, but that common protocol surface is not byte lineage.

### CVE-2025-24132 and CVE-2025-30422

Apple states that AirPlay audio SDK 2.7.1, AirPlay video SDK 3.6.0.126, and
CarPlay Communication Plug-in R18.1 contain fixes for these issues. Apple's
terse advisory/NVD wording describes memory or buffer handling reachable by a
local-network attacker and emphasizes unexpected application termination.

Oligo, the reporting researcher, makes materially stronger but still
cross-product claims:

- CVE-2025-24132 is classified as CWE-121 stack-based buffer overflow and RCE;
  Oligo says it applies to CarPlay and can be zero-click under stated Wi-Fi or
  physical-USB conditions, with Bluetooth/PIN and victim-click conditions on
  some implementations;
- CVE-2025-30422 is classified as CWE-190 integer overflow or wraparound with
  potential RCE; and
- the same fixed SDK releases, including CarPlay Communication Plug-in R18.1,
  are named.

The reviewed Oligo publication explicitly withholds the detailed route and
implementation for these newly published flaws. It therefore raises the
priority of the exact recovered AirPlay/plist processor, but supplies no
function bytes or patch for an exact match. No mapping from private plug-in
string `320.17` to R18.1 was found, so neither affected nor fixed status follows
from the version string.

## Mitigations and impact boundary

All reviewed executable/shared-object ELF files reference the stack protector,
have a non-executable GNU stack, and carry a GNU RELRO segment. The executables
are PIE. These facts constrain generic exploitation but do not prove parser
safety or prevent all code execution.

Configured UID zero is not the same as unrestricted root after exploitation:
the intended runtime SMACK domain is `App::projection`. Conversely, the
projection policy grants broad cross-application execute/access relationships,
so a demonstrated compromise would warrant separate domain-amplification
analysis. Runtime uid, capabilities, labels, device state, authentication,
network interface creation, and installed owner-unit hashes remain bench gates.

## Artifact

- tool: `tools/uk_fw/carplay_sdk_applicability.py`
- schema: `ioniq-carplay-sdk-applicability/v1`
- report: `evidence/artifacts/projection-candidates/carplay-sdk-applicability.json`
- size: `19,365` bytes
- file SHA-256: `4fa51c73fc7930aea24fc506d8f5f429c193022e56003ffc41ea45ebf60155ad`
- canonical SHA-256: `44cc84f3494c9794141b62294cb810ae30f2f4abf27325152b7dedadb4651b13`

## Sources

- `https://www.zerodayinitiative.com/advisories/ZDI-24-877/`
- `https://www.zerodayinitiative.com/advisories/ZDI-25-763/`
- `https://securelist.com/mercedes-benz-head-unit-security-research/115218/`
- `https://support.apple.com/en-us/122403`
- `https://www.oligo.security/blog/airborne`
- NVD records for CVE-2024-23933, CVE-2025-8474, CVE-2024-37602,
  CVE-2025-24132, and CVE-2025-30422

## Next exact-static work

1. Trace every call to `iAp2MarshalGetBytes` into its destination semantics and
   reject or prioritize fixed-size consumers.
2. Audit `iAp2ConectionHandleExternalAccessoryProtocolData`, file-transfer,
   HID, Wi-Fi configuration, and list-update handlers for destination-size
   checks.
3. Partition `_requestProcessSetupPlist` by route and audit each binary-plist
   branch, type check, length conversion, and stack/heap destination without
   constructing protocol input.
4. Trace consumers of the exact UTF-16 wrap/truncation result in the setup
   dictionary; the direct converter OOB hypothesis is excluded, while semantic
   security impact and CVE attribution remain unproved.
5. Inventory other `libAirPlay.so` HTTP/TLV entry points and their fixed-stack
   copies.
6. Obtain a lawfully available post-R18.1 binary for byte comparison if one
   becomes available; do not infer lineage from private version strings.
7. On a disconnected bench, passively capture installed hashes, unit state,
   uid/capabilities/SMACK labels, module state, and interface metadata before
   any protocol interaction.
