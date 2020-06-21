#!/bin/sh

# STATUS VARS
CK_FWS=1             # CK PB
CK_PM=2              # CK PB
CK_IPS_BL=4          # CK PB
CK_IPS_WL=8          # CK PB
CK_WG_IN_BL=16       # CK ..
PB_WG_SNE=16         # .. PB
CK_WG_BP=32          # CK PB
CK_IPT_CH=64         # CK PB
CK_IPT_WG=128        # CK PB
CK_IPT_WL=256        # CK PB
CK_IPT_LOG=512       # CK ..
PB_IPT_IFO=512       # .. PB
CK_IPT_TUN=1024      # CK PB
CK_IPT_WAN=2048      # CK PB
PB_IPT_WAN_MISS=4096 # .. PB
WN_BL_FILE_DIFF=1   # . . . . _ x
WN_BL_FILE_MISS=2   # . . . . x _
WN_BL_FILE_NTLD=3   # . . . . x x
WN_WL_FILE_DIFF=4   # . . _ x . .
WN_WL_FILE_MISS=8   # . . x _ . .
WN_WL_FILE_NTLD=12  # . . x x . .
WN_TUN_MISS=16      # . x . . . .
WN_LOG_DIFF=32      # x . . . . .
CK_MASK=4095 #12 bits
PB_MASK=8191 #13 bits
WN_MASK=63   #6 bits

# INFO FROM (2 bits)
INFO_FROM_MASK=3
INFO_FROM_FWS=1       # _ x
INFO_FROM_PM=2        # x _
INFO_FROM_SC=3        # x x

# INFO IPSET (8 bits)
INFO_IPS_MASK=255
                      # . . . . . . _ _  PBM, BL FILE MISSING
INFO_IPS_BL_SAME=1    # . . . . . . _ x  KEEP
INFO_IPS_BL_MISS=2    # . . . . . . x _  KEEP
INFO_IPS_BL_LOAD=3    # . . . . . . x x
INFO_IPS_BL_MASK=3    # . . . . . . x x

INFO_IPS_WL_SAME=4    # . . . _ . x . .  SAME => KEEP
INFO_IPS_WL_KEEP=8    # . . . _ x . . .  KEEP
INFO_IPS_WL_LOAD=16   # . . . x _ _ . .
INFO_IPS_WL_SWAP=20   # . . . x _ x . . = RELOAD
INFO_IPS_WL_DEL=24    # . . . x x _ . . => was there, was deleted
                      # . . . _ _ _ . . => was not there, was not loaded
INFO_IPS_WL_MASK=28   # . . . x x x . .

INFO_IPS_WG_ADD=32    # _ _ x . . . . . => IN BL
INFO_IPS_WG_KEEP=64   # _ x _ . . . . . => IN BK
INFO_IPS_WG_DEL=128   # x _ _ . . . . .
INFO_IPS_WG_MASK=224  # x x x . . . . .
                      # _ _ _ . . . . . => was not there, was not loaded

# INFO IPTABLES (16 bits)
INFO_IPT_MASK=65535
INFO_IPT_SRC_KEEP=1        # . . . . . . . . . . . . . . . x (or NEW)
INFO_IPT_DST_KEEP=2        # . . . . . . . . . . . . . . x . (or NEW)
INFO_IPT_WG=4              # . . . . . . . . . . . . . x . .
INFO_IPT_WG_SRC_NEW=8      # . . . . . . . . . . . . x . . . (or KEEP)
INFO_IPT_WG_DST_NEW=16     # . . . . . . . . . . . x . . . . (or KEEP)
INFO_IPT_WL=32             # . . . . . . . . . . x . . . . .
INFO_IPT_WL_SRC_NEW=64     # . . . . . . . . . x . . . . . . (or KEEP)
INFO_IPT_WL_DST_NEW=128    # . . . . . . . . x . . . . . . . (or KEEP)
INFO_IPT_LOG=256           # . . . . . . . x . . . . . . . .
INFO_IPT_LOG_SRC_NEW=512   # . . . . . . x . . . . . . . . . (or KEEP)
INFO_IPT_LOG_DST_NEW=1024  # . . . . . x . . . . . . . . . . (or KEEP)


INFO_IPT_IF_NEW=1  # _ x
INFO_IPT_IF_KEEP=2 # x _
INFO_IPT_IF_PBM=3  # x x

INFO_IPT_WAN_SHIFT=11
INFO_IPT_WAN_NEW=2048      # . . . _ x . . . . . . . . . . .
INFO_IPT_WAN_KEEP=4096     # . . . x _ . . . . . . . . . . .
INFO_IPT_WAN_PBM=6144      # . . . x x . . . . . . . . . . .

INFO_IPT_TUN_SHIFT=13
INFO_IPT_TUN_NEW=8192      # . _ x . . . . . . . . . . . . .
INFO_IPT_TUN_KEEP=16384    # . x _ . . . . . . . . . . . . .
INFO_IPT_TUN_PBM=24576     # . x x . . . . . . . . . . . . .

INFO_IPT_IFO_PBM=32768     # x . . . . . . . . . . . . . . .

