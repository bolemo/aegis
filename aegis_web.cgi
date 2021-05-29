#!/bin/sh
wcAEGIS_BIN='/opt/bolemo/scripts/aegis'
wcGIT_DIR='https://raw.githubusercontent.com/bolemo/aegis/stable'
wcPRT_URL="$wcGIT_DIR/data/net-protocols.csv"
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

uninstall() {
  /bin/rm -f /opt/bolemo/etc/config/aegis_web
  /bin/rm -f /tmp/aegis_web
  /bin/rm -rf "$wcDAT_DIR"
  /bin/rm -rf "$wcLHTTPD_WC_CONF"
} 2>/dev/null

aegis_env() { eval "$($wcAEGIS_BIN _env)"; } # source environment we need from aegis

status() {
  aegis_env
  set -- $($wcAEGIS_BIN _status)
  eval "_CK=$1 _DNA=$2 _DIR=$3 _ABLC=$4 _AWLC=$5 _WBLC=$6 _WWLC=$7 _TBLC=$8 _TWLC=$9 _WAN=${10} _TUN=${11} _WINET=${12} _TINET=${13} _ONFO=${14} _ODNA=${15} _OWAN=${16} _OWINET=${17} _OTUN=${18} _OTINET=${19}"

  _OFROM=$((_ONFO&INFO_FROM_MASK))
  _ODIR=$(((_ONFO>>INFO_DIR_SHIFT)&INFO_DIR_MASK))
  _OIPT=$(((_ONFO>>INFO_IPT_SHIFT)&INFO_IPT_MASK))
  _OLOGD=$(((_ONFO>>INFO_LOGD_SHIFT)&INFO_LOGD_MASK))
  
  _PB=false _UNSET=false _DOWN=false
  
  [ $((_CK&CK_SET)) -gt $CK_UNSET ] && [ $((_CK&CK_SET)) -lt $CK_SETOK ] && _PB=true
  [ $((_CK&CK_SND)) -eq 0 ] &&                _DOWN=true
  if [ $_CK -le $CK_UNSET ]; then             _UNSET=true
  elif [ $_CK -le $CK_SET ]; then : # Down, already known
  elif [ $((_CK&CK_DPB)) -lt $CK_UPOK ]; then _PB=true
  elif [ $((_CK&CK_DPB)) -gt $CK_DOK ]; then  _PB=true
  fi
  [ $((_CK&CK_DLOGD)) -ne 0 ] && _PB=true
  
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
      _UPSTR=" for: $_UPSTR.</li><li>Blocking a total of $((_ABLC+_WBLC+_TBLC)) IP addresses ($_STRBLC).</li><li>Bypassing $((_AWLC+_WWLC+_TWLC)) IP addresses ($_STRWLC)"
    fi
    echo -n "<li>Aegis shield is up$_UPSTR.</li>" 
  fi
  case $((_CK&CK_LOG)) in        0) echo -e "<li>Logging is disabled.</li>";;
                          $CK_LOGD) echo -e "<li>Logging is enabled.</li>";;
                                 *) echo -e "<li><i>Logging is defective!</i></li>";;
  esac
  echo '</ul>'
  
  #    echo '<h3 class="warning">Warnings</h3>'

  if $_PB; then # we have problems
    echo '<h3 class="error">Problems</h3>'
    echo '<ul>'
    [ $((_CK&CK_FWS)) -eq 0 ] &&       echo "<li>set: firewall-start.sh is not set for $SC_NAME!</li>"
    [ $((_CK&CK_PM)) -eq 0 ] &&        echo "<li>set: post-mount.sh is not set for $SC_NAME!</li>"
    if [ $((_CK&CK_SND)) -ne 0 ]; then
      [ $((_CK&CK_NFO)) -eq 0 ] &&     echo "<li>status file is missing!</li>"
      [ $((_CK&CK_UPF)) -eq 0 ] &&     echo "<li>shield should be down, but is not!</li>"
    else
      [ $((_CK&CK_NFO)) -ne 0 ] &&     echo "<li>shield is down, but status file exists!</li>"
      [ $((_CK&CK_UPF)) -ne 0 ] &&     echo "<li>shield was upreared, but is not up!</li>"
    fi
    [ $((_CK&CK_BLNS)) -eq 0 ] &&      echo "<li>directives: there are no blocking directives!</li>"
    if [ $((_CK&CK_DDNA)) -ne 0 ]; then
       _parse_dir() { case "$(($1&INFO_DIR__MASK))" in
         "$INFO_DIR__DIFF") echo "<li>directives: $2 changed since $SC_NAME was upreared!</li>";; # loaded != file
         "$INFO_DIR__KEEP") echo "<li>directives: $2 is missing (but loaded in ipset)!</li>";; # loaded but no file
         "$INFO_DIR__LOAD") echo "<li>directives: $2 was created after $SC_NAME was upreared!</li>";; # file exists, but not loaded
       esac; }
      _parse_dir $((_DIR>>(INFO_DIR_ALL+INFO_DIR_BL))) 'global block list'
      _parse_dir $((_DIR>>(INFO_DIR_WAN+INFO_DIR_BL))) 'WAN specific block list'
      _parse_dir $((_DIR>>(INFO_DIR_TUN+INFO_DIR_BL))) 'VPN specific block list'
      _parse_dir $((_DIR>>(INFO_DIR_ALL+INFO_DIR_WL))) 'global bypass list'
      _parse_dir $((_DIR>>(INFO_DIR_WAN+INFO_DIR_WL))) 'WAN specific bypass list'
      _parse_dir $((_DIR>>(INFO_DIR_TUN+INFO_DIR_WL))) 'VPN specific bypass list'
    fi
    [ $((_CK&CK_DWIF)) -ne 0 ] &&   echo "<li>WAN: interface changed from '$_OWAN' to '$WAN_IF' since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_DWINET)) -ne 0 ] && echo "<li>WAN: interface subnet range changed from $_OWINET to $_WINET since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_DTIF)) -ne 0 ] &&   echo "<li>VPN: tunnel changed from '$_OTUN' to '$TUN_IF' since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_DTINET)) -ne 0 ] && echo "<li>VPN: tunnel subnet range changed from $_OTINET to $_TINET since $SC_NAME was upreared!</li>"
    [ $((_CK&CK_OIPT)) -ne 0 ] &&   echo "<li>iptables: $SC_NAME rules were UNSUCCESSFULLY (re)set during last uprear!</li>"
    [ $((_CK&CK_DIPT)) -ne 0 ] &&   echo "<li>iptables: current $SC_NAME rules were modified since last uprear!</li>"
    
    if [ $((_CK&CK_LOG)) -eq $CK_LOG ]; then echo "<li>logd: the log daemon is running but was not started from the shield!</li>"
    elif [ $((_CK&CK_DLOGD)) -ne 0 ]; then   echo "<li>logd: log daemon was started but is not running!</li>"
    fi
    echo '</ul>'
  fi
  
  echo '<h3 class="more collapsibleList">Setting status</h3>'
  echo '<input type="checkbox" id="setting-status" /><label for="setting-status">Setting status</label>'
  echo '<ul>'
  [ $((_CK&CK_FWS)) -ne 0 ] &&   echo "<li>Script firewall-start.sh is set for $SC_NAME.</li>"
  case $((_CK&CK_PM)) in $CK_PM) echo "<li>Script post-mount.sh is set for $SC_NAME.</li>" ;;
                       $CK_PMND) echo "<li>Ignoring post-mount.sh script ($SC_NAME is on internal memory).</li>" ;;
  esac
  echo '</ul>'
  
  echo '<h3 class="more collapsibleList">Directives generation times</h3>'
  echo '<input type="checkbox" id="generation-status" /><label for="generation-status">Directives generation times</label>'
  echo '<ul>'
  _gentimeforlist() { [ -e "$1" ] && echo "<li>$2: $(/bin/date +'%Y-%m-%d %X' -r "$1")</li>"; }
  [ -r "$SRC_BL_CACHE" ] && echo "<li>Sources cache list latest update: $(/bin/date +'%Y-%m-%d %X' -r "$SRC_BL_CACHE")</li>"
  _gentimeforlist "$ALL_BL_FILE" "Global block list"
  _gentimeforlist "$WAN_BL_FILE" "WAN specific block list"
  _gentimeforlist "$TUN_BL_FILE" "VPN specific block list"
  _gentimeforlist "$ALL_WL_FILE" "Global bypass list"
  _gentimeforlist "$WAN_WL_FILE" "WAN specific bypass list"
  _gentimeforlist "$TUN_WL_FILE" "VPN specific bypass list"
  echo '</ul>'

  if [ -r "$INFO_FILE" ]; then echo '<h3 class="more collapsibleList">Uprear information</h3>'
  echo '<input type="checkbox" id="uprear-info" /><label for="uprear-info">Uprear information</label>'
  echo '<ul>'
    case "$_OFROM" in
      $INFO_FROM_SC)  FROM="$SC_NAME script" ;;
      $INFO_FROM_PM)  FROM="post-mount.sh" ;;
      $INFO_FROM_FWS) FROM="firewall-start.sh" ;;
    esac
    echo "<li>Shield was upreared from: $FROM @ $(/bin/date +'%Y-%m-%d %X' -r $INFO_FILE)</li>"
    _parse_odir() { case "$(($1&INFO_DIR__MASK))" in
      "$INFO_DIR__SAME") echo "<li>ipset: latest $2 was already loaded and conform with directives.</li>";;
      "$INFO_DIR__KEEP") echo "<li>ipset: loaded $2 was kept since no directives file could be found for it!</li>";;
      "$INFO_DIR__LOAD") echo "<li>ipset: $2 was loaded from file directives.</li>";;
      "$INFO_DIR__SWAP") echo "<li>ipset: $2 was reloaded from directives.</li>";;
      "$INFO_DIR__DEST") echo "<li>ipset: $2 was unloaded.</li>";;
      "$INFO_DIR__MISS") :;;
    esac; }
    _parse_odir $((_ODIR>>(INFO_DIR_ALL+INFO_DIR_BL))) 'global block list'
    _parse_odir $((_ODIR>>(INFO_DIR_WAN+INFO_DIR_BL))) 'WAN specific block list'
    _parse_odir $((_ODIR>>(INFO_DIR_TUN+INFO_DIR_BL))) 'VPN specific block list'
    _parse_odir $((_ODIR>>(INFO_DIR_ALL+INFO_DIR_WL))) 'global bypass list'
    _parse_odir $((_ODIR>>(INFO_DIR_WAN+INFO_DIR_WL))) 'WAN specific bypass list'
    _parse_odir $((_ODIR>>(INFO_DIR_TUN+INFO_DIR_WL))) 'VPN specific bypass list'
    if  [ $((_OIPT&INFO_IPT_KEEP)) -ne 0 ]; then echo -n "<li>iptables: rules were already set with:"
    elif [ $((_OIPT&INFO_IPT_RUN)) -ne 0 ]; then echo -n "<li>iptables: rules were (re)set with:"
    else echo -n "<li>iptables: rules were UNSUCCESSFULLY (re)set with:"
    fi
    # _ODNA
    _AND=''
    [ $((_ODNA&DNA_ABL)) -ne 0 ] && echo -n " global block" && _AND=','
    [ $((_ODNA&DNA_AWL)) -ne 0 ] && echo -n "$_AND global bypass" && _AND=','
    [ $((_ODNA&DNA_WBW)) -ne 0 ] && echo -n "$_AND WAN network bypass" && _AND=','
    [ $((_ODNA&DNA_WBL)) -ne 0 ] && echo -n "$_AND WAN block" && _AND=','
    [ $((_ODNA&DNA_WWL)) -ne 0 ] && echo -n "$_AND WAN bypass" && _AND=','
    [ $((_ODNA&DNA_TBW)) -ne 0 ] && echo -n "$_AND VPN network bypass" && _AND=','
    [ $((_ODNA&DNA_TBL)) -ne 0 ] && echo -n "$_AND VPN block" && _AND=','
    [ $((_ODNA&DNA_TWL)) -ne 0 ] && echo -n "$_AND VPN bypass"
    [ $((_ODNA&DNA_LOG)) -ne 0 ] && echo -n "$_AND logging"
    echo '.</li>'
    # _OLOGD
    case "$_OLOGD" in
      $INFO_LOGD_KEEP_OFF) echo '<li>log daemon: was already off.</li>';;
      $INFO_LOGD_KEEP_ON)  echo '<li>log daemon: was already on.</li>';;
      $INFO_LOGD_STOPPED)  echo '<li>log daemon: was turned off.</li>';;
      $INFO_LOGD_STARTED)  echo '<li>log daemon: was turned on.</li>';;
    esac
    echo '</ul>'
  fi
} 2>/dev/null

