# Passive, Runtime, and Later-Stage Hardware Evidence Routes

Status: research artifact; Council correction round applied.
Task: T4, requirements R2 and R3.
Target: 2021 Australian Hyundai IONIQ 5, Standard Gen5W infotainment.
Accepted T1 contract: AU 2021-23 IONIQ 5; Standard Gen5W Linux branch indicated by
`NE_E.AUS.S5W_L.001.001.260319`; model `NEAE.S5BLN.AAU`.
Research date: 2026-10-18 (Australia/Sydney); Council re-verification date: 2026-10-19.
All URLs below were accessed on 2026-10-18 unless a different date is stated.

No vehicle interaction, update installation, dealer diagnostic session, network capture,
or hardware work was performed for this artifact. This document maps evidence routes and
their limits; it does not report observations from the owner's car.

## 1. Scope and reading rules

This artifact covers:

- R2: owner-accessible passive and runtime observations on the car, including screens,
  official update media metadata, documented diagnostics/log exports, USB enumeration,
  phone projection, Bluetooth, Wi-Fi/LTE behaviour, and passive radio observation that
  does not inject, associate, impersonate, or modify.
- R3: later-stage, non-invasive through invasive hardware evidence acquisition on a
  spare or bench unit, including public parts data, regulator filings, teardown imagery,
  spare-unit acquisition, storage imaging, UART/JTAG/eMMC, and test points as
  architecture-level options only.

This artifact deliberately does not contain:

- dealer-mode entry sequences, passwords, engineering-mode paths, or reset procedures;
- wiring, connector pinouts, UART/JTAG/eMMC pad maps, or instructions to probe the car;
- firmware execution, update installation, root, exploit, bypass, or disable steps;
- vehicle mutation, live-bus probing, or any instruction to alter the car.

Source-strength labels used throughout:

| Label | Meaning |
|---|---|
| A0 | Direct owner observation or owner-supplied capture from the target car/unit; strength depends on the method, instrumentation, and redaction, and it is not a manufacturer or regulator source. |
| A1 | Hyundai official current/archival owner, service, warranty, or update documentation. |
| A2 | Hyundai official marketing or press material. |
| B1 | Government/regulator material or regulator-hosted filing. |
| B2 | Authoritative third-party industry body, service-information authority, or standards body; not the manufacturer or a government regulator. |
| C1 | Peer-reviewed or original research with a stated method. |
| C2 | Professional teardown with a public summary; full report may be paywalled. |
| D1 | Community research, parts reseller, used-parts listing, or forum evidence used only as corroboration or hypothesis. |
| D2 | Third-party mirror, index, or transcription of a regulator/manufacturer filing; useful for discovery but not verified as an authoritative copy. |
| E1 | Generic automotive inference, not direct evidence for this vehicle. |
| T1 | Accepted internal task contract; not a public source and not independently re-proven here. |

Claim labels:

- OBS: directly stated by a cited source, or directly observable in the cited screen/page.
- INF: reasoned from cited evidence but not directly stated for this exact AU unit.
- UNK: not established by the public or owner-accessible evidence reviewed here.

## 2. Bottom line

The practical sequence is:

1. Freeze identity and privacy controls.
2. Capture only owner-visible screens and metadata, without pressing Update, Default, or
   any dealer/service action.
3. Download official update media on a PC and hash it. Do not install it merely to collect
   evidence: Hyundai's AU notice says installation cannot be reverted.
4. Observe USB and phone-projection behaviour with an inline USB analyzer and trusted
   media/phones. Do not use update-bearing media.
5. If needed, perform short passive Wi-Fi/Bluetooth observation with no association,
   injection, impersonation, or payload capture. The AU manual and product specification
   list LTE and Bluetooth 4.2 while omitting Wi-Fi; that documents a cellular capability
   and a missing documented Wi-Fi feature, not LTE exclusivity or absent Wi-Fi hardware.
   A negative RF result is expected but weak.
6. Use a Hyundai dealer or authorised service-information subscriber for documented
   diagnostic data. GDS/GSW access is restricted, paid, and can mutate the vehicle; a
   read-only request must be explicit.
7. Move hardware work to a matching spare/bench unit. Photograph labels and boards first;
   keep storage imaging, UART, JTAG, and eMMC work bench-only, and classify physical
   invasiveness and restoration outlook separately for each method.

The central unresolved question is not whether this is a Gen5W-family unit. The accepted
contract and Hyundai's AU update table point to that family. The unresolved question is the
exact AU hardware configuration and part identity: SoC, RAM, storage medium, radio module,
Wi-Fi hardware presence, USB role, service connector, debug access, and the unit label's
exact part number.

The `AVN5W` name is not part of the 2021 identity rationale. It appears in 2024 US service
material (C-11), which is a later-model analogy for naming and part-prefix context only.
Nothing in this artifact uses it to establish the 2021 Australian unit's family, part
number, or hardware.

### 2.1 Consolidated route matrix

The matrix carries three dimensions beyond the action itself: the minimum instrument class
each route needs ("minimum tools" names a class of equipment, not a procedure), the
safety/warranty exposure a mistake would create, and the evidentiary value that route can
actually deliver. Warranty exposure cites the AU warranty terms in C-10; installation
cannot be reverted per the AU notice in C-09.

| Route | Physical/electrical action | Minimum tools | Possible persistent software state | Restoration | Safety / warranty risk | Evidentiary value | Principal limit |
|---|---|---|---|---|---|---|---|
| 4.1 Owner screens | None if Update, Default, and dealer actions are avoided | Camera or screen capture; no diagnostic equipment | Timestamps, counters, usage history, What's new, indexing, logs | Physical state restored; software state not guaranteed | None expected from viewing menus; Update, Default, and dealer actions are excluded from this route | Low-to-medium: user-facing build, feature, and Device ID facts; cannot establish internal hardware | UI-only; Device ID and exact part number remain sensitive/unknown |
| 4.2 Official media metadata | PC download only; car untouched | PC browser, `curl` or equivalent, SHA-256 tool, archive inspector; updater client on the PC only | Local files, hashes, download history | Download reversible; installing the media on the car is not (C-09) | None to the car while the media stays on the PC; installing via USB is a different route with its own exposure | High for package name, size, hash, and model/version metadata; proves the published media, not the installed build | Exact AU variant mapping and package signature unknown |
| 4.3 Dealer diagnostics | Diagnostic connection; transmits requests and may mutate wake/session/log state even when non-actuating | GDS/GDS-M or compatible tester; authorised GSW or AASRA access | Module wake, session/log/counter changes; DTC clear, coding, update, or reset changes | Non-actuating is not state-free; mutating actions may not be reversible | Highest of the low-invasiveness routes: outstanding campaigns may be applied, and testing or repair outside an authorised dealer can affect warranty coverage (C-10) | Highest for module inventory, DTC history, and part family; limited on security policy unless the service matrix is exposed | GSW access/licence; raw log export unknown |
| 4.4 USB enumeration | Passive inline tap; no electrical mutation | USB protocol analyzer rated for the observed link speed (not a generic logic analyzer); clean test drive; clean test phone | Logs, media indexes, device/pairing entries, caches | Electrical state restored; persistent entries may remain | Low electrical risk; the connection itself creates device and index state; update-bearing media is excluded | Medium-high for USB role, descriptors, and projection protocol; low for internal storage or credentials | USB speed/role and internal filesystem unknown |
| 4.5 Projection/BT/LTE | Normal cable/pairing; no injection | Clean test phone; ordinary cables; OS-level pairing records | Pairing entries, contact/message caches, device state | Clean test phone and deletion reduce, but do not guarantee, reversal | Low mechanical and electrical risk; personal-data exposure is the main hazard | Medium for supported protocols and pairing behaviour; cannot show RF internals or telematics provisioning | Wireless projection unknown; personal-data exposure |
| 4.6 Passive RF | Monitor only; no association or injection | Receive-only receiver or SDR with transmit disabled; shielded enclosure for bench work | No vehicle state, but capture data exists | Stop capture and delete raw data | No vehicle state expected; legal and privacy limits apply to capture and retention | Low: a negative result is weak, and a positive result is generic to the radio technology | Legal/privacy limits; negative result is weak |
| 5.1 Service docs | Desk review or dealer session | Desk review: public documents only. Dealer session: as 4.3 | Diagnostic/session changes if mutating | Documentation review reversible; diagnostic actions conditional | Documentation review carries none; any dealer action inherits the 4.3 campaign and warranty exposure | High for documented function, procedure, and module names; not proof of the fitted build | AU procedure and DTC/log coverage unknown |
| 5.2 Parts lookup | No car interaction | VIN-scoped dealer parts query; resale listings only as corroboration | Seller/listing metadata only | Financial resale; label verification | No car state; wrong-part purchase risk | Medium for part family and fitment; resale listings are D1 | Exact AU part number unknown |
| 5.3 FCC/RCM | Desk review or spare label | Public filing databases; label photography on a spare unit | Label/photo identifiers; no car state | Reversible | No car state | Medium for radio and module identity; mirror provenance limits apply (D2) | FCC mirror provenance; FCC is not AU approval |
| 5.4 Teardown imagery | Desk review or spare exterior | Public teardown reports; spare-unit exterior photography | Photo metadata only | Reversible | No car state | Medium for family-level board layout and module identity; not AU-specific | Family-level; exact AU board unknown |
| 5.5 Spare/bench power | Bench power; no car interaction | Current-limited bench supply; bench harness; serial console only if one is present | Boot logs, counters, error records, first-run state, indexing | Electrical state restorable; software state may persist | No effect on the car while the car stays untouched; the spare unit can be altered irreversibly | High for hardware identity, boot behaviour, and first-run state; needs a matching spare | Part/region/lock and bench wake-up unknown |
| 5.6 Storage/debug | Bench only; destructive or conditionally invasive depending on method | Bench-only; method-specific (eMMC reader, UART, JTAG) | Partition, log, and stored-material exposure possible; logs and counters may change | Conditional on method, damage, and security state | Method-dependent: chip-off is destructive; accessible-header, in-circuit, UART/JTAG, or vendor-service methods may be non-destructive but still risk damage, and persistent software or security-state change remains possible; no effect on the car only while the car stays untouched | Highest for firmware, partitions, and stored material; reversibility is method-dependent (lowest for chip-off; higher where access is read-only) | Exact pads, encryption, and test points unknown |

