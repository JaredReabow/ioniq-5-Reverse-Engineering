# Owner USB-Ethernet SSH candidate: offline and Radxa verification

Date: 2026-11-11

## Scope

This record covers the minimally modified owner-SSH candidate for the owner's
UK-origin 2021 IONIQ 5. The vehicle evidence identifies model
`NEAE.S5BLC.AEU` with installed software
`NE_E.EUR.S5W_L.001.001.250604`; the candidate is built from the official EU
`NE_E.EUR.S5W_L.001.001.260128` forward-update package.

The steady-state SSH transport is a dedicated USB-to-Ethernet link. The Radxa
Zero 3W remains the dynamic update-media presenter and is not part of the SSH
connection after installation.

## Candidate identity

- Firmware builder: `ioniq5_custom_firmware` `1.0.2`.
- Overlay payload: `1.0.1`.
- Owner USB-Ethernet overlay: `2.0.0`, manifest format `2`.
- Radxa owner image: `1.0.3`, SHA-256
  `14d8662e84a84d8ce079042fb2ddb428a385af6c58e35ede853bf0273f169312`.
- Radxa adapter: `1.1.6`, state schema `v4`.
- Genuine rootfs envelope size: `879126179` bytes.
- Genuine rootfs SHA-256:
  `362d9e329d970f403df4e69fece976ed6b4aaa27537e27a99e96e7796b9ad491`.
- Custom rootfs SHA-256:
  `880cfb89a9aca758d9b9c4aef912855813b1ad9a632ae81d00cd03484a7d381c`.
- The custom TE2 integrity check passed. Decrypted archive verification matched
  all 25 overlay members, modes, and root ownership. The earlier proof payload
  is absent from this candidate.

## USB-Ethernet policy

The generated target service:

- accepts only `0bda:8152`, `0bda:8153`, `0b95:7720`, `0b95:772a`, or
  `0b95:772b`, with the recovered `r8152` or `asix` driver;
- claims the dedicated name `ownerusb0` and address `10.42.0.1/24`;
- expects the directly connected client at `10.42.0.2/24`;
- provides no DHCP, default route, forwarding, or internet sharing;
- leaves OEM network services running and excludes only `ownerusb0` from
  ConnMan;
- exposes TCP/22 only on the dedicated interface and drops IPv6 and forwarding
  on that interface; and
- uses a pinned static Dropbear 2026.94 build with password, PAM, agent
  forwarding, and TCP/stream forwarding disabled at build time. Login is
  root-by-Ed25519-key only.

## Real exFAT image verification

The official 36-file EU package was copied into a raw 30,064,771,072-byte exFAT
image with `HU/images/mango-rootfs.tar.gz` copied first. The source tree and
mounted image had identical path and size inventories. A dry-run recursive
checksum comparison (`rsync -nrc --delete`, excluding only `.fseventsd`) exited
zero with no differences. There were no `._*` AppleDouble files.

Filesystem verification ran `fsck_exfat -n -x` and reported the volume OK.

A bounded exFAT parser independently read the boot record and directory-entry
sets. It established:

- bytes per sector: `512`;
- sectors per cluster: `64`;
- cluster size: `32768`;
- rootfs first cluster: `15`;
- rootfs raw-image offset: `5668864`;
- rootfs length: `879126179`; and
- 26,829 consecutive clusters (`NoFatChain`), so the rootfs is one contiguous
  extent.

Hashing the exact raw extent produced the genuine rootfs SHA-256 above. The
complete baseline image SHA-256 is
`bcfc2eb5a7d9cd63dce85eee088b59361400277e381e6e554ade3b1e4f889a36`.

The content-bound Radxa serve plan then passed validation. A complete two-pass
read replay compared every returned byte with an independently assembled
expected byte stream:

| Pass | Full image SHA-256 | Rootfs extent SHA-256 | Result |
|---|---|---|---|
| 1, genuine | `bcfc2eb5a7d9cd63dce85eee088b59361400277e381e6e554ade3b1e4f889a36` | `362d9e329d970f403df4e69fece976ed6b4aaa27537e27a99e96e7796b9ad491` | exact match |
| 2, custom | `dfb101b8390f1166949edbe8a2acff914f3347ab3c44bb76a2b127625ed294a2` | `880cfb89a9aca758d9b9c4aef912855813b1ad9a632ae81d00cd03484a7d381c` | exact match |

Every byte outside `[5668864, 884795043)` remained identical to the baseline.

## Source and harness checks

The integrated focused suite completed with `121 passed, 35 subtests passed`.
The generated target startup script passed `sh -n`. The exact static Dropbear
binary SHA-256 is
`57651d3d0e9781374484c951bf49a70cda92e9c5f9108159c8f72ecbe9254163`;
its pinned source accepts the generated `-F`, `-m`, `-l`, `-p`, `-D`, `-r`, and
`-P` options, while the build configuration removes password and forwarding
features.

