/*
 * Copyright © 2010-2011 Benjamin Franzke
 * Copyright © 2012 Intel Corporation
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice (including the
 * next paragraph) shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include "config.h"

#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <stdbool.h>
#include <stdio.h>

#include "shared/helpers.h"
#include "compositor.h"
#include "pixman-renderer.h"
#include "presentation_timing-server-protocol.h"

void ias_publish(struct wl_display *display);

struct headless_backend {
	struct weston_backend base;
	struct weston_compositor *compositor;
	struct weston_seat fake_seat;
	bool use_pixman;
};

struct headless_output {
	struct weston_output base;
	struct weston_mode mode;
	struct wl_event_source *finish_frame_timer;
	uint32_t *image_buf;
	pixman_image_t *image;
	int repaint_count;
};

struct headless_parameters {
	int width;
	int height;
	int use_pixman;
	uint32_t transform;
	/* How many outputs to create. ivi-shell numbers its screens by position in
	 * the compositor output list, so screen N needs N+1 outputs. */
	int count;
};

static void
headless_output_start_repaint_loop(struct weston_output *output)
{
	struct timespec ts;

	weston_compositor_read_presentation_clock(output->compositor, &ts);
	weston_output_finish_frame(output, &ts, PRESENTATION_FEEDBACK_INVALID);
}

static int
finish_frame_handler(void *data)
{
	struct headless_output *output = data;
	struct timespec ts;

	weston_compositor_read_presentation_clock(output->base.compositor, &ts);
	weston_output_finish_frame(&output->base, &ts, 0);

	return 1;
}

static int
headless_output_repaint(struct weston_output *output_base,
		       pixman_region32_t *damage)
{
	struct headless_output *output = (struct headless_output *) output_base;
	struct weston_compositor *ec = output->base.compositor;
	static int last_views = -1;
	int views = wl_list_length(&ec->view_list);
	int repaint_count = output->repaint_count++;

	/* Diagnostic: distinguish "nothing to draw" from "drawn but not captured". */
	if (views != last_views || repaint_count < 5) {
		last_views = views;
		weston_log("ias-soft: repaint output=%u views=%d layers=%d\n",
			   output->base.id, views,
			   wl_list_length(&ec->layer_list));
	}

	ec->renderer->repaint_output(&output->base, damage);

	/* Diagnostic: write a downscaled PPM of the backend framebuffer. Small enough to
	 * move out of the guest over the serial link without truncation. */
	if (output->image_buf && repaint_count < 10) {
		static char path[64];
		const int sw = 240, sh = 90;
		int w = output->base.current_mode->width;
		int h = output->base.current_mode->height;
		const unsigned char *src = output->image_buf;

		/* Per output, otherwise N outputs overwrite each other's dump. */
		snprintf(path, sizeof path, "/tmp/fb-%u-%d.ppm",
			 output->base.id, repaint_count);
		{
			FILE *f = fopen(path, "wb");
			if (f) {
				fprintf(f, "P6\n%d %d\n255\n", sw, sh);
				for (int y = 0; y < sh; y++)
					for (int x = 0; x < sw; x++) {
						size_t o = ((size_t)(y * h / sh) * w + (x * w / sw)) * 4;
						unsigned char bgr[3] = { src[o+2], src[o+1], src[o+0] };
						fwrite(bgr, 1, 3, f);
					}
				fclose(f);
				weston_log("ias-soft: dumped %s\n", path);
			}
		}
	}

	pixman_region32_subtract(&ec->primary_plane.damage,
				 &ec->primary_plane.damage, damage);

	wl_event_source_timer_update(output->finish_frame_timer, 16);

	return 0;
}

static void
headless_output_destroy(struct weston_output *output_base)
{
	struct headless_output *output = (struct headless_output *) output_base;
	struct headless_backend *b =
			(struct headless_backend *) output->base.compositor->backend;

	wl_event_source_remove(output->finish_frame_timer);

	if (b->use_pixman) {
		pixman_renderer_output_destroy(&output->base);
		pixman_image_unref(output->image);
		free(output->image_buf);
	}

	weston_output_destroy(&output->base);

	free(output);

	return;
}

