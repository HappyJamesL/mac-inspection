"""批次相关的数据验证模型"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.api.schemas.glass import GlassResponse


class LotBase(BaseModel):
    """批次基础模型"""
    lot_id: str = Field(..., description="批次号")
    product_id: str = Field(..., description="产品编号")
    quantity: int = Field(..., ge=1, description="批次数量")


class LotCreate(LotBase):
    """批次创建模型"""
    pass


class LotUpdate(BaseModel):
    """批次更新模型"""
    product_id: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)


class LotResponse(LotBase):
    """批次响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int
    
    class Config:
        orm_mode = True


class LotWithGlassesResponse(LotResponse):
    """包含玻璃信息的批次响应模型"""
    glasses: List[GlassResponse] = []