
work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/libc-2.25.so:	file format elf64-x86-64

Disassembly of section .text:

000000000011fc80 <__nss_passwd_lookup>:
  128d90: c5 f8 77                     	vzeroupper
  128d93: c3                           	retq
  128d94: 4c 8d 14 11                  	leaq	(%rcx,%rdx), %r10
  128d98: 4d 39 d1                     	cmpq	%r10, %r9
  128d9b: 0f 82 03 ff ff ff            	jb	0x128ca4 <__nss_passwd_lookup+0x9024>
  128da1: 0f 18 89 00 ff ff ff         	prefetcht0	-0x100(%rcx)
  128da8: 0f 18 89 c0 fe ff ff         	prefetcht0	-0x140(%rcx)
  128daf: 0f 18 89 80 fe ff ff         	prefetcht0	-0x180(%rcx)
  128db6: 0f 18 89 40 fe ff ff         	prefetcht0	-0x1c0(%rcx)
  128dbd: c5 fe 6f 01                  	vmovdqu	(%rcx), %ymm0
  128dc1: c5 fe 6f 49 e0               	vmovdqu	-0x20(%rcx), %ymm1
  128dc6: c5 fe 6f 51 c0               	vmovdqu	-0x40(%rcx), %ymm2
  128dcb: c5 fe 6f 59 a0               	vmovdqu	-0x60(%rcx), %ymm3
  128dd0: 48 81 e9 80 00 00 00         	subq	$0x80, %rcx
  128dd7: 48 81 ea 80 00 00 00         	subq	$0x80, %rdx
  128dde: c4 c1 7d e7 01               	vmovntdq	%ymm0, (%r9)
  128de3: c4 c1 7d e7 49 e0            	vmovntdq	%ymm1, -0x20(%r9)
  128de9: c4 c1 7d e7 51 c0            	vmovntdq	%ymm2, -0x40(%r9)
  128def: c4 c1 7d e7 59 a0            	vmovntdq	%ymm3, -0x60(%r9)
  128df5: 49 81 e9 80 00 00 00         	subq	$0x80, %r9
  128dfc: 48 81 fa 80 00 00 00         	cmpq	$0x80, %rdx
  128e03: 77 9c                        	ja	0x128da1 <__nss_passwd_lookup+0x9121>
  128e05: 0f ae f8                     	sfence
  128e08: c5 fe 7f 27                  	vmovdqu	%ymm4, (%rdi)
  128e0c: c5 fe 7f 6f 20               	vmovdqu	%ymm5, 0x20(%rdi)
  128e11: c5 fe 7f 77 40               	vmovdqu	%ymm6, 0x40(%rdi)
  128e16: c5 fe 7f 7f 60               	vmovdqu	%ymm7, 0x60(%rdi)
  128e1b: c4 41 7e 7f 03               	vmovdqu	%ymm8, (%r11)
