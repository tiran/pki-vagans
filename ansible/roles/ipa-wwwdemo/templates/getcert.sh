#!/bin/bash
set -e

kinit -kt /etc/krb5.keytab
ipa service-show HTTP/{{ ansible_fqdn }} > /dev/null
rm -f {{ private_key }} {{ cert }}

set -x

ipa-getcert request -w \
    -k {{ private_key }} \
    -f {{ cert }} \
    -D {{ ansible_fqdn }} \
    -K HTTP/{{ ansible_fqdn }} \
    -C 'systemctl reload httpd.service'

set +x

read -p next

ipa-getcert list

read -p next

openssl x509 -noout -text -in {{ cert }}
