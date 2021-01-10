# Aegis
A firewall blocklist script for Netgear R7800, R8900 & R9000 Routers with Voxel firmware.
Should work with several other Netgear routers as well.

It will filter all traffic to and from WAN and WireGuard or OpenVPN clients tunnels.

## Version
1.5.8

## Prerequisite
* You need to have Voxel's Firmware: https://www.voxel-firmware.com
* It is not mandatory, but it is strongly recommanded to have iprange installed (either on the internal flash `/usr/bin`, or through Entware). The install script will offer to install iprange on the internal flash (R7800 and R9000 only for now, but Entware should support any model). You can decide to install it separately or not at all.
* The script can be installed either on the router internal memory (no extra USB drive required) or an external (USB) drive (like the one on which you may have installed Entware). If installed on external drive (recommanded), it will survive firmware upgrades and factory resets.
* This script will be creating `firewall-start.sh` in `/opt/scripts`; that is a way to define custom iptables in Voxel's Firmwares. If you are already using your own `/opt/scripts/firewall-start.sh`, a line will be added to it to allow this script to work. The clean process will remove that line leaving the rest of `/opt/scripts/firewall-start.sh` in place.
* If installed on external drive, this script will be creating `post-mount.sh` in `(DRIVE)/autorun/scripts`; that is a way to automatically execute code when a drive is connected in Voxel's Firmwares. If you are already using your own `post-mount.sh` (using Entware for example), a line will be added to it to allow this script to automatically work after reboot when on external drive (this is not needed when in internal memory). The clean process will remove that line leaving the rest of `post-mount.sh` in place.

## Install
You can install either on external (USB) drive or internal memory.

