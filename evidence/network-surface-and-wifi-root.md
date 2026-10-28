# Wi-Fi network surface and remote-root feasibility

Status: research plan for the owner's Gen5W AVN on an isolated bench network.
Scope is a single owned unit. No vehicle is connected. This document records
what a network route to root would require; it is not an exploit and contains no
payload, credential attack, or procedure against a third-party network.

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

## What I need from you to make this concrete

1. Is the unit's Wi-Fi in AP/hotspot mode, client mode, or dealer mode?
2. The IP the unit hands out or receives, and the subnet.
3. Output of `net_surface.py --target <ip> --authorised`.
4. Whether any dealer/engineering Wi-Fi menu is reachable on the unit UI.
5. The installed build shown on the version screen.

## Safety

Keep the unit on an isolated AP or VLAN with no route to other networks. Do not
scan or test any address you do not own. A network finding on this unit is a
research result; treat any working chain as disclosure-bound rather than as a
tool to distribute.
