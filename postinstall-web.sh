#!/bin/sh
  /bin/rm -f '/opt/bolemo/www/aegis_data/README.htm'
  /bin/rm -f '/opt/bolemo/www/aegis_data/CHANGELOG.htm'
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
