#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import *
import copy
import os
from subprocess import Popen, PIPE, STDOUT
import time

DOCUMENTATION = """
---
module: sdc_pipeline
short_description: Performs common actions on a StreamSets pipeline
description:
    - Performs common actions such as list, status, start, stop, reset,
      import, export, and delete of pipelines in StreamSets Data Collector.
author: "StreamSets, @streamsets"
requirements:
    - StreamSets Data Collector should be installed on the target hosts.
options:
    sdc_dist:
        description:
            - Path where StreamSets Data Collector is installed.
        required: false
        default: SDC_DIST environment variable.
    url:
        description:
            - URL of Data Collector UI.
        required: false
        default: http://localhost:18630
    auth_type:
        description:
            - Authentication type for this instance of Data Collector
        required: false
        default: form
        choices: [none, basic, digest, form]
    user:
        description:
            - Username to authenticate with.
        required: false
        default: admin
    password:
        description:
            - Password to authenticate with.
        required: false
        default: admin
    action:
        description:
            - The action to perform.
        required: true
        choices: [list, status, start, stop, reset, import, export, delete]
    pipeline:
        description:
            - The name of the pipeline to operate on. Not required for 'list'
    src:
        description:
            - Path to JSON file to import. Used only with the 'import' action.
    dest:
        description:
            - Path to JSON file to write. Used only with the 'export' action.
"""

EXAMPLES = """
- name: updating load_balance policy
  vertica_configuration: name=failovertostandbyafter value='8 hours'
"""

actions = {
    'list': ['store', 'list'],
    'status': ['manager', 'status'],
    'start': ['manager', 'start'],
    'stop': ['manager', 'stop'],
    'reset': ['manager', 'reset-origin'],
    'import': ['store', 'import'],
    'export': ['store', 'export'],
    'delete': ['store', 'delete'],
}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            sdc_dist=dict(default=os.environ.get('SDC_DIST')),
            url=dict(default='http://localhost:18630', aliases=['instance']),
            action=dict(required=True),
            pipeline=dict(default=None),
            src=dict(default=None),
            dest=dict(default=None),
            auth_type=dict(default='form'),
            user=dict(default='admin'),
            password=dict(default='admin'),
        ),
        supports_check_mode=True,
    )

    sdc_dist = module.params['sdc_dist']
    url = module.params['url']
    action = module.params['action']
    pipeline = module.params['pipeline']
    src = module.params['src']
    dest = module.params['dest']
    auth_type = module.params['auth_type']
    user = module.params['user']
    password = module.params['password']

    if sdc_dist is not None:
        if not os.path.exists(sdc_dist):
            module.fail_json(msg="Path '%s' does not exist" % sdc_dist)
    else:
        module.fail_json(
            msg="Since the SDC_DIST environment variable is not set, you " +
                "must specify the 'sdc_dist' argument to Ansible."
        )

    if 'list' != action and pipeline is None:
        module.fail_json(
            msg='pipeline must be specified for this action.'
        )

    if 'import' == action and src is None:
        module.fail_json(
            msg='src must be specified when importing a pipeline.'
        )

    if 'export' == action and dest is None:
        module.fail_json(
            msg='dest must be specified when exporting a pipeline.'
        )

    changed = False

    streamsets_cli = os.path.join(sdc_dist, 'bin', 'streamsets')

    args = []
    if pipeline:
        args = args + ['--name', pipeline]

    if src:
        args = args + ['--file', src]

    if dest:
        args = args + ['--file', dest]

    command = build_command(
        [
            streamsets_cli,
            'cli',
            '--auth-type',
            auth_type,
            '--url',
            url,
            '--user',
            user,
            '--password',
            password,
        ],
        action,
        args
    )

    # Used for result output only
    str_command = ' '.join(command)

    if not module.check_mode:
        p = Popen(
            command,
            shell=False,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            close_fds=True
        )
        result = p.stdout.read()
        time.sleep(1)

        # The CLI currently always returns exit code 0, so we look for
        # a parseable JSON response to determine success/failure.
        try:
            parsed_result = json.loads(result)
            changed = True
        except ValueError as e:
            # In some cases we wish to just report that a change wasn't needed.
            parsed_result = result

            if is_skipped(result):
                result = None
            else:
                module.fail_json(msg=result)
    else:
        parsed_result = 'Not run in check mode.'

    module.exit_json(
        changed=changed,
        command=str_command,
        result=parsed_result,
    )


def build_command(base_command, action, args):
    return base_command + actions[action] + args


def is_skipped(result):
    skipped = False
    # Pipeline exists
    if 'CONTAINER_0201' in result:
        skipped = True
    # Pipeline already in desired state
    elif 'CONTAINER_0102' or 'CONTAINER_0166' in result:
        skipped = True
    return skipped


if __name__ == '__main__':
    main()
