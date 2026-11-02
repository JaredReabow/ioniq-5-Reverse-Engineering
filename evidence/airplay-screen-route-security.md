# Recovered AirPlay screen route and security state

Status: exact-static route and prerequisite refinement for EU `260128`. No
recovered executable, service, parser, or shared-library entry point was run. No
HTTP request, stream descriptor, screen header, AVCC body, media frame, packet,
key, or protocol input was created or transmitted.

## Result

The previously bound screen-parser read/write candidate is reached through a
separate TCP listener created while processing a screen stream descriptor. The
exact recovered route is:

1. `AirPlayReceiverSessionSetup` reads each stream descriptor's `type` and
   dispatches value `0x6e` to the screen branch;
2. the branch rejects an already initialized screen and requires a nonzero
   `streamConnectionID`;
3. it selects pair-verify-derived ChaCha20-Poly1305 security when the session's
   pair-verify pointer is non-null, otherwise it derives an AES-CTR screen key
   from the session's 16-byte base key and the stream connection identifier;
4. it calls `ServerSocketOpen` for a TCP stream listener and returns the
   resulting `dataPort` in the setup response;
5. once the receiver session is started, a screen thread accepts one socket,
   wraps it as a `NetSocket`, starts the screen stream, and calls
   `AirPlayReceiverSessionScreen_ProcessFrames`.

The exact `ServerSocketOpen` implementation binds IPv4 to the zero address
(`INADDR_ANY`) and IPv6 to `in6addr_any`. The preferred screen port argument is
negative `6030`, which means that a bind failure may fall back to a dynamic
port. The accepted-socket call passes a null peer-address output; the reviewed
caller therefore neither obtains nor compares the connecting peer address
before giving that socket to the screen parser.

This is static listener construction and caller behavior. It does not establish
that the listener is live on any externally reachable interface, that a port is
disclosed to an unauthenticated party, or that no policy is enforced elsewhere.

## Exact no-MFi fallback candidate

The screen branch does **not** require that the session's ordinary base-key
state was initialized before deriving the screen AES key:

- `AirPlayReceiverSessionCreate` explicitly clears the fresh session body,
  including the 16 bytes at session offset `+0x260`;
- in the setup callback, a missing encryption-type dictionary value produces an
  error from exact `CFDictionaryGetInt64`, and that error branch goes directly
  to `AirPlayReceiverSessionSetup`;
- encryption type `0x01` takes the same direct branch. Public comparative source
  names `0x01` `kAirPlayEncryptionType_None`;
- neither branch calls `AirPlayReceiverSessionSetSecurityInfo`;
- the screen type-`0x6e` branch tests the pair-verify pointer, but on the null
  branch it does not test the ordinary base-key initialized marker at session
  `+0x258`;
- it passes the 16 bytes at `+0x260`, length 16, and the request's nonzero
  `streamConnectionID` to `AirPlay_DeriveAESKeySHA512ForScreen` and installs the
  result with `AirPlayReceiverSessionScreen_SetSecurityInfo`;
- exact derivation constructs the literal salts `AirPlayStreamKey` and
  `AirPlayStreamIV`, appends the connection identifier, hashes each salt then
  the supplied base key with SHA-512, and retains 16 bytes for each result. No
  additional secret is read by these exact derivation bodies.

A complete direct constant-offset disassembly inventory found one explicit
store to the session base key (`0x1759e`, in
`AirPlayReceiverSessionSetSecurityInfo`) and one explicit address use
(`0x1b809`, in the screen branch). This inventory does not exclude indirect
aliases or another object's writes, so the result is stated for a **fresh,
zero-initialized session following the exact missing/None callback branch**.

Therefore, under those exact static conditions, MFi-SAP is not a necessary
cryptographic prerequisite for configuring the screen parser route. The route
still enables AES-CTR before parsing; the finding is that its base material is
then deterministic and not MFi-hardware-backed, not that raw socket bytes are
passed through as cleartext. Upstream authorization, control-session acceptance,
session start, port reachability, and socket delivery remain independent gates.

## Body-security branches

The recovered body-processing code distinguishes two states before calling
`ScreenStreamProcessData`:

- pair verify: ChaCha20-Poly1305 decrypts the body and verifies its tag before
  parser dispatch; and
- null pair verify: AES-CTR decrypts in place when its initialized flag is set,
  with no body authentication check in that branch.

The exact setup branch installs one of those states when its key initialization
succeeds. The pair-verify route therefore retains a valid-key and valid-tag
prerequisite. The no-MFi candidate is confined to the null-pair-verify AES-CTR
route.

## Exact identities and ranges

| Object | Size | SHA-256 |
|---|---:|---|
| `libAirPlay.so` | 215,896 | `ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0` |
| `libCoreUtils.so` | 1,200,368 | `9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae` |

Principal byte-bound ranges are:

