/*
 * navi_bg_0x0.c — observe AppNavi surface attaches and optionally hold them.
 *
 * ApplicationManager's navigation window byte is latched through a background
 * (BG) window notification, and the IVI compositor classifies a surface as BG
 * only when both dimensions are non-positive. The retained full-chain evidence
 * does not yet show whether AppNavi's genuine hide path reaches a zero-size
 * configure; this interposer records bounded null-attach and following-commit
 * observations to help inspect that lifecycle in the VM.
 *
 * A single null-buffer attach is not enough. In weston_surface_commit_state the
 * size block at 0x40f470 stores the previous `width_from_buffer` before the
 * null-buffer branch at 0x40f813 zeroes that field, so the first null attach keeps
 * the old positive size. A second null attach enters the same block with the field
 * already zero and therefore stores 0x0.
 *
 * This version deliberately uses no filesystem. Load and timeline messages go to
 * stderr and /dev/kmsg so a run can distinguish "not loaded" from a denied log
 * path. Null attaches and commits immediately following them are logged with a
 * cap of 32 each. The optional hold is driven by
 * target-surface attach count, not elapsed time; the monotonic clock is for logs.
 *
 * Environment:
 *   NAVI_BG_HOLD_AFTER  target-surface attach count to allow before holding
 *   NAVI_BG_HOLD_COUNT  subsequent target-surface attaches to suppress (default 600)
 * If NAVI_BG_HOLD_AFTER is unset, every attach is forwarded unchanged.
 * The first surface passed to wl_surface_attach is the hold target.
 *
 * Commit observation has two hook points. The legacy one wraps the exported
 * wl_surface_attach/wl_surface_commit symbols, which only clients built against
 * old libwayland versions call: in this vendor library (1.10, 0.3.0) those two
 * are header inlines and have no symbol at all, verified in the guest. The hook
 * that actually fires wraps wl_proxy_marshal, decodes the call from the
 * interface's own signature, and forwards once through wl_proxy_marshal_array.
 * Both wrappers resolve their successor with dlsym(RTLD_NEXT, ...) and compare it
 * with the global-scope definition: they differ only when this object precedes
 * the real library, so that comparison is the interposition proof.
 *
 * The marshaller wrapper never drops a request. Everything a message can carry is
 * decoded ('i','u','f','s','o','n','a','h', plus the '?' nullable prefix) and
 * forwarded once through wl_proxy_marshal_array; when a signature cannot be read,
 * the raw arguments go straight to the next wl_proxy_marshal instead, with a
 * bounded `undecoded-opcode ... forwarded=1` line. Observation is best-effort,
 * forwarding is not: a client's request must never be lost to the instrument.
 * The unload
 * verdict reports `observed` only when the proof held and at least one commit was
 * counted, `shadowed` when another object precedes this one, `unverified` when the
 * wrapper never ran inside a process that did attach, and `idle` when the client
 * produced no traffic. Read `unverified` as "commits were not observed", never as
 * "no commit happened", and never let a hold decision rest on it.
 *
 * Build:
 *   zig cc -target x86_64-linux-gnu.2.25 -shared -fPIC -O2 -Wall -Wextra -Werror \
 *       -o navi-bg-0x0.so navi_bg_0x0.c
 */

#define _GNU_SOURCE

#include <dlfcn.h>
#include <stdarg.h>
#include <stdint.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

typedef struct wl_surface wl_surface;
typedef struct wl_buffer wl_buffer;

typedef void (*attach_fn)(wl_surface *, wl_buffer *, int, int);
typedef void (*commit_fn)(wl_surface *);

static attach_fn real_attach;
static commit_fn real_commit;
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
/* Per-surface accounting; log caps keep kernel/stderr output bounded. */
#define MAX_SURFACES 6
#define MAX_NULL_ATTACH_LOGS 32
#define MAX_NULL_COMMIT_LOGS 32
#define MAX_UNDECODED_LOGS 4
static unsigned int undecoded_calls;
static struct {
    wl_surface *s;
    unsigned int attaches;
    unsigned int null_attaches;
    unsigned int commits_after_null;
    int awaiting_null_commit;
    int last_null_was_forced;
} seen[MAX_SURFACES];
static int nseen;
static unsigned int total_attaches;
static unsigned int total_commits;
/* Interposition proof, reported as a verdict by on_unload. */
static int wrapper_entered;   /* the commit wrapper ran at least once */
static int interposed;        /* 1: this object precedes the real definition */
static unsigned int total_null_attaches;
static unsigned int total_commits_after_null;
static unsigned int null_attach_logs;
static unsigned int null_commit_logs;
static int announced_exit;
static unsigned int attaches;
static long first_attach_ms = -1;

