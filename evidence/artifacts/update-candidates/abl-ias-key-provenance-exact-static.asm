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

## IBBL descriptor-directed dword copy helper (file [0x118e,0x1199))
## SHA-256: fa4ff48022ec39639e171133f556be4f08e63ae6eb127b983b39db35f506755a

0000118e:
    118e: mov     edi, dword ptr [esi]
    1190: mov     ecx, dword ptr [esi + 0x4]
    1193: mov     esi, dword ptr [esi + 0x8]
    1196: rep movsd dword ptr es:[edi], dword ptr [esi]
    1198: ret

## IBBL CSE-SRAM-to-temporary-memory handoff setup (file [0x269a,0x275b))
## SHA-256: 9fb4c68a8041510cbd3fe188a7abc30f0f6be8aa2ef95bc5407af5d773b80fe4

0000269a:
    269a: mov     eax, 0xfef80006
    269f: mov     ecx, 0x200
    26a4: wrmsr
    26a6: mov     eax, 0xfffe0001
    26ab: mov     ecx, 0x202
    26b0: wrmsr
    26b2: mov     edx, 0x7f
    26b7: mov     eax, 0xfff80800
    26bc: mov     ecx, 0x201
    26c1: wrmsr
    26c3: mov     eax, 0xfffe0800
    26c8: mov     ecx, 0x203
    26cd: wrmsr
    26cf: mov     ecx, 0x2ff
    26d4: rdmsr
    26d6: or      eax, 0x800
    26db: wrmsr
    26dd: mov     eax, cr0
    26e0: and     eax, 0x9fffffff
    26e5: invd
    26e7: mov     cr0, eax
    26ea: mov     ecx, 0x2e0
    26ef: rdmsr
    26f1: or      eax, 0x1
    26f4: wrmsr
    26f6: xor     eax, eax
    26f8: mov     edi, 0xfef80000
    26fd: mov     ecx, 0x20000
    2702: rep stosd dword ptr es:[edi], eax
    2704: sfence
    2707: mov     ecx, 0x2e0
    270c: rdmsr
    270e: or      eax, 0x2
    2711: wrmsr
    2713: mov     al, 0x6
    2715: out     0x80, al
    2717: rdtsc
    2719: shrd    eax, edx, 0x4
    271d: movd    mm3, eax
    2720: mov     esp, 0xfeffbc00
    2725: rdtsc
    2727: shrd    eax, edx, 0x4
    272b: movd    mm4, eax
    272e: mov     esi, 0xffffe760
    2733: call    0x118e
    2738: rdtsc
    273a: shrd    eax, edx, 0x4
    273e: movd    mm5, eax
    2741: mov     esi, 0xfef80000
    2746: mov     ecx, 0x4800
    274b: rep lodsd eax, dword ptr [esi]
    274d: mov     ecx, 0x120
    2752: rdmsr
    2754: or      eax, 0x100
    2759: wrmsr

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

## Exact CSE RBE key-manifest materialization
# RBEP member: rbe
# Flash offset: 0x105000
# Size: 0x9000
# SHA-256: ec4c2ea54c2943f6f6ffed4b4157b7b03cbccf6ca2cc9b21ccc3dd62adc88cc1
# Code base: 0x40000
# Main thread entry: 0x407a3
# 0x47a80: "oem.key"
# 0x47a9a: "oem_key_man"
# At 0x43001 the caller sets EDX=0, ECX=0x47a9a, EAX=0x47a80 and
# passes output slot 0x604102c to 0x42e61. The materializer resolves the
# source CPD descriptor, creates the named destination at that exact length,
# transfers the exact source length, and rejects a destination whose manifest
# dword count at +0x18 multiplied by four differs from the source length.

### Main entry reaches key initialization (file [0x7a3,0x7d3), runtime [0x407a3,0x407d3))

   407a3: 55                           	push	ebp
   407a4: 89 e5                        	mov	ebp, esp
   407a6: 56                           	push	esi
   407a7: 53                           	push	ebx
   407a8: 56                           	push	esi
   407a9: 8b 5d 08                     	mov	ebx, dword ptr [ebp + 0x8]
   407ac: 8b 75 0c                     	mov	esi, dword ptr [ebp + 0xc]
   407af: e8 58 f8 ff ff               	call	0x4000c <.text+0xc>
   407b4: e8 14 fd ff ff               	call	0x404cd <.text+0x4cd>
   407b9: e8 8e fc ff ff               	call	0x4044c <.text+0x44c>
   407be: 85 c0                        	test	eax, eax
   407c0: 0f 85 6e 01 00 00            	jne	0x40934 <.text+0x934>
   407c6: e8 2a fd ff ff               	call	0x404f5 <.text+0x4f5>
   407cb: 85 c0                        	test	eax, eax
   407cd: 0f 85 61 01 00 00            	jne	0x40934 <.text+0x934>

### Fail-closed key-initialization caller (file [0x4f5,0x544), runtime [0x404f5,0x40544))

   404f5: 55                           	push	ebp
   404f6: 89 e5                        	mov	ebp, esp
   404f8: e8 24 fe ff ff               	call	0x40321 <.text+0x321>
   404fd: 85 c0                        	test	eax, eax
   404ff: 75 41                        	jne	0x40542 <.text+0x542>
   40501: e8 cd 2d 00 00               	call	0x432d3 <.text+0x32d3>
   40506: 85 c0                        	test	eax, eax
   40508: 75 38                        	jne	0x40542 <.text+0x542>
   4050a: e8 43 36 00 00               	call	0x43b52 <.text+0x3b52>
   4050f: 85 c0                        	test	eax, eax
   40511: 75 2f                        	jne	0x40542 <.text+0x542>
   40513: e8 5e 4c 00 00               	call	0x45176 <.text+0x5176>
   40518: e8 3f fb ff ff               	call	0x4005c <.text+0x5c>
   4051d: 85 c0                        	test	eax, eax
   4051f: 75 21                        	jne	0x40542 <.text+0x542>
   40521: e8 99 20 00 00               	call	0x425bf <.text+0x25bf>
   40526: 85 c0                        	test	eax, eax
   40528: 75 18                        	jne	0x40542 <.text+0x542>
   4052a: e8 16 2a 00 00               	call	0x42f45 <.text+0x2f45>
   4052f: 85 c0                        	test	eax, eax
   40531: 75 0f                        	jne	0x40542 <.text+0x542>
   40533: e8 da 28 00 00               	call	0x42e12 <.text+0x2e12>
   40538: 85 c0                        	test	eax, eax
   4053a: 75 06                        	jne	0x40542 <.text+0x542>
   4053c: 5d                           	pop	ebp
   4053d: e9 c7 1d 00 00               	jmp	0x42309 <.text+0x2309>
   40542: 5d                           	pop	ebp
   40543: c3                           	ret

