# AppFUMO inactive-partition selector continuity

## Result

The exact embedded EU `260128` AppFUMO ELF contains a closed static chain from
the selected update record's partition selector to the inactive root target
used by the root writer branch:

1. the current record is selected from the list at object `+0x28` with the
   current index at object `+0x98`;
2. its selector at record `+0x20` is copied and passed to the ten-name lookup
   at raw VA `0xbfb20`;
3. the returned index controls the writer jump table at `0xc60ae`;
4. the root branch is index `1` and passes literal index `1` to the record-copy
   helper at raw VA `0xa0d50`;
5. that helper applies the same runtime predicate used when the two static
   record tables are populated, then copies record `index * 0xf8`;
6. the populated root target at copied-record `+0x28` is used while building
   the root target/mount string.

The exact inactive mapping table contains:

- active root `/dev/mmcblk0p3` → inactive root `/dev/mmcblk0p5`, inactive boot
  `/dev/mmcblk0p2`, and inactive VR `/dev/mmcblk0p7`;
- active root `/dev/mmcblk0p5` → inactive root `/dev/mmcblk0p3`, inactive boot
  `/dev/mmcblk0p1`, and inactive VR `/dev/mmcblk0p6`.

This closes **selector/index/inactive-target continuity for the root branch**.
It does not close source-file byte continuity, final partition integrity,
activation, boot acceptance, health, mark-good, rollback, root, or persistence.

## Exact identity

- ELF:
  `work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf`
- size: `5,066,264`
- SHA-256:
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`
- GNU Build ID: `863a8730e66a1c5245a1bf458fe2554adee0351a`
- embedded outer offset: `0x5721c8`
- address convention: this note uses raw embedded-ELF VAs; the existing
  Ghidra project represents each as raw VA plus `0x100000`.

## Exact chain

### Inactive-name derivation and table population

`FUN_0xa14c0` carries the diagnostic name `getInActivePartitionName` and a
`m_rootfs`/`inName` log format. It copies a 20-pointer table, matches the
current root device, and selects the requested root, boot, VR, or related
entry. The caller at `0xa1b70`:

- calls one runtime predicate at `0x8e840`;
- on one branch writes the derived root target to `0x6d30a0`, which is root
  record `1` at table `0x6d2f80` plus `0x28`;
- on the other branch writes it to `0x6d3a60`, which is root record `1` at
  table `0x6d3940` plus `0x28`;
- derives and writes the corresponding VR and folder-VR targets in the same
  selected table.

The copy helper at `0xa0d50` calls that same predicate at `0x8e840`. It selects
`0x6d3940` when the predicate is false and `0x6d2f80` when true, bounds indices
above `9` to zero, and copies exactly `0xf8` bytes from `base + index * 0xf8`.
Thus population and later retrieval agree on which table is selected.

### Selected record to root branch

At `0xc541a`, the updater reads object `+0x98`, indexes object `+0x28`, takes
the selected record, and copies its `+0x20` selector. At `0xc54ca`, it calls
the ten-name lookup and retains the returned index. A negative result exits the
normal dispatch path.

At `0xc608d`, indices above `9` go to the default path. Otherwise the index
selects a relative jump-table entry. The frozen jump table maps index `1` to
raw VA `0xc7638`, the root-specific branch.

The root branch repeatedly calls `0xa0d50` with literal index `1`. At
`0xc7861` it addresses copied-record `+0x28`; the subsequent string operations
combine that target with literal `mount -t ext4 ` and the root staging path
`/rw_data/mnt/root`. This establishes that the writer-side root processing
uses the inactive root target derived for index `1`, rather than an unrelated
record index.

## Deterministic verifier

`tools/uk_fw/appfumo_inactive_partition_continuity.py`:

- reads one regular no-follow file descriptor and revalidates its identity;
- requires the exact size, SHA-256, and Build ID;
- validates ELF table geometry, bounds, unique section names, non-overlapping
  file-backed `PT_LOAD` ranges, and a unique Build ID;
- parses `.rela.dyn` itself and reconstructs the 20-pointer inactive-partition
  table from `R_X86_64_RELATIVE` addends;
- validates seven frozen instruction-range hashes covering derivation,
  population, selected-table copy, selector lookup, writer selection, jump
  dispatch, and root-target construction;
- emits deterministic UTF-8 with LF endings and uses exclusive output-file
  creation.

Report:
`evidence/artifacts/update-candidates/appfumo-inactive-partition-continuity.json`

- schema: `appfumo-inactive-partition-continuity/v1`
- report SHA-256:
  `bb464780848a635202b8f9d35b40f89caa923fccab2e9aad1cf172e9886d9328`

Exact Homebrew LLVM excerpts:
`evidence/artifacts/update-candidates/appfumo-inactive-partition-continuity-exact-static.asm`

- artifact SHA-256:
  `0093a189b584aaf07abd8197241517273f02633b5be762f9d9933938cf1bcce3`

## Boundary

This package establishes exact-static continuity only between a selected
record's partition selector, the writer's partition index, and the root
branch's selected inactive target. It does **not** establish:

- that the selected source pathname remains the same object or bytes across
  verification, transformation, and writer reopen;
- that authenticated bytes equal final partition bytes;
- that any write succeeds on an owner unit;
- that the inactive root becomes the persistent boot selection;
- MICOM/ABL acceptance, health checks, attempt counters, mark-good, rollback,
  or recovery behavior;
- root access or persistent custom firmware.

No updater, recovered target executable, partition writer, mount operation,
reset, flash action, slot change, exploit, or persistence mechanism was run.
