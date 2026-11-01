# AppFUMO boot-partition write and weak-success boundary

## Scope and identity

This execution-free package follows the previously closed staging path into the
exact AppFUMO routine logged as `swapSystem`.

Exact ELF:

- size `5,066,264`;
- SHA-256
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
- Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`.

The `swapSystem` FDE is raw `[0x148e70,0x14bba6)`, size `11,574`, SHA-256
`741fbf2e3fe1321cdc8a2274c4f194ea26c0a90801ca2a6994e4292ef40f8a60`.

## Destination construction

The routine constructs one mountpoint and two mount commands, for boot
partitions p1 and p2. It reuses the exact filename selector at `0xa2480` and
constructs staged normal and `_sub` paths under the previously bound temporary
boot-image directory.

The loop's intended destination matrix is:

| Iteration | Boot partition | Staged source | Destination basename |
|---:|---|---|---|
| 0 | p1 | selected normal image | `iasImage` |
| 1 | p2 | selected normal image | `iasImage` |
| 1 | p2 | selected `_sub` image | `iasImage_sub` |

There is no corresponding p1 `_sub` write in this routine.

Updating files on both boot partitions is not itself persistent boot-target
selection. The routine contains no proved selector/index or mark-good write.

## Mode-byte branches

Mode byte VA `0x6d20b4` selects:

- zero: the already reviewed size-checking direct copy helper at `0x1413f0`;
- nonzero: a command assembled from `DecryptToPIPE`, a staged source, a
  temporary key path, and a `dd` sink targeting the mounted destination.

The pipeline text is a constructed internal implementation detail. It is not a
recommended or executed update procedure.

## Mount completion is not mount success

The mount path is:

`swapSystem 0x149c3c -> 0x13c1a0 -> 0x13bfd0 -> 0x13bba0`.

The final helper calls `QProcess::waitForFinished(-1)`. A false wait result is
logged, but the helper returns void. Its exact FDE contains no call to
`QProcess::exitCode()`, and no child exit status reaches `swapSystem`.

Therefore the code waits for process completion but does not prove or propagate
mount success. Because the mountpoint directory is created before command
dispatch, a failed mount can leave an ordinary directory at the same pathname.
Whether later writes affect that ordinary directory or a mounted partition is a
runtime fact, not established by the true return.

## Pipeline correction and remaining weakness

The initial advisory pass incorrectly stopped after `popen()` and stated that
no `pclose()` existed. Exact FDE review corrects that:

1. raw helper `[0x1397c0,0x1398fb)` appends a stderr-to-stdout redirect;
2. calls `popen(..., "r")` at `0x139867`;
3. drains output through `fgets()` in a loop at `0x1398a3`;
4. calls `pclose()` at `0x1398b0`.

However, the `pclose()` return is immediately discarded and control jumps to
the epilogue. The helper returns void. Thus the pipeline is waited and drained,
but decryption/`dd` exit success is not propagated to `swapSystem`.

## Direct-copy and unmount results

The direct branch calls the copy helper for the normal image at `0x14a1be` and,
on p2, for `_sub` at `0x14a404`. Both Boolean results are tested and failures
are logged. Those failures do not increment the key-failure counter and do not
change the common return formula.

`umount()` is called at `0x14a00f`. Its nonzero result is logged, followed by
continued cleanup. It does not change the common return formula.

These are material result-propagation gaps. They do not prove that failure
occurred on a real unit, only that the reviewed Boolean return is weaker than
successful durable writes.

## Exact common return

A counter initialized to zero is incremented only for a nonzero temporary-key
retrieval result. The loop has two boot-partition iterations. The common tail at
`0x149585` computes:

`1 XOR ((key_failures > 1) AND (mode_byte & 1))`

Consequences for the observed zero/one mode contract:

- mode zero reaches a true common-tail result regardless of direct-copy
  Boolean failures;
- mode one returns false only if both per-partition key retrievals fail;
- one key failure still permits a true result;
- mount exit status, pipeline `pclose()` status, direct-copy results and unmount
  status do not enter this formula.

Early setup failures may take other paths; this conclusion is limited to the
shared continuing tail.

## Caller latch

Two production callers invoke `swapSystem` at raw `0x12003f` and `0x1225c8`.
Each tests the returned byte and stores `1` at caller-object offset `+0x240` only
when it is nonzero.

Because the callee's continuing-tail true result does not prove mount, copy,
pipeline, or unmount success, the `+0x240` latch is a weak-success latch rather
than evidence of durable boot-partition bytes.

A third direct call at `0x14bbfa` belongs to a bounded diagnostic wrapper.

## Result and boundary

The exact-static chain now reaches intended boot-partition file writes:

`staged selected normal/_sub paths`
`-> p1/p2 mount command completion`
`-> direct copy or decrypt-to-pipe/dd`
`-> sync/unmount attempts`
`-> weak Boolean result`
`-> caller +0x240 latch`

It does not establish:

- successful mount or that the pathname referred to a mounted partition;
- successful direct copies;
- successful decryption or `dd` exit status;
- final destination bytes, durability, or authentication after writing;
- a persistent boot selector;
- reset, ABL/MICOM acceptance, boot health, mark-good, attempt counters,
  rollback, root, or persistence.

## Reproduction

```sh
PY="<platformio-env>/bin/python3"
"$PY" tools/uk_fw/appfumo_boot_partition_write.py \
  work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf \
  -o work/appfumo-boot-partition-write.json
"$PY" -m pytest -q tests/test_appfumo_boot_partition_write.py
```

Tracked machine evidence:

- `evidence/artifacts/update-candidates/appfumo-boot-partition-write.json`;
- `evidence/artifacts/update-candidates/appfumo-boot-partition-write-exact-static.asm`.
