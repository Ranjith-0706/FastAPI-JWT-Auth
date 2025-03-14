from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends, status
from app.config import settings
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi.security import OAuth2PasswordBearer


ACCESS_TOKEN_SECRET_KEY = settings.ACCESS_TOKEN_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
# REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


# Create access token from the Input dictionary. Now we are encrypting only user_id object
def create_access_token(data: dict):
    to_encode = data.copy()
    # print(to_encode)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=JWT_ALGORITHM
    )
    return encoded_jwt


# Verify the token for every request if it is invalid we will send the error message.
def verify_access_token(token):
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        print(payload)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={
                "status": 0,
                "description": "Session Timed out, Please login again",
            },
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"status": 0, "description": "Invalid access token"},
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
