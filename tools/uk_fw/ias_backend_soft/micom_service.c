/* micom_service — research adaptor that owns com.lge.car.micom on the system bus.
 *
 * The vendor micommanager_userspace cannot publish: it logs
 * "[writeToDBus] There is no connection." while root demonstrably reaches the bus
 * from the same context. AppLauncher then blocks on the vehicle asks
 * (askSysBootinfo / askCustomSetting / askSettingInfoValue "Did not receive a reply")
 * and never exports com.lge.avn.applauncher.
 *
 * This supplies the missing peer. The method set, the reply shapes and the
 * fail-closed behaviour are ported from the proven simulator
 * tools/uk_fw/guest/micom_dbus_sim.c so that this process can stand in for the
 * MICOM daemon, not merely answer the three asks above:
 *
 *   /Ihu                    com.lge.car.micom.ihu     AskSysBootinfo (35-byte v2 'ay')
 *                                                    AskEtcCarInformationRead 32 zero bytes
 *                                                    AskFactoryModeInfo 8 zero bytes
 *                                                    SetControlKeyLock / SetETCCPUAliveMsg /
 *                                                    SetETCAppBootComplete / SetDIDInfo
 *                                                    -> empty return (signature "ay")
 *   /Can                    com.lge.car.micom.can     AskCANMMCANMicomReq / AskCANICANMicomReq /
 *                                                    SetCANMicomRecv / SetCANTPMicomRecv
 *                                                    -> empty return ("ay")
 *                                                    SetCANFixedMicomRecv ("ayiii") -> empty
 *                                                    SetDATCInitialRequest / SetCARSETInitialRequest /
 *                                                    SetLowFuelWarnningRequest ("") -> empty
 *   /com/lge/car/micom      com.lge.car.micom.audio   AskVolumeInfo / AskSoundSetupInfo 8 zero bytes
 *                                                    AskAMPSupportInfo 4 zero bytes
 *   any of the three paths  org.freedesktop.DBus.Introspectable.Introspect (per-path XML)
 *                           org.freedesktop.DBus.Peer.Ping -> empty return
 *
 * Anything else — an unknown object path, an unknown member, or a known member
 * called with the wrong signature — is answered with a D-Bus *error* and logged,
 * exactly as the simulator does. There is no catch-all "4 zero bytes" reply.
 *
 * libdbus is resolved with dlopen because this cross build has no development
 * headers for it; every entry point below is hand-declared.
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

#define DBUS_MESSAGE_TYPE_METHOD_CALL 1

#define DBUS_TYPE_BYTE   ((int) 'y')
#define DBUS_TYPE_ARRAY  ((int) 'a')
#define DBUS_TYPE_STRING ((int) 's')

#define DBUS_HANDLER_RESULT_HANDLED 0
#define DBUS_HANDLER_RESULT_NOT_YET_HANDLED 1

/* libdbus error names (dbus-protocol.h); spelled out, no header needed. */
#define ERR_UNKNOWN_METHOD "org.freedesktop.DBus.Error.UnknownMethod"
#define ERR_UNKNOWN_OBJECT "org.freedesktop.DBus.Error.UnknownObject"

