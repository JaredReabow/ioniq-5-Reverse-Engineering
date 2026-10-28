
work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/ApplicationManager:	file format elf64-x86-64

Disassembly of section .text:

00000000001e5440 <_ZN5QListI8QVariantED2Ev>:
  2052e0: 48 83 ec 18                  	subq	$0x18, %rsp
  2052e4: 48 8b 4f 10                  	movq	0x10(%rdi), %rcx
  2052e8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
  2052f1: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
  2052f6: 31 c0                        	xorl	%eax, %eax
  2052f8: 44 8b 49 0c                  	movl	0xc(%rcx), %r9d
  2052fc: 8b 41 08                     	movl	0x8(%rcx), %eax
  2052ff: 41 29 c1                     	subl	%eax, %r9d
  205302: 45 85 c9                     	testl	%r9d, %r9d
  205305: 7e 3b                        	jle	0x205342 <_ZN5QListI8QVariantED2Ev+0x1ff02>
  205307: 4c 8d 41 10                  	leaq	0x10(%rcx), %r8
  20530b: 48 63 c8                     	movslq	%eax, %rcx
  20530e: 49 8d 04 c8                  	leaq	(%r8,%rcx,8), %rax
  205312: 48 8b 38                     	movq	(%rax), %rdi
  205315: 3b 77 10                     	cmpl	0x10(%rdi), %esi
  205318: 74 46                        	je	0x205360 <_ZN5QListI8QVariantED2Ev+0x1ff20>
  20531a: 41 8d 79 ff                  	leal	-0x1(%r9), %edi
  20531e: 48 01 f9                     	addq	%rdi, %rcx
  205321: 49 8d 0c c8                  	leaq	(%r8,%rcx,8), %rcx
  205325: eb 16                        	jmp	0x20533d <_ZN5QListI8QVariantED2Ev+0x1fefd>
  205327: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
  205330: 48 8b 78 08                  	movq	0x8(%rax), %rdi
  205334: 48 83 c0 08                  	addq	$0x8, %rax
  205338: 39 77 10                     	cmpl	%esi, 0x10(%rdi)
  20533b: 74 23                        	je	0x205360 <_ZN5QListI8QVariantED2Ev+0x1ff20>
  20533d: 48 39 c8                     	cmpq	%rcx, %rax
  205340: 75 ee                        	jne	0x205330 <_ZN5QListI8QVariantED2Ev+0x1fef0>
  205342: 31 c0                        	xorl	%eax, %eax
  205344: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
  205349: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
  205352: 75 2c                        	jne	0x205380 <_ZN5QListI8QVariantED2Ev+0x1ff40>
  205354: 48 83 c4 18                  	addq	$0x18, %rsp
  205358: c3                           	retq
  205359: 0f 1f 80 00 00 00 00         	nopl	(%rax)
  205360: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
  205365: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
  20536e: 75 10                        	jne	0x205380 <_ZN5QListI8QVariantED2Ev+0x1ff40>
  205370: 48 83 c7 08                  	addq	$0x8, %rdi
  205374: 48 89 d6                     	movq	%rdx, %rsi
  205377: 48 83 c4 18                  	addq	$0x18, %rsp
  20537b: e9 b0 03 00 00               	jmp	0x205730 <_ZN5QListI8QVariantED2Ev+0x202f0>
  205380: e8 eb 5c e2 ff               	callq	0x2b070 <__stack_chk_fail@plt>
