from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, HTTPException, status
from app.middleware.jwt_utils import verify_access_token
import app.database as DB
from typing import Callable
from fastapi.responses import JSONResponse
import re
import asyncio
import time
EXCLUDED_ROUTES = [
    "/api/authn/login",
]


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


class AccessCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            if request.url.path in EXCLUDED_ROUTES or re.match(
            r"^/api/(authn|auth|issue)/(verifyemail|forgotpassword|verifyotp|resetpassword|confirm_deletion|confirm_close)/?.*$",
                request.url.path,
            ):
                return await call_next(request)

            if "Authorization" in request.headers:
                jwt_token = request.headers["Authorization"].replace("Bearer ", "")
                payload = verify_access_token(jwt_token)
                request.state.user_info = {"user_id": payload.get("user_id")}
            else:
                raise HTTPException(
                    status_code=401,
                    detail={"status": 0, "description": "Invalid access token"},
                )

            return await call_next(request)

        except HTTPException as exc:
            return JSONResponse(
                content={"detail": exc.detail}, status_code=exc.status_code
            )
        except Exception as exc:
            error_logger.exception(f"Access Error: {str(exc)}")
            return JSONResponse(
                content={"details": f"Internal Server Error: {str(exc)}"},
                status_code=500,
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            if request.url.path not in EXCLUDED_ROUTES:
                if "Authorization" in request.headers:
                    jwt_token = request.headers["Authorization"].replace("Bearer ", "")
                    try:
                        payload = verify_access_token(jwt_token)
                    except HTTPException as exc:
                        raise HTTPException(
                            status_code=401,
                            detail={
                                "status": 0,
                                "description": "Invalid or expired token",
                            },
                        ) from exc
                    except Exception as exc:
                        error_logger.exception(f"Token verification failed: {exc}")
                        raise HTTPException(
                            status_code=500,
                            detail="Internal Server Error during token verification",
                        ) from exc

                    if not payload or "user_id" not in payload:
                        raise HTTPException(
                            status_code=401,
                            detail={
                                "status": 0,
                                "description": "Invalid token payload",
                            },
                        )
                    request.state.user_info = {"user_id": payload["user_id"]}
                else:
                    raise HTTPException(
                        status_code=401,
                        detail={
                            "status": 0,
                            "description": "Authorization header missing",
                        },
                    )

            response = await call_next(request)

            return response

        except HTTPException as exc:
            return JSONResponse(
                content={"detail": exc.detail}, status_code=exc.status_code
            )
        except Exception as exc:
            error_logger.exception(f"Unexpected error: {exc}")
            return JSONResponse(
                content={"detail": "Internal Server Error"}, status_code=500
            )

