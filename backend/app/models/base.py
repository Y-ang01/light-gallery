# backend/app/models/base.py - 统一的 Base 类
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# 统一的元数据配置
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# 全局唯一的 Base 类
Base = declarative_base(metadata=metadata)

__all__ = ["Base", "metadata"]