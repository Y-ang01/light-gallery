from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, String
from ..models.album import Album
from ..models.image import Image
from ..models.blog import BlogPost
from ..utils.security_utils import AlbumPermission


# 全文搜索
def full_text_search(
        db: Session,
        keyword: str,
        type: str = None,
        user_id: str = None,
        page: int = 1,
        page_size: int = 10
) -> tuple:
    results = []
    total = 0

    # 构建搜索条件
    if not keyword:
        return results, total

    # 搜索图片集
    if type is None or type == "album":
        album_query = db.query(Album).filter(
            Album.is_deleted == False,
            or_(
                Album.name.ilike(f"%{keyword}%"),
                Album.description.ilike(f"%{keyword}%")
            )
        )

        # 权限过滤
        if not user_id:
            album_query = album_query.filter(Album.permission == AlbumPermission.PUBLIC)
        else:
            album_query = album_query.filter(
                or_(
                    Album.user_id == user_id,
                    Album.permission == AlbumPermission.PUBLIC
                )
            )

        albums = album_query.all()
        for album in albums:
            results.append({
                "type": "album",
                "id": album.id,
                "name": album.name,
                "description": album.description,
                "image_count": album.image_count,
                "permission": album.permission.value,
                "created_at": album.created_at
            })

    # 搜索图片
    if type is None or type == "image":
        image_query = db.query(Image).join(Album).filter(
            Image.is_deleted == False,
            Album.is_deleted == False,
            or_(
                Image.filename.ilike(f"%{keyword}%"),
                func.cast(Image.exif_data["camera_model"], String).ilike(f"%{keyword}%")
            )
        )

        # 权限过滤
        if not user_id:
            image_query = image_query.filter(Album.permission == AlbumPermission.PUBLIC)
        else:
            image_query = image_query.filter(
                or_(
                    Album.user_id == user_id,
                    Album.permission == AlbumPermission.PUBLIC
                )
            )

        images = image_query.all()
        for image in images:
            results.append({
                "type": "image",
                "id": image.id,
                "filename": image.filename,
                "file_type": image.file_type,
                "file_size": image.file_size,
                "album_id": image.album_id,
                "album_name": image.album.name,
                "thumbnail_path": image.thumbnail_path,
                "created_at": image.created_at
            })

    # 搜索博客
    if type is None or type == "blog":
        blog_query = db.query(BlogPost).filter(
            BlogPost.is_draft == False,
            or_(
                BlogPost.title.ilike(f"%{keyword}%"),
                BlogPost.content.ilike(f"%{keyword}%")
            )
        )

        # 权限过滤
        if not user_id:
            blog_query = blog_query.filter(BlogPost.is_private == False)
        else:
            blog_query = blog_query.filter(
                or_(
                    BlogPost.user_id == user_id,
                    BlogPost.is_private == False
                )
            )

        blogs = blog_query.all()
        for blog in blogs:
            results.append({
                "type": "blog",
                "id": blog.id,
                "title": blog.title,
                "cover_image_url": blog.cover_image_url,
                "view_count": blog.view_count,
                "comment_count": blog.comment_count,
                "created_at": blog.created_at
            })

    # 总数
    total = len(results)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated_results = results[start:end]

    return paginated_results, total


