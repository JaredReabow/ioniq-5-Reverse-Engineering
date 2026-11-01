# AppFUMO boot-activation boundary

Status: exact-static, execution-free analysis of the recovered embedded FUMO
ELF and a streamed audit of the canonical rootfs archive. No recovered target
code, updater, helper, service, boot component, or rootfs executable was run.
No update, reset, recovery, slot, boot, mount, write, or persistence action was
attempted.

## Result

The completion resource contains an active countdown timer whose zero-count
branch emits the normalized `reboot-clicked` signal. The `UpdateView`
constructor at `[0xdea90,0xdf6ac)` connects that root-object signal to the
view's normalized `start-reboot` signal using Qt auto connection type. Its Qt
metadata declares `start-reboot` as local signal index zero, and generated dispatch
`[0x16d430,0x16daad)` maps index zero to a `QMetaObject::activate` path.

The controller constructor at `[0x135a80,0x135fa6)` separately connects the
view's `start-reboot` signal to the controller's normalized `reboot` slot using
Qt auto connection type. Controller metadata assigns that slot local method
index 12. Generated controller dispatch `[0x16f520,0x16fab3)` calls controller reboot
`[0x134ce0,0x134d79)` at `0x16f930`. Controller reboot calls the reset wrapper
`[0x146680,0x146711)` at `0x134d18`; the wrapper tail-jumps at `0x1466cc` to the
reset core `[0x145ca0,0x14667e)`. This closes the requested static completion-
QML-to-reset-request chain.

It does **not** close a boot-activation chain. The reset core constructs one
byte-array argument, appends one normalized reset-request byte, and sends the
request asynchronously. The argument has no slot identifier. Local send
acceptance and retry/fallback flow do not establish remote hardware action,
and
the operational fallback text is deliberately redacted from retained evidence.

## Separate reset and recovery paths

The generated dispatcher calls the separate reboot-system wrapper
`[0xe8c20,0xe8d06)` at `0x16e801`. That wrapper tail-jumps at `0xe8c92` to its
core `[0xe7810,0xe7fe1)`. This route also sends a one-byte normalized reset
request asynchronously, without a slot identifier. As in the completion-reset
core, local send failure enters bounded retry and terminal fallback flow; the
fallback text is redacted and local send success does not prove remote action.
The route is kept separate from the completion-reset chain.

Recovery notification setup `[0xe2790,0xe2c2b)` installs a system-bus
connection with wildcard sender service and path and hash-bound fixed
interface/member values. Retained evidence publishes only normalized roles,
not callable coordinates. Generated dispatch calls recovery slot
`[0x11f060,0x11f1a9)` at `0x16e8f6`. The slot checks a nonempty byte array and a
normalized last-byte recovery request plus local state gates, then tail-jumps
at `0x11f11c` to recovery-request construction `[0xe8d10,0xe907c)`.

The recovery request contains one normalized recovery byte and no slot
identifier. Its asynchronous send result does not control the return flow and
does not prove that an external controller changed mode.

## Boot-information observations

Boot-information request `[0xeeb00,0xeef10)` uses Qt's block-with-GUI call mode
with a 1,000 ms timeout and no outgoing arguments. The first reply argument is
converted to a byte array. A reply of at least 27 bytes supplies the byte at
offset 26 to the local status path; a short or absent result yields zero. The
meaning of that status value is not established.

Booting-type reader `[0x1122d0,0x112a58)` constructs `QSharedMemory`, binds the
hash-identified normalized `micom-status-message` key, requests/copies 35
bytes, and follows lock/copy/unlock/detach flow. Bytes at offsets zero and two
feed direct local selectors, and additional copied fields are parsed. The
producer, freshness/atomicity guarantees, and enum meanings remain unknown.
Nothing in this observation proves a persistent boot-slot choice.

## Canonical rootfs stream audit

The analyzer streams all `66,836` tar members and binds the canonical inventory
SHA-256
`c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`.
Selected members must have their exact canonical names and must be unique
regular files with empty link targets and exact type, mode, size, and content
hash. Aliases, duplicates, links, special files, and selected-member metadata
drift fail closed.

The two selected update-start scripts are label-management/checking scripts;
their mentions of inactive trees are labeling roots, not established slot
activation. The selected root-fsck service invokes the generic fsck helper for
the current root device and does not establish an inactive-slot selector.
Generic systemd system-update components, `bootctl`, and `fastboot` are
installed, but no reviewed AppFUMO edge binds them to this flow.

