## Change Log


### 1.7.12
- Changed when the boot time is calculated. With recent Voxel firmwares, aegis was calculating its base time (for logs) before date or uptime was properly set.
- Changed the Web Companion post install script, as it was not checking if a directory was present before installing DOC files.
---
### 1.7.11
- Web Companion: in STATS, fixed the display when no port is involved (all traffic involving portless protocols). Instead of an empty string, it mentions NO PORT. Also, HIT(S) now shows as HIT for 0 or 1, and HITS if more than one. Shows latest HIT time. Reloads every minute.
- The log daemon at each loop now checks records treated during previous loop to make sure device names were not missed if known.
---
### 1.7.10
- Changed the logging daemon process, optimizations, clearer log file, and determination of local device name upstream. Also the length of the aegis log file is now based on a minimum TTL in seconds instead of a minimum number of lines. Default is 86400 (24 sliding hours).
- Replaced `log -get-history` and `log -set-history` by `log -get-ttl` and `log -set-ttl`.
- Rewrote code for `log -show` and `log -live` (simplified code and output).
- Web Companion: updated protocols database to latest IANA entry.
- Web Companion: simplified and improved log output.
- Web Companion: new STATS tab allowing to get some stats from the log using a selection of associative keys and filters.
---
### 1.7.9
- calling net-scan daemon directly to get LAN devices names, instead of using the NG web page net-cgi trick.
- added a pre-upgrade process.
- improved upgrade process output.
- improved CSS for documentation display.
---
### 1.7.8
- Web Companion: added DOC tab to read 'Aegis Read Me', 'Web Companion', 'Change Log' and 'Links'.
---
### 1.7.7
- Change log starting point
