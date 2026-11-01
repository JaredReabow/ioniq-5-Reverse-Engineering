
work/vm/vendor-userspace-260128/navigation-contract-audit/guest-libEGL.so:	file format elf64-x86-64

Disassembly of section .text:

0000000000016a50 <swrast_update_buffers>:
   16a50: 55                           	pushq	%rbp
   16a51: 48 89 e5                     	movq	%rsp, %rbp
   16a54: 41 57                        	pushq	%r15
   16a56: 41 56                        	pushq	%r14
   16a58: 41 55                        	pushq	%r13
   16a5a: 41 54                        	pushq	%r12
   16a5c: 53                           	pushq	%rbx
   16a5d: 48 83 ec 48                  	subq	$0x48, %rsp
   16a61: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
   16a6a: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
   16a6e: 31 c0                        	xorl	%eax, %eax
   16a70: 48 83 bf 50 02 00 00 00      	cmpq	$0x0, 0x250(%rdi)
   16a78: 74 26                        	je	0x16aa0 <swrast_update_buffers+0x50>
   16a7a: 31 c0                        	xorl	%eax, %eax
   16a7c: 48 8b 4d c8                  	movq	-0x38(%rbp), %rcx
   16a80: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
   16a89: 0f 85 ef 03 00 00            	jne	0x16e7e <swrast_update_buffers+0x42e>
   16a8f: 48 8d 65 d8                  	leaq	-0x28(%rbp), %rsp
   16a93: 5b                           	popq	%rbx
   16a94: 41 5c                        	popq	%r12
   16a96: 41 5d                        	popq	%r13
   16a98: 41 5e                        	popq	%r14
   16a9a: 41 5f                        	popq	%r15
   16a9c: 5d                           	popq	%rbp
   16a9d: c3                           	retq
   16a9e: 66 90                        	nop
   16aa0: 48 8b 07                     	movq	(%rdi), %rax
   16aa3: 49 89 fe                     	movq	%rdi, %r14
   16aa6: 4c 8b 68 58                  	movq	0x58(%rax), %r13
   16aaa: 48 8b 87 f0 00 00 00         	movq	0xf0(%rdi), %rax
   16ab1: 8b 48 08                     	movl	0x8(%rax), %ecx
   16ab4: 39 4f 2c                     	cmpl	%ecx, 0x2c(%rdi)
   16ab7: 0f 84 03 01 00 00            	je	0x16bc0 <swrast_update_buffers+0x170>
   16abd: 4c 89 f7                     	movq	%r14, %rdi
   16ac0: e8 4b e6 ff ff               	callq	0x15110 <dri2_wl_release_buffers>
   16ac5: 49 8b 86 f0 00 00 00         	movq	0xf0(%r14), %rax
   16acc: 8b 50 08                     	movl	0x8(%rax), %edx
   16acf: 41 89 56 2c                  	movl	%edx, 0x2c(%r14)
   16ad3: 8b 50 0c                     	movl	0xc(%rax), %edx
   16ad6: 41 89 56 30                  	movl	%edx, 0x30(%r14)
   16ada: 8b 50 10                     	movl	0x10(%rax), %edx
   16add: 41 89 96 f8 00 00 00         	movl	%edx, 0xf8(%r14)
   16ae4: 8b 40 14                     	movl	0x14(%rax), %eax
   16ae7: 49 c7 86 58 02 00 00 00 00 00 00     	movq	$0x0, 0x258(%r14)
   16af2: 41 89 86 fc 00 00 00         	movl	%eax, 0xfc(%r14)
   16af9: eb 21                        	jmp	0x16b1c <swrast_update_buffers+0xcc>
   16afb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
   16b00: 49 8b b5 78 01 00 00         	movq	0x178(%r13), %rsi
   16b07: 49 8b bd 50 01 00 00         	movq	0x150(%r13), %rdi
   16b0e: e8 bd e5 fe ff               	callq	0x50d0 <wl_display_dispatch_queue@plt>
   16b13: 83 f8 ff                     	cmpl	$-0x1, %eax
   16b16: 0f 84 60 ff ff ff            	je	0x16a7c <swrast_update_buffers+0x2c>
   16b1c: 49 83 be 00 01 00 00 00      	cmpq	$0x0, 0x100(%r14)
   16b24: 75 da                        	jne	0x16b00 <swrast_update_buffers+0xb0>
   16b26: 49 8d 86 a0 01 00 00         	leaq	0x1a0(%r14), %rax
   16b2d: 31 d2                        	xorl	%edx, %edx
   16b2f: 44 8b 00                     	movl	(%rax), %r8d
   16b32: 45 85 c0                     	testl	%r8d, %r8d
   16b35: 75 0b                        	jne	0x16b42 <swrast_update_buffers+0xf2>
   16b37: 48 83 78 d0 00               	cmpq	$0x0, -0x30(%rax)
   16b3c: 0f 85 e3 00 00 00            	jne	0x16c25 <swrast_update_buffers+0x1d5>
   16b42: 83 c2 01                     	addl	$0x1, %edx
   16b45: 48 83 c0 38                  	addq	$0x38, %rax
   16b49: 83 fa 04                     	cmpl	$0x4, %edx
   16b4c: 75 e1                        	jne	0x16b2f <swrast_update_buffers+0xdf>
   16b4e: 49 8b 86 50 02 00 00         	movq	0x250(%r14), %rax
   16b55: 48 85 c0                     	testq	%rax, %rax
   16b58: 74 77                        	je	0x16bd1 <swrast_update_buffers+0x181>
   16b5a: c7 40 30 01 00 00 00         	movl	$0x1, 0x30(%rax)
   16b61: 49 8d 9e 70 01 00 00         	leaq	0x170(%r14), %rbx
   16b68: 4d 8d ae 50 02 00 00         	leaq	0x250(%r14), %r13
   16b6f: 8b 53 30                     	movl	0x30(%rbx), %edx
   16b72: 85 d2                        	testl	%edx, %edx
   16b74: 75 38                        	jne	0x16bae <swrast_update_buffers+0x15e>
   16b76: 4c 8b 23                     	movq	(%rbx), %r12
   16b79: 4d 85 e4                     	testq	%r12, %r12
   16b7c: 74 30                        	je	0x16bae <swrast_update_buffers+0x15e>
   16b7e: 31 f6                        	xorl	%esi, %esi
   16b80: 31 c0                        	xorl	%eax, %eax
   16b82: 4c 89 e7                     	movq	%r12, %rdi
   16b85: e8 d6 e6 fe ff               	callq	0x5260 <wl_proxy_marshal@plt>
   16b8a: 4c 89 e7                     	movq	%r12, %rdi
   16b8d: e8 8e e6 fe ff               	callq	0x5220 <wl_proxy_destroy@plt>
   16b92: 48 63 73 20                  	movslq	0x20(%rbx), %rsi
   16b96: 48 8b 7b 18                  	movq	0x18(%rbx), %rdi
   16b9a: e8 51 e5 fe ff               	callq	0x50f0 <munmap@plt>
   16b9f: 48 c7 03 00 00 00 00         	movq	$0x0, (%rbx)
   16ba6: 48 c7 43 18 00 00 00 00      	movq	$0x0, 0x18(%rbx)
   16bae: 48 83 c3 38                  	addq	$0x38, %rbx
   16bb2: 49 39 dd                     	cmpq	%rbx, %r13
   16bb5: 75 b8                        	jne	0x16b6f <swrast_update_buffers+0x11f>
   16bb7: e9 be fe ff ff               	jmp	0x16a7a <swrast_update_buffers+0x2a>
   16bbc: 0f 1f 40 00                  	nopl	(%rax)
   16bc0: 8b 40 0c                     	movl	0xc(%rax), %eax
   16bc3: 39 47 30                     	cmpl	%eax, 0x30(%rdi)
   16bc6: 0f 85 f1 fe ff ff            	jne	0x16abd <swrast_update_buffers+0x6d>
   16bcc: e9 4b ff ff ff               	jmp	0x16b1c <swrast_update_buffers+0xcc>
   16bd1: 41 8b 86 a0 01 00 00         	movl	0x1a0(%r14), %eax
   16bd8: 85 c0                        	testl	%eax, %eax
   16bda: 74 6f                        	je	0x16c4b <swrast_update_buffers+0x1fb>
   16bdc: 41 8b be d8 01 00 00         	movl	0x1d8(%r14), %edi
   16be3: 85 ff                        	testl	%edi, %edi
   16be5: 0f 84 a2 02 00 00            	je	0x16e8d <swrast_update_buffers+0x43d>
   16beb: 41 8b b6 10 02 00 00         	movl	0x210(%r14), %esi
   16bf2: 85 f6                        	testl	%esi, %esi
   16bf4: 0f 84 89 02 00 00            	je	0x16e83 <swrast_update_buffers+0x433>
   16bfa: 41 8b 8e 48 02 00 00         	movl	0x248(%r14), %ecx
   16c01: b8 03 00 00 00               	movl	$0x3, %eax
   16c06: 85 c9                        	testl	%ecx, %ecx
   16c08: 74 43                        	je	0x16c4d <swrast_update_buffers+0x1fd>
   16c0a: 48 8d 35 4b b0 00 00         	leaq	0xb04b(%rip), %rsi      # 0x21c5c <wl_drm_components+0x11c>
   16c11: bf 03 30 00 00               	movl	$0x3003, %edi           # imm = 0x3003
   16c16: e8 75 6e ff ff               	callq	0xda90 <_eglError>
   16c1b: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
