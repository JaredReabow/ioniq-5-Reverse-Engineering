/*
 * crash_probe — positive control for the crash-trace interposer.
 *
 * Why
 * ---
 * The crash-trace shim (tools/uk_fw/ias_backend_soft/crash_trace.c) was written to explain two
 * vendor-client deaths, but it has never produced a log. It is also not installed by any part of
 * the image build. That combination is the failure this project has already paid for three times:
 * an instrument that is silently never consulted, whose empty output is then read as "no crash".
 *
 * This probe exists so the instrument can be proven to reach its target BEFORE any real crash is
 * interpreted. It takes its fault mode from argv[1] and faults deterministically, so the only
 * variable under test is whether the interposer fired.
 *
 * Falsification condition
 * -----------------------
 * Run under /etc/ld.so.preload with crash-trace.so present:
 *   PASS  /tmp/crash-trace.log exists, contains "=== signal N (", a "--- backtrace" section with at
 *         least 3 frames, and a "--- maps ---" section naming this binary.
 *   FAIL  any of those absent => the interposer did not reach this process, and every earlier
 *         "no trace" observation was an instrumentation artefact rather than evidence.
 *
 * Usage: crash_probe segv | abort | bus | fpe | ill
 */

#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int touch_volatile(void)
{
	volatile int *p = (volatile int *)0;
	return *p; /* SIGSEGV */
}

int main(int argc, char **argv)
{
	const char *mode = (argc > 1) ? argv[1] : "segv";

	fprintf(stderr, "crash_probe: mode=%s pid=%d\n", mode, (int)getpid());

	if (strcmp(mode, "segv") == 0) {
		return touch_volatile();
	} else if (strcmp(mode, "abort") == 0) {
		abort();
	} else if (strcmp(mode, "bus") == 0) {
		raise(SIGBUS);
	} else if (strcmp(mode, "fpe") == 0) {
		raise(SIGFPE);
	} else if (strcmp(mode, "ill") == 0) {
		raise(SIGILL);
	}

	fprintf(stderr, "crash_probe: unknown mode %s\n", mode);
	return 2;
}
