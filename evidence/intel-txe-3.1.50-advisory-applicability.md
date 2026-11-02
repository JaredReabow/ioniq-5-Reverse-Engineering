# Intel TXE 3.1.50 advisory applicability

## Scope

This note compares the exact Intel firmware identity recovered from the EU
`260128` ABL image with Intel's public security advisories. It is an offline
applicability assessment. It does not establish installed-unit identity,
Linux-to-TXE reachability, a usable MEI client, or an exploitation procedure.
No MEI endpoint or recovered firmware module was executed.

## Exact recovered identity

The canonical 8 MiB ABL is SHA-256
`f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac`.
Its exact signed FTPR partition manifest contains:

- firmware version components at manifest `+0x24`: `3, 1, 50, 2222`;
- version: **Intel TXE 3.1.50.2222**;
- manifest date field at `+0x14`: `0x20170926` (`2017-09-26`);
- TCB Security Version Number at `+0x2c`: `3`.

The exact execution layout independently agrees with public TXE v3 research:
BUP uses non-kernel-module base `0x26000`, and the signed FTPR syslib is called
at base `0x6000`. This identity is now emitted and tested by
`tools/uk_fw/abl_ias_key_provenance.py`.

## Intel-SA-00086: resolved by the recovered version

Official source:

- <https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00086.html>
- downloaded HTML SHA-256
  `df5e2e77660c45a6703daaaadf6cb5a206c3e1493c7e7e062cfceeb909536c50`.

Intel-SA-00086 identifies TXE 3.0 kernel issues including:

- CVE-2017-5707: multiple TXE-kernel buffer overflows allowing local arbitrary
  code execution;
- CVE-2017-5710: TXE-kernel privilege escalations allowing unauthorized access
  to privileged content.

Intel's resolved-version table lists **TXE 3.1.50.2222** as the production
release for Apollo Lake Atom E3900, Pentium, Celeron N, and Celeron J families.
The recovered FTPR version exactly equals that resolved release. Therefore
CVE-2017-5707/CVE-2017-5710 must not be promoted as candidates merely because
the platform uses TXE v3. Exact instruction-level backport identity was not
independently reconstructed, but Intel's own product/version classification is
direct negative applicability evidence.

## Intel-SA-00125: the recovered version is in the affected range

Official source:

- <https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00125.html>
- downloaded HTML SHA-256
  `e922a381b06eacf4e59ac7e9910d7651ca0713b22a4d155a913f586b23636e2f`.

Intel-SA-00125 states that TXE versions **3.0 through 3.1.50** are affected and
that TXE **3.1.55 or higher** is not affected. Its update table explicitly says
TXE 3.1.55 replaces **3.1.50.2222**. The recovered artifact is therefore an
exact version match for the advisory's superseded TXE release.

The relevant CVEs have materially different prerequisites:

- **CVE-2018-3655**: a subsystem flaw before TXE 3.1.55 may allow an
  unauthenticated user to modify or disclose information with **physical
  access**. Intel additionally states that a physical attacker may bypass CSME
  anti-replay protection, tamper with CSME/SPS/TXE data-file integrity, and
  potentially roll firmware back to a release affected by the earlier
  SA-00086 issues. Those consequences make persistent `/snowball` policy and
  provisioning-state rollback high-priority questions. The advisory does not
  identify the subsystem, object, transaction, or required electrical/debug
  interface, however; exact version applicability is established but an
  actionable route is not.
- **CVE-2018-12147**: insufficient input validation in the HECI subsystem before
  TXE 3.1.55 may allow a **privileged local user** to escalate privileges. This
  is a host-root/privileged-to-TXE lead, not an unprivileged Linux-root path.
  The exact rootfs ships MEI/TXE kernel modules and passive module-load
  configuration, but runtime device nodes, permissions, SMACK labels, client
  identities, transport binding, and installed bytes remain unknown.

Neither CVE by itself proves a way to replace `ipub_key`, UEP, `rot.key`, the
persistent `/snowball` policy objects, or a signed boot manifest. Those
consequences require exact client/protocol and write-authority evidence.

## Exact signed HECI receive-path bounds

The recovered `NFTP.man → heci.met → compressed heci` chain binds the exact
transport module:

- `heci.met` flash `0x205600`, size `0x1cc`, SHA-256
  `0826dda708681158fa6727e5dd50e5f7b8308869907e5d94dd5b458120429a59`;
