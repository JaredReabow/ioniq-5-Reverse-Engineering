# Update-candidate retained evidence

This directory contains bounded, reviewable static excerpts and deterministic
reports supporting update-path assessments. Original firmware and recovered
executables remain ignored under `work/`; retained files must not contain target
payloads, bypasses, private operator paths, or executable target material.

## AppDMClient AppUpgrade launch routing

- [`appdmclient-appupgrade-launch-routing-manifest.json`](appdmclient-appupgrade-launch-routing-manifest.json):
  strict canonical-rootfs/member, exact ELF/Build-ID/LLVM, complete
  instruction/FDE, selected FDE, complete direct-caller, machine-anchor, and
  literal-role expectations (SHA-256
  `61f3c6327bfeb521df2970f9fd281f828c0bd11ee219fc1ba98b5f29be53bf62`);
- [`appdmclient-appupgrade-launch-routing-report.json`](appdmclient-appupgrade-launch-routing-report.json):
  normalized deterministic report with static path roles and runtime facts
  retained as unknown (SHA-256
  `7584e9a7f4107f451bd690e05babefb60f6d20928ab27c5eb3efe4eb310b2449`).

The launch proxy builds logical `(int, QString, QString)` arguments in that
order. Its complete direct inventory has four app-ID-300 callers. In the
staging terminal split, marker presence selects the source-root-derived
AppUpgrade path; marker absence selects the fixed staged path only if the local
ELF/executable helper succeeds. The provisional stack-slot interpretation is
corrected: slot `0x8` is the staged destination, while slot `0x0` is the
source-root-derived executable. D-Bus delivery, AppLauncher dispatch, process
creation, execution, update acceptance, partition writes, boot acceptance,
root, and persistence remain unknown. Assessment:
[`../../appdmclient-appupgrade-launch-routing.md`](../../appdmclient-appupgrade-launch-routing.md).

## AppFUMO wildcard D-Bus recovery-signal boundary

- [`appfumo-dbus-recovery-signal-boundary-exact-static.txt`](appfumo-dbus-recovery-signal-boundary-exact-static.txt):
  byte-free FDE/transfer/anchor/literal-role hashes plus name-hashed canonical
  policy inventory and normalized kernel/daemon inventories (SHA-256
  `4b0c525ee7ec862dfc65df2e4e0a991d5bb934708dfb8ba1f102110759a95ab7`);
- [`appfumo-dbus-recovery-signal-boundary-manifest.json`](appfumo-dbus-recovery-signal-boundary-manifest.json):
  strict exact ELF, Build ID, rootfs, kernel config, LLVM, complete
  instruction/FDE, policy XML, launcher/label, and daemon-string expectations
  (SHA-256
  `ff934574db6c0204c05f1e2a3766b83b5ea60394b366d2c9ec8c902db7b6e82c`);
- [`appfumo-dbus-recovery-signal-boundary.json`](appfumo-dbus-recovery-signal-boundary.json):
  normalized deterministic report (SHA-256
  `826ed7c3fcfcd7077840fbad792a88737a2555ba9e2a528f1baf9179bd07a936`).

The exact Qt 5 subscription has wildcard service/path filters and fixed
hash-bound interface/member filters. Main `system.conf` default-policy counts
are reported separately from the 18-member `system.d` audit. The directory
contains 15 named-sender signal allows and one named-sender signal deny. One
hash-bound sender is denied in default scope and allowed for root: the deny can
override the main default receive allow for non-root, while the root rule later
allows root. The installed consumer uid is unknown. All 137
`send_destination` values are named/non-wildcard and do not match a
destination-less broadcast. Policy constraints do not authenticate the Qt
subscription's origin, and same-bus socket reachability under SMACK remains
unknown. The guarded local consumer may construct a separate asynchronous
recovery request, but external action, code execution, root, and persistence
are not established. Assessment:
[`../../appfumo-dbus-recovery-signal-boundary.md`](../../appfumo-dbus-recovery-signal-boundary.md).

## AppFUMO boot-activation boundary

- [`appfumo-boot-activation-boundary-exact-static.txt`](appfumo-boot-activation-boundary-exact-static.txt):
  selected FDE ranges, complete direct transfers, machine/literal/resource
  hashes, and canonical rootfs member identities, without target instructions,
  raw bytes, callable endpoint coordinates, serial bytes, or fallback text
  (SHA-256
  `216d5d271b1d6aa4a83916eecbbeddc04f65a12504cbdb421529739c6aa4e7e6`);
- [`appfumo-boot-activation-boundary-manifest.json`](appfumo-boot-activation-boundary-manifest.json):
  strict ELF/Build-ID/rootfs/LLVM, complete instruction/FDE, direct-transfer,
  anchor, literal/resource, selected-member, and full tar-inventory expectations
  (SHA-256
  `ffb452bc2f0a012935b0b0e7b44a808dca1a76e6ae8a169af30fbed08cd8d4c5`);
- [`appfumo-boot-activation-boundary.json`](appfumo-boot-activation-boundary.json):
  normalized deterministic report (SHA-256
  `0f1100d80b7197ed0c1fdcee48ef25f171423b4b00253b11ecdd6f1424e04196`).

The completion timer's QML signal, view signal relay, controller slot dispatch,
reset wrapper, and reset core form a closed local static chain. Reboot-system
and recovery are bound separately. Their asynchronous request arguments carry
no slot identifier and do not prove external action. The canonical rootfs
contains generic update, boot-control, and flashing components, but no reviewed
edge binds them to this AppFUMO flow. Slot activation, mark-good, counters,
rollback, persistent choice, and external MICOM/ABL/bootloader behavior remain
unresolved. Assessment:
[`../../appfumo-boot-activation-boundary.md`](../../appfumo-boot-activation-boundary.md).

## AppFUMO PartitionUpdater integrity and target selection

- [`appfumo-partition-write-integrity-exact-static.asm`](appfumo-partition-write-integrity-exact-static.asm):
  selected FDEs, complete direct-transfer inventories, literal/blob identities,
  and machine anchors without raw instruction bytes or target command/pathname
  text (SHA-256
  `e3acf80fdc76df6f1defd29d74fedcd1a62a90ef74ebe170f4a48591b20ec61c`);
- [`appfumo-partition-write-integrity-manifest.json`](appfumo-partition-write-integrity-manifest.json):
  strict exact ELF/Build-ID/LLVM, complete instruction/FDE identity,
  direct-transfer, anchor, literal, blob, and provenance expectations (SHA-256
  `5d3ca7bf8261805ca10d02d61d75ec1ee54c1205c66cb15be03a3e009dd0c5c5`);
- [`appfumo-partition-write-integrity.json`](appfumo-partition-write-integrity.json):
  normalized deterministic report (SHA-256
  `e84e0771dea6aabe8f76fbe5a495084d0d6ef42650d7c39bec54fe68ab55c612`).

The nonzero mode routes selected-primary and non-excluded entry source
pathnames through exact-zero integrity gates before the write starter; zero mode
reaches the writer directly. Verifier and writer reuse a stored pathname value
but reopen it independently, so object, byte, transformed-output, and final
partition identity remain unknown. Static inactive-target machinery, record
lookup, and the writer target field are bound, but the exact helper-return to
runtime-record assignment and all bootloader activation/mark-good behavior
remain unknown. The named post-write FDEs have no direct edge to five inventoried
file signature/hash helpers; broader absence is not claimed. Assessment:
[`../../appfumo-partition-write-integrity.md`](../../appfumo-partition-write-integrity.md).

## AppFUMO parameterized verifier provenance

- [`appfumo-parameterized-verifier-provenance-exact-static.asm`](appfumo-parameterized-verifier-provenance-exact-static.asm):
  exact Homebrew LLVM 23.1.3 FDE and selected instruction evidence without raw
  instruction bytes (SHA-256
  `6c0abdf94c0cec730d890cdacb0d87b44bc49410a7815007e0159a28ff22e187`);
