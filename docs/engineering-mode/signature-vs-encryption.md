# Does "Encryption Update: Disable" bypass RSA signature verification?

Status: **read-only exact-binary static analysis.** No updater, helper, payload or
recovered executable was run. No package was staged, no partition written, no slot
changed, no USB media created. Nothing in `vm/` was touched.

Marks: **[E]** = evidenced by a quoted string, address, instruction or file;
**[I]** = inference, clearly labelled. Where the evidence does not reach, this note
says so instead of filling the gap.

## Answer in one paragraph

File id 10 is the marker file `/update/disableEncryptionUpdate`. Its presence means
"encryption update disabled", and the recovered FUMO updater reads that marker once at
start-up into a global mode byte (`.data` VA `0x6d20b4`, initial value `1`). The byte is
then a **policy switch, not an encryption-only switch**: with the marker present, the
descriptor reader skips its public-key verification and parses `.lge.upgrade.xml` as
plaintext, and `filterUpdateList` skips the component "HashCheck" function entirely. The
verifier itself is not mode-aware; the *calls* to it are. So on the paths that matter the
RSA/public-key check is gated by exactly this byte. What is **not** established here is
that an attacker can create the marker without a privileged write; the QML control that
nominally creates it is not implemented in this build.

**Static-mbedtls precondition (the published Chimaera attack): yes.** The updater set in
this image links mbedtls statically — the rootfs ships no `libmbedtls`/`libmbedcrypto` at
all, no `NEEDED` entry names one, and `mbedtls_ctr_drbg_random` /
`mbedtls_hmac_drbg_random` are *defined* inside each binary's own `.dynsym`. The paper's
exact dormant sink string `"Unexpected error, return code = %08X\n"` is present in those
binaries, including `app/share/AppUpgrade/DecryptToPIPE`. Its two call sites pass a
compile-time literal format, so the bug class is present as a *condition* but is not
reachable as shipped (§4). That matters for the question: the published route recovers
the **data** key, not a signing key, so it confirms the signature wall rather than
breaching it.

## Namespaces and exact identities

All addresses below are link-time virtual addresses in one exact embedded ELF. Its first
`PT_LOAD` has `vaddr - offset = 0`, so code/`.rodata` VAs equal file offsets; `.data` is
in the second segment (`delta 0x200000`), so `0x6d20b4` is file offset `0x4d20b4`. **[E]**

