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
- A complete `ipc_drv` operation callback comparison binds a new first-fixed `0x88`-byte local-buffer clear through gate `0x103d`. Both versions then store a four-byte header, copy at most `0x80` payload bytes, and pass the buffer with fixed `0x88` size arguments to syslib wrapper `0x61d6`.
- The `ipc_drv` delta is an exact stale-stack/partial-initialization information-disclosure hardening candidate, not proof of HECI reachability, boundary crossing, practical disclosure, or CVE-2018-12147 attribution.
- The analysis does not establish the vendor status names or full semantics, identify the message recipient or appended byte, establish HECI reachability, or attribute the change to CVE-2018-12147.

## Artifacts

- `tools/uk_fw/txe_first_fixed_module_inventory.py`
- `tests/test_txe_first_fixed_module_inventory.py`
- `evidence/intel-txe-first-fixed-module-inventory.md`
- `evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json`
  - schema `ioniq-txe-first-fixed-module-inventory/v1`
  - size `127,346`
  - SHA-256 `2507d868f76eb9fe098b9044095f1b75f93cbc0b0692472b11cc3d97645b6750`

## Validation

- focused tests: `3 passed in 0.19s`;
- canonical suite: `1025 passed, 352351 subtests passed in 176.65s`;
- canonical log SHA-256: `62474cde9e7b17fbdb32f09cc0ed66d21a367106cf9339e1934cd8ac0530b7cf`;
- normal versus UTF-16 environment output: byte-identical;
- `py_compile` and `git diff --check`: passed.

## Next work

1. Recover the vendor names and full semantics of the queue/deferred sentinel and inserted ordinals `0xc4`, `0xc5`, and `0xc9`.
2. Identify the semantics and recipient associated with message dword-zero value `0x02000200`, then determine the meaning of the appended byte without sending a request.
3. Identify the named major-39 `ipc_drv` operation bound to callback `0x274bd` / `0x274e5`, and determine whether the fixed-size buffer crosses an internal privilege or HECI boundary.
4. Extend the same exact inventory to the remaining FTPR `kernel`, `bup`, and `syslib` service-handler mappings.
5. Continue first-fixed NDL transaction/counter analysis for CVE-2018-3655.

## Safety boundary

No firmware module, updater, target executable, or MEI/HECI endpoint was executed or opened. No malformed message, exploit, boot image, flash instruction, signature bypass, or persistence payload was created.
