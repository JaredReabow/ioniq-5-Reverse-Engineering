# What the projection shows when none of our instruments interfere

Date: 2026-11-05. No `LD_PRELOAD`, no `ivi-wm`, no `ivi_place`. Only the power-on call and captures.

## The run

```
Z1_APPUP=0s   pid=[2416]
Z1_a_pre=129,844   pid=2416      before the power-on call
power on
Z1_b_30=130,457    pid=2605       one restart, then settled
Z1_c_75=130,457    pid=2605
Z1_d_135=130,457   pid=2605
Z1_ERRS=3          pid_end=[2605]
```

**One restart, then the application held pid 2605 for 105 seconds.** So with the instruments removed the
application is stable; both earlier crash sources were ours.

## What is on screen

`docs/vm/44-stable-app-kia-splash-no-instruments-2026-11-05.png` (130,457 bytes, 1920x720): **the KIA logo
on black, with a thin blue bar along the bottom.** No title bar, no left panel, no widgets.

That is **neither** the standby face this project has been capturing (title bar reading `STR_CAMERA_ALERT2`,
left panel, logo) **nor** the laid-out home screen (Battery and Range widgets). It is the application's own
**splash/startup frame**, and it is what the application shows, stably, with nothing of ours touching it.

## What that means

- The three frames this project has been confusing are now distinguishable: **splash** (130,457, logo, no
  chrome), **standby** (114,782-120,562, title bar + left panel + logo), **layout** (16,062 seen once,
  widgets placed).
- The application **does not leave the splash** in this projection. It is not crashing - it is waiting.
- Since the log records `AppHome Init Done` and then widget-level chatter (`setDayNightSuffix "#GUI_DAY"`,
  `AW_AUTO_LIGHT_STATUS_CHANGED`, `SaveSetupLayoutDB ... DB UPDATE COMMIT FAIL`), the next read has to be
  **what it is waiting for**, from its own log, with no crash in the way.

## Note on `DB UPDATE COMMIT FAIL`

The log contains **`DB UPDATE COMMIT FAIL`** repeatedly while saving the setup layout. That is the application
failing to persist its own layout database, which is plausibly why a freshly started instance never restores
a layout. It is the first concrete candidate for "why the splash never turns into a home screen", and it is in
this project's own capture - not something to be hypothesised about.

## The methodological finding, stated plainly

**Two of this project's instruments independently killed the application under test** - the process-wide
`ld.so.preload` and the `ivi-wm` placement tool. Between them they produced: a restart loop misread as a power
state problem, three runs of hypotheses about "standby", and a frame misattributed to `AppCamera`. Any future
work on this projection should start with **no instruments**, establish the stable state, and add one
instrument at a time.
