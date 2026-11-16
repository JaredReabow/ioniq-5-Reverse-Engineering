# Registration belongs to `ApplicationManager`, and no run has shown whether it is running

Date: 2026-11-06. Static analysis of the two binaries, done to avoid another boot spent guessing. **One red herring was caught and one
interface was found.**

## The red herring

`AppHomeScreen` contains the string `RegisterRequest` six times, which reads like the registration call and is not:

```
<interface name="com.lge.hkmc.avn.BluetoothHMI.interface">
  <method name="RegisterRequest">
    <arg direction="in" type="a(ii)" name="btrequestinfo"/>
```

**That is Bluetooth**, with a `btrequestinfo` argument. It would have cost a run to discover, and it is recorded here so nobody chases it
twice. (`docs/MEASUREMENT-DISCIPLINE.md` rule 14 in spirit: a string is not a call site.)

## The interfaces that actually matter

The launcher implements, and the application calls:

```
com.lge.avn.applauncher.request      launch / terminate / appkill        <- the launcher's command surface
com.lge.avn.applauncher.inform       launched                            <- the application announcing itself
com.lge.avn.appmanager.registration  launched / deregistration / launch / appkill
```

**`com.lge.avn.appmanager.registration` is the one that owns lifecycle state**, and the launcher holds a client for it
(`ComLgeAvnAppmanagerRegistrationInterface`, with `AppManagerInterface::requestAppDeregister`). The vendor's `ApplicationManager`
binary is present in the image (3,956,056 B) and carries the same interface strings.

## So the duplicate registration has a likely owner, and it is not our D-Bus stub

The previous hypothesis - a stand-in that never acks `RequestRegister` - was **built on the Bluetooth string**. The corrected shape:

- the application announces itself to **`ApplicationManager`**, not to the launcher;
- the launcher separately drives the same lifecycle through its own client;
- if **`ApplicationManager` is not running**, the application's announcement reaches nobody, the launcher's own load-timeout path
  registers the app, and the application's retry collides with it - producing `[REGISTERED]` then `[REGISTERED ERROR] Already
  registered`, 10 ms apart, from one pid.

That is consistent with everything measured, and it is **not yet measured**.

## What no run has answered, and the three checks that would

Boot50's log contains **no mention of `ApplicationManager`** - not its absence, just silence, which under rule 17 is
**NOT MEASURED**. The next run must answer, through `tools/uk_fw/guest/measure.sh` so that a blind instrument reports nothing:

```
measure.sh am_running   <pid of any live process> ls /proc/<appmanager-pid>        # is it running at all
measure.sh am_bus_owner 1  busctl --user status com.lge.avn.appmanager.registration  # who owns the name
measure.sh am_calls     1  dbus-monitor "interface=com.lge.avn.appmanager.registration"  # who calls what, in order
```

**And the decisive one, which is cheap:** if the name has **no owner**, the application's announcement cannot be delivered, and the fix is
to start the vendor's own `ApplicationManager` - not to write another stand-in. That would make this the **fifth** documented substitution
replaced by the vendor's real component, and the first one replaced *upward* rather than patched around.
