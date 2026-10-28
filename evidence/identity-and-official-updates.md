# Australian 2021 Hyundai IONIQ 5: identity and official update evidence

- Task: T1 (research), requirements R1 and R2
- Research/access date: 2026-10-18 (Australia/Sydney)
- Scope: identity only. No package was downloaded, extracted, modified or flashed; no
  vehicle was touched. "Examined" below means an HTML/PDF page was read, never a
  firmware image.
- Status: complete for the T1 acceptance criteria.

> **2026-10-27 vehicle evidence:** Owner-supplied USB logs identify the
> UK-origin car's installed software as `NE_E.EUR.S5W_L.001.001.250604` and
> head-unit model as `NEAE.S5BLC.AEU`. The Australian values below remain
> market-comparison evidence. See
> `vehicle-usb/README.md` for the captured source and
> integrity check.

## Bottom line

The Australian 2021-23 IONIQ 5 (NE1, pre-facelift) is published by Hyundai
Australia's official navigation updater as **Standard Gen5W Navigation**, model name
**NEAE.S5BLN.AAU**, current software **NE_E.AUS.S5W_L.001.001.260319**, current map
**AUS.19.41.47.011.611.0** (S1).

Both identifiers named in the task are confirmed, not refuted, as the current
officially published identifiers for this vehicle family on 2026-10-18. That is a
publication-level verification. It does not prove what a particular car has
installed, and no firmware package was inspected.

## Source-backed identity table

Status legend: **observed** = read directly from the cited page; **community** =
owner report, supplementary only; **unknown** = not established.

| Field | Value | Status | Source |
|---|---|---|---|
| Vehicle family / updater group | IONIQ 5, 2021-23 (NE1, pre-facelift) | observed | S1 |
| Head-unit family label | "Standard Gen5W Navigation" (10.25 and 12.3 in touchscreen) | observed | S1, S3 |
| Model name | `NEAE.S5BLN.AAU` | observed (official); also shown on an AU owner's screen | S1, S16 |
| Current software version | `NE_E.AUS.S5W_L.001.001.260319` | observed | S1 |
| Current map version | `AUS.19.41.47.011.611.0` | observed | S1 |
| Region tokens | `AUS` in software string; `AAU` in model name | observed; token semantics **unknown** | S1 |
| Early software string example | `NE E.AUS.S5W_L.001.001.210326` (as posted; underscore/space ambiguous) | community | S16 |
| Early firmware string example | `NE_E.AUS.03.210325.MICOM` | community | S16 |
| Early navigation app string example | `STD5W.AUS.HMC.210303.b3c41806_ne` | community | S16 |
| 2024-25 IONIQ 5 (different platform) | ccNC; `NE1.OCE.ccNC.001.002.260408`, model `NE1AE.SCBMC.AU` | observed; **not** the 2021 car | S1 |
| European sibling (different region) | `NE_E.EUR.S5W_L.001.001.260128`, models `NEAE.S5BLC.AEU` and `NEAE.S5BLN.AEU` | observed; **must not** be cross-loaded with AU | S14 |

The model-name suffix differs between the Australian (`AAU`) and European (`AEU`)
listings while the software prefix differs in the region field (`AUS` vs `EUR`).
Hyundai publishes these as different rows for different regions (S1, S14).

## Australian variant history

- The Australian September 2021 specification sheet has a single trim column,
  "IONIQ 5", with 2WD and AWD drivetrains: 160 kW rear motor or 225 kW combined,
  72.6 kWh battery, 12.3-inch touchscreen with satellite navigation (S11).
- Hyundai Australia's July 2022 release describes a "revised 2022 IONIQ 5 range"
  that introduces the RWD **DYNAMIQ** and AWD **TECHNIQ** grades (S12).
- Hyundai Australia's launch release said Australia would launch in Q3 2021
  and described a dual 12-inch cockpit (S13). Australian ordering opened in late
  September 2021 in a single highly equipped specification with a 2WD/AWD choice
  (secondary reporting; not used for the identity conclusion).

Inference (flagged): a car sold as a "2021 IONIQ 5" is normally the single launch
specification, not a DYNAMIQ or TECHNIQ, because those grade names appear with the
2022 revision. This does not change the head unit: Hyundai's updater groups the
whole 2021-23 range as Standard Gen5W (S1).

