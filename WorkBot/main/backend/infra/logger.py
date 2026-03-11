import logging
import json
import os
import threading
from logging.handlers import RotatingFileHandler
from functools import wraps

from backend.infra.paths import MASTER_LOG_FILE

class Logger:
    '''Centralized logging class with per-module loggers, rotating files, and optional JSON formatting.'''

    _loggers = {}                # Store named loggers to prevent duplication
    _lock    = threading.Lock()  # Ensure thread safety, don't want to multi-edit

    @staticmethod
    def get_logger(name='app', log_file='logs/app.log', level=logging.DEBUG, json_format=False):
        '''Creates or retrieves a named logger with rotating file and console handlers.'''

        with Logger._lock:

            if name in Logger._loggers:
                return Logger._loggers[name]

            master_log_file = MASTER_LOG_FILE

            # Ensure master log directory exists
            os.makedirs(os.path.dirname(master_log_file), exist_ok=True)

            # Create logger
            logger = logging.getLogger(name)
            logger.setLevel(level)

            # Prevent duplicate handlers
            if logger.hasHandlers():
                return logger

            # Shared master file handler only
            master_handler = RotatingFileHandler(master_log_file, maxBytes=5_000_000, backupCount=5, delay=False)
            master_handler.setLevel(logging.INFO)

            # Console Handler (Warnings & Errors only)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)

            # Formatters
            formatter = (
                JsonFormatter() if json_format
                else logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - (%(filename)s:%(lineno)d) - %(message)s')
            )

            master_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Attach handlers
            logger.addHandler(master_handler)
            logger.addHandler(console_handler)

            # Store and return logger
            Logger._loggers[name] = logger
            return logger

    @staticmethod
    def set_log_level(name, level):
        '''Dynamically set the log level for a specific logger.'''
        if name in Logger._loggers:
            Logger._loggers[name].setLevel(level)
            for handler in Logger._loggers[name].handlers:
                handler.setLevel(level)

    @staticmethod
    def enable_json_logging(name):
        '''Enable JSON logging format for a specific logger.'''
        if name in Logger._loggers:
            json_formatter = JsonFormatter()
            for handler in Logger._loggers[name].handlers:
                if isinstance(handler, RotatingFileHandler):
                    handler.setFormatter(json_formatter)

    @staticmethod
    def add_external_handler(name, handler):
        '''Attach an external logging handler (e.g., email, syslog, cloud service).'''
        if name in Logger._loggers:
            Logger._loggers[name].addHandler(handler)

    @staticmethod
    def log_exceptions(func):
        '''Decorator to log exceptions using the logger from the class instance, if available.'''
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            instance_logger = None

            # Check if the function is bound to an instance and if the instance has a `logger` attribute
            if args and hasattr(args[0], 'logger') and isinstance(args[0].logger, logging.Logger):
                instance_logger = args[0].logger
            else:
                # Fallback: Use module-level logger if no instance logger is found
                instance_logger = Logger.get_logger(func.__module__)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                instance_logger.error(f'Error in {func.__name__}: {e}', exc_info=True)
                raise  # Ensure the error still propagates

        return wrapper
    
    @staticmethod
    def attach_logger(cls):
        '''
        Decorator that attaches a class-specific logger based on its full module path.

        Example:
            backend.orders.OrderCoordinator
            frontend.cli.WorkBotCLI
        '''
        logger_name = f'{cls.__module__}.{cls.__name__}'

        cls.logger = Logger.get_logger(logger_name)
        
        # detect frozen dataclass
        is_frozen = bool(getattr(getattr(cls, "__dataclass_params__", None), "frozen", False))

        # Patch __init__ to attach to instances as well
        orig_init = cls.__init__

        def new_init(self, *args, **kwargs):

            if is_frozen:
                object.__setattr__(self, 'logger', Logger.get_logger(logger_name))
            else:
                self.logger = Logger.get_logger(logger_name)
            
            orig_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

        
class JsonFormatter(logging.Formatter):
    '''Custom JSON log formatter for structured logging.'''
    def format(self, record):
        return json.dumps({
            'time':       self.formatTime(record),
            'level':      record.levelname,
            'name':       record.name,
            'message':    record.getMessage(),
            'filename':   record.filename,
            'lineno':     record.lineno,
            'funcName':   record.funcName,
            'threadName': record.threadName
        })