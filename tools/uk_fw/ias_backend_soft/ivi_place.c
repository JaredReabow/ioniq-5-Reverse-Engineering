/*
 * ivi_place — put an already-created ivi surface on an ivi layer, make it
 * visible, and give it a destination rectangle.
 *
 * WHY THIS EXISTS
 * ---------------
 * On the vehicle the vendor's ApplicationManager is the actor that drives
 * ivi_controller: it looks up the application's surface id, adds it to a layer,
 * sets a rectangle, sets visibility and commits. When the application is
 * started standalone (the only configuration in which we can hand it a forced
 * surface id) no such actor exists, so the client creates a wl_surface, attaches
 * a buffer and commits, and nothing ever puts that surface on a layer that an
 * output composites. This tool is that missing actor, for one surface at a time.
 *
 * WHAT IT DOES, IN ORDER
 * ----------------------
 *   1. wl_display_connect($XDG_RUNTIME_DIR/$WAYLAND_DISPLAY)
 *   2. bind the ivi_controller global, collect the objects it announces
 *      (ivi_controller posts screen/layer/surface for everything that already
 *      exists — that announcement list is how a surface id can be checked
 *      before anything is sent)
 *   3. layer_create(layer-id, w, h, new ivi_controller_layer)
 *      The vendor implementation of this request is create-or-lookup: it tries
 *      ivi_extension_get_layer_from_id() first and only creates the layer when
 *      the lookup fails, so it is safe (and required — there is no other way to
 *      obtain a layer object) to call it for a layer that already exists.
 *   4. surface_create(surface-id, new ivi_controller_surface)
 *      Likewise lookup-only, and this is where the trap is: the vendor
 *      implementation resolves the id with ivi_extension_get_surface_from_id()
 *      and, when that returns NULL, returns silently — no error event, no
 *      resource. So this tool treats "the id was not in the announcement list"
 *      and "no property events arrived on the new object" as a hard failure
 *      instead of blithely sending add_surface() at an object id the compositor
 *      does not have (which would earn a disconnect, not a diagnosis).
 *   5. layer.add_surface(surface)
 *   6. surface.set_destination_rectangle(x, y, w, h)   [layer coordinates]
 *   7. layer.set_destination_rectangle(x, y, w, h)     [screen coordinates]
 *      unless --surface-only
 *   8. surface.set_visibility(1)
 *   9. ivi_controller.commit_changes()
 *  10. one roundtrip and print what the compositor reports back.
 *
 * The surface id must be the id that the client passed to
 * ivi_application.surface_create() — the ivi layout surface id. It is NOT the
 * wl_surface id and not the id of the ivi_controller_surface object. Use
 * `ivi_place --list` against a running compositor to see which ids exist.
 * (For the vendor application the id derives from QT_WAYLAND_SET_SURFACE_ID;
 * AppNavi on the vehicle ends up as ivi surface 30000 from env value 3000.)
 *
 * The protocol code in ivi-controller-protocol.c was generated from
 * ivi-controller.xml, whose provenance and verification are documented there
 * and in the build script. Requests and argument order emitted here:
 *
 *   ivi_controller.commit_changes()
 *   ivi_controller.layer_create(uint id, int w, int h, new_id layer)
 *   ivi_controller.surface_create(uint id, new_id surface)
 *   ivi_controller_layer.add_surface(object surface)
 *   ivi_controller_layer.set_destination_rectangle(int x, int y, int w, int h)
 *   ivi_controller_layer.set_visibility(uint is_visible)
 *   ivi_controller_surface.set_destination_rectangle(int x, int y, int w, int h)
 *   ivi_controller_surface.set_visibility(uint is_visible)
 *
 * This file says nothing about whether the result is visible on the panel.
 * That is a measurement, and not one this program can make.
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
#include "ivi-controller-client-protocol.h"

#define DEFAULT_W        1920
#define DEFAULT_H         720
#define DEFAULT_TIMEOUT  5000
#define IDS_MAX           512

/* exit codes, documented in usage() */
#define EX_OK          0
#define EX_USAGE       1
#define EX_CONNECT     2
#define EX_PROTOCOL    3
#define EX_NO_SURFACE  4
#define EX_NO_LAYER    5

static int verbose;

