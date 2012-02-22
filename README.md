logging-config
==============

A configuration wrapper class for the standard Python logging package. Since
DictConfigurator is not available until 2.7 and I still need to support 2.6,
I wanted a consistent way to handle configuration of application logging.

I've attempted to match the configuration dictionary schema as much as it makes
sense to do so.  For more information on the configuration dictionary schema
check out http://docs.python.org/library/logging.config.html#logging-config-dictschema

Example Config
--------------

  {'loggers': {'pika': {'propagate': True, 'level': 'INFO'},
               'tinman': {'propagate': True, 'level': 'INFO'}},
   'formatters': {'syslog': ('%(levelname)s <PID %(process)d:%(processName)s> '
                             '%(name).%(funcName)s: %(message)s'),
                  'verbose': ('%(levelname) -10s %(asctime)s %(name) -30s '
                              '%(funcName) -25s: %(message)s')},
   'filters': None,
   'handlers': {'syslog': {'facility': 'local6',
                           'level': 'INFO',
                           'formatter': 'syslog',
                           'class': 'logging.handlers.SysLogHandler',
                           'address': '/var/run/syslog'},
                'console': {'formatter': 'verbose',
                            'debug_only': True,
                            'class': 'logging.StreamHandler',
                            'level': 'DEBUG'}}}

Example use
-----------

Given a yaml file "example.yaml":

    %YAML 1.2
    ---
    loggers:
      pika:
        level: INFO
        propagate: True
      tinman:
        level: INFO
        propagate: True
      file:
        filename: /var/log/example.log
        class: logging.RotatingFileHandler
        mode: a
        maxBytes: 104857600
        backupCount: 6
        encoding: UTF-8
        delay: False
        formatter: verbose
    filters:
      my_logger: my_app.*
    formatters:
      verbose: "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -25s: %(message)s"
      syslog: "%(levelname)s <PID %(process)d:%(processName)s> %(name).%(funcName)s: %(message)s"
    handlers:
      console:
        class: logging.StreamHandler
        formatter: verbose
        debug_only: True
        level: DEBUG
      syslog:
        class: logging.handlers.SysLogHandler
        facility: local6
        address: /var/run/syslog
        filters: [my_logger]
        formatter: syslog
        level: INFO

The following code will setup the logging module with the specified handlers:

    import logging_config
    import yaml

    with open('example.yaml', 'r') as handle:
        config = yaml.load(handle)

    cfg = logging_config.Logging(config)
    cfg.setup()
