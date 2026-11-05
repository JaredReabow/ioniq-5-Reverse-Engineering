# FROZEN BRIEF — decide the next best steps

Date frozen: 2026-11-05. Do not add facts; if you need something that is not here, say so and
name what would settle it.

## Engagement

Authorised security research on a Hyundai Ioniq 5 (LGE **Gen5W** / S5W_L) infotainment head unit.
Installed build `NE_E.EUR.S5W_L.001.001.260128` (EU, Jan 2026), x86-64 Linux, kernel `4.1.27-abl`
(Apollo Lake), SMACK MAC, glibc 2.23-era, Qt 5.4, no SELinux enforcing.

**Standing goal:** an end-to-end stock physical-device → arbitrary code / root entry vector.

Hard constraints, unchanged:

- **No physical device.** A QEMU VM of the vendor kernel + rootfs is the only execution environment.
  The VM is being improved by a separate thread in the same repository; co-ordinate, do not fight it.
- Identify and test exploits. **Do not build final payloads**, do not produce flashing procedures,
  do not bypass signatures operationally.
- Conclusions must bind to exact bytes (hashes, offsets, instruction ranges). No version-only
  promotion of a CVE. "Static flow" is not "runtime reachability".
- Everything is committed and pushed to two remotes.

## What is VERIFIED (measured, not inferred)

1. **Update pipeline is path-based end to end.** `checkHash` (fn `0xe9288` in the `0x7c64` embedded
   updater stage of `AppUpgrade`) stats a path, opens it by path, hashes it, then persists the
   verified **pathname** to `/update/activeResourcePath`. It has **zero `call rel32` callers** — it is
   reached as `CheckHashOnceAppEvent`, a Qt event. Both install-side consumers re-open by path:
   `extract_prepareFiles`, and `DecryptToPIPE` as a separate process in the shell pipeline
   `%1 -d %2 %3 0 | dd`, whose `pclose()` status the parent discards. **No verified descriptor
   crosses from verify to use.**

2. **`AppUpgrade` builds shell commands from `%s` with no sanitisation.** 16 `system()` sites; three
   are privileged filesystem operations: `sudo mount -o loop -t ext4 %s %s`, `sudo umount %s`,
   `sudo mount -o remount,rw %s`, each via `__snprintf_chk` into a 0x400 stack buffer then
   `system()`. A targeted search for any escape/quote/sanitise helper across the whole binary
   returned **zero hits**. The same function then executes `fota_script.txt` taken from inside the
   supplied update image.

3. **Signature-disable switches are present in the binary**: `/update/disableEncryptionUpdate`,
   `/update/disableNaviMapSignatureCheck_20220502` and `_20230207`, and independently
   `/update/force_ua_test.txt` → `### Unencryption Update. ####`. A guard string
   `MASS_PRODUCT or PENETRATION Build mode -> Ignore disableEncryptionUpdate` shows the vendor tried
   to neuter the first switch on production builds.

4. **`iAP2Service-2.0` runs as UID 0** with a 0777 Unix socket at `/tmp/iAp2Socket`. A crafted
   `0x2eff` packet produces heap-metadata corruption; a **symbolised SIGABRT trace with no debugger**
   now proves the abort is glibc rejecting corrupted heap metadata at `free()` in the server thread
   (`iAP2Service+0x2e015` called from `+0x2cc2c`, via `abort+0x16a`). This is the project's one
   confirmed memory-corruption primitive seen at runtime.

5. **Engineer mode exists and is reachable from the UI** (gesture then PIN), runs as root, and its
   `S/W Update` menu contains the Encryption Update toggle that creates
   `/update/disableEncryptionUpdate`. `/etc/shadow.Global` holds `root:$1$7Zo7g2fd$...` (MD5-crypt,
   offline-crackable; ~2,700 H/s in pure Python, no GPU here, ~1,350 targeted candidates already
   failed). `/etc/passwd` and `/etc/shadow` are boot-time symlinks into `/tmp`.

6. **Console/network posture**: `/tmp/secure_console_disable` is touched **unconditionally** by
   `esinit`; only MICOM reporting `secure_console=1` suppresses it, and `set_secure_console()` has no
   in-tree caller (boot-flag only, `secure=` on the kernel cmdline). `dropbear@.service` is gated on
   `/tmp/secure_console_disable`, runs `-s` (pubkey only), with an `authorized_keys` whose private key
   is not in the image. `/etc/ip_setup.sh` hardcodes a debug network `192.168.1.100 gw 192.168.1.1`.

