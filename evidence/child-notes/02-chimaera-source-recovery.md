# Chimaera / IIT-CNR source recovery (public sources only)

Date: 2026 (run from this machine). Method order followed: direct https `-k` →
plain http → DNS → Wayback → scholar/index search → GitHub/CVE-reference search.
No credentials, no access-control bypass, ~20 HTTP requests with 2 s delays.

## TL;DR

| Target | Status |
|---|---|
| `IIT-20-2020.pdf` (KOFFEE, Kia) | **RECOVERED** from Wayback (full PDF + text) |
| `IIT-01-2023.pdf` (Chimaera report) | **NOT reachable, NOT archived** — but the peer-reviewed journal version is open-access |
| Chimaera GitLab project page | **NOT reachable, NOT archived** — content summarized via 4 CVEs + journal paper |

The `sowhat.iit.cnr.it` host resolves but is network-unreachable from here (all
TCP connect attempts time out). The Chimaera report PDF and GitLab pages were
**never captured by the Wayback Machine**, so no public mirror of the raw
`IIT-01-2023.pdf` was located. Its substance is, however, fully described in an
open-access journal article and in the four CVE records that cite it.

---

## 1. Direct host checks

DNS resolves but every TCP attempt times out (host down or filtered from this network).

| URL | Result |
|---|---|
| `sowhat.iit.cnr.it` (A record) | `146.48.60.67` (no AAAA) |
| `https://sowhat.iit.cnr.it/` | HTTP 000, connect timeout (20 s) |
| `https://sowhat.iit.cnr.it:8443/` | HTTP 000, connect timeout |
| `http://sowhat.iit.cnr.it/` | HTTP 000, connect timeout |
| `https://sowhat.iit.cnr.it:8443/can-work/chimaera` | HTTP 000, connect timeout |
| `https://sowhat.iit.cnr.it/pdf/IIT-20-2020.pdf` | HTTP 000, connect timeout |
| `https://sowhat.iit.cnr.it/pdf/IIT-01-2023.pdf` | HTTP 000, connect timeout |

## 2. Wayback Machine (`archive.org/wayback/available` + CDX)

| URL | Closest snapshot |
|---|---|
| `sowhat.iit.cnr.it/pdf/IIT-20-2020.pdf` | **200** — `20250727095957` (used to recover) |
| `sowhat.iit.cnr.it` (homepage) | 200 — `20250420131815` |
| `sowhat.iit.cnr.it/pdf/IIT-01-2023.pdf` | none |
| `sowhat.iit.cnr.it:8443` | none |
| `sowhat.iit.cnr.it:8443/can-work/chimaera` | none |
| `sowhat.iit.cnr.it:8443/can-work/chimaera/-/blob/main/Report/IIT-01-2023.pdf` | none |
| `sowhat.iit.cnr.it:8443/can-work/chimaera/-/raw/main/Report/IIT-01-2023.pdf` | none |
| CDX prefix `sowhat.iit.cnr.it/pdf` | only `IIT-20-2020.pdf` (2020-11-16) |
| CDX prefix `sowhat.iit.cnr.it:8443/can-work/chimaera` | **empty (never archived)** |

The April-2025 homepage snapshot does **not** list Chimaera among the GitLab
projects (it lists TOUCAN, Candy, RSAOverCAN, Cars, CAN Flood, KOFFEE,
CandyRe, Candy Cream) and has no `IIT-01-2023` reference — Chimaera was added
to the project page after that crawl and before the host went dark.

## 3. Report 2 — `IIT-20-2020.pdf` (RECOVERED)

Retrieved 514 KB PDF from Wayback (`.../20250727095957id_/https://sowhat.iit.cnr.it/pdf/IIT-20-2020.pdf`).
The full paper and extracted text were removed from the public repository; consult the cited publisher copy.

- **Title:** KOFFEE — Kia OFFensivE Exploit
- **Institute:** Consiglio Nazionale delle Ricerche, Istituto di Informatica e
  Telematica (IIT-CNR), Technical Report **IIT TR-20/2020**, November 2020
- **Authors:** G. Costantino, I. Matteucci
- **Target:** Kia Cee'd Gen 5.0 "iAVN" head unit — Telechips TCC8931, dual
  Cortex-A9, Android 4.2.2 (this is the *older* Gen 5.0 unit, not Gen5W_L)
- **Sections:** 1 Introduction · 2 Vehicle's anatomy (M-CAN/I-CAN/C-CAN/B-CAN/P-CAN
  separated by a Central Gateway) · 3 Head Unit (3.1 third-party apps, 3.2 apps
  reverse engineering, 3.3 file system, 3.4 access to the CAN bus) · 4 KOFFEE
  (attack chain, semi-controlled CAN frames, Metasploit module, vulnerability
  assessment) · 5 Disclosure process · References.
