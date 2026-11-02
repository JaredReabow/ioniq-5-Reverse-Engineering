# BusyBox unsafe-filename fix — exact AppScomoDM applicability

## Result

Upstream BusyBox commit `8c06bc6ba14949d945eff0abcabab885f1ef7680`
(`unzip: prevent attacks via malicious filenames`) is absent from release
`1_23_2` and present beginning with release `1_24_0`. That ancestry identifies a
candidate, but it does **not** make the recovered AppScomoDM route traversable.

The exact EU `260128` AppScomoDM command supplies two literal inclusion names:

```text
unzip -o <selected archive> -d /update/usb/temp AppUpgrade .lge.upgrade.xml
```

Exact stock BusyBox instructions pass each local-header filename to the
inclusion-list matcher before directory creation, `stat`, output `open`, or
member decompression. The matcher calls `fnmatch(pattern, member, 0)`. Because
both accepted patterns are literal names without wildcard metacharacters, an
absolute name, parent-prefixed name, extra directory component, or trailing
traversal component does not match and is skipped.

Classification: **upstream unsafe-filename fix absent, but not applicable as a
path-traversal finding to this exact two-literal-member AppScomoDM command**.
This is a bounded negative result, not a statement about every stock `unzip`
caller.

Exact evidence:
`evidence/artifacts/update-candidates/busybox-unzip-unsafe-filename-exact-static.txt`.

## Provenance

Canonical rootfs:

- path: `work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz`;
- size: `879109759`;
- SHA-256: `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`.

Stock BusyBox:

- `/bin/busybox` SHA-256:
  `95bab633630fb158344497af52dc112e9e777458b810860068d4daa257bd9ebc`;
- banner: `BusyBox v1.23.2 (2026-01-28 16:00:27 KST)`;
- preserved stock analysis copy:
  `work/decrypted-eu-260128/extracted-partial-bsdtar/mango-rootfs/bin/busybox`.

AppScomoDM:

- SHA-256: `c44da21eb39987e88d71c648f625338722b8458f0ff8ecfe29e3321cf6d62046`;
- GNU Build ID: `496a47fae4cca227723b1f4037be918cae18473c`;
- `QProcess::execute(QString)` call: `0xbfaf2`.

Public-source record:

- commit: `8c06bc6ba14949d945eff0abcabab885f1ef7680`;
- preserved patch:
  `work/online-busybox-unzip-20261108/8c06bc6ba.patch`;
- patch SHA-256:
  `6110c8337bf4115c9d581a3b5af21ebc6e3aaf7193ce2b38989c7edaa878cb73`.

The commit adds `strip_unsafe_prefix(dst_fn)` before archive-member filtering.
Its absence in the target is corroboration. The route verdict below depends on
the exact target filter instructions and exact AppScomoDM operands rather than
on the version banner.

## Exact target order

The target reads the local-header filename into a zero-terminated allocation.
It then calls list matcher `0x491a0` from `0x45e25` and `0x45e52`. The second
call is the inclusion-list check; a null result branches to the entry-skip path
at `0x45e5a → 0x45e2f`.

Matcher `0x491a0` walks list nodes and calls:

```c
fnmatch(pattern, member_name, 0)
```

The register binding is exact:

- pattern: node field `+0x8` → `%rdi` at `0x491c1`;
- member name: `%rbp` → `%rsi` at `0x491c7`;
- flags: `%edx = 0` at `0x491c5`;
- `fnmatch@plt`: `0x491ca`.

Only after the filters accept an entry does control reach listing, directory,
file-open, or decompression handling. No unsafe-prefix stripping call exists in
this reviewed target region.

## Why the literal list blocks this route

The two patterns are exactly:

```text
AppUpgrade
.lge.upgrade.xml
```

Neither contains `*`, `?`, or a bracket expression. Consequently a filename
with any added path bytes is not an exact match. This rejects the relevant
unsafe-name shape classes before path use, including:

- an absolute prefix;
- one or more `../` prefixes;
- a directory before the accepted basename;
- a slash and traversal suffix after the accepted basename.

An embedded NUL does not provide a suffix escape in this implementation:
`fnmatch` and later filesystem functions consume the same C-string prefix. A
name whose visible prefix is `AppUpgrade` therefore still names the literal
`AppUpgrade` output, while a traversal prefix before the NUL does not match.
No malformed ZIP was constructed to reach this conclusion.

## Important separation from V-020

This negative result does not weaken the established CVE-2015-9261 package.
An accepted literal `AppUpgrade` or `.lge.upgrade.xml` member may still use
method 8. Its compressed bytes reach the exact pre-fix Huffman-table logic before
AppScomoDM invokes either public-key-backed member verifier.

The two issues are different:

- `8c06bc6b…`: unsafe output filename/prefix handling;
- CVE-2015-9261: dynamic-Huffman table construction and an uninitialized read.

The first is blocked in this caller by literal member selection. The second acts
inside the data stream of a member that has already matched the literal name.

## Remaining boundaries

This review does not establish:

- safety of other BusyBox `unzip` callers lacking a literal inclusion list;
- safety against a pre-existing symlink at a literal output name;
- output-directory identity or immutability at runtime;
- absence of a filesystem race between `stat` and output `open`;
- owner-unit reachability;
- code execution, SMACK escape, unrestricted root, signature bypass, update
  acceptance, partition writes, boot acceptance, or persistence.

Pre-existing output objects and races are separate filesystem-object questions;
the upstream unsafe-prefix commit neither proves nor resolves them. They require
independent ownership, label, lifecycle, and same-object analysis.

## Safety boundary

No archive, malicious filename, compressed stream, command, payload, target
execution, filesystem write, D-Bus request, update, flash operation, or
persistence mechanism was created or attempted.
