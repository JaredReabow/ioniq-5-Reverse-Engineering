/*
 * ias-shot — capture one frame of the Gen5W HMI through weston_screenshooter.
 *
 * Guest-side capture client for the softbackend compositor. Binds wl_compositor,
 * wl_shm, the first wl_output and weston_screenshooter, creates a 1920x720
 * WL_SHM_FORMAT_ARGB8888 buffer, sends shoot(), waits for done(), and writes the
 * frame as binary PPM (P6, RGB) so no image library is needed on either side.
 *
 * Built host-side with tools/uk_fw/ias_backend_soft/build-shot.sh against the
 * guest's own libwayland-client; the protocol headers are generated in the guest
 * by the image's wayland-scanner (see README).
 */
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>

#include <wayland-client.h>
#include "weston-screenshooter-client-protocol.h"
#include "wayland-client-protocol.h"

/* The compositor's output is not guaranteed to be 1920x720: with the vendor
 * configuration it reported a surface of 1926x753, and capturing that into a
 * hard-coded 1920x720 buffer shears every row by the difference. The size is taken
 * from the wl_output mode event instead, with these values only as a fallback if no
 * mode arrives. */
#define OUT_W_DEFAULT 1920
#define OUT_H_DEFAULT 720
static int out_w = OUT_W_DEFAULT;
static int out_h = OUT_H_DEFAULT;
#define OUT_STRIDE (out_w * 4)
#define OUT_SIZE ((size_t)OUT_STRIDE * out_h)
#define WAIT_MS 20000

static struct wl_shm *shm;
static struct wl_output *output;
/* The vendor stack places an application on a specific IVI screen (the home screen sits
 * on screen 9 in this configuration), and the screenshooter captures whichever wl_output
 * it is asked for. Binding only the first output therefore captures output 0 and reports
 * an empty screen. All outputs are bound and one is selected by index from argv. */
#define MAX_OUTPUTS 32
static struct wl_output *outputs[MAX_OUTPUTS];
static int output_count;
static int out_index;
static struct weston_screenshooter *shooter;
static int shoot_done;
static int done_events;

static void
shooter_done(void *data, struct weston_screenshooter *s)
{
	(void)data;
	(void)s;
	done_events++;
	shoot_done = 1;
}

static const struct weston_screenshooter_listener shooter_listener = {
	shooter_done
};

static void
output_handle_geometry(void *data, struct wl_output *o, int32_t x, int32_t y,
		       int32_t pw, int32_t ph, int32_t subpixel,
		       const char *make, const char *model, int32_t transform)
{
	(void)data; (void)o; (void)x; (void)y; (void)pw; (void)ph;
	(void)subpixel; (void)make; (void)model; (void)transform;
}

static void
output_handle_mode(void *data, struct wl_output *o, uint32_t flags,
		   int32_t width, int32_t height, int32_t refresh)
{
	(void)data; (void)o; (void)flags; (void)refresh;
	if (width > 0 && height > 0) {
		out_w = width;
		out_h = height;
	}
}

static void
output_handle_done(void *data, struct wl_output *o) { (void)data; (void)o; }
static void
output_handle_scale(void *data, struct wl_output *o, int32_t f)
{ (void)data; (void)o; (void)f; }

static const struct wl_output_listener output_listener = {
	output_handle_geometry,
	output_handle_mode,
	output_handle_done,
	output_handle_scale,
};

static void
registry_global(void *data, struct wl_registry *registry, uint32_t name,
		const char *interface, uint32_t version)
{
	(void)data;
	if (strcmp(interface, "wl_compositor") == 0)
		wl_registry_bind(registry, name, &wl_compositor_interface,
				 version < 3 ? version : 3);
	else if (strcmp(interface, "wl_shm") == 0)
		shm = wl_registry_bind(registry, name, &wl_shm_interface, 1);
	else if (strcmp(interface, "wl_output") == 0) {
		if (output_count < MAX_OUTPUTS) {
			struct wl_output *o = wl_registry_bind(registry, name,
							       &wl_output_interface,
							       version < 2 ? version : 2);
			wl_output_add_listener(o, &output_listener, NULL);
			outputs[output_count++] = o;
		}
	} else if (strcmp(interface, "weston_screenshooter") == 0) {
		shooter = wl_registry_bind(registry, name,
					   &weston_screenshooter_interface, 1);
		weston_screenshooter_add_listener(shooter, &shooter_listener, NULL);
	}
}

static void
registry_global_remove(void *data, struct wl_registry *registry, uint32_t name)
{
	(void)data;
	(void)registry;
	(void)name;
}

static const struct wl_registry_listener registry_listener = {
	registry_global,
	registry_global_remove
};

static int
create_shm_buffer(struct wl_buffer **out, void **data)
{
	char name[] = "/tmp/ias-shot-XXXXXX";
	int fd = mkstemp(name);
	if (fd < 0) {
		fprintf(stderr, "ias-shot: mkstemp: %s\n", strerror(errno));
		return -1;
	}
	unlink(name);
	if (ftruncate(fd, (off_t)OUT_SIZE) < 0) {
		fprintf(stderr, "ias-shot: ftruncate: %s\n", strerror(errno));
		close(fd);
		return -1;
	}
	void *p = mmap(NULL, OUT_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
	if (p == MAP_FAILED) {
		fprintf(stderr, "ias-shot: mmap: %s\n", strerror(errno));
		close(fd);
		return -1;
	}
	struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, (int)OUT_SIZE);
	*out = wl_shm_pool_create_buffer(pool, 0, out_w, out_h, OUT_STRIDE,
					 WL_SHM_FORMAT_ARGB8888);
	wl_shm_pool_destroy(pool);
	close(fd);
	if (!*out) {
		fprintf(stderr, "ias-shot: wl_shm_pool_create_buffer failed\n");
		return -1;
	}
	*data = p;
	return 0;
}

