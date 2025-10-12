'''
==================

Core error definitions and the global ErrorBus for WorkBot.

This is the *foundation* of the entire error-handling system.

Goals:
- Provide a single, semantic exception hierarchy (`WorkBotError` base).
- Allow all exceptions to emit structured `ErrorEvent` objects.
- Avoid dependencies on logging or infrastructure.
- Remain stable across all layers: domain, app, infra, bots, CLI.

The ErrorBus enables system-wide observability without coupling.
Other layers (infra, CLI, bots) can subscribe to ErrorBus events
to log, alert, or handle them as needed.
'''

from __future__ import annotations
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Callable, List, Optional


# ============================================================
# Error Event & Bus
# ============================================================

@dataclass
class ErrorEvent:
    '''
    Represents a structured error emission for observers.

    Attributes:
        id (str): Unique identifier for the error instance.
        type (str): Exception class name.
        message (str): Human-readable message.
        context (Optional[str]): Logical context (e.g., function, service).
        severity (str): Level indicator ("ERROR", "WARNING", "CRITICAL", etc.).
        trace (Optional[str]): Formatted stack trace (optional).
    '''
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    message: str = ""
    context: Optional[str] = None
    severity: str = "ERROR"
    trace: Optional[str] = None


class ErrorBus:
    '''
    Global pub/sub mechanism for WorkBot errors.

    - Purely synchronous.
    - Subscribers are callbacks taking a single `ErrorEvent`.
    - Subscribers should handle their own errors gracefully.
    '''
    _subscribers: List[Callable[[ErrorEvent], None]] = []

    @classmethod
    def subscribe(cls, handler: Callable[[ErrorEvent], None]) -> None:
        '''Attach a new subscriber to receive all ErrorEvents.'''
        cls._subscribers.append(handler)

    @classmethod
    def unsubscribe(cls, handler: Callable[[ErrorEvent], None]) -> None:
        '''Detach a subscriber.'''
        if handler in cls._subscribers:
            cls._subscribers.remove(handler)

    @classmethod
    def emit(cls, event: ErrorEvent) -> None:
        '''Broadcast an ErrorEvent to all registered subscribers.'''
        for handler in list(cls._subscribers):
            try:
                handler(event)
            except Exception:
                # Defensive design: one subscriber should never break others
                pass


# ============================================================
# Base Exception
# ============================================================

class WorkBotError(Exception):
    '''
    Root of all domain/application/infra exceptions in WorkBot.

    Each WorkBotError automatically emits an ErrorEvent to the
    global ErrorBus upon initialization — providing decoupled
    observability without coupling to logging or I/O systems.

    Args:
        message (str): Human-readable description.
        context (str, optional): Logical or component context.
        cause (Exception, optional): Original underlying exception.
    '''

    severity = "ERROR"

    def __init__(
        self,
        message: str,
        *,
        context: Optional[str] = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.context = context
        self.cause = cause
        self.trace = traceback.format_exc()

        # Emit a structured event automatically.
        ErrorBus.emit(
            ErrorEvent(
                type=self.__class__.__name__,
                message=message,
                context=context,
                severity=self.severity,
                trace=self.trace,
            )
        )

    def __str__(self):
        ctx = f" [{self.context}]" if self.context else ""
        return f"{self.__class__.__name__}{ctx}: {self.message}"


# ============================================================
# Domain-Level Exceptions
# ============================================================

class ValidationError(WorkBotError):
    '''Raised when a domain object fails validation.'''

class NotFoundError(WorkBotError):
    '''Raised when an expected resource or record is not found.'''

class ConflictError(WorkBotError):
    '''Raised when an operation conflicts with existing data.'''

class OrderError(WorkBotError):
    '''Raised for issues specific to order operations.'''

class VendorError(WorkBotError):
    '''Raised for vendor-related operations or integrations.'''

class StoreError(WorkBotError):
    '''Raised for store-related operations.'''


# ============================================================
# Infrastructure-Level Exceptions
# ============================================================

class FileAccessError(WorkBotError):
    '''Raised when file read/write/delete operations fail.'''

class SerializationError(WorkBotError):
    '''Raised when serialization or deserialization fails.'''

class BlobStoreError(WorkBotError):
    '''Raised for underlying BlobStore (local or cloud) issues.'''


# ============================================================
# External or Automation-Level Exceptions
# ============================================================

class SeleniumError(WorkBotError):
    '''Raised for browser automation failures (CraftableBot, etc.).'''

class NetworkError(WorkBotError):
    '''Raised for networking timeouts, disconnections, etc.'''

class VendorIntegrationError(WorkBotError):
    '''Raised for vendor-specific system or API errors.'''


# ============================================================
# Decorators for Translating Errors
# ============================================================

def translate_errors(context: str | None = None):
    '''
    Decorator that wraps low-level exceptions into WorkBotErrors.

    Use this at layer boundaries (repositories, adapters, services)
    to ensure all exceptions are represented consistently.

    Example:
        @translate_errors("OrderRepository.save")
        def save(self, order): ...
    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except WorkBotError:
                raise
            except FileNotFoundError as e:
                raise FileAccessError(f"File not found: {e}", context=context, cause=e)
            except PermissionError as e:
                raise FileAccessError(f"Permission denied: {e}", context=context, cause=e)
            except TimeoutError as e:
                raise NetworkError(f"Operation timed out: {e}", context=context, cause=e)
            except Exception as e:
                raise WorkBotError(f"Unexpected error: {e}", context=context, cause=e)
        return wrapper
    return decorator
