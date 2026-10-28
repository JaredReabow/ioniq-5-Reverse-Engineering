# Vendor-kernel VM: interactive userspace reached

Updated 2026-10-20. **Using only existing local files and installed tools, the
recovered EU kernel now mounts an ext4 SD root and executes interactive shell
commands.** This is a VM-adapted vendor kernel with BusyBox research userland,
**not the infotainment UI or an unchanged complete firmware system**.

**Later in the same continuation:** a QEMU window and keyboard-controlled
800×480 diagnostic display also work, without an additional kernel patch.
See [`vendor-kernel-graphics.md`](vendor-kernel-graphics.md) for the verified
screenshots and graphical launch command. This is our test program, not the
recovered infotainment application.

No firmware was flashed, no head unit was contacted, and nothing was downloaded.
The official container and the extracted boot image were not modified. One
SDHCI PCI-match entry was changed **in guest RAM** at a debugger breakpoint.

## Measured result

The repeatable harness produced:

```
sdhci-pci 0000:00:02.0: SDHCI controller found [1b36:0007] (rev 0)
mmc0: SDHCI controller on PCI [0000:00:02.0] using ADMA
mmcblk0: mmc0:8294 QEMU! 256 MiB
VFS: Mounted root (ext4 filesystem) on device 179:0.
IONIQ_VM_USERSPACE_READY
4.1.27-abl
uid=0 gid=0
```

These are distinct milestones: controller probe, block-device discovery, root
mount, PID 1 userspace execution, and a command/response round trip through the
serial shell. `/proc`, `/sys`, devtmpfs and smackfs are mounted. The collected
ABL parameters are visible under `/sys/kernel/abl/`.

Evidence:

- [`vm-local-only/serial-success.log`](vm-local-only/serial-success.log): full
  serial output from the repeatable launcher, including command responses.
- [`vm-local-only/result-success.json`](vm-local-only/result-success.json):
  userspace/root mount true, command exit 0, no timeout or launcher error.
- [`vm-local-only/ram-patch.json`](vm-local-only/ram-patch.json): exact original
  and replacement bytes, address and scope.
- [`vm-local-only/result-unpatched.json`](vm-local-only/result-unpatched.json):
  negative control with the same new disk and command line but **no table
  adaptation**; still waiting for `/dev/mmcblk0` at the eight-second deadline.
- [`vm-local-only/evidence-sha256.json`](vm-local-only/evidence-sha256.json):
  hashes of retained evidence and locally retained diagnostic logs.

The launcher deliberately terminates QEMU after a successful noninteractive
check. Its QEMU return code of `-15` records that termination, not a guest panic.
Prepared artifact hashes were checked again after the boot; all were unchanged.

### Validation

These counts describe the original boot milestone. The 2026-10-21 continuation
passes **137 total tests**, plus fresh serial and graphical VM regressions;
see [`local-ui-recovery.md`](local-ui-recovery.md). No original evidence hash
was changed to record the later result.

- 19 new offline tests cover boot-header/bounds parsing, exact table layout,
  patch refusal/readback, debug-protocol framing, output confinement and QEMU
  arguments.
- The complete suite passes **100 tests** with the already-installed
  `/Users/researcher/.platformio/penv/bin/python3`. Bare Homebrew Python 3.13 passes
  the VM tests but lacks `cryptography`, which an unrelated existing test module
  imports; no dependency was downloaded to resolve that.
- A live `--cmd false` control reaches userspace but records command exit 1 and
  returns harness exit 1. Merely reaching a prompt does not make every test pass.
- Full local test output: `work/vm/local-only/tests-full-platformio.log`.
  Live failing-command result: `work/vm/bootable/runs/1792471105870910000/result.json`.

## What was actually wrong

### 1. SDHCI PCI matching

The driver exists. Its structure is named `sdhci_driver`, not
`sdhci_pci_driver`. Reading its `id_table` pointer established:

| Object | Virtual address |
|---|---|
| `sdhci_driver` | `0xffffffff81a42980` |
| `id_table` | `0xffffffff8164c960` |
| `sdhci_driver_init` | `0xffffffff81b24bac` |
| Table entry 61 | `0xffffffff8164d100` |

QEMU's actual PCI ID is **`1b36:0007`**, class `0805`, not the previously guessed
`1b36:000e`. Its monitor and the later guest probe agree.

The table contains 62 nonzero records and a zero terminator. It lacks both an
explicit QEMU match and an unrestricted SDHCI class match. Entry 61 is a
**vendor-restricted AMD class match** (`1022:*`, class `080500`, mask `ffff00`),
with an AMD-quirks pointer. See the complete
[`sdhci-pci-table.json`](vm-local-only/sdhci-pci-table.json).

For this emulator only, the harness stops at `sdhci_driver_init`, verifies the
original 32 bytes, and replaces entry 61 with:

```
vendor=1b36 device=0007 subvendor=* subdevice=*
class=080500 mask=ffff00 driver_data=0
```

The zero `driver_data` avoids applying AMD-specific quirks to QEMU's generic
controller. The write is read back, the breakpoint removed, and the guest
resumed. A SHA-256 check pins the exact supported boot image. Unexpected bytes
cause a refusal, not an attempted patch.

This changes the **running kernel's table**, so the result must not be called
an unmodified stock-kernel boot. It is not an update-signature bypass.

### 2. The original test disk used unsupported ext4 features

Once the controller bound, the old `work/vm/rootfs.img` was rejected:

```
EXT4-fs (mmcblk0): Couldn't mount because of unsupported optional features (2000)
VFS: Unable to mount root fs on unknown-block(179,0)
```

