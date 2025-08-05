import logging
import json
import os
import threading
from logging.handlers import RotatingFileHandler
from functools import wraps

from config.paths import MASTER_LOG_FILE

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
            if logger.hasHandlers(): return logger 

            master_log_file = MASTER_LOG_FILE

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
            console_handler.setFormatter(formatter) 

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
    
    # @staticmethod
    # def log_exceptions(func, logger=None):
    #     '''Decorator to log exceptions using a given logger (defaults to module-level logger).'''

    #     @wraps(func)
    #     def wrapper(*args, **kwargs):

    #         # TIL: "nonlocal" references a variable from the outer scope from the in-line reference.  
    #         # I have found contradicting information whether it is exactly one scope up, or the first
    #         # instance of the variable before arriving at the global scope.
    #         # I should test, but I won't...

    #         # Okay, I tested it. It unravels the scope until it finds the variable.
    #         # It is impossible to call "nonlocal" on a variable which doesn't exist, or one that exists
    #         # in the global scope.

    #         # Now ask me why we shouldn't instead just use depedency injection for the variable state.

    #         # Excellent question. This lets us provide a default logger without requiring an explicit argument.
    #         # This is nice for the wrapper/decorator style where we're just attaching a 
    #         # function reference above another function and don't necessarily know if a logger is available
    #         # to pass down.

    #         # This is dumb because we can run the risk of a hidden namespace collision, n-files deep. So we won't be doing this.
    #         # A nice exercise though.

    #         # nonlocal logger 
    #         # if logger is None:
    #         #     logger = Logger.get_logger(func.__module__)

    #         logger = logger if logger else Logger.get_logger(func.__module__)
    #         try:
    #             return func(*args, **kwargs)
    #         except Exception as e:
    #             logger.error(f'Error in {func.__name__}: {e}', exc_info=True)
    #             raise  
    #     return wrapper
 
    @staticmethod
    def attach_logger(cls):
        """
        Decorator that attaches a class-specific logger based on its full module path.
        
        Example:
            backend.orders.OrderCoordinator → logs/backend/orders/OrderCoordinator.log
            frontend.cli.WorkBotCLI         → logs/frontend/cli/WorkBotCLI.log
        """
        module_path = cls.__module__.replace('.', '/')
        log_file    = f'logs/{module_path}/{cls.__name__}.log'
        logger_name = f'{cls.__module__}.{cls.__name__}'

        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        cls.logger = Logger.get_logger(logger_name, log_file=log_file)

        # Patch __init__ to attach to instances as well
        orig_init = cls.__init__

        def new_init(self, *args, **kwargs):
            self.logger = Logger.get_logger(logger_name, log_file=log_file)
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

