/*
 * eng_data_sim — research adaptor that answers the engineering-mode data asks
 * that AppEngineerMode issues ~20 s after launch, every one of which currently
 * comes back empty and leaves the page body black.
 *
 * The six queries (DLT log -> D-Bus call), recovered from AppEngineerMode's own
 * QDBus proxy vtables and from disassembling its VR-version call site:
 *
 *   SysInfoEng::ResponseAskSysVersionEng      com.lge.car.micom.ihu    /Ihu   AskSysVersion       -> ay  (system bus)
 *   SysInfoEng::ResponseWipidInfo             com.lge.car.micom.can    /Can   AskAutotestWIPID    -> ay  (system bus)
 *   SysInfoEng::ResponseTracedateInfo         com.lge.car.micom.ihu    /Ihu   AskTraceDate        -> ay  (system bus)
 *   SystemProxyMethodEng::resRecvMicomPartInfo com.lge.car.micom.ihu   /Ihu   AskPartNumberInfo   -> ay  (system bus)
 *   EngAutoTestRefactor::resRecvUserModeInfo  com.lge.car.micom.ihu    /Ihu   AskFactoryModeInfo  -> ay  (system bus)
 *   AppEngineerModeEngine::Response_VH_VRVersion
 *                                             com.lge.hkmc.avn.AppVR   /com/lge/hkmc/avn/AppVR
 *                                             com.lge.avn.appvh.atversionvrreq AtVersionVrReq / AtVersionVrReqAll -> s (session bus)
 *
 * The first five are on the bus name com.lge.car.micom, which the older
 * /micom-dbus-sim also owns (to answer AskSysBootinfo for the launcher). This
 * process is a *superset* of that simulator: it keeps the proven boot-info and
 * transport-ack answers so the launcher still starts, and adds the six
 * engineering-mode replies. In the engdata chain it is the single owner of
 * com.lge.car.micom, so there is no name fight with the older simulator.
 *
 * Reply values are INVENTED but self-consistent with the EU 260128 build under
 * test; the UI only needs a well-formed, non-empty reply to stop being black,
 * and every field here is an ASCII identifier the QML renders verbatim.
 */
#include <dbus/dbus.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

/* ---- system bus: the micom name and its object paths ---- */
#define MICOM_BUS_NAME  "com.lge.car.micom"
#define IHU_PATH        "/Ihu"
#define IHU_INTERFACE   "com.lge.car.micom.ihu"
#define CAN_PATH        "/Can"
#define CAN_INTERFACE   "com.lge.car.micom.can"
#define ENG_PATH        "/Eng"
#define ENG_INTERFACE   "com.lge.car.micom.eng"
#define AUDIO_PATH      "/com/lge/car/micom"
#define AUDIO_INTERFACE "com.lge.car.micom.audio"

/* ---- session bus: AppVH's VR-version service ---- */
#define VR_BUS_NAME     "com.lge.hkmc.avn.AppVR"
#define VR_PATH         "/com/lge/hkmc/avn/AppVR"
#define VR_INTERFACE    "com.lge.avn.appvh.atversionvrreq"

#define INTROSPECTABLE  "org.freedesktop.DBus.Introspectable"
#define PEER_INTERFACE  "org.freedesktop.DBus.Peer"

#define BOOTINFO_LEN 35

static volatile sig_atomic_t keep_running = 1;

/* Simulator-owned debug-count setting. The consumer reads byte 0 of the
 * recovered AskDebuggingMode reply; zero is the observed off default. Other
 * values are deliberately labelled simulator inputs, not vehicle behaviour. */
static unsigned char sim_debug_count;
/* -1 means unconfigured; this is the recovered IHU field, not gear or speed. */
static int sim_parking_status = -1;

static int sim_parking_notify(DBusConnection *conn, int value)
{
    DBusMessage *msg = dbus_message_new_signal(IHU_PATH, IHU_INTERFACE,
                                               "NotifyETCCarIFStatusEvent");
    DBusMessageIter iter, array;
    unsigned char payload[2] = { 4, (unsigned char)value };
    const unsigned char *bytes = payload;
    int ok = 0;
    if (msg == NULL)
        return 0;
    dbus_message_iter_init_append(msg, &iter);
    if (dbus_message_iter_open_container(&iter, DBUS_TYPE_ARRAY, DBUS_TYPE_BYTE_AS_STRING, &array) &&
        dbus_message_iter_append_fixed_array(&array, DBUS_TYPE_BYTE, &bytes, 2) &&
        dbus_message_iter_close_container(&iter, &array) &&
        dbus_connection_send(conn, msg, NULL)) {
        dbus_connection_flush(conn);
        ok = 1;
    }
    dbus_message_unref(msg);
    return ok;
}

/* Host/guest control protocol, local to this VM (no second D-Bus owner):
 * atomically rename a complete ASCII command into
 * $ENG_DATA_SIM_CONTROL_DIR/eng-data-sim-command (default directory /tmp):
 *   ID GET debug_count\n
 *   ID SET debug_count N\n    N is canonical decimal 0..255
 *   ID GET parking_status\n
 *   ID SET parking_status N\n N is canonical 0 or 1; the latter emits the
 *                             recovered IHU subtype-4 status signal.
 * ID is 1..32 ASCII letters/digits/_/-. Serialize writers and wait for the
 * matching ID in eng-data-sim-reply before publishing the next command:
 *   ID OK debug_count N evidence=recovered-consumer-byte0\n
 *   ID OK parking_status N evidence=recovered-ihu-parking-status\n
 *   ID ERR reason\n
 * Repeating the most recent ID and exact command replays its receipt; reusing
 * that ID with different contents is rejected. The response confirms that the
 * simulator applied state, not that any guest consumer requested the value.
 * Guest observations are logged by the corresponding method handlers. An
 * unconfigured parking status is explicitly reported as an error. */
#define CONTROL_COMMAND_MAX 128
#define CONTROL_ID_MAX 32
static char control_last_id[CONTROL_ID_MAX + 1];
static char control_last_command[CONTROL_COMMAND_MAX + 1];
static char control_last_reply[256];

