#! /bin/sh

SC_NAME="bolemo_firewall"
IPSET_NAME="bolemo_firewall"
IPSET_TMP="${IPSET_NAME}_tmp"
ROOT_DIR="/mnt/optware/bolemo"
SRC_LIST="$ROOT_DIR/etc/$SC_NAME.sources"
IP_LIST="/tmp/$SC_NAME.netset"
TMP_FILE="$IP_LIST.tmp"
FWS_FILE="/opt/scripts/firewall-start-bolemo.sh"

check_firewall_start() {
  [ -x $FWS_FILE ] || return 1
  [ "$(sed 's/[[:space:]]\+/ /g' $FWS_FILE | grep -- "iptables -I INPUT -i brwan -m set --match-set $IPSET_NAME src -j DROP")" ] || return 1
  [ "$(sed 's/[[:space:]]\+/ /g' $FWS_FILE | grep -- "iptables -I FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP")" ] || return 1
  return 0
}

init() {
  ipset -! create $IPSET_NAME hash:net
  if ! check_firewall_start; then
    { echo "iptables -I INPUT   -i brwan -m set --match-set $IPSET_NAME src -j DROP";
      echo "iptables -I FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP";
    } > $FWS_FILE
    chmod +x $FWS_FILE
  fi
  /usr/sbin/net-wall restart
}

clean() {
  [ -e $FWS_FILE ] && rm $FWS_FILE
#  iptables -D INPUT   -i brwan -m set --match-set $IPSET_NAME src -j DROP
#  iptables -D FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP
  /usr/sbin/net-wall restart
  ipset -q destroy $IPSET_NAME
  ipset -q destroy $IPSET_TMP
  [ -e $TMP_FILE ] && rm $TMP_FILE
}

set_ipset() {
  [ -r $IP_LIST ] || { >&2 echo "$IP_LIST not readable!"; return; }

  ipset -! create $IPSET_TMP hash:net
  ipset flush $IPSET_TMP > /dev/null
  while read -r IP; do
    ipset add $IPSET_TMP "$IP"
  done < $IP_LIST
  ipset swap $IPSET_NAME $IPSET_TMP
  ipset destroy $IPSET_TMP
}

update_iplist() {
  [ -r $SRC_LIST ] || { >&2 echo "$SRC_LIST not readable!"; return; }

  :>"$TMP_FILE"
  # Process each source url
  grep -v "^[[:space:]*\#]" "$SRC_LIST" | while read -r URL; do
    wget -qO- "$URL" | grep '^[0-9]' | sed -e 's/;.*//' >> "$TMP_FILE"
  done
  sort "$TMP_FILE" | uniq > "$IP_LIST"
  rm "$TMP_FILE"
}

status() {
  check_firewall_start && STAT_FWS='ok' || STAT_FWS=''
  STAT_IPT_IN=$(iptables -S INPUT | grep -- "-A INPUT -i brwan -m set --match-set $IPSET_NAME src -j DROP")
  STAT_IPT_FW=$(iptables -S FORWARD | grep -- "-A FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP")
  STAT_IPSET=$(ipset list $IPSET_NAME -t)
  if   [ "$STAT_IPT_IN" -a "$STAT_IPT_FW" -a "$STAT_IPSET" -a "$STAT_FWS" ]; then echo -e "Firewall is set and active\n"
  elif [ -z "$STAT_IPT_IN$STAT_IPT_FW$STAT_IPSET$STAT_FWS" ]; then echo -e "Firewall is not active; Settings are clean\n"
  else echo -e "Something is not right!\n"; fi
  if [ "$STAT_FWS" ]; then
    echo "- $FWS_FILE exists with correct settings"
  else
    echo "- $FWS_FILE does not exist or does not have settings"
  fi
  if [ "$STAT_IPT_IN" ];
    then echo -e "- INPUT firewall filter is active:\n     iptables $STAT_IPT_IN"
    else echo "- INPUT firewall filter is inactive"
  fi
  if [ "$STAT_IPT_FW" ];
    then echo -e "- FORWARD firewall filter is active:\n     iptables $STAT_IPT_FW"
    else echo "- FORWARD firewall filter inactive"
  fi
  if [ "$STAT_IPSET" ]; then
    echo "- ipset filter is set:"
    echo "$STAT_IPSET" | sed -e 's/^/     /g'
  else
    echo "- ipset filter does not exist"
  fi
}

print_help() {
  echo "Valid Parameters (only one):"
  echo " init        - setup ipset and iptables for this script to work"
  echo " clean       - clean ipset and iptables rules from setup created by this script"
  echo " load_set    - populates ipset set from $IP_LIST after performing init"
  echo " update_only - generates $IP_LIST from servers in $SRC_LIST"
  echo " update      - update_only then load_set [probably what you want to use]"
  echo " status      - display status"
  echo " help        - display this"
}

# Main routine
#[ -w $ROOT_DIR ] || { >&2 echo "$ROOT_DIR not Writable!"; exit 1; }
[ $# = 0 ] && { >&2 echo "No parameter!"; print_help; exit 1; }

if [ "$1" != "_niced" ]; then
  nice -n 15 "$0" _niced "$1"
  exit $?
fi

case $2 in
  "init") init ;;
  "clean") clean ;;
  "load_set") init; set_ipset ;;
  "update_only") update_iplist ;;
  "update") init; update_iplist; set_ipset ;;
  "status") status ;;
  "help") print_help ;;
  *) >&2 echo "Unknown Parameter $2!"; print_help; exit 1 ;;
esac

exit 0
