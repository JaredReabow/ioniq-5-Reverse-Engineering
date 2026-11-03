/*
 * gallium_trace_env — turn on Mesa's own Gallium trace module inside processes the vendor
 * launcher starts, by answering getenv("GALLIUM_TRACE") with a writable path.
 *
 * Why this file exists
 * --------------------
 * The frame's image content is sheared by a measured 3 pixels per row while its text stays
 * crisp, which points at how a texture is sampled onto a quad rather than at any upload or
 * composite step. A hand-written draw tracer is the obvious instrument, but Mesa already
 * contains one: the Gallium "trace" driver dumps every pipe_context/pipe_screen call. It is
 * selected purely by environment variable, and the one obstacle — the application manager
 * rebuilding its children's environment — is already solved by this project's /etc/ld.so.preload
 * getenv() interposition (the same trick that pinned GALLIUM_DRIVER to llvmpipe, verified
 * reaching Mesa with ten logged queries).
 *
 * What the in-use driver was checked to contain
 * ---------------------------------------------
 * The trace module is a compile-time option, so "Mesa has tracing" is not enough; the shipped
 * swrast_dri.so must have been built with it. Both staged trees were inspected and both were
 * built with the trace module enabled:
 *
 *   work/software-egl/extracted/mesa18/usr/lib/x86_64-linux-gnu/dri/swrast_dri.so  (Mesa 18.2.8)
 *   work/software-egl/extracted/mesa/usr/lib/.../dri/swrast_dri.so                 (Mesa 13.0.6)
 *
 * Each contains, in .rodata, the trace module's entire output format and its controls:
 *   "<trace version='0.1'>", "<?xml ...?>", "<?xml-stylesheet ... href='trace.xsl'?>",
 *   "<call no='", "' class='", "' method='", "</trace>",
 *   "<int>%lli</int>", "<uint>%llu</uint>", "<float>%g</float>", "<bool>%c</bool>",
 *   "<ptr>0x%08lx</ptr>", "<null/>", "<bytes>", "</bytes>", "<string>", "<enum>",
 *   "<array>", "<elem>", "<struct name='%s'>", "<member name='%s'>",
 *   the literal hex alphabet "0123456789ABCDEF" (it writes byte blobs by table lookup, which is
 *   why no "%02x" format string exists), and the strings "GALLIUM_TRACE", "stdout", "stderr".
 *
 * Two consequences that shape the rest of this work:
 *
 *   1. The dump is **XML** ("<trace version='0.1'>"), not the binary apitrace .trace format.
 *      A parser reading it is a text parser; no apitrace tooling is involved.
 *   2. GALLIUM_TRACE takes a *filename*, with "stdout"/"stderr" accepted as special values
 *      (they appear immediately next to the variable name in .rodata). There is no
 *      GALLIUM_TRACE_TRIGGER in either build — a scan of every GALLIUM_* literal in the binary
 *      finds DDEBUG, DDEBUG_SKIP, DRIVER, DUMP_VS, HUD*, NOOP, NOSSE, PRINT_OPTIONS,
 *      PROCESS_NAME, RBUG, RBUG_START_BLOCKED, TESTS, THREAD and TRACE, and nothing else — so
 *      this build cannot be told to trace only one frame. It dumps from screen creation until
 *      the process exits. Plan for a large file and a short run.
 *
 * Deliberately a separate object
 * ------------------------------
 * gallium_force.c already interposes getenv() for GALLIUM_DRIVER. Both must not be active at
 * once and expect the other to answer: ld.so.preload objects all land in the global scope, and
 * RTLD_NEXT from the second object skips the first, so a second interposer would silently stop
 * gallium_force.c's answer from being reached. Run one at a time, replacing the line in
 * /etc/ld.so.preload. Tracing does not need a driver pin: the Gallium driver is already excluded
 * by measurement, so nothing is lost by taking gallium_force.c out for the trace run.
 *
 * Per-process filenames
 * ----------------------
 * /etc/ld.so.preload applies to *every* process, and the trace module opens its file itself.
 * If the application and, say, a GL-using compositor were both told "/tmp/gallium.trace", they
 * would open the same path and destroy each other's dump. So a "%p" in the configured path is
 * expanded to the process id here, and the default path uses it. The resolved path is written to
 * the log, so the run does not have to guess which file is the application's.
 *
 * Control without rebuilding
 * --------------------------
 * The path is read from /etc/gallium-trace-path if that file exists, so a run can be retargeted
 * or switched off without recompiling: a first line of "off", "none" or "0" leaves the variable
 * unanswered, which disables tracing while the object stays preloaded.
 *
 * Research instrument: answers one variable, forwards everything else untouched.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define CONTROL_PATH "/etc/gallium-trace-path"
#define DEFAULT_PATH "/tmp/gallium-%p.trace"
#define LOG_PATH "/tmp/gallium-trace-env.log"

/* Path state is decided once, on the first query, because the trace module may ask from GL
 * init and again later. 0 = undecided, 1 = answer with path[], 2 = do not answer. */
