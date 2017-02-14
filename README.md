Vagrant + Ansible for FreeIPA and Dogtag PKI
============================================

Authors:
    Christian Heimes <cheimes@redhat.com>

The playbook is partly inspired by and based on Adam Young's rippowam
https://github.com/admiyo/rippowam.

Requirements
============

The FreeIPA setup needs about 3 to 3.5 GB of free RAM and 6 to 7 GB disk space.

Install dependencies
--------------------

```shell
sudo dnf install ansible libvirt vagrant vagrant-libvirt vagrant-hostmanager libselinux-python nss-tools
sudo systemctl enable libvirtd
sudo systemctl start libvirtd
sudo usermod -G libvirt -a YOUR_USER
```


Either restart your session or use newgrp to join the new user group
(current shell only).

```shell
$ newgrp libvirt
```

passwords
=========

The default password for the users root and vagrant, FreeIPA's admin user,
389-DS, PKI CA and PKI KRA is **Secret123**.


FreeIPA
=======

```shell
$ cd ipa
$ ./setup.sh
```

Vagrant's multi-machine setup can run into a race condition and starts
provisioning before all machines have a new SSH key.
```vagrant up --no-provision``` followed by ```vagrant provision``` is more stable.
Sometimes the initial provision fails to configure the client or
replica. A second provisioning run with ```vagrant provision``` fixes most issues.

The FreeIPA playbook deploys six machines:

  * ipamaster (master.ipa.example) with CA and KRA
  * ipareplica1 (replica1.ipa.example)
  * ipaclient1 (client1.ipa.example)
  * ipafilesserver (fileserver.ipa.example) for NFS, Samba and Apache demos
  * ipavpnserver (vpn.ipa.example) for ocserv VPN
  * ipaidpserver (idp.ipa.example) for Ipsilon IdP

When the machines are up, you can acquire a Kerberos ticket and start a local
instance of Firefox to explore the WebUI. The admin password is **Secret123**.

```shell
$ bin/ipa_kinit admin
$ bin/ipa_firefox
$ bin/ipa_ssh admin@client1.ipa.example
```


FreeIPA test server
===================

```shell
$ cd ipatests
$ ./setup.sh
```

One test machine:

  * ipatestmaster (master.ipatests.local) with CA and KRA


Dogtag PKI
==========

```shell
$ cd pki
$ vagrant up
```

The playbook for Dogtag PKI deploys 389-DS, a CA and a KRA in one VM.

 * pki_server (dogtag.pki.example)


Python 3 dependencies
---------------------

There is a shell script in pki/rpms that will download some dependencies.

forceful cleanup
----------------

```shell
rm -rf /var/lib/pki/ /var/log/pki/ /etc/sysconfig/pki-tomcat/ /etc/sysconfig/pki/tomcat/pki-tomcat/ /root/.dogtag/pki-tomcat /etc/pki/pki-tomcat/
```

Vagrant quick manual
====================

create VM
---------

```shell
$ cd pki
$ vagrant up
```

Provision the VM again
----------------------

For example to update RPMs

```shell
$ vagrant provision
```

Log into VM
-----------

```shell
$ vagrant ssh <machine>
```

Destroy VM
----------

```shell
$ vagrant destroy
```

Install custom RPMs
-------------------

Copy or symlink files or directories with RPMs into pki/rpms or
ipa/rpms and set custom_rpms to True. The Ansible playbook will pick up all
RPMs (even in symlinked and nested directory structures) and install them.

When something fails
--------------------

```shell
$ sudo systemctl restart libvirtd.service
$ vagrant provision
```

Provision non Vagrant machines
==============================

Create an ```inventory.cfg```

```
[ipaserver_master]
master.domain.example

[ipaserver_replica]
replica1.domain.example
replica2.domain.example

[ipa_client]
client1.domain.example
client2.domain.example
client3.domain.example
```

and shell script

```shell
#!/bin/sh
set -ex

PKI_VAGANS="/path/to/pki-vagans"
IPA_DOMAIN="domain.example"

export ANSIBLE_CONFIG=${PKI_VAGANS}/ansible/ansible.cfg

ansible-playbook \
    -i inventory.cfg \
    ${PKI_VAGANS}/ansible/ipa-playbook.yml \
    -vv \
    --extra-vars='{"package_install":true,"package_upgrade":true,"coprs_enabled":[],"ipa_replica_kra":false,"ipa_domain": "'${IPA_DOMAIN}'"}'
```


Ansible roles
=============

bootstrap
---------

General bootstrapping tasks to set up networking and Ansible dependecies (Python 2).

common
------

Common tasks for FreeIPA and Dogtag:

 * firewalld
 * SELinux
 * rngd
 * time zones
 * hosts

ipa
---

FreeIPA base package and common facts

ipa-client
----------

Configure host as FreeIPA client

ipa-httpd
---------

Prepare Apache HTTPD for Ipsilon IdP, GSSAPI and SAML2 service point example

ipa-httpexample
---------------

GSSAPI + mod_lookup_identity example

ipa-inventory
-------------

Create local configuration files and scripts for kinit, ssh and Firefox

ipa-ipsilon-idp
---------------

Set up Ipsilon IdP with SAML2, Persona and OpenID

ipa-nfsserver
-------------

Kerberized NFS server and auto.fs for home directories

ipaserver
---------

Install FreeIPA server packages

ipaserver-master
----------------

Set up FreeIPA master

ipaserver-replica
-----------------

Set up FreeIPA replica

ipa-smbserver
-------------

Kerberized Samba/CIFS server

ipa-sp-example
--------------

SAML2 service point example with mod_auth_mellon

ipa-vpnserver
-------------

Kerberized occserv (OpenConnect) VPN server with MS-KKDCP support.

pki
---

Install Dogtag PKI base packages for stand-alone CA

pki-389ds
---------

Configure 389-DS LDAP server for Dogtag

pki-ca
------

Configure Dogtag CA instance

pki-kra
-------

Configure Dogtag KRA instance
