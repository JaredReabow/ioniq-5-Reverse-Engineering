# The reordered call lands on a stable, preload-complete instance — and the frame still does not lay out

Date: 2026-11-06. Doc 16 showed the power-on call was landing on the doomed instance. This run polls for
pid stability **before** the call, then calls, then captures.

## The run, in the order earned

```
[stable] NAME_OWNED=yes at +100s
[stable] PID_CHANGED 2324 -> (none)         ← the doomed instance
[stable] PID_CHANGED 2497 -> 2634
[stable] PID_STABLE_GATE=yes pid=[2634]     ← same pid across two samples 15 s apart
[stable] CALLING_AGAINST pid=[2634]
[stable] SET_POWER_SENT
[stable] AFTER_CALL pid=[2634] (was 2634) preload=[int32 1]
[stable] SAME_INSTANCE=yes
[stable] CAP_30s  pid=[2634] bytes=129844
[stable] CAP_60s  pid=[2634] bytes=129844
[stable] CAP_120s pid=[2634] bytes=129844
```

So the reordering **worked mechanically**: the call went to the instance that survived the deregister
race, that instance stayed up (`SAME_INSTANCE=yes`, same pid through +120 s), and preload reads
`int32 1`.

## But the frame is not the laid-out home screen

All three captures are **129,844 bytes**, which is the **early background** — decoded: 1920×720,
~98 % `#010001` black with grey text tones (`#E1E2E2`, `#535B63`, `#9EA3A8`), **no blue title bar**.
That is the compositor's default surface, not the app's standby face (doc 11's 144,501-byte frame with
the blue bar and logo) and not the 16,062-byte laid-out frame.

## The honest reading

Per the decision rule in this thread: the surviving instance is stable and preload-complete, yet it does
**not** lay out. The reordering removed the deregister race as the blocker and the frame still did not
appear — so the blocker is a **different** reason, downstream of the preload gate.

## One observation, labelled as a candidate not a conclusion

Doc 11's standby-face capture (144,501, blue bar) was taken by the *old* monitor, which placed the app
surface with `ivi-wm <surface-id>` immediately before capturing. This run does not place the surface, and
the frame is the background. So **surface placement** is a candidate next check: the app may be stable
and preload-complete but not yet placed/visible. That is the thing to test before concluding anything
about the launcher deadline (option 2).

## Files

- `work/vm/kbuild/boot42-stable.log` — the run.
- `work/vm/kbuild/ws/partimg-build/stable-call.sh` — the reordered script.
