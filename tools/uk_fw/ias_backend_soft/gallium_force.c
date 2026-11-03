/*
 * gallium_force — force Mesa's Gallium driver selection inside processes that the vendor
 * launcher starts, where the environment cannot be set from outside.
 *
 * Why
 * ---
 * This project has run the vendor GL stack with GALLIUM_DRIVER=softpipe throughout. softpipe is
 * the reference rasteriser and is known to be less complete than llvmpipe, which the same
 * swrast_dri.so also provides. Testing llvmpipe is a one-variable change that has never been
 * tried, and the application's environment cannot be set directly because the application
 * manager rebuilds it (changelog 2.67.0) — hence a getenv() override installed through
 * /etc/ld.so.preload, which every process reads.
 *
 * Research instrument: rewrites only GALLIUM_DRIVER, forwards everything else.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>

const char *getenv(const char *name)
{
	static const char *(*real_getenv)(const char *);

	if (name != NULL && strcmp(name, "GALLIUM_DRIVER") == 0)
		return "llvmpipe";

	if (real_getenv == NULL) {
		real_getenv = dlsym(RTLD_NEXT, "getenv");
		if (real_getenv == NULL)
			return NULL;
	}
	return real_getenv(name);
}
