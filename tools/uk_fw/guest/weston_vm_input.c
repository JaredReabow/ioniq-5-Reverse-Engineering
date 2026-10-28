/*
 * VM-only input injector for the recovered, exact-build Weston 1.10 compositor.
 *
 * This module is deliberately pinned to two structure offsets recovered from
 * DWARF in the firmware's /usr/bin/weston:
 *   struct weston_compositor.seat_list = 0x1f8
 *   struct weston_seat.link            = 0x70
 *
 * It polls /tmp/weston-vm-input for one command at a time:
 *   click X Y
 *   drag X1 Y1 X2 Y2       (touch)
 *   pdrag X1 Y1 X2 Y2      (pointer)
 *
 * Input is injected through Weston's exported notify_* API.  The command file
 * is unlinked before execution, so repeated input is explicit and bounded.
 */
#include <stddef.h>
#include <stdint.h>

struct wl_list { struct wl_list *prev, *next; };
struct wl_display;
struct wl_event_loop;
struct wl_event_source;
struct weston_compositor;
struct weston_seat;
struct weston_view;
struct weston_surface;
struct wl_resource;
struct wl_client;

typedef int32_t wl_fixed_t;
typedef long ssize_t;

extern struct wl_event_loop *wl_display_get_event_loop(struct wl_display *);
extern struct wl_event_source *wl_event_loop_add_timer(
    struct wl_event_loop *, int (*)(void *), void *);
extern int wl_event_source_timer_update(struct wl_event_source *, int);
extern uint32_t weston_compositor_get_time(void);
extern void notify_motion_absolute(struct weston_seat *, uint32_t,
                                   wl_fixed_t, wl_fixed_t);
extern void notify_button(struct weston_seat *, uint32_t, int32_t, int);
extern void notify_pointer_frame(struct weston_seat *);
extern void weston_seat_init_touch(struct weston_seat *);
extern void notify_touch(struct weston_seat *, uint32_t, int,
                         wl_fixed_t, wl_fixed_t, int);
extern void notify_touch_frame(struct weston_seat *);
extern struct wl_client *wl_resource_get_client(struct wl_resource *);
extern void wl_client_get_credentials(struct wl_client *, int *, unsigned int *,
                                      unsigned int *);
extern int open(const char *, int, ...);
extern ssize_t read(int, void *, size_t);
extern int close(int);
extern int unlink(const char *);
extern ssize_t write(int, const void *, size_t);

#define SEAT_LIST_OFFSET 0x1f8u
#define SEAT_LINK_OFFSET 0x70u
#define DISPLAY_OFFSET 0x10u
#define SEAT_POINTER_STATE_OFFSET 0x18u
#define POINTER_FOCUS_OFFSET 0x18u
#define VIEW_SURFACE_OFFSET 0x00u
#define SURFACE_RESOURCE_OFFSET 0x00u
#define O_RDONLY 0
#define BTN_LEFT 0x110
#define BUTTON_RELEASED 0
#define BUTTON_PRESSED 1
#define WL_TOUCH_DOWN 0
#define WL_TOUCH_UP 1
#define WL_TOUCH_MOTION 2
#define POLL_MS 100

static struct weston_seat *vm_seat;
static struct wl_event_source *vm_timer;
static int action;             /* 0 idle, 1 click, 2 touch drag, 3 pointer drag */
static int phase;
static int x1, y1, x2, y2;

static void log_literal(const char *s, size_t n)
{
    (void)write(2, s, n);
}

static void log_int(int value)
{
    char buf[16];
    unsigned int n = 0;
    unsigned int v;
    if (value < 0) {
        log_literal("-", 1);
        v = (unsigned int)(-(value + 1)) + 1u;
    } else {
        v = (unsigned int)value;
    }
    do {
        buf[n++] = (char)('0' + (v % 10u));
        v /= 10u;
    } while (v && n < sizeof(buf));
    while (n)
        (void)write(2, &buf[--n], 1);
}

/*
 * Observational exact-build focus trace. The offsets are recovered from the
 * vendor Weston's DWARF and do not alter focus or application state.
 */
