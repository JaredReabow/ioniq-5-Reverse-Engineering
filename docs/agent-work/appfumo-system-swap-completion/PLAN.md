# AppFUMO system-swap completion plan

## Objective

Freeze how the weak `swapSystem` Boolean and object latch `+0x240` feed the
production update-info handler, and determine whether system-swap success is a
mandatory gate for downstream completion-marker handling.

## Safety

Static analysis only. Do not run AppFUMO, updater helpers, mount/copy/pipeline
commands, reset handlers, or recovered binaries. Do not create update media,
modify an image, flash, select a boot target, or claim boot acceptance.

## Questions

1. Which controller field requests the system swap?
2. What happens when `swapSystem` returns true or false?
3. Which downstream action actually requires `+0x240`?
4. Does the handler abort completion processing when `+0x240` remains zero?
5. What completion files and log commands are reached after the swap block?
6. Which additional predicates remain before final update completion/reset?

## Exact-static implementation

Bind the exact AppFUMO identity; the complete progress-handler FDE; the four
update-state getter FDEs; marker helper; literals; call targets; branch and
latch anchors; and bounded result-use semantics. Reuse only the previously
published stable ELF helper after verifying its exact tool hash.

## Boundary

A downstream path or log marker does not prove runtime invocation, successful
writes, durable storage, boot-target selection, ABL/MICOM acceptance,
mark-good, rollback, root or persistence.
