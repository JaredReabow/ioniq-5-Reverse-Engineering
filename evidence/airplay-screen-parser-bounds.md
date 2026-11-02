# AirPlay screen parser output-capacity audit

## Scope and classification

This note binds an **exact-static heap out-of-bounds read/write candidate** in
the recovered EU `260128` projection stack. It does not report a live crash,
phone-to-handler delivery, code execution, root access, persistence, or CVE
identity.

The reviewed path spans three exact recovered ELF files:

| File | Size | SHA-256 |
|---|---:|---|
| `libAirPlay.so` | 215,896 | `ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0` |
| `libCarPlayMediaFramework.so` | 162,392 | `69690210d1aa4dec33c77b0e80f1d3368f8a70bcb507c1b158b6245dc29eb2f3` |
| `libCoreUtils.so` | 1,200,368 | `9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae` |

All addresses below are ELF virtual addresses. The associated REA dossiers use
a Ghidra image base of `0x100000`, so their displayed addresses are exactly
`0x100000` higher.

## Socket-to-parser route

`AirPlayReceiverSessionScreen_ProcessFrames` is exact range
`0x1f250..0x1fa93`, size 2,115, SHA-256
`51016b6ba869ea0cda6a2940196ced53b1b9957735f3a114935d06d976d1c0b1`.
The exact body shows:

1. `0x1f4b9` requests exactly `0x80` bytes from the already-established screen
   `NetSocket` into the retained screen header.
2. `0x1f4f6` loads the header's 32-bit body-size field; `0x1f502` allocates that
   many bytes, and a second socket read fills the body.
3. Opcode `0` reaches `ScreenStreamProcessData@plt` at `0x1f747` with the body
   pointer and 32-bit body size.
4. Opcode `1` reaches `ScreenStreamSetAVCC@plt` at `0x1f7ca` when the body is
   non-empty.

The recovered code therefore binds a socket-read body to the reviewed media
callbacks. It does **not** identify how a peer obtains the screen socket or
prove listener exposure, pairing, authorization, authenticated-encryption
state, or live peer control.

The public `45clouds/WirelessCarPlay` source at commit
`51145ef55f8dd9f1cbadd58353cacb5e0ca215e9` provides comparative protocol names
and the 128-byte `AirPlayScreenHeader` geometry. Its
`AirPlayReceiverSessionScreen.c` SHA-256 is
`c5fc6bca8a6758caaea59394859d5d857e6f9683d079ae3741a35da6f8999bc7`.
Recovered bytes, not that source, are authoritative here.

## Retained parser state

The media implementation has the following byte-bound state transitions:

- `ScreenStreamInitialize`, `0x11d34..0x11fdd`, size 681, SHA-256
  `f922e85799a0795d2fd9df80a595d98fe79923023f798853b2ae08bd4e257a3b`,
  calls `calloc(1, 0xc8)`. The output pointer, output capacity, AVCC fields, and
  first-frame flag therefore begin zeroed.
- `ScreenStreamSetAVCC`, `0x1227b..0x124c1`, size 582, SHA-256
  `60c4af44c4c3634702ba8b20ad1297e2e50d26302ccb4a352149adece798d439`,
  invokes the bounded AVCC-header converter and retains:
  - converted header pointer at context `+0x80`;
  - converted header length `H` at `+0x88`;
  - length-prefix width `p` at `+0x90`.
- `ScreenStreamStart`, `0x124c1..0x126fc`, size 571, SHA-256
  `a05f3a63efd7c708ed916d871d098acf69a42bc916b5ce95bc5b729bf2902516`,
  stores `1` at context `+0x98`. That selects a one-time retained-header copy
  on the next processed frame.

`H264ConvertAVCCtoAnnexBHeader`, exact range `0x81f2e..0x821f4`, validates the
source lengths it consumes and derives `p` in the range `1..4`. The downstream
NAL helper accepts `1`, `2`, or `4` and rejects `3`. This review does not claim
an out-of-bounds write inside the converter.

## Exact true-input and output-capacity mismatches

`ScreenStreamProcessData` is exact range `0x133f2..0x13f06`, size 2,836,
SHA-256
`f80e0c035321845e4c5e8e0c7d50e8d973e1059725887e509429262cec63af47`.
It rejects a null body and a zero body size. Its output-buffer growth path then:

- computes `2*S` at `0x1361f`, where `S` is the frame body size;
- compares that value with retained capacity at context `+0xa8`;
- when growth is needed, allocates exactly `2*S` bytes at `0x136a3`;
- records exactly `2*S` as capacity at `0x1372b`.

The NAL caller also loses the true socket-body bound before those writes:

- `0x13849..0x13911` reads the next `p`-byte declared NAL length without first
  checking that `p` bytes remain in the body.
- `0x139c2` computes `p + declared_length`.
- `0x139eb` adds that unchecked extent to the current input pointer and treats
  the result as the NAL helper's end pointer.
- `0x13a2c` calls `H264GetNextNALUnit` with this **synthetic end**, not the true
  `body_start + S` end.

For the first NAL inside that declared extent, the helper's body check is
against an end manufactured from the same declared length. A declared extent
past the socket body can therefore be accepted, after which `memcpy` reads the
accepted declared length from beyond the body allocation. The cumulative
`consumed < S` comparison occurs only later at `0x13a9d..0x13ac6`, after the
copy. If an outer iteration begins with fewer than `p` bytes remaining, the
initial prefix read itself is already beyond the true body for `p=2` or `p=4`.

