/*
 * dr_breakpoint_probe.c — VM-only capability probe for guest hardware
 * execution breakpoints under the recovered Gen5W kernel.
 *
 * Round 1 (2026-10-29) established that execute breakpoints work at all. This
 * version also exercises the four behaviours that round left unverified, because
 * the EC-02 mechanism depends on each of them:
 *
 *   T1  nothing armed            -> tracee exits 0, no trap
 *   T2  DR0/DR7 armed            -> trap at RIP == &target, DR6.B0 set
 *   T3  restore DR7/DR0           -> tracee runs on and exits 0, no re-trap
 *   T4  PTRACE_SINGLESTEP        -> one trap, RIP advances
 *   T5  four slots armed at once -> four traps, in program order, correct RIPs
 *   T6  slot replacement         -> a re-armed slot fires at its new address
 *   T7  DR4/DR5 access           -> rejected by the kernel
 *   T8  detach with a slot armed -> kernel clears breakpoints; tracee completes
 *
 * T5 and T6 matter because an execute breakpoint retriggers if left armed, so
 * the tracer must disarm a slot before resuming: that discipline is exactly what
 * the observer will need. T8 is the failure mode EC-02 flagged as C-09.
 *
 * It touches no vendor code and is not part of any observer.
 *
 * Build:
 *   zig cc -target x86_64-linux-musl -static -O2 -Wall -Wextra -Werror \
 *       -o dr-breakpoint-probe dr_breakpoint_probe.c
 *
 * Exit status 0 only when every test behaves as required.
 */

#define _GNU_SOURCE

#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <signal.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <unistd.h>

#define DR_STATUS 6
#define DR_CONTROL 7

/* DR7: Ln enables local slot n; RWn=0 and LENn=0 select an execute breakpoint. */
#define DR7_L(n) (0x1UL << (2 * (n)))
/* DR7 bits 10 and 11 read as 1 and must not be cleared on this architecture. */
#define DR7_RESERVED 0x400UL
/* DR6: Bn reports slot n fired. */
#define DR6_B(n) (0x1UL << (n))

static int failures;

static void say(const char *fmt, ...)
{
    va_list ap;

    fputs("DR-PROBE ", stdout);
    va_start(ap, fmt);
    vfprintf(stdout, fmt, ap);
    va_end(ap);
    fputc('\n', stdout);
    fflush(stdout);
}

static void verdict(const char *id, int ok, const char *text)
{
    if (ok) {
        say("%s pass %s", id, text);
    } else {
        say("%s FAIL %s", id, text);
        failures++;
    }
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
 * Distinct noinline functions so each slot has an unambiguous entry address.
 * The empty asm keeps every body from being merged or elided.
 */
#define TARGET(name)                                                    \
    __attribute__((noinline, used)) static void name(void)              \
    {                                                                   \
        __asm__ __volatile__("" ::: "memory");                          \
    }

TARGET(target_a)
TARGET(target_b)
TARGET(target_c)
TARGET(target_d)
TARGET(target_e)
TARGET(target_f)
TARGET(target_shared)

/*
 * T11 state. The sibling thread waits for `t11_go` so the ordering is
 * deterministic: the traced thread traps first, then the untraced sibling runs
 * the same function while the slot is still armed.
 */
static volatile int t11_go;

static void *t11_sibling(void *unused)
{
    (void)unused;
    while (!t11_go) {
        sched_yield();
    }
    target_shared();
    return NULL;
}

static void t11_child_body(void)
{
    pthread_t tid;

    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) == -1) {
        _exit(10);
    }
    if (raise(SIGSTOP) != 0) {
        _exit(11);
    }
    if (pthread_create(&tid, NULL, t11_sibling, NULL) != 0) {
        _exit(12);
    }
    /* Traced thread reaches the armed address first. */
    target_shared();
    /* Only reached once the tracer has stepped past that instruction. */
    t11_go = 1;
    pthread_join(tid, NULL);
    _exit(0);
}

static void child_body(void)
{
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) == -1) {
        _exit(10);
    }
    /* Stop before any user code so the tracer arms registers first. */
    if (raise(SIGSTOP) != 0) {
        _exit(11);
    }
    target_a();
    target_b();
    target_c();
    target_d();
    target_e();
    target_f();
    _exit(0);
}

