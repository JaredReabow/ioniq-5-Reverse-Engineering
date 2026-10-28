
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

0000000002bf7db0 <CAppManagerComm::RequestRegistrationAllAppIDToAppManager()>:
 2bf7db0: 53                           	pushq	%rbx
 2bf7db1: 4c 8d 05 68 a0 3c 03         	leaq	0x33ca068(%rip), %r8    # 0x5fc1e20 <typeinfo name for CAppModeInfoImpl+0x5d50>
 2bf7db8: 48 8d 15 81 02 3d 03         	leaq	0x33d0281(%rip), %rdx   # 0x5fc8040 <CAppManagerComm::RequestRegistrationAllAppIDToAppManager()::__func__>
 2bf7dbf: 48 8d 35 22 43 3c 03         	leaq	0x33c4322(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf7dc6: 48 89 fb                     	movq	%rdi, %rbx
 2bf7dc9: b9 8d 19 00 00               	movl	$0x198d, %ecx           # imm = 0x198D
 2bf7dce: 48 83 ec 10                  	subq	$0x10, %rsp
 2bf7dd2: 44 8b 8f dc 01 00 00         	movl	0x1dc(%rdi), %r9d
 2bf7dd9: bf 02 00 00 00               	movl	$0x2, %edi
 2bf7dde: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 2bf7de7: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 2bf7dec: 31 c0                        	xorl	%eax, %eax
 2bf7dee: e8 bd 78 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf7df3: 83 bb dc 01 00 00 05         	cmpl	$0x5, 0x1dc(%rbx)
 2bf7dfa: 74 6c                        	je	0x2bf7e68 <CAppManagerComm::RequestRegistrationAllAppIDToAppManager()+0xb8>
 2bf7dfc: 48 89 df                     	movq	%rbx, %rdi
 2bf7dff: e8 4c d4 ff ff               	callq	0x2bf5250 <CAppManagerComm::SendToAppManagerRegistrationMapFront()>
 2bf7e04: 48 89 df                     	movq	%rbx, %rdi
 2bf7e07: e8 d4 d7 ff ff               	callq	0x2bf55e0 <CAppManagerComm::SendToAppManagerRegistrationMapRear()>
 2bf7e0c: 48 89 df                     	movq	%rbx, %rdi
 2bf7e0f: e8 ac e2 ff ff               	callq	0x2bf60c0 <CAppManagerComm::SendToAppManagerRegistrationMenuFront()>
 2bf7e14: 48 89 df                     	movq	%rbx, %rdi
 2bf7e17: e8 34 e6 ff ff               	callq	0x2bf6450 <CAppManagerComm::SendToAppManagerRegistrationMenuRear()>
 2bf7e1c: 48 89 df                     	movq	%rbx, %rdi
 2bf7e1f: e8 5c db ff ff               	callq	0x2bf5980 <CAppManagerComm::SendToAppManagerRegistrationSetupFront()>
 2bf7e24: 48 89 df                     	movq	%rbx, %rdi
 2bf7e27: e8 f4 de ff ff               	callq	0x2bf5d20 <CAppManagerComm::SendToAppManagerRegistrationSetupRear()>
 2bf7e2c: 48 89 df                     	movq	%rbx, %rdi
 2bf7e2f: e8 bc e9 ff ff               	callq	0x2bf67f0 <CAppManagerComm::SendToAppManagerRegistrationEngModeFront()>
 2bf7e34: 48 89 df                     	movq	%rbx, %rdi
 2bf7e37: e8 54 ed ff ff               	callq	0x2bf6b90 <CAppManagerComm::SendToAppManagerRegistrationEngModeRear()>
 2bf7e3c: 48 89 df                     	movq	%rbx, %rdi
 2bf7e3f: e8 ec f0 ff ff               	callq	0x2bf6f30 <CAppManagerComm::SendToAppManagerRegistrationTemporaryFront()>
 2bf7e44: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 2bf7e49: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 2bf7e52: 75 26                        	jne	0x2bf7e7a <CAppManagerComm::RequestRegistrationAllAppIDToAppManager()+0xca>
 2bf7e54: 48 83 c4 10                  	addq	$0x10, %rsp
 2bf7e58: 48 89 df                     	movq	%rbx, %rdi
 2bf7e5b: 5b                           	popq	%rbx
 2bf7e5c: e9 6f f4 ff ff               	jmp	0x2bf72d0 <CAppManagerComm::SendToAppManagerRegistrationTemporaryRear()>
 2bf7e61: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 2bf7e68: 48 89 df                     	movq	%rbx, %rdi
 2bf7e6b: e8 00 f8 ff ff               	callq	0x2bf7670 <CAppManagerComm::SendToAppManagerRegistrationQiblaFront()>
 2bf7e70: 48 89 df                     	movq	%rbx, %rdi
 2bf7e73: e8 98 fb ff ff               	callq	0x2bf7a10 <CAppManagerComm::SendToAppManagerRegistrationQiblaRear()>
 2bf7e78: eb 82                        	jmp	0x2bf7dfc <CAppManagerComm::RequestRegistrationAllAppIDToAppManager()+0x4c>
 2bf7e7a: e8 11 2d 85 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 2bf7e7f: 90                           	nop

0000000002bf7e80 <CAppManagerComm::request_register_all_app()>:
 2bf7e80: 53                           	pushq	%rbx
 2bf7e81: 4c 8d 05 20 a0 3c 03         	leaq	0x33ca020(%rip), %r8    # 0x5fc1ea8 <typeinfo name for CAppModeInfoImpl+0x5dd8>
 2bf7e88: 48 8d 15 01 01 3d 03         	leaq	0x33d0101(%rip), %rdx   # 0x5fc7f90 <CAppManagerComm::request_register_all_app()::__func__>
 2bf7e8f: 48 8d 35 52 42 3c 03         	leaq	0x33c4252(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf7e96: 48 89 fb                     	movq	%rdi, %rbx
 2bf7e99: b9 df 19 00 00               	movl	$0x19df, %ecx           # imm = 0x19DF
 2bf7e9e: 48 83 ec 10                  	subq	$0x10, %rsp
 2bf7ea2: bf 02 00 00 00               	movl	$0x2, %edi
 2bf7ea7: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 2bf7eb0: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 2bf7eb5: 31 c0                        	xorl	%eax, %eax
 2bf7eb7: e8 f4 77 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf7ebc: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 2bf7ec1: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 2bf7eca: 75 0d                        	jne	0x2bf7ed9 <CAppManagerComm::request_register_all_app()+0x59>
 2bf7ecc: 48 83 c4 10                  	addq	$0x10, %rsp
 2bf7ed0: 48 89 df                     	movq	%rbx, %rdi
 2bf7ed3: 5b                           	popq	%rbx
 2bf7ed4: e9 d7 fe ff ff               	jmp	0x2bf7db0 <CAppManagerComm::RequestRegistrationAllAppIDToAppManager()>
 2bf7ed9: e8 b2 2c 85 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 2bf7ede: 66 90                        	nop

0000000002bf7ee0 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)>:
 2bf7ee0: 41 57                        	pushq	%r15
 2bf7ee2: 41 56                        	pushq	%r14
 2bf7ee4: 4c 8d 05 25 a0 3c 03         	leaq	0x33ca025(%rip), %r8    # 0x5fc1f10 <typeinfo name for CAppModeInfoImpl+0x5e40>
 2bf7eeb: 41 55                        	pushq	%r13
 2bf7eed: 41 54                        	pushq	%r12
 2bf7eef: 48 8d 15 0a 0a 3d 03         	leaq	0x33d0a0a(%rip), %rdx   # 0x5fc8900 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::__func__>
 2bf7ef6: 55                           	pushq	%rbp
 2bf7ef7: 53                           	pushq	%rbx
 2bf7ef8: 49 89 f4                     	movq	%rsi, %r12
 2bf7efb: 48 8d 35 e6 41 3c 03         	leaq	0x33c41e6(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf7f02: b9 30 0b 00 00               	movl	$0xb30, %ecx            # imm = 0xB30
 2bf7f07: 49 89 fd                     	movq	%rdi, %r13
 2bf7f0a: 48 81 ec 98 01 00 00         	subq	$0x198, %rsp            # imm = 0x198
 2bf7f11: 44 8b 0d 9c 87 ab 04         	movl	0x4ab879c(%rip), %r9d   # 0x76b06b4 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::nCount>
 2bf7f18: bf 02 00 00 00               	movl	$0x2, %edi
 2bf7f1d: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 2bf7f26: 48 89 84 24 88 01 00 00      	movq	%rax, 0x188(%rsp)
 2bf7f2e: 31 c0                        	xorl	%eax, %eax
 2bf7f30: 48 8d 5c 24 20               	leaq	0x20(%rsp), %rbx
 2bf7f35: e8 76 77 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf7f3a: 48 89 df                     	movq	%rbx, %rdi
 2bf7f3d: e8 2e 37 85 fe               	callq	0x144b670 <_ZN21QDBusPendingReplyDataC2Ev@plt>
 2bf7f42: 49 8d 74 24 10               	leaq	0x10(%r12), %rsi
 2bf7f47: 48 89 df                     	movq	%rbx, %rdi
 2bf7f4a: e8 31 44 85 fe               	callq	0x144c380 <_ZN21QDBusPendingReplyData6assignERK16QDBusPendingCall@plt>
 2bf7f4f: 48 83 7c 24 20 00            	cmpq	$0x0, 0x20(%rsp)
 2bf7f55: 74 20                        	je	0x2bf7f77 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x97>
 2bf7f57: 48 8d 94 24 80 01 00 00      	leaq	0x180(%rsp), %rdx
 2bf7f5f: be 01 00 00 00               	movl	$0x1, %esi
 2bf7f64: 48 89 df                     	movq	%rbx, %rdi
 2bf7f67: c7 84 24 80 01 00 00 02 00 00 00     	movl	$0x2, 0x180(%rsp)
 2bf7f72: e8 49 57 85 fe               	callq	0x144d6c0 <_ZN21QDBusPendingReplyData12setMetaTypesEiPKi@plt>
 2bf7f77: 48 89 df                     	movq	%rbx, %rdi
 2bf7f7a: e8 11 56 85 fe               	callq	0x144d590 <_ZNK16QDBusPendingCall7isErrorEv@plt>
 2bf7f7f: 84 c0                        	testb	%al, %al
 2bf7f81: 0f 84 a9 00 00 00            	je	0x2bf8030 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x150>
 2bf7f87: 48 8d ac 24 60 01 00 00      	leaq	0x160(%rsp), %rbp
 2bf7f8f: 48 89 de                     	movq	%rbx, %rsi
 2bf7f92: 48 89 ef                     	movq	%rbp, %rdi
 2bf7f95: e8 e6 48 85 fe               	callq	0x144c880 <_ZNK16QDBusPendingCall5errorEv@plt>
 2bf7f9a: 4c 8d 6c 24 40               	leaq	0x40(%rsp), %r13
 2bf7f9f: 48 89 ee                     	movq	%rbp, %rsi
 2bf7fa2: 4c 89 ef                     	movq	%r13, %rdi
 2bf7fa5: e8 d6 65 85 fe               	callq	0x144e580 <_ZNK10QDBusError7messageEv@plt>
 2bf7faa: 4c 89 ef                     	movq	%r13, %rdi
 2bf7fad: e8 3e 66 85 fe               	callq	0x144e5f0 <_ZNK7QString5utf16Ev@plt>
 2bf7fb2: 4c 8d 05 bb 0d 3d 03         	leaq	0x33d0dbb(%rip), %r8    # 0x5fc8d74 <CAppManagerComm::Initialize(int, char**)::__func__+0xc>
 2bf7fb9: 48 8d 15 40 09 3d 03         	leaq	0x33d0940(%rip), %rdx   # 0x5fc8900 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::__func__>
 2bf7fc0: 48 8d 35 21 41 3c 03         	leaq	0x33c4121(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf7fc7: 49 89 c1                     	movq	%rax, %r9
 2bf7fca: b9 34 0b 00 00               	movl	$0xb34, %ecx            # imm = 0xB34
 2bf7fcf: bf 03 00 00 00               	movl	$0x3, %edi
 2bf7fd4: 31 c0                        	xorl	%eax, %eax
 2bf7fd6: e8 d5 76 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf7fdb: 4c 89 ef                     	movq	%r13, %rdi
 2bf7fde: e8 5d ba f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf7fe3: 48 8d 7d 10                  	leaq	0x10(%rbp), %rdi
 2bf7fe7: e8 54 ba f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf7fec: 48 8d 7d 08                  	leaq	0x8(%rbp), %rdi
 2bf7ff0: e8 4b ba f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf7ff5: 4c 89 e7                     	movq	%r12, %rdi
 2bf7ff8: e8 43 33 85 fe               	callq	0x144b340 <_ZN7QObject11deleteLaterEv@plt>
 2bf7ffd: 48 89 df                     	movq	%rbx, %rdi
 2bf8000: e8 1b 6d 85 fe               	callq	0x144ed20 <_ZN21QDBusPendingReplyDataD2Ev@plt>
 2bf8005: 48 8b 84 24 88 01 00 00      	movq	0x188(%rsp), %rax
 2bf800d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 2bf8016: 0f 85 2f 04 00 00            	jne	0x2bf844b <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x56b>
 2bf801c: 48 81 c4 98 01 00 00         	addq	$0x198, %rsp            # imm = 0x198
 2bf8023: 5b                           	popq	%rbx
 2bf8024: 5d                           	popq	%rbp
 2bf8025: 41 5c                        	popq	%r12
 2bf8027: 41 5d                        	popq	%r13
 2bf8029: 41 5e                        	popq	%r14
 2bf802b: 41 5f                        	popq	%r15
 2bf802d: c3                           	retq
 2bf802e: 66 90                        	nop
 2bf8030: 48 89 df                     	movq	%rbx, %rdi
 2bf8033: e8 a8 63 01 00               	callq	0x2c0e3e0 <QDBusPendingReply<int, void, void, void, void, void, void, void>::Select<0>::Type const QDBusPendingReply<int, void, void, void, void, void, void, void>::argumentAt<0>() const>
 2bf8038: 4c 8d 05 59 9f 3c 03         	leaq	0x33c9f59(%rip), %r8    # 0x5fc1f98 <typeinfo name for CAppModeInfoImpl+0x5ec8>
 2bf803f: 48 8d 15 ba 08 3d 03         	leaq	0x33d08ba(%rip), %rdx   # 0x5fc8900 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::__func__>
 2bf8046: 48 8d 35 9b 40 3c 03         	leaq	0x33c409b(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf804d: 89 c5                        	movl	%eax, %ebp
 2bf804f: 41 89 c1                     	movl	%eax, %r9d
 2bf8052: b9 37 0b 00 00               	movl	$0xb37, %ecx            # imm = 0xB37
 2bf8057: bf 02 00 00 00               	movl	$0x2, %edi
 2bf805c: 31 c0                        	xorl	%eax, %eax
 2bf805e: e8 4d 76 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf8063: 85 ed                        	testl	%ebp, %ebp
 2bf8065: 74 21                        	je	0x2bf8088 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x1a8>
 2bf8067: 83 3d 46 86 ab 04 03         	cmpl	$0x3, 0x4ab8646(%rip)   # 0x76b06b4 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::nCount>
 2bf806e: 7f 85                        	jg	0x2bf7ff5 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x115>
 2bf8070: 4c 89 ef                     	movq	%r13, %rdi
 2bf8073: e8 d8 d1 ff ff               	callq	0x2bf5250 <CAppManagerComm::SendToAppManagerRegistrationMapFront()>
 2bf8078: 83 05 35 86 ab 04 01         	addl	$0x1, 0x4ab8635(%rip)   # 0x76b06b4 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::nCount>
 2bf807f: e9 71 ff ff ff               	jmp	0x2bf7ff5 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x115>
 2bf8084: 0f 1f 40 00                  	nopl	(%rax)
 2bf8088: 4c 8d bc 24 c0 00 00 00      	leaq	0xc0(%rsp), %r15
 2bf8090: 48 8d 35 4f 5c 3c 03         	leaq	0x33c5c4f(%rip), %rsi   # 0x5fbdce6 <typeinfo name for CAppModeInfoImpl+0x1c16>
 2bf8097: 4c 89 ff                     	movq	%r15, %rdi
 2bf809a: e8 91 72 f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf809f: 48 8d 84 24 a0 00 00 00      	leaq	0xa0(%rsp), %rax
 2bf80a7: 48 8d 35 52 48 3c 03         	leaq	0x33c4852(%rip), %rsi   # 0x5fbc900 <typeinfo name for CAppModeInfoImpl+0x830>
 2bf80ae: 48 89 c7                     	movq	%rax, %rdi
 2bf80b1: 48 89 c5                     	movq	%rax, %rbp
 2bf80b4: 48 89 04 24                  	movq	%rax, (%rsp)
 2bf80b8: e8 73 72 f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf80bd: 4c 8d 74 24 60               	leaq	0x60(%rsp), %r14
 2bf80c2: 48 8d 35 1f 08 3b 03         	leaq	0x33b081f(%rip), %rsi   # 0x5fa88e8 <typeinfo name for NimoLanguageImpl+0x768>
 2bf80c9: 4c 89 f7                     	movq	%r14, %rdi
 2bf80cc: e8 5f 72 f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf80d1: 48 8d 44 24 30               	leaq	0x30(%rsp), %rax
 2bf80d6: 4c 89 f9                     	movq	%r15, %rcx
 2bf80d9: 48 89 ea                     	movq	%rbp, %rdx
 2bf80dc: 4c 89 f6                     	movq	%r14, %rsi
 2bf80df: 48 89 c7                     	movq	%rax, %rdi
 2bf80e2: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 2bf80e7: e8 74 68 85 fe               	callq	0x144e960 <_ZN12QDBusMessage12createSignalERK7QStringS2_S2_@plt>
 2bf80ec: 4c 89 f7                     	movq	%r14, %rdi
 2bf80ef: 4c 8d 6c 24 40               	leaq	0x40(%rsp), %r13
 2bf80f4: e8 47 b9 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf80f9: 48 89 ef                     	movq	%rbp, %rdi
 2bf80fc: 48 89 2c 24                  	movq	%rbp, (%rsp)
 2bf8100: e8 3b b9 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf8105: 4c 89 ff                     	movq	%r15, %rdi
 2bf8108: e8 33 b9 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf810d: 48 8b 0d 2c 58 ab 04         	movq	0x4ab582c(%rip), %rcx   # 0x76ad940 <_GLOBAL_OFFSET_TABLE_+0x46d8>
 2bf8114: be 16 00 00 00               	movl	$0x16, %esi
 2bf8119: 48 89 4c 24 40               	movq	%rcx, 0x40(%rsp)
 2bf811e: 48 8d 8c 24 20 01 00 00      	leaq	0x120(%rsp), %rcx
 2bf8126: 48 89 cf                     	movq	%rcx, %rdi
 2bf8129: 48 89 4c 24 10               	movq	%rcx, 0x10(%rsp)
 2bf812e: e8 2d 45 85 fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 2bf8133: 48 8d ac 24 10 01 00 00      	leaq	0x110(%rsp), %rbp
 2bf813b: be 1f 00 00 00               	movl	$0x1f, %esi
 2bf8140: 48 89 ef                     	movq	%rbp, %rdi
 2bf8143: e8 18 45 85 fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 2bf8148: 4c 8d 6c 24 40               	leaq	0x40(%rsp), %r13
 2bf814d: 48 89 ee                     	movq	%rbp, %rsi
 2bf8150: 4c 89 ef                     	movq	%r13, %rdi
 2bf8153: e8 98 b9 fc ff               	callq	0x2bc3af0 <QList<QVariant>::append(QVariant const&)>
 2bf8158: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 2bf815d: 4c 89 ef                     	movq	%r13, %rdi
 2bf8160: e8 8b b9 fc ff               	callq	0x2bc3af0 <QList<QVariant>::append(QVariant const&)>
 2bf8165: 48 89 ef                     	movq	%rbp, %rdi
 2bf8168: 48 8d ac 24 30 01 00 00      	leaq	0x130(%rsp), %rbp
 2bf8170: e8 4b 50 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf8175: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
 2bf817a: e8 41 50 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf817f: 4c 89 ee                     	movq	%r13, %rsi
 2bf8182: 48 89 ef                     	movq	%rbp, %rdi
 2bf8185: e8 86 46 85 fe               	callq	0x144c810 <_ZN8QVariantC1ERK5QListIS_E@plt>
 2bf818a: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
 2bf818f: 48 89 ee                     	movq	%rbp, %rsi
 2bf8192: e8 09 5f 85 fe               	callq	0x144e0a0 <_ZN12QDBusMessagelsERK8QVariant@plt>
 2bf8197: 48 89 ef                     	movq	%rbp, %rdi
 2bf819a: 48 8d 6c 24 50               	leaq	0x50(%rsp), %rbp
 2bf819f: e8 1c 50 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf81a4: 48 89 ef                     	movq	%rbp, %rdi
 2bf81a7: e8 34 49 85 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2bf81ac: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
 2bf81b1: 48 89 ef                     	movq	%rbp, %rdi
 2bf81b4: e8 57 40 85 fe               	callq	0x144c210 <_ZNK15QDBusConnection4sendERK12QDBusMessage@plt>
 2bf81b9: 48 89 ef                     	movq	%rbp, %rdi
 2bf81bc: 88 44 24 10                  	movb	%al, 0x10(%rsp)
 2bf81c0: e8 eb 56 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf81c5: 44 0f b6 4c 24 10            	movzbl	0x10(%rsp), %r9d
 2bf81cb: 4c 8d 05 36 95 3c 03         	leaq	0x33c9536(%rip), %r8    # 0x5fc1708 <typeinfo name for CAppModeInfoImpl+0x5638>
 2bf81d2: 48 8d 15 27 07 3d 03         	leaq	0x33d0727(%rip), %rdx   # 0x5fc8900 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::__func__>
 2bf81d9: 48 8d 35 08 3f 3c 03         	leaq	0x33c3f08(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf81e0: b9 45 0b 00 00               	movl	$0xb45, %ecx            # imm = 0xB45
 2bf81e5: bf 02 00 00 00               	movl	$0x2, %edi
 2bf81ea: 31 c0                        	xorl	%eax, %eax
 2bf81ec: e8 bf 74 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf81f1: 48 8d 8c 24 90 00 00 00      	leaq	0x90(%rsp), %rcx
 2bf81f9: 48 8d 35 08 5b 3c 03         	leaq	0x33c5b08(%rip), %rsi   # 0x5fbdd08 <typeinfo name for CAppModeInfoImpl+0x1c38>
 2bf8200: 48 89 cf                     	movq	%rcx, %rdi
 2bf8203: 48 89 4c 24 18               	movq	%rcx, 0x18(%rsp)
 2bf8208: e8 23 71 f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf820d: 48 8d 94 24 80 00 00 00      	leaq	0x80(%rsp), %rdx
 2bf8215: 48 8d 35 e4 46 3c 03         	leaq	0x33c46e4(%rip), %rsi   # 0x5fbc900 <typeinfo name for CAppModeInfoImpl+0x830>
 2bf821c: 48 89 d7                     	movq	%rdx, %rdi
 2bf821f: 48 89 54 24 10               	movq	%rdx, 0x10(%rsp)
 2bf8224: e8 07 71 f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf8229: 48 8d 6c 24 70               	leaq	0x70(%rsp), %rbp
 2bf822e: 48 8d 35 b3 06 3b 03         	leaq	0x33b06b3(%rip), %rsi   # 0x5fa88e8 <typeinfo name for NimoLanguageImpl+0x768>
 2bf8235: 48 89 ef                     	movq	%rbp, %rdi
 2bf8238: e8 f3 70 f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf823d: 48 8b 4c 24 18               	movq	0x18(%rsp), %rcx
 2bf8242: 48 8b 54 24 10               	movq	0x10(%rsp), %rdx
 2bf8247: 48 89 ee                     	movq	%rbp, %rsi
 2bf824a: 4c 89 f7                     	movq	%r14, %rdi
 2bf824d: e8 0e 67 85 fe               	callq	0x144e960 <_ZN12QDBusMessage12createSignalERK7QStringS2_S2_@plt>
 2bf8252: 48 89 ef                     	movq	%rbp, %rdi
 2bf8255: 48 8d ac 24 40 01 00 00      	leaq	0x140(%rsp), %rbp
 2bf825d: e8 de b7 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf8262: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
 2bf8267: e8 d4 b7 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf826c: 48 8b 7c 24 18               	movq	0x18(%rsp), %rdi
 2bf8271: e8 ca b7 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf8276: 48 8b 0d c3 56 ab 04         	movq	0x4ab56c3(%rip), %rcx   # 0x76ad940 <_GLOBAL_OFFSET_TABLE_+0x46d8>
 2bf827d: be 35 01 00 00               	movl	$0x135, %esi            # imm = 0x135
 2bf8282: 48 89 ef                     	movq	%rbp, %rdi
 2bf8285: 48 89 8c 24 a0 00 00 00      	movq	%rcx, 0xa0(%rsp)
 2bf828d: e8 ce 43 85 fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 2bf8292: 48 8b 3c 24                  	movq	(%rsp), %rdi
 2bf8296: 48 89 ee                     	movq	%rbp, %rsi
 2bf8299: e8 52 b8 fc ff               	callq	0x2bc3af0 <QList<QVariant>::append(QVariant const&)>
 2bf829e: 48 89 ef                     	movq	%rbp, %rdi
 2bf82a1: 48 8d ac 24 50 01 00 00      	leaq	0x150(%rsp), %rbp
 2bf82a9: e8 12 4f 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf82ae: 48 8b 34 24                  	movq	(%rsp), %rsi
 2bf82b2: 48 89 ef                     	movq	%rbp, %rdi
 2bf82b5: e8 56 45 85 fe               	callq	0x144c810 <_ZN8QVariantC1ERK5QListIS_E@plt>
 2bf82ba: 48 89 ee                     	movq	%rbp, %rsi
 2bf82bd: 4c 89 f7                     	movq	%r14, %rdi
 2bf82c0: e8 db 5d 85 fe               	callq	0x144e0a0 <_ZN12QDBusMessagelsERK8QVariant@plt>
 2bf82c5: 48 89 ef                     	movq	%rbp, %rdi
 2bf82c8: 48 8d ac 24 b0 00 00 00      	leaq	0xb0(%rsp), %rbp
 2bf82d0: e8 eb 4e 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf82d5: 48 89 ef                     	movq	%rbp, %rdi
 2bf82d8: e8 03 48 85 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2bf82dd: 4c 89 f6                     	movq	%r14, %rsi
 2bf82e0: 48 89 ef                     	movq	%rbp, %rdi
 2bf82e3: e8 28 3f 85 fe               	callq	0x144c210 <_ZNK15QDBusConnection4sendERK12QDBusMessage@plt>
 2bf82e8: 48 89 ef                     	movq	%rbp, %rdi
 2bf82eb: 88 44 24 10                  	movb	%al, 0x10(%rsp)
 2bf82ef: e8 bc 55 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf82f4: 44 0f b6 4c 24 10            	movzbl	0x10(%rsp), %r9d
 2bf82fa: 4c 8d 05 4f 94 3c 03         	leaq	0x33c944f(%rip), %r8    # 0x5fc1750 <typeinfo name for CAppModeInfoImpl+0x5680>
 2bf8301: 48 8d 15 f8 05 3d 03         	leaq	0x33d05f8(%rip), %rdx   # 0x5fc8900 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::__func__>
 2bf8308: 48 8d 35 d9 3d 3c 03         	leaq	0x33c3dd9(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf830f: b9 4f 0b 00 00               	movl	$0xb4f, %ecx            # imm = 0xB4F
 2bf8314: bf 02 00 00 00               	movl	$0x2, %edi
 2bf8319: 31 c0                        	xorl	%eax, %eax
 2bf831b: e8 90 73 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf8320: 48 8d 8c 24 f0 00 00 00      	leaq	0xf0(%rsp), %rcx
 2bf8328: 48 8d 35 ee 59 3c 03         	leaq	0x33c59ee(%rip), %rsi   # 0x5fbdd1d <typeinfo name for CAppModeInfoImpl+0x1c4d>
 2bf832f: 48 89 cf                     	movq	%rcx, %rdi
 2bf8332: 48 89 4c 24 18               	movq	%rcx, 0x18(%rsp)
 2bf8337: e8 f4 6f f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf833c: 48 8d 94 24 e0 00 00 00      	leaq	0xe0(%rsp), %rdx
 2bf8344: 48 8d 35 b5 45 3c 03         	leaq	0x33c45b5(%rip), %rsi   # 0x5fbc900 <typeinfo name for CAppModeInfoImpl+0x830>
 2bf834b: 48 89 d7                     	movq	%rdx, %rdi
 2bf834e: 48 89 54 24 10               	movq	%rdx, 0x10(%rsp)
 2bf8353: e8 d8 6f f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf8358: 48 8d ac 24 d0 00 00 00      	leaq	0xd0(%rsp), %rbp
 2bf8360: 48 8d 35 81 05 3b 03         	leaq	0x33b0581(%rip), %rsi   # 0x5fa88e8 <typeinfo name for NimoLanguageImpl+0x768>
 2bf8367: 48 89 ef                     	movq	%rbp, %rdi
 2bf836a: e8 c1 6f f9 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2bf836f: 48 8b 4c 24 18               	movq	0x18(%rsp), %rcx
 2bf8374: 48 8b 54 24 10               	movq	0x10(%rsp), %rdx
 2bf8379: 48 89 ee                     	movq	%rbp, %rsi
 2bf837c: 4c 89 ff                     	movq	%r15, %rdi
 2bf837f: e8 dc 65 85 fe               	callq	0x144e960 <_ZN12QDBusMessage12createSignalERK7QStringS2_S2_@plt>
 2bf8384: 48 89 ef                     	movq	%rbp, %rdi
 2bf8387: 48 8d ac 24 60 01 00 00      	leaq	0x160(%rsp), %rbp
 2bf838f: e8 ac b6 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf8394: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
 2bf8399: e8 a2 b6 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf839e: 48 8b 7c 24 18               	movq	0x18(%rsp), %rdi
 2bf83a3: e8 98 b6 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf83a8: be 01 00 00 00               	movl	$0x1, %esi
 2bf83ad: 48 89 ef                     	movq	%rbp, %rdi
 2bf83b0: e8 ab 4c 85 fe               	callq	0x144d060 <_ZN8QVariantC1Eb@plt>
 2bf83b5: 48 89 ee                     	movq	%rbp, %rsi
 2bf83b8: 4c 89 ff                     	movq	%r15, %rdi
 2bf83bb: e8 e0 5c 85 fe               	callq	0x144e0a0 <_ZN12QDBusMessagelsERK8QVariant@plt>
 2bf83c0: 48 89 ef                     	movq	%rbp, %rdi
 2bf83c3: 48 8d ac 24 00 01 00 00      	leaq	0x100(%rsp), %rbp
 2bf83cb: e8 f0 4d 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf83d0: 48 89 ef                     	movq	%rbp, %rdi
 2bf83d3: e8 08 47 85 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2bf83d8: 4c 89 fe                     	movq	%r15, %rsi
 2bf83db: 48 89 ef                     	movq	%rbp, %rdi
 2bf83de: e8 2d 3e 85 fe               	callq	0x144c210 <_ZNK15QDBusConnection4sendERK12QDBusMessage@plt>
 2bf83e3: 48 89 ef                     	movq	%rbp, %rdi
 2bf83e6: 88 44 24 10                  	movb	%al, 0x10(%rsp)
 2bf83ea: e8 c1 54 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf83ef: 44 0f b6 4c 24 10            	movzbl	0x10(%rsp), %r9d
 2bf83f5: 4c 8d 05 ec 93 3c 03         	leaq	0x33c93ec(%rip), %r8    # 0x5fc17e8 <typeinfo name for CAppModeInfoImpl+0x5718>
 2bf83fc: 48 8d 15 fd 04 3d 03         	leaq	0x33d04fd(%rip), %rdx   # 0x5fc8900 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)::__func__>
 2bf8403: 48 8d 35 de 3c 3c 03         	leaq	0x33c3cde(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf840a: b9 55 0b 00 00               	movl	$0xb55, %ecx            # imm = 0xB55
 2bf840f: bf 02 00 00 00               	movl	$0x2, %edi
 2bf8414: 31 c0                        	xorl	%eax, %eax
 2bf8416: e8 95 72 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf841b: 4c 89 ff                     	movq	%r15, %rdi
 2bf841e: e8 6d 64 85 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2bf8423: 48 8b 3c 24                  	movq	(%rsp), %rdi
 2bf8427: e8 14 70 f9 ff               	callq	0x2b8f440 <QList<QVariant>::~QList()>
 2bf842c: 4c 89 f7                     	movq	%r14, %rdi
 2bf842f: e8 5c 64 85 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2bf8434: 4c 89 ef                     	movq	%r13, %rdi
 2bf8437: e8 04 70 f9 ff               	callq	0x2b8f440 <QList<QVariant>::~QList()>
 2bf843c: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
 2bf8441: e8 4a 64 85 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2bf8446: e9 aa fb ff ff               	jmp	0x2bf7ff5 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x115>
 2bf844b: e8 40 27 85 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 2bf8450: 49 89 c4                     	movq	%rax, %r12
 2bf8453: 48 89 ef                     	movq	%rbp, %rdi
 2bf8456: 4c 89 e5                     	movq	%r12, %rbp
 2bf8459: e8 52 54 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf845e: 4c 89 ff                     	movq	%r15, %rdi
 2bf8461: e8 2a 64 85 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2bf8466: 48 8b 3c 24                  	movq	(%rsp), %rdi
 2bf846a: e8 d1 6f f9 ff               	callq	0x2b8f440 <QList<QVariant>::~QList()>
 2bf846f: 4c 89 f7                     	movq	%r14, %rdi
 2bf8472: e8 19 64 85 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2bf8477: 4c 89 ef                     	movq	%r13, %rdi
 2bf847a: e8 c1 6f f9 ff               	callq	0x2b8f440 <QList<QVariant>::~QList()>
 2bf847f: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
 2bf8484: e8 07 64 85 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2bf8489: 48 89 df                     	movq	%rbx, %rdi
 2bf848c: e8 8f 68 85 fe               	callq	0x144ed20 <_ZN21QDBusPendingReplyDataD2Ev@plt>
 2bf8491: 48 89 ef                     	movq	%rbp, %rdi
 2bf8494: e8 c7 4d 85 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2bf8499: 49 89 c4                     	movq	%rax, %r12
 2bf849c: 48 89 ef                     	movq	%rbp, %rdi
 2bf849f: e8 1c 4d 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf84a4: 4c 89 e5                     	movq	%r12, %rbp
 2bf84a7: eb b5                        	jmp	0x2bf845e <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x57e>
 2bf84a9: 48 89 c5                     	movq	%rax, %rbp
 2bf84ac: eb b0                        	jmp	0x2bf845e <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x57e>
 2bf84ae: 49 89 c4                     	movq	%rax, %r12
 2bf84b1: 48 89 ef                     	movq	%rbp, %rdi
 2bf84b4: 4c 89 e5                     	movq	%r12, %rbp
 2bf84b7: e8 84 b5 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf84bc: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
 2bf84c1: e8 7a b5 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf84c6: 48 8b 7c 24 18               	movq	0x18(%rsp), %rdi
 2bf84cb: e8 70 b5 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf84d0: eb 94                        	jmp	0x2bf8466 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x586>
 2bf84d2: 48 89 c5                     	movq	%rax, %rbp
 2bf84d5: eb e5                        	jmp	0x2bf84bc <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x5dc>
 2bf84d7: 48 89 c5                     	movq	%rax, %rbp
 2bf84da: eb ea                        	jmp	0x2bf84c6 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x5e6>
 2bf84dc: 49 89 c4                     	movq	%rax, %r12
 2bf84df: 48 89 ef                     	movq	%rbp, %rdi
 2bf84e2: e8 c9 53 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf84e7: 4c 89 e5                     	movq	%r12, %rbp
 2bf84ea: e9 77 ff ff ff               	jmp	0x2bf8466 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x586>
 2bf84ef: 49 89 c4                     	movq	%rax, %r12
 2bf84f2: 48 89 ef                     	movq	%rbp, %rdi
 2bf84f5: e8 c6 4c 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf84fa: 4c 89 e5                     	movq	%r12, %rbp
 2bf84fd: e9 64 ff ff ff               	jmp	0x2bf8466 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x586>
 2bf8502: eb eb                        	jmp	0x2bf84ef <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x60f>
 2bf8504: 48 89 c5                     	movq	%rax, %rbp
 2bf8507: e9 5a ff ff ff               	jmp	0x2bf8466 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x586>
 2bf850c: 49 89 c4                     	movq	%rax, %r12
 2bf850f: 48 89 ef                     	movq	%rbp, %rdi
 2bf8512: 4c 89 e5                     	movq	%r12, %rbp
 2bf8515: e8 26 b5 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf851a: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
 2bf851f: e8 1c b5 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf8524: 48 8b 7c 24 18               	movq	0x18(%rsp), %rdi
 2bf8529: e8 12 b5 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf852e: e9 44 ff ff ff               	jmp	0x2bf8477 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x597>
 2bf8533: 48 89 c5                     	movq	%rax, %rbp
 2bf8536: eb e2                        	jmp	0x2bf851a <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x63a>
 2bf8538: 48 89 c5                     	movq	%rax, %rbp
 2bf853b: eb e7                        	jmp	0x2bf8524 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x644>
 2bf853d: 49 89 c4                     	movq	%rax, %r12
 2bf8540: 48 89 ef                     	movq	%rbp, %rdi
 2bf8543: e8 68 53 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf8548: 4c 89 e5                     	movq	%r12, %rbp
 2bf854b: e9 27 ff ff ff               	jmp	0x2bf8477 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x597>
 2bf8550: 49 89 c4                     	movq	%rax, %r12
 2bf8553: 48 89 ef                     	movq	%rbp, %rdi
 2bf8556: e8 65 4c 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf855b: 4c 89 e5                     	movq	%r12, %rbp
 2bf855e: e9 14 ff ff ff               	jmp	0x2bf8477 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x597>
 2bf8563: 49 89 c4                     	movq	%rax, %r12
 2bf8566: 48 89 ef                     	movq	%rbp, %rdi
 2bf8569: 4c 89 e5                     	movq	%r12, %rbp
 2bf856c: e8 4f 4c 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf8571: 48 8b 7c 24 10               	movq	0x10(%rsp), %rdi
 2bf8576: e8 45 4c 85 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2bf857b: e9 f7 fe ff ff               	jmp	0x2bf8477 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x597>
 2bf8580: 48 89 c5                     	movq	%rax, %rbp
 2bf8583: 4c 8d 6c 24 40               	leaq	0x40(%rsp), %r13
 2bf8588: eb e7                        	jmp	0x2bf8571 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x691>
 2bf858a: 48 89 c5                     	movq	%rax, %rbp
 2bf858d: e9 e5 fe ff ff               	jmp	0x2bf8477 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x597>
 2bf8592: 4c 89 f7                     	movq	%r14, %rdi
 2bf8595: 48 89 c5                     	movq	%rax, %rbp
 2bf8598: e8 a3 b4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf859d: 48 8b 3c 24                  	movq	(%rsp), %rdi
 2bf85a1: e8 9a b4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf85a6: 4c 89 ff                     	movq	%r15, %rdi
 2bf85a9: e8 92 b4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf85ae: e9 d6 fe ff ff               	jmp	0x2bf8489 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x5a9>
 2bf85b3: 48 89 c5                     	movq	%rax, %rbp
 2bf85b6: eb e5                        	jmp	0x2bf859d <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x6bd>
 2bf85b8: 48 89 c5                     	movq	%rax, %rbp
 2bf85bb: eb e9                        	jmp	0x2bf85a6 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x6c6>
 2bf85bd: 49 89 c4                     	movq	%rax, %r12
 2bf85c0: 48 8d 7d 10                  	leaq	0x10(%rbp), %rdi
 2bf85c4: e8 77 b4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf85c9: 48 8d 7d 08                  	leaq	0x8(%rbp), %rdi
 2bf85cd: 4c 89 e5                     	movq	%r12, %rbp
 2bf85d0: e8 6b b4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf85d5: e9 af fe ff ff               	jmp	0x2bf8489 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x5a9>
 2bf85da: 48 89 c5                     	movq	%rax, %rbp
 2bf85dd: e9 a7 fe ff ff               	jmp	0x2bf8489 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x5a9>
 2bf85e2: 4c 89 ef                     	movq	%r13, %rdi
 2bf85e5: 49 89 c4                     	movq	%rax, %r12
 2bf85e8: e8 53 b4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf85ed: eb d1                        	jmp	0x2bf85c0 <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x6e0>
 2bf85ef: eb e9                        	jmp	0x2bf85da <CAppManagerComm::RegisterAllKeyEventFrontMap(QDBusPendingCallWatcher*)+0x6fa>
 2bf85f1: 90                           	nop
 2bf85f2: 0f 1f 40 00                  	nopl	(%rax)
 2bf85f6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000002bf8600 <CAppManagerComm::RegisterAllKeyEventRearMap(QDBusPendingCallWatcher*)>:
 2bf8600: 41 57                        	pushq	%r15
 2bf8602: 41 56                        	pushq	%r14
 2bf8604: 4c 8d 05 c5 99 3c 03         	leaq	0x33c99c5(%rip), %r8    # 0x5fc1fd0 <typeinfo name for CAppModeInfoImpl+0x5f00>
 2bf860b: 41 55                        	pushq	%r13
 2bf860d: 41 54                        	pushq	%r12
 2bf860f: 48 8d 15 ca 02 3d 03         	leaq	0x33d02ca(%rip), %rdx   # 0x5fc88e0 <CAppManagerComm::RegisterAllKeyEventRearMap(QDBusPendingCallWatcher*)::__func__>
 2bf8616: 55                           	pushq	%rbp
 2bf8617: 53                           	pushq	%rbx
 2bf8618: 48 89 f5                     	movq	%rsi, %rbp
 2bf861b: 48 8d 35 c6 3a 3c 03         	leaq	0x33c3ac6(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf8622: b9 72 0b 00 00               	movl	$0xb72, %ecx            # imm = 0xB72
 2bf8627: 49 89 fd                     	movq	%rdi, %r13
 2bf862a: 48 81 ec 18 01 00 00         	subq	$0x118, %rsp            # imm = 0x118
 2bf8631: 44 8b 0d 78 80 ab 04         	movl	0x4ab8078(%rip), %r9d   # 0x76b06b0 <CAppManagerComm::RegisterAllKeyEventRearMap(QDBusPendingCallWatcher*)::nCount>
 2bf8638: bf 02 00 00 00               	movl	$0x2, %edi
 2bf863d: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 2bf8646: 48 89 84 24 08 01 00 00      	movq	%rax, 0x108(%rsp)
 2bf864e: 31 c0                        	xorl	%eax, %eax
 2bf8650: 48 8d 5c 24 10               	leaq	0x10(%rsp), %rbx
 2bf8655: e8 56 70 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf865a: 48 89 df                     	movq	%rbx, %rdi
 2bf865d: e8 0e 30 85 fe               	callq	0x144b670 <_ZN21QDBusPendingReplyDataC2Ev@plt>
 2bf8662: 48 8d 75 10                  	leaq	0x10(%rbp), %rsi
 2bf8666: 48 89 df                     	movq	%rbx, %rdi
 2bf8669: e8 12 3d 85 fe               	callq	0x144c380 <_ZN21QDBusPendingReplyData6assignERK16QDBusPendingCall@plt>
 2bf866e: 48 83 7c 24 10 00            	cmpq	$0x0, 0x10(%rsp)
 2bf8674: 74 20                        	je	0x2bf8696 <CAppManagerComm::RegisterAllKeyEventRearMap(QDBusPendingCallWatcher*)+0x96>
 2bf8676: 48 8d 94 24 00 01 00 00      	leaq	0x100(%rsp), %rdx
 2bf867e: be 01 00 00 00               	movl	$0x1, %esi
 2bf8683: 48 89 df                     	movq	%rbx, %rdi
 2bf8686: c7 84 24 00 01 00 00 02 00 00 00     	movl	$0x2, 0x100(%rsp)
 2bf8691: e8 2a 50 85 fe               	callq	0x144d6c0 <_ZN21QDBusPendingReplyData12setMetaTypesEiPKi@plt>
 2bf8696: 48 89 df                     	movq	%rbx, %rdi
 2bf8699: e8 f2 4e 85 fe               	callq	0x144d590 <_ZNK16QDBusPendingCall7isErrorEv@plt>
 2bf869e: 84 c0                        	testb	%al, %al
 2bf86a0: 0f 84 aa 00 00 00            	je	0x2bf8750 <CAppManagerComm::RegisterAllKeyEventRearMap(QDBusPendingCallWatcher*)+0x150>
 2bf86a6: 4c 8d bc 24 e0 00 00 00      	leaq	0xe0(%rsp), %r15
 2bf86ae: 48 89 de                     	movq	%rbx, %rsi
 2bf86b1: 4c 89 ff                     	movq	%r15, %rdi
 2bf86b4: e8 c7 41 85 fe               	callq	0x144c880 <_ZNK16QDBusPendingCall5errorEv@plt>
 2bf86b9: 4c 8d 64 24 20               	leaq	0x20(%rsp), %r12
 2bf86be: 4c 89 fe                     	movq	%r15, %rsi
 2bf86c1: 4c 89 e7                     	movq	%r12, %rdi
 2bf86c4: e8 b7 5e 85 fe               	callq	0x144e580 <_ZNK10QDBusError7messageEv@plt>
 2bf86c9: 4c 89 e7                     	movq	%r12, %rdi
 2bf86cc: e8 1f 5f 85 fe               	callq	0x144e5f0 <_ZNK7QString5utf16Ev@plt>
 2bf86d1: 4c 8d 05 9c 06 3d 03         	leaq	0x33d069c(%rip), %r8    # 0x5fc8d74 <CAppManagerComm::Initialize(int, char**)::__func__+0xc>
 2bf86d8: 48 8d 15 01 02 3d 03         	leaq	0x33d0201(%rip), %rdx   # 0x5fc88e0 <CAppManagerComm::RegisterAllKeyEventRearMap(QDBusPendingCallWatcher*)::__func__>
 2bf86df: 48 8d 35 02 3a 3c 03         	leaq	0x33c3a02(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf86e6: 49 89 c1                     	movq	%rax, %r9
 2bf86e9: b9 76 0b 00 00               	movl	$0xb76, %ecx            # imm = 0xB76
 2bf86ee: bf 03 00 00 00               	movl	$0x3, %edi
 2bf86f3: 31 c0                        	xorl	%eax, %eax
 2bf86f5: e8 b6 6f c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf86fa: 4c 89 e7                     	movq	%r12, %rdi
 2bf86fd: e8 3e b3 f7 ff               	callq	0x2b73a40 <QString::~QString()>
