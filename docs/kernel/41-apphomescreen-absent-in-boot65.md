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

## What this confirms

The difference is **registration timing** — the cold-launch registration loses to the launcher timeout (48.58 s vs. ~39.8–45 s measured in doc 22), while warm registration takes 1–8 s. Boot58's AppHomeScreen registered before the timeout; boot65's did not. The `qtimer_trace` shim (doc 23) already refuted the "~48 s fixed timer" hypothesis and showed the deadline is a re-armed group-level timer, not a single interval.

The remaining question is whether a fresh run under boot58-identical conditions reproduces the AppHomeScreen registration. Boot58 already proved it can; boot65 shows it can fail. The run is the only instrument that can settle whether the failure is deterministic or a one-off.

## Stop condition

Do not load `hmi-controller.so`, do not patch the launcher, do not change surface IDs, and do not extend timeouts. The next authorized run (boot78) tests one gate only: **does AppHomeScreen register surface 1006 before the launcher timeout, under conditions identical to boot58?** Pre-committed null: AppHomeScreen absent → the registration-timing path is the confirmed blocker and no compositor fix applies. Pre-committed success: `create_hmi_client(1, 1006, "AppHomeScreen")` appears in the raw weston log.

## Files

- `work/vm/kbuild/ws/runs/1793931162561454000/exported-weston.bin` — boot58 decoded weston log.
- `work/vm/kbuild/ws/runs/1793944643111075000/exported-weston.bin` — boot65 decoded weston log.
- `work/vm/kbuild/boot58-hmi.log`, `work/vm/kbuild/boot65-final.log` — launcher/hmi logs.
- `docs/kernel/40-ivi-screen-create-client.md` — protocol direction correction (screen is a server event).
- `docs/planning/astra-c7.md`, `docs/planning/opus-4-7-c7.md` — prior consultations.