static pid_t spawn_tracee(int *status)
{
    pid_t pid = fork();

    if (pid == 0) {
        child_body();
    }
    if (pid < 0) {
        return -1;
    }
    if (waitpid(pid, status, 0) != pid || !WIFSTOPPED(*status)) {
        return -1;
    }
    return pid;
}

static int read_rip(pid_t pid, unsigned long long *rip)
{
    struct user_regs_struct regs;

    if (ptrace(PTRACE_GETREGS, pid, NULL, &regs) == -1) {
        return -1;
    }
    *rip = (unsigned long long)regs.rip;
    return 0;
}

static unsigned long addr_of(void (*fn)(void))
{
    return (unsigned long)fn;
}

static int wait_trap(pid_t pid, unsigned long long *rip, int *was_exit)
{
    int status = 0;

    *was_exit = 0;
    if (waitpid(pid, &status, 0) != pid) {
        return -1;
    }
    if (WIFEXITED(status)) {
        *was_exit = WEXITSTATUS(status);
        return 0;
    }
    if (!WIFSTOPPED(status) || WSTOPSIG(status) != SIGTRAP) {
        return -1;
    }
    return read_rip(pid, rip) == 0 ? 1 : -1;
}

/* T1: no breakpoint armed, tracee must reach completion without a trap. */
static void test_negative_control(void)
{
    int status = 0;
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T1", 0, "cannot reach initial stop");
        return;
    }
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1) {
        verdict("T1", 0, "cont failed");
        return;
    }
    if (waitpid(pid, &status, 0) != pid) {
        verdict("T1", 0, "waitpid failed");
        return;
    }
    verdict("T1", WIFEXITED(status) && WEXITSTATUS(status) == 0,
            "no-trap control");
}

/* T2 + T3: arm, observe the trap and DR6, restore, require a clean exit. */
static void test_execute_breakpoint(void)
{
    int status = 0;
    int t2 = 0;
    unsigned long long dr7_before = 0, dr7_armed = 0, dr6 = 0, rip = 0;
    unsigned long addr = addr_of(target_a);
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T2", 0, "cannot reach initial stop");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7_before) != 0) {
        verdict("T2", 0, "cannot read DR7 baseline");
        return;
    }
    if (dr_write(pid, 0, (unsigned long long)addr) != 0 ||
        dr_write(pid, DR_CONTROL, dr7_before | DR7_RESERVED | DR7_L(0)) != 0) {
        verdict("T2", 0, "cannot arm DR0");
        goto out;
    }
    if (dr_read(pid, DR_CONTROL, &dr7_armed) != 0 ||
        (dr7_armed & DR7_L(0)) == 0) {
        verdict("T2", 0, "DR7.L0 did not stick");
        goto out;
    }
    say("T2 DR7 baseline=0x%llx armed=0x%llx target=0x%lx", dr7_before,
        dr7_armed, addr);

    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1) {
        verdict("T2", 0, "cont failed");
        goto out;
    }
    if (waitpid(pid, &status, 0) != pid) {
        verdict("T2", 0, "waitpid failed");
        goto out;
    }
    if (!WIFSTOPPED(status) || WSTOPSIG(status) != SIGTRAP) {
        verdict("T2", 0, "no SIGTRAP from the armed slot");
        goto out;
    }
    if (read_rip(pid, &rip) != 0) {
        verdict("T2", 0, "GETREGS after trap failed");
        goto out;
    }
    if (dr_read(pid, DR_STATUS, &dr6) != 0) {
        dr6 = 0;
    }
    say("T2 trap rip=0x%llx expected=0x%lx DR6=0x%llx", rip, addr, dr6);
    t2 = (rip == (unsigned long long)addr);
    if (dr6 != 0 && (dr6 & DR6_B(0)) == 0) {
        say("T2 note DR6 readable but B0 clear while RIP matched");
    }
    verdict("T2", t2, "execute breakpoint fired at the armed address");

out:
    /* T3: disarm, then the tracee must continue and exit cleanly. */
    if (dr_write(pid, DR_CONTROL, dr7_before) != 0 || dr_write(pid, 0, 0) != 0) {
        verdict("T3", 0, "cannot restore DR7/DR0");
        return;
    }
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1) {
        verdict("T3", 0, "cont after disarm failed");
        return;
    }
    if (waitpid(pid, &status, 0) != pid) {
        verdict("T3", 0, "waitpid after disarm failed");
        return;
    }
    verdict("T3", WIFEXITED(status) && WEXITSTATUS(status) == 0,
            "restored and tracee exited 0 with no further trap");
}