### CPD member to Snowball object exact-length materializer (file [0x2e61,0x2f45), runtime [0x42e61,0x42f45))

   42e61: 55                           	push	ebp
   42e62: 89 e5                        	mov	ebp, esp
   42e64: 57                           	push	edi
   42e65: 56                           	push	esi
   42e66: 53                           	push	ebx
   42e67: 53                           	push	ebx
   42e68: 89 45 f0                     	mov	dword ptr [ebp - 0x10], eax
   42e6b: 83 7d 08 00                  	cmp	dword ptr [ebp + 0x8], 0x0
   42e6f: 0f 94 c3                     	sete	bl
   42e72: 89 df                        	mov	edi, ebx
   42e74: 83 fa 03                     	cmp	edx, 0x3
   42e77: 0f 97 c3                     	seta	bl
   42e7a: 09 df                        	or	edi, ebx
   42e7c: 85 c9                        	test	ecx, ecx
   42e7e: 89 f8                        	mov	eax, edi
   42e80: 0f 94 c3                     	sete	bl
   42e83: 08 d8                        	or	al, bl
   42e85: 0f 85 81 00 00 00            	jne	0x42f0c <.text+0x2f0c>
   42e8b: 83 7d f0 00                  	cmp	dword ptr [ebp - 0x10], 0x0
   42e8f: 74 7b                        	je	0x42f0c <.text+0x2f0c>
   42e91: 8b 45 f0                     	mov	eax, dword ptr [ebp - 0x10]
   42e94: 6a 01                        	push	0x1
   42e96: 89 ce                        	mov	esi, ecx
   42e98: 50                           	push	eax
   42e99: 89 d3                        	mov	ebx, edx
   42e9b: 52                           	push	edx
   42e9c: e8 4f f1 ff ff               	call	0x41ff0 <.text+0x1ff0>
   42ea1: 83 c4 0c                     	add	esp, 0xc
   42ea4: 89 c7                        	mov	edi, eax
   42ea6: 85 c0                        	test	eax, eax
   42ea8: 74 69                        	je	0x42f13 <.text+0x2f13>
   42eaa: 8b 40 10                     	mov	eax, dword ptr [eax + 0x10]
   42ead: 8d 90 7c fd ff ff            	lea	edx, [eax - 0x284]
   42eb3: 81 fa 7c 1d 00 00            	cmp	edx, 0x1d7c
   42eb9: 77 68                        	ja	0x42f23 <.text+0x2f23>
   42ebb: 6a 00                        	push	0x0
   42ebd: 50                           	push	eax
   42ebe: 6a 00                        	push	0x0
   42ec0: 56                           	push	esi
   42ec1: e8 c6 e6 ff ff               	call	0x4158c <.text+0x158c>
   42ec6: 83 c4 10                     	add	esp, 0x10
   42ec9: 89 c6                        	mov	esi, eax
   42ecb: 85 c0                        	test	eax, eax
   42ecd: 74 4b                        	je	0x42f1a <.text+0x2f1a>
   42ecf: 6b cb 18                     	imul	ecx, ebx, 0x18
   42ed2: ff 77 10                     	push	dword ptr [edi + 0x10]
   42ed5: 8b 47 0c                     	mov	eax, dword ptr [edi + 0xc]
   42ed8: 25 ff ff ff 01               	and	eax, 0x1ffffff
   42edd: 03 81 d4 7f 04 06            	add	eax, dword ptr [ecx + 0x6047fd4]
   42ee3: 50                           	push	eax
   42ee4: 56                           	push	esi
   42ee5: e8 67 15 00 00               	call	0x44451 <.text+0x4451>
   42eea: 83 c4 0c                     	add	esp, 0xc
   42eed: 89 c1                        	mov	ecx, eax
   42eef: 85 c0                        	test	eax, eax
   42ef1: 75 2c                        	jne	0x42f1f <.text+0x2f1f>
   42ef3: 8b 46 18                     	mov	eax, dword ptr [esi + 0x18]
   42ef6: 3d 00 08 00 00               	cmp	eax, 0x800
   42efb: 77 26                        	ja	0x42f23 <.text+0x2f23>
   42efd: c1 e0 02                     	shl	eax, 0x2
   42f00: 39 47 10                     	cmp	dword ptr [edi + 0x10], eax
   42f03: 75 1e                        	jne	0x42f23 <.text+0x2f23>
   42f05: 8b 45 08                     	mov	eax, dword ptr [ebp + 0x8]
   42f08: 89 30                        	mov	dword ptr [eax], esi
   42f0a: eb 13                        	jmp	0x42f1f <.text+0x2f1f>
   42f0c: b8 02 00 00 00               	mov	eax, 0x2
   42f11: eb 2a                        	jmp	0x42f3d <.text+0x2f3d>
   42f13: b9 03 00 00 00               	mov	ecx, 0x3
   42f18: eb 05                        	jmp	0x42f1f <.text+0x2f1f>
   42f1a: b9 05 00 00 00               	mov	ecx, 0x5
   42f1f: 89 c8                        	mov	eax, ecx
   42f21: eb 1a                        	jmp	0x42f3d <.text+0x2f3d>
   42f23: 53                           	push	ebx
   42f24: e8 96 f0 ff ff               	call	0x41fbf <.text+0x1fbf>
   42f29: 89 04 24                     	mov	dword ptr [esp], eax
   42f2c: 6a 03                        	push	0x3
   42f2e: 6a 02                        	push	0x2
   42f30: e8 99 ef ff ff               	call	0x41ece <.text+0x1ece>
   42f35: 83 c4 0c                     	add	esp, 0xc
   42f38: b8 0f 00 00 00               	mov	eax, 0xf
   42f3d: 8d 65 f4                     	lea	esp, [ebp - 0xc]
   42f40: 5b                           	pop	ebx
   42f41: 5e                           	pop	esi
   42f42: 5f                           	pop	edi
   42f43: 5d                           	pop	ebp
   42f44: c3                           	ret

### Key-manifest source/destination routing (file [0x2f45,0x3058), runtime [0x42f45,0x43058))

   42f45: 55                           	push	ebp
   42f46: 89 e5                        	mov	ebp, esp
   42f48: 80 3d 00 00 04 06 00         	cmp	byte ptr [0x6040000], 0x0
   42f4f: 74 31                        	je	0x42f82 <.text+0x2f82>
   42f51: c7 05 90 00 00 f4 43 02 80 02	mov	dword ptr [-0xbffff70], 0x2800243
   42f5b: 66 c7 05 80 00 00 f4 08 00   	mov	word ptr [-0xbffff80], 0x8
   42f64: c7 05 80 00 00 f4 0d 00 02 00	mov	dword ptr [-0xbffff80], 0x2000d
   42f6e: c7 05 80 00 00 f4 02 00 86 80	mov	dword ptr [-0xbffff80], 0x80860002
   42f78: c7 05 b0 00 00 f4 00 00 00 00	mov	dword ptr [-0xbffff50], 0x0
   42f82: 66 83 3d 44 82 04 06 13      	cmp	word ptr [0x6048244], 0x13
   42f8a: 76 09                        	jbe	0x42f95 <.text+0x2f95>
   42f8c: 66 c7 05 44 82 04 06 00 00   	mov	word ptr [0x6048244], 0x0
   42f95: 0f b7 05 44 82 04 06         	movzx	eax, word ptr [0x6048244]
   42f9c: b9 6c 7a 04 00               	mov	ecx, 0x47a6c
   42fa1: 68 28 10 04 06               	push	0x6041028
   42fa6: 8d 50 01                     	lea	edx, [eax + 0x1]
   42fa9: 66 c7 84 00 1c 82 04 06 0d 00	mov	word ptr [eax + eax + 0x604821c], 0xd
   42fb3: 66 89 15 44 82 04 06         	mov	word ptr [0x6048244], dx
   42fba: b8 78 7a 04 00               	mov	eax, 0x47a78
   42fbf: 31 d2                        	xor	edx, edx
   42fc1: e8 9b fe ff ff               	call	0x42e61 <.text+0x2e61>
   42fc6: 5a                           	pop	edx
   42fc7: 85 c0                        	test	eax, eax
   42fc9: 0f 85 87 00 00 00            	jne	0x43056 <.text+0x3056>
   42fcf: 6a 00                        	push	0x0
   42fd1: 68 80 7a 04 00               	push	0x47a80
   42fd6: 6a 00                        	push	0x0
   42fd8: e8 13 f0 ff ff               	call	0x41ff0 <.text+0x1ff0>
   42fdd: 83 c4 0c                     	add	esp, 0xc
   42fe0: 85 c0                        	test	eax, eax
   42fe2: 75 1d                        	jne	0x43001 <.text+0x3001>
   42fe4: b9 88 7a 04 00               	mov	ecx, 0x47a88
   42fe9: 31 d2                        	xor	edx, edx
   42feb: b8 91 7a 04 00               	mov	eax, 0x47a91
   42ff0: 68 c8 7f 04 06               	push	0x6047fc8
   42ff5: e8 67 fe ff ff               	call	0x42e61 <.text+0x2e61>
   42ffa: 59                           	pop	ecx
   42ffb: 85 c0                        	test	eax, eax
   42ffd: 75 57                        	jne	0x43056 <.text+0x3056>
   42fff: eb 1d                        	jmp	0x4301e <.text+0x301e>
   43001: 31 d2                        	xor	edx, edx
   43003: b9 9a 7a 04 00               	mov	ecx, 0x47a9a
   43008: b8 80 7a 04 00               	mov	eax, 0x47a80
   4300d: 68 2c 10 04 06               	push	0x604102c
   43012: e8 4a fe ff ff               	call	0x42e61 <.text+0x2e61>
   43017: 5a                           	pop	edx
   43018: 85 c0                        	test	eax, eax
   4301a: 74 c8                        	je	0x42fe4 <.text+0x2fe4>
   4301c: eb 38                        	jmp	0x43056 <.text+0x3056>
   4301e: b9 a6 7a 04 00               	mov	ecx, 0x47aa6
   43023: ba 03 00 00 00               	mov	edx, 0x3
   43028: b8 ae 7a 04 00               	mov	eax, 0x47aae
   4302d: 68 10 80 04 06               	push	0x6048010
   43032: e8 2a fe ff ff               	call	0x42e61 <.text+0x2e61>
   43037: 59                           	pop	ecx
   43038: 85 c0                        	test	eax, eax
   4303a: 75 1a                        	jne	0x43056 <.text+0x3056>
   4303c: ba 02 00 00 00               	mov	edx, 0x2
   43041: b9 b7 7a 04 00               	mov	ecx, 0x47ab7
   43046: b8 c3 7a 04 00               	mov	eax, 0x47ac3
   4304b: 68 f8 7f 04 06               	push	0x6047ff8
   43050: e8 0c fe ff ff               	call	0x42e61 <.text+0x2e61>
   43055: 5a                           	pop	edx
   43056: c9                           	leave
   43057: c3                           	ret

