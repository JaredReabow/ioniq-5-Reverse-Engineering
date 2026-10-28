# 03 — Public Tooling Survey (GitHub REST API)

Survey date: 2026-10-19. Method: unauthenticated GitHub REST **repository** search
(`/search/repositories?q=…&per_page=50`) plus `in:readme` / `in:name` qualifiers as a
proxy for code-level hits. Terms queried: `Gen5W`, `S5W_L`, `AppUpgrade`, `AppDMClient`,
`micomd`, `navi_extended`, `D-Audio hyundai`, `hyundai navigation updater`,
`lge.upgrade.xml`, plus follow-ups (`gen5 in:name`, `hyundai gen5`, `d-audio`, `dhawn`).

No repository was cloned, built, or executed. Only metadata and READMEs were read.

---

## Ranked table — genuine tooling / documentation

Ranked by substantive relevance to Hyundai/Kia/Genesis (HMG) infotainment reverse engineering.

| # | Repo | URL | Last push | License | ★ | What it actually contains | Class |
|---|------|-----|-----------|---------|---|---------------------------|-------|
| 1 | `chenxiaolong/nudl` | https://github.com/chenxiaolong/nudl | 2026-09-27 | GPL-3.0 | 103 | Rust CLI ("Navigation Update Downloader") that re-implements the official HMG Navigation Updater server protocol to download the same public firmware without login; parallel chunked downloads, resume, model/region selection. | Genuine tooling |
| 2 | `rgerganov/gen5fw` | https://github.com/rgerganov/gen5fw | 2025-01-08 | MIT | 152 | Python tools + instructions to patch and deploy Standard-class **Mobis Gen5** navigation firmware (enables ADB etc.); based on the xakcop.com blog "hyundai-hack-2". | Genuine tooling |
| 3 | `xwtk/hmg_nemesis` | https://github.com/xwtk/hmg_nemesis | 2026-10-12 | AGPL-3.0 | 71 | "NEMESIS" framework to execute software as root on **Gen5W AVNT** systems with OTA update support; reuses the unsigned DSP-OTA path; docs on install/uninstall/package builder. New (created 2026-09-27). | Genuine tooling |
| 4 | `Helloyunho/gen5w-utils` | https://github.com/Helloyunho/gen5w-utils | 2024-02-11 | Apache-2.0 | 64 | Python utility set for **Gen5W** firmware: odex→dex, `TarList.txt_encrypted` decrypt/encrypt, `.ver`/`update.info` parsers, `sw_backup` navi lib decrypt/encrypt, Hyundai SHA224/SHA256 helpers, patched-firmware builder. | Genuine tooling |
| 5 | `cantcs/HKG_Gen5W_ReverseEngineer` | https://github.com/cantcs/HKG_Gen5W_ReverseEngineer | 2024-09-23 | **none** | 51 | Documentation/write-up + C tooling for reverse engineering Android-based **Gen5W** head units: patching official firmware for adb/root, modifying stock APKs, installing third-party APKs. | Documentation + tooling |
| 6 | `laralbir/hyundai-kia-gen5w-navi-firmware` | https://github.com/laralbir/hyundai-kia-gen5w-navi-firmware | 2026-07-11 | NOASSERTION (custom) | 2 | Spanish-language RE of the **Standard Gen5W Navigation** EU variant (SoC "mango", embedded Linux); explicitly documents build `YB_22.EUR.S5W_L.001.001.251204` (build 2025-12-04, release 25RU2_001). | Documentation |
| 7 | `atawi44/hyundai-igas-firmware-tools` | https://github.com/atawi44/hyundai-igas-firmware-tools | 2026-06-04 | **none** | 1 | Tools to decrypt/analyze Hyundai **iGAS Gen5** head-unit update packages via known-plaintext ZipCrypto attack (bkcrack). | Genuine tooling |
| 8 | `AhmedTarek94/KIA-HYUNDAI-Navigation-Updater-Unlocker` | https://github.com/AhmedTarek94/KIA-HYUNDAI-Navigation-Updater-Unlocker | 2026-07-19 | **none** | 1 | Patcher that lets KDM (Korean-market) Kia/Hyundai owners download Navigation Updater images without a Korean VPN. | Patcher |
| 9 | `GoudaCouda/Gen5w-Ioniq6-CAN-Data` | https://github.com/GoudaCouda/Gen5w-Ioniq6-CAN-Data | 2026-07-12 | **none** | 1 | CAN message codes reversed from **Gen5W** software, believed to be the internal comms with the MICOM unit (Ioniq 6). | Data / notes |
| 10 | `tylerharvey/Ioniq5_CAN` | https://github.com/tylerharvey/Ioniq5_CAN | 2026-10-13 | MIT | 72 | Coordination home for Ioniq 5/6/EV6 CAN reverse engineering and the manual-preconditioning button. | Data / notes |
| 11 | `SlayerSS/doom-meego` | https://github.com/SlayerSS/doom-meego | 2026-10-15 | GPL-2.0 | 0 | Unofficial DOOM port for a Hyundai Genesis head unit (LG DHAVN / MeeGo); releases ship `AppUpgrade` packages. | Genuine tooling (tangential) |
| 12 | `Game-K-Hack/hybootloader` | https://github.com/Game-K-Hack/hybootloader | 2026-10-15 | **none** | 0 | Tiny native launcher for the LG Gen5 head unit (Hyundai i20, Windows CE 7). | Genuine tooling (small) |