static void log_pointer_focus(const char *phase_name, size_t phase_len)
{
    void *pointer;
    struct weston_view *view;
    struct weston_surface *surface;
    struct wl_resource *resource;
    struct wl_client *client;
    int pid = -1;
    unsigned int uid = 0, gid = 0;

    log_literal("VM_INPUT_FOCUS_", 15);
    log_literal(phase_name, phase_len);
    log_literal(" pid=", 5);
    pointer = *(void **)((char *)vm_seat + SEAT_POINTER_STATE_OFFSET);
    if (!pointer) {
        log_literal("NO_POINTER\n", 11);
        return;
    }
    view = *(struct weston_view **)((char *)pointer + POINTER_FOCUS_OFFSET);
    if (!view) {
        log_literal("NO_VIEW\n", 8);
        return;
    }
    surface = *(struct weston_surface **)((char *)view + VIEW_SURFACE_OFFSET);
    resource = surface ? *(struct wl_resource **)((char *)surface + SURFACE_RESOURCE_OFFSET) : 0;
    client = resource ? wl_resource_get_client(resource) : 0;
    if (!client) {
        log_literal("NO_CLIENT\n", 10);
        return;
    }
    wl_client_get_credentials(client, &pid, &uid, &gid);
    log_int(pid);
    log_literal(" uid=", 5);
    log_int((int)uid);
    log_literal("\n", 1);
}

static wl_fixed_t fixed_from_int(int value)
{
    return (wl_fixed_t)(value * 256);
}

static void pointer_move(int x, int y)
{
    log_pointer_focus("BEFORE_MOVE", 11);
    notify_motion_absolute(vm_seat, weston_compositor_get_time(),
                           fixed_from_int(x), fixed_from_int(y));
    notify_pointer_frame(vm_seat);
    log_pointer_focus("AFTER_MOVE", 10);
}

static void pointer_button(int state)
{
    log_pointer_focus(state == BUTTON_PRESSED ? "BEFORE_DOWN" : "BEFORE_UP",
                      state == BUTTON_PRESSED ? 11 : 9);
    notify_button(vm_seat, weston_compositor_get_time(), BTN_LEFT, state);
    notify_pointer_frame(vm_seat);
    log_pointer_focus(state == BUTTON_PRESSED ? "AFTER_DOWN" : "AFTER_UP",
                      state == BUTTON_PRESSED ? 10 : 8);
}

static void touch_event(int x, int y, int type)
{
    notify_touch(vm_seat, weston_compositor_get_time(), 0,
                 fixed_from_int(x), fixed_from_int(y), type);
    notify_touch_frame(vm_seat);
}

static const char *skip_space(const char *p, const char *end)
{
    while (p < end && (*p == ' ' || *p == '\t'))
        ++p;
    return p;
}

static const char *parse_int(const char *p, const char *end, int *out)
{
    int value = 0;
    int negative = 0;
    int digits = 0;
    p = skip_space(p, end);
    if (p < end && *p == '-') {
        negative = 1;
        ++p;
    }
    while (p < end && *p >= '0' && *p <= '9') {
        value = value * 10 + (*p - '0');
        ++p;
        digits = 1;
    }
    if (!digits)
        return NULL;
    *out = negative ? -value : value;
    return p;
}

static int in_bounds(int x, int y)
{
    return x >= 0 && x < 1920 && y >= 0 && y < 720;
}

