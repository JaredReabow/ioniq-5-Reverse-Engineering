/*
 * VM-only input injector for the recovered, exact-build Weston 1.10 compositor.
 *
 * This module is deliberately pinned to two structure offsets recovered from
 * DWARF in the firmware's /usr/bin/weston:
 *   struct weston_compositor.seat_list = 0x1f8
 *   struct weston_seat.link            = 0x70
 *
 * It polls /tmp/weston-vm-input for one command at a time. Legacy commands
 * remain supported. The sequenced form adds an integer transaction ID:
 *   seq N click X Y
 *   seq N drag X1 Y1 X2 Y2
 *   seq N pdrag X1 Y1 X2 Y2
 *   seq N key EVDEV_CODE   (one press followed by one release)
 *   seq N cclick X Y BOOTTIME_DEADLINE_MS (bounded one-shot pointer click)
 * N must increase for the lifetime of this Weston process. The guest atomically
 * publishes `seq N accepted|completed|error REASON` to
 * /tmp/weston-vm-input-result. The producer must publish commands atomically,
 * never overwrite an existing command, and wait for a terminal result.
 *
 * The older, unacknowledged syntax is:
 *   click X Y
 *   drag X1 Y1 X2 Y2       (touch)
 *   pdrag X1 Y1 X2 Y2      (pointer)
 *
 * Input is injected through Weston's exported notify_* API.  The command file
 * is unlinked before execution, so repeated input is explicit and bounded.
 */
#include <stddef.h>
#include <stdint.h>
#include <limits.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>

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
/*
 * Keyboard ABI evidence (offline, exact retained Gen5W Weston build):
 *
 * The retained exact Gen5W `/usr/bin/weston` evidence has SHA-256
 *   e2e4ab38bfc5321c829781e3ebb60531cadce84b16cccdfcbe373921e5b2ea00.
 * llvm-readelf --dyn-syms --wide on that ELF shows GLOBAL DEFAULT exports
 * notify_key at 0x417aa0 and weston_seat_init_keyboard at 0x4187a0.
 * The retained matching `vendor-weston.dwarf.txt` evidence has SHA-256
 *   960294b9713624e5d9d2d02009508774264e780b5cc523b00f759c611a4e262a,
 * has the same addresses, the five notify_key argument types at lines
 * 62667-62750, init's int return and (seat, xkb_keymap *) at 64985-65030,
 * and seat.keyboard_state at offset 0x20 at lines 5697-5702.
 * The separately retained Weston 1.10 source's compositor.h lines 1116-1119,
 * 1191-1193 and 1527, and input.c lines 2464-2504, document the enum,
 * signatures and NULL-keymap initialization. Its compositor-headless.c:190
 * uses that same initialization. These are static ABI facts, not evidence of
 * successful key focus or a visible firmware response in this VM.
 */
extern int weston_seat_init_keyboard(struct weston_seat *, void *);
extern void notify_key(struct weston_seat *, uint32_t, uint32_t, int, int);
extern struct wl_client *wl_resource_get_client(struct wl_resource *);
extern void wl_client_get_credentials(struct wl_client *, int *, unsigned int *,
                                      unsigned int *);
#define SEAT_LIST_OFFSET 0x1f8u
#define SEAT_LINK_OFFSET 0x70u
#define DISPLAY_OFFSET 0x10u
#define SEAT_POINTER_STATE_OFFSET 0x18u
#define SEAT_KEYBOARD_STATE_OFFSET 0x20u
#define POINTER_FOCUS_OFFSET 0x18u
#define VIEW_SURFACE_OFFSET 0x00u
#define SURFACE_RESOURCE_OFFSET 0x00u
#define BTN_LEFT 0x110
#define BUTTON_RELEASED 0
#define BUTTON_PRESSED 1
#define WL_TOUCH_DOWN 0
#define WL_TOUCH_UP 1
#define WL_TOUCH_MOTION 2
#define POLL_MS 100
#ifndef VM_INPUT_COMMAND_PATH
#define VM_INPUT_COMMAND_PATH "/tmp/weston-vm-input"
#endif
#ifndef VM_INPUT_RESULT_PATH
#define VM_INPUT_RESULT_PATH "/tmp/weston-vm-input-result"
#endif
#ifndef VM_INPUT_RESULT_TEMP_PATH
#define VM_INPUT_RESULT_TEMP_PATH "/tmp/weston-vm-input-result.tmp"
#endif

