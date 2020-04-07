#! /bin/sh

SC_NAME="firewall-blocklist"
IPSET_NAME="blocklist"
IPSET_TMP="${IPSET_NAME}_tmp"
ROOT_DIR="/opt/bolemo"
SRC_LIST="$ROOT_DIR/etc/$SC_NAME.sources"
IP_LIST="$ROOT_DIR/etc/$SC_NAME.netset"
TMP_FILE="$IP_LIST.tmp"
FWS_FILE="/opt/scripts/firewall-start-blocklist.sh"

check_firewall_start() {
  [ -x $FWS_FILE ] || return 1
  [ "$(sed 's/[[:space:]]\+/ /g' $FWS_FILE | grep -- "iptables -I INPUT -i brwan -m set --match-set $IPSET_NAME src -j DROP")" ] || return 1
  [ "$(sed 's/[[:space:]]\+/ /g' $FWS_FILE | grep -- "iptables -I FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP")" ] || return 1
  return 0
}

check() {
  [ -r "$SRC_LIST" ] && echo "All seems ok" || echo "$SRC_LIST is missing!"
}

init() {
  ipset -q destroy $IPSET_TMP
  ipset -! create $IPSET_NAME hash:net
  if ! check_firewall_start; then
    { echo "iptables -I INPUT   -i brwan -m set --match-set $IPSET_NAME src -j DROP";
      echo "iptables -I FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP";
    } > $FWS_FILE
    chmod +x $FWS_FILE
  fi
  /usr/sbin/net-wall restart > /dev/null
}

clean() {
  [ -e $FWS_FILE ] && rm $FWS_FILE
#  iptables -D INPUT   -i brwan -m set --match-set $IPSET_NAME src -j DROP
#  iptables -D FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP
  /usr/sbin/net-wall restart > /dev/null
  ipset -q destroy $IPSET_NAME
  ipset -q destroy $IPSET_TMP
  [ -e $TMP_FILE ] && rm $TMP_FILE
}

set_ipset() {
  [ -r $IP_LIST ] || { >&2 echo "$IP_LIST not readable!"; return; }

  ipset -! create $IPSET_TMP hash:net
  ipset flush $IPSET_TMP > /dev/null
  if [ $VERBOSE ]; then
    COUNT=0
    MAX="$(wc -l < $IP_LIST)"
    echo "Building ipset blocklist ($MAX entries)..."
    while read -r IP; do
      ipset add $IPSET_TMP "$IP"
      COUNT=$((COUNT+1))
      PROG=$((100*COUNT/MAX))
      [ $((PROG%1)) -eq 0 ] && echo -ne " - Progression: $PROG%  \r"
    done < $IP_LIST
    echo -e "\n Completed"
  else
    while read -r IP; do ipset add $IPSET_TMP "$IP"; done < $IP_LIST
  fi
  ipset swap $IPSET_NAME $IPSET_TMP
  ipset destroy $IPSET_TMP
}

update_iplist() {
  [ -r $SRC_LIST ] || { >&2 echo "$SRC_LIST not readable!"; return; }

  :>"$TMP_FILE"
  # Process each source url
  [ $VERBOSE ] && echo "Downloading lists defined in $SRC_LIST"
  [ $VERBOSE ] && WGET_OPTS='-qO- --show-progress' || WGET_OPTS='-qO-'
  grep -v "^[[:space:]*\#]" "$SRC_LIST" | while read -r URL; do
    [ $VERBOSE ] && echo "$URL"
    wget $WGET_OPTS "$URL" | grep '^[0-9]' | sed -e 's/;.*//' >> "$TMP_FILE"
  done
  [ $VERBOSE ] && echo "Removing duplicates..."
  sort "$TMP_FILE" | uniq > "$IP_LIST"
  rm "$TMP_FILE"
  [ $VERBOSE ] && echo "Done"
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
  echo "Valid commands (only one):"
  echo " init        - setup ipset and iptables for this script to work"
  echo " clean       - clean ipset and iptables rules from setup created by this script"
  echo " load_set    - populates ipset set from $IP_LIST after performing init"
  echo " update_only - generates $IP_LIST from servers in $SRC_LIST"
  echo " update      - update_only then load_set [probably what you want to use]"
  echo " status      - display status"
  echo " help        - display this"
  echo "Options:"
  echo " -v          - verbose mode"
}

# Main routine
[ $# = 0 ] && { >&2 echo "No parameter!"; print_help; exit 1; }

if [ "$1" != "_niced" ]; then
  if [ "$1" = "-v" ]; then
    [ $# = 1 ] && { >&2 echo "No parameter!"; print_help; exit 1; }
    PARAM="$2"; VERB="_verbose"
  elif [ $# = 2 ] && [ "$2" = "-v" ]; then
    PARAM="$1"; VERB="_verbose"
  else
    PARAM="$1"; VERB=''
  fi
  SC_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
  nice -n 15 "$SC_PATH/$SC_NAME.sh" _niced "$PARAM" "$VERB"
  exit $?
fi

VERBOSE=$3
[ $VERBOSE ] && echo "Verbose mode"

case $2 in
  "init") init; [ $VERBOSE ] && status ;;
  "clean") clean; [ $VERBOSE ] && status ;;
  "load_set") init; set_ipset; [ $VERBOSE ] && status ;;
  "update_only") update_iplist ;;
  "update") init; update_iplist; set_ipset; [ $VERBOSE ] && status ;;
  "status") status ;;
  "help") print_help ;;
  *) >&2 echo "Unknown Parameter $2!"; print_help; exit 1 ;;
esac

exit 0
