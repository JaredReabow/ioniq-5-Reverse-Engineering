# AppFUMO boot-image pairing exact-static excerpt
# exact ELF size: 5066264
# exact ELF SHA-256: 464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7
# exact ELF Build ID: 863a8730e66a1c5245a1bf458fe2554adee0351a
# canonical rootfs SHA-256: 423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84
# canonical esinit SHA-256: 9f39947ec144322b29c0366bb681f0452ae3696139589bc2f4a2f05bf44afa52
# Raw AppFUMO VAs are shown. Advisory Ghidra addresses require +0x100000.
# This excerpt is execution-free and does not establish successful copy, activation,
# boot acceptance, mark-good, rollback, root, or persistence.

   a24b6:      	movq	%rax, (%rdi)
   a24b9:      	leaq	0x16ec3c(%rip), %rdi    # 0x2110fc
   a24c0:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a24c5:      	leaq	0x90(%rsp), %rbx
   a24cd:      	movl	$0x1, %edx
   a24d2:      	movq	%r12, %rsi
   a24d5:      	movq	%rax, 0x80(%rsp)
   a24dd:      	movq	%rbx, %rdi
   a24e0:      	callq	0xa0d50 <.text+0x7c520>
   a24e5:      	leaq	0x28(%rbx), %rcx
   a24e9:      	movq	%rcx, %rsi
   a24ec:      	movl	(%rsi), %edx
   a24ee:      	addq	$0x4, %rsi
   a24f2:      	leal	-0x1010101(%rdx), %eax
   a24f8:      	notl	%edx
   a24fa:      	andl	%edx, %eax
   a24fc:      	andl	$0x80808080, %eax       # imm = 0x80808080
   a2501:      	je	0xa24ec <.text+0x7dcbc>
   a2503:      	leaq	0x28(%rbx), %rdi
   a2507:      	movl	%eax, %edx
   a2509:      	shrl	$0x10, %edx
   a250c:      	testl	$0x8080, %eax           # imm = 0x8080
   a2511:      	cmovel	%edx, %eax
   a2514:      	leaq	0x2(%rsi), %rdx
   a2518:      	cmoveq	%rdx, %rsi
   a251c:      	addb	%al, %al
   a251e:      	sbbq	$0x3, %rsi
   a2522:      	subq	%rcx, %rsi
   a2525:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a252a:      	leaq	0x70(%rsp), %r14
   a252f:      	movl	$0x1, %edx
   a2534:      	movq	%rax, 0x70(%rsp)
   a2539:      	leaq	0x80(%rsp), %r13
   a2541:      	movq	%r14, %rdi
   a2544:      	movq	%r13, %rsi
   a2547:      	callq	0x22090 <_ZNK7QString7compareERKS_N2Qt15CaseSensitivityE@plt>
   a254c:      	movq	0x70(%rsp), %rdi
   a2551:      	movl	%eax, %r15d
   a2554:      	movl	(%rdi), %edx
   a2556:      	testl	%edx, %edx
   a2558:      	jne	0xa2600 <.text+0x7ddd0>
   a255e:      	movl	$0x8, %edx
   a2563:      	movl	$0x2, %esi
   a2568:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a256d:      	movq	0x80(%rsp), %rdi
   a2575:      	movl	(%rdi), %edx
   a2577:      	testl	%edx, %edx
   a2579:      	jne	0xa25e0 <.text+0x7ddb0>
   a257b:      	movl	$0x8, %edx
   a2580:      	movl	$0x2, %esi
   a2585:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a258a:      	testl	%r15d, %r15d
   a258d:      	jne	0xa2690 <.text+0x7de60>
   a2593:      	movl	0x62fb17(%rip), %eax    # 0x6d20b0
   a2599:      	cmpl	$0x3, %eax
   a259c:      	je	0xa2830 <.text+0x7e000>
   a25a2:      	cmpl	$0x1, %eax
   a25a5:      	je	0xa29d0 <.text+0x7e1a0>
   a25ab:      	subl	$0x2, %eax
   a25ae:      	andl	$-0x3, %eax
   a25b1:      	je	0xa2628 <.text+0x7ddf8>
   a2690:      	leaq	0x16ea91(%rip), %rdi    # 0x211128
   a2697:      	movl	$0xe, %esi
   a269c:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a26a1:      	movl	$0x1, %edx
   a26a6:      	movq	%r12, %rsi
   a26a9:      	movq	%rbx, %rdi
   a26ac:      	movq	%rax, 0x80(%rsp)
   a26b4:      	callq	0xa0d50 <.text+0x7c520>
   a26b9:      	leaq	0x28(%rbx), %rcx
   a26bd:      	movq	%rcx, %rsi
   a26c0:      	movl	(%rsi), %edx
   a26c2:      	addq	$0x4, %rsi
   a26c6:      	leal	-0x1010101(%rdx), %eax
   a26cc:      	notl	%edx
   a26ce:      	andl	%edx, %eax
   a26d0:      	andl	$0x80808080, %eax       # imm = 0x80808080
   a26d5:      	je	0xa26c0 <.text+0x7de90>
   a26d7:      	leaq	0x28(%rbx), %rdi
   a26db:      	movl	%eax, %edx
   a26dd:      	shrl	$0x10, %edx
   a26e0:      	testl	$0x8080, %eax           # imm = 0x8080
   a26e5:      	cmovel	%edx, %eax
   a26e8:      	leaq	0x2(%rsi), %rdx
   a26ec:      	cmoveq	%rdx, %rsi
   a26f0:      	addb	%al, %al
   a26f2:      	sbbq	$0x3, %rsi
   a26f6:      	subq	%rcx, %rsi
   a26f9:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a26fe:      	movl	$0x1, %edx
   a2703:      	movq	%r13, %rsi
   a2706:      	movq	%r14, %rdi
   a2709:      	movq	%rax, 0x70(%rsp)
   a270e:      	callq	0x22090 <_ZNK7QString7compareERKS_N2Qt15CaseSensitivityE@plt>
   a2713:      	movq	0x70(%rsp), %rdi
   a2718:      	movl	%eax, %r15d
   a271b:      	movl	(%rdi), %edx
   a271d:      	testl	%edx, %edx
   a271f:      	jne	0xa2808 <.text+0x7dfd8>
   a2725:      	movl	$0x8, %edx
   a272a:      	movl	$0x2, %esi
   a272f:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a2734:      	movq	0x80(%rsp), %rdi
   a273c:      	movl	(%rdi), %edx
   a273e:      	testl	%edx, %edx
   a2740:      	jne	0xa27e0 <.text+0x7dfb0>
   a2746:      	movl	$0x8, %edx
   a274b:      	movl	$0x2, %esi
   a2750:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a2755:      	testl	%r15d, %r15d
   a2758:      	jne	0xa2880 <.text+0x7e050>
   a275e:      	movl	0x62f94c(%rip), %eax    # 0x6d20b0
   a2764:      	cmpl	$0x3, %eax
   a2767:      	je	0xa2a78 <.text+0x7e248>
   a276d:      	cmpl	$0x1, %eax
   a2770:      	je	0xa2ad0 <.text+0x7e2a0>
   a2776:      	subl	$0x2, %eax
   a2779:      	andl	$-0x3, %eax
   a2880:      	leaq	0x16e8b0(%rip), %rdi    # 0x211137
   a2887:      	movl	$0xe, %esi
   a288c:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a2891:      	movl	$0x1, %edx
   a2896:      	movq	%r12, %rsi
   a2899:      	movq	%rbx, %rdi
   a289c:      	movq	%rax, 0x80(%rsp)
   a28a4:      	callq	0xa0d50 <.text+0x7c520>
   a28a9:      	leaq	0x28(%rbx), %rcx
   a28ad:      	movq	%rcx, %rsi
   a28b0:      	movl	(%rsi), %edx
   a28b2:      	addq	$0x4, %rsi
   a28b6:      	leal	-0x1010101(%rdx), %eax
   a28bc:      	notl	%edx
   a28be:      	andl	%edx, %eax
   a28c0:      	andl	$0x80808080, %eax       # imm = 0x80808080
   a28c5:      	je	0xa28b0 <.text+0x7e080>
   a28c7:      	leaq	0x28(%rbx), %rdi
   a28cb:      	movl	%eax, %edx
   a28cd:      	shrl	$0x10, %edx
   a28d0:      	testl	$0x8080, %eax           # imm = 0x8080
   a28d5:      	cmovel	%edx, %eax
   a28d8:      	leaq	0x2(%rsi), %rdx
   a28dc:      	cmoveq	%rdx, %rsi
   a28e0:      	addb	%al, %al
   a28e2:      	sbbq	$0x3, %rsi
   a28e6:      	subq	%rcx, %rsi
   a28e9:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a28ee:      	movl	$0x1, %edx
   a28f3:      	movq	%r13, %rsi
   a28f6:      	movq	%r14, %rdi
   a28f9:      	movq	%rax, 0x70(%rsp)
   a28fe:      	callq	0x22090 <_ZNK7QString7compareERKS_N2Qt15CaseSensitivityE@plt>
   a2903:      	movq	0x70(%rsp), %rdi
   a2908:      	movl	%eax, %ebx
   a290a:      	movl	(%rdi), %edx
   a290c:      	testl	%edx, %edx
   a290e:      	jne	0xa2a50 <.text+0x7e220>
   a2914:      	movl	$0x8, %edx
   a2919:      	movl	$0x2, %esi
   a291e:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a2923:      	movq	0x80(%rsp), %rdi
   a292b:      	movl	(%rdi), %edx
   a292d:      	testl	%edx, %edx
   a292f:      	jne	0xa2a28 <.text+0x7e1f8>
   a2935:      	movl	$0x8, %edx
   a293a:      	movl	$0x2, %esi
   a293f:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a2944:      	testl	%ebx, %ebx
   a2946:      	jne	0xa25b3 <.text+0x7dd83>
   a294c:      	movl	0x62f75e(%rip), %eax    # 0x6d20b0
   a2952:      	cmpl	$0x3, %eax
   a2955:      	je	0xa2b28 <.text+0x7e2f8>
   a295b:      	cmpl	$0x1, %eax
   a295e:      	je	0xa2b80 <.text+0x7e350>
   a2964:      	subl	$0x2, %eax
   a2967:      	andl	$-0x3, %eax
   a2f52:      	movl	$0xa, %edx
   a2f57:      	leaq	0x168c68(%rip), %rsi    # 0x20bbc6
   a2f5e:      	movq	%rbp, %rdi
   a2f61:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
   a2f66:      	movq	0x28(%rsp), %rdi
   a2f6b:      	movq	%rbp, %rsi
   a2f6e:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
   a2f73:      	movq	0x1f0(%rsp), %rdi
   a2f7b:      	movl	(%rdi), %eax
   a2f7d:      	testl	%eax, %eax
   a2f7f:      	jne	0xa3828 <.text+0x7eff8>
   a2f85:      	movl	$0x8, %edx
   a2f8a:      	movl	$0x2, %esi
   a2f8f:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a2f94:      	movq	0x28(%rsp), %rsi
   a2f99:      	leaq	0x40(%rsp), %rdi
   a2f9e:      	movq	%rdi, 0x20(%rsp)
   a2fa3:      	callq	0x24320 <_ZN4QDirC1ERK7QString@plt>
   a2fa8:      	movq	0x1e0(%rsp), %rdi
   a2fb0:      	movl	(%rdi), %eax
   a2fb2:      	testl	%eax, %eax
   a2fb4:      	jne	0xa3800 <.text+0x7efd0>
   a2fba:      	movl	$0x8, %edx
   a2fbf:      	movl	$0x2, %esi
   a2fc4:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a2fc9:      	leaq	0x170126(%rip), %rdi    # 0x2130f6
   a2fd0:      	movl	$0xf, %esi
   a2fd5:      	callq	0x22db0 <_ZN7QString16fromAscii_helperEPKci@plt>
   a2fda:      	movl	(%rax), %ebx
   a2fdc:      	movq	%rax, 0x1f0(%rsp)
   a2fe4:      	movq	%rax, 0x60(%rsp)
   a2fe9:      	leal	0x1(%rbx), %edx
   a2fec:      	cmpl	$0x1, %edx
   a2fef:      	jbe	0xa2ff8 <.text+0x7e7c8>
   a2ff1:      	lock
   a2ff2:      	addl	$0x1, (%rax)
   a2ff5:      	setne	%dl
   a2ff8:      	leaq	0x1c0(%rsp), %r12
   a3000:      	movl	$0xa, %edx
   a3005:      	leaq	0x173e86(%rip), %rsi    # 0x216e92
   a300c:      	movq	%r12, %rdi
   a300f:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
   a3014:      	leaq	0x60(%rsp), %rbx
   a3019:      	movq	%r12, %rsi
   a301c:      	movq	%rbx, %rdi
   a301f:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
   a3024:      	movq	0x1c0(%rsp), %rdi
   a302c:      	movl	(%rdi), %eax
   a302e:      	testl	%eax, %eax
   a3030:      	jne	0xa37d8 <.text+0x7efa8>
   a3036:      	movl	$0x8, %edx
   a303b:      	movl	$0x2, %esi
   a3040:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a3045:      	leaq	0x50(%rsp), %rax
   a304a:      	movq	%rbx, %rsi
   a304d:      	movq	%rax, %rdi
   a3050:      	movq	%rax, 0x30(%rsp)
   a3055:      	callq	0x24320 <_ZN4QDirC1ERK7QString@plt>
   a305a:      	movq	0x60(%rsp), %rdi
   a305f:      	movl	(%rdi), %eax
   a3061:      	testl	%eax, %eax
   a3063:      	jne	0xa37b0 <.text+0x7ef80>
   a3069:      	movl	$0x8, %edx
   a306e:      	movl	$0x2, %esi
   a3073:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a3078:      	movq	0x1f0(%rsp), %rdi
   a3080:      	movl	(%rdi), %eax
   a3082:      	testl	%eax, %eax
   a3084:      	jne	0xa3788 <.text+0x7ef58>
   a308a:      	movl	$0x8, %edx
   a308f:      	movl	$0x2, %esi
   a3094:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a3099:      	movq	0x6323f0(%rip), %rsi    # 0x6d5490 <_ZN9QListData11shared_nullE+0xc30>
   a30a0:      	testq	%rsi, %rsi
   a30a3:      	je	0xa3b2b <.text+0x7f2fb>
   a30a9:      	leaq	0x70(%rsp), %rax
   a30ae:      	movq	%rax, %rdi
   a30b1:      	movq	%rax, (%rsp)
   a30b5:      	callq	0xa2480 <.text+0x7dc50>
   a30ba:      	leaq	0x6315df(%rip), %rax    # 0x6d46a0 <_ZN10QArrayData11shared_nullE>
   a30f4:      	leaq	0x90(%rsp), %rax
   a30fc:      	movq	%rbx, %rdi
   a30ff:      	leaq	0x18aa3f(%rip), %rsi    # 0x22db45
   a3106:      	movq	%rax, 0x18(%rsp)
   a310b:      	callq	0x223d0 <_ZN7QString15fromUtf8_helperEPKci@plt>
   a3110:      	leaq	0x90(%rsp), %rax
   a3118:      	movq	%rbx, %rsi
   a311b:      	movq	%rax, %rdi
   a311e:      	movq	%rax, 0x18(%rsp)
   a3123:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
   a3128:      	movq	0x1d0(%rsp), %rdi
   a3130:      	movl	(%rdi), %eax
   a3132:      	testl	%eax, %eax
   a3134:      	jne	0xa3760 <.text+0x7ef30>
   a313a:      	movl	$0x8, %edx
   a313f:      	movl	$0x2, %esi
   a3144:      	callq	0x23ee0 <_ZN10QArrayData10deallocateEPS_mm@plt>
   a3149:      	movq	(%rsp), %rsi
   a314d:      	movq	0x20(%rsp), %rdi
   a3152:      	callq	0x24580 <_ZNK4QDir6existsERK7QString@plt>
   a3157:      	testb	%al, %al
   a3159:      	je	0xa316d <.text+0x7e93d>
   a315b:      	movq	0x30(%rsp), %rdi
   a3160:      	callq	0x23aa0 <_ZNK4QDir6existsEv@plt>
   a3165:      	testb	%al, %al
   a3167:      	je	0xa3a9b <.text+0x7f26b>
   a316d:      	movq	0x18(%rsp), %rsi
   a3172:      	movq	0x20(%rsp), %rdi
   a3177:      	callq	0x24580 <_ZNK4QDir6existsERK7QString@plt>
   a317c:      	testb	%al, %al
   a317e:      	je	0xa36f8 <.text+0x7eec8>
   a3350:      	movq	%rbx, %rdi
   a3353:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
   a3358:      	movq	0x632ba1(%rip), %rdi    # 0x6d5f00 <_ZN9QListData11shared_nullE+0x16a0>
   a335f:      	testq	%rdi, %rdi
   a3362:      	je	0xa3b51 <.text+0x7f321>
   a3368:      	xorl	%ecx, %ecx
   a336a:      	movq	%r12, %rdx
   a336d:      	movq	%rbx, %rsi
   a3370:      	callq	0x1413f0 <.text+0x11cbc0>
   a3375:      	movq	0x100(%rsp), %rdi
   a337d:      	movl	%eax, %ebx
   a337f:      	movl	(%rdi), %eax
   a3381:      	testl	%eax, %eax
   a3383:      	jne	0xa3680 <.text+0x7ee50>
   a3389:      	movl	$0x8, %edx
   a338e:      	movl	$0x2, %esi
   a3941:      	movq	%r12, %rdi
   a3944:      	callq	0x55bf0 <.text+0x313c0>
   a3949:      	movq	0x18(%rsp), %rsi
   a394e:      	movq	%r12, %rdi
   a3951:      	callq	0x23f10 <_ZN7QString6appendERKS_@plt>
   a3956:      	movq	0x6325a3(%rip), %rdi    # 0x6d5f00 <_ZN9QListData11shared_nullE+0x16a0>
   a395d:      	testq	%rdi, %rdi
   a3960:      	je	0xa3bae <.text+0x7f37e>
   a3966:      	xorl	%ecx, %ecx
   a3968:      	movq	%r13, %rdx
   a396b:      	movq	%r12, %rsi
   a396e:      	callq	0x1413f0 <.text+0x11cbc0>
   a3973:      	movq	%r12, %rdi
   a3976:      	movl	%eax, %ebx
   a3978:      	callq	0x4b960 <.text+0x27130>
   a397d:      	movq	0x8(%rsp), %rdi
   aaa8f:      	callq	0x22c70 <_ZN5QFileD1Ev@plt>
   aaa94:      	movq	-0x1570(%rbp), %rax
   aaa9b:      	addl	$0x1, -0x1558(%rbp)
   aaaa2:      	movl	-0x1558(%rbp), %ecx
   aaaa8:      	movq	0x10(%rax), %rdx
   aaaac:      	movl	0xc(%rdx), %eax
   aaaaf:      	subl	0x8(%rdx), %eax
   aaab2:      	cmpl	%eax, %ecx
   aaab4:      	jl	0xaa977 <.text+0x86147>
   aaaba:      	movq	-0x1570(%rbp), %rdi
   aaac1:      	callq	0xa2ef0 <.text+0x7e6c0>
   aaac6:      	movl	%eax, %r14d
   aaac9:      	leaq	-0x1510(%rbp), %rax
  141695:      	leaq	0xb0(%rsp), %rbx
  14169d:      	movq	%r12, %rsi
  1416a0:      	movq	%rbx, %rdi
  1416a3:      	callq	0x24100 <_ZN9QIODevice7readAllEv@plt>
  1416a8:      	movq	0xb0(%rsp), %r15
  1416b0:      	movq	%r15, %rdi
  1416b3:      	callq	0x55ac0 <.text+0x31290>
  1416b8:      	movslq	0x4(%r15), %rdx
  1416bc:      	movq	%rbp, %rdi
  1416bf:      	movq	%rax, %rsi
  1416c2:      	callq	0x231c0 <_ZN9QIODevice5writeEPKcx@plt>
  1416c7:      	movq	%rax, %r15
  1416ca:      	movq	%rbx, %rdi
  1416cd:      	callq	0x4b8e0 <.text+0x270b0>
  1416d2:      	testq	%r15, %r15
  1416d5:      	js	0x141980 <.text+0x11d150>
  1416db:      	movq	%rbp, %rdi
  1416de:      	callq	0x246d0 <_ZN11QFileDevice5flushEv@plt>
  1416e3:      	movq	%rbp, %rdi
  1416e6:      	callq	0x24750 <_ZNK11QFileDevice6handleEv@plt>
  1416eb:      	movl	%eax, %edi
  1416ed:      	callq	0x23840 <fsync@plt>
  1416f2:      	leaq	0x130(%rsp), %rbx
  1416fa:      	movq	%r13, %rsi
  1416fd:      	movq	%rbx, %rdi
  141700:      	callq	0x55bf0 <.text+0x313c0>
  141705:      	leaq	0xd0(%rsp), %rax
  14170d:      	movq	%rbx, %rsi
  141710:      	movq	%rax, %rdi
  141713:      	movq	%rax, 0x8(%rsp)
  141718:      	callq	0x55b20 <.text+0x312f0>
  1417ad:      	movq	%rbx, %rdi
  1417b0:      	callq	0x4b960 <.text+0x27130>
  1417b5:      	movq	%r12, %rdi
  1417b8:      	callq	0x22020 <_ZN11QFileDevice5closeEv@plt>
  1417bd:      	movq	%rbp, %rdi
  1417c0:      	callq	0x22020 <_ZN11QFileDevice5closeEv@plt>
  1417c5:      	leaq	0x120(%rsp), %r15
  1417cd:      	movq	%r14, %rsi
  1417d0:      	movq	%r15, %rdi
  1417d3:      	callq	0x22d00 <_ZN5QFileC1ERK7QString@plt>
  1417d8:      	movq	%r15, %rdi
  1417db:      	callq	0x21f40 <_ZNK5QFile4sizeEv@plt>
  1417e0:      	movq	%r13, %rsi
  1417e3:      	movq	%rbx, %rdi
  1417e6:      	movq	%rax, %r14
  1417e9:      	callq	0x22d00 <_ZN5QFileC1ERK7QString@plt>
  1417ee:      	movq	%rbx, %rdi
  1417f1:      	callq	0x21f40 <_ZNK5QFile4sizeEv@plt>
  1417f6:      	movq	%rbx, %rdi
  1417f9:      	movq	%rax, (%rsp)
  1417fd:      	callq	0x22c70 <_ZN5QFileD1Ev@plt>
  141802:      	movq	%r15, %rdi
  141805:      	callq	0x22c70 <_ZN5QFileD1Ev@plt>
  14180a:      	movq	(%rsp), %rax
  14180e:      	cmpq	%rax, %r14
  141811:      	je	0x1418f8 <.text+0x11d0c8>
  141817:      	callq	0x55c60 <.text+0x31430>
  14181c:      	leaq	0xebbf5(%rip), %rdx     # 0x22d418
  141823:      	movq	%rax, %rdi
  141826:      	xorl	%eax, %eax
  141828:      	leaq	0xeb6d4(%rip), %rsi     # 0x22cf03
  14182f:      	callq	0x137430 <.text+0x112c00>
  141834:      	xorl	%r14d, %r14d
  141837:      	jmp	0x1415de <.text+0x11cdae>
  14183c:      	nopl	(%rax)
  141840:      	leaq	0x130(%rsp), %rbx
  141848:      	movq	%r13, %rsi
  14184b:      	leaq	0x70(%rsp), %r13
  141850:      	movq	%rbx, %rdi
  141853:      	callq	0x55bf0 <.text+0x313c0>
  141858:      	movq	%rbx, %rsi
  14185b:      	movq	%r13, %rdi
  14185e:      	callq	0x55b20 <.text+0x312f0>
  141863:      	movq	0x70(%rsp), %rdi
  141868:      	callq	0x55ac0 <.text+0x31290>
  14186d:      	movq	%rax, %r14
  141870:      	callq	0x55c60 <.text+0x31430>
  141875:      	leaq	0xebb9c(%rip), %rdx     # 0x22d418
  14187c:      	movq	%rax, %rdi
  14187f:      	movq	%r14, %rcx
  141882:      	leaq	0xeb60a(%rip), %rsi     # 0x22ce93
  141889:      	xorl	%eax, %eax
  14188b:      	callq	0x137430 <.text+0x112c00>
  141890:      	jmp	0x1415cb <.text+0x11cd9b>
  141895:      	nopl	(%rax)
  141898:      	leaq	0x130(%rsp), %rbx
  1418a0:      	movq	%r13, %rsi
  1418a3:      	leaq	0xa0(%rsp), %r13
  1418ab:      	movq	%rbx, %rdi
  1418ae:      	callq	0x55bf0 <.text+0x313c0>
  1418b3:      	movq	%rbx, %rsi
  1418b6:      	movq	%r13, %rdi
  1418b9:      	callq	0x55b20 <.text+0x312f0>
  1418be:      	movq	0xa0(%rsp), %rdi
  1418c6:      	callq	0x55ac0 <.text+0x31290>
  1418cb:      	movq	%rax, %r14
  1418ce:      	callq	0x55c60 <.text+0x31430>
  1418d3:      	leaq	0xebb3e(%rip), %rdx     # 0x22d418
  1418da:      	movq	%rax, %rdi
  1418dd:      	movq	%r14, %rcx
  1418e0:      	leaq	0xeb5dc(%rip), %rsi     # 0x22cec3
  1418e7:      	xorl	%eax, %eax
  1418e9:      	callq	0x137430 <.text+0x112c00>
  1418ee:      	jmp	0x1415cb <.text+0x11cd9b>
  1418f3:      	nopl	(%rax,%rax)
  1418f8:      	movq	%r12, %rdi
  1418fb:      	callq	0x23530 <_ZNK5QFile11permissionsEv@plt>
  141900:      	movl	%eax, %esi
  141902:      	movq	%rbp, %rdi
  141905:      	callq	0x231f0 <_ZN5QFile14setPermissionsE6QFlagsIN11QFileDevice10PermissionEE@plt>
  14190a:      	movl	$0x1, %r14d
  141910:      	testb	%al, %al
  141912:      	jne	0x1415de <.text+0x11cdae>
  141918:      	leaq	0xf0(%rsp), %r14

# esinit ordered semantic anchors (offset, size, SHA-256); source text is omitted
# 8656	36	d1209adeb46d6db30824147dc4856b227575b69b2738f5982830fe5c4398c108
# 8713	100	13f3a4decc931d243615aafe1cc11c9c8a1f11b2cdd5db2955effd35c02ad16b
# 8979	53	b1a2ab0d5f579758b50ac954b3894e11641359efe878620ee727ae83bf55db87
# 9329	111	dc66f94dda6482b87a83945155213d2394dc782653084008d6dbe2a66c8edb42
# 9842	157	bc872c4cade9a9bf87dde0d987e0a0bf5c9327d07bb68598193787dbecfe244a
# 10125	53	0e4d7095096bed649b78ce40bd6aedbf32ffa8e31ae9dd32965dd58992aaa1be
# 10444	32	6bfff4db4c5e2ddf95a20381e5414989a69c278d91c1b9fd984d0d903664911b
# 10523	32	2531eccf152507da1ed670c5b4d591343d1b65d2b1f3febc39ecb89becb15045
# 10603	41	ba0b0bce953bbdc806ed1b95b4ef322b61e65c65c00f4fc4d9c7c5df2139a401
