
work/decrypted-eu-260128/extracted-safe/mango-rootfs/lib/libc-2.25.so:	file format elf64-x86-64

Disassembly of section .text:

000000000011fc80 <__nss_passwd_lookup>:
  128000: c5 e9 73 fa 06               	vpslldq	$0x6, %xmm2, %xmm2      # xmm2 = zero,zero,zero,zero,zero,zero,xmm2[0,1,2,3,4,5,6,7,8,9]
  128005: c5 f1 64 fc                  	vpcmpgtb	%xmm4, %xmm1, %xmm7
  128009: c5 71 64 c5                  	vpcmpgtb	%xmm5, %xmm1, %xmm8
  12800d: c5 69 64 cc                  	vpcmpgtb	%xmm4, %xmm2, %xmm9
  128011: c5 69 64 d5                  	vpcmpgtb	%xmm5, %xmm2, %xmm10
  128015: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128019: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  12801e: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128022: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  128026: c5 b9 eb c9                  	vpor	%xmm1, %xmm8, %xmm1
  12802a: c5 a9 eb d2                  	vpor	%xmm2, %xmm10, %xmm2
  12802e: c5 e9 74 d1                  	vpcmpeqb	%xmm1, %xmm2, %xmm2
  128032: c5 e9 f8 d0                  	vpsubb	%xmm0, %xmm2, %xmm2
  128036: c5 79 d7 ca                  	vpmovmskb	%xmm2, %r9d
  12803a: d3 ea                        	shrl	%cl, %edx
  12803c: 41 d3 e9                     	shrl	%cl, %r9d
  12803f: 44 29 ca                     	subl	%r9d, %edx
  128042: 0f 85 15 09 00 00            	jne	0x12895d <__nss_passwd_lookup+0x8cdd>
  128048: c5 f9 6f 1f                  	vmovdqa	(%rdi), %xmm3
  12804c: 4e 8d 4c 19 f0               	leaq	-0x10(%rcx,%r11), %r9
  128051: 4d 39 cb                     	cmpq	%r9, %r11
  128054: 0f 82 37 09 00 00            	jb	0x128991 <__nss_passwd_lookup+0x8d11>
  12805a: 4d 85 c9                     	testq	%r9, %r9
  12805d: 0f 84 2e 09 00 00            	je	0x128991 <__nss_passwd_lookup+0x8d11>
  128063: 4d 89 cb                     	movq	%r9, %r11
  128066: 48 c7 c1 10 00 00 00         	movq	$0x10, %rcx
  12806d: 41 b9 0a 00 00 00            	movl	$0xa, %r9d
  128073: 4c 8d 57 0a                  	leaq	0xa(%rdi), %r10
  128077: 49 81 e2 ff 0f 00 00         	andq	$0xfff, %r10            # imm = 0xFFF
  12807e: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128085: 48 89 ca                     	movq	%rcx, %rdx
  128088: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  128090: 49 83 c2 10                  	addq	$0x10, %r10
  128094: 0f 8f b6 00 00 00            	jg	0x128150 <__nss_passwd_lookup+0x84d0>
  12809a: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12809f: c4 e3 79 0f 44 17 f0 0a      	vpalignr	$0xa, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[10,11,12,13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9]
  1280a7: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  1280ac: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  1280b0: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  1280b4: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  1280b8: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  1280bc: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  1280c0: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  1280c5: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1280c9: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1280cd: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  1280d1: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  1280d5: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  1280db: 0f 86 4f 08 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  1280e1: 49 83 eb 10                  	subq	$0x10, %r11
  1280e5: 0f 86 a6 08 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  1280eb: 48 83 c2 10                  	addq	$0x10, %rdx
  1280ef: 49 83 c2 10                  	addq	$0x10, %r10
  1280f3: 7f 5b                        	jg	0x128150 <__nss_passwd_lookup+0x84d0>
  1280f5: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  1280fa: c4 e3 79 0f 44 17 f0 0a      	vpalignr	$0xa, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[10,11,12,13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9]
  128102: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  128107: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  12810b: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  12810f: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128113: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  128117: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  12811b: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  128120: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128124: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  128128: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  12812c: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  128130: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  128136: 0f 86 f4 07 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  12813c: 49 83 eb 10                  	subq	$0x10, %r11
  128140: 0f 86 4b 08 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  128146: 48 83 c2 10                  	addq	$0x10, %rdx
  12814a: e9 41 ff ff ff               	jmp	0x128090 <__nss_passwd_lookup+0x8410>
  12814f: 90                           	nop
  128150: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128157: c5 f9 6f 44 17 f0            	vmovdqa	-0x10(%rdi,%rdx), %xmm0
  12815d: c5 f9 73 d8 0a               	vpsrldq	$0xa, %xmm0, %xmm0      # xmm0 = xmm0[10,11,12,13,14,15],zero,zero,zero,zero,zero,zero,zero,zero,zero,zero
  128162: c4 e3 79 63 c0 3a            	vpcmpistri	$0x3a, %xmm0, %xmm0
  128168: 4c 39 d9                     	cmpq	%r11, %rcx
  12816b: 0f 83 85 07 00 00            	jae	0x1288f6 <__nss_passwd_lookup+0x8c76>
  128171: 83 f9 05                     	cmpl	$0x5, %ecx
  128174: 0f 87 20 ff ff ff            	ja	0x12809a <__nss_passwd_lookup+0x841a>
  12817a: e9 77 07 00 00               	jmp	0x1288f6 <__nss_passwd_lookup+0x8c76>
  12817f: 90                           	nop
  128180: c5 e9 73 fa 05               	vpslldq	$0x5, %xmm2, %xmm2      # xmm2 = zero,zero,zero,zero,zero,xmm2[0,1,2,3,4,5,6,7,8,9,10]
  128185: c5 f1 64 fc                  	vpcmpgtb	%xmm4, %xmm1, %xmm7
  128189: c5 71 64 c5                  	vpcmpgtb	%xmm5, %xmm1, %xmm8
  12818d: c5 69 64 cc                  	vpcmpgtb	%xmm4, %xmm2, %xmm9
  128191: c5 69 64 d5                  	vpcmpgtb	%xmm5, %xmm2, %xmm10
  128195: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128199: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  12819e: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1281a2: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1281a6: c5 b9 eb c9                  	vpor	%xmm1, %xmm8, %xmm1
  1281aa: c5 a9 eb d2                  	vpor	%xmm2, %xmm10, %xmm2
  1281ae: c5 e9 74 d1                  	vpcmpeqb	%xmm1, %xmm2, %xmm2
  1281b2: c5 e9 f8 d0                  	vpsubb	%xmm0, %xmm2, %xmm2
  1281b6: c5 79 d7 ca                  	vpmovmskb	%xmm2, %r9d
  1281ba: d3 ea                        	shrl	%cl, %edx
  1281bc: 41 d3 e9                     	shrl	%cl, %r9d
  1281bf: 44 29 ca                     	subl	%r9d, %edx
  1281c2: 0f 85 95 07 00 00            	jne	0x12895d <__nss_passwd_lookup+0x8cdd>
  1281c8: c5 f9 6f 1f                  	vmovdqa	(%rdi), %xmm3
  1281cc: 4e 8d 4c 19 f0               	leaq	-0x10(%rcx,%r11), %r9
  1281d1: 4d 39 cb                     	cmpq	%r9, %r11
  1281d4: 0f 82 b7 07 00 00            	jb	0x128991 <__nss_passwd_lookup+0x8d11>
  1281da: 4d 85 c9                     	testq	%r9, %r9
  1281dd: 0f 84 ae 07 00 00            	je	0x128991 <__nss_passwd_lookup+0x8d11>
  1281e3: 4d 89 cb                     	movq	%r9, %r11
  1281e6: 48 c7 c1 10 00 00 00         	movq	$0x10, %rcx
  1281ed: 41 b9 0b 00 00 00            	movl	$0xb, %r9d
  1281f3: 4c 8d 57 0b                  	leaq	0xb(%rdi), %r10
  1281f7: 49 81 e2 ff 0f 00 00         	andq	$0xfff, %r10            # imm = 0xFFF
  1281fe: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128205: 48 89 ca                     	movq	%rcx, %rdx
  128208: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  128210: 49 83 c2 10                  	addq	$0x10, %r10
  128214: 0f 8f b6 00 00 00            	jg	0x1282d0 <__nss_passwd_lookup+0x8650>
  12821a: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12821f: c4 e3 79 0f 44 17 f0 0b      	vpalignr	$0xb, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[11,12,13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10]
  128227: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  12822c: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  128230: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  128234: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128238: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  12823c: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128240: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  128245: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128249: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  12824d: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  128251: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  128255: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  12825b: 0f 86 cf 06 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  128261: 49 83 eb 10                  	subq	$0x10, %r11
  128265: 0f 86 26 07 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  12826b: 48 83 c2 10                  	addq	$0x10, %rdx
  12826f: 49 83 c2 10                  	addq	$0x10, %r10
  128273: 7f 5b                        	jg	0x1282d0 <__nss_passwd_lookup+0x8650>
  128275: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12827a: c4 e3 79 0f 44 17 f0 0b      	vpalignr	$0xb, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[11,12,13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10]
  128282: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  128287: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  12828b: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  12828f: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128293: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  128297: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  12829b: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  1282a0: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1282a4: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1282a8: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  1282ac: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  1282b0: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  1282b6: 0f 86 74 06 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  1282bc: 49 83 eb 10                  	subq	$0x10, %r11
  1282c0: 0f 86 cb 06 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  1282c6: 48 83 c2 10                  	addq	$0x10, %rdx
  1282ca: e9 41 ff ff ff               	jmp	0x128210 <__nss_passwd_lookup+0x8590>
  1282cf: 90                           	nop
  1282d0: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  1282d7: c5 f9 6f 44 17 f0            	vmovdqa	-0x10(%rdi,%rdx), %xmm0
  1282dd: c5 f9 73 d8 0b               	vpsrldq	$0xb, %xmm0, %xmm0      # xmm0 = xmm0[11,12,13,14,15],zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero
  1282e2: c4 e3 79 63 c0 3a            	vpcmpistri	$0x3a, %xmm0, %xmm0
  1282e8: 4c 39 d9                     	cmpq	%r11, %rcx
  1282eb: 0f 83 05 06 00 00            	jae	0x1288f6 <__nss_passwd_lookup+0x8c76>
  1282f1: 83 f9 04                     	cmpl	$0x4, %ecx
  1282f4: 0f 87 20 ff ff ff            	ja	0x12821a <__nss_passwd_lookup+0x859a>
  1282fa: e9 f7 05 00 00               	jmp	0x1288f6 <__nss_passwd_lookup+0x8c76>
  1282ff: 90                           	nop
  128300: c5 e9 73 fa 04               	vpslldq	$0x4, %xmm2, %xmm2      # xmm2 = zero,zero,zero,zero,xmm2[0,1,2,3,4,5,6,7,8,9,10,11]
  128305: c5 f1 64 fc                  	vpcmpgtb	%xmm4, %xmm1, %xmm7
  128309: c5 71 64 c5                  	vpcmpgtb	%xmm5, %xmm1, %xmm8
  12830d: c5 69 64 cc                  	vpcmpgtb	%xmm4, %xmm2, %xmm9
  128311: c5 69 64 d5                  	vpcmpgtb	%xmm5, %xmm2, %xmm10
  128315: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128319: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  12831e: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128322: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  128326: c5 b9 eb c9                  	vpor	%xmm1, %xmm8, %xmm1
  12832a: c5 a9 eb d2                  	vpor	%xmm2, %xmm10, %xmm2
  12832e: c5 e9 74 d1                  	vpcmpeqb	%xmm1, %xmm2, %xmm2
  128332: c5 e9 f8 d0                  	vpsubb	%xmm0, %xmm2, %xmm2
  128336: c5 79 d7 ca                  	vpmovmskb	%xmm2, %r9d
  12833a: d3 ea                        	shrl	%cl, %edx
  12833c: 41 d3 e9                     	shrl	%cl, %r9d
  12833f: 44 29 ca                     	subl	%r9d, %edx
  128342: 0f 85 15 06 00 00            	jne	0x12895d <__nss_passwd_lookup+0x8cdd>
  128348: c5 f9 6f 1f                  	vmovdqa	(%rdi), %xmm3
  12834c: 4e 8d 4c 19 f0               	leaq	-0x10(%rcx,%r11), %r9
  128351: 4d 39 cb                     	cmpq	%r9, %r11
  128354: 0f 82 37 06 00 00            	jb	0x128991 <__nss_passwd_lookup+0x8d11>
  12835a: 4d 85 c9                     	testq	%r9, %r9
  12835d: 0f 84 2e 06 00 00            	je	0x128991 <__nss_passwd_lookup+0x8d11>
  128363: 4d 89 cb                     	movq	%r9, %r11
  128366: 48 c7 c1 10 00 00 00         	movq	$0x10, %rcx
  12836d: 41 b9 0c 00 00 00            	movl	$0xc, %r9d
  128373: 4c 8d 57 0c                  	leaq	0xc(%rdi), %r10
  128377: 49 81 e2 ff 0f 00 00         	andq	$0xfff, %r10            # imm = 0xFFF
  12837e: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128385: 48 89 ca                     	movq	%rcx, %rdx
  128388: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  128390: 49 83 c2 10                  	addq	$0x10, %r10
  128394: 0f 8f b6 00 00 00            	jg	0x128450 <__nss_passwd_lookup+0x87d0>
  12839a: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12839f: c4 e3 79 0f 44 17 f0 0c      	vpalignr	$0xc, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[12,13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11]
  1283a7: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  1283ac: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  1283b0: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  1283b4: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  1283b8: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  1283bc: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  1283c0: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  1283c5: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1283c9: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1283cd: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  1283d1: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  1283d5: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  1283db: 0f 86 4f 05 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  1283e1: 49 83 eb 10                  	subq	$0x10, %r11
  1283e5: 0f 86 a6 05 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  1283eb: 48 83 c2 10                  	addq	$0x10, %rdx
  1283ef: 49 83 c2 10                  	addq	$0x10, %r10
  1283f3: 7f 5b                        	jg	0x128450 <__nss_passwd_lookup+0x87d0>
  1283f5: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  1283fa: c4 e3 79 0f 44 17 f0 0c      	vpalignr	$0xc, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[12,13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11]
  128402: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  128407: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  12840b: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  12840f: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128413: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  128417: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  12841b: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  128420: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128424: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  128428: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  12842c: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  128430: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  128436: 0f 86 f4 04 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  12843c: 49 83 eb 10                  	subq	$0x10, %r11
  128440: 0f 86 4b 05 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  128446: 48 83 c2 10                  	addq	$0x10, %rdx
  12844a: e9 41 ff ff ff               	jmp	0x128390 <__nss_passwd_lookup+0x8710>
  12844f: 90                           	nop
  128450: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128457: c5 f9 6f 44 17 f0            	vmovdqa	-0x10(%rdi,%rdx), %xmm0
  12845d: c5 f9 73 d8 0c               	vpsrldq	$0xc, %xmm0, %xmm0      # xmm0 = xmm0[12,13,14,15],zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero
  128462: c4 e3 79 63 c0 3a            	vpcmpistri	$0x3a, %xmm0, %xmm0
  128468: 4c 39 d9                     	cmpq	%r11, %rcx
  12846b: 0f 83 85 04 00 00            	jae	0x1288f6 <__nss_passwd_lookup+0x8c76>
  128471: 83 f9 03                     	cmpl	$0x3, %ecx
  128474: 0f 87 20 ff ff ff            	ja	0x12839a <__nss_passwd_lookup+0x871a>
  12847a: e9 77 04 00 00               	jmp	0x1288f6 <__nss_passwd_lookup+0x8c76>
  12847f: 90                           	nop
  128480: c5 e9 73 fa 03               	vpslldq	$0x3, %xmm2, %xmm2      # xmm2 = zero,zero,zero,xmm2[0,1,2,3,4,5,6,7,8,9,10,11,12]
  128485: c5 f1 64 fc                  	vpcmpgtb	%xmm4, %xmm1, %xmm7
  128489: c5 71 64 c5                  	vpcmpgtb	%xmm5, %xmm1, %xmm8
  12848d: c5 69 64 cc                  	vpcmpgtb	%xmm4, %xmm2, %xmm9
  128491: c5 69 64 d5                  	vpcmpgtb	%xmm5, %xmm2, %xmm10
  128495: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128499: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  12849e: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1284a2: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1284a6: c5 b9 eb c9                  	vpor	%xmm1, %xmm8, %xmm1
  1284aa: c5 a9 eb d2                  	vpor	%xmm2, %xmm10, %xmm2
  1284ae: c5 e9 74 d1                  	vpcmpeqb	%xmm1, %xmm2, %xmm2
  1284b2: c5 e9 f8 d0                  	vpsubb	%xmm0, %xmm2, %xmm2
  1284b6: c5 79 d7 ca                  	vpmovmskb	%xmm2, %r9d
  1284ba: d3 ea                        	shrl	%cl, %edx
  1284bc: 41 d3 e9                     	shrl	%cl, %r9d
  1284bf: 44 29 ca                     	subl	%r9d, %edx
  1284c2: 0f 85 95 04 00 00            	jne	0x12895d <__nss_passwd_lookup+0x8cdd>
  1284c8: c5 f9 6f 1f                  	vmovdqa	(%rdi), %xmm3
  1284cc: 4e 8d 4c 19 f0               	leaq	-0x10(%rcx,%r11), %r9
  1284d1: 4d 39 cb                     	cmpq	%r9, %r11
  1284d4: 0f 82 b7 04 00 00            	jb	0x128991 <__nss_passwd_lookup+0x8d11>
  1284da: 4d 85 c9                     	testq	%r9, %r9
  1284dd: 0f 84 ae 04 00 00            	je	0x128991 <__nss_passwd_lookup+0x8d11>
  1284e3: 4d 89 cb                     	movq	%r9, %r11
  1284e6: 48 c7 c1 10 00 00 00         	movq	$0x10, %rcx
  1284ed: 41 b9 0d 00 00 00            	movl	$0xd, %r9d
  1284f3: 4c 8d 57 0d                  	leaq	0xd(%rdi), %r10
  1284f7: 49 81 e2 ff 0f 00 00         	andq	$0xfff, %r10            # imm = 0xFFF
  1284fe: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128505: 48 89 ca                     	movq	%rcx, %rdx
  128508: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  128510: 49 83 c2 10                  	addq	$0x10, %r10
  128514: 0f 8f b6 00 00 00            	jg	0x1285d0 <__nss_passwd_lookup+0x8950>
  12851a: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12851f: c4 e3 79 0f 44 17 f0 0d      	vpalignr	$0xd, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11,12]
  128527: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  12852c: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  128530: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  128534: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128538: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  12853c: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128540: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  128545: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128549: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  12854d: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  128551: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  128555: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  12855b: 0f 86 cf 03 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  128561: 49 83 eb 10                  	subq	$0x10, %r11
  128565: 0f 86 26 04 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  12856b: 48 83 c2 10                  	addq	$0x10, %rdx
  12856f: 49 83 c2 10                  	addq	$0x10, %r10
  128573: 7f 5b                        	jg	0x1285d0 <__nss_passwd_lookup+0x8950>
  128575: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12857a: c4 e3 79 0f 44 17 f0 0d      	vpalignr	$0xd, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[13,14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11,12]
  128582: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  128587: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  12858b: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  12858f: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128593: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  128597: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  12859b: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  1285a0: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1285a4: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1285a8: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  1285ac: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  1285b0: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  1285b6: 0f 86 74 03 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  1285bc: 49 83 eb 10                  	subq	$0x10, %r11
  1285c0: 0f 86 cb 03 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  1285c6: 48 83 c2 10                  	addq	$0x10, %rdx
  1285ca: e9 41 ff ff ff               	jmp	0x128510 <__nss_passwd_lookup+0x8890>
  1285cf: 90                           	nop
  1285d0: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  1285d7: c5 f9 6f 44 17 f0            	vmovdqa	-0x10(%rdi,%rdx), %xmm0
  1285dd: c5 f9 73 d8 0d               	vpsrldq	$0xd, %xmm0, %xmm0      # xmm0 = xmm0[13,14,15],zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero
  1285e2: c4 e3 79 63 c0 3a            	vpcmpistri	$0x3a, %xmm0, %xmm0
  1285e8: 4c 39 d9                     	cmpq	%r11, %rcx
  1285eb: 0f 83 05 03 00 00            	jae	0x1288f6 <__nss_passwd_lookup+0x8c76>
  1285f1: 83 f9 02                     	cmpl	$0x2, %ecx
  1285f4: 0f 87 20 ff ff ff            	ja	0x12851a <__nss_passwd_lookup+0x889a>
  1285fa: e9 f7 02 00 00               	jmp	0x1288f6 <__nss_passwd_lookup+0x8c76>
  1285ff: 90                           	nop
  128600: c5 e9 73 fa 02               	vpslldq	$0x2, %xmm2, %xmm2      # xmm2 = zero,zero,xmm2[0,1,2,3,4,5,6,7,8,9,10,11,12,13]
  128605: c5 f1 64 fc                  	vpcmpgtb	%xmm4, %xmm1, %xmm7
  128609: c5 71 64 c5                  	vpcmpgtb	%xmm5, %xmm1, %xmm8
  12860d: c5 69 64 cc                  	vpcmpgtb	%xmm4, %xmm2, %xmm9
  128611: c5 69 64 d5                  	vpcmpgtb	%xmm5, %xmm2, %xmm10
  128615: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128619: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  12861e: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128622: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  128626: c5 b9 eb c9                  	vpor	%xmm1, %xmm8, %xmm1
  12862a: c5 a9 eb d2                  	vpor	%xmm2, %xmm10, %xmm2
  12862e: c5 e9 74 d1                  	vpcmpeqb	%xmm1, %xmm2, %xmm2
  128632: c5 e9 f8 d0                  	vpsubb	%xmm0, %xmm2, %xmm2
  128636: c5 79 d7 ca                  	vpmovmskb	%xmm2, %r9d
  12863a: d3 ea                        	shrl	%cl, %edx
  12863c: 41 d3 e9                     	shrl	%cl, %r9d
  12863f: 44 29 ca                     	subl	%r9d, %edx
  128642: 0f 85 15 03 00 00            	jne	0x12895d <__nss_passwd_lookup+0x8cdd>
  128648: c5 f9 6f 1f                  	vmovdqa	(%rdi), %xmm3
  12864c: 4e 8d 4c 19 f0               	leaq	-0x10(%rcx,%r11), %r9
  128651: 4d 39 cb                     	cmpq	%r9, %r11
  128654: 0f 82 37 03 00 00            	jb	0x128991 <__nss_passwd_lookup+0x8d11>
  12865a: 4d 85 c9                     	testq	%r9, %r9
  12865d: 0f 84 2e 03 00 00            	je	0x128991 <__nss_passwd_lookup+0x8d11>
  128663: 4d 89 cb                     	movq	%r9, %r11
  128666: 48 c7 c1 10 00 00 00         	movq	$0x10, %rcx
  12866d: 41 b9 0e 00 00 00            	movl	$0xe, %r9d
  128673: 4c 8d 57 0e                  	leaq	0xe(%rdi), %r10
  128677: 49 81 e2 ff 0f 00 00         	andq	$0xfff, %r10            # imm = 0xFFF
  12867e: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128685: 48 89 ca                     	movq	%rcx, %rdx
  128688: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  128690: 49 83 c2 10                  	addq	$0x10, %r10
  128694: 0f 8f b6 00 00 00            	jg	0x128750 <__nss_passwd_lookup+0x8ad0>
  12869a: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12869f: c4 e3 79 0f 44 17 f0 0e      	vpalignr	$0xe, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11,12,13]
  1286a7: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  1286ac: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  1286b0: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  1286b4: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  1286b8: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  1286bc: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  1286c0: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  1286c5: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1286c9: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1286cd: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  1286d1: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  1286d5: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  1286db: 0f 86 4f 02 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  1286e1: 49 83 eb 10                  	subq	$0x10, %r11
  1286e5: 0f 86 a6 02 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  1286eb: 48 83 c2 10                  	addq	$0x10, %rdx
  1286ef: 49 83 c2 10                  	addq	$0x10, %r10
  1286f3: 7f 5b                        	jg	0x128750 <__nss_passwd_lookup+0x8ad0>
  1286f5: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  1286fa: c4 e3 79 0f 44 17 f0 0e      	vpalignr	$0xe, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[14,15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11,12,13]
  128702: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  128707: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  12870b: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  12870f: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128713: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  128717: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  12871b: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  128720: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128724: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  128728: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  12872c: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  128730: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  128736: 0f 86 f4 01 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  12873c: 49 83 eb 10                  	subq	$0x10, %r11
  128740: 0f 86 4b 02 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  128746: 48 83 c2 10                  	addq	$0x10, %rdx
  12874a: e9 41 ff ff ff               	jmp	0x128690 <__nss_passwd_lookup+0x8a10>
  12874f: 90                           	nop
  128750: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128757: c5 f9 6f 44 17 f0            	vmovdqa	-0x10(%rdi,%rdx), %xmm0
  12875d: c5 f9 73 d8 0e               	vpsrldq	$0xe, %xmm0, %xmm0      # xmm0 = xmm0[14,15],zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero
  128762: c4 e3 79 63 c0 3a            	vpcmpistri	$0x3a, %xmm0, %xmm0
  128768: 4c 39 d9                     	cmpq	%r11, %rcx
  12876b: 0f 83 85 01 00 00            	jae	0x1288f6 <__nss_passwd_lookup+0x8c76>
  128771: 83 f9 01                     	cmpl	$0x1, %ecx
  128774: 0f 87 20 ff ff ff            	ja	0x12869a <__nss_passwd_lookup+0x8a1a>
  12877a: e9 77 01 00 00               	jmp	0x1288f6 <__nss_passwd_lookup+0x8c76>
  12877f: 90                           	nop
  128780: c5 e9 73 fa 01               	vpslldq	$0x1, %xmm2, %xmm2      # xmm2 = zero,xmm2[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
  128785: c5 f1 64 fc                  	vpcmpgtb	%xmm4, %xmm1, %xmm7
  128789: c5 71 64 c5                  	vpcmpgtb	%xmm5, %xmm1, %xmm8
  12878d: c5 69 64 cc                  	vpcmpgtb	%xmm4, %xmm2, %xmm9
  128791: c5 69 64 d5                  	vpcmpgtb	%xmm5, %xmm2, %xmm10
  128795: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128799: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  12879e: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1287a2: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1287a6: c5 b9 eb c9                  	vpor	%xmm1, %xmm8, %xmm1
  1287aa: c5 a9 eb d2                  	vpor	%xmm2, %xmm10, %xmm2
  1287ae: c5 e9 74 d1                  	vpcmpeqb	%xmm1, %xmm2, %xmm2
  1287b2: c5 e9 f8 d0                  	vpsubb	%xmm0, %xmm2, %xmm2
  1287b6: c5 79 d7 ca                  	vpmovmskb	%xmm2, %r9d
  1287ba: d3 ea                        	shrl	%cl, %edx
  1287bc: 41 d3 e9                     	shrl	%cl, %r9d
  1287bf: 44 29 ca                     	subl	%r9d, %edx
  1287c2: 0f 85 95 01 00 00            	jne	0x12895d <__nss_passwd_lookup+0x8cdd>
  1287c8: c5 f9 6f 1f                  	vmovdqa	(%rdi), %xmm3
  1287cc: 4e 8d 4c 19 f0               	leaq	-0x10(%rcx,%r11), %r9
  1287d1: 4d 39 cb                     	cmpq	%r9, %r11
  1287d4: 0f 82 b7 01 00 00            	jb	0x128991 <__nss_passwd_lookup+0x8d11>
  1287da: 4d 85 c9                     	testq	%r9, %r9
  1287dd: 0f 84 ae 01 00 00            	je	0x128991 <__nss_passwd_lookup+0x8d11>
  1287e3: 4d 89 cb                     	movq	%r9, %r11
  1287e6: 48 c7 c1 10 00 00 00         	movq	$0x10, %rcx
  1287ed: 41 b9 0f 00 00 00            	movl	$0xf, %r9d
  1287f3: 4c 8d 57 0f                  	leaq	0xf(%rdi), %r10
  1287f7: 49 81 e2 ff 0f 00 00         	andq	$0xfff, %r10            # imm = 0xFFF
  1287fe: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  128805: 48 89 ca                     	movq	%rcx, %rdx
  128808: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  128810: 49 83 c2 10                  	addq	$0x10, %r10
  128814: 0f 8f b6 00 00 00            	jg	0x1288d0 <__nss_passwd_lookup+0x8c50>
  12881a: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12881f: c4 e3 79 0f 44 17 f0 0f      	vpalignr	$0xf, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
  128827: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  12882c: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  128830: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  128834: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128838: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  12883c: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  128840: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  128845: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128849: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  12884d: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  128851: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  128855: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  12885b: 0f 86 cf 00 00 00            	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  128861: 49 83 eb 10                  	subq	$0x10, %r11
  128865: 0f 86 26 01 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  12886b: 48 83 c2 10                  	addq	$0x10, %rdx
  12886f: 49 83 c2 10                  	addq	$0x10, %r10
  128873: 7f 5b                        	jg	0x1288d0 <__nss_passwd_lookup+0x8c50>
  128875: c5 f9 6f 04 17               	vmovdqa	(%rdi,%rdx), %xmm0
  12887a: c4 e3 79 0f 44 17 f0 0f      	vpalignr	$0xf, -0x10(%rdi,%rdx), %xmm0, %xmm0 # xmm0 = mem[15],xmm0[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
  128882: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  128887: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  12888b: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  12888f: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128893: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  128897: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  12889b: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  1288a0: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  1288a4: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  1288a8: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  1288ac: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  1288b0: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  1288b6: 76 78                        	jbe	0x128930 <__nss_passwd_lookup+0x8cb0>
  1288b8: 49 83 eb 10                  	subq	$0x10, %r11
  1288bc: 0f 86 cf 00 00 00            	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  1288c2: 48 83 c2 10                  	addq	$0x10, %rdx
  1288c6: e9 45 ff ff ff               	jmp	0x128810 <__nss_passwd_lookup+0x8b90>
  1288cb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
  1288d0: 49 81 ea 00 10 00 00         	subq	$0x1000, %r10           # imm = 0x1000
  1288d7: c5 f9 6f 44 17 f0            	vmovdqa	-0x10(%rdi,%rdx), %xmm0
  1288dd: c5 f9 73 d8 0f               	vpsrldq	$0xf, %xmm0, %xmm0      # xmm0 = xmm0[15],zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero,zero
  1288e2: c4 e3 79 63 c0 3a            	vpcmpistri	$0x3a, %xmm0, %xmm0
  1288e8: 4c 39 d9                     	cmpq	%r11, %rcx
  1288eb: 73 09                        	jae	0x1288f6 <__nss_passwd_lookup+0x8c76>
  1288ed: 83 f9 00                     	cmpl	$0x0, %ecx
  1288f0: 0f 87 24 ff ff ff            	ja	0x12881a <__nss_passwd_lookup+0x8b9a>
  1288f6: c5 f9 6f 0c 16               	vmovdqa	(%rsi,%rdx), %xmm1
  1288fb: c5 f9 64 fc                  	vpcmpgtb	%xmm4, %xmm0, %xmm7
  1288ff: c5 79 64 c5                  	vpcmpgtb	%xmm5, %xmm0, %xmm8
  128903: c5 71 64 cc                  	vpcmpgtb	%xmm4, %xmm1, %xmm9
  128907: c5 71 64 d5                  	vpcmpgtb	%xmm5, %xmm1, %xmm10
  12890b: c5 39 df c7                  	vpandn	%xmm7, %xmm8, %xmm8
  12890f: c4 41 29 df d1               	vpandn	%xmm9, %xmm10, %xmm10
  128914: c5 39 db c6                  	vpand	%xmm6, %xmm8, %xmm8
  128918: c5 29 db d6                  	vpand	%xmm6, %xmm10, %xmm10
  12891c: c5 b9 eb c0                  	vpor	%xmm0, %xmm8, %xmm0
  128920: c5 a9 eb c9                  	vpor	%xmm1, %xmm10, %xmm1
  128924: c4 e3 79 63 c1 1a            	vpcmpistri	$0x1a, %xmm1, %xmm0
  12892a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
  128930: 73 5f                        	jae	0x128991 <__nss_passwd_lookup+0x8d11>
  128932: 49 29 cb                     	subq	%rcx, %r11
  128935: 76 5a                        	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  128937: 48 01 ca                     	addq	%rcx, %rdx
  12893a: 4a 8d 7c 0f f0               	leaq	-0x10(%rdi,%r9), %rdi
  12893f: 0f b6 04 17                  	movzbl	(%rdi,%rdx), %eax
  128943: 0f b6 14 16                  	movzbl	(%rsi,%rdx), %edx
  128947: 45 85 c0                     	testl	%r8d, %r8d
  12894a: 74 01                        	je	0x12894d <__nss_passwd_lookup+0x8ccd>
  12894c: 92                           	xchgl	%edx, %eax
  12894d: 48 8d 0d 0c 2b 02 00         	leaq	0x22b0c(%rip), %rcx     # 0x14b460
  128954: 8b 14 91                     	movl	(%rcx,%rdx,4), %edx
  128957: 8b 04 81                     	movl	(%rcx,%rax,4), %eax
  12895a: 29 d0                        	subl	%edx, %eax
  12895c: c3                           	retq
  12895d: 48 8d 3c 07                  	leaq	(%rdi,%rax), %rdi
  128961: 48 8d 34 0e                  	leaq	(%rsi,%rcx), %rsi
  128965: 45 85 c0                     	testl	%r8d, %r8d
  128968: 74 06                        	je	0x128970 <__nss_passwd_lookup+0x8cf0>
  12896a: 48 87 f7                     	xchgq	%rdi, %rsi
  12896d: 0f 1f 00                     	nopl	(%rax)
  128970: 48 0f bc d2                  	bsfq	%rdx, %rdx
  128974: 49 29 d3                     	subq	%rdx, %r11
  128977: 76 18                        	jbe	0x128991 <__nss_passwd_lookup+0x8d11>
  128979: 0f b6 0c 16                  	movzbl	(%rsi,%rdx), %ecx
  12897d: 0f b6 04 17                  	movzbl	(%rdi,%rdx), %eax
  128981: 48 8d 15 d8 2a 02 00         	leaq	0x22ad8(%rip), %rdx     # 0x14b460
  128988: 8b 0c 8a                     	movl	(%rdx,%rcx,4), %ecx
  12898b: 8b 04 82                     	movl	(%rdx,%rax,4), %eax
  12898e: 29 c8                        	subl	%ecx, %eax
  128990: c3                           	retq
  128991: 31 c0                        	xorl	%eax, %eax
  128993: c3                           	retq
  128994: 66 90                        	nop
  128996: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
  1289a0: 0f b6 0e                     	movzbl	(%rsi), %ecx
  1289a3: 0f b6 07                     	movzbl	(%rdi), %eax
  1289a6: 48 8d 15 b3 2a 02 00         	leaq	0x22ab3(%rip), %rdx     # 0x14b460
  1289ad: 8b 0c 8a                     	movl	(%rdx,%rcx,4), %ecx
  1289b0: 8b 04 82                     	movl	(%rdx,%rax,4), %eax
  1289b3: 29 c8                        	subl	%ecx, %eax
  1289b5: c3                           	retq
  1289b6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
  1289c0: 48 39 d1                     	cmpq	%rdx, %rcx
  1289c3: 0f 82 77 eb fc ff            	jb	0xf7540 <__chk_fail>
  1289c9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
  1289d0: 48 89 f8                     	movq	%rdi, %rax
  1289d3: 48 01 d0                     	addq	%rdx, %rax
  1289d6: eb 1b                        	jmp	0x1289f3 <__nss_passwd_lookup+0x8d73>
  1289d8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  1289e0: 48 39 d1                     	cmpq	%rdx, %rcx
  1289e3: 0f 82 57 eb fc ff            	jb	0xf7540 <__chk_fail>
  1289e9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
  1289f0: 48 89 f8                     	movq	%rdi, %rax
  1289f3: 48 83 fa 20                  	cmpq	$0x20, %rdx
  1289f7: 0f 82 a5 00 00 00            	jb	0x128aa2 <__nss_passwd_lookup+0x8e22>
  1289fd: 48 83 fa 40                  	cmpq	$0x40, %rdx
  128a01: 0f 87 08 01 00 00            	ja	0x128b0f <__nss_passwd_lookup+0x8e8f>
  128a07: c5 fe 6f 06                  	vmovdqu	(%rsi), %ymm0
  128a0b: c5 fe 6f 4c 16 e0            	vmovdqu	-0x20(%rsi,%rdx), %ymm1
  128a11: c5 fe 7f 07                  	vmovdqu	%ymm0, (%rdi)
  128a15: c5 fe 7f 4c 17 e0            	vmovdqu	%ymm1, -0x20(%rdi,%rdx)
  128a1b: c5 f8 77                     	vzeroupper
  128a1e: c3                           	retq
  128a1f: 90                           	nop
  128a20: 48 39 d1                     	cmpq	%rdx, %rcx
  128a23: 0f 82 17 eb fc ff            	jb	0xf7540 <__chk_fail>
  128a29: 0f 1f 80 00 00 00 00         	nopl	(%rax)
  128a30: 48 89 f8                     	movq	%rdi, %rax
  128a33: 48 01 d0                     	addq	%rdx, %rax
  128a36: eb 1b                        	jmp	0x128a53 <__nss_passwd_lookup+0x8dd3>
  128a38: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
  128a40: 48 39 d1                     	cmpq	%rdx, %rcx
  128a43: 0f 82 f7 ea fc ff            	jb	0xf7540 <__chk_fail>
  128a49: 0f 1f 80 00 00 00 00         	nopl	(%rax)
  128a50: 48 89 f8                     	movq	%rdi, %rax
  128a53: 48 83 fa 20                  	cmpq	$0x20, %rdx
  128a57: 72 49                        	jb	0x128aa2 <__nss_passwd_lookup+0x8e22>
  128a59: 48 83 fa 40                  	cmpq	$0x40, %rdx
  128a5d: 0f 87 9f 00 00 00            	ja	0x128b02 <__nss_passwd_lookup+0x8e82>
  128a63: c5 fe 6f 06                  	vmovdqu	(%rsi), %ymm0
  128a67: c5 fe 6f 4c 16 e0            	vmovdqu	-0x20(%rsi,%rdx), %ymm1
  128a6d: c5 fe 7f 07                  	vmovdqu	%ymm0, (%rdi)
  128a71: c5 fe 7f 4c 17 e0            	vmovdqu	%ymm1, -0x20(%rdi,%rdx)
  128a77: c5 f8 77                     	vzeroupper
  128a7a: c3                           	retq
  128a7b: 48 3b 15 26 5a 27 00         	cmpq	0x275a26(%rip), %rdx    # 0x39e4a8 <mallwatch+0x8>
  128a82: 0f 83 25 01 00 00            	jae	0x128bad <__nss_passwd_lookup+0x8f2d>
  128a88: 48 39 f7                     	cmpq	%rsi, %rdi
  128a8b: 72 0f                        	jb	0x128a9c <__nss_passwd_lookup+0x8e1c>
  128a8d: 74 12                        	je	0x128aa1 <__nss_passwd_lookup+0x8e21>
  128a8f: 4c 8d 0c 16                  	leaq	(%rsi,%rdx), %r9
  128a93: 4c 39 cf                     	cmpq	%r9, %rdi
  128a96: 0f 82 c5 01 00 00            	jb	0x128c61 <__nss_passwd_lookup+0x8fe1>
  128a9c: 48 89 d1                     	movq	%rdx, %rcx
  128a9f: f3 a4                        	rep		movsb	(%rsi), %es:(%rdi)
  128aa1: c3                           	retq
  128aa2: 80 fa 10                     	cmpb	$0x10, %dl
  128aa5: 73 17                        	jae	0x128abe <__nss_passwd_lookup+0x8e3e>
  128aa7: 80 fa 08                     	cmpb	$0x8, %dl
  128aaa: 73 27                        	jae	0x128ad3 <__nss_passwd_lookup+0x8e53>
  128aac: 80 fa 04                     	cmpb	$0x4, %dl
  128aaf: 73 33                        	jae	0x128ae4 <__nss_passwd_lookup+0x8e64>
  128ab1: 80 fa 01                     	cmpb	$0x1, %dl
  128ab4: 77 3b                        	ja	0x128af1 <__nss_passwd_lookup+0x8e71>
  128ab6: 72 05                        	jb	0x128abd <__nss_passwd_lookup+0x8e3d>
  128ab8: 0f b6 0e                     	movzbl	(%rsi), %ecx
  128abb: 88 0f                        	movb	%cl, (%rdi)
  128abd: c3                           	retq
  128abe: c5 fa 6f 06                  	vmovdqu	(%rsi), %xmm0
  128ac2: c5 fa 6f 4c 16 f0            	vmovdqu	-0x10(%rsi,%rdx), %xmm1
  128ac8: c5 fa 7f 07                  	vmovdqu	%xmm0, (%rdi)
  128acc: c5 fa 7f 4c 17 f0            	vmovdqu	%xmm1, -0x10(%rdi,%rdx)
  128ad2: c3                           	retq
  128ad3: 48 8b 4c 16 f8               	movq	-0x8(%rsi,%rdx), %rcx
  128ad8: 48 8b 36                     	movq	(%rsi), %rsi
  128adb: 48 89 4c 17 f8               	movq	%rcx, -0x8(%rdi,%rdx)
  128ae0: 48 89 37                     	movq	%rsi, (%rdi)
  128ae3: c3                           	retq
  128ae4: 8b 4c 16 fc                  	movl	-0x4(%rsi,%rdx), %ecx
  128ae8: 8b 36                        	movl	(%rsi), %esi
  128aea: 89 4c 17 fc                  	movl	%ecx, -0x4(%rdi,%rdx)
  128aee: 89 37                        	movl	%esi, (%rdi)
  128af0: c3                           	retq
  128af1: 0f b7 4c 16 fe               	movzwl	-0x2(%rsi,%rdx), %ecx
  128af6: 0f b7 36                     	movzwl	(%rsi), %esi
  128af9: 66 89 4c 17 fe               	movw	%cx, -0x2(%rdi,%rdx)
  128afe: 66 89 37                     	movw	%si, (%rdi)
  128b01: c3                           	retq
  128b02: 48 81 fa 00 10 00 00         	cmpq	$0x1000, %rdx           # imm = 0x1000
  128b09: 0f 87 6c ff ff ff            	ja	0x128a7b <__nss_passwd_lookup+0x8dfb>
  128b0f: 48 81 fa 00 01 00 00         	cmpq	$0x100, %rdx            # imm = 0x100
  128b16: 0f 87 91 00 00 00            	ja	0x128bad <__nss_passwd_lookup+0x8f2d>
  128b1c: 48 81 fa 80 00 00 00         	cmpq	$0x80, %rdx
  128b23: 72 5a                        	jb	0x128b7f <__nss_passwd_lookup+0x8eff>
  128b25: c5 fe 6f 06                  	vmovdqu	(%rsi), %ymm0
  128b29: c5 fe 6f 4e 20               	vmovdqu	0x20(%rsi), %ymm1
  128b2e: c5 fe 6f 56 40               	vmovdqu	0x40(%rsi), %ymm2
  128b33: c5 fe 6f 5e 60               	vmovdqu	0x60(%rsi), %ymm3
  128b38: c5 fe 6f 64 16 e0            	vmovdqu	-0x20(%rsi,%rdx), %ymm4
  128b3e: c5 fe 6f 6c 16 c0            	vmovdqu	-0x40(%rsi,%rdx), %ymm5
  128b44: c5 fe 6f 74 16 a0            	vmovdqu	-0x60(%rsi,%rdx), %ymm6
  128b4a: c5 fe 6f 7c 16 80            	vmovdqu	-0x80(%rsi,%rdx), %ymm7
  128b50: c5 fe 7f 07                  	vmovdqu	%ymm0, (%rdi)
  128b54: c5 fe 7f 4f 20               	vmovdqu	%ymm1, 0x20(%rdi)
  128b59: c5 fe 7f 57 40               	vmovdqu	%ymm2, 0x40(%rdi)
  128b5e: c5 fe 7f 5f 60               	vmovdqu	%ymm3, 0x60(%rdi)
  128b63: c5 fe 7f 64 17 e0            	vmovdqu	%ymm4, -0x20(%rdi,%rdx)
  128b69: c5 fe 7f 6c 17 c0            	vmovdqu	%ymm5, -0x40(%rdi,%rdx)
  128b6f: c5 fe 7f 74 17 a0            	vmovdqu	%ymm6, -0x60(%rdi,%rdx)
  128b75: c5 fe 7f 7c 17 80            	vmovdqu	%ymm7, -0x80(%rdi,%rdx)
  128b7b: c5 f8 77                     	vzeroupper
  128b7e: c3                           	retq
  128b7f: c5 fe 6f 06                  	vmovdqu	(%rsi), %ymm0
  128b83: c5 fe 6f 4e 20               	vmovdqu	0x20(%rsi), %ymm1
  128b88: c5 fe 6f 54 16 e0            	vmovdqu	-0x20(%rsi,%rdx), %ymm2
  128b8e: c5 fe 6f 5c 16 c0            	vmovdqu	-0x40(%rsi,%rdx), %ymm3
  128b94: c5 fe 7f 07                  	vmovdqu	%ymm0, (%rdi)
  128b98: c5 fe 7f 4f 20               	vmovdqu	%ymm1, 0x20(%rdi)
  128b9d: c5 fe 7f 54 17 e0            	vmovdqu	%ymm2, -0x20(%rdi,%rdx)
  128ba3: c5 fe 7f 5c 17 c0            	vmovdqu	%ymm3, -0x40(%rdi,%rdx)
  128ba9: c5 f8 77                     	vzeroupper
  128bac: c3                           	retq
  128bad: 48 39 f7                     	cmpq	%rsi, %rdi
  128bb0: 0f 87 ab 00 00 00            	ja	0x128c61 <__nss_passwd_lookup+0x8fe1>
  128bb6: 0f 84 e5 fe ff ff            	je	0x128aa1 <__nss_passwd_lookup+0x8e21>
  128bbc: c5 fe 6f 26                  	vmovdqu	(%rsi), %ymm4
  128bc0: c5 fe 6f 6c 16 e0            	vmovdqu	-0x20(%rsi,%rdx), %ymm5
  128bc6: c5 fe 6f 74 16 c0            	vmovdqu	-0x40(%rsi,%rdx), %ymm6
  128bcc: c5 fe 6f 7c 16 a0            	vmovdqu	-0x60(%rsi,%rdx), %ymm7
  128bd2: c5 7e 6f 44 16 80            	vmovdqu	-0x80(%rsi,%rdx), %ymm8
  128bd8: 49 89 fb                     	movq	%rdi, %r11
  128bdb: 48 8d 4c 17 e0               	leaq	-0x20(%rdi,%rdx), %rcx
  128be0: 49 89 f8                     	movq	%rdi, %r8
  128be3: 49 83 e0 1f                  	andq	$0x1f, %r8
  128be7: 49 83 e8 20                  	subq	$0x20, %r8
  128beb: 4c 29 c6                     	subq	%r8, %rsi
  128bee: 4c 29 c7                     	subq	%r8, %rdi
  128bf1: 4c 01 c2                     	addq	%r8, %rdx
  128bf4: 48 3b 15 ad 58 27 00         	cmpq	0x2758ad(%rip), %rdx    # 0x39e4a8 <mallwatch+0x8>
  128bfb: 0f 87 07 01 00 00            	ja	0x128d08 <__nss_passwd_lookup+0x9088>
  128c01: c5 fe 6f 06                  	vmovdqu	(%rsi), %ymm0
  128c05: c5 fe 6f 4e 20               	vmovdqu	0x20(%rsi), %ymm1
  128c0a: c5 fe 6f 56 40               	vmovdqu	0x40(%rsi), %ymm2
  128c0f: c5 fe 6f 5e 60               	vmovdqu	0x60(%rsi), %ymm3
  128c14: 48 81 c6 80 00 00 00         	addq	$0x80, %rsi
  128c1b: 48 81 ea 80 00 00 00         	subq	$0x80, %rdx
  128c22: c5 fd 7f 07                  	vmovdqa	%ymm0, (%rdi)
  128c26: c5 fd 7f 4f 20               	vmovdqa	%ymm1, 0x20(%rdi)
  128c2b: c5 fd 7f 57 40               	vmovdqa	%ymm2, 0x40(%rdi)
  128c30: c5 fd 7f 5f 60               	vmovdqa	%ymm3, 0x60(%rdi)
  128c35: 48 81 c7 80 00 00 00         	addq	$0x80, %rdi
  128c3c: 48 81 fa 80 00 00 00         	cmpq	$0x80, %rdx
  128c43: 77 bc                        	ja	0x128c01 <__nss_passwd_lookup+0x8f81>
  128c45: c5 fe 7f 29                  	vmovdqu	%ymm5, (%rcx)
  128c49: c5 fe 7f 71 e0               	vmovdqu	%ymm6, -0x20(%rcx)
  128c4e: c5 fe 7f 79 c0               	vmovdqu	%ymm7, -0x40(%rcx)
  128c53: c5 7e 7f 41 a0               	vmovdqu	%ymm8, -0x60(%rcx)
  128c58: c4 c1 7e 7f 23               	vmovdqu	%ymm4, (%r11)
  128c5d: c5 f8 77                     	vzeroupper
  128c60: c3                           	retq
  128c61: c5 fe 6f 26                  	vmovdqu	(%rsi), %ymm4
  128c65: c5 fe 6f 6e 20               	vmovdqu	0x20(%rsi), %ymm5
  128c6a: c5 fe 6f 76 40               	vmovdqu	0x40(%rsi), %ymm6
  128c6f: c5 fe 6f 7e 60               	vmovdqu	0x60(%rsi), %ymm7
  128c74: c5 7e 6f 44 16 e0            	vmovdqu	-0x20(%rsi,%rdx), %ymm8
  128c7a: 4c 8d 5c 17 e0               	leaq	-0x20(%rdi,%rdx), %r11
  128c7f: 48 8d 4c 16 e0               	leaq	-0x20(%rsi,%rdx), %rcx
  128c84: 4d 89 d9                     	movq	%r11, %r9
  128c87: 4d 89 d8                     	movq	%r11, %r8
  128c8a: 49 83 e0 1f                  	andq	$0x1f, %r8
  128c8e: 4c 29 c1                     	subq	%r8, %rcx
  128c91: 4d 29 c1                     	subq	%r8, %r9
  128c94: 4c 29 c2                     	subq	%r8, %rdx
  128c97: 48 3b 15 0a 58 27 00         	cmpq	0x27580a(%rip), %rdx    # 0x39e4a8 <mallwatch+0x8>
  128c9e: 0f 87 f0 00 00 00            	ja	0x128d94 <__nss_passwd_lookup+0x9114>
  128ca4: c5 fe 6f 01                  	vmovdqu	(%rcx), %ymm0
  128ca8: c5 fe 6f 49 e0               	vmovdqu	-0x20(%rcx), %ymm1
  128cad: c5 fe 6f 51 c0               	vmovdqu	-0x40(%rcx), %ymm2
  128cb2: c5 fe 6f 59 a0               	vmovdqu	-0x60(%rcx), %ymm3
  128cb7: 48 81 e9 80 00 00 00         	subq	$0x80, %rcx
  128cbe: 48 81 ea 80 00 00 00         	subq	$0x80, %rdx
  128cc5: c4 c1 7d 7f 01               	vmovdqa	%ymm0, (%r9)
  128cca: c4 c1 7d 7f 49 e0            	vmovdqa	%ymm1, -0x20(%r9)
  128cd0: c4 c1 7d 7f 51 c0            	vmovdqa	%ymm2, -0x40(%r9)
  128cd6: c4 c1 7d 7f 59 a0            	vmovdqa	%ymm3, -0x60(%r9)
  128cdc: 49 81 e9 80 00 00 00         	subq	$0x80, %r9
  128ce3: 48 81 fa 80 00 00 00         	cmpq	$0x80, %rdx
  128cea: 77 b8                        	ja	0x128ca4 <__nss_passwd_lookup+0x9024>
  128cec: c5 fe 7f 27                  	vmovdqu	%ymm4, (%rdi)
  128cf0: c5 fe 7f 6f 20               	vmovdqu	%ymm5, 0x20(%rdi)
  128cf5: c5 fe 7f 77 40               	vmovdqu	%ymm6, 0x40(%rdi)
  128cfa: c5 fe 7f 7f 60               	vmovdqu	%ymm7, 0x60(%rdi)
  128cff: c4 41 7e 7f 03               	vmovdqu	%ymm8, (%r11)
  128d04: c5 f8 77                     	vzeroupper
  128d07: c3                           	retq
  128d08: 4c 8d 14 17                  	leaq	(%rdi,%rdx), %r10
  128d0c: 4c 39 d6                     	cmpq	%r10, %rsi
  128d0f: 0f 82 ec fe ff ff            	jb	0x128c01 <__nss_passwd_lookup+0x8f81>
  128d15: 0f 18 8e 00 01 00 00         	prefetcht0	0x100(%rsi)
  128d1c: 0f 18 8e 40 01 00 00         	prefetcht0	0x140(%rsi)
  128d23: 0f 18 8e 80 01 00 00         	prefetcht0	0x180(%rsi)
  128d2a: 0f 18 8e c0 01 00 00         	prefetcht0	0x1c0(%rsi)
  128d31: c5 fe 6f 06                  	vmovdqu	(%rsi), %ymm0
  128d35: c5 fe 6f 4e 20               	vmovdqu	0x20(%rsi), %ymm1
  128d3a: c5 fe 6f 56 40               	vmovdqu	0x40(%rsi), %ymm2
  128d3f: c5 fe 6f 5e 60               	vmovdqu	0x60(%rsi), %ymm3
  128d44: 48 81 c6 80 00 00 00         	addq	$0x80, %rsi
  128d4b: 48 81 ea 80 00 00 00         	subq	$0x80, %rdx
  128d52: c5 fd e7 07                  	vmovntdq	%ymm0, (%rdi)
  128d56: c5 fd e7 4f 20               	vmovntdq	%ymm1, 0x20(%rdi)
  128d5b: c5 fd e7 57 40               	vmovntdq	%ymm2, 0x40(%rdi)
  128d60: c5 fd e7 5f 60               	vmovntdq	%ymm3, 0x60(%rdi)
  128d65: 48 81 c7 80 00 00 00         	addq	$0x80, %rdi
  128d6c: 48 81 fa 80 00 00 00         	cmpq	$0x80, %rdx
  128d73: 77 a0                        	ja	0x128d15 <__nss_passwd_lookup+0x9095>
  128d75: 0f ae f8                     	sfence
  128d78: c5 fe 7f 29                  	vmovdqu	%ymm5, (%rcx)
  128d7c: c5 fe 7f 71 e0               	vmovdqu	%ymm6, -0x20(%rcx)
  128d81: c5 fe 7f 79 c0               	vmovdqu	%ymm7, -0x40(%rcx)
  128d86: c5 7e 7f 41 a0               	vmovdqu	%ymm8, -0x60(%rcx)
  128d8b: c4 c1 7e 7f 23               	vmovdqu	%ymm4, (%r11)
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
