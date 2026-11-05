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
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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
    { IHU_PATH, IHU_INTERFACE, "AskEtcCarInformationRead", 32, NULL, "etc-car-info" },
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
        static const unsigned char dbg_off[1] = { 0x00 };
        reply_ay(conn, msg, dbg_off, sizeof dbg_off);
        printf("ENG_DATA_SIM_ANSWER AskDebuggingMode -> cnt=0\n");
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

    signal(SIGINT, stop_handler);
    signal(SIGTERM, stop_handler);

    /* System bus: own the micom name and serve /Ihu /Can /Eng + audio. */
    sys_conn = connect_bus(DBUS_BUS_SYSTEM, "system");
    if (sys_conn == NULL)
        return 2;
    own_name(sys_conn, MICOM_BUS_NAME, "system");
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

    printf("ENG_DATA_SIM_READY system=%s session=%s\n", MICOM_BUS_NAME,
           ses_conn == sys_conn ? "(none)" : VR_BUS_NAME);
    fflush(stdout);

    while (keep_running) {
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
