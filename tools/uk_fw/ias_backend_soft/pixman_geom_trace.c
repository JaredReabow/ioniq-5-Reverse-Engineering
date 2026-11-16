/*
 * pixman_geom_trace — log the geometry pixman images are created with inside the
 * vendor compositor, to find where a sheared composite could come from.
 *
 * Why
 * ---
 * The composited frame is sheared even though (a) the application declares a
 * consistent 1926x753 buffer with stride 7704, and (b) our backend's own output/image
 * strides agree at 1920x720/7680 (measured). What has not been observed is the geometry
 * the renderer uses when it wraps a client buffer as a pixman source image: if the
 * width and stride it passes disagree, every row shifts, which is exactly what the
 * frame shows.
 *
 * pixman_image_create_bits and pixman_image_create_bits_no_clear take (format, width,
 * height, bits, stride) and are exported by libpixman, so they can be interposed. Each
 * distinct (width, height, stride) triple is logged once, which is enough to spot a
 * mismatch without flooding the console or the log.
 *
 * Research instrument: forwards to the real function and changes nothing.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#define LOG_PATH "/tmp/pixman-geom.log"
#define MAX_TRIPLES 48

typedef struct pixman_image pixman_image_t;

static struct {
	int width;
	int height;
	int stride;
} seen[MAX_TRIPLES];
static int seen_count;

static void note(int width, int height, int stride)
{
	char line[96];
	char digits[16];
	int n = 0, i, fd;
	int v;

	for (i = 0; i < seen_count; i++)
		if (seen[i].width == width && seen[i].height == height &&
		    seen[i].stride == stride)
			return;
	if (seen_count >= MAX_TRIPLES)
		return;
	seen[seen_count].width = width;
	seen[seen_count].height = height;
	seen[seen_count].stride = stride;
	seen_count++;

	fd = open(LOG_PATH, O_WRONLY | O_APPEND | O_CREAT, 0644);
	if (fd < 0)
		return;

	memcpy(line, "create_bits width=", 19);
	n = 19;
	v = width;
	{
		int d = 0;
		char tmp[12];
		if (v == 0) tmp[d++] = '0';
		while (v > 0 && d < 11) { tmp[d++] = (char)('0' + v % 10); v /= 10; }
		while (d--) line[n++] = tmp[d];
	}
	memcpy(line + n, " height=", 8); n += 8;
	v = height;
	{
		int d = 0;
		char tmp[12];
		if (v == 0) tmp[d++] = '0';
		while (v > 0 && d < 11) { tmp[d++] = (char)('0' + v % 10); v /= 10; }
		while (d--) line[n++] = tmp[d];
	}
	memcpy(line + n, " stride=", 8); n += 8;
	v = stride;
	{
		int d = 0;
		char tmp[12];
		if (v == 0) tmp[d++] = '0';
		while (v > 0 && d < 11) { tmp[d++] = (char)('0' + v % 10); v /= 10; }
		while (d--) line[n++] = tmp[d];
	}
	line[n++] = '\n';
	(void)digits;
	write(fd, line, (size_t)n);
	close(fd);
}

/* NOT APPLIED — measured and reverted. A stride-4 image for a 1920x720 surface is
 * created by the vendor stack and is intentional; forcing the natural stride made
 * weston exit immediately, so that image is not the shear and must not be "corrected".
 * The helper is kept only as documentation of the experiment. */
/* EXPERIMENT: a caller that passes a stride smaller than width*4 produces a sheared
 * image, which is exactly what the captures show. Correct it to the natural stride and
 * log that it happened. If the pixels are laid out correctly in memory (which the
 * application's own 7704-byte stride for a 1926-wide buffer suggests), the image then
 * renders correctly; if the buffer really is one pixel per row, this would read out of
 * bounds and must be reverted. */
static int __attribute__((unused)) fix_stride(int width, int stride)
{
	int natural = width * 4;
	char line[80];
	char digits[16];
	int n = 0, fd, v;

	if (stride >= natural || width <= 1)
		return stride;

	memcpy(line, "STRIDE_FIX width=", 17);
	n = 17;
	v = width;
	{
		int d = 0;
		char tmp[12];
		while (v > 0 && d < 11) { tmp[d++] = (char)('0' + v % 10); v /= 10; }
		while (d--) line[n++] = tmp[d];
	}
	memcpy(line + n, " from=", 6); n += 6;
	v = stride;
	{
		int d = 0;
		char tmp[12];
		if (v == 0) tmp[d++] = '0';
		while (v > 0 && d < 11) { tmp[d++] = (char)('0' + v % 10); v /= 10; }
		while (d--) line[n++] = tmp[d];
	}
	memcpy(line + n, " to=", 4); n += 4;
	v = natural;
	{
		int d = 0;
		char tmp[12];
		while (v > 0 && d < 11) { tmp[d++] = (char)('0' + v % 10); v /= 10; }
		while (d--) line[n++] = tmp[d];
	}
	line[n++] = '\n';
	(void)digits;
	fd = open(LOG_PATH, O_WRONLY | O_APPEND | O_CREAT, 0644);
	if (fd >= 0) { write(fd, line, (size_t)n); close(fd); }
	return natural;
}

pixman_image_t *pixman_image_create_bits(int format, int width, int height,
					 uint32_t *bits, int rowstride)
{
	static pixman_image_t *(*real)(int, int, int, uint32_t *, int);

	note(width, height, rowstride);
	if (!real)
		real = dlsym(RTLD_NEXT, "pixman_image_create_bits");
	return real ? real(format, width, height, bits, rowstride) : 0;
}

pixman_image_t *pixman_image_create_bits_no_clear(int format, int width,
						  int height, uint32_t *bits,
						  int rowstride)
{
	static pixman_image_t *(*real)(int, int, int, uint32_t *, int);

	note(width, height, rowstride);
	if (!real)
		real = dlsym(RTLD_NEXT, "pixman_image_create_bits_no_clear");
	return real ? real(format, width, height, bits, rowstride) : 0;
}
