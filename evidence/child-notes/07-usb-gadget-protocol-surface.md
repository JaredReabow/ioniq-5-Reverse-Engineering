# 07 — USB Gadget Protocol Surface (iAP2 / CarPlay / Android Auto)

Status: protocol-structure documentation + test-harness design only. No exploit code,
no payloads, no device contact. Facts are tagged **[VERIFIED]** (public source read),
**[INFERRED]** (deduced from kernel config / public architecture), or **[UNK]**.

Subject: Hyundai Ioniq 5 (Gen5W_L) AVN head unit, Linux x86-64 **4.1.27**, LG-built
(`CONFIG_LGE_*`). Kernel config recovered at `work/eu-260128/kernel.config`.

---

## TL;DR

- The head unit is a **dual-role USB device** (`CONFIG_USB_DWC3=m`, `DUAL_ROLE=y`) plus
  a normal USB host (XHCI/EHCI/OHCI). Role is switched by an **iAP2 extcon** driver
  (`CONFIG_EXTCON_IAP2=m`, `EXTCON_IAP2_APL=y` = Apple).
- **CarPlay / iAP2**: the head unit is the USB *gadget* (accessory), the iPhone is the
  USB *host*. The host's link-layer and control-session packets are **length-prefixed and
  parsed by the accessory**. This is the main host->accessory parser surface.
- **Android Auto (AOA)**: the head unit is the USB *host*, the phone is the USB *device*.
  The phone controls its own descriptors, the 2-byte AOA protocol version, the AOA bulk
  stream (projection protobufs), and (AOA 2.0) HID reports.
- CarPlay's audio/video/control media do **not** ride on iAP2 bulk packets; iAP2 only
  bootstraps (auth/identification), then the media runs over a **USB CDC-NCM virtual
  Ethernet** (wired) or Wi-Fi (wireless) as an **AirPlay** session.
- Known real-world bugs are **CarPlay "CTRL"/TLV" stack overflows in accessory-side
  parsers** (Sony XAV-AX5500, Alpine iLX-507) — the exact class this head unit exposes.

---

## 0. Subject configuration (recovered kernel config)

| Option | Value | Meaning |
|---|---|---|
| `CONFIG_USB_DWC3` | m | DWC3 controller driver |
| `CONFIG_USB_DWC3_DUAL_ROLE` | y | same port can be host or device |
| `CONFIG_USB_XHCI_HCD` / `EHCI` / `OHCI` | m | USB *host* side (phone, media) |
| `CONFIG_USB_LIBCOMPOSITE` | m | composite gadget framework |
| `CONFIG_USB_F_IAP2` / `USB_U_IAP2` / `USB_IAP2` | m | iAP2 gadget function (accessory side) |
| `CONFIG_USB_F_NCM` | m | CDC-NCM gadget (CarPlay media link) |
| `CONFIG_USB_F_SERIAL` / `USB_U_SERIAL` / `USB_G_SERIAL` | m | generic serial gadget |
| `CONFIG_USB_F_ACM` | m | CDC-ACM gadget |
| `CONFIG_USB_F_OBEX` | m | OBEX gadget |
| `CONFIG_USB_F_MASS_STORAGE` / `USB_MASS_STORAGE` | m | mass-storage gadget |
| `CONFIG_USB_GADGETFS` | m | GadgetFS (userland descriptors) |
| `CONFIG_USB_CONFIGFS` | **not set** | no modern configfs composite |
| `CONFIG_USB_FUNCTIONFS` | **not set** | no FunctionFS |
| `CONFIG_EXTCON_IAP2` / `EXTCON_IAP2_APL` | m / y | Apple role-switch detection |
| `CONFIG_LGE_CARPLAY` | y | CarPlay flag; **parsing is userland** |
| `CONFIG_LGE_USB` / `LGE_USB_ADAPTER` / `LGE_USB_EMULATOR` | y/m/m | LG USB composite glue |

Implication **[INFERRED]**: `f_iap2.ko`/`u_iap2.ko`, the LG USB composite glue, the iAP2
userland daemon, and the CarPlay daemon all live in the **encrypted rootfs** (see
`evidence/attack-surface-prioritisation.md`). No `carplay` symbols exist in `vmlinux`,
confirming `CONFIG_LGE_CARPLAY=y` is a **userland** feature.

### Threat model

The "attacker" is a **malicious or malformed phone** physically attached to the vehicle
USB port (AV:P). Two opposite roles must be analysed separately:

```
                    head unit = USB DEVICE (gadget)        phone = USB HOST
CarPlay / iAP2      f_iap2 / u_iap2 / NCM / mass-storage  (iPhone / rogue host)
---- role switch ----
                    head unit = USB HOST (XHCI/EHCI/OHCI)  phone = USB DEVICE
Android Auto (AOA)  enumerates the phone                  (Android / rogue device)
```

- Gadget role: attacker controls **host→device control requests and bulk data** (iAP2
  frames, SCSI command blocks).
- Host role: attacker controls **its own USB descriptors and endpoint data** (AOA bulk,
  HID reports, audio).

---

## 1. iAP2 (iPod Accessory Protocol 2)

### 1.1 Transport and roles

iAP2 runs over four transports (public iAP2 reverse engineering, `wiomoc/iap2`):
Bluetooth RFCOMM, serial, **USB Device Mode** (iPhone=device, accessory=host, HID
reports), and **USB Host Mode** (iPhone=host, accessory=device, bulk IN/OUT). CarPlay
wired uses **USB Host Mode**: the head unit exposes a bulk IN + bulk OUT interface.

Bluetooth UUIDs (verified): accessory service `00000000-deca-fade-deca-deafdecacaff`,
iPhone client `00000000-deca-fade-deca-deafdecacafe`.

### 1.2 Link-layer framing **[VERIFIED — `wiomoc/iap2/link_layer.py`]**

```
detect/iAP2 marker (6 bytes):  FF 55 02 00 EE 10

link packet header (9 bytes):
 +0  start      u16 BE  = 0xFF5A   (bytes FF 5A)
 +2  length     u16 BE  = total = 9 (no payload) or 9 + len(payload) + 1
 +4  control    u8       bit flags: SYN=0x80 ACK=0x40 EAK=0x20 RST=0x10
 +5  seq        u8       PSN (packet sequence number)
 +6  ack        u8       acknowledged PSN
 +7  session_id u8       10 = control session, 11 = EA session
 +8  checksum   u8       header checksum (sum of bytes 0..7 + this == 0 mod 256)

payload (when present):  payload bytes + 1 trailing checksum byte
                         (sum(payload) + checksum == 0 mod 256)
```

**Length encoding**: `length` is a big-endian 16-bit total packet length. The receiver
computes `length - 9` payload bytes, then verifies the 1-byte payload checksum. A
malicious host fully controls `length`, `control`, `seq`, `ack`, `session_id`, and the
payload — the accessory-side parser must bounds-check `length` before copying.

### 1.3 Link negotiation (SYN / LinkSynchronizationPayload) **[VERIFIED]**

```
LSP payload (big-endian):
 +0  version              u8   = 0x01
 +1  max_outgoing         u8   window size (unacked packets)
 +2  max_len              u16  max packet length
 +4  retransmission_timeout u16 (ms)
 +6  ack_timeout          u16 (ms)
 +8  max_retransmissions  u8
 +9  max_ack              u8
+10  sessions[]           3 bytes each: { id u8, type u8, version u8 }
                            (control id=10 type=0 ver=1; EA id=11 type=2 ver=1)
```

State machine: `DETECT (send marker) -> NEGOTIATE (SYN/SYN-ACK) -> NORMAL (data) -> DEAD`.
The link layer is a **TCP-like sliding window over 8-bit PSNs** with ACK/EAK/RST. All
window/timeout parameters are **attacker-influenced** (the host's SYN LSP is accepted and
adopted by the accessory).

### 1.4 Control Session Messages (CSM) **[VERIFIED]**

```
CSM frame (control session, session_id=10):
 +0  start    u16 BE = 0x4040
 +2  length   u16 BE = total message length (header + params)
 +4  msg_id   u16 BE
 +6  params[] TLV: { length u16 BE (incl. 4-byte TLV header), param_id u16 BE, value }

EA session data (session_id=11):  stream_id u16 BE + payload
```

Message IDs observed in the public reimplementation:

| msg_id | Direction (host=iPhone) | Name |
|---|---|---|
| 0x1D00 | host→acc | StartIdentification |
| 0x1D01 | both | IdentificationInformation (many strings + lists) |
| 0x1D02/03 | host→acc | IdentificationAccepted / Rejected |
| 0xAA00 | host→acc | RequestAuthenticationCertificate |
| 0xAA01 | acc→host | AuthenticationCertificate |
| 0xAA02 | host→acc | RequestAuthenticationChallengeResponse (**challenge bytes**) |
| 0xAA03 | acc→host | AuthenticationResponse |
| 0xAA04/05 | host→acc | AuthenticationFailed / Succeeded |
| 0xEA00 | host→acc | StartExternalAccessoryProtocolSession { protocol_id u8, session_id u16 } |
| 0xEA01 | host→acc | StopExternalAccessoryProtocolSession { session_id u16 } |
| 0xEA03 | host→acc | StatusExternalAccessoryProtocolSession { session_id u16, status } |
| 0x4E0D/0E | host→acc | WirelessCarPlayUpdate / DeviceTransportIdentifierNotification |
| 0x5700..03 | host→acc | WiFi information request/config (ssid, passphrase, security, channel) |
| 0xA100..02 | host→acc | Vehicle-status start/update/stop |

### 1.5 Where the host sends variable-length / length-prefixed data

The accessory (head unit) consumes attacker-controlled host bytes at **three nesting
levels**, each with its own length field:

1. **Link layer** `length` (u16) → drives `read(length-9)`.
2. **CSM frame** `length` (u16) and **CSM param** `length` (u16) → TLV walking.
3. **Application fields** inside TLVs:
   - `IdentificationInformation`: variable-length UTF-8 strings (name, model, manufacturer,
     serial, firmware/hardware version, languages), `messages_sent_by_accessory` /
     `messages_received_from_accessory` byte blobs, and **lists** of
     `ExternalAccessoryProtocol` / `SerialTransportComponent` /
     `USBDeviceTransportComponent` / `USBHostTransportComponent` /
     `BluetoothTransportComponent` / `VehicleInformationComponent` /
     `VehicleStatusComponent` / `WirelessCarPlayTransportComponent` records.
   - `RequestAuthenticationChallengeResponse`: arbitrary-length challenge bytes.
   - `StartExternalAccessoryProtocolSession`: `protocol_id` + `session_id`.
   - WiFi info: `ssid` / `passphrase` strings.

### 1.6 Accessory-side parsers (head unit)

- **Kernel**: `u_iap2.ko` (link framing, checksum, PSN window, retransmit timers,
  session demux) and `f_iap2.ko` (USB function + endpoints). These parse the link header
  and `length` fields directly. **[INFERRED — module code in encrypted rootfs]**
- **Userland**: LG iAP2 daemon parses CSM TLVs (identification/auth/EAP/WiFi/vehicle
  status); LG CarPlay daemon (`CONFIG_LGE_CARPLAY=y`) handles the CarPlay session.
  **[INFERRED]**
- **MFi Authentication Coprocessor** (hardware, I2C addr 0x10): the accessory reads the
  Apple-signed certificate and signs the phone's challenge (RSA-1024/SHA-1 in the 2.0
  coprocessor). Registers (verified): 0x30 cert length, 0x31 cert data, 0x20 challenge
  length, 0x21 challenge, 0x10 auth control/status, 0x11 response length, 0x12 response.

---

## 2. Android Auto

### 2.1 Roles

Android Auto over USB uses the **Android Open Accessory (AOA)** protocol. In AOA the
**accessory = USB host** and the **Android device = USB device (in "accessory mode")**.
Therefore the head unit is the USB **host** (XHCI/EHCI/OHCI) and the phone is the USB
**device**.

### 2.2 AOA handshake **[VERIFIED — AOSP `drivers/usb/gadget/function/f_accessory.c`, Android AOA 2.0 docs]**

All requests are vendor-type control transfers on endpoint 0:

```
ACCESSORY (head unit, HOST)                         ANDROID DEVICE (phone)
  |-- GET_PROTOCOL  (bmReqType 0xC0, bReq 51, wLen 2) -->|  returns 2-byte version
  |<----------------------------------------------- vers |
  |-- SEND_STRING   (bReq 52, wIndex = string id 0..5) -->|  id: 0 manufacturer
  |     UTF-8 string data                                  |      1 model
  |   (6 strings: manufacturer/model/description/          |      2 description
  |    version/URI/serial)                                 |      3 version
  |                                                        |      4 URI
  |                                                        |      5 serial
  |-- START         (bReq 53) --------------------------->|
  |                                                        |  phone re-enumerates in
  |                                                        |  "accessory mode"
  |<=== re-enumeration: VID 0x18D1, PID 0x2D00..0x2D05 ====|
  |    then bulk IN/OUT pipes carry the projection stream  |
```

