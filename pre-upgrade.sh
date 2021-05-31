#!/bin/sh
# Delete log prior to version 1.7.10
if grep -qF 'PHYSIN=' /var/log/log-aegis; then {
  /opt/bolemo/scripts/aegis down
  /sbin/uci -qc /opt/bolemo/etc/config/ delete aegis.log.len
  /sbin/uci -qc /opt/bolemo/etc/config delete aegis_web.log.basetime
  /sbin/uci -qc /opt/bolemo/etc/config/ set aegis.repo="stable"
  /sbin/uci -qc /opt/bolemo/etc/config/ commit
  /bin/rm -f /var/log/log-aegis; } 2>/dev/null
fi
echo '- pre-upgrade script: done!'