| Artifact | Identity |
|---|---|
| embedded FUMO updater, `work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf` | SHA-256 `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`, Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a` |
| outer `/app/bin/AppUpgrade` | SHA-256 `5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0` |
| `/app/bin/AppLogExtractor` | Build ID `beac12cfab550e848c07bf5c3e02e8de0aa03ca3` (stripped) |
| `/app/bin/AppDMClient` | SHA-256 `9a1fb796d7ac24fcce71c16e3dbee9306c888f43e705ee081f41b7d473978bd0` |

Which child runs matters: per `evidence/appupgrade-update-trust.md`, the recovered
`NE`/EUR option row carries `-un:0`, so the outer wrapper selects the **FUMO** child for
this vehicle. The gate below is FUMO's. **[E]**

---

## 1. What file id 10 actually controls

### 1.1 The QML control (already established, restated for the chain)

`app/share/AppEngineerMode/qml/Update/AppEngineerMode_Encryption_Update.qml` binds
`property bool statusFile: UpgradeVerInfo.checkUpdateFile(10)` and calls
`UpgradeVerInfo.disableUpdateFile(10)` / `enableUpdateFile(10)`. **[E]**

Two facts that the earlier note did not have:

- Neither `checkUpdateFile` nor `enableUpdateFile` exists as a byte string **anywhere**
  in the extracted rootfs except in the two QML files that call them (full-tree scan,
  both ASCII and UTF-16LE). `AppEngineerMode` does not contain them. **[E]**
- `AppEngineerMode` is a single x86-64 PIE with exactly one `\x7fELF` magic and no
  embedded child image, so this is not a "wrong binary" artefact. **[E]**

### 1.2 The one implementation that does exist: id → path is proved, not guessed

`AppLogExtractor` contains `void AppLogExtractor_CopyLogThrd::disableUpdateFile(int)`
as a `__PRETTY_FUNCTION__` string at `0x54ac0`, and the function itself is
`[0x289d0,0x28e2e)`. The dispatch is a literal compare chain, so the id mapping is
exact: **[E]**

```asm
289db: mov  ebx,esi                 ; id
28a07: cmp  ebx,0xa ; je 28d90      ; id 10
28a10: cmp  ebx,0xb ; je 28da8      ; id 11
28a19: cmp  ebx,0xc ; je 28dc0      ; id 12
28a22: cmp  ebx,0xd ; je 28dd8      ; id 13
...
28d90: lea  rdi,[rip+...]  # 532e0  ; "rm -rf /update/disableEncryptionUpdate"
28da8: lea  rdi,[rip+...]  # 53308  ; "rm -rf /update/test_scheduled_time"
28dc0: lea  rdi,[rip+...]  # 53330  ; "rm -rf /update/test_scheduled_controller"
28dd8: lea  rdi,[rip+...]  # 53360  ; "rm -rf /update/updateCompleteTime"
```

| id | marker path | verb |
|---:|---|---|
| 10 | `/update/disableEncryptionUpdate` | remove |
| 11 | `/update/test_scheduled_time` | remove |
| 12 | `/update/test_scheduled_controller` | remove |
| 13 | `/update/updateCompleteTime` | remove |

`disableUpdateFile` therefore **removes** the marker, which finally resolves the
label/verb mismatch visible in the QML: the button labelled *Enable* clears the
"disable" marker, i.e. it re-enables encrypted update, and the displayed state string
(`statusFile ? "Disable" : "Enable"`) names the *current* state, so marker present =
"Encryption Update: Disable". **[E]** for the removal and the ids; **[I]** for the
"shows current state" reading of `strSelectText`.

The matching creator exists elsewhere in the image. `AppMPAutoTest` carries a
factory-test event pair with the same path: **[E]**

```text
18baf0  rm -rf /update/disableEncryptionUpdate      ; ] EVT_MP_ENCRYPTION_ENABLE_REQ
18bb38  touch /update/disableEncryptionUpdate       ; ] EVT_MP_ENCRYPTION_DISABLE_REQ
```

That is independent confirmation of the polarity: **"ENCRYPTION_DISABLE_REQ" creates the
marker**, so the marker's presence is the disabled state, not the enabled one.

### 1.3 What the updater does with it

FUMO `main` (starts `0x27a10`, `QApplication` ctor at `0x27a55`) reads it once, early:
**[E]**

```asm
27a9f: lea  rsi,[rip+...]   # 2119f0  ; "/update/disableEncryptionUpdate"
27aab: mov  rdi,rbx
27aae: call 55b90                     ; QString ctor
27ac1: call 22d00                     ; QFile::QFile(QString const&)
27ac9: call 239a0                     ; QFile::exists()
27ad1: mov  ebp,eax
27ae0: test bpl,bpl
27ae3: je   27f14                     ; marker absent  -> keep default
27ae9: mov  BYTE PTR [rip+...],0x0    # 6d20b4    ; marker present -> mode = 0
27af5: lea  rsi,[rip+...]   # 211b43  ; "### Unencryption Update. ####"
...
27f19: lea  rsi,[rip+...]   # 211b7b  ; "### Encryption Update. ####"
```

The default is not a leftover: `.data` byte at VA `0x6d20b4` is `0x01` in the shipped
file, so *absent marker ⇒ mode 1 (encryption update on)*, and `main` only ever writes
`0`. **[E]**

So file id 10 controls **one global boolean that the whole updater consults**, named by
its own log strings as the encryption/unencryption update mode. Thirty-eight instruction
sites read `0x6d20b4` in this ELF. **[E]**

---

## 2. Does signature verification consult that state?

### 2.1 The verifier is not mode-aware

The fixed-public-key verifier wrapper is `[0x45820,0x45d75)`: it starts by loading the
key pathname `0x209d5a` = `teruten5_pub.key` and calls the signed-container driver
`0x18f740` at `0x45a76`. **[E]**

```asm
45822: lea  rdi,[rip+...]  # 209d5a   ; "teruten5_pub.key"
45a73: mov  rsi,r15
45a76: call 18f740                    ; signed-container driver
45a7b: ...  mov ebp,eax               ; status returned to caller
```

There is **no reference to `0x6d20b4` anywhere inside `[0x45820,0x45d75)`**. The check
itself is unconditional; only its callers decide whether it runs. **[E]**

This matters for the premise. The strings `"RSA key validation"` (`0x45d0e1`) and
`"PKCS#1 sig. verify"` (`0x45d152`) are not the updater's messages: they sit in a
contiguous `.rodata` blob that also contains a hex modulus, `10001`, and
`"PKCS#1 decryption :"`, `"PKCS#1 encryption :"`, `"PKCS#1 data sign  :"` — i.e. the
mbedtls `rsa_selftest()` text and test vector. They evidence that an RSA-capable mbedtls
is statically linked; they do **not** evidence that the update path verifies anything.
**[E]** for the blob contents; **[I]** for the `rsa_selftest` attribution.
Whether the `0x18f740` driver is RSA specifically was not re-derived here; it is a
public-key container verifier keyed by `teruten5_pub.key`. **[I]**

### 2.2 Site A — the descriptor `.lge.upgrade.xml` is not verified when the marker is present

Descriptor reader `[0x7bc50,0x7f82a)` is reached from start-up initialiser `[0x8dc60,…)`
at `0x8dcf4`, and that initialiser is reached from the application object constructed in
`main` at `0x126d09`. The mode read is immediately before the verify/skip decision:
**[E]**

```asm
7bd6c: movzx r12d,BYTE PTR [rip+...]   # 6d20b4
7bd74: mov  rax,QWORD PTR [rbp+0x0]    ; base directory QString
7bd78: test r12b,r12b
7bd7b: je   7c270                      ; mode 0  -> NO VERIFICATION
...                                     ; mode 1  -> build "<base>/.lge.upgrade.xml"
7be3a: call 45820                       ; public-key verification of the descriptor
7be47: mov  ebp,eax
7be6a: test ebp,ebp
7be6c: jne  7c430                       ; nonzero -> failure path
```

and the taken-on-disabled branch: **[E]**

```asm
7c270: mov  ecx,DWORD PTR [rax]
7c296: lea  rsi,[rip+...]  # 212258    ; "/.lge.upgrade.xml"
7c2ee: call 22d00                       ; QFile::QFile
7c31d: call 22690                       ; QFile::open(ReadOnly)
7c6d9: call 22b70                       ; QDomDocument::setContent
```

So with `/update/disableEncryptionUpdate` present, the descriptor is opened and parsed as
a plaintext XML document with **no** call to `0x45820` on that path. A whole-function scan
of `[0x7bc50,0x7f82a)` finds exactly one `call 45820`, at `0x7be3a`, on the other side of
this branch. **[E]**

### 2.3 Site B — firmware component verification is skipped outright

`filterUpdateList` `[0x8acf0,…)` (log tag string `0x213950` = `"filterUpdateList"`) logs,
`sync`s, builds the update list (`0x81240`), and then: **[E]**

```asm
8ad3b: cmp  BYTE PTR [rip+...],0x0    # 6d20b4
8ad42: je   8ae5f                      ; mode 0 -> jump over the check
8ad48: mov  rdi,rbp
8ad4b: call 7fe40                      ; "HashCheck"
8ad50: test al,al
8ad52: jne  8ae5f                      ; check passed -> same continuation
```

`0x8ae5f` is the shared continuation (`0x89e50`, `0x85ca0`, then `0x80a00`, `0x83c40`,
`0x84f40`). Mode 0 and "verification passed" are indistinguishable downstream. **[E]**

`0x7fe40` is the component check; its log tag is `0x213938` = `"HashCheck"`, and it calls
the same verifier `0x45820` twice: **[E]**

- `0x80095`, over a path built from `0x213074` = `"%1/HU/firmware/modem/%2"`;
- `0x802f0`, over a path built from `0x2130d9` = `"%1/HU/firmware/update.tar.gz"`;
- its own failure text is `0x2125b8` = `"[%s] --> Firmware Update file is non-encryption!!"`.

Calling it "HashCheck" is the binary's own naming; the two calls it makes are to the
public-key verifier, not to a bare digest routine. **[E]** for the name and calls;
**[I]** for "the name understates what it does".

### 2.4 Where the byte is *not* consulted

This is not "every check is skipped". There are 38 readers of `0x6d20b4`; four of the six
verifier call sites sit in functions with no local mode read: `0x9d1d2`
(`[0x9cbc0,0x9e260)`, controller `.enc` resources), `0x100bb0` and `0x140092`
(`decryptionFile` / whatsnew paths). Those routes keep authenticating unless an
unresolved caller gates them. **[E]** for the local absence of a gate; **[I]** for the
upstream.

One more gate is *not* a signature check and should not be described as one: at
`0xc0816` the writer-side path reads the same byte and sets a per-record flag: **[E]**

```asm
c0816: cmp  BYTE PTR [rip+...],0x0    # 6d20b4
c0820: je   c0829                      ; mode 0 -> leave record+0x9c = 0
c0822: mov  BYTE PTR [rdi+0x9c],0x1    ; mode 1 -> enable the pre-write source gate
```

`record+0x9c` selects the pre-write source/hash gate documented in
`evidence/appfumo-partition-write-integrity.md` (source gate `0xc1ff0`). That gate calls
`0x43890`, `0x45d80`, `0x43b20`, `0x45370` and `QFile::exists` — **no** `call 45820` — so
it is a hash/consistency gate, not the public-key verifier. **[E]** for the call set;
**[I]** for the "hash, not signature" classification of those helpers.

---

## 3. The direct answer, and what it is worth

**With the encryption update disabled, the RSA/public-key signature is *not* verified on
the two payload-critical routes** — the `.lge.upgrade.xml` descriptor and the
`filterUpdateList` component check — because the mode byte suppresses the calls to
`0x45820` rather than the verifier's own logic. Elsewhere in the same binary the
verification still runs. Confidence: **high** for the control flow (§2.2, §2.3 are
straight-line branch facts with quoted instructions); **medium** for the end-to-end
effect, because reachability is not uniform.

Reachability caveats, stated plainly:

- The descriptor gate is statically reached from `main` (§2.2). **[E]**
- `filterUpdateList` has **no direct caller**: `0x8acf0` appears only in a `.data.rel.ro`
  relocation at `0x6cdb78` (type 8, `R_X86_64_RELATIVE`), i.e. it is a **virtual method
  reached through a vtable**. Which state-machine entry invokes that slot at runtime was
  not resolved in this pass. **[E]** for the vtable slot; **[I]** for "it runs during an
  update".

### Practical consequence

1. **It is not a decryption-only switch.** The disabled state removes, on its own, two
   independent public-key verifications of update material inside the updater. A
   modified `update.tar.gz` or a modified descriptor does not meet the verifier on those
   paths. **[E]**
2. **The parent stager is inverted, not switched off.** On the unequal AppUpgrade path,
   `AppDMClient` requires retained verifier results `0/0` when the marker is absent and
   `-404/-404` when it is present (`0x80bc2` → `0x815e0` `or`/`jne`; `0x80bc8`/`0x80bd6`
   compare against `0xfffffe6c`; helper `[0x696f0,…)` returns `QFile::exists(marker) ^ 1`
   so the `jne` on it means "marker absent"). `-404` is "the file lacks a recognised
   `TER`/`TE2` trailer" — a *format* result, not a cryptographic pass. So the plaintext
   arrangement is admitted on purpose, without either file being authenticated. **[E]**
3. **What stays shut.** (a) The trust anchor is a normal file, `app/share/AppUpgrade/teruten5_pub.key`
   (mode 0755, 294 bytes) on a root that mounts `rw` — replacing it is a separate,
   *equally* effective route that does not need this marker (V-034). (b) The boot
   containers carry their own RSA-2048 signature (`evidence/eu-boot-container-signature.md`);
   whether the loader rejects a re-signed container is an open bench question, so nothing
   here should be read as "modified firmware boots". (c) Descriptor version/model/region
   logic and every check listed in §2.4 are untouched by the byte.
4. **The precondition is the whole finding.** Producing the marker requires a write to
   `/update`. On this build the engineering-mode UI cannot do it (the reader/writer
   methods are absent, §1.1); the writers that are present are `AppMPAutoTest`'s
   factory-test event handler and whatever calls `enableUpdateFile`. Whether the marker
   is reachable by anything short of root was **not** established here, and the
   `/update` mount's uid/gid, mode and SMACK label were not measured. Treat this as "the
   signature wall has a documented service hatch, and the hatch's lock state is
   unmeasured", not as an unauthenticated USB bypass. **[I]**

---

## 4. Does our image match the paper's precondition (statically linked mbedtls)?

Yes. This is a measured check, not a citation of the paper's claim about its own build.

| Binary | `libmbed*` in `NEEDED` | mbedtls functions *defined* in the ELF (order: `ctr_drbg_random`, `hmac_drbg_random`) | Chimaera sink string |
|---|---|---|---|
| `/app/bin/AppUpgrade` (outer Qt wrapper) | no | none | absent |
| embedded FUMO updater | no | `mbedtls_ctr_drbg_random` @`0x198c00`, `mbedtls_hmac_drbg_random` @`0x1d9590` | present |
| embedded SCOMO updater | no | @`0x1ff060`, @`0x23f9f0` | present |
| `/app/bin/AppDMClient` | no | @`0x12a500`, @`0x16ae90` | present |
| `/app/bin/AppScomoDM` | no | @`0xec930`, @`0x12d2c0` | present |
| `app/share/AppUpgrade/DecryptToPIPE` | no | @`0x13ae0`, @`0x54470` | present |
| `/app/bin/AppEngineerMode` | no | none | absent |

Evidence for the table:

- A whole-rootfs `find` for `*mbed*` returns **nothing**: no shared mbedtls object is
  shipped, so a `NEEDED` entry could not have resolved anyway. **[E]**
- The only crypto shared library in `NEEDED` for these binaries is
  `libcrypto.so.1.0.2` (OpenSSL 1.0.2), plus Qt5/dlt/libc. No `libmbed*` appears in any
  `DT_NEEDED` list. **[E]**
- Instead, `mbedtls_ctr_drbg_random` and `mbedtls_hmac_drbg_random` are **defined**
  symbols in the binaries: `.dynsym`, `st_shndx 13` (`.text`), `STT_FUNC`, `STB_GLOBAL`,
  `STV_DEFAULT`. Defined-and-not-imported is the direct evidence of a static link. **[E]**
- The *negative* half of the proposed test is worth recording: there is **no long run of
  `mbedtls_` strings**. Each binary contains exactly three `mbedtls_` tokens — the two
  symbol names above and one sample-program line — and no `mbed TLS x.y.z` banner. The
  static link was made with default visibility on only those two functions, so a
  string-run heuristic would have missed it. **[E]**
- Library identity is corroborated by library-internal text in the same `.rodata`:
  `"RSA key validation:"`, `"PKCS#1 decryption :"`, `"PKCS#1 encryption :"`,
  `"PKCS#1 sig. verify:"` next to a hex modulus and `10001` (mbedtls `rsa_selftest`
  data), and `"  failed\n  ! mbedtls_rsa_pkcs1_decrypt returned %d\n\n"` beside
  `rsa_decrypt` / `rb` / `%s%d` (the mbedtls `programs/pkey/rsa_decrypt` sample text).
  **[E]** for presence; **[I]** for the source-file attribution.

### 4.1 The sink exists; the vulnerability does not (as shipped)

The paper's string is at `DecryptToPIPE` `.rodata` VA `0x5e718` and is referenced
**exactly twice** in the whole binary. Both are the mbedtls self-test idiom
`if (ret < 0 && verbose != 0)`: **[E]**

```asm
12b20: mov  edx,r15d            ; return code
12b23: mov  edi,0x1             ; __printf_chk flag (FORTIFY_SOURCE)
12b28: xor  eax,eax
12b2a: lea  rsi,[rip+...]       # 5e718   ; fixed format literal
12b31: call 7d90 <__printf_chk@plt>