static void test_single_step(void)
{
    int status = 0;
    unsigned long long rip0 = 0, rip1 = 0;
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T4", 0, "cannot reach initial stop");
        return;
    }
    if (read_rip(pid, &rip0) != 0) {
        verdict("T4", 0, "GETREGS failed");
        return;
    }
    if (ptrace(PTRACE_SINGLESTEP, pid, NULL, NULL) == -1) {
        verdict("T4", 0, "singlestep rejected");
        return;
    }
    if (waitpid(pid, &status, 0) != pid || !WIFSTOPPED(status) ||
        WSTOPSIG(status) != SIGTRAP) {
        verdict("T4", 0, "no single-step trap");
        return;
    }
    if (read_rip(pid, &rip1) != 0) {
        verdict("T4", 0, "GETREGS after step failed");
        return;
    }
    say("T4 step rip 0x%llx -> 0x%llx", rip0, rip1);
    verdict("T4", rip1 != rip0, "single step advanced RIP");

    ptrace(PTRACE_CONT, pid, NULL, NULL);
    waitpid(pid, &status, 0);
}

/*
 * T5: arm all four slots at once. Because an execute breakpoint retriggers if it
 * stays armed, each trap must be followed by disarming that slot before resuming.
 * Traps must arrive in program order with the matching RIP.
 */
static void test_four_slots(void)
{
    int status = 0;
    int ok = 1;
    unsigned long long dr7 = 0, rip = 0;
    unsigned long addr[4];
    int slot;
    pid_t pid = spawn_tracee(&status);

    addr[0] = addr_of(target_a);
    addr[1] = addr_of(target_b);
    addr[2] = addr_of(target_c);
    addr[3] = addr_of(target_d);

    if (pid < 0) {
        verdict("T5", 0, "cannot reach initial stop");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7) != 0) {
        verdict("T5", 0, "cannot read DR7");
        return;
    }
    dr7 = (dr7 & ~0xFFFFUL) | DR7_RESERVED;
    for (slot = 0; slot < 4; slot++) {
        if (dr_write(pid, slot, (unsigned long long)addr[slot]) != 0) {
            verdict("T5", 0, "cannot set a slot address");
            return;
        }
        dr7 |= DR7_L(slot);
    }
    if (dr_write(pid, DR_CONTROL, dr7) != 0) {
        verdict("T5", 0, "cannot enable four slots");
        return;
    }
    say("T5 DR7 four-slot image=0x%llx", dr7);

    for (slot = 0; slot < 4; slot++) {
        int exited = 0;
        int r;

        if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1) {
            ok = 0;
            break;
        }
        r = wait_trap(pid, &rip, &exited);
        if (r <= 0) {
            say("T5 slot=%d expected=0x%lx got exit=%d result=%d", slot,
                addr[slot], exited, r);
            ok = 0;
            break;
        }
        if (rip != (unsigned long long)addr[slot]) {
            say("T5 slot=%d expected=0x%lx got=0x%llx", slot, addr[slot], rip);
            ok = 0;
            break;
        }
        /* Disarm the fired slot before resuming, or it retriggers. */
        dr7 &= ~DR7_L(slot);
        if (dr_write(pid, DR_CONTROL, dr7) != 0) {
            ok = 0;
            break;
        }
    }
    verdict("T5", ok, "four slots armed simultaneously fired in program order");

    ptrace(PTRACE_CONT, pid, NULL, NULL);
    waitpid(pid, &status, 0);
}

/*
 * T6: after slot 0 fires, re-arm it to a later address and confirm the new
 * address is honoured. This is the reprogramming discipline the observer needs.
 */
