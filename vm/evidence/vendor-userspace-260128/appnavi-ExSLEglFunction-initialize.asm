
work/decrypted-eu-260128/extracted-safe/appnavi/Bin/AppNavi:	file format elf64-x86-64

Disassembly of section .text:

00000000031fbd30 <ExSLEglFunction::initialize(void*)>:
 31fbd30: 41 57                        	pushq	%r15
 31fbd32: 41 56                        	pushq	%r14
 31fbd34: 41 55                        	pushq	%r13
 31fbd36: 41 54                        	pushq	%r12
 31fbd38: 55                           	pushq	%rbp
 31fbd39: 53                           	pushq	%rbx
 31fbd3a: 48 81 ec c8 00 00 00         	subq	$0xc8, %rsp
 31fbd41: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
 31fbd4a: 48 89 84 24 b8 00 00 00      	movq	%rax, 0xb8(%rsp)
 31fbd52: 31 c0                        	xorl	%eax, %eax
 31fbd54: 48 83 3d 24 6c c7 04 00      	cmpq	$0x0, 0x4c76c24(%rip)   # 0x7e72980 <g_eglDefaultDisplay>
 31fbd5c: 74 32                        	je	0x31fbd90 <ExSLEglFunction::initialize(void*)+0x60>
 31fbd5e: bb 01 00 00 00               	movl	$0x1, %ebx
 31fbd63: 48 8b 8c 24 b8 00 00 00      	movq	0xb8(%rsp), %rcx
 31fbd6b: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
 31fbd74: 89 d8                        	movl	%ebx, %eax
 31fbd76: 0f 85 36 0a 00 00            	jne	0x31fc7b2 <ExSLEglFunction::initialize(void*)+0xa82>
 31fbd7c: 48 81 c4 c8 00 00 00         	addq	$0xc8, %rsp
 31fbd83: 5b                           	popq	%rbx
 31fbd84: 5d                           	popq	%rbp
 31fbd85: 41 5c                        	popq	%r12
 31fbd87: 41 5d                        	popq	%r13
 31fbd89: 41 5e                        	popq	%r14
 31fbd8b: 41 5f                        	popq	%r15
 31fbd8d: c3                           	retq
 31fbd8e: 66 90                        	nop
 31fbd90: e8 ab 20 25 fe               	callq	0x144de40 <eglGetDisplay@plt>
 31fbd95: 48 85 c0                     	testq	%rax, %rax
 31fbd98: 48 89 05 e1 6b c7 04         	movq	%rax, 0x4c76be1(%rip)   # 0x7e72980 <g_eglDefaultDisplay>
 31fbd9f: 0f 84 ab 07 00 00            	je	0x31fc550 <ExSLEglFunction::initialize(void*)+0x820>
 31fbda5: 31 d2                        	xorl	%edx, %edx
 31fbda7: 31 f6                        	xorl	%esi, %esi
 31fbda9: 48 89 c7                     	movq	%rax, %rdi
 31fbdac: e8 df 0b 25 fe               	callq	0x144c990 <eglInitialize@plt>
 31fbdb1: 85 c0                        	testl	%eax, %eax
 31fbdb3: 0f 84 cf 01 00 00            	je	0x31fbf88 <ExSLEglFunction::initialize(void*)+0x258>
 31fbdb9: bf a0 30 00 00               	movl	$0x30a0, %edi           # imm = 0x30A0
 31fbdbe: e8 2d 0a 25 fe               	callq	0x144c7f0 <eglBindAPI@plt>
 31fbdc3: 85 c0                        	testl	%eax, %eax
 31fbdc5: 0f 84 65 01 00 00            	je	0x31fbf30 <ExSLEglFunction::initialize(void*)+0x200>
 31fbdcb: 48 8b 3d ae 6b c7 04         	movq	0x4c76bae(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fbdd2: 48 8d 4c 24 40               	leaq	0x40(%rsp), %rcx
 31fbdd7: 31 d2                        	xorl	%edx, %edx
 31fbdd9: 31 f6                        	xorl	%esi, %esi
 31fbddb: c7 44 24 40 00 00 00 00      	movl	$0x0, 0x40(%rsp)
 31fbde3: e8 a8 15 25 fe               	callq	0x144d390 <eglGetConfigs@plt>
 31fbde8: 85 c0                        	testl	%eax, %eax
 31fbdea: 8b 6c 24 40                  	movl	0x40(%rsp), %ebp
 31fbdee: 0f 84 ac 01 00 00            	je	0x31fbfa0 <ExSLEglFunction::initialize(void*)+0x270>
 31fbdf4: 85 ed                        	testl	%ebp, %ebp
 31fbdf6: 0f 8e a4 01 00 00            	jle	0x31fbfa0 <ExSLEglFunction::initialize(void*)+0x270>
 31fbdfc: 48 8b 35 1d 1e 4b 04         	movq	0x44b1e1d(%rip), %rsi   # 0x76adc20 <_GLOBAL_OFFSET_TABLE_+0x49b8>
 31fbe03: 48 63 fd                     	movslq	%ebp, %rdi
 31fbe06: 4c 8d 64 24 70               	leaq	0x70(%rsp), %r12
 31fbe0b: 48 c1 e7 03                  	shlq	$0x3, %rdi
 31fbe0f: c1 e5 03                     	shll	$0x3, %ebp
 31fbe12: e8 29 2d 25 fe               	callq	0x144eb40 <_ZnamRKSt9nothrow_t@plt>
 31fbe17: 48 89 04 24                  	movq	%rax, (%rsp)
 31fbe1b: 49 8d 44 24 10               	leaq	0x10(%r12), %rax
 31fbe20: 31 d2                        	xorl	%edx, %edx
 31fbe22: 4c 89 e7                     	movq	%r12, %rdi
 31fbe25: 48 c7 44 24 68 3f 00 00 00   	movq	$0x3f, 0x68(%rsp)
 31fbe2e: 48 89 44 24 70               	movq	%rax, 0x70(%rsp)
 31fbe33: 48 8d 44 24 68               	leaq	0x68(%rsp), %rax
 31fbe38: 48 89 c6                     	movq	%rax, %rsi
 31fbe3b: 48 89 44 24 10               	movq	%rax, 0x10(%rsp)
 31fbe40: e8 2b 14 25 fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 31fbe45: 48 8b 54 24 68               	movq	0x68(%rsp), %rdx
 31fbe4a: 48 be 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rsi # imm = 0x2E2E2F2E2E2F2E2E
 31fbe54: 48 89 44 24 70               	movq	%rax, 0x70(%rsp)
 31fbe59: 41 bb 63 70 00 00            	movl	$0x7063, %r11d          # imm = 0x7063
 31fbe5f: c7 40 38 69 6f 6e 2e         	movl	$0x2e6e6f69, 0x38(%rax) # imm = 0x2E6E6F69
 31fbe66: c6 40 3e 70                  	movb	$0x70, 0x3e(%rax)
 31fbe6a: 66 44 89 58 3c               	movw	%r11w, 0x3c(%rax)
 31fbe6f: 48 8d bc 24 a0 00 00 00      	leaq	0xa0(%rsp), %rdi
 31fbe77: 48 89 94 24 80 00 00 00      	movq	%rdx, 0x80(%rsp)
 31fbe7f: 48 89 30                     	movq	%rsi, (%rax)
 31fbe82: 48 be 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rsi # imm = 0x76614E2F6372732F
 31fbe8c: 48 89 70 08                  	movq	%rsi, 0x8(%rax)
 31fbe90: 48 be 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rsi # imm = 0x6C6F72746E6F4369
 31fbe9a: 48 ba 72 6b 2f 52 65 6e 64 65	movabsq	$0x65646e65522f6b72, %rdx # imm = 0x65646E65522F6B72
 31fbea4: 48 89 70 10                  	movq	%rsi, 0x10(%rax)
 31fbea8: 48 be 2f 46 72 61 6d 65 77 6f	movabsq	$0x6f77656d6172462f, %rsi # imm = 0x6F77656D6172462F
 31fbeb2: 48 89 50 20                  	movq	%rdx, 0x20(%rax)
 31fbeb6: 48 89 70 18                  	movq	%rsi, 0x18(%rax)
 31fbeba: 48 ba 45 67 6c 46 75 6e 63 74	movabsq	$0x74636e75466c6745, %rdx # imm = 0x74636E75466C6745
 31fbec4: 48 be 72 65 72 2f 45 78 53 4c	movabsq	$0x4c5378452f726572, %rsi # imm = 0x4C5378452F726572
 31fbece: 48 89 50 30                  	movq	%rdx, 0x30(%rax)
 31fbed2: 48 89 70 28                  	movq	%rsi, 0x28(%rax)
 31fbed6: 48 8b 54 24 70               	movq	0x70(%rsp), %rdx
 31fbedb: 48 8b 44 24 68               	movq	0x68(%rsp), %rax
 31fbee0: 48 89 44 24 78               	movq	%rax, 0x78(%rsp)
 31fbee5: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 31fbee9: 48 8d 84 24 90 00 00 00      	leaq	0x90(%rsp), %rax
 31fbef1: 4c 8b 74 24 70               	movq	0x70(%rsp), %r14
 31fbef6: 4c 8b 6c 24 78               	movq	0x78(%rsp), %r13
 31fbefb: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
 31fbf00: 48 89 bc 24 90 00 00 00      	movq	%rdi, 0x90(%rsp)
 31fbf08: 4c 89 f0                     	movq	%r14, %rax
 31fbf0b: 4c 01 e8                     	addq	%r13, %rax
 31fbf0e: 0f 95 c3                     	setne	%bl
 31fbf11: 4d 85 f6                     	testq	%r14, %r14
 31fbf14: 0f 94 c0                     	sete	%al
 31fbf17: 20 c3                        	andb	%al, %bl
 31fbf19: 0f 84 bf 00 00 00            	je	0x31fbfde <ExSLEglFunction::initialize(void*)+0x2ae>
 31fbf1f: 48 8d 3d 22 8b b6 02         	leaq	0x2b68b22(%rip), %rdi   # 0x5d64a48 <_IO_stdin_used+0x8>
 31fbf26: e8 f5 1c 25 fe               	callq	0x144dc20 <_ZSt19__throw_logic_errorPKc@plt>
 31fbf2b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 31fbf30: e8 6b fe 24 fe               	callq	0x144bda0 <eglGetError@plt>
 31fbf35: 4c 8d 05 fc 77 e7 02         	leaq	0x2e777fc(%rip), %r8    # 0x6073738 <typeinfo name for ExSLEglSurface+0xb8>
 31fbf3c: 41 89 c1                     	movl	%eax, %r9d
 31fbf3f: b9 5b 00 00 00               	movl	$0x5b, %ecx
 31fbf44: 48 8d 15 fd 7a e7 02         	leaq	0x2e77afd(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fbf4b: 48 8d 35 76 77 e7 02         	leaq	0x2e77776(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fbf52: bf 03 00 00 00               	movl	$0x3, %edi
 31fbf57: 31 c0                        	xorl	%eax, %eax
 31fbf59: 31 db                        	xorl	%ebx, %ebx
 31fbf5b: e8 d0 3d 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fbf60: e9 fe fd ff ff               	jmp	0x31fbd63 <ExSLEglFunction::initialize(void*)+0x33>
 31fbf65: 48 89 c3                     	movq	%rax, %rbx
 31fbf68: 48 8b 7c 24 70               	movq	0x70(%rsp), %rdi
 31fbf6d: 49 83 c4 10                  	addq	$0x10, %r12
 31fbf71: 4c 39 e7                     	cmpq	%r12, %rdi
 31fbf74: 74 05                        	je	0x31fbf7b <ExSLEglFunction::initialize(void*)+0x24b>
 31fbf76: e8 35 ef 24 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 31fbf7b: 48 89 df                     	movq	%rbx, %rdi
 31fbf7e: e8 dd 12 25 fe               	callq	0x144d260 <_Unwind_Resume@plt>
 31fbf83: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 31fbf88: e8 13 fe 24 fe               	callq	0x144bda0 <eglGetError@plt>
 31fbf8d: 4c 8d 05 74 77 e7 02         	leaq	0x2e77774(%rip), %r8    # 0x6073708 <typeinfo name for ExSLEglSurface+0x88>
 31fbf94: 41 89 c1                     	movl	%eax, %r9d
 31fbf97: b9 56 00 00 00               	movl	$0x56, %ecx
 31fbf9c: eb a6                        	jmp	0x31fbf44 <ExSLEglFunction::initialize(void*)+0x214>
 31fbf9e: 66 90                        	nop
 31fbfa0: e8 fb fd 24 fe               	callq	0x144bda0 <eglGetError@plt>
 31fbfa5: 48 83 ec 08                  	subq	$0x8, %rsp
 31fbfa9: 4c 8d 05 28 79 e7 02         	leaq	0x2e77928(%rip), %r8    # 0x60738d8 <typeinfo name for ExSLEglSurface+0x258>
 31fbfb0: 48 8d 15 91 7a e7 02         	leaq	0x2e77a91(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fbfb7: 55                           	pushq	%rbp
 31fbfb8: 48 8d 35 09 77 e7 02         	leaq	0x2e77709(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fbfbf: 41 89 c1                     	movl	%eax, %r9d
 31fbfc2: b9 62 00 00 00               	movl	$0x62, %ecx
 31fbfc7: bf 03 00 00 00               	movl	$0x3, %edi
 31fbfcc: 31 c0                        	xorl	%eax, %eax
 31fbfce: e8 5d 3d 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fbfd3: 31 db                        	xorl	%ebx, %ebx
 31fbfd5: 41 59                        	popq	%r9
 31fbfd7: 41 5a                        	popq	%r10
 31fbfd9: e9 85 fd ff ff               	jmp	0x31fbd63 <ExSLEglFunction::initialize(void*)+0x33>
 31fbfde: 49 83 fd 0f                  	cmpq	$0xf, %r13
 31fbfe2: 4c 89 6c 24 68               	movq	%r13, 0x68(%rsp)
 31fbfe7: 0f 87 7c 05 00 00            	ja	0x31fc569 <ExSLEglFunction::initialize(void*)+0x839>
 31fbfed: 49 83 fd 01                  	cmpq	$0x1, %r13
 31fbff1: 0f 85 9b 05 00 00            	jne	0x31fc592 <ExSLEglFunction::initialize(void*)+0x862>
 31fbff7: 41 0f b6 06                  	movzbl	(%r14), %eax
 31fbffb: 88 84 24 a0 00 00 00         	movb	%al, 0xa0(%rsp)
 31fc002: b8 01 00 00 00               	movl	$0x1, %eax
 31fc007: 4c 8b 7c 24 08               	movq	0x8(%rsp), %r15
 31fc00c: 48 8b 0c 24                  	movq	(%rsp), %rcx
 31fc010: 41 b9 01 00 00 00            	movl	$0x1, %r9d
 31fc016: 48 89 84 24 98 00 00 00      	movq	%rax, 0x98(%rsp)
 31fc01e: 41 89 e8                     	movl	%ebp, %r8d
 31fc021: c6 04 07 00                  	movb	$0x0, (%rdi,%rax)
 31fc025: ba 66 00 00 00               	movl	$0x66, %edx
 31fc02a: bf 10 20 00 00               	movl	$0x2010, %edi           # imm = 0x2010
 31fc02f: 4c 89 fe                     	movq	%r15, %rsi
 31fc032: e8 59 cd 60 ff               	callq	0x2808d90 <ExSLMemoryNew>
 31fc037: 48 8b bc 24 90 00 00 00      	movq	0x90(%rsp), %rdi
 31fc03f: 4c 89 f8                     	movq	%r15, %rax
 31fc042: 48 83 c0 10                  	addq	$0x10, %rax
 31fc046: 48 39 c7                     	cmpq	%rax, %rdi
 31fc049: 74 05                        	je	0x31fc050 <ExSLEglFunction::initialize(void*)+0x320>
 31fc04b: e8 60 ee 24 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 31fc050: 48 8b 7c 24 70               	movq	0x70(%rsp), %rdi
 31fc055: 49 83 c4 10                  	addq	$0x10, %r12
 31fc059: 4c 39 e7                     	cmpq	%r12, %rdi
 31fc05c: 74 05                        	je	0x31fc063 <ExSLEglFunction::initialize(void*)+0x333>
 31fc05e: e8 4d ee 24 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 31fc063: 48 83 3c 24 00               	cmpq	$0x0, (%rsp)
 31fc068: 0f 84 e6 06 00 00            	je	0x31fc754 <ExSLEglFunction::initialize(void*)+0xa24>
 31fc06e: 48 8d 6c 24 64               	leaq	0x64(%rsp), %rbp
 31fc073: 8b 4c 24 40                  	movl	0x40(%rsp), %ecx
 31fc077: 48 8b 14 24                  	movq	(%rsp), %rdx
 31fc07b: 48 8b 3d fe 68 c7 04         	movq	0x4c768fe(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc082: 48 8d 35 77 4b 4b 04         	leaq	0x44b4b77(%rip), %rsi   # 0x76b0c00 <g_eglDefaultConfigAttribs>
 31fc089: c7 44 24 44 00 00 00 00      	movl	$0x0, 0x44(%rsp)
 31fc091: 49 89 e8                     	movq	%rbp, %r8
 31fc094: c7 44 24 48 00 00 00 00      	movl	$0x0, 0x48(%rsp)
 31fc09c: c7 44 24 4c 00 00 00 00      	movl	$0x0, 0x4c(%rsp)
 31fc0a4: c7 44 24 50 00 00 00 00      	movl	$0x0, 0x50(%rsp)
 31fc0ac: c7 44 24 54 00 00 00 00      	movl	$0x0, 0x54(%rsp)
 31fc0b4: c7 44 24 58 00 00 00 00      	movl	$0x0, 0x58(%rsp)
 31fc0bc: c7 44 24 5c 00 00 00 00      	movl	$0x0, 0x5c(%rsp)
 31fc0c4: c7 44 24 60 00 00 00 00      	movl	$0x0, 0x60(%rsp)
 31fc0cc: c7 44 24 64 00 00 00 00      	movl	$0x0, 0x64(%rsp)
 31fc0d4: e8 57 11 25 fe               	callq	0x144d230 <eglChooseConfig@plt>
 31fc0d9: 85 c0                        	testl	%eax, %eax
 31fc0db: 44 8b 64 24 64               	movl	0x64(%rsp), %r12d
 31fc0e0: 0f 84 e2 02 00 00            	je	0x31fc3c8 <ExSLEglFunction::initialize(void*)+0x698>
 31fc0e6: 45 85 e4                     	testl	%r12d, %r12d
 31fc0e9: 0f 8e d9 02 00 00            	jle	0x31fc3c8 <ExSLEglFunction::initialize(void*)+0x698>
 31fc0ef: 48 83 ec 08                  	subq	$0x8, %rsp
 31fc0f3: 4c 8d 05 1e 78 e7 02         	leaq	0x2e7781e(%rip), %r8    # 0x6073918 <typeinfo name for ExSLEglSurface+0x298>
 31fc0fa: 48 8d 35 c7 75 e7 02         	leaq	0x2e775c7(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fc101: 41 54                        	pushq	%r12
 31fc103: 44 8b 4c 24 50               	movl	0x50(%rsp), %r9d
 31fc108: 48 8d 15 39 79 e7 02         	leaq	0x2e77939(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fc10f: bf 02 00 00 00               	movl	$0x2, %edi
 31fc114: 31 c0                        	xorl	%eax, %eax
 31fc116: b9 8d 00 00 00               	movl	$0x8d, %ecx
 31fc11b: e8 10 3c 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fc120: 5e                           	popq	%rsi
 31fc121: 5f                           	popq	%rdi
 31fc122: 44 8b 44 24 64               	movl	0x64(%rsp), %r8d
 31fc127: 45 85 c0                     	testl	%r8d, %r8d
 31fc12a: 0f 8e 7a 06 00 00            	jle	0x31fc7aa <ExSLEglFunction::initialize(void*)+0xa7a>
 31fc130: 48 8d 44 24 60               	leaq	0x60(%rsp), %rax
 31fc135: 88 5c 24 18                  	movb	%bl, 0x18(%rsp)
 31fc139: 48 8b 2c 24                  	movq	(%rsp), %rbp
 31fc13d: 45 31 e4                     	xorl	%r12d, %r12d
 31fc140: 4c 8d 7c 24 54               	leaq	0x54(%rsp), %r15
 31fc145: 4c 8d 74 24 58               	leaq	0x58(%rsp), %r14
 31fc14a: 4c 8d 6c 24 5c               	leaq	0x5c(%rsp), %r13
 31fc14f: 48 89 c3                     	movq	%rax, %rbx
 31fc152: eb 17                        	jmp	0x31fc16b <ExSLEglFunction::initialize(void*)+0x43b>
 31fc154: 0f 1f 40 00                  	nopl	(%rax)
 31fc158: 41 83 c4 01                  	addl	$0x1, %r12d
 31fc15c: 48 83 c5 08                  	addq	$0x8, %rbp
 31fc160: 44 39 64 24 64               	cmpl	%r12d, 0x64(%rsp)
 31fc165: 0f 8e d5 03 00 00            	jle	0x31fc540 <ExSLEglFunction::initialize(void*)+0x810>
 31fc16b: 48 8b 75 00                  	movq	(%rbp), %rsi
 31fc16f: 48 8b 3d 0a 68 c7 04         	movq	0x4c7680a(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc176: 48 89 d9                     	movq	%rbx, %rcx
 31fc179: ba 20 30 00 00               	movl	$0x3020, %edx           # imm = 0x3020
 31fc17e: e8 cd f9 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc183: 48 8b 75 00                  	movq	(%rbp), %rsi
 31fc187: 48 8b 3d f2 67 c7 04         	movq	0x4c767f2(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc18e: 4c 89 f9                     	movq	%r15, %rcx
 31fc191: ba 25 30 00 00               	movl	$0x3025, %edx           # imm = 0x3025
 31fc196: e8 b5 f9 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc19b: 48 8b 75 00                  	movq	(%rbp), %rsi
 31fc19f: 48 8b 3d da 67 c7 04         	movq	0x4c767da(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc1a6: 4c 89 f1                     	movq	%r14, %rcx
 31fc1a9: ba 26 30 00 00               	movl	$0x3026, %edx           # imm = 0x3026
 31fc1ae: e8 9d f9 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc1b3: 48 8b 75 00                  	movq	(%rbp), %rsi
 31fc1b7: 48 8b 3d c2 67 c7 04         	movq	0x4c767c2(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc1be: 4c 89 e9                     	movq	%r13, %rcx
 31fc1c1: ba 31 30 00 00               	movl	$0x3031, %edx           # imm = 0x3031
 31fc1c6: e8 85 f9 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc1cb: 83 7c 24 60 20               	cmpl	$0x20, 0x60(%rsp)
 31fc1d0: 75 86                        	jne	0x31fc158 <ExSLEglFunction::initialize(void*)+0x428>
 31fc1d2: 83 7c 24 54 18               	cmpl	$0x18, 0x54(%rsp)
 31fc1d7: 0f 85 7b ff ff ff            	jne	0x31fc158 <ExSLEglFunction::initialize(void*)+0x428>
 31fc1dd: 83 7c 24 58 08               	cmpl	$0x8, 0x58(%rsp)
 31fc1e2: 0f 85 70 ff ff ff            	jne	0x31fc158 <ExSLEglFunction::initialize(void*)+0x428>
 31fc1e8: 83 7c 24 5c 02               	cmpl	$0x2, 0x5c(%rsp)
 31fc1ed: 0f 85 65 ff ff ff            	jne	0x31fc158 <ExSLEglFunction::initialize(void*)+0x428>
 31fc1f3: 48 8b 45 00                  	movq	(%rbp), %rax
 31fc1f7: 0f b6 5c 24 18               	movzbl	0x18(%rsp), %ebx
 31fc1fc: 48 89 05 75 67 c7 04         	movq	%rax, 0x4c76775(%rip)   # 0x7e72978 <g_eglDefaultConfig>
 31fc203: 0f 1f 44 00 00               	nopl	(%rax,%rax)
 31fc208: 4c 8b 74 24 08               	movq	0x8(%rsp), %r14
 31fc20d: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 31fc212: 31 d2                        	xorl	%edx, %edx
 31fc214: 48 c7 44 24 68 3f 00 00 00   	movq	$0x3f, 0x68(%rsp)
 31fc21d: bd 63 70 00 00               	movl	$0x7063, %ebp           # imm = 0x7063
 31fc222: 4c 89 f0                     	movq	%r14, %rax
 31fc225: 4c 89 f7                     	movq	%r14, %rdi
 31fc228: 48 83 c0 10                  	addq	$0x10, %rax
 31fc22c: 48 89 84 24 90 00 00 00      	movq	%rax, 0x90(%rsp)
 31fc234: e8 37 10 25 fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 31fc239: 48 8b 54 24 68               	movq	0x68(%rsp), %rdx
 31fc23e: 48 be 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rsi # imm = 0x2E2E2F2E2E2F2E2E
 31fc248: 48 89 84 24 90 00 00 00      	movq	%rax, 0x90(%rsp)
 31fc250: 4c 8b 3c 24                  	movq	(%rsp), %r15
 31fc254: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 31fc25a: bf 10 20 00 00               	movl	$0x2010, %edi           # imm = 0x2010
 31fc25f: 48 89 94 24 a0 00 00 00      	movq	%rdx, 0xa0(%rsp)
 31fc267: 48 89 30                     	movq	%rsi, (%rax)
 31fc26a: 48 ba 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rdx # imm = 0x76614E2F6372732F
 31fc274: 48 be 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rsi # imm = 0x6C6F72746E6F4369
 31fc27e: 48 89 50 08                  	movq	%rdx, 0x8(%rax)
 31fc282: 48 ba 2f 46 72 61 6d 65 77 6f	movabsq	$0x6f77656d6172462f, %rdx # imm = 0x6F77656D6172462F
 31fc28c: 48 89 70 10                  	movq	%rsi, 0x10(%rax)
 31fc290: 48 be 72 6b 2f 52 65 6e 64 65	movabsq	$0x65646e65522f6b72, %rsi # imm = 0x65646E65522F6B72
 31fc29a: 48 89 50 18                  	movq	%rdx, 0x18(%rax)
 31fc29e: 48 89 70 20                  	movq	%rsi, 0x20(%rax)
 31fc2a2: 48 ba 72 65 72 2f 45 78 53 4c	movabsq	$0x4c5378452f726572, %rdx # imm = 0x4C5378452F726572
 31fc2ac: 48 be 45 67 6c 46 75 6e 63 74	movabsq	$0x74636e75466c6745, %rsi # imm = 0x74636E75466C6745
 31fc2b6: 48 89 70 30                  	movq	%rsi, 0x30(%rax)
 31fc2ba: 48 89 50 28                  	movq	%rdx, 0x28(%rax)
 31fc2be: 4c 89 f9                     	movq	%r15, %rcx
 31fc2c1: c7 40 38 69 6f 6e 2e         	movl	$0x2e6e6f69, 0x38(%rax) # imm = 0x2E6E6F69
 31fc2c8: 66 89 68 3c                  	movw	%bp, 0x3c(%rax)
 31fc2cc: 4c 89 f6                     	movq	%r14, %rsi
 31fc2cf: c6 40 3e 70                  	movb	$0x70, 0x3e(%rax)
 31fc2d3: 48 8b 44 24 68               	movq	0x68(%rsp), %rax
 31fc2d8: 48 8b 94 24 90 00 00 00      	movq	0x90(%rsp), %rdx
 31fc2e0: 48 89 84 24 98 00 00 00      	movq	%rax, 0x98(%rsp)
 31fc2e8: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 31fc2ec: ba 9b 00 00 00               	movl	$0x9b, %edx
 31fc2f1: e8 1a db 60 ff               	callq	0x2809e10 <ExSLMemoryDel>
 31fc2f6: 4c 89 ff                     	movq	%r15, %rdi
 31fc2f9: e8 a2 0c 25 fe               	callq	0x144cfa0 <_ZdaPv@plt>
 31fc2fe: 48 8b bc 24 90 00 00 00      	movq	0x90(%rsp), %rdi
 31fc306: 4c 89 f0                     	movq	%r14, %rax
 31fc309: 48 83 c0 10                  	addq	$0x10, %rax
 31fc30d: 48 39 c7                     	cmpq	%rax, %rdi
 31fc310: 74 05                        	je	0x31fc317 <ExSLEglFunction::initialize(void*)+0x5e7>
 31fc312: e8 99 eb 24 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 31fc317: 48 83 3d 59 66 c7 04 00      	cmpq	$0x0, 0x4c76659(%rip)   # 0x7e72978 <g_eglDefaultConfig>
 31fc31f: 0f 84 5a 04 00 00            	je	0x31fc77f <ExSLEglFunction::initialize(void*)+0xa4f>
 31fc325: 8b 44 24 5c                  	movl	0x5c(%rsp), %eax
 31fc329: 4c 8d 05 08 75 e7 02         	leaq	0x2e77508(%rip), %r8    # 0x6073838 <typeinfo name for ExSLEglSurface+0x1b8>
 31fc330: 48 8d 15 11 77 e7 02         	leaq	0x2e77711(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fc337: 48 8d 35 8a 73 e7 02         	leaq	0x2e7738a(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fc33e: 45 89 e1                     	movl	%r12d, %r9d
 31fc341: b9 a1 00 00 00               	movl	$0xa1, %ecx
 31fc346: bf 02 00 00 00               	movl	$0x2, %edi
 31fc34b: 50                           	pushq	%rax
 31fc34c: 8b 44 24 60                  	movl	0x60(%rsp), %eax
 31fc350: 50                           	pushq	%rax
 31fc351: 8b 44 24 64                  	movl	0x64(%rsp), %eax
 31fc355: 50                           	pushq	%rax
 31fc356: 8b 44 24 78                  	movl	0x78(%rsp), %eax
 31fc35a: 50                           	pushq	%rax
 31fc35b: 31 c0                        	xorl	%eax, %eax
 31fc35d: e8 ce 39 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fc362: 48 8b 35 0f 66 c7 04         	movq	0x4c7660f(%rip), %rsi   # 0x7e72978 <g_eglDefaultConfig>
 31fc369: 48 8b 3d 10 66 c7 04         	movq	0x4c76610(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc370: 48 8d 0d d9 48 4b 04         	leaq	0x44b48d9(%rip), %rcx   # 0x76b0c50 <g_eglDefaultContextAttribs>
 31fc377: 48 83 c4 20                  	addq	$0x20, %rsp
 31fc37b: 31 d2                        	xorl	%edx, %edx
 31fc37d: e8 8e 18 25 fe               	callq	0x144dc10 <eglCreateContext@plt>
 31fc382: 48 85 c0                     	testq	%rax, %rax
 31fc385: 48 89 05 e4 65 c7 04         	movq	%rax, 0x4c765e4(%rip)   # 0x7e72970 <g_eglDefaultContext>
 31fc38c: 0f 85 cc f9 ff ff            	jne	0x31fbd5e <ExSLEglFunction::initialize(void*)+0x2e>
 31fc392: e8 09 fa 24 fe               	callq	0x144bda0 <eglGetError@plt>
 31fc397: 4c 8d 05 02 75 e7 02         	leaq	0x2e77502(%rip), %r8    # 0x60738a0 <typeinfo name for ExSLEglSurface+0x220>
 31fc39e: 48 8d 15 a3 76 e7 02         	leaq	0x2e776a3(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fc3a5: 48 8d 35 1c 73 e7 02         	leaq	0x2e7731c(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fc3ac: 41 89 c1                     	movl	%eax, %r9d
 31fc3af: b9 a6 00 00 00               	movl	$0xa6, %ecx
 31fc3b4: bf 03 00 00 00               	movl	$0x3, %edi
 31fc3b9: 31 c0                        	xorl	%eax, %eax
 31fc3bb: e8 70 39 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fc3c0: e9 9e f9 ff ff               	jmp	0x31fbd63 <ExSLEglFunction::initialize(void*)+0x33>
 31fc3c5: 0f 1f 00                     	nopl	(%rax)
 31fc3c8: e8 d3 f9 24 fe               	callq	0x144bda0 <eglGetError@plt>
 31fc3cd: 48 83 ec 08                  	subq	$0x8, %rsp
 31fc3d1: 4c 8d 05 70 75 e7 02         	leaq	0x2e77570(%rip), %r8    # 0x6073948 <typeinfo name for ExSLEglSurface+0x2c8>
 31fc3d8: 48 8d 15 69 76 e7 02         	leaq	0x2e77669(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fc3df: 41 54                        	pushq	%r12
 31fc3e1: 48 8d 35 e0 72 e7 02         	leaq	0x2e772e0(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fc3e8: 41 89 c1                     	movl	%eax, %r9d
 31fc3eb: b9 78 00 00 00               	movl	$0x78, %ecx
 31fc3f0: 31 c0                        	xorl	%eax, %eax
 31fc3f2: bf 03 00 00 00               	movl	$0x3, %edi
 31fc3f7: e8 34 39 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fc3fc: 5a                           	popq	%rdx
 31fc3fd: 59                           	popq	%rcx
 31fc3fe: 8b 4c 24 40                  	movl	0x40(%rsp), %ecx
 31fc402: 48 8b 14 24                  	movq	(%rsp), %rdx
 31fc406: 31 f6                        	xorl	%esi, %esi
 31fc408: 48 8b 3d 71 65 c7 04         	movq	0x4c76571(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc40f: 49 89 e8                     	movq	%rbp, %r8
 31fc412: e8 19 0e 25 fe               	callq	0x144d230 <eglChooseConfig@plt>
 31fc417: 83 f8 01                     	cmpl	$0x1, %eax
 31fc41a: 0f 84 8f 01 00 00            	je	0x31fc5af <ExSLEglFunction::initialize(void*)+0x87f>
 31fc420: 4c 8b 7c 24 08               	movq	0x8(%rsp), %r15
 31fc425: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 31fc42a: 31 d2                        	xorl	%edx, %edx
 31fc42c: 48 c7 44 24 68 3f 00 00 00   	movq	$0x3f, 0x68(%rsp)
 31fc435: 41 bc 63 70 00 00            	movl	$0x7063, %r12d          # imm = 0x7063
 31fc43b: 4c 89 f8                     	movq	%r15, %rax
 31fc43e: 4c 89 ff                     	movq	%r15, %rdi
 31fc441: 48 83 c0 10                  	addq	$0x10, %rax
 31fc445: 48 89 84 24 90 00 00 00      	movq	%rax, 0x90(%rsp)
 31fc44d: e8 1e 0e 25 fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 31fc452: 48 8b 54 24 68               	movq	0x68(%rsp), %rdx
 31fc457: 48 be 2e 2e 2f 2e 2e 2f 2e 2e	movabsq	$0x2e2e2f2e2e2f2e2e, %rsi # imm = 0x2E2E2F2E2E2F2E2E
 31fc461: 48 89 84 24 90 00 00 00      	movq	%rax, 0x90(%rsp)
 31fc469: 4c 8b 34 24                  	movq	(%rsp), %r14
 31fc46d: 41 b8 01 00 00 00            	movl	$0x1, %r8d
 31fc473: bf 10 20 00 00               	movl	$0x2010, %edi           # imm = 0x2010
 31fc478: 48 89 94 24 a0 00 00 00      	movq	%rdx, 0xa0(%rsp)
 31fc480: 48 89 30                     	movq	%rsi, (%rax)
 31fc483: 48 ba 69 43 6f 6e 74 72 6f 6c	movabsq	$0x6c6f72746e6f4369, %rdx # imm = 0x6C6F72746E6F4369
 31fc48d: 48 be 2f 73 72 63 2f 4e 61 76	movabsq	$0x76614e2f6372732f, %rsi # imm = 0x76614E2F6372732F
 31fc497: 48 89 50 10                  	movq	%rdx, 0x10(%rax)
 31fc49b: 48 ba 72 6b 2f 52 65 6e 64 65	movabsq	$0x65646e65522f6b72, %rdx # imm = 0x65646E65522F6B72
 31fc4a5: 48 89 70 08                  	movq	%rsi, 0x8(%rax)
 31fc4a9: 48 be 2f 46 72 61 6d 65 77 6f	movabsq	$0x6f77656d6172462f, %rsi # imm = 0x6F77656D6172462F
 31fc4b3: 48 89 50 20                  	movq	%rdx, 0x20(%rax)
 31fc4b7: 48 89 70 18                  	movq	%rsi, 0x18(%rax)
 31fc4bb: 48 ba 45 67 6c 46 75 6e 63 74	movabsq	$0x74636e75466c6745, %rdx # imm = 0x74636E75466C6745
 31fc4c5: 48 be 72 65 72 2f 45 78 53 4c	movabsq	$0x4c5378452f726572, %rsi # imm = 0x4C5378452F726572
 31fc4cf: 48 89 70 28                  	movq	%rsi, 0x28(%rax)
 31fc4d3: 48 89 50 30                  	movq	%rdx, 0x30(%rax)
 31fc4d7: 4c 89 f1                     	movq	%r14, %rcx
 31fc4da: c7 40 38 69 6f 6e 2e         	movl	$0x2e6e6f69, 0x38(%rax) # imm = 0x2E6E6F69
 31fc4e1: 66 44 89 60 3c               	movw	%r12w, 0x3c(%rax)
 31fc4e6: 4c 89 fe                     	movq	%r15, %rsi
 31fc4e9: c6 40 3e 70                  	movb	$0x70, 0x3e(%rax)
 31fc4ed: 48 8b 44 24 68               	movq	0x68(%rsp), %rax
 31fc4f2: 48 8b 94 24 90 00 00 00      	movq	0x90(%rsp), %rdx
 31fc4fa: 48 89 84 24 98 00 00 00      	movq	%rax, 0x98(%rsp)
 31fc502: c6 04 02 00                  	movb	$0x0, (%rdx,%rax)
 31fc506: ba 89 00 00 00               	movl	$0x89, %edx
 31fc50b: e8 00 d9 60 ff               	callq	0x2809e10 <ExSLMemoryDel>
 31fc510: 4c 89 f7                     	movq	%r14, %rdi
 31fc513: e8 88 0a 25 fe               	callq	0x144cfa0 <_ZdaPv@plt>
 31fc518: 48 8b bc 24 90 00 00 00      	movq	0x90(%rsp), %rdi
 31fc520: 4c 89 f8                     	movq	%r15, %rax
 31fc523: 48 83 c0 10                  	addq	$0x10, %rax
 31fc527: 48 39 c7                     	cmpq	%rax, %rdi
 31fc52a: 0f 84 33 f8 ff ff            	je	0x31fbd63 <ExSLEglFunction::initialize(void*)+0x33>
 31fc530: e8 7b e9 24 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 31fc535: e9 29 f8 ff ff               	jmp	0x31fbd63 <ExSLEglFunction::initialize(void*)+0x33>
 31fc53a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 31fc540: 0f b6 5c 24 18               	movzbl	0x18(%rsp), %ebx
 31fc545: e9 be fc ff ff               	jmp	0x31fc208 <ExSLEglFunction::initialize(void*)+0x4d8>
 31fc54a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
 31fc550: e8 4b f8 24 fe               	callq	0x144bda0 <eglGetError@plt>
 31fc555: 4c 8d 05 3c 71 e7 02         	leaq	0x2e7713c(%rip), %r8    # 0x6073698 <typeinfo name for ExSLEglSurface+0x18>
 31fc55c: 41 89 c1                     	movl	%eax, %r9d
 31fc55f: b9 51 00 00 00               	movl	$0x51, %ecx
 31fc564: e9 db f9 ff ff               	jmp	0x31fbf44 <ExSLEglFunction::initialize(void*)+0x214>
 31fc569: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
 31fc56e: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
 31fc573: 31 d2                        	xorl	%edx, %edx
 31fc575: e8 f6 0c 25 fe               	callq	0x144d270 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm@plt>
 31fc57a: 48 8b 54 24 68               	movq	0x68(%rsp), %rdx
 31fc57f: 48 89 84 24 90 00 00 00      	movq	%rax, 0x90(%rsp)
 31fc587: 48 89 c7                     	movq	%rax, %rdi
 31fc58a: 48 89 94 24 a0 00 00 00      	movq	%rdx, 0xa0(%rsp)
 31fc592: 4c 89 ea                     	movq	%r13, %rdx
 31fc595: 4c 89 f6                     	movq	%r14, %rsi
 31fc598: e8 f3 16 25 fe               	callq	0x144dc90 <memcpy@plt>
 31fc59d: 48 8b 44 24 68               	movq	0x68(%rsp), %rax
 31fc5a2: 48 8b bc 24 90 00 00 00      	movq	0x90(%rsp), %rdi
 31fc5aa: e9 58 fa ff ff               	jmp	0x31fc007 <ExSLEglFunction::initialize(void*)+0x2d7>
 31fc5af: 8b 44 24 64                  	movl	0x64(%rsp), %eax
 31fc5b3: 85 c0                        	testl	%eax, %eax
 31fc5b5: 0f 8e 65 fe ff ff            	jle	0x31fc420 <ExSLEglFunction::initialize(void*)+0x6f0>
 31fc5bb: 48 8d 44 24 44               	leaq	0x44(%rsp), %rax
 31fc5c0: 48 8b 2c 24                  	movq	(%rsp), %rbp
 31fc5c4: 4c 8d 7c 24 54               	leaq	0x54(%rsp), %r15
 31fc5c9: 4c 8d 74 24 58               	leaq	0x58(%rsp), %r14
 31fc5ce: 4c 8d 6c 24 5c               	leaq	0x5c(%rsp), %r13
 31fc5d3: 88 5c 24 3f                  	movb	%bl, 0x3f(%rsp)
 31fc5d7: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
 31fc5dc: 48 8d 44 24 48               	leaq	0x48(%rsp), %rax
 31fc5e1: 45 31 e4                     	xorl	%r12d, %r12d
 31fc5e4: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
 31fc5e9: 48 8d 44 24 4c               	leaq	0x4c(%rsp), %rax
 31fc5ee: 48 89 44 24 28               	movq	%rax, 0x28(%rsp)
 31fc5f3: 48 8d 44 24 50               	leaq	0x50(%rsp), %rax
 31fc5f8: 48 89 44 24 30               	movq	%rax, 0x30(%rsp)
 31fc5fd: 48 8d 44 24 60               	leaq	0x60(%rsp), %rax
 31fc602: 48 89 c3                     	movq	%rax, %rbx
 31fc605: 0f 1f 00                     	nopl	(%rax)
 31fc608: 48 8b 4c 24 18               	movq	0x18(%rsp), %rcx
 31fc60d: 48 8b 75 00                  	movq	(%rbp), %rsi
 31fc611: ba 24 30 00 00               	movl	$0x3024, %edx           # imm = 0x3024
 31fc616: 48 8b 3d 63 63 c7 04         	movq	0x4c76363(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc61d: 48 83 c5 08                  	addq	$0x8, %rbp
 31fc621: e8 2a f5 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc626: 48 8b 4c 24 20               	movq	0x20(%rsp), %rcx
 31fc62b: 48 8b 75 f8                  	movq	-0x8(%rbp), %rsi
 31fc62f: ba 23 30 00 00               	movl	$0x3023, %edx           # imm = 0x3023
 31fc634: 48 8b 3d 45 63 c7 04         	movq	0x4c76345(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc63b: e8 10 f5 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc640: 48 8b 4c 24 28               	movq	0x28(%rsp), %rcx
 31fc645: 48 8b 75 f8                  	movq	-0x8(%rbp), %rsi
 31fc649: ba 22 30 00 00               	movl	$0x3022, %edx           # imm = 0x3022
 31fc64e: 48 8b 3d 2b 63 c7 04         	movq	0x4c7632b(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc655: e8 f6 f4 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc65a: 48 8b 4c 24 30               	movq	0x30(%rsp), %rcx
 31fc65f: 48 8b 75 f8                  	movq	-0x8(%rbp), %rsi
 31fc663: ba 21 30 00 00               	movl	$0x3021, %edx           # imm = 0x3021
 31fc668: 48 8b 3d 11 63 c7 04         	movq	0x4c76311(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc66f: e8 dc f4 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc674: 48 8b 75 f8                  	movq	-0x8(%rbp), %rsi
 31fc678: 48 8b 3d 01 63 c7 04         	movq	0x4c76301(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc67f: 4c 89 f9                     	movq	%r15, %rcx
 31fc682: ba 25 30 00 00               	movl	$0x3025, %edx           # imm = 0x3025
 31fc687: e8 c4 f4 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc68c: 48 8b 75 f8                  	movq	-0x8(%rbp), %rsi
 31fc690: 48 8b 3d e9 62 c7 04         	movq	0x4c762e9(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc697: 4c 89 f1                     	movq	%r14, %rcx
 31fc69a: ba 26 30 00 00               	movl	$0x3026, %edx           # imm = 0x3026
 31fc69f: e8 ac f4 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc6a4: 48 8b 75 f8                  	movq	-0x8(%rbp), %rsi
 31fc6a8: 48 8b 3d d1 62 c7 04         	movq	0x4c762d1(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc6af: 4c 89 e9                     	movq	%r13, %rcx
 31fc6b2: ba 31 30 00 00               	movl	$0x3031, %edx           # imm = 0x3031
 31fc6b7: e8 94 f4 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc6bc: 48 8b 75 f8                  	movq	-0x8(%rbp), %rsi
 31fc6c0: 48 8b 3d b9 62 c7 04         	movq	0x4c762b9(%rip), %rdi   # 0x7e72980 <g_eglDefaultDisplay>
 31fc6c7: 48 89 d9                     	movq	%rbx, %rcx
 31fc6ca: ba 20 30 00 00               	movl	$0x3020, %edx           # imm = 0x3020
 31fc6cf: e8 7c f4 24 fe               	callq	0x144bb50 <eglGetConfigAttrib@plt>
 31fc6d4: 48 83 ec 08                  	subq	$0x8, %rsp
 31fc6d8: 4c 8d 05 b9 70 e7 02         	leaq	0x2e770b9(%rip), %r8    # 0x6073798 <typeinfo name for ExSLEglSurface+0x118>
 31fc6df: 48 8d 15 62 73 e7 02         	leaq	0x2e77362(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fc6e6: 8b 44 24 68                  	movl	0x68(%rsp), %eax
 31fc6ea: 48 8d 35 d7 6f e7 02         	leaq	0x2e76fd7(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fc6f1: 45 89 e1                     	movl	%r12d, %r9d
 31fc6f4: b9 85 00 00 00               	movl	$0x85, %ecx
 31fc6f9: bf 02 00 00 00               	movl	$0x2, %edi
 31fc6fe: 41 83 c4 01                  	addl	$0x1, %r12d
 31fc702: 50                           	pushq	%rax
 31fc703: 8b 44 24 6c                  	movl	0x6c(%rsp), %eax
 31fc707: 50                           	pushq	%rax
 31fc708: 8b 44 24 70                  	movl	0x70(%rsp), %eax
 31fc70c: 50                           	pushq	%rax
 31fc70d: 8b 44 24 74                  	movl	0x74(%rsp), %eax
 31fc711: 50                           	pushq	%rax
 31fc712: 8b 44 24 78                  	movl	0x78(%rsp), %eax
 31fc716: 50                           	pushq	%rax
 31fc717: 8b 44 24 7c                  	movl	0x7c(%rsp), %eax
 31fc71b: 50                           	pushq	%rax
 31fc71c: 8b 84 24 80 00 00 00         	movl	0x80(%rsp), %eax
 31fc723: 50                           	pushq	%rax
 31fc724: 8b 84 24 84 00 00 00         	movl	0x84(%rsp), %eax
 31fc72b: 50                           	pushq	%rax
 31fc72c: 8b 84 24 ac 00 00 00         	movl	0xac(%rsp), %eax
 31fc733: 50                           	pushq	%rax
 31fc734: 31 c0                        	xorl	%eax, %eax
 31fc736: e8 f5 35 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fc73b: 48 83 c4 50                  	addq	$0x50, %rsp
 31fc73f: 44 39 64 24 64               	cmpl	%r12d, 0x64(%rsp)
 31fc744: 0f 8f be fe ff ff            	jg	0x31fc608 <ExSLEglFunction::initialize(void*)+0x8d8>
 31fc74a: 0f b6 5c 24 3f               	movzbl	0x3f(%rsp), %ebx
 31fc74f: e9 cc fc ff ff               	jmp	0x31fc420 <ExSLEglFunction::initialize(void*)+0x6f0>
 31fc754: 4c 8d 05 0d 70 e7 02         	leaq	0x2e7700d(%rip), %r8    # 0x6073768 <typeinfo name for ExSLEglSurface+0xe8>
 31fc75b: 48 8d 15 e6 72 e7 02         	leaq	0x2e772e6(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fc762: 48 8d 35 5f 6f e7 02         	leaq	0x2e76f5f(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fc769: b9 68 00 00 00               	movl	$0x68, %ecx
 31fc76e: bf 03 00 00 00               	movl	$0x3, %edi
 31fc773: 31 c0                        	xorl	%eax, %eax
 31fc775: e8 b6 35 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fc77a: e9 e4 f5 ff ff               	jmp	0x31fbd63 <ExSLEglFunction::initialize(void*)+0x33>
 31fc77f: 4c 8d 05 82 70 e7 02         	leaq	0x2e77082(%rip), %r8    # 0x6073808 <typeinfo name for ExSLEglSurface+0x188>
 31fc786: 48 8d 15 bb 72 e7 02         	leaq	0x2e772bb(%rip), %rdx   # 0x6073a48 <ExSLEglFunction::initialize(void*)::__func__>
 31fc78d: 48 8d 35 34 6f e7 02         	leaq	0x2e76f34(%rip), %rsi   # 0x60736c8 <typeinfo name for ExSLEglSurface+0x48>
 31fc794: b9 9e 00 00 00               	movl	$0x9e, %ecx
 31fc799: bf 02 00 00 00               	movl	$0x2, %edi
 31fc79e: 31 c0                        	xorl	%eax, %eax
 31fc7a0: e8 8b 35 61 ff               	callq	0x280fd30 <printExSLLog(ecExSLLogLevel, char const*, char const*, unsigned int, char const*, ...)>
 31fc7a5: e9 b9 f5 ff ff               	jmp	0x31fbd63 <ExSLEglFunction::initialize(void*)+0x33>
 31fc7aa: 45 31 e4                     	xorl	%r12d, %r12d
 31fc7ad: e9 56 fa ff ff               	jmp	0x31fc208 <ExSLEglFunction::initialize(void*)+0x4d8>
 31fc7b2: e8 d9 e3 24 fe               	callq	0x144ab90 <__stack_chk_fail@plt>
 31fc7b7: 48 89 c3                     	movq	%rax, %rbx
 31fc7ba: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 31fc7bf: 48 8b bc 24 90 00 00 00      	movq	0x90(%rsp), %rdi
 31fc7c7: 48 83 c0 10                  	addq	$0x10, %rax
 31fc7cb: 48 39 c7                     	cmpq	%rax, %rdi
 31fc7ce: 0f 84 94 f7 ff ff            	je	0x31fbf68 <ExSLEglFunction::initialize(void*)+0x238>
 31fc7d4: e8 d7 e6 24 fe               	callq	0x144aeb0 <_ZdlPv@plt>
 31fc7d9: e9 8a f7 ff ff               	jmp	0x31fbf68 <ExSLEglFunction::initialize(void*)+0x238>
 31fc7de: 48 89 c3                     	movq	%rax, %rbx
 31fc7e1: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
 31fc7e6: 48 8b bc 24 90 00 00 00      	movq	0x90(%rsp), %rdi
 31fc7ee: 48 83 c0 10                  	addq	$0x10, %rax
 31fc7f2: 48 39 c7                     	cmpq	%rax, %rdi
 31fc7f5: 0f 85 7b f7 ff ff            	jne	0x31fbf76 <ExSLEglFunction::initialize(void*)+0x246>
 31fc7fb: e9 7b f7 ff ff               	jmp	0x31fbf7b <ExSLEglFunction::initialize(void*)+0x24b>
 31fc800: eb dc                        	jmp	0x31fc7de <ExSLEglFunction::initialize(void*)+0xaae>
 31fc802: 0f 1f 40 00                  	nopl	(%rax)
 31fc806: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
