/* Freestanding Linux/x86-64 QEMU-only graphics diagnostic.
 * NOT Hyundai/LG userland, not an infotainment UI, and not a hardware driver.
 * Uses QEMU std-VGA PCI resource mmap + DISPI MMIO, with polling keyboard input.
 * All code/data are in one position-independent section; no libc or linker.
 */
.text
.globl _start
_start:
    subq $4096, %rsp
    movq %rsp, %r15

    /* Refuse ordinary bare metal before touching virtual display or I/O. */
    movl $1, %eax
    cpuid
    testl $0x80000000, %ecx
    jz .Lidentity_error

    /* Require the fixed harness BDF to be QEMU std-VGA (1234:1111). */
    leaq .Lvendor_path(%rip), %rdi
    leaq .Lvendor_value(%rip), %rsi
    call .Lcheck_identity
    leaq .Ldevice_path(%rip), %rdi
    leaq .Ldevice_value(%rip), %rsi
    call .Lcheck_identity

    /* BAR2: QEMU's standard VGA MMIO aperture, including DISPI at +0x500. */
    leaq .Lmmio_path(%rip), %rdi
    movl $4096, %esi
    call .Lmap_resource
    movq %rax, %r13
    movzwl 0x500(%r13), %eax
    cmpl $0xb0c0, %eax
    jb .Ldisplay_error
    cmpl $0xb0c5, %eax
    ja .Ldisplay_error

    /* BAR0: 800 * 480 * 4 bytes of framebuffer memory. */
    leaq .Lfb_path(%rip), %rdi
    movl $1536000, %esi
    call .Lmap_resource
    movq %rax, %r12

    /* Read our own diagnostic background, never a vendor GUI asset. */
    leaq .Lbackground_path(%rip), %rdi
    xorl %esi, %esi
    xorl %edx, %edx
    movl $2, %eax                 /* open */
    syscall
    testq %rax, %rax
    js .Lbackground_error
    movq %rax, %rbx
    movq %r12, %r10
    movl $1536000, %r9d
.Lread_background:
    xorl %eax, %eax               /* read */
    movq %rbx, %rdi
    movq %r10, %rsi
    movq %r9, %rdx
    syscall
    testq %rax, %rax
    jle .Lbackground_error
    addq %rax, %r10
    subq %rax, %r9
    jnz .Lread_background
    movl $3, %eax                 /* close */
    movq %rbx, %rdi
    syscall

    /* Configure a 32-bpp linear framebuffer through DISPI registers. */
    movw $0, 0x508(%r13)          /* disable */
    movw $800, 0x502(%r13)
    movw $480, 0x504(%r13)
    movw $32, 0x506(%r13)
    movw $0, 0x50a(%r13)          /* bank */
    movw $800, 0x50c(%r13)        /* virtual width */
    movw $0, 0x510(%r13)          /* x offset */
    movw $0, 0x512(%r13)          /* y offset */
    movw $0xc1, 0x508(%r13)       /* enabled, LFB, retain framebuffer */
    movl $0x224466, %eax
    call .Lfill_patch

    /* Only the emulated PS/2 controller ports; never /dev/mem or host ports. */
    movl $173, %eax               /* ioperm(0x60, 5, 1) */
    movl $0x60, %edi
    movl $5, %esi
    movl $1, %edx
    syscall
    testq %rax, %rax
    js .Linput_error
    movl $100000, %ecx
.Lkeyboard_wait:
    inb $0x64, %al
    testb $2, %al
    jz .Lkeyboard_enable
    loop .Lkeyboard_wait
    jmp .Linput_error
.Lkeyboard_enable:
    movb $0xf4, %al               /* enable keyboard scanning */
    outb %al, $0x60

    movl $72, %eax                /* fcntl(0, F_GETFL) */
    xorl %edi, %edi
    movl $3, %esi
    xorl %edx, %edx
    syscall
    testq %rax, %rax
    js .Linput_error
    movq %rax, %rbp
    movq %rax, %rdx
    orl $0x800, %edx              /* O_NONBLOCK, restored on normal exit */
    movl $72, %eax
    xorl %edi, %edi
    movl $4, %esi
    syscall
    testq %rax, %rax
    js .Linput_error
    movq $0, 32(%r15)
    movq $20000000, 40(%r15)      /* 20 ms poll interval */
    leaq .Lready(%rip), %rsi
    movl $.Lready_end-.Lready, %edx
    call .Lprint

.Lpoll:
    xorl %eax, %eax
    xorl %edi, %edi
    movq %r15, %rsi
    movl $1, %edx
    syscall
    cmpq $1, %rax
    jne .Lpoll_keyboard
    movzbl (%r15), %eax
    cmpb $'r', %al
    je .Lred
    cmpb $'g', %al
    je .Lgreen
    cmpb $'b', %al
    je .Lblue
    cmpb $'q', %al
    je .Lquit
.Lpoll_keyboard:
    inb $0x64, %al
    testb $1, %al
    jz .Lsleep
    testb $0x20, %al              /* discard auxiliary/mouse bytes */
    jnz .Ldiscard_aux
    inb $0x60, %al
    cmpb $0x13, %al              /* translated set-1 R/G/B/Q make codes */
    je .Lred
    cmpb $0x22, %al
    je .Lgreen
    cmpb $0x30, %al
    je .Lblue
    cmpb $0x10, %al
    je .Lquit
    jmp .Lpoll
.Ldiscard_aux:
    inb $0x60, %al
    jmp .Lpoll
.Lsleep:
    movl $35, %eax                /* nanosleep */
    leaq 32(%r15), %rdi
    xorl %esi, %esi
    syscall
    jmp .Lpoll
