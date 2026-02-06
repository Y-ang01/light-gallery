# backend/app/models/user.py - PostgreSQL 适配版
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Boolean
import enum

from sqlalchemy.orm import relationship

from .base import Base


# 角色枚举
class UserRole(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    AUTHOR = "AUTHOR"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {
        'extend_existing': True,
        # PostgreSQL 编码配置
        'schema': 'public',
        'comment': '用户表'
    }

    # PostgreSQL 使用 String 替代 VARCHAR，长度通过参数指定
    id = Column(String(36), primary_key=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    avatar_url = Column(String(255), default="", comment="头像URL")
    role = Column(Enum(UserRole), default=UserRole.USER, comment="用户角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    albums = relationship("Album", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }