# Firewall Blocklist
Firewall blocklist script for Netgear R7800 Router with Voxel firmware.

should work with R9000 as well.

## Prerequisite
* You need to have Voxel's Firmware: https://www.voxel-firmware.com
* Although it is technically possible to install the script on the system partition, this is not recommanded and this installation requires to be on an external (USB) drive (the one on which you lay have installed Entware).
* This script will be creating `firewall-start.sh` in `/opt/scripts`; that is a way to define custom iptables in Voxel's Firmwares. If you are already using your own `/opt/scripts/firewall-start.sh`, a line will be added to it to allow this script to work. The clean process will remove that line leaving the rest of `/opt/scripts/firewall-start.sh` in place.

## Install
* Connect to router's terminal with ssh or telnet
* Go to the attached drive (USB): `cd /mnt/optware/` (or change optware by the mountpoint of your drive)
* Copy and paste the following command: `wget -qO- https://github.com/bolemo/firewall-blocklist/archive/v1.5.3.tar.gz | tar xzf - --one-top-level=fbl --strip-components 1`
* Make install script executable: `chmod +x fbl/install.sh`
* Run install script: `fbl/install.sh`
* Check if it was installed: `/opt/bolemo/scripts/firewall-blocklist test`
* Remove the install files and folder: `rm -r fbl` check then confirm each file to delete answering y

The install script will create a symbolic link of the bolemo directory in /opt and creates /opt/scripts if it does not exists.

Once installed, you will likely want to launch the script.
Use `/opt/bolemo/scripts/firewall-blocklist -v update` to update blocklists, generate netset, setup ipset and iptables. Use of `-v` is to see the progress. V1.5 is a lot faster in building ipsets (a few seconds vs several minutes with v1.0).

Anytime, you can use `/opt/bolemo/scripts/firewall-blocklist status` to check if everything is up and running or not.

You will probably want to setup a cron job to update the blocklists once a day (use entware cron or Kamoj's addon for that). For example: `15 3 * * * /bin/sh /opt/bolemo/scripts/firewall-blocklist update` (without the `-v` option), will update the blocklist (and the firewall) everyday at 3:15 GMT in the morning.

## Usage
use: `/opt/bolemo/scripts/firewall-blocklist [-v] COMMAND`

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
