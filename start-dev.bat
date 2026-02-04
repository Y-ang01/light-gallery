@echo off
chcp 65001
cls
echo ================================
echo 启动光影收藏馆开发环境
echo ================================

REM 启动 Docker 服务
echo 1. 启动 Docker 服务...
docker system prune -f
docker-compose up -d

REM 启动后端服务
echo 2. 启动后端服务...
cd backend
start cmd /k "conda activate private-website && python run.py"

REM 启动前端服务
echo 3. 启动前端服务...
cd ..\frontend
start cmd /k "npm run dev"

echo ================================
echo 服务启动完成
echo 前端: http://localhost:5173
echo 后端API: http://localhost:8000/docs
echo pgAdmin: http://localhost:5050 (admin@lightgallery.com / admin123)
echo ================================
pause