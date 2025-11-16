# backend/infra/errors.py

from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Optional, Callable, TypeVar, Type, Any


# ==========================================
# Base Infra Error
# ==========================================

class InfraError(Exception):
    '''
    Base class for all infrastructure-level exceptions.
    Anything that talks to the OS, browser, network, etc.,
    should raise subclasses of this, not raw exceptions.
    '''

    def __init__(self, message: str, *, cause: Exception | None = None):
        super().__init__(message)
        self.message = message
        self.cause   = cause
        self.trace   = traceback.format_exc() # Captured at the point we wrap the error

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


# ==========================================
# Filesystem / Storage Errors
# ==========================================

class FileSystemError(InfraError):
    """Generic filesystem error."""


class FileReadError(FileSystemError):
    """Failure when reading a file or directory."""


class FileWriteError(FileSystemError):
    """Failure when writing/creating a file."""


class FileDeleteError(FileSystemError):
    """Failure when deleting a file."""


class FileNotFoundInfraError(FileSystemError):
    """Wrapper around missing paths at the infra level."""


class StoragePermissionError(FileSystemError):
    """Permission denied when touching the filesystem."""


# ==========================================
# Browser / Selenium / Automation Errors
# ==========================================

class AutomationError(InfraError):
    """Generic automation/bot error."""


class SeleniumError(AutomationError):
    """Base for Selenium-related issues."""


class SeleniumTimeoutError(SeleniumError):
    """Selenium waited too long for a condition."""


class BrowserDownloadError(SeleniumError):
    """Something went wrong with a browser download."""


# ==========================================
# Network-ish Errors (if needed later)
# ==========================================

class NetworkInfraError(InfraError):
    """Generic network/HTTP/socket error."""



T = TypeVar("T")


def translate_infra_errors(
    *,
    context: str | None = None,
    default_exc: Type[InfraError] = InfraError,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for infra/adapters (BlobStore, DownloadManager, CraftableBot helpers).

    - Converts built-in OS / Selenium / Timeout errors into InfraError subclasses.
    - Keeps higher layers from ever seeing raw OSError, FileNotFoundError, etc.

    Usage:

        @translate_infra_errors(context="LocalBlobStore.list_paths")
        def list_paths(...): ...

    Higher layers (repos/services) will then catch InfraError and translate
    into their own error types.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)

            # Already an InfraError? Let it bubble up unchanged.
            except InfraError:
                raise

            # Common FS errors
            except FileNotFoundError as e:
                msg = f"{context or func.__name__}: file or directory not found: {e}"
                raise FileNotFoundInfraError(msg, cause=e)
            except PermissionError as e:
                msg = f"{context or func.__name__}: permission denied: {e}"
                raise StoragePermissionError(msg, cause=e)

            # Generic OS error
            except OSError as e:
                msg = f"{context or func.__name__}: filesystem error: {e}"
                raise FileSystemError(msg, cause=e)

            # Timeouts (can also be Selenium, network, etc.)
            except TimeoutError as e:
                msg = f"{context or func.__name__}: operation timed out: {e}"
                raise SeleniumTimeoutError(msg, cause=e)

            # Fallback for anything else
            except Exception as e:
                msg = f"{context or func.__name__}: unexpected infra error: {e}"
                raise default_exc(msg, cause=e)

        return wrapper

    return decorator
