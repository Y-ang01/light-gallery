# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="光影收藏馆 API",
    version="1.0.0",
    description="光影收藏馆后端服务"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "光影收藏馆后端服务运行中",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc"
    }
