# AirPlay session-setup divisor audit plan

## Objective

Determine whether the exact recovered `libAirPlay.so` contains a request-derived zero-divisor path in `AirPlayReceiverSessionSetup`, bind it to the existing `SETUP` callback analysis, and preserve strict runtime and CVE-attribution boundaries.

## Safety boundary

- Offline static analysis only.
- Do not execute recovered binaries, parsers, services, or helpers.
- Do not create or transmit protocol input.
- Do not access network, radio, projection, I2C, USB, or target device endpoints.
- Do not infer installed-unit impact from the recovered package.

## Work phases

1. Resolve the apparent `0x1998a` versus `0x11998a` address discrepancy.
2. Bind the callback call site and encryption-bypass branches to session setup.
3. Recover MainHighAudio dispatch, exact dictionary keys, retained fields, and arithmetic.
4. Verify the redundant-audio branch, divisor load, and `DIV` instruction against exact bytes.
5. Compare semantic names with public source without treating it as exact provenance.
6. Build a deterministic identity/range/anchor audit and tests.
7. Document demonstrated facts, prerequisites, and non-demonstrated impact.
8. Run focused and canonical validation; commit only attributable paths.

## Acceptance criteria

- Exact library identity and function/range hashes are reproducible.
- ELF/Ghidra address normalization is explicit.
- Every control-flow claim is tied to exact addresses and bytes.
- The report does not contain a malformed request or operational delivery procedure.
- Classification remains an exact-static denial-of-service candidate unless runtime evidence exists.
- No CVE, authentication bypass, code execution, root, or persistence claim is made without evidence.
