"""
logging_config_tests.py

"""

__author__ = 'Gavin M. Roy'
__email__ = 'gmr@myyearbook.com'
__since__ = '2012-02-12'

import sys
sys.path.insert(0, '..')

import logging
import mock
from logging.handlers import SysLogHandler
import platform
import socket
import unittest

import logging_config


_DEBUG = 'DEBUG'
_ERROR = 'ERROR'
_INFO  = 'INFO'

_FORMATTERS = logging_config._FORMATTERS
_FILTERS = logging_config._FILTERS
_HANDLERS = logging_config._HANDLERS
_LEVELS = logging_config._LEVELS
_LOGGERS = logging_config._LOGGERS


_LOGGER_NAME = 'logging_config'
_TEST_LOGGERS = {_LOGGER_NAME: {logging_config._PROPAGATE: True,
                                logging_config._LEVEL: _INFO}}

_CONSOLE = {logging_config._FORMATTER: 'verbose',
            logging_config._DEBUG_ONLY: True,
            _FILTERS: ['test'],
            logging_config._CLASS: 'logging.StreamHandler',
            logging_config._LEVEL: _DEBUG}

_SYSLOG =  {logging_config._FACILITY: 'local6',
            logging_config._LEVEL: _INFO,
            logging_config._FORMATTER: 'syslog',
            logging_config._CLASS: 'logging.handlers.SysLogHandler',
            logging_config._ADDRESS: ('localhost',
                                      logging.handlers.SYSLOG_UDP_PORT)}

_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -25s: '
           '%(message)s')


def print_message(message, *arguments):
    print message % arguments


class LoggingConfigTests(unittest.TestCase):

    def _syslog_address(self):
        system = platform.system()
        if system == 'Darwin':
            return '/var/run/syslog'
        return '/dev/log'

    def setUp(self):
        self._config = {_FORMATTERS: {'syslog': _FORMAT,
                                      'verbose': _FORMAT},
                        _FILTERS: {'test': _LOGGER_NAME},
                        _LOGGERS: _TEST_LOGGERS.copy(),
                        _HANDLERS: {'console': _CONSOLE.copy(),
                                    'syslog': _SYSLOG.copy()},
                        _LEVELS: {'pika': _INFO}}


        handler = mock.Mock()
        handler.get_name = mock.Mock(return_value='handle_getName')
        handler.set_same = mock.Mock()

        self._root_handler = mock.Mock()
        self._root_handler.handlers = [handler]

        self._logger = logging.getLogger(_LOGGER_NAME)
        self._logger.handlers = [handler]

        self._logging = logging_config.Logging(self._config)

        self.setUpLogger(self._logging)

        logging_config._get_root_logger =\
            mock.Mock(return_value=self._root_handler)

    def setUpLogger(self, obj):
        obj._logger.debug = print_message
        obj._logger.error = print_message
        obj._logger.info = print_message
        obj._logger.warning = print_message

    def tearDown(self):
        del self._logging

    def test_build_arguments(self):
        config = self._config[_HANDLERS]['syslog']
        config['socktype'] = socket.SOCK_DGRAM
        args = self._logging._build_arguments(config)
        self.assertEqual(args['facility'],
                         SysLogHandler.facility_names['local6'])
        self.assertEqual(args['address'],
            ('localhost', logging.handlers.SYSLOG_UDP_PORT))
        config['address'] = self._syslog_address()
        args = self._logging._build_arguments(config)
        self.assertEqual(args['address'], config['address'])

    def test_get_level(self):
        self.assertEqual(self._logging._get_level(_DEBUG), logging.DEBUG)

    def test_setup_formatters(self):
        formatters = self._logging._setup_formatters(self._config[_FORMATTERS])
        self.assertTrue(isinstance(formatters['syslog'], logging.Formatter))
        self.assertEqual(formatters['syslog']._fmt, _FORMAT)

    def test_setup_filters(self):
        filters = self._logging._setup_filters(self._config[_FILTERS])
        self.assertTrue(isinstance(filters['test'], logging.Filter))
        self.assertEqual(filters['test'].name, _LOGGER_NAME)

    def test_setup_loggers(self):
        logger = self._logging._setup_loggers(self._config[_LOGGERS])[0]
        self.assertTrue(isinstance(logger, logging.Logger))
        print logger.level
        self.assertEqual(logger.level, logging.INFO)


    def test_get_handler_names(self):
        handlers = self._logging._get_handler_names(self._logger)
        self.assertEqual(handlers[0],
                         self._logger.handlers[0].get_name())

    def test_new_handler(self):
        response = self._logging._new_handler(logging.StreamHandler, dict())
        self.assertTrue(isinstance(response, logging.StreamHandler))

        # Test second pass through
        response = self._logging._new_handler(logging.StreamHandler, dict())
        self.assertTrue(isinstance(response, logging.StreamHandler))

    def test_setup_handlers(self):
        # Setup the filter objects
        filters = self._logging._setup_filters(self._config[_FILTERS])

        # Setup the formatter objects
        formatters = self._logging._setup_formatters(self._config[_FORMATTERS])

        # Get the loggers from the logger text list
        loggers = self._logging._setup_loggers(self._config[_LOGGERS])

        handlers = self._logging._setup_handlers(self._config[_HANDLERS],
                                                 formatters,
                                                 filters,
                                                 loggers)

        # We should only have one handler since the other is debug only
        self.assertEqual(1,  len(handlers))

    def test_setup(self):
        handler = mock.Mock()
        logger = mock.Mock()
        logger.handlers = list()
        self._logging._new_handler = mock.Mock(return_value=handler)
        self._logging._get_logger = mock.Mock(return_value=logger)
        self._logging.setup()
        logger.addHandler.assert_called_with(handler)

    def test_setup_missing_class(self):
        del self._config[_HANDLERS]['syslog'][logging_config._CLASS]
        cfg_obj = logging_config.Logging(self._config, True)
        cfg_obj.setup()
        self.assertTrue(isinstance(cfg_obj._handlers[0], logging.StreamHandler))

    def test_setup_missing_level(self):
        del self._config[_HANDLERS]['syslog'][logging_config._LEVEL]
        cfg_obj = logging_config.Logging(self._config)
        self.setUpLogger(cfg_obj)
        cfg_obj.setup()
        self.assertTrue(isinstance(cfg_obj._handlers[0],
                                   logging.handlers.SysLogHandler))

    def test_get_root_logger(self):
        self.assertEqual(self._logging._get_logger('root'), logging.root)

    def test_setup_internal_handler(self):
        self._logging._logger.handlers = list()
        self._logging._setup_internal_handler()
        self.assertTrue(isinstance(self._logging._logger.handlers[0],
                                   logging.handlers.MemoryHandler))

    def test_remove_existing_loggers(self):
        self._logging.remove_existing_loggers()
        self.assertEqual(len(logging._handlers), 0)

    def test_remove_root_logger(self):
        self._logging.remove_root_logger()
        self.assertEqual(len(logging.root.handlers), 0)