#define BUS_NAME "com.lge.car.micom"
#define IHU_PATH "/Ihu"
#define IHU_INTERFACE "com.lge.car.micom.ihu"
#define CAN_PATH "/Can"
#define CAN_INTERFACE "com.lge.car.micom.can"
#define AUDIO_PATH "/com/lge/car/micom"
#define AUDIO_INTERFACE "com.lge.car.micom.audio"
#define INTROSPECTABLE_INTERFACE "org.freedesktop.DBus.Introspectable"
#define PEER_INTERFACE "org.freedesktop.DBus.Peer"

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
static DBusMessage *(*p_new_error)(DBusMessage *, const char *, const char *);
static int (*p_iter_init_append)(DBusMessage *, DBusMessageIter *);
static int (*p_open_container)(DBusMessageIter *, int, const char *, DBusMessageIter *);
static int (*p_append_basic)(DBusMessageIter *, int, const void *);
static int (*p_close_container)(DBusMessageIter *, DBusMessageIter *);
static int (*p_send)(DBusConnection *, DBusMessage *, unsigned int *);
static void (*p_flush)(DBusConnection *);
static int (*p_read_write_dispatch)(DBusConnection *, int);
static int (*p_message_get_type)(DBusMessage *);
static const char *(*p_get_path)(DBusMessage *);
static const char *(*p_get_interface)(DBusMessage *);
static const char *(*p_get_signature)(DBusMessage *);
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
	p_new_error = dlsym(h, "dbus_message_new_error");
	p_iter_init_append = dlsym(h, "dbus_message_iter_init_append");
	p_open_container = dlsym(h, "dbus_message_iter_open_container");
	p_append_basic = dlsym(h, "dbus_message_iter_append_basic");
	p_close_container = dlsym(h, "dbus_message_iter_close_container");
	p_send = dlsym(h, "dbus_connection_send");
	p_flush = dlsym(h, "dbus_connection_flush");
	p_read_write_dispatch = dlsym(h, "dbus_connection_read_write_dispatch");
	p_message_get_type = dlsym(h, "dbus_message_get_type");
	p_get_path = dlsym(h, "dbus_message_get_path");
	p_get_interface = dlsym(h, "dbus_message_get_interface");
	p_get_signature = dlsym(h, "dbus_message_get_signature");
	p_get_member = dlsym(h, "dbus_message_get_member");
	p_message_unref = dlsym(h, "dbus_message_unref");

	if (!(p_bus_get && p_request_name && p_register_path && p_new_method_return &&
	      p_new_error && p_iter_init_append && p_open_container && p_append_basic &&
	      p_close_container && p_send && p_flush && p_read_write_dispatch &&
	      p_message_get_type && p_get_path && p_get_interface && p_get_signature &&
	      p_get_member && p_message_unref)) {
		say("libdbus entry points missing\n");
		return -1;
	}
	return 0;
}

static int send_message(DBusConnection *conn, DBusMessage *reply)
{
	if (!reply)
		return 0;
	if (!p_send(conn, reply, NULL)) {
		p_message_unref(reply);
		return 0;
	}
	p_flush(conn);
	p_message_unref(reply);
	return 1;
}

static void reply_error(DBusConnection *conn, DBusMessage *msg, const char *name,
			const char *text)
{
	send_message(conn, p_new_error(msg, name, text));
}

static void reply_empty(DBusConnection *conn, DBusMessage *msg)
{
	send_message(conn, p_new_method_return(msg));
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
	send_message(conn, reply);
}

static void reply_string(DBusConnection *conn, DBusMessage *msg, const char *value)
{
	DBusMessage *reply = p_new_method_return(msg);
	DBusMessageIter it;
	const char *s = value ? value : "";

	if (!reply)
		return;
	if (!p_iter_init_append(reply, &it) ||
	    !p_append_basic(&it, DBUS_TYPE_STRING, &s)) {
		p_message_unref(reply);
		return;
	}
	send_message(conn, reply);
}

/* ---- dispatch table ported from tools/uk_fw/guest/micom_dbus_sim.c ---------- */

/* Fixed-shape 'ay' replies. The simulator's sizes are placeholders: the app only
 * checks whether the payload is empty and otherwise parses it field by field, and
 * zeroes read as "nothing to report" for every field exercised so far. */
struct ay_reply {
	const char *path;
	const char *iface;
	const char *member;
	unsigned int len;
};

static const struct ay_reply ay_replies[] = {
	{ IHU_PATH,   IHU_INTERFACE,   "AskEtcCarInformationRead", 32 },
	{ IHU_PATH,   IHU_INTERFACE,   "AskFactoryModeInfo",        8 },
	{ AUDIO_PATH, AUDIO_INTERFACE, "AskVolumeInfo",             8 },
	{ AUDIO_PATH, AUDIO_INTERFACE, "AskSoundSetupInfo",         8 },
	{ AUDIO_PATH, AUDIO_INTERFACE, "AskAMPSupportInfo",         4 },
};

/* Calls the platform awaits an ack for; the simulator answers them with a plain
 * empty METHOD_RETURN, gated on the exact incoming signature. */
struct ack_call {
	const char *path;
	const char *iface;
	const char *member;
	const char *signature;
};

