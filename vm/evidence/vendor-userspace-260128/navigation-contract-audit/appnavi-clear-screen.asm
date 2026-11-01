
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

0000000003368420 <NimoExSLScreen::clearScreen()>:
 3368420: 53                           	pushq	%rbx
 3368421: 48 83 ec 10                  	subq	$0x10, %rsp
 3368425: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 336842e: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 3368433: 31 c0                        	xorl	%eax, %eax
 3368435: 48 8b 47 58                  	movq	0x58(%rdi), %rax
 3368439: 48 85 c0                     	testq	%rax, %rax
 336843c: 0f 84 8e 00 00 00            	je	0x33684d0 <NimoExSLScreen::clearScreen()+0xb0>
 3368442: 48 8b 17                     	movq	(%rdi), %rdx
 3368445: 48 8d 0d 64 e7 ff ff         	leaq	-0x189c(%rip), %rcx     # 0x3366bb0 <NimoExSLScreen::makeCurrent() (.localalias.214)>
 336844c: 48 89 fb                     	movq	%rdi, %rbx
 336844f: 48 8b 92 e0 00 00 00         	movq	0xe0(%rdx), %rdx
 3368456: 48 39 ca                     	cmpq	%rcx, %rdx
 3368459: 0f 85 b1 00 00 00            	jne	0x3368510 <NimoExSLScreen::clearScreen()+0xf0>
 336845f: 48 8b 7f 60                  	movq	0x60(%rdi), %rdi
 3368463: 48 85 ff                     	testq	%rdi, %rdi
 3368466: 74 0a                        	je	0x3368472 <NimoExSLScreen::clearScreen()+0x52>
 3368468: 48 8b 07                     	movq	(%rdi), %rax
 336846b: ff 50 18                     	callq	*0x18(%rax)
 336846e: 48 8b 43 58                  	movq	0x58(%rbx), %rax
 3368472: 8b 4b 10                     	movl	0x10(%rbx), %ecx
 3368475: 44 8b 43 14                  	movl	0x14(%rbx), %r8d
 3368479: 31 d2                        	xorl	%edx, %edx
 336847b: 48 89 c7                     	movq	%rax, %rdi
 336847e: 31 f6                        	xorl	%esi, %esi
 3368480: e8 5b 9e 78 ff               	callq	0x2af22e0 <nimo::Renderer::SetViewPort(int, int, int, int)>
 3368485: 48 8b 7b 58                  	movq	0x58(%rbx), %rdi
 3368489: be 00 41 00 00               	movl	$0x4100, %esi           # imm = 0x4100
 336848e: e8 5d 9d 78 ff               	callq	0x2af21f0 <nimo::Renderer::Clear(unsigned int)>
 3368493: 48 8b 03                     	movq	(%rbx), %rax
 3368496: 48 8d 15 73 e7 ff ff         	leaq	-0x188d(%rip), %rdx     # 0x3366c10 <NimoExSLScreen::swapBuffer() (.localalias.218)>
 336849d: 48 8b 80 e8 00 00 00         	movq	0xe8(%rax), %rax
 33684a4: 48 39 d0                     	cmpq	%rdx, %rax
 33684a7: 75 47                        	jne	0x33684f0 <NimoExSLScreen::clearScreen()+0xd0>
 33684a9: 48 8b 7b 60                  	movq	0x60(%rbx), %rdi
 33684ad: 48 85 ff                     	testq	%rdi, %rdi
 33684b0: 74 1e                        	je	0x33684d0 <NimoExSLScreen::clearScreen()+0xb0>
 33684b2: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 33684b7: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 33684c0: 75 59                        	jne	0x336851b <NimoExSLScreen::clearScreen()+0xfb>
 33684c2: 48 8b 07                     	movq	(%rdi), %rax
 33684c5: 48 8b 40 20                  	movq	0x20(%rax), %rax
 33684c9: 48 83 c4 10                  	addq	$0x10, %rsp
 33684cd: 5b                           	popq	%rbx
 33684ce: ff e0                        	jmpq	*%rax
 33684d0: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 33684d5: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
 33684de: 75 3b                        	jne	0x336851b <NimoExSLScreen::clearScreen()+0xfb>
