#!/bin/sh
# Delete log prior to version 1.7.10
if grep -qF 'PHYSIN=' /var/log/log-aegis; then {
  /opt/bolemo/scripts/aegis down
  /sbin/uci -c /opt/bolemo/etc/config/ delete aegis.log.len
  /bin/rm -f /var/log/log-aegis; } 2>/dev/null
fi
echo '- pre-upgrade script: done!'
