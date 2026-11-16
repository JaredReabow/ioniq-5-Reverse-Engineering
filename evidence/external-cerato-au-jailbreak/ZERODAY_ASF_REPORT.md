# ZERO-DAY: lms_asf.so Heap Over-Read + Integer Underflow
## LGE Gen5W IVI — 2022 Kia Cerato AU
## Firmware BD_PE.AUS.S5W_L.001.001.260319 (LATEST — March 2026)

---

## Summary

Three zero-day vulnerabilities in the ASF media parser plugin (`lms_asf.so`)
for LGE's lightmediascanner (LMS). These are custom C code bugs (source: `asf.c`),
not in any upstream library. **All are triggered by placing a crafted .wma/.wmv/.asf
file on a USB stick and inserting it into the car.**

| ID | Type | CWE | Severity | Exploitable? |
|---|---|---|---|---|
| ZD-ASF-1 | Heap Buffer Over-Read | CWE-125 | High | Yes — heap spray on glibc 2.25 |
| ZD-ASF-2 | Integer Underflow → Wrapped Size | CWE-191 | High | Yes — compound with ZD-ASF-1 |
| ZD-ASF-3 | Missing Return Value Check | CWE-252 | Medium | Possible null-deref crash |

---

## ZD-ASF-1: Heap Buffer Over-Read in WM/Picture Handler

### Root Cause

The Extended Content Description parser's `WM/Picture` attribute handler
hardcodes buffer offsets without validating the allocation size:

```
# At virtual address 0x102570 + 0xEB8 (file offset 0x3428):

mov   rax, [rsp+0x60]           # rax = malloc'd buffer (value_length bytes)
movsx r8d, word ptr [rsp+0x8e]  # r8d = value_length from file
lea   rbx, [rax + 0x37]         # rbx = buf + 55  ← HARDCODED
lea   r13, [rax + 0x5]          # r13 = buf + 5   ← HARDCODED

# Outer MIME-type scan loop:
.loop:
  mov   rax, [r13]              # READ 8 bytes (may be past allocation!)
  mov   rax, [r13+8]            # READ 8 more bytes past allocation
  mov   eax, [r13+0x10]         # READ 4 more bytes past allocation
  call  memcmp                   # compare 20 bytes against MIME patterns
  add   r13, 1
  cmp   r13, rbp                # compare against buf+55, NOT buffer end
  jne   .loop
```

When `value_length < 55`, the buffer is smaller than the hardcoded scan range.
The code reads from `buf+5` through `buf+55` unconditionally, reading up to
**50 bytes past the heap allocation** into adjacent heap memory.

### Trigger

Place a .wma file on USB with an Extended Content Description Object containing:
- Attribute name: `WM/Picture` (UTF-16LE, type 1 = byte array)  
- Attribute value_length: 0 (or any value < 55)

When LMS scans the file:
1. `malloc(0)` allocates a glibc minimum chunk (typically 16-32 bytes)
2. `read(fd, buf, 0)` reads nothing
3. Size comparison `0 == 0` passes → enters WM/Picture handler
4. Handler scans `buf+5` through `buf+55` → **reads 39-50 bytes of adjacent heap**

### Impact

- **Crash (DoS)**: If adjacent heap contains unmapped memory → SIGSEGV
- **Information Disclosure**: Heap metadata or data from other allocations is read
- **Code Execution (with heap grooming)**: On glibc 2.25 without ASLR:
  - LMS scans ALL files on USB in sequence
  - Earlier files create predictable heap layout
  - Adjacent allocation can contain attacker-controlled data
  - If adjacent data matches "image/jpeg" MIME pattern (18 bytes),
    execution enters the APIC save path with controlled parameters
  - Combined with ZD-ASF-2, this gives a controlled write primitive

---

## ZD-ASF-2: Integer Underflow in WM/Picture Remaining Size

### Root Cause

The remaining-size calculation subtracts fixed constants from the
attacker-controlled `value_length` without unsigned underflow protection:

```
# Virtual address 0x102570 + 0xEDE:
lea   r12d, [r8 - 0x5]     # remaining = value_length - 5
                             # For value_length=0: remaining = 0xFFFFFFFB
                             # For value_length=3: remaining = 0xFFFFFFFE

# After MIME match (subtracts 18 more):
sub   r12d, 0x12            # remaining -= 18 (wraps further)

# Inner description scan loop: NO bounds check on r12d
.desc_loop:
  sub   r12d, 1             # remaining-- (keeps wrapping)
  add   rbx, 1              # pointer advances past buffer
  ...                        # loop has NO exit on r12d <= 0

# Final: wrapped size passed to APIC save
lea   esi, [r12 - 1]        # esi = remaining - 1 (huge wrapped value)
call  lightmediascanner_apic_save   # called with ~4GB "size"
```

### Trigger

Same as ZD-ASF-1 — `WM/Picture` with `value_length < 5`.

### Impact

- `lightmediascanner_apic_save()` receives a wrapped size (~4 billion)
- If it performs a `memcpy(dst, src, size)`, this is a **massive heap overflow**
- Combined with ZD-ASF-1's heap grooming, the source pointer can be controlled
- Even without a write primitive, the huge read causes a guaranteed crash

---

## ZD-ASF-3: Missing Return Value Check in Content Description

