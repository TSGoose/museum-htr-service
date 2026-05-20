from fastapi import HTTPException, status


class AppError(Exception):
    code = "APP_ERROR"
    message = "Application error"

    def __init__(self, message: str | None = None, details: dict | None = None) -> None:
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


def http_error(status_code: int, code: str, message: str, details: dict | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


def not_found(code: str, message: str) -> HTTPException:
    return http_error(status.HTTP_404_NOT_FOUND, code, message)


def bad_request(code: str, message: str, details: dict | None = None) -> HTTPException:
    return http_error(status.HTTP_400_BAD_REQUEST, code, message, details)
