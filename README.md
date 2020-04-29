# Firewall Blocklist
Firewall blocklist script for Netgear R7800 Router with Voxel firmware.
Should work with several other Netgear routers as well.

## Version
3.1.0

## Prerequisite
* You need to have Voxel's Firmware: https://www.voxel-firmware.com
* Although not mandatory for this script to work properly, it is recommanded to bave iprange installed (either on the internal flash `/usr/bin`, or through Entware [self compiled]). The install script will offer to install iprange on the internal flash. You can decide to install it separately or not at all. iprange allows great optimizations.
* If it is possible to install the script on the system partition, this is not recommanded and this installation requires to be on an external (USB) drive (the one on which you may have installed Entware).
* This script will be creating `firewall-start.sh` in `/opt/scripts`; that is a way to define custom iptables in Voxel's Firmwares. If you are already using your own `/opt/scripts/firewall-start.sh`, a line will be added to it to allow this script to work. The clean process will remove that line leaving the rest of `/opt/scripts/firewall-start.sh` in place.

## Install
* Connect to router's terminal with ssh or telnet
* Go to the attached drive (USB): `cd /mnt/optware/` (or change optware by the mountpoint of your drive)
* Copy and paste the following command: `wget -qO- https://github.com/bolemo/firewall-blocklist/archive/v3.1.0.tar.gz | tar xzf - --one-top-level=fbl --strip-components 1`
* Make install script executable: `chmod +x fbl/install.sh`
* Run install script: `fbl/install.sh`
* Answer `y` if you want to install iprange
* Check if installation went fine: `/opt/bolemo/scripts/firewall-blocklist info`
* Remove the install files and folder: `rm -r fbl` check then confirm each file to delete answering y

The install script will create a symbolic link of the bolemo directory in /opt and creates /opt/scripts if it does not exists.

Once installed, you will likely want to launch the script.
Use `/opt/bolemo/scripts/firewall-blocklist update -v` to update blocklists, generate netset, setup ipset and iptables. Use of `-v` is to see the progress.

Anytime, you can use `/opt/bolemo/scripts/firewall-blocklist status` to check if everything is up and running or not.

You will probably want to setup a cron job to update the blocklists once a day (use Entware's cron or Kamoj's addon for that). For example: `15 3 * * * /bin/sh /opt/bolemo/scripts/firewall-blocklist update` (without the `-v` option), will update the blocklist (and the firewall) everyday at 3:15 GMT in the morning (or local time if using Kamoj's addon).

## Upgrade
Since version 2, you do not need to go through the whole installation process to install a new version.
The comnand `/opt/bolemo/scripts/firewall-blocklist info` will show the installed version and the latest version available online.
The `/opt/bolemo/scripts/firewall-blocklist upgrade` command will also show installed and latest version available and ask if you want to upgrade if the online version is different than the one installed.

## Usage
Usage: `/opt/bolemo/scripts/firewall-blocklist COMMAND [OPTION(S)]`

### Valid commands (only one):
* `restart` - setup ipset and iptables then restarts internal firewall
* `update_set` - generates `firewall-blocklist.netset` from servers in `firewall-blocklist.sources`
* `load_set` - loads `firewall-blocklist.netset` into ipset then restarts internal firewall
* `update` - update_set then load_set [probably what you want to use]
* `clean` - clean ipset and iptables rules from setup created by this script
* `help` - displays help
* `info` - displays info on this script
* `status` - displays status
* `log` - displays log
* `upgrade` - download and install latest version

### Options:
* `-v` - verbose mode
* `-log=on`/`off` - when used with restart, load_set or update, will enable/disable logging

## Blocklists
The file `/opt/bolemo/etc/firewall-blocklist.sources` contains the list of server url to get lists from (hash:net or hash:ip). It has several by default. You change this list to suit your needs (like blocking a specific country ip range).

You can find a lot of lists on internet. One great source are the lists from FireHOL: http://iplists.firehol.org/

Since version 3.1, you can have your own custom list of IPs or netsets (IPs with cidr netmask): just create a file named `firewall-blocklist.custom.netset` in `/opt/bolemo/etc/` with your own list. Next tile you will perform a `firewall-blocklist update`, it will integrate your custom list to the master blocklist.

## Logging
### Enabling
To log activity of firewall-blocklist and see what is blocked, you can use the `-log=on` option with the parameter `restart`, `load_set` or `update` using this script.
You can also use the following command: `nvram set log_firewall_blocklist=1`; the next time the firewall-blocklist will be restarted, logging will be active until next reboot of the router.
If you want logging to stay on after a reboot, after using the `-log=on` option or the command `nvram set log_firewall_blocklist=1` do `nvram commit`.

### Accessing the log
To watch the log, use `/opt/bolemo/scripts/firewall-blocklist log` or `dmesg | grep 'firewall-blocklist'`.

### Disabling
To stop logging, use the `-log=off` option with the parameter `restart`, `load_set` or `update` using this script.
You can also use `nvram unset log_firewall_blocklist`.
If you used `nvram commit` after enabling logging, then you need to use `nvram commit` again after using the `-log=off` option or the command `nvram unset log_firewall_blocklist` to stay disabled after router reboot.

## iprange
iprange is a great little utility dealing that is now part of the FireHOL project.
firewall-blocklist works fine without iprange installed, but it is recommanded to install it as it allows great optimizations.

The install script offers to install a version of it on the router (rootfs in /usr/bin). It has been kindly compiled by Voxel and does not require Entware or an external drive.
You can also install it separately directly from Voxel's website here: https://voxel-firmware.com/Downloads/iprange_1.0.4-1_ipq806x.ipk and install it using the command `/bin/opkg install iprange_1.0.4-1_ipq806x.ipk`.

If you prefer not to install it in the rootfs and are a poweruser, you can install it from Entware. It is not available in Voxel's repo, and you will have to compile it yourself. The source is here: https://github.com/firehol/iprange
