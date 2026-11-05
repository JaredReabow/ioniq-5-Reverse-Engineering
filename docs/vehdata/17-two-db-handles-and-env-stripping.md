# Two database handles on one file, and the launcher strips the environment

Date: 2026-11-05. Attempt: `WAYLAND_DEBUG=1` for the application, via a systemd drop-in on
`ApplicationLauncher.service` (`Environment=WAYLAND_DEBUG=1`), one change only, no preload.

## Result 1: the variable never reached the application

```
W2_PIDS=[2604]  LOGSZ=90877  LINES=677  INITDONE=0  WLD=[0]
```

**Zero `wl_display` lines in a 90 KB log.** If `WAYLAND_DEBUG` had been in the application's environment the
log would be dominated by protocol traces. It is not, so **`ApplicationLauncher` does not pass its environment
to the application** - consistent with this project's earlier finding that the launcher strips `LIBGL_*` from
its children. Setting the variable on the launcher is not sufficient; a **wrapper around the application
binary** is the mechanism that will work.

## Result 2, which is more valuable: the database failure has a cause in the log

Because the Wayland error did not occur in this run, the captured window is ordinary operation - and it names
the database problem precisely:

```
[6029] openVariantDB()  ] VARIANT DB ALREADY OPENED!!!
[6079] openVariantDB()  ] return true
[6299] SaveVariantDB()  ] BEGIN TRANSACTION FAIL
[6301] SaveVariantDB()  ] DELETE FAIL   QSqlError("1", "Unable to execute statement", ...)
[6225] SaveSetupLayoutDB ] DB DELETE COMMIT OK
[6226] SaveSetupLayoutDB ] DELETE DB DONE  QSqlError("", "", "")
```

**The application holds at least two database handles - a "variant" database and a "setup layout" database -
and one reports `BEGIN TRANSACTION FAIL` with `Unable to execute statement` while the other commits fine.** That
is the shape of SQLite writer contention: a second connection writing while the first holds the lock, which in
`journal_mode=delete` (measured earlier: `delete`) serialises hard.

**This is a defect in the application, not in the projection.** It explains why the widget settings tables stay
empty while the layout table fills: the layout writer wins, the variant/settings writer gets a busy database and
retries in a tight loop that logs `DB UPDATE COMMIT FAIL` dozens of times.

## What this changes about the diagnosis

Earlier entries treated the commit failures as a possible cause of the missing UI. **They are not** - a commit
of the *layout* succeeds in the same window, and the tables that fail are the settings ones. The remaining
candidate for the screen is still the **Wayland `invalid object`**, which happens in *some* runs and not others -
this run had none, and this run's application was alive and working.

## Next, in order

1. **Wrapper around `/app/bin/AppHomeScreen`** to export `WAYLAND_DEBUG=1` (rename the real binary, put a script
   in its place - documented, reversible) so the next run's log carries protocol traces and object 19 becomes a
   named request.
2. Record whether the Wayland error **correlates with the presence of two instances** across runs - there is
   weak evidence for it and now a way to test it without counting an empty file (log size and `INITDONE`
   alongside every count).
