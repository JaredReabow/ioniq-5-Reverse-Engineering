
work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/ApplicationManager:	file format elf64-x86-64

Disassembly of section .text:

00000000001e5440 <_ZN5QListI8QVariantED2Ev>:
  205730: 41 54                        	pushq	%r12
  205732: 49 89 f4                     	movq	%rsi, %r12
  205735: 55                           	pushq	%rbp
  205736: 53                           	pushq	%rbx
  205737: 48 83 ec 10                  	subq	$0x10, %rsp
  20573b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
  205744: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
  205749: 31 c0                        	xorl	%eax, %eax
  20574b: 48 8b 07                     	movq	(%rdi), %rax
  20574e: 48 8d 50 10                  	leaq	0x10(%rax), %rdx
  205752: 48 63 48 08                  	movslq	0x8(%rax), %rcx
  205756: 48 63 40 0c                  	movslq	0xc(%rax), %rax
  20575a: 48 8d 2c ca                  	leaq	(%rdx,%rcx,8), %rbp
  20575e: 48 8d 1c c2                  	leaq	(%rdx,%rax,8), %rbx
  205762: eb 13                        	jmp	0x205777 <_ZN5QListI8QVariantED2Ev+0x20337>
  205764: 0f 1f 40 00                  	nopl	(%rax)
  205768: 4c 89 e6                     	movq	%r12, %rsi
  20576b: 48 89 df                     	movq	%rbx, %rdi
  20576e: e8 6d 65 e2 ff               	callq	0x2bce0 <_ZeqRK7QStringS1_@plt>
  205773: 84 c0                        	testb	%al, %al
  205775: 75 0f                        	jne	0x205786 <_ZN5QListI8QVariantED2Ev+0x20346>
  205777: 48 83 eb 08                  	subq	$0x8, %rbx
  20577b: 48 8d 43 08                  	leaq	0x8(%rbx), %rax
  20577f: 48 39 c5                     	cmpq	%rax, %rbp
  205782: 75 e4                        	jne	0x205768 <_ZN5QListI8QVariantED2Ev+0x20328>
  205784: 31 c0                        	xorl	%eax, %eax
  205786: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
  20578b: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
  205794: 75 09                        	jne	0x20579f <_ZN5QListI8QVariantED2Ev+0x2035f>
  205796: 48 83 c4 10                  	addq	$0x10, %rsp
  20579a: 5b                           	popq	%rbx
  20579b: 5d                           	popq	%rbp
  20579c: 41 5c                        	popq	%r12
  20579e: c3                           	retq
  20579f: e8 cc 58 e2 ff               	callq	0x2b070 <__stack_chk_fail@plt>
