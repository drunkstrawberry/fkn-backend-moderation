from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routers.predict import router as predict_router
from schemas import ValidationErrorResponse, ValidationIssue

app = FastAPI(title="Модерация объявлений")
app.include_router(predict_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    response = ValidationErrorResponse(
        detail=[
            ValidationIssue(loc=error["loc"], msg=error["msg"], type=error["type"])
            for error in exc.errors()
        ]
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=response.model_dump(mode="json")
    )
