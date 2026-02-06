# backend/app/services/blog_service.py - 修复导入 + 完善逻辑
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from backend.app.models.blog import Blog
# 现在能正确导入（BlogPost 是 Blog 的别名，Comment 已定义）
from ..models.blog import BlogPost, Comment


# ========== 博客相关服务 ==========
def create_blog_post(
        db: Session,
        title: str,
        content: str,
        user_id: str,
        cover_image_url: str = "",
        tags=None,
        is_draft: bool = True,
        is_private: bool = False
) -> BlogPost:
    """创建博客"""
    if tags is None:
        tags = []
    blog_post = BlogPost(
        id=str(uuid.uuid4()),
        title=title,
        content=content,
        cover_image_url=cover_image_url,
        tags=tags,
        is_draft=is_draft,
        is_private=is_private,
        user_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(blog_post)
    db.commit()
    db.refresh(blog_post)
    return blog_post


def get_blog_post_by_id(
        db: Session,
        blog_id: str,
        user_id: Optional[str] = None
) -> Optional[BlogPost]:
    """根据ID获取博客"""
    query = db.query(BlogPost).filter(BlogPost.id == blog_id)

    # 如果不是作者，只能看非私有、非草稿的博客
    if user_id:
        query = query.filter(
            or_(
                BlogPost.user_id == user_id,
                and_(
                    BlogPost.is_private == False,
                    BlogPost.is_draft == False
                )
            )
        )
    else:
        query = query.filter(
            BlogPost.is_private == False,
            BlogPost.is_draft == False
        )

    return query.first()


def get_blog_posts(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        keyword: str = "",
        sort_field: str = "created_at",
        sort_order: str = "desc",
        user_id: Optional[str] = None,
        is_draft: Optional[bool] = None
) -> tuple[list[type[Blog]], int]:
    """获取博客列表"""
    query = db.query(BlogPost)

    # 筛选条件
    if keyword:
        query = query.filter(
            or_(
                BlogPost.title.contains(keyword),
                BlogPost.content.contains(keyword),
                BlogPost.tags.contains(keyword)
            )
        )

    if user_id:
        query = query.filter(BlogPost.user_id == user_id)

    if is_draft is not None:
        query = query.filter(BlogPost.is_draft == is_draft)

    # 非作者只能看公开博客
    if not user_id:
        query = query.filter(
            BlogPost.is_private == False,
            BlogPost.is_draft == False
        )

    # 总数
    total = query.count()

    # 排序
    if sort_order == "desc":
        query = query.order_by(getattr(BlogPost, sort_field).desc())
    else:
        query = query.order_by(getattr(BlogPost, sort_field).asc())

    # 分页
    blog_posts = query.offset(skip).limit(limit).all()

    return blog_posts, total


def update_blog_post(
        db: Session,
        blog_id: str,
        user_id: str,
        **kwargs
) -> type[Blog] | None:
    """更新博客"""
    blog_post = db.query(BlogPost).filter(
        BlogPost.id == blog_id,
        BlogPost.user_id == user_id
    ).first()

    if not blog_post:
        return None

    # 更新字段
    for key, value in kwargs.items():
        if hasattr(blog_post, key):
            setattr(blog_post, key, value)

    blog_post.updated_at = datetime.now()
    db.commit()
    db.refresh(blog_post)

    return blog_post


def delete_blog_post(
        db: Session,
        blog_id: str,
        user_id: str
) -> bool:
    """删除博客"""
    blog_post = db.query(BlogPost).filter(
        BlogPost.id == blog_id,
        BlogPost.user_id == user_id
    ).first()

    if not blog_post:
        return False

    db.delete(blog_post)
    db.commit()
    return True


# ========== 评论相关服务 ==========
def create_comment(
        db: Session,
        content: str,
        blog_id: str,
        user_id: str,
        parent_id: Optional[str] = None
) -> Comment:
    """创建评论"""
    comment = Comment(
        id=str(uuid.uuid4()),
        content=content,
        blog_id=blog_id,
        user_id=user_id,
        parent_id=parent_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_blog_id(
        db: Session,
        blog_id: str,
        skip: int = 0,
        limit: int = 20
) -> tuple[list[type[Comment]], int]:
    """获取博客评论"""
    query = db.query(Comment).filter(
        Comment.blog_id == blog_id,
        Comment.is_deleted == False
    )

    total = query.count()
    comments = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()

    return comments, total


def delete_comment(
        db: Session,
        comment_id: str,
        user_id: str
) -> bool:
    """删除评论（软删除）"""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.user_id == user_id
    ).first()

    if not comment:
        return False

    comment.is_deleted = True
    comment.updated_at = datetime.now()
    db.commit()

    return True