static int
headless_backend_create_output(struct headless_backend *b,
			       struct headless_parameters *param,
			       int index)
{
	struct weston_compositor *c = b->compositor;
	struct headless_output *output;
	struct wl_event_loop *loop;
	char name[32];

	output = zalloc(sizeof *output);
	if (output == NULL)
		return -1;

	/* Give every output a distinct name: the output is identified by name in
	 * logs and by the screenshooter, and duplicate names would make a
	 * multi-output run unreadable. weston_output_destroy() frees this. */
	snprintf(name, sizeof name, "IAS-%d", index);
	output->base.name = strdup(name);

	output->mode.flags =
		WL_OUTPUT_MODE_CURRENT | WL_OUTPUT_MODE_PREFERRED;
	output->mode.width = param->width;
	output->mode.height = param->height;
	output->mode.refresh = 60000;
	wl_list_init(&output->base.mode_list);
	wl_list_insert(&output->base.mode_list, &output->mode.link);

	output->base.current_mode = &output->mode;
	/* Nail the outputs side by side instead of stacking them at (0,0):
	 * ivi-layout offsets a layer's destination by output->x/y, so overlapping
	 * outputs would draw every screen's content on every output. Laid out
	 * left to right, each output owns a disjoint global region and holds only
	 * the surfaces the ivi-shell assigned to that screen. */
	weston_output_init(&output->base, c, index * param->width, 0,
			   param->width, param->height, param->transform, 1);

	output->base.make = "gen5w";
	output->base.model = "HDMI1";

	loop = wl_display_get_event_loop(c->wl_display);
	output->finish_frame_timer =
		wl_event_loop_add_timer(loop, finish_frame_handler, output);

	output->base.start_repaint_loop = headless_output_start_repaint_loop;
	output->base.repaint = headless_output_repaint;
	output->base.destroy = headless_output_destroy;
	output->base.assign_planes = NULL;
	output->base.set_backlight = NULL;
	output->base.set_dpms = NULL;
	output->base.switch_mode = NULL;

	if (b->use_pixman) {
		output->image_buf = malloc(param->width * param->height * 4);
		if (!output->image_buf)
			return -1;

		output->image = pixman_image_create_bits(PIXMAN_x8r8g8b8,
							 param->width,
							 param->height,
							 output->image_buf,
							 param->width * 4);

		if (pixman_renderer_output_create(&output->base) < 0)
			return -1;

		pixman_renderer_output_set_buffer(&output->base,
						  output->image);
	}

	weston_compositor_add_output(c, &output->base);

	return 0;
}

static int
headless_input_create(struct headless_backend *b)
{
	weston_seat_init(&b->fake_seat, b->compositor, "default");

	weston_seat_init_pointer(&b->fake_seat);

	if (weston_seat_init_keyboard(&b->fake_seat, NULL) < 0)
		return -1;

	return 0;
}

static void
headless_input_destroy(struct headless_backend *b)
{
	weston_seat_release(&b->fake_seat);
}

static void
headless_restore(struct weston_compositor *ec)
{
}

static void
headless_destroy(struct weston_compositor *ec)
{
	struct headless_backend *b = (struct headless_backend *) ec->backend;

	headless_input_destroy(b);
	weston_compositor_shutdown(ec);

	free(b);
}

static struct headless_backend *
headless_backend_create(struct weston_compositor *compositor,
			struct headless_parameters *param,
			const char *display_name)
{
	struct headless_backend *b;
	int i;

	b = zalloc(sizeof *b);
	if (b == NULL)
		return NULL;

	b->compositor = compositor;
	if (weston_compositor_set_presentation_clock_software(compositor) < 0)
		goto err_free;

	if (headless_input_create(b) < 0)
		goto err_free;

	b->base.destroy = headless_destroy;
	b->base.restore = headless_restore;

	b->use_pixman = param->use_pixman;
	if (b->use_pixman) {
		pixman_renderer_init(compositor);
	}

	/* Outputs are appended to compositor->output_list in creation order, and
	 * ivi-shell's create_screen() walks that list assigning
	 * iviscrn->id_screen = position. So creating them here in index order is
	 * what makes screen 0..count-1 come out in that order. */
	for (i = 0; i < param->count; i++) {
		if (headless_backend_create_output(b, param, i) < 0) {
			weston_log("ias-soft: failed to create output %d of %d\n",
				   i, param->count);
			/* Nothing to fall back on, and no list for ivi-shell to
			 * number. */
			if (i == 0)
				goto err_input;
			/* Keep the outputs that did come up: screens 0..i-1 are
			 * still numbered as expected, just fewer of them. */
			break;
		}
	}

	if (!b->use_pixman && noop_renderer_init(compositor) < 0)
		goto err_input;

	compositor->backend = &b->base;
	return b;

err_input:
	weston_compositor_shutdown(compositor);
	headless_input_destroy(b);
err_free:
	free(b);
	return NULL;
}


