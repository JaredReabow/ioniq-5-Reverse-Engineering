# Wi-Fi network surface and remote-root feasibility

Status: offline exact-build review plus a future isolated-bench plan for the
owner's Gen5W AVN. Scope is a single owned unit. No vehicle is connected. This
document records what a network route to root would require; it is not an exploit
and contains no payload, credential attack, or procedure against a third-party
network.

## Why network root is a separate path

Physical rungs (UART, bootloader, storage) give root but require the unit open
on a bench. A network route is the only one that persists across reboots without
physical access, which is why it is worth mapping separately. It is also the
hardest: it requires a reachable service with a real defect, and the exact-build
trust chain does not help an attacker who is already past the login boundary.

## What "Wi-Fi on a Gen5W" can mean

Three very different exposures share the word "Wi-Fi":

| Mode | Typical services | Attack relevance |
|---|---|---|
| AP / hotspot mode | `dnsmasq` (DHCP+DNS), `hostapd`, captive portal, local UI | Highest: unauthenticated listeners on a network the unit creates |
| Client / tethering mode | Outbound only, mDNS, update client | Lower: unit initiates connections |
| Dealer / engineering Wi-Fi | SSH, telnet, debug UI, file transfer | Highest if enabled, but usually gated behind a dealer menu |

Telling them apart is the first output of enumeration, not an assumption.

## Enumeration protocol

Run `tools/uk_fw/net_surface.py` against the unit on an isolated AP/VLAN and
record, per run:

- open TCP ports and round-trip times;
- HTTP status, `Server`, `X-Powered-By`, and page title;
- TLS certificate subject/issuer/SAN and DER SHA-256;
- SSDP `SERVER`/`LOCATION` and USN values;
- mDNS responders and service names.

Indicators and what they imply:

| Observation | Implication |
|---|---|
| TCP 53 open on the unit | Local DNS resolver — likely `dnsmasq` in AP mode |
| SSDP/UPnP response | A UPnP daemon (`miniupnpd` or vendor) is exposed |
| mDNS responders | Avahi/Bonjour-class service discovery is active |
| HTTP `Server:` with a known daemon/version | Version-matched CVE triage becomes possible |
| TLS cert with vendor CN but self-signed | Vendor web UI; check for auth-bypass and injection |
| Telnet/SSH open without a dealer gate | Immediate high-value target |

## Service → vulnerability class

Ranked by expected yield on a 2018-era Linux `4.1.27` embedded build. Every row
is a hypothesis until version and code evidence confirm it.

| Class | Typical component | Example defect family | What confirms it |
|---|---|---|---|
| Vendor web/update endpoint logic | Custom HTTP handlers, OTA client | Auth bypass, path traversal, unauthenticated command dispatch | Endpoint inventory + request/response diffing |
| Command injection in diagnostics | Config, logging, network-setup handlers | Unsanitised shell interpolation | Source or binary strings showing `system()`/`popen()` with request data |
| Known CVE in old daemon | `dnsmasq`, `hostapd`, `wpa_supplicant`, `miniupnpd`, `dropbear`, `BusyBox` | Version-specific memory-safety or logic bugs | Exact version string from banner/cert/HTTP |
| Custom parser memory corruption | Update protocol, projection, media | Heap/stack overflow, integer bugs | Fuzzing a local harness of the parser |
| TLS/crypto weakness | Old OpenSSL/mbedTLS | Protocol downgrade, weak cert validation in the update client | Client behaviour against a test server |

Memory-corruption work (row 4) is the most expensive and should follow, not
precede, rows 1–3. Logic flaws in vendor endpoints usually yield root faster
than a memory bug because they bypass the whole hardening stack.

## Preconditions and evidence per class

A network finding is only actionable when it has:

1. **Reachability** — the service answers on the unit's Wi-Fi interface without
   a dealer/engineering gate.
2. **Identity** — exact daemon and version, or the exact binary hash.
3. **Trigger** — a minimal request that reaches the vulnerable code path.
4. **Impact** — the resulting identity, and whether it survives reboot.
5. **Reproducer** — a local harness or recorded packet trace, not a live claim.

## What the exact-build analysis already contributes

From `evidence/eu-custom-firmware-feasibility.md` and
`evidence/eu-root-sideload-applicability.md`:

- the platform is x86-64 Linux `4.1.27-abl` with SMACK; a network bug must also
  clear SMACK to reach protected objects;
