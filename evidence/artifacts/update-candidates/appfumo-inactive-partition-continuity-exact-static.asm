# AppFUMO inactive-partition continuity exact-static excerpts
# Source ELF SHA-256: 464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7
# Build ID: 863a8730e66a1c5245a1bf458fe2554adee0351a
# Disassembler: Homebrew LLVM; raw AppFUMO VAs (Ghidra addresses add 0x100000).

## [0xa14c0, 0xa1530)
   a14c0:      	pushq	%r15
   a14c2:      	movq	%rdx, %r15
   a14c5:      	pushq	%r14
   a14c7:      	movq	%rdi, %r14
   a14ca:      	pushq	%r13
   a14cc:      	movq	%rsi, %r13
   a14cf:      	xorl	%esi, %esi
   a14d1:      	pushq	%r12
   a14d3:      	pushq	%rbp
   a14d4:      	pushq	%rbx
   a14d5:      	subq	$0x3b8, %rsp            # imm = 0x3B8
   a14dc:      	movq	%fs:0x28, %rax
   a14e5:      	movq	%rax, 0x3a8(%rsp)
   a14ed:      	xorl	%eax, %eax
   a14ef:      	leaq	0x80(%rsp), %rbx
   a14f7:      	movq	%rdx, 0x18(%rsp)
   a14fc:      	movl	$0x320, %edx            # imm = 0x320
   a1501:      	movq	%rbx, %rdi
   a1504:      	callq	0x22790 <memset@plt>
   a1509:      	leaq	0x623c90(%rip), %rsi    # 0x6c51a0
   a1510:      	movl	$0xa0, %edx
   a1515:      	movq	%rbx, %rdi
   a1518:      	callq	0x22010 <memcpy@plt>
   a151d:      	movq	(%r15), %rsi
   a1520:      	movl	(%rsi), %eax
   a1522:      	movq	%rsi, 0x50(%rsp)
   a1527:      	addl	$0x1, %eax
   a152a:      	cmpl	$0x1, %eax
   a152d:      	jbe	0xa153b <.text+0x7cd0b>
   a152f:      	lock

## [0xa1740, 0xa1870)
   a1741:      	je	0xa166f <.text+0x7ce3f>
   a1747:      	lock
   a1748:      	subl	$0x1, (%rdi)
   a174b:      	setne	%al
   a174e:      	testb	%al, %al
   a1750:      	jne	0xa166f <.text+0x7ce3f>
   a1756:      	movq	0x30(%rsp), %rdi
   a175b:      	jmp	0xa1660 <.text+0x7ce30>
   a1760:      	cmpl	$-0x1, %eax
   a1763:      	je	0xa16ab <.text+0x7ce7b>
   a1769:      	lock
   a176a:      	subl	$0x1, (%rdi)
   a176d:      	setne	%al
   a1770:      	testb	%al, %al
   a1772:      	jne	0xa16ab <.text+0x7ce7b>
   a1778:      	movq	0x50(%rsp), %rdi
   a177d:      	jmp	0xa169c <.text+0x7ce6c>
   a1782:      	nopw	(%rax,%rax)
   a1788:      	cmpl	$-0x1, %eax
   a178b:      	je	0xa168d <.text+0x7ce5d>
   a1791:      	lock
   a1792:      	subl	$0x1, (%rdi)
   a1795:      	setne	%al
   a1798:      	testb	%al, %al
   a179a:      	jne	0xa168d <.text+0x7ce5d>
   a17a0:      	movq	0x60(%rsp), %rdi
   a17a5:      	jmp	0xa167e <.text+0x7ce4e>
   a17aa:      	nopw	(%rax,%rax)
   a17b0:      	movq	0x80(%rsp), %r15
   a17b8:      	addq	$0x50, %rbx
   a17bc:      	xorl	%r12d, %r12d
   a17bf:      	leaq	0x70(%rsp), %r13
   a17c4:      	testq	%r15, %r15
   a17c7:      	jne	0xa1807 <.text+0x7cfd7>
   a17c9:      	jmp	0xa16e1 <.text+0x7ceb1>
   a17ce:      	nop
   a17d0:      	movl	$0x8, %edx
   a17d5:      	movl	$0x2, %esi
   a17da:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a17df:      	testl	%r15d, %r15d
   a17e2:      	je	0xa18a0 <.text+0x7d070>
   a17e8:      	addl	$0x1, %r12d
   a17ec:      	cmpl	$0xa, %r12d
   a17f0:      	je	0xa16e1 <.text+0x7ceb1>
   a17f6:      	addq	$0x50, %rbx
   a17fa:      	movq	-0x50(%rbx), %r15
   a17fe:      	testq	%r15, %r15
   a1801:      	je	0xa16e1 <.text+0x7ceb1>
   a1807:      	movq	%rbp, %rsi
   a180a:      	movq	%r13, %rdi
   a180d:      	callq	0x229d0 <_ZNK7QString7toLowerEv@plt>
   a1812:      	movq	0x70(%rsp), %rax
   a1817:      	movl	0x4(%rax), %esi
   a181a:      	movq	0x10(%rax), %rdi
   a181e:      	testl	%esi, %esi
   a1820:      	je	0xa182c <.text+0x7cffc>
   a1822:      	cmpq	$0x17, %rdi
   a1826:      	jbe	0xa18b9 <.text+0x7d089>
   a182c:      	addq	%rax, %rdi
   a182f:      	movl	$0x1, %r8d
   a1835:      	movl	$0xffffffff, %ecx       # imm = 0xFFFFFFFF
   a183a:      	movq	%r15, %rdx
   a183d:      	callq	0x23630 <_ZN7QString14compare_helperEPK5QChariPKciN2Qt15CaseSensitivityE@plt>
   a1842:      	movq	0x70(%rsp), %rdi
   a1847:      	movl	%eax, %r15d
   a184a:      	movl	(%rdi), %edx
   a184c:      	testl	%edx, %edx
   a184e:      	je	0xa17d0 <.text+0x7cfa0>
   a1850:      	cmpl	$-0x1, %edx
   a1853:      	je	0xa17df <.text+0x7cfaf>
   a1855:      	lock
   a1856:      	subl	$0x1, (%rdi)
   a1859:      	setne	%dl
   a185c:      	testb	%dl, %dl
   a185e:      	jne	0xa17df <.text+0x7cfaf>
   a1864:      	movq	0x70(%rsp), %rdi
   a1869:      	jmp	0xa17d0 <.text+0x7cfa0>
   a186e:      	nop