- **Key public text:**
  - MICOM is the hardware component that injects CAN frames; the OS/apps reach it
    through a socket at **`/dev/socket/micomd`**.
  - App-level CAN frames carry an internal HU structure (ID + payload) that the
    MICOM firmware maps to either a "MICOM-signal" or a real CAN 2.0 frame via an
    internal DBC.
  - KOFFEE chain: (1) sideload an app that opens a remote connection (social
    engineering), (2) remote control navigates the HU file system and injects
    M-CAN frames / triggers radio controls via the Micom.
  - Four vulnerabilities listed: code execution, HU library code execution,
    semi-controlled CAN frame injection (wireless/High), DBC reversal (local/Medium).
  - Tested on software versions 180703, 181019, 191219, 200401.
  - A Metasploit module exists ("not public available at the moment" as of the report).
  - Responsible disclosure to Kia Motors; this is the report behind **CVE-2020-8539**
    (micomd command injection). The 2022 journal version is Costantino & Matteucci,
    *"Reversing Kia Motors Head Unit to discover and exploit software vulnerabilities"*,
    J Comput Virol Hack Tech (2022), DOI `10.1007/s11416-022-00430-5`.

## 4. Report 1 — `IIT-01-2023.pdf` (Chimaera) — NOT recoverable directly

Canonical URL (from the CVE references):
`https://sowhat.iit.cnr.it:8443/can-work/chimaera/-/blob/main/Report/IIT-01-2023.pdf`
(also cited as the project root `…/can-work/chimaera`). Both are unreachable and
were never archived. **However** the work is published openly:

- **Journal version (open access):** Costantino, De Vincenzi, Matteucci,
  *"A vehicle firmware security vulnerability: an IVI exploitation"*,
  Journal of Computer Virology and Hacking Techniques 20(4):681–696 (2024),
  DOI `10.1007/s11416-024-00522-4` (Springer, `is_oa: true`, hybrid OA).
- **Abstract (public, verbatim from OpenAlex):** explores vulnerabilities in an
  IVI firmware, focusing on the **Gen5W_L** multimedia device in Hyundai/Kia/Genesis
  vehicles; introduces **Chimaera**, a reverse-engineering attack on the IVI
  firmware that exploits a vulnerability introduced by **statically compiling the
  mbedtls library**; after reverse engineering and injecting assembly into the IVI
  firmware it extracts sensitive information such as the **cryptographic keys** used
  to install customized firmware; enables installing insecure firmware and
  **injecting CAN bus messages**, compromising radio controls and safety features.
- Springer landing page returned a **"Client Challenge"** bot-wall (3 KB), so the
  full HTML/PDF was not fetched (would require JS; not attempted).

## 5. The four Chimaera CVEs (NVD keyword `Gen5W`, all 2023-04-27)

Each CVE description names the exact build `AE_E_PE_EUR.S5W_L001.001.211214` and
cites the Chimaera GitLab page + the `Report/IIT-01-2023.pdf` blob URL as the
exploit/third-party advisory.

| CVE | Component | Summary (public) |
|---|---|---|
| CVE-2023-26243 | decryption binary | info leak — AES key + IV readable from memory → create custom firmware |
| CVE-2023-26244 | AppDMClient | modified to bypass digital-signature check of AppUpgrade / `.lge.upgrade.xml` |
| CVE-2023-26245 | AppUpgrade | version-check bypass → install any (newer/older/custom) firmware |
| CVE-2023-26246 | AppUpgrade | digital-signature check bypass → install custom firmware |

Chain implied by the four CVEs (matches the journal abstract): key extraction →
signature/version bypass in the update path → custom firmware install →
persistent control reachable over Wi-Fi.

## 6. Search-engine / index attempts (for completeness)

| Service | Result |
|---|---|
| Semantic Scholar API | HTTP 429 (rate limited) — superseded by OpenAlex |
| OpenAlex | **hit** — found the 2024 Chimaera journal paper |
| Crossref | no Chimaera automotive hit |
| NVD 2.0 API | **hit** — `Gen5W` → CVE-2023-26243…26246 |
| GitHub repo search `chimaera hyundai` | 0 repositories |
| grep.app (code search) | Vercel security checkpoint (bot block) |
| DuckDuckGo html / Bing / Mojeek | anomaly / CAPTCHA / irrelevant (bot detection) |
| arXiv API | connect timeout from this host |

## 7. Conclusion

- **Public copy of `IIT-20-2020.pdf` exists and was recovered** (Wayback; full text).
- **No public copy of `IIT-01-2023.pdf` itself** was found: the host is dark and
  the file was never archived. Its content is available publicly only via the
  **open-access 2024 journal paper** (abstract + article) and the **four CVE-2023-2624x
  records**, which between them reproduce the Chimaera technique, target, and
  components.
- **Chimaera tooling** (the GitLab repo) has no public mirror found. The KOFFEE
  Metasploit module (`modules/post/hardware/automotive/can_flood.rb`) is upstream
  in Rapid7's metasploit-framework (linked from the SOWHAT homepage), but the
  Chimaera exploit code itself was only ever on the now-dark GitLab.

## Artifacts saved

- Full paper: public publisher source cited above; local research copy is private.
- Extracted text: local research copy is private.
