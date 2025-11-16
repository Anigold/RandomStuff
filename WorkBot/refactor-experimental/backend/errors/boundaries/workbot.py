from backend.errors.exceptions import *
from backend.errors.error_bus import ErrorBus, ErrorEvent
from backend.workbot.work_result import WorkResult
import traceback

class WorkBotErrorBoundary:

    @staticmethod
    def run(fn, *args, **kwargs) -> WorkResult:
        try:
            result = fn(*args, **kwargs)
            return WorkResult.ok("Success", payload=result)

        except DomainError as err:
            ErrorBus.emit(
                ErrorEvent(
                    type=err.__class__.__name__,
                    message=str(err),
                    context=fn.__name__,
                    layer="domain",
                    trace=traceback.format_exc()
                )
            )
            return WorkResult.fail("Domain operation failed", errors=[str(err)])

        except Exception as err:
            # Other errors get converted into WorkBotError
            wb_err = WorkBotError(str(err), cause=err)
            ErrorBus.emit(ErrorEvent(
                type="WorkBotError",
                message=str(err),
                context=fn.__name__,
                layer="workbot",
                trace=traceback.format_exc()
            ))
            return WorkResult.fail("Unexpected WorkBot error", errors=[str(wb_err)])
