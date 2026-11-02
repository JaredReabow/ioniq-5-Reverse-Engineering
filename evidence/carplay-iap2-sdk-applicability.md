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

The FDE-bounded HTTP connection delegate installed at `0xc7a7` contains an
inlined `_requestProcessSetupPlist` branch and occupies `0xf3d1..0x11a3b`
(`0x266a` bytes), SHA-256
`fccea004635853ec3d685f24815e548a227bf8f65853f5e025e4115cda0cfc10`.
The callback has a `0x178`-byte stack frame and loads a stack canary. Across
its inlined request branches it calls the binary-plist parser at `0x10032`,
`0x107a7`, `0x10b75`, and `0x10e1a`, and reaches `CFDictionaryGetTypeID` at
five reviewed sites. Its direct libc-style call
inventory has bounded text writers `TruncateUTF8`, `snprintf`, and `strlcpy`, but
no direct `memcpy`/`strcpy`/`sprintf`/`strcat` call. The three direct
repeated-memory operations are `rep stosd` structure clears. That inventory did
not clear internal callees: the deeper encryption-key branch below contains an
exact unbounded stack write through `MFiSAP_Decrypt` and `AES_CTR_Update`.

At call site `0x10032`, this exact request processor passes the HTTP message's
`+0x518` body pointer and `+0x530` body length to
`CFBinaryPlistV0CreateWithData`, checks the returned error, then verifies that
the decoded object is a dictionary at `0x100a3..0x100b6`. This is a static
request-body-to-parser route. Runtime delivery remains unobserved.

### Exact SETUP and MFi-SAP route gates

Two additional ranges bind the local callback dispatch rather than inferring it
from route strings:

| Reviewed callback role | Range | SHA-256 |
|---|---|---|
| `SETUP` method/content-type/plist dispatch | `0xff0d..0x100b6` | `c208fb3bb3d4ff1c63a25e39dc7b2263aed1258cd62d73797bd591576f52304a` |
| pre-key metadata/session branch | `0x100a3..0x103c3` | `44ad05b420c93321d8bef6dd724d52eed547ca9e0274ef8399f8424f5e368b39` |
| `POST /auth-setup` dispatch | `0x1094d..0x10b3f` | `4220993de1cc6fd57f9cfd5234217482a5001b5dffe8e5b4604b08cd94a87163` |

The first branch compares the request method with `SETUP` at `0xff1b`, reads
`Content-Type`, accepts the binary-plist and XML-plist MIME strings, and calls
the binary-plist parser at `0x10032`. No URL-specific acceptance check, HTTP
`Authorization` check, or pair-setup/pair-verify state check occurs in this
reviewed callback before the setup parser. This is a stronger exact local-route
result than the earlier marker inventory. It does **not** exclude an upstream
generic `HTTPConnection` gate before the callback is invoked, and it does not
establish a listening interface or phone delivery.

The direct pre-key field branch is now partitioned as well. It handles
`deviceID` as a six-byte hardware address, formats `interfaceName` with a
17-byte `snprintf` capacity, copies `macAddress` with a six-byte capacity,
retrieves `name` with a 128-byte capacity, retrieves `sessionUUID` with a
16-byte capacity and an exact returned-length check at `0x10192`, and retrieves
`sourceVersion` and `model` with 64-byte capacities. It clears the session-create
parameter structure before populating it and calls `AirPlayReceiverSessionCreate`
at `0x10333`. This excludes a missing-capacity argument among those direct
callback-local writes only; the CF helper implementations and downstream
`AirPlayReceiverSessionSetup` consumers remain separate review surfaces.

The normal exact route to the cryptographic prerequisite is `POST
/auth-setup`. That branch requires a non-empty body, deletes a previous
completed MFi-SAP context before restarting, creates a version-1 server
context, and calls `MFiSAP_Exchange` at `0x10a8f` with the HTTP body pointer,
body length, and the connection's done byte at `+0xe8`. On success it returns
`application/octet-stream` response data.

The downstream state and hardware path are also byte-bound:

| Reviewed MFi role | Range | SHA-256 |
|---|---|---|
| server-M1 exchange body | `0x7f184..0x7f6d2` | `82f0acf4129488fd468c797af0ab57fc997ec9f8900558ff1537f437d312c00d` |
| `MFiSAP_Exchange` | `0x7f8ce..0x7f99b` | `366334d17eabce1093798b600a43004e4b8140230ecb8fb4c178421899d63a6c` |
| `MFiPlatform_CreateSignature` | `0x8068a..0x80d6c` | `923e37d7fd3828db659fd135fd652a0c35b9e6f17f030946d1bf702a21648677` |
| `MFiPlatform_CopyCertificate` | `0x80d6c..0x8129f` | `0b1160862646812e44f1e019eab17f6545cc4e58c601611e8ddb758e994c035e` |

