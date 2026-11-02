/* persistence_admin_stub — research adaptor that owns org.genivi.persistence.admin on the system bus.
 *
 * The image ships libpersistence_client_library.so.7, the interface XML
 * (/usr/share/dbus-1/interfaces/org.genivi.persistence.admin.xml) and two D-Bus policy files,
 * but no daemon that provides the name. On the running projection `dbus-send` to
 * org.genivi.persistence.admin returns org.freedesktop.DBus.Error.ServiceUnknown.
 * AppHomeScreen, AppCamera and AppOSDManager share this client library and die in free()+0x14;
 * whether the missing service is the cause is a hypothesis this stub exists to test, not a claim.
 *
 * It owns the name, serves /org/genivi/persistence/admin with both interfaces declared in the
 * shipped XML, answers org.freedesktop.DBus.Introspectable.Introspect and
 * org.freedesktop.DBus.Peer.Ping, and replies org.freedesktop.DBus.Error.UnknownMethod to
 * anything else so no caller is left waiting. libdbus is resolved with dlopen because this cross
 * build has no development headers for it — same arrangement as micom_service.c.
 *
 * A shim standing in for vendor behaviour, not vendor behaviour.
 *
 * BUILD NOTE: build.sh always links with -shared, so its product is a plugin (e_entry == 0) and
 * cannot be executed — the kernel enters it at the load base and it dies before main(). This file
 * must be linked as an executable to be a daemon:
 *   zig cc -target x86_64-linux-gnu -O1 -o persistence-admin-service persistence_admin_stub.c
 */
/* usleep() is declared by glibc only under _DEFAULT_SOURCE; the build does not pass -std=c99,
 * but this keeps a strict-mode compile clean too. */
#define _DEFAULT_SOURCE 1
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

/* dbus_bus_request_name() return codes */
#define REQUEST_NAME_PRIMARY_OWNER 1

/* DBusMessageType */
#define DBUS_MESSAGE_TYPE_METHOD_CALL 1

/* DBusHandlerResult: these are the public values, not micom_service.c's placeholder. */
#define NOT_YET_HANDLED 0
#define HANDLED 1

#define DBUS_TYPE_INVALID ((int) '\0')
#define DBUS_TYPE_STRING  ((int) 's')
#define DBUS_TYPE_INT32   ((int) 'i')
#define DBUS_TYPE_UINT32  ((int) 'u')

#define ADMIN_IFACE    "org.genivi.persistence.admin"
#define CONSUMER_IFACE "org.genivi.persistence.adminconsumer"
#define SERVICE_NAME   ADMIN_IFACE
#define SERVICE_PATH   "/org/genivi/persistence/admin"

#define PEER_IFACE          "org.freedesktop.DBus.Peer"
#define INTROSPECTABLE_IFACE "org.freedesktop.DBus.Introspectable"

#define ERR_UNKNOWN_METHOD "org.freedesktop.DBus.Error.UnknownMethod"

/* ErrorCode returned by every implemented method.
 * GUESS: the shipped XML types ErrorCode as int32 but never enumerates values, and the image
 * ships no administrative daemon to copy behaviour from. 0 is reported as success here. */
#define PERS_ERROR_CODE_OK 0

typedef struct DBusConnection DBusConnection;
typedef struct DBusMessage DBusMessage;
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
static unsigned int unknown;

/* Console output goes through write(2) on an fd obtained here, never through stdio: the first
 * line has to survive on /dev/ttyS0 even if the crash happens immediately afterwards, and stdio
 * buffers are lost on a hard fault. */
static void open_console(void)
{
	if (log_fd < 0) {
		log_fd = open("/tmp/persist-stub.log", O_WRONLY | O_CREAT | O_APPEND | O_NOCTTY, 0644);
		if (log_fd < 0)
			log_fd = open("/dev/console", O_WRONLY | O_NOCTTY);
	}
}