- the kernel exposes no KASLR and has `debugfs`, `/dev/kmem`, `/proc/kcore`
  and non-strict `/dev/mem` compiled in — high post-exploitation value, but not
  an entry route;
- unsigned kernel modules are permitted, so a network-to-root step can be
  consolidated into a module once root exists;
- the update trust chain is asymmetric and kernel-side, so a network route does
  **not** by itself permit custom firmware — it permits a shell.

## Exact offline candidate: ConnMan CVE-2026-115863

The recovered RPM Btree identifies
`connman-1.29+5w.master.38-r1.corei7_64`, and exact binary analysis—not that
version label—confirms CVE-2026-115863's affected DHCPv6 DOMAIN_LIST parser.
`connmand+0x1f150` copies a fixed 1,025 bytes into a local stack area, then walks
DNS labels and writes `'.'` without checking the cursor against the local-buffer
end. Exact option dispatch calls it for DHCPv6 option 24.

The static activation path is also present. On a connected ConnMan-managed
network, the exact Router Advertisement callback routes Managed/Other flags to
stateful DHCPv6 or an information request. The information-request routine
explicitly asks for option 24. The installed service defaults to uid 0 and does
not exclude the intended `wlan0` interface. A reply must nevertheless match the
live transaction ID, client/server identifiers, message type, and client state.

No packet was sent. Production Wi-Fi association, interface ownership, IPv6
policy, RA acceptance, and DHCPv6 reachability remain unknown. The binary has
PIE, a non-executable stack, stack canaries, and full RELRO; a conditional daemon
crash is the only currently defensible impact. Do not call this Wi-Fi-to-root.
See `evidence/connman-cve-2026-115863.md`.

### Related availability finding: ConnMan CVE-2023-28488

Exact binary review also confirms V-016/CVE-2023-28488's pre-fix DHCPv4
IP-total-length ordering and its normal activation route. Ordinary IPv4 startup
enters `INIT_SELECTING`; listening mode 1 creates an `AF_PACKET` datagram socket
and registers the affected callback.

This is not another Wi-Fi-to-root candidate for recovered `260128`. Exact code
calls `__memcpy_chk` with a 628-byte destination size, and all recovered libc
checked-copy implementations reviewed branch to `__chk_fail` before an
underflowed request writes the stack. Non-underflowing lengths that survive the
read check fit the destination. The exact-build result is therefore conditional
ConnMan process termination/availability. No packet or dynamic abort was
produced. See `evidence/connman-cve-2023-28488.md`.

## Separate cellular/modem candidates: oFono TPDU and QMI decoding

V-017 is not a Wi-Fi listener or an IP-service result. Exact shipped
instructions retain destination checks fixed by CVE-2023-4232 through
CVE-2023-4235, CVE-2023-2794, and CVE-2024-7547. Compiled `lgeqmimodem`
callbacks pass QMI direct indications and stored/raw-read TPDUs to
`sms_decode(..., FALSE, ...)`; deliver, submit-report, and status-report copies
complete before the handler's late DELIVER type check. Deliver-report and
command are outgoing-only but have exact local transmit-queue and SIM-Toolkit
callers. Message-free arithmetic permits writes beyond the local `0x128`-byte
`sms` object; no dynamic corruption or execution was attempted.

V-018 is a distinct modem trust-boundary result. The QMI WMS message-list
callback retains CVE-2024-7537's missing count/length equality check. Its vendor
32-bit overflow diagnostic falls through to a four-byte allocation while the
original-count copy loop continues, admitting selected-TLV overreads, possible
backing-result OOB reads, and heap writes. This QMI result is
supplied by the modem; direct SMS/base-station control is not established.

The conditional service would run as uid 0 but receives SMACK label `App::tms`.
It requires a telematics marker, and the recovered `ofono.path` also watches a
`no_isa` marker; no enable symlink for that path was identified. Production
activation, modem/QMI state, carrier attachment, byte preservation, SIM-Toolkit
state, the owner's installed hash, RCE, and unrestricted root are unproven. See
`evidence/ofono-sms-decoder-cves.md` and
`evidence/ofono-qmi-message-list-cve-2024-7537.md`.

## Exact P2P backport result: two wpa_supplicant candidates rejected

