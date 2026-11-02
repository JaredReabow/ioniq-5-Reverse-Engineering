Exact rel.1714-HF3 decompressed IBB stage-1 excerpt
Load base: 0x000e0000
Bytes/raw opcodes intentionally omitted.

ABL configuration image at flash 0x00102e6a:
  image type 0x00060000, payload 0x0a68 bytes
  boot index 2: descriptor kind 2, instance 1, iasImage, predicate pcbver=10 lge.sign=1
  boot index 3: descriptor kind 2, instance 2, iasImage, predicate pcbver=10 lge.sign=1

--- boot dispatch tail: file [0x6ba, 0x70d), runtime [0xe06ba, 0xe070d) ---
000e0000 <stage1>:
   e06ba:      	cmp	eax, 0x2
   e06bd:      	mov	bl, byte ptr [0xc0214]
   e06c3:      	jne	0xe06f3 <stage1>
   e06c5:      	and	ebx, 0x1f
   e06c8:      	movzx	eax, bl
   e06cb:      	push	eax
   e06cc:      	push	0xfa4b6
   e06d1:      	call	0xf5bc3 <stage1>
   e06d6:      	pop	eax
   e06d7:      	cmp	bl, 0x1
   e06da:      	pop	edx
   e06db:      	mov	eax, 0x3
   e06e0:      	je	0xe06ed <stage1>
   e06e2:      	xor	eax, eax
   e06e4:      	cmp	bl, 0x2
   e06e7:      	sete	al
   e06ea:      	lea	eax, [eax + 4*eax]
   e06ed:      	push	eax
   e06ee:      	call	0xe9731 <stage1>
   e06f3:      	cmp	eax, 0x3
   e06f6:      	jne	0xe0702 <stage1>
   e06f8:      	mov	eax, ebx
   e06fa:      	and	eax, 0x1f
   e06fd:      	call	0xe03c2 <stage1>
   e0702:      	and	ebx, 0x1f
   e0705:      	push	ebx
   e0706:      	call	0xeb034 <stage1>
   e070b:      	jmp	0xe06ae <stage1>

