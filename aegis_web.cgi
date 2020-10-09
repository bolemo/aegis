#!/bin/sh
eval "$(aegis _env)"

status() {
  set -- $(/opt/bolemo/scripts/aegis _status)
  eval "_STAT=$1; WAN_IF=$2; TUN_IF=$3; BL_NB=$4; WL_NB=$5"
  _CK=$((_STAT&CK_MASK)); _PB=$(((_STAT>>12)&PB_MASK)); _WN=$(((_STAT>>25)&WN_MASK))
  echo '<h2>Status:</h2>'
  echo '<ul>'
  if [ $((_CK+_PB)) -eq 0 ]; then
    echo "<li>Aegis is not active; Settings are clean.</li>"
  elif [ $_CK -ne 0 ] && [ $_PB -eq 0 ]; then
    echo -n "<li>Aegis is set and active"
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] && echo -n " for WAN interface ($WAN_IF)"
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] && echo -n " and VPN tunnel ($TUN_IF)"
    echo -ne ".</li>\n<li>Filtering $BL_NB IP adresses.</li>"
    [ $((_CK&CK_IPT_WL)) -ne 0 ] && echo "<li>Bypassing $WL_NB IP adresses.</li>"
  else
    echo "<li><strong>Something is not right!</strong></li>"
  fi
  echo '</ul>'
  
  if [ $_PB -ne 0 ]; then
    echo '<h3>Errors:</h3>'
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
    echo '<h3>Warnings:</h3>'
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
 
  echo '<h3>Detailed status:</h3>'
  echo '<ul>'
  echo "<li>Active WAN interface is '$WAN_IF'.</li>"
  [ "$TUN_IF" ] && echo "<li>Active VPN tunnel is '$TUN_IF'.</li>" || echo "<li>no VPN tunnel found.</li>"
  # dates
  echo "<li>Actual router time: $(/bin/date +'%Y-%m-%d %X')</li>"
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
  echo '<h3>Aegis engine last launch report:</h3>'
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
  
  [ "$VERBOSE" -lt 3 ] && return 0
  
  if [ $((_CK+_PB)) -ne 0 ]; then
    echo -e "\033[1;36miptables:\033[0m"
    [ -z "$_IPT" ] && echo "- no $SC_NAME rules are set." || echo "$_IPT"|/bin/sed 's/^/- iptables /'
    ipset -L -n|/bin/grep -F -- "$SC_ABR"|while read _SET; do
      case "$_SET" in
        "$IPSET_BL_NAME") _NAME='blocklist' ;;
        "$IPSET_WL_NAME") _NAME='whitelist' ;;
        "$IPSET_WG_NAME") _NAME='wan gateway bypass' ;;
        *) _NAME="$_SET" ;;
      esac
      echo -e "\033[1;36mipset '$_NAME':\033[0m"
      ipset -L -t $_SET|/bin/sed 's/^/- /'
    done
  fi
}

status