static void
trace(const char *fmt, ...)
{
	va_list ap;

	fputs("ivi_place: ", stdout);
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

/* ---- small id sets, for the ivi_controller announcement lists ---- */

struct ids {
	uint32_t v[IDS_MAX];
	int n;
	int truncated;
};

static void
ids_add(struct ids *l, uint32_t id)
{
	if (l->n < IDS_MAX)
		l->v[l->n++] = id;
	else
		l->truncated = 1;
}

static int
ids_has(const struct ids *l, uint32_t id)
{
	int i;

	for (i = 0; i < l->n; i++)
		if (l->v[i] == id)
			return 1;
	return 0;
}

static void
ids_print(FILE *f, const struct ids *l)
{
	int i;

	if (l->n == 0) {
		fputs("(none)", f);
	} else {
		for (i = 0; i < l->n; i++)
			fprintf(f, "%s%u", i ? ", " : "", l->v[i]);
	}
	if (l->truncated)
		fputs(" ...", f);
}

/* ---- what we learn about one layer / surface object ---- */

struct obs {
	const char *kind;      /* "layer" or "surface" */
	int events;            /* property events seen on this object */
	int vis_seen;
	int32_t visibility;
	int dest_seen;
	int32_t dx, dy, dw, dh;
	int layer_event_seen;  /* surface only: compositor said which layer */
};

static void
obs_snapshot(const struct obs *o, const char *phase)
{
	if (!o->dest_seen && !o->vis_seen)
		return;
	printf("ivi_place:   %s %s: ", o->kind, phase);
	if (o->vis_seen)
		printf("visibility=%d ", o->visibility);
	if (o->dest_seen)
		printf("destination_rectangle=%d %d %d %d",
		       o->dx, o->dy, o->dw, o->dh);
	printf("\n");
}

/* ---- ivi_controller_layer listener ---- */

static void
layer_visibility(void *data, struct ivi_controller_layer *l, int32_t v)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	o->vis_seen = 1;
	o->visibility = v;
	if (verbose)
		trace("  <- layer.visibility(%d)", v);
}

static void
layer_opacity(void *data, struct ivi_controller_layer *l, wl_fixed_t v)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	if (verbose)
		trace("  <- layer.opacity(%f)", wl_fixed_to_double(v));
}

static void
layer_source_rectangle(void *data, struct ivi_controller_layer *l,
		       int32_t x, int32_t y, int32_t w, int32_t h)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	if (verbose)
		trace("  <- layer.source_rectangle(%d %d %d %d)", x, y, w, h);
}

static void
layer_destination_rectangle(void *data, struct ivi_controller_layer *l,
			    int32_t x, int32_t y, int32_t w, int32_t h)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	o->dest_seen = 1;
	o->dx = x; o->dy = y; o->dw = w; o->dh = h;
	if (verbose)
		trace("  <- layer.destination_rectangle(%d %d %d %d)", x, y, w, h);
}

static void
layer_configuration(void *data, struct ivi_controller_layer *l,
		    int32_t w, int32_t h)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	if (verbose)
		trace("  <- layer.configuration(%d %d)", w, h);
}

static void
layer_orientation(void *data, struct ivi_controller_layer *l, int32_t v)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	if (verbose)
		trace("  <- layer.orientation(%d)", v);
}

static void
layer_screen(void *data, struct ivi_controller_layer *l, void *screen)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	if (verbose)
		trace("  <- layer.screen(%s)", screen ? "screen" : "NULL");
}

static void
layer_destroyed(void *data, struct ivi_controller_layer *l)
{
	struct obs *o = data;

	(void)l;
	o->events++;
	trace("  <- layer.destroyed");
}

static const struct ivi_controller_layer_listener layer_listener = {
	layer_visibility,
	layer_opacity,
	layer_source_rectangle,
	layer_destination_rectangle,
	layer_configuration,
	layer_orientation,
	layer_screen,
	layer_destroyed,
};

/* ---- ivi_controller_surface listener ---- */

static void
surface_visibility(void *data, struct ivi_controller_surface *s, int32_t v)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	o->vis_seen = 1;
	o->visibility = v;
	if (verbose)
		trace("  <- surface.visibility(%d)", v);
}

static void
surface_opacity(void *data, struct ivi_controller_surface *s, wl_fixed_t v)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	if (verbose)
		trace("  <- surface.opacity(%f)", wl_fixed_to_double(v));
}

static void
surface_source_rectangle(void *data, struct ivi_controller_surface *s,
			 int32_t x, int32_t y, int32_t w, int32_t h)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	if (verbose)
		trace("  <- surface.source_rectangle(%d %d %d %d)", x, y, w, h);
}

