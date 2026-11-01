/* micom_service — research adaptor that owns com.lge.car.micom on the system bus.
 *
 * The vendor micommanager_userspace cannot publish: it logs
 * "[writeToDBus] There is no connection." while root demonstrably reaches the bus
 * from the same context. AppLauncher then blocks on the vehicle asks
 * (askSysBootinfo / askCustomSetting / askSettingInfoValue "Did not receive a reply")
 * and never exports com.lge.avn.applauncher.
 *
 * This supplies the missing peer: object /Ihu, interface com.lge.car.micom.ihu,
 * answering each method with an 'ay' payload — 35 bytes for AskSysBootinfo,
 * empty otherwise. libdbus is resolved with dlopen because this cross build has no
 * development headers for it.
 *
 * A shim standing in for vendor behaviour, not vendor behaviour.
 */
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdlib.h>

#define DBUS_BUS_SYSTEM 1
#define DBUS_NAME_FLAG_REPLACE_EXISTING 0x2
#define DBUS_NAME_FLAG_DO_NOT_QUEUE 0x4

#define DBUS_TYPE_BYTE  ((int) 'y')
#define DBUS_TYPE_ARRAY ((int) 'a')

#define HANDLED 0

#define BOOTINFO_LEN 35

typedef struct DBusConnection DBusConnection;
typedef struct DBusMessage DBusMessage;
typedef struct DBusError DBusError;
typedef struct DBusMessageIter DBusMessageIter;
typedef struct DBusObjectPathVTable DBusObjectPathVTable;

/* libdbus 1.x public layout */
struct DBusMessageIter {
	void *dummy1;
	void *dummy2;
	unsigned int dummy3;
	int dummy4, dummy5, dummy6, dummy7, dummy8, dummy9;
	int dummy10, dummy11, pad1, pad2;
	void *pad3;
};

struct DBusObjectPathVTable {
	void (*unregister_function)(DBusConnection *, void *);
	int (*message_function)(DBusConnection *, DBusMessage *, void *);
	void (*pad1)(void *);
	void (*pad2)(void *);
	void (*pad3)(void *);
	void (*pad4)(void *);
};

static int log_fd = -1;
static unsigned int answered;

static void say(const char *fmt, ...)
{
	char buf[256];
	va_list ap;

	va_start(ap, fmt);
	vsnprintf(buf, sizeof buf, fmt, ap);
	va_end(ap);
	fprintf(stderr, "micom-svc: %s", buf);
	if (log_fd < 0)
		log_fd = open("/dev/ttyS0", O_WRONLY);
	if (log_fd >= 0)
		dprintf(log_fd, "micom-svc: %s", buf);
}

static DBusConnection *(*p_bus_get)(int, DBusError *);
static int (*p_request_name)(DBusConnection *, const char *, unsigned int, DBusError *);
static int (*p_register_path)(DBusConnection *, const char *, const DBusObjectPathVTable *, void *);
static DBusMessage *(*p_new_method_return)(DBusMessage *);
static int (*p_iter_init_append)(DBusMessage *, DBusMessageIter *);
static int (*p_open_container)(DBusMessageIter *, int, const char *, DBusMessageIter *);
static int (*p_append_basic)(DBusMessageIter *, int, const void *);
static int (*p_close_container)(DBusMessageIter *, DBusMessageIter *);
static int (*p_send)(DBusConnection *, DBusMessage *, unsigned int *);
static void (*p_flush)(DBusConnection *);
static int (*p_read_write_dispatch)(DBusConnection *, int);
static const char *(*p_get_member)(DBusMessage *);
static void (*p_message_unref)(DBusMessage *);

static int resolve(void)
{
	void *h = dlopen("libdbus-1.so.3", RTLD_NOW);

	if (!h)
		h = dlopen("libdbus-1.so", RTLD_NOW);
	if (!h) {
		say("cannot open libdbus-1: %s\n", dlerror());
		return -1;
	}
	p_bus_get = dlsym(h, "dbus_bus_get");
	p_request_name = dlsym(h, "dbus_bus_request_name");
	p_register_path = dlsym(h, "dbus_connection_register_object_path");
	p_new_method_return = dlsym(h, "dbus_message_new_method_return");
	p_iter_init_append = dlsym(h, "dbus_message_iter_init_append");
	p_open_container = dlsym(h, "dbus_message_iter_open_container");
	p_append_basic = dlsym(h, "dbus_message_iter_append_basic");
	p_close_container = dlsym(h, "dbus_message_iter_close_container");
	p_send = dlsym(h, "dbus_connection_send");
	p_flush = dlsym(h, "dbus_connection_flush");
	p_read_write_dispatch = dlsym(h, "dbus_connection_read_write_dispatch");
	p_get_member = dlsym(h, "dbus_message_get_member");
	p_message_unref = dlsym(h, "dbus_message_unref");

	return (p_bus_get && p_request_name && p_register_path && p_new_method_return &&
		p_iter_init_append && p_open_container && p_append_basic &&
		p_close_container && p_send && p_flush && p_read_write_dispatch &&
		p_get_member && p_message_unref) ? 0 : -1;
}

