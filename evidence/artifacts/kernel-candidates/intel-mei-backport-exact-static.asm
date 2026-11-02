# Intel MEI exact-static backport excerpt
# Source module: canonical EU 260128 mango rootfs /lib/modules/4.1.27-abl/kernel/drivers/misc/mei/mei.ko
# Module SHA-256: 8518715e6e1910aacddf9da116aa97b98e7fca8f14c64da83959c60204d83609
# Build ID: ca127bac6266f1afd1ff48cdd0c0bdcb4a67d643
# Read-only disassembly; no recovered target code was executed.

## mei_cl_irq_read_msg

work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/drivers/misc/mei/mei.ko:	file format elf64-x86-64

Disassembly of section .text:

000000000000228c <mei_cl_irq_read_msg>:
    228c:      	pushq	%rbp
    228d:      	leaq	0xb0(%rdi), %r8
    2294:      	movq	%rsp, %rbp
    2297:      	pushq	%r15
    2299:      	pushq	%r14
    229b:      	pushq	%r13
    229d:      	pushq	%r12
    229f:      	movq	%rsi, %r14
    22a2:      	pushq	%rbx
    22a3:      	movq	%rdi, %r12
    22a6:      	movq	%rdx, %r15
    22a9:      	subq	$0x18, %rsp
    22ad:      	movq	0xb0(%rdi), %rbx
    22b4:      	movq	0x10(%rdi), %r13
    22b8:      	testq	%rbx, %rbx
    22bb:      	je	0x22c2 <mei_cl_irq_read_msg+0x36>
    22bd:      	cmpq	%rbx, %r8
    22c0:      	jne	0x2340 <mei_cl_irq_read_msg+0xb4>
    22c2:      	movq	0x90(%r12), %rax
    22ca:      	testq	%rax, %rax
    22cd:      	je	0x22db <mei_cl_irq_read_msg+0x4f>
    22cf:      	cmpb	$0x0, 0x26(%rax)
    22d3:      	jne	0x22fd <mei_cl_irq_read_msg+0x71>
    22d5:      	movzbl	0x2c(%rax), %ecx
    22d9:      	jmp	0x22dd <mei_cl_irq_read_msg+0x51>
    22db:      	xorl	%ecx, %ecx
    22dd:      	movzbl	0xa0(%r12), %edx
    22e6:      	movq	(%r13), %rdi
    22ea:      	movq	$0x0, %rsi
		00000000000022ed:  R_X86_64_32S	.rodata.str1.1+0xf0c
    22f1:      	xorl	%eax, %eax
    22f3:      	callq	0x22f8 <mei_cl_irq_read_msg+0x6c>
		00000000000022f4:  R_X86_64_PC32	dev_err-0x4
    22f8:      	jmp	0x250c <mei_cl_irq_read_msg+0x280>
    22fd:      	movl	0x28(%rax), %esi
    2300:      	movq	0x98(%r12), %rcx
    2308:      	xorl	%edx, %edx
    230a:      	movq	%r12, %rdi
    230d:      	movq	%r8, -0x38(%rbp)
    2311:      	callq	0x2316 <mei_cl_irq_read_msg+0x8a>
		0000000000002312:  R_X86_64_PC32	mei_cl_alloc_cb-0x4
    2316:      	testq	%rax, %rax
    2319:      	movq	%rax, %rbx
    231c:      	movq	-0x38(%rbp), %r8
    2320:      	je	0x250c <mei_cl_irq_read_msg+0x280>
    2326:      	movq	0xb8(%r12), %rax
    232e:      	movq	%rbx, 0xb8(%r12)
    2336:      	movq	%r8, (%rbx)
    2339:      	movq	%rax, 0x8(%rbx)
    233d:      	movq	%rbx, (%rax)
    2340:      	cmpl	$0x2, 0x18(%r12)
    2346:      	je	0x239f <mei_cl_irq_read_msg+0x113>
    2348:      	testb	$0x4, (%rip)            # 0x234f <mei_cl_irq_read_msg+0xc3>
		000000000000234a:  R_X86_64_PC32	__verbose+0x6d5
    234f:      	je	0x2388 <mei_cl_irq_read_msg+0xfc>
    2351:      	movq	0x90(%r12), %rax
    2359:      	xorl	%r8d, %r8d
    235c:      	testq	%rax, %rax
    235f:      	je	0x2366 <mei_cl_irq_read_msg+0xda>
    2361:      	movzbl	0x2c(%rax), %r8d
    2366:      	movzbl	0xa0(%r12), %ecx
    236f:      	movq	(%r13), %rsi
    2373:      	movq	$0x0, %rdx
		0000000000002376:  R_X86_64_32S	.rodata.str1.1+0xf3c
    237a:      	movq	$0x0, %rdi
		000000000000237d:  R_X86_64_32S	__verbose+0x6b8
    2381:      	xorl	%eax, %eax
    2383:      	callq	0x2388 <mei_cl_irq_read_msg+0xfc>
		0000000000002384:  R_X86_64_PC32	__dynamic_dev_dbg-0x4
    2388:      	movq	%r15, %rsi
    238b:      	movq	%rbx, %rdi
    238e:      	callq	0x1e82 <list_move_tail>
    2393:      	movl	$0xffffffed, 0x40(%rbx) # imm = 0xFFFFFFED
    239a:      	jmp	0x250c <mei_cl_irq_read_msg+0x280>
    239f:      	movzbl	0x3(%r14), %r8d
    23a4:      	movzbl	0x2(%r14), %eax
    23a9:      	movq	0x30(%rbx), %rsi
    23ad:      	andl	$0x1, %r8d
    23b1:      	shlq	$0x8, %r8
    23b5:      	orq	%rax, %r8
    23b8:      	movzwl	%r8w, %edx
    23bc:      	movq	%rdx, %rax
    23bf:      	addq	%rsi, %rax
    23c2:      	jae	0x23fb <mei_cl_irq_read_msg+0x16f>
    23c4:      	movq	0x90(%r12), %rax
    23cc:      	xorl	%ecx, %ecx
    23ce:      	movzwl	%r8w, %r8d
    23d2:      	testq	%rax, %rax
    23d5:      	je	0x23db <mei_cl_irq_read_msg+0x14f>
    23d7:      	movzbl	0x2c(%rax), %ecx
    23db:      	movzbl	0xa0(%r12), %edx
    23e4:      	movq	(%r13), %rdi
    23e8:      	movq	%rsi, %r9
    23eb:      	xorl	%eax, %eax
    23ed:      	movq	$0x0, %rsi
		00000000000023f0:  R_X86_64_32S	.rodata.str1.1+0xf60
    23f4:      	callq	0x23f9 <mei_cl_irq_read_msg+0x16d>
		00000000000023f5:  R_X86_64_PC32	dev_err-0x4
    23f9:      	jmp	0x244e <mei_cl_irq_read_msg+0x1c2>
    23fb:      	movq	0x20(%rbx), %r9
    23ff:      	cmpq	%r9, %rax
    2402:      	jbe	0x2465 <mei_cl_irq_read_msg+0x1d9>
    2404:      	testb	$0x4, (%rip)            # 0x240b <mei_cl_irq_read_msg+0x17f>
		0000000000002406:  R_X86_64_PC32	__verbose+0x6ad
    240b:      	je	0x244e <mei_cl_irq_read_msg+0x1c2>
    240d:      	movq	0x90(%r12), %rdx
    2415:      	xorl	%eax, %eax
    2417:      	movzwl	%r8w, %r8d
    241b:      	testq	%rdx, %rdx
    241e:      	je	0x2423 <mei_cl_irq_read_msg+0x197>
    2420:      	movb	0x2c(%rdx), %al
    2423:      	movzbl	0xa0(%r12), %ecx
    242c:      	pushq	%rsi
    242d:      	movq	$0x0, %rdx
		0000000000002430:  R_X86_64_32S	.rodata.str1.1+0xf98
    2434:      	pushq	%r8
    2436:      	movq	(%r13), %rsi
    243a:      	movzbl	%al, %r8d
    243e:      	movq	$0x0, %rdi
		0000000000002441:  R_X86_64_32S	__verbose+0x690
    2445:      	xorl	%eax, %eax
    2447:      	callq	0x244c <mei_cl_irq_read_msg+0x1c0>
		0000000000002448:  R_X86_64_PC32	__dynamic_dev_dbg-0x4
    244c:      	popq	%rax
    244d:      	popq	%rdx
    244e:      	movq	%r15, %rsi
    2451:      	movq	%rbx, %rdi
    2454:      	callq	0x1e82 <list_move_tail>
    2459:      	movl	$0xffffffa6, 0x40(%rbx) # imm = 0xFFFFFFA6
    2460:      	jmp	0x250c <mei_cl_irq_read_msg+0x280>
    2465:      	movq	0x7c8(%r13), %rax
    246c:      	addq	0x28(%rbx), %rsi
    2470:      	movq	%r13, %rdi
    2473:      	callq	*0x98(%rax)
    2479:      	movzbl	0x3(%r14), %r9d
    247e:      	movzbl	0x2(%r14), %eax
    2483:      	andl	$0x1, %r9d
    2487:      	shlq	$0x8, %r9
    248b:      	orq	%rax, %r9
    248e:      	addq	0x30(%rbx), %r9
    2492:      	movq	%r9, 0x30(%rbx)
    2496:      	cmpb	$0x0, 0x3(%r14)
    249b:      	jns	0x24ea <mei_cl_irq_read_msg+0x25e>
    249d:      	testb	$0x4, (%rip)            # 0x24a4 <mei_cl_irq_read_msg+0x218>
		000000000000249f:  R_X86_64_PC32	__verbose+0x685
    24a4:      	je	0x24dd <mei_cl_irq_read_msg+0x251>
    24a6:      	movq	0x90(%r12), %rax
    24ae:      	xorl	%r8d, %r8d
    24b1:      	testq	%rax, %rax
    24b4:      	je	0x24bb <mei_cl_irq_read_msg+0x22f>
    24b6:      	movzbl	0x2c(%rax), %r8d
    24bb:      	movzbl	0xa0(%r12), %ecx
    24c4:      	movq	(%r13), %rsi
    24c8:      	movq	$0x0, %rdx
		00000000000024cb:  R_X86_64_32S	.rodata.str1.1+0xfd8
    24cf:      	movq	$0x0, %rdi
		00000000000024d2:  R_X86_64_32S	__verbose+0x668
    24d6:      	xorl	%eax, %eax
    24d8:      	callq	0x24dd <mei_cl_irq_read_msg+0x251>
		00000000000024d9:  R_X86_64_PC32	__dynamic_dev_dbg-0x4
    24dd:      	movq	%r15, %rsi
    24e0:      	movq	%rbx, %rdi
    24e3:      	callq	0x1e82 <list_move_tail>
    24e8:      	jmp	0x2517 <mei_cl_irq_read_msg+0x28b>
    24ea:      	movq	(%r13), %rax
    24ee:      	movq	(%rip), %rdx            # 0x24f5 <mei_cl_irq_read_msg+0x269>
		00000000000024f1:  R_X86_64_PC32	jiffies-0x4
    24f5:      	movl	$0x9, %esi
    24fa:      	movq	%rdx, 0x188(%rax)
    2501:      	movq	(%r13), %rdi
    2505:      	callq	0x250a <mei_cl_irq_read_msg+0x27e>
		0000000000002506:  R_X86_64_PC32	__pm_runtime_suspend-0x4
    250a:      	jmp	0x2517 <mei_cl_irq_read_msg+0x28b>
    250c:      	movq	%r14, %rsi
    250f:      	movq	%r13, %rdi
    2512:      	callq	0x2517 <mei_cl_irq_read_msg+0x28b>
		0000000000002513:  R_X86_64_PC32	mei_irq_discard_msg-0x4
    2517:      	leaq	-0x28(%rbp), %rsp
    251b:      	xorl	%eax, %eax
    251d:      	popq	%rbx
    251e:      	popq	%r12
    2520:      	popq	%r13
    2522:      	popq	%r14
    2524:      	popq	%r15
    2526:      	popq	%rbp
    2527:      	retq