- compressed `heci` flash `0x239000`, size `0x40b0`, SHA-256
  `e6e69c0bc6b33ac5d7651cb999da9b6f97c682011fca43800c6ffd1adfab2770`;
- strictly decompressed size `0x9000`, SHA-256
  `82b7be7bb8069aebfb2c9f7a0e994500fe10d631e67a16f5a5fec71d29679125`;
- code base `0x26000`, main entry `0x29015`.

The adjacent internal bus driver is independently bound by the same signed NFTP
manifest:

- `busdrv.met` flash `0x204cac`, size `0x260`, SHA-256
  `1857be7e234b2d88a9055d91c8bb9f69412d3db494b47f13cf407e9a0677da71`;
- compressed `busdrv` flash `0x21b000`, size `0x22ee`, SHA-256
  `e58a354055281fe2ab8809ef1d6705b7bdccc8acc11bf20faeaf0187a200eb50`;
- strictly decompressed size `0x6000`, SHA-256
  `f226a92dd219a020bca96aeca3b54d8b0870f230128b7cb206c3389d5096ad21`;
- code base `0x26000`, main entry `0x27d42`.

HECI opens its internal `/dev/bus_drv` service. `busdrv` publishes internal
`bus_drv`, `bus_mstro`, and `bus_prman` special files and performs MMIO,
interrupt, isolation, and power-state services. Its operation dispatcher is an
internal CSE interface, not a recovered Linux MEI client grammar.

Exact receive dispatcher `0x277c8..0x27dc9` and host-fragment consumer
`0x28a2d..0x28e77` establish that this transport path:

1. decodes payload length as `(header >> 16) & 0x1ff`;
2. rejects lengths above `0x1fc`;
3. requires enough FIFO words for the header plus rounded payload;
4. restricts control payloads to aligned lengths from four through eight;
5. copies ordinary fragments through a fixed `0x1fc`-byte local buffer;
6. looks up an enabled firmware client and a matching connection before use;
7. compares an initial fragment with the client's maximum message size; and
8. compares continuation fragments with remaining message capacity before the
   process-buffer copy.

This rejects a simple “nine-bit length directly overflows the local receive
buffer” theory. It does **not** identify CVE-2018-12147's actual proprietary
state/input defect, prove every HECI state or downstream client parser safe, or
justify rejecting the advisory for this exact module.

`heci.met` publishes internal special files `heci1`, `heci1ose`, `hecisoh`,
`heci1handoff`, `heci2`, and `heci3`, with CSE user/group IDs. These are not
Linux `/dev/mei*` DAC identities. Strings `/dev/bup_heci`, `/dev/events`,
`/dev/bus_drv`, `/dev/bus_prman`, `/dev/bus_bupdrv`, and
`/snowball/pm_ctxt` likewise describe internal CSE paths; they do not disclose
a host MEI client UUID or message grammar.

## Independent exact-module occurrence in a public ChromeOS image

A public Apollo Lake `reef` ChromeOS recovery was downloaded only as a
comparative artifact:

- URL: `https://dl.google.com/dl/edgedl/chromeos/recovery/chromeos_15572.63.0_reef_recovery_stable-channel_mp-v4.bin.zip`;
- recovery ZIP SHA-256
  `8843097ae538d5eda95ec1c0d60a150ec654670b2071cc9860e946443add7f69`;
- embedded firmware updater SHA-256
  `460eb573e8ec06157da3d2cd3c86173e122483ed1729902142b0beee02a260d1`;
- extracted `bios-reef.ro-9042-233-0.rw-9042-233-0.bin` SHA-256
  `85b99e6f91ae2fad154cb8394dc0afefe3178901713dea325a27cb7a5b6b62f9`.

ME Analyzer identifies that image's signed TXE manifests as `3.1.50.2238` and
extracts byte-identical modules:

- NFTP `heci` SHA-256 `82b7be7b...d29679125`;
- NFTP `busdrv` SHA-256 `f226a92d...096ad21`;
- FTPR `syslib` SHA-256 `dba068b8...e2dda961c`.

This independently reproduces the exact proprietary HECI transport bytes in a
public Apollo Lake firmware lineage. It is not evidence of target-board
acceptance, a vulnerability fix, or installed-unit identity: the comparative
image itself remains in the superseded TXE 3.1.50 family and therefore cannot
serve as the required 3.1.55 fixed-version diff.

