# IONIQ 5 (LG Gen5W) infotainment research

Reverse-engineering notes and tooling for the 2021 IONIQ 5 head unit, with the
goal of **running the authentic vendor firmware — unmodified — inside an isolated
QEMU VM**.

This is research documentation. It is not a jailbreak guide and does not describe
how to modify a vehicle.

#### From the parallel repository

The parallel repository publishes this same research under the title
*IONIQ 5 reverse-engineering research*; the body follows.

Research notes, source tools and validation tests for a 2021 UK-origin
Hyundai IONIQ 5 Standard Gen5W infotainment system. The documented methods
and compatibility assessments distinguish official package evidence,
owner-supplied observations and community reports.

This public repository was initialized from a sanitized snapshot with fresh
Git history. Raw diagnostic exports, device dumps and private working
records are not included. See [PUBLIC-RELEASE.md](PUBLIC-RELEASE.md) for the
publication boundary and [tests/README.md](tests/README.md) for validation.

The research documents software and subsystem behavior. It does not include
a tested vehicle modification, update procedure or claim that a community
method works on the owner's installed build.

## VM research

The [current technical handover](HANDOVER.md) records a VM-adapted boot of the
European Gen5W Linux kernel, authentic Home rendering, isolated AppNavi map
pixels, and the unresolved Home-to-Navigation transition. Authored guest
helpers and experiment scripts are in [vm/repro](vm/repro), with bounded
evidence and inspected screenshots in [vm/evidence](vm/evidence). See
[vm/README.md](vm/README.md) for the source mapping and local artifact
requirements.

## Where the project is right now

The VM boots the genuine vendor kernel and the genuine recovered userspace, and
reaches the real Hyundai home screen. Navigation is the open problem.

| Area | State | Notes |
| --- | --- | --- |
| Vendor kernel boot | **Working** | Gen5W kernel boots under QEMU with a documented ABL boot-parameter adaptation. Anti-tamper is satisfied inside the VM. |
| Recovered rootfs / userspace | **Working** | EU 2026-01-28 image decrypted offline and mounted read-only. |
| Launcher: standby → profile confirm | **Working** | Authentic driver-selection and safety-notice screen. |
| Launcher: Home screen | **Working** | Authentic `AppHomeScreen` with real tile grid. |
| AppNavi (navigation) | **Partial** | Process starts, initialises, and renders genuine map pixels into its own surface. |
| Home ↔ Navigation compositing | **Blocked** | AppNavi never becomes the foreground window; Home stays visible. See below. |
| Audio | Not started | Needs C-TRACS/audio service contracts. |
| CAN / MICOM | Partial | Local D-Bus simulation exists; real contract still being reconstructed. |
| Persistence, restart/suspend | Not started | Needs evidence-derived storage and power contracts. |
| Input (touch/keys) | Partial | Wayland input harness exists; not wired end to end. |

Everything above is measured by snapshot runs — the disk image is never written
to, and the base rootfs hash is rechecked after each experiment
(`4953a005…6d036f`).

### Where the VM work stands

| Area | State | Notes |
| --- | --- | --- |
| Vendor kernel boot | Working | Gen5W kernel boots under QEMU with a documented ABL boot-parameter adaptation; anti-tamper satisfied inside the VM |
| Recovered rootfs / userspace | Working | EU `260128` image decrypted offline; mounted read-only |
| Launcher standby → profile confirm | Working | Authentic driver-selection and safety-notice screen |
| Authentic Home screen | Working | Real `AppHomeScreen` tile grid |
| AppNavi (navigation) | Partial | Process starts and renders genuine map pixels into surface 3000 |
| Home ↔ Navigation compositing | Blocked | AppNavi never becomes the foreground window; Home stays composed |
| Audio, persistence, restart/suspend | Not started | Need evidence-derived service contracts |
| CAN / MICOM | Partial | Local D-Bus simulation exists; real contract still being reconstructed |
| Input (touch/keys) | Partial | Wayland input harness exists; not wired end to end |

