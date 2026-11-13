# VM-only `/tmp/no_unece` observation

## Specification fixed before launch

Use a new APFS CoW clone of `work/vm/kbuild/ws-run68`. Never mutate the immutable vendor base or the source workspace. Retain `tools/uk_fw/guest/no-unece-probe.sh`, the init wrapper, launch command, hashes and raw serial log. Boot authentic `/lib/systemd/esinit` through an init wrapper that starts the observer in the background.

After systemd is responsive, collect a baseline for **30 guest seconds**, create `/tmp/no_unece` only if absent, and sample the path/service state every **10 guest seconds for 60 seconds**. If boot already creates the marker, do not remove it to manufacture a transition: report the intervention as not performed. Host stop rule: **420 seconds**, or the exact probe completion line. A missing terminal line is incomplete observation, not a negative.

Observe `supplicantmanager.path` and `.service`, journal, process listing and network interfaces. Do not alter UNECE flags on hardware, manually start the service, force radio GPIOs, attach external networking, or change the frozen interval-capture harness. This experiment is about systemd/service behaviour only; it does not establish working Wi-Fi, visible controls, or interactivity. The VM lacks the real PCIe Broadcom radio and vehicle GPIO/MICOM hardware.

## Hardware provenance

The owner's supplied inventory agrees with the already committed live-unit summary in `evidence/vehicle-usb/owner-usb-ssh-offline-verification.md` (locate the detailed inventory there). Commit `180600a` records its private raw capture provenance, Wi-Fi `14e4:43ef`, Atom A3930, memory, 127305515008-byte eMMC, graphics/touch, audio/camera and vehicle interfaces. Hardware presence is now established for that observed unit, not inferred solely from shipped firmware. Do not publish serial numbers, credentials or raw identifying captures.

## Result

Pending VM execution. No physical-head-unit changes are authorized by this specification.
