/*
 * gl_loader_probe — record which GL entry points an application asks the loader for.
 *
 * Why
 * ---
 * The vendor reaches GL through the function table, so the draw path cannot be interposed by
 * exported symbol. Before building a tracer around the loader, this answers the prior question
 * in one run: does the application resolve its draw entry points through eglGetProcAddress at
 * all, and under which names? If glDrawElements never appears here, a loader wrapper is the
 * wrong instrument and the next attempt should not be built on it.
 *
 * Bounded output: names are logged once each, and only for the first 400 distinct lookups.
 *
 * Research instrument: returns the real pointer unchanged.
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

#define LOG_PATH "/tmp/gl-loader.log"
#define MAX_NAMES 400

static const char *seen[MAX_NAMES];
static int seen_count;

static void note(const char *name)
{
	int i, fd;
	size_t len;

	if (name == NULL || seen_count >= MAX_NAMES)
		return;
	for (i = 0; i < seen_count; i++)
		if (strcmp(seen[i], name) == 0)
			return;
	seen[seen_count++] = name;

	fd = open(LOG_PATH, O_WRONLY | O_CREAT | O_APPEND, 0644);
	if (fd < 0)
		return;
	len = strlen(name);
	(void)!write(fd, name, len);
	(void)!write(fd, "\n", 1);
	close(fd);
}

void *eglGetProcAddress(const char *name)
{
	static void *(*real)(const char *);

	note(name);
	if (real == NULL)
		real = dlsym(RTLD_NEXT, "eglGetProcAddress");
	return real ? real(name) : NULL;
}

void *glXGetProcAddress(const unsigned char *name)
{
	static void *(*real)(const unsigned char *);

	note((const char *)name);
	if (real == NULL)
		real = dlsym(RTLD_NEXT, "glXGetProcAddress");
	return real ? real(name) : NULL;
}
