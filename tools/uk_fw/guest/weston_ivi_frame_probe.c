/* VM-only, opt-in diagnostic for the pinned Gen5W Weston/pixman build.
 *
 * The two image copies happen in one post-composition callback.  Source bytes
 * are client-owned shared memory: the Wayland busy buffer contract requires
 * a compliant client not to change them while the compositor holds the buffer.
 * This is not a proof against a client that violates that contract, nor proof
 * that any particular screen is visible or that the two copies are atomic.
 * No compositor pixel-copy helper is used: the retained implementation of
 * those helpers changes pixman image transforms.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <sys/stat.h>
#include <dlfcn.h>

struct wl_list { struct wl_list *prev, *next; };
struct wl_listener { struct wl_list link; void (*notify)(struct wl_listener *, void *); };
struct wl_display; struct wl_event_loop; struct wl_event_source;
struct wl_resource; struct wl_client; struct wl_shm_buffer;
struct weston_compositor; struct weston_output; struct weston_surface;
struct ivi_layout_surface; struct pixman_image;
extern void wl_list_insert(struct wl_list *, struct wl_list *);
extern void wl_list_remove(struct wl_list *);
extern struct wl_event_loop *wl_display_get_event_loop(struct wl_display *);
extern struct wl_event_source *wl_event_loop_add_timer(struct wl_event_loop *, int (*)(void *), void *);
extern int wl_event_source_timer_update(struct wl_event_source *, int);
extern struct wl_client *wl_resource_get_client(struct wl_resource *);
extern void wl_client_get_credentials(struct wl_client *, int *, unsigned int *, unsigned int *);
extern struct wl_shm_buffer *wl_shm_buffer_get(struct wl_resource *);
extern void wl_shm_buffer_begin_access(struct wl_shm_buffer *);
extern void wl_shm_buffer_end_access(struct wl_shm_buffer *);
extern void *wl_shm_buffer_get_data(struct wl_shm_buffer *);
extern int32_t wl_shm_buffer_get_width(struct wl_shm_buffer *);
extern int32_t wl_shm_buffer_get_height(struct wl_shm_buffer *);
extern int32_t wl_shm_buffer_get_stride(struct wl_shm_buffer *);
extern uint32_t wl_shm_buffer_get_format(struct wl_shm_buffer *);
extern uint32_t *pixman_image_get_data(struct pixman_image *);
extern int pixman_image_get_width(struct pixman_image *);
extern int pixman_image_get_height(struct pixman_image *);
extern int pixman_image_get_stride(struct pixman_image *);
extern uint32_t pixman_image_get_format(struct pixman_image *);
extern void weston_output_schedule_repaint(struct weston_output *);

/* Exact vendor DWARF offsets. The launcher verifies the executable, shell and
 * pixman hashes before the optional module is loaded. */
#define DISPLAY 0x10u
#define OUTPUT_LIST 0x1e8u
#define OUTPUT_LINK 0x18u
#define OUTPUT_STATE 0x10u
#define OUTPUT_FRAME 0x200u
#define OUTPUT_DESTROY 0x210u
#define COMPOSITOR_RENDERER 0x310u
#define SURFACE_RESOURCE 0x00u
#define SURFACE_RENDERER 0x78u
#define PS_IMAGE 0x08u
#define PS_BUFFER 0x10u
#define WB_RESOURCE 0x00u
#define WB_SHM 0x30u
#define WB_BUSY 0x40u
#define PO_HW_IMAGE 0x10u
#ifndef PROBE_DIR
#define PROBE_DIR "/tmp/vm-ivi-frame-probe"
#endif
#define MAX_BYTES (8u * 1024u * 1024u)
#define VM_PROBE_LEGACY_WINDOW_MS 10000ull
/* Match the largest host-generated foreground window. The regular profile
 * emits 29,999 ms and the WSL1 slow-TCG profile emits 59,999 ms. */
#define VM_PROBE_FOREGROUND_WINDOW_MS 59999ull
#define ACCESS(ptr, offset, type) (*(type *)((unsigned char *)(ptr) + (offset)))

