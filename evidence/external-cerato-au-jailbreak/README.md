# Imported material: `coopermarino/2022-cerato-au-jailbreak`

**Provenance.** Copied verbatim from the public repository
`https://github.com/coopermarino/2022-cerato-au-jailbreak` on 2026-11-04, for cross-reference against this
project's own findings. Nothing here is this project's work, and nothing here has been independently verified
by this project unless a file in this repository says so.

**Why it is relevant.** That project targets the **same platform generation**: LGE Gen5W IVI, LGE "mango",
Linux kernel `4.1.27-abl`, glibc 2.25, SMACK. The model differs (Kia Cerato 2022 AU vs Hyundai IONIQ 5 EU
`260128`), so **platform-level analysis ports; model-specific binaries, signatures and offsets do not.**

## Copied (analysis and scaffolding that generalises)

| File | Why |
| --- | --- |
| `VULNERABILITY_REPORT.md` | platform-level vulnerability analysis, cross-checked against this register |
| `VULNERABILITY_ANALYSIS.md` | USB attack-surface analysis |
| `ZERODAY_ASF_REPORT.md` | media-parser (ASF) vulnerability class |
| `LGE_Gen5W_IVI_Security_Briefing.md` | platform architecture summary |
| `TOCTOU_ATTACK_PLAN.md` | maps directly onto this register's V-034 (trust anchor on a read-write root) |
| `UPDATED_STRATEGY.md` | independent description of the engineering-mode Encryption Update toggle |
| `JAILBREAK_GUIDE.md` | engineering-mode gesture and PINs |
| `FINDINGS.md` | their findings list |

## Deliberately **not** copied

Per a triage pass, the following are keyed to the Cerato build and would silently mis-target this image:

- `2022_Cerato_AU.ver`, `2022_Cerato_AU.ver.patched` — model-specific signature/version files
- `exploit/fb_pwn.c`, `exploit/pwn.sh`, `exploit/build_exploit.sh` — hardcoded framebuffer addresses and offsets
- `HU/images/mustwithcopy` — image blobs tied to their layout
- `build_exploit_mp4.py`, `build_all_pocs.py` — useful as a scaffold only; any regenerated exploit must take this
  image's own offsets from `/proc` and its own binaries, never theirs

## Overlap with this project's register (so findings are not double-counted)

| Their claim | This project's entry | Handling |
| --- | --- | --- |
| Update trust anchor weakness / TOCTOU on a writable root | **V-034** (and duplicate **V-044**) | same root issue; do not count twice |
| Engineering-mode PIN derived from static unsalted hashes | **V-041** | same finding; their PINs are a useful cross-check |

## What this project independently confirmed before seeing this repository

The engineering-mode **develop/SOP state** is an integer on the engineering engine decided by
`setEngType()`; the **`MASS_PRODUCT or PENETRATION Build mode -> Ignore disableEncryptionUpdate`** string is
present in this image's `AppUpgrade`; the flag is the file `/update/disableEncryptionUpdate`; `AppUpgrade` is
fully static with mbedtls inside. Their material agrees on the flag and the toggle; it does not describe the
integer/path mechanism, which remains this project's own result.
