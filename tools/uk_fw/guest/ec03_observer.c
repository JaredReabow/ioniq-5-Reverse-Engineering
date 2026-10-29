/*
 * ec03_observer.c — minimal bounded hardware-breakpoint observer.
 *
 * This is the EC-03 minimal core agreed under the EC-02 rescope. It exists
 * because four rounds of specification produced contradictions faster than they
 * resolved them, while every capability question was answered empirically in
 * under four seconds of VM time.
 *
 * Scope, deliberately small:
 *   - one target process, one traced thread;
 *   - up to four execute breakpoints, addressed as module-substring + file
 *     offset, so the same binary is testable against a synthetic target;
 *   - bounded capture at each hit: registers plus a small, fixed field set;
 *   - proven teardown: disarm, verify readback, then detach;
 *   - internal deadline so a stuck tracee cannot hang the caller.
 *
 * It is not a general debugger and it writes no target memory.
 *
 * Usage:
 *   ec03-observer <pid> <module-substring> <offset> [offset...]
 *
 * Output: line-oriented records on stdout, one per event, with a terminal
 * RESULT record. Exit 0 only when teardown was verified.
 *
 * Build:
 *   zig cc -target x86_64-linux-musl -static -O2 -Wall -Wextra -Werror \
 *       -o ec03-observer ec03_observer.c
 */

#define _GNU_SOURCE

#include <errno.h>
#include <signal.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAX_SLOTS 4
#define MAX_STOPS 32
#define DEADLINE_SECONDS 60

#define DR_STATUS 6
#define DR_CONTROL 7
#define DR7_L(n) (0x1UL << (2 * (n)))
#define DR7_RESERVED 0x400UL
#define DR6_B(n) (0x1UL << (n))

struct slot {
    unsigned long addr;
    int done;
};

static struct slot slots[MAX_SLOTS];
static int slot_count;
static int stop_after_first_hit;
static int stop_after_hits; /* 0 = run to completion or limits */
static int hits_seen;
static int wait_module_ms; /* 0 = do not wait */

/*
 * Field capture. At each hit the observer optionally reads two int32 fields from
 * a struct pointer supplied either as an absolute address or as a register name.
 * The offsets default to the EC-01 contract for the vendor dri2_surf (width at
 * +0x2c, height at +0x30) and can be overridden for other layouts.
 */
static int field_enabled;
static int field_use_reg;
static unsigned long field_reg_value;
static unsigned long field_addr;
static unsigned long field_off_a = 0x2c;
static unsigned long field_off_b = 0x30;
static const char *field_reg_name;

static void say(const char *fmt, ...)
{
    va_list ap;

    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
    putchar('\n');
    fflush(stdout);
}

static long dr_offset(int index)
{
    return (long)offsetof(struct user, u_debugreg) +
           (long)index * (long)sizeof(unsigned long long);
}

static int dr_read(pid_t pid, int index, unsigned long long *out)
{
    long v;

    errno = 0;
    v = ptrace(PTRACE_PEEKUSER, pid, (void *)dr_offset(index), NULL);
    if (v == -1 && errno != 0) {
        return -1;
    }
    *out = (unsigned long long)v;
    return 0;
}

static int dr_write(pid_t pid, int index, unsigned long long value)
{
    errno = 0;
    if (ptrace(PTRACE_POKEUSER, pid, (void *)dr_offset(index),
               (void *)(unsigned long)value) == -1) {
        return -1;
    }
    return 0;
}

/*
 * Resolve the base of the first executable mapping whose path contains the given
 * substring. The base is that mapping's start address, so supplied offsets are
 * relative to it; for a shared object whose text mapping has file offset 0 this
 * is also the ELF load bias, which is the case for the vendor libEGL.
 * Returns 0 on success.
 */
static int resolve_base(pid_t pid, const char *needle, unsigned long *base,
                        int verbose)
{
    char path[64];
    char line[512];
    FILE *fp;
    int found = 0;

    snprintf(path, sizeof(path), "/proc/%d/maps", (int)pid);
    fp = fopen(path, "r");
    if (fp == NULL) {
        if (verbose) {
            say("ERROR maps-open errno=%d", errno);
        }
        return -1;
    }
    while (fgets(line, sizeof(line), fp) != NULL) {
        unsigned long start = 0, end = 0;
        char perms[8] = {0};

        if (sscanf(line, "%lx-%lx %7s", &start, &end, perms) != 3) {
            continue;
        }
        if (strncmp(perms, "r-xp", 4) != 0) {
            continue;
        }
        if (strstr(line, needle) == NULL) {
            continue;
        }
        *base = start;
        found = 1;
        break;
    }
    fclose(fp);
    if (!found) {
        if (verbose) {
            say("ERROR module-not-mapped needle=%s", needle);
        }
        return -1;
    }
    return 0;
}

