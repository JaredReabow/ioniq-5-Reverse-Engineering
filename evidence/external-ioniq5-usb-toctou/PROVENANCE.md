# Provenance — `CloudPapi/ioniq5-usb-toctou`

Imported 2026-11-05 from <https://github.com/CloudPapi/ioniq5-usb-toctou> (shallow clone at the time of import). **Documentation only.** The upstream `poc/` (USB
emulator), `pizero/` (gadget deployment, TE2 tooling) and any key material were **not** vendored — they are reproducible from upstream and there is no research value in
duplicating attacker tooling into this repository.

Their claims are tagged in their own docs with `[LOG]` (car logs), `[RE]` (decompiled/strings) and `[INFER]`. This repository's corroboration is separate and is recorded in
`Ioniq5-VULNERABILITIES.md` **V-059**: the four strings their mechanism depends on are present in *our* copy of the same build, which makes the structural claim independently
checkable rather than resting on their report.

What we did **not** do: reproduce the dynamic-media demonstration. That needs programmable USB hardware, and the TOCTOU window itself is a property of the shipped code rather than
of our image.

Their documents keep their **original internal cross-references** (`01-vulnerability.md` and friends, under their own `docs/` directory), which are relative to the upstream layout. Those paths are
allowlisted as `EXTERNAL` in `tools/doc_link_allowlist.txt` rather than edited, so the imported text stays verbatim.
