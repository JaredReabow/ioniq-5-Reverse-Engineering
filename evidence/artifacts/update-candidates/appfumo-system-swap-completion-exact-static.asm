# AppFUMO system-swap completion exact-static excerpt
# ELF SHA-256: 464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7
# Build ID: 863a8730e66a1c5245a1bf458fe2554adee0351a
# Raw VAs shown; Ghidra VAs are raw + 0x100000.
# Execution-free; downstream handling does not prove successful writes or boot.

   8ed40:      	pushq	%rbp
   8ed41:      	pushq	%rbx
   8ed42:      	movq	%rdi, %rbx
   8ed45:      	subq	$0x18, %rsp
   8ed49:      	movzbl	0x44(%rdi), %ebp
   8ed4d:      	movq	%fs:0x28, %rax
   8ed56:      	movq	%rax, 0x8(%rsp)
   8ed5b:      	xorl	%eax, %eax
   8ed5d:      	callq	0x55c60 <.text+0x31430>
   8ed62:      	leaq	0x187267(%rip), %rdx    # 0x215fd0
   8ed69:      	leaq	0x185560(%rip), %rsi    # 0x2142d0
   8ed70:      	movq	%rax, %rdi
   8ed73:      	xorl	%eax, %eax
   8ed75:      	movl	%ebp, %ecx
   8ed77:      	callq	0x137430 <.text+0x112c00>
   8ed7c:      	movzbl	0x44(%rbx), %eax
   8ed80:      	movq	0x8(%rsp), %rdx
   8ed85:      	xorq	%fs:0x28, %rdx
   8ed8e:      	jne	0x8ed97 <.text+0x6a567>
   8ed90:      	addq	$0x18, %rsp
   8ed94:      	popq	%rbx
   8ed95:      	popq	%rbp
   8ed96:      	retq
   8ed97:      	callq	0x226b0 <__stack_chk_fail@plt>
   8ee00:      	pushq	%rbp
   8ee01:      	pushq	%rbx
   8ee02:      	movq	%rdi, %rbx
   8ee05:      	subq	$0x18, %rsp
   8ee09:      	movzbl	0x45(%rdi), %ebp
   8ee0d:      	movq	%fs:0x28, %rax
   8ee16:      	movq	%rax, 0x8(%rsp)
   8ee1b:      	xorl	%eax, %eax
   8ee1d:      	callq	0x55c60 <.text+0x31430>
   8ee22:      	leaq	0x18717f(%rip), %rdx    # 0x215fa8
   8ee29:      	leaq	0x186221(%rip), %rsi    # 0x215051
   8ee30:      	movq	%rax, %rdi
   8ee33:      	xorl	%eax, %eax
   8ee35:      	movl	%ebp, %ecx
   8ee37:      	callq	0x137430 <.text+0x112c00>
   8ee3c:      	movzbl	0x45(%rbx), %eax
   8ee40:      	movq	0x8(%rsp), %rdx
   8ee45:      	xorq	%fs:0x28, %rdx
   8ee4e:      	jne	0x8ee57 <.text+0x6a627>
   8ee50:      	addq	$0x18, %rsp
   8ee54:      	popq	%rbx
   8ee55:      	popq	%rbp
   8ee56:      	retq
   8ee57:      	callq	0x226b0 <__stack_chk_fail@plt>
   8eec0:      	pushq	%rbp
   8eec1:      	pushq	%rbx
   8eec2:      	movq	%rdi, %rbx
   8eec5:      	subq	$0x18, %rsp
   8eec9:      	movzbl	0x46(%rdi), %ebp
   8eecd:      	movq	%fs:0x28, %rax
   8eed6:      	movq	%rax, 0x8(%rsp)
   8eedb:      	xorl	%eax, %eax
   8eedd:      	callq	0x55c60 <.text+0x31430>
   8eee2:      	leaq	0x18709f(%rip), %rdx    # 0x215f88
   8eee9:      	leaq	0x18617c(%rip), %rsi    # 0x21506c
   8eef0:      	movq	%rax, %rdi
   8eef3:      	xorl	%eax, %eax
   8eef5:      	movl	%ebp, %ecx
   8eef7:      	callq	0x137430 <.text+0x112c00>
   8eefc:      	movzbl	0x46(%rbx), %eax
   8ef00:      	movq	0x8(%rsp), %rdx
   8ef05:      	xorq	%fs:0x28, %rdx
   8ef0e:      	jne	0x8ef17 <.text+0x6a6e7>
   8ef10:      	addq	$0x18, %rsp
   8ef14:      	popq	%rbx
   8ef15:      	popq	%rbp
   8ef16:      	retq
   8ef17:      	callq	0x226b0 <__stack_chk_fail@plt>
   8f100:      	pushq	%rbp
   8f101:      	pushq	%rbx
   8f102:      	movq	%rdi, %rbx
   8f105:      	subq	$0x18, %rsp
   8f109:      	movzbl	0x47(%rdi), %ebp
   8f10d:      	movq	%fs:0x28, %rax
   8f116:      	movq	%rax, 0x8(%rsp)
   8f11b:      	xorl	%eax, %eax
   8f11d:      	callq	0x55c60 <.text+0x31430>
   8f122:      	leaq	0x186de7(%rip), %rdx    # 0x215f10
   8f129:      	leaq	0x1851c8(%rip), %rsi    # 0x2142f8
   8f130:      	movq	%rax, %rdi
   8f133:      	xorl	%eax, %eax
   8f135:      	movl	%ebp, %ecx
   8f137:      	callq	0x137430 <.text+0x112c00>
   8f13c:      	movzbl	0x47(%rbx), %eax
   8f140:      	movq	0x8(%rsp), %rdx
   8f145:      	xorq	%fs:0x28, %rdx
   8f14e:      	jne	0x8f157 <.text+0x6a927>
   8f150:      	addq	$0x18, %rsp
   8f154:      	popq	%rbx
   8f155:      	popq	%rbp
   8f156:      	retq
   8f157:      	callq	0x226b0 <__stack_chk_fail@plt>
   edef0:      	pushq	%r15
   edef2:      	leaq	0x126b5f(%rip), %rdi    # 0x214a58
   edef9:      	movl	$0x1f, %esi
   edefe:      	pushq	%r14
   edf00:      	pushq	%r13
   edf02:      	pushq	%r12
   edf04:      	pushq	%rbp
   edf05:      	pushq	%rbx
   edf06:      	subq	$0x98, %rsp
   edf0d:      	movq	%fs:0x28, %rax
   edf16:      	movq	%rax, 0x88(%rsp)
   edf1e:      	xorl	%eax, %eax
   edf20:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   edf25:      	leaq	0x20(%rsp), %rbx
   edf2a:      	movq	%rax, 0x10(%rsp)
   edf2f:      	leaq	0x10(%rsp), %rsi
   edf34:      	movq	%rbx, %rdi
   edf37:      	callq	0x24320 <_ZN4QDirC1ERK7QString@plt>
   edf3c:      	movq	%rbx, %rdi
   edf3f:      	callq	0x23aa0 <_ZNK4QDir6existsEv@plt>
   edf44:      	movl	%eax, %r13d
   edf47:      	movl	$0x1, %r15d
   edf4d:      	testb	%al, %al
   edf4f:      	je	0xee000 <.text+0xc97d0>
   edf55:      	movq	%rbx, %rdi
   edf58:      	callq	0x22580 <_ZN4QDirD1Ev@plt>
   edf5d:      	movq	0x10(%rsp), %rdi
   edf62:      	movl	(%rdi), %eax
   edf64:      	testl	%eax, %eax
   edf66:      	jne	0xedfe0 <.text+0xc97b0>
   edf68:      	movl	$0x8, %edx
   edf6d:      	movl	$0x2, %esi
   edf72:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   edf77:      	movq	0x5e7e6a(%rip), %rdi    # 0x6d5de8 <_ZN9QListData11shared_nullE+0x1588>
   edf7e:      	testq	%rdi, %rdi
   edf81:      	je	0xee058 <.text+0xc9828>
   edf87:      	xorl	%eax, %eax
   edf89:      	movl	$0x3635, %ecx           # imm = 0x3635
   edf8e:      	movl	%r15d, %r9d
   edf91:      	leaq	0x13b228(%rip), %r8     # 0x2291c0
   edf98:      	leaq	0x130b87(%rip), %rdx    # 0x21eb26
   edf9f:      	leaq	0x133d3a(%rip), %rsi    # 0x221ce0
   edfa6:      	callq	0x137430 <.text+0x112c00>
   edfab:      	movl	%r13d, %eax
   edfae:      	movq	0x88(%rsp), %rcx
   edfb6:      	xorq	%fs:0x28, %rcx
   edfbf:      	jne	0xee12a <.text+0xc98fa>
   edfc5:      	addq	$0x98, %rsp
   edfcc:      	popq	%rbx
   edfcd:      	popq	%rbp
   edfce:      	popq	%r12
   edfd0:      	popq	%r13
   edfd2:      	popq	%r14
   edfd4:      	popq	%r15
   edfd6:      	retq
   edfd7:      	nopw	(%rax,%rax)
   edfe0:      	cmpl	$-0x1, %eax
   edfe3:      	je	0xedf77 <.text+0xc9747>
   edfe5:      	lock
   edfe6:      	subl	$0x1, (%rdi)
   edfe9:      	setne	%al
   edfec:      	testb	%al, %al
   edfee:      	jne	0xedf77 <.text+0xc9747>
   edff0:      	movq	0x10(%rsp), %rdi
   edff5:      	jmp	0xedf68 <.text+0xc9738>
   edffa:      	nopw	(%rax,%rax)
   ee000:      	leaq	0x126a71(%rip), %rdi    # 0x214a78
   ee007:      	movl	$0x1f, %esi
   ee00c:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   ee011:      	leaq	0x30(%rsp), %r12
   ee016:      	movq	%rax, 0x30(%rsp)
   ee01b:      	leaq	0x40(%rsp), %rbp
   ee020:      	movq	%r12, %rsi
   ee023:      	movq	%rbp, %rdi
   ee026:      	callq	0x24320 <_ZN4QDirC1ERK7QString@plt>
   ee02b:      	movq	%rbp, %rdi
   ee02e:      	callq	0x23aa0 <_ZNK4QDir6existsEv@plt>
   ee033:      	movl	%eax, %r13d
   ee036:      	movl	$0x1, %r15d
   ee03c:      	testb	%al, %al
   ee03e:      	je	0xee080 <.text+0xc9850>
   ee040:      	movq	%rbp, %rdi
   ee043:      	callq	0x22580 <_ZN4QDirD1Ev@plt>
   ee048:      	movq	%r12, %rdi
   ee04b:      	callq	0x4b960 <.text+0x27130>
   ee050:      	jmp	0xedf55 <.text+0xc9725>
   ee055:      	nopl	(%rax)
   ee058:      	movl	$0x8, %edi
   ee05d:      	callq	0x221f0 <_Znwm@plt>
   ee062:      	movq	%rax, %rdi
   ee065:      	movq	%rax, %rbx
   ee068:      	callq	0x1376a0 <.text+0x112e70>
   ee06d:      	movq	%rbx, 0x5e7d74(%rip)    # 0x6d5de8 <_ZN9QListData11shared_nullE+0x1588>
   ee074:      	movq	%rbx, %rdi
   ee077:      	jmp	0xedf87 <.text+0xc9757>
   ee07c:      	nopl	(%rax)
   ee080:      	leaq	0x50(%rsp), %rax
   ee085:      	leaq	0x126a0c(%rip), %rsi    # 0x214a98
   ee08c:      	movq	%rax, %rdi
   ee08f:      	movq	%rax, (%rsp)
   ee093:      	callq	0x55b90 <.text+0x31360>
   ee098:      	movq	(%rsp), %rsi
   ee09c:      	leaq	0x60(%rsp), %r14
   ee0a1:      	movq	%r14, %rdi
   ee0a4:      	callq	0x24320 <_ZN4QDirC1ERK7QString@plt>
   ee0a9:      	movq	%r14, %rdi
   ee0ac:      	callq	0x23aa0 <_ZNK4QDir6existsEv@plt>
   ee0b1:      	movl	%eax, %r13d
   ee0b4:      	movl	$0x1, %r15d
   ee0ba:      	testb	%al, %al
   ee0bc:      	je	0xee0d8 <.text+0xc98a8>
   ee0be:      	movq	%r14, %rdi
   ee0c1:      	callq	0x22580 <_ZN4QDirD1Ev@plt>
   ee0c6:      	movq	(%rsp), %rdi
   ee0ca:      	callq	0x4b960 <.text+0x27130>
   ee0cf:      	jmp	0xee040 <.text+0xc9810>
   ee0d4:      	nopl	(%rax)
   ee0d8:      	leaq	0x70(%rsp), %rax
   ee0dd:      	leaq	0x12694c(%rip), %rsi    # 0x214a30
   ee0e4:      	movq	%rax, %rdi
   ee0e7:      	movq	%rax, %r13
   ee0ea:      	movq	%rax, 0x8(%rsp)
   ee0ef:      	callq	0x55b90 <.text+0x31360>
   ee0f4:      	leaq	0x80(%rsp), %r15
   ee0fc:      	movq	%r13, %rsi
   ee0ff:      	movq	%r15, %rdi
   ee102:      	callq	0x24320 <_ZN4QDirC1ERK7QString@plt>
   ee107:      	movq	%r15, %rdi
   ee10a:      	callq	0x23aa0 <_ZNK4QDir6existsEv@plt>
   ee10f:      	movq	%r15, %rdi
   ee112:      	movl	%eax, %r13d
   ee115:      	callq	0x22580 <_ZN4QDirD1Ev@plt>
   ee11a:      	movq	0x8(%rsp), %rdi
   ee11f:      	movzbl	%r13b, %r15d
   ee123:      	callq	0x4b960 <.text+0x27130>
   ee128:      	jmp	0xee0be <.text+0xc988e>
   ee12a:      	callq	0x226b0 <__stack_chk_fail@plt>
   ee12f:      	movq	%rax, %rbx
  11f620:      	movq	0x40(%rbx), %rdi
  11f624:      	callq	0x8ee00 <.text+0x6a5d0>
  11f629:      	testb	%al, %al
  11f62b:      	jne	0x11fdf0 <.text+0xfb5c0>
  11f631:      	movzbl	0x240(%rbx), %ebp
  11f638:      	callq	0x55c60 <.text+0x31430>
  11f63d:      	movq	%rax, %rdi
  11f640:      	movl	%ebp, %r9d
  11f643:      	movl	$0xd0c, %ecx            # imm = 0xD0C
  11f648:      	leaq	0x10acb1(%rip), %r8     # 0x22a300
  11f64f:      	xorl	%eax, %eax
  11f651:      	leaq	0xff4ce(%rip), %rdx     # 0x21eb26
  11f658:      	leaq	0x105d39(%rip), %rsi    # 0x225398
  11f65f:      	callq	0x137430 <.text+0x112c00>
  11f664:      	movq	%rbx, %rdi
  11f667:      	callq	0xedef0 <.text+0xc96c0>
  11f66c:      	testb	%al, %al
  11f66e:      	je	0x11f83c <.text+0xfb00c>
  11f674:      	cmpb	$0x0, 0x240(%rbx)
  11f67b:      	je	0x11f83c <.text+0xfb00c>
  11f681:      	callq	0x55c60 <.text+0x31430>
  11f686:      	leaq	0x10ac73(%rip), %r8     # 0x22a300
  11f68d:      	movq	%rax, %rdi
  11f690:      	movl	$0xd0e, %ecx            # imm = 0xD0E
  11f695:      	leaq	0xff48a(%rip), %rdx     # 0x21eb26
  11f69c:      	xorl	%eax, %eax
  11f69e:      	leaq	0x105d7b(%rip), %rsi    # 0x225420
  11f6a5:      	callq	0x137430 <.text+0x112c00>
  11f6aa:      	leaq	0x130(%rsp), %rbp
  11f6b2:      	leaq	0x104457(%rip), %rsi    # 0x223b10
  11f6b9:      	movq	%rbp, %rdi
  11f6bc:      	callq	0x55b90 <.text+0x31360>
  11f6c1:      	leaq	0x120(%rsp), %r13
  11f6c9:      	leaq	0x10106d(%rip), %rsi    # 0x22073d
  11f6d0:      	movq	%r13, %rdi
  11f6d3:      	callq	0x55b90 <.text+0x31360>
  11f6d8:      	leaq	0x140(%rsp), %r15
  11f6e0:      	movl	$0x20, %r8d
  11f6e6:      	xorl	%ecx, %ecx
  11f6e8:      	movq	%rbp, %rdx
  11f6eb:      	movq	%r13, %rsi
  11f6ee:      	movq	%r15, %rdi
  11f6f1:      	callq	0x22c30 <_ZNK7QString3argERKS_i5QChar@plt>
  11f6f6:      	movq	%r15, %rdi
  11f6f9:      	callq	0x23900 <_ZN8QProcess7executeERK7QString@plt>
  11f6fe:      	movq	%r15, %rdi
  11f701:      	callq	0x4b960 <.text+0x27130>
  11f706:      	movq	%r13, %rdi
  11f709:      	callq	0x4b960 <.text+0x27130>
  11f70e:      	movq	%rbp, %rdi
  11f711:      	callq	0x4b960 <.text+0x27130>
  11f716:      	leaq	0x150(%rsp), %rbp
  11f71e:      	leaq	0x105d4b(%rip), %rsi    # 0x225470
  11f725:      	movq	%rbp, %rdi
  11f728:      	callq	0x55b90 <.text+0x31360>
  11f72d:      	leaq	0x360(%rsp), %r13
  11f735:      	movq	%rbp, %rsi
  11f738:      	movq	%r13, %rdi
  11f73b:      	callq	0x22d00 <_ZN5QFileC1ERK7QString@plt>
  11f740:      	movq	%r13, %rdi
  11f743:      	callq	0x237c0 <_ZN5QFile6removeEv@plt>
  11f748:      	movq	%r13, %rdi
  11f74b:      	callq	0x22c70 <_ZN5QFileD1Ev@plt>
  11f750:      	movq	%rbp, %rdi
  11f753:      	callq	0x4b960 <.text+0x27130>
  11f758:      	leaq	0x170(%rsp), %rbp
  11f760:      	leaq	0x105d09(%rip), %rsi    # 0x225470
  11f767:      	movq	%rbp, %rdi
  11f76a:      	callq	0x55b90 <.text+0x31360>
  11f76f:      	leaq	0x160(%rsp), %r13
  11f777:      	leaq	0x100fbf(%rip), %rsi    # 0x22073d
  11f77e:      	movq	%r13, %rdi
  11f781:      	callq	0x55b90 <.text+0x31360>
  11f786:      	leaq	0x180(%rsp), %r15
  11f78e:      	movl	$0x20, %r8d
  11f794:      	xorl	%ecx, %ecx
  11f796:      	movq	%rbp, %rdx
  11f799:      	movq	%r13, %rsi
  11f79c:      	movq	%r15, %rdi
  11f79f:      	callq	0x22c30 <_ZNK7QString3argERKS_i5QChar@plt>
  11f7a4:      	movq	%r15, %rdi
  11f7a7:      	callq	0x23900 <_ZN8QProcess7executeERK7QString@plt>
  11f7ac:      	movq	%r15, %rdi
  11f7af:      	callq	0x4b960 <.text+0x27130>
  11f7b4:      	movq	%r13, %rdi
  11f7b7:      	callq	0x4b960 <.text+0x27130>
  11f7bc:      	movq	%rbp, %rdi
  11f7bf:      	callq	0x4b960 <.text+0x27130>
  11f7c4:      	movl	$0x1, %edi
  11f7c9:      	callq	0x24390 <sleep@plt>
  11f7ce:      	leaq	0x1a0(%rsp), %rbp
  11f7d6:      	leaq	0x10e51f(%rip), %rsi    # 0x22dcfc
  11f7dd:      	movq	%rbp, %rdi
  11f7e0:      	callq	0x55b90 <.text+0x31360>
  11f7e5:      	leaq	0x190(%rsp), %r13
  11f7ed:      	leaq	0x102c84(%rip), %rsi    # 0x222478
  11f7f4:      	movq	%r13, %rdi
  11f7f7:      	callq	0x55b90 <.text+0x31360>
  11f7fc:      	callq	0x66460 <.text+0x41c30>
  11f801:      	movq	%rbp, %rdx
  11f804:      	movq	%r13, %rsi
  11f807:      	movq	%rax, %rdi
  11f80a:      	callq	0x140a50 <.text+0x11c220>
  11f80f:      	movq	%r13, %rdi
  11f812:      	callq	0x4b960 <.text+0x27130>
  11f817:      	movq	%rbp, %rdi
  11f81a:      	callq	0x4b960 <.text+0x27130>
  11f81f:      	callq	0x55c60 <.text+0x31430>
  11f824:      	leaq	0x10aaf5(%rip), %rdx    # 0x22a320
  11f82b:      	movq	%rax, %rdi
  11f82e:      	xorl	%eax, %eax
  11f830:      	leaq	0x105c61(%rip), %rsi    # 0x225498
  11f837:      	callq	0x137430 <.text+0x112c00>
  11f83c:      	movq	0x40(%rbx), %rdi
  11f840:      	callq	0x8eec0 <.text+0x6a690>
  11f845:      	testb	%al, %al
  11f847:      	je	0x11f880 <.text+0xfb050>
  11f84d:      	cmpb	$0x0, 0x241(%rbx)
  11f854:      	jne	0x11f880 <.text+0xfb050>
  11f856:      	movq	0x40(%rbx), %rdi
  11f85a:      	callq	0x8ed40 <.text+0x6a510>
  11f85f:      	testb	%al, %al
  11f861:      	je	0x1204c0 <.text+0xfbc90>
  11f867:      	movq	0x238(%rbx), %rdi
  11f86e:      	callq	0x148010 <.text+0x1237e0>
  11f873:      	testb	%al, %al
  11f875:      	je	0x11f880 <.text+0xfb050>
  11f877:      	movb	$0x1, 0x241(%rbx)
  11f87e:      	nop
  11f880:      	movq	0x40(%rbx), %rdi
  11f884:      	callq	0x8f100 <.text+0x6a8d0>
  11f889:      	testb	%al, %al
  11f88b:      	jne	0x11fe10 <.text+0xfb5e0>
  11f891:      	leaq	0x1b0(%rsp), %rbp
  11f899:      	leaq	0xeadb8(%rip), %rsi     # 0x20a658
  11f8a0:      	movq	%rbp, %rdi
  11f8a3:      	callq	0x55b90 <.text+0x31360>
  11f8a8:      	callq	0x66460 <.text+0x41c30>
  11f8ad:      	movq	%rbp, %rsi
  11f8b0:      	movq	%rax, %rdi
  11f8b3:      	callq	0x13feb0 <.text+0x11b680>
  11f8b8:      	movq	%rbp, %rdi
  11f8bb:      	callq	0x4b960 <.text+0x27130>
  120038:      	movq	0x238(%rbx), %rdi
  12003f:      	callq	0x148e70 <.text+0x124640>
  120044:      	testb	%al, %al
  120046:      	je	0x11f631 <.text+0xfae01>
  12004c:      	movb	$0x1, 0x240(%rbx)
  120053:      	movl	$0x1, %ebp
  120058:      	jmp	0x11f638 <.text+0xfae08>
  1200c8:      	movq	%rbx, %rdi
  1200cb:      	callq	0xea450 <.text+0xc5c20>
  1200d0:      	leaq	0x105491(%rip), %rdi    # 0x225568
  1200d7:      	callq	0x24790 <system@plt>
  1200dc:      	callq	0x55c60 <.text+0x31430>
  1200e1:      	leaq	0x10a238(%rip), %rdx    # 0x22a320
  1200e8:      	movq	%rax, %rdi
  1200eb:      	xorl	%eax, %eax
  1200ed:      	leaq	0x10066d(%rip), %rsi    # 0x220761
  1200f4:      	callq	0x137430 <.text+0x112c00>
  13feb0:      	pushq	%r13
  13feb2:      	movq	%rsi, %r13
  13feb5:      	pushq	%r12
  13feb7:      	pushq	%rbp
  13feb8:      	pushq	%rbx
  13feb9:      	subq	$0x48, %rsp
  13febd:      	movq	%fs:0x28, %rax
  13fec6:      	movq	%rax, 0x38(%rsp)
  13fecb:      	xorl	%eax, %eax
  13fecd:      	leaq	0x20(%rsp), %rbx
  13fed2:      	movq	%rbx, %rdi
  13fed5:      	callq	0x22d00 <_ZN5QFileC1ERK7QString@plt>
  13feda:      	movq	%rbx, %rdi
  13fedd:      	callq	0x239a0 <_ZNK5QFile6existsEv@plt>
  13fee2:      	testb	%al, %al
  13fee4:      	je	0x13ff70 <.text+0x11b740>
  13feea:      	movq	%rbx, %rdi
  13feed:      	callq	0x237c0 <_ZN5QFile6removeEv@plt>
  13fef2:      	leaq	0x10(%rsp), %r12
  13fef7:      	movq	%r13, %rsi
  13fefa:      	movq	%rsp, %rbp
  13fefd:      	movq	%r12, %rdi
  13ff00:      	callq	0x55bf0 <.text+0x313c0>
  13ff05:      	movq	%r12, %rsi
  13ff08:      	movq	%rsp, %rdi
  13ff0b:      	callq	0x55b20 <.text+0x312f0>
  13ff10:      	movq	(%rsp), %rdi
  13ff14:      	callq	0x55ac0 <.text+0x31290>
  13ff19:      	movq	%rax, %r13
  13ff1c:      	callq	0x55c60 <.text+0x31430>
  13ff21:      	leaq	0xed4b0(%rip), %rdx     # 0x22d3d8
  13ff28:      	movq	%rax, %rdi
  13ff2b:      	movq	%r13, %rcx
  13ff2e:      	leaq	0xeceb0(%rip), %rsi     # 0x22cde5
  13ff35:      	xorl	%eax, %eax
  13ff37:      	callq	0x137430 <.text+0x112c00>
  13ff3c:      	movq	%rsp, %rdi
  13ff3f:      	callq	0x4b8e0 <.text+0x270b0>
  13ff44:      	movq	%r12, %rdi
  13ff47:      	callq	0x4b960 <.text+0x27130>
  13ff4c:      	movq	%rbx, %rdi
  13ff4f:      	callq	0x22c70 <_ZN5QFileD1Ev@plt>
  13ff54:      	movq	0x38(%rsp), %rax
  13ff59:      	xorq	%fs:0x28, %rax
  13ff62:      	jne	0x13ffd0 <.text+0x11b7a0>
  13ff64:      	addq	$0x48, %rsp
  13ff68:      	popq	%rbx
  13ff69:      	popq	%rbp
  13ff6a:      	popq	%r12
  13ff6c:      	popq	%r13
  13ff6e:      	retq
  13ff6f:      	nop
  13ff70:      	movq	%r13, %rsi
  13ff73:      	movq	%rsp, %rdi
  13ff76:      	movq	%rsp, %rbp
  13ff79:      	callq	0x55bf0 <.text+0x313c0>
  13ff7e:      	leaq	0x10(%rsp), %r12
  13ff83:      	movq	%rsp, %rsi
  13ff86:      	movq	%r12, %rdi
  13ff89:      	callq	0x55b20 <.text+0x312f0>
  13ff8e:      	movq	0x10(%rsp), %rdi
  13ff93:      	callq	0x55ac0 <.text+0x31290>
  13ff98:      	movq	%rax, %r13
  13ff9b:      	callq	0x55c60 <.text+0x31430>
  13ffa0:      	leaq	0xed431(%rip), %rdx     # 0x22d3d8
  13ffa7:      	movq	%rax, %rdi
  13ffaa:      	movq	%r13, %rcx
  13ffad:      	leaq	0xece49(%rip), %rsi     # 0x22cdfd
  13ffb4:      	xorl	%eax, %eax
  13ffb6:      	callq	0x137430 <.text+0x112c00>
  13ffbb:      	movq	%r12, %rdi
  13ffbe:      	callq	0x4b8e0 <.text+0x270b0>
  13ffc3:      	movq	%rsp, %rdi
  13ffc6:      	callq	0x4b960 <.text+0x27130>
  13ffcb:      	jmp	0x13ff4c <.text+0x11b71c>
  13ffd0:      	callq	0x226b0 <__stack_chk_fail@plt>
  13ffd5:      	movq	%rax, %r13
  13ffd8:      	movq	%rbp, %rdi
  13ffdb:      	callq	0x4b8e0 <.text+0x270b0>
  13ffe0:      	movq	%r13, %rbp
  13ffe3:      	movq	%r12, %rdi
  13ffe6:      	callq	0x4b960 <.text+0x27130>
  13ffeb:      	movq	%rbx, %rdi
  13ffee:      	callq	0x22c70 <_ZN5QFileD1Ev@plt>
  13fff3:      	movq	%rbp, %rdi
  13fff6:      	callq	0x23190 <_Unwind_Resume@plt>
  13fffb:      	movq	%rax, %rbp
  13fffe:      	jmp	0x13ffe3 <.text+0x11b7b3>
  140000:      	movq	%rax, %rbp
  140003:      	jmp	0x13ffeb <.text+0x11b7bb>
  140005:      	movq	%rax, %r13
  140008:      	movq	%r12, %rdi
  14000b:      	callq	0x4b8e0 <.text+0x270b0>
  140010:      	movq	%r13, %r12
  140013:      	movq	%rbp, %rdi
  140016:      	movq	%r12, %rbp
  140019:      	callq	0x4b960 <.text+0x27130>
  14001e:      	jmp	0x13ffeb <.text+0x11b7bb>
  140020:      	movq	%rax, %r12
  140023:      	jmp	0x140013 <.text+0x11b7e3>
