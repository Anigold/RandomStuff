import logging
import json
import os
import threading
from logging.handlers import RotatingFileHandler
from functools import wraps

class Logger:
    '''Centralized logging class with per-module loggers, rotating files, and optional JSON formatting.'''

    _loggers = {}                # Store named loggers to prevent duplication
    _lock    = threading.Lock()  # Ensure thread safety, don't want to multi-edit

    @staticmethod
    def get_logger(name='app', log_file='logs/app.log', level=logging.DEBUG, json_format=False):
        '''Creates or retrieves a named logger with rotating file and console handlers.'''

        with Logger._lock:

            if name in Logger._loggers: return Logger._loggers[name]

            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            # Create logger
            logger = logging.getLogger(name)
            logger.setLevel(level)

            # # Prevent duplicate handlers
            # if logger.hasHandlers(): return logger 

            master_log_file = 'logs/master.log'

            # File Handler (Rotating)
            file_handler   = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5, delay=False)
            master_handler = RotatingFileHandler(master_log_file, maxBytes=5_000_000, backupCount=5, delay=False)

            file_handler.setLevel(logging.INFO)
            master_handler.setLevel(logging.INFO)

            # Console Handler (Warnings & Errors only)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)

            # Formatters
            formatter = JsonFormatter() if json_format else logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

            file_handler.setFormatter(formatter)
            master_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)  # Red for visibility

            # Attach handlers
            logger.addHandler(file_handler)
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
 
    def attach_logger(cls):
        '''Decorator to automatically attach a class-specific logger.'''
        
        log_file = f'logs/{cls.__name__}.log'
        cls.logger = Logger.get_logger(cls.__name__, log_file=log_file)

        orig_init = cls.__init__  # Store original __init__

        def new_init(self, *args, **kwargs):
            
            self.logger = Logger.get_logger(cls.__name__, log_file=log_file)  # Attach class-specific logger
            orig_init(self, *args, **kwargs)  # Call original __init__

        cls.__init__ = new_init  # Replace __init__
        return cls
    
class JsonFormatter(logging.Formatter):
    '''Custom JSON log formatter for structured logging.'''
    def format(self, record):
        log_record = {
            'time': self.formatTime(record),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        return json.dumps(log_record)