## Hash-bound first-fixed and later comparison

The official ASUS X541NA BIOS `321` archive supplies the first-fixed family:

- official ZIP size `5,742,372`, SHA-256
  `26819e607f0ee9a9fd3b26518c9f9efa2c2e05bcca2a460992311826e603e1b7`;
- member `X541NA-AS.321` size `8,390,656`, SHA-256
  `bfc75d03e113184b84078a00f09be75779e80c6d0d14fb2f63dba350e31690c6`;
- 8 MiB IFWI SHA-256
  `db9325168976e1e68cba25924e82c2aeb2db85fb7a678de5fd66e200ab7643b9`;
- validly self-signed NFTP version `3.1.55.2269`, date `2018-07-16`, TCB SVN
  `3`;
- first-fixed HECI size `0x9000`, SHA-256
  `16afeb7e9a9328bd22b5c8b383b5e003bcce2e4d46db18ea1737606bffa3ed31`.

A public Intel NUC `AY0076.bio` capsule separately supplies a later Apollo Lake
image:

- capsule size `11,841,568`, SHA-256
  `ab8caa3fe9e5b3d14afb765e6a806d48d5918d21d85c3bff083b6b17ea4e7ec2`;
- strictly extracted IFWI size `16,773,120`, SHA-256
  `75a866331d8f23d023bbdcf9efdfee7b57bf4727eb50f6162940a2a51cb57b4a`;
- signed TXE version `3.1.94.3086`, date `2023-01-02`, TCB SVN `3`, ARB SVN
  `7`, and VCN `112`;
- signed later HECI size `0x9000`, SHA-256
  `04dceeb0b42db7910d913545b9b2342e9a26349c8e9d2e2bede201af62bf3b8f`.

`tools/uk_fw/txe_fixed_module_diff.py` verifies the FTPR/NFTP embedded
signatures, manifest-to-metadata and metadata-to-module reverse-SHA-256 chains,
and strict decompression for HECI, busdrv, storage, policy, fpf, dal_sdm, VFS,
and syslib. Its reviewed report is
`evidence/artifacts/update-candidates/txe-fixed-module-diff.json`, schema v3,
SHA-256
`d1043552b8ef772e825dc9e624dc3b62ab57f0fc8496cce7b359fbd5942d5fdb`.

Across the complete affected and first-fixed HECI modules, all 377 raw
differing bytes lie inside 369 same-offset external `rel32` encodings—366 calls
and three tail jumps—to 42 targets in `0x6460..0x67b2`. Every target shifts by
exactly +5, and zeroing only those immediates makes the complete modules
byte-identical. First-fixed also retains the affected nine-bit/`0x1fc` bound,
complete-bit-only top-header test, and aligned control geometry `4..8`.

The later HECI keeps the nine-bit length and `0x1fc` fragment maximum, while
adding exact header-state behavior:

- the later-defined DMA-ring bit 29 is rejected before payload dispatch;
- control messages require `(top_header_byte & 0x90) == 0x80`, rejecting the
  later-defined extended-header bit 28;
- aligned control payload geometry expands from `4..8` to `4..40` bytes; and
- bit 28 on ordinary messages selects a new bounded extended-header parser that
  checks its encoded length against both the payload and `0x1fc` destination.

Public Linux history names these as later DMA-ring and extended/vtag protocol
features. More importantly, exact recovered `mei.ko` transmit range
`0x4db1..0x4dd1` masks the header byte with `0x41`, clearing full-header bits
25..29 before stock transmission. Ordinary `/dev/mei` writes therefore do not
supply bits 28/29 through this path.

The first-fixed comparison proves these `3.1.94` header and extended-parser
deltas postdate `3.1.55`; they are not the primary-path CVE-2018-12147 fix.

The relocated syslib targets are now resolved rather than merely suspected.
Directly decoding all 42 affected and first-fixed import stubs maps 42 unique
syslib destination bodies. Across 4,410 reviewed body bytes, 39 raw differences
are wholly explained by 37 `rel32` address operands and one indexed-jump-table
base operand. All 42 body pairs are byte-identical after only those reviewed
address operands are normalized. This excludes an opcode or non-address-data
change in every syslib body directly imported by HECI. It does not exclude a
changed transitive callee, syscall/service implementation, indirect dispatch
target, another signed module, or downstream parser.

