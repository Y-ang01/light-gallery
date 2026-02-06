# backend/app/models/album.py - PostgreSQL 适配版
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Album(Base):
    __tablename__ = "albums"
    __table_args__ = {
        'extend_existing': True,
        'schema': 'public',
        'comment': '相册表'
    }

    id = Column(String(36), primary_key=True, comment="相册ID")
    name = Column(String(100), nullable=False, comment="相册名称")
    description = Column(Text, default="", comment="相册描述")
    cover_url = Column(String(255), default="", comment="封面图片URL")
    is_public = Column(Boolean, default=True, comment="是否公开")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系 - 使用完整模块路径
    user = relationship("User", back_populates="albums")

    def __repr__(self):
        return f"<Album(id={self.id}, name={self.name}, user_id={self.user_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cover_url": self.cover_url,
            "is_public": self.is_public,
            "user_id": self.user_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "user": self.user.to_dict() if self.user else None
        }