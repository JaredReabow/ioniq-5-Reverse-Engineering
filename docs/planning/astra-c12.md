# Astra C12 — do C now: defer application rendering, and audit the DRI compatibility once before choosing between A and B

Decision consultation, 2026-11-08, after runs 5 and 6. No file was written by the consultation.

## Decision

**C now — defer application rendering and move to the defensive root-access register — with A
preserved as the preferred future rendering route, not B.** Plus **one read-only compatibility audit**
before that choice is finalised.

Astra's framing, adopted: *"This is a sequencing decision — not a declaration that the interactive
objective has been met or should be abandoned."*

## Why

> Neither acquiring an old driver nor replacing the graphics stack immediately produces an interactive
> infotainment system. Even successful EGL initialisation would leave application presentation, IVI
> visibility/layer assignment, and input delivery to establish.

> When rendering resumes, **A** best fits "as close to stock as reasonable." It preserves vendor
> EGL/GLES and supplies a real software-rendering implementation for the virtual hardware environment.
> **B** changes more of the environment whose behaviour you are trying to preserve.

And the correction that mattered most, because it invalidated this session's own conclusion:

> the reported warning and unchanged result after staging four libraries establish that those additions
> did not fix loading. They do **not alone prove** that Mesa 18.2.8 cannot work with the Mesa 11.2.1
> loader. **Mesa release numbers are not themselves a definitive DRI incompatibility test.**

## What "interactive" requires

Astra enumerated the chain: (1) a vendor app initialises graphics and produces buffers, (2) buffers are
committed to the compositor, (3) IVI policy assigns a layer, makes the surface visible and presents it,
(4) an input path delivers events through the guest's device/seat stack, (5) focus and routing deliver
events to the intended app, (6) the app visibly responds.

Currently blocked at (1); (3) is unresolved; (4)–(6) are unimplemented. **Rendering and input are
independent blockers, and presentation policy is a third.**

## The offline check, performed

Astra required one ELF/DRI compatibility audit against the exact library environment `AppLauncher.sh`
selects. Result in `docs/kernel/48-dri-compatibility-audit.md`, and it landed in Astra's **first**
category — a specific dependency/symbol-resolution defect, not an unavoidable ABI conflict:
`libLLVM-6.0.so.1` requires `GLIBCXX_3.4.22`, the vendor `libstdc++6.0.21` stops at `3.4.21`, and the
projection already holds a `3.4.22` build.

## Middle paths Astra assessed

- **Compositor-only change:** *"not a solution to the measured failure"* — software rendering in Weston
  cannot make a Qt client that fails EGL initialisation produce buffers.
- **Process-scoped newer stack:** real but is *"scoped B, not a free solution"*.
- **Loader-path-only fix:** *"conditional, not established"* — helps only if the audit finds a
  resolvable selection/dependency problem, and does not repair an ABI incompatibility.

## Security-status distinction adopted

Keep **statically identified candidate**, **VM-validated behaviour**, and **production-device-validated
path** as separate statuses. **VM root access supplied by the research setup is not a vendor
vulnerability.**

## Next exact action (Astra's)

> Run the single read-only compatibility audit above and classify its result. **Do not acquire or build
> Mesa yet.** Then begin the defensive register with the vendor startup configuration: identify
> root-running services, their entry points and trust boundaries, and trace the highest-exposure
> candidate into its authentication or authorisation logic. Keep the rendering objective explicitly
> deferred and incomplete.