Caveat on "2021": this may be the build or registration year rather than the model
year. Hyundai's own July 2022 article calls the revised car the "2022 IONIQ 5",
which implies the launch cars already sat inside the 2022 model-year range. Use the
compliance plate/VIN for model year and the head-unit screen for software.

## How the owner reads the installed version

Hyundai's Australian Gen5W documentation and updater FAQ give this path:

1. Power the car to ON/READY so the head unit stays awake.
2. Press **SETUP** on the head unit, or open **All Menus > Settings**.
3. Open **General > Version info/Update**.
   - Shortcut documented in the Australian Gen5W manual: press and hold **SETUP**
     to jump to the Version info/Update screen (S7).
   - Hyundai's Australian updater FAQ labels the same screen **Settings > General >
     SW Info.** for "Standard Gen5W" (S6). Menu wording varies by software build.
4. Record or photograph every field: Model, Software version, Firmware version,
   NAV APP (navigation application), Map version, Device ID (S8, English edition
   of the Gen5W manual).
5. Compare the Software line with `NE_E.AUS.S5W_L.001.001.260319`.
6. If using Navigation Updater, the AU FAQ says to type the software version into
   the updater (special characters such as `.`, `,`, `_` are optional) to confirm
   the vehicle type (S6).

Hyundai's Gen5W manual documents the screen as showing software, firmware,
navigation application, map and device ID (S8). The separate "Model" line with
`NEAE.S5BLN.AAU` is visible on an Australian owner's report of the same screen
(S16); treat that line as community-observed rather than manual-documented.

## Official updater compatibility

- Hyundai Australia's updater lists the 2021-23 IONIQ 5 under **Standard Gen5W
  Navigation** and publishes the model/software/map values in the table above (S1).
- Navigation Updater is a PC application: Windows 10/11 or macOS 10.10 and later,
  with more than 1 GB free on the C drive; it cannot be downloaded on a tablet or
  phone (S17).
- The update is written to portable storage. Hyundai recommends a 32 GB USB drive
  formatted **exFAT** for USB-based systems (S18). The notice's SD-card branch only
  applies to systems that have an SD card (S3).
- Vehicle selection must be correct. Hyundai warns: "If the wrong model/model year
  is chosen, the update cannot be performed" (S3).
- The car must be running during installation; do not switch off the ignition or
  eject the media during the upgrade (S3).
- Hyundai states: "After installation, it is not possible to revert to the previous
  software version" (S3). This is a one-way update from the owner's perspective.
- Hyundai's Australian Sat Nav Update Plan lists IONIQ 5 (NE) as covered: updates
  within 10 years of first registration, maximum 9 updates, for AutoEver units,
  included with a scheduled dealer service; Hyundai also says owners may be
  eligible to perform the AutoEver update themselves via USB (S9).

OTA: Hyundai Australia's OTA notice page lists IONIQ 5 (NE1) entries with short
codes (`6900`, `6902`, `6908`, `690A`) and 25MY entries, including a 1 June 2026
notice (S10). Those pages do not establish OTA coverage for the 2021-23 Gen5W
family; the Gen5W route published for that family is the USB updater.

## Dated official releases and currency check (2026-10-18)

Hyundai Australia's notification list, read on 2026-10-18, shows:

| Notice | Register date | URL |
|---|---|---|
| 2026 June Infotainment Update | 19-Jun-2026 | S3 |
| 2026 February infotainment update | 10-Feb-2026 | S4 |
| September 2025 Navigation Map and Software Update | 17-Sep-2025 | S5 |

No Australian notice dated after 19-Jun-2026 appeared on that list (S2).

Verification of the two named identifiers:

1. **`NEAE.S5BLN.AAU` - confirmed.** It appears in the Model Name column of the
   current Australian software-version table for "2021-23 IONIQ 5" (S1). It is a
   model-name identifier, not a VIN or a hardware part number, so it identifies the
   family rather than a specific car.
2. **`NE_E.AUS.S5W_L.001.001.260319` - confirmed as the current published version.**
   It appears in the Software Version column for the same row (S1). The
   accompanying map version is `AUS.19.41.47.011.611.0`.

Why "current" is a reasonable reading: the same table also contains 2026 ccNC
builds (`260408`), so it is a live table rather than a stale snapshot; the newest
Australian notice is 19 June 2026; and the trailing `260319` in the software
string is consistent with a 19 March 2026 build, after the February notice and
before the June notice. The June notice's stated new feature is a map update (S3).

