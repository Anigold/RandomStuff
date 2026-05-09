from __future__ import annotations


class WorkBotError(Exception):
    """Base exception for WorkBot."""


class ConfigurationError(WorkBotError):
    """Raised when application configuration is invalid."""


class RepositoryError(WorkBotError):
    """Raised when persistence operations fail."""
