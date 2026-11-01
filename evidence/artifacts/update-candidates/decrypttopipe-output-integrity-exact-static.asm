# Stock DecryptToPIPE exact-static excerpt
# Canonical member SHA-256: e3110811e83701368e638947e6d8887f59321707e70f6288adf0790090d929c0
# Build ID: 4303e27a93f0acfb308146a5d034dafbffa064d0
# Execution-free; call sites and zero exit do not prove complete output.

work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/share/AppUpgrade/DecryptToPIPE:	file format elf64-x86-64

Disassembly of section .text:

0000000000008020 <.text>:
    8110: 53                           	pushq	%rbx
    8111: 48 83 ec 10                  	subq	$0x10, %rsp
    8115: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    811e: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8123: 31 c0                        	xorl	%eax, %eax
    8125: 83 ff 04                     	cmpl	$0x4, %edi
    8128: 7e 0c                        	jle	0x8136 <.text+0x116>
    812a: 48 8b 46 08                  	movq	0x8(%rsi), %rax
    812e: 48 89 f3                     	movq	%rsi, %rbx
    8131: 80 38 2d                     	cmpb	$0x2d, (%rax)
    8134: 74 18                        	je	0x814e <.text+0x12e>
    8136: 31 c0                        	xorl	%eax, %eax
    8138: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    813d: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    8146: 75 4a                        	jne	0x8192 <.text+0x172>
    8148: 48 83 c4 10                  	addq	$0x10, %rsp
    814c: 5b                           	popq	%rbx
    814d: c3                           	retq
    814e: 0f b6 50 01                  	movzbl	0x1(%rax), %edx
    8152: 80 fa 64                     	cmpb	$0x64, %dl
    8155: 75 34                        	jne	0x818b <.text+0x16b>
    8157: 80 78 02 00                  	cmpb	$0x0, 0x2(%rax)
    815b: 75 d9                        	jne	0x8136 <.text+0x116>
    815d: 48 8b 7b 10                  	movq	0x10(%rbx), %rdi
    8161: 48 8d 35 18 ff 27 00         	leaq	0x27ff18(%rip), %rsi    # 0x288080 <__bss_start+0x38>
    8168: e8 e3 1c 00 00               	callq	0x9e50 <.text+0x1e30>
    816d: 48 8b 7b 20                  	movq	0x20(%rbx), %rdi
    8171: e8 fa 02 00 00               	callq	0x8470 <.text+0x450>
    8176: 48 8d 15 f3 fe 27 00         	leaq	0x27fef3(%rip), %rdx    # 0x288070 <__bss_start+0x28>
    817d: 48 8b 7b 18                  	movq	0x18(%rbx), %rdi
    8181: 48 89 02                     	movq	%rax, (%rdx)
    8184: e8 47 01 00 00               	callq	0x82d0 <.text+0x2b0>
    8189: eb ab                        	jmp	0x8136 <.text+0x116>
    818b: 80 fa 44                     	cmpb	$0x44, %dl
    818e: 75 a6                        	jne	0x8136 <.text+0x116>
    8190: eb c5                        	jmp	0x8157 <.text+0x137>
    8192: e8 49 fd ff ff               	callq	0x7ee0 <__stack_chk_fail@plt>

work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/share/AppUpgrade/DecryptToPIPE:	file format elf64-x86-64

Disassembly of section .text:

