/*
 * stderr_tee_pid — copy each process's stderr to /tmp/stderr-<pid>.log.
 *
 * Same as stderr_tee.c but names the capture file by PID so a run that
 * preloads the whole chain can read one process's diagnostics in isolation
 * (AppEngineerMode is the target here).  The original write() to fd 2 is
 * left intact, so behaviour is unchanged; if the file cannot be opened the
 * call still proceeds normally.
 *
 * Research instrument only.  Built for the Gen5W guest with zig, e.g.:
 *   work/toolchains/zig-macos-aarch64-0.13.0/zig cc -target x86_64-linux-gnu \
 *     -shared -fPIC -O1 -o stderr-tee-pid.so stderr_tee_pid.c
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

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
		if (logfd == -2) {
			char path[64];

			snprintf(path, sizeof(path), "/tmp/stderr-%d.log",
				 (int)getpid());
			logfd = open(path, O_WRONLY | O_CREAT | O_APPEND, 0644);
		}
		if (logfd >= 0)
			(void)real_write(logfd, buf, count);
	}

	rc = real_write(fd, buf, count);
	return rc;
}
