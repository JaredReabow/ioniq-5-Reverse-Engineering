# TOCTOU on the update source: verifier-to-installer object continuity

Status: **structural candidate, confirmed architecture, window unmeasured.**

## Why this file exists

An external report (relayed 2026-11-05) describes a published technique against this
platform: a Raspberry Pi Zero-class board acts as a **USB mass-storage gadget**, presents a
genuine update package so the unit passes its cryptographic checks, then **swaps the backing
file for a modified one** before the installer reads it. The unit then installs the modified
image without ever failing a check.

This is the classic check-then-use split. The claim is unverified for our build; this note
records what our own artefacts show about whether such a split exists.

It maps exactly onto two questions our own evidence already listed as open, in
`evidence/decrypttopipe-output-integrity.md` §"Remaining trust boundary":

- verifier-to-staged-source **same-object continuity**;
- source and destination **inode stability** during the pipeline.

## What is already established (prior work, not re-derived)

From `evidence/decrypttopipe-output-integrity.md`, all measured against the canonical EU
rootfs archive (sha256 `423491fd…`):

- Stock helper `/app/share/AppUpgrade/DecryptToPIPE`, size 559,192, mode 0755,
  sha256 `e3110811e83701368e638947e6d8887f59321707e70f6288adf0790090d929c0`,
  Build ID `4303e27a93f0acfb308146a5d034dafbffa064d0`.
- AppFUMO invokes it as a **shell pipeline**: `%1 -d %2 %3 0 |` with a downstream `dd` sink.
- The parent calls `pclose()` and **discards the status**.
- `DecryptToPIPE` opens the source **by path**, measures its size, seeks to
  `file_size - 0x4024`, reads a 0x4024 trailer, and recognises only `TER`/`TE2`.
- Its own exit status is unconditionally zero: no parser, decrypt, read, fallback or
  write result reaches it.

So the install-side consumer is a **separate process that re-opens the source by path**. It
does not inherit a file descriptor from a verifier. That is the precondition for a swap to
matter.

## What this pass adds

Analysed binary: the `0x7c64` embedded updater stage of `AppUpgrade`
(sha256 `dc11f293e4e8465fe3c23a55c6c6878925104576a719f9bba44cabd24e0d9d39`).

### 1. The USB image collection and verification entry points

| string | stage offset |
|---|---|
| `collectUSBImages` | `0x285430` (xref `0x92670`) |
| `getXMLChecksum` | `0x2853d8` (xrefs `0xa8db3`, `0xa8e30`) |
| `checkHash` | `0x28a158` (xrefs `0xe931c`, `0xe94ca`, `0xe9578`, `0xe963d`, `0xe9730`) |
| `CheckHashOnceAppEvent` | `0x278b80` (xrefs `0x46a4c`, `0x46bfb`) |
| `extract_prepareFiles` | `0x284f40`, `0x284f60` |

Also present: `teruten5_pub.key`, `Checksum.txt`, `[%s] Check Signature for %s ...`,
`[%s:%d] Check Signature Result is OK - %s ...`, `[%s] Check Signature Error (%d) : %s`.

### 2. `checkHash` is a path-based verifier that persists the verified path

The function containing the `checkHash` references begins at `0xe9288`. Its own rodata
references, in address order, tell the whole story:

```
0xe931c -> 0x28a158 : "checkHash"
0xe9328 -> 0x283e16 : "[%s] %s"
0xe94d7 -> 0x288b00 : "[%s] %s file non-exist error !!"
0xe957f -> 0x28e67c : "[%s] %s (%d)"
0xe9644 -> 0x289938 : "[%s] Stop hash check."
0xe973d -> 0x28994e : "[%s] %s file open error !!"
0xe9882 -> 0x288b20 : "/update/activeResourcePath_new"
0xe98ad -> 0x289969 : "/update/activeResourcePath"
0xe99e2 -> 0x28a0c0 : "updateResourcePathFile"
0xe99ee -> 0x289984 : "[%s] path : %s "
0xe9ab5 -> 0x288b40 : "\n\n write m_resourceFullPath : %s \n\n "
0xe9bf9 -> 0x288b68 : "\n\n Error !! : write fail m_resourceFullPath : %s \n\n "
```

Reading the sequence: stat the path (`file non-exist error`), **open it by path**
(`file open error`), hash it, and on success **write the verified path** to
`/update/activeResourcePath_new`, then rename it to `/update/activeResourcePath`
(`updateResourcePathFile`, `m_resourceFullPath`).

The verifier therefore does not hand a descriptor to the installer. It hands over a
**path name in a file on the unit**.

### 3. Verify and install are separated by Qt event dispatch, not by shared state

`checkHash`'s enclosing function at `0xe9288` has **zero direct `call rel32` callers**
anywhere in the embedded stage's 2.4 MB of `.text`. The only reachable entry is
`CheckHashOnceAppEvent` — i.e. the check is dispatched as a **Qt signal/event**, exactly as
its name says.

Consequence: the verification completes, returns through the event loop, and the
extraction is a later, separate invocation. There is no single scope in which a verified
handle stays open across the install.

### 4. Combined architecture

```
collectUSBImages()        enumerate images on /update/usb        (path list)
getXMLChecksum()          read expected checksums                (Checksum.txt / XML)
checkHash(path)           open-by-path, hash, compare            [verify]
    -> write /update/activeResourcePath(_new)                    [persist PATH]
    ... event loop returns ...
extract_prepareFiles()    consumer re-opens by path              [use]
DecryptToPIPE (separate process)  open source by path, decrypt   [use, status discarded]
                                              -> pipe -> dd      [write]
```

Every arrow that crosses from verify to use carries a **path**, never an inode or a
descriptor. The two use-side consumers (`extract_prepareFiles`, `DecryptToPIPE`) both
re-open by name.

## 5. Assessment

**Confirmed from our own bytes:** the update pipeline is path-based end to end. Verification
produces a recorded pathname; installation re-opens that pathname in a different process
(`DecryptToPIPE`) whose exit status the parent discards. No verified descriptor is carried
across the boundary.

**Therefore:** the reported class of attack — pass the check, then change the bytes behind
the path — is **architecturally permitted** by this design. Nothing found so far prevents
it.

**Not proven, and must not be claimed:**

- that the *rootfs image specifically* travels this exact path (the `activeResourcePath`
  machinery is named for a *resource*, and may be the navi-map path rather than the boot
  image); the boot image may instead be handled by AppFUMO's separate pipeline;
- the size of the window between verify and use (the external report suggests ~15 s;
  our build has not been measured);
- that the unit re-reads from the same medium rather than from an on-unit staging copy —
  **if** the verified bytes are copied to internal storage first, the swap is ineffective
  and the whole technique fails;
- mass-storage gadget enumeration acceptance, which is a bench fact;
- any signature-bypass, modified image, or successful install.

## 6. Falsification sequence, cheapest first

1. **Static, decisive:** determine whether `extract_prepareFiles` / the boot-image consumer
   reads the **USB medium** or an **on-unit copy**. If it copies-then-verifies-then-uses the
   copy, the technique is refuted for this build. This is the question that decides
   everything and it is answerable from the binary we already have.
2. **Static:** resolve whether `activeResourcePath` is the navi resource or the boot image.
3. **VM:** run the decrypted `AppUpgrade` in QEMU against a staged `/update` tree, with a
   second process rewriting the staged file at a controlled delay, and observe whether the
   consumer's read differs from the bytes that were hashed. This is our own binary in our
   own VM and needs no unit. The delay sweep also **measures the window**.
4. **Bench, last:** mass-storage gadget identity acceptance.

Step 3 gives a measured window without any hardware. It is the highest-value next
experiment in this thread.

## 7. Bounds

- Static analysis only. No gadget was built, no image modified, no check bypassed, no
  partition written, no unit touched.
- The external technique is recorded as a **claim**; only the architectural facts in §2–§4
  are ours.
- Nothing here is a root vector yet. Whether the swap is effective depends entirely on
  whether §6.1 shows the consumer reads the medium or a copy.

---

## 8. Update (still static): a staging tree exists, which leans toward REFUTED

A follow-up pass enumerated the shell templates in the `0x7c64` stage. The decisive new finding is
that the unit **creates its own staging tree and populates it before installing**:

```
0x282ee0  rm -rf /update/HU /update/HU.tar* /update/micom /update/gps /update/S5W_*.tar;
0x282f30  mkdir -p /update/HU/firmware /update/HU/images;
0x283dcd  du --max-depth=0 /update/HU
```

with the copy/extract primitives alongside them:

```
0x27dc83  cp -r %1 %2
0x2839d6  cp -ar %1 %2
0x283d99  cp -vf %1 %2
0x27e9e2  cp -a %1 /app/bin/
0x27dba4   | tar -xzvm -C %1
0x27dc20  pv -q %1 | tar -xzvm -C %2
0x283e76  unzip -o %1 -d %2
0x27c500  %1 -d %2 %3 0
0x27c50e   | dd of=%1 bs=512
```

`/update/HU` is wiped and recreated on every update and is where the HU payload is assembled, so the
install almost certainly consumes `/update/HU/...` rather than the removable medium. That is the
`REFUTED-COPY-THEN-VERIFY` shape.

**But it is not yet proof**, and the distinction matters:

- we have not shown *which* path the `[%s] Check Signature for %s ...` log is called with, i.e.
  whether verification runs on the `/update/HU` copy or on the `/update/usb/...` original;
- if verification ran on the **USB original** and installation on the `/update/HU` copy, the swap
  would still work — the swap would only have to happen before the copy, not before the install;
- so the remaining question is narrower and different from §6.1: **is the copy made before or after
  verification?** Copy-then-verify refutes the technique; verify-then-copy does not.

Honest verdict therefore stays **AMBIGUOUS**, but it now leans hard toward refuted, and the remaining
work is one ordering question rather than an open-ended hunt.

### Note on a worker answer

A delegated static-analysis run returned `REFUTED-COPY-THEN-VERIFY` confidently, but cited
`0x2b520` as `extract_prepareFiles` — that address is simply the start of `.text` — and gave no
reproducible commands. It was not adopted. The conclusion above rests on the quoted rodata strings,
which are checkable: `strings -a -t x <stage> | grep -E 'cp |mkdir|rm -rf /update/HU'`.