4fe18: mov  eax,r15d
4fe1b: shr  eax,0x1f
4fe1e: je   4fe98              ; ret >= 0 -> skip
4fe20: test r14d,r14d
4fe23: je   4fe98              ; verbose == 0 -> skip
4fe25: mov  edx,r15d
4fe28: mov  edi,0x1
4fe2d: xor  eax,eax
4fe2f: lea  rsi,[rip+...]       # 5e718
4fe36: call 7d90 <__printf_chk@plt>
```

The embedded FUMO/SCOMO updaters contain the same pair of sites with the same shape
(`__printf_chk(1, <literal>, rc)`). Answering the specific question: **no mbedtls
function in this image takes a caller-controlled format string.** At both sites the
format operand is a compile-time literal, the sink is the FORTIFY `__printf_chk` (which
would additionally reject `%n`), and those two `lea`s are the complete reference set for
the string. The `mbedtls_printf` *call* is present and dormant, which is the condition
the paper exploits — but it becomes a leak only after code modification, which is exactly
what the paper did (injected assembly that re-enters the call and prints registers).
"Statically linked mbedtls" is therefore the precondition, not the vulnerability. **[E]**
for the call sites and the complete xref set; **[I]** for the exploitability conclusion.

### 4.2 What that does to the signature question

The paper's chain needs *three* things: the data key (Chimaera), a payload the updater
will accept, and a signature it will accept. Chimaera supplies only the first. It yields
the AES-CBC data key; the signature is RSA and the private half is not recoverable from
it — the authors say so directly (`"we can not replicate the digital signature because we
have retrieved only the public RSA key"`). The 294-byte
`app/share/AppUpgrade/teruten5_pub.key` in this image is a public key. **[E]** for the key
file and the paper text; **[I]** for "no private key material in the image" — no such
material was located in this pass, which is not a proof of absence.

