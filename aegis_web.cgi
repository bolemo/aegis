#!/bin/sh
wcAEGIS_BIN='/opt/bolemo/scripts/aegis'
wcPRT_URL='https://raw.githubusercontent.com/bolemo/aegis/master/data/net-protocols.csv'
wcDAT_DIR='/www/bolemo/aegis_data'; wcPRT_PTH="$wcDAT_DIR/net-protocols.csv"
wcUCI='/sbin/uci -qc /opt/bolemo/etc/config'
wcLHTTPD_CONF='/etc/lighttpd/conf.d'
wcLHTTPD_WC_CONF="$wcLHTTPD_CONF/31-aegis.conf"

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
  /usr/bin/wget -qO- --no-check-certificate $wcPRT_URL >$wcPRT_PTH
} 2>/dev/null

postinstall() {
  if test -d "$wcLHTTPD_CONF" && ! test -e "$wcLHTTPD_WC_CONF"; then
    cat >/opt/bolemo/etc/lighttpd_aegis_web.conf <<'EOF'
$HTTP["url"] =~ "/bolemo/" {
    cgi.assign = ( "aegis_web.cgi" => "/opt/bolemo/www/cgi-bin/aegis_web.cgi" )
}
EOF
    /bin/ln -sfn /opt/bolemo/etc/lighttpd_aegis_web.conf "$wcLHTTPD_WC_CONF"
    /etc/init.d/lighttpd restart
  fi
}

uninstall() {
  /bin/rm -f /opt/bolemo/etc/config/aegis_web
  /bin/rm -f /tmp/aegis_web
  /bin/rm -rf "$wcDAT_DIR"
  /bin/rm -rf "$wcLHTTPD_WC_CONF"
} 2>/dev/null

aegis_env() eval "$($wcAEGIS_BIN _env)" # source environment we need from aegis

