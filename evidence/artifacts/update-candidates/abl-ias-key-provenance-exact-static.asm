# Exact ABL FIT/OEM-key-manifest provenance disassembly
# Exact ABL flash SHA-256: f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac
# IBBL size: 0x4000
# IBBL SHA-256: 394c442368c67f82f17e84854575bf07abafac2b8fbf2fda7dca68b182f91b93
# Decompressed IBB stage-1 size: 0x1fe00
# Decompressed IBB stage-1 SHA-256: 3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2
# Stage-1 load base: 0x000e0000
# Tool: Homebrew LLVM 23.1.3
# Raw instruction bytes intentionally omitted.

## IBBL FIT payload relocator (file [0x40,0xf3))

00000040:
      40: push    ebp
      41: mov     ebp, esp
      43: push    edi
      44: push    esi
      45: push    ebx
      46: sub     esp, 0x10
      49: mov     dword ptr [ebp - 0x18], edx
      4c: test    eax, eax
      4e: je      0xeb
      54: mov     edx, dword ptr [eax + 0x8]
      57: and     edx, 0xffffff
      5d: cmp     edx, 0x1
      60: jbe     0xeb
      66: lea     ecx, [edx + 0xfffffff]
      6c: mov     dword ptr [ebp - 0x10], 0x1
      73: shl     ecx, 0x4
      76: lea     esi, [eax + ecx]
      79: add     eax, 0x10
      7c: mov     dword ptr [ebp - 0x14], esi
      7f: mov     ebx, dword ptr [esi]
      81: lea     esi, [edx - 0x1]
      84: mov     dword ptr [ebp - 0x1c], esi
      87: mov     ecx, dword ptr [ebp - 0x1c]
      8a: cmp     dword ptr [ebp - 0x10], ecx
      8d: jae     0xe6
      8f: cmp     dword ptr [ebp - 0x18], 0x1
      93: jne     0x9d
      95: cmp     dword ptr [eax], 0xfffdffff
      9b: jbe     0xde
      9d: mov     dl, byte ptr [eax + 0xe]
      a0: and     edx, 0x7f
      a3: cmp     edx, 0x1
      a6: je      0xde
      a8: cmp     dword ptr [ebp - 0x18], 0x0
      ac: jne     0xc3
      ae: cmp     edx, 0x10
      b1: jne     0xc3
      b3: mov     dl, byte ptr [eax + 0xb]
      b6: lea     ecx, [edx - 0x5]
      b9: cmp     cl, 0x1
      bc: jbe     0xde
      be: cmp     dl, 0x8
      c1: je      0xde
      c3: mov     edx, dword ptr [eax + 0x8]
      c6: mov     esi, dword ptr [eax]
      c8: and     edx, 0xffffff
      ce: mov     edi, ebx
      d0: mov     ecx, edx
      d2: add     edx, 0xf
      d5: and     edx, -0x10
      d8: rep movsb byte ptr es:[edi], byte ptr [esi]
      da: mov     dword ptr [eax], ebx
      dc: add     ebx, edx
      de: inc     dword ptr [ebp - 0x10]
      e1: add     eax, 0x10
      e4: jmp     0x87
      e6: mov     eax, dword ptr [ebp - 0x14]
      e9: mov     dword ptr [eax], ebx
      eb: add     esp, 0x10
      ee: pop     ebx
      ef: pop     esi
      f0: pop     edi
      f1: pop     ebp
      f2: ret

## IBBL FIT validator and table copy (file [0xf3,0x171))

