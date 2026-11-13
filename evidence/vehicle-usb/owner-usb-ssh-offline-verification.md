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

## 2026-11-12 complete readiness retest

The final committed 4.0.2/1.0.7 source passed a fresh complete pytest run:
**1391 tests and 352442 subtests passed; four tests skipped** for unavailable
private AppLauncher/Smack audit inputs. No failures remained. The exact amd64
packaged HTTPS smoke was enabled, and fresh Go race tests/vet passed. The
consolidated repository consistency runner passed. Its separate public-snapshot
privacy scan retains the 12 findings recorded in history; an exact search for
retained owner private inputs across 1589 tracked paths found no matches.

The actual encrypted package SHA and size matched the selected manifest.
Decryption of a private temporary copy verified all 38 overlay members,
including bytes, root ownership, modes and links. Fresh exact-binary Linux
Dropbear tests passed key/password and rejection cases, PTY, SCP and forwarding
refusal. Real Chrome-to-Linux recovery-terminal login, command and logout
passed. Live dashboard checks at 1280x800 and 800x480 passed, including HTTP
405 for its arm endpoint. Test servers and tunnels were stopped afterward.

Forced content preparation on the installed Radxa freshly read the complete
30064771072-byte baseline and selected replacement and verified the genuine
extent against its builder manifest. This took **411 seconds**; prior cache
and preparation log were backed up before the operation. The resulting cache
is persistent and current. This was verification, not an SD image rebuild.

With the car confirmed disconnected, the installed controller completed an
actual service/NBD/configfs/UDC lifecycle. Arming took **2.965 seconds** and
teardown **1.766 seconds**. Aligned `O_DIRECT` reads bypassed the Linux block
cache and established:

| Read | Bytes | SHA-256 |
| --- | ---: | --- |
| First region pass, genuine | 879126179 | `362d9e329d970f403df4e69fece976ed6b4aaa27537e27a99e96e7796b9ad491` |
| Second region pass, custom | 879126179 | `94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6` |

The boot-sector read matched baseline too. Post-test checks found no owned
gadget, NBD PID, backend process, controller state, arm marker or test listener.
The updater remains inactive/disabled, with the dashboard reporting ready and
unarmed. A fresh cached plan passed in **0.864 seconds**. Persisted autologin,
idle-lock/power policy and active unlocked desktop were checked without reboot.

The UDC reported **no USB host attached**. These direct NBD reads prove the
installed board-side serving and switching path; physical USB enumeration and
host-side reads remain unverified. The owner reported that moving the cable
to the Mac would interrupt power. No shutdown/reboot was sent. Head-unit
installation, kernel 4.1 execution, real vehicle authentication and local
terminal visibility remain target-only checks; no car update was started.

## Subsequent cold-boot and physical USB test: unresolved second-read mismatch

The owner connected the Radxa to the Mac after a clean cable-swap shutdown.
Cold boot restored SSH, an unlocked autologin desktop, dashboard 1.0.7 and
keepawake. The persistent preflight passed in 0.782 seconds; arming took 2.799
seconds. USB identity, serial/port and the exact 30064771072-byte physical
medium were checked before mounting its IONIQ5_EU volume read-only.

| Physical USB file read | Seconds | SHA-256 | Result |
| --- | ---: | --- | --- |
| First | 22.418 | `362d9e329d970f403df4e69fece976ed6b4aaa27537e27a99e96e7796b9ad491` | exact genuine |
| Second | 28.826 | `9ec5e571393f3df51b21ec99b2019afc449321250721212b149b82a94f065386` | does not match custom |

Each read contained 879126179 bytes and used Mac F_NOCACHE with read-ahead
disabled. The test unmounted its owned volume and tore down the gadget. This
does not qualify the physical switching path. It also does not demonstrate
that the retained package is corrupt: its byte-level checks and direct Linux
NBD sweeps passed. A later repeat-arm NBD boot-sector probe passed in 0.0046
seconds after a 2.468-second arm, with clean teardown.

Astra and Sol recommended classifying received blocks and correlating backend
read traces before changing the switching heuristic. Mac/gadget caching is
plausible but unproven. Local genuine-prefix and genuine-edge/custom-middle
hash reconstructions did not reproduce the wrong digest. Diagnostic retries
preserved state/backend logs but did not obtain another usable Mac volume.
The local diagnostic is prepared to capture per-block classifications once
the host permits a fresh connection. No production switching change was made.

Computer control explicitly refused access to macOS UserNotificationCenter
for safety reasons despite the owner's USB-prompt authorization. That block
was reported and not bypassed; a manual Allow click may be required at the
next attempt. The device remains running, with the updater inactive/disabled
and its test resources cleaned up. The selected 4.0.2 firmware is preserved,
but the new vehicle flash is not marked ready pending physical USB diagnosis.

## 2026-11-13: cache correlation and physical direct-I/O prototype

The next correlated capture established stale reuse above nbdkit: 602112 bytes
in the second host read were genuine-only, while all 6719 backend requests in
that interval selected replacement/pass 2 and none covered those stale ranges.
See `work/usb-diagnostic-5d5a4476fe80/`. The precise cache layer was not isolated.

A pinned nbdfuse 1.14.2 frontend was built with an explicit successful-open
`direct_io=1, keep_cache=0` change. One readonly connection and a single FUSE
thread back the actual mass-storage LUN directly, without a kernel NBD or loop
block device. The firmware package, byte ranges and backend switching profile
were unchanged.

