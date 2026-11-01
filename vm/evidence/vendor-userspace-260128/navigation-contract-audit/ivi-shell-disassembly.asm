
work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/weston/ivi-shell.so:	file format elf64-x86-64

Disassembly of section .init:

0000000000003000 <_init>:
    3000: 48 83 ec 08                  	subq	$0x8, %rsp
    3004: 48 8b 05 9d df 20 00         	movq	0x20df9d(%rip), %rax    # 0x210fa8 <_GLOBAL_OFFSET_TABLE_+0x390>
    300b: 48 85 c0                     	testq	%rax, %rax
    300e: 74 02                        	je	0x3012 <_init+0x12>
    3010: ff d0                        	callq	*%rax
    3012: e8 c2 07 00 00               	callq	0x37d9 <frame_dummy>
    3017: e8 4e 97 00 00               	callq	0xc76a <__do_global_ctors_aux>
    301c: 48 83 c4 08                  	addq	$0x8, %rsp
    3020: c3                           	retq

Disassembly of section .plt:

0000000000003030 <.plt>:
    3030: ff 35 ea db 20 00            	pushq	0x20dbea(%rip)          # 0x210c20 <_GLOBAL_OFFSET_TABLE_+0x8>
    3036: ff 25 ec db 20 00            	jmpq	*0x20dbec(%rip)         # 0x210c28 <_GLOBAL_OFFSET_TABLE_+0x10>
    303c: 0f 1f 40 00                  	nopl	(%rax)

0000000000003040 <weston_compositor_schedule_repaint@plt>:
    3040: ff 25 ea db 20 00            	jmpq	*0x20dbea(%rip)         # 0x210c30 <_GLOBAL_OFFSET_TABLE_+0x18>
    3046: 68 00 00 00 00               	pushq	$0x0
    304b: e9 e0 ff ff ff               	jmp	0x3030 <.plt>

0000000000003050 <getenv@plt>:
    3050: ff 25 e2 db 20 00            	jmpq	*0x20dbe2(%rip)         # 0x210c38 <_GLOBAL_OFFSET_TABLE_+0x20>
    3056: 68 01 00 00 00               	pushq	$0x1
    305b: e9 d0 ff ff ff               	jmp	0x3030 <.plt>

0000000000003060 <__snprintf_chk@plt>:
    3060: ff 25 da db 20 00            	jmpq	*0x20dbda(%rip)         # 0x210c40 <_GLOBAL_OFFSET_TABLE_+0x28>
    3066: 68 02 00 00 00               	pushq	$0x2
    306b: e9 c0 ff ff ff               	jmp	0x3030 <.plt>

0000000000003070 <free@plt>:
    3070: ff 25 d2 db 20 00            	jmpq	*0x20dbd2(%rip)         # 0x210c48 <_GLOBAL_OFFSET_TABLE_+0x30>
    3076: 68 03 00 00 00               	pushq	$0x3
    307b: e9 b0 ff ff ff               	jmp	0x3030 <.plt>

0000000000003080 <wl_global_create@plt>:
    3080: ff 25 ca db 20 00            	jmpq	*0x20dbca(%rip)         # 0x210c50 <_GLOBAL_OFFSET_TABLE_+0x38>
    3086: 68 04 00 00 00               	pushq	$0x4
    308b: e9 a0 ff ff ff               	jmp	0x3030 <.plt>

0000000000003090 <wl_event_source_timer_update@plt>:
    3090: ff 25 c2 db 20 00            	jmpq	*0x20dbc2(%rip)         # 0x210c58 <_GLOBAL_OFFSET_TABLE_+0x40>
    3096: 68 05 00 00 00               	pushq	$0x5
    309b: e9 90 ff ff ff               	jmp	0x3030 <.plt>

00000000000030a0 <localtime@plt>:
    30a0: ff 25 ba db 20 00            	jmpq	*0x20dbba(%rip)         # 0x210c60 <_GLOBAL_OFFSET_TABLE_+0x48>
    30a6: 68 06 00 00 00               	pushq	$0x6
    30ab: e9 80 ff ff ff               	jmp	0x3030 <.plt>

00000000000030b0 <__errno_location@plt>:
    30b0: ff 25 b2 db 20 00            	jmpq	*0x20dbb2(%rip)         # 0x210c68 <_GLOBAL_OFFSET_TABLE_+0x50>
    30b6: 68 07 00 00 00               	pushq	$0x7
    30bb: e9 70 ff ff ff               	jmp	0x3030 <.plt>

00000000000030c0 <wl_display_terminate@plt>:
    30c0: ff 25 aa db 20 00            	jmpq	*0x20dbaa(%rip)         # 0x210c70 <_GLOBAL_OFFSET_TABLE_+0x58>
    30c6: 68 08 00 00 00               	pushq	$0x8
    30cb: e9 60 ff ff ff               	jmp	0x3030 <.plt>

00000000000030d0 <unlink@plt>:
    30d0: ff 25 a2 db 20 00            	jmpq	*0x20dba2(%rip)         # 0x210c78 <_GLOBAL_OFFSET_TABLE_+0x60>
    30d6: 68 09 00 00 00               	pushq	$0x9
    30db: e9 50 ff ff ff               	jmp	0x3030 <.plt>

00000000000030e0 <strncmp@plt>:
    30e0: ff 25 9a db 20 00            	jmpq	*0x20db9a(%rip)         # 0x210c80 <_GLOBAL_OFFSET_TABLE_+0x68>
    30e6: 68 0a 00 00 00               	pushq	$0xa
    30eb: e9 40 ff ff ff               	jmp	0x3030 <.plt>

00000000000030f0 <weston_install_debug_key_binding@plt>:
    30f0: ff 25 92 db 20 00            	jmpq	*0x20db92(%rip)         # 0x210c88 <_GLOBAL_OFFSET_TABLE_+0x70>
    30f6: 68 0b 00 00 00               	pushq	$0xb
    30fb: e9 30 ff ff ff               	jmp	0x3030 <.plt>

0000000000003100 <weston_layer_init@plt>:
    3100: ff 25 8a db 20 00            	jmpq	*0x20db8a(%rip)         # 0x210c90 <_GLOBAL_OFFSET_TABLE_+0x78>
    3106: 68 0c 00 00 00               	pushq	$0xc
    310b: e9 20 ff ff ff               	jmp	0x3030 <.plt>

0000000000003110 <pixman_region32_fini@plt>:
    3110: ff 25 82 db 20 00            	jmpq	*0x20db82(%rip)         # 0x210c98 <_GLOBAL_OFFSET_TABLE_+0x80>
    3116: 68 0d 00 00 00               	pushq	$0xd
    311b: e9 10 ff ff ff               	jmp	0x3030 <.plt>

0000000000003120 <weston_matrix_init@plt>:
    3120: ff 25 7a db 20 00            	jmpq	*0x20db7a(%rip)         # 0x210ca0 <_GLOBAL_OFFSET_TABLE_+0x88>
    3126: 68 0e 00 00 00               	pushq	$0xe
    312b: e9 00 ff ff ff               	jmp	0x3030 <.plt>

0000000000003130 <weston_load_module@plt>:
    3130: ff 25 72 db 20 00            	jmpq	*0x20db72(%rip)         # 0x210ca8 <_GLOBAL_OFFSET_TABLE_+0x90>
    3136: 68 0f 00 00 00               	pushq	$0xf
    313b: e9 f0 fe ff ff               	jmp	0x3030 <.plt>

0000000000003140 <strtod@plt>:
    3140: ff 25 6a db 20 00            	jmpq	*0x20db6a(%rip)         # 0x210cb0 <_GLOBAL_OFFSET_TABLE_+0x98>
    3146: 68 10 00 00 00               	pushq	$0x10
    314b: e9 e0 fe ff ff               	jmp	0x3030 <.plt>

0000000000003150 <strchrnul@plt>:
    3150: ff 25 62 db 20 00            	jmpq	*0x20db62(%rip)         # 0x210cb8 <_GLOBAL_OFFSET_TABLE_+0xa0>
    3156: 68 11 00 00 00               	pushq	$0x11
    315b: e9 d0 fe ff ff               	jmp	0x3030 <.plt>

0000000000003160 <weston_view_destroy@plt>:
    3160: ff 25 5a db 20 00            	jmpq	*0x20db5a(%rip)         # 0x210cc0 <_GLOBAL_OFFSET_TABLE_+0xa8>
    3166: 68 12 00 00 00               	pushq	$0x12
    316b: e9 c0 fe ff ff               	jmp	0x3030 <.plt>

0000000000003170 <fcntl@plt>:
    3170: ff 25 52 db 20 00            	jmpq	*0x20db52(%rip)         # 0x210cc8 <_GLOBAL_OFFSET_TABLE_+0xb0>
    3176: 68 13 00 00 00               	pushq	$0x13
    317b: e9 b0 fe ff ff               	jmp	0x3030 <.plt>

0000000000003180 <weston_layer_entry_insert@plt>:
    3180: ff 25 4a db 20 00            	jmpq	*0x20db4a(%rip)         # 0x210cd0 <_GLOBAL_OFFSET_TABLE_+0xb8>
    3186: 68 14 00 00 00               	pushq	$0x14
    318b: e9 a0 fe ff ff               	jmp	0x3030 <.plt>

0000000000003190 <wl_resource_create@plt>:
    3190: ff 25 42 db 20 00            	jmpq	*0x20db42(%rip)         # 0x210cd8 <_GLOBAL_OFFSET_TABLE_+0xc0>
    3196: 68 15 00 00 00               	pushq	$0x15
    319b: e9 90 fe ff ff               	jmp	0x3030 <.plt>

00000000000031a0 <weston_view_set_position@plt>:
    31a0: ff 25 3a db 20 00            	jmpq	*0x20db3a(%rip)         # 0x210ce0 <_GLOBAL_OFFSET_TABLE_+0xc8>
    31a6: 68 16 00 00 00               	pushq	$0x16
    31ab: e9 80 fe ff ff               	jmp	0x3030 <.plt>

00000000000031b0 <fclose@plt>:
    31b0: ff 25 32 db 20 00            	jmpq	*0x20db32(%rip)         # 0x210ce8 <_GLOBAL_OFFSET_TABLE_+0xd0>
    31b6: 68 17 00 00 00               	pushq	$0x17
    31bb: e9 70 fe ff ff               	jmp	0x3030 <.plt>

00000000000031c0 <weston_surface_get_content_size@plt>:
    31c0: ff 25 2a db 20 00            	jmpq	*0x20db2a(%rip)         # 0x210cf0 <_GLOBAL_OFFSET_TABLE_+0xd8>
    31c6: 68 18 00 00 00               	pushq	$0x18
    31cb: e9 60 fe ff ff               	jmp	0x3030 <.plt>

00000000000031d0 <pixman_region32_not_empty@plt>:
    31d0: ff 25 22 db 20 00            	jmpq	*0x20db22(%rip)         # 0x210cf8 <_GLOBAL_OFFSET_TABLE_+0xe0>
    31d6: 68 19 00 00 00               	pushq	$0x19
    31db: e9 50 fe ff ff               	jmp	0x3030 <.plt>

00000000000031e0 <weston_surface_get_main_surface@plt>:
    31e0: ff 25 1a db 20 00            	jmpq	*0x20db1a(%rip)         # 0x210d00 <_GLOBAL_OFFSET_TABLE_+0xe8>
    31e6: 68 1a 00 00 00               	pushq	$0x1a
    31eb: e9 40 fe ff ff               	jmp	0x3030 <.plt>

00000000000031f0 <pixman_region32_init@plt>:
    31f0: ff 25 12 db 20 00            	jmpq	*0x20db12(%rip)         # 0x210d08 <_GLOBAL_OFFSET_TABLE_+0xf0>
    31f6: 68 1b 00 00 00               	pushq	$0x1b
    31fb: e9 30 fe ff ff               	jmp	0x3030 <.plt>

0000000000003200 <strlen@plt>:
    3200: ff 25 0a db 20 00            	jmpq	*0x20db0a(%rip)         # 0x210d10 <_GLOBAL_OFFSET_TABLE_+0xf8>
    3206: 68 1c 00 00 00               	pushq	$0x1c
    320b: e9 20 fe ff ff               	jmp	0x3030 <.plt>

0000000000003210 <weston_log@plt>:
    3210: ff 25 02 db 20 00            	jmpq	*0x20db02(%rip)         # 0x210d18 <_GLOBAL_OFFSET_TABLE_+0x100>
    3216: 68 1d 00 00 00               	pushq	$0x1d
    321b: e9 10 fe ff ff               	jmp	0x3030 <.plt>

0000000000003220 <__stack_chk_fail@plt>:
    3220: ff 25 fa da 20 00            	jmpq	*0x20dafa(%rip)         # 0x210d20 <_GLOBAL_OFFSET_TABLE_+0x108>
    3226: 68 1e 00 00 00               	pushq	$0x1e
    322b: e9 00 fe ff ff               	jmp	0x3030 <.plt>

0000000000003230 <wl_resource_get_user_data@plt>:
    3230: ff 25 f2 da 20 00            	jmpq	*0x20daf2(%rip)         # 0x210d28 <_GLOBAL_OFFSET_TABLE_+0x110>
    3236: 68 1f 00 00 00               	pushq	$0x1f
    323b: e9 f0 fd ff ff               	jmp	0x3030 <.plt>

0000000000003240 <wl_resource_destroy@plt>:
    3240: ff 25 ea da 20 00            	jmpq	*0x20daea(%rip)         # 0x210d30 <_GLOBAL_OFFSET_TABLE_+0x118>
    3246: 68 20 00 00 00               	pushq	$0x20
    324b: e9 e0 fd ff ff               	jmp	0x3030 <.plt>

0000000000003250 <strchr@plt>:
    3250: ff 25 e2 da 20 00            	jmpq	*0x20dae2(%rip)         # 0x210d38 <_GLOBAL_OFFSET_TABLE_+0x120>
    3256: 68 21 00 00 00               	pushq	$0x21
    325b: e9 d0 fd ff ff               	jmp	0x3030 <.plt>

0000000000003260 <weston_seat_get_keyboard@plt>:
    3260: ff 25 da da 20 00            	jmpq	*0x20dada(%rip)         # 0x210d40 <_GLOBAL_OFFSET_TABLE_+0x128>
    3266: 68 22 00 00 00               	pushq	$0x22
    326b: e9 c0 fd ff ff               	jmp	0x3030 <.plt>

0000000000003270 <snprintf@plt>:
    3270: ff 25 d2 da 20 00            	jmpq	*0x20dad2(%rip)         # 0x210d48 <_GLOBAL_OFFSET_TABLE_+0x130>
    3276: 68 23 00 00 00               	pushq	$0x23
    327b: e9 b0 fd ff ff               	jmp	0x3030 <.plt>

0000000000003280 <mkostemp@plt>:
    3280: ff 25 ca da 20 00            	jmpq	*0x20daca(%rip)         # 0x210d50 <_GLOBAL_OFFSET_TABLE_+0x138>
    3286: 68 24 00 00 00               	pushq	$0x24
    328b: e9 a0 fd ff ff               	jmp	0x3030 <.plt>

0000000000003290 <pixman_region32_extents@plt>:
    3290: ff 25 c2 da 20 00            	jmpq	*0x20dac2(%rip)         # 0x210d58 <_GLOBAL_OFFSET_TABLE_+0x140>
    3296: 68 25 00 00 00               	pushq	$0x25
    329b: e9 90 fd ff ff               	jmp	0x3030 <.plt>

00000000000032a0 <text_backend_destroy@plt>:
    32a0: ff 25 ba da 20 00            	jmpq	*0x20daba(%rip)         # 0x210d60 <_GLOBAL_OFFSET_TABLE_+0x148>
    32a6: 68 26 00 00 00               	pushq	$0x26
    32ab: e9 80 fd ff ff               	jmp	0x3030 <.plt>

00000000000032b0 <weston_surface_set_role@plt>:
    32b0: ff 25 b2 da 20 00            	jmpq	*0x20dab2(%rip)         # 0x210d68 <_GLOBAL_OFFSET_TABLE_+0x150>
    32b6: 68 27 00 00 00               	pushq	$0x27
    32bb: e9 70 fd ff ff               	jmp	0x3030 <.plt>

00000000000032c0 <__assert_fail@plt>:
    32c0: ff 25 aa da 20 00            	jmpq	*0x20daaa(%rip)         # 0x210d70 <_GLOBAL_OFFSET_TABLE_+0x158>
    32c6: 68 28 00 00 00               	pushq	$0x28
    32cb: e9 60 fd ff ff               	jmp	0x3030 <.plt>

00000000000032d0 <pixman_region32_intersect@plt>:
    32d0: ff 25 a2 da 20 00            	jmpq	*0x20daa2(%rip)         # 0x210d78 <_GLOBAL_OFFSET_TABLE_+0x160>
    32d6: 68 29 00 00 00               	pushq	$0x29
    32db: e9 50 fd ff ff               	jmp	0x3030 <.plt>

00000000000032e0 <wl_resource_set_implementation@plt>:
    32e0: ff 25 9a da 20 00            	jmpq	*0x20da9a(%rip)         # 0x210d80 <_GLOBAL_OFFSET_TABLE_+0x168>
    32e6: 68 2a 00 00 00               	pushq	$0x2a
    32eb: e9 40 fd ff ff               	jmp	0x3030 <.plt>

00000000000032f0 <weston_surface_is_mapped@plt>:
    32f0: ff 25 92 da 20 00            	jmpq	*0x20da92(%rip)         # 0x210d88 <_GLOBAL_OFFSET_TABLE_+0x170>
    32f6: 68 2b 00 00 00               	pushq	$0x2b
    32fb: e9 30 fd ff ff               	jmp	0x3030 <.plt>

0000000000003300 <close@plt>:
    3300: ff 25 8a da 20 00            	jmpq	*0x20da8a(%rip)         # 0x210d90 <_GLOBAL_OFFSET_TABLE_+0x178>
    3306: 68 2c 00 00 00               	pushq	$0x2c
    330b: e9 20 fd ff ff               	jmp	0x3030 <.plt>

0000000000003310 <weston_compositor_add_button_binding@plt>:
    3310: ff 25 82 da 20 00            	jmpq	*0x20da82(%rip)         # 0x210d98 <_GLOBAL_OFFSET_TABLE_+0x180>
    3316: 68 2d 00 00 00               	pushq	$0x2d
    331b: e9 10 fd ff ff               	jmp	0x3030 <.plt>

0000000000003320 <__strdup@plt>:
    3320: ff 25 7a da 20 00            	jmpq	*0x20da7a(%rip)         # 0x210da0 <_GLOBAL_OFFSET_TABLE_+0x188>
    3326: 68 2e 00 00 00               	pushq	$0x2e
    332b: e9 00 fd ff ff               	jmp	0x3030 <.plt>

0000000000003330 <wl_resource_post_error@plt>:
    3330: ff 25 72 da 20 00            	jmpq	*0x20da72(%rip)         # 0x210da8 <_GLOBAL_OFFSET_TABLE_+0x190>
    3336: 68 2f 00 00 00               	pushq	$0x2f
    333b: e9 f0 fc ff ff               	jmp	0x3030 <.plt>

0000000000003340 <wl_list_init@plt>:
    3340: ff 25 6a da 20 00            	jmpq	*0x20da6a(%rip)         # 0x210db0 <_GLOBAL_OFFSET_TABLE_+0x198>
    3346: 68 30 00 00 00               	pushq	$0x30
    334b: e9 e0 fc ff ff               	jmp	0x3030 <.plt>

0000000000003350 <fgets@plt>:
    3350: ff 25 62 da 20 00            	jmpq	*0x20da62(%rip)         # 0x210db8 <_GLOBAL_OFFSET_TABLE_+0x1a0>
    3356: 68 31 00 00 00               	pushq	$0x31
    335b: e9 d0 fc ff ff               	jmp	0x3030 <.plt>

0000000000003360 <ceilf@plt>:
    3360: ff 25 5a da 20 00            	jmpq	*0x20da5a(%rip)         # 0x210dc0 <_GLOBAL_OFFSET_TABLE_+0x1a8>
    3366: 68 32 00 00 00               	pushq	$0x32
    336b: e9 c0 fc ff ff               	jmp	0x3030 <.plt>

0000000000003370 <calloc@plt>:
    3370: ff 25 52 da 20 00            	jmpq	*0x20da52(%rip)         # 0x210dc8 <_GLOBAL_OFFSET_TABLE_+0x1b0>
    3376: 68 33 00 00 00               	pushq	$0x33
    337b: e9 b0 fc ff ff               	jmp	0x3030 <.plt>

0000000000003380 <weston_view_set_transform_parent@plt>:
    3380: ff 25 4a da 20 00            	jmpq	*0x20da4a(%rip)         # 0x210dd0 <_GLOBAL_OFFSET_TABLE_+0x1b8>
    3386: 68 34 00 00 00               	pushq	$0x34
    338b: e9 a0 fc ff ff               	jmp	0x3030 <.plt>

0000000000003390 <strcmp@plt>:
    3390: ff 25 42 da 20 00            	jmpq	*0x20da42(%rip)         # 0x210dd8 <_GLOBAL_OFFSET_TABLE_+0x1c0>
    3396: 68 35 00 00 00               	pushq	$0x35
    339b: e9 90 fc ff ff               	jmp	0x3030 <.plt>

00000000000033a0 <weston_layer_entry_remove@plt>:
    33a0: ff 25 3a da 20 00            	jmpq	*0x20da3a(%rip)         # 0x210de0 <_GLOBAL_OFFSET_TABLE_+0x1c8>
    33a6: 68 36 00 00 00               	pushq	$0x36
    33ab: e9 80 fc ff ff               	jmp	0x3030 <.plt>

00000000000033b0 <wl_client_post_no_memory@plt>:
    33b0: ff 25 32 da 20 00            	jmpq	*0x20da32(%rip)         # 0x210de8 <_GLOBAL_OFFSET_TABLE_+0x1d0>
    33b6: 68 37 00 00 00               	pushq	$0x37
    33bb: e9 70 fc ff ff               	jmp	0x3030 <.plt>

00000000000033c0 <wl_display_get_event_loop@plt>:
    33c0: ff 25 2a da 20 00            	jmpq	*0x20da2a(%rip)         # 0x210df0 <_GLOBAL_OFFSET_TABLE_+0x1d8>
    33c6: 68 38 00 00 00               	pushq	$0x38
    33cb: e9 60 fc ff ff               	jmp	0x3030 <.plt>

00000000000033d0 <strtol@plt>:
    33d0: ff 25 22 da 20 00            	jmpq	*0x20da22(%rip)         # 0x210df8 <_GLOBAL_OFFSET_TABLE_+0x1e0>
    33d6: 68 39 00 00 00               	pushq	$0x39
    33db: e9 50 fc ff ff               	jmp	0x3030 <.plt>

00000000000033e0 <memcpy@plt>:
    33e0: ff 25 1a da 20 00            	jmpq	*0x20da1a(%rip)         # 0x210e00 <_GLOBAL_OFFSET_TABLE_+0x1e8>
    33e6: 68 3a 00 00 00               	pushq	$0x3a
    33eb: e9 40 fc ff ff               	jmp	0x3030 <.plt>

00000000000033f0 <wl_list_empty@plt>:
    33f0: ff 25 12 da 20 00            	jmpq	*0x20da12(%rip)         # 0x210e08 <_GLOBAL_OFFSET_TABLE_+0x1f0>
    33f6: 68 3b 00 00 00               	pushq	$0x3b
    33fb: e9 30 fc ff ff               	jmp	0x3030 <.plt>

0000000000003400 <socketpair@plt>:
    3400: ff 25 0a da 20 00            	jmpq	*0x20da0a(%rip)         # 0x210e10 <_GLOBAL_OFFSET_TABLE_+0x1f8>
    3406: 68 3c 00 00 00               	pushq	$0x3c
    340b: e9 20 fc ff ff               	jmp	0x3030 <.plt>

0000000000003410 <weston_view_create@plt>:
    3410: ff 25 02 da 20 00            	jmpq	*0x20da02(%rip)         # 0x210e18 <_GLOBAL_OFFSET_TABLE_+0x200>
    3416: 68 3d 00 00 00               	pushq	$0x3d
    341b: e9 10 fc ff ff               	jmp	0x3030 <.plt>

0000000000003420 <posix_fallocate@plt>:
    3420: ff 25 fa d9 20 00            	jmpq	*0x20d9fa(%rip)         # 0x210e20 <_GLOBAL_OFFSET_TABLE_+0x208>
    3426: 68 3e 00 00 00               	pushq	$0x3e
    342b: e9 00 fc ff ff               	jmp	0x3030 <.plt>

0000000000003430 <wl_list_remove@plt>:
    3430: ff 25 f2 d9 20 00            	jmpq	*0x20d9f2(%rip)         # 0x210e28 <_GLOBAL_OFFSET_TABLE_+0x210>
    3436: 68 3f 00 00 00               	pushq	$0x3f
    343b: e9 f0 fb ff ff               	jmp	0x3030 <.plt>

0000000000003440 <weston_view_animation_destroy@plt>:
    3440: ff 25 ea d9 20 00            	jmpq	*0x20d9ea(%rip)         # 0x210e30 <_GLOBAL_OFFSET_TABLE_+0x218>
    3446: 68 40 00 00 00               	pushq	$0x40
    344b: e9 e0 fb ff ff               	jmp	0x3030 <.plt>

0000000000003450 <time@plt>:
    3450: ff 25 e2 d9 20 00            	jmpq	*0x20d9e2(%rip)         # 0x210e38 <_GLOBAL_OFFSET_TABLE_+0x220>
    3456: 68 41 00 00 00               	pushq	$0x41
    345b: e9 d0 fb ff ff               	jmp	0x3030 <.plt>

0000000000003460 <weston_surface_activate@plt>:
    3460: ff 25 da d9 20 00            	jmpq	*0x20d9da(%rip)         # 0x210e40 <_GLOBAL_OFFSET_TABLE_+0x228>
    3466: 68 42 00 00 00               	pushq	$0x42
    346b: e9 c0 fb ff ff               	jmp	0x3030 <.plt>

0000000000003470 <malloc@plt>:
    3470: ff 25 d2 d9 20 00            	jmpq	*0x20d9d2(%rip)         # 0x210e48 <_GLOBAL_OFFSET_TABLE_+0x230>
    3476: 68 43 00 00 00               	pushq	$0x43
    347b: e9 b0 fb ff ff               	jmp	0x3030 <.plt>

0000000000003480 <weston_matrix_rotate_xy@plt>:
    3480: ff 25 ca d9 20 00            	jmpq	*0x20d9ca(%rip)         # 0x210e50 <_GLOBAL_OFFSET_TABLE_+0x238>
    3486: 68 44 00 00 00               	pushq	$0x44
    348b: e9 a0 fb ff ff               	jmp	0x3030 <.plt>

0000000000003490 <weston_surface_damage@plt>:
    3490: ff 25 c2 d9 20 00            	jmpq	*0x20d9c2(%rip)         # 0x210e58 <_GLOBAL_OFFSET_TABLE_+0x240>
    3496: 68 45 00 00 00               	pushq	$0x45
    349b: e9 90 fb ff ff               	jmp	0x3030 <.plt>

00000000000034a0 <weston_config_section_get_bool@plt>:
    34a0: ff 25 ba d9 20 00            	jmpq	*0x20d9ba(%rip)         # 0x210e60 <_GLOBAL_OFFSET_TABLE_+0x248>
    34a6: 68 46 00 00 00               	pushq	$0x46
    34ab: e9 80 fb ff ff               	jmp	0x3030 <.plt>

00000000000034b0 <__fxstat@plt>:
    34b0: ff 25 b2 d9 20 00            	jmpq	*0x20d9b2(%rip)         # 0x210e68 <_GLOBAL_OFFSET_TABLE_+0x250>
    34b6: 68 47 00 00 00               	pushq	$0x47
    34bb: e9 70 fb ff ff               	jmp	0x3030 <.plt>

00000000000034c0 <clock_gettime@plt>:
    34c0: ff 25 aa d9 20 00            	jmpq	*0x20d9aa(%rip)         # 0x210e70 <_GLOBAL_OFFSET_TABLE_+0x258>
    34c6: 68 48 00 00 00               	pushq	$0x48
    34cb: e9 60 fb ff ff               	jmp	0x3030 <.plt>

00000000000034d0 <weston_config_get_section@plt>:
    34d0: ff 25 a2 d9 20 00            	jmpq	*0x20d9a2(%rip)         # 0x210e78 <_GLOBAL_OFFSET_TABLE_+0x260>
    34d6: 68 49 00 00 00               	pushq	$0x49
    34db: e9 50 fb ff ff               	jmp	0x3030 <.plt>

00000000000034e0 <weston_view_is_mapped@plt>:
    34e0: ff 25 9a d9 20 00            	jmpq	*0x20d99a(%rip)         # 0x210e80 <_GLOBAL_OFFSET_TABLE_+0x268>
    34e6: 68 4a 00 00 00               	pushq	$0x4a
    34eb: e9 40 fb ff ff               	jmp	0x3030 <.plt>

00000000000034f0 <weston_surface_copy_content@plt>:
    34f0: ff 25 92 d9 20 00            	jmpq	*0x20d992(%rip)         # 0x210e88 <_GLOBAL_OFFSET_TABLE_+0x270>
    34f6: 68 4b 00 00 00               	pushq	$0x4b
    34fb: e9 30 fb ff ff               	jmp	0x3030 <.plt>

0000000000003500 <fdopen@plt>:
    3500: ff 25 8a d9 20 00            	jmpq	*0x20d98a(%rip)         # 0x210e90 <_GLOBAL_OFFSET_TABLE_+0x278>
    3506: 68 4c 00 00 00               	pushq	$0x4c
    350b: e9 20 fb ff ff               	jmp	0x3030 <.plt>

0000000000003510 <wl_list_insert_list@plt>:
    3510: ff 25 82 d9 20 00            	jmpq	*0x20d982(%rip)         # 0x210e98 <_GLOBAL_OFFSET_TABLE_+0x280>
    3516: 68 4d 00 00 00               	pushq	$0x4d
    351b: e9 10 fb ff ff               	jmp	0x3030 <.plt>

0000000000003520 <weston_compositor_add_touch_binding@plt>:
    3520: ff 25 7a d9 20 00            	jmpq	*0x20d97a(%rip)         # 0x210ea0 <_GLOBAL_OFFSET_TABLE_+0x288>
    3526: 68 4e 00 00 00               	pushq	$0x4e
    352b: e9 00 fb ff ff               	jmp	0x3030 <.plt>

0000000000003530 <weston_slide_run@plt>:
    3530: ff 25 72 d9 20 00            	jmpq	*0x20d972(%rip)         # 0x210ea8 <_GLOBAL_OFFSET_TABLE_+0x290>
    3536: 68 4f 00 00 00               	pushq	$0x4f
    353b: e9 f0 fa ff ff               	jmp	0x3030 <.plt>

0000000000003540 <weston_view_unmap@plt>:
    3540: ff 25 6a d9 20 00            	jmpq	*0x20d96a(%rip)         # 0x210eb0 <_GLOBAL_OFFSET_TABLE_+0x298>
    3546: 68 50 00 00 00               	pushq	$0x50
    354b: e9 e0 fa ff ff               	jmp	0x3030 <.plt>

0000000000003550 <strftime@plt>:
    3550: ff 25 62 d9 20 00            	jmpq	*0x20d962(%rip)         # 0x210eb8 <_GLOBAL_OFFSET_TABLE_+0x2a0>
    3556: 68 51 00 00 00               	pushq	$0x51
    355b: e9 d0 fa ff ff               	jmp	0x3030 <.plt>

0000000000003560 <wl_resource_post_event@plt>:
    3560: ff 25 5a d9 20 00            	jmpq	*0x20d95a(%rip)         # 0x210ec0 <_GLOBAL_OFFSET_TABLE_+0x2a8>
    3566: 68 52 00 00 00               	pushq	$0x52
    356b: e9 c0 fa ff ff               	jmp	0x3030 <.plt>

0000000000003570 <pixman_region32_init_rect@plt>:
    3570: ff 25 52 d9 20 00            	jmpq	*0x20d952(%rip)         # 0x210ec8 <_GLOBAL_OFFSET_TABLE_+0x2b0>
    3576: 68 53 00 00 00               	pushq	$0x53
    357b: e9 b0 fa ff ff               	jmp	0x3030 <.plt>

0000000000003580 <screenshooter_create@plt>:
    3580: ff 25 4a d9 20 00            	jmpq	*0x20d94a(%rip)         # 0x210ed0 <_GLOBAL_OFFSET_TABLE_+0x2b8>
    3586: 68 54 00 00 00               	pushq	$0x54
    358b: e9 a0 fa ff ff               	jmp	0x3030 <.plt>

0000000000003590 <wl_list_length@plt>:
    3590: ff 25 42 d9 20 00            	jmpq	*0x20d942(%rip)         # 0x210ed8 <_GLOBAL_OFFSET_TABLE_+0x2c0>
    3596: 68 55 00 00 00               	pushq	$0x55
    359b: e9 90 fa ff ff               	jmp	0x3030 <.plt>

00000000000035a0 <open@plt>:
    35a0: ff 25 3a d9 20 00            	jmpq	*0x20d93a(%rip)         # 0x210ee0 <_GLOBAL_OFFSET_TABLE_+0x2c8>
    35a6: 68 56 00 00 00               	pushq	$0x56
    35ab: e9 80 fa ff ff               	jmp	0x3030 <.plt>

00000000000035b0 <weston_matrix_translate@plt>:
    35b0: ff 25 32 d9 20 00            	jmpq	*0x20d932(%rip)         # 0x210ee8 <_GLOBAL_OFFSET_TABLE_+0x2d0>
    35b6: 68 57 00 00 00               	pushq	$0x57
    35bb: e9 70 fa ff ff               	jmp	0x3030 <.plt>

00000000000035c0 <weston_config_section_get_string@plt>:
    35c0: ff 25 2a d9 20 00            	jmpq	*0x20d92a(%rip)         # 0x210ef0 <_GLOBAL_OFFSET_TABLE_+0x2d8>
    35c6: 68 58 00 00 00               	pushq	$0x58
    35cb: e9 60 fa ff ff               	jmp	0x3030 <.plt>

00000000000035d0 <text_backend_init@plt>:
    35d0: ff 25 22 d9 20 00            	jmpq	*0x20d922(%rip)         # 0x210ef8 <_GLOBAL_OFFSET_TABLE_+0x2e0>
    35d6: 68 59 00 00 00               	pushq	$0x59
    35db: e9 50 fa ff ff               	jmp	0x3030 <.plt>

00000000000035e0 <weston_view_set_mask@plt>:
    35e0: ff 25 1a d9 20 00            	jmpq	*0x20d91a(%rip)         # 0x210f00 <_GLOBAL_OFFSET_TABLE_+0x2e8>
    35e6: 68 5a 00 00 00               	pushq	$0x5a
    35eb: e9 40 fa ff ff               	jmp	0x3030 <.plt>

00000000000035f0 <floorf@plt>:
    35f0: ff 25 12 d9 20 00            	jmpq	*0x20d912(%rip)         # 0x210f08 <_GLOBAL_OFFSET_TABLE_+0x2f0>
    35f6: 68 5b 00 00 00               	pushq	$0x5b
    35fb: e9 30 fa ff ff               	jmp	0x3030 <.plt>

0000000000003600 <sin@plt>:
    3600: ff 25 0a d9 20 00            	jmpq	*0x20d90a(%rip)         # 0x210f10 <_GLOBAL_OFFSET_TABLE_+0x2f8>
    3606: 68 5c 00 00 00               	pushq	$0x5c
    360b: e9 20 fa ff ff               	jmp	0x3030 <.plt>

0000000000003610 <strtoul@plt>:
    3610: ff 25 02 d9 20 00            	jmpq	*0x20d902(%rip)         # 0x210f18 <_GLOBAL_OFFSET_TABLE_+0x300>
    3616: 68 5d 00 00 00               	pushq	$0x5d
    361b: e9 10 fa ff ff               	jmp	0x3030 <.plt>

0000000000003620 <weston_matrix_transform@plt>:
    3620: ff 25 fa d8 20 00            	jmpq	*0x20d8fa(%rip)         # 0x210f20 <_GLOBAL_OFFSET_TABLE_+0x308>
    3626: 68 5e 00 00 00               	pushq	$0x5e
    362b: e9 00 fa ff ff               	jmp	0x3030 <.plt>

0000000000003630 <weston_view_geometry_dirty@plt>:
    3630: ff 25 f2 d8 20 00            	jmpq	*0x20d8f2(%rip)         # 0x210f28 <_GLOBAL_OFFSET_TABLE_+0x310>
    3636: 68 5f 00 00 00               	pushq	$0x5f
    363b: e9 f0 f9 ff ff               	jmp	0x3030 <.plt>

0000000000003640 <wl_event_loop_add_timer@plt>:
    3640: ff 25 ea d8 20 00            	jmpq	*0x20d8ea(%rip)         # 0x210f30 <_GLOBAL_OFFSET_TABLE_+0x318>
    3646: 68 60 00 00 00               	pushq	$0x60
    364b: e9 e0 f9 ff ff               	jmp	0x3030 <.plt>

0000000000003650 <weston_view_update_transform@plt>:
    3650: ff 25 e2 d8 20 00            	jmpq	*0x20d8e2(%rip)         # 0x210f38 <_GLOBAL_OFFSET_TABLE_+0x320>
    3656: 68 61 00 00 00               	pushq	$0x61
    365b: e9 d0 f9 ff ff               	jmp	0x3030 <.plt>

0000000000003660 <epoll_create@plt>:
    3660: ff 25 da d8 20 00            	jmpq	*0x20d8da(%rip)         # 0x210f40 <_GLOBAL_OFFSET_TABLE_+0x328>
    3666: 68 62 00 00 00               	pushq	$0x62
    366b: e9 c0 f9 ff ff               	jmp	0x3030 <.plt>

0000000000003670 <fwrite@plt>:
    3670: ff 25 d2 d8 20 00            	jmpq	*0x20d8d2(%rip)         # 0x210f48 <_GLOBAL_OFFSET_TABLE_+0x330>
    3676: 68 63 00 00 00               	pushq	$0x63
    367b: e9 b0 f9 ff ff               	jmp	0x3030 <.plt>

0000000000003680 <weston_compositor_add_key_binding@plt>:
    3680: ff 25 ca d8 20 00            	jmpq	*0x20d8ca(%rip)         # 0x210f50 <_GLOBAL_OFFSET_TABLE_+0x338>
    3686: 68 64 00 00 00               	pushq	$0x64
    368b: e9 a0 f9 ff ff               	jmp	0x3030 <.plt>

0000000000003690 <__fprintf_chk@plt>:
    3690: ff 25 c2 d8 20 00            	jmpq	*0x20d8c2(%rip)         # 0x210f58 <_GLOBAL_OFFSET_TABLE_+0x340>
    3696: 68 65 00 00 00               	pushq	$0x65
    369b: e9 90 f9 ff ff               	jmp	0x3030 <.plt>

00000000000036a0 <wl_list_insert@plt>:
    36a0: ff 25 ba d8 20 00            	jmpq	*0x20d8ba(%rip)         # 0x210f60 <_GLOBAL_OFFSET_TABLE_+0x348>
    36a6: 68 66 00 00 00               	pushq	$0x66
    36ab: e9 80 f9 ff ff               	jmp	0x3030 <.plt>

00000000000036b0 <wl_resource_post_no_memory@plt>:
    36b0: ff 25 b2 d8 20 00            	jmpq	*0x20d8b2(%rip)         # 0x210f68 <_GLOBAL_OFFSET_TABLE_+0x350>
    36b6: 68 67 00 00 00               	pushq	$0x67
    36bb: e9 70 f9 ff ff               	jmp	0x3030 <.plt>

00000000000036c0 <epoll_create1@plt>:
    36c0: ff 25 aa d8 20 00            	jmpq	*0x20d8aa(%rip)         # 0x210f70 <_GLOBAL_OFFSET_TABLE_+0x358>
    36c6: 68 68 00 00 00               	pushq	$0x68
    36cb: e9 60 f9 ff ff               	jmp	0x3030 <.plt>

00000000000036d0 <__cxa_finalize@plt>:
    36d0: ff 25 a2 d8 20 00            	jmpq	*0x20d8a2(%rip)         # 0x210f78 <_GLOBAL_OFFSET_TABLE_+0x360>
    36d6: 68 69 00 00 00               	pushq	$0x69
    36db: e9 50 f9 ff ff               	jmp	0x3030 <.plt>

00000000000036e0 <weston_matrix_scale@plt>:
    36e0: ff 25 9a d8 20 00            	jmpq	*0x20d89a(%rip)         # 0x210f80 <_GLOBAL_OFFSET_TABLE_+0x368>
    36e6: 68 6a 00 00 00               	pushq	$0x6a
    36eb: e9 40 f9 ff ff               	jmp	0x3030 <.plt>

00000000000036f0 <__ctype_b_loc@plt>:
    36f0: ff 25 92 d8 20 00            	jmpq	*0x20d892(%rip)         # 0x210f88 <_GLOBAL_OFFSET_TABLE_+0x370>
    36f6: 68 6b 00 00 00               	pushq	$0x6b
    36fb: e9 30 f9 ff ff               	jmp	0x3030 <.plt>

Disassembly of section .text:

0000000000003700 <deregister_tm_clones>:
    3700: 48 8d 3d c1 db 20 00         	leaq	0x20dbc1(%rip), %rdi    # 0x2112c8 <_edata>
    3707: 55                           	pushq	%rbp
    3708: 48 8d 05 c0 db 20 00         	leaq	0x20dbc0(%rip), %rax    # 0x2112cf <_edata+0x7>
    370f: 48 89 e5                     	movq	%rsp, %rbp
    3712: 48 29 f8                     	subq	%rdi, %rax
    3715: 48 83 f8 0e                  	cmpq	$0xe, %rax
    3719: 76 0f                        	jbe	0x372a <deregister_tm_clones+0x2a>
    371b: 48 8b 05 6e d8 20 00         	movq	0x20d86e(%rip), %rax    # 0x210f90 <_GLOBAL_OFFSET_TABLE_+0x378>
    3722: 48 85 c0                     	testq	%rax, %rax
    3725: 74 03                        	je	0x372a <deregister_tm_clones+0x2a>
    3727: 5d                           	popq	%rbp
    3728: ff e0                        	jmpq	*%rax
    372a: 5d                           	popq	%rbp
    372b: c3                           	retq

000000000000372c <register_tm_clones>:
    372c: 48 8d 3d 95 db 20 00         	leaq	0x20db95(%rip), %rdi    # 0x2112c8 <_edata>
    3733: 55                           	pushq	%rbp
    3734: b9 02 00 00 00               	movl	$0x2, %ecx
    3739: 48 8d 35 88 db 20 00         	leaq	0x20db88(%rip), %rsi    # 0x2112c8 <_edata>
    3740: 48 89 e5                     	movq	%rsp, %rbp
    3743: 48 29 fe                     	subq	%rdi, %rsi
    3746: 48 89 f0                     	movq	%rsi, %rax
    3749: 48 c1 f8 03                  	sarq	$0x3, %rax
    374d: 48 99                        	cqto
    374f: 48 f7 f9                     	idivq	%rcx
    3752: 48 85 c0                     	testq	%rax, %rax
    3755: 74 12                        	je	0x3769 <register_tm_clones+0x3d>
    3757: 48 89 c6                     	movq	%rax, %rsi
    375a: 48 8b 05 6f d8 20 00         	movq	0x20d86f(%rip), %rax    # 0x210fd0 <_GLOBAL_OFFSET_TABLE_+0x3b8>
    3761: 48 85 c0                     	testq	%rax, %rax
    3764: 74 03                        	je	0x3769 <register_tm_clones+0x3d>
    3766: 5d                           	popq	%rbp
    3767: ff e0                        	jmpq	*%rax
    3769: 5d                           	popq	%rbp
    376a: c3                           	retq

000000000000376b <__do_global_dtors_aux>:
    376b: 80 3d 6e db 20 00 00         	cmpb	$0x0, 0x20db6e(%rip)    # 0x2112e0 <completed.7699>
    3772: 75 64                        	jne	0x37d8 <__do_global_dtors_aux+0x6d>
    3774: 48 83 3d 5c d8 20 00 00      	cmpq	$0x0, 0x20d85c(%rip)    # 0x210fd8 <_GLOBAL_OFFSET_TABLE_+0x3c0>
    377c: 55                           	pushq	%rbp
    377d: 48 89 e5                     	movq	%rsp, %rbp
    3780: 41 54                        	pushq	%r12
    3782: 53                           	pushq	%rbx
    3783: 74 0c                        	je	0x3791 <__do_global_dtors_aux+0x26>
    3785: 48 8b 3d 74 d8 20 00         	movq	0x20d874(%rip), %rdi    # 0x211000 <__dso_handle>
    378c: e8 3f ff ff ff               	callq	0x36d0 <__cxa_finalize@plt>
    3791: 48 8d 05 10 d1 20 00         	leaq	0x20d110(%rip), %rax    # 0x2108a8 <__DTOR_LIST__>
    3798: 48 8d 1d 11 d1 20 00         	leaq	0x20d111(%rip), %rbx    # 0x2108b0 <__DTOR_END__>
    379f: 49 89 c4                     	movq	%rax, %r12
    37a2: 48 29 c3                     	subq	%rax, %rbx
    37a5: 48 c1 fb 03                  	sarq	$0x3, %rbx
    37a9: 48 ff cb                     	decq	%rbx
    37ac: 48 8b 05 35 db 20 00         	movq	0x20db35(%rip), %rax    # 0x2112e8 <dtor_idx.7701>
    37b3: 48 39 d8                     	cmpq	%rbx, %rax
    37b6: 73 10                        	jae	0x37c8 <__do_global_dtors_aux+0x5d>
    37b8: 48 ff c0                     	incq	%rax
    37bb: 48 89 05 26 db 20 00         	movq	%rax, 0x20db26(%rip)    # 0x2112e8 <dtor_idx.7701>
    37c2: 41 ff 14 c4                  	callq	*(%r12,%rax,8)
    37c6: eb e4                        	jmp	0x37ac <__do_global_dtors_aux+0x41>
    37c8: e8 33 ff ff ff               	callq	0x3700 <deregister_tm_clones>
    37cd: 5b                           	popq	%rbx
    37ce: c6 05 0b db 20 00 01         	movb	$0x1, 0x20db0b(%rip)    # 0x2112e0 <completed.7699>
    37d5: 41 5c                        	popq	%r12
    37d7: 5d                           	popq	%rbp
    37d8: c3                           	retq

00000000000037d9 <frame_dummy>:
    37d9: 48 8d 3d d8 d0 20 00         	leaq	0x20d0d8(%rip), %rdi    # 0x2108b8 <__JCR_LIST__>
    37e0: 48 83 3f 00                  	cmpq	$0x0, (%rdi)
    37e4: 74 13                        	je	0x37f9 <frame_dummy+0x20>
    37e6: 48 8b 05 d3 d7 20 00         	movq	0x20d7d3(%rip), %rax    # 0x210fc0 <_GLOBAL_OFFSET_TABLE_+0x3a8>
    37ed: 48 85 c0                     	testq	%rax, %rax
    37f0: 74 07                        	je	0x37f9 <frame_dummy+0x20>
    37f2: 55                           	pushq	%rbp
    37f3: 48 89 e5                     	movq	%rsp, %rbp
    37f6: ff d0                        	callq	*%rax
    37f8: 5d                           	popq	%rbp
    37f9: e9 2e ff ff ff               	jmp	0x372c <register_tm_clones>
    37fe: 66 90                        	nop

0000000000003800 <layer_prop_changed>:
    3800: 48 83 ec 18                  	subq	$0x18, %rsp
    3804: 48 8b 7f f8                  	movq	-0x8(%rdi), %rdi
    3808: 64 48 8b 14 25 28 00 00 00   	movq	%fs:0x28, %rdx
    3811: 48 89 54 24 08               	movq	%rdx, 0x8(%rsp)
    3816: 31 d2                        	xorl	%edx, %edx
    3818: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    381d: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    3826: 75 1e                        	jne	0x3846 <layer_prop_changed+0x46>
    3828: 48 89 f0                     	movq	%rsi, %rax
    382b: 48 8b 4f 08                  	movq	0x8(%rdi), %rcx
    382f: 8b 96 88 00 00 00            	movl	0x88(%rsi), %edx
    3835: 48 8d 76 38                  	leaq	0x38(%rsi), %rsi
    3839: 4c 8b 07                     	movq	(%rdi), %r8
    383c: 48 89 c7                     	movq	%rax, %rdi
    383f: 48 83 c4 18                  	addq	$0x18, %rsp
    3843: 41 ff e0                     	jmpq	*%r8
    3846: e8 d5 f9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    384b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000003850 <surface_prop_changed>:
    3850: 48 83 ec 18                  	subq	$0x18, %rsp
    3854: 48 8b 7f f8                  	movq	-0x8(%rdi), %rdi
    3858: 64 48 8b 14 25 28 00 00 00   	movq	%fs:0x28, %rdx
    3861: 48 89 54 24 08               	movq	%rdx, 0x8(%rsp)
    3866: 31 d2                        	xorl	%edx, %edx
    3868: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    386d: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    3876: 75 21                        	jne	0x3899 <surface_prop_changed+0x49>
    3878: 48 89 f0                     	movq	%rsi, %rax
    387b: 48 8b 4f 08                  	movq	0x8(%rdi), %rcx
    387f: 8b 96 dc 00 00 00            	movl	0xdc(%rsi), %edx
    3885: 48 8d b6 98 00 00 00         	leaq	0x98(%rsi), %rsi
    388c: 4c 8b 07                     	movq	(%rdi), %r8
    388f: 48 89 c7                     	movq	%rax, %rdi
    3892: 48 83 c4 18                  	addq	$0x18, %rsp
    3896: 41 ff e0                     	jmpq	*%r8
    3899: e8 82 f9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    389e: 66 90                        	nop

00000000000038a0 <surface_configure_changed>:
    38a0: 48 83 ec 18                  	subq	$0x18, %rsp
    38a4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    38ad: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    38b2: 31 c0                        	xorl	%eax, %eax
    38b4: 48 8b 47 f8                  	movq	-0x8(%rdi), %rax
    38b8: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    38bd: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    38c6: 75 13                        	jne	0x38db <surface_configure_changed+0x3b>
    38c8: 48 89 f2                     	movq	%rsi, %rdx
    38cb: 48 8b 70 08                  	movq	0x8(%rax), %rsi
    38cf: 48 89 d7                     	movq	%rdx, %rdi
    38d2: 48 8b 00                     	movq	(%rax), %rax
    38d5: 48 83 c4 18                  	addq	$0x18, %rsp
    38d9: ff e0                        	jmpq	*%rax
    38db: e8 40 f9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>

00000000000038e0 <surface_removed>:
    38e0: 48 83 ec 18                  	subq	$0x18, %rsp
    38e4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    38ed: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    38f2: 31 c0                        	xorl	%eax, %eax
    38f4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    38f9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    3902: 75 06                        	jne	0x390a <surface_removed+0x2a>
    3904: 48 83 c4 18                  	addq	$0x18, %rsp
    3908: eb 96                        	jmp	0x38a0 <surface_configure_changed>
    390a: e8 11 f9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    390f: 90                           	nop

0000000000003910 <surface_created>:
    3910: 48 83 ec 18                  	subq	$0x18, %rsp
    3914: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    391d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3922: 31 c0                        	xorl	%eax, %eax
    3924: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    3929: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    3932: 75 09                        	jne	0x393d <surface_created+0x2d>
    3934: 48 83 c4 18                  	addq	$0x18, %rsp
    3938: e9 63 ff ff ff               	jmp	0x38a0 <surface_configure_changed>
    393d: e8 de f8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3942: 0f 1f 40 00                  	nopl	(%rax)
    3946: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003950 <layer_removed>:
    3950: 48 83 ec 18                  	subq	$0x18, %rsp
    3954: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    395d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3962: 31 c0                        	xorl	%eax, %eax
    3964: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    3969: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    3972: 75 09                        	jne	0x397d <layer_removed+0x2d>
    3974: 48 83 c4 18                  	addq	$0x18, %rsp
    3978: e9 23 ff ff ff               	jmp	0x38a0 <surface_configure_changed>
    397d: e8 9e f8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3982: 0f 1f 40 00                  	nopl	(%rax)
    3986: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003990 <layer_created>:
    3990: 48 83 ec 18                  	subq	$0x18, %rsp
    3994: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    399d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    39a2: 31 c0                        	xorl	%eax, %eax
    39a4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    39a9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    39b2: 75 09                        	jne	0x39bd <layer_created+0x2d>
    39b4: 48 83 c4 18                  	addq	$0x18, %rsp
    39b8: e9 e3 fe ff ff               	jmp	0x38a0 <surface_configure_changed>
    39bd: e8 5e f8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    39c2: 0f 1f 40 00                  	nopl	(%rax)
    39c6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000039d0 <ivi_layout_get_id_of_surface>:
    39d0: 48 83 ec 18                  	subq	$0x18, %rsp
    39d4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    39dd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    39e2: 31 c0                        	xorl	%eax, %eax
    39e4: 8b 47 24                     	movl	0x24(%rdi), %eax
    39e7: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    39ec: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    39f5: 75 05                        	jne	0x39fc <ivi_layout_get_id_of_surface+0x2c>
    39f7: 48 83 c4 18                  	addq	$0x18, %rsp
    39fb: c3                           	retq
    39fc: e8 1f f8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3a01: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    3a06: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003a10 <ivi_layout_get_id_of_layer>:
    3a10: 48 83 ec 18                  	subq	$0x18, %rsp
    3a14: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3a1d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3a22: 31 c0                        	xorl	%eax, %eax
    3a24: 8b 47 20                     	movl	0x20(%rdi), %eax
    3a27: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3a2c: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3a35: 75 05                        	jne	0x3a3c <ivi_layout_get_id_of_layer+0x2c>
    3a37: 48 83 c4 18                  	addq	$0x18, %rsp
    3a3b: c3                           	retq
    3a3c: e8 df f7 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3a41: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    3a46: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003a50 <ivi_layout_get_id_of_screen>:
    3a50: 48 83 ec 18                  	subq	$0x18, %rsp
    3a54: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3a5d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3a62: 31 c0                        	xorl	%eax, %eax
    3a64: 8b 47 10                     	movl	0x10(%rdi), %eax
    3a67: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3a6c: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3a75: 75 05                        	jne	0x3a7c <ivi_layout_get_id_of_screen+0x2c>
    3a77: 48 83 c4 18                  	addq	$0x18, %rsp
    3a7b: c3                           	retq
    3a7c: e8 9f f7 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3a81: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    3a86: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003a90 <ivi_layout_get_layer_from_id>:
    3a90: 48 8d 15 81 d8 20 00         	leaq	0x20d881(%rip), %rdx    # 0x211318 <ivilayout+0x18>
    3a97: 48 83 ec 18                  	subq	$0x18, %rsp
    3a9b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3aa4: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3aa9: 31 c0                        	xorl	%eax, %eax
    3aab: 48 8b 05 6e d8 20 00         	movq	0x20d86e(%rip), %rax    # 0x211320 <ivilayout+0x20>
    3ab2: 48 39 d0                     	cmpq	%rdx, %rax
    3ab5: 74 17                        	je	0x3ace <ivi_layout_get_layer_from_id+0x3e>
    3ab7: 3b 78 20                     	cmpl	0x20(%rax), %edi
    3aba: 75 09                        	jne	0x3ac5 <ivi_layout_get_layer_from_id+0x35>
    3abc: eb 12                        	jmp	0x3ad0 <ivi_layout_get_layer_from_id+0x40>
    3abe: 66 90                        	nop
    3ac0: 39 78 20                     	cmpl	%edi, 0x20(%rax)
    3ac3: 74 0b                        	je	0x3ad0 <ivi_layout_get_layer_from_id+0x40>
    3ac5: 48 8b 40 08                  	movq	0x8(%rax), %rax
    3ac9: 48 39 d0                     	cmpq	%rdx, %rax
    3acc: 75 f2                        	jne	0x3ac0 <ivi_layout_get_layer_from_id+0x30>
    3ace: 31 c0                        	xorl	%eax, %eax
    3ad0: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    3ad5: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    3ade: 75 05                        	jne	0x3ae5 <ivi_layout_get_layer_from_id+0x55>
    3ae0: 48 83 c4 18                  	addq	$0x18, %rsp
    3ae4: c3                           	retq
    3ae5: e8 36 f7 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3aea: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000003af0 <ivi_layout_get_surface_from_id>:
    3af0: 48 8d 15 11 d8 20 00         	leaq	0x20d811(%rip), %rdx    # 0x211308 <ivilayout+0x8>
    3af7: 48 83 ec 18                  	subq	$0x18, %rsp
    3afb: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3b04: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3b09: 31 c0                        	xorl	%eax, %eax
    3b0b: 48 8b 05 fe d7 20 00         	movq	0x20d7fe(%rip), %rax    # 0x211310 <ivilayout+0x10>
    3b12: 48 39 d0                     	cmpq	%rdx, %rax
    3b15: 74 17                        	je	0x3b2e <ivi_layout_get_surface_from_id+0x3e>
    3b17: 3b 78 24                     	cmpl	0x24(%rax), %edi
    3b1a: 75 09                        	jne	0x3b25 <ivi_layout_get_surface_from_id+0x35>
    3b1c: eb 12                        	jmp	0x3b30 <ivi_layout_get_surface_from_id+0x40>
    3b1e: 66 90                        	nop
    3b20: 39 78 24                     	cmpl	%edi, 0x24(%rax)
    3b23: 74 0b                        	je	0x3b30 <ivi_layout_get_surface_from_id+0x40>
    3b25: 48 8b 40 08                  	movq	0x8(%rax), %rax
    3b29: 48 39 d0                     	cmpq	%rdx, %rax
    3b2c: 75 f2                        	jne	0x3b20 <ivi_layout_get_surface_from_id+0x30>
    3b2e: 31 c0                        	xorl	%eax, %eax
    3b30: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    3b35: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    3b3e: 75 05                        	jne	0x3b45 <ivi_layout_get_surface_from_id+0x55>
    3b40: 48 83 c4 18                  	addq	$0x18, %rsp
    3b44: c3                           	retq
    3b45: e8 d6 f6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3b4a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000003b50 <ivi_layout_get_screen_from_id>:
    3b50: 48 8d 15 d1 d7 20 00         	leaq	0x20d7d1(%rip), %rdx    # 0x211328 <ivilayout+0x28>
    3b57: 48 83 ec 18                  	subq	$0x18, %rsp
    3b5b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3b64: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3b69: 31 c0                        	xorl	%eax, %eax
    3b6b: 48 8b 05 be d7 20 00         	movq	0x20d7be(%rip), %rax    # 0x211330 <ivilayout+0x30>
    3b72: 48 39 d0                     	cmpq	%rdx, %rax
    3b75: 74 17                        	je	0x3b8e <ivi_layout_get_screen_from_id+0x3e>
    3b77: 3b 78 10                     	cmpl	0x10(%rax), %edi
    3b7a: 75 09                        	jne	0x3b85 <ivi_layout_get_screen_from_id+0x35>
    3b7c: eb 12                        	jmp	0x3b90 <ivi_layout_get_screen_from_id+0x40>
    3b7e: 66 90                        	nop
    3b80: 39 78 10                     	cmpl	%edi, 0x10(%rax)
    3b83: 74 0b                        	je	0x3b90 <ivi_layout_get_screen_from_id+0x40>
    3b85: 48 8b 40 08                  	movq	0x8(%rax), %rax
    3b89: 48 39 d0                     	cmpq	%rdx, %rax
    3b8c: 75 f2                        	jne	0x3b80 <ivi_layout_get_screen_from_id+0x30>
    3b8e: 31 c0                        	xorl	%eax, %eax
    3b90: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    3b95: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    3b9e: 75 05                        	jne	0x3ba5 <ivi_layout_get_screen_from_id+0x55>
    3ba0: 48 83 c4 18                  	addq	$0x18, %rsp
    3ba4: c3                           	retq
    3ba5: e8 76 f6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3baa: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000003bb0 <ivi_layout_screen_get_output>:
    3bb0: 48 83 ec 18                  	subq	$0x18, %rsp
    3bb4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3bbd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3bc2: 31 c0                        	xorl	%eax, %eax
    3bc4: 48 8b 47 20                  	movq	0x20(%rdi), %rax
    3bc8: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3bcd: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3bd6: 75 05                        	jne	0x3bdd <ivi_layout_screen_get_output+0x2d>
    3bd8: 48 83 c4 18                  	addq	$0x18, %rsp
    3bdc: c3                           	retq
    3bdd: e8 3e f6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3be2: 0f 1f 40 00                  	nopl	(%rax)
    3be6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003bf0 <ivi_layout_surface_get_weston_surface>:
    3bf0: 48 83 ec 18                  	subq	$0x18, %rsp
    3bf4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3bfd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3c02: 31 c0                        	xorl	%eax, %eax
    3c04: 48 85 ff                     	testq	%rdi, %rdi
    3c07: 74 1f                        	je	0x3c28 <ivi_layout_surface_get_weston_surface+0x38>
    3c09: 48 8b 47 38                  	movq	0x38(%rdi), %rax
    3c0d: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3c12: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3c1b: 75 0f                        	jne	0x3c2c <ivi_layout_surface_get_weston_surface+0x3c>
    3c1d: 48 83 c4 18                  	addq	$0x18, %rsp
    3c21: c3                           	retq
    3c22: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    3c28: 31 c0                        	xorl	%eax, %eax
    3c2a: eb e1                        	jmp	0x3c0d <ivi_layout_surface_get_weston_surface+0x1d>
    3c2c: e8 ef f5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3c31: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    3c36: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003c40 <ivi_layout_surface_set_content_observer>:
    3c40: 48 83 ec 18                  	subq	$0x18, %rsp
    3c44: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3c4d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3c52: 31 c0                        	xorl	%eax, %eax
    3c54: 48 85 ff                     	testq	%rdi, %rdi
    3c57: 74 23                        	je	0x3c7c <ivi_layout_surface_set_content_observer+0x3c>
    3c59: 48 89 b7 58 01 00 00         	movq	%rsi, 0x158(%rdi)
    3c60: 48 89 97 60 01 00 00         	movq	%rdx, 0x160(%rdi)
    3c67: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    3c6c: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    3c75: 75 0c                        	jne	0x3c83 <ivi_layout_surface_set_content_observer+0x43>
    3c77: 48 83 c4 18                  	addq	$0x18, %rsp
    3c7b: c3                           	retq
    3c7c: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    3c81: eb e4                        	jmp	0x3c67 <ivi_layout_surface_set_content_observer+0x27>
    3c83: e8 98 f5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3c88: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

0000000000003c90 <ivi_layout_layer_set_visibility>:
    3c90: 48 83 ec 18                  	subq	$0x18, %rsp
    3c94: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3c9d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3ca2: 31 c0                        	xorl	%eax, %eax
    3ca4: 48 85 ff                     	testq	%rdi, %rdi
    3ca7: 74 45                        	je	0x3cee <ivi_layout_layer_set_visibility+0x5e>
    3ca9: 40 0f b6 f6                  	movzbl	%sil, %esi
    3cad: 89 b7 b8 00 00 00            	movl	%esi, 0xb8(%rdi)
    3cb3: 3b 77 60                     	cmpl	0x60(%rdi), %esi
    3cb6: 74 28                        	je	0x3ce0 <ivi_layout_layer_set_visibility+0x50>
    3cb8: 81 8f 88 00 00 00 80 00 00 00	orl	$0x80, 0x88(%rdi)
    3cc2: 31 c0                        	xorl	%eax, %eax
    3cc4: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3cc9: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3cd2: 75 2d                        	jne	0x3d01 <ivi_layout_layer_set_visibility+0x71>
    3cd4: 48 83 c4 18                  	addq	$0x18, %rsp
    3cd8: c3                           	retq
    3cd9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    3ce0: 81 a7 88 00 00 00 7f ff ff ff	andl	$0xffffff7f, 0x88(%rdi) # imm = 0xFFFFFF7F
    3cea: 31 c0                        	xorl	%eax, %eax
    3cec: eb d6                        	jmp	0x3cc4 <ivi_layout_layer_set_visibility+0x34>
    3cee: 48 8d 3d ab 8a 00 00         	leaq	0x8aab(%rip), %rdi      # 0xc7a0 <zwp_input_panel_v1_interface+0xc7a0>
    3cf5: e8 16 f5 ff ff               	callq	0x3210 <weston_log@plt>
    3cfa: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    3cff: eb c3                        	jmp	0x3cc4 <ivi_layout_layer_set_visibility+0x34>
    3d01: e8 1a f5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3d06: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003d10 <ivi_layout_layer_set_opacity>:
    3d10: 48 83 ec 18                  	subq	$0x18, %rsp
    3d14: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3d1d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3d22: 31 c0                        	xorl	%eax, %eax
    3d24: 48 85 ff                     	testq	%rdi, %rdi
    3d27: 74 47                        	je	0x3d70 <ivi_layout_layer_set_opacity+0x60>
    3d29: 81 fe 00 01 00 00            	cmpl	$0x100, %esi            # imm = 0x100
    3d2f: 77 3f                        	ja	0x3d70 <ivi_layout_layer_set_opacity+0x60>
    3d31: 89 b7 90 00 00 00            	movl	%esi, 0x90(%rdi)
    3d37: 3b 77 38                     	cmpl	0x38(%rdi), %esi
    3d3a: 74 24                        	je	0x3d60 <ivi_layout_layer_set_opacity+0x50>
    3d3c: 83 8f 88 00 00 00 02         	orl	$0x2, 0x88(%rdi)
    3d43: 31 c0                        	xorl	%eax, %eax
    3d45: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3d4a: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3d53: 75 30                        	jne	0x3d85 <ivi_layout_layer_set_opacity+0x75>
    3d55: 48 83 c4 18                  	addq	$0x18, %rsp
    3d59: c3                           	retq
    3d5a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    3d60: 83 a7 88 00 00 00 fd         	andl	$-0x3, 0x88(%rdi)
    3d67: 31 c0                        	xorl	%eax, %eax
    3d69: eb da                        	jmp	0x3d45 <ivi_layout_layer_set_opacity+0x35>
    3d6b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    3d70: 48 8d 3d 61 8a 00 00         	leaq	0x8a61(%rip), %rdi      # 0xc7d8 <zwp_input_panel_v1_interface+0xc7d8>
    3d77: 31 c0                        	xorl	%eax, %eax
    3d79: e8 92 f4 ff ff               	callq	0x3210 <weston_log@plt>
    3d7e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    3d83: eb c0                        	jmp	0x3d45 <ivi_layout_layer_set_opacity+0x35>
    3d85: e8 96 f4 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3d8a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000003d90 <ivi_layout_layer_get_opacity>:
    3d90: 48 83 ec 18                  	subq	$0x18, %rsp
    3d94: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3d9d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3da2: 31 c0                        	xorl	%eax, %eax
    3da4: 48 85 ff                     	testq	%rdi, %rdi
    3da7: 74 1f                        	je	0x3dc8 <ivi_layout_layer_get_opacity+0x38>
    3da9: 8b 47 38                     	movl	0x38(%rdi), %eax
    3dac: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3db1: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3dba: 75 1c                        	jne	0x3dd8 <ivi_layout_layer_get_opacity+0x48>
    3dbc: 48 83 c4 18                  	addq	$0x18, %rsp
    3dc0: c3                           	retq
    3dc1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    3dc8: 48 8d 3d 39 8a 00 00         	leaq	0x8a39(%rip), %rdi      # 0xc808 <zwp_input_panel_v1_interface+0xc808>
    3dcf: e8 3c f4 ff ff               	callq	0x3210 <weston_log@plt>
    3dd4: 31 c0                        	xorl	%eax, %eax
    3dd6: eb d4                        	jmp	0x3dac <ivi_layout_layer_get_opacity+0x1c>
    3dd8: e8 43 f4 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3ddd: 0f 1f 00                     	nopl	(%rax)

0000000000003de0 <ivi_layout_layer_get_position>:
    3de0: 48 83 ec 18                  	subq	$0x18, %rsp
    3de4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3ded: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3df2: 31 c0                        	xorl	%eax, %eax
    3df4: 48 85 f6                     	testq	%rsi, %rsi
    3df7: 0f 94 c1                     	sete	%cl
    3dfa: 48 85 d2                     	testq	%rdx, %rdx
    3dfd: 0f 94 c0                     	sete	%al
    3e00: 08 c1                        	orb	%al, %cl
    3e02: 75 26                        	jne	0x3e2a <ivi_layout_layer_get_position+0x4a>
    3e04: 48 85 ff                     	testq	%rdi, %rdi
    3e07: 74 21                        	je	0x3e2a <ivi_layout_layer_get_position+0x4a>
    3e09: 8b 47 4c                     	movl	0x4c(%rdi), %eax
    3e0c: 89 06                        	movl	%eax, (%rsi)
    3e0e: 8b 47 50                     	movl	0x50(%rdi), %eax
    3e11: 89 02                        	movl	%eax, (%rdx)
    3e13: 31 c0                        	xorl	%eax, %eax
    3e15: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3e1a: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3e23: 75 1a                        	jne	0x3e3f <ivi_layout_layer_get_position+0x5f>
    3e25: 48 83 c4 18                  	addq	$0x18, %rsp
    3e29: c3                           	retq
    3e2a: 48 8d 3d 07 8a 00 00         	leaq	0x8a07(%rip), %rdi      # 0xc838 <zwp_input_panel_v1_interface+0xc838>
    3e31: 31 c0                        	xorl	%eax, %eax
    3e33: e8 d8 f3 ff ff               	callq	0x3210 <weston_log@plt>
    3e38: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    3e3d: eb d6                        	jmp	0x3e15 <ivi_layout_layer_get_position+0x35>
    3e3f: e8 dc f3 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3e44: 66 90                        	nop
    3e46: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003e50 <ivi_layout_layer_set_position>:
    3e50: 48 83 ec 18                  	subq	$0x18, %rsp
    3e54: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3e5d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3e62: 31 c0                        	xorl	%eax, %eax
    3e64: 48 85 ff                     	testq	%rdi, %rdi
    3e67: 74 47                        	je	0x3eb0 <ivi_layout_layer_set_position+0x60>
    3e69: 89 b7 a4 00 00 00            	movl	%esi, 0xa4(%rdi)
    3e6f: 89 97 a8 00 00 00            	movl	%edx, 0xa8(%rdi)
    3e75: 3b 77 4c                     	cmpl	0x4c(%rdi), %esi
    3e78: 74 26                        	je	0x3ea0 <ivi_layout_layer_set_position+0x50>
    3e7a: 83 8f 88 00 00 00 20         	orl	$0x20, 0x88(%rdi)
    3e81: 31 c0                        	xorl	%eax, %eax
    3e83: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    3e88: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    3e91: 75 30                        	jne	0x3ec3 <ivi_layout_layer_set_position+0x73>
    3e93: 48 83 c4 18                  	addq	$0x18, %rsp
    3e97: c3                           	retq
    3e98: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    3ea0: 3b 57 50                     	cmpl	0x50(%rdi), %edx
    3ea3: 75 d5                        	jne	0x3e7a <ivi_layout_layer_set_position+0x2a>
    3ea5: 83 a7 88 00 00 00 df         	andl	$-0x21, 0x88(%rdi)
    3eac: 31 c0                        	xorl	%eax, %eax
    3eae: eb d3                        	jmp	0x3e83 <ivi_layout_layer_set_position+0x33>
    3eb0: 48 8d 3d b9 89 00 00         	leaq	0x89b9(%rip), %rdi      # 0xc870 <zwp_input_panel_v1_interface+0xc870>
    3eb7: e8 54 f3 ff ff               	callq	0x3210 <weston_log@plt>
    3ebc: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    3ec1: eb c0                        	jmp	0x3e83 <ivi_layout_layer_set_position+0x33>
    3ec3: e8 58 f3 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3ec8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

0000000000003ed0 <ivi_layout_surface_set_visibility>:
    3ed0: 48 83 ec 18                  	subq	$0x18, %rsp
    3ed4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3edd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3ee2: 31 c0                        	xorl	%eax, %eax
    3ee4: 48 85 ff                     	testq	%rdi, %rdi
    3ee7: 74 45                        	je	0x3f2e <ivi_layout_surface_set_visibility+0x5e>
    3ee9: 40 88 b7 18 01 00 00         	movb	%sil, 0x118(%rdi)
    3ef0: 40 3a b7 d0 00 00 00         	cmpb	0xd0(%rdi), %sil
    3ef7: 74 27                        	je	0x3f20 <ivi_layout_surface_set_visibility+0x50>
    3ef9: 81 8f dc 00 00 00 80 00 00 00	orl	$0x80, 0xdc(%rdi)
    3f03: 31 c0                        	xorl	%eax, %eax
    3f05: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3f0a: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3f13: 75 2c                        	jne	0x3f41 <ivi_layout_surface_set_visibility+0x71>
    3f15: 48 83 c4 18                  	addq	$0x18, %rsp
    3f19: c3                           	retq
    3f1a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    3f20: 81 a7 dc 00 00 00 7f ff ff ff	andl	$0xffffff7f, 0xdc(%rdi) # imm = 0xFFFFFF7F
    3f2a: 31 c0                        	xorl	%eax, %eax
    3f2c: eb d7                        	jmp	0x3f05 <ivi_layout_surface_set_visibility+0x35>
    3f2e: 48 8d 3d 73 89 00 00         	leaq	0x8973(%rip), %rdi      # 0xc8a8 <zwp_input_panel_v1_interface+0xc8a8>
    3f35: e8 d6 f2 ff ff               	callq	0x3210 <weston_log@plt>
    3f3a: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    3f3f: eb c4                        	jmp	0x3f05 <ivi_layout_surface_set_visibility+0x35>
    3f41: e8 da f2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3f46: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000003f50 <ivi_layout_surface_get_visibility>:
    3f50: 48 83 ec 18                  	subq	$0x18, %rsp
    3f54: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3f5d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3f62: 31 c0                        	xorl	%eax, %eax
    3f64: 48 85 ff                     	testq	%rdi, %rdi
    3f67: 74 1f                        	je	0x3f88 <ivi_layout_surface_get_visibility+0x38>
    3f69: 0f b6 87 d0 00 00 00         	movzbl	0xd0(%rdi), %eax
    3f70: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3f75: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3f7e: 75 18                        	jne	0x3f98 <ivi_layout_surface_get_visibility+0x48>
    3f80: 48 83 c4 18                  	addq	$0x18, %rsp
    3f84: c3                           	retq
    3f85: 0f 1f 00                     	nopl	(%rax)
    3f88: 48 8d 3d 51 89 00 00         	leaq	0x8951(%rip), %rdi      # 0xc8e0 <zwp_input_panel_v1_interface+0xc8e0>
    3f8f: e8 7c f2 ff ff               	callq	0x3210 <weston_log@plt>
    3f94: 31 c0                        	xorl	%eax, %eax
    3f96: eb d8                        	jmp	0x3f70 <ivi_layout_surface_get_visibility+0x20>
    3f98: e8 83 f2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    3f9d: 0f 1f 00                     	nopl	(%rax)

0000000000003fa0 <ivi_layout_surface_set_opacity>:
    3fa0: 48 83 ec 18                  	subq	$0x18, %rsp
    3fa4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    3fad: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    3fb2: 31 c0                        	xorl	%eax, %eax
    3fb4: 48 85 ff                     	testq	%rdi, %rdi
    3fb7: 74 47                        	je	0x4000 <ivi_layout_surface_set_opacity+0x60>
    3fb9: 81 fe 00 01 00 00            	cmpl	$0x100, %esi            # imm = 0x100
    3fbf: 77 3f                        	ja	0x4000 <ivi_layout_surface_set_opacity+0x60>
    3fc1: 89 b7 e0 00 00 00            	movl	%esi, 0xe0(%rdi)
    3fc7: 3b b7 98 00 00 00            	cmpl	0x98(%rdi), %esi
    3fcd: 74 21                        	je	0x3ff0 <ivi_layout_surface_set_opacity+0x50>
    3fcf: 83 8f dc 00 00 00 02         	orl	$0x2, 0xdc(%rdi)
    3fd6: 31 c0                        	xorl	%eax, %eax
    3fd8: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    3fdd: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    3fe6: 75 2d                        	jne	0x4015 <ivi_layout_surface_set_opacity+0x75>
    3fe8: 48 83 c4 18                  	addq	$0x18, %rsp
    3fec: c3                           	retq
    3fed: 0f 1f 00                     	nopl	(%rax)
    3ff0: 83 a7 dc 00 00 00 fd         	andl	$-0x3, 0xdc(%rdi)
    3ff7: 31 c0                        	xorl	%eax, %eax
    3ff9: eb dd                        	jmp	0x3fd8 <ivi_layout_surface_set_opacity+0x38>
    3ffb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    4000: 48 8d 3d 11 89 00 00         	leaq	0x8911(%rip), %rdi      # 0xc918 <zwp_input_panel_v1_interface+0xc918>
    4007: 31 c0                        	xorl	%eax, %eax
    4009: e8 02 f2 ff ff               	callq	0x3210 <weston_log@plt>
    400e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4013: eb c3                        	jmp	0x3fd8 <ivi_layout_surface_set_opacity+0x38>
    4015: e8 06 f2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    401a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000004020 <ivi_layout_surface_get_opacity>:
    4020: 48 83 ec 18                  	subq	$0x18, %rsp
    4024: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    402d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4032: 31 c0                        	xorl	%eax, %eax
    4034: 48 85 ff                     	testq	%rdi, %rdi
    4037: 74 1f                        	je	0x4058 <ivi_layout_surface_get_opacity+0x38>
    4039: 8b 87 98 00 00 00            	movl	0x98(%rdi), %eax
    403f: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4044: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    404d: 75 19                        	jne	0x4068 <ivi_layout_surface_get_opacity+0x48>
    404f: 48 83 c4 18                  	addq	$0x18, %rsp
    4053: c3                           	retq
    4054: 0f 1f 40 00                  	nopl	(%rax)
    4058: 48 8d 3d f1 88 00 00         	leaq	0x88f1(%rip), %rdi      # 0xc950 <zwp_input_panel_v1_interface+0xc950>
    405f: e8 ac f1 ff ff               	callq	0x3210 <weston_log@plt>
    4064: 31 c0                        	xorl	%eax, %eax
    4066: eb d7                        	jmp	0x403f <ivi_layout_surface_get_opacity+0x1f>
    4068: e8 b3 f1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    406d: 0f 1f 00                     	nopl	(%rax)

0000000000004070 <ivi_layout_surface_set_destination_rectangle>:
    4070: 48 83 ec 18                  	subq	$0x18, %rsp
    4074: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    407d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4082: 31 c0                        	xorl	%eax, %eax
    4084: 48 85 ff                     	testq	%rdi, %rdi
    4087: 0f 84 97 00 00 00            	je	0x4124 <ivi_layout_surface_set_destination_rectangle+0xb4>
    408d: 8b 87 04 01 00 00            	movl	0x104(%rdi), %eax
    4093: 89 b7 04 01 00 00            	movl	%esi, 0x104(%rdi)
    4099: 89 87 f4 00 00 00            	movl	%eax, 0xf4(%rdi)
    409f: 8b 87 08 01 00 00            	movl	0x108(%rdi), %eax
    40a5: 89 97 08 01 00 00            	movl	%edx, 0x108(%rdi)
    40ab: 89 87 f8 00 00 00            	movl	%eax, 0xf8(%rdi)
    40b1: 8b 87 0c 01 00 00            	movl	0x10c(%rdi), %eax
    40b7: 89 8f 0c 01 00 00            	movl	%ecx, 0x10c(%rdi)
    40bd: 89 87 fc 00 00 00            	movl	%eax, 0xfc(%rdi)
    40c3: 8b 87 10 01 00 00            	movl	0x110(%rdi), %eax
    40c9: 44 89 87 10 01 00 00         	movl	%r8d, 0x110(%rdi)
    40d0: 89 87 00 01 00 00            	movl	%eax, 0x100(%rdi)
    40d6: 3b b7 bc 00 00 00            	cmpl	0xbc(%rdi), %esi
    40dc: 74 22                        	je	0x4100 <ivi_layout_surface_set_destination_rectangle+0x90>
    40de: 83 8f dc 00 00 00 08         	orl	$0x8, 0xdc(%rdi)
    40e5: 31 c0                        	xorl	%eax, %eax
    40e7: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    40ec: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    40f5: 75 40                        	jne	0x4137 <ivi_layout_surface_set_destination_rectangle+0xc7>
    40f7: 48 83 c4 18                  	addq	$0x18, %rsp
    40fb: c3                           	retq
    40fc: 0f 1f 40 00                  	nopl	(%rax)
    4100: 3b 97 c0 00 00 00            	cmpl	0xc0(%rdi), %edx
    4106: 75 d6                        	jne	0x40de <ivi_layout_surface_set_destination_rectangle+0x6e>
    4108: 3b 8f c4 00 00 00            	cmpl	0xc4(%rdi), %ecx
    410e: 75 ce                        	jne	0x40de <ivi_layout_surface_set_destination_rectangle+0x6e>
    4110: 44 3b 87 c8 00 00 00         	cmpl	0xc8(%rdi), %r8d
    4117: 75 c5                        	jne	0x40de <ivi_layout_surface_set_destination_rectangle+0x6e>
    4119: 83 a7 dc 00 00 00 f7         	andl	$-0x9, 0xdc(%rdi)
    4120: 31 c0                        	xorl	%eax, %eax
    4122: eb c3                        	jmp	0x40e7 <ivi_layout_surface_set_destination_rectangle+0x77>
    4124: 48 8d 3d 5d 88 00 00         	leaq	0x885d(%rip), %rdi      # 0xc988 <zwp_input_panel_v1_interface+0xc988>
    412b: e8 e0 f0 ff ff               	callq	0x3210 <weston_log@plt>
    4130: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4135: eb b0                        	jmp	0x40e7 <ivi_layout_surface_set_destination_rectangle+0x77>
    4137: e8 e4 f0 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    413c: 0f 1f 40 00                  	nopl	(%rax)

0000000000004140 <ivi_layout_surface_get_dimension>:
    4140: 48 83 ec 18                  	subq	$0x18, %rsp
    4144: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    414d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4152: 31 c0                        	xorl	%eax, %eax
    4154: 48 85 f6                     	testq	%rsi, %rsi
    4157: 0f 94 c1                     	sete	%cl
    415a: 48 85 d2                     	testq	%rdx, %rdx
    415d: 0f 94 c0                     	sete	%al
    4160: 08 c1                        	orb	%al, %cl
    4162: 75 2c                        	jne	0x4190 <ivi_layout_surface_get_dimension+0x50>
    4164: 48 85 ff                     	testq	%rdi, %rdi
    4167: 74 27                        	je	0x4190 <ivi_layout_surface_get_dimension+0x50>
    4169: 8b 87 c4 00 00 00            	movl	0xc4(%rdi), %eax
    416f: 89 06                        	movl	%eax, (%rsi)
    4171: 8b 87 c8 00 00 00            	movl	0xc8(%rdi), %eax
    4177: 89 02                        	movl	%eax, (%rdx)
    4179: 31 c0                        	xorl	%eax, %eax
    417b: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4180: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    4189: 75 1a                        	jne	0x41a5 <ivi_layout_surface_get_dimension+0x65>
    418b: 48 83 c4 18                  	addq	$0x18, %rsp
    418f: c3                           	retq
    4190: 48 8d 3d 31 88 00 00         	leaq	0x8831(%rip), %rdi      # 0xc9c8 <zwp_input_panel_v1_interface+0xc9c8>
    4197: 31 c0                        	xorl	%eax, %eax
    4199: e8 72 f0 ff ff               	callq	0x3210 <weston_log@plt>
    419e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    41a3: eb d6                        	jmp	0x417b <ivi_layout_surface_get_dimension+0x3b>
    41a5: e8 76 f0 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    41aa: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000000041b0 <ivi_layout_surface_set_source_rectangle>:
    41b0: 48 83 ec 18                  	subq	$0x18, %rsp
    41b4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    41bd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    41c2: 31 c0                        	xorl	%eax, %eax
    41c4: 48 85 ff                     	testq	%rdi, %rdi
    41c7: 74 6b                        	je	0x4234 <ivi_layout_surface_set_source_rectangle+0x84>
    41c9: 89 b7 e4 00 00 00            	movl	%esi, 0xe4(%rdi)
    41cf: 89 97 e8 00 00 00            	movl	%edx, 0xe8(%rdi)
    41d5: 89 8f ec 00 00 00            	movl	%ecx, 0xec(%rdi)
    41db: 44 89 87 f0 00 00 00         	movl	%r8d, 0xf0(%rdi)
    41e2: 3b b7 9c 00 00 00            	cmpl	0x9c(%rdi), %esi
    41e8: 74 26                        	je	0x4210 <ivi_layout_surface_set_source_rectangle+0x60>
    41ea: 83 8f dc 00 00 00 04         	orl	$0x4, 0xdc(%rdi)
    41f1: 31 c0                        	xorl	%eax, %eax
    41f3: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    41f8: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    4201: 75 44                        	jne	0x4247 <ivi_layout_surface_set_source_rectangle+0x97>
    4203: 48 83 c4 18                  	addq	$0x18, %rsp
    4207: c3                           	retq
    4208: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    4210: 3b 97 a0 00 00 00            	cmpl	0xa0(%rdi), %edx
    4216: 75 d2                        	jne	0x41ea <ivi_layout_surface_set_source_rectangle+0x3a>
    4218: 3b 8f a4 00 00 00            	cmpl	0xa4(%rdi), %ecx
    421e: 75 ca                        	jne	0x41ea <ivi_layout_surface_set_source_rectangle+0x3a>
    4220: 44 3b 87 a8 00 00 00         	cmpl	0xa8(%rdi), %r8d
    4227: 75 c1                        	jne	0x41ea <ivi_layout_surface_set_source_rectangle+0x3a>
    4229: 83 a7 dc 00 00 00 fb         	andl	$-0x5, 0xdc(%rdi)
    4230: 31 c0                        	xorl	%eax, %eax
    4232: eb bf                        	jmp	0x41f3 <ivi_layout_surface_set_source_rectangle+0x43>
    4234: 48 8d 3d c5 87 00 00         	leaq	0x87c5(%rip), %rdi      # 0xca00 <zwp_input_panel_v1_interface+0xca00>
    423b: e8 d0 ef ff ff               	callq	0x3210 <weston_log@plt>
    4240: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4245: eb ac                        	jmp	0x41f3 <ivi_layout_surface_set_source_rectangle+0x43>
    4247: e8 d4 ef ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    424c: 0f 1f 40 00                  	nopl	(%rax)

0000000000004250 <ivi_layout_get_screen_resolution>:
    4250: 48 83 ec 18                  	subq	$0x18, %rsp
    4254: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    425d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4262: 31 c0                        	xorl	%eax, %eax
    4264: 48 85 f6                     	testq	%rsi, %rsi
    4267: 0f 94 c1                     	sete	%cl
    426a: 48 85 d2                     	testq	%rdx, %rdx
    426d: 0f 94 c0                     	sete	%al
    4270: 08 c1                        	orb	%al, %cl
    4272: 75 30                        	jne	0x42a4 <ivi_layout_get_screen_resolution+0x54>
    4274: 48 85 ff                     	testq	%rdi, %rdi
    4277: 74 2b                        	je	0x42a4 <ivi_layout_get_screen_resolution+0x54>
    4279: 48 8b 47 20                  	movq	0x20(%rdi), %rax
    427d: 8b 88 e8 00 00 00            	movl	0xe8(%rax), %ecx
    4283: 89 0e                        	movl	%ecx, (%rsi)
    4285: 8b 80 ec 00 00 00            	movl	0xec(%rax), %eax
    428b: 89 02                        	movl	%eax, (%rdx)
    428d: 31 c0                        	xorl	%eax, %eax
    428f: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4294: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    429d: 75 1a                        	jne	0x42b9 <ivi_layout_get_screen_resolution+0x69>
    429f: 48 83 c4 18                  	addq	$0x18, %rsp
    42a3: c3                           	retq
    42a4: 48 8d 3d 95 87 00 00         	leaq	0x8795(%rip), %rdi      # 0xca40 <zwp_input_panel_v1_interface+0xca40>
    42ab: 31 c0                        	xorl	%eax, %eax
    42ad: e8 5e ef ff ff               	callq	0x3210 <weston_log@plt>
    42b2: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    42b7: eb d6                        	jmp	0x428f <ivi_layout_get_screen_resolution+0x3f>
    42b9: e8 62 ef ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    42be: 66 90                        	nop

00000000000042c0 <ivi_layout_layer_get_orientation>:
    42c0: 48 83 ec 18                  	subq	$0x18, %rsp
    42c4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    42cd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    42d2: 31 c0                        	xorl	%eax, %eax
    42d4: 48 85 ff                     	testq	%rdi, %rdi
    42d7: 74 1f                        	je	0x42f8 <ivi_layout_layer_get_orientation+0x38>
    42d9: 8b 47 5c                     	movl	0x5c(%rdi), %eax
    42dc: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    42e1: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    42ea: 75 1c                        	jne	0x4308 <ivi_layout_layer_get_orientation+0x48>
    42ec: 48 83 c4 18                  	addq	$0x18, %rsp
    42f0: c3                           	retq
    42f1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    42f8: 48 8d 3d 79 87 00 00         	leaq	0x8779(%rip), %rdi      # 0xca78 <zwp_input_panel_v1_interface+0xca78>
    42ff: e8 0c ef ff ff               	callq	0x3210 <weston_log@plt>
    4304: 31 c0                        	xorl	%eax, %eax
    4306: eb d4                        	jmp	0x42dc <ivi_layout_layer_get_orientation+0x1c>
    4308: e8 13 ef ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    430d: 0f 1f 00                     	nopl	(%rax)

0000000000004310 <ivi_layout_layer_set_orientation>:
    4310: 48 83 ec 18                  	subq	$0x18, %rsp
    4314: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    431d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4322: 31 c0                        	xorl	%eax, %eax
    4324: 48 85 ff                     	testq	%rdi, %rdi
    4327: 74 3a                        	je	0x4363 <ivi_layout_layer_set_orientation+0x53>
    4329: 89 b7 b4 00 00 00            	movl	%esi, 0xb4(%rdi)
    432f: 3b 77 5c                     	cmpl	0x5c(%rdi), %esi
    4332: 74 24                        	je	0x4358 <ivi_layout_layer_set_orientation+0x48>
    4334: 83 8f 88 00 00 00 40         	orl	$0x40, 0x88(%rdi)
    433b: 31 c0                        	xorl	%eax, %eax
    433d: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4342: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    434b: 75 29                        	jne	0x4376 <ivi_layout_layer_set_orientation+0x66>
    434d: 48 83 c4 18                  	addq	$0x18, %rsp
    4351: c3                           	retq
    4352: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    4358: 83 a7 88 00 00 00 bf         	andl	$-0x41, 0x88(%rdi)
    435f: 31 c0                        	xorl	%eax, %eax
    4361: eb da                        	jmp	0x433d <ivi_layout_layer_set_orientation+0x2d>
    4363: 48 8d 3d 46 87 00 00         	leaq	0x8746(%rip), %rdi      # 0xcab0 <zwp_input_panel_v1_interface+0xcab0>
    436a: e8 a1 ee ff ff               	callq	0x3210 <weston_log@plt>
    436f: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4374: eb c7                        	jmp	0x433d <ivi_layout_layer_set_orientation+0x2d>
    4376: e8 a5 ee ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    437b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000004380 <ivi_layout_layer_get_dimension>:
    4380: 48 83 ec 18                  	subq	$0x18, %rsp
    4384: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    438d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4392: 31 c0                        	xorl	%eax, %eax
    4394: 48 85 f6                     	testq	%rsi, %rsi
    4397: 0f 94 c1                     	sete	%cl
    439a: 48 85 d2                     	testq	%rdx, %rdx
    439d: 0f 94 c0                     	sete	%al
    43a0: 08 c1                        	orb	%al, %cl
    43a2: 75 26                        	jne	0x43ca <ivi_layout_layer_get_dimension+0x4a>
    43a4: 48 85 ff                     	testq	%rdi, %rdi
    43a7: 74 21                        	je	0x43ca <ivi_layout_layer_get_dimension+0x4a>
    43a9: 8b 47 54                     	movl	0x54(%rdi), %eax
    43ac: 89 06                        	movl	%eax, (%rsi)
    43ae: 8b 47 58                     	movl	0x58(%rdi), %eax
    43b1: 89 02                        	movl	%eax, (%rdx)
    43b3: 31 c0                        	xorl	%eax, %eax
    43b5: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    43ba: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    43c3: 75 1a                        	jne	0x43df <ivi_layout_layer_get_dimension+0x5f>
    43c5: 48 83 c4 18                  	addq	$0x18, %rsp
    43c9: c3                           	retq
    43ca: 48 8d 3d 17 87 00 00         	leaq	0x8717(%rip), %rdi      # 0xcae8 <zwp_input_panel_v1_interface+0xcae8>
    43d1: 31 c0                        	xorl	%eax, %eax
    43d3: e8 38 ee ff ff               	callq	0x3210 <weston_log@plt>
    43d8: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    43dd: eb d6                        	jmp	0x43b5 <ivi_layout_layer_get_dimension+0x35>
    43df: e8 3c ee ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    43e4: 66 90                        	nop
    43e6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000043f0 <ivi_layout_layer_set_dimension>:
    43f0: 48 83 ec 18                  	subq	$0x18, %rsp
    43f4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    43fd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4402: 31 c0                        	xorl	%eax, %eax
    4404: 48 85 ff                     	testq	%rdi, %rdi
    4407: 74 47                        	je	0x4450 <ivi_layout_layer_set_dimension+0x60>
    4409: 89 b7 ac 00 00 00            	movl	%esi, 0xac(%rdi)
    440f: 89 97 b0 00 00 00            	movl	%edx, 0xb0(%rdi)
    4415: 3b 77 54                     	cmpl	0x54(%rdi), %esi
    4418: 74 26                        	je	0x4440 <ivi_layout_layer_set_dimension+0x50>
    441a: 83 8f 88 00 00 00 10         	orl	$0x10, 0x88(%rdi)
    4421: 31 c0                        	xorl	%eax, %eax
    4423: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    4428: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    4431: 75 30                        	jne	0x4463 <ivi_layout_layer_set_dimension+0x73>
    4433: 48 83 c4 18                  	addq	$0x18, %rsp
    4437: c3                           	retq
    4438: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    4440: 3b 57 58                     	cmpl	0x58(%rdi), %edx
    4443: 75 d5                        	jne	0x441a <ivi_layout_layer_set_dimension+0x2a>
    4445: 83 a7 88 00 00 00 ef         	andl	$-0x11, 0x88(%rdi)
    444c: 31 c0                        	xorl	%eax, %eax
    444e: eb d3                        	jmp	0x4423 <ivi_layout_layer_set_dimension+0x33>
    4450: 48 8d 3d c9 86 00 00         	leaq	0x86c9(%rip), %rdi      # 0xcb20 <zwp_input_panel_v1_interface+0xcb20>
    4457: e8 b4 ed ff ff               	callq	0x3210 <weston_log@plt>
    445c: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4461: eb c0                        	jmp	0x4423 <ivi_layout_layer_set_dimension+0x33>
    4463: e8 b8 ed ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4468: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

0000000000004470 <ivi_layout_layer_set_destination_rectangle>:
    4470: 48 83 ec 18                  	subq	$0x18, %rsp
    4474: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    447d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4482: 31 c0                        	xorl	%eax, %eax
    4484: 48 85 ff                     	testq	%rdi, %rdi
    4487: 74 5a                        	je	0x44e3 <ivi_layout_layer_set_destination_rectangle+0x73>
    4489: 89 b7 a4 00 00 00            	movl	%esi, 0xa4(%rdi)
    448f: 89 97 a8 00 00 00            	movl	%edx, 0xa8(%rdi)
    4495: 89 8f ac 00 00 00            	movl	%ecx, 0xac(%rdi)
    449b: 44 89 87 b0 00 00 00         	movl	%r8d, 0xb0(%rdi)
    44a2: 3b 77 4c                     	cmpl	0x4c(%rdi), %esi
    44a5: 74 21                        	je	0x44c8 <ivi_layout_layer_set_destination_rectangle+0x58>
    44a7: 83 8f 88 00 00 00 08         	orl	$0x8, 0x88(%rdi)
    44ae: 31 c0                        	xorl	%eax, %eax
    44b0: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    44b5: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    44be: 75 36                        	jne	0x44f6 <ivi_layout_layer_set_destination_rectangle+0x86>
    44c0: 48 83 c4 18                  	addq	$0x18, %rsp
    44c4: c3                           	retq
    44c5: 0f 1f 00                     	nopl	(%rax)
    44c8: 3b 57 50                     	cmpl	0x50(%rdi), %edx
    44cb: 75 da                        	jne	0x44a7 <ivi_layout_layer_set_destination_rectangle+0x37>
    44cd: 3b 4f 54                     	cmpl	0x54(%rdi), %ecx
    44d0: 75 d5                        	jne	0x44a7 <ivi_layout_layer_set_destination_rectangle+0x37>
    44d2: 44 3b 47 58                  	cmpl	0x58(%rdi), %r8d
    44d6: 75 cf                        	jne	0x44a7 <ivi_layout_layer_set_destination_rectangle+0x37>
    44d8: 83 a7 88 00 00 00 f7         	andl	$-0x9, 0x88(%rdi)
    44df: 31 c0                        	xorl	%eax, %eax
    44e1: eb cd                        	jmp	0x44b0 <ivi_layout_layer_set_destination_rectangle+0x40>
    44e3: 48 8d 3d 6e 86 00 00         	leaq	0x866e(%rip), %rdi      # 0xcb58 <zwp_input_panel_v1_interface+0xcb58>
    44ea: e8 21 ed ff ff               	callq	0x3210 <weston_log@plt>
    44ef: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    44f4: eb ba                        	jmp	0x44b0 <ivi_layout_layer_set_destination_rectangle+0x40>
    44f6: e8 25 ed ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    44fb: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000004500 <ivi_layout_layer_set_source_rectangle>:
    4500: 48 83 ec 18                  	subq	$0x18, %rsp
    4504: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    450d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4512: 31 c0                        	xorl	%eax, %eax
    4514: 48 85 ff                     	testq	%rdi, %rdi
    4517: 74 5a                        	je	0x4573 <ivi_layout_layer_set_source_rectangle+0x73>
    4519: 89 b7 94 00 00 00            	movl	%esi, 0x94(%rdi)
    451f: 89 97 98 00 00 00            	movl	%edx, 0x98(%rdi)
    4525: 89 8f 9c 00 00 00            	movl	%ecx, 0x9c(%rdi)
    452b: 44 89 87 a0 00 00 00         	movl	%r8d, 0xa0(%rdi)
    4532: 3b 77 3c                     	cmpl	0x3c(%rdi), %esi
    4535: 74 21                        	je	0x4558 <ivi_layout_layer_set_source_rectangle+0x58>
    4537: 83 8f 88 00 00 00 04         	orl	$0x4, 0x88(%rdi)
    453e: 31 c0                        	xorl	%eax, %eax
    4540: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    4545: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    454e: 75 36                        	jne	0x4586 <ivi_layout_layer_set_source_rectangle+0x86>
    4550: 48 83 c4 18                  	addq	$0x18, %rsp
    4554: c3                           	retq
    4555: 0f 1f 00                     	nopl	(%rax)
    4558: 3b 57 40                     	cmpl	0x40(%rdi), %edx
    455b: 75 da                        	jne	0x4537 <ivi_layout_layer_set_source_rectangle+0x37>
    455d: 3b 4f 44                     	cmpl	0x44(%rdi), %ecx
    4560: 75 d5                        	jne	0x4537 <ivi_layout_layer_set_source_rectangle+0x37>
    4562: 44 3b 47 48                  	cmpl	0x48(%rdi), %r8d
    4566: 75 cf                        	jne	0x4537 <ivi_layout_layer_set_source_rectangle+0x37>
    4568: 83 a7 88 00 00 00 fb         	andl	$-0x5, 0x88(%rdi)
    456f: 31 c0                        	xorl	%eax, %eax
    4571: eb cd                        	jmp	0x4540 <ivi_layout_layer_set_source_rectangle+0x40>
    4573: 48 8d 3d 1e 86 00 00         	leaq	0x861e(%rip), %rdi      # 0xcb98 <zwp_input_panel_v1_interface+0xcb98>
    457a: e8 91 ec ff ff               	callq	0x3210 <weston_log@plt>
    457f: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4584: eb ba                        	jmp	0x4540 <ivi_layout_layer_set_source_rectangle+0x40>
    4586: e8 95 ec ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    458b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000004590 <ivi_layout_layer_get_visibility>:
    4590: 48 83 ec 18                  	subq	$0x18, %rsp
    4594: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    459d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    45a2: 31 c0                        	xorl	%eax, %eax
    45a4: 48 85 ff                     	testq	%rdi, %rdi
    45a7: 74 27                        	je	0x45d0 <ivi_layout_layer_get_visibility+0x40>
    45a9: 8b 47 60                     	movl	0x60(%rdi), %eax
    45ac: 85 c0                        	testl	%eax, %eax
    45ae: 0f 95 c0                     	setne	%al
    45b1: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    45b6: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    45bf: 75 1f                        	jne	0x45e0 <ivi_layout_layer_get_visibility+0x50>
    45c1: 48 83 c4 18                  	addq	$0x18, %rsp
    45c5: c3                           	retq
    45c6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    45d0: 48 8d 3d 01 86 00 00         	leaq	0x8601(%rip), %rdi      # 0xcbd8 <zwp_input_panel_v1_interface+0xcbd8>
    45d7: e8 34 ec ff ff               	callq	0x3210 <weston_log@plt>
    45dc: 31 c0                        	xorl	%eax, %eax
    45de: eb d1                        	jmp	0x45b1 <ivi_layout_layer_get_visibility+0x21>
    45e0: e8 3b ec ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    45e5: 90                           	nop
    45e6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000045f0 <ivi_layout_get_properties_of_layer>:
    45f0: 48 83 ec 18                  	subq	$0x18, %rsp
    45f4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    45fd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4602: 31 c0                        	xorl	%eax, %eax
    4604: 48 85 ff                     	testq	%rdi, %rdi
    4607: 74 19                        	je	0x4622 <ivi_layout_get_properties_of_layer+0x32>
    4609: 48 8d 47 38                  	leaq	0x38(%rdi), %rax
    460d: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4612: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    461b: 75 15                        	jne	0x4632 <ivi_layout_get_properties_of_layer+0x42>
    461d: 48 83 c4 18                  	addq	$0x18, %rsp
    4621: c3                           	retq
    4622: 48 8d 3d e7 85 00 00         	leaq	0x85e7(%rip), %rdi      # 0xcc10 <zwp_input_panel_v1_interface+0xcc10>
    4629: e8 e2 eb ff ff               	callq	0x3210 <weston_log@plt>
    462e: 31 c0                        	xorl	%eax, %eax
    4630: eb db                        	jmp	0x460d <ivi_layout_get_properties_of_layer+0x1d>
    4632: e8 e9 eb ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4637: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000004640 <ivi_layout_surface_get_orientation>:
    4640: 48 83 ec 18                  	subq	$0x18, %rsp
    4644: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    464d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4652: 31 c0                        	xorl	%eax, %eax
    4654: 48 85 ff                     	testq	%rdi, %rdi
    4657: 74 1f                        	je	0x4678 <ivi_layout_surface_get_orientation+0x38>
    4659: 8b 87 cc 00 00 00            	movl	0xcc(%rdi), %eax
    465f: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4664: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    466d: 75 19                        	jne	0x4688 <ivi_layout_surface_get_orientation+0x48>
    466f: 48 83 c4 18                  	addq	$0x18, %rsp
    4673: c3                           	retq
    4674: 0f 1f 40 00                  	nopl	(%rax)
    4678: 48 8d 3d c9 85 00 00         	leaq	0x85c9(%rip), %rdi      # 0xcc48 <zwp_input_panel_v1_interface+0xcc48>
    467f: e8 8c eb ff ff               	callq	0x3210 <weston_log@plt>
    4684: 31 c0                        	xorl	%eax, %eax
    4686: eb d7                        	jmp	0x465f <ivi_layout_surface_get_orientation+0x1f>
    4688: e8 93 eb ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    468d: 0f 1f 00                     	nopl	(%rax)

0000000000004690 <ivi_layout_surface_set_orientation>:
    4690: 48 83 ec 18                  	subq	$0x18, %rsp
    4694: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    469d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    46a2: 31 c0                        	xorl	%eax, %eax
    46a4: 48 85 ff                     	testq	%rdi, %rdi
    46a7: 74 3a                        	je	0x46e3 <ivi_layout_surface_set_orientation+0x53>
    46a9: 89 b7 14 01 00 00            	movl	%esi, 0x114(%rdi)
    46af: 3b b7 cc 00 00 00            	cmpl	0xcc(%rdi), %esi
    46b5: 74 21                        	je	0x46d8 <ivi_layout_surface_set_orientation+0x48>
    46b7: 83 8f dc 00 00 00 40         	orl	$0x40, 0xdc(%rdi)
    46be: 31 c0                        	xorl	%eax, %eax
    46c0: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    46c5: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    46ce: 75 26                        	jne	0x46f6 <ivi_layout_surface_set_orientation+0x66>
    46d0: 48 83 c4 18                  	addq	$0x18, %rsp
    46d4: c3                           	retq
    46d5: 0f 1f 00                     	nopl	(%rax)
    46d8: 83 a7 dc 00 00 00 bf         	andl	$-0x41, 0xdc(%rdi)
    46df: 31 c0                        	xorl	%eax, %eax
    46e1: eb dd                        	jmp	0x46c0 <ivi_layout_surface_set_orientation+0x30>
    46e3: 48 8d 3d 96 85 00 00         	leaq	0x8596(%rip), %rdi      # 0xcc80 <zwp_input_panel_v1_interface+0xcc80>
    46ea: e8 21 eb ff ff               	callq	0x3210 <weston_log@plt>
    46ef: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    46f4: eb ca                        	jmp	0x46c0 <ivi_layout_surface_set_orientation+0x30>
    46f6: e8 25 eb ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    46fb: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000004700 <ivi_layout_surface_set_dimension>:
    4700: 48 83 ec 18                  	subq	$0x18, %rsp
    4704: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    470d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4712: 31 c0                        	xorl	%eax, %eax
    4714: 48 85 ff                     	testq	%rdi, %rdi
    4717: 74 4a                        	je	0x4763 <ivi_layout_surface_set_dimension+0x63>
    4719: 89 b7 0c 01 00 00            	movl	%esi, 0x10c(%rdi)
    471f: 89 97 10 01 00 00            	movl	%edx, 0x110(%rdi)
    4725: 3b b7 c4 00 00 00            	cmpl	0xc4(%rdi), %esi
    472b: 74 23                        	je	0x4750 <ivi_layout_surface_set_dimension+0x50>
    472d: 83 8f dc 00 00 00 10         	orl	$0x10, 0xdc(%rdi)
    4734: 31 c0                        	xorl	%eax, %eax
    4736: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    473b: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    4744: 75 30                        	jne	0x4776 <ivi_layout_surface_set_dimension+0x76>
    4746: 48 83 c4 18                  	addq	$0x18, %rsp
    474a: c3                           	retq
    474b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    4750: 3b 97 c8 00 00 00            	cmpl	0xc8(%rdi), %edx
    4756: 75 d5                        	jne	0x472d <ivi_layout_surface_set_dimension+0x2d>
    4758: 83 a7 dc 00 00 00 ef         	andl	$-0x11, 0xdc(%rdi)
    475f: 31 c0                        	xorl	%eax, %eax
    4761: eb d3                        	jmp	0x4736 <ivi_layout_surface_set_dimension+0x36>
    4763: 48 8d 3d 4e 85 00 00         	leaq	0x854e(%rip), %rdi      # 0xccb8 <zwp_input_panel_v1_interface+0xccb8>
    476a: e8 a1 ea ff ff               	callq	0x3210 <weston_log@plt>
    476f: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4774: eb c0                        	jmp	0x4736 <ivi_layout_surface_set_dimension+0x36>
    4776: e8 a5 ea ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    477b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000004780 <ivi_layout_surface_get_position>:
    4780: 48 83 ec 18                  	subq	$0x18, %rsp
    4784: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    478d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4792: 31 c0                        	xorl	%eax, %eax
    4794: 48 85 f6                     	testq	%rsi, %rsi
    4797: 0f 94 c1                     	sete	%cl
    479a: 48 85 d2                     	testq	%rdx, %rdx
    479d: 0f 94 c0                     	sete	%al
    47a0: 08 c1                        	orb	%al, %cl
    47a2: 75 2c                        	jne	0x47d0 <ivi_layout_surface_get_position+0x50>
    47a4: 48 85 ff                     	testq	%rdi, %rdi
    47a7: 74 27                        	je	0x47d0 <ivi_layout_surface_get_position+0x50>
    47a9: 8b 87 bc 00 00 00            	movl	0xbc(%rdi), %eax
    47af: 89 06                        	movl	%eax, (%rsi)
    47b1: 8b 87 c0 00 00 00            	movl	0xc0(%rdi), %eax
    47b7: 89 02                        	movl	%eax, (%rdx)
    47b9: 31 c0                        	xorl	%eax, %eax
    47bb: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    47c0: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    47c9: 75 1a                        	jne	0x47e5 <ivi_layout_surface_get_position+0x65>
    47cb: 48 83 c4 18                  	addq	$0x18, %rsp
    47cf: c3                           	retq
    47d0: 48 8d 3d 19 85 00 00         	leaq	0x8519(%rip), %rdi      # 0xccf0 <zwp_input_panel_v1_interface+0xccf0>
    47d7: 31 c0                        	xorl	%eax, %eax
    47d9: e8 32 ea ff ff               	callq	0x3210 <weston_log@plt>
    47de: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    47e3: eb d6                        	jmp	0x47bb <ivi_layout_surface_get_position+0x3b>
    47e5: e8 36 ea ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    47ea: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000000047f0 <ivi_layout_surface_set_position>:
    47f0: 48 83 ec 18                  	subq	$0x18, %rsp
    47f4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    47fd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4802: 31 c0                        	xorl	%eax, %eax
    4804: 48 85 ff                     	testq	%rdi, %rdi
    4807: 74 4a                        	je	0x4853 <ivi_layout_surface_set_position+0x63>
    4809: 89 b7 04 01 00 00            	movl	%esi, 0x104(%rdi)
    480f: 89 97 08 01 00 00            	movl	%edx, 0x108(%rdi)
    4815: 3b b7 bc 00 00 00            	cmpl	0xbc(%rdi), %esi
    481b: 74 23                        	je	0x4840 <ivi_layout_surface_set_position+0x50>
    481d: 83 8f dc 00 00 00 20         	orl	$0x20, 0xdc(%rdi)
    4824: 31 c0                        	xorl	%eax, %eax
    4826: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    482b: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    4834: 75 30                        	jne	0x4866 <ivi_layout_surface_set_position+0x76>
    4836: 48 83 c4 18                  	addq	$0x18, %rsp
    483a: c3                           	retq
    483b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    4840: 3b 97 c0 00 00 00            	cmpl	0xc0(%rdi), %edx
    4846: 75 d5                        	jne	0x481d <ivi_layout_surface_set_position+0x2d>
    4848: 83 a7 dc 00 00 00 df         	andl	$-0x21, 0xdc(%rdi)
    484f: 31 c0                        	xorl	%eax, %eax
    4851: eb d3                        	jmp	0x4826 <ivi_layout_surface_set_position+0x36>
    4853: 48 8d 3d ce 84 00 00         	leaq	0x84ce(%rip), %rdi      # 0xcd28 <zwp_input_panel_v1_interface+0xcd28>
    485a: e8 b1 e9 ff ff               	callq	0x3210 <weston_log@plt>
    485f: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4864: eb c0                        	jmp	0x4826 <ivi_layout_surface_set_position+0x36>
    4866: e8 b5 e9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    486b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000004870 <ivi_layout_get_properties_of_surface>:
    4870: 48 83 ec 18                  	subq	$0x18, %rsp
    4874: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    487d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4882: 31 c0                        	xorl	%eax, %eax
    4884: 48 85 ff                     	testq	%rdi, %rdi
    4887: 74 1c                        	je	0x48a5 <ivi_layout_get_properties_of_surface+0x35>
    4889: 48 8d 87 98 00 00 00         	leaq	0x98(%rdi), %rax
    4890: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4895: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    489e: 75 15                        	jne	0x48b5 <ivi_layout_get_properties_of_surface+0x45>
    48a0: 48 83 c4 18                  	addq	$0x18, %rsp
    48a4: c3                           	retq
    48a5: 48 8d 3d b4 84 00 00         	leaq	0x84b4(%rip), %rdi      # 0xcd60 <zwp_input_panel_v1_interface+0xcd60>
    48ac: e8 5f e9 ff ff               	callq	0x3210 <weston_log@plt>
    48b1: 31 c0                        	xorl	%eax, %eax
    48b3: eb db                        	jmp	0x4890 <ivi_layout_get_properties_of_surface+0x20>
    48b5: e8 66 e9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    48ba: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000000048c0 <remove_all_notification>:
    48c0: 41 54                        	pushq	%r12
    48c2: 49 89 fc                     	movq	%rdi, %r12
    48c5: 55                           	pushq	%rbp
    48c6: 53                           	pushq	%rbx
    48c7: 48 83 ec 10                  	subq	$0x10, %rsp
    48cb: 48 8b 5f 08                  	movq	0x8(%rdi), %rbx
    48cf: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    48d8: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    48dd: 31 c0                        	xorl	%eax, %eax
    48df: 48 8b 6b 08                  	movq	0x8(%rbx), %rbp
    48e3: 48 39 df                     	cmpq	%rbx, %rdi
    48e6: 74 2e                        	je	0x4916 <remove_all_notification+0x56>
    48e8: 48 89 df                     	movq	%rbx, %rdi
    48eb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    48f0: e8 3b eb ff ff               	callq	0x3430 <wl_list_remove@plt>
    48f5: 48 8b 7b f8                  	movq	-0x8(%rbx), %rdi
    48f9: e8 72 e7 ff ff               	callq	0x3070 <free@plt>
    48fe: 48 8d 7b f8                  	leaq	-0x8(%rbx), %rdi
    4902: 48 89 eb                     	movq	%rbp, %rbx
    4905: e8 66 e7 ff ff               	callq	0x3070 <free@plt>
    490a: 48 89 ef                     	movq	%rbp, %rdi
    490d: 48 8b 6d 08                  	movq	0x8(%rbp), %rbp
    4911: 49 39 fc                     	cmpq	%rdi, %r12
    4914: 75 da                        	jne	0x48f0 <remove_all_notification+0x30>
    4916: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    491b: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4924: 75 09                        	jne	0x492f <remove_all_notification+0x6f>
    4926: 48 83 c4 10                  	addq	$0x10, %rsp
    492a: 5b                           	popq	%rbx
    492b: 5d                           	popq	%rbp
    492c: 41 5c                        	popq	%r12
    492e: c3                           	retq
    492f: e8 ec e8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4934: 66 90                        	nop
    4936: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000004940 <ivi_layout_surface_remove_notification>:
    4940: 48 83 ec 18                  	subq	$0x18, %rsp
    4944: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    494d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4952: 31 c0                        	xorl	%eax, %eax
    4954: 48 85 ff                     	testq	%rdi, %rdi
    4957: 74 27                        	je	0x4980 <ivi_layout_surface_remove_notification+0x40>
    4959: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    495e: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4967: 75 39                        	jne	0x49a2 <ivi_layout_surface_remove_notification+0x62>
    4969: 48 83 c7 10                  	addq	$0x10, %rdi
    496d: 48 83 c4 18                  	addq	$0x18, %rsp
    4971: e9 4a ff ff ff               	jmp	0x48c0 <remove_all_notification>
    4976: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    4980: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4985: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    498e: 75 12                        	jne	0x49a2 <ivi_layout_surface_remove_notification+0x62>
    4990: 48 8d 3d 01 84 00 00         	leaq	0x8401(%rip), %rdi      # 0xcd98 <zwp_input_panel_v1_interface+0xcd98>
    4997: 31 c0                        	xorl	%eax, %eax
    4999: 48 83 c4 18                  	addq	$0x18, %rsp
    499d: e9 6e e8 ff ff               	jmp	0x3210 <weston_log@plt>
    49a2: e8 79 e8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    49a7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

00000000000049b0 <ivi_layout_layer_remove_notification>:
    49b0: 48 83 ec 18                  	subq	$0x18, %rsp
    49b4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    49bd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    49c2: 31 c0                        	xorl	%eax, %eax
    49c4: 48 85 ff                     	testq	%rdi, %rdi
    49c7: 74 27                        	je	0x49f0 <ivi_layout_layer_remove_notification+0x40>
    49c9: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    49ce: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    49d7: 75 39                        	jne	0x4a12 <ivi_layout_layer_remove_notification+0x62>
    49d9: 48 83 c7 10                  	addq	$0x10, %rdi
    49dd: 48 83 c4 18                  	addq	$0x18, %rsp
    49e1: e9 da fe ff ff               	jmp	0x48c0 <remove_all_notification>
    49e6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    49f0: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    49f5: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    49fe: 75 12                        	jne	0x4a12 <ivi_layout_layer_remove_notification+0x62>
    4a00: 48 8d 3d d1 83 00 00         	leaq	0x83d1(%rip), %rdi      # 0xcdd8 <zwp_input_panel_v1_interface+0xcdd8>
    4a07: 31 c0                        	xorl	%eax, %eax
    4a09: 48 83 c4 18                  	addq	$0x18, %rsp
    4a0d: e9 fe e7 ff ff               	jmp	0x3210 <weston_log@plt>
    4a12: e8 09 e8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4a17: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000004a20 <remove_notification>:
    4a20: 41 54                        	pushq	%r12
    4a22: 49 89 fc                     	movq	%rdi, %r12
    4a25: 55                           	pushq	%rbp
    4a26: 53                           	pushq	%rbx
    4a27: 48 83 ec 20                  	subq	$0x20, %rsp
    4a2b: 48 8b 6f 08                  	movq	0x8(%rdi), %rbp
    4a2f: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4a38: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    4a3d: 31 c0                        	xorl	%eax, %eax
    4a3f: 48 8b 5d 08                  	movq	0x8(%rbp), %rbx
    4a43: 48 89 ef                     	movq	%rbp, %rdi
    4a46: 49 39 ec                     	cmpq	%rbp, %r12
    4a49: 75 17                        	jne	0x4a62 <remove_notification+0x42>
    4a4b: eb 63                        	jmp	0x4ab0 <remove_notification+0x90>
    4a4d: 0f 1f 00                     	nopl	(%rax)
    4a50: 48 8b 43 08                  	movq	0x8(%rbx), %rax
    4a54: 48 89 df                     	movq	%rbx, %rdi
    4a57: 48 89 dd                     	movq	%rbx, %rbp
    4a5a: 49 39 dc                     	cmpq	%rbx, %r12
    4a5d: 74 51                        	je	0x4ab0 <remove_notification+0x90>
    4a5f: 48 89 c3                     	movq	%rax, %rbx
    4a62: 48 8b 45 f8                  	movq	-0x8(%rbp), %rax
    4a66: 48 39 30                     	cmpq	%rsi, (%rax)
    4a69: 75 e5                        	jne	0x4a50 <remove_notification+0x30>
    4a6b: 48 39 50 08                  	cmpq	%rdx, 0x8(%rax)
    4a6f: 75 df                        	jne	0x4a50 <remove_notification+0x30>
    4a71: 48 89 54 24 08               	movq	%rdx, 0x8(%rsp)
    4a76: 48 89 34 24                  	movq	%rsi, (%rsp)
    4a7a: e8 b1 e9 ff ff               	callq	0x3430 <wl_list_remove@plt>
    4a7f: 48 8b 7d f8                  	movq	-0x8(%rbp), %rdi
    4a83: e8 e8 e5 ff ff               	callq	0x3070 <free@plt>
    4a88: 48 8d 7d f8                  	leaq	-0x8(%rbp), %rdi
    4a8c: 48 89 dd                     	movq	%rbx, %rbp
    4a8f: e8 dc e5 ff ff               	callq	0x3070 <free@plt>
    4a94: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4a99: 48 89 df                     	movq	%rbx, %rdi
    4a9c: 48 8b 34 24                  	movq	(%rsp), %rsi
    4aa0: 48 8b 43 08                  	movq	0x8(%rbx), %rax
    4aa4: 49 39 dc                     	cmpq	%rbx, %r12
    4aa7: 75 b6                        	jne	0x4a5f <remove_notification+0x3f>
    4aa9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    4ab0: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    4ab5: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4abe: 75 09                        	jne	0x4ac9 <remove_notification+0xa9>
    4ac0: 48 83 c4 20                  	addq	$0x20, %rsp
    4ac4: 5b                           	popq	%rbx
    4ac5: 5d                           	popq	%rbp
    4ac6: 41 5c                        	popq	%r12
    4ac8: c3                           	retq
    4ac9: e8 52 e7 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4ace: 66 90                        	nop

0000000000004ad0 <ivi_layout_layer_remove_notification_by_callback>:
    4ad0: 48 83 ec 18                  	subq	$0x18, %rsp
    4ad4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4add: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4ae2: 31 c0                        	xorl	%eax, %eax
    4ae4: 48 85 ff                     	testq	%rdi, %rdi
    4ae7: 74 27                        	je	0x4b10 <ivi_layout_layer_remove_notification_by_callback+0x40>
    4ae9: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4aee: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4af7: 75 39                        	jne	0x4b32 <ivi_layout_layer_remove_notification_by_callback+0x62>
    4af9: 48 83 c7 10                  	addq	$0x10, %rdi
    4afd: 48 83 c4 18                  	addq	$0x18, %rsp
    4b01: e9 1a ff ff ff               	jmp	0x4a20 <remove_notification>
    4b06: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    4b10: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4b15: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4b1e: 75 12                        	jne	0x4b32 <ivi_layout_layer_remove_notification_by_callback+0x62>
    4b20: 48 8d 3d e9 82 00 00         	leaq	0x82e9(%rip), %rdi      # 0xce10 <zwp_input_panel_v1_interface+0xce10>
    4b27: 31 c0                        	xorl	%eax, %eax
    4b29: 48 83 c4 18                  	addq	$0x18, %rsp
    4b2d: e9 de e6 ff ff               	jmp	0x3210 <weston_log@plt>
    4b32: e8 e9 e6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4b37: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000004b40 <ivi_layout_surface_remove_notification_by_callback>:
    4b40: 48 83 ec 18                  	subq	$0x18, %rsp
    4b44: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4b4d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4b52: 31 c0                        	xorl	%eax, %eax
    4b54: 48 85 ff                     	testq	%rdi, %rdi
    4b57: 74 27                        	je	0x4b80 <ivi_layout_surface_remove_notification_by_callback+0x40>
    4b59: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4b5e: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4b67: 75 39                        	jne	0x4ba2 <ivi_layout_surface_remove_notification_by_callback+0x62>
    4b69: 48 83 c7 10                  	addq	$0x10, %rdi
    4b6d: 48 83 c4 18                  	addq	$0x18, %rsp
    4b71: e9 aa fe ff ff               	jmp	0x4a20 <remove_notification>
    4b76: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    4b80: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4b85: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4b8e: 75 12                        	jne	0x4ba2 <ivi_layout_surface_remove_notification_by_callback+0x62>
    4b90: 48 8d 3d c1 82 00 00         	leaq	0x82c1(%rip), %rdi      # 0xce58 <zwp_input_panel_v1_interface+0xce58>
    4b97: 31 c0                        	xorl	%eax, %eax
    4b99: 48 83 c4 18                  	addq	$0x18, %rsp
    4b9d: e9 6e e6 ff ff               	jmp	0x3210 <weston_log@plt>
    4ba2: e8 79 e6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4ba7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000004bb0 <ivi_layout_remove_notification_remove_layer>:
    4bb0: 48 83 ec 18                  	subq	$0x18, %rsp
    4bb4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4bbd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4bc2: 31 c0                        	xorl	%eax, %eax
    4bc4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4bc9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4bd2: 75 16                        	jne	0x4bea <ivi_layout_remove_notification_remove_layer+0x3a>
    4bd4: 48 89 f2                     	movq	%rsi, %rdx
    4bd7: 48 83 c4 18                  	addq	$0x18, %rsp
    4bdb: 48 89 fe                     	movq	%rdi, %rsi
    4bde: 48 8d 3d 63 c7 20 00         	leaq	0x20c763(%rip), %rdi    # 0x211348 <ivilayout+0x48>
    4be5: e9 36 fe ff ff               	jmp	0x4a20 <remove_notification>
    4bea: e8 31 e6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4bef: 90                           	nop

0000000000004bf0 <ivi_layout_remove_notification_create_layer>:
    4bf0: 48 83 ec 18                  	subq	$0x18, %rsp
    4bf4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4bfd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4c02: 31 c0                        	xorl	%eax, %eax
    4c04: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4c09: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4c12: 75 16                        	jne	0x4c2a <ivi_layout_remove_notification_create_layer+0x3a>
    4c14: 48 89 f2                     	movq	%rsi, %rdx
    4c17: 48 83 c4 18                  	addq	$0x18, %rsp
    4c1b: 48 89 fe                     	movq	%rdi, %rsi
    4c1e: 48 8d 3d 13 c7 20 00         	leaq	0x20c713(%rip), %rdi    # 0x211338 <ivilayout+0x38>
    4c25: e9 f6 fd ff ff               	jmp	0x4a20 <remove_notification>
    4c2a: e8 f1 e5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4c2f: 90                           	nop

0000000000004c30 <ivi_layout_remove_notification_configure_surface>:
    4c30: 48 83 ec 18                  	subq	$0x18, %rsp
    4c34: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4c3d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4c42: 31 c0                        	xorl	%eax, %eax
    4c44: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4c49: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4c52: 75 16                        	jne	0x4c6a <ivi_layout_remove_notification_configure_surface+0x3a>
    4c54: 48 89 f2                     	movq	%rsi, %rdx
    4c57: 48 83 c4 18                  	addq	$0x18, %rsp
    4c5b: 48 89 fe                     	movq	%rdi, %rsi
    4c5e: 48 8d 3d 13 c7 20 00         	leaq	0x20c713(%rip), %rdi    # 0x211378 <ivilayout+0x78>
    4c65: e9 b6 fd ff ff               	jmp	0x4a20 <remove_notification>
    4c6a: e8 b1 e5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4c6f: 90                           	nop

0000000000004c70 <ivi_layout_remove_notification_remove_surface>:
    4c70: 48 83 ec 18                  	subq	$0x18, %rsp
    4c74: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4c7d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4c82: 31 c0                        	xorl	%eax, %eax
    4c84: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4c89: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4c92: 75 16                        	jne	0x4caa <ivi_layout_remove_notification_remove_surface+0x3a>
    4c94: 48 89 f2                     	movq	%rsi, %rdx
    4c97: 48 83 c4 18                  	addq	$0x18, %rsp
    4c9b: 48 89 fe                     	movq	%rdi, %rsi
    4c9e: 48 8d 3d c3 c6 20 00         	leaq	0x20c6c3(%rip), %rdi    # 0x211368 <ivilayout+0x68>
    4ca5: e9 76 fd ff ff               	jmp	0x4a20 <remove_notification>
    4caa: e8 71 e5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4caf: 90                           	nop

0000000000004cb0 <ivi_layout_remove_notification_create_surface>:
    4cb0: 48 83 ec 18                  	subq	$0x18, %rsp
    4cb4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4cbd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4cc2: 31 c0                        	xorl	%eax, %eax
    4cc4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4cc9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4cd2: 75 16                        	jne	0x4cea <ivi_layout_remove_notification_create_surface+0x3a>
    4cd4: 48 89 f2                     	movq	%rsi, %rdx
    4cd7: 48 83 c4 18                  	addq	$0x18, %rsp
    4cdb: 48 89 fe                     	movq	%rdi, %rsi
    4cde: 48 8d 3d 73 c6 20 00         	leaq	0x20c673(%rip), %rdi    # 0x211358 <ivilayout+0x58>
    4ce5: e9 36 fd ff ff               	jmp	0x4a20 <remove_notification>
    4cea: e8 31 e5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4cef: 90                           	nop

0000000000004cf0 <ivi_layout_surface_destroy>:
    4cf0: 41 54                        	pushq	%r12
    4cf2: 55                           	pushq	%rbp
    4cf3: 53                           	pushq	%rbx
    4cf4: 48 83 ec 10                  	subq	$0x10, %rsp
    4cf8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4d01: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4d06: 31 c0                        	xorl	%eax, %eax
    4d08: 48 85 ff                     	testq	%rdi, %rdi
    4d0b: 0f 84 df 00 00 00            	je	0x4df0 <ivi_layout_surface_destroy+0x100>
    4d11: 4c 8d 25 50 c6 20 00         	leaq	0x20c650(%rip), %r12    # 0x211368 <ivilayout+0x68>
    4d18: 48 89 fd                     	movq	%rdi, %rbp
    4d1b: 48 8d bf 88 00 00 00         	leaq	0x88(%rdi), %rdi
    4d22: e8 09 e7 ff ff               	callq	0x3430 <wl_list_remove@plt>
    4d27: 48 8d bd 28 01 00 00         	leaq	0x128(%rbp), %rdi
    4d2e: e8 fd e6 ff ff               	callq	0x3430 <wl_list_remove@plt>
    4d33: 48 8d bd 38 01 00 00         	leaq	0x138(%rbp), %rdi
    4d3a: e8 f1 e6 ff ff               	callq	0x3430 <wl_list_remove@plt>
    4d3f: 48 89 ef                     	movq	%rbp, %rdi
    4d42: e8 e9 e6 ff ff               	callq	0x3430 <wl_list_remove@plt>
    4d47: 48 8b 05 22 c6 20 00         	movq	0x20c622(%rip), %rax    # 0x211370 <ivilayout+0x70>
    4d4e: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    4d52: 4c 39 e0                     	cmpq	%r12, %rax
    4d55: 75 0c                        	jne	0x4d63 <ivi_layout_surface_destroy+0x73>
    4d57: eb 1f                        	jmp	0x4d78 <ivi_layout_surface_destroy+0x88>
    4d59: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    4d60: 48 89 d3                     	movq	%rdx, %rbx
    4d63: 48 89 c7                     	movq	%rax, %rdi
    4d66: 48 89 ee                     	movq	%rbp, %rsi
    4d69: ff 50 10                     	callq	*0x10(%rax)
    4d6c: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    4d70: 48 89 d8                     	movq	%rbx, %rax
    4d73: 4c 39 e3                     	cmpq	%r12, %rbx
    4d76: 75 e8                        	jne	0x4d60 <ivi_layout_surface_destroy+0x70>
    4d78: 4c 8d a5 68 01 00 00         	leaq	0x168(%rbp), %r12
    4d7f: 48 89 ef                     	movq	%rbp, %rdi
    4d82: e8 c9 44 00 00               	callq	0x9250 <ivi_layout_remove_all_surface_transitions>
    4d87: 48 8b bd 70 01 00 00         	movq	0x170(%rbp), %rdi
    4d8e: 48 8b 5f 08                  	movq	0x8(%rdi), %rbx
    4d92: 49 39 fc                     	cmpq	%rdi, %r12
    4d95: 74 1a                        	je	0x4db1 <ivi_layout_surface_destroy+0xc1>
    4d97: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    4da0: e8 8b e6 ff ff               	callq	0x3430 <wl_list_remove@plt>
    4da5: 48 89 df                     	movq	%rbx, %rdi
    4da8: 48 8b 5b 08                  	movq	0x8(%rbx), %rbx
    4dac: 4c 39 e7                     	cmpq	%r12, %rdi
    4daf: 75 ef                        	jne	0x4da0 <ivi_layout_surface_destroy+0xb0>
    4db1: 48 8d 7d 10                  	leaq	0x10(%rbp), %rdi
    4db5: e8 06 fb ff ff               	callq	0x48c0 <remove_all_notification>
    4dba: 48 8b bd 88 01 00 00         	movq	0x188(%rbp), %rdi
    4dc1: 48 85 ff                     	testq	%rdi, %rdi
    4dc4: 74 05                        	je	0x4dcb <ivi_layout_surface_destroy+0xdb>
    4dc6: e8 95 e3 ff ff               	callq	0x3160 <weston_view_destroy@plt>
    4dcb: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4dd0: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4dd9: 75 42                        	jne	0x4e1d <ivi_layout_surface_destroy+0x12d>
    4ddb: 48 83 c4 10                  	addq	$0x10, %rsp
    4ddf: 48 89 ef                     	movq	%rbp, %rdi
    4de2: 5b                           	popq	%rbx
    4de3: 5d                           	popq	%rbp
    4de4: 41 5c                        	popq	%r12
    4de6: e9 85 e2 ff ff               	jmp	0x3070 <free@plt>
    4deb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    4df0: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    4df5: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    4dfe: 75 1d                        	jne	0x4e1d <ivi_layout_surface_destroy+0x12d>
    4e00: 48 8d 35 09 8a 00 00         	leaq	0x8a09(%rip), %rsi      # 0xd810 <__func__.12894>
    4e07: 48 83 c4 10                  	addq	$0x10, %rsp
    4e0b: 31 c0                        	xorl	%eax, %eax
    4e0d: 5b                           	popq	%rbx
    4e0e: 48 8d 3d 58 87 00 00         	leaq	0x8758(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    4e15: 5d                           	popq	%rbp
    4e16: 41 5c                        	popq	%r12
    4e18: e9 f3 e3 ff ff               	jmp	0x3210 <weston_log@plt>
    4e1d: e8 fe e3 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4e22: 0f 1f 40 00                  	nopl	(%rax)
    4e26: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000004e30 <ivi_layout_surface_add_notification>:
    4e30: 41 55                        	pushq	%r13
    4e32: 41 54                        	pushq	%r12
    4e34: 55                           	pushq	%rbp
    4e35: 53                           	pushq	%rbx
    4e36: 48 83 ec 18                  	subq	$0x18, %rsp
    4e3a: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4e43: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4e48: 31 c0                        	xorl	%eax, %eax
    4e4a: 48 85 ff                     	testq	%rdi, %rdi
    4e4d: 74 79                        	je	0x4ec8 <ivi_layout_surface_add_notification+0x98>
    4e4f: 49 89 f4                     	movq	%rsi, %r12
    4e52: 48 85 f6                     	testq	%rsi, %rsi
    4e55: 74 71                        	je	0x4ec8 <ivi_layout_surface_add_notification+0x98>
    4e57: 48 89 fd                     	movq	%rdi, %rbp
    4e5a: bf 20 00 00 00               	movl	$0x20, %edi
    4e5f: 49 89 d5                     	movq	%rdx, %r13
    4e62: e8 09 e6 ff ff               	callq	0x3470 <malloc@plt>
    4e67: 48 89 c3                     	movq	%rax, %rbx
    4e6a: 48 85 c0                     	testq	%rax, %rax
    4e6d: 0f 84 85 00 00 00            	je	0x4ef8 <ivi_layout_surface_add_notification+0xc8>
    4e73: bf 10 00 00 00               	movl	$0x10, %edi
    4e78: e8 f3 e5 ff ff               	callq	0x3470 <malloc@plt>
    4e7d: 48 85 c0                     	testq	%rax, %rax
    4e80: 74 5b                        	je	0x4edd <ivi_layout_surface_add_notification+0xad>
    4e82: 48 8b 7d 10                  	movq	0x10(%rbp), %rdi
    4e86: 4c 89 20                     	movq	%r12, (%rax)
    4e89: 48 8d 73 08                  	leaq	0x8(%rbx), %rsi
    4e8d: 4c 89 68 08                  	movq	%r13, 0x8(%rax)
    4e91: 48 8d 0d b8 e9 ff ff         	leaq	-0x1648(%rip), %rcx     # 0x3850 <surface_prop_changed>
    4e98: 48 89 03                     	movq	%rax, (%rbx)
    4e9b: 48 89 4b 18                  	movq	%rcx, 0x18(%rbx)
    4e9f: e8 fc e7 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    4ea4: 31 c0                        	xorl	%eax, %eax
    4ea6: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    4eab: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    4eb4: 75 57                        	jne	0x4f0d <ivi_layout_surface_add_notification+0xdd>
    4eb6: 48 83 c4 18                  	addq	$0x18, %rsp
    4eba: 5b                           	popq	%rbx
    4ebb: 5d                           	popq	%rbp
    4ebc: 41 5c                        	popq	%r12
    4ebe: 41 5d                        	popq	%r13
    4ec0: c3                           	retq
    4ec1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    4ec8: 48 8d 3d d1 7f 00 00         	leaq	0x7fd1(%rip), %rdi      # 0xcea0 <zwp_input_panel_v1_interface+0xcea0>
    4ecf: 31 c0                        	xorl	%eax, %eax
    4ed1: e8 3a e3 ff ff               	callq	0x3210 <weston_log@plt>
    4ed6: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4edb: eb c9                        	jmp	0x4ea6 <ivi_layout_surface_add_notification+0x76>
    4edd: 48 8d 3d 9f 86 00 00         	leaq	0x869f(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    4ee4: e8 27 e3 ff ff               	callq	0x3210 <weston_log@plt>
    4ee9: 48 89 df                     	movq	%rbx, %rdi
    4eec: e8 7f e1 ff ff               	callq	0x3070 <free@plt>
    4ef1: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4ef6: eb ae                        	jmp	0x4ea6 <ivi_layout_surface_add_notification+0x76>
    4ef8: 48 8d 3d 84 86 00 00         	leaq	0x8684(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    4eff: 31 c0                        	xorl	%eax, %eax
    4f01: e8 0a e3 ff ff               	callq	0x3210 <weston_log@plt>
    4f06: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    4f0b: eb 99                        	jmp	0x4ea6 <ivi_layout_surface_add_notification+0x76>
    4f0d: e8 0e e3 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    4f12: 0f 1f 40 00                  	nopl	(%rax)
    4f16: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000004f20 <ivi_layout_layer_set_render_order>:
    4f20: 41 57                        	pushq	%r15
    4f22: 41 56                        	pushq	%r14
    4f24: 41 55                        	pushq	%r13
    4f26: 41 54                        	pushq	%r12
    4f28: 55                           	pushq	%rbp
    4f29: 53                           	pushq	%rbx
    4f2a: 48 83 ec 18                  	subq	$0x18, %rsp
    4f2e: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    4f37: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    4f3c: 31 c0                        	xorl	%eax, %eax
    4f3e: 48 85 ff                     	testq	%rdi, %rdi
    4f41: 0f 84 ae 00 00 00            	je	0x4ff5 <ivi_layout_layer_set_render_order+0xd5>
    4f47: 49 89 fd                     	movq	%rdi, %r13
    4f4a: 85 d2                        	testl	%edx, %edx
    4f4c: 7e 76                        	jle	0x4fc4 <ivi_layout_layer_set_render_order+0xa4>
    4f4e: 8d 42 ff                     	leal	-0x1(%rdx), %eax
    4f51: 49 89 f7                     	movq	%rsi, %r15
    4f54: 48 8d 6c c6 08               	leaq	0x8(%rsi,%rax,8), %rbp
    4f59: 4c 8d 35 a8 c3 20 00         	leaq	0x20c3a8(%rip), %r14    # 0x211308 <ivilayout+0x8>
    4f60: 4c 8d a7 e0 00 00 00         	leaq	0xe0(%rdi), %r12
    4f67: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    4f70: 48 8b 05 99 c3 20 00         	movq	0x20c399(%rip), %rax    # 0x211310 <ivilayout+0x10>
    4f77: 49 8b 17                     	movq	(%r15), %rdx
    4f7a: 48 8b 70 08                  	movq	0x8(%rax), %rsi
    4f7e: 4c 39 f0                     	cmpq	%r14, %rax
    4f81: 74 38                        	je	0x4fbb <ivi_layout_layer_set_render_order+0x9b>
    4f83: 8b 52 24                     	movl	0x24(%rdx), %edx
    4f86: 3b 50 24                     	cmpl	0x24(%rax), %edx
    4f89: 75 08                        	jne	0x4f93 <ivi_layout_layer_set_render_order+0x73>
    4f8b: eb 63                        	jmp	0x4ff0 <ivi_layout_layer_set_render_order+0xd0>
    4f8d: 0f 1f 00                     	nopl	(%rax)
    4f90: 48 89 c6                     	movq	%rax, %rsi
    4f93: 48 8b 46 08                  	movq	0x8(%rsi), %rax
    4f97: 4c 39 f6                     	cmpq	%r14, %rsi
    4f9a: 74 1f                        	je	0x4fbb <ivi_layout_layer_set_render_order+0x9b>
    4f9c: 39 56 24                     	cmpl	%edx, 0x24(%rsi)
    4f9f: 75 ef                        	jne	0x4f90 <ivi_layout_layer_set_render_order+0x70>
    4fa1: 48 8d 9e 28 01 00 00         	leaq	0x128(%rsi), %rbx
    4fa8: 48 89 df                     	movq	%rbx, %rdi
    4fab: e8 80 e4 ff ff               	callq	0x3430 <wl_list_remove@plt>
    4fb0: 48 89 de                     	movq	%rbx, %rsi
    4fb3: 4c 89 e7                     	movq	%r12, %rdi
    4fb6: e8 e5 e6 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    4fbb: 49 83 c7 08                  	addq	$0x8, %r15
    4fbf: 49 39 ef                     	cmpq	%rbp, %r15
    4fc2: 75 ac                        	jne	0x4f70 <ivi_layout_layer_set_render_order+0x50>
    4fc4: 41 c7 85 00 01 00 00 01 00 00 00     	movl	$0x1, 0x100(%r13)
    4fcf: 31 c0                        	xorl	%eax, %eax
    4fd1: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    4fd6: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    4fdf: 75 29                        	jne	0x500a <ivi_layout_layer_set_render_order+0xea>
    4fe1: 48 83 c4 18                  	addq	$0x18, %rsp
    4fe5: 5b                           	popq	%rbx
    4fe6: 5d                           	popq	%rbp
    4fe7: 41 5c                        	popq	%r12
    4fe9: 41 5d                        	popq	%r13
    4feb: 41 5e                        	popq	%r14
    4fed: 41 5f                        	popq	%r15
    4fef: c3                           	retq
    4ff0: 48 89 c6                     	movq	%rax, %rsi
    4ff3: eb ac                        	jmp	0x4fa1 <ivi_layout_layer_set_render_order+0x81>
    4ff5: 48 8d 3d dc 7e 00 00         	leaq	0x7edc(%rip), %rdi      # 0xced8 <zwp_input_panel_v1_interface+0xced8>
    4ffc: 31 c0                        	xorl	%eax, %eax
    4ffe: e8 0d e2 ff ff               	callq	0x3210 <weston_log@plt>
    5003: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5008: eb c7                        	jmp	0x4fd1 <ivi_layout_layer_set_render_order+0xb1>
    500a: e8 11 e2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    500f: 90                           	nop

0000000000005010 <ivi_layout_screen_add_layer>:
    5010: 55                           	pushq	%rbp
    5011: 53                           	pushq	%rbx
    5012: 48 83 ec 18                  	subq	$0x18, %rsp
    5016: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    501f: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5024: 31 c0                        	xorl	%eax, %eax
    5026: 48 85 ff                     	testq	%rdi, %rdi
    5029: 0f 84 a0 00 00 00            	je	0x50cf <ivi_layout_screen_add_layer+0xbf>
    502f: 48 85 f6                     	testq	%rsi, %rsi
    5032: 0f 84 97 00 00 00            	je	0x50cf <ivi_layout_screen_add_layer+0xbf>
    5038: 48 89 fd                     	movq	%rdi, %rbp
    503b: 48 3b 7e 30                  	cmpq	0x30(%rsi), %rdi
    503f: 74 7c                        	je	0x50bd <ivi_layout_screen_add_layer+0xad>
    5041: 48 8b 15 d8 c2 20 00         	movq	0x20c2d8(%rip), %rdx    # 0x211320 <ivilayout+0x20>
    5048: 48 8d 0d c9 c2 20 00         	leaq	0x20c2c9(%rip), %rcx    # 0x211318 <ivilayout+0x18>
    504f: 48 8b 42 08                  	movq	0x8(%rdx), %rax
    5053: 48 39 ca                     	cmpq	%rcx, %rdx
    5056: 74 21                        	je	0x5079 <ivi_layout_screen_add_layer+0x69>
    5058: 8b 76 20                     	movl	0x20(%rsi), %esi
    505b: 3b 72 20                     	cmpl	0x20(%rdx), %esi
    505e: 75 10                        	jne	0x5070 <ivi_layout_screen_add_layer+0x60>
    5060: eb 37                        	jmp	0x5099 <ivi_layout_screen_add_layer+0x89>
    5062: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    5068: 39 70 20                     	cmpl	%esi, 0x20(%rax)
    506b: 74 33                        	je	0x50a0 <ivi_layout_screen_add_layer+0x90>
    506d: 48 89 d0                     	movq	%rdx, %rax
    5070: 48 8b 50 08                  	movq	0x8(%rax), %rdx
    5074: 48 39 c8                     	cmpq	%rcx, %rax
    5077: 75 ef                        	jne	0x5068 <ivi_layout_screen_add_layer+0x58>
    5079: c7 45 48 01 00 00 00         	movl	$0x1, 0x48(%rbp)
    5080: 31 c0                        	xorl	%eax, %eax
    5082: 48 8b 5c 24 08               	movq	0x8(%rsp), %rbx
    5087: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
    5090: 75 52                        	jne	0x50e4 <ivi_layout_screen_add_layer+0xd4>
    5092: 48 83 c4 18                  	addq	$0x18, %rsp
    5096: 5b                           	popq	%rbx
    5097: 5d                           	popq	%rbp
    5098: c3                           	retq
    5099: 48 89 d0                     	movq	%rdx, %rax
    509c: 0f 1f 40 00                  	nopl	(%rax)
    50a0: 48 8d 98 f0 00 00 00         	leaq	0xf0(%rax), %rbx
    50a7: 48 89 df                     	movq	%rbx, %rdi
    50aa: e8 81 e3 ff ff               	callq	0x3430 <wl_list_remove@plt>
    50af: 48 8d 7d 28                  	leaq	0x28(%rbp), %rdi
    50b3: 48 89 de                     	movq	%rbx, %rsi
    50b6: e8 e5 e5 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    50bb: eb bc                        	jmp	0x5079 <ivi_layout_screen_add_layer+0x69>
    50bd: 48 8d 3d 7c 7e 00 00         	leaq	0x7e7c(%rip), %rdi      # 0xcf40 <zwp_input_panel_v1_interface+0xcf40>
    50c4: 31 c0                        	xorl	%eax, %eax
    50c6: e8 45 e1 ff ff               	callq	0x3210 <weston_log@plt>
    50cb: 31 c0                        	xorl	%eax, %eax
    50cd: eb b3                        	jmp	0x5082 <ivi_layout_screen_add_layer+0x72>
    50cf: 48 8d 3d 3a 7e 00 00         	leaq	0x7e3a(%rip), %rdi      # 0xcf10 <zwp_input_panel_v1_interface+0xcf10>
    50d6: 31 c0                        	xorl	%eax, %eax
    50d8: e8 33 e1 ff ff               	callq	0x3210 <weston_log@plt>
    50dd: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    50e2: eb 9e                        	jmp	0x5082 <ivi_layout_screen_add_layer+0x72>
    50e4: e8 37 e1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    50e9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000050f0 <ivi_layout_layer_add_surface>:
    50f0: 55                           	pushq	%rbp
    50f1: 53                           	pushq	%rbx
    50f2: 48 83 ec 18                  	subq	$0x18, %rsp
    50f6: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    50ff: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5104: 31 c0                        	xorl	%eax, %eax
    5106: 48 85 ff                     	testq	%rdi, %rdi
    5109: 0f 84 a3 00 00 00            	je	0x51b2 <ivi_layout_layer_add_surface+0xc2>
    510f: 48 85 f6                     	testq	%rsi, %rsi
    5112: 0f 84 9a 00 00 00            	je	0x51b2 <ivi_layout_layer_add_surface+0xc2>
    5118: 48 89 fd                     	movq	%rdi, %rbp
    511b: 48 3b 7e 30                  	cmpq	0x30(%rsi), %rdi
    511f: 74 7f                        	je	0x51a0 <ivi_layout_layer_add_surface+0xb0>
    5121: 48 8b 15 e8 c1 20 00         	movq	0x20c1e8(%rip), %rdx    # 0x211310 <ivilayout+0x10>
    5128: 48 8d 0d d9 c1 20 00         	leaq	0x20c1d9(%rip), %rcx    # 0x211308 <ivilayout+0x8>
    512f: 48 8b 42 08                  	movq	0x8(%rdx), %rax
    5133: 48 39 ca                     	cmpq	%rcx, %rdx
    5136: 74 21                        	je	0x5159 <ivi_layout_layer_add_surface+0x69>
    5138: 8b 76 24                     	movl	0x24(%rsi), %esi
    513b: 3b 72 24                     	cmpl	0x24(%rdx), %esi
    513e: 75 10                        	jne	0x5150 <ivi_layout_layer_add_surface+0x60>
    5140: eb 3a                        	jmp	0x517c <ivi_layout_layer_add_surface+0x8c>
    5142: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    5148: 39 70 24                     	cmpl	%esi, 0x24(%rax)
    514b: 74 33                        	je	0x5180 <ivi_layout_layer_add_surface+0x90>
    514d: 48 89 d0                     	movq	%rdx, %rax
    5150: 48 8b 50 08                  	movq	0x8(%rax), %rdx
    5154: 48 39 c8                     	cmpq	%rcx, %rax
    5157: 75 ef                        	jne	0x5148 <ivi_layout_layer_add_surface+0x58>
    5159: c7 85 00 01 00 00 01 00 00 00	movl	$0x1, 0x100(%rbp)
    5163: 31 c0                        	xorl	%eax, %eax
    5165: 48 8b 5c 24 08               	movq	0x8(%rsp), %rbx
    516a: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
    5173: 75 52                        	jne	0x51c7 <ivi_layout_layer_add_surface+0xd7>
    5175: 48 83 c4 18                  	addq	$0x18, %rsp
    5179: 5b                           	popq	%rbx
    517a: 5d                           	popq	%rbp
    517b: c3                           	retq
    517c: 48 89 d0                     	movq	%rdx, %rax
    517f: 90                           	nop
    5180: 48 8d 98 28 01 00 00         	leaq	0x128(%rax), %rbx
    5187: 48 89 df                     	movq	%rbx, %rdi
    518a: e8 a1 e2 ff ff               	callq	0x3430 <wl_list_remove@plt>
    518f: 48 8d bd e0 00 00 00         	leaq	0xe0(%rbp), %rdi
    5196: 48 89 de                     	movq	%rbx, %rsi
    5199: e8 02 e5 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    519e: eb b9                        	jmp	0x5159 <ivi_layout_layer_add_surface+0x69>
    51a0: 48 8d 3d 09 7e 00 00         	leaq	0x7e09(%rip), %rdi      # 0xcfb0 <zwp_input_panel_v1_interface+0xcfb0>
    51a7: 31 c0                        	xorl	%eax, %eax
    51a9: e8 62 e0 ff ff               	callq	0x3210 <weston_log@plt>
    51ae: 31 c0                        	xorl	%eax, %eax
    51b0: eb b3                        	jmp	0x5165 <ivi_layout_layer_add_surface+0x75>
    51b2: 48 8d 3d c7 7d 00 00         	leaq	0x7dc7(%rip), %rdi      # 0xcf80 <zwp_input_panel_v1_interface+0xcf80>
    51b9: 31 c0                        	xorl	%eax, %eax
    51bb: e8 50 e0 ff ff               	callq	0x3210 <weston_log@plt>
    51c0: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    51c5: eb 9e                        	jmp	0x5165 <ivi_layout_layer_add_surface+0x75>
    51c7: e8 54 e0 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    51cc: 0f 1f 40 00                  	nopl	(%rax)

00000000000051d0 <ivi_layout_layer_remove_surface>:
    51d0: 55                           	pushq	%rbp
    51d1: 53                           	pushq	%rbx
    51d2: 48 83 ec 18                  	subq	$0x18, %rsp
    51d6: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    51df: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    51e4: 31 c0                        	xorl	%eax, %eax
    51e6: 48 85 ff                     	testq	%rdi, %rdi
    51e9: 0f 84 99 00 00 00            	je	0x5288 <ivi_layout_layer_remove_surface+0xb8>
    51ef: 48 85 f6                     	testq	%rsi, %rsi
    51f2: 0f 84 90 00 00 00            	je	0x5288 <ivi_layout_layer_remove_surface+0xb8>
    51f8: 48 8b 9f e8 00 00 00         	movq	0xe8(%rdi), %rbx
    51ff: 48 89 fd                     	movq	%rdi, %rbp
    5202: 48 8d bf e0 00 00 00         	leaq	0xe0(%rdi), %rdi
    5209: 48 8b 43 08                  	movq	0x8(%rbx), %rax
    520d: 48 2d 28 01 00 00            	subq	$0x128, %rax            # imm = 0x128
    5213: 48 39 df                     	cmpq	%rbx, %rdi
    5216: 74 34                        	je	0x524c <ivi_layout_layer_remove_surface+0x7c>
    5218: 8b 76 24                     	movl	0x24(%rsi), %esi
    521b: 39 b3 fc fe ff ff            	cmpl	%esi, -0x104(%rbx)
    5221: 75 0f                        	jne	0x5232 <ivi_layout_layer_remove_surface+0x62>
    5223: eb 4b                        	jmp	0x5270 <ivi_layout_layer_remove_surface+0xa0>
    5225: 0f 1f 00                     	nopl	(%rax)
    5228: 8b 48 24                     	movl	0x24(%rax), %ecx
    522b: 48 89 d0                     	movq	%rdx, %rax
    522e: 39 f1                        	cmpl	%esi, %ecx
    5230: 74 3e                        	je	0x5270 <ivi_layout_layer_remove_surface+0xa0>
    5232: 48 8b 88 30 01 00 00         	movq	0x130(%rax), %rcx
    5239: 48 8d 98 28 01 00 00         	leaq	0x128(%rax), %rbx
    5240: 48 8d 91 d8 fe ff ff         	leaq	-0x128(%rcx), %rdx
    5247: 48 39 fb                     	cmpq	%rdi, %rbx
    524a: 75 dc                        	jne	0x5228 <ivi_layout_layer_remove_surface+0x58>
    524c: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    5251: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    525a: c7 85 00 01 00 00 01 00 00 00	movl	$0x1, 0x100(%rbp)
    5264: 75 46                        	jne	0x52ac <ivi_layout_layer_remove_surface+0xdc>
    5266: 48 83 c4 18                  	addq	$0x18, %rsp
    526a: 5b                           	popq	%rbx
    526b: 5d                           	popq	%rbp
    526c: c3                           	retq
    526d: 0f 1f 00                     	nopl	(%rax)
    5270: 48 89 df                     	movq	%rbx, %rdi
    5273: e8 b8 e1 ff ff               	callq	0x3430 <wl_list_remove@plt>
    5278: 48 89 df                     	movq	%rbx, %rdi
    527b: e8 c0 e0 ff ff               	callq	0x3340 <wl_list_init@plt>
    5280: eb ca                        	jmp	0x524c <ivi_layout_layer_remove_surface+0x7c>
    5282: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    5288: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    528d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    5296: 75 14                        	jne	0x52ac <ivi_layout_layer_remove_surface+0xdc>
    5298: 48 8d 3d 51 7d 00 00         	leaq	0x7d51(%rip), %rdi      # 0xcff0 <zwp_input_panel_v1_interface+0xcff0>
    529f: 48 83 c4 18                  	addq	$0x18, %rsp
    52a3: 31 c0                        	xorl	%eax, %eax
    52a5: 5b                           	popq	%rbx
    52a6: 5d                           	popq	%rbp
    52a7: e9 64 df ff ff               	jmp	0x3210 <weston_log@plt>
    52ac: e8 6f df ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    52b1: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    52b6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000052c0 <ivi_layout_screen_set_render_order>:
    52c0: 41 57                        	pushq	%r15
    52c2: 41 56                        	pushq	%r14
    52c4: 41 55                        	pushq	%r13
    52c6: 41 54                        	pushq	%r12
    52c8: 55                           	pushq	%rbp
    52c9: 53                           	pushq	%rbx
    52ca: 48 83 ec 18                  	subq	$0x18, %rsp
    52ce: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    52d7: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    52dc: 31 c0                        	xorl	%eax, %eax
    52de: 48 85 ff                     	testq	%rdi, %rdi
    52e1: 0f 84 f3 00 00 00            	je	0x53da <ivi_layout_screen_set_render_order+0x11a>
    52e7: 48 8b 5f 30                  	movq	0x30(%rdi), %rbx
    52eb: 48 8d 6f 28                  	leaq	0x28(%rdi), %rbp
    52ef: 49 89 fd                     	movq	%rdi, %r13
    52f2: 49 89 f7                     	movq	%rsi, %r15
    52f5: 41 89 d4                     	movl	%edx, %r12d
    52f8: 48 8b 43 08                  	movq	0x8(%rbx), %rax
    52fc: 4c 8d b0 10 ff ff ff         	leaq	-0xf0(%rax), %r14
    5303: 48 39 eb                     	cmpq	%rbp, %rbx
    5306: 74 32                        	je	0x533a <ivi_layout_screen_set_render_order+0x7a>
    5308: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    5310: 48 89 df                     	movq	%rbx, %rdi
    5313: e8 18 e1 ff ff               	callq	0x3430 <wl_list_remove@plt>
    5318: 48 89 df                     	movq	%rbx, %rdi
    531b: e8 20 e0 ff ff               	callq	0x3340 <wl_list_init@plt>
    5320: 49 8b 86 f8 00 00 00         	movq	0xf8(%r14), %rax
    5327: 49 8d 9e f0 00 00 00         	leaq	0xf0(%r14), %rbx
    532e: 4c 8d b0 10 ff ff ff         	leaq	-0xf0(%rax), %r14
    5335: 48 39 eb                     	cmpq	%rbp, %rbx
    5338: 75 d6                        	jne	0x5310 <ivi_layout_screen_set_render_order+0x50>
    533a: 48 89 ef                     	movq	%rbp, %rdi
    533d: e8 ae e0 ff ff               	callq	0x33f0 <wl_list_empty@plt>
    5342: 85 c0                        	testl	%eax, %eax
    5344: 0f 84 a8 00 00 00            	je	0x53f2 <ivi_layout_screen_set_render_order+0x132>
    534a: 45 85 e4                     	testl	%r12d, %r12d
    534d: 7e 62                        	jle	0x53b1 <ivi_layout_screen_set_render_order+0xf1>
    534f: 41 8d 44 24 ff               	leal	-0x1(%r12), %eax
    5354: 4d 8d 64 c7 08               	leaq	0x8(%r15,%rax,8), %r12
    5359: 4c 8d 35 b8 bf 20 00         	leaq	0x20bfb8(%rip), %r14    # 0x211318 <ivilayout+0x18>
    5360: 48 8b 3d b9 bf 20 00         	movq	0x20bfb9(%rip), %rdi    # 0x211320 <ivilayout+0x20>
    5367: 49 8b 07                     	movq	(%r15), %rax
    536a: 4c 39 f7                     	cmpq	%r14, %rdi
    536d: 74 39                        	je	0x53a8 <ivi_layout_screen_set_render_order+0xe8>
    536f: 8b 40 20                     	movl	0x20(%rax), %eax
    5372: 3b 47 20                     	cmpl	0x20(%rdi), %eax
    5375: 74 17                        	je	0x538e <ivi_layout_screen_set_render_order+0xce>
    5377: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    5380: 48 8b 7f 08                  	movq	0x8(%rdi), %rdi
    5384: 4c 39 f7                     	cmpq	%r14, %rdi
    5387: 74 1f                        	je	0x53a8 <ivi_layout_screen_set_render_order+0xe8>
    5389: 39 47 20                     	cmpl	%eax, 0x20(%rdi)
    538c: 75 f2                        	jne	0x5380 <ivi_layout_screen_set_render_order+0xc0>
    538e: 48 8d 9f f0 00 00 00         	leaq	0xf0(%rdi), %rbx
    5395: 48 89 df                     	movq	%rbx, %rdi
    5398: e8 93 e0 ff ff               	callq	0x3430 <wl_list_remove@plt>
    539d: 48 89 de                     	movq	%rbx, %rsi
    53a0: 48 89 ef                     	movq	%rbp, %rdi
    53a3: e8 f8 e2 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    53a8: 49 83 c7 08                  	addq	$0x8, %r15
    53ac: 4d 39 fc                     	cmpq	%r15, %r12
    53af: 75 af                        	jne	0x5360 <ivi_layout_screen_set_render_order+0xa0>
    53b1: 41 c7 45 48 01 00 00 00      	movl	$0x1, 0x48(%r13)
    53b9: 31 c0                        	xorl	%eax, %eax
    53bb: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    53c0: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    53c9: 75 22                        	jne	0x53ed <ivi_layout_screen_set_render_order+0x12d>
    53cb: 48 83 c4 18                  	addq	$0x18, %rsp
    53cf: 5b                           	popq	%rbx
    53d0: 5d                           	popq	%rbp
    53d1: 41 5c                        	popq	%r12
    53d3: 41 5d                        	popq	%r13
    53d5: 41 5e                        	popq	%r14
    53d7: 41 5f                        	popq	%r15
    53d9: c3                           	retq
    53da: 48 8d 3d 47 7c 00 00         	leaq	0x7c47(%rip), %rdi      # 0xd028 <zwp_input_panel_v1_interface+0xd028>
    53e1: e8 2a de ff ff               	callq	0x3210 <weston_log@plt>
    53e6: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    53eb: eb ce                        	jmp	0x53bb <ivi_layout_screen_set_render_order+0xfb>
    53ed: e8 2e de ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    53f2: 48 8d 0d e7 82 00 00         	leaq	0x82e7(%rip), %rcx      # 0xd6e0 <__PRETTY_FUNCTION__.13630>
    53f9: ba 17 0a 00 00               	movl	$0xa17, %edx            # imm = 0xA17
    53fe: 48 8d 35 98 81 00 00         	leaq	0x8198(%rip), %rsi      # 0xd59d <zwp_input_panel_v1_interface+0xd59d>
    5405: 48 8d 3d 54 7c 00 00         	leaq	0x7c54(%rip), %rdi      # 0xd060 <zwp_input_panel_v1_interface+0xd060>
    540c: e8 af de ff ff               	callq	0x32c0 <__assert_fail@plt>
    5411: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    5416: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000005420 <calc_transformation_matrix>:
    5420: 41 55                        	pushq	%r13
    5422: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    5426: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    542a: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    542e: 41 54                        	pushq	%r12
    5430: 41 89 d5                     	movl	%edx, %r13d
    5433: 49 89 cc                     	movq	%rcx, %r12
    5436: 55                           	pushq	%rbp
    5437: 48 89 f5                     	movq	%rsi, %rbp
    543a: 53                           	pushq	%rbx
    543b: 48 89 fb                     	movq	%rdi, %rbx
    543e: 48 83 ec 18                  	subq	$0x18, %rsp
    5442: f3 0f 10 1d f6 83 00 00      	movss	0x83f6(%rip), %xmm3     # 0xd840 <__func__.12894+0x30>
    544a: f3 0f 2a 4f 0c               	cvtsi2ssl	0xc(%rdi), %xmm1
    544f: f3 0f 59 0d d9 83 00 00      	mulss	0x83d9(%rip), %xmm1     # 0xd830 <__func__.12894+0x20>
    5457: f3 0f 2a 47 04               	cvtsi2ssl	0x4(%rdi), %xmm0
    545c: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5465: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    546a: 31 c0                        	xorl	%eax, %eax
    546c: f3 0f 2a 17                  	cvtsi2ssl	(%rdi), %xmm2
    5470: f3 0f 58 c1                  	addss	%xmm1, %xmm0
    5474: 0f 28 c8                     	movaps	%xmm0, %xmm1
    5477: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    547b: f3 0f 2a 47 08               	cvtsi2ssl	0x8(%rdi), %xmm0
    5480: 48 89 cf                     	movq	%rcx, %rdi
    5483: f3 0f 59 05 a5 83 00 00      	mulss	0x83a5(%rip), %xmm0     # 0xd830 <__func__.12894+0x20>
    548b: 0f 57 cb                     	xorps	%xmm3, %xmm1
    548e: f3 0f 58 d0                  	addss	%xmm0, %xmm2
    5492: 0f 57 d3                     	xorps	%xmm3, %xmm2
    5495: 0f 28 c2                     	movaps	%xmm2, %xmm0
    5498: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    549c: e8 0f e1 ff ff               	callq	0x35b0 <weston_matrix_translate@plt>
    54a1: 41 8d 45 ff                  	leal	-0x1(%r13), %eax
    54a5: 83 f8 02                     	cmpl	$0x2, %eax
    54a8: 0f 87 f2 00 00 00            	ja	0x55a0 <calc_transformation_matrix+0x180>
    54ae: 48 8d 15 7b 81 00 00         	leaq	0x817b(%rip), %rdx      # 0xd630 <CSWTCH.120>
    54b5: f3 0f 10 0c 82               	movss	(%rdx,%rax,4), %xmm1
    54ba: 48 8d 15 5f 81 00 00         	leaq	0x815f(%rip), %rdx      # 0xd620 <CSWTCH.121>
    54c1: f3 0f 10 04 82               	movss	(%rdx,%rax,4), %xmm0
    54c6: 4c 89 e7                     	movq	%r12, %rdi
    54c9: e8 b2 df ff ff               	callq	0x3480 <weston_matrix_rotate_xy@plt>
    54ce: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    54d2: 66 0f ef db                  	pxor	%xmm3, %xmm3
    54d6: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    54da: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    54de: f3 0f 2a 53 0c               	cvtsi2ssl	0xc(%rbx), %xmm2
    54e3: f3 0f 2a 5b 08               	cvtsi2ssl	0x8(%rbx), %xmm3
    54e8: f3 0f 2a 4d 0c               	cvtsi2ssl	0xc(%rbp), %xmm1
    54ed: f3 0f 2a 45 08               	cvtsi2ssl	0x8(%rbp), %xmm0
    54f2: 41 83 fd 02                  	cmpl	$0x2, %r13d
    54f6: 74 14                        	je	0x550c <calc_transformation_matrix+0xec>
    54f8: 41 83 fd 03                  	cmpl	$0x3, %r13d
    54fc: 0f 84 8e 00 00 00            	je	0x5590 <calc_transformation_matrix+0x170>
    5502: 41 83 fd 01                  	cmpl	$0x1, %r13d
    5506: 0f 84 84 00 00 00            	je	0x5590 <calc_transformation_matrix+0x170>
    550c: f3 0f 5e c3                  	divss	%xmm3, %xmm0
    5510: f3 0f 5e ca                  	divss	%xmm2, %xmm1
    5514: f3 0f 10 15 10 83 00 00      	movss	0x8310(%rip), %xmm2     # 0xd82c <__func__.12894+0x1c>
    551c: 4c 89 e7                     	movq	%r12, %rdi
    551f: e8 bc e1 ff ff               	callq	0x36e0 <weston_matrix_scale@plt>
    5524: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    5529: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    5532: 75 7d                        	jne	0x55b1 <calc_transformation_matrix+0x191>
    5534: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    5538: 66 0f ef db                  	pxor	%xmm3, %xmm3
    553c: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    5540: f3 0f 2a 4d 0c               	cvtsi2ssl	0xc(%rbp), %xmm1
    5545: f3 0f 2a 5d 04               	cvtsi2ssl	0x4(%rbp), %xmm3
    554a: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    554e: 4c 89 e7                     	movq	%r12, %rdi
    5551: f3 0f 59 0d d7 82 00 00      	mulss	0x82d7(%rip), %xmm1     # 0xd830 <__func__.12894+0x20>
    5559: f3 0f 2a 55 00               	cvtsi2ssl	(%rbp), %xmm2
    555e: f3 0f 2a 45 08               	cvtsi2ssl	0x8(%rbp), %xmm0
    5563: f3 0f 59 05 c5 82 00 00      	mulss	0x82c5(%rip), %xmm0     # 0xd830 <__func__.12894+0x20>
    556b: 48 83 c4 18                  	addq	$0x18, %rsp
    556f: 5b                           	popq	%rbx
    5570: 5d                           	popq	%rbp
    5571: 41 5c                        	popq	%r12
    5573: f3 0f 58 cb                  	addss	%xmm3, %xmm1
    5577: 41 5d                        	popq	%r13
    5579: f3 0f 58 c2                  	addss	%xmm2, %xmm0
    557d: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    5581: e9 2a e0 ff ff               	jmp	0x35b0 <weston_matrix_translate@plt>
    5586: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    5590: f3 0f 5e c2                  	divss	%xmm2, %xmm0
    5594: f3 0f 5e cb                  	divss	%xmm3, %xmm1
    5598: e9 77 ff ff ff               	jmp	0x5514 <calc_transformation_matrix+0xf4>
    559d: 0f 1f 00                     	nopl	(%rax)
    55a0: f3 0f 10 05 84 82 00 00      	movss	0x8284(%rip), %xmm0     # 0xd82c <__func__.12894+0x1c>
    55a8: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    55ac: e9 15 ff ff ff               	jmp	0x54c6 <calc_transformation_matrix+0xa6>
    55b1: e8 6a dc ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    55b6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000055c0 <ivi_layout_get_screens_under_layer>:
    55c0: 41 54                        	pushq	%r12
    55c2: 49 89 d4                     	movq	%rdx, %r12
    55c5: 55                           	pushq	%rbp
    55c6: 53                           	pushq	%rbx
    55c7: 48 83 ec 10                  	subq	$0x10, %rsp
    55cb: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    55d4: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    55d9: 31 c0                        	xorl	%eax, %eax
    55db: 48 85 f6                     	testq	%rsi, %rsi
    55de: 0f 94 c2                     	sete	%dl
    55e1: 4d 85 e4                     	testq	%r12, %r12
    55e4: 0f 94 c0                     	sete	%al
    55e7: 08 c2                        	orb	%al, %dl
    55e9: 75 56                        	jne	0x5641 <ivi_layout_get_screens_under_layer+0x81>
    55eb: 48 89 fb                     	movq	%rdi, %rbx
    55ee: 48 85 ff                     	testq	%rdi, %rdi
    55f1: 74 4e                        	je	0x5641 <ivi_layout_get_screens_under_layer+0x81>
    55f3: 31 c0                        	xorl	%eax, %eax
    55f5: 48 83 7f 30 00               	cmpq	$0x0, 0x30(%rdi)
    55fa: 48 89 f5                     	movq	%rsi, %rbp
    55fd: 74 24                        	je	0x5623 <ivi_layout_get_screens_under_layer+0x63>
    55ff: be 08 00 00 00               	movl	$0x8, %esi
    5604: bf 01 00 00 00               	movl	$0x1, %edi
    5609: e8 62 dd ff ff               	callq	0x3370 <calloc@plt>
    560e: 49 89 04 24                  	movq	%rax, (%r12)
    5612: 48 85 c0                     	testq	%rax, %rax
    5615: 74 3f                        	je	0x5656 <ivi_layout_get_screens_under_layer+0x96>
    5617: 48 8b 53 30                  	movq	0x30(%rbx), %rdx
    561b: 48 89 10                     	movq	%rdx, (%rax)
    561e: b8 01 00 00 00               	movl	$0x1, %eax
    5623: 89 45 00                     	movl	%eax, (%rbp)
    5626: 31 c0                        	xorl	%eax, %eax
    5628: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    562d: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    5636: 75 31                        	jne	0x5669 <ivi_layout_get_screens_under_layer+0xa9>
    5638: 48 83 c4 10                  	addq	$0x10, %rsp
    563c: 5b                           	popq	%rbx
    563d: 5d                           	popq	%rbp
    563e: 41 5c                        	popq	%r12
    5640: c3                           	retq
    5641: 48 8d 3d 48 7a 00 00         	leaq	0x7a48(%rip), %rdi      # 0xd090 <zwp_input_panel_v1_interface+0xd090>
    5648: 31 c0                        	xorl	%eax, %eax
    564a: e8 c1 db ff ff               	callq	0x3210 <weston_log@plt>
    564f: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5654: eb d2                        	jmp	0x5628 <ivi_layout_get_screens_under_layer+0x68>
    5656: 48 8d 3d 26 7f 00 00         	leaq	0x7f26(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    565d: 31 c0                        	xorl	%eax, %eax
    565f: e8 ac db ff ff               	callq	0x3210 <weston_log@plt>
    5664: 83 c8 ff                     	orl	$-0x1, %eax
    5667: eb bf                        	jmp	0x5628 <ivi_layout_get_screens_under_layer+0x68>
    5669: e8 b2 db ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    566e: 66 90                        	nop

0000000000005670 <ivi_layout_get_layers_under_surface>:
    5670: 41 54                        	pushq	%r12
    5672: 49 89 d4                     	movq	%rdx, %r12
    5675: 55                           	pushq	%rbp
    5676: 53                           	pushq	%rbx
    5677: 48 83 ec 10                  	subq	$0x10, %rsp
    567b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5684: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5689: 31 c0                        	xorl	%eax, %eax
    568b: 48 85 f6                     	testq	%rsi, %rsi
    568e: 0f 94 c2                     	sete	%dl
    5691: 4d 85 e4                     	testq	%r12, %r12
    5694: 0f 94 c0                     	sete	%al
    5697: 08 c2                        	orb	%al, %dl
    5699: 75 59                        	jne	0x56f4 <ivi_layout_get_layers_under_surface+0x84>
    569b: 48 89 fb                     	movq	%rdi, %rbx
    569e: 48 85 ff                     	testq	%rdi, %rdi
    56a1: 74 51                        	je	0x56f4 <ivi_layout_get_layers_under_surface+0x84>
    56a3: 48 83 7f 30 00               	cmpq	$0x0, 0x30(%rdi)
    56a8: 48 89 f5                     	movq	%rsi, %rbp
    56ab: 74 43                        	je	0x56f0 <ivi_layout_get_layers_under_surface+0x80>
    56ad: be 08 00 00 00               	movl	$0x8, %esi
    56b2: bf 01 00 00 00               	movl	$0x1, %edi
    56b7: e8 b4 dc ff ff               	callq	0x3370 <calloc@plt>
    56bc: 49 89 04 24                  	movq	%rax, (%r12)
    56c0: 48 85 c0                     	testq	%rax, %rax
    56c3: 74 44                        	je	0x5709 <ivi_layout_get_layers_under_surface+0x99>
    56c5: 48 8b 53 30                  	movq	0x30(%rbx), %rdx
    56c9: 48 89 10                     	movq	%rdx, (%rax)
    56cc: b8 01 00 00 00               	movl	$0x1, %eax
    56d1: 89 45 00                     	movl	%eax, (%rbp)
    56d4: 31 c0                        	xorl	%eax, %eax
    56d6: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    56db: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    56e4: 75 36                        	jne	0x571c <ivi_layout_get_layers_under_surface+0xac>
    56e6: 48 83 c4 10                  	addq	$0x10, %rsp
    56ea: 5b                           	popq	%rbx
    56eb: 5d                           	popq	%rbp
    56ec: 41 5c                        	popq	%r12
    56ee: c3                           	retq
    56ef: 90                           	nop
    56f0: 31 c0                        	xorl	%eax, %eax
    56f2: eb dd                        	jmp	0x56d1 <ivi_layout_get_layers_under_surface+0x61>
    56f4: 48 8d 3d cd 79 00 00         	leaq	0x79cd(%rip), %rdi      # 0xd0c8 <zwp_input_panel_v1_interface+0xd0c8>
    56fb: 31 c0                        	xorl	%eax, %eax
    56fd: e8 0e db ff ff               	callq	0x3210 <weston_log@plt>
    5702: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5707: eb cd                        	jmp	0x56d6 <ivi_layout_get_layers_under_surface+0x66>
    5709: 48 8d 3d 73 7e 00 00         	leaq	0x7e73(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    5710: e8 fb da ff ff               	callq	0x3210 <weston_log@plt>
    5715: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    571a: eb ba                        	jmp	0x56d6 <ivi_layout_get_layers_under_surface+0x66>
    571c: e8 ff da ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5721: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    5726: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000005730 <ivi_layout_surface_create>:
    5730: 41 54                        	pushq	%r12
    5732: 55                           	pushq	%rbp
    5733: 53                           	pushq	%rbx
    5734: 48 83 ec 10                  	subq	$0x10, %rsp
    5738: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5741: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5746: 31 c0                        	xorl	%eax, %eax
    5748: 48 85 ff                     	testq	%rdi, %rdi
    574b: 0f 84 48 02 00 00            	je	0x5999 <ivi_layout_surface_create+0x269>
    5751: 48 8b 05 b8 bb 20 00         	movq	0x20bbb8(%rip), %rax    # 0x211310 <ivilayout+0x10>
    5758: 48 8d 15 a9 bb 20 00         	leaq	0x20bba9(%rip), %rdx    # 0x211308 <ivilayout+0x8>
    575f: 49 89 fc                     	movq	%rdi, %r12
    5762: 89 f5                        	movl	%esi, %ebp
    5764: 48 39 d0                     	cmpq	%rdx, %rax
    5767: 75 10                        	jne	0x5779 <ivi_layout_surface_create+0x49>
    5769: eb 1e                        	jmp	0x5789 <ivi_layout_surface_create+0x59>
    576b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    5770: 48 8b 40 08                  	movq	0x8(%rax), %rax
    5774: 48 39 d0                     	cmpq	%rdx, %rax
    5777: 74 10                        	je	0x5789 <ivi_layout_surface_create+0x59>
    5779: 3b 68 24                     	cmpl	0x24(%rax), %ebp
    577c: 75 f2                        	jne	0x5770 <ivi_layout_surface_create+0x40>
    577e: 48 83 78 38 00               	cmpq	$0x0, 0x38(%rax)
    5783: 0f 85 d7 01 00 00            	jne	0x5960 <ivi_layout_surface_create+0x230>
    5789: be 98 01 00 00               	movl	$0x198, %esi            # imm = 0x198
    578e: bf 01 00 00 00               	movl	$0x1, %edi
    5793: e8 d8 db ff ff               	callq	0x3370 <calloc@plt>
    5798: 48 89 c3                     	movq	%rax, %rbx
    579b: 48 85 c0                     	testq	%rax, %rax
    579e: 0f 84 e3 01 00 00            	je	0x5987 <ivi_layout_surface_create+0x257>
    57a4: 48 8d 78 10                  	leaq	0x10(%rax), %rdi
    57a8: e8 93 db ff ff               	callq	0x3340 <wl_list_init@plt>
    57ad: 48 8d bb 68 01 00 00         	leaq	0x168(%rbx), %rdi
    57b4: e8 87 db ff ff               	callq	0x3340 <wl_list_init@plt>
    57b9: 48 8d 05 40 bb 20 00         	leaq	0x20bb40(%rip), %rax    # 0x211300 <ivilayout>
    57c0: 4c 89 e7                     	movq	%r12, %rdi
    57c3: 89 6b 24                     	movl	%ebp, 0x24(%rbx)
    57c6: 48 89 43 28                  	movq	%rax, 0x28(%rbx)
    57ca: 4c 89 63 38                  	movq	%r12, 0x38(%rbx)
    57ce: e8 3d dc ff ff               	callq	0x3410 <weston_view_create@plt>
    57d3: 48 89 c5                     	movq	%rax, %rbp
    57d6: 48 85 c0                     	testq	%rax, %rax
    57d9: 0f 84 95 01 00 00            	je	0x5974 <ivi_layout_surface_create+0x244>
    57df: 48 8b 43 38                  	movq	0x38(%rbx), %rax
    57e3: 48 89 ab 88 01 00 00         	movq	%rbp, 0x188(%rbx)
    57ea: 48 8d 7b 40                  	leaq	0x40(%rbx), %rdi
    57ee: c6 83 90 01 00 00 00         	movb	$0x0, 0x190(%rbx)
    57f5: 4c 8d 25 5c bb 20 00         	leaq	0x20bb5c(%rip), %r12    # 0x211358 <ivilayout+0x58>
    57fc: c7 80 04 01 00 00 00 00 00 00	movl	$0x0, 0x104(%rax)
    5806: c7 80 08 01 00 00 00 00 00 00	movl	$0x0, 0x108(%rax)
    5810: e8 0b d9 ff ff               	callq	0x3120 <weston_matrix_init@plt>
    5815: 48 8d bb 88 00 00 00         	leaq	0x88(%rbx), %rdi
    581c: e8 1f db ff ff               	callq	0x3340 <wl_list_init@plt>
    5821: 48 8d 93 98 00 00 00         	leaq	0x98(%rbx), %rdx
    5828: 31 c0                        	xorl	%eax, %eax
    582a: b9 08 00 00 00               	movl	$0x8, %ecx
    582f: 48 89 d7                     	movq	%rdx, %rdi
    5832: f3 48 ab                     	rep		stosq	%rax, %es:(%rdi)
    5835: c7 07 00 00 00 00            	movl	$0x0, (%rdi)
    583b: 48 8d bb 28 01 00 00         	leaq	0x128(%rbx), %rdi
    5842: c7 83 98 00 00 00 00 01 00 00	movl	$0x100, 0x98(%rbx)      # imm = 0x100
    584c: 48 8b 83 98 00 00 00         	movq	0x98(%rbx), %rax
    5853: c7 83 c4 00 00 00 01 00 00 00	movl	$0x1, 0xc4(%rbx)
    585d: c7 83 c8 00 00 00 01 00 00 00	movl	$0x1, 0xc8(%rbx)
    5867: c7 83 dc 00 00 00 00 00 00 00	movl	$0x0, 0xdc(%rbx)
    5871: 48 89 83 e0 00 00 00         	movq	%rax, 0xe0(%rbx)
    5878: 48 8b 83 a0 00 00 00         	movq	0xa0(%rbx), %rax
    587f: c7 83 20 01 00 00 00 00 00 00	movl	$0x0, 0x120(%rbx)
    5889: 48 89 83 e8 00 00 00         	movq	%rax, 0xe8(%rbx)
    5890: 48 8b 83 a8 00 00 00         	movq	0xa8(%rbx), %rax
    5897: 48 89 83 f0 00 00 00         	movq	%rax, 0xf0(%rbx)
    589e: 48 8b 83 b0 00 00 00         	movq	0xb0(%rbx), %rax
    58a5: 48 89 83 f8 00 00 00         	movq	%rax, 0xf8(%rbx)
    58ac: 48 8b 83 b8 00 00 00         	movq	0xb8(%rbx), %rax
    58b3: 48 89 83 00 01 00 00         	movq	%rax, 0x100(%rbx)
    58ba: 48 8b 83 c0 00 00 00         	movq	0xc0(%rbx), %rax
    58c1: 48 89 83 08 01 00 00         	movq	%rax, 0x108(%rbx)
    58c8: 48 8b 83 c8 00 00 00         	movq	0xc8(%rbx), %rax
    58cf: 48 89 83 10 01 00 00         	movq	%rax, 0x110(%rbx)
    58d6: 48 8b 83 d0 00 00 00         	movq	0xd0(%rbx), %rax
    58dd: 48 89 83 18 01 00 00         	movq	%rax, 0x118(%rbx)
    58e4: e8 57 da ff ff               	callq	0x3340 <wl_list_init@plt>
    58e9: 48 8d bb 38 01 00 00         	leaq	0x138(%rbx), %rdi
    58f0: e8 4b da ff ff               	callq	0x3340 <wl_list_init@plt>
    58f5: 48 8d bb 48 01 00 00         	leaq	0x148(%rbx), %rdi
    58fc: e8 3f da ff ff               	callq	0x3340 <wl_list_init@plt>
    5901: 48 8d 3d 00 ba 20 00         	leaq	0x20ba00(%rip), %rdi    # 0x211308 <ivilayout+0x8>
    5908: 48 89 de                     	movq	%rbx, %rsi
    590b: e8 90 dd ff ff               	callq	0x36a0 <wl_list_insert@plt>
    5910: 48 8b 05 49 ba 20 00         	movq	0x20ba49(%rip), %rax    # 0x211360 <ivilayout+0x60>
    5917: 48 8b 68 08                  	movq	0x8(%rax), %rbp
    591b: 4c 39 e0                     	cmpq	%r12, %rax
    591e: 75 0b                        	jne	0x592b <ivi_layout_surface_create+0x1fb>
    5920: eb 1e                        	jmp	0x5940 <ivi_layout_surface_create+0x210>
    5922: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    5928: 48 89 d5                     	movq	%rdx, %rbp
    592b: 48 89 c7                     	movq	%rax, %rdi
    592e: 48 89 de                     	movq	%rbx, %rsi
    5931: ff 50 10                     	callq	*0x10(%rax)
    5934: 48 8b 55 08                  	movq	0x8(%rbp), %rdx
    5938: 48 89 e8                     	movq	%rbp, %rax
    593b: 4c 39 e5                     	cmpq	%r12, %rbp
    593e: 75 e8                        	jne	0x5928 <ivi_layout_surface_create+0x1f8>
    5940: 48 89 d8                     	movq	%rbx, %rax
    5943: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    5948: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    5951: 75 56                        	jne	0x59a9 <ivi_layout_surface_create+0x279>
    5953: 48 83 c4 10                  	addq	$0x10, %rsp
    5957: 5b                           	popq	%rbx
    5958: 5d                           	popq	%rbp
    5959: 41 5c                        	popq	%r12
    595b: c3                           	retq
    595c: 0f 1f 40 00                  	nopl	(%rax)
    5960: 48 8d 3d b9 77 00 00         	leaq	0x77b9(%rip), %rdi      # 0xd120 <zwp_input_panel_v1_interface+0xd120>
    5967: 89 ee                        	movl	%ebp, %esi
    5969: 31 c0                        	xorl	%eax, %eax
    596b: e8 a0 d8 ff ff               	callq	0x3210 <weston_log@plt>
    5970: 31 c0                        	xorl	%eax, %eax
    5972: eb cf                        	jmp	0x5943 <ivi_layout_surface_create+0x213>
    5974: 48 8d 3d 08 7c 00 00         	leaq	0x7c08(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    597b: 31 c0                        	xorl	%eax, %eax
    597d: e8 8e d8 ff ff               	callq	0x3210 <weston_log@plt>
    5982: e9 58 fe ff ff               	jmp	0x57df <ivi_layout_surface_create+0xaf>
    5987: 48 8d 3d f5 7b 00 00         	leaq	0x7bf5(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    598e: 31 c0                        	xorl	%eax, %eax
    5990: e8 7b d8 ff ff               	callq	0x3210 <weston_log@plt>
    5995: 31 c0                        	xorl	%eax, %eax
    5997: eb aa                        	jmp	0x5943 <ivi_layout_surface_create+0x213>
    5999: 48 8d 3d 50 77 00 00         	leaq	0x7750(%rip), %rdi      # 0xd0f0 <zwp_input_panel_v1_interface+0xd0f0>
    59a0: e8 6b d8 ff ff               	callq	0x3210 <weston_log@plt>
    59a5: 31 c0                        	xorl	%eax, %eax
    59a7: eb 9a                        	jmp	0x5943 <ivi_layout_surface_create+0x213>
    59a9: e8 72 d8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    59ae: 66 90                        	nop

00000000000059b0 <ivi_layout_get_layers_on_screen>:
    59b0: 41 56                        	pushq	%r14
    59b2: 41 55                        	pushq	%r13
    59b4: 41 54                        	pushq	%r12
    59b6: 55                           	pushq	%rbp
    59b7: 48 89 d5                     	movq	%rdx, %rbp
    59ba: 53                           	pushq	%rbx
    59bb: 48 83 ec 10                  	subq	$0x10, %rsp
    59bf: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    59c8: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    59cd: 31 c0                        	xorl	%eax, %eax
    59cf: 48 85 f6                     	testq	%rsi, %rsi
    59d2: 0f 94 c2                     	sete	%dl
    59d5: 48 85 ed                     	testq	%rbp, %rbp
    59d8: 0f 94 c0                     	sete	%al
    59db: 08 c2                        	orb	%al, %dl
    59dd: 0f 85 9e 00 00 00            	jne	0x5a81 <ivi_layout_get_layers_on_screen+0xd1>
    59e3: 49 89 fc                     	movq	%rdi, %r12
    59e6: 48 85 ff                     	testq	%rdi, %rdi
    59e9: 0f 84 92 00 00 00            	je	0x5a81 <ivi_layout_get_layers_on_screen+0xd1>
    59ef: 48 8d 5f 50                  	leaq	0x50(%rdi), %rbx
    59f3: 49 89 f6                     	movq	%rsi, %r14
    59f6: 48 89 df                     	movq	%rbx, %rdi
    59f9: e8 92 db ff ff               	callq	0x3590 <wl_list_length@plt>
    59fe: 41 89 c5                     	movl	%eax, %r13d
    5a01: 85 c0                        	testl	%eax, %eax
    5a03: 75 2b                        	jne	0x5a30 <ivi_layout_get_layers_on_screen+0x80>
    5a05: 45 89 2e                     	movl	%r13d, (%r14)
    5a08: 31 c0                        	xorl	%eax, %eax
    5a0a: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
    5a0f: 64 48 33 3c 25 28 00 00 00   	xorq	%fs:0x28, %rdi
    5a18: 0f 85 91 00 00 00            	jne	0x5aaf <ivi_layout_get_layers_on_screen+0xff>
    5a1e: 48 83 c4 10                  	addq	$0x10, %rsp
    5a22: 5b                           	popq	%rbx
    5a23: 5d                           	popq	%rbp
    5a24: 41 5c                        	popq	%r12
    5a26: 41 5d                        	popq	%r13
    5a28: 41 5e                        	popq	%r14
    5a2a: c3                           	retq
    5a2b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    5a30: 48 63 f8                     	movslq	%eax, %rdi
    5a33: be 08 00 00 00               	movl	$0x8, %esi
    5a38: e8 33 d9 ff ff               	callq	0x3370 <calloc@plt>
    5a3d: 48 89 45 00                  	movq	%rax, (%rbp)
    5a41: 48 85 c0                     	testq	%rax, %rax
    5a44: 74 53                        	je	0x5a99 <ivi_layout_get_layers_on_screen+0xe9>
    5a46: 49 8b 54 24 58               	movq	0x58(%r12), %rdx
    5a4b: 48 8d 8a e8 fe ff ff         	leaq	-0x118(%rdx), %rcx
    5a52: 48 39 d3                     	cmpq	%rdx, %rbx
    5a55: 74 ae                        	je	0x5a05 <ivi_layout_get_layers_on_screen+0x55>
    5a57: 31 f6                        	xorl	%esi, %esi
    5a59: eb 09                        	jmp	0x5a64 <ivi_layout_get_layers_on_screen+0xb4>
    5a5b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    5a60: 48 8b 45 00                  	movq	(%rbp), %rax
    5a64: 48 89 0c 30                  	movq	%rcx, (%rax,%rsi)
    5a68: 48 8b 81 20 01 00 00         	movq	0x120(%rcx), %rax
    5a6f: 48 83 c6 08                  	addq	$0x8, %rsi
    5a73: 48 8d 88 e8 fe ff ff         	leaq	-0x118(%rax), %rcx
    5a7a: 48 39 c3                     	cmpq	%rax, %rbx
    5a7d: 75 e1                        	jne	0x5a60 <ivi_layout_get_layers_on_screen+0xb0>
    5a7f: eb 84                        	jmp	0x5a05 <ivi_layout_get_layers_on_screen+0x55>
    5a81: 48 8d 3d c0 76 00 00         	leaq	0x76c0(%rip), %rdi      # 0xd148 <zwp_input_panel_v1_interface+0xd148>
    5a88: 31 c0                        	xorl	%eax, %eax
    5a8a: e8 81 d7 ff ff               	callq	0x3210 <weston_log@plt>
    5a8f: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5a94: e9 71 ff ff ff               	jmp	0x5a0a <ivi_layout_get_layers_on_screen+0x5a>
    5a99: 48 8d 3d e3 7a 00 00         	leaq	0x7ae3(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    5aa0: e8 6b d7 ff ff               	callq	0x3210 <weston_log@plt>
    5aa5: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5aaa: e9 5b ff ff ff               	jmp	0x5a0a <ivi_layout_get_layers_on_screen+0x5a>
    5aaf: e8 6c d7 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5ab4: 66 90                        	nop
    5ab6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000005ac0 <ivi_layout_get_surfaces_on_layer>:
    5ac0: 41 56                        	pushq	%r14
    5ac2: 41 55                        	pushq	%r13
    5ac4: 41 54                        	pushq	%r12
    5ac6: 55                           	pushq	%rbp
    5ac7: 48 89 d5                     	movq	%rdx, %rbp
    5aca: 53                           	pushq	%rbx
    5acb: 48 83 ec 10                  	subq	$0x10, %rsp
    5acf: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5ad8: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5add: 31 c0                        	xorl	%eax, %eax
    5adf: 48 85 f6                     	testq	%rsi, %rsi
    5ae2: 0f 94 c2                     	sete	%dl
    5ae5: 48 85 ed                     	testq	%rbp, %rbp
    5ae8: 0f 94 c0                     	sete	%al
    5aeb: 08 c2                        	orb	%al, %dl
    5aed: 0f 85 a1 00 00 00            	jne	0x5b94 <ivi_layout_get_surfaces_on_layer+0xd4>
    5af3: 49 89 fc                     	movq	%rdi, %r12
    5af6: 48 85 ff                     	testq	%rdi, %rdi
    5af9: 0f 84 95 00 00 00            	je	0x5b94 <ivi_layout_get_surfaces_on_layer+0xd4>
    5aff: 48 8d 9f 08 01 00 00         	leaq	0x108(%rdi), %rbx
    5b06: 49 89 f6                     	movq	%rsi, %r14
    5b09: 48 89 df                     	movq	%rbx, %rdi
    5b0c: e8 7f da ff ff               	callq	0x3590 <wl_list_length@plt>
    5b11: 41 89 c5                     	movl	%eax, %r13d
    5b14: 85 c0                        	testl	%eax, %eax
    5b16: 75 28                        	jne	0x5b40 <ivi_layout_get_surfaces_on_layer+0x80>
    5b18: 45 89 2e                     	movl	%r13d, (%r14)
    5b1b: 31 c0                        	xorl	%eax, %eax
    5b1d: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
    5b22: 64 48 33 3c 25 28 00 00 00   	xorq	%fs:0x28, %rdi
    5b2b: 0f 85 91 00 00 00            	jne	0x5bc2 <ivi_layout_get_surfaces_on_layer+0x102>
    5b31: 48 83 c4 10                  	addq	$0x10, %rsp
    5b35: 5b                           	popq	%rbx
    5b36: 5d                           	popq	%rbp
    5b37: 41 5c                        	popq	%r12
    5b39: 41 5d                        	popq	%r13
    5b3b: 41 5e                        	popq	%r14
    5b3d: c3                           	retq
    5b3e: 66 90                        	nop
    5b40: 48 63 f8                     	movslq	%eax, %rdi
    5b43: be 08 00 00 00               	movl	$0x8, %esi
    5b48: e8 23 d8 ff ff               	callq	0x3370 <calloc@plt>
    5b4d: 48 89 45 00                  	movq	%rax, (%rbp)
    5b51: 48 85 c0                     	testq	%rax, %rax
    5b54: 74 56                        	je	0x5bac <ivi_layout_get_surfaces_on_layer+0xec>
    5b56: 49 8b 94 24 10 01 00 00      	movq	0x110(%r12), %rdx
    5b5e: 48 8d 8a c8 fe ff ff         	leaq	-0x138(%rdx), %rcx
    5b65: 48 39 d3                     	cmpq	%rdx, %rbx
    5b68: 74 ae                        	je	0x5b18 <ivi_layout_get_surfaces_on_layer+0x58>
    5b6a: 31 f6                        	xorl	%esi, %esi
    5b6c: eb 06                        	jmp	0x5b74 <ivi_layout_get_surfaces_on_layer+0xb4>
    5b6e: 66 90                        	nop
    5b70: 48 8b 45 00                  	movq	(%rbp), %rax
    5b74: 48 89 0c 30                  	movq	%rcx, (%rax,%rsi)
    5b78: 48 8b 81 40 01 00 00         	movq	0x140(%rcx), %rax
    5b7f: 48 83 c6 08                  	addq	$0x8, %rsi
    5b83: 48 8d 88 c8 fe ff ff         	leaq	-0x138(%rax), %rcx
    5b8a: 48 39 c3                     	cmpq	%rax, %rbx
    5b8d: 75 e1                        	jne	0x5b70 <ivi_layout_get_surfaces_on_layer+0xb0>
    5b8f: e9 84 ff ff ff               	jmp	0x5b18 <ivi_layout_get_surfaces_on_layer+0x58>
    5b94: 48 8d 3d e5 75 00 00         	leaq	0x75e5(%rip), %rdi      # 0xd180 <zwp_input_panel_v1_interface+0xd180>
    5b9b: 31 c0                        	xorl	%eax, %eax
    5b9d: e8 6e d6 ff ff               	callq	0x3210 <weston_log@plt>
    5ba2: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5ba7: e9 71 ff ff ff               	jmp	0x5b1d <ivi_layout_get_surfaces_on_layer+0x5d>
    5bac: 48 8d 3d d0 79 00 00         	leaq	0x79d0(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    5bb3: e8 58 d6 ff ff               	callq	0x3210 <weston_log@plt>
    5bb8: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5bbd: e9 5b ff ff ff               	jmp	0x5b1d <ivi_layout_get_surfaces_on_layer+0x5d>
    5bc2: e8 59 d6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5bc7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000005bd0 <ivi_layout_get_screens>:
    5bd0: 41 54                        	pushq	%r12
    5bd2: 55                           	pushq	%rbp
    5bd3: 53                           	pushq	%rbx
    5bd4: 48 83 ec 10                  	subq	$0x10, %rsp
    5bd8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5be1: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5be6: 31 c0                        	xorl	%eax, %eax
    5be8: 48 85 ff                     	testq	%rdi, %rdi
    5beb: 0f 84 8f 00 00 00            	je	0x5c80 <ivi_layout_get_screens+0xb0>
    5bf1: 48 89 f3                     	movq	%rsi, %rbx
    5bf4: 48 85 f6                     	testq	%rsi, %rsi
    5bf7: 0f 84 83 00 00 00            	je	0x5c80 <ivi_layout_get_screens+0xb0>
    5bfd: 49 89 fc                     	movq	%rdi, %r12
    5c00: 48 8d 3d 21 b7 20 00         	leaq	0x20b721(%rip), %rdi    # 0x211328 <ivilayout+0x28>
    5c07: e8 84 d9 ff ff               	callq	0x3590 <wl_list_length@plt>
    5c0c: 89 c5                        	movl	%eax, %ebp
    5c0e: 85 c0                        	testl	%eax, %eax
    5c10: 75 26                        	jne	0x5c38 <ivi_layout_get_screens+0x68>
    5c12: 41 89 2c 24                  	movl	%ebp, (%r12)
    5c16: 31 c0                        	xorl	%eax, %eax
    5c18: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
    5c1d: 64 48 33 3c 25 28 00 00 00   	xorq	%fs:0x28, %rdi
    5c26: 0f 85 82 00 00 00            	jne	0x5cae <ivi_layout_get_screens+0xde>
    5c2c: 48 83 c4 10                  	addq	$0x10, %rsp
    5c30: 5b                           	popq	%rbx
    5c31: 5d                           	popq	%rbp
    5c32: 41 5c                        	popq	%r12
    5c34: c3                           	retq
    5c35: 0f 1f 00                     	nopl	(%rax)
    5c38: 48 63 f8                     	movslq	%eax, %rdi
    5c3b: be 08 00 00 00               	movl	$0x8, %esi
    5c40: e8 2b d7 ff ff               	callq	0x3370 <calloc@plt>
    5c45: 48 89 03                     	movq	%rax, (%rbx)
    5c48: 48 85 c0                     	testq	%rax, %rax
    5c4b: 74 4b                        	je	0x5c98 <ivi_layout_get_screens+0xc8>
    5c4d: 48 8b 15 dc b6 20 00         	movq	0x20b6dc(%rip), %rdx    # 0x211330 <ivilayout+0x30>
    5c54: 48 8d 35 cd b6 20 00         	leaq	0x20b6cd(%rip), %rsi    # 0x211328 <ivilayout+0x28>
    5c5b: 48 39 f2                     	cmpq	%rsi, %rdx
    5c5e: 74 b2                        	je	0x5c12 <ivi_layout_get_screens+0x42>
    5c60: 31 c9                        	xorl	%ecx, %ecx
    5c62: eb 07                        	jmp	0x5c6b <ivi_layout_get_screens+0x9b>
    5c64: 0f 1f 40 00                  	nopl	(%rax)
    5c68: 48 8b 03                     	movq	(%rbx), %rax
    5c6b: 48 89 14 08                  	movq	%rdx, (%rax,%rcx)
    5c6f: 48 8b 52 08                  	movq	0x8(%rdx), %rdx
    5c73: 48 83 c1 08                  	addq	$0x8, %rcx
    5c77: 48 39 f2                     	cmpq	%rsi, %rdx
    5c7a: 75 ec                        	jne	0x5c68 <ivi_layout_get_screens+0x98>
    5c7c: eb 94                        	jmp	0x5c12 <ivi_layout_get_screens+0x42>
    5c7e: 66 90                        	nop
    5c80: 48 8d 3d 31 75 00 00         	leaq	0x7531(%rip), %rdi      # 0xd1b8 <zwp_input_panel_v1_interface+0xd1b8>
    5c87: 31 c0                        	xorl	%eax, %eax
    5c89: e8 82 d5 ff ff               	callq	0x3210 <weston_log@plt>
    5c8e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5c93: e9 80 ff ff ff               	jmp	0x5c18 <ivi_layout_get_screens+0x48>
    5c98: 48 8d 3d e4 78 00 00         	leaq	0x78e4(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    5c9f: e8 6c d5 ff ff               	callq	0x3210 <weston_log@plt>
    5ca4: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5ca9: e9 6a ff ff ff               	jmp	0x5c18 <ivi_layout_get_screens+0x48>
    5cae: e8 6d d5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5cb3: 0f 1f 00                     	nopl	(%rax)
    5cb6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000005cc0 <ivi_layout_get_layers>:
    5cc0: 41 54                        	pushq	%r12
    5cc2: 55                           	pushq	%rbp
    5cc3: 53                           	pushq	%rbx
    5cc4: 48 83 ec 10                  	subq	$0x10, %rsp
    5cc8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5cd1: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5cd6: 31 c0                        	xorl	%eax, %eax
    5cd8: 48 85 ff                     	testq	%rdi, %rdi
    5cdb: 0f 84 8f 00 00 00            	je	0x5d70 <ivi_layout_get_layers+0xb0>
    5ce1: 48 89 f3                     	movq	%rsi, %rbx
    5ce4: 48 85 f6                     	testq	%rsi, %rsi
    5ce7: 0f 84 83 00 00 00            	je	0x5d70 <ivi_layout_get_layers+0xb0>
    5ced: 49 89 fc                     	movq	%rdi, %r12
    5cf0: 48 8d 3d 21 b6 20 00         	leaq	0x20b621(%rip), %rdi    # 0x211318 <ivilayout+0x18>
    5cf7: e8 94 d8 ff ff               	callq	0x3590 <wl_list_length@plt>
    5cfc: 89 c5                        	movl	%eax, %ebp
    5cfe: 85 c0                        	testl	%eax, %eax
    5d00: 75 26                        	jne	0x5d28 <ivi_layout_get_layers+0x68>
    5d02: 41 89 2c 24                  	movl	%ebp, (%r12)
    5d06: 31 c0                        	xorl	%eax, %eax
    5d08: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
    5d0d: 64 48 33 3c 25 28 00 00 00   	xorq	%fs:0x28, %rdi
    5d16: 0f 85 82 00 00 00            	jne	0x5d9e <ivi_layout_get_layers+0xde>
    5d1c: 48 83 c4 10                  	addq	$0x10, %rsp
    5d20: 5b                           	popq	%rbx
    5d21: 5d                           	popq	%rbp
    5d22: 41 5c                        	popq	%r12
    5d24: c3                           	retq
    5d25: 0f 1f 00                     	nopl	(%rax)
    5d28: 48 63 f8                     	movslq	%eax, %rdi
    5d2b: be 08 00 00 00               	movl	$0x8, %esi
    5d30: e8 3b d6 ff ff               	callq	0x3370 <calloc@plt>
    5d35: 48 89 03                     	movq	%rax, (%rbx)
    5d38: 48 85 c0                     	testq	%rax, %rax
    5d3b: 74 4b                        	je	0x5d88 <ivi_layout_get_layers+0xc8>
    5d3d: 48 8b 15 dc b5 20 00         	movq	0x20b5dc(%rip), %rdx    # 0x211320 <ivilayout+0x20>
    5d44: 48 8d 35 cd b5 20 00         	leaq	0x20b5cd(%rip), %rsi    # 0x211318 <ivilayout+0x18>
    5d4b: 48 39 f2                     	cmpq	%rsi, %rdx
    5d4e: 74 b2                        	je	0x5d02 <ivi_layout_get_layers+0x42>
    5d50: 31 c9                        	xorl	%ecx, %ecx
    5d52: eb 07                        	jmp	0x5d5b <ivi_layout_get_layers+0x9b>
    5d54: 0f 1f 40 00                  	nopl	(%rax)
    5d58: 48 8b 03                     	movq	(%rbx), %rax
    5d5b: 48 89 14 08                  	movq	%rdx, (%rax,%rcx)
    5d5f: 48 8b 52 08                  	movq	0x8(%rdx), %rdx
    5d63: 48 83 c1 08                  	addq	$0x8, %rcx
    5d67: 48 39 f2                     	cmpq	%rsi, %rdx
    5d6a: 75 ec                        	jne	0x5d58 <ivi_layout_get_layers+0x98>
    5d6c: eb 94                        	jmp	0x5d02 <ivi_layout_get_layers+0x42>
    5d6e: 66 90                        	nop
    5d70: 48 8d 3d 71 74 00 00         	leaq	0x7471(%rip), %rdi      # 0xd1e8 <zwp_input_panel_v1_interface+0xd1e8>
    5d77: 31 c0                        	xorl	%eax, %eax
    5d79: e8 92 d4 ff ff               	callq	0x3210 <weston_log@plt>
    5d7e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5d83: e9 80 ff ff ff               	jmp	0x5d08 <ivi_layout_get_layers+0x48>
    5d88: 48 8d 3d f4 77 00 00         	leaq	0x77f4(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    5d8f: e8 7c d4 ff ff               	callq	0x3210 <weston_log@plt>
    5d94: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5d99: e9 6a ff ff ff               	jmp	0x5d08 <ivi_layout_get_layers+0x48>
    5d9e: e8 7d d4 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5da3: 0f 1f 00                     	nopl	(%rax)
    5da6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000005db0 <ivi_layout_get_surfaces>:
    5db0: 41 54                        	pushq	%r12
    5db2: 55                           	pushq	%rbp
    5db3: 53                           	pushq	%rbx
    5db4: 48 83 ec 10                  	subq	$0x10, %rsp
    5db8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5dc1: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5dc6: 31 c0                        	xorl	%eax, %eax
    5dc8: 48 85 ff                     	testq	%rdi, %rdi
    5dcb: 0f 84 8f 00 00 00            	je	0x5e60 <ivi_layout_get_surfaces+0xb0>
    5dd1: 48 89 f3                     	movq	%rsi, %rbx
    5dd4: 48 85 f6                     	testq	%rsi, %rsi
    5dd7: 0f 84 83 00 00 00            	je	0x5e60 <ivi_layout_get_surfaces+0xb0>
    5ddd: 49 89 fc                     	movq	%rdi, %r12
    5de0: 48 8d 3d 21 b5 20 00         	leaq	0x20b521(%rip), %rdi    # 0x211308 <ivilayout+0x8>
    5de7: e8 a4 d7 ff ff               	callq	0x3590 <wl_list_length@plt>
    5dec: 89 c5                        	movl	%eax, %ebp
    5dee: 85 c0                        	testl	%eax, %eax
    5df0: 75 26                        	jne	0x5e18 <ivi_layout_get_surfaces+0x68>
    5df2: 41 89 2c 24                  	movl	%ebp, (%r12)
    5df6: 31 c0                        	xorl	%eax, %eax
    5df8: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
    5dfd: 64 48 33 3c 25 28 00 00 00   	xorq	%fs:0x28, %rdi
    5e06: 0f 85 82 00 00 00            	jne	0x5e8e <ivi_layout_get_surfaces+0xde>
    5e0c: 48 83 c4 10                  	addq	$0x10, %rsp
    5e10: 5b                           	popq	%rbx
    5e11: 5d                           	popq	%rbp
    5e12: 41 5c                        	popq	%r12
    5e14: c3                           	retq
    5e15: 0f 1f 00                     	nopl	(%rax)
    5e18: 48 63 f8                     	movslq	%eax, %rdi
    5e1b: be 08 00 00 00               	movl	$0x8, %esi
    5e20: e8 4b d5 ff ff               	callq	0x3370 <calloc@plt>
    5e25: 48 89 03                     	movq	%rax, (%rbx)
    5e28: 48 85 c0                     	testq	%rax, %rax
    5e2b: 74 4b                        	je	0x5e78 <ivi_layout_get_surfaces+0xc8>
    5e2d: 48 8b 15 dc b4 20 00         	movq	0x20b4dc(%rip), %rdx    # 0x211310 <ivilayout+0x10>
    5e34: 48 8d 35 cd b4 20 00         	leaq	0x20b4cd(%rip), %rsi    # 0x211308 <ivilayout+0x8>
    5e3b: 48 39 f2                     	cmpq	%rsi, %rdx
    5e3e: 74 b2                        	je	0x5df2 <ivi_layout_get_surfaces+0x42>
    5e40: 31 c9                        	xorl	%ecx, %ecx
    5e42: eb 07                        	jmp	0x5e4b <ivi_layout_get_surfaces+0x9b>
    5e44: 0f 1f 40 00                  	nopl	(%rax)
    5e48: 48 8b 03                     	movq	(%rbx), %rax
    5e4b: 48 89 14 08                  	movq	%rdx, (%rax,%rcx)
    5e4f: 48 8b 52 08                  	movq	0x8(%rdx), %rdx
    5e53: 48 83 c1 08                  	addq	$0x8, %rcx
    5e57: 48 39 f2                     	cmpq	%rsi, %rdx
    5e5a: 75 ec                        	jne	0x5e48 <ivi_layout_get_surfaces+0x98>
    5e5c: eb 94                        	jmp	0x5df2 <ivi_layout_get_surfaces+0x42>
    5e5e: 66 90                        	nop
    5e60: 48 8d 3d b1 73 00 00         	leaq	0x73b1(%rip), %rdi      # 0xd218 <zwp_input_panel_v1_interface+0xd218>
    5e67: 31 c0                        	xorl	%eax, %eax
    5e69: e8 a2 d3 ff ff               	callq	0x3210 <weston_log@plt>
    5e6e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5e73: e9 80 ff ff ff               	jmp	0x5df8 <ivi_layout_get_surfaces+0x48>
    5e78: 48 8d 3d 04 77 00 00         	leaq	0x7704(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    5e7f: e8 8c d3 ff ff               	callq	0x3210 <weston_log@plt>
    5e84: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5e89: e9 6a ff ff ff               	jmp	0x5df8 <ivi_layout_get_surfaces+0x48>
    5e8e: e8 8d d3 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5e93: 0f 1f 00                     	nopl	(%rax)
    5e96: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000005ea0 <ivi_layout_surface_request_resize>:
    5ea0: 41 54                        	pushq	%r12
    5ea2: 55                           	pushq	%rbp
    5ea3: 53                           	pushq	%rbx
    5ea4: 48 83 ec 10                  	subq	$0x10, %rsp
    5ea8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5eb1: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5eb6: 31 c0                        	xorl	%eax, %eax
    5eb8: 48 85 ff                     	testq	%rdi, %rdi
    5ebb: 74 7b                        	je	0x5f38 <ivi_layout_surface_request_resize+0x98>
    5ebd: 48 83 7f 38 00               	cmpq	$0x0, 0x38(%rdi)
    5ec2: 48 89 fd                     	movq	%rdi, %rbp
    5ec5: 74 71                        	je	0x5f38 <ivi_layout_surface_request_resize+0x98>
    5ec7: 48 8b 87 70 01 00 00         	movq	0x170(%rdi), %rax
    5ece: 4c 8d a7 68 01 00 00         	leaq	0x168(%rdi), %r12
    5ed5: c7 87 84 01 00 00 01 00 00 00	movl	$0x1, 0x184(%rdi)
    5edf: 89 b7 78 01 00 00            	movl	%esi, 0x178(%rdi)
    5ee5: 89 97 7c 01 00 00            	movl	%edx, 0x17c(%rdi)
    5eeb: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    5eef: 49 39 c4                     	cmpq	%rax, %r12
    5ef2: 75 0f                        	jne	0x5f03 <ivi_layout_surface_request_resize+0x63>
    5ef4: eb 22                        	jmp	0x5f18 <ivi_layout_surface_request_resize+0x78>
    5ef6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    5f00: 48 89 d3                     	movq	%rdx, %rbx
    5f03: 48 89 c7                     	movq	%rax, %rdi
    5f06: 48 89 ee                     	movq	%rbp, %rsi
    5f09: ff 50 10                     	callq	*0x10(%rax)
    5f0c: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    5f10: 48 89 d8                     	movq	%rbx, %rax
    5f13: 49 39 dc                     	cmpq	%rbx, %r12
    5f16: 75 e8                        	jne	0x5f00 <ivi_layout_surface_request_resize+0x60>
    5f18: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    5f1d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    5f26: 75 3d                        	jne	0x5f65 <ivi_layout_surface_request_resize+0xc5>
    5f28: 48 83 c4 10                  	addq	$0x10, %rsp
    5f2c: 5b                           	popq	%rbx
    5f2d: 5d                           	popq	%rbp
    5f2e: 41 5c                        	popq	%r12
    5f30: c3                           	retq
    5f31: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    5f38: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    5f3d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    5f46: 75 1d                        	jne	0x5f65 <ivi_layout_surface_request_resize+0xc5>
    5f48: 48 8d 35 31 78 00 00         	leaq	0x7831(%rip), %rsi      # 0xd780 <__func__.13766>
    5f4f: 48 83 c4 10                  	addq	$0x10, %rsp
    5f53: 31 c0                        	xorl	%eax, %eax
    5f55: 5b                           	popq	%rbx
    5f56: 48 8d 3d 10 76 00 00         	leaq	0x7610(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    5f5d: 5d                           	popq	%rbp
    5f5e: 41 5c                        	popq	%r12
    5f60: e9 ab d2 ff ff               	jmp	0x3210 <weston_log@plt>
    5f65: e8 b6 d2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5f6a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000005f70 <ivi_layout_layer_set_fade_info>:
    5f70: 48 83 ec 18                  	subq	$0x18, %rsp
    5f74: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5f7d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5f82: 31 c0                        	xorl	%eax, %eax
    5f84: 48 85 ff                     	testq	%rdi, %rdi
    5f87: 74 2d                        	je	0x5fb6 <ivi_layout_layer_set_fade_info+0x46>
    5f89: 89 b7 d8 00 00 00            	movl	%esi, 0xd8(%rdi)
    5f8f: 31 c0                        	xorl	%eax, %eax
    5f91: f2 0f 11 87 c8 00 00 00      	movsd	%xmm0, 0xc8(%rdi)
    5f99: f2 0f 11 8f d0 00 00 00      	movsd	%xmm1, 0xd0(%rdi)
    5fa1: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    5fa6: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    5faf: 75 1f                        	jne	0x5fd0 <ivi_layout_layer_set_fade_info+0x60>
    5fb1: 48 83 c4 18                  	addq	$0x18, %rsp
    5fb5: c3                           	retq
    5fb6: 48 8d 35 53 77 00 00         	leaq	0x7753(%rip), %rsi      # 0xd710 <__func__.13706>
    5fbd: 48 8d 3d a9 75 00 00         	leaq	0x75a9(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    5fc4: e8 47 d2 ff ff               	callq	0x3210 <weston_log@plt>
    5fc9: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    5fce: eb d1                        	jmp	0x5fa1 <ivi_layout_layer_set_fade_info+0x31>
    5fd0: e8 4b d2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    5fd5: 90                           	nop
    5fd6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000005fe0 <ivi_layout_layer_set_transition>:
    5fe0: 48 83 ec 18                  	subq	$0x18, %rsp
    5fe4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    5fed: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    5ff2: 31 c0                        	xorl	%eax, %eax
    5ff4: 48 85 ff                     	testq	%rdi, %rdi
    5ff7: 74 23                        	je	0x601c <ivi_layout_layer_set_transition+0x3c>
    5ff9: 89 b7 bc 00 00 00            	movl	%esi, 0xbc(%rdi)
    5fff: 31 c0                        	xorl	%eax, %eax
    6001: 89 97 c0 00 00 00            	movl	%edx, 0xc0(%rdi)
    6007: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    600c: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    6015: 75 1f                        	jne	0x6036 <ivi_layout_layer_set_transition+0x56>
    6017: 48 83 c4 18                  	addq	$0x18, %rsp
    601b: c3                           	retq
    601c: 48 8d 35 9d 76 00 00         	leaq	0x769d(%rip), %rsi      # 0xd6c0 <__func__.13699>
    6023: 48 8d 3d 43 75 00 00         	leaq	0x7543(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    602a: e8 e1 d1 ff ff               	callq	0x3210 <weston_log@plt>
    602f: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6034: eb d1                        	jmp	0x6007 <ivi_layout_layer_set_transition+0x27>
    6036: e8 e5 d1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    603b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000006040 <ivi_layout_surface_set_transition_duration>:
    6040: 48 83 ec 18                  	subq	$0x18, %rsp
    6044: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    604d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6052: 31 c0                        	xorl	%eax, %eax
    6054: 48 85 ff                     	testq	%rdi, %rdi
    6057: 74 22                        	je	0x607b <ivi_layout_surface_set_transition_duration+0x3b>
    6059: 8d 04 b6                     	leal	(%rsi,%rsi,4), %eax
    605c: 01 c0                        	addl	%eax, %eax
    605e: 89 87 20 01 00 00            	movl	%eax, 0x120(%rdi)
    6064: 31 c0                        	xorl	%eax, %eax
    6066: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    606b: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    6074: 75 1f                        	jne	0x6095 <ivi_layout_surface_set_transition_duration+0x55>
    6076: 48 83 c4 18                  	addq	$0x18, %rsp
    607a: c3                           	retq
    607b: 48 8d 35 fe 75 00 00         	leaq	0x75fe(%rip), %rsi      # 0xd680 <__func__.13712>
    6082: 48 8d 3d e4 74 00 00         	leaq	0x74e4(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    6089: e8 82 d1 ff ff               	callq	0x3210 <weston_log@plt>
    608e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6093: eb d1                        	jmp	0x6066 <ivi_layout_surface_set_transition_duration+0x26>
    6095: e8 86 d1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    609a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000000060a0 <ivi_layout_surface_set_transition>:
    60a0: 48 83 ec 18                  	subq	$0x18, %rsp
    60a4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    60ad: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    60b2: 31 c0                        	xorl	%eax, %eax
    60b4: 48 85 ff                     	testq	%rdi, %rdi
    60b7: 74 23                        	je	0x60dc <ivi_layout_surface_set_transition+0x3c>
    60b9: 89 b7 1c 01 00 00            	movl	%esi, 0x11c(%rdi)
    60bf: 31 c0                        	xorl	%eax, %eax
    60c1: 89 97 20 01 00 00            	movl	%edx, 0x120(%rdi)
    60c7: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    60cc: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    60d5: 75 1f                        	jne	0x60f6 <ivi_layout_surface_set_transition+0x56>
    60d7: 48 83 c4 18                  	addq	$0x18, %rsp
    60db: c3                           	retq
    60dc: 48 8d 35 5d 75 00 00         	leaq	0x755d(%rip), %rsi      # 0xd640 <__func__.13719>
    60e3: 48 8d 3d 83 74 00 00         	leaq	0x7483(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    60ea: e8 21 d1 ff ff               	callq	0x3210 <weston_log@plt>
    60ef: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    60f4: eb d1                        	jmp	0x60c7 <ivi_layout_surface_set_transition+0x27>
    60f6: e8 25 d1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    60fb: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000006100 <add_notification>:
    6100: 41 54                        	pushq	%r12
    6102: 49 89 f4                     	movq	%rsi, %r12
    6105: 55                           	pushq	%rbp
    6106: 48 89 fd                     	movq	%rdi, %rbp
    6109: bf 20 00 00 00               	movl	$0x20, %edi
    610e: 53                           	pushq	%rbx
    610f: 48 89 d3                     	movq	%rdx, %rbx
    6112: 48 83 ec 10                  	subq	$0x10, %rsp
    6116: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    611f: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6124: 31 c0                        	xorl	%eax, %eax
    6126: e8 45 d3 ff ff               	callq	0x3470 <malloc@plt>
    612b: 48 85 c0                     	testq	%rax, %rax
    612e: 74 2f                        	je	0x615f <add_notification+0x5f>
    6130: 48 8b 7d 00                  	movq	(%rbp), %rdi
    6134: 4c 89 60 18                  	movq	%r12, 0x18(%rax)
    6138: 48 8d 70 08                  	leaq	0x8(%rax), %rsi
    613c: 48 89 18                     	movq	%rbx, (%rax)
    613f: e8 5c d5 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    6144: 31 c0                        	xorl	%eax, %eax
    6146: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    614b: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    6154: 75 24                        	jne	0x617a <add_notification+0x7a>
    6156: 48 83 c4 10                  	addq	$0x10, %rsp
    615a: 5b                           	popq	%rbx
    615b: 5d                           	popq	%rbp
    615c: 41 5c                        	popq	%r12
    615e: c3                           	retq
    615f: 48 8d 3d 1d 74 00 00         	leaq	0x741d(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    6166: e8 a5 d0 ff ff               	callq	0x3210 <weston_log@plt>
    616b: 48 89 df                     	movq	%rbx, %rdi
    616e: e8 fd ce ff ff               	callq	0x3070 <free@plt>
    6173: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6178: eb cc                        	jmp	0x6146 <add_notification+0x46>
    617a: e8 a1 d0 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    617f: 90                           	nop

0000000000006180 <ivi_layout_layer_add_notification>:
    6180: 41 54                        	pushq	%r12
    6182: 55                           	pushq	%rbp
    6183: 53                           	pushq	%rbx
    6184: 48 83 ec 10                  	subq	$0x10, %rsp
    6188: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    6191: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6196: 31 c0                        	xorl	%eax, %eax
    6198: 48 85 ff                     	testq	%rdi, %rdi
    619b: 74 53                        	je	0x61f0 <ivi_layout_layer_add_notification+0x70>
    619d: 48 89 f5                     	movq	%rsi, %rbp
    61a0: 48 85 f6                     	testq	%rsi, %rsi
    61a3: 74 4b                        	je	0x61f0 <ivi_layout_layer_add_notification+0x70>
    61a5: 48 89 fb                     	movq	%rdi, %rbx
    61a8: bf 10 00 00 00               	movl	$0x10, %edi
    61ad: 49 89 d4                     	movq	%rdx, %r12
    61b0: e8 bb d2 ff ff               	callq	0x3470 <malloc@plt>
    61b5: 48 85 c0                     	testq	%rax, %rax
    61b8: 74 62                        	je	0x621c <ivi_layout_layer_add_notification+0x9c>
    61ba: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    61bf: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    61c8: 48 89 28                     	movq	%rbp, (%rax)
    61cb: 4c 89 60 08                  	movq	%r12, 0x8(%rax)
    61cf: 75 59                        	jne	0x622a <ivi_layout_layer_add_notification+0xaa>
    61d1: 48 8d 7b 10                  	leaq	0x10(%rbx), %rdi
    61d5: 48 83 c4 10                  	addq	$0x10, %rsp
    61d9: 48 89 c2                     	movq	%rax, %rdx
    61dc: 5b                           	popq	%rbx
    61dd: 48 8d 35 1c d6 ff ff         	leaq	-0x29e4(%rip), %rsi     # 0x3800 <layer_prop_changed>
    61e4: 5d                           	popq	%rbp
    61e5: 41 5c                        	popq	%r12
    61e7: e9 14 ff ff ff               	jmp	0x6100 <add_notification>
    61ec: 0f 1f 40 00                  	nopl	(%rax)
    61f0: 48 8d 3d 51 70 00 00         	leaq	0x7051(%rip), %rdi      # 0xd248 <zwp_input_panel_v1_interface+0xd248>
    61f7: 31 c0                        	xorl	%eax, %eax
    61f9: e8 12 d0 ff ff               	callq	0x3210 <weston_log@plt>
    61fe: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    6203: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    620c: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6211: 75 17                        	jne	0x622a <ivi_layout_layer_add_notification+0xaa>
    6213: 48 83 c4 10                  	addq	$0x10, %rsp
    6217: 5b                           	popq	%rbx
    6218: 5d                           	popq	%rbp
    6219: 41 5c                        	popq	%r12
    621b: c3                           	retq
    621c: 48 8d 3d 60 73 00 00         	leaq	0x7360(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    6223: e8 e8 cf ff ff               	callq	0x3210 <weston_log@plt>
    6228: eb d4                        	jmp	0x61fe <ivi_layout_layer_add_notification+0x7e>
    622a: e8 f1 cf ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    622f: 90                           	nop

0000000000006230 <ivi_layout_add_notification_remove_layer>:
    6230: 55                           	pushq	%rbp
    6231: 53                           	pushq	%rbx
    6232: 48 83 ec 18                  	subq	$0x18, %rsp
    6236: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    623f: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6244: 31 c0                        	xorl	%eax, %eax
    6246: 48 85 ff                     	testq	%rdi, %rdi
    6249: 74 48                        	je	0x6293 <ivi_layout_add_notification_remove_layer+0x63>
    624b: 48 89 fb                     	movq	%rdi, %rbx
    624e: bf 10 00 00 00               	movl	$0x10, %edi
    6253: 48 89 f5                     	movq	%rsi, %rbp
    6256: e8 15 d2 ff ff               	callq	0x3470 <malloc@plt>
    625b: 48 85 c0                     	testq	%rax, %rax
    625e: 74 5b                        	je	0x62bb <ivi_layout_add_notification_remove_layer+0x8b>
    6260: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    6265: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    626e: 48 89 18                     	movq	%rbx, (%rax)
    6271: 48 89 68 08                  	movq	%rbp, 0x8(%rax)
    6275: 75 52                        	jne	0x62c9 <ivi_layout_add_notification_remove_layer+0x99>
    6277: 48 8d 35 d2 d6 ff ff         	leaq	-0x292e(%rip), %rsi     # 0x3950 <layer_removed>
    627e: 48 83 c4 18                  	addq	$0x18, %rsp
    6282: 48 89 c2                     	movq	%rax, %rdx
    6285: 5b                           	popq	%rbx
    6286: 48 8d 3d bb b0 20 00         	leaq	0x20b0bb(%rip), %rdi    # 0x211348 <ivilayout+0x48>
    628d: 5d                           	popq	%rbp
    628e: e9 6d fe ff ff               	jmp	0x6100 <add_notification>
    6293: 48 8d 3d e6 6f 00 00         	leaq	0x6fe6(%rip), %rdi      # 0xd280 <zwp_input_panel_v1_interface+0xd280>
    629a: e8 71 cf ff ff               	callq	0x3210 <weston_log@plt>
    629f: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    62a4: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    62ad: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    62b2: 75 15                        	jne	0x62c9 <ivi_layout_add_notification_remove_layer+0x99>
    62b4: 48 83 c4 18                  	addq	$0x18, %rsp
    62b8: 5b                           	popq	%rbx
    62b9: 5d                           	popq	%rbp
    62ba: c3                           	retq
    62bb: 48 8d 3d c1 72 00 00         	leaq	0x72c1(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    62c2: e8 49 cf ff ff               	callq	0x3210 <weston_log@plt>
    62c7: eb d6                        	jmp	0x629f <ivi_layout_add_notification_remove_layer+0x6f>
    62c9: e8 52 cf ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    62ce: 66 90                        	nop

00000000000062d0 <ivi_layout_add_notification_create_layer>:
    62d0: 55                           	pushq	%rbp
    62d1: 53                           	pushq	%rbx
    62d2: 48 83 ec 18                  	subq	$0x18, %rsp
    62d6: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    62df: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    62e4: 31 c0                        	xorl	%eax, %eax
    62e6: 48 85 ff                     	testq	%rdi, %rdi
    62e9: 74 48                        	je	0x6333 <ivi_layout_add_notification_create_layer+0x63>
    62eb: 48 89 fb                     	movq	%rdi, %rbx
    62ee: bf 10 00 00 00               	movl	$0x10, %edi
    62f3: 48 89 f5                     	movq	%rsi, %rbp
    62f6: e8 75 d1 ff ff               	callq	0x3470 <malloc@plt>
    62fb: 48 85 c0                     	testq	%rax, %rax
    62fe: 74 5b                        	je	0x635b <ivi_layout_add_notification_create_layer+0x8b>
    6300: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    6305: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    630e: 48 89 18                     	movq	%rbx, (%rax)
    6311: 48 89 68 08                  	movq	%rbp, 0x8(%rax)
    6315: 75 52                        	jne	0x6369 <ivi_layout_add_notification_create_layer+0x99>
    6317: 48 8d 35 72 d6 ff ff         	leaq	-0x298e(%rip), %rsi     # 0x3990 <layer_created>
    631e: 48 83 c4 18                  	addq	$0x18, %rsp
    6322: 48 89 c2                     	movq	%rax, %rdx
    6325: 5b                           	popq	%rbx
    6326: 48 8d 3d 0b b0 20 00         	leaq	0x20b00b(%rip), %rdi    # 0x211338 <ivilayout+0x38>
    632d: 5d                           	popq	%rbp
    632e: e9 cd fd ff ff               	jmp	0x6100 <add_notification>
    6333: 48 8d 3d 86 6f 00 00         	leaq	0x6f86(%rip), %rdi      # 0xd2c0 <zwp_input_panel_v1_interface+0xd2c0>
    633a: e8 d1 ce ff ff               	callq	0x3210 <weston_log@plt>
    633f: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    6344: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    634d: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6352: 75 15                        	jne	0x6369 <ivi_layout_add_notification_create_layer+0x99>
    6354: 48 83 c4 18                  	addq	$0x18, %rsp
    6358: 5b                           	popq	%rbx
    6359: 5d                           	popq	%rbp
    635a: c3                           	retq
    635b: 48 8d 3d 21 72 00 00         	leaq	0x7221(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    6362: e8 a9 ce ff ff               	callq	0x3210 <weston_log@plt>
    6367: eb d6                        	jmp	0x633f <ivi_layout_add_notification_create_layer+0x6f>
    6369: e8 b2 ce ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    636e: 66 90                        	nop

0000000000006370 <ivi_layout_add_notification_configure_surface>:
    6370: 55                           	pushq	%rbp
    6371: 53                           	pushq	%rbx
    6372: 48 83 ec 18                  	subq	$0x18, %rsp
    6376: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    637f: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6384: 31 c0                        	xorl	%eax, %eax
    6386: 48 85 ff                     	testq	%rdi, %rdi
    6389: 74 48                        	je	0x63d3 <ivi_layout_add_notification_configure_surface+0x63>
    638b: 48 89 fb                     	movq	%rdi, %rbx
    638e: bf 10 00 00 00               	movl	$0x10, %edi
    6393: 48 89 f5                     	movq	%rsi, %rbp
    6396: e8 d5 d0 ff ff               	callq	0x3470 <malloc@plt>
    639b: 48 85 c0                     	testq	%rax, %rax
    639e: 74 5b                        	je	0x63fb <ivi_layout_add_notification_configure_surface+0x8b>
    63a0: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    63a5: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    63ae: 48 89 18                     	movq	%rbx, (%rax)
    63b1: 48 89 68 08                  	movq	%rbp, 0x8(%rax)
    63b5: 75 52                        	jne	0x6409 <ivi_layout_add_notification_configure_surface+0x99>
    63b7: 48 8d 35 e2 d4 ff ff         	leaq	-0x2b1e(%rip), %rsi     # 0x38a0 <surface_configure_changed>
    63be: 48 83 c4 18                  	addq	$0x18, %rsp
    63c2: 48 89 c2                     	movq	%rax, %rdx
    63c5: 5b                           	popq	%rbx
    63c6: 48 8d 3d ab af 20 00         	leaq	0x20afab(%rip), %rdi    # 0x211378 <ivilayout+0x78>
    63cd: 5d                           	popq	%rbp
    63ce: e9 2d fd ff ff               	jmp	0x6100 <add_notification>
    63d3: 48 8d 3d 26 6f 00 00         	leaq	0x6f26(%rip), %rdi      # 0xd300 <zwp_input_panel_v1_interface+0xd300>
    63da: e8 31 ce ff ff               	callq	0x3210 <weston_log@plt>
    63df: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    63e4: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    63ed: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    63f2: 75 15                        	jne	0x6409 <ivi_layout_add_notification_configure_surface+0x99>
    63f4: 48 83 c4 18                  	addq	$0x18, %rsp
    63f8: 5b                           	popq	%rbx
    63f9: 5d                           	popq	%rbp
    63fa: c3                           	retq
    63fb: 48 8d 3d 81 71 00 00         	leaq	0x7181(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    6402: e8 09 ce ff ff               	callq	0x3210 <weston_log@plt>
    6407: eb d6                        	jmp	0x63df <ivi_layout_add_notification_configure_surface+0x6f>
    6409: e8 12 ce ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    640e: 66 90                        	nop

0000000000006410 <ivi_layout_add_notification_remove_surface>:
    6410: 55                           	pushq	%rbp
    6411: 53                           	pushq	%rbx
    6412: 48 83 ec 18                  	subq	$0x18, %rsp
    6416: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    641f: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6424: 31 c0                        	xorl	%eax, %eax
    6426: 48 85 ff                     	testq	%rdi, %rdi
    6429: 74 48                        	je	0x6473 <ivi_layout_add_notification_remove_surface+0x63>
    642b: 48 89 fb                     	movq	%rdi, %rbx
    642e: bf 10 00 00 00               	movl	$0x10, %edi
    6433: 48 89 f5                     	movq	%rsi, %rbp
    6436: e8 35 d0 ff ff               	callq	0x3470 <malloc@plt>
    643b: 48 85 c0                     	testq	%rax, %rax
    643e: 74 5b                        	je	0x649b <ivi_layout_add_notification_remove_surface+0x8b>
    6440: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    6445: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    644e: 48 89 18                     	movq	%rbx, (%rax)
    6451: 48 89 68 08                  	movq	%rbp, 0x8(%rax)
    6455: 75 52                        	jne	0x64a9 <ivi_layout_add_notification_remove_surface+0x99>
    6457: 48 8d 35 82 d4 ff ff         	leaq	-0x2b7e(%rip), %rsi     # 0x38e0 <surface_removed>
    645e: 48 83 c4 18                  	addq	$0x18, %rsp
    6462: 48 89 c2                     	movq	%rax, %rdx
    6465: 5b                           	popq	%rbx
    6466: 48 8d 3d fb ae 20 00         	leaq	0x20aefb(%rip), %rdi    # 0x211368 <ivilayout+0x68>
    646d: 5d                           	popq	%rbp
    646e: e9 8d fc ff ff               	jmp	0x6100 <add_notification>
    6473: 48 8d 3d ce 6e 00 00         	leaq	0x6ece(%rip), %rdi      # 0xd348 <zwp_input_panel_v1_interface+0xd348>
    647a: e8 91 cd ff ff               	callq	0x3210 <weston_log@plt>
    647f: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    6484: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    648d: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6492: 75 15                        	jne	0x64a9 <ivi_layout_add_notification_remove_surface+0x99>
    6494: 48 83 c4 18                  	addq	$0x18, %rsp
    6498: 5b                           	popq	%rbx
    6499: 5d                           	popq	%rbp
    649a: c3                           	retq
    649b: 48 8d 3d e1 70 00 00         	leaq	0x70e1(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    64a2: e8 69 cd ff ff               	callq	0x3210 <weston_log@plt>
    64a7: eb d6                        	jmp	0x647f <ivi_layout_add_notification_remove_surface+0x6f>
    64a9: e8 72 cd ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    64ae: 66 90                        	nop

00000000000064b0 <ivi_layout_add_notification_create_surface>:
    64b0: 55                           	pushq	%rbp
    64b1: 53                           	pushq	%rbx
    64b2: 48 83 ec 18                  	subq	$0x18, %rsp
    64b6: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    64bf: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    64c4: 31 c0                        	xorl	%eax, %eax
    64c6: 48 85 ff                     	testq	%rdi, %rdi
    64c9: 74 48                        	je	0x6513 <ivi_layout_add_notification_create_surface+0x63>
    64cb: 48 89 fb                     	movq	%rdi, %rbx
    64ce: bf 10 00 00 00               	movl	$0x10, %edi
    64d3: 48 89 f5                     	movq	%rsi, %rbp
    64d6: e8 95 cf ff ff               	callq	0x3470 <malloc@plt>
    64db: 48 85 c0                     	testq	%rax, %rax
    64de: 74 5b                        	je	0x653b <ivi_layout_add_notification_create_surface+0x8b>
    64e0: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    64e5: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    64ee: 48 89 18                     	movq	%rbx, (%rax)
    64f1: 48 89 68 08                  	movq	%rbp, 0x8(%rax)
    64f5: 75 52                        	jne	0x6549 <ivi_layout_add_notification_create_surface+0x99>
    64f7: 48 8d 35 12 d4 ff ff         	leaq	-0x2bee(%rip), %rsi     # 0x3910 <surface_created>
    64fe: 48 83 c4 18                  	addq	$0x18, %rsp
    6502: 48 89 c2                     	movq	%rax, %rdx
    6505: 5b                           	popq	%rbx
    6506: 48 8d 3d 4b ae 20 00         	leaq	0x20ae4b(%rip), %rdi    # 0x211358 <ivilayout+0x58>
    650d: 5d                           	popq	%rbp
    650e: e9 ed fb ff ff               	jmp	0x6100 <add_notification>
    6513: 48 8d 3d 6e 6e 00 00         	leaq	0x6e6e(%rip), %rdi      # 0xd388 <zwp_input_panel_v1_interface+0xd388>
    651a: e8 f1 cc ff ff               	callq	0x3210 <weston_log@plt>
    651f: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    6524: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    652d: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6532: 75 15                        	jne	0x6549 <ivi_layout_add_notification_create_surface+0x99>
    6534: 48 83 c4 18                  	addq	$0x18, %rsp
    6538: 5b                           	popq	%rbx
    6539: 5d                           	popq	%rbp
    653a: c3                           	retq
    653b: 48 8d 3d 41 70 00 00         	leaq	0x7041(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    6542: e8 c9 cc ff ff               	callq	0x3210 <weston_log@plt>
    6547: eb d6                        	jmp	0x651f <ivi_layout_add_notification_create_surface+0x6f>
    6549: e8 d2 cc ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    654e: 66 90                        	nop

0000000000006550 <ivi_layout_surface_dump>:
    6550: 48 83 ec 18                  	subq	$0x18, %rsp
    6554: 64 4c 8b 14 25 28 00 00 00   	movq	%fs:0x28, %r10
    655d: 4c 89 54 24 08               	movq	%r10, 0x8(%rsp)
    6562: 45 31 d2                     	xorl	%r10d, %r10d
    6565: 8b 44 24 20                  	movl	0x20(%rsp), %eax
    6569: 48 85 ff                     	testq	%rdi, %rdi
    656c: 74 2b                        	je	0x6599 <ivi_layout_surface_dump+0x49>
    656e: 48 83 ec 08                  	subq	$0x8, %rsp
    6572: 50                           	pushq	%rax
    6573: e8 78 cf ff ff               	callq	0x34f0 <weston_surface_copy_content@plt>
    6578: 5a                           	popq	%rdx
    6579: 85 c0                        	testl	%eax, %eax
    657b: 59                           	popq	%rcx
    657c: 0f 95 c0                     	setne	%al
    657f: 0f b6 c0                     	movzbl	%al, %eax
    6582: f7 d8                        	negl	%eax
    6584: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    6589: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    6592: 75 21                        	jne	0x65b5 <ivi_layout_surface_dump+0x65>
    6594: 48 83 c4 18                  	addq	$0x18, %rsp
    6598: c3                           	retq
    6599: 48 8d 35 b0 71 00 00         	leaq	0x71b0(%rip), %rsi      # 0xd750 <__func__.13730>
    65a0: 31 c0                        	xorl	%eax, %eax
    65a2: 48 8d 3d c4 6f 00 00         	leaq	0x6fc4(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    65a9: e8 62 cc ff ff               	callq	0x3210 <weston_log@plt>
    65ae: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    65b3: eb cf                        	jmp	0x6584 <ivi_layout_surface_dump+0x34>
    65b5: e8 66 cc ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    65ba: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

00000000000065c0 <ivi_layout_surface_get_size>:
    65c0: 41 54                        	pushq	%r12
    65c2: 55                           	pushq	%rbp
    65c3: 53                           	pushq	%rbx
    65c4: 48 83 ec 10                  	subq	$0x10, %rsp
    65c8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    65d1: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    65d6: 31 c0                        	xorl	%eax, %eax
    65d8: 48 85 ff                     	testq	%rdi, %rdi
    65db: 74 6b                        	je	0x6648 <ivi_layout_surface_get_size+0x88>
    65dd: 48 8b 7f 38                  	movq	0x38(%rdi), %rdi
    65e1: 48 85 ff                     	testq	%rdi, %rdi
    65e4: 74 62                        	je	0x6648 <ivi_layout_surface_get_size+0x88>
    65e6: 49 89 f4                     	movq	%rsi, %r12
    65e9: 48 89 d5                     	movq	%rdx, %rbp
    65ec: 48 89 e6                     	movq	%rsp, %rsi
    65ef: 48 8d 54 24 04               	leaq	0x4(%rsp), %rdx
    65f4: 48 89 cb                     	movq	%rcx, %rbx
    65f7: e8 c4 cb ff ff               	callq	0x31c0 <weston_surface_get_content_size@plt>
    65fc: 4d 85 e4                     	testq	%r12, %r12
    65ff: 74 07                        	je	0x6608 <ivi_layout_surface_get_size+0x48>
    6601: 8b 04 24                     	movl	(%rsp), %eax
    6604: 41 89 04 24                  	movl	%eax, (%r12)
    6608: 48 85 ed                     	testq	%rbp, %rbp
    660b: 74 07                        	je	0x6614 <ivi_layout_surface_get_size+0x54>
    660d: 8b 44 24 04                  	movl	0x4(%rsp), %eax
    6611: 89 45 00                     	movl	%eax, (%rbp)
    6614: 48 85 db                     	testq	%rbx, %rbx
    6617: 74 27                        	je	0x6640 <ivi_layout_surface_get_size+0x80>
    6619: 8b 04 24                     	movl	(%rsp), %eax
    661c: c1 e0 02                     	shll	$0x2, %eax
    661f: 89 03                        	movl	%eax, (%rbx)
    6621: 31 c0                        	xorl	%eax, %eax
    6623: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    6628: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    6631: 75 31                        	jne	0x6664 <ivi_layout_surface_get_size+0xa4>
    6633: 48 83 c4 10                  	addq	$0x10, %rsp
    6637: 5b                           	popq	%rbx
    6638: 5d                           	popq	%rbp
    6639: 41 5c                        	popq	%r12
    663b: c3                           	retq
    663c: 0f 1f 40 00                  	nopl	(%rax)
    6640: 31 c0                        	xorl	%eax, %eax
    6642: eb df                        	jmp	0x6623 <ivi_layout_surface_get_size+0x63>
    6644: 0f 1f 40 00                  	nopl	(%rax)
    6648: 48 8d 35 e1 70 00 00         	leaq	0x70e1(%rip), %rsi      # 0xd730 <__func__.13653>
    664f: 31 c0                        	xorl	%eax, %eax
    6651: 48 8d 3d 15 6f 00 00         	leaq	0x6f15(%rip), %rdi      # 0xd56d <zwp_input_panel_v1_interface+0xd56d>
    6658: e8 b3 cb ff ff               	callq	0x3210 <weston_log@plt>
    665d: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    6662: eb bf                        	jmp	0x6623 <ivi_layout_surface_get_size+0x63>
    6664: e8 b7 cb ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    6669: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000006670 <ivi_layout_layer_destroy>:
    6670: 41 55                        	pushq	%r13
    6672: 41 54                        	pushq	%r12
    6674: 55                           	pushq	%rbp
    6675: 53                           	pushq	%rbx
    6676: 48 83 ec 18                  	subq	$0x18, %rsp
    667a: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    6683: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6688: 31 c0                        	xorl	%eax, %eax
    668a: 48 85 ff                     	testq	%rdi, %rdi
    668d: 0f 84 6d 01 00 00            	je	0x6800 <ivi_layout_layer_destroy+0x190>
    6693: 8b 87 28 01 00 00            	movl	0x128(%rdi), %eax
    6699: 48 89 fd                     	movq	%rdi, %rbp
    669c: 83 e8 01                     	subl	$0x1, %eax
    669f: 89 87 28 01 00 00            	movl	%eax, 0x128(%rdi)
    66a5: 85 c0                        	testl	%eax, %eax
    66a7: 7e 27                        	jle	0x66d0 <ivi_layout_layer_destroy+0x60>
    66a9: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    66ae: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    66b7: 0f 85 6b 01 00 00            	jne	0x6828 <ivi_layout_layer_destroy+0x1b8>
    66bd: 48 83 c4 18                  	addq	$0x18, %rsp
    66c1: 5b                           	popq	%rbx
    66c2: 5d                           	popq	%rbp
    66c3: 41 5c                        	popq	%r12
    66c5: 41 5d                        	popq	%r13
    66c7: c3                           	retq
    66c8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    66d0: 48 8b 05 79 ac 20 00         	movq	0x20ac79(%rip), %rax    # 0x211350 <ivilayout+0x50>
    66d7: 4c 8d 25 6a ac 20 00         	leaq	0x20ac6a(%rip), %r12    # 0x211348 <ivilayout+0x48>
    66de: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    66e2: 4c 39 e0                     	cmpq	%r12, %rax
    66e5: 75 0c                        	jne	0x66f3 <ivi_layout_layer_destroy+0x83>
    66e7: eb 1f                        	jmp	0x6708 <ivi_layout_layer_destroy+0x98>
    66e9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    66f0: 48 89 d3                     	movq	%rdx, %rbx
    66f3: 48 89 c7                     	movq	%rax, %rdi
    66f6: 48 89 ee                     	movq	%rbp, %rsi
    66f9: ff 50 10                     	callq	*0x10(%rax)
    66fc: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    6700: 48 89 d8                     	movq	%rbx, %rax
    6703: 4c 39 e3                     	cmpq	%r12, %rbx
    6706: 75 e8                        	jne	0x66f0 <ivi_layout_layer_destroy+0x80>
    6708: 48 8b 9d e8 00 00 00         	movq	0xe8(%rbp), %rbx
    670f: 4c 8d ad e0 00 00 00         	leaq	0xe0(%rbp), %r13
    6716: 48 8b 43 08                  	movq	0x8(%rbx), %rax
    671a: 4c 8d a0 d8 fe ff ff         	leaq	-0x128(%rax), %r12
    6721: 4c 39 eb                     	cmpq	%r13, %rbx
    6724: 74 36                        	je	0x675c <ivi_layout_layer_destroy+0xec>
    6726: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    6730: 48 89 df                     	movq	%rbx, %rdi
    6733: e8 f8 cc ff ff               	callq	0x3430 <wl_list_remove@plt>
    6738: 48 89 df                     	movq	%rbx, %rdi
    673b: e8 00 cc ff ff               	callq	0x3340 <wl_list_init@plt>
    6740: 49 8b 84 24 30 01 00 00      	movq	0x130(%r12), %rax
    6748: 49 8d 9c 24 28 01 00 00      	leaq	0x128(%r12), %rbx
    6750: 4c 8d a0 d8 fe ff ff         	leaq	-0x128(%rax), %r12
    6757: 4c 39 eb                     	cmpq	%r13, %rbx
    675a: 75 d4                        	jne	0x6730 <ivi_layout_layer_destroy+0xc0>
    675c: 48 8b 9d 10 01 00 00         	movq	0x110(%rbp), %rbx
    6763: 4c 8d ad 08 01 00 00         	leaq	0x108(%rbp), %r13
    676a: 48 8b 43 08                  	movq	0x8(%rbx), %rax
    676e: 4c 8d a0 c8 fe ff ff         	leaq	-0x138(%rax), %r12
    6775: 49 39 dd                     	cmpq	%rbx, %r13
    6778: 74 32                        	je	0x67ac <ivi_layout_layer_destroy+0x13c>
    677a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    6780: 48 89 df                     	movq	%rbx, %rdi
    6783: e8 a8 cc ff ff               	callq	0x3430 <wl_list_remove@plt>
    6788: 48 89 df                     	movq	%rbx, %rdi
    678b: e8 b0 cb ff ff               	callq	0x3340 <wl_list_init@plt>
    6790: 49 8b 84 24 40 01 00 00      	movq	0x140(%r12), %rax
    6798: 49 8d 9c 24 38 01 00 00      	leaq	0x138(%r12), %rbx
    67a0: 4c 8d a0 c8 fe ff ff         	leaq	-0x138(%rax), %r12
    67a7: 4c 39 eb                     	cmpq	%r13, %rbx
    67aa: 75 d4                        	jne	0x6780 <ivi_layout_layer_destroy+0x110>
    67ac: 48 8d bd f0 00 00 00         	leaq	0xf0(%rbp), %rdi
    67b3: e8 78 cc ff ff               	callq	0x3430 <wl_list_remove@plt>
    67b8: 48 8d bd 18 01 00 00         	leaq	0x118(%rbp), %rdi
    67bf: e8 6c cc ff ff               	callq	0x3430 <wl_list_remove@plt>
    67c4: 48 89 ef                     	movq	%rbp, %rdi
    67c7: e8 64 cc ff ff               	callq	0x3430 <wl_list_remove@plt>
    67cc: 48 8d 7d 10                  	leaq	0x10(%rbp), %rdi
    67d0: e8 eb e0 ff ff               	callq	0x48c0 <remove_all_notification>
    67d5: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    67da: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    67e3: 75 43                        	jne	0x6828 <ivi_layout_layer_destroy+0x1b8>
    67e5: 48 83 c4 18                  	addq	$0x18, %rsp
    67e9: 48 89 ef                     	movq	%rbp, %rdi
    67ec: 5b                           	popq	%rbx
    67ed: 5d                           	popq	%rbp
    67ee: 41 5c                        	popq	%r12
    67f0: 41 5d                        	popq	%r13
    67f2: e9 79 c8 ff ff               	jmp	0x3070 <free@plt>
    67f7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    6800: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    6805: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    680e: 75 18                        	jne	0x6828 <ivi_layout_layer_destroy+0x1b8>
    6810: 48 8d 3d b1 6b 00 00         	leaq	0x6bb1(%rip), %rdi      # 0xd3c8 <zwp_input_panel_v1_interface+0xd3c8>
    6817: 48 83 c4 18                  	addq	$0x18, %rsp
    681b: 31 c0                        	xorl	%eax, %eax
    681d: 5b                           	popq	%rbx
    681e: 5d                           	popq	%rbp
    681f: 41 5c                        	popq	%r12
    6821: 41 5d                        	popq	%r13
    6823: e9 e8 c9 ff ff               	jmp	0x3210 <weston_log@plt>
    6828: e8 f3 c9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    682d: 0f 1f 00                     	nopl	(%rax)

0000000000006830 <ivi_layout_layer_create_with_dimension>:
    6830: 41 55                        	pushq	%r13
    6832: 41 89 d5                     	movl	%edx, %r13d
    6835: 41 54                        	pushq	%r12
    6837: 41 89 f4                     	movl	%esi, %r12d
    683a: 55                           	pushq	%rbp
    683b: 89 fd                        	movl	%edi, %ebp
    683d: 53                           	pushq	%rbx
    683e: 48 83 ec 18                  	subq	$0x18, %rsp
    6842: 48 8b 1d d7 aa 20 00         	movq	0x20aad7(%rip), %rbx    # 0x211320 <ivilayout+0x20>
    6849: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    6852: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    6857: 31 c0                        	xorl	%eax, %eax
    6859: 48 8d 05 b8 aa 20 00         	leaq	0x20aab8(%rip), %rax    # 0x211318 <ivilayout+0x18>
    6860: 48 39 c3                     	cmpq	%rax, %rbx
    6863: 75 14                        	jne	0x6879 <ivi_layout_layer_create_with_dimension+0x49>
    6865: eb 51                        	jmp	0x68b8 <ivi_layout_layer_create_with_dimension+0x88>
    6867: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    6870: 48 8b 5b 08                  	movq	0x8(%rbx), %rbx
    6874: 48 39 c3                     	cmpq	%rax, %rbx
    6877: 74 3f                        	je	0x68b8 <ivi_layout_layer_create_with_dimension+0x88>
    6879: 3b 6b 20                     	cmpl	0x20(%rbx), %ebp
    687c: 75 f2                        	jne	0x6870 <ivi_layout_layer_create_with_dimension+0x40>
    687e: 48 8d 3d 2f 6d 00 00         	leaq	0x6d2f(%rip), %rdi      # 0xd5b4 <zwp_input_panel_v1_interface+0xd5b4>
    6885: 31 c0                        	xorl	%eax, %eax
    6887: e8 84 c9 ff ff               	callq	0x3210 <weston_log@plt>
    688c: 48 89 d8                     	movq	%rbx, %rax
    688f: 83 83 28 01 00 00 01         	addl	$0x1, 0x128(%rbx)
    6896: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    689b: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    68a4: 0f 85 8b 01 00 00            	jne	0x6a35 <ivi_layout_layer_create_with_dimension+0x205>
    68aa: 48 83 c4 18                  	addq	$0x18, %rsp
    68ae: 5b                           	popq	%rbx
    68af: 5d                           	popq	%rbp
    68b0: 41 5c                        	popq	%r12
    68b2: 41 5d                        	popq	%r13
    68b4: c3                           	retq
    68b5: 0f 1f 00                     	nopl	(%rax)
    68b8: be 30 01 00 00               	movl	$0x130, %esi            # imm = 0x130
    68bd: bf 01 00 00 00               	movl	$0x1, %edi
    68c2: e8 a9 ca ff ff               	callq	0x3370 <calloc@plt>
    68c7: 48 89 c3                     	movq	%rax, %rbx
    68ca: 48 85 c0                     	testq	%rax, %rax
    68cd: 0f 84 4d 01 00 00            	je	0x6a20 <ivi_layout_layer_create_with_dimension+0x1f0>
    68d3: c7 83 28 01 00 00 01 00 00 00	movl	$0x1, 0x128(%rbx)
    68dd: 48 8d 7b 10                  	leaq	0x10(%rbx), %rdi
    68e1: e8 5a ca ff ff               	callq	0x3340 <wl_list_init@plt>
    68e6: 48 8d 53 38                  	leaq	0x38(%rbx), %rdx
    68ea: b9 0a 00 00 00               	movl	$0xa, %ecx
    68ef: 89 6b 20                     	movl	%ebp, 0x20(%rbx)
    68f2: 48 8d 05 07 aa 20 00         	leaq	0x20aa07(%rip), %rax    # 0x211300 <ivilayout>
    68f9: 48 89 d7                     	movq	%rdx, %rdi
    68fc: 48 89 43 28                  	movq	%rax, 0x28(%rbx)
    6900: 31 c0                        	xorl	%eax, %eax
    6902: f3 48 ab                     	rep		stosq	%rax, %es:(%rdi)
    6905: 44 89 63 44                  	movl	%r12d, 0x44(%rbx)
    6909: 48 8d bb e0 00 00 00         	leaq	0xe0(%rbx), %rdi
    6910: 44 89 63 54                  	movl	%r12d, 0x54(%rbx)
    6914: 4c 8d 25 1d aa 20 00         	leaq	0x20aa1d(%rip), %r12    # 0x211338 <ivilayout+0x38>
    691b: c7 43 38 00 01 00 00         	movl	$0x100, 0x38(%rbx)      # imm = 0x100
    6922: 44 89 6b 48                  	movl	%r13d, 0x48(%rbx)
    6926: 44 89 6b 58                  	movl	%r13d, 0x58(%rbx)
    692a: c7 83 88 00 00 00 00 00 00 00	movl	$0x0, 0x88(%rbx)
    6934: e8 07 ca ff ff               	callq	0x3340 <wl_list_init@plt>
    6939: 48 8d bb f0 00 00 00         	leaq	0xf0(%rbx), %rdi
    6940: e8 fb c9 ff ff               	callq	0x3340 <wl_list_init@plt>
    6945: 48 8b 43 38                  	movq	0x38(%rbx), %rax
    6949: 48 8d bb 08 01 00 00         	leaq	0x108(%rbx), %rdi
    6950: 48 89 83 90 00 00 00         	movq	%rax, 0x90(%rbx)
    6957: 48 8b 43 40                  	movq	0x40(%rbx), %rax
    695b: 48 89 83 98 00 00 00         	movq	%rax, 0x98(%rbx)
    6962: 48 8b 43 48                  	movq	0x48(%rbx), %rax
    6966: 48 89 83 a0 00 00 00         	movq	%rax, 0xa0(%rbx)
    696d: 48 8b 43 50                  	movq	0x50(%rbx), %rax
    6971: 48 89 83 a8 00 00 00         	movq	%rax, 0xa8(%rbx)
    6978: 48 8b 43 58                  	movq	0x58(%rbx), %rax
    697c: 48 89 83 b0 00 00 00         	movq	%rax, 0xb0(%rbx)
    6983: 48 8b 43 60                  	movq	0x60(%rbx), %rax
    6987: 48 89 83 b8 00 00 00         	movq	%rax, 0xb8(%rbx)
    698e: 48 8b 43 68                  	movq	0x68(%rbx), %rax
    6992: 48 89 83 c0 00 00 00         	movq	%rax, 0xc0(%rbx)
    6999: 48 8b 43 70                  	movq	0x70(%rbx), %rax
    699d: 48 89 83 c8 00 00 00         	movq	%rax, 0xc8(%rbx)
    69a4: 48 8b 43 78                  	movq	0x78(%rbx), %rax
    69a8: 48 89 83 d0 00 00 00         	movq	%rax, 0xd0(%rbx)
    69af: 48 8b 83 80 00 00 00         	movq	0x80(%rbx), %rax
    69b6: 48 89 83 d8 00 00 00         	movq	%rax, 0xd8(%rbx)
    69bd: e8 7e c9 ff ff               	callq	0x3340 <wl_list_init@plt>
    69c2: 48 8d bb 18 01 00 00         	leaq	0x118(%rbx), %rdi
    69c9: e8 72 c9 ff ff               	callq	0x3340 <wl_list_init@plt>
    69ce: 48 8d 3d 43 a9 20 00         	leaq	0x20a943(%rip), %rdi    # 0x211318 <ivilayout+0x18>
    69d5: 48 89 de                     	movq	%rbx, %rsi
    69d8: e8 c3 cc ff ff               	callq	0x36a0 <wl_list_insert@plt>
    69dd: 48 8b 05 5c a9 20 00         	movq	0x20a95c(%rip), %rax    # 0x211340 <ivilayout+0x40>
    69e4: 48 8b 68 08                  	movq	0x8(%rax), %rbp
    69e8: 4c 39 e0                     	cmpq	%r12, %rax
    69eb: 0f 85 12 00 00 00            	jne	0x6a03 <ivi_layout_layer_create_with_dimension+0x1d3>
    69f1: 48 89 d8                     	movq	%rbx, %rax
    69f4: e9 9d fe ff ff               	jmp	0x6896 <ivi_layout_layer_create_with_dimension+0x66>
    69f9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    6a00: 48 89 d5                     	movq	%rdx, %rbp
    6a03: 48 89 c7                     	movq	%rax, %rdi
    6a06: 48 89 de                     	movq	%rbx, %rsi
    6a09: ff 50 10                     	callq	*0x10(%rax)
    6a0c: 48 8b 55 08                  	movq	0x8(%rbp), %rdx
    6a10: 48 89 e8                     	movq	%rbp, %rax
    6a13: 4c 39 e5                     	cmpq	%r12, %rbp
    6a16: 75 e8                        	jne	0x6a00 <ivi_layout_layer_create_with_dimension+0x1d0>
    6a18: 48 89 d8                     	movq	%rbx, %rax
    6a1b: e9 76 fe ff ff               	jmp	0x6896 <ivi_layout_layer_create_with_dimension+0x66>
    6a20: 48 8d 3d 5c 6b 00 00         	leaq	0x6b5c(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    6a27: 31 c0                        	xorl	%eax, %eax
    6a29: e8 e2 c7 ff ff               	callq	0x3210 <weston_log@plt>
    6a2e: 31 c0                        	xorl	%eax, %eax
    6a30: e9 61 fe ff ff               	jmp	0x6896 <ivi_layout_layer_create_with_dimension+0x66>
    6a35: e8 e6 c7 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    6a3a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000006a40 <ivi_layout_commit_changes>:
    6a40: 41 57                        	pushq	%r15
    6a42: 41 56                        	pushq	%r14
    6a44: 41 55                        	pushq	%r13
    6a46: 41 54                        	pushq	%r12
    6a48: 55                           	pushq	%rbp
    6a49: 53                           	pushq	%rbx
    6a4a: 48 81 ec 38 01 00 00         	subq	$0x138, %rsp            # imm = 0x138
    6a51: 48 8b 2d b8 a8 20 00         	movq	0x20a8b8(%rip), %rbp    # 0x211310 <ivilayout+0x10>
    6a58: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    6a61: 48 89 84 24 28 01 00 00      	movq	%rax, 0x128(%rsp)
    6a69: 31 c0                        	xorl	%eax, %eax
    6a6b: 48 8d 05 96 a8 20 00         	leaq	0x20a896(%rip), %rax    # 0x211308 <ivilayout+0x8>
    6a72: 48 39 c5                     	cmpq	%rax, %rbp
    6a75: 0f 84 68 01 00 00            	je	0x6be3 <ivi_layout_commit_changes+0x1a3>
    6a7b: 8b 85 1c 01 00 00            	movl	0x11c(%rbp), %eax
    6a81: 83 f8 01                     	cmpl	$0x1, %eax
    6a84: 0f 84 cf 0c 00 00            	je	0x7759 <ivi_layout_commit_changes+0xd19>
    6a8a: 83 f8 0a                     	cmpl	$0xa, %eax
    6a8d: 0f 84 71 0b 00 00            	je	0x7604 <ivi_layout_commit_changes+0xbc4>
    6a93: 83 f8 02                     	cmpl	$0x2, %eax
    6a96: 0f 84 e2 0d 00 00            	je	0x787e <ivi_layout_commit_changes+0xe3e>
    6a9c: 83 f8 03                     	cmpl	$0x3, %eax
    6a9f: 0f 84 ab 09 00 00            	je	0x7450 <ivi_layout_commit_changes+0xa10>
    6aa5: 8b 85 0c 01 00 00            	movl	0x10c(%rbp), %eax
    6aab: 39 85 c4 00 00 00            	cmpl	%eax, 0xc4(%rbp)
    6ab1: 0f 84 a6 0a 00 00            	je	0x755d <ivi_layout_commit_changes+0xb1d>
    6ab7: 48 8b 85 e0 00 00 00         	movq	0xe0(%rbp), %rax
    6abe: 48 89 ef                     	movq	%rbp, %rdi
    6ac1: 48 89 85 98 00 00 00         	movq	%rax, 0x98(%rbp)
    6ac8: 48 8b 85 e8 00 00 00         	movq	0xe8(%rbp), %rax
    6acf: 48 89 85 a0 00 00 00         	movq	%rax, 0xa0(%rbp)
    6ad6: 48 8b 85 f0 00 00 00         	movq	0xf0(%rbp), %rax
    6add: 48 89 85 a8 00 00 00         	movq	%rax, 0xa8(%rbp)
    6ae4: 48 8b 85 f8 00 00 00         	movq	0xf8(%rbp), %rax
    6aeb: 48 89 85 b0 00 00 00         	movq	%rax, 0xb0(%rbp)
    6af2: 48 8b 85 00 01 00 00         	movq	0x100(%rbp), %rax
    6af9: 48 89 85 b8 00 00 00         	movq	%rax, 0xb8(%rbp)
    6b00: 48 8b 85 08 01 00 00         	movq	0x108(%rbp), %rax
    6b07: 48 89 85 c0 00 00 00         	movq	%rax, 0xc0(%rbp)
    6b0e: 48 8b 85 10 01 00 00         	movq	0x110(%rbp), %rax
    6b15: 48 89 85 c8 00 00 00         	movq	%rax, 0xc8(%rbp)
    6b1c: 48 8b 85 18 01 00 00         	movq	0x118(%rbp), %rax
    6b23: c7 85 1c 01 00 00 00 00 00 00	movl	$0x0, 0x11c(%rbp)
    6b2d: 48 89 85 d0 00 00 00         	movq	%rax, 0xd0(%rbp)
    6b34: 8b 85 20 01 00 00            	movl	0x120(%rbp), %eax
    6b3a: c7 85 d4 00 00 00 00 00 00 00	movl	$0x0, 0xd4(%rbp)
    6b44: 89 85 d8 00 00 00            	movl	%eax, 0xd8(%rbp)
    6b4a: e8 c1 25 00 00               	callq	0x9110 <is_surface_transition>
    6b4f: 85 c0                        	testl	%eax, %eax
    6b51: 75 7c                        	jne	0x6bcf <ivi_layout_commit_changes+0x18f>
    6b53: 48 8b 85 70 01 00 00         	movq	0x170(%rbp), %rax
    6b5a: 4c 8d a5 68 01 00 00         	leaq	0x168(%rbp), %r12
    6b61: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    6b65: 49 39 c4                     	cmpq	%rax, %r12
    6b68: 75 09                        	jne	0x6b73 <ivi_layout_commit_changes+0x133>
    6b6a: eb 1c                        	jmp	0x6b88 <ivi_layout_commit_changes+0x148>
    6b6c: 0f 1f 40 00                  	nopl	(%rax)
    6b70: 48 89 d3                     	movq	%rdx, %rbx
    6b73: 48 89 c7                     	movq	%rax, %rdi
    6b76: 48 89 ee                     	movq	%rbp, %rsi
    6b79: ff 50 10                     	callq	*0x10(%rax)
    6b7c: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    6b80: 48 89 d8                     	movq	%rbx, %rax
    6b83: 49 39 dc                     	cmpq	%rbx, %r12
    6b86: 75 e8                        	jne	0x6b70 <ivi_layout_commit_changes+0x130>
    6b88: 80 bd 90 01 00 00 00         	cmpb	$0x0, 0x190(%rbp)
    6b8f: 0f 84 52 0e 00 00            	je	0x79e7 <ivi_layout_commit_changes+0xfa7>
    6b95: 48 8b 05 e4 a7 20 00         	movq	0x20a7e4(%rip), %rax    # 0x211380 <ivilayout+0x80>
    6b9c: 48 8d 0d d5 a7 20 00         	leaq	0x20a7d5(%rip), %rcx    # 0x211378 <ivilayout+0x78>
    6ba3: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    6ba7: 48 39 c8                     	cmpq	%rcx, %rax
    6baa: 75 07                        	jne	0x6bb3 <ivi_layout_commit_changes+0x173>
    6bac: eb 21                        	jmp	0x6bcf <ivi_layout_commit_changes+0x18f>
    6bae: 66 90                        	nop
    6bb0: 48 89 d3                     	movq	%rdx, %rbx
    6bb3: 48 89 c7                     	movq	%rax, %rdi
    6bb6: 48 89 ee                     	movq	%rbp, %rsi
    6bb9: ff 50 10                     	callq	*0x10(%rax)
    6bbc: 48 8d 0d b5 a7 20 00         	leaq	0x20a7b5(%rip), %rcx    # 0x211378 <ivilayout+0x78>
    6bc3: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    6bc7: 48 89 d8                     	movq	%rbx, %rax
    6bca: 48 39 cb                     	cmpq	%rcx, %rbx
    6bcd: 75 e1                        	jne	0x6bb0 <ivi_layout_commit_changes+0x170>
    6bcf: 48 8b 6d 08                  	movq	0x8(%rbp), %rbp
    6bd3: 48 8d 05 2e a7 20 00         	leaq	0x20a72e(%rip), %rax    # 0x211308 <ivilayout+0x8>
    6bda: 48 39 c5                     	cmpq	%rax, %rbp
    6bdd: 0f 85 98 fe ff ff            	jne	0x6a7b <ivi_layout_commit_changes+0x3b>
    6be3: 48 8b 1d 36 a7 20 00         	movq	0x20a736(%rip), %rbx    # 0x211320 <ivilayout+0x20>
    6bea: 48 8d 05 27 a7 20 00         	leaq	0x20a727(%rip), %rax    # 0x211318 <ivilayout+0x18>
    6bf1: 48 39 c3                     	cmpq	%rax, %rbx
    6bf4: 0f 84 9f 01 00 00            	je	0x6d99 <ivi_layout_commit_changes+0x359>
    6bfa: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    6c00: 8b 83 bc 00 00 00            	movl	0xbc(%rbx), %eax
    6c06: 83 f8 05                     	cmpl	$0x5, %eax
    6c09: 0f 84 70 07 00 00            	je	0x737f <ivi_layout_commit_changes+0x93f>
    6c0f: 83 f8 04                     	cmpl	$0x4, %eax
    6c12: 0f 84 0a 08 00 00            	je	0x7422 <ivi_layout_commit_changes+0x9e2>
    6c18: 48 8b 83 90 00 00 00         	movq	0x90(%rbx), %rax
    6c1f: 48 89 43 38                  	movq	%rax, 0x38(%rbx)
    6c23: 48 8b 83 98 00 00 00         	movq	0x98(%rbx), %rax
    6c2a: 48 89 43 40                  	movq	%rax, 0x40(%rbx)
    6c2e: 48 8b 83 a0 00 00 00         	movq	0xa0(%rbx), %rax
    6c35: 48 89 43 48                  	movq	%rax, 0x48(%rbx)
    6c39: 48 8b 83 a8 00 00 00         	movq	0xa8(%rbx), %rax
    6c40: 48 89 43 50                  	movq	%rax, 0x50(%rbx)
    6c44: 48 8b 83 b0 00 00 00         	movq	0xb0(%rbx), %rax
    6c4b: 48 89 43 58                  	movq	%rax, 0x58(%rbx)
    6c4f: 48 8b 83 b8 00 00 00         	movq	0xb8(%rbx), %rax
    6c56: 48 89 43 60                  	movq	%rax, 0x60(%rbx)
    6c5a: 48 8b 83 c0 00 00 00         	movq	0xc0(%rbx), %rax
    6c61: 48 89 43 68                  	movq	%rax, 0x68(%rbx)
    6c65: 48 8b 83 c8 00 00 00         	movq	0xc8(%rbx), %rax
    6c6c: 48 89 43 70                  	movq	%rax, 0x70(%rbx)
    6c70: 48 8b 83 d0 00 00 00         	movq	0xd0(%rbx), %rax
    6c77: 48 89 43 78                  	movq	%rax, 0x78(%rbx)
    6c7b: 48 8b 83 d8 00 00 00         	movq	0xd8(%rbx), %rax
    6c82: 48 89 83 80 00 00 00         	movq	%rax, 0x80(%rbx)
    6c89: 44 8b ab 00 01 00 00         	movl	0x100(%rbx), %r13d
    6c90: c7 83 bc 00 00 00 00 00 00 00	movl	$0x0, 0xbc(%rbx)
    6c9a: 45 85 ed                     	testl	%r13d, %r13d
    6c9d: 0f 84 e2 00 00 00            	je	0x6d85 <ivi_layout_commit_changes+0x345>
    6ca3: 48 8b ab 10 01 00 00         	movq	0x110(%rbx), %rbp
    6caa: 4c 8d b3 08 01 00 00         	leaq	0x108(%rbx), %r14
    6cb1: 48 8b 45 08                  	movq	0x8(%rbp), %rax
    6cb5: 4c 8d ad c8 fe ff ff         	leaq	-0x138(%rbp), %r13
    6cbc: 4c 8d a0 c8 fe ff ff         	leaq	-0x138(%rax), %r12
    6cc3: 4c 39 f5                     	cmpq	%r14, %rbp
    6cc6: 74 4a                        	je	0x6d12 <ivi_layout_commit_changes+0x2d2>
    6cc8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    6cd0: 48 89 ef                     	movq	%rbp, %rdi
    6cd3: 49 c7 45 30 00 00 00 00      	movq	$0x0, 0x30(%r13)
    6cdb: e8 50 c7 ff ff               	callq	0x3430 <wl_list_remove@plt>
    6ce0: 48 89 ef                     	movq	%rbp, %rdi
    6ce3: e8 58 c6 ff ff               	callq	0x3340 <wl_list_init@plt>
    6ce8: 49 8b 84 24 40 01 00 00      	movq	0x140(%r12), %rax
    6cf0: 49 8d ac 24 38 01 00 00      	leaq	0x138(%r12), %rbp
    6cf8: 41 81 8d dc 00 00 00 00 04 00 00     	orl	$0x400, 0xdc(%r13) # imm = 0x400
    6d03: 4d 89 e5                     	movq	%r12, %r13
    6d06: 4c 8d a0 c8 fe ff ff         	leaq	-0x138(%rax), %r12
    6d0d: 4c 39 f5                     	cmpq	%r14, %rbp
    6d10: 75 be                        	jne	0x6cd0 <ivi_layout_commit_changes+0x290>
    6d12: 4c 89 f7                     	movq	%r14, %rdi
    6d15: e8 d6 c6 ff ff               	callq	0x33f0 <wl_list_empty@plt>
    6d1a: 85 c0                        	testl	%eax, %eax
    6d1c: 0f 84 36 13 00 00            	je	0x8058 <ivi_layout_commit_changes+0x1618>
    6d22: 48 8b 83 e8 00 00 00         	movq	0xe8(%rbx), %rax
    6d29: 4c 8d ab e0 00 00 00         	leaq	0xe0(%rbx), %r13
    6d30: 48 8d a8 d8 fe ff ff         	leaq	-0x128(%rax), %rbp
    6d37: 49 39 c5                     	cmpq	%rax, %r13
    6d3a: 74 3f                        	je	0x6d7b <ivi_layout_commit_changes+0x33b>
    6d3c: 0f 1f 40 00                  	nopl	(%rax)
    6d40: 4c 8d a5 38 01 00 00         	leaq	0x138(%rbp), %r12
    6d47: 4c 89 e7                     	movq	%r12, %rdi
    6d4a: e8 e1 c6 ff ff               	callq	0x3430 <wl_list_remove@plt>
    6d4f: 4c 89 e6                     	movq	%r12, %rsi
    6d52: 4c 89 f7                     	movq	%r14, %rdi
    6d55: e8 46 c9 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    6d5a: 48 8b 85 30 01 00 00         	movq	0x130(%rbp), %rax
    6d61: 48 89 5d 30                  	movq	%rbx, 0x30(%rbp)
    6d65: 81 8d dc 00 00 00 00 02 00 00	orl	$0x200, 0xdc(%rbp)      # imm = 0x200
    6d6f: 48 8d a8 d8 fe ff ff         	leaq	-0x128(%rax), %rbp
    6d76: 49 39 c5                     	cmpq	%rax, %r13
    6d79: 75 c5                        	jne	0x6d40 <ivi_layout_commit_changes+0x300>
    6d7b: c7 83 00 01 00 00 00 00 00 00	movl	$0x0, 0x100(%rbx)
    6d85: 48 8b 5b 08                  	movq	0x8(%rbx), %rbx
    6d89: 48 8d 05 88 a5 20 00         	leaq	0x20a588(%rip), %rax    # 0x211318 <ivilayout+0x18>
    6d90: 48 39 c3                     	cmpq	%rax, %rbx
    6d93: 0f 85 67 fe ff ff            	jne	0x6c00 <ivi_layout_commit_changes+0x1c0>
    6d99: 48 8b 3d f0 a5 20 00         	movq	0x20a5f0(%rip), %rdi    # 0x211390 <ivilayout+0x90>
    6da0: 48 8d 2d e1 a5 20 00         	leaq	0x20a5e1(%rip), %rbp    # 0x211388 <ivilayout+0x88>
    6da7: 48 8b 5f 08                  	movq	0x8(%rdi), %rbx
    6dab: 48 39 ef                     	cmpq	%rbp, %rdi
    6dae: 74 14                        	je	0x6dc4 <ivi_layout_commit_changes+0x384>
    6db0: e8 eb c5 ff ff               	callq	0x33a0 <weston_layer_entry_remove@plt>
    6db5: 48 89 d8                     	movq	%rbx, %rax
    6db8: 48 89 df                     	movq	%rbx, %rdi
    6dbb: 48 8b 5b 08                  	movq	0x8(%rbx), %rbx
    6dbf: 48 39 e8                     	cmpq	%rbp, %rax
    6dc2: 75 ec                        	jne	0x6db0 <ivi_layout_commit_changes+0x370>
    6dc4: 48 8b 2d 65 a5 20 00         	movq	0x20a565(%rip), %rbp    # 0x211330 <ivilayout+0x30>
    6dcb: 4c 8d 3d 56 a5 20 00         	leaq	0x20a556(%rip), %r15    # 0x211328 <ivilayout+0x28>
    6dd2: 4c 39 fd                     	cmpq	%r15, %rbp
    6dd5: 0f 84 7d 01 00 00            	je	0x6f58 <ivi_layout_commit_changes+0x518>
    6ddb: 44 8b 65 48                  	movl	0x48(%rbp), %r12d
    6ddf: 4c 8d 6d 50                  	leaq	0x50(%rbp), %r13
    6de3: 45 85 e4                     	testl	%r12d, %r12d
    6de6: 0f 84 d6 00 00 00            	je	0x6ec2 <ivi_layout_commit_changes+0x482>
    6dec: 48 8b 5d 58                  	movq	0x58(%rbp), %rbx
    6df0: 4c 8d 6d 50                  	leaq	0x50(%rbp), %r13
    6df4: 48 8b 43 08                  	movq	0x8(%rbx), %rax
    6df8: 4c 8d b3 e8 fe ff ff         	leaq	-0x118(%rbx), %r14
    6dff: 4c 8d a0 e8 fe ff ff         	leaq	-0x118(%rax), %r12
    6e06: 4c 39 eb                     	cmpq	%r13, %rbx
    6e09: 74 47                        	je	0x6e52 <ivi_layout_commit_changes+0x412>
    6e0b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    6e10: 48 89 df                     	movq	%rbx, %rdi
    6e13: 49 c7 46 30 00 00 00 00      	movq	$0x0, 0x30(%r14)
    6e1b: e8 10 c6 ff ff               	callq	0x3430 <wl_list_remove@plt>
    6e20: 48 89 df                     	movq	%rbx, %rdi
    6e23: e8 18 c5 ff ff               	callq	0x3340 <wl_list_init@plt>
    6e28: 49 8b 84 24 20 01 00 00      	movq	0x120(%r12), %rax
    6e30: 49 8d 9c 24 18 01 00 00      	leaq	0x118(%r12), %rbx
    6e38: 41 81 8e 88 00 00 00 00 04 00 00     	orl	$0x400, 0x88(%r14) # imm = 0x400
    6e43: 4d 89 e6                     	movq	%r12, %r14
    6e46: 4c 8d a0 e8 fe ff ff         	leaq	-0x118(%rax), %r12
    6e4d: 4c 39 eb                     	cmpq	%r13, %rbx
    6e50: 75 be                        	jne	0x6e10 <ivi_layout_commit_changes+0x3d0>
    6e52: 4c 89 ef                     	movq	%r13, %rdi
    6e55: e8 96 c5 ff ff               	callq	0x33f0 <wl_list_empty@plt>
    6e5a: 85 c0                        	testl	%eax, %eax
    6e5c: 0f 84 15 12 00 00            	je	0x8077 <ivi_layout_commit_changes+0x1637>
    6e62: 48 8b 45 30                  	movq	0x30(%rbp), %rax
    6e66: 4c 8d 65 28                  	leaq	0x28(%rbp), %r12
    6e6a: 48 8d 98 10 ff ff ff         	leaq	-0xf0(%rax), %rbx
    6e71: 49 39 c4                     	cmpq	%rax, %r12
    6e74: 74 45                        	je	0x6ebb <ivi_layout_commit_changes+0x47b>
    6e76: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    6e80: 4c 8d b3 18 01 00 00         	leaq	0x118(%rbx), %r14
    6e87: 4c 89 f7                     	movq	%r14, %rdi
    6e8a: e8 a1 c5 ff ff               	callq	0x3430 <wl_list_remove@plt>
    6e8f: 4c 89 f6                     	movq	%r14, %rsi
    6e92: 4c 89 ef                     	movq	%r13, %rdi
    6e95: e8 06 c8 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    6e9a: 48 8b 83 f8 00 00 00         	movq	0xf8(%rbx), %rax
    6ea1: 48 89 6b 30                  	movq	%rbp, 0x30(%rbx)
    6ea5: 81 8b 88 00 00 00 00 02 00 00	orl	$0x200, 0x88(%rbx)      # imm = 0x200
    6eaf: 48 8d 98 10 ff ff ff         	leaq	-0xf0(%rax), %rbx
    6eb6: 49 39 c4                     	cmpq	%rax, %r12
    6eb9: 75 c5                        	jne	0x6e80 <ivi_layout_commit_changes+0x440>
    6ebb: c7 45 48 00 00 00 00         	movl	$0x0, 0x48(%rbp)
    6ec2: 48 8b 45 58                  	movq	0x58(%rbp), %rax
    6ec6: 4c 8d a0 e8 fe ff ff         	leaq	-0x118(%rax), %r12
    6ecd: 49 39 c5                     	cmpq	%rax, %r13
    6ed0: 74 79                        	je	0x6f4b <ivi_layout_commit_changes+0x50b>
    6ed2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    6ed8: 49 8b 84 24 10 01 00 00      	movq	0x110(%r12), %rax
    6ee0: 49 8d 9c 24 08 01 00 00      	leaq	0x108(%r12), %rbx
    6ee8: 4c 8d b0 c8 fe ff ff         	leaq	-0x138(%rax), %r14
    6eef: 48 39 c3                     	cmpq	%rax, %rbx
    6ef2: 74 43                        	je	0x6f37 <ivi_layout_commit_changes+0x4f7>
    6ef4: 0f 1f 40 00                  	nopl	(%rax)
    6ef8: 48 8b 70 50                  	movq	0x50(%rax), %rsi
    6efc: 48 85 f6                     	testq	%rsi, %rsi
    6eff: 0f 84 af 0a 00 00            	je	0x79b4 <ivi_layout_commit_changes+0xf74>
    6f05: 48 8d 3d 7c a4 20 00         	leaq	0x20a47c(%rip), %rdi    # 0x211388 <ivilayout+0x88>
    6f0c: 48 83 c6 38                  	addq	$0x38, %rsi
    6f10: e8 6b c2 ff ff               	callq	0x3180 <weston_layer_entry_insert@plt>
    6f15: 49 8b 46 38                  	movq	0x38(%r14), %rax
    6f19: 48 8b 55 20                  	movq	0x20(%rbp), %rdx
    6f1d: 48 89 90 90 00 00 00         	movq	%rdx, 0x90(%rax)
    6f24: 49 8b 86 40 01 00 00         	movq	0x140(%r14), %rax
    6f2b: 4c 8d b0 c8 fe ff ff         	leaq	-0x138(%rax), %r14
    6f32: 48 39 c3                     	cmpq	%rax, %rbx
    6f35: 75 c1                        	jne	0x6ef8 <ivi_layout_commit_changes+0x4b8>
    6f37: 49 8b 84 24 20 01 00 00      	movq	0x120(%r12), %rax
    6f3f: 4c 8d a0 e8 fe ff ff         	leaq	-0x118(%rax), %r12
    6f46: 49 39 c5                     	cmpq	%rax, %r13
    6f49: 75 8d                        	jne	0x6ed8 <ivi_layout_commit_changes+0x498>
    6f4b: 48 8b 6d 08                  	movq	0x8(%rbp), %rbp
    6f4f: 4c 39 fd                     	cmpq	%r15, %rbp
    6f52: 0f 85 83 fe ff ff            	jne	0x6ddb <ivi_layout_commit_changes+0x39b>
    6f58: 48 8d 3d 79 a4 20 00         	leaq	0x20a479(%rip), %rdi    # 0x2113d8 <ivilayout+0xd8>
    6f5f: e8 8c c4 ff ff               	callq	0x33f0 <wl_list_empty@plt>
    6f64: 85 c0                        	testl	%eax, %eax
    6f66: 0f 84 b0 10 00 00            	je	0x801c <ivi_layout_commit_changes+0x15dc>
    6f6c: 48 8b 05 bd a3 20 00         	movq	0x20a3bd(%rip), %rax    # 0x211330 <ivilayout+0x30>
    6f73: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
    6f78: 4c 39 f8                     	cmpq	%r15, %rax
    6f7b: 0f 84 b9 0b 00 00            	je	0x7b3a <ivi_layout_commit_changes+0x10fa>
    6f81: 48 8d 84 24 90 00 00 00      	leaq	0x90(%rsp), %rax
    6f89: 48 89 44 24 20               	movq	%rax, 0x20(%rsp)
    6f8e: 48 8d 44 24 70               	leaq	0x70(%rsp), %rax
    6f93: 48 89 44 24 40               	movq	%rax, 0x40(%rsp)
    6f98: 48 8d 84 24 d0 00 00 00      	leaq	0xd0(%rsp), %rax
    6fa0: 48 89 44 24 28               	movq	%rax, 0x28(%rsp)
    6fa5: 48 8b 4c 24 60               	movq	0x60(%rsp), %rcx
    6faa: 48 8b 41 58                  	movq	0x58(%rcx), %rax
    6fae: 48 83 c1 50                  	addq	$0x50, %rcx
    6fb2: 48 89 4c 24 68               	movq	%rcx, 0x68(%rsp)
    6fb7: 4c 8d a0 e8 fe ff ff         	leaq	-0x118(%rax), %r12
    6fbe: 4d 89 e6                     	movq	%r12, %r14
    6fc1: 48 39 c1                     	cmpq	%rax, %rcx
    6fc4: 0f 84 59 0b 00 00            	je	0x7b23 <ivi_layout_commit_changes+0x10e3>
    6fca: 49 8b 86 10 01 00 00         	movq	0x110(%r14), %rax
    6fd1: 49 8d 8e 08 01 00 00         	leaq	0x108(%r14), %rcx
    6fd8: 48 89 4c 24 08               	movq	%rcx, 0x8(%rsp)
    6fdd: 4c 8d a0 c8 fe ff ff         	leaq	-0x138(%rax), %r12
    6fe4: 4d 89 e5                     	movq	%r12, %r13
    6fe7: 48 39 c1                     	cmpq	%rax, %rcx
    6fea: 0f 84 1a 0b 00 00            	je	0x7b0a <ivi_layout_commit_changes+0x10ca>
    6ff0: 41 8b 9e 88 00 00 00         	movl	0x88(%r14), %ebx
    6ff7: 85 db                        	testl	%ebx, %ebx
    6ff9: 75 10                        	jne	0x700b <ivi_layout_commit_changes+0x5cb>
    6ffb: 45 8b 9d dc 00 00 00         	movl	0xdc(%r13), %r11d
    7002: 45 85 db                     	testl	%r11d, %r11d
    7005: 0f 84 e6 0a 00 00            	je	0x7af1 <ivi_layout_commit_changes+0x10b1>
    700b: 48 b8 00 00 00 00 00 00 b8 42	movabsq	$0x42b8000000000000, %rax # imm = 0x42B8000000000000
    7015: 49 63 56 38                  	movslq	0x38(%r14), %rdx
    7019: 49 8b 8d 88 01 00 00         	movq	0x188(%r13), %rcx
    7020: 48 8d 1c 02                  	leaq	(%rdx,%rax), %rbx
    7024: 49 63 95 98 00 00 00         	movslq	0x98(%r13), %rdx
    702b: 66 48 0f 6e cb               	movq	%rbx, %xmm1
    7030: f2 0f 5c 0d 18 68 00 00      	subsd	0x6818(%rip), %xmm1     # 0xd850 <__func__.12894+0x40>
    7038: 48 01 d0                     	addq	%rdx, %rax
    703b: 66 48 0f 6e c0               	movq	%rax, %xmm0
    7040: f2 0f 5c 05 08 68 00 00      	subsd	0x6808(%rip), %xmm0     # 0xd850 <__func__.12894+0x40>
    7048: 48 85 c9                     	testq	%rcx, %rcx
    704b: 0f 84 53 10 00 00            	je	0x80a4 <ivi_layout_commit_changes+0x1664>
    7051: f2 0f 59 c1                  	mulsd	%xmm1, %xmm0
    7055: 49 83 7d 38 00               	cmpq	$0x0, 0x38(%r13)
    705a: 66 0f ef f6                  	pxor	%xmm6, %xmm6
    705e: f2 0f 5a f0                  	cvtsd2ss	%xmm0, %xmm6
    7062: f3 0f 11 71 78               	movss	%xmm6, 0x78(%rcx)
    7067: 0f 84 84 0a 00 00            	je	0x7af1 <ivi_layout_commit_changes+0x10b1>
    706d: 49 8b 9d 88 01 00 00         	movq	0x188(%r13), %rbx
    7074: 48 85 db                     	testq	%rbx, %rbx
    7077: 0f 84 88 0f 00 00            	je	0x8005 <ivi_layout_commit_changes+0x15c5>
    707d: 45 8b 95 a4 00 00 00         	movl	0xa4(%r13), %r10d
    7084: 45 85 d2                     	testl	%r10d, %r10d
    7087: 74 11                        	je	0x709a <ivi_layout_commit_changes+0x65a>
    7089: 45 8b 8d a8 00 00 00         	movl	0xa8(%r13), %r9d
    7090: b8 01 00 00 00               	movl	$0x1, %eax
    7095: 45 85 c9                     	testl	%r9d, %r9d
    7098: 75 10                        	jne	0x70aa <ivi_layout_commit_changes+0x66a>
    709a: 48 8d 3d d7 63 00 00         	leaq	0x63d7(%rip), %rdi      # 0xd478 <zwp_input_panel_v1_interface+0xd478>
    70a1: 31 c0                        	xorl	%eax, %eax
    70a3: e8 68 c1 ff ff               	callq	0x3210 <weston_log@plt>
    70a8: 31 c0                        	xorl	%eax, %eax
    70aa: 45 8b 85 c4 00 00 00         	movl	0xc4(%r13), %r8d
    70b1: 45 85 c0                     	testl	%r8d, %r8d
    70b4: 0f 84 ee 09 00 00            	je	0x7aa8 <ivi_layout_commit_changes+0x1068>
    70ba: 41 8b bd c8 00 00 00         	movl	0xc8(%r13), %edi
    70c1: 85 ff                        	testl	%edi, %edi
    70c3: 0f 84 df 09 00 00            	je	0x7aa8 <ivi_layout_commit_changes+0x1068>
    70c9: 84 c0                        	testb	%al, %al
    70cb: 0f 84 e5 09 00 00            	je	0x7ab6 <ivi_layout_commit_changes+0x1076>
    70d1: 49 8d 85 88 00 00 00         	leaq	0x88(%r13), %rax
    70d8: 49 8d 6d 40                  	leaq	0x40(%r13), %rbp
    70dc: 48 89 c7                     	movq	%rax, %rdi
    70df: 48 89 44 24 50               	movq	%rax, 0x50(%rsp)
    70e4: e8 47 c3 ff ff               	callq	0x3430 <wl_list_remove@plt>
    70e9: 48 89 ef                     	movq	%rbp, %rdi
    70ec: e8 2f c0 ff ff               	callq	0x3120 <weston_matrix_init@plt>
    70f1: 41 8b 85 9c 00 00 00         	movl	0x9c(%r13), %eax
    70f8: 48 89 e9                     	movq	%rbp, %rcx
    70fb: 89 44 24 70                  	movl	%eax, 0x70(%rsp)
    70ff: 41 8b 85 a0 00 00 00         	movl	0xa0(%r13), %eax
    7106: 89 44 24 74                  	movl	%eax, 0x74(%rsp)
    710a: 41 8b 85 a4 00 00 00         	movl	0xa4(%r13), %eax
    7111: 89 44 24 78                  	movl	%eax, 0x78(%rsp)
    7115: 41 8b 85 a8 00 00 00         	movl	0xa8(%r13), %eax
    711c: 89 44 24 7c                  	movl	%eax, 0x7c(%rsp)
    7120: 41 8b 85 bc 00 00 00         	movl	0xbc(%r13), %eax
    7127: 89 84 24 90 00 00 00         	movl	%eax, 0x90(%rsp)
    712e: 41 8b 85 c0 00 00 00         	movl	0xc0(%r13), %eax
    7135: 89 84 24 94 00 00 00         	movl	%eax, 0x94(%rsp)
    713c: 41 8b 85 c4 00 00 00         	movl	0xc4(%r13), %eax
    7143: 89 84 24 98 00 00 00         	movl	%eax, 0x98(%rsp)
    714a: 41 8b 85 c8 00 00 00         	movl	0xc8(%r13), %eax
    7151: 89 84 24 9c 00 00 00         	movl	%eax, 0x9c(%rsp)
    7158: 41 8b 46 3c                  	movl	0x3c(%r14), %eax
    715c: 89 84 24 b0 00 00 00         	movl	%eax, 0xb0(%rsp)
    7163: 41 8b 46 40                  	movl	0x40(%r14), %eax
    7167: 89 84 24 b4 00 00 00         	movl	%eax, 0xb4(%rsp)
    716e: 41 8b 46 44                  	movl	0x44(%r14), %eax
    7172: 89 84 24 b8 00 00 00         	movl	%eax, 0xb8(%rsp)
    7179: 41 8b 46 48                  	movl	0x48(%r14), %eax
    717d: 89 84 24 bc 00 00 00         	movl	%eax, 0xbc(%rsp)
    7184: 41 8b 46 4c                  	movl	0x4c(%r14), %eax
    7188: 89 84 24 d0 00 00 00         	movl	%eax, 0xd0(%rsp)
    718f: 41 8b 46 50                  	movl	0x50(%r14), %eax
    7193: 89 84 24 d4 00 00 00         	movl	%eax, 0xd4(%rsp)
    719a: 41 8b 46 54                  	movl	0x54(%r14), %eax
    719e: 89 84 24 d8 00 00 00         	movl	%eax, 0xd8(%rsp)
    71a5: 41 8b 46 58                  	movl	0x58(%r14), %eax
    71a9: 89 84 24 dc 00 00 00         	movl	%eax, 0xdc(%rsp)
    71b0: 41 8b 95 cc 00 00 00         	movl	0xcc(%r13), %edx
    71b7: 4c 8b 64 24 40               	movq	0x40(%rsp), %r12
    71bc: 48 8b 74 24 20               	movq	0x20(%rsp), %rsi
    71c1: 4c 89 e7                     	movq	%r12, %rdi
    71c4: e8 57 e2 ff ff               	callq	0x5420 <calc_transformation_matrix>
    71c9: 41 8b 56 5c                  	movl	0x5c(%r14), %edx
    71cd: 48 8d 84 24 b0 00 00 00      	leaq	0xb0(%rsp), %rax
    71d5: 48 89 e9                     	movq	%rbp, %rcx
    71d8: 48 8b 74 24 28               	movq	0x28(%rsp), %rsi
    71dd: 48 89 c7                     	movq	%rax, %rdi
    71e0: 48 89 44 24 48               	movq	%rax, 0x48(%rsp)
    71e5: e8 36 e2 ff ff               	callq	0x5420 <calc_transformation_matrix>
    71ea: 48 8b 44 24 60               	movq	0x60(%rsp), %rax
    71ef: 4c 89 e7                     	movq	%r12, %rdi
    71f2: 41 8b 8d a4 00 00 00         	movl	0xa4(%r13), %ecx
    71f9: 41 8b 95 a0 00 00 00         	movl	0xa0(%r13), %edx
    7200: 41 8b b5 9c 00 00 00         	movl	0x9c(%r13), %esi
    7207: 48 8b 40 20                  	movq	0x20(%rax), %rax
    720b: 45 8b 85 a8 00 00 00         	movl	0xa8(%r13), %r8d
    7212: 48 89 44 24 58               	movq	%rax, 0x58(%rsp)
    7217: e8 54 c3 ff ff               	callq	0x3570 <pixman_region32_init_rect@plt>
    721c: 4c 89 e7                     	movq	%r12, %rdi
    721f: e8 6c c0 ff ff               	callq	0x3290 <pixman_region32_extents@plt>
    7224: 8b 10                        	movl	(%rax), %edx
    7226: 8b 48 04                     	movl	0x4(%rax), %ecx
    7229: 8b 70 0c                     	movl	0xc(%rax), %esi
    722c: 8b 40 08                     	movl	0x8(%rax), %eax
    722f: 89 94 24 00 01 00 00         	movl	%edx, 0x100(%rsp)
    7236: 89 8c 24 04 01 00 00         	movl	%ecx, 0x104(%rsp)
    723d: 89 94 24 08 01 00 00         	movl	%edx, 0x108(%rsp)
    7244: 89 b4 24 0c 01 00 00         	movl	%esi, 0x10c(%rsp)
    724b: 89 84 24 10 01 00 00         	movl	%eax, 0x110(%rsp)
    7252: 89 8c 24 14 01 00 00         	movl	%ecx, 0x114(%rsp)
    7259: 89 84 24 18 01 00 00         	movl	%eax, 0x118(%rsp)
    7260: 89 b4 24 1c 01 00 00         	movl	%esi, 0x11c(%rsp)
    7267: 39 f1                        	cmpl	%esi, %ecx
    7269: 0f 84 87 0d 00 00            	je	0x7ff6 <ivi_layout_commit_changes+0x15b6>
    726f: 39 c2                        	cmpl	%eax, %edx
    7271: 0f 84 7f 0d 00 00            	je	0x7ff6 <ivi_layout_commit_changes+0x15b6>
    7277: 4c 8d a4 24 00 01 00 00      	leaq	0x100(%rsp), %r12
    727f: f3 0f 10 25 ad 65 00 00      	movss	0x65ad(%rip), %xmm4     # 0xd834 <__func__.12894+0x24>
    7287: f3 0f 10 2d a9 65 00 00      	movss	0x65a9(%rip), %xmm5     # 0xd838 <__func__.12894+0x28>
    728f: 49 8d 44 24 20               	leaq	0x20(%r12), %rax
    7294: 48 89 44 24 30               	movq	%rax, 0x30(%rsp)
    7299: 48 8d 84 24 f0 00 00 00      	leaq	0xf0(%rsp), %rax
    72a1: f3 0f 11 64 24 10            	movss	%xmm4, 0x10(%rsp)
    72a7: 0f 28 c5                     	movaps	%xmm5, %xmm0
    72aa: 48 89 44 24 38               	movq	%rax, 0x38(%rsp)
    72af: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    72b3: f3 0f 2a ca                  	cvtsi2ss	%edx, %xmm1
    72b7: 48 89 ef                     	movq	%rbp, %rdi
    72ba: 48 8b 74 24 38               	movq	0x38(%rsp), %rsi
    72bf: f3 0f 11 64 24 1c            	movss	%xmm4, 0x1c(%rsp)
    72c5: 49 83 c4 08                  	addq	$0x8, %r12
    72c9: f3 0f 11 44 24 18            	movss	%xmm0, 0x18(%rsp)
    72cf: f3 0f 11 6c 24 14            	movss	%xmm5, 0x14(%rsp)
    72d5: f3 0f 11 8c 24 f0 00 00 00   	movss	%xmm1, 0xf0(%rsp)
    72de: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    72e2: f3 0f 2a c9                  	cvtsi2ss	%ecx, %xmm1
    72e6: c7 84 24 f8 00 00 00 00 00 00 00     	movl	$0x0, 0xf8(%rsp)
    72f1: c7 84 24 fc 00 00 00 00 00 80 3f     	movl	$0x3f800000, 0xfc(%rsp) # imm = 0x3F800000
    72fc: f3 0f 11 8c 24 f4 00 00 00   	movss	%xmm1, 0xf4(%rsp)
    7305: e8 16 c3 ff ff               	callq	0x3620 <weston_matrix_transform@plt>
    730a: f3 0f 10 44 24 18            	movss	0x18(%rsp), %xmm0
    7310: f3 0f 10 9c 24 fc 00 00 00   	movss	0xfc(%rsp), %xmm3
    7319: f3 0f 10 94 24 f0 00 00 00   	movss	0xf0(%rsp), %xmm2
    7322: f3 0f 10 8c 24 f4 00 00 00   	movss	0xf4(%rsp), %xmm1
    732b: f3 0f 5e d3                  	divss	%xmm3, %xmm2
    732f: f3 0f 10 6c 24 14            	movss	0x14(%rsp), %xmm5
    7335: f3 0f 10 64 24 1c            	movss	0x1c(%rsp), %xmm4
    733b: f3 0f 5e cb                  	divss	%xmm3, %xmm1
    733f: 0f 28 fa                     	movaps	%xmm2, %xmm7
    7342: f3 0f 5f 54 24 10            	maxss	0x10(%rsp), %xmm2
    7348: f3 0f 5d f8                  	minss	%xmm0, %xmm7
    734c: f3 0f 11 54 24 10            	movss	%xmm2, 0x10(%rsp)
    7352: 0f 28 c7                     	movaps	%xmm7, %xmm0
    7355: 0f 28 f9                     	movaps	%xmm1, %xmm7
    7358: f3 0f 5f cc                  	maxss	%xmm4, %xmm1
    735c: f3 0f 5d fd                  	minss	%xmm5, %xmm7
    7360: 0f 28 e1                     	movaps	%xmm1, %xmm4
    7363: 0f 28 ef                     	movaps	%xmm7, %xmm5
    7366: 4c 39 64 24 30               	cmpq	%r12, 0x30(%rsp)
    736b: 0f 84 cf 08 00 00            	je	0x7c40 <ivi_layout_commit_changes+0x1200>
    7371: 41 8b 14 24                  	movl	(%r12), %edx
    7375: 41 8b 4c 24 04               	movl	0x4(%r12), %ecx
    737a: e9 30 ff ff ff               	jmp	0x72af <ivi_layout_commit_changes+0x86f>
    737f: 8b 8b c0 00 00 00            	movl	0xc0(%rbx), %ecx
    7385: 48 89 df                     	movq	%rbx, %rdi
    7388: 8b 93 a8 00 00 00            	movl	0xa8(%rbx), %edx
    738e: 8b b3 a4 00 00 00            	movl	0xa4(%rbx), %esi
    7394: 44 8b 73 4c                  	movl	0x4c(%rbx), %r14d
    7398: 44 8b 6b 50                  	movl	0x50(%rbx), %r13d
    739c: 44 8b 63 54                  	movl	0x54(%rbx), %r12d
    73a0: 8b 6b 58                     	movl	0x58(%rbx), %ebp
    73a3: e8 78 24 00 00               	callq	0x9820 <ivi_layout_transition_move_layer>
    73a8: 48 8b 83 90 00 00 00         	movq	0x90(%rbx), %rax
    73af: 44 89 6b 50                  	movl	%r13d, 0x50(%rbx)
    73b3: 44 89 63 54                  	movl	%r12d, 0x54(%rbx)
    73b7: 48 89 43 38                  	movq	%rax, 0x38(%rbx)
    73bb: 48 8b 83 98 00 00 00         	movq	0x98(%rbx), %rax
    73c2: 48 89 43 40                  	movq	%rax, 0x40(%rbx)
    73c6: 48 8b 83 a0 00 00 00         	movq	0xa0(%rbx), %rax
    73cd: 48 89 43 48                  	movq	%rax, 0x48(%rbx)
    73d1: 48 8b 83 b0 00 00 00         	movq	0xb0(%rbx), %rax
    73d8: 44 89 73 4c                  	movl	%r14d, 0x4c(%rbx)
    73dc: 48 89 43 58                  	movq	%rax, 0x58(%rbx)
    73e0: 48 8b 83 b8 00 00 00         	movq	0xb8(%rbx), %rax
    73e7: 89 6b 58                     	movl	%ebp, 0x58(%rbx)
    73ea: 48 89 43 60                  	movq	%rax, 0x60(%rbx)
    73ee: 48 8b 83 c0 00 00 00         	movq	0xc0(%rbx), %rax
    73f5: 48 89 43 68                  	movq	%rax, 0x68(%rbx)
    73f9: 48 8b 83 c8 00 00 00         	movq	0xc8(%rbx), %rax
    7400: 48 89 43 70                  	movq	%rax, 0x70(%rbx)
    7404: 48 8b 83 d0 00 00 00         	movq	0xd0(%rbx), %rax
    740b: 48 89 43 78                  	movq	%rax, 0x78(%rbx)
    740f: 48 8b 83 d8 00 00 00         	movq	0xd8(%rbx), %rax
    7416: 48 89 83 80 00 00 00         	movq	%rax, 0x80(%rbx)
    741d: e9 67 f8 ff ff               	jmp	0x6c89 <ivi_layout_commit_changes+0x249>
    7422: 8b b3 d8 00 00 00            	movl	0xd8(%rbx), %esi
    7428: 31 c9                        	xorl	%ecx, %ecx
    742a: 31 d2                        	xorl	%edx, %edx
    742c: 48 89 df                     	movq	%rbx, %rdi
    742f: 44 8b 83 c0 00 00 00         	movl	0xc0(%rbx), %r8d
    7436: f2 0f 10 8b d0 00 00 00      	movsd	0xd0(%rbx), %xmm1
    743e: f2 0f 10 83 c8 00 00 00      	movsd	0xc8(%rbx), %xmm0
    7446: e8 b5 25 00 00               	callq	0x9a00 <ivi_layout_transition_fade_layer>
    744b: e9 c8 f7 ff ff               	jmp	0x6c18 <ivi_layout_commit_changes+0x1d8>
    7450: 80 bd 18 01 00 00 00         	cmpb	$0x0, 0x118(%rbp)
    7457: 48 89 ef                     	movq	%rbp, %rdi
    745a: 8b b5 20 01 00 00            	movl	0x120(%rbp), %esi
    7460: 0f 84 20 05 00 00            	je	0x7986 <ivi_layout_commit_changes+0xf46>
    7466: e8 f5 20 00 00               	callq	0x9560 <ivi_layout_transition_visibility_on>
    746b: 8b 85 0c 01 00 00            	movl	0x10c(%rbp), %eax
    7471: 39 85 c4 00 00 00            	cmpl	%eax, 0xc4(%rbp)
    7477: 0f 84 20 05 00 00            	je	0x799d <ivi_layout_commit_changes+0xf5d>
    747d: 48 8b 85 e0 00 00 00         	movq	0xe0(%rbp), %rax
    7484: 48 89 ef                     	movq	%rbp, %rdi
    7487: 48 89 85 98 00 00 00         	movq	%rax, 0x98(%rbp)
    748e: 48 8b 85 e8 00 00 00         	movq	0xe8(%rbp), %rax
    7495: 48 89 85 a0 00 00 00         	movq	%rax, 0xa0(%rbp)
    749c: 48 8b 85 f0 00 00 00         	movq	0xf0(%rbp), %rax
    74a3: 48 89 85 a8 00 00 00         	movq	%rax, 0xa8(%rbp)
    74aa: 48 8b 85 f8 00 00 00         	movq	0xf8(%rbp), %rax
    74b1: 48 89 85 b0 00 00 00         	movq	%rax, 0xb0(%rbp)
    74b8: 48 8b 85 00 01 00 00         	movq	0x100(%rbp), %rax
    74bf: 48 89 85 b8 00 00 00         	movq	%rax, 0xb8(%rbp)
    74c6: 48 8b 85 08 01 00 00         	movq	0x108(%rbp), %rax
    74cd: 48 89 85 c0 00 00 00         	movq	%rax, 0xc0(%rbp)
    74d4: 48 8b 85 10 01 00 00         	movq	0x110(%rbp), %rax
    74db: 48 89 85 c8 00 00 00         	movq	%rax, 0xc8(%rbp)
    74e2: 48 8b 85 18 01 00 00         	movq	0x118(%rbp), %rax
    74e9: c7 85 1c 01 00 00 00 00 00 00	movl	$0x0, 0x11c(%rbp)
    74f3: 48 89 85 d0 00 00 00         	movq	%rax, 0xd0(%rbp)
    74fa: 8b 85 20 01 00 00            	movl	0x120(%rbp), %eax
    7500: c7 85 d4 00 00 00 00 00 00 00	movl	$0x0, 0xd4(%rbp)
    750a: 89 85 d8 00 00 00            	movl	%eax, 0xd8(%rbp)
    7510: e8 fb 1b 00 00               	callq	0x9110 <is_surface_transition>
    7515: 85 c0                        	testl	%eax, %eax
    7517: 0f 85 b2 f6 ff ff            	jne	0x6bcf <ivi_layout_commit_changes+0x18f>
    751d: 48 8b 85 70 01 00 00         	movq	0x170(%rbp), %rax
    7524: 4c 8d a5 68 01 00 00         	leaq	0x168(%rbp), %r12
    752b: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    752f: 49 39 c4                     	cmpq	%rax, %r12
    7532: 75 0f                        	jne	0x7543 <ivi_layout_commit_changes+0xb03>
    7534: e9 96 f6 ff ff               	jmp	0x6bcf <ivi_layout_commit_changes+0x18f>
    7539: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    7540: 48 89 d3                     	movq	%rdx, %rbx
    7543: 48 89 c7                     	movq	%rax, %rdi
    7546: 48 89 ee                     	movq	%rbp, %rsi
    7549: ff 50 10                     	callq	*0x10(%rax)
    754c: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    7550: 48 89 d8                     	movq	%rbx, %rax
    7553: 49 39 dc                     	cmpq	%rbx, %r12
    7556: 75 e8                        	jne	0x7540 <ivi_layout_commit_changes+0xb00>
    7558: e9 72 f6 ff ff               	jmp	0x6bcf <ivi_layout_commit_changes+0x18f>
    755d: 8b 85 10 01 00 00            	movl	0x110(%rbp), %eax
    7563: 39 85 c8 00 00 00            	cmpl	%eax, 0xc8(%rbp)
    7569: 0f 85 48 f5 ff ff            	jne	0x6ab7 <ivi_layout_commit_changes+0x77>
    756f: 48 8b 85 e0 00 00 00         	movq	0xe0(%rbp), %rax
    7576: 48 89 85 98 00 00 00         	movq	%rax, 0x98(%rbp)
    757d: 48 8b 85 e8 00 00 00         	movq	0xe8(%rbp), %rax
    7584: 48 89 85 a0 00 00 00         	movq	%rax, 0xa0(%rbp)
    758b: 48 8b 85 f0 00 00 00         	movq	0xf0(%rbp), %rax
    7592: 48 89 85 a8 00 00 00         	movq	%rax, 0xa8(%rbp)
    7599: 48 8b 85 f8 00 00 00         	movq	0xf8(%rbp), %rax
    75a0: 48 89 85 b0 00 00 00         	movq	%rax, 0xb0(%rbp)
    75a7: 48 8b 85 00 01 00 00         	movq	0x100(%rbp), %rax
    75ae: 48 89 85 b8 00 00 00         	movq	%rax, 0xb8(%rbp)
    75b5: 48 8b 85 08 01 00 00         	movq	0x108(%rbp), %rax
    75bc: 48 89 85 c0 00 00 00         	movq	%rax, 0xc0(%rbp)
    75c3: 48 8b 85 10 01 00 00         	movq	0x110(%rbp), %rax
    75ca: 48 89 85 c8 00 00 00         	movq	%rax, 0xc8(%rbp)
    75d1: 48 8b 85 18 01 00 00         	movq	0x118(%rbp), %rax
    75d8: c7 85 1c 01 00 00 00 00 00 00	movl	$0x0, 0x11c(%rbp)
    75e2: 48 89 85 d0 00 00 00         	movq	%rax, 0xd0(%rbp)
    75e9: 8b 85 20 01 00 00            	movl	0x120(%rbp), %eax
    75ef: c7 85 d4 00 00 00 00 00 00 00	movl	$0x0, 0xd4(%rbp)
    75f9: 89 85 d8 00 00 00            	movl	%eax, 0xd8(%rbp)
    75ff: e9 cb f5 ff ff               	jmp	0x6bcf <ivi_layout_commit_changes+0x18f>
    7604: 8b 85 bc 00 00 00            	movl	0xbc(%rbp), %eax
    760a: 48 83 ec 08                  	subq	$0x8, %rsp
    760e: 48 89 ef                     	movq	%rbp, %rdi
    7611: 8b b5 04 01 00 00            	movl	0x104(%rbp), %esi
    7617: 8b 8d 0c 01 00 00            	movl	0x10c(%rbp), %ecx
    761d: 8b 95 08 01 00 00            	movl	0x108(%rbp), %edx
    7623: 44 8b 8d 20 01 00 00         	movl	0x120(%rbp), %r9d
    762a: 89 44 24 10                  	movl	%eax, 0x10(%rsp)
    762e: 44 8b 85 10 01 00 00         	movl	0x110(%rbp), %r8d
    7635: 44 8b ad c0 00 00 00         	movl	0xc0(%rbp), %r13d
    763c: 44 8b b5 c4 00 00 00         	movl	0xc4(%rbp), %r14d
    7643: 44 8b bd c8 00 00 00         	movl	0xc8(%rbp), %r15d
    764a: 6a 0a                        	pushq	$0xa
    764c: e8 2f 1d 00 00               	callq	0x9380 <ivi_layout_transition_move_resize_view>
    7651: 80 bd 18 01 00 00 00         	cmpb	$0x0, 0x118(%rbp)
    7658: 5e                           	popq	%rsi
    7659: 8b b5 20 01 00 00            	movl	0x120(%rbp), %esi
    765f: 5f                           	popq	%rdi
    7660: 48 89 ef                     	movq	%rbp, %rdi
    7663: 0f 84 6a 03 00 00            	je	0x79d3 <ivi_layout_commit_changes+0xf93>
    7669: e8 f2 1e 00 00               	callq	0x9560 <ivi_layout_transition_visibility_on>
    766e: 48 8b 85 e0 00 00 00         	movq	0xe0(%rbp), %rax
    7675: 48 8d 9d 68 01 00 00         	leaq	0x168(%rbp), %rbx
    767c: 48 89 85 98 00 00 00         	movq	%rax, 0x98(%rbp)
    7683: 48 8b 85 e8 00 00 00         	movq	0xe8(%rbp), %rax
    768a: 48 89 85 a0 00 00 00         	movq	%rax, 0xa0(%rbp)
    7691: 48 8b 85 f0 00 00 00         	movq	0xf0(%rbp), %rax
    7698: 48 89 85 a8 00 00 00         	movq	%rax, 0xa8(%rbp)
    769f: 48 8b 85 f8 00 00 00         	movq	0xf8(%rbp), %rax
    76a6: 48 89 85 b0 00 00 00         	movq	%rax, 0xb0(%rbp)
    76ad: 48 8b 85 00 01 00 00         	movq	0x100(%rbp), %rax
    76b4: 48 89 85 b8 00 00 00         	movq	%rax, 0xb8(%rbp)
    76bb: 48 8b 85 08 01 00 00         	movq	0x108(%rbp), %rax
    76c2: 48 89 85 c0 00 00 00         	movq	%rax, 0xc0(%rbp)
    76c9: 48 8b 85 10 01 00 00         	movq	0x110(%rbp), %rax
    76d0: 48 89 85 c8 00 00 00         	movq	%rax, 0xc8(%rbp)
    76d7: 48 8b 85 18 01 00 00         	movq	0x118(%rbp), %rax
    76de: 48 89 85 d0 00 00 00         	movq	%rax, 0xd0(%rbp)
    76e5: 8b 85 20 01 00 00            	movl	0x120(%rbp), %eax
    76eb: 89 85 d8 00 00 00            	movl	%eax, 0xd8(%rbp)
    76f1: 48 8b 85 70 01 00 00         	movq	0x170(%rbp), %rax
    76f8: 4c 8b 60 08                  	movq	0x8(%rax), %r12
    76fc: 48 39 c3                     	cmpq	%rax, %rbx
    76ff: 75 0a                        	jne	0x770b <ivi_layout_commit_changes+0xccb>
    7701: eb 1e                        	jmp	0x7721 <ivi_layout_commit_changes+0xce1>
    7703: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    7708: 49 89 cc                     	movq	%rcx, %r12
    770b: 48 89 c7                     	movq	%rax, %rdi
    770e: 48 89 ee                     	movq	%rbp, %rsi
    7711: ff 50 10                     	callq	*0x10(%rax)
    7714: 49 8b 4c 24 08               	movq	0x8(%r12), %rcx
    7719: 4c 89 e0                     	movq	%r12, %rax
    771c: 4c 39 e3                     	cmpq	%r12, %rbx
    771f: 75 e7                        	jne	0x7708 <ivi_layout_commit_changes+0xcc8>
    7721: 8b 44 24 08                  	movl	0x8(%rsp), %eax
    7725: 44 89 ad c0 00 00 00         	movl	%r13d, 0xc0(%rbp)
    772c: 44 89 b5 c4 00 00 00         	movl	%r14d, 0xc4(%rbp)
    7733: 44 89 bd c8 00 00 00         	movl	%r15d, 0xc8(%rbp)
    773a: c7 85 d4 00 00 00 00 00 00 00	movl	$0x0, 0xd4(%rbp)
    7744: 89 85 bc 00 00 00            	movl	%eax, 0xbc(%rbp)
    774a: c7 85 1c 01 00 00 00 00 00 00	movl	$0x0, 0x11c(%rbp)
    7754: e9 76 f4 ff ff               	jmp	0x6bcf <ivi_layout_commit_changes+0x18f>
    7759: 8b 85 bc 00 00 00            	movl	0xbc(%rbp), %eax
    775f: 48 83 ec 08                  	subq	$0x8, %rsp
    7763: 48 89 ef                     	movq	%rbp, %rdi
    7766: 8b b5 04 01 00 00            	movl	0x104(%rbp), %esi
    776c: 8b 8d 0c 01 00 00            	movl	0x10c(%rbp), %ecx
    7772: 8b 95 08 01 00 00            	movl	0x108(%rbp), %edx
    7778: 44 8b 8d 20 01 00 00         	movl	0x120(%rbp), %r9d
    777f: 89 44 24 10                  	movl	%eax, 0x10(%rsp)
    7783: 44 8b 85 10 01 00 00         	movl	0x110(%rbp), %r8d
    778a: 44 8b ad c0 00 00 00         	movl	0xc0(%rbp), %r13d
    7791: 44 8b b5 c4 00 00 00         	movl	0xc4(%rbp), %r14d
    7798: 44 8b bd c8 00 00 00         	movl	0xc8(%rbp), %r15d
    779f: 6a 07                        	pushq	$0x7
    77a1: e8 da 1b 00 00               	callq	0x9380 <ivi_layout_transition_move_resize_view>
    77a6: 80 bd 18 01 00 00 00         	cmpb	$0x0, 0x118(%rbp)
    77ad: 48 89 ef                     	movq	%rbp, %rdi
    77b0: 41 58                        	popq	%r8
    77b2: 8b b5 20 01 00 00            	movl	0x120(%rbp), %esi
    77b8: 41 59                        	popq	%r9
    77ba: 0f 84 1d 02 00 00            	je	0x79dd <ivi_layout_commit_changes+0xf9d>
    77c0: e8 9b 1d 00 00               	callq	0x9560 <ivi_layout_transition_visibility_on>
    77c5: 48 8b 85 e0 00 00 00         	movq	0xe0(%rbp), %rax
    77cc: 48 8d 9d 68 01 00 00         	leaq	0x168(%rbp), %rbx
    77d3: 48 89 85 98 00 00 00         	movq	%rax, 0x98(%rbp)
    77da: 48 8b 85 e8 00 00 00         	movq	0xe8(%rbp), %rax
    77e1: 48 89 85 a0 00 00 00         	movq	%rax, 0xa0(%rbp)
    77e8: 48 8b 85 f0 00 00 00         	movq	0xf0(%rbp), %rax
    77ef: 48 89 85 a8 00 00 00         	movq	%rax, 0xa8(%rbp)
    77f6: 48 8b 85 f8 00 00 00         	movq	0xf8(%rbp), %rax
    77fd: 48 89 85 b0 00 00 00         	movq	%rax, 0xb0(%rbp)
    7804: 48 8b 85 00 01 00 00         	movq	0x100(%rbp), %rax
    780b: 48 89 85 b8 00 00 00         	movq	%rax, 0xb8(%rbp)
    7812: 48 8b 85 08 01 00 00         	movq	0x108(%rbp), %rax
    7819: 48 89 85 c0 00 00 00         	movq	%rax, 0xc0(%rbp)
    7820: 48 8b 85 10 01 00 00         	movq	0x110(%rbp), %rax
    7827: 48 89 85 c8 00 00 00         	movq	%rax, 0xc8(%rbp)
    782e: 48 8b 85 18 01 00 00         	movq	0x118(%rbp), %rax
    7835: 48 89 85 d0 00 00 00         	movq	%rax, 0xd0(%rbp)
    783c: 8b 85 20 01 00 00            	movl	0x120(%rbp), %eax
    7842: 89 85 d8 00 00 00            	movl	%eax, 0xd8(%rbp)
    7848: 48 8b 85 70 01 00 00         	movq	0x170(%rbp), %rax
    784f: 4c 8b 60 08                  	movq	0x8(%rax), %r12
    7853: 48 39 c3                     	cmpq	%rax, %rbx
    7856: 75 0b                        	jne	0x7863 <ivi_layout_commit_changes+0xe23>
    7858: e9 c4 fe ff ff               	jmp	0x7721 <ivi_layout_commit_changes+0xce1>
    785d: 0f 1f 00                     	nopl	(%rax)
    7860: 49 89 cc                     	movq	%rcx, %r12
    7863: 48 89 c7                     	movq	%rax, %rdi
    7866: 48 89 ee                     	movq	%rbp, %rsi
    7869: ff 50 10                     	callq	*0x10(%rax)
    786c: 49 8b 4c 24 08               	movq	0x8(%r12), %rcx
    7871: 4c 89 e0                     	movq	%r12, %rax
    7874: 4c 39 e3                     	cmpq	%r12, %rbx
    7877: 75 e7                        	jne	0x7860 <ivi_layout_commit_changes+0xe20>
    7879: e9 a3 fe ff ff               	jmp	0x7721 <ivi_layout_commit_changes+0xce1>
    787e: 8b 85 bc 00 00 00            	movl	0xbc(%rbp), %eax
    7884: 48 83 ec 08                  	subq	$0x8, %rsp
    7888: 48 89 ef                     	movq	%rbp, %rdi
    788b: 8b 8d 0c 01 00 00            	movl	0x10c(%rbp), %ecx
    7891: 48 8d 9d 68 01 00 00         	leaq	0x168(%rbp), %rbx
    7898: 8b 95 08 01 00 00            	movl	0x108(%rbp), %edx
    789e: 8b b5 04 01 00 00            	movl	0x104(%rbp), %esi
    78a4: 44 8b 8d 20 01 00 00         	movl	0x120(%rbp), %r9d
    78ab: 89 44 24 10                  	movl	%eax, 0x10(%rsp)
    78af: 44 8b 85 10 01 00 00         	movl	0x110(%rbp), %r8d
    78b6: 44 8b ad c0 00 00 00         	movl	0xc0(%rbp), %r13d
    78bd: 44 8b b5 c4 00 00 00         	movl	0xc4(%rbp), %r14d
    78c4: 44 8b bd c8 00 00 00         	movl	0xc8(%rbp), %r15d
    78cb: 6a 07                        	pushq	$0x7
    78cd: e8 ae 1a 00 00               	callq	0x9380 <ivi_layout_transition_move_resize_view>
    78d2: 48 8b 85 e0 00 00 00         	movq	0xe0(%rbp), %rax
    78d9: 48 89 85 98 00 00 00         	movq	%rax, 0x98(%rbp)
    78e0: 48 8b 85 e8 00 00 00         	movq	0xe8(%rbp), %rax
    78e7: 48 89 85 a0 00 00 00         	movq	%rax, 0xa0(%rbp)
    78ee: 48 8b 85 f0 00 00 00         	movq	0xf0(%rbp), %rax
    78f5: 48 89 85 a8 00 00 00         	movq	%rax, 0xa8(%rbp)
    78fc: 48 8b 85 f8 00 00 00         	movq	0xf8(%rbp), %rax
    7903: 48 89 85 b0 00 00 00         	movq	%rax, 0xb0(%rbp)
    790a: 48 8b 85 00 01 00 00         	movq	0x100(%rbp), %rax
    7911: 48 89 85 b8 00 00 00         	movq	%rax, 0xb8(%rbp)
    7918: 48 8b 85 08 01 00 00         	movq	0x108(%rbp), %rax
    791f: 48 89 85 c0 00 00 00         	movq	%rax, 0xc0(%rbp)
    7926: 48 8b 85 10 01 00 00         	movq	0x110(%rbp), %rax
    792d: 48 89 85 c8 00 00 00         	movq	%rax, 0xc8(%rbp)
    7934: 48 8b 85 18 01 00 00         	movq	0x118(%rbp), %rax
    793b: 48 89 85 d0 00 00 00         	movq	%rax, 0xd0(%rbp)
    7942: 8b 85 20 01 00 00            	movl	0x120(%rbp), %eax
    7948: 89 85 d8 00 00 00            	movl	%eax, 0xd8(%rbp)
    794e: 48 8b 85 70 01 00 00         	movq	0x170(%rbp), %rax
    7955: 5a                           	popq	%rdx
    7956: 59                           	popq	%rcx
    7957: 4c 8b 60 08                  	movq	0x8(%rax), %r12
    795b: 48 39 c3                     	cmpq	%rax, %rbx
    795e: 75 0b                        	jne	0x796b <ivi_layout_commit_changes+0xf2b>
    7960: e9 bc fd ff ff               	jmp	0x7721 <ivi_layout_commit_changes+0xce1>
    7965: 0f 1f 00                     	nopl	(%rax)
    7968: 49 89 cc                     	movq	%rcx, %r12
    796b: 48 89 c7                     	movq	%rax, %rdi
    796e: 48 89 ee                     	movq	%rbp, %rsi
    7971: ff 50 10                     	callq	*0x10(%rax)
    7974: 49 8b 4c 24 08               	movq	0x8(%r12), %rcx
    7979: 4c 89 e0                     	movq	%r12, %rax
    797c: 4c 39 e3                     	cmpq	%r12, %rbx
    797f: 75 e7                        	jne	0x7968 <ivi_layout_commit_changes+0xf28>
    7981: e9 9b fd ff ff               	jmp	0x7721 <ivi_layout_commit_changes+0xce1>
    7986: e8 55 1d 00 00               	callq	0x96e0 <ivi_layout_transition_visibility_off>
    798b: 8b 85 0c 01 00 00            	movl	0x10c(%rbp), %eax
    7991: 39 85 c4 00 00 00            	cmpl	%eax, 0xc4(%rbp)
    7997: 0f 85 e0 fa ff ff            	jne	0x747d <ivi_layout_commit_changes+0xa3d>
    799d: 8b 85 10 01 00 00            	movl	0x110(%rbp), %eax
    79a3: 39 85 c8 00 00 00            	cmpl	%eax, 0xc8(%rbp)
    79a9: 0f 85 ce fa ff ff            	jne	0x747d <ivi_layout_commit_changes+0xa3d>
    79af: e9 bb fb ff ff               	jmp	0x756f <ivi_layout_commit_changes+0xb2f>
    79b4: 48 8d 0d 15 5e 00 00         	leaq	0x5e15(%rip), %rcx      # 0xd7d0 <__PRETTY_FUNCTION__.13149>
    79bb: ba 90 04 00 00               	movl	$0x490, %edx            # imm = 0x490
    79c0: 48 8d 35 d6 5b 00 00         	leaq	0x5bd6(%rip), %rsi      # 0xd59d <zwp_input_panel_v1_interface+0xd59d>
    79c7: 48 8d 3d 03 5c 00 00         	leaq	0x5c03(%rip), %rdi      # 0xd5d1 <zwp_input_panel_v1_interface+0xd5d1>
    79ce: e8 ed b8 ff ff               	callq	0x32c0 <__assert_fail@plt>
    79d3: e8 08 1d 00 00               	callq	0x96e0 <ivi_layout_transition_visibility_off>
    79d8: e9 91 fc ff ff               	jmp	0x766e <ivi_layout_commit_changes+0xc2e>
    79dd: e8 fe 1c 00 00               	callq	0x96e0 <ivi_layout_transition_visibility_off>
    79e2: e9 de fd ff ff               	jmp	0x77c5 <ivi_layout_commit_changes+0xd85>
    79e7: 48 8b 35 22 99 20 00         	movq	0x209922(%rip), %rsi    # 0x211310 <ivilayout+0x10>
    79ee: 48 8d 05 13 99 20 00         	leaq	0x209913(%rip), %rax    # 0x211308 <ivilayout+0x8>
    79f5: 48 39 c6                     	cmpq	%rax, %rsi
    79f8: 0f 84 d1 f1 ff ff            	je	0x6bcf <ivi_layout_commit_changes+0x18f>
    79fe: 8b 4d 24                     	movl	0x24(%rbp), %ecx
    7a01: ba d3 4d 62 10               	movl	$0x10624dd3, %edx       # imm = 0x10624DD3
    7a06: 41 b8 d3 4d 62 10            	movl	$0x10624dd3, %r8d       # imm = 0x10624DD3
    7a0c: 4c 8b 4d 38                  	movq	0x38(%rbp), %r9
    7a10: 89 c8                        	movl	%ecx, %eax
    7a12: c1 f9 1f                     	sarl	$0x1f, %ecx
    7a15: f7 ea                        	imull	%edx
    7a17: c1 fa 06                     	sarl	$0x6, %edx
    7a1a: 29 ca                        	subl	%ecx, %edx
    7a1c: 89 d1                        	movl	%edx, %ecx
    7a1e: eb 14                        	jmp	0x7a34 <ivi_layout_commit_changes+0xff4>
    7a20: 48 8b 76 08                  	movq	0x8(%rsi), %rsi
    7a24: 48 8d 05 dd 98 20 00         	leaq	0x2098dd(%rip), %rax    # 0x211308 <ivilayout+0x8>
    7a2b: 48 39 c6                     	cmpq	%rax, %rsi
    7a2e: 0f 84 9b f1 ff ff            	je	0x6bcf <ivi_layout_commit_changes+0x18f>
    7a34: 4c 39 4e 38                  	cmpq	%r9, 0x38(%rsi)
    7a38: 75 e6                        	jne	0x7a20 <ivi_layout_commit_changes+0xfe0>
    7a3a: 48 39 f5                     	cmpq	%rsi, %rbp
    7a3d: 74 e1                        	je	0x7a20 <ivi_layout_commit_changes+0xfe0>
    7a3f: 8b 7e 24                     	movl	0x24(%rsi), %edi
    7a42: 89 f8                        	movl	%edi, %eax
    7a44: c1 ff 1f                     	sarl	$0x1f, %edi
    7a47: 41 f7 e8                     	imull	%r8d
    7a4a: 89 d0                        	movl	%edx, %eax
    7a4c: c1 f8 06                     	sarl	$0x6, %eax
    7a4f: 29 f8                        	subl	%edi, %eax
    7a51: 39 c8                        	cmpl	%ecx, %eax
    7a53: 75 cb                        	jne	0x7a20 <ivi_layout_commit_changes+0xfe0>
    7a55: 83 f8 04                     	cmpl	$0x4, %eax
    7a58: 75 c6                        	jne	0x7a20 <ivi_layout_commit_changes+0xfe0>
    7a5a: 48 8b 05 1f 99 20 00         	movq	0x20991f(%rip), %rax    # 0x211380 <ivilayout+0x80>
    7a61: 48 8d 0d 10 99 20 00         	leaq	0x209910(%rip), %rcx    # 0x211378 <ivilayout+0x78>
    7a68: c6 85 90 01 00 00 01         	movb	$0x1, 0x190(%rbp)
    7a6f: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    7a73: 48 39 c8                     	cmpq	%rcx, %rax
    7a76: 75 0b                        	jne	0x7a83 <ivi_layout_commit_changes+0x1043>
    7a78: e9 52 f1 ff ff               	jmp	0x6bcf <ivi_layout_commit_changes+0x18f>
    7a7d: 0f 1f 00                     	nopl	(%rax)
    7a80: 48 89 d3                     	movq	%rdx, %rbx
    7a83: 48 89 c7                     	movq	%rax, %rdi
    7a86: 48 89 ee                     	movq	%rbp, %rsi
    7a89: ff 50 10                     	callq	*0x10(%rax)
    7a8c: 48 8d 0d e5 98 20 00         	leaq	0x2098e5(%rip), %rcx    # 0x211378 <ivilayout+0x78>
    7a93: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    7a97: 48 89 d8                     	movq	%rbx, %rax
    7a9a: 48 39 cb                     	cmpq	%rcx, %rbx
    7a9d: 75 e1                        	jne	0x7a80 <ivi_layout_commit_changes+0x1040>
    7a9f: e9 2b f1 ff ff               	jmp	0x6bcf <ivi_layout_commit_changes+0x18f>
    7aa4: 0f 1f 40 00                  	nopl	(%rax)
    7aa8: 48 8d 3d 21 5a 00 00         	leaq	0x5a21(%rip), %rdi      # 0xd4d0 <zwp_input_panel_v1_interface+0xd4d0>
    7aaf: 31 c0                        	xorl	%eax, %eax
    7ab1: e8 5a b7 ff ff               	callq	0x3210 <weston_log@plt>
    7ab6: 45 0f b6 a5 d0 00 00 00      	movzbl	0xd0(%r13), %r12d
    7abe: 45 84 e4                     	testb	%r12b, %r12b
    7ac1: 0f 85 57 03 00 00            	jne	0x7e1e <ivi_layout_commit_changes+0x13de>
    7ac7: 41 c7 85 80 01 00 00 00 00 00 00     	movl	$0x0, 0x180(%r13)
    7ad2: 41 83 45 20 01               	addl	$0x1, 0x20(%r13)
    7ad7: 45 84 e4                     	testb	%r12b, %r12b
    7ada: 0f 84 bb 05 00 00            	je	0x809b <ivi_layout_commit_changes+0x165b>
    7ae0: 48 89 df                     	movq	%rbx, %rdi
    7ae3: e8 48 bb ff ff               	callq	0x3630 <weston_view_geometry_dirty@plt>
    7ae8: 49 8b 7d 38                  	movq	0x38(%r13), %rdi
    7aec: e8 9f b9 ff ff               	callq	0x3490 <weston_surface_damage@plt>
    7af1: 49 8b 85 40 01 00 00         	movq	0x140(%r13), %rax
    7af8: 4c 8d a8 c8 fe ff ff         	leaq	-0x138(%rax), %r13
    7aff: 48 39 44 24 08               	cmpq	%rax, 0x8(%rsp)
    7b04: 0f 85 e6 f4 ff ff            	jne	0x6ff0 <ivi_layout_commit_changes+0x5b0>
    7b0a: 49 8b 86 20 01 00 00         	movq	0x120(%r14), %rax
    7b11: 4c 8d b0 e8 fe ff ff         	leaq	-0x118(%rax), %r14
    7b18: 48 39 44 24 68               	cmpq	%rax, 0x68(%rsp)
    7b1d: 0f 85 a7 f4 ff ff            	jne	0x6fca <ivi_layout_commit_changes+0x58a>
    7b23: 48 8b 44 24 60               	movq	0x60(%rsp), %rax
    7b28: 48 8b 40 08                  	movq	0x8(%rax), %rax
    7b2c: 48 89 44 24 60               	movq	%rax, 0x60(%rsp)
    7b31: 4c 39 f8                     	cmpq	%r15, %rax
    7b34: 0f 85 6b f4 ff ff            	jne	0x6fa5 <ivi_layout_commit_changes+0x565>
    7b3a: 48 8b 1d d7 97 20 00         	movq	0x2097d7(%rip), %rbx    # 0x211318 <ivilayout+0x18>
    7b41: 48 8d 05 d0 97 20 00         	leaq	0x2097d0(%rip), %rax    # 0x211318 <ivilayout+0x18>
    7b48: 48 39 c3                     	cmpq	%rax, %rbx
    7b4b: 74 54                        	je	0x7ba1 <ivi_layout_commit_changes+0x1161>
    7b4d: 8b 8b 88 00 00 00            	movl	0x88(%rbx), %ecx
    7b53: 85 c9                        	testl	%ecx, %ecx
    7b55: 74 3b                        	je	0x7b92 <ivi_layout_commit_changes+0x1152>
    7b57: 48 8b 43 18                  	movq	0x18(%rbx), %rax
    7b5b: 4c 8d 63 10                  	leaq	0x10(%rbx), %r12
    7b5f: 48 8b 68 08                  	movq	0x8(%rax), %rbp
    7b63: 49 39 c4                     	cmpq	%rax, %r12
    7b66: 75 0b                        	jne	0x7b73 <ivi_layout_commit_changes+0x1133>
    7b68: eb 1e                        	jmp	0x7b88 <ivi_layout_commit_changes+0x1148>
    7b6a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    7b70: 48 89 d5                     	movq	%rdx, %rbp
    7b73: 48 89 c7                     	movq	%rax, %rdi
    7b76: 48 89 de                     	movq	%rbx, %rsi
    7b79: ff 50 10                     	callq	*0x10(%rax)
    7b7c: 48 8b 55 08                  	movq	0x8(%rbp), %rdx
    7b80: 48 89 e8                     	movq	%rbp, %rax
    7b83: 49 39 ec                     	cmpq	%rbp, %r12
    7b86: 75 e8                        	jne	0x7b70 <ivi_layout_commit_changes+0x1130>
    7b88: c7 83 88 00 00 00 00 00 00 00	movl	$0x0, 0x88(%rbx)
    7b92: 48 8b 1b                     	movq	(%rbx), %rbx
    7b95: 48 8d 05 7c 97 20 00         	leaq	0x20977c(%rip), %rax    # 0x211318 <ivilayout+0x18>
    7b9c: 48 39 c3                     	cmpq	%rax, %rbx
    7b9f: 75 ac                        	jne	0x7b4d <ivi_layout_commit_changes+0x110d>
    7ba1: 48 8b 1d 60 97 20 00         	movq	0x209760(%rip), %rbx    # 0x211308 <ivilayout+0x8>
    7ba8: 48 8d 05 59 97 20 00         	leaq	0x209759(%rip), %rax    # 0x211308 <ivilayout+0x8>
    7baf: 48 39 c3                     	cmpq	%rax, %rbx
    7bb2: 74 55                        	je	0x7c09 <ivi_layout_commit_changes+0x11c9>
    7bb4: 8b 93 dc 00 00 00            	movl	0xdc(%rbx), %edx
    7bba: 85 d2                        	testl	%edx, %edx
    7bbc: 74 3c                        	je	0x7bfa <ivi_layout_commit_changes+0x11ba>
    7bbe: 48 8b 43 18                  	movq	0x18(%rbx), %rax
    7bc2: 4c 8d 63 10                  	leaq	0x10(%rbx), %r12
    7bc6: 48 8b 68 08                  	movq	0x8(%rax), %rbp
    7bca: 49 39 c4                     	cmpq	%rax, %r12
    7bcd: 75 0c                        	jne	0x7bdb <ivi_layout_commit_changes+0x119b>
    7bcf: eb 1f                        	jmp	0x7bf0 <ivi_layout_commit_changes+0x11b0>
    7bd1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    7bd8: 48 89 d5                     	movq	%rdx, %rbp
    7bdb: 48 89 c7                     	movq	%rax, %rdi
    7bde: 48 89 de                     	movq	%rbx, %rsi
    7be1: ff 50 10                     	callq	*0x10(%rax)
    7be4: 48 8b 55 08                  	movq	0x8(%rbp), %rdx
    7be8: 48 89 e8                     	movq	%rbp, %rax
    7beb: 49 39 ec                     	cmpq	%rbp, %r12
    7bee: 75 e8                        	jne	0x7bd8 <ivi_layout_commit_changes+0x1198>
    7bf0: c7 83 dc 00 00 00 00 00 00 00	movl	$0x0, 0xdc(%rbx)
    7bfa: 48 8b 1b                     	movq	(%rbx), %rbx
    7bfd: 48 8d 05 04 97 20 00         	leaq	0x209704(%rip), %rax    # 0x211308 <ivilayout+0x8>
    7c04: 48 39 c3                     	cmpq	%rax, %rbx
    7c07: 75 ab                        	jne	0x7bb4 <ivi_layout_commit_changes+0x1174>
    7c09: 48 8b 3d f0 96 20 00         	movq	0x2096f0(%rip), %rdi    # 0x211300 <ivilayout>
    7c10: e8 2b b4 ff ff               	callq	0x3040 <weston_compositor_schedule_repaint@plt>
    7c15: 31 c0                        	xorl	%eax, %eax
    7c17: 48 8b 8c 24 28 01 00 00      	movq	0x128(%rsp), %rcx
    7c1f: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    7c28: 0f 85 68 04 00 00            	jne	0x8096 <ivi_layout_commit_changes+0x1656>
    7c2e: 48 81 c4 38 01 00 00         	addq	$0x138, %rsp            # imm = 0x138
    7c35: 5b                           	popq	%rbx
    7c36: 5d                           	popq	%rbp
    7c37: 41 5c                        	popq	%r12
    7c39: 41 5d                        	popq	%r13
    7c3b: 41 5e                        	popq	%r14
    7c3d: 41 5f                        	popq	%r15
    7c3f: c3                           	retq
    7c40: f3 0f 11 4c 24 1c            	movss	%xmm1, 0x1c(%rsp)
    7c46: f3 0f 11 7c 24 14            	movss	%xmm7, 0x14(%rsp)
    7c4c: e8 9f b9 ff ff               	callq	0x35f0 <floorf@plt>
    7c51: f3 0f 10 6c 24 14            	movss	0x14(%rsp), %xmm5
    7c57: f3 0f 11 44 24 18            	movss	%xmm0, 0x18(%rsp)
    7c5d: 0f 28 c5                     	movaps	%xmm5, %xmm0
    7c60: e8 8b b9 ff ff               	callq	0x35f0 <floorf@plt>
    7c65: f3 0f 10 64 24 1c            	movss	0x1c(%rsp), %xmm4
    7c6b: f3 0f 11 44 24 14            	movss	%xmm0, 0x14(%rsp)
    7c71: 0f 28 c4                     	movaps	%xmm4, %xmm0
    7c74: e8 e7 b6 ff ff               	callq	0x3360 <ceilf@plt>
    7c79: 66 41 0f 7e c4               	movd	%xmm0, %r12d
    7c7e: f3 0f 10 44 24 10            	movss	0x10(%rsp), %xmm0
    7c84: e8 d7 b6 ff ff               	callq	0x3360 <ceilf@plt>
    7c89: f3 0f 10 54 24 14            	movss	0x14(%rsp), %xmm2
    7c8f: 66 41 0f 6e dc               	movd	%r12d, %xmm3
    7c94: f3 0f 10 4c 24 18            	movss	0x18(%rsp), %xmm1
    7c9a: f3 0f 5c da                  	subss	%xmm2, %xmm3
    7c9e: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
    7ca3: f3 0f 5c c1                  	subss	%xmm1, %xmm0
    7ca7: f3 0f 2c d2                  	cvttss2si	%xmm2, %edx
    7cab: f3 0f 2c f1                  	cvttss2si	%xmm1, %esi
    7caf: f3 48 0f 2c c8               	cvttss2si	%xmm0, %rcx
    7cb4: f3 4c 0f 2c c3               	cvttss2si	%xmm3, %r8
    7cb9: e8 b2 b8 ff ff               	callq	0x3570 <pixman_region32_init_rect@plt>
    7cbe: 4c 8b 64 24 48               	movq	0x48(%rsp), %r12
    7cc3: 41 8b 4e 54                  	movl	0x54(%r14), %ecx
    7cc7: 41 8b 56 50                  	movl	0x50(%r14), %edx
    7ccb: 41 8b 76 4c                  	movl	0x4c(%r14), %esi
    7ccf: 45 8b 46 58                  	movl	0x58(%r14), %r8d
    7cd3: 4c 89 e7                     	movq	%r12, %rdi
    7cd6: e8 95 b8 ff ff               	callq	0x3570 <pixman_region32_init_rect@plt>
    7cdb: 48 8b 44 24 58               	movq	0x58(%rsp), %rax
    7ce0: 48 8b 7c 24 28               	movq	0x28(%rsp), %rdi
    7ce5: 8b 88 e8 00 00 00            	movl	0xe8(%rax), %ecx
    7ceb: 8b 90 e4 00 00 00            	movl	0xe4(%rax), %edx
    7cf1: 8b b0 e0 00 00 00            	movl	0xe0(%rax), %esi
    7cf7: 44 8b 80 ec 00 00 00         	movl	0xec(%rax), %r8d
    7cfe: e8 6d b8 ff ff               	callq	0x3570 <pixman_region32_init_rect@plt>
    7d03: 4c 89 e2                     	movq	%r12, %rdx
    7d06: 4c 8b 64 24 40               	movq	0x40(%rsp), %r12
    7d0b: 48 8b 74 24 20               	movq	0x20(%rsp), %rsi
    7d10: 4c 89 e7                     	movq	%r12, %rdi
    7d13: e8 b8 b5 ff ff               	callq	0x32d0 <pixman_region32_intersect@plt>
    7d18: 48 8b 54 24 28               	movq	0x28(%rsp), %rdx
    7d1d: 4c 89 e7                     	movq	%r12, %rdi
    7d20: 4c 89 e6                     	movq	%r12, %rsi
    7d23: e8 a8 b5 ff ff               	callq	0x32d0 <pixman_region32_intersect@plt>
    7d28: 4c 89 e7                     	movq	%r12, %rdi
    7d2b: e8 a0 b4 ff ff               	callq	0x31d0 <pixman_region32_not_empty@plt>
    7d30: 85 c0                        	testl	%eax, %eax
    7d32: 0f 85 d0 01 00 00            	jne	0x7f08 <ivi_layout_commit_changes+0x14c8>
    7d38: 45 31 c0                     	xorl	%r8d, %r8d
    7d3b: 31 c9                        	xorl	%ecx, %ecx
    7d3d: c7 44 24 10 00 00 00 00      	movl	$0x0, 0x10(%rsp)
    7d45: 31 f6                        	xorl	%esi, %esi
    7d47: 41 bc 01 00 00 00            	movl	$0x1, %r12d
    7d4d: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
    7d52: 44 89 44 24 1c               	movl	%r8d, 0x1c(%rsp)
    7d57: 89 4c 24 18                  	movl	%ecx, 0x18(%rsp)
    7d5b: 89 74 24 14                  	movl	%esi, 0x14(%rsp)
    7d5f: e8 ac b3 ff ff               	callq	0x3110 <pixman_region32_fini@plt>
    7d64: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
    7d69: e8 a2 b3 ff ff               	callq	0x3110 <pixman_region32_fini@plt>
    7d6e: 48 8b 7c 24 48               	movq	0x48(%rsp), %rdi
    7d73: e8 98 b3 ff ff               	callq	0x3110 <pixman_region32_fini@plt>
    7d78: 48 8b 7c 24 28               	movq	0x28(%rsp), %rdi
    7d7d: e8 8e b3 ff ff               	callq	0x3110 <pixman_region32_fini@plt>
    7d82: 44 8b 44 24 1c               	movl	0x1c(%rsp), %r8d
    7d87: 48 89 df                     	movq	%rbx, %rdi
    7d8a: 8b 4c 24 18                  	movl	0x18(%rsp), %ecx
    7d8e: 8b 54 24 10                  	movl	0x10(%rsp), %edx
    7d92: 8b 74 24 14                  	movl	0x14(%rsp), %esi
    7d96: e8 45 b8 ff ff               	callq	0x35e0 <weston_view_set_mask@plt>
    7d9b: 48 8b 74 24 50               	movq	0x50(%rsp), %rsi
    7da0: 48 8d bb 90 00 00 00         	leaq	0x90(%rbx), %rdi
    7da7: e8 f4 b8 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    7dac: 31 f6                        	xorl	%esi, %esi
    7dae: 48 89 df                     	movq	%rbx, %rdi
    7db1: e8 ca b5 ff ff               	callq	0x3380 <weston_view_set_transform_parent@plt>
    7db6: 45 84 e4                     	testb	%r12b, %r12b
    7db9: 0f 84 f7 fc ff ff            	je	0x7ab6 <ivi_layout_commit_changes+0x1076>
    7dbf: 41 8b b5 80 01 00 00         	movl	0x180(%r13), %esi
    7dc6: 85 f6                        	testl	%esi, %esi
    7dc8: 75 47                        	jne	0x7e11 <ivi_layout_commit_changes+0x13d1>
    7dca: 41 81 8d dc 00 00 00 80 00 00 00     	orl	$0x80, 0xdc(%r13)
    7dd5: 41 83 45 20 01               	addl	$0x1, 0x20(%r13)
    7dda: 41 c6 85 d0 00 00 00 00      	movb	$0x0, 0xd0(%r13)
    7de2: 41 c7 85 80 01 00 00 01 00 00 00     	movl	$0x1, 0x180(%r13)
    7ded: 48 89 ef                     	movq	%rbp, %rdi
    7df0: e8 2b b3 ff ff               	callq	0x3120 <weston_matrix_init@plt>
    7df5: 48 89 ef                     	movq	%rbp, %rdi
    7df8: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    7dfc: f3 0f 10 0d 38 5a 00 00      	movss	0x5a38(%rip), %xmm1     # 0xd83c <__func__.12894+0x2c>
    7e04: 0f 28 c1                     	movaps	%xmm1, %xmm0
    7e07: e8 a4 b7 ff ff               	callq	0x35b0 <weston_matrix_translate@plt>
    7e0c: e9 cf fc ff ff               	jmp	0x7ae0 <ivi_layout_commit_changes+0x10a0>
    7e11: 41 81 a5 dc 00 00 00 7f ff ff ff     	andl	$0xffffff7f, 0xdc(%r13) # imm = 0xFFFFFF7F
    7e1c: eb b7                        	jmp	0x7dd5 <ivi_layout_commit_changes+0x1395>
    7e1e: 45 8b 85 bc 00 00 00         	movl	0xbc(%r13), %r8d
    7e25: 45 8b 95 c0 00 00 00         	movl	0xc0(%r13), %r10d
    7e2c: 45 03 46 4c                  	addl	0x4c(%r14), %r8d
    7e30: 45 03 56 50                  	addl	0x50(%r14), %r10d
    7e34: 45 8b 9d c4 00 00 00         	movl	0xc4(%r13), %r11d
    7e3b: 41 8b ad c8 00 00 00         	movl	0xc8(%r13), %ebp
    7e42: 48 8b 0d e7 94 20 00         	movq	0x2094e7(%rip), %rcx    # 0x211330 <ivilayout+0x30>
    7e49: 45 01 c3                     	addl	%r8d, %r11d
    7e4c: 44 01 d5                     	addl	%r10d, %ebp
    7e4f: 4c 39 f9                     	cmpq	%r15, %rcx
    7e52: 0f 84 a7 00 00 00            	je	0x7eff <ivi_layout_commit_changes+0x14bf>
    7e58: 48 8b 41 20                  	movq	0x20(%rcx), %rax
    7e5c: 8b b0 e4 00 00 00            	movl	0xe4(%rax), %esi
    7e62: 8b b8 ec 00 00 00            	movl	0xec(%rax), %edi
    7e68: 8b 90 e0 00 00 00            	movl	0xe0(%rax), %edx
    7e6e: 44 8b 88 e8 00 00 00         	movl	0xe8(%rax), %r9d
    7e75: 01 f7                        	addl	%esi, %edi
    7e77: 44 39 d7                     	cmpl	%r10d, %edi
    7e7a: 40 0f 9f c7                  	setg	%dil
    7e7e: 41 01 d1                     	addl	%edx, %r9d
    7e81: 45 39 c1                     	cmpl	%r8d, %r9d
    7e84: 0f 9f c0                     	setg	%al
    7e87: 21 c7                        	andl	%eax, %edi
    7e89: 41 39 d3                     	cmpl	%edx, %r11d
    7e8c: 0f 9f c0                     	setg	%al
    7e8f: 40 84 c7                     	testb	%al, %dil
    7e92: 75 48                        	jne	0x7edc <ivi_layout_commit_changes+0x149c>
    7e94: 0f 1f 40 00                  	nopl	(%rax)
    7e98: 48 8b 49 08                  	movq	0x8(%rcx), %rcx
    7e9c: 4c 39 f9                     	cmpq	%r15, %rcx
    7e9f: 74 5e                        	je	0x7eff <ivi_layout_commit_changes+0x14bf>
    7ea1: 48 8b 41 20                  	movq	0x20(%rcx), %rax
    7ea5: 8b 90 e0 00 00 00            	movl	0xe0(%rax), %edx
    7eab: 8b b8 e8 00 00 00            	movl	0xe8(%rax), %edi
    7eb1: 8b b0 e4 00 00 00            	movl	0xe4(%rax), %esi
    7eb7: 44 8b 88 ec 00 00 00         	movl	0xec(%rax), %r9d
    7ebe: 01 d7                        	addl	%edx, %edi
    7ec0: 41 39 f8                     	cmpl	%edi, %r8d
    7ec3: 40 0f 9c c7                  	setl	%dil
    7ec7: 41 01 f1                     	addl	%esi, %r9d
    7eca: 45 39 ca                     	cmpl	%r9d, %r10d
    7ecd: 0f 9c c0                     	setl	%al
    7ed0: 21 f8                        	andl	%edi, %eax
    7ed2: 41 39 d3                     	cmpl	%edx, %r11d
    7ed5: 0f 9f c2                     	setg	%dl
    7ed8: 84 d0                        	testb	%dl, %al
    7eda: 74 bc                        	je	0x7e98 <ivi_layout_commit_changes+0x1458>
    7edc: 39 f5                        	cmpl	%esi, %ebp
    7ede: 7e b8                        	jle	0x7e98 <ivi_layout_commit_changes+0x1458>
    7ee0: 41 8b 85 80 01 00 00         	movl	0x180(%r13), %eax
    7ee7: 85 c0                        	testl	%eax, %eax
    7ee9: 0f 84 d8 fb ff ff            	je	0x7ac7 <ivi_layout_commit_changes+0x1087>
    7eef: 41 81 8d dc 00 00 00 80 00 00 00     	orl	$0x80, 0xdc(%r13)
    7efa: e9 c8 fb ff ff               	jmp	0x7ac7 <ivi_layout_commit_changes+0x1087>
    7eff: 49 8d 6d 40                  	leaq	0x40(%r13), %rbp
    7f03: e9 b7 fe ff ff               	jmp	0x7dbf <ivi_layout_commit_changes+0x137f>
    7f08: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
    7f0d: e8 7e b3 ff ff               	callq	0x3290 <pixman_region32_extents@plt>
    7f12: 48 8b 7c 24 40               	movq	0x40(%rsp), %rdi
    7f17: 49 89 c4                     	movq	%rax, %r12
    7f1a: e8 71 b3 ff ff               	callq	0x3290 <pixman_region32_extents@plt>
    7f1f: 45 8b 44 24 08               	movl	0x8(%r12), %r8d
    7f24: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    7f28: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    7f2c: 41 8b 14 24                  	movl	(%r12), %edx
    7f30: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    7f34: 45 8b 8d a4 00 00 00         	movl	0xa4(%r13), %r9d
    7f3b: 41 8b 7c 24 0c               	movl	0xc(%r12), %edi
    7f40: 44 89 c1                     	movl	%r8d, %ecx
    7f43: 41 8b 74 24 04               	movl	0x4(%r12), %esi
    7f48: 45 31 e4                     	xorl	%r12d, %r12d
    7f4b: 29 d1                        	subl	%edx, %ecx
    7f4d: 45 8b 95 a8 00 00 00         	movl	0xa8(%r13), %r10d
    7f54: f3 0f 2a c1                  	cvtsi2ss	%ecx, %xmm0
    7f58: 44 2b 40 08                  	subl	0x8(%rax), %r8d
    7f5c: f3 41 0f 2a c9               	cvtsi2ss	%r9d, %xmm1
    7f61: 89 f9                        	movl	%edi, %ecx
    7f63: 2b 78 0c                     	subl	0xc(%rax), %edi
    7f66: 29 f1                        	subl	%esi, %ecx
    7f68: 45 8b 9d a0 00 00 00         	movl	0xa0(%r13), %r11d
    7f6f: f3 0f 2a d1                  	cvtsi2ss	%ecx, %xmm2
    7f73: 8b 08                        	movl	(%rax), %ecx
    7f75: f3 0f 5e c8                  	divss	%xmm0, %xmm1
    7f79: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    7f7d: f3 41 0f 2a c2               	cvtsi2ss	%r10d, %xmm0
    7f82: 29 d1                        	subl	%edx, %ecx
    7f84: 8b 50 04                     	movl	0x4(%rax), %edx
    7f87: 29 f2                        	subl	%esi, %edx
    7f89: 41 8b b5 9c 00 00 00         	movl	0x9c(%r13), %esi
    7f90: f3 0f 5e c2                  	divss	%xmm2, %xmm0
    7f94: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    7f98: f3 0f 2a d1                  	cvtsi2ss	%ecx, %xmm2
    7f9c: f3 0f 59 d1                  	mulss	%xmm1, %xmm2
    7fa0: f3 0f 2c ca                  	cvttss2si	%xmm2, %ecx
    7fa4: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    7fa8: f3 0f 2a d2                  	cvtsi2ss	%edx, %xmm2
    7fac: 41 29 c9                     	subl	%ecx, %r9d
    7faf: 01 ce                        	addl	%ecx, %esi
    7fb1: f3 0f 59 d0                  	mulss	%xmm0, %xmm2
    7fb5: f3 0f 2c d2                  	cvttss2si	%xmm2, %edx
    7fb9: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    7fbd: f3 41 0f 2a d0               	cvtsi2ss	%r8d, %xmm2
    7fc2: 41 01 d3                     	addl	%edx, %r11d
    7fc5: f3 0f 59 ca                  	mulss	%xmm2, %xmm1
    7fc9: 44 89 5c 24 10               	movl	%r11d, 0x10(%rsp)
    7fce: f3 0f 2c c9                  	cvttss2si	%xmm1, %ecx
    7fd2: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    7fd6: f3 0f 2a cf                  	cvtsi2ss	%edi, %xmm1
    7fda: 41 29 c9                     	subl	%ecx, %r9d
    7fdd: f3 0f 59 c1                  	mulss	%xmm1, %xmm0
    7fe1: 44 89 c9                     	movl	%r9d, %ecx
    7fe4: f3 0f 2c c0                  	cvttss2si	%xmm0, %eax
    7fe8: 41 29 c2                     	subl	%eax, %r10d
    7feb: 45 89 d0                     	movl	%r10d, %r8d
    7fee: 41 29 d0                     	subl	%edx, %r8d
    7ff1: e9 57 fd ff ff               	jmp	0x7d4d <ivi_layout_commit_changes+0x130d>
    7ff6: 48 8b 7c 24 20               	movq	0x20(%rsp), %rdi
    7ffb: e8 f0 b1 ff ff               	callq	0x31f0 <pixman_region32_init@plt>
    8000: e9 b9 fc ff ff               	jmp	0x7cbe <ivi_layout_commit_changes+0x127e>
    8005: 41 8b 75 24                  	movl	0x24(%r13), %esi
    8009: 48 8d 3d 48 54 00 00         	leaq	0x5448(%rip), %rdi      # 0xd458 <zwp_input_panel_v1_interface+0xd458>
    8010: 31 c0                        	xorl	%eax, %eax
    8012: e8 f9 b1 ff ff               	callq	0x3210 <weston_log@plt>
    8017: e9 d5 fa ff ff               	jmp	0x7af1 <ivi_layout_commit_changes+0x10b1>
    801c: 48 8b 05 ad 93 20 00         	movq	0x2093ad(%rip), %rax    # 0x2113d0 <ivilayout+0xd0>
    8023: 48 8d 35 ae 93 20 00         	leaq	0x2093ae(%rip), %rsi    # 0x2113d8 <ivilayout+0xd8>
    802a: 48 8d 78 08                  	leaq	0x8(%rax), %rdi
    802e: e8 dd b4 ff ff               	callq	0x3510 <wl_list_insert_list@plt>
    8033: 48 8d 3d 9e 93 20 00         	leaq	0x20939e(%rip), %rdi    # 0x2113d8 <ivilayout+0xd8>
    803a: e8 01 b3 ff ff               	callq	0x3340 <wl_list_init@plt>
    803f: 48 8b 05 8a 93 20 00         	movq	0x20938a(%rip), %rax    # 0x2113d0 <ivilayout+0xd0>
    8046: be 01 00 00 00               	movl	$0x1, %esi
    804b: 48 8b 38                     	movq	(%rax), %rdi
    804e: e8 3d b0 ff ff               	callq	0x3090 <wl_event_source_timer_update@plt>
    8053: e9 14 ef ff ff               	jmp	0x6f6c <ivi_layout_commit_changes+0x52c>
    8058: 48 8d 0d 91 57 00 00         	leaq	0x5791(%rip), %rcx      # 0xd7f0 <__PRETTY_FUNCTION__.13126>
    805f: ba 53 04 00 00               	movl	$0x453, %edx            # imm = 0x453
    8064: 48 8d 35 32 55 00 00         	leaq	0x5532(%rip), %rsi      # 0xd59d <zwp_input_panel_v1_interface+0xd59d>
    806b: 48 8d 3d 86 53 00 00         	leaq	0x5386(%rip), %rdi      # 0xd3f8 <zwp_input_panel_v1_interface+0xd3f8>
    8072: e8 49 b2 ff ff               	callq	0x32c0 <__assert_fail@plt>
    8077: 48 8d 0d 52 57 00 00         	leaq	0x5752(%rip), %rcx      # 0xd7d0 <__PRETTY_FUNCTION__.13149>
    807e: ba 7d 04 00 00               	movl	$0x47d, %edx            # imm = 0x47D
    8083: 48 8d 35 13 55 00 00         	leaq	0x5513(%rip), %rsi      # 0xd59d <zwp_input_panel_v1_interface+0xd59d>
    808a: 48 8d 3d 97 53 00 00         	leaq	0x5397(%rip), %rdi      # 0xd428 <zwp_input_panel_v1_interface+0xd428>
    8091: e8 2a b2 ff ff               	callq	0x32c0 <__assert_fail@plt>
    8096: e8 85 b1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    809b: 49 8d 6d 40                  	leaq	0x40(%r13), %rbp
    809f: e9 49 fd ff ff               	jmp	0x7ded <ivi_layout_commit_changes+0x13ad>
    80a4: 48 8d 0d 15 57 00 00         	leaq	0x5715(%rip), %rcx      # 0xd7c0 <__PRETTY_FUNCTION__.12921>
    80ab: ba 4c 01 00 00               	movl	$0x14c, %edx            # imm = 0x14C
    80b0: 48 8d 35 e6 54 00 00         	leaq	0x54e6(%rip), %rsi      # 0xd59d <zwp_input_panel_v1_interface+0xd59d>
    80b7: 48 8d 3d 13 55 00 00         	leaq	0x5513(%rip), %rdi      # 0xd5d1 <zwp_input_panel_v1_interface+0xd5d1>
    80be: e8 fd b1 ff ff               	callq	0x32c0 <__assert_fail@plt>
    80c3: 0f 1f 00                     	nopl	(%rax)
    80c6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000080d0 <get_instance>:
    80d0: 48 83 ec 18                  	subq	$0x18, %rsp
    80d4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    80dd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    80e2: 31 c0                        	xorl	%eax, %eax
    80e4: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    80e9: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    80f2: 75 0c                        	jne	0x8100 <get_instance+0x30>
    80f4: 48 8d 05 05 92 20 00         	leaq	0x209205(%rip), %rax    # 0x211300 <ivilayout>
    80fb: 48 83 c4 18                  	addq	$0x18, %rsp
    80ff: c3                           	retq
    8100: e8 1b b1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8105: 90                           	nop
    8106: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000008110 <ivi_layout_get_weston_view>:
    8110: 53                           	pushq	%rbx
    8111: 48 83 ec 10                  	subq	$0x10, %rsp
    8115: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    811e: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8123: 31 c0                        	xorl	%eax, %eax
    8125: 48 85 ff                     	testq	%rdi, %rdi
    8128: 74 46                        	je	0x8170 <ivi_layout_get_weston_view+0x60>
    812a: 48 89 fb                     	movq	%rdi, %rbx
    812d: 48 8b 7f 38                  	movq	0x38(%rdi), %rdi
    8131: 48 85 ff                     	testq	%rdi, %rdi
    8134: 74 3e                        	je	0x8174 <ivi_layout_get_weston_view+0x64>
    8136: 48 83 ef 80                  	subq	$-0x80, %rdi
    813a: e8 b1 b2 ff ff               	callq	0x33f0 <wl_list_empty@plt>
    813f: 85 c0                        	testl	%eax, %eax
    8141: 75 2d                        	jne	0x8170 <ivi_layout_get_weston_view+0x60>
    8143: 48 8b 43 38                  	movq	0x38(%rbx), %rax
    8147: 48 8b 80 88 00 00 00         	movq	0x88(%rax), %rax
    814e: 48 83 e8 08                  	subq	$0x8, %rax
    8152: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    8157: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    8160: 75 31                        	jne	0x8193 <ivi_layout_get_weston_view+0x83>
    8162: 48 83 c4 10                  	addq	$0x10, %rsp
    8166: 5b                           	popq	%rbx
    8167: c3                           	retq
    8168: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    8170: 31 c0                        	xorl	%eax, %eax
    8172: eb de                        	jmp	0x8152 <ivi_layout_get_weston_view+0x42>
    8174: 48 8d 0d 35 56 00 00         	leaq	0x5635(%rip), %rcx      # 0xd7b0 <__PRETTY_FUNCTION__.12862>
    817b: ba 9f 00 00 00               	movl	$0x9f, %edx
    8180: 48 8d 35 16 54 00 00         	leaq	0x5416(%rip), %rsi      # 0xd59d <zwp_input_panel_v1_interface+0xd59d>
    8187: 48 8d 3d 53 54 00 00         	leaq	0x5453(%rip), %rdi      # 0xd5e1 <zwp_input_panel_v1_interface+0xd5e1>
    818e: e8 2d b1 ff ff               	callq	0x32c0 <__assert_fail@plt>
    8193: e8 88 b0 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8198: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

00000000000081a0 <ivi_layout_surface_configure>:
    81a0: 41 54                        	pushq	%r12
    81a2: 49 89 fc                     	movq	%rdi, %r12
    81a5: 55                           	pushq	%rbp
    81a6: 48 8d 2d cb 91 20 00         	leaq	0x2091cb(%rip), %rbp    # 0x211378 <ivilayout+0x78>
    81ad: 53                           	pushq	%rbx
    81ae: 48 83 ec 10                  	subq	$0x10, %rsp
    81b2: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    81bb: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    81c0: 31 c0                        	xorl	%eax, %eax
    81c2: 48 8b 05 b7 91 20 00         	movq	0x2091b7(%rip), %rax    # 0x211380 <ivilayout+0x80>
    81c9: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    81cd: 48 39 e8                     	cmpq	%rbp, %rax
    81d0: 75 09                        	jne	0x81db <ivi_layout_surface_configure+0x3b>
    81d2: eb 1c                        	jmp	0x81f0 <ivi_layout_surface_configure+0x50>
    81d4: 0f 1f 40 00                  	nopl	(%rax)
    81d8: 48 89 d3                     	movq	%rdx, %rbx
    81db: 48 89 c7                     	movq	%rax, %rdi
    81de: 4c 89 e6                     	movq	%r12, %rsi
    81e1: ff 50 10                     	callq	*0x10(%rax)
    81e4: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    81e8: 48 89 d8                     	movq	%rbx, %rax
    81eb: 48 39 eb                     	cmpq	%rbp, %rbx
    81ee: 75 e8                        	jne	0x81d8 <ivi_layout_surface_configure+0x38>
    81f0: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    81f5: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    81fe: 75 09                        	jne	0x8209 <ivi_layout_surface_configure+0x69>
    8200: 48 83 c4 10                  	addq	$0x10, %rsp
    8204: 5b                           	popq	%rbx
    8205: 5d                           	popq	%rbp
    8206: 41 5c                        	popq	%r12
    8208: c3                           	retq
    8209: e8 12 b0 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    820e: 66 90                        	nop

0000000000008210 <ivi_layout_init_with_compositor>:
    8210: 41 56                        	pushq	%r14
    8212: 49 89 fe                     	movq	%rdi, %r14
    8215: 41 55                        	pushq	%r13
    8217: 4d 8d ae e8 01 00 00         	leaq	0x1e8(%r14), %r13
    821e: 41 54                        	pushq	%r12
    8220: 45 31 e4                     	xorl	%r12d, %r12d
    8223: 55                           	pushq	%rbp
    8224: 53                           	pushq	%rbx
    8225: 48 83 ec 10                  	subq	$0x10, %rsp
    8229: 48 89 3d d0 90 20 00         	movq	%rdi, 0x2090d0(%rip)    # 0x211300 <ivilayout>
    8230: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8239: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    823e: 31 c0                        	xorl	%eax, %eax
    8240: 48 8d 3d c1 90 20 00         	leaq	0x2090c1(%rip), %rdi    # 0x211308 <ivilayout+0x8>
    8247: e8 f4 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    824c: 48 8d 3d c5 90 20 00         	leaq	0x2090c5(%rip), %rdi    # 0x211318 <ivilayout+0x18>
    8253: e8 e8 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    8258: 48 8d 3d c9 90 20 00         	leaq	0x2090c9(%rip), %rdi    # 0x211328 <ivilayout+0x28>
    825f: e8 dc b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    8264: 48 8d 3d cd 90 20 00         	leaq	0x2090cd(%rip), %rdi    # 0x211338 <ivilayout+0x38>
    826b: e8 d0 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    8270: 48 8d 3d d1 90 20 00         	leaq	0x2090d1(%rip), %rdi    # 0x211348 <ivilayout+0x48>
    8277: e8 c4 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    827c: 48 8d 3d d5 90 20 00         	leaq	0x2090d5(%rip), %rdi    # 0x211358 <ivilayout+0x58>
    8283: e8 b8 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    8288: 48 8d 3d d9 90 20 00         	leaq	0x2090d9(%rip), %rdi    # 0x211368 <ivilayout+0x68>
    828f: e8 ac b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    8294: 48 8d 3d dd 90 20 00         	leaq	0x2090dd(%rip), %rdi    # 0x211378 <ivilayout+0x78>
    829b: e8 a0 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    82a0: 49 8b b6 08 02 00 00         	movq	0x208(%r14), %rsi
    82a7: 48 8d 3d da 90 20 00         	leaq	0x2090da(%rip), %rdi    # 0x211388 <ivilayout+0x88>
    82ae: e8 4d ae ff ff               	callq	0x3100 <weston_layer_init@plt>
    82b3: 49 8b 86 f0 01 00 00         	movq	0x1f0(%r14), %rax
    82ba: 48 8d 68 e8                  	leaq	-0x18(%rax), %rbp
    82be: 49 39 c5                     	cmpq	%rax, %r13
    82c1: 75 64                        	jne	0x8327 <ivi_layout_init_with_compositor+0x117>
    82c3: e9 98 00 00 00               	jmp	0x8360 <ivi_layout_init_with_compositor+0x150>
    82c8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    82d0: 48 8d 05 29 90 20 00         	leaq	0x209029(%rip), %rax    # 0x211300 <ivilayout>
    82d7: 44 89 63 10                  	movl	%r12d, 0x10(%rbx)
    82db: 41 83 c4 01                  	addl	$0x1, %r12d
    82df: 48 8d 7b 28                  	leaq	0x28(%rbx), %rdi
    82e3: 48 89 43 18                  	movq	%rax, 0x18(%rbx)
    82e7: 48 89 6b 20                  	movq	%rbp, 0x20(%rbx)
    82eb: e8 50 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    82f0: 48 8d 7b 38                  	leaq	0x38(%rbx), %rdi
    82f4: e8 47 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    82f9: 48 8d 7b 50                  	leaq	0x50(%rbx), %rdi
    82fd: e8 3e b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    8302: 48 8d 7b 60                  	leaq	0x60(%rbx), %rdi
    8306: e8 35 b0 ff ff               	callq	0x3340 <wl_list_init@plt>
    830b: 48 8b 3d 16 90 20 00         	movq	0x209016(%rip), %rdi    # 0x211328 <ivilayout+0x28>
    8312: 48 89 de                     	movq	%rbx, %rsi
    8315: e8 86 b3 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    831a: 48 8b 45 20                  	movq	0x20(%rbp), %rax
    831e: 48 8d 68 e8                  	leaq	-0x18(%rax), %rbp
    8322: 49 39 c5                     	cmpq	%rax, %r13
    8325: 74 39                        	je	0x8360 <ivi_layout_init_with_compositor+0x150>
    8327: be 70 00 00 00               	movl	$0x70, %esi
    832c: bf 01 00 00 00               	movl	$0x1, %edi
    8331: e8 3a b0 ff ff               	callq	0x3370 <calloc@plt>
    8336: 48 89 c3                     	movq	%rax, %rbx
    8339: 48 85 c0                     	testq	%rax, %rax
    833c: 75 92                        	jne	0x82d0 <ivi_layout_init_with_compositor+0xc0>
    833e: 48 8d 3d 3e 52 00 00         	leaq	0x523e(%rip), %rdi      # 0xd583 <zwp_input_panel_v1_interface+0xd583>
    8345: 31 c0                        	xorl	%eax, %eax
    8347: e8 c4 ae ff ff               	callq	0x3210 <weston_log@plt>
    834c: 48 8b 45 20                  	movq	0x20(%rbp), %rax
    8350: 48 8d 68 e8                  	leaq	-0x18(%rax), %rbp
    8354: 49 39 c5                     	cmpq	%rax, %r13
    8357: 75 ce                        	jne	0x8327 <ivi_layout_init_with_compositor+0x117>
    8359: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    8360: 4c 89 f7                     	movq	%r14, %rdi
    8363: e8 88 0f 00 00               	callq	0x92f0 <ivi_layout_transition_set_create>
    8368: 48 89 05 61 90 20 00         	movq	%rax, 0x209061(%rip)    # 0x2113d0 <ivilayout+0xd0>
    836f: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    8374: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    837d: 75 18                        	jne	0x8397 <ivi_layout_init_with_compositor+0x187>
    837f: 48 8d 3d 52 90 20 00         	leaq	0x209052(%rip), %rdi    # 0x2113d8 <ivilayout+0xd8>
    8386: 48 83 c4 10                  	addq	$0x10, %rsp
    838a: 5b                           	popq	%rbx
    838b: 5d                           	popq	%rbp
    838c: 41 5c                        	popq	%r12
    838e: 41 5d                        	popq	%r13
    8390: 41 5e                        	popq	%r14
    8392: e9 a9 af ff ff               	jmp	0x3340 <wl_list_init@plt>
    8397: e8 84 ae ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    839c: 0f 1f 40 00                  	nopl	(%rax)

00000000000083a0 <ivi_layout_surface_add_configured_listener>:
    83a0: 48 83 ec 18                  	subq	$0x18, %rsp
    83a4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    83ad: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    83b2: 31 c0                        	xorl	%eax, %eax
    83b4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    83b9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    83c2: 75 10                        	jne	0x83d4 <ivi_layout_surface_add_configured_listener+0x34>
    83c4: 48 8b bf 68 01 00 00         	movq	0x168(%rdi), %rdi
    83cb: 48 83 c4 18                  	addq	$0x18, %rsp
    83cf: e9 cc b2 ff ff               	jmp	0x36a0 <wl_list_insert@plt>
    83d4: e8 47 ae ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    83d9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

00000000000083e0 <load_controller_modules>:
    83e0: 41 57                        	pushq	%r15
    83e2: 41 56                        	pushq	%r14
    83e4: 41 55                        	pushq	%r13
    83e6: 41 54                        	pushq	%r12
    83e8: 55                           	pushq	%rbp
    83e9: 53                           	pushq	%rbx
    83ea: 48 81 ec 18 01 00 00         	subq	$0x118, %rsp            # imm = 0x118
    83f1: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    83fa: 48 89 84 24 08 01 00 00      	movq	%rax, 0x108(%rsp)
    8402: 31 c0                        	xorl	%eax, %eax
    8404: 48 85 f6                     	testq	%rsi, %rsi
    8407: 0f 84 b6 00 00 00            	je	0x84c3 <load_controller_modules+0xe3>
    840d: 0f b6 06                     	movzbl	(%rsi), %eax
    8410: 49 89 fc                     	movq	%rdi, %r12
    8413: 48 89 f3                     	movq	%rsi, %rbx
    8416: 49 89 d5                     	movq	%rdx, %r13
    8419: 49 89 ce                     	movq	%rcx, %r14
    841c: 48 89 e5                     	movq	%rsp, %rbp
    841f: 84 c0                        	testb	%al, %al
    8421: 0f 84 9c 00 00 00            	je	0x84c3 <load_controller_modules+0xe3>
    8427: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    8430: be 2c 00 00 00               	movl	$0x2c, %esi
    8435: 48 89 df                     	movq	%rbx, %rdi
    8438: e8 13 ad ff ff               	callq	0x3150 <strchrnul@plt>
    843d: 48 83 ec 08                  	subq	$0x8, %rsp
    8441: 48 89 ef                     	movq	%rbp, %rdi
    8444: b9 00 01 00 00               	movl	$0x100, %ecx            # imm = 0x100
    8449: 41 89 c1                     	movl	%eax, %r9d
    844c: 53                           	pushq	%rbx
    844d: ba 01 00 00 00               	movl	$0x1, %edx
    8452: be 00 01 00 00               	movl	$0x100, %esi            # imm = 0x100
    8457: 4c 8d 05 9c 51 00 00         	leaq	0x519c(%rip), %r8       # 0xd5fa <zwp_input_panel_v1_interface+0xd5fa>
    845e: 41 29 d9                     	subl	%ebx, %r9d
    8461: 49 89 c7                     	movq	%rax, %r15
    8464: 31 c0                        	xorl	%eax, %eax
    8466: e8 f5 ab ff ff               	callq	0x3060 <__snprintf_chk@plt>
    846b: 48 8d 35 8d 51 00 00         	leaq	0x518d(%rip), %rsi      # 0xd5ff <zwp_input_panel_v1_interface+0xd5ff>
    8472: 48 89 ef                     	movq	%rbp, %rdi
    8475: e8 b6 ac ff ff               	callq	0x3130 <weston_load_module@plt>
    847a: 5a                           	popq	%rdx
    847b: 59                           	popq	%rcx
    847c: 48 85 c0                     	testq	%rax, %rax
    847f: 74 69                        	je	0x84ea <load_controller_modules+0x10a>
    8481: 41 b8 78 02 00 00            	movl	$0x278, %r8d            # imm = 0x278
    8487: 4c 89 f2                     	movq	%r14, %rdx
    848a: 48 8d 0d 8f 8b 20 00         	leaq	0x208b8f(%rip), %rcx    # 0x211020 <ivi_layout_interface>
    8491: 4c 89 ee                     	movq	%r13, %rsi
    8494: 4c 89 e7                     	movq	%r12, %rdi
    8497: ff d0                        	callq	*%rax
    8499: 85 c0                        	testl	%eax, %eax
    849b: 75 54                        	jne	0x84f1 <load_controller_modules+0x111>
    849d: 41 0f b6 07                  	movzbl	(%r15), %eax
    84a1: 4c 89 fb                     	movq	%r15, %rbx
    84a4: 3c 2c                        	cmpb	$0x2c, %al
    84a6: 0f 85 73 ff ff ff            	jne	0x841f <load_controller_modules+0x3f>
    84ac: 0f 1f 40 00                  	nopl	(%rax)
    84b0: 48 83 c3 01                  	addq	$0x1, %rbx
    84b4: 0f b6 03                     	movzbl	(%rbx), %eax
    84b7: 3c 2c                        	cmpb	$0x2c, %al
    84b9: 74 f5                        	je	0x84b0 <load_controller_modules+0xd0>
    84bb: 84 c0                        	testb	%al, %al
    84bd: 0f 85 6d ff ff ff            	jne	0x8430 <load_controller_modules+0x50>
    84c3: 31 c0                        	xorl	%eax, %eax
    84c5: 48 8b 94 24 08 01 00 00      	movq	0x108(%rsp), %rdx
    84cd: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    84d6: 75 2e                        	jne	0x8506 <load_controller_modules+0x126>
    84d8: 48 81 c4 18 01 00 00         	addq	$0x118, %rsp            # imm = 0x118
    84df: 5b                           	popq	%rbx
    84e0: 5d                           	popq	%rbp
    84e1: 41 5c                        	popq	%r12
    84e3: 41 5d                        	popq	%r13
    84e5: 41 5e                        	popq	%r14
    84e7: 41 5f                        	popq	%r15
    84e9: c3                           	retq
    84ea: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    84ef: eb d4                        	jmp	0x84c5 <load_controller_modules+0xe5>
    84f1: 48 8d 3d 40 50 00 00         	leaq	0x5040(%rip), %rdi      # 0xd538 <zwp_input_panel_v1_interface+0xd538>
    84f8: 31 c0                        	xorl	%eax, %eax
    84fa: e8 11 ad ff ff               	callq	0x3210 <weston_log@plt>
    84ff: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    8504: eb bf                        	jmp	0x84c5 <load_controller_modules+0xe5>
    8506: e8 15 ad ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    850b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

0000000000008510 <is_transition_move_resize_view_func>:
    8510: 48 83 ec 18                  	subq	$0x18, %rsp
    8514: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    851d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8522: 31 c0                        	xorl	%eax, %eax
    8524: 48 39 37                     	cmpq	%rsi, (%rdi)
    8527: 0f 94 c0                     	sete	%al
    852a: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    852f: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    8538: 75 08                        	jne	0x8542 <is_transition_move_resize_view_func+0x32>
    853a: 0f b6 c0                     	movzbl	%al, %eax
    853d: 48 83 c4 18                  	addq	$0x18, %rsp
    8541: c3                           	retq
    8542: e8 d9 ac ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8547: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000008550 <is_transition_fade_view_func>:
    8550: 48 83 ec 18                  	subq	$0x18, %rsp
    8554: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    855d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8562: 31 c0                        	xorl	%eax, %eax
    8564: 48 39 37                     	cmpq	%rsi, (%rdi)
    8567: 0f 94 c0                     	sete	%al
    856a: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    856f: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    8578: 75 08                        	jne	0x8582 <is_transition_fade_view_func+0x32>
    857a: 0f b6 c0                     	movzbl	%al, %eax
    857d: 48 83 c4 18                  	addq	$0x18, %rsp
    8581: c3                           	retq
    8582: e8 99 ac ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8587: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000008590 <is_transition_move_layer_func>:
    8590: 48 83 ec 18                  	subq	$0x18, %rsp
    8594: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    859d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    85a2: 31 c0                        	xorl	%eax, %eax
    85a4: 48 39 37                     	cmpq	%rsi, (%rdi)
    85a7: 0f 94 c0                     	sete	%al
    85aa: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    85af: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    85b8: 75 08                        	jne	0x85c2 <is_transition_move_layer_func+0x32>
    85ba: 0f b6 c0                     	movzbl	%al, %eax
    85bd: 48 83 c4 18                  	addq	$0x18, %rsp
    85c1: c3                           	retq
    85c2: e8 59 ac ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    85c7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

00000000000085d0 <is_transition_fade_layer_func>:
    85d0: 48 83 ec 18                  	subq	$0x18, %rsp
    85d4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    85dd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    85e2: 31 c0                        	xorl	%eax, %eax
    85e4: 48 39 37                     	cmpq	%rsi, (%rdi)
    85e7: 0f 94 c0                     	sete	%al
    85ea: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    85ef: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    85f8: 75 08                        	jne	0x8602 <is_transition_fade_layer_func+0x32>
    85fa: 0f b6 c0                     	movzbl	%al, %eax
    85fd: 48 83 c4 18                  	addq	$0x18, %rsp
    8601: c3                           	retq
    8602: e8 19 ac ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8607: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000008610 <get_transition_from_type_and_id>:
    8610: 41 56                        	pushq	%r14
    8612: 49 89 f6                     	movq	%rsi, %r14
    8615: 41 55                        	pushq	%r13
    8617: 41 89 fd                     	movl	%edi, %r13d
    861a: 41 54                        	pushq	%r12
    861c: 55                           	pushq	%rbp
    861d: 53                           	pushq	%rbx
    861e: 48 83 ec 10                  	subq	$0x10, %rsp
    8622: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    862b: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8630: 31 c0                        	xorl	%eax, %eax
    8632: e8 99 fa ff ff               	callq	0x80d0 <get_instance>
    8637: 49 89 c4                     	movq	%rax, %r12
    863a: 48 8b 80 d0 00 00 00         	movq	0xd0(%rax), %rax
    8641: 48 8b 50 10                  	movq	0x10(%rax), %rdx
    8645: 48 8d 5a f8                  	leaq	-0x8(%rdx), %rbx
    8649: 48 39 d8                     	cmpq	%rbx, %rax
    864c: 75 14                        	jne	0x8662 <get_transition_from_type_and_id+0x52>
    864e: eb 30                        	jmp	0x8680 <get_transition_from_type_and_id+0x70>
    8650: 48 8b 5b 10                  	movq	0x10(%rbx), %rbx
    8654: 48 83 eb 08                  	subq	$0x8, %rbx
    8658: 49 39 9c 24 d0 00 00 00      	cmpq	%rbx, 0xd0(%r12)
    8660: 74 1e                        	je	0x8680 <get_transition_from_type_and_id+0x70>
    8662: 48 8b 2b                     	movq	(%rbx), %rbp
    8665: 44 39 6d 00                  	cmpl	%r13d, (%rbp)
    8669: 75 e5                        	jne	0x8650 <get_transition_from_type_and_id+0x40>
    866b: 48 8b 7d 08                  	movq	0x8(%rbp), %rdi
    866f: 4c 89 f6                     	movq	%r14, %rsi
    8672: ff 55 28                     	callq	*0x28(%rbp)
    8675: 85 c0                        	testl	%eax, %eax
    8677: 74 d7                        	je	0x8650 <get_transition_from_type_and_id+0x40>
    8679: 48 89 e8                     	movq	%rbp, %rax
    867c: eb 04                        	jmp	0x8682 <get_transition_from_type_and_id+0x72>
    867e: 66 90                        	nop
    8680: 31 c0                        	xorl	%eax, %eax
    8682: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    8687: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    8690: 75 0d                        	jne	0x869f <get_transition_from_type_and_id+0x8f>
    8692: 48 83 c4 10                  	addq	$0x10, %rsp
    8696: 5b                           	popq	%rbx
    8697: 5d                           	popq	%rbp
    8698: 41 5c                        	popq	%r12
    869a: 41 5d                        	popq	%r13
    869c: 41 5e                        	popq	%r14
    869e: c3                           	retq
    869f: e8 7c ab ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    86a4: 66 90                        	nop
    86a6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000086b0 <transition_move_resize_view_destroy>:
    86b0: 53                           	pushq	%rbx
    86b1: 48 89 fb                     	movq	%rdi, %rbx
    86b4: 48 83 ec 10                  	subq	$0x10, %rsp
    86b8: 48 8b 7f 08                  	movq	0x8(%rdi), %rdi
    86bc: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    86c5: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    86ca: 31 c0                        	xorl	%eax, %eax
    86cc: 48 85 ff                     	testq	%rdi, %rdi
    86cf: 74 0d                        	je	0x86de <transition_move_resize_view_destroy+0x2e>
    86d1: e8 9a a9 ff ff               	callq	0x3070 <free@plt>
    86d6: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
    86de: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    86e3: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    86ec: 75 06                        	jne	0x86f4 <transition_move_resize_view_destroy+0x44>
    86ee: 48 83 c4 10                  	addq	$0x10, %rsp
    86f2: 5b                           	popq	%rbx
    86f3: c3                           	retq
    86f4: e8 27 ab ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    86f9: 0f 1f 80 00 00 00 00         	nopl	(%rax)

0000000000008700 <transition_move_layer_destroy>:
    8700: 55                           	pushq	%rbp
    8701: 53                           	pushq	%rbx
    8702: 48 89 fb                     	movq	%rdi, %rbx
    8705: 48 83 ec 18                  	subq	$0x18, %rsp
    8709: 48 8b 6f 08                  	movq	0x8(%rdi), %rbp
    870d: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8716: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    871b: 31 c0                        	xorl	%eax, %eax
    871d: 48 8b 45 18                  	movq	0x18(%rbp), %rax
    8721: 48 85 c0                     	testq	%rax, %rax
    8724: 74 06                        	je	0x872c <transition_move_layer_destroy+0x2c>
    8726: 48 8b 7f 10                  	movq	0x10(%rdi), %rdi
    872a: ff d0                        	callq	*%rax
    872c: 48 89 ef                     	movq	%rbp, %rdi
    872f: e8 3c a9 ff ff               	callq	0x3070 <free@plt>
    8734: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
    873c: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    8741: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    874a: 75 07                        	jne	0x8753 <transition_move_layer_destroy+0x53>
    874c: 48 83 c4 18                  	addq	$0x18, %rsp
    8750: 5b                           	popq	%rbx
    8751: 5d                           	popq	%rbp
    8752: c3                           	retq
    8753: e8 c8 aa ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8758: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

0000000000008760 <transition_fade_layer_destroy>:
    8760: 48 83 ec 18                  	subq	$0x18, %rsp
    8764: 48 89 f8                     	movq	%rdi, %rax
    8767: 48 8b 7f 08                  	movq	0x8(%rdi), %rdi
    876b: 64 48 8b 14 25 28 00 00 00   	movq	%fs:0x28, %rdx
    8774: 48 89 54 24 08               	movq	%rdx, 0x8(%rsp)
    8779: 31 d2                        	xorl	%edx, %edx
    877b: 48 c7 40 08 00 00 00 00      	movq	$0x0, 0x8(%rax)
    8783: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    8788: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    8791: 75 09                        	jne	0x879c <transition_fade_layer_destroy+0x3c>
    8793: 48 83 c4 18                  	addq	$0x18, %rsp
    8797: e9 d4 a8 ff ff               	jmp	0x3070 <free@plt>
    879c: e8 7f aa ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    87a1: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    87a6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000087b0 <layout_transition_destroy>:
    87b0: 55                           	pushq	%rbp
    87b1: 48 89 fd                     	movq	%rdi, %rbp
    87b4: 53                           	pushq	%rbx
    87b5: 48 83 ec 18                  	subq	$0x18, %rsp
    87b9: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    87c2: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    87c7: 31 c0                        	xorl	%eax, %eax
    87c9: e8 02 f9 ff ff               	callq	0x80d0 <get_instance>
    87ce: 48 8b 88 d0 00 00 00         	movq	0xd0(%rax), %rcx
    87d5: 48 8b 51 10                  	movq	0x10(%rcx), %rdx
    87d9: 48 8d 72 f8                  	leaq	-0x8(%rdx), %rsi
    87dd: 48 8b 7a 08                  	movq	0x8(%rdx), %rdi
    87e1: 48 39 f1                     	cmpq	%rsi, %rcx
    87e4: 74 2b                        	je	0x8811 <layout_transition_destroy+0x61>
    87e6: 48 8d 5f f8                  	leaq	-0x8(%rdi), %rbx
    87ea: 48 3b 6a f8                  	cmpq	-0x8(%rdx), %rbp
    87ee: 75 14                        	jne	0x8804 <layout_transition_destroy+0x54>
    87f0: e9 90 00 00 00               	jmp	0x8885 <layout_transition_destroy+0xd5>
    87f5: 0f 1f 00                     	nopl	(%rax)
    87f8: 48 3b 2b                     	cmpq	(%rbx), %rbp
    87fb: 0f 84 8f 00 00 00            	je	0x8890 <layout_transition_destroy+0xe0>
    8801: 48 89 d3                     	movq	%rdx, %rbx
    8804: 48 8b 73 10                  	movq	0x10(%rbx), %rsi
    8808: 48 8d 56 f8                  	leaq	-0x8(%rsi), %rdx
    880c: 48 39 d9                     	cmpq	%rbx, %rcx
    880f: 75 e7                        	jne	0x87f8 <layout_transition_destroy+0x48>
    8811: 48 8b b8 e0 00 00 00         	movq	0xe0(%rax), %rdi
    8818: 48 05 d8 00 00 00            	addq	$0xd8, %rax
    881e: 48 8b 77 08                  	movq	0x8(%rdi), %rsi
    8822: 48 8d 57 f8                  	leaq	-0x8(%rdi), %rdx
    8826: 48 8d 5e f8                  	leaq	-0x8(%rsi), %rbx
    882a: 48 39 c7                     	cmpq	%rax, %rdi
    882d: 74 2a                        	je	0x8859 <layout_transition_destroy+0xa9>
    882f: 48 3b 6f f8                  	cmpq	-0x8(%rdi), %rbp
    8833: 75 13                        	jne	0x8848 <layout_transition_destroy+0x98>
    8835: eb 6c                        	jmp	0x88a3 <layout_transition_destroy+0xf3>
    8837: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    8840: 48 3b 2b                     	cmpq	(%rbx), %rbp
    8843: 74 6b                        	je	0x88b0 <layout_transition_destroy+0x100>
    8845: 48 89 d3                     	movq	%rdx, %rbx
    8848: 48 8b 4b 10                  	movq	0x10(%rbx), %rcx
    884c: 48 8d 7b 08                  	leaq	0x8(%rbx), %rdi
    8850: 48 8d 51 f8                  	leaq	-0x8(%rcx), %rdx
    8854: 48 39 c7                     	cmpq	%rax, %rdi
    8857: 75 e7                        	jne	0x8840 <layout_transition_destroy+0x90>
    8859: 48 8b 45 38                  	movq	0x38(%rbp), %rax
    885d: 48 85 c0                     	testq	%rax, %rax
    8860: 74 05                        	je	0x8867 <layout_transition_destroy+0xb7>
    8862: 48 89 ef                     	movq	%rbp, %rdi
    8865: ff d0                        	callq	*%rax
    8867: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    886c: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    8875: 75 48                        	jne	0x88bf <layout_transition_destroy+0x10f>
    8877: 48 83 c4 18                  	addq	$0x18, %rsp
    887b: 48 89 ef                     	movq	%rbp, %rdi
    887e: 5b                           	popq	%rbx
    887f: 5d                           	popq	%rbp
    8880: e9 eb a7 ff ff               	jmp	0x3070 <free@plt>
    8885: 48 89 f3                     	movq	%rsi, %rbx
    8888: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    8890: 48 8d 7b 08                  	leaq	0x8(%rbx), %rdi
    8894: e8 97 ab ff ff               	callq	0x3430 <wl_list_remove@plt>
    8899: 48 89 df                     	movq	%rbx, %rdi
    889c: e8 cf a7 ff ff               	callq	0x3070 <free@plt>
    88a1: eb b6                        	jmp	0x8859 <layout_transition_destroy+0xa9>
    88a3: 48 89 d3                     	movq	%rdx, %rbx
    88a6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    88b0: e8 7b ab ff ff               	callq	0x3430 <wl_list_remove@plt>
    88b5: 48 89 df                     	movq	%rbx, %rdi
    88b8: e8 b3 a7 ff ff               	callq	0x3070 <free@plt>
    88bd: eb 9a                        	jmp	0x8859 <layout_transition_destroy+0xa9>
    88bf: e8 5c a9 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    88c4: 66 90                        	nop
    88c6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000088d0 <transition_move_resize_view_user_frame>:
    88d0: 41 57                        	pushq	%r15
    88d2: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    88d6: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    88da: 49 89 ff                     	movq	%rdi, %r15
    88dd: 41 56                        	pushq	%r14
    88df: 41 55                        	pushq	%r13
    88e1: 41 54                        	pushq	%r12
    88e3: 55                           	pushq	%rbp
    88e4: 53                           	pushq	%rbx
    88e5: 48 83 ec 18                  	subq	$0x18, %rsp
    88e9: 48 8b 5f 08                  	movq	0x8(%rdi), %rbx
    88ed: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    88f6: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    88fb: 31 c0                        	xorl	%eax, %eax
    88fd: 8b 47 20                     	movl	0x20(%rdi), %eax
    8900: f3 48 0f 2a c0               	cvtsi2ss	%rax, %xmm0
    8905: 8b 47 1c                     	movl	0x1c(%rdi), %eax
    8908: f3 48 0f 2a c8               	cvtsi2ss	%rax, %xmm1
    890d: f3 0f 5e c1                  	divss	%xmm1, %xmm0
    8911: f3 0f 5a c0                  	cvtss2sd	%xmm0, %xmm0
    8915: f2 0f 59 05 0b 51 00 00      	mulsd	0x510b(%rip), %xmm0     # 0xda28 <__func__.11687+0x28>
    891d: e8 de ac ff ff               	callq	0x3600 <sin@plt>
    8922: 8b 53 08                     	movl	0x8(%rbx), %edx
    8925: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8929: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    892d: 8b 43 10                     	movl	0x10(%rbx), %eax
    8930: f2 0f 5a c0                  	cvtsd2ss	%xmm0, %xmm0
    8934: f3 0f 5a c0                  	cvtss2sd	%xmm0, %xmm0
    8938: f2 0f 2a d2                  	cvtsi2sd	%edx, %xmm2
    893c: 29 d0                        	subl	%edx, %eax
    893e: 8b 53 0c                     	movl	0xc(%rbx), %edx
    8941: f2 0f 2a c8                  	cvtsi2sd	%eax, %xmm1
    8945: 8b 43 14                     	movl	0x14(%rbx), %eax
    8948: f2 0f 59 c8                  	mulsd	%xmm0, %xmm1
    894c: 29 d0                        	subl	%edx, %eax
    894e: f2 0f 58 ca                  	addsd	%xmm2, %xmm1
    8952: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    8956: f2 0f 2a d2                  	cvtsi2sd	%edx, %xmm2
    895a: 8b 53 20                     	movl	0x20(%rbx), %edx
    895d: f2 44 0f 2c e9               	cvttsd2si	%xmm1, %r13d
    8962: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8966: f2 0f 2a c8                  	cvtsi2sd	%eax, %xmm1
    896a: 8b 43 18                     	movl	0x18(%rbx), %eax
    896d: f2 0f 59 c8                  	mulsd	%xmm0, %xmm1
    8971: 29 c2                        	subl	%eax, %edx
    8973: f2 0f 58 ca                  	addsd	%xmm2, %xmm1
    8977: f2 44 0f 2c f1               	cvttsd2si	%xmm1, %r14d
    897c: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8980: f2 0f 2a ca                  	cvtsi2sd	%edx, %xmm1
    8984: 8b 53 24                     	movl	0x24(%rbx), %edx
    8987: 66 0f 28 d1                  	movapd	%xmm1, %xmm2
    898b: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    898f: f2 0f 59 d0                  	mulsd	%xmm0, %xmm2
    8993: f2 0f 2a c8                  	cvtsi2sd	%eax, %xmm1
    8997: 8b 43 1c                     	movl	0x1c(%rbx), %eax
    899a: f2 0f 58 ca                  	addsd	%xmm2, %xmm1
    899e: 29 c2                        	subl	%eax, %edx
    89a0: 41 83 3f 0a                  	cmpl	$0xa, (%r15)
    89a4: f2 0f 2c e9                  	cvttsd2si	%xmm1, %ebp
    89a8: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    89ac: f2 0f 2a ca                  	cvtsi2sd	%edx, %xmm1
    89b0: f2 0f 59 c1                  	mulsd	%xmm1, %xmm0
    89b4: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    89b8: f2 0f 2a c8                  	cvtsi2sd	%eax, %xmm1
    89bc: f2 0f 58 c1                  	addsd	%xmm1, %xmm0
    89c0: f2 44 0f 2c e0               	cvttsd2si	%xmm0, %r12d
    89c5: 74 39                        	je	0x8a00 <transition_move_resize_view_user_frame+0x130>
    89c7: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    89cc: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    89d5: 75 3c                        	jne	0x8a13 <transition_move_resize_view_user_frame+0x143>
    89d7: 48 8b 3b                     	movq	(%rbx), %rdi
    89da: 48 83 c4 18                  	addq	$0x18, %rsp
    89de: 45 89 e0                     	movl	%r12d, %r8d
    89e1: 89 e9                        	movl	%ebp, %ecx
    89e3: 5b                           	popq	%rbx
    89e4: 44 89 f2                     	movl	%r14d, %edx
    89e7: 44 89 ee                     	movl	%r13d, %esi
    89ea: 5d                           	popq	%rbp
    89eb: 41 5c                        	popq	%r12
    89ed: 41 5d                        	popq	%r13
    89ef: 41 5e                        	popq	%r14
    89f1: 41 5f                        	popq	%r15
    89f3: e9 78 b6 ff ff               	jmp	0x4070 <ivi_layout_surface_set_destination_rectangle>
    89f8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    8a00: 48 8b 3b                     	movq	(%rbx), %rdi
    8a03: 45 89 e0                     	movl	%r12d, %r8d
    8a06: 89 e9                        	movl	%ebp, %ecx
    8a08: 31 d2                        	xorl	%edx, %edx
    8a0a: 31 f6                        	xorl	%esi, %esi
    8a0c: e8 9f b7 ff ff               	callq	0x41b0 <ivi_layout_surface_set_source_rectangle>
    8a11: eb b4                        	jmp	0x89c7 <transition_move_resize_view_user_frame+0xf7>
    8a13: e8 08 a8 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8a18: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

0000000000008a20 <visibility_on_transition_destroy>:
    8a20: 41 54                        	pushq	%r12
    8a22: be 01 00 00 00               	movl	$0x1, %esi
    8a27: 55                           	pushq	%rbp
    8a28: 53                           	pushq	%rbx
    8a29: 48 89 fb                     	movq	%rdi, %rbx
    8a2c: 48 83 ec 10                  	subq	$0x10, %rsp
    8a30: 48 8b 6f 08                  	movq	0x8(%rdi), %rbp
    8a34: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8a3d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8a42: 31 c0                        	xorl	%eax, %eax
    8a44: 4c 8b 67 10                  	movq	0x10(%rdi), %r12
    8a48: 48 8b 7d 00                  	movq	(%rbp), %rdi
    8a4c: e8 7f b4 ff ff               	callq	0x3ed0 <ivi_layout_surface_set_visibility>
    8a51: 48 89 ef                     	movq	%rbp, %rdi
    8a54: e8 17 a6 ff ff               	callq	0x3070 <free@plt>
    8a59: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
    8a61: 4c 89 e7                     	movq	%r12, %rdi
    8a64: e8 07 a6 ff ff               	callq	0x3070 <free@plt>
    8a69: 48 c7 43 10 00 00 00 00      	movq	$0x0, 0x10(%rbx)
    8a71: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    8a76: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    8a7f: 75 09                        	jne	0x8a8a <visibility_on_transition_destroy+0x6a>
    8a81: 48 83 c4 10                  	addq	$0x10, %rsp
    8a85: 5b                           	popq	%rbx
    8a86: 5d                           	popq	%rbp
    8a87: 41 5c                        	popq	%r12
    8a89: c3                           	retq
    8a8a: e8 91 a7 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8a8f: 90                           	nop

0000000000008a90 <fade_view_user_frame>:
    8a90: 55                           	pushq	%rbp
    8a91: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    8a95: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8a99: 53                           	pushq	%rbx
    8a9a: 48 83 ec 18                  	subq	$0x18, %rsp
    8a9e: 48 8b 6f 08                  	movq	0x8(%rdi), %rbp
    8aa2: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8aab: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8ab0: 31 c0                        	xorl	%eax, %eax
    8ab2: 8b 47 20                     	movl	0x20(%rdi), %eax
    8ab5: 48 8b 5d 00                  	movq	(%rbp), %rbx
    8ab9: f3 48 0f 2a c0               	cvtsi2ss	%rax, %xmm0
    8abe: 8b 47 1c                     	movl	0x1c(%rdi), %eax
    8ac1: f3 48 0f 2a c8               	cvtsi2ss	%rax, %xmm1
    8ac6: f3 0f 5e c1                  	divss	%xmm1, %xmm0
    8aca: f3 0f 5a c0                  	cvtss2sd	%xmm0, %xmm0
    8ace: f2 0f 59 05 52 4f 00 00      	mulsd	0x4f52(%rip), %xmm0     # 0xda28 <__func__.11687+0x28>
    8ad6: e8 25 ab ff ff               	callq	0x3600 <sin@plt>
    8adb: f2 0f 10 4d 08               	movsd	0x8(%rbp), %xmm1
    8ae0: 48 89 df                     	movq	%rbx, %rdi
    8ae3: 66 0f 28 d0                  	movapd	%xmm0, %xmm2
    8ae7: f2 0f 10 45 10               	movsd	0x10(%rbp), %xmm0
    8aec: f2 0f 5a d2                  	cvtsd2ss	%xmm2, %xmm2
    8af0: f3 0f 5a d2                  	cvtss2sd	%xmm2, %xmm2
    8af4: f2 0f 5c c1                  	subsd	%xmm1, %xmm0
    8af8: f2 0f 59 c2                  	mulsd	%xmm2, %xmm0
    8afc: f2 0f 58 c8                  	addsd	%xmm0, %xmm1
    8b00: f2 0f 58 0d 48 4d 00 00      	addsd	0x4d48(%rip), %xmm1     # 0xd850 <__func__.12894+0x40>
    8b08: 66 48 0f 7e ce               	movq	%xmm1, %rsi
    8b0d: e8 8e b4 ff ff               	callq	0x3fa0 <ivi_layout_surface_set_opacity>
    8b12: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    8b17: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    8b20: 75 13                        	jne	0x8b35 <fade_view_user_frame+0xa5>
    8b22: 48 83 c4 18                  	addq	$0x18, %rsp
    8b26: 48 89 df                     	movq	%rbx, %rdi
    8b29: be 01 00 00 00               	movl	$0x1, %esi
    8b2e: 5b                           	popq	%rbx
    8b2f: 5d                           	popq	%rbp
    8b30: e9 9b b3 ff ff               	jmp	0x3ed0 <ivi_layout_surface_set_visibility>
    8b35: e8 e6 a6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8b3a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000008b40 <visibility_off_transition_destroy>:
    8b40: 41 54                        	pushq	%r12
    8b42: 31 f6                        	xorl	%esi, %esi
    8b44: 55                           	pushq	%rbp
    8b45: 53                           	pushq	%rbx
    8b46: 48 89 fb                     	movq	%rdi, %rbx
    8b49: 48 83 ec 10                  	subq	$0x10, %rsp
    8b4d: 48 8b 6f 08                  	movq	0x8(%rdi), %rbp
    8b51: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8b5a: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8b5f: 31 c0                        	xorl	%eax, %eax
    8b61: 4c 8b 67 10                  	movq	0x10(%rdi), %r12
    8b65: 48 8b 7d 00                  	movq	(%rbp), %rdi
    8b69: e8 62 b3 ff ff               	callq	0x3ed0 <ivi_layout_surface_set_visibility>
    8b6e: 48 8b 7d 00                  	movq	(%rbp), %rdi
    8b72: f2 0f 10 05 d6 4c 00 00      	movsd	0x4cd6(%rip), %xmm0     # 0xd850 <__func__.12894+0x40>
    8b7a: f2 41 0f 58 04 24            	addsd	(%r12), %xmm0
    8b80: 66 48 0f 7e c6               	movq	%xmm0, %rsi
    8b85: e8 16 b4 ff ff               	callq	0x3fa0 <ivi_layout_surface_set_opacity>
    8b8a: 48 89 ef                     	movq	%rbp, %rdi
    8b8d: e8 de a4 ff ff               	callq	0x3070 <free@plt>
    8b92: 48 c7 43 08 00 00 00 00      	movq	$0x0, 0x8(%rbx)
    8b9a: 4c 89 e7                     	movq	%r12, %rdi
    8b9d: e8 ce a4 ff ff               	callq	0x3070 <free@plt>
    8ba2: 48 c7 43 10 00 00 00 00      	movq	$0x0, 0x10(%rbx)
    8baa: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    8baf: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    8bb8: 75 09                        	jne	0x8bc3 <visibility_off_transition_destroy+0x83>
    8bba: 48 83 c4 10                  	addq	$0x10, %rsp
    8bbe: 5b                           	popq	%rbx
    8bbf: 5d                           	popq	%rbp
    8bc0: 41 5c                        	popq	%r12
    8bc2: c3                           	retq
    8bc3: e8 58 a6 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8bc8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

0000000000008bd0 <transition_move_layer_user_frame>:
    8bd0: 53                           	pushq	%rbx
    8bd1: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    8bd5: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8bd9: 48 83 ec 10                  	subq	$0x10, %rsp
    8bdd: 48 8b 5f 08                  	movq	0x8(%rdi), %rbx
    8be1: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8bea: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8bef: 31 c0                        	xorl	%eax, %eax
    8bf1: 8b 47 20                     	movl	0x20(%rdi), %eax
    8bf4: f3 48 0f 2a c0               	cvtsi2ss	%rax, %xmm0
    8bf9: 8b 47 1c                     	movl	0x1c(%rdi), %eax
    8bfc: f3 48 0f 2a c8               	cvtsi2ss	%rax, %xmm1
    8c01: f3 0f 5e c1                  	divss	%xmm1, %xmm0
    8c05: f3 0f 5a c0                  	cvtss2sd	%xmm0, %xmm0
    8c09: f2 0f 59 05 17 4e 00 00      	mulsd	0x4e17(%rip), %xmm0     # 0xda28 <__func__.11687+0x28>
    8c11: e8 ea a9 ff ff               	callq	0x3600 <sin@plt>
    8c16: 8b 43 08                     	movl	0x8(%rbx), %eax
    8c19: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
    8c1e: 64 48 33 34 25 28 00 00 00   	xorq	%fs:0x28, %rsi
    8c27: 8b 53 0c                     	movl	0xc(%rbx), %edx
    8c2a: 75 56                        	jne	0x8c82 <transition_move_layer_user_frame+0xb2>
    8c2c: 8b 4b 14                     	movl	0x14(%rbx), %ecx
    8c2f: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    8c33: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8c37: f2 0f 5a c0                  	cvtsd2ss	%xmm0, %xmm0
    8c3b: 48 8b 3b                     	movq	(%rbx), %rdi
    8c3e: 29 d1                        	subl	%edx, %ecx
    8c40: f3 0f 2a d1                  	cvtsi2ss	%ecx, %xmm2
    8c44: 8b 4b 10                     	movl	0x10(%rbx), %ecx
    8c47: 48 83 c4 10                  	addq	$0x10, %rsp
    8c4b: 5b                           	popq	%rbx
    8c4c: 29 c1                        	subl	%eax, %ecx
    8c4e: 0f 28 da                     	movaps	%xmm2, %xmm3
    8c51: 66 0f ef d2                  	pxor	%xmm2, %xmm2
    8c55: f3 0f 2a c9                  	cvtsi2ss	%ecx, %xmm1
    8c59: f3 0f 59 d8                  	mulss	%xmm0, %xmm3
    8c5d: f3 0f 2a d2                  	cvtsi2ss	%edx, %xmm2
    8c61: f3 0f 59 c1                  	mulss	%xmm1, %xmm0
    8c65: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8c69: f3 0f 2a c8                  	cvtsi2ss	%eax, %xmm1
    8c6d: f3 0f 58 d3                  	addss	%xmm3, %xmm2
    8c71: f3 0f 58 c8                  	addss	%xmm0, %xmm1
    8c75: f3 0f 2c d2                  	cvttss2si	%xmm2, %edx
    8c79: f3 0f 2c f1                  	cvttss2si	%xmm1, %esi
    8c7d: e9 ce b1 ff ff               	jmp	0x3e50 <ivi_layout_layer_set_position>
    8c82: e8 99 a5 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8c87: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000008c90 <transition_fade_layer_user_frame>:
    8c90: 41 54                        	pushq	%r12
    8c92: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    8c96: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8c9a: 41 bc 01 00 00 00            	movl	$0x1, %r12d
    8ca0: 55                           	pushq	%rbp
    8ca1: 48 89 fd                     	movq	%rdi, %rbp
    8ca4: 53                           	pushq	%rbx
    8ca5: 48 83 ec 10                  	subq	$0x10, %rsp
    8ca9: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8cb2: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8cb7: 31 c0                        	xorl	%eax, %eax
    8cb9: 8b 47 20                     	movl	0x20(%rdi), %eax
    8cbc: f3 48 0f 2a c0               	cvtsi2ss	%rax, %xmm0
    8cc1: 8b 47 1c                     	movl	0x1c(%rdi), %eax
    8cc4: f3 48 0f 2a c8               	cvtsi2ss	%rax, %xmm1
    8cc9: f3 0f 5e c1                  	divss	%xmm1, %xmm0
    8ccd: f3 0f 5a c0                  	cvtss2sd	%xmm0, %xmm0
    8cd1: f2 0f 59 05 4f 4d 00 00      	mulsd	0x4d4f(%rip), %xmm0     # 0xda28 <__func__.11687+0x28>
    8cd9: e8 22 a9 ff ff               	callq	0x3600 <sin@plt>
    8cde: 48 8b 5d 08                  	movq	0x8(%rbp), %rbx
    8ce2: 66 0f 28 d0                  	movapd	%xmm0, %xmm2
    8ce6: 8b 55 24                     	movl	0x24(%rbp), %edx
    8ce9: f2 0f 5a d2                  	cvtsd2ss	%xmm2, %xmm2
    8ced: f3 0f 5a d2                  	cvtss2sd	%xmm2, %xmm2
    8cf1: f2 0f 10 4b 10               	movsd	0x10(%rbx), %xmm1
    8cf6: f2 0f 10 43 18               	movsd	0x18(%rbx), %xmm0
    8cfb: f2 0f 5c c1                  	subsd	%xmm1, %xmm0
    8cff: f2 0f 59 c2                  	mulsd	%xmm2, %xmm0
    8d03: f2 0f 58 c8                  	addsd	%xmm0, %xmm1
    8d07: f2 0f 58 0d 41 4b 00 00      	addsd	0x4b41(%rip), %xmm1     # 0xd850 <__func__.12894+0x40>
    8d0f: 66 48 0f 7e ce               	movq	%xmm1, %rsi
    8d14: 85 d2                        	testl	%edx, %edx
    8d16: 74 0c                        	je	0x8d24 <transition_fade_layer_user_frame+0x94>
    8d18: 8b 43 08                     	movl	0x8(%rbx), %eax
    8d1b: 45 31 e4                     	xorl	%r12d, %r12d
    8d1e: 85 c0                        	testl	%eax, %eax
    8d20: 41 0f 95 c4                  	setne	%r12b
    8d24: 48 8b 3b                     	movq	(%rbx), %rdi
    8d27: e8 e4 af ff ff               	callq	0x3d10 <ivi_layout_layer_set_opacity>
    8d2c: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    8d31: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    8d3a: 75 13                        	jne	0x8d4f <transition_fade_layer_user_frame+0xbf>
    8d3c: 48 8b 3b                     	movq	(%rbx), %rdi
    8d3f: 48 83 c4 10                  	addq	$0x10, %rsp
    8d43: 44 89 e6                     	movl	%r12d, %esi
    8d46: 5b                           	popq	%rbx
    8d47: 5d                           	popq	%rbp
    8d48: 41 5c                        	popq	%r12
    8d4a: e9 41 af ff ff               	jmp	0x3c90 <ivi_layout_layer_set_visibility>
    8d4f: e8 cc a4 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8d54: 66 90                        	nop
    8d56: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000008d60 <create_layout_transition>:
    8d60: 48 83 ec 18                  	subq	$0x18, %rsp
    8d64: bf 40 00 00 00               	movl	$0x40, %edi
    8d69: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8d72: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8d77: 31 c0                        	xorl	%eax, %eax
    8d79: e8 f2 a6 ff ff               	callq	0x3470 <malloc@plt>
    8d7e: 48 85 c0                     	testq	%rax, %rax
    8d81: 74 5f                        	je	0x8de2 <create_layout_transition+0x82>
    8d83: c7 00 0b 00 00 00            	movl	$0xb, (%rax)
    8d89: c7 40 18 00 00 00 00         	movl	$0x0, 0x18(%rax)
    8d90: c7 40 1c 2c 01 00 00         	movl	$0x12c, 0x1c(%rax)      # imm = 0x12C
    8d97: c7 40 20 00 00 00 00         	movl	$0x0, 0x20(%rax)
    8d9e: c7 40 24 00 00 00 00         	movl	$0x0, 0x24(%rax)
    8da5: 48 c7 40 28 00 00 00 00      	movq	$0x0, 0x28(%rax)
    8dad: 48 c7 40 08 00 00 00 00      	movq	$0x0, 0x8(%rax)
    8db5: 48 c7 40 10 00 00 00 00      	movq	$0x0, 0x10(%rax)
    8dbd: 48 c7 40 30 00 00 00 00      	movq	$0x0, 0x30(%rax)
    8dc5: 48 c7 40 38 00 00 00 00      	movq	$0x0, 0x38(%rax)
    8dcd: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    8dd2: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    8ddb: 75 1c                        	jne	0x8df9 <create_layout_transition+0x99>
    8ddd: 48 83 c4 18                  	addq	$0x18, %rsp
    8de1: c3                           	retq
    8de2: 48 8d 35 a7 4b 00 00         	leaq	0x4ba7(%rip), %rsi      # 0xd990 <__func__.11714>
    8de9: 48 8d 3d 68 4a 00 00         	leaq	0x4a68(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    8df0: e8 1b a4 ff ff               	callq	0x3210 <weston_log@plt>
    8df5: 31 c0                        	xorl	%eax, %eax
    8df7: eb d4                        	jmp	0x8dcd <create_layout_transition+0x6d>
    8df9: e8 22 a4 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8dfe: 66 90                        	nop

0000000000008e00 <layout_transition_frame>:
    8e00: 41 55                        	pushq	%r13
    8e02: 41 54                        	pushq	%r12
    8e04: 49 89 fc                     	movq	%rdi, %r12
    8e07: 48 83 c7 08                  	addq	$0x8, %rdi
    8e0b: 55                           	pushq	%rbp
    8e0c: 53                           	pushq	%rbx
    8e0d: 48 83 ec 28                  	subq	$0x28, %rsp
    8e11: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8e1a: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    8e1f: 31 c0                        	xorl	%eax, %eax
    8e21: 48 c7 04 24 00 00 00 00      	movq	$0x0, (%rsp)
    8e29: 48 c7 44 24 08 00 00 00 00   	movq	$0x0, 0x8(%rsp)
    8e32: e8 b9 a5 ff ff               	callq	0x33f0 <wl_list_empty@plt>
    8e37: 85 c0                        	testl	%eax, %eax
    8e39: 0f 85 09 01 00 00            	jne	0x8f48 <layout_transition_frame+0x148>
    8e3f: 49 8b 3c 24                  	movq	(%r12), %rdi
    8e43: be 21 00 00 00               	movl	$0x21, %esi
    8e48: e8 43 a2 ff ff               	callq	0x3090 <wl_event_source_timer_update@plt>
    8e4d: 48 89 e6                     	movq	%rsp, %rsi
    8e50: bf 01 00 00 00               	movl	$0x1, %edi
    8e55: e8 66 a6 ff ff               	callq	0x34c0 <clock_gettime@plt>
    8e5a: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    8e5e: 49 8b 44 24 10               	movq	0x10(%r12), %rax
    8e63: f2 48 0f 2a 04 24            	cvtsi2sdq	(%rsp), %xmm0
    8e69: f2 0f 10 0d bf 4b 00 00      	movsd	0x4bbf(%rip), %xmm1     # 0xda30 <__func__.11687+0x30>
    8e71: 4c 8b 68 08                  	movq	0x8(%rax), %r13
    8e75: 48 8d 50 f8                  	leaq	-0x8(%rax), %rdx
    8e79: f2 0f 59 c8                  	mulsd	%xmm0, %xmm1
    8e7d: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    8e81: f2 48 0f 2a 44 24 08         	cvtsi2sdq	0x8(%rsp), %xmm0
    8e88: f2 0f 59 05 a8 4b 00 00      	mulsd	0x4ba8(%rip), %xmm0     # 0xda38 <__func__.11687+0x38>
    8e90: 49 83 ed 08                  	subq	$0x8, %r13
    8e94: f2 0f 58 c1                  	addsd	%xmm1, %xmm0
    8e98: f2 48 0f 2c e8               	cvttsd2si	%xmm0, %rbp
    8e9d: 49 39 d4                     	cmpq	%rdx, %r12
    8ea0: 75 5c                        	jne	0x8efe <layout_transition_frame+0xfe>
    8ea2: eb 7c                        	jmp	0x8f20 <layout_transition_frame+0x120>
    8ea4: 0f 1f 40 00                  	nopl	(%rax)
    8ea8: 89 ee                        	movl	%ebp, %esi
    8eaa: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8eae: 29 c6                        	subl	%eax, %esi
    8eb0: 89 f2                        	movl	%esi, %edx
    8eb2: f2 48 0f 2a ca               	cvtsi2sd	%rdx, %xmm1
    8eb7: 48 89 d0                     	movq	%rdx, %rax
    8eba: 8b 53 1c                     	movl	0x1c(%rbx), %edx
    8ebd: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    8ec1: f2 48 0f 2a c2               	cvtsi2sd	%rdx, %xmm0
    8ec6: 66 0f 2e c8                  	ucomisd	%xmm0, %xmm1
    8eca: 72 4c                        	jb	0x8f18 <layout_transition_frame+0x118>
    8ecc: 89 53 20                     	movl	%edx, 0x20(%rbx)
    8ecf: c7 43 24 01 00 00 00         	movl	$0x1, 0x24(%rbx)
    8ed6: 48 89 df                     	movq	%rbx, %rdi
    8ed9: ff 53 30                     	callq	*0x30(%rbx)
    8edc: 8b 43 24                     	movl	0x24(%rbx), %eax
    8edf: 85 c0                        	testl	%eax, %eax
    8ee1: 74 08                        	je	0x8eeb <layout_transition_frame+0xeb>
    8ee3: 48 89 df                     	movq	%rbx, %rdi
    8ee6: e8 c5 f8 ff ff               	callq	0x87b0 <layout_transition_destroy>
    8eeb: 49 8b 45 10                  	movq	0x10(%r13), %rax
    8eef: 4c 89 ea                     	movq	%r13, %rdx
    8ef2: 48 83 e8 08                  	subq	$0x8, %rax
    8ef6: 4d 39 ec                     	cmpq	%r13, %r12
    8ef9: 74 25                        	je	0x8f20 <layout_transition_frame+0x120>
    8efb: 49 89 c5                     	movq	%rax, %r13
    8efe: 48 8b 1a                     	movq	(%rdx), %rbx
    8f01: 8b 43 18                     	movl	0x18(%rbx), %eax
    8f04: 85 c0                        	testl	%eax, %eax
    8f06: 75 a0                        	jne	0x8ea8 <layout_transition_frame+0xa8>
    8f08: 89 6b 18                     	movl	%ebp, 0x18(%rbx)
    8f0b: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    8f0f: eb a9                        	jmp	0x8eba <layout_transition_frame+0xba>
    8f11: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    8f18: 89 43 20                     	movl	%eax, 0x20(%rbx)
    8f1b: eb b9                        	jmp	0x8ed6 <layout_transition_frame+0xd6>
    8f1d: 0f 1f 00                     	nopl	(%rax)
    8f20: e8 1b db ff ff               	callq	0x6a40 <ivi_layout_commit_changes>
    8f25: 48 8b 74 24 18               	movq	0x18(%rsp), %rsi
    8f2a: 64 48 33 34 25 28 00 00 00   	xorq	%fs:0x28, %rsi
    8f33: b8 01 00 00 00               	movl	$0x1, %eax
    8f38: 75 1b                        	jne	0x8f55 <layout_transition_frame+0x155>
    8f3a: 48 83 c4 28                  	addq	$0x28, %rsp
    8f3e: 5b                           	popq	%rbx
    8f3f: 5d                           	popq	%rbp
    8f40: 41 5c                        	popq	%r12
    8f42: 41 5d                        	popq	%r13
    8f44: c3                           	retq
    8f45: 0f 1f 00                     	nopl	(%rax)
    8f48: 49 8b 3c 24                  	movq	(%r12), %rdi
    8f4c: 31 f6                        	xorl	%esi, %esi
    8f4e: e8 3d a1 ff ff               	callq	0x3090 <wl_event_source_timer_update@plt>
    8f53: eb d0                        	jmp	0x8f25 <layout_transition_frame+0x125>
    8f55: e8 c6 a2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8f5a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000008f60 <layout_transition_register>:
    8f60: 55                           	pushq	%rbp
    8f61: 48 89 fd                     	movq	%rdi, %rbp
    8f64: 53                           	pushq	%rbx
    8f65: 48 83 ec 18                  	subq	$0x18, %rsp
    8f69: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    8f72: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    8f77: 31 c0                        	xorl	%eax, %eax
    8f79: e8 52 f1 ff ff               	callq	0x80d0 <get_instance>
    8f7e: bf 18 00 00 00               	movl	$0x18, %edi
    8f83: 48 89 c3                     	movq	%rax, %rbx
    8f86: e8 e5 a4 ff ff               	callq	0x3470 <malloc@plt>
    8f8b: 48 85 c0                     	testq	%rax, %rax
    8f8e: 74 30                        	je	0x8fc0 <layout_transition_register+0x60>
    8f90: 48 89 28                     	movq	%rbp, (%rax)
    8f93: 48 8d 70 08                  	leaq	0x8(%rax), %rsi
    8f97: 48 8d bb d8 00 00 00         	leaq	0xd8(%rbx), %rdi
    8f9e: e8 fd a6 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    8fa3: b8 01 00 00 00               	movl	$0x1, %eax
    8fa8: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    8fad: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    8fb6: 75 1f                        	jne	0x8fd7 <layout_transition_register+0x77>
    8fb8: 48 83 c4 18                  	addq	$0x18, %rsp
    8fbc: 5b                           	popq	%rbx
    8fbd: 5d                           	popq	%rbp
    8fbe: c3                           	retq
    8fbf: 90                           	nop
    8fc0: 48 8d 35 a9 49 00 00         	leaq	0x49a9(%rip), %rsi      # 0xd970 <__func__.11693>
    8fc7: 48 8d 3d 8a 48 00 00         	leaq	0x488a(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    8fce: e8 3d a2 ff ff               	callq	0x3210 <weston_log@plt>
    8fd3: 31 c0                        	xorl	%eax, %eax
    8fd5: eb d1                        	jmp	0x8fa8 <layout_transition_register+0x48>
    8fd7: e8 44 a2 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    8fdc: 0f 1f 40 00                  	nopl	(%rax)

0000000000008fe0 <create_visibility_transition>:
    8fe0: 41 57                        	pushq	%r15
    8fe2: 66 49 0f 7e c7               	movq	%xmm0, %r15
    8fe7: 41 56                        	pushq	%r14
    8fe9: 49 89 f6                     	movq	%rsi, %r14
    8fec: 41 55                        	pushq	%r13
    8fee: 49 89 d5                     	movq	%rdx, %r13
    8ff1: 41 54                        	pushq	%r12
    8ff3: 49 89 fc                     	movq	%rdi, %r12
    8ff6: 55                           	pushq	%rbp
    8ff7: 89 cd                        	movl	%ecx, %ebp
    8ff9: 53                           	pushq	%rbx
    8ffa: 48 83 ec 28                  	subq	$0x28, %rsp
    8ffe: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9007: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    900c: 31 c0                        	xorl	%eax, %eax
    900e: f2 0f 11 4c 24 08            	movsd	%xmm1, 0x8(%rsp)
    9014: e8 47 fd ff ff               	callq	0x8d60 <create_layout_transition>
    9019: 48 85 c0                     	testq	%rax, %rax
    901c: 0f 84 d6 00 00 00            	je	0x90f8 <create_visibility_transition+0x118>
    9022: bf 18 00 00 00               	movl	$0x18, %edi
    9027: 48 89 c3                     	movq	%rax, %rbx
    902a: e8 41 a4 ff ff               	callq	0x3470 <malloc@plt>
    902f: f2 0f 10 4c 24 08            	movsd	0x8(%rsp), %xmm1
    9035: 48 85 c0                     	testq	%rax, %rax
    9038: 0f 84 99 00 00 00            	je	0x90d7 <create_visibility_transition+0xf7>
    903e: 48 8d 15 0b f5 ff ff         	leaq	-0xaf5(%rip), %rdx      # 0x8550 <is_transition_fade_view_func>
    9045: c7 03 09 00 00 00            	movl	$0x9, (%rbx)
    904b: 48 8d 0d 3e fa ff ff         	leaq	-0x5c2(%rip), %rcx      # 0x8a90 <fade_view_user_frame>
    9052: 48 89 53 28                  	movq	%rdx, 0x28(%rbx)
    9056: 4c 89 73 10                  	movq	%r14, 0x10(%rbx)
    905a: 48 89 43 08                  	movq	%rax, 0x8(%rbx)
    905e: 48 89 4b 30                  	movq	%rcx, 0x30(%rbx)
    9062: 4c 89 6b 38                  	movq	%r13, 0x38(%rbx)
    9066: 85 ed                        	testl	%ebp, %ebp
    9068: 75 46                        	jne	0x90b0 <create_visibility_transition+0xd0>
    906a: 4c 89 20                     	movq	%r12, (%rax)
    906d: 48 89 df                     	movq	%rbx, %rdi
    9070: 4c 89 78 08                  	movq	%r15, 0x8(%rax)
    9074: f2 0f 11 48 10               	movsd	%xmm1, 0x10(%rax)
    9079: e8 e2 fe ff ff               	callq	0x8f60 <layout_transition_register>
    907e: 84 c0                        	testb	%al, %al
    9080: 75 36                        	jne	0x90b8 <create_visibility_transition+0xd8>
    9082: 48 89 df                     	movq	%rbx, %rdi
    9085: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    908a: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9093: 75 67                        	jne	0x90fc <create_visibility_transition+0x11c>
    9095: 48 83 c4 28                  	addq	$0x28, %rsp
    9099: 5b                           	popq	%rbx
    909a: 5d                           	popq	%rbp
    909b: 41 5c                        	popq	%r12
    909d: 41 5d                        	popq	%r13
    909f: 41 5e                        	popq	%r14
    90a1: 41 5f                        	popq	%r15
    90a3: e9 08 f7 ff ff               	jmp	0x87b0 <layout_transition_destroy>
    90a8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    90b0: 89 6b 1c                     	movl	%ebp, 0x1c(%rbx)
    90b3: eb b5                        	jmp	0x906a <create_visibility_transition+0x8a>
    90b5: 0f 1f 00                     	nopl	(%rax)
    90b8: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    90bd: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    90c6: 75 34                        	jne	0x90fc <create_visibility_transition+0x11c>
    90c8: 48 83 c4 28                  	addq	$0x28, %rsp
    90cc: 5b                           	popq	%rbx
    90cd: 5d                           	popq	%rbp
    90ce: 41 5c                        	popq	%r12
    90d0: 41 5d                        	popq	%r13
    90d2: 41 5e                        	popq	%r14
    90d4: 41 5f                        	popq	%r15
    90d6: c3                           	retq
    90d7: 48 8d 3d 7a 47 00 00         	leaq	0x477a(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    90de: 48 8d 35 2b 48 00 00         	leaq	0x482b(%rip), %rsi      # 0xd910 <__func__.11800>
    90e5: e8 26 a1 ff ff               	callq	0x3210 <weston_log@plt>
    90ea: 48 89 df                     	movq	%rbx, %rdi
    90ed: e8 7e 9f ff ff               	callq	0x3070 <free@plt>
    90f2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    90f8: 31 ff                        	xorl	%edi, %edi
    90fa: eb 89                        	jmp	0x9085 <create_visibility_transition+0xa5>
    90fc: e8 1f a1 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9101: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    9106: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000009110 <is_surface_transition>:
    9110: 41 54                        	pushq	%r12
    9112: 55                           	pushq	%rbp
    9113: 48 89 fd                     	movq	%rdi, %rbp
    9116: 53                           	pushq	%rbx
    9117: 48 83 ec 10                  	subq	$0x10, %rsp
    911b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9124: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9129: 31 c0                        	xorl	%eax, %eax
    912b: e8 a0 ef ff ff               	callq	0x80d0 <get_instance>
    9130: 49 89 c4                     	movq	%rax, %r12
    9133: 48 8b 80 d0 00 00 00         	movq	0xd0(%rax), %rax
    913a: 48 8b 70 10                  	movq	0x10(%rax), %rsi
    913e: 48 8d 5e f8                  	leaq	-0x8(%rsi), %rbx
    9142: 48 39 d8                     	cmpq	%rbx, %rax
    9145: 75 20                        	jne	0x9167 <is_surface_transition+0x57>
    9147: eb 47                        	jmp	0x9190 <is_surface_transition+0x80>
    9149: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    9150: 83 f8 0a                     	cmpl	$0xa, %eax
    9153: 74 1f                        	je	0x9174 <is_surface_transition+0x64>
    9155: 48 8b 5b 10                  	movq	0x10(%rbx), %rbx
    9159: 48 83 eb 08                  	subq	$0x8, %rbx
    915d: 49 39 9c 24 d0 00 00 00      	cmpq	%rbx, 0xd0(%r12)
    9165: 74 29                        	je	0x9190 <is_surface_transition+0x80>
    9167: 48 8b 13                     	movq	(%rbx), %rdx
    916a: 8b 02                        	movl	(%rdx), %eax
    916c: 8d 48 f9                     	leal	-0x7(%rax), %ecx
    916f: 83 f9 01                     	cmpl	$0x1, %ecx
    9172: 77 dc                        	ja	0x9150 <is_surface_transition+0x40>
    9174: 48 8b 7a 08                  	movq	0x8(%rdx), %rdi
    9178: 48 89 ee                     	movq	%rbp, %rsi
    917b: ff 52 28                     	callq	*0x28(%rdx)
    917e: 85 c0                        	testl	%eax, %eax
    9180: 74 d3                        	je	0x9155 <is_surface_transition+0x45>
    9182: b8 01 00 00 00               	movl	$0x1, %eax
    9187: eb 09                        	jmp	0x9192 <is_surface_transition+0x82>
    9189: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    9190: 31 c0                        	xorl	%eax, %eax
    9192: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
    9197: 64 48 33 34 25 28 00 00 00   	xorq	%fs:0x28, %rsi
    91a0: 75 09                        	jne	0x91ab <is_surface_transition+0x9b>
    91a2: 48 83 c4 10                  	addq	$0x10, %rsp
    91a6: 5b                           	popq	%rbx
    91a7: 5d                           	popq	%rbp
    91a8: 41 5c                        	popq	%r12
    91aa: c3                           	retq
    91ab: e8 70 a0 ff ff               	callq	0x3220 <__stack_chk_fail@plt>

00000000000091b0 <is_surface_transition_with_type>:
    91b0: 41 55                        	pushq	%r13
    91b2: 49 89 fd                     	movq	%rdi, %r13
    91b5: 41 54                        	pushq	%r12
    91b7: 41 89 f4                     	movl	%esi, %r12d
    91ba: 55                           	pushq	%rbp
    91bb: 53                           	pushq	%rbx
    91bc: 48 83 ec 18                  	subq	$0x18, %rsp
    91c0: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    91c9: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    91ce: 31 c0                        	xorl	%eax, %eax
    91d0: e8 fb ee ff ff               	callq	0x80d0 <get_instance>
    91d5: 48 89 c5                     	movq	%rax, %rbp
    91d8: 48 8b 80 d0 00 00 00         	movq	0xd0(%rax), %rax
    91df: 48 8b 50 10                  	movq	0x10(%rax), %rdx
    91e3: 48 8d 5a f8                  	leaq	-0x8(%rdx), %rbx
    91e7: 48 39 d8                     	cmpq	%rbx, %rax
    91ea: 75 15                        	jne	0x9201 <is_surface_transition_with_type+0x51>
    91ec: eb 32                        	jmp	0x9220 <is_surface_transition_with_type+0x70>
    91ee: 66 90                        	nop
    91f0: 48 8b 5b 10                  	movq	0x10(%rbx), %rbx
    91f4: 48 83 eb 08                  	subq	$0x8, %rbx
    91f8: 48 39 9d d0 00 00 00         	cmpq	%rbx, 0xd0(%rbp)
    91ff: 74 1f                        	je	0x9220 <is_surface_transition_with_type+0x70>
    9201: 48 8b 03                     	movq	(%rbx), %rax
    9204: 44 39 20                     	cmpl	%r12d, (%rax)
    9207: 75 e7                        	jne	0x91f0 <is_surface_transition_with_type+0x40>
    9209: 48 8b 78 08                  	movq	0x8(%rax), %rdi
    920d: 4c 89 ee                     	movq	%r13, %rsi
    9210: ff 50 28                     	callq	*0x28(%rax)
    9213: 85 c0                        	testl	%eax, %eax
    9215: 74 d9                        	je	0x91f0 <is_surface_transition_with_type+0x40>
    9217: b8 01 00 00 00               	movl	$0x1, %eax
    921c: eb 04                        	jmp	0x9222 <is_surface_transition_with_type+0x72>
    921e: 66 90                        	nop
    9220: 31 c0                        	xorl	%eax, %eax
    9222: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    9227: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    9230: 75 0b                        	jne	0x923d <is_surface_transition_with_type+0x8d>
    9232: 48 83 c4 18                  	addq	$0x18, %rsp
    9236: 5b                           	popq	%rbx
    9237: 5d                           	popq	%rbp
    9238: 41 5c                        	popq	%r12
    923a: 41 5d                        	popq	%r13
    923c: c3                           	retq
    923d: e8 de 9f ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9242: 0f 1f 40 00                  	nopl	(%rax)
    9246: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000009250 <ivi_layout_remove_all_surface_transitions>:
    9250: 41 55                        	pushq	%r13
    9252: 49 89 fd                     	movq	%rdi, %r13
    9255: 41 54                        	pushq	%r12
    9257: 55                           	pushq	%rbp
    9258: 53                           	pushq	%rbx
    9259: 48 83 ec 18                  	subq	$0x18, %rsp
    925d: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9266: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    926b: 31 c0                        	xorl	%eax, %eax
    926d: e8 5e ee ff ff               	callq	0x80d0 <get_instance>
    9272: 49 89 c4                     	movq	%rax, %r12
    9275: 48 8b 80 d0 00 00 00         	movq	0xd0(%rax), %rax
    927c: 48 8b 48 10                  	movq	0x10(%rax), %rcx
    9280: 48 8b 69 08                  	movq	0x8(%rcx), %rbp
    9284: 48 8d 51 f8                  	leaq	-0x8(%rcx), %rdx
    9288: 48 83 ed 08                  	subq	$0x8, %rbp
    928c: 48 39 d0                     	cmpq	%rdx, %rax
    928f: 75 1f                        	jne	0x92b0 <ivi_layout_remove_all_surface_transitions+0x60>
    9291: eb 3d                        	jmp	0x92d0 <ivi_layout_remove_all_surface_transitions+0x80>
    9293: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    9298: 48 8b 45 10                  	movq	0x10(%rbp), %rax
    929c: 48 89 ea                     	movq	%rbp, %rdx
    929f: 48 83 e8 08                  	subq	$0x8, %rax
    92a3: 49 39 ac 24 d0 00 00 00      	cmpq	%rbp, 0xd0(%r12)
    92ab: 74 23                        	je	0x92d0 <ivi_layout_remove_all_surface_transitions+0x80>
    92ad: 48 89 c5                     	movq	%rax, %rbp
    92b0: 48 8b 1a                     	movq	(%rdx), %rbx
    92b3: 4c 89 ee                     	movq	%r13, %rsi
    92b6: 48 8b 7b 08                  	movq	0x8(%rbx), %rdi
    92ba: ff 53 28                     	callq	*0x28(%rbx)
    92bd: 85 c0                        	testl	%eax, %eax
    92bf: 74 d7                        	je	0x9298 <ivi_layout_remove_all_surface_transitions+0x48>
    92c1: 48 89 df                     	movq	%rbx, %rdi
    92c4: e8 e7 f4 ff ff               	callq	0x87b0 <layout_transition_destroy>
    92c9: eb cd                        	jmp	0x9298 <ivi_layout_remove_all_surface_transitions+0x48>
    92cb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    92d0: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    92d5: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    92de: 75 0b                        	jne	0x92eb <ivi_layout_remove_all_surface_transitions+0x9b>
    92e0: 48 83 c4 18                  	addq	$0x18, %rsp
    92e4: 5b                           	popq	%rbx
    92e5: 5d                           	popq	%rbp
    92e6: 41 5c                        	popq	%r12
    92e8: 41 5d                        	popq	%r13
    92ea: c3                           	retq
    92eb: e8 30 9f ff ff               	callq	0x3220 <__stack_chk_fail@plt>

00000000000092f0 <ivi_layout_transition_set_create>:
    92f0: 55                           	pushq	%rbp
    92f1: 48 89 fd                     	movq	%rdi, %rbp
    92f4: bf 18 00 00 00               	movl	$0x18, %edi
    92f9: 53                           	pushq	%rbx
    92fa: 48 83 ec 18                  	subq	$0x18, %rsp
    92fe: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9307: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    930c: 31 c0                        	xorl	%eax, %eax
    930e: e8 5d a1 ff ff               	callq	0x3470 <malloc@plt>
    9313: 48 85 c0                     	testq	%rax, %rax
    9316: 74 48                        	je	0x9360 <ivi_layout_transition_set_create+0x70>
    9318: 48 8d 78 08                  	leaq	0x8(%rax), %rdi
    931c: 48 89 c3                     	movq	%rax, %rbx
    931f: e8 1c a0 ff ff               	callq	0x3340 <wl_list_init@plt>
    9324: 48 8b 7d 10                  	movq	0x10(%rbp), %rdi
    9328: e8 93 a0 ff ff               	callq	0x33c0 <wl_display_get_event_loop@plt>
    932d: 48 8d 35 cc fa ff ff         	leaq	-0x534(%rip), %rsi      # 0x8e00 <layout_transition_frame>
    9334: 48 89 da                     	movq	%rbx, %rdx
    9337: 48 89 c7                     	movq	%rax, %rdi
    933a: e8 01 a3 ff ff               	callq	0x3640 <wl_event_loop_add_timer@plt>
    933f: 48 89 03                     	movq	%rax, (%rbx)
    9342: 48 89 d8                     	movq	%rbx, %rax
    9345: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    934a: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    9353: 75 24                        	jne	0x9379 <ivi_layout_transition_set_create+0x89>
    9355: 48 83 c4 18                  	addq	$0x18, %rsp
    9359: 5b                           	popq	%rbx
    935a: 5d                           	popq	%rbp
    935b: c3                           	retq
    935c: 0f 1f 40 00                  	nopl	(%rax)
    9360: 48 8d 35 99 46 00 00         	leaq	0x4699(%rip), %rsi      # 0xda00 <__func__.11687>
    9367: 31 c0                        	xorl	%eax, %eax
    9369: 48 8d 3d e8 44 00 00         	leaq	0x44e8(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    9370: e8 9b 9e ff ff               	callq	0x3210 <weston_log@plt>
    9375: 31 c0                        	xorl	%eax, %eax
    9377: eb cc                        	jmp	0x9345 <ivi_layout_transition_set_create+0x55>
    9379: e8 a2 9e ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    937e: 66 90                        	nop

0000000000009380 <ivi_layout_transition_move_resize_view>:
    9380: 41 57                        	pushq	%r15
    9382: 41 56                        	pushq	%r14
    9384: 41 55                        	pushq	%r13
    9386: 41 89 f5                     	movl	%esi, %r13d
    9389: 41 54                        	pushq	%r12
    938b: 55                           	pushq	%rbp
    938c: 48 89 fd                     	movq	%rdi, %rbp
    938f: 53                           	pushq	%rbx
    9390: 48 89 ee                     	movq	%rbp, %rsi
    9393: 44 89 cb                     	movl	%r9d, %ebx
    9396: 48 83 ec 38                  	subq	$0x38, %rsp
    939a: 44 8b bf f4 00 00 00         	movl	0xf4(%rdi), %r15d
    93a1: 8b 44 24 70                  	movl	0x70(%rsp), %eax
    93a5: 89 54 24 10                  	movl	%edx, 0x10(%rsp)
    93a9: 44 8b b7 f8 00 00 00         	movl	0xf8(%rdi), %r14d
    93b0: 89 4c 24 0c                  	movl	%ecx, 0xc(%rsp)
    93b4: 64 48 8b 14 25 28 00 00 00   	movq	%fs:0x28, %rdx
    93bd: 48 89 54 24 28               	movq	%rdx, 0x28(%rsp)
    93c2: 31 d2                        	xorl	%edx, %edx
    93c4: 44 8b a7 fc 00 00 00         	movl	0xfc(%rdi), %r12d
    93cb: 44 89 04 24                  	movl	%r8d, (%rsp)
    93cf: 8b bf 00 01 00 00            	movl	0x100(%rdi), %edi
    93d5: 89 44 24 18                  	movl	%eax, 0x18(%rsp)
    93d9: 89 7c 24 14                  	movl	%edi, 0x14(%rsp)
    93dd: 89 c7                        	movl	%eax, %edi
    93df: e8 2c f2 ff ff               	callq	0x8610 <get_transition_from_type_and_id>
    93e4: 44 8b 04 24                  	movl	(%rsp), %r8d
    93e8: 48 85 c0                     	testq	%rax, %rax
    93eb: 8b 4c 24 0c                  	movl	0xc(%rsp), %ecx
    93ef: 8b 54 24 10                  	movl	0x10(%rsp), %edx
    93f3: 74 5b                        	je	0x9450 <ivi_layout_transition_move_resize_view+0xd0>
    93f5: 48 8b 70 08                  	movq	0x8(%rax), %rsi
    93f9: c7 40 18 00 00 00 00         	movl	$0x0, 0x18(%rax)
    9400: 8b 7c 24 14                  	movl	0x14(%rsp), %edi
    9404: 89 58 1c                     	movl	%ebx, 0x1c(%rax)
    9407: 44 89 7e 08                  	movl	%r15d, 0x8(%rsi)
    940b: 44 89 76 0c                  	movl	%r14d, 0xc(%rsi)
    940f: 44 89 6e 10                  	movl	%r13d, 0x10(%rsi)
    9413: 89 56 14                     	movl	%edx, 0x14(%rsi)
    9416: 44 89 66 18                  	movl	%r12d, 0x18(%rsi)
    941a: 89 7e 1c                     	movl	%edi, 0x1c(%rsi)
    941d: 89 4e 20                     	movl	%ecx, 0x20(%rsi)
    9420: 44 89 46 24                  	movl	%r8d, 0x24(%rsi)
    9424: 48 8b 44 24 28               	movq	0x28(%rsp), %rax
    9429: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9432: 0f 85 14 01 00 00            	jne	0x954c <ivi_layout_transition_move_resize_view+0x1cc>
    9438: 48 83 c4 38                  	addq	$0x38, %rsp
    943c: 5b                           	popq	%rbx
    943d: 5d                           	popq	%rbp
    943e: 41 5c                        	popq	%r12
    9440: 41 5d                        	popq	%r13
    9442: 41 5e                        	popq	%r14
    9444: 41 5f                        	popq	%r15
    9446: c3                           	retq
    9447: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    9450: 44 89 44 24 1c               	movl	%r8d, 0x1c(%rsp)
    9455: 89 4c 24 10                  	movl	%ecx, 0x10(%rsp)
    9459: 89 54 24 0c                  	movl	%edx, 0xc(%rsp)
    945d: e8 fe f8 ff ff               	callq	0x8d60 <create_layout_transition>
    9462: 48 85 c0                     	testq	%rax, %rax
    9465: 48 89 04 24                  	movq	%rax, (%rsp)
    9469: 0f 84 d9 00 00 00            	je	0x9548 <ivi_layout_transition_move_resize_view+0x1c8>
    946f: bf 28 00 00 00               	movl	$0x28, %edi
    9474: e8 f7 9f ff ff               	callq	0x3470 <malloc@plt>
    9479: 4c 8b 0c 24                  	movq	(%rsp), %r9
    947d: 48 85 c0                     	testq	%rax, %rax
    9480: 8b 54 24 0c                  	movl	0xc(%rsp), %edx
    9484: 8b 4c 24 10                  	movl	0x10(%rsp), %ecx
    9488: 44 8b 44 24 1c               	movl	0x1c(%rsp), %r8d
    948d: 0f 84 96 00 00 00            	je	0x9529 <ivi_layout_transition_move_resize_view+0x1a9>
    9493: 8b 7c 24 18                  	movl	0x18(%rsp), %edi
    9497: 49 89 41 08                  	movq	%rax, 0x8(%r9)
    949b: 41 89 39                     	movl	%edi, (%r9)
    949e: 48 8d 3d 6b f0 ff ff         	leaq	-0xf95(%rip), %rdi      # 0x8510 <is_transition_move_resize_view_func>
    94a5: 49 89 79 28                  	movq	%rdi, 0x28(%r9)
    94a9: 48 8d 3d 20 f4 ff ff         	leaq	-0xbe0(%rip), %rdi      # 0x88d0 <transition_move_resize_view_user_frame>
    94b0: 49 89 79 30                  	movq	%rdi, 0x30(%r9)
    94b4: 48 8d 3d f5 f1 ff ff         	leaq	-0xe0b(%rip), %rdi      # 0x86b0 <transition_move_resize_view_destroy>
    94bb: 49 89 79 38                  	movq	%rdi, 0x38(%r9)
    94bf: 85 db                        	testl	%ebx, %ebx
    94c1: 74 04                        	je	0x94c7 <ivi_layout_transition_move_resize_view+0x147>
    94c3: 41 89 59 1c                  	movl	%ebx, 0x1c(%r9)
    94c7: 8b 5c 24 14                  	movl	0x14(%rsp), %ebx
    94cb: 4c 89 cf                     	movq	%r9, %rdi
    94ce: 48 89 28                     	movq	%rbp, (%rax)
    94d1: 44 89 78 08                  	movl	%r15d, 0x8(%rax)
    94d5: 44 89 70 0c                  	movl	%r14d, 0xc(%rax)
    94d9: 44 89 68 10                  	movl	%r13d, 0x10(%rax)
    94dd: 89 50 14                     	movl	%edx, 0x14(%rax)
    94e0: 44 89 60 18                  	movl	%r12d, 0x18(%rax)
    94e4: 89 58 1c                     	movl	%ebx, 0x1c(%rax)
    94e7: 89 48 20                     	movl	%ecx, 0x20(%rax)
    94ea: 44 89 40 24                  	movl	%r8d, 0x24(%rax)
    94ee: 4c 89 0c 24                  	movq	%r9, (%rsp)
    94f2: e8 69 fa ff ff               	callq	0x8f60 <layout_transition_register>
    94f7: 4c 8b 0c 24                  	movq	(%rsp), %r9
    94fb: 84 c0                        	testb	%al, %al
    94fd: 0f 85 21 ff ff ff            	jne	0x9424 <ivi_layout_transition_move_resize_view+0xa4>
    9503: 4c 89 cf                     	movq	%r9, %rdi
    9506: 48 8b 44 24 28               	movq	0x28(%rsp), %rax
    950b: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9514: 75 36                        	jne	0x954c <ivi_layout_transition_move_resize_view+0x1cc>
    9516: 48 83 c4 38                  	addq	$0x38, %rsp
    951a: 5b                           	popq	%rbx
    951b: 5d                           	popq	%rbp
    951c: 41 5c                        	popq	%r12
    951e: 41 5d                        	popq	%r13
    9520: 41 5e                        	popq	%r14
    9522: 41 5f                        	popq	%r15
    9524: e9 87 f2 ff ff               	jmp	0x87b0 <layout_transition_destroy>
    9529: 48 8d 3d 28 43 00 00         	leaq	0x4328(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    9530: 48 8d 35 89 44 00 00         	leaq	0x4489(%rip), %rsi      # 0xd9c0 <__func__.11758>
    9537: e8 d4 9c ff ff               	callq	0x3210 <weston_log@plt>
    953c: 4c 8b 0c 24                  	movq	(%rsp), %r9
    9540: 4c 89 cf                     	movq	%r9, %rdi
    9543: e8 28 9b ff ff               	callq	0x3070 <free@plt>
    9548: 31 ff                        	xorl	%edi, %edi
    954a: eb ba                        	jmp	0x9506 <ivi_layout_transition_move_resize_view+0x186>
    954c: e8 cf 9c ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9551: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    9556: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000009560 <ivi_layout_transition_visibility_on>:
    9560: 41 56                        	pushq	%r14
    9562: 41 55                        	pushq	%r13
    9564: 41 54                        	pushq	%r12
    9566: 41 89 f4                     	movl	%esi, %r12d
    9569: 55                           	pushq	%rbp
    956a: 53                           	pushq	%rbx
    956b: 48 89 fb                     	movq	%rdi, %rbx
    956e: 48 83 ec 10                  	subq	$0x10, %rsp
    9572: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    957b: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9580: 31 c0                        	xorl	%eax, %eax
    9582: e8 c9 a9 ff ff               	callq	0x3f50 <ivi_layout_surface_get_visibility>
    9587: 48 89 df                     	movq	%rbx, %rdi
    958a: 41 89 c5                     	movl	%eax, %r13d
    958d: e8 8e aa ff ff               	callq	0x4020 <ivi_layout_surface_get_opacity>
    9592: 48 89 de                     	movq	%rbx, %rsi
    9595: bf 09 00 00 00               	movl	$0x9, %edi
    959a: 4c 63 f0                     	movslq	%eax, %r14
    959d: e8 6e f0 ff ff               	callq	0x8610 <get_transition_from_type_and_id>
    95a2: 48 85 c0                     	testq	%rax, %rax
    95a5: 74 79                        	je	0x9620 <ivi_layout_transition_visibility_on+0xc0>
    95a7: 48 89 df                     	movq	%rbx, %rdi
    95aa: 48 89 c5                     	movq	%rax, %rbp
    95ad: e8 6e aa ff ff               	callq	0x4020 <ivi_layout_surface_get_opacity>
    95b2: 48 8b 75 10                  	movq	0x10(%rbp), %rsi
    95b6: 44 89 65 1c                  	movl	%r12d, 0x1c(%rbp)
    95ba: 48 8d 15 5f f4 ff ff         	leaq	-0xba1(%rip), %rdx      # 0x8a20 <visibility_on_transition_destroy>
    95c1: 48 89 55 38                  	movq	%rdx, 0x38(%rbp)
    95c5: 48 98                        	cltq
    95c7: 48 8b 4d 08                  	movq	0x8(%rbp), %rcx
    95cb: 48 ba 00 00 00 00 00 00 b8 42	movabsq	$0x42b8000000000000, %rdx # imm = 0x42B8000000000000
    95d5: 48 01 d0                     	addq	%rdx, %rax
    95d8: c7 45 18 00 00 00 00         	movl	$0x0, 0x18(%rbp)
    95df: 66 48 0f 6e c0               	movq	%rax, %xmm0
    95e4: f2 0f 5c 05 64 42 00 00      	subsd	0x4264(%rip), %xmm0     # 0xd850 <__func__.12894+0x40>
    95ec: f2 0f 11 41 08               	movsd	%xmm0, 0x8(%rcx)
    95f1: f2 0f 10 06                  	movsd	(%rsi), %xmm0
    95f5: f2 0f 11 41 10               	movsd	%xmm0, 0x10(%rcx)
    95fa: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    95ff: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9608: 0f 85 bf 00 00 00            	jne	0x96cd <ivi_layout_transition_visibility_on+0x16d>
    960e: 48 83 c4 10                  	addq	$0x10, %rsp
    9612: 5b                           	popq	%rbx
    9613: 5d                           	popq	%rbp
    9614: 41 5c                        	popq	%r12
    9616: 41 5d                        	popq	%r13
    9618: 41 5e                        	popq	%r14
    961a: c3                           	retq
    961b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    9620: 45 84 ed                     	testb	%r13b, %r13b
    9623: 75 d5                        	jne	0x95fa <ivi_layout_transition_visibility_on+0x9a>
    9625: 8b 83 80 01 00 00            	movl	0x180(%rbx), %eax
    962b: 85 c0                        	testl	%eax, %eax
    962d: 75 cb                        	jne	0x95fa <ivi_layout_transition_visibility_on+0x9a>
    962f: bf 08 00 00 00               	movl	$0x8, %edi
    9634: e8 37 9e ff ff               	callq	0x3470 <malloc@plt>
    9639: 48 85 c0                     	testq	%rax, %rax
    963c: 74 5e                        	je	0x969c <ivi_layout_transition_visibility_on+0x13c>
    963e: 48 ba 00 00 00 00 00 00 b8 42	movabsq	$0x42b8000000000000, %rdx # imm = 0x42B8000000000000
    9648: 48 89 c6                     	movq	%rax, %rsi
    964b: 48 89 df                     	movq	%rbx, %rdi
    964e: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    9652: 49 8d 0c 16                  	leaq	(%r14,%rdx), %rcx
    9656: 48 8d 15 c3 f3 ff ff         	leaq	-0xc3d(%rip), %rdx      # 0x8a20 <visibility_on_transition_destroy>
    965d: 66 48 0f 6e c9               	movq	%rcx, %xmm1
    9662: 44 89 e1                     	movl	%r12d, %ecx
    9665: f2 0f 5c 0d e3 41 00 00      	subsd	0x41e3(%rip), %xmm1     # 0xd850 <__func__.12894+0x40>
    966d: f2 0f 11 08                  	movsd	%xmm1, (%rax)
    9671: e8 6a f9 ff ff               	callq	0x8fe0 <create_visibility_transition>
    9676: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    967b: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9684: 75 47                        	jne	0x96cd <ivi_layout_transition_visibility_on+0x16d>
    9686: 48 83 c4 10                  	addq	$0x10, %rsp
    968a: 48 89 df                     	movq	%rbx, %rdi
    968d: 31 f6                        	xorl	%esi, %esi
    968f: 5b                           	popq	%rbx
    9690: 5d                           	popq	%rbp
    9691: 41 5c                        	popq	%r12
    9693: 41 5d                        	popq	%r13
    9695: 41 5e                        	popq	%r14
    9697: e9 04 a9 ff ff               	jmp	0x3fa0 <ivi_layout_surface_set_opacity>
    969c: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    96a1: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    96aa: 75 21                        	jne	0x96cd <ivi_layout_transition_visibility_on+0x16d>
    96ac: 48 8d 35 8d 42 00 00         	leaq	0x428d(%rip), %rsi      # 0xd940 <__func__.11825>
    96b3: 48 83 c4 10                  	addq	$0x10, %rsp
    96b7: 31 c0                        	xorl	%eax, %eax
    96b9: 5b                           	popq	%rbx
    96ba: 48 8d 3d 97 41 00 00         	leaq	0x4197(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    96c1: 5d                           	popq	%rbp
    96c2: 41 5c                        	popq	%r12
    96c4: 41 5d                        	popq	%r13
    96c6: 41 5e                        	popq	%r14
    96c8: e9 43 9b ff ff               	jmp	0x3210 <weston_log@plt>
    96cd: e8 4e 9b ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    96d2: 0f 1f 40 00                  	nopl	(%rax)
    96d6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

00000000000096e0 <ivi_layout_transition_visibility_off>:
    96e0: 41 55                        	pushq	%r13
    96e2: 41 54                        	pushq	%r12
    96e4: 41 89 f4                     	movl	%esi, %r12d
    96e7: 55                           	pushq	%rbp
    96e8: 53                           	pushq	%rbx
    96e9: 48 89 fb                     	movq	%rdi, %rbx
    96ec: 48 83 ec 18                  	subq	$0x18, %rsp
    96f0: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    96f9: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    96fe: 31 c0                        	xorl	%eax, %eax
    9700: e8 1b a9 ff ff               	callq	0x4020 <ivi_layout_surface_get_opacity>
    9705: 48 89 df                     	movq	%rbx, %rdi
    9708: 48 63 e8                     	movslq	%eax, %rbp
    970b: e8 40 a8 ff ff               	callq	0x3f50 <ivi_layout_surface_get_visibility>
    9710: 48 89 de                     	movq	%rbx, %rsi
    9713: bf 09 00 00 00               	movl	$0x9, %edi
    9718: 41 89 c5                     	movl	%eax, %r13d
    971b: e8 f0 ee ff ff               	callq	0x8610 <get_transition_from_type_and_id>
    9720: 48 85 c0                     	testq	%rax, %rax
    9723: 74 6b                        	je	0x9790 <ivi_layout_transition_visibility_off+0xb0>
    9725: 48 8d 15 14 f4 ff ff         	leaq	-0xbec(%rip), %rdx      # 0x8b40 <visibility_off_transition_destroy>
    972c: 48 8b 48 08                  	movq	0x8(%rax), %rcx
    9730: c7 40 18 00 00 00 00         	movl	$0x0, 0x18(%rax)
    9737: 48 89 50 38                  	movq	%rdx, 0x38(%rax)
    973b: 48 ba 00 00 00 00 00 00 b8 42	movabsq	$0x42b8000000000000, %rdx # imm = 0x42B8000000000000
    9745: 44 89 60 1c                  	movl	%r12d, 0x1c(%rax)
    9749: 48 8d 44 15 00               	leaq	(%rbp,%rdx), %rax
    974e: 66 48 0f 6e c0               	movq	%rax, %xmm0
    9753: f2 0f 5c 05 f5 40 00 00      	subsd	0x40f5(%rip), %xmm0     # 0xd850 <__func__.12894+0x40>
    975b: 48 c7 41 10 00 00 00 00      	movq	$0x0, 0x10(%rcx)
    9763: f2 0f 11 41 08               	movsd	%xmm0, 0x8(%rcx)
    9768: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    976d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9776: 0f 85 99 00 00 00            	jne	0x9815 <ivi_layout_transition_visibility_off+0x135>
    977c: 48 83 c4 18                  	addq	$0x18, %rsp
    9780: 5b                           	popq	%rbx
    9781: 5d                           	popq	%rbp
    9782: 41 5c                        	popq	%r12
    9784: 41 5d                        	popq	%r13
    9786: c3                           	retq
    9787: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    9790: 45 84 ed                     	testb	%r13b, %r13b
    9793: 74 d3                        	je	0x9768 <ivi_layout_transition_visibility_off+0x88>
    9795: bf 08 00 00 00               	movl	$0x8, %edi
    979a: e8 d1 9c ff ff               	callq	0x3470 <malloc@plt>
    979f: 48 85 c0                     	testq	%rax, %rax
    97a2: 74 42                        	je	0x97e6 <ivi_layout_transition_visibility_off+0x106>
    97a4: 48 ba 00 00 00 00 00 00 b8 42	movabsq	$0x42b8000000000000, %rdx # imm = 0x42B8000000000000
    97ae: 44 89 e1                     	movl	%r12d, %ecx
    97b1: 48 89 df                     	movq	%rbx, %rdi
    97b4: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    97b8: 48 8d 74 15 00               	leaq	(%rbp,%rdx), %rsi
    97bd: 48 8d 15 7c f3 ff ff         	leaq	-0xc84(%rip), %rdx      # 0x8b40 <visibility_off_transition_destroy>
    97c4: 66 48 0f 6e c6               	movq	%rsi, %xmm0
    97c9: 48 89 c6                     	movq	%rax, %rsi
    97cc: f2 0f 5c 05 7c 40 00 00      	subsd	0x407c(%rip), %xmm0     # 0xd850 <__func__.12894+0x40>
    97d4: f2 0f 11 00                  	movsd	%xmm0, (%rax)
    97d8: e8 03 f8 ff ff               	callq	0x8fe0 <create_visibility_transition>
    97dd: c6 83 18 01 00 00 01         	movb	$0x1, 0x118(%rbx)
    97e4: eb 82                        	jmp	0x9768 <ivi_layout_transition_visibility_off+0x88>
    97e6: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    97eb: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    97f4: 75 1f                        	jne	0x9815 <ivi_layout_transition_visibility_off+0x135>
    97f6: 48 8d 35 e3 40 00 00         	leaq	0x40e3(%rip), %rsi      # 0xd8e0 <__func__.11840>
    97fd: 48 83 c4 18                  	addq	$0x18, %rsp
    9801: 31 c0                        	xorl	%eax, %eax
    9803: 5b                           	popq	%rbx
    9804: 48 8d 3d 4d 40 00 00         	leaq	0x404d(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    980b: 5d                           	popq	%rbp
    980c: 41 5c                        	popq	%r12
    980e: 41 5d                        	popq	%r13
    9810: e9 fb 99 ff ff               	jmp	0x3210 <weston_log@plt>
    9815: e8 06 9a ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    981a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000009820 <ivi_layout_transition_move_layer>:
    9820: 41 57                        	pushq	%r15
    9822: 41 56                        	pushq	%r14
    9824: 41 55                        	pushq	%r13
    9826: 41 89 f5                     	movl	%esi, %r13d
    9829: 41 54                        	pushq	%r12
    982b: 41 89 d4                     	movl	%edx, %r12d
    982e: 55                           	pushq	%rbp
    982f: 89 cd                        	movl	%ecx, %ebp
    9831: 53                           	pushq	%rbx
    9832: 48 89 fb                     	movq	%rdi, %rbx
    9835: 48 83 ec 28                  	subq	$0x28, %rsp
    9839: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9842: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    9847: 31 c0                        	xorl	%eax, %eax
    9849: 48 8d 74 24 10               	leaq	0x10(%rsp), %rsi
    984e: c7 44 24 10 00 00 00 00      	movl	$0x0, 0x10(%rsp)
    9856: 48 8d 54 24 14               	leaq	0x14(%rsp), %rdx
    985b: c7 44 24 14 00 00 00 00      	movl	$0x0, 0x14(%rsp)
    9863: e8 78 a5 ff ff               	callq	0x3de0 <ivi_layout_layer_get_position>
    9868: 48 89 de                     	movq	%rbx, %rsi
    986b: bf 05 00 00 00               	movl	$0x5, %edi
    9870: e8 9b ed ff ff               	callq	0x8610 <get_transition_from_type_and_id>
    9875: 48 85 c0                     	testq	%rax, %rax
    9878: 74 4e                        	je	0x98c8 <ivi_layout_transition_move_layer+0xa8>
    987a: 48 8b 50 08                  	movq	0x8(%rax), %rdx
    987e: c7 40 18 00 00 00 00         	movl	$0x0, 0x18(%rax)
    9885: 89 68 1c                     	movl	%ebp, 0x1c(%rax)
    9888: 8b 44 24 10                  	movl	0x10(%rsp), %eax
    988c: 44 89 6a 10                  	movl	%r13d, 0x10(%rdx)
    9890: 89 42 08                     	movl	%eax, 0x8(%rdx)
    9893: 8b 44 24 14                  	movl	0x14(%rsp), %eax
    9897: 44 89 62 14                  	movl	%r12d, 0x14(%rdx)
    989b: 89 42 0c                     	movl	%eax, 0xc(%rdx)
    989e: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    98a3: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    98ac: 0f 85 d9 00 00 00            	jne	0x998b <ivi_layout_transition_move_layer+0x16b>
    98b2: 48 83 c4 28                  	addq	$0x28, %rsp
    98b6: 5b                           	popq	%rbx
    98b7: 5d                           	popq	%rbp
    98b8: 41 5c                        	popq	%r12
    98ba: 41 5d                        	popq	%r13
    98bc: 41 5e                        	popq	%r14
    98be: 41 5f                        	popq	%r15
    98c0: c3                           	retq
    98c1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    98c8: 8b 44 24 14                  	movl	0x14(%rsp), %eax
    98cc: 44 8b 7c 24 10               	movl	0x10(%rsp), %r15d
    98d1: 89 44 24 0c                  	movl	%eax, 0xc(%rsp)
    98d5: e8 86 f4 ff ff               	callq	0x8d60 <create_layout_transition>
    98da: 49 89 c6                     	movq	%rax, %r14
    98dd: 48 85 c0                     	testq	%rax, %rax
    98e0: 0f 84 a1 00 00 00            	je	0x9987 <ivi_layout_transition_move_layer+0x167>
    98e6: bf 20 00 00 00               	movl	$0x20, %edi
    98eb: e8 80 9b ff ff               	callq	0x3470 <malloc@plt>
    98f0: 48 85 c0                     	testq	%rax, %rax
    98f3: 74 77                        	je	0x996c <ivi_layout_transition_move_layer+0x14c>
    98f5: 48 8d 0d 94 ec ff ff         	leaq	-0x136c(%rip), %rcx     # 0x8590 <is_transition_move_layer_func>
    98fc: 41 c7 06 05 00 00 00         	movl	$0x5, (%r14)
    9903: 49 89 4e 28                  	movq	%rcx, 0x28(%r14)
    9907: 48 8d 0d c2 f2 ff ff         	leaq	-0xd3e(%rip), %rcx      # 0x8bd0 <transition_move_layer_user_frame>
    990e: 49 89 4e 30                  	movq	%rcx, 0x30(%r14)
    9912: 48 8d 0d e7 ed ff ff         	leaq	-0x1219(%rip), %rcx     # 0x8700 <transition_move_layer_destroy>
    9919: 49 89 4e 38                  	movq	%rcx, 0x38(%r14)
    991d: 49 89 46 08                  	movq	%rax, 0x8(%r14)
    9921: 49 c7 46 10 00 00 00 00      	movq	$0x0, 0x10(%r14)
    9929: 85 ed                        	testl	%ebp, %ebp
    992b: 74 04                        	je	0x9931 <ivi_layout_transition_move_layer+0x111>
    992d: 41 89 6e 1c                  	movl	%ebp, 0x1c(%r14)
    9931: 8b 4c 24 0c                  	movl	0xc(%rsp), %ecx
    9935: 48 89 18                     	movq	%rbx, (%rax)
    9938: 4c 89 f7                     	movq	%r14, %rdi
    993b: 44 89 78 08                  	movl	%r15d, 0x8(%rax)
    993f: 44 89 68 10                  	movl	%r13d, 0x10(%rax)
    9943: 44 89 60 14                  	movl	%r12d, 0x14(%rax)
    9947: 89 48 0c                     	movl	%ecx, 0xc(%rax)
    994a: 48 c7 40 18 00 00 00 00      	movq	$0x0, 0x18(%rax)
    9952: e8 09 f6 ff ff               	callq	0x8f60 <layout_transition_register>
    9957: 84 c0                        	testb	%al, %al
    9959: 0f 85 3f ff ff ff            	jne	0x989e <ivi_layout_transition_move_layer+0x7e>
    995f: 4c 89 f7                     	movq	%r14, %rdi
    9962: e8 09 97 ff ff               	callq	0x3070 <free@plt>
    9967: e9 32 ff ff ff               	jmp	0x989e <ivi_layout_transition_move_layer+0x7e>
    996c: 48 8d 3d e5 3e 00 00         	leaq	0x3ee5(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    9973: 48 8d 35 36 3f 00 00         	leaq	0x3f36(%rip), %rsi      # 0xd8b0 <__func__.11876>
    997a: e8 91 98 ff ff               	callq	0x3210 <weston_log@plt>
    997f: 4c 89 f7                     	movq	%r14, %rdi
    9982: e8 e9 96 ff ff               	callq	0x3070 <free@plt>
    9987: 31 ff                        	xorl	%edi, %edi
    9989: eb d7                        	jmp	0x9962 <ivi_layout_transition_move_layer+0x142>
    998b: e8 90 98 ff ff               	callq	0x3220 <__stack_chk_fail@plt>

0000000000009990 <ivi_layout_transition_move_layer_cancel>:
    9990: 48 83 ec 18                  	subq	$0x18, %rsp
    9994: 48 89 fe                     	movq	%rdi, %rsi
    9997: bf 05 00 00 00               	movl	$0x5, %edi
    999c: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    99a5: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    99aa: 31 c0                        	xorl	%eax, %eax
    99ac: e8 5f ec ff ff               	callq	0x8610 <get_transition_from_type_and_id>
    99b1: 48 85 c0                     	testq	%rax, %rax
    99b4: 74 22                        	je	0x99d8 <ivi_layout_transition_move_layer_cancel+0x48>
    99b6: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    99bb: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    99c4: 75 27                        	jne	0x99ed <ivi_layout_transition_move_layer_cancel+0x5d>
    99c6: 48 89 c7                     	movq	%rax, %rdi
    99c9: 48 83 c4 18                  	addq	$0x18, %rsp
    99cd: e9 de ed ff ff               	jmp	0x87b0 <layout_transition_destroy>
    99d2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    99d8: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    99dd: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    99e6: 75 05                        	jne	0x99ed <ivi_layout_transition_move_layer_cancel+0x5d>
    99e8: 48 83 c4 18                  	addq	$0x18, %rsp
    99ec: c3                           	retq
    99ed: e8 2e 98 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    99f2: 0f 1f 40 00                  	nopl	(%rax)
    99f6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000009a00 <ivi_layout_transition_fade_layer>:
    9a00: 41 57                        	pushq	%r15
    9a02: 41 56                        	pushq	%r14
    9a04: 49 89 d6                     	movq	%rdx, %r14
    9a07: 41 55                        	pushq	%r13
    9a09: 49 89 cd                     	movq	%rcx, %r13
    9a0c: 41 54                        	pushq	%r12
    9a0e: 41 89 f4                     	movl	%esi, %r12d
    9a11: 48 89 fe                     	movq	%rdi, %rsi
    9a14: 55                           	pushq	%rbp
    9a15: 48 89 fd                     	movq	%rdi, %rbp
    9a18: bf 04 00 00 00               	movl	$0x4, %edi
    9a1d: 53                           	pushq	%rbx
    9a1e: 44 89 c3                     	movl	%r8d, %ebx
    9a21: 48 83 ec 28                  	subq	$0x28, %rsp
    9a25: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9a2e: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    9a33: 31 c0                        	xorl	%eax, %eax
    9a35: f2 0f 11 44 24 08            	movsd	%xmm0, 0x8(%rsp)
    9a3b: f2 0f 11 0c 24               	movsd	%xmm1, (%rsp)
    9a40: e8 cb eb ff ff               	callq	0x8610 <get_transition_from_type_and_id>
    9a45: f2 0f 10 0c 24               	movsd	(%rsp), %xmm1
    9a4a: 48 85 c0                     	testq	%rax, %rax
    9a4d: f2 0f 10 44 24 08            	movsd	0x8(%rsp), %xmm0
    9a53: 0f 84 a7 00 00 00            	je	0x9b00 <ivi_layout_transition_fade_layer+0x100>
    9a59: 48 89 ef                     	movq	%rbp, %rdi
    9a5c: 4c 8b 68 08                  	movq	0x8(%rax), %r13
    9a60: 49 89 c7                     	movq	%rax, %r15
    9a63: e8 28 a3 ff ff               	callq	0x3d90 <ivi_layout_layer_get_opacity>
    9a68: f2 0f 10 0c 24               	movsd	(%rsp), %xmm1
    9a6d: 48 ba 00 00 00 00 00 00 b8 42	movabsq	$0x42b8000000000000, %rdx # imm = 0x42B8000000000000
    9a77: 48 98                        	cltq
    9a79: 48 01 d0                     	addq	%rdx, %rax
    9a7c: 66 48 0f 6e c0               	movq	%rax, %xmm0
    9a81: 45 89 65 08                  	movl	%r12d, 0x8(%r13)
    9a85: f2 0f 5c 05 c3 3d 00 00      	subsd	0x3dc3(%rip), %xmm0     # 0xd850 <__func__.12894+0x40>
    9a8d: f2 41 0f 11 4d 18            	movsd	%xmm1, 0x18(%r13)
    9a93: f2 41 0f 11 45 10            	movsd	%xmm0, 0x10(%r13)
    9a99: 45 85 e4                     	testl	%r12d, %r12d
    9a9c: 74 10                        	je	0x9aae <ivi_layout_transition_fade_layer+0xae>
    9a9e: f2 0f 10 0d 9a 3f 00 00      	movsd	0x3f9a(%rip), %xmm1     # 0xda40 <__func__.11687+0x40>
    9aa6: f2 0f 5c c8                  	subsd	%xmm0, %xmm1
    9aaa: 66 0f 28 c1                  	movapd	%xmm1, %xmm0
    9aae: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    9ab2: f2 48 0f 2a cb               	cvtsi2sd	%rbx, %xmm1
    9ab7: 41 c7 47 18 00 00 00 00      	movl	$0x0, 0x18(%r15)
    9abf: 41 c7 47 20 00 00 00 00      	movl	$0x0, 0x20(%r15)
    9ac7: f2 0f 59 c1                  	mulsd	%xmm1, %xmm0
    9acb: f2 48 0f 2c c0               	cvttsd2si	%xmm0, %rax
    9ad0: 41 89 47 1c                  	movl	%eax, 0x1c(%r15)
    9ad4: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    9ad9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9ae2: 0f 85 0a 01 00 00            	jne	0x9bf2 <ivi_layout_transition_fade_layer+0x1f2>
    9ae8: 48 83 c4 28                  	addq	$0x28, %rsp
    9aec: 5b                           	popq	%rbx
    9aed: 5d                           	popq	%rbp
    9aee: 41 5c                        	popq	%r12
    9af0: 41 5d                        	popq	%r13
    9af2: 41 5e                        	popq	%r14
    9af4: 41 5f                        	popq	%r15
    9af6: c3                           	retq
    9af7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    9b00: f2 0f 11 4c 24 08            	movsd	%xmm1, 0x8(%rsp)
    9b06: f2 0f 11 04 24               	movsd	%xmm0, (%rsp)
    9b0b: e8 50 f2 ff ff               	callq	0x8d60 <create_layout_transition>
    9b10: 49 89 c7                     	movq	%rax, %r15
    9b13: 48 85 c0                     	testq	%rax, %rax
    9b16: 74 bc                        	je	0x9ad4 <ivi_layout_transition_fade_layer+0xd4>
    9b18: bf 28 00 00 00               	movl	$0x28, %edi
    9b1d: e8 4e 99 ff ff               	callq	0x3470 <malloc@plt>
    9b22: f2 0f 10 04 24               	movsd	(%rsp), %xmm0
    9b27: 48 85 c0                     	testq	%rax, %rax
    9b2a: f2 0f 10 4c 24 08            	movsd	0x8(%rsp), %xmm1
    9b30: 0f 84 83 00 00 00            	je	0x9bb9 <ivi_layout_transition_fade_layer+0x1b9>
    9b36: 48 8d 0d 93 ea ff ff         	leaq	-0x156d(%rip), %rcx     # 0x85d0 <is_transition_fade_layer_func>
    9b3d: 41 c7 07 04 00 00 00         	movl	$0x4, (%r15)
    9b44: 49 89 4f 28                  	movq	%rcx, 0x28(%r15)
    9b48: 48 8d 0d 41 f1 ff ff         	leaq	-0xebf(%rip), %rcx      # 0x8c90 <transition_fade_layer_user_frame>
    9b4f: 49 89 4f 30                  	movq	%rcx, 0x30(%r15)
    9b53: 48 8d 0d 06 ec ff ff         	leaq	-0x13fa(%rip), %rcx     # 0x8760 <transition_fade_layer_destroy>
    9b5a: 49 89 47 08                  	movq	%rax, 0x8(%r15)
    9b5e: 4d 89 77 10                  	movq	%r14, 0x10(%r15)
    9b62: 49 89 4f 38                  	movq	%rcx, 0x38(%r15)
    9b66: 85 db                        	testl	%ebx, %ebx
    9b68: 74 04                        	je	0x9b6e <ivi_layout_transition_fade_layer+0x16e>
    9b6a: 41 89 5f 1c                  	movl	%ebx, 0x1c(%r15)
    9b6e: 48 89 28                     	movq	%rbp, (%rax)
    9b71: 4c 89 ff                     	movq	%r15, %rdi
    9b74: 44 89 60 08                  	movl	%r12d, 0x8(%rax)
    9b78: f2 0f 11 40 10               	movsd	%xmm0, 0x10(%rax)
    9b7d: f2 0f 11 48 18               	movsd	%xmm1, 0x18(%rax)
    9b82: 4c 89 68 20                  	movq	%r13, 0x20(%rax)
    9b86: e8 d5 f3 ff ff               	callq	0x8f60 <layout_transition_register>
    9b8b: 84 c0                        	testb	%al, %al
    9b8d: 0f 85 41 ff ff ff            	jne	0x9ad4 <ivi_layout_transition_fade_layer+0xd4>
    9b93: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    9b98: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9ba1: 75 4f                        	jne	0x9bf2 <ivi_layout_transition_fade_layer+0x1f2>
    9ba3: 48 83 c4 28                  	addq	$0x28, %rsp
    9ba7: 4c 89 ff                     	movq	%r15, %rdi
    9baa: 5b                           	popq	%rbx
    9bab: 5d                           	popq	%rbp
    9bac: 41 5c                        	popq	%r12
    9bae: 41 5d                        	popq	%r13
    9bb0: 41 5e                        	popq	%r14
    9bb2: 41 5f                        	popq	%r15
    9bb4: e9 f7 eb ff ff               	jmp	0x87b0 <layout_transition_destroy>
    9bb9: 48 8d 35 c0 3c 00 00         	leaq	0x3cc0(%rip), %rsi      # 0xd880 <__func__.11928>
    9bc0: 48 8d 3d 91 3c 00 00         	leaq	0x3c91(%rip), %rdi      # 0xd858 <__func__.12894+0x48>
    9bc7: e8 44 96 ff ff               	callq	0x3210 <weston_log@plt>
    9bcc: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    9bd1: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9bda: 75 16                        	jne	0x9bf2 <ivi_layout_transition_fade_layer+0x1f2>
    9bdc: 48 83 c4 28                  	addq	$0x28, %rsp
    9be0: 4c 89 ff                     	movq	%r15, %rdi
    9be3: 5b                           	popq	%rbx
    9be4: 5d                           	popq	%rbp
    9be5: 41 5c                        	popq	%r12
    9be7: 41 5d                        	popq	%r13
    9be9: 41 5e                        	popq	%r14
    9beb: 41 5f                        	popq	%r15
    9bed: e9 7e 94 ff ff               	jmp	0x3070 <free@plt>
    9bf2: e8 29 96 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9bf7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000009c00 <ivi_shell_surface_configure>:
    9c00: 53                           	pushq	%rbx
    9c01: 48 83 ec 10                  	subq	$0x10, %rsp
    9c05: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9c0e: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9c13: 31 c0                        	xorl	%eax, %eax
    9c15: 48 8b 05 ac 73 20 00         	movq	0x2073ac(%rip), %rax    # 0x210fc8 <_GLOBAL_OFFSET_TABLE_+0x3b0>
    9c1c: 48 39 87 80 02 00 00         	cmpq	%rax, 0x280(%rdi)
    9c23: 74 1b                        	je	0x9c40 <ivi_shell_surface_configure+0x40>
    9c25: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    9c2a: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9c33: 75 6b                        	jne	0x9ca0 <ivi_shell_surface_configure+0xa0>
    9c35: 48 83 c4 10                  	addq	$0x10, %rsp
    9c39: 5b                           	popq	%rbx
    9c3a: c3                           	retq
    9c3b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    9c40: 48 8b 9f 88 02 00 00         	movq	0x288(%rdi), %rbx
    9c47: 48 85 db                     	testq	%rbx, %rbx
    9c4a: 74 d9                        	je	0x9c25 <ivi_shell_surface_configure+0x25>
    9c4c: 8b 77 68                     	movl	0x68(%rdi), %esi
    9c4f: 39 73 3c                     	cmpl	%esi, 0x3c(%rbx)
    9c52: 8b 57 6c                     	movl	0x6c(%rdi), %edx
    9c55: 75 05                        	jne	0x9c5c <ivi_shell_surface_configure+0x5c>
    9c57: 39 53 40                     	cmpl	%edx, 0x40(%rbx)
    9c5a: 74 c9                        	je	0x9c25 <ivi_shell_surface_configure+0x25>
    9c5c: 48 8b 7b 10                  	movq	0x10(%rbx), %rdi
    9c60: 89 73 3c                     	movl	%esi, 0x3c(%rbx)
    9c63: 89 53 40                     	movl	%edx, 0x40(%rbx)
    9c66: e8 35 e5 ff ff               	callq	0x81a0 <ivi_layout_surface_configure>
    9c6b: 8b 43 70                     	movl	0x70(%rbx), %eax
    9c6e: 85 c0                        	testl	%eax, %eax
    9c70: 75 b3                        	jne	0x9c25 <ivi_shell_surface_configure+0x25>
    9c72: 48 8b 43 10                  	movq	0x10(%rbx), %rax
    9c76: 80 b8 d0 00 00 00 00         	cmpb	$0x0, 0xd0(%rax)
    9c7d: 74 11                        	je	0x9c90 <ivi_shell_surface_configure+0x90>
    9c7f: c7 43 70 01 00 00 00         	movl	$0x1, 0x70(%rbx)
    9c86: eb 9d                        	jmp	0x9c25 <ivi_shell_surface_configure+0x25>
    9c88: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    9c90: 48 8b 3b                     	movq	(%rbx), %rdi
    9c93: 31 d2                        	xorl	%edx, %edx
    9c95: 31 f6                        	xorl	%esi, %esi
    9c97: 31 c0                        	xorl	%eax, %eax
    9c99: e8 c2 98 ff ff               	callq	0x3560 <wl_resource_post_event@plt>
    9c9e: eb df                        	jmp	0x9c7f <ivi_shell_surface_configure+0x7f>
    9ca0: e8 7b 95 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9ca5: 90                           	nop
    9ca6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000009cb0 <bind_ivi_application>:
    9cb0: 53                           	pushq	%rbx
    9cb1: 48 89 f3                     	movq	%rsi, %rbx
    9cb4: ba 01 00 00 00               	movl	$0x1, %edx
    9cb9: 48 83 ec 10                  	subq	$0x10, %rsp
    9cbd: 48 8b 35 dc 72 20 00         	movq	0x2072dc(%rip), %rsi    # 0x210fa0 <_GLOBAL_OFFSET_TABLE_+0x388>
    9cc4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9ccd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9cd2: 31 c0                        	xorl	%eax, %eax
    9cd4: e8 b7 94 ff ff               	callq	0x3190 <wl_resource_create@plt>
    9cd9: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    9cde: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    9ce7: 75 19                        	jne	0x9d02 <bind_ivi_application+0x52>
    9ce9: 48 83 c4 10                  	addq	$0x10, %rsp
    9ced: 48 89 da                     	movq	%rbx, %rdx
    9cf0: 31 c9                        	xorl	%ecx, %ecx
    9cf2: 5b                           	popq	%rbx
    9cf3: 48 8d 35 c6 6b 20 00         	leaq	0x206bc6(%rip), %rsi    # 0x2108c0 <application_implementation>
    9cfa: 48 89 c7                     	movq	%rax, %rdi
    9cfd: e9 de 95 ff ff               	jmp	0x32e0 <wl_resource_set_implementation@plt>
    9d02: e8 19 95 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9d07: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

0000000000009d10 <surface_destroy>:
    9d10: 48 83 ec 18                  	subq	$0x18, %rsp
    9d14: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9d1d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9d22: 31 c0                        	xorl	%eax, %eax
    9d24: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    9d29: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9d32: 75 0c                        	jne	0x9d40 <surface_destroy+0x30>
    9d34: 48 89 f7                     	movq	%rsi, %rdi
    9d37: 48 83 c4 18                  	addq	$0x18, %rsp
    9d3b: e9 00 95 ff ff               	jmp	0x3240 <wl_resource_destroy@plt>
    9d40: e8 db 94 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9d45: 90                           	nop
    9d46: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

0000000000009d50 <surface_configure_notify>:
    9d50: 55                           	pushq	%rbp
    9d51: 48 89 fd                     	movq	%rdi, %rbp
    9d54: 53                           	pushq	%rbx
    9d55: 48 89 f3                     	movq	%rsi, %rbx
    9d58: 48 83 ec 18                  	subq	$0x18, %rsp
    9d5c: 8b 96 84 01 00 00            	movl	0x184(%rsi), %edx
    9d62: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9d6b: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9d70: 31 c0                        	xorl	%eax, %eax
    9d72: 85 d2                        	testl	%edx, %edx
    9d74: 74 4a                        	je	0x9dc0 <surface_configure_notify+0x70>
    9d76: 48 8b 7f a8                  	movq	-0x58(%rdi), %rdi
    9d7a: 48 85 ff                     	testq	%rdi, %rdi
    9d7d: 74 41                        	je	0x9dc0 <surface_configure_notify+0x70>
    9d7f: 8b 8e 7c 01 00 00            	movl	0x17c(%rsi), %ecx
    9d85: 8b 96 78 01 00 00            	movl	0x178(%rsi), %edx
    9d8b: be 01 00 00 00               	movl	$0x1, %esi
    9d90: e8 cb 97 ff ff               	callq	0x3560 <wl_resource_post_event@plt>
    9d95: c7 83 84 01 00 00 00 00 00 00	movl	$0x0, 0x184(%rbx)
    9d9f: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    9da4: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9dad: 75 76                        	jne	0x9e25 <surface_configure_notify+0xd5>
    9daf: 48 83 c4 18                  	addq	$0x18, %rsp
    9db3: 5b                           	popq	%rbx
    9db4: 5d                           	popq	%rbp
    9db5: c3                           	retq
    9db6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    9dc0: 48 8d 54 24 04               	leaq	0x4(%rsp), %rdx
    9dc5: 48 89 e6                     	movq	%rsp, %rsi
    9dc8: 48 89 df                     	movq	%rbx, %rdi
    9dcb: c7 04 24 00 00 00 00         	movl	$0x0, (%rsp)
    9dd2: c7 44 24 04 00 00 00 00      	movl	$0x0, 0x4(%rsp)
    9dda: e8 61 a3 ff ff               	callq	0x4140 <ivi_layout_surface_get_dimension>
    9ddf: 8b 14 24                     	movl	(%rsp), %edx
    9de2: 8b 4c 24 04                  	movl	0x4(%rsp), %ecx
    9de6: 39 93 78 01 00 00            	cmpl	%edx, 0x178(%rbx)
    9dec: 74 2a                        	je	0x9e18 <surface_configure_notify+0xc8>
    9dee: 48 8b 7d a8                  	movq	-0x58(%rbp), %rdi
    9df2: 89 93 78 01 00 00            	movl	%edx, 0x178(%rbx)
    9df8: 89 8b 7c 01 00 00            	movl	%ecx, 0x17c(%rbx)
    9dfe: 48 85 ff                     	testq	%rdi, %rdi
    9e01: 74 9c                        	je	0x9d9f <surface_configure_notify+0x4f>
    9e03: be 01 00 00 00               	movl	$0x1, %esi
    9e08: 31 c0                        	xorl	%eax, %eax
    9e0a: e8 51 97 ff ff               	callq	0x3560 <wl_resource_post_event@plt>
    9e0f: eb 8e                        	jmp	0x9d9f <surface_configure_notify+0x4f>
    9e11: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    9e18: 39 8b 7c 01 00 00            	cmpl	%ecx, 0x17c(%rbx)
    9e1e: 75 ce                        	jne	0x9dee <surface_configure_notify+0x9e>
    9e20: e9 7a ff ff ff               	jmp	0x9d9f <surface_configure_notify+0x4f>
    9e25: e8 f6 93 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9e2a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

0000000000009e30 <shell_destroy>:
    9e30: 41 55                        	pushq	%r13
    9e32: 41 54                        	pushq	%r12
    9e34: 49 89 fc                     	movq	%rdi, %r12
    9e37: 55                           	pushq	%rbp
    9e38: 4d 8d 6c 24 20               	leaq	0x20(%r12), %r13
    9e3d: 53                           	pushq	%rbx
    9e3e: 48 83 ec 18                  	subq	$0x18, %rsp
    9e42: 48 8b 7f 30                  	movq	0x30(%rdi), %rdi
    9e46: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    9e4f: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    9e54: 31 c0                        	xorl	%eax, %eax
    9e56: e8 45 94 ff ff               	callq	0x32a0 <text_backend_destroy@plt>
    9e5b: 4c 89 e7                     	movq	%r12, %rdi
    9e5e: e8 ed 12 00 00               	callq	0xb150 <input_panel_destroy>
    9e63: 49 8b 7c 24 28               	movq	0x28(%r12), %rdi
    9e68: 48 8b 47 08                  	movq	0x8(%rdi), %rax
    9e6c: 48 8d 6f b8                  	leaq	-0x48(%rdi), %rbp
    9e70: 48 8d 58 b8                  	leaq	-0x48(%rax), %rbx
    9e74: 4c 39 ef                     	cmpq	%r13, %rdi
    9e77: 74 28                        	je	0x9ea1 <shell_destroy+0x71>
    9e79: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    9e80: e8 ab 95 ff ff               	callq	0x3430 <wl_list_remove@plt>
    9e85: 48 89 ef                     	movq	%rbp, %rdi
    9e88: 48 89 dd                     	movq	%rbx, %rbp
    9e8b: e8 e0 91 ff ff               	callq	0x3070 <free@plt>
    9e90: 48 8b 43 50                  	movq	0x50(%rbx), %rax
    9e94: 48 8d 7b 48                  	leaq	0x48(%rbx), %rdi
    9e98: 48 8d 58 b8                  	leaq	-0x48(%rax), %rbx
    9e9c: 4c 39 ef                     	cmpq	%r13, %rdi
    9e9f: 75 df                        	jne	0x9e80 <shell_destroy+0x50>
    9ea1: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    9ea6: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    9eaf: 75 12                        	jne	0x9ec3 <shell_destroy+0x93>
    9eb1: 48 83 c4 18                  	addq	$0x18, %rsp
    9eb5: 4c 89 e7                     	movq	%r12, %rdi
    9eb8: 5b                           	popq	%rbx
    9eb9: 5d                           	popq	%rbp
    9eba: 41 5c                        	popq	%r12
    9ebc: 41 5d                        	popq	%r13
    9ebe: e9 ad 91 ff ff               	jmp	0x3070 <free@plt>
    9ec3: e8 58 93 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    9ec8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

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
    a050: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    a055: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a05e: 0f 85 9a 00 00 00            	jne	0xa0fe <application_surface_create+0x22e>
    a064: 48 83 c4 28                  	addq	$0x28, %rsp
    a068: 5b                           	popq	%rbx
    a069: 5d                           	popq	%rbp
    a06a: 41 5c                        	popq	%r12
    a06c: 41 5d                        	popq	%r13
    a06e: 41 5e                        	popq	%r14
    a070: 41 5f                        	popq	%r15
    a072: c3                           	retq
    a073: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    a078: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    a07d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a086: 75 76                        	jne	0xa0fe <application_surface_create+0x22e>
    a088: 48 8b 3c 24                  	movq	(%rsp), %rdi
    a08c: 48 83 c4 28                  	addq	$0x28, %rsp
    a090: 5b                           	popq	%rbx
    a091: 5d                           	popq	%rbp
    a092: 41 5c                        	popq	%r12
    a094: 41 5d                        	popq	%r13
    a096: 41 5e                        	popq	%r14
    a098: 41 5f                        	popq	%r15
    a09a: e9 11 93 ff ff               	jmp	0x33b0 <wl_client_post_no_memory@plt>
    a09f: 90                           	nop
    a0a0: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    a0a5: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a0ae: 75 4e                        	jne	0xa0fe <application_surface_create+0x22e>
    a0b0: 48 83 c4 28                  	addq	$0x28, %rsp
    a0b4: 48 89 ef                     	movq	%rbp, %rdi
    a0b7: be 01 00 00 00               	movl	$0x1, %esi
    a0bc: 5b                           	popq	%rbx
    a0bd: 48 8d 15 fc 39 00 00         	leaq	0x39fc(%rip), %rdx      # 0xdac0 <__func__.11687+0xc0>
    a0c4: 31 c0                        	xorl	%eax, %eax
    a0c6: 5d                           	popq	%rbp
    a0c7: 41 5c                        	popq	%r12
    a0c9: 41 5d                        	popq	%r13
    a0cb: 41 5e                        	popq	%r14
    a0cd: 41 5f                        	popq	%r15
    a0cf: e9 5c 92 ff ff               	jmp	0x3330 <wl_resource_post_error@plt>
    a0d4: 0f 1f 40 00                  	nopl	(%rax)
    a0d8: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    a0dd: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a0e6: 75 16                        	jne	0xa0fe <application_surface_create+0x22e>
    a0e8: 48 83 c4 28                  	addq	$0x28, %rsp
    a0ec: 48 89 ef                     	movq	%rbp, %rdi
    a0ef: 5b                           	popq	%rbx
    a0f0: 5d                           	popq	%rbp
    a0f1: 41 5c                        	popq	%r12
    a0f3: 41 5d                        	popq	%r13
    a0f5: 41 5e                        	popq	%r14
    a0f7: 41 5f                        	popq	%r15
    a0f9: e9 b2 95 ff ff               	jmp	0x36b0 <wl_resource_post_no_memory@plt>
    a0fe: e8 1d 91 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a103: 0f 1f 00                     	nopl	(%rax)
    a106: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a110 <terminate_binding>:
    a110: 48 83 ec 18                  	subq	$0x18, %rsp
    a114: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a11d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a122: 31 c0                        	xorl	%eax, %eax
    a124: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a129: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a132: 75 0d                        	jne	0xa141 <terminate_binding+0x31>
    a134: 48 8b 79 10                  	movq	0x10(%rcx), %rdi
    a138: 48 83 c4 18                  	addq	$0x18, %rsp
    a13c: e9 7f 8f ff ff               	jmp	0x30c0 <wl_display_terminate@plt>
    a141: e8 da 90 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a146: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a150 <surface_property_notify>:
    a150: 48 83 ec 18                  	subq	$0x18, %rsp
    a154: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a15d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a162: 31 c0                        	xorl	%eax, %eax
    a164: 81 e2 80 00 00 00            	andl	$0x80, %edx
    a16a: 74 2c                        	je	0xa198 <surface_property_notify+0x48>
    a16c: 48 8b 39                     	movq	(%rcx), %rdi
    a16f: 48 85 ff                     	testq	%rdi, %rdi
    a172: 74 24                        	je	0xa198 <surface_property_notify+0x48>
    a174: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a179: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a182: 75 29                        	jne	0xa1ad <surface_property_notify+0x5d>
    a184: 0f b6 56 38                  	movzbl	0x38(%rsi), %edx
    a188: 31 c0                        	xorl	%eax, %eax
    a18a: 31 f6                        	xorl	%esi, %esi
    a18c: 48 83 c4 18                  	addq	$0x18, %rsp
    a190: e9 cb 93 ff ff               	jmp	0x3560 <wl_resource_post_event@plt>
    a195: 0f 1f 00                     	nopl	(%rax)
    a198: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a19d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a1a6: 75 05                        	jne	0xa1ad <surface_property_notify+0x5d>
    a1a8: 48 83 c4 18                  	addq	$0x18, %rsp
    a1ac: c3                           	retq
    a1ad: e8 6e 90 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a1b2: 0f 1f 40 00                  	nopl	(%rax)
    a1b6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a1c0 <layout_surface_cleanup>:
    a1c0: 53                           	pushq	%rbx
    a1c1: 48 89 fb                     	movq	%rdi, %rbx
    a1c4: 48 83 ec 10                  	subq	$0x10, %rsp
    a1c8: 48 8b 7f 10                  	movq	0x10(%rdi), %rdi
    a1cc: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a1d5: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a1da: 31 c0                        	xorl	%eax, %eax
    a1dc: 48 85 ff                     	testq	%rdi, %rdi
    a1df: 74 4d                        	je	0xa22e <layout_surface_cleanup+0x6e>
    a1e1: e8 0a ab ff ff               	callq	0x4cf0 <ivi_layout_surface_destroy>
    a1e6: 48 8b 43 18                  	movq	0x18(%rbx), %rax
    a1ea: 48 c7 43 10 00 00 00 00      	movq	$0x0, 0x10(%rbx)
    a1f2: 48 c7 80 80 02 00 00 00 00 00 00     	movq	$0x0, 0x280(%rax)
    a1fd: 48 c7 80 88 02 00 00 00 00 00 00     	movq	$0x0, 0x288(%rax)
    a208: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a20d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a216: 48 c7 43 18 00 00 00 00      	movq	$0x0, 0x18(%rbx)
    a21e: 75 2d                        	jne	0xa24d <layout_surface_cleanup+0x8d>
    a220: 48 8d 7b 20                  	leaq	0x20(%rbx), %rdi
    a224: 48 83 c4 10                  	addq	$0x10, %rsp
    a228: 5b                           	popq	%rbx
    a229: e9 02 92 ff ff               	jmp	0x3430 <wl_list_remove@plt>
    a22e: 48 8d 0d 2b 39 00 00         	leaq	0x392b(%rip), %rcx      # 0xdb60 <__PRETTY_FUNCTION__.12770>
    a235: ba 97 00 00 00               	movl	$0x97, %edx
    a23a: 48 8d 35 13 38 00 00         	leaq	0x3813(%rip), %rsi      # 0xda54 <__func__.11687+0x54>
    a241: 48 8d 3d a8 38 00 00         	leaq	0x38a8(%rip), %rdi      # 0xdaf0 <__func__.11687+0xf0>
    a248: e8 73 90 ff ff               	callq	0x32c0 <__assert_fail@plt>
    a24d: e8 ce 8f ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a252: 0f 1f 40 00                  	nopl	(%rax)
    a256: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a260 <shell_destroy_shell_surface>:
    a260: 55                           	pushq	%rbp
    a261: 48 89 fd                     	movq	%rdi, %rbp
    a264: 53                           	pushq	%rbx
    a265: 48 83 ec 18                  	subq	$0x18, %rsp
    a269: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a272: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a277: 31 c0                        	xorl	%eax, %eax
    a279: e8 b2 8f ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    a27e: 48 85 c0                     	testq	%rax, %rax
    a281: 74 45                        	je	0xa2c8 <shell_destroy_shell_surface+0x68>
    a283: 48 89 c3                     	movq	%rax, %rbx
    a286: 48 3b 28                     	cmpq	(%rax), %rbp
    a289: 75 54                        	jne	0xa2df <shell_destroy_shell_surface+0x7f>
    a28b: 48 83 78 10 00               	cmpq	$0x0, 0x10(%rax)
    a290: 74 08                        	je	0xa29a <shell_destroy_shell_surface+0x3a>
    a292: 48 89 c7                     	movq	%rax, %rdi
    a295: e8 26 ff ff ff               	callq	0xa1c0 <layout_surface_cleanup>
    a29a: 48 8d 7b 48                  	leaq	0x48(%rbx), %rdi
    a29e: e8 8d 91 ff ff               	callq	0x3430 <wl_list_remove@plt>
    a2a3: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a2a8: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a2b1: 75 4b                        	jne	0xa2fe <shell_destroy_shell_surface+0x9e>
    a2b3: 48 83 c4 18                  	addq	$0x18, %rsp
    a2b7: 48 89 df                     	movq	%rbx, %rdi
    a2ba: 5b                           	popq	%rbx
    a2bb: 5d                           	popq	%rbp
    a2bc: e9 af 8d ff ff               	jmp	0x3070 <free@plt>
    a2c1: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    a2c8: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a2cd: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a2d6: 75 26                        	jne	0xa2fe <shell_destroy_shell_surface+0x9e>
    a2d8: 48 83 c4 18                  	addq	$0x18, %rsp
    a2dc: 5b                           	popq	%rbx
    a2dd: 5d                           	popq	%rbp
    a2de: c3                           	retq
    a2df: 48 8d 0d 9a 38 00 00         	leaq	0x389a(%rip), %rcx      # 0xdb80 <__PRETTY_FUNCTION__.12775>
    a2e6: ba b1 00 00 00               	movl	$0xb1, %edx
    a2eb: 48 8d 35 62 37 00 00         	leaq	0x3762(%rip), %rsi      # 0xda54 <__func__.11687+0x54>
    a2f2: 48 8d 3d 71 37 00 00         	leaq	0x3771(%rip), %rdi      # 0xda6a <__func__.11687+0x6a>
    a2f9: e8 c2 8f ff ff               	callq	0x32c0 <__assert_fail@plt>
    a2fe: e8 1d 8f ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a303: 0f 1f 00                     	nopl	(%rax)
    a306: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a310 <shell_handle_surface_destroy>:
    a310: 48 83 ec 18                  	subq	$0x18, %rsp
    a314: 48 89 f8                     	movq	%rdi, %rax
    a317: 64 48 8b 14 25 28 00 00 00   	movq	%fs:0x28, %rdx
    a320: 48 89 54 24 08               	movq	%rdx, 0x8(%rsp)
    a325: 31 d2                        	xorl	%edx, %edx
    a327: 48 83 ef 20                  	subq	$0x20, %rdi
    a32b: 74 38                        	je	0xa365 <shell_handle_surface_destroy+0x55>
    a32d: 48 83 78 f0 00               	cmpq	$0x0, -0x10(%rax)
    a332: 74 1c                        	je	0xa350 <shell_handle_surface_destroy+0x40>
    a334: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a339: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a342: 75 40                        	jne	0xa384 <shell_handle_surface_destroy+0x74>
    a344: 48 83 c4 18                  	addq	$0x18, %rsp
    a348: e9 73 fe ff ff               	jmp	0xa1c0 <layout_surface_cleanup>
    a34d: 0f 1f 00                     	nopl	(%rax)
    a350: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a355: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a35e: 75 24                        	jne	0xa384 <shell_handle_surface_destroy+0x74>
    a360: 48 83 c4 18                  	addq	$0x18, %rsp
    a364: c3                           	retq
    a365: 48 8d 0d d4 37 00 00         	leaq	0x37d4(%rip), %rcx      # 0xdb40 <__PRETTY_FUNCTION__.12783>
    a36c: ba c3 00 00 00               	movl	$0xc3, %edx
    a371: 48 8d 35 dc 36 00 00         	leaq	0x36dc(%rip), %rsi      # 0xda54 <__func__.11687+0x54>
    a378: 48 8d 3d 09 37 00 00         	leaq	0x3709(%rip), %rdi      # 0xda88 <__func__.11687+0x88>
    a37f: e8 3c 8f ff ff               	callq	0x32c0 <__assert_fail@plt>
    a384: e8 97 8e ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a389: 0f 1f 80 00 00 00 00         	nopl	(%rax)

000000000000a390 <activate_binding.isra.8>:
    a390: 55                           	pushq	%rbp
    a391: 48 89 fd                     	movq	%rdi, %rbp
    a394: 48 89 f7                     	movq	%rsi, %rdi
    a397: 53                           	pushq	%rbx
    a398: 48 89 f3                     	movq	%rsi, %rbx
    a39b: 48 83 ec 18                  	subq	$0x18, %rsp
    a39f: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a3a8: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a3ad: 31 c0                        	xorl	%eax, %eax
    a3af: e8 2c 8e ff ff               	callq	0x31e0 <weston_surface_get_main_surface@plt>
    a3b4: 48 8b 15 0d 6c 20 00         	movq	0x206c0d(%rip), %rdx    # 0x210fc8 <_GLOBAL_OFFSET_TABLE_+0x3b0>
    a3bb: 48 39 90 80 02 00 00         	cmpq	%rdx, 0x280(%rax)
    a3c2: 74 1c                        	je	0xa3e0 <activate_binding.isra.8+0x50>
    a3c4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a3c9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a3d2: 75 37                        	jne	0xa40b <activate_binding.isra.8+0x7b>
    a3d4: 48 83 c4 18                  	addq	$0x18, %rsp
    a3d8: 5b                           	popq	%rbx
    a3d9: 5d                           	popq	%rbp
    a3da: c3                           	retq
    a3db: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    a3e0: 48 83 b8 88 02 00 00 00      	cmpq	$0x0, 0x288(%rax)
    a3e8: 74 da                        	je	0xa3c4 <activate_binding.isra.8+0x34>
    a3ea: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a3ef: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a3f8: 75 11                        	jne	0xa40b <activate_binding.isra.8+0x7b>
    a3fa: 48 83 c4 18                  	addq	$0x18, %rsp
    a3fe: 48 89 ee                     	movq	%rbp, %rsi
    a401: 48 89 df                     	movq	%rbx, %rdi
    a404: 5b                           	popq	%rbx
    a405: 5d                           	popq	%rbp
    a406: e9 55 90 ff ff               	jmp	0x3460 <weston_surface_activate@plt>
    a40b: e8 10 8e ff ff               	callq	0x3220 <__stack_chk_fail@plt>

000000000000a410 <touch_to_activate_binding>:
    a410: 48 83 ec 18                  	subq	$0x18, %rsp
    a414: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a41d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a422: 31 c0                        	xorl	%eax, %eax
    a424: 48 8d 87 88 00 00 00         	leaq	0x88(%rdi), %rax
    a42b: 48 39 87 80 00 00 00         	cmpq	%rax, 0x80(%rdi)
    a432: 74 1c                        	je	0xa450 <touch_to_activate_binding+0x40>
    a434: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a439: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a442: 75 34                        	jne	0xa478 <touch_to_activate_binding+0x68>
    a444: 48 83 c4 18                  	addq	$0x18, %rsp
    a448: c3                           	retq
    a449: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    a450: 48 8b 47 28                  	movq	0x28(%rdi), %rax
    a454: 48 85 c0                     	testq	%rax, %rax
    a457: 74 db                        	je	0xa434 <touch_to_activate_binding+0x24>
    a459: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    a45e: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    a467: 75 0f                        	jne	0xa478 <touch_to_activate_binding+0x68>
    a469: 48 8b 30                     	movq	(%rax), %rsi
    a46c: 48 8b 3f                     	movq	(%rdi), %rdi
    a46f: 48 83 c4 18                  	addq	$0x18, %rsp
    a473: e9 18 ff ff ff               	jmp	0xa390 <activate_binding.isra.8>
    a478: e8 a3 8d ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a47d: 0f 1f 00                     	nopl	(%rax)

000000000000a480 <click_to_activate_binding>:
    a480: 48 83 ec 18                  	subq	$0x18, %rsp
    a484: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a48d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a492: 31 c0                        	xorl	%eax, %eax
    a494: 48 8d 87 b0 00 00 00         	leaq	0xb0(%rdi), %rax
    a49b: 48 39 87 a8 00 00 00         	cmpq	%rax, 0xa8(%rdi)
    a4a2: 74 1c                        	je	0xa4c0 <click_to_activate_binding+0x40>
    a4a4: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a4a9: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a4b2: 75 34                        	jne	0xa4e8 <click_to_activate_binding+0x68>
    a4b4: 48 83 c4 18                  	addq	$0x18, %rsp
    a4b8: c3                           	retq
    a4b9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    a4c0: 48 8b 47 18                  	movq	0x18(%rdi), %rax
    a4c4: 48 85 c0                     	testq	%rax, %rax
    a4c7: 74 db                        	je	0xa4a4 <click_to_activate_binding+0x24>
    a4c9: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    a4ce: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    a4d7: 75 0f                        	jne	0xa4e8 <click_to_activate_binding+0x68>
    a4d9: 48 8b 30                     	movq	(%rax), %rsi
    a4dc: 48 8b 3f                     	movq	(%rdi), %rdi
    a4df: 48 83 c4 18                  	addq	$0x18, %rsp
    a4e3: e9 a8 fe ff ff               	jmp	0xa390 <activate_binding.isra.8>
    a4e8: e8 33 8d ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a4ed: 0f 1f 00                     	nopl	(%rax)

000000000000a4f0 <get_default_view>:
    a4f0: 41 54                        	pushq	%r12
    a4f2: 55                           	pushq	%rbp
    a4f3: 53                           	pushq	%rbx
    a4f4: 48 83 ec 10                  	subq	$0x10, %rsp
    a4f8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a501: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a506: 31 c0                        	xorl	%eax, %eax
    a508: 48 85 ff                     	testq	%rdi, %rdi
    a50b: 0f 84 8f 00 00 00            	je	0xa5a0 <get_default_view+0xb0>
    a511: 48 8d af 80 00 00 00         	leaq	0x80(%rdi), %rbp
    a518: 49 89 fc                     	movq	%rdi, %r12
    a51b: 48 89 ef                     	movq	%rbp, %rdi
    a51e: e8 cd 8e ff ff               	callq	0x33f0 <wl_list_empty@plt>
    a523: 85 c0                        	testl	%eax, %eax
    a525: 75 79                        	jne	0xa5a0 <get_default_view+0xb0>
    a527: 48 8b 05 9a 6a 20 00         	movq	0x206a9a(%rip), %rax    # 0x210fc8 <_GLOBAL_OFFSET_TABLE_+0x3b0>
    a52e: 49 39 84 24 80 02 00 00      	cmpq	%rax, 0x280(%r12)
    a536: 74 70                        	je	0xa5a8 <get_default_view+0xb8>
    a538: 49 8b 84 24 88 00 00 00      	movq	0x88(%r12), %rax
    a540: 48 8d 58 f8                  	leaq	-0x8(%rax), %rbx
    a544: 48 39 c5                     	cmpq	%rax, %rbp
    a547: 75 14                        	jne	0xa55d <get_default_view+0x6d>
    a549: eb 1e                        	jmp	0xa569 <get_default_view+0x79>
    a54b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    a550: 48 8b 43 10                  	movq	0x10(%rbx), %rax
    a554: 48 8d 58 f8                  	leaq	-0x8(%rax), %rbx
    a558: 48 39 c5                     	cmpq	%rax, %rbp
    a55b: 74 2b                        	je	0xa588 <get_default_view+0x98>
    a55d: 48 89 df                     	movq	%rbx, %rdi
    a560: e8 7b 8f ff ff               	callq	0x34e0 <weston_view_is_mapped@plt>
    a565: 84 c0                        	testb	%al, %al
    a567: 74 e7                        	je	0xa550 <get_default_view+0x60>
    a569: 48 89 d8                     	movq	%rbx, %rax
    a56c: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    a571: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    a57a: 75 55                        	jne	0xa5d1 <get_default_view+0xe1>
    a57c: 48 83 c4 10                  	addq	$0x10, %rsp
    a580: 5b                           	popq	%rbx
    a581: 5d                           	popq	%rbp
    a582: 41 5c                        	popq	%r12
    a584: c3                           	retq
    a585: 0f 1f 00                     	nopl	(%rax)
    a588: 49 8b 9c 24 88 00 00 00      	movq	0x88(%r12), %rbx
    a590: 48 83 eb 08                  	subq	$0x8, %rbx
    a594: eb d3                        	jmp	0xa569 <get_default_view+0x79>
    a596: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    a5a0: 31 c0                        	xorl	%eax, %eax
    a5a2: eb c8                        	jmp	0xa56c <get_default_view+0x7c>
    a5a4: 0f 1f 40 00                  	nopl	(%rax)
    a5a8: 49 8b 84 24 88 02 00 00      	movq	0x288(%r12), %rax
    a5b0: 48 85 c0                     	testq	%rax, %rax
    a5b3: 74 83                        	je	0xa538 <get_default_view+0x48>
    a5b5: 48 8b 78 10                  	movq	0x10(%rax), %rdi
    a5b9: 48 85 ff                     	testq	%rdi, %rdi
    a5bc: 0f 84 76 ff ff ff            	je	0xa538 <get_default_view+0x48>
    a5c2: e8 49 db ff ff               	callq	0x8110 <ivi_layout_get_weston_view>
    a5c7: 48 85 c0                     	testq	%rax, %rax
    a5ca: 75 a0                        	jne	0xa56c <get_default_view+0x7c>
    a5cc: e9 67 ff ff ff               	jmp	0xa538 <get_default_view+0x48>
    a5d1: e8 4a 8c ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a5d6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a5e0 <module_init>:
    a5e0: 41 57                        	pushq	%r15
    a5e2: 41 56                        	pushq	%r14
    a5e4: 49 89 d6                     	movq	%rdx, %r14
    a5e7: 41 55                        	pushq	%r13
    a5e9: 49 89 f5                     	movq	%rsi, %r13
    a5ec: be f0 00 00 00               	movl	$0xf0, %esi
    a5f1: 41 54                        	pushq	%r12
    a5f3: 55                           	pushq	%rbp
    a5f4: 48 89 fd                     	movq	%rdi, %rbp
    a5f7: bf 01 00 00 00               	movl	$0x1, %edi
    a5fc: 53                           	pushq	%rbx
    a5fd: 48 83 ec 48                  	subq	$0x48, %rsp
    a601: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a60a: 48 89 44 24 38               	movq	%rax, 0x38(%rsp)
    a60f: 31 c0                        	xorl	%eax, %eax
    a611: 48 c7 04 24 00 00 00 00      	movq	$0x0, (%rsp)
    a619: 48 c7 44 24 08 00 00 00 00   	movq	$0x0, 0x8(%rsp)
    a622: e8 49 8d ff ff               	callq	0x3370 <calloc@plt>
    a627: 48 85 c0                     	testq	%rax, %rax
    a62a: 0f 84 20 02 00 00            	je	0xa850 <module_init+0x270>
    a630: 4c 8b 7d 78                  	movq	0x78(%rbp), %r15
    a634: 48 8d 7c 24 10               	leaq	0x10(%rsp), %rdi
    a639: 4c 89 f1                     	movq	%r14, %rcx
    a63c: 4c 89 ea                     	movq	%r13, %rdx
    a63f: be 01 00 00 00               	movl	$0x1, %esi
    a644: 48 89 c3                     	movq	%rax, %rbx
    a647: 48 89 64 24 28               	movq	%rsp, 0x28(%rsp)
    a64c: 49 89 e4                     	movq	%rsp, %r12
    a64f: 48 8d 05 42 34 00 00         	leaq	0x3442(%rip), %rax      # 0xda98 <__func__.11687+0x98>
    a656: c7 44 24 10 02 00 00 00      	movl	$0x2, 0x10(%rsp)
    a65e: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    a663: c7 44 24 20 00 00 00 00      	movl	$0x0, 0x20(%rsp)
    a66b: e8 e0 19 00 00               	callq	0xc050 <parse_options>
    a670: 31 c9                        	xorl	%ecx, %ecx
    a672: 31 d2                        	xorl	%edx, %edx
    a674: 4c 89 ff                     	movq	%r15, %rdi
    a677: 48 8d 35 25 34 00 00         	leaq	0x3425(%rip), %rsi      # 0xdaa3 <__func__.11687+0xa3>
    a67e: e8 4d 8e ff ff               	callq	0x34d0 <weston_config_get_section@plt>
    a683: 48 83 3c 24 00               	cmpq	$0x0, (%rsp)
    a688: 49 89 c7                     	movq	%rax, %r15
    a68b: 0f 84 6f 01 00 00            	je	0xa800 <module_init+0x220>
    a691: 49 8d 54 24 08               	leaq	0x8(%r12), %rdx
    a696: 31 c9                        	xorl	%ecx, %ecx
    a698: 4c 89 ff                     	movq	%r15, %rdi
    a69b: 48 8d 35 0b 34 00 00         	leaq	0x340b(%rip), %rsi      # 0xdaad <__func__.11687+0xad>
    a6a2: e8 f9 8d ff ff               	callq	0x34a0 <weston_config_section_get_bool@plt>
    a6a7: 48 8d 7b 20                  	leaq	0x20(%rbx), %rdi
    a6ab: 48 89 6b 18                  	movq	%rbp, 0x18(%rbx)
    a6af: e8 8c 8c ff ff               	callq	0x3340 <wl_list_init@plt>
    a6b4: 48 8d bb 80 00 00 00         	leaq	0x80(%rbx), %rdi
    a6bb: 31 f6                        	xorl	%esi, %esi
    a6bd: e8 3e 8a ff ff               	callq	0x3100 <weston_layer_init@plt>
    a6c2: 8b 44 24 08                  	movl	0x8(%rsp), %eax
    a6c6: 85 c0                        	testl	%eax, %eax
    a6c8: 74 29                        	je	0xa6f3 <module_init+0x113>
    a6ca: be 04 00 00 00               	movl	$0x4, %esi
    a6cf: 48 89 ef                     	movq	%rbp, %rdi
    a6d2: e8 19 8a ff ff               	callq	0x30f0 <weston_install_debug_key_binding@plt>
    a6d7: 49 89 e8                     	movq	%rbp, %r8
    a6da: ba 03 00 00 00               	movl	$0x3, %edx
    a6df: 48 89 ef                     	movq	%rbp, %rdi
    a6e2: 48 8d 0d 27 fa ff ff         	leaq	-0x5d9(%rip), %rcx      # 0xa110 <terminate_binding>
    a6e9: be 0e 00 00 00               	movl	$0xe, %esi
    a6ee: e8 8d 8f ff ff               	callq	0x3680 <weston_compositor_add_key_binding@plt>
    a6f3: 48 8b 7d 00                  	movq	(%rbp), %rdi
    a6f7: 48 8d 05 32 f7 ff ff         	leaq	-0x8ce(%rip), %rax      # 0x9e30 <shell_destroy>
    a6fe: 48 89 de                     	movq	%rbx, %rsi
    a701: 48 89 43 10                  	movq	%rax, 0x10(%rbx)
    a705: e8 96 8f ff ff               	callq	0x36a0 <wl_list_insert@plt>
    a70a: 48 89 df                     	movq	%rbx, %rdi
    a70d: e8 8e 0a 00 00               	callq	0xb1a0 <input_panel_setup>
    a712: 85 c0                        	testl	%eax, %eax
    a714: 0f 88 ae 00 00 00            	js	0xa7c8 <module_init+0x1e8>
    a71a: 48 89 ef                     	movq	%rbp, %rdi
    a71d: e8 ae 8e ff ff               	callq	0x35d0 <text_backend_init@plt>
    a722: 48 89 43 30                  	movq	%rax, 0x30(%rbx)
    a726: 48 85 c0                     	testq	%rax, %rax
    a729: 0f 84 99 00 00 00            	je	0xa7c8 <module_init+0x1e8>
    a72f: 48 8b 7d 10                  	movq	0x10(%rbp), %rdi
    a733: 4c 8d 05 76 f5 ff ff         	leaq	-0xa8a(%rip), %r8       # 0x9cb0 <bind_ivi_application>
    a73a: 48 89 d9                     	movq	%rbx, %rcx
    a73d: ba 01 00 00 00               	movl	$0x1, %edx
    a742: 48 8b 35 57 68 20 00         	movq	0x206857(%rip), %rsi    # 0x210fa0 <_GLOBAL_OFFSET_TABLE_+0x388>
    a749: e8 32 89 ff ff               	callq	0x3080 <wl_global_create@plt>
    a74e: 48 85 c0                     	testq	%rax, %rax
    a751: 74 75                        	je	0xa7c8 <module_init+0x1e8>
    a753: 48 89 ef                     	movq	%rbp, %rdi
    a756: e8 b5 da ff ff               	callq	0x8210 <ivi_layout_init_with_compositor>
    a75b: 31 d2                        	xorl	%edx, %edx
    a75d: 49 89 d8                     	movq	%rbx, %r8
    a760: be 10 01 00 00               	movl	$0x110, %esi            # imm = 0x110
    a765: 48 8d 0d 14 fd ff ff         	leaq	-0x2ec(%rip), %rcx      # 0xa480 <click_to_activate_binding>
    a76c: 48 89 ef                     	movq	%rbp, %rdi
    a76f: e8 9c 8b ff ff               	callq	0x3310 <weston_compositor_add_button_binding@plt>
    a774: 31 d2                        	xorl	%edx, %edx
    a776: 49 89 d8                     	movq	%rbx, %r8
    a779: be 11 01 00 00               	movl	$0x111, %esi            # imm = 0x111
    a77e: 48 8d 0d fb fc ff ff         	leaq	-0x305(%rip), %rcx      # 0xa480 <click_to_activate_binding>
    a785: 48 89 ef                     	movq	%rbp, %rdi
    a788: e8 83 8b ff ff               	callq	0x3310 <weston_compositor_add_button_binding@plt>
    a78d: 31 f6                        	xorl	%esi, %esi
    a78f: 48 89 d9                     	movq	%rbx, %rcx
    a792: 48 89 ef                     	movq	%rbp, %rdi
    a795: 48 8d 15 74 fc ff ff         	leaq	-0x38c(%rip), %rdx      # 0xa410 <touch_to_activate_binding>
    a79c: e8 7f 8d ff ff               	callq	0x3520 <weston_compositor_add_touch_binding@plt>
    a7a1: 48 8b 34 24                  	movq	(%rsp), %rsi
    a7a5: 4c 89 f1                     	movq	%r14, %rcx
    a7a8: 4c 89 ea                     	movq	%r13, %rdx
    a7ab: 48 89 ef                     	movq	%rbp, %rdi
    a7ae: e8 2d dc ff ff               	callq	0x83e0 <load_controller_modules>
    a7b3: 85 c0                        	testl	%eax, %eax
    a7b5: 78 11                        	js	0xa7c8 <module_init+0x1e8>
    a7b7: 48 89 ef                     	movq	%rbp, %rdi
    a7ba: 31 db                        	xorl	%ebx, %ebx
    a7bc: e8 bf 8d ff ff               	callq	0x3580 <screenshooter_create@plt>
    a7c1: eb 0a                        	jmp	0xa7cd <module_init+0x1ed>
    a7c3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    a7c8: bb ff ff ff ff               	movl	$0xffffffff, %ebx       # imm = 0xFFFFFFFF
    a7cd: 48 8b 3c 24                  	movq	(%rsp), %rdi
    a7d1: e8 9a 88 ff ff               	callq	0x3070 <free@plt>
    a7d6: 89 d8                        	movl	%ebx, %eax
    a7d8: 48 8b 4c 24 38               	movq	0x38(%rsp), %rcx
    a7dd: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    a7e6: 75 6f                        	jne	0xa857 <module_init+0x277>
    a7e8: 48 83 c4 48                  	addq	$0x48, %rsp
    a7ec: 5b                           	popq	%rbx
    a7ed: 5d                           	popq	%rbp
    a7ee: 41 5c                        	popq	%r12
    a7f0: 41 5d                        	popq	%r13
    a7f2: 41 5e                        	popq	%r14
    a7f4: 41 5f                        	popq	%r15
    a7f6: c3                           	retq
    a7f7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    a800: 31 c9                        	xorl	%ecx, %ecx
    a802: 48 89 e2                     	movq	%rsp, %rdx
    a805: 48 89 c7                     	movq	%rax, %rdi
    a808: 48 8d 35 89 32 00 00         	leaq	0x3289(%rip), %rsi      # 0xda98 <__func__.11687+0x98>
    a80f: e8 ac 8d ff ff               	callq	0x35c0 <weston_config_section_get_string@plt>
    a814: 85 c0                        	testl	%eax, %eax
    a816: 0f 89 75 fe ff ff            	jns	0xa691 <module_init+0xb1>
    a81c: 48 8d 3d ed 32 00 00         	leaq	0x32ed(%rip), %rdi      # 0xdb10 <__func__.11687+0x110>
    a823: 31 c0                        	xorl	%eax, %eax
    a825: e8 e6 89 ff ff               	callq	0x3210 <weston_log@plt>
    a82a: 48 8d 54 24 08               	leaq	0x8(%rsp), %rdx
    a82f: 31 c9                        	xorl	%ecx, %ecx
    a831: 4c 89 ff                     	movq	%r15, %rdi
    a834: 48 8d 35 72 32 00 00         	leaq	0x3272(%rip), %rsi      # 0xdaad <__func__.11687+0xad>
    a83b: e8 60 8c ff ff               	callq	0x34a0 <weston_config_section_get_bool@plt>
    a840: 48 89 df                     	movq	%rbx, %rdi
    a843: e8 28 88 ff ff               	callq	0x3070 <free@plt>
    a848: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    a84d: eb 89                        	jmp	0xa7d8 <module_init+0x1f8>
    a84f: 90                           	nop
    a850: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    a855: eb 81                        	jmp	0xa7d8 <module_init+0x1f8>
    a857: e8 c4 89 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a85c: 0f 1f 40 00                  	nopl	(%rax)

000000000000a860 <input_panel_slide_done>:
    a860: 48 83 ec 18                  	subq	$0x18, %rsp
    a864: 48 c7 46 58 00 00 00 00      	movq	$0x0, 0x58(%rsi)
    a86c: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a875: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a87a: 31 c0                        	xorl	%eax, %eax
    a87c: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a881: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a88a: 75 05                        	jne	0xa891 <input_panel_slide_done+0x31>
    a88c: 48 83 c4 18                  	addq	$0x18, %rsp
    a890: c3                           	retq
    a891: e8 8a 89 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a896: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a8a0 <bind_input_panel>:
    a8a0: 53                           	pushq	%rbx
    a8a1: 48 89 f3                     	movq	%rsi, %rbx
    a8a4: ba 01 00 00 00               	movl	$0x1, %edx
    a8a9: 48 83 ec 20                  	subq	$0x20, %rsp
    a8ad: 48 8b 35 e4 66 20 00         	movq	0x2066e4(%rip), %rsi    # 0x210f98 <_GLOBAL_OFFSET_TABLE_+0x380>
    a8b4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a8bd: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    a8c2: 31 c0                        	xorl	%eax, %eax
    a8c4: e8 c7 88 ff ff               	callq	0x3190 <wl_resource_create@plt>
    a8c9: 48 83 bb d8 00 00 00 00      	cmpq	$0x0, 0xd8(%rbx)
    a8d1: 74 2d                        	je	0xa900 <bind_input_panel+0x60>
    a8d3: 48 8b 54 24 18               	movq	0x18(%rsp), %rdx
    a8d8: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    a8e1: 75 5d                        	jne	0xa940 <bind_input_panel+0xa0>
    a8e3: 48 83 c4 20                  	addq	$0x20, %rsp
    a8e7: 48 89 c7                     	movq	%rax, %rdi
    a8ea: 31 f6                        	xorl	%esi, %esi
    a8ec: 5b                           	popq	%rbx
    a8ed: 48 8d 15 ac 32 00 00         	leaq	0x32ac(%rip), %rdx      # 0xdba0 <__PRETTY_FUNCTION__.12775+0x20>
    a8f4: 31 c0                        	xorl	%eax, %eax
    a8f6: e9 35 8a ff ff               	jmp	0x3330 <wl_resource_post_error@plt>
    a8fb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    a900: 48 89 c7                     	movq	%rax, %rdi
    a903: 48 89 da                     	movq	%rbx, %rdx
    a906: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a90b: 48 8d 0d 3e 00 00 00         	leaq	0x3e(%rip), %rcx        # 0xa950 <unbind_input_panel>
    a912: 48 8d 35 b7 5f 20 00         	leaq	0x205fb7(%rip), %rsi    # 0x2108d0 <input_panel_implementation>
    a919: e8 c2 89 ff ff               	callq	0x32e0 <wl_resource_set_implementation@plt>
    a91e: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a923: 48 89 83 d8 00 00 00         	movq	%rax, 0xd8(%rbx)
    a92a: 48 8b 44 24 18               	movq	0x18(%rsp), %rax
    a92f: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a938: 75 06                        	jne	0xa940 <bind_input_panel+0xa0>
    a93a: 48 83 c4 20                  	addq	$0x20, %rsp
    a93e: 5b                           	popq	%rbx
    a93f: c3                           	retq
    a940: e8 db 88 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a945: 90                           	nop
    a946: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000a950 <unbind_input_panel>:
    a950: 48 83 ec 18                  	subq	$0x18, %rsp
    a954: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a95d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a962: 31 c0                        	xorl	%eax, %eax
    a964: e8 c7 88 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    a969: 48 c7 80 d8 00 00 00 00 00 00 00     	movq	$0x0, 0xd8(%rax)
    a974: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    a979: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    a982: 75 05                        	jne	0xa989 <unbind_input_panel+0x39>
    a984: 48 83 c4 18                  	addq	$0x18, %rsp
    a988: c3                           	retq
    a989: e8 92 88 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    a98e: 66 90                        	nop

000000000000a990 <destroy_input_panel_surface>:
    a990: 41 54                        	pushq	%r12
    a992: 4c 8d 67 08                  	leaq	0x8(%rdi), %r12
    a996: 55                           	pushq	%rbp
    a997: 48 89 fd                     	movq	%rdi, %rbp
    a99a: 53                           	pushq	%rbx
    a99b: 48 83 ec 10                  	subq	$0x10, %rsp
    a99f: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    a9a8: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    a9ad: 31 c0                        	xorl	%eax, %eax
    a9af: 48 8b 47 10                  	movq	0x10(%rdi), %rax
    a9b3: 48 8b 58 08                  	movq	0x8(%rax), %rbx
    a9b7: 49 39 c4                     	cmpq	%rax, %r12
    a9ba: 75 07                        	jne	0xa9c3 <destroy_input_panel_surface+0x33>
    a9bc: eb 1a                        	jmp	0xa9d8 <destroy_input_panel_surface+0x48>
    a9be: 66 90                        	nop
    a9c0: 48 89 d3                     	movq	%rdx, %rbx
    a9c3: 48 89 c7                     	movq	%rax, %rdi
    a9c6: 48 89 ee                     	movq	%rbp, %rsi
    a9c9: ff 50 10                     	callq	*0x10(%rax)
    a9cc: 48 8b 53 08                  	movq	0x8(%rbx), %rdx
    a9d0: 48 89 d8                     	movq	%rbx, %rax
    a9d3: 49 39 dc                     	cmpq	%rbx, %r12
    a9d6: 75 e8                        	jne	0xa9c0 <destroy_input_panel_surface+0x30>
    a9d8: 48 8d 7d 40                  	leaq	0x40(%rbp), %rdi
    a9dc: e8 4f 8a ff ff               	callq	0x3430 <wl_list_remove@plt>
    a9e1: 48 8d 7d 20                  	leaq	0x20(%rbp), %rdi
    a9e5: e8 46 8a ff ff               	callq	0x3430 <wl_list_remove@plt>
    a9ea: 48 8b 45 30                  	movq	0x30(%rbp), %rax
    a9ee: 48 8b 7d 38                  	movq	0x38(%rbp), %rdi
    a9f2: 48 c7 80 80 02 00 00 00 00 00 00     	movq	$0x0, 0x280(%rax)
    a9fd: e8 5e 87 ff ff               	callq	0x3160 <weston_view_destroy@plt>
    aa02: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    aa07: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    aa10: 75 10                        	jne	0xaa22 <destroy_input_panel_surface+0x92>
    aa12: 48 83 c4 10                  	addq	$0x10, %rsp
    aa16: 48 89 ef                     	movq	%rbp, %rdi
    aa19: 5b                           	popq	%rbx
    aa1a: 5d                           	popq	%rbp
    aa1b: 41 5c                        	popq	%r12
    aa1d: e9 4e 86 ff ff               	jmp	0x3070 <free@plt>
    aa22: e8 f9 87 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    aa27: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

000000000000aa30 <destroy_input_panel_surface_resource>:
    aa30: 48 83 ec 18                  	subq	$0x18, %rsp
    aa34: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    aa3d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    aa42: 31 c0                        	xorl	%eax, %eax
    aa44: e8 e7 87 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    aa49: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    aa4e: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    aa57: 75 0c                        	jne	0xaa65 <destroy_input_panel_surface_resource+0x35>
    aa59: 48 89 c7                     	movq	%rax, %rdi
    aa5c: 48 83 c4 18                  	addq	$0x18, %rsp
    aa60: e9 2b ff ff ff               	jmp	0xa990 <destroy_input_panel_surface>
    aa65: e8 b6 87 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    aa6a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

000000000000aa70 <input_panel_surface_set_overlay_panel>:
    aa70: 53                           	pushq	%rbx
    aa71: 48 89 f7                     	movq	%rsi, %rdi
    aa74: 48 83 ec 10                  	subq	$0x10, %rsp
    aa78: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    aa81: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    aa86: 31 c0                        	xorl	%eax, %eax
    aa88: e8 a3 87 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    aa8d: 48 8d 70 20                  	leaq	0x20(%rax), %rsi
    aa91: 48 89 c3                     	movq	%rax, %rbx
    aa94: 48 8b 40 18                  	movq	0x18(%rax), %rax
    aa98: 48 8d b8 e0 00 00 00         	leaq	0xe0(%rax), %rdi
    aa9f: e8 fc 8b ff ff               	callq	0x36a0 <wl_list_insert@plt>
    aaa4: c7 43 68 01 00 00 00         	movl	$0x1, 0x68(%rbx)
    aaab: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    aab0: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    aab9: 75 06                        	jne	0xaac1 <input_panel_surface_set_overlay_panel+0x51>
    aabb: 48 83 c4 10                  	addq	$0x10, %rsp
    aabf: 5b                           	popq	%rbx
    aac0: c3                           	retq
    aac1: e8 5a 87 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    aac6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000aad0 <input_panel_surface_set_toplevel>:
    aad0: 55                           	pushq	%rbp
    aad1: 48 89 f7                     	movq	%rsi, %rdi
    aad4: 48 89 d5                     	movq	%rdx, %rbp
    aad7: 53                           	pushq	%rbx
    aad8: 48 83 ec 18                  	subq	$0x18, %rsp
    aadc: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    aae5: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    aaea: 31 c0                        	xorl	%eax, %eax
    aaec: e8 3f 87 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    aaf1: 48 8d 70 20                  	leaq	0x20(%rax), %rsi
    aaf5: 48 89 c3                     	movq	%rax, %rbx
    aaf8: 48 8b 40 18                  	movq	0x18(%rax), %rax
    aafc: 48 8d b8 e0 00 00 00         	leaq	0xe0(%rax), %rdi
    ab03: e8 98 8b ff ff               	callq	0x36a0 <wl_list_insert@plt>
    ab08: 48 89 ef                     	movq	%rbp, %rdi
    ab0b: e8 20 87 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    ab10: c7 43 68 00 00 00 00         	movl	$0x0, 0x68(%rbx)
    ab17: 48 89 43 60                  	movq	%rax, 0x60(%rbx)
    ab1b: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    ab20: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    ab29: 75 07                        	jne	0xab32 <input_panel_surface_set_toplevel+0x62>
    ab2b: 48 83 c4 18                  	addq	$0x18, %rsp
    ab2f: 5b                           	popq	%rbx
    ab30: 5d                           	popq	%rbp
    ab31: c3                           	retq
    ab32: e8 e9 86 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    ab37: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

000000000000ab40 <show_input_panel_surface>:
    ab40: 41 54                        	pushq	%r12
    ab42: 55                           	pushq	%rbp
    ab43: 48 89 fd                     	movq	%rdi, %rbp
    ab46: 53                           	pushq	%rbx
    ab47: 48 83 ec 10                  	subq	$0x10, %rsp
    ab4b: 4c 8b 67 18                  	movq	0x18(%rdi), %r12
    ab4f: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    ab58: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    ab5d: 31 c0                        	xorl	%eax, %eax
    ab5f: 49 8b 44 24 18               	movq	0x18(%r12), %rax
    ab64: 48 8b 90 00 02 00 00         	movq	0x200(%rax), %rdx
    ab6b: 48 05 f8 01 00 00            	addq	$0x1f8, %rax            # imm = 0x1F8
    ab71: 48 8d 5a 90                  	leaq	-0x70(%rdx), %rbx
    ab75: 48 39 d0                     	cmpq	%rdx, %rax
    ab78: 0f 84 88 00 00 00            	je	0xac06 <show_input_panel_surface+0xc6>
    ab7e: 66 90                        	nop
    ab80: 48 89 df                     	movq	%rbx, %rdi
    ab83: e8 d8 86 ff ff               	callq	0x3260 <weston_seat_get_keyboard@plt>
    ab88: 48 85 c0                     	testq	%rax, %rax
    ab8b: 74 5d                        	je	0xabea <show_input_panel_surface+0xaa>
    ab8d: 48 8b 78 28                  	movq	0x28(%rax), %rdi
    ab91: 48 85 ff                     	testq	%rdi, %rdi
    ab94: 74 54                        	je	0xabea <show_input_panel_surface+0xaa>
    ab96: e8 45 86 ff ff               	callq	0x31e0 <weston_surface_get_main_surface@plt>
    ab9b: 48 8b 75 30                  	movq	0x30(%rbp), %rsi
    ab9f: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    aba3: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    aba7: 48 8b 88 90 00 00 00         	movq	0x90(%rax), %rcx
    abae: 48 8b 7d 38                  	movq	0x38(%rbp), %rdi
    abb2: 8b 81 e8 00 00 00            	movl	0xe8(%rcx), %eax
    abb8: 48 89 4d 60                  	movq	%rcx, 0x60(%rbp)
    abbc: 2b 46 68                     	subl	0x68(%rsi), %eax
    abbf: 8b 91 ec 00 00 00            	movl	0xec(%rcx), %edx
    abc5: 03 91 e4 00 00 00            	addl	0xe4(%rcx), %edx
    abcb: 2b 56 6c                     	subl	0x6c(%rsi), %edx
    abce: 89 c6                        	movl	%eax, %esi
    abd0: c1 ee 1f                     	shrl	$0x1f, %esi
    abd3: 01 f0                        	addl	%esi, %eax
    abd5: d1 f8                        	sarl	%eax
    abd7: 03 81 e0 00 00 00            	addl	0xe0(%rcx), %eax
    abdd: f3 0f 2a ca                  	cvtsi2ss	%edx, %xmm1
    abe1: f3 0f 2a c0                  	cvtsi2ss	%eax, %xmm0
    abe5: e8 b6 85 ff ff               	callq	0x31a0 <weston_view_set_position@plt>
    abea: 49 8b 44 24 18               	movq	0x18(%r12), %rax
    abef: 48 8b 53 78                  	movq	0x78(%rbx), %rdx
    abf3: 48 05 f8 01 00 00            	addq	$0x1f8, %rax            # imm = 0x1F8
    abf9: 48 8d 5a 90                  	leaq	-0x70(%rdx), %rbx
    abfd: 48 39 c2                     	cmpq	%rax, %rdx
    ac00: 0f 85 7a ff ff ff            	jne	0xab80 <show_input_panel_surface+0x40>
    ac06: 48 8b 45 38                  	movq	0x38(%rbp), %rax
    ac0a: 49 8d bc 24 80 00 00 00      	leaq	0x80(%r12), %rdi
    ac12: 48 8d 70 38                  	leaq	0x38(%rax), %rsi
    ac16: e8 65 85 ff ff               	callq	0x3180 <weston_layer_entry_insert@plt>
    ac1b: 48 8b 7d 38                  	movq	0x38(%rbp), %rdi
    ac1f: e8 0c 8a ff ff               	callq	0x3630 <weston_view_geometry_dirty@plt>
    ac24: 48 8b 7d 38                  	movq	0x38(%rbp), %rdi
    ac28: e8 23 8a ff ff               	callq	0x3650 <weston_view_update_transform@plt>
    ac2d: 48 8b 7d 30                  	movq	0x30(%rbp), %rdi
    ac31: e8 5a 88 ff ff               	callq	0x3490 <weston_surface_damage@plt>
    ac36: 48 8b 7d 58                  	movq	0x58(%rbp), %rdi
    ac3a: 48 85 ff                     	testq	%rdi, %rdi
    ac3d: 74 05                        	je	0xac44 <show_input_panel_surface+0x104>
    ac3f: e8 fc 87 ff ff               	callq	0x3440 <weston_view_animation_destroy@plt>
    ac44: 48 8b 45 30                  	movq	0x30(%rbp), %rax
    ac48: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    ac4c: 48 89 ea                     	movq	%rbp, %rdx
    ac4f: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    ac53: 48 8b 7d 38                  	movq	0x38(%rbp), %rdi
    ac57: 48 8d 35 02 fc ff ff         	leaq	-0x3fe(%rip), %rsi      # 0xa860 <input_panel_slide_done>
    ac5e: f2 0f 2a 40 6c               	cvtsi2sdl	0x6c(%rax), %xmm0
    ac63: f2 0f 59 05 b5 2f 00 00      	mulsd	0x2fb5(%rip), %xmm0     # 0xdc20 <__PRETTY_FUNCTION__.12775+0xa0>
    ac6b: f2 0f 5a c0                  	cvtsd2ss	%xmm0, %xmm0
    ac6f: e8 bc 88 ff ff               	callq	0x3530 <weston_slide_run@plt>
    ac74: 48 89 45 58                  	movq	%rax, 0x58(%rbp)
    ac78: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    ac7d: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    ac86: 75 09                        	jne	0xac91 <show_input_panel_surface+0x151>
    ac88: 48 83 c4 10                  	addq	$0x10, %rsp
    ac8c: 5b                           	popq	%rbx
    ac8d: 5d                           	popq	%rbp
    ac8e: 41 5c                        	popq	%r12
    ac90: c3                           	retq
    ac91: e8 8a 85 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    ac96: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000aca0 <input_panel_configure>:
    aca0: 41 54                        	pushq	%r12
    aca2: 55                           	pushq	%rbp
    aca3: 53                           	pushq	%rbx
    aca4: 48 83 ec 10                  	subq	$0x10, %rsp
    aca8: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    acb1: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    acb6: 31 c0                        	xorl	%eax, %eax
    acb8: 8b 47 68                     	movl	0x68(%rdi), %eax
    acbb: 85 c0                        	testl	%eax, %eax
    acbd: 74 71                        	je	0xad30 <input_panel_configure+0x90>
    acbf: 48 8b af 88 02 00 00         	movq	0x288(%rdi), %rbp
    acc6: 48 89 fb                     	movq	%rdi, %rbx
    acc9: 8b 55 68                     	movl	0x68(%rbp), %edx
    accc: 4c 8b 65 18                  	movq	0x18(%rbp), %r12
    acd0: 85 d2                        	testl	%edx, %edx
    acd2: 75 7c                        	jne	0xad50 <input_panel_configure+0xb0>
    acd4: 48 8b 55 60                  	movq	0x60(%rbp), %rdx
    acd8: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    acdc: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    ace0: 8b b2 e8 00 00 00            	movl	0xe8(%rdx), %esi
    ace6: 29 c6                        	subl	%eax, %esi
    ace8: 89 f1                        	movl	%esi, %ecx
    acea: 89 f0                        	movl	%esi, %eax
    acec: c1 e9 1f                     	shrl	$0x1f, %ecx
    acef: 01 c8                        	addl	%ecx, %eax
    acf1: d1 f8                        	sarl	%eax
    acf3: 03 82 e0 00 00 00            	addl	0xe0(%rdx), %eax
    acf9: f3 0f 2a c0                  	cvtsi2ss	%eax, %xmm0
    acfd: 8b 82 ec 00 00 00            	movl	0xec(%rdx), %eax
    ad03: 03 82 e4 00 00 00            	addl	0xe4(%rdx), %eax
    ad09: 2b 47 6c                     	subl	0x6c(%rdi), %eax
    ad0c: f3 0f 2a c8                  	cvtsi2ss	%eax, %xmm1
    ad10: 48 8b 7d 38                  	movq	0x38(%rbp), %rdi
    ad14: e8 87 84 ff ff               	callq	0x31a0 <weston_view_set_position@plt>
    ad19: 48 89 df                     	movq	%rbx, %rdi
    ad1c: e8 cf 85 ff ff               	callq	0x32f0 <weston_surface_is_mapped@plt>
    ad21: 84 c0                        	testb	%al, %al
    ad23: 75 0b                        	jne	0xad30 <input_panel_configure+0x90>
    ad25: 41 80 bc 24 b9 00 00 00 00   	cmpb	$0x0, 0xb9(%r12)
    ad2e: 75 60                        	jne	0xad90 <input_panel_configure+0xf0>
    ad30: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    ad35: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    ad3e: 75 70                        	jne	0xadb0 <input_panel_configure+0x110>
    ad40: 48 83 c4 10                  	addq	$0x10, %rsp
    ad44: 5b                           	popq	%rbx
    ad45: 5d                           	popq	%rbp
    ad46: 41 5c                        	popq	%r12
    ad48: c3                           	retq
    ad49: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    ad50: 49 8b bc 24 c0 00 00 00      	movq	0xc0(%r12), %rdi
    ad58: e8 93 f7 ff ff               	callq	0xa4f0 <get_default_view>
    ad5d: 48 85 c0                     	testq	%rax, %rax
    ad60: 74 ce                        	je	0xad30 <input_panel_configure+0x90>
    ad62: 66 0f ef c0                  	pxor	%xmm0, %xmm0
    ad66: 66 0f ef c9                  	pxor	%xmm1, %xmm1
    ad6a: f3 41 0f 2a 84 24 d0 00 00 00	cvtsi2ssl	0xd0(%r12), %xmm0
    ad74: f3 41 0f 2a 8c 24 d4 00 00 00	cvtsi2ssl	0xd4(%r12), %xmm1
    ad7e: f3 0f 58 80 88 00 00 00      	addss	0x88(%rax), %xmm0
    ad86: f3 0f 58 88 8c 00 00 00      	addss	0x8c(%rax), %xmm1
    ad8e: eb 80                        	jmp	0xad10 <input_panel_configure+0x70>
    ad90: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    ad95: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    ad9e: 75 10                        	jne	0xadb0 <input_panel_configure+0x110>
    ada0: 48 83 c4 10                  	addq	$0x10, %rsp
    ada4: 48 89 ef                     	movq	%rbp, %rdi
    ada7: 5b                           	popq	%rbx
    ada8: 5d                           	popq	%rbp
    ada9: 41 5c                        	popq	%r12
    adab: e9 90 fd ff ff               	jmp	0xab40 <show_input_panel_surface>
    adb0: e8 6b 84 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    adb5: 90                           	nop
    adb6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000adc0 <input_panel_handle_surface_destroy>:
    adc0: 48 83 ec 18                  	subq	$0x18, %rsp
    adc4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    adcd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    add2: 31 c0                        	xorl	%eax, %eax
    add4: 48 8b 47 c0                  	movq	-0x40(%rdi), %rax
    add8: 48 85 c0                     	testq	%rax, %rax
    addb: 74 23                        	je	0xae00 <input_panel_handle_surface_destroy+0x40>
    addd: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    ade2: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    adeb: 75 30                        	jne	0xae1d <input_panel_handle_surface_destroy+0x5d>
    aded: 48 89 c7                     	movq	%rax, %rdi
    adf0: 48 83 c4 18                  	addq	$0x18, %rsp
    adf4: e9 47 84 ff ff               	jmp	0x3240 <wl_resource_destroy@plt>
    adf9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    ae00: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    ae05: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    ae0e: 75 0d                        	jne	0xae1d <input_panel_handle_surface_destroy+0x5d>
    ae10: 48 83 ef 40                  	subq	$0x40, %rdi
    ae14: 48 83 c4 18                  	addq	$0x18, %rsp
    ae18: e9 73 fb ff ff               	jmp	0xa990 <destroy_input_panel_surface>
    ae1d: e8 fe 83 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    ae22: 0f 1f 40 00                  	nopl	(%rax)
    ae26: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000ae30 <update_input_panels>:
    ae30: 48 83 ec 18                  	subq	$0x18, %rsp
    ae34: 48 8b 56 08                  	movq	0x8(%rsi), %rdx
    ae38: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    ae41: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    ae46: 31 c0                        	xorl	%eax, %eax
    ae48: 48 8b 06                     	movq	(%rsi), %rax
    ae4b: 48 89 57 68                  	movq	%rdx, 0x68(%rdi)
    ae4f: 48 89 47 60                  	movq	%rax, 0x60(%rdi)
    ae53: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    ae58: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    ae61: 75 05                        	jne	0xae68 <update_input_panels+0x38>
    ae63: 48 83 c4 18                  	addq	$0x18, %rsp
    ae67: c3                           	retq
    ae68: e8 b3 83 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    ae6d: 0f 1f 00                     	nopl	(%rax)

000000000000ae70 <show_input_panels>:
    ae70: 55                           	pushq	%rbp
    ae71: 53                           	pushq	%rbx
    ae72: 48 83 ec 18                  	subq	$0x18, %rsp
    ae76: 48 89 b7 88 00 00 00         	movq	%rsi, 0x88(%rdi)
    ae7d: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    ae86: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    ae8b: 31 c0                        	xorl	%eax, %eax
    ae8d: 80 bf 81 00 00 00 00         	cmpb	$0x0, 0x81(%rdi)
    ae94: 75 6a                        	jne	0xaf00 <show_input_panels+0x90>
    ae96: 80 bf 80 00 00 00 00         	cmpb	$0x0, 0x80(%rdi)
    ae9d: 48 89 fd                     	movq	%rdi, %rbp
    aea0: c6 87 81 00 00 00 01         	movb	$0x1, 0x81(%rdi)
    aea7: 74 77                        	je	0xaf20 <show_input_panels+0xb0>
    aea9: 48 8b 85 b0 00 00 00         	movq	0xb0(%rbp), %rax
    aeb0: 48 81 c5 a8 00 00 00         	addq	$0xa8, %rbp
    aeb7: 48 8b 48 08                  	movq	0x8(%rax), %rcx
    aebb: 48 8d 78 e0                  	leaq	-0x20(%rax), %rdi
    aebf: 48 8d 59 e0                  	leaq	-0x20(%rcx), %rbx
    aec3: 48 39 c5                     	cmpq	%rax, %rbp
    aec6: 75 1f                        	jne	0xaee7 <show_input_panels+0x77>
    aec8: eb 36                        	jmp	0xaf00 <show_input_panels+0x90>
    aeca: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    aed0: 48 8b 43 28                  	movq	0x28(%rbx), %rax
    aed4: 48 8d 53 20                  	leaq	0x20(%rbx), %rdx
    aed8: 48 89 df                     	movq	%rbx, %rdi
    aedb: 48 83 e8 20                  	subq	$0x20, %rax
    aedf: 48 39 d5                     	cmpq	%rdx, %rbp
    aee2: 74 1c                        	je	0xaf00 <show_input_panels+0x90>
    aee4: 48 89 c3                     	movq	%rax, %rbx
    aee7: 48 8b 47 30                  	movq	0x30(%rdi), %rax
    aeeb: 8b 40 68                     	movl	0x68(%rax), %eax
    aeee: 85 c0                        	testl	%eax, %eax
    aef0: 74 de                        	je	0xaed0 <show_input_panels+0x60>
    aef2: e8 49 fc ff ff               	callq	0xab40 <show_input_panel_surface>
    aef7: eb d7                        	jmp	0xaed0 <show_input_panels+0x60>
    aef9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    af00: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    af05: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    af0e: 75 29                        	jne	0xaf39 <show_input_panels+0xc9>
    af10: 48 83 c4 18                  	addq	$0x18, %rsp
    af14: 5b                           	popq	%rbx
    af15: 5d                           	popq	%rbp
    af16: c3                           	retq
    af17: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    af20: 48 8b 47 e0                  	movq	-0x20(%rdi), %rax
    af24: 48 8d 77 60                  	leaq	0x60(%rdi), %rsi
    af28: 48 8d b8 c8 01 00 00         	leaq	0x1c8(%rax), %rdi
    af2f: e8 6c 87 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    af34: e9 70 ff ff ff               	jmp	0xaea9 <show_input_panels+0x39>
    af39: e8 e2 82 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    af3e: 66 90                        	nop

000000000000af40 <input_panel_get_input_panel_surface>:
    af40: 41 57                        	pushq	%r15
    af42: 41 56                        	pushq	%r14
    af44: 41 89 d6                     	movl	%edx, %r14d
    af47: 41 55                        	pushq	%r13
    af49: 49 89 fd                     	movq	%rdi, %r13
    af4c: 48 89 cf                     	movq	%rcx, %rdi
    af4f: 41 54                        	pushq	%r12
    af51: 49 89 f4                     	movq	%rsi, %r12
    af54: 55                           	pushq	%rbp
    af55: 48 89 cd                     	movq	%rcx, %rbp
    af58: 53                           	pushq	%rbx
    af59: 48 83 ec 18                  	subq	$0x18, %rsp
    af5d: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    af66: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    af6b: 31 c0                        	xorl	%eax, %eax
    af6d: e8 be 82 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    af72: 4c 89 e7                     	movq	%r12, %rdi
    af75: 48 89 c3                     	movq	%rax, %rbx
    af78: e8 b3 82 ff ff               	callq	0x3230 <wl_resource_get_user_data@plt>
    af7d: 49 89 c7                     	movq	%rax, %r15
    af80: 48 8d 05 19 fd ff ff         	leaq	-0x2e7(%rip), %rax      # 0xaca0 <input_panel_configure>
    af87: 48 39 83 80 02 00 00         	cmpq	%rax, 0x280(%rbx)
    af8e: 0f 84 cc 00 00 00            	je	0xb060 <input_panel_get_input_panel_surface+0x120>
    af94: be 70 00 00 00               	movl	$0x70, %esi
    af99: bf 01 00 00 00               	movl	$0x1, %edi
    af9e: e8 cd 83 ff ff               	callq	0x3370 <calloc@plt>
    afa3: 49 89 c4                     	movq	%rax, %r12
    afa6: 48 85 c0                     	testq	%rax, %rax
    afa9: 0f 84 f0 00 00 00            	je	0xb09f <input_panel_get_input_panel_surface+0x15f>
    afaf: 48 8d 05 ea fc ff ff         	leaq	-0x316(%rip), %rax      # 0xaca0 <input_panel_configure>
    afb6: 4c 89 a3 88 02 00 00         	movq	%r12, 0x288(%rbx)
    afbd: 48 89 df                     	movq	%rbx, %rdi
    afc0: 48 89 83 80 02 00 00         	movq	%rax, 0x280(%rbx)
    afc7: 4d 89 7c 24 18               	movq	%r15, 0x18(%r12)
    afcc: 49 89 5c 24 30               	movq	%rbx, 0x30(%r12)
    afd1: e8 3a 84 ff ff               	callq	0x3410 <weston_view_create@plt>
    afd6: 49 8d 7c 24 08               	leaq	0x8(%r12), %rdi
    afdb: 49 89 44 24 38               	movq	%rax, 0x38(%r12)
    afe0: e8 5b 83 ff ff               	callq	0x3340 <wl_list_init@plt>
    afe5: 48 8d 05 d4 fd ff ff         	leaq	-0x22c(%rip), %rax      # 0xadc0 <input_panel_handle_surface_destroy>
    afec: 49 89 44 24 50               	movq	%rax, 0x50(%r12)
    aff1: 48 8b 7b 08                  	movq	0x8(%rbx), %rdi
    aff5: 49 8d 74 24 40               	leaq	0x40(%r12), %rsi
    affa: e8 a1 86 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    afff: 49 8d 7c 24 20               	leaq	0x20(%r12), %rdi
    b004: e8 37 83 ff ff               	callq	0x3340 <wl_list_init@plt>
    b009: 44 89 f1                     	movl	%r14d, %ecx
    b00c: ba 01 00 00 00               	movl	$0x1, %edx
    b011: 4c 89 ef                     	movq	%r13, %rdi
    b014: 48 8b 35 9d 5f 20 00         	movq	0x205f9d(%rip), %rsi    # 0x210fb8 <_GLOBAL_OFFSET_TABLE_+0x3a0>
    b01b: e8 70 81 ff ff               	callq	0x3190 <wl_resource_create@plt>
    b020: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    b025: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    b02e: 49 89 04 24                  	movq	%rax, (%r12)
    b032: 0f 85 80 00 00 00            	jne	0xb0b8 <input_panel_get_input_panel_surface+0x178>
    b038: 48 83 c4 18                  	addq	$0x18, %rsp
    b03c: 4c 89 e2                     	movq	%r12, %rdx
    b03f: 48 89 c7                     	movq	%rax, %rdi
    b042: 5b                           	popq	%rbx
    b043: 48 8d 0d e6 f9 ff ff         	leaq	-0x61a(%rip), %rcx      # 0xaa30 <destroy_input_panel_surface_resource>
    b04a: 5d                           	popq	%rbp
    b04b: 41 5c                        	popq	%r12
    b04d: 41 5d                        	popq	%r13
    b04f: 41 5e                        	popq	%r14
    b051: 41 5f                        	popq	%r15
    b053: 48 8d 35 86 58 20 00         	leaq	0x205886(%rip), %rsi    # 0x2108e0 <input_panel_surface_implementation>
    b05a: e9 81 82 ff ff               	jmp	0x32e0 <wl_resource_set_implementation@plt>
    b05f: 90                           	nop
    b060: 48 83 bb 88 02 00 00 00      	cmpq	$0x0, 0x288(%rbx)
    b068: 0f 84 26 ff ff ff            	je	0xaf94 <input_panel_get_input_panel_surface+0x54>
    b06e: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    b073: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    b07c: 75 3a                        	jne	0xb0b8 <input_panel_get_input_panel_surface+0x178>
    b07e: 48 8d 15 3b 2b 00 00         	leaq	0x2b3b(%rip), %rdx      # 0xdbc0 <__PRETTY_FUNCTION__.12775+0x40>
    b085: 48 83 c4 18                  	addq	$0x18, %rsp
    b089: 48 89 ef                     	movq	%rbp, %rdi
    b08c: 31 f6                        	xorl	%esi, %esi
    b08e: 5b                           	popq	%rbx
    b08f: 31 c0                        	xorl	%eax, %eax
    b091: 5d                           	popq	%rbp
    b092: 41 5c                        	popq	%r12
    b094: 41 5d                        	popq	%r13
    b096: 41 5e                        	popq	%r14
    b098: 41 5f                        	popq	%r15
    b09a: e9 91 82 ff ff               	jmp	0x3330 <wl_resource_post_error@plt>
    b09f: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    b0a4: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    b0ad: 75 09                        	jne	0xb0b8 <input_panel_get_input_panel_surface+0x178>
    b0af: 48 8d 15 4a 2b 00 00         	leaq	0x2b4a(%rip), %rdx      # 0xdc00 <__PRETTY_FUNCTION__.12775+0x80>
    b0b6: eb cd                        	jmp	0xb085 <input_panel_get_input_panel_surface+0x145>
    b0b8: e8 63 81 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b0bd: 0f 1f 00                     	nopl	(%rax)

000000000000b0c0 <hide_input_panels>:
    b0c0: 55                           	pushq	%rbp
    b0c1: 53                           	pushq	%rbx
    b0c2: 48 83 ec 18                  	subq	$0x18, %rsp
    b0c6: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b0cf: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b0d4: 31 c0                        	xorl	%eax, %eax
    b0d6: 80 7f 69 00                  	cmpb	$0x0, 0x69(%rdi)
    b0da: 74 45                        	je	0xb121 <hide_input_panels+0x61>
    b0dc: 80 7f 68 00                  	cmpb	$0x0, 0x68(%rdi)
    b0e0: 48 89 fd                     	movq	%rdi, %rbp
    b0e3: c6 47 69 00                  	movb	$0x0, 0x69(%rdi)
    b0e7: 74 57                        	je	0xb140 <hide_input_panels+0x80>
    b0e9: 48 8b 45 38                  	movq	0x38(%rbp), %rax
    b0ed: 48 83 c5 30                  	addq	$0x30, %rbp
    b0f1: 48 8b 48 08                  	movq	0x8(%rax), %rcx
    b0f5: 48 8d 78 c8                  	leaq	-0x38(%rax), %rdi
    b0f9: 48 8d 59 c8                  	leaq	-0x38(%rcx), %rbx
    b0fd: 48 39 c5                     	cmpq	%rax, %rbp
    b100: 74 1f                        	je	0xb121 <hide_input_panels+0x61>
    b102: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    b108: e8 33 84 ff ff               	callq	0x3540 <weston_view_unmap@plt>
    b10d: 48 8b 53 40                  	movq	0x40(%rbx), %rdx
    b111: 48 8d 43 38                  	leaq	0x38(%rbx), %rax
    b115: 48 89 df                     	movq	%rbx, %rdi
    b118: 48 8d 5a c8                  	leaq	-0x38(%rdx), %rbx
    b11c: 48 39 e8                     	cmpq	%rbp, %rax
    b11f: 75 e7                        	jne	0xb108 <hide_input_panels+0x48>
    b121: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    b126: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    b12f: 75 1a                        	jne	0xb14b <hide_input_panels+0x8b>
    b131: 48 83 c4 18                  	addq	$0x18, %rsp
    b135: 5b                           	popq	%rbx
    b136: 5d                           	popq	%rbp
    b137: c3                           	retq
    b138: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    b140: 48 8d 7f 48                  	leaq	0x48(%rdi), %rdi
    b144: e8 e7 82 ff ff               	callq	0x3430 <wl_list_remove@plt>
    b149: eb 9e                        	jmp	0xb0e9 <hide_input_panels+0x29>
    b14b: e8 d0 80 ff ff               	callq	0x3220 <__stack_chk_fail@plt>

000000000000b150 <input_panel_destroy>:
    b150: 53                           	pushq	%rbx
    b151: 48 89 fb                     	movq	%rdi, %rbx
    b154: 48 83 c7 38                  	addq	$0x38, %rdi
    b158: 48 83 ec 10                  	subq	$0x10, %rsp
    b15c: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b165: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b16a: 31 c0                        	xorl	%eax, %eax
    b16c: e8 bf 82 ff ff               	callq	0x3430 <wl_list_remove@plt>
    b171: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    b176: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    b17f: 75 0e                        	jne	0xb18f <input_panel_destroy+0x3f>
    b181: 48 8d 7b 50                  	leaq	0x50(%rbx), %rdi
    b185: 48 83 c4 10                  	addq	$0x10, %rsp
    b189: 5b                           	popq	%rbx
    b18a: e9 a1 82 ff ff               	jmp	0x3430 <wl_list_remove@plt>
    b18f: e8 8c 80 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b194: 66 90                        	nop
    b196: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000b1a0 <input_panel_setup>:
    b1a0: 55                           	pushq	%rbp
    b1a1: 48 8d 77 38                  	leaq	0x38(%rdi), %rsi
    b1a5: 53                           	pushq	%rbx
    b1a6: 48 89 fb                     	movq	%rdi, %rbx
    b1a9: 48 83 ec 18                  	subq	$0x18, %rsp
    b1ad: 48 8b 6f 18                  	movq	0x18(%rdi), %rbp
    b1b1: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b1ba: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b1bf: 31 c0                        	xorl	%eax, %eax
    b1c1: 48 8d 05 a8 fc ff ff         	leaq	-0x358(%rip), %rax      # 0xae70 <show_input_panels>
    b1c8: 48 89 47 48                  	movq	%rax, 0x48(%rdi)
    b1cc: 48 8b bd e0 00 00 00         	movq	0xe0(%rbp), %rdi
    b1d3: e8 c8 84 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    b1d8: 48 8d 05 e1 fe ff ff         	leaq	-0x11f(%rip), %rax      # 0xb0c0 <hide_input_panels>
    b1df: 48 89 43 60                  	movq	%rax, 0x60(%rbx)
    b1e3: 48 8b bd f0 00 00 00         	movq	0xf0(%rbp), %rdi
    b1ea: 48 8d 73 50                  	leaq	0x50(%rbx), %rsi
    b1ee: e8 ad 84 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    b1f3: 48 8d 05 36 fc ff ff         	leaq	-0x3ca(%rip), %rax      # 0xae30 <update_input_panels>
    b1fa: 48 89 43 78                  	movq	%rax, 0x78(%rbx)
    b1fe: 48 8b bd 00 01 00 00         	movq	0x100(%rbp), %rdi
    b205: 48 8d 73 68                  	leaq	0x68(%rbx), %rsi
    b209: e8 92 84 ff ff               	callq	0x36a0 <wl_list_insert@plt>
    b20e: 48 8d bb e0 00 00 00         	leaq	0xe0(%rbx), %rdi
    b215: e8 26 81 ff ff               	callq	0x3340 <wl_list_init@plt>
    b21a: 48 8b 43 18                  	movq	0x18(%rbx), %rax
    b21e: 48 89 d9                     	movq	%rbx, %rcx
    b221: ba 01 00 00 00               	movl	$0x1, %edx
    b226: 48 8b 35 6b 5d 20 00         	movq	0x205d6b(%rip), %rsi    # 0x210f98 <_GLOBAL_OFFSET_TABLE_+0x380>
    b22d: 4c 8d 05 6c f6 ff ff         	leaq	-0x994(%rip), %r8       # 0xa8a0 <bind_input_panel>
    b234: 48 8b 78 10                  	movq	0x10(%rax), %rdi
    b238: e8 43 7e ff ff               	callq	0x3080 <wl_global_create@plt>
    b23d: 48 85 c0                     	testq	%rax, %rax
    b240: 0f 94 c0                     	sete	%al
    b243: 0f b6 c0                     	movzbl	%al, %eax
    b246: f7 d8                        	negl	%eax
    b248: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    b24d: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    b256: 75 07                        	jne	0xb25f <input_panel_setup+0xbf>
    b258: 48 83 c4 18                  	addq	$0x18, %rsp
    b25c: 5b                           	popq	%rbx
    b25d: 5d                           	popq	%rbp
    b25e: c3                           	retq
    b25f: e8 bc 7f ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b264: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    b26e: 66 90                        	nop

000000000000b270 <config_section_get_entry>:
    b270: 41 54                        	pushq	%r12
    b272: 55                           	pushq	%rbp
    b273: 53                           	pushq	%rbx
    b274: 48 83 ec 10                  	subq	$0x10, %rsp
    b278: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b281: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b286: 31 c0                        	xorl	%eax, %eax
    b288: 48 85 ff                     	testq	%rdi, %rdi
    b28b: 74 43                        	je	0xb2d0 <config_section_get_entry+0x60>
    b28d: 48 8b 47 10                  	movq	0x10(%rdi), %rax
    b291: 48 8d 6f 08                  	leaq	0x8(%rdi), %rbp
    b295: 49 89 f4                     	movq	%rsi, %r12
    b298: 48 8d 58 f0                  	leaq	-0x10(%rax), %rbx
    b29c: 48 39 c5                     	cmpq	%rax, %rbp
    b29f: 75 14                        	jne	0xb2b5 <config_section_get_entry+0x45>
    b2a1: eb 2d                        	jmp	0xb2d0 <config_section_get_entry+0x60>
    b2a3: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    b2a8: 48 8b 43 18                  	movq	0x18(%rbx), %rax
    b2ac: 48 8d 58 f0                  	leaq	-0x10(%rax), %rbx
    b2b0: 48 39 c5                     	cmpq	%rax, %rbp
    b2b3: 74 1b                        	je	0xb2d0 <config_section_get_entry+0x60>
    b2b5: 48 8b 3b                     	movq	(%rbx), %rdi
    b2b8: 4c 89 e6                     	movq	%r12, %rsi
    b2bb: e8 d0 80 ff ff               	callq	0x3390 <strcmp@plt>
    b2c0: 85 c0                        	testl	%eax, %eax
    b2c2: 75 e4                        	jne	0xb2a8 <config_section_get_entry+0x38>
    b2c4: 48 89 d8                     	movq	%rbx, %rax
    b2c7: eb 09                        	jmp	0xb2d2 <config_section_get_entry+0x62>
    b2c9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    b2d0: 31 c0                        	xorl	%eax, %eax
    b2d2: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    b2d7: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    b2e0: 75 09                        	jne	0xb2eb <config_section_get_entry+0x7b>
    b2e2: 48 83 c4 10                  	addq	$0x10, %rsp
    b2e6: 5b                           	popq	%rbx
    b2e7: 5d                           	popq	%rbp
    b2e8: 41 5c                        	popq	%r12
    b2ea: c3                           	retq
    b2eb: e8 30 7f ff ff               	callq	0x3220 <__stack_chk_fail@plt>

000000000000b2f0 <weston_config_get_section>:
    b2f0: 41 56                        	pushq	%r14
    b2f2: 41 55                        	pushq	%r13
    b2f4: 41 54                        	pushq	%r12
    b2f6: 55                           	pushq	%rbp
    b2f7: 53                           	pushq	%rbx
    b2f8: 48 83 ec 10                  	subq	$0x10, %rsp
    b2fc: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b305: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b30a: 31 c0                        	xorl	%eax, %eax
    b30c: 48 85 ff                     	testq	%rdi, %rdi
    b30f: 74 60                        	je	0xb371 <weston_config_get_section+0x81>
    b311: 48 8b 47 08                  	movq	0x8(%rdi), %rax
    b315: 48 89 fd                     	movq	%rdi, %rbp
    b318: 49 89 f4                     	movq	%rsi, %r12
    b31b: 49 89 d5                     	movq	%rdx, %r13
    b31e: 49 89 ce                     	movq	%rcx, %r14
    b321: 48 8d 58 e8                  	leaq	-0x18(%rax), %rbx
    b325: 48 39 c7                     	cmpq	%rax, %rdi
    b328: 74 47                        	je	0xb371 <weston_config_get_section+0x81>
    b32a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    b330: 48 8b 3b                     	movq	(%rbx), %rdi
    b333: 4c 89 e6                     	movq	%r12, %rsi
    b336: e8 55 80 ff ff               	callq	0x3390 <strcmp@plt>
    b33b: 85 c0                        	testl	%eax, %eax
    b33d: 75 25                        	jne	0xb364 <weston_config_get_section+0x74>
    b33f: 4d 85 ed                     	testq	%r13, %r13
    b342: 74 4c                        	je	0xb390 <weston_config_get_section+0xa0>
    b344: 4c 89 ee                     	movq	%r13, %rsi
    b347: 48 89 df                     	movq	%rbx, %rdi
    b34a: e8 21 ff ff ff               	callq	0xb270 <config_section_get_entry>
    b34f: 48 85 c0                     	testq	%rax, %rax
    b352: 74 10                        	je	0xb364 <weston_config_get_section+0x74>
    b354: 48 8b 78 08                  	movq	0x8(%rax), %rdi
    b358: 4c 89 f6                     	movq	%r14, %rsi
    b35b: e8 30 80 ff ff               	callq	0x3390 <strcmp@plt>
    b360: 85 c0                        	testl	%eax, %eax
    b362: 74 2c                        	je	0xb390 <weston_config_get_section+0xa0>
    b364: 48 8b 43 20                  	movq	0x20(%rbx), %rax
    b368: 48 8d 58 e8                  	leaq	-0x18(%rax), %rbx
    b36c: 48 39 c5                     	cmpq	%rax, %rbp
    b36f: 75 bf                        	jne	0xb330 <weston_config_get_section+0x40>
    b371: 31 c0                        	xorl	%eax, %eax
    b373: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    b378: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    b381: 75 12                        	jne	0xb395 <weston_config_get_section+0xa5>
    b383: 48 83 c4 10                  	addq	$0x10, %rsp
    b387: 5b                           	popq	%rbx
    b388: 5d                           	popq	%rbp
    b389: 41 5c                        	popq	%r12
    b38b: 41 5d                        	popq	%r13
    b38d: 41 5e                        	popq	%r14
    b38f: c3                           	retq
    b390: 48 89 d8                     	movq	%rbx, %rax
    b393: eb de                        	jmp	0xb373 <weston_config_get_section+0x83>
    b395: e8 86 7e ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b39a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)

000000000000b3a0 <weston_config_section_get_int>:
    b3a0: 55                           	pushq	%rbp
    b3a1: 89 cd                        	movl	%ecx, %ebp
    b3a3: 53                           	pushq	%rbx
    b3a4: 48 89 d3                     	movq	%rdx, %rbx
    b3a7: 48 83 ec 18                  	subq	$0x18, %rsp
    b3ab: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b3b4: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b3b9: 31 c0                        	xorl	%eax, %eax
    b3bb: e8 b0 fe ff ff               	callq	0xb270 <config_section_get_entry>
    b3c0: 48 85 c0                     	testq	%rax, %rax
    b3c3: 74 53                        	je	0xb418 <weston_config_section_get_int+0x78>
    b3c5: 48 8b 78 08                  	movq	0x8(%rax), %rdi
    b3c9: 31 d2                        	xorl	%edx, %edx
    b3cb: 48 89 e6                     	movq	%rsp, %rsi
    b3ce: e8 fd 7f ff ff               	callq	0x33d0 <strtol@plt>
    b3d3: 48 8b 14 24                  	movq	(%rsp), %rdx
    b3d7: 89 03                        	movl	%eax, (%rbx)
    b3d9: 31 c0                        	xorl	%eax, %eax
    b3db: 80 3a 00                     	cmpb	$0x0, (%rdx)
    b3de: 75 20                        	jne	0xb400 <weston_config_section_get_int+0x60>
    b3e0: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    b3e5: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    b3ee: 75 3c                        	jne	0xb42c <weston_config_section_get_int+0x8c>
    b3f0: 48 83 c4 18                  	addq	$0x18, %rsp
    b3f4: 5b                           	popq	%rbx
    b3f5: 5d                           	popq	%rbp
    b3f6: c3                           	retq
    b3f7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    b400: 89 2b                        	movl	%ebp, (%rbx)
    b402: e8 a9 7c ff ff               	callq	0x30b0 <__errno_location@plt>
    b407: c7 00 16 00 00 00            	movl	$0x16, (%rax)
    b40d: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b412: eb cc                        	jmp	0xb3e0 <weston_config_section_get_int+0x40>
    b414: 0f 1f 40 00                  	nopl	(%rax)
    b418: 89 2b                        	movl	%ebp, (%rbx)
    b41a: e8 91 7c ff ff               	callq	0x30b0 <__errno_location@plt>
    b41f: c7 00 02 00 00 00            	movl	$0x2, (%rax)
    b425: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b42a: eb b4                        	jmp	0xb3e0 <weston_config_section_get_int+0x40>
    b42c: e8 ef 7d ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b431: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    b436: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000b440 <weston_config_section_get_uint>:
    b440: 55                           	pushq	%rbp
    b441: 89 cd                        	movl	%ecx, %ebp
    b443: 53                           	pushq	%rbx
    b444: 48 89 d3                     	movq	%rdx, %rbx
    b447: 48 83 ec 18                  	subq	$0x18, %rsp
    b44b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b454: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b459: 31 c0                        	xorl	%eax, %eax
    b45b: e8 10 fe ff ff               	callq	0xb270 <config_section_get_entry>
    b460: 48 85 c0                     	testq	%rax, %rax
    b463: 74 53                        	je	0xb4b8 <weston_config_section_get_uint+0x78>
    b465: 48 8b 78 08                  	movq	0x8(%rax), %rdi
    b469: 31 d2                        	xorl	%edx, %edx
    b46b: 48 89 e6                     	movq	%rsp, %rsi
    b46e: e8 9d 81 ff ff               	callq	0x3610 <strtoul@plt>
    b473: 48 8b 14 24                  	movq	(%rsp), %rdx
    b477: 89 03                        	movl	%eax, (%rbx)
    b479: 31 c0                        	xorl	%eax, %eax
    b47b: 80 3a 00                     	cmpb	$0x0, (%rdx)
    b47e: 75 20                        	jne	0xb4a0 <weston_config_section_get_uint+0x60>
    b480: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    b485: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    b48e: 75 3c                        	jne	0xb4cc <weston_config_section_get_uint+0x8c>
    b490: 48 83 c4 18                  	addq	$0x18, %rsp
    b494: 5b                           	popq	%rbx
    b495: 5d                           	popq	%rbp
    b496: c3                           	retq
    b497: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    b4a0: 89 2b                        	movl	%ebp, (%rbx)
    b4a2: e8 09 7c ff ff               	callq	0x30b0 <__errno_location@plt>
    b4a7: c7 00 16 00 00 00            	movl	$0x16, (%rax)
    b4ad: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b4b2: eb cc                        	jmp	0xb480 <weston_config_section_get_uint+0x40>
    b4b4: 0f 1f 40 00                  	nopl	(%rax)
    b4b8: 89 2b                        	movl	%ebp, (%rbx)
    b4ba: e8 f1 7b ff ff               	callq	0x30b0 <__errno_location@plt>
    b4bf: c7 00 02 00 00 00            	movl	$0x2, (%rax)
    b4c5: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b4ca: eb b4                        	jmp	0xb480 <weston_config_section_get_uint+0x40>
    b4cc: e8 4f 7d ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b4d1: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    b4d6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000b4e0 <weston_config_section_get_double>:
    b4e0: 41 56                        	pushq	%r14
    b4e2: 66 49 0f 7e c6               	movq	%xmm0, %r14
    b4e7: 53                           	pushq	%rbx
    b4e8: 48 89 d3                     	movq	%rdx, %rbx
    b4eb: 48 83 ec 18                  	subq	$0x18, %rsp
    b4ef: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b4f8: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b4fd: 31 c0                        	xorl	%eax, %eax
    b4ff: e8 6c fd ff ff               	callq	0xb270 <config_section_get_entry>
    b504: 48 85 c0                     	testq	%rax, %rax
    b507: 74 4f                        	je	0xb558 <weston_config_section_get_double+0x78>
    b509: 48 8b 78 08                  	movq	0x8(%rax), %rdi
    b50d: 48 89 e6                     	movq	%rsp, %rsi
    b510: e8 2b 7c ff ff               	callq	0x3140 <strtod@plt>
    b515: 48 8b 14 24                  	movq	(%rsp), %rdx
    b519: 31 c0                        	xorl	%eax, %eax
    b51b: f2 0f 11 03                  	movsd	%xmm0, (%rbx)
    b51f: 80 3a 00                     	cmpb	$0x0, (%rdx)
    b522: 75 1c                        	jne	0xb540 <weston_config_section_get_double+0x60>
    b524: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    b529: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    b532: 75 39                        	jne	0xb56d <weston_config_section_get_double+0x8d>
    b534: 48 83 c4 18                  	addq	$0x18, %rsp
    b538: 5b                           	popq	%rbx
    b539: 41 5e                        	popq	%r14
    b53b: c3                           	retq
    b53c: 0f 1f 40 00                  	nopl	(%rax)
    b540: 4c 89 33                     	movq	%r14, (%rbx)
    b543: e8 68 7b ff ff               	callq	0x30b0 <__errno_location@plt>
    b548: c7 00 16 00 00 00            	movl	$0x16, (%rax)
    b54e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b553: eb cf                        	jmp	0xb524 <weston_config_section_get_double+0x44>
    b555: 0f 1f 00                     	nopl	(%rax)
    b558: 4c 89 33                     	movq	%r14, (%rbx)
    b55b: e8 50 7b ff ff               	callq	0x30b0 <__errno_location@plt>
    b560: c7 00 02 00 00 00            	movl	$0x2, (%rax)
    b566: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b56b: eb b7                        	jmp	0xb524 <weston_config_section_get_double+0x44>
    b56d: e8 ae 7c ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b572: 0f 1f 40 00                  	nopl	(%rax)
    b576: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000b580 <weston_config_section_get_string>:
    b580: 55                           	pushq	%rbp
    b581: 48 89 cd                     	movq	%rcx, %rbp
    b584: 53                           	pushq	%rbx
    b585: 48 89 d3                     	movq	%rdx, %rbx
    b588: 48 83 ec 18                  	subq	$0x18, %rsp
    b58c: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b595: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b59a: 31 c0                        	xorl	%eax, %eax
    b59c: e8 cf fc ff ff               	callq	0xb270 <config_section_get_entry>
    b5a1: 48 85 c0                     	testq	%rax, %rax
    b5a4: 74 2a                        	je	0xb5d0 <weston_config_section_get_string+0x50>
    b5a6: 48 8b 78 08                  	movq	0x8(%rax), %rdi
    b5aa: e8 71 7d ff ff               	callq	0x3320 <__strdup@plt>
    b5af: 48 89 03                     	movq	%rax, (%rbx)
    b5b2: 31 c0                        	xorl	%eax, %eax
    b5b4: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    b5b9: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    b5c2: 75 37                        	jne	0xb5fb <weston_config_section_get_string+0x7b>
    b5c4: 48 83 c4 18                  	addq	$0x18, %rsp
    b5c8: 5b                           	popq	%rbx
    b5c9: 5d                           	popq	%rbp
    b5ca: c3                           	retq
    b5cb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    b5d0: 48 85 ed                     	testq	%rbp, %rbp
    b5d3: 74 1d                        	je	0xb5f2 <weston_config_section_get_string+0x72>
    b5d5: 48 89 ef                     	movq	%rbp, %rdi
    b5d8: e8 43 7d ff ff               	callq	0x3320 <__strdup@plt>
    b5dd: 48 89 03                     	movq	%rax, (%rbx)
    b5e0: e8 cb 7a ff ff               	callq	0x30b0 <__errno_location@plt>
    b5e5: c7 00 02 00 00 00            	movl	$0x2, (%rax)
    b5eb: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b5f0: eb c2                        	jmp	0xb5b4 <weston_config_section_get_string+0x34>
    b5f2: 48 c7 03 00 00 00 00         	movq	$0x0, (%rbx)
    b5f9: eb e5                        	jmp	0xb5e0 <weston_config_section_get_string+0x60>
    b5fb: e8 20 7c ff ff               	callq	0x3220 <__stack_chk_fail@plt>

000000000000b600 <weston_config_section_get_bool>:
    b600: 55                           	pushq	%rbp
    b601: 48 89 d5                     	movq	%rdx, %rbp
    b604: 53                           	pushq	%rbx
    b605: 89 cb                        	movl	%ecx, %ebx
    b607: 48 83 ec 18                  	subq	$0x18, %rsp
    b60b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b614: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b619: 31 c0                        	xorl	%eax, %eax
    b61b: e8 50 fc ff ff               	callq	0xb270 <config_section_get_entry>
    b620: 48 85 c0                     	testq	%rax, %rax
    b623: 0f 84 8c 00 00 00            	je	0xb6b5 <weston_config_section_get_bool+0xb5>
    b629: 4c 8b 40 08                  	movq	0x8(%rax), %r8
    b62d: b9 06 00 00 00               	movl	$0x6, %ecx
    b632: 48 8d 3d 32 26 00 00         	leaq	0x2632(%rip), %rdi      # 0xdc6b <__PRETTY_FUNCTION__.12775+0xeb>
    b639: 4c 89 c6                     	movq	%r8, %rsi
    b63c: f3 a6                        	rep		cmpsb	%es:(%rdi), (%rsi)
    b63e: 0f 97 c0                     	seta	%al
    b641: 0f 92 c2                     	setb	%dl
    b644: 29 d0                        	subl	%edx, %eax
    b646: 0f be c0                     	movsbl	%al, %eax
    b649: 85 c0                        	testl	%eax, %eax
    b64b: 74 43                        	je	0xb690 <weston_config_section_get_bool+0x90>
    b64d: 48 8d 3d 1d 26 00 00         	leaq	0x261d(%rip), %rdi      # 0xdc71 <__PRETTY_FUNCTION__.12775+0xf1>
    b654: b9 05 00 00 00               	movl	$0x5, %ecx
    b659: 4c 89 c6                     	movq	%r8, %rsi
    b65c: f3 a6                        	rep		cmpsb	%es:(%rdi), (%rsi)
    b65e: 0f 97 c0                     	seta	%al
    b661: 0f 92 c2                     	setb	%dl
    b664: 29 d0                        	subl	%edx, %eax
    b666: 0f be c0                     	movsbl	%al, %eax
    b669: 85 c0                        	testl	%eax, %eax
    b66b: 75 33                        	jne	0xb6a0 <weston_config_section_get_bool+0xa0>
    b66d: c7 45 00 01 00 00 00         	movl	$0x1, (%rbp)
    b674: 48 8b 5c 24 08               	movq	0x8(%rsp), %rbx
    b679: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
    b682: 75 46                        	jne	0xb6ca <weston_config_section_get_bool+0xca>
    b684: 48 83 c4 18                  	addq	$0x18, %rsp
    b688: 5b                           	popq	%rbx
    b689: 5d                           	popq	%rbp
    b68a: c3                           	retq
    b68b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    b690: c7 45 00 00 00 00 00         	movl	$0x0, (%rbp)
    b697: eb db                        	jmp	0xb674 <weston_config_section_get_bool+0x74>
    b699: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    b6a0: 89 5d 00                     	movl	%ebx, (%rbp)
    b6a3: e8 08 7a ff ff               	callq	0x30b0 <__errno_location@plt>
    b6a8: c7 00 16 00 00 00            	movl	$0x16, (%rax)
    b6ae: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b6b3: eb bf                        	jmp	0xb674 <weston_config_section_get_bool+0x74>
    b6b5: 89 5d 00                     	movl	%ebx, (%rbp)
    b6b8: e8 f3 79 ff ff               	callq	0x30b0 <__errno_location@plt>
    b6bd: c7 00 02 00 00 00            	movl	$0x2, (%rax)
    b6c3: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    b6c8: eb aa                        	jmp	0xb674 <weston_config_section_get_bool+0x74>
    b6ca: e8 51 7b ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b6cf: 90                           	nop

000000000000b6d0 <weston_config_get_libexec_dir>:
    b6d0: 48 8d 3d ac 25 00 00         	leaq	0x25ac(%rip), %rdi      # 0xdc83 <__PRETTY_FUNCTION__.12775+0x103>
    b6d7: 48 83 ec 18                  	subq	$0x18, %rsp
    b6db: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b6e4: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b6e9: 31 c0                        	xorl	%eax, %eax
    b6eb: e8 60 79 ff ff               	callq	0x3050 <getenv@plt>
    b6f0: 48 8d 15 7f 25 00 00         	leaq	0x257f(%rip), %rdx      # 0xdc76 <__PRETTY_FUNCTION__.12775+0xf6>
    b6f7: 48 85 c0                     	testq	%rax, %rax
    b6fa: 48 0f 44 c2                  	cmoveq	%rdx, %rax
    b6fe: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    b703: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    b70c: 75 05                        	jne	0xb713 <weston_config_get_libexec_dir+0x43>
    b70e: 48 83 c4 18                  	addq	$0x18, %rsp
    b712: c3                           	retq
    b713: e8 08 7b ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b718: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

000000000000b720 <weston_config_get_name_from_env>:
    b720: 48 8d 3d 78 25 00 00         	leaq	0x2578(%rip), %rdi      # 0xdc9f <__PRETTY_FUNCTION__.12775+0x11f>
    b727: 48 83 ec 18                  	subq	$0x18, %rsp
    b72b: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b734: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b739: 31 c0                        	xorl	%eax, %eax
    b73b: e8 10 79 ff ff               	callq	0x3050 <getenv@plt>
    b740: 48 8d 15 4d 25 00 00         	leaq	0x254d(%rip), %rdx      # 0xdc94 <__PRETTY_FUNCTION__.12775+0x114>
    b747: 48 85 c0                     	testq	%rax, %rax
    b74a: 48 0f 44 c2                  	cmoveq	%rdx, %rax
    b74e: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    b753: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    b75c: 75 05                        	jne	0xb763 <weston_config_get_name_from_env+0x43>
    b75e: 48 83 c4 18                  	addq	$0x18, %rsp
    b762: c3                           	retq
    b763: e8 b8 7a ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b768: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)

000000000000b770 <weston_config_get_full_path>:
    b770: 48 83 ec 18                  	subq	$0x18, %rsp
    b774: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b77d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b782: 31 c0                        	xorl	%eax, %eax
    b784: 48 85 ff                     	testq	%rdi, %rdi
    b787: 74 1f                        	je	0xb7a8 <weston_config_get_full_path+0x38>
    b789: 48 8d 47 10                  	leaq	0x10(%rdi), %rax
    b78d: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    b792: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    b79b: 75 0f                        	jne	0xb7ac <weston_config_get_full_path+0x3c>
    b79d: 48 83 c4 18                  	addq	$0x18, %rsp
    b7a1: c3                           	retq
    b7a2: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    b7a8: 31 c0                        	xorl	%eax, %eax
    b7aa: eb e1                        	jmp	0xb78d <weston_config_get_full_path+0x1d>
    b7ac: e8 6f 7a ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b7b1: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    b7b6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000b7c0 <weston_config_next_section>:
    b7c0: 48 83 ec 18                  	subq	$0x18, %rsp
    b7c4: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b7cd: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b7d2: 31 c0                        	xorl	%eax, %eax
    b7d4: 48 85 ff                     	testq	%rdi, %rdi
    b7d7: 74 3f                        	je	0xb818 <weston_config_next_section+0x58>
    b7d9: 48 8b 06                     	movq	(%rsi), %rax
    b7dc: 48 85 c0                     	testq	%rax, %rax
    b7df: 74 3f                        	je	0xb820 <weston_config_next_section+0x60>
    b7e1: 48 8b 40 20                  	movq	0x20(%rax), %rax
    b7e5: 48 83 e8 18                  	subq	$0x18, %rax
    b7e9: 48 89 06                     	movq	%rax, (%rsi)
    b7ec: 48 8d 48 18                  	leaq	0x18(%rax), %rcx
    b7f0: 48 39 cf                     	cmpq	%rcx, %rdi
    b7f3: 74 23                        	je	0xb818 <weston_config_next_section+0x58>
    b7f5: 48 8b 00                     	movq	(%rax), %rax
    b7f8: 48 89 02                     	movq	%rax, (%rdx)
    b7fb: b8 01 00 00 00               	movl	$0x1, %eax
    b800: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    b805: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    b80e: 75 1d                        	jne	0xb82d <weston_config_next_section+0x6d>
    b810: 48 83 c4 18                  	addq	$0x18, %rsp
    b814: c3                           	retq
    b815: 0f 1f 00                     	nopl	(%rax)
    b818: 31 c0                        	xorl	%eax, %eax
    b81a: eb e4                        	jmp	0xb800 <weston_config_next_section+0x40>
    b81c: 0f 1f 40 00                  	nopl	(%rax)
    b820: 48 8b 47 08                  	movq	0x8(%rdi), %rax
    b824: 48 83 e8 18                  	subq	$0x18, %rax
    b828: 48 89 06                     	movq	%rax, (%rsi)
    b82b: eb bf                        	jmp	0xb7ec <weston_config_next_section+0x2c>
    b82d: e8 ee 79 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b832: 0f 1f 40 00                  	nopl	(%rax)
    b836: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000b840 <weston_config_destroy>:
    b840: 41 57                        	pushq	%r15
    b842: 41 56                        	pushq	%r14
    b844: 41 55                        	pushq	%r13
    b846: 41 54                        	pushq	%r12
    b848: 55                           	pushq	%rbp
    b849: 53                           	pushq	%rbx
    b84a: 48 83 ec 18                  	subq	$0x18, %rsp
    b84e: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b857: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    b85c: 31 c0                        	xorl	%eax, %eax
    b85e: 48 85 ff                     	testq	%rdi, %rdi
    b861: 0f 84 b7 00 00 00            	je	0xb91e <weston_config_destroy+0xde>
    b867: 48 8b 47 08                  	movq	0x8(%rdi), %rax
    b86b: 49 89 ff                     	movq	%rdi, %r15
    b86e: 48 8b 70 08                  	movq	0x8(%rax), %rsi
    b872: 4c 8d 68 e8                  	leaq	-0x18(%rax), %r13
    b876: 4c 8d 76 e8                  	leaq	-0x18(%rsi), %r14
    b87a: 48 39 c7                     	cmpq	%rax, %rdi
    b87d: 74 79                        	je	0xb8f8 <weston_config_destroy+0xb8>
    b87f: 90                           	nop
    b880: 49 8b 45 10                  	movq	0x10(%r13), %rax
    b884: 4d 8d 65 08                  	leaq	0x8(%r13), %r12
    b888: 48 8b 48 08                  	movq	0x8(%rax), %rcx
    b88c: 48 8d 68 f0                  	leaq	-0x10(%rax), %rbp
    b890: 48 8d 59 f0                  	leaq	-0x10(%rcx), %rbx
    b894: 49 39 c4                     	cmpq	%rax, %r12
    b897: 74 35                        	je	0xb8ce <weston_config_destroy+0x8e>
    b899: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    b8a0: 48 8b 7d 00                  	movq	(%rbp), %rdi
    b8a4: e8 c7 77 ff ff               	callq	0x3070 <free@plt>
    b8a9: 48 8b 7d 08                  	movq	0x8(%rbp), %rdi
    b8ad: e8 be 77 ff ff               	callq	0x3070 <free@plt>
    b8b2: 48 89 ef                     	movq	%rbp, %rdi
    b8b5: 48 89 dd                     	movq	%rbx, %rbp
    b8b8: e8 b3 77 ff ff               	callq	0x3070 <free@plt>
    b8bd: 48 8b 53 18                  	movq	0x18(%rbx), %rdx
    b8c1: 48 8d 43 10                  	leaq	0x10(%rbx), %rax
    b8c5: 48 8d 5a f0                  	leaq	-0x10(%rdx), %rbx
    b8c9: 4c 39 e0                     	cmpq	%r12, %rax
    b8cc: 75 d2                        	jne	0xb8a0 <weston_config_destroy+0x60>
    b8ce: 49 8b 7d 00                  	movq	(%r13), %rdi
    b8d2: e8 99 77 ff ff               	callq	0x3070 <free@plt>
    b8d7: 4c 89 ef                     	movq	%r13, %rdi
    b8da: 4d 89 f5                     	movq	%r14, %r13
    b8dd: e8 8e 77 ff ff               	callq	0x3070 <free@plt>
    b8e2: 49 8b 46 20                  	movq	0x20(%r14), %rax
    b8e6: 49 8d 56 18                  	leaq	0x18(%r14), %rdx
    b8ea: 48 83 e8 18                  	subq	$0x18, %rax
    b8ee: 49 39 d7                     	cmpq	%rdx, %r15
    b8f1: 74 05                        	je	0xb8f8 <weston_config_destroy+0xb8>
    b8f3: 49 89 c6                     	movq	%rax, %r14
    b8f6: eb 88                        	jmp	0xb880 <weston_config_destroy+0x40>
    b8f8: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    b8fd: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    b906: 75 35                        	jne	0xb93d <weston_config_destroy+0xfd>
    b908: 48 83 c4 18                  	addq	$0x18, %rsp
    b90c: 4c 89 ff                     	movq	%r15, %rdi
    b90f: 5b                           	popq	%rbx
    b910: 5d                           	popq	%rbp
    b911: 41 5c                        	popq	%r12
    b913: 41 5d                        	popq	%r13
    b915: 41 5e                        	popq	%r14
    b917: 41 5f                        	popq	%r15
    b919: e9 52 77 ff ff               	jmp	0x3070 <free@plt>
    b91e: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    b923: 64 48 33 04 25 28 00 00 00   	xorq	%fs:0x28, %rax
    b92c: 75 0f                        	jne	0xb93d <weston_config_destroy+0xfd>
    b92e: 48 83 c4 18                  	addq	$0x18, %rsp
    b932: 5b                           	popq	%rbx
    b933: 5d                           	popq	%rbp
    b934: 41 5c                        	popq	%r12
    b936: 41 5d                        	popq	%r13
    b938: 41 5e                        	popq	%r14
    b93a: 41 5f                        	popq	%r15
    b93c: c3                           	retq
    b93d: e8 de 78 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    b942: 0f 1f 40 00                  	nopl	(%rax)
    b946: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000b950 <weston_config_parse>:
    b950: 41 57                        	pushq	%r15
    b952: 49 89 ff                     	movq	%rdi, %r15
    b955: bf 10 10 00 00               	movl	$0x1010, %edi           # imm = 0x1010
    b95a: 41 56                        	pushq	%r14
    b95c: 41 55                        	pushq	%r13
    b95e: 41 54                        	pushq	%r12
    b960: 55                           	pushq	%rbp
    b961: 53                           	pushq	%rbx
    b962: 48 81 ec b8 02 00 00         	subq	$0x2b8, %rsp            # imm = 0x2B8
    b969: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    b972: 48 89 84 24 a8 02 00 00      	movq	%rax, 0x2a8(%rsp)
    b97a: 31 c0                        	xorl	%eax, %eax
    b97c: e8 ef 7a ff ff               	callq	0x3470 <malloc@plt>
    b981: 48 85 c0                     	testq	%rax, %rax
    b984: 0f 84 55 04 00 00            	je	0xbddf <weston_config_parse+0x48f>
    b98a: 48 89 c7                     	movq	%rax, %rdi
    b98d: 48 89 c3                     	movq	%rax, %rbx
    b990: e8 ab 79 ff ff               	callq	0x3340 <wl_list_init@plt>
    b995: 48 8d 3d 1f 23 00 00         	leaq	0x231f(%rip), %rdi      # 0xdcbb <__PRETTY_FUNCTION__.12775+0x13b>
    b99c: e8 af 76 ff ff               	callq	0x3050 <getenv@plt>
    b9a1: 48 8d 3d 1e 23 00 00         	leaq	0x231e(%rip), %rdi      # 0xdcc6 <__PRETTY_FUNCTION__.12775+0x146>
    b9a8: 49 89 c5                     	movq	%rax, %r13
    b9ab: e8 a0 76 ff ff               	callq	0x3050 <getenv@plt>
    b9b0: 48 8d 3d 14 23 00 00         	leaq	0x2314(%rip), %rdi      # 0xdccb <__PRETTY_FUNCTION__.12775+0x14b>
    b9b7: 48 89 c5                     	movq	%rax, %rbp
    b9ba: e8 91 76 ff ff               	callq	0x3050 <getenv@plt>
    b9bf: 41 80 3f 2f                  	cmpb	$0x2f, (%r15)
    b9c3: 49 89 c4                     	movq	%rax, %r12
    b9c6: 0f 84 c6 03 00 00            	je	0xbd92 <weston_config_parse+0x442>
    b9cc: 4c 8d 73 10                  	leaq	0x10(%rbx), %r14
    b9d0: 4d 85 ed                     	testq	%r13, %r13
    b9d3: 0f 84 1f 02 00 00            	je	0xbbf8 <weston_config_parse+0x2a8>
    b9d9: 48 83 ec 08                  	subq	$0x8, %rsp
    b9dd: 4d 89 e9                     	movq	%r13, %r9
    b9e0: b9 00 10 00 00               	movl	$0x1000, %ecx           # imm = 0x1000
    b9e5: 41 57                        	pushq	%r15
    b9e7: 4c 8d 05 ed 22 00 00         	leaq	0x22ed(%rip), %r8       # 0xdcdb <__PRETTY_FUNCTION__.12775+0x15b>
    b9ee: 4c 89 f7                     	movq	%r14, %rdi
    b9f1: 31 c0                        	xorl	%eax, %eax
    b9f3: ba 01 00 00 00               	movl	$0x1, %edx
    b9f8: be 00 10 00 00               	movl	$0x1000, %esi           # imm = 0x1000
    b9fd: e8 5e 76 ff ff               	callq	0x3060 <__snprintf_chk@plt>
    ba02: 4c 89 f7                     	movq	%r14, %rdi
    ba05: be 00 00 08 00               	movl	$0x80000, %esi          # imm = 0x80000
    ba0a: 31 c0                        	xorl	%eax, %eax
    ba0c: e8 8f 7b ff ff               	callq	0x35a0 <open@plt>
    ba11: 5f                           	popq	%rdi
    ba12: 41 89 c5                     	movl	%eax, %r13d
    ba15: 41 58                        	popq	%r8
    ba17: 85 c0                        	testl	%eax, %eax
    ba19: 0f 88 d9 01 00 00            	js	0xbbf8 <weston_config_parse+0x2a8>
    ba1f: 48 8d 54 24 10               	leaq	0x10(%rsp), %rdx
    ba24: 44 89 ee                     	movl	%r13d, %esi
    ba27: bf 01 00 00 00               	movl	$0x1, %edi
    ba2c: e8 7f 7a ff ff               	callq	0x34b0 <__fxstat@plt>
    ba31: 85 c0                        	testl	%eax, %eax
    ba33: 0f 88 9f 02 00 00            	js	0xbcd8 <weston_config_parse+0x388>
    ba39: 8b 44 24 28                  	movl	0x28(%rsp), %eax
    ba3d: 25 00 f0 00 00               	andl	$0xf000, %eax           # imm = 0xF000
    ba42: 3d 00 80 00 00               	cmpl	$0x8000, %eax           # imm = 0x8000
    ba47: 0f 85 8b 02 00 00            	jne	0xbcd8 <weston_config_parse+0x388>
    ba4d: 48 8d 35 af 22 00 00         	leaq	0x22af(%rip), %rsi      # 0xdd03 <__PRETTY_FUNCTION__.12775+0x183>
    ba54: 44 89 ef                     	movl	%r13d, %edi
    ba57: e8 a4 7a ff ff               	callq	0x3500 <fdopen@plt>
    ba5c: 49 89 c5                     	movq	%rax, %r13
    ba5f: 48 85 c0                     	testq	%rax, %rax
    ba62: 0f 84 78 02 00 00            	je	0xbce0 <weston_config_parse+0x390>
    ba68: 48 8d ac 24 a0 00 00 00      	leaq	0xa0(%rsp), %rbp
    ba70: 45 31 e4                     	xorl	%r12d, %r12d
    ba73: 48 8d 45 01                  	leaq	0x1(%rbp), %rax
    ba77: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    ba7c: 0f 1f 40 00                  	nopl	(%rax)
    ba80: 4c 89 ea                     	movq	%r13, %rdx
    ba83: be 00 02 00 00               	movl	$0x200, %esi            # imm = 0x200
    ba88: 48 89 ef                     	movq	%rbp, %rdi
    ba8b: e8 c0 78 ff ff               	callq	0x3350 <fgets@plt>
    ba90: 48 85 c0                     	testq	%rax, %rax
    ba93: 0f 84 27 03 00 00            	je	0xbdc0 <weston_config_parse+0x470>
    ba99: 0f b6 84 24 a0 00 00 00      	movzbl	0xa0(%rsp), %eax
    baa1: 3c 23                        	cmpb	$0x23, %al
    baa3: 74 db                        	je	0xba80 <weston_config_parse+0x130>
    baa5: 3c 5b                        	cmpb	$0x5b, %al
    baa7: 0f 84 e3 00 00 00            	je	0xbb90 <weston_config_parse+0x240>
    baad: 3c 0a                        	cmpb	$0xa, %al
    baaf: 74 cf                        	je	0xba80 <weston_config_parse+0x130>
    bab1: be 3d 00 00 00               	movl	$0x3d, %esi
    bab6: 48 89 ef                     	movq	%rbp, %rdi
    bab9: e8 92 77 ff ff               	callq	0x3250 <strchr@plt>
    babe: 48 39 e8                     	cmpq	%rbp, %rax
    bac1: 0f 94 c1                     	sete	%cl
    bac4: 48 85 c0                     	testq	%rax, %rax
    bac7: 0f 94 c2                     	sete	%dl
    baca: 08 d1                        	orb	%dl, %cl
    bacc: 0f 85 fe 02 00 00            	jne	0xbdd0 <weston_config_parse+0x480>
    bad2: 4d 85 e4                     	testq	%r12, %r12
    bad5: 0f 84 f5 02 00 00            	je	0xbdd0 <weston_config_parse+0x480>
    badb: c6 00 00                     	movb	$0x0, (%rax)
    bade: 4c 8d 78 01                  	leaq	0x1(%rax), %r15
    bae2: e8 09 7c ff ff               	callq	0x36f0 <__ctype_b_loc@plt>
    bae7: 4c 8b 30                     	movq	(%rax), %r14
    baea: eb 08                        	jmp	0xbaf4 <weston_config_parse+0x1a4>
    baec: 0f 1f 40 00                  	nopl	(%rax)
    baf0: 49 83 c7 01                  	addq	$0x1, %r15
    baf4: 49 0f be 07                  	movsbq	(%r15), %rax
    baf8: 41 f6 44 46 01 20            	testb	$0x20, 0x1(%r14,%rax,2)
    bafe: 75 f0                        	jne	0xbaf0 <weston_config_parse+0x1a0>
    bb00: 4c 89 ff                     	movq	%r15, %rdi
    bb03: e8 f8 76 ff ff               	callq	0x3200 <strlen@plt>
    bb08: 85 c0                        	testl	%eax, %eax
    bb0a: 7e 40                        	jle	0xbb4c <weston_config_parse+0x1fc>
    bb0c: 48 63 f0                     	movslq	%eax, %rsi
    bb0f: 4d 8d 44 37 ff               	leaq	-0x1(%r15,%rsi), %r8
    bb14: 49 0f be 10                  	movsbq	(%r8), %rdx
    bb18: 41 f6 44 56 01 20            	testb	$0x20, 0x1(%r14,%rdx,2)
    bb1e: 74 2c                        	je	0xbb4c <weston_config_parse+0x1fc>
    bb20: 31 d2                        	xorl	%edx, %edx
    bb22: 4c 01 fe                     	addq	%r15, %rsi
    bb25: 8d 78 ff                     	leal	-0x1(%rax), %edi
    bb28: 48 f7 df                     	negq	%rdi
    bb2b: eb 15                        	jmp	0xbb42 <weston_config_parse+0x1f2>
    bb2d: 0f 1f 00                     	nopl	(%rax)
    bb30: 48 0f be 44 16 fe            	movsbq	-0x2(%rsi,%rdx), %rax
    bb36: 48 83 ea 01                  	subq	$0x1, %rdx
    bb3a: 41 f6 44 46 01 20            	testb	$0x20, 0x1(%r14,%rax,2)
    bb40: 74 0a                        	je	0xbb4c <weston_config_parse+0x1fc>
    bb42: 41 c6 04 10 00               	movb	$0x0, (%r8,%rdx)
    bb47: 48 39 d7                     	cmpq	%rdx, %rdi
    bb4a: 75 e4                        	jne	0xbb30 <weston_config_parse+0x1e0>
    bb4c: bf 20 00 00 00               	movl	$0x20, %edi
    bb51: e8 1a 79 ff ff               	callq	0x3470 <malloc@plt>
    bb56: 49 89 c6                     	movq	%rax, %r14
    bb59: 48 85 c0                     	testq	%rax, %rax
    bb5c: 0f 84 1e ff ff ff            	je	0xba80 <weston_config_parse+0x130>
    bb62: 48 89 ef                     	movq	%rbp, %rdi
    bb65: e8 b6 77 ff ff               	callq	0x3320 <__strdup@plt>
    bb6a: 4c 89 ff                     	movq	%r15, %rdi
    bb6d: 49 89 06                     	movq	%rax, (%r14)
    bb70: e8 ab 77 ff ff               	callq	0x3320 <__strdup@plt>
    bb75: 49 8b 7c 24 08               	movq	0x8(%r12), %rdi
    bb7a: 49 8d 76 10                  	leaq	0x10(%r14), %rsi
    bb7e: 49 89 46 08                  	movq	%rax, 0x8(%r14)
    bb82: e8 19 7b ff ff               	callq	0x36a0 <wl_list_insert@plt>
    bb87: e9 f4 fe ff ff               	jmp	0xba80 <weston_config_parse+0x130>
    bb8c: 0f 1f 40 00                  	nopl	(%rax)
    bb90: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
    bb95: be 5d 00 00 00               	movl	$0x5d, %esi
    bb9a: e8 b1 76 ff ff               	callq	0x3250 <strchr@plt>
    bb9f: 48 85 c0                     	testq	%rax, %rax
    bba2: 0f 84 70 01 00 00            	je	0xbd18 <weston_config_parse+0x3c8>
    bba8: 80 78 01 0a                  	cmpb	$0xa, 0x1(%rax)
    bbac: 0f 85 66 01 00 00            	jne	0xbd18 <weston_config_parse+0x3c8>
    bbb2: c6 00 00                     	movb	$0x0, (%rax)
    bbb5: bf 28 00 00 00               	movl	$0x28, %edi
    bbba: e8 b1 78 ff ff               	callq	0x3470 <malloc@plt>
    bbbf: 49 89 c4                     	movq	%rax, %r12
    bbc2: 48 85 c0                     	testq	%rax, %rax
    bbc5: 0f 84 b5 fe ff ff            	je	0xba80 <weston_config_parse+0x130>
    bbcb: 48 8b 7c 24 08               	movq	0x8(%rsp), %rdi
    bbd0: e8 4b 77 ff ff               	callq	0x3320 <__strdup@plt>
    bbd5: 49 8d 7c 24 08               	leaq	0x8(%r12), %rdi
    bbda: 49 89 04 24                  	movq	%rax, (%r12)
    bbde: e8 5d 77 ff ff               	callq	0x3340 <wl_list_init@plt>
    bbe3: 48 8b 3b                     	movq	(%rbx), %rdi
    bbe6: 49 8d 74 24 18               	leaq	0x18(%r12), %rsi
    bbeb: e8 b0 7a ff ff               	callq	0x36a0 <wl_list_insert@plt>
    bbf0: e9 8b fe ff ff               	jmp	0xba80 <weston_config_parse+0x130>
    bbf5: 0f 1f 00                     	nopl	(%rax)
    bbf8: 48 85 ed                     	testq	%rbp, %rbp
    bbfb: 74 45                        	je	0xbc42 <weston_config_parse+0x2f2>
    bbfd: 48 83 ec 08                  	subq	$0x8, %rsp
    bc01: b9 00 10 00 00               	movl	$0x1000, %ecx           # imm = 0x1000
    bc06: 49 89 e9                     	movq	%rbp, %r9
    bc09: 41 57                        	pushq	%r15
    bc0b: 4c 8d 05 cf 20 00 00         	leaq	0x20cf(%rip), %r8       # 0xdce1 <__PRETTY_FUNCTION__.12775+0x161>
    bc12: 4c 89 f7                     	movq	%r14, %rdi
    bc15: 31 c0                        	xorl	%eax, %eax
    bc17: ba 01 00 00 00               	movl	$0x1, %edx
    bc1c: be 00 10 00 00               	movl	$0x1000, %esi           # imm = 0x1000
    bc21: e8 3a 74 ff ff               	callq	0x3060 <__snprintf_chk@plt>
    bc26: be 00 00 08 00               	movl	$0x80000, %esi          # imm = 0x80000
    bc2b: 4c 89 f7                     	movq	%r14, %rdi
    bc2e: 31 c0                        	xorl	%eax, %eax
    bc30: e8 6b 79 ff ff               	callq	0x35a0 <open@plt>
    bc35: 59                           	popq	%rcx
    bc36: 41 89 c5                     	movl	%eax, %r13d
    bc39: 5e                           	popq	%rsi
    bc3a: 85 c0                        	testl	%eax, %eax
    bc3c: 0f 89 dd fd ff ff            	jns	0xba1f <weston_config_parse+0xcf>
    bc42: 48 8d 05 69 20 00 00         	leaq	0x2069(%rip), %rax      # 0xdcb2 <__PRETTY_FUNCTION__.12775+0x132>
    bc49: 4d 85 e4                     	testq	%r12, %r12
    bc4c: 4c 0f 44 e0                  	cmoveq	%rax, %r12
    bc50: 41 0f b6 04 24               	movzbl	(%r12), %eax
    bc55: eb 0c                        	jmp	0xbc63 <weston_config_parse+0x313>
    bc57: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    bc60: 49 89 ec                     	movq	%rbp, %r12
    bc63: 84 c0                        	testb	%al, %al
    bc65: 0f 84 e5 00 00 00            	je	0xbd50 <weston_config_parse+0x400>
    bc6b: be 3a 00 00 00               	movl	$0x3a, %esi
    bc70: 4c 89 e7                     	movq	%r12, %rdi
    bc73: e8 d8 74 ff ff               	callq	0x3150 <strchrnul@plt>
    bc78: 41 57                        	pushq	%r15
    bc7a: ba 01 00 00 00               	movl	$0x1, %edx
    bc7f: 4c 89 f7                     	movq	%r14, %rdi
    bc82: 41 89 c1                     	movl	%eax, %r9d
    bc85: 41 54                        	pushq	%r12
    bc87: b9 00 10 00 00               	movl	$0x1000, %ecx           # imm = 0x1000
    bc8c: be 00 10 00 00               	movl	$0x1000, %esi           # imm = 0x1000
    bc91: 4c 8d 05 57 20 00 00         	leaq	0x2057(%rip), %r8       # 0xdcef <__PRETTY_FUNCTION__.12775+0x16f>
    bc98: 45 29 e1                     	subl	%r12d, %r9d
    bc9b: 48 89 c5                     	movq	%rax, %rbp
    bc9e: 31 c0                        	xorl	%eax, %eax
    bca0: e8 bb 73 ff ff               	callq	0x3060 <__snprintf_chk@plt>
    bca5: be 00 00 08 00               	movl	$0x80000, %esi          # imm = 0x80000
    bcaa: 4c 89 f7                     	movq	%r14, %rdi
    bcad: 31 c0                        	xorl	%eax, %eax
    bcaf: e8 ec 78 ff ff               	callq	0x35a0 <open@plt>
    bcb4: 41 89 c5                     	movl	%eax, %r13d
    bcb7: 58                           	popq	%rax
    bcb8: 5a                           	popq	%rdx
    bcb9: 45 85 ed                     	testl	%r13d, %r13d
    bcbc: 0f 89 5d fd ff ff            	jns	0xba1f <weston_config_parse+0xcf>
    bcc2: 0f b6 45 00                  	movzbl	(%rbp), %eax
    bcc6: 3c 3a                        	cmpb	$0x3a, %al
    bcc8: 75 96                        	jne	0xbc60 <weston_config_parse+0x310>
    bcca: 0f b6 45 01                  	movzbl	0x1(%rbp), %eax
    bcce: 48 83 c5 01                  	addq	$0x1, %rbp
    bcd2: eb 8c                        	jmp	0xbc60 <weston_config_parse+0x310>
    bcd4: 0f 1f 40 00                  	nopl	(%rax)
    bcd8: 44 89 ef                     	movl	%r13d, %edi
    bcdb: e8 20 76 ff ff               	callq	0x3300 <close@plt>
    bce0: 48 89 df                     	movq	%rbx, %rdi
    bce3: e8 88 73 ff ff               	callq	0x3070 <free@plt>
    bce8: 31 c0                        	xorl	%eax, %eax
    bcea: 48 8b 9c 24 a8 02 00 00      	movq	0x2a8(%rsp), %rbx
    bcf2: 64 48 33 1c 25 28 00 00 00   	xorq	%fs:0x28, %rbx
    bcfb: 0f 85 e5 00 00 00            	jne	0xbde6 <weston_config_parse+0x496>
    bd01: 48 81 c4 b8 02 00 00         	addq	$0x2b8, %rsp            # imm = 0x2B8
    bd08: 5b                           	popq	%rbx
    bd09: 5d                           	popq	%rbp
    bd0a: 41 5c                        	popq	%r12
    bd0c: 41 5d                        	popq	%r13
    bd0e: 41 5e                        	popq	%r14
    bd10: 41 5f                        	popq	%r15
    bd12: c3                           	retq
    bd13: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    bd18: 48 8d 15 e6 1f 00 00         	leaq	0x1fe6(%rip), %rdx      # 0xdd05 <__PRETTY_FUNCTION__.12775+0x185>
    bd1f: 48 89 e9                     	movq	%rbp, %rcx
    bd22: 48 8b 05 b7 52 20 00         	movq	0x2052b7(%rip), %rax    # 0x210fe0 <_GLOBAL_OFFSET_TABLE_+0x3c8>
    bd29: be 01 00 00 00               	movl	$0x1, %esi
    bd2e: 48 8b 38                     	movq	(%rax), %rdi
    bd31: 31 c0                        	xorl	%eax, %eax
    bd33: e8 58 79 ff ff               	callq	0x3690 <__fprintf_chk@plt>
    bd38: 4c 89 ef                     	movq	%r13, %rdi
    bd3b: e8 70 74 ff ff               	callq	0x31b0 <fclose@plt>
    bd40: 48 89 df                     	movq	%rbx, %rdi
    bd43: e8 f8 fa ff ff               	callq	0xb840 <weston_config_destroy>
    bd48: 31 c0                        	xorl	%eax, %eax
    bd4a: eb 9e                        	jmp	0xbcea <weston_config_parse+0x39a>
    bd4c: 0f 1f 40 00                  	nopl	(%rax)
    bd50: 4d 89 f9                     	movq	%r15, %r9
    bd53: b9 00 10 00 00               	movl	$0x1000, %ecx           # imm = 0x1000
    bd58: ba 01 00 00 00               	movl	$0x1, %edx
    bd5d: 4c 8d 05 9a 1f 00 00         	leaq	0x1f9a(%rip), %r8       # 0xdcfe <__PRETTY_FUNCTION__.12775+0x17e>
    bd64: be 00 10 00 00               	movl	$0x1000, %esi           # imm = 0x1000
    bd69: 4c 89 f7                     	movq	%r14, %rdi
    bd6c: e8 ef 72 ff ff               	callq	0x3060 <__snprintf_chk@plt>
    bd71: be 00 00 08 00               	movl	$0x80000, %esi          # imm = 0x80000
    bd76: 4c 89 f7                     	movq	%r14, %rdi
    bd79: 31 c0                        	xorl	%eax, %eax
    bd7b: e8 20 78 ff ff               	callq	0x35a0 <open@plt>
    bd80: 41 89 c5                     	movl	%eax, %r13d
    bd83: 41 83 fd ff                  	cmpl	$-0x1, %r13d
    bd87: 0f 85 92 fc ff ff            	jne	0xba1f <weston_config_parse+0xcf>
    bd8d: e9 4e ff ff ff               	jmp	0xbce0 <weston_config_parse+0x390>
    bd92: 48 8d 7b 10                  	leaq	0x10(%rbx), %rdi
    bd96: 4c 89 f9                     	movq	%r15, %rcx
    bd99: be 00 10 00 00               	movl	$0x1000, %esi           # imm = 0x1000
    bd9e: 48 8d 15 5b 1f 00 00         	leaq	0x1f5b(%rip), %rdx      # 0xdd00 <__PRETTY_FUNCTION__.12775+0x180>
    bda5: 31 c0                        	xorl	%eax, %eax
    bda7: e8 c4 74 ff ff               	callq	0x3270 <snprintf@plt>
    bdac: be 00 00 08 00               	movl	$0x80000, %esi          # imm = 0x80000
    bdb1: 4c 89 ff                     	movq	%r15, %rdi
    bdb4: 31 c0                        	xorl	%eax, %eax
    bdb6: e8 e5 77 ff ff               	callq	0x35a0 <open@plt>
    bdbb: 41 89 c5                     	movl	%eax, %r13d
    bdbe: eb c3                        	jmp	0xbd83 <weston_config_parse+0x433>
    bdc0: 4c 89 ef                     	movq	%r13, %rdi
    bdc3: e8 e8 73 ff ff               	callq	0x31b0 <fclose@plt>
    bdc8: 48 89 d8                     	movq	%rbx, %rax
    bdcb: e9 1a ff ff ff               	jmp	0xbcea <weston_config_parse+0x39a>
    bdd0: 48 8d 15 4c 1f 00 00         	leaq	0x1f4c(%rip), %rdx      # 0xdd23 <__PRETTY_FUNCTION__.12775+0x1a3>
    bdd7: 48 89 e9                     	movq	%rbp, %rcx
    bdda: e9 43 ff ff ff               	jmp	0xbd22 <weston_config_parse+0x3d2>
    bddf: 31 c0                        	xorl	%eax, %eax
    bde1: e9 04 ff ff ff               	jmp	0xbcea <weston_config_parse+0x39a>
    bde6: e8 35 74 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    bdeb: 0f 1f 44 00 00               	nopl	(%rax,%rax)

000000000000bdf0 <config_file_path>:
    bdf0: 41 55                        	pushq	%r13
    bdf2: b9 2f 00 00 00               	movl	$0x2f, %ecx
    bdf7: 41 54                        	pushq	%r12
    bdf9: 49 89 fc                     	movq	%rdi, %r12
    bdfc: 55                           	pushq	%rbp
    bdfd: 48 8d 3d b7 1e 00 00         	leaq	0x1eb7(%rip), %rdi      # 0xdcbb <__PRETTY_FUNCTION__.12775+0x13b>
    be04: 53                           	pushq	%rbx
    be05: 48 83 ec 28                  	subq	$0x28, %rsp
    be09: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    be12: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    be17: 31 c0                        	xorl	%eax, %eax
    be19: 66 89 4c 24 08               	movw	%cx, 0x8(%rsp)
    be1e: 48 b8 2f 2e 63 6f 6e 66 69 67	movabsq	$0x6769666e6f632e2f, %rax # imm = 0x6769666E6F632E2F
    be28: 48 89 04 24                  	movq	%rax, (%rsp)
    be2c: e8 1f 72 ff ff               	callq	0x3050 <getenv@plt>
    be31: 48 85 c0                     	testq	%rax, %rax
    be34: 0f 84 86 00 00 00            	je	0xbec0 <config_file_path+0xd0>
    be3a: 48 89 c7                     	movq	%rax, %rdi
    be3d: 48 89 c5                     	movq	%rax, %rbp
    be40: e8 bb 73 ff ff               	callq	0x3200 <strlen@plt>
    be45: 4c 89 e7                     	movq	%r12, %rdi
    be48: 48 89 c3                     	movq	%rax, %rbx
    be4b: e8 b0 73 ff ff               	callq	0x3200 <strlen@plt>
    be50: 4c 8d 6c 03 02               	leaq	0x2(%rbx,%rax), %r13
    be55: 4c 89 ef                     	movq	%r13, %rdi
    be58: e8 13 76 ff ff               	callq	0x3470 <malloc@plt>
    be5d: 48 89 c3                     	movq	%rax, %rbx
    be60: 48 85 c0                     	testq	%rax, %rax
    be63: 0f 84 af 00 00 00            	je	0xbf18 <config_file_path+0x128>
    be69: 4c 8d 05 6b 1e 00 00         	leaq	0x1e6b(%rip), %r8       # 0xdcdb <__PRETTY_FUNCTION__.12775+0x15b>
    be70: 48 83 ec 08                  	subq	$0x8, %rsp
    be74: 49 89 e9                     	movq	%rbp, %r9
    be77: 41 54                        	pushq	%r12
    be79: ba 01 00 00 00               	movl	$0x1, %edx
    be7e: 48 c7 c1 ff ff ff ff         	movq	$-0x1, %rcx
    be85: 4c 89 ee                     	movq	%r13, %rsi
    be88: 48 89 df                     	movq	%rbx, %rdi
    be8b: 31 c0                        	xorl	%eax, %eax
    be8d: e8 ce 71 ff ff               	callq	0x3060 <__snprintf_chk@plt>
    be92: 58                           	popq	%rax
    be93: 48 89 d8                     	movq	%rbx, %rax
    be96: 5a                           	popq	%rdx
    be97: 48 8b 54 24 18               	movq	0x18(%rsp), %rdx
    be9c: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    bea5: 0f 85 a2 00 00 00            	jne	0xbf4d <config_file_path+0x15d>
    beab: 48 83 c4 28                  	addq	$0x28, %rsp
    beaf: 5b                           	popq	%rbx
    beb0: 5d                           	popq	%rbp
    beb1: 41 5c                        	popq	%r12
    beb3: 41 5d                        	popq	%r13
    beb5: c3                           	retq
    beb6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    bec0: 48 8d 3d ff 1d 00 00         	leaq	0x1dff(%rip), %rdi      # 0xdcc6 <__PRETTY_FUNCTION__.12775+0x146>
    bec7: e8 84 71 ff ff               	callq	0x3050 <getenv@plt>
    becc: 48 89 c5                     	movq	%rax, %rbp
    becf: 48 85 c0                     	testq	%rax, %rax
    bed2: 74 4c                        	je	0xbf20 <config_file_path+0x130>
    bed4: 48 89 c7                     	movq	%rax, %rdi
    bed7: e8 24 73 ff ff               	callq	0x3200 <strlen@plt>
    bedc: 4c 89 e7                     	movq	%r12, %rdi
    bedf: 48 89 c3                     	movq	%rax, %rbx
    bee2: e8 19 73 ff ff               	callq	0x3200 <strlen@plt>
    bee7: 4c 8d 6c 03 0a               	leaq	0xa(%rbx,%rax), %r13
    beec: 4c 89 ef                     	movq	%r13, %rdi
    beef: e8 7c 75 ff ff               	callq	0x3470 <malloc@plt>
    bef4: 48 89 c3                     	movq	%rax, %rbx
    bef7: 48 85 c0                     	testq	%rax, %rax
    befa: 74 1c                        	je	0xbf18 <config_file_path+0x128>
    befc: 41 54                        	pushq	%r12
    befe: 4c 8d 05 56 1e 00 00         	leaq	0x1e56(%rip), %r8       # 0xdd5b <__PRETTY_FUNCTION__.12775+0x1db>
    bf05: 49 89 e9                     	movq	%rbp, %r9
    bf08: 48 8d 44 24 08               	leaq	0x8(%rsp), %rax
    bf0d: 50                           	pushq	%rax
    bf0e: e9 66 ff ff ff               	jmp	0xbe79 <config_file_path+0x89>
    bf13: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    bf18: 31 c0                        	xorl	%eax, %eax
    bf1a: e9 78 ff ff ff               	jmp	0xbe97 <config_file_path+0xa7>
    bf1f: 90                           	nop
    bf20: 48 8b 05 b9 50 20 00         	movq	0x2050b9(%rip), %rax    # 0x210fe0 <_GLOBAL_OFFSET_TABLE_+0x3c8>
    bf27: ba 1c 00 00 00               	movl	$0x1c, %edx
    bf2c: be 01 00 00 00               	movl	$0x1, %esi
    bf31: 48 8d 3d 06 1e 00 00         	leaq	0x1e06(%rip), %rdi      # 0xdd3e <__PRETTY_FUNCTION__.12775+0x1be>
    bf38: 48 8b 08                     	movq	(%rax), %rcx
    bf3b: e8 30 77 ff ff               	callq	0x3670 <fwrite@plt>
    bf40: 4c 89 e7                     	movq	%r12, %rdi
    bf43: e8 d8 73 ff ff               	callq	0x3320 <__strdup@plt>
    bf48: e9 4a ff ff ff               	jmp	0xbe97 <config_file_path+0xa7>
    bf4d: e8 ce 72 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    bf52: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    bf5c: 0f 1f 40 00                  	nopl	(%rax)

000000000000bf60 <handle_option.isra.0>:
    bf60: 55                           	pushq	%rbp
    bf61: 53                           	pushq	%rbx
    bf62: 48 89 d3                     	movq	%rdx, %rbx
    bf65: 48 83 ec 18                  	subq	$0x18, %rsp
    bf69: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    bf72: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    bf77: 31 c0                        	xorl	%eax, %eax
    bf79: 83 ff 01                     	cmpl	$0x1, %edi
    bf7c: 0f 84 8e 00 00 00            	je	0xc010 <handle_option.isra.0+0xb0>
    bf82: 72 5c                        	jb	0xbfe0 <handle_option.isra.0+0x80>
    bf84: 83 ff 02                     	cmpl	$0x2, %edi
    bf87: 75 37                        	jne	0xbfc0 <handle_option.isra.0+0x60>
    bf89: 48 8b 2e                     	movq	(%rsi), %rbp
    bf8c: 48 89 d7                     	movq	%rdx, %rdi
    bf8f: e8 8c 73 ff ff               	callq	0x3320 <__strdup@plt>
    bf94: 48 89 45 00                  	movq	%rax, (%rbp)
    bf98: b8 01 00 00 00               	movl	$0x1, %eax
    bf9d: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    bfa2: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    bfab: 0f 85 8f 00 00 00            	jne	0xc040 <handle_option.isra.0+0xe0>
    bfb1: 48 83 c4 18                  	addq	$0x18, %rsp
    bfb5: 5b                           	popq	%rbx
    bfb6: 5d                           	popq	%rbp
    bfb7: c3                           	retq
    bfb8: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    bfc0: 48 8d 0d b9 1d 00 00         	leaq	0x1db9(%rip), %rcx      # 0xdd80 <__PRETTY_FUNCTION__.3896>
    bfc7: ba 34 00 00 00               	movl	$0x34, %edx
    bfcc: 48 8d 35 8f 1d 00 00         	leaq	0x1d8f(%rip), %rsi      # 0xdd62 <__PRETTY_FUNCTION__.12775+0x1e2>
    bfd3: 48 8d 3d 9f 1d 00 00         	leaq	0x1d9f(%rip), %rdi      # 0xdd79 <__PRETTY_FUNCTION__.12775+0x1f9>
    bfda: e8 e1 72 ff ff               	callq	0x32c0 <__assert_fail@plt>
    bfdf: 90                           	nop
    bfe0: 48 8b 2e                     	movq	(%rsi), %rbp
    bfe3: 31 d2                        	xorl	%edx, %edx
    bfe5: 48 89 e6                     	movq	%rsp, %rsi
    bfe8: 48 89 df                     	movq	%rbx, %rdi
    bfeb: e8 e0 73 ff ff               	callq	0x33d0 <strtol@plt>
    bff0: 89 45 00                     	movl	%eax, (%rbp)
    bff3: 31 c0                        	xorl	%eax, %eax
    bff5: 80 3b 00                     	cmpb	$0x0, (%rbx)
    bff8: 74 a3                        	je	0xbf9d <handle_option.isra.0+0x3d>
    bffa: 48 8b 04 24                  	movq	(%rsp), %rax
    bffe: 80 38 00                     	cmpb	$0x0, (%rax)
    c001: 0f 94 c0                     	sete	%al
    c004: 0f b6 c0                     	movzbl	%al, %eax
    c007: eb 94                        	jmp	0xbf9d <handle_option.isra.0+0x3d>
    c009: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    c010: 48 8b 2e                     	movq	(%rsi), %rbp
    c013: 31 d2                        	xorl	%edx, %edx
    c015: 48 89 e6                     	movq	%rsp, %rsi
    c018: 48 89 df                     	movq	%rbx, %rdi
    c01b: e8 f0 75 ff ff               	callq	0x3610 <strtoul@plt>
    c020: 89 45 00                     	movl	%eax, (%rbp)
    c023: 31 c0                        	xorl	%eax, %eax
    c025: 80 3b 00                     	cmpb	$0x0, (%rbx)
    c028: 0f 84 6f ff ff ff            	je	0xbf9d <handle_option.isra.0+0x3d>
    c02e: 48 8b 04 24                  	movq	(%rsp), %rax
    c032: 80 38 00                     	cmpb	$0x0, (%rax)
    c035: 0f 94 c0                     	sete	%al
    c038: 0f b6 c0                     	movzbl	%al, %eax
    c03b: e9 5d ff ff ff               	jmp	0xbf9d <handle_option.isra.0+0x3d>
    c040: e8 db 71 ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    c045: 90                           	nop
    c046: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000c050 <parse_options>:
    c050: 41 57                        	pushq	%r15
    c052: 41 56                        	pushq	%r14
    c054: 41 55                        	pushq	%r13
    c056: 41 54                        	pushq	%r12
    c058: 55                           	pushq	%rbp
    c059: 53                           	pushq	%rbx
    c05a: 48 83 ec 48                  	subq	$0x48, %rsp
    c05e: 48 89 4c 24 08               	movq	%rcx, 0x8(%rsp)
    c063: 64 48 8b 0c 25 28 00 00 00   	movq	%fs:0x28, %rcx
    c06c: 48 89 4c 24 38               	movq	%rcx, 0x38(%rsp)
    c071: 31 c9                        	xorl	%ecx, %ecx
    c073: 83 3a 01                     	cmpl	$0x1, (%rdx)
    c076: 48 89 7c 24 28               	movq	%rdi, 0x28(%rsp)
    c07b: 89 74 24 24                  	movl	%esi, 0x24(%rsp)
    c07f: 48 89 54 24 18               	movq	%rdx, 0x18(%rsp)
    c084: 0f 8e c6 01 00 00            	jle	0xc250 <parse_options+0x200>
    c08a: 44 8d 4e ff                  	leal	-0x1(%rsi), %r9d
    c08e: 45 31 ff                     	xorl	%r15d, %r15d
    c091: c7 44 24 20 01 00 00 00      	movl	$0x1, 0x20(%rsp)
    c099: 49 83 c1 01                  	addq	$0x1, %r9
    c09d: 49 c1 e1 05                  	shlq	$0x5, %r9
    c0a1: 4e 8d 2c 0f                  	leaq	(%rdi,%r9), %r13
    c0a5: eb 33                        	jmp	0xc0da <parse_options+0x8a>
    c0a7: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    c0b0: 8b 4c 24 20                  	movl	0x20(%rsp), %ecx
    c0b4: 48 8b 74 24 08               	movq	0x8(%rsp), %rsi
    c0b9: 48 63 c1                     	movslq	%ecx, %rax
    c0bc: 4c 89 34 c6                  	movq	%r14, (%rsi,%rax,8)
    c0c0: 89 c8                        	movl	%ecx, %eax
    c0c2: 83 c0 01                     	addl	$0x1, %eax
    c0c5: 89 44 24 20                  	movl	%eax, 0x20(%rsp)
    c0c9: 48 8b 74 24 18               	movq	0x18(%rsp), %rsi
    c0ce: 41 8d 47 02                  	leal	0x2(%r15), %eax
    c0d2: 49 83 c7 01                  	addq	$0x1, %r15
    c0d6: 3b 06                        	cmpl	(%rsi), %eax
    c0d8: 7d 66                        	jge	0xc140 <parse_options+0xf0>
    c0da: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    c0df: 4e 8b 74 f8 08               	movq	0x8(%rax,%r15,8), %r14
    c0e4: 41 80 3e 2d                  	cmpb	$0x2d, (%r14)
    c0e8: 75 c6                        	jne	0xc0b0 <parse_options+0x60>
    c0ea: 41 0f be 56 01               	movsbl	0x1(%r14), %edx
    c0ef: 80 fa 2d                     	cmpb	$0x2d, %dl
    c0f2: 0f 84 90 00 00 00            	je	0xc188 <parse_options+0x138>
    c0f8: 84 d2                        	testb	%dl, %dl
    c0fa: 74 b4                        	je	0xc0b0 <parse_options+0x60>
    c0fc: 8b 44 24 24                  	movl	0x24(%rsp), %eax
    c100: 85 c0                        	testl	%eax, %eax
    c102: 7e ac                        	jle	0xc0b0 <parse_options+0x60>
    c104: 48 8b 44 24 28               	movq	0x28(%rsp), %rax
    c109: eb 0e                        	jmp	0xc119 <parse_options+0xc9>
    c10b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    c110: 48 83 c0 20                  	addq	$0x20, %rax
    c114: 4c 39 e8                     	cmpq	%r13, %rax
    c117: 74 97                        	je	0xc0b0 <parse_options+0x60>
    c119: 39 50 10                     	cmpl	%edx, 0x10(%rax)
    c11c: 75 f2                        	jne	0xc110 <parse_options+0xc0>
    c11e: 8b 38                        	movl	(%rax), %edi
    c120: 83 ff 03                     	cmpl	$0x3, %edi
    c123: 0f 85 de 00 00 00            	jne	0xc207 <parse_options+0x1b7>
    c129: 41 80 7e 02 00               	cmpb	$0x0, 0x2(%r14)
    c12e: 75 e0                        	jne	0xc110 <parse_options+0xc0>
    c130: 48 8b 40 18                  	movq	0x18(%rax), %rax
    c134: c7 00 01 00 00 00            	movl	$0x1, (%rax)
    c13a: eb 8d                        	jmp	0xc0c9 <parse_options+0x79>
    c13c: 0f 1f 40 00                  	nopl	(%rax)
    c140: 48 63 44 24 20               	movslq	0x20(%rsp), %rax
    c145: 48 c1 e0 03                  	shlq	$0x3, %rax
    c149: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    c14e: 48 c7 04 01 00 00 00 00      	movq	$0x0, (%rcx,%rax)
    c156: 48 8b 4c 24 18               	movq	0x18(%rsp), %rcx
    c15b: 8b 44 24 20                  	movl	0x20(%rsp), %eax
    c15f: 89 01                        	movl	%eax, (%rcx)
    c161: 48 8b 4c 24 38               	movq	0x38(%rsp), %rcx
    c166: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    c16f: 0f 85 ed 00 00 00            	jne	0xc262 <parse_options+0x212>
    c175: 48 83 c4 48                  	addq	$0x48, %rsp
    c179: 5b                           	popq	%rbx
    c17a: 5d                           	popq	%rbp
    c17b: 41 5c                        	popq	%r12
    c17d: 41 5d                        	popq	%r13
    c17f: 41 5e                        	popq	%r14
    c181: 41 5f                        	popq	%r15
    c183: c3                           	retq
    c184: 0f 1f 40 00                  	nopl	(%rax)
    c188: 8b 54 24 24                  	movl	0x24(%rsp), %edx
    c18c: 85 d2                        	testl	%edx, %edx
    c18e: 0f 8e 1c ff ff ff            	jle	0xc0b0 <parse_options+0x60>
    c194: 49 8d 46 02                  	leaq	0x2(%r14), %rax
    c198: 48 8b 5c 24 28               	movq	0x28(%rsp), %rbx
    c19d: 48 89 44 24 10               	movq	%rax, 0x10(%rsp)
    c1a2: eb 1d                        	jmp	0xc1c1 <parse_options+0x171>
    c1a4: 0f 1f 40 00                  	nopl	(%rax)
    c1a8: 43 80 7c 26 02 3d            	cmpb	$0x3d, 0x2(%r14,%r12)
    c1ae: 0f 84 7c 00 00 00            	je	0xc230 <parse_options+0x1e0>
    c1b4: 48 83 c3 20                  	addq	$0x20, %rbx
    c1b8: 49 39 dd                     	cmpq	%rbx, %r13
    c1bb: 0f 84 ef fe ff ff            	je	0xc0b0 <parse_options+0x60>
    c1c1: 48 8b 6b 08                  	movq	0x8(%rbx), %rbp
    c1c5: 48 85 ed                     	testq	%rbp, %rbp
    c1c8: 74 ea                        	je	0xc1b4 <parse_options+0x164>
    c1ca: 48 89 ef                     	movq	%rbp, %rdi
    c1cd: e8 2e 70 ff ff               	callq	0x3200 <strlen@plt>
    c1d2: 48 8b 74 24 10               	movq	0x10(%rsp), %rsi
    c1d7: 48 89 ef                     	movq	%rbp, %rdi
    c1da: 4c 63 e0                     	movslq	%eax, %r12
    c1dd: 4c 89 e2                     	movq	%r12, %rdx
    c1e0: e8 fb 6e ff ff               	callq	0x30e0 <strncmp@plt>
    c1e5: 85 c0                        	testl	%eax, %eax
    c1e7: 75 cb                        	jne	0xc1b4 <parse_options+0x164>
    c1e9: 8b 3b                        	movl	(%rbx), %edi
    c1eb: 83 ff 03                     	cmpl	$0x3, %edi
    c1ee: 75 b8                        	jne	0xc1a8 <parse_options+0x158>
    c1f0: 43 80 7c 26 02 00            	cmpb	$0x0, 0x2(%r14,%r12)
    c1f6: 75 bc                        	jne	0xc1b4 <parse_options+0x164>
    c1f8: 48 8b 43 18                  	movq	0x18(%rbx), %rax
    c1fc: c7 00 01 00 00 00            	movl	$0x1, (%rax)
    c202: e9 c2 fe ff ff               	jmp	0xc0c9 <parse_options+0x79>
    c207: 49 8d 56 02                  	leaq	0x2(%r14), %rdx
    c20b: 48 8d 70 18                  	leaq	0x18(%rax), %rsi
    c20f: e8 4c fd ff ff               	callq	0xbf60 <handle_option.isra.0>
    c214: 85 c0                        	testl	%eax, %eax
    c216: 0f 85 ad fe ff ff            	jne	0xc0c9 <parse_options+0x79>
    c21c: 48 8b 44 24 08               	movq	0x8(%rsp), %rax
    c221: 4e 8b 74 f8 08               	movq	0x8(%rax,%r15,8), %r14
    c226: e9 85 fe ff ff               	jmp	0xc0b0 <parse_options+0x60>
    c22b: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    c230: 4b 8d 54 26 03               	leaq	0x3(%r14,%r12), %rdx
    c235: 48 8d 73 18                  	leaq	0x18(%rbx), %rsi
    c239: e8 22 fd ff ff               	callq	0xbf60 <handle_option.isra.0>
    c23e: 85 c0                        	testl	%eax, %eax
    c240: 0f 85 83 fe ff ff            	jne	0xc0c9 <parse_options+0x79>
    c246: eb d4                        	jmp	0xc21c <parse_options+0x1cc>
    c248: 0f 1f 84 00 00 00 00 00      	nopl	(%rax,%rax)
    c250: b8 08 00 00 00               	movl	$0x8, %eax
    c255: c7 44 24 20 01 00 00 00      	movl	$0x1, 0x20(%rsp)
    c25d: e9 e7 fe ff ff               	jmp	0xc149 <parse_options+0xf9>
    c262: e8 b9 6f ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    c267: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)

000000000000c270 <file_create_dated>:
    c270: 41 57                        	pushq	%r15
    c272: 41 56                        	pushq	%r14
    c274: 49 89 f6                     	movq	%rsi, %r14
    c277: 41 55                        	pushq	%r13
    c279: 41 54                        	pushq	%r12
    c27b: 49 89 d4                     	movq	%rdx, %r12
    c27e: 55                           	pushq	%rbp
    c27f: 48 89 cd                     	movq	%rcx, %rbp
    c282: 53                           	pushq	%rbx
    c283: 48 81 ec b8 00 00 00         	subq	$0xb8, %rsp
    c28a: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    c293: 48 89 84 24 a8 00 00 00      	movq	%rax, 0xa8(%rsp)
    c29b: 31 c0                        	xorl	%eax, %eax
    c29d: 48 89 7c 24 08               	movq	%rdi, 0x8(%rsp)
    c2a2: 31 ff                        	xorl	%edi, %edi
    c2a4: e8 a7 71 ff ff               	callq	0x3450 <time@plt>
    c2a9: 48 8d 7c 24 18               	leaq	0x18(%rsp), %rdi
    c2ae: 48 89 44 24 18               	movq	%rax, 0x18(%rsp)
    c2b3: e8 e8 6d ff ff               	callq	0x30a0 <localtime@plt>
    c2b8: 48 85 c0                     	testq	%rax, %rax
    c2bb: 0f 84 4e 01 00 00            	je	0xc40f <file_create_dated+0x19f>
    c2c1: 4c 8d 6c 24 20               	leaq	0x20(%rsp), %r13
    c2c6: 48 89 c1                     	movq	%rax, %rcx
    c2c9: be 80 00 00 00               	movl	$0x80, %esi
    c2ce: 48 8d 15 b9 1a 00 00         	leaq	0x1ab9(%rip), %rdx      # 0xdd8e <__PRETTY_FUNCTION__.3896+0xe>
    c2d5: 4c 89 ef                     	movq	%r13, %rdi
    c2d8: e8 73 72 ff ff               	callq	0x3550 <strftime@plt>
    c2dd: 85 c0                        	testl	%eax, %eax
    c2df: 0f 84 2a 01 00 00            	je	0xc40f <file_create_dated+0x19f>
    c2e5: 0f 88 cc 00 00 00            	js	0xc3b7 <file_create_dated+0x147>
    c2eb: 41 56                        	pushq	%r14
    c2ed: 48 c7 c1 ff ff ff ff         	movq	$-0x1, %rcx
    c2f4: ba 01 00 00 00               	movl	$0x1, %edx
    c2f9: 31 c0                        	xorl	%eax, %eax
    c2fb: 41 55                        	pushq	%r13
    c2fd: 4c 8b 4c 24 18               	movq	0x18(%rsp), %r9
    c302: 48 89 ee                     	movq	%rbp, %rsi
    c305: 4c 89 e7                     	movq	%r12, %rdi
    c308: 4c 8d 05 4c 1a 00 00         	leaq	0x1a4c(%rip), %r8       # 0xdd5b <__PRETTY_FUNCTION__.12775+0x1db>
    c30f: e8 4c 6d ff ff               	callq	0x3060 <__snprintf_chk@plt>
    c314: 5a                           	popq	%rdx
    c315: 59                           	popq	%rcx
    c316: 85 c0                        	testl	%eax, %eax
    c318: 0f 88 e2 00 00 00            	js	0xc400 <file_create_dated+0x190>
    c31e: 48 98                        	cltq
    c320: 48 39 c5                     	cmpq	%rax, %rbp
    c323: 0f 86 d7 00 00 00            	jbe	0xc400 <file_create_dated+0x190>
    c329: 31 c0                        	xorl	%eax, %eax
    c32b: ba b6 01 00 00               	movl	$0x1b6, %edx            # imm = 0x1B6
    c330: be c2 00 08 00               	movl	$0x800c2, %esi          # imm = 0x800C2
    c335: 4c 89 e7                     	movq	%r12, %rdi
    c338: e8 63 72 ff ff               	callq	0x35a0 <open@plt>
    c33d: 83 f8 ff                     	cmpl	$-0x1, %eax
    c340: 0f 85 aa 00 00 00            	jne	0xc3f0 <file_create_dated+0x180>
    c346: e8 65 6d ff ff               	callq	0x30b0 <__errno_location@plt>
    c34b: 31 db                        	xorl	%ebx, %ebx
    c34d: 49 89 c7                     	movq	%rax, %r15
    c350: eb 5f                        	jmp	0xc3b1 <file_create_dated+0x141>
    c352: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    c358: 48 83 ec 08                  	subq	$0x8, %rsp
    c35c: 83 c3 01                     	addl	$0x1, %ebx
    c35f: ba 01 00 00 00               	movl	$0x1, %edx
    c364: 41 56                        	pushq	%r14
    c366: 4c 8d 05 2d 1a 00 00         	leaq	0x1a2d(%rip), %r8       # 0xdd9a <__PRETTY_FUNCTION__.3896+0x1a>
    c36d: 48 89 ee                     	movq	%rbp, %rsi
    c370: 4c 89 e7                     	movq	%r12, %rdi
    c373: 53                           	pushq	%rbx
    c374: 48 c7 c1 ff ff ff ff         	movq	$-0x1, %rcx
    c37b: 31 c0                        	xorl	%eax, %eax
    c37d: 41 55                        	pushq	%r13
    c37f: 4c 8b 4c 24 28               	movq	0x28(%rsp), %r9
    c384: e8 d7 6c ff ff               	callq	0x3060 <__snprintf_chk@plt>
    c389: 48 83 c4 20                  	addq	$0x20, %rsp
    c38d: 85 c0                        	testl	%eax, %eax
    c38f: 78 4f                        	js	0xc3e0 <file_create_dated+0x170>
    c391: 48 98                        	cltq
    c393: 48 39 c5                     	cmpq	%rax, %rbp
    c396: 76 48                        	jbe	0xc3e0 <file_create_dated+0x170>
    c398: 31 c0                        	xorl	%eax, %eax
    c39a: ba b6 01 00 00               	movl	$0x1b6, %edx            # imm = 0x1B6
    c39f: be c2 00 08 00               	movl	$0x800c2, %esi          # imm = 0x800C2
    c3a4: 4c 89 e7                     	movq	%r12, %rdi
    c3a7: e8 f4 71 ff ff               	callq	0x35a0 <open@plt>
    c3ac: 83 f8 ff                     	cmpl	$-0x1, %eax
    c3af: 75 3f                        	jne	0xc3f0 <file_create_dated+0x180>
    c3b1: 41 83 3f 11                  	cmpl	$0x11, (%r15)
    c3b5: 74 a1                        	je	0xc358 <file_create_dated+0xe8>
    c3b7: 31 c0                        	xorl	%eax, %eax
    c3b9: 48 8b 8c 24 a8 00 00 00      	movq	0xa8(%rsp), %rcx
    c3c1: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    c3ca: 75 50                        	jne	0xc41c <file_create_dated+0x1ac>
    c3cc: 48 81 c4 b8 00 00 00         	addq	$0xb8, %rsp
    c3d3: 5b                           	popq	%rbx
    c3d4: 5d                           	popq	%rbp
    c3d5: 41 5c                        	popq	%r12
    c3d7: 41 5d                        	popq	%r13
    c3d9: 41 5e                        	popq	%r14
    c3db: 41 5f                        	popq	%r15
    c3dd: c3                           	retq
    c3de: 66 90                        	nop
    c3e0: 41 c7 07 69 00 00 00         	movl	$0x69, (%r15)
    c3e7: 31 c0                        	xorl	%eax, %eax
    c3e9: eb ce                        	jmp	0xc3b9 <file_create_dated+0x149>
    c3eb: 0f 1f 44 00 00               	nopl	(%rax,%rax)
    c3f0: 48 8d 35 ad 19 00 00         	leaq	0x19ad(%rip), %rsi      # 0xdda4 <__PRETTY_FUNCTION__.3896+0x24>
    c3f7: 89 c7                        	movl	%eax, %edi
    c3f9: e8 02 71 ff ff               	callq	0x3500 <fdopen@plt>
    c3fe: eb b9                        	jmp	0xc3b9 <file_create_dated+0x149>
    c400: e8 ab 6c ff ff               	callq	0x30b0 <__errno_location@plt>
    c405: c7 00 69 00 00 00            	movl	$0x69, (%rax)
    c40b: 31 c0                        	xorl	%eax, %eax
    c40d: eb aa                        	jmp	0xc3b9 <file_create_dated+0x149>
    c40f: e8 9c 6c ff ff               	callq	0x30b0 <__errno_location@plt>
    c414: c7 00 3e 00 00 00            	movl	$0x3e, (%rax)
    c41a: eb 9b                        	jmp	0xc3b7 <file_create_dated+0x147>
    c41c: e8 ff 6d ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    c421: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    c42b: 0f 1f 44 00 00               	nopl	(%rax,%rax)

000000000000c430 <os_fd_set_cloexec>:
    c430: 53                           	pushq	%rbx
    c431: 48 83 ec 10                  	subq	$0x10, %rsp
    c435: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    c43e: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    c443: 31 c0                        	xorl	%eax, %eax
    c445: 83 ff ff                     	cmpl	$-0x1, %edi
    c448: 74 4e                        	je	0xc498 <os_fd_set_cloexec+0x68>
    c44a: 31 c0                        	xorl	%eax, %eax
    c44c: be 01 00 00 00               	movl	$0x1, %esi
    c451: 89 fb                        	movl	%edi, %ebx
    c453: e8 18 6d ff ff               	callq	0x3170 <fcntl@plt>
    c458: 83 f8 ff                     	cmpl	$-0x1, %eax
    c45b: 74 3b                        	je	0xc498 <os_fd_set_cloexec+0x68>
    c45d: 83 c8 01                     	orl	$0x1, %eax
    c460: be 02 00 00 00               	movl	$0x2, %esi
    c465: 89 df                        	movl	%ebx, %edi
    c467: 48 63 d0                     	movslq	%eax, %rdx
    c46a: 31 c0                        	xorl	%eax, %eax
    c46c: e8 ff 6c ff ff               	callq	0x3170 <fcntl@plt>
    c471: 83 f8 ff                     	cmpl	$-0x1, %eax
    c474: 0f 94 c0                     	sete	%al
    c477: 0f b6 c0                     	movzbl	%al, %eax
    c47a: f7 d8                        	negl	%eax
    c47c: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    c481: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    c48a: 75 13                        	jne	0xc49f <os_fd_set_cloexec+0x6f>
    c48c: 48 83 c4 10                  	addq	$0x10, %rsp
    c490: 5b                           	popq	%rbx
    c491: c3                           	retq
    c492: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    c498: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    c49d: eb dd                        	jmp	0xc47c <os_fd_set_cloexec+0x4c>
    c49f: e8 7c 6d ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    c4a4: 66 90                        	nop
    c4a6: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)

000000000000c4b0 <os_socketpair_cloexec>:
    c4b0: 41 56                        	pushq	%r14
    c4b2: 41 89 d6                     	movl	%edx, %r14d
    c4b5: 41 55                        	pushq	%r13
    c4b7: 41 89 f5                     	movl	%esi, %r13d
    c4ba: 81 ce 00 00 08 00            	orl	$0x80000, %esi          # imm = 0x80000
    c4c0: 41 54                        	pushq	%r12
    c4c2: 41 89 fc                     	movl	%edi, %r12d
    c4c5: 55                           	pushq	%rbp
    c4c6: 48 89 cd                     	movq	%rcx, %rbp
    c4c9: 53                           	pushq	%rbx
    c4ca: 48 83 ec 10                  	subq	$0x10, %rsp
    c4ce: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    c4d7: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    c4dc: 31 c0                        	xorl	%eax, %eax
    c4de: e8 1d 6f ff ff               	callq	0x3400 <socketpair@plt>
    c4e3: 85 c0                        	testl	%eax, %eax
    c4e5: 0f 84 85 00 00 00            	je	0xc570 <os_socketpair_cloexec+0xc0>
    c4eb: 89 c3                        	movl	%eax, %ebx
    c4ed: e8 be 6b ff ff               	callq	0x30b0 <__errno_location@plt>
    c4f2: 83 38 16                     	cmpl	$0x16, (%rax)
    c4f5: 74 29                        	je	0xc520 <os_socketpair_cloexec+0x70>
    c4f7: 48 8b 54 24 08               	movq	0x8(%rsp), %rdx
    c4fc: 64 48 33 14 25 28 00 00 00   	xorq	%fs:0x28, %rdx
    c505: 89 d8                        	movl	%ebx, %eax
    c507: 0f 85 ab 00 00 00            	jne	0xc5b8 <os_socketpair_cloexec+0x108>
    c50d: 48 83 c4 10                  	addq	$0x10, %rsp
    c511: 5b                           	popq	%rbx
    c512: 5d                           	popq	%rbp
    c513: 41 5c                        	popq	%r12
    c515: 41 5d                        	popq	%r13
    c517: 41 5e                        	popq	%r14
    c519: c3                           	retq
    c51a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    c520: 48 89 e9                     	movq	%rbp, %rcx
    c523: 44 89 f2                     	movl	%r14d, %edx
    c526: 44 89 ee                     	movl	%r13d, %esi
    c529: 44 89 e7                     	movl	%r12d, %edi
    c52c: e8 cf 6e ff ff               	callq	0x3400 <socketpair@plt>
    c531: 89 c3                        	movl	%eax, %ebx
    c533: 85 c0                        	testl	%eax, %eax
    c535: 78 c0                        	js	0xc4f7 <os_socketpair_cloexec+0x47>
    c537: 8b 5d 00                     	movl	(%rbp), %ebx
    c53a: 89 df                        	movl	%ebx, %edi
    c53c: e8 ef fe ff ff               	callq	0xc430 <os_fd_set_cloexec>
    c541: 85 c0                        	testl	%eax, %eax
    c543: 75 3b                        	jne	0xc580 <os_socketpair_cloexec+0xd0>
    c545: 89 5d 00                     	movl	%ebx, (%rbp)
    c548: 8b 5d 04                     	movl	0x4(%rbp), %ebx
    c54b: 89 df                        	movl	%ebx, %edi
    c54d: e8 de fe ff ff               	callq	0xc430 <os_fd_set_cloexec>
    c552: 85 c0                        	testl	%eax, %eax
    c554: 75 3a                        	jne	0xc590 <os_socketpair_cloexec+0xe0>
    c556: 89 5d 04                     	movl	%ebx, 0x4(%rbp)
    c559: 8b 7d 00                     	movl	(%rbp), %edi
    c55c: 83 fb ff                     	cmpl	$-0x1, %ebx
    c55f: 74 40                        	je	0xc5a1 <os_socketpair_cloexec+0xf1>
    c561: 83 ff ff                     	cmpl	$-0x1, %edi
    c564: 74 3b                        	je	0xc5a1 <os_socketpair_cloexec+0xf1>
    c566: 66 2e 0f 1f 84 00 00 00 00 00	nopw	%cs:(%rax,%rax)
    c570: 31 db                        	xorl	%ebx, %ebx
    c572: e9 80 ff ff ff               	jmp	0xc4f7 <os_socketpair_cloexec+0x47>
    c577: 66 0f 1f 84 00 00 00 00 00   	nopw	(%rax,%rax)
    c580: 89 df                        	movl	%ebx, %edi
    c582: bb ff ff ff ff               	movl	$0xffffffff, %ebx       # imm = 0xFFFFFFFF
    c587: e8 74 6d ff ff               	callq	0x3300 <close@plt>
    c58c: eb b7                        	jmp	0xc545 <os_socketpair_cloexec+0x95>
    c58e: 66 90                        	nop
    c590: 89 df                        	movl	%ebx, %edi
    c592: e8 69 6d ff ff               	callq	0x3300 <close@plt>
    c597: 8b 7d 00                     	movl	(%rbp), %edi
    c59a: c7 45 04 ff ff ff ff         	movl	$0xffffffff, 0x4(%rbp)  # imm = 0xFFFFFFFF
    c5a1: e8 5a 6d ff ff               	callq	0x3300 <close@plt>
    c5a6: 8b 7d 04                     	movl	0x4(%rbp), %edi
    c5a9: bb ff ff ff ff               	movl	$0xffffffff, %ebx       # imm = 0xFFFFFFFF
    c5ae: e8 4d 6d ff ff               	callq	0x3300 <close@plt>
    c5b3: e9 3f ff ff ff               	jmp	0xc4f7 <os_socketpair_cloexec+0x47>
    c5b8: e8 63 6c ff ff               	callq	0x3220 <__stack_chk_fail@plt>
    c5bd: 0f 1f 00                     	nopl	(%rax)

000000000000c5c0 <os_epoll_create_cloexec>:
    c5c0: 53                           	pushq	%rbx
    c5c1: bf 00 00 08 00               	movl	$0x80000, %edi          # imm = 0x80000
    c5c6: 48 83 ec 10                  	subq	$0x10, %rsp
    c5ca: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    c5d3: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    c5d8: 31 c0                        	xorl	%eax, %eax
    c5da: e8 e1 70 ff ff               	callq	0x36c0 <epoll_create1@plt>
    c5df: 85 c0                        	testl	%eax, %eax
    c5e1: 78 1d                        	js	0xc600 <os_epoll_create_cloexec+0x40>
    c5e3: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    c5e8: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    c5f1: 75 48                        	jne	0xc63b <os_epoll_create_cloexec+0x7b>
    c5f3: 48 83 c4 10                  	addq	$0x10, %rsp
    c5f7: 5b                           	popq	%rbx
    c5f8: c3                           	retq
    c5f9: 0f 1f 80 00 00 00 00         	nopl	(%rax)
    c600: e8 ab 6a ff ff               	callq	0x30b0 <__errno_location@plt>
    c605: 48 89 c2                     	movq	%rax, %rdx
    c608: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    c60d: 83 3a 16                     	cmpl	$0x16, (%rdx)
    c610: 75 d1                        	jne	0xc5e3 <os_epoll_create_cloexec+0x23>
    c612: bf 01 00 00 00               	movl	$0x1, %edi
    c617: e8 44 70 ff ff               	callq	0x3660 <epoll_create@plt>
    c61c: 89 c7                        	movl	%eax, %edi
    c61e: 89 c3                        	movl	%eax, %ebx
    c620: e8 0b fe ff ff               	callq	0xc430 <os_fd_set_cloexec>
    c625: 89 c2                        	movl	%eax, %edx
    c627: 89 d8                        	movl	%ebx, %eax
    c629: 85 d2                        	testl	%edx, %edx
    c62b: 74 b6                        	je	0xc5e3 <os_epoll_create_cloexec+0x23>
    c62d: 89 df                        	movl	%ebx, %edi
    c62f: e8 cc 6c ff ff               	callq	0x3300 <close@plt>
    c634: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    c639: eb a8                        	jmp	0xc5e3 <os_epoll_create_cloexec+0x23>
    c63b: e8 e0 6b ff ff               	callq	0x3220 <__stack_chk_fail@plt>

000000000000c640 <os_create_anonymous_file>:
    c640: 41 55                        	pushq	%r13
    c642: 49 89 fd                     	movq	%rdi, %r13
    c645: 41 54                        	pushq	%r12
    c647: 48 8d 3d 58 17 00 00         	leaq	0x1758(%rip), %rdi      # 0xdda6 <__PRETTY_FUNCTION__.3896+0x26>
    c64e: 55                           	pushq	%rbp
    c64f: 53                           	pushq	%rbx
    c650: 48 83 ec 18                  	subq	$0x18, %rsp
    c654: 64 48 8b 04 25 28 00 00 00   	movq	%fs:0x28, %rax
    c65d: 48 89 44 24 08               	movq	%rax, 0x8(%rsp)
    c662: 31 c0                        	xorl	%eax, %eax
    c664: e8 e7 69 ff ff               	callq	0x3050 <getenv@plt>
    c669: 48 85 c0                     	testq	%rax, %rax
    c66c: 0f 84 c6 00 00 00            	je	0xc738 <os_create_anonymous_file+0xf8>
    c672: 48 89 c7                     	movq	%rax, %rdi
    c675: 49 89 c4                     	movq	%rax, %r12
    c678: e8 83 6b ff ff               	callq	0x3200 <strlen@plt>
    c67d: 48 8d 78 16                  	leaq	0x16(%rax), %rdi
    c681: 48 89 c5                     	movq	%rax, %rbp
    c684: e8 e7 6d ff ff               	callq	0x3470 <malloc@plt>
    c689: 48 89 c3                     	movq	%rax, %rbx
    c68c: 48 85 c0                     	testq	%rax, %rax
    c68f: 0f 84 98 00 00 00            	je	0xc72d <os_create_anonymous_file+0xed>
    c695: 48 89 ea                     	movq	%rbp, %rdx
    c698: 4c 89 e6                     	movq	%r12, %rsi
    c69b: 48 89 c7                     	movq	%rax, %rdi
    c69e: e8 3d 6d ff ff               	callq	0x33e0 <memcpy@plt>
    c6a3: c7 44 2b 10 58 58 58 58      	movl	$0x58585858, 0x10(%rbx,%rbp) # imm = 0x58585858
    c6ab: 48 89 df                     	movq	%rbx, %rdi
    c6ae: 48 b8 2f 77 65 73 74 6f 6e 2d	movabsq	$0x2d6e6f747365772f, %rax # imm = 0x2D6E6F747365772F
    c6b8: 48 89 04 2b                  	movq	%rax, (%rbx,%rbp)
    c6bc: be 00 00 08 00               	movl	$0x80000, %esi          # imm = 0x80000
    c6c1: 48 b8 73 68 61 72 65 64 2d 58	movabsq	$0x582d646572616873, %rax # imm = 0x582D646572616873
    c6cb: 48 89 44 2b 08               	movq	%rax, 0x8(%rbx,%rbp)
    c6d0: b8 58 00 00 00               	movl	$0x58, %eax
    c6d5: 66 89 44 2b 14               	movw	%ax, 0x14(%rbx,%rbp)
    c6da: e8 a1 6b ff ff               	callq	0x3280 <mkostemp@plt>
    c6df: 48 89 df                     	movq	%rbx, %rdi
    c6e2: 89 c5                        	movl	%eax, %ebp
    c6e4: 85 c0                        	testl	%eax, %eax
    c6e6: 78 40                        	js	0xc728 <os_create_anonymous_file+0xe8>
    c6e8: e8 e3 69 ff ff               	callq	0x30d0 <unlink@plt>
    c6ed: 48 89 df                     	movq	%rbx, %rdi
    c6f0: e8 7b 69 ff ff               	callq	0x3070 <free@plt>
    c6f5: 4c 89 ea                     	movq	%r13, %rdx
    c6f8: 31 f6                        	xorl	%esi, %esi
    c6fa: 89 ef                        	movl	%ebp, %edi
    c6fc: e8 1f 6d ff ff               	callq	0x3420 <posix_fallocate@plt>
    c701: 89 c3                        	movl	%eax, %ebx
    c703: 85 c0                        	testl	%eax, %eax
    c705: 75 49                        	jne	0xc750 <os_create_anonymous_file+0x110>
    c707: 89 e8                        	movl	%ebp, %eax
    c709: 48 8b 4c 24 08               	movq	0x8(%rsp), %rcx
    c70e: 64 48 33 0c 25 28 00 00 00   	xorq	%fs:0x28, %rcx
    c717: 75 4c                        	jne	0xc765 <os_create_anonymous_file+0x125>
    c719: 48 83 c4 18                  	addq	$0x18, %rsp
    c71d: 5b                           	popq	%rbx
    c71e: 5d                           	popq	%rbp
    c71f: 41 5c                        	popq	%r12
    c721: 41 5d                        	popq	%r13
    c723: c3                           	retq
    c724: 0f 1f 40 00                  	nopl	(%rax)
    c728: e8 43 69 ff ff               	callq	0x3070 <free@plt>
    c72d: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    c732: eb d5                        	jmp	0xc709 <os_create_anonymous_file+0xc9>
    c734: 0f 1f 40 00                  	nopl	(%rax)
    c738: e8 73 69 ff ff               	callq	0x30b0 <__errno_location@plt>
    c73d: c7 00 02 00 00 00            	movl	$0x2, (%rax)
    c743: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    c748: eb bf                        	jmp	0xc709 <os_create_anonymous_file+0xc9>
    c74a: 66 0f 1f 44 00 00            	nopw	(%rax,%rax)
    c750: 89 ef                        	movl	%ebp, %edi
    c752: e8 a9 6b ff ff               	callq	0x3300 <close@plt>
    c757: e8 54 69 ff ff               	callq	0x30b0 <__errno_location@plt>
    c75c: 89 18                        	movl	%ebx, (%rax)
    c75e: b8 ff ff ff ff               	movl	$0xffffffff, %eax       # imm = 0xFFFFFFFF
    c763: eb a4                        	jmp	0xc709 <os_create_anonymous_file+0xc9>
    c765: e8 b6 6a ff ff               	callq	0x3220 <__stack_chk_fail@plt>

000000000000c76a <__do_global_ctors_aux>:
    c76a: 55                           	pushq	%rbp
    c76b: 48 89 e5                     	movq	%rsp, %rbp
    c76e: 53                           	pushq	%rbx
    c76f: 48 8d 1d 22 41 20 00         	leaq	0x204122(%rip), %rbx    # 0x210898 <__CTOR_LIST__>
    c776: 52                           	pushq	%rdx
    c777: 48 8b 03                     	movq	(%rbx), %rax
    c77a: 48 83 f8 ff                  	cmpq	$-0x1, %rax
    c77e: 74 08                        	je	0xc788 <__do_global_ctors_aux+0x1e>
    c780: ff d0                        	callq	*%rax
    c782: 48 83 eb 08                  	subq	$0x8, %rbx
    c786: eb ef                        	jmp	0xc777 <__do_global_ctors_aux+0xd>
    c788: 58                           	popq	%rax
    c789: 5b                           	popq	%rbx
    c78a: 5d                           	popq	%rbp
    c78b: c3                           	retq

Disassembly of section .fini:

000000000000c78c <_fini>:
    c78c: 48 83 ec 08                  	subq	$0x8, %rsp
    c790: e8 d6 6f ff ff               	callq	0x376b <__do_global_dtors_aux>
    c795: 48 83 c4 08                  	addq	$0x8, %rsp
    c799: c3                           	retq
