#!/bin/sh
# Inject the stockui projection-only files into p5.img and sync back into the
# 36 GiB GPT image (only changed 1 MiB chunks).  See docs/vm/authentic-hmi-apps.md.
set -e
# Usage: inject-stockui.sh <stage-dir> <workspace>
# Copies the projection-only files listed in docs/vm/reproducing-the-authentic-image.md
# into p5 and places the partition back into the GPT image.
set -e
STAGE=${1:?stage directory}
WS=${2:?workspace (contains partimg-build/p5.img and layout.json)}
cd "$WS"

DFS=${DEBUGFS:-$(command -v debugfs || echo /opt/homebrew/opt/e2fsprogs/sbin/debugfs)}
ST=$STAGE
IMG=partimg-build/p5.img

# debugfs -R splits its command string on whitespace, so feed commands from a
# file with -f (one command per line); sources are space-free relative paths.
cat > /tmp/stockui-debugfs.cmds <<'EOF'
rm /app/bin/AppLauncher.sh
write applauncher-sh-new /app/bin/AppLauncher.sh
rm /etc/systemd/system/dbus-com.lge.car.micom.service
write micom-override.service /etc/systemd/system/dbus-com.lge.car.micom.service
rm /weston-apps-check.sh
write weston-apps-check.sh /weston-apps-check.sh
rm /etc/xdg/weston/weston_1920.ini
write weston_1920.ini /etc/xdg/weston/weston_1920.ini
rm /eng-data-sim
write eng-data-sim /eng-data-sim
rm /weston-vm-input.so
write weston-vm-input.so /weston-vm-input.so
write libsensors.so.4 /opt/software-egl18/lib/libsensors.so.4
write libedit.so.2 /opt/software-egl18/lib/libedit.so.2
write libbsd.so.0 /opt/software-egl18/lib/libbsd.so.0
write libstdc++.so.6 /opt/software-egl18/lib/libstdc++.so.6
write swrast_dri.so /usr/lib/dri/swrast_dri.so
mkdir /etc/systemd/system/ApplicationLauncher.service.d
write 50-vm-gl.conf /etc/systemd/system/ApplicationLauncher.service.d/50-vm-gl.conf
EOF

echo "=== debugfs write ==="
( cd "$ST" && "$DFS" -w -f /tmp/stockui-debugfs.cmds "$PWD/../../$IMG" )

echo "=== verify ==="
for p in /eng-data-sim /weston-vm-input.so /weston-apps-check.sh /init-authentic-hmi.sh \
         /app/bin/AppLauncher.sh /app/bin/AppLauncher.sh.vendor \
         /etc/xdg/weston/weston_1920.ini \
         /etc/systemd/system/dbus-com.lge.car.micom.service; do
  echo "--- $p"
  "$DFS" -R "stat $p" "$IMG" 2>&1 | grep -E "Inode:|Mode:|Size:" || echo "MISSING $p"
done

echo "=== sync partition 5 back into rootfs.img ==="
python3.13 ../../../tools/uk_fw/vm_partimg/sync-partition.py work/vm/stockui 5
