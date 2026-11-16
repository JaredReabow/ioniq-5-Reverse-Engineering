# The SIGSEGV is a PHEV-data SMACK denial — the layout faults where the widget data is locked away

Date: 2026-11-06. Surface id corrected to 1010 (the camera's 2080 was a wrong assign), the deadline patch
reverted, and the run's `dmesg` collected. The crash's shape is now named.

## The corrected patch, confirmed

- `AppLauncher` re-patched: `0x475e8` now `11 -> 1010` (`0b 00 00 00 f2 03 00 00`); the ineffective
  `0x18270` deadline change reverted to the vendor `10 s`. sha256 `38ea164a…c912c`.
- Launcher log confirms the assignment: `AppID : 11, Set to QT_WAYLAND_SET_SURFACE_ID=1010` (× several).
- Capture is **144,501 bytes** — the user can open it to confirm it is the home screen's chrome, not the
  camera's `STR_CAMERA_ALERT2` window.

One honest flag: the surface *list* at grep time showed `…2080…1005…` (no literal `1010`), and
`APP_SURFACE_ID=[1005]` — so the ivi id the compositor assigned at that moment was 1005, not the env-var
1010. The textual assignment (1010) is confirmed; the surface-list id is a separate, not-yet-reconciled
number.

## The crash is a stand-in problem: PHEV DB is SMACK-denied

`dmesg` for pid 2990 (AppHomeScreen):

```
audit: lsm=SMACK fn=smack_file_fcntl action=denied subject="_" object="Data::commonphev"
       requested=l pid=2990 comm="AppHomeScreen" path="/rw_data/app_data/common/AppPhev/PHEVDB"
```

AppHomeScreen's subject is `_` (unlabelled) and it is denied a **file lock (`requested=l`) on the PHEV
database** — the Battery/Range (PHEV = plug-in hybrid EV) widget data. The launcher log separately shows
`appProcessFinishedSlot [11][0][1][11]` (SIGSEGV) ~24 s after a fast registration, i.e. the app faults
in the layout where it tries to open/lock the data it is not allowed to touch. No `segfault at` line
appears for AppHomeScreen itself (the only one is `BSA_Srv:BTU` in `libpthread`), which fits a
userspace null-deref after a failed open/lock rather than a kernel-visible fault.

## What this means

This is exactly the predicted stand-in problem: the app reaches the layout (registration is now fast once
warm — doc 25) and then faults where it expects the PHEV widget data, which SMACK denies to an unlabelled
subject. The fix is a **SMACK label or data stand-in**, not a timer, not a surface id, not a byte in the
launcher.

## Files

- `work/vm/kbuild/boot49-1010.log` — the run.
- `work/vm/kbuild/ws/partimg-build/AppLauncher.patched.bin` — surface-id 1010, sha256 `38ea164a…c912c`.
