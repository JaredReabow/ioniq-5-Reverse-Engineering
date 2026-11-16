# Agreed next steps, after four independent plans

Date: 2026-11-06. Four planners were given the same repository state and the same constraints, and asked the same question
independently. This page records **where they agree**, **where they disagree**, and **what changed because of them**. The
individual plans are `fable.md`, `astra.md`, `daybreak-blue.md` and `opus-5-5.md`.

## 1. The headline: an independent reviewer found a real error

Opus 5.5 (§5 of its plan) noticed that the surface-id patch assigns **`11 -> 2080`**, while the vendor's own table assigns
**`12 -> 2080` to `AppCamera`** - and that the patched run's surface list contained **2080 twice**. Verified here against the
binary: the table reads `17->1030, 12->2080, 110->2110, 111->2110, 112->2160, 113->2170, 73->2200, 30->3000`.

**So the "compositing works" claim is withdrawn** (`docs/vm/45-...` §66): the frame showing the literal `STR_CAMERA_ALERT2` is very
probably the **camera's** window, which is what this project had already concluded hours before and then contradicted.

**The corrected patch uses an id absent from the table** (`1010`, or `2210`), and the check is: the launcher line for `AppID : 11`
with the **new** id, and that id appearing **once** in the surface list.

## 2. Where all four agree

| point | agreement |
|---|---|
| **The next action is a read, not a change** | all four put the launcher log ahead of any patch or boot |
| **Stop patching constants on a guess** | three of four say so explicitly; the fourth says the same in different words |
| **Prefer projection-side fixes** | unanimous, and all four cite the four documented substitutions as the ceiling of what may be changed |
| **Move remediation to configuration-first** | all four rank V-065 (the nine `/tmp` anchors), V-071 (fail-closed console/SSH) and V-064 (root-everywhere) at or near the top |
| **The register is already longer than its evidence** | all four say the next move is demonstration of a few items, not more entries |

## 3. Where they disagree, and the disagreement is the useful part

**The ~24 s second termination.** Opus 5.5 hypothesises the launcher's **relaunch loop SIGTERMing the incumbent** (2606 dies at
`21:40:57.199`, 2857 launches at `21:40:57.712` - 0.5 s apart). Astra suspects **one mechanism with two faces**. Fable and Daybreak
Blue both defer to the log. **The measurement settles it for all of them**: `docs/kernel/26-second-kill-is-sigsegv.md` shows
`appProcessFinishedSlot [11][0][1][11]` - **exit code 11 = SIGSEGV** - so the warm instance **crashes during the power-on layout**,
with `ClearTimeoutLoading : 11` printed immediately before it. **Opus's relaunch-loop hypothesis is therefore refuted by the
evidence, and the crash is the real second mechanism.**

**What to cut.** Astra cuts micom/SPI emulation and any further backend or vCPU work; Opus cuts blanket preload automation and
global preload-complete forgery; Daybreak Blue cuts claim growth before evidence consolidation. **No disagreement**, but Astra's cut
is the largest and the most defensible.

## 4. The plan, merged and ordered

1. **Re-run with a free surface id** (`1010`), verify textually: `QT_WAYLAND_SET_SURFACE_ID=1010` for `AppID : 11`, and `1010`
   appears **once** in the surface list. **Only then** look at a frame, and describe what is visible rather than what it should be.
2. **Read the app's own stderr immediately before the SIGSEGV** (`/tmp/applauncher-stdio.log`, last ~30 lines before
   `App has been Crashed`). Every one of tonight's blockers was answered by a log nobody had collected.
3. **Do not touch the 45 s deadline again.** Its value is computed, two candidate constants have failed, and the warm path clears
   the deadline anyway (`ClearTimeoutLoading : 11`).
4. **Security: five configuration items first**, in Daybreak Blue's order - `/tmp` trust anchors (V-065), fail-closed console/SSH
   (V-071), service containment (V-064 then V-072), update credentials off writable/shared storage (V-068/V-069), and the single-stream
   update verification (V-059 item 7).
5. **Demonstrate three, state the rest as configuration-level** - and publish bounded confidence rather than an unbounded list.

## 5. The stopping rule, adopted from Fable 5.1

**Stop when** the two remaining threads have each been attributed to a named mechanism that is **not** one of this project's
instruments, **and** the text evidence exists for both; **or** when a further run would only re-measure something already measured
twice. Continue **only** while a cheap read could still name a mechanism.

**As of tonight:** the display thread is one read away (the app's stderr before the SIGSEGV) and the security work is one
configuration change away from its first verifiable item. **Neither is a guess, which is why both are worth doing next.**
