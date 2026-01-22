# Apply pydantic patch for Python 3.9 compatibility
import pydantic_patch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import api_router
from app.core.config import settings


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Mac Insp 玻璃缺陷检测系统API"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(api_router, prefix="/mac/api/v1")

# 根路径
@app.get("/")
async def root():
    return {"message": "Mac Insp API", "version": "1.0.0"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )