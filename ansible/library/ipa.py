#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Run ipa commands with Kerberos credentials

(c) 2016, Christian Heimes <cheimes@redhat.com>
"""
from ConfigParser import SafeConfigParser
import re
import subprocess
import shlex

from ansible.module_utils.basic import *

DOCUMENTATION = """
---
module: reversezone
short_description: get reverse zone from an IP address
description:
     - get reverse zone from an IP address
version_added: "1.1"
options:
  args:
    description:
      - ipa arguments
    required: true
    default: null
    aliases: []
  principal:
    description:
      - principal to run as
    required: false
    default: admin
    aliases: []
  password:
    description:
      - password for principal
    required: true
    default:
    aliases: []
  ignore_no_modifications:
    description:
      - ignore 'ERROR: no modifications to be performed'
    required: false
    default: false
    aliases: []
  ignore_already_exists:
    description:
      - ignore 'ERROR: ... already exists'
    required: false
    default: false
    aliases: []
author: Christian Heimes
"""

EXAMPLES = """
"""


class IPA(object):
    KINIT = 'kinit'
    KLIST = 'klist'

    def __init__(self, module, cmd, args, principal, password):
        self.module = module
        self.cmd = cmd
        self.args = args
        self.principal = principal
        self.password = password

    def kinit(self):
        rc = subprocess.call([self.KLIST, '-s'])
        if rc == 0:
            # we have a non-expired TGT
            return
        cmd = [self.KINIT, self.principal]
        popen = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout, stderr = popen.communicate(self.password + '\n')
        if popen.returncode != 0:
            raise subprocess.CalledProcessError(popen.returncode, cmd, stdout)

    def ipa_cmd(self):
        cmd = [self.cmd]
        cmd.extend(shlex.split(self.args))
        popen = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = popen.communicate()
        return popen.returncode, stdout, stderr

    def __call__(self):
        self.kinit()
        return self.ipa_cmd()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cmd=dict(default='ipa'),
            args=dict(required=True),
            principal=dict(default='admin'),
            password=dict(required=True),
            result_regex=dict(default=None),
            ignore_no_modifications=dict(default=False, type='bool'),
            ignore_already_exists=dict(default=False, type='bool'),
        )
    )
    cmd = module.params.get('cmd', 'ipa')
    args = module.params.get('args')
    principal = module.params.get('principal', 'admin')
    password = module.params.get('password')
    result_regex = module.params.get('result_regex')
    ignore_nomod = module.params.get('ignore_no_modifications', False)
    ignore_exists = module.params.get('ignore_already_exists', False)

    if '$IPA_SERVER' in args:
        cfg = SafeConfigParser()
        with open('/etc/ipa/default.conf') as f:
            cfg.readfp(f)
        server = cfg.get('global', 'server')
        args = args.replace('$IPA_SERVER', server)

    ipa = IPA(module, cmd, args, principal, password)
    try:
        rc, stdout, stderr = ipa()
    except Exception as e:
        msg = ": ".join((type(e).__name__, str(e)))
        if hasattr(e, 'output'):
            msg = '\n'.join((msg, e.output))
        module.fail_json(msg=msg)

    changed = True
    if rc != 0:
        if ignore_nomod and 'no modifications' in stderr:
            rc = 0
            changed = False
        elif ignore_exists and 'already exists' in stderr:
            rc = 0
            changed = False

    results = []
    if result_regex is not None:
        result_regex = re.compile(result_regex)
        for line in stdout.split('\n'):
            mo = result_regex.search(line)
            if not mo:
                continue
            results.append(mo.group(1))

    kwargs = dict(rc=rc, stdout=stdout, stderr=stderr, changed=changed, results=results)
    if rc != 0:
        module.fail_json(msg='command failed', **kwargs)
    else:
        module.exit_json(**kwargs)


if __name__ == '__main__':
    main()
