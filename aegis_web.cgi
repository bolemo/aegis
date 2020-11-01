#!/bin/sh
if [ $QUERY_STRING ]; then
  CMD=$(echo "$QUERY_STRING"|/bin/sed 's/cmd=\([^&]*\).*/\1/')
  ARG=$(echo "$QUERY_STRING"|/bin/sed 's/.*arg=\([^&]*\)/\1/')
else
  CMD=$1
  ARG=$2
fi

aegis_env() {
  # source environment we need from aegis
  eval "$(/opt/bolemo/scripts/aegis _env)"
}

status() {
  aegis_env
  set -- $(/opt/bolemo/scripts/aegis _status)
  eval "_STAT=$1; WAN_IF=$2; TUN_IF=$3; BL_NB=$4; WL_NB=$5"
  _CK=$((_STAT&CK_MASK)); _PB=$(((_STAT>>12)&PB_MASK)); _WN=$(((_STAT>>25)&WN_MASK))
  echo "<h2>Status <span style='color: DarkGrey; font-weight: normal;'>@ $(/bin/date +'%Y-%m-%d %X') (router time)</span></h2>"
  if [ $((_CK+_PB)) -eq 0 ]; then
    echo '<ul id="status" class="off">'
    echo "<li>Aegis is not active; Settings are clean.</li>"
  elif [ $_CK -ne 0 ] && [ $_PB -eq 0 ]; then
    echo '<ul id="status" class="running">'
    echo -n "<li>Aegis is set and active"
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] && echo -n " for WAN interface ($WAN_IF)"
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] && echo -n " and VPN tunnel ($TUN_IF)"
    echo -ne ".</li>\n<li>Filtering $BL_NB IP adresses.</li>"
    [ $((_CK&CK_IPT_WL)) -ne 0 ] && echo "<li>Bypassing $WL_NB IP adresses.</li>"
  else
    echo '<ul id="status" class="error">'
    echo "<li><strong>Something is not right!</strong></li>"
  fi
  echo '</ul>'
  
  if [ $_PB -ne 0 ]; then
    echo '<h3 class="error">Errors</h3>'
    echo '<ul>'
    [ $((_PB&CK_FWS)) -ne 0 ] &&     echo "<li>'firewall-start.sh' is not set properly for $SC_NAME!</li>"
    [ $((_PB&CK_PM)) -ne 0 ] &&      echo "<li>'post-mount.sh' is not set properly for $SC_NAME!</li>"
    [ $((_PB&CK_IPS_BL)) -ne 0 ] &&  echo "<li>ipset: no blocklist is set!</li>"
    [ $((_PB&CK_IPS_WL)) -ne 0 ] &&  echo "<li>ipset: no whitelist is set!</li>"
    [ $((_PB&PB_WG_SNE)) -ne 0 ] &&  echo "<li>ipset: a gateway bypass is set but should not!</li>"
    [ $((_PB&CK_WG_BP)) -ne 0 ] &&   echo "<li>ipset: WAN gateway bypass is not set!</li>"
    [ $((_PB&CK_IPT_CH)) -ne 0 ] &&  echo "<li>iptables: engine chains are not right!</li>"
    [ $((_PB&CK_IPT_WG)) -ne 0 ] &&  echo "<li>iptables: WAN gateway bypass rules are not right!</li>"
    [ $((_PB&CK_IPT_WL)) -ne 0 ] &&  echo "<li>iptables: whitelist rules are not right!</li>"
    [ $((_PB&CK_IPT_TUN)) -ne 0 ] &&      echo "<li>iptables: VPN tunnel IFO rules are corrupted!</li>"
    [ $((_PB&CK_IPT_WAN)) -ne 0 ] &&      echo "<li>iptables: WAN interface IFO rules are corrupted!</li>"
    [ $((_PB&PB_IPT_WAN_MISS)) -ne 0 ] && echo "<li>iptables: WAN interface ($WAN_IF) IFO rules are missing!</li>"
    [ $((_PB&PB_IPT_IFO)) -ne 0 ] &&      echo "<li>iptables: Extra engine IFO rules were found (likely from an old interface)!</li>"
    echo '</ul>'
  fi
  
  if [ $((_CK+_PB)) -ne 0 ] && [ $_WN -ne 0 ]; then
    echo '<h3 class="warning">Warnings</h3>'
    echo '<ul>'
    case "$((_WN&WN_BL_FILE_NTLD))" in
      $WN_BL_FILE_DIFF) echo "<li>blocklist set is different than file.</li>";;
      $WN_BL_FILE_MISS) echo "<li>blocklist is set but file is missing.</li>";;
      $WN_BL_FILE_NTLD) echo "<li>no blocklist is set but file exists.</li>";;
    esac
    case "$((_WN&WN_WL_FILE_NTLD))" in
      $WN_WL_FILE_DIFF) echo "<li>whitelist set is different than file.</li>";;
      $WN_WL_FILE_MISS) echo "<li>whitelist is set but file is missing.</li>";;
      $WN_WL_FILE_NTLD) echo "<li>no whitelist is set but file exists.</li>";;
    esac
    [ $((_WN&WN_TUN_MISS)) -ne 0 ] && echo "<li>iptables: VPN tunnel ($TUN_IF) IFO rules are missing!</li>"
    [ $((_WN&WN_LOG_DIFF)) -ne 0 ] && echo "<li>current logging settings differs from last time engine was started.</li>"
    echo '</ul>'
  fi
  
  echo '<h3 class="more collapsibleList">Detailed status</h3>'
  echo '<input type="checkbox" id="detailed-status" /><label for="detailed-status">Detailed status</label>'
  echo '<ul>'
  echo "<li>Active WAN interface is '$WAN_IF'.</li>"
  [ "$TUN_IF" ] && echo "<li>Active VPN tunnel is '$TUN_IF'.</li>" || echo "<li>no VPN tunnel found.</li>"
  # dates
  [ -e "$BL_FILE" ] && echo "<li>Blocklist generation time: $(/bin/date +'%Y-%m-%d %X' -r $BL_FILE)</li>"
  [ -e "$WL_FILE" ] && echo "<li>Whitelist generation time: $(/bin/date +'%Y-%m-%d %X' -r $WL_FILE)</li>"
  if [ $_CK -ne 0 ]; then
    [ $((_CK&CK_FWS)) -ne 0 ] &&      echo "<li>'firewall-start.sh' is set for $SC_NAME.</li>"
    [ $((_CK&CK_PM)) -ne 0 ] &&       echo "<li>'post-mount.sh' is set for $SC_NAME.</li>"
    [ $((_CK&CK_IPS_BL)) -ne 0 ] &&   echo "<li>ipset: blocklist is set.</li>"
    [ $((_CK&CK_IPS_WL)) -ne 0 ] &&   echo "<li>ipset: whitelist is set.</li>"
    [ $((_CK&CK_WG_IN_BL)) -ne 0 ] && echo "<li>ipset: WAN gateway is in blocklist.</li>"
    [ $((_CK&CK_WG_BP)) -ne 0 ] &&    echo "<li>ipset: WAN gateway bypass is set.</li>"
    [ $((_CK&CK_IPT_CH)) -ne 0 ] &&   echo "<li>iptables: engine chains are set.</li>"
    [ $((_CK&CK_IPT_WG)) -ne 0 ] &&   echo "<li>iptables: WAN gateway bypass rules are set.</li>"
    [ $((_CK&CK_IPT_WL)) -ne 0 ] &&   echo "<li>iptables: whitelist rules are set.</li>"
    [ $((_CK&CK_IPT_LOG)) -ne 0 ] &&  echo "<li>iptables: $SC_NAME logging is on.</li>"
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] &&  echo "<li>iptables: VPN tunnel IFO rules are set.</li>"
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] &&  echo "<li>iptables: WAN interface IFO rules are set.</li>"
  fi
  echo '</ul>'
  
  # Status file
  echo '<h3 class="more collapsibleList">Last Aegis engine launch report</h3>'
  echo '<input type="checkbox" id="launch-report" /><label for="launch-report">Last Aegis engine launch report</label>'
  echo '<ul>'
  if [ -r "$INFO_FILE" ]; then
    read INFO INFO_WAN INFO_TUN<"$INFO_FILE"
    INFO_FROM=$((INFO&INFO_FROM_MASK))
    INFO_IPS=$(((INFO>>2)&INFO_IPS_MASK))
    INFO_IPT=$(((INFO>>10)&INFO_IPT_MASK))
    case "$INFO_FROM" in
      $INFO_FROM_SC) FROM="$SC_NAME script" ;;
      $INFO_FROM_PM) FROM="post-mount.sh" ;;
      $INFO_FROM_FWS) FROM="firewall-start.sh" ;;
    esac
    echo "<li>engine was launched from: $FROM @ $(/bin/date +'%Y-%m-%d %X' -r $INFO_FILE)</li>"
    echo "<li>WAN interface was '$INFO_WAN'.</li>"
    [ "$INFO_TUN" ] && echo "<li>VPN tunnel was '$INFO_TUN'.</li>" || echo "<li>No VPN tunnel was found.</li>"
    case $((INFO_IPS&INFO_IPS_BL_MASK)) in
      0) echo "<li><strong>blocklist file was not found!</strong></li>" ;;
      $INFO_IPS_BL_SAME) echo "<li>ipset: blocklist was already set and identical to file.</li>" ;;
      $INFO_IPS_BL_MISS) echo "<li>ipset: blocklist file was not found! The one already set was kept.</li>" ;;
      $INFO_IPS_BL_LOAD) echo "<li>ipset: blocklist was set from file.</li>" ;;
    esac
    case $((INFO_IPS&INFO_IPS_WL_MASK)) in
      0) echo "<li>no whitelist file was found.</li>" ;;
      $((INFO_IPS_WL_SAME+INFO_IPS_WL_KEEP))) echo "<li>ipset: whitelist was already set and identical to file.</li>" ;;
      $INFO_IPS_WL_KEEP) echo "<li>ipset: whitelist was kept.</li>" ;;
      $INFO_IPS_WL_LOAD) echo "<li>ipset: whitelist was set from file.</li>" ;;
      $INFO_IPS_WL_SWAP) echo "<li>ipset: whitelist was updated from file.</li>" ;;
      $INFO_IPS_WL_DEL) echo "<li>ipset: whitelist was unset.</li>" ;;
    esac
    case $((INFO_IPS&INFO_IPS_WG_MASK)) in
      0) echo "<li>WAN gateway was not in blocklist set and therefore was not bypassed.</li>" ;;
      $INFO_IPS_WG_ADD) echo "<li>ipset: WAN gateway was in blocklist and was bypassed.</li>" ;;
      $INFO_IPS_WG_KEEP) echo "<li>ipset: WAN gateway bypass was already properly set.</li>" ;;
      $INFO_IPS_WG_DEL) echo "<li>ipset: WAN gateway bypass was unset.</li>" ;;
    esac
    if [ $((INFO_IPT & INFO_IPT_SRC_KEEP)) -eq 0 ]
      then echo "<li>iptables: engine inbound chain was set.</li>"
      else echo "<li>iptables: engine inbound chain was already set.</li>"
    fi
    if [ $((INFO_IPT & INFO_IPT_DST_KEEP)) -eq 0 ]
      then echo "<li>iptables: engine outbound chain was set.</li>"
      else echo "<li>iptables: engine outbound chain was already set.</li>"
    fi
    if [ $((INFO_IPT & INFO_IPT_WG)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_WG_SRC_NEW)) -ne 0 ]
        then echo "<li>iptables: inbound WAN gateway bypass rules were set.</li>"
        else echo "<li>iptables: inbound WAN gateway bypass rules were kept.</li>"
      fi
      if [ $((INFO_IPT & INFO_IPT_WG_DST_NEW)) -ne 0 ]
        then echo "<li>iptables: outbound WAN gateway bypass rules were set.</li>"
        else echo "<li>iptables: outbound WAN gateway bypass rules were kept.</li>"
      fi
    fi
    if [ $((INFO_IPT & INFO_IPT_WL)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_WL_SRC_NEW)) -ne 0 ]
        then echo "<li>iptables: inbound whitelist rules were set.</li>"
        else echo "<li>iptables: inbound whitelist rules were kept.</li>"
      fi
      if [ $((INFO_IPT & INFO_IPT_WL_DST_NEW)) -ne 0 ]
        then echo "<li>iptables: outbound whitelist rules were set.</li>"
        else echo "<li>iptables: outbound whitelist rules were kept.</li>"
      fi
    fi
    if [ $((INFO_IPT & INFO_IPT_LOG)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_LOG_SRC_NEW)) -ne 0 ]
        then echo "<li>iptables: inbound logging rules were set.</li>"
        else echo "<li>iptables: inbound logging rules were kept.</li>"
      fi
      if [ $((INFO_IPT & INFO_IPT_LOG_DST_NEW)) -ne 0 ]
        then echo "<li>iptables: outbound logging rules were set.</li>"
        else echo "<li>iptables: outbound logging rules were kept.</li>"
      fi
    fi
    
    [ $((INFO_IPT & INFO_IPT_IFO_PBM)) -ne 0 ] && echo "<li>iptables: some irrelevant IFO rules had to be removed.</li>"
    if [ $((INFO_IPT & INFO_IPT_WAN_PBM)) -eq $INFO_IPT_WAN_PBM ]; then echo "<li>iptables: WAN interface IFO rules had to be reset.</li>"
    elif [ $((INFO_IPT & INFO_IPT_WAN_NEW)) -ne 0 ]; then echo "<li>iptables: WAN interface IFO rules were set.</li>"
    elif [ $((INFO_IPT & INFO_IPT_WAN_KEEP)) -ne 0 ]; then echo "<li>iptables: WAN interface IFO rules were kept.</li>"
    fi
    if [ $((INFO_IPT & INFO_IPT_TUN_PBM)) -eq $INFO_IPT_TUN_PBM ]; then echo "<li>iptables: VPN tunnel IFO rules had to be reset.</li>"
    elif [ $((INFO_IPT & INFO_IPT_TUN_NEW)) -ne 0 ]; then echo "<li>iptables: VPN tunnel IFO rules were set.</li>"
    elif [ $((INFO_IPT & INFO_IPT_TUN_KEEP)) -ne 0 ]; then echo "<li>iptables: VPN tunnel IFO rules were kept.</li>"
    fi
  else
    echo "<li>No status file found.</li>"
  fi
  echo '</ul>'
}

