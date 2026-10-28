
work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/weston/ivi-shell.so:	file format elf64-x86-64

Disassembly of section .text:

0000000000009c00 <ivi_shell_surface_configure>:
    9c00: 53                           	pushq	%rbx
    9c01: 48 83 ec 10                  	subq	$0x10, %rsp
    9c05: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9c0e: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9c13: 31 c0                        	xorl	%eax, %eax
    9c15: 48 8b 05 ac 73 20 00         	movq	0x2073ac(%rip), %rax    # 0x210fc8 <_GLOBAL_OFFSET_TABLE_+0x3b0>
    9c1c: 48 39 87 80 02 00 00         	cmpq	%rax, 0x280(%rdi)
    9c23: 74 1b                        	je	0x9c40 <ivi_shell_surface_configure+0x40>
    9c25: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    9c2a: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9c33: 75 6b                        	jne	0x9ca0 <ivi_shell_surface_configure+0xa0>
    9c35: 48 83 c4 10                  	addq	$0x10, %rsp
    9c39: 5b                           	popq	%rbx
    9c3a: c3                           	retq
    9c3b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    9c40: 48 8b 9f 88 02 00 00         	movq	0x288(%rdi), %rbx
    9c47: 48 85 db                     	testq	%rbx, %rbx
    9c4a: 74 d9                        	je	0x9c25 <ivi_shell_surface_configure+0x25>
    9c4c: 8b 77 68                     	movl	0x68(%rdi), %esi
    9c4f: 39 73 3c                     	cmpl	%esi, 0x3c(%rbx)
    9c52: 8b 57 6c                     	movl	0x6c(%rdi), %edx
    9c55: 75 05                        	jne	0x9c5c <ivi_shell_surface_configure+0x5c>
    9c57: 39 53 40                     	cmpl	%edx, 0x40(%rbx)
    9c5a: 74 c9                        	je	0x9c25 <ivi_shell_surface_configure+0x25>
    9c5c: 48 8b 7b 10                  	movq	0x10(%rbx), %rdi
    9c60: 89 73 3c                     	movl	%esi, 0x3c(%rbx)
    9c63: 89 53 40                     	movl	%edx, 0x40(%rbx)
    9c66: e8 35 e5 ff ff               	callq	0x81a0 <ivi_layout_surface_configure>
    9c6b: 8b 43 70                     	movl	0x70(%rbx), %eax
    9c6e: 85 c0                        	testl	%eax, %eax
    9c70: 75 b3                        	jne	0x9c25 <ivi_shell_surface_configure+0x25>
    9c72: 48 8b 43 10                  	movq	0x10(%rbx), %rax
    9c76: 80 b8 d0 00 00 00 00         	cmpb	$0x0, 0xd0(%rax)
    9c7d: 74 11                        	je	0x9c90 <ivi_shell_surface_configure+0x90>
    9c7f: c7 43 70 01 00 00 00         	movl	$0x1, 0x70(%rbx)
    9c86: eb 9d                        	jmp	0x9c25 <ivi_shell_surface_configure+0x25>
    9c88: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    9c90: 48 8b 3b                     	movq	(%rbx), %rdi
    9c93: 31 d2                        	xorl	%edx, %edx
    9c95: 31 f6                        	xorl	%esi, %esi
    9c97: 31 c0                        	xorl	%eax, %eax
    9c99: e8 c2 98 ff ff               	callq	0x3560 <wl_resource_post_event@plt>
    9c9e: eb df                        	jmp	0x9c7f <ivi_shell_surface_configure+0x7f>
    9ca0: e8 7b 95 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
