import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..models.user import User
from ..utils.security_utils import Role

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-safe")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天有效期

# OAuth2令牌获取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 加密密码
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 获取当前用户
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# 角色权限依赖
def get_current_active_user(
        current_user: User = Depends(get_current_user),
        required_role: Role = Role.USER
):
    # 检查用户是否激活
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    # 检查角色权限
    role_order = {
        Role.GUEST: 0,
        Role.USER: 1,
        Role.AUTHOR: 2,
        Role.ADMIN: 3
    }

    if role_order[current_user.role] < role_order[required_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    return current_user


# 管理员权限依赖
def admin_required(current_user: User = Depends(get_current_user)):
    return get_current_active_user(current_user, Role.ADMIN)


# 作者权限依赖
def author_required(current_user: User = Depends(get_current_user)):
    return get_current_active_user(current_user, Role.AUTHOR)