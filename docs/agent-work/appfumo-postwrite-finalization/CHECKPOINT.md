# AppFUMO post-write finalization checkpoint

Status: implementation and canonical validation complete.

## Exact result

- The finish implementation is bound by a relative relocation at vtable slot
  `0x6ce350` to raw VA `0xd1e70`.
- `finish` resolves and maintains the inactive root, then calls the separate
  fstab helper at `0xd2400`.
- The helper admits only selected `root` updates that also include `foldervr` or
  `vr`, chooses `foldervr` when present, and rewrites the selected VR variant's
  active pathname to its inactive pathname inside the mounted inactive root.
- Supported paths are `fstab_emmc`, `fstab_emmc_fde`, and fallback `fstab`.
- Each reviewed file path reaches replace, write, flush, `fsync`, and close.
- A false helper result records a false finish result and rejoins immediately
  before progress 99. If later processing reaches the normal tail, progress 100
  can be reported while `finish` still returns false.
- The reviewed finalizer does not expose a persistent root-slot selector.

## Package

- `tools/uk_fw/appfumo_postwrite_finalization.py`
- `tests/test_appfumo_postwrite_finalization.py`
- `evidence/appfumo-postwrite-finalization.md`
- `evidence/artifacts/update-candidates/appfumo-postwrite-finalization.json`
- `evidence/artifacts/update-candidates/appfumo-postwrite-finalization-exact-static.asm`

## Validation

- final focused suite: `10 passed in 0.16s`;
- final canonical full suite:
  `932 passed, 352185 subtests passed in 129.32s`;
- final full log:
  `work/local-validation/pytest-full-appfumo-postwrite-finalization-final.log`;
- final full-log SHA-256:
  `8983660163d70785aad2a4e831a73341f20a20fc11f75d374f2c046cca3afee0`;
- normalized report size: `10,472` bytes;
- normalized report SHA-256:
  `ac968b4cb39813c69948d22f4b8cd8282ec1ad0ae60d9b295cf4498342c0781f`;
- selected evidence size: `3,968` bytes;
- selected evidence SHA-256:
  `0eabf7189a9fcc5eceb36f0e05dfd723d0cef9f6ea3b296b94fc935d78300f74`;
- Python compilation passed;
- normal and `PYTHONIOENCODING=utf-16` output were byte-identical and matched
  the retained report;
- strict UTF-8, LF-only, final-newline, NUL, trailing-whitespace, and
  path-limited diff checks passed.

## Boundary

No recovered target code or updater was run. No update, mount, trim, write,
unmount, reset, flash, slot, boot, root, or persistence operation was attempted.
Runtime invocation, successful maintenance, final partition integrity,
persistent activation, MICOM/ABL action, boot acceptance, health, mark-good,
rollback, root, and persistence remain unknown.