--- boot record callback: file [0xae16, 0xaff7), runtime [0xeae16, 0xeaff7) ---
000e0000 <stage1>:
   eae16:      	push	ebp
   eae17:      	mov	ebp, esp
   eae19:      	push	edi
   eae1a:      	push	esi
   eae1b:      	push	ebx
   eae1c:      	sub	esp, 0x10
   eae1f:      	mov	cl, byte ptr [0xc0214]
   eae25:      	mov	eax, dword ptr [ebp + 0xc]
   eae28:      	mov	edi, ecx
   eae2a:      	mov	ebx, dword ptr [ebp + 0x8]
   eae2d:      	and	edi, 0x1f
   eae30:      	mov	dword ptr [ebp - 0x18], edi
   eae33:      	mov	edi, dword ptr [eax]
   eae35:      	mov	edx, dword ptr [ebx]
   eae37:      	lea	ecx, [edi + 0x1]
   eae3a:      	mov	dword ptr [eax], ecx
   eae3c:      	xor	eax, eax
   eae3e:      	cmp	dword ptr [ebp - 0x18], edi
   eae41:      	ja	0xeafef <stage1>
   eae47:      	mov	eax, edx
   eae49:      	and	eax, 0x3
   eae4c:      	lea	esi, [ebx + 4*eax + 0x4]
   eae50:      	lea	eax, [esi + 0x6]
   eae53:      	cmp	dword ptr [esi + 0x2], 0x0
   eae57:      	je	0xeae89 <stage1>
   eae59:      	cmp	byte ptr [esi + 0x2], 0x0
   eae5d:      	jne	0xeae89 <stage1>
   eae5f:      	cmp	byte ptr [esi + 0x3], 0x0
   eae63:      	jne	0xeae89 <stage1>
   eae65:      	mov	cl, byte ptr [esi + 0x4]
   eae68:      	lea	edx, [ecx - 0x21]
   eae6b:      	cmp	dl, 0x5d
   eae6e:      	ja	0xeae89 <stage1>
   eae70:      	mov	cl, byte ptr [esi + 0x5]
   eae73:      	lea	edx, [ecx - 0x21]
   eae76:      	cmp	dl, 0x5d
   eae79:      	ja	0xeae89 <stage1>
   eae7b:      	push	0xfc481
   eae80:      	call	0xf5bc3 <stage1>
   eae85:      	lea	eax, [esi + 0x4]
   eae88:      	pop	edx
   eae89:      	mov	edx, dword ptr [ebx]
   eae8b:      	xor	ecx, ecx
   eae8d:      	and	edx, 0xffc
   eae93:      	add	ebx, edx
   eae95:      	mov	dword ptr [ebp - 0x1c], ebx
   eae98:      	mov	ebx, dword ptr [ebp - 0x1c]
   eae9b:      	xor	edx, edx
   eae9d:      	sub	ebx, eax
   eae9f:      	cmp	edx, ebx
   eaea1:      	jne	0xeaeab <stage1>
   eaea3:      	xor	ebx, ebx
   eaea5:      	test	edx, edx
   eaea7:      	je	0xeaed5 <stage1>
   eaea9:      	jmp	0xeaeb4 <stage1>
   eaeab:      	cmp	byte ptr [eax + edx], 0x0
   eaeaf:      	je	0xeaea3 <stage1>
   eaeb1:      	inc	edx
   eaeb2:      	jmp	0xeae9f <stage1>
   eaeb4:      	lea	ebx, [eax + edx]
   eaeb7:      	cmp	dword ptr [ebp - 0x1c], ebx
   eaeba:      	ja	0xeaed3 <stage1>
   eaebc:      	push	edi
   eaebd:      	push	0xfc4bb
   eaec2:      	call	0xf5bc3 <stage1>
   eaec7:      	pop	ecx
   eaec8:      	mov	eax, 0x1
   eaecd:      	pop	ebx
   eaece:      	jmp	0xeafef <stage1>
   eaed3:      	mov	ebx, eax
   eaed5:      	mov	dword ptr [ebp + 4*ecx - 0x14], ebx
   eaed9:      	inc	ecx
   eaeda:      	lea	eax, [eax + edx + 0x1]
   eaede:      	cmp	ecx, 0x2
   eaee1:      	jne	0xeae98 <stage1>
   eaee3:      	cmp	dword ptr [ebp - 0x18], edi
   eaee6:      	jae	0xeaeef <stage1>
   eaee8:      	push	0x4
   eaeea:      	call	0xe7231 <stage1>
   eaeef:      	cmp	dword ptr [ebp - 0x10], 0x0
   eaef3:      	setne	byte ptr [ebp - 0x18]
   eaef7:      	mov	edx, dword ptr [ebp - 0x14]
   eaefa:      	mov	byte ptr [0xcfc40], 0x0
   eaf01:      	mov	dword ptr [0xce884], edi
   eaf07:      	cmp	dword ptr [0xcfbc0], 0x0
   eaf0e:      	jne	0xeaf20 <stage1>
   eaf10:      	mov	dword ptr [ebp - 0x1c], edx
   eaf13:      	call	0xe71c1 <stage1>
   eaf18:      	mov	edx, dword ptr [ebp - 0x1c]
   eaf1b:      	mov	dword ptr [0xcfbc0], eax
   eaf20:      	mov	al, byte ptr [esi]
   eaf22:      	mov	ebx, 0xe00d8000
   eaf27:      	cmp	al, 0x4
   eaf29:      	je	0xeaf4f <stage1>
   eaf2b:      	mov	ebx, 0xe00e0000
   eaf30:      	cmp	al, 0x3
   eaf32:      	jne	0xeaf4f <stage1>
   eaf34:      	lea	eax, [ebp - 0x10]
   eaf37:      	mov	dword ptr [ebp - 0x1c], edx
   eaf3a:      	push	eax
   eaf3b:      	movzx	eax, byte ptr [ebp - 0x18]
   eaf3f:      	push	eax
   eaf40:      	call	0xeab75 <stage1>
   eaf45:      	mov	byte ptr [0xcfc40], 0x0
   eaf4c:      	mov	edx, dword ptr [ebp - 0x1c]
   eaf4f:      	mov	al, byte ptr [esi]
   eaf51:      	sub	eax, 0x2
   eaf54:      	cmp	al, 0x2
   eaf56:      	ja	0xeaf88 <stage1>
   eaf58:      	test	edx, edx
   eaf5a:      	lea	ecx, [ebp - 0x10]
   eaf5d:      	movzx	eax, byte ptr [esi + 0x1]
   eaf61:      	je	0xeaf78 <stage1>
   eaf63:      	cmp	byte ptr [edx], 0x0
   eaf66:      	je	0xeaf78 <stage1>
   eaf68:      	push	ecx
   eaf69:      	movzx	ecx, byte ptr [ebp - 0x18]
   eaf6d:      	push	ecx
   eaf6e:      	push	edx
   eaf6f:      	push	eax
   eaf70:      	push	ebx
   eaf71:      	call	0xeabf1 <stage1>
   eaf76:      	jmp	0xeaf88 <stage1>
   eaf78:      	movzx	edx, byte ptr [ebp - 0x18]
   eaf7c:      	push	ecx
   eaf7d:      	push	edx
   eaf7e:      	push	dword ptr [esi + 0x2]
   eaf81:      	push	eax
   eaf82:      	push	ebx
   eaf83:      	call	0xeaca8 <stage1>
   eaf88:      	cmp	byte ptr [esi], 0x1
   eaf8b:      	jne	0xeafaf <stage1>
   eaf8d:      	cmp	byte ptr [esi + 0x1], 0x4
   eaf91:      	lea	eax, [ebp - 0x10]
   eaf94:      	movzx	ebx, byte ptr [ebp - 0x18]
   eaf98:      	jne	0xeafa6 <stage1>
   eaf9a:      	push	eax
   eaf9b:      	push	ebx
   eaf9c:      	push	dword ptr [esi + 0x2]
   eaf9f:      	call	0xeaff9 <stage1>
   eafa4:      	jmp	0xeafaf <stage1>
   eafa6:      	push	eax
   eafa7:      	push	ebx
   eafa8:      	push	0x0
   eafaa:      	call	0xead5f <stage1>
   eafaf:      	cmp	byte ptr [esi], -0x1
   eafb2:      	jne	0xeafcb <stage1>
   eafb4:      	push	edi
   eafb5:      	push	0xfc4f9
   eafba:      	call	0xf5bc3 <stage1>
   eafbf:      	push	0xfa470
   eafc4:      	call	0xee760 <stage1>
   eafc9:      	pop	eax
   eafca:      	pop	edx
   eafcb:      	cmp	byte ptr [esi], 0x0
   eafce:      	jne	0xeafe2 <stage1>
   eafd0:      	push	edi
   eafd1:      	push	0xfc512
   eafd6:      	call	0xf5bc3 <stage1>
   eafdb:      	push	0x0
   eafdd:      	call	0xe9731 <stage1>
   eafe2:      	push	dword ptr [0xcfbc0]
   eafe8:      	call	0xe71cb <stage1>
   eafed:      	xor	eax, eax
   eafef:      	lea	esp, [ebp - 0xc]
   eaff2:      	pop	ebx
   eaff3:      	pop	esi
   eaff4:      	pop	edi
   eaff5:      	pop	ebp
   eaff6:      	ret	0xc

