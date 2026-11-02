/*
 * interpose_probe.c — prove the guest's dynamic linker resolves a Wayland
 * symbol to the observer wrapper instead of the real library.
 *
 * The observer in navi_bg_0x0.c can only report a commit it was handed, so the
 * link chain itself has to be verified where it runs. This probe dlopen()s the
 * vendor libwayland-client in the global scope (the same scope a client resolves
 * through) and asks for wl_proxy_marshal, which is the ABI that library really
 * exports: wl_surface_attach/commit are header inlines there and have no symbol
 * at all. Run it under LD_PRELOAD: only a path naming the observer, plus a
 * different address inside the library, proves the interposition.
 *
 * Build (vendor glibc floor):
 *   zig cc -target x86_64-linux-gnu.2.25 -O2 -Wall -Wextra -Werror \
 *       -o interpose-probe interpose_probe.c -ldl
 */
#define _GNU_SOURCE

#include <dlfcn.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    const char *library = argc > 1 ? argv[1] : "libwayland-client.so.0";
    Dl_info info;
    void *handle;
    void *symbol;
    void *native;

    handle = dlopen(library, RTLD_NOW | RTLD_GLOBAL);
    if (handle == NULL) {
        printf("PROBE dlopen-failed %s\n", dlerror());
        return 2;
    }
    symbol = dlsym(RTLD_DEFAULT, "wl_proxy_marshal");
    if (symbol == NULL) {
        printf("PROBE symbol-missing %s\n", dlerror());
        return 3;
    }
    native = dlsym(handle, "wl_proxy_marshal");
    printf("PROBE shared=%d\n", symbol == native);
    printf("PROBE surface_symbol=%d\n",
           dlsym(handle, "wl_surface_commit") != NULL);
    memset(&info, 0, sizeof(info));
    if (dladdr(symbol, &info) == 0 || info.dli_fname == NULL
        || info.dli_fname[0] == '\0') {
        puts("PROBE dladdr-failed");
        return 4;
    }
    printf("PROBE resolved=%s\n", info.dli_fname);
    return symbol == native ? 5 : 0;
}
