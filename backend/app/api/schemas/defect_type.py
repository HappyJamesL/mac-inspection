"""缺陷类型相关的数据验证模型"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DefectTypeBase(BaseModel):
    """缺陷类型基础模型"""
    code: str = Field(..., description="缺陷代码")
    name: str = Field(..., description="缺陷名称")
    description: Optional[str] = Field(None, description="缺陷描述")
    severity_level: Optional[str] = Field(None, description="严重等级")
    color: Optional[str] = Field(None, description="显示颜色")


class DefectTypeCreate(DefectTypeBase):
    """缺陷类型创建模型"""
    pass


class DefectTypeUpdate(BaseModel):
    """缺陷类型更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    severity_level: Optional[str] = None
    color: Optional[str] = None


class DefectTypeResponse(DefectTypeBase):
    """缺陷类型响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True