debug() {
  /opt/bolemo/scripts/aegis debug|/usr/bin/awk '{gsub("[[:cntrl:]]\[[0-9;]+m","\0",$0)} !/^[[:space:]]*$/{print;system("")}'
}

info() {
  aegis_env
  _JSON="{\"version\":\"$SC_VERS\""
  $EXT_DRIVE && _JSON="$_JSON, \"location\":\"external\"" || _JSON="$_JSON, \"location\":\"internal\""
  SC_LAST_VERS="$(last_avail_version)";
  if [ "$SC_LAST_VERS" ]; then
    if [ "$SC_VERS" = "$SC_LAST_VERS" ]; then _VSTAT=0
    else VERS_ARRAY="$(echo -e "$SC_VERS\n$SC_LAST_VERS")"; SORT_ARRAY="$(echo "$VERS_ARRAY"|/usr/bin/awk -F. '{o=$0;if(!gsub(/b/,".0")){$0=$0".999"};a[sprintf("%d%03d%03d%03d\n",$1,$2,$3,$4)]=o;} END {for(i in a){printf("%d:%s\n",i,a[i])|"/usr/bin/sort -n|/usr/bin/cut -d: -f2"}}')"
      if [ "$VERS_ARRAY" = "$SORT_ARRAY" ]; then _VSTAT=1
      else _VSTAT=2; fi
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
    'upgrade'*) _CMD="aegis _upgrade" ;;
    'up'*) _CMD="aegis _up$_LOG" ;;
    'refresh_custom'*) _CMD="aegis _refresh -custom-only$_LOG" ;;
    'refresh'*) _CMD="aegis _refresh$_LOG" ;;
    'down'*) _CMD="aegis _down" ;;
    'unset'*) _CMD="aegis _unset" ;;
  esac
  [ -z "${ARG##*-*}" ] && _ARG2="${ARG#*-}"
  /opt/bolemo/scripts/$_CMD|/usr/bin/awk '{gsub("[[:cntrl:]]\[[0-9;]+m","\0",$0)} !/^[[:space:]]*$/{print;system("")}'
  if [ $? = 0 ]; then [ -z "$_ARG2" ] && echo "Success!"; else echo "A problem was encountered."; exit 1; fi;
  if [ $_ARG2 ]; then ARG="$_ARG2"; _ARG2=''; command; fi;
}

