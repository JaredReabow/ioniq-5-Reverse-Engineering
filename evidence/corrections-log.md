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
- **Now:** the documented userspace version gate is a string comparison, and the public
  `navi_extended` FAQ documents substitution — older official payloads paired
  with the **latest** `.lge.upgrade.xml` for the same vehicle, so a genuine signed
  newer manifest satisfies the check. The Android sibling differs: its signed
  `update_info` binds the package, which is why the EV6 report failed.
- **Why:** child note 10 plus the tracker evidence.
- **Caveat:** feed, target build, unconfirmed behavior on 2026 packages, and
  unaudited loader/fuse rollback policy remain.

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

## C15 — D-Bus transition result `255` is not sufficient to call the request rejected

- **Was:** the immediate `/transition` out value `255` was treated as a
  rejection/non-success result, even after the standby state changed.
- **Now:** it is not a completion verdict in isolation. In the corroborated
  post-agreement run, the same immediate value is followed by
  `is_standby_agree_pressed ... result[1]`, exception-filter results zero,
  current AppID Home `11`, authentic Home response `ret[1]`, drawing AppID
  `11`, IVI foreground of surface `1001`, and visibly composed Home pixels.
- **Why:** the full downstream asynchronous manager/application/IVI chain is
  stronger evidence than the method's immediate integer.
- **Boundary:** this does not assign an exact enum name to `255` and does not
  prove Home↔Navigation operation. Classify each request from downstream state
  and response evidence.
- **Evidence:** `HANDOVER.md`, `Ioniq5-CHANGELOG.md` 0.44.0, and archive SHA-256
  `87d81b278f8b1bb20236faedd17dda0493b49b6cfc1e0fd2f1acfe8b8d2c6f5e`.

---

## C16 — V-006's unquoted root shell sink is not descriptor-based command injection

- **Was:** static review stopped at `util_replace_whitespace()` and concluded that
  USB serial punctuation, `${IFS}`, separators and redirects reached
  `/app/bin/usb-automount` unchanged. V-006 was therefore labelled a confirmed
  CWE-78 USB-to-root path and a physical payload sequence was documented.
- **Now:** `builtin_usb_id` next calls `util_replace_chars(..., NULL)`. Its default
  allowlist is alphanumerics plus `#+-.:=@_`; other tested printable characters
  become `_`. QEMU `usb-mtp` exercised the authentic udev → root automounter →
  `system()` chain. The old payload was sanitized and no command executed.
- **Why:** the call at `0x1c33e` was misidentified as trimming rather than the
  security-relevant character filter. Static sink analysis omitted an upstream
  transformation at the trust boundary.
- **Boundary:** the shell construction is still unsafe and a leading `#` can
  disrupt it. Other firmware/udev builds and untested property paths require
  separate validation. Physical-head-unit parity is unverified.
- **Evidence:** `v006-exploit-host.log` SHA-256
  `568f3197ff178cbf8356674c74a149b66ec1bfd96eedd5f2098a830c84adb27a`;
  sanitizer matrix SHA-256
  `de0757442ca4a74d3a3f87db79e8c3eb2b16b101dc47131d266af71ac734b0a1`;
  `Ioniq5-VULNERABILITIES.md` V-006.

---

## C17 — Missing `MS_NODEV` does not mean every USB image can carry a live device node

- **Was:** the confirmed absence of `MS_NODEV` was immediately described as a
  first-ranked path where “any normal image containing `mknod` nodes” exposes raw
  internal block devices.
- **Now:** the automounter constructs vendor filesystem names `tntfs`/`texfat`;
  other types become literal `mtp`. FAT/exFAT do not natively encode POSIX device
  inodes. Whether a special-file encoding produced on NTFS is materialized as a
  device by this exact Tuxera module is untested. Even if it is, a local process
  must still open and use the node; the node does not execute from USB.
- **Why:** mount flags establish policy, not on-disk filesystem semantics or an
  execution trigger. Those are separate reachability steps.
