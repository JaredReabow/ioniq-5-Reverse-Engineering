# V-048 proof of concept — root execution through the manager's `/tmp` key

Demonstrates that the application manager launches a binary signed with a key supplied by the caller and runs it as **root**.
See `Ioniq5-VULNERABILITIES.md` V-048 and `docs/engineering-mode/app-signature-check.md` for the recovered verifier.

## Files

- `payload.c` — the test payload. It writes `/tmp/v048-proof.txt` containing its own `getuid()` and then idles.
- A throwaway public key was generated for the demonstration. It is **not committed** (the repository ignores `*.pem`), and neither is the private key: generate a fresh pair with `openssl genrsa -out my_private.pem 2048` and `openssl rsa -in my_private.pem -pubout -out my_public.pem`. The file name does not matter to the verifier; only its PEM content does.
- `repro_v048.sh` — guest script: stages the payload and key, then asks the manager for app id 301.
- `../../uk_fw/poc_sign.py` — adds the `.sign` section and signs it (this host has no `objcopy`).

## Procedure

```sh
Z=work/toolchains/zig-macos-aarch64-0.13.0/zig
$Z cc -target x86_64-linux-musl -O2 -static -o payload payload.c
/opt/homebrew/bin/python3.13 ../../uk_fw/poc_sign.py add payload payload.signed
/opt/homebrew/bin/python3.13 ../../uk_fw/poc_sign.py sign payload.signed my_private.pem
/opt/homebrew/bin/python3.13 ../../uk_fw/poc_sign.py info payload.signed
```

The linker used here discards orphan sections, so `payload.c` does **not** rely on a `.sign` attribute; the section is created by
rewriting the section header table in `poc_sign.py`. Signing hashes the file with the `.sign` bytes zeroed, so the file that is hashed
is the file that is shipped.

Then, in the projection, place `payload.signed` at `/tmp/app/bin/AppEngineerMode`, place your public key (PEM) at
`/tmp/app_normal.key`, and request app id 301 — `repro_v048.sh` does all of it. Measured result:

```
V048_PAYLOAD_RAN
uid=0 euid=0 gid=0
```

## Why the key file wins

The authentic keys are pinned inside the binary as Qt resources (`:/app_normal.key`, `:/navi_public.key`), but they are copied to
`/tmp` once on first use and the `/tmp` copy is trusted from then on **without being compared against the resource**. Replacing
`/tmp/app_normal.key` therefore replaces the trust anchor, and the manager takes the binary's path from the caller's `appLocation`
argument.
