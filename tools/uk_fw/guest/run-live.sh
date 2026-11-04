#!/bin/sh
# Report whether the vendor stack is up, and print the exact commands for interacting.
BB=/bin/busybox
W=/tmp/launcher-chain/weston.log
echo "compositor: $($BB pidof weston-headless)"
echo "homescreen: $($BB pidof AppHomeScreen)"
echo "engineer  : $($BB pidof AppEngineerMode)"
echo "surfaces  :"
$BB grep -a 'Surface id(' "$W" 2>/dev/null | $BB tail -4 | $BB sed 's/^/  /'
SID=$($BB grep -a 'Surface id(' "$W" 2>/dev/null | $BB tail -1 | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/')
[ -n "$SID" ] && echo "newest surface is $SID - place it with:  /usr/bin/ivi-wm $SID"
echo
echo "capture : cd /tmp && timeout 25 /usr/libexec/weston-screenshooter"
echo "touch   : echo 'click 960 400' > /tmp/weston-vm-input"
echo "logs    : /tmp/launcher-chain/{launcher,weston,dlt}.log"
