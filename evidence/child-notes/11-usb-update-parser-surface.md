# USB Update Parser Surface — exFAT / FAT / tar / gzip / XML

> Scope: automotive head unit, Linux `4.1.27-abl` (x86-64), ~2018-era userspace.
> Update path: `AppUpgrade` reads a directory tree from a removable USB stick,
> checksums files, decrypts and extracts `tar.gz`/`tar` archives, and copies them
> to a partition. Kernel config has `CONFIG_VFAT_FS=m` and `CONFIG_MSDOS_FS=m` but
> **no `exfat` driver and no `fuse`** (`evidence/eu-kernel-symbol-recovery-and-trust-chain.md`
> §4). The USB stick is documented as exFAT-formatted (`evidence/passive-runtime-and-hardware.md`).
>
> This note is offline analysis and harness design only. No exploit code, no
> malicious images, no device contact. It does not attempt decryption and does not
> assert that any parser is reachable; it maps *where* attacker-controlled bytes can
> enter and *which* parser classes consume them.

Companion documents: `evidence/official-package-static.md` (opaque envelopes),
`evidence/eu-custom-firmware-feasibility.md` (AppUpgrade/`update.tar.gz` layout),
`evidence/known-exploits-and-cve-survey.md` and
`evidence/child-notes/01-component-cve-corpus.md` (CVE corpus).

---

## 0. The one distinction that drives everything

The update path has **two different trust layers**, and they must not be conflated:

| Layer | When consumed | Attacker control without any signature bypass? |
|---|---|---|
| **Filesystem metadata** — boot sector, FAT, directory entries, cluster chains, filenames | Before anything is checksummed or decrypted; the filesystem must be walked to *find* the files | **Yes.** A hostile stick is a hostile filesystem image, full stop. |
| **File payloads** — tar, gzip, XML manifest | After decryption (and, in the intended flow, after a signature/version gate) | Only if the signature/version gate is bypassed (cf. CVE-2023-26244/26245/26246) or the plaintext is otherwise attacker-controlled. |

Consequence: the **exFAT/FAT parser is the unconditional entry point**. It runs on
raw attacker bytes with no cryptographic gate in front of it. tar/gzip/XML are
one hop deeper, behind the decryptor and signature check — still worth mapping,
because those checks are themselves the historically broken piece, but they are
not the first code that touches hostile input.

---

## 1. How can exFAT be mounted with no `exfat` driver and no `fuse`?

The premise (exFAT stick + a kernel without exFAT/FUSE) is not a contradiction;
it is a *question about where the exFAT parser lives*. Enumerated mechanisms,
most-plausible first:

### M1 — Vendor userspace exFAT library + mount helper / daemon (highest prior)

