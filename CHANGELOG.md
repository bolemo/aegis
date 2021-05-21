## Change Log

### 1.7.10
- Changed the logging daemon process, optimizations, clearer log file, and determination of local device name upstream. Also the length of the aegis log file is now based on a minimum TTL in seconds instead of a minimum number of lines. Default is 86400 (24 sliding hours).
- Replaced `log -get-history` and `log -set-history` by `log -get-ttl` and `log -set-ttl`.
- Rewrote code for `log -show` and `log -live` (simplified code and output).
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
