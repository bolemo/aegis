#!/bin/sh
wcAEGIS_BIN='/opt/bolemo/scripts/aegis'
wcPRT_URL='https://raw.githubusercontent.com/bolemo/aegis/master/data/net-protocols.csv'
wcDAT_DIR='/www/bolemo/aegis_data'; wcPRT_PTH="$wcDAT_DIR/net-protocols.csv"
wcUCI='/sbin/uci -qc /opt/bolemo/etc/config'

if [ $QUERY_STRING ]; then
  CMD=$(echo "$QUERY_STRING"|/bin/sed 's/cmd=\([^&]*\).*/\1/')
  ARG=$(echo "$QUERY_STRING"|/bin/sed 's/.*arg=\([^&]*\)/\1/')
else
  CMD=$1
  ARG=$2
fi

init() {
  $wcUCI import aegis_web << EOF
package aegis_web
config subsection 'log'
EOF
$wcUCI aegis_web commit
  [ -r "$wcPRT_PTH" ] && [ $(/bin/date -d $(($(date +%s)-$(date -r $wcPRT_PTH +%s))) -D %s +%s) -lt 1296000 ] && return
  [ -d "$wcDAT_DIR" ] || mkdir $wcDAT_DIR
  /usr/bin/wget -qO- $wcPRT_URL >$wcPRT_PTH
} 2>/dev/null

uninstall() {
  /bin/rm -f /opt/bolemo/etc/config/aegis_web
  /bin/rm -f /tmp/aegis_web
  /bin/rm -rf $wcDAT_DIR
} 2>/dev/null

aegis_env() eval "$($wcAEGIS_BIN _env)" # source environment we need from aegis