### Exact-length transfer wrapper (file [0x4451,0x449c), runtime [0x44451,0x4449c))

   44451: f6 05 08 e0 04 06 01         	test	byte ptr [0x604e008], 0x1
   44458: 74 3c                        	je	0x44496 <.text+0x4496>
   4445a: 55                           	push	ebp
   4445b: 89 e5                        	mov	ebp, esp
   4445d: ff 35 00 e0 04 06            	push	dword ptr [0x604e000]
   44463: 68 00 f0 04 06               	push	0x604f000
   44468: e8 ce 1c fc ff               	call	0x613b
   4446d: 5a                           	pop	edx
   4446e: 85 c0                        	test	eax, eax
   44470: 59                           	pop	ecx
   44471: 74 07                        	je	0x4447a <.text+0x447a>
   44473: b8 12 00 00 00               	mov	eax, 0x12
   44478: eb 1a                        	jmp	0x44494 <.text+0x4494>
   4447a: ff 75 10                     	push	dword ptr [ebp + 0x10]
   4447d: ff 75 0c                     	push	dword ptr [ebp + 0xc]
   44480: ff 75 08                     	push	dword ptr [ebp + 0x8]
   44483: 68 00 f0 04 06               	push	0x604f000
   44488: e8 a4 1c fc ff               	call	0x6131
   4448d: 83 c4 10                     	add	esp, 0x10
   44490: 85 c0                        	test	eax, eax
   44492: 75 df                        	jne	0x44473 <.text+0x4473>
   44494: c9                           	leave
   44495: c3                           	ret
   44496: b8 12 00 00 00               	mov	eax, 0x12
   4449b: c3                           	ret

## Exact CSE RBE UEP-to-OEM-key authentication
# Exact RBE SHA-256: ec4c2ea54c2943f6f6ffed4b4157b7b03cbccf6ca2cc9b21ccc3dd62adc88cc1
# ifp_uep object string: runtime 0x47ae0 / file 0x7ae0
# Field 0x20 descriptor at runtime 0x47f74: bit offset 0x160, bit length 0x100
# Field input base is UEP + 8, so bit offset 0x160 begins at UEP + 0x34.
# Extracted 256-bit field is written to global 0x6048038.
# 0x42b83 passes that global into 0x42768 before extension selector 6 validation.

### UEP CRC-16 validator (file [0x3814,0x386e), runtime [0x43814,0x4386e))

   43814: 55                           	push	ebp
   43815: 83 c8 ff                     	or	eax, -0x1
   43818: 89 e5                        	mov	ebp, esp
   4381a: 31 d2                        	xor	edx, edx
   4381c: 53                           	push	ebx
   4381d: 3b 55 0c                     	cmp	edx, dword ptr [ebp + 0xc]
   43820: 74 1a                        	je	0x4383c <.text+0x383c>
   43822: 8b 5d 08                     	mov	ebx, dword ptr [ebp + 0x8]
   43825: 0f b6 cc                     	movzx	ecx, ah
   43828: 0f b6 1c 13                  	movzx	ebx, byte ptr [ebx + edx]
   4382c: 31 d9                        	xor	ecx, ebx
   4382e: 42                           	inc	edx
   4382f: c1 e0 08                     	shl	eax, 0x8
   43832: 66 33 84 09 34 7b 04 00      	xor	ax, word ptr [ecx + ecx + 0x47b34]
   4383a: eb e1                        	jmp	0x4381d <.text+0x381d>
   4383c: 5b                           	pop	ebx
   4383d: 5d                           	pop	ebp
   4383e: c3                           	ret
   4383f: 55                           	push	ebp
   43840: 31 c0                        	xor	eax, eax
   43842: 89 e5                        	mov	ebp, esp
   43844: 53                           	push	ebx
   43845: 8b 5d 08                     	mov	ebx, dword ptr [ebp + 0x8]
   43848: 81 3b 24 55 45 50            	cmp	dword ptr [ebx], 0x50455524
   4384e: 75 19                        	jne	0x43869 <.text+0x3869>
   43850: 8b 45 0c                     	mov	eax, dword ptr [ebp + 0xc]
   43853: 83 e8 06                     	sub	eax, 0x6
   43856: 50                           	push	eax
   43857: 8d 43 06                     	lea	eax, [ebx + 0x6]
   4385a: 50                           	push	eax
   4385b: e8 b4 ff ff ff               	call	0x43814 <.text+0x3814>
   43860: 66 3b 43 04                  	cmp	ax, word ptr [ebx + 0x4]
   43864: 5a                           	pop	edx
   43865: 0f 94 c0                     	sete	al
   43868: 59                           	pop	ecx
   43869: 8b 5d fc                     	mov	ebx, dword ptr [ebp - 0x4]
   4386c: c9                           	leave
   4386d: c3                           	ret

### UEP primary/fallback loader (file [0x386e,0x39b9), runtime [0x4386e,0x439b9))

   4386e: 55                           	push	ebp
   4386f: 89 e5                        	mov	ebp, esp
   43871: 57                           	push	edi
   43872: 56                           	push	esi
   43873: 53                           	push	ebx
   43874: 8d 45 f3                     	lea	eax, [ebp - 0xd]
   43877: 53                           	push	ebx
   43878: 8b 75 08                     	mov	esi, dword ptr [ebp + 0x8]
   4387b: 50                           	push	eax
   4387c: c6 45 f3 00                  	mov	byte ptr [ebp - 0xd], 0x0
   43880: e8 07 0d 00 00               	call	0x4458c <.text+0x458c>
   43885: 5f                           	pop	edi
   43886: 89 c3                        	mov	ebx, eax
   43888: 85 c0                        	test	eax, eax
   4388a: 0f 85 0b 01 00 00            	jne	0x4399b <.text+0x399b>
   43890: 80 7d f3 00                  	cmp	byte ptr [ebp - 0xd], 0x0
   43894: 0f 84 9b 00 00 00            	je	0x43935 <.text+0x3935>
   4389a: 68 55 45 50 00               	push	0x504555
   4389f: e8 67 dc ff ff               	call	0x4150b <.text+0x150b>
   438a4: 59                           	pop	ecx
   438a5: 89 c7                        	mov	edi, eax
   438a7: 85 c0                        	test	eax, eax
   438a9: 75 15                        	jne	0x438c0 <.text+0x38c0>
   438ab: 6a 04                        	push	0x4
   438ad: 6a 01                        	push	0x1
   438af: 6a 00                        	push	0x0
   438b1: b3 1b                        	mov	bl, 0x1b
   438b3: e8 fe e5 ff ff               	call	0x41eb6 <.text+0x1eb6>
   438b8: 83 c4 0c                     	add	esp, 0xc
   438bb: e9 db 00 00 00               	jmp	0x4399b <.text+0x399b>
   438c0: 81 78 0c 00 20 00 00         	cmp	dword ptr [eax + 0xc], 0x2000
   438c7: 74 10                        	je	0x438d9 <.text+0x38d9>
   438c9: 6a 04                        	push	0x4
   438cb: 6a 02                        	push	0x2
   438cd: 6a 02                        	push	0x2
   438cf: e8 e2 e5 ff ff               	call	0x41eb6 <.text+0x1eb6>
   438d4: e9 87 00 00 00               	jmp	0x43960 <.text+0x3960>
   438d9: 68 08 01 00 00               	push	0x108
   438de: ff 70 08                     	push	dword ptr [eax + 0x8]
   438e1: 56                           	push	esi
   438e2: e8 b5 0b 00 00               	call	0x4449c <.text+0x449c>
   438e7: 83 c4 0c                     	add	esp, 0xc
   438ea: 85 c0                        	test	eax, eax
   438ec: 0f 85 a7 00 00 00            	jne	0x43999 <.text+0x3999>
   438f2: 68 08 01 00 00               	push	0x108
   438f7: 56                           	push	esi
   438f8: e8 42 ff ff ff               	call	0x4383f <.text+0x383f>
   438fd: 59                           	pop	ecx
   438fe: 84 c0                        	test	al, al
   43900: 5a                           	pop	edx
   43901: 0f 85 a8 00 00 00            	jne	0x439af <.text+0x39af>
   43907: 68 08 01 00 00               	push	0x108
   4390c: 8b 47 08                     	mov	eax, dword ptr [edi + 0x8]
   4390f: 05 00 10 00 00               	add	eax, 0x1000
   43914: 50                           	push	eax
   43915: 56                           	push	esi
   43916: e8 81 0b 00 00               	call	0x4449c <.text+0x449c>
   4391b: 83 c4 0c                     	add	esp, 0xc
   4391e: 85 c0                        	test	eax, eax
   43920: 75 77                        	jne	0x43999 <.text+0x3999>
   43922: 68 08 01 00 00               	push	0x108
   43927: 56                           	push	esi
   43928: e8 12 ff ff ff               	call	0x4383f <.text+0x383f>
   4392d: 5f                           	pop	edi
   4392e: 84 c0                        	test	al, al
   43930: 5a                           	pop	edx
   43931: 75 7c                        	jne	0x439af <.text+0x39af>
   43933: eb 94                        	jmp	0x438c9 <.text+0x38c9>
   43935: 6a 01                        	push	0x1
   43937: 6a 11                        	push	0x11
   43939: 6a 12                        	push	0x12
   4393b: 68 3c 10 04 06               	push	0x604103c
   43940: e8 a1 e5 ff ff               	call	0x41ee6 <.text+0x1ee6>
   43945: 83 c4 10                     	add	esp, 0x10
   43948: 85 c0                        	test	eax, eax
   4394a: 74 46                        	je	0x43992 <.text+0x3992>
   4394c: 81 78 08 08 01 00 00         	cmp	dword ptr [eax + 0x8], 0x108
   43953: 74 15                        	je	0x4396a <.text+0x396a>
   43955: 6a 11                        	push	0x11
   43957: 6a 02                        	push	0x2
   43959: 6a 02                        	push	0x2
   4395b: e8 6e e5 ff ff               	call	0x41ece <.text+0x1ece>
   43960: 83 c4 0c                     	add	esp, 0xc
   43963: bb 1b 00 00 00               	mov	ebx, 0x1b
   43968: eb 31                        	jmp	0x4399b <.text+0x399b>
   4396a: 68 08 01 00 00               	push	0x108
   4396f: ff 70 04                     	push	dword ptr [eax + 0x4]
   43972: 56                           	push	esi
   43973: e8 d9 0a 00 00               	call	0x44451 <.text+0x4451>
   43978: 83 c4 0c                     	add	esp, 0xc
   4397b: 85 c0                        	test	eax, eax
   4397d: 75 1a                        	jne	0x43999 <.text+0x3999>
   4397f: 68 08 01 00 00               	push	0x108
   43984: 56                           	push	esi
   43985: e8 b5 fe ff ff               	call	0x4383f <.text+0x383f>
   4398a: 5a                           	pop	edx
   4398b: 84 c0                        	test	al, al
   4398d: 59                           	pop	ecx
   4398e: 75 1f                        	jne	0x439af <.text+0x39af>
   43990: eb c3                        	jmp	0x43955 <.text+0x3955>
   43992: bb 03 00 00 00               	mov	ebx, 0x3
   43997: eb 02                        	jmp	0x4399b <.text+0x399b>
   43999: 89 c3                        	mov	ebx, eax
   4399b: 85 f6                        	test	esi, esi
   4399d: 74 10                        	je	0x439af <.text+0x39af>
   4399f: 68 08 01 00 00               	push	0x108
   439a4: 6a 00                        	push	0x0
   439a6: 56                           	push	esi
   439a7: e8 91 d6 fb ff               	call	0x103d
   439ac: 83 c4 0c                     	add	esp, 0xc
   439af: 8d 65 f4                     	lea	esp, [ebp - 0xc]
   439b2: 89 d8                        	mov	eax, ebx
   439b4: 5b                           	pop	ebx
   439b5: 5e                           	pop	esi
   439b6: 5f                           	pop	edi
   439b7: 5d                           	pop	ebp
   439b8: c3                           	ret