typedef uint32_t (*id_fn)(struct ivi_layout_surface *);
typedef struct ivi_layout_surface *(*lookup_fn)(uint32_t);
typedef struct weston_surface *(*surface_fn)(struct ivi_layout_surface *);
typedef const void *(*properties_fn)(struct ivi_layout_surface *);
typedef int (*notify_add_fn)(void (*)(struct ivi_layout_surface *, void *), void *);
/* FAIL-only numeric codes occupy otherwise unused receipt geometry fields.
 * Keep 0 as unknown; do not infer which condition failed in compound checks. */
enum vm_probe_failure {
    VM_PROBE_UNKNOWN = 0, VM_PROBE_TIMEOUT = 1, VM_PROBE_OUTPUT_GONE = 2,
    VM_PROBE_EPOCH_CHANGED = 3, VM_PROBE_CLOCK = 4, VM_PROBE_GO_INVALID = 5,
    VM_PROBE_BASELINE_IO = 6, VM_PROBE_OWNER_CHANGED = 7,
    VM_PROBE_FRAME_CHECK = 8, VM_PROBE_OUTPUT_IO = 9, VM_PROBE_INITIAL_LAYOUT = 10
};
struct vm_probe {
    struct weston_compositor *compositor;
    struct wl_event_source *timer;
    struct wl_listener frame, output_destroy;
    struct weston_output *output;
    struct ivi_layout_surface *layout;
    struct weston_surface *surface;
    uintptr_t weston_base;
    uintptr_t captured_surface, captured_output;
    id_fn id; lookup_fn lookup; surface_fn surface_get; properties_fn properties;
    unsigned long epoch, armed_epoch, sequence;
    int armed, copied, failed, expected_pid;
    int foreground, baseline_ready, baseline_published, observe, observations;
    unsigned int fail_code, frame_callbacks, unchanged_comparisons;
    unsigned long long fail_elapsed_ms;
    unsigned long long expected_start, deadline_ms, captured_ms, request_epoch_ms;
    unsigned long long baseline_ms, observation_start_ms, last_observation_ms;
    char nonce[33];
    unsigned char *source_copy, *output_copy, *baseline;
    size_t source_size, output_size;
    size_t baseline_size;
    int baseline_width, baseline_height;
    uint32_t baseline_format;
    uint32_t baseline_output_format;
    int32_t baseline_geometry[4], baseline_output_x, baseline_output_y;
    uintptr_t baseline_buffer, selected_buffer;
    struct wl_resource *baseline_resource;
    struct wl_client *baseline_client;
    char baseline_hash[65], ack_hash[65];
    int source_width, source_height, output_width, output_height;
    int32_t geometry[4], output_x, output_y;
    uint32_t source_format, output_format;
};
static struct vm_probe vm_probe_state;

static unsigned long long vm_probe_now(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts)) return 0;
    return (unsigned long long)ts.tv_sec * 1000u + (unsigned long long)ts.tv_nsec / 1000000u;
}

/* Set the first observed failure once. Zero elapsed means unavailable or less
 * than one millisecond; it is not a claim about a successful clock sample. */
static void vm_probe_fail(struct vm_probe *p, unsigned int code)
{
    unsigned long long now;
    if (!p->failed) {
        p->fail_code = code;
        now = vm_probe_now();
        if (now && p->request_epoch_ms && now >= p->request_epoch_ms)
            p->fail_elapsed_ms = now - p->request_epoch_ms;
    }
    p->armed = 0;
    p->failed = 1;
}

#ifndef VM_PROBE_TEST
static unsigned long long vm_probe_starttime(int pid)
{
    char path[64], buf[2048], *p, *end;
    FILE *f; int field;
    if (pid <= 0 || snprintf(path, sizeof path, "/proc/%d/stat", pid) >= (int)sizeof path) return 0;
    f = fopen(path, "r");
    if (!f) return 0;
    p = fgets(buf, sizeof buf, f); fclose(f);
    if (!p || !strchr(buf, '\n') || !(p = strrchr(buf, ')')) || p[1] != ' ') return 0;
    p += 2;
    for (field = 3; field < 22; field++) {
        p = strchr(p, ' '); if (!p) return 0;
        while (*p == ' ') p++;
    }
    errno = 0;
    { unsigned long long n = strtoull(p, &end, 10);
      return errno || end == p || (*end != ' ' && *end != '\n') ? 0 : n; }
}
#else
extern unsigned long long vm_probe_starttime(int pid);
#endif

