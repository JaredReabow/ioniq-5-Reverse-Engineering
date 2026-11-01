# Exact ABL IAS key-trust disassembly
# Source: decompressed IBB stage 1
# Source SHA-256: 3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2
# Load base: 0x000e0000
# Tool: Homebrew LLVM version 23.1.3

## type-3 OS caller (file [0xc1d0,0xc220))

<decompressed-ibb-stage1>:	file format elf32-i386

Disassembly of section .text:

000e0000 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start>:
   ec1d0:      	mov	eax, dword ptr [0xe8000fc0]
   ec1d5:      	ljmp	-0x7a0a, 0x59000099
   ec1dc:      	aam	-0x2
   ec1de:      	<unknown>
   ec1e0:      	add	al, 0x5b
   ec1e2:      	je	0xec203 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0xc203>
   ec1e4:      	push	0x27
   ec1e6:      	push	dword ptr [ebp + 0xc]
   ec1e9:      	push	esi
   ec1ea:      	call	0xf57a3 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x157a3>
   ec1ef:      	test	eax, eax
   ec1f1:      	jne	0xec203 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0xc203>
   ec1f3:      	push	0xfc0a9
   ec1f8:      	call	0xf5bc3 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15bc3>
   ec1fd:      	pop	edx
   ec1fe:      	jmp	0xec420 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0xc420>
   ec203:      	movzx	eax, word ptr [esi + 0x6]
   ec207:      	cmp	eax, 0x3
   ec20a:      	jne	0xec251 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0xc251>
   ec20c:      	mov	ebx, dword ptr [ebp - 0xfc]
   ec212:      	mov	esi, dword ptr [ebp - 0xf8]
   ec218:      	test	byte ptr [0xc0210], 0x1
   ec21f:      	je	0xec3e1 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0xc3e1>

## key hash and RSA authentication (file [0x157a3,0x159fe))

<decompressed-ibb-stage1>:	file format elf32-i386

Disassembly of section .text:

000e0000 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start>:
   f57a3:      	push	ebp
   f57a4:      	mov	ebp, esp
   f57a6:      	push	edi
   f57a7:      	push	esi
   f57a8:      	push	ebx
   f57a9:      	sub	esp, 0x270
   f57af:      	mov	eax, dword ptr [ebp + 0x8]
   f57b2:      	mov	edi, dword ptr [ebp + 0x8]
   f57b5:      	mov	ecx, dword ptr [ebp + 0x10]
   f57b8:      	mov	eax, dword ptr [eax + 0xc]
   f57bb:      	add	eax, dword ptr [edi + 0x10]
   f57be:      	mov	dword ptr [ebp - 0x260], eax
   f57c4:      	add	eax, 0x103
   f57c9:      	xor	al, al
   f57cb:      	mov	dword ptr [ebp - 0x264], eax
   f57d1:      	xor	eax, eax
   f57d3:      	test	byte ptr [edi + 0x5], 0x2
   f57d7:      	je	0xf59f6 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x159f6>
   f57dd:      	mov	eax, dword ptr [0xc10c8]
   f57e2:      	mov	ebx, dword ptr [0xc1060]
   f57e8:      	and	eax, 0xffffff
   f57ed:      	mov	byte ptr [ebp - 0x25a], 0x0
   f57f4:      	mov	dword ptr [ebp - 0x274], eax
   f57fa:      	mov	eax, dword ptr [0xc1064]
   f57ff:      	mov	dword ptr [ebp - 0x258], eax
   f5805:      	mov	eax, ecx
   f5807:      	shr	eax, 0x3
   f580a:      	and	ecx, 0x7
   f580d:      	mov	dword ptr [ebp - 0x270], eax
   f5813:      	mov	eax, 0x1
   f5818:      	shl	eax, cl
   f581a:      	mov	dword ptr [ebp - 0x278], eax
   f5820:      	mov	ecx, 0xc10c0
   f5825:      	mov	byte ptr [ebp - 0x259], 0x0
   f582c:      	mov	dword ptr [ebp - 0x268], 0x0
   f5836:      	mov	edi, dword ptr [ebp - 0x274]
   f583c:      	cmp	dword ptr [ebp - 0x268], edi
   f5842:      	jge	0xf5921 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15921>
   f5848:      	mov	al, byte ptr [ecx + 0xe]
   f584b:      	and	eax, 0x7f
   f584e:      	cmp	al, 0xb
   f5850:      	je	0xf585d <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x1585d>
   f5852:      	inc	dword ptr [ebp - 0x268]
   f5858:      	add	ecx, 0x10
   f585b:      	jmp	0xf5836 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15836>
   f585d:      	mov	edi, dword ptr [ecx]
   f585f:      	xor	edx, edx
   f5861:      	mov	esi, 0x44
   f5866:      	mov	eax, dword ptr [edi + 0x288]
   f586c:      	mov	dword ptr [ebp - 0x26c], eax
   f5872:      	sub	eax, 0x24
   f5875:      	div	esi
   f5877:      	mov	dword ptr [ebp - 0x27c], eax
   f587d:      	test	ebx, ebx
   f587f:      	lea	eax, [edi + 0x2a8]
   f5885:      	jne	0xf58a7 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x158a7>
   f5887:      	mov	esi, dword ptr [ebp - 0x26c]
   f588d:      	lea	ebx, [edi + 0x284]
   f5893:      	mov	dword ptr [ebp - 0x258], esi
   f5899:      	mov	byte ptr [ebp - 0x25a], 0x1
   f58a0:      	mov	byte ptr [ebp - 0x259], 0x1
   f58a7:      	xor	edx, edx
   f58a9:      	cmp	dword ptr [ebp - 0x27c], edx
   f58af:      	jle	0xf5852 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15852>
   f58b1:      	mov	esi, dword ptr [ebp - 0x270]
   f58b7:      	movzx	esi, byte ptr [eax + esi]
   f58bb:      	test	dword ptr [ebp - 0x278], esi
   f58c1:      	je	0xf591b <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x1591b>
   f58c3:      	cmp	byte ptr [ebp - 0x259], 0x0
   f58ca:      	je	0xf58d2 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x158d2>
   f58cc:      	mov	dword ptr [0xc1060], ebx
   f58d2:      	cmp	byte ptr [ebp - 0x25a], 0x0
   f58d9:      	je	0xf58e7 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x158e7>
   f58db:      	mov	esi, dword ptr [ebp - 0x258]
   f58e1:      	mov	dword ptr [0xc1064], esi
   f58e7:      	lea	edi, [ebp - 0x234]
   f58ed:      	lea	esi, [eax + 0x24]
   f58f0:      	mov	ecx, 0x8
   f58f5:      	rep		movsd	dword ptr es:[edi], dword ptr [esi]
   f58f7:      	cmp	dword ptr [ebp + 0xc], 0x0
   f58fb:      	jne	0xf594b <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x1594b>
   f58fd:      	mov	eax, dword ptr [ebp - 0x260]
   f5903:      	lea	ebx, [ebp - 0x254]
   f5909:      	add	eax, 0x4
   f590c:      	push	ebx
   f590d:      	push	eax
   f590e:      	push	dword ptr [ebp + 0x8]
   f5911:      	call	0xf6bd0 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16bd0>
   f5916:      	mov	dword ptr [ebp + 0xc], ebx
   f5919:      	jmp	0xf594b <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x1594b>
   f591b:      	add	eax, 0x44
   f591e:      	inc	edx
   f591f:      	jmp	0xf58a9 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x158a9>
   f5921:      	cmp	byte ptr [ebp - 0x259], 0x0
   f5928:      	je	0xf5930 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15930>
   f592a:      	mov	dword ptr [0xc1060], ebx
   f5930:      	cmp	byte ptr [ebp - 0x25a], 0x0
   f5937:      	je	0xf5944 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15944>
   f5939:      	mov	eax, dword ptr [ebp - 0x258]
   f593f:      	mov	dword ptr [0xc1064], eax
   f5944:      	xor	eax, eax
   f5946:      	jmp	0xf59f6 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x159f6>
   f594b:      	mov	eax, dword ptr [ebp + 0x8]
   f594e:      	mov	edx, dword ptr [ebp - 0x264]
   f5954:      	lea	esi, [ebp - 0x115]
   f595a:      	lea	edx, [eax + edx + 0x100]
   f5961:      	xor	eax, eax
   f5963:      	mov	ebx, esi
   f5965:      	mov	cl, byte ptr [edx + eax]
   f5968:      	sub	ebx, eax
   f596a:      	inc	eax
   f596b:      	lea	edi, [ebp - 0x214]
   f5971:      	cmp	eax, 0x100
   f5976:      	mov	byte ptr [ebx], cl
   f5978:      	jne	0xf5963 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15963>
   f597a:      	mov	eax, dword ptr [edx + 0x100]
   f5980:      	lea	ebx, [ebp - 0x110]
   f5986:      	mov	dword ptr [ebp - 0x258], edx
   f598c:      	push	ebx
   f598d:      	mov	dword ptr [ebp - 0x114], eax
   f5993:      	push	0x104
   f5998:      	push	edi
   f5999:      	call	0xf6bd0 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16bd0>
   f599e:      	lea	eax, [ebp - 0x234]
   f59a4:      	push	0x20
   f59a6:      	push	ebx
   f59a7:      	push	eax
   f59a8:      	call	0xf60d8 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x160d8>
   f59ad:      	mov	edx, dword ptr [ebp - 0x258]
   f59b3:      	test	eax, eax
   f59b5:      	jne	0xf5944 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x15944>
   f59b7:      	mov	esi, edx
   f59b9:      	mov	ecx, 0x40
   f59be:      	mov	edi, ebx
   f59c0:      	mov	eax, dword ptr [edx + 0x100]
   f59c6:      	rep		movsd	dword ptr es:[edi], dword ptr [esi]
   f59c8:      	mov	dword ptr [ebp - 0x10], eax
   f59cb:      	mov	eax, dword ptr [ebp - 0x264]
   f59d1:      	add	eax, dword ptr [ebp + 0x8]
   f59d4:      	push	0x100
   f59d9:      	push	eax
   f59da:      	lea	eax, [ebp - 0x10]
   f59dd:      	push	0x3
   f59df:      	push	eax
   f59e0:      	push	0x100
   f59e5:      	push	ebx
   f59e6:      	push	dword ptr [ebp + 0xc]
   f59e9:      	call	0xf6c0c <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16c0c>
   f59ee:      	test	eax, eax
   f59f0:      	sete	al
   f59f3:      	movzx	eax, al
   f59f6:      	lea	esp, [ebp - 0xc]
   f59f9:      	pop	ebx
   f59fa:      	pop	esi
   f59fb:      	pop	edi
   f59fc:      	pop	ebp
   f59fd:      	ret	0xc

