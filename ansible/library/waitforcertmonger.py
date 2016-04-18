#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Wait for certmonger

(c) 2016, Christian Heimes <cheimes@redhat.com>
"""
import subprocess
import time

from ansible.module_utils.basic import *

DOCUMENTATION = """
---
module: waitforcertmonger
short_description: Wait for certmonger to fetch a cert
description:
version_added: "1.0"
options:
  max_retries:
    description:
      - how many retries
    required: false
    default: 6
    aliases: []
  sleep:
    description:
      - how long to sleep between retries
    required: false
    default: 5
    aliases: []
author: Christian Heimes
"""

EXAMPLES = """
# Get reverse zone
- waitforcertmonger
"""


class CAUnreachable(Exception):
    pass


def get_status():
    stdout = subprocess.check_output(['ipa-getcert', 'list'])
    if 'CA_UNREACHABLE' in stdout:
        raise CAUnreachable(stdout)
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith('status') and line != 'status: MONITORING':
            return line, stdout
    return True, stdout


def main():
    module = AnsibleModule(
        argument_spec=dict(
            max_retries=dict(default=10, type='int'),
            sleep=dict(default=3, type='int'),
        )
    )

    max_retries = int(module.params.get('max_retries', 6))
    sleep = int(module.params.get('sleep', 5))

    states = []
    kwargs = {'states': states, 'stdout': '', 'changed': False}

    for i in range(1, max_retries + 1):
        try:
            status, stdout = get_status()
        except CAUnreachable as e:
            status = 'CA_UNREACHABLE'
            stdout = e.args[0]
            subprocess.check_call(['systemctl', 'restart', 'certmonger.service'])

        kwargs['stdout'] = stdout
        if status is True:
            module.exit_json(**kwargs)
        else:
            time.sleep(sleep)
            kwargs['changed'] = True
            kwargs['states'].append(status)

    module.fail_json(msg='certmonger failed to retrieve cert', **kwargs)


if __name__ == '__main__':
    main()
