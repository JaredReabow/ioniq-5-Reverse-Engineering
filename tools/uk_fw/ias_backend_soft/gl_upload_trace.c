/*
 * gl_upload_trace — log the geometry the application hands to GL when it uploads an image,
 * to find a pitch/stride disagreement between an image's row length and what GL is told
 * to assume.
 *
 * Why
 * ---
 * The application's window now renders on screen, and the diagnostic detail is that its
 * **text is crisp while its image content is sheared** (changelog 3.4.0). Vector glyphs are
 * geometry; images are textures. So the fault is in the texture upload path, and the most
 * likely form of it is a disagreement between the data's row length and the value passed to
 * glPixelStorei(GL_UNPACK_ROW_LENGTH) — the GL state that says "each row of this image is N
 * pixels, not width pixels". A mismatch of a few pixels per row produces exactly the
 * diagonal stripe pattern observed, while leaving glyph geometry untouched.
 *
 * Symbols are declared here rather than included, so this object builds against no GL
 * headers and forwards to whichever libGL the compositor or application loaded.
 *
 * Research instrument: every call is forwarded unchanged.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#define LOG_PATH "/tmp/gl-upload.log"
#define MAX_EVENTS 64

typedef unsigned int GLenum;
typedef int GLint;
typedef int GLsizei;
typedef unsigned int GLuint;
typedef unsigned int GLbitfield;

static int events;

static void put(char **p, const char *s)
{
	while (*s)
		*(*p)++ = *s++;
}

static void putnum(char **p, long v)
{
	char tmp[24];
	int n = 0, i;

	if (v < 0) {
		*(*p)++ = '-';
		v = -v;
	}
	if (v == 0)
		tmp[n++] = '0';
	while (v > 0 && n < 22) {
		tmp[n++] = (char)('0' + v % 10);
		v /= 10;
	}
	for (i = n - 1; i >= 0; i--)
		*(*p)++ = tmp[i];
}

static void emit(const char *what, long a, long b, long c, long d)
{
	char line[160];
	char *p = line;
	int fd;

	if (events >= MAX_EVENTS)
		return;
	events++;

	put(&p, what);
	put(&p, " a=");
	putnum(&p, a);
	put(&p, " b=");
	putnum(&p, b);
	put(&p, " c=");
	putnum(&p, c);
	put(&p, " d=");
	putnum(&p, d);
	put(&p, "\n");

	fd = open(LOG_PATH, O_WRONLY | O_APPEND | O_CREAT, 0644);
	if (fd >= 0) {
		write(fd, line, (size_t)(p - line));
		close(fd);
	}
}

void glPixelStorei(GLenum pname, GLint param)
{
	static void (*real)(GLenum, GLint);

	/* GL_UNPACK_ROW_LENGTH is 0x0CF2: the pitch GL will use for uploads. */
	if (pname == 0x0CF2)
		emit("glPixelStorei(ROW_LENGTH)", (long)param, pname, 0, 0);
	else if (pname == 0x0D05)	/* GL_PACK_ROW_LENGTH */
		emit("glPixelStorei(PACK_ROW_LENGTH)", (long)param, pname, 0, 0);

	if (!real)
		real = dlsym(RTLD_NEXT, "glPixelStorei");
	if (real)
		real(pname, param);
}

void glTexImage2D(GLenum target, GLint level, GLint internalformat, GLsizei width,
		  GLsizei height, GLint border, GLenum format, GLenum type,
		  const void *pixels)
{
	static void (*real)(GLenum, GLint, GLint, GLsizei, GLsizei, GLint, GLenum,
			    GLenum, const void *);

	emit("glTexImage2D", (long)width, (long)height, (long)internalformat,
	     (long)format);
	if (!real)
		real = dlsym(RTLD_NEXT, "glTexImage2D");
	if (real)
		real(target, level, internalformat, width, height, border, format, type,
		     pixels);
}

void glTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset,
		     GLsizei width, GLsizei height, GLenum format, GLenum type,
		     const void *pixels)
{
	static void (*real)(GLenum, GLint, GLint, GLint, GLsizei, GLsizei, GLenum,
			    GLenum, const void *);

	emit("glTexSubImage2D", (long)width, (long)height, (long)xoffset,
	     (long)yoffset);
	if (!real)
		real = dlsym(RTLD_NEXT, "glTexSubImage2D");
	if (real)
		real(target, level, xoffset, yoffset, width, height, format, type,
		     pixels);
}