## 32-byte comparison (file [0x160d8,0x16100))

<decompressed-ibb-stage1>:	file format elf32-i386

Disassembly of section .text:

000e0000 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start>:
   f60d8:      	push	ebp
   f60d9:      	xor	edx, edx
   f60db:      	mov	ebp, esp
   f60dd:      	cmp	dword ptr [ebp + 0x10], edx
   f60e0:      	je	0xf60fa <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x160fa>
   f60e2:      	mov	eax, dword ptr [ebp + 0x8]
   f60e5:      	mov	ecx, dword ptr [ebp + 0xc]
   f60e8:      	movzx	eax, byte ptr [eax + edx]
   f60ec:      	inc	edx
   f60ed:      	movzx	ecx, byte ptr [ecx + edx - 0x1]
   f60f2:      	cmp	al, cl
   f60f4:      	je	0xf60dd <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x160dd>
   f60f6:      	sub	eax, ecx
   f60f8:      	jmp	0xf60fc <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x160fc>
   f60fa:      	xor	eax, eax
   f60fc:      	pop	ebp
   f60fd:      	ret	0xc

## SHA-256 wrapper (file [0x16bd0,0x16c0c))

<decompressed-ibb-stage1>:	file format elf32-i386

Disassembly of section .text:

000e0000 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start>:
   f6bd0:      	push	esi
   f6bd1:      	push	ebx
   f6bd2:      	sub	esp, 0x20
   f6bd5:      	push	0xff480
   f6bda:      	push	dword ptr [esp + 0x34]
   f6bde:      	push	dword ptr [esp + 0x34]
   f6be2:      	lea	esi, [esp + 0xc]
   f6be6:      	push	esi
   f6be7:      	call	0xf6a8d <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16a8d>
   f6bec:      	mov	ebx, eax
   f6bee:      	test	eax, eax
   f6bf0:      	jne	0xf6c02 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16c02>
   f6bf2:      	mov	ecx, 0x20
   f6bf7:      	mov	edx, dword ptr [esp + 0x34]
   f6bfb:      	mov	eax, esi
   f6bfd:      	call	0xf6808 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16808>
   f6c02:      	add	esp, 0x20
   f6c05:      	mov	eax, ebx
   f6c07:      	pop	ebx
   f6c08:      	pop	esi
   f6c09:      	ret	0xc

## RSA verifier entry (file [0x16c0c,0x16da0))

<decompressed-ibb-stage1>:	file format elf32-i386

Disassembly of section .text:

000e0000 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start>:
   f6c0c:      	push	ebp
   f6c0d:      	push	edi
   f6c0e:      	push	esi
   f6c0f:      	push	ebx
   f6c10:      	sub	esp, 0x2c60
   f6c16:      	mov	ebp, dword ptr [esp + 0x2c78]
   f6c1d:      	mov	edi, dword ptr [esp + 0x2c7c]
   f6c24:      	mov	dword ptr [esp + 0x4], 0x0
   f6c2c:      	cmp	dword ptr [esp + 0x2c74], 0x0
   f6c34:      	je	0xf6d8a <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d8a>
   f6c3a:      	test	ebp, ebp
   f6c3c:      	je	0xf6d8a <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d8a>
   f6c42:      	cmp	dword ptr [esp + 0x2c80], 0x0
   f6c4a:      	je	0xf6d8a <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d8a>
   f6c50:      	cmp	dword ptr [esp + 0x2c88], 0x0
   f6c58:      	je	0xf6d8a <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d8a>
   f6c5e:      	cmp	edi, 0x100
   f6c64:      	jg	0xf6d91 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d91>
   f6c6a:      	cmp	dword ptr [esp + 0x2c8c], 0x100
   f6c75:      	jne	0xf6d91 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d91>
   f6c7b:      	push	esp
   f6c7c:      	push	0x20
   f6c7e:      	push	0x800
   f6c83:      	call	0xf7a08 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x17a08>
   f6c88:      	test	eax, eax
   f6c8a:      	jne	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6c90:      	cmp	dword ptr [esp], 0x162b
   f6c97:      	jle	0xf6ca3 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16ca3>
   f6c99:      	mov	eax, 0xfffffffc
   f6c9e:      	jmp	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6ca3:      	push	0x162b
   f6ca8:      	lea	eax, [esp + 0xe]
   f6cac:      	push	eax
   f6cad:      	push	0x20
   f6caf:      	push	0x800
   f6cb4:      	call	0xf7a3e <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x17a3e>
   f6cb9:      	test	eax, eax
   f6cbb:      	jne	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6cc1:      	lea	esi, [edi + 0x3]
   f6cc4:      	push	esp
   f6cc5:      	shr	esi, 0x2
   f6cc8:      	push	esi
   f6cc9:      	call	0xf8218 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x18218>
   f6cce:      	test	eax, eax
   f6cd0:      	jne	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6cd6:      	cmp	dword ptr [esp], 0x237
   f6cdd:      	jg	0xf6c99 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16c99>
   f6cdf:      	mov	eax, dword ptr [esp + 0x2c84]
   f6ce6:      	push	esp
   f6ce7:      	lea	ebx, [eax + 0x3]
   f6cea:      	shr	ebx, 0x2
   f6ced:      	push	ebx
   f6cee:      	call	0xf8218 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x18218>
   f6cf3:      	test	eax, eax
   f6cf5:      	jne	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6cfb:      	cmp	dword ptr [esp], 0x47
   f6cff:      	jg	0xf6c99 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16c99>
   f6d01:      	push	0xcf4e0
   f6d06:      	push	esi
   f6d07:      	call	0xf822e <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x1822e>
   f6d0c:      	push	0xcf4e0
   f6d11:      	push	edi
   f6d12:      	push	ebp
   f6d13:      	call	0xf7117 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x17117>
   f6d18:      	push	0xcf480
   f6d1d:      	push	ebx
   f6d1e:      	call	0xf822e <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x1822e>
   f6d23:      	push	0xcf480
   f6d28:      	push	dword ptr [esp + 0x2c88]
   f6d2f:      	push	dword ptr [esp + 0x2c88]
   f6d36:      	call	0xf7117 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x17117>
   f6d3b:      	lea	ebx, [esp + 0xa]
   f6d3f:      	push	ebx
   f6d40:      	push	0xcf480
   f6d45:      	push	0xcf4e0
   f6d4a:      	call	0xf7acd <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x17acd>
   f6d4f:      	test	eax, eax
   f6d51:      	jne	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6d53:      	lea	eax, [esp + 0x1635]
   f6d5a:      	push	eax
   f6d5b:      	push	0x2
   f6d5d:      	push	ebx
   f6d5e:      	lea	eax, [esp + 0x10]
   f6d62:      	push	eax
   f6d63:      	push	dword ptr [esp + 0x2c98]
   f6d6a:      	push	0x20
   f6d6c:      	push	dword ptr [esp + 0x2c8c]
   f6d73:      	call	0xf81ae <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x181ae>
   f6d78:      	test	eax, eax
   f6d7a:      	jne	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6d7c:      	xor	eax, eax
   f6d7e:      	cmp	dword ptr [esp + 0x4], 0x0
   f6d83:      	sete	al
   f6d86:      	neg	eax
   f6d88:      	jmp	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6d8a:      	mov	eax, 0xfffffff8
   f6d8f:      	jmp	0xf6d96 <_binary_work_abl_ias_extract_IBB_sub1_172d2_lz4_bin_start+0x16d96>
   f6d91:      	mov	eax, 0xfffffffa
   f6d96:      	add	esp, 0x2c60
   f6d9c:      	pop	ebx
   f6d9d:      	pop	esi
   f6d9e:      	pop	edi
   f6d9f:      	pop	ebp