000000f3:
      f3: push    ebp
      f4: mov     ebp, esp
      f6: push    edi
      f7: push    esi
      f8: push    ebx
      f9: push    ecx
      fa: mov     ebx, eax
      fc: mov     esi, edx
      fe: cmp     dword ptr [edx + 0x4], 0x2020205f
     105: jne     0x120
     107: cmp     dword ptr [edx], 0x5449465f
     10d: jne     0x120
     10f: mov     edx, dword ptr [edx + 0x8]
     112: and     edx, 0xffffff
     118: lea     eax, [edx - 0x1]
     11b: cmp     eax, 0x14
     11e: jbe     0x12d
     120: mov     ecx, 0x4
     125: xor     eax, eax
     127: mov     edi, ebx
     129: rep stosd dword ptr es:[edi], eax
     12b: jmp     0x16b
     12d: mov     eax, edx
     12f: mov     edi, ebx
     131: shl     eax, 0x4
     134: mov     ecx, eax
     136: mov     dword ptr [ebp - 0x10], eax
     139: rep movsb byte ptr es:[edi], byte ptr [esi]
     13b: mov     eax, ecx
     13d: mov     ecx, 0x4
     142: mov     esi, edi
     144: rep stosd dword ptr es:[edi], eax
     146: mov     eax, dword ptr [ebp - 0x10]
     149: mov     byte ptr [esi + 0xe], 0x7f
     14d: lea     eax, [ebx + eax + 0x10]
     151: mov     dword ptr [esi], eax
     153: lea     eax, [edx + 0x1]
     156: mov     edx, dword ptr [ebx + 0x8]
     159: and     eax, 0xffffff
     15e: and     edx, 0xff000000
     164: or      eax, edx
     166: mov     dword ptr [ebx + 0x8], eax
     169: mov     eax, ebx
     16b: pop     edx
     16c: pop     ebx
     16d: pop     esi
     16e: pop     edi
     16f: pop     ebp
     170: ret

## IBBL source-FIT handoff copy (file [0x4ef,0x54c))

000004ef:
     4ef: push    ebp
     4f0: mov     edx, 0xfef80000
     4f5: mov     ebp, esp
     4f7: mov     eax, 0xc10c0
     4fc: push    edi
     4fd: call    0xf3
     502: mov     edx, 0x2
     507: mov     eax, 0xc10c0
     50c: call    0x40
     511: mov     edx, dword ptr [ebp + 0x10]
     514: mov     ecx, 0xfeffc199
     519: mov     eax, 0x2
     51e: call    0x1a5
     523: mov     edx, dword ptr [ebp + 0x8]
     526: mov     ecx, 0xfeffc19f
     52b: mov     eax, 0x1
     530: call    0x1a5
     535: mov     ecx, dword ptr [ebp + 0x18]
     538: sub     ecx, dword ptr [ebp + 0x14]
     53b: mov     edi, dword ptr [ebp + 0x14]
     53e: xor     eax, eax
     540: rep stosb byte ptr es:[edi], al
     542: call    0x92d
     547: pop     edi
     548: pop     ebp
     549: ret     0x14

## Stage-1 FIT type-0x0b key-manifest traversal
## Stage file [0x157dd,0x15944), runtime [0xf57dd,0xf5944)