/*
 * Report to the kernel log as well as stderr. The serial console captures dmesg,
 * so this channel survives any decision about where a child's stderr is routed,
 * and it does not depend on a writable directory. Local mock tests define
 * NAVI_BG_DISABLE_KMSG to avoid writing to the host kernel log.
 */
static const char *log_path;
/* AppNavi by default; NAVI_BG_CLIENT_MATCH lets a harness exercise the same
 * observation against another vendor Wayland client without renaming it. */
static const char *client_match = "AppNavi";

static void kmsg(const char *fmt, ...)
{
    char buf[256];
    va_list ap;
    int n;

    va_start(ap, fmt);
    n = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (n > 0) {
#ifndef NAVI_BG_DISABLE_KMSG
        int fd = open("/dev/kmsg", O_WRONLY);
          if (fd >= 0) {
            ssize_t ignored = write(fd, buf, (size_t)n);
            (void)ignored;
              close(fd);
        }
#endif
        /* A sandboxed client can be non-root with stderr discarded: /dev/kmsg is
         * then closed to it and this file is the only channel left. Nothing is
         * written unless the launcher opts in. */
        if (log_path != NULL) {
            int fd = open(log_path, O_WRONLY | O_CREAT | O_APPEND, 0644);
            if (fd >= 0) {
                ssize_t ignored = write(fd, buf, (size_t)n);
                (void)ignored;
                close(fd);
            }
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

static long elapsed_ms(void)
{
    return have_start ? now_ms() - (started.tv_sec * 1000L +
           started.tv_nsec / 1000000L) : 0L;
}

static int surface_index(wl_surface *surface)
{
    int k;

    for (k = 0; k < nseen; k++) {
        if (seen[k].s == surface) {
            return k;
        }
    }
    if (nseen >= MAX_SURFACES) {
        return -1;
    }
    k = nseen++;
    seen[k].s = surface;
    seen[k].attaches = 0;
    seen[k].null_attaches = 0;
    seen[k].commits_after_null = 0;
    seen[k].awaiting_null_commit = 0;
    seen[k].last_null_was_forced = 0;
    kmsg("navi-bg: surface#%d first observed at_ms=%ld", k, elapsed_ms());
    return k;
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
        if (client_match != NULL && client_match[0] != '\0'
            && strstr(buf, client_match) != NULL) {
            is_navi = 1;
        }
    }
    return is_navi;
}

__attribute__((constructor)) static void on_load(void)
{
    const char *match;
    const char *env;

    /* Environment first: navi_process() caches its answer, so the client
     * selector has to be in place before the first lookup. */
    log_path = getenv("NAVI_BG_LOG_FILE");
    if (log_path != NULL && log_path[0] == '\0') {
        log_path = NULL;
    }
    match = getenv("NAVI_BG_CLIENT_MATCH");
    if (match != NULL && match[0] != '\0') {
        client_match = match;
    }
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
    const char *verdict;
    int complete = 0;
    int k;

    if (!navi_process() || announced_exit) {
        return;
    }
    announced_exit = 1;
    if (wrapper_entered && interposed == 1) {
        verdict = "observed";
        complete = 1;
    } else if (wrapper_entered) {
        verdict = "shadowed";
    } else if (total_attaches > 0) {
        verdict = "unverified";
    } else {
        verdict = "idle";
    }
    kmsg("navi-bg: observation verdict=%s commits=%u interposed=%d complete=%d",
         verdict, total_commits, interposed, complete);
    kmsg("navi-bg: summary pid=%d attaches=%u commits=%u null_attaches=%u "
         "commits_after_null=%u surfaces=%d suppressed=%u",
         (int)getpid(), total_attaches, total_commits, total_null_attaches,
         total_commits_after_null, nseen, suppressed);
    for (k = 0; k < nseen; k++) {
        kmsg("navi-bg: surface#%d attaches=%u null_attaches=%u "
             "commits_after_null=%u pending_null_commit=%d forced=%d",
             k, seen[k].attaches, seen[k].null_attaches,
             seen[k].commits_after_null, seen[k].awaiting_null_commit,
             seen[k].last_null_was_forced);
    }
}

/* Observation core shared by both entry points: the exported wl_surface_* symbols
 * that old clients link against, and the wl_proxy_marshal ABI that this vendor
 * library actually exports (wl_surface_attach/commit are header inlines there, so
 * they are not symbols at all). The core reports what to forward. */
struct forwarded {
    wl_buffer *buffer;
    int x;
    int y;
};

static void observe_attach(wl_surface *surface, wl_buffer *buffer, int x, int y,
                           struct forwarded *out)
{
    long elapsed;
    int holding;
    int index;

    out->buffer = buffer;
    out->x = x;
    out->y = y;
    if (target_surface == NULL) {
        target_surface = surface;
    }

    index = surface_index(surface);
    if (index >= 0) {
        seen[index].attaches++;
    }
    total_attaches++;
    if (buffer == NULL) {
        total_null_attaches++;
        if (index >= 0) {
            seen[index].null_attaches++;
            seen[index].awaiting_null_commit = 1;
            seen[index].last_null_was_forced = 0;
        }
        if (null_attach_logs < MAX_NULL_ATTACH_LOGS) {
            null_attach_logs++;
            kmsg("navi-bg: null-attach surface#%d target=%d x=%d y=%d "
                 "attach=%u at_ms=%ld", index, surface == target_surface,
                 x, y, total_attaches, elapsed_ms());
        }
    }

    if (surface != target_surface) {
        return;
    }

    attaches++;
    elapsed = elapsed_ms();
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
        if (index >= 0) {
            seen[index].awaiting_null_commit = 1;
            seen[index].last_null_was_forced = buffer != NULL;
        }
        out->buffer = NULL;
        out->x = 0;
        out->y = 0;
    }
}

static void observe_commit(wl_surface *surface)
{
    int index;

    total_commits++;
    index = surface_index(surface);
    if (index >= 0 && seen[index].awaiting_null_commit) {
        seen[index].awaiting_null_commit = 0;
        seen[index].commits_after_null++;
        total_commits_after_null++;
        if (null_commit_logs < MAX_NULL_COMMIT_LOGS) {
            null_commit_logs++;
            kmsg("navi-bg: commit-after-null-attach surface#%d forced=%d "
                 "commit=%u at_ms=%ld", index,
                 seen[index].last_null_was_forced, total_commits,
                 elapsed_ms());
        }
    }
}

/* Legacy entry points: real symbols only in old libwayland versions. */
void wl_surface_attach(wl_surface *surface, wl_buffer *buffer, int x, int y)
{
    struct forwarded out;

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
    observe_attach(surface, buffer, x, y, &out);
    real_attach(surface, out.buffer, out.x, out.y);
}

void wl_surface_commit(wl_surface *surface)
{
    if (real_commit == NULL) {
        void *global;

        real_commit = (commit_fn)dlsym(RTLD_NEXT, "wl_surface_commit");
        if (real_commit == NULL) {
            return;
        }
        /* Only a different global-scope definition proves this object is first. */
        global = dlsym(RTLD_DEFAULT, "wl_surface_commit");
        interposed = (global != NULL && global != (void *)real_commit) ? 1 : -1;
        kmsg("navi-bg: commit global=%p next=%p interposed=%d",
             global, (void *)real_commit, interposed);
    }
    wrapper_entered = 1;
    if (!navi_process()) {
        real_commit(surface);
        return;
    }
    observe_commit(surface);
    real_commit(surface);
}

/* --- the ABI this vendor library actually exports ------------------------- */

union marshal_argument {
    int32_t i;
    uint32_t u;
    int32_t f;
    const char *s;
    void *o;
    uint32_t n;
    void *a;
    int32_t h;
};

typedef void (*marshal_fn)(void *proxy, uint32_t opcode, ...);
typedef void (*marshal_array_fn)(void *proxy, uint32_t opcode,
                                 union marshal_argument *args);
typedef const char *(*class_fn)(void *proxy);

#define SURFACE_ATTACH 1u
#define SURFACE_COMMIT 6u

static marshal_array_fn real_marshal_array;
static marshal_fn real_marshal;
static class_fn proxy_class;

/* The message signature lives in the interface table, so the varargs can be read
 * exactly rather than guessed, then forwarded once through the array entry. */
#define MAX_MARSHAL_ARGS 32

static int read_arguments(const char *signature, va_list source,
                          union marshal_argument *args)
{
    int count = 0;

    for (const char *p = signature; p != NULL && *p != '\0'; p++) {
        if (count >= MAX_MARSHAL_ARGS) {
            return -1;
        }
        switch (*p) {
        case '?':
            continue;
        case 'i':
            args[count++].i = va_arg(source, int32_t);
            break;
        case 'u':
            args[count++].u = va_arg(source, uint32_t);
            break;
        case 'f':
            /* |'f'| is wl_fixed_t: a 24.8 fixed-point *integer*, not a C float, so it
             * travels in an integer slot like 'i' and no promotion happens. */
            args[count++].f = va_arg(source, int32_t);
            break;
        case 's':
            args[count++].s = va_arg(source, const char *);
            break;
        case 'o':
            args[count++].o = va_arg(source, void *);
            break;
        case 'n':
            args[count++].n = va_arg(source, uint32_t);
            break;
        case 'a':
            args[count++].a = va_arg(source, void *);
            break;
        case 'h':
            args[count++].h = va_arg(source, int32_t);
            break;
        default:
            return -1;
        }
    }
    return count;
}

static int is_surface(void *proxy)
{
    const char *name;

    if (proxy_class == NULL) {
        proxy_class = (class_fn)dlsym(RTLD_NEXT, "wl_proxy_get_class");
        if (proxy_class == NULL) {
            return 0;
        }
    }
    name = proxy_class(proxy);
    return name != NULL && strcmp(name, "wl_surface") == 0;
}

static const char *interface_signature(void *proxy, uint32_t opcode);

/* Same proof as the legacy wrapper, for the ABI this library really exports. */
static void prove_marshal_interposition(void)
{
    void *global;
    void *next;

    if (interposed != 0) {
        return;
    }
    global = dlsym(RTLD_DEFAULT, "wl_proxy_marshal");
    next = dlsym(RTLD_NEXT, "wl_proxy_marshal");
    interposed = (global != NULL && next != NULL && global != next) ? 1 : -1;
    kmsg("navi-bg: marshal global=%p next=%p interposed=%d",
         global, next, interposed);
}

/* Last-resort pass-through. On this ABI every message argument occupies one
 * integer slot — |'f'| is fixed point, not a C float — and a message never carries
 * more than eight, so an unreadable signature is still forwarded instead of losing
 * the client's request: the callee consumes exactly its own signature's count and
 * ignores the rest. */
static void call_vararg(marshal_fn next_marshal, void *proxy, uint32_t opcode,
                        const intptr_t *slot)
{
    next_marshal(proxy, opcode, slot[0], slot[1], slot[2], slot[3],
                 slot[4], slot[5], slot[6], slot[7]);
}

static void forward_undecoded(void *proxy, uint32_t opcode, va_list source,
                              marshal_fn next_marshal)
{
    intptr_t slot[8];
    int k;

    for (k = 0; k < 8; k++) {
        slot[k] = va_arg(source, intptr_t);
    }
    call_vararg(next_marshal, proxy, opcode, slot);
}

/* Same pass-through from an already-decoded array: every message argument occupies
 * one integer slot, so the union's pointer-sized read reproduces the slot exactly. */
static void forward_arguments(void *proxy, uint32_t opcode,
                              union marshal_argument *args, int count,
                              marshal_fn next_marshal)
{
    intptr_t slot[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };
    int k;

    for (k = 0; k < count && k < 8; k++) {
        slot[k] = (intptr_t)args[k].o;
    }
    call_vararg(next_marshal, proxy, opcode, slot);
}

void wl_proxy_marshal(void *proxy, uint32_t opcode, ...)
{
    union marshal_argument args[MAX_MARSHAL_ARGS];
    struct forwarded out;
    va_list source;
    int surface_proxy;
    int count;
    const char *signature = NULL;

    if (real_marshal_array == NULL) {
        real_marshal_array = (marshal_array_fn)dlsym(RTLD_NEXT, "wl_proxy_marshal_array");
    }
    if (real_marshal == NULL) {
        real_marshal = (marshal_fn)dlsym(RTLD_NEXT, "wl_proxy_marshal");
    }
    if (real_marshal_array == NULL && real_marshal == NULL) {
        /* Being called at all means a client resolved this object, so the library
         * must be next in the chain and one of the two lookups succeeds. This is
         * unreachable in a real link, and nothing would be forwardable anyway. */
        return;
    }
    prove_marshal_interposition();
    /* is_surface() also performs the one-time class lookup the signature check
     * relies on, so it runs before any interface field is read. */
    surface_proxy = is_surface(proxy);
    signature = interface_signature(proxy, opcode);
    va_start(source, opcode);
    count = signature != NULL ? read_arguments(signature, source, args) : -1;
    if (count < 0 && real_marshal != NULL) {
        forward_undecoded(proxy, opcode, source, real_marshal);
        va_end(source);
        undecoded_calls++;
        if (undecoded_calls <= MAX_UNDECODED_LOGS) {
            kmsg("navi-bg: undecoded-opcode opcode=%u signature=%s forwarded=1",
                 opcode, signature != NULL ? signature : "(unreadable)");
        }
        return;
    }
    va_end(source);
    if (count < 0) {
        /* Only reachable when wl_proxy_marshal_array is absent from the library;
         * then the request cannot be rebuilt, so it is dropped with a loud line
         * instead of being sent with invented arguments. */
        undecoded_calls++;
        if (undecoded_calls <= MAX_UNDECODED_LOGS) {
            kmsg("navi-bg: undecoded-opcode opcode=%u signature=%s forwarded=0",
                 opcode, signature != NULL ? signature : "(unreadable)");
        }
        return;
    }

    if (navi_process() && surface_proxy && real_marshal_array != NULL) {
        wrapper_entered = 1;
        if (opcode == SURFACE_ATTACH && count >= 3) {
            observe_attach((wl_surface *)proxy, (wl_buffer *)args[0].o,
                           args[1].i, args[2].i, &out);
            args[0].o = out.buffer;
            args[1].i = out.x;
            args[2].i = out.y;
        } else if (opcode == SURFACE_COMMIT) {
            observe_commit((wl_surface *)proxy);
        }
    }
    if (real_marshal_array != NULL) {
        real_marshal_array(proxy, opcode, args);
        return;
    }
    /* No array entry to rebuild through: replay the already-decoded arguments
     * through the vararg entry so the request still arrives. Holding is skipped,
     * because the arguments cannot be marked up here. */
    forward_arguments(proxy, opcode, args, count, real_marshal);
}

/* interface sits at offset 0 of this library's proxies (legacy wl_object first),
 * and the interface's own name is checked against wl_proxy_get_class() so a
 * different layout can never be read as a signature. */
static const char *interface_signature(void *proxy, uint32_t opcode)
{
    struct message_layout {
        const char *name;
        const char *signature;
        const void *types;
    };
    struct interface_layout {
        const char *name;
        int version;
        int method_count;
        const struct message_layout *methods;
        int event_count;
        const struct message_layout *events;
    };
    const struct interface_layout *iface = *(const struct interface_layout *const *)proxy;
    const char *class_name;

    if (iface == NULL || iface->name == NULL || iface->methods == NULL) {
        return NULL;
    }
    class_name = proxy_class != NULL ? proxy_class(proxy) : NULL;
    if (class_name == NULL || strcmp(class_name, iface->name) != 0) {
        return NULL;
    }
    if (opcode >= (uint32_t)iface->method_count) {
        return NULL;
    }
    return iface->methods[opcode].signature;
}
