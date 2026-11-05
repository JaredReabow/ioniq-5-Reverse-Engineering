# A MICOM-coupled hash and key-check exists in the launcher (defence, enforcement unproven)

Date: 2026-11-05. Found while asking why a replaced application binary refuses to run.

## What is there

`app/bin/AppLauncher` contains a cipher subsystem wired to MICOM events:

```
interface  com.lge.avn.applauncher.cipher
  method     getIVDHash() -> ay hash_data            a system hash, exposed over D-Bus
object     /com/lge/avn/applauncher/cipher

classes    HashCipherInterface, AskCipherInterface, CipherAdaptor, OsslCipherUtils, AskCipherThread
strings    AskCipherThread::SystemIVD=
           AskCipherInterface::onNotifySystemHashDataEvent
           AskCipherInterface::onNotifyAdvancedSecurityKeyEvent KeyCheck
           AskCipherInterface::onNotifyAdvancedSecurityKeyEvent Seed
           onMicomSelfEmergencyGO(QByteArray)
```

**This is a challenge/response design**: a `Seed` and a `KeyCheck` delivered as MICOM events, an OpenSSL-backed
cipher utility, and a system hash (`SystemIVD`) that the launcher can hand out.

## Why it matters in both directions

**As a defence.** If `SystemIVD` is a hash over the application payload and the launcher refuses to start a
binary whose hash does not match, then tampering with `AppHomeScreen` - which this project now has direct
experience with - would be **detected and blocked**. That is a real anti-tamper control, and it is the first one
this project has found in the shipped image.

**As a nuance to V-051.** V-051 records that the application manager **executes any caller-named path as root**.
That is still measured. What this mechanism shows is that somewhere in the same component there is also an
**integrity identity** (`SystemIVD`) and a MICOM challenge - so the platform has the parts for verification even
where the launch path does not use them. The two facts sit side by side rather than contradicting each other.

**As a (small) exposure.** `getIVDHash` is a D-Bus method any process on the session bus can call. That bus is
root-only (measured for V-051), so the reach is limited to processes already running as root - which is most of
the application stack on this unit. It discloses a system hash, not content.

## What is *not* established, and how to test it

**That this mechanism is enforced at all.** The observation that started this - a shell wrapper in place of
`AppHomeScreen` produced **no process and no log** - is *consistent* with a hash check, and equally consistent
with an `exec` that requires an ELF, or a path table that was never consulted. The evidence does not separate
those.

Three cheap tests would:

1. **Replace a *different* application's binary** with a wrapper and see whether it also fails to start. If only
   some applications are protected, that implicates a per-app manifest; if all fail identically, an `exec`
   requirement is more likely.
2. **Call `getIVDHash` on a running unit** and see whether it answers, and whether the value changes when a
   binary changes. That tests the mechanism directly without touching the vendor's launch logic.
3. **Read `onNotifySystemHashDataEvent`'s reaction** in the launcher's own log on a real unit, where MICOM is
   present - this projection has no MICOM link, so the event never arrives here and the enforcement path may
   simply be **inert under emulation**. That possibility is important: it would mean the control exists but is
   untested by everything this project can run.

## Verdict

**A defence-shaped mechanism, unproven in effect, and inert in the projection because the MICOM events it depends
on never arrive.** Recorded so nobody concludes from the wrapper experiment that the launcher verifies binaries -
and so that the next person knows where to look if they want to prove it does.

---

## 4. Test 1, run against a different application: it fails the same way

Replaced `/app/bin/AppSetup` with a wrapper that simply `exec`s the real binary - **copying to `.real` first and
verifying the ELF magic before replacing the original**, per rule 15 - and let the projection start normally.

```
T1_SETUP_PID=[]     AppSetup is not running
T1_HOME=[3200]      AppHomeScreen, whose binary is the vendor's own, is running
```

**A second, different application also refuses to start when its binary is a shell script.** So the behaviour is
**general**, not a per-application manifest - which moves the explanation toward an **`exec` or format
requirement** in the launch path rather than toward per-app integrity verification.

Both clones are restored: `/app/bin/AppSetup` and `/app/bin/AppHomeScreen` are the vendor binaries again, with no
`.real` copies left behind.