000f57dd:
   f57dd: mov     eax, dword ptr [0xc10c8]
   f57e2: mov     ebx, dword ptr [0xc1060]
   f57e8: and     eax, 0xffffff
   f57ed: mov     byte ptr [ebp - 0x25a], 0x0
   f57f4: mov     dword ptr [ebp - 0x274], eax
   f57fa: mov     eax, dword ptr [0xc1064]
   f57ff: mov     dword ptr [ebp - 0x258], eax
   f5805: mov     eax, ecx
   f5807: shr     eax, 0x3
   f580a: and     ecx, 0x7
   f580d: mov     dword ptr [ebp - 0x270], eax
   f5813: mov     eax, 0x1
   f5818: shl     eax, cl
   f581a: mov     dword ptr [ebp - 0x278], eax
   f5820: mov     ecx, 0xc10c0
   f5825: mov     byte ptr [ebp - 0x259], 0x0
   f582c: mov     dword ptr [ebp - 0x268], 0x0
   f5836: mov     edi, dword ptr [ebp - 0x274]
   f583c: cmp     dword ptr [ebp - 0x268], edi
   f5842: jge     0xf5921
   f5848: mov     al, byte ptr [ecx + 0xe]
   f584b: and     eax, 0x7f
   f584e: cmp     al, 0xb
   f5850: je      0xf585d
   f5852: inc     dword ptr [ebp - 0x268]
   f5858: add     ecx, 0x10
   f585b: jmp     0xf5836
   f585d: mov     edi, dword ptr [ecx]
   f585f: xor     edx, edx
   f5861: mov     esi, 0x44
   f5866: mov     eax, dword ptr [edi + 0x288]
   f586c: mov     dword ptr [ebp - 0x26c], eax
   f5872: sub     eax, 0x24
   f5875: div     esi
   f5877: mov     dword ptr [ebp - 0x27c], eax
   f587d: test    ebx, ebx
   f587f: lea     eax, [edi + 0x2a8]
   f5885: jne     0xf58a7
   f5887: mov     esi, dword ptr [ebp - 0x26c]
   f588d: lea     ebx, [edi + 0x284]
   f5893: mov     dword ptr [ebp - 0x258], esi
   f5899: mov     byte ptr [ebp - 0x25a], 0x1
   f58a0: mov     byte ptr [ebp - 0x259], 0x1
   f58a7: xor     edx, edx
   f58a9: cmp     dword ptr [ebp - 0x27c], edx
   f58af: jle     0xf5852
   f58b1: mov     esi, dword ptr [ebp - 0x270]
   f58b7: movzx   esi, byte ptr [eax + esi]
   f58bb: test    dword ptr [ebp - 0x278], esi
   f58c1: je      0xf591b
   f58c3: cmp     byte ptr [ebp - 0x259], 0x0
   f58ca: je      0xf58d2
   f58cc: mov     dword ptr [0xc1060], ebx
   f58d2: cmp     byte ptr [ebp - 0x25a], 0x0
   f58d9: je      0xf58e7
   f58db: mov     esi, dword ptr [ebp - 0x258]
   f58e1: mov     dword ptr [0xc1064], esi
   f58e7: lea     edi, [ebp - 0x234]
   f58ed: lea     esi, [eax + 0x24]
   f58f0: mov     ecx, 0x8
   f58f5: rep movsd dword ptr es:[edi], dword ptr [esi]
   f591b: add     eax, 0x44
   f591e: inc     edx
   f591f: jmp     0xf58a9
   f5921: cmp     byte ptr [ebp - 0x259], 0x0
   f5928: je      0xf5930
   f592a: mov     dword ptr [0xc1060], ebx
   f5930: cmp     byte ptr [ebp - 0x25a], 0x0
   f5937: je      0xf5944
   f5939: mov     eax, dword ptr [ebp - 0x258]
   f593f: mov     dword ptr [0xc1064], eax

## Exact type-3 OS caller selector
## Stage file [0xc1e4,0xc1f3), runtime [0xec1e4,0xec1f3)

000ec1e4:
   ec1e4: push    0x27
   ec1e6: push    dword ptr [ebp + 0xc]
   ec1e9: push    esi
   ec1ea: call    0xf57a3
   ec1ef: test    eax, eax
   ec1f1: jne     0xec203

## ABL.oemkm command-line export
## Stage file [0xbea5,0xbf10), runtime [0xebea5,0xebf10)

000ebee2:
   ebee2: mov     eax, dword ptr [0xc1060]
   ebee7: add     esp, 0x14
   ebeea: test    eax, eax
   ebeec: je      0xebf10
   ebeee: push    eax
   ebeef: push    dword ptr [0xc1064]
   ebef5: push    0xfc85b
   ebefa: push    0x50
   ebefc: push    ebx
   ebefd: call    0xf5bd4
   ebf02: push    ebx
   ebf03: push    0xfc861
   ebf08: call    0xeb132
   ebf0d: add     esp, 0x14

# Stage strings:
# runtime 0xfc85b: "%x@%x"
# runtime 0xfc861: "ABL.oemkm"

## Exact CSE BUP provenance
# FTPR member: bup
# Flash offset: 0x145000
# Size: 0x33000
# SHA-256: cee77bc172a9df1c4088d5f716b9e55cda539a26656d07a92268c3cd5d4f0165
# Code base: 0x26000