static void say(const char *fmt, ...)
{
	char msg[448];
	char line[512];
	va_list ap;
	size_t n;

	va_start(ap, fmt);
	vsnprintf(msg, sizeof msg, fmt, ap);
	va_end(ap);
	snprintf(line, sizeof line, "persadmin-svc: %s", msg);
	n = strlen(line);

	open_console();
	/* stderr first: if ttyS0 is not yet a usable console, fd 2 still reaches the log. */
	if (write(2, line, n) < 0) { /* nothing useful to do if even stderr is gone */ }
	if (log_fd >= 0 && write(log_fd, line, n) < 0) { /* same */ }
}

/* Runs from .init_array, i.e. before main. If this line is absent from the serial log the image
 * never reached libc startup and the fault is in the ELF entry point, not in this code. */
__attribute__((constructor))
static void announce_load(void)
{
	say("image loaded (constructor reached), pid will follow\n");
}

static DBusConnection *(*p_bus_get)(int, void *);
static int (*p_request_name)(DBusConnection *, const char *, unsigned int, void *);
static int (*p_register_path)(DBusConnection *, const char *, const DBusObjectPathVTable *, void *);
static DBusMessage *(*p_new_method_return)(DBusMessage *);
static DBusMessage *(*p_new_error)(DBusMessage *, const char *, const char *);
static int (*p_iter_init_append)(DBusMessage *, DBusMessageIter *);
static int (*p_append_basic)(DBusMessageIter *, int, const void *);
static int (*p_send)(DBusConnection *, DBusMessage *, unsigned int *);
static void (*p_flush)(DBusConnection *);
static int (*p_read_write_dispatch)(DBusConnection *, int);
static const char *(*p_get_member)(DBusMessage *);
static const char *(*p_get_interface)(DBusMessage *);
static const char *(*p_get_sender)(DBusMessage *);
static int (*p_get_type)(DBusMessage *);
static int (*p_iter_init)(DBusMessage *, DBusMessageIter *);
static int (*p_iter_get_arg_type)(DBusMessageIter *);
static int (*p_iter_get_basic)(DBusMessageIter *, void *);
static int (*p_iter_next)(DBusMessageIter *);
static void (*p_message_unref)(DBusMessage *);

/* Every libdbus entry point this stub uses, with the prototype it is called through. dbus_bool_t
 * is a 4-byte int on x86-64, so every boolean return is declared int. This list is the whole
 * surface: if a symbol is missing the daemon refuses to run rather than calling NULL.
 *
 *   DBusConnection *dbus_bus_get(DBusBusType, DBusError *)
 *   int             dbus_bus_request_name(DBusConnection *, const char *, unsigned int, DBusError *)
 *   dbus_bool_t     dbus_connection_register_object_path(DBusConnection *, const char *,
 *                                                       const DBusObjectPathVTable *, void *)
 *   DBusMessage    *dbus_message_new_method_return(DBusMessage *)
 *   DBusMessage    *dbus_message_new_error(DBusMessage *, const char *, const char *)
 *   dbus_bool_t     dbus_message_iter_init_append(DBusMessage *, DBusMessageIter *)
 *   dbus_bool_t     dbus_message_iter_append_basic(DBusMessageIter *, int, const void *)
 *   dbus_bool_t     dbus_connection_send(DBusConnection *, DBusMessage *, dbus_uint32_t *)
 *   void            dbus_connection_flush(DBusConnection *)
 *   dbus_bool_t     dbus_connection_read_write_dispatch(DBusConnection *, int)
 *   const char     *dbus_message_get_member(DBusMessage *)
 *   const char     *dbus_message_get_interface(DBusMessage *)
 *   const char     *dbus_message_get_sender(DBusMessage *)
 *   int             dbus_message_get_type(DBusMessage *)
 *   dbus_bool_t     dbus_message_iter_init(DBusMessage *, DBusMessageIter *)
 *   int             dbus_message_iter_get_arg_type(DBusMessageIter *)
 *   dbus_bool_t     dbus_message_iter_get_basic(DBusMessageIter *, void *)
 *   dbus_bool_t     dbus_message_iter_next(DBusMessageIter *)
 *   void            dbus_message_unref(DBusMessage *)
 */
struct sym {
	const char *name;
	void **slot;
	int required;
};

/* One table, one loop: no pointer can be left unset by a forgotten assignment, and a symbol the
 * guest's libdbus does not export is named in the log instead of becoming a NULL call. */
static int resolve(void)
{
	static const struct sym syms[] = {
		{ "dbus_bus_get", (void **) &p_bus_get, 1 },
		{ "dbus_bus_request_name", (void **) &p_request_name, 1 },
		{ "dbus_connection_register_object_path", (void **) &p_register_path, 1 },
		{ "dbus_message_new_method_return", (void **) &p_new_method_return, 1 },
		{ "dbus_message_new_error", (void **) &p_new_error, 1 },
		{ "dbus_message_iter_init_append", (void **) &p_iter_init_append, 1 },
		{ "dbus_message_iter_append_basic", (void **) &p_append_basic, 1 },
		{ "dbus_connection_send", (void **) &p_send, 1 },
		{ "dbus_connection_flush", (void **) &p_flush, 1 },
		{ "dbus_connection_read_write_dispatch", (void **) &p_read_write_dispatch, 1 },
		{ "dbus_message_get_member", (void **) &p_get_member, 1 },
		{ "dbus_message_get_interface", (void **) &p_get_interface, 1 },
		{ "dbus_message_get_sender", (void **) &p_get_sender, 0 },
		{ "dbus_message_get_type", (void **) &p_get_type, 1 },
		{ "dbus_message_iter_init", (void **) &p_iter_init, 1 },
		{ "dbus_message_iter_get_arg_type", (void **) &p_iter_get_arg_type, 1 },
		{ "dbus_message_iter_get_basic", (void **) &p_iter_get_basic, 1 },
		{ "dbus_message_iter_next", (void **) &p_iter_next, 1 },
		{ "dbus_message_unref", (void **) &p_message_unref, 1 },
	};
	const char *tried = "libdbus-1.so.3";
	void *h;
	unsigned int missing = 0, total = 0, i;

	h = dlopen("libdbus-1.so.3", RTLD_NOW);
	if (!h) {
		say("dlopen(libdbus-1.so.3) failed: %s\n", dlerror());
		tried = "libdbus-1.so";
		h = dlopen("libdbus-1.so", RTLD_NOW);
	}
	if (!h) {
		say("dlopen(libdbus-1.so) failed: %s\n", dlerror());
		return -1;
	}
	say("dlopen(%s) -> %p\n", tried, h);

	for (i = 0; i < sizeof syms / sizeof syms[0]; i++) {
		if (syms[i].required)
			total++;
		*syms[i].slot = dlsym(h, syms[i].name);
		if (!*syms[i].slot) {
			say("dlsym %s -> NULL (%s)%s\n", syms[i].name, dlerror(),
			    syms[i].required ? " [required]" : " [optional]");
			if (syms[i].required)
				missing++;
		}
	}
	if (missing) {
		say("%u of %u required libdbus symbols missing; refusing to serve\n",
		    missing, total);
		return -1;
	}
	say("resolved all %u required libdbus symbols\n", total);
	return 0;
}

/* Read-only dump of the call's arguments for the serial log. Purely diagnostic: a type it does
 * not understand stops the walk instead of being forced through get_basic. */
static void log_args(DBusMessage *msg)
{
	DBusMessageIter it;
	int n = 0;

	if (!p_iter_init || !p_iter_get_arg_type || !p_iter_get_basic || !p_iter_next) {
		say(" args=<no iterator symbols>");
		return;
	}
	if (!p_iter_init(msg, &it)) {
		say(" args=<none>");
		return;
	}
	for (;;) {
		int t = p_iter_get_arg_type(&it);

		if (t == DBUS_TYPE_INVALID)
			break;
		if (n >= 8) {
			say(" args=<truncated>");
			break;
		}
		if (t == DBUS_TYPE_STRING) {
			const char *s = NULL;
			p_iter_get_basic(&it, &s);
			say(" arg%d='%s'", n, s ? s : "(null)");
		} else if (t == DBUS_TYPE_INT32) {
			int v = 0;
			p_iter_get_basic(&it, &v);
			say(" arg%d=i%d", n, v);
		} else if (t == DBUS_TYPE_UINT32) {
			unsigned int v = 0;
			p_iter_get_basic(&it, &v);
			say(" arg%d=u%u", n, v);
		} else {
			say(" arg%d=<type '%c'>", n, (t > 32 && t < 127) ? t : '?');
			break;
		}
		n++;
		if (!p_iter_next(&it))
			break;
	}
}

/* Every reply path funnels through these so a failed allocation can never send a half-built
 * message or take the daemon down. */
static void send_reply(DBusConnection *conn, DBusMessage *reply)
{
	if (!reply)
		return;
	if (!p_send || !p_flush || !p_message_unref) {
		/* Unreachable while resolve() gates main(), but a NULL call here is precisely the
		 * failure mode this stub must never exhibit. */
		say("BUG: unresolved send/flush/unref; dropping reply\n");
		return;
	}
	p_send(conn, reply, NULL);
	p_flush(conn);
	p_message_unref(reply);
}

static void reply_error_code(DBusConnection *conn, DBusMessage *msg, int code)
{
	DBusMessage *reply = p_new_method_return(msg);
	DBusMessageIter it;

	if (!reply)
		return;
	if (!p_iter_init_append(reply, &it)) {
		p_message_unref(reply);
		return;
	}
	/* <arg name="ErrorCode" type="i" direction="out"/> */
	p_append_basic(&it, DBUS_TYPE_INT32, &code);
	send_reply(conn, reply);
}

static void reply_string(DBusConnection *conn, DBusMessage *msg, const char *s)
{
	DBusMessage *reply = p_new_method_return(msg);
	DBusMessageIter it;

	if (!reply)
		return;
	if (!p_iter_init_append(reply, &it)) {
		p_message_unref(reply);
		return;
	}
	p_append_basic(&it, DBUS_TYPE_STRING, &s);
	send_reply(conn, reply);
}

static void reply_empty(DBusConnection *conn, DBusMessage *msg)
{
	send_reply(conn, p_new_method_return(msg));
}

static void reply_unknown_method(DBusConnection *conn, DBusMessage *msg, const char *iface,
				 const char *member)
{
	char detail[256];
	DBusMessage *reply;

	snprintf(detail, sizeof detail, "no such method %s.%s",
		 iface ? iface : "(no interface)", member ? member : "(no member)");
	reply = p_new_error(msg, ERR_UNKNOWN_METHOD, detail);
	send_reply(conn, reply);
}

/* A real XML document describing exactly what this process answers, so a client that
 * introspects before calling sees the two vendor interfaces plus the two standard ones. */
static const char introspection_xml[] =
"<!DOCTYPE node PUBLIC \"-//freedesktop//DTD D-BUS Object Introspection 1.0//EN\"\n"
" \"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd\">\n"
"<node name=\"/org/genivi/persistence/admin\">\n"
"  <interface name=\"org.genivi.persistence.admin\">\n"
"    <method name=\"RegisterPersAdminNotification\">\n"
"      <arg name=\"BusName\" type=\"s\" direction=\"in\"/>\n"
"      <arg name=\"ObjName\" type=\"s\" direction=\"in\"/>\n"
"      <arg name=\"NotificationFlag\" type=\"i\" direction=\"in\"/>\n"
"      <arg name=\"TimeoutMs\" type=\"u\" direction=\"in\"/>\n"
"      <arg name=\"AppPid\" type=\"u\" direction=\"in\"/>\n"
"      <arg name=\"ErrorCode\" type=\"i\" direction=\"out\"/>\n"
"    </method>\n"
"    <method name=\"UnRegisterPersAdminNotification\">\n"
"      <arg name=\"BusName\" type=\"s\" direction=\"in\"/>\n"
"      <arg name=\"ObjName\" type=\"s\" direction=\"in\"/>\n"
"      <arg name=\"NotificationFlag\" type=\"i\" direction=\"in\"/>\n"
"      <arg name=\"TimeoutMs\" type=\"u\" direction=\"in\"/>\n"
"      <arg name=\"ErrorCode\" type=\"i\" direction=\"out\"/>\n"
"    </method>\n"
"    <method name=\"PersistenceAdminRequestCompleted\">\n"
"      <arg name=\"RequestId\" type=\"u\" direction=\"in\"/>\n"
"      <arg name=\"Status\" type=\"i\" direction=\"in\"/>\n"
"      <arg name=\"ErrorCode\" type=\"i\" direction=\"out\"/>\n"
"    </method>\n"
"  </interface>\n"
"  <interface name=\"org.genivi.persistence.adminconsumer\">\n"
"    <method name=\"PersistenceAdminRequest\">\n"
"      <arg name=\"Request\" type=\"i\" direction=\"in\"/>\n"
"      <arg name=\"RequestId\" type=\"i\" direction=\"in\"/>\n"
"      <arg name=\"ErrorCode\" type=\"i\" direction=\"out\"/>\n"
"    </method>\n"
"  </interface>\n"
"  <interface name=\"org.freedesktop.DBus.Introspectable\">\n"
"    <method name=\"Introspect\">\n"
"      <arg name=\"xml_data\" type=\"s\" direction=\"out\"/>\n"
"    </method>\n"
"  </interface>\n"
"  <interface name=\"org.freedesktop.DBus.Peer\">\n"
"    <method name=\"Ping\"/>\n"
"  </interface>\n"
"</node>\n";

static int iface_is_ours(const char *iface)
{
	if (!iface)
		return 1;	/* no interface header: match on member name alone */
	return strcmp(iface, ADMIN_IFACE) == 0 ||
	       strcmp(iface, CONSUMER_IFACE) == 0 ||
	       strcmp(iface, PEER_IFACE) == 0 ||
	       strcmp(iface, INTROSPECTABLE_IFACE) == 0;
}

static int on_message(DBusConnection *conn, DBusMessage *msg, void *user)
{
	const char *member, *iface, *sender;

	(void)user;

	if (!p_get_type || p_get_type(msg) != DBUS_MESSAGE_TYPE_METHOD_CALL) {
		/* Signals, method replies and errors are not ours to answer. */
		return NOT_YET_HANDLED;
	}

	member = p_get_member(msg);
	iface = p_get_interface(msg);
	sender = p_get_sender ? p_get_sender(msg) : NULL;

	say("call %s.%s from %s", iface ? iface : "(none)",
	    member ? member : "(none)", sender ? sender : "(none)");
	log_args(msg);
	say("\n");

	if (!member) {
		say("UNRECOGNISED method call with no member\n");
		unknown++;
		reply_unknown_method(conn, msg, iface, member);
		return HANDLED;
	}

	if (!iface_is_ours(iface)) {
		say("UNRECOGNISED interface %s (member %s)\n", iface, member);
		unknown++;
		reply_unknown_method(conn, msg, iface, member);
		return HANDLED;
	}

	/* --- standard interfaces ------------------------------------------------- */

	if (strcmp(member, "Introspect") == 0) {
		reply_string(conn, msg, introspection_xml);
		say("Introspect -> %u bytes of XML\n",
		    (unsigned int) (sizeof introspection_xml - 1));
		answered++;
		return HANDLED;
	}
	if (strcmp(member, "Ping") == 0) {
		reply_empty(conn, msg);
		say("Ping -> empty reply\n");
		answered++;
		return HANDLED;
	}

	/* --- org.genivi.persistence.admin --------------------------------------- */

	/* RegisterPersAdminNotification(s s i u u) -> i
	 * UnRegisterPersAdminNotification(s s i u) -> i
	 * PersistenceAdminRequestCompleted(u i)  -> i
	 * PersistenceAdminRequest(i i)           -> i  (org.genivi.persistence.adminconsumer)
	 *
	 * All four are answered the same way: the declared single int32 ErrorCode.
	 * GUESS: nothing in the image says what a real daemon returns, and this stub
	 * keeps no registration or request state, so it reports success (0) for every
	 * call rather than inventing per-argument validation. */
	if (strcmp(member, "RegisterPersAdminNotification") == 0 ||
	    strcmp(member, "UnRegisterPersAdminNotification") == 0 ||
	    strcmp(member, "PersistenceAdminRequestCompleted") == 0 ||
	    strcmp(member, "PersistenceAdminRequest") == 0) {
		reply_error_code(conn, msg, PERS_ERROR_CODE_OK);
		say("%s -> ErrorCode=%d\n", member, PERS_ERROR_CODE_OK);
		answered++;
		return HANDLED;
	}

	say("UNRECOGNISED member %s on %s (no reply is correct, but silence hangs callers)\n",
	    member, iface ? iface : "(none)");
	unknown++;
	reply_unknown_method(conn, msg, iface, member);
	return HANDLED;
}