With non-null input, exact `MFiSAP_Exchange` selects server-M1 state 5. Its
server body requires version 1 plus one 32-byte public key and exact input
consumption, derives the shared state, and calls the platform certificate and
signature functions. Only successful completion increments the context to
server-done state 6 and sets the connection done byte; an exchange error
invalidates the state. Exact `MFiSAP_Decrypt` accepts state 4 or 6. Both exact
platform operations open `/dev/i2c-1`, so the recovered implementation expects
an MFi authentication-chip transport there.

At `0x103a9..0x103c3`, a non-null HomeKit pair-verify security context takes an
alternate branch that installs that context and bypasses the `ekey` decrypt
path. The reviewed stack write therefore requires this HomeKit context to be
null; pair-verify is not a prerequisite for entering the affected branch.

Consequently, for setup encryption type `0x10`, the route has a real
cryptographic/hardware prerequisite rather than a local HTTP-password or
pairing-state check: a successful MFi-SAP exchange must first establish an
accepted state. Static code and a device-path string do not prove that
`/dev/i2c-1`, an authentication chip, a valid certificate/signature operation,
or a phone exchange exists at runtime. No exchange was attempted.

### Exact setup `ekey` stack-write mechanism

The inlined encryption-key path at `0x103c3..0x10580` is `0x1bd` bytes with
SHA-256
`93bcf61544059dc8e162d80012a9527905fc3a26cee51bac471634678b110d67`.
For encryption type `0x10` (public comparative source names this
`kAirPlayEncryptionType_MFi_SAPv1`), the recovered bytes:

1. call `CFDictionaryGetData` at `0x1040f` for the setup `ekey` value with a
   null destination and zero maximum length;
2. retain the returned full CFData length at stack offset `+0x80` and the
   underlying data pointer in `rax`;
3. make no `length == 16` check before calling `MFiSAP_Decrypt` at `0x1048c`;
4. pass that unchanged length and a destination at stack offset `+0x108`; and
5. only apply a 16-byte maximum and exact-length check to the separate IV copy
   at `0x1050d..0x10548`.

The destination at `stack + 0x108` is the 16-byte key buffer; the adjacent
16-byte IV starts at `+0x118`, and the function canary is at `+0x168`, 0x60
bytes after the key-buffer start. Exact code passes `+0x108` and `+0x118` as
the key/IV pair to `AirPlayReceiverSessionSetSecurityInfo`, then clears exactly
16 bytes from the key address. The call-chain bodies are independently
byte-bound:

| Reviewed role | Range | SHA-256 |
|---|---|---|
| `CFGetData` | `0x47075..0x4720f` | `714c493f4fef6c0807b8fa82458806df30ea98f87cf9a58d84959393c7be7e19` |
| `CFDictionaryGetData` | `0x472a0..0x4733f` | `615a9d9fde2ef58caf77a8f6cc7a59f1a206bdc7cb885e90a7a06629d49f85f7` |
| `MFiSAP_Decrypt` | `0x7fa41..0x7fae7` | `d73d2a706aaf00c7eaa472e9c9f2f1110834bc029f59581a7cd7d1f7b1c5e5e7` |
| `AES_CTR_Update` | `0x1f373..0x1f578` | `6f3b5d9b617ee004f966833d32539166615cc2e12adc0fc9afaeda5bcdbfa610` |

Exact `CFGetData` returns the underlying CFData pointer and full length when its
destination is null. Exact `MFiSAP_Decrypt` preserves the caller's length and
destination while forwarding them to `AES_CTR_Update`; exact
`AES_CTR_Update` emits that many output bytes to the caller destination. No
destination capacity reaches either cryptographic function. This establishes an
unbounded stack write in the recovered bytes, not merely architecture overlap.

A public third-party demonstration published in
`TheGamingGallifreyan/LiberationPlay-CVE-2025-24132-AirBourne-POC` attributes
CVE-2025-24132 to the same setup `ekey`, MFi-SAP, AES-CTR, and 16-byte-key-buffer
chain and says its analysis used vulnerable and patched binaries. The reviewed
snapshot is commit `ffd24a03dc5425dd89f6352bf588fcde5f4081ff`; its public source
has SHA-256
`dafbad8b342e705543ee03f132ab09c320fecf719503b735ac8d6d99ba3fb6e7`.
That is a strong third-party mechanism match. It is not Apple/Oligo confirmation
of the function, and the claimed patched binary or patch bytes were not
published for an exact affected-versus-fixed comparison.

