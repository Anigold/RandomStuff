from backend.errors.exceptions import *
from backend.errors.error_bus import ErrorBus, ErrorEvent
import traceback

class RepositoryErrorBoundary:

    @staticmethod
    def run(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)

        except InfraError as err:
            evt = ErrorEvent(
                type=err.__class__.__name__,
                message=str(err),
                context=fn.__name__,
                layer="infra",
                trace=err.trace if hasattr(err, "trace") else traceback.format_exc()
            )
            ErrorBus.emit(evt)

            # Translate to repo-level
            if isinstance(err, FileReadError):
                raise FileLoadError(err.message, cause=err)
            if isinstance(err, FileWriteError):
                raise FileSaveError(err.message, cause=err)
            
            raise RepositoryError(err.message, cause=err)
