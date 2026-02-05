from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
from ..core.db import get_db
from ..core.dependencies import get_current_user
from ..services.image_service import (
    upload_image, get_album_images, get_image_detail,
    update_image_sort, delete_image, batch_delete_images
)
from ..utils.format_utils import model_to_dict, format_pagination_response
from ..utils.file_utils import extract_exif_data

router = APIRouter()
upload_router = APIRouter()


# 上传图片到图片集
@upload_router.post("/images/{album_id}")
async def upload_images_to_album(
        album_id: str,
        files: List[UploadFile] = File(...),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请选择要上传的图片"
        )

    uploaded_images = []
    for file in files:
        image = upload_image(
            db=db,
            file=file,
            album_id=album_id,
            user_id=current_user.id
        )
        uploaded_images.append(model_to_dict(image))

    return {
        "code": 200,
        "message": f"成功上传{len(uploaded_images)}张图片",
        "data": uploaded_images
    }


# 上传博客图片
@upload_router.post("/blog-image")
async def upload_blog_image(
        file: UploadFile = File(...),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 复用图片上传逻辑，使用特殊的博客图片集ID
    # 实际项目中可创建专门的博客图片存储逻辑
    image = upload_image(
        db=db,
        file=file,
        album_id=f"blog_{current_user.id}",  # 虚拟图片集ID
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "博客图片上传成功",
        "data": {"url": image.file_path}
    }


# 获取图片集内图片列表
@router.get("/album/{album_id}")
async def list_album_images(
        album_id: str,
        page: int = 1,
        page_size: int = 20,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    images, total = get_album_images(
        db=db,
        album_id=album_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    return {
        "code": 200,
        "message": "获取图片列表成功",
        "data": format_pagination_response(
            items=[model_to_dict(image) for image in images],
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 获取图片详情
@router.get("/{image_id}")
async def get_image(
        image_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    image = get_image_detail(
        db=db,
        image_id=image_id,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "获取图片详情成功",
        "data": model_to_dict(image)
    }


# 获取图片EXIF信息
@router.get("/{image_id}/exif")
async def get_image_exif(
        image_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    image = get_image_detail(
        db=db,
        image_id=image_id,
        user_id=current_user.id
    )

    # 如果数据库中没有EXIF数据，重新提取
    exif_data = image.exif_data
    if not exif_data and os.path.exists(image.file_path.lstrip('/')):
        exif_data = extract_exif_data(image.file_path.lstrip('/'))
        image.exif_data = exif_data
        db.commit()

    return {
        "code": 200,
        "message": "获取EXIF信息成功",
        "data": exif_data or {}
    }


# 下载图片
@router.get("/{image_id}/download")
async def download_image_file(
        image_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    image = get_image_detail(
        db=db,
        image_id=image_id,
        user_id=current_user.id
    )

    file_path = image.file_path.lstrip('/')
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片文件不存在"
        )

    return FileResponse(
        path=file_path,
        filename=image.filename,
        media_type=image.file_type
    )


# 批量下载图片
@router.post("/batch-download")
async def batch_download_images(
        image_ids: List[str] = Form(...),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 实际项目中应打包为ZIP文件返回
    # 这里返回图片URL列表，前端自行处理下载
    images = []
    for image_id in image_ids:
        image = get_image_detail(db=db, image_id=image_id, user_id=current_user.id)
        images.append({
            "id": image.id,
            "filename": image.filename,
            "url": image.file_path
        })

    return {
        "code": 200,
        "message": "获取批量下载链接成功",
        "data": images
    }


# 更新图片排序
@router.put("/sort")
async def sort_images(
        image_ids: List[str],
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    result = update_image_sort(
        db=db,
        image_ids=image_ids,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "图片排序更新成功",
        "data": {"success": result}
    }


# 删除图片
@router.delete("/{image_id}")
async def remove_image(
        image_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    result = delete_image(
        db=db,
        image_id=image_id,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "图片删除成功",
        "data": {"success": result}
    }


# 批量删除图片
@router.post("/batch-delete")
async def batch_remove_images(
        image_ids: List[str],
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    result = batch_delete_images(
        db=db,
        image_ids=image_ids,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": f"成功删除{len(image_ids)}张图片",
        "data": {"success": result}
    }