So the published answer is consistent with §2–§3 rather than an alternative to them:
**the signature is an independent wall that the encryption compromise does not breach.**
The marker (id 10) and the trust-anchor replacement (V-034) reach the same wall from
other directions; Chimaera does not reach it at all without binary patches.

## 5. The linked paper

Costantino, De Vincenzi, Matteucci, *"A vehicle firmware security vulnerability: an IVI
exploitation"*, **Journal of Computer Virology and Hacking Techniques 20(4):681–696
(2024)**, DOI `10.1007/s11416-024-00522-4`. Open access (hybrid, CC-BY) per Crossref and
OpenAlex. **[E]**

Retrieval: `link.springer.com` (both the article and the PDF endpoint) returned a
3,038-byte JavaScript "Client Challenge" page, i.e. blocked; Crossref metadata and the
rendered full text via a text-extraction proxy were used instead. Nothing below is
inferred from the DOI alone. **[E]**

### What it covers

Subject is `AE_E_PE_EUR.S5W_L001.001.211214` on a Gen5W_L unit — the same product family
and the same update stack (`DecryptToPIPE`, `AppDMClient`, `AppUpgrade`,
`.lge.upgrade.xml`). Its chain: **[E]**

- `DecryptToPIPE` statically links mbedtls, leaving an unused
  `mbedtls_printf("Unexpected error, return code = %08X")`; patched assembly re-uses it to
  print registers, leaking stack values including the wrapped **AES-CBC-128** key.
