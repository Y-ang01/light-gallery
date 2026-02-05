import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth_api, album_api, image_api, blog_api, search_api, admin_api
from app.core.db import create_tables

# 创建FastAPI应用实例
app = FastAPI(
    title="光影收藏馆API",
    description="专业图片集管理展示平台API接口文档",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（图片存储）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth_api.router, prefix="/api/v1/auth", tags=["用户认证"])
app.include_router(album_api.router, prefix="/api/v1/albums", tags=["图片集管理"])
app.include_router(image_api.router, prefix="/api/v1/images", tags=["图片管理"])
app.include_router(image_api.upload_router, prefix="/api/v1/upload", tags=["文件上传"])
app.include_router(blog_api.router, prefix="/api/v1/blog", tags=["博客管理"])
app.include_router(search_api.router, prefix="/api/v1/search", tags=["搜索功能"])
app.include_router(admin_api.router, prefix="/api/v1/admin", tags=["管理员功能"])

# 根路由
@app.get("/")
async def root():
    return {"message": "欢迎使用光影收藏馆API", "version": "1.0.0"}

# 创建数据库表（首次运行）
@app.on_event("startup")
async def startup_event():
    create_tables()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,  # 开发环境启用热重载
        log_level="info"
    )