info() {
  aegis_env
  _JSON="{\"version\":\"$SC_VERS\""
  [ "$EXT_DRIVE" ] && _JSON="$_JSON, \"location\":\"external\"" || _JSON="$_JSON, \"location\":\"internal\""
  SC_LAST_VERS="$(last_avail_version)";
  if [ "$SC_LAST_VERS" ]; then
    _LOC_VERS=$(echo "$SC_VERS"|/bin/sed 's/[^[:digit:]]//g')
    _REM_VERS=$(echo "$SC_LAST_VERS"|/bin/sed 's/[^[:digit:]]//g')
    if [ $_LOC_VERS -eq $_REM_VERS ]; then _VSTAT=0
    elif [ $_LOC_VERS -lt $_REM_VERS ]; then _VSTAT=1
    else _VSTAT=2
    fi
  else _VSTAT=3
  fi
  _JSON="$_JSON, \"newVersion\":\"$SC_LAST_VERS\", \"versionStatus\":$_VSTAT}"
  echo "$_JSON"
}

command() {
  [ "$(echo -n "$ARG"|/usr/bin/cut -d: -f2)" = 'on' ] && _LOG='-log=on' || _LOG='-log=off'
  case $ARG in
    restart*) _CMD="aegis _restart $_LOG" ;;
    update*) _CMD="aegis _update $_LOG" ;;
    'stop-upgrade-restart') _CMD="aegis _clean"
      [ "$(nvram get aegis_log)" = "1" ] && ARG="$ARG:on" || ARG="$ARG:off"
      ;;
    stop*) _CMD="aegis _clean" ;;
    upgrade*) _CMD="aegis _upgrade" ;;
  esac
  [ -z "${ARG##*-*}" ] && _ARG2="${ARG#*-}"
  eval "/opt/bolemo/scripts/$_CMD"|/bin/sed "s/$(printf '\r')//g ; s/[[:cntrl:]]\[\([^m]*\)m//g ; /^[[:space:]]*$/d"
  if [ $? = 0 ]; then echo "Success!"; else echo "A problem was encountered."; exit 1; fi;
  if [ $_ARG2 ]; then ARG="$_ARG2"; _ARG2=''; command; fi;
}

