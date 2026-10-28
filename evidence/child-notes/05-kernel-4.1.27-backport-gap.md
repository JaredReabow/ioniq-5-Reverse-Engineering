# 05 — Linux 4.1.27 backport-gap triage (4.1.28 → 4.1.52 and later LTS)

Subject: x86-64 Linux 4.1.27, vendor localversion `-abl`, built Jan 2026.
Config: `CONFIG_USER_NS=n`, `CONFIG_MODULE_SIG=n`, `CONFIG_RANDOMIZE_BASE=n`,
SMEP=y, SMAP=y, netfilter/iptables/NAT, IPv6, CAN, **no** DCCP/SCTP/Bluetooth.

Scope boundary: triage only. No exploit code, no payloads, no device contact.

---

## (a) Method

Exact sources used:

1. Stable changelogs (download as raw text):
   `https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.28`
   … through …
   `https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.52`
   (25 files, ~4.9 MB total, cached under `work/kernel-4.1-changelogs/`).
   These are the authoritative "what landed in the 4.1 longterm tail" source.

2. NVD 2.0 API, one CVE at a time:
   `https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-XXXX-YYYY`
   (raw JSON cached under `work/nvd.json` and `work/nvd2.json`).
   Used to obtain the description / affected-version / CVSS for every CVE
   id found in the changelogs plus a curated list of network-relevant CVEs.

3. MITRE CVE records for cross-checking the description text:
   `https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-XXXX-YYYY`

4. Method steps:
   - `grep -hoiE 'CVE-[0-9]{4}-[0-9]+' ChangeLog-4.1.*` → 46 distinct CVE ids
     that are explicitly cited in the 4.1.28–4.1.52 changelogs.
   - Map each CVE id back to the ChangeLog file(s) that cite it.
   - Keyword sweep of the changelogs for SACK / fragment / IPv6 frag /
     netfilter / xt_ / UFO / GRO / challenge-ACK / gup / COW to catch fixes
     that were backported **without** a CVE tag (several were).
   - Query NVD for those 46 ids plus the known post-EOL network CVEs
     (SACK trio, SegmentSmack/FragmentSmack, UDP frag, AF_PACKET) to decide
     which "apply to 4.1.27-era code" but were **never** backported to 4.1.

Key timeline facts established from the changelog headers:
- `Linux 4.1.28` = 2016-07-13 (Sasha Levin).
- `Linux 4.1.52` = 2018-05-27 (Sasha Levin) — **final 4.1 release; the branch
  went EOL here.** Nothing after 2018-05-27 was ever backported to 4.1.

---

## (b) Triage table

Legend:
- **Reachability**: `NET` = triggerable by a remote peer sending packets (no
  local code execution); `NET*` = remote packet but requires a specific
  firewall/tunnel configuration that a privileged admin installed; `LOCAL` =
  needs a process running on the unit; `N/A` = not applicable to this config.
- **Privilege**: what the *attacker* needs. `none` = unprivileged/anon.
  `CAP_NET_RAW`, `CAP_NET_ADMIN`, `root` as marked.
- "Fixed-in 4.1.x" = the version where the fix is present in the changelog.
  "—" = never backported to 4.1 (post-EOL), so the 4.1.27-era code is exposed.

### Network / TCP-IP-stack focus (task item 1, 2, 3)