static int control_id_valid(const char *id)
{
    size_t i, n = strlen(id);
    if (n == 0 || n > CONTROL_ID_MAX)
        return 0;
    for (i = 0; i < n; ++i)
        if (!((id[i] >= 'A' && id[i] <= 'Z') ||
              (id[i] >= 'a' && id[i] <= 'z') ||
              (id[i] >= '0' && id[i] <= '9') || id[i] == '_' || id[i] == '-'))
            return 0;
    return 1;
}

static int control_path(char *out, size_t capacity, const char *name)
{
    const char *dir = getenv("ENG_DATA_SIM_CONTROL_DIR");
    int n;
    if (dir == NULL || *dir == '\0')
        dir = "/tmp";
    n = snprintf(out, capacity, "%s/%s", dir, name);
    return n > 0 && (size_t)n < capacity;
}

static void control_reply(const char *reply)
{
    char tmp[PATH_MAX], dest[PATH_MAX];
    int fd;
    size_t length = strlen(reply), written = 0;
    if (!control_path(tmp, sizeof tmp, "eng-data-sim-reply.tmp") ||
        !control_path(dest, sizeof dest, "eng-data-sim-reply"))
        return;
    fd = open(tmp, O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, 0600);
    if (fd < 0)
        return;
    while (written < length) {
        ssize_t n = write(fd, reply + written, length - written);
        if (n < 0 && errno == EINTR)
            continue;
        if (n <= 0)
            break;
        written += (size_t)n;
    }
    if (close(fd) == 0 && written == length) {
        if (rename(tmp, dest) == 0) {
            printf("ENG_DATA_SIM_CONTROL %s", reply);
            fflush(stdout);
            return;
        }
    }
    (void)unlink(tmp);
}

static void control_poll(DBusConnection *conn)
{
    char path[PATH_MAX], command[CONTROL_COMMAND_MAX + 2];
    char id[CONTROL_ID_MAX + 2], op[8], field[32], value[16], extra[2];
    char reply[256];
    struct stat st;
    ssize_t length;
    int fd, count, n = 0;
    unsigned long number = 0;
    char *end;

    if (!control_path(path, sizeof path, "eng-data-sim-command"))
        return;
    fd = open(path, O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
    if (fd < 0)
        return;
    if (fstat(fd, &st) != 0 || !S_ISREG(st.st_mode)) {
        close(fd);
        return;
    }
    length = read(fd, command, sizeof command - 1);
    close(fd);
    /* A single producer must wait for the receipt before replacing this file. */
    (void)unlink(path);
    if (length <= 0 || length > CONTROL_COMMAND_MAX) {
        control_reply("- ERR malformed\n");
        return;
    }
    command[length] = '\0';
    if (memchr(command, '\0', (size_t)length) != NULL ||
        command[length - 1] != '\n' || memchr(command, '\n', (size_t)length - 1) != NULL) {
        control_reply("- ERR malformed\n");
        return;
    }
    id[0] = op[0] = field[0] = value[0] = extra[0] = '\0';
    count = sscanf(command, "%33s %7s %31s %15s %1s %n", id, op, field, value, extra, &n);
    if (count < 1 || !control_id_valid(id)) {
        control_reply("- ERR malformed\n");
        return;
    }
    if (strcmp(id, control_last_id) == 0) {
        if (strcmp(command, control_last_command) == 0)
            control_reply(control_last_reply);
        else {
            snprintf(reply, sizeof reply, "%s ERR duplicate_id\n", id);
            control_reply(reply);
        }
        return;
    }
    if ((count != 3 && count != 4) ||
        (strcmp(field, "debug_count") != 0 && strcmp(field, "parking_status") != 0) ||
        !((count == 3 && strcmp(op, "GET") == 0) ||
          (count == 4 && strcmp(op, "SET") == 0))) {
        snprintf(reply, sizeof reply, "%s ERR unsupported\n", id);
    } else if (count == 4) {
        size_t i, len = strlen(value);
        int valid = len > 0 && (len == 1 || value[0] != '0');
        for (i = 0; i < len; ++i)
            if (value[i] < '0' || value[i] > '9')
                valid = 0;
        errno = 0;
        number = strtoul(value, &end, 10);
        if (!valid || errno != 0 || *end != '\0' ||
            number > (strcmp(field, "parking_status") == 0 ? 1UL : 255UL)) {
            snprintf(reply, sizeof reply, "%s ERR invalid_value\n", id);
        } else if (strcmp(field, "parking_status") == 0) {
            if (!sim_parking_notify(conn, (int)number)) {
                snprintf(reply, sizeof reply, "%s ERR signal_failed\n", id);
            } else {
                sim_parking_status = (int)number;
                snprintf(reply, sizeof reply, "%s OK parking_status %d evidence=recovered-ihu-parking-status\n", id, sim_parking_status);
            }
        } else {
            sim_debug_count = (unsigned char)number;
            snprintf(reply, sizeof reply,
                     "%s OK debug_count %u evidence=recovered-consumer-byte0\n",
                     id, (unsigned int)sim_debug_count);
        }
    } else if (strcmp(field, "parking_status") == 0) {
        if (sim_parking_status < 0)
            snprintf(reply, sizeof reply, "%s ERR unconfigured\n", id);
        else
            snprintf(reply, sizeof reply, "%s OK parking_status %d evidence=recovered-ihu-parking-status\n", id, sim_parking_status);
    } else {
        snprintf(reply, sizeof reply,
                 "%s OK debug_count %u evidence=recovered-consumer-byte0\n",
                 id, (unsigned int)sim_debug_count);
    }
    memcpy(control_last_id, id, strlen(id) + 1);
    memcpy(control_last_command, command, (size_t)length + 1);
    snprintf(control_last_reply, sizeof control_last_reply, "%s", reply);
    control_reply(reply);
}

static void stop_handler(int signo)
{
    (void)signo;
    keep_running = 0;
}

/* ---- invented, self-consistent replies (see file header) ---- */
static const char SYS_VERSION[]  = "NE_E.EUR.S5W_L.001.001.260128";
static const char WIPID[]        = "WIPID-5AE0001234";
static const char TRACE_DATE[]   = "2026.01.28";
static const char PART_NUMBER[]  = "96560-GI000";
static const char VR_VERSION[]   = "VR_SW_6.1.0.0";

/* Boot-info profile ported verbatim from tools/uk_fw/ias_backend_soft/micom_service.c:
 * 35 bytes, EV-family Europe, 12.3" LCD, nav+modem+RHD+amp, English US, last GUI
 * mode 1. Served verbatim rather than invented. */
static const unsigned char v2_bootinfo[BOOTINFO_LEN] = {
    0x00, 0x00, 0x08, 0x26, 0x05, 0x00, 0x00, 0x05, 0x13, 0x02,
    0x00, 0x00, 0x03, 0xc8, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00,
    0x01, 0x00, 0x00, 0x00, 0x00,
};

static void log_call(const char *bus, DBusMessage *msg)
{
    const char *path = dbus_message_get_path(msg);
    const char *iface = dbus_message_get_interface(msg);
    const char *member = dbus_message_get_member(msg);
    printf("ENG_DATA_SIM_CALL bus=%s sender=%s path=%s interface=%s member=%s signature=%s\n",
           bus,
           dbus_message_get_sender(msg) ? dbus_message_get_sender(msg) : "(null)",
           path ? path : "(null)", iface ? iface : "(null)",
           member ? member : "(null)", dbus_message_get_signature(msg));
    fflush(stdout);
}

/* PROJECTION-ONLY diagnostic: dump the first 'ay' argument as hex so the CAN
 * registration payloads (SetCANMicomRecv / SetCANTPMicomRecv /
 * SetCANFixedMicomRecv / AskCANMMCANMicomReq / AskCANICANMicomReq) can be read
 * out of /tmp/eng-data-sim.log.  Not part of the shipped system. */
static void log_ay_payload(DBusMessage *msg)
{
    DBusMessageIter iter, sub;
    char hex[2048];
    int n = 0;

    if (!dbus_message_iter_init(msg, &iter))
        return;
    if (dbus_message_iter_get_arg_type(&iter) != DBUS_TYPE_ARRAY)
        return;
    dbus_message_iter_recurse(&iter, &sub);
    while (dbus_message_iter_get_arg_type(&sub) == DBUS_TYPE_BYTE) {
        unsigned char b = 0;
        dbus_message_iter_get_basic(&sub, &b);
        n += snprintf(hex + n, sizeof(hex) - n, "%02x", b);
        if (n >= (int)sizeof(hex) - 4)
            break;
        if (!dbus_message_iter_next(&sub))
            break;
    }
    printf("ENG_DATA_SIM_PAYLOAD %s (%d bytes): %s\n",
           dbus_message_get_member(msg) ? dbus_message_get_member(msg) : "(null)",
           n / 2, hex);
    fflush(stdout);
}

static int send_message(DBusConnection *conn, DBusMessage *reply)
{
    if (reply == NULL)
        return 0;
    if (!dbus_connection_send(conn, reply, NULL)) {
        dbus_message_unref(reply);
        return 0;
    }
    dbus_connection_flush(conn);
    dbus_message_unref(reply);
    return 1;
}

static int reply_empty(DBusConnection *conn, DBusMessage *request)
{
    return send_message(conn, dbus_message_new_method_return(request));
}

static int reply_error(DBusConnection *conn, DBusMessage *request,
                       const char *name, const char *text)
{
    return send_message(conn, dbus_message_new_error(request, name, text));
}

static int reply_string(DBusConnection *conn, DBusMessage *request, const char *value)
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    if (reply == NULL)
        return 0;
    if (!dbus_message_append_args(reply, DBUS_TYPE_STRING, &value, DBUS_TYPE_INVALID)) {
        dbus_message_unref(reply);
        return 0;
    }
    return send_message(conn, reply);
}

