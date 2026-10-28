
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

00000000033712a0 <NimoExSLScreen::onForeground(bool, bool)>:
 33712a0: 41 54                        	pushq	%r12
 33712a2: 55                           	pushq	%rbp
 33712a3: 31 d2                        	xorl	%edx, %edx
 33712a5: 53                           	pushq	%rbx
 33712a6: 89 f5                        	movl	%esi, %ebp
 33712a8: 40 0f b6 f6                  	movzbl	%sil, %esi
 33712ac: 48 89 fb                     	movq	%rdi, %rbx
 33712af: 48 83 ec 10                  	subq	$0x10, %rsp
 33712b3: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 33712bc: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 33712c1: 31 c0                        	xorl	%eax, %eax
 33712c3: e8 68 64 29 ff               	callq	0x2607730 <ExSLScreen::onForeground(bool, bool)>
 33712c8: 84 c0                        	testb	%al, %al
 33712ca: 41 89 c4                     	movl	%eax, %r12d
 33712cd: 74 22                        	je	0x33712f1 <NimoExSLScreen::onForeground(bool, bool)+0x51>
 33712cf: 40 84 ed                     	testb	%bpl, %bpl
 33712d2: 74 5c                        	je	0x3371330 <NimoExSLScreen::onForeground(bool, bool)+0x90>
 33712d4: e8 17 bc 91 fe               	callq	0x1c8cef0 <CServiceShareData::getInstance()>
 33712d9: c6 80 a0 a0 04 00 01         	movb	$0x1, 0x4a0a0(%rax)
 33712e0: 48 8b 03                     	movq	(%rbx), %rax
 33712e3: be 02 00 00 00               	movl	$0x2, %esi
 33712e8: 48 89 df                     	movq	%rbx, %rdi
 33712eb: ff 90 f0 00 00 00            	callq	*0xf0(%rax)
 33712f1: 31 f6                        	xorl	%esi, %esi
 33712f3: 48 89 df                     	movq	%rbx, %rdi
 33712f6: e8 95 84 ff ff               	callq	0x3369790 <NimoExSLScreen::setRequestNaviHide(bool)>
 33712fb: 40 84 ed                     	testb	%bpl, %bpl
 33712fe: 74 06                        	je	0x3371306 <NimoExSLScreen::onForeground(bool, bool)+0x66>
 3371300: 83 7b 0c 01                  	cmpl	$0x1, 0xc(%rbx)
 3371304: 74 7a                        	je	0x3371380 <NimoExSLScreen::onForeground(bool, bool)+0xe0>
 3371306: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
 337130b: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 3371314: 44 89 e0                     	movl	%r12d, %eax
 3371317: 0f 85 8a 00 00 00            	jne	0x33713a7 <NimoExSLScreen::onForeground(bool, bool)+0x107>
 337131d: 48 83 c4 10                  	addq	$0x10, %rsp
 3371321: 5b                           	popq	%rbx
 3371322: 5d                           	popq	%rbp
 3371323: 41 5c                        	popq	%r12
 3371325: c3                           	retq
 3371326: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
 3371330: 48 8b 7b 20                  	movq	0x20(%rbx), %rdi
 3371334: 48 8b 07                     	movq	(%rdi), %rax
 3371337: ff 50 20                     	callq	*0x20(%rax)
 337133a: 48 85 c0                     	testq	%rax, %rax
 337133d: 74 08                        	je	0x3371347 <NimoExSLScreen::onForeground(bool, bool)+0xa7>
 337133f: 48 89 c7                     	movq	%rax, %rdi
 3371342: e8 89 0c 7e fe               	callq	0x1b51fd0 <NimoExSLScene::dispatchTouchCancel()>
 3371347: 83 7b 0c 01                  	cmpl	$0x1, 0xc(%rbx)
 337134b: 75 93                        	jne	0x33712e0 <NimoExSLScreen::onForeground(bool, bool)+0x40>
 337134d: 31 f6                        	xorl	%esi, %esi
 337134f: ba 01 00 00 00               	movl	$0x1, %edx
 3371354: 48 89 df                     	movq	%rbx, %rdi
 3371357: e8 64 fe ff ff               	callq	0x33711c0 <NimoExSLScreen::statusbarDimRequest(bool, bool)>
 337135c: e8 7f 91 83 fe               	callq	0x1baa4e0 <SystemVariant::GetInstance()>
 3371361: 48 89 c7                     	movq	%rax, %rdi
 3371364: e8 27 c2 83 fe               	callq	0x1bad590 <SystemVariant::getPlatformCode()>
 3371369: 83 f8 09                     	cmpl	$0x9, %eax
 337136c: 74 27                        	je	0x3371395 <NimoExSLScreen::onForeground(bool, bool)+0xf5>
 337136e: c6 83 a4 00 00 00 00         	movb	$0x0, 0xa4(%rbx)
 3371375: e9 66 ff ff ff               	jmp	0x33712e0 <NimoExSLScreen::onForeground(bool, bool)+0x40>
 337137a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 3371380: 48 8b 7b 28                  	movq	0x28(%rbx), %rdi
 3371384: ba 01 00 00 00               	movl	$0x1, %edx
 3371389: 31 f6                        	xorl	%esi, %esi
 337138b: e8 50 60 00 00               	callq	0x33773e0 <NimoExSLPopupController::popUniOSD(ecSceneId, bool)>
 3371390: e9 71 ff ff ff               	jmp	0x3371306 <NimoExSLScreen::onForeground(bool, bool)+0x66>
 3371395: be 01 00 00 00               	movl	$0x1, %esi
 337139a: 48 89 df                     	movq	%rbx, %rdi
 337139d: e8 1e 87 ff ff               	callq	0x3369ac0 <NimoExSLScreen::requestStatusbarVisible(bool)>
 33713a2: e9 39 ff ff ff               	jmp	0x33712e0 <NimoExSLScreen::onForeground(bool, bool)+0x40>
 33713a7: e8 e4 97 0d fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 33713ac: 0f 1f 40 00                  	nopl	(%rax)
