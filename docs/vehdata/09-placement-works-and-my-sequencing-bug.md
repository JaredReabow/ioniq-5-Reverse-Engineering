# Placement works; the app was in standby because my power-on call came too early

Date: 2026-11-05. Shipped compositor configuration (no `hmi-controller`), three captures in one run.

## What the run showed

```
K1_BEFORE   home=[2623] cam=[2632] setup=[3109] weston=[797]      capture 129,844
            ivi-wm 2080
K1_placed                                                          capture 114,782
K1_AFTERKILL home=[2623] cam=[3277] setup=[3300]                   capture 129,844
```

**`ivi-wm 2080` changed the composited output** - 129,844 to 114,782 - so **placement through
`ivi_window_manager` works**, and the whole `hmi-controller` line of investigation was unnecessary.

The 114,782-byte frame (`docs/vm/43-surface-2080-placed-standby-face-2026-11-05.png`) shows a title bar
reading `STR_CAMERA_ALERT2`, a left panel, and the KIA logo on black: **the application's standby face**,
which is the same face this project documented at 120,561 bytes days ago. So it is 2080, it is the
application, and it is **not powered on**.

**Killing `AppCamera` and `AppSetup` did not help and cannot help:** both were back within eight seconds
(2632 -> 3277, 3109 -> 3300). The application manager supervises them; they are not strays to be cleared.

## The probable cause, and it is mine

The probe script issues `set_power_on_status` at the **top**, immediately after the `TimeManager` drop-in
fires - but `AppHomeScreen` had not necessarily registered its bus name at that moment. The manager accepts
the call either way, and the state event goes to nobody. Every earlier attempt in this series had the same
shape: the call lands at a fixed second, not at a state.

**The correction is sequencing, not a new hypothesis:** poll for `AppHomeScreen` owning its name, *then*
call `set_power_on_status`, *then* wait for the frame to settle (~90 s measured), *then* place 2080, *then*
capture.

## What is established now

- **placement works** via `ivi-wm` on the shipped configuration (measured, two different outputs)
- **the projection can present the application's own surface** - it is showing the standby face because the
  application believes the vehicle is off
- **`hmi-controller` is not needed** and cannot be loaded here anyway
- the remaining obstacle is **sequencing of the power-on call**, which is a defect in this project's probe
  scripts, not in the vendor's software

## Not established

That the laid-out home screen appears with the corrected sequencing. It should - the same call is what
produced `docs/vm/38-gesture-home-layout-after-set-power-on-2026-11-05.png` in a run where it was issued
after the name was owned - but that has to be measured, not assumed.
