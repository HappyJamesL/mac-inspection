"""API路由模块"""
from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.lots import router as lots_router
from app.api.routes.defects import router as defects_router
from app.api.routes.init import router as init_router
from app.api.routes.product import router as product_router
from app.api.routes.historical import router as historical_router

# 创建主路由
api_router = APIRouter()

# 包含各个子路由
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(init_router, prefix="", tags=["init"])
api_router.include_router(product_router, prefix="", tags=["product"])
api_router.include_router(lots_router, prefix="/lots", tags=["lots"])
api_router.include_router(defects_router, prefix="", tags=["defects"])
api_router.include_router(historical_router, prefix="/historical", tags=["historical"])