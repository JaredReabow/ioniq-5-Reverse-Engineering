/*
 * qt_env_shim — forces the vendor IVI surface-id variables to the values the
 * vendor shell integration needs in order to create a surface at all.
 *
 * Why
 * ---
 * AppHomeScreen creates Wayland surfaces, attaches a buffer and commits **only**
 * when QT_WAYLAND_SET_SURFACE_ID is a non-zero id and
 * QT_WAYLAND_SET_SURFACE_ID_FORCED is set (measured: see the changelog entries for
 * the surface discovery). The vendor application manager exports
 * QT_WAYLAND_SET_SURFACE_ID=0 to every child it launches, and it does so from
 * inside its own binary, so overriding it in the launcher script does not work —
 * the child's environment is rebuilt by the manager.
 *
 * This shim intercepts getenv() inside the application process instead, which is
 * the last point before libivi-platform-interface reads the value. It rewrites only
 * those two names and forwards everything else to the real getenv, so no other
 * behaviour of the process changes.
 *
 * This is a research instrument, not a fix: it stands in for the vendor
 * provisioning step that would supply a real surface id on the vehicle.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>

const char *getenv(const char *name)
{
	static const char *(*real_getenv)(const char *);

	if (name != NULL) {
		if (strcmp(name, "QT_WAYLAND_SET_SURFACE_ID") == 0)
			return "4001";
		if (strcmp(name, "QT_WAYLAND_SET_SURFACE_ID_FORCED") == 0)
			return "1";
	}

	if (real_getenv == NULL) {
		/* dlsym may itself call getenv on some platforms; with RTLD_NEXT the
		 * first lookup is cheap enough that recursion is not a practical risk,
		 * but guard it anyway. */
		real_getenv = dlsym(RTLD_NEXT, "getenv");
		if (real_getenv == NULL)
			return NULL;
	}
	return real_getenv(name);
}
