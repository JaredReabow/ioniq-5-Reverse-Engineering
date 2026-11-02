/*
 * guest_client_probe.c — drive the observer's attach/commit path from a real
 * Wayland client inside the recovered guest.
 *
 * The vendor root has no EGL stack for its own GUI applications and its bundled
 * simple clients need either libwebp.so.5 or the ivi client API, so none of them
 * can be pointed at the observation path. This probe speaks the protocol through
 * the vendor libwayland-client using only what that library really exports:
 * wl_display_connect, wl_proxy_marshal_constructor(_versioned), wl_proxy_marshal.
 * wl_surface_attach/wl_surface_commit are header inlines in this version and are
 * not symbols at all, so the attach and the commit are issued through
 * wl_proxy_marshal — the same ABI the interposer observes.
 *
 * Build (vendor glibc floor):
 *   zig cc -target x86_64-linux-gnu.2.25 -O2 -Wall -Wextra -Werror \
 *       -o guest-client-probe guest_client_probe.c -ldl
 */
#define _GNU_SOURCE

#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define SURFACE_ATTACH 1u
#define SURFACE_COMMIT 6u

struct wl_registry_listener {
    void (*global)(void *data, void *registry, uint32_t name,
                   const char *interface, uint32_t version);
    void (*global_remove)(void *data, void *registry, uint32_t name);
};

typedef void *(*connect_fn)(const char *);
typedef int (*roundtrip_fn)(void *);
typedef void *(*marshal_ctor_fn)(void *, uint32_t, const void *, ...);
typedef void *(*marshal_ctor_versioned_fn)(void *, uint32_t, const void *,
                                           uint32_t, ...);
typedef void (*marshal_fn)(void *, uint32_t, ...);
typedef int (*add_listener_fn)(void *, const void *, void *);

static uint32_t compositor_name;
static uint32_t compositor_version;

static void registry_global(void *data, void *registry, uint32_t name,
                            const char *interface, uint32_t version)
{
    (void)data;
    (void)registry;
    if (interface != NULL && strcmp(interface, "wl_compositor") == 0
        && compositor_name == 0) {
        compositor_name = name;
        compositor_version = version;
    }
}

int main(int argc, char **argv)
{
    struct wl_registry_listener listener = {registry_global, NULL};
    const void *(*surface_interface_at)(void);
    const void *compositor_interface;
    const void *registry_interface;
    const void *surface_interface;
    connect_fn connect_display;
    roundtrip_fn roundtrip;
    marshal_ctor_fn marshal_constructor;
    marshal_ctor_versioned_fn marshal_constructor_versioned;
    marshal_fn marshal;
    add_listener_fn add_listener;
    void *library;
    void *display;
    void *registry;
    void *compositor;
    void *surface;

    (void)surface_interface_at;
    library = dlopen("libwayland-client.so.0", RTLD_NOW | RTLD_GLOBAL);
    if (library == NULL) {
        printf("CLIENT dlopen-failed %s\n", dlerror());
        return 2;
    }
    connect_display = (connect_fn)dlsym(library, "wl_display_connect");
    roundtrip = (roundtrip_fn)dlsym(library, "wl_display_roundtrip");
    marshal_constructor = (marshal_ctor_fn)dlsym(library, "wl_proxy_marshal_constructor");
    marshal_constructor_versioned =
        (marshal_ctor_versioned_fn)dlsym(library, "wl_proxy_marshal_constructor_versioned");
    add_listener = (add_listener_fn)dlsym(library, "wl_proxy_add_listener");
    registry_interface = dlsym(library, "wl_registry_interface");
    compositor_interface = dlsym(library, "wl_compositor_interface");
    surface_interface = dlsym(library, "wl_surface_interface");
    /* Resolved through the global scope on purpose: this is the interposed one. */
    marshal = (marshal_fn)dlsym(RTLD_DEFAULT, "wl_proxy_marshal");
    if (!connect_display || !roundtrip || !marshal_constructor
        || !marshal_constructor_versioned || !add_listener || !registry_interface
        || !compositor_interface || !surface_interface || !marshal) {
        printf("CLIENT symbol-missing connect=%d roundtrip=%d ctor=%d ctorv=%d "
               "listener=%d registry=%d compositor=%d surface=%d marshal=%d\n",
               connect_display != NULL, roundtrip != NULL,
               marshal_constructor != NULL, marshal_constructor_versioned != NULL,
               add_listener != NULL, registry_interface != NULL,
               compositor_interface != NULL, surface_interface != NULL,
               marshal != NULL);
        return 3;
    }

    display = connect_display(NULL);
    if (display == NULL) {
        puts("CLIENT connect-failed");
        return 4;
    }
    /* wl_display.get_registry is a constructor: opcode 1. */
    registry = marshal_constructor(display, 1, registry_interface);
    if (registry == NULL || add_listener(registry, &listener, NULL) != 0) {
        puts("CLIENT registry-failed");
        return 5;
    }
    if (roundtrip(display) < 0 || compositor_name == 0) {
        puts("CLIENT no-compositor");
        return 6;
    }
    /* wl_registry.bind: a versioned constructor, opcode 0. */
    compositor = marshal_constructor_versioned(
        registry, 0, compositor_interface, compositor_version, compositor_name,
        "wl_compositor", compositor_version, NULL);
    if (compositor == NULL) {
        puts("CLIENT bind-failed");
        return 7;
    }
    /* wl_compositor.create_surface: constructor, opcode 0. */
    surface = marshal_constructor(compositor, 0, surface_interface);
    if (surface == NULL) {
        puts("CLIENT surface-failed");
        return 8;
    }
    printf("CLIENT surface=%p compositor_version=%u\n", surface, compositor_version);
    if (argc > 1 && strcmp(argv[1], "--inspect") == 0) {
        /* Report which 8-byte slot of the proxy holds the interface pointer, so
         * the interposer never guesses a struct layout. */
        unsigned int offset;

        printf("CLIENT interface_symbol=%p\n", surface_interface);
        for (offset = 0; offset <= 80; offset += 8) {
            void *slot = *(void **)((char *)surface + offset);
            printf("CLIENT slot[%u]=%p%s\n", offset, slot,
                   slot == surface_interface ? " <- interface" : "");
        }
        if (surface_interface != NULL) {
            const char *name = *(const char *const *)surface_interface;
            printf("CLIENT interface_name=%s\n", name != NULL ? name : "(null)");
        }
        return 0;
    }

    /* A client-requested null attach (opcode 1, signature "?oii") and two
     * commits (opcode 6, no arguments) through the interposed marshaller. */
    marshal(surface, SURFACE_ATTACH, NULL, 0, 0);
    marshal(surface, SURFACE_COMMIT);
    marshal(surface, SURFACE_ATTACH, NULL, 0, 0);
    marshal(surface, SURFACE_COMMIT);
    puts("CLIENT attach-commit-sent");
    return 0;
}
