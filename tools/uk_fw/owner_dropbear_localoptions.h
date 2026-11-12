/* Owner maintenance access: key OR nonempty password, interactive PTY and SCP.
 * Forwarding is absent at compile time, independent of runtime arguments.
 * Configure with --disable-shadow: the service supplies a private passwd file.
 */
#define DROPBEAR_SVR_PASSWORD_AUTH 1
#define DROPBEAR_SVR_PAM_AUTH 0
#define DROPBEAR_SVR_PUBKEY_AUTH 1
#define DROPBEAR_SVR_LOCALTCPFWD 0
#define DROPBEAR_SVR_REMOTETCPFWD 0
#define DROPBEAR_SVR_LOCALSTREAMFWD 0
#define DROPBEAR_SVR_REMOTESTREAMFWD 0
#define DROPBEAR_SVR_AGENTFWD 0
#define DROPBEAR_X11FWD 0
#define DROPBEAR_CLI_LOCALTCPFWD 0
#define DROPBEAR_CLI_REMOTETCPFWD 0
#define DROPBEAR_CLI_AGENTFWD 0
#define DROPBEAR_CLI_PROXYCMD 0
#define DROPBEAR_CLI_NETCAT 0
#define DROPBEAR_CLI_PASSWORD_AUTH 0
#define DROPBEAR_USE_PASSWORD_ENV 0
#define DROPBEAR_SFTPSERVER 0
#define DROPBEAR_CLI_COMPRESSION 0
#define DROPBEAR_SVR_DROP_PRIVS 1
