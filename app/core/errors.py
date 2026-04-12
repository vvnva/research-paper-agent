class ApplicationError(Exception):
    """Base application exception."""


class ValidationError(ApplicationError):
    """Raised when input is invalid."""


class ExternalServiceError(ApplicationError):
    """Raised for external dependency failures."""


class CircuitOpenError(ApplicationError):
    """Raised when circuit breaker is open."""
