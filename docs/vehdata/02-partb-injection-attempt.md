# Part B - D-Bus `NotifyCANTPRECVMsg` injection attempt (negative)

Date: 2026-11-05. Workspace: `work/vm/vehdata`. Runner: `run-vehdata.py --init
/init-authentic-hmi.sh --smp 4`. Run: `work/vm/vehdata/runs/1793857420103938000`.

Part A (`01-battery-range-data-path.md`) concluded that the home-screen Battery/Range widgets are
fed from the **raw `can0` socket**, not the D-Bus `com.lge.car.micom.can` transport. This run
tests the D-Bus premise anyway: it emits `NotifyCANTPRECVMsg` with a synthesised CAN frame and
checks whether the placeholder dashes change.

## What was attempted

After `set_power_on_status` laid out the home screen, the guest emitted these system-bus signals
(`dbus-send --system --type=signal /Can com.lge.car.micom.can.NotifyCANTPRECVMsg <ay>`):

```
# SOC frame: CAN id 0x2fc, DLC 8, data 00 00 12 00 00 00 00 77  (byte 7 = 119 -> 59.5 %)
array:byte:0x02,0xfc,0x08,0x00,0x00,0x12,0x00,0x00,0x00,0x00,0x77
# DTE/other candidates on ids the app itself requested via AskCANMMCANMicomReq
array:byte:0x01,0x9e,0x08,0x04,0x01,0x00,0x00,0x00,0x00,0x00,0x00
array:byte:0x01,0x9f,0x08,0x04,0x01,0x00,0x00,0x00,0x00,0x00,0x00
array:byte:0x01,0xa0,0x08,0x04,0x01,0x00,0x00,0x00,0x00,0x00,0x00
array:byte:0x01,0x2f,0x08,0x50,0x00,0x00,0x00,0x00,0x00,0x00,0x00
```

Each `dbus-send` produced an empty reply (signals return nothing), logged as `EMIT_CAN_* []`.
After ~15 s the home surface (ivi id 1004) was placed and captured with
`/usr/libexec/weston-screenshooter`.

## Result - nothing changed

- Capture `docs/vm/39-vehdata-after-notifycantprecvmsg-injection-2026-11-05.png`:
  **131,845 bytes**, mean RGB ≈ (7.0, 10.8, 14.7) - a **dark** frame. OCR still shows the
  placeholder dashes and no numeric Battery/Range values.
- The pre-injection surface-1004 capture is byte-identical content at the same size
  (`39b-…`, 131,845 bytes, same MD5 `7fd0891d2da1a635a8b025a0cb363c0e`): the injection changed
  nothing.
- `set_power_on_status` did return `method return` this run, but note the layout landed on the
  **dark** variant (131,845 bytes) rather than the light 16,062-byte layout of the earlier
  session - a theme/timing variance, so this run's screen is not a clean re-plot of the 16,062
  capture. The absence of any change across injection is still the measured result.

## Why the dashes did not move

The host-side state check in the same run shows the real reason:

```
NETDEV=[lo rmnet_usb0 rmnet_usb1 … rmnet_usb7]   # no can0
MODPROBE_VCAN=[modprobe: FATAL: Module vcan not found.]
```

There is **no `can0`** and no loadable CAN device driver in this kernel. The widget path reads the
raw socket (`HomeCanThread`/`QCANControllerListener`), so a D-Bus signal on
`com.lge.car.micom.can` - even a well-formed `ay` CAN frame - has no route to
`AppPHEVModel::display_Batlevel` / `display_DTE`.

## Conclusion

**Negative, as predicted by Part A.** The exact call attempted is

```
dbus-send --system --type=signal /Can \
  com.lge.car.micom.can.NotifyCANTPRECVMsg \
  array:byte:0x02,0xfc,0x08,0x00,0x00,0x12,0x00,0x00,0x00,0x00,0x77
```

and it does not replace the placeholder dashes. The faithful injection is a CAN frame on `can0`,
which requires rebuilding the vendor kernel with `CONFIG_CAN_VCAN=m` (see
`01-battery-range-data-path.md` §4) - not a one-shot guest call.
