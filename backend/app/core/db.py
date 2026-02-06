from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from ..core.config import settings
from ..models.base import Base  # 所有模型的父类Base
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. 创建引擎（连接已手动建表的light_gallery库）
engine = create_engine(
    settings.DATABASE_URI,
    echo=False,  # 关闭SQL日志（减少冗余）
    pool_pre_ping=True  # 验证连接有效性
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    try:
        logger.info("数据库连接初始化")
        with engine.connect():
            pass
        logger.info("数据库连接成功！")
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}", exc_info=True)
        raise


# 3. 数据库依赖函数（供接口调用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()