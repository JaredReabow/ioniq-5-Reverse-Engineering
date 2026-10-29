# Navigation status: what is measured, and what still blocks the transition

Recorded 2026-10-29. Build `NE_E.EUR.S5W_L.001.001.260128`, x86-64, kernel
`4.1.27-abl`. Everything below is measured in the project's isolated QEMU VM unless
stated otherwise.

## Where the VM is

The vendor kernel boots, the recovered userspace runs, the authentic launcher chain
passes the standby and profile-confirm gates, and the genuine `AppHomeScreen` renders
with real tiles. AppNavi starts and can render genuine map pixels into its own
surface. **Home ↔ Navigation does not transition**, and this document records why the
remaining gap is narrower than it was.

## What is now measured rather than inferred

### 1. The EGL dimension ordering defect

An in-VM hardware-breakpoint observer attached to the authentic `AppCamera` inside the
real launcher chain and captured two stages of vendor `libEGL`'s software path, reading
the surface fields at `+0x2c` (width) and `+0x30` (height):

| Stage | Location | width | height |
| --- | --- | --- | --- |
| before the width cache | `libEGL+0x16f16` | **-1** | **-1** |
| immediately after `swrast_update_buffers` returns | `libEGL+0x16f1e` | **1920** | **720** |

Same surface pointer at both stages. So `swrast_update_buffers` populates the
dimensions *during* that invocation, while the copy path had already derived its stride
from `Width = -1`, yielding `-4` bytes. The stale-stride ordering defect is measured,
not deduced.

Scope: the affected code is the vendor's **Wayland software (swrast) display path**. The
binary contains separate constructors for the hardware paths
(`dri2_wl_create_window_surface`, `dri2_drm_create_window_surface`) which do not share
that vtable, so this evidence does not implicate the i965/i915 path. Tracked as I-001.

### 2. A Qt hide cannot produce the background notification

ApplicationManager only latches its navigation window byte on a **background** (BG)
window notification, and the compositor classifies a surface as BG only when both
dimensions are non-positive. `usr/bin/weston` retains DWARF for `weston_surface`, which
fixes the layout (`width` `0x68`, `height` `0x6c`, `width_from_buffer` `0x104`,
`height_from_buffer` `0x108`).

A null-buffer attach — what a Qt `hide()` becomes — zeroes the `_from_buffer` pair, but
the commit size block at `0x40f470` runs **before** that zeroing, so the surface keeps
its previous positive size and still classifies as foreground. A subsequent commit
without a new attach does not re-enter that block.

**Conclusion: a bare `hide()` is insufficient; a genuine transition to `0x0` is
required**, which matches the earlier Camera/Standby control that drove
`1926x753 → 0x0 → BG`.

### 3. Guest hardware breakpoints work

Execute breakpoints via `ptrace` on `DR0`/`DR7` function correctly under QEMU TCG with
this kernel: four slots arm and fire in program order, slot replacement works,
`DR4`/`DR5` are rejected, `DR6` reports per-slot bits and is clearable, single step
works, and debug registers are **per thread**.

One behavioural finding matters for any observer: **`PTRACE_DETACH` with a slot still
armed leaves the breakpoint live and kills the tracee.** Disarm, verify the readback,
then detach — that sequence is proven safe.

## The remaining blocker

A scoped adapter was built to drive AppNavi's parent surface to a real `0x0` configure:
an `LD_PRELOAD` interposer on `wl_surface_attach` that suppresses buffer attachment
once a hold condition is met. Two useful things were learned building it, and one
problem remains.

**Injection is solved.** The launcher's own interposer calls
`unsetenv("LD_PRELOAD")` when running as AppLauncher, so vendor children inherit a clean
environment and no `LD_PRELOAD` on the launcher command line reaches an app. Injection
must go through that interposer's `execve` hook, which rewrites `envp` for AppNavi
alone. A variant doing exactly that is included here
(`launcher_appnavi_navibg_preload.c`).

**The adapter loads.** With direct exec, AppNavi's own log records the adapter loading
with its hold parameters.

**AppNavi still never attaches a surface.** In both the full launcher chain and the
standalone render probe, AppNavi loads libraries and then produces no attach. The
manager reports drawing application `0` throughout. This is the blocker: there is no
surface for the compositor to classify, so neither the adapter nor the BG path can be
exercised yet.

## Open question, stated plainly

Whether the interposer itself is what prevents AppNavi from rendering. A
`wl_surface_attach` wrap is exactly the kind of interception that can break a client
that is not expecting it, and AppNavi's log being otherwise empty is suspicious. The
cheapest discriminator is a baseline run of the same probe **without** the preload: if
AppNavi renders normally there, the adapter is at fault; if it is equally silent,
AppNavi's startup is failing for unrelated reasons.

## Next steps, in cost order

1. Baseline the render probe without the preload and compare AppNavi's log and
   behaviour. One run.
2. If the adapter is at fault, narrow it to attaching only, with no hold, to separate
   interception cost from behaviour change.
3. If AppNavi is silent either way, treat startup as the blocker and investigate why
   the client exits before its first frame.
4. Only then revisit the `0x0` hold and the BG notification.

## Reproducing

The probe used for these runs is `tools/uk_fw/guest/appnavi_bg_probe.sh`; the interposer
is `tools/uk_fw/guest/navi_bg_0x0.c` and builds against the vendor's glibc:

```sh
zig cc -target x86_64-linux-gnu.2.25 -shared -fPIC -O2 -Wall -Wextra -Werror \
    -o navi-bg-0x0.so navi_bg_0x0.c
```

A musl-linked `.so` will not load into the vendor's glibc process. All experiments run
in snapshot mode with no NIC, and the canonical vendor image is never modified — runs
use an APFS copy-on-write clone with helper binaries injected by `debugfs`.

## Bounds

- Static evidence and VM measurement only; no hardware was used.
- The adapter has not been shown to produce a BG notification, because it has not yet
  had a rendering client to act on.
- Nothing here demonstrates a change to a vehicle head unit.
