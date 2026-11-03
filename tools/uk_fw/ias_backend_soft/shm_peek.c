/*
 * shm_peek — dump a running process's shared-memory framebuffer by reading its open
 * file descriptors, without interposing anything.
 *
 * Why
 * ---
 * Wayland clients pass wl_shm buffers as fds (typically an unlinked tmpfile or memfd).
 * That fd stays open in the client, so the client's own pixels can be read out of
 * /proc/<pid>/fd and judged separately from what the compositor produced — which is
 * exactly what is needed here: the composited frame is sheared, and the application's own
 * rendering has never been observed.
 *
 * Name-based interposition does not work for libwayland protocol calls because the
 * bindings are static inline wrappers around wl_proxy_marshal_flags, so this reads the
 * buffer from the process instead of hooking the protocol.
 *
 * Usage: shm_peek <pid> <width> <height> [out.ppm] [max_bytes]
 * The fd whose size is at least width*height*4 and smallest among those is chosen, on the
 * assumption that the app's framebuffer is the largest-and-tightest match.
 */

#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <dirent.h>
#include <unistd.h>

static int
dump_fd(const char *fdpath, size_t want, const char *out, int width, int height,
	int stride)
{
	int fd = open(fdpath, O_RDONLY);
	unsigned char *p;
	FILE *f;
	int y, x;

	if (fd < 0)
		return -1;
	p = mmap(NULL, want, PROT_READ, MAP_SHARED, fd, 0);
	if (p == MAP_FAILED) {
		close(fd);
		return -1;
	}
	f = fopen(out, "wb");
	if (!f) {
		munmap(p, want);
		close(fd);
		return -1;
	}
	fprintf(f, "P6\n%d %d\n255\n", width, height);
	for (y = 0; y < height; y++) {
		unsigned char *row = p + (size_t)y * stride;
		for (x = 0; x < width; x++) {
			unsigned char bgr[3] = { row[x * 4 + 2], row[x * 4 + 1], row[x * 4] };
			fwrite(bgr, 1, 3, f);
		}
	}
	fclose(f);
	munmap(p, want);
	close(fd);
	return 0;
}

int main(int argc, char **argv)
{
	char dirpath[64], fdpath[128];
	struct dirent *de;
	DIR *d;
	int pid, width, height;
	size_t want;
	char best[128] = "";
	off_t best_size = 0;

	if (argc < 4) {
		fprintf(stderr, "usage: %s <pid> <width> <height> [out.ppm]\n", argv[0]);
		return 2;
	}
	pid = atoi(argv[1]);
	width = atoi(argv[2]);
	height = atoi(argv[3]);
	want = (size_t)width * (size_t)height * 4;

	snprintf(dirpath, sizeof dirpath, "/proc/%d/fd", pid);
	d = opendir(dirpath);
	if (!d) {
		fprintf(stderr, "shm_peek: cannot open %s\n", dirpath);
		return 3;
	}
	while ((de = readdir(d)) != NULL) {
		struct stat st;
		if (de->d_name[0] == '.')
			continue;
		snprintf(fdpath, sizeof fdpath, "%s/%s", dirpath, de->d_name);
		if (stat(fdpath, &st) != 0 || !S_ISREG(st.st_mode))
			continue;
		if ((size_t)st.st_size < want)
			continue;
		if (best_size == 0 || st.st_size < best_size) {
			best_size = st.st_size;
			snprintf(best, sizeof best, "%s", fdpath);
		}
	}
	closedir(d);

	if (best_size == 0) {
		fprintf(stderr, "shm_peek: no fd of at least %zu bytes in pid %d\n", want, pid);
		return 4;
	}
	printf("shm_peek: using %s (%lld bytes, want %zu)\n", best,
	       (long long)best_size, want);
	if (dump_fd(best, want, argc > 4 ? argv[4] : "/tmp/appbuf.ppm", width, height,
		    width * 4) < 0) {
		fprintf(stderr, "shm_peek: dump failed\n");
		return 5;
	}
	return 0;
}