## [0xa1bf0, 0xa1c30)
   a1bf0:      	movq	0x633769(%rip), %rdi    # 0x6d5360 <_ZN9QListData11shared_nullE+0xb00>
   a1bf7:      	callq	0x8e840 <.text+0x6a010>
   a1bfc:      	movl	$0x4, %esi
   a1c01:      	leaq	0x17e39f(%rip), %rdi    # 0x21ffa7
   a1c08:      	testb	%al, %al
   a1c0a:      	je	0xa1ec0 <.text+0x7d690>
   a1c10:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a1c15:      	leaq	0x10(%rsp), %r12
   a1c1a:      	movq	%rsp, %rdx
   a1c1d:      	movq	%rbx, %rsi
   a1c20:      	movq	%r12, %rdi
   a1c23:      	movq	%rax, (%rsp)
   a1c27:      	movq	%rsp, %rbp
   a1c2a:      	callq	0xa14c0 <.text+0x7cc90>
   a1c2f:      	movq	0x10(%rsp), %rsi

## [0xa1c70, 0xa1c86)
   a1c72:      	leaq	0x631427(%rip), %rdi    # 0x6d30a0
   a1c79:      	addq	%rbp, %rsi
   a1c7c:      	movl	$0x10, %edx
   a1c81:      	callq	0x221e0 <strncpy@plt>

## [0xa1ec0, 0xa1ef0)
   a1ec0:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a1ec5:      	leaq	0xa0(%rsp), %r12
   a1ecd:      	movq	%rbx, %rsi
   a1ed0:      	leaq	0x90(%rsp), %rbp
   a1ed8:      	movq	%r12, %rdi
   a1edb:      	movq	%rax, 0x90(%rsp)
   a1ee3:      	movq	%rbp, %rdx
   a1ee6:      	callq	0xa14c0 <.text+0x7cc90>
   a1eeb:      	movq	0xa0(%rsp), %rsi

## [0xa1f30, 0xa1f49)
   a1f35:      	leaq	0x631b24(%rip), %rdi    # 0x6d3a60
   a1f3c:      	addq	%rbp, %rsi
   a1f3f:      	movl	$0x10, %edx
   a1f44:      	callq	0x221e0 <strncpy@plt>

