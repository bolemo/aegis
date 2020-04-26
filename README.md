# Firewall Blocklist
Firewall blocklist script for Netgear R7800 Router with Voxel firmware.

should work with R9000 as well (nor sure about iprange binary that was compiled on R7800)

## Version
3.0.0

## Prerequisite
* You need to have Voxel's Firmware: https://www.voxel-firmware.com
* Although not mandatory for this script to work properly, it is recommanded to bave iprange installed (either on the internal flash `/usr/bin`, either installed through Entware [self compiled]. The install script will offer to install iprange on the internal flash. You can decide to install it separately or not at all. iprange allows great optimizations.
* Although it is possible to install the script on the system partition, this is not recommanded and this installation requires to be on an external (USB) drive (the one on which you may have installed Entware).
* This script will be creating `firewall-start.sh` in `/opt/scripts`; that is a way to define custom iptables in Voxel's Firmwares. If you are already using your own `/opt/scripts/firewall-start.sh`, a line will be added to it to allow this script to work. The clean process will remove that line leaving the rest of `/opt/scripts/firewall-start.sh` in place.

## Install
* Connect to router's terminal with ssh or telnet
* Go to the attached drive (USB): `cd /mnt/optware/` (or change optware by the mountpoint of your drive)
* Copy and paste the following command: `wget -qO- https://github.com/bolemo/firewall-blocklist/archive/v3.0.0.tar.gz | tar xzf - --one-top-level=fbl --strip-components 1`
* Make install script executable: `chmod +x fbl/install.sh`
* Run install script: `fbl/install.sh`
* Answer `y` if you want to install iprange
* Check if installation went fine: `/opt/bolemo/scripts/firewall-blocklist info`
* Remove the install files and folder: `rm -r fbl` check then confirm each file to delete answering y

The install script will create a symbolic link of the bolemo directory in /opt and creates /opt/scripts if it does not exists.

Once installed, you will likely want to launch the script.
Use `/opt/bolemo/scripts/firewall-blocklist -v update` to update blocklists, generate netset, setup ipset and iptables. Use of `-v` is to see the progress.

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
* `info` - check if this script is installed properly
* `upgrade` - download and install latest version
* `help` - display this

Options:
* `-v` - verbose mode

## Blocklists
The file `/opt/bolemo/etc/firewall-blocklist.sources` contains the list of server url to get lists from (hash:net or hash:ip). It has several by default. You change this list to suit your needs (like blocking a specific country ip range).

You can find a lot of lists on internet. One great source are the lists from FireHOL: http://iplists.firehol.org/

## Logging
To log activity of firewall-blocklist and see what is blocked, you can use the following command: `nvram set log_firewall_blocklist=1`; the next time the firewall-blocklist will be restarted, logging will be active until next reboot of the router. To watch the log, use `dmesg | grep 'firewall-blocklist'`. If you want logging to stay on after a reboot, after `nvram set log_firewall_blocklist=1` do `nvram commit`.
To stop logging, use `nvram unset log_firewall_blocklist` or `nvram uncommit log_firewall_blocklist` if you used commit, then the next time the firewall-blocklist will be restarted logging will be disabled.