Two output writes do not consult the recorded capacity:

1. If context `+0x98` is `1`, `0x13776..0x1379f` copies all `H` retained
   configuration-header bytes to the output, then advances output-used by `H`.
   There is no `H <= capacity` check around this copy.
2. The NAL loop calls `H264GetNextNALUnit`, writes a four-byte Annex-B start
   code at `0x13a44`, copies the returned NAL length at `0x13a65`, and advances
   output-used by `4 + length`. `0x13a9d..0x13ac6` repeats according to consumed
   **input** bytes. It never compares output-used with context `+0xa8`.

`H264GetNextNALUnit`, exact range `0x821f4..0x82295`, size 161, SHA-256
`4f93ad628a9cfbaf35c18a3e6cc5eca8c3ac67d82c93e56a1bf85607bac93c82`,
checks that the selected prefix and NAL body lie inside the start/end range it
is given. It also accepts a zero NAL length and advances the input pointer by
the selected prefix width. The helper itself is bounded, but this caller gives
it an end derived from the unchecked declared length rather than the true
socket-body end. Its checks therefore do not close the caller's true-input or
output-capacity failures.

## Length proof

Let:

- `S` be frame-body bytes;
- `p` be the retained AVCC length-prefix width (`1`, `2`, or `4`);
- `N` be the number of NAL units accepted by the bounded helper;
- `L` be the sum of their payload lengths;
- `H` be the retained header bytes copied on the first-frame branch.

Complete input consumption gives:

```text
S = p*N + L
```

The reviewed caller produces:

```text
O = H + 4*N + L
  = H + S + (4-p)*N
```

The exact growth branch records:

```text
C = 2*S
```

The output crosses the allocation when:

```text
H + (4-p)*N > S
```

This condition is satisfiable by input geometry that the exact helper accepts.
In particular, because a one-byte prefix and zero NAL length are both accepted,
the per-NAL four-byte expansion can make output approach four times input while
the fresh-context growth branch allocates twice input. Separately, the
first-frame header copy crosses capacity whenever retained `H` alone is larger
than the current allocation.

An independent true-input condition is missing: before forming the synthetic
helper end, the caller never requires
`p + declared_length <= true_remaining`. When this condition is false, the
helper can accept and copy a declared extent outside the socket body because it
was given the synthetic end. This establishes an exact-static out-of-bounds
read/copy candidate even without relying on the four-byte expansion proof.

No concrete frame, AVCC body, packet, or malformed input was created for this
analysis.

## Important integer-overflow correction

The `2*S` instruction is unchecked, but the exact socket route supplies a
32-bit body size zero-extended into an x86-64 `size_t`. Therefore:

```text
S <= 0xffffffff
2*S <= 0x1fffffffe
```

The doubling does **not** wrap in 64-bit arithmetic on this route. The exact
findings are a missing true-remaining check plus insufficient output-capacity
accounting for retained-header and per-NAL expansion, not a demonstrated `2*S`
integer wrap.

## CVE-2025-30422 boundary

Apple describes CVE-2025-30422 as a buffer overflow fixed in AirPlay audio SDK
2.7.1 and AirPlay video SDK 3.6.0.126, with unexpected application termination
possible for a local-network attacker. Oligo classifies it more strongly as a
potential integer-overflow RCE and states that detailed routes are withheld.

Neither reviewed publication names `ScreenStreamProcessData`, identifies these
bytes, or provides a lawful affected-versus-fixed binary comparator. Moreover,
the exact socket route above rules out a 64-bit `2*S` wrap. The recovered
finding therefore remains **unattributed**. Broad buffer-overflow or parser
class overlap is not CVE identity.

## Security and runtime boundaries

Established statically:

- exact socket-body dispatch into the reviewed config and frame callbacks;
- exact zeroed context, retained AVCC state, and first-frame flag;
- exact `2*S` output allocation on the growth path;
- exact declared-prefix/body handling that substitutes a synthetic helper end
  for the true socket-body end;
- exact unchecked header prepend and unchecked NAL output writes;
- accepted parser geometry for which input reads exceed the body or calculated
  output exceeds capacity.

Not established:

- physical-phone, USB/NCM, or network delivery to the exact installed unit;
- screen listener/interface exposure or successful session setup;
- pairing, authorization, authentication, encryption, and stream-state
  prerequisites;
- an observed allocator overwrite, crash, process exit, restart, or user-visible
  denial of service;
- reliable control-flow influence, code execution, root, SMACK escape,
  persistence, or firmware modification;
- CVE identity, fixed-version lineage, or owner-unit applicability.

The recovered projection stack is separately documented as privileged and
high-priority, but that configuration does not turn this static mechanism into
a demonstrated root path.

## Reproduction

The deterministic verifier performs no target execution and creates no media
input:

```sh
<platformio-env>/bin/python3 \
  tools/uk_fw/airplay_screen_parser_bounds_audit.py \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libAirPlay.so \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libCarPlayMediaFramework.so \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libCoreUtils.so \
  --output /tmp/airplay-screen-parser-bounds.json
```

Tracked report:

- `evidence/artifacts/projection-candidates/airplay-screen-parser-bounds.json`

Public references:

- `https://support.apple.com/en-us/122403`
- `https://www.oligo.security/blog/airborne`