## [0xa0d50, 0xa0dc3)
   a0d50:      	pushq	%rbp
   a0d51:      	movq	%rdi, %rbp
   a0d54:      	pushq	%rbx
   a0d55:      	movslq	%edx, %rbx
   a0d58:      	subq	$0x18, %rsp
   a0d5c:      	movq	0x6345fd(%rip), %rdi    # 0x6d5360 <_ZN9QListData11shared_nullE+0xb00>
   a0d63:      	movq	%fs:0x28, %rax
   a0d6c:      	movq	%rax, 0x8(%rsp)
   a0d71:      	xorl	%eax, %eax
   a0d73:      	callq	0x8e840 <.text+0x6a010>
   a0d78:      	testb	%al, %al
   a0d7a:      	je	0xa0dd0 <.text+0x7c5a0>
   a0d7c:      	cmpl	$0xa, %ebx
   a0d7f:      	movl	$0x0, %eax
   a0d84:      	movl	$0xf8, %edx
   a0d89:      	cmovaeq	%rax, %rbx
   a0d8d:      	movq	%rbp, %rdi
   a0d90:      	leaq	(,%rbx,8), %rax
   a0d98:      	shlq	$0x8, %rbx
   a0d9c:      	leaq	0x6321dd(%rip), %rsi    # 0x6d2f80
   a0da3:      	subq	%rax, %rbx
   a0da6:      	addq	%rbx, %rsi
   a0da9:      	callq	0x22010 <memcpy@plt>
   a0dae:      	movq	0x8(%rsp), %rcx
   a0db3:      	xorq	%fs:0x28, %rcx
   a0dbc:      	movq	%rbp, %rax
   a0dbf:      	jne	0xa0e04 <.text+0x7c5d4>
   a0dc1:      	addq	$0x18, %rsp

## [0xbfb20, 0xbfc25)
   bfb20:      	pushq	%r14
   bfb22:      	pushq	%r13
   bfb24:      	movq	%rsi, %r13
   bfb27:      	pushq	%r12
   bfb29:      	pushq	%rbp
   bfb2a:      	pushq	%rbx
   bfb2b:      	xorl	%ebx, %ebx
   bfb2d:      	subq	$0x120, %rsp            # imm = 0x120
   bfb34:      	movq	%fs:0x28, %rax
   bfb3d:      	movq	%rax, 0x118(%rsp)
   bfb45:      	xorl	%eax, %eax
   bfb47:      	leaq	0x20(%rsp), %rbp
   bfb4c:      	leaq	0x10(%rsp), %r12
   bfb51:      	jmp	0xbfb7c <.text+0x9b34c>
   bfb53:      	nopl	(%rax,%rax)
   bfb58:      	movl	$0x8, %edx
   bfb5d:      	movl	$0x2, %esi
   bfb62:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   bfb67:      	testb	%r14b, %r14b
   bfb6a:      	jne	0xbfd90 <.text+0x9b560>
   bfb70:      	addl	$0x1, %ebx
   bfb73:      	cmpl	$0xa, %ebx
   bfb76:      	je	0xbfc50 <.text+0x9b420>
   bfb7c:      	movq	0x61590d(%rip), %rsi    # 0x6d5490 <_ZN9QListData11shared_nullE+0xc30>
   bfb83:      	testq	%rsi, %rsi
   bfb86:      	je	0xbfc20 <.text+0x9b3f0>
   bfb8c:      	movl	%ebx, %edx
   bfb8e:      	movq	%rbp, %rdi
   bfb91:      	callq	0xa0d50 <.text+0x7c520>
   bfb96:      	movq	%rbp, %rsi
   bfb99:      	movl	(%rsi), %eax
   bfb9b:      	addq	$0x4, %rsi
   bfb9f:      	leal	-0x1010101(%rax), %edx
   bfba5:      	notl	%eax
   bfba7:      	andl	%eax, %edx
   bfba9:      	andl	$0x80808080, %edx       # imm = 0x80808080
   bfbaf:      	je	0xbfb99 <.text+0x9b369>
   bfbb1:      	movl	%edx, %eax
   bfbb3:      	movq	%rbp, %rdi
   bfbb6:      	shrl	$0x10, %eax
   bfbb9:      	testl	$0x8080, %edx           # imm = 0x8080
   bfbbf:      	cmovel	%eax, %edx
   bfbc2:      	leaq	0x2(%rsi), %rax
   bfbc6:      	cmoveq	%rax, %rsi
   bfbca:      	addb	%dl, %dl
   bfbcc:      	sbbq	$0x3, %rsi
   bfbd0:      	subq	%rbp, %rsi
   bfbd3:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   bfbd8:      	movq	%r13, %rsi
   bfbdb:      	movq	%r12, %rdi
   bfbde:      	movq	%rax, 0x10(%rsp)
   bfbe3:      	callq	0x229e0 <_ZeqRK7QStringS1_@plt>
   bfbe8:      	movq	0x10(%rsp), %rdi
   bfbed:      	movl	%eax, %r14d
   bfbf0:      	movl	(%rdi), %eax
   bfbf2:      	testl	%eax, %eax
   bfbf4:      	je	0xbfb58 <.text+0x9b328>
   bfbfa:      	cmpl	$-0x1, %eax
   bfbfd:      	je	0xbfb67 <.text+0x9b337>
   bfc03:      	lock
   bfc04:      	subl	$0x1, (%rdi)
   bfc07:      	setne	%al
   bfc0a:      	testb	%al, %al
   bfc0c:      	jne	0xbfb67 <.text+0x9b337>
   bfc12:      	movq	0x10(%rsp), %rdi
   bfc17:      	jmp	0xbfb58 <.text+0x9b328>
   bfc1c:      	nopl	(%rax)
   bfc20:      	movl	$0x18, %edi