Runs use QEMU with TCG acceleration, `-cpu max,vendor=GenuineIntel`, 1536 MiB RAM,
disk `snapshot=on`, and **no NIC**. Snapshot mode is mandatory: a run must never
mutate the base image or reach the network.

## Screenshots

All frames are Wayland framebuffer captures from the running VM, at the head
unit's real 1920×720 geometry.

### 1. Profile / confirm screen

![Authentic driver-selection and safety notice screen](docs/vm/01-profile-confirm.png)

Produced by the genuine launcher, not a mock-up. Driver 1 / Driver 2 / Guest
selection with the real safety notice and Confirm / Language buttons.

### 2. Authentic Home screen

![Authentic AppHomeScreen tile grid](docs/vm/02-home-screen.png)

The real `AppHomeScreen`: EV, Map, Navigation, Phone, Phone projection, Voice
memo, Climate, Valet mode, Quiet Mode, Bluelink, Hyundai LIVE, Settings — with
the genuine top bar (profile orb, home, menu).

### 3. Attempted navigation, still showing Home

![Navigation attempt still displaying Home screen](docs/vm/03-navigation-attempt.png)

The honest failure case. This frame was captured during the navigation window.
Only the page-indicator dots changed; Home remains composed. This is the visible
symptom of the ApplicationManager state problem described below.

### 4. Genuine AppNavi map pixels

![Authentic AppNavi map surface with roads, river and position arrow](docs/vm/04-appnavi-map-surface.png)

Rendered by the authentic AppNavi binary into surface `3000`: real road network,
river, and the red position arrow. The map surface only occupies part of the
width, so the right-hand region is empty.

#### From the parallel repository

The parallel repository files these four frames under the heading
`### Inspected screenshots`.

All frames are Wayland framebuffer captures at the head unit's real 1920×720
geometry, taken from the running VM. The same four frames are published under
`vm/evidence/screenshots/`:

**Authentic profile / confirm screen** — produced by the genuine launcher, not a
mock-up.

![Authentic driver-selection and safety notice screen](vm/evidence/screenshots/profile-confirm.png)

**Authentic `AppHomeScreen`** — the real tile grid and top bar.

![Authentic AppHomeScreen tile grid](vm/evidence/screenshots/authentic-home.png)

**Attempted navigation, still showing Home** — the honest failure case. This
frame was captured during the navigation window; only the page-indicator dots
changed.

![Navigation attempt still displaying Home screen](vm/evidence/screenshots/navigation-attempt.png)

**Genuine AppNavi map pixels** — real road network, river and position arrow,
rendered by the authentic binary into its own surface.

![Authentic AppNavi map surface](vm/evidence/screenshots/appnavi-map-widget.png)

## Why Navigation does not appear yet

This is the current focus, and it is a contract problem rather than a rendering
problem. Recovered from disassembly plus runtime traces:

- AppNavi calls launcher `launched(30)`, then separately emits
  `SendNaviBootFail(5)` on `/navigation_map`. The `5` is a hard-coded literal, not
  derived from an engine result.
- ApplicationManager caches that status, but gates downstream handling on a
  *separate* window byte. That byte stays `0`, so the manager returns to
  `11/11` instead of settling in `APP_NAVI` (`30`).
- Only a **background** (BG) window notification updates that byte, and the
  observed runtime only delivers **foreground** (FG).
- The compositor rule is now known: **any positive width or height selects FG**;
  BG requires both dimensions non-positive. So "fixing" geometry from 1926×753 to
  1920×720 would not change the outcome.
- The BG path is not hypothetical: positive Camera/Standby controls were observed
  driving `1926×753 → 0×0 → BG → slotNotifyBGInfo`.

Open question: does AppNavi's genuine Qt `hide()`/null-buffer attach ever occur in
this stack, and can the VM legitimately produce the BG notification?

Deliberate non-actions: the status is not patched, the window flag is not forced,
and no success callback is synthesised.

#### From the parallel repository

The current state, with the measured evidence behind it, is documented in
[docs/navigation-status.md](docs/navigation-status.md). In short: the EGL dimension
ordering defect and the "a hide is not a background notification" result are both
measured now, and the remaining blocker is that AppNavi never attaches a surface, so
nothing reaches the compositor to be classified.