static void
surface_destination_rectangle(void *data, struct ivi_controller_surface *s,
			      int32_t x, int32_t y, int32_t w, int32_t h)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	o->dest_seen = 1;
	o->dx = x; o->dy = y; o->dw = w; o->dh = h;
	if (verbose)
		trace("  <- surface.destination_rectangle(%d %d %d %d)", x, y, w, h);
}

static void
surface_configuration(void *data, struct ivi_controller_surface *s,
		      int32_t w, int32_t h)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	if (verbose)
		trace("  <- surface.configuration(%d %d)", w, h);
}

static void
surface_orientation(void *data, struct ivi_controller_surface *s, int32_t v)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	if (verbose)
		trace("  <- surface.orientation(%d)", v);
}

static void
surface_pixelformat(void *data, struct ivi_controller_surface *s, int32_t v)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	if (verbose)
		trace("  <- surface.pixelformat(%d)", v);
}

static void
surface_layer(void *data, struct ivi_controller_surface *s,
	      struct ivi_controller_layer *layer)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	o->layer_event_seen = 1;
	if (verbose)
		trace("  <- surface.layer(%s)", layer ? "layer" : "NULL");
}

static void
surface_stats(void *data, struct ivi_controller_surface *s,
	      uint32_t a, uint32_t b, uint32_t c, uint32_t d, const char *name)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	if (verbose)
		trace("  <- surface.stats(%u %u %u %u %s)", a, b, c, d,
		      name ? name : "(null)");
}

static void
surface_destroyed(void *data, struct ivi_controller_surface *s)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	trace("  <- surface.destroyed");
}

static void
surface_content(void *data, struct ivi_controller_surface *s, int32_t v)
{
	struct obs *o = data;

	(void)s;
	o->events++;
	if (verbose)
		trace("  <- surface.content(%d)", v);
}

static const struct ivi_controller_surface_listener surface_listener = {
	surface_visibility,
	surface_opacity,
	surface_source_rectangle,
	surface_destination_rectangle,
	surface_configuration,
	surface_orientation,
	surface_pixelformat,
	surface_layer,
	surface_stats,
	surface_destroyed,
	surface_content,
};

/* ---- wl_registry ---- */

static struct ivi_controller *controller;
static struct ids layers, surfaces, screens;
static int controller_global_name;
static int protocol_error_seen;

static void
controller_screen(void *data, struct ivi_controller *c,
		  uint32_t id_screen, struct ivi_controller_screen *id)
{
	(void)data; (void)c; (void)id;
	ids_add(&screens, id_screen);
}

static void
controller_layer(void *data, struct ivi_controller *c, uint32_t id_layer)
{
	(void)data; (void)c;
	ids_add(&layers, id_layer);
}

static void
controller_surface(void *data, struct ivi_controller *c, uint32_t id_surface)
{
	(void)data; (void)c;
	ids_add(&surfaces, id_surface);
}

static void
controller_error(void *data, struct ivi_controller *c, int32_t object_id,
		 int32_t object_type, int32_t error, const char *message)
{
	(void)data; (void)c;
	protocol_error_seen = 1;
	fprintf(stderr,
		"ivi_place: ivi_controller.error: object_id=%d object_type=%d "
		"error=%d message=%s\n",
		object_id, object_type, error, message ? message : "(null)");
}

static const struct ivi_controller_listener controller_listener = {
	controller_screen,
	controller_layer,
	controller_surface,
	controller_error,
};

struct global_names {
	const char *name;
	int seen;
	int version;
};

