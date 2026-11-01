
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

000000000335b990 <NimoExSLScreenLinux::onBeforeRendering()>:
 335bd00: 00 ff                        	addb	%bh, %bh
 335bd02: 15 21 9d b2 04               	adcl	$0x4b29d21, %eax        # imm = 0x4B29D21
 335bd07: ba 04 00 00 00               	movl	$0x4, %edx
 335bd0c: 31 f6                        	xorl	%esi, %esi
 335bd0e: bf 05 00 00 00               	movl	$0x5, %edi
 335bd13: e8 68 1d 0f fe               	callq	0x144da80 <glDrawArrays@plt>
 335bd18: 4c 89 e6                     	movq	%r12, %rsi
 335bd1b: 48 89 ef                     	movq	%rbp, %rdi
 335bd1e: ff 15 0c 9d b2 04            	callq	*0x4b29d0c(%rip)        # 0x7e85a30 <NimoExSLScreenLinux::onBeforeRendering()::eglDestroyImageKHR>
 335bd24: 31 f6                        	xorl	%esi, %esi
 335bd26: bf 92 88 00 00               	movl	$0x8892, %edi           # imm = 0x8892
 335bd2b: e8 90 17 0f fe               	callq	0x144d4c0 <glBindBuffer@plt>
 335bd30: 31 ff                        	xorl	%edi, %edi
 335bd32: e8 19 2a 0f fe               	callq	0x144e750 <glDisableVertexAttribArray@plt>
 335bd37: bf 01 00 00 00               	movl	$0x1, %edi
 335bd3c: e8 0f 2a 0f fe               	callq	0x144e750 <glDisableVertexAttribArray@plt>
 335bd41: 31 ff                        	xorl	%edi, %edi
 335bd43: e8 98 ed 0e fe               	callq	0x144aae0 <glUseProgram@plt>
 335bd48: e9 9f fd ff ff               	jmp	0x335baec <NimoExSLScreenLinux::onBeforeRendering()+0x15c>
 335bd4d: 0f 1f 00                     	nopl	(%rax)
 335bd50: bf e1 0d 00 00               	movl	$0xde1, %edi            # imm = 0xDE1
 335bd55: e8 56 0c 0f fe               	callq	0x144c9b0 <glBindTexture@plt>
 335bd5a: eb 9d                        	jmp	0x335bcf9 <NimoExSLScreenLinux::onBeforeRendering()+0x369>
 335bd5c: 0f 1f 40 00                  	nopl	(%rax)
 335bd60: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 335bd64: 4c 8d 05 45 b5 d5 02         	leaq	0x2d5b545(%rip), %r8    # 0x60b72b0 <CPersistenceComm::Initialize()::__func__+0x428>
 335bd6b: 48 8d 15 6e c6 d5 02         	leaq	0x2d5c66e(%rip), %rdx   # 0x60b83e0 <NimoExSLScreenLinux::onBeforeRendering()::__func__>
 335bd72: 48 8d 35 67 b1 d5 02         	leaq	0x2d5b167(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335bd79: b9 12 02 00 00               	movl	$0x212, %ecx            # imm = 0x212
 335bd7e: bf 01 00 00 00               	movl	$0x1, %edi
 335bd83: 31 c0                        	xorl	%eax, %eax
 335bd85: e8 a6 3f 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335bd8a: 48 89 df                     	movq	%rbx, %rdi
 335bd8d: e8 5e 11 0f fe               	callq	0x144cef0 <_ZN12QQuickWindow16resetOpenGLStateEv@plt>
 335bd92: e9 55 fd ff ff               	jmp	0x335baec <NimoExSLScreenLinux::onBeforeRendering()+0x15c>
 335bd97: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 335bda0: 4c 8d 05 fb c1 d5 02         	leaq	0x2d5c1fb(%rip), %r8    # 0x60b7fa2 <CPersistenceComm::Initialize()::__func__+0x111a>
 335bda7: b9 15 02 00 00               	movl	$0x215, %ecx            # imm = 0x215
 335bdac: e9 eb fd ff ff               	jmp	0x335bb9c <NimoExSLScreenLinux::onBeforeRendering()+0x20c>
 335bdb1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335bdb8: 0f 28 05 a1 c7 d5 02         	movaps	0x2d5c7a1(%rip), %xmm0  # 0x60b8560 <NimoExSLScreenLinux::onCreateWindow()::'lambda'()::operator()() const::qstring_literal+0x40>
 335bdbf: 48 8d b3 74 01 00 00         	leaq	0x174(%rbx), %rsi
 335bdc6: bf 01 00 00 00               	movl	$0x1, %edi
 335bdcb: 0f 29 44 24 30               	movaps	%xmm0, 0x30(%rsp)
 335bdd0: 0f 28 05 99 c7 d5 02         	movaps	0x2d5c799(%rip), %xmm0  # 0x60b8570 <NimoExSLScreenLinux::onCreateWindow()::'lambda'()::operator()() const::qstring_literal+0x50>
 335bdd7: 0f 29 44 24 40               	movaps	%xmm0, 0x40(%rsp)
 335bddc: 0f 28 05 9d c7 d5 02         	movaps	0x2d5c79d(%rip), %xmm0  # 0x60b8580 <NimoExSLScreenLinux::onCreateWindow()::'lambda'()::operator()() const::qstring_literal+0x60>
 335bde3: 0f 29 44 24 50               	movaps	%xmm0, 0x50(%rsp)
 335bde8: 0f 28 05 a1 c7 d5 02         	movaps	0x2d5c7a1(%rip), %xmm0  # 0x60b8590 <NimoExSLScreenLinux::onCreateWindow()::'lambda'()::operator()() const::qstring_literal+0x70>
 335bdef: 0f 29 44 24 60               	movaps	%xmm0, 0x60(%rsp)
 335bdf4: e8 e7 eb 0e fe               	callq	0x144a9e0 <glGenBuffers@plt>
 335bdf9: bf 92 88 00 00               	movl	$0x8892, %edi           # imm = 0x8892
 335bdfe: 8b b3 74 01 00 00            	movl	0x174(%rbx), %esi
 335be04: e8 b7 16 0f fe               	callq	0x144d4c0 <glBindBuffer@plt>
 335be09: 48 8d 54 24 30               	leaq	0x30(%rsp), %rdx
 335be0e: be 40 00 00 00               	movl	$0x40, %esi
 335be13: b9 e4 88 00 00               	movl	$0x88e4, %ecx           # imm = 0x88E4
 335be18: bf 92 88 00 00               	movl	$0x8892, %edi           # imm = 0x8892
 335be1d: e8 ee 20 0f fe               	callq	0x144df10 <glBufferData@plt>
 335be22: 8b b3 74 01 00 00            	movl	0x174(%rbx), %esi
 335be28: e9 59 fe ff ff               	jmp	0x335bc86 <NimoExSLScreenLinux::onBeforeRendering()+0x2f6>
 335be2d: e8 5e ed 0e fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 335be32: 48 8d 3d 47 9c b2 04         	leaq	0x4b29c47(%rip), %rdi   # 0x7e85a80 <guard variable for NimoExSLScreenLinux::onBeforeRendering()::glEGLImageTargetTexture2DOES>
 335be39: 48 89 c3                     	movq	%rax, %rbx
 335be3c: e8 bf ee 0e fe               	callq	0x144ad00 <__cxa_guard_abort@plt>
 335be41: 48 89 df                     	movq	%rbx, %rdi
 335be44: e8 17 14 0f fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335be49: 48 8d 3d 38 9c b2 04         	leaq	0x4b29c38(%rip), %rdi   # 0x7e85a88 <guard variable for NimoExSLScreenLinux::onBeforeRendering()::eglDestroyImageKHR>
 335be50: 48 89 c3                     	movq	%rax, %rbx
 335be53: e8 a8 ee 0e fe               	callq	0x144ad00 <__cxa_guard_abort@plt>
 335be58: 48 89 df                     	movq	%rbx, %rdi
 335be5b: e8 00 14 0f fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335be60: 48 8d 3d 29 9c b2 04         	leaq	0x4b29c29(%rip), %rdi   # 0x7e85a90 <guard variable for NimoExSLScreenLinux::onBeforeRendering()::eglCreateImageKHR>
 335be67: 48 89 c3                     	movq	%rax, %rbx
 335be6a: e8 91 ee 0e fe               	callq	0x144ad00 <__cxa_guard_abort@plt>
 335be6f: 48 89 df                     	movq	%rbx, %rdi
 335be72: e8 e9 13 0f fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335be77: 90                           	nop
 335be78: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

000000000335be80 <NimoExSLScreenLinux::onVisibleChanged(bool)>:
 335be80: 41 57                        	pushq	%r15
 335be82: 41 56                        	pushq	%r14
 335be84: 44 0f b6 ce                  	movzbl	%sil, %r9d
 335be88: 41 55                        	pushq	%r13
 335be8a: 41 54                        	pushq	%r12
 335be8c: 4c 8d 05 29 c1 d5 02         	leaq	0x2d5c129(%rip), %r8    # 0x60b7fbc <CPersistenceComm::Initialize()::__func__+0x1134>
 335be93: 55                           	pushq	%rbp
 335be94: 53                           	pushq	%rbx
 335be95: 89 f5                        	movl	%esi, %ebp
 335be97: 48 8d 15 22 c5 d5 02         	leaq	0x2d5c522(%rip), %rdx   # 0x60b83c0 <NimoExSLScreenLinux::onVisibleChanged(bool)::__func__>
 335be9e: 48 8d 35 3b b0 d5 02         	leaq	0x2d5b03b(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335bea5: 48 89 fb                     	movq	%rdi, %rbx
 335bea8: 48 81 ec 98 00 00 00         	subq	$0x98, %rsp
 335beaf: b9 4a 02 00 00               	movl	$0x24a, %ecx            # imm = 0x24A
 335beb4: bf 01 00 00 00               	movl	$0x1, %edi
 335beb9: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 335bec2: 48 89 84 24 88 00 00 00      	movq	%rax, 0x88(%rsp)
 335beca: 31 c0                        	xorl	%eax, %eax
 335becc: e8 5f 3e 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335bed1: 83 7b 34 01                  	cmpl	$0x1, 0x34(%rbx)
 335bed5: 74 31                        	je	0x335bf08 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x88>
 335bed7: 40 88 6b 74                  	movb	%bpl, 0x74(%rbx)
 335bedb: 48 8b 84 24 88 00 00 00      	movq	0x88(%rsp), %rax
 335bee3: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 335beec: 0f 85 76 04 00 00            	jne	0x335c368 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x4e8>
 335bef2: 48 81 c4 98 00 00 00         	addq	$0x98, %rsp
 335bef9: 5b                           	popq	%rbx
 335befa: 5d                           	popq	%rbp
 335befb: 41 5c                        	popq	%r12
 335befd: 41 5d                        	popq	%r13
 335beff: 41 5e                        	popq	%r14
 335bf01: 41 5f                        	popq	%r15
 335bf03: c3                           	retq
 335bf04: 0f 1f 40 00                  	nopl	(%rax)
 335bf08: 40 84 ed                     	testb	%bpl, %bpl
 335bf0b: 0f 85 ff 02 00 00            	jne	0x335c210 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x390>
 335bf11: 48 8d 05 08 9b b2 04         	leaq	0x4b29b08(%rip), %rax   # 0x7e85a20 <g_firstTimeHideByWM>
 335bf18: 80 38 00                     	cmpb	$0x0, (%rax)
 335bf1b: 0f 85 8e 00 00 00            	jne	0x335bfaf <NimoExSLScreenLinux::onVisibleChanged(bool)+0x12f>
 335bf21: c6 00 01                     	movb	$0x1, (%rax)
 335bf24: 48 8d 05 b5 a1 b2 04         	leaq	0x4b2a1b5(%rip), %rax   # 0x7e860e0 <g_NaviLaunched>
 335bf2b: 4c 8d 05 3e b4 d5 02         	leaq	0x2d5b43e(%rip), %r8    # 0x60b7370 <CPersistenceComm::Initialize()::__func__+0x4e8>
 335bf32: b9 56 02 00 00               	movl	$0x256, %ecx            # imm = 0x256
 335bf37: 80 38 00                     	cmpb	$0x0, (%rax)
 335bf3a: 0f 85 e0 02 00 00            	jne	0x335c220 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3a0>
 335bf40: 48 8d 15 79 c4 d5 02         	leaq	0x2d5c479(%rip), %rdx   # 0x60b83c0 <NimoExSLScreenLinux::onVisibleChanged(bool)::__func__>
 335bf47: 48 8d 35 92 af d5 02         	leaq	0x2d5af92(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335bf4e: bf 01 00 00 00               	movl	$0x1, %edi
 335bf53: 31 c0                        	xorl	%eax, %eax
 335bf55: e8 d6 3d 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335bf5a: 4c 8d 05 2f b4 d5 02         	leaq	0x2d5b42f(%rip), %r8    # 0x60b7390 <CPersistenceComm::Initialize()::__func__+0x508>
 335bf61: 48 8d 15 58 c4 d5 02         	leaq	0x2d5c458(%rip), %rdx   # 0x60b83c0 <NimoExSLScreenLinux::onVisibleChanged(bool)::__func__>
 335bf68: 48 8d 35 71 af d5 02         	leaq	0x2d5af71(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335bf6f: b9 59 02 00 00               	movl	$0x259, %ecx            # imm = 0x259
 335bf74: 31 c0                        	xorl	%eax, %eax
 335bf76: bf 01 00 00 00               	movl	$0x1, %edi
 335bf7b: e8 b0 3d 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335bf80: 48 8d 7b 28                  	leaq	0x28(%rbx), %rdi
 335bf84: e8 97 c4 00 00               	callq	0x3368420 <NimoExSLScreen::clearScreen()>
 335bf89: 4c 8d 05 38 b4 d5 02         	leaq	0x2d5b438(%rip), %r8    # 0x60b73c8 <CPersistenceComm::Initialize()::__func__+0x540>
 335bf90: 48 8d 15 29 c4 d5 02         	leaq	0x2d5c429(%rip), %rdx   # 0x60b83c0 <NimoExSLScreenLinux::onVisibleChanged(bool)::__func__>
 335bf97: 48 8d 35 42 af d5 02         	leaq	0x2d5af42(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335bf9e: b9 5b 02 00 00               	movl	$0x25b, %ecx            # imm = 0x25B
 335bfa3: bf 01 00 00 00               	movl	$0x1, %edi
 335bfa8: 31 c0                        	xorl	%eax, %eax
 335bfaa: e8 81 3d 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335bfaf: 80 7b 40 00                  	cmpb	$0x0, 0x40(%rbx)
 335bfb3: c6 43 74 00                  	movb	$0x0, 0x74(%rbx)
 335bfb7: 0f 84 1e ff ff ff            	je	0x335bedb <NimoExSLScreenLinux::onVisibleChanged(bool)+0x5b>
 335bfbd: 83 7b 34 01                  	cmpl	$0x1, 0x34(%rbx)
 335bfc1: 0f 85 14 ff ff ff            	jne	0x335bedb <NimoExSLScreenLinux::onVisibleChanged(bool)+0x5b>
 335bfc7: e8 94 49 2a ff               	callq	0x2600960 <getTickCount()>
 335bfcc: 48 8d 15 2d da 38 04         	leaq	0x438da2d(%rip), %rdx   # 0x76e9a00 <g_startTime>
 335bfd3: 2b 02                        	subl	(%rdx), %eax
 335bfd5: 3d 4f c3 00 00               	cmpl	$0xc34f, %eax           # imm = 0xC34F
 335bfda: 0f 87 fb fe ff ff            	ja	0x335bedb <NimoExSLScreenLinux::onVisibleChanged(bool)+0x5b>
 335bfe0: 4c 8d 05 19 b4 d5 02         	leaq	0x2d5b419(%rip), %r8    # 0x60b7400 <CPersistenceComm::Initialize()::__func__+0x578>
 335bfe7: 48 8d 15 d2 c3 d5 02         	leaq	0x2d5c3d2(%rip), %rdx   # 0x60b83c0 <NimoExSLScreenLinux::onVisibleChanged(bool)::__func__>
 335bfee: 48 8d 35 eb ae d5 02         	leaq	0x2d5aeeb(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 335bff5: 4c 8d 64 24 40               	leaq	0x40(%rsp), %r12
 335bffa: b9 62 02 00 00               	movl	$0x262, %ecx            # imm = 0x262
 335bfff: 31 c0                        	xorl	%eax, %eax
 335c001: bf 02 00 00 00               	movl	$0x2, %edi
 335c006: e8 25 3d 4b ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 335c00b: 49 8d 44 24 10               	leaq	0x10(%r12), %rax
 335c010: 31 d2                        	xorl	%edx, %edx
 335c012: 4c 89 e7                     	movq	%r12, %rdi
 335c015: 48 c7 44 24 18 10 00 00 00   	movq	$0x10, 0x18(%rsp)
 335c01e: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 335c023: 48 8d 44 24 18               	leaq	0x18(%rsp), %rax
 335c028: 48 89 c6                     	movq	%rax, %rsi
 335c02b: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 335c030: e8 3b 12 0f fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 335c035: 48 8b 54 24 18               	movq	0x18(%rsp), %rdx
 335c03a: 48 b9 6f 6e 56 69 73 69 62 6c	movabsq	$0x6c62697369566e6f, %rcx # imm = 0x6C62697369566E6F
 335c044: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 335c049: 48 8b 35 d0 1b 35 04         	movq	0x4351bd0(%rip), %rsi   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 335c050: bf 68 00 00 00               	movl	$0x68, %edi
 335c055: 48 89 54 24 50               	movq	%rdx, 0x50(%rsp)
 335c05a: 48 89 08                     	movq	%rcx, (%rax)
 335c05d: 48 b9 65 43 68 61 6e 67 65 64	movabsq	$0x6465676e61684365, %rcx # imm = 0x6465676E61684365
 335c067: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 335c06b: 48 8b 54 24 40               	movq	0x40(%rsp), %rdx
 335c070: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
 335c075: 48 89 44 24 48               	movq	%rax, 0x48(%rsp)
 335c07a: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 335c07e: e8 3d 18 0f fe               	callq	0x144d8c0 <_ZnwmRKSt9nothrow_t@plt>
 335c083: 48 85 c0                     	testq	%rax, %rax
 335c086: 48 89 c5                     	movq	%rax, %rbp
 335c089: 0f 84 83 00 00 00            	je	0x335c112 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x292>
 335c08f: c7 40 08 00 00 00 00         	movl	$0x0, 0x8(%rax)
 335c096: c7 40 0c 00 00 00 00         	movl	$0x0, 0xc(%rax)
 335c09d: 48 8d 40 20                  	leaq	0x20(%rax), %rax
 335c0a1: 48 c7 45 18 00 00 00 00      	movq	$0x0, 0x18(%rbp)
 335c0a9: c6 45 20 00                  	movb	$0x0, 0x20(%rbp)
 335c0ad: 48 89 45 10                  	movq	%rax, 0x10(%rbp)
 335c0b1: 48 8d 05 48 3d 1a 04         	leaq	0x41a3d48(%rip), %rax   # 0x74ffe00 <vtable for ExSLTransitionEvent>
 335c0b8: c7 45 30 02 00 00 00         	movl	$0x2, 0x30(%rbp)
 335c0bf: c7 45 34 00 00 00 00         	movl	$0x0, 0x34(%rbp)
 335c0c6: c7 45 38 00 00 00 00         	movl	$0x0, 0x38(%rbp)
 335c0cd: c7 45 3c 00 00 00 00         	movl	$0x0, 0x3c(%rbp)
 335c0d4: 48 83 c0 10                  	addq	$0x10, %rax
 335c0d8: c7 45 40 00 00 00 00         	movl	$0x0, 0x40(%rbp)
 335c0df: c7 45 44 04 00 00 00         	movl	$0x4, 0x44(%rbp)
 335c0e6: 48 89 45 00                  	movq	%rax, (%rbp)
 335c0ea: c6 45 48 00                  	movb	$0x0, 0x48(%rbp)
 335c0ee: c6 45 49 00                  	movb	$0x0, 0x49(%rbp)
 335c0f2: c6 45 4a 00                  	movb	$0x0, 0x4a(%rbp)
 335c0f6: c6 45 4b 00                  	movb	$0x0, 0x4b(%rbp)
 335c0fa: 48 c7 45 50 00 00 00 00      	movq	$0x0, 0x50(%rbp)
 335c102: 48 c7 45 58 00 00 00 00      	movq	$0x0, 0x58(%rbp)
 335c10a: 48 c7 45 60 00 00 00 00      	movq	$0x0, 0x60(%rbp)
 335c112: 48 8d 44 24 20               	leaq	0x20(%rsp), %rax
 335c117: 48 8d 74 24 10               	leaq	0x10(%rsp), %rsi
 335c11c: 31 d2                        	xorl	%edx, %edx
 335c11e: 48 c7 44 24 10 44 00 00 00   	movq	$0x44, 0x10(%rsp)
 335c127: 48 89 c7                     	movq	%rax, %rdi
 335c12a: 48 89 04 24                  	movq	%rax, (%rsp)
 335c12e: 48 8d 44 24 30               	leaq	0x30(%rsp), %rax
 335c133: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 335c138: e8 33 11 0f fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 335c13d: 48 8b 54 24 10               	movq	0x10(%rsp), %rdx
 335c142: 48 b9 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rcx # imm = 0x2E2E2F2E2E2F2E2E
 335c14c: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 335c151: c7 40 40 2e 63 70 70         	movl	$0x7070632e, 0x40(%rax) # imm = 0x7070632E
 335c158: 4c 8d 6c 24 60               	leaq	0x60(%rsp), %r13
 335c15d: 48 89 54 24 30               	movq	%rdx, 0x30(%rsp)
 335c162: 48 89 08                     	movq	%rcx, (%rax)
 335c165: 48 b9 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rcx # imm = 0x76614E2F6372732F
 335c16f: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 335c173: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 335c17d: 48 8b 54 24 20               	movq	0x20(%rsp), %rdx
 335c182: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 335c186: 48 b9 4e 69 6d 6f 2f 46 72 61	movabsq	$0x6172462f6f6d694e, %rcx # imm = 0x6172462F6F6D694E
 335c190: 48 89 48 18                  	movq	%rcx, 0x18(%rax)
 335c194: 48 b9 6d 65 77 6f 72 6b 2f 4c	movabsq	$0x4c2f6b726f77656d, %rcx # imm = 0x4C2F6B726F77656D
 335c19e: 48 89 48 20                  	movq	%rcx, 0x20(%rax)
 335c1a2: 48 b9 69 6e 75 78 2f 4e 69 6d	movabsq	$0x6d694e2f78756e69, %rcx # imm = 0x6D694E2F78756E69
 335c1ac: 48 89 48 28                  	movq	%rcx, 0x28(%rax)
 335c1b0: 48 b9 6f 45 78 53 4c 53 63 72	movabsq	$0x7263534c5378456f, %rcx # imm = 0x7263534C5378456F
 335c1ba: 48 89 48 30                  	movq	%rcx, 0x30(%rax)
 335c1be: 48 b9 65 65 6e 4c 69 6e 75 78	movabsq	$0x78756e694c6e6565, %rcx # imm = 0x78756E694C6E6565
 335c1c8: 48 89 48 38                  	movq	%rcx, 0x38(%rax)
 335c1cc: 48 8b 44 24 10               	movq	0x10(%rsp), %rax
 335c1d1: 48 89 44 24 28               	movq	%rax, 0x28(%rsp)
 335c1d6: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 335c1da: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 335c1de: 4c 8b 7c 24 20               	movq	0x20(%rsp), %r15
 335c1e3: 4c 8b 74 24 28               	movq	0x28(%rsp), %r14
 335c1e8: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 335c1ed: 4c 89 f8                     	movq	%r15, %rax
 335c1f0: 4c 01 f0                     	addq	%r14, %rax
 335c1f3: 0f 84 7f 00 00 00            	je	0x335c278 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3f8>
 335c1f9: 4d 85 ff                     	testq	%r15, %r15
 335c1fc: 75 7a                        	jne	0x335c278 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3f8>
 335c1fe: 48 8d 3d 43 88 a0 02         	leaq	0x2a08843(%rip), %rdi   # 0x5d64a48 <_IO_stdin_used+0x8>
 335c205: e8 16 1a 0f fe               	callq	0x144dc20 <_ZSt19__throw_logic_errorPKc@plt>
 335c20a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 335c210: c6 43 74 01                  	movb	$0x1, 0x74(%rbx)
 335c214: e9 c2 fc ff ff               	jmp	0x335bedb <NimoExSLScreenLinux::onVisibleChanged(bool)+0x5b>
 335c219: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 335c220: e8 fb 7e 8a ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 335c225: 48 89 c7                     	movq	%rax, %rdi
 335c228: e8 83 c8 8a ff               	callq	0x2c08ab0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()>
 335c22d: 4c 8d 05 f4 b0 d5 02         	leaq	0x2d5b0f4(%rip), %r8    # 0x60b7328 <CPersistenceComm::Initialize()::__func__+0x4a0>
 335c234: b9 54 02 00 00               	movl	$0x254, %ecx            # imm = 0x254
 335c239: e9 02 fd ff ff               	jmp	0x335bf40 <NimoExSLScreenLinux::onVisibleChanged(bool)+0xc0>
 335c23e: 48 89 c3                     	movq	%rax, %rbx
 335c241: 48 8b 04 24                  	movq	(%rsp), %rax
 335c245: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
 335c24a: 48 83 c0 10                  	addq	$0x10, %rax
 335c24e: 48 39 c7                     	cmpq	%rax, %rdi
 335c251: 74 05                        	je	0x335c258 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3d8>
 335c253: e8 58 ec 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 335c258: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 335c25d: 49 83 c4 10                  	addq	$0x10, %r12
 335c261: 4c 39 e7                     	cmpq	%r12, %rdi
 335c264: 74 05                        	je	0x335c26b <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3eb>
 335c266: e8 45 ec 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 335c26b: 48 89 df                     	movq	%rbx, %rdi
 335c26e: e8 ed 0f 0f fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335c273: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 335c278: 49 83 fe 0f                  	cmpq	$0xf, %r14
 335c27c: 4c 89 74 24 18               	movq	%r14, 0x18(%rsp)
 335c281: 0f 87 be 00 00 00            	ja	0x335c345 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x4c5>
 335c287: 49 83 fe 01                  	cmpq	$0x1, %r14
 335c28b: 0f 85 96 00 00 00            	jne	0x335c327 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x4a7>
 335c291: 41 0f b6 07                  	movzbl	(%r15), %eax
 335c295: 49 8d 55 10                  	leaq	0x10(%r13), %rdx
 335c299: 88 44 24 70                  	movb	%al, 0x70(%rsp)
 335c29d: b8 01 00 00 00               	movl	$0x1, %eax
 335c2a2: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 335c2a7: 45 31 c9                     	xorl	%r9d, %r9d
 335c2aa: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 335c2ae: 41 b8 68 00 00 00            	movl	$0x68, %r8d
 335c2b4: 48 89 e9                     	movq	%rbp, %rcx
 335c2b7: ba 63 02 00 00               	movl	$0x263, %edx            # imm = 0x263
 335c2bc: 4c 89 ee                     	movq	%r13, %rsi
 335c2bf: bf 00 20 00 00               	movl	$0x2000, %edi           # imm = 0x2000
 335c2c4: e8 c7 ca 4a ff               	callq	0x2808d90 <ExSLMemoryNew>
 335c2c9: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 335c2ce: 49 83 c5 10                  	addq	$0x10, %r13
 335c2d2: 4c 39 ef                     	cmpq	%r13, %rdi
 335c2d5: 74 05                        	je	0x335c2dc <NimoExSLScreenLinux::onVisibleChanged(bool)+0x45c>
 335c2d7: e8 d4 eb 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 335c2dc: 8b 5b 34                     	movl	0x34(%rbx), %ebx
 335c2df: e8 dc 8d 4b ff               	callq	0x28150c0 <ExSLEventHandler::getInstance()>
 335c2e4: 4c 89 e1                     	movq	%r12, %rcx
 335c2e7: 48 89 ea                     	movq	%rbp, %rdx
 335c2ea: 89 de                        	movl	%ebx, %esi
 335c2ec: 48 89 c7                     	movq	%rax, %rdi
 335c2ef: e8 7c 99 4b ff               	callq	0x2815c70 <ExSLEventHandler::addEvent_external(ecScreenId, ExSLEventBase*, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>)>
 335c2f4: 48 8b 04 24                  	movq	(%rsp), %rax
 335c2f8: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
 335c2fd: 48 83 c0 10                  	addq	$0x10, %rax
 335c301: 48 39 c7                     	cmpq	%rax, %rdi
 335c304: 74 05                        	je	0x335c30b <NimoExSLScreenLinux::onVisibleChanged(bool)+0x48b>
 335c306: e8 a5 eb 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 335c30b: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 335c310: 49 83 c4 10                  	addq	$0x10, %r12
 335c314: 4c 39 e7                     	cmpq	%r12, %rdi
 335c317: 0f 84 be fb ff ff            	je	0x335bedb <NimoExSLScreenLinux::onVisibleChanged(bool)+0x5b>
 335c31d: e8 8e eb 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 335c322: e9 b4 fb ff ff               	jmp	0x335bedb <NimoExSLScreenLinux::onVisibleChanged(bool)+0x5b>
 335c327: 49 8d 7d 10                  	leaq	0x10(%r13), %rdi
 335c32b: 4c 89 f2                     	movq	%r14, %rdx
 335c32e: 4c 89 fe                     	movq	%r15, %rsi
 335c331: e8 5a 19 0f fe               	callq	0x144dc90 <memcpy@plt>
 335c336: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
 335c33b: 48 8b 54 24 60               	movq	0x60(%rsp), %rdx
 335c340: e9 5d ff ff ff               	jmp	0x335c2a2 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x422>
 335c345: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
 335c34a: 31 d2                        	xorl	%edx, %edx
 335c34c: 4c 89 ef                     	movq	%r13, %rdi
 335c34f: e8 1c 0f 0f fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 335c354: 48 8b 54 24 18               	movq	0x18(%rsp), %rdx
 335c359: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 335c35e: 48 89 c7                     	movq	%rax, %rdi
 335c361: 48 89 54 24 70               	movq	%rdx, 0x70(%rsp)
 335c366: eb c3                        	jmp	0x335c32b <NimoExSLScreenLinux::onVisibleChanged(bool)+0x4ab>
 335c368: e8 23 e8 0e fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 335c36d: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 335c372: 49 83 c5 10                  	addq	$0x10, %r13
 335c376: 48 89 c3                     	movq	%rax, %rbx
 335c379: 4c 39 ef                     	cmpq	%r13, %rdi
 335c37c: 0f 84 bf fe ff ff            	je	0x335c241 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3c1>
 335c382: e8 29 eb 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 335c387: e9 b5 fe ff ff               	jmp	0x335c241 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3c1>
 335c38c: 48 89 c3                     	movq	%rax, %rbx
 335c38f: e9 c4 fe ff ff               	jmp	0x335c258 <NimoExSLScreenLinux::onVisibleChanged(bool)+0x3d8>
 335c394: 66 90                        	nop
 335c396: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000335c3a0 <NimoExSLScreenLinux::SetFullModeFromPlugin(QString const&, short)>:
 335c3a0: 48 83 ec 18                  	subq	$0x18, %rsp
 335c3a4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 335c3ad: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 335c3b2: 31 c0                        	xorl	%eax, %eax
 335c3b4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 335c3b9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 335c3c2: 75 05                        	jne	0x335c3c9 <NimoExSLScreenLinux::SetFullModeFromPlugin(QString const&, short)+0x29>
 335c3c4: 48 83 c4 18                  	addq	$0x18, %rsp
 335c3c8: c3                           	retq
 335c3c9: e8 c2 e7 0e fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 335c3ce: 66 90                        	nop

000000000335c3d0 <NimoExSLScreenLinux::ChangeCard(int)>:
 335c3d0: 48 83 ec 18                  	subq	$0x18, %rsp
 335c3d4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 335c3dd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 335c3e2: 31 c0                        	xorl	%eax, %eax
 335c3e4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 335c3e9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 335c3f2: 75 05                        	jne	0x335c3f9 <NimoExSLScreenLinux::ChangeCard(int)+0x29>
 335c3f4: 48 83 c4 18                  	addq	$0x18, %rsp
 335c3f8: c3                           	retq
 335c3f9: e8 92 e7 0e fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 335c3fe: 66 90                        	nop

000000000335c400 <NimoExSLScreenLinux::getShareSurface()>:
 335c400: 41 57                        	pushq	%r15
 335c402: 41 56                        	pushq	%r14
 335c404: 41 55                        	pushq	%r13
 335c406: 41 54                        	pushq	%r12
 335c408: 55                           	pushq	%rbp
 335c409: 53                           	pushq	%rbx
 335c40a: 48 89 fb                     	movq	%rdi, %rbx
 335c40d: 48 83 ec 78                  	subq	$0x78, %rsp
 335c411: 48 8b bf 88 00 00 00         	movq	0x88(%rdi), %rdi
 335c418: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 335c421: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 335c426: 31 c0                        	xorl	%eax, %eax
 335c428: 48 8b 07                     	movq	(%rdi), %rax
 335c42b: 48 8b 40 30                  	movq	0x30(%rax), %rax
 335c42f: 48 3b 05 42 24 35 04         	cmpq	0x4352442(%rip), %rax   # 0x76ae878 <_GLOBAL_OFFSET_TABLE_+0x5610>
 335c436: 75 78                        	jne	0x335c4b0 <NimoExSLScreenLinux::getShareSurface()+0xb0>
 335c438: 8b 47 0c                     	movl	0xc(%rdi), %eax
 335c43b: 85 c0                        	testl	%eax, %eax
 335c43d: 74 4d                        	je	0x335c48c <NimoExSLScreenLinux::getShareSurface()+0x8c>
 335c43f: 48 8b bb 80 01 00 00         	movq	0x180(%rbx), %rdi
 335c446: 48 8d 6c 24 40               	leaq	0x40(%rsp), %rbp
 335c44b: 48 85 ff                     	testq	%rdi, %rdi
 335c44e: 74 68                        	je	0x335c4b8 <NimoExSLScreenLinux::getShareSurface()+0xb8>
 335c450: 48 8d 05 c9 ea ff ff         	leaq	-0x1537(%rip), %rax     # 0x335af20 <std::_Function_handler<void (ivi_share*), NimoExSLScreenLinux::getShareSurface()::'lambda'(ivi_share*)>::_M_invoke(std::_Any_data const&, ivi_share*&&)>
 335c457: 48 89 ee                     	movq	%rbp, %rsi
 335c45a: 48 89 5c 24 40               	movq	%rbx, 0x40(%rsp)
 335c45f: 48 89 44 24 58               	movq	%rax, 0x58(%rsp)
 335c464: 48 8d 05 45 e7 ff ff         	leaq	-0x18bb(%rip), %rax     # 0x335abb0 <std::_Function_base::_Base_manager<NimoExSLScreenLinux::getShareSurface()::'lambda'(ivi_share*)>::_M_manager(std::_Any_data&, std::_Any_data const&, std::_Manager_operation)>
 335c46b: 48 89 44 24 50               	movq	%rax, 0x50(%rsp)
 335c470: e8 0b 00 06 00               	callq	0x33bc480 <IVIShareControl::fetchIviShare(std::function<void (ivi_share*)> const&)>
 335c475: 48 8b 44 24 50               	movq	0x50(%rsp), %rax
 335c47a: 48 85 c0                     	testq	%rax, %rax
 335c47d: 74 0d                        	je	0x335c48c <NimoExSLScreenLinux::getShareSurface()+0x8c>
 335c47f: ba 03 00 00 00               	movl	$0x3, %edx
 335c484: 48 89 ee                     	movq	%rbp, %rsi
 335c487: 48 89 ef                     	movq	%rbp, %rdi
 335c48a: ff d0                        	callq	*%rax
 335c48c: 48 8b 44 24 68               	movq	0x68(%rsp), %rax
 335c491: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 335c49a: 0f 85 33 02 00 00            	jne	0x335c6d3 <NimoExSLScreenLinux::getShareSurface()+0x2d3>
 335c4a0: 48 83 c4 78                  	addq	$0x78, %rsp
 335c4a4: 5b                           	popq	%rbx
 335c4a5: 5d                           	popq	%rbp
 335c4a6: 41 5c                        	popq	%r12
 335c4a8: 41 5d                        	popq	%r13
 335c4aa: 41 5e                        	popq	%r14
 335c4ac: 41 5f                        	popq	%r15
 335c4ae: c3                           	retq
 335c4af: 90                           	nop
 335c4b0: ff d0                        	callq	*%rax
 335c4b2: eb 87                        	jmp	0x335c43b <NimoExSLScreenLinux::getShareSurface()+0x3b>
 335c4b4: 0f 1f 40 00                  	nopl	(%rax)
 335c4b8: 48 8b 35 61 17 35 04         	movq	0x4351761(%rip), %rsi   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 335c4bf: bf 28 00 00 00               	movl	$0x28, %edi
 335c4c4: e8 f7 13 0f fe               	callq	0x144d8c0 <_ZnwmRKSt9nothrow_t@plt>
 335c4c9: 48 85 c0                     	testq	%rax, %rax
 335c4cc: 49 89 c4                     	movq	%rax, %r12
 335c4cf: 74 08                        	je	0x335c4d9 <NimoExSLScreenLinux::getShareSurface()+0xd9>
 335c4d1: 48 89 c7                     	movq	%rax, %rdi
 335c4d4: e8 e7 fb 05 00               	callq	0x33bc0c0 <IVIShareControl::IVIShareControl()>
 335c4d9: 4c 8d 6c 24 20               	leaq	0x20(%rsp), %r13
 335c4de: 31 d2                        	xorl	%edx, %edx
 335c4e0: 48 c7 44 24 18 44 00 00 00   	movq	$0x44, 0x18(%rsp)
 335c4e9: 48 8d 6c 24 40               	leaq	0x40(%rsp), %rbp
 335c4ee: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 335c4f2: 4c 89 ef                     	movq	%r13, %rdi
 335c4f5: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 335c4fa: 48 8d 44 24 18               	leaq	0x18(%rsp), %rax
 335c4ff: 48 89 c6                     	movq	%rax, %rsi