status() {
  aegis_env
  set -- $($wcAEGIS_BIN _status)
  eval "_CK=$1; _PB=$2; _WN=$3; BL_NB=$4; WL_NB=$5; _LOGD=$6; WAN_IF=$7; TUN_IF=$8"
  
  echo "<h2>Status <span>@ $(/bin/date +'%Y-%m-%d %X') (router time)</span></h2>"
  if [ $((_CK+_PB)) -eq 0 ]; then
    echo '<ul id="status" class="off">'
    echo "<li>Aegis shield is not set (environment is clean).</li>"
  elif [ $_CK -le $CK_ENV_MASK ] && [ $_PB -eq 0 ]; then
    echo '<ul id="status" class="off">'
    echo "<li>Aegis shield is down (environment is set).</li>"
  elif [ $_CK -ne 0 ] && [ $_PB -eq 0 ]; then
    echo '<ul id="status" class="running">'
    echo -n "<li>Aegis shield is up."
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] && echo -n " for WAN interface ($WAN_IF)"
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] && echo -n " and VPN tunnel ($TUN_IF)"
    echo -ne ".</li>\n<li>Filtering $BL_NB IP adresses.</li>"
    [ $((_CK&CK_IPT_WL)) -ne 0 ] && echo "<li>Bypassing $WL_NB IP adresses.</li>"
    [ $_LOGD -eq 0 ] && echo "<li>Logging is enabled.</li>" || echo "<li>Logging is disabled.</li>"
  else
    echo '<ul id="status" class="error">'
    echo "<li><strong>Something is not right!</strong></li>"
  fi
  echo '</ul>'
  
  if [ $_PB -ne 0 ]; then
    echo '<h3 class="error">Errors</h3>'
    echo '<ul>'
    [ $((_PB&CK_FWS)) -ne 0 ] &&          echo "<li>set: firewall-start.sh is not set properly for $SC_NAME!</li>"
    [ $((_PB&CK_PM)) -ne 0 ] &&           echo "<li>set: post-mount.sh is not set properly for $SC_NAME!</li>"
    [ $((_PB&CK_IPS_BL)) -ne 0 ] &&       echo "<li>ipset: no blocklist is set!</li>"
    [ $((_PB&CK_IPS_WL)) -ne 0 ] &&       echo "<li>ipset: no whitelist is set!</li>"
    [ $((_PB&CK_IPT_CH)) -ne 0 ] &&       echo "<li>iptables: shield chains are not right!</li>"
    [ $((_PB&CK_IPT_WAN_BP)) -ne 0 ] &&   echo "<li>iptables: WAN network range bypass rules are not right!</li>"
    [ $((_PB&CK_IPT_TUN_BP)) -ne 0 ] &&   echo "<li>iptables: VPN network range bypass rules are not right!</li>"
    [ $((_PB&CK_IPT_WL)) -ne 0 ] &&       echo "<li>iptables: whitelist rules are not right!</li>"
    [ $((_PB&CK_IPT_TUN)) -ne 0 ] &&      echo "<li>iptables: VPN tunnel IFO rules are corrupted!</li>"
    [ $((_PB&CK_IPT_WAN)) -ne 0 ] &&      echo "<li>iptables: WAN interface IFO rules are corrupted!</li>"
    [ $((_PB&PB_IPT_WAN_MISS)) -ne 0 ] && echo "<li>iptables: WAN interface ($WAN_IF) IFO rules are missing!</li>"
    [ $((_PB&PB_IPT_IFO)) -ne 0 ] &&      echo "<li>iptables: Extra shield IFO rules were found (likely from an old interface)!</li>"
    echo '</ul>'
  fi
  
  if [ $((_CK+_PB)) -ne 0 ] && [ $_WN -ne 0 ]; then
    echo '<h3 class="warning">Warnings</h3>'
    echo '<ul>'
    case "$((_WN&WN_BL_FILE_NTLD))" in
      $WN_BL_FILE_DIFF) echo "<li>directives: ipset blocklist is different than file.</li>";;
      $WN_BL_FILE_MISS) echo "<li>directives: ipset blocklist is set but file is missing.</li>";;
      $WN_BL_FILE_NTLD) echo "<li>directives: no ipset blocklist is set but file exists.</li>";;
    esac
    case "$((_WN&WN_WL_FILE_NTLD))" in
      $WN_WL_FILE_DIFF) echo "<li>directives: ipset whitelist is different than file.</li>";;
      $WN_WL_FILE_MISS) echo "<li>directives: ipset whitelist is set but file is missing.</li>";;
      $WN_WL_FILE_NTLD) echo "<li>directives: no ipset whitelist is set but file exists.</li>";;
    esac
    [ $((_WN&CK_IPT_WAN_BP)) -ne 0 ]                  && echo "<li>iptables: WAN network range bypass rules are missing!</li>"
    [ "$TUN_IF" ] && [ $((_WN&CK_IPT_TUN_BP)) -ne 0 ] && echo "<li>iptables: VPN network range bypass rules are missing!</li>"
    [ $((_WN&WN_TUN_MISS)) -ne 0 ]                    && echo "<li>iptables: VPN tunnel ($TUN_IF) IFO rules are missing!</li>"
    [ $((_WN&WN_LOG_DIFF)) -ne 0 ]                    && echo "<li>current logging settings differs from last time shield was upreared.</li>"
    echo '</ul>'
  fi
  
  echo '<h3 class="more collapsibleList">Detailed status</h3>'
  echo '<input type="checkbox" id="detailed-status" /><label for="detailed-status">Detailed status</label>'
  echo '<ul>'
  echo "<li>Active WAN interface is '$WAN_IF'.</li>"
  [ "$TUN_IF" ] && echo "<li>Active VPN tunnel is '$TUN_IF'.</li>" || echo "<li>no VPN tunnel found.</li>"
  # dates
  [ -e "$SRC_BL_CACHE" ] && echo "<li>Sources cache directives update time: $(/bin/date +'%Y-%m-%d %X' -r $SRC_BL_CACHE)</li>"
  [ -e "$BL_FILE" ] && echo "<li>Blocklist directives generation time: $(/bin/date +'%Y-%m-%d %X' -r $BL_FILE)</li>"
  [ -e "$WL_FILE" ] && echo "<li>Whitelist directives generation time: $(/bin/date +'%Y-%m-%d %X' -r $WL_FILE)</li>"
  if [ $_CK -ne 0 ]; then
    [ $((_CK&CK_FWS)) -ne 0 ] &&        echo "<li>set: firewall-start.sh is set for $SC_NAME.</li>"
    [ $((_CK&CK_PM)) -ne 0 ] &&         echo "<li>set: post-mount.sh is set for $SC_NAME.</li>"
    [ $((_CK&CK_IPS_BL)) -ne 0 ] &&     echo "<li>ipset: blocklist is set.</li>"
    [ $((_CK&CK_IPS_WL)) -ne 0 ] &&     echo "<li>ipset: whitelist is set.</li>"
    [ $((_CK&CK_IPT_CH)) -ne 0 ] &&     echo "<li>iptables: shield chains are set.</li>"
    [ $((_CK&CK_IPT_WAN_BP)) -ne 0 ] && echo "<li>iptables: WAN network range bypass rules are set.</li>"
    [ $((_CK&CK_IPT_TUN_BP)) -ne 0 ] && echo "<li>iptables: VPN network range bypass rules are set.</li>"
    [ $((_CK&CK_IPT_WL)) -ne 0 ] &&     echo "<li>iptables: whitelist rules are set.</li>"
    [ $((_CK&CK_IPT_LOG)) -ne 0 ] &&    echo "<li>iptables: logging is on.</li>"
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] &&    echo "<li>iptables: VPN tunnel IFO rules are set.</li>"
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] &&    echo "<li>iptables: WAN interface IFO rules are set.</li>"
  fi
  echo '</ul>'
  
  # Status file
  echo '<h3 class="more collapsibleList">Last shield uprear report</h3>'
  echo '<input type="checkbox" id="launch-report" /><label for="launch-report">Last shield uprear report</label>'
  echo '<ul>'
  if [ -r "$INFO_FILE" ]; then
    read INFO INFO_WAN INFO_TUN<"$INFO_FILE"
    INFO_FROM=$((INFO&INFO_FROM_MASK))
    INFO_IPS=$(((INFO>>INFO_IPS_SHIFT)&INFO_IPS_MASK))
    INFO_IPT=$(((INFO>>INFO_IPT_SHIFT)&INFO_IPT_MASK))
    INFO_LOGD=$(((INFO>>INFO_LOGD_SHIFT)&INFO_LOGD_MASK))
    case "$INFO_FROM" in
      $INFO_FROM_SC) FROM="$SC_NAME script" ;;
      $INFO_FROM_PM) FROM="post-mount.sh" ;;
      $INFO_FROM_FWS) FROM="firewall-start.sh" ;;
    esac
    echo "<li>shield was upreared from: $FROM @ $(/bin/date +'%Y-%m-%d %X' -r $INFO_FILE)</li>"
    echo "<li>WAN interface was '$INFO_WAN'.</li>"
    [ "$INFO_TUN" ] && echo "<li>VPN tunnel was '$INFO_TUN'.</li>" || echo "<li>No VPN tunnel was found.</li>"
    case $((INFO_IPS&INFO_IPS_BL_MASK)) in
      0)                 echo "<li><strong>directives: blocklist file was not found!</strong></li>" ;;
      $INFO_IPS_BL_SAME) echo "<li>directives: ipset blocklist was already set and identical to file.</li>" ;;
      $INFO_IPS_BL_MISS) echo "<li>directives: ipset blocklist file was not found! The one already set was kept.</li>" ;;
      $INFO_IPS_BL_LOAD) echo "<li>directives: ipset blocklist was set from file.</li>" ;;
    esac
    case $((INFO_IPS&INFO_IPS_WL_MASK)) in
      0)                                      echo "<li>directives: no whitelist file was found.</li>" ;;
      $((INFO_IPS_WL_SAME+INFO_IPS_WL_KEEP))) echo "<li>directives: ipset whitelist was already set and identical to file.</li>" ;;
      $INFO_IPS_WL_KEEP)                      echo "<li>directives: ipset whitelist was kept.</li>" ;;
      $INFO_IPS_WL_LOAD)                      echo "<li>directives: ipset whitelist was set from file.</li>" ;;
      $INFO_IPS_WL_SWAP)                      echo "<li>directives: ipset whitelist was updated from file.</li>" ;;
      $INFO_IPS_WL_DEL)                       echo "<li>directives: ipset whitelist was unset.</li>" ;;
    esac
    if [ $((INFO_IPT & INFO_IPT_SRC_KEEP)) -eq 0 ]
      then echo "<li>iptables: shield inbound chain was set.</li>"
      else echo "<li>iptables: shield inbound chain was already set.</li>"
    fi
    if [ $((INFO_IPT & INFO_IPT_DST_KEEP)) -eq 0 ]
      then echo "<li>iptables: shield outbound chain was set.</li>"
      else echo "<li>iptables: shield outbound chain was already set.</li>"
    fi
    [ $((INFO_IPT & INFO_IPT_IB_PBM)) -ne 0 ] && echo '<li>iptables: some irrelevant bypass rules had to be removed.</li>'
    if [ $((INFO_IPS & INFO_IPS_WB_NDD)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_WB_SRC_NEW)) -ne 0 ]
        then echo '<li>iptables: inbound WAN network range bypass rules were set.</li>'
        else echo '<li>iptables: inbound WAN network range bypass rules were kept.</li>'
      fi
      if [ $((INFO_IPT & INFO_IPT_WB_DST_NEW)) -ne 0 ]
        then echo '<li>iptables: outbound WAN network range bypass rules were set.</li>'
        else echo '<li>iptables: outbound WAN network range bypass rules were kept.</li>'
      fi
    else echo '<li>iptables: WAN network range bypass rules were not needed or manually skipped.</li>'
    fi
    if [ $((INFO_IPS & INFO_IPS_TB_NDD)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_TB_SRC_NEW)) -ne 0 ]
        then echo '<li>iptables: inbound VPN network range bypass rules were set.</li>'
        else echo '<li>iptables: inbound VPN network range bypass rules were kept.</li>'
      fi
      if [ $((INFO_IPT & INFO_IPT_TB_DST_NEW)) -ne 0 ]
        then echo '<li>iptables: outbound VPN network range bypass rules were set.</li>'
        else echo '<li>iptables: outbound VPN network range bypass rules were kept.</li>'
      fi
    else [ "$INFO_TUN" ] && echo '<li>iptables: VPN network range bypass rules were not needed or manually skipped.</li>'
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
    case "$INFO_LOGD" in
      $INFO_LOGD_KEEP_OFF) echo '<li>log daemon: was already off.</li>';;
      $INFO_LOGD_KEEP_ON) echo '<li>log daemon: was already on.</li>';;
      $INFO_LOGD_STOPPED) echo '<li>log daemon: was turned off.</li>';;
      $INFO_LOGD_STARTED) echo '<li>log daemon: was turned on.</li>';;
    esac
  else
    echo "<li>No status file found.</li>"
  fi
  echo '</ul>'
  
  # Debug
  get_ipt
  echo -e "<h3 class=\"debug collapsibleList\">Debug</h3>
