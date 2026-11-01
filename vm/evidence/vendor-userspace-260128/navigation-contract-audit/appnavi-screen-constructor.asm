
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

000000000335b080 <NimoExSLScreenLinux::NimoExSLScreenLinux(ecScreenId, exSize_t<int>)>:
 335b080: 41 55                        	pushq	%r13
 335b082: 41 54                        	pushq	%r12
 335b084: 49 89 d5                     	movq	%rdx, %r13
 335b087: 55                           	pushq	%rbp
 335b088: 53                           	pushq	%rbx
 335b089: 48 89 fb                     	movq	%rdi, %rbx
 335b08c: 48 8d 6b 28                  	leaq	0x28(%rbx), %rbp
 335b090: 41 89 f4                     	movl	%esi, %r12d
 335b093: 31 f6                        	xorl	%esi, %esi
 335b095: 48 83 ec 48                  	subq	$0x48, %rsp
 335b099: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 335b0a2: 48 89 44 24 38               	movq	%rax, 0x38(%rsp)
 335b0a7: 31 c0                        	xorl	%eax, %eax
 335b0a9: e8 02 20 0f fe               	callq	0x144d0b0 <_ZN10QQuickViewC2EP7QWindow@plt>
 335b0ae: 4c 89 ea                     	movq	%r13, %rdx
 335b0b1: 44 89 e6                     	movl	%r12d, %esi
 335b0b4: 48 89 ef                     	movq	%rbp, %rdi
 335b0b7: e8 44 d0 00 00               	callq	0x3368100 <NimoExSLScreen::NimoExSLScreen(ecScreenId, exSize_t<int>)>
 335b0bc: 48 8d 05 a5 c1 22 04         	leaq	0x422c1a5(%rip), %rax   # 0x7587268 <vtable for NimoExSLScreenLinux>
 335b0c3: c6 83 63 01 00 00 00         	movb	$0x0, 0x163(%rbx)
 335b0ca: be 01 00 00 00               	movl	$0x1, %esi
 335b0cf: c7 83 64 01 00 00 00 00 00 00	movl	$0x0, 0x164(%rbx)
 335b0d9: c7 83 68 01 00 00 00 00 00 00	movl	$0x0, 0x168(%rbx)
 335b0e3: 48 89 df                     	movq	%rbx, %rdi
 335b0e6: c7 83 6c 01 00 00 00 00 00 00	movl	$0x0, 0x16c(%rbx)
 335b0f0: c7 83 70 01 00 00 ff ff ff ff	movl	$0xffffffff, 0x170(%rbx) # imm = 0xFFFFFFFF
 335b0fa: 48 8d 50 10                  	leaq	0x10(%rax), %rdx
 335b0fe: c7 83 74 01 00 00 ff ff ff ff	movl	$0xffffffff, 0x174(%rbx) # imm = 0xFFFFFFFF
 335b108: c7 83 78 01 00 00 00 00 00 00	movl	$0x0, 0x178(%rbx)
 335b112: 48 c7 83 80 01 00 00 00 00 00 00     	movq	$0x0, 0x180(%rbx)
 335b11d: c7 83 90 01 00 00 ff ff ff ff	movl	$0xffffffff, 0x190(%rbx) # imm = 0xFFFFFFFF
 335b127: 48 89 13                     	movq	%rdx, (%rbx)
 335b12a: 48 8d 90 98 01 00 00         	leaq	0x198(%rax), %rdx
 335b131: 48 05 d8 01 00 00            	addq	$0x1d8, %rax            # imm = 0x1D8
 335b137: 48 89 43 28                  	movq	%rax, 0x28(%rbx)
 335b13b: c6 83 94 01 00 00 00         	movb	$0x0, 0x194(%rbx)
 335b142: 48 89 53 10                  	movq	%rdx, 0x10(%rbx)
 335b146: c7 83 98 01 00 00 ff ff ff ff	movl	$0xffffffff, 0x198(%rbx) # imm = 0xFFFFFFFF
 335b150: c7 83 9c 01 00 00 ff ff ff ff	movl	$0xffffffff, 0x19c(%rbx) # imm = 0xFFFFFFFF
 335b15a: c7 83 a0 01 00 00 00 00 00 00	movl	$0x0, 0x1a0(%rbx)
 335b164: 48 c7 83 a8 01 00 00 00 00 00 00     	movq	$0x0, 0x1a8(%rbx)
 335b16f: c7 83 b0 01 00 00 00 00 00 00	movl	$0x0, 0x1b0(%rbx)
 335b179: c7 83 b4 01 00 00 00 00 00 00	movl	$0x0, 0x1b4(%rbx)
 335b183: c7 83 b8 01 00 00 00 00 00 00	movl	$0x0, 0x1b8(%rbx)
 335b18d: 48 c7 83 c0 01 00 00 00 00 00 00     	movq	$0x0, 0x1c0(%rbx)
 335b198: c7 83 c8 01 00 00 00 00 00 00	movl	$0x0, 0x1c8(%rbx)
 335b1a2: e8 19 ff 0e fe               	callq	0x144b0c0 <_ZN10QQuickView13setResizeModeENS_10ResizeModeE@plt>
 335b1a7: 8b 43 34                     	movl	0x34(%rbx), %eax
 335b1aa: 8d 50 ff                     	leal	-0x1(%rax), %edx
 335b1ad: 83 fa 01                     	cmpl	$0x1, %edx
 335b1b0: 76 2e                        	jbe	0x335b1e0 <NimoExSLScreenLinux::NimoExSLScreenLinux(ecScreenId, exSize_t<int>)+0x160>
 335b1b2: 83 f8 04                     	cmpl	$0x4, %eax
 335b1b5: 74 29                        	je	0x335b1e0 <NimoExSLScreenLinux::NimoExSLScreenLinux(ecScreenId, exSize_t<int>)+0x160>
 335b1b7: 48 8b 44 24 38               	movq	0x38(%rsp), %rax
 335b1bc: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 335b1c5: 0f 85 ce 00 00 00            	jne	0x335b299 <NimoExSLScreenLinux::NimoExSLScreenLinux(ecScreenId, exSize_t<int>)+0x219>
 335b1cb: 48 83 c4 48                  	addq	$0x48, %rsp
 335b1cf: 5b                           	popq	%rbx
 335b1d0: 5d                           	popq	%rbp
 335b1d1: 41 5c                        	popq	%r12
 335b1d3: 41 5d                        	popq	%r13
 335b1d5: c3                           	retq
 335b1d6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 335b1e0: 4c 8d 05 a3 cc d5 02         	leaq	0x2d5cca3(%rip), %r8    # 0x60b7e8a <CPersistenceComm::Initialize()::__func__+0x1002>
 335b1e7: 48 8d 15 b7 cc d5 02         	leaq	0x2d5ccb7(%rip), %rdx   # 0x60b7ea5 <CPersistenceComm::Initialize()::__func__+0x101d>
 335b1ee: 41 b9 01 00 00 00            	movl	$0x1, %r9d
 335b1f4: 48 89 d9                     	movq	%rbx, %rcx
 335b1f7: 48 89 de                     	movq	%rbx, %rsi
 335b1fa: 48 89 e7                     	movq	%rsp, %rdi
 335b1fd: e8 2e ff 0e fe               	callq	0x144b130 <_ZN7QObject7connectEPKS_PKcS1_S3_N2Qt14ConnectionTypeE@plt>
 335b202: 48 89 e7                     	movq	%rsp, %rdi
 335b205: 4c 8d 64 24 10               	leaq	0x10(%rsp), %r12
 335b20a: e8 c1 2b 0f fe               	callq	0x144ddd0 <_ZN11QMetaObject10ConnectionD1Ev@plt>
 335b20f: 4c 8d 05 a8 cc d5 02         	leaq	0x2d5cca8(%rip), %r8    # 0x60b7ebe <CPersistenceComm::Initialize()::__func__+0x1036>
 335b216: 48 8d 15 bc cc d5 02         	leaq	0x2d5ccbc(%rip), %rdx   # 0x60b7ed9 <CPersistenceComm::Initialize()::__func__+0x1051>
 335b21d: 41 b9 01 00 00 00            	movl	$0x1, %r9d
 335b223: 48 89 d9                     	movq	%rbx, %rcx
 335b226: 48 89 de                     	movq	%rbx, %rsi
 335b229: 4c 89 e7                     	movq	%r12, %rdi
 335b22c: e8 ff fe 0e fe               	callq	0x144b130 <_ZN7QObject7connectEPKS_PKcS1_S3_N2Qt14ConnectionTypeE@plt>
 335b231: 4c 89 e7                     	movq	%r12, %rdi
 335b234: 4c 8d 64 24 20               	leaq	0x20(%rsp), %r12
 335b239: e8 92 2b 0f fe               	callq	0x144ddd0 <_ZN11QMetaObject10ConnectionD1Ev@plt>
 335b23e: 4c 8d 05 ad cc d5 02         	leaq	0x2d5ccad(%rip), %r8    # 0x60b7ef2 <CPersistenceComm::Initialize()::__func__+0x106a>
 335b245: 48 8d 15 bb cc d5 02         	leaq	0x2d5ccbb(%rip), %rdx   # 0x60b7f07 <CPersistenceComm::Initialize()::__func__+0x107f>
 335b24c: 41 b9 01 00 00 00            	movl	$0x1, %r9d
 335b252: 48 89 d9                     	movq	%rbx, %rcx
 335b255: 48 89 de                     	movq	%rbx, %rsi
 335b258: 4c 89 e7                     	movq	%r12, %rdi
 335b25b: e8 d0 fe 0e fe               	callq	0x144b130 <_ZN7QObject7connectEPKS_PKcS1_S3_N2Qt14ConnectionTypeE@plt>
 335b260: 4c 89 e7                     	movq	%r12, %rdi
 335b263: 4c 8d 64 24 30               	leaq	0x30(%rsp), %r12
 335b268: e8 63 2b 0f fe               	callq	0x144ddd0 <_ZN11QMetaObject10ConnectionD1Ev@plt>
 335b26d: 4c 8d 05 a6 cc d5 02         	leaq	0x2d5cca6(%rip), %r8    # 0x60b7f1a <CPersistenceComm::Initialize()::__func__+0x1092>
 335b274: 48 8d 15 b7 cc d5 02         	leaq	0x2d5ccb7(%rip), %rdx   # 0x60b7f32 <CPersistenceComm::Initialize()::__func__+0x10aa>
 335b27b: 45 31 c9                     	xorl	%r9d, %r9d
 335b27e: 48 89 d9                     	movq	%rbx, %rcx
 335b281: 48 89 de                     	movq	%rbx, %rsi
 335b284: 4c 89 e7                     	movq	%r12, %rdi
 335b287: e8 a4 fe 0e fe               	callq	0x144b130 <_ZN7QObject7connectEPKS_PKcS1_S3_N2Qt14ConnectionTypeE@plt>
 335b28c: 4c 89 e7                     	movq	%r12, %rdi
 335b28f: e8 3c 2b 0f fe               	callq	0x144ddd0 <_ZN11QMetaObject10ConnectionD1Ev@plt>
 335b294: e9 1e ff ff ff               	jmp	0x335b1b7 <NimoExSLScreenLinux::NimoExSLScreenLinux(ecScreenId, exSize_t<int>)+0x137>
 335b299: e8 f2 f8 0e fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 335b29e: 49 89 c4                     	movq	%rax, %r12
 335b2a1: 48 89 ef                     	movq	%rbp, %rdi
 335b2a4: 4c 89 e5                     	movq	%r12, %rbp
 335b2a7: e8 e4 bc 00 00               	callq	0x3366f90 <NimoExSLScreen::~NimoExSLScreen()>
 335b2ac: 48 89 df                     	movq	%rbx, %rdi
 335b2af: e8 cc f9 0e fe               	callq	0x144ac80 <_ZN10QQuickViewD2Ev@plt>
 335b2b4: 48 89 ef                     	movq	%rbp, %rdi
 335b2b7: e8 a4 1f 0f fe               	callq	0x144d260 <_Unwind_Resume@plt>
 335b2bc: 48 89 c5                     	movq	%rax, %rbp
 335b2bf: eb eb                        	jmp	0x335b2ac <NimoExSLScreenLinux::NimoExSLScreenLinux(ecScreenId, exSize_t<int>)+0x22c>
 335b2c1: 90                           	nop
 335b2c2: 0f 1f 40 00                  	nopl	(%rax)
 335b2c6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
