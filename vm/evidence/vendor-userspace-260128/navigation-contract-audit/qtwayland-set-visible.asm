
work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/libQt5WaylandClient.so.5.4.1:	file format elf64-x86-64

Disassembly of section .text:

0000000000063ce0 <QWaylandWindow::setVisible(bool)>:
   63ce0: 41 56                        	pushq	%r14
   63ce2: 41 55                        	pushq	%r13
   63ce4: 41 54                        	pushq	%r12
   63ce6: 55                           	pushq	%rbp
   63ce7: 53                           	pushq	%rbx
   63ce8: 48 89 fb                     	movq	%rdi, %rbx
   63ceb: 48 83 ec 20                  	subq	$0x20, %rsp
   63cef: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
   63cf8: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
   63cfd: 31 c0                        	xorl	%eax, %eax
   63cff: 40 84 f6                     	testb	%sil, %sil
   63d02: 74 6c                        	je	0x63d70 <QWaylandWindow::setVisible(bool)+0x90>
   63d04: 48 8d 6f 10                  	leaq	0x10(%rdi), %rbp
   63d08: 48 89 ef                     	movq	%rbp, %rdi
   63d0b: e8 00 be fe ff               	callq	0x4fb10 <_ZNK15QPlatformWindow6windowEv@plt>
   63d10: 48 89 c7                     	movq	%rax, %rdi
   63d13: e8 c8 be fe ff               	callq	0x4fbe0 <_ZNK7QWindow4typeEv@plt>
   63d18: 83 f8 09                     	cmpl	$0x9, %eax
   63d1b: 0f 84 ef 00 00 00            	je	0x63e10 <QWaylandWindow::setVisible(bool)+0x130>
   63d21: 48 8b 03                     	movq	(%rbx), %rax
   63d24: 48 89 ef                     	movq	%rbp, %rdi
   63d27: 4c 8b a0 90 00 00 00         	movq	0x90(%rax), %r12
   63d2e: e8 dd bd fe ff               	callq	0x4fb10 <_ZNK15QPlatformWindow6windowEv@plt>
   63d33: 48 89 c7                     	movq	%rax, %rdi
   63d36: e8 f5 b3 fe ff               	callq	0x4f130 <_ZNK7QWindow8geometryEv@plt>
   63d3b: 48 89 e6                     	movq	%rsp, %rsi
   63d3e: 48 89 df                     	movq	%rbx, %rdi
   63d41: 48 89 04 24                  	movq	%rax, (%rsp)
   63d45: 48 89 54 24 08               	movq	%rdx, 0x8(%rsp)
   63d4a: 41 ff d4                     	callq	*%r12
   63d4d: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
   63d52: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
   63d5b: 0f 85 5b 01 00 00            	jne	0x63ebc <QWaylandWindow::setVisible(bool)+0x1dc>
   63d61: 48 83 c4 20                  	addq	$0x20, %rsp
   63d65: 5b                           	popq	%rbx
   63d66: 5d                           	popq	%rbp
   63d67: 41 5c                        	popq	%r12
   63d69: 41 5d                        	popq	%r13
   63d6b: 41 5e                        	popq	%r14
   63d6d: c3                           	retq
   63d6e: 66 90                        	nop
   63d70: 48 89 e7                     	movq	%rsp, %rdi
   63d73: e8 e8 b0 fe ff               	callq	0x4ee60 <_ZN7QRegionC1Ev@plt>
   63d78: 48 8d 7b 10                  	leaq	0x10(%rbx), %rdi
   63d7c: e8 8f bd fe ff               	callq	0x4fb10 <_ZNK15QPlatformWindow6windowEv@plt>
   63d81: 48 89 e6                     	movq	%rsp, %rsi
   63d84: 48 89 c7                     	movq	%rax, %rdi
   63d87: e8 b4 c9 fe ff               	callq	0x50740 <_ZN22QWindowSystemInterface17handleExposeEventEP7QWindowRK7QRegion@plt>
   63d8c: 48 89 e7                     	movq	%rsp, %rdi
   63d8f: e8 2c c8 fe ff               	callq	0x505c0 <_ZN7QRegionD1Ev@plt>
   63d94: 48 85 db                     	testq	%rbx, %rbx
   63d97: 74 67                        	je	0x63e00 <QWaylandWindow::setVisible(bool)+0x120>
   63d99: 48 89 df                     	movq	%rbx, %rdi
   63d9c: e8 2f cf fe ff               	callq	0x50cd0 <_ZN15QtSharedPointer20ExternalRefCountData9getAndRefEPK7QObject@plt>
   63da1: 31 ff                        	xorl	%edi, %edi
   63da3: 48 89 c5                     	movq	%rax, %rbp
   63da6: e8 35 ca fe ff               	callq	0x507e0 <_ZN22QWindowSystemInterface23flushWindowSystemEventsE6QFlagsIN10QEventLoop17ProcessEventsFlagEE@plt>
   63dab: 48 85 ed                     	testq	%rbp, %rbp
   63dae: 74 9d                        	je	0x63d4d <QWaylandWindow::setVisible(bool)+0x6d>
   63db0: 8b 45 04                     	movl	0x4(%rbp), %eax
   63db3: 85 c0                        	testl	%eax, %eax
   63db5: 74 22                        	je	0x63dd9 <QWaylandWindow::setVisible(bool)+0xf9>
   63db7: 48 8b 03                     	movq	(%rbx), %rax
   63dba: 48 89 df                     	movq	%rbx, %rdi
   63dbd: ff 50 60                     	callq	*0x60(%rax)
   63dc0: 85 c0                        	testl	%eax, %eax
   63dc2: 0f 84 d8 00 00 00            	je	0x63ea0 <QWaylandWindow::setVisible(bool)+0x1c0>
   63dc8: 48 8b bb 00 01 00 00         	movq	0x100(%rbx), %rdi
   63dcf: 48 85 ff                     	testq	%rdi, %rdi
   63dd2: 74 05                        	je	0x63dd9 <QWaylandWindow::setVisible(bool)+0xf9>
   63dd4: e8 97 34 ff ff               	callq	0x57270 <QWaylandShmBackingStore::hidden()>
   63dd9: f0                           	lock
   63dda: 83 6d 00 01                  	subl	$0x1, (%rbp)
   63dde: 0f 95 c0                     	setne	%al
   63de1: 84 c0                        	testb	%al, %al
   63de3: 0f 85 64 ff ff ff            	jne	0x63d4d <QWaylandWindow::setVisible(bool)+0x6d>
   63de9: 48 89 ef                     	movq	%rbp, %rdi
   63dec: e8 4f be fe ff               	callq	0x4fc40 <_ZdlPv@plt>
   63df1: e9 57 ff ff ff               	jmp	0x63d4d <QWaylandWindow::setVisible(bool)+0x6d>
   63df6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
   63e00: 31 ff                        	xorl	%edi, %edi
   63e02: e8 d9 c9 fe ff               	callq	0x507e0 <_ZN22QWindowSystemInterface23flushWindowSystemEventsE6QFlagsIN10QEventLoop17ProcessEventsFlagEE@plt>
   63e07: e9 41 ff ff ff               	jmp	0x63d4d <QWaylandWindow::setVisible(bool)+0x6d>
   63e0c: 0f 1f 40 00                  	nopl	(%rax)
   63e10: 48 89 df                     	movq	%rbx, %rdi
   63e13: e8 38 fe ff ff               	callq	0x63c50 <QWaylandWindow::transientParent() const>
   63e18: 48 85 c0                     	testq	%rax, %rax
   63e1b: 0f 84 00 ff ff ff            	je	0x63d21 <QWaylandWindow::setVisible(bool)+0x41>
   63e21: 48 89 df                     	movq	%rbx, %rdi
   63e24: e8 27 fe ff ff               	callq	0x63c50 <QWaylandWindow::transientParent() const>
   63e29: 48 8b 7b 48                  	movq	0x48(%rbx), %rdi
   63e2d: 4c 8b a0 f0 00 00 00         	movq	0xf0(%rax), %r12
   63e34: 44 8b a8 f8 00 00 00         	movl	0xf8(%rax), %r13d
   63e3b: 4c 89 a3 f0 00 00 00         	movq	%r12, 0xf0(%rbx)
   63e42: 44 89 ab f8 00 00 00         	movl	%r13d, 0xf8(%rbx)
   63e49: 48 85 ff                     	testq	%rdi, %rdi
   63e4c: 0f 84 cf fe ff ff            	je	0x63d21 <QWaylandWindow::setVisible(bool)+0x41>
   63e52: 48 8b 15 6f 4d 2e 00         	movq	0x2e4d6f(%rip), %rdx    # 0x348bc8
   63e59: b9 10 00 00 00               	movl	$0x10, %ecx
   63e5e: 48 8b 35 73 4e 2e 00         	movq	0x2e4e73(%rip), %rsi    # 0x348cd8
   63e65: e8 56 c1 fe ff               	callq	0x4ffc0 <__dynamic_cast@plt>
   63e6a: 49 89 c6                     	movq	%rax, %r14
   63e6d: 4d 85 e4                     	testq	%r12, %r12
   63e70: 0f 84 ab fe ff ff            	je	0x63d21 <QWaylandWindow::setVisible(bool)+0x41>
   63e76: 48 85 c0                     	testq	%rax, %rax
   63e79: 0f 84 a2 fe ff ff            	je	0x63d21 <QWaylandWindow::setVisible(bool)+0x41>
   63e7f: 48 89 df                     	movq	%rbx, %rdi
   63e82: e8 c9 fd ff ff               	callq	0x63c50 <QWaylandWindow::transientParent() const>
   63e87: 44 89 e9                     	movl	%r13d, %ecx
   63e8a: 4c 89 e2                     	movq	%r12, %rdx
   63e8d: 4c 89 f7                     	movq	%r14, %rdi
   63e90: 48 89 c6                     	movq	%rax, %rsi
   63e93: e8 e8 65 00 00               	callq	0x6a480 <QWaylandWlShellSurface::setPopup(QWaylandWindow*, QWaylandInputDevice*, int)>
   63e98: e9 84 fe ff ff               	jmp	0x63d21 <QWaylandWindow::setVisible(bool)+0x41>
   63e9d: 0f 1f 00                     	nopl	(%rax)
   63ea0: 48 89 df                     	movq	%rbx, %rdi
   63ea3: 31 c9                        	xorl	%ecx, %ecx
   63ea5: 31 d2                        	xorl	%edx, %edx
   63ea7: 31 f6                        	xorl	%esi, %esi
   63ea9: e8 e2 f7 ff ff               	callq	0x63690 <QWaylandWindow::attach(QWaylandBuffer*, int, int)>
   63eae: 48 8d 7b 28                  	leaq	0x28(%rbx), %rdi
   63eb2: e8 09 4f 01 00               	callq	0x78dc0 <QtWayland::wl_surface::commit()>
   63eb7: e9 0c ff ff ff               	jmp	0x63dc8 <QWaylandWindow::setVisible(bool)+0xe8>
   63ebc: e8 bf c0 fe ff               	callq	0x4ff80 <__stack_chk_fail@plt>
   63ec1: 0f 1f 44 00 00               	nopl	(%rax,%rax)
   63ec6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
