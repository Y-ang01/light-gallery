import enum
import re
from passlib.context import CryptContext


# 角色枚举
class Role(enum.Enum):
    GUEST = "GUEST"  # 游客
    USER = "USER"  # 普通用户
    AUTHOR = "AUTHOR"  # 作者
    ADMIN = "ADMIN"  # 管理员


# 图片集权限枚举
class AlbumPermission(enum.Enum):
    PUBLIC = "PUBLIC"  # 公开
    PROTECTED = "PROTECTED"  # 密码保护
    PRIVATE = "PRIVATE"  # 私密


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 验证密码
def verify_album_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 加密密码
def get_album_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 敏感词过滤
def filter_sensitive_words(text: str) -> str:
    # 示例敏感词列表，实际项目应从配置/数据库加载
    sensitive_words = ["敏感词1", "敏感词2", "敏感词3"]

    for word in sensitive_words:
        text = re.sub(word, "*" * len(word), text)

    return text


# 验证用户名
def validate_username(username: str) -> bool:
    # 用户名规则：3-20位，字母、数字、下划线
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))


# 验证邮箱
def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# 验证密码强度
def validate_password_strength(password: str) -> bool:
    # 密码规则：至少6位，包含字母和数字
    if len(password) < 6:
        return False
    if not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
        return False
    return True