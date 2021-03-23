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