static struct weston_seat *vm_seat;
static struct weston_compositor *vm_compositor;
static struct wl_event_source *vm_timer;
static int action;             /* 0 idle, 1 click, 2 touch drag, 3 pointer, 4 key */
static int phase;
static int x1, y1, x2, y2;
static int key_code;
static int keyboard_ready;
static int last_sequence;
static int active_sequence;
static unsigned long long click_deadline_ms;

static unsigned long long vm_input_boottime_ms(void)
{
    struct timespec ts;
#if defined(__linux__) && defined(CLOCK_BOOTTIME)
    if (clock_gettime(CLOCK_BOOTTIME, &ts)) return 0;
#elif defined(__linux__)
    /* Without the suspend-inclusive clock, do not accept bounded input. */
    return 0;
#else
    /* Host-only fixture; deployed guest is Linux and uses CLOCK_BOOTTIME. */
    if (clock_gettime(CLOCK_MONOTONIC, &ts)) return 0;
#endif
    return (unsigned long long)ts.tv_sec * 1000u + (unsigned long long)ts.tv_nsec / 1000000u;
}

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
    if (p >= end || (*p != ' ' && *p != '\t'))
        return NULL;
    p = skip_space(p, end);
    if (p < end && *p == '-') {
        negative = 1;
        ++p;
    }
    while (p < end && *p >= '0' && *p <= '9') {
        if (value > (INT_MAX - (*p - '0')) / 10)
            return NULL;
        value = value * 10 + (*p - '0');
        ++p;
        digits = 1;
    }
    if (!digits)
        return NULL;
    *out = negative ? -value : value;
    return p;
}

static const char *parse_deadline(const char *p, const char *end, unsigned long long *out)
{
    unsigned long long value = 0; int digits = 0;
    if (p >= end || (*p != ' ' && *p != '\t')) return NULL;
    p = skip_space(p, end);
    while (p < end && *p >= '0' && *p <= '9') {
        if (value > (ULLONG_MAX - (unsigned)(*p - '0')) / 10u) return NULL;
        value = value * 10u + (unsigned)(*p++ - '0'); digits = 1;
    }
    if (!digits || !value) return NULL;
    *out = value; return p;
}

static int in_bounds(int x, int y)
{
    return x >= 0 && x < 1920 && y >= 0 && y < 720;
}

/* Replace the result in one rename, so a polling producer never reads a partial
 * line. Failure to publish acceptance prevents the action from executing. */
static int publish_result(int sequence, const char *state, const char *reason)
{
    char result[128];
    int fd, length;
    size_t offset = 0;
    ssize_t n;

    length = snprintf(result, sizeof(result), "seq %d %s %s\n", sequence,
                      state, reason);
    if (length <= 0 || (size_t)length >= sizeof(result))
        return -1;
    fd = open(VM_INPUT_RESULT_TEMP_PATH, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0)
        return -1;
    while (offset < (size_t)length) {
        n = write(fd, result + offset, (size_t)length - offset);
        if (n <= 0) {
            (void)close(fd);
            (void)unlink(VM_INPUT_RESULT_TEMP_PATH);
            return -1;
        }
        offset += (size_t)n;
    }
    if (close(fd) != 0 || rename(VM_INPUT_RESULT_TEMP_PATH, VM_INPUT_RESULT_PATH) != 0) {
        (void)unlink(VM_INPUT_RESULT_TEMP_PATH);
        return -1;
    }
    return 0;
}

static int token(const char **input, const char *end, const char *word)
{
    const char *p = skip_space(*input, end);
    while (*word && p < end && *p == *word) {
        ++p;
        ++word;
    }
    if (*word || (p < end && *p != ' ' && *p != '\t' && *p != '\n' && *p != '\r'))
        return 0;
    *input = p;
    return 1;
}

