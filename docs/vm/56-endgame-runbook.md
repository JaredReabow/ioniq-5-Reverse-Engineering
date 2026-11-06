# The endgame runbook: two gates, both decisions rather than discoveries

Date: 2026-11-06. Registration and the label are closed (`docs/kernel/34`). Astra and Opus 4.7 were given that milestone independently and
**converged on the same next fault** - and Astra supplied a contract this project had not written down.

## Gate 2: prove the power-on was CONSUMED

**Astra found the receiving contract in the binaries**, which is the missing piece:

```
destination  com.lge.hyundai.avn.appmanager
path         /Information
interface    com.lge.avn.appmanager.info
method       set_power_on_status(int on, int position)
signal       power_status(int status)          <- the observable
```

**The observable is the `power_status` signal, not the method's return.** A method that returns is a message that was delivered; a signal
that follows is a state machine that moved. So the check is:

```
dbus-monitor "interface=com.lge.avn.appmanager.info"    # started BEFORE the call
dbus-send --session --dest=com.lge.hyundai.avn.appmanager /Information \
    com.lge.avn.appmanager.info.set_power_on_status int32:1 int32:0
```

**Consumed** = `power_status` appears with a plausible status. **Merely sent** = the method returns and no signal follows. Those two have been
indistinguishable in every previous run because only the method was sent.

## Gate 5: a machine predicate for "this is the home screen"

**Opus 4.7 ranks the capture as the most likely thing to be wrong next** - unreconciled `1010` versus `APP_SURFACE_ID=[1005]` - and notes that
every previous "home frame" in this project turned out to be standby chrome, and once `AppCamera` on the colliding `2080`.

**Astra's predicate, adopted**, because a PNG size has already been mistaken for progress twice:

```
HOME_FRAME = identity && home_tree && geometry && presentation && persistence
```

| term | what it means | how it is checked |
|---|---|---|
| **identity** | the surface belongs to **app 11's pid**, matched to the launcher's record | pid + start time, not "newest surface" |
| **home_tree** | the live Home layout subtree exists, not just its construction messages | the QML object tree, exported |
| **geometry** | the intended surface geometry at 1920x720 | surface dimensions and crop/scale, not the PNG's size |
| **presentation** | a **new** buffer was presented after power-on | compositor frame accounting |
| **persistence** | it is still there 10 s later | a second capture, same identity |

**`identity` is the term this project has failed twice.** Capture by identity, never by recency - a rule already in the runbook for a different
reason, now with a second reason.

## What settles the surface-id question in one run

Not an argument - a listing. After the warm launch, in one run:

1. the launcher's record for app 11 (pid, surface id requested);
2. the compositor's client list with **pid → wl_surface → ivi_surface id**;
3. a capture **taken by the pid from (2)**, not by newest-id and not by size.

**If the compositor's id for app 11's pid is 1005, then 1010 was a request that the shell re-mapped, the mapping is benign, and the capture must
follow the pid.** If app 11's pid has **no** compositor surface, the app is drawing somewhere nothing reads - which is a different fault and
would explain standby-only frames without any new mechanism.

## The ordering that matters

**Gate 2 before gate 5.** If the power-on was never consumed, a laid-out frame cannot exist, and any frame that looks like a layout is a
mislabelled standby screen - which is exactly how `AppCamera`'s chrome was recorded as the home screen once already.

**And one pre-commitment, because Opus asked for one:** the run that closes this must state, *before it starts*, which of the two gates it is
testing and what a null looks like. Three false negatives in one hour came from runs whose null was not defined in advance.
