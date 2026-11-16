# Physical and wireless access vectors — Gen5W (mango) EU build `NE_E.EUR.S5W_L.001.001.260128`

Static inventory of the four access vectors the user asked about. All paths below are relative to the
read-only rootfs `work/decrypted-eu-260128/extracted-safe/mango-rootfs/`, abbreviated **`R/`**. Labels follow the
project convention: **[E]** = measured evidence in this image, **[I]** = inference. Anything that requires
running the kernel is called out explicitly and is **untested on hardware** (and mostly untested in QEMU too;
see §5). A driver existing in the image says nothing about whether the silicon is actually wired on a given
production unit — that distinction is kept explicit throughout.

---

## Summary table

| Vector | Hardware present? | Software enabled? | Root path? | Evidence |
| --- | --- | --- | --- | --- |
| **WiFi (802.11)** | **Yes** — Broadcom/Cypress CYW89359 (BCM4359B1) PCIe, driver + firmware + NVRAM all ship | **Disabled by default** — `modprobe.d` blacklist + GPIO power gate + MICOM state gate + path-flag; enable path exists (supplicantmanager + wpa_supplicant) | **No** (no sshd/hostapd) | `bcmdhd.ko`, `cfg80211.ko`, `lib/firmware/bcmdhd/{rtecdc.bin,nvram.txt,4359b1.clm_blob}`, `etc/modprobe.d/wifi_disable.conf`, `app/bin/supplicantmanager`, `etc/wpa_supplicant.conf` |
| **USB Ethernet** | **Plausible** — full usbnet family ships (loadable, symbols resolve) | **Disabled in practice** — connman ignores `eth*`/`usb1`/`dbg*`; static-IP helper script is absent; no SSH daemon | **No** — `dropbear` binary absent | `kernel/drivers/net/usb/{usbnet,cdc_ether,asix,r8152,smsc95xx,...}.ko`, `lib/udev/rules.d/99-static-ip.rules`, `lib/systemd/system/connman.service` |
| **UART (serial)** | **Yes** — 4 × 8250 UARTs (ttyS0–ttyS3) evidenced | **Console login gated by MICOM** — default/dev has agetty on ttyS2; production `secure_console=1` deletes `/dev/ttyS2` | **Yes, conditionally** — ttyS2 login (dev config), gated by `/sys/module/micom/parameters/secure_console` | `8250.ko/8250_pci.ko/8250_dw.ko` (built-in), `etc/esinit_agetty.sh`, `etc/securetty` (`ttyS2`), `lib/systemd/esinit`, ABL cmdline `console=ttyS2,115200n8` |
| **CAN** | **No socketcan controller** — core stack only | **Stack enabled, no controller** — `can`/`can-raw`/`can-bcm`/`can-gw`/`can-dev` built in and loaded at boot, but no controller driver, no vcan/slcan, no tools | **No** | `kernel/net/can/can.ko` + `can-raw/can-bcm/can-gw.ko` (built-in), boot log `can: netlink gateway (rev 20130117)`, `app/bin/micommanager_userspace` D-Bus `/Can` |

Bottom line: **WiFi is a real, fully-populated stack that is software-disabled by default and turned on by a
vendor daemon under MICOM/GPIO control — it is not hardware-absent.** USB Ethernet is drivable at the kernel
level but has no working address/SSH path in this image. UART has a gated serial console (ttyS2) plus three
other fixed-purpose UARTs. CAN is a socketcan *core* with no controller driver and no userspace — vehicle CAN
actually rides the MICOM link, not socketcan.

---

## 1. WIFI — hardware present, software-disabled by default

### 1.1 Chipset driver and modules (built-in vs loadable)

