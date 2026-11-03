/*
 * stderr_tee — copy a process's stderr to a file as well as letting it through.
 *
 * Why
 * ---
 * The vendor launcher sends every child's stdout and stderr to /dev/null, which is why this
 * project has been blind to the application's own diagnostics since the first run: Qt's QML
 * warnings, the vendor's text warnings, and — most importantly here — **Mesa's GL error output**
 * all go to fd 2 and vanish. Later instrumentation could reach the process (via
 * /etc/ld.so.preload) but could not read what it was told.
 *
 * Tapping write(2) is the least invasive way to recover that: the process still writes to its
 * own (discarded) descriptor exactly as before, and a copy is appended to a file.
 *
 * Research instrument: behaviour is unchanged, and if the file cannot be opened the call still
 * proceeds normally.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stddef.h>
#include <unistd.h>

#define LOG_PATH "/tmp/app-stderr.log"

ssize_t write(int fd, const void *buf, size_t count)
{
	static ssize_t (*real_write)(int, const void *, size_t);
	static int logfd = -2;
	ssize_t rc;

	if (real_write == NULL) {
		real_write = dlsym(RTLD_NEXT, "write");
		if (real_write == NULL)
			return -1;
	}

	if (fd == 2) {
		if (logfd == -2)
			logfd = open(LOG_PATH, O_WRONLY | O_CREAT | O_APPEND, 0644);
		if (logfd >= 0)
			(void)real_write(logfd, buf, count);
	}

	rc = real_write(fd, buf, count);
	return rc;
}
