from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.album import Album
from ..models.image import Image
from ..models.user import User
from ..utils.security_utils import (
    AlbumPermission, get_album_password_hash, verify_album_password
)


# 创建图片集
def create_album(
        db: Session,
        user_id: str,
        name: str,
        description: str = None,
        permission: AlbumPermission = AlbumPermission.PUBLIC,
        password: str = None
) -> Album:
    # 验证名称
    if not name or len(name) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片集名称不能为空且长度不能超过100字符"
        )

    # 密码保护验证
    password_hash = None
    if permission == AlbumPermission.PROTECTED:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码保护的图片集必须设置密码"
            )
        password_hash = get_album_password_hash(password)

    # 创建图片集
    album = Album(
        name=name,
        description=description,
        user_id=user_id,
        permission=permission,
        password_hash=password_hash
    )

    db.add(album)
    db.commit()
    db.refresh(album)

    return album


# 获取图片集列表
def get_album_list(
        db: Session,
        user_id: str = None,
        page: int = 1,
        page_size: int = 10,
        permission: AlbumPermission = None
) -> tuple:
    query = db.query(Album).filter(Album.is_deleted == False)

    # 筛选条件
    if user_id:
        query = query.filter(Album.user_id == user_id)

    if permission:
        query = query.filter(Album.permission == permission)

    # 总数
    total = query.count()

    # 分页
    albums = query.order_by(Album.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return albums, total


# 获取图片集详情
def get_album_detail(
        db: Session,
        album_id: str,
        user_id: str = None,
        password: str = None
) -> Album:
    album = db.query(Album).filter(
        Album.id == album_id,
        Album.is_deleted == False
    ).first()

    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片集不存在或已删除"
        )

    # 权限验证
    if album.permission == AlbumPermission.PRIVATE:
        # 私密图片集仅所有者可访问
        if not user_id or album.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限访问该私密图片集"
            )
    elif album.permission == AlbumPermission.PROTECTED:
        # 密码保护图片集验证密码
        if not user_id or album.user_id != user_id:
            if not password or not verify_album_password(password, album.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="图片集密码错误"
                )

    return album


# 更新图片集信息
def update_album(
        db: Session,
        album_id: str,
        user_id: str,
        name: str = None,
        description: str = None,
        permission: AlbumPermission = None,
        password: str = None,
        cover_image_id: str = None
) -> Album:
    album = get_album_detail(db, album_id, user_id)

    # 验证所有权
    if album.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改该图片集"
        )

    # 更新字段
    if name and name != album.name:
        album.name = name

    if description is not None:
        album.description = description

    if permission and permission != album.permission:
        album.permission = permission

        # 更新密码
        if permission == AlbumPermission.PROTECTED:
            if not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="密码保护的图片集必须设置密码"
                )
            album.password_hash = get_album_password_hash(password)
        else:
            album.password_hash = None

    if cover_image_id:
        # 验证封面图片属于该图片集
        image = db.query(Image).filter(
            Image.id == cover_image_id,
            Image.album_id == album_id
        ).first()

        if not image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="封面图片不属于该图片集"
            )

        album.cover_image_id = cover_image_id

    db.commit()
    db.refresh(album)

    return album


# 删除图片集（移到回收站）
def delete_album(db: Session, album_id: str, user_id: str) -> bool:
    album = get_album_detail(db, album_id, user_id)

    # 验证所有权
    if album.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除该图片集"
        )

    album.is_deleted = True
    db.commit()

    return True


# 恢复回收站图片集
def restore_album(db: Session, album_id: str, user_id: str) -> Album:
    album = db.query(Album).filter(
        Album.id == album_id,
        Album.is_deleted == True
    ).first()

    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回收站中不存在该图片集"
        )

    # 验证所有权
    if album.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限恢复该图片集"
        )

    album.is_deleted = False
    db.commit()
    db.refresh(album)

    return album


# 获取回收站图片集
def get_recycle_albums(
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 10
) -> tuple:
    query = db.query(Album).filter(
        Album.user_id == user_id,
        Album.is_deleted == True
    )

    total = query.count()
    albums = query.order_by(Album.deleted_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return albums, total


# 更新图片集图片数量
def update_album_image_count(db: Session, album_id: str):
    album = db.query(Album).filter(Album.id == album_id).first()
    if album:
        count = db.query(Image).filter(
            Image.album_id == album_id,
            Image.is_deleted == False
        ).count()
        album.image_count = count
        db.commit()