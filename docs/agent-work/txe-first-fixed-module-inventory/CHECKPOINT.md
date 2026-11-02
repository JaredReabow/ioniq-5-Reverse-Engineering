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
- The shared return epilogue uses the same changed comparison. A complete-kernel census finds three `mov` and twelve `cmp` sites using `0xff` in the affected build and `0x102` in the first-fixed build.
- The complete `0xb2`-byte helper directly called by selector `0x10` differs only in its `mov edx, 0xff → 0x102`. Exact instructions first walk `+0x50`/`+0x28` links to a null tail, store the source pointer there, and return the reviewed value through `eax`.
- The shared epilogue treats zero and the reviewed value alike, while other nonzero values call a separate handler. This supports a deferred/nonordinary-completion sentinel interpretation and kernel-wide renumbering candidate, not isolated message-validation proof.
- Sixteen matching instruction contexts locate all three numeric insertions: affected `0xc4..0xc6` shift by two, affected `0xc7` and higher reviewed values shift by three, and exact first-fixed status-return instructions occupy new ordinals `0xc4`, `0xc5`, and `0xc9`.
- The first-fixed page-table producer returning `0x100` is the translated counterpart of an affected producer returning `0xfd`; the first-fixed 128-entry enumeration producer returning `0x101` is the translated counterpart of an affected producer returning `0xfe`. They are not inserted statuses.
- All fifteen kernel sites now have bounded roles: three producers, ten repeated zero-or-sentinel completion filters, one selector-helper acceptance comparison, and one central-dispatcher comparison that continues pending-work dequeue.
- The analysis does not establish the vendor status names or full semantics, identify the message recipient or appended byte, establish HECI reachability, or attribute the change to CVE-2018-12147.

## Artifacts

- `tools/uk_fw/txe_first_fixed_module_inventory.py`
- `tests/test_txe_first_fixed_module_inventory.py`
- `evidence/intel-txe-first-fixed-module-inventory.md`
- `evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json`
  - schema `ioniq-txe-first-fixed-module-inventory/v1`
  - size `124,860`
  - SHA-256 `0de578c50a7126f1941537b5a90ae5add59cf65bd02513e096f140503055bf3d`

## Validation

- focused tests: `3 passed in 0.24s`;
- canonical suite: `1025 passed, 352351 subtests passed in 198.97s`;
- canonical log SHA-256: `a46488667c6d884006c8b985cae5e0f19c4f2c4a0c245fb4ade75f988e1b3e78`;
- normal versus UTF-16 environment output: byte-identical;
- `py_compile` and `git diff --check`: passed.

## Next work

1. Recover the vendor names and full semantics of the queue/deferred sentinel and inserted ordinals `0xc4`, `0xc5`, and `0xc9`.
2. Identify the semantics and recipient associated with message dword-zero value `0x02000200`, then determine the meaning of the appended byte without sending a request.
3. Compare `ipc_drv` changed entry bodies and dispatch tables; retain CVE attribution boundaries.
4. Extend the same exact inventory to the remaining FTPR `kernel`, `bup`, and `syslib` service-handler mappings.
5. Continue first-fixed NDL transaction/counter analysis for CVE-2018-3655.

## Safety boundary

No firmware module, updater, target executable, or MEI/HECI endpoint was executed or opened. No malformed message, exploit, boot image, flash instruction, signature bypass, or persistence payload was created.
