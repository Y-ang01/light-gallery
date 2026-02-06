# backend/app/core/config.py - 新增配置文件
import os
import urllib.parse
from typing import Optional


class Settings:
    # PostgreSQL 配置
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123456")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "light_gallery")

    # 关键：URL 编码密码（处理特殊字符）
    @property
    def DATABASE_URL(self) -> str:
        encoded_password = urllib.parse.quote_plus(self.POSTGRES_PASSWORD)

        # PostgreSQL 连接 URL 格式
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{encoded_password}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # 应用配置
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# 创建配置实例
settings = Settings()

# 导出配置
__all__ = ["settings"]