<input type=\"checkbox\" id=\"debug-status\" /><label for=\"debug-status\">Debug</label>
<ul><li>device info: $(/bin/cat /module_name /hardware_version /firmware_version)</li>
<li>aegis info: $SC_NAME $SC_VERS-$([ "$EXT_DRIVE" ] && echo 'ext' || echo 'int')</li>
<li>status codes: $_CK|$_PB|$_WN|$WAN_IF|$(inet_for_if $WAN_IF)|$TUN_IF|$([ $TUN_IF ] && inet_for_if $TUN_IF)|$BL_NB|$WL_NB|$_LOGD</li>
<li>file codes: $INFO|$INFO_WAN|$INFO_TUN</li>
<li>timestamps: $(/bin/date +%s -r $INFO_FILE)|$(/bin/date +%s -r $BL_FILE)|$(/bin/date +%s -r $WL_FILE)</li>
<li>iptables engine rules:</li><ul>"
  [ -z "$_IPT" ] && echo "<li>no $SC_NAME rules are set.</li>" || echo "$_IPT"|/usr/bin/awk '{print "<li>" $0 "</li>"}'
  echo '</ul><li>ipset engine sets:</li><ul>'
  ipset -L -n|/bin/grep -F -- "$SC_ABR"|while read _SET; do
    case "$_SET" in
      "$IPSET_BL_NAME") _NAME='blocklist' ;;
      "$IPSET_WL_NAME") _NAME='whitelist' ;;
      *) _NAME="$_SET" ;;
    esac
    echo "<li>$_NAME:</li><ul>"
    ipset -L -t $_SET|/usr/bin/awk '{print "<li>" $0 "</li>"}'
    echo '</ul>'
  done
  echo '</ul></ul>'
} 2>/dev/null

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
  case "$(echo -n "$ARG"|/usr/bin/cut -d: -f2)" in
    on)  _LOG=' -log-enable';;
    off) _LOG=' -log-disable';;
    *) _LOG=;;
  esac
  case $ARG in
    upgrade*) _CMD="aegis _upgrade" ;;
    up*) _CMD="aegis _up$_LOG" ;;
    refresh_custom*) _CMD="aegis _refresh -custom-only$_LOG" ;;
    refresh*) _CMD="aegis _refresh$_LOG" ;;
    down*) _CMD="aegis _down" ;;
  esac
  [ -z "${ARG##*-*}" ] && _ARG2="${ARG#*-}"
  /opt/bolemo/scripts/$_CMD|/usr/bin/awk '!/^[[:cntrl:]]\[[0-9;]+m$/{gsub("[[:cntrl:]]\[[0-9;]+m","\0",$0);print;system("")}'
  if [ $? = 0 ]; then echo "Success!"; else echo "A problem was encountered."; exit 1; fi;
  if [ $_ARG2 ]; then ARG="$_ARG2"; _ARG2=''; command; fi;
}

