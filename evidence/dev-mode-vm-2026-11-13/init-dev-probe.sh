#!/bin/sh
/dev-mode-probe.sh &
exec /lib/systemd/esinit