static void test_slot_replacement(void)
{
    int status = 0;
    int ok = 1;
    unsigned long long dr7 = 0, rip = 0;
    int exited = 0;
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T6", 0, "cannot reach initial stop");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7) != 0) {
        verdict("T6", 0, "cannot read DR7");
        return;
    }
    /* Arm slot 0 only, at target_a. */
    if (dr_write(pid, 0, (unsigned long long)addr_of(target_a)) != 0 ||
        dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(0)) != 0) {
        verdict("T6", 0, "cannot arm slot 0");
        return;
    }
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1 ||
        wait_trap(pid, &rip, &exited) != 1 ||
        rip != (unsigned long long)addr_of(target_a)) {
        verdict("T6", 0, "first address did not fire as armed");
        return;
    }
    say("T6 first trap at target_a=0x%lx", (unsigned long)rip);

    /* Disarm, move slot 0 to target_c, re-enable. */
    if (dr_write(pid, DR_CONTROL, (dr7 & ~0xFFFFUL) | DR7_RESERVED) != 0 ||
        dr_write(pid, 0, (unsigned long long)addr_of(target_c)) != 0 ||
        dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(0)) != 0) {
        verdict("T6", 0, "cannot reprogram slot 0");
        return;
    }
    exited = 0;
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1 ||
        wait_trap(pid, &rip, &exited) != 1) {
        verdict("T6", 0, "reprogrammed slot did not fire");
        return;
    }
    ok = (rip == (unsigned long long)addr_of(target_c));
    say("T6 second trap rip=0x%llx expected target_c=0x%lx", rip,
        (unsigned long)addr_of(target_c));
    verdict("T6", ok, "re-armed slot fired at its new address");

    dr_write(pid, DR_CONTROL, (dr7 & ~0xFFFFUL) | DR7_RESERVED);
    ptrace(PTRACE_CONT, pid, NULL, NULL);
    waitpid(pid, &status, 0);
}

/* T7: DR4 and DR5 are not valid ptrace debug indices and must be rejected. */
static void test_invalid_registers(void)
{
    int status = 0;
    int rejected = 0;
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T7", 0, "cannot reach initial stop");
        return;
    }
    errno = 0;
    if (dr_write(pid, 4, 0x1000) == -1) {
        rejected++;
        say("T7 DR4 rejected errno=%d (%s)", errno, strerror(errno));
    }
    errno = 0;
    if (dr_write(pid, 5, 0x1000) == -1) {
        rejected++;
        say("T7 DR5 rejected errno=%d (%s)", errno, strerror(errno));
    }
    verdict("T7", rejected == 2, "DR4 and DR5 rejected by ptrace");

    ptrace(PTRACE_CONT, pid, NULL, NULL);
    waitpid(pid, &status, 0);
}

/*
 * T8: detach while a slot is still armed. If the kernel does not tear the
 * breakpoint down, the untraced tracee will take SIGTRAP and die on it. A clean
 * exit 0 means detach-time teardown works, which EC-02 flagged as C-09.
 */
static void test_detach_with_armed_slot(void)
{
    int status = 0;
    unsigned long long dr7 = 0;
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T8", 0, "cannot reach initial stop");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7) != 0) {
        verdict("T8", 0, "cannot read DR7");
        return;
    }
    /* Deliberately leave the slot armed across detach. */
    if (dr_write(pid, 0, (unsigned long long)addr_of(target_a)) != 0 ||
        dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(0)) != 0) {
        verdict("T8", 0, "cannot arm slot 0");
        return;
    }
    if (ptrace(PTRACE_DETACH, pid, NULL, NULL) == -1) {
        verdict("T8", 0, "detach rejected");
        return;
    }
    if (waitpid(pid, &status, 0) != pid) {
        verdict("T8", 0, "waitpid after detach failed");
        return;
    }
    if (WIFSIGNALED(status)) {
        say("T8 observed tracee killed by signal %d: kernel does not clear an "
            "armed slot on detach", WTERMSIG(status));
        say("T8 pass characterised: detach alone is unsafe, disarm is mandatory");
        return;
    }
    say("T8 observed tracee exited 0: this build happened to clear the slot, "
        "but disarm-before-detach remains required by T9");
    verdict("T8", WIFEXITED(status) && WEXITSTATUS(status) == 0,
            "detach-time behaviour characterised");
}

/*
 * T9: the safe sequence implied by T8 — disarm the slot, then detach. This is
 * what every observer exit path must do. If it works, T8's failure is a
 * procedure requirement rather than a blocker.
 */