## [0xc541a, 0xc5449)
   c541a:      	movl	0x98(%r15), %esi
   c5421:      	leaq	0x28(%r15), %rax
   c5425:      	movq	%rax, %rdi
   c5428:      	movq	%rax, -0x1730(%rbp)
   c542f:      	callq	0x78480 <.text+0x53c50>
   c5434:      	movq	%r13, %rdi
   c5437:      	movq	(%rax), %rsi
   c543a:      	addq	$0x20, %rsi
   c543e:      	callq	0x55bf0 <.text+0x313c0>
   c5443:      	cmpb	$0x0, 0x39(%r15)
   c5448:      	je	0xc5498 <.text+0xa0c68>

## [0xc54c4, 0xc554a)
   c54c4:      	movq	%r13, %rsi
   c54c7:      	movq	%r15, %rdi
   c54ca:      	callq	0xbfb20 <.text+0x9b2f0>
   c54cf:      	leaq	-0x340(%rbp), %r14
   c54d6:      	movq	%r13, %rsi
   c54d9:      	movl	%eax, %r12d
   c54dc:      	movl	%eax, -0x1748(%rbp)
   c54e2:      	leaq	-0x1700(%rbp), %rbx
   c54e9:      	movq	%r14, %rdi
   c54ec:      	callq	0x55bf0 <.text+0x313c0>
   c54f1:      	movq	%r14, %rsi
   c54f4:      	movq	%rbx, %rdi
   c54f7:      	callq	0x55b20 <.text+0x312f0>
   c54fc:      	movq	-0x1700(%rbp), %rdi
   c5503:      	callq	0x55ac0 <.text+0x31290>
   c5508:      	movq	%rax, -0x1718(%rbp)
   c550f:      	callq	0x55c60 <.text+0x31430>
   c5514:      	movq	-0x1718(%rbp), %rcx
   c551b:      	movq	%rax, %rdi
   c551e:      	movl	%r12d, %r8d
   c5521:      	xorl	%eax, %eax
   c5523:      	leaq	0x1557d6(%rip), %rdx    # 0x21ad00
   c552a:      	leaq	0x154237(%rip), %rsi    # 0x219768
   c5531:      	callq	0x137430 <.text+0x112c00>
   c5536:      	movq	%rbx, %rdi
   c5539:      	callq	0x4b8e0 <.text+0x270b0>
   c553e:      	movq	%r14, %rdi
   c5541:      	callq	0x4b960 <.text+0x27130>
   c5546:      	testl	%r12d, %r12d
   c5549:      	js	0xc5990 <.text+0xa1160>

## [0xc608d, 0xc60c4)
   c608d:      	cmpl	$0x9, -0x1748(%rbp)
   c6094:      	movl	%eax, -0x17a0(%rbp)
   c609a:      	leaq	0x60e5ff(%rip), %rax    # 0x6d46a0 <_ZN10QArrayData11shared_nullE>
   c60a1:      	movq	%rax, -0x1360(%rbp)
   c60a8:      	ja	0xc7db0 <.text+0xa3580>
   c60ae:      	movl	-0x1748(%rbp), %edx
   c60b4:      	leaq	0x1549a5(%rip), %rax    # 0x21aa60
   c60bb:      	movslq	(%rax,%rdx,4), %rdx
   c60bf:      	addq	%rdx, %rax
   c60c2:      	jmpq	*%rax

