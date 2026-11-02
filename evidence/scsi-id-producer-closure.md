# Recovered `scsi_id` producer closure

## Result

The recovered build has no ordinary enabled SCSI disk producer that reaches the vulnerable `scsi_id` import with unsanitized identity text:

- ordinary USB mass storage is stopped by prior builtin `usb_id`, including the accepted no-iSerial exact-stack control;
- ordinary libata disks are stopped by prior `ata_id`;
- exact recovered `ata_id` replaces disallowed model/serial/revision bytes, including control characters, with `_` before emitting `ID_SERIAL`;
- iSCSI, optical SCSI, tape, SCSI generic, SAS, FC, SRP, FireWire SCSI, CCISS, and other low-level SCSI producers are not built.

The vulnerable `scsi_id` helper remains an exact mechanism. Malformed enumeration that permits a usable `sd*` event while causing `ata_id` or `usb_id` to fail remains unproved, as does any different installed owner-unit build. No stock external SCSI property-injection path is demonstrated.

## Deterministic artifact

- tool: `tools/uk_fw/scsi_id_producer_closure.py`;
- output: `evidence/artifacts/udev-candidates/scsi-id-producer-closure.json`;
- schema: `ioniq-scsi-id-producer-closure/v1`;
- size: `6,209` bytes;
- file SHA-256: `c4119f8d15d88b601dea5c632825207167e9d31c8ebf23070167924c4d8aad5f`;
- canonical SHA-256: `3f9db2c6485eb7309ccf73adf50da3a260f9593779c0d69ecd27936fddb7ff20`.

The audit revalidates the exact kernel config, complete 160-module inventory, storage rules, accepted transport report, and recovered `ata_id` ELF. It executes none of them.

## Complete enabled producer classes

Exact configuration and the complete module inventory leave these disk-producing classes:

1. `CONFIG_USB_STORAGE=m`, with one `usb-storage.ko`;
2. `CONFIG_ATA=m`, with libata, AHCI, PIIX, and two PATA controller modules;
3. SCSI core and `sd_mod` used by those classes.

The only additional SCSI module is `scsi_transport_spi.ko`; no low-level SPI host adapter is built. Decisive disabled settings include:

```text
# CONFIG_SCSI_LOWLEVEL is not set
# CONFIG_SCSI_ISCSI_ATTRS is not set
# CONFIG_SCSI_FC_ATTRS is not set
# CONFIG_SCSI_SAS_ATTRS is not set
# CONFIG_SCSI_SAS_LIBSAS is not set
# CONFIG_SCSI_SRP_ATTRS is not set
# CONFIG_BLK_DEV_SR is not set
# CONFIG_CHR_DEV_ST is not set
# CONFIG_CHR_DEV_SG is not set
# CONFIG_TARGET_CORE is not set
# CONFIG_FUSION is not set
# CONFIG_FIREWIRE is not set
```

This excludes normal optical, tape, generic-SCSI, iSCSI, FC/SAS/SRP, FireWire, CCISS, and other low-level producer paths from the exact recovered configuration.

## Exact rule precedence

The hash-bound `60-persistent-storage.rules` evaluates:

- line 22: libata `sd*`/`sr*` with vendor `ATA` imports `ata_id` while `ID_SERIAL` is absent;
- line 28: non-removable USB ATA passthrough attempts `ata_id`;
- line 31: USB storage imports builtin `usb_id` while `ID_SERIAL` is absent;
- line 34: generic `scsi_id` runs only if `ID_SERIAL` remains absent;
- line 35: CCISS separately invokes `scsi_id`, but no CCISS producer is built.

The accepted benign no-iSerial USB control proved line 31 still generated `ID_SERIAL=QEMU_QEMU_HARDDISK-0:0`; line 34 did not run.

## Exact `ata_id` sanitization

Recovered `/lib/udev/ata_id` SHA-256:

`daea4efb76661e66bf596ceb3529598a25161f21c2d004ba48b20d6924a8d72d`

Four bounded exact ranges establish its identity dataflow:

| Range | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `0x2d1d..0x2d82` | `0x65` | `c91cdb89bcf2d8e7b668cea78b687e0eb31866c7854ddca5312f64834052db96` | sanitize model, serial, revision |
| `0x3182..0x320b` | `0x89` | `e82aef0e6aad2a25fdc79a6406dcc15eacf40ff67122998360a357ead17940a2` | emit model and serial properties |
| `0x5ae0..0x5b50` | `0x70` | `b6df7075de2009d50feb6191e7a032a92dd92eedb1a9bf5446bc9a63f2e4d6c9` | accepted-character predicate |
| `0x5b50..0x5c30` | `0xe0` | `dac300803f02a51d13818f7cb75341c990a6b06571b075877a0ac9c1df943408` | invalid-character replacement loop |

The predicate accepts ASCII alphanumeric bytes plus exact rodata `#+-.:=@_`. The replacement loop writes byte `0x5f` (`_`) for invalid single-byte characters. The main identity path invokes that loop separately for model, serial, and revision before its output block uses:

```text
ID_MODEL=%s
ID_MODEL_ENC=%s
ID_SERIAL=%s_%s
ID_SERIAL_SHORT=%s
ID_SERIAL=%s
```

A newline or other control character in an ordinary ATA identify string therefore does not survive into the emitted `ID_SERIAL` fields.

## Boundaries

This establishes normal recovered producer behavior, not a universal impossibility theorem. Still open:

- malformed USB or ATA enumeration that creates a usable block device but makes the prior import fail;
- a vendor out-of-tree producer absent from the complete recovered module/config set;
- a different owner-unit installed build;
- physical accessibility of any ATA controller or port;
- end-to-end property injection, unit activation, root access, or persistence.

Enabled ATA controller code alone is not evidence of an externally exposed SATA/PATA connector. No active physical test is justified without a passive disconnected-bench identity match.
