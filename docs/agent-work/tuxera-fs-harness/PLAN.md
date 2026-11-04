# Tuxera filesystem VM probe — phase plan

## Objective

Create a deterministic, project-local harness that attaches an operator-supplied NTFS or exFAT raw image to the existing offline recovered-kernel VM and exercises the exact recovered Tuxera `tntfs` or `texfat` module read-only. The harness is for bounded parser validation and crash triage; it must never mount an image on the macOS host or write the input image.

## Security and operating contract

- QEMU remains offline (`-nic none`, inherited from `vm_boot.py`).
- The raw test image must be a regular, project-local, non-symlink file.
- QEMU must open it read-only and guest mount options must include `ro,nodev,nosuid,noexec`.
- The canonical VM rootfs remains snapshot-backed and unmodified.
- Accept only explicit filesystem choices `tntfs` and `texfat`.
- Do not probe internal/eMMC devices; only the newly attached QEMU USB-storage disk is eligible.
- Do not generate payloads, shellcode, device nodes, or persistence mechanisms.
- Preserve serial/result evidence under the existing `work/vm/.../runs/` convention and emit a concise machine-readable classification.

## Phase 1 — read-only attach and classification harness

Worker scope:

- `tools/uk_fw/tuxera_fs_probe.py` (new)
- `tests/test_tuxera_fs_probe.py` (new)
- optionally a concise usage section in `evidence/usb-root-test-plan.md`
- task report at `docs/agent-work/tuxera-fs-harness/WORKER-REPORT.md`

Required behavior:

1. Validate the workspace through existing `vm_boot` routines and validate the image boundary before QEMU execution.
2. Build QEMU extra arguments for a project-local raw image using a unique drive/controller/device ID and `readonly=on`.
3. Run a fixed guest script which waits for only the attached SCSI/USB block device, loads the chosen authentic module, mounts read-only with `nodev,nosuid,noexec`, performs bounded metadata enumeration, unmounts, and prints stable markers.
4. Classify retained serial/result output as at least: clean mount, clean rejection, kernel fault, timeout/harness error. Kernel-fault markers must include common oops/panic/BUG/general-protection/KASAN strings without claiming exploitability.
5. Emit JSON containing input SHA-256, size, selected filesystem, VM run directory, classification, and salient marker lines.
6. Refuse newline/comma/path escapes that could corrupt QEMU argv, input outside the repository, symlinks, directories, oversized/undersized images, and an image that aliases `rootfs.img`.
7. Unit tests must prove read-only/no-network argv construction, path rejection, stable classification, and no mutation of fixture bytes.

Verification:

```sh
python3 -m pytest -q tests/test_tuxera_fs_probe.py tests/test_vm_boot.py
python3 -m py_compile tools/uk_fw/tuxera_fs_probe.py
git diff --check
```

## Non-goals

- No assertion that a crash is code execution or root access.
- No host filesystem mounts, privileged host operations, package installation, or network-enabled VM.
- No automatic broad mutation/fuzz campaign in phase 1.
- No physical-unit interaction.

## Phase 2 — later, after acceptance

Acquire or generate known-good images project-locally, run clean baseline controls, then add deterministic mutation campaigns and crash deduplication. Exact module behavior and evidence from phase 1 must be accepted first.