status() {
  aegis_env
  set -- $($wcAEGIS_BIN _status)
  eval "_CK=$1 _DNA=$2 _DIR=$3 _ABLC=$4 _AWLC=$5 _WBLC=$6 _WWLC=$7 _TBLC=$8 _TWLC=$9 _WAN=$10 _TUN=$11 _WINET=$12 _TINET=$13 _ONFO=$14 _ODNA=$15 _OWAN=$16 _OWINET=$17 _OTUN=$18 _OTINET=$19"

  _OFROM=$((_ONFO&INFO_FROM_MASK))
  _ODIR=$(((_ONFO>>INFO_DIR_SHIFT)&INFO_DIR_MASK))
  _OIPT=$(((_ONFO>>INFO_IPT_SHIFT)&INFO_IPT_MASK))
  _OLOGD=$(((_ONFO>>INFO_LOGD_SHIFT)&INFO_LOGD_MASK))
  
  _PB=false _UNSET=false _DOWN=false
  
  [ $((_CK&CK_SET)) -gt $CK_UNSET -a $((_CK&CK_SET)) -lt $CK_SETOK ] && _PB=true
  if [ $_CK -le $CK_UNSET ]; then             _UNSET=true
  elif [ $((_CK&CK_DPB)) -lt $CK_SND ]; then  _DOWN=true
  elif [ $((_CK&CK_DPB)) -gt $CK_UPOK ]; then _PB=true
  fi
  
  if [ $_CK -ge $CK_DLOGD ]; then _PB=true
  
  echo "<h2>Status <span>@ $(/bin/date +'%Y-%m-%d %X') (router time)</span></h2>"
  if $_UNSET; then
    if $_PB; then echo '<ul id="status" class="error"><li>Problems found!</li>'
             else echo '<ul id="status" class="off">'
    fi
    echo "<li>Aegis shield is unset.</li>"
  elif $_DOWN; then
    if $_PB; then echo '<ul id="status" class="error"><li>Problems found!</li>'
             else echo '<ul id="status" class="off">'
    fi
    echo "<li>Aegis shield is down.</li>"
  else
    if $_PB; then echo '<ul id="status" class="error"><li>Problems found!</li>'
             else echo '<ul id="status" class="running">'
    fi
    if [ $((_CK&CK_DPB)) -ge $CK_SND ]; then # creating up status info string
      _STRBLC="global: $_ABLC" _STRWLC="global: $_AWLC"
      if [ "$_OWAN" ]; then _UPSTR="WAN interface ($_OWAN)" _STRBLC="$_STRBLC, WAN only: $_WBLC" _STRWLC="$_STRWLC, WAN only: $_WWLC"; fi
      if [ "$_OTUN" ]; then
        [ "$_UPSTR" ] && _UPSTR="$_UPSTR and VPN tunnel ($_OTUN)" || _UPSTR="VPN tunnel ($_OTUN)"
        _STRBLC="$_STRBLC, VPN only: $_TBLC" _STRWLC="$_STRWLC, VPN only: $_TWLC"
      fi
      _UPSTR=" for: $_UPSTR.</li><li>blocking a total of $((_ABLC+_WBLC+_TBLC)) IP adresses ($_STRBLC).\n- bypassing $((_AWLC+_WWLC+_TWLC)) IP adresses ($_STRWLC)"
    fi
    echo -n "<li>Aegis shield is up$_UPSTR.</li>" 
  fi
  if [ $_CK -gt $CK_LOGD ]; then echo "<li>Logging is enabled.</li>"
                            else echo "<li>Logging is disabled.</li>"
  fi
  echo '</ul>'
  
  if $_PB; then # we have problems
    echo '<h3 class="error">Problems</h3>'
    echo '<ul>'
    [ $((_CK&CK_FWS)) -eq 0 ] &&       echo "<li>set: firewall-start.sh is not set for $SC_NAME!</li>"
    [ $((_CK&CK_PM)) -eq $CK_PMND ] && echo "<li>set: post-mount.sh is not set for $SC_NAME!</li>"
    if [ $((_CK&CK_SND)) -ne 0 ]; then
      [ $((_CK&CK_NFO)) -eq 0 ] &&     echo "<li>status file is missing!</li>"
      [ $((_CK&CK_UPF)) -eq 0 ] &&     echo "<li>shield should be down, but is not!</li>"
    else
      [ $((_CK&CK_NFO)) -ne 0 ] &&     echo "<li>shield is down, but status file exists!</li>"
      [ $((_CK&CK_UPF)) -ne 0 ] &&     echo "<li>shield should be up, but is not!</li>"
    fi
    if [ $((_CK&CK_DDNA)) -ne 0 ]; then
       _parse_dir() { case "$(($1&INFO_DIR__MASK))" in
         "$INFO_DIR__DIFF") echo "<li>directives: $2 changed since $SC_NAME was upreared!</li>";; # loaded != file
         "$INFO_DIR__KEEP") echo "<li>directives: $2 is missing (but loaded in ipset)!</li>";; # loaded but no file
         "$INFO_DIR__LOAD") echo "<li>directives: $2 was created after $SC_NAME was upreared!</li>";; # file exists, but not loaded
       esac; }
      _parse_dir $((_DIR>>(INFO_DIR_ALL+INFO_DIR_BL))) 'global blocklist'
      _parse_dir $((_DIR>>(INFO_DIR_WAN+INFO_DIR_BL))) 'WAN specific blocklist'
      _parse_dir $((_DIR>>(INFO_DIR_TUN+INFO_DIR_BL))) 'VPN specific blocklist'
      _parse_dir $((_DIR>>(INFO_DIR_ALL+INFO_DIR_WL))) 'global whitelist'
      _parse_dir $((_DIR>>(INFO_DIR_WAN+INFO_DIR_WL))) 'WAN specific whitelist'
      _parse_dir $((_DIR>>(INFO_DIR_TUN+INFO_DIR_WL))) 'VPN specific whitelist'
    fi
    [ $((_CK&CK_DWIF)) -ne 0 ] &&   echo "<li>WAN: interface changed from '$_OWAN' to '$WAN_IF' since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_DWINET)) -ne 0 ] && echo "<li>WAN: interface subnet range changed from $_OWINET to $_WINET since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_DTIF)) -ne 0 ] &&   echo "<li>VPN: tunnel changed from '$_OTUN' to '$TUN_IF' since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_DTINET)) -ne 0 ] && echo "<li>VPN: tunnel subnet range changed from $_OTINET to $_TINET since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_OIPT)) -ne 0 ] &&   echo "<li>iptables: $SC_NAME rules were UNSUCCESSFULLY (re)set during last uprear!</li>"
    [ $((_CK&CK_DIPT)) -ne 0 ] &&   echo "<li>iptables: current $SC_NAME rules were modified since last uprear!</li>"
    
    if [ $_CK -ge $((CK_DLOGD+CK_LOGD)) ]; then echo "<li>logd: the log daemon is running but was not started from the shield!</li>"
    elif [ $_CK -ge $CK_DLOGD ]; then           echo "<li>logd: log daemon was started but is not running!</li>"
    fi
    echo '</ul>'
  fi
  
  
  
  
  