AOA 2.0 additions (also host-initiated control requests): `REGISTER_HID` (54),
`UNREGISTER_HID` (55), `SET_HID_REPORT_DESC` (56), `SEND_HID_EVENT` (57),
`SET_AUDIO_MODE` (58).

Accessory-mode PIDs: `0x2D00` accessory, `0x2D01` accessory+adb, `0x2D02` accessory+audio,
`0x2D03` accessory+audio+adb, `0x2D04` accessory+audio, `0x2D05` accessory+audio+adb.

### 2.3 Attacker-controlled fields (phone = USB device)

The head unit's **host-side** parsers consume phone-controlled input:

| Field | Controlled by phone | Parser on head unit |
|---|---|---|
| Device/config/interface/endpoint/string descriptors | fully | Linux USB core (`usb`, xHCI/EHCI drivers) |
| AOA GET_PROTOCOL response (2 bytes) | fully | AA projection daemon |
| AOA bulk IN stream (Android Auto projection, protobuf) | fully | Android Auto receiver daemon (userland) |
| AOA 2.0 HID report descriptor + HID reports | reports fully (descriptor is host-supplied) | usbhid / input subsystem |
| Audio stream (AOA audio sink) | not attacker-controlled (host→device direction) | — |

The projection protocol on the AOA bulk pipe is Google's proprietary protobuf-based
Android Auto protocol; the receiver-side parser is a large userland attack surface.

### 2.4 Wireless Android Auto handshake **[INFERRED / standard architecture]**

1. Bluetooth pairing: HFP (telephony), PBAP (contacts), A2DP (media). The phone connects
   to the head unit's Bluetooth (or vice-versa).
2. The head unit's Android Auto service triggers a Wi-Fi handshake over an RFCOMM
   channel: the head unit provisions a **Wi-Fi hotspot or Wi-Fi Direct group** and hands
   the phone credentials.
3. The projection session (same protobuf protocol) runs over **TCP (TLS)** on the Wi-Fi
   link.

Attacker-controlled (malicious phone, radio range): Bluetooth SDP/RFCOMM/HFP AT data,
PBAP vCard (contact) data, and the Wi-Fi/TLS projection stream. **Note for this unit**:
the AU owner's manual documents **USB-cable only** — no official wireless projection.
`evidence/passive-runtime-and-hardware.md` records this as UNK; wireless is treated as
not-present until shown otherwise.

---

## 3. CarPlay over USB

### 3.1 Accessory-side interfaces (head unit = gadget)

```
1. Initial attach: iPhone presents as USB device; head unit acts as USB HOST.
2. Role switch:   head unit sends vendor control request bReq=0x51
                  (wValue 0 = normal accessory, 1 = CarPlay) to the iPhone.
3. Both sides swap: iPhone becomes HOST; head unit re-enumerates as USB DEVICE
   exposing the iAP2 interface (Apple VID 0x05AC, bulk IN/OUT).
4. iAP2 link negotiation + MFi auth + identification (section 1).
5. Head unit additionally exposes a USB CDC-NCM interface (CONFIG_USB_F_NCM) =
   virtual Ethernet. The iPhone runs AirPlay over this NCM link.
```

Role-switch request verified in `wiomoc/iap2/transport/usb_device.py`
(`request_type = RECIPIENT_DEVICE|VENDOR, bRequest 0x51, wValue 1, wIndex 0, wLength 0`).

### 3.2 Discovery / authentication exchange

```
iPhone (HOST)                               Head unit (ACCESSORY, gadget)
  |  [USB role switch 0x51(wValue=1)] ................>|
  |  [iAP2 marker FF 55 02 00 EE 10]  <-------------->|
  |  [SYN / LSP negotiation]            <------------->|
  |  RequestAuthenticationCertificate (0xAA00) ------->|
  |  <------------------------ AuthenticationCertificate (0xAA01) |
  |  RequestAuthenticationChallengeResponse (0xAA02, challenge) ->|
  |  <------------------ AuthenticationResponse (0xAA03, signed) |
  |  AuthenticationSucceeded (0xAA05) ---------------->|
  |  StartIdentification (0x1D00) -------------------->|
  |  <---------------- IdentificationInformation (0x1D01) |
  |  IdentificationAccepted (0x1D02) ---------------->|
  |  StartExternalAccessoryProtocolSession (0xEA00) -->|
  |  [NCM interface up; AirPlay session; CarPlay CTRL/audio/video] |
```