- They read the **RSA public key** (`n`, `e`) and the encrypted AES key from `Key_file`,
  reproduce the unwrap in C, and recover the AES key; then reproduce SHA-256 and the IV
  derivation, so files can be decrypted and re-encrypted.
- File format as described: content, `TE2`/`TER` terminator, 32-byte SHA-256, then a
  16,384-byte RSA signature.
- **Verification is a genuine wall.** They state they cannot forge it: *"we can not
  replicate the digital signature because we have retrieved only the public RSA key and
  it is not feasible to try to find a private RSA key from a public RSA"*, and that *"the
  lack or incorrect signature can block the installation"*. Their workaround is to copy
  the original signature or append 16,384 `0xFF` bytes, and then **patch the check out of
  the binaries**.
- The bypass is a binary patch: they locate the `-403` (`0xfffffe6d`) result in
  `AppDMClient` from the log, change `JZ` to `JMP`; they do the same in `AppUpgrade` to
  skip the per-file signature check and allow "firmware versions with any date". They
  also replace `AppDMClient` on the head unit to carry the patch.
- Demonstrated outcome: a package whose `.lge.upgrade.xml` declares
  `AE_E_PE.EUR.CHIMAERA_CF01.808489` is read and accepted on the unit; post-exploitation
  covers remote command injection onto M-/B-/C-CAN. Entry precondition is stated as an
  existing 1-day (AppNavi) or previously installed custom firmware.