| CVE | Subsystem | Fixed-in 4.1.x | Else fixed-in (later LTS) | Reachability | Privilege | 4.1.x ChangeLog evidence |
|---|---|---|---|---|---|---|
| CVE-2019-11477 | TCP SACK `tcp_gso_segs` integer overflow (SACK panic) | — | 4.4.182 / 4.9.182 / 4.14.127 / 4.19.52 / 5.1.11 | NET (any TCP conn, SACK on by default) | none | not in 4.1 (EOL 2018-05-27; CVE fixed 2019-06) |
| CVE-2019-11478 | TCP SACK `tcp_fragment` retransmit-queue fragmentation | — | 4.4.182 / 4.9.182 / 4.14.127 / 4.19.52 / 5.1.11 | NET (crafted SACK sequence) | none | not in 4.1 |
| CVE-2019-11479 | TCP SACK / hard-coded 48-byte MSS resource exhaustion | — | 4.4.182 / 4.9.182 / 4.14.127 / 4.19.52 / 5.1.11 | NET (low-MSS peer) | none | not in 4.1 |
| CVE-2018-5391 | "FragmentSmack" — IP fragment reassembly DoS (3.9+) | — | 4.9.120 / 4.14.63 / 4.17.14 / 4.18.6 | NET (low-rate crafted IP fragments) | none | not in 4.1 |
| CVE-2018-5390 | "SegmentSmack" — `tcp_collapse_ofo_queue`/`tcp_prune_ofo_queue` DoS | — | 4.9.120 / 4.14.63 / 4.17.14 / 4.18.6 | NET per NVD but NVD scopes it "4.9+" | none | not in 4.1; **likely N/A to 4.1** (see uncertainty) |
| CVE-2016-7039 | GRO unbounded recursion → stack overflow / panic (VLAN-only or tunnel-stacked packets) | **4.1.37** | (4.8.3 upstream) | NET (crafted VLAN/GRE/tunnel packets) | none | 4.1.37 "net: add recursion limit to GRO" |
| CVE-2016-8666 | GRO tunnel-stacking stack consumption (related to 7039) | **4.1.37** (same patch) | — | NET (interleaved IPv4/GRE headers) | none | same GRO recursion-limit commit in 4.1.37 |
| CVE-2017-18017 | `xt_TCPMSS` `tcpmss_mangle_packet` use-after-free | **4.1.43** | (4.11 / 4.9.36 upstream) | NET* (packet must traverse an installed `-j TCPMSS` rule) | none (rule installed by admin) | 4.1.43 "netfilter: xt_TCPMSS: add more sanity tests on tcph->doff" (upstream 2638fd0f92d4) |
| CVE-2016-6828 | TCP SACK `highest_sack` stale pointer / use-after-free in `tcp_xmit_retransmit_queue` | **4.1.37** | (4.7.5 upstream) | NET* (crafted SACK option on an established TCP conn; NVD classifies LOCAL) | none on wire | 4.1.37 `References: CVE-2016-6828` (highest_sack fix) |
| CVE-2016-5696 | TCP challenge-ACK predictability → blind off-path session hijack | **4.1.32** | (4.7 upstream) | NET (off-path) | none | 4.1.32 "tcp: make challenge acks less predictable" + per-socket rate limit (not CVE-tagged in changelog) |
| CVE-2016-2117 | `atl2` NIC wrongly enables SG → kernel-memory info leak | **4.1.28** | — | NET* (only if Atheros/L1 atl2 NIC present — unlikely on Intel Broxton) | none | 4.1.28 atl2 `NETIF_F_SG` fix, `CVE-2016-2117` cited |

### Local / socket-reachable-without-CAP_NET_ADMIN (task item 3)

