## Web Companion Documentation
Here is a quick tour of the web interface for Aegis.

### Header
The page header shows on the right the installed aegis version, and if it is installed on the internal memory or an external drive.

### Tabs
#### STATUS

This tab displays the status of Aegis, if it is set or unset, running or stopped, or if there is a problem.
It gives some extra information about the **Setting status** (is aegis setup or not), the **Directives generation times** (what was the last time the master blocking and bypassing rules were set) and the **Uprear information** (information on the last time aegis was (re)started).

---
#### COMMAND
From this tab, you can pilot aegis.
- **REFRESH directives then start aegis**: to refresh the directives from the sources lists (online), and the custom lists.
- **REFRESH ONLY CUSTOM directives then start aegis**: to refresh the directives only from the custom lists, and will use the cached directives for sources lists (offline, from last time it was refreshed from sources).
- **SHIELD UP (start aegis)**: to start aegis.
- **SHIELD DOWN (stop aegis)**: to stop aegis.
And for any of these commands, you decide if you want to activate or not the logging, or keep it as it is.

---
#### LOG
Tab to watch the live log, when enabled.
It can be filtered by interface (WAN, VPN), and direction (incoming, outgoing).

---
#### STATS
Tab to generate stats from the log, when enabled.
It works on the period of the last sliding 24 hours (or from when router was restarted if it was less than 24 hours ago).
The stats are generated from the association of selected keys:
- **DIRECTION**: select how the direction is taken into account for the statistics):
  - ***BOTH WAYS***: incoming and outgoing are taken into account and differentiated,
  - ***INCOMING***: incoming only (ignore outgoing),
  - ***OUTGOING***: outgoing only (ignore incoming),
  - ***IGNORE WAY***: the direction information is not taking into account (differentiated) for the statistics.
- **INTERFACE**: select how the interface is taken into account for the statistics:
  - ***ALL INTERFACES***: WAN and VPN are taken into account and differentiated,
  - ***WAN***: take only WAN interface into account and ignore VPN interface,
  - ***VPN***: take only VPN interface into account and ignore WAN interface,
  - ***IGNORE INTERFACE***: the interface information is not taking into account (differentiated) for the statistics.
- **PROTOCOL**: if checked, the protocol is taken into account for the statistics (and each one in the log is differentiated), if unchecked, the protocol is ignored.
- **REMOTE IP**: if checked, the remote IP adress is taken into account for the statistics (each different IP in the log is differentiated), if unchecked, the remote IP is ignored.
- **REMOTE PORT**: if checked, the remote port is taken into account for the statistics (each different port in the log is differentiated), if unchecked, the remote port is ignored.
- **LOCAL DEVICE**: if checked, the local device denomination is taken into account for the statistics (each different device in the log is differentiated), if unchecked, the local device denomination is ignored. The denomination can be the router itself, a device on then LAN, or the broadcast.
- **LOCAL IP**: if checked, the local IP adress is taken into account for the statistics (each different IP in the log is differentiated), if unchecked, the local IP is ignored.
- **LOCAL PORT**: if checked, the local port is taken into account for the statistics (each different port in the log is differentiated), if unchecked, the local port is ignored.

---
#### TOOLS
For now, it only allows to check an IP address. It will tells if the address is in any loaded directive, and if it is blocked by the router or not.

---
#### LISTS
The drop down list allows to select which list to view/edit.
Once a list is selected, it displays the last changed date, and the list can be edited directly in the page. The [Reload list] button reloads the list (to discard changes made); the [Save list] button allows to save the changes made in the list.
It allows to select the sources list, and all default custom (global, WAN and VPN) lists (block and white lists). However, if aegis allows to have several custom lists (beside default ones), any extra one is not viewable/editable from the web interface.

---
#### DEBUG
This tab is useful for troubleshooting, in cas of problems. Its output can be shared on the forum.

---
#### DOC
This tab allows to read documentation (read me, change log, links, etc...)

---
#### UPGRADE
When a new version of aegis is available, this tab appears and allows to proceed with ghe upgrade. It does not show when there is no upgrades available.