- Four CVEs: CVE-2023-26243 … CVE-2023-26246.

### Does it bear on signature verification or firmware modification?

Yes, centrally — but it answers a different question from ours. The paper **confirms the
signature is real and unforgeable** and bypasses it by **modifying the verifier binaries**.
It contains **no mention of `disableEncryptionUpdate`, of an engineering/developer mode, of
a plaintext update mode, or of the `-404` result** (full-text search for
"disable"/"engineering"/"-404"/"plain": only unrelated hits such as "disable the car's
firewall"). **[E]** So it neither supports nor contradicts the claim our measurement
makes — that the same wall is opened *by data alone* when that marker exists. That is a
genuine delta of this project over the paper, **conditional on the marker's reachability**
(§3.4).

---

## 6. Comparison with this repository's existing coverage

**Already covered, and already reconciled.** `evidence/chimaera-technique-analysis.md`
summarises the paper phase by phase, records that the cipher is **AES-CBC-128 rather than
AES-256**, that the key material is public-key-wrapped and recoverable from a device file
pair, and that the IV is derived rather than random (matching this project's identical
14,059-byte package tails). It also does what the paper does not: **binds the published
trailer shape to the exact recovered verifier** — `AppDMClient` parser `0x11fe20` seeking
to `file_size - 0x4024`, accepting only `TER`/`TE2` suffixes, `-404` at `0x11ff26` for
"no trailer", `-403` at `0x120f73..0x120f7a` for a 32-byte mismatch. The paper's
`0x4024` = 36-byte terminator/hash area + 16,384-byte signature reconciles exactly.
**[E]**

**Register status already reflects the wall's independence.** V-005 keeps "native
decryption recovery is not equivalent to a signature bypass" as an explicit
non-promotion. V-031/V-032 map the verifier inventory. V-034 records that the trust
anchor is an ordinary 0755 file on a `rw` root. Nothing in this note contradicts any of
them; §2–§3 supplies the missing *policy* input those entries listed as unknown (the
condition under which the verifier is not called). **[E]**

**What this repository had not measured before this note.** (a) The static-mbedtls
condition *in our own image*: `chimaera-technique-analysis.md` reports the paper's claim
about its build, but the symbol/NEEDED check in §4 had not been run here, so "our
`DecryptToPIPE` is the same kind of object" was unverified. (b) The id→path mapping and
the polarity of the marker (now proved by the compare chain and by
`EVT_MP_ENCRYPTION_DISABLE_REQ → touch`). (b) That the mode byte gates **which calls to
the verifier happen**, not what the verifier does. (c) The two specific skipped checks
(descriptor, `filterUpdateList`). (d) That `record+0x9c` (pre-write hash gate) is set
from the same byte at `0xc0816`. **[E]**

**What the paper describes that this project has not measured.** Not nothing: the paper
demonstrates an end-to-end installation of modified firmware on a physical head unit and
a working re-encryption/IV pipeline; this project has run neither. The open gaps it
highlights are concrete:

1. **A live acceptance experiment.** The paper's Fig. 15 (a `CHIMAERA_CF01` version string
   read from the unit) is a real acceptance observation. Everything here stops at static
   control flow plus a boot-container format description; enforcement at the loader is
   still an unrun bench experiment (`evidence/eu-boot-container-signature.md`).