| CVE | Subsystem | Fixed-in 4.1.x | Else fixed-in | Reachability | Privilege | 4.1.x ChangeLog evidence |
|---|---|---|---|---|---|---|
| CVE-2016-5195 | **Dirty COW** — `get_user_pages` FOLL_WRITE race → write to read-only file maps → unprivileged root | **4.1.35** | (4.8.3 / 4.4.23 upstream) | LOCAL | none | 4.1.35 "mm: remove gup_flags FOLL_WRITE games from __get_user_pages()" (upstream 19be0eaffa3a) |
| CVE-2017-1000364 | "Stack Clash" — stack guard-page bypass | **4.1.42** | (4.12) | LOCAL | none | 4.1.42 "mm: larger stack guard gap, between vmas" (1be7107fbe18) |
| CVE-2017-1000112 | UDP/UFO `__ip_append_data` / `__ip6_append_data` frag-length inconsistency → OOB write | **4.1.44** | (4.13) | LOCAL (send UDP w/ MSG_MORE; no cap) | none | 4.1.44 "ipv4: Should use consistent conditional judgement for ip fragment…" + ipv6 twin (e4c5e13aa45c); not CVE-tagged in changelog |
| CVE-2017-9242 | `__ip6_append_data` OOB write (too-late check) | **4.1.42** | — | LOCAL (IPv6 UDP sendmsg) | none | 4.1.42 "ipv6: fix out of bound writes in __ip6_append_data()" (232cd35d0804) |
| CVE-2017-9074 | IPv6 fragment: invalid `nexthdr` option → OOB read in `ip6_fragment` | **4.1.42** | — | LOCAL (crafted send; reproducer uses SOCK_RAW) | none–CAP_NET_RAW | 4.1.42 "ipv6: Prevent overrun when parsing v6 header options" (2423496af35d) + follow-up |
| CVE-2016-8399 | `ping_common_sendmsg` stack OOB (`memcpy_fromiovec`) | **4.1.37** | — | LOCAL (ping socket) | none if `ping_group_range` allows, else CAP_NET_RAW | 4.1.37 `CVE-2016-8399` cited |
| CVE-2016-8655 | AF_PACKET TPACKET_V3 `packet_set_ring` race → UAF | **4.1.37** | — | LOCAL | CAP_NET_RAW | 4.1.37 "packet: fix race condition in packet_set_ring" (84ac7260236a) |
| CVE-2017-1000111 | AF_PACKET `PACKET_RESERVE` race (analog of 8655) | — | 4.12 / 4.4.x / 4.9.x | LOCAL | CAP_NET_RAW | not in 4.1 |
| CVE-2020-14386 | AF_PACKET `tpacket` overflow | — | 5.9-rc4 | LOCAL | CAP_NET_RAW | not in 4.1 |

### Netfilter/xtables reachable **without** CAP_NET_ADMIN (task item 2)

| CVE | Subsystem | Fixed-in 4.1.x | Reachability | Privilege | 4.1.x ChangeLog evidence |
|---|---|---|---|---|---|
| CVE-2017-18017 | `xt_TCPMSS` UAF | **4.1.43** | NET* — the *only* xtables fix in this window reachable by a packet without CAP_NET_ADMIN | none | see above |
| CVE-2016-4997 | compat `IPT_SO_SET_REPLACE` / `IP6T_SO_SET_REPLACE` OOB (32-bit compat) | **4.1.28** | LOCAL | CAP_NET_ADMIN | 4.1.28 x_tables compat-validation series ("do compat validation via translate_table" etc.) |
| CVE-2016-4998 | `IPT_SO_SET_REPLACE` OOB read / heap infoleak | **4.1.28** | LOCAL | CAP_NET_ADMIN | same 4.1.28 x_tables series |

Note: every other xtables fix in the 4.1.28–52 window (`xt_check_entry_offsets`,
`validate targets of jumps`, `fix int overflow in xt_alloc_table_info`,
`xt_check_proc_name`, `xt_LED` timer init, etc.) is a config/rule-install path and
requires CAP_NET_ADMIN; they are relevant only in the "attacker already controls
a root update process" scenario (item 4), not to an unprivileged network peer.

### xfrm / IPsec (local, CAP_NET_ADMIN)

| CVE | Subsystem | Fixed-in 4.1.x | Reachability | Privilege | Evidence |
|---|---|---|---|---|---|
| CVE-2017-7184 | `xfrm_replay_verify_len` heap OOB after `XFRM_MSG_NEWAE` | **4.1.49** | LOCAL | CAP_NET_ADMIN | 4.1.49 `CVE-2017-7184` cited |
| CVE-2017-11600 | `XFRM_MSG_MIGRATE` OOB if `CONFIG_XFRM_MIGRATE` | **4.1.45** | LOCAL | CAP_NET_ADMIN | 4.1.45 `CVE-2017-11600` cited |

### Not applicable to this configuration