static int reply_ay(DBusConnection *conn, DBusMessage *request,
                    const unsigned char *data, int len)
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    DBusMessageIter root, array;
    const unsigned char *p = data;
    if (reply == NULL)
        return 0;
    dbus_message_iter_init_append(reply, &root);
    if (!dbus_message_iter_open_container(&root, DBUS_TYPE_ARRAY,
                                           DBUS_TYPE_BYTE_AS_STRING, &array) ||
        !dbus_message_iter_append_fixed_array(&array, DBUS_TYPE_BYTE, &p, len) ||
        !dbus_message_iter_close_container(&root, &array)) {
        dbus_message_unref(reply);
        return 0;
    }
    return send_message(conn, reply);
}

/* Retain only the first matching native request/reply, never an observer query.
 * The 31-byte zero suffix is checked below so byte0 plus tail_zero binds the
 * complete synthetic payload without storing raw bus traffic. */
static int startup_car_seen;
static void reply_car_info(DBusConnection *conn, DBusMessage *request, const unsigned char *data)
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    DBusMessageIter root, array;
    const unsigned char *bytes = data;
    const char *sender = dbus_message_get_sender(request);
    const char *owner = dbus_bus_get_unique_name(conn);
    dbus_uint32_t req = dbus_message_get_serial(request), serial = 0, correlation;
    int first = !startup_car_seen, fd, n, i;
    char tmp[PATH_MAX], dest[PATH_MAX], record[512];
    startup_car_seen = 1;
    if (reply == NULL)
        return;
    dbus_message_iter_init_append(reply, &root);
    if (!dbus_message_iter_open_container(&root, DBUS_TYPE_ARRAY, DBUS_TYPE_BYTE_AS_STRING, &array) ||
        !dbus_message_iter_append_fixed_array(&array, DBUS_TYPE_BYTE, &bytes, 32) ||
        !dbus_message_iter_close_container(&root, &array)) {
        dbus_message_unref(reply);
        return;
    }
    correlation = dbus_message_get_reply_serial(reply);
    if (!dbus_connection_send(conn, reply, &serial)) {
        dbus_message_unref(reply);
        return;
    }
    dbus_connection_flush(conn);
    dbus_message_unref(reply);
    if (!first || !sender || !owner || sender[0] != ':' || owner[0] != ':' ||
        req == 0 || serial == 0 || correlation != req ||
        !control_path(tmp, sizeof tmp, "eng-data-sim-startup.tmp") ||
        !control_path(dest, sizeof dest, "eng-data-sim-startup"))
        return;
    for (i = 1; i < 32; ++i)
        if (data[i] != 0)
            return;
    n = snprintf(record, sizeof record,
        "WB_IHU_STARTUP 1 sender=%s owner=%s request=%u reply=%u reply_serial=%u len=32 byte0=%02x tail_zero=31\n",
        sender, owner, (unsigned)req, (unsigned)serial, (unsigned)correlation, (unsigned)data[0]);
    if (n <= 0 || (size_t)n >= sizeof record)
        return;
    fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (fd < 0)
        return;
    if (write(fd, record, (size_t)n) == n && close(fd) == 0) {
        (void)link(tmp, dest); /* create-only: never replace another receipt */
    } else {
        (void)close(fd);
    }
    (void)unlink(tmp);
}

