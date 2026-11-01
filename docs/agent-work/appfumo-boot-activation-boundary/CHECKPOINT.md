# AppFUMO boot-activation boundary checkpoint

Date: 2026-11-01
Status: implemented, independently reviewed **ACCEPT**, committed as `e759474`, and published in the combined history

## Delivered

- `tools/uk_fw/appfumo_boot_activation_boundary.py`
  - validates the exact ELF, Build ID, canonical rootfs, and exact LLVM tools;
  - binds complete instruction and FDE identities;
  - validates selected FDEs, complete direct-transfer inventories, machine
    anchors, literal/resource role hashes, and Qt connection/dispatch evidence;
  - streams the rootfs archive and binds complete inventory plus selected exact
    regular-member identities;
  - rejects strict-schema/type failures, including Booleans as integers;
  - emits fixed UTF-8/LF normalized JSON with privacy-safe role labels.
- `tests/test_appfumo_boot_activation_boundary.py`
  - parser, ELF, manifest, integer-type, archive canonicalization, alias/link,
    exact-negative, tool identity, exact-chain, boundary, deterministic-output,
    and privacy coverage.
- retained artifacts under `evidence/artifacts/update-candidates/`
  - `appfumo-boot-activation-boundary-exact-static.txt`;
  - `appfumo-boot-activation-boundary-manifest.json`;
  - `appfumo-boot-activation-boundary.json`.
- `evidence/appfumo-boot-activation-boundary.md`.
- plan/checkpoint and narrow updates to the main README, public ledger, and
  update-candidates index.

## Closed exact-static chains

- completion QML timer -> normalized reboot-clicked signal;
- update-view root-signal relay -> local start-reboot signal dispatch;
- start-reboot signal -> controller reboot slot -> generated dispatch;
- controller reboot `[0x134ce0,0x134d79)` -> reset wrapper
  `[0x146680,0x146711)` -> reset core `[0x145ca0,0x14667e)`;
- separate reboot-system `[0xe8c20,0xe8d06)` -> core
  `[0xe7810,0xe7fe1)`;
- recovery setup `[0xe2790,0xe2c2b)`, recovery slot
  `[0x11f060,0x11f1a9)`, and recovery request `[0xe8d10,0xe907c)`;
- boot-information request `[0xeeb00,0xeef10)` and booting-type shared-memory
  reader `[0x1122d0,0x112a58)`.

## Preserved boundary

- Reset and recovery sends are asynchronous, carry no slot identifier, and do
  not prove external action.
- Shared-memory producer and status/booting-type enum meanings remain unknown.
- Selected update scripts perform label management only; fsck observes the
  current root.
- Generic systemd update, boot-control, and flashing components are installed
  but unbound to the reviewed AppFUMO flow.
- Negative inventory is exact-basename-only for the six requested names.
- No inactive-slot activation, mark-good, boot-counter update, rollback
  programming, or persistent slot choice is established.
- MICOM, ABL, and bootloader behavior remains external.

## Validation

- focused tests: **13 passed, 12 subtests passed**;
- latest full tests-scoped suite: **782 passed, 351486 subtests passed**;
- integrated `tests/run_all.py`: **PASS** (`pass=3`, `info=4`, no pending,
  blocked, or failed checks);
- independent exact-binary/package review: **ACCEPT**, with no blocking
  findings; register-level review confirmed wildcard sender service/path and
  fixed interface/member arguments for the recovery-event subscription;
- two exact analyzer generations under different `PYTHONIOENCODING` values were
  byte-identical and matched the retained report;
- Python compilation: passed;
- `git diff --check`: passed;
- retained-file privacy scan: no private operator path, numbered vulnerability
  identifier, or private-key marker found.

## Artifact identities

- selected evidence SHA-256:
  `216d5d271b1d6aa4a83916eecbbeddc04f65a12504cbdb421529739c6aa4e7e6`;
- strict manifest SHA-256:
  `ffb452bc2f0a012935b0b0e7b44a808dca1a76e6ae8a169af30fbed08cd8d4c5`;
- normalized report SHA-256:
  `0f1100d80b7197ed0c1fdcee48ef25f171423b4b00253b11ecdd6f1424e04196`.

## Repository state

No recovered target code was executed and no reset, recovery, update, mount,
write, slot, boot, or persistence action was performed. Parent integration
committed and published the reviewed package without staging the concurrent
MICOM source modification.