static int path_state;
static char path[256];

static void log_text(const char *s)
{
	int fd = open(LOG_PATH, O_WRONLY | O_CREAT | O_APPEND, 0644);

	if (fd >= 0) {
		write(fd, s, strlen(s));
		close(fd);
	}
}

/* Reads one trimmed line without going through getenv(), so the control file cannot recurse
 * into this function. Returns the length, or 0 if the file is absent. */
static int read_control(char *dst, int cap)
{
	int fd = open(CONTROL_PATH, O_RDONLY);
	int n, i;

	if (fd < 0)
		return 0;
	n = (int)read(fd, dst, (size_t)(cap - 1));
	close(fd);
	if (n <= 0)
		return 0;
	for (i = 0; i < n; i++)
		if (dst[i] == '\n' || dst[i] == '\r')
			break;
	dst[i] = '\0';
	return i;
}

/* Expands a single %p to the pid. A leading "~/" is deliberately not supported: a guest path
 * for this purpose is absolute. snprintf() does not consult the environment, so it is safe to
 * call from inside getenv(). */
static void build_path(const char *tmpl)
{
	const char *at = strstr(tmpl, "%p");

	if (at == NULL) {
		snprintf(path, sizeof(path), "%s", tmpl);
		return;
	}
	snprintf(path, sizeof(path), "%.*s%ld%s", (int)(at - tmpl), tmpl, (long)getpid(),
		 at + 2);
}

static void decide(void)
{
	char ctl[200];
	int n;

	path_state = 1;
	n = read_control(ctl, (int)sizeof(ctl));
	if (n > 0) {
		if (strcmp(ctl, "off") == 0 || strcmp(ctl, "none") == 0 ||
		    strcmp(ctl, "0") == 0) {
			path_state = 2;
			log_text("GALLIUM_TRACE queried, tracing disabled by " CONTROL_PATH "\n");
			return;
		}
		build_path(ctl);
	} else {
		build_path(DEFAULT_PATH);
	}

	{
		char line[320];

		strcpy(line, "GALLIUM_TRACE queried, returning ");
		strncat(line, path, sizeof(line) - 64);
		strcat(line, "\n");
		log_text(line);
	}
}

const char *getenv(const char *name)
{
	static const char *(*real_getenv)(const char *);

	if (name != NULL && strcmp(name, "GALLIUM_TRACE") == 0) {
		if (path_state == 0)
			decide();
		if (path_state == 1)
			return path;
		/* path_state == 2: tracing switched off by the control file. Fall through
		 * rather than returning NULL, so a genuinely set GALLIUM_TRACE still works. */
	}

	if (real_getenv == NULL) {
		real_getenv = dlsym(RTLD_NEXT, "getenv");
		if (real_getenv == NULL)
			return NULL;
	}
	return real_getenv(name);
}
