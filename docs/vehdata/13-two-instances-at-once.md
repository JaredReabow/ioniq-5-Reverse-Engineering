# Two `AppHomeScreen` instances run at once, routinely

Date: 2026-11-05. A test of the `power_status` **signal** (rather than the `ask_power_status` method), with no
instruments other than the screenshooter.

```
G1_APPUP=4s   pid=[2510]
G1_pre=129,844  pid=2572 2510        <- TWO instances before anything of ours ran
G1_EMIT_1=[]    pid=2572 2510        signal emitted twice, no reply expected
G1_s30=129,844  pid=2691 2572
G1_s75=120,565  pid=2691 2572        <- standby frame, not the layout
G1_END          errs=[2]
```

## The finding is in the pid columns

**Two `AppHomeScreen` processes are alive simultaneously, from before the probe does anything.** This has been
visible in several earlier runs and I read past it each time:

| run | pids observed |
|---|---|
| stable run (no instruments) | `2605` alone |
| this run | `2572 2510`, then `2691 2572` |
| earlier | `2535 2465`, `2581 2500` |

**So the "restart loop" is at least partly a *duplicate launch*:** a new instance starts while the previous one is
still alive, rather than the old one exiting first.

## Why that matters more than the power question

Two live instances of a single-instance application explain, without any further hypothesis, the two
failures this project has been chasing separately:

1. **`wl_display@1: error 0: invalid object 19`** - two clients racing the same window/surface ids through the
   same compositor; one of them ends up referring to an object the other has replaced.
2. **`DB UPDATE COMMIT FAIL` on `WidgetSettingFront`** - both instances open the same SQLite file in
   `journal_mode=delete`; the second writer gets `SQLITE_BUSY`, and the application logs the generic failure
   with no error text.

Both are **symptoms of the duplicate**, not causes of anything.

## The signal test itself: inconclusive

Emitting `com.lge.avn.appmanager.info.power_status int32:1` twice on the session bus changed nothing measurable -
the frame went from the background (129,844) to the **standby** face (120,565), not to the layout. A signal from
a client that is not the manager's owner may simply not match the application's subscription, which is the same
caveat as the earlier special-key experiment; **this test does not show the signal is irrelevant, only that this
attempt did not reach the application.**

## The next test, and it is the one that matters

**Stop the duplicate.** With one instance running and no instruments, watch the pid, the application log's
Wayland error count and the widget tables:

1. wait for the first instance, kill the second if a second appears,
2. capture at intervals,
3. re-read `/tmp/apphome-byhand.log` for `invalid object` and `DB UPDATE COMMIT FAIL`,
4. pull the database again and see whether `WidgetSettingFront` has rows.

If the duplicate is the cause, all four signals should improve together. If they do not, the duplicate is a
symptom of something earlier in the launch chain and the launcher's own log becomes the target.
