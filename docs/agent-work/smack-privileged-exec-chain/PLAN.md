# SMACK privileged-exec transition chain

## Objective

Determine, from the canonical EU 260128 rootfs and authoritative public source,
whether configured stock `App::*` tasks can execute the stock relabel anchor and
transition into the label named by `smackfs/onlycap`, without relying on the
AppLauncher D-Bus path. Produce a deterministic, read-only host analyzer and an
exact-static evidence package.

## Non-goals

- no recovered-target execution;
- no D-Bus request, shell payload, command-search substitution, malformed input,
  label change, mount, update, flash, slot change, or persistence action;
- no claim that an owner unit has the recovered build, loaded policy, configured
  xattrs, UID zero, retained capabilities, a caller-controlled `PATH`, or a
  suitable writable executable object;
- no boot-signature bypass or custom-image installation procedure.

## Design

`tools/uk_fw/smack_privileged_exec_chain.py` will:

1. open the canonical rootfs through one no-follow descriptor, stream and hash
   the full archive, revalidate descriptor/path identity, and reject member
   aliases, duplicates, links, special selected nodes, inventory drift, or input
   replacement;
2. parse all canonical `etc/smack/accesses.d/*` rules with a strict three-field
   grammar;
3. bind the delete-then-restore relabel contract, the update anchor's access and
   execute labels, `onlycap=Privileged`, the canonical `/bin/sh -> /bin/bash`
   interpreter, and exact bash identity;
4. validate hash-bound Linux v4.1 SMACK/exec/capability source, the ELF
   credential-commit path, GNU bash 3.2.57 source, and glibc 2.25 loader source;
   bind only the narrow anchors needed for access-label read/execute admission,
   script-chain credential preservation, execute-label transition, capability
   inheritance, UID/GID privileged-mode detection, environment import, and
   command lookup;
5. report the configured transition and every runtime gate without emitting a
   payload, candidate writable pathname, full policy text, or target command.

The existing passive bench probe already captures each selected process's PATH,
credentials, capabilities, task label, selected xattrs, `onlycap`, and mounts.
This phase will document the exact evidence needed from those existing records;
it will not add active behavior.

## Acceptance criteria

- canonical rootfs identity and all selected member metadata are fail-closed;
- report proves or rejects, from exact policy, read and execute permission from
  every enumerated `App::*` source domain to floor `_`;
- report distinguishes the ordinary inode access label that controls open
  admission from `SMACK64EXEC`, which selects proposed post-exec credentials;
- script interpreter recursion is bound to `cred_prepared` behavior rather than
  assumed;
- exact bash identity and public-source PATH behavior are bounded separately
  from live environment control;
- UID, capabilities, securebits, `onlycap`, loaded policy, xattrs, pathname and
  mount admission, environment influence, `AT_SECURE`, command resolution,
  successful interpreter loading, effective SMACK override, and persistence
  remain explicit runtime gates;
- deterministic tests cover policy parsing, duplicate rules, archive aliases,
  source drift, encoding-independent output, and replacement during streaming;
- the complete project test suite passes before acceptance.

## Verification

```sh
/Users/leo/.platformio/penv/bin/python3 -m pytest -q tests/test_smack_privileged_exec_chain.py
/Users/leo/.platformio/penv/bin/python3 -m pytest -q tests
```