static void reply_ay(DBusConnection *conn, DBusMessage *msg, const unsigned char *data,
		     unsigned int len)
{
	DBusMessage *reply = p_new_method_return(msg);
	DBusMessageIter it, arr;

	if (!reply)
		return;
	if (!p_iter_init_append(reply, &it) ||
	    !p_open_container(&it, DBUS_TYPE_ARRAY, "y", &arr)) {
		p_message_unref(reply);
		return;
	}
	for (unsigned int i = 0; i < len; i++) {
		unsigned char b = data ? data[i] : 0;
		if (!p_append_basic(&arr, DBUS_TYPE_BYTE, &b))
			break;
	}
	p_close_container(&it, &arr);
	p_send(conn, reply, NULL);
	p_flush(conn);
	p_message_unref(reply);
}

static int on_message(DBusConnection *conn, DBusMessage *msg, void *user)
{
	const char *member = p_get_member(msg);
	unsigned char bootinfo[BOOTINFO_LEN];

	(void)user;
	memset(bootinfo, 0, sizeof bootinfo);

	if (!member) {
		return 1;	/* NOT_YET_HANDLED */
	}
	if (strcmp(member, "AskSysBootinfo") == 0) {
		/* Cycle payload variants on successive asks so a live client can tell us
		 * which one it accepts. Variant order is logged. */
		static unsigned int variant;
		unsigned int v = variant++;
		memset(bootinfo, 0, sizeof bootinfo);
		switch (v % 5) {
		case 1: bootinfo[28] = 0x01; break;          /* byte 28 nonzero */
		case 2: bootinfo[28] = 0xff; break;          /* byte 28 max */
		case 3: memset(bootinfo, 0xff, sizeof bootinfo); break; /* all set */
		case 4: bootinfo[0] = 0x01; bootinfo[28] = 0x01; break;
		default: break;                               /* all zeros */
		}
		reply_ay(conn, msg, bootinfo, BOOTINFO_LEN);
		say("AskSysBootinfo -> 35 bytes variant %u\n", v % 5);
	} else if (strcmp(member, "AskNaviOutermostRegion") == 0) {
		unsigned char v[8] = { 1, 0, 0, 0, 0, 0, 0, 0 };
		reply_ay(conn, msg, v, sizeof v);
		say("AskNaviOutermostRegion -> 8 bytes\n");
	} else if (strcmp(member, "AskCustomSetting") == 0) {
		unsigned char v[16];
		memset(v, 0, sizeof v);
		reply_ay(conn, msg, v, sizeof v);
		say("AskCustomSetting -> 16 bytes\n");
	} else if (strcmp(member, "AskSettingInfoValue") == 0) {
		unsigned char v[8] = { 0, 0, 0, 0, 0, 0, 0, 1 };
		reply_ay(conn, msg, v, sizeof v);
		say("AskSettingInfoValue -> 8 bytes\n");
	} else {
		unsigned char v[4] = { 0, 0, 0, 0 };
		reply_ay(conn, msg, v, sizeof v);
		if (answered < 20)
			say("answered %s with 4 bytes\n", member);
	}
	answered++;
	return HANDLED;
}

static const DBusObjectPathVTable vtable = {
	NULL, on_message, NULL, NULL, NULL, NULL,
};

int main(void)
{
	DBusConnection *conn;
	int rc;

	if (resolve() < 0) {
		say("libdbus symbols missing\n");
		return 1;
	}
	if (p_bus_get == NULL) {
		say("no bus_get\n");
		return 1;
	}
	conn = p_bus_get(DBUS_BUS_SYSTEM, NULL);
	if (!conn) {
		say("cannot connect to system bus\n");
		return 1;
	}
	/* The vendor daemon owns the name but answers nothing, so wait for it to go
	 * away and take ownership ourselves (1 = primary owner). */
	for (int attempt = 0; attempt < 40; attempt++) {
		rc = p_request_name(conn, "com.lge.car.micom",
				    DBUS_NAME_FLAG_REPLACE_EXISTING | DBUS_NAME_FLAG_DO_NOT_QUEUE, NULL);
		if (attempt == 0 || rc == 1)
			say("request_name com.lge.car.micom -> %d (attempt %d)\n", rc, attempt + 1);
		if (rc == 1)
			break;
		usleep(500000);
	}
	if (rc != 1) {
		say("could not become primary owner (rc=%d); serving anyway\n", rc);
	}

	if (!p_register_path(conn, "/Ihu", &vtable, NULL)) {
		say("register_object_path /Ihu failed\n");
		return 1;
	}
	say("serving /Ihu com.lge.car.micom.ihu\n");

	for (;;) {
		if (!p_read_write_dispatch(conn, 1000))
			break;
	}
	say("dispatch loop ended after %u answers\n", answered);
	return 0;
}
