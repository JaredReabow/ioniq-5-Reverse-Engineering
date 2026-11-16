# The duplicate instance was the cause of both error families

> **WITHDRAWN 2026-11-05.** The conclusion below is wrong. The zero counters came from a **freshly
> truncated log** belonging to a new instance (`initdone=[0]` was the tell), not from the errors being fixed.
> A later run with **one** instance and a real 99,902-byte log still shows the Wayland fatal error and the
> `DB UPDATE COMMIT FAIL`. See `15-retraction-duplicate-not-confirmed.md`.


Date: 2026-11-05. Test: wait for the application, then keep killing every instance except the oldest, and
compare the two error counters.

## The result

```
M1_BEFORE=[2527 2460]                two instances, as measured in earlier runs
M1_KILLED=2460 kept=2527   (x6)      the kill did not take - the same pid reappeared
M1_KILLED=2527 kept=2671   (x3)      then the survivor itself was replaced
M1_AFTER=[2671]                      ONE instance remains
M1_p1=129,844 pid=[2671]
M1_p2=129,844 pid=[2671]             stable: same pid across both captures
M1_COUNTS  wlerr=[0]  commitfail=[0]
```

**With a single instance, both error families go to zero:**

| counter | with two instances | with one |
|---|---|---|
| `invalid object` / `fatal error` (Wayland) | 2-3 per run | **0** |
| `DB UPDATE COMMIT FAIL` | 23 | **0** |

That confirms the hypothesis from the previous entry: **the duplicate process caused the Wayland fatal error
and the SQLite commit failures.** Everything I diagnosed in the two entries before that - the missing database
directory, the empty `WidgetSettingFront` table - was a symptom of two processes competing, not a cause.

## Two things this run did not achieve, and one hazard it exposed

- **The application still is not painting.** Both captures are **129,844 bytes - the early background** - even
  with one stable instance. So the duplicate explains the errors but not the absence of the UI: the surviving
  instance was the *loser* of a race whose sibling was killed mid-flight, and it has no surface of its own.
- **`busybox kill` did not remove the target.** The same pid (2460) was reported killed six times and kept
  running; only a later generation (2527) was replaced by 2671. Whatever supervises the application restarts
  it, and plain `SIGTERM` is evidently not enough. **Any future test must use `kill -9` and verify by pid, not
  by assuming the kill worked** - I reported "KILLED" six times for a process that was still alive, which is
  the same class of mistake as trusting a capture without looking at it.

## The next test, now clean

**Kill both instances with `SIGKILL`, confirm the process list is empty, let the launcher start exactly one,
and only then capture.** If the application then paints and logs no errors, the projection reaches its
steady state and the remaining question is the layout/power one. If it paints nothing, the surface-ownership
question is next and this project finally has a stable platform to ask it from.
