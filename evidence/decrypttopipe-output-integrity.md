# Stock `DecryptToPIPE` output-integrity boundary

## Scope and canonical identity

This execution-free package binds AppFUMO's boot-image pipeline to the stock
helper as installed in the canonical EU rootfs archive.

Canonical archive:

- size `879,109,759`;
- SHA-256
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`.

Selected unique archive member:

- `./app/share/AppUpgrade/DecryptToPIPE`;
- regular file, UID/GID `0/0`, mode `0755`;
- size `559,192`;
- SHA-256
  `e3110811e83701368e638947e6d8887f59321707e70f6288adf0790090d929c0`;
- Build ID `4303e27a93f0acfb308146a5d034dafbffa064d0`.

No recovered helper was executed.

## AppFUMO invocation

The exact AppFUMO pipeline template is:

```text
%1 -d %2 %3 0 |
```

The final argument is parsed by `DecryptToPIPE` raw FDE `[0x8470,0x84ef)` as a
decimal numeric offset. For this exact invocation it is zero.

The shell appends a downstream `dd` sink. The parent helper drains output and
calls `pclose()`, but the previously published package established that it
discards the status.

## Exact parser classification

The stream routine `[0x82d0,0x8461)` calls envelope parser
`[0x9080,0x954e)`. The parser:

1. opens the source and measures its size;
2. treats a source no larger than `0x4024` as non-envelope;
3. seeks to `file_size - 0x4024`;
4. reads exactly `0x4024` bytes;
5. recognizes only trailer prefixes beginning `TER` or `TE2`;
6. stores error `-404` (`0xfffffe6c`) for an unrecognized trailer.

The stream routine classifies that result exactly:

- result zero: encrypted/decryption reader path;
- result `-404`: plaintext fallback;
- any other nonzero result: return without producing the normal output loop.

### Exact EU package applicability

All six normal `iasImage*` inputs have validated TE2 trailers and select the
decryption branch.

All six `_sub` files are plaintext `ipk.` containers. At offset
`file_size - 0x4024`, their trailer prefix is not `TER` or `TE2`; each therefore
selects the exact `-404` fallback. The fallback performs `fseek(input, 0, ...)`
for the AppFUMO argument and copies from the beginning of the plaintext
container to stdout.

This closes the previously advisory `_sub` pass-through question for the exact
EU package.

## Process exit semantics

Raw main FDE `[0x8110,0x8197)` calls:

- key loader `[0x9e50,0x9ef4)`;
- numeric offset parser `[0x8470,0x84ef)`;
- stream routine `[0x82d0,0x8461)`.

After the stream call, control jumps to the common return path, which clears
`eax` and returns zero. No parser, decrypt, read, fallback, or stdout-write
result reaches the process exit status.

Consequently:

- invalid or failed streaming can still produce process exit status zero;
- zero exit does not prove any output was emitted;
- zero exit does not prove all expected bytes were emitted.

## Output-write semantics

Both output loops use 512-byte buffers:

- decrypted output calls `write(1, buffer, n)` at `0x837b`;
- plaintext fallback calls it at `0x842b`.

Each tests only whether the result is negative. A shorter nonnegative result is
not retried or compared with `n`; source/decrypt state advances by the full
input count.

For the ordinary blocking pipe and 512-byte writes, Linux pipe semantics make a
short write less likely than this generic code-level contract suggests. The
static finding is nevertheless exact: the implementation contains no complete
write loop and no final emitted-size check.

The more general failure boundary is stronger: parser/decrypt/read failures can
emit zero or truncated output while `DecryptToPIPE` itself returns zero.
AppFUMO also discards the surrounding shell status and does not perform a final
boot-destination size or byte comparison.

## End-to-end consequence

The now-closed static chain is:

```text
normal package image -> TE2 decrypt path -> stdout
_sub package image   -> -404 fallback at offset zero -> stdout
stdout -> shell pipe -> dd boot-partition destination
```

The chain proves intended byte routing and branch applicability. It does not
prove complete emitted bytes or final partition integrity.

A true AppFUMO result can therefore coexist, statically, with any of these
unobserved states:

- failed mount command;
- parser/decrypt failure with little or no producer output;
- incomplete stdout delivery;
- downstream `dd` failure;
- failed sync/unmount;
- wrong or non-durable final bytes.

This does not demonstrate that any such failure occurred on a unit, nor does it
create an unprivileged route to influence the source images.

## Remaining trust boundary

All exact stock containers carry valid embedded signatures and the recovered
kernel. Remaining questions include:

- verifier-to-staged-source same-object continuity;
- source and destination inode stability during the pipeline;
- final destination size/readback/digest;
- whether ABL/MICOM pins the embedded modulus;
- selection between `iasImage` and `iasImage_sub`;
- persistent activation, health, mark-good, attempts, rollback, root, and
  persistence.

## Reproduction

```sh
PY="<platformio-env>/bin/python3"
"$PY" tools/uk_fw/decrypttopipe_output_integrity.py \
  --rootfs work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz \
  --appfumo work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf \
  --boot-dir work/appfumo-iasimage-eu260128/encrypted \
  -o work/decrypttopipe-output-integrity.json
"$PY" -m pytest -q tests/test_decrypttopipe_output_integrity.py
```

Tracked evidence:

- `evidence/artifacts/update-candidates/decrypttopipe-output-integrity.json`;
- `evidence/artifacts/update-candidates/decrypttopipe-output-integrity-exact-static.asm`.

No update, modified image, shell pipeline, mount, `dd`, partition write, reset,
boot attempt, root action, or persistence mechanism was created or executed.
