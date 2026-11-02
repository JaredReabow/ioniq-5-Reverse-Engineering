# Intel TXE affected-to-first-fixed signed-module inventory

## Scope

This report expands the exact Intel TXE `3.1.50.2222` to official first-fixed
`3.1.55.2269` comparison from selected modules to every paired NFTP
`module/module.met` member. It is a passive static inventory, not a vulnerability
or exploitation demonstration.

Canonical inputs:

- affected EU ABL SHA-256
  `f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac`;
- first-fixed ASUS X541NA IFWI SHA-256
  `db9325168976e1e68cba25924e82c2aeb2db85fb7a678de5fd66e200ab7643b9`;
- affected signed NFTP version `3.1.50.2222`;
- first-fixed signed NFTP version `3.1.55.2269`.

`tools/uk_fw/txe_first_fixed_module_inventory.py` verifies both embedded NFTP
signatures, requires exact input identities and module sets, validates each
manifest-to-metadata binding, validates metadata-to-module binding where the
reviewed strict extractor supports it, and strictly decompresses supported CSE
LZMA members. It also binds affected and first-fixed FTPR syslib identities.

## Classification contract

`syslib_relocation_only` is intentionally narrow. It requires:

1. equal module sizes;
2. every raw difference to fall inside a same-offset `E8`/`E9` relative-branch
   operand;
3. the first-fixed relative target to equal the affected target plus five;
4. both targets to decode as bounded `jmp rel32` export stubs in the exact,
   hash-bound affected and first-fixed syslib modules; and
5. complete module equality after only those reviewed four-byte operands are
   zeroed.

This proves local entry-body byte identity under the reviewed address
normalization. It does **not** prove transitive behavioral identity: the export
stub may reach a changed syslib body, deeper service, kernel handler, indirect
dispatch target, or another module.

`changed_with_unexplained_bytes` means only that at least one byte remains after
that generic normalization. Such a module is a static-review priority, not a
vulnerability or CVE attribution.

## Result

The signed NFTP contains 34 paired module members:

- one is exactly byte-identical: `ish_bup`;
- nine are completely syslib-relocation-only: `adspa`, `busdrv`, `evtdisp`,
  `hci`, `heci`, `pmdrv`, `tcb`, `tls_iso`, and `vdm`;
- 23 retain unexplained bytes; and
- `pavp` remains explicit and opaque because module-extension byte `+9` is
  nonzero in both versions and its stored-member digest is not the digest used
  by the ordinary strict extractor. No transform is guessed.

| module | affected size | fixed size | classification | raw differences | unexplained |
|---|---:|---:|---|---:|---:|
| `adspa` | `0x4000` | `0x4000` | `syslib_relocation_only` | 89 | 0 |
| `busdrv` | `0x6000` | `0x6000` | `syslib_relocation_only` | 97 | 0 |
| `cls` | `0x8000` | `0x8000` | `changed_with_unexplained_bytes` | 5,512 | 5,176 |
| `crypto` | `0x27000` | `0x27000` | `changed_with_unexplained_bytes` | 116,685 | 116,482 |
| `dal_ivm` | `0x64000` | `0x65000` | `changed_with_unexplained_bytes` | 359,257 | 359,257 |
| `dal_lnch` | `0x5000` | `0x6000` | `changed_with_unexplained_bytes` | 23,774 | 23,774 |
| `dal_sdm` | `0xe000` | `0xf000` | `changed_with_unexplained_bytes` | 59,614 | 59,614 |
| `evtdisp` | `0x4000` | `0x4000` | `syslib_relocation_only` | 126 | 0 |
| `fpf` | `0x6000` | `0x6000` | `changed_with_unexplained_bytes` | 16,464 | 16,463 |
| `gpio` | `0x4000` | `0x4000` | `changed_with_unexplained_bytes` | 179 | 2 |
| `hci` | `0x2000` | `0x2000` | `syslib_relocation_only` | 58 | 0 |
| `heci` | `0x9000` | `0x9000` | `syslib_relocation_only` | 377 | 0 |
| `hotham` | `0x7000` | `0x7000` | `changed_with_unexplained_bytes` | 20,845 | 20,838 |
| `ipc_drv` | `0x4000` | `0x4000` | `changed_with_unexplained_bytes` | 6,888 | 6,824 |
| `ish_bup` | `0x3af8` | `0x3af8` | `byte_identical` | 0 | 0 |
| `ish_srv` | `0x6000` | `0x6000` | `changed_with_unexplained_bytes` | 259 | 1 |
| `iunitcse` | `0x5000` | `0x5000` | `changed_with_unexplained_bytes` | 10,914 | 10,849 |
| `loadmgr` | `0x7000` | `0x7000` | `changed_with_unexplained_bytes` | 253 | 1 |
| `maestro` | `0x5000` | `0x5000` | `changed_with_unexplained_bytes` | 8,505 | 8,416 |
| `mca_boot` | `0x5000` | `0x5000` | `changed_with_unexplained_bytes` | 14,338 | 14,336 |
| `mca_srv` | `0x6000` | `0x6000` | `changed_with_unexplained_bytes` | 16,139 | 16,103 |
| `mctp` | `0x8000` | `0x8000` | `changed_with_unexplained_bytes` | 11,103 | 11,035 |
| `pavp` | `0x51000` | `0x51000` | `opaque_changed` | 155,484 | opaque |
| `pm` | `0x6000` | `0x6000` | `changed_with_unexplained_bytes` | 179 | 7 |
| `pmdrv` | `0x3000` | `0x3000` | `syslib_relocation_only` | 75 | 0 |
| `policy` | `0xc000` | `0xc000` | `changed_with_unexplained_bytes` | 13,407 | 13,067 |
| `prtc` | `0x3000` | `0x3000` | `changed_with_unexplained_bytes` | 5,231 | 5,228 |
| `ptt` | `0x2f000` | `0x2f000` | `changed_with_unexplained_bytes` | 175,637 | 175,620 |
| `sigma` | `0x1c000` | `0x1d000` | `changed_with_unexplained_bytes` | 114,701 | 114,701 |
| `storage` | `0x11000` | `0x11000` | `changed_with_unexplained_bytes` | 62,023 | 62,020 |
| `tcb` | `0x4000` | `0x4000` | `syslib_relocation_only` | 129 | 0 |
| `tls_iso` | `0x24000` | `0x24000` | `syslib_relocation_only` | 332 | 0 |
| `vdm` | `0x3000` | `0x3000` | `syslib_relocation_only` | 38 | 0 |
| `vfs` | `0x1d000` | `0x1f000` | `changed_with_unexplained_bytes` | 80,167 | 80,167 |

