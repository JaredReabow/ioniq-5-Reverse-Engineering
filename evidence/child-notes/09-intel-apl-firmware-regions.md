# 09 — Intel Apollo Lake firmware/SPI regions (read-only acquisition)

**Platform (this unit).** Intel **Apollo Lake** (Broxton/BXT, Goldmont), Linux
**4.1.27** on eMMC. Kernel config fingerprints: `CONFIG_APL_SPI_BRD=y`,
`CONFIG_LGE_BRD=y`, i915 + `bxt_dmc/guc/huc` firmware, and an LGE board driver.
The vendor key manifest (`oemkm=<size>@<phys-addr>`) is *not* on the eMMC — it is
handed to the kernel as a physical address and copied out of a firmware-provided
DRAM region at boot (see `eu-keystore-manifest-root-of-trust.md`).

**Scope.** Read-only, bench-only acquisition and parsing guidance. No write /
flash / erase commands, no descriptor-lock bypass, no exploit code, no in-vehicle
contact. Everything below stops at *reading and interpreting* what is already on
the SPI NOR and in the boot log.

**Why SPI matters for the `oemkm` question.** The manifest's *runtime* location
is a reserved DRAM page populated by the boot loader. Its *source of record* is a
flash-resident artifact (BIOS/UEFI NVRAM, a dedicated OEM region, or CSME/PTT).
Reading the SPI NOR and the descriptor is the only way to see where that source
lives and whether it is write-protected.

---

## 1. Apollo Lake SPI layout and the Intel Flash Descriptor (IFD)

Apollo Lake firmware lives in a single shared SPI NOR that is also the CSME's
code store. Its layout is **self-describing**: the first 4 KiB is the Intel Flash
Descriptor (IFD), and the descriptor contains base/limit for every region. Never
assume a fixed map — read the descriptor first.

### 1.1 IFD anatomy (offset 0x000000, fixed 4 KiB)

| Field | Offset | Meaning |
|---|---|---|
| FLVALSIG | 0x000 | Signature `0x0FF0A55A` (bytes `5A A5 F0 0F` on disk). |
| FLMAP0 | 0x004 | `[7:0]` FCBA (component base), `[15:8]` NC (component count), `[23:16]` FRBA (region base), `[31:24]` NR (region count). |
| FLMAP1 | 0x008 | `[7:0]` FMBA (master base), `[15:8]` NM (master count), `[23:16]` FPSBA (PCH strap base), `[31:24]` strap length. |
| FLMAP2 | 0x00C | `[7:0]` FMSBA (master strap base), `[15:8]` strap length. |
| Component section | @ FCBA | FLCOMP (flash density, dual-output, read frequency), FLILL (invalid-instruction table), FLPB (partition boundary). |
| Region section | @ FRBA | FLREG0..FLREG7 — one `u32` per region: `[14:0]` base, `[29:15]` limit, in **4 KiB units**. |
| Master section | @ FMBA | FLMSTR1.. — read/write permission masks per region, per master. |
| VSCC table | @ FCBA | Vendor-specific component capabilities. |

Region 0 (Descriptor) is fixed at 4 KiB regardless of FLREG0. All other regions
are `size = (limit − base + 1) × 4 KiB`. `ifdtool -d` prints byte-exact offsets,
which is what you should record.

### 1.2 Standard regions (index, name, typical content)

| # | Region | Typical size (16 MiB chip) | Contents |
|---|---|---|---|
| 0 | Descriptor (FD) | 4 KiB fixed | IFD, masters, region map, VSCC. |
| 1 | BIOS | ~8 MiB (varies; often 0x1000 → ~0x7FFxxx) | UEFI firmware volumes (SEC/PEI/DXE), boot-policy, ACM/bootguard metadata, UEFI variables, OEM NVRAM. |
| 2 | ME / CSME | ~2–3 MiB near the top | CSME 11.x firmware: Flash Partition Table (`$FPT`), ME kernel, modules, MFS (FTPR/FTAR/NFTP), fTPM (PTT) data. |
| 3 | GbE | 8 KiB (often absent/present) | Gigabit MAC + config, if the board exposes GbE. |
| 4 | Platform Data | 8 KiB | OEM/board-specific data (straps, IDs, calibration). |
| 5 | EC | present on EC-carrying designs | Embedded Controller firmware (Chrome-EC-style designs); often empty on head units. |
| 6–7 | Reserved | — | Unused / second-die options. |

> **Caveat.** Head-unit boards vary. A 8 MiB vs 16 MiB vs 32 MiB chip changes
> absolute offsets; only the descriptor is authoritative. Confirm chip density
> from the FLCOMP field and from the physical part marking before trusting
> offsets.