static const struct ack_call ack_calls[] = {
	{ IHU_PATH, IHU_INTERFACE, "SetControlKeyLock",       "ay" },
	{ IHU_PATH, IHU_INTERFACE, "SetETCCPUAliveMsg",       "ay" },
	{ IHU_PATH, IHU_INTERFACE, "SetETCAppBootComplete",   "ay" },
	{ IHU_PATH, IHU_INTERFACE, "SetDIDInfo",              "ay" },
	{ CAN_PATH, CAN_INTERFACE, "AskCANMMCANMicomReq",     "ay" },
	{ CAN_PATH, CAN_INTERFACE, "AskCANICANMicomReq",      "ay" },
	{ CAN_PATH, CAN_INTERFACE, "SetCANMicomRecv",         "ay" },
	{ CAN_PATH, CAN_INTERFACE, "SetCANTPMicomRecv",       "ay" },
	{ CAN_PATH, CAN_INTERFACE, "SetCANFixedMicomRecv",    "ayiii" },
	{ CAN_PATH, CAN_INTERFACE, "SetDATCInitialRequest",   "" },
	{ CAN_PATH, CAN_INTERFACE, "SetCARSETInitialRequest", "" },
	{ CAN_PATH, CAN_INTERFACE, "SetLowFuelWarnningRequest", "" },
};

/* Introspection documents, byte-identical to the simulator's. */
static const char common_xml[] =
	"<interface name=\"org.freedesktop.DBus.Introspectable\">"
	"<method name=\"Introspect\"><arg direction=\"out\" type=\"s\"/>"
	"</method></interface></node>";
static const char ihu_xml[] =
	"<node><interface name=\"" IHU_INTERFACE "\">"
	"<method name=\"AskSysBootinfo\"><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"AskNaviOutermostRegion\"><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"AskSettingInfoValue\"><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"AskSysVersion\"><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"AskCustomSetting\"><arg direction=\"in\" type=\"ay\"/><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"AskSysAutomaticBrightness\"><arg direction=\"in\" type=\"ay\"/><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"SetControlKeyLock\"><arg direction=\"in\" type=\"ay\"/></method>"
	"<method name=\"SetETCCPUAliveMsg\"><arg direction=\"in\" type=\"ay\"/></method>"
	"<method name=\"SetETCAppBootComplete\"><arg direction=\"in\" type=\"ay\"/></method>"
	"<method name=\"SetDIDInfo\"><arg direction=\"in\" type=\"ay\"/></method>"
	"</interface>";
static const char can_xml[] =
	"<node><interface name=\"" CAN_INTERFACE "\">"
	"<method name=\"AskCANMMCANMicomReq\"><arg direction=\"in\" type=\"ay\"/></method>"
	"<method name=\"AskCANICANMicomReq\"><arg direction=\"in\" type=\"ay\"/></method>"
	"<method name=\"AskNaviAppData\"><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"SetCANMicomRecv\"><arg direction=\"in\" type=\"ay\"/></method>"
	"<method name=\"SetCANTPMicomRecv\"><arg direction=\"in\" type=\"ay\"/></method>"
	"<method name=\"SetCANFixedMicomRecv\"><arg direction=\"in\" type=\"ay\"/><arg direction=\"in\" type=\"i\"/><arg direction=\"in\" type=\"i\"/><arg direction=\"in\" type=\"i\"/></method>"
	"<method name=\"SetDATCInitialRequest\"/><method name=\"SetCARSETInitialRequest\"/>"
	"<method name=\"SetLowFuelWarnningRequest\"/>"
	"<signal name=\"NotifyMCANEachMsg\"><arg type=\"ay\"/></signal>"
	"<signal name=\"NotifyICANEachMsg\"><arg type=\"ay\"/></signal>"
	"<signal name=\"NotifyCANTPRECVMsg\"><arg type=\"ay\"/></signal>"
	"</interface>";
static const char audio_xml[] =
	"<node><interface name=\"" AUDIO_INTERFACE "\">"
	"<method name=\"AskVolumeInfo\"><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"AskAMPSupportInfo\"><arg direction=\"out\" type=\"ay\"/></method>"
	"<method name=\"AskSoundSetupInfo\"><arg direction=\"out\" type=\"ay\"/></method>"
	"</interface>";

static int served_path(const char *path)
{
	return path != NULL && (strcmp(path, IHU_PATH) == 0 ||
				strcmp(path, CAN_PATH) == 0 ||
				strcmp(path, AUDIO_PATH) == 0);
}

/* Interface equality: an explicit mismatch never matches, but a call that simply
 * omits the interface field is accepted when path + member + signature agree, so a
 * terse client still reaches the handler instead of collecting UnknownMethod. */
static int iface_matches(const char *actual, const char *expected)
{
	return actual == NULL || strcmp(actual, expected) == 0;
}

