# Serial console login, captured from the far side of ttyS2

`ttyS2-login-prompt-2026-11-04.log` is the raw bytes the projection's `/dev/ttyS2` emitted after running the vendor's own
`/etc/esinit_agetty.sh` unmodified:

```
OpenEmbedded 1.0 (none) ttyS2

(none) login:
```

Everything needed to reproduce it:

- the guest kernel and rootfs are the recovered EU `260128` image, booted by `tools/uk_fw/vm_boot.py`;
- `/sys/module/micom/parameters/secure_console` read **0** at the time, with the vendor `micom` module loaded, so
  `/lib/systemd/esinit` leaves `secure_console_disable` in place and does not delete the device;
- the script run was `/etc/esinit_agetty.sh` verbatim, i.e. `setsid /sbin/agetty -8 -L ttyS2 115200 xterm` — the `-a root`
  autologin line above it in that file is commented out, so the login is authenticated;
- the bytes were captured with `-chardev file,id=t2,path=...` attached to `isa-serial,index=2`, which is how the harness observes a
  guest serial port without a terminal.

This is a login prompt, not a shell: the password is the single SHA-512 entry for `root` in `/etc/shadow.Global`, whose salt is
identical on every unit built from this image. See `Ioniq5-VULNERABILITIES.md` V-049.
