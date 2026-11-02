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

/* IviShellPrivate::createShellSurface(QWaylandWindow*, unsigned int) — the vendor's
 * actual surface creator; IviShellIntegration calls into this one, and the surface id
 * is already an argument here, so logging it tells us what the HMI layer handed over. */
void _ZN15IviShellPrivate18createShellSurfaceEP14QWaylandWindowj(void *self,
								 void *window,
								 unsigned int id)
{
	static void (*real_create)(void *, void *, unsigned int);
	char line[96];
	int fd;

	fd = open(LOG_PATH, O_WRONLY | O_APPEND | O_CREAT, 0644);
	if (fd >= 0) {
		int n = 0;
		const char *head = "IviShellPrivate::createShellSurface id=";

		write(fd, head, strlen(head));
		if (id == 0)
			write(fd, "0\n", 2);
		else {
			/* decimal without stdio, to stay allocation-free inside a Qt entry point */
			char digits[12];
			int d = 0;
			unsigned int v = id;
			while (v && d < 11) { digits[d++] = (char)('0' + (v % 10)); v /= 10; }
			while (d--) line[n++] = digits[d];
			line[n++] = '\n';
			write(fd, line, n);
		}
		close(fd);
	}

	if (!real_create)
		real_create = dlsym(RTLD_NEXT,
				    "_ZN15IviShellPrivate18createShellSurfaceEP14QWaylandWindowj");
	if (real_create)
		real_create(self, window, id);
}

/* HmiRequesterPrivate::requestId(QWaylandWindow*, QString const&) — the request for a
 * surface id from the compositor's HMI layer. Reaching this is the gate; returning from
 * it is the answer. */
void _ZN19HmiRequesterPrivate9requestIdEP14QWaylandWindowRK7QString(void *self,
								  void *window,
								  const void *name)
{
	static void (*real_request)(void *, void *, const void *);

	trace("HmiRequesterPrivate::requestId enter\n");
	if (!real_request)
		real_request = dlsym(RTLD_NEXT,
				     "_ZN19HmiRequesterPrivate9requestIdEP14QWaylandWindowRK7QString");
	if (real_request)
		real_request(self, window, name);
	trace("HmiRequesterPrivate::requestId return\n");
}
