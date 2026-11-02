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
- The eleven smallest residual bytes across `ish_srv`, `loadmgr`, `gpio`, and `pm` are exact one-byte increases in serialized message-length fields for destination dword `0x02000200`.
- Exact syslib constructor `0x8e8a..0x8ed3` / `0x8e8f..0x8ed8`, SHA-256 `1a9f71789daff697fe6ac80b110101ecc63d84bbc3759c6a869bfc648a6d8c28`, stores the supplied length byte at message offset `+4`; submit wrappers store the destination dword at offset zero.
- The coordinated length change is not attributed to CVE-2018-12147. Recipient identity, added-byte meaning, attacker control, and HECI reachability remain open.

## Artifacts

- `tools/uk_fw/txe_first_fixed_module_inventory.py`
- `tests/test_txe_first_fixed_module_inventory.py`
- `evidence/intel-txe-first-fixed-module-inventory.md`
- `evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json`
  - schema `ioniq-txe-first-fixed-module-inventory/v1`
  - size `107,304`
  - SHA-256 `5ced3ef503b104bf2e6afe331c8c30329b4dfb36c0e2803acaf78df32e8d06a3`

## Validation

- focused tests: `3 passed in 0.21s`;
- canonical suite: `1025 passed, 352351 subtests passed in 181.50s`;
- canonical log SHA-256: `a8ce29b802bb8173b7d8cb915a5f5629c34065fbcf304b9ce36ff0c7d36d4928`;
- normal versus UTF-16 environment output: byte-identical;
- `py_compile` and `git diff --check`: passed.

## Next work

1. Identify the recipient and grammar for destination dword `0x02000200`, then determine the semantic meaning of the appended byte without sending a request.
2. Compare `ipc_drv` changed entry bodies and dispatch tables; retain CVE attribution boundaries.
3. Extend the same exact inventory to FTPR `kernel`, `bup`, and `syslib` service-handler mappings.
4. Continue first-fixed NDL transaction/counter analysis for CVE-2018-3655.

## Safety boundary

No firmware module, updater, target executable, or MEI/HECI endpoint was executed or opened. No malformed message, exploit, boot image, flash instruction, signature bypass, or persistence payload was created.
