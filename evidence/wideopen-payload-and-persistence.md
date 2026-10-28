# WideOpen payload chain: persistence and the exact patch set

Status: analysis of public shell scripts and Dockerfiles from the `g4933/gen5w`
projects (`navi_extended/USB_FILES`, `update-patcher`, `update_decryptor`).
Summarised, not reproduced wholesale. No device was used.

## The decryptor invocation (confirmed)

`update_decryptor/entrypoint.sh` drives the vendor binary like this:

```
DecryptToPIPE -d <keyfile> <input> 0 > <output>
```

Facts this settles:

- the switch is `-d`, followed by the key file, the input path, and a numeric
  mode (`0`);
- **output goes to stdout**, which the script pipes onward;
- the script decrypts **every file** it finds in the mounted package, so the
  container — including the package footer — is handed to `DecryptToPIPE`
  whole. Nothing is stripped first.
- the image is Alpine plus `gcompat`, so `DecryptToPIPE` is a **glibc** x86-64
  binary. On a Mac it will need a Linux container or an equivalent glibc layer.

`tools/uk_fw/gen5w_decrypt.py` has been corrected to use exactly this command
(it previously guessed a different syntax and assumed the footer must be
stripped — both wrong).

## Key extraction: the exact mechanism

`USB_FILES/INITIAL_SETUP_SCRIPTS/extract_keys.sh` and
`USB_FILES/EXTREMELY_RISKY_BECAREFUL/spoof_decrypttopipe.sh` together give the
procedure, and a commented line in the spoof script gives the real invocation the
**unit** uses:

```
/app/share/AppUpgrade/DecryptToPIPE -d /tmp/<32 hex chars> /media/usb/1/<model>/AppUpgrade 0 \
    | dd of=/update/usb/bin/AppUpgrade bs=512
```

Facts this settles:

| Item | Value |
|---|---|
| Decryptor path on the unit | `/app/share/AppUpgrade/DecryptToPIPE` |
| Key file handed to it | **`/tmp/<32 hex characters>`**, generated per update |
| Decrypted output target | `/update/usb/bin/AppUpgrade` via `dd bs=512` |
| Mode argument | `0` |

Because the key file is materialised at a random `/tmp` name, a patched decryptor
cannot rely on a fixed path — it has to capture the **argument**. That is exactly
what `DecryptToPIPE_FK` is for.

### The two-stage procedure

1. **Stage 1 (before reboot).** Remount `/` read-write, copy the genuine
   `DecryptToPIPE` to `DecryptToPIPE_OG` (also onto the USB), install the patched
   `DecryptToPIPE_FK` in its place, remount read-only, reboot.
2. **The unit then runs its own update**, calling the patched decryptor with the
   temporary key path. The patch writes that file to the USB as `*_key_*.der`.
3. **Stage 2 (after reboot).** When a `*_key_*.der` is found on the USB, restore
   `DecryptToPIPE_OG` over the patched binary, remount read-only, reboot.

Every stage is guarded by flag files under `STATUS_FLAGS/` and refuses to
continue if the backup is missing — the scripts are written defensively because a
lost `DecryptToPIPE_OG` means the unit can no longer update.

### What is and is not public

The `update_decryptor` repository lists both `DecryptToPIPE` and
`decryption_key.der`, but both are **placeholders**:

- `DecryptToPIPE` is a 129-byte shell script that prints "This is a binary file
  you can find on your headunit" and exits 1;
- `decryption_key.der` is a 193-byte text file reading `EMPTY_DECRYPTION_KEY`,
  with a hint that the key must be obtained from the unit.

So the decryptor and the key remain device-resident. This closes the last hope of
an offline decryption path: nothing in the public toolchain contains the binary or
the key.

## Why this matters for the plan

- The extraction requires **prior code execution** to install the patched
  decryptor, exactly as assumed everywhere else in this programme.
- The decryptor lives at a known path and the key appears at a known *pattern*
  (`/tmp/<32 hex>`), which makes a minimal capture script a few lines long.
- The unit's own update process supplies the key; nothing has to be guessed.
- The scripts go to considerable lengths to avoid destroying `DecryptToPIPE_OG`.
  Anyone repeating this should keep two independent backups before touching that
  path.

## Where AppNavi actually lives, and the manual replacement

`USB_FILES/EXTREMELY_RISKY_BECAREFUL/update_navi_manually.sh` answers a question
left open by everything else: **the navigation application is not on the root
filesystem.** It lives in the navigation partitions:

| Item | Path |
|---|---|
| AppNavi (active map partition) | `/navi/Bin/AppNavi` |
| AppNavi (inactive map partition) | `/navi2/Bin/AppNavi` |

