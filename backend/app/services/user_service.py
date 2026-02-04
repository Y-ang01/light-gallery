# python
# 文件路径: `backend/app/services/user_service.py`
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password
from typing import Optional
import uuid


class UserService:
    """用户服务类"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        if UserService.get_user_by_email(db, user_data.email):
            raise ValueError("邮箱已被注册")

        # 检查用户名是否已存在
        if UserService.get_user_by_username(db, user_data.username):
            raise ValueError("用户名已被使用")

        # 创建用户对象
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """用户认证"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def update_user_profile(db: Session, user_id: uuid.UUID, **kwargs) -> Optional[User]:
        """更新用户资料"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_users_count(db: Session) -> int:
        """获取用户总数"""
        return db.query(User).count()
