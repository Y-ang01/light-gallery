from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from ..core.db import get_db
from ..core.dependencies import get_current_user
from ..services.blog_service import (
    create_blog_post, get_blog_list, get_blog_detail, update_blog_post,
    delete_blog_post, create_comment, get_blog_comments, delete_comment,
    upload_blog_attachment
)
from ..utils.format_utils import model_to_dict, format_pagination_response

router = APIRouter()


# 创建博客
@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_new_blog(
        title: str,
        content: str,
        is_draft: bool = False,
        is_private: bool = False,
        cover_image_url: str = None,
        tags: List[str] = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    post = create_blog_post(
        db=db,
        user_id=current_user.id,
        title=title,
        content=content,
        is_draft=is_draft,
        is_private=is_private,
        cover_image_url=cover_image_url,
        tags=tags
    )

    return {
        "code": 200,
        "message": "博客创建成功",
        "data": model_to_dict(post)
    }


# 获取博客列表
@router.get("/posts")
async def list_blogs(
        page: int = 1,
        page_size: int = 10,
        keyword: str = None,
        sort: str = "created_at",
        order: str = "desc",
        is_private: bool = None,
        is_draft: bool = False,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 普通用户只能查看自己的草稿和公开博客
    user_id = current_user.id if is_draft else None

    posts, total = get_blog_list(
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        keyword=keyword,
        sort=sort,
        order=order,
        is_private=is_private,
        is_draft=is_draft
    )

    # 补充作者信息
    posts_data = []
    for post in posts:
        post_dict = model_to_dict(post)
        post_dict["author_username"] = post.user.username
        posts_data.append(post_dict)

    return {
        "code": 200,
        "message": "获取博客列表成功",
        "data": format_pagination_response(
            items=posts_data,
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 获取博客详情
@router.get("/posts/{post_id}")
async def get_blog(
        post_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    post = get_blog_detail(
        db=db,
        post_id=post_id,
        user_id=current_user.id
    )

    post_dict = model_to_dict(post)
    post_dict["author_username"] = post.user.username

    return {
        "code": 200,
        "message": "获取博客详情成功",
        "data": post_dict
    }


# 更新博客
@router.put("/posts/{post_id}")
async def update_blog(
        post_id: str,
        title: str = None,
        content: str = None,
        is_draft: bool = None,
        is_private: bool = None,
        cover_image_url: str = None,
        tags: List[str] = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    post = update_blog_post(
        db=db,
        post_id=post_id,
        user_id=current_user.id,
        title=title,
        content=content,
        is_draft=is_draft,
        is_private=is_private,
        cover_image_url=cover_image_url,
        tags=tags
    )

    return {
        "code": 200,
        "message": "博客更新成功",
        "data": model_to_dict(post)
    }


# 删除博客
@router.delete("/posts/{post_id}")
async def remove_blog(
        post_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    result = delete_blog_post(
        db=db,
        post_id=post_id,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "博客删除成功",
        "data": {"success": result}
    }


# 获取博客评论
@router.get("/posts/{post_id}/comments")
async def list_blog_comments(
        post_id: str,
        page: int = 1,
        page_size: int = 20,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    comments, total = get_blog_comments(
        db=db,
        post_id=post_id,
        page=page,
        page_size=page_size
    )

    # 补充评论作者信息
    comments_data = []
    for comment in comments:
        comment_dict = model_to_dict(comment)
        comment_dict["author_username"] = comment.user.username

        # 处理回复
        if hasattr(comment, 'replies') and comment.replies:
            comment_dict["replies"] = []
            for reply in comment.replies:
                reply_dict = model_to_dict(reply)
                reply_dict["author_username"] = reply.user.username
                comment_dict["replies"].append(reply_dict)

        comments_data.append(comment_dict)

    return {
        "code": 200,
        "message": "获取评论列表成功",
        "data": format_pagination_response(
            items=comments_data,
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 发表博客评论
@router.post("/posts/{post_id}/comments")
async def add_blog_comment(
        post_id: str,
        content: str,
        parent_id: str = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    comment = create_comment(
        db=db,
        post_id=post_id,
        user_id=current_user.id,
        content=content,
        parent_id=parent_id
    )

    comment_dict = model_to_dict(comment)
    comment_dict["author_username"] = current_user.username

    return {
        "code": 200,
        "message": "评论发表成功",
        "data": comment_dict
    }


# 删除博客评论
@router.delete("/comments/{comment_id}")
async def remove_blog_comment(
        comment_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    result = delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "评论删除成功",
        "data": {"success": result}
    }


# 上传博客附件
@router.post("/upload-attachment")
async def upload_attachment(
        file: UploadFile = File(...),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    file_path = upload_blog_attachment(
        db=db,
        file=file,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "附件上传成功",
        "data": {"url": file_path, "filename": file.filename}
    }