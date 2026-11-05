# opus-5-5 — the third plan: judgement over coverage

Date: 2026-11-06. Written after reading `docs/CURRENT-STATE.md` (top), `docs/vm/45-…md` §§45-65,
`docs/kernel/25-registration-warm-fast-but-still-killed.md`, `docs/REMEDIATION-REPORT.md`,
`docs/root-access-paths.md`, `docs/defences/controls-inventory.md`, and all sixteen rules of
`docs/MEASUREMENT-DISCIPLINE.md`. Every claim below names the entry it comes from. This is a plan to
*not* make the two mistakes the last ten entries of file 45 made — guessing a constant and patching a
plausible-but-wrong thing — so most of it spends existing evidence before it spends a run.

---

## 1. The single next action on the display thread

**The action is a read, not a change — and that is the decision.** Open the launcher log window that
already exists, `21:40:33` → `21:40:57` (kernel/25; file 45 §65), and classify what kills the *warm,
fast-registering* instance 2606 at `21:40:57.199`.

**The exact change:** none to any binary. The exact operation is three greps over the existing boot-46
launcher log for the pid that registered at `21:40:33.644` (2606):

```
grep -nE '2606|AppId\[11\]|appProcessFinishedSlot|onDemandAppKill|hang|appTerminateSlot|Launch complete|request.launch|\[TIMEOUT\]' <boot46-launcher.log>
```

restricted to the 24-second window, read in timestamp order.

**The textual check / stop condition — three mutually exclusive outcomes, each ends the action:**
- a **new `request.launch`/`[Group]` retry or `onDemandAppKill`** line at `~21:40:57.1` immediately
  *before* 2857 launches at `21:40:57.712` → killer B is the **relaunch loop** (the launcher kills the
  incumbent as it spawns the next retry). Stop; go to §2's loop branch.
- a **`*-hang` / `appTerminateSlot` / watchdog / liveness** line → killer B is an **app-alive
  watchdog** (the same family as `AB010512…AppEngineerMode-5-hang` in CURRENT-STATE §1b). Stop; go to
  §2's liveness branch.
- **nothing in the launcher log** between register and `appProcessFinishedSlot [15]` → the killer is
  **outside the launcher**. Stop; the next read is `ApplicationManager`, not the launcher.

**Why it beats the other candidates (the three changes file 45 queues):** patching the 45 s deadline is
refuted work — §56 applied the `0x18270` 10 s→30 s patch and the timeout fired unchanged, and §60 found
the real value is a *computed* `45000` with an unknown caller, so there is no instruction to patch yet.
Emitting `preload_complete_status` (§53) addresses the deadline, but §64 already shows the deadline is
**moot on warm relaunch** (registration drops to 1–8 s). And re-running a pre-warm (§63) just re-hits
killer B without naming it. Reading a window we already captured is free, cannot damage the target
(MEASUREMENT-DISCIPLINE §3, §8), and is the one thing that gates every downstream change.

---

## 2. The ~24 s second termination

**Best hypothesis:** killer B is the launcher's **relaunch loop still running**, and each new spawn
`onDemandAppKill`s the incumbent. The evidence is already on the page: 2606 is killed at
`21:40:57.199` and 2857 launches at `21:40:57.712` — **0.5 s apart** (kernel/25 table; file 45 §64).
That is not a 24 s watchdog on the instance; it is the ~24–32 s *inter-relaunch interval* of a launcher
that does not consider app 11 "done," expressed as a SIGTERM of the predecessor. The puzzle is that
2606 printed `[Group 2] Launch complete` (kernel/25) and is *still* retried — so the retry trigger is a
flag separate from "launch complete," most likely the preload/registration ack the real
`ApplicationManager` is meant to consume and that nothing in the projection supplies (CURRENT-STATE
§1b: registrations are addressed to `com.lge.hyundai.avn.appmanager`, which **nothing owns**).

**The specific lines that confirm or kill it:** in the `21:40:33`→`21:40:57` window —
- `onDemandAppKill appId[11]` **caused by a fresh launch/group retry** confirms the loop;
- a standalone `appProcessFinishedSlot [15][0][1][11]` with a preceding `*-hang`/`appTerminateSlot`
  kills the loop hypothesis and names a **liveness watchdog** instead;
- `[REGISTERED ERROR] Already registered` re-appearing confirms the **duplicate-registration guard**
  re-firing (file 45 §62).

**If the loop is confirmed:** the fix is projection-side and is the project's own idiom — stop the
retry by supplying the acknowledgement the launcher/manager waits for. Two options, cheapest first:
(a) run the real `ApplicationManager` so the registration addressed to it is *owned* and answered
(CURRENT-STATE §1b names it as the missing owner), or (b) emit the completion/health signal on the
already-mapped `com.lge.avn.appmanager.info` interface (`preload_complete_status(bool)`, file 45 §53)
so the launcher treats the first instance as healthy and stops relaunching. **If a liveness watchdog
is confirmed instead**, file 45 §65 states the useful consequence in advance: the app is being killed
for a heartbeat it never reports because our stand-in does not drive it — which is a **stand-in
problem, the class of work this project is best at**, not a timing problem. In both branches the
action is to *answer a query*, not to patch a constant.

