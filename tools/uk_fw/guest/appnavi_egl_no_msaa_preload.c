/*
 * VM-only AppNavi EGL compatibility shim.
 *
 * The recovered AppNavi requires a 2x-MSAA EGL config, while the project-local
 * Mesa 18 llvmpipe stack exposes only zero-sample configs.  Keep AppNavi's
 * signed executable unchanged: for that executable only, translate its
 * eglChooseConfig request from two samples to zero and report the selected
 * zero-sample config as the two-sample value expected by its exact-build
 * selection loop.  All other callers and EGL attributes pass through.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <link.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

typedef void *EGLDisplay;
typedef void *EGLConfig;
typedef int EGLint;
typedef unsigned int EGLBoolean;

#define EGL_FALSE 0U
#define EGL_NONE 0x3038
#define EGL_SAMPLES 0x3031

static int is_appnavi(void)
{
    static int cached = -1;
    char path[256];
    ssize_t n;

    if (cached >= 0)
        return cached;
    n = readlink("/proc/self/exe", path, sizeof(path) - 1);
    if (n < 0) {
        cached = 0;
        return cached;
    }
    path[n] = '\0';
    cached = strcmp(path, "/navi/Bin/AppNavi") == 0;
    return cached;
}

static int compatibility_enabled(void)
{
    return access("/tmp/launcher-chain/enable-appnavi-egl-compat", F_OK) == 0;
}

static void log_event(const char *message)
{
    int fd;
    if (!is_appnavi())
        return;
    fd = open("/tmp/launcher-chain/appnavi-egl-compat.log",
              O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0)
        return;
    (void)write(fd, message, strlen(message));
    (void)write(fd, "\n", 1);
    (void)close(fd);
}

static int find_main_executable_base(struct dl_phdr_info *info, size_t size,
                                     void *data)
{
    (void)size;
    if (!info->dlpi_name || info->dlpi_name[0] == '\0') {
        *(uintptr_t *)data = (uintptr_t)info->dlpi_addr;
        return 1;
    }
    return 0;
}

__attribute__((constructor))
static void extend_exact_build_startup_deadline(void)
{
    /* The production onInitializeDone path declares boot failure when TCG
     * startup exceeds 22,999 ms, about six times shorter than this VM needs.
     * Preserve the signed file and alter only that guarded immediate in memory.
     * The expected-byte check makes this fail closed on every other build. */
    static const unsigned char expected[4] = {0xd7, 0x59, 0x00, 0x00};
    static const unsigned char deadline_180s[4] = {0x20, 0xbf, 0x02, 0x00};
    unsigned char *immediate;
    uintptr_t executable_base = 0;
    long page_size;
    uintptr_t page;

    if (!is_appnavi() ||
        access("/tmp/launcher-chain/enable-appnavi-startup-deadline-compat",
               F_OK) != 0)
        return;
    (void)dl_iterate_phdr(find_main_executable_base, &executable_base);
    immediate = (unsigned char *)(executable_base + (uintptr_t)0x33b48c0);
    if (memcmp(immediate, expected, sizeof(expected)) != 0) {
        log_event("STARTUP_DEADLINE_EXPECTED_BYTES_MISMATCH");
        return;
    }
    page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0)
        return;
    page = (uintptr_t)immediate & ~((uintptr_t)page_size - 1U);
    if (mprotect((void *)page, (size_t)page_size,
                 PROT_READ | PROT_WRITE | PROT_EXEC) != 0) {
        log_event("STARTUP_DEADLINE_MPROTECT_RW_FAILED");
        return;
    }
    memcpy(immediate, deadline_180s, sizeof(deadline_180s));
    __builtin___clear_cache((char *)immediate,
                            (char *)immediate + sizeof(deadline_180s));
    (void)mprotect((void *)page, (size_t)page_size, PROT_READ | PROT_EXEC);
    log_event("STARTUP_DEADLINE_22999_TO_180000_MS");
}

EGLBoolean eglChooseConfig(EGLDisplay display, const EGLint *attributes,
                           EGLConfig *configs, EGLint config_size,
                           EGLint *config_count)
{
    typedef EGLBoolean (*next_fn)(EGLDisplay, const EGLint *, EGLConfig *,
                                  EGLint, EGLint *);
    static next_fn next;
    EGLint translated[128];
    size_t i;

    if (!next)
        next = (next_fn)dlsym(RTLD_NEXT, "eglChooseConfig");
    if (!next)
        return EGL_FALSE;
    if (!is_appnavi() || !compatibility_enabled() || !attributes)
        return next(display, attributes, configs, config_size, config_count);

    for (i = 0; i + 1 < sizeof(translated) / sizeof(translated[0]); i += 2) {
        translated[i] = attributes[i];
        if (attributes[i] == EGL_NONE) {
            log_event("EGL_CHOOSE_CONFIG_PASSTHROUGH");
            return next(display, translated, configs, config_size,
                        config_count);
        }
        translated[i + 1] = attributes[i + 1];
        if (attributes[i] == EGL_SAMPLES && attributes[i + 1] == 2) {
            translated[i + 1] = 0;
            log_event("EGL_CHOOSE_CONFIG_SAMPLES_2_TO_0");
        }
    }

    /* Fail closed on a malformed or unexpectedly long attribute list. */
    log_event("EGL_CHOOSE_CONFIG_REJECTED_UNTERMINATED_ATTRIBUTES");
    return EGL_FALSE;
}

EGLBoolean eglGetConfigAttrib(EGLDisplay display, EGLConfig config,
                              EGLint attribute, EGLint *value)
{
    typedef EGLBoolean (*next_fn)(EGLDisplay, EGLConfig, EGLint, EGLint *);
    static next_fn next;
    EGLBoolean result;

    if (!next)
        next = (next_fn)dlsym(RTLD_NEXT, "eglGetConfigAttrib");
    if (!next)
        return EGL_FALSE;
    result = next(display, config, attribute, value);
    if (result && value && is_appnavi() && compatibility_enabled() &&
        attribute == EGL_SAMPLES && *value == 0) {
        *value = 2;
        log_event("EGL_GET_CONFIG_ATTRIB_SAMPLES_0_AS_2");
    }
    return result;
}
