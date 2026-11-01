# Checkpoint — exact CVE-2016-9793 socket-buffer signedness audit

## Result

CVE-2016-9793 is rejected for the exact recovered kernel by machine-code
effects matching upstream fix `b98b0bc8c431e3ceb4b26b0dfc8db509518fb290`.
Both forced send/receive buffer routes require `CAP_NET_ADMIN`; success joins a
32-bit doubling followed by signed `cmovle` positive-minimum selection, and the
store occurs only afterward. The named negative socket-buffer premise is absent.
Commit provenance is not inferable from the stripped binary.

## Evidence

- `vmlinux` SHA-256:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`
- Build ID: `273378887b4cf563c10862fdf18b2292765df781`
- configuration SHA-256:
  `987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`
- authoritative map SHA-256:
  `2cfba917c1c8e7444e393e8d94ebfe367e2ba348be4f35ce10fbb331822e3c1f`
- exact range:
  `sock_setsockopt [0xffffffff814790bd,0xffffffff814797e9)`
- exact capability helper:
  `capable = 0xffffffff81062186`
- assembly SHA-256:
  `3911ee771afb2f215013d3bdef4ef93ed2e7fd4b08b96a08d8cb1ebb7433c5df`
- upstream patch SHA-256:
  `620453e77616829f5c311793f02ae9f519dcedcbcda757c4878727e47fe42876`
- deterministic model-report SHA-256:
  `f870c510768654e861a027b42d85cdc83933fdfc9f4c3008e7cae5a556c75417`

## Public-source refresh

Authoritative public records were fetched into ignored `work/`:

- NVD CVE record SHA-256:
  `f77b404dad6adb68c7e545421ec59771c6deaa80fe78405e19576d590324f14f`;
- CVE List v5 record SHA-256:
  `4de4bb3ed4f2e81684b622356a9c9aeaee254b13d3c205a9fd087f5b073b54bf`;
- pristine Linux v4.1 `net/core/sock.c` SHA-256:
  `1561b5e4d3acd9bbff9b87bb704727daf11f253ebe970e7fdf6c7368eb7ffc88`;
- upstream fixed-source snapshot SHA-256:
  `1776f71d09f426568e26e65c87659bf488bf87e78c56323f002d5e278f638a61`.

The public records identify a published exploit repository, but no exploit code
was imported or executed because the exact shipped instructions reject its
necessary socket-buffer signedness premise.

## Boundary and safety

Installed identity, runtime socket policy, live capabilities, invocation,
negative socket state, corruption, crash, code execution, credential/SMACK
transition, root, and persistence remain unobserved. No socket, socket option,
namespace, capability action, packet, malformed input, memory pressure, target
execution, crash attempt, firmware write, flash action, or persistence action
occurred.

## Validation and review

- Focused model validation: `9 passed, 522 subtests passed`.
- Full-suite validation: `915 passed, 352185 subtests passed in 133.05s`.
- Full-suite log:
  `work/local-validation/pytest-full-sock-buffer-force-final.log`, size `1075`,
  SHA-256
  `dfd90c84cdbce234ec0060fdddc3272b19799655a7ef1cb35cb1a65b7ccd9162`.
- Python compilation, focused `git diff --check`, strict UTF-8, LF-only,
  final-newline, NUL, and trailing-whitespace checks passed. The retained
  upstream patch preserves ordinary patch context whitespace and was separately
  checked for UTF-8, LF-only, final newline, CR absence, and NUL absence.
- Normal and `PYTHONIOENCODING=utf-16` model output were byte-identical and
  retained report hash remained
  `f870c510768654e861a027b42d85cdc83933fdfc9f4c3008e7cae5a556c75417`.
- Exact requested Fable route remains unavailable because
  `openrouter/claude-fable-5.1` is not advertised for native v2 subagents. No
  paid probe, alternate model, or private-target disclosure was used.
- Independent review: pending exact-route availability; this package does not
  claim independent acceptance.