### 1.3 Where the `oemkm` source most likely lives

The boot loader reads the key manifest from somewhere and copies it into reserved
DRAM, then appends `oemkm=<size>@<phys>`. Candidate sources, in rough order of
likelihood on an automotive LGE board:

1. **BIOS-region UEFI variables / authenticated variables** — a small blob in the
   BIOS region's variable store, read at boot and relocated to RAM.
2. **A dedicated BIOS-region OEM area** (a pad file in a firmware volume).
3. **Platform Data or EC region** — OEM straps/data region.
4. **CSME PTT/fTPM** — less likely for a plain kernel key manifest, but possible
   if ME hands it to the host during early boot.

None of these are on the eMMC, which matches the static finding that the packaged
command line and filesystem do not contain the manifest.

---

## 2. Reading the SPI NOR externally (bench)

The whole flash is a single SOIC-8 / WSON-8 SPI NOR, e.g. a Winbond W25Q128,
Macronix MX25L128, or GigaDevice GD25B/GD25Q part. This is the cleanest read-only
access: the SoC is not involved, so no OS cooperation is needed and host-side
locks are irrelevant.

### 2.1 Part and pinout

SOIC-8 (1.27 mm pitch) standard pinout — check the datasheet for your exact part:

| Pin | Name | Function |
|---|---|---|
| 1 | CS# | Chip select (active low) |
| 2 | DO / IO1 | Data out |
| 3 | WP# / IO2 | Write protect (high for normal read) |
| 4 | GND | Ground |
| 5 | DI / IO0 | Data in |
| 6 | CLK | Clock |
| 7 | HOLD# / IO3 | Hold (high for normal read) |
| 8 | VCC | Power |

WSON-8 is electrically identical but the pads are under the package (exposed pad
is usually VCC or GND — verify). On the bench this usually means a **test clip**
(Pomona 5250/5252 style for SOIC-8, or a WSON-8 clip) rather than a socket,
because the chip is soldered.

### 2.2 Voltage: 1.8 V vs 3.3 V — check before you clip

Apollo Lake reference designs overwhelmingly use **1.8 V** SPI NOR. A 3.3 V
programmer will **destroy a 1.8 V part** or get corrupted reads. Procedure:

- Read the part marking, look up the datasheet, and confirm VCC range.
- Use a programmer with a selectable I/O rail (FT2232H/FT232H breakout with a
  1.8 V LDO, a 1.8 V-adapted CH341A, or a dedicated 1.8 V SPI adapter).
- Power the chip from **the target's own rail if the board is cold-off but the
  programmer can be level-shifted**, or from the programmer's regulated 1.8 V —
  never a hard 3.3 V rail into a 1.8 V part.

### 2.3 Contention with the SoC (the real risk in-circuit)

While the board is powered, the Apollo Lake SPI controller (LPSS SPI) can drive
CS/CLK/DI and will fight the clip. Rule set for a clean read:

1. **Power the board down** (remove battery / bench supply), and let bulk caps
   discharge.
