# AppFUMO wildcard D-Bus recovery-signal boundary plan

Date: 2026-11-01

## Objective

Build a deterministic, fail-closed, execution-free package for the exact
AppFUMO recovery-signal subscription, its guarded local consumer and separate
asynchronous request tail, the canonical system-bus policy, configured launcher
identity, label assignments, kernel MAC selection, and bounded daemon-integration
evidence.

## Safety and repository boundaries

- Work only in this repository and do not delegate.
- Do not edit the unrelated MICOM service source with concurrent modifications.
- Do not stage, commit, push, reset, or stash.
- Do not execute recovered target code or rootfs executables.
- Do not connect to a bus or create/send signals, methods, requests, payloads,
  packets, flash/update actions, or persistence.
- Use only host-side hashing, exact LLVM static decoding, ELF parsing, tar
  streaming, strict XML/config parsing, and tests.
- Public artifacts must redact callable D-Bus coordinates, event/argument
  values, target instructions and bytes, supplied paths, commands, and exploit
  steps.

## Exact inputs

- embedded FUMO ELF SHA-256:
  `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
- ELF Build ID: `863a8730e66a1c5245a1bf458fe2554adee0351a`;
- canonical rootfs SHA-256:
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
- exact kernel-config SHA-256:
  `987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`;
- exact Homebrew LLVM object-decoder and unwind-reader file identities are bound
  in the strict manifest.

## Phases

1. Bind exact artifact, Build ID, LLVM, complete instruction, and complete FDE
   identities.
2. Bind SysV connection arguments at `0xe29df`: independent empty service/path
   QStrings, hash-bound fixed interface/member, receiver, and slot.
3. Bind generated dispatch, local input/state guards, tail transfer, separate
   request construction, and asynchronous submission without retaining callable
   request coordinates or values.
4. Stream the complete canonical rootfs. Reject policy aliases, duplicates,
   links, special/nested members, malformed XML/DOCTYPEs, unexpected includes,
   unsupported scope values/rule forms, and mixed ownership attributes.
5. Parse the main system policy and every regular system policy member. Apply
   conjunctive attributes, wildcard peer semantics, last-match rule ordering,
   scope precedence, and undefined `includedir` cross-file order. Audit exact,
   general, and named-sender rules while keeping runtime include replacement
   unknown.
6. Bind launcher unit/script/binaries, configured systemd default identity,
   dynamic updater process construction, and both canonical executable-label
   assignments while keeping runtime path/uid/label conditional.
7. Bind kernel SMACK/SELinux/AppArmor selections and the complete canonical bus
   daemon string inventory; limit the negative to named Smack integration.
8. Add manifest, report, byte-free evidence, focused tests, assessment,
   plan/checkpoint, and narrow umbrella/index links.
9. Run focused and full test suites with `<platformio-env>/bin/python3`, plus
   deterministic regeneration/diff checks, integrated public harness/privacy
   checks, and whitespace validation.

## Acceptance boundaries

- Bus policy permission is not same-bus socket reachability.
- A wildcard subscription is not message forgery.
- Interface/member filtering is not sender authentication.
- Local slot invocation is not external controller action.
- Configured uid root is not a SMACK escape.
- Recovery control is not code execution, root, or persistence.
- No operational signal or request is generated.
- No new vulnerability number is assigned; the conclusion is a conditional
  trust-boundary finding.