- **Boundary at correction time:** omitting `MS_NODEV` remained a real hardening
  error and V-011 became a post-execution/DAC-bypass candidate, not a
  stock-to-root claim. The harmless dynamic test has since been completed; see
  C21.

---

## C18 — The `4.1.27-abl` banner does not make Dirty COW present

- **Was:** CVE-2016-5195 was ranked as the leading post-execution local-root
  candidate because upstream Linux 4.1 did not receive the fix until 4.1.35.
- **Now:** the recovered vendor binary contains the fix's paired invariants:
  `follow_page_mask` requires `FOLL_FORCE | FOLL_COW` and a dirty PTE before
  following a forced write PTE, while `__get_user_pages` sets `FOLL_COW` after
  the COW fault. The vulnerable `FOLL_WRITE`-clearing sequence is not used.
- **Why:** the original ranking was version-gap triage and explicitly did not
  confirm vendor cherry-picks. Exact binary inspection now supplies that check.
- **Boundary:** this rejects Dirty COW only for recovered EU `260128`; it does
  not validate other kernel CVEs or the owner's unknown installed build.
- **Evidence:** `evidence/vendor-kernel-dirty-cow-backport.md`.

---

## C19 — Both ranked AF_PACKET races are backported in the shipped module

- **Was:** the TPACKET_V3 version-change and `PACKET_RESERVE` races remained
  ranked as AF_PACKET local-root hypotheses based on upstream fix dates.
- **Now:** shipped `af_packet.ko` acquires the socket lock at the start of
  `packet_set_ring`, locks the `PACKET_VERSION` branch around ring checks and
  `tp_version`, and separately locks the `PACKET_RESERVE` branch around ring
  checks and `tp_reserve`. These are the changes from upstream commits
  `84ac7260236a` and `c27927e372f0`.
- **Why:** as with Dirty COW, a base version identifies candidates but cannot
  establish that an OEM kernel omitted a backport.
- **Boundary:** this rejects CVE-2016-8655 and CVE-2017-1000111 only; other
  AF_PACKET bugs and actual
  `CAP_NET_RAW` assignments need separate checks.
- **Evidence:** `evidence/vendor-kernel-af-packet-backport.md`.

---

## C20 — The larger Stack Clash guard gap is present despite the old banner

- **Was:** CVE-2017-1000364 remained the leading version-derived local-root
  hypothesis after Dirty COW and the AF_PACKET races were rejected.
- **Now:** the vendor binary contains `vm_start_gap`, `stack_guard_gap`, its boot
  parameter parser, and an initialized 1 MiB gap. Those are the central changes
  from upstream commit `1be7107fbe18`.
- **Why:** ranking by the upstream stable version again missed an OEM backport.
- **Boundary:** the larger gap is mitigation rather than a proof against every
  stack-growth technique, but the generic missing-fix premise is false here.
- **Evidence:** `evidence/vendor-kernel-stack-guard-backport.md`.

---

## C21 — Exact Tuxera NTFS does preserve usable special-node semantics

- **Was:** after C17, Tuxera NTFS special-file materialization and the practical
  effect of `nodev` remained unverified.
- **Now:** exact `tntfs` `3016.7.1.2.3` retained an inert character node (`1:3`)
  across unmount/remount. Without `nodev`, numeric uid/gid 65534 under SMACK `_`
  opened it read-only; with `nodev`, the same open failed with `EACCES`.
- **Why:** filesystem semantics must be measured separately from mount-flag
  recovery. The test used only QEMU `/dev/null` and a disposable NTFS image.
- **Boundary:** this confirms a device-policy bypass primitive, not USB-to-root.
  A production local opener, useful major/minor, access mode and SMACK/path
  permission are still required.
- **Evidence:** `evidence/usb-root-test-plan.md` and the hashes recorded there.

---

## C22 — Enabled keyrings do not make CVE-2016-0728 present

