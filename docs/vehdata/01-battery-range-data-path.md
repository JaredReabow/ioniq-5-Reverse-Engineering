# Battery / Range data path — static mapping (final report)

Date: 2026-11-05. Workspace: `work/vm/vehdata`. Rootfs: `NE.EUR.S5W_L.001.001.260128`,
x86-64 Linux 4.1.27. **Stated limitation: both VM runs this session hit the 900 s runner
timeout** (`elapsed_seconds` 900.23 / 900.25). The static mapping below is the deliverable;
Part B is **not a valid test** (§3).

## 1. The QML binding

`app/share/AppHomeScreen/qml_eco3.0/component/QButtonBatteryHomeItemEco3.qml` (eco3.0 GUI
variant; instantiated by `qml_eco3.0/HomeScreen/Screen_HomeScreen_Widget_Advanced.qml` when
`_isEV && _isWideScr`).

- Battery number = `AppPHEVModel.display_Batlevel` — `value_battery` shows `"---"` when `< 0`:
  `text: ... (AppPHEVModel.display_Batlevel >= 0 ? AppPHEVModel.display_Batlevel : "---")`
- Range number = `rangeWidgetConvert` = `AppPHEVModel.display_DTE` (km; `/ (412.0/256.0)` for
  miles) — `range_value` shows `"---"` unless
  `rangeWidgetConvert > 0 && !AppPHEVModel.dte_Calc && AppPHEVModel.dteOffDisp !== 1`.

## 2. What feeds those properties in the binary

`AppPHEVModel` slots write the two properties: `slot_xEV_SocDis(int)` (SOC; sibling
`slot_CR_Bms_DisplaySoc`) and the DTE slots `slot_VCU_DteBaseVal`, `slot_VCU_DteAddVal`,
`slot_CF_Clu_EVDTEDisp`, `slot_CLU_DTEVal`, `slot_MM_CR_Clu_TotalDTEDisp` (gates:
`slot_VCU_DteOffDispSta`, `slot_CF_Vcu_AvnDteCalc`, `vcuReady`). These are bound via
`AppPHEVModel::connectCanListenerSignals(QCANControllerListener*)` to
`QCANControllerListener::onCAN_data_received(SQCanFrameList)`, which is fed by the **raw `can0`
socket** (`HomeCanThread::open_port("can0")`, `CQCANController_CANTxRx::Initialize_raw_socket`).

Earliest outside-process write point: **a CAN frame on `can0`**. SOC is pinned from the
real-vehicle DLT to CAN id `0x2fc`, byte 7, 0.5 %/LSB (`0x77=119 → 59.5 %`). `com.lge.car.micom.can`
`NotifyCANTPRECVMsg` is a separate D-Bus path and is **not** upstream of these slots.

## 3. Part B is not a valid test

The 131,845-byte capture (`docs/vm/39-vehdata-after-notifycantprecvmsg-injection-2026-11-05.png`)
is **not** the laid-out home screen and is **not** evidence about injection. Inspected by eye:
1920×720, dark background, title bar, **KIA logo, no widgets** — the app's **powered-off
presentation**, the same state as `docs/vm/32-…`. `set_power_on_status` did **not** take effect in
that run, so the injected `NotifyCANTPRECVMsg` frames were never going to be visible regardless of
whether the D-Bus path works.

Marker log for that run (`work/vm/vehdata/runs/1793857420103938000/serial.log`):

- The app owned its name before the call: `NAME_OWNED=[com.lge.hkmc.avn.appfunc.AppHomeScreen]`
  — so "the app had not yet registered its bus name" is **not** the cause.
- The call landed and was accepted:
  `SET_POWER_ON_RESULT=[method return sender=:1.10 -> dest=:1.57 reply_serial=2]`.
- Power/acc/ign were already `int32 1` before and after — the value did not move (the call's
  effect is a re-emit/re-layout, not a status change, as the earlier gesture session also found).
- The app's 1926×753 surface (id 1004, first created 00:02:21) stayed the standby face; no new
  surface carrying the laid-out home appeared.

Reusable lesson: `method return` on `set_power_on_status` does **not** mean the app laid out. The
transition to the laid-out home is a separate app-internal step, and this run's log does not show
what gated it (ordering vs. app readiness is the suspect, but unread from this log).

**Byte-size lesson (this defeats the size shortcut).** The standby face is **131,845 bytes** in
this build, not the 120,5xx quoted earlier — two builds of the same standby frame differ by
~11 KB, larger than the gap between some reference sizes. Byte size does **not** identify state.
The only reliable test is the image: **KIA logo and no widgets → standby; Battery and Range placed
with `---` → laid out.**

## 4. The honest gap

Unread: the exact `NotifyCANTPRECVMsg` `ay` frame layout and whether that D-Bus path reaches the
widgets at all (vs. the raw `can0` feed); DTE's exact CAN id/byte is also unpinned.

Next single measurement: disassemble the `NotifyCANTPRECVMsg` handler in `app/bin/AppHomeScreen`
to recover its `ay` byte layout and connection target, and confirm whether `can0` is the only feed
by reading `HomeCanThread`/`CQCANController_CANTxRx` initialization (DLT) at boot.

---

## 6. Why `can0` never appears, measured inside the guest (2026-11-05)

A diagnostic boot on the authentic path, reading the driver's own state rather than inferring it:

```
/sys/class/net          lo rmnet_usb0..7                       no can0
/sys/module             can  can_gw  micom                     all three are LOADED
/sys/bus/spi/devices    (empty)                                no SPI device
/sys/bus/spi/drivers    spidev                                 the only SPI driver
/sys/bus/platform/drivers  (no micom entry)
dmesg   0.68  CAN device driver interface
        0.72  can: controller area network core (rev 20120528 abi 9)
        0.72  can: raw protocol
        0.69  MICOM I> [micom_init] Registering LGE MICOM interface driver
        4.38  [esinit] micom SPI info is OK
```

**So the stack is present and the driver is registered - it simply never probes a device.** The micom
driver is a platform/SPI driver; QEMU provides **no SPI device and no micom platform device**, so there
is nothing to bind to, and the netdevs are created in the probe path that never runs.

There is also a fidelity gap worth naming: **userspace reports `micom SPI info is OK`** while the kernel
has no SPI device at all. The SPI gate and the SPI bus are unrelated things, and only one of them is
satisfied in the projection.

### What that means for the two routes

| route | verdict from this measurement |
|---|---|
| **bring the micom link up** | needs a platform/SPI **device** to exist before any handshake matters, which is a board/device-tree change, not a userspace one |
| **vcan** | still needs a kernel tree and `vcan.ko`, neither of which ships |
| **CAN shim (proposed)** | interpose in the application's CAN socket calls with `LD_PRELOAD`, the same pattern as the three substitutions already in use, and deliver the real frames from the stand-in. **No kernel change.** |

The shim is now the cheapest route that keeps the vendor application and the vendor compositor intact:
it substitutes the *transport*, which is exactly the class of substitution this projection already
documents (backend, MICOM D-Bus, GL driver path).
