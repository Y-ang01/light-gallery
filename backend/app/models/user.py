import uuid
from sqlalchemy import Column, String, Boolean, Enum, DateTime, Text
from sqlalchemy.sql import func
from ..core.db import Base
from ..utils.security_utils import Role


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(100), nullable=False)
    role = Column(Enum(Role), default=Role.USER, nullable=False)
    avatar_url = Column(String(255), default="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png")
    profile = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"