/* SPDX-FileCopyrightText: 2026 The SCOURGE Project contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * TARGET: disconnected workbench guest simulation only; never deploy. */
/* Synthetic loopback subset of pinned WifiPage's HTTP protocol. No radio,
 * ConnMan, USB import, credentials, files, or real Wi-Fi daemon are used. */
#define _DARWIN_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <poll.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>

static volatile sig_atomic_t running = 1;
static int mode, simulated_error, scanning;
static unsigned long long request_deadline_ms;

static void stop_signal(int sig) { (void)sig; running = 0; }

/* This marker is an explicit opt-in, not VM attestation. Its directory and
 * contents must remain trusted and immutable throughout marker inspection. */
static bool marker_file(const char *path, uid_t owner)
{
    static const char expected[] = "I_UNDERSTAND_WIFI_IS_SIMULATED\n";
    char data[sizeof expected]; struct stat st; ssize_t n; int fd;
    fd = open(path, O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
    if (fd < 0) return false;
    if (fstat(fd, &st) || !S_ISREG(st.st_mode) || st.st_uid != owner || (st.st_mode & 0777) != 0600 ||
        st.st_nlink != 1 || st.st_size != (off_t)(sizeof expected - 1)) { close(fd); return false; }
    n = read(fd, data, sizeof data); close(fd);
    return n == (ssize_t)(sizeof expected - 1) && !memcmp(data, expected, sizeof expected - 1);
}

static bool vm_marker(void)
{
    if (geteuid() != 0 || !getenv("IONIQ_VM_WIFI_SIM") || strcmp(getenv("IONIQ_VM_WIFI_SIM"), "1")) return false;
    return marker_file("/run/ioniq-workbench/wifi-simulation-enabled", 0);
}

static unsigned long long monotonic_ms(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts)) return 0;
    return (unsigned long long)ts.tv_sec * 1000u + (unsigned long long)ts.tv_nsec / 1000000u;
}

/* Every request, including its response, shares one absolute deadline.
 * Short poll slices bound shutdown even with a client that sends slowly. */
static bool wait_ready(int fd, short events)
{
    while (running) {
        unsigned long long now = monotonic_ms(), remaining;
        struct pollfd pfd = {fd, events, 0}; int rc;
        if (!now || now >= request_deadline_ms) return false;
        remaining = request_deadline_ms - now;
        rc = poll(&pfd, 1, (int)(remaining < 100u ? remaining : 100u));
        if (rc > 0) return (pfd.revents & events) != 0;
        if (rc < 0 && errno != EINTR) return false;
    }
    return false;
}

static void send_all(int fd, const char *data, size_t size)
{
    while (size && wait_ready(fd, POLLOUT)) {
        ssize_t n = send(fd, data, size, 0);
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)) continue;
        if (n <= 0) return;
        data += n; size -= (size_t)n;
    }
}

static bool header_token_char(unsigned char ch)
{
    return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
           (ch >= '0' && ch <= '9') || strchr("!#$%&'*+-.^_`|~", ch) != NULL;
}

static void reply(int fd, int code, const char *body)
{
    char header[256];
    int n = snprintf(header, sizeof header, "HTTP/1.1 %d %s\r\nContent-Type: application/json\r\nContent-Length: %zu\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n", code, code == 200 ? "OK" : "Error", strlen(body));
    if (n > 0 && (size_t)n < sizeof header) { send_all(fd, header, (size_t)n); send_all(fd, body, strlen(body)); }
}

