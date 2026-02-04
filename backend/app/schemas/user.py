# 文件路径: backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr
    username: str
    role: str = "USER"


class UserCreate(UserBase):
    """用户创建模型"""
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含数字')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含字母')
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 2 or len(v) > 20:
            raise ValueError('用户名长度必须在2-20个字符之间')
        return v


class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(UserBase):
    """用户响应模型"""
    id: uuid.UUID
    avatar_url: Optional[str] = None
    profile: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[str] = None