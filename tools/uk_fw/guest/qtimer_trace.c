/* Projection-only LD_PRELOAD shim: log QTimer arming, for the launcher only.
 *
 * Intercepts QTimer::setInterval(int), QTimer::start() and QTimer::start(int)
 * and writes one line per call to /dev/ttyS2 (the file-backed dbg channel), so
 * the boot can be correlated against the launcher's own wall-clock log.
 *
 * This changes no behaviour: each function resolves the real symbol via
 * dlsym(RTLD_NEXT) and forwards the call unchanged. NOT part of the shipped
 * system. Must be LD_PRELOAD'ed for AppLauncher only, never process-wide.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

static void qtmr_log(const char *tag, void *obj, long ms, void *ret)
{
    struct timespec mono, real;
    clock_gettime(CLOCK_MONOTONIC, &mono);
    clock_gettime(CLOCK_REALTIME, &real);
    long mono_ms = mono.tv_sec * 1000L + mono.tv_nsec / 1000000L;
    long real_ms = real.tv_sec * 1000L + real.tv_nsec / 1000000L;
    char buf[192];
    int n;
    if (ms >= 0)
        n = snprintf(buf, sizeof buf,
                     "QTMR %s obj=%p ms=%ld ret=%p t_mono=%ld t_real=%ld\n",
                     tag, obj, ms, ret, mono_ms, real_ms);
    else
        n = snprintf(buf, sizeof buf,
                     "QTMR %s obj=%p ret=%p t_mono=%ld t_real=%ld\n",
                     tag, obj, ret, mono_ms, real_ms);
    int fd = open("/dev/ttyS2", O_WRONLY | O_APPEND | O_CLOEXEC);
    if (fd >= 0) {
        (void)write(fd, buf, (size_t)n);
        close(fd);
    }
}

typedef void (*setInterval_fn)(void *, int);
typedef void (*start_fn)(void *);
typedef void (*start_int_fn)(void *, int);

void _ZN6QTimer11setIntervalEi(void *obj, int ms)
{
    static setInterval_fn real;
    if (!real)
        real = (setInterval_fn)dlsym(RTLD_NEXT, "_ZN6QTimer11setIntervalEi");
    qtmr_log("setInterval", obj, ms, __builtin_return_address(0));
    real(obj, ms);
}

void _ZN6QTimer5startEv(void *obj)
{
    static start_fn real;
    if (!real)
        real = (start_fn)dlsym(RTLD_NEXT, "_ZN6QTimer5startEv");
    qtmr_log("start", obj, -1, __builtin_return_address(0));
    real(obj);
}

void _ZN6QTimer5startEi(void *obj, int ms)
{
    static start_int_fn real;
    if (!real)
        real = (start_int_fn)dlsym(RTLD_NEXT, "_ZN6QTimer5startEi");
    qtmr_log("startInt", obj, ms, __builtin_return_address(0));
    real(obj, ms);
}