A contract problem, not a rendering problem — the same trace, worded from the
parallel record:

- AppNavi calls launcher `launched(30)`, then separately emits
  `SendNaviBootFail(5)` on `/navigation_map`; the `5` is a hard-coded literal.
- ApplicationManager caches that status but gates downstream handling on a
  separate window byte, which stays `0`, so the manager returns to `11/11`
  instead of settling in `APP_NAVI` (`30`).
- Only a **background** window notification updates that byte; the observed
  runtime delivers **foreground** only.
- The compositor selects FG for any positive width *or* height; BG requires both
  non-positive. Geometry changes therefore cannot fix this branch.
- The BG path is not hypothetical: positive Camera/Standby controls were observed
  driving `1926×753 → 0×0 → BG → slotNotifyBGInfo`.

## Running it

VM control lives in `tools/uk_fw/vm_boot.py`; boot-contract details are in
`evidence/`. The working configuration:

- QEMU with TCG acceleration
- CPU `max,vendor=GenuineIntel`
- 1536 MiB RAM
- disk `snapshot=on`
- **no NIC**

Snapshot mode with no networking is a hard requirement: runs must not mutate the
base image or reach the network.

## Exact-static update-trust and boot boundaries

Recent execution-free work has advanced four adjacent parts of the recovered
FUMO updater without running it or constructing update material:

- [Wildcard recovery-signal boundary](evidence/appfumo-dbus-recovery-signal-boundary.md)
  binds the empty-service/path Qt 5 subscription, guarded local consumer,
  canonical system-bus policy (including the uid-conditioned paired
  default-deny/root-allow sender rule), launcher identity, and
  SMACK/runtime-reachability boundary without publishing callable D-Bus
  coordinates or values.
- [Parameterized verifier provenance](evidence/appfumo-parameterized-verifier-provenance.md)
  resolves two formerly unknown direct verifier operands as one nested
  controller-resource route. Verification and transformation reuse a pathname
  value but independently reopen it, so same-object and same-byte continuity
  remain unproved.
- [Partition-write integrity](evidence/appfumo-partition-write-integrity.md)
  maps the source-integrity gate, its non-hash mode, inactive-target selection,
  and the write-completion boundary. Source verification is pre-write; no
  cryptographic readback of final inactive-partition bytes was found in the
  reviewed direct route.
- [Boot-activation boundary](evidence/appfumo-boot-activation-boundary.md)
  binds the completion QML and Qt dispatch chain to a local asynchronous reset
  request, separately maps reboot-system and recovery requests, and streams the
  canonical rootfs inventory. None of those requests carries a slot identifier
  or proves hardware action.

Together these results narrow the remaining boundary to same-bus runtime
reachability and labels, runtime pathname immutability, and external
MICOM/ABL/bootloader behavior. They do not establish an accepted modified
update, inactive-slot activation, mark-good, rollback, code execution, root
access, or persistence.

## Combined repository history

The two previously parallel public repositories now share the same combined
history. Their original lineages remain reachable through the merge ancestry;
no branch was squashed or replaced to perform the combination. This README
retains the highlights and evidence links from both bodies of work, and the
same reviewed combined commit is published to both repository remotes.

## Validation

```sh
python3 tests/run_all.py        # integrated read-only harness
python3 -m unittest discover -s tests
```

The harness checks the research ledger, artifact hashes, JSON validity, Council
packets, privacy rules and documentation scope. In public mode it inspects only
Git-indexed files.

## Project records

| File | Purpose |
| --- | --- |
| `HANDOVER.md` | Current checkpoint and next bounded task |
| `Ioniq5-CHANGELOG.md` | Editable, newest-first summary |
| `Ioniq5-HISTORY.md` | **Append-only** research history; corrections are appended, never rewritten |
| `Ioniq5-research-plan.md` | Scope, confidentiality and non-actuation boundaries |
| `evidence/` | Source-labelled findings with provenance |
| `PUBLIC-RELEASE.md` | What this public tree excludes, and the publication gate |