# LOG
_LF=/var/log/log-aegis
_SF=/tmp/aegis_status

_getLog() {
  _RNM="$(/bin/nvram get Device_name)"
  _MAX=$($wcUCI get aegis_web.log.len)
  _BT=$($wcUCI get aegis_web.log.basetime)
  _ST=$($wcUCI get aegis_web.log.pos)
  _WIF=$(/usr/bin/cut -d' ' -f2 $_SF)
  _TIF=$(/usr/bin/cut -d' ' -f3 $_SF)
  /usr/bin/awk -F: '
function namefromip(ip){
  cmd="/usr/bin/awk '"'"'$1==\""ip"\"{print $3;exit}'"'"' /tmp/netscan/attach_device";cmd|getline nm;close(cmd);
  if (!nm) {cmd="/usr/bin/awk '"'"'$1==\""ip"\"{print NF;exit}'"'"' /tmp/dhcpd_hostlist /tmp/hosts";cmd|getline nm;close(cmd)}
  if (nm) {nm=nm"<q>"ip"</q>"} else {nm=ip}
  return nm}
function protoname(proto){
  if (proto~/^[0-9]+$/){
     cmd="sed \""proto+2"q;d\" '"$wcPRT_PTH"'|cut -d, -f3";cmd|getline nm;close(cmd);
     nm="<log-ptl value=\""proto"\">"nm"</log-ptl>"
  } else {nm="<log-ptl value=\""proto"\">"proto"</log-ptl>"}
  return nm}
function getval(n){i=index(l[c]," "n"=");if(i==0)return;str=substr(l[c],i+length(n)+2);i=index(str," ");str=substr(str,0,i-1);return str}
function pline(iface){
  if (IN==iface) {REM=SRC; RPT=SPT; LPT=DPT; ATTR="incoming";
     if (OUT=="") {LOC=DST; LNM=(DST=="255.255.255.255")?"broadcast":"router"}
     else {LOC=namefromip(DST); LNM="LAN"}
  } else if (OUT==iface) {REM=DST; RPT=DPT; LPT=SPT; ATTR="outgoing";
     if (IN=="") {LOC='$_RNM'"<q>"SRC"</q>"; LNM="router"}
     else {LOC=namefromip(SRC); LNM="LAN"}
  } else return 0;
  return 1;}
{ts[++c]=$1;uts[c]=$1$2;l[c]=$0} END
{if (uts[c]) {system("'"$wcUCI"' set aegis_web.log.pos="uts[c++])}
 min=(NR>'$_MAX')?NR-'$_MAX':0;while(--c>min && uts[c]>'$_ST'){
   PT=strftime("%F %T", ('$_BT'+ts[c]));
   IN=getval("IN"); OUT=getval("OUT"); SRC=getval("SRC"); DST=getval("DST"); PROTO=protoname(getval("PROTO")); SPT=getval("SPT"); DPT=getval("DPT");
   if (pline("'$_WIF'")) {ATTR2=" wan"} else if (pline("'$_TIF'")) {ATTR2=" vpn"}
   if (RPT) {RPT="<log-pt>"RPT"</log-pt>"}; if (LPT) {LPT="<log-pt>"LPT"</log-pt>"}
   print "<p class=\"new "ATTR ATTR2"\">"PT"<log-lbl></log-lbl><log-dir></log-dir>"PROTO"<log-rll><log-if></log-if></log-rll><log-rem><log-rip>"REM"</log-rip>"RPT"</log-rem><log-lll><log-lnm>"LNM"</log-lnm></log-lll><log-loc><log-lip>"LOC"</log-lip>"LPT"</log-loc></p>"
}}' $_LF
}

log() {
#  aegis_env
  case $ARG in
    ''|*[!0-9]*) LEN=100 ;;
    *) if [ $ARG -lt 1 ]; then LEN=1
       elif [ $ARG -gt 300 ]; then LEN=300
       else LEN=$ARG
       fi ;;
  esac
  $wcUCI set aegis_web.log.len=$LEN
  $wcUCI set aegis_web.log.basetime=$(( $(/bin/date +%s) - $(/usr/bin/cut -d. -f1 /proc/uptime) ))
  $wcUCI set aegis_web.log.pos=0
  _getLog
}

