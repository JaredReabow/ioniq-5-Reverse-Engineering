# A third engineering-mode route: `SetEnginnerModeEntryCheck` on the MICOM engineering interface

Date: 2026-11-05. Found by sweeping every embedded D-Bus interface in `app/bin/` for write/execute-shaped methods,
rather than by following a hypothesis.

## What is there

`app/bin/AppSetup` - the application that owns the settings pages - calls, on the MICOM engineering interface:

```
interface  com.lge.car.micom.eng
  method     SetEnginnerModeEntryCheck()          no arguments, no return
```

The full engineering interface as `AppEngineerMode` sees it is eight methods, all `ay`-based:

```
SetMPModeInfoRequest (out ay, in ay)   AskMPModeInfo ()
SetSoundSrcScaleCtrl (in ay)           SetKeyPWMTest (out ay, in ay)
SetDisPlayRheostatValueCtrl (out ay, in ay)   SetDisPlayUserSettingValueCtrl (out ay, in ay)
AskEcallTirggerCount (out ay, in ay)   signal NotifyEngAirConditionKeyTest
```

**`SetEnginnerModeEntryCheck` is a bare "ask the MICOM whether engineering mode may be entered" call**, made by
the settings application. That makes it a **third route** into engineering mode, distinct from the two already
characterised:

| route | where it was measured |
|---|---|
| `com.lge.avn.appmanager.info.show_engineermode` | **accepted and inert** - measured twice, including with the home screen running |
| `NotifyKeyFrontSpecialEvent` with `[0x01,0x05]` | **delivered, handler declines on internal state** (V-060) |
| **`com.lge.car.micom.eng.SetEnginnerModeEntryCheck`** | **this entry - not yet exercised** |

## Why it matters twice

**For the security goal.** The MICOM engineering interface is on the **system bus**, and this method takes **no
arguments and returns nothing** - the simplest possible request to forge. Whether it *enters* engineering mode or
merely *asks the MICOM whether it may* is the decisive question, and it is answerable: if AppSetup's next step after
this call is a D-Bus request for app id 301, the method is a gate rather than an entry; if AppSetup opens the
engineering screen directly on the reply, then the MICOM's answer is the only control.

**Enforcement is MICOM-side either way**, which means on a real unit it may require vehicle state, and in this
projection it cannot be exercised at all.

**For the VM goal.** `com.lge.car.micom` in the projection is answered by this project's stand-in. **Correction:**
the stand-in *does* implement the engineering interface - `AskMPModeInfo` among others - so "nothing answers" was wrong.
What it did **not** implement is `SetEnginnerModeEntryCheck`, which is now one added row in its acknowledgement table
(`tools/uk_fw/guest/eng_data_sim.c`), rebuilt with no host paths.

**Measured afterwards:** the stand-in logs only what it *rejects*, and after the change no rejection for that method
appears - which is consistent with the fix and equally consistent with the application not calling it during that boot.
A positive test needs the simulator to log accepted calls too; that is the next change to it, not another hypothesis.

## Next, cheap and static first

1. Find what `AppSetup` does **after** `SetEnginnerModeEntryCheck` returns - a request for app 301 would make this a
   gate, anything else makes it an entry.
2. Check whether the stand-in answers `com.lge.car.micom.eng` at all (it does not, by inspection of the methods it
   registers), and add `SetEnginnerModeEntryCheck`/`AskMPModeInfo` so the settings path can proceed.

**Not claimed:** that this route enters engineering mode, or that it is a vulnerability. **Established:** the method
exists, is argument-free, is called by the settings application, and is unanswered in the projection.
