from backend.utils.logger import Logger

@Logger.attach_logger
class ErrorHandler:

    registry = {}

    def __init__(self, context: str = "CLI", debug: bool = False):
        self.context = context
        self.debug = debug

    def handle(self, error: Exception):
        for exc_type in type(error).__mro__:
            if exc_type in self.registry:
                return self.registry[exc_type](error, self)
        return self._default_handler(error)

    def _default_handler(self, error: Exception):
        self.logger.error(f"[{self.context}] Unhandled error: {error}")
        print(f"[Unhandled Error] {error}")
        if self.debug:
            import traceback
            traceback.print_exc()

    @classmethod
    def register(cls, exc_type):
        """Decorator for registering a handler function for a given exception type."""
        def decorator(func):
            cls.registry[exc_type] = func
            return func
        return decorator
