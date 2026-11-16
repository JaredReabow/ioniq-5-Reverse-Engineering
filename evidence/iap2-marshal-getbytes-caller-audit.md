# iAP2 marshaled-byte direct-caller audit

## Scope and verdict

This is an offline exact-static audit of `iAp2MarshalGetBytes` and its recovered
callers. No recovered target executable was run, no iAP2 or CarPlay message was
constructed, and no device, USB endpoint, radio, or network interface was used.

The earlier helper-local conclusion needs a transaction-wide qualification.
The generic accessor performs no copy and enforces the `remaining` value stored
in its marshal state. The exact transaction initializer, however, advances the
parse pointer past the 64-byte header while seeding `remaining` with the
**unreduced total transaction size**. The companion local-socket framing audit
proves that header field `+0x38` is total size, not payload size. The effective
parse bound is therefore 64 bytes past the allocation.

The complete recovered direct-call inventory now identifies three distinct
exact-static candidates:

1. a **transaction-tail out-of-bounds read candidate** of up to 64 bytes through
   otherwise locally bounded marshal accessors;
2. a **null-source denial-of-service candidate** in the heap-string materializer
   used by identification commands; and
3. **unbounded string-read candidates** where length-delimited byte pointers are
   passed to `%s` logging without a local terminator check or precision bound.

The local AF_UNIX audit establishes a candidate local-client route, not physical
phone delivery. None of these candidates establishes a live crash, attacker-
visible disclosure, code execution, root, persistence, CVE identity, or
applicability to the owner's installed unit.

## Exact subjects

| Object | Size | SHA-256 |
|---|---:|---|
| `libiAP2AppFramework-2.0.so` | 190,272 | `d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120` |
| `iAP2Service-2.0` | 633,216 | `38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e` |

Only these two files under the recovered `extracted-safe` tree carry the exact
symbol string. The framework defines it; the service imports it. This excludes
another ordinary ELF import with that symbol name in the reviewed tree. It does
not exclude a symbol-name-free function pointer, a wrapper already captured by
another name, runtime-generated code, an unextracted member, or another build.

Ghidra mapped both ELFs at image base `0x100000`; addresses below are normalized
ELF virtual addresses after subtracting that base.

## Helper-local bound and transaction-wide overstatement

Exact ranges:

| Role | Range | SHA-256 |
|---|---|---|
| `iAp2MarshalInitFromTxn` | `0x210ff..0x21175` | `4e7fbd707234bf553adf0c59de1501865d873ebeae4ee058f59139124dbf5729` |
| aligned span accessor | `0x21645..0x2176a` | `98cbc5af41238b006a7497dfce512b59c21b448f616a55ff641597a058303fcf` |
| `iAp2MarshalGetBytes` | `0x21a56..0x21b21` | `601fc208cd6c41eb6926c782dcafcedd47c88785516c98c1290ebcdd2e08ac31` |

The exact implementation:

1. rejects a null marshal state or null length-output pointer;
2. reads a `uint32` declared length and stores it through the output pointer;
3. rejects values above `UINT32_MAX-3` before alignment;
4. rounds the consumption length up to four-byte alignment;
5. compares that aligned length with the marshal state's remaining byte count;
6. on failure, sets remaining to zero, sets state flag bit 1, logs, and returns
   null;
7. on success, returns the current transaction pointer and advances pointer and
   remaining count by the same aligned length.

The helper returns an interior pointer into the transaction. It does not
allocate a destination and does not copy bytes into a fixed stack object. This
closes the generic helper as the public Sony/Alpine-style fixed-stack-copy
primitive.

Two details become important downstream:

1. the declared length is written to the caller's output field *before* the
   aligned-span accessor can fail, and the failure branch does not clear that
   output field; and
2. at `0x21126..0x2115e`, `iAp2MarshalInitFromTxn` sets the parse pointer to
   `transaction+0x40`, but loads the `uint32` at transaction offset `0x38`
   directly into `remaining` without subtracting `0x40`.

The independently byte-bound local-socket and producer audit establishes the
second field's semantics. All 37 direct `SendEventToApp` producers initialize
marshaling with offset `0x40`, store `iAp2MarshalGetUsedSize()` at `+0x38`, and
send that many bytes. Both socket receivers allocate exactly the `+0x38` value
and receive only `value-0x40` body bytes. Thus `+0x38` is total transaction size
including the header.