| Module | Location in image | Status |
| --- | --- | --- |
| `cfg80211.ko` | `R/lib/modules/4.1.27-abl/kernel/net/wireless/cfg80211.ko` | **loadable** (.ko, not in `modules.builtin`) |
| `bcmdhd.ko` | `R/lib/modules/4.1.27-abl/kernel/drivers/net/wireless/bcmdhd/bcmdhd.ko` | **loadable** (.ko, not in `modules.builtin`) |
| `mac80211.ko` | — | **absent** (bcmdhd is a full-MAC driver, so no mac80211 needed) |

[E] `bcmdhd` is the vendor/Android Broadcom full-MAC driver (not the mainline `brcmfmac`). Its PCI alias in
`R/lib/modules/4.1.27-abl/modules.alias` is `pci:v000014E4d*sv*sd*bc02sc80i*` — vendor **14E4 = Broadcom**,
class `02 80` = network/other. No `brcmfmac`, `wlcore`, `rtl8xxxu`, `iwlwifi`, `ath9k` or `mt76*` modules exist
anywhere in the image.

[E] `R/lib/modules/4.1.27-abl/modules.dep` contains
`kernel/drivers/net/wireless/bcmdhd/bcmdhd.ko: kernel/net/wireless/cfg80211.ko` — the load chain is resolvable
(cfg80211 has no further deps).

### 1.2 Firmware blobs — a real, specific chip

[E] `R/lib/firmware/bcmdhd/` ships the complete radio firmware set:

- `rtecdc.bin` — WiFi firmware image
- `rtecdc_mfg.bin` — manufacturing-test firmware image
- `4359b1.clm_blob` — country/locale matrix blob, named **BCM4359B1**
- `nvram.txt` — per-module calibration. Header: `#LGIT RBHP-B207A module nvram v1.0 171229 Release` and
  `#CYW88359 WLBGA 2G iPA/iLNA, 5G iPA/iLNA`. Contains `ccode=GB` (Great Britain regulatory) and
  `macaddr=00:90:4c:12:d0:e2`.
- `WiFiDriverVersion.txt` = `1.363.68`, `WiFiFWVersion.txt` = `9.40.112.10`

[I] Chip identification: the NVRAM header (`CYW88359`) plus the CLM blob (`4359b1`) identify a **Cypress/Broadcom
CYW89359 = BCM4359B1** 2×2 802.11ac WiFi/BT combo. The BT half of the same module ships as
`R/app/share/firmware/BCM4349B1_002.002.014.0197.0487.hcd` (Bluetooth patchram, see §3 — it is loaded onto
`/dev/ttyS0` by the BT daemon). A *second*, unrelated Marvell firmware also ships —
`R/lib/firmware/mrvl/pcieuart8897_combo.bin` (88W8897) — **but there is no `mwifiex`/Marvell driver in the
image**, so that blob is orphaned in this build. [I] Likely a different radio/ECU or an unused option, not the
head-unit WiFi this image drives.

### 1.3 Userspace: supplicant, tools, network manager

[E] Present: `R/usr/sbin/wpa_supplicant`, `R/usr/sbin/wpa_cli`, `R/usr/bin/wpa_passphrase`, `R/usr/sbin/iw`,
`R/sbin/iwconfig`, `R/usr/sbin/wl` (the proprietary Broadcom `wl` control tool, a 2 MB x86-64 ELF).
`rfkill` is a busybox applet (`R/usr/lib/opkg/alternatives/rfkill` → `/bin/busybox`, priority 50; the vendor
busybox `R/bin/busybox.vendor` contains the `rfkill`/`ifconfig`/`udhcpc` applets). `systemd-rfkill` is also
present (`R/lib/systemd/systemd-rfkill`, `R/lib/systemd/system/systemd-rfkill@.service`).

[E] **Absent**: `hostapd` and `dnsmasq` (no AP/hotspot server side anywhere), no `dhcpcd`/`dhclient`.

[E] `R/etc/wpa_supplicant.conf` exists — a station-mode config: `ctrl_interface=/var/run/wpa_supplicant`,
`network={ key_mgmt=NONE }` (open network). `R/etc/default/volatiles/99_wpa_supplicant` creates
`/var/run/wpa_supplicant` (0700 root).