static int vm_probe_nonce(const char *s)
{
    size_t i;
    if (strlen(s) != 32) return 0;
    for (i = 0; i < 32; i++) if (!((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'a' && s[i] <= 'f'))) return 0;
    return 1;
}

static int vm_probe_dimensions(int width, int height, int stride, uint32_t format, size_t *size)
{
    size_t row;
    if (width <= 0 || height <= 0 || width > 4096 || height > 2160 || stride <= 0 || (format >> 24) != 32) return 0;
    row = (size_t)width * 4u;
    if ((size_t)stride < row || (size_t)stride > MAX_BYTES || row > MAX_BYTES / (size_t)height) return 0;
    *size = row * (size_t)height;
    return 1;
}

/* Legacy standalone requests have three fields; foreground requests add the
 * guest monotonic acquisition epoch and the original strict deadline. */
static int vm_probe_request(struct vm_probe *p, const char *command, unsigned long long now)
{
    unsigned long long epoch = 0, deadline = 0; int used = 0;
    int count = sscanf(command, "%32s %d %llu %llu %llu %n", p->nonce, &p->expected_pid,
                       &p->expected_start, &epoch, &deadline, &used);
    if (count != 5) {
        used = 0;
        count = sscanf(command, "%32s %d %llu %n", p->nonce, &p->expected_pid, &p->expected_start, &used);
    }
    if (!used || command[used] || (count != 3 && count != 5) || !vm_probe_nonce(p->nonce) || p->expected_pid <= 0 ||
        !p->expected_start || !now || vm_probe_starttime(p->expected_pid) != p->expected_start) return 0;
    if (count == 3) { epoch = now; deadline = now + VM_PROBE_LEGACY_WINDOW_MS; }
    if (!epoch || epoch > now || deadline <= now || deadline <= epoch ||
        deadline - epoch > (count == 3 ? VM_PROBE_LEGACY_WINDOW_MS : VM_PROBE_FOREGROUND_WINDOW_MS)) return 0;
    p->request_epoch_ms = epoch; p->deadline_ms = deadline;
    p->foreground = count == 5;
    return 1;
}

static void vm_probe_surface_event(struct ivi_layout_surface *surface, void *userdata)
{
    struct vm_probe *p = userdata;
    if (surface == p->layout || (surface && p->id(surface) == 1000)) p->epoch++;
}

static void vm_probe_output_destroy(struct wl_listener *listener, void *data)
{
    struct vm_probe *p = &vm_probe_state; (void)listener; (void)data;
    wl_list_remove(&p->frame.link); wl_list_remove(&p->output_destroy.link);
    p->output = NULL; p->epoch++;
}

/* Neither copy dispatches the event loop.  Lifecycle notifications and owner
 * rechecks therefore bind both private copies to one compositor callback. */