## [0xc765b, 0xc7699)
   c765b:      	callq	0xae6c0 <.text+0x89e90>
   c7660:      	leaq	-0x16d0(%rbp), %rcx
   c7667:      	movl	$0x1, %edx
   c766c:      	movq	%rax, %rsi
   c766f:      	movq	%rcx, -0x1758(%rbp)
   c7676:      	leaq	-0x330(%rbp), %rdi
   c767d:      	leaq	-0x1360(%rbp), %rcx
   c7684:      	movq	%rcx, -0x1760(%rbp)
   c768b:      	callq	0xa0d50 <.text+0x7c520>
   c7690:      	cmpq	$0x0, -0x258(%rbp)
   c7698:      	leaq	-0x16d0(%rbp), %rax

## [0xc7822, 0xc792c)
   c7822:      	callq	0xae6c0 <.text+0x89e90>
   c7827:      	movl	$0x1, %edx
   c782c:      	movq	%rax, %rsi
   c782f:      	movq	%rbx, %rdi
   c7832:      	callq	0xa0d50 <.text+0x7c520>
   c7837:      	movq	-0x50(%rbp), %rax
   c783b:      	movq	%rax, -0x1748(%rbp)
   c7842:      	callq	0xae6c0 <.text+0x89e90>
   c7847:      	leaq	-0x230(%rbp), %rcx
   c784e:      	movl	$0x1, %edx
   c7853:      	movq	%rax, %rsi
   c7856:      	movq	%rcx, %rdi
   c7859:      	movq	%rcx, %rbx
   c785c:      	callq	0xa0d50 <.text+0x7c520>
   c7861:      	movq	%rbx, %rsi
   c7864:      	leaq	-0x1330(%rbp), %rbx
   c786b:      	addq	$0x28, %rsi
   c786f:      	movq	%rbx, %rdi
   c7872:      	callq	0x55b90 <.text+0x31360>
   c7877:      	leaq	-0x1320(%rbp), %rax
   c787e:      	movq	%rbx, %rdx
   c7881:      	leaq	0x152e65(%rip), %rsi    # 0x21a6ed
   c7888:      	movq	%rax, %rdi
   c788b:      	movq	%rax, %r12
   c788e:      	callq	0xd3600 <.text+0xaedd0>
   c7893:      	leaq	-0x1310(%rbp), %rax
   c789a:      	movq	%r12, %rsi
   c789d:      	movq	%r12, -0x1768(%rbp)
   c78a4:      	leaq	0x1583f1(%rip), %rdx    # 0x21fc9c
   c78ab:      	movq	%rax, %rdi
   c78ae:      	movq	%rax, %r12
   c78b1:      	callq	0x66360 <.text+0x41b30>
   c78b6:      	movq	-0x1748(%rbp), %rdx
   c78bd:      	leaq	-0x1300(%rbp), %rax
   c78c4:      	movq	%r12, %rsi
   c78c7:      	movq	%r12, -0x1780(%rbp)
   c78ce:      	movq	%rax, %rdi
   c78d1:      	movq	%rax, -0x1748(%rbp)
   c78d8:      	callq	0x66360 <.text+0x41b30>
   c78dd:      	movq	-0x1748(%rbp), %rsi
   c78e4:      	leaq	-0x16b0(%rbp), %r12
   c78eb:      	movq	%r12, %rdi
   c78ee:      	callq	0x24010 <_ZN7QStringaSERKS_@plt>
   c78f3:      	movq	-0x1748(%rbp), %rdi
   c78fa:      	callq	0x4b960 <.text+0x27130>
   c78ff:      	movq	-0x1780(%rbp), %rdi
   c7906:      	callq	0x4b960 <.text+0x27130>
   c790b:      	movq	-0x1768(%rbp), %rdi
   c7912:      	callq	0x4b960 <.text+0x27130>
   c7917:      	movq	%rbx, %rdi
   c791a:      	callq	0x4b960 <.text+0x27130>
   c791f:      	cmpb	$0x0, 0x60a78e(%rip)    # 0x6d20b4
   c7926:      	jne	0xc958c <.text+0xa4d5c>