2. Prefer **holding the SoC in reset** (assert PLTRST# / reset strap) if the
   board is powered, so the SPI controller stays idle.
3. Do **not** back-power the whole board through the clip's VCC pin; feed only
   the flash chip. If the programmer's VCC leaks into the 3.3 V rail, use a
   one-way power scheme or lift the VCC connection and power VCC locally.
4. Keep WP# and HOLD# **high** for reads (they must not float).
5. Read the chip **twice** and hash both — a glitching/contended read often
   returns plausible-but-wrong bytes.

---

## 3. How the regions are protected (and why reads still work)

All Intel protection mechanisms below are **enforced by the SoC's SPI controller
and by the CSME**, not by the flash chip. They gate *writes/erases* (and in a few
cases host reads) through the in-circuit host interface. They do **not** stop an
external programmer from reading the NOR — which is the entire point of reading
externally.

| Mechanism | Location | What it does | Effect on read vs write |
|---|---|---|---|
| FLMSTRn master masks | Descriptor (FMBA) | Per-region read/write permission per master (CPU/BIOS, ME, GbE, EC). | Can mark a region **read-disabled** for the host CPU; irrelevant to external read. |
| FLOCKDN (Flash Lock-Down) | HSFS register, bit 15 | Once set, freezes descriptor master access, VSCC, and straps until reset. | Locks descriptor *settings*; does not hide flash contents from external read. |
| PRR (Protected Range Registers) PR0/PR1 | SPI controller MMIO | Base/limit range; WPE = write-protect, RPE = read-protect that range. | WPE blocks host write/erase. **RPE exists but is rarely set** (it would break host reads); external read ignores both. |
| BIOS_CNTL (BIOSWE / BLE / SMM_BWP) | PCI config | Host write gating for the BIOS region; SMM_BWP restricts writes to SMM only. | Write-side only. Read is unaffected. |
| BIOS_WP# / Boot-BIOS strap / Top-swap | board strap + descriptor | Hardware write-protect strap and boot-vector control. | Write-side / boot-selection only. |
| CSME region signing/encryption | ME internals | ME region images are RSA-signed (and partly encrypted) with ME-fused keys. | The region bytes are still readable; contents are authenticated, not readable-blocked. |

**Bottom line for this task:** descriptor locks and PRR/FLOCKDN make *in-circuit
writes* hard, but every one of them is bypassed by a powered-off external read.
There is no need to touch any of them — and per scope we do not.

---

## 4. Intel CSME: what is inside, what is readable

The ME region (region #2) is a plain SPI NOR region. Its bytes are freely
readable externally; what is *inside* is a signed, partly encrypted CSME 11.x
image.

- **Flash Partition Table (`$FPT`)** at the start of the ME region — lists every
  ME partition and its offset/version.
- **Partitions:** BUP (bring-up), ME kernel, loadable modules, MFS (ME File
  System) containing FTPR (code), FTAR (data), NFTP (non-critical), plus fTPM
  (PTT) state and OEM-mappable areas.
- **What is readable:** the whole region and its partition structure; with
  `MEAnalyzer`/`me_unpack` you can enumerate partitions, versions, and extract
  MFS entries. UEFI variables and any OEM NVRAM in the *BIOS* region are also
  readable.
- **What is authenticated:** every ME module is RSA-signed with keys fused into
  the ME ROM; MFS regions are integrity-checked. A tampered ME region fails boot
  and/or sends the ME to recovery.
- **Why modifying it is out of scope:** the ME region is write-locked in the
  descriptor, its images are signed/encrypted against ME fuses, and an invalid
  ME image bricks or recovery-loops the platform. Nothing in the read path
  requires touching it, and this research is read-only.

CSME is also where Intel **PTT (firmware TPM)** lives, so if any TPM-backed
key material is in play, it is reachable only through the ME's own interfaces —
you can read the region bytes but not the fTPM's protected state.

---

## 5. Read-only toolchain (macOS / Linux)

Install on macOS via Homebrew, or use the same tools on Linux:

```sh
# macOS
brew install flashrom binwalk          # ifdtool/uefiextract/MEAnalyzer: see below
# Linux (Debian/Ubuntu)
sudo apt install flashrom binwalk
```

### 5.1 flashrom — chip dump (read-only, external)

List supported programmers (identifies what your adapter is called):

```sh
flashrom -L
```

Dump the chip (read-only `-r`). Pick the programmer matching your adapter:

```sh
# CH341A (1.8 V-adapted)
flashrom -p ch341a_spi -r flash.bin

# FTDI FT2232H/FT232H (selectable I/O voltage)
flashrom -p ft2232_spi:type=2232H,divisor=4 -r flash.bin

# Google "Raiden" / serprog / dediprog style adapters
flashrom -p raiden_debug_spi:target=AP -r flash.bin
```

Read twice and compare — this is the core verification step:

```sh
flashrom -p ch341a_spi -r flash_1.bin
flashrom -p ch341a_spi -r flash_2.bin
shasum -a 256 flash_1.bin flash_2.bin
cmp flash_1.bin flash_2.bin && echo "dumps identical"
```

Check the dump is sane before parsing:

```sh
# descriptor signature 0x0FF0A55A -> bytes 5A A5 F0 0F at offset 0
xxd -l 16 flash.bin
shasum -a 256 flash.bin > flash.bin.sha256   # record the hash
```

> In-circuit read via the running SoC is possible with `flashrom -p internal`
> (or `chipsec_util spi read`) but requires booting Linux on the unit and
> honouring the host SPI controller — and the ME region may be read-masked. The
> external clip is preferred and is the only method that needs no OS on the
> target.

### 5.2 ifdtool — decode descriptor and extract regions

`ifdtool` ships with coreboot (build it there), or install a packaged copy:

```sh
# from coreboot (read-only, no target build needed):
#   git clone https://review.coreboot.org/coreboot && cd coreboot/util/ifdtool && make
ifdtool -d flash.bin > descriptor.txt      # human-readable region/master map
ifdtool -x flash.bin                        # extracts one file per region
```

Extraction produces `flashregion_0_flashdescriptor.bin`, `_1_bios.bin`,
`_2_me.bin`, `_3_gbe.bin`, `_4_platform_data.bin`, `_5_ec.bin` as applicable.
Record `descriptor.txt` — it is your ground truth for offsets and master masks.

### 5.3 uefiextract — BIOS region / UEFI variables

```sh
# UEFITool (GUI) or its CLI "UEFIExtract" (same source, built from the
# longsoft/UEFITool tree) — parses firmware volumes inside region #1.
UEFIExtract flashregion_1_bios.bin all
# -> emits a directory tree of FVs, files, and sections, including NVRAM
#    variable stores (look for NVRAM/varstore files under the output tree).
```

To enumerate the UEFI variable store specifically, also consider
`uefi-firmware-parser` (`pip install uefi_firmware`) which can dump variable
entries from the BIOS region in read-only mode.

### 5.4 binwalk — signature scan

```sh
binwalk flash.bin                       # overview of embedded signatures
binwalk -e flashregion_1_bios.bin       # extract embedded items into _*.extracted/
binwalk -Me flash.bin -C extracted/     # recursive scan (slow on 16 MiB+)
```

### 5.5 MEAnalyzer — ME region (read-only)

```sh
# platomav/MEAnalyzer — parses the $FPT and ME partitions without modifying anything
python me_analyzer.py flash.bin          # run against the full dump; it locates the ME region
python me_analyzer.py flashregion_2_me.bin
```

This gives the CSME version, partition list, and MFS layout — enough to confirm
what is in region #2 without writing to it.

### 5.6 Verify a dump end-to-end

1. Two independent reads hash-equal (`cmp` passes).
2. Dump size == chip density (FLCOMP + part marking agree).
3. Descriptor signature `5A A5 F0 0F` at offset 0; `ifdtool -d` decodes without
   errors and region offsets are monotonic/non-overlapping.
4. `binwalk` finds a `$FPT` at the ME region start and UEFI volumes in the BIOS
   region.
5. Save `shasum -a 256` for every extracted region alongside the raw dump.

---

## 6. Risks (read-only work)

- **Voltage damage.** 1.8 V part + 3.3 V programmer = destroyed chip / bogus
  reads. Confirm VCC range from the marking *before* powering anything.
- **Bus contention / silent corruption.** A powered or residual-powered board
  whose SoC drives the SPI lines can produce garbage that still *looks* valid.
  Mitigate: power off, hold reset, read twice, hash-compare.
- **Back-powering the board.** Driving VCC through the clip can energise the 3.3 V
  rail and make the SoC partially live. Feed only the flash chip.
- **Mis-read descriptor → wrong region boundaries.** Region base/limit are 4 KiB
  units and descriptor-relative; misinterpreting them silently corrupts every
  carve-out. Always trust `ifdtool -d`, not memory.
- **ME region is signed, not freely editable.** Treating the ME region as a
  "firmware blob to fix" leads to brick/recovery; reading it is safe, writing it
  is out of scope.
- **Warranty / board damage.** Clips on a soldered WSON can lift pads; document
  the board before and after. ESD precautions apply.

---

## 7. Evidence to capture

For each bench unit, record:

1. **Physical:** flash part marking (manufacturer + density), package (SOIC-8 vs
   WSON-8), VCC voltage, board/PCB photos, clip placement photo.
2. **Descriptor:** `ifdtool -d flash.bin` output (region base/limit, master
   masks, FLCOMP density) saved verbatim.
3. **Raw dump:** `flash.bin` + `shasum -a 256`, dump size, and both `cmp`-equal
   reads.
4. **Region extracts:** `flashregion_*_*.bin` + per-region SHA-256.
5. **BIOS region:** `UEFIExtract` tree, especially any NVRAM/varstore files;
   enumerate UEFI variable names/guids (candidate `oemkm` source).
6. **ME region:** `MEAnalyzer` report (CSME version, `$FPT` partitions, MFS
   layout) — read-only.
7. **Boot-log cross-check:** capture the bootloader/kernel log line for the
   `oemkm=<size>@<phys-addr>` parameter (serial console or `dmesg`/`/proc/cmdline`)
   and `cat /proc/iomem` reserved ranges, to correlate the runtime manifest
   address against the flash-resident source found in steps 5–6.
8. **Provenance:** programmer model + voltage setting, tool versions
   (`flashrom --version`, `ifdtool --version`, `MEAnalyzer` version), date, and
   operator, so the dump is reproducible and attributable.
