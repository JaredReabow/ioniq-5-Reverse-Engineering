# AppFUMO boot-partition write plan

## Objective

Freeze the exact-static `swapSystem` path from staged `iasImage*` files to boot
partitions p1/p2, including mount completion versus mount success, direct-copy
and encrypted-pipeline branches, return-value semantics, and caller latching.

## Safety and non-goals

- Do not execute AppFUMO, mount helpers, `DecryptToPIPE`, `dd`, boot images, or
  any recovered target executable.
- Do not mount, unmount, copy, flash, reset, select a slot, construct an update,
  bypass a signature, or write a target partition.
- Do not publish an operational flashing procedure.
- Do not equate a true function return, process completion, progress, `sync()`
  call, or unmount attempt with durable boot-partition bytes or boot acceptance.

## Exact input

Embedded AppFUMO ELF, size `5,066,264`, SHA-256
`464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`,
Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`.

## Questions

1. Which staged normal/sub files are directed to p1 and p2?
2. How does mode byte `0x6d20b4` select direct copy versus
   decrypt-to-pipe/`dd`?
3. Does mount dispatch inspect child exit status or only wait completion?
4. Does the pipeline helper drain and `pclose()` its child, and is the returned
   status used?
5. Which failures affect the common Boolean return?
6. Can a true result be latched at caller object offset `+0x240` without proved
   boot-partition writes?
7. Does this routine persistently select a boot target or only update files on
   both boot partitions?

## Implementation

Create a deterministic analyzer binding:

- exact ELF identity and Build ID;
- FDE ranges and hashes for `swapSystem`, mount-dispatch helpers, pipeline
  helper, and three direct callers;
- exact literals, direct calls, branch/immediate anchors, and bounded call
  absence;
- the p1/p2 normal/sub destination matrix;
- the common return formula and caller latch stores;
- deterministic UTF-8/LF JSON with exclusive output creation.

Add focused tests for exact reproduction, malformed/mutated ELF rejection,
call and anchor drift, deterministic output, path privacy, and exclusive output.

## Acceptance boundary

The package may prove construction, call ordering, branch predicates and return
semantics. It must retain successful mount, copied/decrypted bytes, pipeline
exit success, durable storage, persistent selector changes, ABL/MICOM
acceptance, health, mark-good, rollback, root and persistence as unknown.

## Routing

The requested Fable route remains blocked because
`openrouter/claude-fable-5.1` is not advertised for native subagents with
`multi_agent_version=v2`. No paid probe or alternate provider is authorized.
