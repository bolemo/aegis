#!/bin/sh
BASE_DIR="/mnt/optware"
[ -d $BASE_DIR ] || { >&2 echo "$BASE_DIR does not exist!"; exit 1; }
cd $BASE_DIR
[ -d "$BASE_DIR/bolemo" ] || mkdir "$BASE_DIR/bolemo"
[ -d "$BASE_DIR/bolemo/scripts" ] || mkdir "$BASE_DIR/bolemo/scripts"
[ -d "$BASE_DIR/bolemo/etc" ] || mkdir "$BASE_DIR/bolemo/etc"
wget -O "$BASE_DIR/bolemo/scripts/firewall-blocklist.sh" "https://raw.githubusercontent.com/bolemo/firewall-blocklist/master/firewall-blocklist.sh"
wget -O "$BASE_DIR/bolemo/etc/firewall-blocklist.sources" "https://raw.githubusercontent.com/bolemo/firewall-blocklist/master/firewall-blocklist.sources"
chmod -x "$BASE_DIR/bolemo/scripts/firewall-blocklist.sh"
