/* VM-only observational LD_PRELOAD shim for Qt Quick input dispatch. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stddef.h>
#include <unistd.h>

static void log_event(const char *name, size_t n)
{
    int fd = open("/tmp/launcher-chain/qt-input-observe.log",
                  O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0)
        return;
    (void)write(fd, name, n);
    (void)write(fd, "\n", 1);
    (void)close(fd);
}

#define HOOK_VOID(cname, symbol, label)                                      \
    void cname(void *self, void *event) __asm__(symbol);                     \
    void cname(void *self, void *event)                                      \
    {                                                                         \
        typedef void (*fn_t)(void *, void *);                                \
        static fn_t next;                                                     \
        log_event(label, sizeof(label) - 1);                                 \
        if (!next)                                                            \
            next = (fn_t)dlsym(RTLD_NEXT, symbol);                           \
        if (next)                                                             \
            next(self, event);                                                \
    }

HOOK_VOID(observe_qquickview_mouse_press,
          "_ZN10QQuickView15mousePressEventEP11QMouseEvent",
          "QT_INPUT_QQUICKVIEW_MOUSE_PRESS")
HOOK_VOID(observe_qquickview_mouse_release,
          "_ZN10QQuickView17mouseReleaseEventEP11QMouseEvent",
          "QT_INPUT_QQUICKVIEW_MOUSE_RELEASE")
HOOK_VOID(observe_qquickview_mouse_move,
          "_ZN10QQuickView14mouseMoveEventEP11QMouseEvent",
          "QT_INPUT_QQUICKVIEW_MOUSE_MOVE")
HOOK_VOID(observe_qwindow_touch,
          "_ZN7QWindow10touchEventEP11QTouchEvent",
          "QT_INPUT_QWINDOW_TOUCH")
