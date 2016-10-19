import os
import subprocess
import sys

from ansible.module_utils.basic import AnsibleModule

from ipalib import api
from ipaplatform.paths import paths
from ipapython import ipautil, sysrestore, version
from ipapython.dn import DN

try:
    from ipaserver.install.installutils import is_ipa_configured
except ImportError:
    ipaserver_package = False
else:
    ipaserver_package = True
    # from ipaserver.install.cainstance import is_ca_installed_locally
    from ipaserver.install import certs
    from ipaserver.install.cainstance import CAInstance
    from ipaserver.install.krainstance import KRAInstance


DOCUMENTATION = '''
---
module: ipa_facts
short_description: Gather facts about FreeIPA installation
description:
version_added: "1.0"
options:
  domain:
    description:
      - domain name
    required: true
    aliases: []
author: Christian Heimes
'''

EXAMPLES = '''
# Get facts
- ipa_facts: domain={{ ansible_domain }}
- debug: msg={{ ipa.realm }}
- debug: msg={{ ipa.configured.server }}
- debug: msg={{ ipa.paths.IPA_CA_CRT }}
'''

if sys.version_info.major >= 3:
    text = str
else:
    text = unicode


def get_api_env():
    # get api.env
    if not api.isdone('bootstrap'):
        # Workaround for FreeIPA 4.4, use host keytab to fetch LDAP
        # schema cache.
        os.environ['KRB5CCNAME'] = '/tmp/krb5cc_workaround'
        os.environ['KRB5_CLIENT_KTNAME'] = '/etc/krb5.keytab'
        try:
            api.bootstrap(context='cli')
            api.finalize()
        finally:
            os.environ.pop('KRB5_CLIENT_KTNAME')
            subprocess.Popen(['kdestroy', '-q'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE).communicate()
            os.environ.pop('KRB5CCNAME')

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
        )
    )
    domain = module.params['domain']
    if '.' not in domain or domain != domain.lower():
        raise ValueError(domain)

    version_info = []
    for part in version.VERSION.split('.'):
        # DEV versions look like 4.4.90.201610191151GITd852c00
        if 'GIT' in part:
            version_info.append(part)
        else:
            version_info.append(int(part))

    ipa = dict(
        domain=domain,
        realm=None,
        basedn=None,
        packages=dict(
            ipaserver=ipaserver_package
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
    ipa['configured']['client'] = (
        os.path.isfile(paths.IPA_DEFAULT_CONF) and fstore.has_files())

    if ipa['configured']['client']:
        ipa['api_env'].update(get_api_env())
        if ipa['domain'] != ipa['api_env']['domain']:
            raise ValueError('domain {} != {}'.format(domain, ipa['api_env']['domain']))
        ipa['realm'] = ipa['api_env']['realm']
        ipa['basedn'] = ipa['api_env']['basedn']
    else:
        ipa['realm'] = domain.upper()
        ipa['basedn'] = str(ipautil.realm_to_suffix(domain.upper()))

    if ipaserver_package:
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
        ansible_facts=dict(ipa=ipa),
    )


if __name__ == '__main__':
    main()