refreshLog() {
  _getLog
}

_ip_in_if_inet() {
  [ -z "$2" ] && return 1
  _IP="$(/usr/sbin/ip -4 addr show $2|/usr/bin/awk 'NR==2 {print $2;exit}')"
  OLDIFS=$IFS; IFS=. read -r T3 T2 T1 T0 E3 E2 E1 E0 S3 S2 S1 S0 << EOF
$1.$(/bin/ipcalc.sh $_IP|/usr/bin/awk -F= '/BROADCAST|NETWORK/ {ORS=".";print $2}')
EOF
  IFS=$OLDIFS
  T=$(((T3<<24)+(T2<<16)+(T1<<8)+T0))
  S=$(((S3<<24)+(S2<<16)+(S1<<8)+S0))
  E=$(((E3<<24)+(E2<<16)+(E1<<8)+E0))
  [ $T -ge $S -a $T -le $E ] && return 0 || return 1
}

checkIp() {
  aegis_env
  IP="$ARG"
  /usr/bin/traceroute -q1 -m1 -w1 -i $WAN_IF $IP 38 2>&1 >/dev/null | /bin/grep -qF 'sendto: Operation not permitted' \
    && echo "IP address $IP is blocked by the router.<br />" \
    || echo "IP address $IP is not blocked by the router.<br />"
  ipset -L -n|/bin/grep -F -- "$SC_ABR"|while read _SET; do case "$_SET" in
    "$IPSET_BL_NAME") ipset -q test $IPSET_BL_NAME $IP && echo "IP address $IP is in Aegis blocklist directives.<br />" ;;
    "$IPSET_WL_NAME") ipset -q test $IPSET_WL_NAME $IP && echo "IP address $IP is in Aegis whitelist directives.<br />" ;;
  esac; done
  _ip_in_if_inet $IP $WAN_IF && echo "IP address $IP is in the WAN network range ($(inet_for_if $WAN_IF)).<br />"
  _ip_in_if_inet $IP $TUN_IF && echo "IP address $IP is in the VPN network range ($(inet_for_if $TUN_IF)).<br />"
  echo "---<br />"
}

