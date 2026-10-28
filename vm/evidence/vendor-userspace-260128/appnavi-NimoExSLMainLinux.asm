
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

0000000001ba7000 <NimoExSLMainLinux(int, char**)>:
 1ba7000: 41 56                        	pushq	%r14
 1ba7002: 41 55                        	pushq	%r13
 1ba7004: 41 54                        	pushq	%r12
 1ba7006: 55                           	pushq	%rbp
 1ba7007: 89 fd                        	movl	%edi, %ebp
 1ba7009: 53                           	pushq	%rbx
 1ba700a: 48 8d 3d ee d5 6c 04         	leaq	0x46cd5ee(%rip), %rdi   # 0x62745ff <__PRETTY_FUNCTION__.4173+0xe7>
 1ba7011: 48 89 f3                     	movq	%rsi, %rbx
 1ba7014: 48 8d 35 98 ff 71 04         	leaq	0x471ff98(%rip), %rsi   # 0x62c6fb3 <typeinfo name for CGuidanceInfo+0xcb83>
 1ba701b: 48 81 ec 30 01 00 00         	subq	$0x130, %rsp            # imm = 0x130
 1ba7022: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba702b: 48 89 84 24 28 01 00 00      	movq	%rax, 0x128(%rsp)
 1ba7033: 31 c0                        	xorl	%eax, %eax
 1ba7035: e8 46 6e 8a ff               	callq	0x144de80 <dlt_check_library_version@plt>
 1ba703a: 48 8d 35 87 8a 22 04         	leaq	0x4228a87(%rip), %rsi   # 0x5dcfac8 <typeinfo name for NimoExSLMapRenderer+0x268>
 1ba7041: 48 8d 3d 7d e5 3b 04         	leaq	0x43be57d(%rip), %rdi   # 0x5f655c5 <ExSLBootFailLog::SaveBootFailLogFile()::__func__+0x975>
 1ba7048: e8 a3 39 8a ff               	callq	0x144a9f0 <dlt_register_app@plt>
 1ba704d: 48 8d 3d cc 29 b4 05         	leaq	0x5b429cc(%rip), %rdi   # 0x76e9a20 <mLogContext>
 1ba7054: 48 8d 15 95 8a 22 04         	leaq	0x4228a95(%rip), %rdx   # 0x5dcfaf0 <typeinfo name for NimoExSLMapRenderer+0x290>
 1ba705b: 48 8d 35 63 e5 3b 04         	leaq	0x43be563(%rip), %rsi   # 0x5f655c5 <ExSLBootFailLog::SaveBootFailLogFile()::__func__+0x975>
 1ba7062: e8 79 5f 8a ff               	callq	0x144cfe0 <dlt_register_context@plt>
 1ba7067: 4c 8d 05 aa 8a 22 04         	leaq	0x4228aaa(%rip), %r8    # 0x5dcfb18 <typeinfo name for NimoExSLMapRenderer+0x2b8>
 1ba706e: 48 8d 15 8b 8f 22 04         	leaq	0x4228f8b(%rip), %rdx   # 0x5dd0000 <NimoExSLMainLinux(int, char**)::__func__>
 1ba7075: 48 8d 35 e4 88 22 04         	leaq	0x42288e4(%rip), %rsi   # 0x5dcf960 <typeinfo name for NimoExSLMapRenderer+0x100>
 1ba707c: b9 59 00 00 00               	movl	$0x59, %ecx
 1ba7081: bf 03 00 00 00               	movl	$0x3, %edi
 1ba7086: 31 c0                        	xorl	%eax, %eax
 1ba7088: e8 a3 8c c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba708d: e8 ce 98 a5 00               	callq	0x2600960 <getTickCount()>
 1ba7092: 48 8d 15 67 29 b4 05         	leaq	0x5b42967(%rip), %rdx   # 0x76e9a00 <g_startTime>
 1ba7099: 48 83 ec 08                  	subq	$0x8, %rsp
 1ba709d: 4c 8b 0b                     	movq	(%rbx), %r9
 1ba70a0: 48 8d 35 b9 88 22 04         	leaq	0x42288b9(%rip), %rsi   # 0x5dcf960 <typeinfo name for NimoExSLMapRenderer+0x100>
 1ba70a7: 4c 8d 05 8a 88 22 04         	leaq	0x422888a(%rip), %r8    # 0x5dcf938 <typeinfo name for NimoExSLMapRenderer+0xd8>
 1ba70ae: b9 70 00 00 00               	movl	$0x70, %ecx
 1ba70b3: bf 01 00 00 00               	movl	$0x1, %edi
 1ba70b8: 89 02                        	movl	%eax, (%rdx)
 1ba70ba: 55                           	pushq	%rbp
 1ba70bb: 48 8d 15 3e 8f 22 04         	leaq	0x4228f3e(%rip), %rdx   # 0x5dd0000 <NimoExSLMainLinux(int, char**)::__func__>
 1ba70c2: 31 c0                        	xorl	%eax, %eax
 1ba70c4: 4c 8d 6c 24 30               	leaq	0x30(%rsp), %r13
 1ba70c9: e8 62 8c c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba70ce: 31 c0                        	xorl	%eax, %eax
 1ba70d0: b9 20 00 00 00               	movl	$0x20, %ecx
 1ba70d5: 4c 89 ef                     	movq	%r13, %rdi
 1ba70d8: f3 48 ab                     	rep		stosq	%rax, %es:(%rdi)
 1ba70db: 85 ed                        	testl	%ebp, %ebp
 1ba70dd: c7 07 00 00 00 00            	movl	$0x0, (%rdi)
 1ba70e3: 59                           	popq	%rcx
 1ba70e4: 5e                           	popq	%rsi
 1ba70e5: 0f 8e 25 01 00 00            	jle	0x1ba7210 <NimoExSLMainLinux(int, char**)+0x210>
 1ba70eb: 4c 8b 33                     	movq	(%rbx), %r14
 1ba70ee: 4c 89 f7                     	movq	%r14, %rdi
 1ba70f1: e8 2a 5f 8a ff               	callq	0x144d020 <strlen@plt>
 1ba70f6: 48 8d 35 4f 88 22 04         	leaq	0x422884f(%rip), %rsi   # 0x5dcf94c <typeinfo name for NimoExSLMapRenderer+0xec>
 1ba70fd: 4c 89 f7                     	movq	%r14, %rdi
 1ba7100: 49 89 c4                     	movq	%rax, %r12
 1ba7103: e8 98 5f 8a ff               	callq	0x144d0a0 <strstr@plt>
 1ba7108: 48 85 c0                     	testq	%rax, %rax
 1ba710b: 0f 84 f7 00 00 00            	je	0x1ba7208 <NimoExSLMainLinux(int, char**)+0x208>
 1ba7111: 48 89 c7                     	movq	%rax, %rdi
 1ba7114: e8 07 5f 8a ff               	callq	0x144d020 <strlen@plt>
 1ba7119: 41 29 c4                     	subl	%eax, %r12d
 1ba711c: 4c 89 ef                     	movq	%r13, %rdi
 1ba711f: b9 04 01 00 00               	movl	$0x104, %ecx            # imm = 0x104
 1ba7124: 49 63 d4                     	movslq	%r12d, %rdx
 1ba7127: 4c 89 f6                     	movq	%r14, %rsi
 1ba712a: 49 89 e4                     	movq	%rsp, %r12
 1ba712d: e8 be 4b 8a ff               	callq	0x144bcf0 <__strncpy_chk@plt>
 1ba7132: 48 8d 44 24 10               	leaq	0x10(%rsp), %rax
 1ba7137: ba 35 57 00 00               	movl	$0x5735, %edx           # imm = 0x5735
 1ba713c: c7 44 24 10 4c 53 54 44      	movl	$0x4454534c, 0x10(%rsp) # imm = 0x4454534C
 1ba7144: 4c 89 2b                     	movq	%r13, (%rbx)
 1ba7147: 48 89 e7                     	movq	%rsp, %rdi
 1ba714a: 48 c7 44 24 08 06 00 00 00   	movq	$0x6, 0x8(%rsp)
 1ba7153: 66 89 50 04                  	movw	%dx, 0x4(%rax)
 1ba7157: 48 89 04 24                  	movq	%rax, (%rsp)
 1ba715b: c6 44 24 16 00               	movb	$0x0, 0x16(%rsp)
 1ba7160: e8 db df ff ff               	callq	0x1ba5140 <setPlatformInfo(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>)>
 1ba7165: 48 8b 3c 24                  	movq	(%rsp), %rdi
 1ba7169: 49 83 c4 10                  	addq	$0x10, %r12
 1ba716d: 4c 39 e7                     	cmpq	%r12, %rdi
 1ba7170: 74 05                        	je	0x1ba7177 <NimoExSLMainLinux(int, char**)+0x177>
 1ba7172: e8 39 3d 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba7177: 48 89 de                     	movq	%rbx, %rsi
 1ba717a: 89 ef                        	movl	%ebp, %edi
 1ba717c: e8 6f eb ff ff               	callq	0x1ba5cf0 <setRegion(int, char**)>
 1ba7181: 48 89 de                     	movq	%rbx, %rsi
 1ba7184: 89 ef                        	movl	%ebp, %edi
 1ba7186: e8 45 d7 ff ff               	callq	0x1ba48d0 <setECOType(int, char**)>
 1ba718b: 48 89 de                     	movq	%rbx, %rsi
 1ba718e: 89 ef                        	movl	%ebp, %edi
 1ba7190: e8 3b d9 ff ff               	callq	0x1ba4ad0 <setVendor(int, char**)>
 1ba7195: 48 89 de                     	movq	%rbx, %rsi
 1ba7198: 89 ef                        	movl	%ebp, %edi
 1ba719a: e8 91 db ff ff               	callq	0x1ba4d30 <setUNECESupport(int, char**)>
 1ba719f: 48 89 de                     	movq	%rbx, %rsi
 1ba71a2: 89 ef                        	movl	%ebp, %edi
 1ba71a4: e8 a7 dc ff ff               	callq	0x1ba4e50 <setIsRearMonitorExist(int, char**)>
 1ba71a9: 48 89 de                     	movq	%rbx, %rsi
 1ba71ac: 89 ef                        	movl	%ebp, %edi
 1ba71ae: e8 9d dd ff ff               	callq	0x1ba4f50 <setVehicleCode(int, char**)>
 1ba71b3: 48 89 de                     	movq	%rbx, %rsi
 1ba71b6: 89 ef                        	movl	%ebp, %edi
 1ba71b8: e8 d3 df ff ff               	callq	0x1ba5190 <setDisplayType(int, char**)>
 1ba71bd: e8 de f5 ff ff               	callq	0x1ba67a0 <setBootMicomStatus()>
 1ba71c2: 48 89 de                     	movq	%rbx, %rsi
 1ba71c5: 89 ef                        	movl	%ebp, %edi
 1ba71c7: e8 64 ef ff ff               	callq	0x1ba6130 <setOuterMostRegion(int, char**)>
 1ba71cc: 48 89 de                     	movq	%rbx, %rsi
 1ba71cf: 89 ef                        	movl	%ebp, %edi
 1ba71d1: e8 5a e1 ff ff               	callq	0x1ba5330 <createCANReceiver(int, char**)>
 1ba71d6: 48 89 de                     	movq	%rbx, %rsi
 1ba71d9: 89 ef                        	movl	%ebp, %edi
 1ba71db: e8 f0 59 c6 00               	callq	0x280cbd0 <ExSLMain(int, char**)>
 1ba71e0: 48 8b 8c 24 28 01 00 00      	movq	0x128(%rsp), %rcx
 1ba71e8: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 1ba71f1: 75 24                        	jne	0x1ba7217 <NimoExSLMainLinux(int, char**)+0x217>
 1ba71f3: 48 81 c4 30 01 00 00         	addq	$0x130, %rsp            # imm = 0x130
 1ba71fa: 5b                           	popq	%rbx
 1ba71fb: 5d                           	popq	%rbp
 1ba71fc: 41 5c                        	popq	%r12
 1ba71fe: 41 5d                        	popq	%r13
 1ba7200: 41 5e                        	popq	%r14
 1ba7202: c3                           	retq
 1ba7203: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7208: 31 c0                        	xorl	%eax, %eax
 1ba720a: eb d4                        	jmp	0x1ba71e0 <NimoExSLMainLinux(int, char**)+0x1e0>
 1ba720c: 0f 1f 40 00                  	nopl	(%rax)
 1ba7210: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
 1ba7215: eb c9                        	jmp	0x1ba71e0 <NimoExSLMainLinux(int, char**)+0x1e0>
 1ba7217: e8 74 39 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba721c: 48 8b 3c 24                  	movq	(%rsp), %rdi
 1ba7220: 49 83 c4 10                  	addq	$0x10, %r12
 1ba7224: 48 89 c3                     	movq	%rax, %rbx
 1ba7227: 4c 39 e7                     	cmpq	%r12, %rdi
 1ba722a: 74 05                        	je	0x1ba7231 <NimoExSLMainLinux(int, char**)+0x231>
 1ba722c: e8 7f 3c 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba7231: 48 89 df                     	movq	%rbx, %rdi
 1ba7234: e8 27 60 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba7239: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000001ba7240 <std::ctype<char>::do_widen(char) const>:
 1ba7240: 48 83 ec 18                  	subq	$0x18, %rsp
 1ba7244: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba724d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7252: 31 c0                        	xorl	%eax, %eax
 1ba7254: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 1ba7259: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 1ba7262: 75 07                        	jne	0x1ba726b <std::ctype<char>::do_widen(char) const+0x2b>
 1ba7264: 89 f0                        	movl	%esi, %eax
 1ba7266: 48 83 c4 18                  	addq	$0x18, %rsp
 1ba726a: c3                           	retq
 1ba726b: e8 20 39 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>

