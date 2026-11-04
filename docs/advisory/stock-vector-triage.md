# Stock-unit vector triage — two independent assessments, and what they changed

Two models were asked the same question: *on an **unmodified** production unit, with no developer build and no pre-existing root,
which weaknesses are actually reachable, and what experiment would settle each?* Their answers are summarised here with what each
contributed, including two corrections to this repository's own documentation.

Both were asked in a remediation-triage framing. No exploit code was requested or produced; the value was prioritisation,
reachability reasoning and experiment design.

---

## Where they agreed

**USB is the highest-value stock surface**, for the same reason from both: it is the only path where an attacker prepares a payload on
a PC and delivers it to root-owned parsers on the unit, with no credential and no shell first. They disagreed on *which* USB path:

| | Daybreak Blue | shannon-3.1-pro |
| --- | --- | --- |
| First pick | **SCSI/udev property injection** (**V-014**): a crafted INQUIRY/VPD string crosses `scsi_id`'s line-oriented property boundary and selects a root unit. Downstream root-unit selection is **already synthetically confirmed**; only the physical path is untested | **Media parsing** (`libgstasf.so` via the indexer): a malformed media file reaching a root parser |
| Character | Shorter chain to a definite root action, because the hard half is already proven | Broadest "just plug it in" story, but depends on which parser actually opens the file |

Both ranked **serial UART** second as the honest entry: it is the only route that yields a true shell without a bug.

Both put **engineering mode** last for *code execution*, agreeing it is parameter tuning rather than a shell.

## Where they corrected us

**1. The engineering PIN was wrong in this repository.** Daybreak Blue stated the digest in this build corresponds to a different
vendor default than the sibling-platform `19491003` documented here. Checked directly: `AppEngineerMode` carries exactly **two**
SHA-256 constants, and `19491003` matches neither. The engineer constant matches a different vendor default code and the dealer
constant is `2400`; both were verified by hashing candidates against the binary's own constants. Every document in this tree that
quoted `19491003` now carries a correction note. The plaintext engineer code stays out of this public tree, per V-041.

**2. `IpConfigShell` is not the stock shell this repository hoped for.** Daybreak Blue's finding, which is worth recording because it
was previously described here as "the strongest facility on the unit":

- the QML asset exists (`qml/IpConfig/AppEngineerMode_IpConfigMain_Shell.qml`), but the button that reaches it exists only in the
  **full** `AppEngineerMode_AutoTest.qml`;
- production loads `AppEngineerMode_AutoTest_Sop.qml`, which has no route to it;
- the binary's `EngIPConfigRefactor` meta-object contains `getSecureMode` and USB-state methods but **not** `handleSetIPMakeShell`
  or `enggetIP`;
- its UI accepts numeric octets only, with dots inserted by QML — there is no field for command text.

So it is stale, non-functional QML rather than a stock shell. The decisive test is to enumerate `IPInfo.metaObject()` in the
authentic process, or force the screen in a disposable VM and watch Qt report the missing function.

**3. The About-screen tap counter may not exist on this build.** Daybreak Blue notes the exact `260128` image does not contain the
tap counter the external sibling-platform project describes, so engineering entry on *this* build still needs physical confirmation.
This repository has treated the gesture as inferred-but-unverified; that remains the accurate status.

## Additional stock surfaces they raised that we had not examined

- **Wired CarPlay / iAP2** — `carplay_iAP2.service` is enabled, runs as uid 0, and parses phone-controlled, nested length-framed
  data. Named as more concrete than the presence of generic USB gadget modules, with the caution that module presence does **not**
  imply the functions are active.
- **Bluetooth** — `vbtd-51` / `vbtd-63` are enabled, run as uid 0, and contain a pre-fix BNEP parser shape. But both profiles show
  `PAN : N/A` and startup calls `BNEP_Init` without a matching `BNEP_Register`, so reachability is **contradicted rather than
  established**. The next step is to capture the active SDP records and PSMs before spending anything further here.
- **MICOM UART (`ttyS1`)** — unauthenticated framing (`AA | id | len | payload | XOR`); with the unit open this is a bus the unit
  trusts. Event IDs that would trigger privileged behaviour are not established.

## Their answers to the password question

Neither found an image-supported way to avoid cracking the hash: no `passwd` invocation in any stock script, no empty-password
entry (every other shadow entry is `*` or `!`), no rescue path that bypasses it (`sulogin` without `--force`), and no factory-reset
flow that rewrites `/etc/shadow.Global`. The fixed salt therefore helps with cracking and cross-unit reuse only — it does not
reveal the plaintext.

## Recommended order (adopted)

1. **V-014 physical path** — attach an emulated USB mass-storage device whose SCSI INQUIRY/VPD carries a benign injected property and
   observe whether udev acts on it. This needs a boot under the **vendor init** (systemd + udev), not the research init.
2. **CarPlay/iAP2 reachability** — confirm whether `carplay_iAP2.service` is active on this build and what actually parses iAP2 input.
3. **Media parsing depth** — instrument `lightmediascannerd`, its plugin set, and GStreamer to see which parser opens a crafted file.
4. **Bluetooth SDP/PSM capture** — cheap, and it either opens or closes that vector.
5. **UART** remains the honest fallback, pending an offline crack of the hash.