## 3. Identity: what is established and what is not

### 3.1 Established by the accepted contract and official update table

| Claim | Label | Evidence |
|---|---|---|
| The AU update table lists 2021-23 IONIQ 5 as Standard Gen5W Navigation with software `NE_E.AUS.S5W_L.001.001.260319`, map `AUS.19.41.47.011.611.0`, model `NEAE.S5BLN.AAU`. | OBS | Hyundai AU update popup, accessed 2026-10-18: https://update.hyundai.com/AU/EN/updateNoticePopup/aiD0Sq |
| The same table lists 2024-25 IONIQ 5 as ccNC, separating the earlier Gen5W branch from the later system. | OBS | Same AU update popup. |
| Hyundai service language calls the **2024** IONIQ 5 unit `AVN5W` and gives a `96560*` part-number prefix. This is US service material for a later model year, not AU parts data, and it is not used as 2021 identity evidence. | OBS for the 2024 US TSB; later-model analogy only | HMA TSB 24-01-002H, PDF: https://static.nhtsa.gov/odi/tsbs/2024/MC-10249697-0001.pdf |

The model string `NEAE.S5BLN.AAU` and the software string are the strongest public
identity anchors available without reading the car. They should be captured from the car's
own version screen and compared exactly, character by character, before any later-stage
work.

The `AVN5W` row is retained so that a later reader does not confuse it with the 2021
evidence. It applies to the 2024 model year, in the US market, and only to naming and
part-prefix context. It does not establish the 2021 Australian unit's family, part number,
SoC, or any other hardware property.

### 3.2 Not established

| Unknown | Why it matters | Current status |
|---|---|---|
| Exact AU head-unit part number and serial/label identity. | A US/EU part number does not prove AU fitment, radio approvals, or software branch. | UNK. Read the label only on a spare/bench unit or obtain the VIN-scoped dealer parts result. |
| Exact SoC, RAM, storage size and storage medium for the AU unit. | TechInsights describes one IONIQ 5 head unit, but not the AU variant. | UNK for AU. Family-level teardown data only. |
| Whether a Wi-Fi radio and antenna are fitted, even though the AU manual/spec do not expose Wi-Fi. | A passive Wi-Fi observation can be falsely negative. | UNK. Treat "no Wi-Fi menu" as a user-facing fact, not a hardware fact. |
| USB port electrical role and speed. | Determines whether an inline analyzer can see mass-storage and projection descriptors. | UNK until observed. |
| Whether wireless Android Auto/CarPlay is supported. | The AU manual describes USB-cable connection only. | UNK; no official wireless support found. |
| AVN diagnostic trouble codes, freeze frames, and log-export format. | GDS may expose more than the owner UI. | UNK publicly; dealer/GSW access required. |
| UART/JTAG/eMMC test points and service connector. | Needed only for bench-level hardware work. | UNK; no exact AU map found. |
| AU RCM supplier declaration or per-product approval record. | FCC records are US approvals, not AU. | UNK; RCM label on the unit is the practical artefact. |

## 4. R2: owner-accessible passive and runtime routes

### 4.1 Owner-visible software and build screens

The Australian Gen5W manual's own paths are:

