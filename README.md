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
* Check if it was installed: `/opt/bolemo/scripts/firewall-blocklist.sh status`
* Remove the install script: `rm install-firewall-blocklist.sh`

The script will create a symbolic link of the bolemo directory in /opt

Once installed, you will likely want to launch the script. Use `/opt/bolemo/scripts/firewall-blocklist.sh -v update` to update blocklists, generate netset, setup ipset and iptables. Use of `-v` is to see the progress as it takes several minutes to process.

Once the process is done, you can use `/opt/bolemo/scripts/firewall-blocklist.sh status` to check everything is up and running.

You will probably want to setup a cron job to update the blocklists once a day. You can use kamoj addon and add as a cron job: `15 3 * * * /bin/sh /opt/bolemo/scripts/firewall-blocklist.sh update` (without the `-v` option).

## Use
use: `/opt/bolemo/scripts/firewall-blocklist.sh [options] command`

Valid commands (only one):
* init        - setup ipset and iptables for this script to work
* clean       - clean ipset and iptables rules from setup created by this script
* load_set    - populates ipset set from /usr/local/etc/hw_firewall.netset after performing init
* update_only - generates /usr/local/etc/hw_firewall.netset from servers in /usr/local/etc/hw_firewall.sources
* update      - update_only then load_set [probably what you want to use]
* status      - display status
* help        - display this
Options:
* -v          - verbose mode
