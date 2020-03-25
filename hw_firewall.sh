#! /bin/sh

SC_NAME="hw_firewall"
IPSET_NAME="hw_firewall"
IPSET_TMP="${IPSET_NAME}_tmp"
BASE_DIR="/mnt/optware"
ROOT_DIR="$BASE_DIR/$SC_NAME"
SRC_LIST="$ROOT_DIR/$SC_NAME.sources"
IP_LIST="$ROOT_DIR/$SC_NAME.netset"
TMP_FILE="$IP_LIST.tmp"

init() {
  ipset -! create $IPSET_NAME hash:net
  if [ "$(iptables -S INPUT | grep -- "-A INPUT -i brwan -m set --match-set $IPSET_NAME src -j DROP")" = '' ]; then
    iptables -I INPUT   -i brwan -m set --match-set $IPSET_NAME src -j DROP
  fi
  if [ "$(iptables -S FORWARD | grep -- "-A FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP")" = '' ]; then
    iptables -I FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP
  fi
}

clean() {
  iptables -D INPUT   -i brwan -m set --match-set $IPSET_NAME src -j DROP
  iptables -D FORWARD -i brwan -m set --match-set $IPSET_NAME src -j DROP
  ipset -q destroy $IPSET_NAME
  ipset -q destroy $IPSET_TMP
  [ -r $TMP_FILE ] && rm $TMP_FILE
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

print_help() {
  echo "Valid Parameters (only one):"
  echo " init        - setup ipset and iptables for this script to work"
  echo " clean       - clean ipset and iptables rules from setup created by this script"
  echo " load_set    - populates ipset set from $IP_LIST after performing init"
  echo " update_only - generates $IP_LIST from servers in $SRC_LIST"
  echo " update      - update_only then load_set [probably what you want to use]"
  echo " help        - display this"
}

# Main routine
[ -w $ROOT_DIR ] || { >&2 echo "$ROOT_DIR not Writable!"; exit 1; }
[ $# = 0 ] && { >&2 echo "No parameter!"; print_help; exit 1; }

if [ "$1" != "_niced" ]; then
  nice -n 15 "$0" _niced "$1"
  exit $?
fi

case $2 in
  "init") init ;;
  "clean") clean ;;
  "reload") init; set_ipset ;;
  "update_only") update_iplist ;;
  "update") init; update_iplist; set_ipset ;;
  "help") print_help ;;
  *) >&2 echo "Unknown Parameter $2!"; print_help; exit 1 ;;
esac

exit 0