- CVE-2017-8824 (DCCP UAF), CVE-2017-1000410 (L2CAP infoleak), CVE-2017-1000251/1000252
  (BT), CVE-2015-8956 (RFCOMM), CVE-2017-0786 (Broadcom Wi-Fi): **no DCCP/Bluetooth**.
- CVE-2016-5412 / CVE-2016-5828 (powerpc TM): **x86-64**.
- CVE-2015-8709 (ptrace userns): **CONFIG_USER_NS=n**.
- CVE-2016-9604 (root adds key to `.builtin_trusted_keys`): only bypasses module
  signature verification; **CONFIG_MODULE_SIG=n** already, so limited value.
- CVE-2019-11487 (page `_refcount` overflow): needs ~140 GiB RAM + FUSE; unrealistic here.

### Other local CVEs explicitly fixed in the 4.1.28–52 window (for completeness)

CVE-2016-1583 (ecryptfs, 4.1.29), CVE-2016-6213 (mount DoS, 4.1.37/43),
CVE-2016-7042 (proc_keys, 4.1.36), CVE-2016-7097 (setgid/setxattr, 4.1.37),
CVE-2016-7425 (arcmsr SCSI, 4.1.37), CVE-2016-6480 (aacraid, 4.1.32),
CVE-2016-5400 (airspy USB, 4.1.30), CVE-2016-8405 (Android infoleak, 4.1.39),
CVE-2016-8632 (TIPC, 4.1.37 — TIPC probably not built), CVE-2016-9191 (cgroup,
4.1.39), CVE-2017-2618 (SELinux proc attr, 4.1.39), CVE-2017-6951 (dead keyring,
4.1.40), CVE-2017-7472 (keyring DoS, 4.1.40), CVE-2017-7482 (rxrpc kerberos,
4.1.43 — rxrpc likely not built), CVE-2017-12193 (assoc_array, 4.1.46),
CVE-2017-0861 (ALSA pcm UAF, 4.1.49), CVE-2017-15265 (ALSA seq race, 4.1.46),
CVE-2018-1000004 (ALSA seq pool, 4.1.51), CVE-2017-5753 (Spectre-class KVM
barrier, 4.1.50), CVE-2017-1000365/1000370/1000371 (stack/args exhaustion,
4.1.43; 1000370/71 are i386-only), CVE-2017-1000407 (KVM port 0x80, 4.1.49),
CVE-2017-12154 (KVM CR8, 4.1.46), CVE-2017-17741 (KVM write_mmio infoleak,
4.1.50), CVE-2017-7518 (KVM TF, 4.1.47), CVE-2013-4312 (unix fd DoS mitigation,
4.1.28), CVE-2015-1350 (setattr, 4.1.37), CVE-2015-8952 (mbcache, 4.1.37).

---

## (c) Most promising for an **unauthenticated network attacker**

Ranked by (reachability × impact × whether 4.1.27 is actually exposed):

1. **CVE-2019-11477 (SACK `tcp_gso_segs` overflow → kernel panic).**
   Remote, no authentication, no capability, SACK enabled by default; 4.1 went
   EOL 2018-05-27 and never received the 2019-06 fix. A single crafted SACK can
   panic the TCP stack. Highest value DoS for this unit.
2. **CVE-2019-11479 (SACK low-MSS resource exhaustion).** Remote, unauthenticated,
   unfixed in 4.1; degrades the unit via CPU/memory churn even if 11477/11478
   are not reliable on this exact codebase.
3. **CVE-2019-11478 (SACK `tcp_fragment` DoS).** Remote, unauthenticated, unfixed
   in 4.1; sibling of 11477, also panic/resource DoS.
4. **CVE-2018-5391 (FragmentSmack, IPv4/IPv6 fragment reassembly DoS).**
   Remote, unauthenticated, low packet rate; NVD scopes it "3.9+" so 4.1.27 is
   in range and 4.1 never got the reassembly hardening.
