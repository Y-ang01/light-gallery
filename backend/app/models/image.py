import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    thumbnail_path = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    album_id = Column(String(36), ForeignKey("albums.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    exif_data = Column(JSON, nullable=True)
    sort_order = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    album = relationship("Album", back_populates="images", foreign_keys=[album_id])
    user = relationship("User", backref="images")

    def __repr__(self):
        return f"<Image(id={self.id}, filename={self.filename}, album_id={self.album_id})>"