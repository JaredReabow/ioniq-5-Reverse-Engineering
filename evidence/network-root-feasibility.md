# Can the network yield root? A config-filtered answer

Status: analysis of the exact kernel configuration and recovered symbol table.
No device was used. This exists because "Linux 4.1.27 is EOL, therefore it is
vulnerable" is true and also not the question that matters.

## The distinction

Having a CVE and having a **network-to-root path** are different claims. A remote
root requires all four of:

1. the defect is present in this build;
2. the affected code is **compiled in**;
3. it is reachable **before authentication**, over the network;
4. it yields **code execution**, not denial of service.

Most of the famous "Linux is vulnerable" list fails (2), (3) or (4).

## What is compiled out

From `work/eu-260128/kernel.config`, the following are absent entirely, which
removes a large fraction of the remote-RCE catalogue:

| Compounded out | Removes |
|---|---|
| `CONFIG_USER_NS` | essentially every modern netfilter/xtables LPE (they also need `CAP_NET_ADMIN`) |
| `CONFIG_NF_TABLES` | the whole `nf_tables` family (CVE-2022-1015, CVE-2023-32233, CVE-2021-22555-adjacent paths) |
| `CONFIG_BLUETOOTH` | the Bluetooth stack class, a rich remote-RCE source |
| `CONFIG_SCTP`, `CONFIG_DCCP` | SCTP/DCCP remote bugs (CVE-2017-6074 and relatives) |
| `CONFIG_RDS`, `CONFIG_TIPC`, `CONFIG_NFC` | further protocol families |
| `CONFIG_AX25`, `CONFIG_X25` | the classic amateur-radio remote overflow family |
| `CONFIG_INET_ESP`, `CONFIG_XFRM_USER` | xfrm/IPsec attack surface (CVE-2017-7184, CVE-2017-11600) |
| `CONFIG_TCP_MD5SIG` | MD5 signature parsing |
| `CONFIG_INET_DIAG` | the netlink diag family |
| `CONFIG_PACKET=m` | AF_PACKET exists but is a module (in the encrypted rootfs) and needs `CAP_NET_RAW` |

What remains pre-authenticated over the wire: **IPv4/IPv6 packet parsing, TCP,
UDP, ICMP, IP fragment reassembly, and netfilter hook evaluation**.

## What that leaves, CVE-wise

| CVE | Present in 4.1.27 by default | Reachability here | Impact |
|---|---|---|---|
| CVE-2019-11477/11478/11479 (SACK) | yes | any TCP peer | **DoS** |
| CVE-2018-5391 (FragmentSmack) | yes | crafted fragments | **DoS** |
| CVE-2016-7039/8666 (GRO recursion) | yes | crafted VLAN/tunnel packets | **DoS** (fixed 4.1.37) |
| CVE-2016-6828 (SACK `highest_sack` UAF) | yes | established connection | UAF; NVD classes it LOCAL |
| CVE-2017-18017 (`xt_TCPMSS` UAF) | yes | only if a `-j TCPMSS` rule is installed | UAF (fixed 4.1.43) |
| CVE-2016-5696 (challenge-ACK hijack) | **fixed here — see below** | off-path | hijack, not root |

Nothing in that list is an unauthenticated remote root.

## The vendor backports, and that breaks version-string reasoning

`sysctl_tcp_challenge_ack_limit` is present in the recovered symbol table. That
data symbol was introduced by the CVE-2016-5696 fix, which landed in **4.1.32** —
a release *after* this kernel's 4.1.27 base.

So this is **not** a pristine 4.1.27. The vendor cherry-picks selected network
fixes. Two consequences:

- "EOL in 2018, therefore every later CVE applies" is **wrong** for this build.
- Conversely, you cannot assume any given fix is present either. The only reliable
  method is per-fix verification against the binary or source.

Counter-example within the same check: the upstream GRO recursion helpers
(`gro_recursion_inc` / `gro_recursion_dec`) do **not** appear. They are `static
inline` in the upstream patch and could have been inlined away, so this is
suggestive rather than conclusive — exactly the kind of ambiguity that makes
version-matching unreliable and per-fix checks necessary.

Note also that `tcp_gso_segs` (the CVE-2019-11477 fix) is a **struct field**, not a
symbol, so its absence from `kallsyms` proves nothing. Recorded because it is an
easy false inference.

## The honest answer

- **Yes, the kernel certainly contains vulnerabilities.** It is a 2016 kernel base
  rebuilt in 2026 with at least one backport confirmed.
- **No, that does not produce a network root.** The reachable, compiled-in,
  unauthenticated surface yields denial of service and, in narrow conditions, two
  use-after-frees on established connections. Neither is a documented root path.
- **The kernel is not where this unit is weak.** The documented path to root is
  USB, via an application substitution gated by Engineering Mode.

## What would actually settle it

1. Decrypted rootfs → the installed iptables rules and sysctl values, which decide
   whether the `xt_TCPMSS` and netfilter paths are reachable at all.
2. Per-fix binary checks for the DoS fixes, so the crash surface is known rather
   than guessed.
3. `net_surface.py` against the live unit for the *userland* daemons, which remain
   the more promising remote surface (see `child-notes/06`).
