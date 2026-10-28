
work/vm/vendor-userspace-260128/navigation-contract-audit/guest-libEGL.so:	file format elf64-x86-64

Disassembly of section .text:

0000000000016eb0 <dri2_wl_swrast_put_image2>:
   16eb0: 55                           	pushq	%rbp
   16eb1: 48 89 e5                     	movq	%rsp, %rbp
   16eb4: 41 57                        	pushq	%r15
   16eb6: 41 56                        	pushq	%r14
   16eb8: 41 55                        	pushq	%r13
   16eba: 41 54                        	pushq	%r12
   16ebc: 53                           	pushq	%rbx
   16ebd: 48 83 ec 38                  	subq	$0x38, %rsp
   16ec1: 8b 45 10                     	movl	0x10(%rbp), %eax
   16ec4: 48 89 7d a8                  	movq	%rdi, -0x58(%rbp)
   16ec8: 4c 8b 7d 20                  	movq	0x20(%rbp), %r15
   16ecc: 89 4d b8                     	movl	%ecx, -0x48(%rbp)
   16ecf: 44 89 4d b4                  	movl	%r9d, -0x4c(%rbp)
   16ed3: 4c 8b 65 18                  	movq	0x18(%rbp), %r12
   16ed7: 89 45 b0                     	movl	%eax, -0x50(%rbp)
   16eda: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
   16ee3: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
   16ee7: 31 c0                        	xorl	%eax, %eax
   16ee9: 41 81 bf 08 01 00 00 52 47 31 36     	cmpl	$0x36314752, 0x108(%r15) # imm = 0x36314752
   16ef4: 0f 84 1e 02 00 00            	je	0x17118 <dri2_wl_swrast_put_image2+0x268>
   16efa: 41 8b 47 2c                  	movl	0x2c(%r15), %eax
   16efe: 42 8d 1c 85 00 00 00 00      	leal	(,%r8,4), %ebx
   16f06: 44 8d 34 95 00 00 00 00      	leal	(,%rdx,4), %r14d
   16f0e: 44 8d 2c 85 00 00 00 00      	leal	(,%rax,4), %r13d
   16f16: 4c 89 ff                     	movq	%r15, %rdi
   16f19: e8 32 fb ff ff               	callq	0x16a50 <swrast_update_buffers>
   16f1e: 49 8b 87 50 02 00 00         	movq	0x250(%r15), %rax
   16f25: 48 8b 40 18                  	movq	0x18(%rax), %rax
   16f29: 44 39 eb                     	cmpl	%r13d, %ebx
   16f2c: 0f 8c b6 01 00 00            	jl	0x170e8 <dri2_wl_swrast_put_image2+0x238>
   16f32: 8b 75 b8                     	movl	-0x48(%rbp), %esi
   16f35: 49 63 d6                     	movslq	%r14d, %rdx
   16f38: 89 f1                        	movl	%esi, %ecx
   16f3a: 41 0f af cd                  	imull	%r13d, %ecx
   16f3e: 48 63 c9                     	movslq	%ecx, %rcx
   16f41: 48 01 d1                     	addq	%rdx, %rcx
   16f44: 48 01 c1                     	addq	%rax, %rcx
   16f47: 44 89 e8                     	movl	%r13d, %eax
   16f4a: 4d 63 ed                     	movslq	%r13d, %r13
   16f4d: 44 29 f0                     	subl	%r14d, %eax
   16f50: 39 d8                        	cmpl	%ebx, %eax
   16f52: 41 89 c6                     	movl	%eax, %r14d
   16f55: 41 8b 47 30                  	movl	0x30(%r15), %eax
   16f59: 44 0f 4f f3                  	cmovgl	%ebx, %r14d
   16f5d: 8b 5d b4                     	movl	-0x4c(%rbp), %ebx
   16f60: 4d 63 f6                     	movslq	%r14d, %r14
   16f63: 29 f0                        	subl	%esi, %eax
   16f65: 39 d8                        	cmpl	%ebx, %eax
   16f67: 0f 4e d8                     	cmovlel	%eax, %ebx
   16f6a: 48 63 45 b0                  	movslq	-0x50(%rbp), %rax
   16f6e: 85 db                        	testl	%ebx, %ebx
   16f70: 7e 2e                        	jle	0x16fa0 <dri2_wl_swrast_put_image2+0xf0>
   16f72: 4c 89 7d b8                  	movq	%r15, -0x48(%rbp)
   16f76: 4d 89 e7                     	movq	%r12, %r15
   16f79: 49 89 c4                     	movq	%rax, %r12
   16f7c: 0f 1f 40 00                  	nopl	(%rax)
   16f80: 4c 89 fe                     	movq	%r15, %rsi
   16f83: 48 89 cf                     	movq	%rcx, %rdi
   16f86: 4c 89 f2                     	movq	%r14, %rdx
   16f89: e8 52 e0 fe ff               	callq	0x4fe0 <memcpy@plt>
   16f8e: 4d 01 e7                     	addq	%r12, %r15
