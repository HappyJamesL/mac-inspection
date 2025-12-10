"""认证相关的数据验证模型"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None
    role: Optional[str] = None


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserCreate(UserBase):
    """用户创建模型"""
    password: str


class UserUpdate(UserBase):
    """用户更新模型"""
    password: Optional[str] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True