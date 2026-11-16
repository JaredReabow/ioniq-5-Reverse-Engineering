# Ground truth for the home screen's Battery and Range widgets, from a real vehicle

**Why this exists.** The last VM gap is that the Battery and Range widgets render `---` because no
vehicle data reaches them. When something is injected, there has to be a standard to judge it
against - otherwise "the number changed" is mistaken for "the value is right". This note is that
standard: what these two widgets read on an actual IONIQ 5, taken from the upstream log dump already
in this repository.

## Source

`evidence/upstream/Ioniq5_Gen5W_Log_Dump/` - **545 `.dlt` files** captured from a vehicle. The value
lines come from the application's own model:

```
[Thread # 3040 ] [ void AppPHEVModel::setSharedValues() ][ 4797 ] send NotifyPhevValueChange
    DTE:  260 unitSpeed()  1 Battery level:  60
```

**337 matching lines, 321 with both values parsed.** Both numbers are emitted by `AppPHEVModel::setSharedValues()`,
which is the same model the home widgets read - so this is the app's own output, not a CAN decode done
here.

## What the vehicle actually showed

| battery level | median DTE (km) | samples |
|---|---|---|
| 59 % | 260 | 10 |
| **60 %** | **262** | 48 |
| 63 % | 275 | 40 |
| **65 %** | **287** | 65 |
| 66 % | 286 | 58 |
| 67 % | 288 | 16 |

Ranges across the whole dump: **DTE 0-292 km**, **battery 0-67 %** (the zeros are start-up frames
before values arrive - which is exactly the state our projection is stuck in).

**The relationship is close to linear at about 4.4 km per percentage point** over the observed band.
That is a useful sanity check: an injected pair that does not sit near that line is wrong even if both
numbers are plausible on their own.

## How to use it

1. When a value is injected into the projection, compare the pair against this table, not against
   "it looks like a number now".
2. **0 % / 0 km is not success.** It is the pre-data state, identical in meaning to `---`, and a run
   that produces it has demonstrated nothing.
3. A faithful target for a first attempt is a **real observed pair**: battery 65 with DTE 287, or
   battery 60 with DTE 262.

## What this does not tell you

The CAN identifiers and byte offsets that carry these values on the wire. That mapping is being read
separately; this note deliberately stops at the values the application reports, which is the only
part that is ground truth from the vehicle rather than an interpretation of frames.
