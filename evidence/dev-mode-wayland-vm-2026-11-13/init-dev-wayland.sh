#!/bin/sh
/dev-mode-wayland-probe.sh &
exec /lib/systemd/esinit
