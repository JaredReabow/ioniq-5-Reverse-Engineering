# Pre-disclosure security assessment

Status: **internal assessment, not a disclosure.** No vendor was contacted and
nothing was published. This document exists so that any future disclosure is
built on confirmed observations rather than inference.

Scope: the official EU `260128` package, the plaintext kernel within it, and the
public Gen5 Wide-Open toolchain. The encrypted userland was never decrypted and
the unit was never powered.

---

## Method and confidence scale

| Level | Meaning |
|---|---|
| **Confirmed** | Reproduced independently in this workspace from the artifact |
| **Observed** | Seen in the artifact or a primary public source, mechanism not proven |
| **Hypothesis** | Consistent with evidence, contradicted by none, proven by none |

Nothing below has been demonstrated to be exploitable on a live unit.

---

## 1. Manifest integrity is CRC-32 and size — *Confirmed (mechanism) / Hypothesis (impact)*

`IONIQ5_EU.ver` records, per payload, a byte size and a signed 32-bit value. All
35 values match `zlib.crc32` of the file, verified locally on both the EU and AU
packages.

CRC-32 is affine and not collision-resistant. `tools/uk_fw/crc32_forge.py`
demonstrates that any content change can be masked by a 4-byte correction while
the manifest value is preserved, on a real manifest entry.

**Why it may not matter:** the `.ver` values are computed over **ciphertext**, so
producing a modified payload still requires the decryption key, and a public
field report describes repairing both CRC and size and being rejected anyway —
so at least one further check exists.

**Would become disclosable if:** a package with a repaired `.ver` and a
decryptable payload were accepted by a stock unit.

## 2. OEM key manifest located by a command-line parameter — *Confirmed*

`manifest_init` scans kernel parameters for **`oemkm`**, parses
`oemkm=<size>@<physical-address>`, copies the blob out of physical memory, and
validates only four header fields (a type word `0xe` and three zero fields)
before building `.manifest_keyring` with root credentials.

The parameter is absent from all six packaged command lines, so the boot loader
supplies it.

**Design observation:** the root of trust is a plain-text address whose contents
are implicitly trusted; the manifest is not self-signed or measured.

**Why it may not matter:** the boot loader is not attacker-controlled, and the
kernel command line is covered by the `ipk.` container signature.

**Would become disclosable if:** a stock unit could be booted with an
attacker-chosen `oemkm=` value (e.g. via `kexec` before the sysctl is set, or an
alternate command-line source) such that a substituted keyring were accepted.

## 3. `keystore_open` performs no capability check — *Confirmed*

The open handler calls only `nonseekable_open()`. Access is therefore governed
entirely by the device node's mode and SMACK label, both of which live in the
encrypted rootfs and were not recoverable.

**Would become disclosable if:** `/dev/keystore` shipped world-writable or with a
SMACK label reachable by a non-privileged service, and any ioctl produced an
effect beyond returning a public key. The ioctl boundary itself reviewed clean
(size gate, overflow checks, matched allocations), so this is unlikely on its own.

## 4. Boot image signature carries its own modulus — *Confirmed (structure) / Hypothesis (impact)*

The `ipk.` container is RSA-2048 / PKCS#1 v1.5 / SHA-256 over
`header + payload + 4-byte tag`, with the 256-byte modulus and exponent in the
trailer. The modulus appears nowhere in the kernel.

**Would become disclosable if:** the boot loader verified with the embedded
modulus rather than a pinned one. That is testable only on hardware and is the
single highest-value bench experiment in the programme.

## 5. Public modification installs an unauthenticated root runner — *Confirmed, but out of scope for vendor disclosure*

The public `wideopen.service` runs as root, restarts forever, and executes any
file named `wideopen_service.sh` found on `/media/usb`. This is created **by the
modification**, not present in stock firmware. It is a hazard of adopting the mod
rather than a vendor defect, and should not be reported as one.

It is recorded here because it is the most consequential safety fact in the
programme: if a modified unit returns to a vehicle, that service is an
unauthenticated root path on a road-going computer.

---

## What was established as *not* vulnerable

Recorded so a report is not padded with noise:

- the kernel is fully symbolised (64,923, cross-validated against `__ksymtab`)
  and the reviewed trust-chain and keystore code showed no memory-safety defect;
- the OTA cipher is sound for its purpose: no ECB, no keystream reuse, no
  plaintext-equality oracle across builds, no offline break;
- the packages are complete and manifest-consistent: 35/35 files, zero unlisted,
  zero missing, both regions;
- no key material or certificate exists anywhere in the plaintext package
  (223 artifacts scanned).

## Before any disclosure

1. Confirm items 1–4 on hardware, not from the package.
2. Separate what the vendor shipped from what the modification installs.
3. Follow coordinated-disclosure norms: vendor first, reasonable window, no
   working chain published.
4. Keep the reproduction minimal and non-destructive.

## Handling

No vendor contact has been made. No advisory has been written. This file is an
input to a decision that belongs to the device owner, not to this agent.