2. **The AES key in hand.** The paper actually extracts it. This project deliberately does
   not reproduce the key-extraction code (`chimaera-technique-analysis.md`, "What is
   deliberately not reproduced here"), so the IV algorithm and the unwrap are taken from
   the paper rather than independently confirmed.
3. **The post-exploitation surface.** CAN frame injection and the cellular/gateway
   manipulation are outside this repository's measurements.
4. **One format disagreement is still open** and is not resolved by either side: the paper
   describes per-file SHA + signature, while this project measured a *shared*
   14,059-byte tail across three files in one package. The paper's per-file explanation
   would predict differing tails. **[E]** for both observations; the reconciliation in
   `chimaera-technique-analysis.md` is explicitly labelled open.

**What the paper's threat model implies for §3.** Their patch route requires writing to
`/app/bin` on the unit; our marker route requires writing to `/update`. Both are
post-compromise on the same writable root, which is why neither should be sold as an
unauthenticated USB attack. The difference that matters for defenders: a binary patch is
detectable by hashing `/app/bin`, while a one-byte-state marker on a data partition is
not.

---

## 7. What would change this conclusion

0. Show that the dormant `__printf_chk` sink is reachable with a caller-supplied format
   string *without* modifying the binary. Nothing in §4.1 suggests it is; if it were, the
   key-material route would stop requiring a patched helper and would compete with §2 as
   a first-entry route.
1. Read `/update`'s uid/gid/mode and SMACK label on a live unit, and test whether any
   non-root path (AppMPAutoTest event, D-Bus, USB-borne script) can `touch` the marker.
2. Resolve the vtable dispatch at `0x6cdb78` to the state-machine entry that invokes
   `filterUpdateList`, so §2.3 stops being "a virtual method that will run during an
   update" and becomes an observed ordering.
3. Confirm the `0x18f740` driver's algorithm. Until then "RSA" is inherited from the key
   filename and the linked mbedtls, not from a located RSA call in the verifier.
4. Bench: does the loader accept a re-signed `ipk.` container? That is the wall that
   survives both this marker and the paper's patches.

## Evidence index

- Binary: `work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf`
  (disassembly reproduced with `x86_64-linux-gnu-objdump -d -M intel`, this pass).
- `work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/share/AppUpgrade/DecryptToPIPE`,
  SHA-256 `e3110811e83701368e638947e6d8887f59321707e70f6288adf0790090d929c0`,
  Build ID `4303e27a93f0acfb308146a5d034dafbffa064d0`, 559,192 bytes, stripped.
- Rootfs: `work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/{bin,share}`.
- Prior notes built on: `evidence/appupgrade-update-trust.md`,
  `evidence/appfumo-authentication-coverage.md`,
  `evidence/appfumo-partition-write-integrity.md`,
  `evidence/chimaera-technique-analysis.md`, `evidence/engineering-mode-dev-activation.md`,
  `docs/engineering-mode/dev-mode.md`, `Ioniq5-VULNERABILITIES.md` V-005/V-031/V-032/V-034.