The parser begins at the true payload start but treats total size as payload
remaining. The helper's aligned check can consequently accept a returned span
that extends by as much as 64 bytes beyond the transaction allocation. The
helper remains unlike the public fixed-stack-copy primitive, but it is not an
allocation-accurate transaction bound in this recovered integration.

## Transaction-tail out-of-bounds read candidate

The overstatement is constant: at every point after initialization, declared
remaining exceeds the true bytes to the allocation end by 64. Fixed-width get
helpers may therefore read beyond the transaction tail, and
`iAp2MarshalGetBytes` can return an interior pointer plus a declared length whose
accepted span crosses that tail by up to 64 bytes.

This matters to the direct callers rather than merely to the helper body. The
heap-string materializer can pass such a non-null pointer and accepted length to
`strncpy`; the plain-`%s` consumers can begin or continue source traversal past
the transaction; and the pointer-plus-length aggregates require downstream
copy/callback review. This is an exact-static heap out-of-bounds **source read**
candidate, not a demonstrated disclosure or process fault. A specific command,
downstream sink, local-client admission, resulting output, and runtime impact
must still be established separately.

## Complete direct static call inventory

There are 31 exact PLT calls in 11 reviewed service functions.

| Recovered source identity | Commands containing byte fields | Calls | Local handling |
|---|---|---:|---|
| heap-string materializer `0x2957c..0x296a7` | wrapper | 1 | allocates `length+1`, zeroes, then `strncpy(..., length)` |
| `SessionBTConnection.cpp` | `0x2f1d`, `0x2f1e` | 2 | retains pointer+length; right-shifts two lengths before dispatch |
| `SessionLocation.cpp` | `0x2eff` | 7 | seven optional pointer+length pairs in a stack aggregate |
| `SessionAppLaunch.cpp` | `0x2f45` | 1 | AppBundleID pointer+length; `%s` log; downstream dispatch |
| `SessionExternalAccessoryProtocol.cpp` | `0x2f8c` | 1 | pointer+length followed by `uint16`; downstream dispatch |
| `SessionHID.cpp` | `0x2f27`, `0x2f28` | 2 | HID pointer+length pairs; downstream dispatch |
| `SessionMediaLibraryUpdates.cpp` | `0x2f3b`, `0x2f3c` | 3 | library identifiers retained as pointer+length pairs |
| `SessionVoiceOver.cpp` | `0x2f68` | 1 | optional speak-text pointer+length |
| `SessionWiFiInformation.cpp` | `0x2f78` | 2 | two optional Wi-Fi pointer+length pairs |
| `SessionPlayMediaLibrary.cpp` | `0x2f81`..`0x2f84` | 5 | pointer+length pairs; command `0x2f84` logs its byte pointer with `%s` |
| `SessionCommunications.cpp` | `0x2fa3`, `0x2fa4`, `0x2fa5`, `0x2fa8`, `0x2faa` | 6 | destination/address-book/call UUID pairs; byte pointers logged with `%s` |

All 31 call instructions and each FDE-bounded caller range are byte-anchored in
the deterministic artifact. The companion local-socket audit also binds
`handleClientCmd()` `0x2ea28..0x2f1ad` directly to every listed caller function,
closing accepted local transactions to these parsers subject to command/session
predicates. The reviewed direct caller ranges contain no copy performed by
`iAp2MarshalGetBytes`; most retain pointer+length pairs and pass a stack
aggregate to a downstream handler. That conclusion is direct-caller coverage,
not a blanket clearance of every downstream callback.

## Identification null-source candidate

The materializer at `0x2957c..0x296a7`:

1. frees the previous destination pointer if non-null;
2. calls `iAp2MarshalGetBytes` at `0x295d5`;
3. allocates `declared_length + 1` bytes;
4. returns an allocation error only if `malloc` returns null;
5. zeroes the allocation; and
6. calls `strncpy(destination, returned_pointer, declared_length)` without first
   rejecting a null returned pointer.

