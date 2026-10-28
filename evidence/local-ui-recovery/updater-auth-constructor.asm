
/Applications/Navigation Updater.app/Contents/MacOS/Navigation Updater:	file format mach-o 64-bit x86-64

Disassembly of section __TEXT,__text:

000000010019fe20 <AuthenticationService::changeDownloadCode(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char>>, std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char>>)>:
1001a2b31: bf 28 00 00 00              	movl	$0x28, %edi
1001a2b36: e8 f5 0a 18 00              	callq	0x100323630 <dyld_stub_binder+0x100323630>
1001a2b3b: 48 89 05 2e 7c de 03        	movq	%rax, 0x3de7c2e(%rip)   ## 0x103f8a770 <AuthenticationConstants::ENCRYPT_IV+0x10>
1001a2b42: 48 8d 35 17 7c de 03        	leaq	0x3de7c17(%rip), %rsi   ## 0x103f8a760 <AuthenticationConstants::ENCRYPT_IV>
1001a2b49: 48 c7 05 0c 7c de 03 29 00 00 00    	movq	$0x29, 0x3de7c0c(%rip) ## 0x103f8a760 <AuthenticationConstants::ENCRYPT_IV>
1001a2b54: 48 c7 05 09 7c de 03 20 00 00 00    	movq	$0x20, 0x3de7c09(%rip) ## 0x103f8a768 <AuthenticationConstants::ENCRYPT_IV+0x8>
1001a2b5f: 0f 10 05 81 de d9 03        	movups	0x3d9de81(%rip), %xmm0  ## 0x103f409e7 <dyld_stub_binder+0x103f409e7>
1001a2b66: 0f 11 40 10                 	movups	%xmm0, 0x10(%rax)
1001a2b6a: 0f 10 05 66 de d9 03        	movups	0x3d9de66(%rip), %xmm0  ## 0x103f409d7 <dyld_stub_binder+0x103f409d7>
1001a2b71: 0f 11 00                    	movups	%xmm0, (%rax)
1001a2b74: c6 40 20 00                 	movb	$0x0, 0x20(%rax)
1001a2b78: 4c 89 f7                    	movq	%r14, %rdi
1001a2b7b: 48 89 da                    	movq	%rbx, %rdx
1001a2b7e: e8 c5 0a 18 00              	callq	0x100323648 <dyld_stub_binder+0x100323648>
1001a2b83: bf 28 00 00 00              	movl	$0x28, %edi
1001a2b88: e8 a3 0a 18 00              	callq	0x100323630 <dyld_stub_binder+0x100323630>
1001a2b8d: 48 89 05 f4 7b de 03        	movq	%rax, 0x3de7bf4(%rip)   ## 0x103f8a788 <AuthenticationConstants::ENCRYPT_KEY+0x10>
1001a2b94: 48 8d 35 dd 7b de 03        	leaq	0x3de7bdd(%rip), %rsi   ## 0x103f8a778 <AuthenticationConstants::ENCRYPT_KEY>
1001a2b9b: 48 c7 05 d2 7b de 03 29 00 00 00    	movq	$0x29, 0x3de7bd2(%rip) ## 0x103f8a778 <AuthenticationConstants::ENCRYPT_KEY>
1001a2ba6: 48 c7 05 cf 7b de 03 20 00 00 00    	movq	$0x20, 0x3de7bcf(%rip) ## 0x103f8a780 <AuthenticationConstants::ENCRYPT_KEY+0x8>
1001a2bb1: 0f 10 05 50 de d9 03        	movups	0x3d9de50(%rip), %xmm0  ## 0x103f40a08 <dyld_stub_binder+0x103f40a08>
1001a2bb8: 0f 11 40 10                 	movups	%xmm0, 0x10(%rax)
1001a2bbc: 0f 10 05 35 de d9 03        	movups	0x3d9de35(%rip), %xmm0  ## 0x103f409f8 <dyld_stub_binder+0x103f409f8>
1001a2bc3: 0f 11 00                    	movups	%xmm0, (%rax)
1001a2bc6: c6 40 20 00                 	movb	$0x0, 0x20(%rax)
1001a2bca: 4c 89 f7                    	movq	%r14, %rdi
1001a2bcd: 48 89 da                    	movq	%rbx, %rdx
1001a2bd0: e8 73 0a 18 00              	callq	0x100323648 <dyld_stub_binder+0x100323648>
