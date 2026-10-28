# HANDOVER — IONIQ 5 Gen5W research

Updated **2026-10-21**. Current goal: run and interact with the **actual
Hyundai/LG infotainment UI** using resources already available locally.
**That goal remains unmet.** The VM boots and displays our diagnostic; the
vendor applications remain unrecovered.

This replaces the stale pass-12 handover. Older claims remain in Git history
and the historical evidence notes; see `evidence/corrections-log.md` before
quoting them.

## What currently works

| Milestone | Measured result / boundary |
|---|---|
| Vendor kernel | EU package Linux `4.1.27-abl`, x86-64; not Android |
| VM storage/root | QEMU SDHCI binds after one exact-build PCI-table adaptation **in guest RAM**; compatible ext4 root mounts |
| Userspace | Interactive static BusyBox research root; `/proc`, `/sys`, devtmpfs and smackfs mount |
| Graphics/input | 800×480 direct-QEMU-VGA diagnostic; QMP keyboard R/G/B/Q and whole-frame pixel checks pass |
| Real infotainment UI | **Not recovered or executed**; dependencies, launcher, services and graphics API requirements remain unknown |
| Regression checks | **137 unit tests pass**; fresh serial and graphics VM checks pass on 2026-10-21 |

The boot-image file is unchanged, but the running kernel is adapted. Call it a
**VM-adapted vendor kernel**, not a complete stock-firmware boot. Synthetic
`ABL.oemkm` / `ABL.seed` inputs initialize the keystore and manifest subsystems;
they are not recovered device keys or proof of a trust bypass.

## Current constraints

- User-owned UK 2021 IONIQ 5 Ultimate head unit, disconnected from the vehicle.
  **No physical or network access to it is available.** Its installed firmware
  version remains unconfirmed.
- **Existing local resources only.** Do not download firmware, kernels,
  libraries, tools or keys, or make a bench export the immediate solution.
- Keep generated files, VM disks, sockets and test temporaries in this project.
  Do not delete anything outside it; preserve unrelated and pre-existing work.
- No flashing, host-root operations, host filesystem mounts, or substitute
  dashboard presented as the vendor UI.
- Fable was requested as reviewer/planner only. Its tested route was unavailable;
  no substitute child is verified as Fable.
- Unit-test results and evidence hashes are **not Council acceptance**. Do not
  refresh legacy accepted-input hashes to manufacture a pass.

## Run the existing VM

From `/Users/researcher/Documents/ChatGPT/reverse engineering/ioniq research`:

```sh
# Interactive serial research shell
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/bootable --sdhci-compat --interactive --timeout 0

# Windowed diagnostic ONLY; R/G/B change colour, Q returns to the shell
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/graphics --sdhci-compat \
  --display cocoa --cmd /bin/vm-display --interactive --timeout 0

# Automated keyboard and pixel verification
/opt/homebrew/bin/python3.13 tools/uk_fw/vm_boot.py run \
  --workspace work/vm/graphics --sdhci-compat --graphics-smoke
```

Use `/bin/busybox <applet>` in the minimal shell. Ctrl-C stops the launcher.
QEMU has no NIC, uses a snapshot disk, and exposes only local debug sockets.
Preparation refuses to overwrite existing workspaces. Complete preparation,
controls, exact addresses and hashes: `evidence/vendor-kernel-vm.md`.

The display program bypasses missing framebuffer-driver support by mapping
QEMU VGA PCI resources. **It is not a DRM/EGL/Qt compatibility backend.**
Details and actual screenshots: `evidence/vendor-kernel-graphics.md`.

## Latest local recovery work

Read `evidence/local-ui-recovery.md` and its retained evidence directory.

1. **Boot public-key hypothesis:** all 12 plaintext EU/AU `ipk.` containers
   share one RSA-2048 public key and pass strict signature controls. Scanning
   the first/last 16 KiB of 38 opaque envelopes, at every byte offset and in
   both byte orders, made **2,392,520 RSA attempts and found no valid type-1
   block**. This tests one key, one padding format and recorded edge ranges,
   not every possible wrapped-key location or algorithm.