--- boot iterator wrapper: file [0xb034, 0xb05c), runtime [0xeb034, 0xeb05c) ---
000e0000 <stage1>:
   eb034:      	push	ebp
   eb035:      	mov	ebp, esp
   eb037:      	push	eax
   eb038:      	push	0xfc53f
   eb03d:      	call	0xf5bc3 <stage1>
   eb042:      	lea	eax, [ebp - 0x4]
   eb045:      	mov	dword ptr [ebp - 0x4], 0x0
   eb04c:      	push	eax
   eb04d:      	push	0xeae16
   eb052:      	push	0x4b
   eb054:      	call	0xed576 <stage1>
   eb059:      	pop	edx
   eb05a:      	leave
   eb05b:      	ret	0x4

--- command-line builder: file [0xbc60, 0xbcd9), runtime [0xebc60, 0xebcd9) ---
000e0000 <stage1>:
   ebc60:      	cmp	byte ptr [0xcfc40], 0x0
   ebc67:      	je	0xebc78 <stage1>
   ebc69:      	push	0xcfc40
   ebc6e:      	push	0xfc796
   ebc73:      	call	0xeb132 <stage1>
   ebc78:      	movzx	eax, word ptr [0xc0214]
   ebc7f:      	lea	ebx, [ebp - 0x109c]
   ebc85:      	push	eax
   ebc86:      	push	0xfc841
   ebc8b:      	push	0x50
   ebc8d:      	push	ebx
   ebc8e:      	call	0xf5bd4 <stage1>
   ebc93:      	push	ebx
   ebc94:      	push	0xfc79f
   ebc99:      	call	0xeb132 <stage1>
   ebc9e:      	movzx	eax, word ptr [0xc108e]
   ebca5:      	push	eax
   ebca6:      	movzx	eax, word ptr [0xc108c]
   ebcad:      	push	eax
   ebcae:      	movzx	eax, word ptr [0xc108a]
   ebcb5:      	push	eax
   ebcb6:      	movzx	eax, word ptr [0xc1088]
   ebcbd:      	push	eax
   ebcbe:      	push	0xfc7a8
   ebcc3:      	push	0x50
   ebcc5:      	push	ebx
   ebcc6:      	call	0xf5bd4 <stage1>
   ebccb:      	add	esp, 0x2c
   ebcce:      	push	ebx
   ebccf:      	push	0xfc7b4
   ebcd4:      	call	0xeb132 <stage1>

