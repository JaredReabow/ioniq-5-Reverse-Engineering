# Battery / Range widget data path, and the injection point it actually needs

Date: 2026-11-05. Workspace: `work/vm/vehdata` (a CoW clone of `work/vm/gesture`; no other
workspace was touched). Runner: `tools/uk_fw/vm_partimg/run-vehdata.py` (a copy of
`run-gesture.py` with `WS` pointed at `work/vm/vehdata`). Rootfs: EU build
`NE.EUR.S5W_L.001.001.260128`, x86-64 Linux 4.1.27.

This document answers, in order: which QML renders the two widgets, which model properties the
text is bound to, what feeds those properties in `app/bin/AppHomeScreen`, and where the cheapest
faithful injection point actually is. **The headline correction:** the task's premise that the
data arrives as `com.lge.car.micom.can` CAN-transport frames (`NotifyCANTPRECVMsg`) is **not the
path the home-screen Battery/Range widgets use.** They are fed from the **raw CAN socket `can0`**
(`HomeCanThread` / `CQCANController_CANTxRx` / `QCANControllerListener`), which does not exist in
this projection because the vendor kernel has no CAN device driver (see §4). The D-Bus CAN
transport is a separate, parallel path. The negative Part B run that tested the D-Bus path is in
`02-partb-injection-attempt.md`.

---

## 1. The QML that renders the widgets (and the exact bindings)

The laid-out EV home screen (the 16,062-byte capture `docs/vm/38-…`) is the **eco3.0** GUI
variant (`E_GUI_VARIANT_ECO30` → `/app/share/AppHomeScreen/qml_eco3.0/`), *not* the
`qml_new2.0` tree the init script symlinks `qml -> qml_new2.0`. The widget that draws "Battery"
and "Range" side by side exists only in eco3.0.

**`app/share/AppHomeScreen/qml_eco3.0/component/QButtonBatteryHomeItemEco3.qml`**

- Battery value (the `---` placeholder):
  ```qml
  QText{
      id: value_battery
      text: typeof AppPHEVModel != 'undefined'
            ? (AppPHEVModel.display_Batlevel >= 0 ? AppPHEVModel.display_Batlevel : "---")
            : ""
      ...
  }
  ```
- Range value:
  ```qml
  property real rangeWidgetConvert:
      typeof AppPHEVModel != 'undefined'
      ? (((AppPHEVModel.unitWidget !== APPENUMS.E_UNIT_MILE)
          && (AppPHEVModel.unitWidget !== APPENUMS.E_UNIT_YARD))
         ? AppPHEVModel.display_DTE
         : (AppPHEVModel.display_DTE / (412.0/256.0)))
      : 0
  ...
  QText{
      id: range_value
      text: typeof AppPHEVModel != 'undefined'
            ? (((root.rangeWidgetConvert > 0)
                && !AppPHEVModel.dte_Calc
                && (AppPHEVModel.dteOffDisp !== 1))
               ? root.rangeWidgetConvert.toFixed(0) : "---")
            : ""
      ...
  }
  QText{
      id: range_unit
      text: typeof AppPHEVModel != 'undefined'
            ? (((AppPHEVModel.vcuReady === 1) && (root.rangeWidgetConvert > 0)
                && !AppPHEVModel.dte_Calc && (AppPHEVModel.dteOffDisp !== 1)) ? unit : "")
            : ""
  }
  ```

So the two displayed values are:

| widget | property | shows `---` when |
| --- | --- | --- |
| Battery % | `AppPHEVModel.display_Batlevel` | `display_Batlevel < 0` |
| Range km/mi | `AppPHEVModel.display_DTE` (via `rangeWidgetConvert`) | `display_DTE <= 0`, **or** `dte_Calc` true, **or** `dteOffDisp == 1`; unit only when `vcuReady == 1` |

`STR_EV_BATTERY` = "Battery", `STR_EV_RANGE` = "Range" (verified in
`localization/ts/translation_en-au.ts`).

