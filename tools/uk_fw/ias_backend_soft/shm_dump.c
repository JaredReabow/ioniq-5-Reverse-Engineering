/*
 * shm_dump — dump a client's own wl_shm buffer contents at attach time, so the
 * application's rendering can be judged separately from the compositor's composition.
 *
 * Why
 * ---
 * The composited frame is sheared. Everything reachable in this image has been ruled out
 * as the cause: the application's declared buffer geometry is consistent, our backend's
 * strides agree, the renderer's odd stride is intentional, and weston's GL renderer does
 * not run here. What has never been observed is the application's own pixels — only what
 * the compositor produced from them.
 *
 * This interposes the three libwayland-client calls that carry the pixels:
 *   wl_shm_create_pool(shm, fd, size)            — mmap the pool ourselves
 *   wl_shm_pool_create_buffer(pool, offset, ...) — remember data/width/height/stride
 *   wl_surface_attach(surface, buffer, x, y)     — write the buffer out as PPM
 *
 * If the dumped buffer is a coherent UI and the composited frame is striped, the fault is
 * in composition. If the dumped buffer is itself striped, the fault is in the application
 * and the compositor has been blamed unfairly.
 *
 * Research instrument: forwards every call to the real function and changes nothing.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define MAX_POOLS 32
#define MAX_BUFFERS 64
#define MAX_DUMPS 3

struct pool_rec {
	void *pool;
	unsigned char *base;
	size_t size;
};

struct buffer_rec {
	void *buffer;
	unsigned char *data;
	int width;
	int height;
	int stride;
	int dumped;
};

static struct pool_rec pools[MAX_POOLS];
static int pool_count;
static struct buffer_rec buffers[MAX_BUFFERS];
static int buffer_count;
static int dump_count;

static int
write_ppm(const char *path, struct buffer_rec *b)
{
	char header[64];
	int n, fd, y, x;

	fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (fd < 0)
		return -1;
	n = snprintf(header, sizeof header, "P6\n%d %d\n255\n", b->width, b->height);
	if (write(fd, header, (size_t)n) != n) {
		close(fd);
		return -1;
	}
	for (y = 0; y < b->height; y++) {
		unsigned char *row = b->data + (size_t)y * b->stride;
		for (x = 0; x < b->width; x++) {
			unsigned char bgr[3] = { row[x * 4 + 2], row[x * 4 + 1], row[x * 4 + 0] };
			if (write(fd, bgr, 3) != 3) {
				close(fd);
				return -1;
			}
		}
	}
	close(fd);
	return 0;
}

void *
wl_shm_create_pool(void *shm, int fd, int32_t size)
{
	static void *(*real)(void *, int, int32_t);
	void *pool;

	if (!real)
		real = dlsym(RTLD_NEXT, "wl_shm_create_pool");
	pool = real ? real(shm, fd, size) : 0;

	if (pool && pool_count < MAX_POOLS && size > 0) {
		void *base = mmap(0, (size_t)size, PROT_READ, MAP_SHARED, fd, 0);
		if (base != MAP_FAILED) {
			pools[pool_count].pool = pool;
			pools[pool_count].base = base;
			pools[pool_count].size = (size_t)size;
			pool_count++;
		}
	}
	return pool;
}

void *
wl_shm_pool_create_buffer(void *pool, int32_t offset, int32_t width, int32_t height,
			  int32_t stride, uint32_t format)
{
	static void *(*real)(void *, int32_t, int32_t, int32_t, int32_t, uint32_t);
	void *buffer;
	int i;

	if (!real)
		real = dlsym(RTLD_NEXT, "wl_shm_pool_create_buffer");
	buffer = real ? real(pool, offset, width, height, stride, format) : 0;

	if (!buffer || buffer_count >= MAX_BUFFERS)
		return buffer;

	for (i = 0; i < pool_count; i++) {
		if (pools[i].pool != pool)
			continue;
		if ((size_t)offset + (size_t)stride * (size_t)height > pools[i].size)
			break;
		buffers[buffer_count].buffer = buffer;
		buffers[buffer_count].data = pools[i].base + offset;
		buffers[buffer_count].width = width;
		buffers[buffer_count].height = height;
		buffers[buffer_count].stride = stride;
		buffers[buffer_count].dumped = 0;
		buffer_count++;
		break;
	}
	return buffer;
}

void
wl_surface_attach(void *surface, void *buffer, int32_t x, int32_t y)
{
	static void (*real)(void *, void *, int32_t, int32_t);
	int i;

	if (!real)
		real = dlsym(RTLD_NEXT, "wl_surface_attach");
	if (real)
		real(surface, buffer, x, y);

	if (!buffer)
		return;
	for (i = 0; i < buffer_count; i++) {
		if (buffers[i].buffer != buffer || buffers[i].dumped)
			continue;
		if (dump_count < MAX_DUMPS && buffers[i].width > 64 && buffers[i].height > 64) {
			char path[64];
			int n = snprintf(path, sizeof path, "/tmp/appbuf-%d.ppm", dump_count);
			if (n > 0)
				(void)write_ppm(path, &buffers[i]);
			dump_count++;
		}
		buffers[i].dumped = 1;
		break;
	}
}