- [`appfumo-parameterized-verifier-provenance-manifest.json`](appfumo-parameterized-verifier-provenance-manifest.json):
  strict ELF/tool, complete instruction/FDE identity, machine-anchor, direct-call,
  literal-role, and producer-class expectations (SHA-256
  `3631df881c6d5cd7a0e72979f5d2ad2491900e49dc74b99f78fc94ab6fbba665`);
- [`appfumo-parameterized-verifier-provenance.json`](appfumo-parameterized-verifier-provenance.json):
  normalized deterministic report (SHA-256
  `b04af647133dbe480590d27927daae994e17e72911dd9df4a62ee1260b96adb1`).

The two previously parameterized direct targets are one nested controller-
resource route. `0x9d1d2` receives an enumerated encrypted member under one of
four fixed resource trees; `0x140092` receives a QString copy of that same
source pathname before a pathname-based transformation to derived JSON or
binary output. These are not running/staged updater, descriptor, or general
firmware pathname roles in the bounded direct route. Verification and
transformation reopen the pathname, so authenticated-byte identity, output
success, final consumption, and all indirect/virtual/cross-process producers
remain unknown. Assessment:
[`../../appfumo-parameterized-verifier-provenance.md`](../../appfumo-parameterized-verifier-provenance.md).

## AppFUMO decryption direct producers and public-log observation

- [`appfumo-decryption-producer-exact-static.asm`](appfumo-decryption-producer-exact-static.asm):
  bounded Homebrew LLVM 23.1.3 FDE and instruction excerpts (SHA-256
  `d8783cbdc41f5aae6663f339ff2debe2c3e425c8a243845e823b53f087099eb1`);
- [`appfumo-copywhatsnew-index-60.json`](appfumo-copywhatsnew-index-60.json):
  deterministic metadata report binding local public slot
  `void copyWhatsNewFiles()` (SHA-256
  `8f9adf55fbb3f0f65ef565175901a92144d33cf0ebc28bb57bffe39bbb386ee1`);
- [`appfumo-decryption-public-log.json`](appfumo-decryption-public-log.json):
  normalized, token/volume-label-free report over the hash-bound tracked public
  log (SHA-256
  `0dc7fb9c2775b2b201ca3b7e38438f75f1db3aa9ddac4298f315ad2e6f35bb66`).

The exact ELF's three selected direct sites are in the `copyWhatsNewFiles()`
FDE and classify archive/system/control producer families. The expected public
log contains seven matching records, including line 21713 beyond the previously
listed six. Its installed binary identity and invocation mechanism remain
unknown; dynamic/indirect/external producer completeness and attacker control
are not established. Assessment:
[`../../appfumo-decryption-runtime-provenance.md`](../../appfumo-decryption-runtime-provenance.md).

## AppFUMO decryption Qt/D-Bus dispatch provenance

- [`appfumo-decryption-dispatch-provenance-exact-static.txt`](appfumo-decryption-dispatch-provenance-exact-static.txt):
  compact exact name/xref, inherited `qt_metacall`, constructor/connect,
  selected-object D-Bus registration/adaptor, incoming subscription, and targeted
  dispatch inventory (SHA-256
  `c712ff7592022f243c17739242e7e73345f0b91007d4acadced2a89ac2032baf`);
- [`appfumo-decryption-dispatch-provenance-manifest.json`](appfumo-decryption-dispatch-provenance-manifest.json):
  strict exact-input, Homebrew LLVM identity, selected-object, callsite,
  registration helper/option, row-derived adaptor forwarding, ordered hash, and
  privacy expectations (SHA-256
  `d20cefb6941d7c344fcd2c65d659c44a1b30e1a2df63d8694ad1354dec96b53a`);
- [`appfumo-decryption-dispatch-provenance.json`](appfumo-decryption-dispatch-provenance.json):
  compact deterministic report (SHA-256
  `01c26edeaa241f6577ac26f27a5d8c8b71a8ed2866954783752adc997d33814a`) regenerated by
  `tools/uk_fw/appfumo_decryption_dispatch_provenance.py` and verified by
  `tests/test_appfumo_decryption_dispatch_provenance.py`.

Callable D-Bus service/path bytes are represented only by lengths and SHA-256
hashes; the generated report emits no callable coordinate or operator path.

