"""玻璃相关的数据验证模型"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.api.schemas.defect import DefectResponse


class GlassBase(BaseModel):
    """玻璃基础模型"""
    glass_id: str = Field(..., description="玻璃编号")
    lot_id: int = Field(..., description="所属批次ID")
    status: str = Field(default="pending", description="状态：pending, inspected, qualified, unqualified")
    thickness: Optional[float] = Field(None, description="厚度")
    dimensions: Optional[str] = Field(None, description="尺寸")


class GlassCreate(GlassBase):
    """玻璃创建模型"""
    pass


class GlassUpdate(BaseModel):
    """玻璃更新模型"""
    status: Optional[str] = None
    thickness: Optional[float] = None
    dimensions: Optional[str] = None


class GlassResponse(GlassBase):
    """玻璃响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    inspected_by: Optional[int] = None
    
    class Config:
        orm_mode = True


class GlassWithDefectsResponse(GlassResponse):
    """包含缺陷信息的玻璃响应模型"""
    defects: List[DefectResponse] = []