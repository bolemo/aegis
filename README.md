# hw_firewall
Firewall script for Netgear R7800 Router

## Install
* `hw_firewall.sh` goes in `/usr/local/sbin`
* `hw_firewall.sources` goes in `/usr/local/etc/`

## Use
use: `/usr/local/sbin/hw_firewall parameter`

Valid Parameters (only one):
* init        - setup ipset and iptables for this script to work
* clean       - clean ipset and iptables rules from setup created by this script
* load_set    - populates ipset set from /usr/local/etc/hw_firewall.netset after performing init
* update_only - generates /usr/local/etc/hw_firewall.netset from servers in /usr/local/etc/hw_firewall.sources
* update      - update_only then load_set [probably what you want to use]
* status      - display status
* help        - display this
