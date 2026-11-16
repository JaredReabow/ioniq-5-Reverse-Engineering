# V-059: the producer of the substituted path, and the absence of any filter

Date: 2026-11-05. Continues `docs/v059-command-substitution-filtering.md`. Target: the SCOMO payload
embedded in `AppUpgrade` at `0x7c64`.

## 1. SCOMO builds the same kind of shell command

`strings` on SCOMO gives the command templates, with `%1`/`%2` substitutions:

```
0x27dc20  pv -q %1 | tar -xzvm -C %2
0x27dba4  | tar -xzvm -C %1
0x283e76  unzip -o %1 -d %2
0x27dc83  cp -r %1 %2          0x283d99  cp -vf %1 %2
0x28f28d  cp -rf %1 %2         0x28f3f8  cp -a %1/. %2
0x2839d6  cp -ar %1 %2         0x27e9e2  cp -a %1 /app/bin/
```

## 2. What feeds `%1` - the producer

Read at the two extraction sites:

| template | producer of `%1` |
|---|---|
| `pv -q %1 \| tar -xzvm -C %2` (`0x7aaad`-`0x7ab1b`) | **`QFileInfo::absoluteFilePath()`** then `QString::arg` |
| `unzip -o %1 -d %2` (`0xa02d0`-`0xa0309`) | **`QFileInfo::absoluteFilePath()`** then `QString::arg` |

So the substituent is **a path taken from a filesystem entry** - not a constant, not an internally
generated string. Whatever the file is called on disk is what reaches the shell.

## 3. One false lead, recorded so it is not chased again

`cp -a %1 /app/bin/` looks like an attacker-controlled copy into the executable directory. It is not:
the instruction immediately preceding it is

```
84c49: callq QCoreApplication::applicationFilePath()
```

and that value is passed as `%rdx` to `QString::arg`. `%1` is **SCOMO's own binary path** - a
self-install/copy, not an input.

## 4. No filter, in either binary

- FUMO: the whole `.text` has **zero** comparisons against `|` or backtick; the two against `;` are a
  scalar range bound and an integer enum dispatch (`docs/v059-command-substitution-filtering.md`).
- SCOMO: the templates above are all `QString::arg`; the sites read show `absoluteFilePath` feeding
  `arg` directly with no validation call between. Across SCOMO's 575,037 disassembly lines there is
  no character-class test on these arguments.

## 5. What this establishes

**There is no filtering layer anywhere in the path from a filename to a root shell command.**
The consumer substitutes raw, and the producer is the filesystem itself. What is *not* yet read is
how the package file comes to exist with a given name - the copy/staging step into `/tmp/update/usb`
(`0x27d729`) or `/update/usb/bin` (`0x27e990`) - and therefore whether an attacker-chosen name
survives to become a `QFileInfo`.

Two facts make that the whole remaining question:

- **FAT and exFAT forbid `\ / : * ? " < > |` and permit `;`, `$`, backtick, quotes and parentheses.**
  So a legitimate USB stick can carry a package named `x;id>.tar.gz`, and nothing in the filesystem
  layer stops it.
- The staging copy is the only step that could sanitise, and no sanitiser exists in either payload.

**Not established, stated plainly:** that a staged file's name reaches one of these templates on the
vehicle. That needs the copy step read, or a measurement on a unit. It is the single remaining link,
and it is now a narrowly posed question rather than an open one.

## 6. The producer normalises the name - the filename route closes

The staging copy does **not** preserve the name it finds on the stick. Read from the update logs this
project has already collected (36 distinct references to `/update/usb/bin`, 19 of them the package
itself):

```
/update/usb/temp/AppUpgrade                the staged copy
/update/usb/temp/.lge.upgrade.xml          the staged manifest
/update/usb/bin/AppUpgrade                 the installed binary
/update/usb/bin/AppScomoUpgrade            the installed SCOMO
```

Every staged and installed artefact carries a **fixed name**: `AppUpgrade`, `AppScomoUpgrade`,
`.lge.upgrade.xml`. Nothing in the log shows a USB-chosen filename crossing into `/update/usb/bin`.
So the copy **renames**, and the destination - which is what `QFileInfo::absoluteFilePath()` later
reports and what `QString::arg` substitutes - is a constant.

**Therefore the injection route through a crafted filename is closed.** A stick carrying
`x;id>.tar.gz` stages as `/update/usb/temp/AppUpgrade` and the shell sees the fixed name. This is a
correction to §5 and to the earlier note: the substitution is still unfiltered, but **there is no
attacker-controlled string in it**, so the primitive has no route.

## 7. Where V-059's severity actually stands

| element | status |
|---|---|
| unfiltered shell substitution in FUMO and SCOMO | **measured** |
| path derived from `QFileInfo::absoluteFilePath()` | **measured** |
| staging copy renames to a fixed name | **measured from collected logs** |
| attacker-controlled filename reaches the shell | **refuted** |
| downstream behaviour (the `dd of=%4` apply at `0x60f0b`) | measured, and the strongest part of the finding |

What survives as the real finding is the part that never depended on injection: **the version and
signature decisions, and the keyless downgrade** - a genuine older package is encrypted with the
unit's own key, so it passes while the version gate is satisfied against genuine current bytes.