### Install procedure
* Connect to router's terminal with ssh or telnet
* Use command: `wget -qO- https://github.com/bolemo/aegis/raw/master/aegis-install.sh --no-check-certificate | sh`
* Choose where you want to install aegis (external drive or internal memory)
* If not already present, you will be asked if you want to install iprange (if available, you will be asked if you want to install iprange with Entware, if not (or don't want to install with it), you will be asked if you want to install iprange in internal memory.
* Check if installation went fine: `/opt/bolemo/scripts/aegis info` or simply `aegis info`

Once installed, you will likely want to launch the script.
Use `/opt/bolemo/scripts/aegis up -v` or `aegis up` to generate updated directives (first launch), set and uprear the shield protection. Use of `-v` is to see the progress.

Anytime, you can use `/opt/bolemo/scripts/aegis status` or `aegis status` to check if everything is up and running or not.

If aegis was set and running before a router reboot, it should be back automatically after the reboot.

### Cron job
You will probably want to setup a cron job to update the blocklists once a day (use Entware's cron or Kamoj's addon for that). For example: `15 3 * * * /bin/sh /opt/bolemo/scripts/aegis refresh`, will update the blocklist (and the firewall) everyday at 3:15 in the morning (or local time if using Kamoj's addon); this will update and apply new sets without disturbing actual aegis state (up or down).
Or if you want to make sure aegis is (re)started each time, use: `15 3 * * * /bin/sh /opt/bolemo/scripts/aegis up -refresh`

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

To upgrade, it is strongly advised to perform `aegis down` then `aegis upgrade`, then `aegis up`

## Usage
Usage: `/opt/bolemo/scripts/aegis COMMAND [OPTION(S)]` or `aegis COMMAND [OPTION(S)]`

### Valid commands (only one):
* `up` - (re)starts aegis shield protection
  * `-net-wall` + by restarting the internal firewall
  * `-refresh` + with updated shield directives
  * `-log-enable` + with logging enabled
  * `-log-disable` + with logging disabled
  * `-wan-no-bypass` + without WAN network range bypass
  * `-vpn-no-bypass` + without VPN network range bypass
* `down` - stops aegis shield protection
* `refresh` - updates shield directives from servers in `aegis.sources` and custom lists (blocklists, whitelist)
  * `-custom-only` - will refresh directives only from custom lists (using offline cache for sources)
* `unset` - stops and unsets aegis shield
  * `-rm-config` + and removes the configuration system (mostly if you plan not to use the script anymore)
  * `-rm-symlink` + and removes the symlink /usr/bin/aegis (mostly if you plan not to use the script anymore)
  * `-rm-web` + and removes Web Companion
  * `-rm-log` + and removes the log file
* `help` - displays help
* `info` - displays info on this script
* `status` - displays status
* `log -enable` - enables logging
* `log -disable` - disables logging
* `log -show` - displays log
  * `-lines=`N + displays N lines (N being the number of lines to show)
* `log -live` - displays log live (*CTRL-C* to exit)
* `log -get-history` - show the history size for the log file /var/log/log-aegis
* `log -set-history=`N - sets the history size to N records for the log file /var/log/log-aegis
* `upgrade` - downloads and installs latest version
* `web -install` - downloads and installs the Web Companion
* `web -remove`  - removes the Web Companion
### GENERAL OPTIONS (can be used with any command)
* `-v` + verbose mode (level 1)
* `-vv` + verbose mode (level 2)
* `-vvv` + verbose mode (level 3)
* `-q` + quiet mode (no output)load_set or update):

## Blocklists
The file `/opt/bolemo/etc/aegis.sources` contains the list of server url to get lists from (hash:net or hash:ip). It has several by default. You change this list to suit your needs (like blocking a specific country ip range).

You can find a lot of lists on internet. One great source are the lists from FireHOL: http://iplists.firehol.org/

### Custom blocklists
You can have your own custom black list of IPs or netsets (IPs with cidr netmask): just create a file named `aegis.blacklist` in `/opt/bolemo/etc/` with your own list. Next tile you will perform a `aegis update`, it will integrate your custom list to the master blocklist.
You can have several custom black lists, beside aegis.blacklist, any file named aegis-*[SOMETHING]*.blacklist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

### Custom whitelists
You can have your own custom white list of IPs or netsets (IPs with cidr netmask): just create a file named `aegis.whitelist` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis update`, it will integrate your custom list to the master whitelist.
You can have several custom white lists, beside aegis.whitelist, any file named aegis-*[SOMETHING]*.whitelist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

## Web Companion
Aegis can install an optional Web Companion, to do so, once aegis is installed, just run `aegis web -install`; this will install or reinstall the Web Companion.
To remove it, simply run `aegis web -remove`, or while using the command `aegis unset`, add the `-rm-web` option.
Once installed, thr Web Companion is accessible here: http://routerlogin.net/bolemo/aegis.htm

If the Web Companion is installed, it will automatically get upgraded when aegis is upgraded from the command `aegis upgrade`.

## Logging
### Enable logging
To enable logging, just run `aegis log -enable`. If aegis is up, it will activate the logging immediatly. If aegis is down, it won't start it, but next time it will be started, logging will be enabled.
You can also use the `-log-enable` option with the command `up` to (re)start aegis with logging on.
This survives internal firewall restarts and router reboots.
A specific log file is created in `/var/log/log-aegis`. A small daemon is loaded in memory to update this log file and is exited automatically when the log is turned off. The node id of the file is not changing with rotations, allowing to follow it.

### Access the log
To watch the last entries of the log, use `aegis log -show`.
To watch the last N entries of the log, use `aegis log -show -lines=`N.
To watch the log live (in realtime), use `aegis log -live`. To exit use *CTRL-C*.


### Disable logging
To stop logging, just use `aegis log -disable` (if aegis is up, it will desactivates the logging immediatly; if it is down, logging won't be active next time it is started). You an also use the option `-log-disable` when you are (re)starting then engine: `aegis up -log-disable`.

## iprange
iprange is a great little utility dealing that is now part of the FireHOL project.
Aegis works fine without iprange installed, but it is recommanded to install it as it allows great optimizations.

The install script offers to install a version of it on the router (rootfs in /usr/bin). It has been kindly compiled by Voxel and does not require Entware or an external drive.
You can also install it separately:
* [firmware Addon for R7800] directly from Voxel's website here: https://voxel-firmware.com/Downloads/iprange_1.0.4-1_ipq806x.ipk and install it using the command `/bin/opkg install iprange_1.0.4-1_ipq806x.ipk`.
* [firmware Addon for R9000] directly from Voxel's website here: https://voxel-firmware.com/Downloads/iprange_1.0.4-1_r9000.ipk and install it using the command `/bin/opkg install iprange_1.0.4-1_r9000.ipk`.
* using Entware: `/opt/bin/opkg install iprange`.

The source is here: https://github.com/firehol/iprange
