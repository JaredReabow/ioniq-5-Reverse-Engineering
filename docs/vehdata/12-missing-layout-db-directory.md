# The application's layout database has no directory to live in

Date: 2026-11-05. Found from the application's own log, then verified against the image.

## The chain

The log, repeatedly:

```
[ERR] AppHomeModel::SaveSetupLayoutDB(QList<QObject*>) ][ 6254 ] DB UPDATE COMMIT FAIL
```

The binary's own strings name the store:

```
/app/data/AppHomeScreen/CustomLayoutDB/
/app/data/AppHomeScreen/CustomLayoutDB/CustomLayoutDB
CustomLayout DB not exist!!!!! Create default
bool AppHomeModel::openSetupLayoutDB()
bool AppHomeModel::createSetupLayoutDBTable()
m_SetupLayoutSQLDB was not Open
```

And in the image:

```
/app/data  ->  /rw_data/app_data          (a symlink, so the store lives on the writable partition)
/rw_data/app_data/                        contains: NMode, common, vbt
                                          AppHomeScreen/  MISSING
```

**There is no `AppHomeScreen` directory on the data partition**, so
`/app/data/AppHomeScreen/CustomLayoutDB/CustomLayoutDB` cannot be created - **SQLite cannot create a
missing parent directory**. Every save fails, and a freshly started instance has no layout to restore.

## What was changed, and where it is recorded

The directory was created in the clone's data partition image (`p11.img`), with 0755 root:root:

```
/app_data/AppHomeScreen/
/app_data/AppHomeScreen/CustomLayoutDB/
```

**This is a modification to the projection, not to the vendor image**, and it belongs in the reproduction
script (`tools/uk_fw/vm_partimg/inject-stockui.sh`) if it turns out to matter - not yet, because the next run
says it does not settle the question.

## The run after the fix, and what it did and did not do

No instruments, one power-on call, captures at +10/+30/+75/+135 s:

```
Z1_a_pre=129,844  pids 2535 2465      TWO instances at once
Z1_b_30=129,844   pids 2535 2465
Z1_c_75=120,562   pids 2676 2535
Z1_d_135=120,562  pid  3326           a third instance later
Z1_ERRS=2
```

**The application still restarts**, and the frame moved from the background to the **standby** face rather
than the splash - so the run is different from the previous one but not *better*.

**So the missing directory was a real defect and not the whole cause.** It is now recorded as fixed in the
clone, and the restart remains unexplained. The next read is the application's log **after** this change, whose
tail this run did not capture - that is the mistake to avoid repeating: I changed a variable and did not
capture the variable's own diagnostic.

## What is not claimed

That the layout DB directory causes or cures the splash. One run with it present still restarts, and the
frame it settles on is standby.