### ifp_uep materialization and OEM-hash extraction (file [0x39b9,0x3b52), runtime [0x439b9,0x43b52))

   439b9: 55                           	push	ebp
   439ba: 89 e5                        	mov	ebp, esp
   439bc: 57                           	push	edi
   439bd: 56                           	push	esi
   439be: 53                           	push	ebx
   439bf: 53                           	push	ebx
   439c0: 66 c7 45 f2 00 00            	mov	word ptr [ebp - 0xe], 0x0
   439c6: 6a 00                        	push	0x0
   439c8: c6 45 f0 00                  	mov	byte ptr [ebp - 0x10], 0x0
   439cc: 68 08 01 00 00               	push	0x108
   439d1: c6 45 f1 00                  	mov	byte ptr [ebp - 0xf], 0x0
   439d5: 6a 00                        	push	0x0
   439d7: 68 e0 7a 04 00               	push	0x47ae0
   439dc: e8 ab db ff ff               	call	0x4158c <.text+0x158c>
   439e1: bb 05 00 00 00               	mov	ebx, 0x5
   439e6: 83 c4 10                     	add	esp, 0x10
   439e9: 89 c7                        	mov	edi, eax
   439eb: a3 30 10 04 06               	mov	dword ptr [0x6041030], eax
   439f0: 85 c0                        	test	eax, eax
   439f2: 0f 84 50 01 00 00            	je	0x43b48 <.text+0x3b48>
   439f8: a1 10 08 17 f6               	mov	eax, dword ptr [0xf6170810]
   439fd: 8d 77 08                     	lea	esi, [edi + 0x8]
   43a00: c1 e8 18                     	shr	eax, 0x18
   43a03: 83 e0 0f                     	and	eax, 0xf
   43a06: 50                           	push	eax
   43a07: e8 cd e3 ff ff               	call	0x41dd9 <.text+0x1dd9>
   43a0c: 59                           	pop	ecx
   43a0d: a2 59 80 04 06               	mov	byte ptr [0x6048059], al
   43a12: fe c8                        	dec	al
   43a14: 75 20                        	jne	0x43a36 <.text+0x3a36>
   43a16: b8 00 08 17 f6               	mov	eax, 0xf6170800
   43a1b: 8b 10                        	mov	edx, dword ptr [eax]
   43a1d: 89 94 06 00 f8 e8 09         	mov	dword ptr [esi + eax + 0x9e8f800], edx
   43a24: 83 c0 04                     	add	eax, 0x4
   43a27: 3d 00 09 17 f6               	cmp	eax, 0xf6170900
   43a2c: 75 ed                        	jne	0x43a1b <.text+0x3a1b>
   43a2e: c7 07 52 45 41 4c            	mov	dword ptr [edi], 0x4c414552
   43a34: eb 11                        	jmp	0x43a47 <.text+0x3a47>
   43a36: 57                           	push	edi
   43a37: e8 32 fe ff ff               	call	0x4386e <.text+0x386e>
   43a3c: 5a                           	pop	edx
   43a3d: 89 c3                        	mov	ebx, eax
   43a3f: 85 c0                        	test	eax, eax
   43a41: 0f 85 01 01 00 00            	jne	0x43b48 <.text+0x3b48>
   43a47: 8d 45 f0                     	lea	eax, [ebp - 0x10]
   43a4a: 50                           	push	eax
   43a4b: 6a 01                        	push	0x1
   43a4d: 6a 16                        	push	0x16
   43a4f: 56                           	push	esi
   43a50: e8 f6 3c 00 00               	call	0x4774b <.text+0x774b>
   43a55: 83 c4 10                     	add	esp, 0x10
   43a58: 85 c0                        	test	eax, eax
   43a5a: 0f 85 dd 00 00 00            	jne	0x43b3d <.text+0x3b3d>
   43a60: 80 7d f0 00                  	cmp	byte ptr [ebp - 0x10], 0x0
   43a64: 75 19                        	jne	0x43a7f <.text+0x3a7f>
   43a66: 80 7d f1 00                  	cmp	byte ptr [ebp - 0xf], 0x0
   43a6a: 74 2e                        	je	0x43a9a <.text+0x3a9a>
   43a6c: 6a 04                        	push	0x4
   43a6e: 6a 02                        	push	0x2
   43a70: 6a 02                        	push	0x2
   43a72: e8 3f e4 ff ff               	call	0x41eb6 <.text+0x1eb6>
   43a77: 83 c4 0c                     	add	esp, 0xc
   43a7a: e9 c4 00 00 00               	jmp	0x43b43 <.text+0x3b43>
   43a7f: 8d 45 f1                     	lea	eax, [ebp - 0xf]
   43a82: 50                           	push	eax
   43a83: 6a 07                        	push	0x7
   43a85: 6a 15                        	push	0x15
   43a87: 56                           	push	esi
   43a88: e8 be 3c 00 00               	call	0x4774b <.text+0x774b>
   43a8d: 83 c4 10                     	add	esp, 0x10
   43a90: 85 c0                        	test	eax, eax
   43a92: 0f 85 a5 00 00 00            	jne	0x43b3d <.text+0x3b3d>
   43a98: eb cc                        	jmp	0x43a66 <.text+0x3a66>
   43a9a: 68 5a 80 04 06               	push	0x604805a
   43a9f: 6a 03                        	push	0x3
   43aa1: 56                           	push	esi
   43aa2: e8 5d e3 ff ff               	call	0x41e04 <.text+0x1e04>
   43aa7: 83 c4 0c                     	add	esp, 0xc
   43aaa: 89 c3                        	mov	ebx, eax
   43aac: 85 c0                        	test	eax, eax
   43aae: 0f 85 94 00 00 00            	jne	0x43b48 <.text+0x3b48>
   43ab4: 68 5b 80 04 06               	push	0x604805b
   43ab9: 6a 04                        	push	0x4
   43abb: 56                           	push	esi
   43abc: e8 43 e3 ff ff               	call	0x41e04 <.text+0x1e04>
   43ac1: 83 c4 0c                     	add	esp, 0xc
   43ac4: 89 c3                        	mov	ebx, eax
   43ac6: 85 c0                        	test	eax, eax
   43ac8: 75 7e                        	jne	0x43b48 <.text+0x3b48>
   43aca: 80 3d 5b 80 04 06 00         	cmp	byte ptr [0x604805b], 0x0
   43ad1: 75 0b                        	jne	0x43ade <.text+0x3ade>
   43ad3: 80 3d 59 80 04 06 00         	cmp	byte ptr [0x6048059], 0x0
   43ada: 74 3d                        	je	0x43b19 <.text+0x3b19>
   43adc: eb 6a                        	jmp	0x43b48 <.text+0x3b48>
   43ade: 8d 45 f2                     	lea	eax, [ebp - 0xe]
   43ae1: 50                           	push	eax
   43ae2: 6a 10                        	push	0x10
   43ae4: 6a 1f                        	push	0x1f
   43ae6: 56                           	push	esi
   43ae7: e8 5f 3c 00 00               	call	0x4774b <.text+0x774b>
   43aec: 83 c4 10                     	add	esp, 0x10
   43aef: 85 c0                        	test	eax, eax
   43af1: 75 50                        	jne	0x43b43 <.text+0x3b43>
   43af3: 8a 45 f2                     	mov	al, byte ptr [ebp - 0xe]
   43af6: 68 38 80 04 06               	push	0x6048038
   43afb: c0 e8 04                     	shr	al, 0x4
   43afe: 68 00 01 00 00               	push	0x100
   43b03: a2 58 80 04 06               	mov	byte ptr [0x6048058], al
   43b08: 6a 20                        	push	0x20
   43b0a: 56                           	push	esi
   43b0b: e8 3b 3c 00 00               	call	0x4774b <.text+0x774b>
   43b10: 83 c4 10                     	add	esp, 0x10
   43b13: 85 c0                        	test	eax, eax
   43b15: 75 2c                        	jne	0x43b43 <.text+0x3b43>
   43b17: eb ba                        	jmp	0x43ad3 <.text+0x3ad3>
   43b19: a1 1c 10 04 06               	mov	eax, dword ptr [0x604101c]
   43b1e: f6 00 01                     	test	byte ptr [eax], 0x1
   43b21: 74 25                        	je	0x43b48 <.text+0x3b48>
   43b23: 8b 40 04                     	mov	eax, dword ptr [eax + 0x4]
   43b26: 88 c2                        	mov	dl, al
   43b28: 83 e2 0a                     	and	edx, 0xa
   43b2b: 80 fa 0a                     	cmp	dl, 0xa
   43b2e: 75 18                        	jne	0x43b48 <.text+0x3b48>
   43b30: c1 e8 07                     	shr	eax, 0x7
   43b33: 83 e0 01                     	and	eax, 0x1
   43b36: a2 5a 80 04 06               	mov	byte ptr [0x604805a], al
   43b3b: eb 0b                        	jmp	0x43b48 <.text+0x3b48>
   43b3d: 31 db                        	xor	ebx, ebx
   43b3f: 85 c0                        	test	eax, eax
   43b41: 74 05                        	je	0x43b48 <.text+0x3b48>
   43b43: bb 1b 00 00 00               	mov	ebx, 0x1b
   43b48: 8d 65 f4                     	lea	esp, [ebp - 0xc]
   43b4b: 89 d8                        	mov	eax, ebx
   43b4d: 5b                           	pop	ebx
   43b4e: 5e                           	pop	esi
   43b4f: 5f                           	pop	edi
   43b50: 5d                           	pop	ebp
   43b51: c3                           	ret

### UEP-pinned oem.key validation caller (file [0x2b83,0x2c32), runtime [0x42b83,0x42c32))

   42b83: 55                           	push	ebp
   42b84: 89 e5                        	mov	ebp, esp
   42b86: 56                           	push	esi
   42b87: 53                           	push	ebx
   42b88: 83 ec 20                     	sub	esp, 0x20
   42b8b: 8d 75 d8                     	lea	esi, [ebp - 0x28]
   42b8e: 8b 1d 2c 10 04 06            	mov	ebx, dword ptr [0x604102c]
   42b94: 6a 20                        	push	0x20
   42b96: 6a 00                        	push	0x0
   42b98: 56                           	push	esi
   42b99: e8 9f e4 fb ff               	call	0x103d
   42b9e: 83 c4 0c                     	add	esp, 0xc
   42ba1: 31 c0                        	xor	eax, eax
   42ba3: f6 05 08 10 04 06 40         	test	byte ptr [0x6041008], 0x40
   42baa: 75 7f                        	jne	0x42c2b <.text+0x2c2b>
   42bac: 6a 20                        	push	0x20
   42bae: 56                           	push	esi
   42baf: 68 38 80 04 06               	push	0x6048038
   42bb4: e8 70 e4 fb ff               	call	0x1029
   42bb9: 83 c4 0c                     	add	esp, 0xc
   42bbc: 85 c0                        	test	eax, eax
   42bbe: 0f 95 c2                     	setne	dl
   42bc1: 85 db                        	test	ebx, ebx
   42bc3: 0f 95 c0                     	setne	al
   42bc6: 31 f6                        	xor	esi, esi
   42bc8: 38 c2                        	cmp	dl, al
   42bca: 75 41                        	jne	0x42c0d <.text+0x2c0d>
   42bcc: 85 db                        	test	ebx, ebx
   42bce: 74 59                        	je	0x42c29 <.text+0x2c29>
   42bd0: 6a 00                        	push	0x0
   42bd2: 6a 06                        	push	0x6
   42bd4: 68 38 80 04 06               	push	0x6048038
   42bd9: 53                           	push	ebx
   42bda: e8 89 fb ff ff               	call	0x42768 <.text+0x2768>
   42bdf: 83 c4 10                     	add	esp, 0x10
   42be2: 85 c0                        	test	eax, eax
   42be4: 75 45                        	jne	0x42c2b <.text+0x2c2b>
   42be6: ba 06 00 00 00               	mov	edx, 0x6
   42beb: 89 d8                        	mov	eax, ebx
   42bed: e8 e8 e6 ff ff               	call	0x412da <.text+0x12da>
   42bf2: 85 c0                        	test	eax, eax
   42bf4: 75 35                        	jne	0x42c2b <.text+0x2c2b>
   42bf6: 8a 83 96 02 00 00            	mov	al, byte ptr [ebx + 0x296]
   42bfc: 3a 05 58 80 04 06            	cmp	al, byte ptr [0x6048058]
   42c02: 75 04                        	jne	0x42c08 <.text+0x2c08>
   42c04: 84 c0                        	test	al, al
   42c06: 75 21                        	jne	0x42c29 <.text+0x2c29>
   42c08: be 02 00 00 00               	mov	esi, 0x2
   42c0d: 6a 00                        	push	0x0
   42c0f: e8 ab f3 ff ff               	call	0x41fbf <.text+0x1fbf>
   42c14: 89 04 24                     	mov	dword ptr [esp], eax
   42c17: 6a 04                        	push	0x4
   42c19: 56                           	push	esi
   42c1a: e8 af f2 ff ff               	call	0x41ece <.text+0x1ece>
   42c1f: 83 c4 0c                     	add	esp, 0xc
   42c22: b8 18 00 00 00               	mov	eax, 0x18
   42c27: eb 02                        	jmp	0x42c2b <.text+0x2c2b>
   42c29: 31 c0                        	xor	eax, eax
   42c2b: 8d 65 f8                     	lea	esp, [ebp - 0x8]
   42c2e: 5b                           	pop	ebx
   42c2f: 5e                           	pop	esi
   42c30: 5d                           	pop	ebp
   42c31: c3                           	ret

