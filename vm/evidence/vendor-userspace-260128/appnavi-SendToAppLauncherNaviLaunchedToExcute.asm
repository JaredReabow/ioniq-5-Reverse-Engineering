
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

0000000002c08ab0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()>:
 2c08ab0: 55                           	pushq	%rbp
 2c08ab1: 48 89 e5                     	movq	%rsp, %rbp
 2c08ab4: 41 57                        	pushq	%r15
 2c08ab6: 41 56                        	pushq	%r14
 2c08ab8: 41 55                        	pushq	%r13
 2c08aba: 41 54                        	pushq	%r12
 2c08abc: 53                           	pushq	%rbx
 2c08abd: 48 81 ec 78 03 00 00         	subq	$0x378, %rsp            # imm = 0x378
 2c08ac4: 48 89 bd 88 fc ff ff         	movq	%rdi, -0x378(%rbp)
 2c08acb: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 2c08ad4: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
 2c08ad8: 31 c0                        	xorl	%eax, %eax
 2c08ada: 80 3d e0 8a 26 05 00         	cmpb	$0x0, 0x5268ae0(%rip)   # 0x7e715c1 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::alreadySendSignal>
 2c08ae1: 0f 85 b1 05 00 00            	jne	0x2c09098 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x5e8>
 2c08ae7: 4c 8d 05 ca ca 3b 03         	leaq	0x33bcaca(%rip), %r8    # 0x5fc55b8 <typeinfo name for CAppModeInfoImpl+0x94e8>
 2c08aee: 48 8d 15 8b f5 3b 03         	leaq	0x33bf58b(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c08af5: 48 8d 35 ec 35 3b 03         	leaq	0x33b35ec(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c08afc: b9 33 19 00 00               	movl	$0x1933, %ecx           # imm = 0x1933
 2c08b01: 49 89 ff                     	movq	%rdi, %r15
 2c08b04: bf 02 00 00 00               	movl	$0x2, %edi
 2c08b09: e8 a2 6b c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c08b0e: 48 8d 85 10 fd ff ff         	leaq	-0x2f0(%rbp), %rax
 2c08b15: 48 8d 35 72 53 3b 03         	leaq	0x33b5372(%rip), %rsi   # 0x5fbde8e <typeinfo name for CAppModeInfoImpl+0x1dbe>
 2c08b1c: 48 8d 9d 70 fd ff ff         	leaq	-0x290(%rbp), %rbx
 2c08b23: c6 05 97 8a 26 05 01         	movb	$0x1, 0x5268a97(%rip)   # 0x7e715c1 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::alreadySendSignal>
 2c08b2a: 48 89 c7                     	movq	%rax, %rdi
 2c08b2d: 49 89 c6                     	movq	%rax, %r14
 2c08b30: 48 89 85 98 fc ff ff         	movq	%rax, -0x368(%rbp)
 2c08b37: e8 f4 67 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c08b3c: 48 8d 35 63 53 3b 03         	leaq	0x33b5363(%rip), %rsi   # 0x5fbdea6 <typeinfo name for CAppModeInfoImpl+0x1dd6>
 2c08b43: 48 89 df                     	movq	%rbx, %rdi
 2c08b46: e8 e5 67 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c08b4b: 4c 8d a5 d0 fd ff ff         	leaq	-0x230(%rbp), %r12
 2c08b52: 48 8d 35 77 4a 3b 03         	leaq	0x33b4a77(%rip), %rsi   # 0x5fbd5d0 <typeinfo name for CAppModeInfoImpl+0x1500>
 2c08b59: 4c 89 e7                     	movq	%r12, %rdi
 2c08b5c: e8 cf 67 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c08b61: 4c 8d ad 00 fd ff ff         	leaq	-0x300(%rbp), %r13
 2c08b68: 4c 89 ef                     	movq	%r13, %rdi
 2c08b6b: e8 70 3f 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c08b70: bf 10 00 00 00               	movl	$0x10, %edi
 2c08b75: e8 b6 52 84 fe               	callq	0x144de30 <_Znwm@plt>
 2c08b7a: 4d 89 f9                     	movq	%r15, %r9
 2c08b7d: 4d 89 e8                     	movq	%r13, %r8
 2c08b80: 4c 89 e1                     	movq	%r12, %rcx
 2c08b83: 48 89 da                     	movq	%rbx, %rdx
 2c08b86: 4c 89 f6                     	movq	%r14, %rsi
 2c08b89: 48 89 c7                     	movq	%rax, %rdi
 2c08b8c: 48 89 85 80 fc ff ff         	movq	%rax, -0x380(%rbp)
 2c08b93: e8 98 3c 84 fe               	callq	0x144c830 <_ZN14QDBusInterfaceC1ERK7QStringS2_S2_RK15QDBusConnectionP7QObject@plt>
 2c08b98: 4c 89 ef                     	movq	%r13, %rdi
 2c08b9b: 4c 8d bd d0 fc ff ff         	leaq	-0x330(%rbp), %r15
 2c08ba2: e8 09 4d 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c08ba7: 4c 89 e7                     	movq	%r12, %rdi
 2c08baa: e8 91 ae f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c08baf: 48 89 df                     	movq	%rbx, %rdi
 2c08bb2: e8 89 ae f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c08bb7: 4c 89 f7                     	movq	%r14, %rdi
 2c08bba: e8 81 ae f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c08bbf: 8b 85 d8 fd ff ff            	movl	-0x228(%rbp), %eax
 2c08bc5: 48 8d 35 85 6d 1c 03         	leaq	0x31c6d85(%rip), %rsi   # 0x5dcf951 <typeinfo name for NimoExSLMapRenderer+0xf1>
 2c08bcc: 4c 89 ff                     	movq	%r15, %rdi
 2c08bcf: 48 c7 85 d0 fd ff ff 00 00 00 00     	movq	$0x0, -0x230(%rbp)
 2c08bda: 48 c7 85 70 fd ff ff 00 00 00 00     	movq	$0x0, -0x290(%rbp)
 2c08be5: 48 c7 85 10 fd ff ff 00 00 00 00     	movq	$0x0, -0x2f0(%rbp)
 2c08bf0: 48 c7 85 00 fd ff ff 00 00 00 00     	movq	$0x0, -0x300(%rbp)
 2c08bfb: 25 00 00 00 c0               	andl	$0xc0000000, %eax       # imm = 0xC0000000
 2c08c00: 48 c7 85 f0 fc ff ff 00 00 00 00     	movq	$0x0, -0x310(%rbp)
 2c08c0b: 48 c7 85 e0 fc ff ff 00 00 00 00     	movq	$0x0, -0x320(%rbp)
 2c08c16: 89 85 d8 fd ff ff            	movl	%eax, -0x228(%rbp)
 2c08c1c: 8b 85 78 fd ff ff            	movl	-0x288(%rbp), %eax
 2c08c22: c6 85 db fd ff ff 80         	movb	$-0x80, -0x225(%rbp)
 2c08c29: 25 00 00 00 c0               	andl	$0xc0000000, %eax       # imm = 0xC0000000
 2c08c2e: 89 85 78 fd ff ff            	movl	%eax, -0x288(%rbp)
 2c08c34: 8b 85 18 fd ff ff            	movl	-0x2e8(%rbp), %eax
 2c08c3a: c6 85 7b fd ff ff 80         	movb	$-0x80, -0x285(%rbp)
 2c08c41: 25 00 00 00 c0               	andl	$0xc0000000, %eax       # imm = 0xC0000000
 2c08c46: 89 85 18 fd ff ff            	movl	%eax, -0x2e8(%rbp)
 2c08c4c: 8b 85 08 fd ff ff            	movl	-0x2f8(%rbp), %eax
 2c08c52: c6 85 1b fd ff ff 80         	movb	$-0x80, -0x2e5(%rbp)
 2c08c59: 25 00 00 00 c0               	andl	$0xc0000000, %eax       # imm = 0xC0000000
 2c08c5e: 89 85 08 fd ff ff            	movl	%eax, -0x2f8(%rbp)
 2c08c64: 8b 85 f8 fc ff ff            	movl	-0x308(%rbp), %eax
 2c08c6a: c6 85 0b fd ff ff 80         	movb	$-0x80, -0x2f5(%rbp)
 2c08c71: 25 00 00 00 c0               	andl	$0xc0000000, %eax       # imm = 0xC0000000
 2c08c76: 89 85 f8 fc ff ff            	movl	%eax, -0x308(%rbp)
 2c08c7c: 8b 85 e8 fc ff ff            	movl	-0x318(%rbp), %eax
 2c08c82: c6 85 fb fc ff ff 80         	movb	$-0x80, -0x305(%rbp)
 2c08c89: 25 00 00 00 c0               	andl	$0xc0000000, %eax       # imm = 0xC0000000
 2c08c8e: 89 85 e8 fc ff ff            	movl	%eax, -0x318(%rbp)
 2c08c94: c6 85 eb fc ff ff 80         	movb	$-0x80, -0x315(%rbp)
 2c08c9b: e8 60 49 84 fe               	callq	0x144d600 <_ZN8QVariantC1EPKc@plt>
 2c08ca0: 48 8d 85 c0 fc ff ff         	leaq	-0x340(%rbp), %rax
 2c08ca7: be 1e 00 00 00               	movl	$0x1e, %esi
 2c08cac: 48 89 c7                     	movq	%rax, %rdi
 2c08caf: 48 89 85 70 fc ff ff         	movq	%rax, -0x390(%rbp)
 2c08cb6: e8 a5 39 84 fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 2c08cbb: 48 8d 95 a0 fc ff ff         	leaq	-0x360(%rbp), %rdx
 2c08cc2: 48 8d 35 e5 51 3b 03         	leaq	0x33b51e5(%rip), %rsi   # 0x5fbdeae <typeinfo name for CAppModeInfoImpl+0x1dde>
 2c08cc9: 48 89 d7                     	movq	%rdx, %rdi
 2c08ccc: 48 89 95 78 fc ff ff         	movq	%rdx, -0x388(%rbp)
 2c08cd3: e8 58 66 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c08cd8: 48 8d 8d b0 fc ff ff         	leaq	-0x350(%rbp), %rcx
 2c08cdf: 41 54                        	pushq	%r12
 2c08ce1: 4c 89 b5 98 fc ff ff         	movq	%r14, -0x368(%rbp)
 2c08ce8: 53                           	pushq	%rbx
 2c08ce9: 41 56                        	pushq	%r14
 2c08ceb: 4c 8d b5 f0 fc ff ff         	leaq	-0x310(%rbp), %r14
 2c08cf2: 49 89 ca                     	movq	%rcx, %r10
 2c08cf5: 48 8d 8d e0 fc ff ff         	leaq	-0x320(%rbp), %rcx
 2c08cfc: 41 55                        	pushq	%r13
 2c08cfe: 4c 8b 85 70 fc ff ff         	movq	-0x390(%rbp), %r8
 2c08d05: 41 56                        	pushq	%r14
 2c08d07: 4d 89 f9                     	movq	%r15, %r9
 2c08d0a: 48 89 8d 90 fc ff ff         	movq	%rcx, -0x370(%rbp)
 2c08d11: 51                           	pushq	%rcx
 2c08d12: 31 d2                        	xorl	%edx, %edx
 2c08d14: 48 8b 8d 78 fc ff ff         	movq	-0x388(%rbp), %rcx
 2c08d1b: 48 8b b5 80 fc ff ff         	movq	-0x380(%rbp), %rsi
 2c08d22: 4c 89 d7                     	movq	%r10, %rdi
 2c08d25: 4c 89 95 68 fc ff ff         	movq	%r10, -0x398(%rbp)
 2c08d2c: e8 cf 2f 84 fe               	callq	0x144bd00 <_ZN22QDBusAbstractInterface4callEN5QDBus8CallModeERK7QStringRK8QVariantS7_S7_S7_S7_S7_S7_S7_@plt>
 2c08d31: 48 8b bd 68 fc ff ff         	movq	-0x398(%rbp), %rdi
 2c08d38: 48 83 c4 30                  	addq	$0x30, %rsp
 2c08d3c: e8 4f 5b 84 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2c08d41: 48 8b bd 78 fc ff ff         	movq	-0x388(%rbp), %rdi
 2c08d48: e8 f3 ac f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c08d4d: 48 8b bd 70 fc ff ff         	movq	-0x390(%rbp), %rdi
 2c08d54: e8 67 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d59: 4c 89 ff                     	movq	%r15, %rdi
 2c08d5c: e8 5f 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d61: 48 8b bd 90 fc ff ff         	movq	-0x370(%rbp), %rdi
 2c08d68: e8 53 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d6d: 4c 89 f7                     	movq	%r14, %rdi
 2c08d70: e8 4b 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d75: 4c 89 ef                     	movq	%r13, %rdi
 2c08d78: e8 43 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d7d: 48 8b bd 98 fc ff ff         	movq	-0x368(%rbp), %rdi
 2c08d84: e8 37 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d89: 48 89 df                     	movq	%rbx, %rdi
 2c08d8c: e8 2f 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d91: 4c 89 e7                     	movq	%r12, %rdi
 2c08d94: e8 27 44 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08d99: 4c 8d 05 a0 c8 3b 03         	leaq	0x33bc8a0(%rip), %r8    # 0x5fc5640 <typeinfo name for CAppModeInfoImpl+0x9570>
 2c08da0: 48 8d 15 d9 f2 3b 03         	leaq	0x33bf2d9(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c08da7: 48 8d 35 3a 33 3b 03         	leaq	0x33b333a(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c08dae: b9 3e 19 00 00               	movl	$0x193e, %ecx           # imm = 0x193E
 2c08db3: 31 c0                        	xorl	%eax, %eax
 2c08db5: bf 02 00 00 00               	movl	$0x2, %edi
 2c08dba: e8 f1 68 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c08dbf: 48 8b bd 80 fc ff ff         	movq	-0x380(%rbp), %rdi
 2c08dc6: e8 75 25 84 fe               	callq	0x144b340 <_ZN7QObject11deleteLaterEv@plt>
 2c08dcb: 48 8d 35 e5 50 3b 03         	leaq	0x33b50e5(%rip), %rsi   # 0x5fbdeb7 <typeinfo name for CAppModeInfoImpl+0x1de7>
 2c08dd2: 4c 89 e7                     	movq	%r12, %rdi
 2c08dd5: e8 56 65 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c08dda: 48 8d 35 0f 48 3b 03         	leaq	0x33b480f(%rip), %rsi   # 0x5fbd5f0 <typeinfo name for CAppModeInfoImpl+0x1520>
 2c08de1: 48 89 df                     	movq	%rbx, %rdi
 2c08de4: e8 47 65 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c08de9: 48 8b bd 98 fc ff ff         	movq	-0x368(%rbp), %rdi
 2c08df0: 48 8d 35 f1 fa 39 03         	leaq	0x339faf1(%rip), %rsi   # 0x5fa88e8 <typeinfo name for NimoLanguageImpl+0x768>
 2c08df7: e8 34 65 f8 ff               	callq	0x2b8f330 <QString::QString(char const*)>
 2c08dfc: 48 8b b5 98 fc ff ff         	movq	-0x368(%rbp), %rsi
 2c08e03: 48 8b bd 90 fc ff ff         	movq	-0x370(%rbp), %rdi
 2c08e0a: 4c 89 e1                     	movq	%r12, %rcx
 2c08e0d: 48 89 da                     	movq	%rbx, %rdx
 2c08e10: e8 4b 5b 84 fe               	callq	0x144e960 <_ZN12QDBusMessage12createSignalERK7QStringS2_S2_@plt>
 2c08e15: 48 8b bd 98 fc ff ff         	movq	-0x368(%rbp), %rdi
 2c08e1c: e8 1f ac f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c08e21: 48 89 df                     	movq	%rbx, %rdi
 2c08e24: e8 17 ac f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c08e29: 4c 89 e7                     	movq	%r12, %rdi
 2c08e2c: e8 0f ac f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c08e31: be 05 00 00 00               	movl	$0x5, %esi
 2c08e36: 4c 89 ef                     	movq	%r13, %rdi
 2c08e39: e8 22 38 84 fe               	callq	0x144c660 <_ZN8QVariantC1Ei@plt>
 2c08e3e: 48 8b bd 90 fc ff ff         	movq	-0x370(%rbp), %rdi
 2c08e45: 4c 89 ee                     	movq	%r13, %rsi
 2c08e48: e8 53 52 84 fe               	callq	0x144e0a0 <_ZN12QDBusMessagelsERK8QVariant@plt>
 2c08e4d: 4c 89 ef                     	movq	%r13, %rdi
 2c08e50: e8 6b 43 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c08e55: 4c 89 f7                     	movq	%r14, %rdi
 2c08e58: e8 83 3c 84 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2c08e5d: 48 8b b5 90 fc ff ff         	movq	-0x370(%rbp), %rsi
 2c08e64: 4c 89 f7                     	movq	%r14, %rdi
 2c08e67: e8 a4 33 84 fe               	callq	0x144c210 <_ZNK15QDBusConnection4sendERK12QDBusMessage@plt>
 2c08e6c: 4c 89 f7                     	movq	%r14, %rdi
 2c08e6f: 88 85 80 fc ff ff            	movb	%al, -0x380(%rbp)
 2c08e75: e8 36 4a 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c08e7a: 44 0f b6 8d 80 fc ff ff      	movzbl	-0x380(%rbp), %r9d
 2c08e82: 4c 8d 05 57 c8 3b 03         	leaq	0x33bc857(%rip), %r8    # 0x5fc56e0 <typeinfo name for CAppModeInfoImpl+0x9610>
 2c08e89: 48 8d 15 f0 f1 3b 03         	leaq	0x33bf1f0(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c08e90: 48 8d 35 51 32 3b 03         	leaq	0x33b3251(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c08e97: b9 4a 19 00 00               	movl	$0x194a, %ecx           # imm = 0x194A
 2c08e9c: bf 02 00 00 00               	movl	$0x2, %edi
 2c08ea1: 31 c0                        	xorl	%eax, %eax
 2c08ea3: e8 08 68 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c08ea8: 4c 8b b5 98 fc ff ff         	movq	-0x368(%rbp), %r14
 2c08eaf: c7 85 d0 fc ff ff 00 00 00 00	movl	$0x0, -0x330(%rbp)
 2c08eb9: 48 c7 85 20 fd ff ff 00 00 00 00     	movq	$0x0, -0x2e0(%rbp)
 2c08ec4: 48 c7 85 28 fd ff ff 00 00 00 00     	movq	$0x0, -0x2d8(%rbp)
 2c08ecf: 48 c7 85 30 fd ff ff 00 00 00 00     	movq	$0x0, -0x2d0(%rbp)
 2c08eda: 48 c7 85 38 fd ff ff 00 00 00 00     	movq	$0x0, -0x2c8(%rbp)
 2c08ee5: 49 8d 7e 40                  	leaq	0x40(%r14), %rdi
 2c08ee9: 48 c7 85 40 fd ff ff 00 00 00 00     	movq	$0x0, -0x2c0(%rbp)
 2c08ef4: 48 c7 85 48 fd ff ff 00 00 00 00     	movq	$0x0, -0x2b8(%rbp)
 2c08eff: 48 c7 85 50 fd ff ff 00 00 00 00     	movq	$0x0, -0x2b0(%rbp)
 2c08f0a: 48 c7 85 58 fd ff ff 00 00 00 00     	movq	$0x0, -0x2a8(%rbp)
 2c08f15: 48 c7 85 60 fd ff ff 00 00 00 00     	movq	$0x0, -0x2a0(%rbp)
 2c08f20: c7 85 10 fd ff ff 00 00 00 00	movl	$0x0, -0x2f0(%rbp)
 2c08f2a: 48 c7 85 18 fd ff ff 00 00 00 00     	movq	$0x0, -0x2e8(%rbp)
 2c08f35: e8 26 a0 fd ff               	callq	0x2be2f60 <std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>>>::clear() (.constprop.129)>
 2c08f3a: 4c 89 f6                     	movq	%r14, %rsi
 2c08f3d: 48 89 df                     	movq	%rbx, %rdi
 2c08f40: e8 9b 84 09 ff               	callq	0x1ca13e0 <NaviAdapter::ExternalParameter::ExternalParameter(NaviAdapter::ExternalParameter const&)>
 2c08f45: 4c 89 fa                     	movq	%r15, %rdx
 2c08f48: 48 89 de                     	movq	%rbx, %rsi
 2c08f4b: bf 8d 00 00 00               	movl	$0x8d, %edi
 2c08f50: e8 ab 28 67 ff               	callq	0x227b800 <NaviAdapter::VehicleSetting::sendExternalMessage(NaviAdapter::VehicleSetting::eMessageId, NaviAdapter::ExternalParameter, int&)>
 2c08f55: 48 89 df                     	movq	%rbx, %rdi
 2c08f58: e8 13 e3 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c08f5d: e8 de 2d 74 00               	callq	0x334bd40 <CPersistenceComm::GetInstance()>
 2c08f62: 48 89 c7                     	movq	%rax, %rdi
 2c08f65: e8 06 48 74 00               	callq	0x334d770 <CPersistenceComm::GetPersistenceDataAWEnable()>
 2c08f6a: 4c 8d 05 b7 c7 3b 03         	leaq	0x33bc7b7(%rip), %r8    # 0x5fc5728 <typeinfo name for CAppModeInfoImpl+0x9658>
 2c08f71: 48 8d 15 08 f1 3b 03         	leaq	0x33bf108(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c08f78: 48 8d 35 69 31 3b 03         	leaq	0x33b3169(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c08f7f: 41 89 c6                     	movl	%eax, %r14d
 2c08f82: 41 89 c1                     	movl	%eax, %r9d
 2c08f85: b9 62 19 00 00               	movl	$0x1962, %ecx           # imm = 0x1962
 2c08f8a: bf 02 00 00 00               	movl	$0x2, %edi
 2c08f8f: 31 c0                        	xorl	%eax, %eax
 2c08f91: e8 1a 67 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c08f96: 80 3d 23 86 26 05 00         	cmpb	$0x0, 0x5268623(%rip)   # 0x7e715c0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::alreadyCameraSSDataRead>
 2c08f9d: 0f 85 89 00 00 00            	jne	0x2c0902c <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x57c>
 2c08fa3: 48 8b bd 88 fc ff ff         	movq	-0x378(%rbp), %rdi
 2c08faa: c6 05 0f 86 26 05 01         	movb	$0x1, 0x526860f(%rip)   # 0x7e715c0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::alreadyCameraSSDataRead>
 2c08fb1: e8 1a 32 fe ff               	callq	0x2bec1d0 <CAppManagerComm::ReadCameraSSDataFromSharedMemory()>
 2c08fb6: 41 83 fe 01                  	cmpl	$0x1, %r14d
 2c08fba: 41 89 c7                     	movl	%eax, %r15d
 2c08fbd: 74 44                        	je	0x2c09003 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x553>
 2c08fbf: 85 c0                        	testl	%eax, %eax
 2c08fc1: 0f 8e e9 01 00 00            	jle	0x2c091b0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x700>
 2c08fc7: 31 f6                        	xorl	%esi, %esi
 2c08fc9: 83 f8 01                     	cmpl	$0x1, %eax
 2c08fcc: bf 09 00 00 00               	movl	$0x9, %edi
 2c08fd1: 40 0f 94 c6                  	sete	%sil
 2c08fd5: e8 c6 98 66 ff               	callq	0x22728a0 <NaviAdapter::System::onLayoutChanged(ecScreenId, NaviAdapter::System::ecWindowStatus)>
 2c08fda: 4c 8d 05 6f c8 3b 03         	leaq	0x33bc86f(%rip), %r8    # 0x5fc5850 <typeinfo name for CAppModeInfoImpl+0x9780>
 2c08fe1: 45 89 f9                     	movl	%r15d, %r9d
 2c08fe4: b9 6f 19 00 00               	movl	$0x196f, %ecx           # imm = 0x196F
 2c08fe9: 48 8d 15 90 f0 3b 03         	leaq	0x33bf090(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c08ff0: 48 8d 35 f1 30 3b 03         	leaq	0x33b30f1(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c08ff7: bf 02 00 00 00               	movl	$0x2, %edi
 2c08ffc: 31 c0                        	xorl	%eax, %eax
 2c08ffe: e8 ad 66 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c09003: 4c 8d 05 9e c7 3b 03         	leaq	0x33bc79e(%rip), %r8    # 0x5fc57a8 <typeinfo name for CAppModeInfoImpl+0x96d8>
 2c0900a: 48 8d 15 6f f0 3b 03         	leaq	0x33bf06f(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c09011: 48 8d 35 d0 30 3b 03         	leaq	0x33b30d0(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c09018: 45 89 f9                     	movl	%r15d, %r9d
 2c0901b: b9 74 19 00 00               	movl	$0x1974, %ecx           # imm = 0x1974
 2c09020: bf 02 00 00 00               	movl	$0x2, %edi
 2c09025: 31 c0                        	xorl	%eax, %eax
 2c09027: e8 84 66 c0 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2c0902c: e8 1f 5a 6f 00               	callq	0x32fea50 <CTmsComm::GetInstance()>
 2c09031: 83 78 44 04                  	cmpl	$0x4, 0x44(%rax)
 2c09035: 0f 84 85 00 00 00            	je	0x2c090c0 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x610>
 2c0903b: 48 8b bd 88 fc ff ff         	movq	-0x378(%rbp), %rdi
 2c09042: e8 79 3e ff ff               	callq	0x2bfcec0 <CAppManagerComm::getLanguageChangeStandby()>
 2c09047: 48 8b bd 98 fc ff ff         	movq	-0x368(%rbp), %rdi
 2c0904e: e8 1d e2 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c09053: 48 8b bd 90 fc ff ff         	movq	-0x370(%rbp), %rdi
 2c0905a: e8 31 58 84 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2c0905f: 0f b6 05 5b 85 26 05         	movzbl	0x526855b(%rip), %eax   # 0x7e715c1 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::alreadySendSignal>
 2c09066: 48 8b 9d 88 fc ff ff         	movq	-0x378(%rbp), %rbx
 2c0906d: 88 43 30                     	movb	%al, 0x30(%rbx)
 2c09070: 48 8b 45 c8                  	movq	-0x38(%rbp), %rax
 2c09074: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 2c0907d: 0f 85 41 01 00 00            	jne	0x2c091c4 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x714>
 2c09083: 48 8d 65 d8                  	leaq	-0x28(%rbp), %rsp
 2c09087: 5b                           	popq	%rbx
 2c09088: 41 5c                        	popq	%r12
 2c0908a: 41 5d                        	popq	%r13
 2c0908c: 41 5e                        	popq	%r14
 2c0908e: 41 5f                        	popq	%r15
 2c09090: 5d                           	popq	%rbp
 2c09091: c3                           	retq
 2c09092: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 2c09098: 4c 8d 05 d1 45 3b 03         	leaq	0x33b45d1(%rip), %r8    # 0x5fbd670 <typeinfo name for CAppModeInfoImpl+0x15a0>
 2c0909f: 48 8d 15 da ef 3b 03         	leaq	0x33befda(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c090a6: 48 8d 35 3b 30 3b 03         	leaq	0x33b303b(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2c090ad: b9 83 19 00 00               	movl	$0x1983, %ecx           # imm = 0x1983
 2c090b2: bf 02 00 00 00               	movl	$0x2, %edi
 2c090b7: 31 c0                        	xorl	%eax, %eax
 2c090b9: e8 72 6c c0 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 2c090be: eb 9f                        	jmp	0x2c0905f <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x5af>
 2c090c0: 4c 8d b5 30 fe ff ff         	leaq	-0x1d0(%rbp), %r14
 2c090c7: 48 8d 15 b2 ef 3b 03         	leaq	0x33befb2(%rip), %rdx   # 0x5fc8080 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()::__func__>
 2c090ce: b9 79 19 00 00               	movl	$0x1979, %ecx           # imm = 0x1979
 2c090d3: be 02 00 00 00               	movl	$0x2, %esi
 2c090d8: 4c 89 f7                     	movq	%r14, %rdi
 2c090db: e8 20 5a c0 ff               	callq	0x280eb00 <ExSLStreamLogger::ExSLStreamLogger(ecExSLLogLevel, char const*, unsigned int)>
 2c090e0: 48 8d 35 31 45 3b 03         	leaq	0x33b4531(%rip), %rsi   # 0x5fbd618 <typeinfo name for CAppModeInfoImpl+0x1548>
 2c090e7: 4c 89 f7                     	movq	%r14, %rdi
 2c090ea: e8 61 5e c0 ff               	callq	0x280ef50 <ExSLStreamLogger::operator<<(char const*)>
 2c090ef: 4c 89 f7                     	movq	%r14, %rdi
 2c090f2: e8 09 75 c0 ff               	callq	0x2810600 <ExSLStreamLogger::~ExSLStreamLogger()>
 2c090f7: 48 8d 7b 40                  	leaq	0x40(%rbx), %rdi
 2c090fb: 48 c7 85 80 fd ff ff 00 00 00 00     	movq	$0x0, -0x280(%rbp)
 2c09106: 48 c7 85 88 fd ff ff 00 00 00 00     	movq	$0x0, -0x278(%rbp)
 2c09111: 48 c7 85 90 fd ff ff 00 00 00 00     	movq	$0x0, -0x270(%rbp)
 2c0911c: 48 c7 85 98 fd ff ff 00 00 00 00     	movq	$0x0, -0x268(%rbp)
 2c09127: 48 c7 85 a0 fd ff ff 00 00 00 00     	movq	$0x0, -0x260(%rbp)
 2c09132: 48 c7 85 a8 fd ff ff 00 00 00 00     	movq	$0x0, -0x258(%rbp)
 2c0913d: 48 c7 85 b0 fd ff ff 00 00 00 00     	movq	$0x0, -0x250(%rbp)
 2c09148: 48 c7 85 b8 fd ff ff 00 00 00 00     	movq	$0x0, -0x248(%rbp)
 2c09153: 48 c7 85 c0 fd ff ff 00 00 00 00     	movq	$0x0, -0x240(%rbp)
 2c0915e: c7 85 70 fd ff ff 00 00 00 00	movl	$0x0, -0x290(%rbp)
 2c09168: 48 c7 85 78 fd ff ff 00 00 00 00     	movq	$0x0, -0x288(%rbp)
 2c09173: e8 e8 9d fd ff               	callq	0x2be2f60 <std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>>>>::clear() (.constprop.129)>
 2c09178: 48 89 de                     	movq	%rbx, %rsi
 2c0917b: 4c 89 e7                     	movq	%r12, %rdi
 2c0917e: e8 5d 82 09 ff               	callq	0x1ca13e0 <NaviAdapter::ExternalParameter::ExternalParameter(NaviAdapter::ExternalParameter const&)>
 2c09183: 4c 89 ea                     	movq	%r13, %rdx
 2c09186: 4c 89 e6                     	movq	%r12, %rsi
 2c09189: bf 46 00 00 00               	movl	$0x46, %edi
 2c0918e: e8 cd d4 66 ff               	callq	0x2276660 <NaviAdapter::Telematics::sendExternalMessage(NaviAdapter::Telematics::eMessageId, NaviAdapter::ExternalParameter, int&)>
 2c09193: 4c 89 e7                     	movq	%r12, %rdi
 2c09196: e8 d5 e0 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c0919b: 48 89 df                     	movq	%rbx, %rdi
 2c0919e: e8 cd e0 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c091a3: e9 93 fe ff ff               	jmp	0x2c0903b <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x58b>
 2c091a8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
 2c091b0: 41 89 c1                     	movl	%eax, %r9d
 2c091b3: 4c 8d 05 fe c6 3b 03         	leaq	0x33bc6fe(%rip), %r8    # 0x5fc58b8 <typeinfo name for CAppModeInfoImpl+0x97e8>
 2c091ba: b9 71 19 00 00               	movl	$0x1971, %ecx           # imm = 0x1971
 2c091bf: e9 25 fe ff ff               	jmp	0x2c08fe9 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x539>
 2c091c4: e8 c7 19 84 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 2c091c9: 49 89 c4                     	movq	%rax, %r12
 2c091cc: 48 89 df                     	movq	%rbx, %rdi
 2c091cf: 4c 89 e3                     	movq	%r12, %rbx
 2c091d2: e8 99 e0 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c091d7: 48 8b bd 98 fc ff ff         	movq	-0x368(%rbp), %rdi
 2c091de: e8 8d e0 f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c091e3: 48 8b bd 90 fc ff ff         	movq	-0x370(%rbp), %rdi
 2c091ea: e8 a1 56 84 fe               	callq	0x144e890 <_ZN12QDBusMessageD1Ev@plt>
 2c091ef: 48 89 df                     	movq	%rbx, %rdi
 2c091f2: e8 69 40 84 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2c091f7: 4c 89 f7                     	movq	%r14, %rdi
 2c091fa: 48 89 c3                     	movq	%rax, %rbx
 2c091fd: e8 fe 73 c0 ff               	callq	0x2810600 <ExSLStreamLogger::~ExSLStreamLogger()>
 2c09202: eb d3                        	jmp	0x2c091d7 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x727>
 2c09204: 49 89 c7                     	movq	%rax, %r15
 2c09207: 48 8d 85 e0 fc ff ff         	leaq	-0x320(%rbp), %rax
 2c0920e: 4c 8d b5 f0 fc ff ff         	leaq	-0x310(%rbp), %r14
 2c09215: 48 89 85 90 fc ff ff         	movq	%rax, -0x370(%rbp)
 2c0921c: 48 8b bd 90 fc ff ff         	movq	-0x370(%rbp), %rdi
 2c09223: e8 98 3f 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c09228: 4c 89 f7                     	movq	%r14, %rdi
 2c0922b: e8 90 3f 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c09230: 4c 89 ef                     	movq	%r13, %rdi
 2c09233: e8 88 3f 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c09238: 48 8b bd 98 fc ff ff         	movq	-0x368(%rbp), %rdi
 2c0923f: e8 7c 3f 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c09244: 48 89 df                     	movq	%rbx, %rdi
 2c09247: e8 74 3f 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c0924c: 4c 89 e7                     	movq	%r12, %rdi
 2c0924f: e8 6c 3f 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c09254: 4c 89 ff                     	movq	%r15, %rdi
 2c09257: e8 04 40 84 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2c0925c: 48 8b bd 80 fc ff ff         	movq	-0x380(%rbp), %rdi
 2c09263: be 10 00 00 00               	movl	$0x10, %esi
 2c09268: 49 89 c6                     	movq	%rax, %r14
 2c0926b: e8 30 39 84 fe               	callq	0x144cba0 <_ZdlPvm@plt>
 2c09270: 4c 89 ef                     	movq	%r13, %rdi
 2c09273: 4d 89 f5                     	movq	%r14, %r13
 2c09276: e8 35 46 84 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2c0927b: 4c 89 e7                     	movq	%r12, %rdi
 2c0927e: 4d 89 ec                     	movq	%r13, %r12
 2c09281: e8 ba a7 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c09286: 48 89 df                     	movq	%rbx, %rdi
 2c09289: 4c 89 e3                     	movq	%r12, %rbx
 2c0928c: e8 af a7 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c09291: 48 8b bd 98 fc ff ff         	movq	-0x368(%rbp), %rdi
 2c09298: e8 a3 a7 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0929d: 48 89 df                     	movq	%rbx, %rdi
 2c092a0: e8 bb 3f 84 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2c092a5: 49 89 c5                     	movq	%rax, %r13
 2c092a8: 4c 89 e7                     	movq	%r12, %rdi
 2c092ab: e8 c0 df f9 fe               	callq	0x1ba7270 <NaviAdapter::ExternalParameter::~ExternalParameter()>
 2c092b0: 4d 89 ec                     	movq	%r13, %r12
 2c092b3: e9 14 ff ff ff               	jmp	0x2c091cc <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x71c>
 2c092b8: e9 0c ff ff ff               	jmp	0x2c091c9 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x719>
 2c092bd: 48 8d 95 e0 fc ff ff         	leaq	-0x320(%rbp), %rdx
 2c092c4: 4c 8d b5 f0 fc ff ff         	leaq	-0x310(%rbp), %r14
 2c092cb: 48 89 95 90 fc ff ff         	movq	%rdx, -0x370(%rbp)
 2c092d2: 48 8b bd 70 fc ff ff         	movq	-0x390(%rbp), %rdi
 2c092d9: 48 89 85 88 fc ff ff         	movq	%rax, -0x378(%rbp)
 2c092e0: e8 db 3e 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c092e5: 48 8b 85 88 fc ff ff         	movq	-0x378(%rbp), %rax
 2c092ec: 4c 89 ff                     	movq	%r15, %rdi
 2c092ef: 48 89 85 88 fc ff ff         	movq	%rax, -0x378(%rbp)
 2c092f6: e8 c5 3e 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c092fb: 48 8b 85 88 fc ff ff         	movq	-0x378(%rbp), %rax
 2c09302: 49 89 c7                     	movq	%rax, %r15
 2c09305: e9 12 ff ff ff               	jmp	0x2c0921c <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x76c>
 2c0930a: 48 8d 95 e0 fc ff ff         	leaq	-0x320(%rbp), %rdx
 2c09311: 4c 8d b5 f0 fc ff ff         	leaq	-0x310(%rbp), %r14
 2c09318: 48 89 95 90 fc ff ff         	movq	%rdx, -0x370(%rbp)
 2c0931f: eb cb                        	jmp	0x2c092ec <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x83c>
 2c09321: 49 89 c4                     	movq	%rax, %r12
 2c09324: e9 5d ff ff ff               	jmp	0x2c09286 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x7d6>
 2c09329: 48 89 c3                     	movq	%rax, %rbx
 2c0932c: e9 60 ff ff ff               	jmp	0x2c09291 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x7e1>
 2c09331: 48 89 c3                     	movq	%rax, %rbx
 2c09334: 4c 89 e7                     	movq	%r12, %rdi
 2c09337: e8 04 a7 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c0933c: 48 89 df                     	movq	%rbx, %rdi
 2c0933f: e8 1c 3f 84 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2c09344: 48 8b bd 78 fc ff ff         	movq	-0x388(%rbp), %rdi
 2c0934b: 48 89 85 88 fc ff ff         	movq	%rax, -0x378(%rbp)
 2c09352: e8 e9 a6 f6 ff               	callq	0x2b73a40 <QString::~QString()>
 2c09357: 48 8b 85 88 fc ff ff         	movq	-0x378(%rbp), %rax
 2c0935e: e9 6f ff ff ff               	jmp	0x2c092d2 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x822>
 2c09363: 49 89 c6                     	movq	%rax, %r14
 2c09366: e9 05 ff ff ff               	jmp	0x2c09270 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x7c0>
 2c0936b: 49 89 c5                     	movq	%rax, %r13
 2c0936e: e9 08 ff ff ff               	jmp	0x2c0927b <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x7cb>
 2c09373: 4c 89 ef                     	movq	%r13, %rdi
 2c09376: 48 89 c3                     	movq	%rax, %rbx
 2c09379: e8 42 3e 84 fe               	callq	0x144d1c0 <_ZN8QVariantD1Ev@plt>
 2c0937e: e9 60 fe ff ff               	jmp	0x2c091e3 <CAppManagerComm::SendToAppLauncherNaviLaunchedToExcute()+0x733>
