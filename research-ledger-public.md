# Public research status

This repository contains sanitized IONIQ 5 research findings, tools, and tests. The private workflow ledger and frozen Council packets are retained in the local private archive because their absolute paths and hash-bound review records cannot be altered without invalidating the original review. Historical acceptance statements in the IONIQ history describe the original private evidence; this public snapshot independently validates the files it publishes.

The owner USB evidence established installed infotainment software `NE_E.EUR.S5W_L.001.001.250604` and head-unit model `NEAE.S5BLC.AEU`; see [sanitized findings](evidence/vehicle-usb/README.md). No live vehicle action, firmware writing, or flashing was performed for this release.

The execution-free FUMO trust-chain work now covers four linked boundaries:

- [wildcard recovery-signal trust](evidence/appfumo-dbus-recovery-signal-boundary.md),
  including the Qt 5 subscription, guarded local consumer, uid-conditioned
  default-deny/root-allow sender policy, launcher identity, and
  SMACK/runtime-reachability boundary;
- [parameterized verifier provenance](evidence/appfumo-parameterized-verifier-provenance.md)
  for the nested controller-resource route;
- [partition-write integrity](evidence/appfumo-partition-write-integrity.md),
  including pre-write source checking, pathname reopen, non-hash mode, and the
  absence of direct cryptographic readback in the reviewed completion route;
- [boot activation](evidence/appfumo-boot-activation-boundary.md), binding local
  reset/recovery request construction and a streamed canonical-rootfs inventory.

These results do not establish same-bus reachability for an arbitrary label,
accepted modified content, request execution, slot activation, mark-good, boot
counters, rollback, persistent slot selection, code execution, root,
persistence, or external MICOM/ABL/bootloader behavior.

The formerly parallel repository histories have been combined through merge
ancestry rather than replacement. The same reviewed combined branch and README
are published to both repositories so neither lineage's work is discarded.
