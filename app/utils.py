from passlib.context import CryptContext
from fastapi import HTTPException, UploadFile
from typing import List, Dict, Set,Any
from datetime import datetime,timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import uuid
import re
import os
import random
import string
import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def generate_password(length: int = 8) -> str:
    """Generate a random 8-character alphanumeric password."""
    characters = (
        string.ascii_letters + string.digits
    )  # includes both letters and digits
    password = "".join(random.choice(characters) for _ in range(length))
    return password


def is_valid_email(email: str) -> bool:
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def generate_otp():
    return random.randint(100000, 999999)  # Generates a random 6-digit number


def gen_uuid():
    return uuid.uuid4().hex


def gen_millisec():
    return int(datetime.now().timestamp() * 1000)


def create_folder(base_path, property_id, folder, sub_id, subfolder_name,additional_folder_name):
    """
    Creates a folder structure dynamically based on property_id and returns the subfolder path.

    Args:
        base_path (str): The base directory path.
        property_id (str): Unique identifier for the property.
        folder (str): Intermediate folder name.
        sub_id (str): Identifier for the subfolder.
        subfolder_name (str): Name of the specific subfolder to create.

    Returns:
        str: Full path to the created subfolder, or None if an error occurs.
    """
    # Create the main folder for the property_id if it doesn't exist
    property_folder = os.path.join(base_path, property_id, folder, sub_id)

    try:
        # Ensure the property folder exists
        os.makedirs(property_folder, exist_ok=True)

        # Create subfolder inside the property folder
        subfolder_path = os.path.join(property_folder, subfolder_name,additional_folder_name)
        os.makedirs(subfolder_path, exist_ok=True)

        return subfolder_path  # Returning the full path to the subfolder
    except OSError as error:
        return None

def validate_uploaded_files(
    files: List[UploadFile],
    individual_limit: int,
    total_limit: int,
    allowed_extensions: List[str],
):

    # Check if the number of files exceeds the limit
    if len(files) > 5:
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="Only a maximum of 5 files are allowed to be uploaded at a time.",
        )

    valid_files = []
    total_size = 0

    for file in files:
        content = file.file.read()
        size = len(content)
        total_size += size

        # Validate file extension
        file_extension = os.path.splitext(file.filename)[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=415,  # Unsupported Media Type
                detail=f"File {file.filename} has an invalid file type. Allowed types: {', '.join(allowed_extensions)}",
            )

        if size > individual_limit:
            raise HTTPException(
                status_code=413,  # Payload Too Large
                detail=f"File {file.filename} exceeds individual size limit of {individual_limit / 1024 / 1024} MB",
            )
        if total_size > total_limit:
            raise HTTPException(
                status_code=413,  # Payload Too Large
                detail=f"Total uploaded size exceeds limit of {total_limit / 1024 / 1024:.2f} MB",
            )

        valid_files.append(
            {"file_name": file.filename, "size": size, "content": content}
        )
    return valid_files

def check_existence(entity, entity_id, entity_name):
    # Check if the entity exists and the delete field is set to 0
    if not entity or entity.get("delete") != 0 or entity.get("archive") == 1:
        raise HTTPException(
            status_code=404,
            detail=f"{entity_name} no longer exists",
        )
    
# Function to validate if user exists in the specified list
def validate_user_in_list(property_data, user_id, role, active_status):
    users = property_data.get(role, [])
    for user in users:
        if user.get("user_id") == user_id and user.get("active") == active_status:
            return True
    return False    

def validate_user_in_any_list(property_data, user_id, roles, active_status):
    for role in roles:
        if validate_user_in_list(property_data, user_id, role, active_status):
            return True
    return False

def filter_fields(items: List[Dict], exclude_keys: Set[str]) -> List[Dict]:
    """
    Removes specified keys from a list of dictionaries.

    :param items: List of dictionaries to filter.
    :param exclude_keys: Set of keys to exclude from the dictionaries.
    :return: Filtered list of dictionaries.
    """
    return [{k: v for k, v in item.items() if k not in exclude_keys} for item in items]

def date_to_milliseconds(date_string: str, date_format: str = "%Y-%m-%d") -> int:
    """
    Convert a date string to milliseconds since the epoch.

    :param date_string: The date string to convert (e.g., "2024-12-06").
    :param date_format: The format of the date string (default is "%Y-%m-%d").
    :return: The date in milliseconds since the epoch.
    """
    try:
        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date_string, date_format)
        # Convert the datetime object to milliseconds since epoch
        return int(date_obj.timestamp() * 1000)
    except ValueError as e:
        raise ValueError(f"Invalid date or format: {e}")


# Secret key for signing the JWT
secret_key = settings.ACCESS_TOKEN_SECRET_KEY
# Function to encode data with JWT
def encode_data_jwt(data: dict, expiration_minutes: int = 2880) -> str:
    payload = {
        **data,
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes)  # Add expiration
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")  # Encode JWT with HS256
    return token.decode('utf-8')  # Decode bytes to string


def normalize_text(text: str) -> str:
    return text.replace(" ", "").lower()


EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$"
def validate_length(value: str, min_char: int, max_char: int,key:str):
    """Validates that the input meets the specified character length constraints."""
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="Invalid data type, expected string")
    if len(value) < min_char:
        raise HTTPException(status_code=400, detail=f"{key} must be at least {min_char} characters long")
    if len(value) > max_char:
        raise HTTPException(status_code=400, detail=f"{key} exceeds {max_char} characters")
    return value
def validate_email_format(value: str):
        """Validates that the input follows 'text@text.text' email format."""
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail="Invalid data type, expected string")
        
        if not re.match(EMAIL_REGEX, value):
            raise HTTPException(status_code=400, detail="Invalid email format. Expected 'text@text.text'")
        
        return value