#!/bin/sh
AEGIS_REPO='https://raw.githubusercontent.com/bolemo/aegis/master'
AEGIS_SCP_URL="$AEGIS_REPO/aegis"
AEGIS_VER_URL="$AEGIS_REPO/version"
AEGIS_SRC_URL="$AEGIS_REPO/aegis.sources"
SELF_PATH="$(pwd -P)"
WGET_PATH="/usr/bin/wget"
RT_MOD="$(cat /module_name)"
ifconfig ppp0 && WAN_IF='ppp0' || WAN_IF="$(/bin/nvram get wan_ifname)"
WAN_IP="$(/usr/sbin/ip -4 addr show $WAN_IF|/usr/bin/awk 'NR==2 {print substr($2,0,index($2, "/")-1);exit}')"

_dlinfo() { # to know how many people are downloading this script
   /usr/bin/curl --interface $WAN_IF -H 'Content-Type: application/json' -H "Authorization: Bearer 1a3mmidk3rg2j1xv6t82ak65up1yht5dambypyh1ze7xhbw7941r" -X POST "https://aegis.goatcounter.com/api/v0/count" \
                 --data '{"no_sessions": true, "hits": [{"path": "install/'$VERS'", "title": "'$VERS'", "ip": "'$WAN_IP'", "ref": "'$RT_MOD$([ "$CHOICE" ] && echo "/ext" || echo "/int")'"}]}' &
} >/dev/null 2>&1

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
if ! test -d $BASE_DIR; then >&2 echo "$BASE_DIR does not exist!"; exit 1; fi

echo "Creating directory (if not already existing): /opt/scripts"
if ! test -d "/opt/scripts"; then mkdir -p "/opt/scripts"; fi
echo "Creating directory (if not already existing): $BASE_DIR/bolemo"
if ! test -d "$BASE_DIR/bolemo"; then mkdir "$BASE_DIR/bolemo"; fi
echo "Creating symlink (if not already existing): /opt/bolemo"
if ! test -L "/opt/bolemo" || ! test -d "/opt/bolemo"; then ln -sfn "$BASE_DIR/bolemo" "/opt/bolemo"; fi
echo "Creating subdirectories in bolemo: scripts, etc"
if ! test -d "$BASE_DIR/bolemo/scripts"; then mkdir "$BASE_DIR/bolemo/scripts"; fi
if ! test -d "$BASE_DIR/bolemo/etc"; then mkdir "$BASE_DIR/bolemo/etc"; fi
if ! test -d "$BASE_DIR/bolemo/www"; then mkdir "$BASE_DIR/bolemo/www"; fi

echo "Downloading and installing aegis..."
VERS="$($WGET_PATH -qO- --no-check-certificate "$AEGIS_VER_URL")"
_dlinfo
if [ "$VERS" ] && $WGET_PATH -qO '/tmp/aegis_dl.tmp' --no-check-certificate "$AEGIS_SCP_URL"; then
  /bin/sed -i 's/^[[:space:]]*// ; 1!{/^#/d;s/#[^"\}'\'']*$//;} ; s/[[:space:]]*$// ; /^$/d ; s/   *\([^"'\'']*\)$/ \1/ ; s/^\(\([^"'\'' ]\+ \)*\) \+/\1/' '/tmp/aegis_dl.tmp'
  /bin/mv '/tmp/aegis_dl.tmp' '/opt/bolemo/scripts/aegis'
  chmod +x "/opt/bolemo/scripts/aegis"
else >&2 echo 'Could not download aegis!'; exit 1
fi

if [ -s "/opt/bolemo/etc/aegis.sources" ]
  then echo "An aegis sources file already exists, keeping it."
  else
    echo "Downloading aegis default sources file..."
    $WGET_PATH -qO- --no-check-certificate "$AEGIS_SRC_URL" >/opt/bolemo/etc/aegis.sources
fi

# symlink
command -v aegis >/dev/null || ln -s /opt/bolemo/scripts/aegis /usr/bin/aegis

# iprange
if ! $ASK; then case "$2" in
  3) ASK_ENT=true;  ASK_INT=true  ;;
  2) ASK_ENT=true;  ASK_INT=false ;;
  1) ASK_ENT=false; ASK_INT=true  ;;
  *) ASK_ENT=false; ASK_INT=false ;;
esac; fi

if command -v iprange >/dev/null; then
  echo 'iprange is installed.'
  _ASK_ROOTFS=false
else
  echo 'iprange is not installed.'
  if command -v /opt/bin/opkg >/dev/null; then
    $ASK && { ask_yn 'It appears you have Entware, do you want to install it through Entware?' && ASK_ENT=true || ASK_ENT=false; }
    if $ASK_ENT; then _ASK_ROOTFS=false
      echo "Downloading and installing iprange..."
      IPRANGE_IPK_URL="$AEGIS_REPO/iprange_1.0.4-1_cortex-a15-3x.ipk"
      if $WGET_PATH -qO '/tmp/iprange.ipk' --no-check-certificate "$IPRANGE_IPK_URL"; then
        /opt/bin/opkg install '/tmp/iprange.ipk'
        /bin/rm -f '/tmp/iprange.ipk'
      else
        >&2 echo 'Could not download iprange!'
      fi
      else _ASK_ROOTFS=true
    fi
  else _ASK_ROOTFS=true
fi
  
  if $_ASK_ROOTFS; then
    case "$RT_MOD" in
      'R7800') IPRANGE_IPK_URL="$AEGIS_REPO/iprange_1.0.4-1_ipq806x.ipk" ;;
      'R9000') IPRANGE_IPK_URL="$AEGIS_REPO/iprange_1.0.4-1_r9000.ipk" ;;
      *) IPRANGE_IPK_URL=;; 
    esac
    if [ "$IPRANGE_IPK_URL" ]; then
      $ASK && { ask_yn 'Do you want to install iprange into router internal memory (/usr/bin)?' && ASK_INT=true || ASK_INT=false; }
      if $ASK_INT; then
        echo "Downloading and installing iprange..."
        if $WGET_PATH -qO '/tmp/iprange.ipk' --no-check-certificate "$IPRANGE_IPK_URL"; then
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