**This weakens the integrity hypothesis rather than killing it.** A launcher could still verify every binary and
refuse all wrappers; the observation cannot distinguish "refuses non-ELF" from "refuses anything whose hash does
not match". What it does show is that the *specific* case of `AppHomeScreen` was not special, and that the earlier
suspicion of a targeted check was unnecessary.

## 5. A probe bug in the same run, recorded rather than dropped

`getIVDHash` was never actually called:

```
Failed to open connection to "session" message bus: ...
```

**I forgot to export `DBUS_SESSION_BUS_ADDRESS` in this probe**, so the one direct test of the mechanism did not
happen. The mechanism is still untested; the test itself remains valid and cheap, and needs the same environment
every other D-Bus probe in this project uses.

**What is established:** wrapping a second application fails identically. **Not established:** whether the
launcher verifies binaries, and whether `getIVDHash` works in the projection at all.

---

## 6. The mechanism answers, and the answer is a SHA-256 over the application set

Retested properly, with the session bus address set:

```
I1_OWNS=[boolean true]                              com.lge.avn.applauncher is on the session bus
I1_INTROSPECT=... <interface name="com.lge.avn.applauncher.cipher"> ...
I1_GETIVDHASH= method return
               array of bytes [
                 d4 d8 03 8c eb 1d 4a 77 20 93 f2 0b 47 58 72 3a
                 ff 8c e3 20 93 8c 53 a9 55 a4 e9 e0 71 6c df 98 ]
```

**32 bytes - a SHA-256 digest - returned by the projection itself.** This corrects the hedge in §3: the mechanism is
**not inert here**; the hash side works without any MICOM.

What it covers is named in the binary's own strings:

```
/app/bin/AppHomeScreen   /app/bin/AppClimate   /app/bin/AppCamera   /app/bin/AppMediaPlayer  ...
/app/bin/AppLauncher     (a list of application binaries)
SHA256_Init / SHA256_Update / SHA256_Final
AskCipherThread::SystemIVD=
```

**The launcher enumerates the application binaries and hashes them with SHA-256.** The returned digest is therefore
a **fingerprint of the installed application set** - an integrity identity, exactly the shape of a tamper check.

## 7. But the comparison is not in the launcher - it is in MICOM

There is **no reference manifest** anywhere in the extracted image (no `*ivd*`, `*.hash`, `*manifest*`,
`*integrity*` file) and the launcher names **no file** to compare against. What it does have is the MICOM event
handlers:

```
AskCipherInterface::onNotifySystemHashDataEvent      MICOM -> launcher, carries hash data
AskCipherInterface::onNotifyAdvancedSecurityKeyEvent KeyCheck / Seed
```

**So the launcher computes and offers the digest; the comparison happens in MICOM firmware.** That is a coherent
design and it has a direct consequence for this project:

- **In the projection, the integrity check cannot be enforced**, because there is no MICOM to hold the reference
  and no MICOM link to deliver `NotifySystemHashDataEvent`. The hash is computable and the check is unenforceable.
- **The wrapper refusal is therefore not explained by integrity.** Two different applications refused to run as
  shell scripts, no reference exists locally, and the comparison path is absent. An `exec`/ELF requirement in the
  launch path remains the simpler explanation - which is what §4 already leaned toward.

## 8. What this means for the patch list

**A real anti-tamper design exists and is the right shape**: hash the application set, compare with a reference held
where the attacker cannot write, on a device with a trusted element. Two things bound its value as shipped:

1. **The reference lives in MICOM firmware**, so its strength depends on firmware the platform vendor controls -
   and this project cannot test it (no MICOM in the projection).
2. **`getIVDHash` is exposed on the session bus to any process on it.** That bus is root-only (V-051), so it
   discloses a fingerprint to processes already running as root - which on this unit is most of the application
   stack. It is not a content leak, but it is an oracle for "did the application set change", useful to an
   attacker with root who wants to know whether their tampering was noticed.

**Recommendation for the patch list:** treat the MICOM reference as a real control and test it on hardware
(change one byte in one application binary, observe whether the unit refuses to start it); and consider whether
`getIVDHash` needs to be callable by every session-bus client.