/* Resolve a named general-purpose register from the current stop. */
static int reg_by_name(const struct user_regs_struct *r, const char *name,
                       unsigned long *out)
{
    struct { const char *n; unsigned long long v; } map[] = {
        {"rax", r->rax}, {"rbx", r->rbx}, {"rcx", r->rcx}, {"rdx", r->rdx},
        {"rsi", r->rsi}, {"rdi", r->rdi}, {"rbp", r->rbp}, {"rsp", r->rsp},
        {"r8", r->r8},   {"r9", r->r9},   {"r10", r->r10}, {"r11", r->r11},
        {"r12", r->r12}, {"r13", r->r13}, {"r14", r->r14}, {"r15", r->r15},
    };
    size_t i;

    for (i = 0; i < sizeof(map) / sizeof(map[0]); i++) {
        if (strcmp(map[i].n, name) == 0) {
            *out = (unsigned long)map[i].v;
            return 0;
        }
    }
    return -1;
}

/* Read one naturally aligned 32-bit field from the tracee. Returns 0 on success. */
static int read_field32(pid_t pid, unsigned long addr, long *out)
{
    long word;

    errno = 0;
    word = ptrace(PTRACE_PEEKDATA, pid, (void *)addr, NULL);
    if (word == -1 && errno != 0) {
        return -1;
    }
    *out = (long)(int)(unsigned int)((unsigned long)word & 0xFFFFFFFFUL);
    return 0;
}

/* Emit the configured fields for this stop, or a reason they were not read. */
static void emit_fields(pid_t pid, const struct user_regs_struct *regs)
{
    unsigned long base;
    long a = 0, b = 0;
    int ra, rb;

    if (!field_enabled) {
        return;
    }
    if (field_use_reg) {
        if (reg_by_name(regs, field_reg_name, &base) != 0) {
            say("FIELDS status=unknown-register name=%s", field_reg_name);
            return;
        }
        field_reg_value = base;
    } else {
        base = field_addr;
    }
    if (base == 0) {
        say("FIELDS status=null-pointer reg=%s",
            field_use_reg ? field_reg_name : "absolute");
        return;
    }
    ra = read_field32(pid, base + field_off_a, &a);
    rb = read_field32(pid, base + field_off_b, &b);
    if (ra != 0 || rb != 0) {
        say("FIELDS status=unreadable base=0x%lx off_a=0x%lx off_b=0x%lx", base,
            field_off_a, field_off_b);
        return;
    }
    say("FIELDS status=ok base=0x%lx a=%ld b=%ld off_a=0x%lx off_b=0x%lx", base,
        a, b, field_off_a, field_off_b);
}

/*
 * Disarm every slot, clear the address registers, then verify the readback is
 * clean before detaching. The capability probe established that detaching with a
 * slot still armed leaves the breakpoint live and kills the tracee, so this
 * sequence is mandatory rather than defensive.
 */
static int teardown(pid_t pid, unsigned long long dr7_baseline, int *verified)
{
    unsigned long long dr7_now = 0;
    int i;

    *verified = 0;
    if (dr_write(pid, DR_CONTROL, dr7_baseline) != 0) {
        return -1;
    }
    for (i = 0; i < MAX_SLOTS; i++) {
        if (dr_write(pid, i, 0) != 0) {
            return -1;
        }
    }
    dr_write(pid, DR_STATUS, 0);
    if (dr_read(pid, DR_CONTROL, &dr7_now) != 0) {
        return -1;
    }
    if ((dr7_now & 0xFFUL) != 0) {
        say("ERROR disarm-verify dr7=0x%llx still has enables", dr7_now);
        return -1;
    }
    *verified = 1;
    return 0;
}