# LOG
_LF=/var/log/log-aegis

_getLog() {
  _MAX=$($wcUCI get aegis_web.log.len)
  _ST=$($wcUCI get aegis_web.log.pos)

/usr/bin/awk -F: '
function getProts(){fn="'"$wcPRT_PTH"'";while((getline l<fn)>0){split(l,f,",");prots[f[1]]=f[3];prots[f[2]]=f[3]};close(fn)}
function protoname(ptl){return "<log-ptl value=\""ptl"\">"prots[ptl]"</log-ptl>"}
BEGIN {getProts()}
{ts[++c]=$1;uts[c]=($1$2);l[c]=$0}
END {
  if (uts[c]) {system("'"$wcUCI"' set aegis_web.log.pos="uts[c++])}
  dir[">"]="incoming";dir["<"]="outgoing"
  itf["WAN"]=" wan";itf["VPN"]=" vpn"
  adt["ROUTER"]=" rtr";adt["BROADCAST"]=" bdc";adt["LAN"]=" lan"
  min=(NR>'$_MAX')?NR-'$_MAX':0;while(--c>min && uts[c]>'$_ST'){
    split(l[c],f," ")
    n=split(f[6],rem,":");rpt=(n==2)?("<log-pt>"rem[2]"</log-pt>"):""
    n=split(f[9],loc,":");lpt=(n==2)?("<log-pt>"loc[2]"</log-pt>"):""
    n=split(f[8],dst,",");lnm=(n==2)?dst[2]:dst[1]
    print "<p class=\"new "dir[f[7]] itf[f[5]] adt[dst[1]]"\"><log-ts>"strftime("%F %T",f[2])"</log-ts>"protoname(f[4])"<log-if></log-if><log-rem><log-rip>"rem[1]"</log-rip>"rpt"</log-rem><log-dir></log-dir><log-lnm>"lnm"</log-lnm><log-loc><log-lip>"loc[1]"</log-lip>"lpt"</log-loc></p>"
  }
}' $_LF
}

