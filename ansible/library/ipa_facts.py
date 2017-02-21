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
import numbers
import sys

from ansible.module_utils.basic import AnsibleModule

try:
    from ipalib import api
except ImportError:
    HAS_IPALIB = False
else:
    HAS_IPALIB = True
    from ipaplatform.paths import paths
    from ipapython import version
    from ipapython.dn import DN
    try:
        # FreeIPA >= 4.5
        from ipalib.install import sysrestore
    except ImportError:
        # FreeIPA 4.4 and older
        from ipapython import sysrestore

try:
    import ipaserver  # noqa: F401
except ImportError:
    HAS_IPASERVER = False
else:
    HAS_IPASERVER = True
    from ipaserver.install.installutils import is_ipa_configured
    from ipaserver.install.bindinstance import BindInstance
    from ipaserver.install.cainstance import CAInstance
    from ipaserver.install.krainstance import KRAInstance


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
  context:
    description:
      - FreeIPA API context
    required: false
    default: "cli"
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
    - "configured": dns, ca, client, kra, server
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


def get_api_env(context):
    # get api.env
    if not api.isdone('bootstrap'):
        # only call bootstrap, finalize() triggers a download that requires
        # valid Kerberos credentials.
        api.bootstrap(context=context)

    result = {}
    for name in dir(api.env):
        if name.startswith('_'):
            continue
        value = getattr(api.env, name)
        if isinstance(value, (str, text, bool, numbers.Real)):
            result[name] = value
        elif value is None:
            result[name] = None
        elif isinstance(value, DN):
            result[name] = str(value)
    return result


def get_ipa_version():
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

    return dict(
        api_version=version.API_VERSION,
        num_version=version.NUM_VERSION,
        vendor_version=version.VENDOR_VERSION,
        version=version.VERSION,
        version_info=version_info,
    )


def main():
    module = AnsibleModule(
        argument_spec=dict(
            domain=dict(required=True, type='str'),
            realm=dict(required=False, type='str', default=None),
            context=dict(required=False, type='str', default="cli"),
        )
    )

    # get / validate arguments
    domain = module.params['domain']
    realm = module.params['realm']
    if '.' not in domain or domain != domain.lower():
        module.fail_json(
            msg='Invalid domain {}, a lower case string '
                'with at least one dot is expected.'.format(domain)
        )
    if realm is None:
        realm = domain.upper()

    ipa_fact = dict(
        domain=domain,
        realm=realm,
        basedn=','.join('dc=' + p for p in realm.lower().split('.')),
        packages=dict(
            ipalib=HAS_IPALIB,
            ipaserver=HAS_IPASERVER,
        ),
        configured=dict(
            client=False,
            server=False,
            dns=False,
            ca=False,
            kra=False,
        ),
        version=None,
        paths=None,
        api_env=None,
    )

    if HAS_IPALIB:
        ipa_fact['version'] = get_ipa_version()
        ipa_fact['paths'] = {
            name: getattr(paths, name)
            for name in dir(paths) if name[0].isupper()
        }

        fstore = sysrestore.FileStore(paths.IPA_CLIENT_SYSRESTORE)
        if os.path.isfile(paths.IPA_DEFAULT_CONF) and fstore.has_files():
            # ipalib package is present and client is configured.
            ipa_fact['configured']['client'] = True
            ipa_fact['api_env'] = get_api_env(module.params['context'])
            ipa_fact['basedn'] = ipa_fact['api_env']['basedn']

            if ipa_fact['domain'] != ipa_fact['api_env']['domain']:
                module.fail_json(
                    msg='domain mismatch: {} != {}.'.format(
                        ipa_fact['domain'], ipa_fact['api_env']['domain'])
                )

            if ipa_fact['realm'] != ipa_fact['api_env']['realm']:
                module.fail_json(
                    msg='realm mismatch: {} != {}.'.format(
                        ipa_fact['realm'], ipa_fact['api_env']['realm'])
                )

        if HAS_IPASERVER:
            if is_ipa_configured():
                # ipaserver package is present and server is configured.
                bind = BindInstance(ipa_fact['realm'])
                ca = CAInstance(ipa_fact['realm'])
                kra = KRAInstance(ipa_fact['realm'])
                ipa_fact['configured'].update(
                    server=True,
                    dns=bind.is_configured(),
                    ca=ca.is_installed() and ca.is_configured(),
                    kra=kra.is_installed() and kra.is_configured()
                )

    module.exit_json(
        changed=False,
        ansible_facts=dict(
            ipa=ipa_fact
        )
    )


if __name__ == '__main__':
    main()
