#!/usr/bin/env python3.13
"""Boot the engpaint CoW clone and run /run-engpaint.sh (engineering-mode paint
diagnostic). Surface captures stream over the guest's /dev/ttyS2 to a host file
(/tmp/engpaint-shot.b64); the console carries the text evidence."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vm_boot as vb  # noqa: E402

CHARDEF_PATH = "/tmp/engpaint-shot.b64"

cmd = (
    "export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0\n"
    "sh /run-engpaint8.sh\n"
)

rc = vb.run(
    Path("work/vm/engpaint"),
    True,
    cmd,
    timeout=700.0,
    memory_mib=2048,
    extra_devices=[
        "-chardev", f"file,id=engout,path={CHARDEF_PATH}",
        "isa-serial,chardev=engout,index=2",
    ],
)
print("RUN_RC", rc)
