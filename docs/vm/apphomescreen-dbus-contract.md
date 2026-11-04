# The application/manager D-Bus contract, as recovered

This document exists because the link checker recorded `docs/vm/apphomescreen-dbus-contract.md` as **promised and never written**. It collects what has actually been recovered about
how the vendor applications talk to `ApplicationManager`, from the binaries and from the session-bus traffic. Every statement below points at the evidence that produced it; nothing
here was inferred from how similar systems usually work.

Why it matters: **two different applications failed to paint for the same reason**, and it is a violation or absence of this contract. See `engineering-paint.md` and `authentic-hmi-apps.md`.

---

## 1. Application → manager: registration

Observed on the session bus when any vendor app starts (`authentic-hmi-apps.md`, `engineering-paint.md`):

```
method call sender=:1.47 -> dest=com.lge.hyundai.avn.appmanager
  path=/registration  interface=com.lge.avn.appmanager.registration  member=registration
    int32 301                                            appid
    string "AppEngineerMode"                             appname
    string "com.lge.hkmc.avn.appfunc.AppEngineerMode"    servicename
    string "/com/lge/hkmc/avn/appfunc/engineermode"      objectpath
    int32 1                                              plane
```

Two facts worth keeping:

- **The destination is `com.lge.hyundai.avn.appmanager`** — and in the projection **nothing owns that name**, so the call returns no reply and the app is never known to a manager.
  This is the first half of why the HMI does not come up: see `authentic-hmi-apps.md` §1 for the stand-in that starts the launcher anyway.
- **The app registers the `objectpath` it expects to be *called on*.** That path is where a manager is supposed to talk back.

## 2. Manager → application: the show/hide interface

The **application** exports this adaptor (it is the server), recovered from its Qt D-Bus XML (`engineering-paint.md`):

```xml
<interface name="com.lge.avn.appmanager.appbase">
  <method name="show_window_fg">
    <arg direction="in" type="i" name="reason"/>
    <arg direction="in" type="i" name="plane"/>
    <arg direction="in" type="i" name="avmode"/>
    <arg direction="in" type="i" name="command"/>
    <arg direction="out" type="i" name="response_plan"/>
  </method>
  <method name="hide_window_bg"> … </method>
</interface>
```

An application that is never sent `show_window_fg` **never attaches a buffer**. That is measured, not assumed: the engineering app's entire Wayland traffic over 70 s is `624` bytes
of object-id teardown, with no `create_surface`, no `attach`, no `commit` (`engineering-paint.md` §"What the app does with its buffer: nothing"). The home screen behaves identically
on the authentic path (`authentic-hmi-apps.md` §4).

**The manager does not register this interface in the projection**, so there is no D-Bus route to trigger a show, and attempts to deliver the call by hand fail: `NoReply` at the app's
registered path, and at `/com/lge/hkmc/avn/appfunc/appInterface` the app's connection disappears afterwards (`engineering-paint.md`, attempt log).

## 3. Application liveness: the watchdog that reaps unshown apps

A launched application that is never shown is eventually **terminated by the manager**, with a log line naming it (`appmanager-micom-replies.md` §"The named blocker"):

```
AB010512*time*AppEngineerMode-5-hang
appTerminateSlot
a_nSigNum[15]
```

The handshake that prevents this is `set_application_alive_chcek` / `askAlive` (the names appear in the manager's strings; the misspelling is the vendor's). One consequence already
recorded in the register: **V-045's "the call kills the app" claim now has a competing explanation** - the app may simply be reaped for never answering this handshake, with the
`show_window_fg` call blameless.

## 4. Manager ↔ MICOM: what the manager itself asks for

Recovered from the stand-in's own `UNKNOWN` log, with reply types taken from the requesting binaries' introspection (`appmanager-micom-replies.md`):

| method | bus | path | interface | reply |
| --- | --- | --- | --- | --- |
| `AskSysUpmID` | system | `/Ihu` | `com.lge.car.micom.ihu` | `ay` |
| `AskEtcAdmSettingValue` | system | `/Ihu` | `com.lge.car.micom.ihu` | `ay` |
| `AskDebuggingMode` | system | `/Ihu` | `com.lge.car.micom.ihu` | `ay` |
| `AskCameraSetting` | system | `/Ihu` | `com.lge.car.micom.ihu` | `ay` in, `ay` out |
| `AskCameraBrightness` | system | `/Ihu` | `com.lge.car.micom.ihu` | `ay` |
| `AskEtcLcdThemaInfo` | system | `/Ihu` | `com.lge.car.micom.ihu` | `ay` in, `ay` out |
| `SetFCEVInitialRequest` | system | `/Can` | `com.lge.car.micom.can` | void |
| `AmebaEnable` | session | `/com/lge/hkmc/avn/AppVR` | `com.lge.avn.appvh.AmebaEnable` | `b` |

Answering the two that the manager's log named as `reply is not VALID` took the count to **zero**, so this part of the contract is satisfied in the projection.

## 5. Application → data services (engineering mode only)

Six asynchronous asks, answered by the same stand-in (`engineering-data-services.md`): `AskSysVersion`, `AskAutotestWIPID`, `AskTraceDate`, `AskPartNumberInfo`, `AskFactoryModeInfo`
on the MICOM services, and `AtVersionVrReq` on `com.lge.avn.appvh.atversionvrreq`. Answering them removed every `Pending Err` and **did not** fix the paint - which is what moved the
investigation to §2 above.

## 6. What is still missing from the contract

- **Where the manager is supposed to register `com.lge.avn.appmanager.appbase`**, and under what precondition. Its absence is the single blocker for a painted window; a worker is
  checking whether registration is gated on a service we are not providing (a follow-up to `authentic-hmi-apps.md`).
- **`org.freedesktop.DBus.Properties.GetAll`** on the stand-in currently returns `UNKNOWN_METHOD` instead of an empty property dictionary. Wrong, though not blocking.
- **`askMicomBigInfoFaultCode`**, one more MICOM ask the home screen makes, still unanswered.

## Provenance

Every claim above is from a captured log or a binary's own XML, each cited to the document that captured it. Nothing here has been tested on a vehicle; the whole contract was recovered
from one image and its behaviour in a projection.
