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
\cp -n "$SELF_PATH/firewall-blocklist.sources" "$BASE_DIR/bolemo/etc/"
chmod +x "$BASE_DIR/bolemo/scripts/firewall-blocklist"
echo "Done!"
if command -v iprange; then
  echo 'iprange is installed.'
else
  case "$(/bin/uname -p)" in
    'IPQ8065') IPRANGE_IPK="$SELF_PATH/iprange_1.0.4-1_ipq806x.ipk" ;;
    'R9000') IPRANGE_IPK="$SELF_PATH/iprange_1.0.4-1_r9000.ipk" ;;
    *) IPRANGE_IPK='' ;; 
  esac
  if [ -x "$IPRANGE_IPK" ]; then
    echo -ne "iprange does not seem to be installed.\nDo you want to install iprange into internal flash (/usr/bin)? [y/n] "
    case "$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)" in
      Y|y|yes|Yes|YES) echo "Installing iprange..."; /bin/opkg install "$IPRANGE_IPK" ;;
      *) echo 'Skipping installation of iprange' ;;
    esac
  else
    echo 'The iprange version offered by this installer are not supported on this device, if you want to install iprange, you need to do it through Entware.'
  fi
fi
echo -ne "Remove install files? [y/n] "
case "$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)" in
  Y|y|yes|Yes|YES) echo "Removing install files..."; rm -rf "$SELF_PATH" ;;
  *) echo 'Keeping installation files'  ;;
esac
echo "Done!"
