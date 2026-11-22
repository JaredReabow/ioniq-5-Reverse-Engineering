"""Local, no-network Gen5W VM workbench.

The workbench controls only QEMU processes that it starts itself.  Its browser
surface is a loopback operator console, not a vehicle control interface.
"""

WORKBENCH_VERSION = "0.4.0"


def vm_workbench_version() -> str:
    """Return the boot-printed workbench version."""

    return WORKBENCH_VERSION