- **Was:** CVE-2016-0728 remained a local-root candidate because
  `CONFIG_KEYS=y`, the vulnerable-era API exists, and the base version predates
  its upstream stable fix.
- **Now:** exact `join_session_keyring` disassembly releases the lookup reference
  when the located keyring equals the new credentials' current session keyring.
  This is the complete operation added by upstream commit `23567fd052a9`.
- **Why:** subsystem enablement and version range establish reachability for
  triage, not the absence of a vendor backport.
- **Boundary:** this rejects CVE-2016-0728 only. It does not validate unrelated
  keyring lifetime or permission paths.
- **Evidence:** `evidence/vendor-kernel-keyring-backport.md`.

---

## C23 — Read-only ALSA sequencer ioctl access does not expose every sequencer race

- **Was:** once V-013 proved uid/gid-65534 create/delete ioctl reachability on
  `/dev/snd/seq`, nearby sequencer CVEs could appear equally reachable.
- **Now:** exact `snd-seq.ko` lacks CVE-2018-1000004's official Linux 4.1 ioctl
  serialization, but its published pool sequence requires `write()` while
  recovered intended node policy is `root:root 0644`. The VM confirmed V-013
  ioctls through an `O_RDONLY` descriptor under that manually modeled mode, but
  an ordinary uid cannot obtain the write-capable descriptor needed by the
  sibling sequence.
- **Why:** device-node reachability is operation-specific; a readable ioctl
  surface does not confer file write access.
- **Boundary:** altered DAC, a passed write-capable fd, a privileged service, or
  different installed firmware could restore the precondition. The code should
  still be patched.
- **Evidence:** `evidence/vendor-kernel-alsa-follow-up-cves.md`.

---

## C24 — Public ASF source layout is not the exact vendor layout

- **Was:** the source-derived x86-64 `AsfStream` size was treated as 200 bytes,
  placing the 33rd stream's `pad` assignment directly over the live
  `GstFlowCombiner *` field.
- **Now:** exact shipped `libgstasf.so` instructions use a 208-byte (`0xd0`)
  stride and an additional 8 bytes before the pad field. For stream index 32,
  plugin offset `0x990d` zeros the low 32 bits of `flowcombiner`; the pad pointer
  instead overwrites the start of `old_stream[0]`.
- **Why:** the vendor plugin contains a layout-changing source modification not
  represented by the public GStreamer 1.8.3 header. Source is useful for naming
  behavior but cannot supply exact offsets for a modified binary.
- **Dynamic confirmation:** PlayerEngine catches signal 11 with
  `g_queue_push_head+0x1d <- libgstasf.so+0xb6cc`; exact code at
  `0xb6c0..0xb6c7` loads the corrupted `flowcombiner` and calls
  `gst_flow_combiner_add_pad`.
- **Boundary:** this establishes the first observed fatal corrupted use, not an
  attacker-selected pointer, instruction-pointer control, or RCE.
- **Evidence:** `evidence/gstreamer-cve-2026-2920.md` and
  `evidence/artifacts/media-candidates/playerengine-asf-service-evidence.txt`.

---

## C25 — V-006's sanitizer does not sanitize every udev hardware helper

- **Was:** after V-006's `ID_SERIAL_SHORT` route was rejected, it was tempting to
  treat systemd-udev descriptor/property injection as generally blocked on this
  build.
- **Now:** CVE-2026-40225 crosses different helpers. Exact shipped `v4l_id` and
  `scsi_id` instructions print kernel-provided product/serial fields directly as
  line-oriented properties, without the control-character checks added by the
  2026 fix. Installed rules consume those properties, and an installed
  `debug-shell.service` makes the SCSI `SYSTEMD_WANTS` route security-relevant.
- **Why:** sanitization must be traced per property producer and consumer.
  `usb_id`'s restricted `ID_SERIAL_SHORT` does not transform `v4l_id` or
  `scsi_id` output.