| Screen | Exact documented path | What it can establish | Sensitivity and handling |
|---|---|---|---|
| Version info/Update | `SETUP > General > Version info/Update` | Software version, firmware version, navigation application version, map version, and Device ID. | Device ID is explicitly shown. Redact it from every committed image or note. |
| System info > Memory | `SETUP > General > System info > Memory` | Total, used, and remaining memory for voice memos. | Low sensitivity by itself; do not export voice memos. |
| System info > Manual | `SETUP > General > System info > Manual` | QR code to the web manual. | Low sensitivity; QR may contain a session/URL. Crop or re-render. |
| System info > What's new | `SETUP > General > System info > What's new` | Update history, if the system has been updated. | Low sensitivity. |
| System info > Modem information | `SETUP > General > System info > Modem information` | Presence and identity of the cellular modem. | May expose IMEI/ICCID or subscriber data. Redact. |
| Phone connection > Phone connection | `SETUP > Phone connection > Phone connection` | Paired device list, connection status, auto-connection priority. | Contains phone names and possibly addresses. Redact all names and identifiers. |
| Phone connection > Bluetooth system info | `SETUP > Phone connection > Bluetooth system info` | Editable vehicle Bluetooth name and passkey. | Vehicle name is an identifier; passkey is an authentication secret. Never commit either. |
| Phone connection > Phone projection settings | `SETUP > Phone connection > Phone projection settings` | Whether Android Auto and Apple CarPlay are enabled. | Low sensitivity; screen may show a connected phone name. Redact. |
| General > Default | `SETUP > General > Default` | Resets profile or system. | Do not press. This is a state-changing action, not evidence collection. |

Sources:

- Hyundai AU Gen5W manual index: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/
- General/version/system-info page: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/general.html
- Phone-connection page: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/phoneconnection.html

What this route establishes:

- The exact installed software/version tuple, including whether the car matches the accepted
  contract.
- The visible map version and navigation application version.
- Whether the unit exposes a Device ID and a modem information screen at all.
- Whether the owner-facing Bluetooth name/passkey are still at defaults.

What it cannot establish:

- The head unit's part number.
- The SoC/RAM/storage configuration.
- The public sources here do not independently establish the OS; the accepted T1 contract
  identifies the Linux branch.
- Whether hidden engineering or dealer modes exist. Those are out of scope here.

Prerequisites and tools:

- Parked car, ignition on or accessory mode as required by the screen; no driving.
- Camera or phone camera, with location services and cloud sync disabled for the capture.
- A redaction checklist before the first image is committed.

Invasiveness, state change, and reversibility:

- Physical/electrical mutation: none, provided Update, Default, and dealer/service actions
  are not pressed.
- Software-state mutation: possible. Viewing screens can update last-viewed timestamps,
  counters, usage history, notification/What's new state, media/device indexing, or
  diagnostic logs. Physical setup restoration does not guarantee the prior software state.
- Reversibility: the physical/electrical state returns to prior, but persistent
  UI/log/counter state may remain and may not be individually removable. Record the
  visible before/after state where practical.
- Residual risk: a screen may expose Device ID, phone names, or modem identifiers. Treat the
  raw image as sensitive even if the visible version data is not.

Exact-model unknowns:

- Whether the AU unit shows the same labels and order as the AU manual's screenshots.
- Whether the Device ID is stable across resets, and whether it is derived from hardware.
- Whether Modem information is present on a non-Bluelink or non-activated unit.

### 4.2 Official update media metadata

Hyundai's AU notice and update table provide the public metadata anchor. The June 2026
notice is dated 19-Jun-2026 and covers Standard Gen5W Navigation among other units. It
states that after installation it is not possible to revert to the previous software
version, that the update media must be prepared with the official Navigation Updater
(NaU), and that a USB flash drive must be exFAT-formatted when the unit has no SD card.

Sources:

- AU notice list: https://update.hyundai.com/AU/EN/updateNoticeList
- 2026 June Infotainment Update: https://update.hyundai.com/AU/EN/updateNoticeView/yNDC3y
- AU update popup with the exact IONIQ 5 row: https://update.hyundai.com/AU/EN/updateNoticePopup/aiD0Sq
- AU update guide: https://update.hyundai.com/AU/EN/updateGuide/04

What this route establishes:

- The official release date and the supported unit family.
- The exact public version/model strings.
- The official tool and media requirements.
- That installation is a one-way state change from Hyundai's perspective.

Recommended capture:

- Record the NaU installer version, download date, selected vehicle type, selected model
  year, downloaded file names, byte sizes, and SHA-256 of each downloaded file.
- Preserve the official notice URL and a PDF or screenshot of the relevant notice.
- Record whether the selected vehicle in NaU is the 2021-23 IONIQ 5 Standard Gen5W entry,
  not the 2024-25 ccNC entry.
- If the package manifest is readable, record its version and model fields. Do not unpack or
  execute firmware as part of this route; that belongs to the package-static track.

Prerequisites and tools:

- PC with the official NaU application; a clean download directory; a USB drive only if
  download-only operation requires it.
- Sufficient free space and a stable connection.
- A hash tool and a manifest entry for every downloaded file.

Invasiveness and reversibility:

- Invasive to the vehicle: none if the media is never inserted into the car.
- Reversible: download-only is reversible by deleting the local copy.
- Not reversible: installation. Do not insert the prepared USB or press Update as an
  evidence step.

Risks:

- Selecting the wrong model/year can produce a package that the car will not accept.
- Hyundai explicitly warns that update installation cannot be reverted.
- A partial or interrupted download can corrupt the media.
- The update may change the UI and remove or alter features; that would contaminate later
  runtime comparisons.

Exact-model unknowns:

- Which package variant NaU serves for this exact AU VIN/model string.
- Whether the AU package is a full image, delta, encrypted container, or mixed set.
- Whether the package contains a signed manifest usable as an authenticity anchor.
- Whether the public version string maps to the June 2026 notice by build date or by
  publication date; the table does not state that mapping explicitly.

### 4.3 Documented diagnostics and log exports

The owner-accessible AU manual pages reviewed here document System info and Modem
information; this review did not find a documented raw system-log export. The publicly
visible service route is Hyundai Global Service Way (GSW), which the Australian Automotive
Service and Repair Authority (AASRA) describes as containing Shop Manual, ETM, DTC,
Owner's Manuals, Service Information, OBDII Information, and ACU Coding Information for
Hyundai vehicles sold in Australia.

Sources:

- AASRA Hyundai portal page: https://aasra.com.au/?page_id=1037
- Hyundai GSW login: https://service.hyundai-motor.com/euro5/loginAasra.tiles?siteCd=H
- HMA TSB 24-01-002H: https://static.nhtsa.gov/odi/tsbs/2024/MC-10249697-0001.pdf

What this route can establish:

- AVN diagnostic trouble codes, modem activation state, and service procedures, if a
  dealer or authorised GSW subscriber performs the read.
- Whether a documented service reset or update is applicable. This artifact does not
  reproduce those procedures.
- Whether the head unit is recognised as a genuine Hyundai part and what part family the
  service system expects.

Prerequisites and tools:

- Hyundai dealer access, or an AASRA/GSW account tied to an Australian repairer or RTO.
- GDS/GDS-M or compatible diagnostic hardware. AASRA lists paid access tiers; the exact
  current price and eligibility must be confirmed on the site.
- An explicit read-only scope: no DTC clearing, no ECU update, no coding, no reset.

Invasiveness and reversibility:

- A diagnostic read is non-invasive to the vehicle's physical state, but GDS sessions can
  clear codes, change adaptations, or update firmware. Those actions are not automatically
  reversible.
- GSW's EULA restricts copying, republishing, and use outside the platform. Do not commit
  service-manual content or screenshots without checking the licence.

Risks:

- A dealer visit may apply outstanding campaigns or updates unless the owner explicitly
  asks for a read-only session.
- Diagnostic data can contain VIN, odometer, device identifiers, and location history.
- GSW access is not an individual-owner public service; eligibility and confidentiality
  terms apply.

Exact-model unknowns:

- Whether GDS exposes an AVN log export, or only DTC/status screens.
- Whether the AU 2021 unit's AVN DTC list resembles the US 2024 `AVN5W` list, which would
  be a later-model analogy and not a fitment claim.
- Whether any owner-visible Bluelink diagnosis produces a raw report or only a summary.

### 4.4 USB enumeration and metadata

The AU manual documents USB media playback and USB-cable phone projection. It does not
document a USB host shell, ADB, or a diagnostic USB mode. The practical passive route is an
inline USB protocol analyzer between the car's USB port and a known device. The tap is
electrically passive, but the connection itself can still create software state on the
head unit.

Sources:

- AU phone projection page: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/phoneprojection.html
- AU USB general information: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/generalinformation.html
- AU USB music page: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/playingusbmusic.html
- AU USB video page: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/playingusbvideo.html

What this route can establish:

- USB device enumeration: VID, PID, bcdUSB, device class, configuration, interface classes,
  string descriptors, and endpoint layout.
- Whether the port enumerates a mass-storage device, an MTP/PTP device, an Apple
  CarPlay interface, or an Android Open Accessory interface.
- SCSI INQUIRY/READ CAPACITY and read-only traffic for a known USB drive.
- Timing and retry behaviour when a phone is connected or disconnected.
- Whether the head unit creates a media index, device/pairing entry, or cached projection
  metadata, by comparing the owner UI before and after.

What it cannot establish:

- Internal filesystem layout, partitions, or stored credentials.
- Whether the port is USB 2.0 or 3.x from the physical connector alone.
- Whether a hidden diagnostic or debug interface exists behind a vendor-specific request.

Prerequisites and tools:

- A speed-qualified USB protocol analyzer rated for the link under test, for example a
  Total Phase Beagle USB 480 for USB 2.0 High Speed, a Beagle USB 5000 or Ellisys Explorer
  for USB 3.x/SuperSpeed, or an equivalent rated analyzer, plus an appropriate inline
  breakout. A generic logic analyzer is not assumed adequate for High Speed or SuperSpeed
  USB.
- A known, trusted USB drive with benign media only, plus known phones and original cables.
- A powered analyzer and a laptop with capture storage outside Git.
- Parked car; no update files on any device; no untrusted USB device.

Invasiveness, state change, and reversibility:

- Physical/electrical mutation: none, if the analyzer is passive and the media is benign.
- Software-state mutation: possible even when the link is electrically read-only. The head
  unit may log the connection, index media, create a device/pairing entry, or cache
  metadata. Treat the prior software state as not guaranteed.
- Reversibility: unplugging restores the electrical connection, but a created log, index,
  or device entry may persist and may not be individually removable. Record the UI state
  before and after and prefer a clean test phone plus benign media.
- Residual risk: plugging an unknown device can trigger a parser or exploit. Use only
  trusted devices and read-only media.

Risks:

- A USB drive containing update files could cause the head unit to offer or start an update.
  Use a drive with no Hyundai update files and decline any update prompt.
- Descriptors and SCSI INQUIRY strings can contain device serial numbers; redact them.
- Some analyzers can inject traffic if misconfigured. Use a monitor-only/passive mode.
- A benign-looking drive or phone can still create media indexes, cached metadata, or a
  device/pairing entry. Do not use personal media or a personal primary phone.

Exact-model unknowns:

- USB speed and role of the AU port.
- Whether the port is a direct host controller or a hub.
- Whether CarPlay/Android Auto use the same port as mass storage.
- Whether the port remains powered in accessory/off states.

### 4.5 Phone projection, Bluetooth, Wi-Fi, and cellular behaviour

The AU manual describes Android Auto and Apple CarPlay as USB-cable functions, with the
phone's own cable recommended. It also documents a Bluetooth menu, editable vehicle name,
editable passkey, and a privacy mode that hides contacts, call history, favourites, and
messages. The AU product specification lists Bluetooth 4.2 with HFP 1.7, A2DP 1.3,
AVRCP 1.6, PBAP 1.2, and MAP 1.2, plus WCDMA and LTE receive/transmit bands, while omitting
Wi-Fi from the listed specification.

Sources:

- AU phone projection: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/phoneprojection.html
- AU phone connection: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/phoneconnection.html
- AU Bluetooth page: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/bluetoothwirelesstechnology.html
- AU product specification: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/specification.html

What this route can establish:

- Whether wired Android Auto/CarPlay are enabled and actually enumerate.
- Whether the head unit is discoverable over Bluetooth, what name it advertises, and which
  profiles it negotiates during a normal pairing.
- Whether the unit exposes a Wi-Fi menu, Wi-Fi MAC address, or hotspot at all.
- Whether the cellular modem is present and what modem status the owner UI shows.

What it cannot establish:

- Whether the unit has Wi-Fi hardware that is disabled or hidden.
- Whether wireless Android Auto/CarPlay is supported but not documented.
- Internal protocol implementation, credentials, or service secrets.

Recommended capture:

- Wired projection: a short screen recording of the enable/connect/disconnect sequence,
  plus USB analyzer descriptors. Do not capture contacts, messages, notifications, or
  navigation history.
- Bluetooth: a passive over-the-air scan first. If pairing is required, use a dedicated test
  phone with no personal accounts, disable contact/message sync, and enable privacy mode.
  Record the advertised name and profile list, not the passkey.
- Wi-Fi: first check whether the AU menu exposes any Wi-Fi/Data Network screen. If it does
  not, record that negative UI result. Do not attempt to enable hidden Wi-Fi features.
- Cellular: record modem information and signal state if the owner UI exposes it. Do not
  attempt to intercept LTE traffic.

Prerequisites and tools:

- A test phone with a clean profile, original cable, and no sensitive accounts.
- A laptop with a supported Wi-Fi monitor-mode adapter or a Bluetooth passive sniffer if RF
  observation is separately authorised.
- Screen-recording tool with notifications disabled.

Invasiveness and reversibility:

- Normal pairing/projection is reversible by deleting the pairing and disconnecting the
  cable. It can leave contact/message caches on the head unit; use privacy mode and do not
  sync personal data.
- Passive RF observation does not mutate the car.
- Do not create a hotspot with the same SSID, deauthenticate, inject frames, or impersonate
  the head unit.

Risks:

- Phone projection exposes personal data by design; the clean test phone is the control.
- Bluetooth pairing can expose contacts, call logs, and messages if permissions are
  granted. Do not grant them for evidence collection.
- Wi-Fi captures can include bystander devices and locations. Minimise duration and
  channels, and delete raw captures after extracting redacted facts.

Exact-model unknowns:

- Whether Wi-Fi is present but not exposed in the AU branch.
- Whether the AU unit supports wireless projection.
- Whether the LTE modem is integrated in the head unit or in a separate telematics module.
- Which cellular bands are actually active on the AU carrier and subscription.

### 4.6 Passive network observation without injection

This route is optional and should be separately authorised. It is useful only for
establishing whether the unit emits or seeks RF, not for reading encrypted content.

| Medium | Passive method | What it can establish | Hard limits |
|---|---|---|---|
| Wi-Fi | Monitor-mode capture with a supported adapter; no association, no injection. | Whether the unit emits beacons, probes, or association attempts; MAC/OUI if visible. | Encrypted payloads are not readable; absence may mean the radio is off or absent. |
| Bluetooth | Passive advertising/inquiry capture with a dedicated sniffer; no pairing. | Advertised name, address, class of device, and advertising behaviour. | Classic Bluetooth discovery may require an active inquiry; that is a query, not injection, but should be labelled as active. |
| Cellular | No passive capture in this scope. | Nothing without SDR and legal/technical review. | Out of scope; do not attempt to intercept or impersonate the network. |

What this route can establish:

- A bounded, time-stamped RF presence/absence observation.
- Whether the unit's Bluetooth name or address is stable across power cycles.
- Whether a Wi-Fi radio is active despite no documented AU Wi-Fi menu.

Prerequisites and tools:

- A supported monitor-mode Wi-Fi adapter and `tshark`/Wireshark, or a dedicated Bluetooth
  sniffer.
- A short, fixed observation window and a channel plan.
- A laptop with captures stored outside Git.

Invasiveness and reversibility:

- No vehicle mutation and no association.
- Fully reversible; stop the capture and power down the adapter.

Risks:

- Capturing bystander devices and location-correlated data.
- Legal/privacy obligations in Australia; the owner should confirm that the observation is
  lawful and proportionate before capturing.
- A negative result is weak evidence because the radio may be off, sleeping, or absent.

Exact-model unknowns:

- Whether the AU unit has an active Wi-Fi radio.
- Whether Bluetooth is discoverable only during pairing.
- Whether the unit's RF behaviour changes with ignition state or Bluelink activation.

## 5. R3: later-stage hardware and documentation routes

### 5.1 Service documentation and dealer diagnostics

Hyundai's AU service information is distributed through GSW/AASRA, not as a free public
manual. AASRA states that GSW contains the Shop Manual, ETM, DTC, Owner's Manuals, Service
Information, OBDII Information, and ACU Coding Information, and lists paid access tiers
(for example, daily A$18.50+ and weekly A$75+ for five days at the time of access). The
GSW EULA restricts copying and republishing and limits use to authorised repairers/RTOs.

Sources:

- AASRA Hyundai page: https://aasra.com.au/?page_id=1037
- GSW login/EULA: https://service.hyundai-motor.com/euro5/loginAasra.tiles?siteCd=H

What it can establish:

- The exact AU service procedure, connector identification, removal sequence, and DTC
  coverage, if accessed lawfully.
- The part family and replacement procedure expected by Hyundai for this VIN.
- Whether a documented AVN diagnostic or reset procedure exists.

Prerequisites and tools:

- Dealer access, or an eligible AASRA/GSW account.
- GDS/GDS-M or compatible diagnostic hardware.
- A written read-only scope and owner authorisation.

Invasiveness and reversibility:

- Documentation review: non-invasive.
- Diagnostic session: potentially state-changing. DTC clearing, coding, resets, and ECU
  updates may not be reversible.

Risks:

- Warranty and configuration risk from dealer-mode resets or updates.
- Confidentiality/licence risk from copying GSW content.
- Personal data in diagnostic reports (VIN, odometer, location, device identifiers).

Exact-model unknowns:

- Whether the AU 2021 unit has a different service connector or removal procedure from the
  US 2022-24 unit.
- Whether the AVN exposes a diagnostic log or only DTC/status data.
- Whether a dealer-mode reset affects user profiles, paired phones, or navigation data.

### 5.2 Public parts catalogs and service part numbers

Public parts catalogs are useful for generating a spare-unit shortlist, not for proving AU
fitment. The following numbers appear in public listings:

| Part number | Context | Source strength | What it supports | What it does not prove |
|---|---|---|---|---|
| `96560-GI870` | IONIQ 5 2021+ used GPS/navigation unit, EU/used-parts listings. | D1 | A plausible Gen5W head-unit family for 2021+ cars. | AU fitment, AU radio approvals, or exact software branch. |
| `96560-GI580` | US 2022-24 IONIQ 5 "Head unit assy avn", standard sound system. | D1 | US parts family and connector/body similarity hypothesis. | AU part identity. |
| `96560-GI730` | US 2024 IONIQ 5 AVN5W causal part in a Hyundai TSB. | A1 for the US TSB; D1 for fitment | Hyundai service uses the `96560` family for AVN5W. | AU part number or AU compatibility. |
| `94003-GI030-YPK` | IONIQ 5 instrument cluster/display unit, not the infotainment head unit. | D1 | Prevents a common mis-buy. | Nothing about the AVN head unit. |

Sources:

- US parts diagram: https://www.hyundaipartscounter.com/v-2022-hyundai-ioniq-5--se-standard-range--electric/entertainment-and-telematics--mobile-multi-media
- US head-unit listing: https://www.hyundaipartsdeal.com/genuine/hyundai-head-unit-assy-avn~96560-gi580.html
- EU used unit: https://partsouq.com/shop/product/96560GI870-hyundai-kia-head-unit-assy-avn/17664232
- EU used unit: https://www.bruktdel.no/nbf/Bildeler/hyundai/ioniq-5-ne-2022--/gps-navigator/3653-361724/
- US TSB with `96560-GI730`: https://static.nhtsa.gov/odi/tsbs/2024/MC-10249697-0001.pdf
- Hyundai AU genuine-parts page: https://www.hyundai.com/au/en/owning/servicing/parts

What this route can establish:

- A shortlist of plausible part numbers for spare-unit shopping.
- Whether a seller's label photo matches the expected family.
- Whether the unit is a display/cluster part rather than the AVN head unit.

Prerequisites and tools:

- VIN-scoped dealer parts lookup for the exact AU car.
- Seller-provided label photo with the full part number and software version.

Invasiveness and reversibility:

- No vehicle interaction.
- Purchase is financially reversible only by resale; verify seller terms.

Risks:

- Wrong-region unit, wrong software branch, counterfeit, water damage, or theft
  provenance.
- A used unit may contain the previous owner's contacts, messages, locations, or accounts.

Exact-model unknowns:

- The exact AU part number and suffix.
- Whether an EU/US unit can be made to work in the AU car without dealer coding; do not
  assume it can.
- Whether the AU unit uses a different radio module or antenna configuration.

### 5.3 Regulatory filings and RCM evidence

FCC records are US equipment authorisations. They are useful for architecture and board
imagery, but they do not establish Australian compliance or AU fitment. The following
Hyundai Mobis filings are in the relevant Gen5W era:

These exhibits were fetched from the third-party `fccid.io` mirror, not directly from the
FCC's EAS system. They are FCC-origin filings in substance, but the fetched pages and PDFs
are mirror copies. Their provenance, document identity, and byte-for-byte authenticity
against the originating FCC record were not independently verified here. Automated access
to the FCC EAS copies returned HTTP 403 during this review.

| FCC ID | Applicant/date | Frequencies and exhibits | Relevance and limits |
|---|---|---|---|
| `TQ8-VN470ZZZAN` | Hyundai Mobis, 2022-12-18 | 2402-2480 MHz, 2412-2462 MHz, 5745-5825 MHz; internal photos, label, user manual, test reports. | Plausible Gen5W/AVN radio assembly; user manual covers multiple models; AU fitment not proven. |
| `TQ8-DA471ZZZAN` | Hyundai Mobis, 2022-12-26 | 2402-2480 MHz, 2412-2462 MHz, 5745-5825 MHz; internal photos, label, user manual, test reports. | Another Hyundai Mobis infotainment radio assembly; exact vehicle fitment not proven. |

Sources (third-party mirror):

- FCC VN470: https://fccid.io/TQ8-VN470ZZZAN
- FCC VN470 user manual: https://fccid.io/TQ8-VN470ZZZAN/User-Manual/User-Manual-6282809.pdf
- FCC VN470 internal photos: https://fccid.io/TQ8-VN470ZZZAN/Internal-Photos/Internal-Photo-6282810.pdf
- FCC DA471: https://fccid.io/TQ8-DA471ZZZAN
- FCC DA471 internal photos: https://fccid.io/TQ8-DA471ZZZAN/Internal-Photos/Internal-Photo-6295876

Useful filing metadata:

- The VN470 label PDF has SHA-256
  `2bbbdb1f7c59dc8458a35fad8f08bc23412ce94658db6f307377a717fdd98a8c`.
- The DA471 internal-photo PDF has SHA-256
  `6d1238e6180d9fe137ef080a0270cd3e77d636bfd8d277507b0fee647776cfab`.
- These hashes are as displayed by the third-party mirror on 2026-10-18. They identify the
  mirror's displayed files, not an independently verified FCC EAS copy; re-hash after
  download and verify against the originating FCC record before evidentiary use.

Australian RCM:

- ACMA describes the supplier obligations: check the rules, show compliance, sign and keep
  records, register as a responsible supplier, and label the product with the RCM. ACMA
  also warns that overseas markings alone are not sufficient.
- The EESS describes the RCM as the Australian compliance mark owned by the electrical
  regulators and ACMA.
- No public per-product RCM supplier declaration for this exact AU head unit was found in
  the bounded searches below. That is a search result, not proof that no declaration exists.

Sources:

- ACMA supplier obligations: https://www.acma.gov.au/know-what-you-must-do
- EESS RCM: https://www.eess.gov.au/rcm/

What this route can establish:

- Board-level architecture, shield/connector layout, and radio frequencies from FCC exhibits.
- The presence of an RCM label on a bench unit.
- Whether the label's model/part number matches the AU car's parts record.

Prerequisites and tools:

- Access to the originating FCC record (preferred) or a third-party mirror for discovery;
  mirror copies require document-ID, hash, and provenance verification against FCC EAS.
- A bench unit's label and RCM mark, photographed at high resolution.

Invasiveness and reversibility:

- Public filing review: non-invasive.
- Reading a label on a spare unit: non-invasive.
- Reading a label on the car's installed unit may require trim removal; that is a later-stage
  vehicle intervention, not part of R2.

Risks:

- FCC approval is not AU approval; do not present it as such.
- FCC internal photos may reveal board details but not the AU variant.
- A third-party mirror may differ from the FCC-originating exhibit; verify the document ID,
  file hash, and cited content against FCC EAS before relying on it.
- Regulatory labels can include identifiers that should not be published.

Exact-model unknowns:

- Whether either FCC filing corresponds to the AU 2021 unit.
- The AU RCM supplier code and approval record.
- Whether the AU unit uses the same radio module/antenna set as the FCC sample.

### 5.4 Teardown imagery and original research

The strongest public teardown summary for the IONIQ 5 head unit is TechInsights'
17 February 2023 article. It describes:

- Intel 1.8 GHz dual-core Atom application processor.
- 4 GB LPDDR4 SDRAM.
- 128 GB internal storage.
- An LTE board with a Qualcomm multimode baseband processor and power-management IC.
- 512 MB SLC NAND and 256 MB mobile LPDDR2 SDRAM on the LTE board.
- Infineon secure microcontroller and power-conversion devices on the main board.
- Release date January 2021 and global target market.

Source:

- TechInsights public summary: https://electronics360.globalspec.com/article/19251/techinsights-teardown-hyundai-ioniq-5-head-unit
- TechInsights product page: https://www.globalspec.com/FeaturedProducts/Detail/Techinsights/340226/Techinsights_Teardown_Hyundai_Ioniq_5_head_unit

What this route can establish:

- A family-level architecture and a realistic expectation for the AU unit.
- The presence of an LTE subsystem, consistent with the AU manual's LTE bands.
- That the unit is not a simple MCU-only radio.

What it cannot establish:

- The exact AU part number, SoC variant, RAM/storage size, or storage medium.
- Whether the AU unit has Wi-Fi hardware.
- Any test point, connector pinout, or debug interface.

Other original research:

- Springer, "A vehicle firmware security vulnerability: an IVI exploitation" (2024),
  studies a Gen5W_L IVI in a Hyundai IONIQ Electric, not the IONIQ 5. It is family-level
  evidence for the existence of a Linux/IVI firmware update and cryptographic boundary, not
  evidence for the AU IONIQ 5 unit.
  https://link.springer.com/article/10.1007/s11416-024-00522-4
- MDPI, "Android-Based Audio Video Navigation System Forensics: A Case Study" (2023),
  describes chip-off eMMC acquisition on Android 4.4.2 AVN systems and identifies
  Bluetooth, navigation, and system-log artefacts. It is a method paper, not an IONIQ 5
  teardown.
  https://www.mdpi.com/2076-3417/13/10/6176
- `cantcs/HKG_Gen5W_ReverseEngineer` documents a Gen5W Android 4.4.2 variant, including
  eMMC boot-area and encrypted firmware observations. It is community research for a
  different Gen5W variant, not the AU Linux branch.
  https://github.com/cantcs/HKG_Gen5W_ReverseEngineer
- `laralbir/hyundai-kia-gen5w-navi-firmware` documents EU Gen5W firmware reverse
  engineering and mentions UART/GDS/engineering-mode topics. It is family-level context,
  not AU fitment or procedure.
  https://github.com/laralbir/hyundai-kia-gen5w-navi-firmware

Route properties:

- Prerequisites/tools: FCC-origin exhibits (with the mirror-provenance caveat above),
  MDPI, and TechInsights access for desk research; a matching bench unit and a camera for
  direct verification; no car access.
- Invasiveness: none for desk research or exterior photography of a spare. Board-level
  teardown belongs to 5.6 and is not part of this route.
- Reversibility: public-report review is fully reversible; exterior photography changes
  nothing. Destructive teardown can be irreversible or require repair, so it is not
  assumed reversible.
- Safety/warranty/privacy risks: misattributing a family-level teardown to the AU unit;
  paywalled or incomplete reports; board photos containing identifiers, serials, or
  personal data; damage if a spare is opened without ESD/rework controls.
- Exact-model unknowns: whether the photographed board matches the AU part revision; the
  exact storage medium; the exact radio module/antenna set; and whether the AU unit uses
  the same debug/test-point population as the photographed unit.

### 5.5 Spare/bench head-unit acquisition

A spare unit is the cleanest way to separate hardware evidence from the owner's car. It
also converts every destructive or state-changing action into a bench-only action.

Recommended acquisition criteria:

- Prefer a unit with a readable label photo showing the full Hyundai/Mobis part number,
  software version, and any RCM/FCC markings.
- Prefer a unit from the same region/software branch; EU and US units are not substitutes
  without evidence.
- Ask the seller whether the unit was reset/erased and whether it contains personal data.
- Avoid units with cut connectors, corrosion, water damage, or evidence of prior board work.
- Record the seller, listing URL, price, date, and return terms.

What this route can establish:

- The exact part number and label identity of the spare.
- External connector count and physical layout, without touching the car.
- A safe platform for board photographs and later bench work.

Prerequisites and tools:

- A matching or plausibly matching unit, a bench power supply, and the service manual for
  power/connector identification.
- A clean, ESD-safe bench and a camera with EXIF/location disabled.
- A plan for CAN/ignition wake-up if the unit requires vehicle messages; this is unknown
  and must be established from service documentation, not guessed.

Invasiveness, state change, and reversibility:

- No car interaction.
- Purchase is financially reversible only by resale.
- Physical/electrical: power-up can be reversed by removing power if no hardware
  modification was made.
- Software-state: power-up can create or update boot logs, counters, error records,
  first-run state, device entries, or indexing even without hardware modification.
  Power-down does not guarantee the prior software state.
- Reversibility: the physical setup can be restored, but persistent software state may
  remain.

Risks:

- Wrong-region or wrong-software unit.
- Counterfeit, stolen, or damaged goods.
- Previous owner's personal data on the unit.
- Persistent boot logs, counters, first-run state, or device entries may be created.
- Bench power or connector mistakes can destroy the unit.

Exact-model unknowns:

- The exact AU part number and suffix.
- Whether a spare unit will boot without vehicle CAN/IGN messages.
- Whether the unit is paired/locked to a VIN or vehicle configuration.
- Whether the AU unit's connector set matches the EU/US units.

### 5.6 Storage imaging, UART, JTAG, eMMC, and test points

These are architecture-level, later-stage options only. They are not owner-car procedures.
No pinout, pad map, or wiring is provided here.

Physical invasiveness and the probability of restoring a working unit are separate
questions. A destructive method can still leave a repairable board; a pad-level method can
be physically non-destructive yet leave persistent software or security changes.

| Option | What it can establish | Prerequisites | Physical invasiveness | Restoration outlook | Risks |
|---|---|---|---|---|---|
| eMMC chip-off and reader | Full physical image of the storage, partitions, logs, cached contacts, navigation data, and possibly keys. | Bench spare, hot-air/rework station, eMMC reader, NAND/eMMC expertise, forensics tooling. | Destructive: the chip is desoldered and the board/pads may be damaged; rework is required. | May be restored by reballing or replacing the eMMC, or by using a replacement board, but success is not guaranteed. The unit is not categorically destroyed. | Bricking, board damage, personal data, encryption, legal/privacy exposure. |
| In-circuit eMMC/ISP | Similar data, sometimes without chip removal. | Bench spare, service documentation or board-level tracing, suitable probe/reader. | Can be non-destructive if a suitable test point/connector exists; probing or soldering adds damage risk. | Often restorable if no damage occurs and the original state is preserved; not guaranteed. | Signal integrity, back-powering, boot contention, damage. |
| UART console | Boot logs, bootloader prompt, console access if a debug UART exists and is enabled. | Bench spare, board inspection, logic-level serial adapter, correct voltage. | Can be non-destructive with an accessible pad or connector; soldering or probing adds risk. | Usually restorable if the work is read-only and no damage occurs; not guaranteed. | Wrong voltage, short, bricking, security locks. |
| JTAG/SWD | CPU/core debug, memory access, halt/resume. | Bench spare, exact SoC documentation, debug probe, board access. | Can be non-destructive with an accessible debug header or pads; opening, soldering, or probing adds risk. | Usually restorable if no damage occurs and no security fuse is set; not guaranteed. | Security fuses, bricking, corruption. |
| Test points | Board-level observation points for power, clock, reset, or debug. | Board photographs, service documentation, microscope, probing tools. | Non-destructive only if probing is correct; any slip can damage. | Usually no change if read-only; damage can be permanent. | Shorts, ESD, incorrect assumptions. |
| Storage removal via service | Vendor-approved replacement or imaging. | Dealer/service access and authorised procedure. | Vendor-approved removal/replacement; still requires opening the unit. | Restorable if the service procedure and coding are followed; not guaranteed if configuration is lost. | Cost, confidentiality, configuration/coding, warranty. |

Public evidence supporting the method, not the exact AU map:

- MDPI's Android AVN forensic study uses chip-off eMMC acquisition and analyses Bluetooth,
  navigation, and system-log artefacts: https://www.mdpi.com/2076-3417/13/10/6176
- `cantcs/HKG_Gen5W_ReverseEngineer` discusses eMMC boot-area and encrypted firmware for a
  Gen5W Android variant: https://github.com/cantcs/HKG_Gen5W_ReverseEngineer
- TechInsights identifies 128 GB internal storage but does not state the storage medium:
  https://electronics360.globalspec.com/article/19251/techinsights-teardown-hyundai-ioniq-5-head-unit

What this route can establish:

- The storage medium and partition layout, if the exact board is examined.
- Whether logs, paired-device data, navigation history, or update metadata are recoverable.
- Whether debug interfaces are present and enabled.

What it cannot establish without exact-model work:

- That the AU board matches the FCC/TechInsights board.
- That the storage is unencrypted.
- That a UART/JTAG interface is populated or enabled.
- That a test point is safe to probe.

## 6. Staged plan and stop conditions

### Stage 0: Freeze identity and privacy controls

- Create a private evidence directory outside Git.
- Create the manifest before the first capture.
- Record the accepted T1 strings and the car's exact version-screen strings separately.
- Prepare redaction rules and a hash tool.
- Do not touch the car yet.

Gate: the manifest exists and the private directory is excluded from Git.

### Stage 1: Owner-visible screens

- Park safely; ignition/accessory as required.
- Capture Version info/Update, System info (Memory, What's new, Modem information), Phone
  connection, Bluetooth system info, and Phone projection settings.
- Record only visible fields; redact Device ID, phone names, modem identifiers, vehicle
  Bluetooth name, and passkey.
- Record the visible before/after state where practical; viewing screens may update
  timestamps, counters, notification/What's new state, or diagnostic logs.
- Do not press Update, Default, or any dealer/service action.

Gate: the version tuple matches or explicitly differs from the accepted contract; no
installation/reset/dealer action was pressed, and any UI-generated state is noted.

### Stage 2: Official media metadata

- On a PC, download the official NaU package for the 2021-23 IONIQ 5 Standard Gen5W entry.
- Record URLs, dates, file names, sizes, and SHA-256.
- Do not insert the media into the car.

Gate: the package is download-only and hashed; no installation occurred.

### Stage 3: USB and phone projection

- Use a passive USB analyzer and a clean test phone.
- Capture descriptors and a short connect/disconnect sequence.
- Use benign media only; no Hyundai update files.
- Do not grant contacts/messages permissions.
- Record the head-unit UI state before and after for media indexes, paired/device entries,
  and projection entries. These are software-state changes even when the electrical
  connection is passive.
- Prefer a disposable benign media set and a clean test phone; do not use personal media.

Gate: captures contain no personal data or are quarantined for redaction; any new
head-unit log/index/device entry is documented, and no update was triggered.

### Stage 4: Passive RF (optional, separately authorised)

- Use monitor mode or a passive Bluetooth sniffer only.
- Do not associate, inject, deauthenticate, or impersonate.
- Keep the window short and the channel plan fixed.

Gate: no third-party payload or location data leaves the private directory.

### Stage 5: Dealer/service documentation

- Ask for a read-only diagnostic report and VIN-scoped parts identification.
- Explicitly forbid DTC clearing, resets, coding, and ECU updates unless separately
  authorised.
- Do not copy GSW content outside the licence.

Gate: the report is understood as dealer-supplied evidence, not owner observation.

### Stage 6: Bench spare

- Acquire a matching or plausibly matching unit with a label photo.
- Photograph the exterior, label, RCM/FCC marks, and connectors before power.
- Record the visible first-power UI state and any counters/logs before and after power-up.
- Do not open the unit yet.

Gate: the part number and software version are recorded; the unit is not connected to the
car.

### Stage 7: Bench teardown and storage/debug work (optional)

- Photograph the board before and after each step.
- Use ESD protection and a current-limited supply.
- Start with non-destructive external inspection; then decide whether eMMC/UART/JTAG work
  is justified.
- Classify each step by physical invasiveness and restoration outlook separately; do not
  assume chip-off destroys the unit or that pad access is risk-free.
- Treat all storage images as sensitive personal data.

Gate: the work is on a spare, not the car; every destructive or state-changing step has a
written rationale and the owner's explicit approval.

Stop conditions for every stage:

- An update, reset, calibration, coding, or DTC-clear prompt appears.
- A step would require disconnecting high-voltage, airbag, or safety systems.
- A capture contains third-party personal data and cannot be redacted.
- A step requires a pinout, probe point, or procedure not covered by the authorised source.
- The car would be left in a non-standard or undrivable state.

## 7. Evidence manifest

The manifest should live outside Git with the raw captures. Only a redacted summary and the
manifest hash should enter the repository.

Suggested JSON shape:

```json
{
  "manifest_version": "1.0",
  "case_id": "IONIQ5-AU-2021-GEN5W",
  "created_utc": "2026-10-18T00:00:00Z",
  "operator": "owner-authorised",
  "vehicle": {
    "market": "AU",
    "model_year": 2021,
    "variant_contract": "NEAE.S5BLN.AAU",
    "software_contract": "NE_E.AUS.S5W_L.001.001.260319"
  },
  "sources": [
    {
      "source_id": "SRC-001",
      "url": "https://update.hyundai.com/AU/EN/updateNoticePopup/aiD0Sq",
      "accessed_utc": "2026-10-18",
      "strength": "A1",
      "supports": ["identity", "software-version", "model-string"],
      "limits": "Official table; does not provide package hash or hardware configuration."
    }
  ],
  "artifacts": [
    {
      "artifact_id": "EV-001",
      "route": "owner-ui-version",
      "claim_ids": ["C-01", "C-03"],
      "source_type": "owner-observation",
      "source_strength": "A0",
      "captured_utc": "2026-10-18T00:00:00Z",
      "device": "vehicle-head-unit",
      "location": "vehicle",
      "file": "private/2026-10-18/version-screen.png",
      "sha256": "REPLACE_WITH_SHA256",
      "bytes": 0,
      "mime": "image/png",
      "redaction": "applied",
      "sensitivity": "high",
      "notes": "Device ID cropped; no VIN or registration visible.",
      "unknowns": ["exact head-unit part number"]
    }
  ],
  "redaction_log": [
    {
      "artifact_id": "EV-001",
      "fields": ["Device ID"],
      "method": "crop and re-render",
      "performed_by": "owner-authorised",
      "date_utc": "2026-10-18"
    }
  ]
}
```

Minimum fields for every artifact:

- stable artifact ID and route;
- claim IDs it supports or challenges;
- source type and source strength;
- capture date/time in UTC and operator;
- device/cable/analyzer identity;
- file path in the private store, byte size, MIME type, SHA-256;
- redaction status and sensitivity;
- what it establishes and what it cannot establish;
- chain-of-custody note.

## 8. Redaction and confidentiality rules

Never commit, upload, or paste into a public issue:

- VIN, registration number, build plate, odometer if combined with VIN, or dealer job
  numbers.
- Head-unit Device ID, serial number, ESN, IMEI, ICCID, MAC address, or Bluetooth address.
- Vehicle Bluetooth name, passkey, paired phone names, contacts, call history, messages,
  favourites, or notifications.
- Phone/account identifiers, Apple/Google account data, Bluelink credentials, tokens, or
  session cookies.
- Home/work locations, navigation history, previous destinations, GPS traces, or trip logs.
- Wi-Fi SSIDs, BSSIDs, passwords, captive-portal tokens, IP addresses, or packet captures.
- Raw USB captures containing device serial strings.
- Raw iOS sysdiagnose, Android bugreport, HCI snoop logs, packet captures, or storage
  images.
- Photographs showing faces, number plates, houses, or screen reflections with personal
  data.

Storage rules:

- Keep raw captures in a directory outside the repository, mode 0700, on an encrypted
  volume.
- Do not sync that directory to iCloud, Dropbox, OneDrive, or any other cloud service.
- Use a dedicated local account for analysis where practical.
- Hash raw files before analysis and keep the hash in the manifest.
- If correlation is needed, use a local keyed hash (HMAC) rather than storing the raw
  identifier.

Redaction method:

- Crop and re-render images; do not rely on a translucent blur over text.
- Strip EXIF/GPS and re-encode PNG/JPEG.
- For PDFs, remove metadata and ensure redacted text is not recoverable.
- For logs, replace identifiers with stable pseudonyms in the derived note; keep the
  mapping only in the private store.
- Record every redaction in the manifest.

Git rules to propose to the parent (do not edit `.gitignore` in this task):

```gitignore
private/
captures/
*.pcap
*.pcapng
*.har
*.sysdiagnose
*.bugreport
*.hci
*.bin
*.img
*.dd
```

The repository should contain only this artifact, the source register, redacted claim
summaries, and hashes. Raw evidence stays private.

## 9. Claims ledger

| ID | Label | Claim | Evidence/limit |
|---|---|---|---|
| C-01 | OBS | Hyundai AU lists 2021-23 IONIQ 5 as Standard Gen5W with `NE_E.AUS.S5W_L.001.001.260319` and `NEAE.S5BLN.AAU`. | AU update popup; exact row. |
| C-02 | OBS | The 2021 AU specification sheet lists a 12.3-inch capacitive touch display, Apple CarPlay/Android Auto compatibility, Bluetooth audio streaming, USB multimedia input, satellite navigation, RDS-TMC live traffic, and a voice-memo function. | S-13 canonical Sept 2021 spec PDF, fetched 2026-10-19; hash/size limits in the source register. |
| C-03 | OBS | The AU Gen5W version screen shows software version, firmware version, navigation application version, map version, and Device ID. | AU manual `general.html`. |
| C-04 | OBS | The AU Gen5W System info menu shows memory for voice memos, web manual, What's new, and Modem information (if equipped). | AU manual `general.html`. |
| C-05 | OBS | The AU Gen5W Bluetooth system info lets the owner change the vehicle Bluetooth name and a 4-digit passkey; the manual documents a default passkey and recommends changing it (the value is intentionally not reproduced here). | AU manual `phoneconnection.html`. |
| C-06 | OBS | The AU Gen5W phone projection page describes Android Auto and Apple CarPlay with a USB cable; no wireless projection is documented. | AU manual `phoneprojection.html`. |
| C-07 | OBS | The AU Gen5W product specification lists Bluetooth 4.2 with HFP/A2DP/AVRCP/PBAP/MAP, WCDMA B1/B8, and LTE B1/B3/B7/B28/B40; Wi-Fi is omitted from the listed specification. | AU manual `specification.html`. |
| C-08 | OBS | The AU Gen5W manual supports FAT16/32, exFAT, and NTFS USB media, warns against hubs/extensions, and describes metal-cover USB memory. | AU manual `generalinformation.html`. |
| C-09 | OBS | The June 2026 AU update notice says installation cannot be reverted, requires the official NaU tool, and requires exFAT USB media when no SD card is present. | AU notice `yNDC3y`. |
| C-10 | OBS | Hyundai AU's warranty passport gives the Audio/AVN head unit 60 months/unlimited km for private use and excludes defects caused by non-Hyundai modifications or testing/repair outside an authorised dealer. | AU warranty PDF, pp. 9-11. |
| C-11 | OBS | A US Hyundai TSB calls the 2024 IONIQ 5 unit `AVN5W` and uses a `96560*` part-number prefix. | HMA TSB 24-01-002H. |
| C-12 | OBS | TechInsights' IONIQ 5 teardown summary reports an Intel 1.8 GHz dual-core Atom, 4 GB LPDDR4, 128 GB internal storage, and an LTE board with Qualcomm baseband, 512 MB SLC NAND, and 256 MB LPDDR2. | TechInsights public summary. |
| C-13 | INF | The fitted unit is in the Gen5W family, consistent with the accepted T1 contract and the Hyundai AU update table. | Family inference from the AU update table and T1; not an AU hardware proof. The `AVN5W` name comes from 2024 US service material (C-11) and is a later-model analogy only; it contributes nothing to the 2021 identity claim. |
| C-14 | INF | The AU specification lists LTE bands and omits Wi-Fi, and the AU manual exposes no Wi-Fi menu. This documents cellular capability and a missing documented Wi-Fi feature, not LTE exclusivity or absent Wi-Fi hardware. Wired USB projection is documented; wireless projection remains unknown. | AU manual/spec; absence from the documented feature list is not proof of hardware absence. |
| C-15 | UNK | Exact AU head-unit part number and serial label. | No AU parts record or label observed. |
| C-16 | UNK | Exact AU SoC, RAM, storage size, and storage medium. | TechInsights is family-level; no AU teardown. |
| C-17 | UNK | Whether a Wi-Fi radio/antenna is fitted but unexposed. | No AU Wi-Fi documentation; no RF observation performed. |
| C-18 | UNK | USB port speed and role. | Not stated in the cited AU documents. |
| C-19 | UNK | Wireless Android Auto/CarPlay support. | AU manual documents USB cable only. |
| C-20 | UNK | AVN DTC list and log-export format. | Dealer/GSW access required. |
| C-21 | UNK | UART/JTAG/eMMC/test-point map. | No exact AU public map found. |
| C-22 | UNK | AU RCM supplier declaration/approval record. | No public per-product record found. |
| C-23 | UNK | Whether FCC VN470/DA471 corresponds to the AU unit. | Filings do not state AU fitment. |
| C-24 | UNK | Official package signature/encryption and exact AU variant mapping. | Not established by the public notice. |

## 10. Bounded negative searches

These are search results, not proof of absence. They define what was checked on 2026-10-18.

| Query/target | Result | Interpretation |
|---|---|---|
| `"96560-GI580" Australia` | No AU parts-catalog match; US listings dominated. | The US number is not an AU part number. |
| `"NE_E.AUS.S5W_L.001.001.260319"` | Official AU update table/notice only; no public package hash or file list. | Public identity exists; package metadata requires NaU download. |
| AU Gen5W manual TOC for Wi-Fi/Data Network | No Wi-Fi/Data Network page in the AUS branch; EU/US branches have Wi-Fi/Data Network material. | No documented AU Wi-Fi user feature; hardware presence unknown. |
| `Ioniq 5 RCM supplier declaration` / `Ioniq 5 ACMA approval` | No public per-product declaration found. | RCM label on the unit is the practical evidence route. |
| `Ioniq 5 2021 Australia head unit teardown` | No exact AU teardown found; TechInsights global teardown found. | Family-level teardown only. |
| `Ioniq 5 Gen5W UART JTAG test points` | No exact AU map found; generic eMMC/UART methods only. | Bench work must derive its own map from the exact board. |
| `Ioniq 5 wireless CarPlay 2021 Australia` | No official AU wireless support found; AU manual says USB cable. | Wired support is documented; wireless is UNK. |
| `Hyundai Ioniq 5 NE service manual AVN` | AASRA/GSW paid/restricted portal; unofficial resellers only. | No free public AU service manual. |

## 11. Source register

Council re-verification of S-01 and S-13 was performed on 2026-10-19. All other sources
were accessed 2026-10-18 unless noted.

| ID | Source | Strength | Used for | Limits |
|---|---|---|---|---|
| S-01 | Hyundai AU update popup: https://update.hyundai.com/AU/EN/updateNoticePopup/aiD0Sq | A1 | Exact AU version/model row; 2024-25 ccNC split. | Table only; no hardware or package hash; URL verified on 2026-10-19. |
| S-02 | Hyundai AU notice list: https://update.hyundai.com/AU/EN/updateNoticeList | A1 | June 2026 notice date; release cadence. | Does not map every version string to a notice. |
| S-03 | Hyundai AU June 2026 notice: https://update.hyundai.com/AU/EN/updateNoticeView/yNDC3y | A1 | No-revert warning; NaU/USB/exFAT requirements. | Generic notice; not VIN-specific. |
| S-04 | Hyundai AU update guide: https://update.hyundai.com/AU/EN/updateGuide/04 | A1 | Standard Gen5W version-info path. | Illustrative; screen may differ. |
| S-05 | Hyundai AU Gen5W manual index: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/ | A1 | AU manual branch identity. | JavaScript-rendered; page list from `tocData.json`. |
| S-06 | AU manual General: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/general.html | A1 | Version info/Device ID; System info; Modem information. | "If equipped" caveats. |
| S-07 | AU manual Wireless update: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/wirelessupdate.html | A1 | Network-based wireless update; update flow. | Does not identify Wi-Fi vs LTE. |
| S-08 | AU manual Phone connection: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/phoneconnection.html | A1 | Bluetooth name/passkey; privacy mode; projection settings. | "If equipped" caveats. |
| S-09 | AU manual Phone projection: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/phoneprojection.html | A1 | USB-cable CarPlay/Android Auto; no wireless documented. | Does not prove wireless hardware absent. |
| S-10 | AU manual Bluetooth: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/bluetoothwirelesstechnology.html | A1 | Bluetooth pairing and hands-free behaviour. | Generic manual; no version detail. |
| S-11 | AU manual General Information: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/generalinformation.html | A1 | USB formats and limitations. | Only the documented media path. |
| S-12 | AU manual Specification: https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/AUS/English/specification.html | A1 | Bluetooth 4.2/profiles; WCDMA/LTE bands; Wi-Fi omitted from the listed specification. | Product-family specification; omission is not proof of absent hardware or exclusive LTE; exact fitted module not stated. |
| S-13 | Hyundai AU Sept 2021 spec PDF (canonical T1/T5 path): https://www.hyundai.com/content/dam/hyundai/au/en/models/ioniq5/images/IONIQ5_SpecTable_Sept_2021.pdf | A1 | 12.3-inch display; CarPlay/AA; Bluetooth; USB; satellite nav; RDS-TMC; voice memo. | Verified 2026-10-19: 9 pages, 826,664 bytes, SHA-256 `be96e3a636cf95877a4d50f2a84ce3c17f34fc33ff71d7d3508b794d08857f04`; byte-identical to the older edms URL. PDF may be updated in place; hash identifies this snapshot only and does not prove every listed feature was fitted. |
| S-14 | Hyundai AU IONIQ 5 launch news: https://www.hyundai.com/au/en/news/mobility/hyundai-IONIQ-5-redefines-electric-mobility-lifestyle | A2 | AU Q3 2021 launch; 12-inch displays; Bluelink context. | Marketing copy; not a build sheet. |
| S-15 | Hyundai AU OTA page: https://www.hyundai.com/au/en/owning/ota | A1 | OTA requires Bluelink activation; update behaviour. | Current page; may not describe 2021 unit exactly. |
| S-16 | Hyundai AU warranty passport: https://www.hyundai.com/content/dam/hyundai/au/en/models/ioniq5/images/ecommerce/IONIQ5_Service_Warranty_Passport.pdf | A1 | AVN 60-month warranty; modification/testing exclusions. | Dated 09/2021; terms can change. |
| S-17 | AASRA Hyundai portal: https://aasra.com.au/?page_id=1037 | B2 | GSW contents; paid access tiers; AU service-information route. | Authoritative third-party service-information body, not Hyundai or a government regulator; prices/eligibility can change, and this is not the manual itself. |
| S-18 | Hyundai GSW login/EULA: https://service.hyundai-motor.com/euro5/loginAasra.tiles?siteCd=H | A1 | Access restriction and confidentiality terms. | Login required; no content reviewed. |
| S-19 | HMA TSB 24-01-002H: https://static.nhtsa.gov/odi/tsbs/2024/MC-10249697-0001.pdf | A1 | AVN5W name; 96560* part prefix; dealer-only reset context. | US service bulletin; not AU. |
| S-20 | HMA TSB 23-01-017H-1: https://static.nhtsa.gov/odi/tsbs/2023/MC-10238395-0001.pdf | A1 | Early IONIQ 5 AVN map-update context. | US service bulletin; not AU. |
| S-21 | FCC VN470 (third-party mirror): https://fccid.io/TQ8-VN470ZZZAN | D2 | Discovery of a 2022 Hyundai Mobis 2.4/5 GHz infotainment radio filing. | FCC-origin content via a mirror; provenance/document identity not verified against FCC EAS; US approval; exact AU fitment UNK. |
| S-22 | FCC VN470 user manual (third-party mirror): https://fccid.io/TQ8-VN470ZZZAN/User-Manual/User-Manual-6282809.pdf | D2 | Multiple-model AVN manual; feature context. | FCC-origin content via a mirror; not AU-specific; includes DMB/HD Radio/SiriusXM features; provenance not verified. |
| S-23 | FCC VN470 internal photos (third-party mirror): https://fccid.io/TQ8-VN470ZZZAN/Internal-Photos/Internal-Photo-6282810.pdf | D2 | Board-level imagery route. | Mirror copy not downloaded/inspected here (mirror returned 403); no board claims made; provenance not verified against FCC EAS. |
| S-24 | FCC DA471 (third-party mirror): https://fccid.io/TQ8-DA471ZZZAN | D2 | Discovery of another 2022 Hyundai Mobis infotainment radio filing. | FCC-origin content via a mirror; provenance/document identity not verified against FCC EAS; US approval; exact fitment UNK. |
| S-25 | FCC DA471 internal photos (third-party mirror): https://fccid.io/TQ8-DA471ZZZAN/Internal-Photos/Internal-Photo-6295876 | D2 | Board-level imagery route; SHA-256 shown by mirror. | Mirror copy not inspected here; SHA-256 identifies the mirror display, not a verified FCC EAS copy; provenance not verified. |
| S-26 | ACMA supplier obligations: https://www.acma.gov.au/know-what-you-must-do | B1 | RCM/labelling and supplier-record obligations. | General regulatory guidance, not product-specific. |
| S-27 | EESS RCM: https://www.eess.gov.au/rcm/ | B1 | RCM mark ownership/meaning. | General guidance. |
| S-28 | TechInsights teardown: https://electronics360.globalspec.com/article/19251/techinsights-teardown-hyundai-ioniq-5-head-unit | C2 | IONIQ 5 head-unit architecture and component summary. | Public summary; exact AU variant not stated. |
| S-29 | Springer Gen5W_L paper: https://link.springer.com/article/10.1007/s11416-024-00522-4 | C1 | Family-level Gen5W_L IVI research; cryptographic/update boundary. | Hyundai IONIQ Electric, not IONIQ 5; no AU fitment. |
| S-30 | MDPI Android AVN forensics: https://www.mdpi.com/2076-3417/13/10/6176 | C1 | eMMC chip-off method; Bluetooth/navigation/log artefacts. | Android AVN case study, not IONIQ 5. |
| S-31 | cantcs Gen5W research: https://github.com/cantcs/HKG_Gen5W_ReverseEngineer | D1 | Gen5W Android variant; eMMC/encrypted firmware context. | Different variant; not AU Linux branch. |
| S-32 | laralbir Gen5W research: https://github.com/laralbir/hyundai-kia-gen5w-navi-firmware | D1 | EU Gen5W firmware research; UART/GDS/engineering-mode topics. | Family-level; no AU fitment. |
| S-33 | US parts diagram: https://www.hyundaipartscounter.com/v-2022-hyundai-ioniq-5--se-standard-range--electric/entertainment-and-telematics--mobile-multi-media | D1 | `96560-GI580` family context. | US reseller; not AU. |
| S-34 | EU used unit: https://partsouq.com/shop/product/96560GI870-hyundai-kia-head-unit-assy-avn/17664232 | D1 | `96560-GI870` family context. | Used-parts listing; not AU. |
| S-35 | US TSB parts reference: https://static.nhtsa.gov/odi/tsbs/2024/MC-10249697-0001.pdf | A1 | `96560-GI730` causal part. | US TSB; not AU. |

## 12. Unresolved gaps

1. Exact AU head-unit part number, suffix, serial, and label layout.
2. Exact AU SoC, RAM, storage size, and storage medium.
3. Whether the AU unit has a Wi-Fi radio/antenna, even though the AU manual/spec do not
   expose Wi-Fi.
4. USB port speed/role and whether CarPlay/Android Auto use the same port as mass storage.
5. Whether wireless Android Auto/CarPlay is supported.
6. AVN DTC list, freeze-frame data, and log-export format.
7. UART/JTAG/eMMC/test-point map for the exact AU board.
8. AU RCM supplier declaration and approval record.
9. Whether FCC VN470/DA471 corresponds to the AU unit.
10. Official package signature/encryption and exact AU variant mapping.
11. Whether a spare EU/US unit can be adapted to the AU car without dealer coding; do not
    assume it can.
12. Whether the AU unit is VIN/component-locked.

## 13. Artifact hash and change log

Artifact locations (two relative navigation names for the same file):

- Live repository path: `evidence/passive-runtime-and-hardware.md`.
- Frozen review-package path: `artifacts/passive-runtime-and-hardware.md`, relative to the
  package root (the directory containing `artifacts/`, `task.json`, and
  `research-ledger.json`).

Path convention: cite the `evidence/...` form from this working tree and the
`artifacts/...` form from inside a frozen package. A frozen package root holds
`artifacts/`, `task.json`, `research-ledger.json`, and the validation receipt; it has no
`evidence/` directory, so a package-local citation must use `artifacts/...`. The two
relative names identify the same content when the frozen copy is byte-identical to the
live file. The absolute machine path
`/Users/researcher/Documents/ChatGPT/reverse engineering/evidence/passive-runtime-and-hardware.md`
is provenance for this working copy only; it is not a navigation target and is not part
of any claim. Historical receipts that recorded the absolute path are left unchanged.

The SHA-256 below is for the artifact body above this final block. It is recorded after the
body is frozen. Recompute if any line above changes.

Artifact SHA-256: `b9c82c5387e9ab0a27b3fae211f6eb9b7e695f05031670523e393889eab77ab4`

Change log:

- 2026-10-18: Initial T4 research artifact. Corrected the manual branch from the Canada
  Gen5W guide to the Australian (`AUS`) Gen5W branch before making regional claims.
- 2026-10-18: Added the AU-specific no-Wi-Fi/no-wireless-projection observations as
  documented absences, with hardware presence left UNK.
- 2026-10-18: Added FCC, ACMA/RCM, TechInsights, MDPI, Springer, GitHub, parts, service, and
  warranty sources with access dates and source-strength labels.
- 2026-10-19: Correction round 1: split physical invasiveness from restoration outlook;
  documented USB software-state effects; replaced the generic logic-analyzer example with
  speed-qualified USB protocol analyzers; added the B2 third-party authority category for
  AASRA; narrowed C-14/S-12 to the documented LTE/Wi-Fi omission rather than exclusivity.
- 2026-10-19: Council correction: qualified screen-viewing and bench-power software-state
  effects; defined A0 owner observation; reclassified FCC-origin mirror exhibits as D2 with
  provenance-verification limits.
- 2026-10-19: DeepSeek correction: replaced the AU software-table URL with the verified
  `aiD0Sq` popup; reconciled S-13 to the canonical T1/T5 spec path with size/hash limits;
  removed the draft status; added the consolidated route matrix.
- 2026-10-19: Council generation-4 correction: clarified in the consolidated route
  matrix that even non-actuating diagnostic requests transmit and can change wake,
  session, log, and counter state.
- 2026-10-19: Council generation-5 correction (DSG-G5-01/05/08/09): removed `AVN5W` from
  the 2021 identity rationale and from C-13, leaving it only as a labelled 2024 US
  later-model analogy; added explicit minimum-tools, safety/warranty-risk, and
  evidentiary-value dimensions to the consolidated route matrix; added the
  package-relative path convention without altering any historical receipt.
- 2026-10-19: Council generation-6 correction (ASTRA-G6-02/S01): split the path guidance
  into explicit live-repository (`evidence/...`) and frozen-package (`artifacts/...`)
  forms so every package-local citation resolves; replaced the categorical
  storage/debug risk and reversibility wording with the method-dependent language used
  in section 5.6.
