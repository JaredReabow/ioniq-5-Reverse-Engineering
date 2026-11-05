# Cross-project triage: 2022 Kia Cerato AU Gen5W jailbreak

Source: <https://github.com/coopermarino/2022-cerato-au-jailbreak>
(cloned at `work/cerato-jb-20261104/`, excluded from Git by `/work/`; upstream HEAD `8473b25`).

Same platform family as us: LGE **Gen5W** / S5W_L, x86-64 Linux, Qt5. Their build is a
2022 Kia Cerato AU; ours is `NE_E.EUR.S5W_L.001.001.260128`. Platform-level findings
transfer; model- and build-specific ones must be re-verified against our own binaries.

Every claim below was re-checked against our own artefacts. Upstream claims are quoted,
not endorsed.

## 1. Claims that do NOT transfer (refuted against 260128)

**`<SrcFullPath>x;sh /media/usb/pwn.sh #</SrcFullPath>` (their `exploit/.lge.upgrade.xml`).**
Their mechanism requires `SrcFullPath` to be interpolated into a shell command. In our
build it is not:

- Our XML parser uses `QDomElement::attribute()` — it reads **attributes**, not child
  elements — and compares each name against: `password`, `newfirmware`, `updatespeed`,
  `imagefiletype`, `src`, `lcdtype`, `vehicle`, `ccp`, `rrc`, `vess`, `build-date`,
  `essentials`, `upgrade-key`, `car-variant` (rodata `0x212400`–`0x2124e0` of the
  `0x5721c8` embedded stage). `essentials` is present; `SrcFullPath` is not.
- In our binary `SrcFullPath` is a **FOTA D-Bus field**: looked up in a map, and when
  empty the code issues `mfGetUpdateSrcPath` on service `com.lge.hkmc.avn.upgrade.fota`,
  path `/fotaInterface`, logging `[%s] Requery with another method call.`

Full detail: `evidence/updater-system-command-injection.md` §6.

**Their `sudo mount -o loop -t ext4 %s %s` "Alternative Vector #2".** They flag it but
never prove it. It **is** present in our build, and was analysed separately — see
`evidence/updater-system-command-injection.md`. It remains a command-construction
primitive with an untraced argument origin, not a proven vector.

## 2. Claims that DO transfer and are confirmed present in our build

**`/update/force_ua_test.txt` — a second plaintext-update trigger.**
Our `AppUpgrade` contains all three of:

```
### Unencryption Update. ####
/update/force_ua_test.txt
[%s]UnEncryption Mode isZip[%d] target[%s]
```

Upstream asserts this path is *not* gated by the
`MASS_PRODUCT or PENETRATION Build mode -> Ignore disableEncryptionUpdate` guard. That
assertion is **unverified** — it is exactly the kind of claim that needs a measured run.
Worth testing because it is a distinct flag from `disableEncryptionUpdate`, and our
binary demonstrably contains it.

**Engineer-mode "Encryption Update" toggle → `/update/disableEncryptionUpdate`.**
Upstream describes `S/W Update → Encryption Update → Disable` creating
`/update/disableEncryptionUpdate`, and "Enable" removing it. This matches our own
independent finding that `AppUpgrade` keys on exactly that file. Their reported engineer
PIN is `19190301`; ours is documented separately and the values are build-specific, so do
not assume transfer.

**`lightmediascannerd` runs as root and auto-indexes removable media.** Upstream's chain
depends on it. This matches our own privilege-surface work. See §3.

## 3. Highest-value new lead: LMS `id3.so` APIC integer underflow

Upstream `exploits/EXPLOIT_FINDINGS.md` reports a confirmed bug, quoted verbatim:

> "The `_parse` function in `/app/lib/lightmediascanner/plugins/id3.so` (LGE Gen5W IVI)
> has a systematic integer underflow in APIC (album art) frame processing that causes
> `lms_string_size_strndup(out, ptr, -1)` to be called with a negative length.
> On the real system, the real `lms_string_size_strndup` passes this as `size_t` to glibc
> `strndup()`, making it `SIZE_MAX` (0xFFFFFFFFFFFFFFFF). This triggers a massive heap
> buffer over-read through `strnlen()` followed by heap corruption."