static void load_command(void)
{
    static const char path[] = "/tmp/weston-vm-input";
    char buf[96];
    const char *p, *end;
    ssize_t n;
    int fd = open(path, O_RDONLY);
    if (fd < 0)
        return;
    n = read(fd, buf, sizeof(buf));
    (void)close(fd);
    (void)unlink(path);
    if (n <= 0)
        return;
    p = buf;
    end = buf + n;
    if (n >= 5 && p[0] == 'c' && p[1] == 'l' && p[2] == 'i' &&
        p[3] == 'c' && p[4] == 'k') {
        p = parse_int(p + 5, end, &x1);
        if (p) p = parse_int(p, end, &y1);
        if (p && in_bounds(x1, y1)) {
            action = 1;
            phase = 0;
            log_literal("VM_INPUT_CLICK_ACCEPTED\n", 24);
        }
    } else if (n >= 5 && p[0] == 'p' && p[1] == 'd' && p[2] == 'r' &&
               p[3] == 'a' && p[4] == 'g') {
        p = parse_int(p + 5, end, &x1);
        if (p) p = parse_int(p, end, &y1);
        if (p) p = parse_int(p, end, &x2);
        if (p) p = parse_int(p, end, &y2);
        if (p && in_bounds(x1, y1) && in_bounds(x2, y2)) {
            action = 3;
            phase = 0;
            log_literal("VM_INPUT_PDRAG_ACCEPTED\n", 24);
        }
    } else if (n >= 4 && p[0] == 'd' && p[1] == 'r' && p[2] == 'a' &&
               p[3] == 'g') {
        p = parse_int(p + 4, end, &x1);
        if (p) p = parse_int(p, end, &y1);
        if (p) p = parse_int(p, end, &x2);
        if (p) p = parse_int(p, end, &y2);
        if (p && in_bounds(x1, y1) && in_bounds(x2, y2)) {
            action = 2;
            phase = 0;
            log_literal("VM_INPUT_DRAG_ACCEPTED\n", 23);
        }
    }
}

static void execute_action(void)
{
    int step;
    if (action == 1) {
        if (phase == 0) {
            pointer_move(x1, y1);
            touch_event(x1, y1, WL_TOUCH_DOWN);
        } else {
            touch_event(x1, y1, WL_TOUCH_UP);
            action = 0;
            log_literal("VM_INPUT_CLICK_DONE\n", 20);
        }
        ++phase;
        return;
    }
    if (action == 2) {
        if (phase == 0) {
            pointer_move(x1, y1);
            touch_event(x1, y1, WL_TOUCH_DOWN);
        } else if (phase >= 1 && phase <= 6) {
            step = phase;
            touch_event(x1 + ((x2 - x1) * step) / 6,
                        y1 + ((y2 - y1) * step) / 6,
                        WL_TOUCH_MOTION);
        } else {
            touch_event(x2, y2, WL_TOUCH_UP);
            pointer_move(x2, y2);
            action = 0;
            log_literal("VM_INPUT_DRAG_DONE\n", 19);
        }
        ++phase;
        return;
    }
    if (action == 3) {
        if (phase == 0)
            pointer_move(x1, y1);
        else if (phase == 1)
            pointer_button(BUTTON_PRESSED);
        else if (phase == 2)
            pointer_move((x1 + x2) / 2, (y1 + y2) / 2);
        else if (phase == 3)
            pointer_move(x2, y2);
        else {
            pointer_button(BUTTON_RELEASED);
            action = 0;
            log_literal("VM_INPUT_PDRAG_DONE\n", 20);
        }
        ++phase;
    }
}

static int timer_handler(void *data)
{
    (void)data;
    if (action)
        execute_action();
    else
        load_command();
    (void)wl_event_source_timer_update(vm_timer, POLL_MS);
    return 0;
}

__attribute__((visibility("default")))
int module_init(struct weston_compositor *compositor, int *argc, char *argv[])
{
    struct wl_list *head;
    struct wl_list *link;
    struct wl_display *display;
    struct wl_event_loop *loop;
    (void)argc;
    (void)argv;

    head = (struct wl_list *)((char *)compositor + SEAT_LIST_OFFSET);
    link = head->next;
    if (!link || link == head) {
        log_literal("VM_INPUT_NO_SEAT\n", 17);
        return -1;
    }
    vm_seat = (struct weston_seat *)((char *)link - SEAT_LINK_OFFSET);
    weston_seat_init_touch(vm_seat);
    display = *(struct wl_display **)((char *)compositor + DISPLAY_OFFSET);
    loop = wl_display_get_event_loop(display);
    vm_timer = wl_event_loop_add_timer(loop, timer_handler, NULL);
    if (!vm_timer) {
        log_literal("VM_INPUT_NO_TIMER\n", 18);
        return -1;
    }
    (void)wl_event_source_timer_update(vm_timer, POLL_MS);
    log_literal("VM_INPUT_READY\n", 15);
    return 0;
}
