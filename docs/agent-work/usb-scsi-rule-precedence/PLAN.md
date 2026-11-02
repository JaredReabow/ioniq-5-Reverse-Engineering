# USB mass-storage rule-precedence control

## Objective

Determine whether an ordinary USB mass-storage block device can reach the recovered `scsi_id` CVE-2026-40225 output path, or whether the earlier `usb_id` rule always populates `ID_SERIAL` and suppresses the later conditional `scsi_id` import.

## Safety boundary

- Offline exact recovered VM only, with `-nic none`.
- Fixed QEMU USB mass-storage device with an empty USB serial and a zero-filled read-only 4 MiB backing file.
- No control characters, second property, `SYSTEMD_WANTS`, `REMOVE_CMD`, unit name, shell request, uevent, daemon, PID 1 handoff, mount, filesystem, or target write.
- `udevadm test` evaluates one synthetic add action against the already-enumerated benign block device; it does not emit a kernel uevent.
- The recovered root and attached USB disk are read-only at evaluation time.

## Design

Add `tools/uk_fw/usb_scsi_rule_precedence_probe.py` using the existing hash-bound `vm_boot` harness. The probe will:

1. verify the exact prepared VM workspace;
2. create a fixed zero-filled project-local disk image;
3. attach it read-only through QEMU EHCI and USB mass storage with an explicitly empty USB serial;
4. load only the recovered SCSI/EHCI/USB-storage modules needed for enumeration;
5. verify exact hashes for `udevadm`, `scsi_id`, and `60-persistent-storage.rules`;
6. prove the emulated USB device has no serial sysfs attribute and the block device is read-only;
7. run exact recovered `udevadm test --action=add` and record only fixed marker classifications;
8. require `usb_id` execution, nonempty `ID_SERIAL`, absent `ID_SERIAL_SHORT`, absent `ID_SCSI_SERIAL`, and no `scsi_id` execution record;
9. emit a deterministic JSON report with explicit physical-bench and non-USB-SCSI limitations.

Add focused tests, a reviewed compact evidence artifact, primary evidence documentation, and a resumable checkpoint.

## Interpretation

A passing control proves that this ordinary USB mass-storage geometry does not reach `scsi_id` because `usb_id` populates `ID_SERIAL` first. It does not prove that every malformed USB device, non-USB SCSI transport, SCSI tape, CCISS device, or physical head-unit port is blocked. It does not change the exact vulnerable `scsi_id` binary finding; it narrows physical USB reachability.

## Acceptance

- Fixed benign descriptor and QEMU topology only.
- Fail-closed marker sequence and artifact hashes.
- Negative evidence is explicit: missing observations fail rather than pass.
- Focused and canonical tests pass.
- Report and prose do not promote the VM control to physical-device proof.

## Routing

The requested Fable builder remains unavailable: Astra's installed Fable route is present but not advertised for native v2 subagents. No alternate provider or paid-route probe is permitted. Astra therefore owns architecture, implementation, review, validation, integration, and publication for this bounded phase.
