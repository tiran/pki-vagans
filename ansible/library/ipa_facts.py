#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# ipa_facts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ipa_facts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import sys

from ansible.module_utils.basic import AnsibleModule

try:
    from ipalib import api
    from ipaplatform.paths import paths
    from ipapython import ipautil, sysrestore, version
    from ipapython.dn import DN
except ImportError:
    HAS_IPALIB = False
else:
    HAS_IPALIB = True


try:
    from ipaserver.install.installutils import is_ipa_configured
    from ipaserver.install import certs
    from ipaserver.install.cainstance import CAInstance
    from ipaserver.install.krainstance import KRAInstance
except ImportError:
    HAS_IPASERVER = False
else:
    HAS_IPASERVER = True


DOCUMENTATION = '''
---
module: ipa_facts
author: Christian Heimes (@tiran)
short_description: Gather facts about FreeIPA installation.
description:
 - Requires python2-ipaclient to gather facts of a client.
 - Requires python2-ipaserver to gether facts of a server.
 - Prior to FreeIPA 4.3 the packages were called ipaserver and ipaclient.
version_added: "1.0"
options:
  domain:
    description:
      - domain name
    required: true
    aliases: []
  realm:
    description:
      - Kerberos realm name (default: upper case domain name)
    required: false
    default: domain.upper()
    aliases: []
  fact_key:
    description:
      -
    required: false
    default: "ipa"
    aliases: []
'''

EXAMPLES = '''
# Get facts
- ipa_facts: domain={{ ansible_domain }}
- debug: msg={{ ipa.realm }}
- debug: msg={{ ipa.configured.server }}
- debug: msg={{ ipa.paths.IPA_CA_CRT }}
- debug: vars={{ hostvars[inventory_hostname]['ipa'] }}
'''

RETURN = '''
ansible_facts:
  description:
    - "api_env" are ipalib.api.env attributes
    - "basedn": str
    - "configured": ca, client, kra, server
    - "domain": str
    - "packages": ipalib, ipaserver
    - "paths" are ipaplatform.paths.paths attributes
    - "realm": str
    - "version":
  returned: always
  type: dict
'''

if sys.version_info.major >= 3:
    text = str
else:
    text = unicode


def get_api_env():
    # get api.env
    if not api.isdone('bootstrap'):
        api.bootstrap(context='cli')

    result = {}
    for name in dir(api.env):
        if name.startswith('_'):
            continue
        value = getattr(api.env, name)
        if isinstance(value, (str, text, bool, int)):
            result[name] = value
        elif isinstance(value, DN):
            result[name] = str(value)
    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            domain=dict(required=True, type='str'),
            realm=dict(required=False, type='str', default=None),
            fact_key=dict(required=False, type='str', default='ipa'),
        )
    )

    if not HAS_IPALIB:
        module.fail_json(
            msg='ipalib package is not available, install python2-ipaclient.'
        )

    # get / validate arguments
    domain = module.params['domain']
    realm = module.params['realm']
    fact_key = module.params['fact_key']
    if '.' not in domain or domain != domain.lower():
        raise ValueError(domain)
    if realm is None:
        realm = domain.upper()

    # parse version
    version_info = []
    for part in version.VERSION.split('.'):
        # DEV versions look like:
        # 4.4.90.201610191151GITd852c00
        # 4.4.90.dev201701071308+git2e43db1
        if part.startswith('dev') or 'GIT' in part:
            version_info.append(part)
        else:
            version_info.append(int(part))

    ipa = dict(
        domain=domain,
        realm=realm,
        basedn=str(ipautil.realm_to_suffix(realm)),
        packages=dict(
            ipalib=HAS_IPALIB,
            ipaserver=HAS_IPASERVER,
        ),
        configured=dict(
            client=False,
            server=False,
            ca=False,
            kra=False,
        ),
        version=dict(
            api_version=version.API_VERSION,
            num_version=version.NUM_VERSION,
            vendor_version=version.VENDOR_VERSION,
            version=version.VERSION,
            version_info=version_info,
        ),
        paths={name: getattr(paths, name)
               for name in dir(paths) if name[0].isupper()},
        api_env={},
    )

    fstore = sysrestore.FileStore(paths.IPA_CLIENT_SYSRESTORE)
    if os.path.isfile(paths.IPA_DEFAULT_CONF) and fstore.has_files():
        ipa['configured']['client'] = True

    if ipa['configured']['client']:
        ipa['api_env'].update(get_api_env())
        ipa['basedn'] = ipa['api_env']['basedn']

        if ipa['domain'] != ipa['api_env']['domain']:
            raise ValueError('domain {} != {}'.format(
                ipa['domain'], ipa['api_env']['domain']))

        if ipa['realm'] != ipa['api_env']['realm']:
            raise ValueError('realm {} != {}'.format(
                ipa['realm'], ipa['api_env']['realm']))

    if HAS_IPASERVER:
        if is_ipa_configured():
            ca = CAInstance(ipa['realm'], certs.NSS_DIR)
            kra = KRAInstance(ipa['realm'])
            ipa['configured'].update(
                server=True,
                ca=ca.is_installed() and ca.is_configured(),
                kra=kra.is_installed() and kra.is_configured()
            )

    module.exit_json(
        changed=False,
        ansible_facts={
            fact_key: ipa,
        },
    )


if __name__ == '__main__':
    main()