2. **Installed Mac updater hypothesis:** static inspection of Navigation
   Updater `261.015.0.215` found text/API AES routines and constants. Two
   reconstructed constant pairs were tested against the same 38 files under
   bounded CBC-start/IV hypotheses. Two raw gzip-marker matches were the same
   invalid sample in both packages; reserved flags and zlib rejected them.
   **No validated firmware plaintext was recovered.** Other crypto modes and
   derivations were not exhausted. The updater was not launched or contacted
   online.
3. **Earlier plaintext searches:** full-byte ELF/gzip/tar probing covered
   7,134,873,011 bytes across 14 opaque payloads with no validated candidate.
   Prefixes of 1,571 regular map ZIP members and two distinct plaintext voice
   archives were also inspected. See the graphics evidence for exact bounds.

`new_gui.tar.gz`, `mango-rootfs.tar.gz`, `appnavi.tar` and updater payloads remain
opaque. The publicly saved `DecryptToPIPE` and key files are placeholders.
The older Chimaera work documents a real decryptor/key-file mechanism, but does
not itself establish current-package applicability or supply those artifacts.
High entropy or a failed bounded scan is **not proof of permanent offline
impossibility**.

## Useful local resources

- EU: `/Users/researcher/Downloads/NaU/IONIQ5_EU`, version
  `NE_E.EUR.S5W_L.001.001.260128`, model `101489`.
- AU: `/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU`, version
  `NE_E.AUS.S5W_L.001.001.260319`.
- Supported boot container: EU `HU/images/iasImage_1280_sub`, SHA-256
  `55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0`.
- Kernel, correct symbols and saved Ghidra project: `work/eu-260128/`.
  Use `kallsyms.tsv` / `kallsyms_apply.tsv`, **not** the obsolete mispaired
  `kallsyms_fixed.tsv`. About 70 selected functions were decompiled, not the
  entire kernel.
- Existing static BusyBox: `work/vm/busybox`; QEMU: `/opt/homebrew/bin/qemu-system-x86_64`;
  e2fsprogs and LLVM under `/opt/homebrew/opt/`.
- Harness Python: `/opt/homebrew/bin/python3.13`. Full-test Python:
  `/Users/researcher/.platformio/penv/bin/python3` (includes `cryptography`). Do not
  assume the default Homebrew `python3` works.

```sh
mkdir -p work/test-tmp
TMPDIR="$PWD/work/test-tmp" /Users/researcher/.platformio/penv/bin/python3 \
  -m unittest discover -s tests -p 'test_*.py' -v
```

## Next useful work

- Pursue a **specific, falsifiable local recovery hypothesis**, not another
  cosmetic VM diagnostic. Preserve exact artifact identities and scan bounds.
  Remaining updater crypto is relevant only if its dataflow connects to
  head-unit payload processing; text/API encryption alone is not that link.
- Investigate unresolved envelope structure without assuming the old
  `3,385 + payload + 13,035` arithmetic proves field boundaries or semantics.
  Pass whole inputs to any authentic decryptor; do not strip guessed footers.
- If genuine application code is recovered, inventory ELF architecture,
  dynamic loader/libraries, launcher/config, services/IPC and display APIs
  **before** trying to execute it in the research VM.
- Keep serial/graphics controls and prepared-image hashes intact. Earlier
  exFAT/archive/XML parser harness work is secondary to the real-UI goal.

## Repository and evidence discipline

The actual Git root is now **this project directory**. Both current remotes,
`ioniq` and `origin`, point to `https://github.com/JaredReabow/Ioniq-5.git`.
Re-query before future integration; the historical parent/Kona layout is stale.
Stage exact reviewed paths, never all of `work/`. No raw firmware, VM disks,
client key bytes or private-key material belong in this continuation's commit.

Primary current notes: `vendor-kernel-vm.md`, `vendor-kernel-graphics.md`,
`local-ui-recovery.md`. Historical exploit, downgrade, partition-map and
trust-pinning claims require their original scope and current-build validation.
No stock-to-root path, authentic payload decryption, bootloader acceptance of a
self-signed image, or hardware flashing has been demonstrated here.

## Public repository sanitization (2026-10-28)

The proposed public snapshot excludes owner USB exports, imported upstream raw logs, core dumps, traces, driving/location data, and full-text third-party artifacts. It retains sanitized derived findings in `evidence/vehicle-usb/README.md`. The source checkout still contains uncommitted research work and local raw evidence; do not stage these into the public repository. GitHub server-side cached old commits require cleanup before visibility changes.
