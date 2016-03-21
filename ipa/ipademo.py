#!/usr/bin/python
# {key: api.Backend.ldap2.get_attribute_single_value(key) for key in api.Backend.ldap2.schema.tree(ldap.schema.AttributeType).keys()}

import os.path
from pprint import pprint

from ipalib import api

IPA_CFG = os.path.abspath('inventory/default.conf')
NSS_DIR = os.path.abspath('inventory/firefoxprofile')

api.bootstrap(context='cli', conf=IPA_CFG)
api.finalize()
if not api.Backend.rpcclient.isconnected():
    api.Backend.rpcclient.connect(nss_dir=NSS_DIR)


def converter(plugin, *args, **kwargs):
    response = plugin(*args, **kwargs)

    params = {p.name: p for p in plugin.obj.takes_params}
    if hasattr(plugin, 'output_params'):
        params.update({p.name: p for p in plugin.output_params()})

    results = response['result']
    if isinstance(results, dict):
        results = [results]

    for result in results:
        for key, value in result.iteritems():
            param = params.get(key)
            if param is None:
                continue

            if value and isinstance(value, (list, tuple)):
                # workaround for memberof
                if key.startswith(('memberof_', 'memberofindirect_')):
                    result[key] = tuple(param.convert(v) for v in value)
                    continue
                elif not param.multivalue:
                    if len(value) > 1:
                        raise ValueError(key, value)
                    result[key] = param.convert(value[0])
                    continue
            result[key] = param.convert(value)

    return response


pprint(api.Command.ping())
#print(api.Command.dnsconfig_mod(idnsallowsyncptr='FALSE'))

pprint(api.Command.dnsconfig_show())
pprint(converter(api.Command.dnsconfig_show))
pprint(converter(api.Command.user_find))


def get_single_valued():
    from ipalib import api
    from ldap.schema import AttributeType
    if not api.isdone('bootstrap'):
        api.bootstrap(in_server=True)
        api.finalize()
        api.Backend.ldap2.connect()
    ldap2 = api.Backend.ldap2
    name2single = {}
    for nameoroid in ldap2.schema.listall(AttributeType):
        obj = ldap2.schema.get_obj(AttributeType, nameoroid)
        single = ldap2.get_attribute_single_value(nameoroid)
        for name in obj.names:
            name2single[name] = single
    return name2single