### MN2 carried-key hash comparison before RSA (file [0x2768,0x2a9f), runtime [0x42768,0x42a9f))

   42768: 55                           	push	ebp
   42769: 89 e5                        	mov	ebp, esp
   4276b: 57                           	push	edi
   4276c: 56                           	push	esi
   4276d: 53                           	push	ebx
   4276e: 81 ec 98 01 00 00            	sub	esp, 0x198
   42774: 83 7d 0c 00                  	cmp	dword ptr [ebp + 0xc], 0x0
   42778: 0f 94 c2                     	sete	dl
   4277b: 83 7d 14 03                  	cmp	dword ptr [ebp + 0x14], 0x3
   4277f: 0f 97 c0                     	seta	al
   42782: 8b 7d 08                     	mov	edi, dword ptr [ebp + 0x8]
   42785: 08 c2                        	or	dl, al
   42787: 0f 85 ba 02 00 00            	jne	0x42a47 <.text+0x2a47>
   4278d: 85 ff                        	test	edi, edi
   4278f: 0f 84 b2 02 00 00            	je	0x42a47 <.text+0x2a47>
   42795: 80 3d 00 00 04 06 00         	cmp	byte ptr [0x6040000], 0x0
   4279c: 74 41                        	je	0x427df <.text+0x27df>
   4279e: 8b 45 10                     	mov	eax, dword ptr [ebp + 0x10]
   427a1: c7 05 90 00 00 f4 43 02 80 02	mov	dword ptr [-0xbffff70], 0x2800243
   427ab: 66 c7 05 80 00 00 f4 10 00   	mov	word ptr [-0xbffff80], 0x10
   427b4: c7 05 80 00 00 f4 11 00 02 00	mov	dword ptr [-0xbffff80], 0x20011
   427be: c7 05 80 00 00 f4 02 00 86 80	mov	dword ptr [-0xbffff80], 0x80860002
   427c8: a3 80 00 00 f4               	mov	dword ptr [0xf4000080], eax
   427cd: 8b 45 14                     	mov	eax, dword ptr [ebp + 0x14]
   427d0: a3 80 00 00 f4               	mov	dword ptr [0xf4000080], eax
   427d5: c7 05 b0 00 00 f4 00 00 00 00	mov	dword ptr [-0xbffff50], 0x0
   427df: 66 83 3d 44 82 04 06 13      	cmp	word ptr [0x6048244], 0x13
   427e7: 76 09                        	jbe	0x427f2 <.text+0x27f2>
   427e9: 66 c7 05 44 82 04 06 00 00   	mov	word ptr [0x6048244], 0x0
   427f2: 0f b7 05 44 82 04 06         	movzx	eax, word ptr [0x6048244]
   427f9: 81 7f 1c 24 4d 4e 32         	cmp	dword ptr [edi + 0x1c], 0x324e4d24
   42800: 8d 50 01                     	lea	edx, [eax + 0x1]
   42803: 66 c7 84 00 1c 82 04 06 11 00	mov	word ptr [eax + eax + 0x604821c], 0x11
   4280d: 66 89 15 44 82 04 06         	mov	word ptr [0x6048244], dx
   42814: 0f 85 38 02 00 00            	jne	0x42a52 <.text+0x2a52>
   4281a: f6 45 10 01                  	test	byte ptr [ebp + 0x10], 0x1
   4281e: 74 0d                        	je	0x4282d <.text+0x282d>
   42820: 81 7f 10 86 80 00 00         	cmp	dword ptr [edi + 0x10], 0x8086
   42827: 0f 85 25 02 00 00            	jne	0x42a52 <.text+0x2a52>
   4282d: 83 3f 04                     	cmp	dword ptr [edi], 0x4
   42830: 0f 85 1c 02 00 00            	jne	0x42a52 <.text+0x2a52>
   42836: 81 7f 08 00 00 01 00         	cmp	dword ptr [edi + 0x8], 0x10000
   4283d: 0f 85 0f 02 00 00            	jne	0x42a52 <.text+0x2a52>
   42843: 81 7f 04 a1 00 00 00         	cmp	dword ptr [edi + 0x4], 0xa1
   4284a: 0f 85 02 02 00 00            	jne	0x42a52 <.text+0x2a52>
   42850: 8b 47 18                     	mov	eax, dword ptr [edi + 0x18]
   42853: 2d a1 00 00 00               	sub	eax, 0xa1
   42858: 3d 5f 07 00 00               	cmp	eax, 0x75f
   4285d: 0f 87 ef 01 00 00            	ja	0x42a52 <.text+0x2a52>
   42863: 83 7f 78 40                  	cmp	dword ptr [edi + 0x78], 0x40
   42867: 0f 85 e5 01 00 00            	jne	0x42a52 <.text+0x2a52>
   4286d: 83 7f 7c 01                  	cmp	dword ptr [edi + 0x7c], 0x1
   42871: 0f 85 db 01 00 00            	jne	0x42a52 <.text+0x2a52>
   42877: 8d 9d a4 fe ff ff            	lea	ebx, [ebp - 0x15c]
   4287d: 53                           	push	ebx
   4287e: e8 6e 37 00 00               	call	0x45ff1 <.text+0x5ff1>
   42883: 8d 87 80 00 00 00            	lea	eax, [edi + 0x80]
   42889: c7 04 24 05 00 00 00         	mov	dword ptr [esp], 0x5
   42890: 89 85 5c fe ff ff            	mov	dword ptr [ebp - 0x1a4], eax
   42896: 89 85 68 fe ff ff            	mov	dword ptr [ebp - 0x198], eax
   4289c: 8d 85 64 fe ff ff            	lea	eax, [ebp - 0x19c]
   428a2: 53                           	push	ebx
   428a3: c7 85 64 fe ff ff 04 01 00 00	mov	dword ptr [ebp - 0x19c], 0x104
   428ad: 6a 00                        	push	0x0
   428af: 50                           	push	eax
   428b0: e8 5c ee ff ff               	call	0x41711 <.text+0x1711>
   428b5: 83 c4 10                     	add	esp, 0x10
   428b8: 89 c6                        	mov	esi, eax
   428ba: 85 c0                        	test	eax, eax
   428bc: 0f 85 8c 01 00 00            	jne	0x42a4e <.text+0x2a4e>
   428c2: 8d 95 8c fe ff ff            	lea	edx, [ebp - 0x174]
   428c8: 8d b5 b4 fe ff ff            	lea	esi, [ebp - 0x14c]
   428ce: 6a 00                        	push	0x0
   428d0: 89 b5 90 fe ff ff            	mov	dword ptr [ebp - 0x170], esi
   428d6: 52                           	push	edx
   428d7: c7 85 8c fe ff ff 20 00 00 00	mov	dword ptr [ebp - 0x174], 0x20
   428e1: e8 b2 37 00 00               	call	0x46098 <.text+0x6098>
   428e6: 58                           	pop	eax
   428e7: 5a                           	pop	edx
   428e8: 6a 20                        	push	0x20
   428ea: ff 75 0c                     	push	dword ptr [ebp + 0xc]
   428ed: 56                           	push	esi
   428ee: e8 b3 e7 fb ff               	call	0x10a6
   428f3: 83 c4 0c                     	add	esp, 0xc
   428f6: 85 c0                        	test	eax, eax
   428f8: 0f 85 60 01 00 00            	jne	0x42a5e <.text+0x2a5e>
   428fe: 8b 85 5c fe ff ff            	mov	eax, dword ptr [ebp - 0x1a4]
   42904: 8b 57 04                     	mov	edx, dword ptr [edi + 0x4]
   42907: 89 85 98 fe ff ff            	mov	dword ptr [ebp - 0x168], eax
   4290d: 8d 87 80 01 00 00            	lea	eax, [edi + 0x180]
   42913: 89 85 a0 fe ff ff            	mov	dword ptr [ebp - 0x160], eax
   42919: 8b 47 18                     	mov	eax, dword ptr [edi + 0x18]
   4291c: 29 d0                        	sub	eax, edx
   4291e: 8d 8f 84 01 00 00            	lea	ecx, [edi + 0x184]
   42924: c1 e0 02                     	shl	eax, 0x2
   42927: 89 8d 70 fe ff ff            	mov	dword ptr [ebp - 0x190], ecx
   4292d: 89 85 84 fe ff ff            	mov	dword ptr [ebp - 0x17c], eax
   42933: 8d 04 97                     	lea	eax, [edi + 4*edx]
   42936: 89 85 88 fe ff ff            	mov	dword ptr [ebp - 0x178], eax
   4293c: 8d 85 f4 fe ff ff            	lea	eax, [ebp - 0x10c]
   42942: 89 85 78 fe ff ff            	mov	dword ptr [ebp - 0x188], eax
   42948: 8d 85 94 fe ff ff            	lea	eax, [ebp - 0x16c]
   4294e: 50                           	push	eax
   4294f: 8d 85 74 fe ff ff            	lea	eax, [ebp - 0x18c]
   42955: 50                           	push	eax
   42956: 8d 85 6c fe ff ff            	lea	eax, [ebp - 0x194]
   4295c: 50                           	push	eax
   4295d: c7 85 94 fe ff ff 00 01 00 00	mov	dword ptr [ebp - 0x16c], 0x100
   42967: c7 85 9c fe ff ff 04 00 00 00	mov	dword ptr [ebp - 0x164], 0x4
   42971: c7 85 7c fe ff ff 80 00 00 00	mov	dword ptr [ebp - 0x184], 0x80
   4297b: 89 bd 80 fe ff ff            	mov	dword ptr [ebp - 0x180], edi
   42981: c7 85 6c fe ff ff 00 01 00 00	mov	dword ptr [ebp - 0x194], 0x100
   4298b: c7 85 74 fe ff ff 00 01 00 00	mov	dword ptr [ebp - 0x18c], 0x100
   42995: e8 de 36 fc ff               	call	0x6078
   4299a: 83 c4 0c                     	add	esp, 0xc
   4299d: 53                           	push	ebx
   4299e: e8 4e 36 00 00               	call	0x45ff1 <.text+0x5ff1>
   429a3: 8d 85 7c fe ff ff            	lea	eax, [ebp - 0x184]
   429a9: c7 04 24 01 00 00 00         	mov	dword ptr [esp], 0x1
   429b0: 53                           	push	ebx
   429b1: 6a 00                        	push	0x0
   429b3: 50                           	push	eax
   429b4: e8 58 ed ff ff               	call	0x41711 <.text+0x1711>
   429b9: 83 c4 10                     	add	esp, 0x10
   429bc: 89 c6                        	mov	esi, eax
   429be: 85 c0                        	test	eax, eax
   429c0: 0f 85 88 00 00 00            	jne	0x42a4e <.text+0x2a4e>
   429c6: 8d 85 84 fe ff ff            	lea	eax, [ebp - 0x17c]
   429cc: 6a 04                        	push	0x4
   429ce: 53                           	push	ebx
   429cf: 6a 00                        	push	0x0
   429d1: 50                           	push	eax
   429d2: e8 3a ed ff ff               	call	0x41711 <.text+0x1711>
   429d7: 83 c4 10                     	add	esp, 0x10
   429da: 89 c6                        	mov	esi, eax
   429dc: 85 c0                        	test	eax, eax
   429de: 75 6e                        	jne	0x42a4e <.text+0x2a4e>
   429e0: 8d bd d4 fe ff ff            	lea	edi, [ebp - 0x12c]
   429e6: 8d 85 8c fe ff ff            	lea	eax, [ebp - 0x174]
   429ec: 6a 01                        	push	0x1
   429ee: 89 bd 90 fe ff ff            	mov	dword ptr [ebp - 0x170], edi
   429f4: 50                           	push	eax
   429f5: c7 85 8c fe ff ff 20 00 00 00	mov	dword ptr [ebp - 0x174], 0x20
   429ff: e8 94 36 00 00               	call	0x46098 <.text+0x6098>
   42a04: 58                           	pop	eax
   42a05: 8d 85 60 fe ff ff            	lea	eax, [ebp - 0x1a0]
   42a0b: 5a                           	pop	edx
   42a0c: 50                           	push	eax
   42a0d: 6a 04                        	push	0x4
   42a0f: e8 f0 e7 fb ff               	call	0x1204
   42a14: 59                           	pop	ecx
   42a15: 5b                           	pop	ebx
   42a16: 89 c3                        	mov	ebx, eax
   42a18: 8d 85 f4 fe ff ff            	lea	eax, [ebp - 0x10c]
   42a1e: 6a 20                        	push	0x20
   42a20: 50                           	push	eax
   42a21: 57                           	push	edi
   42a22: e8 7f e6 fb ff               	call	0x10a6
   42a27: 83 c4 0c                     	add	esp, 0xc
   42a2a: 89 c7                        	mov	edi, eax
   42a2c: 8d 85 14 ff ff ff            	lea	eax, [ebp - 0xec]
   42a32: 68 e0 00 00 00               	push	0xe0
   42a37: 53                           	push	ebx
   42a38: 50                           	push	eax
   42a39: e8 68 e6 fb ff               	call	0x10a6
   42a3e: 83 c4 0c                     	add	esp, 0xc
   42a41: 09 f8                        	or	eax, edi
   42a43: 75 25                        	jne	0x42a6a <.text+0x2a6a>
   42a45: eb 07                        	jmp	0x42a4e <.text+0x2a4e>
   42a47: b8 02 00 00 00               	mov	eax, 0x2
   42a4c: eb 49                        	jmp	0x42a97 <.text+0x2a97>
   42a4e: 89 f0                        	mov	eax, esi
   42a50: eb 45                        	jmp	0x42a97 <.text+0x2a97>
   42a52: bf 02 00 00 00               	mov	edi, 0x2
   42a57: bb 0c 00 00 00               	mov	ebx, 0xc
   42a5c: eb 16                        	jmp	0x42a74 <.text+0x2a74>
   42a5e: bf 04 00 00 00               	mov	edi, 0x4
   42a63: bb 0e 00 00 00               	mov	ebx, 0xe
   42a68: eb 0a                        	jmp	0x42a74 <.text+0x2a74>
   42a6a: bf 04 00 00 00               	mov	edi, 0x4
   42a6f: bb 0d 00 00 00               	mov	ebx, 0xd
   42a74: ff 75 14                     	push	dword ptr [ebp + 0x14]
   42a77: e8 43 f5 ff ff               	call	0x41fbf <.text+0x1fbf>
   42a7c: 8b 75 10                     	mov	esi, dword ptr [ebp + 0x10]
   42a7f: c1 e6 1d                     	shl	esi, 0x1d
   42a82: 89 04 24                     	mov	dword ptr [esp], eax
   42a85: c1 fe 1f                     	sar	esi, 0x1f
   42a88: 83 c6 05                     	add	esi, 0x5
   42a8b: 56                           	push	esi
   42a8c: 57                           	push	edi
   42a8d: e8 3c f4 ff ff               	call	0x41ece <.text+0x1ece>
   42a92: 83 c4 0c                     	add	esp, 0xc
   42a95: 89 d8                        	mov	eax, ebx
   42a97: 8d 65 f4                     	lea	esp, [ebp - 0xc]
   42a9a: 5b                           	pop	ebx
   42a9b: 5e                           	pop	esi
   42a9c: 5f                           	pop	edi
   42a9d: 5d                           	pop	ebp
   42a9e: c3                           	ret

