#!/bin/busybox sh
# VM-only rendering compatibility: isolate Qt's threaded render loop to
# AppStandbyClock while leaving the rest of the recovered launcher chain on the
# established basic-loop control.
export QSG_RENDER_LOOP=threaded
exec /AppStandbyClock.real "$@"
