# Reproducing the authentic-path image

The working image behind `docs/vm/authentic-hmi-apps.md` and `docs/vm/32-managed-home-screen-kia-logo-authentic-2026-11-05.png` is built from three things that are **not** all in this
repository: the shipped vendor image, a partition layout, and a small set of projection-only files. This page says exactly what each of those is and where it comes from, so the result can be
rebuilt rather than remembered.

## 1. The base, which is the vendor's

```
work/decrypted-eu-260128/extracted-safe/mango-rootfs     the decrypted EU 260128 rootfs
boot/bzImage-4.1.27-abl                                   the vendor kernel, shipped in that rootfs
tools/uk_fw/vm_partimg/build-partitioned-image.py         builds the 17-partition GPT image
```

That script produces `work/vm/<name>/rootfs.img` and `layout.json`; nothing in it is ours except the partition table choices documented in `docs/vm/partitioned-image.md`.

## 2. The projection-only files, and where each comes from

These are staged into `p5` by `inject-stockui.sh`. **They are not committed as binaries** — two of them are megabytes and all are rebuildable — so each entry below names its source.

| staged file | size | where it comes from |
| --- | --- | --- |
| `init-authentic-hmi.sh` | 1,551 | ours: opens the MICOM SPI gate, then execs `esinit` (source pattern in `tools/uk_fw/guest/init-esinit-spi.sh`) |
| `applauncher-sh-new` | 1,379 | ours: the vendor `/app/bin/AppLauncher.sh` with the software-GL environment added; the vendor original is preserved as `applauncher-sh-vendor` (296) and as `/app/bin/AppLauncher.sh.vendor` in the image |
| `micom-override.service` | 845 | ours: satisfies `com.lge.car.micom` with `/eng-data-sim` instead of the vendor manager |
| `weston_1920.ini` | 964 | ours: the vendor ini with `backend=headless-backend.so` and `modules=/weston-vm-input.so` |
| `weston-apps-check.sh` | 6,123 | ours: the probe that reports processes, surfaces and the app's view state |
| `weston-vm-input.so` | 30,992 | **vendor**, from the shipped image (`/weston-vm-input.so`) |
| `eng-data-sim` | 48,096 | ours: built from `tools/uk_fw/guest/eng_data_sim.c` by `build-eng-data-sim.sh` |
| `swrast_dri.so` | 12,369,472 | **host**, from a Debian Mesa of the same generation (the vendor image ships only an `i965_dri.so` symlink stub) |
| `libsensors.so.4`, `libedit.so.2`, `libbsd.so.0`, `libstdc++.so.6` | 59,872 / 212,656 / 84,200 / 1,566,168 | **host**, the dependencies `swrast_dri.so` needs at load time |
| `50-vm-gl.conf` | 644 | ours: the drop-in that puts the software-GL environment on `ApplicationLauncher.service` |

**The one hard dependency is `swrast_dri.so` and its four libraries.** Everything else is either the vendor's own file or a script in this repository. A rebuild therefore needs a Debian
Mesa tree of the same vintage; nothing else here is machine-specific.

## 3. What the injection does

```
tools/uk_fw/vm_partimg/inject-stockui.sh <stage-dir> <workspace>
```

It writes the files above into `p5.img`, places the image back into the 36 GiB disk at the offset recorded in `layout.json` (only changed chunks, via `sync-partition.py`), and refreshes
`prepare.json`. `debugfs -R` splits its command string on whitespace, so the script feeds commands from a file and uses space-free relative names — the project has been bitten by that twice.

## 4. Boot it

```
python3.13 tools/uk_fw/vm_partimg/run-byhand.py --init /init-authentic-hmi.sh --smp 4 --timeout 700
```

`--smp 4` is not cosmetic: at two vCPUs the managed `AppHomeScreen` never registers its bus name, because the vendor launches its whole application set at once and two TCG cores cannot
finish Qt startup before the manager's timers fire.

## 5. What you should see

- `Multi-User System` reached, compositor alive (`weston.real`), and `early-background` showing;
- `AppHomeScreen` owning `com.lge.hkmc.avn.appfunc.AppHomeScreen`;
- surface **2080** rendering the vendor interface — title bar, `STR_CAMERA_ALERT2`, and the KIA logo
  (`docs/vm/32-managed-home-screen-kia-logo-authentic-2026-11-05.png`, 120,561 bytes);
- a synthetic click producing `VM_INPUT_FOCUS_BEFORE_MOVE pid=<app> uid=0`.

## 6. The measurement trap that cost five attempts

**Do not capture "the newest surface".** The background's surface is created last, so the newest surface is almost always the splash. Capture each non-layer surface separately and compare
against the two reference sizes this project has measured: **129,844** for the early background and **120,556 / 120,561** for the painted application. The full account is in
`Ioniq5-CHANGELOG.md` §5.0.7 and §5.3.0.
