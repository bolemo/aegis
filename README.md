# bolemo_firewall
Firewall blocklist script for Netgear R7800 Router with Voxel firmware

## Install
* `bolemo_firewall.sh` goes in `/mnt/optware/bolemo/scripts/`
* `bolemo_firewall.sources` goes in `/mnt/optware/bolemo/etc/`

Install locations can be different as long as you define them in the script (variables at the beginning)

## Use
use: `/mnt/optware/bolemo/scripts/bolemo_firewall parameter`

Valid Parameters (only one):
* init        - setup ipset and iptables for this script to work
* clean       - clean ipset and iptables rules from setup created by this script
* load_set    - populates ipset set from /usr/local/etc/hw_firewall.netset after performing init
* update_only - generates /usr/local/etc/hw_firewall.netset from servers in /usr/local/etc/hw_firewall.sources
* update      - update_only then load_set [probably what you want to use]
* status      - display status
* help        - display this
