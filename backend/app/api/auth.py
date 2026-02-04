# 文件路径: backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from ..core.database import get_db
from ..core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, REMEMBER_ME_EXPIRE_DAYS
from ..services.user_service import UserService
from ..schemas.user import UserCreate, UserLogin, Token, UserResponse
from ..core.dependencies import get_current_active_user
from ..models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        user = UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
        response: Response,
        user_data: UserLogin,
        db: Session = Depends(get_db)
):
    """用户登录"""
    user = UserService.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 设置Token过期时间
    if user_data.remember_me:
        access_token_expires = timedelta(days=REMEMBER_ME_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds()
    }


@router.post("/logout")
async def logout(response: Response):
    """用户登出"""
    response.delete_cookie("access_token")
    return {"message": "成功登出"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
        current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
        user_update: dict,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    # 过滤允许更新的字段
    allowed_fields = ["username", "avatar_url", "profile"]
    update_data = {k: v for k, v in user_update.items() if k in allowed_fields and v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有有效的更新数据"
        )

    user = UserService.update_user_profile(db, current_user.id, **update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return user


@router.post("/refresh")
async def refresh_token(
        current_user: User = Depends(get_current_active_user)
):
    """刷新访问令牌"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds()
    }