#    echo '<h3 class="warning">Warnings</h3>'
  
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
    if  [ $((INFO_IPT&INFO_IPT_KEEP)) -ne 0 ]; then echo "<li>iptables: rules were already set."; _P_IPT=true
    elif [ $((INFO_IPT&INFO_IPT_RUN)) -ne 0 ]; then echo "<li>iptables: rules were (re)set."; _P_IPT=true
    else _P_IPT=false; fi
    if $_P_IPT; then
      [ $((INFO_IPT&INFO_IPT_WIF)) -ne 0 ] && echo "<li>iptables: rules for WAN interface in place.</li>"
      [ $((INFO_IPT&INFO_IPT_TIF)) -ne 0 ] && echo "<li>iptables: rules for VPN interface in place.</li>"
      [ $((INFO_IPT&INFO_IPT_WIB)) -ne 0 ] && echo "<li>iptables: WAN network range bypass rules in place.</li>"
      [ $((INFO_IPT&INFO_IPT_TIB)) -ne 0 ] && echo "<li>iptables: VPN network range bypass rules in place.</li>"
      [ $((INFO_IPT&INFO_IPT_WL)) -ne 0 ]  && echo "<li>iptables: whitelist bypass rules in place.</li>"
      [ $((INFO_IPT&INFO_IPT_LOG)) -ne 0 ] && echo "<li>iptables: logging rules in place.</li>"
    else echo "<li><strong>iptables: rules were UNSUCCESSFULLY (re)set!</strong></li>"; fi
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
<li>aegis info: $SC_NAME $SC_VERS-$($EXT_DRIVE && echo 'ext' || echo 'int')</li>
<li>status codes: ck:$_CK|pb:$_PB|wn:$_WN|wif:$WAN_IF|wnt:$(inet_for_if $WAN_IF)|tif:$TUN_IF|tnt:$([ $TUN_IF ] && inet_for_if $TUN_IF)|blc:$BL_NB|wlc:$WL_NB|log:$_LOGD</li>
<li>info file: $INFO|$INFO_WAN|$INFO_TUN</li>
<li>timestamps: inf:$(/bin/date +%s -r $INFO_FILE)|cch:$(/bin/date +%s -r $SRC_BL_CACHE)|bld:$(/bin/date +%s -r $BL_FILE)|wld:$(/bin/date +%s -r $WL_FILE)</li>
<li>conf:</li><ul>"$(/sbin/uci -c "$CONF_DIR" show|/usr/bin/awk '{print "<li>"$0"</li>"}')"</ul>
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
  $EXT_DRIVE && _JSON="$_JSON, \"location\":\"external\"" || _JSON="$_JSON, \"location\":\"internal\""
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
  # attach_device depends on router model
  if [ "$(cat /module_name)" == "RBR50" ] ; then
    _NSDEVCMD='BEGIN{RS=\"-----device:[[:digit:]]+-----\";FS=\"\\n\"}NR==1{next}$2==\""ip"\"{print $8;exit}'
  else
    _NSDEVCMD='$1==\""ip"\"{print $3;exit}'
  fi
  /usr/bin/awk -F: '
