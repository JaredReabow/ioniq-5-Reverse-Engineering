# Corrections log

Every claim this programme got wrong, what replaced it, and why. The changelog is
chronological; this is claim-oriented, so a reader landing on an older evidence
document knows whether to trust it.

Read this before quoting any evidence document.

**2026-10-21 scope warning:** C1–C11 preserve earlier correction entries, some
of which still overstate what their evidence establishes. In particular, C3/C4
are family/field-report claims, not installed-unit validation; C6/C10 do not
prove encryption boundaries; C11 does not prove all offline analysis impossible.
Use the current VM/recovery notes and C12–C14 below for those boundaries.

---

## C1 — Kernel symbol table was mispaired by 204 entries

- **Was:** 64,923 symbols recovered and applied to Ghidra; 48 security functions
  decompiled and named.
- **Now:** the address array start was taken at the first *kernel-range* pointer,
  so leading absolute (`A`) symbols were skipped and **every** symbol was paired
  with an address 204 entries away. Prologues still looked plausible, so the
  error was invisible.
- **Why:** cross-check against `__ksymtab` showed a constant −204 shift on 4,347
  of 4,375 exports. Fixed in `tools/uk_fw/kallsyms_structural.py`; the corrected
  table matches 4,369/4,375 exports exactly with zero mismatches.
- **Affected documents:** `eu-kernel-decompilation.md`,
  `eu-kernel-symbol-recovery-and-trust-chain.md` (the latter is correct).
  Any function-level claim resting on the original naming should be re-derived.

## C2 — Boot container field `0x18` is not a checksum

- **Was:** treated as a possible CRC covering some region; zlib and
  CRC-32/MPEG-2 hypotheses were tested and failed.
- **Now:** it is a **constant format/build id** (`0x42f08d94`), identical across
  all six `iasImage*_sub` variants whose command lines differ. It cannot be
  content-derived.
- **Why:** comparing the six variants directly.

## C3 — `mmcblk0p3` / `mmcblk0p5` are A/B system partitions, not display variants

- **Was:** interpreted as two root selections tied to 1280 vs 1920 display models.
- **Now:** they are the **A/B system partition pair** of one device family. The
  update writes to the inactive partition and rewrites `/etc/fstab`.
- **Why:** the public `wideopen` wiki's update-process description plus the
  patcher's A/B handling.

## C4 — Downgrade is not blocked

- **Was:** the `>=` version check blocks downgrade on the Linux path.
- **Now:** the version gate is a single userland comparison, and the public
  `navi_extended` FAQ documents substitution — older official payloads paired
  with the **latest** `.lge.upgrade.xml` for the same vehicle, so a genuine signed
  newer manifest satisfies the check. The Android sibling differs: its signed
  `update_info` binds the package, which is why the EV6 report failed.
- **Why:** child note 10 plus the tracker evidence.
- **Caveat:** three non-cryptographic obstacles remain (feed, target build,
  unconfirmed on 2026 packages).

## C5 — The `.ver` CRC hypothesis is weaker than first stated

- **Was:** if the upgrader relied on the `.ver` CRC, a CRC-repaired payload would
  pass and custom firmware would need no key.
- **Now:** the arithmetic stands — CRC-32 is forgeable and `crc32_forge.py`
  demonstrates it. The *exploitable* reading is weakened: a public report
  describes repairing CRC **and** size and being rejected, so at least one further
  check exists. Also, `.ver` values cover **ciphertext**, so modification still
  requires the key.
- **Why:** community field evidence (child note 10 / `community-field-evidence.md`).

## C6 — Header entropy was misread

- **Was:** the 3,385-byte boot-image header looked "structured" at entropy ~5.7.
- **Now:** 6.0 is the maximum for a 64-byte block, so ~5.7 means **random**. The
  header is encrypted, not plaintext metadata.
- **Why:** recomputing entropy correctly. The region contains no little-endian
  copy of 6,210,308 / 3,385 / 13,035 / 52 / 953 / `0x42f08d94`.

## C7 — The `DecryptToPIPE` invocation was guessed, and guessed wrong

- **Was:** `gen5w_decrypt.py` defaulted to `DecryptToPipe {input} {output}` and
  assumed the package footer had to be stripped first.
- **Now:** the documented invocation is
  `DecryptToPIPE -d <keyfile> <input> 0 > <output>`. Output is on stdout, and the
  whole file — footer included — is handed over; nothing is stripped.
- **Why:** the public `update_decryptor` Dockerfile and `entrypoint.sh`.

## C8 — An attempted vulnerability was rejected

