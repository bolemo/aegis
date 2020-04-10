# Firewall Blocklist
Firewall blocklist script for Netgear R7800 Router with Voxel firmware.

should work with R9000 as well.

## Install
* You need to have Voxel's Firmware: https://www.voxel-firmware.com
* Connect to router's terminal with ssh or telnet
* Go to the attached drive (USB): `cd /mnt/optware/` (or change optware by the mountpoint of your drive)
* Download the desired release: `wget -O FWBL.zip "https://github.com/bolemo/firewall-blocklist/archive/LATEST.zip"`
* Unzip the file: `unzip -jd FWBL FWBL.zip`
* Make install script executable: `chmod +x FWBL/install.sh`
* Run install script: `FWBL/install.sh`
* Check if it was installed: `/opt/bolemo/scripts/firewall-blocklist.sh test`
* Remove the install files and folder: `rm -r FWBL*` check then confirm each file to delete answering y

The script will create a symbolic link of the bolemo directory in /opt

Once installed, you will likely want to launch the script.
Use `/opt/bolemo/scripts/firewall-blocklist.sh -v update` to update blocklists, generate netset, setup ipset and iptables. Use of `-v` is to see the progress as it takes several minutes to process (be patient).

Anytime, you can use `/opt/bolemo/scripts/firewall-blocklist.sh status` to check everything is up and running or not.

You will probably want to setup a cron job to update the blocklists once a day (use entware cron or Kamoj's addon for that). For example: `15 3 * * * /bin/sh /opt/bolemo/scripts/firewall-blocklist.sh update` (without the `-v` option), will update the blocklist (and the firewall) everyday at 3:15 in the morning.

## Usage
use: `/opt/bolemo/scripts/firewall-blocklist.sh [-v] COMMAND`

Valid commands (only one):
* `init` - setup ipset and iptables for this script to work
* `clean` - clean ipset and iptables rules from setup created by this script
* `load_set` - populates ipset set from `firewall-blocklist.netset` after performing init
* `update_only` - generates `firewall-blocklist.netset` from servers in `firewall-blocklist.sources`
* `update` - update_only then load_set [probably what you want to use]
* `status` - display status
* `test` - check if this script is installed properly
* `help` - display this

Options:
* `-v` - verbose mode

## Blocklists
The file `/opt/bolemo/etc/firewall-blocklist.sources` contains the list of server url to get lists from (hash:net or hash:ip). It has several by default. You change this list to suit your needs (like blocking a specific country ip range).

You can find a lot of lists on internet. One great source are the lists from FireHOL: http://iplists.firehol.org/
