# Exact ABL boot selection checkpoint

## Completed

- Bound ABL configuration at flash `0x102e6a`, type `0x60000`, total size
  `0xa88`, SHA-256
  `c9a592afcecb6adefc678d5503f98e946370948264690ef46c2bf39a7c718a9a`.
- Verified header CRC-32C `a242938d` and payload CRC-32C `dd7740d8`.
- Bound boot index `2` to device instance `1`/`iasImage` and index `3` to device
  instance `2`/`iasImage`, both under predicate `pcbver=10 lge.sign=1`.
- Bound exact stage callback selection to `byte[0xc0214] & 0x1f`; the exact
  iterator advances to the next record when the callback returns zero after a
  returned load failure.
- Bound distinct `ABL.boot` selected-index and `ABL.bdev` actual-device fields.
- Bound exact config tag `0x04e`, mask `0x0003`, and two GPIO inputs; the exact
  stage names this tag `BOOT_MODE_GPIO`. Hash-bound historical Apollo Lake
  GPIO-decoding semantics remain comparative because exact commitment to
  runtime `0xc0214` is not recovered.
- Bound canonical `esinit` secondary-fallback detection and p2-to-p1 repair
  attempt.
- Bound canonical engineering promotion of `p2/iasImage_sub` by copying it over
  `p1/iasImage`; exact ABL configuration does not directly name `_sub`.
- Added deterministic analyzer, frozen JSON, byte-free excerpt, assessment, and
  focused tests.

## Validation

- Focused: `11 passed, 7 subtests passed`.
- Related ABL/update integration: `52 passed, 19 subtests passed`.
- Canonical suite: `998 passed, 352206 subtests passed in 193.73s`.
- Canonical log SHA-256:
  `4d278bda042649233f564090b344e4b206c7f58af038ff4ac5c785c26dc6b099`.
- Frozen report SHA-256:
  `204adff4a69478db3ca113985585ceff30f7e31b8101068b223b9630c497136e`.
- Frozen excerpt SHA-256:
  `efd46f8f7604daa73a9e51707efa7a1c44fb19aa6868208b2221720dd661899e`.

## Still unresolved

- Exact runtime path from configured GPIO inputs to `0xc0214`, plus its
  persistence semantics.
- Attempt counters, health, mark-good, rollback thresholds, and MICOM policy.
- Successful/durable userspace repair.
- Any dynamically constructed `_sub` route outside the exact literals and
  records bound here.
- Custom-image acceptance, root, and persistence.
