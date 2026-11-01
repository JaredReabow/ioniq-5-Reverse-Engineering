
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

0000000003361df0 <NimoExSLScreenLinux::onForeground(bool, bool)>:
 3361df0: 41 57                        	pushq	%r15
 3361df2: 41 56                        	pushq	%r14
 3361df4: 31 d2                        	xorl	%edx, %edx
 3361df6: 41 55                        	pushq	%r13
 3361df8: 41 54                        	pushq	%r12
 3361dfa: 4c 8d 67 28                  	leaq	0x28(%rdi), %r12
 3361dfe: 55                           	pushq	%rbp
 3361dff: 53                           	pushq	%rbx
 3361e00: 41 89 f5                     	movl	%esi, %r13d
 3361e03: 48 89 fb                     	movq	%rdi, %rbx
 3361e06: 40 0f b6 f6                  	movzbl	%sil, %esi
 3361e0a: 4c 89 e7                     	movq	%r12, %rdi
 3361e0d: 48 81 ec b8 00 00 00         	subq	$0xb8, %rsp
 3361e14: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 3361e1d: 48 89 84 24 a8 00 00 00      	movq	%rax, 0xa8(%rsp)
 3361e25: 31 c0                        	xorl	%eax, %eax
 3361e27: e8 74 f4 00 00               	callq	0x33712a0 <NimoExSLScreen::onForeground(bool, bool)>
 3361e2c: 84 c0                        	testb	%al, %al
 3361e2e: 89 c5                        	movl	%eax, %ebp
 3361e30: 74 46                        	je	0x3361e78 <NimoExSLScreenLinux::onForeground(bool, bool)+0x88>
 3361e32: 8b 43 34                     	movl	0x34(%rbx), %eax
 3361e35: 8d 50 ff                     	leal	-0x1(%rax), %edx
 3361e38: 83 fa 01                     	cmpl	$0x1, %edx
 3361e3b: 76 6b                        	jbe	0x3361ea8 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb8>
 3361e3d: 83 f8 04                     	cmpl	$0x4, %eax
 3361e40: 74 66                        	je	0x3361ea8 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb8>
 3361e42: 83 f8 09                     	cmpl	$0x9, %eax
 3361e45: 0f 94 c2                     	sete	%dl
 3361e48: 83 f8 06                     	cmpl	$0x6, %eax
 3361e4b: 0f 94 c0                     	sete	%al
 3361e4e: 08 c2                        	orb	%al, %dl
 3361e50: 74 26                        	je	0x3361e78 <NimoExSLScreenLinux::onForeground(bool, bool)+0x88>
 3361e52: 45 84 ed                     	testb	%r13b, %r13b
 3361e55: 74 21                        	je	0x3361e78 <NimoExSLScreenLinux::onForeground(bool, bool)+0x88>
 3361e57: e8 b4 e8 8a fe               	callq	0x1c10710 <SessionInteraction::getInstance()>
 3361e5c: 80 b8 48 02 00 00 00         	cmpb	$0x0, 0x248(%rax)
 3361e63: 0f 85 4f 04 00 00            	jne	0x33622b8 <NimoExSLScreenLinux::onForeground(bool, bool)+0x4c8>
 3361e69: 83 7b 34 06                  	cmpl	$0x6, 0x34(%rbx)
 3361e6d: 0f 84 b5 00 00 00            	je	0x3361f28 <NimoExSLScreenLinux::onForeground(bool, bool)+0x138>
 3361e73: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 3361e78: 48 8b 8c 24 a8 00 00 00      	movq	0xa8(%rsp), %rcx
 3361e80: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 3361e89: 89 e8                        	movl	%ebp, %eax
 3361e8b: 0f 85 61 0c 00 00            	jne	0x3362af2 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd02>
 3361e91: 48 81 c4 b8 00 00 00         	addq	$0xb8, %rsp
 3361e98: 5b                           	popq	%rbx
 3361e99: 5d                           	popq	%rbp
 3361e9a: 41 5c                        	popq	%r12
 3361e9c: 41 5d                        	popq	%r13
 3361e9e: 41 5e                        	popq	%r14
 3361ea0: 41 5f                        	popq	%r15
 3361ea2: c3                           	retq
 3361ea3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 3361ea8: 31 f6                        	xorl	%esi, %esi
 3361eaa: 4c 89 e7                     	movq	%r12, %rdi
 3361ead: e8 de 78 00 00               	callq	0x3369790 <NimoExSLScreen::setRequestNaviHide(bool)>
 3361eb2: 45 84 ed                     	testb	%r13b, %r13b
 3361eb5: 0f 84 8d 03 00 00            	je	0x3362248 <NimoExSLScreenLinux::onForeground(bool, bool)+0x458>
 3361ebb: 8b 43 34                     	movl	0x34(%rbx), %eax
 3361ebe: 83 f8 01                     	cmpl	$0x1, %eax
 3361ec1: 0f 84 59 04 00 00            	je	0x3362320 <NimoExSLScreenLinux::onForeground(bool, bool)+0x530>
 3361ec7: 83 f8 04                     	cmpl	$0x4, %eax
 3361eca: 0f 84 b0 03 00 00            	je	0x3362280 <NimoExSLScreenLinux::onForeground(bool, bool)+0x490>
 3361ed0: e8 3b e8 8a fe               	callq	0x1c10710 <SessionInteraction::getInstance()>
 3361ed5: 80 b8 48 02 00 00 00         	cmpb	$0x0, 0x248(%rax)
 3361edc: 0f 85 ee 02 00 00            	jne	0x33621d0 <NimoExSLScreenLinux::onForeground(bool, bool)+0x3e0>
 3361ee2: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 3361ee6: 41 83 f9 01                  	cmpl	$0x1, %r9d
 3361eea: 0f 84 10 04 00 00            	je	0x3362300 <NimoExSLScreenLinux::onForeground(bool, bool)+0x510>
 3361ef0: 4c 8d 05 1b 62 d5 02         	leaq	0x2d5621b(%rip), %r8    # 0x60b8112 <CPersistenceComm::Initialize()::__func__+0x128a>
 3361ef7: 48 8d 15 3a 65 d5 02         	leaq	0x2d5653a(%rip), %rdx   # 0x60b8438 <NimoExSLScreenLinux::onForeground(bool, bool)::__func__>
 3361efe: 48 8d 35 db 4f d5 02         	leaq	0x2d54fdb(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 3361f05: b9 f2 00 00 00               	movl	$0xf2, %ecx
 3361f0a: bf 01 00 00 00               	movl	$0x1, %edi
 3361f0f: 31 c0                        	xorl	%eax, %eax
 3361f11: e8 1a de 4a ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 3361f16: 48 89 df                     	movq	%rbx, %rdi
 3361f19: e8 02 b3 0e fe               	callq	0x144d220 <_ZN7QWindow4showEv@plt>
 3361f1e: e9 55 ff ff ff               	jmp	0x3361e78 <NimoExSLScreenLinux::onForeground(bool, bool)+0x88>
 3361f23: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 3361f28: 4c 8d 05 51 5a d5 02         	leaq	0x2d55a51(%rip), %r8    # 0x60b7980 <CPersistenceComm::Initialize()::__func__+0xaf8>
 3361f2f: 48 8d 15 02 65 d5 02         	leaq	0x2d56502(%rip), %rdx   # 0x60b8438 <NimoExSLScreenLinux::onForeground(bool, bool)::__func__>
 3361f36: 48 8d 35 a3 4f d5 02         	leaq	0x2d54fa3(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 3361f3d: 4c 8d ac 24 80 00 00 00      	leaq	0x80(%rsp), %r13
 3361f45: 31 c0                        	xorl	%eax, %eax
 3361f47: b9 0a 01 00 00               	movl	$0x10a, %ecx            # imm = 0x10A
 3361f4c: bf 01 00 00 00               	movl	$0x1, %edi
 3361f51: e8 da dd 4a ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 3361f56: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 3361f5a: 48 b9 6f 6e 46 6f 72 65 67 72	movabsq	$0x726765726f466e6f, %rcx # imm = 0x726765726F466E6F
 3361f64: bf 90 01 00 00               	movl	$0x190, %edi            # imm = 0x190
 3361f69: 48 89 8c 24 90 00 00 00      	movq	%rcx, 0x90(%rsp)
 3361f71: 48 89 84 24 80 00 00 00      	movq	%rax, 0x80(%rsp)
 3361f79: 48 8b 05 a0 bc 34 04         	movq	0x434bca0(%rip), %rax   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 3361f80: 41 c7 45 18 6f 75 6e 64      	movl	$0x646e756f, 0x18(%r13) # imm = 0x646E756F
 3361f88: 48 c7 84 24 88 00 00 00 0c 00 00 00  	movq	$0xc, 0x88(%rsp)
 3361f94: c6 84 24 9c 00 00 00 00      	movb	$0x0, 0x9c(%rsp)
 3361f9c: 48 89 c6                     	movq	%rax, %rsi
 3361f9f: 48 89 44 24 10               	movq	%rax, 0x10(%rsp)
 3361fa4: e8 17 b9 0e fe               	callq	0x144d8c0 <_ZnwmRKSt9nothrow_t@plt>
 3361fa9: 48 85 c0                     	testq	%rax, %rax
 3361fac: 49 89 c4                     	movq	%rax, %r12
 3361faf: 0f 84 e3 00 00 00            	je	0x3362098 <NimoExSLScreenLinux::onForeground(bool, bool)+0x2a8>
 3361fb5: c7 40 08 08 00 00 00         	movl	$0x8, 0x8(%rax)
 3361fbc: c7 40 0c 00 00 00 00         	movl	$0x0, 0xc(%rax)
 3361fc3: 48 8d 40 20                  	leaq	0x20(%rax), %rax
 3361fc7: 4d 8d 7c 24 50               	leaq	0x50(%r12), %r15
 3361fcc: 49 c7 44 24 18 00 00 00 00   	movq	$0x0, 0x18(%r12)
 3361fd5: 41 c6 44 24 20 00            	movb	$0x0, 0x20(%r12)
 3361fdb: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
 3361fe0: 49 89 44 24 10               	movq	%rax, 0x10(%r12)
 3361fe5: 48 8d 05 d4 df 19 04         	leaq	0x419dfd4(%rip), %rax   # 0x74fffc0 <vtable for ExSLNotifyEvent>
 3361fec: 41 c7 44 24 30 a9 00 00 00   	movl	$0xa9, 0x30(%r12)
 3361ff5: 41 c7 44 24 34 ff ff ff ff   	movl	$0xffffffff, 0x34(%r12) # imm = 0xFFFFFFFF
 3361ffe: 41 c7 44 24 38 ff ff ff ff   	movl	$0xffffffff, 0x38(%r12) # imm = 0xFFFFFFFF
 3362007: 4d 89 7c 24 40               	movq	%r15, 0x40(%r12)
 336200c: 48 83 c0 10                  	addq	$0x10, %rax
 3362010: 66 83 3d 0a a1 31 03 00      	cmpw	$0x0, 0x331a10a(%rip)   # 0x667c122 <typeinfo name for CRampManager+0x186a>
 3362018: 49 89 04 24                  	movq	%rax, (%r12)
 336201c: 0f 84 24 0a 00 00            	je	0x3362a46 <NimoExSLScreenLinux::onForeground(bool, bool)+0xc56>
 3362022: bb 02 00 00 00               	movl	$0x2, %ebx
 3362027: 48 8d 15 f2 a0 31 03         	leaq	0x331a0f2(%rip), %rdx   # 0x667c120 <typeinfo name for CRampManager+0x1868>
 336202e: eb 03                        	jmp	0x3362033 <NimoExSLScreenLinux::onForeground(bool, bool)+0x243>
 3362030: 48 89 c3                     	movq	%rax, %rbx
 3362033: 66 83 7c 1a 02 00            	cmpw	$0x0, 0x2(%rdx,%rbx)
 3362039: 48 8d 43 02                  	leaq	0x2(%rbx), %rax
 336203d: 75 f1                        	jne	0x3362030 <NimoExSLScreenLinux::onForeground(bool, bool)+0x240>
 336203f: 49 89 de                     	movq	%rbx, %r14
 3362042: 4c 89 ff                     	movq	%r15, %rdi
 3362045: 49 d1 fe                     	sarq	%r14
 3362048: 49 83 fe 07                  	cmpq	$0x7, %r14
 336204c: 4c 89 74 24 08               	movq	%r14, 0x8(%rsp)
 3362051: 0f 87 71 03 00 00            	ja	0x33623c8 <NimoExSLScreenLinux::onForeground(bool, bool)+0x5d8>
 3362057: 49 83 fe 01                  	cmpq	$0x1, %r14
 336205b: 0f 84 2a 03 00 00            	je	0x336238b <NimoExSLScreenLinux::onForeground(bool, bool)+0x59b>
 3362061: 48 8d 35 ba a0 31 03         	leaq	0x331a0ba(%rip), %rsi   # 0x667c122 <typeinfo name for CRampManager+0x186a>
 3362068: 48 89 da                     	movq	%rbx, %rdx
 336206b: e8 20 bc 0e fe               	callq	0x144dc90 <memcpy@plt>
 3362070: 49 8b 7c 24 40               	movq	0x40(%r12), %rdi
 3362075: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 336207a: 49 89 44 24 48               	movq	%rax, 0x48(%r12)
 336207f: 31 c0                        	xorl	%eax, %eax
 3362081: 66 89 04 1f                  	movw	%ax, (%rdi,%rbx)
 3362085: 49 8d 7c 24 68               	leaq	0x68(%r12), %rdi
 336208a: 41 c7 44 24 60 00 00 00 00   	movl	$0x0, 0x60(%r12)
 3362093: e8 b8 6d 27 ff               	callq	0x25d8e50 <ExSLVariant::ExSLVariant()>
 3362098: 4c 8d 74 24 60               	leaq	0x60(%rsp), %r14
 336209d: 48 8d 74 24 38               	leaq	0x38(%rsp), %rsi
 33620a2: 31 d2                        	xorl	%edx, %edx
 33620a4: 48 c7 44 24 38 44 00 00 00   	movq	$0x44, 0x38(%rsp)
 33620ad: 49 8d 46 10                  	leaq	0x10(%r14), %rax
 33620b1: 4c 89 f7                     	movq	%r14, %rdi
 33620b4: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 33620b9: e8 b2 b1 0e fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 33620be: 48 8b 54 24 38               	movq	0x38(%rsp), %rdx
 33620c3: 48 b9 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rcx # imm = 0x2E2E2F2E2E2F2E2E
 33620cd: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 33620d2: 45 31 c9                     	xorl	%r9d, %r9d
 33620d5: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 33620db: 4c 89 f6                     	movq	%r14, %rsi
 33620de: bf 00 20 00 00               	movl	$0x2000, %edi           # imm = 0x2000
 33620e3: 48 89 54 24 70               	movq	%rdx, 0x70(%rsp)
 33620e8: 48 89 08                     	movq	%rcx, (%rax)
 33620eb: 48 b9 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rcx # imm = 0x76614E2F6372732F
 33620f5: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 33620f9: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 3362103: c7 40 40 2e 63 70 70         	movl	$0x7070632e, 0x40(%rax) # imm = 0x7070632E
 336210a: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 336210e: 48 b9 4e 69 6d 6f 2f 46 72 61	movabsq	$0x6172462f6f6d694e, %rcx # imm = 0x6172462F6F6D694E
 3362118: 48 89 48 18                  	movq	%rcx, 0x18(%rax)
 336211c: 48 b9 6d 65 77 6f 72 6b 2f 4c	movabsq	$0x4c2f6b726f77656d, %rcx # imm = 0x4C2F6B726F77656D
 3362126: 48 89 48 20                  	movq	%rcx, 0x20(%rax)
 336212a: 48 b9 69 6e 75 78 2f 4e 69 6d	movabsq	$0x6d694e2f78756e69, %rcx # imm = 0x6D694E2F78756E69
 3362134: 48 89 48 28                  	movq	%rcx, 0x28(%rax)
 3362138: 48 b9 6f 45 78 53 4c 53 63 72	movabsq	$0x7263534c5378456f, %rcx # imm = 0x7263534C5378456F
 3362142: 48 89 48 30                  	movq	%rcx, 0x30(%rax)
 3362146: 48 b9 65 65 6e 4c 69 6e 75 78	movabsq	$0x78756e694c6e6565, %rcx # imm = 0x78756E694C6E6565
 3362150: 48 89 48 38                  	movq	%rcx, 0x38(%rax)
 3362154: 48 8b 44 24 38               	movq	0x38(%rsp), %rax
 3362159: 4c 89 e1                     	movq	%r12, %rcx
 336215c: 48 8b 54 24 60               	movq	0x60(%rsp), %rdx
 3362161: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 3362166: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 336216a: ba 0b 01 00 00               	movl	$0x10b, %edx            # imm = 0x10B
 336216f: e8 4c 63 5c fe               	callq	0x19284c0 <ExSLNotifyEvent* ExSLNewTemplate<ExSLNotifyEvent>(unsigned short, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, unsigned short, ExSLNotifyEvent*, unsigned int, bool)>
 3362174: 48 89 c3                     	movq	%rax, %rbx
 3362177: e8 44 2f 4b ff               	callq	0x28150c0 <ExSLEventHandler::getInstance()>
 336217c: 4d 89 e8                     	movq	%r13, %r8
 336217f: b9 03 00 00 00               	movl	$0x3, %ecx
 3362184: 48 89 da                     	movq	%rbx, %rdx
 3362187: be 01 00 00 00               	movl	$0x1, %esi
 336218c: 48 89 c7                     	movq	%rax, %rdi
 336218f: e8 1c 3c 4b ff               	callq	0x2815db0 <ExSLEventHandler::addEvent_external(ecScreenId, ExSLEventBase*, ecEventRun, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>)>
 3362194: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 3362199: 49 83 c6 10                  	addq	$0x10, %r14
 336219d: 4c 39 f7                     	cmpq	%r14, %rdi
 33621a0: 74 05                        	je	0x33621a7 <NimoExSLScreenLinux::onForeground(bool, bool)+0x3b7>
 33621a2: e8 09 8d 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 33621a7: 48 8b bc 24 80 00 00 00      	movq	0x80(%rsp), %rdi
 33621af: 49 83 c5 10                  	addq	$0x10, %r13
 33621b3: 4c 39 ef                     	cmpq	%r13, %rdi
 33621b6: 0f 84 bc fc ff ff            	je	0x3361e78 <NimoExSLScreenLinux::onForeground(bool, bool)+0x88>
 33621bc: e8 ef 8c 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 33621c1: e9 b2 fc ff ff               	jmp	0x3361e78 <NimoExSLScreenLinux::onForeground(bool, bool)+0x88>
 33621c6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 33621d0: e8 3b e5 8a fe               	callq	0x1c10710 <SessionInteraction::getInstance()>
 33621d5: be 01 00 00 00               	movl	$0x1, %esi
 33621da: 48 89 c7                     	movq	%rax, %rdi
 33621dd: e8 2e f7 8a fe               	callq	0x1c11910 <SessionInteraction::getPrevApp(unsigned short)>
 33621e2: 66 83 f8 01                  	cmpw	$0x1, %ax
 33621e6: 0f 84 ae 01 00 00            	je	0x336239a <NimoExSLScreenLinux::onForeground(bool, bool)+0x5aa>
 33621ec: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 33621f0: 4c 8d 05 59 57 d5 02         	leaq	0x2d55759(%rip), %r8    # 0x60b7950 <CPersistenceComm::Initialize()::__func__+0xac8>
 33621f7: 48 8d 15 3a 62 d5 02         	leaq	0x2d5623a(%rip), %rdx   # 0x60b8438 <NimoExSLScreenLinux::onForeground(bool, bool)::__func__>
 33621fe: 48 8d 35 db 4c d5 02         	leaq	0x2d54cdb(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 3362205: 31 c0                        	xorl	%eax, %eax
 3362207: b9 e0 00 00 00               	movl	$0xe0, %ecx
 336220c: bf 01 00 00 00               	movl	$0x1, %edi
 3362211: e8 1a db 4a ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 3362216: be 01 00 00 00               	movl	$0x1, %esi
 336221b: 4c 89 e7                     	movq	%r12, %rdi
 336221e: e8 8d f1 00 00               	callq	0x33713b0 <NimoExSLScreen::onRender(bool)>
 3362223: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 3362227: 41 83 f9 01                  	cmpl	$0x1, %r9d
 336222b: 0f 85 bf fc ff ff            	jne	0x3361ef0 <NimoExSLScreenLinux::onForeground(bool, bool)+0x100>
 3362231: be 01 00 00 00               	movl	$0x1, %esi
 3362236: 4c 89 e7                     	movq	%r12, %rdi
 3362239: e8 72 f1 00 00               	callq	0x33713b0 <NimoExSLScreen::onRender(bool)>
 336223e: e9 9f fc ff ff               	jmp	0x3361ee2 <NimoExSLScreenLinux::onForeground(bool, bool)+0xf2>
 3362243: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 3362248: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 336224c: 4c 8d 05 db 5e d5 02         	leaq	0x2d55edb(%rip), %r8    # 0x60b812e <CPersistenceComm::Initialize()::__func__+0x12a6>
 3362253: 48 8d 15 de 61 d5 02         	leaq	0x2d561de(%rip), %rdx   # 0x60b8438 <NimoExSLScreenLinux::onForeground(bool, bool)::__func__>
 336225a: 48 8d 35 7f 4c d5 02         	leaq	0x2d54c7f(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 3362261: b9 f5 00 00 00               	movl	$0xf5, %ecx
 3362266: bf 01 00 00 00               	movl	$0x1, %edi
 336226b: 31 c0                        	xorl	%eax, %eax
 336226d: e8 be da 4a ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 3362272: 48 89 df                     	movq	%rbx, %rdi
 3362275: e8 d6 af 0e fe               	callq	0x144d250 <_ZN7QWindow4hideEv@plt>
 336227a: e9 f9 fb ff ff               	jmp	0x3361e78 <NimoExSLScreenLinux::onForeground(bool, bool)+0x88>
 336227f: 90                           	nop
 3362280: 8b 83 90 00 00 00            	movl	0x90(%rbx), %eax
 3362286: 83 e0 fd                     	andl	$-0x3, %eax
 3362289: 83 f8 01                     	cmpl	$0x1, %eax
 336228c: 0f 85 3e fc ff ff            	jne	0x3361ed0 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe0>
 3362292: e8 19 57 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 3362297: 41 b8 04 00 00 00            	movl	$0x4, %r8d
 336229d: 31 c9                        	xorl	%ecx, %ecx
 336229f: 31 d2                        	xorl	%edx, %edx
 33622a1: be 01 00 00 00               	movl	$0x1, %esi
 33622a6: 48 89 c7                     	movq	%rax, %rdi
 33622a9: e8 02 5d 87 ff               	callq	0x2bd7fb0 <CAppPluginComm::requestFullMode(bool, bool, bool, ecScreenId)>
 33622ae: e9 1d fc ff ff               	jmp	0x3361ed0 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe0>
 33622b3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 33622b8: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 33622bc: 4c 8d 05 8d 56 d5 02         	leaq	0x2d5568d(%rip), %r8    # 0x60b7950 <CPersistenceComm::Initialize()::__func__+0xac8>
 33622c3: 48 8d 15 6e 61 d5 02         	leaq	0x2d5616e(%rip), %rdx   # 0x60b8438 <NimoExSLScreenLinux::onForeground(bool, bool)::__func__>
 33622ca: 48 8d 35 0f 4c d5 02         	leaq	0x2d54c0f(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 33622d1: 31 c0                        	xorl	%eax, %eax
 33622d3: b9 fc 00 00 00               	movl	$0xfc, %ecx
 33622d8: bf 01 00 00 00               	movl	$0x1, %edi
 33622dd: e8 4e da 4a ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33622e2: 83 7b 34 09                  	cmpl	$0x9, 0x34(%rbx)
 33622e6: 0f 84 0b 01 00 00            	je	0x33623f7 <NimoExSLScreenLinux::onForeground(bool, bool)+0x607>
 33622ec: be 01 00 00 00               	movl	$0x1, %esi
 33622f1: 4c 89 e7                     	movq	%r12, %rdi
 33622f4: e8 b7 f0 00 00               	callq	0x33713b0 <NimoExSLScreen::onRender(bool)>
 33622f9: e9 6b fb ff ff               	jmp	0x3361e69 <NimoExSLScreenLinux::onForeground(bool, bool)+0x79>
 33622fe: 66 90                        	nop
 3362300: e8 db 81 84 fe               	callq	0x1baa4e0 <SystemVariant::GetInstance()>
 3362305: 48 89 c7                     	movq	%rax, %rdi
 3362308: e8 83 b2 84 fe               	callq	0x1bad590 <SystemVariant::getPlatformCode()>
 336230d: 83 f8 09                     	cmpl	$0x9, %eax
 3362310: 0f 84 19 01 00 00            	je	0x336242f <NimoExSLScreenLinux::onForeground(bool, bool)+0x63f>
 3362316: 44 8b 4b 34                  	movl	0x34(%rbx), %r9d
 336231a: e9 d1 fb ff ff               	jmp	0x3361ef0 <NimoExSLScreenLinux::onForeground(bool, bool)+0x100>
 336231f: 90                           	nop
 3362320: e8 bb 81 84 fe               	callq	0x1baa4e0 <SystemVariant::GetInstance()>
 3362325: 48 89 c7                     	movq	%rax, %rdi
 3362328: e8 63 b2 84 fe               	callq	0x1bad590 <SystemVariant::getPlatformCode()>
 336232d: 83 f8 06                     	cmpl	$0x6, %eax
 3362330: 0f 84 6b 01 00 00            	je	0x33624a1 <NimoExSLScreenLinux::onForeground(bool, bool)+0x6b1>
 3362336: 44 8b ab 90 00 00 00         	movl	0x90(%rbx), %r13d
 336233d: 44 89 e8                     	movl	%r13d, %eax
 3362340: 83 e0 fd                     	andl	$-0x3, %eax
 3362343: 83 f8 01                     	cmpl	$0x1, %eax
 3362346: 0f 85 84 fb ff ff            	jne	0x3361ed0 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe0>
 336234c: e8 bf e3 8a fe               	callq	0x1c10710 <SessionInteraction::getInstance()>
 3362351: be 01 00 00 00               	movl	$0x1, %esi
 3362356: 48 89 c7                     	movq	%rax, %rdi
 3362359: e8 82 e9 8a fe               	callq	0x1c10ce0 <SessionInteraction::isSplitScreenEnable(unsigned short)>
 336235e: 41 89 c6                     	movl	%eax, %r14d
 3362361: e8 4a 56 87 ff               	callq	0x2bd79b0 <CAppPluginComm::getInstance()>
 3362366: 31 d2                        	xorl	%edx, %edx
 3362368: 41 83 fd 03                  	cmpl	$0x3, %r13d
 336236c: 41 0f b6 ce                  	movzbl	%r14b, %ecx
 3362370: 0f 94 c2                     	sete	%dl
 3362373: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 3362379: be 01 00 00 00               	movl	$0x1, %esi
 336237e: 48 89 c7                     	movq	%rax, %rdi
 3362381: e8 2a 5c 87 ff               	callq	0x2bd7fb0 <CAppPluginComm::requestFullMode(bool, bool, bool, ecScreenId)>
 3362386: e9 45 fb ff ff               	jmp	0x3361ed0 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe0>
 336238b: 0f b7 05 90 9d 31 03         	movzwl	0x3319d90(%rip), %eax   # 0x667c122 <typeinfo name for CRampManager+0x186a>
 3362392: 66 89 07                     	movw	%ax, (%rdi)
 3362395: e9 db fc ff ff               	jmp	0x3362075 <NimoExSLScreenLinux::onForeground(bool, bool)+0x285>
 336239a: e8 b1 08 81 ff               	callq	0x2b72c50 <createApplicationCreator()>
 336239f: 48 85 c0                     	testq	%rax, %rax
 33623a2: 0f 84 44 fe ff ff            	je	0x33621ec <NimoExSLScreenLinux::onForeground(bool, bool)+0x3fc>
 33623a8: 48 8b 10                     	movq	(%rax), %rdx
 33623ab: 48 89 c7                     	movq	%rax, %rdi
 33623ae: ff 52 20                     	callq	*0x20(%rdx)
 33623b1: 48 85 c0                     	testq	%rax, %rax
 33623b4: 0f 84 32 fe ff ff            	je	0x33621ec <NimoExSLScreenLinux::onForeground(bool, bool)+0x3fc>
 33623ba: 48 8b 10                     	movq	(%rax), %rdx
 33623bd: 48 89 c7                     	movq	%rax, %rdi
 33623c0: ff 52 48                     	callq	*0x48(%rdx)
 33623c3: e9 24 fe ff ff               	jmp	0x33621ec <NimoExSLScreenLinux::onForeground(bool, bool)+0x3fc>
 33623c8: 48 b8 ff ff ff ff ff ff ff 3f	movabsq	$0x3fffffffffffffff, %rax # imm = 0x3FFFFFFFFFFFFFFF
 33623d2: 49 39 c6                     	cmpq	%rax, %r14
 33623d5: 0f 87 96 08 00 00            	ja	0x3362c71 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe81>
 33623db: 4b 8d 7c 36 02               	leaq	0x2(%r14,%r14), %rdi
 33623e0: e8 4b ba 0e fe               	callq	0x144de30 <_Znwm@plt>
 33623e5: 49 89 44 24 40               	movq	%rax, 0x40(%r12)
 33623ea: 4d 89 74 24 50               	movq	%r14, 0x50(%r12)
 33623ef: 48 89 c7                     	movq	%rax, %rdi
 33623f2: e9 60 fc ff ff               	jmp	0x3362057 <NimoExSLScreenLinux::onForeground(bool, bool)+0x267>
 33623f7: 48 8b 7b 48                  	movq	0x48(%rbx), %rdi
 33623fb: 48 8b 07                     	movq	(%rdi), %rax
 33623fe: ff 50 20                     	callq	*0x20(%rax)
 3362401: 48 85 c0                     	testq	%rax, %rax
 3362404: 49 89 c5                     	movq	%rax, %r13
 3362407: 74 14                        	je	0x336241d <NimoExSLScreenLinux::onForeground(bool, bool)+0x62d>
 3362409: 48 8b 00                     	movq	(%rax), %rax
 336240c: 4c 8b 70 40                  	movq	0x40(%rax), %r14
 3362410: e8 4b e5 29 ff               	callq	0x2600960 <getTickCount()>
 3362415: 4c 89 ef                     	movq	%r13, %rdi
 3362418: 89 c6                        	movl	%eax, %esi
 336241a: 41 ff d6                     	callq	*%r14
 336241d: be 01 00 00 00               	movl	$0x1, %esi
 3362422: 4c 89 e7                     	movq	%r12, %rdi
 3362425: e8 86 ef 00 00               	callq	0x33713b0 <NimoExSLScreen::onRender(bool)>
 336242a: e9 bd fe ff ff               	jmp	0x33622ec <NimoExSLScreenLinux::onForeground(bool, bool)+0x4fc>
 336242f: e8 ac 80 84 fe               	callq	0x1baa4e0 <SystemVariant::GetInstance()>
 3362434: 48 89 c7                     	movq	%rax, %rdi
 3362437: e8 14 b2 84 fe               	callq	0x1bad650 <SystemVariant::getRegion()>
 336243c: 83 f8 04                     	cmpl	$0x4, %eax
 336243f: 74 16                        	je	0x3362457 <NimoExSLScreenLinux::onForeground(bool, bool)+0x667>
 3362441: e8 9a 80 84 fe               	callq	0x1baa4e0 <SystemVariant::GetInstance()>
 3362446: 48 89 c7                     	movq	%rax, %rdi
 3362449: e8 02 b2 84 fe               	callq	0x1bad650 <SystemVariant::getRegion()>
 336244e: 83 f8 0b                     	cmpl	$0xb, %eax
 3362451: 0f 85 bf fe ff ff            	jne	0x3362316 <NimoExSLScreenLinux::onForeground(bool, bool)+0x526>
 3362457: e8 b4 e2 8a fe               	callq	0x1c10710 <SessionInteraction::getInstance()>
 336245c: 48 89 c7                     	movq	%rax, %rdi
 336245f: e8 5c f1 8a fe               	callq	0x1c115c0 <SessionInteraction::getEmergencyState()>
 3362464: 8d 50 ff                     	leal	-0x1(%rax), %edx
 3362467: 66 83 fa 02                  	cmpw	$0x2, %dx
 336246b: 76 0a                        	jbe	0x3362477 <NimoExSLScreenLinux::onForeground(bool, bool)+0x687>
 336246d: 66 83 f8 07                  	cmpw	$0x7, %ax
 3362471: 0f 85 9f fe ff ff            	jne	0x3362316 <NimoExSLScreenLinux::onForeground(bool, bool)+0x526>
 3362477: 4c 89 e7                     	movq	%r12, %rdi
 336247a: e8 c1 47 2a ff               	callq	0x2606c40 <ExSLScreen::currentTopSceneId()>
 336247f: 44 0f b7 63 34               	movzwl	0x34(%rbx), %r12d
 3362484: 41 89 c5                     	movl	%eax, %r13d
 3362487: e8 84 e2 8a fe               	callq	0x1c10710 <SessionInteraction::getInstance()>
 336248c: 31 c9                        	xorl	%ecx, %ecx
 336248e: 44 89 ea                     	movl	%r13d, %edx
 3362491: 48 89 c7                     	movq	%rax, %rdi
 3362494: 44 89 e6                     	movl	%r12d, %esi
 3362497: e8 e4 24 8b fe               	callq	0x1c14980 <SessionInteraction::requestSystemEmergency(unsigned short, ecSceneId, bool)>
 336249c: e9 75 fe ff ff               	jmp	0x3362316 <NimoExSLScreenLinux::onForeground(bool, bool)+0x526>
 33624a1: 4c 8d 05 50 54 d5 02         	leaq	0x2d55450(%rip), %r8    # 0x60b78f8 <CPersistenceComm::Initialize()::__func__+0xa70>
 33624a8: 48 8d 15 89 5f d5 02         	leaq	0x2d55f89(%rip), %rdx   # 0x60b8438 <NimoExSLScreenLinux::onForeground(bool, bool)::__func__>
 33624af: 48 8d 35 2a 4a d5 02         	leaq	0x2d54a2a(%rip), %rsi   # 0x60b6ee0 <CPersistenceComm::Initialize()::__func__+0x58>
 33624b6: 4c 8d ac 24 80 00 00 00      	leaq	0x80(%rsp), %r13
 33624be: 31 c0                        	xorl	%eax, %eax
 33624c0: b9 c0 00 00 00               	movl	$0xc0, %ecx
 33624c5: bf 01 00 00 00               	movl	$0x1, %edi
 33624ca: e8 61 d8 4a ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33624cf: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 33624d3: 48 b9 6f 6e 46 6f 72 65 67 72	movabsq	$0x726765726f466e6f, %rcx # imm = 0x726765726F466E6F
 33624dd: bf 90 01 00 00               	movl	$0x190, %edi            # imm = 0x190
 33624e2: 48 89 8c 24 90 00 00 00      	movq	%rcx, 0x90(%rsp)
 33624ea: 48 89 84 24 80 00 00 00      	movq	%rax, 0x80(%rsp)
 33624f2: 48 8b 05 27 b7 34 04         	movq	0x434b727(%rip), %rax   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 33624f9: 41 c7 45 18 6f 75 6e 64      	movl	$0x646e756f, 0x18(%r13) # imm = 0x646E756F
 3362501: 48 c7 84 24 88 00 00 00 0c 00 00 00  	movq	$0xc, 0x88(%rsp)
 336250d: c6 84 24 9c 00 00 00 00      	movb	$0x0, 0x9c(%rsp)
 3362515: 48 89 c6                     	movq	%rax, %rsi
 3362518: 48 89 44 24 10               	movq	%rax, 0x10(%rsp)
 336251d: e8 9e b3 0e fe               	callq	0x144d8c0 <_ZnwmRKSt9nothrow_t@plt>
 3362522: 48 85 c0                     	testq	%rax, %rax
 3362525: 49 89 c7                     	movq	%rax, %r15
 3362528: 0f 84 f1 00 00 00            	je	0x336261f <NimoExSLScreenLinux::onForeground(bool, bool)+0x82f>
 336252e: c7 40 08 08 00 00 00         	movl	$0x8, 0x8(%rax)
 3362535: c7 40 0c 00 00 00 00         	movl	$0x0, 0xc(%rax)
 336253c: 48 8d 40 20                  	leaq	0x20(%rax), %rax
 3362540: 49 c7 47 18 00 00 00 00      	movq	$0x0, 0x18(%r15)
 3362548: 41 c6 47 20 00               	movb	$0x0, 0x20(%r15)
 336254d: 48 89 44 24 28               	movq	%rax, 0x28(%rsp)
 3362552: 49 89 47 10                  	movq	%rax, 0x10(%r15)
 3362556: 48 8d 05 63 da 19 04         	leaq	0x419da63(%rip), %rax   # 0x74fffc0 <vtable for ExSLNotifyEvent>
 336255d: 41 c7 47 30 0f 00 00 00      	movl	$0xf, 0x30(%r15)
 3362565: 41 c7 47 34 00 00 00 00      	movl	$0x0, 0x34(%r15)
 336256d: 41 c7 47 38 ff ff ff ff      	movl	$0xffffffff, 0x38(%r15) # imm = 0xFFFFFFFF
 3362575: 48 83 c0 10                  	addq	$0x10, %rax
 3362579: 66 83 3d a1 9b 31 03 00      	cmpw	$0x0, 0x3319ba1(%rip)   # 0x667c122 <typeinfo name for CRampManager+0x186a>
 3362581: 49 89 07                     	movq	%rax, (%r15)
 3362584: 49 8d 47 50                  	leaq	0x50(%r15), %rax
 3362588: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
 336258d: 49 89 47 40                  	movq	%rax, 0x40(%r15)
 3362591: 0f 84 60 05 00 00            	je	0x3362af7 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd07>
 3362597: 41 be 02 00 00 00            	movl	$0x2, %r14d
 336259d: 48 8d 15 7c 9b 31 03         	leaq	0x3319b7c(%rip), %rdx   # 0x667c120 <typeinfo name for CRampManager+0x1868>
 33625a4: eb 0d                        	jmp	0x33625b3 <NimoExSLScreenLinux::onForeground(bool, bool)+0x7c3>
 33625a6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 33625b0: 49 89 c6                     	movq	%rax, %r14
 33625b3: 66 42 83 7c 32 02 00         	cmpw	$0x0, 0x2(%rdx,%r14)
 33625ba: 49 8d 46 02                  	leaq	0x2(%r14), %rax
 33625be: 75 f0                        	jne	0x33625b0 <NimoExSLScreenLinux::onForeground(bool, bool)+0x7c0>
 33625c0: 4c 89 f0                     	movq	%r14, %rax
 33625c3: 48 8b 7c 24 18               	movq	0x18(%rsp), %rdi
 33625c8: 48 d1 f8                     	sarq	%rax
 33625cb: 48 83 f8 07                  	cmpq	$0x7, %rax
 33625cf: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 33625d4: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 33625d9: 0f 87 da 04 00 00            	ja	0x3362ab9 <NimoExSLScreenLinux::onForeground(bool, bool)+0xcc9>
 33625df: 48 83 7c 24 08 01            	cmpq	$0x1, 0x8(%rsp)
 33625e5: 0f 84 bf 04 00 00            	je	0x3362aaa <NimoExSLScreenLinux::onForeground(bool, bool)+0xcba>
 33625eb: 48 8d 35 30 9b 31 03         	leaq	0x3319b30(%rip), %rsi   # 0x667c122 <typeinfo name for CRampManager+0x186a>
 33625f2: 4c 89 f2                     	movq	%r14, %rdx
 33625f5: e8 96 b6 0e fe               	callq	0x144dc90 <memcpy@plt>
 33625fa: 48 8b 44 24 20               	movq	0x20(%rsp), %rax
 33625ff: 31 d2                        	xorl	%edx, %edx
 3362601: 49 8d 7f 68                  	leaq	0x68(%r15), %rdi
 3362605: 49 89 47 48                  	movq	%rax, 0x48(%r15)
 3362609: 49 8b 47 40                  	movq	0x40(%r15), %rax
 336260d: 66 42 89 14 30               	movw	%dx, (%rax,%r14)
 3362612: 41 c7 47 60 00 00 00 00      	movl	$0x0, 0x60(%r15)
 336261a: e8 31 68 27 ff               	callq	0x25d8e50 <ExSLVariant::ExSLVariant()>
 336261f: 4c 8d 74 24 60               	leaq	0x60(%rsp), %r14
 3362624: 31 d2                        	xorl	%edx, %edx
 3362626: 48 c7 44 24 38 44 00 00 00   	movq	$0x44, 0x38(%rsp)
 336262f: 49 8d 46 10                  	leaq	0x10(%r14), %rax
 3362633: 4c 89 f7                     	movq	%r14, %rdi
 3362636: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 336263b: 48 8d 44 24 38               	leaq	0x38(%rsp), %rax
 3362640: 48 89 c6                     	movq	%rax, %rsi
 3362643: 48 89 44 24 28               	movq	%rax, 0x28(%rsp)
 3362648: e8 23 ac 0e fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 336264d: 48 8b 54 24 38               	movq	0x38(%rsp), %rdx
 3362652: 48 b9 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rcx # imm = 0x2E2E2F2E2E2F2E2E
 336265c: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 3362661: 45 31 c9                     	xorl	%r9d, %r9d
 3362664: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 336266a: 4c 89 f6                     	movq	%r14, %rsi
 336266d: bf 00 20 00 00               	movl	$0x2000, %edi           # imm = 0x2000
 3362672: 48 89 54 24 70               	movq	%rdx, 0x70(%rsp)
 3362677: 48 89 08                     	movq	%rcx, (%rax)
 336267a: 48 b9 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rcx # imm = 0x76614E2F6372732F
 3362684: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 3362688: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 3362692: c7 40 40 2e 63 70 70         	movl	$0x7070632e, 0x40(%rax) # imm = 0x7070632E
 3362699: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 336269d: 48 b9 4e 69 6d 6f 2f 46 72 61	movabsq	$0x6172462f6f6d694e, %rcx # imm = 0x6172462F6F6D694E
 33626a7: 48 89 48 18                  	movq	%rcx, 0x18(%rax)
 33626ab: 48 b9 6d 65 77 6f 72 6b 2f 4c	movabsq	$0x4c2f6b726f77656d, %rcx # imm = 0x4C2F6B726F77656D
 33626b5: 48 89 48 20                  	movq	%rcx, 0x20(%rax)
 33626b9: 48 b9 69 6e 75 78 2f 4e 69 6d	movabsq	$0x6d694e2f78756e69, %rcx # imm = 0x6D694E2F78756E69
 33626c3: 48 89 48 28                  	movq	%rcx, 0x28(%rax)
 33626c7: 48 b9 6f 45 78 53 4c 53 63 72	movabsq	$0x7263534c5378456f, %rcx # imm = 0x7263534C5378456F
 33626d1: 48 89 48 30                  	movq	%rcx, 0x30(%rax)
 33626d5: 48 b9 65 65 6e 4c 69 6e 75 78	movabsq	$0x78756e694c6e6565, %rcx # imm = 0x78756E694C6E6565
 33626df: 48 89 48 38                  	movq	%rcx, 0x38(%rax)
 33626e3: 48 8b 44 24 38               	movq	0x38(%rsp), %rax
 33626e8: 4c 89 f9                     	movq	%r15, %rcx
 33626eb: 48 8b 54 24 60               	movq	0x60(%rsp), %rdx
 33626f0: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 33626f5: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 33626f9: ba c1 00 00 00               	movl	$0xc1, %edx
 33626fe: e8 bd 5d 5c fe               	callq	0x19284c0 <ExSLNotifyEvent* ExSLNewTemplate<ExSLNotifyEvent>(unsigned short, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, unsigned short, ExSLNotifyEvent*, unsigned int, bool)>
 3362703: 49 89 c7                     	movq	%rax, %r15
 3362706: e8 b5 29 4b ff               	callq	0x28150c0 <ExSLEventHandler::getInstance()>
 336270b: 4d 89 e8                     	movq	%r13, %r8
 336270e: b9 04 00 00 00               	movl	$0x4, %ecx
 3362713: 4c 89 fa                     	movq	%r15, %rdx
 3362716: be 05 00 00 00               	movl	$0x5, %esi
 336271b: 48 89 c7                     	movq	%rax, %rdi
 336271e: e8 dd 31 4b ff               	callq	0x2815900 <ExSLEventHandler::addEvent_external(ecEventReceiverId, ExSLEventBase*, ecEventRun, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>)>
 3362723: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 3362728: 49 8d 46 10                  	leaq	0x10(%r14), %rax
 336272c: 48 39 c7                     	cmpq	%rax, %rdi
 336272f: 74 05                        	je	0x3362736 <NimoExSLScreenLinux::onForeground(bool, bool)+0x946>
 3362731: e8 7a 87 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362736: 48 8b bc 24 80 00 00 00      	movq	0x80(%rsp), %rdi
 336273e: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 3362742: 48 39 c7                     	cmpq	%rax, %rdi
 3362745: 74 05                        	je	0x336274c <NimoExSLScreenLinux::onForeground(bool, bool)+0x95c>
 3362747: e8 64 87 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 336274c: 49 8d 46 10                  	leaq	0x10(%r14), %rax
 3362750: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 3362755: 48 b9 6f 6e 46 6f 72 65 67 72	movabsq	$0x726765726f466e6f, %rcx # imm = 0x726765726F466E6F
 336275f: 48 89 4c 24 70               	movq	%rcx, 0x70(%rsp)
 3362764: bf b0 01 00 00               	movl	$0x1b0, %edi            # imm = 0x1B0
 3362769: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 336276e: 41 c7 46 18 6f 75 6e 64      	movl	$0x646e756f, 0x18(%r14) # imm = 0x646E756F
 3362776: 48 c7 44 24 68 0c 00 00 00   	movq	$0xc, 0x68(%rsp)
 336277f: c6 44 24 7c 00               	movb	$0x0, 0x7c(%rsp)
 3362784: e8 37 b1 0e fe               	callq	0x144d8c0 <_ZnwmRKSt9nothrow_t@plt>
 3362789: 48 85 c0                     	testq	%rax, %rax
 336278c: 49 89 c7                     	movq	%rax, %r15
 336278f: 0f 84 a9 00 00 00            	je	0x336283e <NimoExSLScreenLinux::onForeground(bool, bool)+0xa4e>
 3362795: c7 40 08 01 00 00 00         	movl	$0x1, 0x8(%rax)
 336279c: c7 40 0c 00 00 00 00         	movl	$0x0, 0xc(%rax)
 33627a3: 48 8d 40 20                  	leaq	0x20(%rax), %rax
 33627a7: 49 8d bf 80 00 00 00         	leaq	0x80(%r15), %rdi
 33627ae: 49 c7 47 18 00 00 00 00      	movq	$0x0, 0x18(%r15)
 33627b6: 41 c6 47 20 00               	movb	$0x0, 0x20(%r15)
 33627bb: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
 33627c0: 49 89 47 10                  	movq	%rax, 0x10(%r15)
 33627c4: 48 8d 05 15 d6 19 04         	leaq	0x419d615(%rip), %rax   # 0x74ffde0 <vtable for ExSLNaviMethodEvent>
 33627cb: 41 c7 47 30 65 09 00 00      	movl	$0x965, 0x30(%r15)      # imm = 0x965
 33627d3: 49 c7 47 40 00 00 00 00      	movq	$0x0, 0x40(%r15)
 33627db: 41 c6 47 48 00               	movb	$0x0, 0x48(%r15)
 33627e0: 49 c7 47 60 00 00 00 00      	movq	$0x0, 0x60(%r15)
 33627e8: 41 c6 47 68 00               	movb	$0x0, 0x68(%r15)
 33627ed: 48 83 c0 10                  	addq	$0x10, %rax
 33627f1: 41 c7 47 78 ff ff ff ff      	movl	$0xffffffff, 0x78(%r15) # imm = 0xFFFFFFFF
 33627f9: 41 c7 47 7c ff ff ff ff      	movl	$0xffffffff, 0x7c(%r15) # imm = 0xFFFFFFFF
 3362801: 49 89 07                     	movq	%rax, (%r15)
 3362804: 49 8d 47 48                  	leaq	0x48(%r15), %rax
 3362808: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 336280d: 49 89 47 38                  	movq	%rax, 0x38(%r15)
 3362811: 49 8d 47 68                  	leaq	0x68(%r15), %rax
 3362815: 49 89 47 58                  	movq	%rax, 0x58(%r15)
 3362819: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 336281e: e8 2d 66 27 ff               	callq	0x25d8e50 <ExSLVariant::ExSLVariant()>
 3362823: 41 c6 87 a8 01 00 00 00      	movb	$0x0, 0x1a8(%r15)
 336282b: 41 c6 87 a9 01 00 00 00      	movb	$0x0, 0x1a9(%r15)
 3362833: 41 c7 87 ac 01 00 00 00 00 00 00     	movl	$0x0, 0x1ac(%r15)
 336283e: 48 8d 44 24 40               	leaq	0x40(%rsp), %rax
 3362843: 48 8d 74 24 30               	leaq	0x30(%rsp), %rsi
 3362848: 31 d2                        	xorl	%edx, %edx
 336284a: 48 c7 44 24 30 44 00 00 00   	movq	$0x44, 0x30(%rsp)
 3362853: 48 89 c7                     	movq	%rax, %rdi
 3362856: 48 89 44 24 10               	movq	%rax, 0x10(%rsp)
 336285b: 48 8d 44 24 50               	leaq	0x50(%rsp), %rax
 3362860: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 3362865: e8 06 aa 0e fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 336286a: 48 8b 54 24 30               	movq	0x30(%rsp), %rdx
 336286f: 48 b9 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rcx # imm = 0x2E2E2F2E2E2F2E2E
 3362879: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 336287e: c7 40 40 2e 63 70 70         	movl	$0x7070632e, 0x40(%rax) # imm = 0x7070632E
 3362885: 48 89 54 24 50               	movq	%rdx, 0x50(%rsp)
 336288a: 48 89 08                     	movq	%rcx, (%rax)
 336288d: 48 b9 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rcx # imm = 0x76614E2F6372732F
 3362897: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 336289b: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 33628a5: 48 8b 54 24 40               	movq	0x40(%rsp), %rdx
 33628aa: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 33628ae: 48 b9 4e 69 6d 6f 2f 46 72 61	movabsq	$0x6172462f6f6d694e, %rcx # imm = 0x6172462F6F6D694E
 33628b8: 48 89 48 18                  	movq	%rcx, 0x18(%rax)
 33628bc: 48 b9 6d 65 77 6f 72 6b 2f 4c	movabsq	$0x4c2f6b726f77656d, %rcx # imm = 0x4C2F6B726F77656D
 33628c6: 48 89 48 20                  	movq	%rcx, 0x20(%rax)
 33628ca: 48 b9 69 6e 75 78 2f 4e 69 6d	movabsq	$0x6d694e2f78756e69, %rcx # imm = 0x6D694E2F78756E69
 33628d4: 48 89 48 28                  	movq	%rcx, 0x28(%rax)
 33628d8: 48 b9 6f 45 78 53 4c 53 63 72	movabsq	$0x7263534c5378456f, %rcx # imm = 0x7263534C5378456F
 33628e2: 48 89 48 30                  	movq	%rcx, 0x30(%rax)
 33628e6: 48 b9 65 65 6e 4c 69 6e 75 78	movabsq	$0x78756e694c6e6565, %rcx # imm = 0x78756E694C6E6565
 33628f0: 48 89 48 38                  	movq	%rcx, 0x38(%rax)
 33628f4: 48 8b 44 24 30               	movq	0x30(%rsp), %rax
 33628f9: 48 89 44 24 48               	movq	%rax, 0x48(%rsp)
 33628fe: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 3362902: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 3362906: 48 8b 4c 24 48               	movq	0x48(%rsp), %rcx
 336290b: 48 89 84 24 80 00 00 00      	movq	%rax, 0x80(%rsp)
 3362913: 48 8b 44 24 40               	movq	0x40(%rsp), %rax
 3362918: 48 89 cf                     	movq	%rcx, %rdi
 336291b: 48 89 4c 24 08               	movq	%rcx, 0x8(%rsp)
 3362920: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
 3362925: 48 89 c1                     	movq	%rax, %rcx
 3362928: 48 01 f8                     	addq	%rdi, %rax
 336292b: 0f 84 4f 00 00 00            	je	0x3362980 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb90>
 3362931: 48 85 c9                     	testq	%rcx, %rcx
 3362934: 75 4a                        	jne	0x3362980 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb90>
 3362936: 48 8d 3d 0b 21 a0 02         	leaq	0x2a0210b(%rip), %rdi   # 0x5d64a48 <_IO_stdin_used+0x8>
 336293d: e8 de b2 0e fe               	callq	0x144dc20 <_ZSt19__throw_logic_errorPKc@plt>
 3362942: 48 89 c3                     	movq	%rax, %rbx
 3362945: 48 8b 44 24 10               	movq	0x10(%rsp), %rax
 336294a: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 336294f: 48 83 c0 10                  	addq	$0x10, %rax
 3362953: 48 39 c7                     	cmpq	%rax, %rdi
 3362956: 74 05                        	je	0x336295d <NimoExSLScreenLinux::onForeground(bool, bool)+0xb6d>
 3362958: e8 53 85 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 336295d: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 3362962: 49 83 c6 10                  	addq	$0x10, %r14
 3362966: 4c 39 f7                     	cmpq	%r14, %rdi
 3362969: 74 05                        	je	0x3362970 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb80>
 336296b: e8 40 85 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362970: 48 89 df                     	movq	%rbx, %rdi
 3362973: e8 e8 a8 0e fe               	callq	0x144d260 <_Unwind_Resume@plt>
 3362978: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
 3362980: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 3362985: 48 83 f8 0f                  	cmpq	$0xf, %rax
 3362989: 48 89 44 24 38               	movq	%rax, 0x38(%rsp)
 336298e: 0f 87 e8 00 00 00            	ja	0x3362a7c <NimoExSLScreenLinux::onForeground(bool, bool)+0xc8c>
 3362994: 48 83 7c 24 08 01            	cmpq	$0x1, 0x8(%rsp)
 336299a: 0f 85 b9 00 00 00            	jne	0x3362a59 <NimoExSLScreenLinux::onForeground(bool, bool)+0xc69>
 33629a0: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
 33629a5: 49 8d 55 10                  	leaq	0x10(%r13), %rdx
 33629a9: 0f b6 00                     	movzbl	(%rax), %eax
 33629ac: 88 84 24 90 00 00 00         	movb	%al, 0x90(%rsp)
 33629b3: b8 01 00 00 00               	movl	$0x1, %eax
 33629b8: 48 89 84 24 88 00 00 00      	movq	%rax, 0x88(%rsp)
 33629c0: 45 31 c9                     	xorl	%r9d, %r9d
 33629c3: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 33629c7: 41 b8 b0 01 00 00            	movl	$0x1b0, %r8d            # imm = 0x1B0
 33629cd: 4c 89 f9                     	movq	%r15, %rcx
 33629d0: ba c2 00 00 00               	movl	$0xc2, %edx
 33629d5: 4c 89 ee                     	movq	%r13, %rsi
 33629d8: bf 00 20 00 00               	movl	$0x2000, %edi           # imm = 0x2000
 33629dd: e8 ae 63 4a ff               	callq	0x2808d90 <ExSLMemoryNew>
 33629e2: 48 8b bc 24 80 00 00 00      	movq	0x80(%rsp), %rdi
 33629ea: 49 83 c5 10                  	addq	$0x10, %r13
 33629ee: 4c 39 ef                     	cmpq	%r13, %rdi
 33629f1: 74 05                        	je	0x33629f8 <NimoExSLScreenLinux::onForeground(bool, bool)+0xc08>
 33629f3: e8 b8 84 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 33629f8: 44 8b 6b 34                  	movl	0x34(%rbx), %r13d
 33629fc: e8 bf 26 4b ff               	callq	0x28150c0 <ExSLEventHandler::getInstance()>
 3362a01: 4c 89 f1                     	movq	%r14, %rcx
 3362a04: 4c 89 fa                     	movq	%r15, %rdx
 3362a07: 44 89 ee                     	movl	%r13d, %esi
 3362a0a: 48 89 c7                     	movq	%rax, %rdi
 3362a0d: e8 5e 32 4b ff               	callq	0x2815c70 <ExSLEventHandler::addEvent_external(ecScreenId, ExSLEventBase*, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>)>
 3362a12: 48 8b 44 24 10               	movq	0x10(%rsp), %rax
 3362a17: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 3362a1c: 48 83 c0 10                  	addq	$0x10, %rax
 3362a20: 48 39 c7                     	cmpq	%rax, %rdi
 3362a23: 74 05                        	je	0x3362a2a <NimoExSLScreenLinux::onForeground(bool, bool)+0xc3a>
 3362a25: e8 86 84 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362a2a: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 3362a2f: 49 83 c6 10                  	addq	$0x10, %r14
 3362a33: 4c 39 f7                     	cmpq	%r14, %rdi
 3362a36: 0f 84 fa f8 ff ff            	je	0x3362336 <NimoExSLScreenLinux::onForeground(bool, bool)+0x546>
 3362a3c: e8 6f 84 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362a41: e9 f0 f8 ff ff               	jmp	0x3362336 <NimoExSLScreenLinux::onForeground(bool, bool)+0x546>
 3362a46: 4c 89 ff                     	movq	%r15, %rdi
 3362a49: 48 c7 44 24 08 00 00 00 00   	movq	$0x0, 0x8(%rsp)
 3362a52: 31 db                        	xorl	%ebx, %ebx
 3362a54: e9 08 f6 ff ff               	jmp	0x3362061 <NimoExSLScreenLinux::onForeground(bool, bool)+0x271>
 3362a59: 49 8d 7d 10                  	leaq	0x10(%r13), %rdi
 3362a5d: 48 89 c2                     	movq	%rax, %rdx
 3362a60: 48 8b 74 24 18               	movq	0x18(%rsp), %rsi
 3362a65: e8 26 b2 0e fe               	callq	0x144dc90 <memcpy@plt>
 3362a6a: 48 8b 44 24 38               	movq	0x38(%rsp), %rax
 3362a6f: 48 8b 94 24 80 00 00 00      	movq	0x80(%rsp), %rdx
 3362a77: e9 3c ff ff ff               	jmp	0x33629b8 <NimoExSLScreenLinux::onForeground(bool, bool)+0xbc8>
 3362a7c: 48 8b 74 24 28               	movq	0x28(%rsp), %rsi
 3362a81: 31 d2                        	xorl	%edx, %edx
 3362a83: 4c 89 ef                     	movq	%r13, %rdi
 3362a86: e8 e5 a7 0e fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 3362a8b: 48 8b 54 24 38               	movq	0x38(%rsp), %rdx
 3362a90: 48 89 84 24 80 00 00 00      	movq	%rax, 0x80(%rsp)
 3362a98: 48 89 c7                     	movq	%rax, %rdi
 3362a9b: 48 89 94 24 90 00 00 00      	movq	%rdx, 0x90(%rsp)
 3362aa3: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 3362aa8: eb b6                        	jmp	0x3362a60 <NimoExSLScreenLinux::onForeground(bool, bool)+0xc70>
 3362aaa: 0f b7 05 71 96 31 03         	movzwl	0x3319671(%rip), %eax   # 0x667c122 <typeinfo name for CRampManager+0x186a>
 3362ab1: 66 89 07                     	movw	%ax, (%rdi)
 3362ab4: e9 41 fb ff ff               	jmp	0x33625fa <NimoExSLScreenLinux::onForeground(bool, bool)+0x80a>
 3362ab9: 48 b8 ff ff ff ff ff ff ff 3f	movabsq	$0x3fffffffffffffff, %rax # imm = 0x3FFFFFFFFFFFFFFF
 3362ac3: 48 39 44 24 08               	cmpq	%rax, 0x8(%rsp)
 3362ac8: 0f 87 b6 00 00 00            	ja	0x3362b84 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd94>
 3362ace: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 3362ad3: 48 8d 7c 00 02               	leaq	0x2(%rax,%rax), %rdi
 3362ad8: e8 53 b3 0e fe               	callq	0x144de30 <_Znwm@plt>
 3362add: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
 3362ae2: 49 89 47 40                  	movq	%rax, 0x40(%r15)
 3362ae6: 48 89 c7                     	movq	%rax, %rdi
 3362ae9: 49 89 4f 50                  	movq	%rcx, 0x50(%r15)
 3362aed: e9 ed fa ff ff               	jmp	0x33625df <NimoExSLScreenLinux::onForeground(bool, bool)+0x7ef>
 3362af2: e8 99 80 0e fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 3362af7: 48 8b 7c 24 18               	movq	0x18(%rsp), %rdi
 3362afc: 45 31 f6                     	xorl	%r14d, %r14d
 3362aff: 48 c7 44 24 20 00 00 00 00   	movq	$0x0, 0x20(%rsp)
 3362b08: e9 de fa ff ff               	jmp	0x33625eb <NimoExSLScreenLinux::onForeground(bool, bool)+0x7fb>
 3362b0d: 48 89 c3                     	movq	%rax, %rbx
 3362b10: 48 8b bc 24 80 00 00 00      	movq	0x80(%rsp), %rdi
 3362b18: 49 83 c5 10                  	addq	$0x10, %r13
 3362b1c: 4c 39 ef                     	cmpq	%r13, %rdi
 3362b1f: 0f 85 46 fe ff ff            	jne	0x336296b <NimoExSLScreenLinux::onForeground(bool, bool)+0xb7b>
 3362b25: e9 46 fe ff ff               	jmp	0x3362970 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb80>
 3362b2a: 48 89 c3                     	movq	%rax, %rbx
 3362b2d: e9 2b fe ff ff               	jmp	0x336295d <NimoExSLScreenLinux::onForeground(bool, bool)+0xb6d>
 3362b32: 48 8b bc 24 80 00 00 00      	movq	0x80(%rsp), %rdi
 3362b3a: 49 83 c5 10                  	addq	$0x10, %r13
 3362b3e: 48 89 c3                     	movq	%rax, %rbx
 3362b41: 4c 39 ef                     	cmpq	%r13, %rdi
 3362b44: 0f 84 fb fd ff ff            	je	0x3362945 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb55>
 3362b4a: e8 61 83 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362b4f: e9 f1 fd ff ff               	jmp	0x3362945 <NimoExSLScreenLinux::onForeground(bool, bool)+0xb55>
 3362b54: 48 89 c3                     	movq	%rax, %rbx
 3362b57: 48 8d 05 62 d2 19 04         	leaq	0x419d262(%rip), %rax   # 0x74ffdc0 <vtable for ExSLEventBase>
 3362b5e: 49 8b 7f 10                  	movq	0x10(%r15), %rdi
 3362b62: 48 83 c0 10                  	addq	$0x10, %rax
 3362b66: 48 39 7c 24 28               	cmpq	%rdi, 0x28(%rsp)
 3362b6b: 49 89 07                     	movq	%rax, (%r15)
 3362b6e: 74 05                        	je	0x3362b75 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd85>
 3362b70: e8 3b 83 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362b75: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 3362b7a: 4c 89 ff                     	movq	%r15, %rdi
 3362b7d: e8 0e c0 0e fe               	callq	0x144eb90 <_ZdlPvRKSt9nothrow_t@plt>
 3362b82: eb 8c                        	jmp	0x3362b10 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd20>
 3362b84: 48 8d 3d f9 1f a0 02         	leaq	0x2a01ff9(%rip), %rdi   # 0x5d64b84 <_IO_stdin_used+0x144>
 3362b8b: e8 c0 83 0e fe               	callq	0x144af50 <_ZSt20__throw_length_errorPKc@plt>
 3362b90: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 3362b95: 49 83 c6 10                  	addq	$0x10, %r14
 3362b99: 48 89 c3                     	movq	%rax, %rbx
 3362b9c: 4c 39 f7                     	cmpq	%r14, %rdi
 3362b9f: 0f 84 6b ff ff ff            	je	0x3362b10 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd20>
 3362ba5: e8 06 83 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362baa: e9 61 ff ff ff               	jmp	0x3362b10 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd20>
 3362baf: 49 8b 7f 58                  	movq	0x58(%r15), %rdi
 3362bb3: 48 3b 7c 24 20               	cmpq	0x20(%rsp), %rdi
 3362bb8: 48 89 c3                     	movq	%rax, %rbx
 3362bbb: 74 05                        	je	0x3362bc2 <NimoExSLScreenLinux::onForeground(bool, bool)+0xdd2>
 3362bbd: e8 ee 82 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362bc2: 49 8b 7f 38                  	movq	0x38(%r15), %rdi
 3362bc6: 48 39 7c 24 08               	cmpq	%rdi, 0x8(%rsp)
 3362bcb: 74 05                        	je	0x3362bd2 <NimoExSLScreenLinux::onForeground(bool, bool)+0xde2>
 3362bcd: e8 de 82 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362bd2: 48 8d 05 e7 d1 19 04         	leaq	0x419d1e7(%rip), %rax   # 0x74ffdc0 <vtable for ExSLEventBase>
 3362bd9: 49 8b 7f 10                  	movq	0x10(%r15), %rdi
 3362bdd: 48 83 c0 10                  	addq	$0x10, %rax
 3362be1: 48 39 7c 24 18               	cmpq	%rdi, 0x18(%rsp)
 3362be6: 49 89 07                     	movq	%rax, (%r15)
 3362be9: 74 05                        	je	0x3362bf0 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe00>
 3362beb: e8 c0 82 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362bf0: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 3362bf5: 4c 89 ff                     	movq	%r15, %rdi
 3362bf8: e8 93 bf 0e fe               	callq	0x144eb90 <_ZdlPvRKSt9nothrow_t@plt>
 3362bfd: e9 5b fd ff ff               	jmp	0x336295d <NimoExSLScreenLinux::onForeground(bool, bool)+0xb6d>
 3362c02: 49 8b 7c 24 40               	movq	0x40(%r12), %rdi
 3362c07: 48 89 c3                     	movq	%rax, %rbx
 3362c0a: 49 39 ff                     	cmpq	%rdi, %r15
 3362c0d: 74 05                        	je	0x3362c14 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe24>
 3362c0f: e8 9c 82 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362c14: 48 8d 05 a5 d1 19 04         	leaq	0x419d1a5(%rip), %rax   # 0x74ffdc0 <vtable for ExSLEventBase>
 3362c1b: 49 8b 7c 24 10               	movq	0x10(%r12), %rdi
 3362c20: 48 83 c0 10                  	addq	$0x10, %rax
 3362c24: 48 39 7c 24 18               	cmpq	%rdi, 0x18(%rsp)
 3362c29: 49 89 04 24                  	movq	%rax, (%r12)
 3362c2d: 74 05                        	je	0x3362c34 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe44>
 3362c2f: e8 7c 82 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362c34: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 3362c39: 4c 89 e7                     	movq	%r12, %rdi
 3362c3c: e8 4f bf 0e fe               	callq	0x144eb90 <_ZdlPvRKSt9nothrow_t@plt>
 3362c41: e9 ca fe ff ff               	jmp	0x3362b10 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd20>
 3362c46: 49 8b 7f 40                  	movq	0x40(%r15), %rdi
 3362c4a: 48 39 7c 24 18               	cmpq	%rdi, 0x18(%rsp)
 3362c4f: 48 89 c3                     	movq	%rax, %rbx
 3362c52: 0f 84 ff fe ff ff            	je	0x3362b57 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd67>
 3362c58: e8 53 82 0e fe               	callq	0x144aeb0 <_ZdlPv@plt>
 3362c5d: e9 f5 fe ff ff               	jmp	0x3362b57 <NimoExSLScreenLinux::onForeground(bool, bool)+0xd67>
 3362c62: e9 29 ff ff ff               	jmp	0x3362b90 <NimoExSLScreenLinux::onForeground(bool, bool)+0xda0>
 3362c67: e9 a1 fe ff ff               	jmp	0x3362b0d <NimoExSLScreenLinux::onForeground(bool, bool)+0xd1d>
 3362c6c: 48 89 c3                     	movq	%rax, %rbx
 3362c6f: eb a3                        	jmp	0x3362c14 <NimoExSLScreenLinux::onForeground(bool, bool)+0xe24>
 3362c71: 48 8d 3d 0c 1f a0 02         	leaq	0x2a01f0c(%rip), %rdi   # 0x5d64b84 <_IO_stdin_used+0x144>
 3362c78: e8 d3 82 0e fe               	callq	0x144af50 <_ZSt20__throw_length_errorPKc@plt>
 3362c7d: 0f 1f 00                     	nopl	(%rax)

0000000003362c80 <non-virtual thunk to NimoExSLScreenLinux::onForeground(bool, bool)>:
 3362c80: 48 83 ef 28                  	subq	$0x28, %rdi
 3362c84: e9 67 f1 ff ff               	jmp	0x3361df0 <NimoExSLScreenLinux::onForeground(bool, bool)>
 3362c89: 90                           	nop
 3362c8a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
