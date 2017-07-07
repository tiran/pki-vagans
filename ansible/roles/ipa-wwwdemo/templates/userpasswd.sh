#!/bin/bash
set -e

ADMIN_PASSWD="{{ ipa_admin_password }}"
PASSWD="{{ ipa_admin_password }}"
TMPCCACHE="/tmp/ccache.tmp"

export KRB5CCNAME=/tmp/ccache.admin
rm -f "${KRB5CCNAME}"

echo "${ADMIN_PASSWD}" | kinit admin

echo -e "${PASSWD}\n${PASSWD}" | ipa passwd cheimes
echo -e "${PASSWD}\n${PASSWD}\n${PASSWD}" | kinit -c "${TMPCCACHE}" cheimes

echo -e "${PASSWD}\n${PASSWD}" | ipa passwd bob
echo -e "${PASSWD}\n${PASSWD}\n${PASSWD}" | kinit -c "${TMPCCACHE}" bob

rm -f "${KRB5CCNAME}" "${TMPCCACHE}"
