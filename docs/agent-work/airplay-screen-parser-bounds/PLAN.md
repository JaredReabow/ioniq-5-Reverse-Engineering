# AirPlay screen parser bounds audit plan

## Objective

Determine whether exact recovered screen-stream bytes contain request-derived
true-input-bound or output-capacity failures, while preserving authentication,
delivery, process impact, privilege, and CVE-attribution boundaries.

## Safety boundary

- Static, offline inspection only.
- Do not execute recovered libraries, services, parsers, or helpers.
- Do not create or transmit screen headers, AVCC bodies, video frames, packets,
  malformed media, or exploit inputs.
- Do not infer owner-unit applicability from recovered firmware alone.

## Inputs

- Exact recovered `libAirPlay.so`.
- Exact recovered `libCarPlayMediaFramework.so`.
- Exact recovered `libCoreUtils.so`.
- Existing REA/Ghidra dossiers under ignored `work/`.
- Public `45clouds/WirelessCarPlay` source for comparative names only.

## Phases

1. Bind socket header/body reads and opcode dispatch in
   `AirPlayReceiverSessionScreen_ProcessFrames`.
2. Bind screen context initialization, AVCC state retention, and first-frame
   state.
3. Audit `ScreenStreamProcessData` allocation, prepend, declared-length extent,
   true-body handling, NAL conversion, output writes, and loop bounds.
4. Audit `H264GetNextNALUnit` bounds relative to the caller-supplied end and
   zero-length behavior.
5. Derive an abstract length proof without constructing protocol input.
6. Separate the exact output-bound defect from an inapplicable 64-bit doubling
   wrap claim on the uint32 socket route.
7. Build a deterministic multi-ELF verifier and tests.
8. Record public-comparator and CVE-2025-30422 attribution boundaries.
9. Run focused and canonical tests, deterministic reproduction, encoding
   checks, JSON validation, and path-limited diff checks.

## Acceptance criteria

- All claims bind to exact file identities, ranges, anchors, and arithmetic.
- Input bounds and output bounds are distinguished.
- The report states why upstream uint32 `S` cannot wrap `2*S` on x86-64.
- No concrete malformed media or operational exploit procedure is produced.
- CVE identity, live delivery, process impact, code execution, root, and
  persistence remain explicitly unproved.