log() {
#  aegis_env
  [ "$(cat /module_name)" = "RBR50" ] && MAX=150 || MAX=300
  case $ARG in
    ''|*[!0-9]*) LEN=100 ;;
    *) if [ $ARG -lt 1 ]; then LEN=1
       elif [ $ARG -gt $MAX ]; then LEN=$MAX
       else LEN=$ARG
       fi ;;
  esac
  $wcUCI set aegis_web.log.len=$LEN
  $wcUCI set aegis_web.log.pos=0
  _getLog
}

refreshLog() {
  _getLog
}

stats() {
  SR=false SL=false RG=false LG=false
  IFS='-' set -- $ARG ; set -- $(unset IFS; echo $1); unset IFS
  case $1 in
    in)  DF='($7=="<"){next}' A_DIR='kdir=$7';;
    out) DF='($7==">"){next}' A_DIR='kdir=$7';;
    all) DF='' A_DIR='kdir=$7';;
    no) DF='';;
  esac; shift
  case $1 in
    wan) IF='($5!="WAN"){next}' A_IFACE='kiface=$5;siface="<stats-iface class=\"wan\">WAN</stats-iface>"' RG=true;;
    vpn) IF='($5!="VPN"){next}' A_IFACE='kiface=$5;siface="<stats-iface class=\"vpn\">VPN</stats-iface>"' RG=true;;
    all) IF='' A_IFACE='kiface=$5;siface="<stats-iface class=\""itf[$5]"\">"$5"</stats-iface>"' RG=true;;
    no) IF='';;
  esac; shift
  if [ "$1" = 'proto' ]; then shift
    A_PROTO='kproto=$4;sproto=protoname(kproto)'
  fi
  if [ "$1" = 'rip' ]; then shift
    A_RIP='krip=r[1];srip="<stats-rip>"krip"</stats-rip>"' SR=true RG=true
  fi
  if [ "$1" = 'rpt' ]; then shift
 #   A_RPT='pre=((krip)?":":" PORT ");if(rn==2){krpt=r[2];srpt=(pre"<stats-pt>"r[2]"</stats-pt>")}else{krpt="";srpt=""}' SR=true RG=true
    A_RPT='if(rn==2){krpt=r[2];srpt=("<stats-pt>"r[2]"</stats-pt>")}else{krpt="";srpt=""}' SR=true RG=true
  fi
  if [ "$1" = 'loc' ]; then shift
    A_LOC='kln=split($8,kla,",");kloc=$8;sloc="<stats-loc class=\""adt[kla[1]]"\">"((kln>1)?(kla[2]):($8))"</stats-loc>"' LG=true
  fi
  if [ "$1" = 'lip' ]; then shift
    A_LIP='klip=l[1];slip="<stats-lip>"klip"</stats-lip>"' SL=true LG=true
  fi
  if [ "$1" = 'lpt' ]; then shift
 #   A_LPT='pre=((klip)?":":" PORT ");if(ln==2){klpt=l[2];slpt=(pre"<stats-pt>"l[2]"</stats-pt>")}else{klpt="";slpt=""}' SL=true LG=true
    A_LPT='if(ln==2){klpt=l[2];slpt=("<stats-pt>"l[2]"</stats-pt>")}else{klpt="";slpt=""}' SL=true LG=true
  fi
  $SR && PK1='rn=split($6,r,":")'; $RG && PK1=$PK1';rg=1'
  $SL && PK2='ln=split($9,l,":")'; $LG && PK2=$PK2';lg=1'
  /usr/bin/awk '