0000000000008020 <.text>:
    82d0: 41 57                        	pushq	%r15
    82d2: b9 40 00 00 00               	movl	$0x40, %ecx
    82d7: 41 56                        	pushq	%r14
    82d9: 41 55                        	pushq	%r13
    82db: 41 54                        	pushq	%r12
    82dd: 49 89 fc                     	movq	%rdi, %r12
    82e0: 55                           	pushq	%rbp
    82e1: 53                           	pushq	%rbx
    82e2: 48 81 ec 28 02 00 00         	subq	$0x228, %rsp            # imm = 0x228
    82e9: 48 8d 35 90 fd 27 00         	leaq	0x27fd90(%rip), %rsi    # 0x288080 <__bss_start+0x38>
    82f0: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    82f9: 48 89 84 24 18 02 00 00      	movq	%rax, 0x218(%rsp)
    8301: 31 c0                        	xorl	%eax, %eax
    8303: 48 8d 5c 24 10               	leaq	0x10(%rsp), %rbx
    8308: c7 44 24 0c 00 00 00 00      	movl	$0x0, 0xc(%rsp)
    8310: 48 8d 54 24 0c               	leaq	0xc(%rsp), %rdx
    8315: 48 89 df                     	movq	%rbx, %rdi
    8318: f3 48 ab                     	rep		stosq	%rax, %es:(%rdi)
    831b: 48 8d 05 4e fd 27 00         	leaq	0x27fd4e(%rip), %rax    # 0x288070 <__bss_start+0x28>
    8322: 4c 89 e7                     	movq	%r12, %rdi
    8325: 48 8b 28                     	movq	(%rax), %rbp
    8328: e8 53 0d 00 00               	callq	0x9080 <.text+0x1060>
    832d: 49 89 c5                     	movq	%rax, %r13
    8330: 8b 44 24 0c                  	movl	0xc(%rsp), %eax
    8334: 3d 6c fe ff ff               	cmpl	$0xfffffe6c, %eax       # imm = 0xFFFFFE6C
    8339: 0f 84 b1 00 00 00            	je	0x83f0 <.text+0x3d0>
    833f: 85 c0                        	testl	%eax, %eax
    8341: 75 7d                        	jne	0x83c0 <.text+0x3a0>
    8343: ba 02 00 00 00               	movl	$0x2, %edx
    8348: 31 f6                        	xorl	%esi, %esi
    834a: 4c 89 ef                     	movq	%r13, %rdi
    834d: e8 0e 0c 00 00               	callq	0x8f60 <.text+0xf40>
    8352: 31 d2                        	xorl	%edx, %edx
    8354: 48 89 ee                     	movq	%rbp, %rsi
    8357: 4c 89 ef                     	movq	%r13, %rdi
    835a: 49 89 c7                     	movq	%rax, %r15
    835d: 49 89 ec                     	movq	%rbp, %r12
    8360: e8 fb 0b 00 00               	callq	0x8f60 <.text+0xf40>
    8365: eb 29                        	jmp	0x8390 <.text+0x370>
    8367: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    8370: 48 89 c2                     	movq	%rax, %rdx
    8373: 48 89 de                     	movq	%rbx, %rsi
    8376: bf 01 00 00 00               	movl	$0x1, %edi
    837b: e8 50 fc ff ff               	callq	0x7fd0 <write@plt>
    8380: 48 85 c0                     	testq	%rax, %rax
    8383: 78 33                        	js	0x83b8 <.text+0x398>
    8385: 4c 01 f5                     	addq	%r14, %rbp
    8388: 4d 01 f4                     	addq	%r14, %r12
    838b: 49 39 ef                     	cmpq	%rbp, %r15
    838e: 7e 28                        	jle	0x83b8 <.text+0x398>
    8390: 31 c0                        	xorl	%eax, %eax
    8392: b9 40 00 00 00               	movl	$0x40, %ecx
    8397: 48 89 df                     	movq	%rbx, %rdi
    839a: f3 48 ab                     	rep		stosq	%rax, %es:(%rdi)
    839d: 48 89 da                     	movq	%rbx, %rdx
    83a0: b9 00 02 00 00               	movl	$0x200, %ecx            # imm = 0x200
    83a5: 4c 89 e6                     	movq	%r12, %rsi
    83a8: 4c 89 ef                     	movq	%r13, %rdi
    83ab: e8 a0 11 00 00               	callq	0x9550 <.text+0x1530>
    83b0: 49 89 c6                     	movq	%rax, %r14
    83b3: 48 85 c0                     	testq	%rax, %rax
    83b6: 7f b8                        	jg	0x8370 <.text+0x350>
    83b8: 4c 89 ef                     	movq	%r13, %rdi
    83bb: e8 90 19 00 00               	callq	0x9d50 <.text+0x1d30>
    83c0: 31 c0                        	xorl	%eax, %eax
    83c2: 48 8b b4 24 18 02 00 00      	movq	0x218(%rsp), %rsi
    83ca: 64 48 33 34 25 28 00 00 00   	xorq	%fs:0x28, %rsi
    83d3: 0f 85 83 00 00 00            	jne	0x845c <.text+0x43c>
    83d9: 48 81 c4 28 02 00 00         	addq	$0x228, %rsp            # imm = 0x228
    83e0: 5b                           	popq	%rbx
    83e1: 5d                           	popq	%rbp
    83e2: 41 5c                        	popq	%r12
    83e4: 41 5d                        	popq	%r13
    83e6: 41 5e                        	popq	%r14
    83e8: 41 5f                        	popq	%r15
    83ea: c3                           	retq
    83eb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    83f0: 48 8d 35 cd 36 05 00         	leaq	0x536cd(%rip), %rsi     # 0x5bac4
    83f7: 4c 89 e7                     	movq	%r12, %rdi
    83fa: e8 a1 fb ff ff               	callq	0x7fa0 <fopen64@plt>
    83ff: 49 89 c4                     	movq	%rax, %r12
    8402: 48 85 c0                     	testq	%rax, %rax
    8405: 74 b9                        	je	0x83c0 <.text+0x3a0>
    8407: 31 d2                        	xorl	%edx, %edx
    8409: 48 89 ee                     	movq	%rbp, %rsi
    840c: 48 89 c7                     	movq	%rax, %rdi
    840f: e8 6c f9 ff ff               	callq	0x7d80 <fseek@plt>
    8414: eb 1f                        	jmp	0x8435 <.text+0x415>
    8416: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    8420: 48 89 c2                     	movq	%rax, %rdx
    8423: 48 89 de                     	movq	%rbx, %rsi
    8426: bf 01 00 00 00               	movl	$0x1, %edi
    842b: e8 a0 fb ff ff               	callq	0x7fd0 <write@plt>
    8430: 48 85 c0                     	testq	%rax, %rax
    8433: 78 1a                        	js	0x844f <.text+0x42f>
    8435: 4c 89 e1                     	movq	%r12, %rcx
    8438: ba 00 02 00 00               	movl	$0x200, %edx            # imm = 0x200
    843d: be 01 00 00 00               	movl	$0x1, %esi
    8442: 48 89 df                     	movq	%rbx, %rdi
    8445: e8 76 fa ff ff               	callq	0x7ec0 <fread@plt>
    844a: 48 85 c0                     	testq	%rax, %rax
    844d: 7f d1                        	jg	0x8420 <.text+0x400>
    844f: 4c 89 e7                     	movq	%r12, %rdi
    8452: e8 e9 fa ff ff               	callq	0x7f40 <fclose@plt>
    8457: e9 64 ff ff ff               	jmp	0x83c0 <.text+0x3a0>
    845c: e8 7f fa ff ff               	callq	0x7ee0 <__stack_chk_fail@plt>