status() {
  /opt/bolemo/scripts/aegis _status|read WAN_IF TUN_IF
  _STAT=$?; _CK=$((_STAT&CK_MASK)); _PB=$(((_STAT>>12)&PB_MASK)); _WN=$(((_STAT>>25)&WN_MASK))
  echo -e '\033[1;36mStatus:\033[0m'
  if [ $((_CK+_PB)) -eq 0 ]; then
    echo "- '$SC_NAME' is not active; Settings are clean."
  elif [ $_CK -ne 0 ] && [ $_PB -eq 0 ]; then
    echo -n "- '$SC_NAME' is set and active"
    [ $((_CK&CK_IPT_WAN)) -ne 0 ] && echo -n " for WAN interface ($WAN_IF)"
    [ $((_CK&CK_IPT_TUN)) -ne 0 ] && echo -n " and VPN tunnel ($TUN_IF)"
    echo -e ".\n- Filtering $(count_ip_in_ipset $IPSET_BL_NAME) IP adresses."
    [ $((_CK&CK_IPT_WL)) -ne 0 ] && echo "- Bypassing $(count_ip_in_ipset $IPSET_WL_NAME) IP adresses."
  else
    _RETVAL=2
    echo -e "- \033[1;31mSomething is not right!\033[0m"
  fi
  
  if [ $_PB -ne 0 ]; then
    echo -ne '\033[1;31mErrors:\033[0m'; [ "$VERBOSE" -ge 2 ] && echo " (CODE: $_PB)" || echo ''
    [ $((_PB&CK_FWS)) -ne 0 ] &&     echo -e "\033[31m- 'firewall-start.sh' is not set properly for $SC_NAME!\033[0m"
    [ $((_PB&CK_PM)) -ne 0 ] &&      echo -e "\033[31m- 'post-mount.sh' is not set properly for $SC_NAME!\033[0m"
    [ $((_PB&CK_IPS_BL)) -ne 0 ] &&  echo -e "\033[31m- ipset: no blocklist is set!\033[0m"
    [ $((_PB&CK_IPS_WL)) -ne 0 ] &&  echo -e "\033[31m- ipset: no whitelist is set!\033[0m"
    [ $((_PB&PB_WG_SNE)) -ne 0 ] &&  echo -e "\033[31m- ipset: a gateway bypass is set but should not!\033[0m"
    [ $((_PB&CK_WG_BP)) -ne 0 ] &&   echo -e "\033[31m- ipset: WAN gateway bypass is not set!\033[0m"
    [ $((_PB&CK_IPT_CH)) -ne 0 ] &&  echo -e "\033[31m- iptables: engine chains are not right!\033[0m"
    [ $((_PB&CK_IPT_WG)) -ne 0 ] &&  echo -e "\033[31m- iptables: WAN gateway bypass rules are not right!\033[0m"
    [ $((_PB&CK_IPT_WL)) -ne 0 ] &&  echo -e "\033[31m- iptables: whitelist rules are not right!\033[0m"
    [ $((_PB&CK_IPT_TUN)) -ne 0 ] &&      echo -e "\033[31m- iptables: VPN tunnel IFO rules are corrupted!\033[0m"
    [ $((_PB&CK_IPT_WAN)) -ne 0 ] &&      echo -e "\033[31m- iptables: WAN interface IFO rules are corrupted!\033[0m"
    [ $((_PB&PB_IPT_WAN_MISS)) -ne 0 ] && echo -e "\033[31m- iptables: WAN interface ($WAN_IF) IFO rules are missing!\033[0m"
    [ $((_PB&PB_IPT_IFO)) -ne 0 ] &&      echo -e "\033[31m- iptables: Extra engine IFO rules were found (likely from an old interface)!\033[0m"
  fi
  
  if [ $((_CK+_PB)) -ne 0 ] && [ $_WN -ne 0 ]; then
    echo -ne '\033[1;35mWarnings:\033[0m'; [ "$VERBOSE" -ge 2 ] && echo " (CODE: $_WN)" || echo ''
    case "$((_WN&WN_BL_FILE_NTLD))" in
      $WN_BL_FILE_DIFF) echo -e "\033[35m- blocklist set is different than file.\033[0m";;
      $WN_BL_FILE_MISS) echo -e "\033[35m- blocklist is set but file is missing.\033[0m";;
      $WN_BL_FILE_NTLD) echo -e "\033[35m- no blocklist is set but file exists.\033[0m";;
    esac
    case "$((_WN&WN_WL_FILE_NTLD))" in
      $WN_WL_FILE_DIFF) echo -e "\033[35m- whitelist set is different than file.\033[0m";;
      $WN_WL_FILE_MISS) echo -e "\033[35m- whitelist is set but file is missing.\033[0m";;
      $WN_WL_FILE_NTLD) echo -e "\033[35m- no whitelist is set but file exists.\033[0m";;
    esac
    [ $((_WN&WN_TUN_MISS)) -ne 0 ] && echo -e "\033[31m- iptables: VPN tunnel ($TUN_IF) IFO rules are missing!\033[0m"
    [ $((_WN&WN_LOG_DIFF)) -ne 0 ] && echo -e "\033[35m- current logging settings differs from last time engine was started.\033[0m"
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