function getProts(){fn="'"$wcPRT_PTH"'";while((getline l<fn)>0){split(l,f,",");prots[f[1]]=f[3];prots[f[2]]=f[3]};close(fn)}
function protoname(ptl){return "<stats-ptl value=\""ptl"\">"prots[ptl]"</stats-ptl>"}
BEGIN {
  st=(systime()-86400)
  getProts()
  itf["WAN"]="wan";itf["VPN"]="vpn"
  adt["ROUTER"]="rtr";adt["BROADCAST"]="bdc";adt["LAN"]="lan"
}
($2<st){next}
(!st){st=$2}
{tnr++}
'$DF$IF'
{
  '"$PK1"'
  '"$PK2"'
  '"$A_PROTO"'
  '"$A_IFACE"'
  '"$A_RIP"'
  '"$A_RPT"'
  '"$A_DIR"'
  '"$A_LOC"'
  '"$A_LIP"'
  '"$A_LPT"'
  if (kdir==">") {
    str="<stats-dir class=\"incoming\">INCOMING</stats-dir>" sproto " HIT(S) " ((rg)?("<stats-ext>FROM</stats-ext>" siface " " srip srpt):"") ((lg)?("<stats-int>TO</stats-int>" sloc " " slip slpt):"")
  } else if(kdir=="<") {
    str="<stats-dir class=\"outgoing\">OUTGOING</stats-dir>" sproto " HIT(S) " ((lg)?("<stats-int>FROM</stats-int>" sloc " " slip slpt):"") ((rg)?("<stats-ext>TO</stats-ext>" siface " " srip srpt):"")
  } else if(rg && lg) {
    str=sproto" HIT(S) <stats-ntl>BETWEEN</stats-ntl>" siface " " srip srpt "<stats-ntl>AND</stats-ntl>" sloc " " slip slpt
  } else if(rg || lg) {
    str=sproto" HIT(S) <stats-ntl>INVOLVING</stats-ntl>" siface " " srip srpt " " sloc " " slip slpt
  } else {
    str=sproto" HIT(S)"
  }
  act[kproto,kiface,krip,krpt,kdir,kloc,klip,klpt]++
  ast[kproto,kiface,krip,krpt,kdir,kloc,klip,klpt]=str
  nfr++
}
END {
  for(i in act){print act[i] " " ast[i] "<br />"}
}' "$_LF" | /usr/bin/sort -rnk1 | /usr/bin/head -n100
}

