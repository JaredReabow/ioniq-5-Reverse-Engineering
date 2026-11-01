# AppFUMO boot-partition write exact-static excerpt
# ELF SHA-256: 464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7
# Build ID: 863a8730e66a1c5245a1bf458fe2554adee0351a
# Raw VAs shown; advisory Ghidra VAs are raw + 0x100000.
# Execution-free. Calls and returns do not prove successful mounts, writes,
# durable bytes, boot selection, acceptance, root, or persistence.

  120020:      	movq	%r14, %rdi
  120023:      	callq	0x4b960 <.text+0x27130>
  120028:      	movq	%r13, %rdi
  12002b:      	callq	0x4b960 <.text+0x27130>
  120030:      	jmp	0x11f54b <.text+0xfad1b>
  120035:      	nopl	(%rax)
  120038:      	movq	0x238(%rbx), %rdi
  12003f:      	callq	0x148e70 <.text+0x124640>
  120044:      	testb	%al, %al
  120046:      	je	0x11f631 <.text+0xfae01>
  12004c:      	movb	$0x1, 0x240(%rbx)
  120053:      	movl	$0x1, %ebp
  1225ab:      	movq	0x40(%rbx), %rdi
  1225af:      	callq	0x8ee00 <.text+0x6a5d0>
  1225b4:      	testb	%al, %al
  1225b6:      	je	0x1225e0 <.text+0xfddb0>
  1225b8:      	cmpb	$0x0, 0x240(%rbx)
  1225bf:      	jne	0x1225e0 <.text+0xfddb0>
  1225c1:      	movq	0x238(%rbx), %rdi
  1225c8:      	callq	0x148e70 <.text+0x124640>
  1225cd:      	testb	%al, %al
  1225cf:      	je	0x1225e0 <.text+0xfddb0>
  1225d1:      	movb	$0x1, 0x240(%rbx)
  1225d8:      	nopl	(%rax,%rax)
  1225e0:      	movq	0x40(%rbx), %rdi
  1397c0:      	pushq	%r13
  1397c2:      	pushq	%r12
  1397c4:      	pushq	%rbp
  1397c5:      	pushq	%rbx
  1397c6:      	subq	$0x248, %rsp            # imm = 0x248
  1397cd:      	movq	%fs:0x28, %rax
  1397d6:      	movq	%rax, 0x238(%rsp)
  1397de:      	xorl	%eax, %eax
  1397e0:      	movq	(%rsi), %rax
  1397e3:      	movl	0x4(%rax), %eax
  1397e6:      	testl	%eax, %eax
  1397e8:      	jne	0x139810 <.text+0x114fe0>
  1397ea:      	movq	0x238(%rsp), %rax
  1397f2:      	xorq	%fs:0x28, %rax
  1397fb:      	jne	0x1398ba <.text+0x11508a>
  139801:      	addq	$0x248, %rsp            # imm = 0x248
  139808:      	popq	%rbx
  139809:      	popq	%rbp
  13980a:      	popq	%r12
  13980c:      	popq	%r13
  13980e:      	retq
  13980f:      	nop
  139810:      	leaq	0xd2005(%rip), %rdi     # 0x20b81c
  139817:      	movq	%rsi, %rbx
  13981a:      	movl	$0x5, %esi
  13981f:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  139824:      	leaq	0x10(%rsp), %rbp
  139829:      	movq	%rbx, %rsi
  13982c:      	movq	%rax, (%rsp)
  139830:      	movq	%rbp, %rdi
  139833:      	callq	0x55bf0 <.text+0x313c0>
  139838:      	movq	%rsp, %rsi
  13983b:      	movq	%rbp, %rdi
  13983e:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  139843:      	leaq	0x20(%rsp), %r12
  139848:      	movq	%rbp, %rsi
  13984b:      	movq	%r12, %rdi
  13984e:      	callq	0x55b20 <.text+0x312f0>
  139853:      	movq	0x20(%rsp), %rdi
  139858:      	callq	0x55ac0 <.text+0x31290>
  13985d:      	leaq	0xd8427(%rip), %rsi     # 0x211c8b
  139864:      	movq	%rax, %rdi
  139867:      	callq	0x23800 <popen@plt>
  13986c:      	movq	%r12, %rdi
  13986f:      	movq	%rax, %rbx
  139872:      	callq	0x4b8e0 <.text+0x270b0>
  139877:      	movq	%rbp, %rdi
  13987a:      	callq	0x4b960 <.text+0x27130>
  13987f:      	movq	%rsp, %rdi
  139882:      	callq	0x4b960 <.text+0x27130>
  139887:      	testq	%rbx, %rbx
  13988a:      	je	0x1397ea <.text+0x114fba>
  139890:      	leaq	0x30(%rsp), %rbp
  139895:      	nopl	(%rax)
  139898:      	movq	%rbx, %rdx
  13989b:      	movl	$0x200, %esi            # imm = 0x200
  1398a0:      	movq	%rbp, %rdi
  1398a3:      	callq	0x23130 <fgets@plt>
  1398a8:      	testq	%rax, %rax
  1398ab:      	jne	0x139898 <.text+0x115068>
  1398ad:      	movq	%rbx, %rdi
  1398b0:      	callq	0x21fe0 <pclose@plt>
  1398b5:      	jmp	0x1397ea <.text+0x114fba>
  1398ba:      	callq	0x226b0 <__stack_chk_fail@plt>
  13bba0:      	pushq	%r15
  13bba2:      	pushq	%r14
  13bba4:      	pushq	%r13
  13bba6:      	pushq	%r12
  13bba8:      	pushq	%rbp
  13bba9:      	pushq	%rbx
  13bbaa:      	subq	$0x98, %rsp
  13bbb1:      	movq	(%rsi), %rax
  13bbb4:      	movq	%fs:0x28, %rbx
  13bbbd:      	movq	%rbx, 0x88(%rsp)
  13bbc5:      	xorl	%ebx, %ebx
  13bbc7:      	movq	%rsi, 0x8(%rsp)
  13bbcc:      	leaq	0x20(%rsp), %r13
  13bbd1:      	movl	0xc(%rax), %ebx
  13bbd4:      	subl	0x8(%rax), %ebx
  13bbd7:      	leaq	0x598c82(%rip), %rax    # 0x6d4860 <_ZN9QListData11shared_nullE>
  13bbde:      	movq	%rax, 0x20(%rsp)
  13bbe3:      	testl	%ebx, %ebx
  13bbe5:      	jle	0x13be00 <.text+0x1175d0>
  13bbeb:      	leaq	0x20(%rsp), %r13
  13bbf0:      	xorl	%ebp, %ebp
  13bbf2:      	leaq	0x80(%rsp), %r14
  13bbfa:      	nopw	(%rax,%rax)
  13bc00:      	movl	$0x10, %edi
  13bc05:      	callq	0x221f0 <_Znwm@plt>
  13bc0a:      	xorl	%esi, %esi
  13bc0c:      	movq	%rax, %rdi
  13bc0f:      	movq	%rax, %r12
  13bc12:      	callq	0x235b0 <_ZN8QProcessC1EP7QObject@plt>
  13bc17:      	movq	%r14, %rsi
  13bc1a:      	movq	%r13, %rdi
  13bc1d:      	movq	%r12, 0x80(%rsp)
  13bc25:      	callq	0x144bc0 <.text+0x120390>
  13bc2a:      	addl	$0x1, %ebp
  13bc2d:      	cmpl	%ebx, %ebp
  13bc2f:      	jne	0x13bc00 <.text+0x1173d0>
  13bc31:      	leal	-0x1(%rbx), %eax
  13bc34:      	movl	$0x1, %ebp
  13bc39:      	xorl	%r12d, %r12d
  13bc3c:      	movl	%eax, 0x14(%rsp)
  13bc40:      	cmpl	$0x1, %ebx
  13bc43:      	jle	0x13bc60 <.text+0x117430>
  13bc45:      	movl	%ebp, %r15d
  13bc48:      	cmpl	%r12d, 0x14(%rsp)
  13bc4d:      	jg	0x13bf0b <.text+0x1176db>
  13bc53:      	addl	$0x1, %r12d
  13bc57:      	addl	$0x1, %ebp
  13bc5a:      	cmpl	%r15d, %ebx
  13bc5d:      	jg	0x13bc40 <.text+0x117410>
  13bc5f:      	nop
  13bc60:      	movq	0x8(%rsp), %rax
  13bc65:      	movq	(%rax), %rdx
  13bc68:      	movslq	0x8(%rdx), %rax
  13bc6c:      	movl	0xc(%rdx), %ecx
  13bc6f:      	subl	%eax, %ecx
  13bc71:      	testl	%ecx, %ecx
  13bc73:      	jle	0x13beec <.text+0x1176bc>
  13bc79:      	xorl	%r12d, %r12d
  13bc7c:      	xorl	%ebp, %ebp
  13bc7e:      	jmp	0x13bcb0 <.text+0x117480>
  13bc80:      	addl	$0x1, %ebp
  13bc83:      	cmpl	%ebx, %ebp
  13bc85:      	jge	0x13be00 <.text+0x1175d0>
  13bc8b:      	testl	%ebp, %ebp
  13bc8d:      	js	0x13beec <.text+0x1176bc>
  13bc93:      	movq	0x8(%rsp), %rax
  13bc98:      	addq	$0x1, %r12
  13bc9c:      	movq	(%rax), %rdx
  13bc9f:      	movslq	0x8(%rdx), %rax
  13bca3:      	movl	0xc(%rdx), %ecx
  13bca6:      	subl	%eax, %ecx
  13bca8:      	cmpl	%ecx, %ebp
  13bcaa:      	jge	0x13beec <.text+0x1176bc>
  13bcb0:      	movq	0x20(%rsp), %rcx
  13bcb5:      	addq	%r12, %rax
  13bcb8:      	movq	0x10(%rdx,%rax,8), %rsi
  13bcbd:      	movl	0xc(%rcx), %edi
  13bcc0:      	movslq	0x8(%rcx), %rax
  13bcc4:      	leaq	0x8(%rsi), %rdx
  13bcc8:      	subl	%eax, %edi
  13bcca:      	cmpl	%edi, %ebp
  13bccc:      	jge	0x13beec <.text+0x1176bc>
  13bcd2:      	addq	%r12, %rax
  13bcd5:      	movq	0x10(%rcx,%rax,8), %rdi
  13bcda:      	movl	$0x3, %ecx
  13bcdf:      	callq	0x23670 <_ZN8QProcess5startERK7QStringRK11QStringList6QFlagsIN9QIODevice12OpenModeFlagEE@plt>
  13bce4:      	movq	0x20(%rsp), %rdx
  13bce9:      	movslq	0x8(%rdx), %rax
  13bced:      	movl	0xc(%rdx), %ecx
  13bcf0:      	subl	%eax, %ecx
  13bcf2:      	cmpl	%ecx, %ebp
  13bcf4:      	jge	0x13beec <.text+0x1176bc>
  13bcfa:      	addq	%r12, %rax
  13bcfd:      	movl	$0x3e8, %esi            # imm = 0x3E8
  13bd02:      	movq	0x10(%rdx,%rax,8), %rdi
  13bd07:      	callq	0x22330 <_ZN8QProcess14waitForStartedEi@plt>
  13bd0c:      	testb	%al, %al
  13bd0e:      	jne	0x13bc80 <.text+0x117450>
  13bd14:      	leaq	0x40(%rsp), %r12
  13bd19:      	movl	%ebp, %esi
  13bd1b:      	movq	%r13, %rdi
  13bd1e:      	callq	0x66590 <.text+0x41d60>
  13bd23:      	movq	%r12, %rdi
  13bd26:      	movq	(%rax), %rsi
  13bd29:      	callq	0x23770 <_ZNK9QIODevice11errorStringEv@plt>
  13bd2e:      	leaq	0x50(%rsp), %rbx
  13bd33:      	movq	%r12, %rsi
  13bd36:      	movq	%rbx, %rdi
  13bd39:      	callq	0x55b20 <.text+0x312f0>
  13bd3e:      	movq	0x50(%rsp), %rdi
  13bd43:      	callq	0x55ac0 <.text+0x31290>
  13bd48:      	movq	0x8(%rsp), %rdi
  13bd4d:      	movl	%ebp, %esi
  13bd4f:      	leaq	0x30(%rsp), %rbp
  13bd54:      	movq	%rax, %r15
  13bd57:      	callq	0x66590 <.text+0x41d60>
  13bd5c:      	movq	%r14, %rdi
  13bd5f:      	movq	(%rax), %rsi
  13bd62:      	callq	0x55bf0 <.text+0x313c0>
  13bd67:      	movq	%r14, %rsi
  13bd6a:      	movq	%rbp, %rdi
  13bd6d:      	callq	0x55b20 <.text+0x312f0>
  13bd72:      	movq	0x30(%rsp), %rdi
  13bd77:      	callq	0x55ac0 <.text+0x31290>
  13bd7c:      	movq	%rax, 0x8(%rsp)
  13bd81:      	callq	0x55c60 <.text+0x31430>
  13bd86:      	movq	0x8(%rsp), %rcx
  13bd8b:      	movq	%rax, %rdi
  13bd8e:      	movq	%r15, %r8
  13bd91:      	xorl	%eax, %eax
  13bd93:      	leaq	0xf16be(%rip), %rdx     # 0x22d458
  13bd9a:      	leaq	0xf0f1a(%rip), %rsi     # 0x22ccbb
  13bda1:      	callq	0x137430 <.text+0x112c00>
  13bda6:      	movq	%rbp, %rdi
  13bda9:      	callq	0x4b8e0 <.text+0x270b0>
  13bdae:      	movq	%r14, %rdi
  13bdb1:      	callq	0x4b960 <.text+0x27130>
  13bdb6:      	movq	%rbx, %rdi
  13bdb9:      	callq	0x4b8e0 <.text+0x270b0>
  13bdbe:      	movq	%r12, %rdi
  13bdc1:      	callq	0x4b960 <.text+0x27130>
  13bdc6:      	movq	%r13, %rdi
  13bdc9:      	callq	0x1449a0 <.text+0x120170>
  13bdce:      	movq	0x88(%rsp), %rax
  13bdd6:      	xorq	%fs:0x28, %rax
  13bddf:      	jne	0x13bf78 <.text+0x117748>
  13bde5:      	addq	$0x98, %rsp
  13bdec:      	popq	%rbx
  13bded:      	popq	%rbp
  13bdee:      	popq	%r12
  13bdf0:      	popq	%r13
  13bdf2:      	popq	%r14
  13bdf4:      	popq	%r15
  13bdf6:      	retq
  13bdf7:      	nopw	(%rax,%rax)
  13be00:      	subl	$0x1, %ebx
  13be03:      	movq	%r13, %rdi
  13be06:      	movl	%ebx, %esi
  13be08:      	callq	0x66590 <.text+0x41d60>
  13be0d:      	movl	$0xffffffff, %esi       # imm = 0xFFFFFFFF
  13be12:      	movq	(%rax), %rdi
  13be15:      	callq	0x22e90 <_ZN8QProcess15waitForFinishedEi@plt>
  13be1a:      	testb	%al, %al
  13be1c:      	jne	0x13bedf <.text+0x1176af>
  13be22:      	leaq	0x70(%rsp), %rbp
  13be27:      	movl	%ebx, %esi
  13be29:      	movq	%r13, %rdi
  13be2c:      	callq	0x66590 <.text+0x41d60>
  13be31:      	movq	%rbp, %rdi
  13be34:      	movq	(%rax), %rsi
  13be37:      	callq	0x23770 <_ZNK9QIODevice11errorStringEv@plt>
  13be3c:      	leaq	0x80(%rsp), %r12
  13be44:      	movq	%rbp, %rsi
  13be47:      	movq	%r12, %rdi
  13be4a:      	callq	0x55b20 <.text+0x312f0>
  13be4f:      	movq	0x80(%rsp), %rdi
  13be57:      	leaq	0x60(%rsp), %r15
  13be5c:      	callq	0x55ac0 <.text+0x31290>
  13be61:      	movq	0x8(%rsp), %rdi
  13be66:      	movl	%ebx, %esi
  13be68:      	leaq	0x50(%rsp), %rbx
  13be6d:      	movq	%rax, %r14
  13be70:      	callq	0x66590 <.text+0x41d60>
  13be75:      	movq	%rbx, %rdi
  13be78:      	movq	(%rax), %rsi
  13be7b:      	callq	0x55bf0 <.text+0x313c0>
  13be80:      	movq	%rbx, %rsi
  13be83:      	movq	%r15, %rdi
  13be86:      	callq	0x55b20 <.text+0x312f0>
  13be8b:      	movq	0x60(%rsp), %rdi
  13be90:      	callq	0x55ac0 <.text+0x31290>
  13be95:      	movq	%rax, 0x8(%rsp)
  13be9a:      	callq	0x55c60 <.text+0x31430>
  13be9f:      	movq	0x8(%rsp), %rcx
  13bea4:      	movq	%rax, %rdi
  13bea7:      	movq	%r14, %r8
  13beaa:      	xorl	%eax, %eax
  13beac:      	leaq	0xf15a5(%rip), %rdx     # 0x22d458
  13beb3:      	leaq	0xf0e1a(%rip), %rsi     # 0x22ccd4
  13beba:      	callq	0x137430 <.text+0x112c00>
  13bebf:      	movq	%r15, %rdi
  13bec2:      	callq	0x4b8e0 <.text+0x270b0>
  13bec7:      	movq	%rbx, %rdi
  13beca:      	callq	0x4b960 <.text+0x27130>
  13becf:      	movq	%r12, %rdi
  13bfd0:      	pushq	%r14
  13bfd2:      	pushq	%r13
  13bfd4:      	pushq	%r12
  13bfd6:      	movq	%rdi, %r12
  13bfd9:      	pushq	%rbp
  13bfda:      	pushq	%rbx
  13bfdb:      	subq	$0x40, %rsp
  13bfdf:      	movq	%fs:0x28, %rax
  13bfe8:      	movq	%rax, 0x38(%rsp)
  13bfed:      	xorl	%eax, %eax
  13bfef:      	leaq	0x59886a(%rip), %rax    # 0x6d4860 <_ZN9QListData11shared_nullE>
  13bff6:      	movq	%rax, (%rsp)
  13bffa:      	movq	(%rsi), %rax
  13bffd:      	movl	(%rax), %ecx
  13bfff:      	movq	%rax, 0x20(%rsp)
  13c004:      	addl	$0x1, %ecx
  13c007:      	cmpl	$0x1, %ecx
  13c00a:      	jbe	0x13c013 <.text+0x1177e3>
  13c00c:      	lock
  13c00d:      	addl	$0x1, (%rax)
  13c010:      	setne	%cl
  13c013:      	leaq	0x10(%rsp), %r13
  13c018:      	movq	%rdx, %rsi
  13c01b:      	movq	%r13, %rdi
  13c01e:      	callq	0x8d130 <.text+0x68900>
  13c023:      	leaq	0x20(%rsp), %rbp
  13c028:      	movl	$0x10, %edi
  13c02d:      	movq	%rsp, %rbx
  13c030:      	callq	0x221f0 <_Znwm@plt>
  13c035:      	leaq	0x20(%rsp), %rbp
  13c03a:      	movq	%rax, %rbx
  13c03d:      	leaq	0x59865c(%rip), %rax    # 0x6d46a0 <_ZN10QArrayData11shared_nullE>
  13c044:      	movq	%rbp, %rsi
  13c047:      	movq	%rbx, %rdi
  13c04a:      	movq	%rax, (%rbx)
  13c04d:      	leaq	0x59880c(%rip), %rax    # 0x6d4860 <_ZN9QListData11shared_nullE>
  13c054:      	movq	%rax, 0x8(%rbx)
  13c058:      	callq	0x24010 <_ZN7QStringaSERKS_@plt>
  13c05d:      	movq	0x10(%rsp), %rax
  13c062:      	leaq	0x30(%rsp), %r14
  13c067:      	cmpq	%rax, 0x8(%rbx)
  13c06b:      	je	0x13c092 <.text+0x117862>
  13c06d:      	movq	%r13, %rsi
  13c070:      	movq	%r14, %rdi
  13c073:      	callq	0x8d130 <.text+0x68900>
  13c078:      	movq	0x30(%rsp), %rax
  13c07d:      	movq	%r14, %rdi
  13c080:      	movq	0x8(%rbx), %rdx
  13c084:      	movq	%rax, 0x8(%rbx)
  13c088:      	movq	%rdx, 0x30(%rsp)
  13c08d:      	callq	0x55ce0 <.text+0x314b0>
  13c092:      	movq	%r14, %rsi
  13c095:      	movq	%rsp, %rdi
  13c098:      	movq	%rbx, 0x30(%rsp)
  13c09d:      	movq	%rsp, %rbx
  13c0a0:      	callq	0xd38d0 <.text+0xaf0a0>
  13c0a5:      	movq	%r13, %rdi
  13c0a8:      	callq	0x55ce0 <.text+0x314b0>
  13c0ad:      	movq	0x20(%rsp), %rdi
  13c0b2:      	movl	(%rdi), %eax
  13c0b4:      	testl	%eax, %eax
  13c0b6:      	jne	0x13c110 <.text+0x1178e0>
  13c0b8:      	movl	$0x8, %edx
  13c0bd:      	movl	$0x2, %esi
  13c0c2:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  13c0c7:      	movq	%rbx, %rsi
  13c0ca:      	movq	%rbp, %rdi
  13c0cd:      	callq	0xd36f0 <.text+0xaeec0>
  13c0d2:      	movq	%rbp, %rsi
  13c0d5:      	movq	%r12, %rdi
  13c0d8:      	callq	0x13bba0 <.text+0x117370>
  13c0dd:      	movq	%rbp, %rdi
  13c0e0:      	callq	0xd3680 <.text+0xaee50>
  13c0e5:      	movq	%rbx, %rdi
  13c0e8:      	callq	0xd3680 <.text+0xaee50>
  13c0ed:      	movq	0x38(%rsp), %rax
  13c0f2:      	xorq	%fs:0x28, %rax
  13c0fb:      	jne	0x13c127 <.text+0x1178f7>
  13c0fd:      	addq	$0x40, %rsp
  13c101:      	popq	%rbx
  13c102:      	popq	%rbp
  13c103:      	popq	%r12
  13c105:      	popq	%r13
  13c107:      	popq	%r14
  13c109:      	retq
  13c10a:      	nopw	(%rax,%rax)
  13c110:      	cmpl	$-0x1, %eax
  13c113:      	je	0x13c0c7 <.text+0x117897>
  13c115:      	lock
  13c116:      	subl	$0x1, (%rdi)
  13c119:      	setne	%al
  13c11c:      	testb	%al, %al
  13c11e:      	jne	0x13c0c7 <.text+0x117897>
  13c120:      	movq	0x20(%rsp), %rdi
  13c125:      	jmp	0x13c0b8 <.text+0x117888>
  13c127:      	callq	0x226b0 <__stack_chk_fail@plt>
  13c12c:      	movq	%rax, %r12
  13c12f:      	movq	%rbp, %rdi
  13c132:      	callq	0xd3680 <.text+0xaee50>
  13c137:      	movq	%r12, %rbp
  13c13a:      	movq	%rbx, %rdi
  13c13d:      	callq	0xd3680 <.text+0xaee50>
  13c142:      	movq	%rbp, %rdi
  13c145:      	callq	0x23190 <_Unwind_Resume@plt>
  13c14a:      	movq	%rax, %rbp
  13c14d:      	jmp	0x13c13a <.text+0x11790a>
  13c14f:      	leaq	0x8(%rbx), %rdi
  13c153:      	movq	%rax, %r12
  13c156:      	callq	0x55ce0 <.text+0x314b0>
  13c15b:      	movq	%rbx, %rdi
  13c15e:      	callq	0x4b960 <.text+0x27130>
  13c163:      	movq	%rbx, %rdi
  13c166:      	movq	%rsp, %rbx
  13c169:      	callq	0x22e40 <_ZdlPv@plt>
  13c16e:      	movq	%r13, %rdi
  13c171:      	callq	0x55ce0 <.text+0x314b0>
  13c176:      	movq	%rbp, %rdi
  13c179:      	movq	%r12, %rbp
  13c17c:      	callq	0x4b960 <.text+0x27130>
  13c181:      	jmp	0x13c13a <.text+0x11790a>
  13c183:      	movq	%rax, %r12
  13c186:      	jmp	0x13c16e <.text+0x11793e>
  13c188:      	leaq	0x20(%rsp), %rbp
  13c18d:      	movq	%rax, %r12
  13c190:      	movq	%rsp, %rbx
  13c193:      	jmp	0x13c176 <.text+0x117946>
  13c1a0:      	pushq	%r15
  13c1a2:      	movq	%rdi, %r15
  13c1a5:      	pushq	%r14
  13c1a7:      	leaq	0xe3aee(%rip), %rdi     # 0x21fc9c
  13c1ae:      	pushq	%r13
  13c1b0:      	pushq	%r12
  13c1b2:      	pushq	%rbp
  13c1b3:      	pushq	%rbx
  13c1b4:      	movq	%rsi, %rbx
  13c1b7:      	movl	$0x1, %esi
  13c1bc:      	subq	$0x48, %rsp
  13c1c0:      	movq	%fs:0x28, %rax
  13c1c9:      	movq	%rax, 0x38(%rsp)
  13c1ce:      	xorl	%eax, %eax
  13c1d0:      	leaq	0x30(%rsp), %r13
  13c1d5:      	movq	%rsp, %r14
  13c1d8:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  13c1dd:      	movl	$0x1, %ecx
  13c1e2:      	movq	%r13, %rdx
  13c1e5:      	movq	%rbx, %rsi
  13c1e8:      	movl	$0x1, %r8d
  13c1ee:      	movq	%rsp, %rdi
  13c1f1:      	movq	%rax, 0x30(%rsp)
  13c1f6:      	callq	0x23480 <_ZNK7QString5splitERKS_NS_13SplitBehaviorEN2Qt15CaseSensitivityE@plt>
  13c1fb:      	movq	0x30(%rsp), %rdi
  13c200:      	movl	(%rdi), %eax
  13c202:      	testl	%eax, %eax
  13c204:      	jne	0x13c330 <.text+0x117b00>
  13c20a:      	movl	$0x8, %edx
  13c20f:      	movl	$0x2, %esi
  13c214:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  13c219:      	movq	(%rsp), %rdx
  13c21d:      	movl	$0x1, %ebp
  13c222:      	movl	$0x1, %ebx
  13c227:      	leaq	0x598632(%rip), %rax    # 0x6d4860 <_ZN9QListData11shared_nullE>
  13c22e:      	movq	%rax, 0x10(%rsp)
  13c233:      	leaq	0x10(%rsp), %r12
  13c238:      	movslq	0x8(%rdx), %rax
  13c23c:      	movl	0xc(%rdx), %ecx
  13c23f:      	subl	%eax, %ecx
  13c241:      	cmpl	$0x1, %ecx
  13c244:      	jle	0x13c374 <.text+0x117b44>
  13c24a:      	nopw	(%rax,%rax)
  13c250:      	addq	%rbp, %rax
  13c253:      	movq	%r12, %rdi
  13c256:      	leaq	0x10(%rdx,%rax,8), %rsi
  13c25b:      	callq	0x4bc80 <.text+0x27450>
  13c260:      	movq	(%rsp), %rdx
  13c264:      	addl	$0x1, %ebx
  13c267:      	addq	$0x1, %rbp
  13c26b:      	movslq	0x8(%rdx), %rax
  13c26f:      	movl	0xc(%rdx), %ecx
  13c272:      	subl	%eax, %ecx
  13c274:      	cmpl	%ebx, %ecx
  13c276:      	jg	0x13c250 <.text+0x117a20>
  13c278:      	movq	%r12, %rsi
  13c27b:      	movq	%r13, %rdi
  13c27e:      	callq	0x8d130 <.text+0x68900>
  13c283:      	movq	(%rsp), %rdx
  13c287:      	movslq	0x8(%rdx), %rax
  13c28b:      	movl	0xc(%rdx), %ecx
  13c28e:      	subl	%eax, %ecx
  13c290:      	testl	%ecx, %ecx
  13c292:      	jle	0x13c3b1 <.text+0x117b81>
  13c298:      	leaq	0x10(%rdx,%rax,8), %rdx
  13c29d:      	movq	(%rdx), %rax
  13c2a0:      	leaq	0x20(%rsp), %rbx
  13c2a5:      	movq	%rax, 0x20(%rsp)
  13c2aa:      	cmpq	%rbx, %rdx
  13c2ad:      	je	0x13c399 <.text+0x117b69>
  13c2b3:      	movl	(%rax), %edi
  13c2b5:      	leal	0x1(%rdi), %edx
  13c2b8:      	cmpl	$0x1, %edx
  13c2bb:      	jbe	0x13c2c4 <.text+0x117a94>
  13c2bd:      	lock
  13c2be:      	addl	$0x1, (%rax)
  13c2c1:      	setne	%dl
  13c2c4:      	movq	%r13, %rdx
  13c2c7:      	movq	%rbx, %rsi
  13c2ca:      	movq	%r15, %rdi
  13c2cd:      	callq	0x13bfd0 <.text+0x1177a0>
  13c2d2:      	movq	0x20(%rsp), %rdi
  13c2d7:      	movl	(%rdi), %eax
  13c2d9:      	testl	%eax, %eax
  13c2db:      	je	0x13c360 <.text+0x117b30>
  13c2e1:      	cmpl	$-0x1, %eax
  13c2e4:      	je	0x13c2f1 <.text+0x117ac1>
  13c2e6:      	lock
  13c2e7:      	subl	$0x1, (%rdi)
  13c2ea:      	setne	%al
  13c2ed:      	testb	%al, %al
  13c2ef:      	je	0x13c352 <.text+0x117b22>
  13c2f1:      	movq	%r13, %rdi
  13c2f4:      	callq	0x55ce0 <.text+0x314b0>
  13c2f9:      	movq	%r12, %rdi
  13c2fc:      	callq	0x55ce0 <.text+0x314b0>
  13c301:      	movq	%r14, %rdi
  13c304:      	callq	0x55ce0 <.text+0x314b0>
  13c309:      	movq	0x38(%rsp), %rax
  13c30e:      	xorq	%fs:0x28, %rax
  13c317:      	jne	0x13c3fb <.text+0x117bcb>
  13c31d:      	addq	$0x48, %rsp
  13c321:      	popq	%rbx
  13c322:      	popq	%rbp
  13c323:      	popq	%r12
  13c325:      	popq	%r13
  13c327:      	popq	%r14
  13c329:      	popq	%r15
  13c32b:      	retq
  13c32c:      	nopl	(%rax)
  13c330:      	cmpl	$-0x1, %eax
  13c333:      	je	0x13c219 <.text+0x1179e9>
  13c339:      	lock
  13c33a:      	subl	$0x1, (%rdi)
  13c33d:      	setne	%al
  13c340:      	testb	%al, %al
  13c342:      	jne	0x13c219 <.text+0x1179e9>
  13c348:      	movq	0x30(%rsp), %rdi
  13c34d:      	jmp	0x13c20a <.text+0x1179da>
  13c352:      	movq	0x20(%rsp), %rdi
  13c357:      	nopw	(%rax,%rax)
  13c360:      	movl	$0x8, %edx
  13c365:      	movl	$0x2, %esi
  13c36a:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  13c36f:      	jmp	0x13c2f1 <.text+0x117ac1>
  13c374:      	leaq	0x10(%rsp), %r12
  13c379:      	jmp	0x13c278 <.text+0x117a48>
  13c37e:      	movq	%rax, %rbx
  13c381:      	movq	%r12, %rdi
  13c384:      	callq	0x55ce0 <.text+0x314b0>
  13c389:      	movq	%r14, %rdi
  13c38c:      	callq	0x55ce0 <.text+0x314b0>
  13c391:      	movq	%rbx, %rdi
  13c394:      	callq	0x23190 <_Unwind_Resume@plt>
  13c399:      	leaq	0xcd7d8(%rip), %rsi     # 0x209b78
  13c3a0:      	movl	$0x32c, %edx            # imm = 0x32C
  13c3a5:      	leaq	0xcd932(%rip), %rdi     # 0x209cde
  13c3ac:      	callq	0x22900 <_Z9qt_assertPKcS0_i@plt>
  13c3b1:      	leaq	0xcd860(%rip), %rdx     # 0x209c18
  13c3b8:      	movl	$0x1de, %ecx            # imm = 0x1DE
  13c3bd:      	leaq	0xcd941(%rip), %rsi     # 0x209d05
  13c3c4:      	leaq	0xcd94d(%rip), %rdi     # 0x209d18
  13c3cb:      	callq	0x227d0 <_Z11qt_assert_xPKcS0_S0_i@plt>
  13c3d0:      	movq	%rbx, %rdi
  13c3d3:      	movq	%rax, %rbp
  13c3d6:      	callq	0x4b960 <.text+0x27130>
  13c3db:      	movq	%r13, %rdi
  13c3de:      	movq	%rbp, %rbx
  13c3e1:      	callq	0x55ce0 <.text+0x314b0>
  13c3e6:      	jmp	0x13c381 <.text+0x117b51>
  13c3e8:      	movq	%rax, %rbx
  13c3eb:      	movq	%r13, %rdi
  13c3ee:      	callq	0x4b960 <.text+0x27130>
  13c3f3:      	movq	%rbx, %rdi
  13c3f6:      	callq	0x23190 <_Unwind_Resume@plt>
  13c3fb:      	callq	0x226b0 <__stack_chk_fail@plt>
  148e70:      	pushq	%r15
  148e72:      	pushq	%r14
  148e74:      	pushq	%r13
  148e76:      	pushq	%r12
  148e78:      	pushq	%rbp
  148e79:      	pushq	%rbx
  148e7a:      	subq	$0x488, %rsp            # imm = 0x488
  148e81:      	movq	0x58cf60(%rip), %rdi    # 0x6d5de8 <_ZN9QListData11shared_nullE+0x1588>
  148e88:      	movq	%fs:0x28, %rax
  148e91:      	movq	%rax, 0x478(%rsp)
  148e99:      	xorl	%eax, %eax
  148e9b:      	testq	%rdi, %rdi
  148e9e:      	je	0x14af60 <.text+0x126730>
  148ea4:      	leaq	0xe4d8d(%rip), %rdx     # 0x22dc38
  148eab:      	xorl	%eax, %eax
  148ead:      	leaq	0xd1919(%rip), %rsi     # 0x21a7cd
  148eb4:      	callq	0x137430 <.text+0x112c00>
  148eb9:      	leaq	0x460(%rsp), %r15
  148ec1:      	movl	$0xd, %esi
  148ec6:      	leaq	0xe4c08(%rip), %rdi     # 0x22dad5
  148ecd:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  148ed2:      	movl	$0x1d, %edx
  148ed7:      	movq	%r15, %rdi
  148eda:      	leaq	0xe4c02(%rip), %rsi     # 0x22dae3
  148ee1:      	movq	%rax, 0xc0(%rsp)
  148ee9:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
  148eee:      	leaq	0xc0(%rsp), %rsi
  148ef6:      	movq	%r15, %rdi
  148ef9:      	movq	%rsi, 0x18(%rsp)
  148efe:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  148f03:      	leaq	0x468(%rsp), %rdi
  148f0b:      	movl	$0x1d, %edx
  148f10:      	leaq	0xe4bea(%rip), %rsi     # 0x22db01
  148f17:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
  148f1c:      	movq	0x18(%rsp), %rsi
  148f21:      	leaq	0x8(%r15), %rdi
  148f25:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  148f2a:      	movq	0x18(%rsp), %r14
  148f2f:      	leaq	0xd0(%rsp), %rax
  148f69:      	leaq	0xe4bc2(%rip), %rdi     # 0x22db32
  148f70:      	movl	$0x9, %esi
  148f75:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  148f7a:      	movq	0x58c50f(%rip), %rsi    # 0x6d5490 <_ZN9QListData11shared_nullE+0xc30>
  148f81:      	movq	%rax, 0xe0(%rsp)
  148f89:      	testq	%rsi, %rsi
  148f8c:      	je	0x14af38 <.text+0x126708>
  148f92:      	leaq	0xf0(%rsp), %rax
  148f9a:      	movq	%rax, %rdi
  148f9d:      	movq	%rax, 0x60(%rsp)
  148fa2:      	callq	0xa2480 <.text+0x7dc50>
  148fa7:      	leaq	0xca148(%rip), %rdi     # 0x2130f6
  148fae:      	movl	$0xf, %esi
  148fb3:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  148fb8:      	movl	(%rax), %ecx
  148fba:      	movq	%rax, 0x450(%rsp)
  148fc2:      	movq	%rax, 0x110(%rsp)
  148fca:      	leal	0x1(%rcx), %edx
  148fcd:      	cmpl	$0x1, %edx
  148fd0:      	jbe	0x148fd9 <.text+0x1247a9>
  148fd2:      	lock
  148fd3:      	addl	$0x1, (%rax)
  148fd6:      	setne	%dl
  148fd9:      	leaq	0x3f0(%rsp), %rax
  148fe1:      	movl	$0xa, %edx
  148fe6:      	leaq	0xcdea5(%rip), %rsi     # 0x216e92
  148fed:      	movq	%rax, %rdi
  148ff0:      	movq	%rax, %r14
  148ff3:      	movq	%rax, 0x78(%rsp)
  148ff8:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
  148ffd:      	leaq	0x110(%rsp), %rbx
  149005:      	movq	%r14, %rsi
  149008:      	movq	%rbx, %rdi
  14900b:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  149010:      	movq	0x3f0(%rsp), %rdi
  149018:      	movl	(%rdi), %eax
  14901a:      	testl	%eax, %eax
  14901c:      	jne	0x14a6b8 <.text+0x125e88>
  149022:      	movl	$0x8, %edx
  149027:      	movl	$0x2, %esi
  14902c:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149031:      	movq	0x110(%rsp), %rax
  149039:      	movl	(%rax), %ecx
  14903b:      	movq	%rax, 0x120(%rsp)
  149043:      	leal	0x1(%rcx), %edx
  149046:      	cmpl	$0x1, %edx
  149049:      	jbe	0x149052 <.text+0x124822>
  14904b:      	lock
  14904c:      	addl	$0x1, (%rax)
  14904f:      	setne	%dl
  149052:      	leaq	0x400(%rsp), %rax
  14905a:      	movl	$0x1, %edx
  14905f:      	leaq	0xe3c05(%rip), %rsi     # 0x22cc6b
  149066:      	movq	%rax, %rdi
  149069:      	movq	%rax, %r14
  14906c:      	movq	%rax, 0x80(%rsp)
  149074:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
  149079:      	leaq	0x120(%rsp), %rbp
  149081:      	movq	%r14, %rsi
  149084:      	movq	%rbp, %rdi
  149087:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  14908c:      	movq	0x400(%rsp), %rdi
  149094:      	movl	(%rdi), %eax
  149096:      	testl	%eax, %eax
  149098:      	jne	0x14a690 <.text+0x125e60>
  14909e:      	movl	$0x8, %edx
  1490a3:      	movl	$0x2, %esi
  1490a8:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  1490ad:      	movq	0x120(%rsp), %rax
  1490b5:      	movl	(%rax), %ecx
  1490b7:      	movq	%rax, 0x100(%rsp)
  1490bf:      	leal	0x1(%rcx), %edx
  1490c2:      	cmpl	$0x1, %edx
  1490c5:      	jbe	0x1490ce <.text+0x12489e>
  1490c7:      	lock
  1490c8:      	addl	$0x1, (%rax)
  1490cb:      	setne	%dl
  1490ce:      	movq	0x60(%rsp), %rsi
  1490d3:      	leaq	0x100(%rsp), %rax
  1490db:      	movq	%rax, %rdi
  1490de:      	movq	%rax, 0x58(%rsp)
  1490e3:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  1490e8:      	movq	0x120(%rsp), %rdi
  1490f0:      	movl	(%rdi), %eax
  1490f2:      	testl	%eax, %eax
  1490f4:      	jne	0x14a668 <.text+0x125e38>
  1490fa:      	movl	$0x8, %edx
  1490ff:      	movl	$0x2, %esi
  149104:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149109:      	movq	0x110(%rsp), %rdi
  149111:      	movl	(%rdi), %eax
  149113:      	testl	%eax, %eax
  149115:      	jne	0x14a640 <.text+0x125e10>
  14911b:      	movl	$0x8, %edx
  149120:      	movl	$0x2, %esi
  149125:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14912a:      	movq	0x450(%rsp), %rdi
  149132:      	movl	(%rdi), %eax
  149134:      	testl	%eax, %eax
  149136:      	jne	0x14a618 <.text+0x125de8>
  14913c:      	movl	$0x8, %edx
  149141:      	movl	$0x2, %esi
  149146:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14914b:      	leaq	0xe49ea(%rip), %rdi     # 0x22db3c
  149152:      	movl	$0xd, %esi
  149157:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  14915c:      	movq	%rax, 0x130(%rsp)
  149164:      	movq	0xf0(%rsp), %rax
  14916c:      	movl	(%rax), %ecx
  14916e:      	movq	%rax, 0x140(%rsp)
  149176:      	leal	0x1(%rcx), %edx
  149179:      	cmpl	$0x1, %edx
  14917c:      	jbe	0x149185 <.text+0x124955>
  14917e:      	lock
  14917f:      	addl	$0x1, (%rax)
  149182:      	setne	%dl
  149185:      	leaq	0x410(%rsp), %rax
  14918d:      	movl	$0x4, %edx
  149192:      	leaq	0x140(%rsp), %rcx
  14919a:      	movq	%rax, %rdi
  14919d:      	movq	%rax, %rbx
  1491a0:      	movq	%rax, 0x88(%rsp)
  1491a8:      	leaq	0xe4996(%rip), %rsi     # 0x22db45
  1491af:      	movq	%rcx, 0x20(%rsp)
  1491b4:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
  1491b9:      	leaq	0x140(%rsp), %rax
  1491c1:      	movq	%rbx, %rsi
  1491c4:      	movq	%rax, %rdi
  1491c7:      	movq	%rax, 0x20(%rsp)
  1491cc:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  1491d1:      	movq	0x410(%rsp), %rdi
  1491d9:      	movl	(%rdi), %eax
  1491db:      	testl	%eax, %eax
  1491dd:      	jne	0x14a5f0 <.text+0x125dc0>
  1491e3:      	movl	$0x8, %edx
  1491e8:      	movl	$0x2, %esi
  1491ed:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  1491f2:      	leaq	0xc9efd(%rip), %rdi     # 0x2130f6
  1491f9:      	movl	$0xf, %esi
  1491fe:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  149203:      	movl	(%rax), %ecx
  149205:      	movq	%rax, 0x440(%rsp)
  14920d:      	movq	%rax, 0x160(%rsp)
  149215:      	leal	0x1(%rcx), %edx
  149218:      	cmpl	$0x1, %edx
  14921b:      	jbe	0x149224 <.text+0x1249f4>
  14921d:      	lock
  14921e:      	addl	$0x1, (%rax)
  149221:      	setne	%dl
  149224:      	leaq	0x420(%rsp), %rax
  14922c:      	movl	$0xa, %edx
  149231:      	leaq	0xcdc5a(%rip), %rsi     # 0x216e92
  149238:      	movq	%rax, %rdi
  14923b:      	movq	%rax, %r14
  14923e:      	movq	%rax, 0x8(%rsp)
  149243:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
  149248:      	leaq	0x160(%rsp), %rbx
  149250:      	movq	%r14, %rsi
  149253:      	movq	%rbx, %rdi
  149256:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  14925b:      	movq	0x420(%rsp), %rdi
  149263:      	movl	(%rdi), %eax
  149265:      	testl	%eax, %eax
  149267:      	jne	0x14a5c8 <.text+0x125d98>
  14926d:      	movl	$0x8, %edx
  149272:      	movl	$0x2, %esi
  149277:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14927c:      	movq	0x160(%rsp), %rax
  149284:      	movl	(%rax), %ecx
  149286:      	movq	%rax, 0x1b0(%rsp)
  14928e:      	leal	0x1(%rcx), %edx
  149291:      	cmpl	$0x1, %edx
  149294:      	jbe	0x14929d <.text+0x124a6d>
  149296:      	lock
  149297:      	addl	$0x1, (%rax)
  14929a:      	setne	%dl
  14929d:      	leaq	0x450(%rsp), %r14
  1492a5:      	movl	$0x1, %edx
  1492aa:      	leaq	0xe39ba(%rip), %rsi     # 0x22cc6b
  1492b1:      	movq	%r14, %rdi
  1492b4:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
  1492b9:      	leaq	0x1b0(%rsp), %rax
  1492c1:      	movq	%r14, %rsi
  1492c4:      	movq	%rax, %rdi
  1492c7:      	movq	%rax, 0x10(%rsp)
  1492cc:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  1492d1:      	movq	0x450(%rsp), %rdi
  1492d9:      	movl	(%rdi), %eax
  1492db:      	testl	%eax, %eax
  1492dd:      	jne	0x14a5a0 <.text+0x125d70>
  1492e3:      	movl	$0x8, %edx
  1492e8:      	movl	$0x2, %esi
  1492ed:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  1492f2:      	movq	0x1b0(%rsp), %rax
  1492fa:      	movl	(%rax), %ecx
  1492fc:      	movq	%rax, 0x150(%rsp)
  149304:      	leal	0x1(%rcx), %edx
  149307:      	cmpl	$0x1, %edx
  14930a:      	jbe	0x149313 <.text+0x124ae3>
  14930c:      	lock
  14930d:      	addl	$0x1, (%rax)
  149310:      	setne	%dl
  149313:      	movq	0x20(%rsp), %rsi
  149318:      	leaq	0x150(%rsp), %rax
  149320:      	movq	%rax, %rdi
  149323:      	movq	%rax, 0x70(%rsp)
  149328:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  14932d:      	movq	0x1b0(%rsp), %rdi
  149335:      	movl	(%rdi), %eax
  149337:      	testl	%eax, %eax
  149339:      	jne	0x14a578 <.text+0x125d48>
  14933f:      	movl	$0x8, %edx
  149344:      	movl	$0x2, %esi
  149349:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14934e:      	movq	0x160(%rsp), %rdi
  149356:      	movl	(%rdi), %eax
  149358:      	testl	%eax, %eax
  14935a:      	jne	0x14a550 <.text+0x125d20>
  149360:      	movl	$0x8, %edx
  149365:      	movl	$0x2, %esi
  14936a:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14936f:      	movq	0x440(%rsp), %rdi
  149377:      	movl	(%rdi), %eax
  149379:      	testl	%eax, %eax
  14937b:      	jne	0x14a528 <.text+0x125cf8>
  149381:      	movl	$0x8, %edx
  149386:      	movl	$0x2, %esi
  14938b:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149390:      	leaq	0x58b309(%rip), %rax    # 0x6d46a0 <_ZN10QArrayData11shared_nullE>
  149397:      	movl	$0x10, %esi
  14939c:      	leaq	0xe47a7(%rip), %rdi     # 0x22db4a
  1493a3:      	movq	%rax, 0x170(%rsp)
  1493ab:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  1493b0:      	movl	$0xf, %esi
  1493b5:      	movq	%rax, 0x180(%rsp)
  1493bd:      	leaq	0xc8ee4(%rip), %rdi     # 0x2122a8
  1493c4:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
  1493c9:      	movq	%rax, 0x190(%rsp)
  149430:      	movq	0x58b451(%rip), %rsi    # 0x6d4888 <_ZN9QListData11shared_nullE+0x28>
  149437:      	movq	%rax, 0x450(%rsp)
  14943f:      	testq	%rsi, %rsi
  149442:      	je	0x14ad10 <.text+0x1264e0>
  149448:      	movq	0x10(%rsp), %rdi
  14944d:      	movq	%r14, %rdx
  149450:      	callq	0x44010 <.text+0x1f7e0>
  149455:      	movq	0x450(%rsp), %rdi
  14945d:      	movl	(%rdi), %eax
  14945f:      	testl	%eax, %eax
  149461:      	jne	0x14a0f0 <.text+0x1258c0>
  149467:      	movl	$0x8, %edx
  14946c:      	movl	$0x2, %esi
  149471:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149476:      	cmpb	$0x0, 0x588c37(%rip)    # 0x6d20b4
  14947d:      	je	0x149b40 <.text+0x125310>
  149483:      	movq	0x1b0(%rsp), %rax
  14948b:      	movl	(%rax), %ecx
  14948d:      	movq	%rax, 0x450(%rsp)
  149495:      	leal	0x1(%rcx), %edx
  149498:      	cmpl	$0x1, %edx
  14949b:      	jbe	0x1494a4 <.text+0x124c74>
  14949d:      	lock
  14949e:      	addl	$0x1, (%rax)
  1494a1:      	setne	%dl
  1494a4:      	movq	0x58b3dd(%rip), %rdi    # 0x6d4888 <_ZN9QListData11shared_nullE+0x28>
  1494ab:      	movl	0x58bb3b(%rip), %ebp    # 0x6d4fec <_ZN9QListData11shared_nullE+0x78c>
  1494b1:      	testq	%rdi, %rdi
  1494b4:      	je	0x14af88 <.text+0x126758>
  1494ba:      	movq	%r14, %rcx
  1494bd:      	movl	$0x1, %edx
  1494c2:      	movl	%ebp, %esi
  1494c4:      	callq	0x47ae0 <.text+0x232b0>
  1494c9:      	movq	0x450(%rsp), %rdi
  1494d1:      	movl	%eax, 0x48(%rsp)
  1494d5:      	movl	(%rdi), %eax
  1494d7:      	testl	%eax, %eax
  1494d9:      	je	0x14a6e8 <.text+0x125eb8>
  1494df:      	cmpl	$-0x1, %eax
  1494e2:      	je	0x1494f3 <.text+0x124cc3>
  1494e4:      	lock
  1494e5:      	subl	$0x1, (%rdi)
  1494e8:      	setne	%al
  1494eb:      	testb	%al, %al
  1494ed:      	je	0x14a6dd <.text+0x125ead>
  1494f3:      	movl	0x48(%rsp), %ebx
  1494f7:      	testl	%ebx, %ebx
  1494f9:      	je	0x149768 <.text+0x124f38>
  1494ff:      	movq	0x58c8e2(%rip), %rdi    # 0x6d5de8 <_ZN9QListData11shared_nullE+0x1588>
  149506:      	testq	%rdi, %rdi
  149509:      	je	0x14b0e8 <.text+0x1268b8>
  14950f:      	movl	0x48(%rsp), %ecx
  149513:      	leaq	0xe0(%rsp), %rax
  14951b:      	movq	%rax, (%rsp)
  14951f:      	leaq	0xe4712(%rip), %rdx     # 0x22dc38
  149526:      	xorl	%eax, %eax
  149528:      	leaq	0xc1f81(%rip), %rsi     # 0x20b4b0
  14952f:      	leaq	0x190(%rsp), %rbp
  149537:      	leaq	0x180(%rsp), %rbx
  14953f:      	leaq	0x130(%rsp), %r12
  149547:      	callq	0x137430 <.text+0x112c00>
  14954c:      	movq	0x1b0(%rsp), %rdi
  149554:      	addl	$0x1, 0x44(%rsp)
  149559:      	movl	(%rdi), %eax
  14955b:      	testl	%eax, %eax
  14955d:      	jne	0x14a0c8 <.text+0x125898>
  149563:      	movl	$0x8, %edx
  149568:      	movl	$0x2, %esi
  14956d:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149572:      	addq	$0x1, %r13
  149576:      	cmpq	$0x2, %r13
  14957a:      	jne	0x14941f <.text+0x124bef>
  149580:      	callq	0x23420 <sync@plt>
  149585:      	cmpl	$0x1, 0x44(%rsp)
  14958a:      	movq	0x1a0(%rsp), %rdi
  149592:      	setg	%bpl
  149596:      	andb	0x588b17(%rip), %bpl    # 0x6d20b4
  14959d:      	movl	(%rdi), %eax
  14959f:      	xorl	$0x1, %ebp
  1495a2:      	testl	%eax, %eax
  1495a4:      	jne	0x14aa40 <.text+0x126210>
  149b40:      	movq	(%r15,%r13,8), %rsi
  149b44:      	movl	(%rsi), %eax
  149b46:      	movq	%rsi, 0x3f0(%rsp)
  149b4e:      	addl	$0x1, %eax
  149b51:      	cmpl	$0x1, %eax
  149b54:      	jbe	0x149b65 <.text+0x125335>
  149b56:      	lock
  149b57:      	addl	$0x1, (%rsi)
  149b5a:      	setne	%al
  149b5d:      	movq	0x3f0(%rsp), %rsi
  149b65:      	movl	0x4(%rsi), %edx
  149b68:      	movq	0x10(%rsi), %rax
  149b6c:      	testl	%edx, %edx
  149b6e:      	je	0x149b7a <.text+0x12534a>
  149b70:      	cmpq	$0x17, %rax
  149b74:      	jbe	0x14b130 <.text+0x126900>
  149b7a:      	movq	0x28(%rsp), %rdi
  149b7f:      	addq	%rax, %rsi
  149b82:      	callq	0x22470 <_ZN7QString18toLocal8Bit_helperEPK5QChari@plt>
  149b87:      	movq	0x290(%rsp), %rax
  149b8f:      	movl	0x4(%rax), %r11d
  149b93:      	movq	0x10(%rax), %rbx
  149b97:      	testl	%r11d, %r11d
  149b9a:      	je	0x149ba6 <.text+0x125376>
  149b9c:      	cmpq	$0x17, %rbx
  149ba0:      	jbe	0x14b130 <.text+0x126900>
  149ba6:      	movq	0x58c23b(%rip), %rdi    # 0x6d5de8 <_ZN9QListData11shared_nullE+0x1588>
  149bad:      	addq	%rax, %rbx
  149bb0:      	testq	%rdi, %rdi
  149bb3:      	je	0x14af10 <.text+0x1266e0>
  149bb9:      	leaq	0xe3f9b(%rip), %rsi     # 0x22db5b
  149bc0:      	movq	%rbx, %rdx
  149bc3:      	xorl	%eax, %eax
  149bc5:      	callq	0x137430 <.text+0x112c00>
  149bca:      	movq	0x290(%rsp), %rdi
  149bd2:      	movl	(%rdi), %eax
  149bd4:      	testl	%eax, %eax
  149bd6:      	jne	0x14a140 <.text+0x125910>
  149bdc:      	movl	$0x8, %edx
  149be1:      	movl	$0x1, %esi
  149be6:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149beb:      	movq	0x3f0(%rsp), %rdi
  149bf3:      	movl	(%rdi), %eax
  149bf5:      	testl	%eax, %eax
  149bf7:      	jne	0x14a118 <.text+0x1258e8>
  149bfd:      	movl	$0x8, %edx
  149c02:      	movl	$0x2, %esi
  149c07:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149c0c:      	movq	(%r15,%r13,8), %rax
  149c10:      	movl	(%rax), %ecx
  149c12:      	movq	%rax, 0x450(%rsp)
  149c1a:      	leal	0x1(%rcx), %edx
  149c1d:      	cmpl	$0x1, %edx
  149c20:      	jbe	0x149c29 <.text+0x1253f9>
  149c22:      	lock
  149c23:      	addl	$0x1, (%rax)
  149c26:      	setne	%dl
  149c29:      	movq	0x58c2d0(%rip), %rdi    # 0x6d5f00 <_ZN9QListData11shared_nullE+0x16a0>
  149c30:      	testq	%rdi, %rdi
  149c33:      	je	0x14aeb0 <.text+0x126680>
  149c39:      	movq	%r14, %rsi
  149c3c:      	callq	0x13c1a0 <.text+0x117970>
  149c41:      	movq	0x450(%rsp), %rdi
  149c49:      	movl	(%rdi), %eax
  149c4b:      	testl	%eax, %eax
  149c4d:      	jne	0x14a500 <.text+0x125cd0>
  149c53:      	movl	$0x8, %edx
  149c58:      	movl	$0x2, %esi
  149c5d:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  149c62:      	leaq	0xe0(%rsp), %rax
  149c6a:      	movl	$0x2710, %edi           # imm = 0x2710
  149c6f:      	movq	%rax, (%rsp)
  149c73:      	leaq	0x190(%rsp), %rbp
  149c7b:      	leaq	0x180(%rsp), %rbx
  149c83:      	leaq	0x130(%rsp), %r12
  149c8b:      	callq	0x241d0 <usleep@plt>
  149c90:      	cmpb	$0x0, 0x58841d(%rip)    # 0x6d20b4
  149c97:      	je	0x14a168 <.text+0x125938>
  149c9d:      	movq	0x58c25c(%rip), %rdi    # 0x6d5f00 <_ZN9QListData11shared_nullE+0x16a0>
  149ca4:      	testq	%rdi, %rdi
  149ca7:      	je	0x14b068 <.text+0x126838>
  149cad:      	leaq	0xe0(%rsp), %rax
  149cb5:      	leaq	0x1a0(%rsp), %rsi
  149cbd:      	movq	%rax, (%rsp)
  149cc1:      	leaq	0x190(%rsp), %rbp
  149cc9:      	leaq	0x180(%rsp), %rbx
  149cd1:      	leaq	0x130(%rsp), %r12
  149cd9:      	callq	0x1397c0 <.text+0x114f90>
  149cde:      	movq	0xc0(%rsp), %rax
  149fe2:      	movq	0x50(%rsp), %rdi
  149fe7:      	addq	%rax, %rsi
  149fea:      	callq	0x22470 <_ZN7QString18toLocal8Bit_helperEPK5QChari@plt>
  149fef:      	movq	0x3e0(%rsp), %rax
  149ff7:      	movl	0x4(%rax), %edx
  149ffa:      	movq	0x10(%rax), %rdi
  149ffe:      	testl	%edx, %edx
  14a000:      	je	0x14a00c <.text+0x1257dc>
  14a002:      	cmpq	$0x17, %rdi
  14a006:      	jbe	0x14b130 <.text+0x126900>
  14a00c:      	addq	%rax, %rdi
  14a00f:      	callq	0x245e0 <umount@plt>
  14a014:      	movq	0x3e0(%rsp), %rdi
  14a01c:      	movl	%eax, %ebx
  14a01e:      	movl	(%rdi), %eax
  14a020:      	testl	%eax, %eax
  14a022:      	jne	0x14a9a0 <.text+0x126170>
  14a028:      	movl	$0x8, %edx
  14a02d:      	movl	$0x1, %esi
  14a032:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14a037:      	movq	0x440(%rsp), %rdi
  14a03f:      	movl	(%rdi), %eax
  14a041:      	testl	%eax, %eax
  14a043:      	jne	0x14a978 <.text+0x126148>
  14a049:      	movl	$0x8, %edx
  14a04e:      	movl	$0x2, %esi
  14a053:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14a058:      	testl	%ebx, %ebx
  14a05a:      	je	0x14a083 <.text+0x125853>
  14a05c:      	movq	0x58bd85(%rip), %rdi    # 0x6d5de8 <_ZN9QListData11shared_nullE+0x1588>
  14a063:      	testq	%rdi, %rdi
  14a066:      	je	0x14afb0 <.text+0x126780>
  14a06c:      	leaq	0xe3bc5(%rip), %rdx     # 0x22dc38
  14a073:      	movl	%ebx, %ecx
  14a075:      	xorl	%eax, %eax
  14a077:      	leaq	0xe3b24(%rip), %rsi     # 0x22dba2
  14a07e:      	callq	0x137430 <.text+0x112c00>
  14a083:      	movl	$0x2710, %edi           # imm = 0x2710
  14a088:      	callq	0x241d0 <usleep@plt>
  14a08d:      	movq	%r14, %rdi
  14a090:      	callq	0x22c70 <_ZN5QFileD1Ev@plt>
  14a095:      	movq	0x420(%rsp), %rdi
  14a09d:      	movl	(%rdi), %eax
  14a09f:      	testl	%eax, %eax
  14a0a1:      	jne	0x14a9c8 <.text+0x126198>
  14a0a7:      	movl	$0x8, %edx
  14a0ac:      	movl	$0x2, %esi
  14a0b1:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14a168:      	movq	0xc0(%rsp), %rax
  14a170:      	movl	(%rax), %ecx
  14a172:      	movq	%rax, 0x300(%rsp)
  14a17a:      	leal	0x1(%rcx), %edx
  14a17d:      	cmpl	$0x1, %edx
  14a180:      	jbe	0x14a189 <.text+0x125959>
  14a182:      	lock
  14a183:      	addl	$0x1, (%rax)
  14a186:      	setne	%dl
  14a189:      	movq	0x38(%rsp), %rdi
  14a18e:      	leaq	0xe0(%rsp), %rax
  14a196:      	movq	%rax, %rsi
  14a199:      	movq	%rax, (%rsp)
  14a19d:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  14a1a2:      	movq	0x58bd57(%rip), %rdi    # 0x6d5f00 <_ZN9QListData11shared_nullE+0x16a0>
  14a1a9:      	testq	%rdi, %rdi
  14a1ac:      	je	0x14afd8 <.text+0x1267a8>
  14a1b2:      	movq	0x38(%rsp), %rdx
  14a1b7:      	xorl	%ecx, %ecx
  14a1b9:      	movq	0x58(%rsp), %rsi
  14a1be:      	callq	0x1413f0 <.text+0x11cbc0>
  14a1c3:      	movq	0x300(%rsp), %rdi
  14a1cb:      	movl	%eax, %ebx
  14a1cd:      	movl	(%rdi), %edx
  14a1cf:      	testl	%edx, %edx
  14a1d1:      	je	0x14a708 <.text+0x125ed8>
  14a1d7:      	cmpl	$-0x1, %edx
  14a1da:      	je	0x14a1eb <.text+0x1259bb>
  14a1dc:      	lock
  14a1dd:      	subl	$0x1, (%rdi)
  14a1e0:      	setne	%al
  14a1e3:      	testb	%al, %al
  14a1e5:      	je	0x14a6fc <.text+0x125ecc>
  14a1eb:      	movq	0xc0(%rsp), %rax
  14a1f3:      	testb	%bl, %bl
  14a1f5:      	je	0x14a727 <.text+0x125ef7>
  14a1fb:      	movl	(%rax), %ecx
  14a1fd:      	movq	%rax, 0x320(%rsp)
  14a205:      	leal	0x1(%rcx), %edx
  14a208:      	cmpl	$0x1, %edx
  14a20b:      	jbe	0x14a214 <.text+0x1259e4>
  14a20d:      	lock
  14a20e:      	addl	$0x1, (%rax)
  14a211:      	setne	%dl
  14a214:      	movq	(%rsp), %rsi
  14a218:      	leaq	0x320(%rsp), %r12
  14a220:      	movq	%r12, %rdi
  14a223:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
  14a228:      	movq	0x320(%rsp), %rax
  14a230:      	movl	0x4(%rax), %edx
  14a233:      	movq	0x10(%rax), %rsi
  14a237:      	testl	%edx, %edx
  14a239:      	je	0x14a245 <.text+0x125a15>
  14a23b:      	cmpq	$0x17, %rsi
  14a23f:      	jbe	0x14b130 <.text+0x126900>
  14a245:      	leaq	0x330(%rsp), %rcx
  14a24d:      	addq	%rax, %rsi
  14a250:      	movq	%rcx, %rdi
  14a253:      	movq	%rcx, 0x90(%rsp)
  14a25b:      	callq	0x22470 <_ZN7QString18toLocal8Bit_helperEPK5QChari@plt>
  14a260:      	movq	0x330(%rsp), %rax
  14a268:      	movl	0x4(%rax), %r8d
  14a26c:      	movq	0x10(%rax), %rbp
  14a270:      	testl	%r8d, %r8d
  14a273:      	je	0x14a27f <.text+0x125a4f>
  14a275:      	cmpq	$0x17, %rbp
  14a279:      	jbe	0x14b130 <.text+0x126900>
  14a27f:      	movq	0xf0(%rsp), %rsi
  14a287:      	addq	%rbp, %rax
  14a28a:      	movq	%rax, 0x48(%rsp)
  14a28f:      	movl	(%rsi), %eax
  14a291:      	movq	%rsi, 0x410(%rsp)
  14a299:      	addl	$0x1, %eax
  14a29c:      	cmpl	$0x1, %eax
  14a29f:      	jbe	0x14a2b0 <.text+0x125a80>
  14a2a1:      	lock
  14a2a2:      	addl	$0x1, (%rsi)
  14a2a5:      	setne	%al
  14a2a8:      	movq	0x410(%rsp), %rsi
  14a2b0:      	movl	0x4(%rsi), %edx
  14a2b3:      	movq	0x10(%rsi), %rax
  14a2b7:      	testl	%edx, %edx
  14a2b9:      	je	0x14a2c5 <.text+0x125a95>
  14a2bb:      	cmpq	$0x17, %rax
  14a2bf:      	jbe	0x14b130 <.text+0x126900>
  14a2c5:      	leaq	0x310(%rsp), %rbp
  14a2cd:      	addq	%rax, %rsi
  14a2d0:      	movq	%rbp, %rdi
  14a2d3:      	callq	0x22470 <_ZN7QString18toLocal8Bit_helperEPK5QChari@plt>
  14a2d8:      	movq	0x310(%rsp), %rax
  14a2e0:      	movl	0x4(%rax), %edi
  14a2e3:      	movq	0x10(%rax), %rbx
  14a2e7:      	testl	%edi, %edi
  14a2e9:      	je	0x14a2f5 <.text+0x125ac5>
  14a2eb:      	cmpq	$0x17, %rbx
  14a2ef:      	jbe	0x14b130 <.text+0x126900>
  14a2f5:      	movq	0x58baec(%rip), %rdi    # 0x6d5de8 <_ZN9QListData11shared_nullE+0x1588>
  14a2fc:      	addq	%rax, %rbx
  14a2ff:      	testq	%rdi, %rdi
  14a302:      	je	0x14b150 <.text+0x126920>
  14a308:      	movq	0x48(%rsp), %r8
  14a30d:      	movq	%rbx, %rcx
  14a310:      	xorl	%eax, %eax
  14a312:      	leaq	0xe391f(%rip), %rdx     # 0x22dc38
  14a319:      	leaq	0xe384b(%rip), %rsi     # 0x22db6b
  14a320:      	callq	0x137430 <.text+0x112c00>
  14a325:      	movq	0x310(%rsp), %rdi
  14a32d:      	movl	(%rdi), %eax
  14a32f:      	testl	%eax, %eax
  14a331:      	je	0x14ad90 <.text+0x126560>
  14a337:      	cmpl	$-0x1, %eax
  14a33a:      	je	0x14a34b <.text+0x125b1b>
  14a33c:      	lock
  14a33d:      	subl	$0x1, (%rdi)
  14a340:      	setne	%al
  14a343:      	testb	%al, %al
  14a345:      	je	0x14ad86 <.text+0x126556>
  14a34b:      	movq	0x410(%rsp), %rdi
  14a353:      	movl	(%rdi), %eax
  14a355:      	testl	%eax, %eax
  14a357:      	jne	0x14adb1 <.text+0x126581>
  14a35d:      	movl	$0x8, %edx
  14a362:      	movl	$0x2, %esi
  14a367:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14a36c:      	movq	0x330(%rsp), %rdi
  14a374:      	movl	(%rdi), %eax
  14a376:      	testl	%eax, %eax
  14a378:      	jne	0x14ae88 <.text+0x126658>
  14a37e:      	movl	$0x8, %edx
  14a383:      	movl	$0x1, %esi
  14a388:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14a38d:      	movq	0x320(%rsp), %rdi
  14a395:      	movl	(%rdi), %eax
  14a397:      	testl	%eax, %eax
  14a399:      	jne	0x14ae10 <.text+0x1265e0>
  14a39f:      	movl	$0x8, %edx
  14a3a4:      	movl	$0x2, %esi
  14a3a9:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
  14a3ae:      	cmpq	$0x1, %r13
  14a3b2:      	jne	0x149ef7 <.text+0x1256c7>
  14a3b8:      	movq	0x18(%rsp), %rsi
  14a3bd:      	leaq	0x340(%rsp), %rax
  14a3c5:      	leaq	0x130(%rsp), %r12
  14a3cd:      	movq	%rax, %rdi
  14a3d0:      	movq	%rax, 0x48(%rsp)
  14a3d5:      	leaq	0x190(%rsp), %rbp
  14a3dd:      	movq	%r12, %rdx
  14a3e0:      	leaq	0x180(%rsp), %rbx
  14a3e8:      	callq	0x662d0 <.text+0x41aa0>
  14a3ed:      	callq	0x66460 <.text+0x41c30>
  14a3f2:      	movq	0x48(%rsp), %rbp
  14a3f7:      	xorl	%ecx, %ecx
  14a3f9:      	movq	%rax, %rdi
  14a3fc:      	movq	0x70(%rsp), %rsi
  14a401:      	movq	%rbp, %rdx
  14a404:      	callq	0x1413f0 <.text+0x11cbc0>
  14a409:      	movl	%eax, %ebx
  14a40b:      	movq	%rbp, %rdi
  14a40e:      	callq	0x4b960 <.text+0x27130>
  14a413:      	testb	%bl, %bl
  14a415:      	je	0x14ba6d <.text+0x12723d>
  14a41b:      	movq	0x18(%rsp), %rsi
  14a420:      	leaq	0x360(%rsp), %rax
  14a428:      	movq	%r12, %rdx
  14b55c:      	leaq	0x190(%rsp), %rbp
  14b564:      	leaq	0x180(%rsp), %rbx
  14b56c:      	leaq	0x130(%rsp), %r12
  14b574:      	callq	0x66460 <.text+0x41c30>
  14b579:      	leaq	0x170(%rsp), %rsi
  14b581:      	movq	%rax, %rdi
  14b584:      	leaq	0x190(%rsp), %rbp
  14b58c:      	leaq	0x180(%rsp), %rbx
  14b594:      	leaq	0x130(%rsp), %r12
  14b59c:      	callq	0x1397c0 <.text+0x114f90>
  14b5a1:      	movq	0x18(%rsp), %rsi