## Scope and confidentiality

This repository contains sanitised research findings only. Raw vehicle exports,
decrypted firmware, full core dumps, driving traces and third-party paper
artifacts are deliberately excluded and remain in a private archive. See
`PUBLIC-RELEASE.md` for the exact exclusion list and the conditions that must be
met before the repository is made public.

Security findings that could affect real vehicles are tracked in a separate
register outside this public tree and are handled under coordinated-disclosure
rules.

## Latest bring-up — 2026-10-31

State after a long session working the VM end to end. Everything below was measured, not assumed; the
scaffold and its hand-off notes live in `tools/uk_fw/ias_backend_soft/`.

### What now works

- **Authentic boot chain**: `init=/lib/systemd/esinit` reaches `Reached target Multi-User System`. Two vendor
  defects had to be worked around in a copy-on-write clone and both are recorded: `check-mount.sh` ships mode
  `0644` (no execute bit) and eleven `fstab` entries demand `mmcblk0pN` partitions the projection lacks.
- **Our own Weston backend** (`ias-backend-soft.so`): the vendor `weston` runs it with `ias-shell.so`, publishes
  `ias_crtc`/`ias_mode`, and `wrandr` reports `CRTC = 1, 1920x720 @ 60000`. The shipped compositor is
  **LG-patched**: `struct weston_output` differs from upstream 1.10 by `0x18` bytes, so a plugin built against
  upstream headers initialises fields in the wrong place and crashes it — `vendor-abi.patch` restores the layout.
- **EGL**: the image ships **no software rasteriser**, only Intel DRI. Injecting Debian `swrast_dri.so` with
  `libLLVM-3.9` and setting `LIBGL_DRIVERS_PATH`/`MESA_LOADER_DRIVER_OVERRIDE=swrast` is what makes GL work.
- **Frame capture**: a `weston_screenshooter` client plus a backend framebuffer dump. `--use-pixman` is
  mandatory, because the default renderer cannot read pixels back.
- **MICOM adaptors**: `micom-responder` provides the `/dev/ttyS1` peer (the guest is missing `/dev/pts`, so it
  runs on a pty) and `micom-service` owns `com.lge.car.micom` on the session-independent system bus. With them,
  the launcher reaches readiness for the first time:

  ```
  [  OK  ] Started HKMC Preminum AVN 2.1 -Launcher.
  micom-svc: AskSysBootinfo -> 35 bytes
  ApplicationLauncher::getAppProcessByAppId appId[2][ApplicationManager]
  ```

### What is still blocked, and why

The launcher registers and begins dispatching, then loops on `appId[2][ApplicationManager]` because
`ApplicationManager` cannot initialise boot information — it reports `initMicomShareMem() -> pszSrc NULL`.
Seven environmental hypotheses have been excluded by measurement (bus reachability, interface construction,
file-backed segments, peer presence, payload content, `/dev/shm`, segment existence). What remains is the
**layout and validity rules of the MICOM status structure**, which is disassembly work on a stripped binary.
Register entry **V-036** records this, with the elimination list and the anchors.

Because the client commits surfaces but never attaches a buffer, the HMI frame itself is black. That is
recorded honestly rather than cropped out — the control image is the evidence that the compositor renders.

| Compositor control (`weston-simple-shm`) | Current HMI frame |
| --- | --- |
| ![Compositor control](docs/vm/05-compositor-control-2026-10-31.png) | ![HMI frame](docs/vm/06-hmi-frame-2026-10-31.png) |
| Test pattern rendered by the vendor compositor through our backend — **173 distinct colours**, proving the whole path from backend to framebuffer works. | `AppHomeScreen` running with its surfaces mapped: uniformly black because no buffer is ever attached. `initMicomShareMem() -> pszSrc NULL` is why the launcher's dispatch never completes. |

Both frames are downscaled dumps of the backend framebuffer (240×90 natively, shown here upscaled 4×), moved out of
the guest over a `-chardev file` serial port — console transfer corrupts above roughly 8 KB, which is why that channel
is used.
