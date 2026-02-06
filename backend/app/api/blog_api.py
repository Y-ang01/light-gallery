# backend/app/api/blog_api.py - 修复导入路径 + 完善接口
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

# 导入数据库依赖和服务
from ..core.db import get_db
from ..services.blog_service import (
    create_blog_post,
    get_blog_post_by_id,
    get_blog_posts,
    update_blog_post,
    delete_blog_post,
    create_comment,
    get_comments_by_blog_id,
    delete_comment
)
from ..core.dependencies import get_current_user
from ..models.user import User

router = APIRouter()


# ========== Pydantic 模型 ==========
class BlogCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="博客标题")
    content: str = Field(..., min_length=10, description="博客内容")
    cover_image_url: Optional[str] = Field("", description="封面图片URL")
    tags: List[str] = Field([], description="标签列表")
    is_draft: bool = Field(True, description="是否草稿")
    is_private: bool = Field(False, description="是否私有")


class BlogUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="博客标题")
    content: Optional[str] = Field(None, min_length=10, description="博客内容")
    cover_image_url: Optional[str] = Field(None, description="封面图片URL")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    is_draft: Optional[bool] = Field(None, description="是否草稿")
    is_private: Optional[bool] = Field(None, description="是否私有")


class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=500, description="评论内容")
    parent_id: Optional[str] = Field(None, description="父评论ID")


# ========== 博客接口 ==========
@router.post("/", summary="创建博客", response_model=Dict[str, Any])
async def create_blog(
        req: BlogCreateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        blog = create_blog_post(
            db=db,
            title=req.title,
            content=req.content,
            cover_image_url=req.cover_image_url,
            tags=req.tags,
            is_draft=req.is_draft,
            is_private=req.is_private,
            user_id=current_user.id
        )
        return {
            "code": 200,
            "message": "博客创建成功",
            "data": blog.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建博客失败: {str(e)}")


@router.get("/{blog_id}", summary="获取博客详情", response_model=Dict[str, Any])
async def get_blog_detail(
        blog_id: str = Path(..., description="博客ID"),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        blog = get_blog_post_by_id(db=db, blog_id=blog_id, user_id=user_id)

        if not blog:
            raise HTTPException(status_code=404, detail="博客不存在或无访问权限")

        return {
            "code": 200,
            "message": "获取博客成功",
            "data": blog.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取博客失败: {str(e)}")


@router.get("/", summary="获取博客列表", response_model=Dict[str, Any])
async def get_blog_list(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, le=50, description="每页数量"),
        keyword: str = Query("", description="搜索关键词"),
        sort_field: str = Query("created_at", description="排序字段"),
        sort_order: str = Query("desc", description="排序方式"),
        is_draft: Optional[bool] = Query(None, description="是否草稿"),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    try:
        user_id = current_user.id if current_user else None
        skip = (page - 1) * size

        blogs, total = get_blog_posts(
            db=db,
            skip=skip,
            limit=size,
            keyword=keyword,
            sort_field=sort_field,
            sort_order=sort_order,
            user_id=user_id,
            is_draft=is_draft
        )

        return {
            "code": 200,
            "message": "获取博客列表成功",
            "data": {
                "list": [blog.to_dict() for blog in blogs],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取博客列表失败: {str(e)}")


@router.put("/{blog_id}", summary="更新博客", response_model=Dict[str, Any])
async def update_blog(
        blog_id: str = Path(..., description="博客ID"),
        req: BlogUpdateRequest = Depends(),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        # 转换请求数据为字典（过滤 None 值）
        update_data = {k: v for k, v in req.model_dump().items() if v is not None}

        blog = update_blog_post(
            db=db,
            blog_id=blog_id,
            user_id=current_user.id,
            **update_data
        )

        if not blog:
            raise HTTPException(status_code=404, detail="博客不存在或无修改权限")

        return {
            "code": 200,
            "message": "博客更新成功",
            "data": blog.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新博客失败: {str(e)}")


@router.delete("/{blog_id}", summary="删除博客", response_model=Dict[str, Any])
async def delete_blog(
        blog_id: str = Path(..., description="博客ID"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        success = delete_blog_post(
            db=db,
            blog_id=blog_id,
            user_id=current_user.id
        )

        if not success:
            raise HTTPException(status_code=404, detail="博客不存在或无删除权限")

        return {
            "code": 200,
            "message": "博客删除成功",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除博客失败: {str(e)}")


# ========== 评论接口 ==========
@router.post("/{blog_id}/comments", summary="创建评论", response_model=Dict[str, Any])
async def create_blog_comment(
        blog_id: str = Path(..., description="博客ID"),
        req: CommentCreateRequest = Depends(),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        # 检查博客是否存在
        blog = get_blog_post_by_id(db=db, blog_id=blog_id, user_id=current_user.id)
        if not blog:
            raise HTTPException(status_code=404, detail="博客不存在")

        comment = create_comment(
            db=db,
            content=req.content,
            blog_id=blog_id,
            user_id=current_user.id,
            parent_id=req.parent_id
        )

        return {
            "code": 200,
            "message": "评论创建成功",
            "data": comment.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建评论失败: {str(e)}")


@router.get("/{blog_id}/comments", summary="获取博客评论", response_model=Dict[str, Any])
async def get_blog_comments(
        blog_id: str = Path(..., description="博客ID"),
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=50, description="每页数量"),
        db: Session = Depends(get_db),
        current_user: Optional[User] = Depends(get_current_user)
):
    try:
        skip = (page - 1) * size
        comments, total = get_comments_by_blog_id(
            db=db,
            blog_id=blog_id,
            skip=skip,
            limit=size
        )

        return {
            "code": 200,
            "message": "获取评论成功",
            "data": {
                "list": [comment.to_dict() for comment in comments],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评论失败: {str(e)}")


@router.delete("/comments/{comment_id}", summary="删除评论", response_model=Dict[str, Any])
async def delete_blog_comment(
        comment_id: str = Path(..., description="评论ID"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        success = delete_comment(
            db=db,
            comment_id=comment_id,
            user_id=current_user.id
        )

        if not success:
            raise HTTPException(status_code=404, detail="评论不存在或无删除权限")

        return {
            "code": 200,
            "message": "评论删除成功",
            "data": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除评论失败: {str(e)}")