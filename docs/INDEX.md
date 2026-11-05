# Documentation index

The tree grew to thirty documents during one long session. This page says what each one answers, so nobody has to open them to find out. Start at **the four that
matter** unless you know what you are looking for.

## The four that matter

| Document | Answers |
| --- | --- |
| **`CURRENT-STATE.md`** | What works, what is blocked, what to do next. The entry point; everything else is detail behind it. |
| **`REMEDIATION-REPORT.md`** | Ten findings ordered by **cost to fix**, each with evidence, exposure, fix and verification. The document to put in front of a platform team. |
| **`MEASUREMENT-DISCIPLINE.md`** | Eight rules distilled from nine corrections this project made, each with the concrete case. Read before trusting any number here. |
| **`../tools/check_all.sh`** | Runs every consistency check: register numbering, the append-only history invariant, and 1,300+ document cross-references. Each has already caught something a careful read missed. |
| **`VM-RUNBOOK.md`** | How to boot the projection, drive it live, inject touch, and the false readings that have already misled this project. |

## The VM: how faithful it is, and how it got there

| Document | Answers |
| --- | --- |
| `vm/vendor-kernel-boot.md` | Why USB never worked here, and the vendor kernel that fixed it. Includes the module load order that matters. |
| `vm/partitioned-image.md` | The `p1…p17` layout, eight sizes measured from a vehicle's own fsck logs, the A/B slot map, and how `esinit` finally reached multi-user. |
| `vm/vendor-userspace-boot.md` | Booting the authentic rootfs under systemd with udev, and the media-indexer probe underneath it. |
| `vm/reproducing-the-authentic-image.md` | **How to rebuild the working image**: what the three ingredients are, where each staged file comes from, the boot command, what success looks like, and the surface-selection trap that cost five attempts. |
| `docs/vm/interacting-with-the-vm.md` | The interaction recipe: boot it, power it on so the layout appears, click, capture by surface, and how to tell each step worked |
| `vm/authentic-hmi.md` | The authentic `esinit → weston` path rendering: multi-user at 97.3 s, compositor alive, a 129 KB capture. The three projection-only instruments are listed here. |
| `vm/spi-gate.md` | The MICOM SPI gate: shut by default (`param=0`), opened by a stand-in that mounts `/sys` first. Three corrections, and the vendor's `> kmsg` typo that hid it. |
| `vm/SCREENSHOT-LABELS.md` | Which screenshot is actually which surface. Exists because two were mislabelled as the engineering screen and were the home screen. |
| `vm/apphomescreen-show-gate.md` | The early show-gate investigation, superseded in part but kept for the reasoning. |
| `vm/fastest-path-plan.md` | The sequencing plan written mid-session, with the Astra/Fable review folded in. |

## The interface, and why it stays black

| Document | Answers |
| --- | --- |
| `engineering-mode/engineering-paint.md` | The app never attaches a buffer: 624 bytes of Wayland traffic, all object-id teardown. It waits to be *shown* by the app manager. |
| `engineering-mode/appmanager-micom-replies.md` | Answering the manager's MICOM calls worked (`reply is not VALID` → zero), and the two blockers that remain: an unregistered show interface, and a liveness watchdog that reaps the unshown app. |
| `engineering-mode/engineering-data-services.md` | The six data services the engineering UI waits on, and the correction that answering them did not fix the paint. |
| `engineering-mode/dev-mode.md`, `engineering-mode/hidden-menus.md`, `engineering-mode/usb-and-hidden-triggers.md`, `engineering-mode/signature-vs-encryption.md` | The engineering-mode menus, what gates them, and the update/encryption boundary. |

## Security

| Document | Answers |
| --- | --- |
| **`root-access-paths.md`** | Every route to root, **ranked by what it costs to use** — the offensive view of the register: what you would try on a stock unit and what each attempt requires. |
| `../Ioniq5-VULNERABILITIES.md` | The register: ten entries, each with status, evidence and what would falsify it. Corrections are kept in place, not edited away. |
| `trust-anchors-in-writable-runtime-paths.md` | The argument behind six of the ten: a privileged decision resolved from writable state, and why that pattern matters more than any single instance. |
| `advisory/stock-vector-triage.md` | Two outside models asked what is reachable on a stock unit, what they agreed on, and the two things they corrected here. |
| `physical-and-wireless-vectors.md` | WiFi, USB Ethernet, UART, CAN: hardware present vs software enabled vs root path. |
| `wifi-enable-procedure.md` | How the radio would be turned on using the image's own machinery, and why it cannot be tested in QEMU. |
| `DOWNGRADE-POSSIBILITIES.md` | What the updater permits, and the one question (anti-rollback) that decides whether an authentic older image installs. |
| `navigation-status.md` | Navigation stack status, from before this session. |

## Evidence and the record

| Path | Contains |
| --- | --- |
| `evidence/serial-console/` | The raw bytes of the ttyS2 login prompt, and the recipe. |
| `evidence/vehdata-ground-truth.md` | What Battery and Range read on a real IONIQ 5 (321 value pairs from 545 vehicle logs) - the standard any injection is judged against |
| `docs/vehdata/03-can-shim-first-run.md` | The SocketCAN shim: the app's own `socket(PF_CAN)`/bind sequence intercepted, and why the visual result is still unmeasured |
| `docs/vehdata/04-capture-channel-and-light-frame.md` | Getting frames off the guest losslessly (and the `\n`->`\r\n` trap), plus what the first real frames show |
| `evidence/fde/` | The passphrase demonstration with its negative control. |
| `docs/v059-command-substitution-filtering.md` | Whether the mount image path is filtered before it reaches a shell string - measured: it is not |
| `docs/v059-producer-trace.md` | What feeds the substituted path: `QFileInfo::absoluteFilePath`, and `%1` in `cp -a %1 /app/bin/` is the payload's own binary |
| `evidence/vm-bringup/` | The touch proof: `QWaylandInputDevice::Touch::touch_down` in the application's own log. |
| `evidence/engineering-mode-appmanager-micom-methods-*.txt` | The exact MICOM methods the manager asked for and the stand-in did not answer. |
| `../Ioniq5-CHANGELOG.md` | Newest first, every change, including every correction and why it was needed. |
| `../Ioniq5-HISTORY.md` | Append-only, one human paragraph per session event. |

## Conventions used throughout

- **[E]** measured or quoted from the image; **[I]** inference. Where neither is stated, the sentence is a plan, not a finding.
- Every claim that could be wrong names **what would falsify it**.
- Every projection-only addition is labelled in its own file comment **and** in the changelog: the MICOM SPI stand-in, the `/usr/bin/weston` wrapper, the pixman solid-fill
  shim, the `lge_usb_adapter` neutralisation, the SMACK probe drop-in.
- "Not established" is a status. It is used deliberately and often.
