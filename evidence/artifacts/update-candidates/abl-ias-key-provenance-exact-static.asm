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
