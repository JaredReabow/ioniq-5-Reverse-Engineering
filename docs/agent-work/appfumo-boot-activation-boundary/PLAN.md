# AppFUMO boot-activation boundary plan

Date: 2026-11-01

## Objective

Build a deterministic, fail-closed, execution-free exact-static package that
binds the completion-QML-to-controller-reset chain, keeps reboot-system and
recovery paths separate, normalizes D-Bus argument/status observations, audits
selected canonical rootfs members by streaming the archive, and stops at the
external MICOM/ABL/bootloader boundary.

## Safety and repository boundaries

- Work only in this repository and do not delegate.
- Do not execute recovered target code, rootfs executables, services, or
  helpers.
- Do not create update inputs, packages, images, mounts, writes, reset/recovery
  requests, slot operations, boot actions, or persistence.
- Use only host-side parsing, hashing, exact LLVM disassembly/unwind inspection,
  tar streaming, and Python tests.
- Preserve concurrent work; do not stage, reset, stash, commit, or push.
- Retained evidence must omit target instructions and bytes, callable D-Bus
  coordinates, serial bytes, operational fallback text, operator paths, and
  vulnerability identifiers.

## Exact inputs

- embedded ELF SHA-256:
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
- ELF Build ID: `863a8730e66a1c5245a1bf458fe2554adee0351a`;
- canonical rootfs SHA-256:
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
- instruction authority: exact Homebrew LLVM `llvm-objdump` with raw bytes
  suppressed;
- unwind authority: exact Homebrew LLVM `llvm-readelf --unwind`.

## Phases

1. Revalidate exact ELF, Build ID, rootfs, and LLVM executable identities without
   changing concurrent work.
2. Recover and bind the completion QML resource, old-style Qt connections,
   signal index/dispatch, controller slot dispatch, reset wrapper, and reset
   core.
3. Independently bind reboot-system wrapper/core, recovery notification setup,
   recovery slot/request, boot-information request, and booting-type shared-
   memory reader.
4. Normalize D-Bus endpoint roles, argument types/counts, asynchronous versus
   blocking behavior, local status use, and unknown remote effects. Retain only
   hashes for fixed endpoint/method literals and fallback text.
5. Stream the complete canonical rootfs archive. Bind full inventory count/hash;
   exact selected names, types, modes, sizes, and content hashes; reject aliases,
   duplicates, links, and special selected members.
6. Classify selected update scripts as label management, fsck as current-root
   observation, and generic systemd/boot-control/flashing components as installed
   but unbound. Limit negative claims to the six requested exact basenames.
7. Add strict manifest, deterministic normalized report, byte-free selected
   evidence, focused tests, public evidence, plan/checkpoint, and narrow umbrella
   index updates.
8. Run focused and full tests, deterministic generation/diff check, integrated
   harness, `git diff --check`, and privacy scans. Do not stage, commit, or push.

## Acceptance boundaries

The final model must preserve all of these distinctions:

- Qt delivery and local request construction versus request execution;
- asynchronous send acceptance versus external hardware action;
- reset/recovery request bytes versus a slot identifier;
- installed generic tools versus binding to the reviewed AppFUMO flow;
- shared-memory consumption versus producer provenance and enum meaning;
- exact-basename absence versus semantic behavior absence; and
- the reviewed ELF/rootfs evidence versus external MICOM, ABL, and bootloader
  activation, acceptance, counter, and rollback behavior.
