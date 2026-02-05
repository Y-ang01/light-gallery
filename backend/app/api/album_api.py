from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..core.dependencies import get_current_user
from ..services.album_service import (
    create_album, get_album_list, get_album_detail, update_album,
    delete_album, restore_album, get_recycle_albums
)
from ..utils.security_utils import AlbumPermission, verify_album_password
from ..utils.format_utils import model_to_dict, format_pagination_response

router = APIRouter()


# 创建图片集
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_album(
        name: str,
        description: str = None,
        permission: AlbumPermission = AlbumPermission.PUBLIC,
        password: str = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    album = create_album(
        db=db,
        user_id=current_user.id,
        name=name,
        description=description,
        permission=permission,
        password=password
    )

    return {
        "code": 200,
        "message": "图片集创建成功",
        "data": model_to_dict(album)
    }


# 获取图片集列表
@router.get("/")
async def list_albums(
        page: int = 1,
        page_size: int = 10,
        permission: AlbumPermission = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    albums, total = get_album_list(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        permission=permission
    )

    return {
        "code": 200,
        "message": "获取图片集列表成功",
        "data": format_pagination_response(
            items=[model_to_dict(album) for album in albums],
            total=total,
            page=page,
            page_size=page_size
        )
    }


# 获取图片集详情
@router.get("/{album_id}")
async def get_album(
        album_id: str,
        password: str = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    album = get_album_detail(
        db=db,
        album_id=album_id,
        user_id=current_user.id,
        password=password
    )

    return {
        "code": 200,
        "message": "获取图片集详情成功",
        "data": model_to_dict(album)
    }


# 更新图片集信息
@router.put("/{album_id}")
async def update_album_info(
        album_id: str,
        name: str = None,
        description: str = None,
        permission: AlbumPermission = None,
        password: str = None,
        cover_image_id: str = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    album = update_album(
        db=db,
        album_id=album_id,
        user_id=current_user.id,
        name=name,
        description=description,
        permission=permission,
        password=password,
        cover_image_id=cover_image_id
    )

    return {
        "code": 200,
        "message": "更新图片集信息成功",
        "data": model_to_dict(album)
    }


# 删除图片集（移到回收站）
@router.delete("/{album_id}")
async def remove_album(
        album_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    result = delete_album(
        db=db,
        album_id=album_id,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "图片集已移到回收站",
        "data": {"success": result}
    }


# 验证图片集密码
@router.post("/{album_id}/verify-password")
async def verify_album_pwd(
        album_id: str,
        password: str,
        db: Session = Depends(get_db)
):
    album = get_album_detail(db=db, album_id=album_id)

    if album.permission != AlbumPermission.PROTECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图片集不需要密码验证"
        )

    if not verify_album_password(password, album.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="密码错误"
        )

    return {
        "code": 200,
        "message": "密码验证成功",
        "data": {"valid": True}
    }


# 设置图片集密码
@router.post("/{album_id}/password")
async def set_album_pwd(
        album_id: str,
        password: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    album = update_album(
        db=db,
        album_id=album_id,
        user_id=current_user.id,
        permission=AlbumPermission.PROTECTED,
        password=password
    )

    return {
        "code": 200,
        "message": "图片集密码设置成功",
        "data": model_to_dict(album)
    }


# 恢复回收站图片集
@router.post("/{album_id}/restore")
async def restore_deleted_album(
        album_id: str,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    album = restore_album(
        db=db,
        album_id=album_id,
        user_id=current_user.id
    )

    return {
        "code": 200,
        "message": "图片集恢复成功",
        "data": model_to_dict(album)
    }


# 获取回收站图片集列表
@router.get("/recycle")
async def list_recycle_albums(
        page: int = 1,
        page_size: int = 10,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    albums, total = get_recycle_albums(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    return {
        "code": 200,
        "message": "获取回收站图片集成功",
        "data": format_pagination_response(
            items=[model_to_dict(album) for album in albums],
            total=total,
            page=page,
            page_size=page_size
        )
    }