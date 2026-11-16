# AppLauncher binary signature check — recovered algorithm and trust model

Status: read-only static reconstruction of `/app/bin/AppLauncher` from the recovered
EU `260128` rootfs (`work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/AppLauncher`,
BuildID `0452df1033bd1bbae15727a83d4d56576d8b9444`, stripped, dynamically linked,
**OpenSSL `libcrypto.so.1.0.2`**, *not* mbedTLS). Nothing under `work/vm/` was touched.
No target binary was executed, no key was generated, and no signature was produced.

Addresses are link-time VAs; for the first `PT_LOAD` of this PIE, file offsets equal VAs
(`.text` 0xb080, `.rodata` 0x466a0). All quotes are from capstone 5.0.7 disassembly.

---

## TL;DR

- The `.sign` section is located **by ELF section-header walking (name lookup through the
  section-header string table)**, not by a fixed file offset. Its raw bytes are written to
  `/tmp/<basename>.sign`, and its `sh_offset` is recorded in the check-context object.
- The check is **SHA-256 over the whole binary with the `.sign` section bytes zeroed out**,
  then **`RSA_verify(NID_sha256, …, 256-byte signature, …, PEM RSA public key)`** —
  i.e. RSA with **PKCS#1 v1.5** padding (OpenSSL default for `RSA_verify`).
- The public key is **PEM SubjectPublicKeyInfo** (`PEM_read_RSA_PUBKEY`), read fresh from
  `/tmp/app_normal.key` (or `/tmp/navi_public.key`) on every check.
- The trusted keys are **pinned inside the binary as Qt resources** `:/app_normal.key` and
  `:/navi_public.key` (two embedded 2048-bit RSA PEM keys), copied **once** to `/tmp` at first
  use of a singleton object. **The verifier trusts the `/tmp` copy and never re-checks it
  against the embedded resource.** ⇒ a key written to `/tmp/app_normal.key` is accepted.
- The verifier returns **1 iff `RSA_verify(...) == 1`**, else 0. The launch path tolerates only
  the value **1**; any 0 jumps to the no-launch/error branch.

---

## 1. Where the `.sign` section is read, and how

[E] `readSection` at VA **0x15b50** opens the binary with `open(path, O_RDONLY)` (0x15c5b),
`elf_version(1)` (0x15c91), `elf_begin(fd, ELF_C_READ, NULL)` (0x15c9f), then:

```asm
15cc8: movzx esi, word ptr [rax + 0x3e]   ; e_shstrndx
15ccf: call 0xa5a0                        ; elf_getscn(elf, e_shstrndx)
15ce2: call 0xad70                        ; elf_getdata(shstrtab_scn, NULL)  -> Elf_Data*
15ce7: mov r15, rax
```

It then loops sections with `elf_nextscn` + `elf64_getshdr` (0x15d28/0x15d41), computes each
section name as `&shstrtab_data[sh_name]` (0x15d51–0x15d6a), and compares it to `.sign`
case-sensitively:

```asm
15ef5: mov r8d, 1                     ; Qt::CaseSensitive
15efb: mov ecx, 0xffffffff            ; length = strlen
15f00: lea rdx, [rip + 0x30eea]       ; ".sign"  (0x46df1)
15f0e: call 0xa710                    ; QString::compare_helper
15f13: test eax, eax
15f15: jne 0x15f5f                    ; not ".sign" -> next section
```

On a match it opens the output path (the context field at `+0x28`, later shown to be
`/tmp/<basename>.sign`), fetches the section's raw data, and writes it out:

```asm
15f17: mov rsi, [rsp + 0x30]          ; &ctx+0x28 (output .sign path)
15f1f: call 0xa2b0                    ; QFile::QFile(path)
15f2c: call 0x9fe0                    ; QFile::open(OpenMode 3)
15f3e: mov rdi, rbx                   ; Elf_Scn* (.sign section)
15f41: call 0xa830                    ; elf_rawdata(scn, NULL) -> Elf_Data*
162a7: mov rsi, qword ptr [rax]       ; d_buf  (raw .sign bytes)
162aa: mov qword ptr [rbx + 0x230], rdx   ; store sh_offset into ctx+0x230
162b1: movsxd rdx, dword ptr [rax + 0x10] ; d_size
162b5: call 0xa4c0                    ; QIODevice::write(d_buf, d_size)
```

where `rdx` at 0x162aa was loaded by `49 8b 54 24 18` = `mov rdx, [r12+0x18]` (`r12` =
the `.sign` section's `Elf64_Shdr*`), i.e. **`sh_offset`**.

[E] Conclusion: the `.sign` bytes are read **from the ELF section table by name**, via libelf
`elf_rawdata`, and the section's **`sh_offset` is stored at `ctx+0x230`** for the hashing step.
There is **no fixed file offset**; the offset varies per binary.

[E] The measured log line `section name = [.sign]  size[256][266]` is emitted at 0x15dee with
format `"section name = [%1]  size[%2][%3]"` (0x47398). Decoding the arg chain (0x15de4–0x15e5b):
`%2 = [r12+0x20]` = the section header's **`sh_size` = 256**, and `%3 = [r15+0x10]` =
**`d_size` of the section-name string table** (not the signature). For `AppStandbyClock` the
string table is exactly 0x10a = **266**, matching the log. The 266 is *not* the signature size;
the signature size is the `.sign` section size, 256.

## 2. Exact algorithm

[E] Two near-identical crypto helpers exist. The one used by the normal app-launch path is
**`signCheck` at VA 0x127d0** (called from `readSection` at 0x162c5). A sibling **`CheckSign` at
VA 0x12100** hashes the *whole* file with no zeroing and is used by the app-id-30 (navigation)
path. Both share this core:

- `SHA256_Init` → read the data file in 0x200-byte chunks with `fread` → `SHA256_Update` →
  `SHA256_Final` (0x12891 / 0x128e2 / 0x12a83 / 0x12c50 in `signCheck`).
- Read the signature file into a 0x200-byte buffer, remember `bytes_read`
  (0x12cf0, siglen at `[rsp]`).
- `PEM_read_RSA_PUBKEY(fp, NULL, NULL, NULL)` on the key file (0x12d86).
- `RSA_verify(...)` (0x12daa).

[E] **Hash coverage — the `.sign` section is excluded.** In `signCheck`, `rbx = [ctx+0x230]`
(the `sh_offset` recorded by `readSection`) and `r13 = rbx + 0x100`. Inside the hashing loop,
just before `SHA256_Update`, the code zeroes the in-buffer region `[rbx, min(r13, 0x200))`
(0x128f2–0x1292d) and decrements `rbx`/`r13` by 0x200 each chunk (0x12a6a–0x12a7c). This zeroes
exactly the 256 signature bytes so they do not contribute to the digest. The signature is then
verified against a SHA-256 of *the rest of the file*.

[E] **Verification call and argument order** (in `signCheck`, the launch-path function):

```asm
12d7d: mov rdi, r12                   ; FILE* key  (PEM)
12d80: xor ecx, ecx
12d82: xor edx, edx
12d84: xor esi, esi
12d86: call 0xa4f0                    ; PEM_read_RSA_PUBKEY(fp, NULL, NULL, NULL)
12d8b: mov r8d, dword ptr [rsp]       ; siglen = bytes read from .sign file (256)
12d8f: mov rcx, r14                   ; sigbuf = signature bytes buffer
12d92: mov rsi, rbx                   ; digest = SHA-256 output (32 bytes)
12d95: mov edx, 0x20                  ; digest_len = 32
12d9a: mov r9, rax                    ; RSA* public key
12da5: mov edi, 0x2a0                 ; 0x2a0 = 672 = NID_sha256
12daa: call 0xa7e0                    ; RSA_verify(type, digest, 32, sig, siglen, rsa)
```

[E] So the call is `RSA_verify(672 /*NID_sha256*/, sha256_digest, 32, sigbuf, siglen, rsa)`.
`0x2a0 = 672` is OpenSSL's `NID_sha256`. `RSA_verify` with a non-zero type builds the SHA-256
`DigestInfo` and uses **PKCS#1 v1.5** padding (OpenSSL's `RSA_PKCS1_PADDING` default), so the
scheme is **SHA-256 + RSA/PKCS#1 v1.5**. The identical sequence appears in `CheckSign` (0x12100)
at `PEM_read_RSA_PUBKEY`=0x123d3 and `RSA_verify`=0x123fe.

[E] Signature size is 256 bytes ⇒ **RSA-2048**. (`.sign` `sh_size = 0x100` in
`AppStandbyClock`; signature is raw RSA bytes, not PEM/DER — first 16 bytes
`81 6c 31 14 4e 30 3f 99 f8 43 2c 3a 04 2c e7 43`.)

## 3. Key file format — the parser

[E] The key is parsed by **`PEM_read_RSA_PUBKEY`** (OpenSSL), i.e. it expects **PEM
SubjectPublicKeyInfo (`-----BEGIN PUBLIC KEY-----`)**, *not* raw modulus and *not* DER-only.
Call sites: 0x123d3 (`CheckSign`) and 0x12d86 (`signCheck`), each with the canonical
`(fp, NULL, NULL, NULL)` argument list shown above. The two embedded keys are both 294-byte
DER SPKI / 450-byte PEM (**2048-bit RSA**).

[E] The key path is a hard-coded literal in the context-setup code (0x156c8 loads
`"/tmp/app_normal.key"`, 0x180e1 loads `"/tmp/navi_public.key"`), and the verifier `fopen`s that
path fresh on every check (0x1239b / 0x12d4e), so **the file is re-read each time**.

## 4. Is the trusted key pinned, or is `/tmp` authoritative?  ← decisive for V-048

[E] **Both pinned and `/tmp`-authoritative, with no re-validation:**

1. The binary embeds two PEM public keys (both `-----BEGIN PUBLIC KEY-----`,
   2048-bit RSA), at file offsets **0x52f04** (SHA-256 `04c47f95…d01929`) and **0x530cb**
   (SHA-256 `5d59e2c6…9bf0fb`).
2. The Qt resource names `:/app_normal.key` (0x48c8b) and `:/navi_public.key` (0x48caf) are used
   as the *sources* of a one-time copy (0x20e05 / 0x20e8d):

```asm
20e05: lea rdi, [rip + 0x27e7f]       ; ":/app_normal.key"
20e11: mov rsi, rbp
20e14: mov rdi, r13
20e1c: call 0xa2b0                    ; QFile(":/app_normal.key")
20e29: lea rdi, [rip + 0x25fe9]       ; "/tmp/app_normal.key"
20e3d: mov rsi, rbp
20e40: mov rdi, r13
20e45: call 0xa260                    ; QFile::copy -> "/tmp/app_normal.key"
```

   and identically `:/navi_public.key` → `/tmp/navi_public.key` at 0x20e8d–0x20ed2.
3. This copy lives in the constructor **0x20ac0**, which is instantiated **once** through a
   function-local-static guard (`0x21122` calls 0x20ac0; global cached at 0x265560; `new(0x80)`
   at 0x21110). It is *not* repeated per launch.
4. The verifier path strings are the `/tmp` literals (context setup 0x156c8 / 0x180e1), and
   `PEM_read_RSA_PUBKEY` opens that `/tmp` path on every verification. **No code compares the
   `/tmp` file against the embedded resource.**

[I/E] Therefore the embedded PEM keys are the *initial* trust anchor, but the **enforcement
reads `/tmp/app_normal.key` (and `/tmp/navi_public.key` for app id 30) at check time**. If an
attacker can write their own PEM public key to `/tmp/app_normal.key` after the one-time copy
(a writable `/tmp` plus any primitive that lets them drop a file there — the same class of
precondition as the existing `/tmp` findings), **their key is accepted and they can sign
arbitrary app binaries**. This makes V-048 real: the signature check is a *key-location* trust
boundary, not a hard-pinned-key boundary at the point of verification.

[I] Name↔data mapping: the resource tree stores the names `app_normal.key` (UTF-16 @ 0x52ea7)
and `navi_public.key` (UTF-16 @ 0x52ec9) immediately before the two PEM blobs; by proximity the
first PEM (0x52f04) is `:/app_normal.key` and the second (0x530cb) is `:/navi_public.key`. The
*fingerprints* are measured; the *name assignment* is inference.

## 5. Return value and enforcement

[E] Both crypto helpers return `(RSA_verify(...) == 1)`:

```asm
12f17: cmp r14d, 1
12f1b: sete al
```

so **1 = valid, 0 = invalid-or-any-error** (bad file opens, missing section, PEM failure,
`RSA_verify != 1` all collapse to 0; the helpers also emit `CheckSign false 1/2/3` for the three
`fopen` failures — data file / signature file / key file respectively — at 0x126f0/0x12283/0x12720).

[E] Enforcement in the launch handler (the function that ends in `QProcess::start` at
0x17eb2/0x18169; `rbx+0x20` holds the app id):

- Normal apps (app id ≠ 30): 0x17e4e builds `/tmp/<basename>.sign` (helper **0x158c0**), then
  0x17e78 calls `readSection` (which extracts `.sign` and runs `signCheck`), and:

```asm
17e7d: test al, al
17e7f: je  0x18088        ; signature failed -> error path, NO launch
17eb2: call 0xa740        ; QProcess::start(...)  only on ret==1
```

- App id 30 (navigation): 0x180bb calls **0x13f40** (builds `<path>.sign`), 0x180e1 sets the key
  to `/tmp/navi_public.key`, 0x1812f calls `CheckSign` (0x12100), and:

```asm
18134: test al, al
18136: je  0x18088        ; failed -> NO launch
18169: call 0xa740        ; QProcess::start(...)
```

- The failure branch sets `[rbx+0x24] = 0xa` (error code 10) and diverts (0x18088–0x18099).
  **Only the value 1 is tolerated**; 0 never launches.

[E] The signature check is reachable only from this launch handler: `readSection` (0x15b50) is
called only at 0x17e78, `CheckSign` (0x12100) only at 0x1812f, and `signCheck` (0x127d0) only
from `readSection` at 0x162c5. The measured boot/startup launch of `AppStandbyClock` (log
`…CheckSign ret = 1` → `m_AppProcess->start(…)`) therefore went through this same enforced path.

[I] Whether *every* startup-group/preload launch is funnelled through this handler, vs. a
separate preload path, is not fully closed in this pass: `checkBin` (0x13190, the ELF-format +
`has .sign` pre-check) has no statically visible direct caller and is likely invoked via a
Qt meta-object/vtable slot. The *measured* startup launch of AppStandbyClock did enforce the
check, so the startup group is not exempt for the observed app.

## 6. Meaning of `signCheck first : [0] [0] [69] [325]`

[E] Emitted inside the `signCheck` hashing loop at 0x1292f. Decoding the chained `QString::arg`
calls (0x1295e/0x1297c/0x1299c/0x129ba, all with return-slot-in-`rdi` convention):

- `%1` and `%2` are **hard-coded 0** (`xor edx,edx` before each of the first two `.arg` calls).
- `%3` = `rbx` = `[ctx+0x230]` = the `.sign` **`sh_offset` reduced by 0x200 per hash chunk**,
  i.e. the byte offset of `.sign` **within the current 0x200-byte buffer** = 69.
- `%4` = `r13` = `rbx + 0x100` = 69 + 256 = **325** (the end of the 256-byte signature region
  within that buffer).

[E] Cross-check: `AppStandbyClock` has `.sign` at file offset `0x1cb045` = 1 880 133;
`1 880 133 mod 512 = 69`, and `69 + 256 = 325`. So the tuple is
**(0, 0, sh_offset mod 512, sh_offset mod 512 + 256)**, and it marks the in-buffer window that is
zeroed out before `SHA256_Update`. `signCheck second` (0x12ac4) is the analogous log for the
case where the signature region straddles a chunk boundary; with a 256-byte signature at
offset 69 it fits in one chunk, so only `first` was logged.

---

## Reproducibility

Scratch under `work/signcheck/`: capstone/pyelftools/pycryptodome live in `venv/`. The disassembly
and xref approach: parse ELF with pyelftools, map `.rela.plt/.rela.dyn` → GOT symbol names and
`RIP-relative` string targets, then disassemble `.text` with capstone 5.0.7 (`X86_REG_RIP = 41`;
note this Qt build returns `QString` from `QString::arg` via a **return slot in `rdi`**, so arg
chains must be read as `rdi=ret-slot, rsi=this, rdx=value/&arg`).

## Open questions

1. Precise static call graph of `checkBin` (0x13190) and whether a separate preload/startup-group
   path can launch an app *without* the `readSection`→`signCheck` gate. Best resolved by
   reconstructing the Qt meta-object (vtable) entries for the launcher class.
2. Whether the `/tmp` key copy in the 0x20ac0 singleton can be re-triggered (it cannot by normal
   flow — the global guard caches it), and what exactly can write to `/tmp/app_normal.key` at
   runtime (the missing precondition that turns V-048 from "key-location trust" into a usable
   first-entry primitive).

## Single most decisive next experiment

Stand up the recovered rootfs (read-only) or the QEMU VM and, with the launcher running,
**overwrite `/tmp/app_normal.key` with a freshly generated 2048-bit RSA public key, sign a copy of
a benign app binary (with its `.sign` section zeroed, SHA-256, PKCS#1 v1.5, using the matching
private key), replace the app's `.sign` section / `/tmp/<app>.sign`, and request a launch.**
If the launcher logs `CheckSign … ret = 1` and starts the process against the attacker key, V-048
is confirmed end-to-end; if it fails, the remaining gate is elsewhere (e.g. a pinned-key recheck
not yet found, or a non-`/tmp` key read under some runtime state).
