import traceback
from selenium.common.exceptions import TimeoutException, WebDriverException
from backend.errors.exceptions import (
    InfraError,
    FileReadError, FileWriteError, StoragePermissionError,
    SeleniumError, SeleniumTimeoutError,
)
from backend.errors.error_bus import ErrorBus, ErrorEvent

class InfraBoundary:

    @staticmethod
    def run(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)

        # Filesystem normalization
        except FileNotFoundError as e:
            err = FileReadError(str(e), cause=e)

        except PermissionError as e:
            err = StoragePermissionError(str(e), cause=e)

        except OSError as e:
            err = FileWriteError(str(e), cause=e)

        # Selenium normalization
        except TimeoutException as e:
            err = SeleniumTimeoutError(str(e), cause=e)

        except WebDriverException as e:
            err = SeleniumError(str(e), cause=e)

        # Catch-all normalization
        except Exception as e:
            err = InfraError(f"Unexpected infra error: {e}", cause=e)

        # Emit telemetry
        ErrorBus.emit(ErrorEvent(
            type=err.__class__.__name__,
            message=str(err),
            layer="infra",
            context=fn.__name__,
            trace=traceback.format_exc(),
        ))

        raise err
