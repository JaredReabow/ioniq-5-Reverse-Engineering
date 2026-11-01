# Minimal retained kernel-candidate evidence

These are reviewable excerpts and authoritative upstream patches supporting the
2026-11-01 exact-binary assessments. Large firmware inputs and full disassembly
remain ignored under `work/`.

## Inputs and tools

- recovered `vmlinux` SHA-256:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`;
- recovered `snd-seq.ko` SHA-256:
  `ccc802452bb4ac4527d2def96ddef463211c03ae2c07d9003fdc7ebed9eb091d`;
- recovered `snd-pcm.ko` SHA-256:
  `9a1f126d6919812d3e7c6d7c9def51a698564cdfb22b9ebc72022c6e87d19fb9`;
- recovered `af_packet.ko` SHA-256:
  `c810265b3c22f95d2b90494cc206abd6b4e67b7710bff2adcb177ee4867f467b`;
- recovered `snd-usbmidi-lib.ko` SHA-256:
  `ad2180bab3d7433287288c9b8255c8f70cefb6d4ee3c6b7d95ea4826d4b434be`;
- disassembler: Homebrew LLVM `llvm-objdump` 23.1.3, Intel syntax;
- source module path:
  `work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/core/seq/snd-seq.ko`;
- source PCM module path:
  `work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/core/snd-pcm.ko`;
- source packet module path:
  `work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/net/packet/af_packet.ko`;
- source USB-MIDI module path:
  `work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/usb/snd-usbmidi-lib.ko`;
- source kernel path: `work/eu-260128/vmlinux`.

`kernel-keystore-secure-boot-ignore.asm` retains complete exact ranges for
`keystore_init`, `keystore_register`, `manifest_init`, `verify_oem_signature`,
`manifest_key_verify_digest`, `get_apl_manifest_offsets`, `__class_create`, and
the relevant `device_create` wrappers. It establishes
that the configured IGNORE option removes a keystore status prerequisite but
leaves the manifest/signature chain intact. It also retains the parser length
mismatch and interior-pointer cleanup supporting conditional boot-time OOB-read
and invalid-free candidates, plus the class/device ERR_PTR call chain.

The ALSA files retain complete disassemblies of the relevant module functions. The other kernel files retain only the branches needed to review the
claims. They were generated with commands equivalent to:

```sh
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff814cd140 --stop-address=0xffffffff814cd305 \
  work/eu-260128/vmlinux > kernel-ipv4-ufo-branch.asm
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff8151cd2a --stop-address=0xffffffff8151cf25 \
  work/eu-260128/vmlinux > kernel-ipv6-ufo-branch.asm
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff811b6496 --stop-address=0xffffffff811b64fb \
  work/eu-260128/vmlinux > kernel-join-session-keyring-branch.asm
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff811b1694 --stop-address=0xffffffff811b1709 \
  work/eu-260128/vmlinux
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff811b1892 --stop-address=0xffffffff811b18b1 \
  work/eu-260128/vmlinux
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff814a8d51 --stop-address=0xffffffff814a8d70 \
  work/eu-260128/vmlinux
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff81475c1d --stop-address=0xffffffff81475e13 \
  work/eu-260128/vmlinux
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff814d22f5 --stop-address=0xffffffff814d23ab \
  work/eu-260128/vmlinux
llvm-objdump -d --x86-asm-syntax=intel \
  --start-address=0xffffffff811aa199 --stop-address=0xffffffff811aa294 \
  work/eu-260128/vmlinux
llvm-objdump -dr --x86-asm-syntax=intel \
  --start-address=0xc6c --stop-address=0xe7e \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/core/snd-pcm.ko \
  > snd-pcm-control-ioctl.asm
llvm-objdump -dr --x86-asm-syntax=intel \
  --start-address=0x3e8f --stop-address=0x3f1f \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/core/snd-pcm.ko \
  > snd-pcm-release.asm
llvm-objdump -dr --x86-asm-syntax=intel \
  --start-address=0x1621 --stop-address=0x174e \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/core/seq/snd-seq.ko \
  > snd-seq-do-ioctl.asm
