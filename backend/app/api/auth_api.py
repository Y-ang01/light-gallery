from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..core.dependencies import (
    get_current_user, create_access_token, verify_password
)
from ..services.user_service import (
    create_user, get_user_by_id, get_user_by_credentials,
    update_user_profile, update_user_avatar
)
from ..utils.file_utils import (
    ensure_dir, generate_unique_filename, validate_file_size
)
from ..utils.format_utils import model_to_dict
import os

router = APIRouter()


# 用户注册
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        username: str,
        email: str,
        password: str,
        db: Session = Depends(get_db)
):
    user = create_user(db, username, email, password)

    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.id}
    )

    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": model_to_dict(user, exclude=["hashed_password"])
        }
    }


# 用户登录
@router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = get_user_by_credentials(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.id}
    )

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": model_to_dict(user, exclude=["hashed_password"])
        }
    }


# 获取个人信息
@router.get("/profile")
async def get_profile(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user = get_user_by_id(db, current_user.id)

    return {
        "code": 200,
        "message": "获取个人信息成功",
        "data": model_to_dict(user, exclude=["hashed_password"])
    }


# 更新个人信息
@router.put("/profile")
async def update_profile(
        username: str = None,
        profile: str = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user = update_user_profile(db, current_user.id, username, profile)

    return {
        "code": 200,
        "message": "更新个人信息成功",
        "data": model_to_dict(user, exclude=["hashed_password"])
    }


# 上传头像
@router.post("/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证文件大小（5MB）
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件大小不能超过5MB"
        )

    # 确保目录存在
    avatar_dir = f"static/avatars/{current_user.id}"
    ensure_dir(avatar_dir)

    # 保存文件
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(avatar_dir, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 更新用户头像
    avatar_url = f"/{file_path}"
    user = update_user_avatar(db, current_user.id, avatar_url)

    return {
        "code": 200,
        "message": "上传头像成功",
        "data": {
            "avatar_url": avatar_url,
            "user": model_to_dict(user, exclude=["hashed_password"])
        }
    }