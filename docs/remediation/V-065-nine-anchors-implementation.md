# V-065 / remediation item 16: the exact change, and how to verify it

Date: 2026-11-06. Produced as the first action of the four-planner plan (`docs/planning/AGREED-NEXT-STEPS.md` §4), which put
this item first for risk reduction per unit of effort. **Specified, not yet applied** - applying it edits four vendor boot scripts
and nine symlinks inside a working image, and a broken clone costs more than a spec.

## The problem, restated exactly

Nine `/etc` paths are symlinks into the world-writable `/tmp`:

```
/etc/passwd                 -> /tmp/passwd            /etc/ecnr/config   -> /tmp/ecnr_config
/etc/shadow                 -> /tmp/shadow            /etc/fstab         -> /tmp/fstab
/etc/shells                 -> /tmp/shells            /etc/resolv.conf   -> /tmp/resolv.conf
/etc/xdg/weston/weston.ini  -> /tmp/weston.ini
/etc/front_lcd.png          -> /tmp/front_lcd.png     /etc/rear_lcd.png  -> /tmp/rear_lcd.png
```

The reason is sound - the root filesystem is read-only at runtime, and generated configuration needs a writable home. The mistake is
only the destination: `/tmp` is `1777`.

## The change, counted

**Four files carry the 23 references:**

```
lib/systemd/esinit                the earliest writer, and where /run is mounted
etc/smack_setup.sh
etc/setup_ecnr_engine_db.sh
etc/install_westonPngLogo.sh
```

| path | references |
|---|---|
| `/tmp/front_lcd.png` | 11 |
| `/tmp/ecnr_config` | 3 |
| `/tmp/passwd` | 2 |
| `/tmp/shells` | 2 |
| `/tmp/fstab` | 2 |
| `/tmp/shadow` | 1 |
| `/tmp/resolv.conf` | 1 |
| `/tmp/weston.ini` | 1 |
| `/tmp/rear_lcd.png` | 0 (the symlink exists; nothing writes it) |

## The edit

1. **Create the directory root-only, as early as possible** - in `esinit`, immediately after `/run` is mounted:
   `mkdir -p /run/etc && chmod 700 /run/etc`. Repeat defensively in the three other scripts (one line each) because the launch
   order of those is not guaranteed.
2. **Repoint the producers**: in those four files, replace `/tmp/<name>` with `/run/etc/<name>` for the nine names above. That is a
   mechanical substitution and every occurrence is listed in the table, so it can be checked by count.
3. **Repoint the anchors**: the nine `/etc` symlinks now name `/run/etc/<name>` instead of `/tmp/<name>`.

**Trade, stated:** anything outside these four scripts that reads `/tmp/passwd` or `/tmp/weston.ini` **directly** would stop finding
it. The grep for those literals across the image is the check, and it should be run before the change, not after.

## How to verify in ten minutes on a unit

1. `ls -l /etc/passwd /etc/shadow /etc/shells /etc/fstab /etc/resolv.conf` - each should name `/run/etc/`.
2. `ls -ld /run/etc` - mode **0700**, owner root.
3. `ls -l /tmp/passwd` - **should not exist**.
4. As any non-root process: `touch /tmp/passwd` should create a file that **is not** the account database, and `getent passwd`
   should be unchanged by it.
5. Append a line to `/run/etc/passwd` as root and confirm `getent passwd` sees it - proving the anchor still works after the move.

**Step 4 is the one that matters** - it is the difference between "the file moved" and "the weakness closed".
