# Intel MEI historical backport audit checkpoint

Status: exact-static comparison implemented; four public historical premises
rejected for the recovered module; runtime interface identity remains open.

## Completed

- Identified exact `mei.ko`:
  - size `125000`;
  - SHA-256 `8518715e6e1910aacddf9da116aa97b98e7fca8f14c64da83959c60204d83609`;
  - Build ID `ca127bac6266f1afd1ff48cdd0c0bdcb4a67d643`;
  - vermagic `4.1.27-abl SMP mod_unload`.
- Reviewed and hash-bound public patches:
  - `23253c31c6a7a3c5a437ec31830e2100484c0748`;
  - `f862b6b24f0ffd954633a55f39251a6873b664ca`;
  - `6cbb097fd3903fd6b419303ee8dc7f72b47d06f0`;
  - `6a8d648c8d1824117a9e9edb948ed1611fb013c0`.
- Exact module has:
  - callback size cached before queue transfer and callback pointer cleared
    after transfer;
  - caller/callee error ownership that avoids the reviewed reset double-free;
  - unsigned carry rejection plus pre-copy fragment bounds comparison;
  - disconnect state transition deferred to callback completion.
- Added:
  - `evidence/vendor-kernel-intel-mei-backports.md`;
  - `evidence/artifacts/kernel-candidates/intel-mei-backport-exact-static.asm`;
  - `tools/uk_fw/intel_mei_backport_model.py`;
  - `tests/test_intel_mei_backport_model.py`.

## Frozen evidence

Exact-static excerpt:

- size `30430`;
- SHA-256 `f52f4723550174e90eadae6faa87eb8e991c4eda44dbc2c2e460a34753f1f8a8`.

## Claim boundary

This rejects only four exact historical code premises. It does not establish
installed runtime bytes, MEI node presence or permissions, client availability,
host control over firmware responses, a remaining memory-safety flaw, useful
corruption, root, or persistence. No recovered code or MEI endpoint was
executed.

## Validation

- Focused model: `8 passed, 135 subtests passed`.
- Combined MEI/bench scope: `48 passed, 157 subtests passed`.
- Canonical suite: `1019 passed, 352351 subtests passed in 181.98s`.
- Canonical log SHA-256:
  `c7a0ef234d90dd119d7908ad0476460db5cc092cffa4151622cc737e1c22af7e`.
- Default report: `2204` bytes, SHA-256
  `ad7fe8d29735da6e8a800c1ee3d037a33b3f992b45ccb2434fdd04a3f4d295f8`.
- Alternate-output-encoding determinism, `py_compile`, and
  `git diff --check` passed.
