/*
 * navi_bg_0x0.c — drive AppNavi's surface to a real 0x0 configure.
 *
 * Why this exists: ApplicationManager latches its navigation window byte only on a
 * background (BG) window notification, and the IVI compositor classifies a surface
 * as BG only when both width and height are non-positive. AppNavi never hides its
 * surface, so the latch never sets.
 *
 * A single null-buffer attach is not enough. In weston_surface_commit_state the
 * size block at 0x40f470 stores the previous `width_from_buffer` before the
 * null-buffer branch at 0x40f813 zeroes that field, so the first null attach keeps
 * the old positive size. A second null attach enters the same block with the field
 * already zero and therefore stores 0x0.
 *
 * This version deliberately uses no filesystem at all. The previous probe keyed off
 * a trigger file in /tmp and logged there too; a run produced no log and no effect,
 * which could not distinguish "never loaded" from "SMACK denied the path". So:
 *
 *   - load and timeline go to stderr (captured in the launcher log);
 *   - the hold window is derived from a monotonic clock and environment variables
 *     set at launch, which no label policy can refuse.
 *
 * Environment:
 *   NAVI_BG_HOLD_AT_MS   ms after process start at which holding begins
 *   NAVI_BG_HOLD_FOR_MS  how long holding lasts (default 4000)
 * If NAVI_BG_HOLD_AT_MS is unset the interposer only observes and never alters.
 *
 * Build:
 *   zig cc -target x86_64-linux-gnu.2.25 -shared -fPIC -O2 -Wall -Wextra -Werror \
 *       -o navi-bg-0x0.so navi_bg_0x0.c
 */

#define _GNU_SOURCE

#include <dlfcn.h>
#include <stdarg.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

typedef struct wl_surface wl_surface;
typedef struct wl_buffer wl_buffer;

typedef void (*attach_fn)(wl_surface *, wl_buffer *, int, int);

static attach_fn real_attach;
static wl_surface *target_surface;
static int is_navi = -1;
static long hold_after_attaches = -1;
static long hold_count = 600;
static struct timespec started;
static int have_start;
static int announced_load;
static int announced_hold;
static int announced_release;
static unsigned int suppressed;
/* Per-surface attach accounting, so a run that never touches a surface is
 * distinguishable from one that simply missed the hold window. */
#define MAX_SURFACES 6
static struct { wl_surface *s; unsigned int n; } seen[MAX_SURFACES];
static int nseen;
static unsigned int total_attaches;
static int announced_exit;
static unsigned int attaches;
static long first_attach_ms = -1;

/*
 * Report to the kernel log as well as stderr. The serial console captures dmesg,
 * so this channel survives any decision about where a child's stderr is routed,
 * and it does not depend on a writable directory.
 */
static void kmsg(const char *fmt, ...)
{
    char buf[256];
    va_list ap;
    int fd;
    int n;

    va_start(ap, fmt);
    n = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (n > 0) {
        fd = open("/dev/kmsg", O_WRONLY);
        if (fd >= 0) {
            ssize_t ignored = write(fd, buf, (size_t)n);
            (void)ignored;
            close(fd);
        }
        fprintf(stderr, "%s\n", buf);
        fflush(stderr);
    }
}

static long now_ms(void)
{
    struct timespec ts;

    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long)ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

/* True only inside the authentic AppNavi process. */
static int navi_process(void)
{
    char buf[300];
    int fd;
    ssize_t n;

    if (is_navi >= 0) {
        return is_navi;
    }
    is_navi = 0;
    fd = open("/proc/self/cmdline", O_RDONLY);
    if (fd < 0) {
        return is_navi;
    }
    n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n > 0) {
        buf[n] = '\0';
        if (strstr(buf, "AppNavi") != NULL) {
            is_navi = 1;
        }
    }
    return is_navi;
}

__attribute__((constructor)) static void on_load(void)
{
    const char *env;

    if (!navi_process()) {
        return;
    }
    clock_gettime(CLOCK_MONOTONIC, &started);
    have_start = 1;
    env = getenv("NAVI_BG_HOLD_AFTER");
    if (env != NULL && env[0] != '\0') {
        hold_after_attaches = strtol(env, NULL, 10);
    }
    env = getenv("NAVI_BG_HOLD_COUNT");
    if (env != NULL && env[0] != '\0') {
        hold_count = strtol(env, NULL, 10);
    }
    kmsg("navi-bg: loaded pid=%d hold_after=%ld hold_count=%ld",
         (int)getpid(), hold_after_attaches, hold_count);
    announced_load = 1;
}

__attribute__((destructor)) static void on_unload(void)
{
    int k;

    if (!navi_process() || announced_exit) {
        return;
    }
    announced_exit = 1;
    kmsg("navi-bg: summary pid=%d attaches=%u surfaces=%d suppressed=%u",
         (int)getpid(), total_attaches, nseen, suppressed);
    for (k = 0; k < nseen; k++) {
        kmsg("navi-bg: surface#%d attaches=%u", k, seen[k].n);
    }
}

void wl_surface_attach(wl_surface *surface, wl_buffer *buffer, int x, int y)
{
    long elapsed;
    int holding;

    if (real_attach == NULL) {
        real_attach = (attach_fn)dlsym(RTLD_NEXT, "wl_surface_attach");
        if (real_attach == NULL) {
            return;
        }
    }
    if (!navi_process()) {
        real_attach(surface, buffer, x, y);
        return;
    }
    if (target_surface == NULL) {
        target_surface = surface;
    }

    /* Account for every surface before the target filter, so the summary shows
     * whether the client attached anything at all. */
    {
        int k, found = -1;
        for (k = 0; k < nseen; k++) {
            if (seen[k].s == surface) {
                found = k;
                break;
            }
        }
        if (found < 0 && nseen < MAX_SURFACES) {
            seen[nseen].s = surface;
            seen[nseen].n = 0;
            found = nseen++;
            kmsg("navi-bg: surface#%d first attach at_ms=%ld",
                 found, have_start ? now_ms() - (started.tv_sec * 1000L +
                 started.tv_nsec / 1000000L) : 0L);
        }
        if (found >= 0) {
            seen[found].n++;
        }
        total_attaches++;
    }

    if (surface != target_surface) {
        real_attach(surface, buffer, x, y);
        return;
    }

    attaches++;
    elapsed = have_start ? now_ms() - (started.tv_sec * 1000L + started.tv_nsec / 1000000L) : 0;
    if (first_attach_ms < 0) {
        first_attach_ms = elapsed;
        kmsg("navi-bg: first-attach at_ms=%ld", elapsed);
    }

    holding = hold_after_attaches >= 0 &&
              attaches > (unsigned long)hold_after_attaches &&
              suppressed < (unsigned long)hold_count;

    if (holding && !announced_hold) {
        announced_hold = 1;
        kmsg("navi-bg: hold-begin at_ms=%ld attaches=%u", elapsed, attaches);
    }
    if (!holding && announced_hold && !announced_release) {
        announced_release = 1;
        kmsg("navi-bg: hold-end at_ms=%ld suppressed=%u", elapsed, suppressed);
    }

    if (holding) {
        suppressed++;
        real_attach(surface, NULL, 0, 0);
        return;
    }
    real_attach(surface, buffer, x, y);
}
