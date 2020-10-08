#!/bin/sh
eval "$(aegis _env)"

status() {
  set -- $(/opt/bolemo/scripts/aegis _status)
  eval "_STAT=$1; WAN_IF=$2; TUN_IF=$3; BL_NB=$4; WL_NB=$5"
  _CK=$((_STAT&CK_MASK)); _PB=$(((_STAT>>12)&PB_MASK)); _WN=$(((_STAT>>25)&WN_MASK))
  echo '<h2>Status:</h2>'
  echo '<ul>'
  if [ $((_CK+_PB)) -eq 0 ]; then
    echo "<li>'$SC_NAME' is not active; Settings are clean.</li>"
  elif [ $_CK -ne 0 ] && [ $_PB -eq 0 ]; then
    echo -n "<li>'$SC_NAME' is set and active"
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] && echo -n " for WAN interface ($WAN_IF)"
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] && echo -n " and VPN tunnel ($TUN_IF)"
    echo -ne ".</li>\n<li>Filtering $BL_NB IP adresses.</li>"
    [ $((_CK&CK_IPT_WL)) -ne 0 ] && echo "<li>Bypassing $WL_NB IP adresses.</li>"
  else
    echo "<li><strong>Something is not right!</strong></li>"
  fi
  echo '</ul>'
  
  if [ $_PB -ne 0 ]; then
    echo '<h2>Errors:</h2>'
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
    echo '<h2>Warnings:</h2>'
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
 
  [ "$VERBOSE" ] || return 0
  echo -ne '\033[1;36mDetailed status:\033[0m'; [ "$VERBOSE" -ge 2 ] && echo " (CODE: $_CK)" || echo ''
  echo "- Active WAN interface is '$WAN_IF'."
  [ "$TUN_IF" ] && echo "- Active VPN tunnel is '$TUN_IF'." || echo "- no VPN tunnel found."
  # dates
  echo "- Actual router time: $(/bin/date +'%Y-%m-%d %X')"
  [ -e "$BL_FILE" ] && echo "- Blocklist generation time: $(/bin/date +'%Y-%m-%d %X' -r $BL_FILE)"
  [ -e "$WL_FILE" ] && echo "- Whitelist generation time: $(/bin/date +'%Y-%m-%d %X' -r $WL_FILE)"
  if [ $_CK -ne 0 ]; then
    [ $((_CK&CK_FWS)) -ne 0 ] &&      echo "- 'firewall-start.sh' is set for $SC_NAME."
    [ $((_CK&CK_PM)) -ne 0 ] &&       echo "- 'post-mount.sh' is set for $SC_NAME."
    [ $((_CK&CK_IPS_BL)) -ne 0 ] &&   echo "- ipset: blocklist is set."
    [ $((_CK&CK_IPS_WL)) -ne 0 ] &&   echo "- ipset: whitelist is set."
    [ $((_CK&CK_WG_IN_BL)) -ne 0 ] && echo "- ipset: WAN gateway is in blocklist."
    [ $((_CK&CK_WG_BP)) -ne 0 ] &&    echo "- ipset: WAN gateway bypass is set."
    [ $((_CK&CK_IPT_CH)) -ne 0 ] &&   echo "- iptables: engine chains are set."
    [ $((_CK&CK_IPT_WG)) -ne 0 ] &&   echo "- iptables: WAN gateway bypass rules are set."
    [ $((_CK&CK_IPT_WL)) -ne 0 ] &&   echo "- iptables: whitelist rules are set."
    [ $((_CK&CK_IPT_LOG)) -ne 0 ] &&  echo "- iptables: $SC_NAME logging is on."
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] &&  echo "- iptables: VPN tunnel IFO rules are set."
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] &&  echo "- iptables: WAN interface IFO rules are set."
  fi
  
  [ "$VERBOSE" -lt 2 ] && return 0
  # Status file
  echo -ne "\033[1;36m'$SC_NAME' engine last launch report:\033[0m"
  if [ -r "$INFO_FILE" ]; then
    read INFO INFO_WAN INFO_TUN<"$INFO_FILE"
    INFO_FROM=$((INFO&INFO_FROM_MASK))
    INFO_IPS=$(((INFO>>2)&INFO_IPS_MASK))
    INFO_IPT=$(((INFO>>10)&INFO_IPT_MASK))
    echo " (CODE: $INFO_FROM-$INFO_IPS-$INFO_IPT)"
    case "$INFO_FROM" in
      $INFO_FROM_SC) FROM="$SC_NAME script" ;;
      $INFO_FROM_PM) FROM="post-mount.sh" ;;
      $INFO_FROM_FWS) FROM="firewall-start.sh" ;;
    esac
    echo "- engine was launched from: $FROM @ $(/bin/date +'%Y-%m-%d %X' -r $INFO_FILE)"
    echo "- WAN interface was '$INFO_WAN'."
    [ "$INFO_TUN" ] && echo "- VPN tunnel was '$INFO_TUN'." || echo '- No VPN tunnel was found.'
    case $((INFO_IPS&INFO_IPS_BL_MASK)) in
      0) echo '! blocklist file was not found!' ;;
      $INFO_IPS_BL_SAME) echo '- ipset: blocklist was already set and identical to file.' ;;
      $INFO_IPS_BL_MISS) echo '- ipset: blocklist file was not found! The one already set was kept.' ;;
      $INFO_IPS_BL_LOAD) echo '- ipset: blocklist was set from file.' ;;
    esac
    case $((INFO_IPS&INFO_IPS_WL_MASK)) in
      0) echo '- no whitelist file was found.' ;;
      $((INFO_IPS_WL_SAME+INFO_IPS_WL_KEEP))) echo '- ipset: whitelist was already set and identical to file.' ;;
      $INFO_IPS_WL_KEEP) echo '- ipset: whitelist was kept.' ;;
      $INFO_IPS_WL_LOAD) echo '- ipset: whitelist was set from file.' ;;
      $INFO_IPS_WL_SWAP) echo '- ipset: whitelist was updated from file.' ;;
      $INFO_IPS_WL_DEL) echo '- ipset: whitelist was unset.' ;;
    esac
    case $((INFO_IPS&INFO_IPS_WG_MASK)) in
      0) echo '- WAN gateway was not in blocklist set and therefore was not bypassed.' ;;
      $INFO_IPS_WG_ADD) echo '- ipset: WAN gateway was in blocklist and was bypassed.' ;;
      $INFO_IPS_WG_KEEP) echo '- ipset: WAN gateway bypass was already properly set.' ;;
      $INFO_IPS_WG_DEL) echo '- ipset: WAN gateway bypass was unset.' ;;
    esac
    if [ $((INFO_IPT & INFO_IPT_SRC_KEEP)) -eq 0 ]
      then echo "- iptables: engine inbound chain was set."
      else echo "- iptables: engine inbound chain was already set."
    fi
    if [ $((INFO_IPT & INFO_IPT_DST_KEEP)) -eq 0 ]
      then echo '- iptables: engine outbound chain was set.'
      else echo '- iptables: engine outbound chain was already set.'
    fi
    if [ $((INFO_IPT & INFO_IPT_WG)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_WG_SRC_NEW)) -ne 0 ]
        then echo '- iptables: inbound WAN gateway bypass rules were set.'
        else echo '- iptables: inbound WAN gateway bypass rules were kept.'
      fi
      if [ $((INFO_IPT & INFO_IPT_WG_DST_NEW)) -ne 0 ]
        then echo '- iptables: outbound WAN gateway bypass rules were set.'
        else echo '- iptables: outbound WAN gateway bypass rules were kept.'
      fi
    fi
    if [ $((INFO_IPT & INFO_IPT_WL)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_WL_SRC_NEW)) -ne 0 ]
        then echo '- iptables: inbound whitelist rules were set.'
        else echo '- iptables: inbound whitelist rules were kept.'
      fi
      if [ $((INFO_IPT & INFO_IPT_WL_DST_NEW)) -ne 0 ]
        then echo '- iptables: outbound whitelist rules were set.'
        else echo '- iptables: outbound whitelist rules were kept.'
      fi
    fi
    if [ $((INFO_IPT & INFO_IPT_LOG)) -ne 0 ]; then
      if [ $((INFO_IPT & INFO_IPT_LOG_SRC_NEW)) -ne 0 ]
        then echo '- iptables: inbound logging rules were set.'
        else echo '- iptables: inbound logging rules were kept.'
      fi
      if [ $((INFO_IPT & INFO_IPT_LOG_DST_NEW)) -ne 0 ]
        then echo '- iptables: outbound logging rules were set.'
        else echo '- iptables: outbound logging rules were kept.'
      fi
    fi
    
    [ $((INFO_IPT & INFO_IPT_IFO_PBM)) -ne 0 ] && echo '- iptables: some irrelevant IFO rules had to be removed.'
    if [ $((INFO_IPT & INFO_IPT_WAN_PBM)) -eq $INFO_IPT_WAN_PBM ]; then echo '- iptables: WAN interface IFO rules had to be reset.'
    elif [ $((INFO_IPT & INFO_IPT_WAN_NEW)) -ne 0 ]; then echo '- iptables: WAN interface IFO rules were set.'
    elif [ $((INFO_IPT & INFO_IPT_WAN_KEEP)) -ne 0 ]; then echo '- iptables: WAN interface IFO rules were kept.'
    fi
    if [ $((INFO_IPT & INFO_IPT_TUN_PBM)) -eq $INFO_IPT_TUN_PBM ]; then echo '- iptables: VPN tunnel IFO rules had to be reset.'
    elif [ $((INFO_IPT & INFO_IPT_TUN_NEW)) -ne 0 ]; then echo '- iptables: VPN tunnel IFO rules were set.'
    elif [ $((INFO_IPT & INFO_IPT_TUN_KEEP)) -ne 0 ]; then echo '- iptables: VPN tunnel IFO rules were kept.'
    fi
    
    echo -ne "\033[0m"
  else
    echo -e '\n- No status file found.'
  fi
  
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
