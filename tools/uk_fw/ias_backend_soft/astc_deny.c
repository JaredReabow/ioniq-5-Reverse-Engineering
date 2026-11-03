/*
 * astc_deny — make the vendor application's ASTC asset opens fail, so it either falls back to
 * the plain .png assets that ship alongside some of them, or renders nothing.
 *
 * Why
 * ---
 * The application's art is ASTC-compressed and the software GL in this emulation has no ASTC
 * support (changelog 3.7.0), so the uploaded textures are undefined and sampling them produces
 * the diagonal stripes that were chased for two days. The vendor ships plain .png for part of
 * the tree and .png.astc.lz4 for the rest, and its own code contains both an
 * UncompressedTextureFactory and an ASTCCompressedTextureFactory.
 *
 * Whether a plain .png is used when the compressed file is unavailable is a property of the
 * vendor code, not something that can be assumed. Denying the compressed path is the cheapest
 * way to ask: if the UI then renders with crisp images, a fallback exists and the emulation can
 * simply withhold the compressed assets instead of decoding them.
 *
 * Research instrument: affects only paths containing ".astc".
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdarg.h>
#include <string.h>

#define MODE_MASK 3

int open(const char *path, int flags, ...)
{
	static int (*real)(const char *, int, ...);
	mode_t mode = 0;

	if (flags & O_CREAT) {
		va_list ap;
		va_start(ap, flags);
		mode = (mode_t)va_arg(ap, int);
		va_end(ap);
	}

	if (path && strstr(path, ".astc")) {
		errno = ENOENT;
		return -1;
	}

	if (!real)
		real = dlsym(RTLD_NEXT, "open");
	if (!real) {
		errno = ENOSYS;
		return -1;
	}
	return real(path, flags, mode);
}

int open64(const char *path, int flags, ...)
{
	static int (*real)(const char *, int, ...);
	mode_t mode = 0;

	if (flags & O_CREAT) {
		va_list ap;
		va_start(ap, flags);
		mode = (mode_t)va_arg(ap, int);
		va_end(ap);
	}

	if (path && strstr(path, ".astc")) {
		errno = ENOENT;
		return -1;
	}

	if (!real)
		real = dlsym(RTLD_NEXT, "open64");
	if (!real) {
		errno = ENOSYS;
		return -1;
	}
	return real(path, flags, mode);
}