llvm-objdump -dr --x86-asm-syntax=intel \
  --start-address=0x174e --stop-address=0x188d \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/core/seq/snd-seq.ko \
  > snd-seq-create-client.asm
llvm-objdump -dr --x86-asm-syntax=intel \
  --start-address=0x2293 --stop-address=0x23b8 \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/core/seq/snd-seq.ko \
  > snd-seq-set-client-pool.asm
llvm-objdump -dr --x86-asm-syntax=intel \
  --start-address=0x2084 --stop-address=0x20d2 \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/net/packet/af_packet.ko \
  > af-packet-cve-2017-7308.asm
llvm-objdump -dr --x86-asm-syntax=intel \
  --start-address=0x2034 --stop-address=0x2893 \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/sound/usb/snd-usbmidi-lib.ko
```

The `cve-*.patch` files are GitHub patch representations of these upstream
commits:

- CVE-2015-1805 legacy introduction/context:
  `f6762b7ad8edd6abc802542ce845d3bc8adcb92f`; read-side iterator conversion:
  `637b58c2887e5e57850865839cc75f59184b23d1`; write-side iterator conversion:
  `f0d1bec9d58d4c038d0ac958c9af82be6eb18045`;
- CVE-2015-7550: `b4a1b4f5047e4f54e194681125c74c0aa64d637d`;
- CVE-2015-7613: `b9a532277938798b53178d5a66af6e2915cb27cf`;
- CVE-2016-0728: `23567fd052a9abb6d67fe8e7a9ccdd9800a540f2`;
- CVE-2016-2544: `3567eb6af614dac436c4b16a8d426f9faed639b3`;
- CVE-2016-2545: `ee8413b01045c74340aa13ad5bdf905de32be736`;
- CVE-2016-2546: `af368027a49a751d6ff4ee9e3f9961f35bb4fede`;
- CVE-2016-2547/2548: `b5a663aa426f4884c71cd8580adae73f33570f0d`;
- CVE-2016-2549: `2ba1fe7a06d3624f9a7586d672b55f08f7c670f3`;
- CVE-2016-4569: `cec8f96e49d9be372fdb0c3836dcf31ec71e457e`;
- CVE-2016-4578: `9a47e9cff994f37f7f0dbd9ae23740d0f64f9fe6`,
  `e4ec8cc8039a7063e24204299b462bd1383184a5`, and completeness follow-up
  `a8c006aafead3c45ae5d5601e3717055bccf41bc`;
- CVE-2016-2384: `07d86ca93db7e5cdf4743564d98292042ec21af7`;
- CVE-2016-4997: `ce683e5f9d045e5d67d1312a42b359cb2ab2a13c`, with related compat-validation fix `09d9686047dbbe1cf4faa558d3ecc4aae2046054`;
- CVE-2016-7117: `34b88a68f26a75e4fded796f1a49c40f82234b7d`;
- CVE-2016-7910: `77da160530dd1dc94f6ae15a981f24e5f0021e84`;
- CVE-2016-7911: `8ba8682107ee2ca3347354e018865d8e1967c5f4`;
- CVE-2016-7914: `8d4a2ec1e0b41b0cf9a0c5cd4511da7f8e4f3de2`;
- CVE-2018-14634: `da029c11e6b12f321f36dac8771e833b65cec962`;
- CVE-2017-8890: `657831ffc38e30092a2d5f03d385d710eb88b09a`;
- CVE-2017-9242: `232cd35d0804cc241eb887bb8d4d9b3b9881c64a`;
- CVE-2017-11176: `f991af3daabaecff34684fd51fac80319d1baad1`;
- CVE-2017-7533: `49d31c2f389acfe83417083e1208422b4091cd9e`;
- CVE-2017-7184: `677e806da4d916052585301785d847c3b3e6186a`, with required
  follow-up `f843ee6dd019bcece3e74e76ad9df0155655d0df`;
- CVE-2017-6074 mainline: `5edabca9d4cff7f1f2b68f0bac55ef99d9798ba4`;
  stable 4.1.y backport: `98442999b9671784e659b205be8b5b6be8e81629`;
- CVE-2017-10661: `1e38da300e1e395a15048b0af1e5305bd91402f6`;
- CVE-2018-17182: `7a9cdebdcc17e426fb5287e4a82db1dfe86339b2`;
- CVE-2018-18281: `eb66ae030829605d61fbef1909ce310e29f78821`;
- CVE-2020-29660: `c8bcd9c5be24fb9e6132e97da5a35e55a83e36b9`;
- CVE-2020-29661: `54ffccbf053b5b6ca4f6e45094b942fab92a25fc`;
- CVE-2021-0920: `cbcf01128d0a92e131bd09f1688fe032480b65ca`;
- CVE-2017-1000112: `85f1bd9a7b5a79d5baa8bf44af19658f7bf77bfa`;
- CVE-2017-16995: `95a762e2c8c942780948091f8f2a4f32fce1ac6f`;
- CVE-2017-0861: `362bca57f5d78220f8b5907b875961af9436e229`;
- CVE-2017-15265: `71105998845fb012937332fe2e806d443c09e026`;
- CVE-2018-1000004 mainline: `b3defb791b26ea0683a93a4f49c77ec45ec96f10`;
- CVE-2018-1000004 Linux 4.1 stable equivalent:
  `f8a38ab4cd9624fc5ac8a7f965c7b20f5b62c03c`.

The CVE-2017-7308 comparison additionally uses ignored GitHub patch captures
under `work/online-kernel-candidates-20261101/cve-2017-7308/`:

- primary private-area fix `2b6867c2ce76c596676bec7d2d525af525fdc6e2`,
  patch SHA-256
  `a2a31d146687d372bdbe3b40d3a04bf46d544a0d15901664b2ed2130b243a474`;
- companion frame-count fix `8f8d28e4d6d815a391285e121c3a53a0b6cb9e7b`,
  patch SHA-256
  `3e84b1acd9dd82dd0aedbb2ef301ce181993a2f68e106d1e3117d4608571b340`.

`kernel-af-packet-frame-count.asm` retains complete module-relative FDEs for
`free_pg_vec`, `packet_mmap`, `packet_lookup_frame`, `packet_rcv_has_room`, `packet_poll`,
`packet_set_ring`, `tpacket_rcv`, and `packet_sendmsg`, plus absolute-vmlinux
FDEs for `vm_insert_page`, `__get_order`, `__kmalloc`, `kmalloc_order`,
`alloc_kmem_pages`, `__alloc_pages_nodemask`, `get_page_from_freelist`, and
`__rmqueue` in a separately labeled address namespace. It binds the formerly
unresolved wrapped-frame-count producer to all V1/V2 address-sensitive consumers,
the mmap boundary rejection, and exact rejection of every vector large enough
to reach a negative signed index. SHA-256:
`f7097d97fc2e29671673aa67c0cd34df7241e60e0fb49d6d782376fca37d9994`.

`kernel-netlink-cve-2016-9806.asm` retains complete embedded-kallsyms-bounded
`netlink_dump` machine code. It binds callback-mutex ownership, pre-unlock
capture of `cb->module` and `cb->skb`, `cb_running` clear, unlock, and exact
post-unlock `module_put`/`consume_skb` use of the saved registers. These effects
reject the CVE-specific mutable-callback cleanup race. SHA-256:
`5c6e5e86076843d7844cde807f58dc3e74294749be962642ac3198597055d9ab`.
`cve-2016-9806-fix.patch` is upstream commit
`92964c79b357efd980812c4de5c1fd2ec8bb5520`; SHA-256:
`89638f347ae53c86e2d346da8422ac3e33251fc25230c071376a4874a2d41680`.

`kernel-block-cve-2016-7910.asm` retains complete embedded-kallsyms-bounded
`disk_seqf_next`, `disk_seqf_start`, and `disk_seqf_stop` machine code. It binds
the successful iterator store and allocation-failure edge to `seq_file.private`
at offset `0x78`, then shows exact iterator exit/free followed by a pointer-width
zero store to the same owner field. That is the same cleanup-side effect as the
upstream fix and rejects the CVE-specific stale cleanup premise; the stripped
binary does not establish commit provenance. SHA-256:
`466a6c195ec3bfad9367da414716633be9e5fb7ef524a25a5555ebd56094f7d4`.
`cve-2016-7910-fix.patch` is upstream commit
`77da160530dd1dc94f6ae15a981f24e5f0021e84`; SHA-256:
`701c7be0854836b8c7f2f4ff21e8e3d4a932809c2d32fe572215bdd5b03bcff0`.

`kernel-netfilter-compat-cve-2016-4997.asm` retains complete
`sys_ni_syscall` machine code and authoritative-map identities for its weak
`compat_sys_setsockopt` alias plus native IPv4/IPv6 iptables control routines.
The compat alias returns `-ENOSYS`; configuration and the full map have no
compiled compat iptables translation path. SHA-256:
`3f548b2cdac454999d919b8f1d88a696810ee1bbbfa94693fc6060f8214a75f9`.
The primary and related patches have SHA-256
`4a30140d96c857a4cebf0ccdfd6e7a4b80d1d0aed01c002af8a490d33f7afec0`
and `b42c9a22f04883903c3a8b9f86efe22dc4b790c95e8f1a1d83ab8053fabaadd7`.

`kernel-bpf-syscall-cve-2017-16995.asm` retains the exact configuration,
complete `sys_ni_syscall` range, weak `sys_bpf` alias, and native x86-64
syscall-table slot binding. `CONFIG_BPF_SYSCALL` is disabled and native slot
321 points to the stub that returns `-ENOSYS`. Contrary classic-BPF and
interpreter/runtime symbols are retained, so the result rejects only the named
syscall-based eBPF verifier path and is not a general BPF safety or absence
claim. SHA-256:
`e36aa175a3ea5cc7083d30d2e2970d90613409cad2177249e6eeed1a05eaf98f`.
`cve-2017-16995-fix.patch` is upstream commit
`95a762e2c8c942780948091f8f2a4f32fce1ac6f`; SHA-256:
`d09d5733423b14add9cb9d9a25487a088cba449d1ca5c614b55dad307f73f557`.

`kernel-xfrm-user-cve-2017-7184.asm` retains the exact configuration and
complete `xfrm_init_replay` range, the complete eight-name XFRM-user query
inventory, contrary XFRM-core symbols, and a direct member inventory of the
canonical decrypted stock archive (SHA-256
`423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`):
163 regular `.ko` members, no `xfrm_user.ko` or `af_key.ko`, and exactly three
XFRM-named IPv6 mode modules. `CONFIG_XFRM_USER` is disabled, so the assessment
rejects CVE-2017-7184 only for the named
`XFRM_MSG_NEWAE -> xfrm_new_ae` path. `CONFIG_XFRM=y` and state/policy/replay
machinery remain, preventing a whole-XFRM absence or safety claim. Artifact
SHA-256: `9ea9205be67b246aff6d88be2d5b00f3d022cec60a686dcf6a010974136fd34e`.
Public history identifies introducing commit
`d8647b79c3b7e223ac051439d165bc8e7bbb832f` and historical incomplete verifier
commit `e2b19125e94124daaeda1ddcf9b85b04575ad86f`. The retained initial and
required follow-up patches are mainline commits
`677e806da4d916052585301785d847c3b3e6186a` and
`f843ee6dd019bcece3e74e76ad9df0155655d0df`; their official stable 4.1.y
backports are `438db92d7f2792e3bad17be70e6edf0f44a081f0` and
`171a957989c4f398adb41078dbfff73b0821e383`, both first in Linux 4.1.49
(22 January 2018). Version history is contextual; exact absent-path evidence
controls, and verifier presence alone is not remediation. Both fix effects or
exact equivalents would be required if the path existed. Retained mainline-fix
patch SHA-256 values are
`5d419e4862b608a9372f4c93bf27c9a3014fe6598d38f148fa8eeea71fab905e`
and `3e0699ff6c4811470a4007bdb7bff86a72b12ddad739d01a3cc135e3b17ccd75`.
Exact local public-history captures are also retained: introducing patch
`64bccd3fe44942e8b100dd66b9e43c73aed1ebb6b809db868a5e41c046a73581`;
historical-verifier patch
`88a0a46c099de374e5ca19f5a44ca8d1aaa4e1c08538d71471bdaf2375f56d6a`;
stable initial/follow-up patches
`a764b411fcbaa2db8d8ea7420a38d88749dac82f7a17b2b24d997e65485f9232`
and `de91f9ab7bc874defccec57c723740eadfc7f55923dc279a26c0ef0118da92e1`;
Linux 4.1.49 release patch
`344a344b15c2a05330399ce4694a82876765db1031eb1f7a7d700cd9de366963`;
and reviewed official-changelog excerpts with public maintainer email addresses
redacted
`f3623a119582dfe97f9132560f640763abd0c8324545762a74ef0449a421fdcb`.

`kernel-dccp-cve-2017-6074.txt` retains the exact configuration, public v4.1
Kconfig/Kbuild excerpts, complete ten-name zero-row query declaration/results,
and direct member inventory of the canonical decrypted stock archive (SHA-256
`423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`):
163 regular `.ko` members and zero names containing `dccp`. The specific public
CVE path requires DCCP core plus DCCPv6/IPv6. Under applicable public v4.1 rules,
`CONFIG_IP_DCCP=n` excludes that whole named subtree, and the archive ships no
canonical DCCP core or DCCPv6 module. `CONFIG_INET=y` and `CONFIG_IPV6=y`
prevent a general networking or IPv6 absence/safety claim; IPv4-only DCCP would
not establish the CVE path, and USER_NS is non-decisive. Mainline commit
`5edabca9d4cff7f1f2b68f0bac55ef99d9798ba4` and stable 4.1.y backport
`98442999b9671784e659b205be8b5b6be8e81629` are retained byte-identically with
patch SHA-256 values
`e5ac35f2d2b4129e3fca80a5b7d9200035bfd79f703b3045d7b28c9868179eb9` and
`116e4a0d21907c0271cd76e45c2fda40c9c349ef8d0cb59184aba23bcc573c9c`.
The retained official `ChangeLog-4.1.41` release commit/date records 15 June
2017, not 18 March; no separate archive-index claim is retained. Version
history is contextual, and no fix provenance/effect, installed identity,
runtime behavior, corruption, root, or persistence is claimed. Artifact
SHA-256: `79b75516533d8a1a382f2c49cd8186d9c4329d19c5b58318711d38a420a9effc`.

`kernel-pipe-cve-2015-1805.asm` retains complete authoritative-map-successor-
bounded `pipe_write`, `pipe_read`, `copy_page_from_iter`, and
`copy_page_to_iter` machine code. It binds both write copy sites and the read
copy site directly to exact iterator helpers; each helper clamps against
iterator count, traverses fixed 16-byte descriptors, accounts only
requested-minus-residual progress across atomic and fallback stages, and commits
iterator offset/count/descriptor/segment state without storing to descriptor
base/length fields. These effects reject the legacy mutable-iovec fallback
required by CVE-2015-1805 for the exact recovered kernel. Exact-name absence of
the two old pipe-local helpers is bounded corroboration only. Ordinary local
pipe functionality remains compiled; this is not a general pipe/iterator safety
or installed-device claim. Artifact SHA-256:
`e79391d6592ce772f18cf02d97cdbba00e58b68ec8340e67409840470bfff552`.
The introducing, read-conversion, and write-conversion patch SHA-256 values are
`ad43bba30d7d3be2e15c17b605f6d17d92f17fa3ebb239bd2bdc457b10746aec`,
`d44d40a61f9746ec3a8fd2ab6c88f74f0ce09617786ac27f59174effbabaeb5c`,
and `c5966a0a700deb343e5599a716fb116988a85238134099925ced6fda3524340a`.

`kernel-key-read-revoke-cve-2015-7550.asm` retains complete
embedded-kallsyms-bounded `key_revoke`, `keyctl_revoke_key`,
`keyctl_read_key`, and `key_validate` machine code. The reader takes
`key + 0x20` for reading before validation and retains it through the read
callback; revoke takes the same rwsem for writing across revoked-state mutation
and the revoke callback. These effects reject the CVE-specific unlocked
validation-to-read race. SHA-256:
`8dfaf1486bf070d154ac02d1f818ef9193f8a0f16ff9fdc4c72af39f1434ba6e`.
`cve-2015-7550-fix.patch` is upstream commit
`b4a1b4f5047e4f54e194681125c74c0aa64d637d`; SHA-256:
`e2576be983a765c1a462fe9d90bcfcedf9fc076def125ffa94937513e264d7cc`.

`kernel-tty-ldisc-cve-2016-0723.asm` retains complete exact
`tty_ioctl`, `tty_ldisc_ref_wait`, `tty_ldisc_ref`, `tty_ldisc_deref`,
`__put_user_4`, and shared user-copy-error ranges. It binds command `0x5424` to
waited line-discipline acquisition, post-acquisition `ops->num` loads, the
four-byte user copy, and unconditional same-object dereference before return,
including copy error. The complete helpers bind `ldsem_down_read`,
`ldsem_down_read_trylock`, and `ldsem_up_read`. These effects reject only the
CVE-2016-0723 unlocked-dereference premise and do not establish broad TTY safety
or commit provenance. SHA-256:
`358b8e8b4402841fcfc834a2ad23535274b0cd2804114fd78d6c70d5bac903cb`.
`cve-2016-0723-fix.patch` is upstream commit
`5c17c861a357e9458001f021a7afa7aab9937439`; SHA-256:
`b99eb5238c54e8d49834ef225761ded17ebf0d130ea11ea3e4206bad619586c1`.

`kernel-ioprio-cve-2016-7911.asm` retains complete embedded-kallsyms-bounded
`get_task_ioprio`, `SyS_ioprio_get`, and `exit_io_context` machine code. Getter
and exit paths use the same `task + 0x630` lock around the `task + 0x678`
I/O-context pointer; priority is read at `io_context + 0x12` before unlock, and
exit clears the pointer before unlocking and releasing the object. These effects
reject the CVE-specific unlocked UAF-read premise. SHA-256:
`c2ad1649793759124b1f65553194727cc39082a09c4d7c1f2ca82b41a76641d7`.
`cve-2016-7911-fix.patch` is upstream commit
`8ba8682107ee2ca3347354e018865d8e1967c5f4`; SHA-256:
`35c7a6a530095ed0424987d820e46db341a250820ed88ce1b1a89ec30acabd67`.

`kernel-sock-buffer-force-cve-2016-9793.asm` retains complete
embedded-kallsyms-bounded `sock_setsockopt` machine code. Both forced buffer
routes gate on exact `capable(CAP_NET_ADMIN)`, then join send/receive sequences
that double the input-derived value, use signed `cmovle` minimum selection, and
store only after that clamp. These effects reject the CVE-specific negative
socket-buffer premise. SHA-256:
`3911ee771afb2f215013d3bdef4ef93ed2e7fd4b08b96a08d8cb1ebb7433c5df`.
`cve-2016-9793-fix.patch` is upstream commit
`b98b0bc8c431e3ceb4b26b0dfc8db509518fb290`; SHA-256:
`620453e77616829f5c311793f02ae9f519dcedcbcda757c4878727e47fe42876`.

`kernel-assoc-array-cve-2016-7914.asm` retains complete embedded-kallsyms-bounded
`assoc_array_insert` and `__key_link_begin` machine code. In the inlined
terminal-node loop, metadata-tagged node/shortcut slots branch around the
`ops->compare_object` callback; only non-null leaf-tag fallthrough reaches it,
and the loop covers all 16 slots. These effects reject the CVE-specific nonleaf
callback premise. SHA-256:
`382b2a7b6083ebfabfd65cc3fd0c3da11999d190708df69156e7bb6f4ec0386c`.
`cve-2016-7914-fix.patch` is upstream commit
`8d4a2ec1e0b41b0cf9a0c5cd4511da7f8e4f3de2`; SHA-256:
`6ad914e07cb0cab1d3e6826119287553b5e96356f2b4a4366d8e73b7cc18c481`.

`kernel-exec-arg-cap-cve-2018-14634.asm` retains complete
embedded-kallsyms-bounded `copy_strings` machine code. It preserves `ARG_MAX`,
then accepts larger argument space only at or below the exact minimum of one quarter
of the stack rlimit and six MiB; oversize state releases the page and returns
through `-E2BIG`. These effects reject the CVE-specific oversized initial-stack
prerequisite. SHA-256:
`b240d2a93833c9e000ffa19edb5ddf52bbc523af6645ea57f7c9dd208a86e4c4`.
`cve-2018-14634-fix.patch` is upstream preventive commit
`da029c11e6b12f321f36dac8771e833b65cec962`; SHA-256:
`b2bd9af42ba1ada88463ecd5f19c70e9b1b6a789c3a0912f9baf54106c49d724`.

`kernel-perf-cve-2017-6001.asm` retains complete absolute-vmlinux FDEs for
`perf_event_ctx_lock_nested.isra.60` and `SYSC_perf_event_open`. The former
shows the compiled reference/lock/identity/retry discipline; the affected
move-group path loads its group context before the double-mutex wait and omits
those effects and post-lock move-state revalidation. SHA-256:
`6f171c2c89ed13f641f4a5084fd40a90d23f7deeb644a00de8c5eed1a1ef6863`.
`cve-2017-6001-fix.patch` is upstream commit
`321027c1fe77f892f4ea07846aeae08cefbbb290`; SHA-256:
`3349b60feb8808444a3905369e4d4d7660690f2223c6b8e3cbabb9b0e7c6be99`.

`kernel-inotify-cve-2017-7533.asm` binds snapshot dominance around exact parent
and rename notification paths, short-name copying under the dentry lock,
external-name reference retention/release, and the stable pointer passed to the
separate inotify length/copy operations. These exact effects reject the
CVE-2017-7533 mutable-name premise despite the old kernel version banner.

`kernel-ipv6-cve-2017-9242.asm` binds ordinary UDPv6 call flow, skb allocation,
the fraggap copy/trim, later signed copy calculation, and post-copy error
cleanup underlying V-029. The companion `-full.asm` and `-wrapper.asm` files
retain branch-complete evidence for absence of an equivalent early rejection
and exact wrapper-to-internal-function routing.

`kernel-timerfd-cve-2017-10661.asm` binds same-file context identity,
membership/list fields, narrow global locking, later waitqueue locking, and the
absent fixed per-context critical region underlying V-026.

`kernel-unix-peek-cve-2021-0920.asm` binds both MSG_PEEK branches, attached-file
`scm_fp_dup` calls, SCM-cookie continuity, exact global GC-lock identity, and
absence of a direct or indirect barrier underlying V-025.

`kernel-tty-pgrp-cve-2020-29661.asm` binds target/real TTY identities,
reciprocal UNIX98 PTY links, exact pgrp/lock offsets, and same-field updates
under distinct master/slave locks underlying V-024.

`kernel-tty-session-cve-2020-29660.asm` binds `TIOCGSID` dispatch, the unlocked
session null-test/reload/dereference sequence, two same-field writer lifetime
transitions, and exact `pid_vnr` object dereferences underlying V-027.

`kernel-mremap-cve-2018-18281.asm` binds ordinary PTE transfer, exact
source/destination PTL acquisition and release, deferred-flush state, and the
old-range `flush_tlb_mm_range` call underlying V-023.

`kernel-vmacache-cve-2018-17182.asm` retains both live 32-bit invalidation
edges, exact zero-wrap calls, the single-user no-clear flush route, independent
`mmput` user-count binding, and 32-bit lookup generation effects underlying
V-022.

`kernel-cve-2018-9568-exact-static.asm` retains complete authoritative-map-
successor-bounded allocation, clone, immediate/deferred free, TCP
post-clone-cleanup, protocol conversion, disconnect/listen, IPv6 creation, and
TCP child-clone functions. Exact `sk_clone_lock` allocates through source
`sk_prot`. Its second copy spans `[0x78,obj_size)`; raw descriptor `+0x100`
values are `0x780` for `tcp_prot` and `0x840` for `tcpv6_prot`, yielding copy
lengths `0x708` and `0x7c8`. The creator qword is only `0x128..0x12f` bytes
from that copy start, so the span necessarily includes all of source/clone
`+0x1a0..+0x1a7`. The function completes this sole creator-overwriting copy at
`0xffffffff8147884e`, then stores source `sk_prot` to clone `sk_prot_creator` at
`0xffffffff81478867`. Normal control between those points is linear through the
reviewed configured/default LSM clone callback, bound by exact
`security_fixup_ops` to a complete no-op callback. Both failure decisions
feeding the sole in-function post-copy `sk_free` follow the store; that cleanup
returns null, while all non-null returns and every later caller cleanup follow
the corrected return. Exact final free loads the corrected creator and its slab
pointer as the cache argument. The direct fix-shaped effect rejects
CVE-2018-9568's wrong-cache free mechanism for the
exact recovered kernel even though `IPV6_ADDRFORM` divergence and the TCP clone
route are compiled. Artifact SHA-256:
`e876c4eddfc08de17ded57371c447a93c44a44031265c34fb5ffa1decb253273`.
The reviewed mainline and 4.1.y public patches remain only in canonical ignored
`work/online-kernel-candidates-20261107/cve-2018-9568/` because their
byte-identical bodies contain an operational trigger program. The complete
public-reference bindings are mainline commit
`9d538fa60bad4f7b23193c89e843797a1cf71ef3`, parent
`b32ca44a88def4bf92626d8777494c6f14638c42`, patch SHA-256
`c1f7389124f499cc764ce39a25f841bc701f0d3e8e4ab6a86f3c578941ed085d`;
and stable commit `0a11ea32304f6ad6daf5589b6626775b7f00015c`, parent
`cafd2b53da565ca30c48a146635c95d385d83b81`, patch SHA-256
`756c9749346bda510e242b02b849448418196bc1f95684dbcbbf362eff60d8ba`.
Both corresponding 20261102 analysis patches pass byte-for-byte `cmp` against
the canonical files and independently produce those same authoritative hashes;
that directory is analytical/disassembly workspace, not canonical patch
provenance.

`kernel-sysvipc-cve-2015-7613.asm`,
`kernel-recvmmsg-cve-2016-7117.asm`, and
`kernel-inet-csk-cve-2017-8890.asm` retain the initialization/publication,
socket-release, and multicast-child field effects needed to reject those three
version-derived local-kernel candidates.

`snd-timer-2016-backports.asm` retains the list initialization, per-user ioctl
mutex, slave-active singleton lock, timer lock, and complete ack/active unlink
effects needed to reject CVE-2016-2545 through CVE-2016-2548 for exact
`snd-timer.ko`.

`snd-seq-queue-cve-2016-2544.asm` retains the queue timer-mutex region around
stop and close. `snd-timer-padding-cve-2016-4569-4578.asm` retains the complete
32-byte queue/read copies, fixed params/general-callback initialization, and
unfixed timer-interrupt padding paths underlying V-021.

`snd-usbmidi-cve-2016-2384.asm` retains raw-MIDI ownership assignment,
post-registration endpoint-failure branches, direct error returns, and the
owner's legitimate private-free callback. The absence of the second cleanup
after ownership transfer matches the upstream fix.

`mq-notify-cve-2017-11176.asm` retains the return-one retry, failed-lookup
cleanup, detach cleanup, and callee reference-release branches needed to review
the semantic backport. The missing explicit register clear is not treated as a
missing fix: exact failed-retry branches bypass detach, which is equivalent to
the source-level `sock = NULL` assignment.

`alsa-seq-probe-result.json` is the retained machine-readable benign reachability
result. It contains no firmware binary, proprietary module, credential, payload,
or personal identifier.