5. **CVE-2016-7039 / CVE-2016-8666 (GRO recursion → stack overflow/panic).**
   Remote via VLAN/GRE/tunnel-stacked packets. **Fixed in 4.1.37** — so this is
   a *gap only if the device truly runs 4.1.27 code* (a build label alone does
   not prove the vendor didn't cherry-pick it). If unpatched, easy panic.
6. **CVE-2017-18017 (`xt_TCPMSS` UAF).** Remote packet traversal, but only if the
   vendor's firewall has a `-j TCPMSS` rule (common on WAN-facing NAT boxes, less
   certain on an infotainment unit). Fixed in 4.1.43 → gap if not cherry-picked.
7. **CVE-2016-6828 (TCP SACK highest_sack UAF).** NVD says LOCAL, but the trigger
   is a crafted SACK from a peer, so it is plausibly network-reachable on an
   established connection. Fixed in 4.1.37 → gap if not cherry-picked.

Then, once *any* local code execution exists (app / compromised userland
service), the top local escalations that a 4.1.27 device is missing are, in
order: **CVE-2016-5195 (Dirty COW → root)** (fixed 4.1.35),
**CVE-2017-1000364 (Stack Clash)** (fixed 4.1.42),
**CVE-2016-8655 / CVE-2017-1000111 (AF_PACKET UAF → root, needs CAP_NET_RAW)**.

---

## (d) Uncertainty notes

1. **Version-vs-code gap.** All "fixed in 4.1.x" statements mean *the fix is in
   that ChangeLog*. The device labels itself 4.1.27, but a vendor (localversion
   `-abl`, built Jan 2026) may have back-ported arbitrary commits or applied its
   own patches. Every "gap" row must be confirmed against the actual source or
   runtime symbol/string evidence before it is treated as exploitable. The table
   is a *backport-gap hypothesis*, not a proof of vulnerability.
2. **Reachability of CVE-2016-6828.** NVD rates it "local"; the trigger is a
   crafted SACK option, which a remote peer can in principle send. I marked it
   NET* pending confirmation that the UAF is triggerable from the receive path
   without local send-side activity.
3. **CVE-2018-5390 (SegmentSmack).** NVD scopes it "Linux 4.9+", so it is likely
   not applicable to 4.1.27 despite being a TCP DoS; kept in the table only for
   completeness. CVE-2018-5391 (FragmentSmack) *is* scoped "3.9+" and does apply.
4. **SACK trio preconditions.** CVE-2019-11477/11478 require the peer to open a
   TCP connection and negotiate SACK (default on). They do not require the
   attacker to complete a handshake with a privileged local app — the kernel TCP
   stack itself is the victim, so *any* reachable listening socket (e.g., a
   diagnostic, update, or connectivity service) is a candidate.
5. **Driver-dependent rows.** CVE-2016-2117 (atl2), CVE-2016-5400 (airspy),
   CVE-2016-6480 (aacraid), CVE-2016-7425 (arcmsr), CVE-2016-8632 (TIPC),
   CVE-2017-7482 (rxrpc) depend on drivers/protocols that are probably absent
   from an Intel Broxton infotainment build; their applicability needs a config
   check (`/proc/config.gz` or the recovered `.config`).
6. **`CONFIG_XFRM_MIGRATE`** may be off, which would void CVE-2017-11600.
7. **Spectre/Meltdown (CVE-2017-5715/5753/5754).** The 4.1.50 entry only covers a
   KVM vmcs barrier; full mitigations depend on microcode + vendor backports and
   are out of scope for this network-focused triage. `CONFIG_RANDOMIZE_BASE=n`
   makes KASLR irrelevant, but speculative-execution leaks are a separate axis.
8. **Post-EOL list is illustrative, not exhaustive.** Only the most impactful
   post-2018 network CVEs were queried against NVD. A full sweep of the 4.4/4.9/
   4.14 changelogs for net/ commits would surface more candidates (this triage
   prioritized the SACK/fragmentation/UDP/netfilter classes the task named).
9. **No DCCP/SCTP/BT is asserted from the task statement**, not re-verified from
   the recovered `.config`. If any of those are actually built as modules they
   would re-activate CVE-2017-8824, CVE-2017-1000410, CVE-2017-1000251/2.