## Security interpretation

The result materially narrows CVE-2018-12147 without locating it. Complete
local-byte exclusions now cover HECI, busdrv, and HCI, plus six other signed
NFTP modules, at the exact first-fixed boundary. The advisory fix may still be
implemented by a transitive service reached through their unchanged imports.

The eleven smallest residual bytes are now individually bound rather than left
as generic differences:

- `ish_srv`: one serialized length changes `0x13 → 0x14`;
- `loadmgr`: one changes `0x15 → 0x16`;
- `gpio`: two change `0x16 → 0x17` and `0x0e → 0x0f`; and
- `pm`: seven change `0x0b → 0x0c`, `0x0d → 0x0e`, `0x10 → 0x11`,
  `0x18 → 0x19`, `0x0e → 0x0f`, `0x13 → 0x14`, and `0x15 → 0x16`.

All eleven are one-byte increases in messages whose dword at offset zero is
`0x02000200`. Nine are `push imm8` arguments to syslib stub `0x60b4`; exact
constructor `0x8e8a..0x8ed3` / `0x8e8f..0x8ed8`, SHA-256
`1a9f71789daff697fe6ac80b110101ecc63d84bbc3759c6a869bfc648a6d8c28`,
stores that argument's low byte at message offset `+4`. The two remaining PM
sites write the byte at local message offset `+4` directly and preserve their
submit API through syslib-stub translation `0x6609 → 0x660e`. Exact submit
wrappers store first-argument dword `0x02000200` at message offset zero.

This is a coordinated serialized-interface change, not a generic address
relocation. The meaning of dword zero, recipient, added-byte semantics,
attacker control, HECI reachability, and advisory identity remain unresolved;
it must not yet be called the CVE-2018-12147 fix.

The exact submit wrapper gives this cluster a concrete FTPR kernel path. It
stores the message pointer in a `0x40`-byte syscall argument block, passes
selector `0x10`, and calls syslib wrapper `0x16f8f` / `0x16fb1`. That wrapper
constructs syscall value `0x10010040` as
`(selector << 24) | 0x00010000 | argument_size` and tail-jumps to the exact
kernel gate.

The affected and first-fixed syscall tables preserve flags `1` and argument
size `0x40`, but bind selector `0x10` to shifted handlers
`0x8c6b8..0x8c946` and `0x8c65a..0x8c8e8`. Both bodies are `0x28e` bytes.
Across the complete handlers there are only seven raw differing bytes: three
are inside two reviewed `call rel32` operands, while the remaining four encode
two uses of one semantic immediate change:

- `mov eax, 0x000000ff` becomes `mov eax, 0x00000102`; and
- `cmp eax, 0x000000ff` becomes `cmp eax, 0x00000102`.

