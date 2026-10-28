# European `260128` kernel extraction and symbol-aware decompilation

Status: exact-build static evidence; no vehicle or firmware write.

## Artifact identity and platform

The inspected `HU/images/iasImage_1280_sub` has SHA-256
`55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0`.
Its recovered kernel is an x86-64 ELF with SHA-256
`f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`.
The embedded banner identifies Linux `4.1.27-abl`, built 2026-01-28. Its command
line selects ext4 on `/dev/mmcblk0p3`, systemd `esinit`, Intel i915 graphics and
the `ttyS2` console. This is direct evidence that the exact EU package is Linux
on x86-64, not Android on Telechips.

## Complete kallsyms recovery

The stripped ELF has no ordinary `.symtab`, but `CONFIG_KALLSYMS_ALL=y`
preserves the compressed table. A dependency-free extractor recovered 64,923
symbols. The output TSV has SHA-256
`3e94bc98783003490e5474de675f252ea08cd1d000372f2afbb926ce5fd1ea2f`.

| Table | File offset |
|---|---:|
| addresses | `0x89f158` |
| count (`64923`) | `0x91de30` |
| compressed names | `0x91de38` |
| 254 markers | `0x9dedc8` |
| token table | `0x9df5b8` |
| token index | `0x9df940` |

Validation was independent of name plausibility: the decoded count equals the
stored count, the stream consumes the exact names region, all 254 recomputed
markers match, and 64,719 kernel-range addresses are monotonic.

## Symbol-aware Ghidra results

Ghidra renamed 25,068 functions and recognized 25,147 total functions. Forty-
eight of 49 priority security functions were decompiled. The generated stats,
decompile index, caller graph and callee graph have SHA-256 values:

```text
9c478ff617d09f00c124f509074d75d6b4fa1a9ab2719592ba7d2cd3a99a188b  stats
89c3215f13cbb1a0015bf9910a5c76db32d787824f65463ea9399cd0c8275367  index
0f9e1442ee21edf8d0f75fdc7e1a048b37c871001784cea7059025fe243df2ee  callers
05efabea042ad144f0d993544a531760135b4fb996cf4d85f8ffd8a449aff42d  callees
```

### Reproduction record

The analysis used Ghidra `12.1.4 PUBLIC` in headless mode with its standard ELF
loader and default auto-analysis. The one priority name not recovered was
`range_is_allowed`; the final log records `decompiled=48 missing=1`.

Repository-persisted analysis helpers and their SHA-256 values are:

```text
9938972805f37680b4511ac463713ea8d391287d8e69352744c006b2fc12d125  tools/uk_fw/inspect_ipk_kernel.py
1747a5d1cf81c998753e9a62b358d8ea6c7f66f104d4dad67520519a607637ac  tools/uk_fw/kallsyms_extract.py
4f06cd810bcda895bf576e4d1924f378594ca824e63b6ab6729799e215089809  tools/uk_fw/elf_reader.py
f846b8e72f94fb3f623928784ec4b3bbba97ebc3ceaea48ea8f2abacd53cb6e3  tools/uk_fw/ghidra/ApplyKallsymsDecompile.java
c03c071cdd112171a10be8a081d2ac6c6c04ed9b13d11687a1d69681e0839652  tools/uk_fw/ghidra/priority.txt
```

The reproducible sequence is:

```sh
python3 tools/uk_fw/inspect_ipk_kernel.py \
  /absolute/path/to/IONIQ5_EU/HU/images/iasImage_1280_sub

dd if=/absolute/path/to/IONIQ5_EU/HU/images/iasImage_1280_sub \
  of=/private/tmp/ioniq5-eu-kernel.lz4 bs=1 skip=17502
lz4 -d /private/tmp/ioniq5-eu-kernel.lz4 /private/tmp/ioniq5-eu-kernel.elf

python3 tools/uk_fw/kallsyms_extract.py \
  /private/tmp/ioniq5-eu-kernel.elf /private/tmp/ioniq5-ksym-out

mkdir -p /private/tmp/ioniq5-ghidra-out /private/tmp/ioniq5-ghidra-project
/absolute/path/to/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
  /private/tmp/ioniq5-ghidra-project ioniq5-sym \
  -import /private/tmp/ioniq5-eu-kernel.elf \
  -scriptPath tools/uk_fw/ghidra \
  -postScript ApplyKallsymsDecompile.java \
    /private/tmp/ioniq5-ksym-out/kallsyms.tsv \
    /private/tmp/ioniq5-ghidra-out \
    tools/uk_fw/ghidra/priority.txt 20000
```

Hyundai appends signature or padding bytes after the legacy LZ4 frame, so the
local `lz4` command can report trailing undecodable bytes after emitting the
complete ELF. Reproduction must verify the emitted ELF magic and the kernel
SHA-256 above rather than treating that trailer alone as extraction failure.

## Exact-build security observations

- Module loading exists at `load_module` `0xffffffff810a78f6`,
  `sys_init_module` `0xffffffff810a9781`, and `sys_finit_module`
  `0xffffffff810a978c`. No module-signature verification path was recovered,
  matching `# CONFIG_MODULE_SIG is not set`.
- SMACK is active. Relevant symbols include `smack_inode_permission`
  `0xffffffff811bb37b`, `smack_mmap_file` `0xffffffff811bb6f8`, and
  `smk_write_onlycap` `0xffffffff811c07cc`.
- Device-memory, kcore and kexec code is present. `sys_kexec_load` requires
  `CAP_SYS_BOOT` and also checks `kexec_load_disabled`.
- An LG keystore driver is built into the kernel. Symbols include
  `verify_oem_signature` `0xffffffff811c5a36`, `keystore_ioctl`
  `0xffffffff811c44e0`, `keystore_verify`, `keystore_load_key`,
  `keystore_unload_key`, and `keystore_get_ksm_keypair`.

`verify_oem_signature` hashes supplied content with SHA-256 and passes the
digest and signature to `manifest_key_verify_digest`. That routine searches the
kernel asymmetric-key keyring for an OEM key descriptor, checks usage bits,
parses the signature and invokes the kernel public-key verifier. Update-trust
analysis must therefore include the kernel keystore; patching only a userland
check does not demonstrate that a modified update will be accepted.

The keystore open handler contains no explicit capability check, and the ioctl
call graph has no single global `capable()` gate. This does not prove
unprivileged reachability: device-node ownership/mode, SMACK labels, per-client
registration and operation-specific policy remain unknown until plaintext
exact-build rootfs contents or equivalent passive runtime evidence are
available. The encrypted rootfs envelope itself is present and verified.

These surfaces are not evidence of initial unprivileged root. Their usefulness
depends on a reachable execution primitive and the runtime policy in the
vehicle's exact userland.