The CarPlay control channel ("CarPlay CTRL") is a TLV protocol carried over the AirPlay
transport; it carries touch/button/status and is where the public stack-overflow bugs live
(section 4). Wireless CarPlay replaces the NCM hop with Wi-Fi and secures the AirPlay
session with an **internal HomeKit pairing** (public iAP2 research).

---

## 4. Known public vulnerabilities / research

| ID / ref | Target | Class | Relevance |
|---|---|---|---|
| **CVE-2024-23933** (ZDI-24-877, ZDI-CAN-23238) | Sony XAV-AX5500 | **CarPlay TLV stack-based buffer overflow** (missing length check before copy) | Exact parser class in this unit; phys. attacker, CVSS 6.8 AV:P; credited Midnight Blue / PHP Hooligans (Pwn2Own Automotive 2024) |
| **CVE-2025-8474** (ZDI-25-763, ZDI-CAN-26318) | Alpine iLX-507 | **CarPlay stack-based buffer overflow** (missing length check), root context | Same class; credited Radu Motspan / PCAutomotive (Pwn2Own Automotive 2025) |
| CVE-2023-40292 | Harman infotainment | CarPlay CTRL packets disclose IP address | CarPlay CTRL channel info disclosure |
| CVE-2021-26689 (LVE-SMP-200031) | LG mobile (Android 8–10) | USB `laf` gadget use-after-free | LG gadget code quality precedent |
| CVE-2022-25258 | Linux kernel ≤5.16.10 | `usb/gadget/composite.c` interface OS descriptor validation | Gadget descriptor parsing |
| CVE-2022-25375 | Linux kernel ≤5.16.10 | `usb/gadget/function/rndis.c` size validation | Gadget host-input parsing |
| CVE-2021-39685 / CVE-2022-20009 | Android kernel | USB gadget OOB write (setup paths) | Gadget control-request parsing |
| CVE-2023-42533 | Samsung | USB gadget interface improper input validation → kernel RCE (physical) | Gadget host-input → RCE |
| CVE-2006-1368 | Linux ≤2.6.16 | RNDIS gadget buffer overflow | Historic gadget overflow |
| CVE-2017-0537 | Android 3.18 | USB gadget info disclosure | Gadget info leak |

Research/reference material (public, non-exploit):

- `wiomoc/iap2` (GitHub) + wiomoc.de blog *"Exploring Apple's MFI protocol iAP2"* — link
  framing, CSM IDs, auth coprocessor, CarPlay bootstrap, NCM/AirPlay/HomeKit layering.
- `ludwig-v/wireless-carplay-dongle-reverse-engineering` (GitHub) — Carlinkit U2W/U2AC/U2AW
  dongles (`iap2,ncm` composite, `ARMiPhoneIAP2` + `AppleCarPlay` daemons, gadgetfs);
  documents the same accessory architecture the head unit uses.
- Android AOA 2.0 (developer.android.com) + AOSP `f_accessory.c` (device side) — AOA
  control-request numbers, string IDs, accessory PIDs.
- USBFuzz (USENIX Sec 2020) and syzkaller gadget coverage — generic USB driver fuzzing.

---

## 5. Safe local test harness design (no vehicle, no real phone)

Goal: drive the head unit's *gadget* and *host* parsers with attacker-shaped bytes and
observe crashes — without touching the vehicle, a real iPhone, or an MFi coprocessor.

Blocking fact: `f_iap2.ko`/`u_iap2.ko` and the iAP2/CarPlay daemons are in the **encrypted
rootfs**. Until decrypted, the harness targets (a) the recovered `vmlinux` + gadget modules
in an emulator, or (b) reference reimplementations. Both tiers are below.

### 5.1 Tier 1 — pure userspace protocol replayer (no USB, fastest)

- Reimplement the **host (iPhone) side** of iAP2 in Python (framing, SYN/LSP, CSM TLV,
  auth stub). This is the "mock phone" and is the attacker.
- Reimplement/port the **accessory side** (the LGE iAP2 daemon + CarPlay daemon) once
  decrypted, or compile a reference accessory parser.
- Pipe mock-phone bytes → accessory parser in-process; run under ASan/UBSan/gdb; fuzz the
  length fields:
  - link `length` (0, 1..8, 9, 0xFFFF, lengths that wrap `length-9`),
  - CSM `length` and TLV `length` (overlapping, overrunning, zero, odd),
  - string fields (no NUL, huge, embedded NULs),
  - `session_id` (0..255, unknown ids), `seq`/`ack` (window edges, wrap at 256),
  - `protocol_id`/`session_id` in `StartExternalAccessoryProtocolSession`,
  - LSP parameters (max_len, timeouts, retransmission limits = 0/1/255).