**`app/share/AppHomeScreen/qml_eco3.0/HomeScreen/Screen_HomeScreen_Widget_Advanced.qml`**
instantiates it for the EV wide layout:

```qml
property bool _isWideScr: AppHomeModel.isWideScr
property bool _isEV: AppHomeModel.ecoType === AppHome_Enum.E_ECO_EV_TYPE
...
Component{
    id:comEV
    QButtonBatteryHomeItemEco3{
        id: idEV
        visible: _isEV && _isWideScr
        onReleased: AppHomeEngine.requestShowEVApp()
    }
}
Loader{
    id: evLoader
    anchors.left: parent.left; anchors.leftMargin: 520
    anchors.top: parent.top;  anchors.topMargin: 290
    sourceComponent: _isEV ? comEV : null
}
```

(`qml_new2.0/HomeScreen/Screen_HomeScreen_Widget_Advanced.qml` has **no** battery/range widget;
`qml_new2.0/HomeScreen/Screen_HomeScreen_Widget.qml` drives its widgets through the
`AppHomeModel.listWidget[*].sourceInput` plugin list instead.)

---

## 2. What feeds `display_Batlevel` and `display_DTE` in the binary

`app/bin/AppHomeScreen` is stripped, but the Qt metaobject string tables and the vendor's own
DLT format strings are intact. The model is `AppPHEVModel`.

### 2.1 The slots that receive the CAN signals

From the `AppPHEVModel` moc string table (byte offsets ~`0xc786e0`…`0xc78c40`):

```
1slot_xEV_SocDis(int)              2signal_xEV_SocDis(int)
1slot_CR_Bms_DisplaySoc(int)
1slot_VCU_DteBaseVal(int)          2signal_VCU_DteBaseVal(int)
1slot_VCU_DteAddVal(int)
1slot_CF_Clu_EVDTEDisp(int)
1slot_CLU_DTEVal(int)
1slot_MM_CR_Clu_TotalDTEDisp(int)
1slot_VCU_DteOffDispSta(int)
1slot_VCU_AvnDteOnCalcSta(int)     1slot_CF_Vcu_AvnDteCalc(int)
1slot_VCU_RdySta(int) / 1slot_VCU_EvDrvRdySta(int)   (the `vcuReady` gate)
```

The `1slot_`/`2signal_` pairs are the `QObject::connect` normalized signatures: a CAN parser
emits `signal_xEV_SocDis(int)` and `AppPHEVModel::slot_xEV_SocDis(int)` consumes it.

### 2.2 The connection is to the raw-CAN listener, not the micom D-Bus proxy

- `void AppPHEVModel::connectCanListenerSignals(QCANControllerListener*)` - the PHEV model binds
  its `slot_*` to a `QCANControllerListener`.
- `void QCANControllerListener::onCAN_data_received(const SQCanFrameList&)` /
  `onCAN_data_received2D/3DHigh/3DLow` - the listener consumes `SQCanFrameList` (raw CAN frames).
- `void QCANControllerListener::debugCANFrame(const SQCanFrame*)` - prints
  `"CAN ID: 0x2fc, Data length: 8, Data: 00 00 12 00 00 00 00 77 "` (the real-vehicle DLT line).
- `void CQCANController_CANTxRx::Initialize_raw_socket(int,int)` - `[QCAN] … RAW socket`
  creation/bind/ioctl; this is the PF_CAN socket.