For a small nonzero declared length larger than the transaction's remaining
span, the generic helper can return null while retaining that declared length.
If the correspondingly small allocation succeeds, the wrapper supplies the
null pointer to `strncpy` with a nonzero count. This is an exact-static
null-source fault candidate, not a demonstrated process crash.

The wrapper is not orphaned. There are 22 exact calls from two complete
FDE-bounded command handlers:

| Handler | Range | Command | Wrapper calls | Range SHA-256 |
|---|---|---|---:|---|
| `SessionConnection.cpp` | `0x38010..0x3ab40` | `kCmdIdentificationSelect` `0x2afb` | 15 | `9a5af95a4f5f427a3cd0cbbcd60791f594cc25275381d768855f354dc84f5a3d` |
| `SessionIdentification.cpp` | `0x556e2..0x55e2c` | `kCmdIdentificationUpdate` `0x2f95` | 7 | `b63fd6951214ff2c6f1a39caaaaf186cfc405868b828c29ec7e50a6ee155320a` |

The update fields include ProductName, ModelIdentifier, Manufacturer,
SerialNumber, FirmwareVersion, HardwareVersion, and CurrentLanguage. The
selection handler materializes additional identification/capability strings.
This binds the mechanism to recovered iAP2 command handlers, but not to a
physical peer, authenticated session, or accepted runtime command.

## `%s` string-read candidates

Several direct callers pass length-delimited byte pointers to the logger using
plain `%s`. The reviewed ranges contain no preceding local terminator check and
no precision bound such as `%.*s`:

- `SessionAppLaunch`, command `0x2f45`;
- `SessionPlayMediaLibrary` command `0x2f84`; and
- six recovered fields across the listed `SessionCommunications` commands.

If a received byte field lacks a null terminator within its declared extent,
plain `%s` can continue reading beyond that logical field until another null is
encountered. This is an exact-static unbounded-source-read candidate.

The logger is now also exact. Its complete FDE is `0x6fa6..0x7277`, SHA-256
`3a866c421d32438553f151f347a2e7c04fd153a447281aa64625a774d51610ae`.
It builds a prefix in a `0x400`-byte stack buffer, computes the remaining
capacity, and calls `vsnprintf` with only that remainder before passing the
resulting string to the downstream logging sink. A stack canary protects the
frame. This bounds formatted output and excludes a demonstrated logger
*destination* overflow on the reviewed path; it does not make plain `%s`
length-aware with respect to the source field. The source-read extent and effect
still depend on transaction allocation, alignment padding, protocol conformance,
and libc formatting behavior. No live disclosure, crash, log consumer, or
attacker-visible boundary is established.

## Reproduction

```sh
<platformio-env>/bin/python3 tools/uk_fw/iap2_marshal_getbytes_audit.py \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libiAP2AppFramework-2.0.so \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/iAP2Service-2.0 \
  --output /tmp/iap2-marshal-getbytes-audit.json
```

Tracked artifact:

- path: `evidence/artifacts/projection-candidates/iap2-marshal-getbytes-audit.json`
- schema: `ioniq-iap2-marshal-getbytes-audit/v1`
- tool version: `1.2.0`
- size: `31,652` bytes
- file SHA-256: `0437b91abb2d48f844616594f0d7c7a26bed255171adc768fb4d9bdaa777887a`
- canonical SHA-256: `366d116d6154d6245c4fae6937b4f8666185183b665cd9bc877f6feb1161d8b2`

The tool uses stable no-follow reads, exact identity checks, ELF PT_LOAD address
mapping, exact range hashes and instruction anchors, ASCII canonical JSON, and
exclusive no-overwrite output creation.

## Boundaries

This audit does **not** demonstrate:

- that a physical phone, USB/NCM peer, or network peer reaches either command on
  this recovered service;
- successful iAP2 admission, authentication, identification state, or session
  eligibility;
- that the owner's installed unit runs either exact binary;
- a process crash, restart loop, attacker-visible disclosure, reliable memory
  corruption, control-flow influence, code execution, root, SMACK escape,
  persistence, or firmware modification;
- a public CVE identity or affected-versus-fixed SDK mapping; or
- complete indirect-call, unextracted-file, or alternate-build coverage.
