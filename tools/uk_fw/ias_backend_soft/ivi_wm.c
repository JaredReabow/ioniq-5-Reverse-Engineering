/*
 * ivi_wm — drive the vendor's purpose-built `ivi_window_manager` interface:
 * give a surface an ivi layout rectangle, make it visible, and request it as
 * the foreground surface on a display plane.
 *
 * WHY THIS EXISTS
 * ---------------
 * The vendor app (/app/bin/AppHomeScreen) creates a wl_surface, attaches a
 * buffer and commits; that much is visible in its WAYLAND_DEBUG trace. A
 * committed surface with no layout is still not composited: on this image the
 * actor that would otherwise place it (the vendor's ApplicationManager talking
 * to ivi_controller) is absent when the app runs standalone. Rather than
 * hand-rolling generic ivi_controller layer manipulation, use the interface the
 * vendor ships for exactly this: the `ivi_window_manager` global (version 1).
 *
 * WHAT IT DOES, IN ORDER
 * ----------------------
 *   1. wl_display_connect(NULL) -> $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY
 *   2. bind the `ivi_window_manager` global, version 1
 *   3. get_primary_screen_size()                  [skippable: --no-query]
 *      and print the primary_screen_size(width,height) event it answers with.
 *      This is the only event this interface defines, so it doubles as a
 *      liveness check before anything is asked for.
 *   4. set_surface_layout(id, 0, 0, w, h)         defaults 1920x720
 *   5. set_surface_visible(id, 1)
 *   6. request_fg(plane, id)                      default plane 0
 *   7. one blocking sync roundtrip after each request (the interface posts no
 *      error event, so a roundtrip that returns is the only confirmation
 *      available), then flush and disconnect.
 *
 * THE SURFACE ID
 * --------------
 * surface_id is the id the compositor knows the surface by — for a Qt app on
 * this image the ivi surface id derived from QT_WAYLAND_SET_SURFACE_ID /
 * QT_WAYLAND_USE_PID_FOR_SURFACE_ID (see the notes in ivi_place.c and the
 * analysis accompanying this tool). It is not the wl_surface object id and not
 * a protocol object id. Unlike ivi_controller.surface_create() this interface
 * is a plain uint argument, so an unknown id cannot be detected client-side:
 * the compositor simply has nothing to apply the request to.
 *
 * This program sends requests. It cannot observe the panel, so it says nothing
 * about whether the surface ends up on screen; that is a measurement.
 *
 * PROTOCOL CODE
 * -------------
 * ivi-window-manager-client-protocol.h / ivi-window-manager-protocol.c were
 * generated from the vendor XML shipped in the image at
 *   usr/share/ivi-window-manager/ivi-window-manager.xml
 * (work/decrypted-eu-260128/extracted-safe/mango-rootfs/...) with wayland
 * 1.10's own scanner, because the guest's libwayland-client is 1.10 and later
 * scanners emit wl_proxy_marshal_flags(), which does not exist there.
 * The scanner run was:
 *   wl-scanner client-header ivi-window-manager.xml ivi-window-manager-client-protocol.h
 *   wl-scanner code          ivi-window-manager.xml ivi-window-manager-protocol.c
 *
 * Request opcodes as generated (no gaps, XML order):
 *   0  update_layout(uint)
 *   1  get_primary_screen_size()
 *   2  set_surface_visible(uint surface_id, uint is_visible)
 *   3  request_fg(int display_plane_idx, uint surface_id)
 *   4  show_notification(int, uint)          5  show_PAS(int, uint)
 *   6  set_surface_layout(uint, int x, int y, int w, int h)
 *   7  set_surface_alpha(uint, int)          8  set_visible_for_qtwayland(uint, int)
 *   9  expand_drawer(int, int)              10  set_surface_to_top_order_within_layer(uint)
 *  11  set_parent_child_surface(uint, uint) 12  set_surface_to_full_screen(uint, int, uint)
 *  13  request_fg_with_app_id(int, string)  14  set_surface_to_full_screen_with_app_id(int, string, int, uint)
 *  15  set_app_name_with_app_type(uint, string)
 *  16  show_app_with_app_type(int, uint, uint)
 *  17  set_surface_position_with_app_id(int, string, int, int)
 *  18  request_clone_surface_create(uint, uint, uint, int, int, int, int)
 *  19  set_clone_surface_layout(uint, int, int, int, int)
 *  20  request_clone_surface_destroy(uint)
 *  21  request_move_layer(int layer_id, int dx, int dy, int duration)
 *   0  event primary_screen_size(uint width, uint height)
 */
