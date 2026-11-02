# iAP2 local-socket framing and transaction-boundary audit

## Scope and verdict

This is an offline exact-static audit of the recovered local IPC between
`libiAP2AppFramework-2.0.so` and `iAP2Service-2.0`. No recovered executable was
run. No socket was created or connected, no iAP2/CarPlay message was constructed,
and no device, USB endpoint, radio, or network interface was used.

The recovered implementation establishes four exact-static candidates:

1. **heap out-of-bounds write:** a local stream client can declare a total
   transaction size below the fixed 64-byte header; the service allocates the
   smaller size and copies all 64 bytes before its lower-bound branch;
2. **transaction-tail out-of-bounds read:** marshal parsing starts after the
   64-byte header but treats total transaction size as payload remaining, so
   accessors may accept reads extending by as much as 64 bytes beyond the
   allocation;
3. **uninitialized header/body consumption:** both receiver directions accept a
   positive short `MSG_WAITALL` return rather than requiring the requested byte
   count; and
4. **resource exhaustion:** the UID-zero service applies no reviewed maximum to
   the client-supplied `uint32` total before `malloc` and a blocking body receive.

The server pathname, framing code, configured credentials, and broad intended
SMACK relationship are exact. A live socket, actual runtime inode metadata,
connect success, physical phone delivery, allocator corruption, disclosure,
crash, code execution, root, persistence, CVE identity, and installed-unit
applicability remain unproved.

## Exact subjects

| Object | Size | SHA-256 |
|---|---:|---|
| `libiAP2AppFramework-2.0.so` | 190,272 | `d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120` |
| `iAP2Service-2.0` | 633,216 | `38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e` |
| `carplay_iAP2.service` | 397 | `f7cf915509005a4aaa18d09e3a6ccd0abdd72ef2b2816641ea9a592a1e3f4495` |
| `smack-relabel-ro.sh` | 6,206 | `8275625764c30b6e82d99e5fdf887038261f97e9f0ef5a36da8faa743a35a15f` |
| `accesses.d/projection` | 831 | `978ccab43e6724df0bb74c4f84e3319ab3f0022dec442f4389fba140f6b3c1c9` |

Ghidra mapped the ELFs at image base `0x100000`; all code addresses below are
normalized ELF virtual addresses after subtracting that base.

## Exact local endpoint

The framework connector at `0x1ee57..0x1f15d` calls
`socket(AF_UNIX, SOCK_STREAM, 0)`, builds `/tmp/iAp2Socket`, and calls `connect`.
The matching service listener at `0x2e542..0x2e89d`:

1. calls `umask(0)`;
2. unlinks `/tmp/iAp2Socket`;
3. calls `socket(AF_UNIX, SOCK_STREAM, 0)`;
4. binds the pathname and restores the previous umask; and
5. listens with backlog 5.

The bind-time DAC creation mode is therefore `0777` before parent-directory,
mount, and LSM checks. The unit has no `User=` directive, so systemd's configured
default is UID 0. The relabel script maps `iAP2Service-2.0` to
`App::projection`.

The exact accept-to-header-receive path contains no peer-credential check. The
binary has no direct imported `getsockopt`, `getpeereid`, or credential-query
symbol. This does **not** prove universal access: parent `/tmp` traversal, actual
socket mode/owner/label, transmutation, loaded SMACK rules, task labels,
capabilities, namespaces, and indirect/inlined checks remain distinct runtime
gates.

## SMACK relationship

Linux 4.1 Smack Unix stream connect checks require write permission in both
directions unless an applicable override capability succeeds. Across the
recovered `accesses.d` corpus, these 19 labels have `w` in both directions with
`App::projection`:

- `_`;
- `App::bluetooth`, `App::camera`, `App::dlt`, `App::engineermode`;
- `App::euradio`, `App::home`, `App::locationmanager`, `App::manager`;
- `App::mediaplayer`, `App::micommanager`, `App::mpautotest`, `App::navi`;
- `App::setup`, `App::standbyclock`, `App::tms`, `App::upgrade`;
- `App::userprofilemanager`; and
- `App::vh`.

