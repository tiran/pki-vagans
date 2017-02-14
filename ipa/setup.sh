#!/bin/sh
set -e

vagrant up --no-provision
vagrant provision

echo
echo "Rrun 'bin/ipa_kinit admin' to acquire a Kerberos ticket"
echo "The admin password is 'Secret123'"
echo "The DM password is 'DMSecret456'"
echo

