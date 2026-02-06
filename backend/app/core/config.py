# backend/app/core/config.py - 新增配置文件
import os
import urllib.parse


class Settings:
    # PostgreSQL 配置
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123456")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "light_gallery")
    DATABASE_URI: str = "postgresql://postgres:123456@localhost:5432/light_gallery"

    # 应用配置
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# 创建配置实例
settings = Settings()

# 导出配置
__all__ = ["settings"]