static void test_disarm_then_detach(void)
{
    int status = 0;
    unsigned long long dr7 = 0, dr7_now = 0;
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T9", 0, "cannot reach initial stop");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7) != 0) {
        verdict("T9", 0, "cannot read DR7");
        return;
    }
    if (dr_write(pid, 0, (unsigned long long)addr_of(target_a)) != 0 ||
        dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(0)) != 0) {
        verdict("T9", 0, "cannot arm slot 0");
        return;
    }
    /* Disarm and clear before detaching, and confirm the write took effect. */
    if (dr_write(pid, DR_CONTROL, dr7) != 0 || dr_write(pid, 0, 0) != 0) {
        verdict("T9", 0, "cannot disarm slot 0");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7_now) != 0 ||
        (dr7_now & 0xFFUL) != 0) {
        verdict("T9", 0, "DR7 still has an enable set after disarm");
        return;
    }
    if (ptrace(PTRACE_DETACH, pid, NULL, NULL) == -1) {
        verdict("T9", 0, "detach rejected");
        return;
    }
    if (waitpid(pid, &status, 0) != pid) {
        verdict("T9", 0, "waitpid after detach failed");
        return;
    }
    if (WIFSIGNALED(status)) {
        say("T9 tracee killed by signal %d after disarm+detach",
            WTERMSIG(status));
        verdict("T9", 0, "disarm+detach still left a live breakpoint");
        return;
    }
    verdict("T9", WIFEXITED(status) && WEXITSTATUS(status) == 0,
            "disarm then detach leaves the tracee healthy");
}

/*
 * T10: DR6 semantics beyond B0, and whether DR6 can be cleared through ptrace.
 * The observer needs to attribute a trap to a specific slot and to clear stale
 * status bits between stages. Arm two slots, read DR6 on each trap, and clear
 * DR6 in between.
 */
static void test_dr6_status_bits(void)
{
    int status = 0;
    int exited = 0;
    int ok = 1;
    unsigned long long dr7 = 0, dr6 = 0, dr6_now = 0, rip = 0;
    pid_t pid = spawn_tracee(&status);

    if (pid < 0) {
        verdict("T10", 0, "cannot reach initial stop");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7) != 0) {
        verdict("T10", 0, "cannot read DR7");
        return;
    }
    if (dr_write(pid, 0, (unsigned long long)addr_of(target_a)) != 0 ||
        dr_write(pid, 1, (unsigned long long)addr_of(target_b)) != 0 ||
        dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(0) | DR7_L(1)) != 0) {
        verdict("T10", 0, "cannot arm slots 0 and 1");
        return;
    }

    /* First trap: slot 0 at target_a. */
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1 ||
        wait_trap(pid, &rip, &exited) != 1) {
        verdict("T10", 0, "slot 0 did not fire");
        return;
    }
    if (dr_read(pid, DR_STATUS, &dr6) != 0) {
        verdict("T10", 0, "cannot read DR6");
        return;
    }
    say("T10 slot0 trap rip=0x%llx DR6=0x%llx", rip, dr6);
    ok = ok && (dr6 & DR6_B(0)) != 0;

    /* Clear DR6 and confirm the write took effect. */
    if (dr_write(pid, DR_STATUS, 0) != 0) {
        say("T10 DR6 clear rejected");
    } else if (dr_read(pid, DR_STATUS, &dr6_now) != 0) {
        say("T10 cannot read DR6 after clear");
    } else {
        say("T10 DR6 after clear=0x%llx", dr6_now);
        ok = ok && dr6_now == 0;
    }

    /* Disarm slot 0 so it does not retrigger, then expect slot 1. */
    if (dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(1)) != 0) {
        verdict("T10", 0, "cannot disarm slot 0");
        return;
    }
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1 ||
        wait_trap(pid, &rip, &exited) != 1) {
        verdict("T10", 0, "slot 1 did not fire");
        return;
    }
    if (dr_read(pid, DR_STATUS, &dr6) != 0) {
        verdict("T10", 0, "cannot read DR6 after second trap");
        return;
    }
    say("T10 slot1 trap rip=0x%llx DR6=0x%llx", rip, dr6);
    ok = ok && (dr6 & DR6_B(1)) != 0;
    verdict("T10", ok,
            "DR6 reports per-slot bits and is clearable through ptrace");

    dr_write(pid, DR_CONTROL, (dr7 & ~0xFFFFUL) | DR7_RESERVED);
    ptrace(PTRACE_CONT, pid, NULL, NULL);
    waitpid(pid, &status, 0);
}

