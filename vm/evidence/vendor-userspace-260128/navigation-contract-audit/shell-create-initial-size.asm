
work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/weston/ivi-shell.so:	file format elf64-x86-64

Disassembly of section .text:

0000000000009ed0 <application_surface_create>:
    9ed0: 41 57                        	pushq	%r15
    9ed2: 41 56                        	pushq	%r14
    9ed4: 41 55                        	pushq	%r13
    9ed6: 41 89 d5                     	movl	%edx, %r13d
    9ed9: 41 54                        	pushq	%r12
    9edb: 55                           	pushq	%rbp
    9edc: 48 89 f5                     	movq	%rsi, %rbp
    9edf: 53                           	pushq	%rbx
    9ee0: 48 89 cb                     	movq	%rcx, %rbx
    9ee3: 48 83 ec 28                  	subq	$0x28, %rsp
    9ee7: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9ef0: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    9ef5: 31 c0                        	xorl	%eax, %eax
    9ef7: 48 89 3c 24                  	movq	%rdi, (%rsp)
    9efb: 48 89 f7                     	movq	%rsi, %rdi
    9efe: 44 89 44 24 0c               	movl	%r8d, 0xc(%rsp)
    9f03: e8 28 93 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    9f08: 48 89 df                     	movq	%rbx, %rdi
    9f0b: 49 89 c6                     	movq	%rax, %r14
    9f0e: e8 1d 93 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    9f13: 31 c9                        	xorl	%ecx, %ecx
    9f15: 48 89 ea                     	movq	%rbp, %rdx
    9f18: 48 8d 35 29 3b 00 00         	leaq	0x3b29(%rip), %rsi      # 0xda48 <__func__.11687+0x48>
    9f1f: 48 89 c7                     	movq	%rax, %rdi
    9f22: 48 89 c3                     	movq	%rax, %rbx
    9f25: e8 86 93 ff ff               	callq	0x32b0 <weston_surface_set_role@plt>
    9f2a: 85 c0                        	testl	%eax, %eax
    9f2c: 0f 88 1e 01 00 00            	js	0xa050 <application_surface_create+0x180>
    9f32: 44 89 ee                     	movl	%r13d, %esi
    9f35: 48 89 df                     	movq	%rbx, %rdi
    9f38: e8 f3 b7 ff ff               	callq	0x5730 <ivi_layout_surface_create>
    9f3d: 49 89 c4                     	movq	%rax, %r12
    9f40: 48 85 c0                     	testq	%rax, %rax
    9f43: 0f 84 57 01 00 00            	je	0xa0a0 <application_surface_create+0x1d0>
    9f49: be 78 00 00 00               	movl	$0x78, %esi
    9f4e: bf 01 00 00 00               	movl	$0x1, %edi
    9f53: e8 18 94 ff ff               	callq	0x3370 <calloc@plt>
    9f58: 49 89 c7                     	movq	%rax, %r15
    9f5b: 48 85 c0                     	testq	%rax, %rax
    9f5e: 0f 84 74 01 00 00            	je	0xa0d8 <application_surface_create+0x208>
    9f64: 48 8d 68 48                  	leaq	0x48(%rax), %rbp
    9f68: 48 89 ef                     	movq	%rbp, %rdi
    9f6b: e8 d0 93 ff ff               	callq	0x3340 <wl_list_init@plt>
    9f70: 49 8d 7e 20                  	leaq	0x20(%r14), %rdi
    9f74: 48 89 ee                     	movq	%rbp, %rsi
    9f77: e8 24 97 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    9f7c: 49 8d 77 58                  	leaq	0x58(%r15), %rsi
    9f80: 4c 89 e7                     	movq	%r12, %rdi
    9f83: 4d 89 77 08                  	movq	%r14, 0x8(%r15)
    9f87: 48 8d 05 c2 fd ff ff         	leaq	-0x23e(%rip), %rax      # 0x9d50 <surface_configure_notify>
    9f8e: 45 89 6f 38                  	movl	%r13d, 0x38(%r15)
    9f92: 49 89 47 68                  	movq	%rax, 0x68(%r15)
    9f96: 41 c7 47 3c 00 00 00 00      	movl	$0x0, 0x3c(%r15)
    9f9e: 41 c7 47 40 00 00 00 00      	movl	$0x0, 0x40(%r15)
    9fa6: 4d 89 67 10                  	movq	%r12, 0x10(%r15)
    9faa: e8 f1 e3 ff ff               	callq	0x83a0 <ivi_layout_surface_add_configured_listener>
    9faf: 4c 89 fa                     	movq	%r15, %rdx
    9fb2: 4c 89 e7                     	movq	%r12, %rdi
    9fb5: 48 8d 35 94 01 00 00         	leaq	0x194(%rip), %rsi       # 0xa150 <surface_property_notify>
    9fbc: e8 6f ae ff ff               	callq	0x4e30 <ivi_layout_surface_add_notification>
    9fc1: 48 8d 05 48 03 00 00         	leaq	0x348(%rip), %rax       # 0xa310 <shell_handle_surface_destroy>
    9fc8: 49 89 47 30                  	movq	%rax, 0x30(%r15)
    9fcc: 48 8b 7b 08                  	movq	0x8(%rbx), %rdi
    9fd0: 49 8d 77 20                  	leaq	0x20(%r15), %rsi
    9fd4: e8 c7 96 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    9fd9: 8b 4c 24 0c                  	movl	0xc(%rsp), %ecx
    9fdd: 49 89 5f 18                  	movq	%rbx, 0x18(%r15)
    9fe1: ba 01 00 00 00               	movl	$0x1, %edx
    9fe6: 48 8b 05 db 6f 20 00         	movq	0x206fdb(%rip), %rax    # 0x210fc8 <_GLOBAL_OFFSET_TABLE_+0x3b0>
    9fed: 4c 89 bb 88 02 00 00         	movq	%r15, 0x288(%rbx)
    9ff4: 48 8b 35 b5 6f 20 00         	movq	0x206fb5(%rip), %rsi    # 0x210fb0 <_GLOBAL_OFFSET_TABLE_+0x398>
    9ffb: 48 8b 3c 24                  	movq	(%rsp), %rdi
    9fff: 48 89 83 80 02 00 00         	movq	%rax, 0x280(%rbx)
    a006: e8 85 91 ff ff               	callq	0x3190 <wl_resource_create@plt>
    a00b: 48 85 c0                     	testq	%rax, %rax
    a00e: 74 68                        	je	0xa078 <application_surface_create+0x1a8>
    a010: 48 8b 4c 24 18               	movq	0x18(%rsp), %rcx
    a015: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    a01e: 49 89 07                     	movq	%rax, (%r15)
    a021: 0f 85 d7 00 00 00            	jne	0xa0fe <application_surface_create+0x22e>
    a027: 48 83 c4 28                  	addq	$0x28, %rsp
    a02b: 4c 89 fa                     	movq	%r15, %rdx
    a02e: 48 89 c7                     	movq	%rax, %rdi
    a031: 5b                           	popq	%rbx
    a032: 48 8d 0d 27 02 00 00         	leaq	0x227(%rip), %rcx       # 0xa260 <shell_destroy_shell_surface>
    a039: 5d                           	popq	%rbp
    a03a: 41 5c                        	popq	%r12
    a03c: 41 5d                        	popq	%r13
    a03e: 41 5e                        	popq	%r14
    a040: 41 5f                        	popq	%r15
    a042: 48 8d 35 7f 68 20 00         	leaq	0x20687f(%rip), %rsi    # 0x2108c8 <surface_implementation>
    a049: e9 92 92 ff ff               	jmp	0x32e0 <wl_resource_set_implementation@plt>
    a04e: 66 90                        	nop
