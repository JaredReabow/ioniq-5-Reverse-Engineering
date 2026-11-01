
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

0000000002bf5250 <CAppManagerComm::SendToAppManagerRegistrationMapFront()>:
 2bf5250: 55                           	pushq	%rbp
 2bf5251: 4c 8d 05 e0 c5 3c 03         	leaq	0x33cc5e0(%rip), %r8    # 0x5fc1838 <typeinfo name for CAppModeInfoImpl+0x5768>
 2bf5258: 48 8d 15 e1 3a 3d 03         	leaq	0x33d3ae1(%rip), %rdx   # 0x5fc8d40 <CAppManagerComm::SendToAppManagerRegistrationMapFront()::__func__>
 2bf525f: 48 8d 35 82 6e 3c 03         	leaq	0x33c6e82(%rip), %rsi   # 0x5fbc0e8 <typeinfo name for CAppModeInfoImpl+0x18>
 2bf5266: b9 e3 01 00 00               	movl	$0x1e3, %ecx            # imm = 0x1E3
 2bf526b: 48 89 e5                     	movq	%rsp, %rbp
 2bf526e: 41 57                        	pushq	%r15
 2bf5270: 41 56                        	pushq	%r14
 2bf5272: 41 55                        	pushq	%r13
 2bf5274: 41 54                        	pushq	%r12
 2bf5276: 49 89 fd                     	movq	%rdi, %r13
 2bf5279: 53                           	pushq	%rbx
 2bf527a: bf 02 00 00 00               	movl	$0x2, %edi
 2bf527f: 48 83 ec 58                  	subq	$0x58, %rsp
 2bf5283: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 2bf528c: 48 89 45 c8                  	movq	%rax, -0x38(%rbp)
 2bf5290: 31 c0                        	xorl	%eax, %eax
 2bf5292: e8 19 a4 c1 ff               	callq	0x280f6b0 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, wchar_t const*, ...)>
 2bf5297: 48 8d 3d ba 35 3c 03         	leaq	0x33c35ba(%rip), %rdi   # 0x5fb8858 <typeinfo name for CAudioControlImpl+0x148>
 2bf529e: be 1e 00 00 00               	movl	$0x1e, %esi
 2bf52a3: e8 f8 8f 85 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 2bf52a8: 48 8d 3d a5 8a 3c 03         	leaq	0x33c8aa5(%rip), %rdi   # 0x5fbdd54 <typeinfo name for CAppModeInfoImpl+0x1c84>
 2bf52af: be 0d 00 00 00               	movl	$0xd, %esi
 2bf52b4: 48 89 45 b0                  	movq	%rax, -0x50(%rbp)
 2bf52b8: e8 e3 8f 85 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 2bf52bd: 48 8d 5d a0                  	leaq	-0x60(%rbp), %rbx
 2bf52c1: 48 89 45 c0                  	movq	%rax, -0x40(%rbp)
 2bf52c5: 48 89 df                     	movq	%rbx, %rdi
 2bf52c8: e8 13 78 85 fe               	callq	0x144cae0 <_ZN15QDBusConnection10sessionBusEv@plt>
 2bf52cd: bf 10 00 00 00               	movl	$0x10, %edi
 2bf52d2: e8 59 8b 85 fe               	callq	0x144de30 <_Znwm@plt>
 2bf52d7: 4c 8d 7d c0                  	leaq	-0x40(%rbp), %r15
 2bf52db: 4c 8d 75 b0                  	leaq	-0x50(%rbp), %r14
 2bf52df: 45 31 c0                     	xorl	%r8d, %r8d
 2bf52e2: 48 89 d9                     	movq	%rbx, %rcx
 2bf52e5: 48 89 c7                     	movq	%rax, %rdi
 2bf52e8: 49 89 c4                     	movq	%rax, %r12
 2bf52eb: 4c 89 fa                     	movq	%r15, %rdx
 2bf52ee: 4c 89 f6                     	movq	%r14, %rsi
 2bf52f1: e8 da 76 6c 00               	callq	0x32bc9d0 <ComLgeAvnAppmanagerRegistrationInterface::ComLgeAvnAppmanagerRegistrationInterface(QString const&, QString const&, QDBusConnection const&, QObject*)>
 2bf52f6: 48 89 df                     	movq	%rbx, %rdi
 2bf52f9: e8 b2 85 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf52fe: 48 8b 7d c0                  	movq	-0x40(%rbp), %rdi
 2bf5302: 8b 07                        	movl	(%rdi), %eax
 2bf5304: 85 c0                        	testl	%eax, %eax
 2bf5306: 0f 85 54 01 00 00            	jne	0x2bf5460 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x210>
 2bf530c: ba 08 00 00 00               	movl	$0x8, %edx
 2bf5311: be 02 00 00 00               	movl	$0x2, %esi
 2bf5316: e8 85 63 85 fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 2bf531b: 48 8b 7d b0                  	movq	-0x50(%rbp), %rdi
 2bf531f: 8b 07                        	movl	(%rdi), %eax
 2bf5321: 85 c0                        	testl	%eax, %eax
 2bf5323: 0f 85 d7 01 00 00            	jne	0x2bf5500 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x2b0>
 2bf5329: ba 08 00 00 00               	movl	$0x8, %edx
 2bf532e: be 02 00 00 00               	movl	$0x2, %esi
 2bf5333: e8 68 63 85 fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 2bf5338: 48 8d 3d a9 35 3b 03         	leaq	0x33b35a9(%rip), %rdi   # 0x5fa88e8 <typeinfo name for NimoLanguageImpl+0x768>
 2bf533f: be 0f 00 00 00               	movl	$0xf, %esi
 2bf5344: e8 57 8f 85 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 2bf5349: 48 8d 3d 3d 75 3b 03         	leaq	0x33b753d(%rip), %rdi   # 0x5fac88d <CNaviVRComm::Initialize()::__func__+0xd5>
 2bf5350: be 18 00 00 00               	movl	$0x18, %esi
 2bf5355: 48 89 45 c0                  	movq	%rax, -0x40(%rbp)
 2bf5359: e8 42 8f 85 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 2bf535e: 48 8d 3d ec a5 1d 03         	leaq	0x31da5ec(%rip), %rdi   # 0x5dcf951 <typeinfo name for NimoExSLMapRenderer+0xf1>
 2bf5365: be 07 00 00 00               	movl	$0x7, %esi
 2bf536a: 48 89 45 b0                  	movq	%rax, -0x50(%rbp)
 2bf536e: e8 2d 8f 85 fe               	callq	0x144e2a0 <_ZN7QString16fromAscii_helperEPKci@plt>
 2bf5373: 48 89 45 a0                  	movq	%rax, -0x60(%rbp)
 2bf5377: 48 83 ec 08                  	subq	$0x8, %rsp
 2bf537b: 48 8d 45 90                  	leaq	-0x70(%rbp), %rax
 2bf537f: 6a 01                        	pushq	$0x1
 2bf5381: 4d 89 f9                     	movq	%r15, %r9
 2bf5384: 4d 89 f0                     	movq	%r14, %r8
 2bf5387: 48 89 d9                     	movq	%rbx, %rcx
 2bf538a: ba 1e 00 00 00               	movl	$0x1e, %edx
 2bf538f: 4c 89 e6                     	movq	%r12, %rsi
 2bf5392: 48 89 c7                     	movq	%rax, %rdi
 2bf5395: 48 89 45 88                  	movq	%rax, -0x78(%rbp)
 2bf5399: e8 02 93 01 00               	callq	0x2c0e6a0 <ComLgeAvnAppmanagerRegistrationInterface::registration(int, QString const&, QString const&, QString const&, int)>
 2bf539e: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 2bf53a2: 58                           	popq	%rax
 2bf53a3: 5a                           	popq	%rdx
 2bf53a4: 8b 07                        	movl	(%rdi), %eax
 2bf53a6: 85 c0                        	testl	%eax, %eax
 2bf53a8: 0f 85 2a 01 00 00            	jne	0x2bf54d8 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x288>
 2bf53ae: ba 08 00 00 00               	movl	$0x8, %edx
 2bf53b3: be 02 00 00 00               	movl	$0x2, %esi
 2bf53b8: e8 e3 62 85 fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 2bf53bd: 48 8b 7d b0                  	movq	-0x50(%rbp), %rdi
 2bf53c1: 8b 07                        	movl	(%rdi), %eax
 2bf53c3: 85 c0                        	testl	%eax, %eax
 2bf53c5: 0f 85 e5 00 00 00            	jne	0x2bf54b0 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x260>
 2bf53cb: ba 08 00 00 00               	movl	$0x8, %edx
 2bf53d0: be 02 00 00 00               	movl	$0x2, %esi
 2bf53d5: e8 c6 62 85 fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 2bf53da: 48 8b 7d c0                  	movq	-0x40(%rbp), %rdi
 2bf53de: 8b 07                        	movl	(%rdi), %eax
 2bf53e0: 85 c0                        	testl	%eax, %eax
 2bf53e2: 0f 85 a0 00 00 00            	jne	0x2bf5488 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x238>
 2bf53e8: ba 08 00 00 00               	movl	$0x8, %edx
 2bf53ed: be 02 00 00 00               	movl	$0x2, %esi
 2bf53f2: e8 a9 62 85 fe               	callq	0x144b6a0 <_ZN10QArrayData10deallocateEPS_mm@plt>
 2bf53f7: bf 18 00 00 00               	movl	$0x18, %edi
 2bf53fc: e8 2f 8a 85 fe               	callq	0x144de30 <_Znwm@plt>
 2bf5401: 4c 8b 7d 88                  	movq	-0x78(%rbp), %r15
 2bf5405: 4c 89 ea                     	movq	%r13, %rdx
 2bf5408: 48 89 c7                     	movq	%rax, %rdi
 2bf540b: 48 89 c3                     	movq	%rax, %rbx
 2bf540e: 4c 89 fe                     	movq	%r15, %rsi
 2bf5411: e8 1a 71 85 fe               	callq	0x144c530 <_ZN23QDBusPendingCallWatcherC1ERK16QDBusPendingCallP7QObject@plt>
 2bf5416: 48 89 df                     	movq	%rbx, %rdi
 2bf5419: e8 02 6a 85 fe               	callq	0x144be20 <_ZN23QDBusPendingCallWatcher15waitForFinishedEv@plt>
 2bf541e: 4c 89 ef                     	movq	%r13, %rdi
 2bf5421: e8 5a f8 ff ff               	callq	0x2bf4c80 <CAppManagerComm::RegisterAllKeyEventFrontMap()>
 2bf5426: 48 89 df                     	movq	%rbx, %rdi
 2bf5429: e8 12 5f 85 fe               	callq	0x144b340 <_ZN7QObject11deleteLaterEv@plt>
 2bf542e: 4c 89 e7                     	movq	%r12, %rdi
 2bf5431: e8 0a 5f 85 fe               	callq	0x144b340 <_ZN7QObject11deleteLaterEv@plt>
 2bf5436: 4c 89 ff                     	movq	%r15, %rdi
 2bf5439: e8 e2 98 85 fe               	callq	0x144ed20 <_ZN21QDBusPendingReplyDataD2Ev@plt>
 2bf543e: 48 8b 45 c8                  	movq	-0x38(%rbp), %rax
 2bf5442: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 2bf544b: 0f 85 d0 00 00 00            	jne	0x2bf5521 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x2d1>
 2bf5451: 48 8d 65 d8                  	leaq	-0x28(%rbp), %rsp
 2bf5455: 5b                           	popq	%rbx
 2bf5456: 41 5c                        	popq	%r12
 2bf5458: 41 5d                        	popq	%r13
 2bf545a: 41 5e                        	popq	%r14
 2bf545c: 41 5f                        	popq	%r15
 2bf545e: 5d                           	popq	%rbp
 2bf545f: c3                           	retq
 2bf5460: 83 f8 ff                     	cmpl	$-0x1, %eax
 2bf5463: 0f 84 b2 fe ff ff            	je	0x2bf531b <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0xcb>
 2bf5469: f0                           	lock
 2bf546a: 83 2f 01                     	subl	$0x1, (%rdi)
 2bf546d: 0f 95 c0                     	setne	%al
 2bf5470: 84 c0                        	testb	%al, %al
 2bf5472: 0f 85 a3 fe ff ff            	jne	0x2bf531b <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0xcb>
 2bf5478: 48 8b 7d c0                  	movq	-0x40(%rbp), %rdi
 2bf547c: e9 8b fe ff ff               	jmp	0x2bf530c <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0xbc>
 2bf5481: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 2bf5488: 83 f8 ff                     	cmpl	$-0x1, %eax
 2bf548b: 0f 84 66 ff ff ff            	je	0x2bf53f7 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x1a7>
 2bf5491: f0                           	lock
 2bf5492: 83 2f 01                     	subl	$0x1, (%rdi)
 2bf5495: 0f 95 c0                     	setne	%al
 2bf5498: 84 c0                        	testb	%al, %al
 2bf549a: 0f 85 57 ff ff ff            	jne	0x2bf53f7 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x1a7>
 2bf54a0: 48 8b 7d c0                  	movq	-0x40(%rbp), %rdi
 2bf54a4: e9 3f ff ff ff               	jmp	0x2bf53e8 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x198>
 2bf54a9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 2bf54b0: 83 f8 ff                     	cmpl	$-0x1, %eax
 2bf54b3: 0f 84 21 ff ff ff            	je	0x2bf53da <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x18a>
 2bf54b9: f0                           	lock
 2bf54ba: 83 2f 01                     	subl	$0x1, (%rdi)
 2bf54bd: 0f 95 c0                     	setne	%al
 2bf54c0: 84 c0                        	testb	%al, %al
 2bf54c2: 0f 85 12 ff ff ff            	jne	0x2bf53da <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x18a>
 2bf54c8: 48 8b 7d b0                  	movq	-0x50(%rbp), %rdi
 2bf54cc: e9 fa fe ff ff               	jmp	0x2bf53cb <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x17b>
 2bf54d1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 2bf54d8: 83 f8 ff                     	cmpl	$-0x1, %eax
 2bf54db: 0f 84 dc fe ff ff            	je	0x2bf53bd <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x16d>
 2bf54e1: f0                           	lock
 2bf54e2: 83 2f 01                     	subl	$0x1, (%rdi)
 2bf54e5: 0f 95 c0                     	setne	%al
 2bf54e8: 84 c0                        	testb	%al, %al
 2bf54ea: 0f 85 cd fe ff ff            	jne	0x2bf53bd <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x16d>
 2bf54f0: 48 8b 7d a0                  	movq	-0x60(%rbp), %rdi
 2bf54f4: e9 b5 fe ff ff               	jmp	0x2bf53ae <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x15e>
 2bf54f9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
 2bf5500: 83 f8 ff                     	cmpl	$-0x1, %eax
 2bf5503: 0f 84 2f fe ff ff            	je	0x2bf5338 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0xe8>
 2bf5509: f0                           	lock
 2bf550a: 83 2f 01                     	subl	$0x1, (%rdi)
 2bf550d: 0f 95 c0                     	setne	%al
 2bf5510: 84 c0                        	testb	%al, %al
 2bf5512: 0f 85 20 fe ff ff            	jne	0x2bf5338 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0xe8>
 2bf5518: 48 8b 7d b0                  	movq	-0x50(%rbp), %rdi
 2bf551c: e9 08 fe ff ff               	jmp	0x2bf5329 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0xd9>
 2bf5521: e8 6a 56 85 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 2bf5526: 49 89 c4                     	movq	%rax, %r12
 2bf5529: 48 89 df                     	movq	%rbx, %rdi
 2bf552c: be 18 00 00 00               	movl	$0x18, %esi
 2bf5531: 4c 89 e3                     	movq	%r12, %rbx
 2bf5534: e8 67 76 85 fe               	callq	0x144cba0 <_ZdlPvm@plt>
 2bf5539: 48 8b 7d 88                  	movq	-0x78(%rbp), %rdi
 2bf553d: e8 de 97 85 fe               	callq	0x144ed20 <_ZN21QDBusPendingReplyDataD2Ev@plt>
 2bf5542: 48 89 df                     	movq	%rbx, %rdi
 2bf5545: e8 16 7d 85 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2bf554a: 48 89 c3                     	movq	%rax, %rbx
 2bf554d: eb ea                        	jmp	0x2bf5539 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x2e9>
 2bf554f: 49 89 c5                     	movq	%rax, %r13
 2bf5552: 48 89 df                     	movq	%rbx, %rdi
 2bf5555: 4c 89 eb                     	movq	%r13, %rbx
 2bf5558: e8 e3 e4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf555d: 4c 89 f7                     	movq	%r14, %rdi
 2bf5560: e8 db e4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf5565: 4c 89 ff                     	movq	%r15, %rdi
 2bf5568: e8 d3 e4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf556d: 48 89 df                     	movq	%rbx, %rdi
 2bf5570: e8 eb 7c 85 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2bf5575: 48 89 c3                     	movq	%rax, %rbx
 2bf5578: eb e3                        	jmp	0x2bf555d <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x30d>
 2bf557a: 48 89 c3                     	movq	%rax, %rbx
 2bf557d: eb e6                        	jmp	0x2bf5565 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x315>
 2bf557f: be 10 00 00 00               	movl	$0x10, %esi
 2bf5584: 4c 89 e7                     	movq	%r12, %rdi
 2bf5587: 49 89 c5                     	movq	%rax, %r13
 2bf558a: e8 11 76 85 fe               	callq	0x144cba0 <_ZdlPvm@plt>
 2bf558f: 48 89 df                     	movq	%rbx, %rdi
 2bf5592: 4c 89 eb                     	movq	%r13, %rbx
 2bf5595: e8 16 83 85 fe               	callq	0x144d8b0 <_ZN15QDBusConnectionD1Ev@plt>
 2bf559a: 4c 89 ff                     	movq	%r15, %rdi
 2bf559d: e8 9e e4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf55a2: 4c 89 f7                     	movq	%r14, %rdi
 2bf55a5: e8 96 e4 f7 ff               	callq	0x2b73a40 <QString::~QString()>
 2bf55aa: 48 89 df                     	movq	%rbx, %rdi
 2bf55ad: e8 ae 7c 85 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 2bf55b2: 49 89 c5                     	movq	%rax, %r13
 2bf55b5: 4c 8d 7d c0                  	leaq	-0x40(%rbp), %r15
 2bf55b9: 4c 8d 75 b0                  	leaq	-0x50(%rbp), %r14
 2bf55bd: eb d0                        	jmp	0x2bf558f <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x33f>
 2bf55bf: 48 89 c3                     	movq	%rax, %rbx
 2bf55c2: 4c 8d 7d c0                  	leaq	-0x40(%rbp), %r15
 2bf55c6: 4c 8d 75 b0                  	leaq	-0x50(%rbp), %r14
 2bf55ca: eb ce                        	jmp	0x2bf559a <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x34a>
 2bf55cc: 48 89 c3                     	movq	%rax, %rbx
 2bf55cf: 4c 8d 75 b0                  	leaq	-0x50(%rbp), %r14
 2bf55d3: eb cd                        	jmp	0x2bf55a2 <CAppManagerComm::SendToAppManagerRegistrationMapFront()+0x352>
 2bf55d5: 90                           	nop
 2bf55d6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