static int exact_call(const char *path, const char *iface, const char *member,
		      const char *signature, const char *want_path,
		      const char *want_iface, const char *want_member,
		      const char *want_signature)
{
	return path != NULL && member != NULL && signature != NULL &&
	       strcmp(path, want_path) == 0 &&
	       iface_matches(iface, want_iface) &&
	       strcmp(member, want_member) == 0 &&
	       strcmp(signature, want_signature) == 0;
}

static int serve_fixed_ay(DBusConnection *conn, DBusMessage *msg, const char *path,
			  const char *iface, const char *member, const char *signature)
{
	static const unsigned char zeroes[32];
	unsigned int i;

	for (i = 0; i < sizeof ay_replies / sizeof ay_replies[0]; i++) {
		if (!exact_call(path, iface, member, signature, ay_replies[i].path,
				ay_replies[i].iface, ay_replies[i].member, ""))
			continue;
		say("%s %s -> %u zero bytes\n", ay_replies[i].member,
		    ay_replies[i].path, ay_replies[i].len);
		reply_ay(conn, msg, zeroes, ay_replies[i].len);
		return 1;
	}
	return 0;
}

static const struct ack_call *find_ack(const char *path, const char *iface,
				       const char *member, const char *signature)
{
	unsigned int i;

	for (i = 0; i < sizeof ack_calls / sizeof ack_calls[0]; i++) {
		if (exact_call(path, iface, member, signature, ack_calls[i].path,
			       ack_calls[i].iface, ack_calls[i].member,
			       ack_calls[i].signature))
			return &ack_calls[i];
	}
	return NULL;
}

static void serve_bootinfo(DBusConnection *conn, DBusMessage *msg)
{
	/* Boot-info profile recovered from AppLauncher's own BIS decoder logs
	 * (work/vm/vendor-userspace-260128/micom-contract/BOOTINFO-AND-SIM-V2.md):
	 * 35 bytes, EV-family Europe, 12.3" LCD, nav+modem+RHD+amp, English US,
	 * last GUI mode 1. Served verbatim rather than invented. */
	static const unsigned char v2_profile[BOOTINFO_LEN] = {
		0x00, 0x00, 0x08, 0x26, 0x05, 0x00, 0x00, 0x05, 0x13, 0x02,
		0x00, 0x00, 0x03, 0xc8, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00,
		0x01, 0x00, 0x00, 0x00, 0x00,
	};

	reply_ay(conn, msg, v2_profile, BOOTINFO_LEN);
	say("AskSysBootinfo /Ihu -> v2 profile (35 bytes)\n");
}

/* Ask* asks the home screen issues at startup and then waits on forever when
 * nothing answers. Kept from this service's original contract: the v2 boot-info
 * document (BOOTINFO-AND-SIM-V2.md) names them, so they are answered rather than
 * failed closed. Payload sizes match the shapes the app parses. */
static int serve_contract_ask(DBusConnection *conn, DBusMessage *msg, const char *path,
			      const char *iface, const char *member, const char *signature)
{
	if (!exact_call(path, iface, member, signature, IHU_PATH, IHU_INTERFACE,
			"AskNaviOutermostRegion", ""))
		return 0;
	{
		static const unsigned char v[8] = { 1, 0, 0, 0, 0, 0, 0, 0 };
		reply_ay(conn, msg, v, sizeof v);
	}
	say("AskNaviOutermostRegion -> 8 bytes\n");
	return 1;
}