### FIT buffer allocation (file [0xb370,0xb3bd), runtime [0x31370,0x313bd))

00031370:
   31370: push    0x1000
   31375: push    0x20000
   3137a: push    0x0
   3137c: call    0x6087
   31381: add     esp, 0x10
   31384: mov     dword ptr [0xa4aa0], eax
   31389: test    eax, eax
   3138b: jne     0x313a3
   3138d: or      byte ptr [0xa4c81], 0x40
   31394: mov     dword ptr [0xa4b54], 0x1
   3139e: jmp     0x31efd
   313a3: push    0x20000
   313a8: push    0x0
   313aa: push    eax
   313ab: call    0x103d
   313b0: push    0x2
   313b2: mov     ebx, dword ptr [0xa4aa0]
   313b8: call    0x27e30

### FIT header initialization (file [0x1409d,0x140cf), runtime [0x3a09d,0x3a0cf))

0003a09d:
   3a09d: push    ebp
   3a09e: mov     ebp, esp
   3a0a0: mov     eax, dword ptr [ebp + 0x8]
   3a0a3: mov     edx, dword ptr [eax + 0x8]
   3a0a6: mov     dword ptr [eax], 0x5449465f
   3a0ac: and     edx, 0xff000000
   3a0b2: mov     dword ptr [eax + 0x4], 0x2020205f
   3a0b9: or      edx, 0x1
   3a0bc: mov     word ptr [eax + 0xc], 0x100
   3a0c2: mov     dword ptr [eax + 0x8], edx
   3a0c5: mov     byte ptr [eax + 0xe], 0x0
   3a0c9: mov     byte ptr [eax + 0xb], 0x0
   3a0cd: pop     ebp
   3a0ce: ret

### Generic FIT entry append (file [0x91e9,0x924f), runtime [0x2f1e9,0x2f24f))

0002f1e9:
   2f1e9: push    ebp
   2f1ea: mov     ebp, esp
   2f1ec: push    ebx
   2f1ed: mov     ecx, dword ptr [ebp + 0x8]
   2f1f0: mov     edx, dword ptr [ebp + 0xc]
   2f1f3: mov     eax, dword ptr [ecx + 0x8]
   2f1f6: and     eax, 0xffffff
   2f1fb: shl     eax, 0x4
   2f1fe: add     eax, ecx
   2f200: mov     dword ptr [eax], edx
   2f202: mov     dword ptr [eax + 0x4], 0x0
   2f209: mov     edx, dword ptr [ebp + 0x14]
   2f20c: mov     ebx, dword ptr [eax + 0x8]
   2f20f: mov     word ptr [eax + 0xc], dx
   2f213: mov     dl, byte ptr [ebp + 0x18]
   2f216: and     edx, 0x7f
   2f219: and     ebx, 0xff000000
   2f21f: mov     byte ptr [eax + 0xe], dl
   2f222: mov     edx, dword ptr [ebp + 0x10]
   2f225: and     edx, 0xffffff
   2f22b: or      edx, ebx
   2f22d: mov     dword ptr [eax + 0x8], edx
   2f230: mov     edx, dword ptr [ebp + 0x1c]
   2f233: mov     byte ptr [eax + 0xb], dl
   2f236: mov     eax, dword ptr [ecx + 0x8]
   2f239: lea     edx, [eax + 0x1]
   2f23c: and     eax, 0xff000000
   2f241: and     edx, 0xffffff
   2f247: or      eax, edx
   2f249: mov     dword ptr [ecx + 0x8], eax
   2f24c: pop     ebx
   2f24d: pop     ebp
   2f24e: ret

### `oem_key_man` FIT type-0x0b publication
### file [0xb9bc,0xbaf4), runtime [0x319bc,0x31af4)