static struct global_names interesting[] = {
	{ "ivi_application",     0, 0 },
	{ "ivi_window_manager",  0, 0 },
	{ "ivi_hmi_requester",   0, 0 },
	{ "ivi_info_requester",  0, 0 },
	{ "ivi_share",           0, 0 },
	{ "ivi_controller",      0, 0 },
};

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

	if (strcmp(interface, "ivi_controller") == 0 && !controller) {
		controller = wl_registry_bind(registry, name,
					      &ivi_controller_interface,
					      version < 1 ? version : 1);
		controller_global_name = (int)name;
		ivi_controller_add_listener(controller, &controller_listener,
					    NULL);
		return;
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
 * wl_display_roundtrip() has no timeout, and a compositor that has stopped
 * answering would hang a research tool silently. This is the same roundtrip
 * with a deadline; ETIMEDOUT is reported rather than waited out.
 */
static int
roundtrip_timeout(struct wl_display *display, int timeout_ms)
{
	struct wl_callback *cb;
	int64_t deadline = now_ms() + timeout_ms;

	cb = wl_display_sync(display);
	if (!cb) {
		fprintf(stderr, "ivi_place: wl_display_sync: %s\n",
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
"usage: %s [options] <surface-id> <layer-id> [x y w h]\n"
"       %s [options] --list\n"
"\n"
"Place an existing ivi surface on an ivi layer: add it to the layer, set the\n"
"destination rectangle (default %d %d %d %d), set it visible and commit the\n"
"layout through the vendor ivi_controller protocol.\n"
"\n"
"  <surface-id> is the ivi layout surface id the client passed to\n"
"               ivi_application.surface_create() — not the wl_surface id and not\n"
"               the ivi_controller_surface object id. `--list` prints the ids\n"
"               the compositor knows about.\n"
"  <layer-id>   1000 base, 2000 workspace background, 3000 workspace,\n"
"               4000 application (the ids in this configuration).\n"
"\n"
"options:\n"
"  --list              bind ivi_controller, print the globals and the ids it\n"
"                      announces, change nothing, exit.\n"
"  --surface-only      set the rectangle and visibility on the surface only;\n"
"                      leave the layer's own geometry and visibility alone.\n"
"  --visibility N      value for surface.set_visibility (default 1).\n"
"  --timeout MS        per-roundtrip deadline, default %d.\n"
"  -v, --verbose       also print every property event read back.\n"
"  -h, --help          this text.\n"
"\n"
"exit status: 0 ok, 1 usage, 2 no display/ivi_controller, 3 protocol error,\n"
"             4 surface id unknown to the compositor, 5 layer unusable.\n",
		argv0, argv0, 0, 0, DEFAULT_W, DEFAULT_H, DEFAULT_TIMEOUT);
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
	struct ivi_controller_layer *layer = NULL;
	struct ivi_controller_surface *surface = NULL;
	struct obs layer_obs = { .kind = "layer" };
	struct obs surface_obs = { .kind = "surface" };
	uint32_t surface_id = 0, layer_id = 0;
	int32_t rx = 0, ry = 0, rw = DEFAULT_W, rh = DEFAULT_H;
	int have_surface_id = 0, have_layer_id = 0;
	int list_only = 0, surface_only = 0;
	uint32_t visibility = 1;
	int timeout_ms = DEFAULT_TIMEOUT;
	int positional[6];
	int npos = 0;
	int i, rc, layer_existed, surface_announced;
	const char *runtime_dir, *wl_display_name;

	for (i = 1; i < argc; i++) {
		const char *a = argv[i];

		if (strcmp(a, "-h") == 0 || strcmp(a, "--help") == 0) {
			usage(stdout, argv[0]);
			return EX_OK;
		} else if (strcmp(a, "--list") == 0) {
			list_only = 1;
		} else if (strcmp(a, "--surface-only") == 0) {
			surface_only = 1;
		} else if (strcmp(a, "-v") == 0 || strcmp(a, "--verbose") == 0) {
			verbose = 1;
		} else if (strcmp(a, "--visibility") == 0 && i + 1 < argc) {
			if (parse_uint(argv[++i], &visibility) < 0) {
				fprintf(stderr, "ivi_place: bad --visibility value\n");
				return EX_USAGE;
			}
		} else if (strcmp(a, "--timeout") == 0 && i + 1 < argc) {
			uint32_t t;

			if (parse_uint(argv[++i], &t) < 0 || t == 0) {
				fprintf(stderr, "ivi_place: bad --timeout value\n");
				return EX_USAGE;
			}
			timeout_ms = (int)t;
		} else if (a[0] == '-' && a[1] != '\0') {
			fprintf(stderr, "ivi_place: unknown option %s\n", a);
			usage(stderr, argv[0]);
			return EX_USAGE;
		} else {
			if (npos >= 6) {
				fprintf(stderr, "ivi_place: too many arguments\n");
				return EX_USAGE;
			}
			positional[npos++] = i;
		}
	}

	if (!list_only) {
		if (npos != 2 && npos != 6) {
			usage(stderr, argv[0]);
			return EX_USAGE;
		}
		if (parse_uint(argv[positional[0]], &surface_id) < 0) {
			fprintf(stderr, "ivi_place: bad surface id '%s'\n",
				argv[positional[0]]);
			return EX_USAGE;
		}
		if (parse_uint(argv[positional[1]], &layer_id) < 0) {
			fprintf(stderr, "ivi_place: bad layer id '%s'\n",
				argv[positional[1]]);
			return EX_USAGE;
		}
		have_surface_id = 1;
		have_layer_id = 1;
		if (npos == 6) {
			if (parse_int32(argv[positional[2]], &rx) < 0 ||
			    parse_int32(argv[positional[3]], &ry) < 0 ||
			    parse_int32(argv[positional[4]], &rw) < 0 ||
			    parse_int32(argv[positional[5]], &rh) < 0) {
				fprintf(stderr, "ivi_place: bad rectangle\n");
				return EX_USAGE;
			}
			if (rw <= 0 || rh <= 0) {
				/* weston's ivi-layout rejects a non-positive
				 * destination rectangle */
				fprintf(stderr, "ivi_place: rectangle must have a "
					"positive width and height, got %d x %d\n",
					(int)rw, (int)rh);
				return EX_USAGE;
			}
		}
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
			"ivi_place: cannot connect to the wayland display: %s\n"
			"ivi_place: set XDG_RUNTIME_DIR (and WAYLAND_DISPLAY if not "
			"wayland-0)\n", strerror(errno));
		return EX_CONNECT;
	}

	registry = wl_display_get_registry(display);
	wl_registry_add_listener(registry, &registry_listener, NULL);

	/* first roundtrip: globals; ivi_controller also announces its objects */
	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_place: registry roundtrip failed: %s\n",
			strerror(errno));
		wl_display_disconnect(display);
		return EX_CONNECT;
	}

	if (!controller) {
		fprintf(stderr, "ivi_place: the compositor advertises no "
			"ivi_controller global\n");
		for (i = 0; i < (int)(sizeof(interesting) / sizeof(interesting[0])); i++)
			fprintf(stderr, "ivi_place:   %s: %s (version %d)\n",
				interesting[i].name,
				interesting[i].seen ? "present" : "absent",
				interesting[i].version);
		wl_display_disconnect(display);
		return EX_CONNECT;
	}

	trace("bound ivi_controller (registry name %d, version 1)",
	      controller_global_name);
	printf("ivi_place: announced by ivi_controller: %d layers, %d surfaces, "
	       "%d screens\n", layers.n, surfaces.n, screens.n);

	if (list_only) {
		for (i = 0; i < (int)(sizeof(interesting) / sizeof(interesting[0])); i++)
			trace("  global %-20s %s (version %d)",
			      interesting[i].name,
			      interesting[i].seen ? "present" : "absent",
			      interesting[i].version);
		printf("ivi_place: layer ids:   "); ids_print(stdout, &layers); printf("\n");
		printf("ivi_place: surface ids: "); ids_print(stdout, &surfaces); printf("\n");
		printf("ivi_place: screen ids:  "); ids_print(stdout, &screens); printf("\n");
		printf("ivi_place: nothing changed\n");
		wl_display_disconnect(display);
		return EX_OK;
	}

	if (!have_surface_id || !have_layer_id) {
		usage(stderr, argv[0]);
		wl_display_disconnect(display);
		return EX_USAGE;
	}

	surface_announced = ids_has(&surfaces, surface_id);
	layer_existed = ids_has(&layers, layer_id);

	/* ---- layer: create-or-lookup ---- */
	trace("request ivi_controller.layer_create(%u, %d, %d, new "
	      "ivi_controller_layer)", layer_id, (int)rw, (int)rh);
	layer = ivi_controller_layer_create(controller, layer_id, rw, rh);
	if (!layer) {
		fprintf(stderr, "ivi_place: could not create the layer proxy\n");
		wl_display_disconnect(display);
		return EX_NO_LAYER;
	}
	ivi_controller_layer_add_listener(layer, &layer_listener, &layer_obs);

	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_place: roundtrip after layer_create "
			"failed: %s\n", strerror(errno));
		wl_display_disconnect(display);
		return EX_PROTOCOL;
	}

	if (layer_obs.events == 0 || protocol_error_seen) {
		fprintf(stderr,
			"ivi_place: layer %u: the compositor sent no layer "
			"properties for the new object, so the layer does not "
			"exist and was not created\n", layer_id);
		wl_display_disconnect(display);
		return EX_NO_LAYER;
	}

	trace("layer %u %s", layer_id,
	      layer_existed ? "already existed (handle only)"
			    : "did not exist and was created");
	obs_snapshot(&layer_obs, "at create");

	/* ---- surface: lookup only ---- */
	if (!surface_announced) {
		fprintf(stderr,
			"ivi_place: surface %u is not one of the %d ivi surfaces "
			"the compositor announced; ivi_controller.surface_create() "
			"is a lookup, not a create, and fails silently for an "
			"unknown id\n", surface_id, surfaces.n);
		fprintf(stderr, "ivi_place: announced surface ids: ");
		ids_print(stderr, &surfaces);
		fprintf(stderr, "\n");
		fprintf(stderr,
			"ivi_place: the id to pass is the one the client gave to "
			"ivi_application.surface_create(); look for "
			"'ivi_application.surface_create(<id>, ...)' in the "
			"client's WAYLAND_DEBUG output\n");
		wl_display_disconnect(display);
		return EX_NO_SURFACE;
	}

	trace("request ivi_controller.surface_create(%u, new "
	      "ivi_controller_surface)", surface_id);
	surface = ivi_controller_surface_create(controller, surface_id);
	if (!surface) {
		fprintf(stderr, "ivi_place: could not create the surface proxy\n");
		wl_display_disconnect(display);
		return EX_NO_SURFACE;
	}
	ivi_controller_surface_add_listener(surface, &surface_listener,
					    &surface_obs);

	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_place: roundtrip after surface_create "
			"failed: %s\n", strerror(errno));
		wl_display_disconnect(display);
		return EX_PROTOCOL;
	}

	if (surface_obs.events == 0 || protocol_error_seen) {
		fprintf(stderr,
			"ivi_place: surface %u was announced but sent no "
			"properties; the compositor object does not exist\n",
			surface_id);
		wl_display_disconnect(display);
		return EX_NO_SURFACE;
	}
	trace("surface %u exists", surface_id);
	obs_snapshot(&surface_obs, "at create");

	/* ---- the actual placement ---- */
	trace("request ivi_controller_layer.add_surface(layer %u, surface %u)",
	      layer_id, surface_id);
	ivi_controller_layer_add_surface(layer, surface);

	trace("request ivi_controller_surface.set_destination_rectangle"
	      "(%d, %d, %d, %d)", (int)rx, (int)ry, (int)rw, (int)rh);
	ivi_controller_surface_set_destination_rectangle(surface, rx, ry, rw, rh);

	if (!surface_only) {
		trace("request ivi_controller_layer.set_destination_rectangle"
		      "(%d, %d, %d, %d)", (int)rx, (int)ry, (int)rw, (int)rh);
		ivi_controller_layer_set_destination_rectangle(layer, rx, ry,
							       rw, rh);
	}

	trace("request ivi_controller_surface.set_visibility(%u)", visibility);
	ivi_controller_surface_set_visibility(surface, visibility);

	if (!surface_only) {
		trace("request ivi_controller_layer.set_visibility(%u)",
		      visibility);
		ivi_controller_layer_set_visibility(layer, visibility);
	}

	trace("request ivi_controller.commit_changes()");
	ivi_controller_commit_changes(controller);

	if (roundtrip_timeout(display, timeout_ms) < 0) {
		fprintf(stderr, "ivi_place: roundtrip after commit_changes "
			"failed: %s\n", strerror(errno));
		wl_display_disconnect(display);
		return EX_PROTOCOL;
	}

	if (protocol_error_seen) {
		fprintf(stderr, "ivi_place: the compositor posted an "
			"ivi_controller error; see above\n");
		wl_display_disconnect(display);
		return EX_PROTOCOL;
	}

	/* ---- report what the compositor echoed back ---- */
	obs_snapshot(&layer_obs, "after commit");
	obs_snapshot(&surface_obs, "after commit");
	trace("surface %u is now on layer %u%s", surface_id, layer_id,
	      surface_obs.layer_event_seen ? " (compositor confirmed the layer)"
					   : "");

	rc = EX_OK;
	if (surface_obs.vis_seen && surface_obs.visibility != (int32_t)visibility) {
		fprintf(stderr,
			"ivi_place: warning: asked for surface visibility %u but "
			"the compositor reports %d\n",
			visibility, surface_obs.visibility);
		rc = EX_PROTOCOL;
	}

	wl_display_flush(display);
	wl_display_disconnect(display);
	return rc;
}
