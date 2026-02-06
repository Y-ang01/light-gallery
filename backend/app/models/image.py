# backend/app/models/image.py - PostgreSQL 适配版
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from .base import Base


class Image(Base):
    __tablename__ = "images"
    __table_args__ = {
        'extend_existing': True,
        'schema': 'public',
        'comment': '图片表'
    }

    id = Column(String(36), primary_key=True, comment="图片ID")
    name = Column(String(255), nullable=False, comment="图片名称")
    url = Column(String(512), nullable=False, comment="图片URL")
    size = Column(Integer, default=0, comment="图片大小(字节)")
    mime_type = Column(String(50), default="image/jpeg", comment="MIME类型")
    width = Column(Integer, default=0, comment="宽度")
    height = Column(Integer, default=0, comment="高度")
    is_public = Column(Boolean, default=True, comment="是否公开")
    album_id = Column(String(36), ForeignKey("albums.id", ondelete="CASCADE"), nullable=True, comment="相册ID")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    user = relationship(
        "app.models.user.User",
        backref="images",
        lazy="joined"
    )

    album = relationship(
        "app.models.album.Album",
        backref="images",
        lazy="joined"
    )

    def __repr__(self):
        return f"<Image(id={self.id}, name={self.name}, user_id={self.user_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "size": self.size,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "is_public": self.is_public,
            "album_id": self.album_id,
            "user_id": self.user_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }