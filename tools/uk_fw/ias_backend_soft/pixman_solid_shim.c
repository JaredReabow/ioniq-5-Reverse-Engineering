/*
 * pixman_solid_shim — research interposer for the vendor compositor's pixman path.
 *
 * Why this exists
 * ---------------
 * The vendor weston aborts when more than one IVI screen exists:
 *
 *   weston: src/pixman-renderer.c:277: composite_clipped: Assertion `src_format' failed.
 *
 * Instrumenting our own backend showed which views reach that call: views with
 * `buffer=no`, `scissor=1`, size 1920x720 and `client=-1`. No client, no buffer,
 * and scissored means these are the vendor IVI shell's own solid-colour surfaces
 * (layer/screen backgrounds and placeholders), not anything a client drew.
 *
 * pixman_renderer_surface_set_color() renders those with
 * pixman_image_create_solid_fill(), and a solid-fill image has no format, so
 * pixman_image_get_format() returns NULL. composite_clipped() asserts on exactly
 * that, after pixman_renderer has already computed the format. So the assertion is
 * the vendor compositor using a code path that cannot handle its own solid fills
 * once a second screen makes those fills scissored.
 *
 * What this does
 * --------------
 * Replaces pixman_image_create_solid_fill() with one that returns an ordinary
 * 1x1 ARGB32 bits image set to PIXMAN_REPEAT_NORMAL. That image has a real format,
 * so the assertion is satisfied, and it fills a clipped region the same way a
 * solid fill does. Nothing in the vendor binaries is modified: the symbol is
 * resolved at load time ahead of libpixman because this object is preloaded.
 *
 * Risk, stated plainly: if the vendor code depends on the returned image being a
 * solid fill for something other than compositing (e.g. pixman_image_get_format
 * returning NULL as a signal), that behaviour changes. The worst realistic outcome
 * is a missed colour fill; the observed outcome is recorded in the changelog.
 */

#include <stdint.h>
#include <stdlib.h>

/* Declared here rather than by including <pixman.h>: this object is preloaded into
 * the vendor compositor and must not require the guest's pixman headers at build
 * time. Only the handful of entry points used below are referenced, and they are
 * resolved from the process's libpixman at runtime. */
typedef struct pixman_image pixman_image_t;

typedef struct pixman_color {
	uint16_t red;
	uint16_t green;
	uint16_t blue;
	uint16_t alpha;
} pixman_color_t;

typedef enum {
	PIXMAN_REPEAT_NORMAL = 0,
} pixman_repeat_t;

#define PIXMAN_a8r8g8b8 0x20028888

pixman_image_t *pixman_image_create_bits(int format, int width, int height,
					 uint32_t *bits, int rowstride_bytes);
void pixman_image_set_repeat(pixman_image_t *image, pixman_repeat_t repeat);

pixman_image_t *
pixman_image_create_solid_fill(const pixman_color_t *color)
{
	uint32_t *pixel;
	pixman_image_t *image;

	if (!color)
		return NULL;

	/* The image repeats, so a single pixel represents the whole fill. The pixel
	 * is deliberately never freed: pixman does not own caller-supplied bits, and
	 * these images live for the life of the compositor (a handful per run). */
	pixel = malloc(sizeof *pixel);
	if (!pixel)
		return NULL;
	*pixel = ((uint32_t)(color->alpha >> 8) << 24) |
		 ((uint32_t)(color->red >> 8) << 16) |
		 ((uint32_t)(color->green >> 8) << 8) |
		 ((uint32_t)(color->blue >> 8));

	image = pixman_image_create_bits(PIXMAN_a8r8g8b8, 1, 1, pixel, 4);
	if (!image) {
		free(pixel);
		return NULL;
	}
	pixman_image_set_repeat(image, PIXMAN_REPEAT_NORMAL);
	return image;
}
