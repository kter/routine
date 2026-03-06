class DomainError(Exception):
    """Base class for domain errors."""


class NotFoundError(DomainError):
    def __init__(self, resource: str, id: str) -> None:
        super().__init__(f"{resource} with id '{id}' not found")
        self.resource = resource
        self.id = id


class ValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConflictError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class AuthorizationError(DomainError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message)
