# iAP2 service — passive admission facts

**Provenance and scope.** Collected in response to a coordination request for the static iAP2 marshal/capacity work. Everything here is either read from the
sanitised EU `260128` extraction (`work/decrypted-eu-260128/extracted-safe/mango-rootfs`) or observed at runtime in a **clone of the pristine vendor image**
(`work/vm/hmiprobe`, whose `rootfs.img` sha256 begins `4953a00568…`; the reference image was not modified, and the clone was only used to add a probe script).
The service was **started manually under this project's research init (`/init`)** — not under systemd — so the runtime label and environment reported below are
*this projection's*, not necessarily the vehicle's. That distinction is marked on every runtime line.

## 1. Service definition (static)

`/lib/systemd/system/carplay_iAP2.service`, verbatim except for blank lines:

```
[Unit]
Description=AVN2.1 - CarPlay iAP2Service Launcher
Requires=dbus-com.lge.car.micom.service usb-automount.service
After=dbus-com.lge.car.micom.service usb-automount.service
Before=ApplicationLauncher.service

[Service]
Environment=LD_LIBRARY_PATH=/app/lib:$LD_LIBRARY_PATH
ExecStartPre=/etc/iap2_mod.sh
ExecStart=/app/bin/iAP2Service-2.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Facts derived from it, each directly from the text above:

- **No `User=`, `Group=`, `CapabilityBoundingSet=`, `AmbientCapabilities=`, `NoNewPrivileges=`, `PrivateTmp=` or `SmackProcessLabel=` is set.** The service
  therefore runs as the default service identity, inherits the default capability set, and is not confined by any unit-level mechanism.
- **No `SmackProcessLabel=`**: the process label comes from whatever launches it (systemd's own domain), not from the unit. There is no per-service SMACK
  confinement declared anywhere in this file.
- `ExecStartPre=/etc/iap2_mod.sh` loads kernel modules before start: `cdc_ncm`, `extcon-intel-usb`, `udc-core`, `dwc3_pci`, `dwc3` (plus commented-out
  `portmux-intel-drcfg` and state writes). The iAP2 gadget modules (`g_iap2.ko`, `usb_f_iap2.ko`, `u_iap2.ko`, `mfd-iap2.ko`) exist in
  `/lib/modules/4.1.27-abl/` but are **not** among the ones this script loads.
- `Restart=always`, and the unit is `WantedBy=multi-user.target` with a live symlink at
  `/lib/systemd/system/multi-user.target.wants/carplay_iAP2.service` — so on the vehicle it starts at boot and is restarted on exit.
- Ordering is meaningful for admission analysis: it starts **after** `dbus-com.lge.car.micom.service` and `usb-automount.service`, and **before**
  `ApplicationLauncher.service`.

## 2. The socket (static path, runtime metadata)

- The path is a literal in the binary: `/tmp/iAp2Socket` (`SOCKET_FILE_PATH [%s]`), and `grep -rl iAp2Socket` over `/app/bin` and `/usr/bin` matches **only**
  `/app/bin/iAP2Service-2.0`. No other shipped binary names it.
- **Runtime, measured (this projection):** the service creates it within 5 seconds of start and keeps it:
  - `ls -l` → `srwxrwxrwx 1 root root 0 Jan 1 00:00 iAp2Socket` — **Unix stream socket, mode 0777, owner root, group root**
  - `/proc/net/unix` → `ffff88005d29c780: 00000002 00000000 00010000 0001 01 97 /tmp/iAp2Socket` — type `0001` (SOCK_STREAM), state `01` (LISTENING)
- **Consequence for the marshal work:** the filesystem imposes **no permission barrier** on connecting. A 0777 mode means any local UID can `connect(2)`;
  whatever admission control exists is *not* file permissions. Under SMACK the only possible gate is the label pair (socket label vs. peer label), and this
  projection cannot answer what those labels are on the vehicle — see §4.

## 3. Process identity at runtime (this projection only)

```
IAP2_PID=718
Uid:	0	0	0	0
Gid:	0	0	0	0
SMACK_PROC=_
CMDLINE=/app/bin/iAP2Service-2.0
EXE=/app/bin/iAP2Service-2.0
```

- **Runs as root (real, effective, saved and filesystem UID all 0).** That is consistent with the unit's absence of `User=`.
- **SMACK label observed: `_`** — the unconfined/default label. This is *this research init's* default, because the probe did not run the vehicle's
  `smack_setup.sh` labelling. It must **not** be read as the vehicle's label for this process.
- SMACK is present in the kernel under this image: `grep smack /proc/filesystems` → match (so the LSM is available, not merely configured).

## 4. SMACK policy relevant to iAP2 (static)

From `/etc/smack_setup.sh`:

| Path | Label | Line |
| --- | --- | --- |
| `/dev/ttyIAP20` | `System::iap20` (`/sbin/chsmack -a "_"` then `dir_labeling … "System::iap20"`) | 20, 116 |
| `/dev/mfd-iap2` | `System::iap20` | 28, 234 |
| `/rw_data/app_data/AppProjection` | **labelling is commented out** (`#dir_labeling … "Data::projection"`) | 166 |

- There are **no `chsmack` calls on application binaries or libraries** in `smack_setup.sh` or `smack-relabel-ro.sh` (searched for `/app/bin`, `/app/lib`,
  `iAP2`): the iAP2 service binary carries no explicit SMACK assignment in these scripts.
- The only iAP2-adjacent labels the policy assigns are on the two **device nodes**, both `System::iap20`.
- `AppProjection`'s data directory is deliberately **unlabelled** in policy (line commented out), which matters for the chain that the static work is
  ranking: the projection client's own data path has no `Data::projection` label to constrain it.

## 5. What this does not answer

- **The vehicle's runtime label for the iAP2 process and for `/tmp/iAp2Socket`.** Both follow from boot-time labelling under systemd, which this projection
  does not reproduce. Obtaining it needs either a run with the vehicle's `smack_setup.sh` applied, or the systemd unit's effective `SmackProcessLabel`
  default, neither of which I have measured.
- **Effective capabilities.** The unit sets no capability options, but the *bounding set* on the vehicle depends on systemd's configuration and the kernel
  default; I have not measured `/proc/<pid>/status` `CapEff` on a systemd boot.
- **Whether `AppProjection` (or any other client) connects to `/tmp/iAp2Socket`, and as which UID/label.** Under this projection the socket is reached by a
  root service; the client side of the admission question is exactly what the static work is deriving.
- **Whether the socket is created unconditionally or only when the USB gadget is present.** In the measurement it appeared within 5 s with no USB device
  attached and `g_usb` gadget modules unloaded, so at minimum it does not require the gadget; the log stayed empty (0 bytes), so the service is silent here.

## 6. Method notes, so these can be reproduced or disputed

- Static reads: `find`/`grep`/`cat`/`strings` over the sanitised extraction; the unit file quoted verbatim from
  `/lib/systemd/system/carplay_iAP2.service`.
- Runtime: a single probe script (`/run-iap2.sh` in the clone) that starts a system bus, launches `/app/bin/iAP2Service-2.0` directly, then reads
  `/proc/<pid>/status`, `/proc/<pid>/attr/current`, `/proc/<pid>/exe`, `ls -l` on the socket and `/proc/net/unix`.
- The socket was **not** present at a 5-second check in the first probe attempt and **was** present within 5 seconds in the second; the difference between
  the two attempts is not established, so treat "created within 5 s" as observed rather than guaranteed.
