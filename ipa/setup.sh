#!/bin/sh
set -e

vagrant up --no-provision
vagrant provision

echo
echo "Rrun 'bin/ipa_kinit admin' to acquire a Kerberos ticket"
echo "The password is 'Secret123'"
echo