---

## 3. Widget values (CAN): route and defence

**Route: a `vcan` interface on the rebuilt 4.1.27 tree.** Build `CONFIG_CAN_VCAN=m` against the kernel
source already in the repo (the measured state confirms the 4.1.27 tree now rebuilds and boots —
CURRENT-STATE §1), `ip link add can0 type vcan; ip link set can0 up`, and a ~20-line C frame sender
emits the pinned SOC frame `0x2fc` byte 7 = `119` → 59.5 % (CURRENT-STATE §0) plus the range frame,
validated against `evidence/vehdata-ground-truth.md` (65 % → 287 km, ~4.4 km/point).

**Why this route and not the other two:** CURRENT-STATE's original objection to vcan was "we have
neither the tree nor a shipped `vcan.ko`." **Half that objection is gone** — the tree now builds. The
micom-link route is still blocked earlier than its own fix (no SPI device, no micom platform device;
CURRENT-STATE §0), so it needs a board change we cannot make in QEMU.

**The honest risk, stated plainly:** the third route, a `LD_PRELOAD` CAN shim, **has already damaged
this project once.** `can_shim.so` in `/etc/ld.so.preload` overrode `close()` process-wide and
substituted socketpairs for every `PF_CAN` socket, and the app died with
`wl_display@1: error 0: invalid object 19` — it was read as vendor behaviour for several runs
(CURRENT-STATE, "READ THIS BEFORE RUNNING ANYTHING"; MEASUREMENT-DISCIPLINE §3, §8). A launcher-scoped
CAN preload interposing `connect`/`recv`/`close` touches the *exact* call family that produced that
Wayland fatal error, and getting the scoping right is the same fragile targeting that cost the project
an evening. **vcan keeps the interposition at the kernel/socket boundary**, where the application opens
a real `PF_CAN` socket on a real `can0` and cannot tell the difference at the API — no override of
`close()`, no socketpair substitution, no risk to the Wayland connection. Its only honest cost is
fidelity: it is a virtual bus the vendor kernel never had, so it **must be labelled as an instrument in
the artifact and the changelog** (MEASUREMENT-DISCIPLINE §8). Precondition to check before trusting any
result: that the app binds **`can0`**, not `can1`, from `connectCanListenerSignals` (CURRENT-STATE §0).

---

## 4. The register: three to demonstrate, three to drop

**Demonstrate end-to-end (projection-reachable, mechanism-complete, one read/run from proof):**

1. **Item 7 / V-059 — updater verify-then-reinstall (keyless downgrade).** The strongest finding and
   the only open question on it is answerable in the projection without a vehicle: run FUMO's two
   invocations and `strace` the apply pipeline's second open to settle whether
   `DecryptToPIPE … | dd of=<partition>` reopens the **removable medium** or a **staged local copy**
   (REMEDIATION §7; root-access-paths route 1). That one observation turns "mechanism statically
   corroborated" into "demonstrated," and the keyless-downgrade consequence needs no key.
2. **Item 8 / V-051 — `request.launch` runs a caller-named path as root.** Already ran as `uid=0`
   (REMEDIATION §8; root-access-paths route 7). Make it a clean, repeatable end-to-end: arbitrary path
   → `uid=0`, framed against the ambient-root thesis (V-064, 106/107 services as root) that makes it
   the platform's persistence primitive.
3. **Item 2 / V-054 (with the 16/V-065 anchor family) — account DB symlinked into `/tmp`.** Already
   produced a working `uid=0` account; close it with the negative control the discipline demands — the
   write *fails* once the anchor moves to read-only storage (REMEDIATION §2, §16;
   MEASUREMENT-DISCIPLINE §6). It is the cleanest proof of the report's single-sentence thesis.

**Do not spend time on:**

1. **Item 5 / V-049 — crack the serial-console password.** 45,000 candidates already failed
   (REMEDIATION §5; root-access-paths route 4); the *finding* (console enabled, fail-open) is complete.
   What remains is an offline GPU brute-force gamble, not research, and it changes no conclusion.
2. **Item 10-adjacent / V-014 + V-009 — USB SCSI property injection.** QEMU cannot emit the control
   characters into the SCSI serial field (root-access-paths routes 6, 9). It needs a programmable SCSI
   bridge on real hardware; it is not demonstrable in the projection at all.