- **Version boundary:** PID 1's compiled banner/pkg-config report systemd `225`,
  while embedded OpenEmbedded build paths say `systemd/1_249.3-r0`. The finding
  relies on exact helper instructions and rules, not either version string.
- **Dynamic refinement:** a fixed benign `udevadm test` control confirmed parser
  retention. Matched synthetic-add controls then showed exact udevd persisting
  the property and exact PID 1 systemd starting only the positive transient
  BusyBox marker unit; the negative run did not. Vulnerable helper rules were
  masked, and no pre-existing property-selected unit or shell was requested.
- **Evidence boundary:** no malicious physical-device event, shipped vulnerable
  helper execution, installed shell-unit request, or physical root transition
  has been observed. V-014 remains a high-confidence static physical path in
  recovered `260128`, with downstream synthetic semantics dynamically confirmed;
  it is not proof about the owner's
  unknown installed build.
- **Evidence:** `evidence/systemd-udev-cve-2026-40225.md`.

---

## C26 — Thumbnail `Start(as)` does not select the audio/TagLib path by extension

- **Was:** early exploratory thumbnail runs did not map `libgstasf`, and the
  `.wma` route was described as following the extractor's audio/TagLib path.
- **Now:** exact code shows `ThumbnailService::startExtractThumb()` queues every
  path and `StartThumbnail()` always obtains `VideoContext`. Its pipeline is
  `uridecodebin ... appsink`, and its custom autoplug callback does not reject
  `asfdemux`. The separate `AudioProcess` is used by the cover-art context.
- **Invocation boundary:** MediaBrowser exposes explicit CommonAPI
  `requestThumbnails(as)` and forwards it to the extractor's session-bus
  `Start(as)`. Reviewed scan-completed and media-file-found callbacks do not call
  this request path, so automatic scan-time or UI invocation is not established.
- **Dynamic boundary:** bounded VM attempts did not observe service-name
  acquisition, a delivered `Start`, `libgstasf` mapping, cache output, or a
  natural process crash. A no-reply `dbus-send` return code does not prove
  delivery. This is exact static routing evidence, not a thumbnail crash.
- **Evidence:**
  `evidence/artifacts/media-candidates/thumbnail-extractor-asf-route-evidence.txt`.

---

## C27 — Integrated `extracted-safe` BusyBox is a VM helper, not stock firmware

- **Was:** current `extracted-safe/mango-rootfs/bin/busybox`, SHA-256
  `6e123e7f...11348`, was treated as the original `/usr/bin/unzip` provider and
  its BusyBox 1.35.0 method-12 BZIP2 code was assigned to recovered `260128`.
- **Now:** VM integration preserved the original as `busybox.vendor`, removed
  that path, and hard-linked the static research helper from `work/vm/busybox`
  into `/bin/busybox`. Canonical stock bytes from the independent original
  extraction are SHA-256 `95bab633...bd9ebc`, BusyBox 1.23.2. Stock `unzip`
  accepts methods 0/8 and rejects method 12.
- **Replacement finding:** stock method 8 reaches exact pre-fix CVE-2015-9261
  `huft_build` before AppScomoDM authenticates either extracted member. The
  supported result is likely `unzip` child crash/update DoS, not the withdrawn
  method-12 allocation-relative write claim.
- **Additional corrections:** AppScomoDM's archive selector examines one first
  `QDirIterator` result rather than the last match. Exact Qt returns a normalized
  exit code; checking only bits 8–15 accepts every normal 0..255 exit code.
- **Why:** an offline extraction tree became a VM staging tree. Hard links and
  path names are not provenance; original archive/extraction identities must be
  rechecked before exact-binary conclusions.
- **Evidence:** `evidence/busybox-unzip-cve-2015-9261.md` and
  `evidence/artifacts/update-candidates/busybox-unzip-cve-2015-9261-evidence.txt`.

---

## C28 — The published CVE-2017-7308 private-area primitive is backported, but one companion guard is absent

