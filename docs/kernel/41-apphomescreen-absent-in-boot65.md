# AppHomeScreen is absent in boot65 but present in boot58 — registration timing, not compositor or surface ID

Date: 2026-11-07. Static re-read of the retained `exported-weston.bin` logs from boot58 and boot65.
No QEMU was run for this correction. This is a measurement-correction document, not a REA-tool Evidence record.

## The measurement

Both runs load identical IVI modules and produce identical compositor topology:

| Item | boot58 (`1793931162561454000`) | boot65 (`1793944643111075000`) |
|---|---|---|
| Backend | `drm-backend.so` | `drm-backend.so` |
| IVI modules | ivi-shell, ivi-window-manager, ivi-controller, weston-vm-input | identical |
| IVI globals | ivi_application, ivi_window_manager, ivi_hmi_requester, ivi_info_requester, ivi_share, ivi_controller, weston_screenshooter | identical |
| Output | Virtual-1 1920×720 | Virtual-1 1920×720 |
| `screen(7)` events | present (multiple) | present (multiple) |
| `layer(…)` IDs | 107,112,111,104,113,102,110,10 | identical set |
| `surface_create(30000)` | 2 | 2 |

**The decisive difference is AppHomeScreen:**

- **boot58** contains exactly one `create_hmi_client(1, 1006, "AppHomeScreen", new id ivi_hmi_client@21)` at timestamp `[824313.371]`, followed by `set_display_plane(1)`. This is the valid AppHomeScreen surface (ID 1006 per the vendor table at `0x475c0`).
- **boot65** contains **zero** occurrences of the string `AppHomeScreen` anywhere in the entire weston log. Surface 1006 in boot65 is instead consumed by `AppStandbyClock` at `[1397567.242]`.

Boot58 also registers AppStandbyClock at 1006 *before* AppHomeScreen takes it (line 3082), then re-registers AppHomeScreen at 1006 (line 4414). Boot65 never gets to that second registration.

## What this refutes

1. **Not a compositor fault.** Both runs load identical modules with identical layer/screen topology. The compositor is not the discriminator.
2. **Not a surface-ID patch.** The vendor bytes at `0x475c0` assign 1006 to AppCamera; the AppHomeScreen patch was reverted and boot58 proved normal surface creation restored. Boot65's surface 1006 goes to AppStandbyClock, not AppHomeScreen — that is a *name* difference, not an ID collision.
3. **Not the missing `hmi-controller.so` module.** Boot58 created AppHomeScreen without it; boot65 has screen/layer announcements without it. The module is not the gate.
4. **Not `ivi_place` zero counts.** The `ivi_place` zero listing is observer-specific (doc 40 correction); the raw stream shows screens and layers in both runs. The zero count is not the AppHomeScreen difference.

## What this does NOT confirm — the original conclusion in this document was too strong

**CORRECTION (2026-11-08, after Astra review).** An earlier revision of this document concluded that
"the difference is registration timing". That conclusion is **not** established by the two logs. It was
an inference, and it had a live rival explanation that had not been checked. The rival is now measured.

### The capture boundary differs materially between the two runs

The two `exported-weston.bin` files are not atomic snapshots. `final-run.sh` measures the log, then
streams a still-growing file. Re-derived directly from the retained artefacts:

| Property | boot58 | boot65 |
|---|---:|---:|
| Declared `BEGIN weston` length | 234,468 B | 227,371 B |
| Actual decoded length | 277,341 B | 229,663 B |
| Growth during export | **42,873 B** | **2,292 B** |
| Byte offset of `AppHomeScreen` | **253,974** | absent |

`grep -abo 'AppHomeScreen'` places boot58's registration **19,494 bytes beyond boot58's own declared
length**, and 23,367 bytes before that export's end. In other words the observation window that recorded
the positive was not the window the script thought it had measured.

boot65's export grew only 2,292 bytes past its declared length. **The observation window that would have
had to contain the AppHomeScreen registration was roughly 19× shorter in boot65 than in boot58.**

### Consequence

"AppHomeScreen absent from the boot65 export" and "AppHomeScreen never registered in boot65" are now
two different claims, and only the first is measured. The absence is equally consistent with:

1. a genuine registration failure (the original inference);
2. the export ending before the registration occurred (capture truncation);
3. a different launch generation being observed (the warm/capture PIDs differ: boot58 reports 2667 at
   capture, boot65 reports 2677);
4. a launcher child-environment or app-identity difference.

Nothing in the two logs discriminates between these. This document therefore establishes only the
**presence/absence difference itself**, not its cause.

### What the timing numbers may and may not be used for

The ~48.58 s vs ~39.8–45 s figures come from `docs/kernel/22`, measured on a **different run**, not from
these two logs. `docs/kernel/23` further refutes a fixed ~48 s timer and shows a re-armed group-level
deadline. Importing those numbers to explain boot65's absence would stack two inferences, one of them
over a model the project already abandoned. Do not do it.

## Stop condition (revised)

Do not load `hmi-controller.so`, do not patch the launcher, do not change surface IDs, and do not extend
timeouts. **Do not run boot78 as originally specified** — its pre-committed null ("AppHomeScreen absent
⇒ registration timing confirmed") asserts a cause the evidence cannot carry, and would have converted a
capture artefact into a confident negative. The run task has been paused.

The next step is offline: reconstruct and compare the launch-generation and export-cutoff timelines for
both runs from `boot58-hmi.log`, `boot65-final.log`, `serial.log`, `dbg-out.txt` and the decoded streams,
per Astra's consultation. Only a discriminating result from that audit justifies one bounded run.

## Files

- `work/vm/kbuild/ws/runs/1793931162561454000/exported-weston.bin` — boot58 decoded weston log.
- `work/vm/kbuild/ws/runs/1793944643111075000/exported-weston.bin` — boot65 decoded weston log.
- `work/vm/kbuild/boot58-hmi.log`, `work/vm/kbuild/boot65-final.log` — launcher/hmi logs.
- `docs/kernel/40-ivi-screen-create-client.md` — protocol direction correction (screen is a server event).
- `docs/planning/astra-c7.md`, `docs/planning/opus-4-7-c7.md` — prior consultations.