An `exfat-fuse`-style codebase (Samsung's `exfat` / `relan/exfat` "libexfat") is
shipped as a *library*, not as a FUSE filesystem. A vendor `usb`/`media` daemon
(or a `mount.exfat` helper invoked from an fstab/udev rule) opens the block device
(`/dev/sdX`), walks the exFAT structures with libexfat, and either

- (a) copies the update tree to an internal ext4/tmpfs mount, or
- (b) presents a synthetic view to `AppUpgrade` through an IPC.

No FUSE kernel support is needed — libexfat can read the block device directly and
never touches `/dev/fuse`. This is the standard 2018 embedded IVI answer because
the mainline kernel only gained a real exFAT driver in 5.4/5.7, and FUSE is
frequently compiled out on head units for attack-surface reasons.

**Attack surface:** userspace libexfat (ring-3, usually running as root), plus the
helper daemon's filename/copy logic. Highly fuzzable.

### M2 — Out-of-tree Samsung exfat kernel module (`.ko`)

Samsung maintained a standalone `exfat`/`exfat_core` kernel driver for years
(later reworked into the mainline `exfat` driver in 5.4→5.7). A 2018 OEM BSP
could carry it as a module even if it is not in the shipped `.config` for the
`iasImage_*_sub` kernel that was extracted.

**Weighing against:** the extracted config explicitly has no `exfat`. Either the
extracted kernel is not the kernel that mounts USB media (boot vs. runtime split,
or the module is built against an OEM tree whose config was not captured), or M1
is true. This mechanism is **possible but currently un-evidenced**; treat it as a
ring-0 escalation-of-impact path to confirm only on the bench.

### M3 — `AppUpgrade` reads the block device directly

The update tool itself opens `/dev/sdX` and parses exFAT (possibly via the same
libexfat from M1 statically linked in). This collapses "mount" and "walk the
directory tree" into one binary. The task description ("reads a directory tree,
checksums files, …") is compatible with this: `AppUpgrade` may never rely on VFS
for the *source* medium at all.

**Attack surface:** the same libexfat parser, but embedded in the highest-value
process (the one that also decrypts and installs).

### M4 — FUSE-based mount (ruled out by config, note anyway)

`exfat-fuse` mounted via `/dev/fuse`. Requires `CONFIG_FUSE`; the config has none.
Rule out for this kernel unless a second kernel/initramfs with FUSE exists. Do not
spend harness time here until the bench shows `/dev/fuse` or a `fuseblk` mount.

### M5 — The device never parses exFAT; "exFAT" is a PC-side constraint

The manual's "exFAT USB" requirement may describe the *Hyundai Navigation Updater
(PC)* write step, not the head-unit read step. The unit may actually accept FAT32
(or exFAT is only one option alongside FAT16/32 and NTFS — the manual lists all
three). In that case the real filesystem path is the **kernel `vfat`/`msdos`
module** (present as `m`), not exFAT at all.

**Attack surface:** kernel `vfat`/`msdos` (ring-0). This path must be in the
harness regardless, because `CONFIG_VFAT_FS=m` proves FAT12/16/32 *is* available.

### M6 — NTFS path (adjacent, note only)

The AU manual also lists NTFS. If an `ntfs-3g` or similar userspace stack is
present, it is a sibling attack surface. Out of scope for this note but flag for
the bench media survey.

### Assessment

| Mech | Where parser runs | Ring | Evidence today | Priority |
|---|---|---|---|---|
| M1 userspace libexfat + helper | media daemon / helper | 3 (root) | Consistent with no-fuse + 2018 era | **Primary** |
| M3 AppUpgrade embeds parser | AppUpgrade | 3 (root) | Consistent with task description | **Primary** |
| M2 out-of-tree exfat `.ko` | kernel | 0 | Contradicts extracted config | Secondary (confirm on bench) |
| M5 kernel vfat/msdos | kernel | 0 | `CONFIG_VFAT_FS=m` proven | **Primary** (FAT32 path) |
| M4 FUSE exfat | FUSE daemon | 3 | Ruled out by config | Skip until bench shows fuse |

---

## 2. Parser-by-parser risk table (filesystem layer)

Attacker-controlled inputs are the raw on-disk structures. "Classic classes" are
named per input; all of them are the same handful that historically break FAT
parsers: **integer overflow in sector/cluster arithmetic, missing bounds checks →
OOB read/write, unbounded name length, missing cluster-chain loop detection, and
UTF-16 mishandling.**

### 2.1 exFAT on-disk structures (M1/M2/M3)

| Parser / input | Attacker-controlled field | Classic class | Notes |
|---|---|---|---|
| Boot sector / VBR (Main + Backup) | `BPB_FATOffset`, `BPB_FATLength`, `BPB_ClusterHeapOffset`, `BPB_ClusterCount`, `BPB_SectorsPerClusterShift`, `BPB_RootDirectoryCluster`, volume length, sector size (`2^n`, n=9..12) | Integer overflow on `offset + length` and `cluster << shift`; OOB read past volume when offsets/sizes are not clamped; shift out-of-range used as array index | Backup boot region at sector 12 is trusted on mount failure — both must validate identically |
| FAT table | cluster entry values; `0xFFFFFFF7` (bad), `0xFFFFFFFF` (EOC), free `0x00000000` | Cluster-chain **loop** (A→B→A) with no visited-set → infinite walk / DoS; entry index ≥ ClusterCount → OOB read into FAT heap | exFAT FAT walk is the top DoS primitive; loop detection is often missing |
| Directory entry set | `EntryType` (bit 7 = "in use"), `SecondaryCount`, `FileAttributes`, name length byte, file size (64-bit) | `SecondaryCount` not validated → OOB read of next entries; name length vs. UTF-16 field length mismatch; 64-bit size truncation to 32-bit `size_t` on a 32-bit `stat` path | exFAT packs 32-byte primary + secondary entries; counts are per-set and frequently unchecked |
| File name | UTF-16/LE name, 15 chars per entry | Unpaired surrogates, overlong/overread when UTF-16→UTF-8 conversion allocates from the *byte* count and writes a longer UTF-8 sequence; missing NUL termination | The conversion is usually hand-rolled in libexfat; prime heap-overflow candidate |
| Upcase / checksum | `Checksum` (set checksum), `UpcaseTable` | OOB read if upcase table length is trusted and used to index a fixed 128-char table | Low severity but reachable |
| Allocation bitmap | bitmap size, bits referenced by cluster | OOB read if `cluster / 8` exceeds the cached bitmap | Second cluster math site after the FAT walk |

### 2.2 FAT12/16/32 + VFAT long names (kernel `vfat`/`msdos`, M5)

| Parser / input | Attacker-controlled field | Classic class | Notes |
|---|---|---|---|
| BPB (FAT12/16/32) | `BPB_BytsPerSec`, `BPB_SecPerClus`, `BPB_RootEntCnt`, `BPB_FATSz16/32`, `BPB_TotSec`, reserved sectors, media descriptor | Integer overflow in FAT size / cluster-count / sector arithmetic; division by zero when `SecPerClus`=0; OOB read of FAT when cluster numbers exceed computed FAT size | Classic; kernel has hardened much of this, but 4.1-era `vfat` still carries the older checks |
| FAT chain walk | cluster entries, `0xFFF8..0xFFFF` EOC | Loop detection — kernel `fat_bmap`/`fat_follow` historically had `max_fat_loops` but the logic changed across versions | 4.1 is old enough that some loop guards post-date it |
| 8.3 + LFN directory entries | 32-byte entries; LFN `0x40..0x5F` ordinal flags, `0x0F` attr | Unbounded accumulated name length across LFN slots (no cap before concatenation); orphaned LFN slots; UTF-16→UTF-8 conversion overflow; entry order/checksum mismatch | `vfat` name handling is the most-CVE'd area of this layer historically |
| Filename encoding | UTF-16 (VFAT) / codepage (msdos) | Overlong UTF-8 output vs. allocated buffer; codepage table OOB index on high bytes | Only relevant if the OEM enables UTF-8/codepage mount options |

### 2.3 Shared failure classes worth naming explicitly

1. **Cluster chain loops** — the single most reliable DoS on both exFAT and FAT;
   attacker points cluster N back to an earlier cluster and the parser never
   terminates or exhausts memory caching the chain.
2. **Integer overflow in `cluster * bytes_per_cluster`** — on 32-bit code paths
   (`off_t`/`size_t` truncation) a crafted 64-bit size in the exFAT directory
   entry wraps, yielding a short buffer for a long copy.
3. **Unbounded name length** — LFN slots and exFAT secondary name entries both
   allow a name far longer than any consumer's buffer; concatenation without a
   cap is the heap overflow.
4. **UTF-16 handling** — unpaired surrogates and the UTF-16→UTF-8 expansion factor
   are the most common *memory-corruption* (not just DoS) bug in embedded FAT
   stacks.

---

## 3. Archive parsing (tar and gzip)

Reached only after decryption. But note: if the signature/version gate is bypassed
(CVE-2023-26244/26245/26246), or if an engineering/dealer sideload path skips
signature verification, the attacker fully controls these bytes. The observed
packages name `update.tar.gz`, `new_gui.tar.gz`, `mango-rootfs.tar.gz`,
`appnavi.tar`, `mango-vr.tar.gz`, `.whatsnew.tar.gz`
(`evidence/eu-custom-firmware-feasibility.md`, `evidence/official-package-static.md`).

### 3.1 tar

| Input | Field | Classic class |
|---|---|---|
| Header | `name[100]`, `prefix[155]` (ustar), `size[12]` octal or base-256, `typeflag`, `magic` | Missing NUL in name/prefix → OOB read into adjacent header fields; base-256 size (`0x80` top bit) → signed/unsigned `off_t` overflow; `size` used to allocate without sign/overflow check |
| GNU long name | `typeflag='L'`, name field carries a *decimal length* | Trusted length → `malloc(len)` / `read(len)` with no sanity cap → heap overflow / OOM |
| GNU long link | `typeflag='K'` | Same as long name |
| PAX extended header | `typeflag='x'`/`'g'`, header holds `<len> <key>=<value>\n` records | Record length parsed from attacker text and used to advance the pointer → OOB read/write; negative/overflowing record length; `size`, `path`, `linkpath` overrides |
| Sparse files (GNU) | `typeflag='S'`, sparse map in data; old GNU `'D'` | Sparse map entries (`offset,length`) not validated → OOB write / huge allocation / file-hole confusion |
| Hardlink / symlink | `typeflag='1'`/`'2'`, `linkname` | Symlink *then* write-through-link (tar follows existing symlink in later entries); hardlink to a path outside the tree; link chains / self-links |
| Device / fifo | `typeflag='3','4','6'` | Only if extraction runs as root: creates device nodes (post-root persistence primitive) |
| **Path traversal** | `name`/`prefix` containing `../`, absolute `/`, Windows drive, leading `./../` | Extraction outside the target directory → arbitrary file write within the update partition or rootfs |

### 3.2 gzip / deflate

| Input | Field | Classic class |
|---|---|---|
| gzip member header | `FNAME`, `FCOMMENT`, `FHCRC`, extra field | `FNAME`/`FCOMMENT` are NUL-terminated but a hostile member omits the NUL → read past the member; extra-field length trusted |
| Multi-member / concatenated | member boundaries | Parser must re-sync per member; a truncated member with a valid-looking ISIZE/CRC can pass a naive size check |
| Deflate stream | Huffman tables, distances, lengths | zlib inflate bugs: CVE-2016-9840/9841/9842/9843, CVE-2022-37434, CVE-2018-25032 (see §6) |
| Decompression bomb | high compression ratio | Disk exhaustion when the tool streams to a partition without a size cap — matters because "copies to a partition" implies unbounded writes |
| CRC/ISIZE | trailer | Mismatch path (reject vs. continue) can leak a partial file into the tree before validation |

### 3.3 Why this layer is dangerous even "just extracting"

`AppUpgrade` "decrypts and extracts … and copies them to a partition." Extraction
is the moment attacker-controlled *paths and file contents* are written into the
filesystem that will later be executed/booted. tar's `../`, absolute paths, and
symlink-then-write are **arbitrary-write primitives**, not just parser crashes.

---

## 4. Manifest parsing (XML)

The manifest is `.lge.upgrade.xml`. In the observed package it is an **opaque,
encrypted envelope** (`evidence/official-package-static.md` §"Opaque envelopes" —
no readable XML tag, ~8 bits/byte entropy), so the XML parser consumes plaintext
only after decryption. A "small upgrade descriptor" maps directly to the known
Gen5W manifest conventions (path records, sizes, CRC-32/MD5, version
`NE_E.EUR.S5W_L.001.001.260128`).

### Risks of a naive XML parser on embedded Linux

| Risk | Mechanism | Consequence |
|---|---|---|
| Entity expansion ("billion laughs") | Nested internal entities (`<!ENTITY a "…">` ×N) | Exponential memory/time → DoS; the classic embedded XML kill |
| External entity (XXE) | `<!ENTITY x SYSTEM "file:///…">`, parameter entities, DTD fetch | Local file read (e.g. `/etc/keystore*`, device creds), SSRF, DoS via slow DTD fetch |
| DTD processing | Document/parameter entity substitution at all | Enables both of the above; must be disabled or the parser is unsafe |
| Encoding confusion | `<?xml encoding="UTF-16/UTF-32/UCS-4">`, overlong UTF-8, UTF-7 | Parser/signature mismatch, OOB reads in charset conversion |
| Deep nesting | Many nested elements | Stack overflow in recursive DOM parsers |
| Large attribute values | Unbounded attr length | Heap exhaustion / OOB in string handling |

### Which parser is "the naive one"?

The plausible candidates for a 2018 embedded XML consumer, in order of likelihood:

1. **Hand-rolled / `sscanf`-style parser** — the manifest is small and the vendor
   may parse it with ad-hoc string routines rather than a real XML library. This
   is *not safer*: no entity handling means no XXE, but no length checks means
   classic C bugs on hostile element lengths.
2. **libxml2** — if present, its pre-2.9.4/2.9.5 entity and DTD behavior is the
   dominant risk (see §6).
3. **expat** — streaming parser; vulnerable versions mishandle entities and have
   integer-overflow/OOB issues.
4. **TinyXML / TinyXML2** — no DTD/external-entity support (reduces XXE), but has
   its own infinite-loop / OOB history.

The decisive question for the bench is **"does the manifest parser expand
entities or process a DTD?"** — that one boolean determines the XXE/billion-laughs
exposure.

---

## 5. Offline harness design (macOS, no device)

Goal: run the *actual* parser binaries/libraries (once recovered from the device)
against synthetic, fully-controlled inputs, with sanitizers, on the Mac. Until
those binaries are available, build a **reference-generator + reference-parser**
rig so the methodology and corpus are ready the moment the target is dumped.

### 5.1 Layers and targets

| Layer | Target under test (TUT) | Synthetic input generator |
|---|---|---|
| exFAT | libexfat / embedded parser / `.ko` (via a thin QEMU/`syzkaller`-style wrapper if kernel) | Pure-Python exFAT image builder (VBR, FAT, dir-entry sets, names, cluster chains) with a mutation knob per field |
| FAT32/16/12 | kernel `vfat` (if re-hosted) or a userspace reference | `mkfs.fat` (dosfstools) + raw patcher for LFN/BPB edge cases |
| tar | GNU tar / BusyBox tar / embedded extractor | Raw tar writer (own header/PAX/sparse builder) — do **not** rely on `tarfile` for hostile cases because Python sanitizes |
| gzip/zlib | zlib / gzip binary | Raw deflate member builder + bit-level mutations; canonical zlib seed corpus |
| XML | the manifest parser / libxml2 / expat | XML generator + entity/DTD/encoding mutations |

### 5.2 Design rules

1. **No device, no real update tree.** All inputs are synthesized in a scratch
   directory; the harness refuses to run if a mounted `/Volumes/*` or `/dev/sd*`
   path is referenced.
2. **Deterministic generators.** Every field is written explicitly; the generator
   takes a seed and a "knob map" (which field to mutate, to what value) so a crash
   is reproducible from a 64-bit seed + knob list.
3. **Sanitizers.** Build/run TUT under `-fsanitize=address,undefined` (and
   `-fsanitize=bounds,integer` where feasible) via `clang`; use `ASAN_OPTIONS=abort_on_error=1:detect_leaks=0`.
4. **Differential oracle.** For every valid-ish image, run the reference parser
   (`pyfatfs` for exFAT/FAT, `mtools` for FAT, GNU `tar -tvf` for tar, `zlib` for
   gzip, `xmllint --noent` vs `--nonet` for XML) and the TUT; flag divergence
   (different file set, different name, different size) as a bug signal even
   without a crash.
5. **Resource limits.** `ulimit -v`, `-t`, and `-f` per run; kill runs that exceed
   a time/memory/file-size ceiling to catch cluster-chain loops and bombs.
6. **Artifacts.** Each run writes `{seed,knobs,exit_signal,asan_log,stdout,stderr,ref_stdout}`;
   a triage script dedupes by normalized stack trace.

### 5.3 Corpus

- **Valid minima:** one empty exFAT image, one empty FAT32 image, a 1-file tree,
  a PAX/GNU-long-name tar, a sparse tar, a symlink tar, a `../`-name tar, a valid
  gzip of 1 byte, a 3-entity XML.
- **Structured mutations:** per-field boundary values (0, 1, -1/`0xFFFFFFFF`,
  `2^31`, `2^63`, max) for every length/count/offset; cluster-chain cycles of
  length 1/2/N; name-length overflow; UTF-16 surrogates; PAX record-length
  over/underflow; entity nesting depth 1..1000.
- **Dictionary:** exFAT field names, tar magic (`ustar`, `GNUtar`), PAX keys
  (`path=`, `linkpath=`, `size=`), XML tokens (`<!ENTITY`, `<!DOCTYPE`,
  `SYSTEM`, `encoding=`).

### 5.4 Fuzzing plan

1. **Phase A — build the rig first.** Generators + reference parsers + triage
   script, all offline, all unit-tested on synthetic inputs. No TUT yet.
2. **Phase B — differential smoke.** Run every generated corpus item through the
   reference parser; fix generator bugs; establish the "agreed" output.
3. **Phase C — TUT under libFuzzer/afl.** Once a parser binary is recovered:
   compile the thin `LLVMFuzzerTestOneInput` wrapper that feeds bytes to the
   parser entry point (`open_image`, `parse_dir`, `extract_tar`, `inflate`,
   `parse_manifest`). Fuzz each entry point separately with its dictionary.
4. **Phase D — kernel layer (only if M2/M5 confirmed).** For `vfat`/`msdos`/`exfat.ko`,
   re-host in a QEMU x86-64 VM booting the recovered kernel and mount the synthetic
   image; run a syzkaller-style loop against the mount syscall. No physical device.
5. **Phase E — triage.** Dedupe by stack, minimize with `libFuzzer -minimize_crash`,
   classify (OOB read / OOB write / infinite loop / divergence / arbitrary-write
   via `../`), and file findings without further exploitation.

### 5.5 What the harness must **not** do

- Never write outside the scratch dir (enforce via the `../`-extraction tests
  being *contained*: extract into a disposable `root/` and assert no escape).
- Never run a recovered binary that could execute system()/shell commands against
  the host; wrap extraction with `sandbox-exec`/a chroot-free seccomp shim.
- Never touch a real `/dev/` node or mounted volume.

---

## 6. CVE triage list

CVEs plausibly present in a 2018 embedded userspace. Confidence is marked; exact
IDs and fixed versions should be re-verified against NVD/vendor advisories before
being asserted in the ledger (this is a *triage* list, not a finding list).
Reachability is bounded by the trust-layer table in §0.

### 6.1 exFAT / FAT

| CVE / reference | Component | Class | Confidence | Note |
|---|---|---|---|---|
| (no CVE; vendor-silent) | Samsung out-of-tree `exfat` driver / libexfat | cluster math, name length, OOB | — | The 2018-era codebase has essentially **no public CVE record**; treat as "unknown-vulnerability territory", the whole reason to fuzz M1/M2/M3 |
| Mainline `exfat` driver fixes (5.4+, e.g. out-of-bounds dir-entry/namei patches) | Linux kernel `fs/exfat` | OOB read/write | Medium (post-dates the unit) | Useful as a *shopping list* of bug classes the vendor driver may also have |
| `CONFIG_VFAT_FS`/`CONFIG_MSDOS_FS` CVEs | Linux kernel 4.1 `fat` | LFN name length, FAT chain, BPB math | Medium | 4.1 predates several later `fat` hardening patches; enumerate by "Linux kernel fat CVE 2015-2020" on the bench |
| (device-specific, e.g. Qualcomm/Android exfat) | CVE-2019-9375 et al. | OOB | Low | Cross-check only; platform mismatch likely |

### 6.2 zlib / gzip

| CVE | Component | Class | Fixed in | Confidence |
|---|---|---|---|---|
| CVE-2016-9840 | zlib `inftrees` | pointer arithmetic / OOB | 1.2.9 | High |
| CVE-2016-9841 | zlib `inflate` | OOB read | 1.2.9 | High |
| CVE-2016-9842 | zlib | undefined shift / OOB read | 1.2.9 | High |
| CVE-2016-9843 | zlib `deflate` | OOB write | 1.2.9 | High |
| CVE-2018-25032 | zlib | memory corruption (deflate) | 1.2.12 | High |
| CVE-2022-37434 | zlib `inflate` | heap overflow | 1.2.12 | High |
| CVE-2005-2096 | zlib 1.2.2 gzip | DoS | 1.2.3 | Medium (old, may still ship) |
| CVE-2010-0001 | GNU gzip `unlzw` | integer overflow | 1.4 | Medium |

### 6.3 tar

| CVE | Component | Class | Confidence | Note |
|---|---|---|---|---|
| CVE-2016-6321 | GNU tar | path traversal / symlink escape on extract | High | The exact "arbitrary write" primitive of §3.1 |
| CVE-2007-4131 | GNU tar 1.16 | `..` traversal | High | Historical but the class persists |
| CVE-2001-1267 | GNU tar | `..` traversal | High | Historical |
| CVE-2011-5325 | BusyBox tar < 1.22.0 v5 | directory traversal | High | Already in `01-component-cve-corpus.md`; BusyBox tar is a strong candidate for a head unit |
| CVE-2016-4300/4301/4302, CVE-2016-5418, CVE-2017-14501/14502/14503 | libarchive (bsdtar) | OOB / symlink / path traversal | Medium | Only if the unit links libarchive instead of GNU/BusyBox tar |
| CVE-2019-1000019/1000020, CVE-2019-18408 | libarchive | 7zip/rar OOB | Low | Only if libarchive + those formats |

### 6.4 XML

| CVE | Component | Class | Fixed in | Confidence |
|---|---|---|---|---|
| CVE-2014-3660 | libxml2 | recursive entity expansion DoS | 2.9.2 | High |
| CVE-2016-9318 | libxml2 | XXE / external entity | 2.9.4 | High |
| CVE-2017-7375 | libxml2 | entity expansion (needs `XML_PARSE_HUGE` in some paths) | 2.9.5 | High |
| CVE-2017-7376 | libxml2 | entity expansion family | 2.9.5 | High |
| CVE-2016-4658 | libxml2 (Apple) | memory corruption | — | Medium |
| CVE-2019-19956 | libxml2 | memory leak | 2.9.10 | Medium |
| CVE-2018-14404 | libxml2 | NULL deref | 2.9.8 | Medium |
| CVE-2016-0718 | expat | buffer over-read | 2.1.1 | High |
| CVE-2017-9233 | expat | entity expansion / billion laughs | 2.2.1 | High |
| CVE-2019-15903 | expat | heap overflow | 2.2.8 | High |
| CVE-2022-22822 … 22827 | expat | integer overflow / OOB | 2.4.5 | Medium (post-dates 2018) |
| CVE-2021-45960/46143/46144 | expat | OOB | 2.4.1 | Medium |
| CVE-2021-42260 | TinyXML2 | infinite loop | 9.0.0 | Medium |

---

## 7. Open questions for the bench (blocking)

1. **Which filesystem parser actually runs?** Capture the mount table / media
   daemon strings on the bench: look for `libexfat`, `exfat`, `mount.exfat`,
   `fuseblk`, or a vendor media daemon. This selects M1/M2/M3/M5 and the TUT.
2. **Does the manifest parser expand entities / process DTDs?** One boolean that
   decides XXE/billion-laughs exposure.
3. **Does `AppUpgrade` extract with a path-traversal guard?** Test with synthetic
   `../`/absolute/symlink tars once the binary is recovered.
4. **Is FAT32 accepted despite the exFAT requirement?** If yes, the kernel `vfat`
   module is a real ring-0 path and needs the QEMU re-host harness.
5. **Which tar/gzip/XML libraries are linked?** `strings`/`readelf` on the
   recovered `AppUpgrade` to pin GNU tar vs BusyBox vs libarchive, and libxml2 vs
   expat vs TinyXML.
