
work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/ApplicationManager:	file format elf64-x86-64

Disassembly of section .text:

0000000000225900 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE>:
  287e70: 41 57                        	pushq	%r15
  287e72: 41 56                        	pushq	%r14
  287e74: 41 89 f6                     	movl	%esi, %r14d
  287e77: be 30 00 00 00               	movl	$0x30, %esi
  287e7c: 41 55                        	pushq	%r13
  287e7e: 49 89 fd                     	movq	%rdi, %r13
  287e81: 41 54                        	pushq	%r12
  287e83: 55                           	pushq	%rbp
  287e84: 53                           	pushq	%rbx
  287e85: 48 83 ec 38                  	subq	$0x38, %rsp
  287e89: 44 0f b6 67 20               	movzbl	0x20(%rdi), %r12d
  287e8e: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
  287e97: 48 89 44 24 28               	movq	%rax, 0x28(%rsp)
  287e9c: 31 c0                        	xorl	%eax, %eax
  287e9e: 48 8d 3d 4b 48 09 00         	leaq	0x9484b(%rip), %rdi     # 0x31c6f0
  287ea5: 49 89 e7                     	movq	%rsp, %r15
  287ea8: e8 f3 29 da ff               	callq	0x2a8a0 <_ZN7QString16fromAscii_helperEPKci@plt>
  287ead: 48 8d 6c 24 10               	leaq	0x10(%rsp), %rbp
  287eb2: 49 63 d6                     	movslq	%r14d, %rdx
  287eb5: 31 c9                        	xorl	%ecx, %ecx
  287eb7: 41 b9 20 00 00 00            	movl	$0x20, %r9d
  287ebd: 48 89 e6                     	movq	%rsp, %rsi
  287ec0: 48 89 ef                     	movq	%rbp, %rdi
  287ec3: 48 89 04 24                  	movq	%rax, (%rsp)
  287ec7: 41 b8 0a 00 00 00            	movl	$0xa, %r8d
  287ecd: e8 3e 26 da ff               	callq	0x2a510 <_ZNK7QString3argExii5QChar@plt>
  287ed2: 48 8d 5c 24 20               	leaq	0x20(%rsp), %rbx
  287ed7: 41 0f b6 d4                  	movzbl	%r12b, %edx
  287edb: 41 b9 20 00 00 00            	movl	$0x20, %r9d
  287ee1: 41 b8 0a 00 00 00            	movl	$0xa, %r8d
  287ee7: 31 c9                        	xorl	%ecx, %ecx
  287ee9: 48 89 ee                     	movq	%rbp, %rsi
  287eec: 48 89 df                     	movq	%rbx, %rdi
  287eef: e8 1c 26 da ff               	callq	0x2a510 <_ZNK7QString3argExii5QChar@plt>
  287ef4: e8 37 da f5 ff               	callq	0x1e5930 <_ZN5QListI8QVariantED2Ev+0x4f0>
  287ef9: ba 04 00 00 00               	movl	$0x4, %edx
  287efe: 48 89 de                     	movq	%rbx, %rsi
  287f01: 48 89 c7                     	movq	%rax, %rdi
  287f04: e8 57 db f5 ff               	callq	0x1e5a60 <_ZN5QListI8QVariantED2Ev+0x620>
  287f09: 48 89 df                     	movq	%rbx, %rdi
  287f0c: e8 af 02 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  287f11: 48 89 ef                     	movq	%rbp, %rdi
  287f14: e8 a7 02 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  287f19: 48 89 e7                     	movq	%rsp, %rdi
  287f1c: e8 9f 02 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  287f21: 45 89 75 1c                  	movl	%r14d, 0x1c(%r13)
  287f25: be 01 00 00 00               	movl	$0x1, %esi
  287f2a: 48 8b 3d cf 16 36 00         	movq	0x3616cf(%rip), %rdi    # 0x5e9600 <_ZN23QDBusPendingCallWatcher16staticMetaObjectE+0x23ee0>
  287f31: 48 8b 07                     	movq	(%rdi), %rax
  287f34: ff 50 68                     	callq	*0x68(%rax)
  287f37: 48 89 c5                     	movq	%rax, %rbp
  287f3a: 48 85 c0                     	testq	%rax, %rax
  287f3d: 74 50                        	je	0x287f8f <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x6268f>
  287f3f: 41 80 7d 20 00               	cmpb	$0x0, 0x20(%r13)
  287f44: 74 49                        	je	0x287f8f <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x6268f>
  287f46: 41 83 fe 05                  	cmpl	$0x5, %r14d
  287f4a: 0f 84 88 00 00 00            	je	0x287fd8 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x626d8>
  287f50: 48 8d 1d 39 14 00 00         	leaq	0x1439(%rip), %rbx      # 0x289390 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x63a90>
  287f57: be 1e 00 00 00               	movl	$0x1e, %esi
  287f5c: 48 89 ef                     	movq	%rbp, %rdi
  287f5f: e8 4c 13 f0 ff               	callq	0x1892b0 <_ZN5QListI7QStringE6appendERKS0_+0x5b10>
  287f64: 48 8b 10                     	movq	(%rax), %rdx
  287f67: 48 8b 92 10 01 00 00         	movq	0x110(%rdx), %rdx
  287f6e: 48 39 da                     	cmpq	%rbx, %rdx
  287f71: 75 55                        	jne	0x287fc8 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x626c8>
  287f73: be 20 00 00 00               	movl	$0x20, %esi
  287f78: 48 89 ef                     	movq	%rbp, %rdi
  287f7b: e8 30 13 f0 ff               	callq	0x1892b0 <_ZN5QListI7QStringE6appendERKS0_+0x5b10>
  287f80: 48 8b 10                     	movq	(%rax), %rdx
  287f83: 48 8b 92 10 01 00 00         	movq	0x110(%rdx), %rdx
  287f8a: 48 39 da                     	cmpq	%rbx, %rdx
  287f8d: 75 29                        	jne	0x287fb8 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x626b8>
  287f8f: 48 8b 44 24 28               	movq	0x28(%rsp), %rax
  287f94: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
  287f9d: 0f 85 94 00 00 00            	jne	0x288037 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62737>
  287fa3: 48 83 c4 38                  	addq	$0x38, %rsp
  287fa7: 5b                           	popq	%rbx
  287fa8: 5d                           	popq	%rbp
  287fa9: 41 5c                        	popq	%r12
  287fab: 41 5d                        	popq	%r13
  287fad: 41 5e                        	popq	%r14
  287faf: 41 5f                        	popq	%r15
  287fb1: c3                           	retq
  287fb2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
  287fb8: 44 89 f6                     	movl	%r14d, %esi
  287fbb: 48 89 c7                     	movq	%rax, %rdi
  287fbe: ff d2                        	callq	*%rdx
  287fc0: eb cd                        	jmp	0x287f8f <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x6268f>
  287fc2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
  287fc8: 44 89 f6                     	movl	%r14d, %esi
  287fcb: 48 89 c7                     	movq	%rax, %rdi
  287fce: ff d2                        	callq	*%rdx
  287fd0: eb a1                        	jmp	0x287f73 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62673>
  287fd2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
  287fd8: be 23 00 00 00               	movl	$0x23, %esi
  287fdd: 48 89 c7                     	movq	%rax, %rdi
  287fe0: e8 cb 12 f0 ff               	callq	0x1892b0 <_ZN5QListI7QStringE6appendERKS0_+0x5b10>
  287fe5: 48 8d 0d f4 d4 33 00         	leaq	0x33d4f4(%rip), %rcx    # 0x5c54e0 <_ZN9QListData11shared_nullE>
  287fec: 48 89 df                     	movq	%rbx, %rdi
  287fef: 48 8b 40 60                  	movq	0x60(%rax), %rax
  287ff3: 48 8b 50 48                  	movq	0x48(%rax), %rdx
  287ff7: 48 89 48 48                  	movq	%rcx, 0x48(%rax)
  287ffb: 48 89 54 24 20               	movq	%rdx, 0x20(%rsp)
  288000: e8 bb b5 ef ff               	callq	0x1835c0 <_ZN5QListI7QStringED2Ev+0xb380>
  288005: 48 89 ef                     	movq	%rbp, %rdi
  288008: be 23 00 00 00               	movl	$0x23, %esi
  28800d: e8 9e 12 f0 ff               	callq	0x1892b0 <_ZN5QListI7QStringE6appendERKS0_+0x5b10>
  288012: 48 8d 0d c7 d4 33 00         	leaq	0x33d4c7(%rip), %rcx    # 0x5c54e0 <_ZN9QListData11shared_nullE>
  288019: 48 89 df                     	movq	%rbx, %rdi
  28801c: 48 8b 40 60                  	movq	0x60(%rax), %rax
  288020: 48 8b 50 58                  	movq	0x58(%rax), %rdx
  288024: 48 89 48 58                  	movq	%rcx, 0x58(%rax)
  288028: 48 89 54 24 20               	movq	%rdx, 0x20(%rsp)
  28802d: e8 8e b5 ef ff               	callq	0x1835c0 <_ZN5QListI7QStringED2Ev+0xb380>
  288032: e9 19 ff ff ff               	jmp	0x287f50 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62650>
  288037: e8 34 30 da ff               	callq	0x2b070 <__stack_chk_fail@plt>
  28803c: 49 89 c4                     	movq	%rax, %r12
  28803f: 48 89 df                     	movq	%rbx, %rdi
  288042: e8 79 01 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  288047: 4c 89 e3                     	movq	%r12, %rbx
  28804a: 48 89 ef                     	movq	%rbp, %rdi
  28804d: e8 6e 01 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  288052: 4c 89 ff                     	movq	%r15, %rdi
  288055: e8 66 01 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  28805a: 48 89 df                     	movq	%rbx, %rdi
  28805d: e8 de 3a da ff               	callq	0x2bb40 <_Unwind_Resume@plt>
  288062: 48 89 c3                     	movq	%rax, %rbx
  288065: eb e3                        	jmp	0x28804a <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x6274a>
  288067: 48 89 c3                     	movq	%rax, %rbx
  28806a: eb e6                        	jmp	0x288052 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62752>
  28806c: 0f 1f 40 00                  	nopl	(%rax)