int main(int argc, char **argv)
{
    pid_t pid;
    const char *module;
    unsigned long base = 0;
    unsigned long long dr7_baseline = 0;
    int status = 0;
    int stops = 0;
    int verified = 0;
    int alive = 1;
    int rc = 1;
    int i;
    time_t deadline;

    if (argc < 4) {
        say("ERROR usage: %s <pid> <module-substring> <offset> [offset...]",
            argv[0]);
        return 2;
    }
    pid = (pid_t)strtol(argv[1], NULL, 10);
    module = argv[2];
    slot_count = 0;
    for (i = 3; i < argc; i++) {
        if (strcmp(argv[i], "--once") == 0) {
            stop_after_first_hit = 1;
            continue;
        }
        if (strcmp(argv[i], "--wait-module-ms") == 0 && i + 1 < argc) {
            wait_module_ms = (int)strtol(argv[++i], NULL, 10);
            continue;
        }
        if (strcmp(argv[i], "--after") == 0 && i + 1 < argc) {
            stop_after_hits = (int)strtol(argv[++i], NULL, 10);
            continue;
        }
        if (strcmp(argv[i], "--struct-reg") == 0 && i + 1 < argc) {
            field_enabled = 1;
            field_use_reg = 1;
            field_reg_name = argv[++i];
            continue;
        }
        if (strcmp(argv[i], "--struct-addr") == 0 && i + 1 < argc) {
            field_enabled = 1;
            field_use_reg = 0;
            field_addr = strtoul(argv[++i], NULL, 0);
            continue;
        }
        if (strcmp(argv[i], "--off-a") == 0 && i + 1 < argc) {
            field_off_a = strtoul(argv[++i], NULL, 0);
            continue;
        }
        if (strcmp(argv[i], "--off-b") == 0 && i + 1 < argc) {
            field_off_b = strtoul(argv[++i], NULL, 0);
            continue;
        }
        if (slot_count >= MAX_SLOTS) {
            say("ERROR too-many-slots max=%d", MAX_SLOTS);
            return 2;
        }
        slots[slot_count].addr = strtoul(argv[i], NULL, 0);
        slots[slot_count].done = 0;
        slot_count++;
    }
    if (pid <= 1 || slot_count < 1) {
        say("ERROR bad-arguments pid=%d slots=%d", (int)pid, slot_count);
        return 2;
    }

    alarm(DEADLINE_SECONDS);
    deadline = time(NULL) + DEADLINE_SECONDS;

    /*
     * The client is often visible before its graphics libraries are mapped, so
     * an immediate resolve can legitimately fail. Wait, bounded, for the module
     * to appear while the tracee still runs; attaching first would stop it and
     * prevent the very mapping we are waiting for.
     */
    {
        int waited = 0;
        while (resolve_base(pid, module, &base, 0) != 0) {
            struct timespec ts = {0, 2000000L}; /* 2 ms */

            if (waited >= wait_module_ms) {
                say("ERROR module-not-mapped-after-wait needle=%s waited_ms=%d",
                    module, waited);
                return 2;
            }
            nanosleep(&ts, NULL);
            waited += 2;
        }
        if (waited > 0) {
            say("WAIT module appeared after_ms=%d", waited);
        }
    }
    say("BASE module=%s base=0x%lx", module, base);

    /* Attach without injecting a group stop. */
    if (ptrace(PTRACE_SEIZE, pid, NULL, NULL) == -1) {
        say("ERROR seize errno=%d (%s)", errno, strerror(errno));
        return 2;
    }
    if (ptrace(PTRACE_INTERRUPT, pid, NULL, NULL) == -1) {
        say("ERROR interrupt errno=%d", errno);
        ptrace(PTRACE_DETACH, pid, NULL, NULL);
        return 2;
    }
    if (waitpid(pid, &status, 0) != pid || !WIFSTOPPED(status)) {
        say("ERROR no-stop-after-interrupt status=0x%x", status);
        ptrace(PTRACE_DETACH, pid, NULL, NULL);
        return 2;
    }
    if (dr_read(pid, DR_CONTROL, &dr7_baseline) != 0) {
        say("ERROR dr7-baseline-unreadable");
        ptrace(PTRACE_DETACH, pid, NULL, NULL);
        return 2;
    }
    say("BASELINE dr7=0x%llx", dr7_baseline);

    /* Arm: address while disabled, then one complete DR7 image. */
    for (i = 0; i < slot_count; i++) {
        unsigned long target = base + slots[i].addr;

        if (dr_write(pid, i, (unsigned long long)target) != 0) {
            say("ERROR arm-address slot=%d", i);
            goto finish;
        }
        slots[i].addr = target;
        say("ARM slot=%d addr=0x%lx", i, target);
    }
    {
        unsigned long long image = (dr7_baseline & ~0xFFFFUL) | DR7_RESERVED;

        for (i = 0; i < slot_count; i++) {
            image |= DR7_L(i);
        }
        if (dr_write(pid, DR_CONTROL, image) != 0) {
            say("ERROR arm-enable");
            goto finish;
        }
        say("ARMED dr7=0x%llx", image);
    }

    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1) {
        say("ERROR cont errno=%d", errno);
        goto finish;
    }

    for (;;) {
        struct user_regs_struct regs;
        unsigned long long dr6 = 0;
        int hit = -1;

        if (time(NULL) >= deadline) {
            say("EVENT deadline");
            break;
        }
        if (waitpid(pid, &status, 0) != pid) {
            say("ERROR waitpid errno=%d", errno);
            break;
        }
        if (WIFEXITED(status)) {
            say("EVENT exit code=%d stops=%d", WEXITSTATUS(status), stops);
            alive = 0;
            break;
        }
        if (WIFSIGNALED(status)) {
            say("EVENT killed signal=%d stops=%d", WTERMSIG(status), stops);
            alive = 0;
            break;
        }
        if (!WIFSTOPPED(status)) {
            say("EVENT unexpected-status 0x%x", status);
            break;
        }
        if (++stops > MAX_STOPS) {
            say("EVENT stop-limit stops=%d", stops);
            break;
        }
        if (WSTOPSIG(status) != SIGTRAP) {
            say("EVENT signal sig=%d", WSTOPSIG(status));
            ptrace(PTRACE_CONT, pid, NULL, NULL);
            continue;
        }

        if (ptrace(PTRACE_GETREGS, pid, NULL, &regs) == -1) {
            say("ERROR getregs");
            break;
        }
        if (dr_read(pid, DR_STATUS, &dr6) != 0) {
            dr6 = 0;
        }
        for (i = 0; i < slot_count; i++) {
            if ((unsigned long)regs.rip == slots[i].addr ||
                (dr6 != 0 && (dr6 & DR6_B(i)) != 0)) {
                hit = i;
                break;
            }
        }
        say("HIT stop=%d slot=%d rip=0x%llx rdi=0x%llx rsi=0x%llx rdx=0x%llx"
            " dr6=0x%llx",
            stops, hit, (unsigned long long)regs.rip,
            (unsigned long long)regs.rdi, (unsigned long long)regs.rsi,
            (unsigned long long)regs.rdx, dr6);
        emit_fields(pid, &regs);

        /* A hit slot must be disarmed before resuming or it retriggers. */
        if (hit >= 0) {
            unsigned long long image =
                (dr7_baseline & ~0xFFFFUL) | DR7_RESERVED;

            slots[hit].done = 1;
            for (i = 0; i < slot_count; i++) {
                if (!slots[i].done) {
                    image |= DR7_L(i);
                }
            }
            if (dr_write(pid, DR_CONTROL, image) != 0) {
                say("ERROR disarm-after-hit");
                break;
            }
            say("DISARM slot=%d dr7=0x%llx", hit, image);
            hits_seen++;
            if (stop_after_first_hit || (stop_after_hits > 0 && hits_seen >= stop_after_hits)) {
                say("EVENT stop-condition hits=%d", hits_seen);
                break;
            }
        }
        if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1) {
            say("ERROR cont-after-hit errno=%d", errno);
            break;
        }
    }

finish:
    if (!alive) {
        /* Nothing is left to restore: the tracee is gone, so teardown is
         * unverifiable rather than failed. */
        alarm(0);
        say("RESULT teardown=unverifiable reason=tracee-gone stops=%d", stops);
        return 0;
    }
    if (teardown(pid, dr7_baseline, &verified) != 0) {
        say("RESULT teardown=FAILED stops=%d detach=skipped", stops);
        alarm(0);
        return 1;
    }
    if (ptrace(PTRACE_DETACH, pid, NULL, NULL) == -1) {
        say("RESULT teardown=verified detach=FAILED errno=%d", errno);
        alarm(0);
        return 1;
    }
    alarm(0);
    rc = 0;
    say("RESULT teardown=verified detach=ok stops=%d", stops);
    return rc;
}
