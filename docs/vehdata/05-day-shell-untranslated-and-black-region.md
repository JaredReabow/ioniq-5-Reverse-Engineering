# The settled frame at +90 s: untranslated string, black right region

Date: 2026-11-05. Shim preloaded, `set_power_on_status` issued, captures at +30, +90 and +150 s.

## Timing first, because it invalidates earlier readings

| when | surface 1004 | surface 2080 |
|---|---|---|
| +30 s | 129,844 | 129,844 |
| **+90 s** | **22,057** | **22,057** |
| +150 s | 22,057 | 22,057 |

**The frame is not settled at +30 s.** Everything captured earlier in that window - including my own
"light frame with a placeholder glyph" at 7,510 bytes - was a **mid-transition state**, not a result. The
application needs roughly **90 seconds** after the power-on call before its frame stops changing.

## What the settled frame actually shows

`docs/vm/42-day-shell-untranslated-string-black-region-2026-11-05.png` (22,057 bytes, 1920x720):

- the **day theme**, so `set_power_on_status` took effect
- a title bar containing the literal text **`STR_CAMERA_ALERT2`**
- a light left panel
- a **black region covering the right third** of the screen

## Why the literal string matters more than the black region

`STR_CAMERA_ALERT2` is a **translation key rendered as text**. The application is being handed its own
key back instead of a translated string, which means **the translations model is not resolving**. The QML
for these widgets reads `TranslationsModel.STR_EV_BATTERY + AppHomeModel.textUpdate`, so a model that
returns keys is a model that is not populated.

The black region has the same shape of cause: earlier work found the menu bar **renders black because
theme image assets are not loaded**. Missing images draw black; missing translations draw keys.

**So the visible defect is not the CAN data and not the layout.** It is that the application is running
without its **resource/translation model** - the same class of gap as the six services answered earlier,
but a different one: a data/model load, not a D-Bus method.

## What that changes about the plan

The widget *values* still need CAN. But before values can appear, the widgets need **text and images**,
and they are currently getting keys and black. That is the nearer and more cheaply testable gap:

1. Find where the application loads its translations and theme assets (a `.qm` file, a data partition
   path, or a model service) and whether that load reports an error.
2. Compare against the vehicle's own logs, where the same screen shows translated text - so the load
   succeeds on a real unit and something in the projection prevents it.

**Not established:** which load fails. **Established:** the settled frame carries untranslated keys and a
black region, and both are the signature of an unloaded resource model rather than of missing CAN data.

---

## 7. Correction: that frame is `AppCamera`, not the home screen

**I attributed the 22,057-byte frame to the home screen. It is almost certainly `AppCamera`.**

The string in its title bar, `STR_CAMERA_ALERT2`, does **not** exist anywhere in the home screen's
translations. A full-image search for that key finds it in exactly one application:

```
app/share/AppCamera/system/StringInfo.qml
app/share/AppCamera/localization/AppCamera_en_GB.qm   (+ 50 more locale files)
```

**54 files, all under `AppCamera`.** Meanwhile `STR_EV_BATTERY` and `STR_EV_RANGE` - the strings the home
screen's widgets use - are present in **all 26** of the home screen's own `.qm` files. So the home screen
had its translations available, and the frame I looked at was displaying a string that belongs to a
different application.

The **black region fits the same conclusion**: `AppCamera` with no camera attached draws an unpainted
preview area. It was never the home screen's missing theme images.

**What this means for the previous section:** the "unloaded resource model" reading was **too broad**. The
evidence supports a narrower and different statement - *the topmost window in that run was the camera
application, and its title string is untranslated* - and says nothing about the home screen's translations,
which demonstrably exist.

**Why the captures could not tell me this:** every surface id returned the **same byte size (22,057)**,
which means `weston-screenshooter` was compositing the same output regardless of which surface was placed
in front. So the surface ids did not identify anything in that run, and surface **identity has to come from
the compositor log**, not from the id I asked to be placed.

**The next measurement, and it is cheap:** pull `/tmp/weston-real.log` off the guest through the base64
channel and read which client owned which surface at each capture. Until that is done, no capture in this
series can be attributed with confidence.