static int on_message(DBusConnection *conn, DBusMessage *msg, void *user)
{
	static char xml[4096];
	const char *path, *iface, *member, *signature;
	const struct ack_call *ack;
	const char *specific;

	(void)user;

	/* Signals and method returns also reach an object-path handler. The simulator
	 * never answers those, so leave them to the bus. */
	if (p_message_get_type(msg) != DBUS_MESSAGE_TYPE_METHOD_CALL)
		return DBUS_HANDLER_RESULT_NOT_YET_HANDLED;

	path = p_get_path(msg);
	iface = p_get_interface(msg);
	member = p_get_member(msg);
	signature = p_get_signature(msg);

	if (!member || !signature)	/* impossible for a valid method call */
		return DBUS_HANDLER_RESULT_HANDLED;

	say("call path=%s interface=%s member=%s signature=%s\n",
	    path ? path : "(null)", iface ? iface : "(null)", member, signature);

	if (!served_path(path)) {
		say("unknown object path %s -> %s\n", path ? path : "(null)",
		    ERR_UNKNOWN_OBJECT);
		reply_error(conn, msg, ERR_UNKNOWN_OBJECT,
			    "object path not provided by micom research service");
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}

	if (iface && strcmp(iface, INTROSPECTABLE_INTERFACE) == 0 &&
	    strcmp(member, "Introspect") == 0 &&
	    strcmp(signature, "") == 0) {
		specific = strcmp(path, IHU_PATH) == 0 ? ihu_xml :
			   strcmp(path, CAN_PATH) == 0 ? can_xml : audio_xml;
		if ((size_t)snprintf(xml, sizeof xml, "%s%s", specific, common_xml) >=
		    sizeof xml) {
			reply_error(conn, msg, "org.freedesktop.DBus.Error.Failed",
				    "introspection document exceeded fixed buffer");
		} else {
			reply_string(conn, msg, xml);
			say("Introspect %s -> %zu bytes\n", path, strlen(xml));
		}
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}

	if (iface && strcmp(iface, PEER_INTERFACE) == 0 &&
	    strcmp(member, "Ping") == 0) {
		reply_empty(conn, msg);
		say("Ping %s -> empty\n", path);
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}

	if (exact_call(path, iface, member, signature, IHU_PATH, IHU_INTERFACE,
		       "AskSysBootinfo", "")) {
		serve_bootinfo(conn, msg);
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}

	if (serve_fixed_ay(conn, msg, path, iface, member, signature)) {
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}

	/* Documented-but-unimplemented asks from the v2 contract, answered with the
	 * same shapes this service has always returned. */
	if (serve_contract_ask(conn, msg, path, iface, member, signature)) {
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}
	if (exact_call(path, iface, member, signature, IHU_PATH, IHU_INTERFACE,
		       "AskCustomSetting", "ay")) {
		static const unsigned char v[16];
		reply_ay(conn, msg, v, sizeof v);
		say("AskCustomSetting -> 16 zero bytes\n");
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}
	if (exact_call(path, iface, member, signature, IHU_PATH, IHU_INTERFACE,
		       "AskSettingInfoValue", "")) {
		static const unsigned char v[8] = { 0, 0, 0, 0, 0, 0, 0, 1 };
		reply_ay(conn, msg, v, sizeof v);
		say("AskSettingInfoValue -> 8 bytes\n");
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}

	ack = find_ack(path, iface, member, signature);
	if (ack) {
		reply_empty(conn, msg);
		if (answered < 40)
			say("ack %s %s -> empty\n", ack->path, ack->member);
		answered++;
		return DBUS_HANDLER_RESULT_HANDLED;
	}

	say("unknown method %s %s.%s signature=%s -> %s\n", path,
	    iface ? iface : "(null)", member, signature, ERR_UNKNOWN_METHOD);
	reply_error(conn, msg, ERR_UNKNOWN_METHOD,
		    "method not implemented by micom research service");
	answered++;
	return DBUS_HANDLER_RESULT_HANDLED;
}

static const DBusObjectPathVTable vtable = {
	NULL, on_message, NULL, NULL, NULL, NULL,
};

static int register_served_paths(DBusConnection *conn)
{
	static const char *paths[] = { IHU_PATH, CAN_PATH, AUDIO_PATH };
	unsigned int i;

	for (i = 0; i < sizeof paths / sizeof paths[0]; i++) {
		if (!p_register_path(conn, paths[i], &vtable, NULL)) {
			say("register_object_path %s failed\n", paths[i]);
			return -1;
		}
	}
	return 0;
}

int main(void)
{
	DBusConnection *conn;
	int rc;

	if (resolve() < 0) {
		say("libdbus symbols missing\n");
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
		rc = p_request_name(conn, BUS_NAME,
				    DBUS_NAME_FLAG_REPLACE_EXISTING | DBUS_NAME_FLAG_DO_NOT_QUEUE, NULL);
		if (attempt == 0 || rc == 1)
			say("request_name %s -> %d (attempt %d)\n", BUS_NAME, rc, attempt + 1);
		if (rc == 1)
			break;
		usleep(500000);
	}
	if (rc != 1) {
		say("could not become primary owner (rc=%d); serving anyway\n", rc);
	}

	if (register_served_paths(conn) < 0)
		return 1;
	say("serving %s, %s, %s (ihu/can/audio)\n", IHU_PATH, CAN_PATH, AUDIO_PATH);

	for (;;) {
		if (!p_read_write_dispatch(conn, 1000))
			break;
	}
	say("dispatch loop ended after %u answers\n", answered);
	return 0;
}
