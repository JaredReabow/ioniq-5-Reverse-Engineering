#!/usr/bin/env python3.13
"""Boot the micomsim CoW clone and run /run-micomsim.sh (chain + real
ApplicationManager + engineering-mode launch), watching whether the manager's
MICOM replies stop being "not VALID" and show_window_fg is delivered. The
engineering-surface capture streams over /dev/ttyS2 to a host file."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vm_boot as vb  # noqa: E402

CHARDEF_PATH = "/tmp/micomsim-shot.b64"

cmd = (
    "export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0\n"
    "sh /run-micomsim.sh\n"
)

rc = vb.run(
    Path("work/vm/micomsim"),
    True,
    cmd,
    timeout=700.0,
    memory_mib=2048,
    extra_devices=[
        "-chardev", f"file,id=micomsimout,path={CHARDEF_PATH}",
        "isa-serial,chardev=micomsimout,index=2",
    ],
)
print("RUN_RC", rc)
