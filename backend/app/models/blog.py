import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer, ARRAY, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.db import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    cover_image_url = Column(String(255), nullable=True)
    is_draft = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    tags = Column(ARRAY(String), default=[], nullable=True)
    view_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", backref="blog_posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BlogPost(id={self.id}, title={self.title}, user_id={self.user_id})>"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    post_id = Column(String(36), ForeignKey("blog_posts.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    parent_id = Column(String(36), ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    post = relationship("BlogPost", back_populates="comments")
    user = relationship("User", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"