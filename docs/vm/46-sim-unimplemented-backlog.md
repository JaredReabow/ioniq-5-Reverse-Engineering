# The stand-in's unimplemented-method backlog, measured from a live boot

Date: 2026-11-05. The data simulator logs every method call it cannot answer. One boot of the authentic path, at
130 s, produced **60 such calls across 10 distinct methods** - a concrete work list instead of a guess.

## The backlog

```
com.lge.car.micom.can  member=SetCANAMP_HU_P_01Request
com.lge.car.micom.can  member=SetLevelGearInitialRequest
com.lge.car.micom.can  member=SetUSMInitialRequest
com.lge.car.micom.ihu  member=AskEtcLcd2SensorNotSupportPwmControl
com.lge.car.micom.ihu  member=AskExternalSPDIFAMPVersion
com.lge.car.micom.ihu  member=AskInfoFaultCodeStatus
com.lge.car.micom.ihu  member=AskUSMSetting
com.lge.car.micom.ihu  member=AskVolumeTuneKeySwap
com.lge.car.micom.ihu  member=SetETCLanguageInfoSet
com.lge.car.micom.ihu  member=SetSettingValueStatusMsg
```

Ten methods, two interfaces, each caught by the simulator's own `ENG_DATA_SIM_UNKNOWN` log line. **These are questions the
running vendor stack actually asked and did not get an answer to** - not a list of everything the MICOM interface
defines.

## What this is good for

1. **It is the adaptor backlog, ranked by evidence.** Each entry has a caller that wanted it during a normal boot, so
   implementing them is fidelity work with a known consumer rather than speculative completeness.
2. **It bounds the "unknown" condition.** The stack tolerates ten unanswered methods and still boots, brings up the
   launcher and starts the application - so these are not blockers for the boot path, but they are the reasons the
   settings, audio and geometry state the application reads are partly default values.
3. **It is cheap to extend**: the simulator already has an acknowledgement table, so each of these is one row plus a
   reply payload whose size and semantics come from the same introspection data this project has been using.

## What it does not establish

That answering them changes anything visible. Several are plausibly cosmetic (`AskVolumeTuneKeySwap`,
`AskEtcLcd2SensorNotSupportPwmControl`), and the two `AskInfoFaultCodeStatus` / `AskUSMSetting` paths touch diagnostic
state whose correct reply is not known from the image alone. Each needs its reply shape established before it can be
implemented honestly.

## Method note

The simulator only logs what it *rejects*, so **a method that was added and accepted produces no log line at all** - the
absence of `SetEnginnerModeEntryCheck` from this list is consistent with the entry added to the acknowledgement table
working, and equally consistent with the application never having called it during that boot. A positive test needs the
simulator to log accepted calls too.

---

## 2. The instrument now logs what it accepts - and that changes what the numbers mean

The simulator logged rejections from the start and said nothing about accepted calls, so **"no rejection appeared" was
indistinguishable from "the method was never called"**. That is the same failure mode as counting a truncated log
(`docs/MEASUREMENT-DISCIPLINE.md` rule 14), one layer down. Accepted calls are now logged too.

Same boot, unchanged image except the new binary:

```
ENG_DATA_SIM_ACK      393 calls
ENG_DATA_SIM_UNKNOWN   57 calls
SetEnginnerModeEntryCheck  ACKED: 0     MISSING because it was never CALLED
AskMPModeInfo              ACKED: 0     likewise
```

**The accepts, by volume:**

```
330  com.lge.car.micom.can  AskCANMMCANMicomReq          <- the poll loop
 35  com.lge.car.micom.ihu  SetETCCPUAliveMsg             <- the heartbeat
 13  com.lge.car.micom.can  SetCANFixedMicomRecv
  4  com.lge.car.micom.ihu  SetETCAppBootComplete
  4  com.lge.car.micom.can  SetDATCInitialRequest
  3  com.lge.car.micom.ihu  SetDIDInfo, SetControlKeyLock
  1  com.lge.car.micom.can  SetCANMicomRecv
```

**So eight methods account for all 393 calls**, and one of them (`AskCANMMCANMicomReq`, 330 of 393) is the CAN polling
loop - which is why the CAN values matter and why its absence (`can0`, V-0xx) shows up as missing widget data.

## 3. The engineering entry-check row is added but **unexercised**

`SetEnginnerModeEntryCheck` and `AskMPModeInfo` were **never called** during a normal boot, so the row added in the
previous entry has not been tested by anything. **That is the honest status: implemented, rebuilt, injected, and
unreached** - because the settings application only asks that question when a user navigates toward engineering mode,
which this projection cannot currently do.

**Which closes a loop:** the VM goal needs engineering mode to be reachable to verify that method; the method exists to
let the settings application enter engineering mode. Neither side can be verified without the other, and the way out is
the same as before - the engagement has to come from the manager side (`V-060`'s signal or the entry-check reply), not
from a normal boot.
