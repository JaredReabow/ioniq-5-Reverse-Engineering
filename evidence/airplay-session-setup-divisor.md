# AirPlay session-setup zero-divisor candidate

## Scope and result

Offline review of the recovered EU `260128` `libAirPlay.so` found an exact zero-divisor path in `AirPlayReceiverSessionSetup`. The finding is presently an **exact-static denial-of-service candidate** (CWE-369), not an observed crash and not a demonstrated entry, code-execution, root, or persistence path.

The reviewed library is:

- path: `work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libAirPlay.so`;
- size: `215,896` bytes;
- SHA-256: `ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0`;
- format: x86-64 little-endian ET_DYN ELF.

The deterministic report is `evidence/artifacts/projection-candidates/airplay-session-setup-divisor.json`. Its file SHA-256 is `2c9de034982def8e707689cb3be8b09342c3128a1c1fc4d831f392b84eafbc7a`; its embedded canonical SHA-256 is `e4eb3df14e54bd65c9fe3b52ea839d579eccae6989a495afab0fb2b8bbc7d527`.

No recovered executable, service, parser, or network endpoint was run. No protocol input was created or transmitted.

## Address normalization

`nm` reports `AirPlayReceiverSessionSetup` at ELF virtual address `0x1998a`. The Ghidra/REA report uses image base `0x100000`, so it reports the same entry at `0x11998a`. This is not a function mismatch:

- Ghidra range: `0x11998a..0x11c249` inclusive;
- normalized ELF range: `0x1998a..0x1c24a` exclusive;
- size: `0x28c0` (`10,432`) bytes;
- range SHA-256: `31f794fd8074bde88c42fea984664430b3c1a38b2ae43835936e2f25c6a56f41`.

The audit tool resolves ELF virtual addresses through file-backed `PT_LOAD` segments rather than assuming virtual addresses always equal file offsets.

## Exact callback route

The already-bound `SETUP` plist callback calls `AirPlayReceiverSessionSetup` directly:

- `0x10626`: loads the session, request dictionary, and response pointer;
- `0x10632`: calls `AirPlayReceiverSessionSetup@plt` at `0x85e0`;
- callback-to-call range `0x103c3..0x10637`, size `628`, SHA-256 `5cde34310a8cdf36004c110ed3f9656dbdadaacf2b808fb12dc057e1fce57a81`.

MFi-SAP decryption is not a necessary local prerequisite for this candidate:

- `0x103d7` tests the error result from the encryption-type dictionary lookup;
- `0x103df` branches to `0x10626` when that result is nonzero;
- `0x103e5` compares the encryption type with `1` (None);
- `0x103e8` branches to `0x10626` when it is None.

This establishes only callback-local control flow. It does **not** exclude a generic upstream HTTP authorization gate, establish listening-interface exposure, or prove that a phone or other peer can deliver such a request on the recovered build.

## Exact MainHighAudio and `spf` flow

`AirPlayReceiverSessionSetup` obtains the `streams` array and dispatches each typed dictionary. The reviewed MainHighAudio branch is selected as follows:

- `0x19f3f`: loads the exact recovered `type` key;
- `0x19f4b`: calls `CFDictionaryGetInt64`;
- `0x19f53`: compares the result with `0x66`;
- `0x19f56`: branches into the MainHighAudio path when equal.

Within that branch:

- the exact recovered CFString object at `0x2a33c` contains key bytes `spf`;
- public comparative source names this field `framesPerPacket`, but that source is semantic comparison only;
- `0x1a35d` loads the `spf` CFString object;
- `0x1a378` calls `CFDictionaryGetInt64`;
- `0x1a38c` stores the low 32-bit result at session offset `+0x434`;
- no positive-value check is present before the later divide.

The `spf` lookup/geometry range `0x1a35a..0x1a39b` is 65 bytes with SHA-256 `53725b779b9ee88d61bedbfce06dfb9d1039070ef2338eeb1e621c07aa595324`.