static int reply_boolean(DBusConnection *conn, DBusMessage *request, int value)
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    dbus_bool_t b = value ? TRUE : FALSE;
    if (reply == NULL)
        return 0;
    if (!dbus_message_append_args(reply, DBUS_TYPE_BOOLEAN, &b, DBUS_TYPE_INVALID)) {
        dbus_message_unref(reply);
        return 0;
    }
    return send_message(conn, reply);
}

/* org.freedesktop.DBus.Properties.GetAll -> empty a{sv} dictionary.
 * The home screen introspects the stand-in; an empty property map is the
 * correct well-formed reply (an error here is a wrong reply that the app may
 * treat as a failure). */
static int reply_empty_asv(DBusConnection *conn, DBusMessage *request)
{
    DBusMessage *reply = dbus_message_new_method_return(request);
    DBusMessageIter root, arr;
    if (reply == NULL)
        return 0;
    dbus_message_iter_init_append(reply, &root);
    if (!dbus_message_iter_open_container(&root, DBUS_TYPE_ARRAY, "{sv}", &arr) ||
        !dbus_message_iter_close_container(&root, &arr)) {
        dbus_message_unref(reply);
        return 0;
    }
    return send_message(conn, reply);
}

/* Interface equality: a call that omits the interface field is accepted when
 * path + member + signature agree (Qt QDBusInterface sometimes omits it). */
static int iface_matches(const char *actual, const char *expected)
{
    return actual == NULL || strcmp(actual, expected) == 0;
}

static int exact_call(DBusMessage *msg, const char *path, const char *iface,
                      const char *member, const char *signature)
{
    const char *p = dbus_message_get_path(msg);
    return p != NULL && strcmp(p, path) == 0 &&
           iface_matches(dbus_message_get_interface(msg), iface) &&
           strcmp(dbus_message_get_member(msg), member) == 0 &&
           strcmp(dbus_message_get_signature(msg), signature) == 0;
}

/* ---- fixed-shape 'ay' asks, ported from micom_dbus_sim.c ---- */
struct ay_reply {
    const char *path;
    const char *iface;
    const char *member;
    int len;
    const unsigned char *data;      /* NULL -> zeroes */
    const char *label;
};

static const unsigned char factory_mode_customer[8] = { 1, 0, 0, 0, 0, 0, 0, 0 };
static const unsigned char zeroes32[32];

static const struct ay_reply ay_replies[] = {
    { IHU_PATH, IHU_INTERFACE, "AskFactoryModeInfo", 8, factory_mode_customer, "factory-mode/user-mode" },
    { AUDIO_PATH, AUDIO_INTERFACE, "AskVolumeInfo", 8, NULL, "volume" },
    { AUDIO_PATH, AUDIO_INTERFACE, "AskSoundSetupInfo", 8, NULL, "sound-setup" },
    { AUDIO_PATH, AUDIO_INTERFACE, "AskAMPSupportInfo", 4, NULL, "amp-support" },
    { AUDIO_PATH, AUDIO_INTERFACE, "AskAudioMuteInfo", 8, NULL, "audio-mute-info" },
    { AUDIO_PATH, AUDIO_INTERFACE, "AskAudioLastMemory", 8, NULL, "audio-last-memory" },
    { CAN_PATH, CAN_INTERFACE, "AskNaviAppData", 32, NULL, "navi-app-data" },
};

/* ---- transport acks the launcher/home-screen wait on ---- */
struct ack_call {
    const char *path;
    const char *iface;
    const char *member;
    const char *signature;
};

static const struct ack_call ack_calls[] = {
    { IHU_PATH, IHU_INTERFACE, "SetControlKeyLock",     "ay" },
    { IHU_PATH, IHU_INTERFACE, "SetETCCPUAliveMsg",     "ay" },
    { IHU_PATH, IHU_INTERFACE, "SetETCAppBootComplete", "ay" },
    { IHU_PATH, IHU_INTERFACE, "SetDIDInfo",            "ay" },
    { CAN_PATH, CAN_INTERFACE, "AskCANMMCANMicomReq",   "ay" },
    { CAN_PATH, CAN_INTERFACE, "AskCANICANMicomReq",    "ay" },
    { CAN_PATH, CAN_INTERFACE, "SetCANMicomRecv",       "ay" },
    { CAN_PATH, CAN_INTERFACE, "SetCANTPMicomRecv",     "ay" },
    { CAN_PATH, CAN_INTERFACE, "SetCANFixedMicomRecv",  "ayiii" },
    { CAN_PATH, CAN_INTERFACE, "SetDATCInitialRequest", "" },
    { CAN_PATH, CAN_INTERFACE, "SetCARSETInitialRequest", "" },
    { CAN_PATH, CAN_INTERFACE, "SetLowFuelWarnningRequest", "" },
    { AUDIO_PATH, AUDIO_INTERFACE, "SetAudioMainCHChange", "ay" },
    { AUDIO_PATH, AUDIO_INTERFACE, "SetAudioMixingCHChange", "ay" },
    { AUDIO_PATH, AUDIO_INTERFACE, "SetAudioVolume", "ay" },
    { AUDIO_PATH, AUDIO_INTERFACE, "SetAudioSetup", "ay" },
    { AUDIO_PATH, AUDIO_INTERFACE, "SetBeepPlay", "ay" },
    { AUDIO_PATH, AUDIO_INTERFACE, "SetCurrentModeVolume", "ay" },
    { AUDIO_PATH, AUDIO_INTERFACE, "SetAudioSpeakerCtrl", "ay" },
    /* V-0xx: the settings application asks MICOM whether engineering mode may be entered. */
    { ENG_PATH, ENG_INTERFACE, "SetEnginnerModeEntryCheck", "" },
    /* Backlog methods whose argument lists were recovered from the calling binaries' own
     * introspection XML: all three take no arguments (the simulator logged signature= empty). */
    { CAN_PATH, CAN_INTERFACE, "SetCANAMP_HU_P_01Request",   "" },
    { CAN_PATH, CAN_INTERFACE, "SetLevelGearInitialRequest", "" },
    { CAN_PATH, CAN_INTERFACE, "SetUSMInitialRequest",       "" },
    { IHU_PATH, IHU_INTERFACE, "SetETCLanguageInfoSet",      "ay" },
    { IHU_PATH, IHU_INTERFACE, "SetSettingValueStatusMsg",   "ay" },
};

