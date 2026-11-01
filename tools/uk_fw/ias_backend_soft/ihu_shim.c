/* ihu_shim — research stand-in for the component that publishes the UI's shared
 * memory. The segment names below are not derived: they are the exact paths
 * AppHomeScreen opens, taken from a strace of its openat calls. Qt validates the
 * segment it finds under that name, so guessing the naming scheme is unnecessary
 * once the paths are observed. Each has a matching qipc_systemsem_ file, which is
 * created too because Qt's lock primitive keys off it. */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ipc.h>
#include <sys/shm.h>

#define SEG_SIZE (256 * 1024)
#define LOG "/dev/ttyS0"

static const char *shm_names[] = {
	"qipc_sharedmemory_KEYSUPPORTCHINESEe3470ef71edd715f5f694841d355b50f7c71483d",
	"qipc_sharedmemory_MICOMSTATUSMESSAGEea9b2c48d97ddb319dd9ac9fa4f70206a8ccd52c",
	"qipc_sharedmemory_NMODELAPTIMEKEYc453fc8fe1f96116d96145fd37645e3658489c99",
	"qipc_sharedmemory_STATUSBARINTERNALDATA53fb489e58485f4bd4d94f2dce92ad7002f7f4ca",
	"qipc_sharedmemory_STSTATUSBARNAME610af764cdf93ec51776f5a81c46c30b9e6c1436",
	"qipc_sharedmemory_TMSSERVICETABLEc56e0ae23d521cc964a353161d21b85f4b71b883",
};

static const char *sem_names[] = {
	"qipc_systemsem_KEYSUPPORTCHINESEe3470ef71edd715f5f694841d355b50f7c71483d",
	"qipc_systemsem_MICOMSTATUSMESSAGEea9b2c48d97ddb319dd9ac9fa4f70206a8ccd52c",
	"qipc_systemsem_NMODELAPTIMEKEYc453fc8fe1f96116d96145fd37645e3658489c99",
	"qipc_systemsem_STATUSBARINTERNALDATA53fb489e58485f4bd4d94f2dce92ad7002f7f4ca",
	"qipc_systemsem_STSTATUSBARNAME610af764cdf93ec51776f5a81c46c30b9e6c1436",
	"qipc_systemsem_TMSSERVICETABLEc56e0ae23d521cc964a353161d21b85f4b71b883",
};

static void touch(const char *path)
{
	int fd = open(path, O_CREAT | O_RDWR, 0666);
	if (fd >= 0)
		close(fd);
}

int main(void)
{
	int log = open(LOG, O_WRONLY);
	unsigned int i, made = 0;
	char path[256];

	for (i = 0; i < sizeof sem_names / sizeof sem_names[0]; i++) {
		snprintf(path, sizeof path, "/tmp/%s", sem_names[i]);
		touch(path);
	}
	for (i = 0; i < sizeof shm_names / sizeof shm_names[0]; i++) {
		key_t k;
		int id;
		void *p;

		snprintf(path, sizeof path, "/tmp/%s", shm_names[i]);
		touch(path);
		k = ftok(path, 'Q');
		if (k == -1) {
			dprintf(log, "ihu-shim: ftok failed %s\n", shm_names[i]);
			continue;
		}
		id = shmget(k, SEG_SIZE, IPC_CREAT | 0666);
		if (id < 0) {
			dprintf(log, "ihu-shim: shmget failed %s: %s\n", shm_names[i], strerror(errno));
			continue;
		}
		p = shmat(id, NULL, 0);
		if (p != (void *)-1) {
			memset(p, 0, SEG_SIZE);
			shmdt(p);
		}
		made++;
		dprintf(log, "ihu-shim: created %s (id=%d size=%d)\n", shm_names[i], id, SEG_SIZE);
	}
	/* If a boot-info profile is available, seed it into the MICOM status region:
	 * the client maps that region and reads boot info from it, so a zero-filled
	 * region parses to nothing and its source pointer comes back NULL. */
	{
		const char *profile = "/micom-profile.bin";
		int pf = open(profile, O_RDONLY);
		if (pf >= 0) {
			unsigned char buf[4096];
			ssize_t n = read(pf, buf, sizeof buf);
			close(pf);
			if (n > 0) {
				for (i = 0; i < sizeof shm_names / sizeof shm_names[0]; i++) {
					key_t k;
					int id;
					void *p;
					snprintf(path, sizeof path, "/tmp/%s", shm_names[i]);
					if (!strstr(shm_names[i], "MICOMSTATUSMESSAGE"))
						continue;
					k = ftok(path, 'Q');
					if (k == -1)
						break;
					id = shmget(k, SEG_SIZE, 0600);
					if (id < 0)
						break;
					p = shmat(id, NULL, 0);
					if (p == (void *) -1)
						break;
					memcpy(p, buf, (size_t) n);
					shmdt(p);
					dprintf(log, "ihu-shim: seeded %zd profile bytes\n", n);
					break;
				}
			}
		}
	}
	dprintf(log, "ihu-shim: %u segment(s)\n", made);
	return made ? 0 : 1;
}