Earlier code must still accept the stream's compression and audio format, initialize control/session state, and open the required sockets. Any failure before the divide prevents this path from being reached.

## Exact divisor path

The retransmission branch uses the separately recovered `redundantAudio` state at session offset `+0x14bc`:

- `0x1a5e1`: compares `session+0x14bc` with zero;
- when nonzero, `0x1a5ea` records retransmission-disabled state and `0x1a5f1` jumps to `0x1a6d5`, bypassing the divide;
- when zero, execution falls through retransmission-list initialization;
- `0x1a647`: loads ECX from `session+0x434`, the retained `spf` value;
- `0x1a683..0x1a6b5`: calculates the numerator and initializes timing fields;
- `0x1a6c0`: executes unsigned `div ecx`;
- there is no divisor-zero rejection in the exact `0x1a647..0x1a6c2` range.

The divisor range is 123 bytes with SHA-256 `4ca9172f3de6ce259425fe3cb7611aa53f92d561730f5cf6fb21c55688899b84`. The larger redundant-audio branch range `0x1a5e1..0x1a6d5` is 244 bytes with SHA-256 `617d62b9cd30e77f9f29e7406f36631d451a6d1e5e06e28d9bb460f42214245d`.

On x86, unsigned `DIV` with a zero divisor raises the architectural divide-error exception (`#DE`) before producing a result. In a normal Unix process this commonly becomes `SIGFPE`, but this review did not run the process and does not establish final process or service behavior. An application-level signal handler or supervisor behavior outside this function remains possible.

## Comparative source

The closest public semantic comparator reviewed is `45clouds/WirelessCarPlay` commit `51145ef55f8dd9f1cbadd58353cacb5e0ca215e9`:

- `source/Sources/AirPlayReceiverSession.c` SHA-256 `5ed352778a8e786707245ef993994e6e172efd6b89f5fb71893e71e1c8ca3b61`;
- `source/Sources/AirPlayReceiverServer.c` SHA-256 `c517c24c4ae07510b7d00c5b31656e9397076c2de9058ef5ad3d41383d47a571`.

That source identifies the semantic field as `framesPerPacket` and contains the corresponding retransmission expression. It is not byte-identical provenance, a fixed-version comparator, or proof of affected runtime behavior. The recovered binary bytes and offsets above are authoritative for this finding.

## Classification and boundaries

### Demonstrated

- The exact recovered `SETUP` callback calls the exact recovered `AirPlayReceiverSessionSetup`.
- A callback-local path reaches setup without entering MFi-SAP decryption when encryption lookup reports an error or encryption type is None.
- MainHighAudio type `0x66` reads exact key `spf` and stores its 32-bit value at session offset `+0x434`.
- With `redundantAudio == 0`, the exact code loads that value into ECX and executes unguarded unsigned `div ecx`.
- A zero divisor at that instruction raises architectural `#DE`.

### Not demonstrated

- A complete phone-to-handler, USB/NCM, Wi-Fi, or other physical/network delivery path.
- Listener binding, upstream HTTP authorization, pairing state, route eligibility, or successful session/control/socket setup on a live unit.
- A crash, restart loop, persistent denial of service, or user-visible effect.
- Memory corruption, control-flow takeover, authentication bypass, root, SMACK escape, persistence, firmware modification, or custom-firmware installation.
- A CVE identity, vendor advisory mapping, affected-versus-fixed byte comparison, or impact on the owner's installed firmware.

The finding must therefore remain an exact-static mechanism candidate until an owner-controlled disconnected bench passively confirms exact identity and a separately authorized runtime plan establishes safe observability. This report provides no malformed request, payload, or transmission procedure.

## Reproduction

Offline report generation:

```sh
<platformio-env>/bin/python3 tools/uk_fw/airplay_session_setup_divisor_audit.py \
  work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libAirPlay.so \
  --output /new/path/airplay-session-setup-divisor.json
```

The output path must not already exist. The tool performs no network or device access and executes no recovered code.
