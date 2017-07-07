#!/bin/sh
set -e

kinit -kt /etc/krb5.keytab
ipa service-show HTTP/{{ ansible_fqdn }} > /dev/null

rm -f {{ http_keytab }}

set -x
ipa-getkeytab -p HTTP/{{ ansible_fqdn }} -k {{ http_keytab }}
chown apache:apache {{ http_keytab }}
chmod 600 {{ http_keytab }}
