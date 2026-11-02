# Recovered scsi_id producer closure checkpoint

## Status

Implemented, generated, and focused-validation complete. No ordinary built recovered SCSI producer reaches `scsi_id` with unsanitized identity text.

## Findings

- ordinary USB mass storage: prior `usb_id` suppression, including exact no-iSerial control;
- ordinary ATA: prior exact sanitizing `ata_id` suppression;
- `ata_id` allows alphanumeric plus `#+-.:=@_` and replaces invalid model/serial/revision bytes with `_` before output;
- SCSI optical, tape, generic, iSCSI, SAS/FC/SRP, FireWire, CCISS, and other low-level producers: not built;
- malformed enumeration or prior-import failure: unproved;
- external stock property injection, root, and persistence: not demonstrated.

## Deliverables

- `tools/uk_fw/scsi_id_producer_closure.py`;
- `tests/test_scsi_id_producer_closure.py`;
- `evidence/scsi-id-producer-closure.md`;
- `evidence/artifacts/udev-candidates/scsi-id-producer-closure.json`;
- updated transport and primary CVE evidence.

## Artifact identity

- schema `ioniq-scsi-id-producer-closure/v1`;
- size `6,209` bytes;
- file SHA-256 `c4119f8d15d88b601dea5c632825207167e9d31c8ebf23070167924c4d8aad5f`;
- canonical SHA-256 `3f9db2c6485eb7309ccf73adf50da3a260f9593779c0d69ecd27936fddb7ff20`.

## Validation

- focused phase scope: `37 passed, 6 subtests passed in 0.64s`;
- exact config, complete 160-module inventory, rules, transport report, ELF ranges, patterns, and strings validated;
- normal and `PYTHONIOENCODING=utf-16` stdout byte-identical;
- canonical: `1062 passed, 352357 subtests passed in 160.02s (0:02:40)`;
- canonical log SHA-256: `53f89ca6c1becfb67d2833037b2535e5e2746a37414c819f69c1ab05dd0036f8`.

## Safety

No device, VM, ioctl, helper, uevent, property, service, network, mount, target write, root transition, or persistence mechanism was executed.

## Resume action

Obtain a future passive disconnected-bench identity capture. If and only if exact prerequisites match, characterize benign prior-import failure semantics without a unit name, service request, property injection, control-character descriptor, or target write. Otherwise continue unrelated static trust/update/TXE work.