static void status_json(char *body, size_t size)
{
    long long now = (long long)time(NULL) * 1000LL;
    bool wlan = mode != 0, client = mode == 1 && !simulated_error, ap = mode == 2 && !simulated_error;
    const char *message = simulated_error ? "SIMULATED - injected error; no radio" : "SIMULATED - no radio or network";
    snprintf(body, size,
        "{\"ok\":true,\"simulated\":true,\"build_id\":\"SIMULATED\",\"updated_ms\":%lld,"
        "\"observations_fresh\":true,\"mode\":\"%s\",\"applying\":false,"
        "\"home_seq\":0,\"home_epoch\":1,\"home_source\":\"simulated\",\"home_monitor\":false,"
        "\"wlan_on\":%s,\"driver\":false,\"ip\":\"%s\",\"ssid\":\"%s\",\"signal\":%d,"
        "\"ap_active\":%s,\"ap_ssid\":\"%s\",\"ap_clients\":0,"
        "\"carplay_ready\":false,\"carplay_ie\":false,\"carplay_iap2\":false,\"carplay_mdns\":false,"
        "\"ssh_active\":false,\"ssh_enabled\":false,\"ssh_port\":2222,\"ssh_port_fallback\":false,"
        "\"vendor_ssh_22\":false,\"secure_console\":-1,\"debug_console\":false,"
        "\"imported\":false,\"imported_from\":\"\",\"client_ssid\":\"SIMULATED-NET\","
        "\"client_networks\":\"SIMULATED-NET\",\"client_net_count\":1,"
        "\"carplay_ssid\":\"SIMULATED-AP\",\"carplay_psk\":\"\",\"carplay_psk_set\":false,"
        "\"carplay_band\":2,\"carplay_channel\":36,\"carplay_btaddr\":\"\",\"carplay_id\":\"\","
        "\"bt_discoverable\":false,\"bt_pairable\":false,\"pair_message\":\"\",\"message\":\"%s\"}\n",
        now, mode == 0 ? "off" : mode == 1 ? "client" : "carplay", wlan ? "true" : "false",
        client ? "192.0.2.10" : ap ? "192.0.2.1" : "", client ? "SIMULATED-NET" : "",
        client ? -55 : 0, ap ? "true" : "false", ap ? "SIMULATED-AP" : "", message);
}

static void handle_request(int fd)
{
    char req[2048], method[8], path[256], version[16], extra, body[4096]; size_t used = 0; char *end, *line;
    int flags, content_length_seen = 0;
    request_deadline_ms = monotonic_ms(); if (!request_deadline_ms) return;
    request_deadline_ms += 1500u;
    flags = fcntl(fd, F_GETFL); if (flags < 0 || fcntl(fd, F_SETFL, flags | O_NONBLOCK)) return;
    req[0] = 0;
    while (used < sizeof req - 1 && wait_ready(fd, POLLIN)) {
        ssize_t n = recv(fd, req + used, sizeof req - 1 - used, 0);
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)) continue;
        if (n <= 0) return;
        used += (size_t)n; req[used] = 0;
        if ((end = strstr(req, "\r\n\r\n")) != NULL) break;
    }
    if (!(end = strstr(req, "\r\n\r\n")) || end + 4 != req + used || memchr(req, '\0', used)) { reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return; }
    line = strstr(req, "\r\n"); if (!line) return; *line = 0;
    if (sscanf(req, "%7s %255s %15s %c", method, path, version, &extra) != 3 ||
        (strcmp(version, "HTTP/1.1") && strcmp(version, "HTTP/1.0"))) { reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return; }
    for (char *header = line + 2; header < end;) {
        char *colon, *next = strstr(header, "\r\n"); if (!next || next > end) { reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return; }
        *next = 0;
        colon = strchr(header, ':');
        if (!colon || colon == header) { reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return; }
        for (char *ch = header; ch < colon; ch++) if (!header_token_char((unsigned char)*ch)) {
            reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return;
        }
        for (char *ch = colon + 1; *ch; ch++) if (((unsigned char)*ch < 32 && *ch != '\t') || (unsigned char)*ch == 127) {
            reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return;
        }
        if (!strncasecmp(header, "Content-Length:", 15) && ++content_length_seen != 1) {
            reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return;
        }
        if (!strncasecmp(header, "Authorization:", 14) || !strncasecmp(header, "Proxy-Authorization:", 20) ||
            !strncasecmp(header, "Cookie:", 7) || !strncasecmp(header, "Transfer-Encoding:", 18) ||
            (!strncasecmp(header, "Content-Length:", 15) && strcmp(header + 15, " 0"))) {
            reply(fd, 400, "{\"ok\":false,\"simulated\":true}\n"); return;
        }
        header = next + 2;
    }
    if (!strcmp(method, "GET") && (!strcmp(path, "/status") || !strcmp(path, "/"))) { status_json(body, sizeof body); reply(fd, 200, body); return; }
    if (!strcmp(method, "GET") && !strcmp(path, "/health")) { reply(fd, 200, "{\"ok\":true,\"simulated\":true}\n"); return; }
    if (!strcmp(method, "GET") && !strcmp(path, "/scan")) {
        if (mode == 2 || simulated_error) { reply(fd, 409, "{\"ok\":false,\"simulated\":true,\"scanning\":false,\"error\":\"SIMULATED scan unavailable\"}\n"); return; }
        scanning = 1; reply(fd, 202, "{\"ok\":true,\"simulated\":true,\"scanning\":true,\"networks\":[]}\n"); return;
    }
    if (!strcmp(method, "GET") && !strcmp(path, "/scan?poll=1")) {
        if (!scanning) { reply(fd, 200, "{\"ok\":true,\"simulated\":true,\"scanning\":false,\"networks\":[]}\n"); return; }
        scanning = 0; reply(fd, 200, "{\"ok\":true,\"simulated\":true,\"scanning\":false,\"networks\":[{\"ssid\":\"SIMULATED-NET\",\"security\":\"SIMULATED\",\"signal\":-55}]}\n"); return;
    }
    if (!strcmp(method, "GET") && (!strcmp(path, "/logs?source=daemon") || !strcmp(path, "/logs?source=wpa") || !strcmp(path, "/logs?source=ssh"))) { reply(fd, 200, "{\"ok\":true,\"simulated\":true,\"log\":\"SIMULATED - no device logs\"}\n"); return; }
    if (!strcmp(method, "POST")) {
        if (!strcmp(path, "/mode?value=off") || !strcmp(path, "/wlan?on=0") || !strcmp(path, "/client/disconnect") || !strcmp(path, "/carplay/stop")) mode = 0;
        else if (!strcmp(path, "/mode?value=client") || !strcmp(path, "/client/connect")) mode = 1;
        else if (!strcmp(path, "/wlan?on=1")) { if (mode == 0) mode = 1; }
        else if (!strcmp(path, "/mode?value=carplay") || !strcmp(path, "/carplay/start") || !strcmp(path, "/carplay/restart")) mode = 2;
        else if (!strcmp(path, "/sim/error?on=1")) simulated_error = 1;
        else if (!strcmp(path, "/sim/error?on=0")) simulated_error = 0;
        else { reply(fd, 403, "{\"ok\":false,\"simulated\":true,\"error\":\"SIMULATED action unavailable\"}\n"); return; }
        scanning = 0; reply(fd, 200, "{\"ok\":true,\"simulated\":true}\n"); return;
    }
    reply(fd, 404, "{\"ok\":false,\"simulated\":true,\"error\":\"not found\"}\n");
}

