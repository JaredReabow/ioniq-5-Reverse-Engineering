# Persistent developer-mode initialization: VM-only experiment

## Precommitted scope

Owner requested testing persistent developer-mode menus, not disabling update verification. The authentic EU 260128 `AppEngineerMode` SHA-256 is `6ecfb7d1716d2b4f56d66477681127175c0ede9204e99f59980323d07d1adc7d`.

Reconfirmed with LLVM disassembly: at virtual address `0x737268`, bytes `c7 85 3c 01 00 00 01 00 00 00` encode `movl $1,0x13c(%rbp)`. Use ELF program headers to derive the file offset; verify expected bytes before mutation. Change only the four-byte immediate at instruction+6 from 1 to 0 in a separate copy named `/app/bin/AppEngineerMode-dev-probe`. Preserve `/app/bin/AppEngineerMode`, the source workspace and the immutable vendor base. No AppUpgrade, AppDMClient, ABL, signature-check or encryption-update-marker change.

Trade-off: this is a modified vendor application and deliberately departs from its production initialization. It may expose unsupported or hazardous diagnostic actions; do not invoke those actions. Persistence across file-backed boots is distinct from proving a runtime field value or visible menus, and official updates may replace the application.

Use a new CoW clone of `work/vm/kbuild/ws-run68` and a retained init wrapper starting `tools/uk_fw/guest/dev-mode-probe.sh` before authentic esinit. At +60 guest seconds attempt baseline, modified and modified-again launches, each observed for 20 seconds. Use the shipped Qt offscreen platform solely as an initialization diagnostic: **no visible-menu or interactivity claim is possible from offscreen execution**. Terminate only the processes launched by the probe. Host deadline 360 seconds, exact completion marker `DEV_MODE_PROBE_COMPLETE`. Retain raw serial, launch identities, source/modified hashes and byte-difference manifest.

Stop rule: if launches fail before developer-state initialization, report runtime activation unresolved and do not deploy to hardware. Do not infer a runtime state from patched bytes alone. A second boot to test initialization persistence is warranted only if the first produces useful runtime evidence. No automatic physical-device access.

## Result

**Runtime activation unresolved; do not deploy this experiment to hardware.** The earlier no_unece experiment was aborted and supplies no completed result for this question. `no_unece` and `disableEncryptionUpdate` are not substitutes for the AppEngineerMode build-state field.

The ELF program-header mapping confirmed instruction file offset `0x737268`. The separate modified copy differs in exactly one byte: file offset `0x73726e`, `01` to `00`. Modified SHA-256: `73d282a73a8de1804041ff9658c286f19d9830710ed15c6f9dcd5e42badca0e9`. This changes the instruction's immediate; it does not write to a fixed runtime flag address. `/app/bin/AppEngineerMode` remains the unmodified control.

Two runs were retained locally under `work/vm/kbuild/ws-dev-mode-probe/`:

- `runs/1794571026254438000`: interrupted host invocation. `host-run.log` (111115 bytes, SHA-256 `642b78db19d7fc1849af9babe1213e524d2a2f4c40d57f8307095bf0a83d96af`) records `DEV_PROBE_BEGIN`, the baseline hash and `DEV_PROBE_ALIVE baseline pid=1931`, but no completed baseline stop or modified launch. An initial chat statement claiming there was no probe execution record was wrong: searching the NUL-containing serial log as text reveals it. No cause of the stall is established.
- `runs/1794571645088431000`: resumed with bounded TERM/KILL handling and without procfs executable-link inspection. `host-resume.log` (138193 bytes, SHA-256 `028a704772e8274b9515c0ae935a773e1ea3fd9f2ef1cc34e2b50c498481854f`) reaches `DEV_PROBE_BEGIN` and the baseline launch announcement, but no subsequent baseline hash or modified launch. Result: `root_mounted=true`, `userspace=false`, `serial_completion_seen=false`, `timeout=true`, elapsed 360.17 host seconds. Here `userspace=false` is the harness's missing readiness marker, not proof that no userspace ran: systemd and the observer demonstrably did run.

No modified-application startup, runtime developer-state value, menu appearance, application-restart persistence or reboot persistence was measured. Logs/launch records and modified binaries remain private local artifacts; no firmware binary is committed. Stop repeated boots until the baseline observer stall is understood. Successful file patching is not successful developer-mode activation.

## Dedicated-channel follow-up and fixed longer interval

Run `1794577309908072000` moved observer output to a dedicated file-backed ttyS3 and enabled shell tracing. All three launch phases and their hash/stop/log-export records completed; the completion line was received at 147.28 host seconds, with `timeout=false`. The wrapper still returned failure because its separate userspace-ready marker was absent. This is a completed observer transaction, not full VM acceptance. Its trace establishes that the console-path ambiguity is removed, without proving the exact earlier ttyS0 blocking mechanism.

All three processes were alive at their 20-second checks; baseline and first modified launch terminated with 143 (TERM), modified restart required KILL (137). The last launch reached `initAppication` line 736 (`m_view->show() = 1`) but no `setEngType` or `Run Version` output was recorded. The 20-second interval was therefore not sufficient to establish the target initializer executed. Reconfirmed statically that the `setEngType` call is at `0x74db11`, after the late window/native-platform setup.

**One follow-up, fixed before launch:** retain dedicated ttyS3 and extend each launch observation from 20 to **60 guest seconds**, keeping the +60-second initial wait and 360-second host deadline. No additional binary patch. If developer-state initialization remains unobserved, stop and report unresolved rather than infer it from process liveness.

## Production interpretation

The object field is `this + 0x13c`; its object address is not a constant RAM address. A fixed-address boot-time write is therefore not established or recommended. The code at `0x737268` is the initializer, while the changed file byte is at `0x73726e` in this exact build. A file-backed application-specific modification could survive ordinary reboots, but update replacement, application-integrity checks, startup dependencies and actual UI behaviour still need verification. Enabling engineering UI is not a global developer mode for the entire head unit, nor does it imply update verification is disabled.