printList() {
  aegis_env
  case "$ARG" in
    sources) _LIST="$SRC_LIST";;
    blacklist) _LIST="$(echo "$CUST_BL_FILE"|sed 's/\*//')";;
    whitelist) _LIST="$(echo "$CUST_WL_FILE"|sed 's/\*//')";;
  esac
  if test -s "$_LIST"
    then echo -n "<u>File:</u> $_LIST, <u>last modified:</u> "; date -r "$_LIST"; /bin/sed '/^[[:space:]]*$/d' "$_LIST"
    else echo "<u>File:</u> $_LIST does not exist or is empty."
  fi
}

saveList() {
  aegis_env
  _READ=`/bin/sed '/^[[:space:]]*$/d'`
  case "$ARG" in
    sources) _LIST="$SRC_LIST";;
    blacklist) _LIST="$(echo "$CUST_BL_FILE"|sed 's/\*//')";;
    whitelist) _LIST="$(echo "$CUST_WL_FILE"|sed 's/\*//')";;
  esac
  if [ -z "$_READ" ]; then
    [ -e "$_LIST" ] && { rm -f "$_LIST" 2>/dev/null; echo $?; return; }
    echo 0
  elif [ "$(/bin/cat $_LIST)" = "$_READ" ]; then
    echo 0
  else
    echo "$_READ" >"$_LIST"
    [ "$(/bin/cat $_LIST)" = "$_READ" ] && echo 0 || echo 1
  fi
}

protoInfo() {
  [ -r "$wcPRT_PTH" ] || return
  [ -z "${ARG##*[!0-9]*}" ] && _M='$2' || _M='$1'
  _DATA="$(/usr/bin/awk -F, 'match ('$_M',/^'$ARG'$/) {print $0; exit}' $wcPRT_PTH)"
  _TITLE="$(echo "$_DATA"|/usr/bin/cut -d, -f3)"
  [ -z "$(echo "$_DATA"|/usr/bin/cut -d, -f5)" ] || _PREMSG="<p><u>IPv6 Extension Header</u></p>"
  _MESSAGE="$_PREMSG<p>$(echo "$_DATA"|/usr/bin/cut -d, -f4)</p>"
  echo "{\"title\":\"$_TITLE\",\"message\":\"$_MESSAGE\"}"
}

# MAIN
case $CMD in
  init) init;;
  info) info;;
  status) status;;
  command) command;;
  log) log;;
  refresh_log) refreshLog;;
  check) checkIp;;
  print_list) printList;;
  save_list) saveList;;
  proto_info) protoInfo;;
  uninstall) uninstall;;
esac
exit 0
