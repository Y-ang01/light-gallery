# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default='USER')
    avatar_url = Column(String(500))
    profile = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