- **Was:** the AF_PACKET review rejected two race CVEs but explicitly left other
  TPACKET arithmetic defects unchecked.
- **Now:** exact `af_packet.ko` performs the CVE-2017-7308
  `BLK_PLUS_PRIV((u64)tp_sizeof_priv)` calculation in 64-bit registers before
  comparing it with block size, matching upstream fix `2b6867c2ce76`. The
  Project Zero private-area signedness/overflow primitive is therefore absent.
- **Residual, now resolved:** the same exact function still performs
  `frames_per_block * tp_block_nr` in 32 bits without the companion
  `UINT_MAX / tp_block_nr` guard from `8f8d28e4d6d8`. Completed exact V1/V2
  tracing proves allocation uses full block count and every wrapped logical
  position remains within the vector and block, including wrapped count zero.
  Separate mmap size wrap fails at exact VMA insertion bounds. The omission is a
  correctness/early-rejection gap, not an impact-unknown frame-lookup primitive.
  Three signed vector-index opcodes begin at block count `0x80000001`, but the
  minimum vector yields order 23 and exact allocator paths reject every order
  above 10. They are predicate-infeasible even though the final frame-product
  guard alone would not reject every such `F=1` geometry.
- **Boundary:** all packet-socket paths still require `CAP_NET_RAW`, applicable
  ring-version reachability, and the owner's installed module identity. This does not reject
  unrelated AF_PACKET defects.
- **Evidence:** `evidence/vendor-kernel-af-packet-backport.md` and
  `evidence/vendor-kernel-af-packet-frame-count.md`.

---

## C29 — The FUMO encryption-mode byte does control one navigation signature gate

- **Was:** a separate Navi NUA signature path was noted, but the reviewed data
  flow had not shown `/update/disableEncryptionUpdate` controlling it.
- **Now:** exact inner-FUMO function `0x128070` tests the shared mode byte at
  `0x128940`. Byte zero logs the non-encrypted navigation-map signature skip and
  sets gate-complete byte `this+0xd5`. FUMO startup sets that mode byte to zero
  when `/update/disableEncryptionUpdate` exists.
- **Additional skip:** dedicated marker
  `/update/disableNaviMapSignatureCheck_20230207`, absent NaviUpdateApp/NUA
  provider, and no navigation-map candidate also complete this one gate without
  running its asynchronous verifier. The exact binary has only the existence
  check as a static reference to the dedicated marker literal; dynamic
  construction and other-process writers remain unexcluded.
- **Boundary:** this is a named navigation-map signature skip, not a universal
  package-signature or payload-acceptance bypass. Marker creation, outer FUMO
  contracts, version/model/region, non-map digests, writes, slot/boot trust,
  root, and persistence remain separate.
- **Evidence:** `evidence/appupgrade-update-trust.md` and
  `evidence/artifacts/update-candidates/fumo-navi-signature-gate-evidence.txt`.

---

## C30 — `force_launch=run` does not itself establish completion

- **Was:** inner FUMO writer sites were known, but the completion-string
  provenance and authentication state preceding force-marker creation remained
  unnamed.
- **Now:** callback FDE `[0x11f1b0,0x120a9e)` attempts `processing` at
  progress zero and then `force_launch=run`; the branch-local progress-100
  sequence attempts `complete` and then force value `none`, while later
  scheduled flow can attempt `run` again. The weak writer does not prove full,
  successful, or atomic transitions. Exact `DeltaUpdateProgressHandler` and
  timer routes feed some callback events.
- **Boundary:** no named cryptographic result is read at the direct force-write
  sites, so the marker alone does not establish completion or authentication in
  this write-site evidence. This does not prove an unauthenticated package can
  generate a valid upstream progress event. The scheduled call site retains its
  separate two-completion-string and schedule-state conditions.