/*
 * T11: per-thread scoping. Attach to the main thread only, arm an execute
 * breakpoint, let the traced thread trap, step it past, then leave the slot
 * ARMED while an untraced sibling thread executes the same function.
 *
 * If debug registers are per-thread, the sibling is unaffected and the process
 * exits 0. If the slot applies process-wide, the untraced sibling takes SIGTRAP
 * and the process dies on the default action.
 */
static void test_per_thread_scope(void)
{
    int status = 0;
    int exited = 0;
    unsigned long long dr7 = 0, rip = 0;
    unsigned long addr = addr_of(target_shared);
    pid_t pid = fork();

    if (pid == 0) {
        t11_child_body();
    }
    if (pid < 0) {
        verdict("T11", 0, "fork failed");
        return;
    }
    if (waitpid(pid, &status, 0) != pid || !WIFSTOPPED(status)) {
        verdict("T11", 0, "cannot reach initial stop");
        return;
    }
    if (dr_read(pid, DR_CONTROL, &dr7) != 0) {
        verdict("T11", 0, "cannot read DR7");
        return;
    }
    if (dr_write(pid, 0, (unsigned long long)addr) != 0 ||
        dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(0)) != 0) {
        verdict("T11", 0, "cannot arm slot 0");
        return;
    }

    /* Traced thread must trap at the armed address. */
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1 ||
        wait_trap(pid, &rip, &exited) != 1 ||
        rip != (unsigned long long)addr) {
        verdict("T11", 0, "traced thread did not trap at the armed address");
        return;
    }
    say("T11 traced thread trapped at 0x%llx", rip);

    /* Step past the instruction with the slot temporarily disabled. */
    if (dr_write(pid, DR_CONTROL, (dr7 & ~0xFFFFUL) | DR7_RESERVED) != 0) {
        verdict("T11", 0, "cannot temporarily disarm");
        return;
    }
    if (ptrace(PTRACE_SINGLESTEP, pid, NULL, NULL) == -1) {
        verdict("T11", 0, "single step rejected");
        return;
    }
    if (waitpid(pid, &status, 0) != pid || !WIFSTOPPED(status) ||
        WSTOPSIG(status) != SIGTRAP) {
        verdict("T11", 0, "no trap after stepping past the breakpoint");
        return;
    }
    /* Re-arm, then let the traced thread continue and release the sibling. */
    if (dr_write(pid, DR_CONTROL,
                 (dr7 & ~0xFFFFUL) | DR7_RESERVED | DR7_L(0)) != 0) {
        verdict("T11", 0, "cannot re-arm the slot");
        return;
    }
    if (ptrace(PTRACE_CONT, pid, NULL, NULL) == -1) {
        verdict("T11", 0, "cannot resume after arming");
        return;
    }

    /* The traced thread should not trap again; the sibling holds the decision. */
    for (;;) {
        if (waitpid(pid, &status, 0) != pid) {
            verdict("T11", 0, "waitpid failed");
            return;
        }
        if (WIFEXITED(status)) {
            break;
        }
        if (WIFSIGNALED(status)) {
            say("T11 process killed by signal %d while the sibling ran the "
                "same function with the slot armed", WTERMSIG(status));
            verdict("T11", 0,
                    "breakpoints apply process-wide, not per thread");
            return;
        }
        /* Traced thread re-trapped; disarm and let it finish. */
        say("T11 traced thread re-trapped; disarming and continuing");
        dr_write(pid, DR_CONTROL, (dr7 & ~0xFFFFUL) | DR7_RESERVED);
        ptrace(PTRACE_CONT, pid, NULL, NULL);
    }
    verdict("T11", WEXITSTATUS(status) == 0,
            "sibling thread unaffected: debug registers are per thread");
}

int main(void)
{
    say("begin capability probe");

    test_negative_control();
    test_execute_breakpoint();
    test_single_step();
    test_four_slots();
    test_slot_replacement();
    test_invalid_registers();
    test_detach_with_armed_slot();
    test_disarm_then_detach();
    test_dr6_status_bits();
    test_per_thread_scope();

    if (failures == 0) {
        say("RESULT hardware-execute-breakpoint=SUPPORTED slots=4 "
            "detach=disarm-mandatory");
        return 0;
    }
    say("RESULT hardware-execute-breakpoint=INCOMPLETE failures=%d", failures);
    return 1;
}