The selected constructor registers the exact `AppUpgradeEngine` object with
option `1 = ExportAdaptors` after attaching six adaptors. Their 30 local methods
(16 slots, 14 signals), 16 forwarding names, and 12 separate D-Bus signal
subscriptions contain no row-64 target. All 90 old-style connects and all 105
imported named invokes likewise contain no target name. This rejects only those
reviewed literal routes: runtime registration/policy, synthesized/indexed or
cross-library producers, exact-ELF invocation, and attacker control remain
unknown. Assessment:
[`../../appfumo-decryption-producer-provenance.md`](../../appfumo-decryption-producer-provenance.md).

## AppFUMO USB pathname provenance

- [`appfumo-usb-pathname-provenance-exact-static.asm`](appfumo-usb-pathname-provenance-exact-static.asm):
  archive-member identities plus complete dispatcher, mount, shipped
  systemd-udevd/libblkid, AppDMClient, and AppUpgrade excerpts (SHA-256
  `932510a860b40cce280f217670cbf2c213e31b0a90008ac5c011c933cd584e8f`);
- [`appfumo-iso9660-mount-prerequisite-exact-static.txt`](appfumo-iso9660-mount-prerequisite-exact-static.txt):
  compact post-delivery binding of canonical bzImage -> vmlinux -> IKCONFIG,
  config offsets, bounded 163-member module identities/aliases, generic type
  dispatch, direct mount calls, read-only retry, and success-signal dominance.
  LZ4 literal/match and aggregate growth are preflighted before extension;
  overlap copying is chunk-bounded and uses no repeated-pattern multiplication
  (SHA-256
  `7935f331841eed2374a8318ce5f4d9c287cc76225ebefbfd9dd4e5a94b62cc0e`).

The complete dispatcher proves that exact `usb-automount` uses `ID_FS_UUID` or
the serial/partition no-UUID alternate—not `ID_FS_LABEL`—as the final
`/media/usb/<port>/<component>`. Label and model are separate D-Bus fields.
Exact stock `./lib/libblkid.so.1.1.0` is SHA-256
`56a6b8b7fd08dcec92a6c1ad84bc7a7cc44071f33c571339415e1cbf00d60701`,
Build ID `c6f98d98cb2cbc2ff864167f37048233d90a8fef`. Constrained
VFAT/exFAT/NTFS/ext/UDF UUID-family negatives remain, but ISO9660 exact code
`[0x1c4c0,0x1c654)` copies 16 raw date bytes, checks only the all-ASCII-`'0'`
case, formats raw `%c` values at `0x35368`, and passes through UUID
`blkid_safe_string`. The matching util-linux v2.27.1 `iso9660.c` lines 110-151
has SHA-256
`601d9311b1a68b5fbccf7d6af28f089b4f919494b36edb7f144786cec651477b`.
Allowed shell/path-sensitive byte classes can therefore reach the UUID mount
component statically. Label preservation remains non-path, and the no-UUID
sanitizer/context negative remains.

