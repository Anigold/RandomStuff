from backend.errors.exceptions import *
from backend.errors.error_bus import ErrorBus, ErrorEvent
import traceback

class ServiceErrorBoundary:

    @staticmethod
    def run(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)

        except RepositoryError as err:
            ErrorBus.emit(ErrorEvent(
                type=err.__class__.__name__,
                message=str(err),
                context=fn.__name__,
                layer="repository",
                trace=traceback.format_exc()
            ))

            if isinstance(err, FileLoadError):
                raise OrderNotFoundError(err.message, cause=err)

            raise DomainError(err.message, cause=err)