- **Was (hypothesis):** `KEYSTORE_IOC_TEST_VERIFY_ECC_SIGNATURE` (0x412037c9)
  left its tail fields uninitialised because the ioctl declared only 32 bytes.
- **Now:** rejected. Decoded size is `0x120` (288), which covers the offsets the
  handler reads. **Not a bug.**
- **Why:** decoding `_IOC` correctly instead of by eye. Recorded so it is not
  re-raised.

## C9 — A second attempted vulnerability was rejected

- **Was (hypothesis):** `keystore_get_ksm_key` zeroed one buffer then copied from
  another, suggesting an uninitialised-stack disclosure.
- **Now:** rejected at instruction level. The buffer is
  `[68-byte private][136-byte public]`; the code zeroes the private half and
  returns the public half. **Not a bug.** The earlier reading was a decompiler
  artefact.
- **Why:** disassembling the function rather than trusting Ghidra's variable
  sizing.

## C10 — The `iasImage` decomposition replaced an earlier, vaguer note

- **Was:** "16,420 bytes larger than `_sub`, five of six share a 13,035-byte
  trailer."
- **Now:** exact — `3,385 header + 6,210,308 payload + 13,035 trailer =
  6,226,728`, where the payload length equals the plaintext `_sub` size.
- **Why:** arithmetic closes exactly.

## C11 — A "kernel IAS driver" does not exist

- **Was (hope):** the `ipk.`/`iasImage` format might be handled by Linux and
  therefore analysable.
- **Now:** the kernel contains no IAS symbol, string or config option. The format
  is a **boot loader** concern; it cannot be analysed without an SPI dump.
- **Why:** symbol, string and config searches.

---

## C12 — VM impossibility, PCI enumeration and panic attribution

- **Was:** no usable block device or display path; a nearby keystore warning
  established an anti-tamper panic; successful synthetic inputs bypassed it.
- **Now:** the panic trace is a root-mount failure. QEMU SDHCI `1b36:0007`
  binds after an exact-build guest-RAM PCI-table adaptation, and a compatible
  ext4 root executes BusyBox. A userspace PCI-mapped VGA diagnostic displays
  verified pixels and accepts virtual keyboard events. Missing framebuffer
  support did not make all graphics impossible.
- **Boundary:** this is a VM-adapted vendor kernel and our research userland,
  not a recovered HMI or a boot-trust bypass. Synthetic initialization is not
  possession of device keys. Sparse logs did not prove failed PCI enumeration.
- **Evidence:** `vendor-kernel-vm.md`, `vendor-kernel-graphics.md` and fresh
  regressions in `local-ui-recovery.md`.

## C13 — Entropy, arithmetic and suffix equality do not decode an envelope

- **Was:** the 3,385/payload/13,035 split was an exact decoded layout; shared
  high-entropy suffixes were definitely encrypted descriptors; a decryptor
  must strip those suffixes; the unique prefix length was a plaintext length.
- **Now:** those interpretations exceed the measurements. Arithmetic and
  shared bytes do not establish fields, keys, signature coverage or acceptance.
  Finite-sample entropy does not distinguish encrypted data from other
  high-entropy content. The documented vendor CLI takes the **whole input**,
  as already noted in C7. `eu-ota-container-structure.md` now says so directly.
- **Boundary:** no current payload format or authentic decryption is recovered.

## C14 — Local recovery negatives must retain their search bounds

- **Was:** broad claims that no package key material or offline avenue exists.
- **Now:** the new public-RSA probe finds no type-1 block under the boot key
  in the recorded edges of 38 files. Two statically reconstructed Mac updater
  AES pairs yield no validated plaintext in the tested CBC hypotheses. Two
  gzip-marker matches fail reserved-flag/zlib checks. Positive controls pass.
- **Boundary:** other keys, encodings, locations and derivations are untested.
  The Mac updater's text/API crypto is not established firmware crypto. REA
  Mach-O inspection succeeded; its deep Ghidra function analysis timed out,
  so function claims here use explicitly identified LLVM disassembly instead.
- **Evidence:** `local-ui-recovery.md`, retained reports and 13 new RSA-probe
  unit tests. No new Fable/Council acceptance is claimed.

---

## Standing practice that produced these corrections

1. Cross-check a symbol table against an independent table before trusting names.
2. Disassemble a function before calling a decompiler artefact a vulnerability.
3. Compute an entropy maximum before calling entropy "low".
4. Treat a field report as evidence against a hypothesis, not just for it.
5. Record rejected hypotheses, not only accepted findings.

Items C8 and C9 were never vulnerabilities; they are kept here because a reader
who finds the earlier reasoning in a draft should know it was tested and failed.
