# Controls that exist, and what each is worth

Date: 2026-11-05. The register lists **75 findings**. This page lists the **controls the platform does have**, because a
patch team that only reads the findings will not know what it must not break - and because several findings are only
severe *because* a neighbouring control is missing rather than because the control itself is weak.

Every entry is measured; the caveat column is where each one actually stands.

| # | control | evidence | what it is worth | caveat |
|---|---|---|---|---|
| 1 | **System bus is deny-by-default** | `/etc/dbus-1/system.conf`: `<deny own="*"/>`, `<deny send_type="method_call"/>`, with per-service allows | no non-root process can call a service that has not explicitly allowed it | **nine services add a `context="default"` allow** - V-063 - so the rule is only as good as the individual policy files |
| 2 | **SMACK is loaded and specific** | 636 rules across 27 files; **no rule grants `w` or `x` broadly**; wildcard objects are `t` (transmute) only | the label set does not hand out write or execute, the two permissions every finding here concerns | enforcement **unproven** - no relabel has ever been demonstrated; and `smack_setup.sh` switches to permissive when `optUNECE=0` (V-052, measured 0) |
| 3 | **No setuid or setgid binaries** | `find -perm -4000 -o -perm -2000` → **0** | there is no privilege-bit escalation surface at all | none - this is a genuinely clean result, and it is why every escalation in the register goes through **file access or a service** |
| 4 | **No world-writable directories** outside `/tmp`, `/run`, `/var/volatile` | `find -type d -perm -0002` → **0** | a compromise cannot simply drop files into a directory it can write | the two world-writable **files** in V-066 are therefore anomalies in two paths, fixable with a targeted `chmod`, not a tree audit |
| 5 | **Update packages are signature-checked** | FUMO: `ionice -c3 md5sum %1` + `PKCS#1 sig. verify` / `md5WithRSAEncryption`; SCOMO: `run_signatureCheck`, `PKCS#1 sig. verify:`, mbedtls RSA | unsigned content is refused in the normal path | the **keys and CAs are trusted from writable paths** (V-048 `/tmp/app_normal.key`, V-069 navi CA on `/rw_data`), so the check is only as strong as where it reads its anchor |
| 6 | **A/B boot with self-repair** | `esinit` runs `fsck.ext2 -fy` on the inactive slot in crash-recovery mode, `mke2fs -F` if fsck fails badly, then `cp /tmp/plk2/iasImage /tmp/plk1/iasImage` | a corrupted boot slot is **recovered**, not fatal | nothing verifies `iasImage` in userspace - V-075 - so the recovery will happily restore whatever is in the other slot |
| 7 | **Application-set hash + MICOM challenge** | `getIVDHash() -> ay` returns a SHA-256 over the application binaries; `Seed`/`KeyCheck` handlers; OpenSSL cipher utility | an integrity identity exists and is computable without a MICOM | the **reference lives in MICOM firmware**, so enforcement is unprovable here; and the digest itself is queryable (V-061) |
| 8 | **WiFi is gated three ways** | blacklist, GPIO 466, MICOM parameter; enable triggered by `/tmp/no_unece` | the radio does not come up by accident | it is a *gate*, not a control: one `/tmp` write removes it (V-050, V-042) |

## The pattern across all eight

**Six of the eight place a decision on state an attacker can reach** - a `/tmp` marker, a writable partition, a
policy file with a default allow, a CA on a read-write filesystem. Two do not: **there is no setuid surface** (#3) and
**no world-writable directory** (#4).

That split is the most useful thing on this page. **The platform's hygiene is good where it is structural and weak where
it is configured**, which is exactly the boundary the register's recommendation names: *never resolve a security decision
from a writable path, and make every such check fail closed.*

## How to use this page when patching

1. **Do not lose #3 and #4** while fixing anything else - they are load-bearing and cheap to keep.
2. **#1 and #2 are already correct in form**; the fixes in V-063 (default allows) and V-052 (`optUNECE`) make them
   effective rather than replacing them.
3. **#5, #6 and #7 are good designs with unreachable anchors.** Every one of them becomes sound the moment its anchor moves
   to read-only storage - the same fix, three times.
