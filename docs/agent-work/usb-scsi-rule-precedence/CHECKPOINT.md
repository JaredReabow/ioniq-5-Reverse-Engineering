# USB mass-storage rule-precedence checkpoint

## Status

Implemented, executed offline, and accepted locally. The exact recovered stack showed that an ordinary empty-serial USB mass-storage device does not reach the vulnerable `scsi_id` helper because the earlier `usb_id` rule creates nonempty `ID_SERIAL`.

## Accepted result

Classification: `usb-id-suppresses-scsi-id`.

Observed exact frame:

```text
USB_SCSI_RULE_PROBE_BEGIN
USB_SCSI_RULE_ARTIFACTS=verified
USB_SCSI_RULE_MODULES=loaded
USB_SCSI_RULE_TARGET=sda
USB_SCSI_RULE_USB_SERIAL_ATTR=absent
USB_SCSI_RULE_BLOCK_READONLY=1
USB_SCSI_RULE_ROOT_READONLY=1
USB_SCSI_RULE_UDEVADM_RC=0
USB_SCSI_RULE_USB_ID_IMPORT=present
USB_SCSI_RULE_ID_BUS=usb
USB_SCSI_RULE_ID_SERIAL=QEMU_QEMU_HARDDISK-0:0
USB_SCSI_RULE_ID_SERIAL_SHORT=absent
USB_SCSI_RULE_ID_SCSI_SERIAL=absent
USB_SCSI_RULE_SCSI_ID_EXECUTION=absent
USB_SCSI_RULE_PROBE_COMPLETE
```

The QEMU USB device had no `serial` sysfs attribute. `usb_id` nevertheless built `ID_SERIAL` from the SCSI vendor/model plus target/LUN, making the line-34 `ENV{ID_SERIAL}!="?*"` predicate false.

## Safety

- fixed EHCI/QEMU USB mass-storage model;
- explicit empty USB serial;
- 4 MiB all-zero disk with no partition table/filesystem;
- disk `snapshot=on,readonly=on`;
- recovered root remounted read-only before rule evaluation;
- `udevadm test` only; no kernel uevent or daemon;
- `-nic none`;
- no control characters, injected property, unit name, service request, shell, root transition, or persistence.

## Artifacts

- tool: `tools/uk_fw/usb_scsi_rule_precedence_probe.py`;
- tests: `tests/test_usb_scsi_rule_precedence_probe.py`;
- reviewed evidence: `evidence/artifacts/udev-candidates/cve-2026-40225-usb-scsi-rule-precedence.txt`;
- reviewed evidence SHA-256: `4d4de48bd7e9c8c541e3ead056e1bac9c919e6a6a5c4922dd180740513d57417`;
- ignored primary JSON: `work/usb-scsi-rule-precedence-20260325/usb-scsi-rule-precedence.json`;
- primary JSON SHA-256: `51ce9a437295ed82e3b624fcddc84325e738e033f106583e2c0660d24f342800`;
- VM run: `work/vm/vendor-userspace-260128/runs/1793635062045933000`.

## Validation

- focused: `37 passed, 9 subtests passed in 0.06s`;
- canonical: `1043 passed, 352351 subtests passed in 169.04s`;
- canonical log SHA-256: `69daaea7751be2a1e2e6869056257e92a0c178e2a6ed904f2caf1f748d98f44b`;
- `py_compile`: passed;
- `git diff --check`: passed.

## Scope correction

The exact kernel configuration also disables `CONFIG_SCSI_ISCSI_ATTRS`, `CONFIG_SCSI_LOWLEVEL`, and `CONFIG_MEDIA_USB_SUPPORT`; no iSCSI or generic USB-video module is installed. Thus the public advisory's ordinary iSCSI and USB-V4L transports are not presently exact stock entry vectors on the recovered build. The vulnerable helper mechanisms remain present, but end-to-end physical root is unproved.

## Routing

Fable remains unavailable because the installed Fable route is not advertised for native v2 subagents. No alternate provider or paid-route probe was used.

## Resume action

Audit vendor/internal IPU4 camera metadata producers and any non-USB SCSI registration path. Determine whether any attacker-influenced external hardware can reach either vulnerable helper despite the recovered transport exclusions.
