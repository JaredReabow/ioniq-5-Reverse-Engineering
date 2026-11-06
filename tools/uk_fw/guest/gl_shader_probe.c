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
 *   /tmp/gl-draw-trace.calls    four lines: needle yes/yes, no/yes, no/no, and no/no for the decoy
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
typedef void (*teximage_fn)(unsigned int, int, int, int, int, int, unsigned int, unsigned int, const void *);

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

/*
 * Decoy: needle-adjacent but not the needle. Opus 4.7 pointed out that the three original cases
 * prove detection when the needle is present, but do not bound false positives -- so a "yes" from
 * the real vendor shader could be a substring artefact of the shim's search rather than a genuine
 * match. This case must report frag_needle=no and vtx_needle=no; if it reports yes, the
 * discriminator is unreliable and no vendor result may be trusted either.
 */
static const char *SRC_DECOY =
	"#version 100\n"
	"varying vec2 outTexCoords;\n"
	"uniform sampler2D texture;\n"
	"void main() { gl_FragColor = texture2D( texture , outTexCoords ); }\n"
	"// outTexCoords = texCoords.xy  (commented out, deliberately not the needle)\n";

/* Verbatim shapes from libQt5Quick.so.5.4.1 attribute/varying corpus. */
static const char *SRC_QT_REAL =
	"attribute highp vec4 qt_Vertex;\n"
	"attribute highp vec2 qt_MultiTexCoord0;\n"
	"varying highp vec2 qt_TexCoord0;\n"
	"void main() { gl_Position = qt_Vertex; qt_TexCoord0 = qt_MultiTexCoord0; }\n"
	"---fragment---\n"
	"varying highp vec2 qt_TexCoord0;\n"
	"uniform sampler2D qt_Texture;\n"
	"void main() { gl_FragColor = texture2D(qt_Texture, qt_TexCoord0); }\n";

/* Verbatim GL Studio shape from app/bin/kcei/*.glsl (v_texCoord, u_texture) and
 * libglstudio_ES20_release.a (a_texCoord). */
static const char *SRC_GS_REAL =
	"attribute vec2 a_texCoord;\n"
	"varying vec2 v_texCoord;\n"
	"void main() { gl_Position = vec4(0.0); v_texCoord = a_texCoord; }\n"
	"---fragment---\n"
	"precision mediump float;\n"
	"varying vec2 v_texCoord;\n"
	"uniform sampler2D u_texture;\n"
	"void main() { gl_FragColor = texture2D(u_texture, v_texCoord); }\n";

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

	/* Must report no/no. A yes here invalidates the discriminator. */
	one[0] = SRC_DECOY;
	len = (int)strlen(SRC_DECOY);
	ss(4u, 1, one, &len);

	/*
	 * The REAL vendor shader shape, taken from libQt5Quick.so.5.4.1. The dead needles must both
	 * report "no" and the real_* fields must report "yes" -- that is the case which proves the
	 * repointed instrument works against identifiers the vendor actually emits.
	 */
	one[0] = SRC_QT_REAL;
	len = (int)strlen(SRC_QT_REAL);
	ss(5u, 1, one, &len);

	/* The actual home-screen effect shape: GL Studio naming, verbatim from app/bin/kcei/*.glsl
	 * and libglstudio_ES20_release.a. gs_* must all report yes. */
	one[0] = SRC_GS_REAL;
	len = (int)strlen(SRC_GS_REAL);
	ss(6u, 1, one, &len);

	printf("glShaderSource calls made\n");

	/*
	 * Self-validation check for the texture dump. A uniform upload must be logged as
	 * NO-UNIFORM and a varied one as yes; if the uniform case reported "yes", the
	 * has_content detector would be useless and a black dump could again be read as a
	 * clean texture.
	 */
	{
		teximage_fn ti = (teximage_fn)dlsym(h, "glTexImage2D");
		static unsigned char flat[512 * 256 * 4];
		static unsigned char grad[512 * 256 * 4];
		int y, x;

		if (ti != NULL) {
			memset(flat, 0, sizeof flat);
			ti(0x0DE1u, 0, 0x1908, 512, 256, 0, 0x1908, 0x1401, flat);

			for (y = 0; y < 256; y++)
				for (x = 0; x < 512; x++) {
					unsigned char *px = &grad[(y * 512 + x) * 4];
					px[0] = (unsigned char)(x & 0xff);
					px[1] = (unsigned char)(y & 0xff);
					px[2] = (unsigned char)((x ^ y) & 0xff);
					px[3] = 0xff;
				}
			ti(0x0DE1u, 0, 0x1908, 512, 256, 0, 0x1908, 0x1401, grad);
			printf("two glTexImage2D calls made\n");
		}
	}
	show("/tmp/gl-draw-trace.active");
	show("/tmp/gl-draw-trace.calls");
	return 0;
}
