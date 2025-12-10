"""FastAPI应用主入口"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.base import engine, Base
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("应用启动完成")
    
    yield
    
    # 关闭时执行
    print("应用关闭中...")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="MAC检测系统API",
    lifespan=lifespan
)

# 配置CORS
origins = settings.BACKEND_CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "MAC检测系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )