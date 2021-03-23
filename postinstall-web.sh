#!/bin/sh
GIT_DIR='https://raw.githubusercontent.com/bolemo/aegis/dev'
DAT_DIR='/opt/bolemo/www/aegis_data'
_getMDFile() {
  /bin/rm -f "$DAT_DIR/$1.htm"
  /usr/bin/wget -qO- --no-check-certificate "$GIT_DIR/$1.md" | curl -sS -X POST --data-binary @- https://api.github.com/markdown/raw --header "Content-Type:text/x-markdown" >"$DAT_DIR/$1.htm"
}
  _getMDFile 'README'
  _getMDFile 'CHANGELOG'
  _getMDFile 'LINKS'
  _getMDFile 'WEB.README'
LHTTPD_CONF='/etc/lighttpd/conf.d'
LHTTPD_WC_CONF="$LHTTPD_CONF/31-aegis.conf"
if test -d "$LHTTPD_CONF" && ! test -e "$LHTTPD_WC_CONF"; then
    cat >/opt/bolemo/etc/lighttpd_aegis_web.conf <<'EOF'
$HTTP["url"] =~ "/bolemo/" {
    cgi.assign = ( "aegis_web.cgi" => "/opt/bolemo/www/cgi-bin/aegis_web.cgi" )
}
EOF
  /bin/ln -sfn /opt/bolemo/etc/lighttpd_aegis_web.conf "$LHTTPD_WC_CONF"
  /etc/init.d/lighttpd restart
fi
echo '- Web Companion post install: done!'
