#!/bin/sh
set -e

vagrant up --no-provision
vagrant provision

mkdir -p ~/.ipa

cat << EOF

Now prepare the FreeIPA test enviroment:
    cp -ru ./inventory/dotipa/* ~/.ipa/
    export KRB5_CONFIG=~/.ipa/krb5.conf
    export MASTER_env1=master.ipatests.local
    kinit admin
EOF