### UEP bitfield extractor (file [0x774b,0x78f4), runtime [0x4774b,0x478f4))

   4774b: 55                           	push	ebp
   4774c: 89 e5                        	mov	ebp, esp
   4774e: 57                           	push	edi
   4774f: 56                           	push	esi
   47750: 53                           	push	ebx
   47751: 83 ec 7c                     	sub	esp, 0x7c
   47754: 8b 5d 0c                     	mov	ebx, dword ptr [ebp + 0xc]
   47757: 8b 55 10                     	mov	edx, dword ptr [ebp + 0x10]
   4775a: 66 89 55 84                  	mov	word ptr [ebp - 0x7c], dx
   4775e: 83 fb 24                     	cmp	ebx, 0x24
   47761: 77 05                        	ja	0x47768 <.text+0x7768>
   47763: 66 85 d2                     	test	dx, dx
   47766: 75 0a                        	jne	0x47772 <.text+0x7772>
   47768: bb 16 00 00 00               	mov	ebx, 0x16
   4776d: e9 78 01 00 00               	jmp	0x478ea <.text+0x78ea>
   47772: 66 3b 14 9d f6 7e 04 00      	cmp	dx, word ptr [4*ebx + 0x47ef6]
   4777a: 75 ec                        	jne	0x47768 <.text+0x7768>
   4777c: 8d 43 fd                     	lea	eax, [ebx - 0x3]
   4777f: 83 f8 0e                     	cmp	eax, 0xe
   47782: 77 63                        	ja	0x477e7 <.text+0x77e7>
   47784: 0f b7 1c 9d f4 7e 04 00      	movzx	ebx, word ptr [4*ebx + 0x47ef4]
   4778c: 8d 43 02                     	lea	eax, [ebx + 0x2]
   4778f: 0f b7 c0                     	movzx	eax, ax
   47792: 50                           	push	eax
   47793: ff 75 08                     	push	dword ptr [ebp + 0x8]
   47796: e8 82 ff ff ff               	call	0x4771d <.text+0x771d>
   4779b: 5e                           	pop	esi
   4779c: 85 c0                        	test	eax, eax
   4779e: 5f                           	pop	edi
   4779f: 89 c6                        	mov	esi, eax
   477a1: 74 07                        	je	0x477aa <.text+0x77aa>
   477a3: 3d c2 01 00 00               	cmp	eax, 0x1c2
   477a8: 75 be                        	jne	0x47768 <.text+0x7768>
   477aa: 8d 45 94                     	lea	eax, [ebp - 0x6c]
   477ad: 50                           	push	eax
   477ae: 6a 02                        	push	0x2
   477b0: 53                           	push	ebx
   477b1: ff 75 08                     	push	dword ptr [ebp + 0x8]
   477b4: e8 da fe ff ff               	call	0x47693 <.text+0x7693>
   477b9: 83 c4 10                     	add	esp, 0x10
   477bc: 89 c3                        	mov	ebx, eax
   477be: 85 c0                        	test	eax, eax
   477c0: 0f 85 24 01 00 00            	jne	0x478ea <.text+0x78ea>
   477c6: 8a 45 94                     	mov	al, byte ptr [ebp - 0x6c]
   477c9: 8b 7d 14                     	mov	edi, dword ptr [ebp + 0x14]
   477cc: 83 e0 03                     	and	eax, 0x3
   477cf: 81 fe c2 01 00 00            	cmp	esi, 0x1c2
   477d5: 88 07                        	mov	byte ptr [edi], al
   477d7: 0f 85 0d 01 00 00            	jne	0x478ea <.text+0x78ea>
   477dd: bb c2 01 00 00               	mov	ebx, 0x1c2
   477e2: e9 03 01 00 00               	jmp	0x478ea <.text+0x78ea>
   477e7: 8d 7d 94                     	lea	edi, [ebp - 0x6c]
   477ea: 6a 60                        	push	0x60
   477ec: 6a 00                        	push	0x0
   477ee: 57                           	push	edi
   477ef: 89 55 8c                     	mov	dword ptr [ebp - 0x74], edx
   477f2: e8 46 98 fb ff               	call	0x103d
   477f7: 83 c4 0c                     	add	esp, 0xc
   477fa: 8b 34 9d f4 7e 04 00         	mov	esi, dword ptr [4*ebx + 0x47ef4]
   47801: 8d 45 93                     	lea	eax, [ebp - 0x6d]
   47804: c6 45 93 ff                  	mov	byte ptr [ebp - 0x6d], -0x1
   47808: 50                           	push	eax
   47809: 0f b7 c6                     	movzx	eax, si
   4780c: 50                           	push	eax
   4780d: e8 d1 fd ff ff               	call	0x475e3 <.text+0x75e3>
   47812: 5a                           	pop	edx
   47813: 89 c3                        	mov	ebx, eax
   47815: 59                           	pop	ecx
   47816: 85 c0                        	test	eax, eax
   47818: 8b 55 8c                     	mov	edx, dword ptr [ebp - 0x74]
   4781b: 0f 85 c9 00 00 00            	jne	0x478ea <.text+0x78ea>
   47821: 0f b7 c2                     	movzx	eax, dx
   47824: 89 45 88                     	mov	dword ptr [ebp - 0x78], eax
   47827: 48                           	dec	eax
   47828: b9 20 00 00 00               	mov	ecx, 0x20
   4782d: 83 e6 1f                     	and	esi, 0x1f
   47830: 99                           	cdq
   47831: f7 f9                        	idiv	ecx
   47833: 40                           	inc	eax
   47834: 89 7d 8c                     	mov	dword ptr [ebp - 0x74], edi
   47837: 88 45 87                     	mov	byte ptr [ebp - 0x79], al
   4783a: 31 ff                        	xor	edi, edi
   4783c: 66 89 b5 7e ff ff ff         	mov	word ptr [ebp - 0x82], si
   47843: 89 fa                        	mov	edx, edi
   47845: 3a 55 87                     	cmp	dl, byte ptr [ebp - 0x79]
   47848: 0f 83 81 00 00 00            	jae	0x478cf <.text+0x78cf>
   4784e: 89 f8                        	mov	eax, edi
   47850: 8b 4d 84                     	mov	ecx, dword ptr [ebp - 0x7c]
   47853: c1 e0 05                     	shl	eax, 0x5
   47856: 29 c1                        	sub	ecx, eax
   47858: b0 20                        	mov	al, 0x20
   4785a: 66 83 f9 1f                  	cmp	cx, 0x1f
   4785e: 77 08                        	ja	0x47868 <.text+0x7868>
   47860: c1 e2 05                     	shl	edx, 0x5
   47863: 8a 45 84                     	mov	al, byte ptr [ebp - 0x7c]
   47866: 29 d0                        	sub	eax, edx
   47868: 0f b6 c0                     	movzx	eax, al
   4786b: 8b 55 8c                     	mov	edx, dword ptr [ebp - 0x74]
   4786e: 31 f6                        	xor	esi, esi
   47870: 89 45 80                     	mov	dword ptr [ebp - 0x80], eax
   47873: 0f b6 45 93                  	movzx	eax, byte ptr [ebp - 0x6d]
   47877: 6b c0 0e                     	imul	eax, eax, 0xe
   4787a: 52                           	push	edx
   4787b: 89 95 78 ff ff ff            	mov	dword ptr [ebp - 0x88], edx
   47881: 8d 0c b0                     	lea	ecx, [eax + 4*esi]
   47884: 66 8b 85 7e ff ff ff         	mov	ax, word ptr [ebp - 0x82]
   4788b: ff 75 80                     	push	dword ptr [ebp - 0x80]
   4788e: 66 03 81 06 7e 04 00         	add	ax, word ptr [ecx + 0x47e06]
   47895: 0f b7 c0                     	movzx	eax, ax
   47898: 50                           	push	eax
   47899: 0f b6 81 04 7e 04 00         	movzx	eax, byte ptr [ecx + 0x47e04]
   478a0: c1 e0 07                     	shl	eax, 0x7
   478a3: 03 45 08                     	add	eax, dword ptr [ebp + 0x8]
   478a6: 50                           	push	eax
   478a7: e8 e7 fd ff ff               	call	0x47693 <.text+0x7693>
   478ac: 83 c4 10                     	add	esp, 0x10
   478af: 85 c0                        	test	eax, eax
   478b1: 75 35                        	jne	0x478e8 <.text+0x78e8>
   478b3: 46                           	inc	esi
   478b4: 8b 95 78 ff ff ff            	mov	edx, dword ptr [ebp - 0x88]
   478ba: 83 c2 20                     	add	edx, 0x20
   478bd: 83 fe 03                     	cmp	esi, 0x3
   478c0: 75 b1                        	jne	0x47873 <.text+0x7873>
   478c2: fe 45 93                     	inc	byte ptr [ebp - 0x6d]
   478c5: 47                           	inc	edi
   478c6: 83 45 8c 04                  	add	dword ptr [ebp - 0x74], 0x4
   478ca: e9 74 ff ff ff               	jmp	0x47843 <.text+0x7843>
   478cf: 3a 55 87                     	cmp	dl, byte ptr [ebp - 0x79]
   478d2: 75 16                        	jne	0x478ea <.text+0x78ea>
   478d4: ff 75 14                     	push	dword ptr [ebp + 0x14]
   478d7: ff 75 88                     	push	dword ptr [ebp - 0x78]
   478da: 8d 45 94                     	lea	eax, [ebp - 0x6c]
   478dd: 50                           	push	eax
   478de: e8 3d fd ff ff               	call	0x47620 <.text+0x7620>
   478e3: 83 c4 0c                     	add	esp, 0xc
   478e6: eb 02                        	jmp	0x478ea <.text+0x78ea>
   478e8: 89 c3                        	mov	ebx, eax
   478ea: 8d 65 f4                     	lea	esp, [ebp - 0xc]
   478ed: 89 d8                        	mov	eax, ebx
   478ef: 5b                           	pop	ebx
   478f0: 5e                           	pop	esi
   478f1: 5f                           	pop	edi
   478f2: 5d                           	pop	ebp
   478f3: c3                           	ret
