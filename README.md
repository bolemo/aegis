# Aegis
A firewall blocklist script for Netgear R7800, R8900, R9000 and Orbi Routers [with Voxel firmware].
Might work with several other Netgear routers supporting Voxel firmware as well.

It will filter all traffic to and from WAN and WireGuard or OpenVPN clients tunnels.

## Version
1.7.8

## Prerequisite
* You need to have Voxel's Firmware: https://www.voxel-firmware.com
* The binary iprange (included with latest Voxel's firmwares) is now mandatory. If for some reason you are using an older Voxel firmware, it is possible to install iprange (either on the internal flash `/usr/bin`, or through Entware), and in that case, the install script will offer to install iprange on the internal flash (R7800 and R9000 only) or Entware.
* The script can be installed either on the router internal memory (no extra USB drive required) or an external (USB) drive (like the one on which you may have installed Entware). If installed on external drive (recommanded), it will survive firmware upgrades and factory resets.
* This script will be creating `firewall-start.sh` in `/opt/scripts`; that is a way to define custom iptables in Voxel's Firmwares. If you are already using your own `/opt/scripts/firewall-start.sh`, a line will be added to it to allow this script to work. The clean process will remove that line leaving the rest of `/opt/scripts/firewall-start.sh` in place.
* If installed on external drive, this script will be creating `post-mount.sh` in `(DRIVE)/autorun/scripts`; that is a way to automatically execute code when a drive is connected in Voxel's Firmwares. If you are already using your own `post-mount.sh` (using Entware for example), a line will be added to it to allow this script to automatically work after reboot when on external drive (this is not needed when in internal memory). The unset process will remove that line leaving the rest of `post-mount.sh` in place.

## Install
You can install either on external (USB) drive or internal memory.

### Install procedure
* Connect to router's terminal with ssh or telnet
* Use command: `wget -qO- https://github.com/bolemo/aegis/raw/stable/aegis-install.sh --no-check-certificate | sh`
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
* iprange will be installed in /opt/bin

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
* `test -ip=`IP  - test if IP is blocked or not by aegis
### GENERAL OPTIONS (can be used with any command)
* `-v` + verbose mode (level 1)
* `-vv` + verbose mode (level 2)
* `-q` + quiet mode (no output)load_set or update):

## Lists (online blocklists, custom blacklists, custom whitelists)
### Blocklists sources (online blocklists)
The file `/opt/bolemo/etc/aegis.sources` contains the list of server url to get lists from (hash:net or hash:ip). It has several by default. You change this list to suit your needs (like blocking a specific country ip range).

You can find a lot of lists on internet. One great source are the lists from FireHOL: http://iplists.firehol.org/

### Custom blacklists
You can have your own custom blacklists of IPs or netsets (IPs with cidr netmask) that aegis will block for you.
There are optional and needed only if you want to add you own IP addresses to aegis blocking directives.
You can create global lists (will apply for WAN and VPN), or lists that will apply specifically to only WAN or only VPN traffic.

#### Custom global blacklists (will block on WAN & VPN)
Just create a file named `aegis.blacklist` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis refresh`, it will integrate your custom list to the master blocklist (shield blocking directives) for WAN and VPN traffic.
You can have additionnal custom global blacklists, beside aegis.blacklist, any file named aegis-*[SOMETHING]*.blacklist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

#### Custom WAN blacklists (will block only on WAN)
Just create a file named `aegis.wan-blacklist` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis refresh`, it will integrate your custom list to the master blocklist (shield blocking directives) **only for WAN traffic**.
You can have additionnal custom WAN blacklists, beside aegis.wan-blacklist, any file named aegis-*[SOMETHING]*.wan-blacklist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

#### Custom VPN blacklists (will block only on VPN)
Just create a file named `aegis.vpn-blacklist` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis refresh`, it will integrate your custom list to the master blocklist (shield blocking directives) **only for VPN traffic**.
You can have additionnal custom VPN blacklists, beside aegis.vpn-blacklist, any file named aegis-*[SOMETHING]*.vpn-blacklist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

#### Custom whitelists
You can have your own custom whitelist of IPs or netsets (IPs with cidr netmask) that aegis will bypass for you.
Such lists are optional and only needed if you want/need to bypass a blocking directive, so any IP address in a whitelist will never be blocked by aegis, even if it is in a blocklist or a custom blacklist.
You can create global lists (will apply for WAN and VPN), or lists that will only apply to WAN or to VPN traffic.

#### Custom global whitelists (will bypass on WAN & VPN)
Just create a file named `aegis.whitelist` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis refresh`, it will integrate your custom list to the master whitelist (shield bypassing directives) for WAN and VPN traffic.
You can have additionnal custom global whitelists, beside aegis.whitelist, any file named aegis-*[SOMETHING]*.whitelist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

#### Custom WAN whitelists (will bypass only on WAN)
Just create a file named `aegis.wan-whitelist` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis refresh`, it will integrate your custom list to the master whitelist (shield bypassing directives) **only for WAN traffic**.
You can have additionnal custom WAN whitelists, beside aegis.wan-whitelist, any file named aegis-*[SOMETHING]*.wan-whitelist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

#### Custom VPN whitelists (will bypass only on VPN)
Just create a file named `aegis.vpn-whitelist` in `/opt/bolemo/etc/` with your own list. Next time you will perform a `aegis refresh`, it will integrate your custom list to the master whitelist (shield bypassing directives) **only for VPN traffic**.
You can have additionnal custom VPN whitelists, beside aegis.vpn-whitelist, any file named aegis-*[SOMETHING]*.vpn-whitelist (*[SOMETHING]* being any alphanumerical name) in `/opt/bolemo/etc/` will also be taken in consideration.

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
Aegis needs iprange installed, as it allows great optimizations.

**Since February 2021, Voxel's firmwares already include iprange.**

With older firmwares, the install script wikl offers to install a version of it on the router 1) through Entware if you have it, or 2) directly on rootfs (in /usr/bin) if you don't have Entware (or don't want to install with Entware).

The source is here: https://github.com/firehol/iprange

## Metrics
There are very basic privacy friendly metrics sent when an install or an upgrade is made (and only then).

What is sent then is:
* the ip (that is **not stored**, it is just to find the country),
* the router model (just the short string model name is sent: `R7800`, `R9000`, `RBR50`, ...),
* an anonymous unique identifier string (a locally generated md5 hash),
* the aegis version number being downloaded,
* and if it is installed internally or externally (just `ext` or `int` string; no drive name sent).

It is using https://www.goatcounter.com/ that is open source and respects privacy.

All that is visible at the end is the country (no ip), router model, aegis version being downloaded as well as installation being internal or external. Nothing more.

This is to have basic statistics about aegis (how many people are downloading it, where in the world, router models).

Only installations or upgrades are sending these basic metrics: once an upgrade or install is done, it does not send anything until next upgrade. No data collection, metrics, stats... are ever sent when aegis is used. How and when you are using it is private.