| Role | Object | Range | SHA-256 |
|---|---|---|---|
| callback encryption branch to session setup | `libAirPlay.so` | `0x103c3..0x10637` | `5cde34310a8cdf36004c110ed3f9656dbdadaacf2b808fb12dc057e1fce57a81` |
| fresh receiver-session creation | `libAirPlay.so` | `0x16e90..0x172c2` | `1a4852541d7e277ff9b2de1b7d0cff7bb9795cb930ec5fe178e7be9f11c7bc62` |
| explicit fresh-session clear | `libAirPlay.so` | `0x16ec4..0x16f23` | `5790f507c7df6f73bb0f512a7f81454dfca0fd4a2df3ca0d3690a81e50951eda` |
| session base-key setter | `libAirPlay.so` | `0x17515..0x175d5` | `7b8cee275a7702e4c9948e380144ecae461b03dc9a3d336d3e94fb042a9ba64b` |
| screen type dispatch | `libAirPlay.so` | `0x19f3f..0x19f71` | `24a836755508aba236f508184264747e42fb1d6d3ef8edd7eb91598d26adab7d` |
| screen security/listener branch | `libAirPlay.so` | `0x1b665..0x1b92b` | `494935dce8d51a8da5cb51ebd00fa6d9b5236f5d1e2565bffea52c5c3b4f6b63` |
| screen thread start | `libAirPlay.so` | `0x134f0..0x135d6` | `47a54d3ebb0561039dd3fb779d7edbd6f6088d3e39fd4e21dc78c80a42aba59e` |
| accept-to-parser thread | `libAirPlay.so` | `0x135d6..0x138f5` | `9833c94f4dddfd8ca3199fc34dc146ed4f9d2f129be2133798d39da2bcdaf0f6` |
| screen body crypto dispatch | `libAirPlay.so` | `0x1f5e5..0x1f74c` | `146bc2d367c4eecb4e4d9822e2f8f47d0e892a34f0376f5595b14628459d67b3` |
| SHA-512 key derivation | `libAirPlay.so` | `0x21234..0x2135a` | `b94de2155c65cd4269b8d7d45a55bdd89d514c0c79e06937aa6c1fadd249d60a` |
| screen salt/ID derivation wrapper | `libAirPlay.so` | `0x2135a..0x21478` | `1e5e4c0fa02925c4985e5adcd42924bac894fa9ab2799095f4a2fdefda9a9c11` |
| missing-value integer semantics | `libCoreUtils.so` | `0x43d18..0x43d87` | `be58439ad302800e4b0330e1d8120ff2be822aab800238e7220ee4e71badb202` |
| socket accept wrapper | `libCoreUtils.so` | `0x87ae3..0x87ccc` | `91f051bbf297b0b5adca67abbb9c61cc161f6afa9023ba55228efd226fc343f2` |
| wildcard server socket | `libCoreUtils.so` | `0x88f84..0x89420` | `2f850a99c9164348285e59b94c967255d8b5f6223912d069ee486ebef77a05ee` |

The public `45clouds/WirelessCarPlay` snapshot at commit
`51145ef55f8dd9f1cbadd58353cacb5e0ca215e9` supplies comparative names and
protocol semantics. Recovered bytes, not that source, establish the exact route.

## Security consequence and boundary

This result lowers one **static prerequisite** for the already established
screen-parser candidate: on the fresh missing/None encryption path, no successful
MFi-SAP certificate/signature exchange or MFi-derived base key is required by
the reviewed screen setup code. It also proves that the secondary parser socket
is opened on a wildcard address and that this caller does not request a peer
address at accept time.

It does **not** prove:

- an upstream generic `HTTPConnection` authorization bypass;
- live `SETUP`, session-start, or secondary-socket eligibility;
- a reachable listener on USB/NCM, Wi-Fi, Ethernet, or another interface;
- phone or network-peer delivery, port discovery, or a completed connection;
- a crash, allocator overwrite consequence, process exit, or restart behavior;
- reliable code execution, SMACK escape, unrestricted root, or persistence;
- CVE-2025-30422 or any other CVE identity; or
- applicability to the owner's installed unit.

The prior parser result remains an exact-static CWE-125/CWE-787 candidate. This
route analysis does not promote it to a demonstrated exploit.

## Deterministic artifact

- tool: `tools/uk_fw/airplay_screen_route_security_audit.py`
- tests: `tests/test_airplay_screen_route_security_audit.py`
- schema: `ioniq-airplay-screen-route-security-audit/v1`
- report: `evidence/artifacts/projection-candidates/airplay-screen-route-security.json`
- report size: 16,458 bytes
- report file SHA-256: `aae4dcec49e0e0a36c86f34cb721cf1f97e4883b656bf2ec5c36ce5fb4433166`
- embedded canonical SHA-256: `9e69506830676153ca09737ae86cc28ce88cf4db151e953fa5a57683419cb447`

Validation passed with 5 focused tests, 20 projection-focused tests, and the
canonical suite: 1,090 tests plus 352,357 subtests in 161.57 seconds. The full
suite log SHA-256 is
`41633edf1836def9551a721507935e2bd2ac60330241a0aeb130e15b1e2d946a`.
`py_compile`, strict ASCII JSON decoding, deterministic reproduction,
exclusive no-overwrite behavior, and path-limited `git diff --check` also
passed.