- **Evidence:** `evidence/appdmclient-fumo-usb-eligibility.md` and
  `evidence/artifacts/update-candidates/fumo-progress-force-marker-evidence.txt`.

---

## C31 — Missing explicit `sock = NULL` opcode is not a missing CVE-2017-11176 fix

- **Tempting but wrong shortcut:** exact `sys_mq_notify` loops when
  `netlink_attachskb()` returns one without an explicit zeroing instruction for
  its socket register. Reading only that edge would classify the old kernel as
  pre-fix.
- **Exact result:** the callee first drops the socket reference, but both failed
  retry lookup paths jump directly to notification-skb cleanup at
  `0xffffffff811b18a4`. Neither can reach socket-detach cleanup at
  `0xffffffff811b1892` with the old pointer. That branch structure is
  machine-code-equivalent to upstream `sock = NULL`.
- **Conclusion:** CVE-2017-11176's stale-reference over-release is rejected for
  recovered `vmlinux` SHA-256 `f5ee9c2f...6b102b`, even though
  `CONFIG_POSIX_MQUEUE=y`. The conclusion does not cover unrelated mqueue or
  netlink defects or the owner's unknown installed kernel.
- **Evidence:** `evidence/vendor-kernel-mq-notify-backport.md` and
  `evidence/artifacts/kernel-candidates/mq-notify-cve-2017-11176.asm`.

---

## C32 — Old USB-audio configuration does not imply CVE-2016-2384

- **Candidate:** the recovered kernel enables `CONFIG_SND_USB_AUDIO=m` and ships
  exact generic USB-audio and USB-MIDI modules, so descriptor-driven probe code
  is a genuine physical pre-login surface.
- **Exact result:** after `snd_rawmidi_new()` installs the private-free owner,
  every reviewed endpoint-creation failure branches directly to the error
  epilogue. None calls or inlines the second USB-MIDI object free removed by
  upstream `07d86ca93db7e5cdf4743564d98292042ec21af7`.
- **Conclusion:** CVE-2016-2384 is rejected for exact `snd-usbmidi-lib.ko`
  SHA-256 `ad2180ba...b434be`. This does not remove other USB parser candidates
  or prove production port/module state on the owner's unknown build.
- **Evidence:** `evidence/vendor-kernel-usb-midi-backport.md` and
  `evidence/artifacts/kernel-candidates/snd-usbmidi-cve-2016-2384.asm`.

---

## C33 — Three ordinary local-kernel paths also carry semantic backports

- **Candidates:** CVE-2015-7613, CVE-2016-7117, and CVE-2017-8890 need no user
  namespace or special device in their generic upstream routes, and the
  recovered kernel compiles in SysV IPC, sockets, IPv4 and multicast.
- **Exact result:** credentials and object state dominate SysV IDR publication;
  `recvmmsg` writes delayed `sk_err` before exact `fput_light`; and cloned
  accepted sockets clear child `mc_list` before return. Exact
  `ip_mc_drop_socket` independently binds the cleared offset to multicast
  teardown.
- **Conclusion:** all three named primitives are rejected for recovered
  `vmlinux` SHA-256 `f5ee9c2f...6b102b`. This does not cover other defects or
  the owner's unknown installed kernel.
- **Evidence:** `evidence/vendor-kernel-socket-ipc-backports.md`.

---

## C34 — shipped ALSA timer code is not enough to inherit four 2016 flaws

- **Candidate:** `CONFIG_SND_TIMER=m`, exact `snd-timer.ko`, and intended static
  `/dev/snd/timer` policy made CVE-2016-2545 through CVE-2016-2548 credible
  local candidates despite unknown runtime load and access.
- **Exact result:** interrupt expiry uses `list_del_init`; open initializes one
  mutex used by every ioctl and release; and slave attach, master close,
  delayed start, and stop carry the complete nested lock-and-unlink effects.
- **Conclusion:** all four named primitives are rejected for exact module
  SHA-256 `3b2fa4e7...ac46a91`. This is not a claim about other ALSA timer bugs
  or the owner's installed module.
