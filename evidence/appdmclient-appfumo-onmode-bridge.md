# AppDMClient → AppFUMO priority-mode bridge

## Result

**Exact-static continuity is established, but runtime delivery and impact remain
unknown.** The recovered AppDMClient mounted-source callback carries its first
QString through the staging and checker path into a session-bus signal. The
selected embedded AppFUMO subscribes with empty service and path filters, fixed
interface and member filters, forwards the matching logical arguments through
Qt row 69, stores the source pathname in global QString `0x6d4fa8`, checks a
readiness predicate, and conditionally calls the What's New copy function.

This closes the static cross-binary path to the conditional copy call. It does
not establish that both processes participate in the same runtime bus, that a
signal is delivered, that the slot runs, that readiness succeeds, or that a copy
completes.

## Canonical binding

The deterministic analyzer binds all conclusions to:

- canonical rootfs SHA-256
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
- AppDMClient SHA-256
  `9a1fb796d7ac24fcce71c16e3dbee9306c888f43e705ee081f41b7d473978bd0`,
  Build ID `b2dbcc5231f444d8f1dd68eb7a2376323ce805df`;
- canonical outer updater SHA-256
  `5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0`;
- selected embedded AppFUMO structural extent SHA-256
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`,
  Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`.

The embedded selection starts at outer file offset `0x5721c8` and stops at its
structural extent of 5,066,264 bytes. Resource metadata, padding, and following
container data are excluded.

## Corrected subscription identity

The priority-mode subscription is the `QDBusConnection::connect` call at
`0xe308b` in FDE `[0xe2c30,0xe3296)`. Its service and path QString filters are
independently empty; its interface and member filters are fixed.

The earlier provisional attribution to `0xe2fc5` is superseded. That call is a
separate fixed-service, fixed-path, fixed-interface subscription whose member
bytes have a different SHA-256 identity. The package regression-tests this
distinction.

The emitter and corrected receiver use byte-identical interface and member
values. Public retained output records only normalized roles, lengths, and
SHA-256 identities:

| Role pair | Length | SHA-256 | Equal |
|---|---:|---|---|
| emitter/receiver interface | 43 | `35b9b701c51a53cd99d064f5e36c4a53866b0d6640547064fe8b984497867c5f` | yes |
| emitter/receiver member | 14 | `3fc391aa95b1e4284d7516044213fd4f4023e344be926a9e60ac56de59f00bee` | yes |

The emitter's fixed signal path is not compared to the receiver because the
corrected receiver path filter is empty.

## Exact static chain

### AppDMClient producer

1. Mounted-source callback FDE `[0x84700,0x84e2d)` accepts the callback's first
   QString when the selected index is one.
2. It copies that QString into object field `+0x128` and passes a QString copy to
   staging at `0x849a7`.
3. Staging FDE `[0x7ff60,0x830e4)` passes the copied source to checker FDE
   `[0x67e30,0x69144)` at `0x8079d`.
4. At selected call `0x685e7`, the checker supplies a fixed accepted-state
   enumerand, the parsed/reference-version QString as the first string, and the
   checker source QString as the second string.
5. Sender FDE `[0x4f1c0,0x4f58a)` constructs a signal, appends logical arguments
   in `int, QString, QString` order, obtains the session bus, and invokes signal
   send.
6. The whole-text direct-call inventory to the sender is exactly `0x685e7`,
   `0x8573f`, `0x8595f`, and generated forwarding `0x109766`.
7. Calls `0x8573f` and `0x8595f` construct empty QString arguments; they are state
   notifications, not removable-source pathname producers.

### AppFUMO receiver and conditional consumer

1. The corrected subscription at `0xe308b` has wildcard service/path matching
   and fixed interface/member matching.
2. Generated row 69 at `0x16e66c` forwards logical `(status, version,
   source-path)` at `0x16e6da` to body FDE `[0x10f4a0,0x10fa30)`.