The exact later signed FPF adds structured `RbeArbEn`, `RbeArbSvn`,
`OemKmArbEn`, `OemKmArbSvn`, `UcodeArbEn`, and `UcodeArbSvn` records absent by
name from both affected and first-fixed signed FPF. This proves the named
records are not the `3.1.55` CVE-2018-3655 fix.

A stronger first-fixed storage candidate is now exact. Signed affected and
first-fixed storage metadata both define `ndl_critical` and `ndl_counting`
special files, but affected VFS contains neither `/dev/` path. First-fixed VFS
grows from `0x1d000` to `0x1f000`, opens `/dev/ndl_critical` and
`/dev/ndl_counting`, and passes both results to new syslib setter
`0x16691..0x166ab`. That setter marks and stores the two descriptors in a
thread-context structure. First-fixed VFS also adds a 25-pointer critical-name
table and bounded classifier for TPM/DRM/key-cache state names whose affected
counterparts occur only in full paths. The NDL names, critical classification,
and first-fixed timing make this the strongest current CVE-2018-3655
anti-replay/data-integrity candidate. Exact NDL
transaction semantics, monotonic-counter use, physical reachability, and
advisory attribution remain unproved. See
`evidence/intel-txe-fixed-module-diff.md` for full provenance, range hashes,
and boundaries.

## Intel's public recovery tool is not a firmware flasher

Intel's advisory links the public repository
`intel/INTEL-SA-00086-Linux-Recovery-Tools`, reviewed at commit
`a36d2c80e4c1782daab8d20d629ca91717fea33c`:

- `README.md` SHA-256
  `9e8b2aa709392e21c5326d5b860ff9c262c5ff616e4cc046883becfc6e8092fa`;
- `Intel-SA-00086-Recovery-Tool` SHA-256
  `be5bcf00ff34171104016232648a2c361745dc9760e247753b5ff6a965be6245`.

The repository describes post-update **platform-key reprovisioning** and
requires Intel PTT, the TPM CRB driver, `/dev/tpm*`, and the MEI driver. Its
published tool is a shell workflow around TPM2 and endorsement-certificate
operations. It neither supplies the TXE firmware update nor documents the
SA-00125 HECI flaw, `/snowball` access, a CSE filesystem writer, or arbitrary
key installation. It nevertheless justifies collecting passive TPM/PTT state
alongside MEI identity on the future bench.

## Practical research consequence

For a future disconnected bench, the safe order is:

1. passively confirm installed TXE/ABL identity and whether it still reports
   `3.1.50.2222` rather than a different board or service update;
2. record `/dev/mei*`, `/dev/tpm0`, and `/dev/tpmrm0` metadata without opening
   the nodes;
3. hash the MEI/TXE and TPM/CRB/TIS modules, and record the bound transport plus
   `/sys/class/mei/*` and `/sys/class/tpm/tpm*` identities;
4. determine host credentials, DAC, capabilities, and SMACK policy required to
   reach any client;
5. identify the exact client UUID and message grammar from recovered bytes or
   authoritative public material before considering any active request;
6. obtain separate authorization for active MEI/HECI interaction, and begin
   with read-only identity operations rather than storage, provisioning, or
   update commands.

The strongest current interpretation is:

- SA-00086 is a rejected version-only lead for this exact artifact;
- SA-00125 is an exact advisory-version match and a high-priority future bench
  lead;
- exact first-fixed comparison excludes HECI-local code/data and opcode or
  non-address-data changes in all 42 directly imported syslib destination
  bodies as the location of the `3.1.55` fix; changed transitive callees,
  syscall/service implementations, indirect dispatch, another signed module,
  or a downstream parser remain open, while later header/extended-parser
  changes postdate `3.1.55`;
- CVE-2018-12147 does not solve initial Linux root because it requires a
  privileged local caller;
- CVE-2018-3655 is directly relevant to a physically isolated bench because
  Intel names anti-replay bypass, TXE data-file tampering, and rollback as
  consequences; exact first-fixed VFS/syslib integration of `ndl_critical` and
  `ndl_counting` materially narrows the candidate subsystem, but does not yet
  expose a safe reproducible interface or equate NDL data with the exact
  `/snowball` objects;
- no TXE exploit, HECI message, malformed request, flash operation, or trust
  replacement has been generated or executed.
