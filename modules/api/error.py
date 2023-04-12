from fastapi.exceptions import HTTPException

class ApiException(HTTPException):
    def __init__(
        self,
        code,
        message,
        status_code: int = 200,
    ) -> None:
        self.code = code
        self.message = message
        super().__init__(status_code=status_code)
