# The vendor userspace boots: systemd as PID 1, udev up, login prompts reached

This is the step that had been blocking every USB and hotplug question in this project. Until now the projection ran either the
research `/init` (no udev, no systemd) or `/lib/systemd/esinit`, which stops before systemd on a single-partition clone. It turns out
esinit is not the only way in.

## Recipe

Boot the **vendor kernel** (`boot/bzImage-4.1.27-abl`, see `docs/vm/vendor-kernel-boot.md`) with **systemd itself as init**:

```python
vb.KERNEL_SHA256  = hashlib.sha256((ws / 'bzImage').read_bytes()).hexdigest()
vb.INIT_CHOICES   = ("/init", "/lib/systemd/esinit", "/lib/systemd/systemd")
vb.run(ws, True, command, timeout=240.0, memory_mib=2048, init='/lib/systemd/systemd')
```

Both assignments are module-level overrides made from the calling script; `tools/uk_fw/vm_boot.py` is not edited.

## What it produces

```
systemd[1]: Listening on udev Control Socket.
[  OK  ] Listening on udev Control Socket.
systemd[1]: Listening on udev Kernel Socket.
[  OK  ] Listening on udev Kernel Socket.
systemd[1]: Starting udev Kernel Device Manager...
```

and the target list settles at:

```
Basic System.
Local File Systems (Pre).
Local File Systems.
Login Prompts.
Paths.
Slices.
Sockets.
Swap.
```

So `systemd` runs as PID 1 from the **authentic rootfs**, `systemd-udevd` is active, and **login prompts are reached** — which is also
the first time the stock console path has existed end to end inside the projection rather than as an isolated `agetty` invocation.

Twenty-four units fail, all of them explained by missing hardware: `pas-daemon` (persistence admin), `connman` (no NICs), `TimeManager`
(depends on the former), and `tmp.mount` does not exist as a unit on this image. None of that blocks Basic System or udev.

## What this unblocks

- **V-014's missing tail.** `SYSTEMD_WANTS` only means anything with systemd running. Now a device property naming a unit can
  actually be acted on, so the question "does a crafted device property start the installed root-shell unit" is measurable here.
- **udev without hand-holding.** The standalone `systemd-udevd` recipe in `tools/uk_fw/guest/run-udev-standalone.sh` was a workaround;
  under systemd the daemon is started by the unit as it is on the vehicle.
- **The USB media path.** Mounting a stick and running the indexer was previously blocked on orchestration, not parsing.

## Does not settle

`esinit` itself still stops at `[FDE] ***** use fstab for non FDE`, because it recovers eMMC partitions `p8`–`p12` and our clone has one
partition. Starting systemd directly bypasses esinit rather than fixing it. A faithful boot of the **vehicle's own init sequence**
therefore still needs a partitioned image — that remains the honest remaining gap, and it is a different question from "does the vendor
userspace run", which is now answered yes.

## Media-parsing probe results (same session)

- A USB stick with a real ext4 filesystem mounts at `/media/usb/` (`MOUNTED=1 FILES=lost+found probe.asf readme.txt`). It must be built
  without `metadata_csum`, which kernel 4.1 rejects: `EXT4-fs (sda): Couldn't mount because of unsupported optional features (2000)`.
- **Correction to an earlier note in this repository:** the indexer's ASF plugin **is** present at
  `app/lib/lightmediascanner/plugins/asf.so`. An earlier conclusion that it was absent came from looking for `lms_asf.so`, which is not
  the filename. The ASF parser therefore does exist in the indexer, not only in `libgstasf.so`.
- The indexer starts and runs as **uid 0**, but it does not scan: it blocks on the DLT FIFO until `dlt-daemon` is running, and once that
  is satisfied it still opens no files and loads no plugins, because it expects the session bus and the media manager to drive it
  (`org.lightmediascanner`, `lightmediascannerctl scan`). So the parser's behaviour on a crafted file is **not yet demonstrated**; what
  is established is that the component exists, runs as root, and is reachable by path once the surrounding service mesh is up.
