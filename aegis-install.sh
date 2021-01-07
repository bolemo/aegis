#!/bin/sh
AEGIS_REPO='https://raw.githubusercontent.com/bolemo/aegis/master'
AEGIS_SCP_URL="$AEGIS_REPO/aegis"
AEGIS_VER_URL="$AEGIS_REPO/version"
AEGIS_SRC_URL="$AEGIS_REPO/aegis.sources"
SELF_PATH="$(pwd -P)"
WGET_PATH="/usr/bin/wget"

ask_yn() {
  echo -ne "$1 [y/n] "
  case "$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)" in
    Y|y|yes|Yes|YES) return 0 ;;
    *) return 1  ;;
  esac
}

[ -z ${1+x} ] && ASK=true || ASK=false

if $ASK; then
  i=1; for var in $(ls /tmp/mnt); do eval var$i="'$var'"; i=$((i+1)); done;
  until [ "$A" ] && $(echo "$A" | grep -qE '^[0-9]?$') && [ "$A" -ge 0 ] && [ "$A" -lt "$i" ]; do
    echo "Where do you want to install aegis?"
    echo '  0 - router internal memory (rootfs)'
    j=1; while [ "$j" -ne "$i" ]; do
      echo "  $j - external drive: /mnt/$(eval echo "\$var$j")"
      j=$((j+1))
    done
    echo "  c - cancel installation"
    echo -n 'Your choice: '
    A="$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)"
    [ "$A" = 'c' ] && exit 0
  done;
  CHOICE="$(eval echo "\$var$A")";
else CHOICE="$1"; fi

if [ "$CHOICE" ]; then
  BASE_DIR="/tmp/mnt/$CHOICE"
  echo "aegis will be installed on external drive $BASE_DIR"
else
  BASE_DIR="/root"
  echo "aegis will be installed on internal memory $BASE_DIR"
fi
[ -d $BASE_DIR ] || { >&2 echo "$BASE_DIR does not exist!"; exit 1; }

echo "Creating directory (if not already existing): /opt/scripts"
[ -d "/opt/scripts" ] || mkdir -p "/opt/scripts"
echo "Creating directory (if not already existing): $BASE_DIR/bolemo"
[ -d "$BASE_DIR/bolemo" ] || mkdir "$BASE_DIR/bolemo"
echo "Creating symlink (if not already existing): /opt/bolemo"
[ -L "/opt/bolemo" ] && [ -d "/opt/bolemo" ] || ln -sfn "$BASE_DIR/bolemo" "/opt/bolemo"
echo "Creating subdirectories in bolemo: scripts, etc"
[ -d "$BASE_DIR/bolemo/scripts" ] || mkdir "$BASE_DIR/bolemo/scripts"
[ -d "$BASE_DIR/bolemo/etc" ] || mkdir "$BASE_DIR/bolemo/etc"
[ -d "$BASE_DIR/bolemo/www" ] || mkdir "$BASE_DIR/bolemo/www"

echo "Downloading and installing aegis..."
VERS="$($WGET_PATH -qO- "$AEGIS_VER_URL")"
if [ "$VERS" ] && $WGET_PATH -qO '/tmp/aegis_dl.tmp' "$AEGIS_SCP_URL"; then
  /bin/sed -i 's/^[[:space:]]*// ; 1!{/^#/d;s/#[^"\}'\'']*$//;} ; s/[[:space:]]*$// ; /^$/d ; s/   *\([^"'\'']*\)$/ \1/ ; s/^\(\([^"'\'' ]\+ \)*\) \+/\1/' '/tmp/aegis_dl.tmp'
  /bin/mv '/tmp/aegis_dl.tmp' '/opt/bolemo/scripts/aegis'
  chmod +x "/opt/bolemo/scripts/aegis"
else >&2 echo 'Could not download aegis!'; exit 1
fi

if [ -e "/opt/bolemo/etc/aegis.sources" ]
  then echo "An aegis sources file already exists, keeping it."
  else
    echo "Downloading aegis default sources file..."
    wget -qO "/opt/bolemo/etc/aegis.sources" "$AEGIS_SRC_URL"
fi

# symlink
command -v aegis > /dev/null || ln -s /opt/bolemo/scripts/aegis /usr/bin/aegis

# iprange
if ! $ASK; then case "$2" in
  3) ASK_ENT=true;  ASK_INT=true  ;;
  2) ASK_ENT=true;  ASK_INT=false ;;
  1) ASK_ENT=false; ASK_INT=true  ;;
  *) ASK_ENT=false; ASK_INT=false ;;
esac; fi

if command -v iprange>/dev/null; then
  echo 'iprange is installed.'
  _ASK_ROOTFS=false
else
  echo 'iprange is not installed.'
  if command -v /opt/bin/opkg && [ "$(/opt/bin/opkg list iprange)" ]; then
    $ASK && { ask_yn 'It appears you have Entware, do you want to install it through Entware?' && ASK_ENT=true || ASK_ENT=false; }
    if $ASK_ENT
      then /opt/bin/opkg update; /opt/bin/opkg install iprange; _ASK_ROOTFS=false
      else _ASK_ROOTFS=true
    fi
  else _ASK_ROOTFS=true
fi
  
  if $_ASK_ROOTFS; then
    case "$(cat /module_name)" in
      'R7800') IPRANGE_IPK_URL="$AEGIS_REPO/iprange_1.0.4-1_ipq806x.ipk" ;;
      'R9000') IPRANGE_IPK_URL="$AEGIS_REPO/iprange_1.0.4-1_r9000.ipk" ;;
      *) IPRANGE_IPK_URL=;; 
    esac
    if [ "$IPRANGE_IPK_URL" ]; then
      $ASK && { ask_yn 'Do you want to install iprange into router internal memory (/usr/bin)?' && ASK_INT=true || ASK_INT=false; }
      if $ASK_INT; then
        echo "Downloading and installing iprange..."
        if $WGET_PATH -qO '/tmp/iprange.ipk' "$IPRANGE_IPK_URL"; then
          /bin/opkg install '/tmp/iprange.ipk'
          /bin/rm -f '/tmp/iprange.ipk'
        else
          >&2 echo 'Could not download iprange!'
        fi
      else
        echo 'Skipping installation of iprange'
      fi
    else
      echo 'The iprange versions available from this installer are not supported on this device.'
    fi
  fi
fi
echo "Done!"
exit 0
