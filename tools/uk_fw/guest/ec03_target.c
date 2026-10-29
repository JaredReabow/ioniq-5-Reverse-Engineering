/*
 * ec03_target.c — synthetic target for validating the minimal observer.
 *
 * Prints its pid and the address of the function to be instrumented, waits long
 * enough for a tracer to attach and arm, then calls that function three times.
 * The observer disarms a slot after its first hit, so a correct run shows exactly
 * one hit and a clean exit.
 *
 * Build:
 *   zig cc -target x86_64-linux-musl -static -O2 -Wall -Wextra -Werror \
 *       -o ec03-target ec03_target.c
 */

#define _GNU_SOURCE

#include <stdio.h>
#include <unistd.h>

/*
 * Stand-in for the vendor surface struct so field capture can be validated:
 * int32 width at +0x2c and height at +0x30, matching the EC-01 contract.
 */
static unsigned char fake_surface[0x40]
    __attribute__((aligned(16)));

static void seed_surface(void)
{
    int *w = (int *)(void *)(fake_surface + 0x2c);
    int *h = (int *)(void *)(fake_surface + 0x30);

    *w = 1926;
    *h = 753;
}

__attribute__((noinline, used)) static void probe_target(void)
{
    __asm__ __volatile__("" ::: "memory");
}

int main(void)
{
    int i;

    seed_surface();
    printf("PID %d ADDR 0x%lx STRUCT 0x%lx\n", (int)getpid(),
           (unsigned long)(void (*)(void))probe_target,
           (unsigned long)(void *)fake_surface);
    fflush(stdout);

    /* Give the tracer time to attach and arm before the first call. */
    sleep(3);
    for (i = 0; i < 3; i++) {
        probe_target();
    }
    printf("TARGET done calls=3\n");
    fflush(stdout);
    return 0;
}
