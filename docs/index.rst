.. logging-config documentation master file, created by
   sphinx-quickstart on Thu Feb 23 23:43:23 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

logging-config
==============

A configuration wrapper class for the standard Python logging package. Since
DictConfigurator is not available until 2.7 and I still need to support 2.6,
I wanted a consistent way to handle configuration of application logging.

Currently, this module passes tests in Python 2.5, 2.6 and 2.7.

I've attempted to match the configuration dictionary schema as much as it makes
sense to do so.  For more information on the configuration dictionary schema
check out http://docs.python.org/library/logging.config.html#logging-config-dictschema

Logging
-------

.. autoclass:: logging_config.Logging
  :members:
  :undoc-members:
  :show-inheritance:
  
Example Use
-----------

The following example creates multiple handlers, with the console handler only
being created if debug=True were to be passed into the Logging constructor::

    config = {'loggers': {'pika': {'propagate': True, 'level': 'INFO'},
                          'tinman': {'propagate': True, 'level': 'DEBUG'}},
             'formatters': {'syslog': ('%(levelname)s <PID %(process)d:%(processName)s> '
                                       '%(name).%(funcName)s: %(message)s'),
                            'verbose': ('%(levelname) -10s %(asctime)s %(name) -30s '
                                        '%(funcName) -25s: %(message)s')},
             'filters': {'myapp': 'myapp.*'},
             'handlers': {'syslog': {'facility': 'local6',
                                     'level': 'INFO',
                                     'filters': ['myapp'],
                                     'formatter': 'syslog',
                                     'class': 'logging.handlers.SysLogHandler',
                                     'address': '/var/run/syslog'},
                          'console': {'formatter': 'verbose',
                                      'debug_only': True,
                                      'class': 'logging.StreamHandler',
                                      'level': 'DEBUG'}}}

    cfg = logging_config.Logging(config)
    cfg.setup()
