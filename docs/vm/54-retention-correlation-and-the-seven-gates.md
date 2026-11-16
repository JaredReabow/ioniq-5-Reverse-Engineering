# Retention, correlation, and the seven gates to an interactive screen

Date: 2026-11-06. Astra and Opus 4.7 were given the corrected state (handshake flows, wrong-bus refuted, duplicate unexplained)
independently. Their answers are complementary rather than overlapping, and one of them withdraws part of the evidence.

## First: a correction to the duplicate evidence itself

**Opus 4.7, §4:** `WARM_DUPLICATE=1` in `docs/kernel/31` was derived from a `WARM_REG=[…]` string **the probe assembled by grepping the
launcher log in place**. If the probe's pattern is wrong, the duplicate it reports is the probe's conclusion, not the system's behaviour.

**That is the third instance of one shape of error in an hour** - the interface/name confusion, the wrong-bus inference from a capture taken
before the process existed, and now a finding derived from a derived string. **Every one of them looked like a vendor fault.** Until the
launcher log is retained raw and read directly, the duplicate is **NOT MEASURED** in the strict sense this project now uses.

## Second: retention is a launch prerequisite, not a post-hoc convenience

**Astra's contract**, adopted: a **host-chosen run ID** before boot, a **host-retained evidence volume** (never the guest's `/tmp`, which
took the full monitor log last run and kept 500 characters on the console), and a **verified export** - the run does not count as started until
the export path is proven writable from the guest and readable from the host.

**The rule this enforces:** *a null result must still answer the question.* The last two runs each produced a number that looked like an
answer and was not, because the evidence that would have qualified it lived somewhere ephemeral.

## Third: correlation, given two different clocks

The monitor logs **guest-monotonic** time; the launcher logs **wall clock**. Ordering must be **proven, not inferred**, for the specific
question *which registration notification arrived second*:

- emit a **marker** into both streams at one instant (a `logger` line the launcher writes plus a `dbus-send` ping the monitor sees), so one
  event exists in both clocks;
- then compare **content**, not timestamps: the monitor's `registration` call carries `appid`, `appname`, `servicename`, `objectpath`, `plane`;
  the launcher's line carries `AppId` and `AppName`. Match on the **pair**, and the wall-clock gap becomes corroboration rather than proof.

## Fourth: the four candidate sources of the duplicate, and the one capture that discriminates

Opus 4.7's enumeration, with the discriminator:

| source | how it would look in a retained trace |
|---|---|
| manager fans out two signals per `registration` | one method call, **two** signal emissions on the interface |
| two launcher subscribers on one connection | one signal, **two** `[REGISTERED]` log lines in one process |
| the launcher's own timeout path registers first, app's announce second | `[TIMEOUT]` immediately before the first `[REGISTERED]` |
| the app announces twice (`registration` to the manager AND `launched` to the launcher) | **two** method calls from the same sender in the trace |

**One retained, unfiltered monitor log plus one retained launcher log discriminates all four.** No further probes needed.

## Fifth: the seven gates to an interactive screen, adopted from Astra

Assuming the duplicate resolves, in order - and each gate is separate because this project has twice mistaken one gate for another:

1. **Lifecycle closure** - correct owner, correlated completion, no fallback duplicate, authentic label, warm start.
2. **Deliver power-on to that instance** - and retain evidence it was **consumed**, not merely sent.
3. **Survive the home layout** - home stderr, denials, lifecycle and any crash at power-on.
4. **Prove surface ownership** - app 11 owns a **unique, non-colliding** surface (the `2080`-twice mistake is why this is its own gate).
5. **Prove content and geometry** - an actual 1920x720 output with the intended surface geometry, not a same-sized standby frame.
6. **Prove interaction, not just pixels** - declare one harmless action and its expected visible transition **before** performing it.
7. **Repeat from a clean, documented start** - the declared warm-up, label, surface and input configuration reproduced end to end.

**Gate 6 is the one that answers the user's actual goal.** A composited frame is not an interactive system; a declared action with a predicted
result, observed, is.

## And the discipline lesson, both models independently raised

**Three false negatives in one hour, all looking like vendor faults.** Rules 17 and 18 cover two of them. The third needs its own line:
**a finding derived from a string your own probe assembled is not evidence** - read the raw artefact.
