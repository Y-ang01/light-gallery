from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User
from ..utils.security_utils import (
    get_password_hash, verify_password, validate_username,
    validate_email, validate_password_strength
)


# 创建用户
def create_user(
        db: Session,
        username: str,
        email: str,
        password: str
) -> User:
    # 验证用户名
    if not validate_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名格式错误，必须是3-20位字母、数字或下划线"
        )

    # 验证邮箱
    if not validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱格式错误"
        )

    # 验证密码强度
    if not validate_password_strength(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码强度不足，至少6位且包含字母和数字"
        )

    # 检查用户名是否已存在
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )

    # 创建用户
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# 获取用户信息
def get_user_by_id(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


# 获取用户信息（用户名/邮箱）
def get_user_by_credentials(db: Session, username: str) -> User:
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    return user


# 更新用户信息
def update_user_profile(
        db: Session,
        user_id: str,
        username: str = None,
        profile: str = None
) -> User:
    user = get_user_by_id(db, user_id)

    if username and username != user.username:
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        user.username = username

    if profile is not None:
        user.profile = profile

    db.commit()
    db.refresh(user)

    return user


# 更新用户头像
def update_user_avatar(db: Session, user_id: str, avatar_url: str) -> User:
    user = get_user_by_id(db, user_id)
    user.avatar_url = avatar_url

    db.commit()
    db.refresh(user)

    return user


# 管理员获取所有用户
def get_all_users(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        keyword: str = None,
        role: str = None,
        is_active: bool = None
) -> tuple:
    query = db.query(User)

    # 筛选条件
    if keyword:
        query = query.filter(
            (User.username.ilike(f"%{keyword}%")) |
            (User.email.ilike(f"%{keyword}%"))
        )

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # 总数
    total = query.count()

    # 分页
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    return users, total


# 管理员更新用户角色
def update_user_role(db: Session, user_id: str, role: str) -> User:
    user = get_user_by_id(db, user_id)
    user.role = role

    db.commit()
    db.refresh(user)

    return user


# 管理员禁用/启用用户
def toggle_user_active(db: Session, user_id: str, is_active: bool) -> User:
    user = get_user_by_id(db, user_id)
    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user