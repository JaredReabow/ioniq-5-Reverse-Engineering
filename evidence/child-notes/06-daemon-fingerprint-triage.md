# Daemon Fingerprinting & Version-Bound CVE Triage

> Scope: embedded Linux head unit, kernel `4.1.27-abl`, ~2018-era userspace, x86-64.
> Candidate daemons: `dnsmasq`, `hostapd`, `wpa_supplicant`, `miniupnpd` (+ companion
> `minissdpd`), `dropbear`, BusyBox (multi-call). Exact versions are unknown because
> the root filesystem is encrypted, so **every conclusion here is keyed on a captured
> version string or binary-string artifact** and must be confirmed on the bench.
>
> This document contains fingerprinting and triage guidance only. No exploit code,
> no payloads, no device contact, no third-party network procedures.

Companion documents: the full 2015–2020 CVE corpus is in
`evidence/child-notes/01-component-cve-corpus.md`; network-surface mapping is in
`evidence/network-surface-and-wifi-root.md`. This note extends that corpus to 2021
and adds the **fingerprint → version → fix-line** mapping needed for triage.

---

## 0. How to read the tables

- **Signal** = what an observer captures (banner / header / option / binary string).
- **Min affected / Fixed in** = the version boundary from NVD / vendor advisory.
  "`< 2.78` / `2.78`" means "affected in versions below 2.78, fixed in 2.78".
- **Attacker position** = the minimum capability an attacker needs to reach the code
  path (e.g. "be a DHCPv6 client on the link"). This is the triage gate: if the
  service is not reachable in that role, the CVE does not apply to your bench.
- **Exploitability** uses three grades:
  - **WILD** — trivially triggerable / actively scanned / turnkey public tooling.
  - **PoC** — public proof-of-concept or exploit exists; needs setup or a specific role.
  - **Theoretical** — side-channel, config-dependent, local-only, or no public exploit.

> Caveats that apply to every row:
> 1. A bare version string does not prove a fix is present — vendors backport patches
>    into old versions. Treat the version as a *likely* boundary and confirm by
>    behaviour or binary strings.
> 2. Reachability depends on which Wi-Fi mode the unit is in (AP/hotspot vs client vs
>    dealer). See `network-surface-and-wifi-root.md`.

---

## 1. dnsmasq

### 1.1 Fingerprinting

| Signal | Where | What you get | Confidence |
|---|---|---|---|
| DNS `CHAOS TXT version.bind` | `dig @<unit> CH TXT version.bind` (also `version.server`) | `dnsmasq-2.78` style string — **the primary remote fingerprint** | High (default on) |
| DNS behaviour | reply case-randomisation, EDNS0 handling, NXDOMAIN/`SOA` in negative answers, `local` answer authoritativeness | narrows dnsmasq vs BusyBox-udhcpd vs unbound | Medium (behavioural) |
| DHCP server replies | option ordering, absence of a vendor-class/version option (dnsmasq DHCP server does **not** advertise a version by default) | confirms dnsmasq-as-DHCP but **no version** | Medium |
| Offline strings | `Dnsmasq version %s`, `dnsmasq-%s`, `started, version %s`, `Compile time options`, `--version` output path | exact `%s` value = version | High (when a binary is dumped) |

### 1.2 Version-bound CVE triage (high impact, 2015–2021)

