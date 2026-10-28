
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

000000000335e920 <NimoExSLScreenLinux::onCreateWindow()>:
 335e920: 55                           	pushq	%rbp
 335e921: 4c 8d 05 0f 97 d5 02         	leaq	0x2d5970f(%rip), %r8    # 0x60b8037 <CPersistenceComm::Initialize()::__func__+0x11af>
 335e928: 48 8d 15 19 9b d5 02         	leaq	0x2d59b19(%rip), %rdx   # 0x60b8448 <NimoExSLScreenLinux::onCreateWindow()::__func__>
 335e92f: 48 8d 35 aa 85 d5 02         	leaq	0x2d585aa(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335e936: b9 57 00 00 00               	movl	$0x57, %ecx
 335e93b: 48 89 e5                     	movq	%rsp, %rbp
 335e93e: 41 57                        	pushq	%r15
 335e940: 41 56                        	pushq	%r14
 335e942: 41 55                        	pushq	%r13
 335e944: 41 54                        	pushq	%r12
 335e946: 53                           	pushq	%rbx
 335e947: 48 89 fb                     	movq	%rdi, %rbx
 335e94a: 48 81 ec d8 00 00 00         	subq	$0xd8, %rsp
 335e951: 44 8b 4f 34                  	movl	0x34(%rdi), %r9d
 335e955: bf 05 00 00 00               	movl	$0x5, %edi
 335e95a: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 335e963: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
 335e967: 31 c0                        	xorl	%eax, %eax
 335e969: e8 c2 13 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335e96e: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 335e972: 41 83 f9 01                  	cmpl	$0x1, %r9d
 335e976: 0f 84 a4 04 00 00            	je	0x335ee20 <NimoExSLScreenLinux::onCreateWindow()+0x500>
 335e97c: 41 8d 41 fe                  	leal	-0x2(%r9), %eax
 335e980: 83 e0 fd                     	andl	$-0x3, %eax
 335e983: 0f 84 8f 00 00 00            	je	0x335ea18 <NimoExSLScreenLinux::onCreateWindow()+0xf8>
 335e989: 41 83 f9 09                  	cmpl	$0x9, %r9d
 335e98d: 0f 84 25 09 00 00            	je	0x335f2b8 <NimoExSLScreenLinux::onCreateWindow()+0x998>
 335e993: 41 83 f9 0d                  	cmpl	$0xd, %r9d
 335e997: 76 57                        	jbe	0x335e9f0 <NimoExSLScreenLinux::onCreateWindow()+0xd0>
 335e999: 4c 8d 05 1b 97 d5 02         	leaq	0x2d5971b(%rip), %r8    # 0x60b80bb <CPersistenceComm::Initialize()::__func__+0x1233>
 335e9a0: 48 8d 15 a1 9a d5 02         	leaq	0x2d59aa1(%rip), %rdx   # 0x60b8448 <NimoExSLScreenLinux::onCreateWindow()::__func__>
 335e9a7: 48 8d 35 32 85 d5 02         	leaq	0x2d58532(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335e9ae: 31 c0                        	xorl	%eax, %eax
 335e9b0: b9 af 00 00 00               	movl	$0xaf, %ecx
 335e9b5: bf 05 00 00 00               	movl	$0x5, %edi
 335e9ba: e8 71 13 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335e9bf: b8 01 00 00 00               	movl	$0x1, %eax
 335e9c4: 48 8b 4d c8                  	movq	-0x38(%rbp), %rcx
 335e9c8: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 335e9d1: 0f 85 4a 11 00 00            	jne	0x335fb21 <NimoExSLScreenLinux::onCreateWindow()+0x1201>
 335e9d7: 48 8d 65 d8                  	leaq	-0x28(%rbp), %rsp
 335e9db: 5b                           	popq	%rbx
 335e9dc: 41 5c                        	popq	%r12
 335e9de: 41 5d                        	popq	%r13
 335e9e0: 41 5e                        	popq	%r14
 335e9e2: 41 5f                        	popq	%r15
 335e9e4: 5d                           	popq	%rbp
 335e9e5: c3                           	retq
 335e9e6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 335e9f0: b8 40 2c 00 00               	movl	$0x2c40, %eax           # imm = 0x2C40
 335e9f5: 4c 0f a3 c8                  	btq	%r9, %rax
 335e9f9: 73 9e                        	jae	0x335e999 <NimoExSLScreenLinux::onCreateWindow()+0x79>
 335e9fb: bf 02 00 00 00               	movl	$0x2, %edi
 335ea00: e8 4b ea e9 ff               	callq	0x31fd450 <ExSLEglFunction::createExSLEglSurface(ExSLEglFunction::ecSurfaceType)>
 335ea05: 48 89 83 88 00 00 00         	movq	%rax, 0x88(%rbx)
 335ea0c: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 335ea10: eb 87                        	jmp	0x335e999 <NimoExSLScreenLinux::onCreateWindow()+0x79>
 335ea12: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 335ea18: 31 f6                        	xorl	%esi, %esi
 335ea1a: 48 89 df                     	movq	%rbx, %rdi
 335ea1d: e8 0e c9 0e fe               	callq	0x144b330 <_ZN12QQuickWindow23setClearBeforeRenderingEb@plt>
 335ea22: bf 38 00 00 00               	movl	$0x38, %edi
 335ea27: e8 04 f4 0e fe               	callq	0x144de30 <_Znwm@plt>
 335ea2c: 48 89 c7                     	movq	%rax, %rdi
 335ea2f: 49 89 c4                     	movq	%rax, %r12
 335ea32: e8 69 c3 0e fe               	callq	0x144ada0 <_ZN13ImageProviderC1Ev@plt>
 335ea37: 48 8d 3d 13 0f a7 02         	leaq	0x2a70f13(%rip), %rdi   # 0x5dcf951 <typeinfo name for NimoExSLMapRenderer+0xf1>
 335ea3e: be 07 00 00 00               	movl	$0x7, %esi
 335ea43: e8 58 f8 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335ea48: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335ea4c: 48 8d 45 a0                  	leaq	-0x60(%rbp), %rax
 335ea50: 48 89 df                     	movq	%rbx, %rdi
 335ea53: 48 89 85 18 ff ff ff         	movq	%rax, -0xe8(%rbp)
 335ea5a: e8 51 f7 0e fe               	callq	0x144e1b0 <_ZNK10QQuickView6engineEv@plt>
 335ea5f: 48 8d 4d a0                  	leaq	-0x60(%rbp), %rcx
 335ea63: 4c 89 e2                     	movq	%r12, %rdx
 335ea66: 48 89 c7                     	movq	%rax, %rdi
 335ea69: 48 89 ce                     	movq	%rcx, %rsi
 335ea6c: 48 89 8d 18 ff ff ff         	movq	%rcx, -0xe8(%rbp)
 335ea73: e8 28 fa 0e fe               	callq	0x144e4a0 <_ZN10QQmlEngine16addImageProviderERK7QStringP21QQmlImageProviderBase@plt>
 335ea78: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335ea7c: 8b 07                        	movl	(%rdi), %eax
 335ea7e: 85 c0                        	testl	%eax, %eax
 335ea80: 0f 84 3a 03 00 00            	je	0x335edc0 <NimoExSLScreenLinux::onCreateWindow()+0x4a0>
 335ea86: 83 f8 ff                     	cmpl	$-0x1, %eax
 335ea89: 74 0f                        	je	0x335ea9a <NimoExSLScreenLinux::onCreateWindow()+0x17a>
 335ea8b: f0                           	lock
 335ea8c: 83 2f 01                     	subl	$0x1, (%rdi)
 335ea8f: 0f 95 c0                     	setne	%al
 335ea92: 84 c0                        	testb	%al, %al
 335ea94: 0f 84 21 03 00 00            	je	0x335edbb <NimoExSLScreenLinux::onCreateWindow()+0x49b>
 335ea9a: 4c 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %r15
 335eaa1: 8b 73 38                     	movl	0x38(%rbx), %esi
 335eaa4: 4c 89 ff                     	movq	%r15, %rdi
 335eaa7: e8 b4 db 0e fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 335eaac: 48 8d 3d 9c 95 d5 02         	leaq	0x2d5959c(%rip), %rdi   # 0x60b804f <CPersistenceComm::Initialize()::__func__+0x11c7>
 335eab3: be 0c 00 00 00               	movl	$0xc, %esi
 335eab8: e8 e3 f7 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335eabd: 48 89 df                     	movq	%rbx, %rdi
 335eac0: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335eac4: 4c 8d 65 80                  	leaq	-0x80(%rbp), %r12
 335eac8: e8 f3 f8 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335eacd: 4c 89 fa                     	movq	%r15, %rdx
 335ead0: 4c 89 e6                     	movq	%r12, %rsi
 335ead3: 48 89 c7                     	movq	%rax, %rdi
 335ead6: e8 a5 e4 0e fe               	callq	0x144cf80 <_ZN11QQmlContext18setContextPropertyERK7QStringRK8QVariant@plt>
 335eadb: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335eadf: 8b 07                        	movl	(%rdi), %eax
 335eae1: 85 c0                        	testl	%eax, %eax
 335eae3: 0f 85 a7 07 00 00            	jne	0x335f290 <NimoExSLScreenLinux::onCreateWindow()+0x970>
 335eae9: ba 08 00 00 00               	movl	$0x8, %edx
 335eaee: be 02 00 00 00               	movl	$0x2, %esi
 335eaf3: e8 a8 cb 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335eaf8: 4c 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %r15
 335eaff: 4c 89 ff                     	movq	%r15, %rdi
 335eb02: e8 b9 e6 0e fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 335eb07: 8b 73 3c                     	movl	0x3c(%rbx), %esi
 335eb0a: 4c 89 ff                     	movq	%r15, %rdi
 335eb0d: e8 4e db 0e fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 335eb12: 48 8d 3d 43 95 d5 02         	leaq	0x2d59543(%rip), %rdi   # 0x60b805c <CPersistenceComm::Initialize()::__func__+0x11d4>
 335eb19: be 0d 00 00 00               	movl	$0xd, %esi
 335eb1e: e8 7d f7 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335eb23: 48 89 df                     	movq	%rbx, %rdi
 335eb26: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335eb2a: e8 91 f8 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335eb2f: 4c 89 fa                     	movq	%r15, %rdx
 335eb32: 4c 89 e6                     	movq	%r12, %rsi
 335eb35: 48 89 c7                     	movq	%rax, %rdi
 335eb38: e8 43 e4 0e fe               	callq	0x144cf80 <_ZN11QQmlContext18setContextPropertyERK7QStringRK8QVariant@plt>
 335eb3d: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335eb41: 8b 07                        	movl	(%rdi), %eax
 335eb43: 85 c0                        	testl	%eax, %eax
 335eb45: 0f 85 1d 07 00 00            	jne	0x335f268 <NimoExSLScreenLinux::onCreateWindow()+0x948>
 335eb4b: ba 08 00 00 00               	movl	$0x8, %edx
 335eb50: be 02 00 00 00               	movl	$0x2, %esi
 335eb55: e8 46 cb 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335eb5a: 4c 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %r14
 335eb61: 4c 89 f7                     	movq	%r14, %rdi
 335eb64: e8 57 e6 0e fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 335eb69: 48 8d 3d 12 95 d5 02         	leaq	0x2d59512(%rip), %rdi   # 0x60b8082 <CPersistenceComm::Initialize()::__func__+0x11fa>
 335eb70: be 0c 00 00 00               	movl	$0xc, %esi
 335eb75: e8 26 f7 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335eb7a: 48 89 df                     	movq	%rbx, %rdi
 335eb7d: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335eb81: e8 3a f8 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335eb86: 48 89 da                     	movq	%rbx, %rdx
 335eb89: 4c 89 f6                     	movq	%r14, %rsi
 335eb8c: 48 89 c7                     	movq	%rax, %rdi
 335eb8f: e8 7c db 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335eb94: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335eb98: 8b 07                        	movl	(%rdi), %eax
 335eb9a: 85 c0                        	testl	%eax, %eax
 335eb9c: 0f 85 9e 06 00 00            	jne	0x335f240 <NimoExSLScreenLinux::onCreateWindow()+0x920>
 335eba2: ba 08 00 00 00               	movl	$0x8, %edx
 335eba7: be 02 00 00 00               	movl	$0x2, %esi
 335ebac: e8 ef ca 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335ebb1: 48 8d 3d be 94 d5 02         	leaq	0x2d594be(%rip), %rdi   # 0x60b8076 <CPersistenceComm::Initialize()::__func__+0x11ee>
 335ebb8: be 0b 00 00 00               	movl	$0xb, %esi
 335ebbd: e8 de f6 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335ebc2: 48 89 df                     	movq	%rbx, %rdi
 335ebc5: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335ebc9: e8 f2 f7 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335ebce: 48 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %rsi
 335ebd5: 31 d2                        	xorl	%edx, %edx
 335ebd7: 48 89 c7                     	movq	%rax, %rdi
 335ebda: e8 31 db 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335ebdf: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335ebe3: 8b 07                        	movl	(%rdi), %eax
 335ebe5: 85 c0                        	testl	%eax, %eax
 335ebe7: 0f 85 2b 06 00 00            	jne	0x335f218 <NimoExSLScreenLinux::onCreateWindow()+0x8f8>
 335ebed: ba 08 00 00 00               	movl	$0x8, %edx
 335ebf2: be 02 00 00 00               	movl	$0x2, %esi
 335ebf7: e8 a4 ca 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335ebfc: 48 8d 3d 45 8a d5 02         	leaq	0x2d58a45(%rip), %rdi   # 0x60b7648 <CPersistenceComm::Initialize()::__func__+0x7c0>
 335ec03: be 1e 00 00 00               	movl	$0x1e, %esi
 335ec08: e8 93 f6 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335ec0d: 4c 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %r14
 335ec14: 31 d2                        	xorl	%edx, %edx
 335ec16: 4c 89 e6                     	movq	%r12, %rsi
 335ec19: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335ec1d: 4c 89 f7                     	movq	%r14, %rdi
 335ec20: e8 9b c3 0e fe               	callq	0x144afc0 <_ZN4QUrlC1ERK7QStringNS_11ParsingModeE@plt>
 335ec25: 4c 89 f6                     	movq	%r14, %rsi
 335ec28: 48 89 df                     	movq	%rbx, %rdi
 335ec2b: e8 00 e3 0e fe               	callq	0x144cf30 <_ZN10QQuickView9setSourceERK4QUrl@plt>
 335ec30: 4c 89 f7                     	movq	%r14, %rdi
 335ec33: e8 88 eb 0e fe               	callq	0x144d7c0 <_ZN4QUrlD1Ev@plt>
 335ec38: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335ec3c: 8b 07                        	movl	(%rdi), %eax
 335ec3e: 85 c0                        	testl	%eax, %eax
 335ec40: 0f 85 aa 05 00 00            	jne	0x335f1f0 <NimoExSLScreenLinux::onCreateWindow()+0x8d0>
 335ec46: ba 08 00 00 00               	movl	$0x8, %edx
 335ec4b: be 02 00 00 00               	movl	$0x2, %esi
 335ec50: e8 4b ca 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335ec55: 44 8b 6b 34                  	movl	0x34(%rbx), %r13d
 335ec59: e8 52 8d 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 335ec5e: 31 d2                        	xorl	%edx, %edx
 335ec60: 48 89 d9                     	movq	%rbx, %rcx
 335ec63: 48 89 c7                     	movq	%rax, %rdi
 335ec66: 44 89 ee                     	movl	%r13d, %esi
 335ec69: e8 12 d8 87 ff               	callq	0x2bdc480 <CAppPluginComm::initializePlugin(ecScreenId, bool, QQuickView*)>
 335ec6e: 84 c0                        	testb	%al, %al
 335ec70: 0f 84 8a 00 00 00            	je	0x335ed00 <NimoExSLScreenLinux::onCreateWindow()+0x3e0>
 335ec76: 44 8b 6b 34                  	movl	0x34(%rbx), %r13d
 335ec7a: e8 31 8d 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 335ec7f: 31 d2                        	xorl	%edx, %edx
 335ec81: 48 89 c7                     	movq	%rax, %rdi
 335ec84: 44 89 ee                     	movl	%r13d, %esi
 335ec87: e8 24 8e 87 ff               	callq	0x2bd7ab0 <CAppPluginComm::getPlugin(ecScreenId, bool)>
 335ec8c: 48 85 c0                     	testq	%rax, %rax
 335ec8f: 74 6f                        	je	0x335ed00 <NimoExSLScreenLinux::onCreateWindow()+0x3e0>
 335ec91: 48 89 c7                     	movq	%rax, %rdi
 335ec94: e8 87 ab fe ff               	callq	0x3349820 <PluginCardManager::getPluginCard()>
 335ec99: 48 8d 3d d6 93 d5 02         	leaq	0x2d593d6(%rip), %rdi   # 0x60b8076 <CPersistenceComm::Initialize()::__func__+0x11ee>
 335eca0: be 0b 00 00 00               	movl	$0xb, %esi
 335eca5: 49 89 c5                     	movq	%rax, %r13
 335eca8: e8 f3 f5 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335ecad: 48 89 df                     	movq	%rbx, %rdi
 335ecb0: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335ecb4: e8 07 f7 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335ecb9: 48 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %rsi
 335ecc0: 4c 89 ea                     	movq	%r13, %rdx
 335ecc3: 48 89 c7                     	movq	%rax, %rdi
 335ecc6: e8 45 da 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335eccb: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335eccf: 8b 07                        	movl	(%rdi), %eax
 335ecd1: 85 c0                        	testl	%eax, %eax
 335ecd3: 74 1b                        	je	0x335ecf0 <NimoExSLScreenLinux::onCreateWindow()+0x3d0>
 335ecd5: 83 f8 ff                     	cmpl	$-0x1, %eax
 335ecd8: 74 26                        	je	0x335ed00 <NimoExSLScreenLinux::onCreateWindow()+0x3e0>
 335ecda: f0                           	lock
 335ecdb: 83 2f 01                     	subl	$0x1, (%rdi)
 335ecde: 0f 95 c0                     	setne	%al
 335ece1: 84 c0                        	testb	%al, %al
 335ece3: 75 1b                        	jne	0x335ed00 <NimoExSLScreenLinux::onCreateWindow()+0x3e0>
 335ece5: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335ece9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335ecf0: ba 08 00 00 00               	movl	$0x8, %edx
 335ecf5: be 02 00 00 00               	movl	$0x2, %esi
 335ecfa: e8 a1 c9 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335ecff: 90                           	nop
 335ed00: bf 02 00 00 00               	movl	$0x2, %edi
 335ed05: e8 46 e7 e9 ff               	callq	0x31fd450 <ExSLEglFunction::createExSLEglSurface(ExSLEglFunction::ecSurfaceType)>
 335ed0a: 48 89 df                     	movq	%rbx, %rdi
 335ed0d: 48 89 83 88 00 00 00         	movq	%rax, 0x88(%rbx)
 335ed14: e8 07 e5 0e fe               	callq	0x144d220 <_ZN7QWindow4showEv@plt>
 335ed19: e8 c2 d0 0e fe               	callq	0x144bde0 <_ZN15QGuiApplication23platformNativeInterfaceEv@plt>
 335ed1e: 49 89 c6                     	movq	%rax, %r14
 335ed21: 48 8b 00                     	movq	(%rax), %rax
 335ed24: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335ed2b: 4c 89 e6                     	movq	%r12, %rsi
 335ed2e: 4c 8b b8 d0 00 00 00         	movq	0xd0(%rax), %r15
 335ed35: 48 8d 05 64 97 d5 02         	leaq	0x2d59764(%rip), %rax   # 0x60b84a0 <NimoExSLScreenLinux::onCreateWindow()::'lambda2'()::operator()() const::qstring_literal>
 335ed3c: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335ed40: e8 0b c3 0e fe               	callq	0x144b050 <_ZN8QVariantC1ERK7QString@plt>
 335ed45: 48 8d 05 74 97 d5 02         	leaq	0x2d59774(%rip), %rax   # 0x60b84c0 <NimoExSLScreenLinux::onCreateWindow()::'lambda1'()::operator()() const::qstring_literal>
 335ed4c: 48 89 df                     	movq	%rbx, %rdi
 335ed4f: 4c 8d ad 70 ff ff ff         	leaq	-0x90(%rbp), %r13
 335ed56: 48 89 85 70 ff ff ff         	movq	%rax, -0x90(%rbp)
 335ed5d: e8 2e ea 0e fe               	callq	0x144d790 <_ZNK7QWindow6handleEv@plt>
 335ed62: 48 8b 8d 18 ff ff ff         	movq	-0xe8(%rbp), %rcx
 335ed69: 4c 89 ea                     	movq	%r13, %rdx
 335ed6c: 48 89 c6                     	movq	%rax, %rsi
 335ed6f: 4c 89 f7                     	movq	%r14, %rdi
 335ed72: 41 ff d7                     	callq	*%r15
 335ed75: 48 8b bd 70 ff ff ff         	movq	-0x90(%rbp), %rdi
 335ed7c: 8b 07                        	movl	(%rdi), %eax
 335ed7e: 85 c0                        	testl	%eax, %eax
 335ed80: 75 56                        	jne	0x335edd8 <NimoExSLScreenLinux::onCreateWindow()+0x4b8>
 335ed82: ba 08 00 00 00               	movl	$0x8, %edx
 335ed87: be 02 00 00 00               	movl	$0x2, %esi
 335ed8c: e8 0f c9 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335ed91: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335ed98: e8 23 e4 0e fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 335ed9d: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335eda1: 8b 07                        	movl	(%rdi), %eax
 335eda3: 85 c0                        	testl	%eax, %eax
 335eda5: 75 51                        	jne	0x335edf8 <NimoExSLScreenLinux::onCreateWindow()+0x4d8>
 335eda7: ba 08 00 00 00               	movl	$0x8, %edx
 335edac: be 02 00 00 00               	movl	$0x2, %esi
 335edb1: e8 ea c8 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335edb6: e9 51 fc ff ff               	jmp	0x335ea0c <NimoExSLScreenLinux::onCreateWindow()+0xec>
 335edbb: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335edbf: 90                           	nop
 335edc0: ba 08 00 00 00               	movl	$0x8, %edx
 335edc5: be 02 00 00 00               	movl	$0x2, %esi
 335edca: e8 d1 c8 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335edcf: e9 c6 fc ff ff               	jmp	0x335ea9a <NimoExSLScreenLinux::onCreateWindow()+0x17a>
 335edd4: 0f 1f 40 00                  	nopl	(%rax)
 335edd8: 83 f8 ff                     	cmpl	$-0x1, %eax
 335eddb: 74 b4                        	je	0x335ed91 <NimoExSLScreenLinux::onCreateWindow()+0x471>
 335eddd: f0                           	lock
 335edde: 83 2f 01                     	subl	$0x1, (%rdi)
 335ede1: 0f 95 c0                     	setne	%al
 335ede4: 84 c0                        	testb	%al, %al
 335ede6: 75 a9                        	jne	0x335ed91 <NimoExSLScreenLinux::onCreateWindow()+0x471>
 335ede8: 48 8b bd 70 ff ff ff         	movq	-0x90(%rbp), %rdi
 335edef: eb 91                        	jmp	0x335ed82 <NimoExSLScreenLinux::onCreateWindow()+0x462>
 335edf1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335edf8: 83 f8 ff                     	cmpl	$-0x1, %eax
 335edfb: 0f 84 0b fc ff ff            	je	0x335ea0c <NimoExSLScreenLinux::onCreateWindow()+0xec>
 335ee01: f0                           	lock
 335ee02: 83 2f 01                     	subl	$0x1, (%rdi)
 335ee05: 0f 95 c0                     	setne	%al
 335ee08: 84 c0                        	testb	%al, %al
 335ee0a: 0f 85 fc fb ff ff            	jne	0x335ea0c <NimoExSLScreenLinux::onCreateWindow()+0xec>
 335ee10: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335ee14: eb 91                        	jmp	0x335eda7 <NimoExSLScreenLinux::onCreateWindow()+0x487>
 335ee16: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 335ee20: 31 f6                        	xorl	%esi, %esi
 335ee22: 48 89 df                     	movq	%rbx, %rdi
 335ee25: e8 06 c5 0e fe               	callq	0x144b330 <_ZN12QQuickWindow23setClearBeforeRenderingEb@plt>
 335ee2a: bf 38 00 00 00               	movl	$0x38, %edi
 335ee2f: e8 fc ef 0e fe               	callq	0x144de30 <_Znwm@plt>
 335ee34: 48 89 c7                     	movq	%rax, %rdi
 335ee37: 49 89 c4                     	movq	%rax, %r12
 335ee3a: e8 61 bf 0e fe               	callq	0x144ada0 <_ZN13ImageProviderC1Ev@plt>
 335ee3f: 48 8d 3d 0b 0b a7 02         	leaq	0x2a70b0b(%rip), %rdi   # 0x5dcf951 <typeinfo name for NimoExSLMapRenderer+0xf1>
 335ee46: be 07 00 00 00               	movl	$0x7, %esi
 335ee4b: e8 50 f4 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335ee50: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335ee54: 48 8d 45 a0                  	leaq	-0x60(%rbp), %rax
 335ee58: 48 89 df                     	movq	%rbx, %rdi
 335ee5b: 48 89 85 18 ff ff ff         	movq	%rax, -0xe8(%rbp)
 335ee62: e8 49 f3 0e fe               	callq	0x144e1b0 <_ZNK10QQuickView6engineEv@plt>
 335ee67: 48 8d 4d a0                  	leaq	-0x60(%rbp), %rcx
 335ee6b: 4c 89 e2                     	movq	%r12, %rdx
 335ee6e: 48 89 c7                     	movq	%rax, %rdi
 335ee71: 48 89 ce                     	movq	%rcx, %rsi
 335ee74: 48 89 8d 18 ff ff ff         	movq	%rcx, -0xe8(%rbp)
 335ee7b: e8 20 f6 0e fe               	callq	0x144e4a0 <_ZN10QQmlEngine16addImageProviderERK7QStringP21QQmlImageProviderBase@plt>
 335ee80: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335ee84: 8b 07                        	movl	(%rdi), %eax
 335ee86: 85 c0                        	testl	%eax, %eax
 335ee88: 0f 85 02 05 00 00            	jne	0x335f390 <NimoExSLScreenLinux::onCreateWindow()+0xa70>
 335ee8e: ba 08 00 00 00               	movl	$0x8, %edx
 335ee93: be 02 00 00 00               	movl	$0x2, %esi
 335ee98: e8 03 c8 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335ee9d: 4c 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %r15
 335eea4: 8b 73 38                     	movl	0x38(%rbx), %esi
 335eea7: 4c 89 ff                     	movq	%r15, %rdi
 335eeaa: e8 b1 d7 0e fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 335eeaf: 48 8d 3d 99 91 d5 02         	leaq	0x2d59199(%rip), %rdi   # 0x60b804f <CPersistenceComm::Initialize()::__func__+0x11c7>
 335eeb6: be 0c 00 00 00               	movl	$0xc, %esi
 335eebb: e8 e0 f3 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335eec0: 48 89 df                     	movq	%rbx, %rdi
 335eec3: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335eec7: 4c 8d 65 80                  	leaq	-0x80(%rbp), %r12
 335eecb: e8 f0 f4 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335eed0: 4c 89 fa                     	movq	%r15, %rdx
 335eed3: 4c 89 e6                     	movq	%r12, %rsi
 335eed6: 48 89 c7                     	movq	%rax, %rdi
 335eed9: e8 a2 e0 0e fe               	callq	0x144cf80 <_ZN11QQmlContext18setContextPropertyERK7QStringRK8QVariant@plt>
 335eede: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335eee2: 8b 07                        	movl	(%rdi), %eax
 335eee4: 85 c0                        	testl	%eax, %eax
 335eee6: 0f 85 f4 04 00 00            	jne	0x335f3e0 <NimoExSLScreenLinux::onCreateWindow()+0xac0>
 335eeec: ba 08 00 00 00               	movl	$0x8, %edx
 335eef1: be 02 00 00 00               	movl	$0x2, %esi
 335eef6: e8 a5 c7 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335eefb: 4c 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %r15
 335ef02: 4c 89 ff                     	movq	%r15, %rdi
 335ef05: e8 b6 e2 0e fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 335ef0a: 8b 73 3c                     	movl	0x3c(%rbx), %esi
 335ef0d: 4c 89 ff                     	movq	%r15, %rdi
 335ef10: e8 4b d7 0e fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 335ef15: 48 8d 3d 40 91 d5 02         	leaq	0x2d59140(%rip), %rdi   # 0x60b805c <CPersistenceComm::Initialize()::__func__+0x11d4>
 335ef1c: be 0d 00 00 00               	movl	$0xd, %esi
 335ef21: e8 7a f3 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335ef26: 48 89 df                     	movq	%rbx, %rdi
 335ef29: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335ef2d: e8 8e f4 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335ef32: 4c 89 fa                     	movq	%r15, %rdx
 335ef35: 4c 89 e6                     	movq	%r12, %rsi
 335ef38: 48 89 c7                     	movq	%rax, %rdi
 335ef3b: e8 40 e0 0e fe               	callq	0x144cf80 <_ZN11QQmlContext18setContextPropertyERK7QStringRK8QVariant@plt>
 335ef40: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335ef44: 8b 07                        	movl	(%rdi), %eax
 335ef46: 85 c0                        	testl	%eax, %eax
 335ef48: 0f 85 6a 04 00 00            	jne	0x335f3b8 <NimoExSLScreenLinux::onCreateWindow()+0xa98>
 335ef4e: ba 08 00 00 00               	movl	$0x8, %edx
 335ef53: be 02 00 00 00               	movl	$0x2, %esi
 335ef58: e8 43 c7 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335ef5d: 4c 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %r15
 335ef64: 4c 89 ff                     	movq	%r15, %rdi
 335ef67: e8 54 e2 0e fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 335ef6c: 48 8d 3d f7 90 d5 02         	leaq	0x2d590f7(%rip), %rdi   # 0x60b806a <CPersistenceComm::Initialize()::__func__+0x11e2>
 335ef73: be 0b 00 00 00               	movl	$0xb, %esi
 335ef78: e8 23 f3 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335ef7d: 48 89 df                     	movq	%rbx, %rdi
 335ef80: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335ef84: e8 37 f4 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335ef89: 31 d2                        	xorl	%edx, %edx
 335ef8b: 4c 89 fe                     	movq	%r15, %rsi
 335ef8e: 48 89 c7                     	movq	%rax, %rdi
 335ef91: e8 7a d7 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335ef96: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335ef9a: 8b 07                        	movl	(%rdi), %eax
 335ef9c: 85 c0                        	testl	%eax, %eax
 335ef9e: 0f 85 dc 04 00 00            	jne	0x335f480 <NimoExSLScreenLinux::onCreateWindow()+0xb60>
 335efa4: ba 08 00 00 00               	movl	$0x8, %edx
 335efa9: be 02 00 00 00               	movl	$0x2, %esi
 335efae: e8 ed c6 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335efb3: 48 8d 3d bc 90 d5 02         	leaq	0x2d590bc(%rip), %rdi   # 0x60b8076 <CPersistenceComm::Initialize()::__func__+0x11ee>
 335efba: be 0b 00 00 00               	movl	$0xb, %esi
 335efbf: e8 dc f2 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335efc4: 48 89 df                     	movq	%rbx, %rdi
 335efc7: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335efcb: e8 f0 f3 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335efd0: 48 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %rsi
 335efd7: 31 d2                        	xorl	%edx, %edx
 335efd9: 48 89 c7                     	movq	%rax, %rdi
 335efdc: e8 2f d7 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335efe1: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335efe5: 8b 07                        	movl	(%rdi), %eax
 335efe7: 85 c0                        	testl	%eax, %eax
 335efe9: 0f 85 69 04 00 00            	jne	0x335f458 <NimoExSLScreenLinux::onCreateWindow()+0xb38>
 335efef: ba 08 00 00 00               	movl	$0x8, %edx
 335eff4: be 02 00 00 00               	movl	$0x2, %esi
 335eff9: e8 a2 c6 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335effe: 48 8d 3d 7d 90 d5 02         	leaq	0x2d5907d(%rip), %rdi   # 0x60b8082 <CPersistenceComm::Initialize()::__func__+0x11fa>
 335f005: be 0c 00 00 00               	movl	$0xc, %esi
 335f00a: e8 91 f2 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f00f: 48 89 df                     	movq	%rbx, %rdi
 335f012: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335f016: e8 a5 f3 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335f01b: 48 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %rsi
 335f022: 48 89 da                     	movq	%rbx, %rdx
 335f025: 48 89 c7                     	movq	%rax, %rdi
 335f028: e8 e3 d6 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335f02d: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f031: 8b 07                        	movl	(%rdi), %eax
 335f033: 85 c0                        	testl	%eax, %eax
 335f035: 0f 85 f5 03 00 00            	jne	0x335f430 <NimoExSLScreenLinux::onCreateWindow()+0xb10>
 335f03b: ba 08 00 00 00               	movl	$0x8, %edx
 335f040: be 02 00 00 00               	movl	$0x2, %esi
 335f045: e8 56 c6 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f04a: 48 89 df                     	movq	%rbx, %rdi
 335f04d: e8 8e f4 ff ff               	callq	0x335e4e0 <NimoExSLScreenLinux::setSSKnobType()>
 335f052: 48 8d 3d cf 85 d5 02         	leaq	0x2d585cf(%rip), %rdi   # 0x60b7628 <CPersistenceComm::Initialize()::__func__+0x7a0>
 335f059: be 1f 00 00 00               	movl	$0x1f, %esi
 335f05e: e8 3d f2 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f063: 4c 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %r14
 335f06a: 31 d2                        	xorl	%edx, %edx
 335f06c: 4c 89 e6                     	movq	%r12, %rsi
 335f06f: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335f073: 4c 89 f7                     	movq	%r14, %rdi
 335f076: e8 45 bf 0e fe               	callq	0x144afc0 <_ZN4QUrlC1ERK7QStringNS_11ParsingModeE@plt>
 335f07b: 4c 89 f6                     	movq	%r14, %rsi
 335f07e: 48 89 df                     	movq	%rbx, %rdi
 335f081: e8 aa de 0e fe               	callq	0x144cf30 <_ZN10QQuickView9setSourceERK4QUrl@plt>
 335f086: 4c 89 f7                     	movq	%r14, %rdi
 335f089: e8 32 e7 0e fe               	callq	0x144d7c0 <_ZN4QUrlD1Ev@plt>
 335f08e: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f092: 8b 07                        	movl	(%rdi), %eax
 335f094: 85 c0                        	testl	%eax, %eax
 335f096: 0f 85 6c 03 00 00            	jne	0x335f408 <NimoExSLScreenLinux::onCreateWindow()+0xae8>
 335f09c: ba 08 00 00 00               	movl	$0x8, %edx
 335f0a1: be 02 00 00 00               	movl	$0x2, %esi
 335f0a6: e8 f5 c5 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f0ab: e8 30 b4 84 fe               	callq	0x1baa4e0 <SystemVariant::GetInstance()>
 335f0b0: 48 89 c7                     	movq	%rax, %rdi
 335f0b3: e8 18 e8 84 fe               	callq	0x1bad8d0 <SystemVariant::isSupportSS()>
 335f0b8: 84 c0                        	testb	%al, %al
 335f0ba: 74 24                        	je	0x335f0e0 <NimoExSLScreenLinux::onCreateWindow()+0x7c0>
 335f0bc: 44 8b 6b 34                  	movl	0x34(%rbx), %r13d
 335f0c0: e8 eb 88 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 335f0c5: 48 89 d9                     	movq	%rbx, %rcx
 335f0c8: ba 01 00 00 00               	movl	$0x1, %edx
 335f0cd: 48 89 c7                     	movq	%rax, %rdi
 335f0d0: 44 89 ee                     	movl	%r13d, %esi
 335f0d3: e8 a8 d3 87 ff               	callq	0x2bdc480 <CAppPluginComm::initializePlugin(ecScreenId, bool, QQuickView*)>
 335f0d8: 84 c0                        	testb	%al, %al
 335f0da: 0f 85 f8 03 00 00            	jne	0x335f4d8 <NimoExSLScreenLinux::onCreateWindow()+0xbb8>
 335f0e0: 44 8b 6b 34                  	movl	0x34(%rbx), %r13d
 335f0e4: e8 c7 88 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 335f0e9: 31 d2                        	xorl	%edx, %edx
 335f0eb: 48 89 d9                     	movq	%rbx, %rcx
 335f0ee: 48 89 c7                     	movq	%rax, %rdi
 335f0f1: 44 89 ee                     	movl	%r13d, %esi
 335f0f4: e8 87 d3 87 ff               	callq	0x2bdc480 <CAppPluginComm::initializePlugin(ecScreenId, bool, QQuickView*)>
 335f0f9: 84 c0                        	testb	%al, %al
 335f0fb: 74 73                        	je	0x335f170 <NimoExSLScreenLinux::onCreateWindow()+0x850>
 335f0fd: 44 8b 6b 34                  	movl	0x34(%rbx), %r13d
 335f101: e8 aa 88 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 335f106: 31 d2                        	xorl	%edx, %edx
 335f108: 48 89 c7                     	movq	%rax, %rdi
 335f10b: 44 89 ee                     	movl	%r13d, %esi
 335f10e: e8 9d 89 87 ff               	callq	0x2bd7ab0 <CAppPluginComm::getPlugin(ecScreenId, bool)>
 335f113: 48 85 c0                     	testq	%rax, %rax
 335f116: 74 58                        	je	0x335f170 <NimoExSLScreenLinux::onCreateWindow()+0x850>
 335f118: 48 89 c7                     	movq	%rax, %rdi
 335f11b: e8 00 a7 fe ff               	callq	0x3349820 <PluginCardManager::getPluginCard()>
 335f120: 48 8d 3d 4f 8f d5 02         	leaq	0x2d58f4f(%rip), %rdi   # 0x60b8076 <CPersistenceComm::Initialize()::__func__+0x11ee>
 335f127: be 0b 00 00 00               	movl	$0xb, %esi
 335f12c: 49 89 c5                     	movq	%rax, %r13
 335f12f: e8 6c f1 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f134: 48 89 df                     	movq	%rbx, %rdi
 335f137: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335f13b: e8 80 f2 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335f140: 48 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %rsi
 335f147: 4c 89 ea                     	movq	%r13, %rdx
 335f14a: 48 89 c7                     	movq	%rax, %rdi
 335f14d: e8 be d5 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335f152: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f156: 8b 07                        	movl	(%rdi), %eax
 335f158: 85 c0                        	testl	%eax, %eax
 335f15a: 0f 85 00 04 00 00            	jne	0x335f560 <NimoExSLScreenLinux::onCreateWindow()+0xc40>
 335f160: ba 08 00 00 00               	movl	$0x8, %edx
 335f165: be 02 00 00 00               	movl	$0x2, %esi
 335f16a: e8 31 c5 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f16f: 90                           	nop
 335f170: bf 02 00 00 00               	movl	$0x2, %edi
 335f175: e8 d6 e2 e9 ff               	callq	0x31fd450 <ExSLEglFunction::createExSLEglSurface(ExSLEglFunction::ecSurfaceType)>
 335f17a: 48 89 df                     	movq	%rbx, %rdi
 335f17d: 48 89 83 88 00 00 00         	movq	%rax, 0x88(%rbx)
 335f184: e8 97 e0 0e fe               	callq	0x144d220 <_ZN7QWindow4showEv@plt>
 335f189: e8 52 cc 0e fe               	callq	0x144bde0 <_ZN15QGuiApplication23platformNativeInterfaceEv@plt>
 335f18e: 49 89 c6                     	movq	%rax, %r14
 335f191: 48 8b 00                     	movq	(%rax), %rax
 335f194: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335f19b: 4c 89 e6                     	movq	%r12, %rsi
 335f19e: 4c 8b b8 d0 00 00 00         	movq	0xd0(%rax), %r15
 335f1a5: 48 8d 05 54 93 d5 02         	leaq	0x2d59354(%rip), %rax   # 0x60b8500 <NimoExSLScreenLinux::onCreateWindow()::'lambda0'()::operator()() const::qstring_literal>
 335f1ac: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335f1b0: e8 9b be 0e fe               	callq	0x144b050 <_ZN8QVariantC1ERK7QString@plt>
 335f1b5: 48 8d 05 64 93 d5 02         	leaq	0x2d59364(%rip), %rax   # 0x60b8520 <NimoExSLScreenLinux::onCreateWindow()::'lambda'()::operator()() const::qstring_literal>
 335f1bc: 48 89 df                     	movq	%rbx, %rdi
 335f1bf: 4c 8d ad 70 ff ff ff         	leaq	-0x90(%rbp), %r13
 335f1c6: 48 89 85 70 ff ff ff         	movq	%rax, -0x90(%rbp)
 335f1cd: e8 be e5 0e fe               	callq	0x144d790 <_ZNK7QWindow6handleEv@plt>
 335f1d2: 48 8b 8d 18 ff ff ff         	movq	-0xe8(%rbp), %rcx
 335f1d9: 4c 89 ea                     	movq	%r13, %rdx
 335f1dc: 48 89 c6                     	movq	%rax, %rsi
 335f1df: 4c 89 f7                     	movq	%r14, %rdi
 335f1e2: 41 ff d7                     	callq	*%r15
 335f1e5: e9 8b fb ff ff               	jmp	0x335ed75 <NimoExSLScreenLinux::onCreateWindow()+0x455>
 335f1ea: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 335f1f0: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f1f3: 0f 84 5c fa ff ff            	je	0x335ec55 <NimoExSLScreenLinux::onCreateWindow()+0x335>
 335f1f9: f0                           	lock
 335f1fa: 83 2f 01                     	subl	$0x1, (%rdi)
 335f1fd: 0f 95 c0                     	setne	%al
 335f200: 84 c0                        	testb	%al, %al
 335f202: 0f 85 4d fa ff ff            	jne	0x335ec55 <NimoExSLScreenLinux::onCreateWindow()+0x335>
 335f208: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f20c: e9 35 fa ff ff               	jmp	0x335ec46 <NimoExSLScreenLinux::onCreateWindow()+0x326>
 335f211: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f218: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f21b: 0f 84 db f9 ff ff            	je	0x335ebfc <NimoExSLScreenLinux::onCreateWindow()+0x2dc>
 335f221: f0                           	lock
 335f222: 83 2f 01                     	subl	$0x1, (%rdi)
 335f225: 0f 95 c0                     	setne	%al
 335f228: 84 c0                        	testb	%al, %al
 335f22a: 0f 85 cc f9 ff ff            	jne	0x335ebfc <NimoExSLScreenLinux::onCreateWindow()+0x2dc>
 335f230: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f234: e9 b4 f9 ff ff               	jmp	0x335ebed <NimoExSLScreenLinux::onCreateWindow()+0x2cd>
 335f239: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f240: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f243: 0f 84 68 f9 ff ff            	je	0x335ebb1 <NimoExSLScreenLinux::onCreateWindow()+0x291>
 335f249: f0                           	lock
 335f24a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f24d: 0f 95 c0                     	setne	%al
 335f250: 84 c0                        	testb	%al, %al
 335f252: 0f 85 59 f9 ff ff            	jne	0x335ebb1 <NimoExSLScreenLinux::onCreateWindow()+0x291>
 335f258: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f25c: e9 41 f9 ff ff               	jmp	0x335eba2 <NimoExSLScreenLinux::onCreateWindow()+0x282>
 335f261: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f268: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f26b: 0f 84 e9 f8 ff ff            	je	0x335eb5a <NimoExSLScreenLinux::onCreateWindow()+0x23a>
 335f271: f0                           	lock
 335f272: 83 2f 01                     	subl	$0x1, (%rdi)
 335f275: 0f 95 c0                     	setne	%al
 335f278: 84 c0                        	testb	%al, %al
 335f27a: 0f 85 da f8 ff ff            	jne	0x335eb5a <NimoExSLScreenLinux::onCreateWindow()+0x23a>
 335f280: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f284: e9 c2 f8 ff ff               	jmp	0x335eb4b <NimoExSLScreenLinux::onCreateWindow()+0x22b>
 335f289: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f290: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f293: 0f 84 5f f8 ff ff            	je	0x335eaf8 <NimoExSLScreenLinux::onCreateWindow()+0x1d8>
 335f299: f0                           	lock
 335f29a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f29d: 0f 95 c0                     	setne	%al
 335f2a0: 84 c0                        	testb	%al, %al
 335f2a2: 0f 85 50 f8 ff ff            	jne	0x335eaf8 <NimoExSLScreenLinux::onCreateWindow()+0x1d8>
 335f2a8: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f2ac: e9 38 f8 ff ff               	jmp	0x335eae9 <NimoExSLScreenLinux::onCreateWindow()+0x1c9>
 335f2b1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f2b8: 4c 8d b5 20 ff ff ff         	leaq	-0xe0(%rbp), %r14
 335f2bf: bf 02 00 00 00               	movl	$0x2, %edi
 335f2c4: e8 87 e1 e9 ff               	callq	0x31fd450 <ExSLEglFunction::createExSLEglSurface(ExSLEglFunction::ecSurfaceType)>
 335f2c9: 4c 89 f7                     	movq	%r14, %rdi
 335f2cc: 48 89 83 88 00 00 00         	movq	%rax, 0x88(%rbx)
 335f2d3: e8 08 d8 0e fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 335f2d8: 4c 89 f7                     	movq	%r14, %rdi
 335f2db: e8 b0 bd 0e fe               	callq	0x144b090 <_ZNK15QDBusConnection11isConnectedEv@plt>
 335f2e0: 84 c0                        	testb	%al, %al
 335f2e2: 0f 84 c0 01 00 00            	je	0x335f4a8 <NimoExSLScreenLinux::onCreateWindow()+0xb88>
 335f2e8: 48 8d 3d a1 83 d5 02         	leaq	0x2d583a1(%rip), %rdi   # 0x60b7690 <CPersistenceComm::Initialize()::__func__+0x808>
 335f2ef: be 20 00 00 00               	movl	$0x20, %esi
 335f2f4: e8 a7 ef 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f2f9: 4c 8d a5 30 ff ff ff         	leaq	-0xd0(%rbp), %r12
 335f300: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335f304: 4c 89 e7                     	movq	%r12, %rdi
 335f307: e8 d4 d7 0e fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 335f30c: 48 8d 45 a0                  	leaq	-0x60(%rbp), %rax
 335f310: b9 01 00 00 00               	movl	$0x1, %ecx
 335f315: 48 89 da                     	movq	%rbx, %rdx
 335f318: 4c 89 e7                     	movq	%r12, %rdi
 335f31b: 48 89 c6                     	movq	%rax, %rsi
 335f31e: 48 89 85 18 ff ff ff         	movq	%rax, -0xe8(%rbp)
 335f325: e8 16 cb 0e fe               	callq	0x144be40 <_ZN15QDBusConnection14registerObjectERK7QStringP7QObject6QFlagsINS_14RegisterOptionEE@plt>
 335f32a: 4c 89 e7                     	movq	%r12, %rdi
 335f32d: 41 89 c5                     	movl	%eax, %r13d
 335f330: e8 7b e5 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335f335: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f339: 8b 07                        	movl	(%rdi), %eax
 335f33b: 85 c0                        	testl	%eax, %eax
 335f33d: 0f 85 fd 03 00 00            	jne	0x335f740 <NimoExSLScreenLinux::onCreateWindow()+0xe20>
 335f343: ba 08 00 00 00               	movl	$0x8, %edx
 335f348: be 02 00 00 00               	movl	$0x2, %esi
 335f34d: e8 4e c3 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f352: 45 84 ed                     	testb	%r13b, %r13b
 335f355: 0f 85 2d 02 00 00            	jne	0x335f588 <NimoExSLScreenLinux::onCreateWindow()+0xc68>
 335f35b: 4c 8d 05 56 83 d5 02         	leaq	0x2d58356(%rip), %r8    # 0x60b76b8 <CPersistenceComm::Initialize()::__func__+0x830>
 335f362: 48 8d 15 df 90 d5 02         	leaq	0x2d590df(%rip), %rdx   # 0x60b8448 <NimoExSLScreenLinux::onCreateWindow()::__func__>
 335f369: 48 8d 35 70 7b d5 02         	leaq	0x2d57b70(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335f370: b9 9f 00 00 00               	movl	$0x9f, %ecx
 335f375: bf 01 00 00 00               	movl	$0x1, %edi
 335f37a: 31 c0                        	xorl	%eax, %eax
 335f37c: e8 af 09 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335f381: 4c 89 f7                     	movq	%r14, %rdi
 335f384: e8 27 e5 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335f389: 31 c0                        	xorl	%eax, %eax
 335f38b: e9 34 f6 ff ff               	jmp	0x335e9c4 <NimoExSLScreenLinux::onCreateWindow()+0xa4>
 335f390: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f393: 0f 84 04 fb ff ff            	je	0x335ee9d <NimoExSLScreenLinux::onCreateWindow()+0x57d>
 335f399: f0                           	lock
 335f39a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f39d: 0f 95 c0                     	setne	%al
 335f3a0: 84 c0                        	testb	%al, %al
 335f3a2: 0f 85 f5 fa ff ff            	jne	0x335ee9d <NimoExSLScreenLinux::onCreateWindow()+0x57d>
 335f3a8: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f3ac: e9 dd fa ff ff               	jmp	0x335ee8e <NimoExSLScreenLinux::onCreateWindow()+0x56e>
 335f3b1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f3b8: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f3bb: 0f 84 9c fb ff ff            	je	0x335ef5d <NimoExSLScreenLinux::onCreateWindow()+0x63d>
 335f3c1: f0                           	lock
 335f3c2: 83 2f 01                     	subl	$0x1, (%rdi)
 335f3c5: 0f 95 c0                     	setne	%al
 335f3c8: 84 c0                        	testb	%al, %al
 335f3ca: 0f 85 8d fb ff ff            	jne	0x335ef5d <NimoExSLScreenLinux::onCreateWindow()+0x63d>
 335f3d0: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f3d4: e9 75 fb ff ff               	jmp	0x335ef4e <NimoExSLScreenLinux::onCreateWindow()+0x62e>
 335f3d9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f3e0: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f3e3: 0f 84 12 fb ff ff            	je	0x335eefb <NimoExSLScreenLinux::onCreateWindow()+0x5db>
 335f3e9: f0                           	lock
 335f3ea: 83 2f 01                     	subl	$0x1, (%rdi)
 335f3ed: 0f 95 c0                     	setne	%al
 335f3f0: 84 c0                        	testb	%al, %al
 335f3f2: 0f 85 03 fb ff ff            	jne	0x335eefb <NimoExSLScreenLinux::onCreateWindow()+0x5db>
 335f3f8: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f3fc: e9 eb fa ff ff               	jmp	0x335eeec <NimoExSLScreenLinux::onCreateWindow()+0x5cc>
 335f401: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f408: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f40b: 0f 84 9a fc ff ff            	je	0x335f0ab <NimoExSLScreenLinux::onCreateWindow()+0x78b>
 335f411: f0                           	lock
 335f412: 83 2f 01                     	subl	$0x1, (%rdi)
 335f415: 0f 95 c0                     	setne	%al
 335f418: 84 c0                        	testb	%al, %al
 335f41a: 0f 85 8b fc ff ff            	jne	0x335f0ab <NimoExSLScreenLinux::onCreateWindow()+0x78b>
 335f420: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f424: e9 73 fc ff ff               	jmp	0x335f09c <NimoExSLScreenLinux::onCreateWindow()+0x77c>
 335f429: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f430: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f433: 0f 84 11 fc ff ff            	je	0x335f04a <NimoExSLScreenLinux::onCreateWindow()+0x72a>
 335f439: f0                           	lock
 335f43a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f43d: 0f 95 c0                     	setne	%al
 335f440: 84 c0                        	testb	%al, %al
 335f442: 0f 85 02 fc ff ff            	jne	0x335f04a <NimoExSLScreenLinux::onCreateWindow()+0x72a>
 335f448: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f44c: e9 ea fb ff ff               	jmp	0x335f03b <NimoExSLScreenLinux::onCreateWindow()+0x71b>
 335f451: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f458: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f45b: 0f 84 9d fb ff ff            	je	0x335effe <NimoExSLScreenLinux::onCreateWindow()+0x6de>
 335f461: f0                           	lock
 335f462: 83 2f 01                     	subl	$0x1, (%rdi)
 335f465: 0f 95 c0                     	setne	%al
 335f468: 84 c0                        	testb	%al, %al
 335f46a: 0f 85 8e fb ff ff            	jne	0x335effe <NimoExSLScreenLinux::onCreateWindow()+0x6de>
 335f470: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f474: e9 76 fb ff ff               	jmp	0x335efef <NimoExSLScreenLinux::onCreateWindow()+0x6cf>
 335f479: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f480: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f483: 0f 84 2a fb ff ff            	je	0x335efb3 <NimoExSLScreenLinux::onCreateWindow()+0x693>
 335f489: f0                           	lock
 335f48a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f48d: 0f 95 c0                     	setne	%al
 335f490: 84 c0                        	testb	%al, %al
 335f492: 0f 85 1b fb ff ff            	jne	0x335efb3 <NimoExSLScreenLinux::onCreateWindow()+0x693>
 335f498: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f49c: e9 03 fb ff ff               	jmp	0x335efa4 <NimoExSLScreenLinux::onCreateWindow()+0x684>
 335f4a1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f4a8: 4c 8d 05 b9 81 d5 02         	leaq	0x2d581b9(%rip), %r8    # 0x60b7668 <CPersistenceComm::Initialize()::__func__+0x7e0>
 335f4af: 48 8d 15 92 8f d5 02         	leaq	0x2d58f92(%rip), %rdx   # 0x60b8448 <NimoExSLScreenLinux::onCreateWindow()::__func__>
 335f4b6: 48 8d 35 23 7a d5 02         	leaq	0x2d57a23(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335f4bd: b9 9a 00 00 00               	movl	$0x9a, %ecx
 335f4c2: bf 01 00 00 00               	movl	$0x1, %edi
 335f4c7: e8 64 08 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335f4cc: e9 b0 fe ff ff               	jmp	0x335f381 <NimoExSLScreenLinux::onCreateWindow()+0xa61>
 335f4d1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f4d8: 44 8b 6b 34                  	movl	0x34(%rbx), %r13d
 335f4dc: e8 cf 84 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 335f4e1: ba 01 00 00 00               	movl	$0x1, %edx
 335f4e6: 48 89 c7                     	movq	%rax, %rdi
 335f4e9: 44 89 ee                     	movl	%r13d, %esi
 335f4ec: e8 bf 85 87 ff               	callq	0x2bd7ab0 <CAppPluginComm::getPlugin(ecScreenId, bool)>
 335f4f1: 48 85 c0                     	testq	%rax, %rax
 335f4f4: 0f 84 e6 fb ff ff            	je	0x335f0e0 <NimoExSLScreenLinux::onCreateWindow()+0x7c0>
 335f4fa: 48 89 c7                     	movq	%rax, %rdi
 335f4fd: e8 1e a3 fe ff               	callq	0x3349820 <PluginCardManager::getPluginCard()>
 335f502: 48 8d 3d 61 8b d5 02         	leaq	0x2d58b61(%rip), %rdi   # 0x60b806a <CPersistenceComm::Initialize()::__func__+0x11e2>
 335f509: be 0b 00 00 00               	movl	$0xb, %esi
 335f50e: 49 89 c5                     	movq	%rax, %r13
 335f511: e8 8a ed 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f516: 48 89 df                     	movq	%rbx, %rdi
 335f519: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335f51d: e8 9e ee 0e fe               	callq	0x144e3c0 <_ZNK10QQuickView11rootContextEv@plt>
 335f522: 48 8b b5 18 ff ff ff         	movq	-0xe8(%rbp), %rsi
 335f529: 4c 89 ea                     	movq	%r13, %rdx
 335f52c: 48 89 c7                     	movq	%rax, %rdi
 335f52f: e8 dc d1 0e fe               	callq	0x144c710 <_ZN11QQmlContext18setContextPropertyERK7QStringP7QObject@plt>
 335f534: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f538: 8b 07                        	movl	(%rdi), %eax
 335f53a: 85 c0                        	testl	%eax, %eax
 335f53c: 0f 85 7e 04 00 00            	jne	0x335f9c0 <NimoExSLScreenLinux::onCreateWindow()+0x10a0>
 335f542: ba 08 00 00 00               	movl	$0x8, %edx
 335f547: be 02 00 00 00               	movl	$0x2, %esi
 335f54c: e8 4f c1 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f551: e9 8a fb ff ff               	jmp	0x335f0e0 <NimoExSLScreenLinux::onCreateWindow()+0x7c0>
 335f556: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 335f560: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f563: 0f 84 07 fc ff ff            	je	0x335f170 <NimoExSLScreenLinux::onCreateWindow()+0x850>
 335f569: f0                           	lock
 335f56a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f56d: 0f 95 c0                     	setne	%al
 335f570: 84 c0                        	testb	%al, %al
 335f572: 0f 85 f8 fb ff ff            	jne	0x335f170 <NimoExSLScreenLinux::onCreateWindow()+0x850>
 335f578: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f57c: e9 df fb ff ff               	jmp	0x335f160 <NimoExSLScreenLinux::onCreateWindow()+0x840>
 335f581: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f588: 48 8d 3d 00 8b d5 02         	leaq	0x2d58b00(%rip), %rdi   # 0x60b808f <CPersistenceComm::Initialize()::__func__+0x1207>
 335f58f: be 12 00 00 00               	movl	$0x12, %esi
 335f594: e8 07 ed 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f599: 48 8d 3d 38 81 d5 02         	leaq	0x2d58138(%rip), %rdi   # 0x60b76d8 <CPersistenceComm::Initialize()::__func__+0x850>
 335f5a0: be 28 00 00 00               	movl	$0x28, %esi
 335f5a5: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335f5a9: e8 f2 ec 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f5ae: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335f5b2: 48 8b 05 67 ed 34 04         	movq	0x434ed67(%rip), %rax   # 0x76ae320 <_GLOBAL_OFFSET_TABLE_+0x50b8>
 335f5b9: 48 89 85 70 ff ff ff         	movq	%rax, -0x90(%rbp)
 335f5c0: 48 89 85 60 ff ff ff         	movq	%rax, -0xa0(%rbp)
 335f5c7: 48 8d 85 40 ff ff ff         	leaq	-0xc0(%rbp), %rax
 335f5ce: 48 89 c7                     	movq	%rax, %rdi
 335f5d1: 48 89 85 10 ff ff ff         	movq	%rax, -0xf0(%rbp)
 335f5d8: e8 03 d5 0e fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 335f5dd: 48 8d 0d be 8a d5 02         	leaq	0x2d58abe(%rip), %rcx   # 0x60b80a2 <CPersistenceComm::Initialize()::__func__+0x121a>
 335f5e4: 48 83 ec 08                  	subq	$0x8, %rsp
 335f5e8: 4c 8d 65 80                  	leaq	-0x80(%rbp), %r12
 335f5ec: 4c 8d ad 70 ff ff ff         	leaq	-0x90(%rbp), %r13
 335f5f3: 4c 8d bd 60 ff ff ff         	leaq	-0xa0(%rbp), %r15
 335f5fa: 4c 8b 85 18 ff ff ff         	movq	-0xe8(%rbp), %r8
 335f601: 48 8b bd 10 ff ff ff         	movq	-0xf0(%rbp), %rdi
 335f608: 51                           	pushq	%rcx
 335f609: 49 89 d9                     	movq	%rbx, %r9
 335f60c: 4c 89 e1                     	movq	%r12, %rcx
 335f60f: 4c 89 ea                     	movq	%r13, %rdx
 335f612: 4c 89 fe                     	movq	%r15, %rsi
 335f615: e8 b6 b9 0e fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 335f61a: 59                           	popq	%rcx
 335f61b: 5e                           	popq	%rsi
 335f61c: 48 8b bd 10 ff ff ff         	movq	-0xf0(%rbp), %rdi
 335f623: 88 85 0f ff ff ff            	movb	%al, -0xf1(%rbp)
 335f629: e8 82 e2 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335f62e: 48 8b bd 60 ff ff ff         	movq	-0xa0(%rbp), %rdi
 335f635: 8b 07                        	movl	(%rdi), %eax
 335f637: 85 c0                        	testl	%eax, %eax
 335f639: 0f 85 59 03 00 00            	jne	0x335f998 <NimoExSLScreenLinux::onCreateWindow()+0x1078>
 335f63f: ba 08 00 00 00               	movl	$0x8, %edx
 335f644: be 02 00 00 00               	movl	$0x2, %esi
 335f649: e8 52 c0 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f64e: 48 8b bd 70 ff ff ff         	movq	-0x90(%rbp), %rdi
 335f655: 8b 07                        	movl	(%rdi), %eax
 335f657: 85 c0                        	testl	%eax, %eax
 335f659: 0f 85 11 03 00 00            	jne	0x335f970 <NimoExSLScreenLinux::onCreateWindow()+0x1050>
 335f65f: ba 08 00 00 00               	movl	$0x8, %edx
 335f664: be 02 00 00 00               	movl	$0x2, %esi
 335f669: e8 32 c0 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f66e: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f672: 8b 07                        	movl	(%rdi), %eax
 335f674: 85 c0                        	testl	%eax, %eax
 335f676: 0f 85 cc 02 00 00            	jne	0x335f948 <NimoExSLScreenLinux::onCreateWindow()+0x1028>
 335f67c: ba 08 00 00 00               	movl	$0x8, %edx
 335f681: be 02 00 00 00               	movl	$0x2, %esi
 335f686: e8 15 c0 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f68b: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f68f: 8b 07                        	movl	(%rdi), %eax
 335f691: 85 c0                        	testl	%eax, %eax
 335f693: 0f 85 87 02 00 00            	jne	0x335f920 <NimoExSLScreenLinux::onCreateWindow()+0x1000>
 335f699: ba 08 00 00 00               	movl	$0x8, %edx
 335f69e: be 02 00 00 00               	movl	$0x2, %esi
 335f6a3: e8 f8 bf 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f6a8: 80 bd 0f ff ff ff 00         	cmpb	$0x0, -0xf1(%rbp)
 335f6af: 0f 85 b3 00 00 00            	jne	0x335f768 <NimoExSLScreenLinux::onCreateWindow()+0xe48>
 335f6b5: 4c 89 ff                     	movq	%r15, %rdi
 335f6b8: e8 23 d4 0e fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 335f6bd: 4c 89 fe                     	movq	%r15, %rsi
 335f6c0: 4c 89 e7                     	movq	%r12, %rdi
 335f6c3: e8 78 b5 0e fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 335f6c8: 4c 89 e7                     	movq	%r12, %rdi
 335f6cb: e8 e0 c5 0e fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 335f6d0: 4c 8d 05 31 80 d5 02         	leaq	0x2d58031(%rip), %r8    # 0x60b7708 <CPersistenceComm::Initialize()::__func__+0x880>
 335f6d7: 48 8d 15 6a 8d d5 02         	leaq	0x2d58d6a(%rip), %rdx   # 0x60b8448 <NimoExSLScreenLinux::onCreateWindow()::__func__>
 335f6de: 48 8d 35 fb 77 d5 02         	leaq	0x2d577fb(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335f6e5: 41 89 c1                     	movl	%eax, %r9d
 335f6e8: b9 a5 00 00 00               	movl	$0xa5, %ecx
 335f6ed: bf 01 00 00 00               	movl	$0x1, %edi
 335f6f2: 31 c0                        	xorl	%eax, %eax
 335f6f4: e8 37 06 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335f6f9: 48 8b 7d 90                  	movq	-0x70(%rbp), %rdi
 335f6fd: 8b 07                        	movl	(%rdi), %eax
 335f6ff: 85 c0                        	testl	%eax, %eax
 335f701: 0f 85 a9 03 00 00            	jne	0x335fab0 <NimoExSLScreenLinux::onCreateWindow()+0x1190>
 335f707: ba 08 00 00 00               	movl	$0x8, %edx
 335f70c: be 02 00 00 00               	movl	$0x2, %esi
 335f711: e8 8a bf 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f716: 48 8b 7d 88                  	movq	-0x78(%rbp), %rdi
 335f71a: 8b 07                        	movl	(%rdi), %eax
 335f71c: 85 c0                        	testl	%eax, %eax
 335f71e: 0f 85 64 03 00 00            	jne	0x335fa88 <NimoExSLScreenLinux::onCreateWindow()+0x1168>
 335f724: ba 08 00 00 00               	movl	$0x8, %edx
 335f729: be 02 00 00 00               	movl	$0x2, %esi
 335f72e: e8 6d bf 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f733: 4c 89 ff                     	movq	%r15, %rdi
 335f736: e8 75 e1 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335f73b: e9 41 fc ff ff               	jmp	0x335f381 <NimoExSLScreenLinux::onCreateWindow()+0xa61>
 335f740: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f743: 0f 84 09 fc ff ff            	je	0x335f352 <NimoExSLScreenLinux::onCreateWindow()+0xa32>
 335f749: f0                           	lock
 335f74a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f74d: 0f 95 c0                     	setne	%al
 335f750: 84 c0                        	testb	%al, %al
 335f752: 0f 85 fa fb ff ff            	jne	0x335f352 <NimoExSLScreenLinux::onCreateWindow()+0xa32>
 335f758: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f75c: e9 e2 fb ff ff               	jmp	0x335f343 <NimoExSLScreenLinux::onCreateWindow()+0xa23>
 335f761: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f768: 48 8d 3d c1 7f d5 02         	leaq	0x2d57fc1(%rip), %rdi   # 0x60b7730 <CPersistenceComm::Initialize()::__func__+0x8a8>
 335f76f: be 20 00 00 00               	movl	$0x20, %esi
 335f774: e8 27 eb 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f779: 48 8d 3d 28 c1 c5 02         	leaq	0x2c5c128(%rip), %rdi   # 0x5fbb8a8 <typeinfo name for PluginCardEvent+0x178>
 335f780: be 33 00 00 00               	movl	$0x33, %esi
 335f785: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 335f789: e8 12 eb 0e fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 335f78e: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 335f792: 48 8b 05 87 eb 34 04         	movq	0x434eb87(%rip), %rax   # 0x76ae320 <_GLOBAL_OFFSET_TABLE_+0x50b8>
 335f799: 48 89 85 70 ff ff ff         	movq	%rax, -0x90(%rbp)
 335f7a0: 48 89 85 60 ff ff ff         	movq	%rax, -0xa0(%rbp)
 335f7a7: 48 8d 85 50 ff ff ff         	leaq	-0xb0(%rbp), %rax
 335f7ae: 48 89 c7                     	movq	%rax, %rdi
 335f7b1: 48 89 85 10 ff ff ff         	movq	%rax, -0xf0(%rbp)
 335f7b8: e8 23 d3 0e fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 335f7bd: 48 8d 0d 94 7f d5 02         	leaq	0x2d57f94(%rip), %rcx   # 0x60b7758 <CPersistenceComm::Initialize()::__func__+0x8d0>
 335f7c4: 48 83 ec 08                  	subq	$0x8, %rsp
 335f7c8: 4c 8b 85 18 ff ff ff         	movq	-0xe8(%rbp), %r8
 335f7cf: 48 8b bd 10 ff ff ff         	movq	-0xf0(%rbp), %rdi
 335f7d6: 49 89 d9                     	movq	%rbx, %r9
 335f7d9: 4c 89 ea                     	movq	%r13, %rdx
 335f7dc: 51                           	pushq	%rcx
 335f7dd: 4c 89 fe                     	movq	%r15, %rsi
 335f7e0: 4c 89 e1                     	movq	%r12, %rcx
 335f7e3: e8 e8 b7 0e fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 335f7e8: 41 89 c4                     	movl	%eax, %r12d
 335f7eb: 48 8b bd 10 ff ff ff         	movq	-0xf0(%rbp), %rdi
 335f7f2: 58                           	popq	%rax
 335f7f3: 5a                           	popq	%rdx
 335f7f4: e8 b7 e0 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335f7f9: 48 8b bd 60 ff ff ff         	movq	-0xa0(%rbp), %rdi
 335f800: 8b 07                        	movl	(%rdi), %eax
 335f802: 85 c0                        	testl	%eax, %eax
 335f804: 0f 85 de 01 00 00            	jne	0x335f9e8 <NimoExSLScreenLinux::onCreateWindow()+0x10c8>
 335f80a: ba 08 00 00 00               	movl	$0x8, %edx
 335f80f: be 02 00 00 00               	movl	$0x2, %esi
 335f814: e8 87 be 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f819: 48 8b bd 70 ff ff ff         	movq	-0x90(%rbp), %rdi
 335f820: 8b 07                        	movl	(%rdi), %eax
 335f822: 85 c0                        	testl	%eax, %eax
 335f824: 0f 85 0e 02 00 00            	jne	0x335fa38 <NimoExSLScreenLinux::onCreateWindow()+0x1118>
 335f82a: ba 08 00 00 00               	movl	$0x8, %edx
 335f82f: be 02 00 00 00               	movl	$0x2, %esi
 335f834: e8 67 be 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f839: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f83d: 8b 07                        	movl	(%rdi), %eax
 335f83f: 85 c0                        	testl	%eax, %eax
 335f841: 0f 85 c9 01 00 00            	jne	0x335fa10 <NimoExSLScreenLinux::onCreateWindow()+0x10f0>
 335f847: ba 08 00 00 00               	movl	$0x8, %edx
 335f84c: be 02 00 00 00               	movl	$0x2, %esi
 335f851: e8 4a be 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f856: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f85a: 8b 07                        	movl	(%rdi), %eax
 335f85c: 85 c0                        	testl	%eax, %eax
 335f85e: 0f 85 fc 01 00 00            	jne	0x335fa60 <NimoExSLScreenLinux::onCreateWindow()+0x1140>
 335f864: ba 08 00 00 00               	movl	$0x8, %edx
 335f869: be 02 00 00 00               	movl	$0x2, %esi
 335f86e: e8 2d be 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f873: 45 84 e4                     	testb	%r12b, %r12b
 335f876: 0f 85 8d 00 00 00            	jne	0x335f909 <NimoExSLScreenLinux::onCreateWindow()+0xfe9>
 335f87c: 4c 89 ef                     	movq	%r13, %rdi
 335f87f: e8 5c d2 0e fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 335f884: 4c 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %r15
 335f88b: 4c 89 ee                     	movq	%r13, %rsi
 335f88e: 4c 89 ff                     	movq	%r15, %rdi
 335f891: e8 aa b3 0e fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 335f896: 4c 89 ff                     	movq	%r15, %rdi
 335f899: e8 12 c4 0e fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 335f89e: 4c 8d 05 e3 7e d5 02         	leaq	0x2d57ee3(%rip), %r8    # 0x60b7788 <CPersistenceComm::Initialize()::__func__+0x900>
 335f8a5: 48 8d 15 9c 8b d5 02         	leaq	0x2d58b9c(%rip), %rdx   # 0x60b8448 <NimoExSLScreenLinux::onCreateWindow()::__func__>
 335f8ac: 48 8d 35 2d 76 d5 02         	leaq	0x2d5762d(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335f8b3: 41 89 c1                     	movl	%eax, %r9d
 335f8b6: b9 aa 00 00 00               	movl	$0xaa, %ecx
 335f8bb: bf 01 00 00 00               	movl	$0x1, %edi
 335f8c0: 31 c0                        	xorl	%eax, %eax
 335f8c2: e8 69 04 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335f8c7: 48 8b 7d b0                  	movq	-0x50(%rbp), %rdi
 335f8cb: 8b 07                        	movl	(%rdi), %eax
 335f8cd: 85 c0                        	testl	%eax, %eax
 335f8cf: 0f 85 2b 02 00 00            	jne	0x335fb00 <NimoExSLScreenLinux::onCreateWindow()+0x11e0>
 335f8d5: ba 08 00 00 00               	movl	$0x8, %edx
 335f8da: be 02 00 00 00               	movl	$0x2, %esi
 335f8df: e8 bc bd 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f8e4: 48 8b 7d a8                  	movq	-0x58(%rbp), %rdi
 335f8e8: 8b 07                        	movl	(%rdi), %eax
 335f8ea: 85 c0                        	testl	%eax, %eax
 335f8ec: 0f 85 e6 01 00 00            	jne	0x335fad8 <NimoExSLScreenLinux::onCreateWindow()+0x11b8>
 335f8f2: ba 08 00 00 00               	movl	$0x8, %edx
 335f8f7: be 02 00 00 00               	movl	$0x2, %esi
 335f8fc: e8 9f bd 0e fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 335f901: 4c 89 ef                     	movq	%r13, %rdi
 335f904: e8 a7 df 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335f909: 4c 89 f7                     	movq	%r14, %rdi
 335f90c: e8 9f df 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335f911: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 335f915: e9 7f f0 ff ff               	jmp	0x335e999 <NimoExSLScreenLinux::onCreateWindow()+0x79>
 335f91a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 335f920: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f923: 0f 84 7f fd ff ff            	je	0x335f6a8 <NimoExSLScreenLinux::onCreateWindow()+0xd88>
 335f929: f0                           	lock
 335f92a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f92d: 0f 95 c0                     	setne	%al
 335f930: 84 c0                        	testb	%al, %al
 335f932: 0f 85 70 fd ff ff            	jne	0x335f6a8 <NimoExSLScreenLinux::onCreateWindow()+0xd88>
 335f938: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f93c: e9 58 fd ff ff               	jmp	0x335f699 <NimoExSLScreenLinux::onCreateWindow()+0xd79>
 335f941: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f948: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f94b: 0f 84 3a fd ff ff            	je	0x335f68b <NimoExSLScreenLinux::onCreateWindow()+0xd6b>
 335f951: f0                           	lock
 335f952: 83 2f 01                     	subl	$0x1, (%rdi)
 335f955: 0f 95 c0                     	setne	%al
 335f958: 84 c0                        	testb	%al, %al
 335f95a: 0f 85 2b fd ff ff            	jne	0x335f68b <NimoExSLScreenLinux::onCreateWindow()+0xd6b>
 335f960: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335f964: e9 13 fd ff ff               	jmp	0x335f67c <NimoExSLScreenLinux::onCreateWindow()+0xd5c>
 335f969: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f970: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f973: 0f 84 f5 fc ff ff            	je	0x335f66e <NimoExSLScreenLinux::onCreateWindow()+0xd4e>
 335f979: f0                           	lock
 335f97a: 83 2f 01                     	subl	$0x1, (%rdi)
 335f97d: 0f 95 c0                     	setne	%al
 335f980: 84 c0                        	testb	%al, %al
 335f982: 0f 85 e6 fc ff ff            	jne	0x335f66e <NimoExSLScreenLinux::onCreateWindow()+0xd4e>
 335f988: 48 8b bd 70 ff ff ff         	movq	-0x90(%rbp), %rdi
 335f98f: e9 cb fc ff ff               	jmp	0x335f65f <NimoExSLScreenLinux::onCreateWindow()+0xd3f>
 335f994: 0f 1f 40 00                  	nopl	(%rax)
 335f998: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f99b: 0f 84 ad fc ff ff            	je	0x335f64e <NimoExSLScreenLinux::onCreateWindow()+0xd2e>
 335f9a1: f0                           	lock
 335f9a2: 83 2f 01                     	subl	$0x1, (%rdi)
 335f9a5: 0f 95 c0                     	setne	%al
 335f9a8: 84 c0                        	testb	%al, %al
 335f9aa: 0f 85 9e fc ff ff            	jne	0x335f64e <NimoExSLScreenLinux::onCreateWindow()+0xd2e>
 335f9b0: 48 8b bd 60 ff ff ff         	movq	-0xa0(%rbp), %rdi
 335f9b7: e9 83 fc ff ff               	jmp	0x335f63f <NimoExSLScreenLinux::onCreateWindow()+0xd1f>
 335f9bc: 0f 1f 40 00                  	nopl	(%rax)
 335f9c0: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f9c3: 0f 84 17 f7 ff ff            	je	0x335f0e0 <NimoExSLScreenLinux::onCreateWindow()+0x7c0>
 335f9c9: f0                           	lock
 335f9ca: 83 2f 01                     	subl	$0x1, (%rdi)
 335f9cd: 0f 95 c0                     	setne	%al
 335f9d0: 84 c0                        	testb	%al, %al
 335f9d2: 0f 85 08 f7 ff ff            	jne	0x335f0e0 <NimoExSLScreenLinux::onCreateWindow()+0x7c0>
 335f9d8: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335f9dc: e9 61 fb ff ff               	jmp	0x335f542 <NimoExSLScreenLinux::onCreateWindow()+0xc22>
 335f9e1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335f9e8: 83 f8 ff                     	cmpl	$-0x1, %eax
 335f9eb: 0f 84 28 fe ff ff            	je	0x335f819 <NimoExSLScreenLinux::onCreateWindow()+0xef9>
 335f9f1: f0                           	lock
 335f9f2: 83 2f 01                     	subl	$0x1, (%rdi)
 335f9f5: 0f 95 c0                     	setne	%al
 335f9f8: 84 c0                        	testb	%al, %al
 335f9fa: 0f 85 19 fe ff ff            	jne	0x335f819 <NimoExSLScreenLinux::onCreateWindow()+0xef9>
 335fa00: 48 8b bd 60 ff ff ff         	movq	-0xa0(%rbp), %rdi
 335fa07: e9 fe fd ff ff               	jmp	0x335f80a <NimoExSLScreenLinux::onCreateWindow()+0xeea>
 335fa0c: 0f 1f 40 00                  	nopl	(%rax)
 335fa10: 83 f8 ff                     	cmpl	$-0x1, %eax
 335fa13: 0f 84 3d fe ff ff            	je	0x335f856 <NimoExSLScreenLinux::onCreateWindow()+0xf36>
 335fa19: f0                           	lock
 335fa1a: 83 2f 01                     	subl	$0x1, (%rdi)
 335fa1d: 0f 95 c0                     	setne	%al
 335fa20: 84 c0                        	testb	%al, %al
 335fa22: 0f 85 2e fe ff ff            	jne	0x335f856 <NimoExSLScreenLinux::onCreateWindow()+0xf36>
 335fa28: 48 8b 7d 80                  	movq	-0x80(%rbp), %rdi
 335fa2c: e9 16 fe ff ff               	jmp	0x335f847 <NimoExSLScreenLinux::onCreateWindow()+0xf27>
 335fa31: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335fa38: 83 f8 ff                     	cmpl	$-0x1, %eax
 335fa3b: 0f 84 f8 fd ff ff            	je	0x335f839 <NimoExSLScreenLinux::onCreateWindow()+0xf19>
 335fa41: f0                           	lock
 335fa42: 83 2f 01                     	subl	$0x1, (%rdi)
 335fa45: 0f 95 c0                     	setne	%al
 335fa48: 84 c0                        	testb	%al, %al
 335fa4a: 0f 85 e9 fd ff ff            	jne	0x335f839 <NimoExSLScreenLinux::onCreateWindow()+0xf19>
 335fa50: 48 8b bd 70 ff ff ff         	movq	-0x90(%rbp), %rdi
 335fa57: e9 ce fd ff ff               	jmp	0x335f82a <NimoExSLScreenLinux::onCreateWindow()+0xf0a>
 335fa5c: 0f 1f 40 00                  	nopl	(%rax)
 335fa60: 83 f8 ff                     	cmpl	$-0x1, %eax
 335fa63: 0f 84 0a fe ff ff            	je	0x335f873 <NimoExSLScreenLinux::onCreateWindow()+0xf53>
 335fa69: f0                           	lock
 335fa6a: 83 2f 01                     	subl	$0x1, (%rdi)
 335fa6d: 0f 95 c0                     	setne	%al
 335fa70: 84 c0                        	testb	%al, %al
 335fa72: 0f 85 fb fd ff ff            	jne	0x335f873 <NimoExSLScreenLinux::onCreateWindow()+0xf53>
 335fa78: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 335fa7c: e9 e3 fd ff ff               	jmp	0x335f864 <NimoExSLScreenLinux::onCreateWindow()+0xf44>
 335fa81: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335fa88: 83 f8 ff                     	cmpl	$-0x1, %eax
 335fa8b: 0f 84 a2 fc ff ff            	je	0x335f733 <NimoExSLScreenLinux::onCreateWindow()+0xe13>
 335fa91: f0                           	lock
 335fa92: 83 2f 01                     	subl	$0x1, (%rdi)
 335fa95: 0f 95 c0                     	setne	%al
 335fa98: 84 c0                        	testb	%al, %al
 335fa9a: 0f 85 93 fc ff ff            	jne	0x335f733 <NimoExSLScreenLinux::onCreateWindow()+0xe13>
 335faa0: 48 8b 7d 88                  	movq	-0x78(%rbp), %rdi
 335faa4: e9 7b fc ff ff               	jmp	0x335f724 <NimoExSLScreenLinux::onCreateWindow()+0xe04>
 335faa9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335fab0: 83 f8 ff                     	cmpl	$-0x1, %eax
 335fab3: 0f 84 5d fc ff ff            	je	0x335f716 <NimoExSLScreenLinux::onCreateWindow()+0xdf6>
 335fab9: f0                           	lock
 335faba: 83 2f 01                     	subl	$0x1, (%rdi)
 335fabd: 0f 95 c0                     	setne	%al
 335fac0: 84 c0                        	testb	%al, %al
 335fac2: 0f 85 4e fc ff ff            	jne	0x335f716 <NimoExSLScreenLinux::onCreateWindow()+0xdf6>
 335fac8: 48 8b 7d 90                  	movq	-0x70(%rbp), %rdi
 335facc: e9 36 fc ff ff               	jmp	0x335f707 <NimoExSLScreenLinux::onCreateWindow()+0xde7>
 335fad1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335fad8: 83 f8 ff                     	cmpl	$-0x1, %eax
 335fadb: 0f 84 20 fe ff ff            	je	0x335f901 <NimoExSLScreenLinux::onCreateWindow()+0xfe1>
 335fae1: f0                           	lock
 335fae2: 83 2f 01                     	subl	$0x1, (%rdi)
 335fae5: 0f 95 c0                     	setne	%al
 335fae8: 84 c0                        	testb	%al, %al
 335faea: 0f 85 11 fe ff ff            	jne	0x335f901 <NimoExSLScreenLinux::onCreateWindow()+0xfe1>
 335faf0: 48 8b 7d a8                  	movq	-0x58(%rbp), %rdi
 335faf4: e9 f9 fd ff ff               	jmp	0x335f8f2 <NimoExSLScreenLinux::onCreateWindow()+0xfd2>
 335faf9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335fb00: 83 f8 ff                     	cmpl	$-0x1, %eax
 335fb03: 0f 84 db fd ff ff            	je	0x335f8e4 <NimoExSLScreenLinux::onCreateWindow()+0xfc4>
 335fb09: f0                           	lock
 335fb0a: 83 2f 01                     	subl	$0x1, (%rdi)
 335fb0d: 0f 95 c0                     	setne	%al
 335fb10: 84 c0                        	testb	%al, %al
 335fb12: 0f 85 cc fd ff ff            	jne	0x335f8e4 <NimoExSLScreenLinux::onCreateWindow()+0xfc4>
 335fb18: 48 8b 7d b0                  	movq	-0x50(%rbp), %rdi
 335fb1c: e9 b4 fd ff ff               	jmp	0x335f8d5 <NimoExSLScreenLinux::onCreateWindow()+0xfb5>
 335fb21: e8 6a b0 0e fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 335fb26: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335fb2d: 48 89 c3                     	movq	%rax, %rbx
 335fb30: e8 0b 3f 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fb35: 48 89 df                     	movq	%rbx, %rdi
 335fb38: e8 23 d7 0e fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335fb3d: 48 89 c3                     	movq	%rax, %rbx
 335fb40: 4c 89 f7                     	movq	%r14, %rdi
 335fb43: e8 68 dd 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335fb48: 48 89 df                     	movq	%rbx, %rdi
 335fb4b: e8 10 d7 0e fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335fb50: 4c 89 ef                     	movq	%r13, %rdi
 335fb53: 48 89 c3                     	movq	%rax, %rbx
 335fb56: e8 e5 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fb5b: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335fb62: e8 59 d6 0e fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 335fb67: 4c 89 e7                     	movq	%r12, %rdi
 335fb6a: e8 d1 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fb6f: 48 89 df                     	movq	%rbx, %rdi
 335fb72: e8 e9 d6 0e fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335fb77: 48 89 c3                     	movq	%rax, %rbx
 335fb7a: eb eb                        	jmp	0x335fb67 <NimoExSLScreenLinux::onCreateWindow()+0x1247>
 335fb7c: 48 89 c3                     	movq	%rax, %rbx
 335fb7f: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335fb86: e8 35 d6 0e fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 335fb8b: 48 89 df                     	movq	%rbx, %rdi
 335fb8e: e8 cd d6 0e fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335fb93: 4c 89 e7                     	movq	%r12, %rdi
 335fb96: 48 89 c3                     	movq	%rax, %rbx
 335fb99: e8 a2 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fb9e: eb df                        	jmp	0x335fb7f <NimoExSLScreenLinux::onCreateWindow()+0x125f>
 335fba0: eb da                        	jmp	0x335fb7c <NimoExSLScreenLinux::onCreateWindow()+0x125c>
 335fba2: eb 82                        	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fba4: 48 89 c3                     	movq	%rax, %rbx
 335fba7: 4c 89 e7                     	movq	%r12, %rdi
 335fbaa: be 38 00 00 00               	movl	$0x38, %esi
 335fbaf: e8 ec cf 0e fe               	callq	0x144cba0 <_ZdlPvm@plt>
 335fbb4: 48 89 df                     	movq	%rbx, %rdi
 335fbb7: e8 a4 d6 0e fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335fbbc: eb 92                        	jmp	0x335fb50 <NimoExSLScreenLinux::onCreateWindow()+0x1230>
 335fbbe: 4c 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %r15
 335fbc5: 48 89 c3                     	movq	%rax, %rbx
 335fbc8: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 335fbcc: e8 6f 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fbd1: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 335fbd5: e8 66 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fbda: 4c 89 ef                     	movq	%r13, %rdi
 335fbdd: e8 ce dc 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335fbe2: e9 59 ff ff ff               	jmp	0x335fb40 <NimoExSLScreenLinux::onCreateWindow()+0x1220>
 335fbe7: 48 89 c3                     	movq	%rax, %rbx
 335fbea: eb ee                        	jmp	0x335fbda <NimoExSLScreenLinux::onCreateWindow()+0x12ba>
 335fbec: eb b6                        	jmp	0x335fba4 <NimoExSLScreenLinux::onCreateWindow()+0x1284>
 335fbee: eb a3                        	jmp	0x335fb93 <NimoExSLScreenLinux::onCreateWindow()+0x1273>
 335fbf0: eb 8a                        	jmp	0x335fb7c <NimoExSLScreenLinux::onCreateWindow()+0x125c>
 335fbf2: eb 9f                        	jmp	0x335fb93 <NimoExSLScreenLinux::onCreateWindow()+0x1273>
 335fbf4: eb 86                        	jmp	0x335fb7c <NimoExSLScreenLinux::onCreateWindow()+0x125c>
 335fbf6: 48 8b bd 10 ff ff ff         	movq	-0xf0(%rbp), %rdi
 335fbfd: 48 89 c3                     	movq	%rax, %rbx
 335fc00: e8 ab dc 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335fc05: 4c 89 ff                     	movq	%r15, %rdi
 335fc08: e8 33 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fc0d: 4c 89 ef                     	movq	%r13, %rdi
 335fc10: e8 2b 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fc15: 4c 89 e7                     	movq	%r12, %rdi
 335fc18: e8 23 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fc1d: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335fc24: e8 17 3e 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fc29: e9 12 ff ff ff               	jmp	0x335fb40 <NimoExSLScreenLinux::onCreateWindow()+0x1220>
 335fc2e: e9 f3 fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fc33: e9 ee fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fc38: e9 3a ff ff ff               	jmp	0x335fb77 <NimoExSLScreenLinux::onCreateWindow()+0x1257>
 335fc3d: 48 8b bd 18 ff ff ff         	movq	-0xe8(%rbp), %rdi
 335fc44: 48 89 c3                     	movq	%rax, %rbx
 335fc47: e8 74 db 0e fe               	callq	0x144d7c0 <_ZN4QUrlD1Ev@plt>
 335fc4c: e9 16 ff ff ff               	jmp	0x335fb67 <NimoExSLScreenLinux::onCreateWindow()+0x1247>
 335fc51: e9 21 ff ff ff               	jmp	0x335fb77 <NimoExSLScreenLinux::onCreateWindow()+0x1257>
 335fc56: e9 cb fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fc5b: e9 c6 fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fc60: 48 89 c3                     	movq	%rax, %rbx
 335fc63: 4c 8d 65 80                  	leaq	-0x80(%rbp), %r12
 335fc67: 4c 8d ad 70 ff ff ff         	leaq	-0x90(%rbp), %r13
 335fc6e: 4c 8d bd 60 ff ff ff         	leaq	-0xa0(%rbp), %r15
 335fc75: eb 8e                        	jmp	0x335fc05 <NimoExSLScreenLinux::onCreateWindow()+0x12e5>
 335fc77: 48 89 c3                     	movq	%rax, %rbx
 335fc7a: eb a1                        	jmp	0x335fc1d <NimoExSLScreenLinux::onCreateWindow()+0x12fd>
 335fc7c: 48 89 c3                     	movq	%rax, %rbx
 335fc7f: eb 84                        	jmp	0x335fc05 <NimoExSLScreenLinux::onCreateWindow()+0x12e5>
 335fc81: eb f4                        	jmp	0x335fc77 <NimoExSLScreenLinux::onCreateWindow()+0x1357>
 335fc83: eb b8                        	jmp	0x335fc3d <NimoExSLScreenLinux::onCreateWindow()+0x131d>
 335fc85: e9 ed fe ff ff               	jmp	0x335fb77 <NimoExSLScreenLinux::onCreateWindow()+0x1257>
 335fc8a: 4c 89 e7                     	movq	%r12, %rdi
 335fc8d: 48 89 c3                     	movq	%rax, %rbx
 335fc90: e8 1b dc 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335fc95: eb 86                        	jmp	0x335fc1d <NimoExSLScreenLinux::onCreateWindow()+0x12fd>
 335fc97: 48 89 c3                     	movq	%rax, %rbx
 335fc9a: 48 8d 45 a0                  	leaq	-0x60(%rbp), %rax
 335fc9e: 48 89 85 18 ff ff ff         	movq	%rax, -0xe8(%rbp)
 335fca5: e9 73 ff ff ff               	jmp	0x335fc1d <NimoExSLScreenLinux::onCreateWindow()+0x12fd>
 335fcaa: e9 47 ff ff ff               	jmp	0x335fbf6 <NimoExSLScreenLinux::onCreateWindow()+0x12d6>
 335fcaf: e9 72 fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fcb4: 49 8d 7c 24 10               	leaq	0x10(%r12), %rdi
 335fcb9: 48 89 c3                     	movq	%rax, %rbx
 335fcbc: e8 7f 3d 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fcc1: 49 8d 7c 24 08               	leaq	0x8(%r12), %rdi
 335fcc6: e8 75 3d 81 ff               	callq	0x2b73a40 <QString::~QString()>
 335fccb: 4c 89 ff                     	movq	%r15, %rdi
 335fcce: e8 dd db 0e fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 335fcd3: e9 68 fe ff ff               	jmp	0x335fb40 <NimoExSLScreenLinux::onCreateWindow()+0x1220>
 335fcd8: 48 89 c3                     	movq	%rax, %rbx
 335fcdb: eb ee                        	jmp	0x335fccb <NimoExSLScreenLinux::onCreateWindow()+0x13ab>
 335fcdd: e9 44 fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fce2: e9 3f fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fce7: e9 3a fe ff ff               	jmp	0x335fb26 <NimoExSLScreenLinux::onCreateWindow()+0x1206>
 335fcec: e9 a2 fe ff ff               	jmp	0x335fb93 <NimoExSLScreenLinux::onCreateWindow()+0x1273>
 335fcf1: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 335fcf6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000335fd00 <non-virtual thunk to NimoExSLScreenLinux::onCreateWindow()>:
 335fd00: 48 83 ef 28                  	subq	$0x28, %rdi
 335fd04: e9 17 ec ff ff               	jmp	0x335e920 <NimoExSLScreenLinux::onCreateWindow()>
 335fd09: 90                           	nop
 335fd0a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
