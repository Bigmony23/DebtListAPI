import json
import os
from decimal import Decimal
from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from unicodedata import numeric


class SignUpModel(BaseModel):
    username:str
    name:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]

    class Config:
        from_attributes=True
        json_schema_extra={
            'example': {
                'username': 'admin',
                'name': '<NAME>',
                'email': 'test@mail.com',
                'password': 'password1234',
                'is_staff': True,
                'is_active': True,
            }
        }
class UserCurrencyModel(BaseModel):
    currency:str

class JWTSettings(BaseModel):
    authjwt_secret_key: str = os.getenv("AUTHJWT_SECRET_KEY", "")
    authjwt_token_location: set[str] = set(
        json.loads(os.getenv("AUTHJWT_TOKEN_LOCATION", '["headers"]'))
    )


class TokenData(BaseModel):
    access_token:str
    refresh_token:str

class LoginModel(BaseModel):
    username_or_email:str
    password:str

class LoginResponseModel(BaseModel):
    success:bool
    code:int
    message:str
    data:TokenData

class DebtCreateModel(BaseModel):
    person_full_name:str=Field(min_length=3, max_length=100)
    date_get:date
    date_give:date
    description:str
    summa:Decimal
    currency:str
    debt_type: Literal["owed_by", "owed_to"]
    reminder_at:date

class DebtUpdate(BaseModel):
    person_full_name: Optional[str] = None
    debt_type: Optional[Literal["owed_by", "owed_to"]] = None
    summa: Optional[Decimal] = Field(default=None, gt=0)
    currency: Optional[str] = None
    description: Optional[str] = None
    date_get: Optional[date] = None
    date_give: Optional[date] = None
    reminder_at: Optional[date] = None


class DebtResponse(BaseModel):
    id: int
    person_id: int
    person_full_name: str
    debt_type: str
    summa: Decimal
    currency: str
    description: Optional[str]
    date_get: Optional[date]
    date_give: Optional[date]
    reminder_at: Optional[date]

    model_config = ConfigDict(from_attributes=True)

class UserSettingsUpdate(BaseModel):
    currency: Literal ["UZS","USD","EUR"]

class UserSettingsResponse(BaseModel):
    id: int
    username: str
    currency: str
    model_config = ConfigDict(from_attributes=True)