.Lred:
    movl $0xc23737, %eax
    call .Lfill_patch
    leaq .Lred_msg(%rip), %rsi
    movl $.Lred_end-.Lred_msg, %edx
    call .Lprint
    jmp .Lpoll
.Lgreen:
    movl $0x2b9c6f, %eax
    call .Lfill_patch
    leaq .Lgreen_msg(%rip), %rsi
    movl $.Lgreen_end-.Lgreen_msg, %edx
    call .Lprint
    jmp .Lpoll
.Lblue:
    movl $0x3267c8, %eax
    call .Lfill_patch
    leaq .Lblue_msg(%rip), %rsi
    movl $.Lblue_end-.Lblue_msg, %edx
    call .Lprint
    jmp .Lpoll
.Lquit:
    movl $72, %eax
    xorl %edi, %edi
    movl $4, %esi
    movq %rbp, %rdx
    syscall
    leaq .Lquit_msg(%rip), %rsi
    movl $.Lquit_end-.Lquit_msg, %edx
    call .Lprint
    xorl %edi, %edi
    jmp .Lexit

/* Identity helper: path in rdi, expected seven-byte sysfs value in rsi. */
.Lcheck_identity:
    pushq %rsi
    movq $0, (%r15)
    movl $2, %eax
    xorl %esi, %esi
    xorl %edx, %edx
    syscall
    testq %rax, %rax
    js .Lidentity_error
    movq %rax, %rbx
    movq %rax, %rdi
    movq %r15, %rsi
    movl $8, %edx
    xorl %eax, %eax
    syscall
    cmpq $7, %rax
    jne .Lidentity_error
    movl $3, %eax
    movq %rbx, %rdi
    syscall
    popq %rsi
    movq (%r15), %rax
    cmpq (%rsi), %rax
    jne .Lidentity_error
    ret

/* Map a verified PCI resource: path in rdi, size in rsi; result in rax. */
.Lmap_resource:
    pushq %rsi
    movl $2, %eax
    movl $2, %esi                 /* O_RDWR */
    xorl %edx, %edx
    syscall
    testq %rax, %rax
    js .Lmap_error
    movq %rax, %rbx
    movq %rax, %r8
    movl $9, %eax                 /* mmap */
    xorl %edi, %edi
    popq %rsi
    movl $3, %edx                 /* PROT_READ | PROT_WRITE */
    movl $1, %r10d                /* MAP_SHARED */
    xorl %r9d, %r9d
    syscall
    testq %rax, %rax
    js .Lmap_error
    pushq %rax
    movl $3, %eax
    movq %rbx, %rdi
    syscall
    popq %rax
    ret

/* Fill only the 640x160 color patch at (80,240); preserve diagnostic labels. */
.Lfill_patch:
    leaq 768320(%r12), %rdi
    movl $160, %r8d
.Lfill_row:
    movl $640, %ecx
    rep stosl
    addq $640, %rdi
    decl %r8d
    jnz .Lfill_row
    ret
.Lprint:
    movl $1, %eax
    movl $1, %edi
    syscall
    ret
.Lidentity_error:
    leaq .Lidentity_msg(%rip), %rsi
    movl $.Lidentity_end-.Lidentity_msg, %edx
    jmp .Lerror
.Lmap_error:
    leaq .Lmap_msg(%rip), %rsi
    movl $.Lmap_end-.Lmap_msg, %edx
    jmp .Lerror
.Ldisplay_error:
    leaq .Ldisplay_msg(%rip), %rsi
    movl $.Ldisplay_end-.Ldisplay_msg, %edx
    jmp .Lerror
.Lbackground_error:
    leaq .Lbackground_msg(%rip), %rsi
    movl $.Lbackground_end-.Lbackground_msg, %edx
    jmp .Lerror
.Linput_error:
    leaq .Linput_msg(%rip), %rsi
    movl $.Linput_end-.Linput_msg, %edx
.Lerror:
    call .Lprint
    movl $2, %edi
.Lexit:
    movl $60, %eax
    syscall
    ud2

.Lvendor_path: .asciz "/sys/bus/pci/devices/0000:00:01.0/vendor"
.Ldevice_path: .asciz "/sys/bus/pci/devices/0000:00:01.0/device"
.Lvendor_value: .asciz "0x1234\n"
.Ldevice_value: .asciz "0x1111\n"
.Lmmio_path: .asciz "/sys/bus/pci/devices/0000:00:01.0/resource2"
.Lfb_path: .asciz "/sys/bus/pci/devices/0000:00:01.0/resource0"
.Lbackground_path: .asciz "/opt/vm-display.bgra"
.Lready: .ascii "VM_DISPLAY_READY 800x480 BGRX32 - DIAGNOSTIC ONLY\n"
.Lready_end:
.Lred_msg: .ascii "VM_DISPLAY_RED\n"
.Lred_end:
.Lgreen_msg: .ascii "VM_DISPLAY_GREEN\n"
.Lgreen_end:
.Lblue_msg: .ascii "VM_DISPLAY_BLUE\n"
.Lblue_end:
.Lquit_msg: .ascii "VM_DISPLAY_EXIT\n"
.Lquit_end:
.Lidentity_msg: .ascii "VM_DISPLAY_ERROR: not the expected virtual PCI display\n"
.Lidentity_end:
.Lmap_msg: .ascii "VM_DISPLAY_ERROR: PCI resource open or mmap failed\n"
.Lmap_end:
.Ldisplay_msg: .ascii "VM_DISPLAY_ERROR: unsupported DISPI register ID\n"
.Ldisplay_end:
.Lbackground_msg: .ascii "VM_DISPLAY_ERROR: diagnostic background read failed\n"
.Lbackground_end:
.Linput_msg: .ascii "VM_DISPLAY_ERROR: keyboard IO or serial setup failed\n"
.Linput_end:
