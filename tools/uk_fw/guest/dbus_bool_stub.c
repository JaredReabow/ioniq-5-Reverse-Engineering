/*
 * Minimal D-Bus method stub for isolated recovered-userspace probes.
 *
 * Usage:
 *   dbus-bool-stub BUS_NAME OBJECT_PATH INTERFACE METHOD [true|false]
 *
 * The process owns BUS_NAME on DBUS_SESSION_BUS_ADDRESS and returns one
 * boolean from the selected method.  It also implements Introspect and Peer
 * Ping/GetMachineId sufficiently for Qt D-Bus clients.  This is VM research
 * infrastructure, not recovered Hyundai/LG firmware.
 */
#include <dbus/dbus.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static volatile sig_atomic_t keep_running = 1;

static void stop_handler(int signo)
{
    (void)signo;
    keep_running = 0;
}

static int send_message(DBusConnection *connection, DBusMessage *reply)
{
    if (reply == NULL)
        return 0;
    if (!dbus_connection_send(connection, reply, NULL)) {
        dbus_message_unref(reply);
        return 0;
    }
    dbus_connection_flush(connection);
    dbus_message_unref(reply);
    return 1;
}

static int send_empty_return(DBusConnection *connection, DBusMessage *request)
{
    return send_message(connection, dbus_message_new_method_return(request));
}

static int send_bool_return(DBusConnection *connection, DBusMessage *request,
                            dbus_bool_t value)
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    if (reply == NULL)
        return 0;
    if (!dbus_message_append_args(reply, DBUS_TYPE_BOOLEAN, &value,
                                  DBUS_TYPE_INVALID)) {
        dbus_message_unref(reply);
        return 0;
    }
    return send_message(connection, reply);
}

static int send_string_return(DBusConnection *connection, DBusMessage *request,
                              const char *value)
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    if (reply == NULL)
        return 0;
    if (!dbus_message_append_args(reply, DBUS_TYPE_STRING, &value,
                                  DBUS_TYPE_INVALID)) {
        dbus_message_unref(reply);
        return 0;
    }
    return send_message(connection, reply);
}

static int send_error(DBusConnection *connection, DBusMessage *request,
                      const char *name, const char *text)
{
    return send_message(connection,
                        dbus_message_new_error(request, name, text));
}

int main(int argc, char **argv)
{
    DBusConnection *connection;
    DBusError error;
    const char *bus_name;
    const char *object_path;
    const char *interface;
    const char *method;
    dbus_bool_t result = FALSE;
    int request_result;
    char introspection[2048];

    if (argc != 5 && argc != 6) {
        fprintf(stderr,
                "usage: %s BUS_NAME OBJECT_PATH INTERFACE METHOD [true|false]\n",
                argv[0]);
        return 2;
    }
    bus_name = argv[1];
    object_path = argv[2];
    interface = argv[3];
    method = argv[4];
    if (argc == 6) {
        if (strcmp(argv[5], "true") == 0 || strcmp(argv[5], "1") == 0)
            result = TRUE;
        else if (strcmp(argv[5], "false") != 0 && strcmp(argv[5], "0") != 0) {
            fprintf(stderr, "boolean must be true, false, 1, or 0\n");
            return 2;
        }
    }

    dbus_error_init(&error);
    connection = dbus_bus_get(DBUS_BUS_SESSION, &error);
    if (connection == NULL) {
        fprintf(stderr, "dbus_bus_get: %s: %s\n",
                error.name ? error.name : "unknown",
                error.message ? error.message : "unknown");
        dbus_error_free(&error);
        return 3;
    }
    dbus_connection_set_exit_on_disconnect(connection, FALSE);
    request_result = dbus_bus_request_name(connection, bus_name,
                                            DBUS_NAME_FLAG_DO_NOT_QUEUE, &error);
    if (dbus_error_is_set(&error)) {
        fprintf(stderr, "dbus_bus_request_name: %s: %s\n",
                error.name, error.message);
        dbus_error_free(&error);
        dbus_connection_unref(connection);
        return 4;
    }
    if (request_result != DBUS_REQUEST_NAME_REPLY_PRIMARY_OWNER &&
        request_result != DBUS_REQUEST_NAME_REPLY_ALREADY_OWNER) {
        fprintf(stderr, "name request rejected: %d\n", request_result);
        dbus_connection_unref(connection);
        return 5;
    }

    snprintf(introspection, sizeof(introspection),
             "<node>"
             "<interface name=\"%s\">"
             "<method name=\"%s\">"
             "<arg direction=\"in\" type=\"i\"/>"
             "<arg direction=\"out\" type=\"b\"/>"
             "</method>"
             "</interface>"
             "<interface name=\"org.freedesktop.DBus.Introspectable\">"
             "<method name=\"Introspect\"><arg direction=\"out\" type=\"s\"/>"
             "</method></interface>"
             "</node>", interface, method);

    signal(SIGINT, stop_handler);
    signal(SIGTERM, stop_handler);
    printf("DBUS_BOOL_STUB_READY name=%s path=%s interface=%s method=%s value=%d\n",
           bus_name, object_path, interface, method, result ? 1 : 0);
    fflush(stdout);

    while (keep_running && dbus_connection_get_is_connected(connection)) {
        DBusMessage *request;
        const char *path;

        dbus_connection_read_write(connection, 250);
        request = dbus_connection_pop_message(connection);
        if (request == NULL)
            continue;
        if (dbus_message_get_type(request) != DBUS_MESSAGE_TYPE_METHOD_CALL) {
            dbus_message_unref(request);
            continue;
        }
        path = dbus_message_get_path(request);
        if (path == NULL || strcmp(path, object_path) != 0) {
            send_error(connection, request, DBUS_ERROR_UNKNOWN_OBJECT,
                       "object path not provided by research stub");
        } else if (dbus_message_is_method_call(
                       request, "org.freedesktop.DBus.Introspectable",
                       "Introspect")) {
            send_string_return(connection, request, introspection);
        } else if (dbus_message_is_method_call(
                       request, "org.freedesktop.DBus.Peer", "Ping")) {
            send_empty_return(connection, request);
        } else if (dbus_message_is_method_call(
                       request, "org.freedesktop.DBus.Peer", "GetMachineId")) {
            send_string_return(connection, request,
                               "00000000000000000000000000000000");
        } else if (dbus_message_is_method_call(request, interface, method)) {
            printf("DBUS_BOOL_STUB_CALL sender=%s signature=%s\n",
                   dbus_message_get_sender(request) ?
                       dbus_message_get_sender(request) : "(null)",
                   dbus_message_get_signature(request));
            fflush(stdout);
            send_bool_return(connection, request, result);
        } else {
            send_error(connection, request, DBUS_ERROR_UNKNOWN_METHOD,
                       "method not provided by research stub");
        }
        dbus_message_unref(request);
    }

    dbus_bus_release_name(connection, bus_name, NULL);
    dbus_connection_unref(connection);
    return 0;
}