Its feature list included `metadata_csum_seed`, `metadata_csum` and
`orphan_file`. The new disk uses an explicit, conservative feature allowlist
rather than modern `mkfs.ext4` defaults. It mounts successfully. The old disk
was retained unchanged.

### 3. Explicit userspace entry and discovery wait

The root contains `/init`. The launcher now passes **`init=/init`**, as well as
`rootwait`, a short root delay and `rootfstype=ext4`. Earlier commands omitted
`init=/init`; even a successful root mount would not have selected that script
through the usual default init paths.

## Reproduce using local resources

From the project directory, prepare a **new** workspace:

```sh
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py prepare \
  --container /Users/researcher/Downloads/NaU/IONIQ5_EU/HU/images/iasImage_1280_sub \
  --busybox work/vm/busybox \
  --workspace work/vm/bootable
```

`work/vm/bootable` already exists from the successful test. Preparation refuses
to overwrite it; reuse it for runs or choose a fresh workspace name.

Run a bounded command/response check:

```sh
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/bootable --sdhci-compat --timeout 60
```

Open the line-oriented serial shell in a terminal:

```sh
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/bootable --sdhci-compat --interactive --timeout 0
```

Use `/bin/busybox <applet>` for utilities; `sh`, `echo`, `printf` and other shell
built-ins work directly. Ctrl-C stops the VM. This minimal shell currently
reports that job control is unavailable; it is not a full terminal/getty setup.

The tool records command arguments, serial logs, patch bytes and result JSON
under `work/vm/bootable/runs/`. It disables the guest NIC and uses a temporary
snapshot overlay, leaving the base image unchanged. The debug socket is a local
Unix socket, not a listening TCP port. Temporary overlays and generated files
stay inside the project. There is no package-fetch or BusyBox-download action.

## Input identity and boot parameters

- Container SHA-256:
  `55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0`
- Boot image: container range `[1008:6209536]`, 6,208,528 bytes.
- Boot-image SHA-256:
  `85e0086202758117015437a5ce7b580d7d32484807d1953c3a16e571f65f3f59`
- Recovered ELF SHA-256:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`
- Kernel banner: Linux `4.1.27-abl`, built 28 January 2026.

The boot image contains the `0xaa55` boot flag, `HdrS` header, protocol `0x020d`
and `setup_sects=30`. Bare `vmlinux` is not a substitute for that boot image.
The kernel lacks external initrd support; the launcher no longer constructs an
unused initramfs or defaults to the unbootable bare ELF.

`setup_abl_params` is registered under the case-sensitive prefix **`ABL.`**. It
collects up to 16 name/value pairs. The emulated boot supplies:

```
ABL.oemkm=40@20000000 ABL.seed=21000000,21000040
```

A synthetic 64-byte empty manifest and two synthetic 64-byte seeds are loaded
into those physical addresses. Both subsystem initializers report success.
These are **not authentic device seeds or firmware-decryption material**.

## What the existing resources provide for the UI

The local-only inventory checked all 36 files in each EU/AU package, both map
ZIP central directories (1,335 and 374 entries), and the two distinct plaintext
fixed-voice tar archives (49 and 351 members, including the first 512 bytes of
every regular member). No ELF or QML candidate was found in those voice headers;
the map filename checks found no application/library/QML candidates.

`AppUpgrade`, `mango-rootfs.tar.gz`, `new_gui.tar.gz` and `appnavi.tar` remain
opaque in both package trees, consistent with the previously documented
encrypted packaging. **This is a bounded inventory, not proof that no further
local recovery route exists.** No plaintext vendor GUI or its dependency stack
has been recovered by this work. See
[`local-ui-inventory.json`](vm-local-only/local-ui-inventory.json).

The kernel has no built-in framebuffer console and its configured DRM driver
is i915, not a QEMU display driver. Nevertheless, the subsequent graphics
experiment **demonstrated a working userspace display and keyboard path** by
mapping QEMU's virtual PCI VGA resources. It does not provide a DRM/EGL/Qt
backend for the vendor application, nor does it recover that application's
binaries. See `vendor-kernel-graphics.md`.

The new shell therefore advances the VM, but does not satisfy the separate goal
of interacting with the real infotainment UI. No substitute dashboard is being
presented as that UI.

## Corrections to earlier reports

- **The observed panic was a root-mount failure.** The full earlier trace goes
  through `mount_block_root` and `prepare_namespace`. Adjacent missing-seed
  warnings did not establish an anti-tamper panic. Successful synthetic
  initialization does not establish an anti-tamper bypass either.
- **Sparse PCI log lines did not prove enumeration was broken.** Runtime binding
  now succeeds after the narrowly scoped table adaptation. The original logs
  already showed PCI-device quirks and `lpc_ich` activity.
- **The root was not mounted in the earlier attempts.** That milestone is now
  established by an explicit mount message followed by guest command execution.
- **The previous permanent-impossibility conclusion was unsupported.** Treat
  `child-notes/12-vm-review.md` as a historical, overconfident review, not a
  current acceptance decision or a proof that all VM approaches are impossible.
- **Keystore configuration is package evidence, not installed-unit evidence.**
  `KEYSTORE_TESTMODE`, `KEYSTORE_DEBUG`, `KEYSTORE_SECURE_BOOT_IGNORE` and
  `KEYSTORE_TEST_MIGRATION` are enabled in the recovered config. This does not
  establish the installed firmware version or disable every boot-trust check.
- **No new Council acceptance was issued.** The legacy ledger's accepted-input
  hashes were not refreshed to label this new VM work as reviewed.

Fable's installed route failed the read-only native-subagent availability check;
no Fable review is claimed for this continuation. All implementation and runtime
checks above were performed in the parent session with local tools.
