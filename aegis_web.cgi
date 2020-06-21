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