This is an exact configured policy relationship, not proof that every listed
process exists, has that runtime label, can traverse `/tmp`, or successfully
connects.

## Service receiver framing

The service thread is `0x2d64a..0x2e542`. For each accepted client it:

1. calls `recv(fd, stack_header, 0x40, MSG_WAITALL)` at `0x2daf6`;
2. accepts any return greater than zero rather than requiring `0x40`;
3. loads a zero-extended `uint32` declared total from stack-header offset
   `0x38`;
4. calls `malloc(declared_total)` at `0x2dce3`;
5. performs eight unconditional qword stores copying the complete stack header
   to the allocation at `0x2dd2c..0x2dd89`;
6. only then tests `declared_total <= 0x40` at `0x2dd8a..0x2dd9b`;
7. for larger totals, requests `declared_total-0x40` bytes at allocation offset
   `0x40`, again with `MSG_WAITALL`;
8. accepts any positive body return, not only the requested count; and
9. dispatches the allocation to `handleClientCmd()` on both the at-most-64 and
   positive-body branches.

### Exact local command dispatch

`handleClientCmd()` is byte-bound at `0x2ea28..0x2f1ad`, SHA-256
`b49918f988a4060fbd76847f0e1f6000999a7ae676267ff99d7e37709d18c9e3`.
Its command switch contains direct calls to all 11 functions in the recovered
`iAp2MarshalGetBytes` inventory and to both identification paths that use the
heap-string materializer: `SessionConnection` and `SessionIdentification`.
This closes accepted local transactions to the reviewed command parsers without
requiring an inferred callback. Per-command IDs, current-session predicates,
and field-level parser conditions still apply; no command was constructed or
sent.

### Declared total below 64

For a value from 1 through 63, a non-null `malloc` result is followed by 64
bytes of fixed stores. The branch that recognizes the small value occurs only
after those stores. This is an exact-static local AF_UNIX heap out-of-bounds
write candidate (CWE-787), conditional on local admission and allocator
behavior.

A declared zero can also reach the fixed stores if `malloc(0)` returns non-null;
that implementation-dependent subcase is not needed for the 1..63 candidate.

### Positive short reads

`MSG_WAITALL` can return a positive short count when interrupted, closed after
partial delivery, or otherwise unable to complete after receiving some bytes.
The stack header is not cleared before receive. A short positive header can
therefore leave unread stack fields in use, potentially including offset
`0x38`. A short positive body leaves an uninitialized malloc tail inside the
nominal transaction before dispatch. This is an exact-static uninitialized-data
consumption candidate (CWE-457), not a demonstrated leak or crash.

### Large totals

No reviewed maximum precedes `malloc(declared_total)` or the blocking body
receive. This is an exact-static local resource-exhaustion candidate (CWE-400).
Practical memory, scheduling, timeout, supervisor, and user-visible effects are
unknown.

## Framework receiver symmetry

The framework event thread at `0x1fcf4..0x2052f` repeats the same important
structure for service-to-application events:

- nominal 64-byte `MSG_WAITALL` header receive with only a positive-return check;
- `malloc` of the header's `uint32` total;
- fixed 64-byte copy before the lower-bound branch; and
- body receive and application callback dispatch.

The same undersized-total and short-read mechanisms therefore exist in the
opposite IPC direction. A hostile replacement server, path-hijack race, or
malicious service-to-framework event route has **not** been established.

## Total-size semantics and the 64-byte parse overstatement

The field at header offset `0x38` is not merely named by inference. All 37 exact
direct callers of service function `0x2be82` (`SendEventToApp`) follow the same
construction:

1. initialize a marshal writer with initial offset `0x40`;
2. marshal event fields;
3. call `iAp2MarshalGetUsedSize`;
4. store that value at event offset `0x38`; and
5. pass the event and that same used size to the forwarding function, which
   supplies it to `send(..., MSG_NOSIGNAL)`.

