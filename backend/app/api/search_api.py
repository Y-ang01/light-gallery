from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.db import get_db
from ..core.dependencies import get_current_user
from ..services.search_service import full_text_search, advanced_search
from ..utils.format_utils import format_pagination_response

router = APIRouter()


# 全文搜索
@router.get("/full-text")
async def search_all(
        keyword: str,
        type: str = None,
        page: int = 1,
        page_size: int = 10,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    results, total = full_text_search(
        db=db,
        keyword=keyword,
        type=type,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    return {
        "code": 200,
        "message": "搜索完成",
        "data": format_pagination_response(
            items=results,
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 高级搜索
@router.get("/advanced")
async def advanced_search_all(
        keyword: str = None,
        type: str = None,
        start_time: str = None,
        end_time: str = None,
        permission: str = None,
        file_type: List[str] = None,
        exif_camera: str = None,
        tags: List[str] = None,
        page: int = 1,
        page_size: int = 10,
        sort: str = "created_at",
        order: str = "desc",
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    results, total = advanced_search(
        db=db,
        keyword=keyword,
        type=type,
        start_time=start_time,
        end_time=end_time,
        permission=permission,
        file_type=file_type,
        exif_camera=exif_camera,
        tags=tags,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        sort=sort,
        order=order
    )

    return {
        "code": 200,
        "message": "高级搜索完成",
        "data": format_pagination_response(
            items=results,
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 筛选图片集
@router.get("/filter/albums")
async def filter_album_list(
        permission: str = None,
        create_time: str = None,
        image_count_min: int = None,
        image_count_max: int = None,
        page: int = 1,
        page_size: int = 10,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 转换时间范围
    start_time = None
    end_time = None
    if create_time:
        from datetime import datetime, timedelta
        now = datetime.now()
        if create_time == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif create_time == "week":
            start_time = now - timedelta(days=7)
        elif create_time == "month":
            start_time = now - timedelta(days=30)
        elif create_time == "year":
            start_time = now - timedelta(days=365)

    results, total = advanced_search(
        db=db,
        type="album",
        start_time=start_time,
        end_time=end_time,
        permission=permission,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    # 过滤图片数量
    filtered_results = []
    for item in results:
        if image_count_min and item["image_count"] < image_count_min:
            continue
        if image_count_max and item["image_count"] > image_count_max:
            continue
        filtered_results.append(item)

    return {
        "code": 200,
        "message": "图片集筛选完成",
        "data": format_pagination_response(
            items=filtered_results,
            total=len(filtered_results),
            page=page,
            page_size=page_size
        )
    }


# 筛选图片
@router.get("/filter/images")
async def filter_image_list(
        album_id: str = None,
        file_type: List[str] = None,
        size_min: int = None,
        size_max: int = None,
        exif_camera: str = None,
        exif_iso: List[int] = None,
        page: int = 1,
        page_size: int = 10,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    results, total = advanced_search(
        db=db,
        type="image",
        file_type=file_type,
        exif_camera=exif_camera,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    # 额外过滤条件
    filtered_results = []
    for item in results:
        # 图片集过滤
        if album_id and item["album_id"] != album_id:
            continue

        # 文件大小过滤
        if size_min and item["file_size"] < size_min:
            continue
        if size_max and item["file_size"] > size_max:
            continue

        filtered_results.append(item)

    return {
        "code": 200,
        "message": "图片筛选完成",
        "data": format_pagination_response(
            items=filtered_results,
            total=len(filtered_results),
            page=page,
            page_size=page_size
        )
    }