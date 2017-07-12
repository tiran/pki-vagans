#!/bin/sh
set -ex

openssl s_client \
    -connect {{ ansible_fqdn }}:443 \
    -verify_hostname {{ ansible_fqdn }} \
    -CAfile /etc/pki/tls/certs/ca-bundle.crt \
    -status | egrep --color=always '.*Status.*|$' | less -R
