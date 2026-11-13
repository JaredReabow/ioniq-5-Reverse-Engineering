#!/bin/sh
# VM-only observation, not a hardware enablement procedure.
# Baseline 30 guest seconds after systemd becomes responsive; observe 60 seconds after touch.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
while [ ! -r /proc/uptime ] || [ ! -e /dev/ttyS0 ]; do sleep 1; done
exec >>/dev/ttyS0 2>&1
say() { printf '\n[no-unece-probe] '; cat /proc/uptime; printf '%s\n' "$*"; }
snapshot() {
    say "SNAPSHOT $1"
    ls -l /tmp/no_unece /tmp/no_isa 2>&1
    systemctl show supplicantmanager.path supplicantmanager.service -p Id -p LoadState -p ActiveState -p SubState -p Result -p MainPID -p ExecMainStatus -p NRestarts 2>&1
    ps | grep -E 'supplicant|AppSetup|AppLauncher' || true
    ls /sys/class/net 2>&1
}
i=0
while ! systemctl show supplicantmanager.path >/dev/null 2>&1; do
    i=$((i+1)); [ "$i" -lt 120 ] || { say 'ABORT systemd_unresponsive'; exit 2; }
    sleep 1
done
say 'BEGIN baseline_s=30 observation_s=60 sample_s=10'
systemctl cat supplicantmanager.path supplicantmanager.service 2>&1
snapshot baseline_start
sleep 30
snapshot before_touch
if [ -e /tmp/no_unece ]; then
    say 'NOT_TOUCHED marker_already_present; natural boot already satisfies PathExists'
else
    say 'ACTION touch /tmp/no_unece'
    touch /tmp/no_unece || { say 'ABORT touch_failed'; exit 3; }
fi
i=0
while [ "$i" -lt 6 ]; do sleep 10; i=$((i+1)); snapshot "post_$((i*10))s"; done
say 'JOURNAL'
journalctl --no-pager -u supplicantmanager.path -u supplicantmanager.service -n 120 2>&1
say 'KERNEL_WIFI'
dmesg | grep -iE 'bcmdhd|cfg80211|wlan|gpio' | tail -50
say 'COMPLETE no UI rendering or radio success inferred'
printf '\nNO_UNECE_PROBE_COMPLETE\n'
