# The swrast is Mesa 18.2.8 and the vendor libEGL is Mesa 11.2.1 — the library fix was necessary but not sufficient

> **CORRECTION (same day, `docs/kernel/48`):** the claim below that the "real cause" is a categorical
> Mesa-generation incompatibility is **withdrawn as overstated**. Astra C12 correctly noted that
> release numbers are not a definitive DRI incompatibility test. The performed audit found a **specific**
> defect instead: `libLLVM-6.0.so.1` requires `GLIBCXX_3.4.22` while the vendor `libstdc++6.0.21` stops
> at `3.4.21`. That is resolvable, and the projection already holds a `3.4.22` build. What stands from
> this document is the **measurement** (18.2.8 vs 11.2.1) and the fact that runs 5/6 refuted the
> library-staging hypothesis; what does not stand is the categorical conclusion.

Date: 2026-11-08. Runs 5 (`1794060182350787000`) and 6 (`1794060579223340000`), workspaces
`ws-run65` and `ws-run66`. **This entry records a refuted hypothesis and the evidence that replaced it.**

## What was tried

`docs/kernel/46` concluded that the staged `swrast_dri.so` could not load because two of its
dependencies (`libsensors.so.4`, `libLLVM-6.0.so.1`) existed only in `/opt/software-egl18/lib`, which
the vendor `AppLauncher.sh` discards. The fix was to stage them into `/usr/lib`, where the vendor
loader already searches.

Run 5 staged those two. **EGL still failed**, identically:

```
libEGL warning: DRI2: failed to open swrast (search paths /usr/lib/dri)
failed to initialize EGL d…
```

A dependency-closure check then found two more libraries reachable only from `/opt`:

| Library | Needed by | On vendor path before |
|---|---|---|
| `libedit.so.2` | `libLLVM-6.0.so.1` | no |
| `libbsd.so.0` | `libedit.so.2` | no |

`libncurses.so.5`, libedit's other dependency, was already present in `/lib`. Run 6 staged all four
libraries into `/usr/lib` — verified present by `debugfs` — and **EGL still failed in exactly the same
way**.

So the missing-library explanation is **refuted**. It was a real defect in the projection and fixing it
was necessary; it is not sufficient.

## The evidence that replaces it

| Artifact | Mesa generation |
|---|---|
| staged `/usr/lib/dri/swrast_dri.so` | **Mesa 18.2.8** |
| vendor `/usr/lib/libEGL.so.1.0.0` | **Mesa 11.2.1** |

A Mesa 18 driver cannot be loaded by a Mesa 11.2.1 DRI loader. The driver interface (`__DRI_DRI2`
extension versions, the loader's expectations of `__driDriverGetExtensions` and the driver-private
contract) changed materially across those seven major releases. Mesa's own documentation treats the
loader and driver as a matched set; mixing them is not a supported configuration, and the failure mode
is precisely "failed to open <driver>".

The staged driver does export `__driDriverExtensions` and `__driDriverGetExtensions`, which is why the
file is found and attempted rather than ignored — the rejection happens deeper, inside version
negotiation.

## What this means

The projection supplies a **modern software Mesa stack for a 2016 compositor and a 2016 EGL**, and the
one thing that cannot be mixed is exactly the piece that matters here: the DRI driver.

Two coherent fixes, and only one of them is small:

| Option | Change | Trade-off |
|---|---|---|
| **A: matched older driver** | Supply a `swrast_dri.so` from **Mesa 11.2.1** (the vendor's generation) | Smallest conceptual change: the rest of the vendor stack stays untouched. Cost is obtaining or building a 2016 Mesa swrast for x86-64 — a build task, not a config change |
| **B: matched newer stack** | Replace the vendor EGL with a **complete, self-consistent Mesa 18.2.8 set** — `libEGL.so.1`, `libglapi.so.0`, `libGLESv2` as needed, plus the matching `swrast_dri.so` | No 2016 build needed, and `LD_PRELOAD=/usr/lib/libEGL.so.1` means the replacement is the one actually used. Cost is replacing four vendor libraries rather than adding one, and the apps' expectations of vendor EGL extensions must be checked |

Neither should be attempted half-way. Mixing a 2016 loader with a 2026 driver is what the last two runs
were, and it fails deterministically.

## What must NOT be concluded

- **Not** that the earlier dependency finding was wrong. It was correct and it was fixed; runs 5 and 6
  prove it was incomplete, not mistaken.
- **Not** that the app is at fault. It never gets an EGL display; that is decided before any app code
  runs.
- **Not** that the layout gap disappeared. `visibility(0)` / `layer(nil)` from `docs/kernel/44` remains
  a separate, open gap. Fixing EGL gives a committed buffer, not a visible layer.

## Run 5 and 6 export outcomes

Both runs: `BINDING_FAILED phase=start reason=pid_not_running`. The app process had exited before the
`EXPORT_AT_S = 30` snapshot in both. Those are instrument-failure verdicts and license **no conclusion
about Home**; they are recorded only so the runs are not silently dropped.

Display captures in both runs succeeded (129,844 B, `shooter_rc=0`) and showed the same shell-UI frame.

## Next exact action

Choose between A and B **before** another run, and state the choice as a projection decision:

1. Determine whether a Mesa 11.2.1 `swrast_dri.so` can be obtained or built for x86-64. If yes, A is
   the smaller divergence and should be preferred under the project's projection-side-fix rule.
2. If not, specify B properly: the exact four-or-so vendor libraries to replace, their provenance, and
   the check that the vendor apps still find the EGL entry points they use.

Either way, the run after that has a binary pre-committed observation: **does `wl_surface.attach(...)`
appear before `commit()`?**
