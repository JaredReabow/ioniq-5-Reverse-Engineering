/*
 * iap2_socket_admission_probe — comprehensive runtime admission test for /tmp/iAp2Socket
 *
 * This tool captures all admission-relevant metadata for the iAP2 service's Unix socket:
 * - Socket inode, mode, owner UID/GID, SMACK label
 * - /tmp mount options and transmutation state
 * - Caller's SMACK label, capabilities, credentials
 * - Connection test result with errno
 * - Peer credential check (SO_PEERCRED) on accepted connection
 *
 * Usage: iap2_socket_admission_probe [--json] [--connect] [--verbose]
 * Exit: 0 = connected, 1 = denied, 2 = socket not found, 3 = other error
 */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <pwd.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/xattr.h>

/* libcap is Linux-only; conditionally include */
#if defined(__linux__)
#include <sys/capability.h>
#define HAVE_LIBCAP 1
#else
#define HAVE_LIBCAP 0
#endif

/* SO_PEERCRED and struct ucred are Linux-specific */
#if defined(__linux__)
#include <linux/socket.h>
#define HAVE_PEERCRED 1
#else
#define HAVE_PEERCRED 0
#endif

#define SOCKET_PATH "/tmp/iAp2Socket"
#define MAX_LABEL 256

static int output_json = 0;
static int do_connect = 0;
static int verbose = 0;

static void json_start(void) {
    if (output_json) printf("{\n");
}

static void json_end(void) {
    if (output_json) printf("}\n");
}

static void json_field_str(const char *key, const char *value, int last) {
    if (output_json) {
        printf("  \"%s\": \"%s\"%s\n", key, value ? value : "null", last ? "" : ",");
    }
}

static void json_field_int(const char *key, long value, int last) {
    if (output_json) {
        printf("  \"%s\": %ld%s\n", key, value, last ? "" : ",");
    }
}

static void json_field_bool(const char *key, int value, int last) {
    if (output_json) {
        printf("  \"%s\": %s%s\n", key, value ? "true" : "false", last ? "" : ",");
    }
}

static void print_verbose(const char *fmt, ...) {
    if (verbose && !output_json) {
        va_list ap;
        va_start(ap, fmt);
        vfprintf(stderr, fmt, ap);
        va_end(ap);
    }
}

static const char *uid_to_name(uid_t uid) {
    struct passwd *pw = getpwuid(uid);
    static char buf[32];
    if (pw) return pw->pw_name;
    snprintf(buf, sizeof(buf), "%u", uid);
    return buf;
}

static const char *gid_to_name(gid_t gid) {
    struct group *gr = getgrgid(gid);
    static char buf[32];
    if (gr) return gr->gr_name;
    snprintf(buf, sizeof(buf), "%u", gid);
    return buf;
}

static void read_smack_label(const char *path, char *buf, size_t buflen) {
#if defined(__linux__)
    ssize_t len = getxattr(path, "security.SMACK64", buf, buflen - 1);
    if (len > 0) {
        buf[len] = '\0';
    } else {
        strncpy(buf, "(none)", buflen - 1);
        buf[buflen - 1] = '\0';
    }
#else
    strncpy(buf, "(SMACK xattr not available on this platform)", buflen - 1);
#endif
}

static void read_self_attr(const char *attr, char *buf, size_t buflen) {
    char path[128];
    snprintf(path, sizeof(path), "/proc/self/attr/%s", attr);
    FILE *f = fopen(path, "r");
    if (f) {
        if (fgets(buf, buflen, f)) {
            buf[strcspn(buf, "\n")] = '\0';
        } else {
            strncpy(buf, "(unreadable)", buflen - 1);
        }
        fclose(f);
    } else {
        strncpy(buf, "(unavailable)", buflen - 1);
    }
}

static void get_capabilities(char *buf, size_t buflen) {
#if HAVE_LIBCAP
    cap_t caps = cap_get_proc();
    if (caps) {
        char *text = cap_to_text(caps, NULL);
        if (text) {
            strncpy(buf, text, buflen - 1);
            buf[buflen - 1] = '\0';
            cap_free(text);
        } else {
            strncpy(buf, "(cap_to_text failed)", buflen - 1);
        }
        cap_free(caps);
    } else {
        strncpy(buf, "(cap_get_proc failed)", buflen - 1);
    }
#else
    strncpy(buf, "(libcap not available on this platform)", buflen - 1);
#endif
}

static int check_tmp_mount(char *buf, size_t buflen) {
    FILE *f = fopen("/proc/mounts", "r");
    if (!f) return -1;
    char line[512];
    while (fgets(line, sizeof(line), f)) {
        char dev[128], mnt[128], fs[32], opts[256];
        if (sscanf(line, "%127s %127s %31s %255s", dev, mnt, fs, opts) == 4) {
            if (strcmp(mnt, "/tmp") == 0) {
                strncpy(buf, opts, buflen - 1);
                buf[buflen - 1] = '\0';
                fclose(f);
                return 0;
            }
        }
    }
    fclose(f);
    return -1;
}

static int stat_socket(const char *path, struct stat *st, char *label, size_t labellen) {
    if (lstat(path, st) != 0) {
        return -1;
    }
    read_smack_label(path, label, labellen);
    return 0;
}