| Actual Mac USB read | Seconds | SHA-256 | Result |
| --- | ---: | --- | --- |
| First | 83.920 | `362d9e329d970f403df4e69fece976ed6b4aaa27537e27a99e96e7796b9ad491` | exact genuine |
| Second | 94.839 | `94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6` | exact custom |

Each read contained 879126179 bytes. Second-pass classification contained zero
genuine-only or unknown bytes. The temporary chain became ready in 0.415 seconds
from the persistent preparation cache. Its effective LUN was read-only (`ro=1`),
which remains an explicit car-compatibility boundary.

This diagnostic enabled verbose libnbd tracing and filled `/run`; its final
trace was partial and automatic teardown failed after USB unbinding. The
200646656-byte log was verified and preserved in private persistent storage,
then ownership-checked recovery removed the exact gadget and mount and verified
process absence. The proof directory's cleanup.json records that recovery;
this is not a claim of successful normal teardown. Prototype runtimes/journals
are saved under `/var/lib/ioniq5-update/fuse-proof-preserved/` and the Mac's
ignored work directory. The production candidate uses no verbose helper trace.

The recreated packaged helper compiled natively with a zero-fuzz patch against
the pinned source archive; its three patched C files match the USB-proven
prototype exactly. SHA256:
`c80695d05c904a829252495b36f85c67313b89281cfa3dcc9c41d5325fcdec9d`.
Normal installed-controller lifecycle and physical replay are the next checks.
No vehicle update has been performed in this diagnostic session.

## Installed runtime qualification

Controller 1.3.0's direct FUSE file mount passed complete physical USB reads
of all 879126179 bytes: genuine in **69.716 s**, custom in **81.298 s**. The
second read had **zero stale genuine-only or unclassified bytes**. The exact
hashes are the same genuine/custom hashes above. Normal stop returned successful
and inactive, with no state, gadget, mount or recorded child processes.
See `work/usb-diagnostic-82b9af1e09df/`.

A separate actual helper-crash test confirmed USB withdrawal and complete
owned cleanup (`work/usb-diagnostic-507c949b5f74/`). Its final redundant Mac
unmount failed because the test intentionally removed that disk; independent
checks verified the expected absence and saved cleanup.json.

Final controller **1.3.1** only changes status inspection to use the owned
backend's mount namespace. Dashboard **1.0.9** loads the canonical controller
and has the process-inspection capability needed by the hardened service.
The actual installed HTTP service then reported a healthy USB backing while
armed; a fresh physical USB 4096-byte prefix matched genuine, and stop again
left no state, gadget, mount or owned processes. Final arming was **2.989 s**;
fresh cached preflight was **0.878 s**, with no baseline rehash. See
`work/usb-diagnostic-ddcdbefb8f22/`.

The board remains running, prepared and unarmed. The firmware stays 4.0.2.
The effective readonly disk and actual head-unit update/login behavior remain
vehicle-only checks. No car was connected during these tests.

The final dashboard-only follow-up is **1.0.10**. Sol identified that procfs
command lines report size zero; the prior bounded reader therefore produced
a false backend-process error. The corrected reader uses its explicit byte
limit, with two regressions. In the final actual armed HTTP result, Controller
service, Backend process and USB backing are all healthy and `errors=[]`.
Arming took **2.875 s**, a physical USB prefix matched genuine again, and clean
stop removed all owned resources. See `work/usb-diagnostic-973da2442d6f/`.

Canonical tests: **1404 passed, 352442 subtests passed, five skipped**. After
the last dashboard-only correction, all **122 affected tests and six subtests**
passed. The controller/data-serving path remains 1.3.1 and firmware remains
4.0.2. This qualifies the Radxa–Mac bench workflow, not vehicle installation
or authentication.

## Additional unarmed readiness audit

Runtime **1.3.2** fixes a stale installed test bundle and includes the FUSE
module in `ioniq-update-media selftest`. The actual board passed **13 + 80 + 5**
tests, and the Mac suite passed **1407 tests / 352442 subtests**, with five
skipped. The transport behavior, helper, firmware 4.0.2 and cache policy remain
unchanged. The fresh cached plan took **1.121 s** and the updater stayed unarmed.

The selected firmware's owner key, host key, SSH password verifier, independent
HTTPS verifier and TLS material all match retained recovery credentials. The
Mac now has a strict host-pinned profile:

```sh
ssh ioniq-headunit
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password ioniq-headunit
```

Both this alias and the raw `10.42.0.1` address select the intended owner key.
The Mac Ethernet interface already has `10.42.0.2/24` and a direct route. A live
head-unit SSH server was not reachable in the current setup; no login was claimed.

Read-only filesystem checks of synced copies of both SD boot partitions passed.
No physical-card read/write failures were found in the current kernel log; the
older NBD fault-test errors are separate. Required kernel modules match the
installed kernel; package audit, free space, and sleep inhibition were checked.

Existing authentic-kernel Tuxera evidence explicitly mounted write-protected
USB media, and the retained stock automounter has an `MS_RDONLY` retry path.
See `work/vm/vendor-userspace-260128/tuxera-exfat-clean-probe-v2-host.log` and
`work/appfumo-usb-pathname-provenance/usb-automount.full.asm`. These checks improve
confidence but leave actual car USB/power, boot, authentication and terminal
visibility unverified. No power cycle or car update was performed.
