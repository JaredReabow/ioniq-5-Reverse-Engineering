# Findings summary — Gen5W (mango) VM, dev mode, hidden menus, and entry vectors

Consolidated summary of the state of this project as of 2026-11-04. Everything here is either measured in this
project or explicitly attributed to an external source; each section says which.

---

> **Status note (2026-11-05).** This page is a summary written mid-investigation and is kept for its reasoning. Several of its claims have since been narrowed or corrected by
> measurement; where they disagree, `CURRENT-STATE.md` and `Ioniq5-VULNERABILITIES.md` are authoritative and this page carries a correction note. The three that changed most:
> the MAC layer's rules **do** ship (27 files, 636 rules) but whether applications carry labels is unverified; the data "encryption" is flag-gated and may never engage, which
> makes "unencrypted" the likelier field state; and the engineering-mode faceplate `IpConfigShell` is **dead QML** on this build rather than a shell.

## 1. What works

| Capability | State | Evidence |
| --- | --- | --- |
| Vendor kernel boot in QEMU | working | documented ABL boot-parameter adaptation |
| Vendor userspace (EU `260128`) | working | decrypted offline, booted, mounted read-only |
| Launcher, driver-select, safety notice | working | authentic screens captured |
| Home screen application | **renders** | creates a surface, commits buffers, placed via `ivi_window_manager` |
| Clean frame on the vendor compositor | **working, reproduced 2026-11-04** | `docs/vm/24-clean-vendor-backend-2026-11-04.png` |
| MICOM transport + boot-info profile | working | `micom-dbus-sim`, 35-byte authentic profile served |
| Engineering mode | **launchable, renders striped under our backend** | `docs/vm/23-…png` |

## 2. Why the screenshots were striped — and the answer

The stripes were **our own research backend's artefact**, not the application's. The comparison is two
measurements:

- vendor `headless-backend.so`, **single output** → clean frame, smooth wave background, crisp text (twice: the
  archived `docs/vm/13` and the reproduction `docs/vm/24`).
- our `ias-backend-soft.so`, **ten outputs** → diagonal stripes in every run.

Six sampling-side experiments (wrap state forced, `u` negated, axes swapped, coordinates normalised, divided by
texture size, collapsed 1000×) had no effect **because none could have** — the corruption is downstream of
everything they touched. The remaining question is bounded inside `ias-backend-soft.c`: ten outputs tiled at
`x = index × 1920`, an application surface reported as 1926×753 on screen 9, and one output actually composited.

## 3. DEV mode — what it is

`checkSOPVersion()` returns `cmp`/`sete` on the int at `engine + 0x13c`. The only write to that field is in
`setEngType()`, which — **in this `260128` build — writes 1 unconditionally**; the comparison against
`/tmp/app/bin/AppEngineerMode` only changes which message is logged. So:

- **The develop state is not reachable by relaunching the shipped binary from `/tmp`.** Measured: the launcher
  did run the copy (readlink confirmed), and the state did not change.
- The container is real: `AppLauncher` prefers `/tmp/app/bin/AppEngineerMode` for app id **301**, and
  `AppDMClient` constructs that path from a **`<usb>/VarUpgrade`** directory subject to key/hash checks.
- What dev mode unlocks is the full engineering update list, including **Encryption Update**, which calls
  `UpgradeVerInfo.enableUpdateFile(10)`.

## 4. Hidden menus and how they are triggered

| Menu | Trigger | Status |
| --- | --- | --- |
| **Engineering mode** | Settings → General → About, tap the software version **5–10×** (or the blank area at the bottom), then enter a PIN | **documented by the external project**; the equivalent code path exists in our image (`AppSetup` compares app id `0x12D` at `0x573194`) |
| Engineering PIN — engineer | **`19491003 *(see correction below — not valid on this build)*`** | external; verified as unsalted SHA-256 hashes in the binary. Overlaps this register's **V-041** |

> **Corrected 2026-11-04:** the value `19491003` comes from the sibling platform and does **not** match this build. `AppEngineerMode` carries exactly two SHA-256 constants; the engineer one matches a different vendor default code, and the dealer one is `2400`. Both were verified against those constants. The plaintext engineer code is withheld from this public tree as V-041 requires.
| Engineering PIN — dealer | **`2400`** | external; same |
| `S/W Update → Encryption Update` | inside engineering mode | our binary analysis and their guide agree; creates `/update/disableEncryptionUpdate` |
| `IpConfigShell` | inside engineering mode | external: described as shell-command execution |
| Develop state | a develop build placed at `/tmp/app/bin/AppEngineerMode` by a VarUpgrade deployment | launcher hook is ours, deployment is theirs |