Static entry into the write still requires the callback to receive a recognized
plist `SETUP`, a parsed dictionary, a null HomeKit pair-verify context,
encryption type `0x10`, a non-null MFiSAP context, and state 4 or 6. The normal
exact server route reaches state 6 only
after the successful `/auth-setup` certificate/signature exchange described
above. No live phone delivery, completed authentication, crash, reliable control
flow, code execution, SMACK escape, unrestricted root, or persistence was
observed. The canary provides a fail-stop boundary for overwrites reaching it;
it does not repair the preceding memory corruption.

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
implementation for these newly published flaws. A later third-party public
crash demonstration identifies the setup `ekey`/MFiSAP/AES-CTR mechanism for
CVE-2025-24132, and that mechanism independently matches the recovered bytes as
described above. Apple/Oligo have not confirmed this function publicly, and no
published fixed bytes are available for a first-fixed comparison. No mapping
from private plug-in string `320.17` to R18.1 was found, so affected or fixed
status does not follow from the version string alone.

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

## Disconnected-bench readiness

`tools/uk_fw/bench_carplay_readiness.py` now consumes the canonical passive
state bundle and compares the installed owner-unit projection stack against
these exact identities. It separately gates active service state, EUID/SMACK
process context, `/dev/mfd-iap2`, device labels, and loaded transport modules,
and now reports `/dev/i2c-1` character-device metadata as the exact MFi
certificate/signature transport prerequisite. It sends no traffic and cannot
promote passive prerequisites into CVE
applicability, code execution, unrestricted root, or persistence. See
`evidence/carplay-bench-readiness.md`.

## Artifact

- tool: `tools/uk_fw/carplay_sdk_applicability.py`
- schema: `ioniq-carplay-sdk-applicability/v1`
- report: `evidence/artifacts/projection-candidates/carplay-sdk-applicability.json`
- size: `32,307` bytes
- file SHA-256: `de3f59b5d9db0bbbe916a5919972065331fb550f2a2c210ed39870e397ada699`
- canonical SHA-256: `c2f25b6489a0853dfc598e499d02e0fb2ff92de5f83dce29f4f50e1690dd31e2`

## Sources

- `https://www.zerodayinitiative.com/advisories/ZDI-24-877/`
- `https://www.zerodayinitiative.com/advisories/ZDI-25-763/`
- `https://securelist.com/mercedes-benz-head-unit-security-research/115218/`
- `https://support.apple.com/en-us/122403`
- `https://www.oligo.security/blog/airborne`
- `https://github.com/TheGamingGallifreyan/LiberationPlay-CVE-2025-24132-AirBourne-POC`
- comparative Accessory SDK source snapshot at
  `https://github.com/xueming1988/test1/tree/1b6a732fda35f3423b12edabbaf4bc9389b41a98/middleware/private/mfi_airplay/MapleSDK`
- NVD records for CVE-2024-23933, CVE-2025-8474, CVE-2024-37602,
  CVE-2025-24132, and CVE-2025-30422

## Next exact-static work

1. Trace every call to `iAp2MarshalGetBytes` into its destination semantics and
   reject or prioritize fixed-size consumers.
2. Audit `iAp2ConectionHandleExternalAccessoryProtocolData`, file-transfer,
   HID, Wi-Fi configuration, and list-update handlers for destination-size
   checks.
3. Seek lawful fixed R18.1 bytes for the now-bound setup-key route without
   constructing or sending protocol input; do not infer the patch from private
   version strings.
4. Partition the remaining `_requestProcessSetupPlist` branches by type check,
   length conversion, and stack/heap destination.
5. Trace consumers of the exact UTF-16 wrap/truncation result in the setup
   dictionary; the direct converter OOB hypothesis is excluded, while semantic
   security impact and CVE attribution remain unproved.
6. Inventory other `libAirPlay.so` HTTP/TLV entry points and their fixed-stack
   copies.
7. Obtain a lawfully available post-R18.1 binary for byte comparison if one
   becomes available; do not infer lineage from private version strings.
8. On a disconnected bench, run the prepared passive state capture and
   CarPlay-readiness assessor before any protocol interaction.