Other real-but-minor HMG hits (not ranked above):
- `cantcs/Launcher_WP3_KR` — Apache-style launcher extracted from a Gen5W head unit (Korean), no license, 2★, 2024-03-19.
- `obenturk/Ioniq5_Gen5W_Log_Dump` — Ioniq 5 Gen5W log dump, GPL-3.0, 0★, 2024-10-13.
- `IvanVojtko/hyundai-firmware` — no license, 1★, 2025-02-11; mentions Gen5W in README (content not further inspected).
- `paytondevs/ioniq5-preconditioning` — no license, 3★; manual preconditioning app (CAN-level, not firmware).

## Forks / mirrors

- `C457/-gen5w-utils` — Apache-2.0, 1★, 2023-05-30. A fork/renamed copy of `Helloyunho/gen5w-utils` (name prefixed with `-`). No original content identified. Class: fork/mirror.
- `JohnWitchall/Gen5Weltec` — no license, 0★, 2022-10-06. Empty/unmaintained placeholder; likely stale copy of the Gen5W topic. Class: dead/empty.

## Unrelated name collisions (not HMG)

- **`AppUpgrade` (47 repos):** overwhelmingly generic Android/iOS in-app update SDKs and
  ByteDance "techtrainingcamp" student projects (e.g. `appupgrade-dev/*`,
  `zhouxu88/APPUpgrade`, `henleylee/AppUpgrade`, `LiJiakai/cordova-plugin-AppUpgrade`).
  None relate to Hyundai `AppUpgrade`/OTA. Exception: `SlayerSS/doom-meego` (table #11),
  which genuinely uses Hyundai `AppUpgrade`-format packages.
- **`navi_extended` (31 repos):** Android navigation UI libraries, extended-Kalman-filter
  robotics projects, Contao/WordPress navigation plugins, etc. All unrelated to HMG.
- **`micomd` (2 repos):** `ednoct/MicomDetour` (Xiaomi Mi-account bootloader-unlock
  automation) and `W-Floyd/go-micomd` (Go reimplementation of Xiaomi IoT `micomd`);
  `W-Floyd/bootmanager` is an LG WK7 smart-speaker tool. These are Xiaomi/LG-ecosystem
  "micom daemon" collisions, **not** Hyundai's MICOM (body-controller) daemon.
- **`S5W_L` (4 repos):** `S5withLRAimdb`, `s5williane-devopseasy-learning`, random-string
  repos. No HMG content.
- **`d-audio` / `dhawn`:** audio-player plugins and personal-name repos. `D-Audio hyundai`
  as a combined query returned **0 repositories**.

## Terms with zero public hits

- `D-Audio hyundai` — 0 repos.
- `lge.upgrade.xml` — 0 repos.
- `AppDMClient` — 0 repos (and 0 readme matches).

## Caveats

1. **Code search is not usable unauthenticated.** `GET /search/code` returns HTTP 401
   "Requires authentication". Therefore arbitrary code-level mentions of the target
   strings *inside* repositories (e.g. `AppDMClient` or `lge.upgrade.xml` appearing in a
   source file rather than a repo name/description/README) **cannot be enumerated** by
   this survey. I approximated with `in:readme` / `in:name` repository search, which only
   surfaces the term when it appears in a README, description, or repo name. This is a
   significant coverage gap: a repo that contains these strings only in code would be
   missed.
2. **Unauthenticated search rate limits** (~10 req/min) were respected with ~2–3 s pacing.
3. **License accuracy:** license field taken from the API `license.spdx_id`. `null` →
   "none" (no detected LICENSE file). `NOASSERTION` means a LICENSE file exists but has a
   non-SPDX/custom text (e.g. `laralbir/...`). Star counts and `pushed_at` are point-in-time
   snapshots of 2026-10-19.
4. **Several `pushed_at` values are 2026** (current date at survey time), not data errors;
   e.g. `hmg_nemesis` was created 2026-09-27, only weeks before this survey.
5. **No exploit code was reproduced**; descriptions summarize README/intended function only.
   Repos like `hmg_nemesis` describe root/OTA-persistence techniques — treated here as
   classification targets, not as instructions.
6. **Build coverage:** the strongest public tooling targets **Gen5W Android** (2019+,
   ccOS/Android variants) and **Mobis Standard Gen5 Linux** (pre-2021-era cars). Only
   `laralbir/hyundai-kia-gen5w-navi-firmware` explicitly documents a **newer-than-2021**
   build: `S5W_L.001.001.251204` (build dated 2025-12-04, EUR). `nudl` and `hmg_nemesis`
   are maintained against current (2026) firmware/OTA servers, so they implicitly track
   post-2021 builds, but neither pins a specific 2024+ build string in its metadata.
7. **Repo-name-only searches can false-positive** on `Gen5` (3D printers, PCIe Gen5,
   Makerbot) — those were filtered out as name collisions.
