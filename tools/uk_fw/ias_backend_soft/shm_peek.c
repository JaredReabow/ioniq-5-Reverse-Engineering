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

/* Fallback: libwayland maps the pool and may close the fd afterwards, so the buffer is
 * not necessarily visible in /proc/<pid>/fd. The mapping itself does persist, so scan
 * /proc/<pid>/maps for a readable anonymous region of at least the expected size and read
 * it through /proc/<pid>/mem. */


/* Score how image-like a region is: a framebuffer has spatially coherent pixels, so the
 * mean absolute difference between horizontal neighbours is small; heap noise and code
 * are large. Regions that are entirely zero are rejected outright. This is what separates
 * a real framebuffer from an 8 MB allocator arena when both are anonymous mappings. */
static double
coherence(unsigned char *buf, size_t len)
{
	size_t i, n = 0;
	unsigned long long diff = 0;
	int nonzero = 0;

	for (i = 4; i + 4 < len && n < 200000; i += 4) {
		int d = (int)buf[i] - (int)buf[i - 4];
		if (d < 0) d = -d;
		diff += (unsigned)d;
		if (buf[i] != 0) nonzero++;
		n++;
	}
	if (n == 0 || nonzero == 0)
		return 1e9;
	return (double)diff / (double)n;
}

#define MAX_CAND 12

static int
dump_from_maps(int pid, size_t want, int width, int height, const char *out)
{
	char path[64];
	FILE *maps;
	char line[512];
	unsigned long best_start = 0, best_end = 0;
	struct { unsigned long start; unsigned long size; char name[192]; } cand[MAX_CAND];
	int cand_count = 0, ci;

	snprintf(path, sizeof path, "/proc/%d/maps", pid);
	maps = fopen(path, "r");
	if (!maps)
		return -1;
	while (fgets(line, sizeof line, maps)) {
		unsigned long start, end;
		char perms[8] = {0};
		if (sscanf(line, "%lx-%lx %7s", &start, &end, perms) != 3)
			continue;
		if (perms[0] != 'r' || perms[2] == 'x')
			continue;	/* readable but not executable: data, not code */
		/* A wl_shm pool need not be exactly one frame: measured in the guest, the only
		 * candidate in the right size class was 5,423,104 bytes for a 1926x753 frame
		 * (5,801,112), so accept three quarters of a frame and read what fits. */
		if (end - start < want * 3 / 4)
			continue;
		/* Record every candidate. The "smallest that fits" guess was wrong once
		 * (it picked an unrelated heap mapping that dumped as noise), so list them
		 * and let the caller dump several. */
		if (cand_count < MAX_CAND) {
			cand[cand_count].start = start;
			cand[cand_count].size = end - start;
			snprintf(cand[cand_count].name, sizeof cand[cand_count].name, "%s",
				 strchr(line, '/') ? strchr(line, '/') : "");
			cand_count++;
		}
		if (best_start == 0 || (end - start) > (best_end - best_start)) {
			best_start = start;
			best_end = end;
		}
	}
	fclose(maps);
	if (best_start == 0)
		return -1;
	{
		int a, b;
		for (a = 0; a < cand_count; a++)
			for (b = a + 1; b < cand_count; b++)
				if (cand[b].size < cand[a].size) {
					typeof(cand[0]) t = cand[a];
					cand[a] = cand[b];
					cand[b] = t;
				}
	}
	for (ci = 0; ci < cand_count; ci++)
		fprintf(stderr, "shm_peek: cand[%d] start=%lx size=%lu name=%s\n", ci,
			cand[ci].start, cand[ci].size, cand[ci].name);
	/* Choose the most image-like candidate rather than the first or largest. */
	{
		double best_score = 1e18;
		int best_i = -1;
		for (ci = 0; ci < cand_count; ci++) {
			char mempath[64];
			int mem3;
			unsigned char *b3;
			double sc;
			snprintf(mempath, sizeof mempath, "/proc/%d/mem", pid);
			mem3 = open(mempath, O_RDONLY);
			if (mem3 < 0)
				continue;
			b3 = malloc(want);
			if (!b3) { close(mem3); continue; }
			{
			ssize_t got = pread(mem3, b3, want, (off_t)cand[ci].start);
			if (got < (ssize_t)(want * 3 / 4))
				memset(b3, 0, want);
			else if (got < (ssize_t)want)
				memset(b3 + got, 0, want - (size_t)got);
		}
		if (1) {
				sc = coherence(b3, want);
				fprintf(stderr, "shm_peek: cand[%d] score=%.2f\n", ci, sc);
				if (sc < best_score) { best_score = sc; best_i = ci; }
			}
			free(b3);
			close(mem3);
		}
		if (best_i >= 0) {
			char out3[96], mempath[64];
			int mem4;
			unsigned char *b4;
			FILE *f4;
			int y4, x4;
			snprintf(mempath, sizeof mempath, "/proc/%d/mem", pid);
			mem4 = open(mempath, O_RDONLY);
			b4 = malloc(want);
			if (mem4 >= 0 && b4 &&
			    pread(mem4, b4, want, (off_t)cand[best_i].start) == (ssize_t)want) {
				snprintf(out3, sizeof out3, "%s", out);
				f4 = fopen(out3, "wb");
				if (f4) {
					fprintf(f4, "P6\n%d %d\n255\n", width, height);
					for (y4 = 0; y4 < height; y4++) {
						unsigned char *row = b4 + (size_t)y4 * width * 4;
						for (x4 = 0; x4 < width; x4++) {
							unsigned char bgr[3] = { row[x4*4+2], row[x4*4+1], row[x4*4] };
							fwrite(bgr, 1, 3, f4);
						}
					}
					fclose(f4);
					fprintf(stderr, "shm_peek: wrote %s from cand[%d] score=%.2f\n",
						out3, best_i, best_score);
				}
			}
			free(b4);
			if (mem4 >= 0) close(mem4);
		}
	}
	return 0;

	snprintf(path, sizeof path, "/proc/%d/mem", pid);
	{
		int mem = open(path, O_RDONLY);
		unsigned char *buf;
		FILE *f;
		int y, x;

		if (mem < 0)
			return -1;
		buf = malloc(want);
		if (!buf) { close(mem); return -1; }
		if (pread(mem, buf, want, (off_t)best_start) != (ssize_t)want) {
			free(buf); close(mem); return -1;
		}
		close(mem);
		f = fopen(out, "wb");
		if (!f) { free(buf); return -1; }
		fprintf(f, "P6\n%d %d\n255\n", width, height);
		for (y = 0; y < height; y++) {
			unsigned char *row = buf + (size_t)y * width * 4;
			for (x = 0; x < width; x++) {
				unsigned char bgr[3] = { row[x * 4 + 2], row[x * 4 + 1], row[x * 4] };
				fwrite(bgr, 1, 3, f);
			}
		}
		fclose(f);
		free(buf);
	}
	fprintf(stderr, "shm_peek: dumped from maps region %lx-%lx\n", best_start, best_end);
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
		int rc = dump_from_maps(pid, want, width, height,
					argc > 4 ? argv[4] : "/tmp/appbuf.ppm");
		if (rc == 0)
			return 0;
		fprintf(stderr, "shm_peek: no fd or map of at least %zu bytes in pid %d\n",
			want, pid);
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