3. **V-057 / removable-media FS driver fuzzing (texfat/tntfs).** 20 crafted images across 9 mutation
   classes already produced **no fault** (root-access-paths route 5). An open-ended coverage-guided
   sweep is large investment with no lead and low expected yield.

**What distinguishes the two sets:** the three to demonstrate are each one read or one run from an
end-to-end proof *inside the projection* and each strengthens the register's actual thesis; the three
to drop are each blocked by something the projection cannot supply — a GPU, a hardware bridge, or an
unbounded search — and none would change the conclusion that the platform's weakness is *persistence
from writable anchors*, not *entry* (root-access-paths, "What this page is really saying").

---

## 5. The one thing the project is most likely wrong about

**That the composited frame after the surface-id patch is the home screen at all. It is most likely
`AppCamera`.** The contradiction is already in the repo: §0 of CURRENT-STATE concluded that the
`STR_CAMERA_ALERT2` title "exists **only** in AppCamera's translations" and that such a frame is
"almost certainly `AppCamera`, not the home screen" — yet file 45 §49 (a day later) describes a frame
with "the blue title bar with the literal `STR_CAMERA_ALERT2`" and calls it "the app's standby face"
of the home screen. Both cannot be true. Worse, the surface id the patch assigns to app 11 is **2080,
which the vendor's own launcher table maps to app 12 = `AppCamera`** (file 45 §45, §47: `12 → 2080`).
So the patch gives the home screen the *camera's* surface id, and file 45 §48 then shows
`SURFACES=[30000|2080|1001|1002|2080|1004]` — **2080 appears twice** — a surface-id collision in which
the camera's chrome can win. The patch may be compositing, and the project may be photographing, the
wrong application (MEASUREMENT-DISCIPLINE §4 "black is a conclusion", §11 "a byte size is a hint, never
a verdict — describe the frame, and say which surface id it came from").

**The cheapest check:** in the same existing capture run, read which pid owns each `2080` entry in the
`SURFACES` list and whether `AppCamera` (app 12) is among the running processes — one `grep` of the
launcher log for app 12's launch and for the two `Set to QT_WAYLAND_SET_SURFACE_ID=2080` lines. If
app 12 is running, its surface is the collision and the `STR_CAMERA_ALERT2` pixels are camera chrome,
not home standby. Even cheaper, and already available: trust the title the frame already shows —
`STR_CAMERA_ALERT2` is a camera string — over the attribution, which is precisely rules 4 and 11. If
this is right, the surface-id patch needs a **non-colliding** id (an id that appears in *no* launcher
log row *and* is not already owned by a running app), which is a one-field correction at the same
offset `0x475e8`, with the same stated trade.

---

## 6. Opening message for the next session

> You inherit a display path that is eight of nine steps complete: the rebuilt 4.1.27 kernel gives
> `bochs-drm`/`card0`/native 1920×720, the vendor `drm-backend.so` binds it, the compositor serves a
> Wayland socket, and after a one-entry launcher patch at `0x475e8` (11 → surface 2080, consuming
> app 113's row) the vendor application composites — but only its standby chrome, and every instance
> that responds to `set_power_on_status` is terminated. Two killers are now distinguished: a cold 45 s
> registration deadline (moot on warm relaunch, 1–8 s) and a second SIGTERM ~24 s after a warm
> instance registers. **Do this first, and change nothing until you have:** read the existing launcher
> window `21:40:33`→`21:40:57` and classify killer B as relaunch-loop, liveness-watchdog, or
> outside-the-launcher (§1). Before you trust any composited frame as "the home screen," confirm it is
> app 11 and not `AppCamera` on a colliding surface 2080 (§5) — describe the frame in words and name
> the surface id, per MEASUREMENT-DISCIPLINE §11. Do not re-patch the 45 s deadline (§56/§60 refuted
> that) and do not reach for an `LD_PRELOAD` CAN shim (it has already killed the app once); CAN data
> goes through a `vcan` interface on the kernel tree you now have (§3).

---

### Final message

**Single next action:** read the launcher log window `21:40:33`→`21:40:57` that already exists and
classify what SIGTERMs the warm instance 2606 — a free read that gates every downstream change and
avoids repeating §56/§60's refuted patches.

**24 s hypothesis:** it is the launcher's relaunch loop, not a timer on the instance — 2606 is killed
`21:40:57.199` and 2857 spawns `21:40:57.712`, 0.5 s later; the launcher keeps retrying app 11 because
nothing owns the registration it waits to ack (`com.lge.hyundai.avn.appmanager`), so the fix is to
answer that ack projection-side, not to patch a constant.

**Most likely wrong:** that the composited frame is the home screen — its `STR_CAMERA_ALERT2` title is
a camera-only string and the patched id 2080 is the vendor's `AppCamera` id (it appears twice in the
`SURFACES` list); it is probably `AppCamera` on a colliding surface, checkable with one `grep` for
app 12.
