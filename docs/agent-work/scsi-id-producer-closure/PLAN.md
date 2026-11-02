# Recovered scsi_id producer closure

## Objective

Enumerate every built recovered SCSI disk producer that can reach the installed `scsi_id` rule and determine whether ordinary USB or ATA devices bypass prior identity imports with unsafe property text.

## Method

A deterministic host-only audit will bind:

1. exact kernel configuration for disk, tape, optical, generic, low-level, network, SAS/FC/SRP, FireWire, USB-storage, and ATA support;
2. the complete 160-module inventory and exact ATA/SCSI module subset;
3. exact persistent-storage rule ordering for `ata_id`, `usb_id`, and `scsi_id`;
4. the accepted ordinary USB no-iSerial control;
5. exact recovered `ata_id` sanitizer, allowlist, replacement loop, and output instructions;
6. the remaining malformed/failure and physical-port boundaries.

## Safety

No device, VM, ioctl, helper, target binary, uevent, property, service, network, mount, write, root action, or payload is executed or generated. The audit only reads and hashes local recovered files and accepted reports.

## Acceptance

- Complete enabled producer classes are enumerated.
- Ordinary USB and ATA precedence are separately established.
- ATA model/serial control-character handling is byte-bound before output.
- Disabled tape/optical/generic/network/low-level classes are explicit.
- Failure and alternate-installed-build cases remain unproved rather than silently closed.
- No stock external physical entry, root, or persistence is claimed.
