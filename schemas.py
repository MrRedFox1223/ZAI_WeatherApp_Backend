from pydantic import BaseModel
from datetime import date


class WeatherRecordBase(BaseModel):
    city_name: str
    date: date
    temperature: float


class WeatherRecordUpdate(BaseModel):
    id: int
    city_name: str
    date: date
    temperature: float


class WeatherRecordResponse(WeatherRecordBase):
    id: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    id: int
    username: str
    role: str
    token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    message: str

