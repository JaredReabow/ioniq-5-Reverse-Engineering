/*
 * setenv_surface_id_shim — forces the vendor surface-id variable to the value the
 * IVI shell integration needs, at the moment the launcher sets it.
 *
 * Why this and not an environment variable in the script
 * ------------------------------------------------------
 * The vendor application manager does not pass its own environment to the children it
 * starts: exporting QT_WAYLAND_SET_SURFACE_ID from the launcher script has no effect
 * (measured — the app's /proc/<pid>/environ still showed 0), and an LD_PRELOAD placed
 * on the app likewise never arrives, because the manager builds the child environment
 * itself.
 *
 * The manager does, however, call setenv() in its own process to set the value to "0",
 * and the children then inherit whatever is in its environment. Interposing setenv()
 * here means the manager places the working value into the environment it hands to its
 * children, which is the earliest point that survives the manager's own environment
 * construction.
 *
 * 1007 is the id the vendor recipe declares for the home surface
 * (vm/repro/vendor-userspace-260128/hmi-wayland-probe.sh: "1007 is the home surface id
 * declared by the recovered weston_1920.ini"). Forcing a single id is only safe because
 * the home screen's own windows are what this launcher starts first; the forced-value
 * route was measured to collide when applied to the application directly.
 *
 * Research instrument, not a fix: it stands in for the vehicle provisioning that
 * supplies the id.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdlib.h>
#include <string.h>

int setenv(const char *name, const char *value, int overwrite)
{
	static int (*real_setenv)(const char *, const char *, int);

	if (name != NULL && strcmp(name, "QT_WAYLAND_SET_SURFACE_ID") == 0)
		value = "1007";

	if (real_setenv == NULL) {
		real_setenv = dlsym(RTLD_NEXT, "setenv");
		if (real_setenv == NULL)
			return -1;
	}
	return real_setenv(name, value, overwrite);
}
