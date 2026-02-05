from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from ..models.blog import BlogPost, Comment
from ..models.user import User
from ..utils.file_utils import (
    ensure_dir, generate_unique_filename, validate_file_size
)
from ..utils.security_utils import filter_sensitive_words
import os

# 博客附件存储路径
BLOG_UPLOAD_DIR = "static/blog/uploads"


# 创建博客
def create_blog_post(
        db: Session,
        user_id: str,
        title: str,
        content: str,
        is_draft: bool = False,
        is_private: bool = False,
        cover_image_url: str = None,
        tags: list = None
) -> BlogPost:
    # 验证标题
    if not title or len(title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="博客标题不能为空且长度不能超过200字符"
        )

    # 验证内容（非草稿）
    if not is_draft and (not content or len(content) < 10):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="博客内容不能为空且长度不能少于10字符"
        )

    # 过滤敏感词
    title = filter_sensitive_words(title)
    content = filter_sensitive_words(content)

    # 处理标签
    if tags:
        # 去重、限制数量和长度
        tags = list(set(tags))[:5]
        tags = [tag.strip() for tag in tags if tag.strip() and len(tag.strip()) <= 10]

    # 创建博客
    post = BlogPost(
        title=title,
        content=content,
        user_id=user_id,
        is_draft=is_draft,
        is_private=is_private,
        cover_image_url=cover_image_url,
        tags=tags or []
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


# 获取博客列表
def get_blog_list(
        db: Session,
        user_id: str = None,
        page: int = 1,
        page_size: int = 10,
        keyword: str = None,
        sort: str = "created_at",
        order: str = "desc",
        is_private: bool = None,
        is_draft: bool = False
) -> tuple:
    query = db.query(BlogPost)

    # 筛选条件
    if user_id:
        query = query.filter(BlogPost.user_id == user_id)

    # 非草稿（公开列表）
    if not is_draft:
        query = query.filter(BlogPost.is_draft == False)

    # 私密博客仅作者可见
    if is_private is None and not user_id:
        query = query.filter(BlogPost.is_private == False)

    if is_private is not None:
        query = query.filter(BlogPost.is_private == is_private)

    if keyword:
        query = query.filter(
            (BlogPost.title.ilike(f"%{keyword}%")) |
            (BlogPost.content.ilike(f"%{keyword}%"))
        )

    # 排序
    if sort == "created_at":
        if order == "desc":
            query = query.order_by(BlogPost.created_at.desc())
        else:
            query = query.order_by(BlogPost.created_at.asc())
    elif sort == "view_count":
        if order == "desc":
            query = query.order_by(BlogPost.view_count.desc())
        else:
            query = query.order_by(BlogPost.view_count.asc())

    # 总数
    total = query.count()

    # 分页
    posts = query.offset((page - 1) * page_size).limit(page_size).all()

    return posts, total


# 获取博客详情
def get_blog_detail(
        db: Session,
        post_id: str,
        user_id: str = None
) -> BlogPost:
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="博客不存在"
        )

    # 权限验证
    if post.is_draft or post.is_private:
        if not user_id or post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问该博客"
            )

    # 增加阅读量
    post.view_count += 1
    db.commit()

    return post


# 更新博客
def update_blog_post(
        db: Session,
        post_id: str,
        user_id: str,
        title: str = None,
        content: str = None,
        is_draft: bool = None,
        is_private: bool = None,
        cover_image_url: str = None,
        tags: list = None
) -> BlogPost:
    post = get_blog_detail(db, post_id, user_id)

    # 验证所有权
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改该博客"
        )

    # 更新字段
    if title and title != post.title:
        post.title = filter_sensitive_words(title)

    if content is not None and content != post.content:
        post.content = filter_sensitive_words(content)

    if is_draft is not None:
        post.is_draft = is_draft

    if is_private is not None:
        post.is_private = is_private

    if cover_image_url is not None:
        post.cover_image_url = cover_image_url

    if tags is not None:
        # 处理标签
        tags = list(set(tags))[:5]
        tags = [tag.strip() for tag in tags if tag.strip() and len(tag.strip()) <= 10]
        post.tags = tags

    db.commit()
    db.refresh(post)

    return post


# 删除博客
def delete_blog_post(db: Session, post_id: str, user_id: str) -> bool:
    post = get_blog_detail(db, post_id, user_id)

    # 验证所有权
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除该博客"
        )

    db.delete(post)
    db.commit()

    return True


# 创建评论
def create_comment(
        db: Session,
        post_id: str,
        user_id: str,
        content: str,
        parent_id: str = None
) -> Comment:
    # 验证博客
    post = get_blog_detail(db, post_id)

    # 验证内容
    if not content or len(content) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="评论内容不能为空且长度不能超过1000字符"
        )

    # 过滤敏感词
    content = filter_sensitive_words(content)

    # 验证父评论
    parent_comment = None
    if parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == parent_id).first()
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父评论不存在"
            )

    # 创建评论
    comment = Comment(
        content=content,
        post_id=post_id,
        user_id=user_id,
        parent_id=parent_id
    )

    db.add(comment)

    # 更新博客评论数
    post.comment_count += 1

    db.commit()
    db.refresh(comment)

    return comment


# 获取博客评论
def get_blog_comments(
        db: Session,
        post_id: str,
        page: int = 1,
        page_size: int = 20
) -> tuple:
    # 验证博客
    get_blog_detail(db, post_id)

    query = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.parent_id == None  # 只获取顶级评论
    ).order_by(Comment.created_at.desc())

    total = query.count()
    comments = query.offset((page - 1) * page_size).limit(page_size).all()

    # 获取回复
    for comment in comments:
        replies = db.query(Comment).filter(
            Comment.parent_id == comment.id
        ).order_by(Comment.created_at.asc()).all()
        comment.replies = replies

    return comments, total


# 删除评论
def delete_comment(db: Session, comment_id: str, user_id: str) -> bool:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    # 验证权限（评论作者或博客作者）
    post = get_blog_detail(db, comment.post_id, user_id)
    if comment.user_id != user_id and post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除该评论"
        )

    # 删除评论及其回复
    db.query(Comment).filter(
        (Comment.id == comment_id) | (Comment.parent_id == comment_id)
    ).delete()

    # 更新博客评论数
    post.comment_count = max(0, post.comment_count - 1)

    db.commit()

    return True


# 上传博客附件
def upload_blog_attachment(
        db: Session,
        file: UploadFile,
        user_id: str
) -> str:
    # 验证文件大小（50MB）
    if file.size > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过50MB"
        )

    # 确保目录存在
    user_dir = os.path.join(BLOG_UPLOAD_DIR, user_id)
    ensure_dir(user_dir)

    # 保存文件
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(user_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return f"/{file_path}"