# AppFUMO PartitionUpdater source-integrity and target-selection boundary

Status: exact-static, execution-free analysis of the recovered embedded FUMO
ELF. No updater, helper, or recovered target code was run. No update input,
package, image, mount, write, slot change, boot action, or persistence action was
created or attempted.

## Result

The reviewed `PartitionUpdater` route has two materially different modes.
When global mode byte `0x6d20b4` is nonzero, the orchestrator emits its
integrity-check signal; the constructor's hash-bound signal/slot identities and
generated metadata tail jump `0x16ba9c -> 0xcd640` bind that route to
`slotHashCheck`. When the byte is zero, the same orchestrator tail-jumps directly
to `startPartitionUpdate` at `0xce110 -> 0xc53d0` after its ordinary setup
checks.

In the hash-gated route, `slotHashCheck` verifies the selected primary source
when that candidate is present and verifies each non-excluded entry source
pathname. The complete direct-call inventory for source gate `0xc1ff0` is only
`0xcd6fa` and `0xcdbae`, both inside `slotHashCheck`. Each nonzero result takes a
failure path; only loop completion reaches post-hash starter `0xcd560`, whose
sole direct caller is `0xcdea7` and which tail-jumps to the writer at `0xcd5db`.
A mismatch therefore does not reach the write starter through this reviewed
route.

This is **pre-write source authentication**, not final-partition integrity.
Verifier and writer receive the same stored `QString` pathname value from record
field `+0x10`, but independently reopen it. No retained descriptor or open
object binds the verifier's bytes to the writer's bytes. Exact same-object,
same-byte, transformed-output, and final-partition identity remain unknown.

The static map and active/inactive helper functions are present and hash-bound.
The writer finds a selected runtime record by field `+0x20`; image-backed and
clone branches are distinct. A later exact-static pass corrects and closes the
previously unknown target sublink: the selected runtime record's `+0x20`
selector is mapped to an index, and the root branch uses that index to copy a
separate static partition record whose `+0x28` field contains the populated
inactive target. Active root `/dev/mmcblk0p3` maps to inactive root
`/dev/mmcblk0p5`, and vice versa. See
[`appfumo-inactive-partition-continuity.md`](appfumo-inactive-partition-continuity.md).
This does not close source-byte continuity, write success, final-partition
integrity, bootloader activation, or mark-good.

The process-completion handler, fstab-state updater, and finalization FDEs have
no direct call or jump to any inventoried file-signature/source-hash target
`0x45820`, `0x45d80`, `0x18f700`, `0x140f50`, or `0xc1ff0`. This proves only a
bounded direct-edge negative for those exact FDEs and targets. It does not
exclude indirect, virtual, external, inlined, loader, boot-stage, or dynamically
invoked verification. Process completion is not cryptographic readback, and
final partition byte identity remains unknown.

## Exact identities and authority

- exact embedded ELF size: `5,066,264` bytes;
- SHA-256:
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
- GNU Build ID: `863a8730e66a1c5245a1bf458fe2554adee0351a`;
- instruction authority: Homebrew LLVM 23.1.3 `llvm-objdump` with raw bytes
  suppressed;
- unwind authority: Homebrew LLVM 23.1.3 `llvm-readelf --unwind`;
- complete decoded instructions: `470,739`, canonical SHA-256
  `693dce0d89faabeea30512fe0a696a733e9bdd64fd7be7379dba98a44d2dc0c8`;
- complete FDE ranges: `3,789`, canonical SHA-256
  `2c71813a3f098f8f949c6acee1080c0147df182e589f8b8b576798ce4807eb07`.

The analyzer also binds the exact executable-file identities and version line of
both LLVM tools. Addresses below are link-time virtual addresses in the
image-base-zero embedded ELF namespace.

## Independently recovered FDEs

| Role | Exact FDE |
|---|---|
| active partition helper | `[0xa0e10,0xa14b2)` |
| inactive partition helper | `[0xa14c0,0xa1b64)` |
| partition-map population | `[0xa1b70,0xa247e)` |
| primary-image selector | `[0xa2480,0xa2c17)` |
| record lookup | `[0xbfb20,0xbfe67)` |
| constructor | `[0xc0130,0xc0518)` |
| source-integrity gate | `[0xc1ff0,0xc255d)` |
| write starter | `[0xc53d0,0xcc479)` |
| process counter | `[0xcc480,0xcc6b4)` |
| post-hash starter | `[0xcd560,0xcd637)` |
| slot hash check | `[0xcd640,0xce067)` |
| mode orchestrator | `[0xce070,0xce217)` |
| completion handler | `[0xcf9b0,0xd0c79)` |
| fstab-state update | `[0xd0c80,0xd1e6c)` |
| finalization | `[0xd1e70,0xd327f)` |