work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/share/AppUpgrade/DecryptToPIPE:	file format elf64-x86-64

Disassembly of section .text:

0000000000008020 <.text>:
    8470: 53                           	pushq	%rbx
    8471: 48 89 fb                     	movq	%rdi, %rbx
    8474: 48 83 ec 10                  	subq	$0x10, %rsp
    8478: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8481: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8486: 31 c0                        	xorl	%eax, %eax
    8488: e8 63 f9 ff ff               	callq	0x7df0 <strlen@plt>
    848d: 83 e8 01                     	subl	$0x1, %eax
    8490: 78 54                        	js	0x84e6 <.text+0x4c6>
    8492: 48 63 f8                     	movslq	%eax, %rdi
    8495: 89 c0                        	movl	%eax, %eax
    8497: b9 01 00 00 00               	movl	$0x1, %ecx
    849c: 48 8d 34 3b                  	leaq	(%rbx,%rdi), %rsi
    84a0: 48 83 ef 01                  	subq	$0x1, %rdi
    84a4: 48 29 c7                     	subq	%rax, %rdi
    84a7: 31 c0                        	xorl	%eax, %eax
    84a9: 48 01 df                     	addq	%rbx, %rdi
    84ac: 0f 1f 40 00                  	nopl	(%rax)
    84b0: 0f be 16                     	movsbl	(%rsi), %edx
    84b3: 48 83 ee 01                  	subq	$0x1, %rsi
    84b7: 83 ea 30                     	subl	$0x30, %edx
    84ba: 48 63 d2                     	movslq	%edx, %rdx
    84bd: 48 0f af d1                  	imulq	%rcx, %rdx
    84c1: 48 8d 0c 89                  	leaq	(%rcx,%rcx,4), %rcx
    84c5: 48 01 c9                     	addq	%rcx, %rcx
    84c8: 48 01 d0                     	addq	%rdx, %rax
    84cb: 48 39 fe                     	cmpq	%rdi, %rsi
    84ce: 75 e0                        	jne	0x84b0 <.text+0x490>
    84d0: 48 8b 5c 24 08               	movq	0x8(%rsp), %rbx
    84d5: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
    84de: 75 0a                        	jne	0x84ea <.text+0x4ca>
    84e0: 48 83 c4 10                  	addq	$0x10, %rsp
    84e4: 5b                           	popq	%rbx
    84e5: c3                           	retq
    84e6: 31 c0                        	xorl	%eax, %eax
    84e8: eb e6                        	jmp	0x84d0 <.text+0x4b0>
    84ea: e8 f1 f9 ff ff               	callq	0x7ee0 <__stack_chk_fail@plt>

