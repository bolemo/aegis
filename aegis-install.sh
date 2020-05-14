#!/bin/sh
AEGIS_REPO='https://raw.githubusercontent.com/bolemo/aegis/master'
AEGIS_SCP_URL="$AEGIS_REPO/aegis"
AEGIS_SRC_URL="$AEGIS_REPO/aegis.sources"
SELF_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

ask_yn() {
  echo -ne "$1 [y/n] "
  case "$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)" in
    Y|y|yes|Yes|YES) return 0 ;;
    *) return 1  ;;
  esac
}

ask_install_loc() {
  A=''; until [ "$A" = 'e' ] || [ "$A" = 'E' ] || [ "$A" = 'i' ] || [ "$A" = 'I' ]; do
    echo -ne "Where do you want to install aegis?\n  e - external drive ($BASE_DIR)\n  i - router internal memory (rootfs)\nYour choice [e/i]: "
    A="$(i=0;while [ $i -lt 2 ];do i=$((i+1));read -p "" yn </dev/tty;[ -n "$yn" ] && echo "$yn" && break;done)"
  done
  echo $A
}

if echo "$SELF_PATH" | grep -q '^/tmp/mnt/.*/'; then
  # We are on external drive
  BASE_DIR="$( echo "$SELF_PATH" | sed "s|\(/tmp/mnt/.*\)/.*|\1|")"
  case ask_install_loc in
    i|I) BASE_DIR="/root"; echo "aegis will be installed on internal memory $BASE_DIR" ;;
    *) echo "aegis will be installed on external device $BASE_DIR" ;;
  esac
elif echo "$SELF_PATH" | grep -q '^/root/'; then
  BASE_DIR="/root"
  echo "aegis will be installed on internal memory $BASE_DIR"
else
  >&2 echo "aegis-install.sh is not in the right place!"; exit 1
fi
[ -d $BASE_DIR ] || { >&2 echo "$BASE_DIR does not exist!"; exit 1; }

echo "Creating directory (if not already existing): $BASE_DIR/bolemo"
[ -d "$BASE_DIR/bolemo" ] || mkdir "$BASE_DIR/bolemo"
echo "Creating symlink (if not already existing): /opt/bolemo"
[ -L "/opt/bolemo" ] && [ -d "/opt/bolemo" ] || ln -s "$BASE_DIR/bolemo" "/opt/bolemo"
echo "Creating subdirectories in bolemo: scripts, etc"
[ -d "$BASE_DIR/bolemo/scripts" ] || mkdir "$BASE_DIR/bolemo/scripts"
[ -d "$BASE_DIR/bolemo/etc" ] || mkdir "$BASE_DIR/bolemo/etc"

echo "Downloading and installing aegis..."
if wget -qO "$BASE_DIR/bolemo/scripts/" "$AEGIS_SCP_URL"
  then chmod +x "$BASE_DIR/bolemo/scripts/aegis"
  else >&2 echo 'Could not download aegis!'; exit 1
fi

if [ -e "$BASE_DIR/bolemo/etc/aegis.sources" ]
  then echo "An aegis sources file already exists, keeping it."
  else
    echo "Downloading aegis default sources file..."
    wget -qO "$BASE_DIR/bolemo/etc/" "$AEGIS_SRC_URL"
fi

# iprange
if command -v iprange>/dev/null; then
  echo 'iprange is installed.'
else
  echo 'iprange is not installed.'
  if command -v /opt/bin/opkg && [ "$(/opt/bin/opkg list iprange)" ]; then
    if ask_yn 'It appears you have Entware, do you want to install it through Entware?'
      then /opt/bin/opkg update; /opt/bin/opkg install iprange
      else _ASK_ROOTFS='y'
    fi
  else _ASK_ROOTFS='y'
  fi
  
  if [ $_ASK_ROOTFS ]; then
    case "$(/bin/uname -p)" in
      'IPQ8065') IPRANGE_IPK_URL="$AEGIS_REPO/iprange_1.0.4-1_ipq806x.ipk" ;;
      'unknown') if [ "$(/bin/uname -n)" = 'R9000' ]
                   then IPRANGE_IPK="$SELF_PATH/iprange_1.0.4-1_r9000.ipk"
                 elif ask_yn 'Can you confirm you have a R9000 router?'
                   then IPRANGE_IPK_URL="$AEGIS_REPO/iprange_1.0.4-1_r9000.ipk"
                 else IPRANGE_IPK_URL=''
                 fi ;;
      *) IPRANGE_IPK_URL='' ;; 
    esac
    if [ -x "$IPRANGE_IPK_URL" ]; then
      if ask_yn 'Do you want to install iprange into router internal memory (/usr/bin)?'; then
        echo "Downloading and installing iprange..."
        if wget -qO '/tmp/iprange.ipk' "$IPRANGE_IPK_URL"; then
          /bin/opkg install '/tmp/iprange.ipk'
          rm -f '/tmp/iprange.ipk'
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

if ask_yn 'Remove install script?'
  then echo 'Removing install script...'; rm -f "$0"
  else echo 'Keeping install script'
fi

echo "Done!"
