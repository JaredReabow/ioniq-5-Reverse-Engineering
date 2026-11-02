/*
 * unix_connect_probe — attempt one connect() to a Unix stream socket and report the
 * outcome, without sending anything. Used to measure whether an admission control
 * (SMACK, in this project) actually gates a socket that filesystem permissions leave
 * open.
 *
 * Usage: unix_connect_probe <path>
 * Exit: 0 connected, 1 refused/unavailable (errno printed), 2 usage.
 *
 * Deliberately does not write to the socket: the question is admission, not protocol.
 */

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

int main(int argc, char **argv)
{
	struct sockaddr_un addr;
	int fd;
	char label[128] = "(unreadable)";
	FILE *f;

	if (argc != 2) {
		fprintf(stderr, "usage: %s <socket-path>\n", argv[0]);
		return 2;
	}

	/* Report the caller's own label so the log records both sides of the check. */
	f = fopen("/proc/self/attr/current", "r");
	if (f) {
		if (fgets(label, sizeof label, f))
			label[strcspn(label, "\n")] = '\0';
		fclose(f);
	}

	if (strlen(argv[1]) >= sizeof addr.sun_path) {
		fprintf(stderr, "path too long: %s\n", argv[1]);
		return 1;
	}

	memset(&addr, 0, sizeof addr);
	addr.sun_family = AF_UNIX;
	strncpy(addr.sun_path, argv[1], sizeof addr.sun_path - 1);

	fd = socket(AF_UNIX, SOCK_STREAM, 0);
	if (fd < 0) {
		printf("CONNECT label=%s socket() errno=%d (%s)\n", label, errno,
		       strerror(errno));
		return 1;
	}

	if (connect(fd, (struct sockaddr *)&addr, sizeof addr) == 0) {
		printf("CONNECT label=%s result=CONNECTED\n", label);
		close(fd);
		return 0;
	}

	printf("CONNECT label=%s result=DENIED errno=%d (%s)\n", label, errno,
	       strerror(errno));
	close(fd);
	return 1;
}
