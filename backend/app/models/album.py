import uuid
from sqlalchemy import Column, String, Text, Enum, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.db import Base
from ..utils.security_utils import AlbumPermission


class Album(Base):
    __tablename__ = "albums"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    permission = Column(Enum(AlbumPermission), default=AlbumPermission.PUBLIC, nullable=False)
    password_hash = Column(String(100), nullable=True)
    cover_image_id = Column(String(36), ForeignKey("images.id"), nullable=True)
    image_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", backref="albums")
    cover_image = relationship("Image", foreign_keys=[cover_image_id])
    images = relationship("Image", back_populates="album", foreign_keys="Image.album_id")

    def __repr__(self):
        return f"<Album(id={self.id}, name={self.name}, user_id={self.user_id})>"