# Plan: iAP2 local-socket framing audit

## Objective

Byte-bind the recovered `/tmp/iAp2Socket` server/client, framing length semantics,
local admission prerequisites, first-party event producers, and marshal
transaction bounds without running target code or constructing protocol input.

## Tasks

1. Verify exact framework, service, unit, relabel, and SMACK-policy identities.
2. Recover server creation, accept, header/body receive, allocation, copy,
   validation, dispatch, cleanup, and framework receiver symmetry.
3. Determine offset `0x38` semantics from every direct event producer.
4. Reconcile total-size framing with `iAp2MarshalInitFromTxn` and direct byte
   accessor behavior.
5. Inventory the intended bilateral `App::projection` SMACK label set while
   preserving runtime DAC/LSM/capability boundaries.
6. Partition fixed and dynamic-capacity event producers and retain arithmetic
   wrap as a separate unresolved question.
7. Publish a deterministic no-follow audit, exact artifact, tests, and bounded
   evidence narrative.

## Safety boundary

Offline reads, hashing, ELF parsing, disassembly, and decompilation only. Do not
run recovered executables, connect a socket, create a client command, construct
an iAP2/CarPlay message, access a device node, transmit traffic, or modify target
state.
