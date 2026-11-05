# Retraction: the duplicate is not the cause; the zeroes were a truncated log

Date: 2026-11-05. This withdraws the conclusion in
`14-duplicate-confirmed-as-the-cause.md`.

## What I claimed

That reducing the application to a single instance drove both error families to zero -
`wlerr=[0]  commitfail=[0]` - and therefore that the duplicate process caused the Wayland fatal error and the
SQLite commit failures.

## Why that was wrong

That run also reported **`initdone=[0]`** - not one `AppHome Init Done` line in the log - and I did not stop
to ask what a log with no initialisation line actually was. It was a **freshly created log belonging to a
new instance**, because the launcher's redirection truncates the file on each start. Counting errors in a file
that has just been replaced measures the *new* file, not the application's history.

**The counter-observation, from a run with one instance and a log that is demonstrably real:**

```
V2_PIDS=[2654]   LOGSZ=99902   LINES=745
```

99,902 bytes, 745 lines, one instance - and the tail still contains:

```
wl_display@1: error 0: invalid object 19
[FTL] [QtMsg] The Wayland connection experienced a fatal error (Invalid argument)
[ERR] AppHomeModel::SaveSetupLayoutDB ][ 6254 ] DB UPDATE COMMIT FAIL
```

**With a single instance, both failures are still there.** The duplicate is therefore **not**
the cause of either. The previous entry's table of "two instances -> one instance" was comparing a real
log against an empty one.

## What survives

- Duplicate instances **do** occur and are worth noting as an observation (`2535 2465`, `2581 2500`, `2628 2561`).
- They are, at most, a **contributing** factor. Nothing measured supports them being the cause.
- The two error families are real, occur **around 00:02:29** in every run (a specific point after start), and
  are **present with one instance**.

## The methodological failure, in plain terms

I compared counts from two files **without checking that the files were the same kind of thing**. A process
that recreates its log on start makes every count meaningless unless the log's size and the instance's pid are
recorded alongside it. The evidence was in my own output - `initdone=[0]` - and I read it as "good news" rather
than as "the log is empty".

## Next

The failure is now pinned to a moment: **~00:02:29**, immediately after `AppHome Init Done`, where the
application both fails a database commit and receives a Wayland `invalid object` on `wl_display@1`. The next
measurement is not "how many instances" but **what the application does at that instant** - the last 30 log
lines *before* the fatal error, in a run whose log size and instance pid are recorded with the counts.
