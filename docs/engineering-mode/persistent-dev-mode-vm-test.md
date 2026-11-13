# Persistent developer-mode initialization: VM-only experiment

## Precommitted scope

Owner requested testing persistent developer-mode menus, not disabling update verification. The authentic EU 260128 `AppEngineerMode` SHA-256 is `6ecfb7d1716d2b4f56d66477681127175c0ede9204e99f59980323d07d1adc7d`.

Reconfirmed with LLVM disassembly: at virtual address `0x737268`, bytes `c7 85 3c 01 00 00 01 00 00 00` encode `movl $1,0x13c(%rbp)`. Use ELF program headers to derive the file offset; verify expected bytes before mutation. Change only the four-byte immediate at instruction+6 from 1 to 0 in a separate copy named `/app/bin/AppEngineerMode-dev-probe`. Preserve `/app/bin/AppEngineerMode`, the source workspace and the immutable vendor base. No AppUpgrade, AppDMClient, ABL, signature-check or encryption-update-marker change.

Trade-off: this is a modified vendor application and deliberately departs from its production initialization. It may expose unsupported or hazardous diagnostic actions; do not invoke those actions. Persistence across file-backed boots is distinct from proving a runtime field value or visible menus, and official updates may replace the application.

Use a new CoW clone of `work/vm/kbuild/ws-run68` and a retained init wrapper starting `tools/uk_fw/guest/dev-mode-probe.sh` before authentic esinit. At +60 guest seconds attempt baseline, modified and modified-again launches, each observed for 20 seconds. Use the shipped Qt offscreen platform solely as an initialization diagnostic: **no visible-menu or interactivity claim is possible from offscreen execution**. Terminate only the processes launched by the probe. Host deadline 360 seconds, exact completion marker `DEV_MODE_PROBE_COMPLETE`. Retain raw serial, launch identities, source/modified hashes and byte-difference manifest.

Stop rule: if launches fail before developer-state initialization, report runtime activation unresolved and do not deploy to hardware. Do not infer a runtime state from patched bytes alone. A second boot to test initialization persistence is warranted only if the first produces useful runtime evidence. No automatic physical-device access.

## Result

Pending execution. The earlier no_unece experiment was aborted and supplies no completed result for this question. `no_unece` and `disableEncryptionUpdate` are not substitutes for the AppEngineerMode build-state field.