/* ---- research shim: place surfaces the missing IAS layout plugin would place ----
 * grid_layout.so is absent from the image, so ias-shell never creates views and the
 * compositor has nothing to draw. For the research build only, create a view for every
 * new surface and put it on the output. This is a shim, not vendor behaviour. */
static int shim_mapped;

static void
shim_on_create_surface(struct wl_listener *listener, void *data)
{
	struct weston_surface *ws = data;
	struct weston_compositor *ec = ws->compositor;
	struct weston_view *v;

	(void) listener;
	v = weston_view_create(ws);
	if (!v)
		return;
	weston_view_set_position(v, 0, 0);
	weston_layer_entry_insert(&ec->cursor_layer.view_list, &v->layer_link);
	weston_view_update_transform(v);
	weston_compositor_schedule_repaint(ec);
	shim_mapped++;
	weston_log("ias-soft: shim mapped surface %p (%d total)\n", (void *) ws, shim_mapped);
}

static struct wl_listener shim_create_surface_listener = {
	.notify = shim_on_create_surface,
};

/* The vendor ivi-shell assigns screen ids by output-list position, so IVI screen
 * 9 exists only when there are at least ten outputs. weston 1.10's headless
 * backend has no --output-count option and the vendor ivi-shell.so has no
 * configurable screen id, so the count is selected here at runtime. Default 1
 * keeps the single-output geometry and behaviour of every earlier run. */
static int
headless_output_count(void)
{
	const char *env = getenv("IAS_OUTPUT_COUNT");
	char *end = NULL;
	long count;

	if (env == NULL || *env == '\0')
		return 1;

	count = strtol(env, &end, 10);
	if (end == NULL || *end != '\0' || count < 1) {
		weston_log("ias-soft: invalid IAS_OUTPUT_COUNT \"%s\", using 1\n",
			   env);
		return 1;
	}

	/* weston_output_init() asserts a free bit in output_id_pool, which is 32
	 * bits wide. */
	if (count > 32) {
		weston_log("ias-soft: clamping IAS_OUTPUT_COUNT %ld to 32\n", count);
		count = 32;
	}

	return (int) count;
}

WL_EXPORT int
backend_init(struct weston_compositor *compositor,
	     int *argc, char *argv[],
	     struct weston_config *config,
	     struct weston_backend_config *config_base)
{
	int width = 1920, height = 720;
	char *display_name = NULL;
	struct headless_parameters param = { 0, };
	const char *transform = "normal";
	struct headless_backend *b;

	const struct weston_option headless_options[] = {
		{ WESTON_OPTION_INTEGER, "width", 0, &width },
		{ WESTON_OPTION_INTEGER, "height", 0, &height },
		{ WESTON_OPTION_BOOLEAN, "use-pixman", 0, &param.use_pixman },
		{ WESTON_OPTION_STRING, "transform", 0, &transform },
	};

	parse_options(headless_options,
		      ARRAY_LENGTH(headless_options), argc, argv);

	param.width = width;
	param.height = height;
	param.count = headless_output_count();
	weston_log("ias-soft: %d output(s), ivi screen ids 0..%d\n", param.count,
		   param.count - 1);

	if (weston_parse_transform(transform, &param.transform) < 0)
		weston_log("Invalid transform \"%s\"\n", transform);

	b = headless_backend_create(compositor, &param, display_name);
	if (b == NULL)
		return -1;

	ias_publish(compositor->wl_display);

	wl_signal_add(&compositor->create_surface_signal, &shim_create_surface_listener);

	return 0;
}