_nameForIp() {
  while read -r LINE; do
    if [ -z "${LINE##$1*}" ]; then echo "${LINE##* }<small> ($1)</small>"; return; break; fi;
  done < /tmp/dhcpd_hostlist
  while read -r LINE; do
    if [ -z "${LINE##$1*}" ]; then echo "${LINE##* }<small> ($1)</small>"; return; break; fi;
  done < /tmp/hosts
  echo "$1"
}

# _getLog key name in syslog, max lines,  start timestamp, wan interface name, vpn interface name
_getLog() {
#  _WIP="$(nvram get wan_ipaddr)"
  _RNM="$(nvram get Device_name)"
  _LOG=''
  _KEY=$1
  _MAX=$2
  [ $3 = 0 ] && _BT=$(( $(/bin/date +%s) - $(cat /proc/uptime|/usr/bin/cut -d. -f1) )) || _BT=$3
  _ST=$4
  _WIF=$5
  _TIF=$6
  _MD5=$7
  _CKMD5=$_MD5
#  /bin/date -d 0 -D %s>/dev/null 2>&1 && _DATE_D=1 || _DATE_D=''
  /bin/grep -F $_KEY /var/log/log-message | /usr/bin/tail -n$_MAX | { IFS=;while read -r LINE; do
    _TS=$(echo $LINE|/usr/bin/cut -d: -f1)
    [ $_TS -lt $_ST ] && continue
    if [ $_TS -eq $_ST ] && [ $_CKMD5 ]; then
       LINE_MD5=$(echo $LINE|/usr/bin/md5sum -)
       [ -z "${LINE_MD5##*$_MD5*}" ] && _CKMD5=''
       continue
    fi
    _LT=$((_BT+_TS))
    _PT="<log-ts>$(/bin/date -d $_LT -D %s +"%F %T")</log-ts>" # || _PT="<log-ts>$(/bin/date -d @$_LT +"%F %T")</log-ts>"
    _1=${LINE#* SRC=}; _SRC=${_1%% *}
    _1=${LINE#* DST=}; _DST=${_1%% *}
    _1=${LINE#* PROTO=}; _PROTO=${_1%% *}; [ $_PROTO = 47 ] && _PROTO='GRE'
    _1=${LINE#* SPT=}; [ "$_1" = "$LINE" ] && _SPT='' || _SPT="<log-pt>${_1%% *}</log-pt>"
    _1=${LINE#* DPT=}; [ "$_1" = "$LINE" ] && _DPT='' || _DPT="<log-pt>${_1%% *}</log-pt>"

    if [ -z "${LINE##* OUT= *}" ]
      then [ "$_DST" = '255.255.255.255' ] && _DST="<i>BROADCAST</i><small> ($_DST)</small>" || _DST="$_RNM<small> ($_DST)</small>"
      else _DST="$(_nameForIp $_DST)"; [ -z "${LINE##* IN= *}" ] && _SRC="$_RNM<small> ($_SRC)</small>" || _SRC="$(_nameForIp $_SRC)"
    fi

    case $LINE in
      *"IN=$_WIF"*)
        _LOG="<p class='new incoming wan'>$_PT Blocked <log-if>WAN</log-if> <log-dir>incoming</log-dir> $_PROTO packet from remote: <log-rip>$_SRC</log-rip>$_SPT, to local: <log-lip>$_DST</log-lip>$_DPT</p>$_LOG"
        ;;
      *"OUT=$_WIF"*)
        _LOG="<p class='new outgoing wan'>$_PT Blocked <log-if>WAN</log-if> <log-dir>outgoing</log-dir> $_PROTO packet to remote: <log-rip>$_DST</log-rip>$_DPT, from local: <log-lip>$_SRC</log-lip>$_SPT</p>$_LOG"
        ;;
      *"IN=$_TIF"*)
        _LOG="<p class='new incoming vpn'>$_PT Blocked <log-if>VPN</log-if> <log-dir>incoming</log-dir> $_PROTO packet from remote: <log-rip>$_SRC</log-rip>$_SPT, to local: <log-lip>$_DST</log-lip>$_DPT</p>$_LOG"
        ;;
      *"OUT=$_TIF"*)
        _LOG="<p class='new outgoing vpn'>$_PT Blocked <log-if>VPN</log-if> <log-dir>outgoing</log-dir> $_PROTO packet to remote: <log-rip>$_DST</log-rip>$_DPT, from local: <log-lip>$_SEC</log-lip>$_SPT</p>$_LOG"
        ;;
    esac
    _LINE=$LINE
  done
  [ "$_TIF" ] || _TIF="''"
  [ "$_LINE" ] && _MD5="$(echo $_LINE|/usr/bin/md5sum -|/usr/bin/cut -d' ' -f1)"
  echo "$_KEY $_MAX $_BT $_TS $_WIF $_TIF $_MD5">/tmp/aegis_web
  echo "$_LOG"
  }
}

log() {
  aegis_env
  case $ARG in
    ''|*[!0-9]*) LEN=100 ;;
    *) if [ $ARG -lt 1 ]; then LEN=1
       elif [ $ARG -gt 300 ]; then LEN=300
       else LEN=$ARG
       fi ;;
  esac
  _getLog $SC_NAME $LEN 0 0 $WAN_IF $TUN_IF
}

refreshLog() {
  [ -r /tmp/aegis_web ] && _getLog $(cat /tmp/aegis_web) || log
}

# MAIN
case $CMD in
  info) info;;
  status) status;;
  command) command;;
  log) log;;
  refresh_log) refreshLog;;
esac
exit 0
