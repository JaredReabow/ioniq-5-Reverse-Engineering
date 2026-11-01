
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

0000000002c0b380 <CAppManagerComm::Initialize(int, char**)>:
 2c0b380: 55                           	pushq	%rbp
 2c0b381: 48 89 e5                     	movq	%rsp, %rbp
 2c0b384: 41 57                        	pushq	%r15
 2c0b386: 41 56                        	pushq	%r14
 2c0b388: 41 55                        	pushq	%r13
 2c0b38a: 41 54                        	pushq	%r12
 2c0b38c: 49 89 fd                     	movq	%rdi, %r13
 2c0b38f: 53                           	pushq	%rbx
 2c0b390: 48 81 ec f8 0b 00 00         	subq	$0xbf8, %rsp            # imm = 0xBF8
 2c0b397: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 2c0b3a0: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
 2c0b3a4: 31 c0                        	xorl	%eax, %eax
 2c0b3a6: e8 15 f8 ff ff               	callq	0x2c0abc0 <CAppManagerComm::GetInitStatusFromSystem(int, char**)>
 2c0b3ab: 4c 89 ef                     	movq	%r13, %rdi
 2c0b3ae: e8 1d e9 fd ff               	callq	0x2be9cd0 <CAppManagerComm::CreateSharedMemKnobZoomInOut()>
 2c0b3b3: e8 28 f1 f9 fe               	callq	0x1baa4e0 <SystemVariant::GetInstance()>
 2c0b3b8: 48 89 c7                     	movq	%rax, %rdi
 2c0b3bb: e8 90 22 fa fe               	callq	0x1bad650 <SystemVariant::getRegion()>
 2c0b3c0: 4c 8d 05 19 25 3b 03         	leaq	0x33b2519(%rip), %r8    # 0x5fbd8e0 <typeinfo name for CAppModeInfoImpl+0x1810>
 2c0b3c7: 48 8d 15 9a d9 3b 03         	leaq	0x33bd99a(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b3ce: 48 8d 35 13 0d 3b 03         	leaq	0x33b0d13(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b3d5: 41 89 c1                     	movl	%eax, %r9d
 2c0b3d8: 41 89 85 dc 01 00 00         	movl	%eax, 0x1dc(%r13)
 2c0b3df: b9 d3 00 00 00               	movl	$0xd3, %ecx
 2c0b3e4: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b3e9: 31 c0                        	xorl	%eax, %eax
 2c0b3eb: e8 40 49 c0 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 2c0b3f0: 48 8d 85 20 f4 ff ff         	leaq	-0xbe0(%rbp), %rax
 2c0b3f7: 48 89 c3                     	movq	%rax, %rbx
 2c0b3fa: 48 89 c7                     	movq	%rax, %rdi
 2c0b3fd: 48 89 85 e8 f3 ff ff         	movq	%rax, -0xc18(%rbp)
 2c0b404: e8 d7 16 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b409: 48 89 df                     	movq	%rbx, %rdi
 2c0b40c: e8 7f fc 83 fe               	callq	0x144b090 <_ZNK15QDBusConnection11isConnectedEv@plt>
 2c0b411: 84 c0                        	testb	%al, %al
 2c0b413: 0f 84 fc 02 00 00            	je	0x2c0b715 <CAppManagerComm::Initialize(int, char**)+0x395>
 2c0b419: 4c 8d 05 f8 ad 3b 03         	leaq	0x33badf8(%rip), %r8    # 0x5fc6218 <typeinfo name for CAppModeInfoImpl+0xa148>
 2c0b420: 48 8d 15 41 d9 3b 03         	leaq	0x33bd941(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b427: 48 8d 35 ba 0c 3b 03         	leaq	0x33b0cba(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b42e: b9 d7 00 00 00               	movl	$0xd7, %ecx
 2c0b433: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b438: 31 c0                        	xorl	%eax, %eax
 2c0b43a: e8 71 42 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0b43f: 48 8d 9d 40 f4 ff ff         	leaq	-0xbc0(%rbp), %rbx
 2c0b446: 48 8d 35 40 14 3a 03         	leaq	0x33a1440(%rip), %rsi   # 0x5fac88d <CNaviVRComm::Initialize()::__func__+0xd5>
 2c0b44d: 48 89 df                     	movq	%rbx, %rdi
 2c0b450: e8 db 3e f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b455: 48 8d 85 30 f4 ff ff         	leaq	-0xbd0(%rbp), %rax
 2c0b45c: 48 89 c7                     	movq	%rax, %rdi
 2c0b45f: 49 89 c6                     	movq	%rax, %r14
 2c0b462: e8 79 16 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b467: 48 89 de                     	movq	%rbx, %rsi
 2c0b46a: 4c 89 f7                     	movq	%r14, %rdi
 2c0b46d: e8 de 31 84 fe               	callq	0x144e650 <_ZN15QDBusConnection15registerServiceERK7QString@plt>
 2c0b472: 4c 89 f7                     	movq	%r14, %rdi
 2c0b475: 41 89 c4                     	movl	%eax, %r12d
 2c0b478: e8 33 24 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0b47d: 48 89 df                     	movq	%rbx, %rdi
 2c0b480: e8 bb 85 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b485: 4c 8d 05 bc ad 3b 03         	leaq	0x33badbc(%rip), %r8    # 0x5fc6248 <typeinfo name for CAppModeInfoImpl+0xa178>
 2c0b48c: 48 8d 15 d5 d8 3b 03         	leaq	0x33bd8d5(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b493: 48 8d 35 4e 0c 3b 03         	leaq	0x33b0c4e(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b49a: 45 0f b6 cc                  	movzbl	%r12b, %r9d
 2c0b49e: b9 d9 00 00 00               	movl	$0xd9, %ecx
 2c0b4a3: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b4a8: 31 c0                        	xorl	%eax, %eax
 2c0b4aa: e8 01 42 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0b4af: 48 8d 9d 60 f4 ff ff         	leaq	-0xba0(%rbp), %rbx
 2c0b4b6: 48 8d 35 2b d4 39 03         	leaq	0x339d42b(%rip), %rsi   # 0x5fa88e8 <typeinfo name for NimoLanguageImpl+0x768>
 2c0b4bd: 48 89 df                     	movq	%rbx, %rdi
 2c0b4c0: e8 6b 3e f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b4c5: 48 8d 85 50 f4 ff ff         	leaq	-0xbb0(%rbp), %rax
 2c0b4cc: 48 89 c7                     	movq	%rax, %rdi
 2c0b4cf: 49 89 c6                     	movq	%rax, %r14
 2c0b4d2: e8 09 16 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b4d7: b9 01 00 00 00               	movl	$0x1, %ecx
 2c0b4dc: 4c 89 ea                     	movq	%r13, %rdx
 2c0b4df: 48 89 de                     	movq	%rbx, %rsi
 2c0b4e2: 4c 89 f7                     	movq	%r14, %rdi
 2c0b4e5: e8 56 09 84 fe               	callq	0x144be40 <_ZN15QDBusConnection14registerObjectERK7QStringP7QObject6QFlagsINS_14RegisterOptionEE@plt>
 2c0b4ea: 4c 89 f7                     	movq	%r14, %rdi
 2c0b4ed: 41 89 c4                     	movl	%eax, %r12d
 2c0b4f0: e8 bb 23 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0b4f5: 48 89 df                     	movq	%rbx, %rdi
 2c0b4f8: e8 43 85 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b4fd: 4c 8d 05 94 ad 3b 03         	leaq	0x33bad94(%rip), %r8    # 0x5fc6298 <typeinfo name for CAppModeInfoImpl+0xa1c8>
 2c0b504: 48 8d 15 5d d8 3b 03         	leaq	0x33bd85d(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b50b: 48 8d 35 d6 0b 3b 03         	leaq	0x33b0bd6(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b512: 45 0f b6 cc                  	movzbl	%r12b, %r9d
 2c0b516: b9 db 00 00 00               	movl	$0xdb, %ecx
 2c0b51b: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b520: 31 c0                        	xorl	%eax, %eax
 2c0b522: e8 89 41 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0b527: 48 8d 9d 80 f4 ff ff         	leaq	-0xb80(%rbp), %rbx
 2c0b52e: 48 8d 35 c2 27 3b 03         	leaq	0x33b27c2(%rip), %rsi   # 0x5fbdcf7 <typeinfo name for CAppModeInfoImpl+0x1c27>
 2c0b535: 48 89 df                     	movq	%rbx, %rdi
 2c0b538: e8 f3 3d f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b53d: 48 8d 85 70 f4 ff ff         	leaq	-0xb90(%rbp), %rax
 2c0b544: 48 89 c7                     	movq	%rax, %rdi
 2c0b547: 49 89 c6                     	movq	%rax, %r14
 2c0b54a: e8 91 15 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b54f: b9 01 00 00 00               	movl	$0x1, %ecx
 2c0b554: 4c 89 ea                     	movq	%r13, %rdx
 2c0b557: 48 89 de                     	movq	%rbx, %rsi
 2c0b55a: 4c 89 f7                     	movq	%r14, %rdi
 2c0b55d: e8 de 08 84 fe               	callq	0x144be40 <_ZN15QDBusConnection14registerObjectERK7QStringP7QObject6QFlagsINS_14RegisterOptionEE@plt>
 2c0b562: 4c 89 f7                     	movq	%r14, %rdi
 2c0b565: 41 89 c4                     	movl	%eax, %r12d
 2c0b568: e8 43 23 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0b56d: 48 89 df                     	movq	%rbx, %rdi
 2c0b570: e8 cb 84 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b575: 4c 8d 05 5c ad 3b 03         	leaq	0x33bad5c(%rip), %r8    # 0x5fc62d8 <typeinfo name for CAppModeInfoImpl+0xa208>
 2c0b57c: 48 8d 15 e5 d7 3b 03         	leaq	0x33bd7e5(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b583: 48 8d 35 5e 0b 3b 03         	leaq	0x33b0b5e(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b58a: 45 0f b6 cc                  	movzbl	%r12b, %r9d
 2c0b58e: b9 dd 00 00 00               	movl	$0xdd, %ecx
 2c0b593: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b598: 31 c0                        	xorl	%eax, %eax
 2c0b59a: e8 11 41 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0b59f: 48 8d 9d a0 f4 ff ff         	leaq	-0xb60(%rbp), %rbx
 2c0b5a6: 48 8d 35 b5 27 3b 03         	leaq	0x33b27b5(%rip), %rsi   # 0x5fbdd62 <typeinfo name for CAppModeInfoImpl+0x1c92>
 2c0b5ad: 48 89 df                     	movq	%rbx, %rdi
 2c0b5b0: e8 7b 3d f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b5b5: 48 8d 85 90 f4 ff ff         	leaq	-0xb70(%rbp), %rax
 2c0b5bc: 48 89 c7                     	movq	%rax, %rdi
 2c0b5bf: 49 89 c6                     	movq	%rax, %r14
 2c0b5c2: e8 19 15 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b5c7: b9 01 00 00 00               	movl	$0x1, %ecx
 2c0b5cc: 4c 89 ea                     	movq	%r13, %rdx
 2c0b5cf: 48 89 de                     	movq	%rbx, %rsi
 2c0b5d2: 4c 89 f7                     	movq	%r14, %rdi
 2c0b5d5: e8 66 08 84 fe               	callq	0x144be40 <_ZN15QDBusConnection14registerObjectERK7QStringP7QObject6QFlagsINS_14RegisterOptionEE@plt>
 2c0b5da: 4c 89 f7                     	movq	%r14, %rdi
 2c0b5dd: 41 89 c4                     	movl	%eax, %r12d
 2c0b5e0: e8 cb 22 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0b5e5: 48 89 df                     	movq	%rbx, %rdi
 2c0b5e8: e8 53 84 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b5ed: 4c 8d 05 24 ad 3b 03         	leaq	0x33bad24(%rip), %r8    # 0x5fc6318 <typeinfo name for CAppModeInfoImpl+0xa248>
 2c0b5f4: 48 8d 15 6d d7 3b 03         	leaq	0x33bd76d(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b5fb: 48 8d 35 e6 0a 3b 03         	leaq	0x33b0ae6(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b602: 45 0f b6 cc                  	movzbl	%r12b, %r9d
 2c0b606: b9 df 00 00 00               	movl	$0xdf, %ecx
 2c0b60b: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b610: 31 c0                        	xorl	%eax, %eax
 2c0b612: e8 99 40 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0b617: 48 8d 9d c0 f4 ff ff         	leaq	-0xb40(%rbp), %rbx
 2c0b61e: 48 8d 35 4f 27 3b 03         	leaq	0x33b274f(%rip), %rsi   # 0x5fbdd74 <typeinfo name for CAppModeInfoImpl+0x1ca4>
 2c0b625: 48 89 df                     	movq	%rbx, %rdi
 2c0b628: e8 03 3d f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b62d: 48 8d 85 b0 f4 ff ff         	leaq	-0xb50(%rbp), %rax
 2c0b634: 48 89 c7                     	movq	%rax, %rdi
 2c0b637: 49 89 c6                     	movq	%rax, %r14
 2c0b63a: e8 a1 14 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b63f: b9 01 00 00 00               	movl	$0x1, %ecx
 2c0b644: 4c 89 ea                     	movq	%r13, %rdx
 2c0b647: 48 89 de                     	movq	%rbx, %rsi
 2c0b64a: 4c 89 f7                     	movq	%r14, %rdi
 2c0b64d: e8 ee 07 84 fe               	callq	0x144be40 <_ZN15QDBusConnection14registerObjectERK7QStringP7QObject6QFlagsINS_14RegisterOptionEE@plt>
 2c0b652: 4c 89 f7                     	movq	%r14, %rdi
 2c0b655: 41 89 c4                     	movl	%eax, %r12d
 2c0b658: e8 53 22 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0b65d: 48 89 df                     	movq	%rbx, %rdi
 2c0b660: e8 db 83 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b665: 4c 8d 05 f4 ac 3b 03         	leaq	0x33bacf4(%rip), %r8    # 0x5fc6360 <typeinfo name for CAppModeInfoImpl+0xa290>
 2c0b66c: 48 8d 15 f5 d6 3b 03         	leaq	0x33bd6f5(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b673: 48 8d 35 6e 0a 3b 03         	leaq	0x33b0a6e(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b67a: 45 0f b6 cc                  	movzbl	%r12b, %r9d
 2c0b67e: b9 e1 00 00 00               	movl	$0xe1, %ecx
 2c0b683: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b688: 31 c0                        	xorl	%eax, %eax
 2c0b68a: e8 21 40 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0b68f: 48 8d 9d e0 f4 ff ff         	leaq	-0xb20(%rbp), %rbx
 2c0b696: 48 8d 35 eb 26 3b 03         	leaq	0x33b26eb(%rip), %rsi   # 0x5fbdd88 <typeinfo name for CAppModeInfoImpl+0x1cb8>
 2c0b69d: 48 89 df                     	movq	%rbx, %rdi
 2c0b6a0: e8 8b 3c f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b6a5: 48 8d 85 d0 f4 ff ff         	leaq	-0xb30(%rbp), %rax
 2c0b6ac: 48 89 c7                     	movq	%rax, %rdi
 2c0b6af: 49 89 c6                     	movq	%rax, %r14
 2c0b6b2: e8 29 14 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b6b7: b9 01 00 00 00               	movl	$0x1, %ecx
 2c0b6bc: 4c 89 ea                     	movq	%r13, %rdx
 2c0b6bf: 48 89 de                     	movq	%rbx, %rsi
 2c0b6c2: 4c 89 f7                     	movq	%r14, %rdi
 2c0b6c5: e8 76 07 84 fe               	callq	0x144be40 <_ZN15QDBusConnection14registerObjectERK7QStringP7QObject6QFlagsINS_14RegisterOptionEE@plt>
 2c0b6ca: 4c 89 f7                     	movq	%r14, %rdi
 2c0b6cd: 41 89 c4                     	movl	%eax, %r12d
 2c0b6d0: e8 db 21 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0b6d5: 48 89 df                     	movq	%rbx, %rdi
 2c0b6d8: e8 63 83 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b6dd: 4c 8d 05 c4 ac 3b 03         	leaq	0x33bacc4(%rip), %r8    # 0x5fc63a8 <typeinfo name for CAppModeInfoImpl+0xa2d8>
 2c0b6e4: 48 8d 15 7d d6 3b 03         	leaq	0x33bd67d(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0b6eb: 48 8d 35 f6 09 3b 03         	leaq	0x33b09f6(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0b6f2: 45 0f b6 cc                  	movzbl	%r12b, %r9d
 2c0b6f6: b9 e3 00 00 00               	movl	$0xe3, %ecx
 2c0b6fb: bf 02 00 00 00               	movl	$0x2, %edi
 2c0b700: 31 c0                        	xorl	%eax, %eax
 2c0b702: e8 a9 3f c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0b707: 41 83 bd dc 01 00 00 05      	cmpl	$0x5, 0x1dc(%r13)
 2c0b70f: 0f 84 1b 28 00 00            	je	0x2c0df30 <CAppManagerComm::Initialize(int, char**)+0x2bb0>
 2c0b715: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b71a: e8 11 27 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b71f: 4c 89 ee                     	movq	%r13, %rsi
 2c0b722: 48 89 c7                     	movq	%rax, %rdi
 2c0b725: 48 89 c3                     	movq	%rax, %rbx
 2c0b728: e8 73 28 6b 00               	callq	0x32bdfa0 <BroadcastAdaptor::BroadcastAdaptor(QObject*)>
 2c0b72d: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b732: e8 f9 26 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b737: 4c 89 ee                     	movq	%r13, %rsi
 2c0b73a: 48 89 c7                     	movq	%rax, %rdi
 2c0b73d: 48 89 c3                     	movq	%rax, %rbx
 2c0b740: e8 5b 29 6b 00               	callq	0x32be0a0 <RegistrationAdaptor::RegistrationAdaptor(QObject*)>
 2c0b745: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b74a: e8 e1 26 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b74f: 4c 89 ee                     	movq	%r13, %rsi
 2c0b752: 48 89 c7                     	movq	%rax, %rdi
 2c0b755: 48 89 c3                     	movq	%rax, %rbx
 2c0b758: e8 a3 2b 6b 00               	callq	0x32be300 <ScreentransitionAdaptor::ScreentransitionAdaptor(QObject*)>
 2c0b75d: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b762: e8 c9 26 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b767: 4c 89 ee                     	movq	%r13, %rsi
 2c0b76a: 48 89 c7                     	movq	%rax, %rdi
 2c0b76d: 48 89 c3                     	movq	%rax, %rbx
 2c0b770: e8 1b 16 6b 00               	callq	0x32bcd90 <AppbaseAdaptor::AppbaseAdaptor(QObject*)>
 2c0b775: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b77a: e8 b1 26 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b77f: 4c 89 ee                     	movq	%r13, %rsi
 2c0b782: 48 89 c7                     	movq	%rax, %rdi
 2c0b785: 48 89 c3                     	movq	%rax, %rbx
 2c0b788: e8 f3 03 6b 00               	callq	0x32bbb80 <InterfaceAdaptor::InterfaceAdaptor(QObject*)>
 2c0b78d: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b792: e8 99 26 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b797: 4c 89 ee                     	movq	%r13, %rsi
 2c0b79a: 48 89 c7                     	movq	%rax, %rdi
 2c0b79d: 48 89 c3                     	movq	%rax, %rbx
 2c0b7a0: e8 cb 0a 6b 00               	callq	0x32bc270 <MydataAdaptor::MydataAdaptor(QObject*)>
 2c0b7a5: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b7aa: e8 81 26 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b7af: 4c 89 ee                     	movq	%r13, %rsi
 2c0b7b2: 48 89 c7                     	movq	%rax, %rdi
 2c0b7b5: 48 89 c3                     	movq	%rax, %rbx
 2c0b7b8: e8 23 09 6b 00               	callq	0x32bc0e0 <GpsStatusAdaptor::GpsStatusAdaptor(QObject*)>
 2c0b7bd: bf 10 00 00 00               	movl	$0x10, %edi
 2c0b7c2: e8 69 26 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0b7c7: 4c 89 ee                     	movq	%r13, %rsi
 2c0b7ca: 48 89 c7                     	movq	%rax, %rdi
 2c0b7cd: 48 89 c3                     	movq	%rax, %rbx
 2c0b7d0: e8 2b 07 6b 00               	callq	0x32bbf00 <AddressInfoAdaptor::AddressInfoAdaptor(QObject*)>
 2c0b7d5: 4c 8d b5 b0 fe ff ff         	leaq	-0x150(%rbp), %r14
 2c0b7dc: 48 8d 9d 70 ff ff ff         	leaq	-0x90(%rbp), %rbx
 2c0b7e3: c7 85 1c f4 ff ff ff ff ff ff	movl	$0xffffffff, -0xbe4(%rbp) # imm = 0xFFFFFFFF
 2c0b7ed: 48 c7 85 c0 fe ff ff 00 00 00 00     	movq	$0x0, -0x140(%rbp)
 2c0b7f8: 48 c7 85 c8 fe ff ff 00 00 00 00     	movq	$0x0, -0x138(%rbp)
 2c0b803: 49 8d 7e 40                  	leaq	0x40(%r14), %rdi
 2c0b807: 48 c7 85 d0 fe ff ff 00 00 00 00     	movq	$0x0, -0x130(%rbp)
 2c0b812: 48 c7 85 d8 fe ff ff 00 00 00 00     	movq	$0x0, -0x128(%rbp)
 2c0b81d: 48 c7 85 e0 fe ff ff 00 00 00 00     	movq	$0x0, -0x120(%rbp)
 2c0b828: 48 c7 85 e8 fe ff ff 00 00 00 00     	movq	$0x0, -0x118(%rbp)
 2c0b833: 48 c7 85 f0 fe ff ff 00 00 00 00     	movq	$0x0, -0x110(%rbp)
 2c0b83e: 48 c7 85 f8 fe ff ff 00 00 00 00     	movq	$0x0, -0x108(%rbp)
 2c0b849: 48 c7 85 00 ff ff ff 00 00 00 00     	movq	$0x0, -0x100(%rbp)
 2c0b854: c7 85 b0 fe ff ff 00 00 00 00	movl	$0x0, -0x150(%rbp)
 2c0b85e: 48 c7 85 b8 fe ff ff 00 00 00 00     	movq	$0x0, -0x148(%rbp)
 2c0b869: e8 f2 76 fd ff               	callq	0x2be2f60 <std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>>>::clear() (.constprop.129)>
 2c0b86e: 49 8d 7e 10                  	leaq	0x10(%r14), %rdi
 2c0b872: 48 89 de                     	movq	%rbx, %rsi
 2c0b875: c7 85 70 ff ff ff 01 00 00 00	movl	$0x1, -0x90(%rbp)
 2c0b87f: e8 dc a2 cd fe               	callq	0x18e5b60 <void std::vector<int, std::allocator<int>>::emplace_back<int>(int&&)>
 2c0b884: 49 8d 7e 10                  	leaq	0x10(%r14), %rdi
 2c0b888: 48 89 de                     	movq	%rbx, %rsi
 2c0b88b: c7 85 70 ff ff ff 02 00 00 00	movl	$0x2, -0x90(%rbp)
 2c0b895: e8 c6 a2 cd fe               	callq	0x18e5b60 <void std::vector<int, std::allocator<int>>::emplace_back<int>(int&&)>
 2c0b89a: 48 8d 85 10 ff ff ff         	leaq	-0xf0(%rbp), %rax
 2c0b8a1: 4c 89 f6                     	movq	%r14, %rsi
 2c0b8a4: 48 89 c7                     	movq	%rax, %rdi
 2c0b8a7: 49 89 c7                     	movq	%rax, %r15
 2c0b8aa: 48 89 85 08 f4 ff ff         	movq	%rax, -0xbf8(%rbp)
 2c0b8b1: e8 2a 5b 09 ff               	callq	0x1ca13e0 <NaviAdapter::ExternalParameter::ExternalParameter(NaviAdapter::ExternalParameter const&)>
 2c0b8b6: 4c 8d a5 1c f4 ff ff         	leaq	-0xbe4(%rbp), %r12
 2c0b8bd: 4c 89 fe                     	movq	%r15, %rsi
 2c0b8c0: 31 ff                        	xorl	%edi, %edi
 2c0b8c2: 4c 89 e2                     	movq	%r12, %rdx
 2c0b8c5: e8 86 be 66 ff               	callq	0x2277750 <NaviAdapter::AppModeInfo::sendExternalMessage(NaviAdapter::AppModeInfo::eMessageId, NaviAdapter::ExternalParameter, int&)>
 2c0b8ca: 4c 89 ff                     	movq	%r15, %rdi
 2c0b8cd: 4c 89 bd 08 f4 ff ff         	movq	%r15, -0xbf8(%rbp)
 2c0b8d4: e8 97 b9 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c0b8d9: 4c 89 f6                     	movq	%r14, %rsi
 2c0b8dc: 48 89 df                     	movq	%rbx, %rdi
 2c0b8df: e8 fc 5a 09 ff               	callq	0x1ca13e0 <NaviAdapter::ExternalParameter::ExternalParameter(NaviAdapter::ExternalParameter const&)>
 2c0b8e4: 4c 89 e2                     	movq	%r12, %rdx
 2c0b8e7: 48 89 de                     	movq	%rbx, %rsi
 2c0b8ea: bf 01 00 00 00               	movl	$0x1, %edi
 2c0b8ef: e8 5c be 66 ff               	callq	0x2277750 <NaviAdapter::AppModeInfo::sendExternalMessage(NaviAdapter::AppModeInfo::eMessageId, NaviAdapter::ExternalParameter, int&)>
 2c0b8f4: 48 89 df                     	movq	%rbx, %rdi
 2c0b8f7: e8 74 b9 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c0b8fc: 48 8d 8d 30 f5 ff ff         	leaq	-0xad0(%rbp), %rcx
 2c0b903: 48 8d 35 11 26 3b 03         	leaq	0x33b2611(%rip), %rsi   # 0x5fbdf1b <typeinfo name for CAppModeInfoImpl+0x1e4b>
 2c0b90a: 48 89 cf                     	movq	%rcx, %rdi
 2c0b90d: 48 89 8d f8 f3 ff ff         	movq	%rcx, -0xc08(%rbp)
 2c0b914: e8 17 3a f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b919: 48 8d 95 20 f5 ff ff         	leaq	-0xae0(%rbp), %rdx
 2c0b920: 48 8d 35 49 22 3b 03         	leaq	0x33b2249(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0b927: 48 89 d7                     	movq	%rdx, %rdi
 2c0b92a: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0b931: e8 fa 39 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0b936: 4c 8b 25 e3 29 aa 04         	movq	0x4aa29e3(%rip), %r12   # 0x76ae320 <_GLOBAL_OFFSET_TABLE_+0x50b8>
 2c0b93d: 4c 8d bd 10 f5 ff ff         	leaq	-0xaf0(%rbp), %r15
 2c0b944: 4c 89 ff                     	movq	%r15, %rdi
 2c0b947: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0b94e: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0b955: e8 86 11 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b95a: 48 8d 35 c7 25 3b 03         	leaq	0x33b25c7(%rip), %rsi   # 0x5fbdf28 <typeinfo name for CAppModeInfoImpl+0x1e58>
 2c0b961: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0b965: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0b96c: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0b973: 4d 89 e9                     	movq	%r13, %r9
 2c0b976: 48 89 da                     	movq	%rbx, %rdx
 2c0b979: 56                           	pushq	%rsi
 2c0b97a: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0b981: 4c 89 ff                     	movq	%r15, %rdi
 2c0b984: e8 47 f6 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0b989: 41 5b                        	popq	%r11
 2c0b98b: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0b991: 4c 89 ff                     	movq	%r15, %rdi
 2c0b994: 58                           	popq	%rax
 2c0b995: e8 16 1f 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0b99a: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0b9a1: e8 9a 80 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b9a6: 48 89 df                     	movq	%rbx, %rdi
 2c0b9a9: e8 92 80 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b9ae: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0b9b5: e8 86 80 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b9ba: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0b9c1: e8 7a 80 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0b9c6: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0b9cd: 84 c0                        	testb	%al, %al
 2c0b9cf: 0f 85 4b 1f 00 00            	jne	0x2c0d920 <CAppManagerComm::Initialize(int, char**)+0x25a0>
 2c0b9d5: 48 8d 85 40 f5 ff ff         	leaq	-0xac0(%rbp), %rax
 2c0b9dc: 48 89 c7                     	movq	%rax, %rdi
 2c0b9df: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0b9e6: e8 f5 10 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0b9eb: 4c 8d bd 90 fb ff ff         	leaq	-0x470(%rbp), %r15
 2c0b9f2: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0b9f9: 4c 89 ff                     	movq	%r15, %rdi
 2c0b9fc: e8 3f f2 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0ba01: 4c 89 ff                     	movq	%r15, %rdi
 2c0ba04: e8 a7 02 84 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0ba09: 4c 8d 05 30 aa 3b 03         	leaq	0x33baa30(%rip), %r8    # 0x5fc6440 <typeinfo name for CAppModeInfoImpl+0xa370>
 2c0ba10: 48 8d 15 51 d3 3b 03         	leaq	0x33bd351(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0ba17: 48 8d 35 ca 06 3b 03         	leaq	0x33b06ca(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0ba1e: 41 89 c1                     	movl	%eax, %r9d
 2c0ba21: b9 1c 01 00 00               	movl	$0x11c, %ecx            # imm = 0x11C
 2c0ba26: bf 03 00 00 00               	movl	$0x3, %edi
 2c0ba2b: 31 c0                        	xorl	%eax, %eax
 2c0ba2d: e8 7e 3c c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0ba32: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0ba36: e8 05 80 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ba3b: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0ba3f: e8 fc 7f f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ba44: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0ba4b: e8 60 1e 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0ba50: 48 8d 85 70 f5 ff ff         	leaq	-0xa90(%rbp), %rax
 2c0ba57: 48 8d 35 dd 24 3b 03         	leaq	0x33b24dd(%rip), %rsi   # 0x5fbdf3b <typeinfo name for CAppModeInfoImpl+0x1e6b>
 2c0ba5e: 48 89 c7                     	movq	%rax, %rdi
 2c0ba61: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0ba68: e8 c3 38 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0ba6d: 48 8d 8d 60 f5 ff ff         	leaq	-0xaa0(%rbp), %rcx
 2c0ba74: 48 8d 35 f5 20 3b 03         	leaq	0x33b20f5(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0ba7b: 48 89 cf                     	movq	%rcx, %rdi
 2c0ba7e: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0ba85: e8 a6 38 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0ba8a: 4c 8d bd 50 f5 ff ff         	leaq	-0xab0(%rbp), %r15
 2c0ba91: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0ba98: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0ba9f: 4c 89 ff                     	movq	%r15, %rdi
 2c0baa2: e8 39 10 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0baa7: 48 8d 15 9c 24 3b 03         	leaq	0x33b249c(%rip), %rdx   # 0x5fbdf4a <typeinfo name for CAppModeInfoImpl+0x1e7a>
 2c0baae: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0bab2: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0bab9: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0bac0: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0bac7: 4d 89 e9                     	movq	%r13, %r9
 2c0baca: 52                           	pushq	%rdx
 2c0bacb: 4c 89 ff                     	movq	%r15, %rdi
 2c0bace: 48 89 da                     	movq	%rbx, %rdx
 2c0bad1: e8 fa f4 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0bad6: 41 59                        	popq	%r9
 2c0bad8: 41 5a                        	popq	%r10
 2c0bada: 4c 89 ff                     	movq	%r15, %rdi
 2c0badd: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0bae3: e8 c8 1d 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0bae8: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0baef: e8 4c 7f f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0baf4: 48 89 df                     	movq	%rbx, %rdi
 2c0baf7: e8 44 7f f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bafc: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0bb03: e8 38 7f f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bb08: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0bb0f: e8 2c 7f f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bb14: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0bb1b: 84 c0                        	testb	%al, %al
 2c0bb1d: 0f 85 ad 23 00 00            	jne	0x2c0ded0 <CAppManagerComm::Initialize(int, char**)+0x2b50>
 2c0bb23: 48 8d 85 80 f5 ff ff         	leaq	-0xa80(%rbp), %rax
 2c0bb2a: 48 89 c7                     	movq	%rax, %rdi
 2c0bb2d: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0bb34: e8 a7 0f 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0bb39: 4c 8d bd b0 fb ff ff         	leaq	-0x450(%rbp), %r15
 2c0bb40: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0bb47: 4c 89 ff                     	movq	%r15, %rdi
 2c0bb4a: e8 f1 f0 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0bb4f: 4c 89 ff                     	movq	%r15, %rdi
 2c0bb52: e8 59 01 84 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0bb57: 4c 8d 05 6a a9 3b 03         	leaq	0x33ba96a(%rip), %r8    # 0x5fc64c8 <typeinfo name for CAppModeInfoImpl+0xa3f8>
 2c0bb5e: 48 8d 15 03 d2 3b 03         	leaq	0x33bd203(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0bb65: 48 8d 35 7c 05 3b 03         	leaq	0x33b057c(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0bb6c: 41 89 c1                     	movl	%eax, %r9d
 2c0bb6f: b9 22 01 00 00               	movl	$0x122, %ecx            # imm = 0x122
 2c0bb74: bf 03 00 00 00               	movl	$0x3, %edi
 2c0bb79: 31 c0                        	xorl	%eax, %eax
 2c0bb7b: e8 30 3b c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0bb80: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0bb84: e8 b7 7e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bb89: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0bb8d: e8 ae 7e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bb92: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0bb99: e8 12 1d 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0bb9e: 48 8d 85 b0 f5 ff ff         	leaq	-0xa50(%rbp), %rax
 2c0bba5: 48 8d 35 b3 23 3b 03         	leaq	0x33b23b3(%rip), %rsi   # 0x5fbdf5f <typeinfo name for CAppModeInfoImpl+0x1e8f>
 2c0bbac: 48 89 c7                     	movq	%rax, %rdi
 2c0bbaf: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0bbb6: e8 75 37 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0bbbb: 48 8d 8d a0 f5 ff ff         	leaq	-0xa60(%rbp), %rcx
 2c0bbc2: 48 8d 35 a7 1f 3b 03         	leaq	0x33b1fa7(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0bbc9: 48 89 cf                     	movq	%rcx, %rdi
 2c0bbcc: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0bbd3: e8 58 37 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0bbd8: 4c 8d bd 90 f5 ff ff         	leaq	-0xa70(%rbp), %r15
 2c0bbdf: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0bbe6: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0bbed: 4c 89 ff                     	movq	%r15, %rdi
 2c0bbf0: e8 eb 0e 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0bbf5: 48 8d 15 75 23 3b 03         	leaq	0x33b2375(%rip), %rdx   # 0x5fbdf71 <typeinfo name for CAppModeInfoImpl+0x1ea1>
 2c0bbfc: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0bc00: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0bc07: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0bc0e: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0bc15: 4d 89 e9                     	movq	%r13, %r9
 2c0bc18: 52                           	pushq	%rdx
 2c0bc19: 4c 89 ff                     	movq	%r15, %rdi
 2c0bc1c: 48 89 da                     	movq	%rbx, %rdx
 2c0bc1f: e8 ac f3 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0bc24: 5f                           	popq	%rdi
 2c0bc25: 41 58                        	popq	%r8
 2c0bc27: 4c 89 ff                     	movq	%r15, %rdi
 2c0bc2a: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0bc30: e8 7b 1c 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0bc35: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0bc3c: e8 ff 7d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bc41: 48 89 df                     	movq	%rbx, %rdi
 2c0bc44: e8 f7 7d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bc49: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0bc50: e8 eb 7d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bc55: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0bc5c: e8 df 7d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bc61: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0bc68: 84 c0                        	testb	%al, %al
 2c0bc6a: 0f 85 30 22 00 00            	jne	0x2c0dea0 <CAppManagerComm::Initialize(int, char**)+0x2b20>
 2c0bc70: 48 8d 85 c0 f5 ff ff         	leaq	-0xa40(%rbp), %rax
 2c0bc77: 48 89 c7                     	movq	%rax, %rdi
 2c0bc7a: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0bc81: e8 5a 0e 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0bc86: 4c 8d bd d0 fb ff ff         	leaq	-0x430(%rbp), %r15
 2c0bc8d: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0bc94: 4c 89 ff                     	movq	%r15, %rdi
 2c0bc97: e8 a4 ef 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0bc9c: 4c 89 ff                     	movq	%r15, %rdi
 2c0bc9f: e8 0c 00 84 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0bca4: 4c 8d 05 a5 a8 3b 03         	leaq	0x33ba8a5(%rip), %r8    # 0x5fc6550 <typeinfo name for CAppModeInfoImpl+0xa480>
 2c0bcab: 48 8d 15 b6 d0 3b 03         	leaq	0x33bd0b6(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0bcb2: 48 8d 35 2f 04 3b 03         	leaq	0x33b042f(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0bcb9: 41 89 c1                     	movl	%eax, %r9d
 2c0bcbc: b9 30 01 00 00               	movl	$0x130, %ecx            # imm = 0x130
 2c0bcc1: bf 03 00 00 00               	movl	$0x3, %edi
 2c0bcc6: 31 c0                        	xorl	%eax, %eax
 2c0bcc8: e8 e3 39 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0bccd: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0bcd1: e8 6a 7d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bcd6: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0bcda: e8 61 7d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bcdf: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0bce6: e8 c5 1b 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0bceb: 48 8d 85 f0 f5 ff ff         	leaq	-0xa10(%rbp), %rax
 2c0bcf2: 48 8d 35 97 1e 3b 03         	leaq	0x33b1e97(%rip), %rsi   # 0x5fbdb90 <typeinfo name for CAppModeInfoImpl+0x1ac0>
 2c0bcf9: 48 89 c7                     	movq	%rax, %rdi
 2c0bcfc: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0bd03: e8 28 36 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0bd08: 48 8d 95 e0 f5 ff ff         	leaq	-0xa20(%rbp), %rdx
 2c0bd0f: 48 8d 35 5a 1e 3b 03         	leaq	0x33b1e5a(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0bd16: 48 89 d7                     	movq	%rdx, %rdi
 2c0bd19: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0bd20: e8 0b 36 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0bd25: 4c 8d bd d0 f5 ff ff         	leaq	-0xa30(%rbp), %r15
 2c0bd2c: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0bd33: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0bd3a: 4c 89 ff                     	movq	%r15, %rdi
 2c0bd3d: e8 9e 0d 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0bd42: 48 8d 0d 40 22 3b 03         	leaq	0x33b2240(%rip), %rcx   # 0x5fbdf89 <typeinfo name for CAppModeInfoImpl+0x1eb9>
 2c0bd49: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0bd4d: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0bd54: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0bd5b: 4d 89 e9                     	movq	%r13, %r9
 2c0bd5e: 48 89 da                     	movq	%rbx, %rdx
 2c0bd61: 51                           	pushq	%rcx
 2c0bd62: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0bd69: 4c 89 ff                     	movq	%r15, %rdi
 2c0bd6c: e8 5f f2 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0bd71: 59                           	popq	%rcx
 2c0bd72: 5e                           	popq	%rsi
 2c0bd73: 4c 89 ff                     	movq	%r15, %rdi
 2c0bd76: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0bd7c: e8 2f 1b 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0bd81: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0bd88: e8 b3 7c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bd8d: 48 89 df                     	movq	%rbx, %rdi
 2c0bd90: e8 ab 7c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bd95: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0bd9c: e8 9f 7c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bda1: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0bda8: e8 93 7c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bdad: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0bdb4: 84 c0                        	testb	%al, %al
 2c0bdb6: 0f 85 b4 20 00 00            	jne	0x2c0de70 <CAppManagerComm::Initialize(int, char**)+0x2af0>
 2c0bdbc: 48 8d 85 00 f6 ff ff         	leaq	-0xa00(%rbp), %rax
 2c0bdc3: 48 89 c7                     	movq	%rax, %rdi
 2c0bdc6: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0bdcd: e8 0e 0d 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0bdd2: 4c 8d bd f0 fb ff ff         	leaq	-0x410(%rbp), %r15
 2c0bdd9: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0bde0: 4c 89 ff                     	movq	%r15, %rdi
 2c0bde3: e8 58 ee 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0bde8: 4c 89 ff                     	movq	%r15, %rdi
 2c0bdeb: e8 c0 fe 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0bdf0: 4c 8d 05 f1 a7 3b 03         	leaq	0x33ba7f1(%rip), %r8    # 0x5fc65e8 <typeinfo name for CAppModeInfoImpl+0xa518>
 2c0bdf7: 48 8d 15 6a cf 3b 03         	leaq	0x33bcf6a(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0bdfe: 48 8d 35 e3 02 3b 03         	leaq	0x33b02e3(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0be05: 41 89 c1                     	movl	%eax, %r9d
 2c0be08: b9 37 01 00 00               	movl	$0x137, %ecx            # imm = 0x137
 2c0be0d: bf 03 00 00 00               	movl	$0x3, %edi
 2c0be12: 31 c0                        	xorl	%eax, %eax
 2c0be14: e8 97 38 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0be19: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0be1d: e8 1e 7c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0be22: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0be26: e8 15 7c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0be2b: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0be32: e8 79 1a 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0be37: 48 8d 85 30 f6 ff ff         	leaq	-0x9d0(%rbp), %rax
 2c0be3e: 48 8d 35 57 21 3b 03         	leaq	0x33b2157(%rip), %rsi   # 0x5fbdf9c <typeinfo name for CAppModeInfoImpl+0x1ecc>
 2c0be45: 48 89 c7                     	movq	%rax, %rdi
 2c0be48: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0be4f: e8 dc 34 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0be54: 48 8d 8d 20 f6 ff ff         	leaq	-0x9e0(%rbp), %rcx
 2c0be5b: 48 8d 35 0e 1d 3b 03         	leaq	0x33b1d0e(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0be62: 48 89 cf                     	movq	%rcx, %rdi
 2c0be65: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0be6c: e8 bf 34 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0be71: 4c 8d bd 10 f6 ff ff         	leaq	-0x9f0(%rbp), %r15
 2c0be78: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0be7f: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0be86: 4c 89 ff                     	movq	%r15, %rdi
 2c0be89: e8 52 0c 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0be8e: 48 8d 15 13 21 3b 03         	leaq	0x33b2113(%rip), %rdx   # 0x5fbdfa8 <typeinfo name for CAppModeInfoImpl+0x1ed8>
 2c0be95: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0be99: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0bea0: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0bea7: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0beae: 4d 89 e9                     	movq	%r13, %r9
 2c0beb1: 52                           	pushq	%rdx
 2c0beb2: 4c 89 ff                     	movq	%r15, %rdi
 2c0beb5: 48 89 da                     	movq	%rbx, %rdx
 2c0beb8: e8 13 f1 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0bebd: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0bec3: 4c 89 ff                     	movq	%r15, %rdi
 2c0bec6: 58                           	popq	%rax
 2c0bec7: 5a                           	popq	%rdx
 2c0bec8: e8 e3 19 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0becd: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0bed4: e8 67 7b f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bed9: 48 89 df                     	movq	%rbx, %rdi
 2c0bedc: e8 5f 7b f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bee1: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0bee8: e8 53 7b f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0beed: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0bef4: e8 47 7b f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bef9: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0bf00: 84 c0                        	testb	%al, %al
 2c0bf02: 0f 85 38 1f 00 00            	jne	0x2c0de40 <CAppManagerComm::Initialize(int, char**)+0x2ac0>
 2c0bf08: 48 8d 85 40 f6 ff ff         	leaq	-0x9c0(%rbp), %rax
 2c0bf0f: 48 89 c7                     	movq	%rax, %rdi
 2c0bf12: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0bf19: e8 c2 0b 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0bf1e: 4c 8d bd 10 fc ff ff         	leaq	-0x3f0(%rbp), %r15
 2c0bf25: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0bf2c: 4c 89 ff                     	movq	%r15, %rdi
 2c0bf2f: e8 0c ed 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0bf34: 4c 89 ff                     	movq	%r15, %rdi
 2c0bf37: e8 74 fd 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0bf3c: 4c 8d 05 2d a7 3b 03         	leaq	0x33ba72d(%rip), %r8    # 0x5fc6670 <typeinfo name for CAppModeInfoImpl+0xa5a0>
 2c0bf43: 48 8d 15 1e ce 3b 03         	leaq	0x33bce1e(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0bf4a: 48 8d 35 97 01 3b 03         	leaq	0x33b0197(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0bf51: 41 89 c1                     	movl	%eax, %r9d
 2c0bf54: b9 3e 01 00 00               	movl	$0x13e, %ecx            # imm = 0x13E
 2c0bf59: bf 03 00 00 00               	movl	$0x3, %edi
 2c0bf5e: 31 c0                        	xorl	%eax, %eax
 2c0bf60: e8 4b 37 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0bf65: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0bf69: e8 d2 7a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bf6e: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0bf72: e8 c9 7a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0bf77: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0bf7e: e8 2d 19 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0bf83: 48 8d 85 70 f6 ff ff         	leaq	-0x990(%rbp), %rax
 2c0bf8a: 48 8d 35 77 19 3b 03         	leaq	0x33b1977(%rip), %rsi   # 0x5fbd908 <typeinfo name for CAppModeInfoImpl+0x1838>
 2c0bf91: 48 89 c7                     	movq	%rax, %rdi
 2c0bf94: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0bf9b: e8 90 33 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0bfa0: 48 8d 95 60 f6 ff ff         	leaq	-0x9a0(%rbp), %rdx
 2c0bfa7: 48 8d 35 c2 69 3a 03         	leaq	0x33a69c2(%rip), %rsi   # 0x5fb2970 <CNaviCanComm::Initialize()::__func__+0x4f8>
 2c0bfae: 48 89 d7                     	movq	%rdx, %rdi
 2c0bfb1: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0bfb8: e8 73 33 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0bfbd: 4c 8d bd 50 f6 ff ff         	leaq	-0x9b0(%rbp), %r15
 2c0bfc4: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0bfcb: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0bfd2: 4c 89 ff                     	movq	%r15, %rdi
 2c0bfd5: e8 06 0b 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0bfda: 48 8d 0d 4f 19 3b 03         	leaq	0x33b194f(%rip), %rcx   # 0x5fbd930 <typeinfo name for CAppModeInfoImpl+0x1860>
 2c0bfe1: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0bfe5: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0bfec: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0bff3: 4d 89 e9                     	movq	%r13, %r9
 2c0bff6: 48 89 da                     	movq	%rbx, %rdx
 2c0bff9: 51                           	pushq	%rcx
 2c0bffa: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c001: 4c 89 ff                     	movq	%r15, %rdi
 2c0c004: e8 c7 ef 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c009: 41 5b                        	popq	%r11
 2c0c00b: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c011: 4c 89 ff                     	movq	%r15, %rdi
 2c0c014: 58                           	popq	%rax
 2c0c015: e8 96 18 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c01a: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0c021: e8 1a 7a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c026: 48 89 df                     	movq	%rbx, %rdi
 2c0c029: e8 12 7a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c02e: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c035: e8 06 7a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c03a: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c041: e8 fa 79 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c046: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0c04d: 84 c0                        	testb	%al, %al
 2c0c04f: 0f 85 bb 1d 00 00            	jne	0x2c0de10 <CAppManagerComm::Initialize(int, char**)+0x2a90>
 2c0c055: 48 8d 85 80 f6 ff ff         	leaq	-0x980(%rbp), %rax
 2c0c05c: 48 89 c7                     	movq	%rax, %rdi
 2c0c05f: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c066: e8 75 0a 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c06b: 4c 8d bd 30 fc ff ff         	leaq	-0x3d0(%rbp), %r15
 2c0c072: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c079: 4c 89 ff                     	movq	%r15, %rdi
 2c0c07c: e8 bf eb 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0c081: 4c 89 ff                     	movq	%r15, %rdi
 2c0c084: e8 27 fc 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0c089: 4c 8d 05 60 a6 3b 03         	leaq	0x33ba660(%rip), %r8    # 0x5fc66f0 <typeinfo name for CAppModeInfoImpl+0xa620>
 2c0c090: 48 8d 15 d1 cc 3b 03         	leaq	0x33bccd1(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0c097: 48 8d 35 4a 00 3b 03         	leaq	0x33b004a(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0c09e: 41 89 c1                     	movl	%eax, %r9d
 2c0c0a1: b9 45 01 00 00               	movl	$0x145, %ecx            # imm = 0x145
 2c0c0a6: bf 03 00 00 00               	movl	$0x3, %edi
 2c0c0ab: 31 c0                        	xorl	%eax, %eax
 2c0c0ad: e8 fe 35 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0c0b2: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0c0b6: e8 85 79 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c0bb: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0c0bf: e8 7c 79 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c0c4: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c0cb: e8 e0 17 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c0d0: 48 8d 85 a0 f6 ff ff         	leaq	-0x960(%rbp), %rax
 2c0c0d7: 48 8d 35 7a c7 3a 03         	leaq	0x33ac77a(%rip), %rsi   # 0x5fb8858 <typeinfo name for CAudioControlImpl+0x148>
 2c0c0de: 48 89 c7                     	movq	%rax, %rdi
 2c0c0e1: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c0e8: e8 43 32 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c0ed: 48 8d 8d b0 f6 ff ff         	leaq	-0x950(%rbp), %rcx
 2c0c0f4: 48 8d 35 68 1a 3b 03         	leaq	0x33b1a68(%rip), %rsi   # 0x5fbdb63 <typeinfo name for CAppModeInfoImpl+0x1a93>
 2c0c0fb: 48 89 cf                     	movq	%rcx, %rdi
 2c0c0fe: 48 89 8d f8 f3 ff ff         	movq	%rcx, -0xc08(%rbp)
 2c0c105: e8 26 32 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c10a: 4c 8d bd 90 f6 ff ff         	leaq	-0x970(%rbp), %r15
 2c0c111: 4c 89 ff                     	movq	%r15, %rdi
 2c0c114: e8 c7 09 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c119: bf 10 00 00 00               	movl	$0x10, %edi
 2c0c11e: e8 0d 1d 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c0c123: 48 8b 95 f8 f3 ff ff         	movq	-0xc08(%rbp), %rdx
 2c0c12a: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c131: 4d 89 e8                     	movq	%r13, %r8
 2c0c134: 4c 89 f9                     	movq	%r15, %rcx
 2c0c137: 48 89 c7                     	movq	%rax, %rdi
 2c0c13a: 48 89 85 f0 f3 ff ff         	movq	%rax, -0xc10(%rbp)
 2c0c141: e8 5a 0b 6b 00               	callq	0x32bcca0 <ComLgeAvnAppmanagerInfoInterface::ComLgeAvnAppmanagerInfoInterface(QString const&, QString const&, QDBusConnection const&, QObject*)>
 2c0c146: 4c 89 ff                     	movq	%r15, %rdi
 2c0c149: 4c 8d bd c0 f6 ff ff         	leaq	-0x940(%rbp), %r15
 2c0c150: e8 5b 17 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c155: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c15c: e8 df 78 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c161: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c168: e8 d3 78 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c16d: 48 8b b5 f0 f3 ff ff         	movq	-0xc10(%rbp), %rsi
 2c0c174: 4c 8d 05 e5 17 3b 03         	leaq	0x33b17e5(%rip), %r8    # 0x5fbd960 <typeinfo name for CAppModeInfoImpl+0x1890>
 2c0c17b: 48 8d 15 06 18 3b 03         	leaq	0x33b1806(%rip), %rdx   # 0x5fbd988 <typeinfo name for CAppModeInfoImpl+0x18b8>
 2c0c182: 45 31 c9                     	xorl	%r9d, %r9d
 2c0c185: 4c 89 e9                     	movq	%r13, %rcx
 2c0c188: 4c 89 ff                     	movq	%r15, %rdi
 2c0c18b: e8 a0 ef 83 fe               	callq	0x144b130 <_ZN7QObject7connectEPKS_PKcS1_S3_N2Qt14ConnectionTypeE@plt>
 2c0c190: 4c 89 ff                     	movq	%r15, %rdi
 2c0c193: e8 38 1c 84 fe               	callq	0x144ddd0 <_ZN11QMetaObject10ConnectionD1Ev@plt>
 2c0c198: 48 8d 85 f0 f6 ff ff         	leaq	-0x910(%rbp), %rax
 2c0c19f: 48 8d 35 19 1e 3b 03         	leaq	0x33b1e19(%rip), %rsi   # 0x5fbdfbf <typeinfo name for CAppModeInfoImpl+0x1eef>
 2c0c1a6: 48 89 c7                     	movq	%rax, %rdi
 2c0c1a9: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0c1b0: e8 7b 31 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c1b5: 48 8d 95 e0 f6 ff ff         	leaq	-0x920(%rbp), %rdx
 2c0c1bc: 48 8d 35 ad 19 3b 03         	leaq	0x33b19ad(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0c1c3: 48 89 d7                     	movq	%rdx, %rdi
 2c0c1c6: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0c1cd: e8 5e 31 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c1d2: 4c 8d bd d0 f6 ff ff         	leaq	-0x930(%rbp), %r15
 2c0c1d9: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0c1e0: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0c1e7: 4c 89 ff                     	movq	%r15, %rdi
 2c0c1ea: e8 f1 08 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c1ef: 48 8d 0d d4 1d 3b 03         	leaq	0x33b1dd4(%rip), %rcx   # 0x5fbdfca <typeinfo name for CAppModeInfoImpl+0x1efa>
 2c0c1f6: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0c1fa: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0c201: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0c208: 4d 89 e9                     	movq	%r13, %r9
 2c0c20b: 48 89 da                     	movq	%rbx, %rdx
 2c0c20e: 51                           	pushq	%rcx
 2c0c20f: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c216: 4c 89 ff                     	movq	%r15, %rdi
 2c0c219: e8 b2 ed 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c21e: 41 59                        	popq	%r9
 2c0c220: 41 5a                        	popq	%r10
 2c0c222: 4c 89 ff                     	movq	%r15, %rdi
 2c0c225: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c22b: e8 80 16 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c230: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0c237: e8 04 78 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c23c: 48 89 df                     	movq	%rbx, %rdi
 2c0c23f: e8 fc 77 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c244: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c24b: e8 f0 77 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c250: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c257: e8 e4 77 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c25c: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0c263: 84 c0                        	testb	%al, %al
 2c0c265: 0f 85 75 1b 00 00            	jne	0x2c0dde0 <CAppManagerComm::Initialize(int, char**)+0x2a60>
 2c0c26b: 48 8d 85 00 f7 ff ff         	leaq	-0x900(%rbp), %rax
 2c0c272: 48 89 c7                     	movq	%rax, %rdi
 2c0c275: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c27c: e8 5f 08 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c281: 4c 8d bd 50 fc ff ff         	leaq	-0x3b0(%rbp), %r15
 2c0c288: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c28f: 4c 89 ff                     	movq	%r15, %rdi
 2c0c292: e8 a9 e9 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0c297: 4c 89 ff                     	movq	%r15, %rdi
 2c0c29a: e8 11 fa 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0c29f: 4c 8d 05 32 a5 3b 03         	leaq	0x33ba532(%rip), %r8    # 0x5fc67d8 <typeinfo name for CAppModeInfoImpl+0xa708>
 2c0c2a6: 48 8d 15 bb ca 3b 03         	leaq	0x33bcabb(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0c2ad: 48 8d 35 34 fe 3a 03         	leaq	0x33afe34(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0c2b4: 41 89 c1                     	movl	%eax, %r9d
 2c0c2b7: b9 59 01 00 00               	movl	$0x159, %ecx            # imm = 0x159
 2c0c2bc: bf 03 00 00 00               	movl	$0x3, %edi
 2c0c2c1: 31 c0                        	xorl	%eax, %eax
 2c0c2c3: e8 e8 33 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0c2c8: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0c2cc: e8 6f 77 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c2d1: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0c2d5: e8 66 77 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c2da: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c2e1: e8 ca 15 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c2e6: 48 8d 85 30 f7 ff ff         	leaq	-0x8d0(%rbp), %rax
 2c0c2ed: 48 8d 35 bd 19 3b 03         	leaq	0x33b19bd(%rip), %rsi   # 0x5fbdcb1 <typeinfo name for CAppModeInfoImpl+0x1be1>
 2c0c2f4: 48 89 c7                     	movq	%rax, %rdi
 2c0c2f7: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0c2fe: e8 2d 30 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c303: 48 8d 8d 20 f7 ff ff         	leaq	-0x8e0(%rbp), %rcx
 2c0c30a: 48 8d 35 5f 18 3b 03         	leaq	0x33b185f(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0c311: 48 89 cf                     	movq	%rcx, %rdi
 2c0c314: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0c31b: e8 10 30 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c320: 4c 8d bd 10 f7 ff ff         	leaq	-0x8f0(%rbp), %r15
 2c0c327: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0c32e: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0c335: 4c 89 ff                     	movq	%r15, %rdi
 2c0c338: e8 a3 07 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c33d: 48 8d 15 97 1c 3b 03         	leaq	0x33b1c97(%rip), %rdx   # 0x5fbdfdb <typeinfo name for CAppModeInfoImpl+0x1f0b>
 2c0c344: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0c348: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0c34f: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c356: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0c35d: 4d 89 e9                     	movq	%r13, %r9
 2c0c360: 52                           	pushq	%rdx
 2c0c361: 4c 89 ff                     	movq	%r15, %rdi
 2c0c364: 48 89 da                     	movq	%rbx, %rdx
 2c0c367: e8 64 ec 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c36c: 5f                           	popq	%rdi
 2c0c36d: 41 58                        	popq	%r8
 2c0c36f: 4c 89 ff                     	movq	%r15, %rdi
 2c0c372: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c378: e8 33 15 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c37d: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0c384: e8 b7 76 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c389: 48 89 df                     	movq	%rbx, %rdi
 2c0c38c: e8 af 76 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c391: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c398: e8 a3 76 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c39d: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c3a4: e8 97 76 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c3a9: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0c3b0: 84 c0                        	testb	%al, %al
 2c0c3b2: 0f 85 f8 19 00 00            	jne	0x2c0ddb0 <CAppManagerComm::Initialize(int, char**)+0x2a30>
 2c0c3b8: 48 8d 85 40 f7 ff ff         	leaq	-0x8c0(%rbp), %rax
 2c0c3bf: 48 89 c7                     	movq	%rax, %rdi
 2c0c3c2: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c3c9: e8 12 07 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c3ce: 4c 8d bd 70 fc ff ff         	leaq	-0x390(%rbp), %r15
 2c0c3d5: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c3dc: 4c 89 ff                     	movq	%r15, %rdi
 2c0c3df: e8 5c e8 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0c3e4: 4c 89 ff                     	movq	%r15, %rdi
 2c0c3e7: e8 c4 f8 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0c3ec: 4c 8d 05 5d a4 3b 03         	leaq	0x33ba45d(%rip), %r8    # 0x5fc6850 <typeinfo name for CAppModeInfoImpl+0xa780>
 2c0c3f3: 48 8d 15 6e c9 3b 03         	leaq	0x33bc96e(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0c3fa: 48 8d 35 e7 fc 3a 03         	leaq	0x33afce7(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0c401: 41 89 c1                     	movl	%eax, %r9d
 2c0c404: b9 60 01 00 00               	movl	$0x160, %ecx            # imm = 0x160
 2c0c409: bf 03 00 00 00               	movl	$0x3, %edi
 2c0c40e: 31 c0                        	xorl	%eax, %eax
 2c0c410: e8 9b 32 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0c415: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0c419: e8 22 76 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c41e: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0c422: e8 19 76 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c427: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c42e: e8 7d 14 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c433: 48 8d 85 70 f7 ff ff         	leaq	-0x890(%rbp), %rax
 2c0c43a: 48 8d 35 70 18 3b 03         	leaq	0x33b1870(%rip), %rsi   # 0x5fbdcb1 <typeinfo name for CAppModeInfoImpl+0x1be1>
 2c0c441: 48 89 c7                     	movq	%rax, %rdi
 2c0c444: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0c44b: e8 e0 2e f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c450: 48 8d 95 60 f7 ff ff         	leaq	-0x8a0(%rbp), %rdx
 2c0c457: 48 8d 35 12 17 3b 03         	leaq	0x33b1712(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0c45e: 48 89 d7                     	movq	%rdx, %rdi
 2c0c461: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0c468: e8 c3 2e f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c46d: 4c 8d bd 50 f7 ff ff         	leaq	-0x8b0(%rbp), %r15
 2c0c474: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0c47b: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0c482: 4c 89 ff                     	movq	%r15, %rdi
 2c0c485: e8 56 06 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c48a: 48 8d 0d 5b 1b 3b 03         	leaq	0x33b1b5b(%rip), %rcx   # 0x5fbdfec <typeinfo name for CAppModeInfoImpl+0x1f1c>
 2c0c491: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0c495: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0c49c: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0c4a3: 4d 89 e9                     	movq	%r13, %r9
 2c0c4a6: 48 89 da                     	movq	%rbx, %rdx
 2c0c4a9: 51                           	pushq	%rcx
 2c0c4aa: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c4b1: 4c 89 ff                     	movq	%r15, %rdi
 2c0c4b4: e8 17 eb 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c4b9: 59                           	popq	%rcx
 2c0c4ba: 5e                           	popq	%rsi
 2c0c4bb: 4c 89 ff                     	movq	%r15, %rdi
 2c0c4be: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c4c4: e8 e7 13 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c4c9: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0c4d0: e8 6b 75 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c4d5: 48 89 df                     	movq	%rbx, %rdi
 2c0c4d8: e8 63 75 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c4dd: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c4e4: e8 57 75 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c4e9: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c4f0: e8 4b 75 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c4f5: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0c4fc: 84 c0                        	testb	%al, %al
 2c0c4fe: 0f 85 7c 18 00 00            	jne	0x2c0dd80 <CAppManagerComm::Initialize(int, char**)+0x2a00>
 2c0c504: 48 8d 85 80 f7 ff ff         	leaq	-0x880(%rbp), %rax
 2c0c50b: 48 89 c7                     	movq	%rax, %rdi
 2c0c50e: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c515: e8 c6 05 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c51a: 4c 8d bd 90 fc ff ff         	leaq	-0x370(%rbp), %r15
 2c0c521: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c528: 4c 89 ff                     	movq	%r15, %rdi
 2c0c52b: e8 10 e7 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0c530: 4c 89 ff                     	movq	%r15, %rdi
 2c0c533: e8 78 f7 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0c538: 4c 8d 05 89 a3 3b 03         	leaq	0x33ba389(%rip), %r8    # 0x5fc68c8 <typeinfo name for CAppModeInfoImpl+0xa7f8>
 2c0c53f: 48 8d 15 22 c8 3b 03         	leaq	0x33bc822(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0c546: 48 8d 35 9b fb 3a 03         	leaq	0x33afb9b(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0c54d: 41 89 c1                     	movl	%eax, %r9d
 2c0c550: b9 67 01 00 00               	movl	$0x167, %ecx            # imm = 0x167
 2c0c555: bf 03 00 00 00               	movl	$0x3, %edi
 2c0c55a: 31 c0                        	xorl	%eax, %eax
 2c0c55c: e8 4f 31 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0c561: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0c565: e8 d6 74 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c56a: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0c56e: e8 cd 74 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c573: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c57a: e8 31 13 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c57f: 48 8d 85 b0 f7 ff ff         	leaq	-0x850(%rbp), %rax
 2c0c586: 48 8d 35 75 1a 3b 03         	leaq	0x33b1a75(%rip), %rsi   # 0x5fbe002 <typeinfo name for CAppModeInfoImpl+0x1f32>
 2c0c58d: 48 89 c7                     	movq	%rax, %rdi
 2c0c590: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0c597: e8 94 2d f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c59c: 48 8d 8d a0 f7 ff ff         	leaq	-0x860(%rbp), %rcx
 2c0c5a3: 48 8d 35 c6 15 3b 03         	leaq	0x33b15c6(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0c5aa: 48 89 cf                     	movq	%rcx, %rdi
 2c0c5ad: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0c5b4: e8 77 2d f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c5b9: 4c 8d bd 90 f7 ff ff         	leaq	-0x870(%rbp), %r15
 2c0c5c0: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0c5c7: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0c5ce: 4c 89 ff                     	movq	%r15, %rdi
 2c0c5d1: e8 0a 05 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c5d6: 48 8d 15 d3 13 3b 03         	leaq	0x33b13d3(%rip), %rdx   # 0x5fbd9b0 <typeinfo name for CAppModeInfoImpl+0x18e0>
 2c0c5dd: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0c5e1: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0c5e8: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c5ef: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0c5f6: 4d 89 e9                     	movq	%r13, %r9
 2c0c5f9: 52                           	pushq	%rdx
 2c0c5fa: 4c 89 ff                     	movq	%r15, %rdi
 2c0c5fd: 48 89 da                     	movq	%rbx, %rdx
 2c0c600: e8 cb e9 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c605: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c60b: 4c 89 ff                     	movq	%r15, %rdi
 2c0c60e: 58                           	popq	%rax
 2c0c60f: 5a                           	popq	%rdx
 2c0c610: e8 9b 12 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c615: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0c61c: e8 1f 74 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c621: 48 89 df                     	movq	%rbx, %rdi
 2c0c624: e8 17 74 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c629: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c630: e8 0b 74 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c635: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c63c: e8 ff 73 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c641: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0c648: 84 c0                        	testb	%al, %al
 2c0c64a: 0f 85 00 17 00 00            	jne	0x2c0dd50 <CAppManagerComm::Initialize(int, char**)+0x29d0>
 2c0c650: 48 8d 85 c0 f7 ff ff         	leaq	-0x840(%rbp), %rax
 2c0c657: 48 89 c7                     	movq	%rax, %rdi
 2c0c65a: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c661: e8 7a 04 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c666: 4c 8d bd b0 fc ff ff         	leaq	-0x350(%rbp), %r15
 2c0c66d: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c674: 4c 89 ff                     	movq	%r15, %rdi
 2c0c677: e8 c4 e5 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0c67c: 4c 89 ff                     	movq	%r15, %rdi
 2c0c67f: e8 2c f6 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0c684: 4c 8d 05 bd a2 3b 03         	leaq	0x33ba2bd(%rip), %r8    # 0x5fc6948 <typeinfo name for CAppModeInfoImpl+0xa878>
 2c0c68b: 48 8d 15 d6 c6 3b 03         	leaq	0x33bc6d6(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0c692: 48 8d 35 4f fa 3a 03         	leaq	0x33afa4f(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0c699: 41 89 c1                     	movl	%eax, %r9d
 2c0c69c: b9 6e 01 00 00               	movl	$0x16e, %ecx            # imm = 0x16E
 2c0c6a1: bf 03 00 00 00               	movl	$0x3, %edi
 2c0c6a6: 31 c0                        	xorl	%eax, %eax
 2c0c6a8: e8 03 30 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0c6ad: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0c6b1: e8 8a 73 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c6b6: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0c6ba: e8 81 73 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c6bf: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c6c6: e8 e5 11 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c6cb: 48 8d 85 f0 f7 ff ff         	leaq	-0x810(%rbp), %rax
 2c0c6d2: 48 8d 35 ff 12 3b 03         	leaq	0x33b12ff(%rip), %rsi   # 0x5fbd9d8 <typeinfo name for CAppModeInfoImpl+0x1908>
 2c0c6d9: 48 89 c7                     	movq	%rax, %rdi
 2c0c6dc: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0c6e3: e8 48 2c f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c6e8: 48 8d 95 e0 f7 ff ff         	leaq	-0x820(%rbp), %rdx
 2c0c6ef: 48 8d 35 7a 14 3b 03         	leaq	0x33b147a(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0c6f6: 48 89 d7                     	movq	%rdx, %rdi
 2c0c6f9: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0c700: e8 2b 2c f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c705: 4c 8d bd d0 f7 ff ff         	leaq	-0x830(%rbp), %r15
 2c0c70c: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0c713: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0c71a: 4c 89 ff                     	movq	%r15, %rdi
 2c0c71d: e8 be 03 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c722: 48 8d 0d cf 12 3b 03         	leaq	0x33b12cf(%rip), %rcx   # 0x5fbd9f8 <typeinfo name for CAppModeInfoImpl+0x1928>
 2c0c729: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0c72d: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0c734: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0c73b: 4d 89 e9                     	movq	%r13, %r9
 2c0c73e: 48 89 da                     	movq	%rbx, %rdx
 2c0c741: 51                           	pushq	%rcx
 2c0c742: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c749: 4c 89 ff                     	movq	%r15, %rdi
 2c0c74c: e8 7f e8 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c751: 41 5b                        	popq	%r11
 2c0c753: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c759: 4c 89 ff                     	movq	%r15, %rdi
 2c0c75c: 58                           	popq	%rax
 2c0c75d: e8 4e 11 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c762: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0c769: e8 d2 72 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c76e: 48 89 df                     	movq	%rbx, %rdi
 2c0c771: e8 ca 72 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c776: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c77d: e8 be 72 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c782: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c789: e8 b2 72 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c78e: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0c795: 84 c0                        	testb	%al, %al
 2c0c797: 0f 85 83 15 00 00            	jne	0x2c0dd20 <CAppManagerComm::Initialize(int, char**)+0x29a0>
 2c0c79d: 48 8d 85 00 f8 ff ff         	leaq	-0x800(%rbp), %rax
 2c0c7a4: 48 89 c7                     	movq	%rax, %rdi
 2c0c7a7: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c7ae: e8 2d 03 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c7b3: 4c 8d bd d0 fc ff ff         	leaq	-0x330(%rbp), %r15
 2c0c7ba: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c7c1: 4c 89 ff                     	movq	%r15, %rdi
 2c0c7c4: e8 77 e4 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0c7c9: 4c 89 ff                     	movq	%r15, %rdi
 2c0c7cc: e8 df f4 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0c7d1: 4c 8d 05 28 a2 3b 03         	leaq	0x33ba228(%rip), %r8    # 0x5fc6a00 <typeinfo name for CAppModeInfoImpl+0xa930>
 2c0c7d8: 48 8d 15 89 c5 3b 03         	leaq	0x33bc589(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0c7df: 48 8d 35 02 f9 3a 03         	leaq	0x33af902(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0c7e6: 41 89 c1                     	movl	%eax, %r9d
 2c0c7e9: b9 75 01 00 00               	movl	$0x175, %ecx            # imm = 0x175
 2c0c7ee: bf 03 00 00 00               	movl	$0x3, %edi
 2c0c7f3: 31 c0                        	xorl	%eax, %eax
 2c0c7f5: e8 b6 2e c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0c7fa: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0c7fe: e8 3d 72 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c803: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0c807: e8 34 72 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c80c: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c813: e8 98 10 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c818: 48 8d 85 30 f8 ff ff         	leaq	-0x7d0(%rbp), %rax
 2c0c81f: 48 8d 35 f7 17 3b 03         	leaq	0x33b17f7(%rip), %rsi   # 0x5fbe01d <typeinfo name for CAppModeInfoImpl+0x1f4d>
 2c0c826: 48 89 c7                     	movq	%rax, %rdi
 2c0c829: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0c830: e8 fb 2a f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c835: 48 8d 8d 20 f8 ff ff         	leaq	-0x7e0(%rbp), %rcx
 2c0c83c: 48 8d 35 2d 13 3b 03         	leaq	0x33b132d(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0c843: 48 89 cf                     	movq	%rcx, %rdi
 2c0c846: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0c84d: e8 de 2a f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c852: 4c 8d bd 10 f8 ff ff         	leaq	-0x7f0(%rbp), %r15
 2c0c859: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0c860: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0c867: 4c 89 ff                     	movq	%r15, %rdi
 2c0c86a: e8 71 02 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c86f: 48 8d 15 b5 17 3b 03         	leaq	0x33b17b5(%rip), %rdx   # 0x5fbe02b <typeinfo name for CAppModeInfoImpl+0x1f5b>
 2c0c876: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0c87a: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0c881: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c888: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0c88f: 4d 89 e9                     	movq	%r13, %r9
 2c0c892: 52                           	pushq	%rdx
 2c0c893: 4c 89 ff                     	movq	%r15, %rdi
 2c0c896: 48 89 da                     	movq	%rbx, %rdx
 2c0c899: e8 32 e7 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c89e: 41 59                        	popq	%r9
 2c0c8a0: 41 5a                        	popq	%r10
 2c0c8a2: 4c 89 ff                     	movq	%r15, %rdi
 2c0c8a5: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c8ab: e8 00 10 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c8b0: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0c8b7: e8 84 71 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c8bc: 48 89 df                     	movq	%rbx, %rdi
 2c0c8bf: e8 7c 71 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c8c4: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c8cb: e8 70 71 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c8d0: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0c8d7: e8 64 71 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c8dc: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0c8e3: 84 c0                        	testb	%al, %al
 2c0c8e5: 0f 85 05 14 00 00            	jne	0x2c0dcf0 <CAppManagerComm::Initialize(int, char**)+0x2970>
 2c0c8eb: 48 8d 85 40 f8 ff ff         	leaq	-0x7c0(%rbp), %rax
 2c0c8f2: 48 89 c7                     	movq	%rax, %rdi
 2c0c8f5: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0c8fc: e8 df 01 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c901: 4c 8d bd f0 fc ff ff         	leaq	-0x310(%rbp), %r15
 2c0c908: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0c90f: 4c 89 ff                     	movq	%r15, %rdi
 2c0c912: e8 29 e3 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0c917: 4c 89 ff                     	movq	%r15, %rdi
 2c0c91a: e8 91 f3 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0c91f: 4c 8d 05 da a0 3b 03         	leaq	0x33ba0da(%rip), %r8    # 0x5fc6a00 <typeinfo name for CAppModeInfoImpl+0xa930>
 2c0c926: 48 8d 15 3b c4 3b 03         	leaq	0x33bc43b(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0c92d: 48 8d 35 b4 f7 3a 03         	leaq	0x33af7b4(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0c934: 41 89 c1                     	movl	%eax, %r9d
 2c0c937: b9 7c 01 00 00               	movl	$0x17c, %ecx            # imm = 0x17C
 2c0c93c: bf 03 00 00 00               	movl	$0x3, %edi
 2c0c941: 31 c0                        	xorl	%eax, %eax
 2c0c943: e8 68 2d c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0c948: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0c94c: e8 ef 70 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c951: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0c955: e8 e6 70 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0c95a: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0c961: e8 4a 0f 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c966: 48 8d 85 70 f8 ff ff         	leaq	-0x790(%rbp), %rax
 2c0c96d: 48 8d 35 cb 16 3b 03         	leaq	0x33b16cb(%rip), %rsi   # 0x5fbe03f <typeinfo name for CAppModeInfoImpl+0x1f6f>
 2c0c974: 48 89 c7                     	movq	%rax, %rdi
 2c0c977: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0c97e: e8 ad 29 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c983: 48 8d 95 60 f8 ff ff         	leaq	-0x7a0(%rbp), %rdx
 2c0c98a: 48 8d 35 df 11 3b 03         	leaq	0x33b11df(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0c991: 48 89 d7                     	movq	%rdx, %rdi
 2c0c994: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0c99b: e8 90 29 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0c9a0: 4c 8d bd 50 f8 ff ff         	leaq	-0x7b0(%rbp), %r15
 2c0c9a7: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0c9ae: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0c9b5: 4c 89 ff                     	movq	%r15, %rdi
 2c0c9b8: e8 23 01 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0c9bd: 48 8d 0d 5c 10 3b 03         	leaq	0x33b105c(%rip), %rcx   # 0x5fbda20 <typeinfo name for CAppModeInfoImpl+0x1950>
 2c0c9c4: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0c9c8: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0c9cf: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0c9d6: 4d 89 e9                     	movq	%r13, %r9
 2c0c9d9: 48 89 da                     	movq	%rbx, %rdx
 2c0c9dc: 51                           	pushq	%rcx
 2c0c9dd: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0c9e4: 4c 89 ff                     	movq	%r15, %rdi
 2c0c9e7: e8 e4 e5 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0c9ec: 5f                           	popq	%rdi
 2c0c9ed: 41 58                        	popq	%r8
 2c0c9ef: 4c 89 ff                     	movq	%r15, %rdi
 2c0c9f2: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0c9f8: e8 b3 0e 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0c9fd: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0ca04: e8 37 70 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ca09: 48 89 df                     	movq	%rbx, %rdi
 2c0ca0c: e8 2f 70 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ca11: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0ca18: e8 23 70 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ca1d: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0ca24: e8 17 70 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ca29: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0ca30: 84 c0                        	testb	%al, %al
 2c0ca32: 0f 85 88 12 00 00            	jne	0x2c0dcc0 <CAppManagerComm::Initialize(int, char**)+0x2940>
 2c0ca38: 48 8d 85 80 f8 ff ff         	leaq	-0x780(%rbp), %rax
 2c0ca3f: 48 89 c7                     	movq	%rax, %rdi
 2c0ca42: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0ca49: e8 92 00 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0ca4e: 4c 8d bd 10 fd ff ff         	leaq	-0x2f0(%rbp), %r15
 2c0ca55: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0ca5c: 4c 89 ff                     	movq	%r15, %rdi
 2c0ca5f: e8 dc e1 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0ca64: 4c 89 ff                     	movq	%r15, %rdi
 2c0ca67: e8 44 f2 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0ca6c: 4c 8d 05 5d a0 3b 03         	leaq	0x33ba05d(%rip), %r8    # 0x5fc6ad0 <typeinfo name for CAppModeInfoImpl+0xaa00>
 2c0ca73: 48 8d 15 ee c2 3b 03         	leaq	0x33bc2ee(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0ca7a: 48 8d 35 67 f6 3a 03         	leaq	0x33af667(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0ca81: 41 89 c1                     	movl	%eax, %r9d
 2c0ca84: b9 83 01 00 00               	movl	$0x183, %ecx            # imm = 0x183
 2c0ca89: bf 03 00 00 00               	movl	$0x3, %edi
 2c0ca8e: 31 c0                        	xorl	%eax, %eax
 2c0ca90: e8 1b 2c c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0ca95: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0ca99: e8 a2 6f f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ca9e: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0caa2: e8 99 6f f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0caa7: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0caae: e8 fd 0d 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cab3: 48 8d 85 b0 f8 ff ff         	leaq	-0x750(%rbp), %rax
 2c0caba: 48 8d 35 9b 15 3b 03         	leaq	0x33b159b(%rip), %rsi   # 0x5fbe05c <typeinfo name for CAppModeInfoImpl+0x1f8c>
 2c0cac1: 48 89 c7                     	movq	%rax, %rdi
 2c0cac4: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0cacb: e8 60 28 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0cad0: 48 8d 8d a0 f8 ff ff         	leaq	-0x760(%rbp), %rcx
 2c0cad7: 48 8d 35 92 10 3b 03         	leaq	0x33b1092(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0cade: 48 89 cf                     	movq	%rcx, %rdi
 2c0cae1: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0cae8: e8 43 28 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0caed: 4c 8d bd 90 f8 ff ff         	leaq	-0x770(%rbp), %r15
 2c0caf4: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0cafb: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0cb02: 4c 89 ff                     	movq	%r15, %rdi
 2c0cb05: e8 d6 ff 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0cb0a: 48 8d 15 37 0f 3b 03         	leaq	0x33b0f37(%rip), %rdx   # 0x5fbda48 <typeinfo name for CAppModeInfoImpl+0x1978>
 2c0cb11: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0cb15: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0cb1c: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0cb23: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0cb2a: 4d 89 e9                     	movq	%r13, %r9
 2c0cb2d: 52                           	pushq	%rdx
 2c0cb2e: 4c 89 ff                     	movq	%r15, %rdi
 2c0cb31: 48 89 da                     	movq	%rbx, %rdx
 2c0cb34: e8 97 e4 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0cb39: 59                           	popq	%rcx
 2c0cb3a: 5e                           	popq	%rsi
 2c0cb3b: 4c 89 ff                     	movq	%r15, %rdi
 2c0cb3e: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0cb44: e8 67 0d 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cb49: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0cb50: e8 eb 6e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cb55: 48 89 df                     	movq	%rbx, %rdi
 2c0cb58: e8 e3 6e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cb5d: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0cb64: e8 d7 6e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cb69: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0cb70: e8 cb 6e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cb75: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0cb7c: 84 c0                        	testb	%al, %al
 2c0cb7e: 0f 85 0c 11 00 00            	jne	0x2c0dc90 <CAppManagerComm::Initialize(int, char**)+0x2910>
 2c0cb84: 48 8d 85 c0 f8 ff ff         	leaq	-0x740(%rbp), %rax
 2c0cb8b: 48 89 c7                     	movq	%rax, %rdi
 2c0cb8e: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0cb95: e8 46 ff 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0cb9a: 4c 8d bd 30 fd ff ff         	leaq	-0x2d0(%rbp), %r15
 2c0cba1: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0cba8: 4c 89 ff                     	movq	%r15, %rdi
 2c0cbab: e8 90 e0 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0cbb0: 4c 89 ff                     	movq	%r15, %rdi
 2c0cbb3: e8 f8 f0 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0cbb8: 4c 8d 05 d9 9f 3b 03         	leaq	0x33b9fd9(%rip), %r8    # 0x5fc6b98 <typeinfo name for CAppModeInfoImpl+0xaac8>
 2c0cbbf: 48 8d 15 a2 c1 3b 03         	leaq	0x33bc1a2(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0cbc6: 48 8d 35 1b f5 3a 03         	leaq	0x33af51b(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0cbcd: 41 89 c1                     	movl	%eax, %r9d
 2c0cbd0: b9 89 01 00 00               	movl	$0x189, %ecx            # imm = 0x189
 2c0cbd5: bf 03 00 00 00               	movl	$0x3, %edi
 2c0cbda: 31 c0                        	xorl	%eax, %eax
 2c0cbdc: e8 cf 2a c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0cbe1: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0cbe5: e8 56 6e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cbea: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0cbee: e8 4d 6e f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cbf3: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0cbfa: e8 b1 0c 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cbff: 48 8d 85 f0 f8 ff ff         	leaq	-0x710(%rbp), %rax
 2c0cc06: 48 8d 35 6b 14 3b 03         	leaq	0x33b146b(%rip), %rsi   # 0x5fbe078 <typeinfo name for CAppModeInfoImpl+0x1fa8>
 2c0cc0d: 48 89 c7                     	movq	%rax, %rdi
 2c0cc10: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0cc17: e8 14 27 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0cc1c: 48 8d 95 e0 f8 ff ff         	leaq	-0x720(%rbp), %rdx
 2c0cc23: 48 8d 35 46 0f 3b 03         	leaq	0x33b0f46(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0cc2a: 48 89 d7                     	movq	%rdx, %rdi
 2c0cc2d: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0cc34: e8 f7 26 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0cc39: 4c 8d bd d0 f8 ff ff         	leaq	-0x730(%rbp), %r15
 2c0cc40: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0cc47: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0cc4e: 4c 89 ff                     	movq	%r15, %rdi
 2c0cc51: e8 8a fe 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0cc56: 48 8d 0d 13 0e 3b 03         	leaq	0x33b0e13(%rip), %rcx   # 0x5fbda70 <typeinfo name for CAppModeInfoImpl+0x19a0>
 2c0cc5d: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0cc61: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0cc68: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0cc6f: 4d 89 e9                     	movq	%r13, %r9
 2c0cc72: 48 89 da                     	movq	%rbx, %rdx
 2c0cc75: 51                           	pushq	%rcx
 2c0cc76: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0cc7d: 4c 89 ff                     	movq	%r15, %rdi
 2c0cc80: e8 4b e3 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0cc85: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0cc8b: 4c 89 ff                     	movq	%r15, %rdi
 2c0cc8e: 58                           	popq	%rax
 2c0cc8f: 5a                           	popq	%rdx
 2c0cc90: e8 1b 0c 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cc95: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0cc9c: e8 9f 6d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cca1: 48 89 df                     	movq	%rbx, %rdi
 2c0cca4: e8 97 6d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cca9: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0ccb0: e8 8b 6d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ccb5: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0ccbc: e8 7f 6d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ccc1: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0ccc8: 84 c0                        	testb	%al, %al
 2c0ccca: 0f 85 90 0f 00 00            	jne	0x2c0dc60 <CAppManagerComm::Initialize(int, char**)+0x28e0>
 2c0ccd0: 48 8d 85 00 f9 ff ff         	leaq	-0x700(%rbp), %rax
 2c0ccd7: 48 89 c7                     	movq	%rax, %rdi
 2c0ccda: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0cce1: e8 fa fd 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0cce6: 4c 8d bd 50 fd ff ff         	leaq	-0x2b0(%rbp), %r15
 2c0cced: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0ccf4: 4c 89 ff                     	movq	%r15, %rdi
 2c0ccf7: e8 44 df 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0ccfc: 4c 89 ff                     	movq	%r15, %rdi
 2c0ccff: e8 ac ef 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0cd04: 4c 8d 05 4d 9f 3b 03         	leaq	0x33b9f4d(%rip), %r8    # 0x5fc6c58 <typeinfo name for CAppModeInfoImpl+0xab88>
 2c0cd0b: 48 8d 15 56 c0 3b 03         	leaq	0x33bc056(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0cd12: 48 8d 35 cf f3 3a 03         	leaq	0x33af3cf(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0cd19: 41 89 c1                     	movl	%eax, %r9d
 2c0cd1c: b9 90 01 00 00               	movl	$0x190, %ecx            # imm = 0x190
 2c0cd21: bf 03 00 00 00               	movl	$0x3, %edi
 2c0cd26: 31 c0                        	xorl	%eax, %eax
 2c0cd28: e8 83 29 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0cd2d: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0cd31: e8 0a 6d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cd36: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0cd3a: e8 01 6d f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cd3f: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0cd46: e8 65 0b 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cd4b: 48 8d 85 30 f9 ff ff         	leaq	-0x6d0(%rbp), %rax
 2c0cd52: 48 8d 35 39 13 3b 03         	leaq	0x33b1339(%rip), %rsi   # 0x5fbe092 <typeinfo name for CAppModeInfoImpl+0x1fc2>
 2c0cd59: 48 89 c7                     	movq	%rax, %rdi
 2c0cd5c: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0cd63: e8 c8 25 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0cd68: 48 8d 8d 20 f9 ff ff         	leaq	-0x6e0(%rbp), %rcx
 2c0cd6f: 48 8d 35 fa 0d 3b 03         	leaq	0x33b0dfa(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0cd76: 48 89 cf                     	movq	%rcx, %rdi
 2c0cd79: 48 89 8d 00 f4 ff ff         	movq	%rcx, -0xc00(%rbp)
 2c0cd80: e8 ab 25 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0cd85: 4c 8d bd 10 f9 ff ff         	leaq	-0x6f0(%rbp), %r15
 2c0cd8c: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0cd93: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0cd9a: 4c 89 ff                     	movq	%r15, %rdi
 2c0cd9d: e8 3e fd 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0cda2: 48 8d 15 e7 0c 3b 03         	leaq	0x33b0ce7(%rip), %rdx   # 0x5fbda90 <typeinfo name for CAppModeInfoImpl+0x19c0>
 2c0cda9: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0cdad: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0cdb4: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0cdbb: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0cdc2: 4d 89 e9                     	movq	%r13, %r9
 2c0cdc5: 52                           	pushq	%rdx
 2c0cdc6: 4c 89 ff                     	movq	%r15, %rdi
 2c0cdc9: 48 89 da                     	movq	%rbx, %rdx
 2c0cdcc: e8 ff e1 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0cdd1: 41 5b                        	popq	%r11
 2c0cdd3: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0cdd9: 4c 89 ff                     	movq	%r15, %rdi
 2c0cddc: 58                           	popq	%rax
 2c0cddd: e8 ce 0a 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cde2: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0cde9: e8 52 6c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cdee: 48 89 df                     	movq	%rbx, %rdi
 2c0cdf1: e8 4a 6c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cdf6: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0cdfd: e8 3e 6c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ce02: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0ce09: e8 32 6c f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ce0e: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0ce15: 84 c0                        	testb	%al, %al
 2c0ce17: 0f 85 13 0e 00 00            	jne	0x2c0dc30 <CAppManagerComm::Initialize(int, char**)+0x28b0>
 2c0ce1d: 48 8d 85 40 f9 ff ff         	leaq	-0x6c0(%rbp), %rax
 2c0ce24: 48 89 c7                     	movq	%rax, %rdi
 2c0ce27: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0ce2e: e8 ad fc 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0ce33: 4c 8d bd 70 fd ff ff         	leaq	-0x290(%rbp), %r15
 2c0ce3a: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0ce41: 4c 89 ff                     	movq	%r15, %rdi
 2c0ce44: e8 f7 dd 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0ce49: 4c 89 ff                     	movq	%r15, %rdi
 2c0ce4c: e8 5f ee 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0ce51: 4c 8d 05 b8 9e 3b 03         	leaq	0x33b9eb8(%rip), %r8    # 0x5fc6d10 <typeinfo name for CAppModeInfoImpl+0xac40>
 2c0ce58: 48 8d 15 09 bf 3b 03         	leaq	0x33bbf09(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0ce5f: 48 8d 35 82 f2 3a 03         	leaq	0x33af282(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0ce66: 41 89 c1                     	movl	%eax, %r9d
 2c0ce69: b9 96 01 00 00               	movl	$0x196, %ecx            # imm = 0x196
 2c0ce6e: bf 03 00 00 00               	movl	$0x3, %edi
 2c0ce73: 31 c0                        	xorl	%eax, %eax
 2c0ce75: e8 36 28 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0ce7a: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0ce7e: e8 bd 6b f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ce83: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0ce87: e8 b4 6b f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0ce8c: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0ce93: e8 18 0a 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0ce98: 48 8d 85 70 f9 ff ff         	leaq	-0x690(%rbp), %rax
 2c0ce9f: 48 8d 35 05 12 3b 03         	leaq	0x33b1205(%rip), %rsi   # 0x5fbe0ab <typeinfo name for CAppModeInfoImpl+0x1fdb>
 2c0cea6: 48 89 c7                     	movq	%rax, %rdi
 2c0cea9: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0ceb0: e8 7b 24 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0ceb5: 48 8d 95 60 f9 ff ff         	leaq	-0x6a0(%rbp), %rdx
 2c0cebc: 48 8d 35 ad 0c 3b 03         	leaq	0x33b0cad(%rip), %rsi   # 0x5fbdb70 <typeinfo name for CAppModeInfoImpl+0x1aa0>
 2c0cec3: 48 89 d7                     	movq	%rdx, %rdi
 2c0cec6: 48 89 95 00 f4 ff ff         	movq	%rdx, -0xc00(%rbp)
 2c0cecd: e8 5e 24 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c0ced2: 4c 8d bd 50 f9 ff ff         	leaq	-0x6b0(%rbp), %r15
 2c0ced9: 4c 89 a5 70 ff ff ff         	movq	%r12, -0x90(%rbp)
 2c0cee0: 4c 89 a5 10 ff ff ff         	movq	%r12, -0xf0(%rbp)
 2c0cee7: 4c 89 ff                     	movq	%r15, %rdi
 2c0ceea: e8 f1 fb 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0ceef: 48 8d 0d ca 11 3b 03         	leaq	0x33b11ca(%rip), %rcx   # 0x5fbe0c0 <typeinfo name for CAppModeInfoImpl+0x1ff0>
 2c0cef6: 48 83 ec 08                  	subq	$0x8, %rsp
 2c0cefa: 4c 8b 85 f8 f3 ff ff         	movq	-0xc08(%rbp), %r8
 2c0cf01: 48 8b b5 08 f4 ff ff         	movq	-0xbf8(%rbp), %rsi
 2c0cf08: 4d 89 e9                     	movq	%r13, %r9
 2c0cf0b: 48 89 da                     	movq	%rbx, %rdx
 2c0cf0e: 51                           	pushq	%rcx
 2c0cf0f: 48 8b 8d 00 f4 ff ff         	movq	-0xc00(%rbp), %rcx
 2c0cf16: 4c 89 ff                     	movq	%r15, %rdi
 2c0cf19: e8 b2 e0 83 fe               	callq	0x144afd0 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>
 2c0cf1e: 41 59                        	popq	%r9
 2c0cf20: 41 5a                        	popq	%r10
 2c0cf22: 4c 89 ff                     	movq	%r15, %rdi
 2c0cf25: 88 85 f0 f3 ff ff            	movb	%al, -0xc10(%rbp)
 2c0cf2b: e8 80 09 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cf30: 48 8b bd 08 f4 ff ff         	movq	-0xbf8(%rbp), %rdi
 2c0cf37: e8 04 6b f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cf3c: 48 89 df                     	movq	%rbx, %rdi
 2c0cf3f: e8 fc 6a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cf44: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0cf4b: e8 f0 6a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cf50: 48 8b bd f8 f3 ff ff         	movq	-0xc08(%rbp), %rdi
 2c0cf57: e8 e4 6a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cf5c: 0f b6 85 f0 f3 ff ff         	movzbl	-0xc10(%rbp), %eax
 2c0cf63: 84 c0                        	testb	%al, %al
 2c0cf65: 0f 85 95 0c 00 00            	jne	0x2c0dc00 <CAppManagerComm::Initialize(int, char**)+0x2880>
 2c0cf6b: 48 8d 85 80 f9 ff ff         	leaq	-0x680(%rbp), %rax
 2c0cf72: 48 89 c7                     	movq	%rax, %rdi
 2c0cf75: 48 89 85 00 f4 ff ff         	movq	%rax, -0xc00(%rbp)
 2c0cf7c: e8 5f fb 83 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c0cf81: 4c 8d bd 90 fd ff ff         	leaq	-0x270(%rbp), %r15
 2c0cf88: 48 8b b5 00 f4 ff ff         	movq	-0xc00(%rbp), %rsi
 2c0cf8f: 4c 89 ff                     	movq	%r15, %rdi
 2c0cf92: e8 a9 dc 83 fe               	callq	0x144ac40 <_ZNK15QDBusConnection9lastErrorEv@plt>
 2c0cf97: 4c 89 ff                     	movq	%r15, %rdi
 2c0cf9a: e8 11 ed 83 fe               	callq	0x144bcb0 <_ZNK10QDBusError4typeEv@plt>
 2c0cf9f: 4c 8d 05 22 9e 3b 03         	leaq	0x33b9e22(%rip), %r8    # 0x5fc6dc8 <typeinfo name for CAppModeInfoImpl+0xacf8>
 2c0cfa6: 48 8d 15 bb bd 3b 03         	leaq	0x33bbdbb(%rip), %rdx   # 0x5fc8d68 <CAppManagerComm::Initialize(int, char**)::__func__>
 2c0cfad: 48 8d 35 34 f1 3a 03         	leaq	0x33af134(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c0cfb4: 41 89 c1                     	movl	%eax, %r9d
 2c0cfb7: b9 9d 01 00 00               	movl	$0x19d, %ecx            # imm = 0x19D
 2c0cfbc: bf 03 00 00 00               	movl	$0x3, %edi
 2c0cfc1: 31 c0                        	xorl	%eax, %eax
 2c0cfc3: e8 e8 26 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0cfc8: 49 8d 7f 10                  	leaq	0x10(%r15), %rdi
 2c0cfcc: e8 6f 6a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cfd1: 49 8d 7f 08                  	leaq	0x8(%r15), %rdi
 2c0cfd5: e8 66 6a f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0cfda: 48 8b bd 00 f4 ff ff         	movq	-0xc00(%rbp), %rdi
 2c0cfe1: e8 ca 08 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0cfe6: 48 8d 85 b0 f9 ff ff         	leaq	-0x650(%rbp), %rax
 2c0cfed: 48 8d 35 e7 10 3b 03         	leaq	0x33b10e7(%rip), %rsi   # 0x5fbe0db <typeinfo name for CAppModeInfoImpl+0x200b>
 2c0cff4: 48 89 c7                     	movq	%rax, %rdi
 2c0cff7: 48 89 85 f8 f3 ff ff         	movq	%rax, -0xc08(%rbp)
 2c0cffe: e8 2d 23 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
