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

---

## 3. Run with the directory present: the file is created, the commits still fail

```
D1_DBDIR=[/rw_data/app_data/AppHomeScreen/CustomLayoutDB]   dbfile=[36864]
D1_COUNTS commitfail=[23]  initdone=[1]  wlerr=[2]  pid=[3068]
```

**The database file now exists (36,864 bytes)** - so the missing directory was genuinely blocking creation, and
that part of the chain is closed. **But 23 `DB UPDATE COMMIT FAIL` remain**, and the log prints no
`lastError` text for them even though the binary carries the string for it, so the cause of the *commit*
failure is still unread.

## 4. A second, unrelated failure in the same tail

The log ends with hardware access attempts that cannot succeed here:

```
[ERR] Home_Worker::writeGPIO(QString) ][ 202 ] B.NV:  "0"
[ERR] Home_Worker::writeGPIO(QString) ][ 212 ] Open kernel file failed!, errorNo:  2
[ERR] Home_Worker::writeGPIO(QString) ][ 202 ] B.NV:  "1"
[ERR] Home_Worker::writeGPIO(QString) ][ 212 ] Open kernel file failed!, errorNo:  2
[ERR] Home_Worker::slotSetStatusDrToKernel(QString) ][ 236 ] Open kernel file failed!, errorNo:  2
```

`errorNo: 2` is `ENOENT`: the application is opening **kernel GPIO nodes via sysfs** that do not exist in the
projection. This is expected in a VM without the vendor's GPIO hardware, and it is the same class of gap as
the missing CAN interface: **the application expects kernel-side hardware that QEMU does not provide.**

It is also useful: these are **named sysfs paths we could provide as stub files**, which is cheaper than a
kernel driver - the same substitution trick, one layer lower. The exact paths are the next thing to read
from the binary's `writeGPIO` caller.

## 5. Where this leaves the layout question

- layout DB directory: **fixed in the clone, file created (measured)**
- commit failure: **still present, cause unread**
- the application also expects **sysfs GPIO nodes** that do not exist
- so "why the splash never becomes a home screen" now has two named, unrelated candidates, both in the
  application's own logging rather than in a hypothesis

---

## 6. Pulled the database out of the guest, and it is not the blocker

The file is a valid SQLite 3 database (36,864 bytes, 9 pages, `journal_mode=delete`) and **the schema and the
layout are both there**:

| table | rows |
|---|---|
| `CustomLayoutFront` | **25** |
| `CustomLayoutVersion` | 1 - `(1.9, 1.6, 1.3, 2, 0, 0)` |
| `sqlite_sequence` | 1 - `('CustomLayoutFront', 24)` |
| `WidgetSettingFront` | **0** |
| `WidgetSettingAdvList` | **0** |

A copy is kept at `evidence/vehdata-CustomLayoutDB-empty-widget-tables.db`.

**So the `DB UPDATE COMMIT FAIL` lines are the *widget settings* inserts failing, not the layout.** The
application has a persisted layout of 25 entries and still does not render a home screen.

**That withdraws the suggestion in §1-§2 that the missing directory might explain the splash.** The directory
was genuinely missing and creating it genuinely let the database be created - that part stands - but **the
layout is present and the screen is still splash/standby**, so the database is not what stands between the
application and its home screen.

## 7. What the empty widget tables suggest instead

`WidgetSettingFront` and `WidgetSettingAdvList` are empty while the layout is populated. Two readings:

1. **Two instances at once** (measured repeatedly: pids `2535 2465`, `2581 2500`) both open the same database.
   SQLite in `journal_mode=delete` serialises writers with a file lock, so a second writer gets `SQLITE_BUSY`
   and the application reports exactly the generic "COMMIT FAIL" it logs without the error text.
2. A schema/insert mismatch in this build, which is not supported by any evidence here and should not be
   assumed.

**Reading 1 is testable and cheap:** one instance, no restarts, then look at whether the two widget tables have
rows. If they do, the commit failure is a symptom of the restart loop and not a cause of anything.

## 8. So where is the screen actually blocked

Not the database, and not placement. The application sits in its **splash** with a valid layout on disk and a
manager that reports the vehicle is on. The next thing to test is the **event the application actually
listens for**: `com.lge.avn.appmanager.info` carries a `power_status(int)` **signal** as well as the
`ask_power_status` method, and this project has only ever called the method. Emitting that signal on the
session bus to the application is the untried half of the same interface.
