"""Local regression tests for the AppNavi Wayland observation interposer."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).parents[1]
COMPILER = shutil.which("gcc")


# The vendor libwayland-client exports no wl_surface_commit symbol at all: those
# calls are header inlines over wl_proxy_marshal. This mock reproduces that ABI,
# with the interface table layout the recovered 1.10 library uses (interface at
# offset 0, name first, methods table with signatures).
MOCK_MARSHAL_LIBRARY = r"""
#include <stdint.h>
#include <stdio.h>

struct my_message { const char *name; const char *signature; const void *types; };
struct my_interface {
    const char *name;
    int version;
    int method_count;
    const struct my_message *methods;
    int event_count;
    const struct my_message *events;
};
static const struct my_message surface_methods[] = {
    { "destroy", "", 0 },
    { "attach", "?oii", 0 },
    { "damage", "iiii", 0 },
    { "frame", "n", 0 },
    { "set_opaque_region", "?o", 0 },
    { "set_input_region", "?o", 0 },
    { "commit", "", 0 },
    { "bogus", "x", 0 },
    { "set_scale", "f", 0 },
};
const struct my_interface wl_surface_interface = {
    "wl_surface", 4, 9, surface_methods, 3, 0
};
union my_argument { int32_t i; uint32_t u; int32_t f; const char *s;
                     void *o; uint32_t n; void *a; int32_t h; };

const char *wl_proxy_get_class(void *proxy) { (void)proxy; return "wl_surface"; }

void wl_proxy_marshal_array(void *proxy, uint32_t opcode, union my_argument *args)
{
    (void)proxy;
    if (opcode == 8) {
        printf("REAL_ARRAY fixed=%d\n", args[0].f);
        return;
    }
    printf("REAL_ARRAY opcode=%u first=%p second=%d third=%d\n",
           opcode, args[0].o, args[1].i, args[2].i);
}

void wl_proxy_marshal(void *proxy, uint32_t opcode, ...)
{
    (void)proxy;
    printf("REAL_MARSHAL opcode=%u\n", opcode);
}
"""

MOCK_MARSHAL_APP = r"""
#include <stdint.h>
struct my_interface {
    const char *name;
    int version;
    int method_count;
    const void *methods;
    int event_count;
    const void *events;
};
struct proxy { const struct my_interface *interface; };
extern const struct my_interface wl_surface_interface;
extern void wl_proxy_marshal(void *, uint32_t, ...);
int main(void)
{
    struct proxy surface = { &wl_surface_interface };
    wl_proxy_marshal(&surface, 1, 0, 0, 0);
    wl_proxy_marshal(&surface, 6);
    wl_proxy_marshal(&surface, 1, 0, 0, 0);
    wl_proxy_marshal(&surface, 6);
    return 0;
}
"""

MOCK_FIXED_APP = r"""
#include <stdint.h>
struct my_interface {
    const char *name;
    int version;
    int method_count;
    const void *methods;
    int event_count;
    const void *events;
};
struct proxy { const struct my_interface *interface; };
extern const struct my_interface wl_surface_interface;
extern void wl_proxy_marshal(void *, uint32_t, ...);
int main(void)
{
    struct proxy surface = { &wl_surface_interface };
    /* |'f'| is wl_fixed_t: a 24.8 fixed-point integer (1.5 == 0x0180), so it travels
     * in an integer slot and the wrapper must forward the integer unchanged. */
    wl_proxy_marshal(&surface, 8, 0x0180);
    wl_proxy_marshal(&surface, 6);
    return 0;
}
"""

MOCK_FALLBACK_APP = r"""
#include <stdint.h>
struct my_interface {
    const char *name;
    int version;
    int method_count;
    const void *methods;
    int event_count;
    const void *events;
};
struct proxy { const struct my_interface *interface; };
extern const struct my_interface wl_surface_interface;
extern void wl_proxy_marshal(void *, uint32_t, ...);
int main(void)
{
    struct proxy readable = { &wl_surface_interface };
    struct proxy unreadable = { 0 };
    /* 7 is declared with an unsupported signature code; the second proxy has no
     * interface at all. Neither may lose the request. */
    wl_proxy_marshal(&readable, 7);
    wl_proxy_marshal(&readable, 7, 1);
    wl_proxy_marshal(&unreadable, 2, 3, 4);
    return 0;
}
"""

MOCK_NO_ARRAY_LIBRARY = r"""
#include <stdint.h>
#include <stdio.h>

struct my_message { const char *name; const char *signature; const void *types; };
struct my_interface {
    const char *name;
    int version;
    int method_count;
    const struct my_message *methods;
    int event_count;
    const struct my_message *events;
};
static const struct my_message surface_methods[] = {
    { "destroy", "", 0 },
    { "attach", "?oii", 0 },
    { "damage", "iiii", 0 },
    { "frame", "n", 0 },
    { "set_opaque_region", "?o", 0 },
    { "set_input_region", "?o", 0 },
    { "commit", "", 0 },
};
const struct my_interface wl_surface_interface = {
    "wl_surface", 4, 7, surface_methods, 3, 0
};

const char *wl_proxy_get_class(void *proxy) { (void)proxy; return "wl_surface"; }

/* Deliberately no wl_proxy_marshal_array: the observer must still deliver. */
void wl_proxy_marshal(void *proxy, uint32_t opcode, ...)
{
    (void)proxy;
    printf("REAL_MARSHAL opcode=%u\\n", opcode);
}
"""


MOCK_WAYLAND = r"""
#include <stdio.h>
struct wl_surface { int value; };
struct wl_buffer { int value; };
void wl_surface_attach(struct wl_surface *surface, struct wl_buffer *buffer,
                       int x, int y)
{
    (void)surface;
    printf("REAL_ATTACH null=%d x=%d y=%d\n", buffer == NULL, x, y);
}
void wl_surface_commit(struct wl_surface *surface)
{
    (void)surface;
    puts("REAL_COMMIT");
}
"""

MOCK_APP = r"""
struct wl_surface { int value; };
struct wl_buffer { int value; };
extern void wl_surface_attach(struct wl_surface *, struct wl_buffer *, int, int);
extern void wl_surface_commit(struct wl_surface *);
int main(void)
{
    struct wl_surface surface = {0};
    struct wl_buffer buffer = {0};
    wl_surface_attach(&surface, &buffer, 4, 5);
    wl_surface_commit(&surface);
    wl_surface_attach(&surface, 0, 0, 0);
    wl_surface_commit(&surface);
    return 0;
}
"""


MOCK_BYPASS = r"""
#include <dlfcn.h>
#include <stdio.h>
struct wl_surface { int value; };
struct wl_buffer { int value; };
extern void wl_surface_attach(struct wl_surface *, struct wl_buffer *, int, int);
int main(int argc, char **argv)
{
    struct wl_surface surface = {0};
    struct wl_buffer buffer = {0};
    void (*commit)(struct wl_surface *);
    void *lib;

    if (argc != 2) {
        return 4;
    }
    lib = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (lib == NULL) {
        puts("DLOPEN_FAILED");
        return 2;
    }
    commit = (void (*)(struct wl_surface *))dlsym(lib, "wl_surface_commit");
    if (commit == NULL) {
        return 3;
    }
    wl_surface_attach(&surface, &buffer, 1, 2);
    commit(&surface);
    return 0;
}
"""


@unittest.skipUnless(sys.platform.startswith("linux") and COMPILER, "Linux and gcc required")
class NaviBgObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        mock_source = root / "mock-wayland.c"
        app_source = root / "app.c"
        mock_source.write_text(MOCK_WAYLAND)
        app_source.write_text(MOCK_APP)
        bypass_source = root / "bypass.c"
        bypass_source.write_text(MOCK_BYPASS)
        cls.mock_library = root / "libmockwayland.so"
        cls.app = root / "AppNavi"
        cls.bypass = root / "AppNaviBypass"
        cls.observer = root / "navi-bg-0x0.so"
        commands = [
            [COMPILER, "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
             "-Wl,-soname,libmockwayland.so", "-o", str(cls.mock_library), str(mock_source)],
            [COMPILER, "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(cls.app),
             str(app_source), "-L" + str(root), "-lmockwayland", "-Wl,-rpath," + str(root)],
            [COMPILER, "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
             "-DNAVI_BG_DISABLE_KMSG", "-o", str(cls.observer),
             str(PROJECT / "tools/uk_fw/guest/navi_bg_0x0.c"), "-ldl"],
            [COMPILER, "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(cls.bypass),
             str(bypass_source), "-L" + str(root), "-lmockwayland", "-ldl",
             "-Wl,-rpath," + str(root)],
        ]
        for command in commands:
            subprocess.run(command, check=True, capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_probe(self, settings=None):
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.observer)
        env.pop("NAVI_BG_HOLD_AFTER", None)
        env.pop("NAVI_BG_HOLD_COUNT", None)
        env.update(settings or {})
        return subprocess.run(
            [str(self.app)], env=env, capture_output=True, text=True, timeout=5
        )

    def test_observer_logs_null_attach_and_commit_without_changing_requests(self):
        result = self.run_probe()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "REAL_ATTACH null=0 x=4 y=5",
                "REAL_COMMIT",
                "REAL_ATTACH null=1 x=0 y=0",
                "REAL_COMMIT",
            ],
        )
        self.assertIn("null-attach surface#0 target=1", result.stderr)
        self.assertIn("commit-after-null-attach surface#0 forced=0", result.stderr)
        self.assertIn("null_attaches=1 commits_after_null=1", result.stderr)
        self.assertIn("suppressed=0", result.stderr)

    def test_verdict_proves_interposition_when_the_wrapper_is_first(self):
        result = self.run_probe()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("interposed=1", result.stderr)
        self.assertIn("observation verdict=observed", result.stderr)
        self.assertIn("complete=1", result.stderr)

    def test_verdict_is_unverified_when_the_client_commits_outside_the_link_chain(self):
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.observer)
        env.pop("NAVI_BG_HOLD_AFTER", None)
        result = subprocess.run(
            [str(self.bypass), str(self.mock_library)],
            env=env, capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REAL_COMMIT", result.stdout)
        self.assertNotIn("observation verdict=observed", result.stderr)
        self.assertIn("observation verdict=unverified", result.stderr)
        self.assertIn("complete=0", result.stderr)

    def test_explicit_hold_is_labeled_separately_from_client_null_attach(self):
        result = self.run_probe({"NAVI_BG_HOLD_AFTER": "0", "NAVI_BG_HOLD_COUNT": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("REAL_ATTACH null=1"), 2)
        self.assertIn("commit-after-null-attach surface#0 forced=1", result.stderr)
        self.assertIn("commit-after-null-attach surface#0 forced=0", result.stderr)
        self.assertIn("suppressed=1", result.stderr)


@unittest.skipUnless(sys.platform.startswith("linux") and COMPILER, "Linux and gcc required")
class MarshalInterpositionTests(unittest.TestCase):
    """The hook that fires for this vendor library: wl_proxy_marshal."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        library_source = root / "mock-marshal.c"
        app_source = root / "app.c"
        library_source.write_text(MOCK_MARSHAL_LIBRARY)
        app_source.write_text(MOCK_MARSHAL_APP)
        fallback_source = root / "fallback.c"
        fallback_source.write_text(MOCK_FALLBACK_APP)
        no_array_source = root / "no-array.c"
        no_array_source.write_text(MOCK_NO_ARRAY_LIBRARY)
        fixed_source = root / "fixed.c"
        fixed_source.write_text(MOCK_FIXED_APP)
        cls.library = root / "libmockmarshal.so"
        cls.no_array_library = root / "libmocknoarray.so"
        cls.app = root / "AppNavi"
        cls.fallback = root / "AppNaviFallback"
        cls.no_array_app = root / "AppNaviNoArray"
        cls.fixed_app = root / "AppNaviFixed"
        cls.observer = root / "navi-bg-0x0.so"
        for command in (
            [COMPILER, "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
             "-Wl,-soname,libmockmarshal.so", "-o", str(cls.library), str(library_source)],
            [COMPILER, "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(cls.app),
             str(app_source), "-L" + str(root), "-lmockmarshal", "-Wl,-rpath," + str(root)],
            [COMPILER, "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
             "-DNAVI_BG_DISABLE_KMSG", "-o", str(cls.observer),
             str(PROJECT / "tools/uk_fw/guest/navi_bg_0x0.c"), "-ldl"],
            [COMPILER, "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(cls.fallback),
             str(fallback_source), "-L" + str(root), "-lmockmarshal",
             "-Wl,-rpath," + str(root)],
            [COMPILER, "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
             "-Wl,-soname,libmocknoarray.so", "-o", str(cls.no_array_library),
             str(no_array_source)],
            [COMPILER, "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(cls.no_array_app),
             str(app_source), "-L" + str(root), "-lmocknoarray",
             "-Wl,-rpath," + str(root)],
            [COMPILER, "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(cls.fixed_app),
             str(fixed_source), "-L" + str(root), "-lmockmarshal",
             "-Wl,-rpath," + str(root)],
        ):
            subprocess.run(command, check=True, capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_probe(self):
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.observer)
        env.pop("NAVI_BG_HOLD_AFTER", None)
        env.pop("NAVI_BG_CLIENT_MATCH", None)
        return subprocess.run([str(self.app)], env=env, capture_output=True,
                              text=True, timeout=5)

    def test_marshalled_attach_and_commit_are_observed_and_forwarded_once(self):
        result = self.run_probe()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("REAL_ARRAY opcode=1"), 2)
        self.assertEqual(result.stdout.count("REAL_ARRAY opcode=6"), 2)
        self.assertNotIn("REAL_MARSHAL", result.stdout)
        self.assertIn("REAL_ARRAY opcode=1 first=(nil) second=0 third=0", result.stdout)
        self.assertIn("null-attach surface#0 target=1", result.stderr)
        self.assertIn("commit-after-null-attach surface#0 forced=0", result.stderr)
        self.assertIn("interposed=1", result.stderr)
        self.assertIn("observation verdict=observed", result.stderr)
        self.assertIn("complete=1", result.stderr)

    def test_a_fixed_point_argument_survives_the_wrapper(self):
        """|'f'| is a 24.8 fixed-point integer; the wrapper must not alter it."""
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.observer)
        env.pop("NAVI_BG_HOLD_AFTER", None)
        env.pop("NAVI_BG_CLIENT_MATCH", None)
        result = subprocess.run([str(self.fixed_app)], env=env, capture_output=True,
                                text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REAL_ARRAY fixed=384", result.stdout)
        self.assertEqual(result.stdout.count("REAL_ARRAY fixed="), 1, result.stdout)

    def test_undecodable_requests_are_forwarded_not_dropped(self):
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.observer)
        env.pop("NAVI_BG_HOLD_AFTER", None)
        env.pop("NAVI_BG_CLIENT_MATCH", None)
        result = subprocess.run([str(self.fallback)], env=env, capture_output=True,
                                text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        # Every call reaches the library through the vararg pass-through instead of
        # disappearing, and none of them is rebuilt with invented arguments.
        self.assertEqual(result.stdout.count("REAL_MARSHAL"), 3, result.stdout)
        self.assertEqual(result.stdout.count("REAL_MARSHAL opcode=7"), 2, result.stdout)
        self.assertEqual(result.stdout.count("REAL_MARSHAL opcode=2"), 1, result.stdout)
        self.assertNotIn("REAL_ARRAY", result.stdout)
        self.assertIn("undecoded-opcode opcode=7 signature=x forwarded=1", result.stderr)
        self.assertIn("undecoded-opcode opcode=2 signature=(unreadable) forwarded=1",
                      result.stderr)

    def test_missing_array_entry_still_delivers_the_request(self):
        """No wl_proxy_marshal_array: replay through the vararg entry, never NULL."""
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.observer)
        env.pop("NAVI_BG_HOLD_AFTER", None)
        env.pop("NAVI_BG_CLIENT_MATCH", None)
        result = subprocess.run([str(self.no_array_app)], env=env,
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("REAL_MARSHAL opcode=1"), 2, result.stdout)
        self.assertEqual(result.stdout.count("REAL_MARSHAL opcode=6"), 2, result.stdout)
        self.assertNotIn("REAL_ARRAY", result.stdout)

    def test_hold_suppresses_a_forwarded_attach(self):
        env = os.environ.copy()
        env["LD_PRELOAD"] = str(self.observer)
        env["NAVI_BG_HOLD_AFTER"] = "0"
        env["NAVI_BG_HOLD_COUNT"] = "1"
        env.pop("NAVI_BG_CLIENT_MATCH", None)
        result = subprocess.run([str(self.app)], env=env, capture_output=True,
                                text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("suppressed=1", result.stderr)
        self.assertEqual(result.stdout.count("REAL_ARRAY opcode=1"), 2)
