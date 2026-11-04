# Turning the WiFi on — the procedure the image itself implies

The radio is a **Cypress/Broadcom CYW88359 (BCM4359B1)** PCIe part with its driver, firmware, CLM blob and NVRAM all present (see
`docs/physical-and-wireless-vectors.md` §1). It is off by default for three reasons, all of them software, and the image contains the
machinery to reverse every one of them. This document is that procedure.

**Nothing here has been executed on hardware, and none of it can be executed in the QEMU projection** — QEMU has no CYW89359 device
and no GPIO controller, so there is nothing for `bcmdhd` to bind to and nothing for the regulator pin to drive. What follows is
derived from the shipped units, configs and the daemon's own disassembly, and is labelled accordingly.

---

## 0. What has to be true first

- **Root.** Everything below needs uid 0. On a stock unit the only no-vulnerability route to that is the serial console
  (`Ioniq5-VULNERABILITIES.md` V-049), which is enabled by default and prompts for the fleet-wide root password.
- **The part must actually be populated on your unit.** The NVRAM names the module (`RBHP-B207A`) but software cannot prove the
  silicon is fitted. `lspci -nn | grep -i 14e4` after step 2 is the first honest check.

## 1. The three gates, and how each is opened

| Gate | Evidence | What opens it |
| --- | --- | --- |
| Blacklist | `/etc/modprobe.d/wifi_disable.conf` = `blacklist bcmdhd`, `blacklist cfg80211` | name the modules explicitly, or `modprobe -f`, or remove the file |
| Regulator pin | `supplicantmanager` disassembly: `reset_WLAN_REG_ON(): movl $0x1d2,%edi` / `off_WLAN_REG_ON(): movl $0x1d2,%edi` — GPIO **0x1D2 = 466** is the Broadcom `WLAN_REG_ON` enable | drive GPIO 466 high |
| MICOM state + trigger file | `supplicantmanager.path` = `PathExists=/tmp/no_unece`, `Unit=supplicantmanager.service`; the daemon subscribes to `MicomInterface::SubscribeSystemStateChanged` and gates on `powerKeyStateChanged` / `accStateChanged` / `driverDoorStateChanged` | create `/tmp/no_unece` **and** keep ignition on |

Blacklist entries only suppress *alias-based autoloading*; an explicit `modprobe bcmdhd` is not blocked by them, which is why the
`ExecStartPre=/sbin/modprobe cfg80211` in the service is enough on its own.

## 2. Load the driver

```sh
modprobe cfg80211          # dependency first; modules.dep has it resolvable
modprobe bcmdhd            # or: insmod /lib/modules/4.1.27-abl/kernel/drivers/net/wireless/bcmdhd/bcmdhd.ko
lsmod | grep -E 'bcmdhd|cfg80211'
lspci -nn | grep -i 14e4   # Broadcom 14e4 — the first honest check that silicon exists
dmesg | tail -40           # bcmdhd prints firmware/NVRAM lines when it probes
```

If `bcmdhd` loads but does not probe, the radio is unpowered — that is step 3, and it is the usual reason.

## 3. Power the regulator (GPIO 466 / 0x1D2)

Prefer the vendor's own library so the pin is driven exactly as the daemon would drive it. `libgpio_ctl.so.1` exports
`set_gpio_value_general`, `get_gpio_general` and `check_gpio_info`; `supplicantmanager` calls `reset_WLAN_REG_ON()` for this pin.

Two ways, in order of preference:

1. **Let the daemon do it** (step 4). `supplicantmanager` owns this pin and will call `reset_WLAN_REG_ON()` when its state machine
   decides to turn WiFi on. This is the supported path and the one to try first.
2. **Drive it yourself** via sysfs, if the pin is exported or exportable:

```sh
GPIO=466
[ -d /sys/class/gpio/gpio$GPIO ] || echo $GPIO > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio$GPIO/direction
echo 1   > /sys/class/gpio/gpio$GPIO/value
cat /sys/class/gpio/gpio$GPIO/value     # expect 1
```

If `export` fails with `EINVAL`/`EBUSY`, the pin is owned by a driver (`libgpio_ctl`'s own path) and option 1 is the only way.
Also check `rfkill list` — a soft block must be cleared with `rfkill unblock all`.

## 4. Start the vendor daemon, which is the actual state machine

```sh
touch /tmp/no_unece                  # this is the path-unit trigger, verbatim from supplicantmanager.path
systemctl start supplicantmanager    # if systemd is running
# or directly, with the session bus present:
SESSION_BUS_ADDRESS_FILE=/tmp/session_appmgr /app/bin/supplicantmanager &
```

Its own symbols say what to expect in the log: `is_wifi_module_loaded()`, `wifi_turn_on()`, `start_wpa_supplicant()`,
`is_supplicant_running()`, and the results are reported through DLT. Ignition state matters — the daemon watches
`accStateChanged` and `powerKeyStateChanged`, so do this with the car on.

## 5. Bring the interface up

```sh
iw dev                              # expect a wlan0 with the BCM4359 phy
ifconfig wlan0 up
wpa_supplicant -i wlan0 -c /etc/wpa_supplicant.conf -B    # shipped config is station mode, key_mgmt=NONE
udhcpc -i wlan0                                           # busybox dhcp client
ifconfig wlan0
```

The shipped `wpa_supplicant.conf` is `ctrl_interface=/var/run/wpa_supplicant` with `network={ key_mgmt=NONE }` — an **open network**
stanza. Pointing it at a WPA2 network means editing that file or using `wpa_passphrase` + `wpa_cli`.

ConnMan will not help: it runs with `--nodevice=…` covering the wired and USB interfaces, and its plugin directory is **empty**, so it
has no WiFi backend at all on this build.

## 6. What "on" then gets you, and what it does not

- **You get**: an associated station interface, outbound connectivity, and the unit's own mDNS/SSDP components becoming reachable —
  `mdnsd` is the only binary in `/app/bin` that references `AF_INET`, and `AppSDS` carries the UPnP/SSDP strings.
- **You do not get a shell.** There is **no `sshd`, no `dropbear` binary, no `telnetd`, no `hostapd` and no `dnsmasq`** in the image,
  and `systemd` has no TCP socket units. Nothing in the image listens on a TCP port by default.
- **NVRAM carries a fixed MAC**: `macaddr=00:90:4c:12:d0:e2`. Units sharing an image share that address unless the NVRAM or the driver
  overrides it at runtime — worth knowing before two of them are on the same network.

## 7. Why this matters for the security work

Turning WiFi on is the step that converts "no network-facing attack surface" into "some". The image's only network-facing components
are `mdnsd` and `AppSDS` (UPnP/SSDP), both of which would then be parsing attacker-reachable input **as root**, since everything on this
unit runs as uid 0. That is the direction to look for a remote vector — but it is a hypothesis, not a finding: nothing here has been
demonstrated against those components.

**Correction-style note:** an earlier note in this repository treated WiFi as "hardware unknown". The image independently corroborates a
specific part (driver + firmware + CLM blob for `4359b1` + NVRAM naming `CYW88359`). That is strong evidence the part is fitted to
units of this family; it is still not the same as having seen one.