static int test_connect(const char *path, int *peer_uid, int *peer_gid, int *peer_pid) {
    struct sockaddr_un addr;
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }
    
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    if (strlen(path) >= sizeof(addr.sun_path)) {
        close(fd);
        return -1;
    }
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);
    
    int rc = connect(fd, (struct sockaddr *)&addr, sizeof(addr));
    if (rc == 0) {
        // Get peer credentials (Linux only)
#if HAVE_PEERCRED
        struct ucred cred;
        socklen_t len = sizeof(cred);
        if (getsockopt(fd, SOL_SOCKET, SO_PEERCRED, &cred, &len) == 0) {
            if (peer_uid) *peer_uid = cred.uid;
            if (peer_gid) *peer_gid = cred.gid;
            if (peer_pid) *peer_pid = cred.pid;
        }
#endif
        close(fd);
        return 0;
    } else {
        int err = errno;
        close(fd);
        return err;
    }
}

int main(int argc, char **argv) {
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--json") == 0) output_json = 1;
        else if (strcmp(argv[i], "--connect") == 0) do_connect = 1;
        else if (strcmp(argv[i], "--verbose") == 0) verbose = 1;
        else {
            fprintf(stderr, "Usage: %s [--json] [--connect] [--verbose]\n", argv[0]);
            return 3;
        }
    }
    
    json_start();
    
    // Self metadata
    char self_label[MAX_LABEL];
    char self_exec_label[MAX_LABEL];
    char self_create_label[MAX_LABEL];
    char caps_buf[4096];
    
    read_self_attr("current", self_label, sizeof(self_label));
    read_self_attr("exec", self_exec_label, sizeof(self_exec_label));
    read_self_attr("create", self_create_label, sizeof(self_create_label));
    get_capabilities(caps_buf, sizeof(caps_buf));
    
    json_field_str("caller_smack_current", self_label, 0);
    json_field_str("caller_smack_exec", self_exec_label, 0);
    json_field_str("caller_smack_create", self_create_label, 0);
    json_field_str("caller_capabilities", caps_buf, 0);
    json_field_int("caller_uid", getuid(), 0);
    json_field_int("caller_gid", getgid(), 0);
    json_field_int("caller_euid", geteuid(), 0);
    json_field_int("caller_egid", getegid(), 0);
    json_field_str("caller_uid_name", uid_to_name(getuid()), 0);
    json_field_str("caller_gid_name", gid_to_name(getgid()), 0);
    
    // /tmp mount
    char tmp_opts[256];
    if (check_tmp_mount(tmp_opts, sizeof(tmp_opts)) == 0) {
        json_field_str("tmp_mount_options", tmp_opts, 0);
    } else {
        json_field_str("tmp_mount_options", "(not found)", 0);
    }
    
    // Socket metadata
    struct stat st;
    char sock_label[MAX_LABEL];
    int stat_rc = stat_socket(SOCKET_PATH, &st, sock_label, sizeof(sock_label));
    
    if (stat_rc != 0) {
        json_field_bool("socket_exists", 0, 0);
        json_field_str("socket_error", strerror(errno), do_connect ? 0 : 1);
        json_end();
        return 2;
    }
    
    json_field_bool("socket_exists", 1, 0);
    json_field_int("socket_inode", (long)st.st_ino, 0);
    json_field_int("socket_mode", st.st_mode & 0777, 0);
    json_field_str("socket_mode_octal", (char *)(&st.st_mode), 0); // placeholder
    json_field_int("socket_uid", (long)st.st_uid, 0);
    json_field_int("socket_gid", (long)st.st_gid, 0);
    json_field_str("socket_uid_name", uid_to_name(st.st_uid), 0);
    json_field_str("socket_gid_name", gid_to_name(st.st_gid), 0);
    json_field_str("socket_smack_label", sock_label, 0);
    json_field_int("socket_nlink", (long)st.st_nlink, 0);
    json_field_int("socket_size", (long)st.st_size, 0);
    
    // Print human-readable mode
    char mode_str[16];
    snprintf(mode_str, sizeof(mode_str), "0%o", st.st_mode & 0777);
    if (!output_json) {
        printf("Socket: %s\n", SOCKET_PATH);
        printf("  inode: %llu\n", (unsigned long long)st.st_ino);
        printf("  mode: %s (%o)\n", mode_str, st.st_mode & 0777);
        printf("  owner: %s (%d):%s (%d)\n", 
               uid_to_name(st.st_uid), st.st_uid,
               gid_to_name(st.st_gid), st.st_gid);
        printf("  SMACK: %s\n", sock_label);
        printf("  nlink: %hu, size: %lld\n", (unsigned short)st.st_nlink, (long long)st.st_size);
    }
    
    if (!do_connect) {
        json_field_str("connect_attempted", "false", 1);
        json_end();
        return 0;
    }
    
    // Connection test
    int peer_uid = -1, peer_gid = -1, peer_pid = -1;
    int conn_err = test_connect(SOCKET_PATH, &peer_uid, &peer_gid, &peer_pid);
    
    if (conn_err == 0) {
        json_field_str("connect_result", "CONNECTED", 0);
        json_field_int("peer_uid", peer_uid, 0);
        json_field_int("peer_gid", peer_gid, 0);
        json_field_int("peer_pid", peer_pid, 0);
        json_field_str("peer_uid_name", uid_to_name(peer_uid), 0);
        json_field_str("peer_gid_name", gid_to_name(peer_gid), 0);
        if (!output_json) {
            printf("CONNECTED: peer uid=%d(%s) gid=%d(%s) pid=%d\n",
                   peer_uid, uid_to_name(peer_uid),
                   peer_gid, gid_to_name(peer_gid), peer_pid);
        }
        json_field_str("connect_error", "none", 1);
        json_end();
        return 0;
    } else {
        json_field_str("connect_result", "DENIED", 0);
        json_field_int("connect_errno", conn_err, 0);
        json_field_str("connect_error", strerror(conn_err), 1);
        if (!output_json) {
            printf("DENIED: errno=%d (%s)\n", conn_err, strerror(conn_err));
        }
        json_end();
        return 1;
    }
}