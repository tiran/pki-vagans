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
sudo dnf install ansible libvirt vagrant vagrant-libvirt vagrant-hostmanager
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
$ vagrant up --no-provision
$ vagrant provision
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
$ ./ipa_kinit admin
$ ./ipa_firefox
$ ./ipa_ssh admin@client1.ipa.example
```

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

Copy or symlink files or directories with RPMs into pki/rpms. The Ansible
playbook will pick up all RPMs (even in symlinked and nested directory
structures) and install them.

When something fails
--------------------

```shell
$ sudo systemctl restart libvirtd.service
$ vagrant provision
```