### Root Cause

The Content Description Object parser calls `_read_string()` for title/author
fields but doesn't check the boolean return value before using the output:

```
# Virtual address 0x102570 + 0x613:
movsx rsi, word ptr [rsp+0xa8]   # title_length (SIGN-EXTENDED from 16-bit)
call  _read_string                 # may return FALSE (0) if malloc fails
# *** NO CHECK OF RETURN VALUE ***
call  lms_charset_conv_force       # called with stale/uninitialized pointers
```

When `title_length` is 32768-65535:
1. `movsx` sign-extends to a huge 64-bit value (e.g., 0xFFFFFFFFFFFF8000)
2. `malloc()` fails → `_read_string` returns 0 (false)
3. Output pointers in the info struct are **not modified** (keep old values)
4. `lms_charset_conv_force()` is called with whatever those pointers contained

### Trigger

ASF Content Description Object with `title_length` = 0x8000 (32768).

### Impact

- If info struct was zero-initialized: `lms_charset_conv_force(conv, NULL, &0)`
  → potential null pointer dereference depending on implementation
- If info struct has stale pointers from a previous iteration: use-after-free

---

## Exploitation Path

### Prerequisites (all confirmed on target)
- glibc 2.25: No tcache (introduced in 2.26), predictable fastbin/smallbin layout
- No ASLR: `CONFIG_RANDOMIZE_BASE` is not set — fixed addresses
- No sandboxing: LMS runs as root, no seccomp/capabilities/MAC
- No stack protector bypass needed: the bugs are heap-based
- USB auto-scan: LMS automatically scans all media files on USB insertion

### Attack Strategy

1. **Heap Grooming Phase**: Place multiple specifically-sized media files on USB
   that LMS will scan BEFORE the malicious .wma file. These files create a
   predictable heap state where the allocation adjacent to our WM/Picture buffer
   contains controlled data (MIME type pattern + shellcode address).

2. **Trigger Phase**: The crafted .wma file with `WM/Picture` value_length=0:
   - malloc(0) → 16-byte chunk
   - Over-read hits the adjacent controlled allocation
   - memcmp matches "image/jpeg" pattern in controlled data
   - Enters APIC save path with controlled pointer and wrapped size

3. **Code Execution**: `lightmediascanner_apic_save` writes/copies data using
   the controlled pointer and huge size. On glibc 2.25, this can overwrite
   heap metadata (fastbin fd pointer) to achieve arbitrary write.

4. **Post-Exploitation**: Already documented — remount rootfs rw, install
   systemd persistence, access /dev/kmem, etc.

### Alternative: DoS-only
Even without heap grooming, ZD-ASF-1 + ZD-ASF-2 cause a reliable crash:
- Adjacent heap is likely unmapped or contains heap metadata
- Reading 50 bytes past allocation + passing ~4GB size → guaranteed SIGSEGV
- LMS restarts via systemd but the crash happens on every USB scan attempt

---

## PoC Files

All in `exploit/asf_poc/`:

| File | Variant | What it triggers |
|---|---|---|
| `crash_heap_overread.wma` | value_length=0 | ZD-ASF-1 + ZD-ASF-2: heap over-read + int underflow |
| `crash_heap_overread_v2.wma` | value_length=1 | Same, 1 byte of controlled data |
| `crash_int_underflow.wma` | value_length=3 | ZD-ASF-2: integer underflow (remaining = -2) |
| `crash_sign_extension.wma` | length=0x8000 | ZD-ASF-3: sign extension → malloc fail → null deref |

**Usage**: Copy any .wma file to a FAT32 USB stick, insert into car.
LMS auto-scans on mount → triggers vulnerability → crash or code execution.

Generator script: `exploit/asf_zeroday_poc.py`

---

## Affected Code

- **Binary**: `lms_asf.so` (SHA256: be6f3b40629b474c88953786a20223302090107cd43a6a32f3393bb7c69ae14a)
- **Size**: 34,792 bytes
- **Source**: `asf.c` (per debug strings)
- **Function**: `_parse` at virtual address 0x102570 (4,592 bytes)
- **Sub-function**: `_read_string` at 0x1021d0, `_read_word` at 0x102040
- **Vulnerable code offsets** (from function start):
  - 0xEB8 (WM/Picture entry): hardcoded buf+5 / buf+0x37
  - 0xEDE (size calc): `lea r12d, [r8 - 5]` without bounds check
  - 0xF61 (inner loop): no `r12d > 0` check
  - 0xF8D (APIC save): wrapped size passed unchecked
  - 0x613 (Content Desc): missing return value check

---

## Verification Notes

- The `memcmp(..., 0)` pattern seen in Ghidra's decompilation was a **decompilation
  artifact**. The actual assembly uses `r12d` (loaded from `[rsp+0x90]`, the name
  string length from `_read_string`) as the memcmp size. Verified via objdump.

- `FUN_00102040` (`_read_word`) takes TWO parameters: `(int fd, ushort *out)`.
  It writes through the pointer, not via return value. Ghidra's decompilation
  of the main function incorrectly showed some calls as single-argument.

- The sign extension throughout uses `movsx` (sign-extending move), confirmed in
  all call sites for `_read_string`. Values 0x8000-0xFFFF always produce huge
  unsigned values that cause `malloc` to fail.