static void vm_probe_frame(struct wl_listener *listener, void *data)
{
    struct vm_probe *p = &vm_probe_state;
    struct weston_surface *s; struct wl_resource *resource, *buf_resource;
    struct wl_client *client; struct wl_shm_buffer *shm;
    struct pixman_image *src, *dst; void *ps, *buffer, *os, *renderer, *src_data, *dst_data; const void *props;
    int32_t geometry[4], output_x, output_y;
    int pid = -1, sw, sh, ss, ow, oh, os_stride, row; unsigned int uid, gid;
    uint32_t sf, of, shm_format; size_t sn, on; unsigned long long now; int changed = 1;
    unsigned int failure = VM_PROBE_FRAME_CHECK;
    (void)listener;
    if (!p->armed || data != p->output) return;
    if (p->foreground && p->baseline_ready && !p->observe) return;
    /* The foreground counter describes callbacks after go was accepted;
     * its mandatory baseline callback is not part of that observation. */
    if ((!p->foreground || p->observe) && p->frame_callbacks < 1000000u) p->frame_callbacks++;
    now = vm_probe_now();
    if (p->foreground && p->baseline_ready && now && now < p->observation_start_ms) goto bad;
    if (p->foreground && p->baseline_ready && now && p->last_observation_ms && now >= p->last_observation_ms && now - p->last_observation_ms < 100) return;
    if (p->foreground && p->baseline_ready) { if (p->observations >= 100) goto bad; p->observations++; p->last_observation_ms = now; }
    p->armed = 0;
    if (!now || now < p->request_epoch_ms) { failure = VM_PROBE_CLOCK; goto bad; }
    if (now >= p->deadline_ms) { failure = VM_PROBE_TIMEOUT; goto bad; }
    if (p->epoch != p->armed_epoch) { failure = VM_PROBE_EPOCH_CHANGED; goto bad; }
    if (p->lookup(1000) != p->layout ||
        !p->layout || p->id(p->layout) != 1000 || !(s = p->surface_get(p->layout)) || s != p->surface) goto bad;
    props = p->properties(p->layout);
    if (!props) goto bad;
    memcpy(geometry, (const unsigned char *)props + 0x24, sizeof geometry);
    output_x = ACCESS(p->output, 0xe0, int32_t); output_y = ACCESS(p->output, 0xe4, int32_t);
    resource = ACCESS(s, SURFACE_RESOURCE, struct wl_resource *);
    client = resource ? wl_resource_get_client(resource) : NULL;
    if (!client) goto bad;
    wl_client_get_credentials(client, &pid, &uid, &gid);
    if (pid != p->expected_pid || vm_probe_starttime(pid) != p->expected_start) { failure = VM_PROBE_OWNER_CHANGED; goto bad; }
    if (p->baseline_ready && (resource != p->baseline_resource || client != p->baseline_client)) goto bad;
    renderer = ACCESS(p->compositor, COMPOSITOR_RENDERER, void *);
    if (!renderer || ACCESS(renderer, 0, uintptr_t) != p->weston_base + 0x21370u) goto bad;
    ps = ACCESS(s, SURFACE_RENDERER, void *);
    if (!ps || !(src = ACCESS(ps, PS_IMAGE, struct pixman_image *)) || !(buffer = ACCESS(ps, PS_BUFFER, void *)) ||
        ACCESS(buffer, WB_BUSY, uint32_t) == 0 || !(buf_resource = ACCESS(buffer, WB_RESOURCE, struct wl_resource *)) ||
        wl_resource_get_client(buf_resource) != client || !(shm = wl_shm_buffer_get(buf_resource)) ||
        shm != ACCESS(buffer, WB_SHM, struct wl_shm_buffer *)) goto bad;
    os = ACCESS(p->output, OUTPUT_STATE, void *);
    if (!os || !(dst = ACCESS(os, PO_HW_IMAGE, struct pixman_image *))) goto bad;
    sw = pixman_image_get_width(src); sh = pixman_image_get_height(src); ss = pixman_image_get_stride(src);
    sf = pixman_image_get_format(src); src_data = pixman_image_get_data(src);
    ow = pixman_image_get_width(dst); oh = pixman_image_get_height(dst); os_stride = pixman_image_get_stride(dst);
    of = pixman_image_get_format(dst); dst_data = pixman_image_get_data(dst);
    shm_format = wl_shm_buffer_get_format(shm);
    if ((shm_format != 0 && shm_format != 1) ||
        sf != (shm_format == 0 ? 0x20028888u : 0x20020888u) ||
        (of != 0x20020888u && of != 0x20028888u) || ow != 1920 || oh != 720 || !src_data || !dst_data ||
        src_data != wl_shm_buffer_get_data(shm) || sw != wl_shm_buffer_get_width(shm) ||
        sh != wl_shm_buffer_get_height(shm) || ss != wl_shm_buffer_get_stride(shm) ||
        !vm_probe_dimensions(sw, sh, ss, sf, &sn) || !vm_probe_dimensions(ow, oh, os_stride, of, &on)) goto bad;
    if (p->baseline_ready && (sw != p->baseline_width || sh != p->baseline_height || sf != p->baseline_format || sn != p->baseline_size)) goto bad;
    if (p->baseline_ready && (of != p->baseline_output_format || memcmp(geometry, p->baseline_geometry, sizeof geometry) ||
                              output_x != p->baseline_output_x || output_y != p->baseline_output_y)) goto bad;
    wl_shm_buffer_begin_access(shm);
    if (p->foreground && p->baseline_ready) {
        changed = 0;
        for (row = 0; row < sh; row++) if (memcmp(p->baseline + (size_t)row * sw * 4u,
                (unsigned char *)src_data + (size_t)row * ss, (size_t)sw * 4u)) { changed = 1; break; }
        if (!changed && p->unchanged_comparisons < 1000000u) p->unchanged_comparisons++;
    }
    if (!p->foreground || !p->baseline_ready || changed) {
        p->source_copy = malloc(sn);
        if (!p->source_copy) { wl_shm_buffer_end_access(shm); goto bad; }
        for (row = 0; row < sh; row++) memcpy(p->source_copy + (size_t)row * sw * 4u, (unsigned char *)src_data + (size_t)row * ss, (size_t)sw * 4u);
        for (row = 0; row < sh; row++) if (memcmp(p->source_copy + (size_t)row * sw * 4u, (unsigned char *)src_data + (size_t)row * ss, (size_t)sw * 4u)) {
            wl_shm_buffer_end_access(shm); goto bad;
        }
    }
    wl_shm_buffer_end_access(shm);
    if (!p->foreground || (p->baseline_ready && changed)) {
        p->output_copy = malloc(on);
        if (!p->output_copy) goto bad;
        for (row = 0; row < oh; row++) memcpy(p->output_copy + (size_t)row * ow * 4u, (unsigned char *)dst_data + (size_t)row * os_stride, (size_t)ow * 4u);
    }
    if (vm_probe_starttime(pid) != p->expected_start || p->epoch != p->armed_epoch || p->lookup(1000) != p->layout ||
        p->surface_get(p->layout) != s || p->properties(p->layout) != props ||
        memcmp(geometry, (const unsigned char *)props + 0x24, sizeof geometry) ||
        ACCESS(p->output, 0xe0, int32_t) != output_x || ACCESS(p->output, 0xe4, int32_t) != output_y ||
        ACCESS(s, SURFACE_RESOURCE, struct wl_resource *) != resource ||
        wl_resource_get_client(resource) != client || ACCESS(s, SURFACE_RENDERER, void *) != ps ||
        ACCESS(ps, PS_IMAGE, struct pixman_image *) != src || ACCESS(ps, PS_BUFFER, void *) != buffer ||
        ACCESS(buffer, WB_BUSY, uint32_t) == 0 || ACCESS(buffer, WB_RESOURCE, struct wl_resource *) != buf_resource ||
        wl_resource_get_client(buf_resource) != client || wl_shm_buffer_get(buf_resource) != shm ||
        ACCESS(buffer, WB_SHM, struct wl_shm_buffer *) != shm ||
        pixman_image_get_data(src) != src_data || wl_shm_buffer_get_data(shm) != src_data ||
        pixman_image_get_width(src) != sw || pixman_image_get_height(src) != sh || pixman_image_get_stride(src) != ss ||
        pixman_image_get_format(src) != sf || ACCESS(p->output, OUTPUT_STATE, void *) != os ||
        ACCESS(p->compositor, COMPOSITOR_RENDERER, void *) != renderer ||
        ACCESS(renderer, 0, uintptr_t) != p->weston_base + 0x21370u ||
        ACCESS(os, PO_HW_IMAGE, struct pixman_image *) != dst || pixman_image_get_data(dst) != dst_data ||
        pixman_image_get_width(dst) != ow || pixman_image_get_height(dst) != oh ||
        pixman_image_get_stride(dst) != os_stride || pixman_image_get_format(dst) != of ||
        !(now = vm_probe_now()) || now >= p->deadline_ms) goto bad;
    if (p->foreground && !p->baseline_ready) {
        p->baseline = p->source_copy; p->source_copy = NULL; p->baseline_size = sn;
        p->baseline_width = sw; p->baseline_height = sh; p->baseline_format = sf;
        p->baseline_output_format = of; memcpy(p->baseline_geometry, geometry, sizeof geometry);
        p->baseline_output_x = output_x; p->baseline_output_y = output_y;
        p->baseline_buffer = (uintptr_t)buffer; p->baseline_resource = resource; p->baseline_client = client;
        p->baseline_ms = now; p->baseline_ready = 1; p->armed = 1; return;
    }
    if (p->foreground && !changed) { free(p->source_copy); p->source_copy = NULL; p->armed = 1; return; }
    p->selected_buffer = (uintptr_t)buffer;
    p->source_size = sn; p->output_size = on; p->source_width = sw; p->source_height = sh;
    p->output_width = ow; p->output_height = oh; p->source_format = sf; p->output_format = of;
    memcpy(p->geometry, geometry, sizeof geometry); p->output_x = output_x; p->output_y = output_y;
    p->captured_surface = (uintptr_t)s; p->captured_output = (uintptr_t)p->output;
    p->captured_ms = now; p->sequence++; p->copied = 1; return;
bad:
    free(p->source_copy); free(p->output_copy); p->source_copy = p->output_copy = NULL; vm_probe_fail(p, failure);
}

