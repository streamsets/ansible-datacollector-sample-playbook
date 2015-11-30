streamsets.datacollector
=========

[StreamSets Data Collector](http://streamsets.com) - An open source data collector.

Requirements
------------

The role currently expects that you already have a JRE installed on the target
system. Oracle Java 8 is recommended. This example playbook includes usage of a
third-party role for installing Oracle Java 8.

Role Variables
--------------

Defaults are provided for the most commonly changed parameters in
`defaults/main.yml`. For a full list of available variables please review the
templates directly.

Dependencies
------------

None.

Example Playbook
----------------
This playbook has a `datacollectors.yml` which has an example of how to install
StreamSets Data Collector using the official streamsets.datacollector role,
optionally use the `sdc_config` module to re-configure an existing instance,
and then deploy and start a pipeline.

Using the streamsets.datacollector role for installation already includes
configuration using templates and variables, so using the `sdc_config` module
is not necessary and included for illustration purposes only. The `sdc_config`
module is more useful when using other installation or deployment methods such
as RPM packaging or Docker containers to customize configuration.

Basic usage only requires specifying the role. To run multiple instances on a
single machine you can specify custom values for `sdc_instance` and `http_port`

    - hosts: datacollectors
      roles:
         - { role: streamsets.datacollector, sdc_instance: 'datacollector_1', http_port: 18630 }
         - { role: streamsets.datacollector, sdc_instance: 'datacollector_2', http_port: 18640 }

To enable JMX with no SSL or authentication configure your vars or host_vars file with:

    jmx_enable: true
    jmx_port: <port number>
    jmx_authenticate: false
    jmx_ssl: false

Enabling JMX with authentication also requires specifying a username and password. For example:

    jmx_authenticate: true
    jmx_monitor_user: streamsetsMonitor
    jmx_monitor_password: mysecretpassword

An entry in `${SDC_CONF}/sdc-security.policy` will automatically be added to allow access to all MBeans.

Enabling SSL will use the $SDC_CONF/keystore.jks by default. To override this setting set the following parameters:

    jmx_keystore: </absolute/path/to/keystore>
    jmx_keystore_password: <password or $(cat /path/to/password_file.txt)>

License
-------

[Apache License, Version 2.0](https://tldrlegal.com/license/apache-license-2.0-(apache-2.0))

Author Information
------------------

- [Adam Kunicki](https://streamsets.com/) | [mailing list](https://groups.google.com/a/streamsets.com/d/forum/sdc-user) | [Twitter](https://twitter.com/streamsets)
