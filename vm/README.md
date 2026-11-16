# VM work included in this repository

The VM research uses the official European Standard Gen5W `260128` package
as a local analysis input. The current [handover](../HANDOVER.md) distinguishes
the measured kernel boot, authentic Home rendering, isolated AppNavi map
rendering and the unresolved Home-to-Navigation transition. The VM uses
guest-only compatibility adaptations; these results do not demonstrate
behavior on an unmodified vehicle head unit.

## Published material

- [Guest helpers](../tools/uk_fw/guest) and the
  [boot harness](../tools/uk_fw/vm_boot.py), with unit tests under
  [tests](../tests).
- [Reproduction source](repro): 195 authored shell, QML, assembler and Python
  files copied from the local `work/vm/` tree. Paths are preserved below
  `vm/repro/`; 48 files have the operator's home path changed to
  `/Users/researcher/`. [source-manifest.json](source-manifest.json)
  records original and published SHA-256 values.
- [Bounded evidence](evidence): 41 text summaries/disassembly excerpts and
  four inspected screenshots, with hashes in
  [evidence-manifest.json](evidence-manifest.json).
- [Navigation launch-status analysis](../evidence/navigation-launch-status-contract.md)
  and [defensive findings register](../Ioniq5-VULNERABILITIES.md).

The reproduction scripts are historical experiment records. They refer to
local firmware, generated guest images and build outputs at their original
`work/vm/` paths, so they are not standalone runnable commands in this
snapshot. Obtain the official package and rebuild the local inputs before
using a script. Check its exact paths and assumptions first.

## One-command local setup

With the verified EU package at `work/firmware/IONIQ5_EU`, run from the project
root:

```sh
python3 tools/uk_fw/setup_eu260128.py
```

This verifies all 35 `.ver` payloads, decrypts seven TE2 files, safely extracts
five archives into `work/decrypted-eu-260128/extracted-safe`, and prepares a
minimal kernel/serial-shell workspace at `work/vm/bootable-eu260128` when static
BusyBox and `mkfs.ext4` are available. To set up a local QEMU without root and
smoke-test that shell, use:

```sh
python3 tools/uk_fw/setup_eu260128.py --setup-qemu --boot-test
```

That optional mode downloads Ubuntu Jammy packages into ignored `work/tools/qemu`
without installing them system-wide. It runs QEMU in snapshot mode with no NIC
and the documented VM-only SDHCI adaptation. The extracted tree does not preserve
original file ownership, and the boot workspace is **not** the full authentic
Home/Navigation HMI. The setup script does not modify or execute vendor payloads;
all outputs remain under ignored `work/` and must not be committed.

`tests/test_vm_e2e.py` then re-boots that workspace and asserts the end-to-end
contract from the host: kernel identity, ext4 root through the SDHCI patch, root
shell, ABL loader arguments, run artifacts, and a relayed guest exit status. It
skips when QEMU or the workspace is absent. `vm_boot.py` resolves QEMU from
`IONIQ_VM_QEMU`, then `work/tools/qemu/bin/qemu-system-x86_64`, then `PATH`, so
the locally unpacked binary needs no `PATH` edit.

## Manual inspection

Two ways to look at a run yourself, both offline and snapshot-only.

**Interactively at the serial shell** — the harness forwards your terminal into the guest:

```sh
# kernel shell
python3 tools/uk_fw/vm_boot.py run --workspace work/vm/bootable-eu260128 \
    --sdhci-compat --interactive --timeout 0

# recovered vendor userspace, with the launcher chain running
python3 tools/uk_fw/vm_boot.py run --workspace work/vm/vendor-userspace-260128 \
    --sdhci-compat --interactive --timeout 0
```

Inside the vendor guest the chain script and its artifacts are on disk, so you can poke at
a live system: `/opt/vm/vendor-chain.sh` re-runs the stages, `/tmp/chain/` holds the
launcher, weston and client logs, `dbus-send` talks to the manager, and
`weston-screenshooter` (run from `/tmp`) captures the real compositor.

**With a display** — `--display vnc` serves the guest framebuffer on
`127.0.0.1:0` (connect any VNC client); `--display gtk` or `sdl` opens a local window
when the host has one. The guest itself stays headless and network-free either way.

## Recovered vendor userspace

The kernel shell above contains no vendor code. The recovered root is booted from a
second workspace, built offline from the same extracted trees:

```sh
pip install --user ziglang                       # guest helpers for glibc 2.25
python3 tools/uk_fw/vendor_rootfs.py prepare \
    --container work/firmware/IONIQ5_EU/HU/images/iasImage_1280_sub
python3 -m unittest discover -s tests -p 'test_vm_vendor_e2e.py' -v
```

`prepare` hardlinks the vendor root and the `new_gui`/`navi` trees into
`work/vm/vendor-userspace-260128/rootfs-tree`, adds a research init and the staged
chain, and images them as an 8 GiB ext4 SD card. QEMU accepts only power-of-two card
sizes, which is why the image is larger than the tree. The chain brings the vendor
dynamic loader, system and session D-Bus, weston 1.10 (`headless-backend.so` with
`ivi-shell.so`, selected from the config file), `dlt-daemon` and `AppLauncher` with
`ApplicationManager` up in about 35 seconds under TCG.

`refresh --workspace <dir>` replaces `/init`, `/opt/vm/vendor-chain.sh`, the weston
config and the guest helpers inside the existing image, then rewrites the manifest
hashes; use it while tuning instead of paying for a full re-image.

`tests/test_vm_vendor_e2e.py` asserts the stages from the host. The interposition
fact is worth stating precisely: the vendor `libwayland-client` exports no
`wl_surface_commit` symbol (`PROBE surface_symbol=0`), so the observer hooks
`wl_proxy_marshal`, and the guest reports `marshal … interposed=1`, a real client's
`null-attach … attach=1` and `commit-after-null-attach … commit=1`, and finally
`verdict=observed commits=2 complete=1`. The chain is ours, not the vendor's: no
vehicle bus input is fabricated, and AppNavi's own hide path is still not exercised —
the process runs, but under this root it never attaches a surface.

## Decompilation and the published input audit

`tools/uk_fw/decompile.py` drives Ghidra headless (JDK 21 unpacked under
`~/.local/tools`, no root) and turns a retained listing address into C under ignored
`work/decompiled/<binary>/`. Two complete runs back the published notes: `ivi-shell.so`
(400 functions) and `AppLauncher` (1114 functions). The `ivi-shell` result is summarised
in [`vendor-userspace-260128/ivi-shell-input-audit.txt`](evidence/vendor-userspace-260128/ivi-shell-input-audit.txt):
no `wl_keyboard`, `wl_pointer`, `notify_key` or `notify_button` reference, with the
activation and input-panel family present. Its SHA-256 is in
[`evidence-manifest.json`](evidence-manifest.json), and `tests/test_vm_publication.py`
re-hashes it on every run.

## Local artifact boundary

The private `work/vm/` tree is about 1.6 TB and contains sparse VM disks,
extracted vendor userspace, firmware/map assets, logs, archived captures and
core dumps. These are not redistributed in Git. Full vendor disassembly
exports and generated binaries are also retained locally; the published
evidence uses bounded excerpts and SHA-256 identifiers. The two PNGs show
the authentic Home frame and the isolated AppNavi map widget seen in the VM.

No vehicle connection, update media, firmware flashing or vehicle actuation
is part of this public VM source snapshot.