### UEP hardware-window mode decoder (file [0x1dd9,0x1e04), runtime [0x41dd9,0x41e04))

   41dd9: 55                           	push	ebp
   41dda: 89 e5                        	mov	ebp, esp
   41ddc: 53                           	push	ebx
   41ddd: 8b 45 08                     	mov	eax, dword ptr [ebp + 0x8]
   41de0: 88 c1                        	mov	cl, al
   41de2: 88 c3                        	mov	bl, al
   41de4: 88 c2                        	mov	dl, al
   41de6: 83 e3 01                     	and	ebx, 0x1
   41de9: c0 e8 02                     	shr	al, 0x2
   41dec: c0 e9 03                     	shr	cl, 0x3
   41def: d0 ea                        	shr	dl
   41df1: 09 c1                        	or	ecx, eax
   41df3: 83 e2 01                     	and	edx, 0x1
   41df6: 31 c0                        	xor	eax, eax
   41df8: 80 e1 01                     	and	cl, 0x1
   41dfb: 74 04                        	je	0x41e01 <.text+0x1e01>
   41dfd: 88 d0                        	mov	al, dl
   41dff: 09 d8                        	or	eax, ebx
   41e01: 5b                           	pop	ebx
   41e02: 5d                           	pop	ebp
   41e03: c3                           	ret

# Input is (dword[0xf6170810] >> 24) & 0x0f.
# Result is true exactly when at least one of bits 3..2 and at least one of bits 1..0 are set.
