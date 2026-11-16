# Stock BusyBox unzip bounds audit

## Objective

Determine whether the exact recovered EU `260128` stock BusyBox `unzip` used by
AppScomoDM's USB-update staging path retains a public memory-safety defect before
member authentication. Keep the stock vendor binary separate from the static
BusyBox injected into the research VM.

## Safety boundaries

- use the canonical stock bytes from the original extraction, SHA-256
  `95bab633630fb158344497af52dc112e9e777458b810860068d4daa257bd9ebc`;
- do not execute recovered BusyBox, AppScomoDM, AppUpgrade, or DecryptToPIPE;
- do not create a malformed DEFLATE/ZIP stream, package, payload, shellcode,
  heap-grooming input, or flash procedure;
- model only table-bound integer states, never compressed input encoding;
- distinguish a child-process crash from AppScomoDM compromise, root, package
  acceptance, partition writes, and persistence;
- preserve the contaminated VM integration tree; do not delete or overwrite its
  injected helper or the original firmware artifacts.

## Phases

1. Prove stock artifact provenance from the original archive/extraction reports
   and identify the VM-only helper substitution.
2. Reconstruct AppScomoDM archive selection, extraction, member verification,
   decryption/copy, and app-ID-300 launch order.
3. Audit exact stock `unzip` method dispatch and reject unsupported method 12.
4. Compare method-8 `huft_build` instructions with CVE-2015-9261 initial fix
   `1de25a6e87e0e627aa34298105a3d17c60a1f44e` and corrective sentinel
   follow-up `6bd3fff51aa74e2ee2d87887b12182a3b09792ef`.
5. Add a data-free model of the recovered `v+n` bound versus the conceptual
   populated prefix and stable `UINT_MAX` sentinel correction, synthetic tests,
   reviewed evidence, and passive bench identity capture.
6. Run the complete suite and independent read-only review before commit.

## Acceptance criteria

- every address is bound to the stock SHA-256 and uses link-time VA/file offset;
- method 12 is explicitly rejected, not transferred from the VM helper;
- the exact method-8 route and pre-authentication order are established;
- CVE-2015-9261 impact is bounded to an uninitialized stack read, conditional
  invalid indexed read, and likely child crash/update denial of service unless
  stronger behavior is separately observed;
- the model emits no archive, compressed stream, packet, command, or payload;
- physical route, RCE, root, signature bypass, package acceptance, writes,
  slots, boot trust, and owner applicability remain explicit unknowns;
- all tracked changes pass focused/full tests, public harness, py_compile, and
  `git diff --check`.

## Verification

```sh
PY="${PYTHON:-python3}"
"$PY" -m pytest -q tests/test_busybox_huft_bounds_model.py
"$PY" -m pytest -q tests
"$PY" tests/run_all.py
git diff --check
```