## Physical Radxa verification

The prepared SD card booted on a Radxa Zero 3W, joined the configured Wi-Fi as
`radxa-ioniq.local`, and accepted root login with the retained Ed25519 key.
Effective OpenSSH policy required public-key authentication and disabled
password and keyboard-interactive authentication. The service remained enabled
and active after reboot.

The board streamed and verified the complete content binding before arming. A
final physical lifecycle bound UDC `fcc00000.usb`, served the image through
nbdkit on loopback port `10809`, attached `/dev/nbd0`, and exposed it through
the owned configfs mass-storage function. The checkpoint recorded controller
`1.1.6`, attached NBD/gadget phases, and no completed cleanup steps. Teardown
completed in `0.839s`; independent checks found no state file, gadget, NBD PID,
nbdkit listener, or nbdkit process. A subsequent reboot remained clean.

Earlier live attempts exposed and fixed two fixture gaps: redundant writes to
an already-empty configfs UDC may return `ENODEV`, and NBD sysfs disappearance
may lag a successful detach command. The final controller skips the redundant
write and polls the exact owned NBD identity for at most five seconds, failing
closed on timeout or identity change.

## Boundary

This is package-, filesystem-, source-, replay-, and physical Radxa lifecycle
evidence. It does not establish head-unit installation or boot, vehicle-side
adapter enumeration, live head-unit SSH authentication, SCP, unplug/replug
recovery, or preservation of normal infotainment behavior. The SD card was
written and the Radxa was exercised; the vehicle was not connected or changed.

## 2026-11-12 correction: authentication recovery candidate 4.0.2

The preceding record is historical v2 evidence. The owner subsequently reported
a completed car update; the RTL8152 link and TCP/22 listener were reached, but
the key was rejected. The corrected candidate keeps authorized_keys in root's
private runtime home and adds nonempty-password SSH, an independently
authenticated HTTPS shell, and a USB-keyboard local Weston terminal trigger.
Wi-Fi AP, Radxa ECM and serial/TTL are excluded from the selected overlay.

The selected artifact is `owner_access_v4.0.2_260128.te2`, 879126179 bytes,
SHA-256 `94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6`.
The builder verified TE2 integrity and the decrypted overlay's bytes, modes
and root ownership, with 44639 padding bytes. Its genuine input remains the
260128 envelope identified above. The pinned password-capable Dropbear SHA is
`722c49d48a435ab47d87df102434edc632b5dce27323c37580b4b4e6aa0cc3d8`;
web binary 1.0.2 SHA is
`18c6ac2eb0f5e3d92661bcf979f447e6bd211ab7541bc83847f5efb26c8e807b`.

Actual Linux tests demonstrated correct key/password login, wrong/blank and
unrelated-key rejection, PTY, SCP round-trip and forwarding refusal under an
OEM-style 0775 root directory. The generated independent SSH launcher received
a separate clean-environment startup regression. Chrome-to-Linux testing of
the browser UI verified click-to-type focus, real shell output, Logout 204,
closed terminal socket, unauthenticated status/reload and no reopened terminal.
The temporary loopback server and tunnel were stopped after the test.

The integrated run passed 1388 tests and 352442 subtests, with four skips.
Two stale generator-version assertions were the only failures; after updating
those assertions, the affected HTTPS module passed eight tests and five
subtests, including the exact packaged amd64 Linux smoke. Go race tests and
vet passed. Astra and Sol independently checked the final artifact hash and
accepted the corrected offline candidate. Local-terminal visibility, execution
on the head unit's kernel 4.1, installation and real head-unit authentication
remain unverified.

The Radxa retains its original SD installation, baseline and previous payloads.
Controller 1.2.1 and dashboard 1.0.7 are installed in place. Journal evidence
identified the apparent crash as KDE deep suspend; idle power actions are now
disabled and an enabled root sleep/idle inhibitor is active. The new payload's
explicit preparation reuses the verified baseline cache, avoiding another
30 GB hash. The updater remains disabled and unarmed; this work did not start
another car update.

The final live API check exposed a display-only cache issue: old-size and
current-size entries for the replaced serve plan were both retained. Dashboard
1.0.7 recognizes a current whole-file record as superseding stale extents for
that same path, while partial records and later mutations cannot hide a stale
identity. The affected Radxa/dashboard/controller/image/wrapper suite passed
106 tests and six subtests. Both reviewers accepted this scoped correction;
the installed API then reported `Prepared media ready; not armed` with current
identities and no active updater. Firmware 4.0.2 bytes remained unchanged.
