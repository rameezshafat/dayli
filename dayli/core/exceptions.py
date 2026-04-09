class DayliError(Exception):
    """Base exception for domain and orchestration failures."""


class ValidationError(DayliError):
    """Raised when a schedule request violates constraints."""