The package database identifies `wpa-supplicant-2.5+56-r1`, but exact recovered
instructions supersede the old version string. In `p2p_add_device()`,
`0x5b1ca..0x5b1d3` gates every SSID copy on peer-supplied length at most 32,
matching the CVE-2015-1863 fix. In the Provision Discovery Request handler,
`0x688e8` calls `p2p_add_device()` and successful return reaches an
unconditional post-add `p2p_get_device(p2p, sa)` at `0x68dee`; this matches the
CVE-2021-27803 fix and replaces the potentially stale pointer. Both CVEs are
therefore rejected for the exact recovered binary. See
`evidence/wpa-supplicant-p2p-cves.md`.

The result does not eliminate P2P as a surface. P2P code is compiled into the
supplicant, ConnMan contains peer/find/listen/provision-discovery machinery, and
an enabled path unit conditionally starts `supplicantmanager` when
`/tmp/no_unece` exists. Production marker state, arguments, interface ownership,
P2P device creation, discovery/listen state, SMACK label, and radio delivery are
unknown. Dropbear's package record is not a network route in this image. The recovered
filesystem retains a socket-fed template, installer, and static root authorized
public key, but no `dropbear`/`dropbearmulti` executable, socket unit, host-key
service/key, or enable link. It is inert; see
`evidence/dropbear-activation-and-authentication.md`. The other package
records—`busybox-1.23.2-r0mango12` and `openssl-1.0.2k-r0`—remain triage leads
pending exact activation and route review. ConnMan's installed `--nodnsproxy`
argument, for example, removes the older DNS-proxy listener route.

## Separate Bluetooth/PAN candidate: Broadcom BSA CVE-2017-0782

Both PCB-selectable `vbtd` binaries contain CVE-2017-0782's exact pre-fix BNEP
remaining-length parser. Their exported `bnep_process_control_packet()` reads
beyond declared remaining length before the public fix's field bounds. The unit
is enabled with a configured uid-0 default and policy intends `App::bluetooth`,
but both profiles say `PAN : N/A` and no direct `BNEP_Register` reference was
found. Treat V-019 as dormant pending indirect/runtime profile-registration
evidence. Any radio route would still require an active adapter and accepted
ACL/L2CAP channel. Pairing/authorization, physical delivery, allocation-bound
OOB, public generic RCE, and owner applicability remain unknown. This is not
Wi-Fi-to-root. See
`evidence/broadcom-bsa-bluetooth-cves.md`.

## What I need from you to make this concrete

1. Is the unit's Wi-Fi in AP/hotspot mode, client mode, or dealer mode?
2. The IP the unit hands out or receives, and the subnet.
3. Output of `net_surface.py --target <ip> --authorised` only after an isolated,
   owner-controlled bench network is available.
   <!-- disagreement: the parallel repository asked for this run without the isolated-bench precondition. Both phrasings are preserved. -->
4. Passive interface/IPv4/IPv6/ConnMan state and benign DHCP/RA capture before
   any malformed input is considered; acquire the installed libc hash alongside
   `connmand` before applying V-016's exact fortify conclusion.
5. Whether any dealer/engineering Wi-Fi menu is reachable on the unit UI.
6. The installed build and, if acquired read-only, the installed `connmand`,
   libc, and `ofonod` hashes.
7. For the separate cellular surface, passive `ofono` unit/marker state,
   process uid/SMACK label, modem devices, QMI services, and normal benign SMS
   behavior before any malformed control is considered.

## Safety

Keep the unit on an isolated AP or VLAN with no route to other networks. Do not
scan or test any address you do not own. A network finding on this unit is a
research result; treat any working chain as disclosure-bound rather than as a
tool to distribute.

#### From the parallel repository

The parallel copy of this document contained the same sections, the same mode/indicator/service tables, the same precondition list, the same exact-build contributions and the same safety note. Its status line read:

> Status: research plan for the owner's Gen5W AVN on an isolated bench network. Scope is a single owned unit. No vehicle is connected. This document records what a network route to root would require; it is not an exploit and contains no payload, credential attack, or procedure against a third-party network.

Its closing request list was shorter:

1. Is the unit's Wi-Fi in AP/hotspot mode, client mode, or dealer mode?
2. The IP the unit hands out or receives, and the subnet.
3. Output of `net_surface.py --target <ip> --authorised`.
4. Whether any dealer/engineering Wi-Fi menu is reachable on the unit UI.
5. The installed build shown on the version screen.