## mei_cl_write

work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/drivers/misc/mei/mei.ko:	file format elf64-x86-64

Disassembly of section .text:

0000000000004c4c <mei_cl_write>:
    4c4c:      	pushq	%rbp
    4c4d:      	movq	%rsp, %rbp
    4c50:      	pushq	%r15
    4c52:      	pushq	%r14
    4c54:      	pushq	%r13
    4c56:      	pushq	%r12
    4c58:      	pushq	%rbx
    4c59:      	subq	$0x58, %rsp
    4c5d:      	movl	%edx, -0x7c(%rbp)
    4c60:      	movq	%gs:0x28, %rax
    4c69:      	movq	%rax, -0x38(%rbp)
    4c6d:      	xorl	%eax, %eax
    4c6f:      	testq	%rdi, %rdi
    4c72:      	je	0x4c80 <mei_cl_write+0x34>
    4c74:      	movq	0x10(%rdi), %r12
    4c78:      	movq	%rdi, %rbx
    4c7b:      	testq	%r12, %r12
    4c7e:      	jne	0x4cae <mei_cl_write+0x62>
    4c80:      	movl	$0x64e, %esi            # imm = 0x64E
    4c85:      	movq	$0x0, %rdi
		0000000000004c88:  R_X86_64_32S	.rodata.str1.1+0x118c
    4c8c:      	callq	0x4c91 <mei_cl_write+0x45>
		0000000000004c8d:  R_X86_64_PC32	warn_slowpath_null-0x4
    4c91:      	movl	$0xffffffed, %eax       # imm = 0xFFFFFFED
    4c96:      	movq	-0x38(%rbp), %rsi
    4c9a:      	xorq	%gs:0x28, %rsi
    4ca3:      	je	0x50c9 <mei_cl_write+0x47d>
    4ca9:      	callq	0x4cae <mei_cl_write+0x62>
		0000000000004caa:  R_X86_64_PC32	__stack_chk_fail-0x4
    4cae:      	testq	%rsi, %rsi
    4cb1:      	movq	%rsi, %r13
    4cb4:      	jne	0x4cce <mei_cl_write+0x82>
    4cb6:      	movl	$0x651, %esi            # imm = 0x651
    4cbb:      	movq	$0x0, %rdi
		0000000000004cbe:  R_X86_64_32S	.rodata.str1.1+0x118c
    4cc2:      	callq	0x4cc7 <mei_cl_write+0x7b>
		0000000000004cc3:  R_X86_64_PC32	warn_slowpath_null-0x4
    4cc7:      	movl	$0xffffffea, %eax       # imm = 0xFFFFFFEA
    4ccc:      	jmp	0x4c96 <mei_cl_write+0x4a>
    4cce:      	testb	$0x4, (%rip)            # 0x4cd5 <mei_cl_write+0x89>
		0000000000004cd0:  R_X86_64_PC32	__verbose+0x7c5
    4cd5:      	movq	0x20(%rsi), %rax
    4cd9:      	movq	%rax, -0x78(%rbp)
    4cdd:      	movl	-0x78(%rbp), %r14d
    4ce1:      	je	0x4d1b <mei_cl_write+0xcf>
    4ce3:      	movq	0x90(%rbx), %rax
    4cea:      	xorl	%r8d, %r8d
    4ced:      	testq	%rax, %rax
    4cf0:      	je	0x4cf7 <mei_cl_write+0xab>
    4cf2:      	movzbl	0x2c(%rax), %r8d
    4cf7:      	movzbl	0xa0(%rbx), %ecx
    4cfe:      	movl	-0x78(%rbp), %r9d
    4d02:      	movq	$0x0, %rdx
		0000000000004d05:  R_X86_64_32S	.rodata.str1.1+0x162f
    4d09:      	movq	(%r12), %rsi
    4d0d:      	movq	$0x0, %rdi
		0000000000004d10:  R_X86_64_32S	__verbose+0x7a8
    4d14:      	xorl	%eax, %eax
    4d16:      	callq	0x4d1b <mei_cl_write+0xcf>
		0000000000004d17:  R_X86_64_PC32	__dynamic_dev_dbg-0x4
    4d1b:      	movq	(%r12), %rdi
    4d1f:      	movl	$0x5, %esi
    4d24:      	callq	0x4d29 <mei_cl_write+0xdd>
		0000000000004d25:  R_X86_64_PC32	__pm_runtime_resume-0x4
    4d29:      	movl	%eax, %r15d
    4d2c:      	shrl	$0x1f, %eax
    4d2f:      	je	0x4d73 <mei_cl_write+0x127>
    4d31:      	cmpl	$-0x73, %r15d
    4d35:      	je	0x4d73 <mei_cl_write+0x127>
    4d37:      	movq	(%r12), %rdi
    4d3b:      	callq	0x2b4d <pm_runtime_put_noidle>
    4d40:      	movq	0x90(%rbx), %rax
    4d47:      	xorl	%ecx, %ecx
    4d49:      	testq	%rax, %rax
    4d4c:      	je	0x4d52 <mei_cl_write+0x106>
    4d4e:      	movzbl	0x2c(%rax), %ecx
    4d52:      	movzbl	0xa0(%rbx), %edx
    4d59:      	movq	(%r12), %rdi
    4d5d:      	movl	%r15d, %r8d
    4d60:      	movq	$0x0, %rsi
		0000000000004d63:  R_X86_64_32S	.rodata.str1.1+0x14f3
    4d67:      	xorl	%eax, %eax
    4d69:      	callq	0x4d6e <mei_cl_write+0x122>
		0000000000004d6a:  R_X86_64_PC32	dev_err-0x4
    4d6e:      	jmp	0x50b9 <mei_cl_write+0x46d>
    4d73:      	movq	$0x0, 0x30(%r13)
    4d7b:      	movq	0x90(%rbx), %r15
    4d82:      	movl	$0x0, 0xa8(%rbx)
    4d8c:      	movq	%r15, %rdi
    4d8f:      	callq	0x2a64 <mei_cl_is_fixed_address.isra.5>
    4d94:      	xorl	%ecx, %ecx
    4d96:      	testb	%al, %al
    4d98:      	jne	0x4da0 <mei_cl_write+0x154>
    4d9a:      	movb	0xa0(%rbx), %cl
    4da0:      	xorl	%eax, %eax
    4da2:      	testq	%r15, %r15
    4da5:      	movb	%cl, -0x63(%rbp)
    4da8:      	je	0x4dae <mei_cl_write+0x162>
    4daa:      	movb	0x2c(%r15), %al
    4dae:      	movb	%al, -0x64(%rbp)
    4db1:      	movb	-0x61(%rbp), %al
    4db4:      	movq	%rbx, %rdi
    4db7:      	movb	%al, %dl
    4db9:      	andl	$0x1, %eax
    4dbc:      	andl	$0x41, %edx
    4dbf:      	movb	%dl, -0x61(%rbp)
    4dc2:      	movb	0x44(%r13), %dl
    4dc6:      	andl	$0x1, %edx
    4dc9:      	shll	$0x6, %edx
    4dcc:      	orl	%edx, %eax
    4dce:      	movb	%al, -0x61(%rbp)
    4dd1:      	callq	0x2a7d <mei_cl_tx_flow_ctrl_creds>
    4dd6:      	testl	%eax, %eax
    4dd8:      	js	0x505b <mei_cl_write+0x40f>
    4dde:      	jne	0x4e1c <mei_cl_write+0x1d0>
    4de0:      	testb	$0x4, (%rip)            # 0x4de7 <mei_cl_write+0x19b>
		0000000000004de2:  R_X86_64_PC32	__verbose+0x79d
    4de7:      	je	0x4f23 <mei_cl_write+0x2d7>
    4ded:      	movq	0x90(%rbx), %rax
    4df4:      	xorl	%r8d, %r8d
    4df7:      	testq	%rax, %rax
    4dfa:      	je	0x4e01 <mei_cl_write+0x1b5>
    4dfc:      	movzbl	0x2c(%rax), %r8d
    4e01:      	movzbl	0xa0(%rbx), %ecx
    4e08:      	movq	$0x0, %rdx
		0000000000004e0b:  R_X86_64_32S	.rodata.str1.1+0x15bf
    4e0f:      	movq	(%r12), %rsi
    4e13:      	movq	$0x0, %rdi
		0000000000004e16:  R_X86_64_32S	__verbose+0x780
    4e1a:      	jmp	0x4e62 <mei_cl_write+0x216>
    4e1c:      	movq	%r12, %rdi
    4e1f:      	callq	0x4e24 <mei_cl_write+0x1d8>
		0000000000004e20:  R_X86_64_PC32	mei_hbuf_acquire-0x4
    4e24:      	testb	%al, %al
    4e26:      	jne	0x4e6e <mei_cl_write+0x222>
    4e28:      	testb	$0x4, (%rip)            # 0x4e2f <mei_cl_write+0x1e3>
		0000000000004e2a:  R_X86_64_PC32	__verbose+0x775
    4e2f:      	je	0x4f23 <mei_cl_write+0x2d7>
    4e35:      	movq	0x90(%rbx), %rax
    4e3c:      	xorl	%r8d, %r8d
    4e3f:      	testq	%rax, %rax
    4e42:      	je	0x4e49 <mei_cl_write+0x1fd>
    4e44:      	movzbl	0x2c(%rax), %r8d
    4e49:      	movzbl	0xa0(%rbx), %ecx
    4e50:      	movq	(%r12), %rsi
    4e54:      	movq	$0x0, %rdx
		0000000000004e57:  R_X86_64_32S	.rodata.str1.1+0x164d
    4e5b:      	movq	$0x0, %rdi
		0000000000004e5e:  R_X86_64_32S	__verbose+0x758
    4e62:      	xorl	%eax, %eax
    4e64:      	callq	0x4e69 <mei_cl_write+0x21d>
		0000000000004e65:  R_X86_64_PC32	__dynamic_dev_dbg-0x4
    4e69:      	jmp	0x4f23 <mei_cl_write+0x2d7>
    4e6e:      	movq	0x7c8(%r12), %rax
    4e76:      	movq	%r12, %rdi
    4e79:      	callq	*0x78(%rax)
    4e7c:      	movslq	-0x78(%rbp), %rdx
    4e80:      	cmpq	%rax, %rdx
    4e83:      	jbe	0x4eac <mei_cl_write+0x260>
    4e85:      	movq	0x7c8(%r12), %rax
    4e8d:      	movq	%r12, %rdi
    4e90:      	callq	*0x78(%rax)
    4e93:      	movw	-0x62(%rbp), %dx
    4e97:      	andw	$0x1ff, %ax             # imm = 0x1FF
    4e9b:      	andw	$0xfe00, %dx            # imm = 0xFE00
    4ea0:      	orl	%edx, %eax
    4ea2:      	movw	%ax, -0x62(%rbp)
    4ea6:      	andb	$0x7f, -0x61(%rbp)
    4eaa:      	jmp	0x4ec6 <mei_cl_write+0x27a>
    4eac:      	movw	-0x62(%rbp), %dx
    4eb0:      	movl	-0x78(%rbp), %eax
    4eb3:      	andw	$0xfe00, %dx            # imm = 0xFE00
    4eb8:      	andw	$0x1ff, %ax             # imm = 0x1FF
    4ebc:      	orl	%edx, %eax
    4ebe:      	movw	%ax, -0x62(%rbp)
    4ec2:      	orb	$-0x80, -0x61(%rbp)
    4ec6:      	movq	0x7c8(%r12), %rax
    4ece:      	movq	0x28(%r13), %rdx
    4ed2:      	leaq	-0x64(%rbp), %rsi
    4ed6:      	movq	%r12, %rdi
    4ed9:      	callq	*0x80(%rax)
    4edf:      	testl	%eax, %eax
    4ee1:      	jne	0x505b <mei_cl_write+0x40f>
    4ee7:      	movq	%rbx, %rdi
    4eea:      	callq	0x2ad9 <mei_cl_tx_flow_ctrl_creds_reduce>
    4eef:      	testl	%eax, %eax
    4ef1:      	jne	0x505b <mei_cl_write+0x40f>
    4ef7:      	movw	-0x62(%rbp), %ax
    4efb:      	movl	$0x1, 0xa8(%rbx)
    4f05:      	movb	0x44(%r13), %dl
    4f09:      	andl	$0x1ff, %eax            # imm = 0x1FF
    4f0e:      	movq	%rax, 0x30(%r13)
    4f12:      	movb	-0x61(%rbp), %al
    4f15:      	andl	$-0x3, %edx
    4f18:      	shrb	$0x7, %al
    4f1b:      	addl	%eax, %eax
    4f1d:      	orl	%edx, %eax
    4f1f:      	movb	%al, 0x44(%r13)
    4f23:      	cmpb	$0x0, -0x61(%rbp)
    4f27:      	jns	0x4f43 <mei_cl_write+0x2f7>
    4f29:      	movq	0xc8(%r12), %rax
    4f31:      	leaq	0xc0(%r12), %rdx
    4f39:      	movq	%r13, 0xc8(%r12)
    4f41:      	jmp	0x4f58 <mei_cl_write+0x30c>
    4f43:      	leaq	0x78(%r12), %rdx
    4f48:      	movq	0x80(%r12), %rax
    4f50:      	movq	%r13, 0x80(%r12)
    4f58:      	movq	%rdx, (%r13)
    4f5c:      	movq	%rax, 0x8(%r13)
    4f60:      	movq	%r13, (%rax)
    4f63:      	xorl	%r13d, %r13d
    4f66:      	cmpb	$0x0, -0x7c(%rbp)
    4f6a:      	je	0x505e <mei_cl_write+0x412>
    4f70:      	cmpl	$0x2, 0xa8(%rbx)
    4f77:      	je	0x505e <mei_cl_write+0x412>
    4f7d:      	leaq	0x1b0(%r12), %r13
    4f85:      	xorl	%r15d, %r15d
    4f88:      	movq	%r13, %rdi
    4f8b:      	callq	0x4f90 <mei_cl_write+0x344>
		0000000000004f8c:  R_X86_64_PC32	mutex_unlock-0x4
    4f90:      	xorl	%edx, %edx
    4f92:      	movl	$0x69b, %esi            # imm = 0x69B
    4f97:      	movq	$0x0, %rdi
		0000000000004f9a:  R_X86_64_32S	.rodata.str1.1+0x118c
    4f9e:      	callq	0x4fa3 <mei_cl_write+0x357>
		0000000000004f9f:  R_X86_64_PC32	__might_sleep-0x4
    4fa3:      	callq	0x4fa8 <mei_cl_write+0x35c>
		0000000000004fa4:  R_X86_64_PC32	_cond_resched-0x4
    4fa8:      	cmpl	$0x2, 0xa8(%rbx)
    4faf:      	je	0x5017 <mei_cl_write+0x3cb>
    4fb1:      	cmpl	$0x2, 0x18(%rbx)
    4fb5:      	jne	0x5017 <mei_cl_write+0x3cb>
    4fb7:      	leaq	-0x60(%rbp), %rax
    4fbb:      	leaq	0x20(%rbx), %r15
    4fbf:      	movl	$0x0, -0x60(%rbp)
    4fc6:      	addq	$0x18, %rax
    4fca:      	movq	%rax, -0x48(%rbp)
    4fce:      	movq	%rax, -0x40(%rbp)
    4fd2:      	leaq	-0x60(%rbp), %rsi
    4fd6:      	movl	$0x1, %edx
    4fdb:      	movq	%r15, %rdi
    4fde:      	callq	0x4fe3 <mei_cl_write+0x397>
		0000000000004fdf:  R_X86_64_PC32	prepare_to_wait_event-0x4
    4fe3:      	cmpl	$0x2, 0xa8(%rbx)
    4fea:      	je	0x4ffe <mei_cl_write+0x3b2>
    4fec:      	cmpl	$0x2, 0x18(%rbx)
    4ff0:      	jne	0x4ffe <mei_cl_write+0x3b2>
    4ff2:      	testq	%rax, %rax
    4ff5:      	jne	0x5000 <mei_cl_write+0x3b4>
    4ff7:      	callq	0x4ffc <mei_cl_write+0x3b0>
		0000000000004ff8:  R_X86_64_PC32	schedule-0x4
    4ffc:      	jmp	0x4fd2 <mei_cl_write+0x386>
    4ffe:      	xorl	%eax, %eax
    5000:      	leaq	-0x60(%rbp), %rsi
    5004:      	movq	%r15, %rdi
    5007:      	movq	%rax, -0x78(%rbp)
    500b:      	callq	0x5010 <mei_cl_write+0x3c4>
		000000000000500c:  R_X86_64_PC32	finish_wait-0x4
    5010:      	movq	-0x78(%rbp), %rax
    5014:      	movl	%eax, %r15d
    5017:      	movq	%r13, %rdi
    501a:      	callq	0x501f <mei_cl_write+0x3d3>
		000000000000501b:  R_X86_64_PC32	mutex_lock-0x4
    501f:      	testl	%r15d, %r15d
    5022:      	je	0x5046 <mei_cl_write+0x3fa>
    5024:      	movq	%gs:0x0, %rax
		0000000000005029:  R_X86_64_32S	current_task
    502d:      	movq	0x8(%rax), %rax
    5031:      	movl	$0xfffffffc, %r14d      # imm = 0xFFFFFFFC
    5037:      	movq	0x8(%rax), %rax
    503b:      	testb	$0x4, %al
    503d:      	cmovel	%r15d, %r14d
    5041:      	xorl	%r13d, %r13d
    5044:      	jmp	0x505e <mei_cl_write+0x412>
    5046:      	xorl	%r13d, %r13d
    5049:      	cmpl	$0x2, 0xa8(%rbx)
    5050:      	movl	$0xfffffff2, %eax       # imm = 0xFFFFFFF2
    5055:      	cmovnel	%eax, %r14d
    5059:      	jmp	0x505e <mei_cl_write+0x412>
    505b:      	movl	%eax, %r14d
    505e:      	testb	$0x4, (%rip)            # 0x5065 <mei_cl_write+0x419>
		0000000000005060:  R_X86_64_PC32	__verbose+0x74d
    5065:      	je	0x509b <mei_cl_write+0x44f>
    5067:      	movq	0x90(%rbx), %rax
    506e:      	xorl	%r8d, %r8d
    5071:      	testq	%rax, %rax
    5074:      	je	0x507b <mei_cl_write+0x42f>
    5076:      	movzbl	0x2c(%rax), %r8d
    507b:      	movzbl	0xa0(%rbx), %ecx
    5082:      	movq	(%r12), %rsi
    5086:      	movq	$0x0, %rdx
		0000000000005089:  R_X86_64_32S	.rodata.str1.1+0x151c
    508d:      	movq	$0x0, %rdi
		0000000000005090:  R_X86_64_32S	__verbose+0x730
    5094:      	xorl	%eax, %eax
    5096:      	callq	0x509b <mei_cl_write+0x44f>
		0000000000005097:  R_X86_64_PC32	__dynamic_dev_dbg-0x4
    509b:      	movq	(%r12), %rax
    509f:      	movq	(%rip), %rdx            # 0x50a6 <mei_cl_write+0x45a>
		00000000000050a2:  R_X86_64_PC32	jiffies-0x4
    50a6:      	movl	%r14d, %r15d
    50a9:      	movq	%rdx, 0x188(%rax)
    50b0:      	movq	(%r12), %rdi
    50b4:      	callq	0x2a54 <pm_runtime_put_autosuspend>
    50b9:      	movq	%r13, %rdi
    50bc:      	callq	0x50c1 <mei_cl_write+0x475>
		00000000000050bd:  R_X86_64_PC32	mei_io_cb_free-0x4
    50c1:      	movl	%r15d, %eax
    50c4:      	jmp	0x4c96 <mei_cl_write+0x4a>
    50c9:      	addq	$0x58, %rsp
    50cd:      	popq	%rbx
    50ce:      	popq	%r12
    50d0:      	popq	%r13
    50d2:      	popq	%r14
    50d4:      	popq	%r15
    50d6:      	popq	%rbp
    50d7:      	retq

