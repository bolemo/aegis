/bin/rm -f /tmp/aegis-logd 2>/dev/null
trapf() {  [ -e /var/run/aegis-logd.pid ] || exit; PID=$(cat /var/run/aegis-logd.pid); /bin/rm -f /var/run/aegis-logd.pid; [ -e /tmp/aegis-logd ] && /bin/rm -f /tmp/aegis-logd;  exit; } 2>>/dev/null
trap "trapf TERM" TERM; trap "trapf INT" INT; trap "trapf QUIT" QUIT; trap "trapf EXIT" EXIT
touch /var/log/log-aegis
inode() { set -- $(/bin/ls -i /var/log/log-message); echo $1; }
lc() { set -- $(/usr/bin/wc -l $1); echo $1; }
while :; do
local INODE=$(inode)
local NUMLINES=$(uci -qc /opt/bolemo/etc/config get aegis.log.len)
if [ -s /var/log/log-aegis ]; then
local FIRST_MSG_LINE="$(/usr/bin/awk '/\[aegis\]/{print; exit}' /var/log/log-message)"
if [ "$FIRST_MSG_LINE" ]; then
local FIRST_EXT_TS="$(/usr/bin/awk -F':' 'NR==1{print $1; exit}' /var/log/log-aegis)"
if [ 0${FIRST_MSG_LINE%%:*} -gt 0$FIRST_EXT_TS ]; then :>/tmp/aegis-logd
/usr/bin/awk '$0=="'"$FIRST_MSG_LINE"'"{exit} {print}' /var/log/log-aegis >>/tmp/aegis-logd
if [ 0$NUMLINES -lt 0$(lc /tmp/aegis-logd) ]
then /usr/bin/tail -n $NUMLINES /tmp/aegis-logd >/var/log/log-aegis
else /bin/cat /tmp/aegis-logd >/var/log/log-aegis
fi
else :>/var/log/log-aegis 
fi
elif [ 0$NUMLINES -lt 0$(lc /var/log/log-aegis) ]
then /usr/bin/tail -n $NUMLINES /var/log/log-aegis >/tmp/aegis-logd; cat /tmp/aegis-logd >/var/log/log-aegis
fi
else :>/var/log/log-aegis 
fi
/bin/rm -f /tmp/aegis-logd
local C=1 D=1 FC=false
while /usr/bin/awk -F: '/\[aegis\]/{st=index($0," ");if ($1==pts) {c++} else {c=0;pts=$1}; printf("%s:%.3d:%s\n",$1,c,substr($0,st)); fflush()}'; do
sleep 2 & wait $!
[ "$INODE" != "$(inode)" ] && break
if [ $C -eq 10 ]; then
if ! /usr/sbin/iptables -w -S 2>/dev/null |/bin/grep -qF -- "-j LOG --log-prefix \"[aegis] "; then
if [ -e "/tmp/aegis_lock" ]; then :
elif $FC; then  /bin/kill $(cat /var/run/aegis-logd.pid); fi
FC=true; C=5
else FC=false; C=1; fi
else C=$((C+1)); fi
if [ $D -eq 300 ]; then  break
else D=$((D+1)); fi
done </var/log/log-message >>/var/log/log-aegis
done 2>>"/dev/null"
