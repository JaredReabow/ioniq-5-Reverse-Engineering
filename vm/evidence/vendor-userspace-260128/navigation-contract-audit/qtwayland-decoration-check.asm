
work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/libQt5WaylandClient.so.5.4.1:	file format elf64-x86-64

Disassembly of section .text:

0000000000060b90 <QWaylandDisplay::supportsWindowDecoration() const>:
   60b90: 55                           	pushq	%rbp
   60b91: 48 89 fd                     	movq	%rdi, %rbp
   60b94: 53                           	pushq	%rbx
   60b95: 48 83 ec 18                  	subq	$0x18, %rsp
   60b99: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
   60ba2: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
   60ba7: 31 c0                        	xorl	%eax, %eax
   60ba9: 80 3d a0 8b 2e 00 00         	cmpb	$0x0, 0x2e8ba0(%rip)    # 0x349750 <__bss_start+0x50>
   60bb0: 74 46                        	je	0x60bf8 <QWaylandDisplay::supportsWindowDecoration() const+0x68>
   60bb2: 0f b6 1d 88 8b 2e 00         	movzbl	0x2e8b88(%rip), %ebx    # 0x349741 <__bss_start+0x41>
   60bb9: 84 db                        	testb	%bl, %bl
   60bbb: 75 33                        	jne	0x60bf0 <QWaylandDisplay::supportsWindowDecoration() const+0x60>
   60bbd: 80 3d 84 8b 2e 00 00         	cmpb	$0x0, 0x2e8b84(%rip)    # 0x349748 <__bss_start+0x48>
   60bc4: 0f 84 b6 00 00 00            	je	0x60c80 <QWaylandDisplay::supportsWindowDecoration() const+0xf0>
   60bca: 0f b6 1d 6f 8b 2e 00         	movzbl	0x2e8b6f(%rip), %ebx    # 0x349740 <__bss_start+0x40>
   60bd1: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
   60bd6: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
   60bdf: 89 d8                        	movl	%ebx, %eax
   60be1: 0f 85 f8 00 00 00            	jne	0x60cdf <QWaylandDisplay::supportsWindowDecoration() const+0x14f>
   60be7: 48 83 c4 18                  	addq	$0x18, %rsp
   60beb: 5b                           	popq	%rbx
   60bec: 5d                           	popq	%rbp
   60bed: c3                           	retq
   60bee: 66 90                        	nop
   60bf0: 31 db                        	xorl	%ebx, %ebx
   60bf2: eb dd                        	jmp	0x60bd1 <QWaylandDisplay::supportsWindowDecoration() const+0x41>
   60bf4: 0f 1f 40 00                  	nopl	(%rax)
   60bf8: 48 8d 3d 51 8b 2e 00         	leaq	0x2e8b51(%rip), %rdi    # 0x349750 <__bss_start+0x50>
   60bff: e8 fc fd fe ff               	callq	0x50a00 <__cxa_guard_acquire@plt>
   60c04: 85 c0                        	testl	%eax, %eax
   60c06: 74 aa                        	je	0x60bb2 <QWaylandDisplay::supportsWindowDecoration() const+0x22>
   60c08: 48 8d 35 f9 c2 09 00         	leaq	0x9c2f9(%rip), %rsi     # 0xfcf08 <typeinfo name for QWaylandCursor+0x48>
   60c0f: 48 89 e7                     	movq	%rsp, %rdi
   60c12: e8 a9 fa fe ff               	callq	0x506c0 <_Z7qgetenvPKc@plt>
   60c17: 31 f6                        	xorl	%esi, %esi
   60c19: ba 0a 00 00 00               	movl	$0xa, %edx
   60c1e: 48 89 e7                     	movq	%rsp, %rdi
   60c21: e8 da fe fe ff               	callq	0x50b00 <_ZNK10QByteArray5toIntEPbi@plt>
   60c26: 48 8d 3d 23 8b 2e 00         	leaq	0x2e8b23(%rip), %rdi    # 0x349750 <__bss_start+0x50>
   60c2d: 85 c0                        	testl	%eax, %eax
   60c2f: 0f 95 c3                     	setne	%bl
   60c32: 88 1d 09 8b 2e 00            	movb	%bl, 0x2e8b09(%rip)     # 0x349741 <__bss_start+0x41>
   60c38: e8 43 eb fe ff               	callq	0x4f780 <__cxa_guard_release@plt>
   60c3d: 48 8b 3c 24                  	movq	(%rsp), %rdi
   60c41: 8b 07                        	movl	(%rdi), %eax
   60c43: 85 c0                        	testl	%eax, %eax
   60c45: 74 21                        	je	0x60c68 <QWaylandDisplay::supportsWindowDecoration() const+0xd8>
   60c47: 83 f8 ff                     	cmpl	$-0x1, %eax
   60c4a: 0f 84 69 ff ff ff            	je	0x60bb9 <QWaylandDisplay::supportsWindowDecoration() const+0x29>
   60c50: f0                           	lock
   60c51: 83 2f 01                     	subl	$0x1, (%rdi)
   60c54: 0f 95 c0                     	setne	%al
   60c57: 84 c0                        	testb	%al, %al
   60c59: 0f 85 53 ff ff ff            	jne	0x60bb2 <QWaylandDisplay::supportsWindowDecoration() const+0x22>
   60c5f: 48 8b 3c 24                  	movq	(%rsp), %rdi
   60c63: 0f 1f 44 00 00               	nopl	(%rax,%rax)
   60c68: ba 08 00 00 00               	movl	$0x8, %edx
   60c6d: be 01 00 00 00               	movl	$0x1, %esi
   60c72: e8 c9 f9 fe ff               	callq	0x50640 <_ZN10QArrayData10deallocateEPS_mm@plt>
   60c77: e9 36 ff ff ff               	jmp	0x60bb2 <QWaylandDisplay::supportsWindowDecoration() const+0x22>
   60c7c: 0f 1f 40 00                  	nopl	(%rax)
   60c80: 48 8d 3d c1 8a 2e 00         	leaq	0x2e8ac1(%rip), %rdi    # 0x349748 <__bss_start+0x48>
   60c87: e8 74 fd fe ff               	callq	0x50a00 <__cxa_guard_acquire@plt>
   60c8c: 85 c0                        	testl	%eax, %eax
   60c8e: 0f 84 36 ff ff ff            	je	0x60bca <QWaylandDisplay::supportsWindowDecoration() const+0x3a>
   60c94: 48 89 ef                     	movq	%rbp, %rdi
   60c97: e8 a4 f5 ff ff               	callq	0x60240 <QWaylandDisplay::clientBufferIntegration() const>
   60c9c: 48 85 c0                     	testq	%rax, %rax
   60c9f: 74 27                        	je	0x60cc8 <QWaylandDisplay::supportsWindowDecoration() const+0x138>
   60ca1: 48 89 ef                     	movq	%rbp, %rdi
   60ca4: e8 97 f5 ff ff               	callq	0x60240 <QWaylandDisplay::clientBufferIntegration() const>
   60ca9: 48 8d 0d d0 13 00 00         	leaq	0x13d0(%rip), %rcx      # 0x62080 <non-virtual thunk to QWaylandDisplay::~QWaylandDisplay()+0x10>
   60cb0: 48 8b 10                     	movq	(%rax), %rdx
   60cb3: 48 8b 52 28                  	movq	0x28(%rdx), %rdx
   60cb7: 48 39 ca                     	cmpq	%rcx, %rdx
   60cba: 74 0c                        	je	0x60cc8 <QWaylandDisplay::supportsWindowDecoration() const+0x138>
   60cbc: 48 89 c7                     	movq	%rax, %rdi
   60cbf: ff d2                        	callq	*%rdx
   60cc1: 89 c3                        	movl	%eax, %ebx
   60cc3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
   60cc8: 48 8d 3d 79 8a 2e 00         	leaq	0x2e8a79(%rip), %rdi    # 0x349748 <__bss_start+0x48>
   60ccf: 88 1d 6b 8a 2e 00            	movb	%bl, 0x2e8a6b(%rip)     # 0x349740 <__bss_start+0x40>
   60cd5: e8 a6 ea fe ff               	callq	0x4f780 <__cxa_guard_release@plt>
   60cda: e9 f2 fe ff ff               	jmp	0x60bd1 <QWaylandDisplay::supportsWindowDecoration() const+0x41>
   60cdf: e8 9c f2 fe ff               	callq	0x4ff80 <__stack_chk_fail@plt>
   60ce4: 66 90                        	nop
   60ce6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000060cf0 <QWaylandDisplay::registry_global(unsigned int, QString const&, unsigned int)>:
   60cf0: 41 57                        	pushq	%r15
   60cf2: 49 89 ff                     	movq	%rdi, %r15
   60cf5: 41 56                        	pushq	%r14
   60cf7: 41 55                        	pushq	%r13
   60cf9: 41 89 cd                     	movl	%ecx, %r13d
   60cfc: 41 54                        	pushq	%r12
   60cfe: 55                           	pushq	%rbp
   60cff: 89 f5                        	movl	%esi, %ebp
   60d01: 53                           	pushq	%rbx
   60d02: 48 89 d3                     	movq	%rdx, %rbx
   60d05: 48 83 ec 58                  	subq	$0x58, %rsp
   60d09: 4c 8b 67 18                  	movq	0x18(%rdi), %r12
   60d0d: 48 89 d7                     	movq	%rdx, %rdi
   60d10: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
   60d19: 48 89 44 24 48               	movq	%rax, 0x48(%rsp)
   60d1e: 31 c0                        	xorl	%eax, %eax
   60d20: 4c 8d 74 24 20               	leaq	0x20(%rsp), %r14
   60d25: 48 8d 05 f4 c6 09 00         	leaq	0x9c6f4(%rip), %rax     # 0xfd420 <typeinfo name for QWaylandCursor+0x560>
   60d2c: 4c 89 f6                     	movq	%r14, %rsi
   60d2f: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
   60d34: e8 97 fd fe ff               	callq	0x50ad0 <_ZeqRK7QStringS1_@plt>
   60d39: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
   60d3e: 8b 17                        	movl	(%rdi), %edx
   60d40: 85 d2                        	testl	%edx, %edx
   60d42: 0f 85 d0 01 00 00            	jne	0x60f18 <QWaylandDisplay::registry_global(unsigned int, QString const&, unsigned int)+0x228>
   60d48: ba 08 00 00 00               	movl	$0x8, %edx
   60d4d: be 02 00 00 00               	movl	$0x2, %esi
   60d52: 88 04 24                     	movb	%al, (%rsp)
   60d55: e8 e6 f8 fe ff               	callq	0x50640 <_ZN10QArrayData10deallocateEPS_mm@plt>
   60d5a: 0f b6 04 24                  	movzbl	(%rsp), %eax
   60d5e: 84 c0                        	testb	%al, %al
   60d60: 0f 84 da 01 00 00            	je	0x60f40 <QWaylandDisplay::registry_global(unsigned int, QString const&, unsigned int)+0x250>
   60d66: bf 78 00 00 00               	movl	$0x78, %edi
   60d6b: e8 80 ef fe ff               	callq	0x4fcf0 <_Znwm@plt>
   60d70: 89 e9                        	movl	%ebp, %ecx
   60d72: 44 89 ea                     	movl	%r13d, %edx
   60d75: 4c 89 fe                     	movq	%r15, %rsi
   60d78: 48 89 c7                     	movq	%rax, %rdi
   60d7b: 48 89 04 24                  	movq	%rax, (%rsp)
   60d7f: e8 ec 64 00 00               	callq	0x67270 <QWaylandScreen::QWaylandScreen(QWaylandDisplay*, int, unsigned int)>
   60d84: 49 8b 87 80 00 00 00         	movq	0x80(%r15), %rax
   60d8b: 49 8d bf 80 00 00 00         	leaq	0x80(%r15), %rdi