3. The body stores:
   - status at `0x6d4fb8`;
   - version at `0x6d4fb0`;
   - source path at `0x6d4fa8`.
4. The accepted-state case checks local object state and calls readiness
   predicate FDE `[0xfed10,0xff280)`.
5. Only a nonzero readiness result reaches the copy call at `0x10f995`.
6. The alternate local request path is not a copy invocation.
7. Copy FDE `[0x101110,0x104c1b)` selects global `0x6d4fa8` as its package base
   in accepted mode and constructs the top-level archive class as the package
   base plus a fixed hidden archive basename.

The static chain therefore establishes pathname-value continuity to a
**conditional** copy call, not unconditional copying or successful I/O.

## Canonical session-bus boundary

The canonical session configuration has:

- session bus type;
- a Unix temporary-directory listener class;
- `EXTERNAL` authentication declaration;
- default allow rules for send, receive, and name ownership;
- a session policy include directory with no regular canonical members;
- an optional local include that is absent in the canonical archive.

These policy facts are not runtime reachability facts. They do not establish
socket access across credentials or SMACK labels, same-bus participation,
service ownership, sender identity, successful Qt connection setup, queueing,
delivery, or slot execution. Empty service/path filters widen matching after bus
admission; they do not authenticate a sender. Fixed interface/member matching
identifies message vocabulary, not origin.

## Deterministic analyzer

Tracked package:

- `tools/uk_fw/appdmclient_appfumo_onmode_bridge.py`;
- `tests/test_appdmclient_appfumo_onmode_bridge.py`;
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-manifest.json`;
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge.json`;
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-exact-static.txt`.

The analyzer streams the canonical archive, validates its complete normalized
inventory, compares the supplied AppDMClient to its canonical member, validates
the selected embedded ELF's structural extent against the canonical outer
updater, checks Build IDs, hashes complete instruction and FDE inventories,
verifies selected FDEs and anchors, inventories direct transfers, parses the
canonical session configuration, and scans public output for prohibited values
and supplied paths.

Generic reproduction form:

```text
<platformio-env>/bin/python3 tools/uk_fw/appdmclient_appfumo_onmode_bridge.py \
  --appdmclient <reviewed-appdmclient> \
  --appfumo <structurally-selected-appfumo> \
  --rootfs <canonical-rootfs> \
  --objdump <identity-bound-llvm-objdump> \
  --readelf <identity-bound-llvm-readelf> \
  --manifest evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-manifest.json
```

The analyzer emits UTF-8 with fixed LF through `sys.stdout.buffer`; hostile
`PYTHONIOENCODING` regeneration is byte-identical. It rejects duplicate JSON
keys, Boolean-as-integer values, schema drift, unsafe or duplicate archive
names, links and special selected members, changing/non-regular/oversized
inputs, canonical member or inventory drift, embedded-extent drift, LLVM tool
identity drift, complete instruction/FDE drift, selected FDE and anchor drift,
direct-transfer drift, literal drift, contradictory runtime promotions, and
privacy-sensitive output.

## Scope and non-claims

Established:

- exact canonical binary and archive identities;
- exact AppDMClient callback → staging → checker → signal-sender continuity;
- exact cross-binary interface/member byte equality;
- corrected wildcard service/path subscription identity;
- exact row-69 argument forwarding and global assignments;
- accepted-mode readiness gating and conditional copy call;
- accepted-mode package-base selection from the row-69 source-path global.

Not established:

- runtime same-bus participation or socket reachability;
- sender identity, sender influence, signal delivery, or slot execution;
- readiness success, file presence, copy success, or byte identity;
- verifier acceptance, command success, code execution, uid/SMACK impact, root,
  partition writes, boot acceptance, rollback behavior, or persistence.

No recovered target executable was run; no bus was contacted; no signal,
method, media, packet, update action, flash operation, or persistence mechanism
was created.