0000000001ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>:
 1ba7270: 41 54                        	pushq	%r12
 1ba7272: 55                           	pushq	%rbp
 1ba7273: 49 89 fc                     	movq	%rdi, %r12
 1ba7276: 53                           	pushq	%rbx
 1ba7277: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba727b: 48 8b 6f 48                  	movq	0x48(%rdi), %rbp
 1ba727f: 48 8b 5f 40                  	movq	0x40(%rdi), %rbx
 1ba7283: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba728c: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7291: 31 c0                        	xorl	%eax, %eax
 1ba7293: 48 39 dd                     	cmpq	%rbx, %rbp
 1ba7296: 74 27                        	je	0x1ba72bf <NaviAdapter::ExternalParameter::~ExternalParameter()+0x4f>
 1ba7298: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
 1ba72a0: 48 8b 3b                     	movq	(%rbx), %rdi
 1ba72a3: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba72a7: 48 39 c7                     	cmpq	%rax, %rdi
 1ba72aa: 74 05                        	je	0x1ba72b1 <NaviAdapter::ExternalParameter::~ExternalParameter()+0x41>
 1ba72ac: e8 ff 3b 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba72b1: 48 83 c3 20                  	addq	$0x20, %rbx
 1ba72b5: 48 39 dd                     	cmpq	%rbx, %rbp
 1ba72b8: 75 e6                        	jne	0x1ba72a0 <NaviAdapter::ExternalParameter::~ExternalParameter()+0x30>
 1ba72ba: 49 8b 6c 24 40               	movq	0x40(%r12), %rbp
 1ba72bf: 48 85 ed                     	testq	%rbp, %rbp
 1ba72c2: 74 08                        	je	0x1ba72cc <NaviAdapter::ExternalParameter::~ExternalParameter()+0x5c>
 1ba72c4: 48 89 ef                     	movq	%rbp, %rdi
 1ba72c7: e8 e4 3b 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba72cc: 49 8b 7c 24 28               	movq	0x28(%r12), %rdi
 1ba72d1: 48 85 ff                     	testq	%rdi, %rdi
 1ba72d4: 74 05                        	je	0x1ba72db <NaviAdapter::ExternalParameter::~ExternalParameter()+0x6b>
 1ba72d6: e8 d5 3b 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba72db: 49 8b 7c 24 10               	movq	0x10(%r12), %rdi
 1ba72e0: 48 85 ff                     	testq	%rdi, %rdi
 1ba72e3: 74 23                        	je	0x1ba7308 <NaviAdapter::ExternalParameter::~ExternalParameter()+0x98>
 1ba72e5: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 1ba72ea: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 1ba72f3: 75 2c                        	jne	0x1ba7321 <NaviAdapter::ExternalParameter::~ExternalParameter()+0xb1>
 1ba72f5: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba72f9: 5b                           	popq	%rbx
 1ba72fa: 5d                           	popq	%rbp
 1ba72fb: 41 5c                        	popq	%r12
 1ba72fd: e9 ae 3b 8a ff               	jmp	0x144aeb0 <_ZdlPv@plt>
 1ba7302: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 1ba7308: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 1ba730d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 1ba7316: 75 09                        	jne	0x1ba7321 <NaviAdapter::ExternalParameter::~ExternalParameter()+0xb1>
 1ba7318: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba731c: 5b                           	popq	%rbx
 1ba731d: 5d                           	popq	%rbp
 1ba731e: 41 5c                        	popq	%r12
 1ba7320: c3                           	retq
 1ba7321: e8 6a 38 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba7326: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000001ba7330 <utf16StringToUtf8String(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>:
 1ba7330: 41 56                        	pushq	%r14
 1ba7332: 41 55                        	pushq	%r13
 1ba7334: 49 89 fe                     	movq	%rdi, %r14
 1ba7337: 41 54                        	pushq	%r12
 1ba7339: 55                           	pushq	%rbp
 1ba733a: 49 89 f5                     	movq	%rsi, %r13
 1ba733d: 53                           	pushq	%rbx
 1ba733e: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba7342: 48 c7 46 08 00 00 00 00      	movq	$0x0, 0x8(%rsi)
 1ba734a: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba7353: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7358: 31 c0                        	xorl	%eax, %eax
 1ba735a: 48 8b 06                     	movq	(%rsi), %rax
 1ba735d: c6 00 00                     	movb	$0x0, (%rax)
 1ba7360: 8b 47 08                     	movl	0x8(%rdi), %eax
 1ba7363: 44 8d 24 85 00 00 00 00      	leal	(,%rax,4), %r12d
 1ba736b: 41 8d 7c 24 01               	leal	0x1(%r12), %edi
 1ba7370: 4c 89 e3                     	movq	%r12, %rbx
 1ba7373: e8 d8 6e 8a ff               	callq	0x144e250 <_Znam@plt>
 1ba7378: 49 8b 3e                     	movq	(%r14), %rdi
 1ba737b: 49 01 c4                     	addq	%rax, %r12
 1ba737e: 89 da                        	movl	%ebx, %edx
 1ba7380: 41 c6 04 24 00               	movb	$0x0, (%r12)
 1ba7385: 48 89 c6                     	movq	%rax, %rsi
 1ba7388: 48 89 c5                     	movq	%rax, %rbp
 1ba738b: e8 f0 66 90 01               	callq	0x34ada80 <mToUtf8(wchar_t const*, char*, int)>
 1ba7390: 41 c6 04 24 00               	movb	$0x0, (%r12)
 1ba7395: 48 89 ef                     	movq	%rbp, %rdi
 1ba7398: 89 c3                        	movl	%eax, %ebx
 1ba739a: e8 81 5c 8a ff               	callq	0x144d020 <strlen@plt>
 1ba739f: 48 b9 ff ff ff ff ff ff ff 7f	movabsq	$0x7fffffffffffffff, %rcx # imm = 0x7FFFFFFFFFFFFFFF
 1ba73a9: 49 2b 4d 08                  	subq	0x8(%r13), %rcx
 1ba73ad: 48 39 c8                     	cmpq	%rcx, %rax
 1ba73b0: 77 35                        	ja	0x1ba73e7 <utf16StringToUtf8String(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xb7>
 1ba73b2: 48 89 c2                     	movq	%rax, %rdx
 1ba73b5: 48 89 ee                     	movq	%rbp, %rsi
 1ba73b8: 4c 89 ef                     	movq	%r13, %rdi
 1ba73bb: e8 50 72 8a ff               	callq	0x144e610 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_appendEPKcm@plt>
 1ba73c0: 48 89 ef                     	movq	%rbp, %rdi
 1ba73c3: e8 d8 5b 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba73c8: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 1ba73cd: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 1ba73d6: 89 d8                        	movl	%ebx, %eax
 1ba73d8: 75 2c                        	jne	0x1ba7406 <utf16StringToUtf8String(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xd6>
 1ba73da: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba73de: 5b                           	popq	%rbx
 1ba73df: 5d                           	popq	%rbp
 1ba73e0: 41 5c                        	popq	%r12
 1ba73e2: 41 5d                        	popq	%r13
 1ba73e4: 41 5e                        	popq	%r14
 1ba73e6: c3                           	retq
 1ba73e7: 48 8d 3d 70 d8 1b 04         	leaq	0x41bd870(%rip), %rdi   # 0x5d64c5e <_IO_stdin_used+0x21e>
 1ba73ee: e8 5d 3b 8a ff               	callq	0x144af50 <_ZSt20__throw_length_errorPKc@plt>
 1ba73f3: 48 89 c3                     	movq	%rax, %rbx
 1ba73f6: 48 89 ef                     	movq	%rbp, %rdi
 1ba73f9: e8 a2 5b 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba73fe: 48 89 df                     	movq	%rbx, %rdi
 1ba7401: e8 5a 5e 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba7406: e8 85 37 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba740b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000001ba7410 <utf16StringToUtf8String(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&)>:
 1ba7410: 41 54                        	pushq	%r12
 1ba7412: 55                           	pushq	%rbp
 1ba7413: 53                           	pushq	%rbx
 1ba7414: 48 89 fb                     	movq	%rdi, %rbx
 1ba7417: 48 89 f7                     	movq	%rsi, %rdi
 1ba741a: 48 8d 6b 10                  	leaq	0x10(%rbx), %rbp
 1ba741e: 48 89 de                     	movq	%rbx, %rsi
 1ba7421: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba7425: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
 1ba742d: c6 43 10 00                  	movb	$0x0, 0x10(%rbx)
 1ba7431: 48 89 2b                     	movq	%rbp, (%rbx)
 1ba7434: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba743d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7442: 31 c0                        	xorl	%eax, %eax
 1ba7444: e8 e7 fe ff ff               	callq	0x1ba7330 <utf16StringToUtf8String(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>
 1ba7449: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 1ba744e: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 1ba7457: 48 89 d8                     	movq	%rbx, %rax
 1ba745a: 75 09                        	jne	0x1ba7465 <utf16StringToUtf8String(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&)+0x55>
 1ba745c: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba7460: 5b                           	popq	%rbx
 1ba7461: 5d                           	popq	%rbp
 1ba7462: 41 5c                        	popq	%r12
 1ba7464: c3                           	retq
 1ba7465: e8 26 37 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba746a: 48 8b 3b                     	movq	(%rbx), %rdi
 1ba746d: 49 89 c4                     	movq	%rax, %r12
 1ba7470: 48 39 ef                     	cmpq	%rbp, %rdi
 1ba7473: 74 05                        	je	0x1ba747a <utf16StringToUtf8String(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&)+0x6a>
 1ba7475: e8 36 3a 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba747a: 4c 89 e7                     	movq	%r12, %rdi
 1ba747d: e8 de 5d 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba7482: 0f 1f 40 00                  	nopl	(%rax)
 1ba7486: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000001ba7490 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>:
 1ba7490: 41 57                        	pushq	%r15
 1ba7492: 41 56                        	pushq	%r14
 1ba7494: 41 55                        	pushq	%r13
 1ba7496: 41 54                        	pushq	%r12
 1ba7498: 55                           	pushq	%rbp
 1ba7499: 53                           	pushq	%rbx
 1ba749a: 48 83 ec 18                  	subq	$0x18, %rsp
 1ba749e: 4c 8b 6f 08                  	movq	0x8(%rdi), %r13
 1ba74a2: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba74ab: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba74b0: 31 c0                        	xorl	%eax, %eax
 1ba74b2: 4d 85 ed                     	testq	%r13, %r13
 1ba74b5: 75 29                        	jne	0x1ba74e0 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x50>
 1ba74b7: 48 8b 5c 24 08               	movq	0x8(%rsp), %rbx
 1ba74bc: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
 1ba74c5: 0f 85 0e 03 00 00            	jne	0x1ba77d9 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x349>
 1ba74cb: 48 83 c4 18                  	addq	$0x18, %rsp
 1ba74cf: 5b                           	popq	%rbx
 1ba74d0: 5d                           	popq	%rbp
 1ba74d1: 41 5c                        	popq	%r12
 1ba74d3: 41 5d                        	popq	%r13
 1ba74d5: 41 5e                        	popq	%r14
 1ba74d7: 41 5f                        	popq	%r15
 1ba74d9: c3                           	retq
 1ba74da: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 1ba74e0: 48 89 fb                     	movq	%rdi, %rbx
 1ba74e3: 4b 8d 7c 2d 01               	leaq	0x1(%r13,%r13), %rdi
 1ba74e8: 49 89 f4                     	movq	%rsi, %r12
 1ba74eb: e8 60 6d 8a ff               	callq	0x144e250 <_Znam@plt>
 1ba74f0: 48 89 c5                     	movq	%rax, %rbp
 1ba74f3: 41 8d 45 01                  	leal	0x1(%r13), %eax
 1ba74f7: 48 8b 13                     	movq	(%rbx), %rdx
 1ba74fa: 85 c0                        	testl	%eax, %eax
 1ba74fc: 0f 8e cb 02 00 00            	jle	0x1ba77cd <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x33d>
 1ba7502: 45 89 ed                     	movl	%r13d, %r13d
 1ba7505: 48 89 ee                     	movq	%rbp, %rsi
 1ba7508: 45 31 c9                     	xorl	%r9d, %r9d
 1ba750b: 4e 8d 44 6a 02               	leaq	0x2(%rdx,%r13,2), %r8
 1ba7510: 41 bb 01 00 00 00            	movl	$0x1, %r11d
 1ba7516: 4c 8d 35 43 b4 22 04         	leaq	0x422b443(%rip), %r14   # 0x5dd2960 <exsl_ksc5601_uni2indx_page30>
 1ba751d: 4c 8d 2d 3c b5 22 04         	leaq	0x422b53c(%rip), %r13   # 0x5dd2a60 <exsl_ksc5601_uni2indx_page20>
 1ba7524: 4c 8d 15 d5 b6 22 04         	leaq	0x422b6d5(%rip), %r10   # 0x5dd2c00 <exsl_ksc5601_uni2indx_page00>
 1ba752b: eb 12                        	jmp	0x1ba753f <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xaf>
 1ba752d: 0f 1f 00                     	nopl	(%rax)
 1ba7530: 88 0e                        	movb	%cl, (%rsi)
 1ba7532: 48 83 c6 01                  	addq	$0x1, %rsi
 1ba7536: 4c 39 c2                     	cmpq	%r8, %rdx
 1ba7539: 0f 84 bd 00 00 00            	je	0x1ba75fc <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x16c>
 1ba753f: 0f b7 0a                     	movzwl	(%rdx), %ecx
 1ba7542: 48 83 c2 02                  	addq	$0x2, %rdx
 1ba7546: 66 83 f9 7f                  	cmpw	$0x7f, %cx
 1ba754a: 76 e4                        	jbe	0x1ba7530 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xa0>
 1ba754c: 66 81 f9 5f 04               	cmpw	$0x45f, %cx             # imm = 0x45F
 1ba7551: 0f 87 19 01 00 00            	ja	0x1ba7670 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x1e0>
 1ba7557: 48 89 cf                     	movq	%rcx, %rdi
 1ba755a: 48 c1 ef 02                  	shrq	$0x2, %rdi
 1ba755e: 81 e7 fc 3f 00 00            	andl	$0x3ffc, %edi           # imm = 0x3FFC
 1ba7564: 4c 01 d7                     	addq	%r10, %rdi
 1ba7567: 0f b7 47 02                  	movzwl	0x2(%rdi), %eax
 1ba756b: 83 e1 0f                     	andl	$0xf, %ecx
 1ba756e: 0f a3 c8                     	btl	%ecx, %eax
 1ba7571: 41 89 c7                     	movl	%eax, %r15d
 1ba7574: 0f 83 e6 00 00 00            	jae	0x1ba7660 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x1d0>
 1ba757a: 44 89 d8                     	movl	%r11d, %eax
 1ba757d: 0f b7 3f                     	movzwl	(%rdi), %edi
 1ba7580: 48 83 c6 02                  	addq	$0x2, %rsi
 1ba7584: d3 e0                        	shll	%cl, %eax
 1ba7586: 83 e8 01                     	subl	$0x1, %eax
 1ba7589: 44 21 f8                     	andl	%r15d, %eax
 1ba758c: 89 c1                        	movl	%eax, %ecx
 1ba758e: 25 aa aa 00 00               	andl	$0xaaaa, %eax           # imm = 0xAAAA
 1ba7593: 66 81 e1 55 55               	andw	$0x5555, %cx            # imm = 0x5555
 1ba7598: d1 f8                        	sarl	%eax
 1ba759a: 44 8d 3c 01                  	leal	(%rcx,%rax), %r15d
 1ba759e: 44 89 f8                     	movl	%r15d, %eax
 1ba75a1: 41 81 e7 cc cc 00 00         	andl	$0xcccc, %r15d          # imm = 0xCCCC
 1ba75a8: 66 25 33 33                  	andw	$0x3333, %ax            # imm = 0x3333
 1ba75ac: 41 c1 ff 02                  	sarl	$0x2, %r15d
 1ba75b0: 42 8d 0c 38                  	leal	(%rax,%r15), %ecx
 1ba75b4: 41 89 cf                     	movl	%ecx, %r15d
 1ba75b7: 81 e1 f0 70 00 00            	andl	$0x70f0, %ecx           # imm = 0x70F0
 1ba75bd: c1 f9 04                     	sarl	$0x4, %ecx
 1ba75c0: 66 41 81 e7 0f 0f            	andw	$0xf0f, %r15w           # imm = 0xF0F
 1ba75c6: 41 8d 04 0f                  	leal	(%r15,%rcx), %eax
 1ba75ca: 0f b7 c8                     	movzwl	%ax, %ecx
 1ba75cd: 0f b6 c0                     	movzbl	%al, %eax
 1ba75d0: c1 f9 08                     	sarl	$0x8, %ecx
 1ba75d3: 01 c8                        	addl	%ecx, %eax
 1ba75d5: 48 8d 0d 44 b7 22 04         	leaq	0x422b744(%rip), %rcx   # 0x5dd2d20 <exsl_ksc5601_2charset>
 1ba75dc: 01 f8                        	addl	%edi, %eax
 1ba75de: 48 98                        	cltq
 1ba75e0: 0f b7 04 41                  	movzwl	(%rcx,%rax,2), %eax
 1ba75e4: 0f b6 cc                     	movzbl	%ah, %ecx
 1ba75e7: 83 c0 80                     	addl	$-0x80, %eax
 1ba75ea: 83 c1 80                     	addl	$-0x80, %ecx
 1ba75ed: 88 46 ff                     	movb	%al, -0x1(%rsi)
 1ba75f0: 88 4e fe                     	movb	%cl, -0x2(%rsi)
 1ba75f3: 4c 39 c2                     	cmpq	%r8, %rdx
 1ba75f6: 0f 85 43 ff ff ff            	jne	0x1ba753f <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xaf>
 1ba75fc: c6 06 00                     	movb	$0x0, (%rsi)
 1ba75ff: 41 bd ff ff ff ff            	movl	$0xffffffff, %r13d      # imm = 0xFFFFFFFF
 1ba7605: 48 29 ee                     	subq	%rbp, %rsi
 1ba7608: 45 85 c9                     	testl	%r9d, %r9d
 1ba760b: 44 0f 44 ee                  	cmovel	%esi, %r13d
 1ba760f: 48 89 ef                     	movq	%rbp, %rdi
 1ba7612: e8 09 5a 8a ff               	callq	0x144d020 <strlen@plt>
 1ba7617: 48 b9 ff ff ff ff ff ff ff 7f	movabsq	$0x7fffffffffffffff, %rcx # imm = 0x7FFFFFFFFFFFFFFF
 1ba7621: 49 2b 4c 24 08               	subq	0x8(%r12), %rcx
 1ba7626: 48 39 c8                     	cmpq	%rcx, %rax
 1ba7629: 0f 87 af 01 00 00            	ja	0x1ba77de <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x34e>
 1ba762f: 48 89 c2                     	movq	%rax, %rdx
 1ba7632: 48 89 ee                     	movq	%rbp, %rsi
 1ba7635: 4c 89 e7                     	movq	%r12, %rdi
 1ba7638: e8 d3 6f 8a ff               	callq	0x144e610 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_appendEPKcm@plt>
 1ba763d: 41 83 fd ff                  	cmpl	$-0x1, %r13d
 1ba7641: 0f 84 11 01 00 00            	je	0x1ba7758 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x2c8>
 1ba7647: 48 89 ef                     	movq	%rbp, %rdi
 1ba764a: e8 51 59 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba764f: b8 01 00 00 00               	movl	$0x1, %eax
 1ba7654: e9 5e fe ff ff               	jmp	0x1ba74b7 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x27>
 1ba7659: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 1ba7660: 41 b9 fe ff ff ff            	movl	$0xfffffffe, %r9d       # imm = 0xFFFFFFFE
 1ba7666: e9 cb fe ff ff               	jmp	0x1ba7536 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xa6>
 1ba766b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7670: 8d 81 00 e0 ff ff            	leal	-0x2000(%rcx), %eax
 1ba7676: 66 3d 6f 06                  	cmpw	$0x66f, %ax             # imm = 0x66F
 1ba767a: 77 1c                        	ja	0x1ba7698 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x208>
 1ba767c: 0f b7 c1                     	movzwl	%cx, %eax
 1ba767f: c1 f8 04                     	sarl	$0x4, %eax
 1ba7682: 2d 00 02 00 00               	subl	$0x200, %eax            # imm = 0x200
 1ba7687: 48 98                        	cltq
 1ba7689: 49 8d 7c 85 00               	leaq	(%r13,%rax,4), %rdi
 1ba768e: e9 d4 fe ff ff               	jmp	0x1ba7567 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xd7>
 1ba7693: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7698: 8d 81 00 d0 ff ff            	leal	-0x3000(%rcx), %eax
 1ba769e: 66 3d df 03                  	cmpw	$0x3df, %ax             # imm = 0x3DF
 1ba76a2: 77 1c                        	ja	0x1ba76c0 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x230>
 1ba76a4: 0f b7 c1                     	movzwl	%cx, %eax
 1ba76a7: c1 f8 04                     	sarl	$0x4, %eax
 1ba76aa: 2d 00 03 00 00               	subl	$0x300, %eax            # imm = 0x300
 1ba76af: 48 98                        	cltq
 1ba76b1: 49 8d 3c 86                  	leaq	(%r14,%rax,4), %rdi
 1ba76b5: e9 ad fe ff ff               	jmp	0x1ba7567 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xd7>
 1ba76ba: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 1ba76c0: 8d 81 00 b2 ff ff            	leal	-0x4e00(%rcx), %eax
 1ba76c6: 66 3d 9f 51                  	cmpw	$0x519f, %ax            # imm = 0x519F
 1ba76ca: 76 2c                        	jbe	0x1ba76f8 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x268>
 1ba76cc: 8d 81 00 54 00 00            	leal	0x5400(%rcx), %eax
 1ba76d2: 66 3d 9f 2b                  	cmpw	$0x2b9f, %ax            # imm = 0x2B9F
 1ba76d6: 77 40                        	ja	0x1ba7718 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x288>
 1ba76d8: 0f b7 c1                     	movzwl	%cx, %eax
 1ba76db: 48 8d 3d fe 92 22 04         	leaq	0x42292fe(%rip), %rdi   # 0x5dd09e0 <exsl_ksc5601_uni2indx_pageac>
 1ba76e2: c1 f8 04                     	sarl	$0x4, %eax
 1ba76e5: 2d c0 0a 00 00               	subl	$0xac0, %eax            # imm = 0xAC0
 1ba76ea: 48 98                        	cltq
 1ba76ec: 48 8d 3c 87                  	leaq	(%rdi,%rax,4), %rdi
 1ba76f0: e9 72 fe ff ff               	jmp	0x1ba7567 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xd7>
 1ba76f5: 0f 1f 00                     	nopl	(%rax)
 1ba76f8: 0f b7 c1                     	movzwl	%cx, %eax
 1ba76fb: 48 8d 3d de 9d 22 04         	leaq	0x4229dde(%rip), %rdi   # 0x5dd14e0 <exsl_ksc5601_uni2indx_page4e>
 1ba7702: c1 f8 04                     	sarl	$0x4, %eax
 1ba7705: 2d e0 04 00 00               	subl	$0x4e0, %eax            # imm = 0x4E0
 1ba770a: 48 98                        	cltq
 1ba770c: 48 8d 3c 87                  	leaq	(%rdi,%rax,4), %rdi
 1ba7710: e9 52 fe ff ff               	jmp	0x1ba7567 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xd7>
 1ba7715: 0f 1f 00                     	nopl	(%rax)
 1ba7718: 8d 81 00 07 00 00            	leal	0x700(%rcx), %eax
 1ba771e: 66 3d 0f 01                  	cmpw	$0x10f, %ax             # imm = 0x10F
 1ba7722: 0f 86 88 00 00 00            	jbe	0x1ba77b0 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x320>
 1ba7728: 8d 81 00 01 00 00            	leal	0x100(%rcx), %eax
 1ba772e: 66 3d ef 00                  	cmpw	$0xef, %ax
 1ba7732: 0f 87 28 ff ff ff            	ja	0x1ba7660 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x1d0>
 1ba7738: 0f b7 c1                     	movzwl	%cx, %eax
 1ba773b: 48 8d 3d fe 91 22 04         	leaq	0x42291fe(%rip), %rdi   # 0x5dd0940 <exsl_ksc5601_uni2indx_pageff>
 1ba7742: c1 f8 04                     	sarl	$0x4, %eax
 1ba7745: 2d f0 0f 00 00               	subl	$0xff0, %eax            # imm = 0xFF0
 1ba774a: 48 98                        	cltq
 1ba774c: 48 8d 3c 87                  	leaq	(%rdi,%rax,4), %rdi
 1ba7750: e9 12 fe ff ff               	jmp	0x1ba7567 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xd7>
 1ba7755: 0f 1f 00                     	nopl	(%rax)
 1ba7758: 4c 8b 0b                     	movq	(%rbx), %r9
 1ba775b: 4c 8d 05 46 8a 22 04         	leaq	0x4228a46(%rip), %r8    # 0x5dd01a8 <NimoExSLMainLinux(int, char**)::__func__+0x1a8>
 1ba7762: 48 8d 15 87 91 22 04         	leaq	0x4229187(%rip), %rdx   # 0x5dd08f0 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)::__func__>
 1ba7769: 48 8d 35 68 8a 22 04         	leaq	0x4228a68(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba7770: b9 c7 00 00 00               	movl	$0xc7, %ecx
 1ba7775: bf 03 00 00 00               	movl	$0x3, %edi
 1ba777a: 31 c0                        	xorl	%eax, %eax
 1ba777c: e8 2f 7f c6 00               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 1ba7781: 4d 8b 0c 24                  	movq	(%r12), %r9
 1ba7785: 4c 8d 05 86 88 22 04         	leaq	0x4228886(%rip), %r8    # 0x5dd0012 <NimoExSLMainLinux(int, char**)::__func__+0x12>
 1ba778c: 48 8d 15 5d 91 22 04         	leaq	0x422915d(%rip), %rdx   # 0x5dd08f0 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)::__func__>
 1ba7793: 48 8d 35 3e 8a 22 04         	leaq	0x4228a3e(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba779a: b9 c8 00 00 00               	movl	$0xc8, %ecx
 1ba779f: bf 03 00 00 00               	movl	$0x3, %edi
 1ba77a4: 31 c0                        	xorl	%eax, %eax
 1ba77a6: e8 85 85 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba77ab: e9 97 fe ff ff               	jmp	0x1ba7647 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x1b7>
 1ba77b0: 0f b7 c1                     	movzwl	%cx, %eax
 1ba77b3: 48 8d 3d c6 91 22 04         	leaq	0x42291c6(%rip), %rdi   # 0x5dd0980 <exsl_ksc5601_uni2indx_pagef9>
 1ba77ba: c1 f8 04                     	sarl	$0x4, %eax
 1ba77bd: 2d 90 0f 00 00               	subl	$0xf90, %eax            # imm = 0xF90
 1ba77c2: 48 98                        	cltq
 1ba77c4: 48 8d 3c 87                  	leaq	(%rdi,%rax,4), %rdi
 1ba77c8: e9 9a fd ff ff               	jmp	0x1ba7567 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0xd7>
 1ba77cd: c6 45 00 00                  	movb	$0x0, (%rbp)
 1ba77d1: 45 31 ed                     	xorl	%r13d, %r13d
 1ba77d4: e9 36 fe ff ff               	jmp	0x1ba760f <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)+0x17f>
 1ba77d9: e8 b2 33 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba77de: 48 8d 3d 79 d4 1b 04         	leaq	0x41bd479(%rip), %rdi   # 0x5d64c5e <_IO_stdin_used+0x21e>
 1ba77e5: e8 66 37 8a ff               	callq	0x144af50 <_ZSt20__throw_length_errorPKc@plt>
 1ba77ea: 48 89 c3                     	movq	%rax, %rbx
 1ba77ed: 48 89 ef                     	movq	%rbp, %rdi
 1ba77f0: e8 ab 57 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba77f5: 48 89 df                     	movq	%rbx, %rdi
 1ba77f8: e8 63 5a 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba77fd: 0f 1f 00                     	nopl	(%rax)

0000000001ba7800 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&)>:
 1ba7800: 41 54                        	pushq	%r12
 1ba7802: 55                           	pushq	%rbp
 1ba7803: 53                           	pushq	%rbx
 1ba7804: 48 89 fb                     	movq	%rdi, %rbx
 1ba7807: 48 89 f7                     	movq	%rsi, %rdi
 1ba780a: 48 8d 6b 10                  	leaq	0x10(%rbx), %rbp
 1ba780e: 48 89 de                     	movq	%rbx, %rsi
 1ba7811: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba7815: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
 1ba781d: c6 43 10 00                  	movb	$0x0, 0x10(%rbx)
 1ba7821: 48 89 2b                     	movq	%rbp, (%rbx)
 1ba7824: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba782d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7832: 31 c0                        	xorl	%eax, %eax
 1ba7834: e8 57 fc ff ff               	callq	0x1ba7490 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&)>
 1ba7839: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 1ba783e: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 1ba7847: 48 89 d8                     	movq	%rbx, %rax
 1ba784a: 75 09                        	jne	0x1ba7855 <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&)+0x55>
 1ba784c: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba7850: 5b                           	popq	%rbx
 1ba7851: 5d                           	popq	%rbp
 1ba7852: 41 5c                        	popq	%r12
 1ba7854: c3                           	retq
 1ba7855: e8 36 33 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba785a: 48 8b 3b                     	movq	(%rbx), %rdi
 1ba785d: 49 89 c4                     	movq	%rax, %r12
 1ba7860: 48 39 ef                     	cmpq	%rbp, %rdi
 1ba7863: 74 05                        	je	0x1ba786a <utf16StringToEucKrString(std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>> const&)+0x6a>
 1ba7865: e8 46 36 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba786a: 4c 89 e7                     	movq	%r12, %rdi
 1ba786d: e8 ee 59 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba7872: 0f 1f 40 00                  	nopl	(%rax)
 1ba7876: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000001ba7880 <tolowercase(wchar_t)>:
 1ba7880: 48 83 ec 18                  	subq	$0x18, %rsp
 1ba7884: 8d 57 bf                     	leal	-0x41(%rdi), %edx
 1ba7887: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba7890: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7895: 31 c0                        	xorl	%eax, %eax
 1ba7897: 8d 47 20                     	leal	0x20(%rdi), %eax
 1ba789a: 66 83 fa 19                  	cmpw	$0x19, %dx
 1ba789e: 0f 47 c7                     	cmoval	%edi, %eax
 1ba78a1: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
 1ba78a6: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 1ba78af: 75 05                        	jne	0x1ba78b6 <tolowercase(wchar_t)+0x36>
 1ba78b1: 48 83 c4 18                  	addq	$0x18, %rsp
 1ba78b5: c3                           	retq
 1ba78b6: e8 d5 32 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba78bb: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000001ba78c0 <base64Encode(char const*, char*, int, int, bool)>:
 1ba78c0: 48 83 ec 68                  	subq	$0x68, %rsp
 1ba78c4: 66 0f 6f 05 14 36 23 04      	movdqa	0x4233614(%rip), %xmm0  # 0x5ddaee0 <exsl_ksc5601_2uni_page21+0x8c0>
 1ba78cc: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba78d5: 48 89 44 24 58               	movq	%rax, 0x58(%rsp)
 1ba78da: 31 c0                        	xorl	%eax, %eax
 1ba78dc: 0f 29 44 24 10               	movaps	%xmm0, 0x10(%rsp)
 1ba78e1: 66 0f 6f 05 07 36 23 04      	movdqa	0x4233607(%rip), %xmm0  # 0x5ddaef0 <exsl_ksc5601_2uni_page21+0x8d0>
 1ba78e9: 0f 29 44 24 20               	movaps	%xmm0, 0x20(%rsp)
 1ba78ee: 66 0f 6f 05 0a 36 23 04      	movdqa	0x423360a(%rip), %xmm0  # 0x5ddaf00 <exsl_ksc5601_2uni_page21+0x8e0>
 1ba78f6: 0f 29 44 24 30               	movaps	%xmm0, 0x30(%rsp)
 1ba78fb: 66 0f 6f 05 0d 36 23 04      	movdqa	0x423360d(%rip), %xmm0  # 0x5ddaf10 <exsl_ksc5601_2uni_page21+0x8f0>
 1ba7903: 0f 29 44 24 40               	movaps	%xmm0, 0x40(%rsp)
 1ba7908: 66 0f ef c0                  	pxor	%xmm0, %xmm0
 1ba790c: f3 0f 2a c2                  	cvtsi2ss	%edx, %xmm0
 1ba7910: f3 0f 5a c0                  	cvtss2sd	%xmm0, %xmm0
 1ba7914: f2 0f 59 05 04 36 23 04      	mulsd	0x4233604(%rip), %xmm0  # 0x5ddaf20 <exsl_ksc5601_2uni_page21+0x900>
 1ba791c: f2 0f 5e 05 04 36 23 04      	divsd	0x4233604(%rip), %xmm0  # 0x5ddaf28 <exsl_ksc5601_2uni_page21+0x908>
 1ba7924: f2 0f 58 05 04 36 23 04      	addsd	0x4233604(%rip), %xmm0  # 0x5ddaf30 <exsl_ksc5601_2uni_page21+0x910>
 1ba792c: f2 0f 2c c0                  	cvttsd2si	%xmm0, %eax
 1ba7930: 39 c8                        	cmpl	%ecx, %eax
 1ba7932: 0f 8d 98 01 00 00            	jge	0x1ba7ad0 <base64Encode(char const*, char*, int, int, bool)+0x210>
 1ba7938: 45 84 c0                     	testb	%r8b, %r8b
 1ba793b: 0f 84 d7 00 00 00            	je	0x1ba7a18 <base64Encode(char const*, char*, int, int, bool)+0x158>
 1ba7941: 85 d2                        	testl	%edx, %edx
 1ba7943: 0f 8e aa 00 00 00            	jle	0x1ba79f3 <base64Encode(char const*, char*, int, int, bool)+0x133>
 1ba7949: 48 83 c6 03                  	addq	$0x3, %rsi
 1ba794d: 41 b9 02 00 00 00            	movl	$0x2, %r9d
 1ba7953: b8 01 00 00 00               	movl	$0x1, %eax
 1ba7958: 41 ba 3d 00 00 00            	movl	$0x3d, %r10d
 1ba795e: eb 02                        	jmp	0x1ba7962 <base64Encode(char const*, char*, int, int, bool)+0xa2>
 1ba7960: 89 c8                        	movl	%ecx, %eax
 1ba7962: 0f b6 0f                     	movzbl	(%rdi), %ecx
 1ba7965: 39 d0                        	cmpl	%edx, %eax
 1ba7967: 88 4c 24 02                  	movb	%cl, 0x2(%rsp)
 1ba796b: 0f 8c c4 01 00 00            	jl	0x1ba7b35 <base64Encode(char const*, char*, int, int, bool)+0x275>
 1ba7971: 31 c9                        	xorl	%ecx, %ecx
 1ba7973: 41 39 d1                     	cmpl	%edx, %r9d
 1ba7976: 88 4c 24 01                  	movb	%cl, 0x1(%rsp)
 1ba797a: 0f 8c be 01 00 00            	jl	0x1ba7b3e <base64Encode(char const*, char*, int, int, bool)+0x27e>
 1ba7980: 45 31 c0                     	xorl	%r8d, %r8d
 1ba7983: 0f b6 4c 24 02               	movzbl	0x2(%rsp), %ecx
 1ba7988: 44 88 04 24                  	movb	%r8b, (%rsp)
 1ba798c: 41 83 e0 3f                  	andl	$0x3f, %r8d
 1ba7990: c0 e9 02                     	shrb	$0x2, %cl
 1ba7993: 83 e1 3f                     	andl	$0x3f, %ecx
 1ba7996: 0f b6 4c 0c 10               	movzbl	0x10(%rsp,%rcx), %ecx
 1ba799b: 88 4e fd                     	movb	%cl, -0x3(%rsi)
 1ba799e: 8b 0c 24                     	movl	(%rsp), %ecx
 1ba79a1: c1 e9 0c                     	shrl	$0xc, %ecx
 1ba79a4: 83 e1 3f                     	andl	$0x3f, %ecx
 1ba79a7: 0f b6 4c 0c 10               	movzbl	0x10(%rsp,%rcx), %ecx
 1ba79ac: 88 4e fe                     	movb	%cl, -0x2(%rsi)
 1ba79af: 0f b7 0c 24                  	movzwl	(%rsp), %ecx
 1ba79b3: 66 c1 e9 06                  	shrw	$0x6, %cx
 1ba79b7: 83 e1 3f                     	andl	$0x3f, %ecx
 1ba79ba: 39 d0                        	cmpl	%edx, %eax
 1ba79bc: 44 0f b6 5c 0c 10            	movzbl	0x10(%rsp,%rcx), %r11d
 1ba79c2: 42 0f b6 4c 04 10            	movzbl	0x10(%rsp,%r8), %ecx
 1ba79c8: 45 0f 4d da                  	cmovgel	%r10d, %r11d
 1ba79cc: 41 39 d1                     	cmpl	%edx, %r9d
 1ba79cf: 41 0f 4d ca                  	cmovgel	%r10d, %ecx
 1ba79d3: 44 88 5e ff                  	movb	%r11b, -0x1(%rsi)
 1ba79d7: 48 83 c7 03                  	addq	$0x3, %rdi
 1ba79db: 88 0e                        	movb	%cl, (%rsi)
 1ba79dd: 8d 48 03                     	leal	0x3(%rax), %ecx
 1ba79e0: 83 c0 02                     	addl	$0x2, %eax
 1ba79e3: 48 83 c6 04                  	addq	$0x4, %rsi
 1ba79e7: 41 83 c1 03                  	addl	$0x3, %r9d
 1ba79eb: 39 d0                        	cmpl	%edx, %eax
 1ba79ed: 0f 8c 6d ff ff ff            	jl	0x1ba7960 <base64Encode(char const*, char*, int, int, bool)+0xa0>
 1ba79f3: b8 01 00 00 00               	movl	$0x1, %eax
 1ba79f8: 48 8b 7c 24 58               	movq	0x58(%rsp), %rdi
 1ba79fd: 64 48 33 3c 25 28 00 00 00   	xorq	%fs:0x28, %rdi
 1ba7a06: 0f 85 3c 01 00 00            	jne	0x1ba7b48 <base64Encode(char const*, char*, int, int, bool)+0x288>
 1ba7a0c: 48 83 c4 68                  	addq	$0x68, %rsp
 1ba7a10: c3                           	retq
 1ba7a11: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 1ba7a18: 85 d2                        	testl	%edx, %edx
 1ba7a1a: 7e d7                        	jle	0x1ba79f3 <base64Encode(char const*, char*, int, int, bool)+0x133>
 1ba7a1c: 48 83 c6 03                  	addq	$0x3, %rsi
 1ba7a20: 41 b8 02 00 00 00            	movl	$0x2, %r8d
 1ba7a26: b9 01 00 00 00               	movl	$0x1, %ecx
 1ba7a2b: 41 ba 3d 00 00 00            	movl	$0x3d, %r10d
 1ba7a31: eb 07                        	jmp	0x1ba7a3a <base64Encode(char const*, char*, int, int, bool)+0x17a>
 1ba7a33: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7a38: 89 c1                        	movl	%eax, %ecx
 1ba7a3a: 0f b6 07                     	movzbl	(%rdi), %eax
 1ba7a3d: 39 ca                        	cmpl	%ecx, %edx
 1ba7a3f: 88 04 24                     	movb	%al, (%rsp)
 1ba7a42: 0f 8f db 00 00 00            	jg	0x1ba7b23 <base64Encode(char const*, char*, int, int, bool)+0x263>
 1ba7a48: 31 c0                        	xorl	%eax, %eax
 1ba7a4a: 41 39 d0                     	cmpl	%edx, %r8d
 1ba7a4d: 88 44 24 01                  	movb	%al, 0x1(%rsp)
 1ba7a51: 0f 8c d5 00 00 00            	jl	0x1ba7b2c <base64Encode(char const*, char*, int, int, bool)+0x26c>
 1ba7a57: 31 c0                        	xorl	%eax, %eax
 1ba7a59: 88 44 24 02                  	movb	%al, 0x2(%rsp)
 1ba7a5d: c0 e8 02                     	shrb	$0x2, %al
 1ba7a60: 83 e0 3f                     	andl	$0x3f, %eax
 1ba7a63: 0f b6 44 04 10               	movzbl	0x10(%rsp,%rax), %eax
 1ba7a68: 88 46 fd                     	movb	%al, -0x3(%rsi)
 1ba7a6b: 8b 04 24                     	movl	(%rsp), %eax
 1ba7a6e: c1 e8 0c                     	shrl	$0xc, %eax
 1ba7a71: 83 e0 3f                     	andl	$0x3f, %eax
 1ba7a74: 0f b6 44 04 10               	movzbl	0x10(%rsp,%rax), %eax
 1ba7a79: 88 46 fe                     	movb	%al, -0x2(%rsi)
 1ba7a7c: 0f b7 04 24                  	movzwl	(%rsp), %eax
 1ba7a80: 66 c1 e8 06                  	shrw	$0x6, %ax
 1ba7a84: 83 e0 3f                     	andl	$0x3f, %eax
 1ba7a87: 44 0f b6 4c 04 10            	movzbl	0x10(%rsp,%rax), %r9d
 1ba7a8d: 0f b6 04 24                  	movzbl	(%rsp), %eax
 1ba7a91: 83 e0 3f                     	andl	$0x3f, %eax
 1ba7a94: 39 ca                        	cmpl	%ecx, %edx
 1ba7a96: 0f b6 44 04 10               	movzbl	0x10(%rsp,%rax), %eax
 1ba7a9b: 45 0f 4e ca                  	cmovlel	%r10d, %r9d
 1ba7a9f: 41 39 d0                     	cmpl	%edx, %r8d
 1ba7aa2: 44 88 4e ff                  	movb	%r9b, -0x1(%rsi)
 1ba7aa6: 41 0f 4d c2                  	cmovgel	%r10d, %eax
 1ba7aaa: 48 83 c7 03                  	addq	$0x3, %rdi
 1ba7aae: 48 83 c6 04                  	addq	$0x4, %rsi
 1ba7ab2: 88 46 fc                     	movb	%al, -0x4(%rsi)
 1ba7ab5: 8d 41 03                     	leal	0x3(%rcx), %eax
 1ba7ab8: 83 c1 02                     	addl	$0x2, %ecx
 1ba7abb: 41 83 c0 03                  	addl	$0x3, %r8d
 1ba7abf: 39 ca                        	cmpl	%ecx, %edx
 1ba7ac1: 0f 8f 71 ff ff ff            	jg	0x1ba7a38 <base64Encode(char const*, char*, int, int, bool)+0x178>
 1ba7ac7: e9 27 ff ff ff               	jmp	0x1ba79f3 <base64Encode(char const*, char*, int, int, bool)+0x133>
 1ba7acc: 0f 1f 40 00                  	nopl	(%rax)
 1ba7ad0: 4c 8d 05 31 87 22 04         	leaq	0x4228731(%rip), %r8    # 0x5dd0208 <NimoExSLMainLinux(int, char**)::__func__+0x208>
 1ba7ad7: 48 8d 15 fa 8d 22 04         	leaq	0x4228dfa(%rip), %rdx   # 0x5dd08d8 <base64Encode(char const*, char*, int, int, bool)::__func__>
 1ba7ade: 48 8d 35 f3 86 22 04         	leaq	0x42286f3(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba7ae5: b9 17 01 00 00               	movl	$0x117, %ecx            # imm = 0x117
 1ba7aea: bf 03 00 00 00               	movl	$0x3, %edi
 1ba7aef: 31 c0                        	xorl	%eax, %eax
 1ba7af1: e8 3a 82 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba7af6: 4c 8d 05 f6 43 1c 04         	leaq	0x41c43f6(%rip), %r8    # 0x5d6bef3 <._1077+0x813>
 1ba7afd: 48 8d 15 c4 8d 22 04         	leaq	0x4228dc4(%rip), %rdx   # 0x5dd08c8 <exAssert(bool)::__FUNCTION__>
 1ba7b04: 48 8d 35 bd 76 22 04         	leaq	0x42276bd(%rip), %rsi   # 0x5dcf1c8 <typeinfo name for NimoExSLMethodDeclare+0x98>
 1ba7b0b: 31 c0                        	xorl	%eax, %eax
 1ba7b0d: b9 69 00 00 00               	movl	$0x69, %ecx
 1ba7b12: bf 03 00 00 00               	movl	$0x3, %edi
 1ba7b17: e8 14 82 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba7b1c: 31 c0                        	xorl	%eax, %eax
 1ba7b1e: e9 d5 fe ff ff               	jmp	0x1ba79f8 <base64Encode(char const*, char*, int, int, bool)+0x138>
 1ba7b23: 0f b6 47 01                  	movzbl	0x1(%rdi), %eax
 1ba7b27: e9 1e ff ff ff               	jmp	0x1ba7a4a <base64Encode(char const*, char*, int, int, bool)+0x18a>
 1ba7b2c: 0f b6 47 02                  	movzbl	0x2(%rdi), %eax
 1ba7b30: e9 24 ff ff ff               	jmp	0x1ba7a59 <base64Encode(char const*, char*, int, int, bool)+0x199>
 1ba7b35: 0f b6 4f 01                  	movzbl	0x1(%rdi), %ecx
 1ba7b39: e9 35 fe ff ff               	jmp	0x1ba7973 <base64Encode(char const*, char*, int, int, bool)+0xb3>
 1ba7b3e: 44 0f b6 47 02               	movzbl	0x2(%rdi), %r8d
 1ba7b43: e9 3b fe ff ff               	jmp	0x1ba7983 <base64Encode(char const*, char*, int, int, bool)+0xc3>
 1ba7b48: e8 43 30 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba7b4d: 0f 1f 00                     	nopl	(%rax)

0000000001ba7b50 <base64Decode(char const*, char*, int*, bool)>:
 1ba7b50: 41 55                        	pushq	%r13
 1ba7b52: 41 54                        	pushq	%r12
 1ba7b54: 41 89 cd                     	movl	%ecx, %r13d
 1ba7b57: 55                           	pushq	%rbp
 1ba7b58: 53                           	pushq	%rbx
 1ba7b59: 48 89 fd                     	movq	%rdi, %rbp
 1ba7b5c: 49 89 f4                     	movq	%rsi, %r12
 1ba7b5f: b9 80 00 00 00               	movl	$0x80, %ecx
 1ba7b64: 48 8d 35 15 89 22 04         	leaq	0x4228915(%rip), %rsi   # 0x5dd0480 <NimoExSLMainLinux(int, char**)::__func__+0x480>
 1ba7b6b: 48 81 ec 28 04 00 00         	subq	$0x428, %rsp            # imm = 0x428
 1ba7b72: 48 89 d3                     	movq	%rdx, %rbx
 1ba7b75: 48 8d 7c 24 10               	leaq	0x10(%rsp), %rdi
 1ba7b7a: f3 48 a5                     	rep		movsq	(%rsi), %es:(%rdi)
 1ba7b7d: 48 89 ef                     	movq	%rbp, %rdi
 1ba7b80: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba7b89: 48 89 84 24 18 04 00 00      	movq	%rax, 0x418(%rsp)
 1ba7b91: 31 c0                        	xorl	%eax, %eax
 1ba7b93: e8 88 54 8a ff               	callq	0x144d020 <strlen@plt>
 1ba7b98: 66 0f ef c0                  	pxor	%xmm0, %xmm0
 1ba7b9c: 48 85 db                     	testq	%rbx, %rbx
 1ba7b9f: f3 0f 2a c0                  	cvtsi2ss	%eax, %xmm0
 1ba7ba3: f3 0f 5a c0                  	cvtss2sd	%xmm0, %xmm0
 1ba7ba7: f2 0f 59 05 89 33 23 04      	mulsd	0x4233389(%rip), %xmm0  # 0x5ddaf38 <exsl_ksc5601_2uni_page21+0x918>
 1ba7baf: f2 0f 58 05 79 33 23 04      	addsd	0x4233379(%rip), %xmm0  # 0x5ddaf30 <exsl_ksc5601_2uni_page21+0x910>
 1ba7bb7: 0f 84 13 02 00 00            	je	0x1ba7dd0 <base64Decode(char const*, char*, int*, bool)+0x280>
 1ba7bbd: f2 0f 2c d0                  	cvttsd2si	%xmm0, %edx
 1ba7bc1: 3b 13                        	cmpl	(%rbx), %edx
 1ba7bc3: 0f 8d 07 02 00 00            	jge	0x1ba7dd0 <base64Decode(char const*, char*, int*, bool)+0x280>
 1ba7bc9: 45 84 ed                     	testb	%r13b, %r13b
 1ba7bcc: 0f 84 d6 00 00 00            	je	0x1ba7ca8 <base64Decode(char const*, char*, int*, bool)+0x158>
 1ba7bd2: 85 c0                        	testl	%eax, %eax
 1ba7bd4: 0f 8e 46 02 00 00            	jle	0x1ba7e20 <base64Decode(char const*, char*, int*, bool)+0x2d0>
 1ba7bda: 83 e8 01                     	subl	$0x1, %eax
 1ba7bdd: 48 89 ef                     	movq	%rbp, %rdi
 1ba7be0: 4c 89 e6                     	movq	%r12, %rsi
 1ba7be3: c1 e8 02                     	shrl	$0x2, %eax
 1ba7be6: 45 31 c0                     	xorl	%r8d, %r8d
 1ba7be9: 89 c2                        	movl	%eax, %edx
 1ba7beb: 4c 8d 4c 52 03               	leaq	0x3(%rdx,%rdx,2), %r9
 1ba7bf0: 4d 01 e1                     	addq	%r12, %r9
 1ba7bf3: eb 63                        	jmp	0x1ba7c58 <base64Decode(char const*, char*, int*, bool)+0x108>
 1ba7bf5: 0f 1f 00                     	nopl	(%rax)
 1ba7bf8: 8b 4c 94 10                  	movl	0x10(%rsp,%rdx,4), %ecx
 1ba7bfc: 83 e1 3f                     	andl	$0x3f, %ecx
 1ba7bff: 0f b7 14 24                  	movzwl	(%rsp), %edx
 1ba7c03: 83 e1 3f                     	andl	$0x3f, %ecx
 1ba7c06: c1 e1 06                     	shll	$0x6, %ecx
 1ba7c09: 66 81 e2 3f f0               	andw	$0xf03f, %dx            # imm = 0xF03F
 1ba7c0e: 09 d1                        	orl	%edx, %ecx
 1ba7c10: 66 89 0c 24                  	movw	%cx, (%rsp)
 1ba7c14: 0f b6 57 03                  	movzbl	0x3(%rdi), %edx
 1ba7c18: 80 fa 3d                     	cmpb	$0x3d, %dl
 1ba7c1b: 0f 84 6f 01 00 00            	je	0x1ba7d90 <base64Decode(char const*, char*, int*, bool)+0x240>
 1ba7c21: 8b 54 94 10                  	movl	0x10(%rsp,%rdx,4), %edx
 1ba7c25: 83 e2 3f                     	andl	$0x3f, %edx
 1ba7c28: 0f b6 0c 24                  	movzbl	(%rsp), %ecx
 1ba7c2c: 48 83 c6 03                  	addq	$0x3, %rsi
 1ba7c30: 48 83 c7 04                  	addq	$0x4, %rdi
 1ba7c34: 83 e1 c0                     	andl	$-0x40, %ecx
 1ba7c37: 09 ca                        	orl	%ecx, %edx
 1ba7c39: 0f b6 4c 24 02               	movzbl	0x2(%rsp), %ecx
 1ba7c3e: 88 56 ff                     	movb	%dl, -0x1(%rsi)
 1ba7c41: 88 14 24                     	movb	%dl, (%rsp)
 1ba7c44: 88 4e fd                     	movb	%cl, -0x3(%rsi)
 1ba7c47: 0f b6 4c 24 01               	movzbl	0x1(%rsp), %ecx
 1ba7c4c: 88 4e fe                     	movb	%cl, -0x2(%rsi)
 1ba7c4f: 49 39 f1                     	cmpq	%rsi, %r9
 1ba7c52: 0f 84 48 01 00 00            	je	0x1ba7da0 <base64Decode(char const*, char*, int*, bool)+0x250>
 1ba7c58: 0f b6 17                     	movzbl	(%rdi), %edx
 1ba7c5b: 0f b6 4c 24 02               	movzbl	0x2(%rsp), %ecx
 1ba7c60: 8b 54 94 10                  	movl	0x10(%rsp,%rdx,4), %edx
 1ba7c64: 83 e1 03                     	andl	$0x3, %ecx
 1ba7c67: c1 e2 02                     	shll	$0x2, %edx
 1ba7c6a: 09 ca                        	orl	%ecx, %edx
 1ba7c6c: 88 54 24 02                  	movb	%dl, 0x2(%rsp)
 1ba7c70: 0f b6 57 01                  	movzbl	0x1(%rdi), %edx
 1ba7c74: 8b 0c 24                     	movl	(%rsp), %ecx
 1ba7c77: 0f b6 54 94 10               	movzbl	0x10(%rsp,%rdx,4), %edx
 1ba7c7c: 81 e1 ff 0f fc ff            	andl	$0xfffc0fff, %ecx       # imm = 0xFFFC0FFF
 1ba7c82: 83 e2 3f                     	andl	$0x3f, %edx
 1ba7c85: c1 e2 0c                     	shll	$0xc, %edx
 1ba7c88: 09 ca                        	orl	%ecx, %edx
 1ba7c8a: 89 14 24                     	movl	%edx, (%rsp)
 1ba7c8d: 0f b6 57 02                  	movzbl	0x2(%rdi), %edx
 1ba7c91: 80 fa 3d                     	cmpb	$0x3d, %dl
 1ba7c94: 0f 85 5e ff ff ff            	jne	0x1ba7bf8 <base64Decode(char const*, char*, int*, bool)+0xa8>
 1ba7c9a: 41 83 c0 01                  	addl	$0x1, %r8d
 1ba7c9e: 31 c9                        	xorl	%ecx, %ecx
 1ba7ca0: e9 5a ff ff ff               	jmp	0x1ba7bff <base64Decode(char const*, char*, int*, bool)+0xaf>
 1ba7ca5: 0f 1f 00                     	nopl	(%rax)
 1ba7ca8: 85 c0                        	testl	%eax, %eax
 1ba7caa: 0f 8e 70 01 00 00            	jle	0x1ba7e20 <base64Decode(char const*, char*, int*, bool)+0x2d0>
 1ba7cb0: 83 e8 01                     	subl	$0x1, %eax
 1ba7cb3: 48 89 ef                     	movq	%rbp, %rdi
 1ba7cb6: 4c 89 e6                     	movq	%r12, %rsi
 1ba7cb9: c1 e8 02                     	shrl	$0x2, %eax
 1ba7cbc: 45 31 c0                     	xorl	%r8d, %r8d
 1ba7cbf: 89 c2                        	movl	%eax, %edx
 1ba7cc1: 4c 8d 4c 52 03               	leaq	0x3(%rdx,%rdx,2), %r9
 1ba7cc6: 4d 01 e1                     	addq	%r12, %r9
 1ba7cc9: eb 61                        	jmp	0x1ba7d2c <base64Decode(char const*, char*, int*, bool)+0x1dc>
 1ba7ccb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7cd0: 8b 4c 94 10                  	movl	0x10(%rsp,%rdx,4), %ecx
 1ba7cd4: 83 e1 3f                     	andl	$0x3f, %ecx
 1ba7cd7: 0f b7 14 24                  	movzwl	(%rsp), %edx
 1ba7cdb: 83 e1 3f                     	andl	$0x3f, %ecx
 1ba7cde: c1 e1 06                     	shll	$0x6, %ecx
 1ba7ce1: 66 81 e2 3f f0               	andw	$0xf03f, %dx            # imm = 0xF03F
 1ba7ce6: 09 d1                        	orl	%edx, %ecx
 1ba7ce8: 66 89 0c 24                  	movw	%cx, (%rsp)
 1ba7cec: 0f b6 57 03                  	movzbl	0x3(%rdi), %edx
 1ba7cf0: 80 fa 3d                     	cmpb	$0x3d, %dl
 1ba7cf3: 0f 84 87 00 00 00            	je	0x1ba7d80 <base64Decode(char const*, char*, int*, bool)+0x230>
 1ba7cf9: 8b 54 94 10                  	movl	0x10(%rsp,%rdx,4), %edx
 1ba7cfd: 83 e2 3f                     	andl	$0x3f, %edx
 1ba7d00: 0f b6 0c 24                  	movzbl	(%rsp), %ecx
 1ba7d04: 48 83 c6 03                  	addq	$0x3, %rsi
 1ba7d08: 48 83 c7 04                  	addq	$0x4, %rdi
 1ba7d0c: 83 e1 c0                     	andl	$-0x40, %ecx
 1ba7d0f: 09 ca                        	orl	%ecx, %edx
 1ba7d11: 88 56 fd                     	movb	%dl, -0x3(%rsi)
 1ba7d14: 88 14 24                     	movb	%dl, (%rsp)
 1ba7d17: 0f b6 54 24 01               	movzbl	0x1(%rsp), %edx
 1ba7d1c: 88 56 fe                     	movb	%dl, -0x2(%rsi)
 1ba7d1f: 0f b6 54 24 02               	movzbl	0x2(%rsp), %edx
 1ba7d24: 88 56 ff                     	movb	%dl, -0x1(%rsi)
 1ba7d27: 4c 39 ce                     	cmpq	%r9, %rsi
 1ba7d2a: 74 74                        	je	0x1ba7da0 <base64Decode(char const*, char*, int*, bool)+0x250>
 1ba7d2c: 0f b6 17                     	movzbl	(%rdi), %edx
 1ba7d2f: 0f b6 4c 24 02               	movzbl	0x2(%rsp), %ecx
 1ba7d34: 8b 54 94 10                  	movl	0x10(%rsp,%rdx,4), %edx
 1ba7d38: 83 e1 03                     	andl	$0x3, %ecx
 1ba7d3b: c1 e2 02                     	shll	$0x2, %edx
 1ba7d3e: 09 ca                        	orl	%ecx, %edx
 1ba7d40: 88 54 24 02                  	movb	%dl, 0x2(%rsp)
 1ba7d44: 0f b6 57 01                  	movzbl	0x1(%rdi), %edx
 1ba7d48: 8b 0c 24                     	movl	(%rsp), %ecx
 1ba7d4b: 0f b6 54 94 10               	movzbl	0x10(%rsp,%rdx,4), %edx
 1ba7d50: 81 e1 ff 0f fc ff            	andl	$0xfffc0fff, %ecx       # imm = 0xFFFC0FFF
 1ba7d56: 83 e2 3f                     	andl	$0x3f, %edx
 1ba7d59: c1 e2 0c                     	shll	$0xc, %edx
 1ba7d5c: 09 ca                        	orl	%ecx, %edx
 1ba7d5e: 89 14 24                     	movl	%edx, (%rsp)
 1ba7d61: 0f b6 57 02                  	movzbl	0x2(%rdi), %edx
 1ba7d65: 80 fa 3d                     	cmpb	$0x3d, %dl
 1ba7d68: 0f 85 62 ff ff ff            	jne	0x1ba7cd0 <base64Decode(char const*, char*, int*, bool)+0x180>
 1ba7d6e: 41 83 c0 01                  	addl	$0x1, %r8d
 1ba7d72: 31 c9                        	xorl	%ecx, %ecx
 1ba7d74: e9 5e ff ff ff               	jmp	0x1ba7cd7 <base64Decode(char const*, char*, int*, bool)+0x187>
 1ba7d79: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 1ba7d80: 41 83 c0 01                  	addl	$0x1, %r8d
 1ba7d84: 31 d2                        	xorl	%edx, %edx
 1ba7d86: e9 75 ff ff ff               	jmp	0x1ba7d00 <base64Decode(char const*, char*, int*, bool)+0x1b0>
 1ba7d8b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7d90: 41 83 c0 01                  	addl	$0x1, %r8d
 1ba7d94: 31 d2                        	xorl	%edx, %edx
 1ba7d96: e9 8d fe ff ff               	jmp	0x1ba7c28 <base64Decode(char const*, char*, int*, bool)+0xd8>
 1ba7d9b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7da0: 8d 44 40 03                  	leal	0x3(%rax,%rax,2), %eax
 1ba7da4: 44 29 c0                     	subl	%r8d, %eax
 1ba7da7: 89 03                        	movl	%eax, (%rbx)
 1ba7da9: b8 01 00 00 00               	movl	$0x1, %eax
 1ba7dae: 48 8b 9c 24 18 04 00 00      	movq	0x418(%rsp), %rbx
 1ba7db6: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
 1ba7dbf: 75 66                        	jne	0x1ba7e27 <base64Decode(char const*, char*, int*, bool)+0x2d7>
 1ba7dc1: 48 81 c4 28 04 00 00         	addq	$0x428, %rsp            # imm = 0x428
 1ba7dc8: 5b                           	popq	%rbx
 1ba7dc9: 5d                           	popq	%rbp
 1ba7dca: 41 5c                        	popq	%r12
 1ba7dcc: 41 5d                        	popq	%r13
 1ba7dce: c3                           	retq
 1ba7dcf: 90                           	nop
 1ba7dd0: 4c 8d 05 81 84 22 04         	leaq	0x4228481(%rip), %r8    # 0x5dd0258 <NimoExSLMainLinux(int, char**)::__func__+0x258>
 1ba7dd7: 48 8d 15 da 8a 22 04         	leaq	0x4228ada(%rip), %rdx   # 0x5dd08b8 <base64Decode(char const*, char*, int*, bool)::__func__>
 1ba7dde: 48 8d 35 f3 83 22 04         	leaq	0x42283f3(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba7de5: b9 80 01 00 00               	movl	$0x180, %ecx            # imm = 0x180
 1ba7dea: bf 03 00 00 00               	movl	$0x3, %edi
 1ba7def: 31 c0                        	xorl	%eax, %eax
 1ba7df1: e8 3a 7f c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba7df6: 4c 8d 05 f6 40 1c 04         	leaq	0x41c40f6(%rip), %r8    # 0x5d6bef3 <._1077+0x813>
 1ba7dfd: 48 8d 15 c4 8a 22 04         	leaq	0x4228ac4(%rip), %rdx   # 0x5dd08c8 <exAssert(bool)::__FUNCTION__>
 1ba7e04: 48 8d 35 bd 73 22 04         	leaq	0x42273bd(%rip), %rsi   # 0x5dcf1c8 <typeinfo name for NimoExSLMethodDeclare+0x98>
 1ba7e0b: 31 c0                        	xorl	%eax, %eax
 1ba7e0d: b9 69 00 00 00               	movl	$0x69, %ecx
 1ba7e12: bf 03 00 00 00               	movl	$0x3, %edi
 1ba7e17: e8 14 7f c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba7e1c: 31 c0                        	xorl	%eax, %eax
 1ba7e1e: eb 8e                        	jmp	0x1ba7dae <base64Decode(char const*, char*, int*, bool)+0x25e>
 1ba7e20: 31 c0                        	xorl	%eax, %eax
 1ba7e22: e9 80 ff ff ff               	jmp	0x1ba7da7 <base64Decode(char const*, char*, int*, bool)+0x257>
 1ba7e27: e8 64 2d 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba7e2c: 0f 1f 40 00                  	nopl	(%rax)

0000000001ba7e30 <stringToHash(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)>:
 1ba7e30: 48 83 ec 18                  	subq	$0x18, %rsp
 1ba7e34: 48 8b 77 08                  	movq	0x8(%rdi), %rsi
 1ba7e38: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba7e41: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7e46: 31 c0                        	xorl	%eax, %eax
 1ba7e48: 48 85 f6                     	testq	%rsi, %rsi
 1ba7e4b: 74 28                        	je	0x1ba7e75 <stringToHash(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x45>
 1ba7e4d: 48 8b 17                     	movq	(%rdi), %rdx
 1ba7e50: b8 a5 b5 02 00               	movl	$0x2b5a5, %eax          # imm = 0x2B5A5
 1ba7e55: 48 01 d6                     	addq	%rdx, %rsi
 1ba7e58: eb 0d                        	jmp	0x1ba7e67 <stringToHash(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x37>
 1ba7e5a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 1ba7e60: 89 c1                        	movl	%eax, %ecx
 1ba7e62: c1 e1 05                     	shll	$0x5, %ecx
 1ba7e65: 01 c8                        	addl	%ecx, %eax
 1ba7e67: 0f be 0a                     	movsbl	(%rdx), %ecx
 1ba7e6a: 48 83 c2 01                  	addq	$0x1, %rdx
 1ba7e6e: 01 c8                        	addl	%ecx, %eax
 1ba7e70: 48 39 d6                     	cmpq	%rdx, %rsi
 1ba7e73: 75 eb                        	jne	0x1ba7e60 <stringToHash(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x30>
 1ba7e75: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
 1ba7e7a: 64 48 33 3c 25 28 00 00 00   	xorq	%fs:0x28, %rdi
 1ba7e83: 75 05                        	jne	0x1ba7e8a <stringToHash(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x5a>
 1ba7e85: 48 83 c4 18                  	addq	$0x18, %rsp
 1ba7e89: c3                           	retq
 1ba7e8a: e8 01 2d 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba7e8f: 90                           	nop

0000000001ba7e90 <convertCodetoISOName_EU[abi:cxx11](unsigned long)>:
 1ba7e90: 41 56                        	pushq	%r14
 1ba7e92: 41 55                        	pushq	%r13
 1ba7e94: 41 54                        	pushq	%r12
 1ba7e96: 55                           	pushq	%rbp
 1ba7e97: 49 89 f4                     	movq	%rsi, %r12
 1ba7e9a: 53                           	pushq	%rbx
 1ba7e9b: 48 89 fb                     	movq	%rdi, %rbx
 1ba7e9e: bf 78 01 00 00               	movl	$0x178, %edi            # imm = 0x178
 1ba7ea3: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba7ea7: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba7eb0: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba7eb5: 31 c0                        	xorl	%eax, %eax
 1ba7eb7: e8 74 5f 8a ff               	callq	0x144de30 <_Znwm@plt>
 1ba7ebc: 48 89 c5                     	movq	%rax, %rbp
 1ba7ebf: 48 8b 05 9a 89 95 05         	movq	0x595899a(%rip), %rax   # 0x7500860 <._118>
 1ba7ec6: 48 ba db 34 b6 d7 82 de 1b 43	movabsq	$0x431bde82d7b634db, %rdx # imm = 0x431BDE82D7B634DB
 1ba7ed0: 48 8d 7d 08                  	leaq	0x8(%rbp), %rdi
 1ba7ed4: 48 89 e9                     	movq	%rbp, %rcx
 1ba7ed7: 48 8d 35 82 89 95 05         	leaq	0x5958982(%rip), %rsi   # 0x7500860 <._118>
 1ba7ede: 48 89 45 00                  	movq	%rax, (%rbp)
 1ba7ee2: 48 8b 05 e7 8a 95 05         	movq	0x5958ae7(%rip), %rax   # 0x75009d0 <._118+0x170>
 1ba7ee9: 48 83 e7 f8                  	andq	$-0x8, %rdi
 1ba7eed: 48 29 f9                     	subq	%rdi, %rcx
 1ba7ef0: 48 29 ce                     	subq	%rcx, %rsi
 1ba7ef3: 81 c1 78 01 00 00            	addl	$0x178, %ecx            # imm = 0x178
 1ba7ef9: 48 89 85 70 01 00 00         	movq	%rax, 0x170(%rbp)
 1ba7f00: 4c 89 e0                     	movq	%r12, %rax
 1ba7f03: c1 e9 03                     	shrl	$0x3, %ecx
 1ba7f06: 48 f7 e2                     	mulq	%rdx
 1ba7f09: f3 48 a5                     	rep		movsq	(%rsi), %es:(%rdi)
 1ba7f0c: 48 c1 ea 12                  	shrq	$0x12, %rdx
 1ba7f10: 48 83 ea 01                  	subq	$0x1, %rdx
 1ba7f14: 48 83 fa 2e                  	cmpq	$0x2e, %rdx
 1ba7f18: 77 46                        	ja	0x1ba7f60 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0xd0>
 1ba7f1a: 4c 8b 74 d5 00               	movq	(%rbp,%rdx,8), %r14
 1ba7f1f: 4c 8d 63 10                  	leaq	0x10(%rbx), %r12
 1ba7f23: 4c 89 23                     	movq	%r12, (%rbx)
 1ba7f26: 4d 85 f6                     	testq	%r14, %r14
 1ba7f29: 0f 84 91 00 00 00            	je	0x1ba7fc0 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0x130>
 1ba7f2f: 4c 89 f7                     	movq	%r14, %rdi
 1ba7f32: e8 e9 50 8a ff               	callq	0x144d020 <strlen@plt>
 1ba7f37: 48 83 f8 0f                  	cmpq	$0xf, %rax
 1ba7f3b: 49 89 c5                     	movq	%rax, %r13
 1ba7f3e: 48 89 04 24                  	movq	%rax, (%rsp)
 1ba7f42: 0f 87 88 00 00 00            	ja	0x1ba7fd0 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0x140>
 1ba7f48: 48 83 f8 01                  	cmpq	$0x1, %rax
 1ba7f4c: 75 52                        	jne	0x1ba7fa0 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0x110>
 1ba7f4e: 41 0f b6 16                  	movzbl	(%r14), %edx
 1ba7f52: 88 53 10                     	movb	%dl, 0x10(%rbx)
 1ba7f55: 48 89 43 08                  	movq	%rax, 0x8(%rbx)
 1ba7f59: 41 c6 04 04 00               	movb	$0x0, (%r12,%rax)
 1ba7f5e: eb 13                        	jmp	0x1ba7f73 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0xe3>
 1ba7f60: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba7f64: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
 1ba7f6c: c6 43 10 00                  	movb	$0x0, 0x10(%rbx)
 1ba7f70: 48 89 03                     	movq	%rax, (%rbx)
 1ba7f73: 48 89 ef                     	movq	%rbp, %rdi
 1ba7f76: e8 35 2f 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba7f7b: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
 1ba7f80: 64 48 33 34 25 28 00 00 00   	xorq	%fs:0x28, %rsi
 1ba7f89: 48 89 d8                     	movq	%rbx, %rax
 1ba7f8c: 75 72                        	jne	0x1ba8000 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0x170>
 1ba7f8e: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba7f92: 5b                           	popq	%rbx
 1ba7f93: 5d                           	popq	%rbp
 1ba7f94: 41 5c                        	popq	%r12
 1ba7f96: 41 5d                        	popq	%r13
 1ba7f98: 41 5e                        	popq	%r14
 1ba7f9a: c3                           	retq
 1ba7f9b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba7fa0: 4c 89 e7                     	movq	%r12, %rdi
 1ba7fa3: 4c 89 ea                     	movq	%r13, %rdx
 1ba7fa6: 4c 89 f6                     	movq	%r14, %rsi
 1ba7fa9: e8 e2 5c 8a ff               	callq	0x144dc90 <memcpy@plt>
 1ba7fae: 48 8b 04 24                  	movq	(%rsp), %rax
 1ba7fb2: 4c 8b 23                     	movq	(%rbx), %r12
 1ba7fb5: eb 9e                        	jmp	0x1ba7f55 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0xc5>
 1ba7fb7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 1ba7fc0: 48 8d 3d 81 ca 1b 04         	leaq	0x41bca81(%rip), %rdi   # 0x5d64a48 <_IO_stdin_used+0x8>
 1ba7fc7: e8 54 5c 8a ff               	callq	0x144dc20 <_ZSt19__throw_logic_errorPKc@plt>
 1ba7fcc: 0f 1f 40 00                  	nopl	(%rax)
 1ba7fd0: 48 89 e6                     	movq	%rsp, %rsi
 1ba7fd3: 31 d2                        	xorl	%edx, %edx
 1ba7fd5: 48 89 df                     	movq	%rbx, %rdi
 1ba7fd8: e8 93 52 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba7fdd: 48 8b 14 24                  	movq	(%rsp), %rdx
 1ba7fe1: 48 89 03                     	movq	%rax, (%rbx)
 1ba7fe4: 48 89 c7                     	movq	%rax, %rdi
 1ba7fe7: 48 89 53 10                  	movq	%rdx, 0x10(%rbx)
 1ba7feb: eb b6                        	jmp	0x1ba7fa3 <convertCodetoISOName_EU[abi:cxx11](unsigned long)+0x113>
 1ba7fed: 48 89 c3                     	movq	%rax, %rbx
 1ba7ff0: 48 89 ef                     	movq	%rbp, %rdi
 1ba7ff3: e8 b8 2e 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba7ff8: 48 89 df                     	movq	%rbx, %rdi
 1ba7ffb: e8 60 52 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba8000: e8 8b 2b 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba8005: 90                           	nop
 1ba8006: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000001ba8010 <convertCodetoISOName_NA[abi:cxx11](unsigned long)>:
 1ba8010: 41 56                        	pushq	%r14
 1ba8012: 41 55                        	pushq	%r13
 1ba8014: 41 54                        	pushq	%r12
 1ba8016: 55                           	pushq	%rbp
 1ba8017: 49 89 f4                     	movq	%rsi, %r12
 1ba801a: 53                           	pushq	%rbx
 1ba801b: 48 89 fb                     	movq	%rdi, %rbx
 1ba801e: bf 60 06 00 00               	movl	$0x660, %edi            # imm = 0x660
 1ba8023: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba8027: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba8030: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba8035: 31 c0                        	xorl	%eax, %eax
 1ba8037: e8 f4 5d 8a ff               	callq	0x144de30 <_Znwm@plt>
 1ba803c: 48 8d 15 1d 88 95 05         	leaq	0x595881d(%rip), %rdx   # 0x7500860 <._118>
 1ba8043: 48 89 c5                     	movq	%rax, %rbp
 1ba8046: 48 89 c1                     	movq	%rax, %rcx
 1ba8049: 48 8d 05 b0 81 95 05         	leaq	0x59581b0(%rip), %rax   # 0x7500200 <._119>
 1ba8050: 48 85 c9                     	testq	%rcx, %rcx
 1ba8053: 74 0e                        	je	0x1ba8063 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x53>
 1ba8055: 4c 8b 08                     	movq	(%rax), %r9
 1ba8058: 4c 8b 50 08                  	movq	0x8(%rax), %r10
 1ba805c: 4c 89 09                     	movq	%r9, (%rcx)
 1ba805f: 4c 89 51 08                  	movq	%r10, 0x8(%rcx)
 1ba8063: 48 83 c0 10                  	addq	$0x10, %rax
 1ba8067: 48 83 c1 10                  	addq	$0x10, %rcx
 1ba806b: 48 39 d0                     	cmpq	%rdx, %rax
 1ba806e: 75 e0                        	jne	0x1ba8050 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x40>
 1ba8070: 4c 89 e0                     	movq	%r12, %rax
 1ba8073: 48 ba db 34 b6 d7 82 de 1b 43	movabsq	$0x431bde82d7b634db, %rdx # imm = 0x431BDE82D7B634DB
 1ba807d: 48 f7 e2                     	mulq	%rdx
 1ba8080: 48 63 45 00                  	movslq	(%rbp), %rax
 1ba8084: 48 c1 ea 12                  	shrq	$0x12, %rdx
 1ba8088: 48 39 c2                     	cmpq	%rax, %rdx
 1ba808b: 74 63                        	je	0x1ba80f0 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0xe0>
 1ba808d: 48 8d 4d 10                  	leaq	0x10(%rbp), %rcx
 1ba8091: 31 c0                        	xorl	%eax, %eax
 1ba8093: eb 16                        	jmp	0x1ba80ab <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x9b>
 1ba8095: 0f 1f 00                     	nopl	(%rax)
 1ba8098: 48 89 cf                     	movq	%rcx, %rdi
 1ba809b: 48 83 c0 01                  	addq	$0x1, %rax
 1ba809f: 48 83 c1 10                  	addq	$0x10, %rcx
 1ba80a3: 4c 63 07                     	movslq	(%rdi), %r8
 1ba80a6: 4c 39 c2                     	cmpq	%r8, %rdx
 1ba80a9: 74 4d                        	je	0x1ba80f8 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0xe8>
 1ba80ab: 48 83 f8 65                  	cmpq	$0x65, %rax
 1ba80af: 75 e7                        	jne	0x1ba8098 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x88>
 1ba80b1: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba80b5: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
 1ba80bd: c6 43 10 00                  	movb	$0x0, 0x10(%rbx)
 1ba80c1: 48 89 03                     	movq	%rax, (%rbx)
 1ba80c4: 48 89 ef                     	movq	%rbp, %rdi
 1ba80c7: e8 e4 2d 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba80cc: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
 1ba80d1: 64 48 33 34 25 28 00 00 00   	xorq	%fs:0x28, %rsi
 1ba80da: 48 89 d8                     	movq	%rbx, %rax
 1ba80dd: 0f 85 ac 00 00 00            	jne	0x1ba818f <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x17f>
 1ba80e3: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba80e7: 5b                           	popq	%rbx
 1ba80e8: 5d                           	popq	%rbp
 1ba80e9: 41 5c                        	popq	%r12
 1ba80eb: 41 5d                        	popq	%r13
 1ba80ed: 41 5e                        	popq	%r14
 1ba80ef: c3                           	retq
 1ba80f0: 48 89 ef                     	movq	%rbp, %rdi
 1ba80f3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba80f8: 4c 8b 77 08                  	movq	0x8(%rdi), %r14
 1ba80fc: 4c 8d 63 10                  	leaq	0x10(%rbx), %r12
 1ba8100: 4c 89 23                     	movq	%r12, (%rbx)
 1ba8103: 4d 85 f6                     	testq	%r14, %r14
 1ba8106: 74 68                        	je	0x1ba8170 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x160>
 1ba8108: 4c 89 f7                     	movq	%r14, %rdi
 1ba810b: e8 10 4f 8a ff               	callq	0x144d020 <strlen@plt>
 1ba8110: 48 83 f8 0f                  	cmpq	$0xf, %rax
 1ba8114: 49 89 c5                     	movq	%rax, %r13
 1ba8117: 48 89 04 24                  	movq	%rax, (%rsp)
 1ba811b: 77 33                        	ja	0x1ba8150 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x140>
 1ba811d: 48 83 f8 01                  	cmpq	$0x1, %rax
 1ba8121: 75 15                        	jne	0x1ba8138 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x128>
 1ba8123: 41 0f b6 16                  	movzbl	(%r14), %edx
 1ba8127: 88 53 10                     	movb	%dl, 0x10(%rbx)
 1ba812a: 48 89 43 08                  	movq	%rax, 0x8(%rbx)
 1ba812e: 41 c6 04 04 00               	movb	$0x0, (%r12,%rax)
 1ba8133: eb 8f                        	jmp	0x1ba80c4 <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0xb4>
 1ba8135: 0f 1f 00                     	nopl	(%rax)
 1ba8138: 4c 89 e7                     	movq	%r12, %rdi
 1ba813b: 4c 89 ea                     	movq	%r13, %rdx
 1ba813e: 4c 89 f6                     	movq	%r14, %rsi
 1ba8141: e8 4a 5b 8a ff               	callq	0x144dc90 <memcpy@plt>
 1ba8146: 48 8b 04 24                  	movq	(%rsp), %rax
 1ba814a: 4c 8b 23                     	movq	(%rbx), %r12
 1ba814d: eb db                        	jmp	0x1ba812a <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x11a>
 1ba814f: 90                           	nop
 1ba8150: 48 89 e6                     	movq	%rsp, %rsi
 1ba8153: 31 d2                        	xorl	%edx, %edx
 1ba8155: 48 89 df                     	movq	%rbx, %rdi
 1ba8158: e8 13 51 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba815d: 48 8b 14 24                  	movq	(%rsp), %rdx
 1ba8161: 48 89 03                     	movq	%rax, (%rbx)
 1ba8164: 48 89 c7                     	movq	%rax, %rdi
 1ba8167: 48 89 53 10                  	movq	%rdx, 0x10(%rbx)
 1ba816b: eb ce                        	jmp	0x1ba813b <convertCodetoISOName_NA[abi:cxx11](unsigned long)+0x12b>
 1ba816d: 0f 1f 00                     	nopl	(%rax)
 1ba8170: 48 8d 3d d1 c8 1b 04         	leaq	0x41bc8d1(%rip), %rdi   # 0x5d64a48 <_IO_stdin_used+0x8>
 1ba8177: e8 a4 5a 8a ff               	callq	0x144dc20 <_ZSt19__throw_logic_errorPKc@plt>
 1ba817c: 48 89 c3                     	movq	%rax, %rbx
 1ba817f: 48 89 ef                     	movq	%rbp, %rdi
 1ba8182: e8 29 2d 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba8187: 48 89 df                     	movq	%rbx, %rdi
 1ba818a: e8 d1 50 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba818f: e8 fc 29 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba8194: 66 90                        	nop
 1ba8196: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000001ba81a0 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)>:
 1ba81a0: 41 57                        	pushq	%r15
 1ba81a2: 41 56                        	pushq	%r14
 1ba81a4: 49 89 f7                     	movq	%rsi, %r15
 1ba81a7: 41 55                        	pushq	%r13
 1ba81a9: 41 54                        	pushq	%r12
 1ba81ab: 49 89 d6                     	movq	%rdx, %r14
 1ba81ae: 55                           	pushq	%rbp
 1ba81af: 53                           	pushq	%rbx
 1ba81b0: 4c 8d 05 f1 80 22 04         	leaq	0x42280f1(%rip), %r8    # 0x5dd02a8 <NimoExSLMainLinux(int, char**)::__func__+0x2a8>
 1ba81b7: 48 8d 35 1a 80 22 04         	leaq	0x422801a(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba81be: 49 89 fc                     	movq	%rdi, %r12
 1ba81c1: b9 d0 01 00 00               	movl	$0x1d0, %ecx            # imm = 0x1D0
 1ba81c6: 48 83 ec 78                  	subq	$0x78, %rsp
 1ba81ca: 4c 8b 0a                     	movq	(%rdx), %r9
 1ba81cd: 48 8d 15 cc 86 22 04         	leaq	0x42286cc(%rip), %rdx   # 0x5dd08a0 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba81d4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba81dd: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 1ba81e2: 31 c0                        	xorl	%eax, %eax
 1ba81e4: bf 02 00 00 00               	movl	$0x2, %edi
 1ba81e9: e8 42 7b c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba81ee: 49 8b 44 24 08               	movq	0x8(%r12), %rax
 1ba81f3: 66 0f ef c0                  	pxor	%xmm0, %xmm0
 1ba81f7: f2 0f 2a c0                  	cvtsi2sd	%eax, %xmm0
 1ba81fb: 89 44 24 08                  	movl	%eax, 0x8(%rsp)
 1ba81ff: f2 0f 59 05 39 2d 23 04      	mulsd	0x4232d39(%rip), %xmm0  # 0x5ddaf40 <exsl_ksc5601_2uni_page21+0x920>
 1ba8207: f2 0f 2c d8                  	cvttsd2si	%xmm0, %ebx
 1ba820b: 83 fb ff                     	cmpl	$-0x1, %ebx
 1ba820e: 0f 84 74 02 00 00            	je	0x1ba8488 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x2e8>
 1ba8214: 8d 43 01                     	leal	0x1(%rbx), %eax
 1ba8217: 48 8b 35 02 5a b0 05         	movq	0x5b05a02(%rip), %rsi   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 1ba821e: 4c 8d 6c 24 20               	leaq	0x20(%rsp), %r13
 1ba8223: 48 63 f8                     	movslq	%eax, %rdi
 1ba8226: 89 44 24 0c                  	movl	%eax, 0xc(%rsp)
 1ba822a: e8 11 69 8a ff               	callq	0x144eb40 <_ZnamRKSt9nothrow_t@plt>
 1ba822f: 48 8d 74 24 10               	leaq	0x10(%rsp), %rsi
 1ba8234: 48 89 c5                     	movq	%rax, %rbp
 1ba8237: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 1ba823b: 31 d2                        	xorl	%edx, %edx
 1ba823d: 4c 89 ef                     	movq	%r13, %rdi
 1ba8240: 48 c7 44 24 10 2f 00 00 00   	movq	$0x2f, 0x10(%rsp)
 1ba8249: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 1ba824e: e8 1d 50 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba8253: 48 8b 54 24 10               	movq	0x10(%rsp), %rdx
 1ba8258: 48 be 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rsi # imm = 0x2E2E2F2E2E2F2E2E
 1ba8262: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 1ba8267: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 1ba8271: c7 40 28 74 65 72 2e         	movl	$0x2e726574, 0x28(%rax) # imm = 0x2E726574
 1ba8278: c6 40 2e 70                  	movb	$0x70, 0x2e(%rax)
 1ba827c: 44 8b 44 24 0c               	movl	0xc(%rsp), %r8d
 1ba8281: 41 b9 01 00 00 00            	movl	$0x1, %r9d
 1ba8287: bf 00 30 00 00               	movl	$0x3000, %edi           # imm = 0x3000
 1ba828c: 48 89 54 24 30               	movq	%rdx, 0x30(%rsp)
 1ba8291: 48 89 30                     	movq	%rsi, (%rax)
 1ba8294: 48 be 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rsi # imm = 0x76614E2F6372732F
 1ba829e: 48 89 70 08                  	movq	%rsi, 0x8(%rax)
 1ba82a2: 48 be 2f 55 74 69 6c 2f 54 79	movabsq	$0x79542f6c6974552f, %rsi # imm = 0x79542F6C6974552F
 1ba82ac: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 1ba82b0: 48 89 70 18                  	movq	%rsi, 0x18(%rax)
 1ba82b4: 48 b9 70 65 43 6f 6e 76 65 72	movabsq	$0x7265766e6f436570, %rcx # imm = 0x7265766E6F436570
 1ba82be: be 63 70 00 00               	movl	$0x7063, %esi           # imm = 0x7063
 1ba82c3: 48 89 48 20                  	movq	%rcx, 0x20(%rax)
 1ba82c7: 66 89 70 2c                  	movw	%si, 0x2c(%rax)
 1ba82cb: 48 89 e9                     	movq	%rbp, %rcx
 1ba82ce: 48 8b 44 24 10               	movq	0x10(%rsp), %rax
 1ba82d3: 48 8b 54 24 20               	movq	0x20(%rsp), %rdx
 1ba82d8: 4c 89 ee                     	movq	%r13, %rsi
 1ba82db: 48 89 44 24 28               	movq	%rax, 0x28(%rsp)
 1ba82e0: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 1ba82e4: ba da 01 00 00               	movl	$0x1da, %edx            # imm = 0x1DA
 1ba82e9: e8 e2 0f 00 00               	callq	0x1ba92d0 <char* ExSLNewTemplate<char>(unsigned short, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, unsigned short, char*, unsigned int, bool)>
 1ba82ee: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
 1ba82f3: 49 83 c5 10                  	addq	$0x10, %r13
 1ba82f7: 48 89 c5                     	movq	%rax, %rbp
 1ba82fa: 4c 39 ef                     	cmpq	%r13, %rdi
 1ba82fd: 74 05                        	je	0x1ba8304 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x164>
 1ba82ff: e8 ac 2b 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba8304: 8b 4c 24 0c                  	movl	0xc(%rsp), %ecx
 1ba8308: 85 c9                        	testl	%ecx, %ecx
 1ba830a: 7e 10                        	jle	0x1ba831c <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x17c>
 1ba830c: 89 da                        	movl	%ebx, %edx
 1ba830e: 31 f6                        	xorl	%esi, %esi
 1ba8310: 48 89 ef                     	movq	%rbp, %rdi
 1ba8313: 48 83 c2 01                  	addq	$0x1, %rdx
 1ba8317: e8 e4 28 8a ff               	callq	0x144ac00 <memset@plt>
 1ba831c: 49 8b 44 24 08               	movq	0x8(%r12), %rax
 1ba8321: 48 85 c0                     	testq	%rax, %rax
 1ba8324: 0f 84 ed 01 00 00            	je	0x1ba8517 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x377>
 1ba832a: 8b 54 24 08                  	movl	0x8(%rsp), %edx
 1ba832e: 49 8b 3c 24                  	movq	(%r12), %rdi
 1ba8332: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 1ba8338: 89 d9                        	movl	%ebx, %ecx
 1ba833a: 48 89 ee                     	movq	%rbp, %rsi
 1ba833d: e8 7e f5 ff ff               	callq	0x1ba78c0 <base64Encode(char const*, char*, int, int, bool)>
 1ba8342: 48 89 ef                     	movq	%rbp, %rdi
 1ba8345: e8 d6 4c 8a ff               	callq	0x144d020 <strlen@plt>
 1ba834a: 49 8b 57 08                  	movq	0x8(%r15), %rdx
 1ba834e: 49 89 c0                     	movq	%rax, %r8
 1ba8351: 48 89 e9                     	movq	%rbp, %rcx
 1ba8354: 31 f6                        	xorl	%esi, %esi
 1ba8356: 4c 89 ff                     	movq	%r15, %rdi
 1ba8359: e8 b2 3a 8a ff               	callq	0x144be10 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_replaceEmmPKcm@plt>
 1ba835e: 48 8d 5c 24 40               	leaq	0x40(%rsp), %rbx
 1ba8363: 48 8d 74 24 18               	leaq	0x18(%rsp), %rsi
 1ba8368: 31 d2                        	xorl	%edx, %edx
 1ba836a: 48 c7 44 24 18 2f 00 00 00   	movq	$0x2f, 0x18(%rsp)
 1ba8373: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba8377: 48 89 df                     	movq	%rbx, %rdi
 1ba837a: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 1ba837f: e8 ec 4e 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba8384: 48 8b 54 24 18               	movq	0x18(%rsp), %rdx
 1ba8389: 48 b9 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rcx # imm = 0x2E2E2F2E2E2F2E2E
 1ba8393: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 1ba8398: c7 40 28 74 65 72 2e         	movl	$0x2e726574, 0x28(%rax) # imm = 0x2E726574
 1ba839f: c6 40 2e 70                  	movb	$0x70, 0x2e(%rax)
 1ba83a3: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 1ba83a9: 48 89 de                     	movq	%rbx, %rsi
 1ba83ac: bf 00 30 00 00               	movl	$0x3000, %edi           # imm = 0x3000
 1ba83b1: 48 89 54 24 50               	movq	%rdx, 0x50(%rsp)
 1ba83b6: 48 89 08                     	movq	%rcx, (%rax)
 1ba83b9: 48 b9 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rcx # imm = 0x76614E2F6372732F
 1ba83c3: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 1ba83c7: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 1ba83d1: ba 63 70 00 00               	movl	$0x7063, %edx           # imm = 0x7063
 1ba83d6: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 1ba83da: 48 b9 2f 55 74 69 6c 2f 54 79	movabsq	$0x79542f6c6974552f, %rcx # imm = 0x79542F6C6974552F
 1ba83e4: 66 89 50 2c                  	movw	%dx, 0x2c(%rax)
 1ba83e8: 48 89 48 18                  	movq	%rcx, 0x18(%rax)
 1ba83ec: 48 b9 70 65 43 6f 6e 76 65 72	movabsq	$0x7265766e6f436570, %rcx # imm = 0x7265766E6F436570
 1ba83f6: 48 8b 54 24 40               	movq	0x40(%rsp), %rdx
 1ba83fb: 48 89 48 20                  	movq	%rcx, 0x20(%rax)
 1ba83ff: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
 1ba8404: 48 89 e9                     	movq	%rbp, %rcx
 1ba8407: 48 89 44 24 48               	movq	%rax, 0x48(%rsp)
 1ba840c: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 1ba8410: ba e1 01 00 00               	movl	$0x1e1, %edx            # imm = 0x1E1
 1ba8415: e8 f6 19 c6 00               	callq	0x2809e10 <ExSLMemoryDel>
 1ba841a: 48 89 ef                     	movq	%rbp, %rdi
 1ba841d: 48 83 c3 10                  	addq	$0x10, %rbx
 1ba8421: e8 7a 4b 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba8426: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 1ba842b: 48 39 df                     	cmpq	%rbx, %rdi
 1ba842e: 74 05                        	je	0x1ba8435 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x295>
 1ba8430: e8 7b 2a 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba8435: bb 01 00 00 00               	movl	$0x1, %ebx
 1ba843a: 4d 8b 0e                     	movq	(%r14), %r9
 1ba843d: 4c 8d 05 dc 7e 22 04         	leaq	0x4227edc(%rip), %r8    # 0x5dd0320 <NimoExSLMainLinux(int, char**)::__func__+0x320>
 1ba8444: 48 8d 15 55 84 22 04         	leaq	0x4228455(%rip), %rdx   # 0x5dd08a0 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba844b: 48 8d 35 86 7d 22 04         	leaq	0x4227d86(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba8452: 31 c0                        	xorl	%eax, %eax
 1ba8454: b9 e6 01 00 00               	movl	$0x1e6, %ecx            # imm = 0x1E6
 1ba8459: bf 02 00 00 00               	movl	$0x2, %edi
 1ba845e: e8 cd 78 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba8463: 89 d8                        	movl	%ebx, %eax
 1ba8465: 48 8b 5c 24 68               	movq	0x68(%rsp), %rbx
 1ba846a: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
 1ba8473: 75 1a                        	jne	0x1ba848f <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x2ef>
 1ba8475: 48 83 c4 78                  	addq	$0x78, %rsp
 1ba8479: 5b                           	popq	%rbx
 1ba847a: 5d                           	popq	%rbp
 1ba847b: 41 5c                        	popq	%r12
 1ba847d: 41 5d                        	popq	%r13
 1ba847f: 41 5e                        	popq	%r14
 1ba8481: 41 5f                        	popq	%r15
 1ba8483: c3                           	retq
 1ba8484: 0f 1f 40 00                  	nopl	(%rax)
 1ba8488: 31 ed                        	xorl	%ebp, %ebp
 1ba848a: e9 92 fe ff ff               	jmp	0x1ba8321 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x181>
 1ba848f: e8 fc 26 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba8494: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
 1ba8499: 49 83 c5 10                  	addq	$0x10, %r13
 1ba849d: 48 89 c3                     	movq	%rax, %rbx
 1ba84a0: 4c 39 ef                     	cmpq	%r13, %rdi
 1ba84a3: 74 05                        	je	0x1ba84aa <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x30a>
 1ba84a5: e8 06 2a 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba84aa: 48 89 d8                     	movq	%rbx, %rax
 1ba84ad: 48 89 c7                     	movq	%rax, %rdi
 1ba84b0: e8 0b 46 8a ff               	callq	0x144cac0 <__cxa_begin_catch@plt>
 1ba84b5: 4d 8b 0e                     	movq	(%r14), %r9
 1ba84b8: 4c 8d 05 91 7e 22 04         	leaq	0x4227e91(%rip), %r8    # 0x5dd0350 <NimoExSLMainLinux(int, char**)::__func__+0x350>
 1ba84bf: 48 8d 15 da 83 22 04         	leaq	0x42283da(%rip), %rdx   # 0x5dd08a0 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba84c6: 48 8d 35 0b 7d 22 04         	leaq	0x4227d0b(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba84cd: b9 e4 01 00 00               	movl	$0x1e4, %ecx            # imm = 0x1E4
 1ba84d2: bf 02 00 00 00               	movl	$0x2, %edi
 1ba84d7: 31 c0                        	xorl	%eax, %eax
 1ba84d9: e8 52 78 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba84de: e8 0d 62 8a ff               	callq	0x144e6f0 <__cxa_end_catch@plt>
 1ba84e3: 31 db                        	xorl	%ebx, %ebx
 1ba84e5: e9 50 ff ff ff               	jmp	0x1ba843a <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x29a>
 1ba84ea: eb c1                        	jmp	0x1ba84ad <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x30d>
 1ba84ec: 48 89 c3                     	movq	%rax, %rbx
 1ba84ef: e8 fc 61 8a ff               	callq	0x144e6f0 <__cxa_end_catch@plt>
 1ba84f4: 48 89 df                     	movq	%rbx, %rdi
 1ba84f7: e8 64 4d 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba84fc: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 1ba8501: 48 83 c3 10                  	addq	$0x10, %rbx
 1ba8505: 48 89 c5                     	movq	%rax, %rbp
 1ba8508: 48 39 df                     	cmpq	%rbx, %rdi
 1ba850b: 74 05                        	je	0x1ba8512 <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x372>
 1ba850d: e8 9e 29 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba8512: 48 89 e8                     	movq	%rbp, %rax
 1ba8515: eb 96                        	jmp	0x1ba84ad <stdStrToBase64Str(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x30d>
 1ba8517: 48 8d 3d ba 7d 22 04         	leaq	0x4227dba(%rip), %rdi   # 0x5dd02d8 <NimoExSLMainLinux(int, char**)::__func__+0x2d8>
 1ba851e: 31 d2                        	xorl	%edx, %edx
 1ba8520: 31 f6                        	xorl	%esi, %esi
 1ba8522: e8 89 69 8a ff               	callq	0x144eeb0 <_ZSt24__throw_out_of_range_fmtPKcz@plt>
 1ba8527: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000001ba8530 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)>:
 1ba8530: 41 57                        	pushq	%r15
 1ba8532: 41 56                        	pushq	%r14
 1ba8534: 4c 8d 05 4d 7e 22 04         	leaq	0x4227e4d(%rip), %r8    # 0x5dd0388 <NimoExSLMainLinux(int, char**)::__func__+0x388>
 1ba853b: 41 55                        	pushq	%r13
 1ba853d: 41 54                        	pushq	%r12
 1ba853f: 49 89 f7                     	movq	%rsi, %r15
 1ba8542: 55                           	pushq	%rbp
 1ba8543: 53                           	pushq	%rbx
 1ba8544: 49 89 d6                     	movq	%rdx, %r14
 1ba8547: 48 8d 35 8a 7c 22 04         	leaq	0x4227c8a(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba854e: 48 89 fd                     	movq	%rdi, %rbp
 1ba8551: b9 ed 01 00 00               	movl	$0x1ed, %ecx            # imm = 0x1ED
 1ba8556: 48 81 ec 98 00 00 00         	subq	$0x98, %rsp
 1ba855d: 4c 8b 0a                     	movq	(%rdx), %r9
 1ba8560: 48 8d 15 19 83 22 04         	leaq	0x4228319(%rip), %rdx   # 0x5dd0880 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba8567: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba8570: 48 89 84 24 88 00 00 00      	movq	%rax, 0x88(%rsp)
 1ba8578: 31 c0                        	xorl	%eax, %eax
 1ba857a: bf 02 00 00 00               	movl	$0x2, %edi
 1ba857f: e8 ac 77 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba8584: 4c 8b 45 08                  	movq	0x8(%rbp), %r8
 1ba8588: c7 44 24 2c 00 00 00 00      	movl	$0x0, 0x2c(%rsp)
 1ba8590: 41 83 f8 ff                  	cmpl	$-0x1, %r8d
 1ba8594: 0f 84 d6 04 00 00            	je	0x1ba8a70 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x540>
 1ba859a: 48 8b 35 7f 56 b0 05         	movq	0x5b0567f(%rip), %rsi   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 1ba85a1: 41 8d 78 01                  	leal	0x1(%r8), %edi
 1ba85a5: 48 8d 5c 24 60               	leaq	0x60(%rsp), %rbx
 1ba85aa: 49 89 fd                     	movq	%rdi, %r13
 1ba85ad: e8 8e 65 8a ff               	callq	0x144eb40 <_ZnamRKSt9nothrow_t@plt>
 1ba85b2: 49 89 c4                     	movq	%rax, %r12
 1ba85b5: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba85b9: 31 d2                        	xorl	%edx, %edx
 1ba85bb: 48 89 df                     	movq	%rbx, %rdi
 1ba85be: 48 c7 44 24 38 2f 00 00 00   	movq	$0x2f, 0x38(%rsp)
 1ba85c7: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 1ba85cc: 48 8d 44 24 38               	leaq	0x38(%rsp), %rax
 1ba85d1: 48 89 c6                     	movq	%rax, %rsi
 1ba85d4: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba85d9: e8 92 4c 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba85de: 48 8b 54 24 38               	movq	0x38(%rsp), %rdx
 1ba85e3: 48 be 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rsi # imm = 0x2E2E2F2E2E2F2E2E
 1ba85ed: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 1ba85f2: 48 b9 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rcx # imm = 0x76614E2F6372732F
 1ba85fc: bf 63 70 00 00               	movl	$0x7063, %edi           # imm = 0x7063
 1ba8601: 41 b9 01 00 00 00            	movl	$0x1, %r9d
 1ba8607: 45 89 e8                     	movl	%r13d, %r8d
 1ba860a: 48 89 54 24 70               	movq	%rdx, 0x70(%rsp)
 1ba860f: 48 89 30                     	movq	%rsi, (%rax)
 1ba8612: 48 be 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rsi # imm = 0x6C6F72746E6F4369
 1ba861c: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 1ba8620: 48 89 70 10                  	movq	%rsi, 0x10(%rax)
 1ba8624: 48 b9 2f 55 74 69 6c 2f 54 79	movabsq	$0x79542f6c6974552f, %rcx # imm = 0x79542F6C6974552F
 1ba862e: 48 be 70 65 43 6f 6e 76 65 72	movabsq	$0x7265766e6f436570, %rsi # imm = 0x7265766E6F436570
 1ba8638: 48 89 48 18                  	movq	%rcx, 0x18(%rax)
 1ba863c: 66 89 78 2c                  	movw	%di, 0x2c(%rax)
 1ba8640: 48 89 70 20                  	movq	%rsi, 0x20(%rax)
 1ba8644: c7 40 28 74 65 72 2e         	movl	$0x2e726574, 0x28(%rax) # imm = 0x2E726574
 1ba864b: 4c 89 e1                     	movq	%r12, %rcx
 1ba864e: c6 40 2e 70                  	movb	$0x70, 0x2e(%rax)
 1ba8652: 48 8b 44 24 38               	movq	0x38(%rsp), %rax
 1ba8657: 48 89 de                     	movq	%rbx, %rsi
 1ba865a: 48 8b 54 24 60               	movq	0x60(%rsp), %rdx
 1ba865f: bf 00 30 00 00               	movl	$0x3000, %edi           # imm = 0x3000
 1ba8664: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 1ba8669: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 1ba866d: ba f4 01 00 00               	movl	$0x1f4, %edx            # imm = 0x1F4
 1ba8672: e8 59 0c 00 00               	callq	0x1ba92d0 <char* ExSLNewTemplate<char>(unsigned short, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, unsigned short, char*, unsigned int, bool)>
 1ba8677: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 1ba867c: 49 89 c4                     	movq	%rax, %r12
 1ba867f: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba8683: 48 39 c7                     	cmpq	%rax, %rdi
 1ba8686: 74 05                        	je	0x1ba868d <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x15d>
 1ba8688: e8 23 28 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba868d: 4d 85 e4                     	testq	%r12, %r12
 1ba8690: 0f 84 da 03 00 00            	je	0x1ba8a70 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x540>
 1ba8696: 48 8b 55 08                  	movq	0x8(%rbp), %rdx
 1ba869a: 48 85 d2                     	testq	%rdx, %rdx
 1ba869d: 0f 85 fd 03 00 00            	jne	0x1ba8aa0 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x570>
 1ba86a3: 41 c6 04 14 00               	movb	$0x0, (%r12,%rdx)
 1ba86a8: 48 8b 45 08                  	movq	0x8(%rbp), %rax
 1ba86ac: 66 0f ef c0                  	pxor	%xmm0, %xmm0
 1ba86b0: 83 c0 01                     	addl	$0x1, %eax
 1ba86b3: f2 0f 2a c0                  	cvtsi2sd	%eax, %xmm0
 1ba86b7: 89 44 24 2c                  	movl	%eax, 0x2c(%rsp)
 1ba86bb: f2 0f 59 05 7d 28 23 04      	mulsd	0x423287d(%rip), %xmm0  # 0x5ddaf40 <exsl_ksc5601_2uni_page21+0x920>
 1ba86c3: f2 0f 2c e8                  	cvttsd2si	%xmm0, %ebp
 1ba86c7: 83 fd ff                     	cmpl	$-0x1, %ebp
 1ba86ca: 0f 84 50 03 00 00            	je	0x1ba8a20 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x4f0>
 1ba86d0: 48 8b 35 49 55 b0 05         	movq	0x5b05549(%rip), %rsi   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 1ba86d7: 83 c5 01                     	addl	$0x1, %ebp
 1ba86da: 4c 8d 6c 24 40               	leaq	0x40(%rsp), %r13
 1ba86df: 48 63 c5                     	movslq	%ebp, %rax
 1ba86e2: 48 89 c7                     	movq	%rax, %rdi
 1ba86e5: 48 89 44 24 10               	movq	%rax, 0x10(%rsp)
 1ba86ea: e8 51 64 8a ff               	callq	0x144eb40 <_ZnamRKSt9nothrow_t@plt>
 1ba86ef: 48 8d 74 24 30               	leaq	0x30(%rsp), %rsi
 1ba86f4: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
 1ba86f9: 49 8d 45 10                  	leaq	0x10(%r13), %rax
 1ba86fd: 31 d2                        	xorl	%edx, %edx
 1ba86ff: 4c 89 ef                     	movq	%r13, %rdi
 1ba8702: 48 c7 44 24 30 2f 00 00 00   	movq	$0x2f, 0x30(%rsp)
 1ba870b: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 1ba8710: e8 5b 4b 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba8715: 48 8b 54 24 30               	movq	0x30(%rsp), %rdx
 1ba871a: 48 be 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rsi # imm = 0x2E2E2F2E2E2F2E2E
 1ba8724: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
 1ba8729: 48 bf 2f 55 74 69 6c 2f 54 79	movabsq	$0x79542f6c6974552f, %rdi # imm = 0x79542F6C6974552F
 1ba8733: c7 40 28 74 65 72 2e         	movl	$0x2e726574, 0x28(%rax) # imm = 0x2E726574
 1ba873a: c6 40 2e 70                  	movb	$0x70, 0x2e(%rax)
 1ba873e: 48 89 78 18                  	movq	%rdi, 0x18(%rax)
 1ba8742: 48 8b 4c 24 18               	movq	0x18(%rsp), %rcx
 1ba8747: 41 b9 01 00 00 00            	movl	$0x1, %r9d
 1ba874d: 48 89 54 24 50               	movq	%rdx, 0x50(%rsp)
 1ba8752: 48 89 30                     	movq	%rsi, (%rax)
 1ba8755: 48 be 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rsi # imm = 0x76614E2F6372732F
 1ba875f: 48 89 70 08                  	movq	%rsi, 0x8(%rax)
 1ba8763: 48 be 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rsi # imm = 0x6C6F72746E6F4369
 1ba876d: 48 8b 54 24 40               	movq	0x40(%rsp), %rdx
 1ba8772: 48 89 70 10                  	movq	%rsi, 0x10(%rax)
 1ba8776: 48 be 70 65 43 6f 6e 76 65 72	movabsq	$0x7265766e6f436570, %rsi # imm = 0x7265766E6F436570
 1ba8780: 41 89 e8                     	movl	%ebp, %r8d
 1ba8783: 48 89 70 20                  	movq	%rsi, 0x20(%rax)
 1ba8787: be 63 70 00 00               	movl	$0x7063, %esi           # imm = 0x7063
 1ba878c: bf 00 30 00 00               	movl	$0x3000, %edi           # imm = 0x3000
 1ba8791: 66 89 70 2c                  	movw	%si, 0x2c(%rax)
 1ba8795: 48 8b 44 24 30               	movq	0x30(%rsp), %rax
 1ba879a: 4c 89 ee                     	movq	%r13, %rsi
 1ba879d: 48 89 44 24 48               	movq	%rax, 0x48(%rsp)
 1ba87a2: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 1ba87a6: ba 02 02 00 00               	movl	$0x202, %edx            # imm = 0x202
 1ba87ab: e8 20 0b 00 00               	callq	0x1ba92d0 <char* ExSLNewTemplate<char>(unsigned short, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, unsigned short, char*, unsigned int, bool)>
 1ba87b0: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 1ba87b5: 49 83 c5 10                  	addq	$0x10, %r13
 1ba87b9: 48 89 c5                     	movq	%rax, %rbp
 1ba87bc: 4c 39 ef                     	cmpq	%r13, %rdi
 1ba87bf: 74 05                        	je	0x1ba87c6 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x296>
 1ba87c1: e8 ea 26 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba87c6: 48 85 ed                     	testq	%rbp, %rbp
 1ba87c9: 0f 84 51 02 00 00            	je	0x1ba8a20 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x4f0>
 1ba87cf: 48 8b 54 24 10               	movq	0x10(%rsp), %rdx
 1ba87d4: 31 f6                        	xorl	%esi, %esi
 1ba87d6: 48 89 ef                     	movq	%rbp, %rdi
 1ba87d9: e8 22 24 8a ff               	callq	0x144ac00 <memset@plt>
 1ba87de: 48 8d 54 24 2c               	leaq	0x2c(%rsp), %rdx
 1ba87e3: b9 01 00 00 00               	movl	$0x1, %ecx
 1ba87e8: 48 89 ee                     	movq	%rbp, %rsi
 1ba87eb: 4c 89 e7                     	movq	%r12, %rdi
 1ba87ee: e8 5d f3 ff ff               	callq	0x1ba7b50 <base64Decode(char const*, char*, int*, bool)>
 1ba87f3: 48 89 ef                     	movq	%rbp, %rdi
 1ba87f6: e8 25 48 8a ff               	callq	0x144d020 <strlen@plt>
 1ba87fb: 49 8b 57 08                  	movq	0x8(%r15), %rdx
 1ba87ff: 49 89 c0                     	movq	%rax, %r8
 1ba8802: 48 89 e9                     	movq	%rbp, %rcx
 1ba8805: 31 f6                        	xorl	%esi, %esi
 1ba8807: 4c 89 ff                     	movq	%r15, %rdi
 1ba880a: e8 01 36 8a ff               	callq	0x144be10 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_replaceEmmPKcm@plt>
 1ba880f: 41 bd 01 00 00 00            	movl	$0x1, %r13d
 1ba8815: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
 1ba881a: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba881e: 31 d2                        	xorl	%edx, %edx
 1ba8820: 48 89 df                     	movq	%rbx, %rdi
 1ba8823: 48 c7 44 24 38 2f 00 00 00   	movq	$0x2f, 0x38(%rsp)
 1ba882c: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 1ba8831: e8 3a 4a 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba8836: 48 8b 54 24 38               	movq	0x38(%rsp), %rdx
 1ba883b: 48 b9 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rcx # imm = 0x2E2E2F2E2E2F2E2E
 1ba8845: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 1ba884a: 48 be 70 65 43 6f 6e 76 65 72	movabsq	$0x7265766e6f436570, %rsi # imm = 0x7265766E6F436570
 1ba8854: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 1ba885a: bf 00 30 00 00               	movl	$0x3000, %edi           # imm = 0x3000
 1ba885f: 48 89 54 24 70               	movq	%rdx, 0x70(%rsp)
 1ba8864: 48 89 08                     	movq	%rcx, (%rax)
 1ba8867: 48 b9 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rcx # imm = 0x76614E2F6372732F
 1ba8871: 48 89 48 08                  	movq	%rcx, 0x8(%rax)
 1ba8875: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 1ba887f: 48 89 70 20                  	movq	%rsi, 0x20(%rax)
 1ba8883: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 1ba8887: 48 b9 2f 55 74 69 6c 2f 54 79	movabsq	$0x79542f6c6974552f, %rcx # imm = 0x79542F6C6974552F
 1ba8891: c7 40 28 74 65 72 2e         	movl	$0x2e726574, 0x28(%rax) # imm = 0x2E726574
 1ba8898: 48 89 48 18                  	movq	%rcx, 0x18(%rax)
 1ba889c: b9 63 70 00 00               	movl	$0x7063, %ecx           # imm = 0x7063
 1ba88a1: c6 40 2e 70                  	movb	$0x70, 0x2e(%rax)
 1ba88a5: 66 89 48 2c                  	movw	%cx, 0x2c(%rax)
 1ba88a9: 48 8b 44 24 38               	movq	0x38(%rsp), %rax
 1ba88ae: 4c 89 e1                     	movq	%r12, %rcx
 1ba88b1: 48 8b 54 24 60               	movq	0x60(%rsp), %rdx
 1ba88b6: 48 89 de                     	movq	%rbx, %rsi
 1ba88b9: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 1ba88be: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 1ba88c2: ba 13 02 00 00               	movl	$0x213, %edx            # imm = 0x213
 1ba88c7: e8 44 15 c6 00               	callq	0x2809e10 <ExSLMemoryDel>
 1ba88cc: 4c 89 e7                     	movq	%r12, %rdi
 1ba88cf: e8 cc 46 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba88d4: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 1ba88d9: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba88dd: 48 39 c7                     	cmpq	%rax, %rdi
 1ba88e0: 74 05                        	je	0x1ba88e7 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x3b7>
 1ba88e2: e8 c9 25 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba88e7: 48 85 ed                     	testq	%rbp, %rbp
 1ba88ea: 0f 84 d2 00 00 00            	je	0x1ba89c2 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x492>
 1ba88f0: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
 1ba88f5: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
 1ba88f9: 31 d2                        	xorl	%edx, %edx
 1ba88fb: 48 89 df                     	movq	%rbx, %rdi
 1ba88fe: 48 c7 44 24 38 2f 00 00 00   	movq	$0x2f, 0x38(%rsp)
 1ba8907: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 1ba890c: e8 5f 49 8a ff               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 1ba8911: 48 8b 54 24 38               	movq	0x38(%rsp), %rdx
 1ba8916: 48 b9 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rcx # imm = 0x2E2E2F2E2E2F2E2E
 1ba8920: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
 1ba8925: 48 be 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rsi # imm = 0x76614E2F6372732F
 1ba892f: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 1ba8935: bf 00 30 00 00               	movl	$0x3000, %edi           # imm = 0x3000
 1ba893a: 48 89 54 24 70               	movq	%rdx, 0x70(%rsp)
 1ba893f: 48 89 08                     	movq	%rcx, (%rax)
 1ba8942: 48 b9 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rcx # imm = 0x6C6F72746E6F4369
 1ba894c: 48 89 70 08                  	movq	%rsi, 0x8(%rax)
 1ba8950: 48 89 48 10                  	movq	%rcx, 0x10(%rax)
 1ba8954: 48 be 2f 55 74 69 6c 2f 54 79	movabsq	$0x79542f6c6974552f, %rsi # imm = 0x79542F6C6974552F
 1ba895e: 48 b9 70 65 43 6f 6e 76 65 72	movabsq	$0x7265766e6f436570, %rcx # imm = 0x7265766E6F436570
 1ba8968: ba 63 70 00 00               	movl	$0x7063, %edx           # imm = 0x7063
 1ba896d: 48 89 70 18                  	movq	%rsi, 0x18(%rax)
 1ba8971: 48 89 48 20                  	movq	%rcx, 0x20(%rax)
 1ba8975: c7 40 28 74 65 72 2e         	movl	$0x2e726574, 0x28(%rax) # imm = 0x2E726574
 1ba897c: 48 89 e9                     	movq	%rbp, %rcx
 1ba897f: 66 89 50 2c                  	movw	%dx, 0x2c(%rax)
 1ba8983: c6 40 2e 70                  	movb	$0x70, 0x2e(%rax)
 1ba8987: 48 89 de                     	movq	%rbx, %rsi
 1ba898a: 48 8b 44 24 38               	movq	0x38(%rsp), %rax
 1ba898f: 48 8b 54 24 60               	movq	0x60(%rsp), %rdx
 1ba8994: 48 89 44 24 68               	movq	%rax, 0x68(%rsp)
 1ba8999: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 1ba899d: ba 16 02 00 00               	movl	$0x216, %edx            # imm = 0x216
 1ba89a2: e8 69 14 c6 00               	callq	0x2809e10 <ExSLMemoryDel>
 1ba89a7: 48 89 ef                     	movq	%rbp, %rdi
 1ba89aa: 48 83 c3 10                  	addq	$0x10, %rbx
 1ba89ae: e8 ed 45 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba89b3: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 1ba89b8: 48 39 df                     	cmpq	%rbx, %rdi
 1ba89bb: 74 05                        	je	0x1ba89c2 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x492>
 1ba89bd: e8 ee 24 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba89c2: 4d 8b 0e                     	movq	(%r14), %r9
 1ba89c5: 4c 8d 05 44 7a 22 04         	leaq	0x4227a44(%rip), %r8    # 0x5dd0410 <NimoExSLMainLinux(int, char**)::__func__+0x410>
 1ba89cc: 48 8d 15 ad 7e 22 04         	leaq	0x4227ead(%rip), %rdx   # 0x5dd0880 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba89d3: 48 8d 35 fe 77 22 04         	leaq	0x42277fe(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba89da: 31 c0                        	xorl	%eax, %eax
 1ba89dc: b9 18 02 00 00               	movl	$0x218, %ecx            # imm = 0x218
 1ba89e1: bf 02 00 00 00               	movl	$0x2, %edi
 1ba89e6: e8 45 73 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba89eb: 44 89 e8                     	movl	%r13d, %eax
 1ba89ee: 48 8b 9c 24 88 00 00 00      	movq	0x88(%rsp), %rbx
 1ba89f6: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
 1ba89ff: 0f 85 f0 00 00 00            	jne	0x1ba8af5 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x5c5>
 1ba8a05: 48 81 c4 98 00 00 00         	addq	$0x98, %rsp
 1ba8a0c: 5b                           	popq	%rbx
 1ba8a0d: 5d                           	popq	%rbp
 1ba8a0e: 41 5c                        	popq	%r12
 1ba8a10: 41 5d                        	popq	%r13
 1ba8a12: 41 5e                        	popq	%r14
 1ba8a14: 41 5f                        	popq	%r15
 1ba8a16: c3                           	retq
 1ba8a17: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 1ba8a20: 4c 8d 05 b9 79 22 04         	leaq	0x42279b9(%rip), %r8    # 0x5dd03e0 <NimoExSLMainLinux(int, char**)::__func__+0x3e0>
 1ba8a27: 48 8d 15 52 7e 22 04         	leaq	0x4227e52(%rip), %rdx   # 0x5dd0880 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba8a2e: 48 8d 35 a3 77 22 04         	leaq	0x42277a3(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba8a35: b9 05 02 00 00               	movl	$0x205, %ecx            # imm = 0x205
 1ba8a3a: bf 02 00 00 00               	movl	$0x2, %edi
 1ba8a3f: 31 c0                        	xorl	%eax, %eax
 1ba8a41: e8 ea 72 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba8a46: bf 04 00 00 00               	movl	$0x4, %edi
 1ba8a4b: e8 c0 32 8a ff               	callq	0x144bd10 <__cxa_allocate_exception@plt>
 1ba8a50: 48 8b 35 d9 31 b0 05         	movq	0x5b031d9(%rip), %rsi   # 0x76abc30 <_GLOBAL_OFFSET_TABLE_+0x29c8>
 1ba8a57: c7 00 00 00 00 00            	movl	$0x0, (%rax)
 1ba8a5d: 31 d2                        	xorl	%edx, %edx
 1ba8a5f: 48 89 c7                     	movq	%rax, %rdi
 1ba8a62: e8 d9 47 8a ff               	callq	0x144d240 <__cxa_throw@plt>
 1ba8a67: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 1ba8a70: 4c 8d 05 41 79 22 04         	leaq	0x4227941(%rip), %r8    # 0x5dd03b8 <NimoExSLMainLinux(int, char**)::__func__+0x3b8>
 1ba8a77: 48 8d 15 02 7e 22 04         	leaq	0x4227e02(%rip), %rdx   # 0x5dd0880 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba8a7e: 48 8d 35 53 77 22 04         	leaq	0x4227753(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba8a85: 31 c0                        	xorl	%eax, %eax
 1ba8a87: b9 f7 01 00 00               	movl	$0x1f7, %ecx            # imm = 0x1F7
 1ba8a8c: bf 02 00 00 00               	movl	$0x2, %edi
 1ba8a91: e8 9a 72 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba8a96: 31 c0                        	xorl	%eax, %eax
 1ba8a98: e9 51 ff ff ff               	jmp	0x1ba89ee <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x4be>
 1ba8a9d: 0f 1f 00                     	nopl	(%rax)
 1ba8aa0: 48 8b 75 00                  	movq	(%rbp), %rsi
 1ba8aa4: 4c 89 e7                     	movq	%r12, %rdi
 1ba8aa7: e8 b4 41 8a ff               	callq	0x144cc60 <memmove@plt>
 1ba8aac: 48 8b 55 08                  	movq	0x8(%rbp), %rdx
 1ba8ab0: e9 ee fb ff ff               	jmp	0x1ba86a3 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x173>
 1ba8ab5: 31 ed                        	xorl	%ebp, %ebp
 1ba8ab7: 48 89 c7                     	movq	%rax, %rdi
 1ba8aba: e8 01 40 8a ff               	callq	0x144cac0 <__cxa_begin_catch@plt>
 1ba8abf: 4d 8b 0e                     	movq	(%r14), %r9
 1ba8ac2: 4c 8d 05 77 79 22 04         	leaq	0x4227977(%rip), %r8    # 0x5dd0440 <NimoExSLMainLinux(int, char**)::__func__+0x440>
 1ba8ac9: 48 8d 15 b0 7d 22 04         	leaq	0x4227db0(%rip), %rdx   # 0x5dd0880 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)::__func__>
 1ba8ad0: 48 8d 35 01 77 22 04         	leaq	0x4227701(%rip), %rsi   # 0x5dd01d8 <NimoExSLMainLinux(int, char**)::__func__+0x1d8>
 1ba8ad7: b9 0f 02 00 00               	movl	$0x20f, %ecx            # imm = 0x20F
 1ba8adc: bf 02 00 00 00               	movl	$0x2, %edi
 1ba8ae1: 31 c0                        	xorl	%eax, %eax
 1ba8ae3: e8 48 72 c6 00               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 1ba8ae8: e8 03 5c 8a ff               	callq	0x144e6f0 <__cxa_end_catch@plt>
 1ba8aed: 45 31 ed                     	xorl	%r13d, %r13d
 1ba8af0: e9 20 fd ff ff               	jmp	0x1ba8815 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x2e5>
 1ba8af5: e8 96 20 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba8afa: 48 8b 7c 24 60               	movq	0x60(%rsp), %rdi
 1ba8aff: 48 83 c3 10                  	addq	$0x10, %rbx
 1ba8b03: 48 89 c5                     	movq	%rax, %rbp
 1ba8b06: 48 39 df                     	cmpq	%rbx, %rdi
 1ba8b09: 74 05                        	je	0x1ba8b10 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x5e0>
 1ba8b0b: e8 a0 23 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba8b10: 48 89 ef                     	movq	%rbp, %rdi
 1ba8b13: e8 48 47 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba8b18: eb 9b                        	jmp	0x1ba8ab5 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x585>
 1ba8b1a: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
 1ba8b1f: 49 83 c5 10                  	addq	$0x10, %r13
 1ba8b23: 48 89 c5                     	movq	%rax, %rbp
 1ba8b26: 4c 39 ef                     	cmpq	%r13, %rdi
 1ba8b29: 74 05                        	je	0x1ba8b30 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x600>
 1ba8b2b: e8 80 23 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba8b30: 48 89 e8                     	movq	%rbp, %rax
 1ba8b33: eb 80                        	jmp	0x1ba8ab5 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x585>
 1ba8b35: eb 80                        	jmp	0x1ba8ab7 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x587>
 1ba8b37: eb c1                        	jmp	0x1ba8afa <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x5ca>
 1ba8b39: eb bf                        	jmp	0x1ba8afa <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x5ca>
 1ba8b3b: e9 75 ff ff ff               	jmp	0x1ba8ab5 <base64StrTostdStr(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x585>
 1ba8b40: 48 89 c3                     	movq	%rax, %rbx
 1ba8b43: e8 a8 5b 8a ff               	callq	0x144e6f0 <__cxa_end_catch@plt>
 1ba8b48: 48 89 df                     	movq	%rbx, %rdi
 1ba8b4b: e8 10 47 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>

0000000001ba8b50 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)>:
 1ba8b50: 41 55                        	pushq	%r13
 1ba8b52: 41 54                        	pushq	%r12
 1ba8b54: 55                           	pushq	%rbp
 1ba8b55: 53                           	pushq	%rbx
 1ba8b56: 48 83 ec 18                  	subq	$0x18, %rsp
 1ba8b5a: 4c 8b 67 08                  	movq	0x8(%rdi), %r12
 1ba8b5e: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba8b67: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba8b6c: 31 c0                        	xorl	%eax, %eax
 1ba8b6e: 4d 85 e4                     	testq	%r12, %r12
 1ba8b71: 0f 84 39 02 00 00            	je	0x1ba8db0 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x260>
 1ba8b77: 49 89 fd                     	movq	%rdi, %r13
 1ba8b7a: 49 8d 7c 24 01               	leaq	0x1(%r12), %rdi
 1ba8b7f: 48 b8 00 00 00 00 00 00 80 3f	movabsq	$0x3f80000000000000, %rax # imm = 0x3F80000000000000
 1ba8b89: 48 39 c7                     	cmpq	%rax, %rdi
 1ba8b8c: 0f 87 a2 02 00 00            	ja	0x1ba8e34 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x2e4>
 1ba8b92: 48 01 ff                     	addq	%rdi, %rdi
 1ba8b95: 48 89 f5                     	movq	%rsi, %rbp
 1ba8b98: e8 b3 56 8a ff               	callq	0x144e250 <_Znam@plt>
 1ba8b9d: 49 8b 75 00                  	movq	(%r13), %rsi
 1ba8ba1: 48 89 c3                     	movq	%rax, %rbx
 1ba8ba4: 48 85 f6                     	testq	%rsi, %rsi
 1ba8ba7: 0f 84 bb 00 00 00            	je	0x1ba8c68 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x118>
 1ba8bad: 41 8d 4c 24 01               	leal	0x1(%r12), %ecx
 1ba8bb2: 85 c9                        	testl	%ecx, %ecx
 1ba8bb4: 0f 8e 4e 02 00 00            	jle	0x1ba8e08 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x2b8>
 1ba8bba: 0f b6 06                     	movzbl	(%rsi), %eax
 1ba8bbd: 48 8d 7e 01                  	leaq	0x1(%rsi), %rdi
 1ba8bc1: 84 c0                        	testb	%al, %al
 1ba8bc3: 0f 84 3f 02 00 00            	je	0x1ba8e08 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x2b8>
 1ba8bc9: 48 8d 53 02                  	leaq	0x2(%rbx), %rdx
 1ba8bcd: eb 29                        	jmp	0x1ba8bf8 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0xa8>
 1ba8bcf: 90                           	nop
 1ba8bd0: 83 e9 01                     	subl	$0x1, %ecx
 1ba8bd3: 49 89 d0                     	movq	%rdx, %r8
 1ba8bd6: 66 89 42 fe                  	movw	%ax, -0x2(%rdx)
 1ba8bda: 85 c9                        	testl	%ecx, %ecx
 1ba8bdc: 48 89 fe                     	movq	%rdi, %rsi
 1ba8bdf: 0f 84 8b 01 00 00            	je	0x1ba8d70 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x220>
 1ba8be5: 0f b6 06                     	movzbl	(%rsi), %eax
 1ba8be8: 48 83 c2 02                  	addq	$0x2, %rdx
 1ba8bec: 48 8d 7e 01                  	leaq	0x1(%rsi), %rdi
 1ba8bf0: 84 c0                        	testb	%al, %al
 1ba8bf2: 0f 84 78 01 00 00            	je	0x1ba8d70 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x220>
 1ba8bf8: 84 c0                        	testb	%al, %al
 1ba8bfa: 4c 8d 4a fe                  	leaq	-0x2(%rdx), %r9
 1ba8bfe: 79 d0                        	jns	0x1ba8bd0 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x80>
 1ba8c00: 83 f9 01                     	cmpl	$0x1, %ecx
 1ba8c03: 74 5a                        	je	0x1ba8c5f <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x10f>
 1ba8c05: 44 0f b6 46 01               	movzbl	0x1(%rsi), %r8d
 1ba8c0a: 44 8d 58 5f                  	leal	0x5f(%rax), %r11d
 1ba8c0e: 8d 78 80                     	leal	-0x80(%rax), %edi
 1ba8c11: 41 80 fb 0b                  	cmpb	$0xb, %r11b
 1ba8c15: 45 8d 50 80                  	leal	-0x80(%r8), %r10d
 1ba8c19: 76 11                        	jbe	0x1ba8c2c <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0xdc>
 1ba8c1b: 44 8d 58 50                  	leal	0x50(%rax), %r11d
 1ba8c1f: 41 80 fb 18                  	cmpb	$0x18, %r11b
 1ba8c23: 76 07                        	jbe	0x1ba8c2c <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0xdc>
 1ba8c25: 83 c0 36                     	addl	$0x36, %eax
 1ba8c28: 3c 33                        	cmpb	$0x33, %al
 1ba8c2a: 77 33                        	ja	0x1ba8c5f <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x10f>
 1ba8c2c: 41 83 c0 5f                  	addl	$0x5f, %r8d
 1ba8c30: 41 80 f8 5d                  	cmpb	$0x5d, %r8b
 1ba8c34: 77 29                        	ja	0x1ba8c5f <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x10f>
 1ba8c36: 40 0f b6 ff                  	movzbl	%dil, %edi
 1ba8c3a: 45 0f b6 d2                  	movzbl	%r10b, %r10d
 1ba8c3e: 83 ef 21                     	subl	$0x21, %edi
 1ba8c41: 6b ff 5e                     	imull	$0x5e, %edi, %edi
 1ba8c44: 42 8d 44 17 df               	leal	-0x21(%rdi,%r10), %eax
 1ba8c49: 3d 81 05 00 00               	cmpl	$0x581, %eax            # imm = 0x581
 1ba8c4e: 0f 87 d4 00 00 00            	ja	0x1ba8d28 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x1d8>
 1ba8c54: 3d 5a 04 00 00               	cmpl	$0x45a, %eax            # imm = 0x45A
 1ba8c59: 0f 86 21 01 00 00            	jbe	0x1ba8d80 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x230>
 1ba8c5f: 31 c9                        	xorl	%ecx, %ecx
 1ba8c61: 66 41 89 09                  	movw	%cx, (%r9)
 1ba8c65: 0f 1f 00                     	nopl	(%rax)
 1ba8c68: 0f b7 0b                     	movzwl	(%rbx), %ecx
 1ba8c6b: 66 85 c9                     	testw	%cx, %cx
 1ba8c6e: 0f 84 86 01 00 00            	je	0x1ba8dfa <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x2aa>
 1ba8c74: 45 31 c0                     	xorl	%r8d, %r8d
 1ba8c77: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 1ba8c80: 49 83 c0 01                  	addq	$0x1, %r8
 1ba8c84: 66 42 83 3c 43 00            	cmpw	$0x0, (%rbx,%r8,2)
 1ba8c8a: 4b 8d 14 00                  	leaq	(%r8,%r8), %rdx
 1ba8c8e: 75 f0                        	jne	0x1ba8c80 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x130>
 1ba8c90: 48 8b 75 08                  	movq	0x8(%rbp), %rsi
 1ba8c94: 48 b8 ff ff ff ff ff ff ff 3f	movabsq	$0x3fffffffffffffff, %rax # imm = 0x3FFFFFFFFFFFFFFF
 1ba8c9e: 48 29 f0                     	subq	%rsi, %rax
 1ba8ca1: 49 39 c0                     	cmpq	%rax, %r8
 1ba8ca4: 0f 87 6b 01 00 00            	ja	0x1ba8e15 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x2c5>
 1ba8caa: 48 8b 45 00                  	movq	(%rbp), %rax
 1ba8cae: 48 8d 7d 10                  	leaq	0x10(%rbp), %rdi
 1ba8cb2: 4d 8d 24 30                  	leaq	(%r8,%rsi), %r12
 1ba8cb6: 48 39 f8                     	cmpq	%rdi, %rax
 1ba8cb9: 0f 84 31 01 00 00            	je	0x1ba8df0 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x2a0>
 1ba8cbf: 48 8b 7d 10                  	movq	0x10(%rbp), %rdi
 1ba8cc3: 49 39 fc                     	cmpq	%rdi, %r12
 1ba8cc6: 0f 87 f4 00 00 00            	ja	0x1ba8dc0 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x270>
 1ba8ccc: 4d 85 c0                     	testq	%r8, %r8
 1ba8ccf: 74 1a                        	je	0x1ba8ceb <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x19b>
 1ba8cd1: 49 83 f8 01                  	cmpq	$0x1, %r8
 1ba8cd5: 48 8d 3c 70                  	leaq	(%rax,%rsi,2), %rdi
 1ba8cd9: 0f 84 01 01 00 00            	je	0x1ba8de0 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x290>
 1ba8cdf: 48 89 de                     	movq	%rbx, %rsi
 1ba8ce2: e8 a9 4f 8a ff               	callq	0x144dc90 <memcpy@plt>
 1ba8ce7: 48 8b 45 00                  	movq	(%rbp), %rax
 1ba8ceb: 31 d2                        	xorl	%edx, %edx
 1ba8ced: 4c 89 65 08                  	movq	%r12, 0x8(%rbp)
 1ba8cf1: 48 89 df                     	movq	%rbx, %rdi
 1ba8cf4: 66 42 89 14 60               	movw	%dx, (%rax,%r12,2)
 1ba8cf9: e8 a2 42 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba8cfe: b8 01 00 00 00               	movl	$0x1, %eax
 1ba8d03: 48 8b 5c 24 08               	movq	0x8(%rsp), %rbx
 1ba8d08: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
 1ba8d11: 0f 85 f9 00 00 00            	jne	0x1ba8e10 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x2c0>
 1ba8d17: 48 83 c4 18                  	addq	$0x18, %rsp
 1ba8d1b: 5b                           	popq	%rbx
 1ba8d1c: 5d                           	popq	%rbp
 1ba8d1d: 41 5c                        	popq	%r12
 1ba8d1f: 41 5d                        	popq	%r13
 1ba8d21: c3                           	retq
 1ba8d22: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 1ba8d28: 3d 0d 0f 00 00               	cmpl	$0xf0d, %eax            # imm = 0xF0D
 1ba8d2d: 77 61                        	ja	0x1ba8d90 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x240>
 1ba8d2f: 3d af 0e 00 00               	cmpl	$0xeaf, %eax            # imm = 0xEAF
 1ba8d34: 0f 87 25 ff ff ff            	ja	0x1ba8c5f <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x10f>
 1ba8d3a: 8d b8 7e fa ff ff            	leal	-0x582(%rax), %edi
 1ba8d40: 48 8d 05 79 06 23 04         	leaq	0x4230679(%rip), %rax   # 0x5dd93c0 <exsl_ksc5601_2uni_page30>
 1ba8d47: 0f b7 04 78                  	movzwl	(%rax,%rdi,2), %eax
 1ba8d4b: 66 83 f8 fd                  	cmpw	$-0x3, %ax
 1ba8d4f: 0f 84 0a ff ff ff            	je	0x1ba8c5f <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x10f>
 1ba8d55: 83 e9 02                     	subl	$0x2, %ecx
 1ba8d58: 48 83 c6 02                  	addq	$0x2, %rsi
 1ba8d5c: 49 89 d0                     	movq	%rdx, %r8
 1ba8d5f: 85 c9                        	testl	%ecx, %ecx
 1ba8d61: 66 89 42 fe                  	movw	%ax, -0x2(%rdx)
 1ba8d65: 0f 85 7a fe ff ff            	jne	0x1ba8be5 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x95>
 1ba8d6b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba8d70: 31 c0                        	xorl	%eax, %eax
 1ba8d72: 66 41 89 00                  	movw	%ax, (%r8)
 1ba8d76: e9 ed fe ff ff               	jmp	0x1ba8c68 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x118>
 1ba8d7b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba8d80: 48 8d 3d 99 18 23 04         	leaq	0x4231899(%rip), %rdi   # 0x5dda620 <exsl_ksc5601_2uni_page21>
 1ba8d87: 0f b7 04 47                  	movzwl	(%rdi,%rax,2), %eax
 1ba8d8b: eb be                        	jmp	0x1ba8d4b <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x1fb>
 1ba8d8d: 0f 1f 00                     	nopl	(%rax)
 1ba8d90: 3d 25 22 00 00               	cmpl	$0x2225, %eax           # imm = 0x2225
 1ba8d95: 0f 87 c4 fe ff ff            	ja	0x1ba8c5f <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x10f>
 1ba8d9b: 8d b8 f2 f0 ff ff            	leal	-0xf0e(%rax), %edi
 1ba8da1: 48 8d 05 d8 df 22 04         	leaq	0x422dfd8(%rip), %rax   # 0x5dd6d80 <exsl_ksc5601_2uni_page4a>
 1ba8da8: 0f b7 04 78                  	movzwl	(%rax,%rdi,2), %eax
 1ba8dac: eb 9d                        	jmp	0x1ba8d4b <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x1fb>
 1ba8dae: 66 90                        	nop
 1ba8db0: 31 c0                        	xorl	%eax, %eax
 1ba8db2: e9 4c ff ff ff               	jmp	0x1ba8d03 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x1b3>
 1ba8db7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
 1ba8dc0: 48 89 d9                     	movq	%rbx, %rcx
 1ba8dc3: 31 d2                        	xorl	%edx, %edx
 1ba8dc5: 48 89 ef                     	movq	%rbp, %rdi
 1ba8dc8: e8 03 1c cc ff               	callq	0x186a9d0 <std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>::_M_mutate(unsigned long, unsigned long, char16_t const*, unsigned long)>
 1ba8dcd: 48 8b 45 00                  	movq	(%rbp), %rax
 1ba8dd1: e9 15 ff ff ff               	jmp	0x1ba8ceb <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x19b>
 1ba8dd6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 1ba8de0: 66 89 0f                     	movw	%cx, (%rdi)
 1ba8de3: e9 03 ff ff ff               	jmp	0x1ba8ceb <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x19b>
 1ba8de8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
 1ba8df0: bf 07 00 00 00               	movl	$0x7, %edi
 1ba8df5: e9 c9 fe ff ff               	jmp	0x1ba8cc3 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x173>
 1ba8dfa: 48 8b 75 08                  	movq	0x8(%rbp), %rsi
 1ba8dfe: 45 31 c0                     	xorl	%r8d, %r8d
 1ba8e01: 31 d2                        	xorl	%edx, %edx
 1ba8e03: e9 a2 fe ff ff               	jmp	0x1ba8caa <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x15a>
 1ba8e08: 49 89 d8                     	movq	%rbx, %r8
 1ba8e0b: e9 60 ff ff ff               	jmp	0x1ba8d70 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x220>
 1ba8e10: e8 7b 1d 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba8e15: 48 8d 3d 42 be 1b 04         	leaq	0x41bbe42(%rip), %rdi   # 0x5d64c5e <_IO_stdin_used+0x21e>
 1ba8e1c: e8 2f 21 8a ff               	callq	0x144af50 <_ZSt20__throw_length_errorPKc@plt>
 1ba8e21: 48 89 c5                     	movq	%rax, %rbp
 1ba8e24: 48 89 df                     	movq	%rbx, %rdi
 1ba8e27: e8 74 41 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba8e2c: 48 89 ef                     	movq	%rbp, %rdi
 1ba8e2f: e8 2c 44 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba8e34: e8 67 59 8a ff               	callq	0x144e7a0 <__cxa_throw_bad_array_new_length@plt>
 1ba8e39: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000001ba8e40 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)>:
 1ba8e40: 41 54                        	pushq	%r12
 1ba8e42: 55                           	pushq	%rbp
 1ba8e43: 53                           	pushq	%rbx
 1ba8e44: 48 89 fb                     	movq	%rdi, %rbx
 1ba8e47: 48 89 f7                     	movq	%rsi, %rdi
 1ba8e4a: 48 8d 6b 10                  	leaq	0x10(%rbx), %rbp
 1ba8e4e: 48 89 de                     	movq	%rbx, %rsi
 1ba8e51: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba8e55: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
 1ba8e5d: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba8e66: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba8e6b: 31 c0                        	xorl	%eax, %eax
 1ba8e6d: 31 c0                        	xorl	%eax, %eax
 1ba8e6f: 48 89 2b                     	movq	%rbp, (%rbx)
 1ba8e72: 66 89 43 10                  	movw	%ax, 0x10(%rbx)
 1ba8e76: e8 d5 fc ff ff               	callq	0x1ba8b50 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)>
 1ba8e7b: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
 1ba8e80: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
 1ba8e89: 48 89 d8                     	movq	%rbx, %rax
 1ba8e8c: 75 09                        	jne	0x1ba8e97 <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x57>
 1ba8e8e: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba8e92: 5b                           	popq	%rbx
 1ba8e93: 5d                           	popq	%rbp
 1ba8e94: 41 5c                        	popq	%r12
 1ba8e96: c3                           	retq
 1ba8e97: e8 f4 1c 8a ff               	callq	0x144ab90 <__stack_chk_fail@plt>
 1ba8e9c: 48 8b 3b                     	movq	(%rbx), %rdi
 1ba8e9f: 49 89 c4                     	movq	%rax, %r12
 1ba8ea2: 48 39 ef                     	cmpq	%rbp, %rdi
 1ba8ea5: 74 05                        	je	0x1ba8eac <eucKrStringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&)+0x6c>
 1ba8ea7: e8 04 20 8a ff               	callq	0x144aeb0 <_ZdlPv@plt>
 1ba8eac: 4c 89 e7                     	movq	%r12, %rdi
 1ba8eaf: e8 ac 43 8a ff               	callq	0x144d260 <_Unwind_Resume@plt>
 1ba8eb4: 66 90                        	nop
 1ba8eb6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000001ba8ec0 <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)>:
 1ba8ec0: 41 56                        	pushq	%r14
 1ba8ec2: 41 55                        	pushq	%r13
 1ba8ec4: 49 89 fd                     	movq	%rdi, %r13
 1ba8ec7: 41 54                        	pushq	%r12
 1ba8ec9: 55                           	pushq	%rbp
 1ba8eca: 31 ff                        	xorl	%edi, %edi
 1ba8ecc: 53                           	pushq	%rbx
 1ba8ecd: 48 89 f5                     	movq	%rsi, %rbp
 1ba8ed0: 48 83 ec 10                  	subq	$0x10, %rsp
 1ba8ed4: 48 c7 46 08 00 00 00 00      	movq	$0x0, 0x8(%rsi)
 1ba8edc: 4d 8b 65 08                  	movq	0x8(%r13), %r12
 1ba8ee0: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 1ba8ee9: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 1ba8eee: 31 c0                        	xorl	%eax, %eax
 1ba8ef0: 48 8b 06                     	movq	(%rsi), %rax
 1ba8ef3: 66 89 38                     	movw	%di, (%rax)
 1ba8ef6: 41 8d 7c 24 01               	leal	0x1(%r12), %edi
 1ba8efb: 48 01 ff                     	addq	%rdi, %rdi
 1ba8efe: e8 4d 53 8a ff               	callq	0x144e250 <_Znam@plt>
 1ba8f03: 48 89 c3                     	movq	%rax, %rbx
 1ba8f06: 44 89 e0                     	movl	%r12d, %eax
 1ba8f09: 49 8b 7d 00                  	movq	(%r13), %rdi
 1ba8f0d: 4c 8d 34 43                  	leaq	(%rbx,%rax,2), %r14
 1ba8f11: 31 f6                        	xorl	%esi, %esi
 1ba8f13: 43 8d 14 24                  	leal	(%r12,%r12), %edx
 1ba8f17: 66 41 89 36                  	movw	%si, (%r14)
 1ba8f1b: 48 89 de                     	movq	%rbx, %rsi
 1ba8f1e: e8 cd 4b 90 01               	callq	0x34adaf0 <mToUcs2(char const*, wchar_t*, int)>
 1ba8f23: 31 c9                        	xorl	%ecx, %ecx
 1ba8f25: 66 41 89 0e                  	movw	%cx, (%r14)
 1ba8f29: 0f b7 0b                     	movzwl	(%rbx), %ecx
 1ba8f2c: 66 85 c9                     	testw	%cx, %cx
 1ba8f2f: 0f 84 d5 00 00 00            	je	0x1ba900a <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x14a>
 1ba8f35: 45 31 c0                     	xorl	%r8d, %r8d
 1ba8f38: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
 1ba8f40: 49 83 c0 01                  	addq	$0x1, %r8
 1ba8f44: 66 42 83 3c 43 00            	cmpw	$0x0, (%rbx,%r8,2)
 1ba8f4a: 4b 8d 14 00                  	leaq	(%r8,%r8), %rdx
 1ba8f4e: 75 f0                        	jne	0x1ba8f40 <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x80>
 1ba8f50: 48 8b 75 08                  	movq	0x8(%rbp), %rsi
 1ba8f54: 48 b8 ff ff ff ff ff ff ff 3f	movabsq	$0x3fffffffffffffff, %rax # imm = 0x3FFFFFFFFFFFFFFF
 1ba8f5e: 48 29 f0                     	subq	%rsi, %rax
 1ba8f61: 49 39 c0                     	cmpq	%rax, %r8
 1ba8f64: 0f 87 01 01 00 00            	ja	0x1ba906b <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x1ab>
 1ba8f6a: 48 8b 45 00                  	movq	(%rbp), %rax
 1ba8f6e: 48 8d 7d 10                  	leaq	0x10(%rbp), %rdi
 1ba8f72: 4e 8d 24 06                  	leaq	(%rsi,%r8), %r12
 1ba8f76: 48 39 f8                     	cmpq	%rdi, %rax
 1ba8f79: 0f 84 81 00 00 00            	je	0x1ba9000 <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x140>
 1ba8f7f: 48 8b 7d 10                  	movq	0x10(%rbp), %rdi
 1ba8f83: 49 39 fc                     	cmpq	%rdi, %r12
 1ba8f86: 77 48                        	ja	0x1ba8fd0 <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x110>
 1ba8f88: 4d 85 c0                     	testq	%r8, %r8
 1ba8f8b: 74 0d                        	je	0x1ba8f9a <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0xda>
 1ba8f8d: 49 83 f8 01                  	cmpq	$0x1, %r8
 1ba8f91: 48 8d 3c 70                  	leaq	(%rax,%rsi,2), %rdi
 1ba8f95: 75 51                        	jne	0x1ba8fe8 <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x128>
 1ba8f97: 66 89 0f                     	movw	%cx, (%rdi)
 1ba8f9a: 31 d2                        	xorl	%edx, %edx
 1ba8f9c: 4c 89 65 08                  	movq	%r12, 0x8(%rbp)
 1ba8fa0: 48 89 df                     	movq	%rbx, %rdi
 1ba8fa3: 66 42 89 14 60               	movw	%dx, (%rax,%r12,2)
 1ba8fa8: e8 f3 3f 8a ff               	callq	0x144cfa0 <_ZdaPv@plt>
 1ba8fad: b8 01 00 00 00               	movl	$0x1, %eax
 1ba8fb2: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
 1ba8fb7: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 1ba8fc0: 75 56                        	jne	0x1ba9018 <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0x158>
 1ba8fc2: 48 83 c4 10                  	addq	$0x10, %rsp
 1ba8fc6: 5b                           	popq	%rbx
 1ba8fc7: 5d                           	popq	%rbp
 1ba8fc8: 41 5c                        	popq	%r12
 1ba8fca: 41 5d                        	popq	%r13
 1ba8fcc: 41 5e                        	popq	%r14
 1ba8fce: c3                           	retq
 1ba8fcf: 90                           	nop
 1ba8fd0: 48 89 d9                     	movq	%rbx, %rcx
 1ba8fd3: 31 d2                        	xorl	%edx, %edx
 1ba8fd5: 48 89 ef                     	movq	%rbp, %rdi
 1ba8fd8: e8 f3 19 cc ff               	callq	0x186a9d0 <std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>::_M_mutate(unsigned long, unsigned long, char16_t const*, unsigned long)>
 1ba8fdd: 48 8b 45 00                  	movq	(%rbp), %rax
 1ba8fe1: eb b7                        	jmp	0x1ba8f9a <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0xda>
 1ba8fe3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 1ba8fe8: 48 89 de                     	movq	%rbx, %rsi
 1ba8feb: e8 a0 4c 8a ff               	callq	0x144dc90 <memcpy@plt>
 1ba8ff0: 48 8b 45 00                  	movq	(%rbp), %rax
 1ba8ff4: eb a4                        	jmp	0x1ba8f9a <utf8StringToUtf16String(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::__cxx11::basic_string<char16_t, std::char_traits<char16_t>, std::allocator<char16_t>>&)+0xda>
 1ba8ff6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
