from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..core.db import get_db
from ..core.dependencies import admin_required
from ..models.user import User
from ..models.album import Album
from ..models.image import Image
from ..models.blog import BlogPost, Comment
from ..services.user_service import (
    get_all_users, update_user_role, toggle_user_active
)
from ..utils.security_utils import Role
from ..utils.format_utils import model_to_dict, format_pagination_response

router = APIRouter()


# 获取所有用户列表
@router.get("/users")
async def list_all_users(
        page: int = 1,
        page_size: int = 10,
        keyword: str = None,
        role: str = None,
        is_active: bool = None,
        current_user=Depends(admin_required),
        db: Session = Depends(get_db)
):
    users, total = get_all_users(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        role=role,
        is_active=is_active
    )

    return {
        "code": 200,
        "message": "获取用户列表成功",
        "data": format_pagination_response(
            items=[model_to_dict(user, exclude=["hashed_password"]) for user in users],
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 修改用户角色
@router.put("/users/{user_id}/role")
async def change_user_role(
        user_id: str,
        role: Role,
        current_user=Depends(admin_required),
        db: Session = Depends(get_db)
):
    # 禁止修改自己的角色
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )

    user = update_user_role(
        db=db,
        user_id=user_id,
        role=role
    )

    return {
        "code": 200,
        "message": "用户角色修改成功",
        "data": model_to_dict(user, exclude=["hashed_password"])
    }


# 禁用/启用用户
@router.put("/users/{user_id}/active")
async def change_user_active_status(
        user_id: str,
        is_active: bool,
        current_user=Depends(admin_required),
        db: Session = Depends(get_db)
):
    # 禁止禁用自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己的账号"
        )

    user = toggle_user_active(
        db=db,
        user_id=user_id,
        is_active=is_active
    )

    status_text = "启用" if is_active else "禁用"

    return {
        "code": 200,
        "message": f"用户{status_text}成功",
        "data": model_to_dict(user, exclude=["hashed_password"])
    }


# 获取系统统计信息
@router.get("/system/stats")
async def get_system_statistics(
        current_user=Depends(admin_required),
        db: Session = Depends(get_db)
):
    # 用户统计
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.role == Role.ADMIN).count()

    # 内容统计
    total_albums = db.query(Album).filter(Album.is_deleted == False).count()
    total_images = db.query(Image).filter(Image.is_deleted == False).count()
    total_blogs = db.query(BlogPost).filter(BlogPost.is_draft == False).count()
    total_comments = db.query(Comment).count()

    # 存储统计
    # 实际项目中应计算文件大小总和
    storage_usage = {
        "total_size": 0,
        "images_size": 0,
        "albums_count": total_albums,
        "users_count": total_users
    }

    # 最近7天新增
    from datetime import datetime, timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)

    new_users_7d = db.query(User).filter(User.created_at >= seven_days_ago).count()
    new_albums_7d = db.query(Album).filter(
        Album.created_at >= seven_days_ago,
        Album.is_deleted == False
    ).count()
    new_images_7d = db.query(Image).filter(
        Image.created_at >= seven_days_ago,
        Image.is_deleted == False
    ).count()

    stats = {
        "user_stats": {
            "total": total_users,
            "active": active_users,
            "admin": admin_users,
            "new_7d": new_users_7d
        },
        "content_stats": {
            "albums": total_albums,
            "images": total_images,
            "blogs": total_blogs,
            "comments": total_comments,
            "new_albums_7d": new_albums_7d,
            "new_images_7d": new_images_7d
        },
        "storage_stats": storage_usage
    }

    return {
        "code": 200,
        "message": "获取系统统计信息成功",
        "data": stats
    }


# 获取用户行为日志（简化版）
@router.get("/logs/action")
async def get_user_action_logs(
        user_id: str = None,
        action: str = None,
        start_time: str = None,
        end_time: str = None,
        page: int = 1,
        page_size: int = 10,
        current_user=Depends(admin_required),
        db: Session = Depends(get_db)
):
    # 实际项目中应实现完整的日志系统
    # 这里返回模拟数据
    logs = []
    total = 0

    return {
        "code": 200,
        "message": "获取用户行为日志成功",
        "data": format_pagination_response(
            items=logs,
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 管理敏感词
@router.post("/sensitive-words")
async def manage_sensitive_word_list(
        words: List[str],
        action: str,  # add/delete/replace
        replace_word: str = "*",
        current_user=Depends(admin_required),
        db: Session = Depends(get_db)
):
    # 实际项目中应将敏感词存储到数据库
    # 这里仅返回操作结果
    action_text = {
        "add": "添加",
        "delete": "删除",
        "replace": "替换"
    }.get(action, "操作")

    return {
        "code": 200,
        "message": f"敏感词{action_text}成功",
        "data": {
            "action": action,
            "words": words,
            "count": len(words)
        }
    }