static int vm_probe_write(int dirfd, const char *name, const void *data, size_t size)
{
    int fd = openat(dirfd, name, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600); size_t pos = 0;
    if (fd < 0) return -1;
    while (pos < size) { ssize_t n = write(fd, (const char *)data + pos, size - pos); if (n <= 0) { close(fd); (void)unlinkat(dirfd, name, 0); return -1; } pos += (size_t)n; }
    if (close(fd)) { (void)unlinkat(dirfd, name, 0); return -1; }
    return 0;
}

static int vm_probe_hash_text(const char *s)
{
    size_t i;
    if (strlen(s) != 64) return 0;
    for (i = 0; i < 64; i++) if (!((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'a' && s[i] <= 'f'))) return 0;
    return 1;
}

static int vm_probe_timer(void *data)
{
    struct vm_probe *p = data; struct wl_list *head; int dirfd, fd; char command[256], receipt[1024]; ssize_t n;
    dirfd = open(PROBE_DIR, O_RDONLY | O_DIRECTORY | O_NOFOLLOW);
    if (dirfd < 0) goto again;
    if (p->copied || p->failed) {
        int source_written = p->copied && vm_probe_write(dirfd, "source.raw", p->source_copy, p->source_size) == 0;
        int ok = source_written && vm_probe_write(dirfd, "output.raw", p->output_copy, p->output_size) == 0;
        if (!ok && p->copied) {
            if (source_written) (void)unlinkat(dirfd, "source.raw", 0);
            vm_probe_fail(p, VM_PROBE_OUTPUT_IO);
        }
        n = snprintf(receipt, sizeof receipt, "%s %s %d %llu %lu %llu %p %p %d %d %u %zu %d %d %u %zu %d %d %d %d %d %d",
                     p->nonce, ok ? "OK" : "FAIL", p->expected_pid, p->expected_start, p->sequence,
                     p->captured_ms, (void *)p->captured_surface, (void *)p->captured_output, p->source_width, p->source_height, p->source_format, p->source_size,
                     p->output_width, p->output_height, p->output_format, p->output_size,
                     ok ? p->geometry[0] : (int)p->fail_code,
                     ok ? p->geometry[1] : p->observe,
                     ok ? p->geometry[2] : (int)p->frame_callbacks,
                     ok ? p->geometry[3] : (int)p->unchanged_comparisons,
                     ok ? p->output_x : (int)(p->fail_elapsed_ms > 2147483647u ? 2147483647u : p->fail_elapsed_ms),
                     ok ? p->output_y : 1); /* FAIL diagnostics schema v1 */
        if (n > 0 && (size_t)n < sizeof receipt && p->foreground && ok) {
            int extra = snprintf(receipt + n, sizeof receipt - (size_t)n, " %llu %zu %u %p %p %d %s %s %llu",
                p->baseline_ms, p->baseline_size, p->baseline_format, (void *)p->baseline_buffer,
                (void *)p->selected_buffer, p->observations, p->baseline_hash, p->ack_hash, p->observation_start_ms);
            if (extra < 0 || (size_t)extra >= sizeof receipt - (size_t)n) n = -1; else n += extra;
        }
        if (n > 0 && (size_t)n + 1 < sizeof receipt) { receipt[n++] = '\n'; receipt[n] = 0; }
        if (n > 0 && (size_t)n < sizeof receipt && vm_probe_write(dirfd, "receipt.tmp", receipt, (size_t)n) == 0) {
            /* Publish only the completely written receipt without replacing one. */
            if (linkat(dirfd, "receipt.tmp", dirfd, "receipt", 0) == 0) (void)unlinkat(dirfd, "receipt.tmp", 0);
        }
        free(p->source_copy); free(p->output_copy); free(p->baseline); p->source_copy = p->output_copy = p->baseline = NULL;
        close(dirfd); return 0; /* one request for this compositor lifetime */
    }
    if (p->armed && !p->output) { vm_probe_fail(p, VM_PROBE_OUTPUT_GONE); close(dirfd); goto again; }
    if (p->armed && p->epoch != p->armed_epoch) { vm_probe_fail(p, VM_PROBE_EPOCH_CHANGED); close(dirfd); goto again; }
    if (p->armed && !vm_probe_now()) { vm_probe_fail(p, VM_PROBE_CLOCK); close(dirfd); goto again; }
    if (p->armed && vm_probe_now() >= p->deadline_ms) { vm_probe_fail(p, VM_PROBE_TIMEOUT); close(dirfd); goto again; }
    if (p->armed && p->foreground && p->baseline_ready && !p->baseline_published) {
        n = snprintf(receipt, sizeof receipt, "%s %d %llu %llu %zu %u %p %p %p\n", p->nonce, p->expected_pid,
            p->expected_start, p->baseline_ms, p->baseline_size, p->baseline_format,
            (void *)p->baseline_buffer, (void *)p->surface, (void *)p->output);
        if (n <= 0 || (size_t)n >= sizeof receipt || vm_probe_write(dirfd, "baseline.raw", p->baseline, p->baseline_size) ||
            vm_probe_write(dirfd, "baseline.meta.tmp", receipt, (size_t)n) ||
            linkat(dirfd, "baseline.meta.tmp", dirfd, "baseline.meta", 0)) {
            (void)unlinkat(dirfd, "baseline.raw", 0); (void)unlinkat(dirfd, "baseline.meta.tmp", 0); vm_probe_fail(p, VM_PROBE_BASELINE_IO);
        } else { (void)unlinkat(dirfd, "baseline.meta.tmp", 0); p->baseline_published = 1; }
        close(dirfd); goto again;
    }
    if (p->armed && p->foreground && p->baseline_published && !p->observe) {
        char nonce[33], basehash[65], ackhash[65]; unsigned long long observe_start; int used = 0;
        fd = openat(dirfd, "go", O_RDONLY | O_NOFOLLOW);
        if (fd >= 0) {
            n = read(fd, command, sizeof command - 1); close(fd);
            if (n <= 0 || n >= (ssize_t)sizeof command - 1) { vm_probe_fail(p, VM_PROBE_GO_INVALID); }
            else {
                command[n] = 0;
                if (sscanf(command, "%32s %64s %64s %llu %n", nonce, basehash, ackhash, &observe_start, &used) != 4 ||
                    !used || command[used] || strcmp(nonce, p->nonce) || !vm_probe_hash_text(basehash) || !vm_probe_hash_text(ackhash) ||
                    observe_start < p->baseline_ms || observe_start >= p->deadline_ms || observe_start > vm_probe_now()) {
                    vm_probe_fail(p, VM_PROBE_GO_INVALID);
                } else { memcpy(p->baseline_hash, basehash, 65); memcpy(p->ack_hash, ackhash, 65); p->observation_start_ms = observe_start; p->observe = 1; }
            }
        }
        close(dirfd); goto again;
    }
    if (p->armed) { if (p->foreground && p->observe) weston_output_schedule_repaint(p->output); close(dirfd); goto again; }
    fd = openat(dirfd, "request", O_RDONLY | O_NOFOLLOW);
    if (fd < 0) { close(dirfd); goto again; }
    n = read(fd, command, sizeof command - 1); close(fd);
    if (n <= 0 || n >= (ssize_t)sizeof command - 1) { close(dirfd); goto again; }
    command[n] = 0;
    if (!vm_probe_request(p, command, vm_probe_now())) { close(dirfd); goto again; }
    p->layout = p->lookup(1000); p->surface = p->layout ? p->surface_get(p->layout) : NULL;
    head = (struct wl_list *)((unsigned char *)p->compositor + OUTPUT_LIST);
    if (!p->layout || !p->surface || head->next == head || head->next->next != head) { vm_probe_fail(p, VM_PROBE_INITIAL_LAYOUT); close(dirfd); goto again; }
    p->output = (struct weston_output *)((unsigned char *)head->next - OUTPUT_LINK);
    wl_list_insert((struct wl_list *)((unsigned char *)p->output + OUTPUT_FRAME), &p->frame.link);
    wl_list_insert((struct wl_list *)((unsigned char *)p->output + OUTPUT_DESTROY), &p->output_destroy.link);
    p->armed_epoch = p->epoch; p->armed = 1;
    weston_output_schedule_repaint(p->output);
    close(dirfd);
again:
    wl_event_source_timer_update(p->timer, 100);
    return 0;
}