| CVE | Class | Min affected | Fixed in | Attacker position | Exploitability |
|---|---|---|---|---|---|
| CVE-2017-14491 | DNS reply heap overflow → RCE | `< 2.78` | 2.78 | Be the upstream DNS server the unit forwards to, or spoof a DNS reply dnsmasq accepts | PoC (Metasploit module exists) |
| CVE-2017-14492 | DHCPv6 heap overflow → RCE | `< 2.78` | 2.78 | Be a DHCPv6 client on the local link | PoC (public) |
| CVE-2017-14493 | DHCPv6 stack overflow → RCE | `< 2.78` | 2.78 | Be a DHCPv6 client on the local link | PoC (public) |
| CVE-2017-14494 | DHCPv6 relay info leak | `< 2.78` (relay mode) | 2.78 | Send DHCPv6 to the relay | Theoretical (needs relay config) |
| CVE-2017-14495 / 14496 | DNS leak / integer underflow (needs `--add-mac`/`--add-subnet`/`--add-cpe-id`) | `< 2.78` | 2.78 | Be a DNS client of the unit | Theoretical (config-dependent) |
| CVE-2017-13704 | DNS packet-size DoS | `< 2.78` | 2.78 | Be a DNS client | WILD (trivial DoS) |
| CVE-2017-15107 | DNSSEC wildcard NSEC validation bypass | `≤ 2.78` | 2.79 | Be a DNS client that can induce a query | Theoretical |
| CVE-2019-14834 | DNS memory leak DoS | `< 2.81` | 2.81 | Be a DNS client | PoC |
| CVE-2020-25681 / 25682 / 25683 / 25687 | **DNSpooq** heap/buffer overflow → RCE (DNSSEC path) | `< 2.83` | 2.83 | Spoof DNS replies (off-path greatly weakened by 25684–25686) | PoC (JSOF); RCE needs DNSSEC enabled |
| CVE-2020-25684 / 25685 / 25686 | **DNSpooq** cache poisoning | `< 2.83` | 2.83 | Off-path attacker (reduced guess-space) | WILD (cache poisoning) |
| CVE-2021-3448 | cache poisoning (fixed source port + ID guess) | `< 2.85` | 2.85 | On-path attacker, when `server=`/`strict-order` pins a fixed port | WILD where config matches |
| CVE-2015-8899 / CVE-2019-14513 | DNS DoS (empty reply / oversized packet) | `< 2.76` | 2.76 | Be the upstream DNS server | PoC |
| CVE-2015-3294 | TCP DNS info leak | `< 2.73rc4` | 2.73 | Be a DNS client over TCP | Theoretical |

**Triage rule:** `version.bind` → `dnsmasq-X.Y`. If `X.Y < 2.83` assume DNSpooq
(poisoning always; RCE only if DNSSEC + local attacker can spoof replies). If
`X.Y < 2.78` and DHCPv6 is served, the 2017 RCE trio is in scope. Cross-check with
the binary strings because vendor backports are common in automotive.

---

## 2. hostapd

### 2.1 Fingerprinting

| Signal | Where | What you get | Confidence |
|---|---|---|---|
| SSDP/WPS UPnP (only if `CONFIG_WPS_UPNP`) | M-SEARCH to `239.255.255.250:1900`, read `LOCATION` → `rootDesc.xml` | `deviceType` `urn:schemas-wifialliance-org:device:WFADevice:1`, WPS service — proves hostapd-WPS, **but** | High for presence |
| SSDP `SERVER` header | same response | **`unspecified, UPnP/1.0, unspecified`** (confirmed in hostapd 2.6 source) — the placeholder string itself is a hostapd fingerprint; it leaks **no version** | High |
| 802.11 beacons / probe response | capability flags, WPS IE, 802.11w/PMF, OWE/SAE IEs | build-feature fingerprint (WPS / WPA3 / PMF present?), not a version | Medium |
| Offline strings | `hostapd v` + `VERSION_STR` (e.g. `hostapd v2.6`), `hostapd-%s` | exact version | High (binary dump) |

**Key point:** hostapd's own UPnP stack deliberately emits no version. Remote
version inference is **behavioural** (feature IEs, WPS device description). The
reliable version comes from `hostapd -v` or the binary on the bench.

### 2.2 Version-bound CVE triage (high impact, 2015–2021)