After normalizing those two call operands and two immediate fields, the handler
bodies are byte-identical. The handler tail reaches a shared return epilogue at
`0x8bdb0..0x8bdcf` / `0x8bd52..0x8bd71`; its only byte change is another
`cmp eax, 0xff → 0x102`.

A complete-kernel instruction census finds the same numeric transition in 15
sites in each build: two `mov eax, immediate`, one `mov edx, immediate`, and
twelve `cmp eax, immediate` sites. The `mov edx` site is in the helper directly
called by selector `0x10`.

That entire helper, `0x8bfe7..0x8c099` / `0x8bf89..0x8c03b`, is `0xb2` bytes.
Its only two raw differing bytes encode `mov edx, 0xff → 0x102`. Immediately
beforeward, exact instructions walk `+0x50`/`+0x28` links until a null tail,
store the source pointer at that tail, and then return the reviewed value through
`eax`. The shared epilogue stores that result at `0x98384`; zero and the reviewed
value both take the path that clears `eax` and returns, while other nonzero
values call a separate handler.

Sixteen context-bound sites now locate the ordinal insertions. Affected values
`0xc4..0xc6` move by two (`0xc4 → 0xc6`, `0xc5 → 0xc7`, and `0xc6 → 0xc8`),
while affected `0xc7` and `0xc8` move by three (`0xca` and `0xcb`). The seven
previously reviewed higher sites likewise translate `0x100 → 0x103`,
`0x101 → 0x104`, and `0x102 → 0x105`. Exact first-fixed status-return
instructions occupy the three inserted numeric ordinals:

- `0xc4` at runtime `0x876a6`;
- `0xc5` at runtime `0x87687`; and
- `0xc9` at runtime `0x8765c`.

This proves two insertions before the affected `0xc4` semantic position and one
between the shifted affected `0xc6` and `0xc7` positions. It does not recover
the vendor names or full semantics of those statuses.

The two previously identified high-value producers are not inserted statuses;
they are translated affected/first-fixed counterparts:

- affected `0x85a04..0x85a90`, SHA-256
  `6a5da5501dac433546a2c08220ddff17b80ef4160549b9c6cde38da2a9f8df19`,
  returns `0xfd`; first-fixed `0x824cb..0x82557`, SHA-256
  `b12ad8b0c4e784655e76de10ba1977c906bb55c14d0b7eccfd2c62479b96d930`,
  returns its translated value `0x100`. Both examine page-table state, validate
  bounds, and can clear/invalidate a page. Their direct caller counts and
  corresponding call roles are preserved across builds.
- affected `0x8539f..0x853fd`, SHA-256
  `1e17058b43cdf950a3abdcb1c729565d66171a19d319c431fc8843c7903a2063`,
  returns `0xfe`; first-fixed `0x8580b..0x85869`, SHA-256
  `004b911c32d58e78d2ffb3aab766308fb6b9168b35781208021eeabeb2f0f10e`,
  returns `0x101`. Both scan 128 entries, append selected indexes, and return
  that status when output count exceeds 62.

All fifteen kernel sites now have bounded roles. Three produce the sentinel:
one returns it after registering an object in a list and invoking a follow-up,
one is an immediate selector-`0x10` handler return, and the already bounded
helper returns it after linking at a null tail. Ten consumers are a repeated
completion filter that stores `eax` at global `0x98384`, treats zero and the
sentinel alike, and forwards other nonzero values to the same error handler.
Selector `0x10` separately accepts the linked-tail helper's sentinel result, and
the central pending-work dispatcher returns to its dequeue path when global
`0x98384` contains the sentinel. These roles cover all two `mov eax`, one
`mov edx`, and twelve `cmp eax` census sites in both builds.

Together, the queue-like helper and epilogue behavior support a deferred or
nonordinary-completion sentinel interpretation. It still does **not** establish
the vendor status names or full semantics, identify the message recipient or
appended byte, establish HECI reachability, or attribute the change to
CVE-2018-12147.

Larger changed modules include plausible service and downstream-parser surfaces
such as `ipc_drv`, but a module name or diff size is not reachability or advisory
proof. The already bound first-fixed VFS/NDL integration remains the strongest
exact CVE-2018-3655 candidate.

## Artifact

- `evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json`
- schema `ioniq-txe-first-fixed-module-inventory/v1`
- size `124,860` bytes
- SHA-256 `0de578c50a7126f1941537b5a90ae5add59cf65bd02513e096f140503055bf3d`

Embedded `$MN2` signatures establish self-consistency and byte binding only.
They do not establish platform ROM/fuse/OEM acceptance or installed-unit
identity. No CSE module, updater, target executable, or HECI/MEI endpoint was
executed or opened.
