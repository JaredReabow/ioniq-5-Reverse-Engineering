/* VM-only AppLauncher liveness control for slow TCG AppNavi startup. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

__attribute__((constructor))
static void keep_preload_launcher_local(void)
{
    /* AppLauncher retains this loaded shim, but vendor child processes inherit
     * the production environment unless a runner explicitly opts one in. */
    char executable[256];
    ssize_t n = readlink("/proc/self/exe", executable, sizeof(executable) - 1);
    if (n >= 0) {
        executable[n] = '\0';
        if (strcmp(executable, "/app/bin/AppLauncher") == 0)
            unsetenv("LD_PRELOAD");
    }
}

static int executable_is(pid_t pid, const char *expected)
{
    char proc_path[64];
    char executable[256];
    ssize_t n;
    if (pid == getpid())
        strcpy(proc_path, "/proc/self/exe");
    else
        snprintf(proc_path, sizeof(proc_path), "/proc/%ld/exe", (long)pid);
    n = readlink(proc_path, executable, sizeof(executable) - 1);
    if (n < 0)
        return 0;
    executable[n] = '\0';
    return strcmp(executable, expected) == 0;
}

static void append_log(const char *event, pid_t pid, int value)
{
    char line[128];
    int n;
    int fd = open("/tmp/launcher-chain/appnavi-liveness-compat.log",
                  O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0)
        return;
    n = snprintf(line, sizeof(line), "%s pid=%ld value=%d\n",
                 event, (long)pid, value);
    if (n > 0)
        (void)write(fd, line, (size_t)n);
    (void)close(fd);
}

int execve(const char *pathname, char *const argv[], char *const envp[])
{
    typedef int (*next_fn)(const char *, char *const[], char *const[]);
    static next_fn next;
    if (!next)
        next = (next_fn)dlsym(RTLD_NEXT, "execve");
    if (!next) {
        errno = ENOSYS;
        return -1;
    }

    const char *base = pathname ? strrchr(pathname, '/') : NULL;
    base = base ? base + 1 : pathname;
    if (!base || strcmp(base, "AppNavi") != 0)
        return next(pathname, argv, envp);

    size_t count = 0;
    while (envp && envp[count])
        ++count;
    char **with_preload = calloc(count + 2, sizeof(*with_preload));
    if (!with_preload)
        return next(pathname, argv, envp);

    size_t out = 0;
    for (size_t i = 0; i < count; ++i) {
        if (strncmp(envp[i], "LD_PRELOAD=", 11) != 0)
            with_preload[out++] = envp[i];
    }
    with_preload[out++] = "LD_PRELOAD=/navi-bg-0x0.so:/appnavi-egl-no-msaa-preload.so";
    with_preload[out] = NULL;
    append_log("TARGETED_APPNAVI_PRELOAD_NAVIBG", getpid(), 0);
    int rc = next(pathname, argv, with_preload);
    int saved_errno = errno;
    free(with_preload);
    errno = saved_errno;
    return rc;
}

int kill(pid_t pid, int signal_number)
{
    typedef int (*next_fn)(pid_t, int);
    static next_fn next;
    if (!next)
        next = (next_fn)dlsym(RTLD_NEXT, "kill");
    if (!next)
        return -1;
    if (access("/tmp/launcher-chain/enable-appnavi-liveness-compat", F_OK) == 0 &&
        executable_is(getpid(), "/app/bin/AppLauncher") &&
        executable_is(pid, "/navi/Bin/AppNavi") &&
        (signal_number == SIGTERM || signal_number == SIGKILL ||
         signal_number == SIGTRAP)) {
        append_log("BLOCKED_APPLAUNCHER_KILL", pid, signal_number);
        return 0;
    }
    return next(pid, signal_number);
}