## mei_cl_complete

work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/drivers/misc/mei/mei.ko:	file format elf64-x86-64

Disassembly of section .text:

00000000000050d8 <mei_cl_complete>:
    50d8:      	cmpl	$0x6, 0x18(%rsi)
    50dc:      	ja	0x51e8 <mei_cl_complete+0x110>
    50e2:      	pushq	%rbp
    50e3:      	movq	%rsp, %rbp
    50e6:      	pushq	%r12
    50e8:      	pushq	%rbx
    50e9:      	movl	0x18(%rsi), %eax
    50ec:      	movq	%rdi, %rbx
    50ef:      	jmpq	*(,%rax,8)
		00000000000050f2:  R_X86_64_32S	.rodata+0x390
    50f6:      	movq	0x10(%rdi), %r12
    50fa:      	movq	%rsi, %rdi
    50fd:      	callq	0x5102 <mei_cl_complete+0x2a>
		00000000000050fe:  R_X86_64_PC32	mei_io_cb_free-0x4
    5102:      	leaq	0x28(%rbx), %rax
    5106:      	cmpq	%rax, 0x28(%rbx)
    510a:      	movl	$0x2, 0xa8(%rbx)
    5114:      	leaq	0x20(%rbx), %rdi
    5118:      	jne	0x5199 <mei_cl_complete+0xc1>
    511a:      	movq	(%r12), %rax
    511e:      	movq	(%rip), %rdx            # 0x5125 <mei_cl_complete+0x4d>
		0000000000005121:  R_X86_64_PC32	jiffies-0x4
    5125:      	movl	$0x9, %esi
    512a:      	movq	%rdx, 0x188(%rax)
    5131:      	movq	(%r12), %rdi
    5135:      	callq	0x513a <mei_cl_complete+0x62>
		0000000000005136:  R_X86_64_PC32	__pm_runtime_suspend-0x4
    513a:      	jmp	0x51e4 <mei_cl_complete+0x10c>
    513f:      	movq	0xc8(%rdi), %rax
    5146:      	leaq	0xc0(%rdi), %rdx
    514d:      	movq	%rsi, 0xc8(%rdi)
    5154:      	movq	%rdx, (%rsi)
    5157:      	movq	%rax, 0x8(%rsi)
    515b:      	movq	%rsi, (%rax)
    515e:      	movq	0x90(%rdi), %rdi
    5165:      	callq	0x2a64 <mei_cl_is_fixed_address.isra.5>
    516a:      	testb	%al, %al
    516c:      	jne	0x5189 <mei_cl_complete+0xb1>
    516e:      	movb	0xa2(%rbx), %al
    5174:      	testb	%al, %al
    5176:      	jne	0x51da <mei_cl_complete+0x102>
    5178:      	movl	$0x6ce, %esi            # imm = 0x6CE
    517d:      	movq	$0x0, %rdi
		0000000000005180:  R_X86_64_32S	.rodata.str1.1+0x118c
    5184:      	callq	0x5189 <mei_cl_complete+0xb1>
		0000000000005185:  R_X86_64_PC32	warn_slowpath_null-0x4
    5189:      	movq	%rbx, %rdi
    518c:      	callq	0x5191 <mei_cl_complete+0xb9>
		000000000000518d:  R_X86_64_PC32	mei_cl_bus_rx_event-0x4
    5191:      	testb	%al, %al
    5193:      	jne	0x51e4 <mei_cl_complete+0x10c>
    5195:      	leaq	0x38(%rbx), %rdi
    5199:      	xorl	%ecx, %ecx
    519b:      	movl	$0x1, %edx
    51a0:      	movl	$0x1, %esi
    51a5:      	jmp	0x51c1 <mei_cl_complete+0xe9>
    51a7:      	leaq	0x58(%rbx), %rax
    51ab:      	cmpq	%rax, 0x58(%rbx)
    51af:      	leaq	0x50(%rdi), %rdi
    51b3:      	je	0x51e4 <mei_cl_complete+0x10c>
    51b5:      	xorl	%ecx, %ecx
    51b7:      	movl	$0x1, %edx
    51bc:      	movl	$0x3, %esi
    51c1:      	callq	0x51c6 <mei_cl_complete+0xee>
		00000000000051c2:  R_X86_64_PC32	__wake_up-0x4
    51c6:      	jmp	0x51e4 <mei_cl_complete+0x10c>
    51c8:      	movq	%rsi, %rdi
    51cb:      	callq	0x51d0 <mei_cl_complete+0xf8>
		00000000000051cc:  R_X86_64_PC32	mei_io_cb_free-0x4
    51d0:      	movq	%rbx, %rdi
    51d3:      	callq	0x51d8 <mei_cl_complete+0x100>
		00000000000051d4:  R_X86_64_PC32	mei_cl_set_disconnected-0x4
    51d8:      	jmp	0x51e4 <mei_cl_complete+0x10c>
    51da:      	decl	%eax
    51dc:      	movb	%al, 0xa2(%rbx)
    51e2:      	jmp	0x5189 <mei_cl_complete+0xb1>
    51e4:      	popq	%rbx
    51e5:      	popq	%r12
    51e7:      	popq	%rbp
    51e8:      	retq

