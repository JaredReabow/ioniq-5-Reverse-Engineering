/*
 * gl_clamp_shim — force CLAMP_TO_EDGE, and report whether the application sets wrap state at all.
 *
 * Why
 * ---
 * The screens render as diagonal stripes while text stays crisp. Upload parameters are measured
 * correct, dumped texture content is clean, and no texture matrix exists. The fragment shader
 * samples with raw varying coordinates, so wrap state decides what is fetched when those leave
 * 0..1 — Aster's ranked first experiment was to A/B wrap state against CLAMP_TO_EDGE.
 *
 * A first version that only rewrote glTexParameteri changed nothing, which is ambiguous: either
 * clamp does not help, or the application never sets wrap state (GL defaults to GL_REPEAT) and the
 * shim never fired. So this version counts the calls it rewrites and, when a texture is bound,
 * applies clamp explicitly through the real glTexParameteri — which works even if the application
 * never asks for a wrap mode.
 *
 * Research instrument: changes only GL_TEXTURE_WRAP_S / GL_TEXTURE_WRAP_T.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

typedef unsigned int GLenum;
typedef int GLint;
typedef unsigned int GLuint;

#define GL_TEXTURE_WRAP_S 0x2802
#define GL_TEXTURE_WRAP_T 0x2803
#define GL_CLAMP_TO_EDGE  0x812F
#define LOG_PATH "/tmp/gl-clamp.log"

static int rewrites;
static int binds;

static void note(const char *what, long a)
{
	char line[96];
	char *p = line;
	int fd;
	int v = (int)a;

	/* tiny formatter, no stdio in this path */
	while (*what)
		*p++ = *what++;
	*p++ = '=';
	if (v == 0)
		*p++ = '0';
	else {
		char tmp[12];
		int n = 0, i;
		while (v > 0 && n < 11) { tmp[n++] = (char)('0' + v % 10); v /= 10; }
		for (i = n - 1; i >= 0; i--)
			*p++ = tmp[i];
	}
	*p++ = '\n';

	fd = open(LOG_PATH, O_WRONLY | O_CREAT | O_APPEND, 0644);
	if (fd >= 0) {
		(void)!write(fd, line, (size_t)(p - line));
		close(fd);
	}
}

void glTexParameteri(GLenum target, GLenum pname, GLint param)
{
	static void (*real)(GLenum, GLenum, GLint);

	if (pname == GL_TEXTURE_WRAP_S || pname == GL_TEXTURE_WRAP_T) {
		param = GL_CLAMP_TO_EDGE;
		if (rewrites++ == 0)
			note("glTexParameteri_rewrites", rewrites);
	}

	if (!real)
		real = dlsym(RTLD_NEXT, "glTexParameteri");
	if (real)
		real(target, pname, param);
}

void glBindTexture(GLenum target, GLuint texture)
{
	static void (*real_bind)(GLenum, GLuint);
	static void (*real_param)(GLenum, GLenum, GLint);

	if (!real_bind)
		real_bind = dlsym(RTLD_NEXT, "glBindTexture");
	if (!real_param)
		real_param = dlsym(RTLD_NEXT, "glTexParameteri");

	if (real_bind)
		real_bind(target, texture);

	/* Apply clamp unconditionally: the application may never set a wrap mode, in which case
	 * GL's default (REPEAT) is what produces repeated diagonal fragments. */
	if (real_param && texture != 0) {
		real_param(target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
		real_param(target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
		if (binds++ == 0)
			note("glBindTexture_clamped_first", texture);
	}
}