`iAp2MarshalGetUsedSize` includes the initial offset. On a successful empty
transaction its minimum used size is 64. Both receiver directions allocate the
field value and receive `value-64` body bytes. The field is therefore total
transaction size including the header.

`iAp2MarshalInitFromTxn` at `0x210ff..0x21175` does something inconsistent:

- parse pointer = `transaction + 0x40`;
- current pointer = parse pointer;
- remaining = `*(uint32_t *)(transaction + 0x38)`; and
- no `remaining -= 0x40` occurs.

The marshal state's remaining count exceeds true allocation-tail availability
by exactly 64. Fixed-width accessors and the recovered `iAp2MarshalGetBytes` can
therefore accept a span extending by as much as 64 bytes beyond the allocation.
The direct byte-accessor consequences and caller boundaries are documented in
[`iap2-marshal-getbytes-caller-audit.md`](iap2-marshal-getbytes-caller-audit.md).
This is an exact-static transaction-tail out-of-bounds read candidate (CWE-125),
not a demonstrated disclosure.

## Producer arithmetic follow-up

Of the 37 direct event producers, 28 use fixed capacities and nine use unchecked
32-bit capacity expressions:

| Producer role | Capacity expression |
|---|---|
| device information | `(length + 0x50) * 4` |
| device language | `(length + 0x50) * 4` |
| device UUID | `(length + 0x50) * 4` |
| external-accessory receive data | `length + 0x58` |
| Wi-Fi information | `(length_a + length_b + 0x68) * 4` |
| file-transfer call UUID | `(length + 0x58) * 4` |
| file-transfer playlist | `(length + 0x68) * 4` |
| call-state strings | `(five lengths + 0xc0) * 4` |
| call-state address | `(length + 0x6230) * 4` |

Each range is separately hashed in the artifact. These formulas can wrap in
`uint32`, but that fact alone is not promoted to a remotely reachable overflow.
Exact upstream length ceilings, allocation feasibility, marshal-writer failure
semantics, ignored statuses, and phone-to-callback delivery remain under review.
The 37-producer inventory does establish ordinary successful first-party output
as total-size framing with a minimum of 64; it does not sanitize hostile local
client framing.

## Reproduction

```sh
<platformio-env>/bin/python3 tools/uk_fw/iap2_local_socket_framing_audit.py \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libiAP2AppFramework-2.0.so \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/iAP2Service-2.0 \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/systemd/system/carplay_iAP2.service \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/etc/smack-relabel-ro.sh \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/etc/smack/accesses.d \
  --output /tmp/iap2-local-socket-framing-audit.json
```

Tracked artifact:

- path: `evidence/artifacts/projection-candidates/iap2-local-socket-framing-audit.json`
- schema: `ioniq-iap2-local-socket-framing-audit/v1`
- tool version: `1.0.0`
- size: `65,111` bytes
- file SHA-256: `4aa88a9460cec0f02aad25e8a6ebef41231b2480dec669abe447447b360af728`
- canonical SHA-256: `2246011e805b39b9f38d1a3af674d299fd0fe782dc8a67c8c5bee7d1f0826336`

The tool uses stable no-follow reads, stable directory membership and file
identity checks, exact hashes, file-backed ELF `PT_LOAD` mapping, instruction
anchors, direct-rel32 call inventory, strict ASCII policy parsing, canonical
ASCII JSON, and exclusive no-overwrite output creation.

## Boundaries

This audit does **not** demonstrate:

- a live `/tmp/iAp2Socket`, its actual mode/owner/label, or a successful
  connection from an untrusted process;
- physical phone, USB/NCM, AirPlay, Bluetooth, or network delivery to the local
  framing code;
- iAP2/CarPlay authentication or session-state bypass;
- that the owner's installed unit runs either exact binary;
- allocator corruption, a process crash or restart loop, attacker-visible
  disclosure, reliable control-flow influence, code execution, unrestricted
  root, SMACK escape, persistence, or firmware modification;
- a CVE identity, public exploit identity, or affected-versus-fixed SDK mapping;
  or
- complete indirect-producer, unextracted-file, or alternate-build coverage.
