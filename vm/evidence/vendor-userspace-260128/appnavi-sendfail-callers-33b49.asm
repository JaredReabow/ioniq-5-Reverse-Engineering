
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

00000000033b4330 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)>:
 33b4500: f8                           	clc
 33b4501: 4c 01 e8                     	addq	%r13, %rax
 33b4504: 74 1a                        	je	0x33b4520 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x1f0>
 33b4506: 4d 85 ff                     	testq	%r15, %r15
 33b4509: 75 15                        	jne	0x33b4520 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x1f0>
 33b450b: 48 8d 3d 36 05 9b 02         	leaq	0x29b0536(%rip), %rdi   # 0x5d64a48 <_IO_stdin_used+0x8>
 33b4512: e8 09 97 09 fe               	callq	0x144dc20 <_ZSt19__throw_logic_errorPKc@plt>
 33b4517: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 33b4520: 49 83 fd 0f                  	cmpq	$0xf, %r13
 33b4524: 4c 89 6c 24 28               	movq	%r13, 0x28(%rsp)
 33b4529: 0f 87 e1 00 00 00            	ja	0x33b4610 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x2e0>
 33b452f: 49 83 fd 01                  	cmpq	$0x1, %r13
 33b4533: 0f 85 b7 00 00 00            	jne	0x33b45f0 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x2c0>
 33b4539: 41 0f b6 07                  	movzbl	(%r15), %eax
 33b453d: 48 8d 55 10                  	leaq	0x10(%rbp), %rdx
 33b4541: 88 44 24 60                  	movb	%al, 0x60(%rsp)
 33b4545: b8 01 00 00 00               	movl	$0x1, %eax
 33b454a: 48 89 44 24 58               	movq	%rax, 0x58(%rsp)
 33b454f: 45 31 c9                     	xorl	%r9d, %r9d
 33b4552: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 33b4556: 41 b8 10 00 00 00            	movl	$0x10, %r8d
 33b455c: 4c 89 f1                     	movq	%r14, %rcx
 33b455f: ba ac 00 00 00               	movl	$0xac, %edx
 33b4564: 48 89 ee                     	movq	%rbp, %rsi
 33b4567: bf 10 20 00 00               	movl	$0x2010, %edi           # imm = 0x2010
 33b456c: e8 1f 48 45 ff               	callq	0x2808d90 <ExSLMemoryNew>
 33b4571: 48 8b 7c 24 50               	movq	0x50(%rsp), %rdi
 33b4576: 48 83 c5 10                  	addq	$0x10, %rbp
 33b457a: 48 39 ef                     	cmpq	%rbp, %rdi
 33b457d: 74 05                        	je	0x33b4584 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x254>
 33b457f: e8 2c 69 09 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 33b4584: 48 8b 7c 24 30               	movq	0x30(%rsp), %rdi
 33b4589: 48 8b 04 24                  	movq	(%rsp), %rax
 33b458d: 49 83 c4 10                  	addq	$0x10, %r12
 33b4591: 4c 39 e7                     	cmpq	%r12, %rdi
 33b4594: 4c 89 b0 b8 00 00 00         	movq	%r14, 0xb8(%rax)
 33b459b: 74 05                        	je	0x33b45a2 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x272>
 33b459d: e8 0e 69 09 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 33b45a2: e8 99 6f 09 fe               	callq	0x144b540 <_ZN7QThread13currentThreadEv@plt>
 33b45a7: be 04 00 00 00               	movl	$0x4, %esi
 33b45ac: 48 89 c7                     	movq	%rax, %rdi
 33b45af: e8 ec 91 09 fe               	callq	0x144d7a0 <_ZN7QThread11setPriorityENS_8PriorityE@plt>
 33b45b4: 48 89 df                     	movq	%rbx, %rdi
 33b45b7: e8 14 7f 09 fe               	callq	0x144c4d0 <_ZN14QSurfaceFormatD1Ev@plt>
 33b45bc: 48 8b 5c 24 78               	movq	0x78(%rsp), %rbx
 33b45c1: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
 33b45ca: b8 01 00 00 00               	movl	$0x1, %eax
 33b45cf: 0f 85 84 00 00 00            	jne	0x33b4659 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x329>
 33b45d5: 48 81 c4 88 00 00 00         	addq	$0x88, %rsp
 33b45dc: 5b                           	popq	%rbx
 33b45dd: 5d                           	popq	%rbp
 33b45de: 41 5c                        	popq	%r12
 33b45e0: 41 5d                        	popq	%r13
 33b45e2: 41 5e                        	popq	%r14
 33b45e4: 41 5f                        	popq	%r15
 33b45e6: c3                           	retq
 33b45e7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 33b45f0: 48 8d 7d 10                  	leaq	0x10(%rbp), %rdi
 33b45f4: 4c 89 ea                     	movq	%r13, %rdx
 33b45f7: 4c 89 fe                     	movq	%r15, %rsi
 33b45fa: e8 91 96 09 fe               	callq	0x144dc90 <memcpy@plt>
 33b45ff: 48 8b 44 24 28               	movq	0x28(%rsp), %rax
 33b4604: 48 8b 54 24 50               	movq	0x50(%rsp), %rdx
 33b4609: e9 3c ff ff ff               	jmp	0x33b454a <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x21a>
 33b460e: 66 90                        	nop
 33b4610: 48 8d 74 24 28               	leaq	0x28(%rsp), %rsi
 33b4615: 31 d2                        	xorl	%edx, %edx
 33b4617: 48 89 ef                     	movq	%rbp, %rdi
 33b461a: e8 51 8c 09 fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 33b461f: 48 8b 54 24 28               	movq	0x28(%rsp), %rdx
 33b4624: 48 89 44 24 50               	movq	%rax, 0x50(%rsp)
 33b4629: 48 89 c7                     	movq	%rax, %rdi
 33b462c: 48 89 54 24 60               	movq	%rdx, 0x60(%rsp)
 33b4631: eb c1                        	jmp	0x33b45f4 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x2c4>
 33b4633: 48 89 c5                     	movq	%rax, %rbp
 33b4636: 48 8b 7c 24 30               	movq	0x30(%rsp), %rdi
 33b463b: 49 83 c4 10                  	addq	$0x10, %r12
 33b463f: 4c 39 e7                     	cmpq	%r12, %rdi
 33b4642: 74 05                        	je	0x33b4649 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x319>
 33b4644: e8 67 68 09 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 33b4649: 48 89 df                     	movq	%rbx, %rdi
 33b464c: e8 7f 7e 09 fe               	callq	0x144c4d0 <_ZN14QSurfaceFormatD1Ev@plt>
 33b4651: 48 89 ef                     	movq	%rbp, %rdi
 33b4654: e8 07 8c 09 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 33b4659: e8 32 65 09 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 33b465e: 48 8b 7c 24 50               	movq	0x50(%rsp), %rdi
 33b4663: 48 83 c5 10                  	addq	$0x10, %rbp
 33b4667: 49 89 c5                     	movq	%rax, %r13
 33b466a: 48 39 ef                     	cmpq	%rbp, %rdi
 33b466d: 74 05                        	je	0x33b4674 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x344>
 33b466f: e8 3c 68 09 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 33b4674: 4c 89 ed                     	movq	%r13, %rbp
 33b4677: eb bd                        	jmp	0x33b4636 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x306>
 33b4679: 48 8b 35 a0 95 2f 04         	movq	0x42f95a0(%rip), %rsi   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 33b4680: 4c 89 f7                     	movq	%r14, %rdi
 33b4683: 48 89 c5                     	movq	%rax, %rbp
 33b4686: e8 05 a5 09 fe               	callq	0x144eb90 <_ZdlPvRKSt9nothrow_t@plt>
 33b468b: eb bc                        	jmp	0x33b4649 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x319>
 33b468d: 48 89 c5                     	movq	%rax, %rbp
 33b4690: eb b7                        	jmp	0x33b4649 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)+0x319>
 33b4692: 0f 1f 40 00                  	nopl	(%rax)
 33b4696: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000033b46a0 <non-virtual thunk to NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)>:
 33b46a0: 48 83 ef 10                  	subq	$0x10, %rdi
 33b46a4: e9 87 fc ff ff               	jmp	0x33b4330 <NimoExSLApplicationLinux::onCreatePlatformApplication(int, char**)>
 33b46a9: 90                           	nop
 33b46aa: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000033b46b0 <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>:
 33b46b0: 55                           	pushq	%rbp
 33b46b1: 53                           	pushq	%rbx
 33b46b2: 4c 8d 05 d1 fb d0 02         	leaq	0x2d0fbd1(%rip), %r8    # 0x60c428a <typeinfo name for NimoExSLNaviCircuitList+0x48a>
 33b46b9: 48 8d 15 40 fd d0 02         	leaq	0x2d0fd40(%rip), %rdx   # 0x60c4400 <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)::__func__>
 33b46c0: 48 89 f5                     	movq	%rsi, %rbp
 33b46c3: 48 8d 35 a6 f7 d0 02         	leaq	0x2d0f7a6(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b46ca: 48 83 ec 18                  	subq	$0x18, %rsp
 33b46ce: b9 c3 00 00 00               	movl	$0xc3, %ecx
 33b46d3: 48 89 fb                     	movq	%rdi, %rbx
 33b46d6: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 33b46df: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 33b46e4: 31 c0                        	xorl	%eax, %eax
 33b46e6: bf 05 00 00 00               	movl	$0x5, %edi
 33b46eb: e8 40 b6 45 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33b46f0: 48 89 df                     	movq	%rbx, %rdi
 33b46f3: e8 98 fa ff ff               	callq	0x33b4190 <NimoExSLApplicationLinux::registerFontResource()>
 33b46f8: 48 8d 3d 31 60 ff ff         	leaq	-0x9fcf(%rip), %rdi     # 0x33aa730 <qmlConsoleLogHandler(QtMsgType, QMessageLogContext const&, QString const&)>
 33b46ff: e8 cc 74 09 fe               	callq	0x144bbd0 <_Z22qInstallMessageHandlerPFv9QtMsgTypeRK18QMessageLogContextRK7QStringE@plt>
 33b4704: 48 8d 7b 10                  	leaq	0x10(%rbx), %rdi
 33b4708: 48 89 ee                     	movq	%rbp, %rsi
 33b470b: e8 60 74 7c ff               	callq	0x2b7bb70 <NimoExSLApplication::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>
 33b4710: 83 f8 01                     	cmpl	$0x1, %eax
 33b4713: 7e 18                        	jle	0x33b472d <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x7d>
 33b4715: e8 56 5a ff ff               	callq	0x33aa170 <createNativeDisplayType()>
 33b471a: 48 89 c7                     	movq	%rax, %rdi
 33b471d: e8 0e 76 e4 ff               	callq	0x31fbd30 <ExSLEglFunction::initialize(void*)>
 33b4722: 89 c2                        	movl	%eax, %edx
 33b4724: b8 02 00 00 00               	movl	$0x2, %eax
 33b4729: 84 d2                        	testb	%dl, %dl
 33b472b: 74 1b                        	je	0x33b4748 <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x98>
 33b472d: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
 33b4732: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 33b473b: 75 38                        	jne	0x33b4775 <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xc5>
 33b473d: 48 83 c4 18                  	addq	$0x18, %rsp
 33b4741: 5b                           	popq	%rbx
 33b4742: 5d                           	popq	%rbp
 33b4743: c3                           	retq
 33b4744: 0f 1f 40 00                  	nopl	(%rax)
 33b4748: 4c 8d 05 61 fb d0 02         	leaq	0x2d0fb61(%rip), %r8    # 0x60c42b0 <typeinfo name for NimoExSLNaviCircuitList+0x4b0>
 33b474f: 48 8d 15 aa fc d0 02         	leaq	0x2d0fcaa(%rip), %rdx   # 0x60c4400 <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)::__func__>
 33b4756: 48 8d 35 13 f7 d0 02         	leaq	0x2d0f713(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b475d: 31 c0                        	xorl	%eax, %eax
 33b475f: b9 cc 00 00 00               	movl	$0xcc, %ecx
 33b4764: bf 03 00 00 00               	movl	$0x3, %edi
 33b4769: e8 42 af 45 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 33b476e: b8 01 00 00 00               	movl	$0x1, %eax
 33b4773: eb b8                        	jmp	0x33b472d <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x7d>
 33b4775: e8 16 64 09 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 33b477a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000033b4780 <non-virtual thunk to NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>:
 33b4780: 48 83 ef 10                  	subq	$0x10, %rdi
 33b4784: e9 27 ff ff ff               	jmp	0x33b46b0 <NimoExSLApplicationLinux::onInitializePlatform(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>
 33b4789: 90                           	nop
 33b478a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000033b4790 <NimoExSLApplicationLinux::onInitializeDone()>:
 33b4790: 55                           	pushq	%rbp
 33b4791: 53                           	pushq	%rbx
 33b4792: 48 83 c7 10                  	addq	$0x10, %rdi
 33b4796: 48 83 ec 18                  	subq	$0x18, %rsp
 33b479a: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 33b47a3: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 33b47a8: 31 c0                        	xorl	%eax, %eax
 33b47aa: e8 61 32 7c ff               	callq	0x2b77a10 <NimoExSLApplication::onInitializeDone()>
 33b47af: e8 cc f1 86 ff               	callq	0x2c23980 <CAppFuncComm::GetInstance()>
 33b47b4: 48 89 c7                     	movq	%rax, %rdi
 33b47b7: e8 b4 6e 86 ff               	callq	0x2c1b670 <CAppFuncComm::WriteNaviVersionInfo()>
 33b47bc: e8 bf f1 86 ff               	callq	0x2c23980 <CAppFuncComm::GetInstance()>
 33b47c1: 48 89 c7                     	movq	%rax, %rdi
 33b47c4: e8 57 77 86 ff               	callq	0x2c1bf20 <CAppFuncComm::WriteNaviVersionInfoToDID()>
 33b47c9: e8 42 d5 7e ff               	callq	0x2ba1d10 <CMicomManagerComm::GetInstance()>
 33b47ce: 48 89 c7                     	movq	%rax, %rdi
 33b47d1: e8 fa a8 7f ff               	callq	0x2baf0d0 <CMicomManagerComm::AskNaviAppData()>
 33b47d6: e8 35 d5 7e ff               	callq	0x2ba1d10 <CMicomManagerComm::GetInstance()>
 33b47db: 48 89 c7                     	movq	%rax, %rdi
 33b47de: e8 ad ab 7f ff               	callq	0x2baf390 <CMicomManagerComm::AskFactoryModeInfo()>
 33b47e3: e8 28 d5 7e ff               	callq	0x2ba1d10 <CMicomManagerComm::GetInstance()>
 33b47e8: 48 89 c7                     	movq	%rax, %rdi
 33b47eb: e8 d0 5f 7f ff               	callq	0x2baa7c0 <CMicomManagerComm::AskADASHandShakingMessage()>
 33b47f0: e8 1b d5 7e ff               	callq	0x2ba1d10 <CMicomManagerComm::GetInstance()>
 33b47f5: 48 89 c7                     	movq	%rax, %rdi
 33b47f8: e8 33 e9 7e ff               	callq	0x2ba3130 <CMicomManagerComm::AskVolumeInfo()>
 33b47fd: e8 0e d5 7e ff               	callq	0x2ba1d10 <CMicomManagerComm::GetInstance()>
 33b4802: 48 89 c7                     	movq	%rax, %rdi
 33b4805: e8 f6 f5 7e ff               	callq	0x2ba3e00 <CMicomManagerComm::AskSysAutomaticBrightness()>
 33b480a: e8 11 f9 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b480f: 48 89 c7                     	movq	%rax, %rdi
 33b4812: e8 89 f6 83 ff               	callq	0x2bf3ea0 <CAppManagerComm::RequestInitStatus()>
 33b4817: e8 64 97 80 ff               	callq	0x2bbdf80 <CAutoMount::GetInstance()>
 33b481c: 48 89 c7                     	movq	%rax, %rdi
 33b481f: e8 dc a4 80 ff               	callq	0x2bbed00 <CAutoMount::RequestMountedList()>
 33b4824: e8 f7 f8 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4829: 48 89 c7                     	movq	%rax, %rdi
 33b482c: e8 ff f1 84 ff               	callq	0x2c03a30 <CAppManagerComm::SetCurrentMountDegreeToExSL()>
 33b4831: e8 ea f8 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4836: 48 89 c7                     	movq	%rax, %rdi
 33b4839: e8 92 c9 84 ff               	callq	0x2c011d0 <CAppManagerComm::SetCurrentTimeFormatToExSL()>
 33b483e: e8 dd f8 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4843: 48 89 c7                     	movq	%rax, %rdi
 33b4846: e8 95 c7 84 ff               	callq	0x2c00fe0 <CAppManagerComm::SetCurrentRearMonitorTypeToExSL()>
 33b484b: e8 d0 f8 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4850: 48 89 c7                     	movq	%rax, %rdi
 33b4853: e8 58 35 84 ff               	callq	0x2bf7db0 <CAppManagerComm::RequestRegistrationAllAppIDToAppManager()>
 33b4858: e8 e3 74 f9 ff               	callq	0x334bd40 <CPersistenceComm::GetInstance()>
 33b485d: 48 89 c7                     	movq	%rax, %rdi
 33b4860: e8 4b 40 fa ff               	callq	0x33588b0 <CPersistenceComm::loadPersistenceDataSetting()>
 33b4865: 48 8d 05 74 18 ad 04         	leaq	0x4ad1874(%rip), %rax   # 0x7e860e0 <g_NaviLaunched>
 33b486c: c6 00 01                     	movb	$0x1, (%rax)
 33b486f: e8 ec c0 24 ff               	callq	0x2600960 <getTickCount()>
 33b4874: 48 8d 15 85 51 33 04         	leaq	0x4335185(%rip), %rdx   # 0x76e9a00 <g_startTime>
 33b487b: 48 8d 2d 9e 11 ad 04         	leaq	0x4ad119e(%rip), %rbp   # 0x7e85a20 <g_firstTimeHideByWM>
 33b4882: 48 83 ec 08                  	subq	$0x8, %rsp
 33b4886: 48 8d 35 e3 f5 d0 02         	leaq	0x2d0f5e3(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b488d: 4c 8d 05 0c f7 d0 02         	leaq	0x2d0f70c(%rip), %r8    # 0x60c3fa0 <typeinfo name for NimoExSLNaviCircuitList+0x1a0>
 33b4894: b9 19 01 00 00               	movl	$0x119, %ecx            # imm = 0x119
 33b4899: bf 05 00 00 00               	movl	$0x5, %edi
 33b489e: 2b 02                        	subl	(%rdx), %eax
 33b48a0: 48 8d 15 39 fb d0 02         	leaq	0x2d0fb39(%rip), %rdx   # 0x60c43e0 <NimoExSLApplicationLinux::onInitializeDone()::__func__>
 33b48a7: 50                           	pushq	%rax
 33b48a8: 44 0f b6 4d 00               	movzbl	(%rbp), %r9d
 33b48ad: 89 c3                        	movl	%eax, %ebx
 33b48af: 31 c0                        	xorl	%eax, %eax
 33b48b1: e8 7a b4 45 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33b48b6: 80 7d 00 00                  	cmpb	$0x0, (%rbp)
 33b48ba: 59                           	popq	%rcx
 33b48bb: 5e                           	popq	%rsi
 33b48bc: 75 52                        	jne	0x33b4910 <NimoExSLApplicationLinux::onInitializeDone()+0x180>
 33b48be: 81 fb d7 59 00 00            	cmpl	$0x59d7, %ebx           # imm = 0x59D7
 33b48c4: 77 4a                        	ja	0x33b4910 <NimoExSLApplicationLinux::onInitializeDone()+0x180>
 33b48c6: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 33b48cb: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 33b48d4: 0f 85 8c 00 00 00            	jne	0x33b4966 <NimoExSLApplicationLinux::onInitializeDone()+0x1d6>
 33b48da: 48 83 c4 18                  	addq	$0x18, %rsp
 33b48de: 4c 8d 05 b4 f9 d0 02         	leaq	0x2d0f9b4(%rip), %r8    # 0x60c4299 <typeinfo name for NimoExSLNaviCircuitList+0x499>
 33b48e5: 48 8d 15 f4 fa d0 02         	leaq	0x2d0faf4(%rip), %rdx   # 0x60c43e0 <NimoExSLApplicationLinux::onInitializeDone()::__func__>
 33b48ec: 5b                           	popq	%rbx
 33b48ed: 5d                           	popq	%rbp
 33b48ee: 48 8d 35 7b f5 d0 02         	leaq	0x2d0f57b(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b48f5: b9 1e 01 00 00               	movl	$0x11e, %ecx            # imm = 0x11E
 33b48fa: bf 01 00 00 00               	movl	$0x1, %edi
 33b48ff: 31 c0                        	xorl	%eax, %eax
 33b4901: e9 2a b4 45 ff               	jmp	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33b4906: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 33b4910: e8 0b f8 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4915: 48 89 c7                     	movq	%rax, %rdi
 33b4918: e8 93 41 85 ff               	callq	0x2c08ab0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()>
 33b491d: 48 83 ec 08                  	subq	$0x8, %rsp
 33b4921: 48 8d 15 b8 fa d0 02         	leaq	0x2d0fab8(%rip), %rdx   # 0x60c43e0 <NimoExSLApplicationLinux::onInitializeDone()::__func__>
 33b4928: 4c 8d 05 99 f6 d0 02         	leaq	0x2d0f699(%rip), %r8    # 0x60c3fc8 <typeinfo name for NimoExSLNaviCircuitList+0x1c8>
 33b492f: 53                           	pushq	%rbx
 33b4930: 44 0f b6 4d 00               	movzbl	(%rbp), %r9d
 33b4935: 48 8d 35 34 f5 d0 02         	leaq	0x2d0f534(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b493c: 31 c0                        	xorl	%eax, %eax
 33b493e: b9 1c 01 00 00               	movl	$0x11c, %ecx            # imm = 0x11C
 33b4943: bf 01 00 00 00               	movl	$0x1, %edi
 33b4948: e8 e3 b3 45 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33b494d: 58                           	popq	%rax
 33b494e: 5a                           	popq	%rdx
 33b494f: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 33b4954: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 33b495d: 75 07                        	jne	0x33b4966 <NimoExSLApplicationLinux::onInitializeDone()+0x1d6>
 33b495f: 48 83 c4 18                  	addq	$0x18, %rsp
 33b4963: 5b                           	popq	%rbx
 33b4964: 5d                           	popq	%rbp
 33b4965: c3                           	retq
 33b4966: e8 25 62 09 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 33b496b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

00000000033b4970 <non-virtual thunk to NimoExSLApplicationLinux::onInitializeDone()>:
 33b4970: 48 83 ef 10                  	subq	$0x10, %rdi
 33b4974: e9 17 fe ff ff               	jmp	0x33b4790 <NimoExSLApplicationLinux::onInitializeDone()>
 33b4979: 90                           	nop
 33b497a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000033b4980 <NimoExSLApplicationLinux::onUpdatePlatform()>:
 33b4980: 48 83 ec 18                  	subq	$0x18, %rsp
 33b4984: 48 83 c7 10                  	addq	$0x10, %rdi
 33b4988: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 33b4991: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 33b4996: 31 c0                        	xorl	%eax, %eax
 33b4998: e8 03 31 7c ff               	callq	0x2b77aa0 <NimoExSLApplication::onUpdatePlatform()>
 33b499d: e8 6e bd 85 fe               	callq	0x1c10710 <SessionInteraction::getInstance()>
 33b49a2: 80 b8 48 02 00 00 00         	cmpb	$0x0, 0x248(%rax)
 33b49a9: 74 09                        	je	0x33b49b4 <NimoExSLApplicationLinux::onUpdatePlatform()+0x34>
 33b49ab: 80 3d 68 17 ad 04 00         	cmpb	$0x0, 0x4ad1768(%rip)   # 0x7e8611a <NimoExSLApplicationLinux::onUpdatePlatform()::naviStateStabilized>
 33b49b2: 74 24                        	je	0x33b49d8 <NimoExSLApplicationLinux::onUpdatePlatform()+0x58>
 33b49b4: e8 67 c8 24 ff               	callq	0x2601220 <ExSLThreadMonitor::instance()>
 33b49b9: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 33b49be: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 33b49c7: 75 4b                        	jne	0x33b4a14 <NimoExSLApplicationLinux::onUpdatePlatform()+0x94>
 33b49c9: 48 89 c7                     	movq	%rax, %rdi
 33b49cc: 48 83 c4 18                  	addq	$0x18, %rsp
 33b49d0: e9 9b dc 24 ff               	jmp	0x2602670 <ExSLThreadMonitor::SetLiveSignalMainThread()>
 33b49d5: 0f 1f 00                     	nopl	(%rax)
 33b49d8: 4c 8d 05 41 f6 d0 02         	leaq	0x2d0f641(%rip), %r8    # 0x60c4020 <typeinfo name for NimoExSLNaviCircuitList+0x220>
 33b49df: 48 8d 15 da f9 d0 02         	leaq	0x2d0f9da(%rip), %rdx   # 0x60c43c0 <NimoExSLApplicationLinux::onUpdatePlatform()::__func__>
 33b49e6: 48 8d 35 83 f4 d0 02         	leaq	0x2d0f483(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b49ed: b9 2d 01 00 00               	movl	$0x12d, %ecx            # imm = 0x12D
 33b49f2: bf 01 00 00 00               	movl	$0x1, %edi
 33b49f7: 31 c0                        	xorl	%eax, %eax
 33b49f9: c6 05 1a 17 ad 04 01         	movb	$0x1, 0x4ad171a(%rip)   # 0x7e8611a <NimoExSLApplicationLinux::onUpdatePlatform()::naviStateStabilized>
 33b4a00: e8 2b b3 45 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33b4a05: e8 16 f7 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4a0a: 48 89 c7                     	movq	%rax, %rdi
 33b4a0d: e8 9e 40 85 ff               	callq	0x2c08ab0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()>
 33b4a12: eb a0                        	jmp	0x33b49b4 <NimoExSLApplicationLinux::onUpdatePlatform()+0x34>
 33b4a14: e8 77 61 09 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 33b4a19: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000033b4a20 <non-virtual thunk to NimoExSLApplicationLinux::onUpdatePlatform()>:
 33b4a20: 48 83 ef 10                  	subq	$0x10, %rdi
 33b4a24: e9 57 ff ff ff               	jmp	0x33b4980 <NimoExSLApplicationLinux::onUpdatePlatform()>
 33b4a29: 90                           	nop
 33b4a2a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000033b4a30 <NimoExSLApplicationLinux::onFinalizePlatform()>:
 33b4a30: 48 83 ec 28                  	subq	$0x28, %rsp
 33b4a34: 48 83 c7 10                  	addq	$0x10, %rdi
 33b4a38: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 33b4a41: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
 33b4a46: 31 c0                        	xorl	%eax, %eax
 33b4a48: e8 33 b4 7c ff               	callq	0x2b7fe80 <NimoExSLApplication::onFinalizePlatform()>
 33b4a4d: 84 c0                        	testb	%al, %al
 33b4a4f: 74 13                        	je	0x33b4a64 <NimoExSLApplicationLinux::onFinalizePlatform()+0x34>
 33b4a51: 88 44 24 0f                  	movb	%al, 0xf(%rsp)
 33b4a55: e8 b6 7d e4 ff               	callq	0x31fc810 <ExSLEglFunction::finalize()>
 33b4a5a: e8 41 58 ff ff               	callq	0x33aa2a0 <destroyNativeDisplayType()>
 33b4a5f: 0f b6 44 24 0f               	movzbl	0xf(%rsp), %eax
 33b4a64: 48 8b 54 24 18               	movq	0x18(%rsp), %rdx
 33b4a69: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 33b4a72: 75 05                        	jne	0x33b4a79 <NimoExSLApplicationLinux::onFinalizePlatform()+0x49>
 33b4a74: 48 83 c4 28                  	addq	$0x28, %rsp
 33b4a78: c3                           	retq
 33b4a79: e8 12 61 09 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 33b4a7e: 66 90                        	nop

00000000033b4a80 <non-virtual thunk to NimoExSLApplicationLinux::onFinalizePlatform()>:
 33b4a80: 48 83 ef 10                  	subq	$0x10, %rdi
 33b4a84: eb aa                        	jmp	0x33b4a30 <NimoExSLApplicationLinux::onFinalizePlatform()>
 33b4a86: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000033b4a90 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)>:
 33b4a90: 55                           	pushq	%rbp
 33b4a91: 53                           	pushq	%rbx
 33b4a92: 48 89 fb                     	movq	%rdi, %rbx
 33b4a95: 48 83 ec 18                  	subq	$0x18, %rsp
 33b4a99: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 33b4aa2: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 33b4aa7: 31 c0                        	xorl	%eax, %eax
 33b4aa9: 8b 46 14                     	movl	0x14(%rsi), %eax
 33b4aac: 39 87 c0 00 00 00            	cmpl	%eax, 0xc0(%rdi)
 33b4ab2: 74 24                        	je	0x33b4ad8 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)+0x48>
 33b4ab4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 33b4ab9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 33b4ac2: 0f 85 29 01 00 00            	jne	0x33b4bf1 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)+0x161>
 33b4ac8: 48 83 c4 18                  	addq	$0x18, %rsp
 33b4acc: 5b                           	popq	%rbx
 33b4acd: 5d                           	popq	%rbp
 33b4ace: e9 bd 83 09 fe               	jmp	0x144ce90 <_ZN7QObject10timerEventEP11QTimerEvent@plt>
 33b4ad3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 33b4ad8: e8 43 f6 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4add: 48 89 c7                     	movq	%rax, %rdi
 33b4ae0: e8 3b bd 83 ff               	callq	0x2bf0820 <CAppManagerComm::GetNaviBootStatus()>
 33b4ae5: 84 c0                        	testb	%al, %al
 33b4ae7: 75 5f                        	jne	0x33b4b48 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)+0xb8>
 33b4ae9: 4c 8d 05 58 f5 d0 02         	leaq	0x2d0f558(%rip), %r8    # 0x60c4048 <typeinfo name for NimoExSLNaviCircuitList+0x248>
 33b4af0: 48 8d 15 b9 f8 d0 02         	leaq	0x2d0f8b9(%rip), %rdx   # 0x60c43b0 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)::__func__>
 33b4af7: 48 8d 35 72 f3 d0 02         	leaq	0x2d0f372(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b4afe: b9 64 01 00 00               	movl	$0x164, %ecx            # imm = 0x164
 33b4b03: bf 01 00 00 00               	movl	$0x1, %edi
 33b4b08: e8 23 b2 45 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33b4b0d: 0f b7 05 04 16 ad 04         	movzwl	0x4ad1604(%rip), %eax   # 0x7e86118 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)::waitCount>
 33b4b14: 66 83 f8 04                  	cmpw	$0x4, %ax
 33b4b18: 0f 87 8a 00 00 00            	ja	0x33b4ba8 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)+0x118>
 33b4b1e: 83 c0 01                     	addl	$0x1, %eax
 33b4b21: 66 89 05 f0 15 ad 04         	movw	%ax, 0x4ad15f0(%rip)    # 0x7e86118 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)::waitCount>
 33b4b28: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 33b4b2d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 33b4b36: 0f 85 b5 00 00 00            	jne	0x33b4bf1 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)+0x161>
 33b4b3c: 48 83 c4 18                  	addq	$0x18, %rsp
 33b4b40: 5b                           	popq	%rbx
 33b4b41: 5d                           	popq	%rbp
 33b4b42: c3                           	retq
 33b4b43: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 33b4b48: e8 d3 c6 24 ff               	callq	0x2601220 <ExSLThreadMonitor::instance()>
 33b4b4d: 48 89 c7                     	movq	%rax, %rdi
 33b4b50: 48 8d 6b 10                  	leaq	0x10(%rbx), %rbp
 33b4b54: e8 87 c2 24 ff               	callq	0x2600de0 <ExSLThreadMonitor::StartTimeTrack()>
 33b4b59: 48 8b 43 10                  	movq	0x10(%rbx), %rax
 33b4b5d: 48 89 ef                     	movq	%rbp, %rdi
 33b4b60: ff 50 48                     	callq	*0x48(%rax)
 33b4b63: 48 8b 43 10                  	movq	0x10(%rbx), %rax
 33b4b67: 31 f6                        	xorl	%esi, %esi
 33b4b69: 48 89 ef                     	movq	%rbp, %rdi
 33b4b6c: ff 50 28                     	callq	*0x28(%rax)
 33b4b6f: 48 8b 43 10                  	movq	0x10(%rbx), %rax
 33b4b73: be 01 00 00 00               	movl	$0x1, %esi
 33b4b78: 48 89 ef                     	movq	%rbp, %rdi
 33b4b7b: ff 50 28                     	callq	*0x28(%rax)
 33b4b7e: e8 9d c6 24 ff               	callq	0x2601220 <ExSLThreadMonitor::instance()>
 33b4b83: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 33b4b88: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 33b4b91: 75 5e                        	jne	0x33b4bf1 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)+0x161>
 33b4b93: 48 83 c4 18                  	addq	$0x18, %rsp
 33b4b97: 48 89 c7                     	movq	%rax, %rdi
 33b4b9a: 5b                           	popq	%rbx
 33b4b9b: 5d                           	popq	%rbp
 33b4b9c: e9 1f f7 24 ff               	jmp	0x26042c0 <ExSLThreadMonitor::EndTimeTrack()>
 33b4ba1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 33b4ba8: e8 73 f5 84 ff               	callq	0x2c04120 <CAppManagerComm::GetInstance()>
 33b4bad: 48 89 c7                     	movq	%rax, %rdi
 33b4bb0: e8 fb 3e 85 ff               	callq	0x2c08ab0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()>
 33b4bb5: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 33b4bba: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 33b4bc3: 75 2c                        	jne	0x33b4bf1 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)+0x161>
 33b4bc5: 48 83 c4 18                  	addq	$0x18, %rsp
 33b4bc9: 4c 8d 05 a0 f4 d0 02         	leaq	0x2d0f4a0(%rip), %r8    # 0x60c4070 <typeinfo name for NimoExSLNaviCircuitList+0x270>
 33b4bd0: 48 8d 15 d9 f7 d0 02         	leaq	0x2d0f7d9(%rip), %rdx   # 0x60c43b0 <NimoExSLApplicationLinux::timerEvent(QTimerEvent*)::__func__>
 33b4bd7: 5b                           	popq	%rbx
 33b4bd8: 5d                           	popq	%rbp
 33b4bd9: 48 8d 35 90 f2 d0 02         	leaq	0x2d0f290(%rip), %rsi   # 0x60c3e70 <typeinfo name for NimoExSLNaviCircuitList+0x70>
 33b4be0: b9 69 01 00 00               	movl	$0x169, %ecx            # imm = 0x169
 33b4be5: bf 01 00 00 00               	movl	$0x1, %edi
 33b4bea: 31 c0                        	xorl	%eax, %eax
 33b4bec: e9 3f b1 45 ff               	jmp	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 33b4bf1: e8 9a 5f 09 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 33b4bf6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000033b4c00 <CNaviTPEGComm::Initialize()>:
 33b4c00: 55                           	pushq	%rbp
 33b4c01: 4c 8d 05 a0 f8 d0 02         	leaq	0x2d0f8a0(%rip), %r8    # 0x60c44a8 <createNativeDisplayType()::__func__+0x18>
 33b4c08: 48 8d 15 59 02 d1 02         	leaq	0x2d10259(%rip), %rdx   # 0x60c4e68 <CNaviTPEGComm::Initialize()::__func__>
 33b4c0f: 48 8d 35 fa ff d0 02         	leaq	0x2d0fffa(%rip), %rsi   # 0x60c4c10 <createNativeDisplayType()::__func__+0x780>
 33b4c16: b9 15 00 00 00               	movl	$0x15, %ecx
 33b4c1b: 48 89 e5                     	movq	%rsp, %rbp
 33b4c1e: 41 57                        	pushq	%r15
 33b4c20: 41 56                        	pushq	%r14
 33b4c22: 41 55                        	pushq	%r13
 33b4c24: 41 54                        	pushq	%r12
 33b4c26: 53                           	pushq	%rbx
 33b4c27: 48 89 fb                     	movq	%rdi, %rbx
 33b4c2a: bf 02 00 00 00               	movl	$0x2, %edi
 33b4c2f: 48 81 ec 98 00 00 00         	subq	$0x98, %rsp
 33b4c36: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 33b4c3f: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
 33b4c43: 31 c0                        	xorl	%eax, %eax
 33b4c45: e8 66 aa 45 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 33b4c4a: 48 8d 3d 7e 00 d1 02         	leaq	0x2d1007e(%rip), %rdi   # 0x60c4ccf <createNativeDisplayType()::__func__+0x83f>
 33b4c51: c6 43 10 00                  	movb	$0x0, 0x10(%rbx)
 33b4c55: c6 43 11 00                  	movb	$0x0, 0x11(%rbx)
 33b4c59: be 0f 00 00 00               	movl	$0xf, %esi
 33b4c5e: e8 3d 96 09 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 33b4c63: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 33b4c67: 48 8d 45 80                  	leaq	-0x80(%rbp), %rax
 33b4c6b: 48 89 c7                     	movq	%rax, %rdi
 33b4c6e: 49 89 c7                     	movq	%rax, %r15
 33b4c71: 48 89 85 48 ff ff ff         	movq	%rax, -0xb8(%rbp)
 33b4c78: e8 63 7e 09 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 33b4c7d: 4c 8d 65 a0                  	leaq	-0x60(%rbp), %r12
 33b4c81: b9 01 00 00 00               	movl	$0x1, %ecx
 33b4c86: 48 89 da                     	movq	%rbx, %rdx
 33b4c89: 4c 89 ff                     	movq	%r15, %rdi
 33b4c8c: 4c 89 e6                     	movq	%r12, %rsi
 33b4c8f: e8 ac 71 09 fe               	callq	0x144be40 <_ZN15QDBusConnection14registerObjectERK7QStringP7QObject6QFlagsINS_14RegisterOptionEE@plt>
 33b4c94: 4c 89 ff                     	movq	%r15, %rdi
 33b4c97: e8 14 8c 09 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 33b4c9c: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 33b4ca0: 8b 07                        	movl	(%rdi), %eax
 33b4ca2: 85 c0                        	testl	%eax, %eax
 33b4ca4: 0f 85 86 02 00 00            	jne	0x33b4f30 <CNaviTPEGComm::Initialize()+0x330>
 33b4caa: ba 08 00 00 00               	movl	$0x8, %edx
 33b4caf: be 02 00 00 00               	movl	$0x2, %esi
 33b4cb4: e8 e7 69 09 fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 33b4cb9: 48 8d 3d 1f 00 d1 02         	leaq	0x2d1001f(%rip), %rdi   # 0x60c4cdf <createNativeDisplayType()::__func__+0x84f>
 33b4cc0: be 0c 00 00 00               	movl	$0xc, %esi
 33b4cc5: e8 d6 95 09 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 33b4cca: 48 8d 3d 1b 00 d1 02         	leaq	0x2d1001b(%rip), %rdi   # 0x60c4cec <createNativeDisplayType()::__func__+0x85c>
 33b4cd1: be 15 00 00 00               	movl	$0x15, %esi
 33b4cd6: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 33b4cda: e8 c1 95 09 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 33b4cdf: 48 89 45 80                  	movq	%rax, -0x80(%rbp)
 33b4ce3: 4c 8d ad 50 ff ff ff         	leaq	-0xb0(%rbp), %r13
 33b4cea: 48 8b 05 2f 96 2f 04         	movq	0x42f962f(%rip), %rax   # 0x76ae320 <_GLOBAL_OFFSET_TABLE_+0x50b8>
 33b4cf1: 4c 89 ef                     	movq	%r13, %rdi
 33b4cf4: 48 89 85 70 ff ff ff         	movq	%rax, -0x90(%rbp)
 33b4cfb: 48 89 85 60 ff ff ff         	movq	%rax, -0xa0(%rbp)
