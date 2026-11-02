# TXE first-fixed signed-module inventory checkpoint

## Status

Accepted locally. The deterministic inventory covers every paired NFTP module in exact affected TXE `3.1.50.2222` and official first-fixed TXE `3.1.55.2269`.

## Findings

- Both exact firmware identities and embedded NFTP signatures are verified.
- All 34 paired `module/module.met` members are represented.
- 33 modules are strictly decoded; `pavp` remains explicit and opaque because module-extension byte `+9` is nonzero in both builds. No transform is guessed.
- `ish_bup` is byte-identical.
- Nine complete modules are syslib-relocation-only after fail-closed target validation: `adspa`, `busdrv`, `evtdisp`, `hci`, `heci`, `pmdrv`, `tcb`, `tls_iso`, and `vdm`.
- 23 modules retain bytes beyond that address normalization and remain review priorities, not vulnerability claims.
- The eleven smallest residual bytes across `ish_srv`, `loadmgr`, `gpio`, and `pm` are exact one-byte increases in serialized message-length fields whose message dword zero is `0x02000200`.
- Exact syslib constructor `0x8e8a..0x8ed3` / `0x8e8f..0x8ed8`, SHA-256 `1a9f71789daff697fe6ac80b110101ecc63d84bbc3759c6a869bfc648a6d8c28`, stores the supplied length byte at message offset `+4`; submit wrappers store first-argument dword `0x02000200` at offset zero.
- The submit wrapper calls syslib selector wrapper `0x16f8f` / `0x16fb1` with selector `0x10` and argument size `0x40`, producing syscall value `0x10010040`.
- The complete hash-bound selector-`0x10` kernel handlers are each `0x28e` bytes. Seven raw bytes differ: three call-relocation bytes plus two uses of immediate `0xff → 0x102` (`mov` and `cmp`). No other handler bytes remain after reviewed normalization.
- The shared return epilogue uses the same changed comparison. A complete-kernel census finds two `mov` and twelve `cmp` sites using `0xff` in the affected build and `0x102` in the first-fixed build.
- This is a kernel-wide status/sentinel-renumbering candidate on the exact message-submit path, not isolated message-validation proof. It does not name the immediate, explain the plus-three change, identify the recipient or appended byte, establish HECI reachability, or attribute the change to CVE-2018-12147.

## Artifacts

- `tools/uk_fw/txe_first_fixed_module_inventory.py`
- `tests/test_txe_first_fixed_module_inventory.py`
- `evidence/intel-txe-first-fixed-module-inventory.md`
- `evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json`
  - schema `ioniq-txe-first-fixed-module-inventory/v1`
  - size `111,564`
  - SHA-256 `3a5df368a7d319101cfd710960a8cfe38e61215e898958442ce382657b4eae1e`

## Validation

- focused tests: `3 passed in 0.21s`;
- canonical suite: `1025 passed, 352351 subtests passed in 181.04s`;
- canonical log SHA-256: `93192080a304cbc7f70eefb91452b370af5d10b1760d1ad40b8f4d7ccf71fd31`;
- normal versus UTF-16 environment output: byte-identical;
- `py_compile` and `git diff --check`: passed.

## Next work

1. Map all fourteen kernel-wide `0xff → 0x102` MOV/CMP sites to callers and return paths, then determine the status/sentinel semantics and why the value increases by three.
2. Identify the semantics and recipient associated with message dword-zero value `0x02000200`, then determine the meaning of the appended byte without sending a request.
3. Compare `ipc_drv` changed entry bodies and dispatch tables; retain CVE attribution boundaries.
4. Extend the same exact inventory to the remaining FTPR `kernel`, `bup`, and `syslib` service-handler mappings.
5. Continue first-fixed NDL transaction/counter analysis for CVE-2018-3655.

## Safety boundary

No firmware module, updater, target executable, or MEI/HECI endpoint was executed or opened. No malformed message, exploit, boot image, flash instruction, signature bypass, or persistence payload was created.
