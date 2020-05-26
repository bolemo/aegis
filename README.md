# Aegis
A firewall blocklist script for Netgear R7800 & R9000 Routers with Voxel firmware.
Should work with several other Netgear routers as well.
Formerly named **firewall-blocklist**

It will filter all traffic to and from WAN and WireGuard or OpenVPN clients tunnels.

## Version
1.1.5

## Prerequisite
* You need to have Voxel's Firmware: https://www.voxel-firmware.com
* It is not mandatory, but it is strongly recommanded to have iprange installed (either on the internal flash `/usr/bin`, or through Entware). The install script will offer to install iprange on the internal flash (R7800 and R9000 only for now, but Entware should support any model). You can decide to install it separately or not at all.
* The script can be installed either on the router internal memory (no extra USB drive required) or an external (USB) drive (like the one on which you may have installed Entware). If installed on external drive (recommanded), it will survive firmware upgrades and factory resets.
* This script will be creating `firewall-start.sh` in `/opt/scripts`; that is a way to define custom iptables in Voxel's Firmwares. If you are already using your own `/opt/scripts/firewall-start.sh`, a line will be added to it to allow this script to work. The clean process will remove that line leaving the rest of `/opt/scripts/firewall-start.sh` in place.
* If installed on external drive, this script will be creating `post-mount.sh` in `(DRIVE)/autorun/scripts`; that is a way to automatically execute code when a drive is connected in Voxel's Firmwares. If you are already using your own `post-mount.sh` (using Entware for example), a line will be added to it to allow this script to automatically work after reboot when on external drive (this is nit needed when in internal memory). The clean process will remove that line leaving the rest of `post-mount.sh` in place.

## Install
You can install either on external (USB) drive or internal memory.