**The PINs and gesture have not been tested by this project** — they come from the external repository, whose
model differs (Kia Cerato 2022 AU vs Hyundai IONIQ 5 EU `260128`). They are platform-plausible because the code
path (`AppSetup` → app id 301) exists here, but that is inference, not measurement.

## 5. Entry vectors, ranked by what they require

| Vector | Requires | Status |
| --- | --- | --- |
| Engineering mode via the About-screen gesture + PIN | nothing but the on-screen UI | **promising, untested here**; the strongest stock-unit route |
| Encryption Update toggle | being inside engineering mode | reachable if the above works; **ignored on MASS_PRODUCT builds** per `AppUpgrade`'s own message |
| USB `VarUpgrade` deployment of a develop build | valid keys/hashes for the VarUpgrade container | evidenced literals, end-to-end flow inferred |
| **USB media file (`.wma`/ASF, `.mkv`/EBML)** | a crafted file and a USB insert | **the strongest exploit class**; see §6 |
| One-byte patch `0x7372a6` `74`→`EB` | firmware modification | identified, not applied |
| Modified firmware via update | replacing the trust anchor first (**V-034**) | needs privileged write first |
| Root shell over the debug network | the `dropbear` binary, which is **absent** from this image | dead end here; the vendor `authorized_keys` ships |
| USB stick carrying an executable | something that executes from the stick | dead end — `usb-automount` only mounts and reports |

## 6. USB media parsers — the vector worth the effort

An external, independently published report on this platform family documents **USB-media-triggered root code
execution with no user interaction beyond insertion**:

- **GStreamer ASF demuxer stream-array overflow** (they cite CVE-2026-2920): out-of-bounds write in the media
  engine, which **runs as root**; up to 127 streams per ASF file.
- `lms_asf.so` heap over-read, integer underflow and missing return-value check in the lightmediascanner ASF
  plugin (their ZD-ASF-1/2/3), reachable from a crafted `.wma`.
- `libebml 1.3.4` heap overflow (CVE-2021-3405) for `.mkv`.

**What our image actually contains** (measured here):

```
/usr/lib/gstreamer-1.0/libgstasf.so     present — built from gst-plugins-ugly 1.8.3, GstASFDemux
/usr/lib/liblightmediascanner.so.0.5.1  present
/usr/share/dbus-1/services/org.lightmediascanner.service   D-Bus activatable
/app/bin/lightmediascannerctl           present
lms_asf.so                              NOT present — **but the plugin is `asf.so`, which ships** (correction, see §6)
libebml.so.4                            present (major 4, newer than their 1.3.4)
```

So the **GStreamer 1.8.3 ASF demuxer** and a **D-Bus-activated lightmediascanner 0.5.1** are both here, while
their specific `lms_asf.so` plugin and libebml 1.3.4 are not — **but this image ships `asf.so`, the plugin's actual filename, so the indexer does have an ASF parser**
(correction, 2026-11-05). The media-parser class is therefore **live but not
identical**: the same product family, different components and versions. That is a concrete research lead rather
than a copyable exploit.

## 7. What was imported, and what was deliberately not

Imported analysis and scaffolding (verbatim, with provenance) is in
`evidence/external-cerato-au-jailbreak/`. Deliberately **not** imported: their `.ver` signature files,
`fb_pwn.c`, `pwn.sh`, hardcoded framebuffer offsets and image blobs — all keyed to their build and liable to
mis-target this image. Their exploit builders are a scaffold only; any regenerated exploit must take offsets from
this image.

## 8. Register reconciliation

| Their finding | This project's entry |
| --- | --- |
| Update trust anchor / TOCTOU on a writable root | **V-034** (duplicate **V-044**) — same issue, not double-counted |
| Engineering PIN from static unsalted hashes | **V-041** — same |
| ASF/GStreamer media parser RCE | **new candidate, filed as V-047**, hedged: components present here, exploit not attempted |

## 9. Dead ends, recorded so they are not retried

- USB stick carrying an executable — nothing executes from a mounted stick.
- Modified firmware through a normal update without replacing the trust anchor — RSA verification rejects it.
- USB Ethernet adaptor on this image — no SSH daemon ships.
- `/tmp` dev-path relaunch on this build — writes the SOP state unconditionally.
- Sampling-side explanations for the stripes — six experiments, all refuted.
- Killing `early-background` to clear the screen — manufactures a striped artefact.

## 10. Next steps

1. **Test the About-screen gesture + PIN in the projection** (input injection) — the cheapest stock-unit route and
   entirely untested here.
2. **Fix the ten-output backend's compositing** so clean captures are routine, not a special recipe.
3. **Characterise the media path**: does inserting a USB volume activate `org.lightmediascanner.service`, and does
   the ASF demuxer run as root? That converts V-047 from candidate to measured.
