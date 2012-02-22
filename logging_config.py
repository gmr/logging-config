"""Setup the logging options

Example configuration YAML definition object:

{ 'filters': None,
  'formatters': { 'syslog': '%(levelname)s <PID %(process)d:%(processName)s> %(name).%(funcName)s: %(message)s',
                  'verbose': '%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -25s: %(message)s'},
  'handlers': { 'console': { 'class': 'logging.StreamHandler',
                             'debug_only': True,
                             'formatter': 'verbose',
                             'level': 'DEBUG'},
                'syslog': { 'address': '/var/run/syslog',
                            'class': 'logging.handlers.SysLogHandler',
                            'facility': 'local6',
                            'formatter': 'syslog',
                            'level': 'INFO'}},
  'loggers': { 'logging_config': { 'level': 'INFO', 'propagate': True},
               'psycopg2': { 'level': 'INFO', 'propagate': True}}}

"""
__author__ = 'Gavin M. Roy'
__email__ = 'gmr@myyearbook.com'
__date__ = '2012-01-20'
__version__ = '1.0.0'

import hashlib
import logging
from logging.handlers import SysLogHandler
import io
import weakref

_ADDRESS = 'address'
_ARGS_IGNORE = ['class', 'formatter', 'filters', 'level', 'debug_only']
_CLASS = 'class'
_DEBUG_ONLY = 'debug_only'
_DEFAULT_LEVEL = logging.INFO
_FACILITY = 'facility'
_FILTERS = 'filters'
_FORMATTER = 'formatter'
_FORMATTERS = 'formatters'
_HANDLERS = 'handlers'
_LEVEL = 'level'
_LEVELS = 'levels'
_LOGGERS = 'loggers'
_PROPAGATE = 'propagate'


def import_class(module_class):  #param: no cover
    """Import the package for the given module and class string and return the
    handle to the class in the module for creating new instances of the class.

    :param str module_class: The module and class in foo.bar.baz.Class format
    :returns: object

    """
    parts = module_class.split('.')
    cls_name = str(parts[-1])
    module = str('.'.join(parts[0:-1]))

    # Return the class handle
    return getattr(__import__(module, fromlist=cls_name), cls_name)


