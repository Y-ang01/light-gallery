# backend/main.py - 最终版
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from app.core.db import init_database
# 加载环境变量
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 生命周期函数：启动时初始化数据库
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动前
    logger.info("🚀 FastAPI application starting up...")
    init_database()  # 调用重构后的初始化函数
    yield
    # 关闭后
    logger.info("🛑 FastAPI application shutting down...")

# 创建应用
app = FastAPI(
    title="Light Gallery API",
    version="1.0",
    lifespan=lifespan
)

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 延迟导入路由
from app.api import auth_api, album_api, image_api, blog_api, search_api, admin_api

# 注册路由
app.include_router(auth_api.router, prefix="/api/auth", tags=["认证"])
app.include_router(album_api.router, prefix="/api/albums", tags=["图片集"])
app.include_router(image_api.router, prefix="/api/images", tags=["图片"])
app.include_router(blog_api.router, prefix="/api/blogs", tags=["博客"])
app.include_router(search_api.router, prefix="/api/search", tags=["搜索"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["管理员"])


# 根路由
@app.get("/")
def root():
    return {"message": "Welcome to Light Gallery API"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="localhost", port=port, reload=True)