| CVE | Class | Min affected | Fixed in | Attacker position | Exploitability |
|---|---|---|---|---|---|
| CVE-2017-13077 … 13082, 13084, 13086–13088 | **KRACK** PTK/GTK/IGTK reinstallation → decrypt/inject frames | `≤ 2.6` | 2.7 (git Oct 2017) | Within radio range; act as MITM on the 4-way/group handshake | WILD (vanhoef scripts public) |
| CVE-2019-9494 … 9499 | **Dragonblood** SAE / EAP-pwd (cache + timing side channels, DoS) | `< 2.8` | 2.8 | Within radio range against WPA3-SAE or EAP-pwd | PoC (needs WPA3/EAP-pwd — unlikely on a 2018 unit) |
| CVE-2019-13377 | SAE / EAP-pwd timing side channel | `2.x ≤ 2.8` | 2.9 | Within radio range, WPA3/EAP-pwd | Theoretical (side-channel) |
| CVE-2018-14526 | EAPOL-Key integrity not checked (wpa_supplicant side; affects unit as client) | `2.0–2.6` | 2.7 | Be the AP the unit associates to | PoC (mostly DoS) |
| CVE-2019-16275 | source-address validation → false disconnect | `< 2.10` | 2.10 | Within radio range | PoC (DoS) |
| CVE-2021-27803 | P2P provision-discovery → overflow / RCE | `< 2.10` | 2.10 | Within radio range, Wi-Fi Direct/P2P enabled | PoC (P2P usually off in automotive) |
| CVE-2021-30004 | SAE forging (AlgorithmIdentifier mishandling) | `2.9` | 2.10 | WPA3-SAE peer | Theoretical |
| CVE-2016-4476 | passphrase newline/CR handling | `0.6.7–2.5` | 2.6 | Config/WPS interaction | Theoretical |
| CVE-2015-4141 … 4146, 8041 | EAP-pwd / WPS / NDEF DoS & memory bugs | `≤ 2.4` (some `≤2.5`) | 2.5 | EAP-pwd/WPS/NDEF peer | PoC (legacy) |
| CVE-2015-5314 / 5315 / 5316 | EAP-pwd reassembly DoS | `2.x < 2.6` | 2.6 | EAP-pwd peer | PoC (legacy) |
| CVE-2019-5061 / 5062 | IAPP / 802.11w state DoS | `2.6` | later release (verify) | Valid 802.11w client / IAPP peer | PoC (DoS) |

**Triage rule:** hostapd version mostly tells you the KRACK / Dragonblood / P2P line.
KRACK is the one that matters for a 2018-era AP: assume vulnerable unless the build
shows the 2.7+ fixes **or** a vendor backport. Feature IEs (802.11w, WPS, SAE) tell
you which of the above classes are even reachable.

---

## 3. wpa_supplicant

### 3.1 Fingerprinting

| Signal | Where | What you get | Confidence |
|---|---|---|---|
| As a station (client) | 802.11 management-frame behaviour, EAPOL key handling, scan/probe patterns | feature fingerprint only, **no version** | Low–Medium |
| As an AP (AP mode) | same SSDP/beacon signals as hostapd §2.1 | presence only | Medium |
| Offline strings | `wpa_supplicant v%s` | exact version | High (binary dump) |

wpa_supplicant has **no remote version banner**. Version triage is from the binary
or from behavioural differentials (e.g. whether a KRACK/Dragonblood PoC succeeds on
your own bench).

### 3.2 Version-bound CVE triage (overlaps hostapd for shared code)

| CVE | Class | Min affected | Fixed in | Attacker position | Exploitability |
|---|---|---|---|---|---|
| CVE-2017-13077 … 13088 | **KRACK** (station side: 4-way, group, FT, TDLS, WNM) | `≤ 2.6` | 2.7 | Be the AP / peer the unit connects to | WILD (public scripts) |
| CVE-2018-14526 | EAPOL-Key integrity check missing | `2.0–2.6` | 2.7 | Be the AP the unit connects to | PoC (DoS) |
| CVE-2019-9497 / 9498 / 9499 | **Dragonblood** EAP-pwd | `< 2.8` | 2.8 | EAP-pwd network | PoC (EAP-pwd unlikely) |
| CVE-2019-13377 | SAE / EAP-pwd timing | `2.x ≤ 2.8` | 2.9 | WPA3/EAP-pwd | Theoretical |
| CVE-2019-16275 | source-address validation | `< 2.10` | 2.10 | Radio-range | PoC (DoS) |
| CVE-2021-27803 / 30004 | P2P / SAE | `< 2.10` / `2.9` | 2.10 | P2P or WPA3 peer | PoC / Theoretical |
| CVE-2015-1863, 4141–4146, 5310, 5315, 5316, 8041 | legacy EAP-pwd/WPS/WNM/NDEF memory bugs | `≤ 2.4` / `2.x <2.6` | 2.5 / 2.6 | EAP-pwd/WPS/WNM peer | PoC (legacy) |

