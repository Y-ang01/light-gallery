# backend/app/models/blog.py - PostgreSQL 适配版
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from .base import Base


class Blog(Base):
    __tablename__ = "blogs"
    __table_args__ = {
        'extend_existing': True,
        'schema': 'public',
        'comment': '博客表'
    }

    id = Column(String(36), primary_key=True, comment="博客ID")
    title = Column(String(200), nullable=False, comment="博客标题")
    content = Column(Text, default="", comment="博客内容(Markdown)")
    cover_image_url = Column(String(512), default="", comment="封面图片URL")
    tags = Column(JSON, default=[], comment="标签列表")
    is_draft = Column(Boolean, default=True, comment="是否草稿")
    is_private = Column(Boolean, default=False, comment="是否私有")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    user = relationship(
        "app.models.user.User",
        backref="blogs",
        lazy="joined"
    )
    comments = relationship(
        "Comment",
        backref="blog",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Blog(id={self.id}, title={self.title}, user_id={self.user_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "cover_image_url": self.cover_image_url,
            "tags": self.tags,
            "is_draft": self.is_draft,
            "is_private": self.is_private,
            "user_id": self.user_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "user": self.user.to_dict() if self.user else None,
            "comment_count": self.comments.count() if hasattr(self, 'comments') else 0
        }


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = {
        'extend_existing': True,
        'schema': 'public',
        'comment': '评论表'
    }

    id = Column(String(36), primary_key=True, comment="评论ID")
    content = Column(Text, nullable=False, comment="评论内容")
    blog_id = Column(String(36), ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False, comment="博客ID")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    parent_id = Column(String(36), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, comment="父评论ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted = Column(Boolean, default=False, comment="是否删除")

    # 关联关系
    user = relationship(
        "app.models.user.User",
        backref="comments",
        lazy="joined"
    )
    parent = relationship(
        "Comment",
        remote_side=[id],
        backref="children",
        lazy="joined"
    )

    def __repr__(self):
        return f"<Comment(id={self.id}, blog_id={self.blog_id}, user_id={self.user_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "blog_id": self.blog_id,
            "user_id": self.user_id,
            "parent_id": self.parent_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "is_deleted": self.is_deleted,
            "user": self.user.to_dict() if self.user else None,
            "children": [child.to_dict() for child in self.children] if hasattr(self, 'children') else []
        }


# 添加别名导出
BlogPost = Blog
__all__ = ["Blog", "BlogPost", "Comment"]