- `QByteArray HomeCanThread::getCanDataByID(uint)` and `int HomeCanThread::open_port(const char*)`
  with the literal **`can0`** (`app/bin/AppHomeScreen` byte offset `0xc90076`, "No Open Port
  for CAN / Ioctl error ! / Bind error ! / can0").
- `unsigned int AppPHEVModel::getDataFromCanData(QByteArray, uint canID, uint startBit, uint size)`
  - signal extraction from a raw frame's bytes.

So the chain is:

```
raw PF_CAN socket "can0"
  -> CQCANController_CANTxRx::Initialize_raw_socket / read
  -> QCANControllerListener::onCAN_data_received(SQCanFrameList)
  -> signal_xEV_SocDis(int) / signal_VCU_DteBaseVal(int) / …
  -> AppPHEVModel::slot_xEV_SocDis / slot_VCU_DteBaseVal / …
  -> display_Batlevel, display_DTE, dte_Calc, dteOffDisp, vcuReady
  -> QButtonBatteryHomeItemEco3.qml
```

### 2.3 The SOC frame, pinned from the real-vehicle DLT

In `evidence/upstream/Ioniq5_Gen5W_Log_Dump/…/dlt_offlinetrace.0000084714.20241013_105501.dlt`
the ordered sequence is (byte offsets 551457 → 575498):

```
[QCANControllerListener::debugCANFrame] "CAN ID: 0x2fc, Data length: 8, Data: 00 00 12 00 00 00 00 77 "
[AppPHEVModel::setSharedValues] "send NotifyPhevValueChange DTE: 260 unitSpeed() 1 Battery level: 59.5"
[AppPHEVModel::slot_xEV_SocDis]   "batlevel: 59.5 , real_range: 12"
```

`0x77 = 119`, `119 × 0.5 = 59.5 %`. The SOC-display signal `xEV_SocDis` (log string
`"Can3L_xEV_SocDis signal is invalid value ="`) is therefore **CAN id `0x2fc`, byte 7, 0.5 %
per LSB**. (The second printed field `real_range` is a derived segment count -
`ceil(batlevel/5)` - not the range.)

The DTE value in the same snapshot is **260** (km, `unitSpeed()=1`), but its exact CAN id/byte
was not pinned in this session: the real-vehicle DLT shows only `slot_xEV_SocDis` among the
SOC/DTE slots firing, and `setSharedValues` reads DTE from state that is populated by the
VCU/CLU DTE slots on the same raw-CAN path. This is called out explicitly rather than guessed
(§5).

---

## 3. Why the D-Bus `com.lge.car.micom.can` transport is NOT the widget path

`com.lge.car.micom.can` on the **system** bus does exist and is active, and the app registers CAN
interest on it. Captured this session from the instrumented micom stand-in
(`/tmp/eng-data-sim.log`, run `1793856081227287000`):

```
SetCANMicomRecv     (11 B): 012f085000000000000000   and   012f08d3ffffffffffffff   (x54)
SetCANFixedMicomRecv(2 B) : 0196, 0197, 0173
AskCANMMCANMicomReq (2 B) : 0131 0132 0133 0134 0135 015e 019e 019f 01a0 012a 016d 055c 055e 056a 056e 055a
AskCANMMCANMicomReq (11 B): 018a…, 018b…
```

The 11-byte record is `[CAN id, 2 bytes big-endian][DLC, 1 byte][8 data bytes]`. But note that
**`0x2fc` (the SOC frame) is not among these registrations**, and the frames the
`QCANControllerListener::debugCANFrame` logs in the real vehicle (`0x2fc`, `0x1ab`, `0x1ac`,
`0x92`, `0x253`, `0x257`, `0x25c`, `0x397`) are the raw-socket frames, not the D-Bus-relayed
ids. The D-Bus micom CAN transport is exercised by a separate family of requesters -
`PHEVHandle::PHEVHandleAskCANMMCANMicomReq(uchar,uchar)`, `AppHomeModel::HOMEHandleAskCANMMCANMicomReq`,
`AppClimateModel::ClimateAskCANMMCANMicomReq(QByteArray)` - for multi-media-CAN (cluster) data,
while the home widget values come through `QCANControllerListener` off `can0`.

This is the measured basis for the correction in the header: **emitting
`NotifyCANTPRECVMsg` on the D-Bus does not reach `display_Batlevel` / `display_DTE`.**

---

## 4. The cheapest faithful injection point

**A CAN frame on the raw `can0` socket**, carrying at minimum `xEV_SocDis` (and the VCU/CLU DTE
signals for Range). Concretely the SOC frame to place on the wire is:

```
CAN id 0x2fc, DLC 8, data 00 00 12 00 00 00 00 77   (byte 7 = 119 -> 59.5 %)
```

In the projection this is **not currently injectable**, measured this session:

- `/sys/class/net` = `lo rmnet_usb0..7` - **no `can0`**.
- `modprobe vcan` → `FATAL: Module vcan not found.`
- `work/kbuild/vendor.config`: `CONFIG_CAN=y`, `CONFIG_CAN_RAW=y`, `CONFIG_CAN_BCM=y`,
  `CONFIG_CAN_GW=y`, `CONFIG_CAN_DEV=y`, but **every** CAN device driver is `# … is not set`
  (`CAN_VCAN`, `CAN_SLCAN`, `CAN_SJA1000`, `CAN_C_CAN`, `CAN_M_CAN`, `CAN_MCP251X`, …).
- The vendor's own `can0`/`can1` are created by the built-in `micom` driver
  (`micom_can_open` / `micom_ext_can_handle_event`) only after the MICOM link is alive; in QEMU
  the link is absent, so the driver never creates them (see `docs/vm/` `spi-gate.md`,
  `hmi-gap-analysis.md` §3.2).

Therefore the faithful injection is a **kernel change**, not a one-shot guest call:
rebuild the vendor kernel with `CONFIG_CAN_VCAN=m` (the path already proposed in
`evidence/vm-bringup/hmi-gap-analysis.md` §3.2), load `vcan.ko`, `ip link add can0 type vcan`,
then `cansend can0 2fc#0000120000000077` (or the matching 8-byte frame). At that point the
home-screen Battery widget should change from `---` to a number; Range additionally needs the
DTE-signal frame(s) and the `vcuReady`/`dte_Calc`/`dteOffDisp` gates driven.

---

## 5. Honest limitations

- **`display_DTE`'s exact CAN id/byte is not pinned.** The evidence pins SOC (`0x2fc` byte 7)
  and the DTE *value* (260 in that snapshot). The DTE slots (`slot_VCU_DteBaseVal`,
  `slot_VCU_DteAddVal`, `slot_CF_Clu_EVDTEDisp`, `slot_CLU_DTEVal`,
  `slot_MM_CR_Clu_TotalDTEDisp`) are all `1slot_` members of `AppPHEVModel` bound through
  `connectCanListenerSignals(QCANControllerListener*)`, i.e. the same raw-CAN listener as SOC,
  so DTE is on the raw-CAN path; but the specific frame id and byte layout were not recovered
  this session, and I did not fabricate them.
- **The D-Bus frame format for `NotifyCANTPRECVMsg` is not the widget path** (§3), so even a
  perfectly-formed `ay` frame would not fix the widgets. The negative run in
  `02-partb-injection-attempt.md` tests that claim empirically.
- The eco3.0-vs-new2.0 selection is inferred from the rendered widget (only eco3.0 has the
  Battery+Range `QButtonBatteryHomeItemEco3`), not from a captured
  `GUI_VARIANT LOAD SUCCESSFULLY: …` DLT line (DLT goes to a file, not the console).

## Provenance

Static: `work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/share/AppHomeScreen/qml_eco3.0/…`
and `…/app/bin/AppHomeScreen` (stripped ELF; Qt moc string tables, log-format strings, and the
`can0`/`QCANControllerListener`/`HomeCanThread` symbols were recovered with `strings`).
Real-vehicle: `evidence/upstream/Ioniq5_Gen5W_Log_Dump/…/dlt_offlinetrace.0000084714.20241013_105501.dlt`.
Projection: `work/vm/vehdata/runs/1793856081227287000/serial.log` (CAN registrations) and
`1793857420103938000/serial.log` (network/CAN state + injection attempt).