int main(int argc, char **argv)
{
    struct sockaddr_in address, peer; socklen_t length; struct sigaction sa; int listener, port = 8090, allowed = 0;
    if (argc == 2 && !strcmp(argv[1], "--vm-only")) allowed = vm_marker();
#ifdef VM_WIFI_TEST
    if (argc == 3 && !strcmp(argv[1], "--test-marker-check")) return marker_file(argv[2], geteuid()) ? 0 : 78;
    if (argc == 3 && !strcmp(argv[1], "--host-test") && !strcmp(argv[2], "0")) { allowed = 1; port = 0; }
#endif
    if (!allowed) { fputs("SIMULATED WiFi requires explicit isolated VM opt-in\n", stderr); return 78; }
    signal(SIGPIPE, SIG_IGN); memset(&sa, 0, sizeof sa); sa.sa_handler = stop_signal; sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL); sigaction(SIGINT, &sa, NULL);
    listener = socket(AF_INET, SOCK_STREAM, 0); if (listener < 0) return 1;
    memset(&address, 0, sizeof address); address.sin_family = AF_INET; address.sin_addr.s_addr = htonl(0x7f000001u); address.sin_port = htons((unsigned short)port);
    if (bind(listener, (struct sockaddr *)&address, sizeof address) || listen(listener, 4)) { close(listener); return 1; }
    length = sizeof address; if (getsockname(listener, (struct sockaddr *)&address, &length)) { close(listener); return 1; }
    printf("SIMULATED WIFI LOOPBACK %u\n", (unsigned)ntohs(address.sin_port)); fflush(stdout);
    while (running) {
        int client; length = sizeof peer; client = accept(listener, (struct sockaddr *)&peer, &length);
        if (client < 0) { if (errno == EINTR) continue; break; }
        if (peer.sin_family == AF_INET && ntohl(peer.sin_addr.s_addr) == 0x7f000001u) handle_request(client);
        close(client);
    }
    close(listener); return 0;
}
