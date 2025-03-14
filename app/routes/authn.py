from fastapi import APIRouter, HTTPException, status, Request, UploadFile, Query
from app.utils import (
    verify_password,
    hash_password,
    create_folder,
    gen_millisec,
    check_existence,
    filter_fields,
    validate_uploaded_files,
    validate_length,
    validate_email_format
)
from app.userSerializers import userEntity
from app.middleware.jwt_utils import create_access_token
from app.models.register_m import LoginUserSchema, CreateUserNewSchema,Email,TechicianUserSchema,MainCompanySchema
from typing import List, Optional
import app.database as DB
from random import randbytes
import hashlib
from .. import utils
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from fastapi import APIRouter, Request, Response

from app.models.response_m import (
    validate_password_length,
    validate_mobile_length,
    ResponseModel,PagenationDataModel
)
from app.config import settings


router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(payload: CreateUserNewSchema, request: Request):
    # Check if user already exists
    user_created = False
    try:
        validate_password_length(payload.password)
        validate_mobile_length(payload.mob_no)
        # user = DB.Users.find_one({"email": payload.email.lower()})
        user = CustomDB.find_one(DB.Users, {"email": payload.email.lower(),"delete":0})
        if user:
            if not user.get("verified", False) and user.get("register_verified", True):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists but hasn't been verified. Please check your email to complete the verification process.",
                )
            elif not user.get("register_verified", False):
                user_id = user.get("user_id")
                payload.password = hash_password(payload.password)
                payload.verified = False
                payload.email = payload.email.lower()
                payload.created_at = gen_millisec()

                # # Generate verification code
                # token = randbytes(10)
                # hashed_code = hashlib.sha256(token).hexdigest()
                DB.Users.find_one_and_update(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "password": payload.password,
                            "register_verified": True,
                            # "verification_code": hashed_code,
                            "verified":True,
                            "updated_at": gen_millisec(),
                        }
                    },
                )
                # url = f"http://localhost:8000/api/authn/verifyemail?token={token.hex()}"
                # url = f"https://stg-pm.mts-om.com/api/authn/verifyemail?token={token.hex()}"

                # # Prepare user data for email
                # user_data = {
                #     "user_name": payload.name,
                #     "email": payload.email,
                #     "verify_link": url,
                #     "mob": payload.mob_no,
                # }

                # # Send verification email
                # await send_email(
                #     subject="Welcome To Maein360",
                #     type="new_register",
                #     data=user_data,
                #     cc=None,
                # )

                return {
                    "status": 1,
                    "message": "Registration Completed Please Login to Continue",
                }

            # elif not user.get("verified", False):
            #     raise HTTPException(
            #         status_code=status.HTTP_409_CONFLICT,
            #         detail="An account with this email already exists but hasn't been verified. Please check your email to complete the verification process.",
            #     )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Account already exists with this Email",
                )
        user = DB.Users.find_one({"mob_no": payload.mob_no,"delete":0})
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account already exists with this Mobile Number",
            )

        # Prepare user data
        payload.name = validate_length(payload.name,min_char=1,max_char=64,key="Name")
        payload.password = hash_password(payload.password)
        payload.verified = False
        payload.email = validate_email_format(payload.email).lower()
        payload.created_at = gen_millisec()
        payload.user_id = utils.gen_uuid()
        payload.verify_sent_count =1

        # Insert new user
        result = DB.Users.insert_one(payload.dict())
        user_created = True

        # Generate verification code
        token = randbytes(10)
        hashed_code = hashlib.sha256(token).hexdigest()
        DB.Users.find_one_and_update(
            {"_id": result.inserted_id},
            {"$set": {"verification_code": hashed_code, "updated_at": gen_millisec()}},
        )

        # Generate verification URL
        url = f"{settings.BACKEND_URL}/api/authn/verifyemail?token={token.hex()}"
        # url = f"http://localhost:8000/api/authn/verifyemail?token={token.hex()}"

        # Prepare user data for email
        user_data = {
            "user_name": payload.name,
            "email": payload.email,
            "verify_link": url,
            "mob": payload.mob_no,
        }
        # Send welcome email
        # await send_email(
        #     subject="Welcome To Maein360",
        #     type="new_register",
        #     data=dict(user_data),
        #     cc=None,
        # )

        return {
            "status": 1,
            "message": "Verification token successfully sent to your email",
        }

    except HTTPException as http_error:

        if user_created:
            DB.Users.find_one_and_delete({"_id": result.inserted_id})
        raise http_error
    except Exception as error:
        error_message = str(error)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_message
        )




@router.post("/login")
@router.post("/api/user/login")
async def login(payload: LoginUserSchema):
    try:
        # Determine if identifier is an email or phone number
        query = {"email": payload.identifier.lower()} if "@" in payload.identifier else {"mob_no": payload.identifier}

        user =  DB.Users.find_one({**query, "delete": 1})
        if user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The account you are trying to login no longer exists.",
            )

        # Check if user exists and is active
        db_user = DB.Users.find_one({**query, "delete": 0})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect Email/Mobile Number or Password",
            )
        
        
        # Define a mapping of reg_type to error messages
        reg_type_messages = {
            1: "Please sign in using your Gmail",
            2: "Please sign in using your Facebook account",
            3: "Please sign in using your Instagram account",
        }

        if db_user:
            reg_type = db_user.get("reg_type")
            if reg_type in reg_type_messages:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=reg_type_messages[reg_type],
                )


        # Convert user to dictionary format
        user = userEntity(db_user)

        # Validate password
        if not verify_password(payload.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect Email/Mobile Number or Password",
            )
         # Check if the user has verified their email
        if not user["verified"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please verify your email ",
            )

        # Generate access token
        access_token = create_access_token(
            data={"user_id": user["user_id"], "email": user["email"]}
        )

        # Log successful login
        await user_log(
            UserLogEntryModel(
                user_id=user["user_id"], type=0, title="Log in", desc="Welcome to Maein360"
            )
        )

        return {
            "status": "Successfully Logged in",
            "name": user["name"],
            "email": user["email"],
            "access_token": access_token,
            "got_email_mob": user["got_email_mob"],
            "role": user["role"],
        }

    except HTTPException as http_err:
        raise http_err  # Return known HTTP errors directly

    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to login",
        )