[E] Network manager is **ConnMan** (`R/usr/sbin/connmand`, `R/usr/sbin/connmanctl`,
`R/lib/systemd/system/connman.service`, enabled at `R/etc/systemd/system/multi-user.target.wants/connman.service`).
Its exec line is decisive:

```
ExecStart=/usr/sbin/connmand -n --nodnsproxy --nobacktrace --nodevice=rmnet_usb1,rmnet_usb2,rmnet_usb3,rmnet_usb4,rmnet_usb5,rmnet_usb6,rmnet_usb7,dbg0,dbg1,dbg2,can0,eth1,eth2,ncmF0,usb1,eth0,tem0,br0,br0:0,ncm0
```

`wlan0` is **not** in the `--nodevice` list, so ConnMan would nominally manage WiFi — but its plugin directory
`R/usr/lib/connman/plugins/` is **empty**, so ConnMan has no WiFi backend on this build. WiFi is instead driven
by the vendor daemon below; ConnMan is effectively de-fanged (see §2).

### 1.4 The enable/disable control path — MICOM state + GPIO, not D-AUDIO

[E] `R/app/bin/supplicantmanager` (80 KB, links `libgpio_ctl.so.1`, `libdbus-1`, `libsystemd`, `libdlt`,
`libglib`) is the WiFi power/state manager. Its dynamic symbols spell out the whole lifecycle:

- `WifiOnThread::wifi_turn_on()`, `wifi_turn_off()`, `wifi_on(int)`, `reqEnableWIFI(int)`, `disableWifi()`
- `WifiOnThread::is_wifi_module_loaded()`, `start_wpa_supplicant()`, `is_supplicant_running()`,
  `send_result_kill_supplicant()`, `setWpaPid()/getWpaPid()`
- `WiFiStateManager::powerKeyStateChanged(unsigned char)`, `accStateChanged(bool)`, `driverDoorStateChanged(bool)`
- `MicomInterface::SubscribeSystemStateChanged(std::function<void(bool)>, std::function<void()>)`,
  `MicomInterface::AskSysBootInfo()`
- `off_WLAN_REG_ON()`, `reset_WLAN_REG_ON()`

[E] The two GPIO functions hard-code the Broadcom power-enable net. Disassembly of `R/app/bin/supplicantmanager`:

```
reset_WLAN_REG_ON():  movl $0x1d2,%edi ; jmp resetHW(int)     # GPIO 0x1D2 = 466
off_WLAN_REG_ON():    movl $0x1d2,%edi ; jmp offHW(int)       # GPIO 0x1D2 = 466
```

`WLAN_REG_ON` is the standard Broadcom WiFi regulator-enable pin; it is toggled through `libgpio_ctl`
(`R/app/lib/libgpio_ctl.so.1` exports `set_gpio_value_general`, `get_gpio_general`, `check_gpio_info`).

[E] Service wiring:

- `R/lib/systemd/system/supplicantmanager.service` — `Description= Wifi ACC Mode Manager Daemon`,
  `ExecStartPre=/sbin/modprobe cfg80211`, `ExecStart=/app/bin/supplicantmanager`. Its `[Install]` block is
  commented out, i.e. it is **not enabled as a normal service**.
- `R/lib/systemd/system/supplicantmanager.path` — `PathExists=/tmp/no_unece`, `Unit=supplicantmanager.service`.
  The daemon is only pulled in when the runtime flag file `/tmp/no_unece` is created.
- `R/app/bin/supplicantmanager.conf` — `SESSION_BUS_ADDRESS_FILE=/tmp/session_appmgr`,
  `GEN5_COUNTRY_EU = GEN5_COUNTRY_EU` (EU region select).

[E] **The default-off mechanism at the module level**: `R/etc/modprobe.d/wifi_disable.conf`:

```
blacklist bcmdhd
blacklist cfg80211
```

[I] Taken together: WiFi is gated at three layers — (a) `modprobe.d` blacklist stops automatic/alias loading of
`bcmdhd`/`cfg80211`; (b) the radio is powered off until `supplicantmanager` asserts `WLAN_REG_ON` (GPIO 466);
(c) `supplicantmanager` only does so in response to MICOM vehicle-state changes it subscribes to (power key, ACC,
driver door) via `MicomInterface`, and only runs at all when `/tmp/no_unece` exists. This is a
**MICOM + GPIO + path-flag** gate; there is no D-AUDIO involvement in WiFi control.

### 1.5 UI toggle

[E] `R/app/share/AppSetup/qml_new2.0/wifi/` contains a complete WiFi settings UI (12 files), including
`Q_AppSettingWifi.qml`, `Screen_AppSettingWifiDetails.qml`, `Screen_AppSettingWifiAddNetwork.qml`,
`Screen_AppSettingWifiAddKeyboard.qml`, `Screen_AppSettingWifiHowToConnect.qml`, the subscription screens
`Screen_AppSettingWifiServiceAgreement.qml` / `Screen_AppSettingWifiServiceInformation.qml`, and
`Q_AppSettingUvo.qml` / `Q_AppSettingLive.qml`.

[E] The model exposes an on/off switch and live state: `property bool isWifiOnOff: AppSettingModel.wifiOnOff`
(`Screen_AppSettingWifiAddKeyboard.qml:20`), `Listwifi.isWifiEnabled`, `Listwifi.doUpdateList`,
`AppSettingModel.isWifiConnected`, `AppSettingModel.wifiMacAddr`, `AppSettingModel.wifiServiceAgree`. UI events
include `KEY_EVT_SETUP_WIFI_CONNECT_TO_NETWORK`, `KEY_EVT_SETUP_WIFI_REQUEST_ADD_NETWORK`,
`EVT_GOTO_SETUP_WIFI_ENTER_PASSWORD`, `KEY_EVT_SETUP_WIFI_REFRESH_NETWORK`, `KEY_EVT_SETUP_WIFI_SCAN_STOPPED`,
and `KEY_EVT_POPUP_WIFI_EUZONE_SHOW` (EU regulatory popup). The same tree exists under `qml_eco3.0/` and
`qml_genesis/`.

[E] The vendor firewall whitelists `wlan0` explicitly: `R/etc/default/iptables/30_wl_static.conf` and
`R/etc/default/iptables/wifi/{wirelesspp,wifi_station}.conf` all contain `-i wlan0` / `-o wlan0` rules
(`WL_STATIC_IN`/`WL_STATIC_OUT` chains). `wlan0` is the expected station interface name.

### 1.6 Verdict — WIFI

