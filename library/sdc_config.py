#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import *
import re
import shutil

DOCUMENTATION = """
---
module: datacollector_configuration
short_description: Updates StreamSets Data Collector configuration parameters.
description:
    - Updates StreamSets Data Collector configuration parameters.
options:
"""

EXAMPLES = """
- name: change default http port
  sdc_config: name=http.port value=18640

- name: update config to use https
  sdc_config: name="{{ item.name }}" value="{{ item.value }}"
  with_items:
    - { name: https.port, value: 18631 }
    - { name: https.keystore.path, value: /path/to/custom/keystore.jks }
"""

SDC_CONF = os.environ.get('SDC_CONF')
DEFAULT_SDC_PROPS = \
        os.path.join(SDC_CONF, 'sdc.properties') if SDC_CONF else None

def apply_change(dest, parameter, new_value, check_mode, backup=False):
    old_value = None
    new_config = []

    with open(dest, 'rb') as f:
        lines = f.readlines()

    regexp = re.compile("^(#?%s)(=)(.*)" % parameter)
    for line in lines:
        match = regexp.match(line)
        if match:
            old_value = match.group(3)
            line = '%s=%s' % (parameter, new_value) + os.linesep
        new_config.append(line)

    if not check_mode:
        if backup:
            make_backup(dest)
        with open(dest, 'wb') as f:
            f.writelines(new_config)

    return old_value

def make_backup(orig):
    suffix = '.bak'
    n = 1
    new_name = orig + suffix
    while os.path.exists(new_name):
        new_name = orig + '.' + str(n) + suffix
        n += 1
    shutil.move(orig, new_name)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            dest=dict(required=False, default=DEFAULT_SDC_PROPS),
            parameter=dict(required=True, aliases=['name']),
            value=dict(required=True),
            backup=dict(default=False, type='bool'),
        ),
        supports_check_mode=True,
    )

    if not module.params['dest']:
        module.fail_json(msg='SDC_CONF is not defined, dest must be ' + \
                'specified explicitly.'
        )

    dest = os.path.expanduser(module.params['dest'])
    parameter = module.params['parameter']
    new_value = module.params['value']
    backup = module.params['backup']
    check_mode = module.check_mode

    if os.path.isdir(dest):
        module.fail_json(msg="Destination '%s' should be sdc.properties, " + \
                "but is a directory." % dest
        )

    if not os.path.isfile(dest):
        module.fail_json(msg="File '%s' does not exist." % dest)

    if not parameter or not new_value:
        module.fail_json(msg="Both 'name' (parameter) and 'value' must be " + \
                "specified."
        )

    old_value = apply_change(dest, parameter, new_value, check_mode, backup)

    changed = False
    if not old_value:
        module.fail_json(msg="Parameter '%s' not found." % parameter)
    elif old_value != new_value:
        changed = True

    module.exit_json(
        changed=changed,
        parameter=parameter,
        old_value=old_value,
        new_value=new_value
    )


if __name__ == '__main__':
    main()