# 高级搜索
def advanced_search(
        db: Session,
        keyword: str = None,
        type: str = None,
        start_time: str = None,
        end_time: str = None,
        permission: str = None,
        file_type: list = None,
        exif_camera: str = None,
        tags: list = None,
        user_id: str = None,
        page: int = 1,
        page_size: int = 10,
        sort: str = "created_at",
        order: str = "desc"
) -> tuple:
    results = []
    total = 0

    # 搜索图片集
    if type is None or type == "album":
        album_query = db.query(Album).filter(Album.is_deleted == False)

        # 关键词过滤
        if keyword:
            album_query = album_query.filter(
                or_(
                    Album.name.ilike(f"%{keyword}%"),
                    Album.description.ilike(f"%{keyword}%")
                )
            )

        # 时间过滤
        if start_time:
            album_query = album_query.filter(Album.created_at >= start_time)
        if end_time:
            album_query = album_query.filter(Album.created_at <= end_time)

        # 权限过滤
        if permission:
            album_query = album_query.filter(Album.permission == permission)

        # 用户权限过滤
        if not user_id:
            album_query = album_query.filter(Album.permission == AlbumPermission.PUBLIC)
        else:
            album_query = album_query.filter(
                or_(
                    Album.user_id == user_id,
                    Album.permission == AlbumPermission.PUBLIC
                )
            )

        # 排序
        if sort == "created_at":
            if order == "desc":
                album_query = album_query.order_by(Album.created_at.desc())
            else:
                album_query = album_query.order_by(Album.created_at.asc())

        # 总数
        album_total = album_query.count()

        # 分页
        albums = album_query.offset((page - 1) * page_size).limit(page_size).all()

        for album in albums:
            results.append({
                "type": "album",
                "id": album.id,
                "name": album.name,
                "description": album.description,
                "image_count": album.image_count,
                "permission": album.permission.value,
                "created_at": album.created_at
            })

        if type == "album":
            total = album_total

    # 搜索图片
    if type is None or type == "image":
        image_query = db.query(Image).join(Album).filter(
            Image.is_deleted == False,
            Album.is_deleted == False
        )

        # 关键词过滤
        if keyword:
            image_query = image_query.filter(
                or_(
                    Image.filename.ilike(f"%{keyword}%"),
                    func.cast(Image.exif_data["camera_model"], String).ilike(f"%{keyword}%")
                )
            )

        # 时间过滤
        if start_time:
            image_query = image_query.filter(Image.created_at >= start_time)
        if end_time:
            image_query = image_query.filter(Image.created_at <= end_time)

        # 权限过滤
        if permission:
            image_query = image_query.filter(Album.permission == permission)

        # 文件类型过滤
        if file_type and len(file_type) > 0:
            image_query = image_query.filter(Image.file_type.in_(file_type))

        # 相机型号过滤
        if exif_camera:
            image_query = image_query.filter(
                func.cast(Image.exif_data["camera_model"], String).ilike(f"%{exif_camera}%")
            )

        # 用户权限过滤
        if not user_id:
            image_query = image_query.filter(Album.permission == AlbumPermission.PUBLIC)
        else:
            image_query = image_query.filter(
                or_(
                    Album.user_id == user_id,
                    Album.permission == AlbumPermission.PUBLIC
                )
            )

        # 排序
        if sort == "created_at":
            if order == "desc":
                image_query = image_query.order_by(Image.created_at.desc())
            else:
                image_query = image_query.order_by(Image.created_at.asc())

        # 总数
        image_total = image_query.count()

        # 分页
        images = image_query.offset((page - 1) * page_size).limit(page_size).all()

        for image in images:
            results.append({
                "type": "image",
                "id": image.id,
                "filename": image.filename,
                "file_type": image.file_type,
                "file_size": image.file_size,
                "album_id": image.album_id,
                "album_name": image.album.name,
                "thumbnail_path": image.thumbnail_path,
                "created_at": image.created_at
            })

        if type == "image":
            total = image_total

    # 搜索博客
    if type is None or type == "blog":
        blog_query = db.query(BlogPost).filter(BlogPost.is_draft == False)

        # 关键词过滤
        if keyword:
            blog_query = blog_query.filter(
                or_(
                    BlogPost.title.ilike(f"%{keyword}%"),
                    BlogPost.content.ilike(f"%{keyword}%")
                )
            )

        # 时间过滤
        if start_time:
            blog_query = blog_query.filter(BlogPost.created_at >= start_time)
        if end_time:
            blog_query = blog_query.filter(BlogPost.created_at <= end_time)

        # 标签过滤
        if tags and len(tags) > 0:
            for tag in tags:
                blog_query = blog_query.filter(BlogPost.tags.any(tag))

        # 权限过滤
        if not user_id:
            blog_query = blog_query.filter(BlogPost.is_private == False)
        else:
            blog_query = blog_query.filter(
                or_(
                    BlogPost.user_id == user_id,
                    BlogPost.is_private == False
                )
            )

        # 排序
        if sort == "created_at":
            if order == "desc":
                blog_query = blog_query.order_by(BlogPost.created_at.desc())
            else:
                blog_query = blog_query.order_by(BlogPost.created_at.asc())
        elif sort == "view_count":
            if order == "desc":
                blog_query = blog_query.order_by(BlogPost.view_count.desc())
            else:
                blog_query = blog_query.order_by(BlogPost.view_count.asc())

        # 总数
        blog_total = blog_query.count()

        # 分页
        blogs = blog_query.offset((page - 1) * page_size).limit(page_size).all()

        for blog in blogs:
            results.append({
                "type": "blog",
                "id": blog.id,
                "title": blog.title,
                "cover_image_url": blog.cover_image_url,
                "view_count": blog.view_count,
                "comment_count": blog.comment_count,
                "created_at": blog.created_at
            })

        if type == "blog":
            total = blog_total

    # 混合搜索时计算总数
    if type is None:
        total = len(results)

    return results, total