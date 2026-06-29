class DomainError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class DomainValidationError(DomainError):
    pass


# Backward-compatible alias (prefer DomainValidationError in new code).
ValidationError = DomainValidationError
