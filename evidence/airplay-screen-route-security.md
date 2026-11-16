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

## Exact generic HTTP dispatch

The exact generic `HTTPConnection` state machine removes one previously retained
ambiguity. `libAirPlay.so` installs the AirPlay HTTP callback at `0xf3d1` into
the connection delegate at `0xc7a7`. Exact
`HTTPConnectionSetDelegate` copies that function pointer to connection offset
`+0x50`. After `HTTPMessageReadMessage` succeeds, the exact state machine only
maps I/O errors and calls `LogHTTP` before invoking the function pointer at
`+0x50`. There is no separate authorization or pair-state check in that
post-read generic dispatcher.

Together with the previously reviewed callback-local `SETUP` dispatch, this
closes a distinct generic `HTTPConnection` gate between a completed request and
the AirPlay callback. It does not establish how a peer reaches the control
connection, whether admission or policy exists before the generic state machine,
or whether another component restricts the underlying interface.

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
| AirPlay HTTP delegate install | `libAirPlay.so` | `0xc750..0xc7d2` | `89012ad230f7302e6d6d77fa90b67db910e417c929eb2ac1208adc6195c75ba5` |
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
| HTTP delegate setter | `libCoreUtils.so` | `0x75e63..0x75eb1` | `03bbd091b0ecba150867d6a1b022ad866bf2e126b1a151bf5c62039834a1ceaa` |
| HTTP connection state machine | `libCoreUtils.so` | `0x76e94..0x77153` | `4130bd9de44106e7e08f072cbd83da4fccd2fcacffffb533c23ee3f62a6e473e` |
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

- absence of authorization or admission policy before completed-message
  dispatch or elsewhere outside the reviewed generic `HTTPConnection` path;
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
- tool version: `1.1.0`
- report: `evidence/artifacts/projection-candidates/airplay-screen-route-security.json`
- report size: 18,738 bytes
- report file SHA-256: `29c979bbdbdfa3bb3e5b95edc2c0e1204c1d5ae96fd2135602be8c927529d801`
- embedded canonical SHA-256: `ce6e1747bf5763efe99acff725a6b7598b11397d9626d8dc474b861eb307633b`

Validation passed with 5 focused tests, 20 projection-focused tests, and the
canonical suite: 1,090 tests plus 352,357 subtests in 173.51 seconds. The full
suite log SHA-256 is
`03a440e14e6a3f629359a00d04ca7900590d54108a1ed21d191b7ab39411d250`.
`py_compile`, strict ASCII JSON decoding, deterministic reproduction,
exclusive no-overwrite behavior, and path-limited `git diff --check` also
passed.
