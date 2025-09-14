class UserAlreadyExistsError(Exception):
    pass


class InvalidVerificationTokenError(Exception):
    pass


class InvalidOldPasswordError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserNotVerifiedError(Exception):
    pass