000319bc:
   319bc: push    0x55a60                 # "oem_key_man"
   319c1: call    0x28cac
   319c6: pop     ecx
   319c7: test    eax, eax
   319c9: jne     0x319e1
   319cb: or      byte ptr [0xa4c82], 0x10
   319d2: mov     dword ptr [0xa4b54], 0x24
   319dc: jmp     0x31efd
   319e1: mov     eax, dword ptr [eax + 0x18]
   319e4: mov     dword ptr [0xa4aa4], eax
   319e9: test    eax, eax
   319eb: je      0x319cb
   319ed: mov     eax, dword ptr [eax + 0x18]
   319f0: shl     eax, 0x2
   319f3: cmp     eax, 0x1000
   319f8: jbe     0x31a10
   319fa: or      byte ptr [0xa4c82], 0x20
   31a01: mov     dword ptr [0xa4b54], 0x25
   31a0b: jmp     0x31efd
   31a10: test    byte ptr [0xa4b38], 0x8
   31a17: je      0x31a1e
   31a19: call    0x5191a
   31a1e: test    byte ptr [0xa4b38], 0x4
   31a25: je      0x31a42
   31a27: push    0xc
   31a29: call    0x27e30
   31a2e: call    0x514dc
   31a33: pop     edx
   31a34: test    eax, eax
   31a36: je      0x31a42
   31a38: mov     dword ptr [0xa4b54], eax
   31a3d: jmp     0x31efd
   31a42: push    0xd
   31a44: mov     edi, 0x20000
   31a49: call    0x27e30
   31a4e: mov     edx, dword ptr [0xa4ad0]
   31a54: mov     eax, dword ptr [0xa4acc]
   31a59: sub     edi, edx
   31a5b: and     eax, 0x1ffffff
   31a60: add     edi, dword ptr [0xa4aa0]
   31a66: add     eax, dword ptr [0xa4ab8]
   31a6c: push    0x0
   31a6e: mov     dword ptr [ebp - 0x38], edi
   31a71: push    edx
   31a72: push    eax
   31a73: push    edx
   31a74: push    edi
   31a75: call    0x2c316
   31a7a: add     esp, 0x18
   31a7d: test    eax, eax
   31a7f: jne     0x314b0
   31a85: push    0x10
   31a87: call    0x27e30
   31a8c: mov     esi, dword ptr [0xa4aa0]
   31a92: push    esi
   31a93: call    0x3a09d               # initialize `_FIT_   ` header
   31a98: pop     ecx
   31a99: test    byte ptr [0xa4c79], 0x2
   31aa0: pop     edi
   31aa1: jne     0x31af4
   31aa3: cmp     byte ptr [0xa4c7b], 0x0
   31aaa: js      0x31b93
   31ab0: mov     edx, dword ptr [0xa4aa4]
   31ab6: mov     eax, dword ptr [edx + 0x18]
   31ab9: shl     eax, 0x2
   31abc: push    eax
   31abd: lea     eax, [ebx + 0x1000]
   31ac3: push    edx
   31ac4: push    0x1000
   31ac9: push    eax
   31aca: call    0x6055                # copy oem_key_man payload
   31acf: mov     eax, dword ptr [0xa4aa4]
   31ad4: push    0x0
   31ad6: push    0xb                   # FIT type 0x0b
   31ad8: push    0x0
   31ada: mov     eax, dword ptr [eax + 0x18]
   31add: shl     eax, 0x2
   31ae0: push    eax                   # object dword count -> bytes
   31ae1: push    0xfffe1000            # published FIT payload address
   31ae6: push    esi                   # FIT table
   31ae7: call    0x2f1e9               # append entry and increment count
   31aec: add     esp, 0x28
   31aef: jmp     0x31b93

### Key-manifest source-name coupling and Extension-14 resolver
### file [0x1f58e,0x1f871), runtime [0x4558e,0x45871)

