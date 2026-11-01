# AppFUMO post-write finalization boundary

Status: exact-static, execution-free analysis of the recovered embedded AppFUMO
ELF. No recovered updater, helper, target executable, mount operation, update,
partition write, reset, slot change, or persistence mechanism was executed.

## Result

The AppFUMO partition updater has a virtual `finish` implementation at raw VA
`0xd1e70`, bound by one `R_X86_64_RELATIVE` relocation at vtable slot
`0x6ce350`. Its exact FDE is `[0xd1e70,0xd327f)`. The separate fstab-maintenance
helper is `[0xd0c80,0xd1e6c)`.

The reviewed path establishes post-write maintenance of the already-selected
inactive root. It does **not** establish a persistent root-slot selection
operation. A mode-byte/object-state guard can return before the main maintenance
body; on the body that continues:

1. `finish` synchronizes, waits one second, derives the inactive `root`
   partition pathname, and compares that pathname with the device currently
   mounted at `/mnt/root`.
2. When the comparison does not match, it constructs the bounded `mount -t
   ext4` operation needed to expose the selected inactive root for maintenance.
3. It calls the fstab helper at `0xd2400`.
4. It then enters progress reporting and bounded filesystem maintenance for the
   root, app, and selected VR mountpoints.
5. On the normal tail it removes two resume-marker paths, reports progress
   value 100 with `System Update Complete!!`, and returns a stored result byte.

The fstab helper is not a root-slot selector. The presence of `root` is an
admission condition. If `root` and either `foldervr` or `vr` are selected, the
helper derives the active and inactive partition pathnames for the selected VR
variant (`foldervr` takes priority), then replaces the active VR pathname with
the inactive VR pathname inside the mounted inactive root.

The candidate files are:

- `/mnt/root/etc/fstab_emmc`;
- `/mnt/root/etc/fstab_emmc_fde`; and
- fallback `/mnt/root/etc/fstab`.

Each decoded update sequence reaches `QString::replace`, `QIODevice::write`,
`QFileDevice::flush`, `fsync(handle)`, and `QFileDevice::close`. This is
configuration consistency for the next root, not evidence that MICOM or ABL has
selected that root for boot.

## Completion is not the same as successful finalization

A material control-flow distinction is now closed.

At `0xd2405`, `finish` tests the fstab helper result. A false result branches to
`0xd2c08`, records a false result byte at `0xd2c28`, and jumps back to
`0xd242e`, immediately before progress value 99. It does not terminate at the
fstab failure.

If subsequent processing reaches the normal tail, the function reports
progress value 100 at `0xd2aeb`, then loads and returns the previously stored
result byte. Therefore progress 100 can coexist with a false `finish` return.
This does not prove that a runtime caller ignores the return value, but it does
prove that completion progress alone is insufficient evidence of successful
post-write finalization.

The local write, flush, and `fsync` return values in the three reviewed fstab
sequences are not used by a conditional branch before close. Likewise, the
reviewed trim, unmount, and resume-marker helper returns are not promoted here
to successful effects. Their call sites establish attempts, not completion or
final-byte integrity.

## Relationship to inactive-partition continuity

The prior selector-continuity package established that the selected runtime
record maps to writer index 1 for `root`, and that the same slot predicate
selects the static record populated with the opposite root target:

- active `/dev/mmcblk0p3` maps to inactive root `/dev/mmcblk0p5`; and
- active `/dev/mmcblk0p5` maps to inactive root `/dev/mmcblk0p3`.

This package begins after that selection and writing path. It shows how the
inactive root is exposed and adjusted during `finish`. It does not close
verifier-to-writer byte continuity or prove that the partition writer completed
successfully.

## Relationship to reset and boot activation

The existing boot-activation package closes the local Qt chain from completion
UI to a one-byte reset request. That request carries no slot identifier, and
local request acceptance does not prove remote action.

The post-write finalizer adds no demonstrated persistent root-slot selector. Its
reviewed effects are mount-state checking, VR fstab-path replacement, trim,
unmount, resume-marker cleanup, and progress reporting. In particular, this
package establishes none of the following:

- a persistent boot selector or attempt counter;
- MICOM acceptance of a reset or recovery request;
- ABL selection or authentication of the newly written boot/root pair;
- health checking or mark-good;
- rollback programming or rollback suppression;
- a successful next boot; or
- root access or persistence.

The most defensible current architecture is therefore:

`selected inactive target → attempted partition write → inactive-root
maintenance → completion progress → local reset request`

with final partition integrity, persistent activation, remote reset effects,
boot acceptance, health, mark-good, and rollback still open.

## Exact authority

- embedded ELF size: `5,066,264` bytes;
- SHA-256:
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
- GNU Build ID: `863a8730e66a1c5245a1bf458fe2554adee0351a`;
- fstab-helper FDE: `[0xd0c80,0xd1e6c)`;
- finish FDE: `[0xd1e70,0xd327f)`;
- instruction authority: exact Homebrew LLVM disassembly, with retained raw-VAs
  and bytes suppressed;
- Ghidra was advisory only, and its project addresses are raw VA plus
  `0x100000`.

The deterministic analyzer binds the exact ELF identity and Build ID, parses
PT_NOTE and `.rela.dyn` from stabilized bytes, verifies the finish vtable
relocation, checks six frozen machine-code range hashes, resolves 39 direct-call
targets, checks fixed instruction anchors for the false/true result and
99/100-progress split, and validates all reported strings through unique
file-backed ELF mappings.

## Deterministic package

- analyzer: `tools/uk_fw/appfumo_postwrite_finalization.py`;
- tests: `tests/test_appfumo_postwrite_finalization.py`;
- report:
  `evidence/artifacts/update-candidates/appfumo-postwrite-finalization.json`;
- report SHA-256:
  `ac968b4cb39813c69948d22f4b8cd8282ec1ad0ae60d9b295cf4498342c0781f`;
- selected decoded evidence:
  `evidence/artifacts/update-candidates/appfumo-postwrite-finalization-exact-static.asm`;
- selected decoded evidence SHA-256:
  `0eabf7189a9fcc5eceb36f0e05dfd723d0cef9f6ea3b296b94fc935d78300f74`.

The analyzer fails closed on nonregular, symlinked, oversized, short, or
changing input; ELF identity, size, SHA-256, Build-ID, geometry, mapping,
section, relocation, code-range, literal, call-target, branch-target, or fixed
instruction drift; duplicate Build IDs; and output-file replacement. JSON is
emitted as explicit UTF-8 bytes with fixed LF endings and rejects non-finite
values.

## Boundary conclusion

This package closes the exact-static writer-adjacent finalization path. It
establishes inactive-root maintenance and shows that completion progress is not
an integrity or success verdict. It does not establish runtime execution,
successful writes, final partition bytes, activation, boot acceptance,
mark-good, rollback, root, or persistence.