- **Evidence:** `evidence/vendor-kernel-alsa-timer-backports.md`.

---

## C35 — ALSA timer fixes are callback-specific, not module-wide

- **Earlier boundary:** the first ALSA timer pass correctly rejected the
  list/ioctl races but did not yet inspect later padding-disclosure fixes.
- **Exact result:** params and `snd_timer_user_ccallback` clear complete 32-byte
  records. `snd_timer_user_tinterrupt` clears only a separate 16-byte timestamp;
  both event branches leave two four-byte padding regions untouched while exact
  queue/read code copies all 32 bytes.
- **Conclusion:** CVE-2016-4569 is rejected and one CVE-2016-4578 callback is
  fixed, but V-021 records a residual conditional information disclosure. It is
  not a root or code-execution finding.
- **Evidence:** `evidence/vendor-kernel-alsa-timer-follow-up.md`.

---

## C40 — missing timerfd context locking is not demonstrated privilege gain

- **Candidate:** CVE-2017-10661 affects an ordinary built-in syscall surface and
  exact code predates the stable 4.1.41 fix.
- **Exact result:** same-file operations resolve one context; setup/removal
  decide membership outside the static global-list lock, and no common
  context-derived lock covers the transition.
- **Conclusion:** V-026 establishes the race premise. It does not establish a
  harmful interleaving, list corruption, UAF, crash, root, or persistence;
  public privilege-escalation impact is weak.
- **Evidence:** `evidence/vendor-kernel-timerfd-cve-2017-10661.md`.

---

## C39 — an exact AF_UNIX GC gap is not an observed object lifetime failure

- **Candidate:** CVE-2021-0920 is a local AF_UNIX descriptor-passing race and
  recovered D-Bus use makes module load plausible.
- **Exact result:** both MSG_PEEK receive paths call exact `scm_fp_dup`, carry the
  result to `scm_recv`, and lack direct or indirect serialization on exact
  `.bss+0x102e` `unix_gc_lock` in that interval.
- **Conclusion:** V-025 establishes the missing-GC-barrier premise, not runtime
  module state, an overlapping GC candidate graph, UAF, corruption, root, or
  persistence.
- **Evidence:** `evidence/vendor-kernel-unix-peek-cve-2021-0920.md`.

---

## C38 — intended `/dev/ptmx` plus wrong locking is not a completed UAF

- **Candidate:** CVE-2020-29661 is an ordinary PTY race, and shipped startup
  intends a world-writable PTY multiplexer.
- **Exact result:** master and slave setters can release/replace the same slave
  pgrp PID reference while holding distinct master/slave `ctrl_lock` objects.
  Reciprocal PTY links and exact field offsets are independently bound.
- **Conclusion:** V-024 establishes the named race premise, not runtime PTY
  exposure, a winning interleaving, PID UAF, controlled reuse, root, or
  persistence.
- **Evidence:** `evidence/vendor-kernel-tty-pgrp-cve-2020-29661.md`.

---

## C37 — mremap flush ordering is an exact window, not demonstrated stale access

- **Candidate:** public CVE-2018-18281 describes stale old-address translations
  when `mremap` flushes only after dropping page-table locks.
- **Exact result:** ordinary PTE transfer clears source and writes destination,
  releases the same bound source/destination PTLs, and only later sets a flag
  that reaches exact old-range `flush_tlb_mm_range` at outer exit.
- **Conclusion:** V-023 retains the named code-level lifetime window. Concurrent
  invalidation, page release/reuse, stale access, corruption, root, and
  persistence remain unproved.
- **Evidence:** `evidence/vendor-kernel-mremap-cve-2018-18281.md`.

---

## C36 — vmacache is a live old-kernel candidate, not a banner inference

- **Candidate:** CVE-2018-17182 applies to an ordinary MMU/thread surface and
  public sources describe possible privilege gain, but a `4.1.27` string alone
  cannot establish a missing vendor backport.
