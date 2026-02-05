import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from ..models.image import Image
from ..models.album import Album
from ..services.album_service import get_album_detail, update_album_image_count
from ..utils.file_utils import (
    ensure_dir, generate_unique_filename, validate_file_type,
    validate_file_size, generate_thumbnail, extract_exif_data
)

# 存储路径配置
BASE_UPLOAD_DIR = "static/uploads"
THUMBNAIL_DIR = "static/thumbnails"


# 上传图片
def upload_image(
        db: Session,
        file: UploadFile,
        album_id: str,
        user_id: str
) -> Image:
    # 验证文件
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型"
        )

    if not validate_file_size(file.filename, file.size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制"
        )

    # 验证图片集
    album = get_album_detail(db, album_id, user_id)
    if album.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限上传图片到该图片集"
        )

    # 确保目录存在
    user_dir = os.path.join(BASE_UPLOAD_DIR, user_id)
    thumbnail_dir = os.path.join(THUMBNAIL_DIR, user_id)
    ensure_dir(user_dir)
    ensure_dir(thumbnail_dir)

    # 保存文件
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(user_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # 生成缩略图
    thumbnail_filename = f"thumb_{filename.rsplit('.', 1)[0]}.jpg"
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
    generate_thumbnail(file_path, thumbnail_path)

    # 提取EXIF信息
    exif_data = extract_exif_data(file_path)

    # 创建图片记录
    image = Image(
        filename=file.filename,
        file_path=f"/{file_path}",
        thumbnail_path=f"/{thumbnail_path}" if os.path.exists(thumbnail_path) else "",
        file_type=file.content_type or "",
        file_size=file.size,
        album_id=album_id,
        user_id=user_id,
        exif_data=exif_data
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    # 更新图片集图片数量
    update_album_image_count(db, album_id)

    return image


# 获取图片集内图片列表
def get_album_images(
        db: Session,
        album_id: str,
        user_id: str = None,
        page: int = 1,
        page_size: int = 20
) -> tuple:
    # 验证图片集权限
    album = get_album_detail(db, album_id, user_id)

    query = db.query(Image).filter(
        Image.album_id == album_id,
        Image.is_deleted == False
    ).order_by(Image.sort_order, Image.created_at.desc())

    total = query.count()
    images = query.offset((page - 1) * page_size).limit(page_size).all()

    return images, total


# 获取图片详情
def get_image_detail(
        db: Session,
        image_id: str,
        user_id: str = None
) -> Image:
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.is_deleted == False
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片不存在或已删除"
        )

    # 验证权限
    album = get_album_detail(db, image.album_id, user_id)

    return image


# 更新图片排序
def update_image_sort(
        db: Session,
        image_ids: list,
        user_id: str
) -> bool:
    if not image_ids:
        return False

    # 验证所有图片属于当前用户
    images = db.query(Image).filter(
        Image.id.in_(image_ids),
        Image.user_id == user_id,
        Image.is_deleted == False
    ).all()

    if len(images) != len(image_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="包含无效的图片ID"
        )

    # 更新排序
    for index, image_id in enumerate(image_ids):
        image = next(img for img in images if img.id == image_id)
        image.sort_order = index

    db.commit()

    return True


# 删除图片
def delete_image(
        db: Session,
        image_id: str,
        user_id: str
) -> bool:
    image = get_image_detail(db, image_id, user_id)

    # 验证所有权
    if image.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除该图片"
        )

    image.is_deleted = True
    db.commit()

    # 更新图片集图片数量
    update_album_image_count(db, image.album_id)

    return True


# 批量删除图片
def batch_delete_images(
        db: Session,
        image_ids: list,
        user_id: str
) -> bool:
    if not image_ids:
        return False

    # 验证所有图片属于当前用户
    images = db.query(Image).filter(
        Image.id.in_(image_ids),
        Image.user_id == user_id,
        Image.is_deleted == False
    ).all()

    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有可删除的图片"
        )

    # 批量删除
    album_ids = set()
    for image in images:
        image.is_deleted = True
        album_ids.add(image.album_id)

    db.commit()

    # 更新图片集图片数量
    for album_id in album_ids:
        update_album_image_count(db, album_id)

    return True