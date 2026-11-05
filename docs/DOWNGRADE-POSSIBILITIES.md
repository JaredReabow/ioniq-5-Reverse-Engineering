# Downgrade possibilities — what the recovered updater actually permits

**Subject firmware:** `NE_E.EUR.S5W_L.001.001.260128` (2026-01-28) — i.e. **later than late-2025**, so the
conclusions here are measured against a recent build, not an old one.

**Method:** static analysis of `AppUpgrade`, `AppDMClient` and the engineering-mode QML in the decrypted rootfs,
plus this repository's prior recovery of the update trust boundaries (`evidence/appupgrade-update-trust.md`,
33 KB). Nothing here has been run against a vehicle.

---

## 1. Short answer

**Engineering mode as normally described does not offer "install older firmware".** The updater's version gate is a
**strictly-newer** comparison, and the two mechanisms that could relax it are gated to development builds or require
write access to `/update` first. There is no stock-unit downgrade route that needs no privilege.

## 2. What actually gates a downgrade

Three separate gates, in the order the pipeline applies them:

| Gate | Behaviour | Relaxable by |
| --- | --- | --- |
| **Version comparison** | `checkVersionUSBUpdate` calls the comparator twice: a **strict** "must be newer than current" test, plus a second reference where **equality is allowed**. A lower version fails the first | the `forceUpdate` argument, or the equal-version local path (§3.2) |
| **Package authentication** | RSA `PKCS#1` verification of `.lge.upgrade.xml` before any payload is unpacked | nothing found; the trust anchor would have to be replaced (**V-034**) |
| **Build mode** | `[FORCE_UPDATE_FUCTION_ENABLE] DEV -> MP` and `force update is not support`: the force-update facility is enabled for development builds and **disabled for mass production** | a develop build of the updater |

The binary is unusually explicit about the second and third:

```
[%s] Force update !! Pass version compare.
[FORCE_UPDATE_FUCTION_ENABLE] DEV -> MP
[%s] force update is not support
[%s] NO CHECK to UNECE Version !!
```

## 3. The routes that do exist, ranked

### 3.1 Engineering-mode **Force Update** — real, but build-gated

Engineering mode's update list contains **Force Update** and, per the external project, a **Previous Version** view.
Force Update's own log line says what it does: **it passes the version comparison**. That is precisely a downgrade
facility — but it is the one the `DEV -> MP` gate disables on production builds, and the list itself is chosen by
`checkSOPVersion()`, which this build sets to production unconditionally.

**Status:** the capability is real; on a production build it is off. **Not available on a stock unit.**

### 3.2 FUMO's equal-version local relaunch — the most interesting evidenced path

`AppUpgrade` is an outer wrapper containing **two** updaters: an exact, case-sensitive **`-un:1`** selects **SCOMO**;
anything else selects **FUMO**. The recovered fallback row for this vehicle (`NE`/EUR) supplies **`-un:0`**, so app ID
300 runs **FUMO**.

In FUMO's USB path, `/update/disableEncryptionUpdate` selects **which verifier result contract** applies — absent
requires retained verifier returns `0/0`; present requires `-404/-404`. **An equal source/destination branch skips
both contracts**, and the prior analysis established that this equal source is **intentionally reachable** for a local
`/update/usb/bin` relaunch, including an exact **`force_launch=run`** state contract.

**Status:** a genuine evidenced bypass of the *verifier-result* contracts, but it requires:
- write access to `/update/usb/bin` (root), and
- the equal-version condition to hold, and
- all later model/region, payload-binding, write, slot, boot and health checks to pass — which the prior analysis
  explicitly says is **not established**.

### 3.3 SCOMO path — worse, not better

SCOMO is the updater selected by `-un:1`. On a `MASS_PRODUCT`/`PENETRATION` build its startup path **explicitly
ignores** `/update/disableEncryptionUpdate`, so the marker route does not even exist there.

**Status:** not a downgrade route on production firmware.

### 3.4 Anti-rollback — unresolved, and it is the ceiling for any of the above

Whether a validly **signed older** package installs depends on an anti-rollback mechanism that this project has
**not** resolved. The prior note is explicit: version/model checks, cryptographic binding, inactive-slot writing, boot
selection and mark-good behaviour remain unresolved, and a marker-bearing package has **not** been shown to pass the
later stages.

**Status:** unknown. This is the single fact that decides whether an older *authentic* firmware can be installed at all
on a stock unit, and it is not answered here.

## 4. What this means for a stock unit, late-2025 onward

- **Downgrade by engineering menu: no.** The item that would do it (Force Update) is disabled on production builds and
  the menu itself is production-gated.
- **Downgrade by modified package: no.** RSA verification rejects it, and the anchor is only replaceable from a
  privileged write (V-034).
- **Downgrade by authentic older package: unknown**, because anti-rollback is unresolved. If anti-rollback is absent or
  weak on this build, an authentic older package **should** install through the ordinary path, and that would be the
  clean, no-privilege downgrade route — `Force Update` would not even be needed for a *signed* older package unless
  the strict comparison is the only thing blocking it.

## 5. The cheapest next experiments

1. **Determine whether the FUMO version gate is strict in both comparisons or only in the first.** The prior analysis
   states strict-newer plus an equality-allowed second reference; confirming which reference is used on the USB path
   decides whether an older package is refused at the first gate or only at a later one.
2. **Look for an anti-rollback counter**: a monotonic version or fuse/OTP value, a slot-metadata field, or a
   `mark-good`/boot-attempt counter. Its presence or absence on this build is the answer to §3.4.
3. **Test with an authentic older package in the projection** — we now have a booting updater and a working touch path,
   so the version gate's actual behaviour can be observed rather than inferred, which is what this project has learned
   to prefer.

## 5b. The ceiling moved: V-059 circumvents the version gate entirely

Everything above assumes the updater installs the bytes it checked. **V-059** says it does not have to: `AppUpgrade` verifies a file and then installs it in a **separate process that
re-opens the same file**, while that file lives on attacker-supplied USB media. A programmable USB device can serve the genuine signed image during the check and different bytes during
the install.

That does not make a downgrade *easy* - it needs hardware and it needs the TE2 content key for the swapped payload - but it changes this document's central conclusion in one respect: the
**version gate runs on the checked bytes, not the installed ones**, so the unresolved anti-rollback question no longer bounds what can be installed. Anti-rollback still decides whether a
*signed older* image is accepted through the ordinary path; it does not decide this one.

**And it needs no key at all for a downgrade.** The TE2 content key (`velix_aes.key`) does **not** ship — it is read at run time from `/update/fota/velix_aes.key` — so crafting an
*arbitrary* payload needs a secret from the unit. But a **genuine older package** is already encrypted with the key the unit holds, so the install pass accepts it while the version gate has
already been satisfied against the *genuine current* bytes. That makes V-059 the first downgrade route in this project that does **not** bottom out in anti-rollback.

Corroborated statically in this image (the check and install command strings, `DecryptToPIPE`, the key-handling strings, and the absence of dm-verity); **not reproduced here**, and nothing
was installed anywhere.

## 6. Honesty statement

Every claim above is static analysis of shipped code or a quotation of this repository's prior recovery. **No downgrade
has been attempted, on hardware or in the projection.** The one question that matters most — anti-rollback — is
unresolved, and this document says so rather than implying a capability that has not been demonstrated.
