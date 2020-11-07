#!/bin/sh
wget -qO- https://www.iana.org/assignments/protocol-numbers/protocol-numbers-1.csv |
/usr/bin/awk -v RS='"[^"]*"' -v ORS= '{gsub(/,/, "\\&#44;", RT); gsub(/[\n[:space:]]+/, " ", RT); print $0 RT}' |
/usr/bin/awk -F, '
function p(w,x,y,z){printf("%s,%s,%s,%s\n",w,x,y,z)}
NR>1 {
  gsub(/"{2}/, "\\&#34;");
  gsub(/"/, "");
  gsub(/ \(deprecated\)/, "", $2);
  if ($1 ~ /-/) {
    split($1,a,"-");
    for (i=a[1]; i<=a[2]; i++) {p(i,$2,$3,$4)}
  } else {p($1,$2,$3,$4)}
}' |
/usr/bin/sort -n |
/usr/bin/awk -F, '
function p(){printf("%s,%s,%s,%s\n",f[1],f[2]?f[2]"["f[1]"]":f[1],f[3],f[4])}
NR>1 {if ($1==f[1]) {$2=f[2]"/"$2;$3=f[3]"/"$3} else {p()}}
{f[1]=$1;f[2]=$2;f[3]=$3;f[4]=$4}
END {p()}'
