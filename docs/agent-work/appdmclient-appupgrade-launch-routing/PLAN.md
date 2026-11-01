# AppDMClient AppUpgrade launch-routing plan

## Objective

Bind the exact recovered AppDMClient launch proxy and the FUMO staging branches that request app ID 300, while keeping static message construction separate from runtime D-Bus delivery, AppLauncher argument construction, process creation, execution, privilege, update acceptance, partition writes, boot acceptance, and persistence.

## Acceptance criteria

1. Bind the canonical AppDMClient identity and unwind extents used for the launch proxy and staging function.
2. Decode helper `[0x8c0c0,0x8c2ab)` under the x86-64 SysV ABI, including the hidden return object, logical argument order/types, QVariant list order, exact UTF-16 method object, and `QDBusAbstractInterface::asyncCallWithArgumentList` call.
3. Inventory every direct transfer to `0x8c0c0` and classify its app ID and two QString producers without assigning semantics from literals alone.
4. Reconstruct the complete branch predicates selecting staging calls `0x818f6` and `0x8201d`, and bind each third logical argument to either the staged destination or source-derived AppUpgrade pathname.
5. Preserve the distinction between the D-Bus launch contract and AppLauncher-created argv; do not infer owner-unit runtime vehicle/model selection from recovered fallback-table data.
6. Add a deterministic, fail-closed exact-static analyzer and tests. Reject identity, schema/type, instruction, FDE, direct-caller, literal, and causal-branch drift.
7. Retain runtime and impact facts as unknown unless independently observed. Emit no callable bus recipe, command, payload, update package, malformed input, signature-bypass patch, flash action, or persistence mechanism.
8. Run focused and tests-scoped validation, obtain independent read-only review if available, then commit and push only the reviewed package.

## Safety boundary

Host-side hashing, ELF parsing, Homebrew LLVM disassembly, deterministic reporting, and tests only. Do not execute recovered targets; contact a bus or device; create a request, media image, update package, executable payload, malformed input, or exploit; write a partition; change a slot; flash; or establish persistence.

## Orchestration note

The configured Astra DeepSeek Flash worker route was attempted first and failed before inference with `Unknown child model: deepseek/deepseek-v4.1-flash`. The coordinator therefore owns the sequential fallback while preserving the same bounded contract.
