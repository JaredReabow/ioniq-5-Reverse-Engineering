# V-059: is the mount image path filtered before it reaches a shell string?

Date: 2026-11-05. Target: the FUMO payload embedded in `AppUpgrade` at `0x5721c8` (`newota`).
Question asked: the package path is substituted into shell commands; **does any character class get
filtered between its producer and that substitution?**

## 1. The builder substitutes raw

The command is built at `0x13a510`:

```
13a511: movl  $0x27, %esi                  length 39
13a54d: leaq  0xf1f8c(%rip), %rdi          # 0x22c4e0   "ionice -c3 md5sum %1 | awk '{print $1}'"
13a554: callq QString::fromAscii_helper
13a561: movq  %r15, %rdx                   the caller's argument: THE PATH
13a56e: callq QString::arg(QString, int, QChar)
```

`0x27` is exactly 39, the length of that format string, which confirms the site. The path arrives as
the **third argument of the function** and is handed straight to `QString::arg`. Between the two
there is **no validation call of any kind** - only `QString::arg` and Qt's string/process helpers.

## 2. There is no metacharacter filter anywhere in the payload

Counted across the whole of FUMO's disassembly (472,147 lines, `.text` `0x24830`-`0x209a33`):

| comparison against | count |
|---|---|
| `0x3b` `;` | 2 |
| `0x7c` `\|` | **0** |
| `0x60` backtick | **0** |
| `0x26` `&` | 8 |
| `0x24` `$` | 2 |
| `0x22` `"` | 1 |
| `0x27` `'` | 3 |

A shell-metacharacter sanitiser would compare against most of these in one loop. **Neither the pipe
nor the backtick is compared against anywhere in the binary.**

The two `;` sites were read in context and are not character tests:

- `0xeb639`: `leal -0x8(%eax), %edx; cmpl $0x3b, %edx; jbe ...` - a **range bound** on a scalar.
- `0xf78f4`: `cmpl $0x3b, %eax; je ...` - a **dispatch on an integer code** (adjacent to `cmpl $0xf`
  and `cmpl $0xb`, clearly an enum comparison), followed by `QString::append`.

## 3. What this establishes, and what it does not

**Established:** FUMO applies no character filtering to the package path before substituting it into
`ionice -c3 md5sum %1 | awk ...` (`0x13a54d`) or the apply pipeline (`0x60f0b`,
`DecryptToPIPE -d <src> <off> 0 | pv -q -L 8m | dd of=%4`). The substitution is `QString::arg`,
which is raw. **Whatever reaches that argument reaches the shell.**

**Not established:** whether a character class can reach it. That depends entirely on the
**producer** - the copy step that puts the package into `/update/usb/bin` - and on what the
filesystem allows in a name. `;`, `$`, quotes and newline are all legal on FAT/exFAT, so the
question reduces to whether the copy preserves the name verbatim. That is the next thing to read,
and it is the same class of question as the SCSI-serial one already filed: the primitive is complete
on the consumer side and blocked on the producer.

## 4. Method notes

- `objdump` on this host is llvm-objdump, which prints `Size VMA Type` and **no file offsets**. This
  payload is a PIE whose `vma == file offset`, so string offsets double as VAs - verified by finding
  the reference `0x13a54d` to `0x22c4e0` at the expected address.
- `0x253225` as given resolves to `.rodata` (past `.text`'s end at `0x209a33`) in FUMO, and to
  `QMapNode<QString,int>::copy` in `ApplicationManager`. It is not a mount-image code path in either,
  so the trace was anchored on the string and its consumer instead of the offset.
