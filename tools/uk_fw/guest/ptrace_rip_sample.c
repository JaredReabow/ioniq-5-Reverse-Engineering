/* VM-only bounded x86-64 instruction-pointer sampler for a guest process. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    struct user_regs_struct r;
    pid_t pid;
    int status;
    int i, j;
    if (argc != 2)
        return 2;
    pid = (pid_t)strtol(argv[1], 0, 10);
    for (i = 0; i < 32; ++i) {
        if (ptrace(PTRACE_ATTACH, pid, 0, 0) != 0) {
            perror("PTRACE_ATTACH");
            return 3;
        }
        if (waitpid(pid, &status, 0) != pid) {
            perror("waitpid");
            return 4;
        }
        if (ptrace(PTRACE_GETREGS, pid, 0, &r) != 0) {
            perror("PTRACE_GETREGS");
            return 5;
        }
        printf("sample=%d rip=%#llx rsp=%#llx stack=", i,
               (unsigned long long)r.rip, (unsigned long long)r.rsp);
        for (j = 0; j < 12; ++j) {
            long v;
            errno = 0;
            v = ptrace(PTRACE_PEEKDATA, pid,
                       (void *)(r.rsp + (unsigned long long)j * 8), 0);
            if (errno)
                printf(" ERR");
            else
                printf(" %#lx", (unsigned long)v);
        }
        putchar('\n');
        fflush(stdout);
        if (ptrace(PTRACE_DETACH, pid, 0, 0) != 0) {
            perror("PTRACE_DETACH");
            return 6;
        }
        usleep(20000);
    }
    return 0;
}
