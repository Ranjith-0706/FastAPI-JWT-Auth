from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any

# from app.custom_middleware.global_exception import (
#     validation_exception_handler,
#     RequestValidationError,
# )
from fastapi.exceptions import RequestValidationError


class ResponseModel(BaseModel):
    status: int
    data: List[Dict[str, Any]]  # Ensure data is a list of dictionaries
    message: str

class SingleResponseModel(BaseModel):
    status: int
    data: List[Dict[str, Any]]  # Ensure data is a list of dictionaries

class ConfirmMail(BaseModel):
    status: int
    message: str


class DataExisitRespModel(BaseModel):
    status: int
    message: str
    data: Optional[Dict] = None


class PagenationDataModel(ResponseModel):
    total: int
    start: Optional[int]
    end: Optional[int]


class CustomExceptionHandler:
    @staticmethod
    def raise_200(data: List[Dict], message: str):
        raise HTTPException(
            status_code=200,
            detail=PagenationDataModel(
                status=1, data=data, total=0, start=0, end=0, message=message
            ).dict(),
        )

    @staticmethod
    def raise_201(data: List[Dict[str, Any]], message: str):
        raise HTTPException(
            status_code=201,
            detail=ResponseModel(status=1, data=data, message=message).dict(),
        )

    @staticmethod
    def raise_422(message: str, missing_fields: Dict):
        raise HTTPException(
            status_code=422,
            detail=DataExisitRespModel(
                status=1, message=message, data=missing_fields
            ).dict(),
        )

    @staticmethod
    def raise_400(message: str):
        raise HTTPException(
            status_code=400,
            detail=DataExisitRespModel(status=1, message=message).dict(),
        )

    @staticmethod
    def raise_409(message: str, data: Optional[Dict] = None):
        raise HTTPException(
            status_code=409,
            detail=DataExisitRespModel(status=1, message=message, data=data).dict(),
        )

    @staticmethod
    def raise_404(message: str):
        raise HTTPException(
            status_code=409,
            detail=DataExisitRespModel(status=1, message=message).dict(),
        )

    @staticmethod
    def raise_401(message: str):
        raise HTTPException(
            status_code=401,
            detail=DataExisitRespModel(status=1, message=message).dict(),
        )


# Define a validation exception handler
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    missing_fields = [
        error["loc"][-1] for error in errors if error["type"] == "value_error.missing"
    ]
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "missing_fields": missing_fields,
            "message": "Field is Missing.",
        },
    )


app = FastAPI()


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    missing_fields = [
        error["loc"][-1] for error in errors if error["type"] == "value_error.missing"
    ]
    # error(f"Missing Fields: {missing_fields}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Input Validation Error",
            "missing_fields": missing_fields,
            "message": "Unable to process the entity.",
        },
    )


# Add the validation exception handler to the FastAPI application
app.add_exception_handler(RequestValidationError, validation_exception_handler)


def validate_password_length(password: str):
    """Validate that the password meets the minimum length requirement (8 characters)."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )


def validate_mobile_length(mob_no: int|str):
    """Validate that the Mobile Number  meets the minimum length requirement (15 characters)."""
    if len(mob_no) > 15 or len(mob_no)<7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile Number must be at least 7 to 15 characters long",
        )
