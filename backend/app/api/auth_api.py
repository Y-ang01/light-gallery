# backend/app/api/auth_api.py - 完整注册接口
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
import re
import uuid
from datetime import datetime

from ..core.db import get_db
from ..core.dependencies import (
    get_password_hash, verify_password, create_access_token, get_current_user
)
from ..models.user import User, UserRole

router = APIRouter()


# 注册请求模型
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    # 数据验证
    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用户名长度必须在3-20字符之间')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


# 登录请求模型
class LoginRequest(BaseModel):
    username: str
    password: str


# 注册接口 - 确保路由路径正确
@router.post("/register", summary="用户注册")
async def register_user(
        req: RegisterRequest,
        db: Session = Depends(get_db)
):
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == req.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == req.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被注册")

        # 创建新用户
        new_user = User(
            id=str(uuid.uuid4()),
            username=req.username,
            email=req.email,
            hashed_password=get_password_hash(req.password),
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 保存到数据库
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "code": 200,
            "message": "注册成功",
            "data": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"注册失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


# 登录接口
@router.post("/login", summary="用户登录")
async def login_user(
        req: LoginRequest,
        db: Session = Depends(get_db)
):
    try:
        # 根据用户名查询用户
        user = db.query(User).filter(User.username == req.username).first()

        # 检查用户是否存在
        if not user:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 检查用户是否激活
        if not user.is_active:
            raise HTTPException(status_code=401, detail="账号已被禁用")

        # 验证密码
        if not verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        # 创建token
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username}
        )

        return {
            "code": 200,
            "message": "登录成功",
            "data": {
                "token": access_token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "avatar_url": user.avatar_url or ""
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录失败: {str(e)}")
        raise HTTPException(status_code=500, detail="登录失败")


# 获取用户信息
@router.get("/info", summary="获取用户信息")
async def get_user_info(
        current_user: User = Depends(get_current_user)
):
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url or "",
            "role": current_user.role.value,
            "created_at": current_user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }


# 登出接口
@router.post("/logout", summary="用户登出")
async def logout_user():
    return {
        "code": 200,
        "message": "登出成功"
    }