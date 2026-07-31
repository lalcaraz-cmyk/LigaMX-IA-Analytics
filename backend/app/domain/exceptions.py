class DomainError(Exception):
    """Base exception for domain-layer errors."""

    def __init__(self, message: str = "Domain error") -> None:
        super().__init__(message)


class EntityValidationError(DomainError):
    """Raised when an entity fails validation."""

    def __init__(self, message: str = "Entity validation failed") -> None:
        super().__init__(message)


class EntityNotFoundError(DomainError):
    """Raised when an expected entity cannot be found."""

    def __init__(self, message: str = "Entity not found") -> None:
        super().__init__(message)


class BusinessRuleViolation(DomainError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str = "Business rule violation") -> None:
        super().__init__(message)