0004558e:
   4558e: push    ebp
   4558f: mov     ebp, esp
   45591: push    edi
   45592: push    esi
   45593: push    ebx
   45594: sub     esp, 0x78
   45597: mov     dword ptr [ebp - 0x6c], 0x0
   4559e: mov     eax, dword ptr [0x100c]
   455a3: mov     dword ptr [ebp - 0x10], eax
   455a6: xor     eax, eax
   455a8: lea     eax, [ebp - 0x30]
   455ab: push    0x20
   455ad: mov     dword ptr [ebp - 0x68], 0x5422d  # "rot.key"
   455b4: push    0x0
   455b6: mov     dword ptr [ebp - 0x64], 0x54235  # "oem.key"
   455bd: push    eax
   455be: mov     dword ptr [ebp - 0x60], 0x5423d  # "rot_key_man"
   455c5: mov     dword ptr [ebp - 0x5c], 0x54249  # "oem_key_man"
   455cc: mov     dword ptr [ebp - 0x58], 0x0
   455d3: mov     dword ptr [ebp - 0x54], 0x0
   455da: call    0x103d
   455df: lea     eax, [ebp - 0x50]
   455e2: push    0x10
   455e4: push    0x0
   455e6: push    eax
   455e7: call    0x103d
   455ec: push    0x4000
   455f1: call    0x6078
   455f6: add     esp, 0x1c
   455f9: mov     dword ptr [ebp - 0x70], eax
   455fc: mov     eax, 0xfffffff4
   45601: cmp     dword ptr [ebp - 0x70], 0x0
   45605: je      0x45859
   4560b: lea     eax, [ebp - 0x30]
   4560e: mov     esi, dword ptr [ebp - 0x70]
   45611: mov     dword ptr [ebp - 0x7c], eax
   45614: mov     edi, eax
   45616: xor     ebx, ebx
   45618: cmp     dword ptr [ebp + 0x8], 0x0
   4561c: jne     0x45631
   4561e: lea     eax, [ebp - 0x6c]
   45621: push    eax
   45622: push    esi
   45623: push    dword ptr [ebp + 4*ebx - 0x60] # *_key_man names
   45627: call    0x453b4
   4562c: add     esp, 0xc
   4562f: jmp     0x45646
   45631: lea     ecx, [ebp - 0x6c]
   45634: mov     eax, dword ptr [ebp + 4*ebx - 0x68] # *.key names
   45638: push    ecx
   45639: mov     edx, 0x2
   4563e: mov     ecx, esi
   45640: call    0x4549a
   45645: pop     ecx
   45646: mov     eax, dword ptr [ebp - 0x6c]
   45649: test    eax, eax
   4564b: jne     0x4567f
   4564d: cmp     ebx, 0x1
   45650: je      0x4565c
   45652: mov     ebx, 0x63
   45657: jmp     0x4584e
   4565c: call    0x45239
   45661: test    al, al
   45663: je      0x45652
   45665: add     edi, 0x10
   45668: add     esi, 0x2000
   4566e: dec     ebx
   4566f: je      0x45678
   45671: mov     ebx, 0x1
   45676: jmp     0x45618
   45678: xor     eax, eax
   4567a: jmp     0x45705
   4567f: sub     eax, 0x284
   45684: push    0xe
   45686: push    eax
   45687: lea     eax, [esi + 0x284]
   4568d: push    eax
   4568e: call    0x60b9               # locate extension tag 0x0e
   45693: add     esp, 0xc
   45696: mov     dword ptr [ebp + 4*ebx - 0x58], eax
   4569a: test    eax, eax
   4569c: jne     0x456a8
   4569e: mov     ebx, 0x16
   456a3: jmp     0x4584e
   456a8: mov     ecx, dword ptr [eax + 0x4]
   456ab: lea     edx, [ecx - 0x24]
   456ae: cmp     edx, 0x2200
   456b4: ja      0x4569e
   456b6: test    ebx, ebx
   456b8: jne     0x456c0
   456ba: cmp     dword ptr [eax + 0x8], 0x1
   456be: jmp     0x456c4
   456c0: cmp     dword ptr [eax + 0x8], 0x2
   456c4: jne     0x4569e

# The remaining hash-bound resolver range merges non-overlapping usage bitmaps
# and materializes 0x34-byte hash records. It does not by itself establish byte
# identity between the object named `oem_key_man` and FTPR member `oem.key`.
