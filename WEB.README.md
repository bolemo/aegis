# Web Companion Documentation
Here is a quick tour of the web interface for Aegis.

## Header
The page header shows on the right the installed aegis version, and if it is installed on the internal memory or an external drive.

## Tabs
- [STATUS](#status) - shows Aegis status.
- [COMMAND](#command) - command Aegis (start, stop, etc...).
- [LOG](#log) - watch the live log if enabled.
- [TOOLS](#tools) - diagnostic tools.
- [LISTS](#lists) - read and edit lists (sources, blocklists, whitelists...)
- [DEBUG](#debug) - debug output.
- [DOC](#doc) - documentation.

### STATUS
This tab displays the status of Aegis, if it is set or unset, running or stopped, or if there is a problem.
It gives some extra information about the **Setting status** (is aegis setup or not), the **Directives generation times** (what was the last time the master blocking and bypassing rules were set) and the **Uprear information** (information on the last time aegis was (re)started).

### COMMAND
From this tab, you can pilot aegis.
- **REFRESH directives then start aegis**: to refresh the directives from the sources lists (online), and the custom lists.
- **REFRESH ONLY CUSTOM directives then start aegis**: to refresh the directives only from the custom lists, and will use the cached directives for sources lists (offline, from last time it was refreshed from sources).
- **SHIELD UP (start aegis)**: to start aegis.
- **SHIELD DOWN (stop aegis)**: to stop aegis.
And for any of these commands, you decide if you want to activate or not the logging, or keep it as it is.

### LOG
Tab to watch the live log, when enabled.
It can be filtered by interface (WAN, VPN), and direction (incoming, outgoing).

### TOOLS
For now, it only allows to check an IP address. It will tells if the address is in any loaded directive, and if it is blocked by the router or not.

### LISTS
The drop down list allows to select which list to view/edit.
Once a list is selected, it displays the last changed date, and the list can be edited directly in the page. The [Reload list] button reloads the list (to discard changes made); the [Save list] button allows to save the changes made in the list.
It allows to select the sources list, and all default custom (global, WAN and VPN) lists (block and white lists). However, if aegis allows to have several custom lists (beside default ones), any extra one is not viewable/editable from the web interface.

### DEBUG
This tab is useful for troubleshooting, in cas of problems. Its output can be shared on the forum.

### DOC
This tab allows to read documentation (read me, change log, links, etc...)