static const DBusObjectPathVTable vtable = {
	NULL, on_message, NULL, NULL, NULL, NULL,
};

int main(void)
{
	DBusConnection *conn;
	int rc = 0;

	/* The very first action, before dlopen and before any libdbus pointer is touched. If this
	 * line is missing from the serial log on a crash, this process never entered main() and the
	 * fault is at the image's entry point, not in anything below. */
	say("main() entered, before dlopen (pid %d)\n", (int) getpid());

	if (resolve() < 0) {
		say("libdbus unavailable; exiting without serving\n");
		return 1;
	}
	/* Belt and braces: resolve() already refuses to return 0 with a required pointer NULL. */
	if (!p_bus_get || !p_request_name || !p_register_path || !p_send ||
	    !p_read_write_dispatch) {
		say("BUG: required libdbus pointer NULL after resolve(); exiting\n");
		return 1;
	}

	conn = p_bus_get(DBUS_BUS_SYSTEM, NULL);
	if (!conn) {
		say("cannot connect to system bus\n");
		return 1;
	}
	/* Nothing else in the image provides this name, so the loop is here for the same
	 * reason as micom_service.c: a leftover owner must not stop us from taking over. */
	for (int attempt = 0; attempt < 40; attempt++) {
		rc = p_request_name(conn, SERVICE_NAME,
				    DBUS_NAME_FLAG_REPLACE_EXISTING | DBUS_NAME_FLAG_DO_NOT_QUEUE, NULL);
		if (attempt == 0 || rc == REQUEST_NAME_PRIMARY_OWNER)
			say("request_name " SERVICE_NAME " -> %d (attempt %d)\n", rc, attempt + 1);
		if (rc == REQUEST_NAME_PRIMARY_OWNER)
			break;
		usleep(500000);
	}
	if (rc != REQUEST_NAME_PRIMARY_OWNER) {
		say("could not become primary owner (rc=%d); serving anyway\n", rc);
	}

	if (!p_register_path(conn, SERVICE_PATH, &vtable, NULL)) {
		say("register_object_path " SERVICE_PATH " failed\n");
		return 1;
	}
	say("serving " SERVICE_PATH " " ADMIN_IFACE " + " CONSUMER_IFACE "\n");
	for (;;) {
		if (!p_read_write_dispatch(conn, 1000))
			break;
	}
	say("dispatch loop ended after %u answers, %u unrecognised\n", answered, unknown);
	return 0;
}
