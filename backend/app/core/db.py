# backend/app/core/db.py - 适配 PostgreSQL 版本
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import logging

# 导入配置
from .config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== 关键修改：PostgreSQL 连接配置 ==========
# 使用配置文件中的 URL，解决编码问题
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=20,
    max_overflow=50,
    pool_pre_ping=True,
    pool_recycle=3600,
    # PostgreSQL 编码配置
    connect_args={
        "options": "-c client_encoding=utf8"  # 强制 UTF-8 编码
    }
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# 线程安全的会话
ScopedSession = scoped_session(SessionLocal)


# 数据库依赖
def get_db():
    db = ScopedSession()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# 初始化数据库
def init_db():
    try:
        logger.info("Importing all models...")
        # 手动导入所有模型，明确依赖顺序
        from ..models.user import User  # 先导入无外键的User模型
        from ..models.album import Album
        from ..models.image import Image
        from ..models.blog import Blog, Comment

        logger.info("Creating database tables in order...")
        # 第一步：先创建users表（无外键，所有其他表都依赖它）
        User.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created table: users")

        # 第二步：创建依赖users的表（按无交叉依赖顺序）
        Album.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created table: albums")
        Blog.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created table: blogs")
        Comment.__table__.create(bind=engine, checkfirst=True)
        logger.info("Created table: comments")
        Image.__table__.create(bind=engine, checkfirst=True)  # 依赖users+albums
        logger.info("Created table: images")

        logger.info("All database tables created successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        raise


# 关闭数据库连接池
def close_db():
    try:
        logger.info("Closing database connections...")
        ScopedSession.remove()
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Failed to close database connections: {e}")