> "APIC frame structure: `[enc=0x00][MIME\x00][pic_type][desc\x00][image_data]`. When
> `desc` is empty (just `\x00`), the parser calculates the text field length as
> `frame_size - overhead - 1`, which underflows to `-1`."

Their stated trigger is "**any** MP3 with a standard ID3v2.3 APIC frame with an empty
description field", delivered by USB, executed in `lightmediascannerd` as root — i.e. a
zero-interaction vector if it holds.

**Re-verification against our build:**

| item | ours |
|---|---|
| plugin path | `app/lib/lightmediascanner/plugins/id3.so` — **present** |
| size | 43,000 bytes (same as theirs) |
| sha256 | `0665fe8302cedf66d38c7cfd7e8eddd054a07ce2cbbc2d0e3ea80a24e766660b` |
| their sha256 | `0067c7e932885d6402de625f27be75141d3edf585b4794bfad41bf90cf096a38` |
| verdict | **different build of the same plugin** — same size, different hash |
| imports | includes `lms_string_size_strndup` (PLT `0x1bf0`), `calloc`, `malloc`, `memcpy`, `strlen`, `strchr` |
| strndup call sites | 8: `0x23a6, 0x24e0, 0x406c, 0x4266, 0x467d, 0x470b, 0x47aa, 0x4cef` |
| APIC handling | present: `=APIC`, `=PIC`, `Invalid picture type %d`, `Could not allocate memory for apic.` |
| consumer | `lightmediascanner_apic_save` is an **import**, so the picture-byte consumer lives in `liblightmediascanner.so`, not in the plugin |

Because the hashes differ, **the presence of the underflow in our build is not
established**. It must be re-derived from our bytes. That verification is the current
open item; the specific questions are: which of the 8 call sites is on the APIC/PIC path,
whether the length arithmetic can wrap, and whether our
`lms_string_size_strndup` clamps the length or forwards it to `strndup()` as `size_t`.

Until that is answered this is **candidate**, not confirmed.

## 4. Things upstream got wrong, and why it matters

Their commit `8473b25` had to correct their own documentation:

> "Fix ASLR documentation: userspace ASLR is enabled (randomize_va_space=2)"

and `a0936b8`:

> "Document RSA private key limitation and TOCTOU bypass across all docs"

Their jailbreak guide admits the signature will not verify and then hopes that
`AppUpgrade` "may not check DecryptToPIPE's exit code (common for pipe commands)". That
is speculation presented in a step-by-step guide. Their "Patches 1–4" (socat root shell
on port 4444, known root password, commented-out secure-console removal) are all patches
to **their own rootfs**, so they demonstrate a desired end state, not that a stock unit
reaches it.

Treat every upstream "works" statement as an untested hypothesis unless it names an
observation from a stock unit.

## 5. Reusable artefacts worth keeping

| path (upstream) | what it is | use to us |
|---|---|---|
| `exploits/RE_FINDINGS_usb_automount.md` | competent RE of `usb-automount` (43 KB, no RELRO, no stack canary) concluding **no** direct label→`system()` injection; mount dir is `sprintf("%s/%d/%s", cfg, part, ID_FS_LABEL)` used only with syscalls | saves us repeating this negative; also gives us the mount-path shape in case a *different* consumer reintroduces the label into a shell string |
| `exploits/tools/xcrypt.py` | Gen5W container crypto | we already have the key (`60a93d70f73302a63e5ed0d0ea38be22`, `tools/uk_fw/gen5w_decrypt.py`); compare IV derivation — they state IV = first 16 bytes of `SHA-256(filename + decimal_size)`, which is what we use |
| `exploit/.lge.upgrade.xml`, `2022_Cerato_AU.ver` | real manifest pair including per-file CRC32 + size list | shows the `.ver` manifest grammar; useful for understanding what the unit validates |
| `exploits/id3tag/gen_id3tag_poc.py` + samples | APIC/PIC frame construction | frame-layout reference for the §3 verification harness — do not use the samples as-is |

## 6. Bounds

- Upstream CLAIMS are quarantined in §2/§3 as claims. Only §1 and the §3 hash/import
  facts are things we measured ourselves.
- No exploit, media file or payload was produced or run.
- Nothing here is a root vector yet. The two live candidates are the untraced
  `system()` argument origin (§1) and the unverified APIC underflow (§3).
