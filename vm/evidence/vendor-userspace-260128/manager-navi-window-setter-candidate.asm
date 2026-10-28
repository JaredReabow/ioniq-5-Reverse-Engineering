
work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/ApplicationManager:	file format elf64-x86-64

Disassembly of section .text:

0000000000225900 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE>:
  288070: 41 55                        	pushq	%r13
  288072: 41 54                        	pushq	%r12
  288074: 41 89 f4                     	movl	%esi, %r12d
  288077: be 3a 00 00 00               	movl	$0x3a, %esi
  28807c: 55                           	pushq	%rbp
  28807d: 53                           	pushq	%rbx
  28807e: 48 89 fb                     	movq	%rdi, %rbx
  288081: 48 8d 3d a0 46 09 00         	leaq	0x946a0(%rip), %rdi     # 0x31c728
  288088: 48 83 ec 28                  	subq	$0x28, %rsp
  28808c: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
  288095: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
  28809a: 31 c0                        	xorl	%eax, %eax
  28809c: 4c 8d 6c 24 10               	leaq	0x10(%rsp), %r13
  2880a1: 48 89 e5                     	movq	%rsp, %rbp
  2880a4: e8 f7 27 da ff               	callq	0x2a8a0 <_ZN7QString16fromAscii_helperEPKci@plt>
  2880a9: 41 0f b6 d4                  	movzbl	%r12b, %edx
  2880ad: 31 c9                        	xorl	%ecx, %ecx
  2880af: 48 89 e6                     	movq	%rsp, %rsi
  2880b2: 41 b9 20 00 00 00            	movl	$0x20, %r9d
  2880b8: 41 b8 0a 00 00 00            	movl	$0xa, %r8d
  2880be: 4c 89 ef                     	movq	%r13, %rdi
  2880c1: 48 89 04 24                  	movq	%rax, (%rsp)
  2880c5: e8 46 24 da ff               	callq	0x2a510 <_ZNK7QString3argExii5QChar@plt>
  2880ca: e8 61 d8 f5 ff               	callq	0x1e5930 <_ZN5QListI8QVariantED2Ev+0x4f0>
  2880cf: ba 04 00 00 00               	movl	$0x4, %edx
  2880d4: 4c 89 ee                     	movq	%r13, %rsi
  2880d7: 48 89 c7                     	movq	%rax, %rdi
  2880da: e8 81 d9 f5 ff               	callq	0x1e5a60 <_ZN5QListI8QVariantED2Ev+0x620>
  2880df: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
  2880e4: 8b 07                        	movl	(%rdi), %eax
  2880e6: 85 c0                        	testl	%eax, %eax
  2880e8: 75 56                        	jne	0x288140 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62840>
  2880ea: ba 08 00 00 00               	movl	$0x8, %edx
  2880ef: be 02 00 00 00               	movl	$0x2, %esi
  2880f4: e8 d7 36 da ff               	callq	0x2b7d0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  2880f9: 48 8b 3c 24                  	movq	(%rsp), %rdi
  2880fd: 8b 07                        	movl	(%rdi), %eax
  2880ff: 85 c0                        	testl	%eax, %eax
  288101: 75 5d                        	jne	0x288160 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62860>
  288103: ba 08 00 00 00               	movl	$0x8, %edx
  288108: be 02 00 00 00               	movl	$0x2, %esi
  28810d: e8 be 36 da ff               	callq	0x2b7d0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  288112: 8b 73 1c                     	movl	0x1c(%rbx), %esi
  288115: 44 88 63 20                  	movb	%r12b, 0x20(%rbx)
  288119: 48 89 df                     	movq	%rbx, %rdi
  28811c: e8 4f fd ff ff               	callq	0x287e70 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62570>
  288121: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
  288126: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
  28812f: 75 45                        	jne	0x288176 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62876>
  288131: 48 83 c4 28                  	addq	$0x28, %rsp
  288135: 5b                           	popq	%rbx
  288136: 5d                           	popq	%rbp
  288137: 41 5c                        	popq	%r12
  288139: 41 5d                        	popq	%r13
  28813b: c3                           	retq
  28813c: 0f 1f 40 00                  	nopl	(%rax)
  288140: 83 f8 ff                     	cmpl	$-0x1, %eax
  288143: 74 b4                        	je	0x2880f9 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x627f9>
  288145: f0                           	lock
  288146: 83 2f 01                     	subl	$0x1, (%rdi)
  288149: 0f 95 c0                     	setne	%al
  28814c: 84 c0                        	testb	%al, %al
  28814e: 75 a9                        	jne	0x2880f9 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x627f9>
  288150: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
  288155: eb 93                        	jmp	0x2880ea <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x627ea>
  288157: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
  288160: 83 f8 ff                     	cmpl	$-0x1, %eax
  288163: 74 ad                        	je	0x288112 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62812>
  288165: f0                           	lock
  288166: 83 2f 01                     	subl	$0x1, (%rdi)
  288169: 0f 95 c0                     	setne	%al
  28816c: 84 c0                        	testb	%al, %al
  28816e: 75 a2                        	jne	0x288112 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62812>
  288170: 48 8b 3c 24                  	movq	(%rsp), %rdi
  288174: eb 8d                        	jmp	0x288103 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62803>
  288176: e8 f5 2e da ff               	callq	0x2b070 <__stack_chk_fail@plt>
  28817b: 4c 89 ef                     	movq	%r13, %rdi
  28817e: 48 89 c3                     	movq	%rax, %rbx
  288181: e8 3a 00 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  288186: 48 89 ef                     	movq	%rbp, %rdi
  288189: e8 32 00 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  28818e: 48 89 df                     	movq	%rbx, %rdi
  288191: e8 aa 39 da ff               	callq	0x2bb40 <_Unwind_Resume@plt>
  288196: 48 89 c3                     	movq	%rax, %rbx
  288199: eb eb                        	jmp	0x288186 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x62886>
  28819b: 90                           	nop
  28819c: 0f 1f 40 00                  	nopl	(%rax)