- **Exact result:** both live invalidation paths perform 32-bit increments and
  call exact `vmacache_flush_all` on zero; its `mm_users==1` route returns
  without clearing pointers; lookup compares and stores only 32-bit
  generations. Exact `mmput` independently binds the user-count field.
- **Conclusion:** V-022 is exact pre-fix code, bounded by an unexecuted 2^32-state
  cycle and unproved stale-pointer survival, dereference, reuse, corruption,
  root, or persistence.
- **Evidence:** `evidence/vendor-kernel-vmacache-cve-2018-17182.md`.

---

## C41 — literal launcher paths do not constrain a runtime D-Bus QString

- **Was:** commit `3090f69` concluded the unverified AppLauncher route could only replace fixed binaries under read-only `/navi`, so it presupposed the privileged write it was proposed to obtain.
- **Now:** exact Request adaptor and vtable routing show exported `launch(appid, appname, applocation, ...)` methods pass the caller's runtime `applocation` to dispatcher `[0x1ffd0,0x205b3)`. That dispatcher overwrites program field `+0x58`, sets direct-launch byte `+0x1c`, and reaches a `QProcess::start` call site without either identified verifier call. A literal-string inventory cannot exclude data supplied as a QString argument.
- **Second correction:** the older public source also said failed verification does not stop launch. Exact ordinary and navigation branches both treat false as terminal; the defect is the separate dispatcher that bypasses both identified verifier calls.
- **Boundary:** the session bus defaults to the daemon's uid, not arbitrary cross-uid clients. Service ownership, Request-object registration, successful same-uid authentication, effective SMACK access, relevant AppProcess-object availability, control of executable bytes at exec time, QProcess acceptance, effective privilege retention, successful exec and resulting context remain unobserved. V-028 is an exact verifier-bypass-to-start-attempt candidate, not demonstrated unrestricted root or persistence.
- **Evidence:** `evidence/applauncher-dbus-launch-bypass.md` and `evidence/artifacts/application-candidates/applauncher-dbus-launch-evidence.txt`.

---

## Standing practice that produced these corrections

1. Cross-check a symbol table against an independent table before trusting names.
2. Disassemble a function before calling a decompiler artefact a vulnerability.
3. Compute an entropy maximum before calling entropy "low".
4. Treat a field report as evidence against a hypothesis, not just for it.
5. Record rejected hypotheses, not only accepted findings.

Items C8 and C9 were never vulnerabilities; they are kept here because a reader
who finds the earlier reasoning in a draft should know it was tested and failed.

#### From the parallel repository

The parallel lineage carries the same entries C1-C15 plus the standing-practice
tail, and stops there; C16 onward above are additions from this lineage. Its C4
entry is the only entry whose wording differs, and it is preserved verbatim.

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

<!-- disagreement: the parallel C4 says "the version gate is a single userland comparison" and that "three non-cryptographic obstacles remain (feed, target build, unconfirmed on 2026 packages)", while the newer C4 says "the documented userspace version gate is a string comparison" and lists "feed, target build, unconfirmed behavior on 2026 packages, and unaudited loader/fuse rollback policy". Both statements are kept; the newer caveat is a superset, but the parallel "single userland comparison" phrasing is retained because it is the stronger claim. -->

Note on lineage coverage: entries C16-C41 above (V-006 sanitizer boundaries,
`MS_NODEV`/Tuxera special nodes, Dirty COW and AF_PACKET backports, Stack Clash
guard gap, keyring, ALSA sequencer/timer follow-ups, ASF layout, BusyBox
provenance, TPACKET arithmetic, FUMO marker/mode/force-launch evidence, mq_notify,
USB-MIDI, SysV/socket/IPC, timerfd, AF_UNIX peek, PTY pgrp, mremap, vmacache and
the AppLauncher D-Bus route) exist only in this lineage and were added after the
parallel repository's last entry.
