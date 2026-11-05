# The projection ran every application unlabelled, and the vendor's data model refused it

Date: 2026-11-06. The crash named in `docs/kernel/26` is a **SMACK denial**, and the rule table says why: this projection never applied
the **exec label** the vendor's applications are meant to run under, so `AppHomeScreen` ran as `_` (unlabelled) and was refused the
directory it creates its own database in.

## The denial

```
audit: lsm=SMACK fn=smack_file_fcntl action=denied subject="_" object="Data::commonphev"
       requested=l pid=2990 comm="AppHomeScreen" path="/rw_data/app_data/common/AppPhev/PHEVDB"
```

A **file lock** on the PHEV database - the Battery/Range widget data - denied to an unlabelled subject. The launcher then reports
`appProcessFinishedSlot [11][0][1][11]`: **SIGSEGV**, ~24 s after a fast registration. A userspace null dereference following a
failed open is consistent with the absence of any `segfault at` line for that process.

## The rule the vendor already wrote

`/etc/smack/accesses.d/home`:

```
App::home _                    rwxa--
App::home *                    ----t-        <- traverse on everything, read on nothing
App::home Data::commonphev     rwxatl
```

`/etc/smack_setup.sh:128`: `dir_labeling /rw_data/app_data/common/AppPhev "Data::commonphev"`

So **`AppHomeScreen` is `App::home`**, and `App::home` holds `rwxatl` on `Data::commonphev`. Our instance was `_`, which every rule
above excludes. **The label was never applied by the projection** - not by the vendor, not by SMACK.

## The application is not missing data; it is missing permission to create it

`strings /app/bin/AppHomeScreen` carries `QSQLITE`, `CREATE TABLE IF NOT EXISTS`, `load PHEVDB DB`, `PHEVDB is not Open`,
`CAN NOT load PHEVDB DB !!!`. The database is **the application's own artefact**. It fails because the *directory* is denied, not
because a data source is absent.

## The fix, in the vendor's own vocabulary

The vendor labels executables with `chsmack -e`, exactly as `smack_setup.sh` does for the upgrade binaries
(`chsmack -e "App::upgrade" /update/usb/bin/AppUpgrade`):

```
/sbin/chsmack -e "App::home" /app/bin/AppHomeScreen      # in the image, before spawn - read at execve
mkdir -p /rw_data/app_data/common/AppPhev                # the dir_labeling at line 128 then applies
```

**Checks in order, text before pixels:** `ps -o label=` must print `App::home`; the `object="Data::commonphev"` denial must be
absent from `dmesg`; a `PHEVDB` file must exist that the application created; only then is a frame worth looking at.

## Why this matters beyond the display

**This is the most faithful thing discovered tonight**: the projection had been running the whole vendor HMI with every process
unlabelled, which means the SMACK rules measured in `V-056` have been **inactive in every run so far** rather than merely permissive.
Two consequences, in opposite directions:

- **For the display goal:** the labels are part of the system's behaviour. Applying them is not a substitution - it is closing the
  largest fidelity gap in the projection, and it may change what the layers above do.
- **For the security register:** a finding that read "SMACK is permissive at 0" must be qualified - the runs that showed permissive
  behaviour had **no subject labels to enforce against**. The rule set itself is narrow where it matters: `App::home *` grants only
  `t` (traverse), which is the one place tonight where the vendor's model did exactly what it promised.

**The vector that remains:** an unlabelled process is denied, which is fail-closed and correct. The weakness documented in `V-065`
is unchanged: nine `/etc` anchors still resolve through world-writable `/tmp`, so a file placed there is read as configuration by
the labelled process. **Labeling the app makes that worse, not better** - a correctly labelled `App::home` reading a `/tmp`-sourced
`/etc` file is exactly the trust inversion `docs/trust-anchors-in-writable-runtime-paths.md` describes.