class Logging(object):
    """Setup and configure logging for the application allowing flexible output
    and better use of the logging module in Python. Closely resembles the
    logging.config.DictConfig functionality in Python 2.7.

    """
    def __init__(self, config, debug=False):
        """Create a new instance of the logging object.

        :param dict config: The configuration data
        :param dict debug: Flag to specify app is in debug mode

        """
        # Default values
        self._config = config
        self._debug = debug
        self._handlers = list()

        # Setup the internal stream handler and logger
        self._stream = self._new_stream()
        self._handler = self._internal_handler()
        self._logger = logging.getLogger('logging_config')
        self._setup_internal_handler()

        # Set a level for this logger
        self._logger.setLevel(logging.DEBUG if debug else logging.INFO)

    def _add_logger_handler(self, logger, handler, level=None):
        """Add the handler to the logger.

        :param logging.Logger logger: The logger to add the handler to
        :param logging.Handler handler: The handler to add
        :param logging.Level level: An optional logger level

        """
        handler_names = self._get_handler_names(logger)
        if handler.get_name() not in handler_names:
            logger.addHandler(handler)
        if isinstance(logger, logging.Logger) and level:
            logger.setLevel(self._get_level(level))

    def _build_arguments(self, config):
        """For the given config dictionary, build out the arguments that will
        be passed to the constructor of the handler.

        :param dict config: The configuration options
        :returns: dict

        """
        out = dict()

        # Determine if this is for the syslog handler
        syslog = (config['class'] == 'logging.handlers.SysLogHandler')

        # Iterate through the keys in the config
        for key in config:

            # Set the logging level
            if key == _LEVEL:
                out[_LEVEL] = self._get_level(config[key])

            # Set the address to the proper format for syslog
            elif key == _ADDRESS:
                if isinstance(config[key], basestring):
                    out[_ADDRESS] = str(config[key])
                elif isinstance(config[key], list) or\
                     isinstance(config[key], tuple):
                    out[_ADDRESS] = config[key][0], config[key][1]

            # If it's facility and a syslog handler, set facility from the name
            elif key == _FACILITY and syslog:
                out[_FACILITY] = SysLogHandler.facility_names[config[key]]

            # It's not special and not in ignore, add it
            elif key not in _ARGS_IGNORE:
                out[key] = config[key]

        self._logger.debug('Arguments: %r', out)
        return out

    def _get_logger(self, logger):
        """Return the logger for the specific logger text.

        :param str logger: The logger name
        :return: logging.Logger

        """
        return logging.getLogger(None if logger == 'root' else logger)

    def _get_handler_names(self, logger):
        """Return a list of handlers for the given logger.

        :param logger.Logger logger: The logger to return the handlers for
        :return list: List of handlers

        """
        out = list()
        for handler in logger.handlers:
            out.append(handler.get_name())
        return out

    def _get_level(self, level_name):
        """Get the logging level for the given level name.

        :param str level_name: The level name
        :returns: int

        """
        self._logger.debug('Fetching constant mapping for %s', level_name)
        return logging._levelNames.get(level_name, logging.INFO)

    def _get_logger_name(self, class_handle, arguments):
        """Get a logger name for when we are creating a logger.

        :param Object class_handle: The class_handle
        :param dict arguments: The arguments for the class
        :returns: str

        """

        logger = dict({'class': class_handle.__name__}.items() +
                      arguments.items())
        return 'logging_config:%x' % (hash(frozenset(logger.items())) &
                                      0xffffffff)

    def _internal_handler(self):
        """Return a StreamHandler for internal logging.

        :returns: logging.StreamHandler

        """
        return logging.StreamHandler(stream=self._stream)

    def _new_handler(self, class_handle, arguments):
        """Return an instance of the specified handler.

        :param Object class_handle: The class to create an instance of
        :param dict arguments: The arguments to pass in
        :returns: Object

        """
        name = self._get_logger_name(class_handle, arguments)

        if name in logging._handlers:
            return logging._handlers[name]

        handler = class_handle(**arguments)
        handler.set_name(name)
        return handler

    def _new_stream(self):
        """Return a new stream object.

        :return: ob.BytesIO

        """
        return io.BytesIO()

    def _setup_filters(self, filters):
        """Iterate through the filters configuration and create a new
        logging.Filter for each filter.

        :param dict filters: Configuration data
        :returns: dict

        """
        out = dict()
        for name in filters or dict():
            self._logger.debug('Creating filter %s: %s', name, filters[name])
            out[name] = logging.Filter(filters[name])
        return out

    def _setup_formatters(self, formatters):
        """Iterate through the formatters configuration and create new
        logging.Formatter for each format.

        :param dict formatters: Configuration data
        :returns: dict

        """
        out = dict()
        for name in formatters or dict():
            self._logger.debug('Creating formatter %s: %s',
                               name, formatters[name])
            out[name] = logging.Formatter(formatters[name])
        return out

    def _setup_handlers(self, handlers, filters, formatters, loggers):
        """Setup the logging handlers with the given filters, formatters and
        configuration options.

        :param dict handlers: The configuration for the handlers
        :param dict filters: Filters to be applied to the handlers
        :params dict formatters: Formatters to be applied to the handlers
        :param list loggers: A list of loggers to add the handlers to
        :returns: list

        """
        out = list()

        # Iterate through the handlers
        for handler_name in handlers:

            # If it's a debug only handler, validate the class is in debug mode
            if handlers[handler_name].get(_DEBUG_ONLY) and not self._debug:
                self._logger.debug('Skipping debug only handler: %s',
                                   handler_name)
                continue

            # Get the class handle
            try:
                class_handle = import_class(handlers[handler_name][_CLASS])
            except KeyError:
                self._logger.debug('Invalid Logging Configuration for %s\n',
                                   handler_name)
                continue

            # Process the dictionary to make cli arguments
            arguments = self._build_arguments(handlers[handler_name])

            # Pull out levels if they're there
            if _LEVEL in arguments:
                level = arguments[_LEVEL]
                del arguments[_LEVEL]
            else:
                level = logging.INFO

            # Create a new instance of the Handler
            handler = self._new_handler(class_handle, arguments)

            # Set the formatter for the handler if specified
            if _FORMATTER in handlers[handler_name]:
                name = handlers[handler_name][_FORMATTER]
                if name in formatters:
                    handler.setFormatter(formatters[name])

            # Set filters for the handler if specified
            if _FILTERS in handlers[handler_name]:
                filter_names = handlers[handler_name][_FILTERS]
                for name in filter_names:
                    if name in filters:
                        handler.addFilter(filters[name])

            # Add the handler to all the specified loggers
            for logger in loggers:
                self._add_logger_handler(logger, handler, level)

            # Add the logger_config logger to this handler
            self._add_logger_handler(self._logger, handler, _DEFAULT_LEVEL)

            # Append the handler to the list
            out.append(handler)

        # Return the handlers
        return out

    def _setup_internal_handler(self):
        """Setup the internal handler, adding to the logger for the module."""
        if not self._logger.handlers:
            self._logger.addHandler(self._handler)

    def _setup_loggers(self, loggers):
        """Iterate through the loggers configuration getting the Logger object
        for each of the named loggers.

        :param dict loggers: Configuration data
        :returns: list

        """
        out = list()
        for logger in loggers or dict():
            level = loggers[logger].get(_LEVEL, logging.INFO)
            self._logger.debug('Fetching %s and setting to %s', logger, level)
            logger_obj = self._get_logger(logger)
            logger_obj.setLevel(level)
            logger_obj.propagate = loggers[logger].get(_PROPAGATE, True)
            out.append(logger_obj)
        return out

    def remove_existing_loggers(self):
        """Remove the existing loggers from the logging module."""
        logging._handlers.clear()
        logging._handlerList = list()

    def remove_root_logger(self):
        """Remove the root logger handlers"""
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    def setup(self):
        """Setup the loggers per the configuration that was passed in when
        the object was created.

        """
        # Setup the filter objects
        filters = self._setup_filters(self._config.get(_FILTERS))

        # Setup the formatter objects
        formatters = self._setup_formatters(self._config.get(_FORMATTERS))

        # Get the loggers from the logger text list
        loggers = self._setup_loggers(self._config.get(_LOGGERS))

        # Setup the handler objects
        self._handlers = self._setup_handlers(self._config.get(_HANDLERS),
                                              filters,
                                              formatters,
                                              loggers)
