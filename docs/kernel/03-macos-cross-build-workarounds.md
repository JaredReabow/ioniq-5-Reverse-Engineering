# Cross-building 4.1.27 on macOS arm64: the four source-level fixes

Date: 2026-11-06. The host is macOS (arm64); the target kernel is x86-64. These are the exact reasons the
first build attempts failed and the fixes that made `bzImage` build. All four are recorded verbatim in
`work/vm/kbuild/kernel.patch` (except the two header shims, which are new files in
`work/vm/kbuild/hostinclude/`).

## Toolchain

`x86_64-linux-musl-gcc` (GCC 14.2.0, Homebrew `musl-cross`) with `x86_64-linux-musl-{ld,objcopy,nm}`
(binutils 2.44). Host tools (kconfig, fixdep, modpost, relocs, …) are compiled by the **host** compiler
(Apple clang, which `/usr/bin/gcc` is a front for) and run on macOS; only kernel objects are cross-built.
This split is why the failures below are all in *host-tool* code.

## Fix 1 — the repo path has spaces, and the kernel build cannot handle that

The first `fixdep` run failed with `fixdep: error opening config file: engineering/ioniq: No such file or
directory` — the command line carrying the absolute path `…/reverse engineering/ioniq research/…` was
word-split on the spaces. The kernel build system does not support paths containing spaces.

Fix: build in a no-space copy. `cp -R work/vm/kbuild/linux-4.1.27 /tmp/kbuild/linux-4.1.27` and build
there; copy `bzImage`/`.config` back. (A symlink does not help: `make` resolves `CURDIR` with `getcwd()`.)

## Fix 2 — macOS has no `<elf.h>`

Host tools `scripts/mod/mk_elfconfig.c`, `scripts/sortextable.c`, `arch/x86/tools/relocs*.c` all include
`<elf.h>`, which is a Linux/glibc header and does not exist on macOS.

Fix: a minimal shim. `work/vm/kbuild/hostinclude/elf.h` is a copy of musl's `elf.h` (target-independent
ELF struct/constant definitions). It is added to the host include path via `CPATH`:
`CPATH=/tmp/kbuild make …`. Only `elf.h` is shimmed; everything else resolves to the macOS SDK headers.

## Fix 3 — macOS has no `<byteswap.h>` and its `<endian.h>` lacks the BSD API

`arch/x86/tools/relocs.h` includes both. macOS provides byte-order macros under
`<libkern/OSByteOrder.h>`/`<machine/endian.h>`, not under these names.

Fix: two new files, `work/vm/kbuild/hostinclude/byteswap.h` (`bswap_16/32/64` via
`__builtin_bswap*`) and `work/vm/kbuild/hostinclude/endian.h` (`BYTE_ORDER`, `LITTLE_ENDIAN`,
`BIG_ENDIAN`, `htole*`/`le*toh`). The host is little-endian, so the `le*toh` conversions are identity;
the bswap path is defined for completeness. (`bswap_*` must be defined in only one of the two files —
defining it in both gave "redefinition of 'bswap_64'".)

## Fix 4 — `scripts/mod/modpost` link fails on arm64 macOS: "Found illegal text-relocations"

`scripts/mod/file2alias.c` collects `devtable_ptr_N` pointers into a Mach-O section via
`__attribute__((section("__TEXT, __devtable")))` and reads them back with `getsectdata("__TEXT", …)`.
Pointers in `__TEXT` are text relocations, which Apple's arm64 linker rejects.

Fix (`kernel.patch`): move the section to `__DATA` — both the `SECTION(name)` attribute and the
`getsectdata("__DATA", …)` call. `__DATA` is the correct home for a table of data pointers, and data
relocations are legal there. This is a change to *host tooling only*; it does not affect the kernel.

## Fix 5 — BSD `sed` does not support GNU `\|` alternation, and BSD `stat` has no `-c`

- `arch/x86/boot/Makefile` generates `voffset.h`/`zoffset.h` with `sed -n -e 's/…\(_text\|_end\)…/'`.
  BSD sed treats `\|` as literal `|`, so the files came out **empty**, and `header.S` then failed with
  `can't resolve VO__end - VO__text`. Fix: `-E` (extended regex) with plain `(…|…)`. The `\#define`
  must stay `\#define` — the backslash escapes `#` from **make**'s comment handling, not from sed.
- `scripts/Makefile.lib`'s `size_append` uses `stat -c "%s"` (GNU); BSD stat rejects `-c`, so the LZ4
  output size was computed as empty (`expr: syntax error`) and the appended size was wrong. Fix:
  `wc -c < "$F"` (POSIX).

## Fix 6 — the LZ4 payload would not decompress ("Decoding failed")

Not a source patch; a config change. Homebrew `lz4` v1.10.0 removed the `-l` "legacy" mode that the
kernel's `cmd_lz4` invokes (`lz4c -l -c1`), so it emitted a modern LZ4 *frame*; the 4.1
`decompress_unlz4` only reads the legacy format, and the boot halted at
`Decompressing Linux... Decoding failed`. Fix: `CONFIG_KERNEL_GZIP=y` (host `gzip` emits the standard
format the kernel's gunzip reads). The compressed image is slightly larger (3,872 kB vs the LZ4
attempt's 4,486 kB system) and boots correctly.

## Net effect

All six fixes are host/build-environment corrections; none changes kernel behaviour for the guest except
`CONFIG_KERNEL_GZIP` (a compression-format choice, invisible to userspace) and the `micom` stand-in in
`04`. The resulting `bzImage` is a stock 4.1.27 kernel built with the vendor's own non-vendor config.