**Not hardware-absent.** Driver (`bcmdhd`/`cfg80211`), firmware (`rtecdc.bin`/`nvram.txt`/`4359b1.clm_blob`),
wpa_supplicant, a dedicated control daemon, firewall rules and a full UI all ship. It is
**software-disabled by default**: `modprobe.d` blacklists both modules (kills automatic/alias loading, though an
explicit `modprobe <name>`/`insmod` still works — which is exactly the daemon's load path), the radio is powered
off (GPIO 466 `WLAN_REG_ON`), and the enable daemon is itself conditional on a runtime flag and MICOM state. There is **no** `hostapd`/`dnsmasq`, so
this is station (client) WiFi — the car connecting to an external network for the "WiFi service"/live feature —
not an AP the attacker connects to. No CRDA/`regulatory.db` ships; [I] regulatory domain comes from `nvram.txt`
`ccode=GB` + the kernel's world regdomain (matching the EU-zone popup in the UI).

---

## 2. USB ETHERNET — drivers present, no working address/SSH path

### 2.1 Kernel modules

All loadable (`.ko`, none in `modules.builtin`), all under `R/lib/modules/4.1.27-abl/kernel/drivers/net/usb/`:

| Module | Purpose |
| --- | --- |
| `usbnet.ko` | generic USB network framework |
| `cdc_ether.ko` | CDC ECM/EEM (also matches RNDIS-class devices per `modules.alias`) |
| `asix.ko` | ASIX AX88xxx (AX8817x/AX88772/AX88772B/AX88760) |
| `r8152.ko` | Realtek RTL8152/8153 |
| `smsc95xx.ko` | SMSC/Microchip LAN95xx |
| `cdc_subset.ko`, `net1080.ko` | older "subset"/NetChip devices |

[E] **Absent**: `ax88179_178a.ko` (ASIX AX88179 USB3 gigabit) — no AX88179 driver in this image.
[E] `modules.dep` shows all chains resolve: e.g. `asix.ko → usbnet.ko, libphy.ko, mii.ko, usbcore.ko, usb-common.ko`;
`r8152.ko → mii.ko, usbcore.ko, usb-common.ko`; `usbnet.ko → mii.ko, usbcore.ko, usb-common.ko`.

### 2.2 Address assignment and the de-fanged ConnMan

[E] ConnMan (the only network manager) is told to ignore every ethernet-class interface in
`R/lib/systemd/system/connman.service`:
`--nodevice=...,dbg0,dbg1,dbg2,can0,eth1,eth2,ncmF0,usb1,eth0,tem0,br0,br0:0,ncm0`. So a USB dongle that comes up
as `eth0`/`usb1` gets **no DHCP** from ConnMan.

[E] The only address-assignment rule is `R/lib/udev/rules.d/99-static-ip.rules`, which targets a *specific*
vendor debug dongle:

```
ACTION=="add", KERNEL=="dbg*", SUBSYSTEM=="net", ENV{ID_VENDOR_ID}=="0424", ENV{ID_MODEL_ID}=="9e00", GOTO="ip_setup_go"
...
RUN+="/home/root/ip_setup.sh %k"
```

`0424:9e00` is SMSC/Microchip (the `smsc95xx.ko` device family) — a known automotive debug ethernet adapter.
**But** the helper `R/home/root/ip_setup.sh` does **not** exist in the image (`R/rw_data/home/root/` is empty),
so even that static-IP path is inert. [I] The rule therefore does not actually assign an address in this build.

[E] A DHCP *client* does exist — `R/bin/busybox.vendor` includes the `udhcpc` applet (plus `ifconfig`,
`rfkill`), and ConnMan has a built-in DHCP client — but nothing is wired to run either on a USB ethernet device.

### 2.3 SSH / remote shell

[E] The `dropbear` **binary is absent** (`R/usr/sbin/dropbear`, `dropbearmulti`, `dropbearkey`, `dbclient` all
missing). What ships instead:

- `R/lib/systemd/system/dropbear@.service` — `ExecStart=-/usr/sbin/dropbear -i -s -r ...`,
  `ConditionPathExists=/tmp/secure_console_disable` (only activates in the "secure console disabled" dev mode),
  and `StandardInput=socket`.
- `R/etc/dropbear/authorized_keys` — **397 bytes** (the vendor's public key ships even though the daemon does not).
- `R/etc/dropbear/dropbear_publickey_installer.sh`.
- `R/usr/lib/opkg/alternatives/{ssh,scp}` → target `/usr/sbin/dropbearmulti` (priority 20), also absent.

[E] No `sshd`, no OpenSSH binaries anywhere. Combined with §2.2, the earlier finding stands: **USB Ethernet is
not a remote-shell vector on this build** — the driver can be loaded, but nothing assigns an address and there is
no SSH daemon to reach.

---

## 3. UART — 4 evidenced 8250 UARTs, gated serial console on ttyS2

### 3.1 Serial drivers — built in

[E] `R/lib/modules/4.1.27-abl/modules.builtin` lists these as compiled-in (`=y`):

```
kernel/drivers/tty/serial/serial_core.ko
kernel/drivers/tty/serial/8250/8250.ko
kernel/drivers/tty/serial/8250/8250_pci.ko
kernel/drivers/tty/serial/8250/8250_dw.ko
```

This is an Intel Apollo Lake/Broxton x86-64 SoC, so the 8250 (PCI + DesignWare MMIO) drivers are the relevant
ones; there is no `msm_serial`/`samsung`/`tegra` driver (not applicable to x86). Also built in:
`kernel/drivers/lge/ttyhook/ttyhook.ko` (LGE TTY interception hook, used for the GPS UART) and loadable
`kernel/drivers/cbc/cbc-ldisc.ko`.

### 3.2 Which ttyS devices exist and what owns them

[E] Four UARTs are evidenced by name across the image:

| Port | Owner / purpose | Evidence |
| --- | --- | --- |
| `ttyS0` | **Bluetooth HCI** (BCM4349B1 patchram) | `R/lib/systemd/system/vbtd.service` → `ExecStart=/app/bin/vbtd -d /dev/ttyS0 -p /tmp/bt_patchram.hcd`; `R/etc/smack_setup.sh` labels `/dev/ttyS0` `System::bluetooth` |
| `ttyS1` | **MICOM UART** | `R/app/bin/micommanager_userspace` strings: `/dev/ttyS1`, `Failed to open the MICOM UART port`; `R/etc/smack_setup.sh` labels `/dev/ttyS1` `System::micominterface` |
| `ttyS2` | **Debug/serial console** | bootloader cmdline (below), `R/etc/securetty` lists `ttyS2`, `R/etc/esinit_agetty.sh` starts agetty on it; `R/app/bin/AppStandbyClock` strings reference `/sys/devices/pci0000:00/0000:00:18.2/dw-apb-uart.10/tty/ttyS2/...` (DesignWare APB UART at PCI 0000:00:18.2) |
| `ttyS3` | **GPS** | `R/lib/systemd/esinit` → `ln -s ttyS3 ttyGPS` |

[E] Debug/test strings in vendor binaries: `R/app/bin/vbtd-51` and `R/app/bin/vbtd-63` both print
`-d device   set the hci device interface (e.g. /dev/ttyHS0)` (the HCI-UART tool, used here with `/dev/ttyS0`);
`R/usr/sbin/wl` (Broadcom tool) references `/dev/ttyS0`/`/dev/ttyS1`.

### 3.3 Bootloader console arguments

[E] The ABL boot-parameter blob (extracted at
`work/abl-mea-unpack/Unpacked_abl1714-Batch10-Ver.11.00-sign-8MB.bin/OBBP 0000 [0x401000]/ELK`) contains:

```
console=tty0 kmemleak=off root=/dev/sda2 rootwait rw init=/sbin/init clocksource=hpet loglevel=8
console=ttyS2,115200n8 earlycon=uart8250,mmio32,0xfc000000,115200n8 i915.tsd_hack_hdmi=0xff
portmux_intel_drcfg.usb0_init_state=0 portmux_intel_drcfg.usb0_auto_role=1 portmux_intel_drcfg.usb0_hardware_mode=0
```

So the kernel gets a second console on **`ttyS2` at 115200 8n1**, and an earlycon on the 8250 DesignWare UART at
MMIO `0xfc000000`. The in-image kdump path repeats it: `R/lib/systemd/kp.sh` re-kexecs with
`console=ttyS2,115200n8`.

### 3.4 Login on the serial console — MICOM-gated

[E] `R/etc/esinit_agetty.sh`:

```
#autologin root
#setsid /sbin/agetty -a root -8 -L ttyS2 115200 xterm
setsid /sbin/agetty  -8 -L ttyS2 115200 xterm
```

(Root auto-login is commented out; a password prompt is used. `R/etc/securetty` permits root on `console`,
`tty1`, `ttyS2`.)

[E] `R/lib/systemd/esinit` gates whether that agetty actually runs and whether the device even survives boot:

```
touch /tmp/secure_console_disable                       # default: secure console OFF → login allowed
...
if [ "$(cat /sys/module/micom/parameters/secure_console)" = "1" ]; then
    rm /tmp/secure_console_disable
    rm /dev/ttyS2                                        # production: delete the UART node
fi
...
if [ -f /etc/esinit_agetty.sh ] && [ -f /tmp/secure_console_disable ]; then
    /etc/esinit_agetty.sh &                              # start agetty on ttyS2
fi
```

[I] So: by default (or when MICOM's `secure_console` parameter is absent/0) the unit **does** expose an
`agetty` login on `ttyS2` (115200 8n1), with a password from `R/etc/passwd.legacy`. When MICOM reports
`secure_console=1` (the production posture), `/dev/ttyS2` is removed and the login goes away. The same
`/tmp/secure_console_disable` flag gates the (absent) dropbear socket service (§2.3) — one flag switches the
whole "secure console" dev mode.

[E] systemd getty units: only `getty@tty1.service` is enabled
(`R/etc/systemd/system/getty.target.wants/getty@tty1.service`). There is **no** `serial-getty@.service`.
`console-getty.service` (`agetty ... console 115200,38400,9600`) exists but is **not** enabled — the serial
login path is the esinit/agetty-on-ttyS2 one above, not a systemd getty.

---

## 4. CAN — socketcan core built in, no controller, no tools

### 4.1 What is compiled in

[E] `R/lib/modules/4.1.27-abl/modules.builtin` (all `=y`, compiled into the kernel):

```
kernel/net/can/can.ko
kernel/net/can/can-raw.ko
kernel/net/can/can-bcm.ko
kernel/net/can/can-gw.ko
kernel/drivers/net/can/can-dev.ko
```

[E] The boot log (QEMU boot of this kernel, `work/vm/bootable/runs/*/serial.log`) confirms they load:

```
can: controller area network core (rev 20120528 abi 9)
can: raw protocol (rev 20120528)
can: broadcast manager protocol (rev 20120528 t)
can: netlink gateway (rev 20130117) max_hops=1
```

### 4.2 What is missing

[E] **No CAN controller driver** — no `m_can`, `sja1000`, `flexcan`, `c_can`, `ifi_canfd`, `kvaser`, `peak_*`,
`ems_*` or `gs_usb` module, neither built-in nor loadable (`modules.builtin` and `modules.alias` have no such
entries). **No `vcan.ko` and no `slcan.ko`** — so there is no virtual CAN either.

[E] **No socketcan userspace tools** — `candump`, `cansend`, `canconfig` are all absent (only the busybox `ip`
alternative exists, which cannot create a `type can`/`type vcan` link without a controller/vcan driver).

[E] The only `can0` reference in the entire rootfs is ConnMan's exclusion list —
`R/lib/systemd/system/connman.service` contains `--nodevice=...,can0,...` — i.e. the vendor *expects* a `can0`
might exist and explicitly tells ConnMan to leave it alone. Nothing in the image creates it.

### 4.3 Where vehicle CAN actually lives — the MICOM

[E] `R/app/bin/micommanager_userspace` (the MICOM gateway daemon) registers D-Bus service
`com.lge.car.micom` and exposes objects `/Radio /Tmu /Ihu /Hdr /Tmc /Can /Eng`. Its strings also reference the
MICOM transport (`/dev/ttyS1`, `Failed to open the MICOM UART port`) and the SPI path
`/sys/bus/spi/drivers/micom_if/spi1.0/...` (from `R/app/bin/AppStandbyClock`).

[I] So vehicle CAN frames are exchanged with the body computer through the **MICOM link** (SPI `micom_if` /
UART `ttyS1`) and surfaced via the `com.lge.car.micom` D-Bus `/Can` object — **not** through the Linux socketcan
`can0` interface. The socketcan stack in the kernel is essentially dormant: core protocol modules are loaded at
boot, but with no controller driver and no userspace there is no way for this image to bring up a `can0`.

---

## 5. Cheapest next experiment per vector (QEMU projection)

Reminder: the research init is a busybox shell (`R/init`) that does **not** run systemd or udev, so nothing is
auto-loaded and none of the systemd units above run automatically. A module can only be loaded if it is a
loadable `.ko` whose symbols resolve. These are all **untested on hardware**; only the ones that need a QEMU
device are listed as such.

1. **WIFI** — `insmod` the chain and watch the PCI probe fail (there is no emulatable BCM4359).
   `modprobe cfg80211 && modprobe bcmdhd` (or `insmod` the two `.ko` files in dependency order). Expected:
   `cfg80211` loads cleanly, `bcmdhd` loads (symbols resolve against cfg80211) and then probes with "no device"
   because QEMU has no Broadcom 14E4 WiFi. This proves the modules load and resolve; it cannot prove the radio.
   A second, userspace-side step is to run `R/app/bin/supplicantmanager` against the existing
   `micom-dbus-sim` and observe whether it calls `modprobe`/`start_wpa_supplicant()` and toggles GPIO 466.

2. **USB ETHERNET** — attach a QEMU USB NIC and load the driver manually. `-device usb-net` (QEMU's CDC-ECM
   gadget) plus `modprobe usbnet && modprobe cdc_ether` (or `r8152`/`asix` for a passed-through real dongle via
   `usb-host`). Then `busybox udhcpc -i eth0` to test whether DHCP can be forced manually. Expected: the module
   loads and `eth0` appears; nothing assigns an address automatically (ConnMan is off and excludes `eth0`), and
   there is no SSH daemon to connect to regardless.

3. **UART** — inspect the existing boot serial capture for the `ttyS2` agetty banner, and toggle the gate.
   In the already-booting VM, check `/dev/ttyS2` existence and `cat /proc/cmdline` (expect
   `console=ttyS2,115200n8`), then set `echo 1 > /sys/module/micom/parameters/secure_console` (or boot with the
   parameter) and confirm `/dev/ttyS2` is deleted per `R/lib/systemd/esinit`. Cheapest possible: grep the
   archived `serial.log` for an agetty/login line on ttyS2.

4. **CAN** — a deliberate *negative* probe of the built-in core. `ip link add dev vcan0 type vcan` (expect
   `RTNETLINK answers: Operation not supported` because `vcan` is not compiled in) and `ls /sys/class/net`
   (expect no `can0`), plus `ip link add can0 type can` failing for lack of a controller. This characterises the
   stack as "core present, no controller" for the record. The only way to make a *positive* CAN test is to
   cross-build a matching `vcan.ko` (or `slcan.ko`) against this exact 4.1.27-abl kernel and `insmod` it — a
   separate build task, not an image inventory.

---

## Appendix — module classification (quick reference)

- **WiFi**: loadable `cfg80211.ko`, `bcmdhd.ko` (depends on cfg80211); `mac80211` absent; `brcmfmac`/`iwlwifi`/
  `ath9k`/`rtl8xxxu`/`mt76*`/`wlcore` absent.
- **USB Ethernet**: loadable `usbnet`, `cdc_ether`, `asix`, `r8152`, `smsc95xx`, `cdc_subset`, `net1080`;
  `ax88179_178a` absent.
- **Serial**: built-in `serial_core`, `8250`, `8250_pci`, `8250_dw`, `ttyhook`; loadable `cbc-ldisc`.
- **CAN**: built-in `can`, `can-raw`, `can-bcm`, `can-gw`, `can-dev`; no controller driver; no `vcan`/`slcan`/
  `gs_usb`; no `candump`/`cansend`.