## mei_write

work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/modules/4.1.27-abl/kernel/drivers/misc/mei/mei.ko:	file format elf64-x86-64

Disassembly of section .text:

000000000000566f <mei_write>:
    566f:      	pushq	%rbp
    5670:      	movq	%rsp, %rbp
    5673:      	pushq	%r15
    5675:      	pushq	%r14
    5677:      	pushq	%r13
    5679:      	pushq	%r12
    567b:      	pushq	%rbx
    567c:      	subq	$0x18, %rsp
    5680:      	movq	0xd0(%rdi), %rbx
    5687:      	movq	%rsi, -0x38(%rbp)
    568b:      	testq	%rbx, %rbx
    568e:      	je	0x5699 <mei_write+0x2a>
    5690:      	movq	0x10(%rbx), %r15
    5694:      	testq	%r15, %r15
    5697:      	jne	0x56b6 <mei_write+0x47>
    5699:      	movl	$0x10e, %esi            # imm = 0x10E
    569e:      	movq	$0x0, %rdi
		00000000000056a1:  R_X86_64_32S	.rodata.str1.1+0x16db
    56a5:      	callq	0x56aa <mei_write+0x3b>
		00000000000056a6:  R_X86_64_PC32	warn_slowpath_null-0x4
    56aa:      	movq	$-0x13, %rax
    56b1:      	jmp	0x5807 <mei_write+0x198>
    56b6:      	leaq	0x1b0(%r15), %r13
    56bd:      	movq	%rdi, %r14
    56c0:      	movq	%rcx, -0x40(%rbp)
    56c4:      	movq	%rdx, %r12
    56c7:      	movq	%r13, %rdi
    56ca:      	callq	0x56cf <mei_write+0x60>
		00000000000056cb:  R_X86_64_PC32	mutex_lock-0x4
    56cf:      	cmpl	$0x2, 0x298(%r15)
    56d7:      	movl	$0xffffffed, %eax       # imm = 0xFFFFFFED
    56dc:      	movq	-0x40(%rbp), %rcx
    56e0:      	jne	0x5744 <mei_write+0xd5>
    56e2:      	cmpl	$0x2, 0x18(%rbx)
    56e6:      	je	0x5719 <mei_write+0xaa>
    56e8:      	movq	0x90(%rbx), %rax
    56ef:      	xorl	%ecx, %ecx
    56f1:      	testq	%rax, %rax
    56f4:      	je	0x56fa <mei_write+0x8b>
    56f6:      	movzbl	0x2c(%rax), %ecx
    56fa:      	movzbl	0xa0(%rbx), %edx
    5701:      	movq	(%r15), %rdi
    5704:      	xorl	%eax, %eax
    5706:      	movq	$0x0, %rsi
		0000000000005709:  R_X86_64_32S	.rodata.str1.1+0x17a6
    570d:      	callq	0x5712 <mei_write+0xa3>
		000000000000570e:  R_X86_64_PC32	dev_err-0x4
    5712:      	movl	$0xffffffed, %eax       # imm = 0xFFFFFFED
    5717:      	jmp	0x5744 <mei_write+0xd5>
    5719:      	movq	0x90(%rbx), %rdx
    5720:      	cmpq	(%rdx), %rdx
    5723:      	jne	0x5730 <mei_write+0xc1>
    5725:      	cmpq	0x8(%rdx), %rdx
    5729:      	movl	$0xffffffe7, %eax       # imm = 0xFFFFFFE7
    572e:      	je	0x5744 <mei_write+0xd5>
    5730:      	movl	0x28(%rdx), %edx
    5733:      	movl	$0xffffffe5, %eax       # imm = 0xFFFFFFE5
    5738:      	cmpq	%rdx, %r12
    573b:      	ja	0x5744 <mei_write+0xd5>
    573d:      	xorl	%eax, %eax
    573f:      	testq	%r12, %r12
    5742:      	jne	0x5758 <mei_write+0xe9>
    5744:      	movq	%r13, %rdi
    5747:      	movl	%eax, -0x38(%rbp)
    574a:      	callq	0x574f <mei_write+0xe0>
		000000000000574b:  R_X86_64_PC32	mutex_unlock-0x4
    574f:      	movslq	-0x38(%rbp), %rax
    5753:      	jmp	0x5807 <mei_write+0x198>
    5758:      	movq	$0x0, (%rcx)
    575f:      	movl	$0x1, %edx
    5764:      	movq	%r14, %rcx
    5767:      	movq	%r12, %rsi
    576a:      	movq	%rbx, %rdi
    576d:      	callq	0x5772 <mei_write+0x103>
		000000000000576e:  R_X86_64_PC32	mei_cl_alloc_cb-0x4
    5772:      	movq	%rax, %r14
    5775:      	movl	$0xfffffff4, %eax       # imm = 0xFFFFFFF4
    577a:      	testq	%r14, %r14
    577d:      	je	0x5744 <mei_write+0xd5>
    577f:      	movq	0x28(%r14), %rdi
    5783:      	movq	%rdi, -0x40(%rbp)
    5787:      	callq	0x578c <mei_write+0x11d>
		0000000000005788:  R_X86_64_PC32	might_fault-0x4
    578c:      	movq	-0x38(%rbp), %rsi
    5790:      	movq	-0x40(%rbp), %rdi
    5794:      	movl	%r12d, %edx
    5797:      	callq	0x579c <mei_write+0x12d>
		0000000000005798:  R_X86_64_PC32	_copy_from_user-0x4
    579c:      	testl	%eax, %eax
    579e:      	je	0x57d3 <mei_write+0x164>
    57a0:      	testb	$0x4, (%rip)            # 0x57a7 <mei_write+0x138>
		00000000000057a2:  R_X86_64_PC32	__verbose+0xe05
    57a7:      	je	0x57c1 <mei_write+0x152>
    57a9:      	movq	(%r15), %rsi
    57ac:      	movq	$0x0, %rdx
		00000000000057af:  R_X86_64_32S	.rodata.str1.1+0x17cc
    57b3:      	movq	$0x0, %rdi
		00000000000057b6:  R_X86_64_32S	__verbose+0xde8
    57ba:      	xorl	%eax, %eax
    57bc:      	callq	0x57c1 <mei_write+0x152>
		00000000000057bd:  R_X86_64_PC32	__dynamic_dev_dbg-0x4
    57c1:      	movq	%r14, %rdi
    57c4:      	callq	0x57c9 <mei_write+0x15a>
		00000000000057c5:  R_X86_64_PC32	mei_io_cb_free-0x4
    57c9:      	movl	$0xfffffff2, %eax       # imm = 0xFFFFFFF2
    57ce:      	jmp	0x5744 <mei_write+0xd5>
    57d3:      	addq	$0x658, %r15            # imm = 0x658
    57da:      	cmpq	%r15, %rbx
    57dd:      	jne	0x57f5 <mei_write+0x186>
    57df:      	movq	%r14, %rsi
    57e2:      	movq	%rbx, %rdi
    57e5:      	callq	0x57ea <mei_write+0x17b>
		00000000000057e6:  R_X86_64_PC32	mei_amthif_write-0x4
    57ea:      	testl	%eax, %eax
    57ec:      	cmovel	%r12d, %eax
    57f0:      	jmp	0x5744 <mei_write+0xd5>
    57f5:      	xorl	%edx, %edx
    57f7:      	movq	%r14, %rsi
    57fa:      	movq	%rbx, %rdi
    57fd:      	callq	0x5802 <mei_write+0x193>
		00000000000057fe:  R_X86_64_PC32	mei_cl_write-0x4
    5802:      	jmp	0x5744 <mei_write+0xd5>
    5807:      	addq	$0x18, %rsp
    580b:      	popq	%rbx
    580c:      	popq	%r12
    580e:      	popq	%r13
    5810:      	popq	%r14
    5812:      	popq	%r15
    5814:      	popq	%rbp
    5815:      	retq
