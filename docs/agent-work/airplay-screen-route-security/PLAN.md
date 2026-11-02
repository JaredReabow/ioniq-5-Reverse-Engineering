# AirPlay screen route security plan

## Contract

Recover and byte-bind the passive/static route from accepted AirPlay setup
state to the secondary screen socket and the existing screen parser. Determine
which cryptographic state is selected, whether MFi-SAP is mandatory on every
exact branch, how the listener is bound, and whether the accepted peer is
compared by the reviewed caller.

## Safety boundary

- Do not run recovered target code or shipped helpers.
- Do not create or transmit HTTP, plist, screen, AVCC, media, network, USB/NCM,
  pairing, authentication, or cryptographic protocol input.
- Do not create keys, payloads, exploit material, signature bypasses, modified
  firmware, flash operations, root transitions, or persistence mechanisms.
- Use only host-side ELF parsing, hashing, disassembly, decompilation, and public
  comparative source.
- Keep runtime reachability, authentication, process impact, root, persistence,
  CVE identity, and installed-unit applicability explicitly unproved.

## Steps

1. Bind the screen stream-type dispatch and nonzero connection-ID requirement.
2. Bind pair-verify and null-pair-verify key selection.
3. Trace fresh session initialization and setup encryption None/error branches.
4. Bind the exact SHA-512 screen derivation inputs and screen crypto flags.
5. Bind secondary listener creation, wildcard bind, dynamic fallback, response
   port, thread start, accept arguments, and parser call.
6. Implement a deterministic no-follow verifier with exact hashes and anchors.
7. Add focused tests, a canonical artifact, evidence prose, and validation.