**Triage rule:** the unit acting as a **client** is most exposed to KRACK/14526
(attacker runs a rogue AP). If it only ever runs AP mode, hostapd §2.2 is the
dominant table and wpa_supplicant's station-side rows drop out.

---

## 4. miniupnpd (+ companion minissdpd)

### 4.1 Fingerprinting

| Signal | Where | What you get | Confidence |
|---|---|---|---|
| SSDP `SERVER` header | M-SEARCH response | `Linux/4.1.27 UPnP/1.1 MiniUPnPd/<ver>` — **version in the SERVER field** | High (primary remote fingerprint) |
| `LOCATION` → `rootDesc.xml` | HTTP GET on the advertised URL | `deviceType` IGD/WANDevice, `URLBase`, `modelName` (often vendor-set) — confirms device class | High |
| UPnP control URL | HTTP `POST` SOAP to the WANIPConn / WANPPPConn control path | behaviour + HTTP `Server:` header (some builds repeat `MiniUPnPd/<ver>`) | Medium |
| Offline strings | `MiniUPnPd/%s`, `miniupnpd %s`, `MINIUPNPD_VERSION` | exact version | High (binary dump) |

### 4.2 Version-bound CVE triage (high impact, 2015–2021)

| CVE | Class | Min affected | Fixed in | Attacker position | Exploitability |
|---|---|---|---|---|---|
| CVE-2017-1000494 | uninitialised stack var in SOAP reply parser → DoS | `< 2.0` | 2.0 | Send a crafted SOAP/UPnP request to the control URL | WILD (trivial DoS) |
| CVE-2019-12107 | `upnpevents.c` heap info leak | `≤ 2.1` | 2.2.0 | Send a SUBSCRIBE with `CALLBACK` of the form `http://ip:port` | PoC |
| CVE-2019-12108 / 12109 | NULL deref in `GetOutboundPinholeTimeout` | `≤ 2.1` | 2.2.0 | Send a crafted SOAP action | WILD (trivial DoS) |
| CVE-2019-12110 | NULL deref in `AddPortMapping` (`upnpredirect.c`) | `≤ 2.1` | 2.2.0 | Send a crafted `AddPortMapping` SOAP | WILD (trivial DoS) |
| CVE-2019-12111 | NULL deref in `copyIPv6IfDifferent` (PCP) | `≤ 2.1` | 2.2.0 | Send a crafted PCP message | PoC |
| CVE-2020-12695 | **CallStranger** — SUBSCRIBE `CALLBACK` SSRF / data exfil | `< 2.2.0` | 2.2.0 (git Apr–May 2020) | Send `SUBSCRIBE` to the event URL (port 1900/`LOCATION`) | **WILD** (actively scanned; one packet) |
| CVE-2019-12106 | **minissdpd** use-after-free → DoS | `1.4 / 1.5` | later release | Send SSDP NOTIFY (minissdpd is the cache daemon) | PoC |

**Triage rule:** `MiniUPnPd/2.x` in SSDP `SERVER` is the linchpin. `≤ 2.1` →
everything above applies (CallStranger + 2019 NULL-deref DoS are the cheap wins).
`≥ 2.2.0` → only look for later/backport gaps. CallStranger is the single most
likely "known to be trivially exploitable in the wild" item in this whole set.

---

## 5. dropbear

### 5.1 Fingerprinting

| Signal | Where | What you get | Confidence |
|---|---|---|---|
| SSH protocol banner | connect to TCP 22 | `SSH-2.0-dropbear_2016.74` — **version embedded in the banner** | High (primary remote fingerprint) |
| KEX / hostkey / MAC list | SSH key-exchange offer | narrows build age (cipher/MAC set changes by release) | Medium |
| Offline strings | `Dropbear sshd v%s`, `DROPBEAR_VERSION` | exact version | High (binary dump) |

### 5.2 Version-bound CVE triage (high impact, 2015–2021)

