# `show_engineermode` is accepted and does nothing (measured twice)

Date: 2026-11-05. Method: the authentic projection, `--smp 4`, a `TimeManager.service` drop-in
issuing the calls to `com.lge.hyundai.avn.appmanager` on the session bus, logging to `ttyS2`.

## The calls and the results

**Run 1** (probe at 105 s):

```
ask_power_status   -> int32 1
show_engineermode  -> method return sender=:1.7 -> dest=:1.31 reply_serial=2
AppEngineerMode    -> no pid appeared in the following 80 s
```

At that point `AppHomeScreen` had **not** yet started (`home=` empty), so the run was inconclusive.

**Run 2** (probe at 120 s, with the app running):

```
EM_START       home=            mgr=2203        the manager is up; the app is not yet
EM_POWERON     method return                     set_power_on_status(1,0) accepted
EM_AFTER_POWER home=2494                         18 s later the home screen is running
EM_CALL        method return                     show_engineermode accepted
EM_ENG_PID=    waited=84s                        no AppEngineerMode process in 84 seconds
```

## What this establishes

**`show_engineermode` is implemented and accepted at the interface level, and does not start the
engineering application** - measured with the home screen running, which was the caveat attached to
run 1. Two independent attempts, same result.

So the D-Bus entry that looked like the technician's route (E1 in `hidden-menus.md`) is **inert as
called**. Three readings remain open, and they are distinguishable:

1. It needs arguments (the method was called with none; the interface block shows no `<arg>` entries,
   but the manager may still read a payload).
2. Its handler is gated on build state - consistent with everything else about engineering mode on this
   build, where the production QML list omits Force Update entirely.
3. It sets a state that a *later* event consumes, rather than launching directly.

## The next route, and why it is better

`hidden-menus.md` E2b: `micommanager_userspace` exposes **test methods** for the front-panel special
key (`TestNotifyKeyFrontSpecialEvent`, and neighbours). E2 is the front-panel special key that a
technician can press; E2b means **any session-bus client can forge it**. That is:
- a signal the manager is known to act on (`HWKeyInterface::SpecialKey`), rather than a method whose
  handler behaviour is unknown;
- reachable without a physical key, so it can be exercised in the projection.

That is the next experiment, and it is the one this project should have tried before the D-Bus method.

## Caveat on the capture

`EM_SHOT=129844` - the known **early background** size, captured because `weston-screenshooter`
composited whatever was newest. So the capture carries no information about the application; the
negative above rests on the process check and the two method returns, not on that image.