--- configuration iterator: file [0xd576, 0xd68b), runtime [0xed576, 0xed68b) ---
000e0000 <stage1>:
   ed576:      	push	ebp
   ed577:      	mov	ebp, esp
   ed579:      	push	edi
   ed57a:      	push	esi
   ed57b:      	push	ebx
   ed57c:      	sub	esp, 0xc
   ed57f:      	test	byte ptr [0xc03c0], 0x2
   ed586:      	jne	0xed5ce <stage1>
   ed588:      	call	0xed50e <stage1>
   ed58d:      	test	eax, eax
   ed58f:      	je	0xed5ae <stage1>
   ed591:      	push	eax
   ed592:      	call	0xeca3d <stage1>
   ed597:      	test	eax, eax
   ed599:      	je	0xed5ae <stage1>
   ed59b:      	mov	edx, dword ptr [eax + 0x10]
   ed59e:      	add	edx, eax
   ed5a0:      	mov	eax, dword ptr [eax + 0xc]
   ed5a3:      	mov	dword ptr [0xc03e0], edx
   ed5a9:      	mov	dword ptr [0xc03e4], eax
   ed5ae:      	mov	eax, 0xcdb98
   ed5b3:      	mov	dword ptr [0xc0400], 0xcc19c
   ed5bd:      	or	dword ptr [0xc03c0], 0x2
   ed5c4:      	sub	eax, 0xcc19c
   ed5c9:      	mov	dword ptr [0xc0404], eax
   ed5ce:      	mov	eax, dword ptr [ebp + 0x8]
   ed5d1:      	mov	edi, 0xc03c0
   ed5d6:      	shl	eax, 0x14
   ed5d9:      	xor	esi, esi
   ed5db:      	mov	dword ptr [ebp - 0x10], eax
   ed5de:      	or	eax, 0xffff
   ed5e3:      	xor	ebx, ebx
   ed5e5:      	mov	dword ptr [ebp - 0x18], eax
   ed5e8:      	cmp	esi, 0x7
   ed5eb:      	ja	0xed671 <stage1>
   ed5f1:      	test	ebx, ebx
   ed5f3:      	jne	0xed671 <stage1>
   ed5f5:      	mov	ebx, dword ptr [edi + 0x8]
   ed5f8:      	mov	eax, dword ptr [edi + 0xc]
   ed5fb:      	add	eax, ebx
   ed5fd:      	mov	dword ptr [ebp - 0x14], eax
   ed600:      	cmp	dword ptr [ebp - 0x14], ebx
   ed603:      	jbe	0xed651 <stage1>
   ed605:      	cmp	dword ptr [ebp - 0x10], 0x0
   ed609:      	je	0xed655 <stage1>
   ed60b:      	mov	edx, dword ptr [ebx]
   ed60d:      	cmp	dword ptr [ebp - 0x18], edx
   ed610:      	jb	0xed617 <stage1>
   ed612:      	cmp	dword ptr [ebp - 0x10], edx
   ed615:      	jbe	0xed62d <stage1>
   ed617:      	mov	eax, dword ptr [ebx]
   ed619:      	shr	eax, 0x2
   ed61c:      	and	eax, 0x3ff
   ed621:      	jne	0xed628 <stage1>
   ed623:      	mov	eax, 0x1
   ed628:      	lea	ebx, [ebx + 4*eax]
   ed62b:      	jmp	0xed600 <stage1>
   ed62d:      	and	edx, 0x3
   ed630:      	je	0xed655 <stage1>
   ed632:      	mov	eax, ebx
   ed634:      	lea	edx, [ebx + 4*edx]
   ed637:      	mov	cx, word ptr [0xc021e]
   ed63e:      	and	cx, word ptr [eax + 0x6]
   ed642:      	cmp	cx, word ptr [eax + 0x4]
   ed646:      	je	0xed655 <stage1>
   ed648:      	add	eax, 0x4
   ed64b:      	cmp	edx, eax
   ed64d:      	jne	0xed637 <stage1>
   ed64f:      	jmp	0xed617 <stage1>
   ed651:      	xor	ebx, ebx
   ed653:      	jmp	0xed668 <stage1>
   ed655:      	cmp	dword ptr [ebp + 0xc], 0x0
   ed659:      	je	0xed668 <stage1>
   ed65b:      	push	esi
   ed65c:      	push	dword ptr [ebp + 0x10]
   ed65f:      	push	ebx
   ed660:      	call	dword ptr [ebp + 0xc]
   ed663:      	cmp	eax, 0x0
   ed666:      	jle	0xed67c <stage1>
   ed668:      	inc	esi
   ed669:      	add	edi, 0x8
   ed66c:      	jmp	0xed5e8 <stage1>
   ed671:      	xor	eax, eax
   ed673:      	cmp	ebx, -0x1
   ed676:      	je	0xed683 <stage1>
   ed678:      	mov	eax, ebx
   ed67a:      	jmp	0xed683 <stage1>
   ed67c:      	je	0xed617 <stage1>
   ed67e:      	or	ebx, -0x1
   ed681:      	jmp	0xed668 <stage1>
   ed683:      	lea	esp, [ebp - 0xc]
   ed686:      	pop	ebx
   ed687:      	pop	esi
   ed688:      	pop	edi
   ed689:      	pop	ebp
   ed68a:      	ret	0xc
