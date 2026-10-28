/*
 * Narrow VM simulator for the recovered Gen5W micom D-Bus boot-info boundary.
 *
 * Usage: micom-dbus-sim BOOTINFO_HEX
 *
 * BOOTINFO_HEX must encode exactly the 35 bytes consumed by EU 260128
 * AppLauncher::parseMicomBootInfo().  The simulator owns the recovered system-
 * bus name and exposes only /Ihu com.lge.car.micom.ihu.AskSysBootinfo. Unknown
 * calls fail closed and are logged. This is research infrastructure, not OEM
 * firmware and not a general micom/CAN implementation.
 */
#include <dbus/dbus.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BOOTINFO_SIZE 35
#define BUS_NAME "com.lge.car.micom"
#define IHU_PATH "/Ihu"
#define IHU_INTERFACE "com.lge.car.micom.ihu"
#define CAN_PATH "/Can"
#define CAN_INTERFACE "com.lge.car.micom.can"
#define AUDIO_PATH "/com/lge/car/micom"
#define AUDIO_INTERFACE "com.lge.car.micom.audio"
#define METHOD "AskSysBootinfo"

static volatile sig_atomic_t keep_running = 1;

static void stop_handler(int signo)
{
    (void)signo;
    keep_running = 0;
}

static int hex_nibble(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static int parse_bootinfo(const char *hex, uint8_t out[BOOTINFO_SIZE])
{
    size_t i;
    if (strlen(hex) != BOOTINFO_SIZE * 2)
        return 0;
    for (i = 0; i < BOOTINFO_SIZE; ++i) {
        int hi = hex_nibble(hex[i * 2]);
        int lo = hex_nibble(hex[i * 2 + 1]);
        if (hi < 0 || lo < 0)
            return 0;
        out[i] = (uint8_t)((hi << 4) | lo);
    }
    return 1;
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

static int send_bootinfo(DBusConnection *connection, DBusMessage *request,
                         const uint8_t bootinfo[BOOTINFO_SIZE])
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    DBusMessageIter root, array;
    const uint8_t *data = bootinfo;
    if (reply == NULL)
        return 0;
    dbus_message_iter_init_append(reply, &root);
    if (!dbus_message_iter_open_container(&root, DBUS_TYPE_ARRAY,
                                           DBUS_TYPE_BYTE_AS_STRING, &array) ||
        !dbus_message_iter_append_fixed_array(&array, DBUS_TYPE_BYTE, &data,
                                               BOOTINFO_SIZE) ||
        !dbus_message_iter_close_container(&root, &array)) {
        dbus_message_unref(reply);
        return 0;
    }
    return send_message(connection, reply);
}

static int send_string(DBusConnection *connection, DBusMessage *request,
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

static int send_empty(DBusConnection *connection, DBusMessage *request)
{
    return send_message(connection, dbus_message_new_method_return(request));
}

static int send_error(DBusConnection *connection, DBusMessage *request,
                      const char *name, const char *text)
{
    return send_message(connection, dbus_message_new_error(request, name, text));
}

static void log_arguments(DBusMessage *request)
{
    DBusMessageIter iter;
    unsigned int argument = 0;
    if (!dbus_message_iter_init(request, &iter))
        return;
    do {
        int type = dbus_message_iter_get_arg_type(&iter);
        if (type == DBUS_TYPE_ARRAY &&
            dbus_message_iter_get_element_type(&iter) == DBUS_TYPE_BYTE) {
            DBusMessageIter array;
            const uint8_t *data = NULL;
            int length = 0;
            int i;
            dbus_message_iter_recurse(&iter, &array);
            dbus_message_iter_get_fixed_array(&array, &data, &length);
            printf("MICOM_DBUS_SIM_ARG index=%u type=ay length=%d hex=", argument,
                   length);
            for (i = 0; i < length; ++i)
                printf("%02x", data[i]);
            putchar('\n');
        } else if (type == DBUS_TYPE_INT32) {
            int32_t value;
            dbus_message_iter_get_basic(&iter, &value);
            printf("MICOM_DBUS_SIM_ARG index=%u type=i value=%d\n", argument,
                   value);
        } else {
            printf("MICOM_DBUS_SIM_ARG index=%u type=%c unsupported-log-type\n",
                   argument, type);
        }
        ++argument;
    } while (dbus_message_iter_next(&iter));
    fflush(stdout);
}

static int exact_call(DBusMessage *request, const char *path, const char *iface,
                      const char *member, const char *signature)
{
    const char *actual_path = dbus_message_get_path(request);
    return actual_path != NULL && strcmp(actual_path, path) == 0 &&
           dbus_message_is_method_call(request, iface, member) &&
           strcmp(dbus_message_get_signature(request), signature) == 0;
}

static int is_transport_ack(DBusMessage *request)
{
    static const char *ihu_ay[] = {
        "SetControlKeyLock", "SetETCCPUAliveMsg", "SetETCAppBootComplete",
        "SetDIDInfo", NULL
    };
    static const char *can_ay[] = {
        "AskCANMMCANMicomReq", "AskCANICANMicomReq", "SetCANMicomRecv",
        "SetCANTPMicomRecv", NULL
    };
    static const char *can_empty[] = {
        "SetDATCInitialRequest", "SetCARSETInitialRequest",
        "SetLowFuelWarnningRequest", NULL
    };
    const char **name;
    for (name = ihu_ay; *name != NULL; ++name)
        if (exact_call(request, IHU_PATH, IHU_INTERFACE, *name, "ay"))
            return 1;
    for (name = can_ay; *name != NULL; ++name)
        if (exact_call(request, CAN_PATH, CAN_INTERFACE, *name, "ay"))
            return 1;
    for (name = can_empty; *name != NULL; ++name)
        if (exact_call(request, CAN_PATH, CAN_INTERFACE, *name, ""))
            return 1;
    return exact_call(request, CAN_PATH, CAN_INTERFACE,
                      "SetCANFixedMicomRecv", "ayiii");
}

int main(int argc, char **argv)
{
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
    uint8_t bootinfo[BOOTINFO_SIZE];
    DBusConnection *connection;
    DBusError error;
    int request_result;

    if (argc != 2 || !parse_bootinfo(argv[1], bootinfo)) {
        fprintf(stderr, "usage: %s BOOTINFO_HEX (exactly 35 bytes)\n", argv[0]);
        return 2;
    }

    dbus_error_init(&error);
    connection = dbus_bus_get(DBUS_BUS_SYSTEM, &error);
    if (connection == NULL) {
        fprintf(stderr, "dbus_bus_get: %s: %s\n",
                error.name ? error.name : "unknown",
                error.message ? error.message : "unknown");
        dbus_error_free(&error);
        return 3;
    }
    dbus_connection_set_exit_on_disconnect(connection, FALSE);
    request_result = dbus_bus_request_name(connection, BUS_NAME,
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

    signal(SIGINT, stop_handler);
    signal(SIGTERM, stop_handler);
    printf("MICOM_DBUS_SIM_READY profile=%s bytes=%d\n", argv[1], BOOTINFO_SIZE);
    fflush(stdout);

    while (keep_running && dbus_connection_get_is_connected(connection)) {
        DBusMessage *request;
        const char *path;
        const char *iface;
        const char *member;

        dbus_connection_read_write(connection, 250);
        request = dbus_connection_pop_message(connection);
        if (request == NULL)
            continue;
        if (dbus_message_get_type(request) != DBUS_MESSAGE_TYPE_METHOD_CALL) {
            dbus_message_unref(request);
            continue;
        }
        path = dbus_message_get_path(request);
        iface = dbus_message_get_interface(request);
        member = dbus_message_get_member(request);
        printf("MICOM_DBUS_SIM_CALL sender=%s path=%s interface=%s member=%s signature=%s\n",
               dbus_message_get_sender(request) ? dbus_message_get_sender(request) : "(null)",
               path ? path : "(null)", iface ? iface : "(null)",
               member ? member : "(null)", dbus_message_get_signature(request));
        log_arguments(request);

        if (path == NULL || (strcmp(path, IHU_PATH) != 0 &&
                             strcmp(path, CAN_PATH) != 0 &&
                             strcmp(path, AUDIO_PATH) != 0)) {
            send_error(connection, request, DBUS_ERROR_UNKNOWN_OBJECT,
                       "object path not provided by micom research simulator");
        } else if (dbus_message_is_method_call(
                       request, "org.freedesktop.DBus.Introspectable", "Introspect")) {
            char xml[4096];
            const char *specific = strcmp(path, IHU_PATH) == 0 ? ihu_xml :
                                   strcmp(path, CAN_PATH) == 0 ? can_xml : audio_xml;
            if ((size_t)snprintf(xml, sizeof(xml), "%s%s", specific, common_xml) >=
                sizeof(xml))
                send_error(connection, request, DBUS_ERROR_FAILED,
                           "introspection document exceeded fixed buffer");
            else
                send_string(connection, request, xml);
        } else if (dbus_message_is_method_call(
                       request, "org.freedesktop.DBus.Peer", "Ping")) {
            send_empty(connection, request);
        } else if (dbus_message_is_method_call(request, IHU_INTERFACE, METHOD) &&
                   strcmp(path, IHU_PATH) == 0 &&
                   strcmp(dbus_message_get_signature(request), "") == 0) {
            send_bootinfo(connection, request, bootinfo);
        } else if (is_transport_ack(request)) {
            printf("MICOM_DBUS_SIM_ACK path=%s interface=%s member=%s\n",
                   path, iface, member);
            fflush(stdout);
            send_empty(connection, request);
        } else {
            send_error(connection, request, DBUS_ERROR_UNKNOWN_METHOD,
                       "method not implemented by micom research simulator");
        }
        dbus_message_unref(request);
    }

    dbus_bus_release_name(connection, BUS_NAME, NULL);
    dbus_connection_unref(connection);
    return 0;
}
