# 建议将以下模型移动到 models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi import UploadFile, File

# 注册请求模型
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    passwordConfirm: str
    name: Optional[str] = None

# 注册响应模型
class UserRegisterResponse(BaseModel):
    collectionId: str
    collectionName: str
    id: str
    email: str | None = None
    emailVisibility: bool
    verified: bool
    name: Optional[str]
    avatar: Optional[str]
    created: str
    updated: str

# 验证邮箱请求模型
class RequestVerificationBody(BaseModel):
    email: EmailStr

# 登录请求模型
class UserLoginRequest(BaseModel):
    identity: EmailStr
    password: str

# 登录响应模型
class UserRecord(BaseModel):
    collectionId: str
    collectionName: str
    id: str
    email: EmailStr
    emailVisibility: bool
    verified: bool
    name: Optional[str]
    avatar: Optional[str]
    created: str
    updated: str

class UserLoginResponse(BaseModel):
    token: str
    record: UserRecord

# 用户更新请求模型
class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    oldPassword: Optional[str] = None
    password: Optional[str] = None
    passwordConfirm: Optional[str] = None
    name: Optional[str] = None