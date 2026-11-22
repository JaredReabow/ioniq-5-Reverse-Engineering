"""Frame-bound input gate for the explicitly simulated Wi-Fi workbench."""
from __future__ import annotations

import hashlib
import subprocess
import threading
from .session import wifi_sim_check_listener, wifi_sim_inventory

PAGE_HEADER_WIDTH = 285
PAGE_HEADER_HEIGHT = 90
PAGE_HEADER_MASK_SHA256 = '2ed0281ceb8f96c17b4b245aa1b117929f8c9c060635033fe91aaacc92585d66'
# Exact status-page controls from the reviewed 1920x720 simulation frame.
CONTROL_RECTS = ((20, 411, 238, 463), (250, 411, 469, 463), (481, 411, 720, 463))


def _page_header_mask_sha256(decoded):
    """Hash stable colour classes for the badge and Wi-Fi page heading.

    The original exact RGBA pin came from all six retained 2026-11-19
    qualification frames. A later compositor frame differed only by up to
    three colour levels, so exact antialiased edge bytes were not a stable
    identity. This mask still binds the exact geometry of the yellow
    simulation badge, blue Wi-Fi mark, and white/grey page heading while
    ignoring only pixels outside those reviewed colour classes.
    """
    if len(decoded) != PAGE_HEADER_WIDTH * PAGE_HEADER_HEIGHT * 4:
        raise ValueError('invalid simulation page header size')
    mask = bytearray(PAGE_HEADER_WIDTH * PAGE_HEADER_HEIGHT)
    for pixel, offset in enumerate(range(0, len(decoded), 4)):
        red, green, blue, alpha = decoded[offset:offset + 4]
        if alpha != 255:
            continue
        if red > 63 and green > 38 and blue < 26 and red * 100 > green * 115:
            mask[pixel] = 1  # yellow simulation badge
        elif blue > 120 and blue > red * 2 and blue * 2 > green * 3:
            mask[pixel] = 2  # blue Wi-Fi mark
        elif min(red, green, blue) > 180 and max(red, green, blue) - min(red, green, blue) < 10:
            mask[pixel] = 3  # bright page title
        elif 60 < red < 180 and max(red, green, blue) - min(red, green, blue) < 10:
            mask[pixel] = 4  # grey page subtitle
    return hashlib.sha256(mask).hexdigest()


class WifiSimInputGuard:
    """Allow only frame-bound clicks inside the three visible mode controls."""
    simulation_mode = True

    def __init__(self, backend, shell, runtime, image_tool='/opt/homebrew/bin/magick'):
        self._backend, self._shell, self._runtime, self._image_tool = backend, shell, runtime, image_tool
        self._lock = threading.Lock()
        self._used = set()

    def __getattr__(self, name):
        return getattr(self._backend, name)

    def _identity(self):
        cmd = '''( p=$(/bin/busybox pidof AppHomeScreen); set -- $p; [ "$#" = 1 ] || exit 1; printf "PID=%s START=" "$1"; /bin/busybox awk '{print $22}' /proc/$1/stat; /usr/bin/readlink /proc/$1/exe )'''
        value = self._shell._run(cmd, timeout=10).decode('ascii', 'strict')
        lines = value.splitlines()
        if len(lines) != 2 or not lines[0].startswith('PID=') or lines[1] != '/app/bin/AppHomeScreen':
            raise RuntimeError('simulation page process identity unavailable')
        return value

    def prepare(self, reference_frame):
        """Precheck the displayed reference and bind it to guest identity.

        Runtime requires a byte-identical fresh frame before calling finish, so
        the badge checked here also belongs to that fresh frame.
        """
        decoded = subprocess.run([self._image_tool, 'png:-', '-crop', '285x90+0+118', '+repage',
                                  '-alpha', 'on', '-depth', '8', 'rgba:-'], input=reference_frame,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=True).stdout
        try:
            visible = _page_header_mask_sha256(decoded) == PAGE_HEADER_MASK_SHA256
        except ValueError:
            visible = False
        if not visible:
            raise RuntimeError('simulation badge or Wi-Fi page is not visible')
        wifi_sim_inventory(self._shell, 'input')
        wifi_sim_check_listener(self._shell)
        return self._identity()

    def finish(self, identity, frame):
        """Recheck guest network, listener and identity after frame equality."""
        wifi_sim_inventory(self._shell, 'input-final')
        wifi_sim_check_listener(self._shell)
        if identity != self._identity():
            raise RuntimeError('simulation page identity changed')

    def send_pointer(self, *, action, x1, y1, frame_sequence=None, correlation_id=None, **kwargs):
        if (action != 'click' or kwargs.get('x2') is not None or kwargs.get('y2') is not None or
                type(x1) is not int or type(y1) is not int or
                not any(x0 < x1 < x2 and y0 < y1 < y2 for x0, y0, x2, y2 in CONTROL_RECTS)):
            raise ValueError('simulation permits only the three visible mode buttons')
        if type(frame_sequence) is not int or not 1 <= frame_sequence <= 2**53 - 1:
            raise ValueError('simulation input requires a displayed frame sequence')
        with self._lock:
            if frame_sequence in self._used or len(self._used) >= 10000:
                raise ValueError('simulation frame is already used or session limit reached')
            self._used.add(frame_sequence)
            return self._runtime.wifi_sim_guarded_click(frame_sequence=frame_sequence, x=x1, y=y1,
                                                                  verifier=self, correlation_id=correlation_id)

    def send_key(self, **kwargs):
        raise ValueError('keyboard input is disabled in Wi-Fi simulation mode')

    def observe_and_confirm_once(self, **kwargs):
        raise ValueError('Confirm is disabled after Wi-Fi simulation starts')
