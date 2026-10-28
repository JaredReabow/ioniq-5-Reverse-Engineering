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

## Local artifact boundary

The private `work/vm/` tree is about 1.6 TB and contains sparse VM disks,
extracted vendor userspace, firmware/map assets, logs, archived captures and
core dumps. These are not redistributed in Git. Full vendor disassembly
exports and generated binaries are also retained locally; the published
evidence uses bounded excerpts and SHA-256 identifiers. The two PNGs show
the authentic Home frame and the isolated AppNavi map widget seen in the VM.

No vehicle connection, update media, firmware flashing or vehicle actuation
is part of this public VM source snapshot.