#include <errno.h>
#include <poll.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include <wayland-client.h>
#include "wayland-client-protocol.h"
#include "ivi-window-manager-client-protocol.h"

#define DEFAULT_W        1920
#define DEFAULT_H         720
#define DEFAULT_PLANE       0
#define DEFAULT_TIMEOUT  5000

/* exit codes, documented in usage() */
#define EX_OK          0
#define EX_USAGE       1
#define EX_CONNECT     2
#define EX_PROTOCOL    3

static int verbose;

static void
trace(const char *fmt, ...)
{
	va_list ap;

	fputs("ivi_wm: ", stdout);
	va_start(ap, fmt);
	vfprintf(stdout, fmt, ap);
	va_end(ap);
	fputc('\n', stdout);
	fflush(stdout);
}

static int64_t
now_ms(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

/* ---- ivi_window_manager listener: one event, the screen size reply ---- */

struct wm_obs {
	int size_seen;
	uint32_t width, height;
};

static void
wm_primary_screen_size(void *data, struct ivi_window_manager *wm,
		       uint32_t width, uint32_t height)
{
	struct wm_obs *o = data;

	(void)wm;
	o->size_seen = 1;
	o->width = width;
	o->height = height;
	trace("  <- ivi_window_manager.primary_screen_size(%u, %u)",
	      width, height);
}

static const struct ivi_window_manager_listener wm_listener = {
	wm_primary_screen_size,
};

/* ---- wl_registry ---- */

struct global_names {
	const char *name;
	int seen;
	int version;
};

static struct global_names interesting[] = {
	{ "ivi_window_manager",  0, 0 },
	{ "ivi_controller",      0, 0 },
	{ "ivi_application",     0, 0 },
	{ "wl_compositor",       0, 0 },
};

static struct ivi_window_manager *wm;
static int wm_global_name;

static void
registry_global(void *data, struct wl_registry *registry, uint32_t name,
		const char *interface, uint32_t version)
{
	(void)data;
	size_t i;

	for (i = 0; i < sizeof(interesting) / sizeof(interesting[0]); i++) {
		if (strcmp(interface, interesting[i].name) == 0) {
			interesting[i].seen = 1;
			interesting[i].version = (int)version;
		}
	}

	if (strcmp(interface, "ivi_window_manager") == 0 && !wm) {
		/*
		 * The global announces version 1 and the XML declares
		 * version="1", so requesting more is a protocol violation and
		 * requesting less buys nothing.
		 */
		wm = wl_registry_bind(registry, name,
				      &ivi_window_manager_interface, 1);
		wm_global_name = (int)name;
		if (wm)
			ivi_window_manager_add_listener(wm, &wm_listener,
							&(struct wm_obs){ 0 });
	}
}

static void
registry_global_remove(void *data, struct wl_registry *registry, uint32_t name)
{
	(void)data; (void)registry; (void)name;
}

static const struct wl_registry_listener registry_listener = {
	registry_global,
	registry_global_remove,
};

/* ---- timeoutable roundtrip ---- */

static int sync_done;

static void
sync_callback(void *data, struct wl_callback *cb, uint32_t serial)
{
	(void)data; (void)cb; (void)serial;
	sync_done = 1;
}

static const struct wl_callback_listener sync_listener = {
	sync_callback
};

/*
 * wl_display_roundtrip() has no timeout. A compositor that has stopped
 * answering would hang this tool silently, so this is the same roundtrip with a
 * deadline; ETIMEDOUT is reported rather than waited out.
 */
static int
roundtrip_timeout(struct wl_display *display, int timeout_ms)
{
	struct wl_callback *cb;
	int64_t deadline = now_ms() + timeout_ms;

	cb = wl_display_sync(display);
	if (!cb) {
		fprintf(stderr, "ivi_wm: wl_display_sync: %s\n",
			strerror(errno));
		return -1;
	}
	wl_callback_add_listener(cb, &sync_listener, NULL);
	sync_done = 0;

	while (!sync_done) {
		struct pollfd pfd;
		int64_t left;
		int r;

		if (wl_display_dispatch_pending(display) < 0) {
			wl_callback_destroy(cb);
			return -1;
		}
		if (sync_done)
			break;
		if (wl_display_flush(display) < 0 && errno != EAGAIN) {
			wl_callback_destroy(cb);
			return -1;
		}

		left = deadline - now_ms();
		if (left <= 0) {
			wl_callback_destroy(cb);
			errno = ETIMEDOUT;
			return -1;
		}

		pfd.fd = wl_display_get_fd(display);
		pfd.events = POLLIN;
		pfd.revents = 0;
		r = poll(&pfd, 1, (int)left);
		if (r < 0) {
			if (errno == EINTR)
				continue;
			wl_callback_destroy(cb);
			return -1;
		}
		if (r == 0) {
			wl_callback_destroy(cb);
			errno = ETIMEDOUT;
			return -1;
		}
		if (wl_display_dispatch(display) < 0) {
			wl_callback_destroy(cb);
			return -1;
		}
	}

	wl_callback_destroy(cb);
	return 0;
}

/* ---- argument parsing ---- */

static void
usage(FILE *f, const char *argv0)
{
	fprintf(f,
"usage: %s [options] <surface-id> [plane] [w h]\n"
"\n"
"Ask the vendor ivi_window_manager interface to lay out a surface, make it\n"
"visible and bring it to the foreground:\n"
"\n"
"  ivi_window_manager.get_primary_screen_size()        (unless --no-query)\n"
"  ivi_window_manager.set_surface_layout(%d, 0, 0, %d, %d)\n"
"  ivi_window_manager.set_surface_visible(%d, 1)\n"
"  ivi_window_manager.request_fg(%d, %d)\n"
"\n"
"  <surface-id>  the ivi surface id the compositor knows the surface by — for\n"
"                a Qt client on this image the id it derived from\n"
"                QT_WAYLAND_SET_SURFACE_ID / QT_WAYLAND_USE_PID_FOR_SURFACE_ID.\n"
"                Not the wl_surface object id.\n"
"  [plane]       display_plane_idx for request_fg, default %d.\n"
"  [w h]         layout width and height passed to set_surface_layout,\n"
"                default %d %d.\n"
"\n"
"options:\n"
"  --no-query    skip get_primary_screen_size and its reply.\n"
"  --timeout MS  per-roundtrip deadline, default %d.\n"
"  -v, --verbose also print the arguments of each request as it is queued.\n"
"  -h, --help    this text.\n"
"\n"
"exit status: 0 ok, 1 usage, 2 no display / no ivi_window_manager global,\n"
"             3 a roundtrip failed.\n"
"\n"
"This tool reports what it sent, not what the panel shows.\n",
		argv0, 0, DEFAULT_W, DEFAULT_H, 0, DEFAULT_PLANE, 0,
		DEFAULT_PLANE, DEFAULT_W, DEFAULT_H, DEFAULT_TIMEOUT);
}

static int
parse_uint(const char *s, uint32_t *out)
{
	char *end = NULL;
	unsigned long v;

	errno = 0;
	v = strtoul(s, &end, 0);
	if (errno || !end || *end != '\0' || s[0] == '\0')
		return -1;
	*out = (uint32_t)v;
	return 0;
}

static int
parse_int32(const char *s, int32_t *out)
{
	char *end = NULL;
	long v;

	errno = 0;
	v = strtol(s, &end, 0);
	if (errno || !end || *end != '\0' || s[0] == '\0')
		return -1;
	*out = (int32_t)v;
	return 0;
}

int
main(int argc, char **argv)
{
	struct wl_display *display;
	struct wl_registry *registry;
	struct wm_obs obs = { 0 };
	uint32_t surface_id = 0;
	int32_t plane = DEFAULT_PLANE;
	int32_t lw = DEFAULT_W, lh = DEFAULT_H;
	int have_surface_id = 0;
	int query = 1;
	int timeout_ms = DEFAULT_TIMEOUT;
	int positional[4];
	int npos = 0;
	int i, rc;
	const char *runtime_dir, *wl_display_name;

	for (i = 1; i < argc; i++) {
		const char *a = argv[i];

		if (strcmp(a, "-h") == 0 || strcmp(a, "--help") == 0) {
			usage(stdout, argv[0]);
			return EX_OK;
		} else if (strcmp(a, "--no-query") == 0) {
			query = 0;
		} else if (strcmp(a, "-v") == 0 || strcmp(a, "--verbose") == 0) {
			verbose = 1;
		} else if (strcmp(a, "--timeout") == 0 && i + 1 < argc) {
			uint32_t t;

			if (parse_uint(argv[++i], &t) < 0 || t == 0) {
				fprintf(stderr, "ivi_wm: bad --timeout value\n");
				return EX_USAGE;
			}
			timeout_ms = (int)t;
		} else if (a[0] == '-' && a[1] != '\0') {
			fprintf(stderr, "ivi_wm: unknown option %s\n", a);
			usage(stderr, argv[0]);
			return EX_USAGE;
		} else {
			if (npos >= 4) {
				fprintf(stderr, "ivi_wm: too many arguments\n");
				return EX_USAGE;
			}
			positional[npos++] = i;
		}
	}

	if (npos != 1 && npos != 2 && npos != 4) {
		usage(stderr, argv[0]);
		return EX_USAGE;
	}
	if (parse_uint(argv[positional[0]], &surface_id) < 0) {
		fprintf(stderr, "ivi_wm: bad surface id '%s'\n",
			argv[positional[0]]);
		return EX_USAGE;
	}
	have_surface_id = 1;
	if (npos >= 2 && parse_int32(argv[positional[1]], &plane) < 0) {
		fprintf(stderr, "ivi_wm: bad plane index '%s'\n",
			argv[positional[1]]);
		return EX_USAGE;
	}
	if (npos == 4) {
		if (parse_int32(argv[positional[2]], &lw) < 0 ||
		    parse_int32(argv[positional[3]], &lh) < 0) {
			fprintf(stderr, "ivi_wm: bad layout size\n");
			return EX_USAGE;
		}
	}
	if (lw <= 0 || lh <= 0) {
		fprintf(stderr, "ivi_wm: layout width and height must be "
			"positive, got %d x %d\n", (int)lw, (int)lh);
		return EX_USAGE;
	}
	if (!have_surface_id) {
		usage(stderr, argv[0]);
		return EX_USAGE;
	}

	/* ---- connect ---- */
	runtime_dir = getenv("XDG_RUNTIME_DIR");
	wl_display_name = getenv("WAYLAND_DISPLAY");
	trace("connecting to %s/%s",
	      runtime_dir ? runtime_dir : "(XDG_RUNTIME_DIR unset)",
	      wl_display_name ? wl_display_name : "wayland-0");

	display = wl_display_connect(NULL);
	if (!display) {
		fprintf(stderr,
			"ivi_wm: cannot connect to the wayland display: %s\n"
			"ivi_wm: set XDG_RUNTIME_DIR (and WAYLAND_DISPLAY if not "
			"wayland-0)\n", strerror(errno));
		return EX_CONNECT;
	}

	registry = wl_display_get_registry(display);
	wl_registry_add_listener(registry, &registry_listener, NULL);

	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_wm: registry roundtrip failed: %s\n",
			strerror(errno));
		wl_display_disconnect(display);
		return EX_CONNECT;
	}

	if (!wm) {
		fprintf(stderr, "ivi_wm: the compositor advertises no "
			"ivi_window_manager global\n");
		for (i = 0; i < (int)(sizeof(interesting) / sizeof(interesting[0])); i++)
			fprintf(stderr, "ivi_wm:   %s: %s (version %d)\n",
				interesting[i].name,
				interesting[i].seen ? "present" : "absent",
				interesting[i].version);
		wl_display_disconnect(display);
		return EX_CONNECT;
	}

	trace("bound ivi_window_manager (registry name %d, version 1)",
	      wm_global_name);

	/* ---- step 1: who is the compositor, and how big is the screen ---- */
	rc = EX_OK;
	if (query) {
		trace("request ivi_window_manager.get_primary_screen_size()");
		ivi_window_manager_get_primary_screen_size(wm);
		if (roundtrip_timeout(display, timeout_ms) < 0) {
			fprintf(stderr, "ivi_wm: roundtrip after "
				"get_primary_screen_size failed: %s\n",
				strerror(errno));
			wl_display_disconnect(display);
			return EX_PROTOCOL;
		}
		if (obs.size_seen) {
			trace("primary screen size: %u x %u", obs.width,
			      obs.height);
		} else {
			/*
			 * Not fatal: the three requests below do not depend on
			 * the reply. It is worth saying out loud, though, since
			 * a silent get_primary_screen_size() means the
			 * interface is bound but not answering.
			 */
			trace("primary screen size: no reply (the compositor "
			      "sent no primary_screen_size event); continuing");
		}
	} else {
		trace("skipping get_primary_screen_size (--no-query)");
	}

	/* ---- step 2: layout ---- */
	trace("request ivi_window_manager.set_surface_layout(%u, 0, 0, %d, %d)",
	      surface_id, (int)lw, (int)lh);
	if (verbose)
		trace("  surface_id=%u x=0 y=0 width=%d height=%d",
		      surface_id, (int)lw, (int)lh);
	ivi_window_manager_set_surface_layout(wm, surface_id, 0, 0, lw, lh);
	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_wm: roundtrip after set_surface_layout "
			"failed: %s\n", strerror(errno));
		wl_display_disconnect(display);
		return EX_PROTOCOL;
	}
	trace("set_surface_layout sent and flushed");

	/* ---- step 3: visible ---- */
	trace("request ivi_window_manager.set_surface_visible(%u, 1)",
	      surface_id);
	ivi_window_manager_set_surface_visible(wm, surface_id, 1);
	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_wm: roundtrip after set_surface_visible "
			"failed: %s\n", strerror(errno));
		wl_display_disconnect(display);
		return EX_PROTOCOL;
	}
	trace("set_surface_visible(1) sent and flushed");

	/* ---- step 4: foreground on the requested plane ---- */
	trace("request ivi_window_manager.request_fg(%d, %u)", (int)plane,
	      surface_id);
	ivi_window_manager_request_fg(wm, plane, surface_id);
	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_wm: roundtrip after request_fg failed: %s\n",
			strerror(errno));
		wl_display_disconnect(display);
		return EX_PROTOCOL;
	}
	trace("request_fg sent and flushed");

	/*
	 * ivi_window_manager defines no error event and no "done" event, so the
	 * requests above are the whole of the evidence available on this side:
	 * the compositor accepted them and is still answering.
	 */
	trace("done: surface %u layout (0,0,%d,%d), visible 1, fg on plane %d",
	      surface_id, (int)lw, (int)lh, (int)plane);
	trace("this tool cannot observe the panel; visibility is unverified "
	      "here");

	wl_display_flush(display);
	wl_display_disconnect(display);
	return rc;
}