Separate exact AppDMClient and AppUpgrade edges do not bind the AppDMClient
launch argument to inner AppUpgrade's package-base constructor. The follow-up
cryptographically binds canonical archive bzImage to bounded legacy-LZ4
vmlinux SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`
and unique gzip IKCONFIG/config SHA-256
`987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`.
`CONFIG_ISO9660_FS`, `CONFIG_UDF_FS`, and `CONFIG_BLK_DEV_SR` are unset. The
canonical 163-member inventory/metadata lack the tested isofs/ISO9660, UDF,
sr/sr_mod identities and SCSI CD-ROM aliases, without excluding every renamed,
inline, or vendor-equivalent implementation. The named canonical routes are
false, while broad exact-stack ISO9660 and physical-optical routes remain
unknown. Userspace recognition, generic direct `mount(2)`, and read-only retry
remain, and the success signal is post-mount only.

Physical ISO9660 source control, accepted/mounted media on an unidentified or
materially different installed runtime, end-to-end installed delivery, and
invocation of the relevant `decryptionFile` call with that path remain unknown.
Those gates would establish only pre-auth decryption-input delivery;
actual shell-sink delivery additionally requires authentication because the
verifier dominates command construction and `popen`. Command success and
amplification remain route-generic observations. Authentication acceptance,
command success, privilege/domain, root, and persistence remain unknown;
arbitrary command execution is not claimed. The
post-extraction route remains structural: `0x10281c` is system-tree,
`0x103398` controls-tree, and `0x102de9` top-level archive; decrypted-member-name
signature binding remains unknown.
Assessments:
[`../../appfumo-usb-pathname-provenance.md`](../../appfumo-usb-pathname-provenance.md)
and
[`../../appfumo-iso9660-mount-prerequisite.md`](../../appfumo-iso9660-mount-prerequisite.md).

## AppFUMO exact shell boundary

- [`appfumo-shell-boundary-exact-static.asm`](appfumo-shell-boundary-exact-static.asm):
  bounded Homebrew LLVM FDE, literal, substitution, direct-call, `popen`, read,
  close, return-path, and separate-function excerpts (SHA-256
  `a6bbe8e74630e7a64001a8bad2b5f67846f465473612a14e8bccf3aad47c5510`).

The exact `decryptionFile` FDE substitutes `encFile` and `destPath` into command
fields without an observed quoting/escaping operation, then directly reaches a
shared `popen` helper. Similar full templates and destination checks are retained
as a separate-FDE correction, and the adjacent output-returning helper has its
own FDE. This establishes static shell-sink structure, not pathname influence,
character survival, runtime reachability, command success, privilege, root, or
persistence. Assessment:
[`../../appfumo-shell-command-boundary.md`](../../appfumo-shell-command-boundary.md).

## AppFUMO Qt 5 local meta-method 64

- [`appfumo-qt-metaobject-exact-static.txt`](appfumo-qt-metaobject-exact-static.txt):
  bounded relocation, metadata, string, jump-table, dispatcher, and verifier-call
  excerpts with addresses and range hashes;
- [`appfumo-qt-metaobject-forwarding-manifest.json`](appfumo-qt-metaobject-forwarding-manifest.json):
  strict machine-code forwarding facts, accepted only when the current bytes of
  the preceding evidence excerpt match its bound digest, with producer
  provenance explicitly unresolved. Excerpt SHA-256 is
  `31a90d0d633d22823fe1e4e61aa1c7df159c1a1acef379fe4e7aa38c7195c1ee`;
  manifest SHA-256 is
  `ecf48b2ec0d5f5c6014e2ef7c4efbfdd25899a3b79da2f4cf808dda062bf16bb`;
- [`appfumo-qt-metaobject-index-64.json`](appfumo-qt-metaobject-index-64.json):
  deterministic decoder report (SHA-256
  `330799c5215a0d3fda7c8870820240cb023c9b3a6c9673100778a038fe1d14a3`).

Assessment:
[`../../appfumo-qt-metaobject-provenance.md`](../../appfumo-qt-metaobject-provenance.md).
The package resolves local `AppUpgradeEngine` metadata row 64 as public slot
`QString decryptionFile(QString encFile, QString destPath)` and its generated
argument forwarding. Follow-up bytes resolve the direct parent and local-count
subtractions but still do not supply an absolute QObject-derived method index.
The reviewed `ExportAdaptors` registration does not expose row 64, while
complete synthesized/indexed, indirect, cross-library, and runtime producers,
registration success/policy, exact-ELF invocation, attacker control, update
acceptance, root, and persistence remain unknown.

Reproduce the exact report only with both bounded evidence inputs:

```sh
<platformio-env>/bin/python3 tools/uk_fw/qt5_metaobject_rev7.py \
  --elf work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf \
  --metadata-va 0x444760 --stringdata-va 0x445260 \
  --local-method-index 64 \
  --evidence-manifest evidence/artifacts/update-candidates/appfumo-qt-metaobject-forwarding-manifest.json \
  --evidence-excerpt evidence/artifacts/update-candidates/appfumo-qt-metaobject-exact-static.txt
```

Other files retain earlier bounded update-route evidence and keep the claim
boundaries stated in their corresponding assessments.
