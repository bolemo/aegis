#!/bin/sh
SELF_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BASE_DIR="$( echo "$SELF_PATH" | sed "s|\(/tmp/mnt/.*\)/.*|\1|")"
echo "Installing on device $BASE_DIR"
[ -d $BASE_DIR ] || { >&2 echo "$BASE_DIR does not exist!"; exit 1; }
echo "Creating directory (if not already existing): $BASE_DIR/bolemo"
[ -d "$BASE_DIR/bolemo" ] || mkdir "$BASE_DIR/bolemo"
echo "Creating symlink (if not already existing): /opt/bolemo"
[ -L "/opt/bolemo" ] && [ -d "/opt/bolemo" ] || ln -s "$BASE_DIR/bolemo" "/opt/bolemo"
echo "Creating subdirectories in bolemo: scripts, etc"
[ -d "$BASE_DIR/bolemo/scripts" ] || mkdir "$BASE_DIR/bolemo/scripts"
[ -d "$BASE_DIR/bolemo/etc" ] || mkdir "$BASE_DIR/bolemo/etc"
echo "Installing firewall-blocklist files"
\cp "$SELF_PATH/firewall-blocklist" "$BASE_DIR/bolemo/scripts/"
cp -i "$SELF_PATH/firewall-blocklist.sources" "$BASE_DIR/bolemo/etc/"
chmod +x "$BASE_DIR/bolemo/scripts/firewall-blocklist"
echo "Done!"
if command -v iprange; then echo 'iprange is installed.'; exit 0; fi
[ "$(/bin/uname -p)" = 'IPQ8065' ] || { echo 'This is not a R7800, if you want to install iprange, you need to do it through Entware.'; exit 0; }
echo -ne "iprange does not seem to be installed.\nDo you want to install iprange into internal flash (/usr/bin)? [y/n] "
case "$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)" in
  Y|y|yes|Yes|YES) echo "Installing iprange..."; /bin/opkg install "$SELF_PATH/iprange_1.0.4-1_ipq806x.ipk" ;;
  *) echo 'Skipping installation of iprange' ;;
esac
echo -ne "Remove install files? [y/n] "
case "$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)" in
  Y|y|yes|Yes|YES) echo "Removing install files..."; rm -rf "$SELF_PATH" ;;
  *) echo 'Keeping installation files'  ;;
esac
echo "Done!"