The script performs, for **both** partitions: remount `/navi` (then `/navi2`)
read-write; copy the replacement to `AppNavi-stg`; back the current binary up to
`AppNavi-original.bak`; `pkill -f "AppNavi"`; move the staged file into place;
remount read-only; `sync`; reboot.

### Why this matters

- **The A/B pairing extends to the navigation app.** A replacement must go into
  both `/navi` and `/navi2` or it disappears when the unit switches map
  partitions. A custom `AppNavi` that patches only the active partition runs once.
- It replaces `AppNavi` **directly on the partition**, bypassing the Engineering
  Mode "Update AppNavi from USB" dialog — but it still needs an execution context
  to run in, so it is a *repair and re-install* path, not an entry bypass.
- The `AppNavi-original.bak` backup beside the binary is what the restore script
  expects.

The companion `restore_decrypttopipe_og.sh` does the same for the decryptor:
refuse if `DecryptToPIPE_OG` is missing, remount rw, copy it back, remount ro,
reboot.

## The entry payload

| Script | Role |
|---|---|
| `main_loop.sh` | loop: run `main_loop_code.sh` every 10 s, guarded by a lock file |
| `main_loop_code.sh` | **empty template** — literally `#Code goes here` |
| `install_wideopen_service.sh` | installs the persistent service |
| `wideopen.service` | the systemd unit |
| `wideopen_service.sh` | on-demand runner, invoked by the service |

### `install_wideopen_service.sh`

```
mount -o remount rw /
cp ./wideopen.service /etc/systemd/system/wideopen.service
systemctl daemon-reload
systemctl start wideopen
systemctl enable wideopen
mount -o remount ro /
mkdir -p STATUS_FLAGS/ ; touch STATUS_FLAGS/WIDEOPEN_SERVICE_FIRST_RUN_FLAG
mv "$0" $0_INSTALLED
```

It remounts `/` read-write, installs and enables the unit, remounts read-only,
and renames itself so it does not repeat.

### `wideopen.service`

```
[Unit]  Description=WideOpen service ; After=network.target ; StartLimitIntervalSec=0
[Service] Type=simple ; Restart=always ; RestartSec=5 ; User=root
          ExecStart=/bin/bash -c "find /media/usb -iname 'wideopen_service.sh' -exec bash {} \;"
[Install] WantedBy=multi-user.target
```

**This is the whole persistence model.** A root-owned, always-restarting service
that every five seconds searches any mounted USB for a file named
`wideopen_service.sh` and executes it.

## Consequence that should be stated plainly

Once that unit is installed, **anyone who plugs a USB stick into the vehicle with
a file called `wideopen_service.sh` gets root code execution**. There is no
authentication, no signature check and no interaction beyond inserting the stick.

On a bench unit that is a research facility. If this unit or its image ever
returns to a vehicle, it is a live, unauthenticated root backdoor on a road-going
computer. That is worth writing down before the tooling gets copied around.

## The exact patch set (Engineering Mode and access)

`update-patcher/update_patcher.sh` performs these edits on the decrypted rootfs,
and they are the concrete form of the bypass described in the public docs:

| Target | Change |
|---|---|
| `AppEngineerMode_PinCodeKeypad.qml` | `enterMenu == 21` → `enterMenu`; `enterMenu == 11` → `enterMenu` (PIN check removed) |
| every `*.qml` | `checkSOPVersion() ===` → `checkSOPVersion() !==`; the no-space variant too; `: AppEngineerModeEngine.checkSOPVersion()` → `: false` |
| `/usr/sbin/dropbear` | symlink to `dropbearmulti` if absent |
| `/etc/systemd/system/` | install `wideopen.service` + `multi-user.target.wants` symlink |

Repack, exactly:

```
tar --format=ustar --exclude="*.DS_Store" --numeric-owner -cf - ./ -P | gzip
```

This confirms `tools/uk_fw/rootfs_patch.py`'s format choices and adds one detail
it should mirror: the `*.DS_Store` exclusion.

## Why this matters for the plan

- The Engineering Mode patch is **the thing that removes the gate**. If a patched
  rootfs can be installed once, Engineering Mode stays available regardless of
  build, and the AppNavi USB install can be repeated at will. The entry problem
  collapses to the *first* install.
- The payload is operator-supplied: `main_loop_code.sh` is empty by design, so
  the "tool" is a scaffold. Copying `DecryptToPIPE` and the key file is a one-line
  script, not a research problem.
- The decryptor's real CLI removes the last guess from the offline workflow.

## Remaining dependency

Unchanged: you need one successful install of a replacement `AppNavi`, or a
patched rootfs, before any of this runs. The scripts assume that execution
already exists.
