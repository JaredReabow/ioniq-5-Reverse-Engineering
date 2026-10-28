
work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/ApplicationManager:	file format elf64-x86-64

Disassembly of section .text:

0000000000225900 <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE>:
  27dde0: 55                           	pushq	%rbp
  27dde1: 48 89 e5                     	movq	%rsp, %rbp
  27dde4: 41 57                        	pushq	%r15
  27dde6: 49 89 ff                     	movq	%rdi, %r15
  27dde9: 41 56                        	pushq	%r14
  27ddeb: 4c 8d 75 80                  	leaq	-0x80(%rbp), %r14
  27ddef: 41 55                        	pushq	%r13
  27ddf1: 4c 89 f7                     	movq	%r14, %rdi
  27ddf4: 41 54                        	pushq	%r12
  27ddf6: 53                           	pushq	%rbx
  27ddf7: 48 83 ec 68                  	subq	$0x68, %rsp
  27ddfb: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
  27de04: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
  27de08: 31 c0                        	xorl	%eax, %eax
  27de0a: e8 e1 d7 da ff               	callq	0x2b5f0 <_ZN15QDBusConnection10sessionBusEv@plt>
  27de0f: be 10 00 00 00               	movl	$0x10, %esi
  27de14: 48 8d 3d 65 c4 09 00         	leaq	0x9c465(%rip), %rdi     # 0x31a280
  27de1b: e8 80 ca da ff               	callq	0x2a8a0 <_ZN7QString16fromAscii_helperEPKci@plt>
  27de20: be 21 00 00 00               	movl	$0x21, %esi
  27de25: 48 89 45 c0                  	movq	%rax, -0x40(%rbp)
  27de29: 48 8d 3d 88 d3 09 00         	leaq	0x9d388(%rip), %rdi     # 0x31b1b8
  27de30: e8 6b ca da ff               	callq	0x2a8a0 <_ZN7QString16fromAscii_helperEPKci@plt>
  27de35: 48 89 45 b0                  	movq	%rax, -0x50(%rbp)
  27de39: 48 83 ec 08                  	subq	$0x8, %rsp
  27de3d: 4d 89 f9                     	movq	%r15, %r9
  27de40: 4c 89 f7                     	movq	%r14, %rdi
  27de43: 48 8d 05 b6 76 34 00         	leaq	0x3476b6(%rip), %rax    # 0x5c5500 <_ZN10QArrayData11shared_nullE>
  27de4a: 48 8d 0d 40 c4 09 00         	leaq	0x9c440(%rip), %rcx     # 0x31a291
  27de51: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
  27de55: 48 89 45 90                  	movq	%rax, -0x70(%rbp)
  27de59: 48 8d 5d c0                  	leaq	-0x40(%rbp), %rbx
  27de5d: 48 8d 45 b0                  	leaq	-0x50(%rbp), %rax
  27de61: 51                           	pushq	%rcx
  27de62: 49 89 d8                     	movq	%rbx, %r8
  27de65: 4c 8d 65 a0                  	leaq	-0x60(%rbp), %r12
  27de69: 48 89 c1                     	movq	%rax, %rcx
  27de6c: 48 89 85 78 ff ff ff         	movq	%rax, -0x88(%rbp)
  27de73: 4c 8d 6d 90                  	leaq	-0x70(%rbp), %r13
  27de77: 4c 89 e2                     	movq	%r12, %rdx
  27de7a: 4c 89 ee                     	movq	%r13, %rsi
  27de7d: e8 8e ce da ff               	callq	0x2ad10 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
  27de82: 59                           	popq	%rcx
  27de83: 4c 89 ef                     	movq	%r13, %rdi
  27de86: 88 85 77 ff ff ff            	movb	%al, -0x89(%rbp)
  27de8c: 5e                           	popq	%rsi
  27de8d: e8 2e a3 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  27de92: 4c 89 e7                     	movq	%r12, %rdi
  27de95: e8 26 a3 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  27de9a: 48 8b bd 78 ff ff ff         	movq	-0x88(%rbp), %rdi
  27dea1: e8 1a a3 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  27dea6: 48 89 df                     	movq	%rbx, %rdi
  27dea9: e8 12 a3 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  27deae: 0f b6 85 77 ff ff ff         	movzbl	-0x89(%rbp), %eax
  27deb5: 84 c0                        	testb	%al, %al
  27deb7: 75 32                        	jne	0x27deeb <_ZNK8QMapNodeI7QStringiE4copyEP8QMapDataIS0_iE+0x585eb>
  27deb9: 48 8d 3d 20 d3 09 00         	leaq	0x9d320(%rip), %rdi     # 0x31b1e0
  27dec0: be 5b 00 00 00               	movl	$0x5b, %esi
  27dec5: e8 d6 c9 da ff               	callq	0x2a8a0 <_ZN7QString16fromAscii_helperEPKci@plt>
  27deca: 48 89 45 c0                  	movq	%rax, -0x40(%rbp)
  27dece: e8 5d 7a f6 ff               	callq	0x1e5930 <_ZN5QListI8QVariantED2Ev+0x4f0>
  27ded3: ba 02 00 00 00               	movl	$0x2, %edx
  27ded8: 48 89 de                     	movq	%rbx, %rsi
  27dedb: 48 89 c7                     	movq	%rax, %rdi
  27dede: e8 7d 7b f6 ff               	callq	0x1e5a60 <_ZN5QListI8QVariantED2Ev+0x620>
  27dee3: 48 89 df                     	movq	%rbx, %rdi
  27dee6: e8 d5 a2 ef ff               	callq	0x1781c0 <.text+0x14c2c0>
  27deeb: 48 8d 3d b8 c3 09 00         	leaq	0x9c3b8(%rip), %rdi     # 0x31a2aa
  27def2: be 0d 00 00 00               	movl	$0xd, %esi
  27def7: e8 a4 c9 da ff               	callq	0x2a8a0 <_ZN7QString16fromAscii_helperEPKci@plt>
  27defc: be 1c 00 00 00               	movl	$0x1c, %esi
  27df01: 48 89 45 c0                  	movq	%rax, -0x40(%rbp)
  27df05: 48 8d 3d ac c3 09 00         	leaq	0x9c3ac(%rip), %rdi     # 0x31a2b8
  27df0c: e8 8f c9 da ff               	callq	0x2a8a0 <_ZN7QString16fromAscii_helperEPKci@plt>
  27df11: 48 8b 8d 78 ff ff ff         	movq	-0x88(%rbp), %rcx
  27df18: 4d 89 f9                     	movq	%r15, %r9
  27df1b: 49 89 d8                     	movq	%rbx, %r8
  27df1e: 4c 89 e2                     	movq	%r12, %rdx
  27df21: 48 89 45 b0                  	movq	%rax, -0x50(%rbp)
  27df25: 48 83 ec 08                  	subq	$0x8, %rsp
  27df29: 4c 89 ee                     	movq	%r13, %rsi
  27df2c: 4c 89 f7                     	movq	%r14, %rdi
  27df2f: 48 8d 05 ca 75 34 00         	leaq	0x3475ca(%rip), %rax    # 0x5c5500 <_ZN10QArrayData11shared_nullE>
  27df36: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
  27df3a: 48 89 45 90                  	movq	%rax, -0x70(%rbp)
  27df3e: 48 8d 05 fb d2 09 00         	leaq	0x9d2fb(%rip), %rax     # 0x31b240
  27df45: 50                           	pushq	%rax
  27df46: e8 c5 cd da ff               	callq	0x2ad10 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
  27df4b: 41 89 c7                     	movl	%eax, %r15d
  27df4e: 58                           	popq	%rax
  27df4f: 4c 89 ef                     	movq	%r13, %rdi
