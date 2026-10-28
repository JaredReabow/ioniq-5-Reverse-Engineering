# Bench-unit hardware and root path

Status: research plan for the owner's Gen5W AVN **removed from the vehicle** and
operated on a bench. Scope is a single owned unit. No vehicle is connected and
no vehicle-side action is in scope.

This document records the root-access ladder for a bench unit, the interface
survey that decides which rung is available, and the evidence each rung
produces. It is a plan, not a procedure, and it deliberately front-loads
read-only acquisition.

## Why the ladder looks like this

The exact-build package (`NE_E.EUR.S5W_L.001.001.260128`) is x86-64 Linux
`4.1.27-abl` with SMACK, ext4 root on `mmcblk0p3`, and an OEM signature/CRC
trust chain. On a bench unit the fastest route to a shell is almost always
physical, because:

- the boot loader and kernel command line are usually reachable in-circuit;
- the root filesystem is directly readable and writable when the storage is
  removed or dumped;
- a software exploit still has to clear asymmetric signature verification,
  which hardware access simply bypasses for research purposes.

Software exploits (CVE-2023-26243…246, `navi_extended`) remain a fallback, not
the default, because they were demonstrated on `211214` and their state on
`260128` is unknown.

## Root-access ladder

| Rung | Mechanism | Yields | Precondition | Evidence to capture |
|---|---|---|---|---|
| 1 | UART / serial console | Boot log, shell, or U-Boot prompt | Debug header or unpopulated pads identified | Pinout, baud, boot log |
| 2 | Bootloader interrupt | Editable `bootargs` → `init=/bin/sh`, `single`, rw remount | Unlocked U-Boot, interrutable autoboot | Env dump, `printenv`, bootargs |
| 3 | Storage dump / offline edit | Full rootfs; edit `/etc/shadow`, add unit, inject service | Storage readable (in-circuit, chip-off, or vendor tool) | Partition table, image hash, diff |
| 4 | Software exploit | Shell via update/AppNavi surface | Reachable vulnerable component on this build | Exact version, trigger, code evidence |

Rungs 1–3 are read-first and reversible if a full image is taken **before** any
write. Rung 4 should only be attempted after 1–3 are shown to be unavailable.

## Interface survey checklist

Record these before applying power a second time:

1. **Board identity** — silkscreen part numbers, PCB revision, connector
   labels, and whether the unit is main+display split or single-board.
2. **Debug headers** — 3/4-pin UART pads (Tx/Rx/GND, sometimes Vcc), JTAG
   (TCK/TMS/TDI/TDO), and any unpopulated 0-ohm/DNP resistor links.
3. **Service ports** — USB (host or device), SD/microSD, Ethernet, and any
   pogo-pad array.
4. **Storage** — eMMC package markings and whether it is socketed; SPI NOR
   near the SoC or EC.
5. **Boot mode straps** — resistors that select USB/DFU/recovery vs eMMC boot.
6. **Power** — required rails and current; do not back-feed a rail that the
   board also drives.
7. **Console behaviour** — what appears on UART at power-on, and whether
   autoboot can be interrupted.

## Evidence a rung must produce

A rung is not "achieved" until it produces reproducible evidence:

- **Full pre-write image** of every readable partition, with SHA-256 per
  partition and a sorted-tree digest, matching the project's existing style.
- **Boot log** bound to the board and firmware version.
- **Version screen** from the unit itself, to confirm the installed build
  before any package analysis is applied to it.
- **Recovery proof** for any write: a documented way back to the pre-write
  image (reflash route, recovery partition, or bootloader restore).

## Recovery requirements before the first write

The project's Gate 4 applies at bench scale:

1. **Readable and restorable storage** — the full image exists and the write
   path to the storage is known and tested on a scratch region.
2. **Known boot chain** — bootloader verification, rollback counters, and
   recovery partition behaviour are understood, not assumed.
3. **Restore rehearsal** — the restore path has been exercised, or the storage
   is removable and can be reprogrammed externally.
4. **No vehicle coupling** — the unit is confirmed off the vehicle network for
   the entire procedure.

Until all four hold, writes are limited to removable or externally
reprogrammable storage.

## Tooling

| Tool | Role |
|---|---|
| `tools/uk_fw/inspect_ipk_kernel.py` | Kernel/IKCONFIG extraction from `iasImage*_sub` |
| `tools/uk_fw/kallsyms_extract.py` | kallsyms recovery from `vmlinux` |
| `tools/uk_fw/elf_reader.py` | Read-only ELF64 section parsing |
| `tools/uk_fw/compare_eu_aus.py` | Byte-level package comparison |
| `tools/uk_fw/dump_survey.py` | **New**: read-only survey of a rootfs dump — accounts, setuid, capabilities, SMACK, systemd, boot cmdline, debug surfaces, persistence, world-writable paths |

`dump_survey.py` is the first thing to run on a rung-3 dump. It produces both a
human summary and `--json` for the ledger.

## Open questions

- Installed build on the bench unit: is it `260128` or another release?
- Does the boot loader verify the kernel/rootfs independently of the kernel
  update verifier?
- Is the storage removable, or does it require in-circuit access?
- Is SMACK policy compiled in, loaded from `/sys/fs/smackfs`, or shipped in
  `/etc/smack`?
- Does the unit expose a UART console before or after U-Boot?
