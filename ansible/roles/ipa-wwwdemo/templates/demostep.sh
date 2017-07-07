#!/bin/bash
set -e

CONF=/etc/httpd/conf.d/wwwdemo.conf

if [ "$#" -ne 1 ] || [ ! -f "${CONF}.${1}" ]; then
    echo "Usage: $0 step" >&2
    exit 1
fi

if [ ! -f "{{ http_keytab }}" ]; then
    echo "{{ http_keytab }} missing"
    exit 2
fi

if [ ! -f "{{ cert }}" ]; then
    echo "{{ cert }} missing"
    exit 3
fi

set -x
cp ${CONF}.${1} ${CONF}
systemctl reload httpd.service