static const unsigned char region_reply[8] = { 1, 0, 0, 0, 0, 0, 0, 0 };
static const unsigned char setting_reply[8] = { 0, 0, 0, 0, 0, 0, 0, 1 };

static DBusHandlerResult on_system_message(DBusConnection *conn, DBusMessage *msg, void *user)
{
    const char *path = dbus_message_get_path(msg);
    const char *iface = dbus_message_get_interface(msg);
    const char *member = dbus_message_get_member(msg);
    const char *sig = dbus_message_get_signature(msg);
    unsigned int i;

    (void)user;

    if (dbus_message_get_type(msg) != DBUS_MESSAGE_TYPE_METHOD_CALL)
        return DBUS_HANDLER_RESULT_NOT_YET_HANDLED;

    log_call("system", msg);

    /* Introspect per path */
    if (iface != NULL && strcmp(iface, INTROSPECTABLE) == 0 &&
        strcmp(member, "Introspect") == 0) {
        reply_string(conn, msg, "<node></node>");
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (iface != NULL && strcmp(iface, PEER_INTERFACE) == 0 &&
        strcmp(member, "Ping") == 0) {
        reply_empty(conn, msg);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (iface != NULL && strcmp(iface, "org.freedesktop.DBus.Properties") == 0 &&
        strcmp(member, "GetAll") == 0) {
        reply_empty_asv(conn, msg);
        printf("ENG_DATA_SIM_ANSWER Properties.GetAll -> {} (empty a{sv})\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (iface != NULL && strcmp(iface, "org.freedesktop.DBus.Properties") == 0 &&
        strcmp(member, "Get") == 0) {
        reply_error(conn, msg, "org.freedesktop.DBus.Error.UnknownProperty",
                    "property not provided by eng data research simulator");
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    /* AskSysBootinfo — the launcher blocks on this. */
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskSysBootinfo", "")) {
        reply_ay(conn, msg, v2_bootinfo, BOOTINFO_LEN);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskEtcCarInformationRead", "")) {
        unsigned char car_info[32];
        memcpy(car_info, zeroes32, sizeof car_info);
        if (sim_parking_status == 1)
            car_info[0] |= 0x08;
        else
            car_info[0] &= (unsigned char)~0x08;
        printf("ENG_DATA_SIM_ANSWER AskEtcCarInformationRead parking_status=%s\n",
               sim_parking_status < 0 ? "unconfigured" : sim_parking_status ? "1" : "0");
        fflush(stdout);
        reply_car_info(conn, msg, car_info);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    /* The six engineering-mode asks on the micom name. */
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskSysVersion", "")) {
        printf("ENG_DATA_SIM_ANSWER AskSysVersion -> '%s'\n", SYS_VERSION);
        fflush(stdout);
        reply_ay(conn, msg, (const unsigned char *)SYS_VERSION, strlen(SYS_VERSION));
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, CAN_PATH, CAN_INTERFACE, "AskAutotestWIPID", "")) {
        printf("ENG_DATA_SIM_ANSWER AskAutotestWIPID -> '%s'\n", WIPID);
        fflush(stdout);
        reply_ay(conn, msg, (const unsigned char *)WIPID, strlen(WIPID));
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskTraceDate", "")) {
        printf("ENG_DATA_SIM_ANSWER AskTraceDate -> '%s'\n", TRACE_DATE);
        fflush(stdout);
        reply_ay(conn, msg, (const unsigned char *)TRACE_DATE, strlen(TRACE_DATE));
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskPartNumberInfo", "")) {
        printf("ENG_DATA_SIM_ANSWER AskPartNumberInfo -> '%s'\n", PART_NUMBER);
        fflush(stdout);
        reply_ay(conn, msg, (const unsigned char *)PART_NUMBER, strlen(PART_NUMBER));
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    /* ------------------------------------------------------------------ */
    /* ApplicationManager state-machine asks (the two that logged
     * "reply is not VALID") plus the other unanswered methods the manager
     * and its sibling apps issue. Reply types are recovered verbatim from
     * micommanager_userspace's D-Bus introspection XML (all `ay`), and from
     * AppVH's com.lge.avn.appvh.AmebaEnable introspection (`b`).
     *
     * AskDebuggingMode:  out ay, byte[0] = debug count. 0 = off. The
     *   manager's AskDebugCntSlot parses byte[0]; <=0 skips the follow-up
     *   SetSysDebuggingMode call.
     * AskEtcAdmSettingValue: out ay, byte[0] = ADM-off value. 0 = normal;
     *   non-zero would drive the manager's ADMOffSettingSlot toward a
     *   "change power to Logic OFF".
     * ------------------------------------------------------------------ */
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskDebuggingMode", "")) {
        reply_ay(conn, msg, &sim_debug_count, 1);
        printf("ENG_DATA_SIM_ANSWER AskDebuggingMode -> cnt=%u (simulator)\n",
               (unsigned int)sim_debug_count);
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskEtcAdmSettingValue", "")) {
        static const unsigned char adm_off[1] = { 0x00 };
        reply_ay(conn, msg, adm_off, sizeof adm_off);
        printf("ENG_DATA_SIM_ANSWER AskEtcAdmSettingValue -> value=0\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskSysUpmID", "")) {
        static const unsigned char upm[1] = { 0x00 };
        reply_ay(conn, msg, upm, sizeof upm);
        printf("ENG_DATA_SIM_ANSWER AskSysUpmID -> 0\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    /* ------------------------------------------------------------------ */
    /* Backlog Ask* methods. Signatures are RECOVERED from the calling binaries' introspection
     * XML (com.lge.car.micom.ihu, out ay). The REPLY VALUES are ASSUMED to be zero/"absent",
     * because the encoding is not recovered - recorded in docs/vm/46-sim-unimplemented-backlog.md.
     * Every one of them is answered rather than rejected, so the caller stops being told the
     * method does not exist; whether the value is meaningful is a separate, unmeasured question.
     * ------------------------------------------------------------------ */
    /* ------------------------------------------------------------------ */
    /* Backlog Ask* methods, with the reply SHAPES and VALUES now taken from the vehicle's own
     * DLT logs (evidence/upstream/Ioniq5_Gen5W_Log_Dump) rather than assumed:
     *
     *   AskExternalSPDIFAMPVersion   "Response LgeDBus_AskAMPVersion() Data Count :: 8"  -> 8 bytes
     *   AskEtcLcd2SensorNotSupportPwmControl
     *                                the consumer logs three fields from the reply
     *                                (isAutoBrightnessSensorMode, ...Value-Auto, ...Value-Manual)
     *                                and "Value-Manual: 2" -> 3 bytes, manual mode = 2
     *   AskUSMSetting                "slotUSMSetting ... ] 2"                            -> 1 byte, value 2
     *   AskVolumeTuneKeySwap         no occurrence in the logs                            -> 1 byte, 0 (ASSUMED)
     * ------------------------------------------------------------------ */
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskExternalSPDIFAMPVersion", "")) {
        static const unsigned char spdif[8] = { 0 };
        reply_ay(conn, msg, spdif, sizeof spdif);
        printf("ENG_DATA_SIM_ANSWER AskExternalSPDIFAMPVersion -> 8 bytes (count from vehicle log)\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskEtcLcd2SensorNotSupportPwmControl", "ay")) {
        static const unsigned char lcd2[3] = { 0x00, 0x00, 0x02 };
        reply_ay(conn, msg, lcd2, sizeof lcd2);
        printf("ENG_DATA_SIM_ANSWER AskEtcLcd2SensorNotSupportPwmControl -> 3 bytes, manual=2 (vehicle log)\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskUSMSetting", "ay")) {
        static const unsigned char usm[1] = { 0x02 };
        reply_ay(conn, msg, usm, sizeof usm);
        printf("ENG_DATA_SIM_ANSWER AskUSMSetting -> 2 (vehicle log)\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskVolumeTuneKeySwap", "")) {
        static const unsigned char swap[1] = { 0x00 };
        reply_ay(conn, msg, swap, sizeof swap);
        printf("ENG_DATA_SIM_ANSWER AskVolumeTuneKeySwap -> 0 (ASSUMED, absent from logs)\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskInfoFaultCodeStatus", "ay")) {
        static const unsigned char no_fault[1] = { 0x00 };
        reply_ay(conn, msg, no_fault, sizeof no_fault);
        printf("ENG_DATA_SIM_ANSWER AskInfoFaultCodeStatus -> 0 (no fault reported)\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskCameraSetting", "ay")) {
        static const unsigned char cam[4] = { 0x00, 0x00, 0x00, 0x00 };
        reply_ay(conn, msg, cam, sizeof cam);
        printf("ENG_DATA_SIM_ANSWER AskCameraSetting -> 4 bytes\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskCameraBrightness", "")) {
        static const unsigned char br[2] = { 0x50, 0x00 };
        reply_ay(conn, msg, br, sizeof br);
        printf("ENG_DATA_SIM_ANSWER AskCameraBrightness -> 2 bytes\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskEtcLcdThemaInfo", "ay")) {
        static const unsigned char thema[4] = { 0x00, 0x00, 0x00, 0x00 };
        reply_ay(conn, msg, thema, sizeof thema);
        printf("ENG_DATA_SIM_ANSWER AskEtcLcdThemaInfo -> 4 bytes\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    /* askLcdInfo(): a manager ask the stand-in did not previously answer. */
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskLCDSetInfoValue", "")) {
        reply_ay(conn, msg, zeroes32, 8);
        printf("ENG_DATA_SIM_ANSWER AskLCDSetInfoValue -> 8 bytes\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    /* The eng app's eCall-status ask (out ay). 0 = eCall inactive. */
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskETCEcallStatus", "")) {
        static const unsigned char ecall[1] = { 0x00 };
        reply_ay(conn, msg, ecall, sizeof ecall);
        printf("ENG_DATA_SIM_ANSWER AskETCEcallStatus -> 0\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    /* /Can SetFCEVInitialRequest: void, like its DATC/CARSET siblings. */
    if (exact_call(msg, CAN_PATH, CAN_INTERFACE, "SetFCEVInitialRequest", "")) {
        reply_empty(conn, msg);
        printf("ENG_DATA_SIM_ANSWER SetFCEVInitialRequest -> (void)\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    /* Fixed-shape 'ay' table (includes AskFactoryModeInfo -> user mode). */
    for (i = 0; i < sizeof ay_replies / sizeof ay_replies[0]; i++) {
        const struct ay_reply *r = &ay_replies[i];
        if (exact_call(msg, r->path, r->iface, r->member, "")) {
            reply_ay(conn, msg, r->data ? r->data : zeroes32, r->len);
            printf("ENG_DATA_SIM_ANSWER %s %s.%s -> %d bytes\n", r->label,
                   r->path, r->member, r->len);
            fflush(stdout);
            return DBUS_HANDLER_RESULT_HANDLED;
        }
    }

    /* Documented launcher asks kept from the proven simulator. */
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskNaviOutermostRegion", "")) {
        reply_ay(conn, msg, region_reply, sizeof region_reply);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskSettingInfoValue", "")) {
        reply_ay(conn, msg, setting_reply, sizeof setting_reply);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskCustomSetting", "ay")) {
        reply_ay(conn, msg, zeroes32, 16);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (exact_call(msg, IHU_PATH, IHU_INTERFACE, "AskSysAutomaticBrightness", "ay")) {
        reply_ay(conn, msg, zeroes32, 8);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    /* /Eng AskMPModeInfo: no output arguments. */
    if (exact_call(msg, ENG_PATH, ENG_INTERFACE, "AskMPModeInfo", "")) {
        reply_empty(conn, msg);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    /* Audio methods with an 'ay' input that answer with an 'ay' payload.
     * Recovered from micommanager_userspace's com.lge.car.micom.audio XML:
     * SetAudioMute/SetAudioLastMemory/SetAudioClusterAnimationCtrl/AskAudioSRCScaleInfo
     * all declare (in ay, out ay).  A few zero bytes read as "nothing to report". */
    if (exact_call(msg, AUDIO_PATH, AUDIO_INTERFACE, "SetAudioMute", "ay") ||
        exact_call(msg, AUDIO_PATH, AUDIO_INTERFACE, "SetAudioLastMemory", "ay") ||
        exact_call(msg, AUDIO_PATH, AUDIO_INTERFACE, "SetAudioClusterAnimationCtrl", "ay") ||
        exact_call(msg, AUDIO_PATH, AUDIO_INTERFACE, "AskAudioSRCScaleInfo", "ay")) {
        reply_ay(conn, msg, zeroes32, 8);
        printf("ENG_DATA_SIM_ANSWER %s %s.%s -> 8 bytes\n", AUDIO_PATH,
               AUDIO_INTERFACE, member);
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    /* Transport acks. */
    for (i = 0; i < sizeof ack_calls / sizeof ack_calls[0]; i++) {
        const struct ack_call *a = &ack_calls[i];
        if (exact_call(msg, a->path, a->iface, a->member, a->signature)) {
            /* PROJECTION-ONLY: dump CAN registration payloads before ACKing. */
            if (a->member && (strcmp(a->member, "SetCANMicomRecv") == 0 ||
                              strcmp(a->member, "SetCANTPMicomRecv") == 0 ||
                              strcmp(a->member, "SetCANFixedMicomRecv") == 0 ||
                              strcmp(a->member, "AskCANMMCANMicomReq") == 0 ||
                              strcmp(a->member, "AskCANICANMicomReq") == 0))
                log_ay_payload(msg);
            /* PROJECTION-ONLY: log accepted calls too. Rejections were logged from the start, so an
             * accepted method was silent - which made "no rejection" indistinguishable from
             * "never called". This makes a fix positively verifiable instead of inferred. */
            printf("ENG_DATA_SIM_ACK path=%s interface=%s member=%s\n",
                   a->path, a->iface, a->member ? a->member : "(null)");
            reply_empty(conn, msg);
            return DBUS_HANDLER_RESULT_HANDLED;
        }
    }

    /* Fail closed, exactly like the proven simulator. */
    printf("ENG_DATA_SIM_UNKNOWN path=%s interface=%s member=%s signature=%s\n",
           path ? path : "(null)", iface ? iface : "(null)",
           member ? member : "(null)", sig ? sig : "(null)");
    fflush(stdout);
    if (path == NULL ||
        (strcmp(path, IHU_PATH) && strcmp(path, CAN_PATH) &&
         strcmp(path, ENG_PATH) && strcmp(path, AUDIO_PATH))) {
        reply_error(conn, msg, DBUS_ERROR_UNKNOWN_OBJECT,
                    "object path not provided by eng data research simulator");
    } else {
        reply_error(conn, msg, DBUS_ERROR_UNKNOWN_METHOD,
                    "method not implemented by eng data research simulator");
    }
    return DBUS_HANDLER_RESULT_HANDLED;
}

static DBusHandlerResult on_session_message(DBusConnection *conn, DBusMessage *msg, void *user)
{
    const char *iface = dbus_message_get_interface(msg);
    const char *member = dbus_message_get_member(msg);

    (void)user;

    if (dbus_message_get_type(msg) != DBUS_MESSAGE_TYPE_METHOD_CALL)
        return DBUS_HANDLER_RESULT_NOT_YET_HANDLED;

    log_call("session", msg);

    if (iface != NULL && strcmp(iface, INTROSPECTABLE) == 0 &&
        strcmp(member, "Introspect") == 0) {
        reply_string(conn, msg, "<node></node>");
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (iface != NULL && strcmp(iface, PEER_INTERFACE) == 0 &&
        strcmp(member, "Ping") == 0) {
        reply_empty(conn, msg);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (iface != NULL && strcmp(iface, "org.freedesktop.DBus.Properties") == 0 &&
        strcmp(member, "GetAll") == 0) {
        reply_empty_asv(conn, msg);
        printf("ENG_DATA_SIM_ANSWER Properties.GetAll -> {} (empty a{sv})\n");
        fflush(stdout);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (iface != NULL && strcmp(iface, "org.freedesktop.DBus.Properties") == 0 &&
        strcmp(member, "Get") == 0) {
        reply_error(conn, msg, "org.freedesktop.DBus.Error.UnknownProperty",
                    "property not provided by eng data research simulator");
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    /* com.lge.avn.appvh.AmebaEnable.AmebaEnable -> out b (AppVH asks whether
     * Ameba VR is enabled). Answer false: Ameba VR is not running here. */
    if (strcmp(member, "AmebaEnable") == 0) {
        printf("ENG_DATA_SIM_ANSWER AmebaEnable -> false\n");
        fflush(stdout);
        reply_boolean(conn, msg, 0);
        return DBUS_HANDLER_RESULT_HANDLED;
    }
    if (strcmp(member, "AtVersionVrReq") == 0 ||
        strcmp(member, "AtVersionVrReqAll") == 0) {
        printf("ENG_DATA_SIM_ANSWER %s -> '%s'\n", member, VR_VERSION);
        fflush(stdout);
        reply_string(conn, msg, VR_VERSION);
        return DBUS_HANDLER_RESULT_HANDLED;
    }

    printf("ENG_DATA_SIM_UNKNOWN bus=session path=%s interface=%s member=%s\n",
           dbus_message_get_path(msg) ? dbus_message_get_path(msg) : "(null)",
           iface ? iface : "(null)", member ? member : "(null)");
    fflush(stdout);
    reply_error(conn, msg, DBUS_ERROR_UNKNOWN_METHOD,
                "method not implemented by eng data research simulator");
    return DBUS_HANDLER_RESULT_HANDLED;
}

static const DBusObjectPathVTable system_vtable = {
    NULL, on_system_message, NULL, NULL, NULL, NULL,
};

static const DBusObjectPathVTable session_vtable = {
    NULL, on_session_message, NULL, NULL, NULL, NULL,
};

static DBusConnection *connect_bus(int type, const char *label)
{
    DBusError error;
    DBusConnection *conn;

    dbus_error_init(&error);
    conn = dbus_bus_get(type, &error);
    if (conn == NULL) {
        fprintf(stderr, "eng-data-sim: %s bus: %s: %s\n", label,
                error.name ? error.name : "unknown",
                error.message ? error.message : "unknown");
        dbus_error_free(&error);
        return NULL;
    }
    dbus_connection_set_exit_on_disconnect(conn, FALSE);
    return conn;
}

static int own_name(DBusConnection *conn, const char *name, const char *label)
{
    DBusError error;
    int rc = -1;
    int attempt;

    dbus_error_init(&error);
    /* Wait for any vendor daemon to release the name, then take it (1 = primary). */
    for (attempt = 0; attempt < 40; attempt++) {
        rc = dbus_bus_request_name(conn, name,
                                   DBUS_NAME_FLAG_REPLACE_EXISTING |
                                   DBUS_NAME_FLAG_DO_NOT_QUEUE, &error);
        if (dbus_error_is_set(&error)) {
            fprintf(stderr, "eng-data-sim: request_name %s (%s): %s: %s\n", name,
                    label, error.name, error.message);
            dbus_error_free(&error);
            dbus_error_init(&error);
        }
        if (rc == DBUS_REQUEST_NAME_REPLY_PRIMARY_OWNER ||
            rc == DBUS_REQUEST_NAME_REPLY_ALREADY_OWNER)
            break;
        usleep(500000);
    }
    return rc;
}

static int register_path(DBusConnection *conn, const char *path,
                         const DBusObjectPathVTable *vt, const char *label)
{
    if (!dbus_connection_register_object_path(conn, path, vt, NULL)) {
        fprintf(stderr, "eng-data-sim: register_object_path %s (%s) failed\n",
                path, label);
        return -1;
    }
    return 0;
}

int main(void)
{
    static const char *sys_paths[] = { IHU_PATH, CAN_PATH, ENG_PATH, AUDIO_PATH };
    DBusConnection *sys_conn, *ses_conn;
    unsigned int i;
    const char *initial_parking = getenv("ENG_DATA_SIM_PARKING_STATUS");

    if (initial_parking != NULL) {
        if (strcmp(initial_parking, "0") != 0 && strcmp(initial_parking, "1") != 0) {
            fprintf(stderr, "eng-data-sim: invalid initial parking status\n");
            return 2;
        }
        sim_parking_status = initial_parking[0] - '0';
    }

    signal(SIGINT, stop_handler);
    signal(SIGTERM, stop_handler);

    /* System bus: own the micom name and serve /Ihu /Can /Eng + audio. */
    sys_conn = connect_bus(DBUS_BUS_SYSTEM, "system");
    if (sys_conn == NULL)
        return 2;
    i = (unsigned int)own_name(sys_conn, MICOM_BUS_NAME, "system");
    if (i != DBUS_REQUEST_NAME_REPLY_PRIMARY_OWNER && i != DBUS_REQUEST_NAME_REPLY_ALREADY_OWNER) {
        fprintf(stderr, "eng-data-sim: failed to own system name\n");
        return 3;
    }
    for (i = 0; i < sizeof sys_paths / sizeof sys_paths[0]; i++) {
        if (register_path(sys_conn, sys_paths[i], &system_vtable, "system") < 0)
            return 3;
    }

    /* Session bus: own AppVH's VR-version name and serve the atversionvrreq
     * interface AppEngineerMode calls for "VR SW Version". */
    ses_conn = connect_bus(DBUS_BUS_SESSION, "session");
    if (ses_conn == NULL)
        ses_conn = sys_conn;    /* tolerate a missing session bus; system still works */
    else {
        own_name(ses_conn, VR_BUS_NAME, "session");
        if (register_path(ses_conn, VR_PATH, &session_vtable, "session") < 0)
            return 4;
    }

    printf("ENG_DATA_SIM_READY pid=%ld owner=%s system=%s session=%s\n", (long)getpid(),
           dbus_bus_get_unique_name(sys_conn), MICOM_BUS_NAME,
           ses_conn == sys_conn ? "(none)" : VR_BUS_NAME);
    fflush(stdout);

    while (keep_running) {
        control_poll(sys_conn);
        if (dbus_connection_get_is_connected(sys_conn))
            dbus_connection_read_write_dispatch(sys_conn, 100);
        if (ses_conn != sys_conn && dbus_connection_get_is_connected(ses_conn))
            dbus_connection_read_write_dispatch(ses_conn, 100);
        if (!dbus_connection_get_is_connected(sys_conn) &&
            (ses_conn == sys_conn || !dbus_connection_get_is_connected(ses_conn)))
            break;
    }

    dbus_connection_unref(sys_conn);
    if (ses_conn != sys_conn)
        dbus_connection_unref(ses_conn);
    return 0;
}