The negative inventory is deliberately narrow. It checks exact basenames only
for `fw_setenv`, `abctl`, `grub`, `systemd-bless-boot`, `mark-good`, and
`bootcount`. It is not a substring, semantic-equivalence, or behavior-absence
claim.

## Exact identities and authority

- embedded ELF size: `5,066,264` bytes;
- ELF SHA-256:
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
- GNU Build ID: `863a8730e66a1c5245a1bf458fe2554adee0351a`;
- canonical rootfs size: `879,109,759` bytes;
- rootfs SHA-256:
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
- instruction authority: exact Homebrew LLVM 23.1.3 `llvm-objdump`, with raw
  bytes suppressed;
- complete decoded instructions: `470,739`, canonical SHA-256
  `693dce0d89faabeea30512fe0a696a733e9bdd64fd7be7379dba98a44d2dc0c8`;
- unwind authority: exact Homebrew LLVM 23.1.3 `llvm-readelf --unwind`;
- complete FDE ranges: `3,789`, canonical SHA-256
  `2c71813a3f098f8f949c6acee1080c0147df182e589f8b8b576798ce4807eb07`.

The strict manifest also binds the exact executable-file hashes, sizes, and
version line of both LLVM tools; all selected FDEs, complete direct transfers,
machine-instruction hashes, literal role hashes, resource hashes, canonical
rootfs members, and full rootfs inventory.

## Selected FDEs

| Normalized role | Exact FDE |
|---|---|
| update-view constructor | `[0xdea90,0xdf6ac)` |
| update-view metadata dispatch | `[0x16d430,0x16daad)` |
| controller constructor | `[0x135a80,0x135fa6)` |
| controller metadata dispatch | `[0x16f520,0x16fab3)` |
| controller reboot | `[0x134ce0,0x134d79)` |
| reset wrapper | `[0x146680,0x146711)` |
| reset core | `[0x145ca0,0x14667e)` |
| recovery notification setup | `[0xe2790,0xe2c2b)` |
| reboot-system wrapper | `[0xe8c20,0xe8d06)` |
| reboot-system core | `[0xe7810,0xe7fe1)` |
| recovery mode slot | `[0x11f060,0x11f1a9)` |
| recovery request | `[0xe8d10,0xe907c)` |
| boot-information request | `[0xeeb00,0xeef10)` |
| booting-type reader | `[0x1122d0,0x112a58)` |

## Boundary conclusion

The reviewed evidence establishes local Qt delivery, request construction,
argument shape, call mode, and immediate status handling. It does not establish
execution of the requests or effects beyond the local process. In particular:

- no reviewed asynchronous reset or recovery request carries a slot identifier;
- no visible inactive-slot activation is established;
- no mark-good operation is established;
- no boot-counter update is established;
- no rollback programming is established;
- no persistent slot-choice mechanism is established;
- request creation or local dispatch status does not prove hardware action;
- MICOM behavior remains outside the ELF boundary; and
- ABL/bootloader selection, acceptance, and rollback remain outside the ELF and
  rootfs evidence boundary.

Installed runtime identity and reachability, boot-slot change, successful boot
acceptance, and rollback behavior therefore remain unknown.

## Deterministic package

- analyzer: `tools/uk_fw/appfumo_boot_activation_boundary.py`;
- selected byte-free evidence SHA-256:
  `216d5d271b1d6aa4a83916eecbbeddc04f65a12504cbdb421529739c6aa4e7e6`;
- strict manifest SHA-256:
  `ffb452bc2f0a012935b0b0e7b44a808dca1a76e6ae8a169af30fbed08cd8d4c5`;
- normalized report SHA-256:
  `0f1100d80b7197ed0c1fdcee48ef25f171423b4b00253b11ecdd6f1424e04196`.

The analyzer rejects unknown/missing keys, wrong types, Booleans used as
integers, nonregular/oversized/changing inputs, malformed or ambiguous ELF
mapping, ELF/Build-ID/rootfs/LLVM drift, malformed or incomplete instruction or
FDE output, whole-inventory drift, selected-range/transfer/anchor/literal/blob
drift, and rootfs member aliases, links, special types, duplicates, or metadata
changes. Output is fixed UTF-8 with LF line endings and omits supplied operator
paths, target instructions and bytes, callable endpoint coordinates, serial
bytes, operational fallback text, and vulnerability identifiers.