7. **Boot chain crypto is intact**: twelve EU `iasImage*` signatures verified against one RSA key;
   ABL enforces IAS-image signatures. Replacing kernel/boot image is not the easy path.

## What is AMBIGUOUS or UNVERIFIED (do not treat as true)

- **USB-swap TOCTOU**: a published same-platform technique uses a Raspberry-Pi-class USB
  mass-storage gadget to serve a genuine package for the checks, then swap the backing file before
  the installer reads it. Our structure **permits** this, but the decisive question is unanswered:
  **does the boot/rootfs consumer read the `/update/usb/...` medium, or an on-unit copy?** If it
  reads a copy, the technique is refuted for our build. The claimed ~15 s window is *their* number,
  not measured by us.
- **`SrcFullPath` shell injection from the same public project does NOT apply to our build**: our XML
  parser uses `QDomElement::attribute()` (attributes, not child elements), `SrcFullPath` is not a
  parsed attribute name, and in our binary it is a FOTA D-Bus request/reply field compared to `""`.
- **`activeResourcePath`** may be the navigation-map resource, not the boot image. Unverified.
- **Command-injection argument origin**: whether any attacker-controlled string reaches the
  `sudo mount … %s %s` slots is **untraced**. Two guards exist that would constrain it
  (`Filename template does not match`; USB addressed through fixed `/update/usb/...` paths rather
  than the volume label) — neither has been tested.
- **`id3.so` APIC integer underflow** reported by the public project: our plugin is the same size but
  a **different hash** (`0665fe83…` vs their `0067c7e9…`), so the defect must be re-derived from our
  bytes. Not established either way.
- **No proven ring-0/root transition of any kind.** No payload, no flash, no persistence attempted.

## VM side (the other thread's active area; affects what the target can be observed doing)

Five blockers: (1) home-screen image rendering, (2) home↔navigation compositing, (3) client
instability, (4) the service landscape (audio/MMUS, persistence, input, suspend-restart), (5) no GL
renderer (time-boxed; treat as a constraint if it fails).

State: blocker 3 step 1 is **done and measured** — `/etc/ld.so.preload` is consulted (proven with a
bogus path), and a real vendor dynamic binary produced a symbolised SIGABRT trace with no debugger.
Blocker 1 is **unexecuted and its instrument unwired**: `fragnorm`/`tinyuv`/`flipv` never run,
`/tmp/gl-shader-*.txt` never captured, and `shader-fix` appears only inside `gl_draw_trace.c` — no
script creates the markers. Note the trap: `rewrite_shader()` silently returns the source unchanged
when its needle is absent, so a no-op is indistinguishable from a falsified hypothesis. Correct order
is dump-first, variant-second.

## Environment reality

- Host is macOS. Guest tooling: `x86_64-linux-musl-*` works; the system `objdump` does not support
  `-b`. Docker is unavailable. Claude-subscription models and some router models have been failing
  with credit/stream errors this session.
- The QEMU guest cannot run the USB gadget stack (`lge_usb_adapter` oopses in `sbi_apl_commit` — no
  SoC SBI), so iAP2-over-USB and any gadget-based test are **not** reproducible in the VM.

## The question put to you

**Independently decide the next best steps.** Specifically:

1. Given the verified facts above, what is the single highest-value next action, and why is it worth
   more than the alternatives? Be decisive — pick one.
2. Which of the open ambiguities, if resolved, would most change the exploitability picture, and what
   is the cheapest exact test that resolves it (static, VM, or bench)?
3. Is there a route to the standing goal that this brief is not looking at — a different surface or a
   different framing? Name it concretely if so.
4. What should be *abandoned* as not worth further effort, and why?
5. If the honest answer is "the VM must reach state X before any meaningful exploit work can
   proceed", say so and name X and the minimum path to it.

Rules for your answer: cite the numbered facts above (e.g. "per §2") rather than restating them.
Prefer one decisive recommendation over a menu. Say UNKNOWN rather than guessing. Do not propose
anything that requires a physical device, builds a payload, or bypasses a signature operationally.