- Auth bypass for fuzzing: the MFi coprocessor is fixed hardware; stub it by replaying a
  captured certificate + a dummy signed response, then continue the session.

### 5.2 Tier 2 — kernel gadget fuzzing via `dummy_hcd` + configfs/gadgetfs

- On a Linux dev host, load `dummy_hcd` (a virtual UDC) and mount `configfs` (or the
  head unit's `gadgetfs`). Compose the iAP2 function (upstream equivalent of `f_iap2`).
- A **mock iPhone host** (Python `pyusb`/`libusb` against the `dummy_hcd` bus, or a second
  machine acting as USB host) sends the mutated iAP2 frames from Tier 1.
- Watch for crashes with kASAN/KCSAN + `dmesg`, and coverage with kCOV; triage with the
  recovered `vmlinux` symbol map (`work/eu-260128/kallsyms.tsv`).
- This exercises the **kernel** framing parser (`u_iap2`) that Tier 1 cannot reach.

### 5.3 Android Auto (head unit = host) harness

- Emulate the **malicious phone as a USB device** using a second Linux/Raspberry Pi/Pico
  running a gadget (`f_accessory`, `f_hid`, `u_audio` via configfs). Mutate:
  - device/config/interface/endpoint/string descriptors,
  - the 2-byte AOA protocol-version response,
  - AOA bulk IN payloads (projection protobufs) — structural fuzz of the protobuf framing,
  - AOA 2.0 HID report descriptors and report payloads.
- Point these at a test host running the Android Auto **receiver** (or a mocked receiver),
  observing the Linux USB core (`usbmon`), usbhid, and the AA daemon.

### 5.4 CarPlay (head unit = accessory) harness

- Mock iPhone = Python/libusb that performs: role-switch request `0x51`, iAP2 negotiation,
  stubbed auth, identification, then `StartExternalAccessoryProtocolSession`.
- After NCM is up, drive the **CarPlay CTRL TLV** channel with mutated TLVs (the field the
  Sony/Alpine CVEs target).
- Run against Tier-1 port or Tier-2 gadget; ASan/kASAN + gdb; no exploit payloads — only
  length/type structure mutations and crash triage.

```
                  +---------------------- dev host ----------------------+
 mock iPhone      |  Tier1: Python iAP2 host  -->  accessory parser      |
 (attacker)       |        (mutated frames)        (ASan/gdb)            |
 libusb/pyusb --->|  Tier2: dummy_hcd + configfs/gadgetfs + f_iap2      |
                  |         kASAN/kCOV  (kernel framing parser)          |
 mock Android     |  gadget PC (f_accessory/f_hid/u_audio) --> usbmon    |
 phone (device)   |         + AA receiver (host-side parsers)            |
                  +------------------------------------------------------+
```

Safety properties: no vehicle, no real phone, no MFi coprocessor (stubbed), no exploit
payloads — mutation/fuzzing of structure fields only, with crash triage via ASan/kASAN.

---

## Sources

- `work/eu-260128/kernel.config` (recovered head-unit kernel configuration)
- `evidence/attack-surface-prioritisation.md`, `evidence/eu-kernel-symbol-recovery-and-trust-chain.md`
- `wiomoc/iap2` (GitHub): `link_layer.py`, `control_session_message/*.py`,
  `mfi_auth_coprocessor.py`, `transport/usb_device.py`, `carplay_bonjour.py`
- wiomoc.de — *"Exploring Apple's MFI protocol iAP2"* (2022)
- `ludwig-v/wireless-carplay-dongle-reverse-engineering` (GitHub): `start_iap2_ncm.sh`,
  `mount-gadgetfs.sh`, `Kernel/README.md`
- AOSP `drivers/usb/gadget/function/f_accessory.c` (android14-6.1); Android AOA 2.0 docs
- NVD / ZDI: CVE-2024-23933 (ZDI-24-877), CVE-2025-8474 (ZDI-25-763), CVE-2023-40292,
  CVE-2021-26689, CVE-2022-25258, CVE-2022-25375, CVE-2021-39685, CVE-2022-20009,
  CVE-2023-42533, CVE-2006-1368, CVE-2017-0537
