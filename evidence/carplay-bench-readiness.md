# Passive CarPlay/iAP2 bench readiness

Status: host tooling ready for a future disconnected owner-controlled bench.
No physical device, target network, service, driver, or protocol was accessed.

## Purpose

The exact-static CarPlay review identifies a configured UID-zero projection
stack, but that does not establish what is installed or active on the owner's
head unit. The existing read-only state probe now captures the minimum facts
needed to separate five questions:

1. Does the installed stack byte-match recovered EU `260128`?
2. Is the exact service active with the expected credentials and SMACK domain?
3. Are the normal wired iAP2/NCM modules and device boundary present?
4. Is an AirPlay port-7000 listener visible? This is informational only.
5. Has a public CVE, code execution, unrestricted root, or persistence been
   demonstrated? The passive assessor always answers no.

## Capture additions

`tools/uk_fw/bench_state_bundle.py` remains stdout-only on the target. It now
adds passive metadata, hashes, or state for:

- `carplay_iAP2.service` and `carplay_mdnsd.service`;
- `/etc/iap2_mod.sh` and `etc/smack/accesses.d/projection`;
- `iAP2Service-2.0`, `AppProjection`, and `mdnsd`;
- the exact iAP2, AirPlay, CoreUtils, AirPlaySupport, and CarPlay libraries;
- shipped `usb_f_ncm.ko`, `usb_f_iap2.ko`, and `mfd-iap2.ko`;
- `/dev/mfd-iap2` and alternate `/dev/ttyIAP20` metadata and `SMACK64` state;
- command lines/PATH for running projection processes; and
- parsed `/proc/modules` lines in the canonical `facts.modules` array.

The existing interface and `ss -lntup`/`netstat -lntup` capture is reused. It
reads local kernel state only; it does not connect to a listener or transmit a
packet.

## Host assessment

After producing `work/bench/state.json` as documented in the runbook:

```sh
PY="${PYTHON:-$HOME/.platformio/penv/bin/python3}"
"$PY" tools/uk_fw/bench_carplay_readiness.py work/bench/state.json \
  -o work/bench/carplay-readiness.json
```

The assessor validates the input's canonical digest and compares sixteen exact
recovered hashes covering units, policy, applications, libraries, and kernel
modules. It then evaluates:

- complete, warning-free capture ordering;
- loaded and active unit state;
- a live `/app/bin/iAP2Service-2.0` process with EUID zero and
  `App::projection`;
- `/dev/mfd-iap2` as a character device with `System::iap20`;
- loaded `usb_f_ncm`, `usb_f_iap2`, and `mfd_iap2` modules;
- the alternate tty endpoint and mDNS state separately; and
- an optional local `:7000` listener as an informational observation.

`active_wired_carplay_prerequisites_observed` deliberately does not require
`/dev/ttyIAP20`, mDNS, or port 7000. The exact service names `/dev/mfd-iap2`, and
public generic AirPlay port behavior must not be imposed on the recovered wired
path without runtime evidence.

## Interpretation boundary

A fully passing report proves only that the owner-unit snapshot matches the
recovered files and that the configured wired projection prerequisites were
present at capture time. It does not prove:

- phone identification, authentication, pairing, or route eligibility;
- attacker-selected bytes reaching `_requestProcessSetupPlist` or another
  parser;
- applicability of CVE-2025-24132, CVE-2025-30422, the Sony/Alpine issues, or
  any other public vulnerability from the passive capture alone; the separate
  exact-static review now establishes an `ekey` stack-write mechanism with
  third-party CVE-2025-24132 attribution, not vendor-confirmed fixed-byte
  identity or runtime delivery;
- a malformed input, crash, memory corruption, or code execution;
- escape from `App::projection`, unrestricted root, flash acceptance, modified
  firmware acceptance, or persistence.

Configured EUID zero and unrestricted root are intentionally separate. The
runtime process gate records capabilities as evidence but does not infer that
SMACK restrictions are bypassed.

## Safety properties

- The generated target script contains no mount, service mutation, module load,
  radio change, network client, target write, device open, ioctl, or package
  installation command.
- Hashing reads regular files only; device nodes receive metadata/xattr queries,
  never content reads.
- The host assessor performs strict duplicate/non-finite JSON rejection, stable
  no-follow reads, canonical digest verification, deterministic UTF-8 output,
  and exclusive no-overwrite creation.
- All exploit, CVE, root, and persistence verdicts remain false regardless of
  passive prerequisite results.