Limits: this confirms what Hyundai Australia publishes as current for the family.
It does not confirm the installed version on the user's car, and no package was
downloaded to compare contents or hash.

## Region and version caveats

- **AUS is not EUR.** The European table lists IONIQ 5 2022-2023 as
  `NE_E.EUR.S5W_L.001.001.260128` with models `NEAE.S5BLC.AEU` and
  `NEAE.S5BLN.AEU` (S14). The region
  token and model suffix differ from the Australian row (S1). Do not treat a
  European package as compatible.
- **AAU is not a unique Australian marker.** The New Zealand updater table lists
  the same 2021-23 IONIQ 5 Gen5W values, `NEAE.S5BLN.AAU` and
  `NE_E.AUS.S5W_L.001.001.260319`, while its ccNC models use a `.NZ` suffix (S15).
  The AAU string is therefore a Gen5W model code shared by the AU/NZ tables, not
  proof of Australian delivery on its own.
- **Model-year selection matters.** The Australian table splits 2021-23 IONIQ 5
  (Gen5W) from 2024-25 IONIQ 5 (ccNC) (S1). Choosing the later year selects a
  different platform and version scheme.
- **Trim does not change the head unit.** Launch 2WD/AWD cars and later
  DYNAMIQ/TECHNIQ cars all fall inside the 2021-23 Gen5W group (S1, S11, S12).
- **Website and car can disagree.** Dealer-installed, OTA or regionally staged
  builds may be newer or older than the website. The car's Software line is the
  installed truth; the website is the published release truth.
- **Map and software belong together.** `AUS.19.41.47.011.611.0` is the map listed
  with `260319` for this family (S1). Do not pair map and software rows by date
  alone.

## Observed facts, inference, unknowns

Observed:

- The Australian updater row, platform label, model name, software and map values
  in the identity table (S1).
- The Australian notice dates and the June notice's map-update description (S2-S5).
- The Australian version-reading paths (S6, S7) and the Gen5W screen fields (S8).
- The updater's PC, USB, selection, power and no-revert rules (S3, S17, S18).
- The single-trim September 2021 Australian specification and the later
  DYNAMIQ/TECHNIQ introduction (S11, S12).
- The European and New Zealand rows showing different region/model suffixes
  (S14, S15).

Inference (not directly stated by Hyundai):

- The launch cars predate the DYNAMIQ/TECHNIQ grade names.
- The AU and NZ Gen5W tables share one package/model code.
- `NE_E` is plausibly the NE electric variant and `S5W_L` plausibly encodes
  Standard Gen5W, but Hyundai publishes no glossary for these tokens.

Unknown / unresolved:

- The official meaning of `NEAE`, `S5BLN`, `AAU`, `S5W_L` and the trailing `_L`.
- The hardware part number, supplier and board revision of the Australian Gen5W
  unit; the updater exposes only the model-name string.
- Whether every 2021-23 Australian car, across hardware revisions, accepts the same
  `260319` package.
- The package filename, size, contents and hash for the Gen5W build; none was
  downloaded in T1.
- Whether a dealer-only or OTA build newer than `260319` exists for these cars.
- Whether OTA is available at all for the 2021-23 Gen5W family in Australia.

## Checks performed, including negative and blocked checks

Read on 2026-10-18:

- Australian software-version table, notice list, June 2026 notice, February 2026
  notice, September 2025 notice (S1-S5).
- Australian updater FAQ on selecting the vehicle type and on reading the version
  (S6), plus the SD/USB update FAQ (S19).
- Australian Gen5W manual component page (S7); Gen5W general-settings manual page
  for the screen fields (S8).
- Australian Navigation Updater download page and update guide (S17, S18).
- Australian Sat Nav Update Plan and OTA notice pages (S9, S10).
- Australian September 2021 specification sheet and 2022 range release (S11, S12).
- European and New Zealand software-version tables (S14, S15).
- One Australian owner report showing the on-screen Model/Software/Firmware/NAV APP
  fields (S16).

Negative checks:

- No official Hyundai glossary was found that decodes `NEAE.S5BLN.AAU` or its
  tokens; searches returned only version tables and owner posts.
- No Australian notice dated after 19 June 2026 was found on the official list.
- No official Australian page was found that offers a direct firmware file
  download outside Navigation Updater; the site directs owners to NaU (S3).

Blocked checks:

- `https://update.hyundai.com/AU/EN/updateNoticeView/software-version` returned
  "not accessible via this tool"; the AU popup table (S1) was used instead.