work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/share/AppUpgrade/DecryptToPIPE:	file format elf64-x86-64

Disassembly of section .text:

0000000000008020 <.text>:
    9080: 41 57                        	pushq	%r15
    9082: 49 89 f7                     	movq	%rsi, %r15
    9085: 41 56                        	pushq	%r14
    9087: 48 8d 35 36 2a 05 00         	leaq	0x52a36(%rip), %rsi     # 0x5bac4
    908e: 49 89 d6                     	movq	%rdx, %r14
    9091: 41 55                        	pushq	%r13
    9093: 41 54                        	pushq	%r12
    9095: 49 89 fc                     	movq	%rdi, %r12
    9098: 55                           	pushq	%rbp
    9099: 53                           	pushq	%rbx
    909a: 48 81 ec d8 02 00 00         	subq	$0x2d8, %rsp            # imm = 0x2D8
    90a1: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    90aa: 48 89 84 24 c8 02 00 00      	movq	%rax, 0x2c8(%rsp)
    90b2: 31 c0                        	xorl	%eax, %eax
    90b4: 48 c7 84 24 90 00 00 00 00 00 00 00  	movq	$0x0, 0x90(%rsp)
    90c0: 48 c7 84 24 98 00 00 00 00 00 00 00  	movq	$0x0, 0x98(%rsp)
    90cc: e8 cf ee ff ff               	callq	0x7fa0 <fopen64@plt>
    90d1: 48 85 c0                     	testq	%rax, %rax
    90d4: 0f 84 f6 03 00 00            	je	0x94d0 <.text+0x14b0>
    90da: 48 89 c7                     	movq	%rax, %rdi
    90dd: ba 02 00 00 00               	movl	$0x2, %edx
    90e2: 31 f6                        	xorl	%esi, %esi
    90e4: 48 89 c3                     	movq	%rax, %rbx
    90e7: e8 34 ec ff ff               	callq	0x7d20 <fseeko64@plt>
    90ec: 48 89 df                     	movq	%rbx, %rdi
    90ef: 85 c0                        	testl	%eax, %eax
    90f1: 0f 85 d4 00 00 00            	jne	0x91cb <.text+0x11ab>
    90f7: e8 e4 ee ff ff               	callq	0x7fe0 <ftello64@plt>
    90fc: 48 85 c0                     	testq	%rax, %rax
    90ff: 0f 8e db 03 00 00            	jle	0x94e0 <.text+0x14c0>
    9105: 48 3d 24 40 00 00            	cmpq	$0x4024, %rax           # imm = 0x4024
    910b: 7e 71                        	jle	0x917e <.text+0x115e>
    910d: 48 8d b0 dc bf ff ff         	leaq	-0x4024(%rax), %rsi
    9114: 48 89 df                     	movq	%rbx, %rdi
    9117: 31 d2                        	xorl	%edx, %edx
    9119: e8 02 ec ff ff               	callq	0x7d20 <fseeko64@plt>
    911e: 48 89 df                     	movq	%rbx, %rdi
    9121: 85 c0                        	testl	%eax, %eax
    9123: 0f 85 a2 00 00 00            	jne	0x91cb <.text+0x11ab>
    9129: e8 b2 ee ff ff               	callq	0x7fe0 <ftello64@plt>
    912e: 49 89 c5                     	movq	%rax, %r13
    9131: 48 85 c0                     	testq	%rax, %rax
    9134: 0f 8e a6 03 00 00            	jle	0x94e0 <.text+0x14c0>
    913a: be 01 00 00 00               	movl	$0x1, %esi
    913f: bf 24 40 00 00               	movl	$0x4024, %edi           # imm = 0x4024
    9144: e8 e7 ed ff ff               	callq	0x7f30 <calloc@plt>
    9149: 48 89 c5                     	movq	%rax, %rbp
    914c: 48 85 c0                     	testq	%rax, %rax
    914f: 0f 84 ae 03 00 00            	je	0x9503 <.text+0x14e3>
    9155: 48 89 d9                     	movq	%rbx, %rcx
    9158: ba 01 00 00 00               	movl	$0x1, %edx
    915d: be 24 40 00 00               	movl	$0x4024, %esi           # imm = 0x4024
    9162: 48 89 c7                     	movq	%rax, %rdi
    9165: e8 56 ed ff ff               	callq	0x7ec0 <fread@plt>
    916a: 48 83 f8 01                  	cmpq	$0x1, %rax
    916e: 75 50                        	jne	0x91c0 <.text+0x11a0>
    9170: 80 7d 00 54                  	cmpb	$0x54, (%rbp)
    9174: 74 6a                        	je	0x91e0 <.text+0x11c0>
    9176: 48 89 ef                     	movq	%rbp, %rdi
    9179: e8 62 ec ff ff               	callq	0x7de0 <free@plt>
    917e: 48 89 df                     	movq	%rbx, %rdi
    9181: e8 ba ed ff ff               	callq	0x7f40 <fclose@plt>
    9186: 41 c7 06 6c fe ff ff         	movl	$0xfffffe6c, (%r14)     # imm = 0xFFFFFE6C
    918d: 31 c0                        	xorl	%eax, %eax
    918f: 48 8b 8c 24 c8 02 00 00      	movq	0x2c8(%rsp), %rcx
    9197: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    91a0: 0f 85 a3 03 00 00            	jne	0x9549 <.text+0x1529>
    91a6: 48 81 c4 d8 02 00 00         	addq	$0x2d8, %rsp            # imm = 0x2D8
    91ad: 5b                           	popq	%rbx
    91ae: 5d                           	popq	%rbp
    91af: 41 5c                        	popq	%r12
    91b1: 41 5d                        	popq	%r13
    91b3: 41 5e                        	popq	%r14
    91b5: 41 5f                        	popq	%r15
    91b7: c3                           	retq
    91b8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    91c0: 48 89 ef                     	movq	%rbp, %rdi
    91c3: e8 18 ec ff ff               	callq	0x7de0 <free@plt>
    91c8: 48 89 df                     	movq	%rbx, %rdi
    91cb: e8 70 ed ff ff               	callq	0x7f40 <fclose@plt>
    91d0: 41 c7 06 6e fe ff ff         	movl	$0xfffffe6e, (%r14)     # imm = 0xFFFFFE6E
    91d7: 31 c0                        	xorl	%eax, %eax
    91d9: eb b4                        	jmp	0x918f <.text+0x116f>
    91db: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    91e0: 80 7d 01 45                  	cmpb	$0x45, 0x1(%rbp)
    91e4: 75 90                        	jne	0x9176 <.text+0x1156>
    91e6: 0f b6 45 02                  	movzbl	0x2(%rbp), %eax
    91ea: 3c 52                        	cmpb	$0x52, %al
    91ec: 0f 84 04 03 00 00            	je	0x94f6 <.text+0x14d6>
    91f2: c7 44 24 14 03 00 00 00      	movl	$0x3, 0x14(%rsp)
    91fa: 3c 32                        	cmpb	$0x32, %al
    91fc: 0f 85 74 ff ff ff            	jne	0x9176 <.text+0x1156>
