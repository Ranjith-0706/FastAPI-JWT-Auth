from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Union
from app.utils import gen_uuid, gen_millisec


class Register(BaseModel):
    user_id: str = Field(default_factory=gen_uuid)
    name: Optional[str]
    email: str
    # created_by: Optional[str] = ""  # user id
    # created_by: Optional[str] = ""  # user id

    created_at: int = Field(default_factory=gen_millisec)
    modified_by: Optional[str] = ""  # modified user id
    updated_at: int = Field(default_factory=gen_millisec)
    delete: Optional[int] = 0
    archive: Optional[int] = 0


class CreateUserNewSchema(Register):
    name: Optional[str]
    password: str
    mob_no: str
    email: str
    cntry_code: str
    verified: bool = False
    updated_at: Optional[int] = Field(default_factory=gen_millisec)
    register_verified = True
    reg_type = 0
    got_email_mob : Optional[int] = 0
    verify_sent_count :Optional[int] = 0
    role:Optional[int] = 0

class SocialAuthCreateNewUserSchema(Register):
    name: Optional[str]
    password: Optional[str]
    mob_no: str
    email: str
    media_id: str
    cntry_code: Optional[str]
    verified: bool = True
    updated_at: Optional[int] = Field(default_factory=gen_millisec)
    register_verified = True
    reg_type: int  # 0 = app_register, 1 = google_register, 2 = fb_register
    got_email_mob : Optional[int] = 0
    verify_sent_count :Optional[int] = 0
    role:Optional[int] = 0
    

class LoginUserSchema(BaseModel):
    identifier: Union[EmailStr, str]
    password: str


class UserDocs(BaseModel):
    user_id: Optional[str]
    docs: Optional[List]

class Email(BaseModel):
    email: str



class TechicianUserSchema(BaseModel):
    user_id: Optional[str]
    name: Optional[str]
    # addrs: address
    mob_no: str
    email: Optional[str]
    password: Optional[str]
    skills: List
    language: List
    # availability: Availabi
    created_at: int = Field(default_factory=gen_millisec)
    modified_by: Optional[str] = ""  # modified user id
    cntry_code: str
    verified: bool = True
    updated_at: Optional[int] = Field(default_factory=gen_millisec)
    register_verified = True
    reg_type = 0
    got_email_mob : Optional[int] = 0
    verify_sent_count :Optional[int] = 0
    delete: Optional[int] = 0
    archive: Optional[int] = 0  
    role:Optional[int] = 1  



class MainCompanySchema(BaseModel):
    user_id: Optional[str]
    name: Optional[str]
    mob_no: str
    email: Optional[str]
    password: Optional[str]
    reg_no:Optional[str]
    created_at: int = Field(default_factory=gen_millisec)
    modified_by: Optional[str] = ""  # modified user id
    cntry_code: str
    verified: bool = True
    updated_at: Optional[int] = Field(default_factory=gen_millisec)
    register_verified = True
    reg_type = 0
    got_email_mob : Optional[int] = 1
    verify_sent_count :Optional[int] = 0
    delete: Optional[int] = 0
    archive: Optional[int] = 0  
    role:Optional[int] = 2  
