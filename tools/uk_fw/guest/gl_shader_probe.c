/*
 * gl-shader-probe — prove the gl_draw_trace shader instrument reaches its target.
 *
 * Why
 * ---
 * The Blocker-1 hypothesis (pixel-space texcoords sampled as if normalised) can only be tested by
 * rewriting the fragment shader at glShaderSource time. Before trusting any result from that
 * rewrite, two things must be shown separately:
 *
 *   (a) the shim is loaded at all, and
 *   (b) glShaderSource is actually reached, and
 *   (c) the rewrite needles are present in the real shader text.
 *
 * If (b) or (c) fails, every variant run is a silent no-op that looks exactly like a falsified
 * hypothesis. That is the instrument-not-consulted trap this project has already paid for.
 *
 * This probe answers (a)-(c) with no weston, no GL driver and no GPU: it dlopen()s the shim,
 * resolves glShaderSource through it, and feeds it three synthetic sources — one carrying both
 * needles, one carrying neither. The shim's own liveness files then say whether it saw what it
 * needed to see.
 *
 * Expected, when the instrument works:
 *   /tmp/gl-draw-trace.active   contains "loaded pid=<probe pid>"
 *   /tmp/gl-draw-trace.calls    three lines: needle yes/yes, yes/no, no/no
 *
 * Falsification: no .active => the shim did not load. .active but no .calls => glShaderSource was
 * never reached and no shader conclusion is available. .calls with unexpected needle flags => the
 * real shader text differs from what the rewrite searches for, so variants cannot fire.
 *
 * Build (glibc, so it can dlopen a glibc .so):
 *   zig cc -target x86_64-linux-gnu.2.17 -O1 -o gl-shader-probe gl_shader_probe.c -ldl
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

typedef void (*shader_source_fn)(unsigned int, int, const char *const *, const int *);

static const char *SRC_BOTH =
	"#version 100\n"
	"attribute vec4 position;\n"
	"attribute vec2 texCoords;\n"
	"varying vec2 outTexCoords;\n"
	"void main() { gl_Position = position; outTexCoords = texCoords.xy; }\n"
	"---fragment---\n"
	"precision mediump float;\n"
	"varying vec2 outTexCoords;\n"
	"uniform sampler2D texture;\n"
	"void main() { gl_FragColor = texture2D(texture, outTexCoords); }\n";

static const char *SRC_VTX_ONLY =
	"#version 100\n"
	"varying vec2 outTexCoords;\n"
	"void main() { outTexCoords = texCoords.xy; }\n";

static const char *SRC_NEITHER =
	"#version 100\n"
	"void main() { gl_Position = vec4(0.0); }\n";

static void show(const char *path)
{
	char buf[2048];
	FILE *f = fopen(path, "r");
	size_t n;

	printf("--- %s ---\n", path);
	if (f == NULL) {
		printf("(absent)\n");
		return;
	}
	n = fread(buf, 1, sizeof buf - 1, f);
	buf[n] = 0;
	fputs(buf, stdout);
	fclose(f);
}

int main(int argc, char **argv)
{
	const char *lib = (argc > 1) ? argv[1] : "/gl-draw-trace.so";
	void *h;
	shader_source_fn ss;
	const char *one[1];
	int len;

	printf("gl-shader-probe pid=%d lib=%s\n", (int)getpid(), lib);

	h = dlopen(lib, RTLD_NOW | RTLD_GLOBAL);
	if (h == NULL) {
		printf("dlopen failed: %s\n", dlerror());
		return 2;
	}
	printf("dlopen ok\n");

	ss = (shader_source_fn)dlsym(h, "glShaderSource");
	if (ss == NULL) {
		printf("dlsym glShaderSource failed: %s\n", dlerror());
		return 3;
	}

	/* Three calls: both needles, vertex only, and neither. */
	one[0] = SRC_BOTH;
	len = (int)strlen(SRC_BOTH);
	ss(1u, 1, one, &len);

	one[0] = SRC_VTX_ONLY;
	len = (int)strlen(SRC_VTX_ONLY);
	ss(2u, 1, one, &len);

	one[0] = SRC_NEITHER;
	len = (int)strlen(SRC_NEITHER);
	ss(3u, 1, one, &len);

	printf("three glShaderSource calls made\n");
	show("/tmp/gl-draw-trace.active");
	show("/tmp/gl-draw-trace.calls");
	return 0;
}