int controller_module_init(struct weston_compositor *compositor, int *argc, char *argv[], const void *interface, size_t version)
{
    struct vm_probe *p = &vm_probe_state; const uintptr_t *slots = interface; Dl_info info;
    struct wl_display *display; struct wl_event_loop *loop; struct stat st, loaded; uintptr_t base;
    (void)argc; (void)argv;
    if (!compositor || !interface || version != 0x278 || !slots[1] || !slots[3] || !slots[8] || !slots[9] || !slots[10] || !slots[27] ||
        !dladdr((void *)slots[9], &info) || !info.dli_fbase) return -1;
    base = (uintptr_t)info.dli_fbase;
    if (slots[1] != base + 0x64b0 || slots[3] != base + 0x6410 || slots[8] != base + 0x39d0 ||
        slots[9] != base + 0x3af0 || slots[10] != base + 0x4870 || slots[27] != base + 0x3bf0) return -1;
    if (stat(info.dli_fname, &loaded) || stat("/usr/lib/weston/ivi-shell.so", &st) ||
        loaded.st_dev != st.st_dev || loaded.st_ino != st.st_ino ||
        !dladdr((void *)pixman_image_get_data, &info) || !info.dli_fname ||
        stat(info.dli_fname, &loaded) || stat("/usr/lib/libpixman-1.so.0.42.2", &st) ||
        loaded.st_dev != st.st_dev || loaded.st_ino != st.st_ino ||
        !dladdr((void *)weston_output_schedule_repaint, &info) || !info.dli_fbase) return -1;
    p->weston_base = (uintptr_t)info.dli_fbase;
    if (mkdir(PROBE_DIR, 0700) || lstat(PROBE_DIR, &st) || !S_ISDIR(st.st_mode) || st.st_uid != 0 || (st.st_mode & 0777) != 0700) return -1;
    p->compositor = compositor; p->id = (id_fn)slots[8]; p->lookup = (lookup_fn)slots[9]; p->properties = (properties_fn)slots[10]; p->surface_get = (surface_fn)slots[27];
    p->frame.notify = vm_probe_frame; p->output_destroy.notify = vm_probe_output_destroy;
    if (((notify_add_fn)slots[1])(vm_probe_surface_event, p) || ((notify_add_fn)slots[3])(vm_probe_surface_event, p)) return -1;
    display = ACCESS(compositor, DISPLAY, struct wl_display *); loop = display ? wl_display_get_event_loop(display) : NULL;
    p->timer = loop ? wl_event_loop_add_timer(loop, vm_probe_timer, p) : NULL;
    if (!p->timer || wl_event_source_timer_update(p->timer, 100)) return -1;
    return 0;
}