int
main(int argc, char **argv)
{
	const char *path = argc > 1 ? argv[1] : "/tmp/shot.ppm";
	out_index = argc > 2 ? atoi(argv[2]) : 0;

	struct wl_display *display = wl_display_connect(NULL);
	if (!display) {
		fprintf(stderr, "ias-shot: cannot connect to wayland display\n");
		return 2;
	}
	struct wl_registry *registry = wl_display_get_registry(display);
	wl_registry_add_listener(registry, &registry_listener, NULL);
	if (wl_display_roundtrip(display) < 0) {
		fprintf(stderr, "ias-shot: registry roundtrip failed\n");
		return 3;
	}
	/* A second roundtrip delivers the output's mode so the buffer matches it. */
	if (wl_display_roundtrip(display) < 0) {
		fprintf(stderr, "ias-shot: output roundtrip failed\n");
		return 3;
	}
	if (out_index < 0)
		out_index = 0;
	if (out_index >= output_count)
		out_index = output_count - 1;
	output = (output_count > 0) ? outputs[out_index] : NULL;
	fprintf(stderr, "ias-shot: %d output(s) bound, capturing index %d\n",
		output_count, out_index);
	if (!shm || !output || !shooter) {
		fprintf(stderr, "ias-shot: missing global shm=%p output=%p screenshooter=%p\n",
			(void *)shm, (void *)output, (void *)shooter);
		return 4;
	}

	struct wl_buffer *buffer = NULL;
	void *pixels = NULL;
	if (create_shm_buffer(&buffer, &pixels) < 0)
		return 5;

	fprintf(stderr, "ias-shot: shooting %dx%d ARGB8888\n", out_w, out_h);
	weston_screenshooter_shoot(shooter, output, buffer);
	if (wl_display_flush(display) < 0) {
		fprintf(stderr, "ias-shot: flush failed: %s\n", strerror(errno));
		return 6;
	}

	struct pollfd pfd = { .fd = wl_display_get_fd(display), .events = POLLIN };
	struct timespec t0, tn;
	clock_gettime(CLOCK_MONOTONIC, &t0);
	while (!shoot_done) {
		clock_gettime(CLOCK_MONOTONIC, &tn);
		long elapsed = (tn.tv_sec - t0.tv_sec) * 1000L +
			       (tn.tv_nsec - t0.tv_nsec) / 1000000L;
		if (elapsed >= WAIT_MS) {
			fprintf(stderr, "ias-shot: timeout waiting for done\n");
			return 7;
		}
		int rc = poll(&pfd, 1, (int)(WAIT_MS - elapsed));
		if (rc < 0 && errno == EINTR)
			continue;
		if (rc <= 0) {
			fprintf(stderr, "ias-shot: poll timeout waiting for done\n");
			return 7;
		}
		if (wl_display_dispatch(display) < 0) {
			fprintf(stderr, "ias-shot: protocol error: %s\n",
				strerror(errno));
			return 8;
		}
	}
	if (!shoot_done) {
		fprintf(stderr, "ias-shot: no done event\n");
		return 9;
	}

	FILE *f = fopen(path, "wb");
	if (!f) {
		fprintf(stderr, "ias-shot: cannot open %s: %s\n", path,
			strerror(errno));
		return 10;
	}
	fprintf(f, "P6\n%d %d\n255\n", out_w, out_h);
	unsigned char *src = pixels;
	unsigned char *row = malloc((size_t)out_w * 3);
	if (!row)
		return 11;
	uint64_t sum[3] = { 0, 0, 0 };
	unsigned char lo[3] = { 255, 255, 255 }, hi[3] = { 0, 0, 0 };
	for (int y = 0; y < out_h; y++) {
		unsigned char *s = src + (size_t)y * OUT_STRIDE;
		for (int x = 0; x < out_w; x++) {
			/* shm ARGB8888 is little-endian B,G,R,A in memory */
			row[x * 3 + 0] = s[2];
			row[x * 3 + 1] = s[1];
			row[x * 3 + 2] = s[0];
			for (int c = 0; c < 3; c++) {
				unsigned char v = row[x * 3 + c];
				sum[c] += v;
				if (v < lo[c]) lo[c] = v;
				if (v > hi[c]) hi[c] = v;
			}
			s += 4;
		}
		if (fwrite(row, 1, (size_t)out_w * 3, f) != (size_t)out_w * 3) {
			fprintf(stderr, "ias-shot: write failed\n");
			fclose(f);
			return 12;
		}
	}
	if (fclose(f) != 0) {
		fprintf(stderr, "ias-shot: close failed\n");
		return 13;
	}
	const double npx = (double)out_w * out_h;
	fprintf(stderr,
		"ias-shot: wrote %s (%zu bytes), done_events=%d, mean R=%.1f G=%.1f B=%.1f, "
		"R[%u..%u] G[%u..%u] B[%u..%u]\n",
		path, (size_t)(15 + OUT_SIZE / 3 * 3), done_events,
		sum[0] / npx, sum[1] / npx, sum[2] / npx,
		lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]);
	wl_display_disconnect(display);
	return 0;
}