### Install procedure
* Connect to router's terminal with ssh or telnet
* Use command: `wget -qO- https://github.com/bolemo/aegis/raw/master/aegis-install.sh | sh`
* Choose where you want to install aegis (external drive or internal memory)
* If not already present, you will be asked if you want to install iprange (if available, you will be asked if you want to install iprange with Entware, if not (or don't want to install with it), you will be asked if you want to install iprange in internal memory.
* Check if installation went fine: `/opt/bolemo/scripts/aegis info` or simply `aegis info`

Once installed, you will likely want to launch the script.
Use `/opt/bolemo/scripts/aegis update -v` or `aegis update` to update blocklists, generate netset, setup ipset and iptables. Use of `-v` is to see the progress.

Anytime, you can use `/opt/bolemo/scripts/aegis status` or `aegis status` to check if everything is up and running or not.

If aegis was set and running before a router reboot, it should be back automatically after the reboot.

### Cron job
You will probably want to setup a cron job to update the blocklists once a day (use Entware's cron or Kamoj's addon for that). For example: `15 3 * * * /bin/sh /opt/bolemo/scripts/aegis update` (without the `-v` option), will update the blocklist (and the firewall) everyday at 3:15 GMT in the morning (or local time if using Kamoj's addon).

### What does install procedure do
***1) If installed on external drive, it will:***
* Create the directory DRIVE/bolemo
* Create a symbolic link of directory DRIVE/bolemo in /opt

***2) If installed on internal memory, it will:***
* Create the directory /root/bolemo
* Create a symbolic link of directory /root/bolemo in /opt

***Then, for both (1) or (2), install will:***
* Create the directory /opt/bolemo/scripts where aegis is physically installed
* Create the directory /opt/bolemo/etc and install default aegis.sources in it (if not already there)
* Install a file named `profile` in /opt/bolemo/etc and edit /root/.profile to include it
* Create /opt/scripts if it does not exist

***If installing iprange with Entware:***
* iprange will be installed from Entware, so location is according to your Entware setup

***If installing iprange without Entware (on internal memory):***
* iprange will be installed in /usr/bin

## Upgrade
You do not need to go through the installation script to install a new version.
The comnand `aegis info` will show the installed version and the latest version available online.
The `aegis upgrade` command will also show installed and latest version available and ask if you want to upgrade if the online version is different than the one installed.

To upgrade, it is strongly advised to perform `aegis clean` then `aegis upgrade`, then `aegis update`

## Usage
Usage: `/opt/bolemo/scripts/aegis COMMAND [OPTION(S)]` or `aegis COMMAND [OPTION(S)]`

### Valid commands (only one):
* `restart` - setup ipset and iptables then restarts internal firewall
* `update_set` - generates `aegis-blocklist.netset` from servers in `aegis.sources`
* `load_set` - loads `aegis-blocklist.netset` into ipset then restarts internal firewall
* `update` - update_set then load_set [probably what you want to use]
* `clean` - clean ipset and iptables rules from setup created by this script
* `help` - displays help
* `info` - displays info on this script
* `status` - displays status
* `log` - displays log
* `upgrade` - download and install latest version

### Options:
* `-v` - verbose mode
* `-html` - sends output to router's web: http://routerlogin.net/bolemo/aegis.htm
* `-log=on`/`off` - when used with restart, load_set or update, will enable/disable logging
* `-rm-symlink` - when used with clean, removes the symlink `/usr/bin/aegis`

## Blocklists
The file `/opt/bolemo/etc/aegis.sources` contains the list of server url to get lists from (hash:net or hash:ip). It has several by default. You change this list to suit your needs (like blocking a specific country ip range).

You can find a lot of lists on internet. One great source are the lists from FireHOL: http://iplists.firehol.org/

### Custom blocklist
Since version 3.1, you can have your own custom black list of IPs or netsets (IPs with cidr netmask): just create a file named `aegis.custom-blacklist.netset` in `/opt/bolemo/etc/` with your own list. Next tile you will perform a `aegis update`, it will integrate your custom list to the master blocklist.

### Custom whitelist
Since version 3.2, you can have your own custom white list of IPs or netsets (IPs with cidr netmask): just create a file named `aegis.custom-whitelist.netset` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis update`, it will integrate your custom list to the master whitelist.

## Web interface
Each time an aegis command is done with the option `-html`, the output is sent to a page accessible here: http://routerlogin.net/bolemo/aegis.htm
The cron job for an update could call `/bin/sh /opt/bolemo/scripts/aegis update -html` or `/bin/sh /opt/bolemo/scripts/aegis update -v -html`.
Also, a cron job called every 10 minutes, or hour... could call `/bin/sh /opt/bolemo/scripts/aegis status -html` or `/bin/sh /opt/bolemo/scripts/aegis status -v -html`.
In the future, I would like to be able to have the page call aegis to refresh itself.

## Logging
### Enable logging
To log activity of aegis and see what is blocked, you can use the `-log=on` option with the parameter `restart`, `load_set` or `update` using this script (for example: `aegis restart -log=on`).
You can also use the following command: `nvram set aegis_log=1`; the next time aegis will be restarted, logging will be active until next reboot of the router.
If you want logging to stay on after a reboot, after using the `-log=on` option or the command `nvram set aegis_log=1` do `nvram commit`.

### Access the log
To watch the log, use `aegis log` or `dmesg | grep 'aegis'`.

### Disable logging
To stop logging, use the `-log=off` option with the parameter `restart`, `load_set` or `update` using this script.
You can also use `nvram unset aegis_log`.
If you used `nvram commit` after enabling logging, then you need to use `nvram commit` again after using the `-log=off` option or the command `nvram unset aegis_log` to stay disabled after router reboot.

## iprange
iprange is a great little utility dealing that is now part of the FireHOL project.
Aegis works fine without iprange installed, but it is recommanded to install it as it allows great optimizations.

The install script offers to install a version of it on the router (rootfs in /usr/bin). It has been kindly compiled by Voxel and does not require Entware or an external drive.
You can also install it separately:
* [firmware Addon for R7800] directly from Voxel's website here: https://voxel-firmware.com/Downloads/iprange_1.0.4-1_ipq806x.ipk and install it using the command `/bin/opkg install iprange_1.0.4-1_ipq806x.ipk`.
* [firmware Addon for R9000] directly from Voxel's website here: https://voxel-firmware.com/Downloads/iprange_1.0.4-1_r9000.ipk and install it using the command `/bin/opkg install iprange_1.0.4-1_r9000.ipk`.
* using Entware: `/opt/bin/opkg install iprange`.

The source is here: https://github.com/firehol/iprange
