/*
 * Minimal x86-64 Linux Wayland client for the recovered Gen5W IVI protocol.
 *
 * This deliberately uses only Linux syscalls and the stable protocol/global
 * numbering exposed by the bounded VM compositor.  It requests that surface
 * 4903 (the home id in weston_1920.ini) be laid out at 1920x720, visible, and
 * foreground on display plane 1.  It is a VM research helper, not firmware.
 */
.text
.globl _start
_start:
    /* socket(AF_UNIX, SOCK_STREAM, 0) */
    mov $41, %rax
    mov $1, %rdi
    mov $1, %rsi
    xor %rdx, %rdx
    syscall
    test %rax, %rax
    js fail_socket
    mov %rax, %r12

    /* connect(fd, "/run/user/root/wayland-0", 27) */
    mov $42, %rax
    mov %r12, %rdi
    lea sockaddr(%rip), %rsi
    mov $27, %rdx
    syscall
    test %rax, %rax
    js fail_connect

    /* wl_display.get_registry(new_id=2) */
    mov $1, %rax
    mov %r12, %rdi
    lea get_registry(%rip), %rsi
    mov $(get_registry_end-get_registry), %rdx
    syscall

    /* wl_registry.bind(global=13, "ivi_window_manager", v1, new_id=3). */
    mov $1, %rax
    mov %r12, %rdi
    lea bind_manager(%rip), %rsi
    mov $(bind_manager_end-bind_manager), %rdx
    syscall

    /* ivi_window_manager.set_surface_layout(4903, 0, 0, 1920, 720) */
    mov $1, %rax
    mov %r12, %rdi
    lea set_layout(%rip), %rsi
    mov $(set_layout_end-set_layout), %rdx
    syscall

    /* set_surface_visible(4903, true) */
    mov $1, %rax
    mov %r12, %rdi
    lea set_visible(%rip), %rsi
    mov $(set_visible_end-set_visible), %rdx
    syscall

    /* set_visible_for_qtwayland(4903, true) */
    mov $1, %rax
    mov %r12, %rdi
    lea set_qt_visible(%rip), %rsi
    mov $(set_qt_visible_end-set_qt_visible), %rdx
    syscall

    /* request_fg(display_plane=1, surface_id=4903) */
    mov $1, %rax
    mov %r12, %rdi
    lea request_fg(%rip), %rsi
    mov $(request_fg_end-request_fg), %rdx
    syscall

    /* update_layout(1) */
    mov $1, %rax
    mov %r12, %rdi
    lea update_layout(%rip), %rsi
    mov $(update_layout_end-update_layout), %rdx
    syscall

    /* Give the compositor time to consume requests before closing. */
    mov $35, %rax
    lea one_second(%rip), %rdi
    xor %rsi, %rsi
    syscall

    mov $1, %rax
    mov $1, %rdi
    lea ok_message(%rip), %rsi
    mov $(ok_message_end-ok_message), %rdx
    syscall
    xor %rdi, %rdi
    jmp exit

fail_socket:
    mov $31, %rdi
    jmp exit
fail_connect:
    mov $32, %rdi
exit:
    mov $60, %rax
    syscall

.p2align 2
sockaddr:
    .short 1
    .ascii "/run/user/root/wayland-0\0"

.p2align 2
get_registry:
    .long 1
    .long (12 << 16) | 1
    .long 2
get_registry_end:

.p2align 2
bind_manager:
    .long 2
    .long (44 << 16) | 0
    .long 13
    .long 19
    .ascii "ivi_window_manager\0"
    .byte 0
    .long 1
    .long 3
bind_manager_end:

.p2align 2
set_layout:
    .long 3
    .long (28 << 16) | 6
    .long 4903
    .long 0
    .long 0
    .long 1920
    .long 720
set_layout_end:

.p2align 2
set_visible:
    .long 3
    .long (16 << 16) | 2
    .long 4903
    .long 1
set_visible_end:

.p2align 2
set_qt_visible:
    .long 3
    .long (16 << 16) | 8
    .long 4903
    .long 1
set_qt_visible_end:

.p2align 2
request_fg:
    .long 3
    .long (16 << 16) | 3
    .long 1
    .long 4903
request_fg_end:

.p2align 2
update_layout:
    .long 3
    .long (12 << 16) | 0
    .long 1
update_layout_end:

.p2align 3
one_second:
    .quad 1
    .quad 0
ok_message:
    .ascii "IVI_FG_REQUEST_SENT\n"
ok_message_end:
