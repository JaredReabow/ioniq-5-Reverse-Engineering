/*
 * crash_trace — record a fatal-signal stack trace and the module map, with no debugger.
 *
 * Why
 * ---
 * Two vendor clients die in this project and neither death is diagnosable: AppNavi faults in
 * libQt5Core at about 55 seconds, AppCamera takes an invalid free at about 181 seconds. The guest
 * image has no gdb, no gdbserver and no ltrace, so every previous attempt to explain these deaths
 * has had to infer a cause from a single kernel line giving an instruction pointer.
 *
 * This interposer installs handlers for the fatal signals and, when one fires, writes:
 *   - the signal number and the faulting address,
 *   - a backtrace symbolised by libc itself (backtrace_symbols_fd, which prints module + offset),
 *   - the process's own memory map, so those offsets can be resolved to functions offline.
 *
 * Installed through /etc/ld.so.preload, which is the only mechanism that reaches processes the
 * vendor launcher starts (their environment is rebuilt, so LD_PRELOAD never arrives).
 *
 * Research instrument: after writing, the original disposition is restored and the signal is
 * re-raised, so the process still dies exactly as it would have.
 */

#define _GNU_SOURCE
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/* Declared here rather than by including <execinfo.h>, to keep this object free of headers
 * that may not exist in a cross sysroot. Both are stable glibc entry points. */
int backtrace(void **buffer, int size);
void backtrace_symbols_fd(void *const *buffer, int size, int fd);

#define MAX_FRAMES 64

static void append_file(int fd, const char *path)
{
	char buf[4096];
	int in = open(path, O_RDONLY);
	ssize_t n;

	if (in < 0)
		return;
	while ((n = read(in, buf, sizeof buf)) > 0)
		(void)!write(fd, buf, (size_t)n);
	close(in);
}

static void handler(int sig, siginfo_t *info, void *ctx)
{
	void *frames[MAX_FRAMES];
	int n, fd;
	char line[256];
	int len;

	(void)ctx;

	len = snprintf(line, sizeof line, "\n=== signal %d (%s) pid %d addr %p ===\n",
		       sig, strsignal(sig), (int)getpid(), info ? info->si_addr : NULL);
	fd = open("/tmp/crash-trace.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
	if (fd >= 0) {
		(void)!write(fd, line, (size_t)len);

		n = backtrace(frames, MAX_FRAMES);
		(void)!write(fd, "--- backtrace (module+offset) ---\n", 34);
		backtrace_symbols_fd(frames, n, fd);

		(void)!write(fd, "--- maps ---\n", 13);
		append_file(fd, "/proc/self/maps");
		(void)!write(fd, "--- end ---\n", 12);
		close(fd);
	}

	/* Preserve the default behaviour: die the way the process would have. */
	signal(sig, SIG_DFL);
	raise(sig);
}

__attribute__((constructor)) static void install(void)
{
	struct sigaction sa;
	static const int sigs[] = { SIGSEGV, SIGABRT, SIGBUS, SIGFPE, SIGILL };
	unsigned i;

	memset(&sa, 0, sizeof sa);
	sa.sa_sigaction = handler;
	sa.sa_flags = SA_SIGINFO | SA_RESETHAND;
	sigemptyset(&sa.sa_mask);

	for (i = 0; i < sizeof sigs / sizeof sigs[0]; i++)
		sigaction(sigs[i], &sa, NULL);
}