- The Australian Gen5W manual pages `010_Settings_general.html` and
  `010_Settings_general2.html` were not accessible; the component page (S7), the
  AU FAQ (S6) and the Gen5W settings page (S8) were used instead.
- A Croatian-language Hyundai dealer PDF on AVN software selection timed out and
  was not used.
- No package or firmware image was downloaded, so no package hash exists.
- No vehicle interaction was performed, so the car's installed version is unknown.

## Sources

All URLs were accessed 2026-10-18 (Australia/Sydney). Publication dates are as
shown by the source where available.

- S1. Hyundai Australia, software-version table (popup view):
  https://update.hyundai.com/AU/EN/updateNoticePopup/aiD0Sq
- S2. Hyundai Australia, notification list:
  https://update.hyundai.com/AU/EN/updateNoticeList
- S3. Hyundai Australia, "2026 June Infotainment Update", register date
  19-Jun-2026: https://update.hyundai.com/AU/EN/updateNoticeView/yNDC3y
- S4. Hyundai Australia, "2026 February infotainment update", register date
  10-Feb-2026: https://update.hyundai.com/AU/EN/updateNoticeView/ng1CLX
- S5. Hyundai Australia, "September 2025 Navigation Map and Software Update",
  register date 17-Sep-2025:
  https://update.hyundai.com/AU/EN/updateNoticeView/OYE7ct
- S6. Hyundai Australia, FAQ "How to select the right vehicle type with the SW
  version available in your car": https://update.hyundai.com/AU/EN/faqView/1628
- S7. Hyundai owner's manual, Standard Gen5W, Australia, "Name of each component":
  https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/nameofeachcomponent.html
- S8. Hyundai owner's manual, Standard Gen5W_8, EU English, "General" settings
  (Version info/Update fields):
  https://ownersmanual.hyundai.com/ivi/STD_GEN5W_8/AVNT/EU/English/general.html
- S9. Hyundai Australia, "Sat Nav Update Plan":
  https://www.hyundai.com/au/en/owning/myhyundaicare/sat-nav-plan
- S10. Hyundai Australia, "OTA Software Notices":
  https://www.hyundai.com/au/en/owning/ota-updates
- S11. Hyundai Australia, IONIQ 5 specification sheet, September 2021:
  https://www.hyundai.com/content/dam/hyundai/au/en/models/ioniq5/images/IONIQ5_SpecTable_Sept_2021.pdf
- S12. Hyundai Australia, "2022 IONIQ 5: Power your world" (DYNAMIQ/TECHNIQ):
  https://www.hyundai.com/au/en/news/vehicles/2022-ioniq-5-power-your-world
- S13. Hyundai Australia, "Hyundai IONIQ 5 redefines electric mobility lifestyle"
  (Q3 2021 Australian launch):
  https://www.hyundai.com/au/en/news/mobility/hyundai-IONIQ-5-redefines-electric-mobility-lifestyle
- S14. Hyundai Europe, software-version table (IONIQ 5 2022-2023 row):
  https://update.hyundai.com/EU/EN/updateNoticeView/software-version
- S15. Hyundai New Zealand, software-version table (popup view):
  https://update.hyundai.com/NZ/EN/updateNoticePopup/oJpu3Y
- S16. Whirlpool forum, Australian IONIQ 5 thread, owner-posted version screen
  (page 4): https://forums.whirlpool.net.au/archive/3nk4kz69-4
- S17. Hyundai Australia, Navigation Updater download page:
  https://update.hyundai.com/AU/EN/navigationUpdate
- S18. Hyundai Australia, Navigation Update guide (USB specifications):
  https://update.hyundai.com/AU/EN/updateGuide
- S19. Hyundai Australia, FAQ "How to update a system in your vehicle" (Gen5W
  version menu): https://update.hyundai.com/AU/EN/faqView/1625

## Gaps handed to T2

- Obtain the official Australian Gen5W package through Navigation Updater and record
  its filename, size and SHA-256 before any inspection.
- Confirm that the package's internal model/software strings match
  `NEAE.S5BLN.AAU` and `NE_E.AUS.S5W_L.001.001.260319`.
- Determine whether the package is a full image or a delta, and whether it contains
  more than the map data described in the June 2026 notice.
- Identify the head-unit hardware revision separately from the software model
  string; the public updater does not expose a part number.
