# Intel MEI historical memory-safety backport audit

## Scope and claim boundary

This note compares four public post-v4.1 Intel MEI fixes with the exact
unexecuted `mei.ko` recovered from the canonical EU `260128` mango rootfs.  It
is an exact-static triage exercise, not a version-banner inference.  No module
was loaded, no MEI device was opened, and no message was sent to CSE firmware.

A matching fix effect rejects only the corresponding historical premise.  It
does not prove the installed module is byte-identical, that the device node is
reachable by an unprivileged process, or that no unrelated MEI issue exists.
Conversely, a firmware-controlled path is not automatically host-controlled.

## Exact artifact

Canonical member:

`/lib/modules/4.1.27-abl/kernel/drivers/misc/mei/mei.ko`

- Size: 125,000 bytes
- SHA-256: `8518715e6e1910aacddf9da116aa97b98e7fca8f14c64da83959c60204d83609`
- ELF Build ID: `ca127bac6266f1afd1ff48cdd0c0bdcb4a67d643`
- Vermagic: `4.1.27-abl SMP mod_unload`
- Not stripped; exact symbols include `mei_cl_irq_read_msg` at `0x228c`,
  `mei_cl_write` at `0x4c4c`, `mei_cl_complete` at `0x50d8`, and file operation
  `mei_write` at `0x566f`.

The tracked read-only excerpt is
`evidence/artifacts/kernel-candidates/intel-mei-backport-exact-static.asm`:

- Size: 30,430 bytes
- SHA-256: `f52f4723550174e90eadae6faa87eb8e991c4eda44dbc2c2e460a34753f1f8a8`

## Public fixes reviewed

The following upstream Linux commits were downloaded from the Torvalds Linux
repository and retained only under ignored `work/`:

| Commit | Public subject | Downloaded patch SHA-256 |
|---|---|---|
| `23253c31c6a7a3c5a437ec31830e2100484c0748` | `mei: do not access freed cb in blocking write` | `1ecde4c9b01b5023722805822e7bdb44a03099deb35976c24f01803356164f7e` |
| `f862b6b24f0ffd954633a55f39251a6873b664ca` | `mei: fix possible integer overflow issue` | `b02cd5d71e87a1d0d613a4aebede669456869f84e6d34f1a629b07b937aaf1bd` |
| `6cbb097fd3903fd6b419303ee8dc7f72b47d06f0` | `mei: fix double freeing of a cb during link reset` | `62883048392de04f7442bb971a5372c13a5d53debd3f8cce4c5a63bc99518341` |
| `6a8d648c8d1824117a9e9edb948ed1611fb013c0` | `mei: fix NULL dereferencing during FW initiated disconnection` | `1d4e7f561689370b9ee64c0f2d636b378c2073bbddaf0cb67a68bc860fb9f340` |

The public commit descriptions identify use-after-free, integer-overflow followed
by buffer-overflow, double-free, and list invalidation/null-dereference
conditions respectively.  These are useful leads despite the target's old
`4.1.27-abl` banner, but the exact module contains later fix effects.

## Exact-static comparison

### Blocking-write callback lifetime (`23253c31`)

At `mei_cl_write+0x89`, the exact module loads the callback buffer size before
ownership can be transferred and stores it in a stack local.  Queue insertion
ends at `0x4f60`; `xor %r13d,%r13d` at `0x4f63` clears the live callback pointer.
After the optional blocking wait, the return value is taken from the cached
size/status path.  The common cleanup calls `mei_io_cb_free` with the remaining
pointer, which is null after successful queue transfer rather than a completed
and freed callback.

This is the material effect of the public fix.  The exact path does not
re-read the queued callback to obtain its size after completion.

### Firmware-fragment arithmetic (`f862b6b2`)

In exact `mei_cl_irq_read_msg`:

1. The fragment length is reconstructed into a 64-bit register.
2. The current callback index is loaded as 64-bit state.
3. `addq` at `0x23bf` computes the total.
4. `jae` at `0x23c2` accepts only a non-wrapping unsigned addition.
5. The overflow path moves the callback to the completion list and records
   `-EMSGSIZE` (`0xffffffa6`).
6. On the non-wrapping path, `cmpq` at `0x23ff` compares the total against the
   allocated callback-buffer size before the hardware copy call at `0x2473`.

The exact target therefore has both the carry guard and the pre-copy bounds
comparison.  The reviewed public integer-overflow premise is rejected for this
function.

### Link-reset callback ownership (`6cbb097f`)

The exact userspace file operation `mei_write` frees the callback itself only
when `copy_from_user` fails.  Its ordinary path calls `mei_cl_write` at `0x57fd`
and returns directly; it does not free the callback again on a negative return.
The callee retains cleanup ownership on pre-queue failures and nulls its pointer
on queue transfer.  This rejects the reviewed caller/callee double-free premise.

### Firmware-initiated disconnect (`6a8d648c`)

Exact `mei_cl_complete` has a disconnect-response completion arm at `0x51c8`.
It calls `mei_io_cb_free` and then calls `mei_cl_set_disconnected`.  The state
transition and list flushing therefore occur from completion handling rather
than from the control-write-list iterator described in the vulnerable public
flow.  This rejects that specific list-invalidation/null-dereference premise.

## Later superficially similar report

Upstream commit `c1a214ad82d7ac6f19fe48f90b13403b40ead9dc` fixed another
`mei_cl_write` stale-buffer read introduced by upstream commit
`98e70866aacb`'s variable-length-header change.  The exact target has the older
three-argument `mei_cl_write(..., bool blocking)` flow and already caches the
size before transfer.  Name similarity is not evidence that the later
introduced regression applies here.

## Reachability and privilege boundary

The exact rootfs ships and requests loading of:

- `mei.ko`
- `mei-me.ko`
- `mei-txe.ko`
- `/etc/modules-load.d/lge-intel-mei-mod.conf`

No recovered udev rule was found that deliberately grants broad access to a MEI
character node.  That bounded absence does not establish runtime mode, owner,
SMACK label, driver binding, or client availability.  The passive bench-state
collector now records `/dev/mei{,0,1}` metadata and `/sys/class/mei/*` identity
without opening an endpoint.

Even if a node exists, a local root path still requires all of the following to
be established separately:

1. A caller can open and use the node under DAC, capabilities, and SMACK.
2. A reachable client and message sequence reaches the exact candidate path.
3. The installed module matches the audited bytes.
4. A memory-safety premise remains after vendor backports.
5. Corruption is controllable enough to affect privilege rather than merely
   causing a reset or denial of service.

The four reviewed public fixes do not currently satisfy those requirements.
They are rejected leads, not exploit instructions.

## Reproduction

```sh
<platformio-env>/bin/python3 tools/uk_fw/intel_mei_backport_model.py
<platformio-env>/bin/python3 -m pytest -q tests/test_intel_mei_backport_model.py
```

The model is deliberately non-operational: it classifies supplied fix effects
and emits no MEI protocol, payload, ioctl, flash, or persistence material.
