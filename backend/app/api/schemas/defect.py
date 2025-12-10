"""缺陷相关的数据验证模型"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


# 旧模型，保留用于兼容现有功能
class DefectBase(BaseModel):
    """缺陷基础模型"""
    glass_id: int = Field(..., description="所属玻璃ID")
    defect_type_id: int = Field(..., description="缺陷类型ID")
    x: float = Field(..., description="X坐标")
    y: float = Field(..., description="Y坐标")
    width: float = Field(..., gt=0, description="宽度")
    height: float = Field(..., gt=0, description="高度")
    severity: str = Field(default="medium", description="严重程度：low, medium, high")
    description: Optional[str] = Field(None, description="缺陷描述")
    image_url: Optional[str] = Field(None, description="缺陷图片URL")


class DefectCreate(DefectBase):
    """缺陷创建模型"""
    pass


class DefectUpdate(BaseModel):
    """缺陷更新模型"""
    defect_type_id: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    severity: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class DefectResponse(DefectBase):
    """缺陷响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: int
    defect_type: Optional[dict] = None  # 简化的缺陷类型信息
    
    class Config:
        from_attributes = True


class DefectWithDetailsResponse(DefectResponse):
    """包含详细信息的缺陷响应模型"""
    glass: Optional[dict] = None  # 简化的玻璃信息


# 新模型，用于技术规格要求的缺陷保存接口
class DefectSaveRequest(BaseModel):
    """缺陷保存请求模型"""
    uuid: str = Field(..., description="前端生成的唯一ID")
    glass_id: Optional[str] = Field(None, description="玻璃ID")
    lotname: Optional[str] = Field(None, description="生产批次LOT名称")
    productrequestname: Optional[str] = Field(None, description="工单号")
    product_id: str = Field(..., description="产品型号")
    defect_code: Optional[str] = Field("", description="缺陷代码 (如 C01)")
    defect_type: Optional[str] = Field("point", description="缺陷类型: point, line, curve, area")
    geom_data: Optional[List[List[float]]] = Field(None, description="缺陷轨迹坐标，JSON格式，数组形式如[[x1,y1],[x2,y2]]")
    panel_id: Optional[str] = Field(None, description="缺陷的Panel的IDs, 一个缺陷可能跨越多个Panel")
    is_symmetry: Optional[str] = Field("N", description="是否为 Mask 对称缺陷产生的记录")
    remark: Optional[str] = Field(None, description="备注")
    operator_id: Optional[str] = Field(None, description="操作员ID")
    machinename: Optional[str] = Field(None, description="机器名称")
    processoperationname: Optional[str] = Field(None, description="工序站点名称")


class DefectSaveResponse(BaseModel):
    """缺陷保存响应模型"""
    success: bool = Field(..., description="保存是否成功")
    uuid: str = Field(..., description="缺陷唯一ID")
    panel_id: Optional[str] = Field(None, description="判定的Panel ID")
    message: Optional[str] = Field(None, description="响应消息")
    
    class Config:
        from_attributes = True


class DefectQueryRequest(BaseModel):
    """缺陷查询请求模型"""
    glass_id: Optional[str] = Field(None, description="玻璃ID")
    lotname: Optional[str] = Field(None, description="生产批次LOT名称")
    productrequestname: Optional[str] = Field(None, description="工单号")
    product_id: Optional[str] = Field(None, description="产品型号")
    defect_code: Optional[str] = Field(None, description="缺陷代码")
    defect_type: Optional[str] = Field(None, description="缺陷类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    panel_id: Optional[str] = Field(None, description="Panel ID")
    is_symmetry: Optional[str] = Field(None, description="是否为 Mask 对称点")
    skip: int = Field(default=0, description="跳过的记录数")
    limit: int = Field(default=100, description="返回的记录数")


class DefectQueryResponse(BaseModel):
    """缺陷查询响应模型"""
    total: int = Field(..., description="总记录数")
    defects: List[Dict] = Field(..., description="缺陷列表")
    
    class Config:
        from_attributes = True