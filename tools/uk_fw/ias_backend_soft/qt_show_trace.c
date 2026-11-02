/*
 * qt_show_trace — research interposer that reports whether a Qt5 application ever
 * asks for a window to be shown, and whether the vendor IVI shell integration
 * then stalls waiting for a surface id.
 *
 * Why this exists
 * ---------------
 * AppHomeScreen keeps a QQuickWindow alive and builds scene-graph textures for it,
 * yet never calls wl_compositor.create_surface. Without a debugger in the guest,
 * the open question is whether QWindow::show() is simply never reached, or whether
 * it is reached and the vendor IVI integration (libivi-platform-interface.so)
 * blocks in waitForGetSurfaceId() before any surface is created.
 *
 * Those two possibilities need different fixes, so this shim distinguishes them by
 * logging the calls as they happen. Symbols are the Itanium-mangled names exported
 * by Qt5 and by the vendor platform library; each wrapper forwards to the real
 * function with RTLD_NEXT, so behaviour is unchanged.
 *
 * Method note: logging uses raw write(2) to a fixed path rather than stdio, because
 * the vendor launcher redirects stdout/stderr to /dev/null, and because a shim that
 * allocates or locks inside a Qt entry point risks disturbing what it measures.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>

#define LOG_PATH "/tmp/qt-show-trace.log"

static void
trace(const char *message)
{
	int fd = open(LOG_PATH, O_WRONLY | O_APPEND | O_CREAT, 0644);

	if (fd < 0)
		return;
	write(fd, message, strlen(message));
	close(fd);
}

/* QWindow::show() */
void _ZN7QWindow4showEv(void *self)
{
	static void (*real_show)(void *);

	trace("show()\n");
	if (!real_show)
		real_show = dlsym(RTLD_NEXT, "_ZN7QWindow4showEv");
	if (real_show)
		real_show(self);
}

/* QWindow::isVisible() const */
bool _ZNK7QWindow9isVisibleEv(const void *self)
{
	static bool (*real_is_visible)(const void *);
	bool result;

	if (!real_is_visible)
		real_is_visible = dlsym(RTLD_NEXT, "_ZNK7QWindow9isVisibleEv");
	if (!real_is_visible)
		return false;

	result = real_is_visible(self);
	trace(result ? "isVisible() -> true\n" : "isVisible() -> false\n");
	return result;
}

/* IviShellIntegration::waitForGetSurfaceId(HmiReceiver*) — the vendor gate that sits
 * between "the application asked for a window" and "a Wayland surface exists". */
void _ZN19IviShellIntegration19waitForGetSurfaceIdEP11HmiReceiver(void *self,
								 void *receiver)
{
	static void (*real_wait)(void *, void *);

	trace("waitForGetSurfaceId() enter\n");
	if (!real_wait)
		real_wait = dlsym(RTLD_NEXT,
				  "_ZN19IviShellIntegration19waitForGetSurfaceIdEP11HmiReceiver");
	if (real_wait)
		real_wait(self, receiver);
	trace("waitForGetSurfaceId() return\n");
}

/* IviShellIntegration::createShellSurface(QWaylandWindow*, QString const&) */
void _ZN19IviShellIntegration18createShellSurfaceEP14QWaylandWindowRK7QString(
	void *self, void *window, const void *title)
{
	static void (*real_create)(void *, void *, const void *);

	trace("createShellSurface() enter\n");
	if (!real_create)
		real_create = dlsym(RTLD_NEXT,
				    "_ZN19IviShellIntegration18createShellSurfaceEP14QWaylandWindowRK7QString");
	if (real_create)
		real_create(self, window, title);
	trace("createShellSurface() return\n");
}
