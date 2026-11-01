# EU 260128 boot-container matrix plan

## Objective

Close the previously conditional `iasImage*` payload-presence boundary using the
original EU package, without executing updater or target code. Verify all twelve
containers through TE2 decryption where required, exact `ipk.` parsing, embedded
RSA signature verification, command-line root target extraction, and filename
pairing.

## Safety

- Copy source files into ignored `work/`; never modify the original download.
- Host-side parsing and cryptography only.
- Do not re-sign or construct a modified container in this package.
- Do not mount, write, flash, reset, select a slot, or run recovered binaries.
- Do not infer that an embedded-key signature is accepted by MICOM/ABL.

## Questions

1. Are all twelve filenames referenced by AppFUMO present in the EU package?
2. Which six are TE2 envelopes and which six are already plaintext `ipk.`
   containers?
3. Do all twelve pass their embedded RSA-2048 PKCS#1 v1.5 SHA-256 signatures?
4. Do they share one modulus?
5. Which root partition and console settings are encoded in each command line?
6. Does payload presence close boot acceptance or persistent activation? (No.)

## Acceptance

The analyzer must fail closed on directory shape, names, file type, symlinks,
size/hash identity, TE2 metadata integrity, plaintext hash, `ipk.` fields,
command-line bounds, RSA padding/digest, modulus, root target, and unexpected
extra entries. Output must be deterministic UTF-8/LF and path-private.