refreshDev() {
  /usr/bin/killall -10 net-scan # Refreshing device list
}

checkIp() {
  aegis_env
  IP="$ARG"
  if /usr/bin/traceroute -q1 -m1 -w1 -i $WAN_IF $IP 38 2>&1 >/dev/null | /bin/grep -qF 'sendto: Operation not permitted'
    then echo "IP address $IP is blocked by the router for WAN interface.<br />"
    else echo "IP address $IP is not blocked by the router for WAN interface.<br />"
  fi
  if [ "$TUN_IF" ]; then
    if /usr/bin/traceroute -q1 -m1 -w1 -i $TUN_IF $IP 38 2>&1 >/dev/null | /bin/grep -qF 'sendto: Operation not permitted'
      then echo "IP address $IP is blocked by the router for VPN tunnel.<br />"
      else echo "IP address $IP is not blocked by the router for VPN tunnel.<br />"
    fi
  fi
  $IPS_BIN -L -n|/bin/grep -F -- "$SC_ABR"|while read _SET; do case "$_SET" in
    "$IPSET_ALL_BL_NAME") $IPS_BIN -q test $IPSET_ALL_BL_NAME $IP && echo "IP address $IP is in $SC_NAME global block directives.<br />" ;;
    "$IPSET_ALL_WL_NAME") $IPS_BIN -q test $IPSET_ALL_WL_NAME $IP && echo "IP address $IP is in $SC_NAME global bypass directives.<br />" ;;
    "$IPSET_WAN_BL_NAME") $IPS_BIN -q test $IPSET_WAN_BL_NAME $IP && echo "IP address $IP is in $SC_NAME WAN specific block directives.<br />" ;;
    "$IPSET_WAN_WL_NAME") $IPS_BIN -q test $IPSET_WAN_WL_NAME $IP && echo "IP address $IP is in $SC_NAME WAN specific bypass directives.<br />" ;;
    "$IPSET_TUN_BL_NAME") $IPS_BIN -q test $IPSET_TUN_BL_NAME $IP && echo "IP address $IP is in $SC_NAME VPN specific block directives.<br />" ;;
    "$IPSET_TUN_WL_NAME") $IPS_BIN -q test $IPSET_TUN_WL_NAME $IP && echo "IP address $IP is in $SC_NAME VPN specific bypass directives.<br />" ;;
  esac; done
  ip_in_if_inet $IP $WAN_IF && echo "IP address $IP is in the WAN network range ($(inet_for_if $WAN_IF)).<br />"
  ip_in_if_inet $IP $TUN_IF && echo "IP address $IP is in the VPN network range ($(inet_for_if $TUN_IF)).<br />"
  echo "---<br />"
}

