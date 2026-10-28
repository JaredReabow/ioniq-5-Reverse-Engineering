/* VM-only x86-64 fatal-signal observer. No register or target-memory writes.
 * Linux PTRACE_SEIZE avoids SIGSTOP/group-stop side effects. Only an explicitly
 * selected authentic early Qt-client main thread is observed; other threads
 * are not traced. Output is private research evidence, not an unwind/backtrace.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t cancelled;
static void cancel(int sig) { (void)sig; cancelled = 1; }
static double now(void)
{
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t)) return -1;
    return t.tv_sec + t.tv_nsec / 1000000000.0;
}
static int fatal_signal(int sig)
{
    return sig == SIGSEGV || sig == SIGBUS || sig == SIGILL || sig == SIGABRT;
}
static int allowed(pid_t pid)
{
    char path[64], exe[512];
    snprintf(path, sizeof(path), "/proc/%ld/exe", (long)pid);
    ssize_t n = readlink(path, exe, sizeof(exe) - 1);
    if (n < 0 || (size_t)n >= sizeof(exe) - 1) return 0;
    exe[n] = 0;
    return !strcmp(exe, "/app/bin/AppCamera") ||
           !strcmp(exe, "/app/bin/AppStandbyClock");
}
static void maps(pid_t pid)
{
    char path[64], buf[4096];
    size_t total = 0, n;
    snprintf(path, sizeof(path), "/proc/%ld/maps", (long)pid);
    FILE *f = fopen(path, "r");
    if (!f) { perror("maps"); return; }
    puts("MAPS_BEGIN");
    while (total < 65536 && (n = fread(buf, 1, sizeof(buf), f))) {
        fwrite(buf, 1, n, stdout);
        total += n;
    }
    printf("\nMAPS_END bytes=%zu bounded_at=65536\n", total);
    fclose(f);
}
static int capture(pid_t pid, int sig)
{
    siginfo_t si;
    struct user_regs_struct r;
    int have_siginfo = 0, readable = 0;
    printf("FAULT tid=%ld signal=%d\n", (long)pid, sig);
    if (ptrace(PTRACE_GETSIGINFO, pid, 0, &si)) perror("GETSIGINFO");
    else {
        have_siginfo = 1;
        printf("SIGINFO signo=%d code=%d address=%p\n",
               si.si_signo, si.si_code, si.si_addr);
    }
    if (ptrace(PTRACE_GETREGS, pid, 0, &r)) perror("GETREGS");
    else {
        printf("REGS rip=%#llx rsp=%#llx rbp=%#llx rax=%#llx rbx=%#llx "
               "rcx=%#llx rdx=%#llx rsi=%#llx rdi=%#llx r8=%#llx r9=%#llx "
               "r10=%#llx r11=%#llx r12=%#llx r13=%#llx r14=%#llx r15=%#llx\n",
               (unsigned long long)r.rip, (unsigned long long)r.rsp,
               (unsigned long long)r.rbp, (unsigned long long)r.rax,
               (unsigned long long)r.rbx, (unsigned long long)r.rcx,
               (unsigned long long)r.rdx, (unsigned long long)r.rsi,
               (unsigned long long)r.rdi, (unsigned long long)r.r8,
               (unsigned long long)r.r9, (unsigned long long)r.r10,
               (unsigned long long)r.r11, (unsigned long long)r.r12,
               (unsigned long long)r.r13, (unsigned long long)r.r14,
               (unsigned long long)r.r15);
        puts("STACK_WORDS_BEGIN count=64 (candidate pointers, not an unwind)");
        for (unsigned i = 0; i < 64; ++i) {
            if (r.rsp > UINT64_MAX - (uint64_t)i * 8) break;
            uint64_t addr = r.rsp + (uint64_t)i * 8;
            errno = 0;
            long value = ptrace(PTRACE_PEEKDATA, pid, (void *)(uintptr_t)addr, 0);
            if (errno) printf("STACK address=%#llx error=%d\n",
                              (unsigned long long)addr, errno);
            else {
                ++readable;
                printf("STACK address=%#llx value=%#lx\n",
                       (unsigned long long)addr, (unsigned long)value);
            }
        }
        puts("STACK_WORDS_END");
    }
    maps(pid);
    printf("CAPTURE readable_stack_words=%d siginfo=%d\n", readable, have_siginfo);
    fflush(stdout);
    return have_siginfo && readable > 0;
}
static int stop_signal(int status)
{
    /* PTRACE_EVENT_STOP is synthetic, never inject its SIGTRAP on detach. */
    return ((unsigned)status >> 16) == PTRACE_EVENT_STOP ? 0 : WSTOPSIG(status);
}
static int detach(pid_t pid, int sig)
{
    if (ptrace(PTRACE_DETACH, pid, 0, (void *)(intptr_t)sig)) {
        perror("DETACH"); return 1;
    }
    printf("DETACHED signal_redelivered=%d\n", sig);
    return 0;
}
int main(int argc, char **argv)
{
    char *end;
    long value;
    pid_t pid;
    int status;
    if (argc != 2) return 2;
    errno = 0; value = strtol(argv[1], &end, 10);
    if (errno || argv[1][0] < '0' || argv[1][0] > '9' || *end ||
        value <= 1 || value > INT_MAX) return 2;
    pid = (pid_t)value;
    if (!allowed(pid)) { fputs("TARGET_REJECTED\n", stderr); return 3; }
    double start = now();
    if (start < 0) return 4;
    signal(SIGINT, cancel); signal(SIGTERM, cancel);
    if (ptrace(PTRACE_SEIZE, pid, 0, 0)) { perror("SEIZE"); return 5; }
    printf("SEIZED tid=%ld deadline_seconds=60 main_thread_only=1\n", (long)pid);
    fflush(stdout);
    int interrupting = 0, verified_stop = 0;
    double deadline = start + 60;
    for (;;) {
        pid_t got = waitpid(pid, &status, WNOHANG | __WALL);
        if (got < 0 && errno == EINTR) continue;
        if (got < 0) { perror("WAIT"); return 6; }
        if (got == pid) {
            if (WIFEXITED(status) || WIFSIGNALED(status)) {
                printf("EXIT_WITHOUT_CAPTURE status=%#x\n", status); return 7;
            }
            if (!WIFSTOPPED(status)) continue;
            int sig = stop_signal(status);
            if (!verified_stop) {
                if (!allowed(pid)) { detach(pid, sig); return 3; }
                verified_stop = 1;
            }
            if (fatal_signal(sig)) {
                int captured = capture(pid, sig);
                return detach(pid, sig) ? 8 : captured ? 0 : 10;
            }
            if (interrupting || cancelled) return detach(pid, sig) ? 8 : 9;
            if (((unsigned)status >> 16) == PTRACE_EVENT_STOP &&
                WSTOPSIG(status) != SIGTRAP) {
                /* Preserve external job-control stops until genuine SIGCONT. */
                if (ptrace(PTRACE_LISTEN, pid, 0, 0)) {
                    perror("LISTEN"); detach(pid, 0); return 8;
                }
                continue;
            }
            if (ptrace(PTRACE_CONT, pid, 0, (void *)(intptr_t)sig)) {
                perror("CONT"); detach(pid, sig); return 8;
            }
        }
        double t = now();
        if (t < 0 || cancelled || t >= deadline) {
            if (!interrupting) {
                if (ptrace(PTRACE_INTERRUPT, pid, 0, 0)) {
                    perror("INTERRUPT"); return 8;
                }
                interrupting = 1;
                deadline = t + 2;
            } else if (t < 0 || t >= deadline) {
                /* No EXITKILL: tracer exit lets the kernel detach safely. */
                fputs("STOP_TIMEOUT; detach unconfirmed\n", stderr); return 8;
            }
        }
        usleep(10000);
    }
}