| CVE | Class | Min affected | Fixed in | Attacker position | Exploitability |
|---|---|---|---|---|---|
| CVE-2016-7406 | **format string** in username/host → RCE | `< 2016.74` | 2016.74 | Connect to TCP 22 and send a crafted username | WILD (public; single connection) |
| CVE-2016-7408 | dbclient `-m`/`-c` format string → RCE (client) | `< 2016.74` | 2016.74 | Client-side only (unit as client) | PoC |
| CVE-2017-9078 | server double-free → post-auth root RCE (needs `-a`) | `< 2017.75` | 2017.75 | Authenticate, then trigger TCP-listener cleanup (`-a` enabled) | PoC (post-auth, `-a`-gated) |
| CVE-2016-3116 | X11-forwarding CRLF injection → command restriction bypass | `< 2016.72` | 2016.72 | Authenticated user with X11 forwarding | PoC |
| CVE-2018-15599 | user enumeration (auth timing) | `≤ 2018.76` | 2018.77 | Connect to TCP 22 | WILD (trivial enumeration) |
| CVE-2019-12953 | user enumeration (failure-delay variance) | `2011.54–2018.76` | 2019.77+ | Connect to TCP 22 | WILD (trivial enumeration) |
| CVE-2021-36369 | client-side auth-method confusion (FIDO/Askpass bypass) | `≤ 2020.81` | 2022.82 | Client-side (unit as client) | Theoretical (server-side irrelevant) |

**Triage rule:** the SSH banner gives the year directly (`dropbear_YYYY.NN`).
`< 2016.74` → CVE-2016-7406 is the headline (format-string RCE by connecting).
`< 2018.77` → username enumeration. `2017.75`–`2020.81` → nothing remotely trivially
code-executing on the server side; move on to other services.

---

## 6. BusyBox (multi-call)

### 6.1 Fingerprinting

| Signal | Where | What you get | Confidence |
|---|---|---|---|
| `udhcpc` DHCP vendor class (option 60) | unit as DHCP client | default `udhcp <BB_VER>` (e.g. `udhcp 1.27.2`) | High (when the unit runs udhcpc) |
| `udhcpd` / DNS behaviour | DHCP-server + resolver behaviour | behavioural only, no version | Low–Medium |
| `httpd` `Server:` header | any BusyBox httpd listener | typically no version (often just `httpd` or a vendor string) | Low |
| `ntpd` | NTP response quirks | behavioural only | Low |
| telnetd/`getty` | TCP 23 | no version | — |
| Offline strings | `BusyBox v1.27.2`, `BusyBox v%s`, multi-call applet table | exact version | High (binary dump / `busybox` invocation) |

### 6.2 Version-bound CVE triage (high impact, 2015–2021)

| CVE | Class | Min affected | Fixed in | Attacker position | Exploitability |
|---|---|---|---|---|---|
| CVE-2016-2148 | udhcpc heap overflow (option 6RD) → RCE | `< 1.25.0` | 1.25.0 | Be the DHCP server the unit's udhcpc talks to | PoC (public) |
| CVE-2016-2147 | udhcpc integer overflow (RFC1035 domain) → DoS | `< 1.25.0` | 1.25.0 | Be the DHCP server the unit talks to | PoC |
| CVE-2018-20679 / 2019-5747 | udhcp OOB read (client/server/relay) → DoS | `< 1.30.0` / `≤ 1.30.0` | 1.30.0 / 1.30.1 | Be a DHCP peer on the link | PoC (DoS) |
| CVE-2018-1000517 | `wget` buffer overflow → RCE | `< 1.29.0` | 1.29.0 (commit `8e2174e`) | Control a URL the unit fetches with busybox wget | PoC (context-dependent) |
| CVE-2018-1000500 | `wget` missing TLS cert validation | `< 1.29.x` | 1.29.x+ | MITM a TLS fetch | PoC |
| CVE-2021-28831 | `gunzip` invalid free → DoS | `≤ 1.32.1` | 1.33.1 | Feed crafted gzip to a BusyBox gunzip path | Theoretical (local/supply-chain) |
| CVE-2021-42374 … 42386 | `awk` use-after-free → DoS/RCE | `≤ 1.33.1` | 1.34.0 | Invoke `awk` on a crafted pattern (local) | Theoretical (local) |
| CVE-2021-42373 | `man` applet NULL deref → DoS | `≤ 1.33.1` | 1.34.0 | Local `man` invocation | Theoretical (local) |
| CVE-2016-6301 | `ntpd` CPU/bandwidth DoS | `< 1.26.0` | 1.26.0 | Send crafted NTP packets to BusyBox ntpd | WILD (trivial DoS, if ntpd enabled) |
| CVE-2017-15873 / 15874 | `bunzip2`/`unlzma` int overflow → DoS | `≤ 1.27.2` | 1.28.0 | Feed crafted archive to a local decompression path | Theoretical (local) |