_getList() {
  case "$ARG" in
    src) _LIST="$SRC_LIST";;
    abl) _LIST="$(echo "$CUST_ALL_BL_FILE"|sed 's/\*//')";;
    awl) _LIST="$(echo "$CUST_ALL_WL_FILE"|sed 's/\*//')";;
    wbl) _LIST="$(echo "$CUST_WAN_BL_FILE"|sed 's/\*//')";;
    wwl) _LIST="$(echo "$CUST_WAN_WL_FILE"|sed 's/\*//')";;
    tbl) _LIST="$(echo "$CUST_TUN_BL_FILE"|sed 's/\*//')";;
    twl) _LIST="$(echo "$CUST_TUN_WL_FILE"|sed 's/\*//')";;
  esac
}

printList() {
  aegis_env
  _getList
  if test -s "$_LIST"
    then echo -n "<u>File:</u> $_LIST, <u>last modified:</u> "; date -r "$_LIST"; /bin/sed '/^[[:space:]]*$/d' "$_LIST"
    else echo "<u>File:</u> $_LIST does not exist or is empty."
  fi
}

saveList() {
  aegis_env
  _READ=`/bin/sed '/^[[:space:]]*$/d'`
  _getList
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
  debug) debug;;
  command) command;;
  log) log;;
  refresh_log) refreshLog;;
  stats) stats;;
  refresh_dev) refreshDev;;
  check) checkIp;;
  print_list) printList; exit;;
  save_list) saveList; exit;;
  proto_info) protoInfo;;
# called from aegis only
  uninstall) uninstall; exit;;
esac

# lighttpd empty response fix:
echo ' '

exit 0