Support FDEs for the fixed-key verifier, signed-trailer parser, record/key
verification, process-thread starter, and generated metadata dispatcher are
also bound in the strict report.

## Verifier format: bounded claims only

The source gate checks source-file existence, runs its first hash/status stage,
and, on zero status, calls the fixed-public-key verifier at `0xc22eb`. That
verifier constructs its key pathname from two hash-bound literals, reads the
key file, and calls record/key verifier `0x18f700` over the supplied source
pathname.

The signed-file parser seeks to `file_size - 0x4024`, allocates and reads exactly
`0x4024` bytes, and recognizes two three-byte header families: `TER` and `TE2`.
It does not test a four-byte `TER2` literal. Internal record verification contains
a 32-byte comparison and linked mbedTLS operations, but this package does not
bind the exact signed byte ranges, the digest algorithm for this route, or RSA
padding/signature encoding. Those fields are `null` rather than inferred.

## Complete selected direct-transfer inventories

The strict manifest records calls and direct/tail jumps separately. Critical
inventories are:

- source-integrity gate `0xc1ff0`: calls `0xcd6fa`, `0xcdbae`; no direct jumps;
- write starter `0xc53d0`: call `0xcc646`; tail jumps `0xcd5db`, `0xce110`;
- post-hash starter `0xcd560`: call `0xcdea7` only;
- slot-hash slot `0xcd640`: generated metadata tail jump `0x16ba9c` only;
- completion handler `0xcf9b0`: generated metadata tail jump `0x16ba28` only;
- fstab updater `0xd0c80`: call `0xd2400` only;
- finalization `0xd1e70`: no direct calls or jumps to its entry.

The last row is important: finalization is a mapped FDE, but this direct
inventory does not prove its dynamic invoker or that every completion path
reaches it.

## Trust-boundary model

| Boundary | Exact-static result |
|---|---|
| pre-write source authentication | present in nonzero/hash-gated mode; zero/non-hash mode reaches writer directly |
| pathname value vs object/bytes | same stored pathname value; object and byte identity unknown because of independent reopen |
| package source vs transformed/final partition | no binding proved |
| image-backed vs clone | distinct writer branches |
| process completion vs cryptographic readback | distinct; completion is not readback authentication |
| inactive target vs bootloader activation | later exact-static pass closes selector/index/static inactive-target continuity; activation/mark-good remain unknown |
| destination re-verification | no direct edge to the five inventoried helpers in the three reviewed post-write FDEs; broader absence unknown |
| write/update success | unknown |
| boot acceptance, root, persistence | all unknown |

## Deterministic package

- analyzer:
  `tools/uk_fw/appfumo_partition_write_integrity.py`;
- strict manifest SHA-256:
  `5d3ca7bf8261805ca10d02d61d75ec1ee54c1205c66cb15be03a3e009dd0c5c5`;
- selected exact-static text SHA-256:
  `e3acf80fdc76df6f1defd29d74fedcd1a62a90ef74ebe170f4a48591b20ec61c`;
- normalized report SHA-256:
  `e84e0771dea6aabe8f76fbe5a495084d0d6ef42650d7c39bec54fe68ab55c612`.

The analyzer rejects unknown or missing keys, wrong types, Boolean-as-integer,
nonregular/oversized/changing inputs, malformed or ambiguous ELF mappings,
exact ELF/Build-ID/tool drift, malformed/duplicate/unordered/truncated
instructions, complete instruction/FDE count or hash drift, selected-FDE drift,
direct-transfer drift, machine-anchor drift, literal/blob drift, mismatch-gate
drift, and mode-flow drift. Output is fixed UTF-8/LF through
`sys.stdout.buffer`, independent of `PYTHONIOENCODING`, and contains no supplied
paths, target pathnames, commands, proprietary bytes, or exploit material.
