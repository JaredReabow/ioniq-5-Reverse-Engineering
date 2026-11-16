/* can_shim.so - stand in for the SocketCAN transport the vendor application expects.
 *
 * Why this exists: the home screen's Battery and Range widgets are fed by the app's own raw-CAN
 * listener, and the projection has no can0 because the vendor's micom driver never probes (no SPI or
 * platform device in QEMU). Rather than rebuild the kernel, this interposes the CAN socket calls and
 * delivers synthetic can_frame datagrams on an AF_UNIX socketpair, which read() returns unchanged.
 *
 * Interposed: socket/bind/ioctl/setsockopt for PF_CAN sockets only. Everything else passes through.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdarg.h>
#include <pthread.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <fcntl.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>


/* The vendor launcher discards child stderr, so report on the serial console instead. */
static int logfd = -2;
static void shimlog(const char *fmt, ...)
{
    char buf[256];
    va_list ap;
    if (logfd == -2) logfd = open("/dev/ttyS2", 1);
    if (logfd < 0) return;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof buf, fmt, ap);
    va_end(ap);
    if (n > 0) { ssize_t w = write(logfd, buf, (size_t)n); (void)w; }
}

static int (*real_socket)(int, int, int);
static int (*real_bind)(int, const struct sockaddr *, socklen_t);
static int (*real_ioctl)(int, unsigned long, ...);
static int (*real_setsockopt)(int, int, int, const void *, socklen_t);
static int (*real_close)(int);

#define MAXFAKE 32
static int fake[MAXFAKE];
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

static void init_real(void)
{
    if (!real_socket) {
        real_socket = dlsym(RTLD_NEXT, "socket");
        real_bind = dlsym(RTLD_NEXT, "bind");
        real_ioctl = dlsym(RTLD_NEXT, "ioctl");
        real_setsockopt = dlsym(RTLD_NEXT, "setsockopt");
        real_close = dlsym(RTLD_NEXT, "close");
    }
}

static int is_fake(int fd)
{
    int r = 0;
    pthread_mutex_lock(&lock);
    for (int i = 0; i < MAXFAKE; i++) if (fake[i] == fd) { r = 1; break; }
    pthread_mutex_unlock(&lock);
    return r;
}

static void add_fake(int fd)
{
    pthread_mutex_lock(&lock);
    for (int i = 0; i < MAXFAKE; i++) if (fake[i] == 0) { fake[i] = fd; break; }
    pthread_mutex_unlock(&lock);
}

static void drop_fake(int fd)
{
    pthread_mutex_lock(&lock);
    for (int i = 0; i < MAXFAKE; i++) if (fake[i] == fd) fake[i] = 0;
    pthread_mutex_unlock(&lock);
}

/* One frame per interval, repeating: 0x2fc byte7 = 119 -> 59.5 % SOC, the value a real vehicle logged. */
static void *feeder(void *arg)
{
    int wfd = (int)(long)arg;
    const unsigned int period_ms = 2000;
    struct can_frame f;
    memset(&f, 0, sizeof f);
    f.can_id = 0x2fc;
    f.can_dlc = 8;
    f.data[2] = 0x12;
    f.data[7] = 119;
    for (;;) {
        if (write(wfd, &f, sizeof f) < 0) {
            /* reader gone */
            if (errno == EPIPE) break;
        }
        struct timespec ts = { period_ms / 1000, (period_ms % 1000) * 1000000L };
        nanosleep(&ts, NULL);
    }
    return NULL;
}

int socket(int domain, int type, int protocol)
{
    init_real();
    if (domain == PF_CAN) {
        int sv[2];
        if (socketpair(AF_UNIX, SOCK_DGRAM, 0, sv) != 0) return real_socket(domain, type, protocol);
        add_fake(sv[0]);
        pthread_t t;
        pthread_create(&t, NULL, feeder, (void *)(long)sv[1]);
        pthread_detach(t);
        shimlog("CAN_SHIM_SOCKET fd=%d (synthetic can0)\n", sv[0]);
        return sv[0];
    }
    return real_socket(domain, type, protocol);
}

int bind(int fd, const struct sockaddr *addr, socklen_t len)
{
    init_real();
    if (is_fake(fd)) {
        shimlog("CAN_SHIM_BIND ok\n");
        return 0;
    }
    return real_bind(fd, addr, len);
}

int ioctl(int fd, unsigned long req, ...)
{
    init_real();
    va_list ap;
    va_start(ap, req);
    void *arg = va_arg(ap, void *);
    va_end(ap);
    if (is_fake(fd)) {
        if (req == SIOCGIFINDEX) {
            struct ifreq *ifr = (struct ifreq *)arg;
            if (ifr) { ifr->ifr_ifindex = 1; }
            shimlog("CAN_SHIM_IFINDEX ok\n");
            return 0;
        }
        shimlog("CAN_SHIM_IOCTL 0x%lx ok\n", req);
        return 0;
    }
    return real_ioctl(fd, req, arg);
}

int setsockopt(int fd, int level, int opt, const void *val, socklen_t len)
{
    init_real();
    if (is_fake(fd)) {
        shimlog("CAN_SHIM_SETSOCKOPT lvl=%d opt=%d ok\n", level, opt);
        return 0;
    }
    return real_setsockopt(fd, level, opt, val, len);
}

int close(int fd)
{
    init_real();
    if (is_fake(fd)) drop_fake(fd);
    return real_close(fd);
}
