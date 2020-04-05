# Firewall Blocklist
Firewall blocklist script for Netgear R7800 Router with Voxel firmware.

should work with R9000 as well.

## Install
* You need to have Voxel's Firmware
* Connect to router's terminal with ssh or telnet
* Go to the attached drive (USB): `cd /mnt/optware/`
* Download install script: `wget -O install-firewall-blocklist.sh "https://raw.githubusercontent.com/bolemo/firewall-blocklist/master/install-firewall-blocklist.sh"`
* Make install script executable: `chmod +x install-firewall-blocklist.sh`
* Run install script: `./install-firewall-blocklist.sh`

Install locations can be different as long as you define them in the script (variables at the beginning).

## Use
use: `/mnt/optware/bolemo/scripts/firewall-blocklist.sh parameter`

Valid Parameters (only one):
* init        - setup ipset and iptables for this script to work
* clean       - clean ipset and iptables rules from setup created by this script
* load_set    - populates ipset set from /usr/local/etc/hw_firewall.netset after performing init
* update_only - generates /usr/local/etc/hw_firewall.netset from servers in /usr/local/etc/hw_firewall.sources
* update      - update_only then load_set [probably what you want to use]
* status      - display status
* help        - display this