**Triage rule:** BusyBox is the hardest to fingerprint remotely — only `udhcp
<ver>` (client mode) and `BusyBox v%s` (binary) leak a version. Its **remote**
high-value items are the udhcpc/udhcp family (`< 1.25.0` RCE; `< 1.30.1` DoS) and
`ntpd` DoS; everything else needs a local or supply-chain trigger.

---

## 7. Signals to capture on the bench

Capture these **before** touching any CVE table; each one feeds a specific section:

- [ ] `dig CHAOS TXT version.bind @<unit>` and `version.server` → dnsmasq version (§1).
- [ ] DHCP server reply capture (offer/ACK) → confirm dnsmasq vs udhcpd (§1, §6).
- [ ] If unit is a DHCP **client**: capture its `DISCOVER` option 60 → BusyBox version (§6).
- [ ] SSDP M-SEARCH (`239.255.255.250:1900`, ST `ssdp:all`); record every `SERVER`,
      `LOCATION`, `USN` → miniupnpd version + hostapd-WPS presence (§2, §4).
- [ ] `GET` each `LOCATION` → `rootDesc.xml`; record `deviceType`, `URLBase`,
      `modelName`, and any HTTP `Server:` header (§2, §4).
- [ ] TCP connect to 22; record the `SSH-2.0-dropbear_...` banner (§5).
- [ ] TCP connect to 23 (if open); note telnetd presence (no version, but a finding).
- [ ] HTTP/HTTPS `Server:`, `X-Powered-By`, TLS cert subject/issuer/SAN + DER SHA-256
      → custom vendor services (not these daemons, but §"network-surface" coverage).
- [ ] 802.11 capture of beacons/probe-responses on the unit's AP: record RSN/WPS/PMF
      capability bits and any WFA/WPS IEs → hostapd feature fingerprint (§2).
- [ ] If root/binary access is ever obtained: `hostapd -v`, `wpa_supplicant -v`,
      `busybox`, `dnsmasq -v`, `miniupnpd -V`, and `strings`/grep for
      `dnsmasq-%s`, `hostapd v%s`, `wpa_supplicant v%s`, `MiniUPnPd/%s`,
      `Dropbear sshd v%s`, `BusyBox v%s` → exact versions for §1–§6.

**Record per capture:** timestamp, unit Wi-Fi mode, the interface the unit uses, and
the request that elicited each signal — triage needs reachability + identity, not
just the string.

---

## 8. Sources

- NVD 2.0 CVE API (`https://services.nvd.nist.gov/rest/json/cves/2.0`), retrieved
  2026-10-19; `cveId` lookups for the 2021 set and `keywordSearch` corpus in
  `01-component-cve-corpus.md`.
- Google Project Zero / dnsmasq advisory (CVE-2017-14491–14496, 13704), Oct 2017.
- JSOF **DNSpooq** advisory (CVE-2020-25681–25687), Jan 2021; Red Hat write-ups.
- w1.fi security advisories 2017-1 (KRACK), 2019-1..5 (Dragonblood / SAE / EAP-pwd);
  hostapd 2.6 source (`src/wps/wps_upnp_web.c`, `hostapd/main.c`) — confirmed the
  WPS UPnP `SERVER: unspecified, UPnP/1.0, unspecified` string and `hostapd v%s`.
- vanhoef: KRACK (2017), Dragonblood (2019), FragAttacks (2020/2021) disclosures.
- miniupnpd `Changelog.txt` (release dates: 2.0 = 2016-04-19, 2.1 = 2018-05-08,
  2.2.0 = 2020-10-31) and CallStranger advisory (CVE-2020-12695).
- dropbear `CHANGES` (version-numbered releases) and NVD records.
- BusyBox release notes / commits (`8e2174e9bd836e53c8b9c6e00d1bc6e2a718686e`,
  JFrog/Claroty awk disclosure Nov 2021).