function namefromip(ip){
  nm="";cmd="/usr/bin/awk '"'$_NSDEVCMD'"' /tmp/netscan/attach_device";cmd|getline nm;close(cmd);
  if (!nm) {cmd="/usr/bin/awk '"'"'$1==\""ip"\"{print $NF;exit}'"'"' /tmp/dhcpd_hostlist /tmp/hosts";cmd|getline nm;close(cmd)}
  if (nm) {nm=nm"<q>"ip"</q>"} else {nm=ip}
  return nm}
function protoname(proto){
  if (proto~/^[0-9]+$/){
     cmd="sed \""proto+2"q;d\" '"$wcPRT_PTH"'|cut -d, -f3";cmd|getline nm;close(cmd);
     nm="<log-ptl value=\""proto"\">"nm"</log-ptl>"
  } else {nm="<log-ptl value=\""proto"\">"proto"</log-ptl>"}
  return nm}
function getval(n){i=index(l[c]," "n"=");if(i==0)return;str=substr(l[c],i+length(n)+2);i=index(str," ");str=substr(str,0,i-1);return str}
{ts[++c]=$1;uts[c]=$1$2;l[c]=$0} END
{if (uts[c]) {system("'"$wcUCI"' set aegis_web.log.pos="uts[c++])}
 min=(NR>'$_MAX')?NR-'$_MAX':0;while(--c>min && uts[c]>'$_ST'){
   PT=strftime("%F %T", ('$_BT'+ts[c]));
   IFACE=getval("IF"); WAY=getval("DIR"); IN=getval("IN"); OUT=getval("OUT"); SRC=getval("SRC"); DST=getval("DST"); PROTO=protoname(getval("PROTO")); SPT=getval("SPT"); DPT=getval("DPT");
   if (IFACE=="WAN") {ATTR2=" wan"} else if (IFACE=="VPN") {ATTR2=" vpn"}
   if (WAY=="IN"){REM=SRC;RPT=SPT;LPT=DPT;ATTR="incoming";
     if (OUT=="") {LOC=DST; LNM=(DST=="255.255.255.255")?"broadcast":"router"}
     else {LOC=namefromip(DST); LNM="LAN"}
   } else if (WAY=="OUT"){REM=DST;RPT=DPT;LPT=SPT;ATTR="outgoing";
     if (IN=="") {LOC=SRC; LNM="router"}
     else {LOC=namefromip(SRC); LNM="LAN"}
   }
   if (RPT) {RPT="<log-pt>"RPT"</log-pt>"}; if (LPT) {LPT="<log-pt>"LPT"</log-pt>"}
   print "<p class=\"new "ATTR ATTR2"\">"PT"<log-lbl></log-lbl><log-dir></log-dir>"PROTO"<log-rll><log-if></log-if></log-rll><log-rem><log-rip>"REM"</log-rip>"RPT"</log-rem><log-lll><log-lnm>"LNM"</log-lnm></log-lll><log-loc><log-lip>"LOC"</log-lip>"LPT"</log-loc></p>"
}}' $_LF
}

log() {
#  aegis_env
  [ "$(cat /module_name)" == "RBR50" ] && MAX=150 || MAX=300
  case $ARG in
    ''|*[!0-9]*) LEN=100 ;;
    *) if [ $ARG -lt 1 ]; then LEN=1
       elif [ $ARG -gt $MAX ]; then LEN=$MAX
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
  ip_in_if_inet $IP $WAN_IF && echo "IP address $IP is in the WAN network range ($(inet_for_if $WAN_IF)).<br />"
  ip_in_if_inet $IP $TUN_IF && echo "IP address $IP is in the VPN network range ($(inet_for_if $TUN_IF)).<br />"
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
# called from ajax, expecting output for lighttpd
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
# called from aegis only
  postinstall) postinstall; exit;;
  uninstall) uninstall; exit;;
esac

# lighttpd empty response fix:
echo ' '

exit 0
