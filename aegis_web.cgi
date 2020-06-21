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