static int only_trailing_space(const char *p, const char *end)
{
    while (p < end && (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r'))
        ++p;
    return p == end;
}

/* Parse and validate a complete line before modifying the active action. */
static void accept_command(const char *buf, size_t size)
{
    const char *p = buf, *end = buf + size;
    int seq = 0, next_action = 0, a = 0, b = 0, c = 0, d = 0;
    unsigned long long deadline_ms = 0;
    int sequenced = token(&p, end, "seq");

    if (sequenced) {
        p = parse_int(p, end, &seq);
        if (!p || seq <= 0) {
            (void)publish_result(0, "error", "invalid_sequence");
            return;
        }
        if (seq <= last_sequence) {
            (void)publish_result(seq, "error", "duplicate_or_old_sequence");
            return;
        }
    }
    if (sequenced && token(&p, end, "cclick"))
        next_action = 5;
    else if (token(&p, end, "click"))
        next_action = 1;
    else if (token(&p, end, "pdrag"))
        next_action = 3;
    else if (token(&p, end, "drag"))
        next_action = 2;
    else if (sequenced && token(&p, end, "key"))
        next_action = 4;

    if (next_action)
        p = parse_int(p, end, &a);
    if (p && ((next_action >= 1 && next_action <= 3) || next_action == 5))
        p = parse_int(p, end, &b);
    if (p && (next_action == 2 || next_action == 3))
        p = parse_int(p, end, &c);
    if (p && (next_action == 2 || next_action == 3))
        p = parse_int(p, end, &d);
    if (p && next_action == 5)
        p = parse_deadline(p, end, &deadline_ms);
    if (!next_action || !p || !only_trailing_space(p, end) ||
        (next_action == 4 && (a < 1 || a > 255)) ||
        (next_action != 4 && !in_bounds(a, b)) ||
        ((next_action == 2 || next_action == 3) && !in_bounds(c, d))) {
        if (sequenced) {
            last_sequence = seq;
            (void)publish_result(seq, "error", "invalid_command");
        }
        return;
    }
    if (next_action == 4 && !keyboard_ready) {
        if (sequenced) {
            last_sequence = seq;
            (void)publish_result(seq, "error", "keyboard_unavailable");
        }
        return;
    }
    if (sequenced && publish_result(seq, "accepted", "queued") != 0) {
        log_literal("VM_INPUT_RESULT_ERROR\n", 22);
        return;
    }
    if (sequenced)
        last_sequence = seq;
    active_sequence = seq;
    click_deadline_ms = deadline_ms;
    x1 = a;
    y1 = b;
    x2 = c;
    y2 = d;
    key_code = a;
    action = next_action;
    phase = 0;
    if (action == 1 || action == 5)
        log_literal("VM_INPUT_CLICK_ACCEPTED\n", 24);
    else if (action == 2)
        log_literal("VM_INPUT_DRAG_ACCEPTED\n", 23);
    else if (action == 3)
        log_literal("VM_INPUT_PDRAG_ACCEPTED\n", 24);
    else
        log_literal("VM_INPUT_KEY_ACCEPTED\n", 22);
}

static void load_command(void)
{
    char buf[128];
    ssize_t n;
    int fd = open(VM_INPUT_COMMAND_PATH, O_RDONLY);
    if (fd < 0)
        return;
    n = read(fd, buf, sizeof(buf));
    (void)close(fd);
    (void)unlink(VM_INPUT_COMMAND_PATH);
    if (n <= 0)
        return;
    if ((size_t)n == sizeof(buf)) {
        (void)publish_result(0, "error", "command_too_long");
        return;
    }
    accept_command(buf, (size_t)n);
}

static void execute_action(void)
{
    int step;
    if (action == 5) {
        if (phase == 0) {
            unsigned long long now = vm_input_boottime_ms();
            if (!now || now >= click_deadline_ms) {
                action = 0;
                if (active_sequence) (void)publish_result(active_sequence, "error", "expired");
                return;
            }
            /* Non-real-time scheduling may still preempt between this check
             * and injection; the paired release is always sent once pressed. */
            pointer_move(x1, y1);
            pointer_button(BUTTON_PRESSED);
        } else {
            pointer_button(BUTTON_RELEASED);
            action = 0;
            if (active_sequence) (void)publish_result(active_sequence, "completed", "injected");
        }
        ++phase;
        return;
    }
    if (action == 1) {
        if (phase == 0) {
            pointer_move(x1, y1);
            touch_event(x1, y1, WL_TOUCH_DOWN);
        } else {
            touch_event(x1, y1, WL_TOUCH_UP);
            action = 0;
            log_literal("VM_INPUT_CLICK_DONE\n", 20);
            if (active_sequence)
                (void)publish_result(active_sequence, "completed", "injected");
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
            if (active_sequence)
                (void)publish_result(active_sequence, "completed", "injected");
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
            if (active_sequence)
                (void)publish_result(active_sequence, "completed", "injected");
        }
        ++phase;
        return;
    }
    if (action == 4) {
        /* STATE_UPDATE_AUTOMATIC=0, WL_KEYBOARD_KEY_STATE_PRESSED=1,
         * RELEASED=0 in the matching Weston 1.10 headers. Always release. */
        if (phase == 0)
            notify_key(vm_seat, weston_compositor_get_time(), (uint32_t)key_code, 1, 0);
        else {
            notify_key(vm_seat, weston_compositor_get_time(), (uint32_t)key_code, 0, 0);
            action = 0;
            (void)publish_result(active_sequence, "completed", "injected");
        }
        ++phase;
    }
}


/* PROJECTION-ONLY: bind the first seat if the compositor has one.
 *
 * weston 1.10 creates a seat in the *backend*: headless does it unconditionally
 * (weston_seat_init(&b->fake_seat, ...)), while drm and fbdev rely on the
 * libinput/udev path and only get a seat when udev reports an input device - which
 * QEMU does not provide. Returning -1 here made the module abort the whole
 * compositor on those backends (VM_INPUT_NO_SEAT, then teardown), which looked like
 * a display-backend failure for several runs before a trace showed the exit.
 *
 * So: attach if a seat exists, otherwise stay loaded and try again on the timer.
 */
static int bind_first_seat(struct weston_compositor *c)
{
    struct wl_list *head = (struct wl_list *)((char *)c + SEAT_LIST_OFFSET);
    struct wl_list *link = head->next;

    if (!link || link == head)
        return 0;                       /* no seat yet - not an error */
    vm_seat = (struct weston_seat *)((char *)link - SEAT_LINK_OFFSET);
    weston_seat_init_touch(vm_seat);
    /* The retained binary's DWARF places keyboard_state at 0x20. Avoid
     * incrementing an already-present keyboard's device count. A NULL keymap
     * requests Weston's compositor default, as in its headless backend. */
    keyboard_ready = *(void **)((char *)vm_seat + SEAT_KEYBOARD_STATE_OFFSET) != NULL;
    if (!keyboard_ready)
        keyboard_ready = weston_seat_init_keyboard(vm_seat, NULL) == 0;
    if (!keyboard_ready)
        log_literal("VM_INPUT_KEYBOARD_UNAVAILABLE\n", 30);
    log_literal("VM_INPUT_SEAT_BOUND\n", 21);
    return 1;
}

static int timer_handler(void *data)
{
    (void)data;
    if (!vm_seat) {
        if (!bind_first_seat(vm_compositor)) {
            (void)wl_event_source_timer_update(vm_timer, POLL_MS);
            return 0;                   /* still no seat: stay alive, keep polling */
        }
    }
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
    struct wl_display *display;
    struct wl_event_loop *loop;
    (void)argc;
    (void)argv;

    vm_compositor = compositor;
    if (!bind_first_seat(compositor)) {
        log_literal("VM_INPUT_NO_SEAT_DEFERRED\n", 26);
        /* not an error: the timer binds when a seat appears (drm/fbdev have none
         * under QEMU until an input device is reported) */
    }
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
