"""Mask规格模型"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class DMaskSpec(Base):
    """Mask规格表模型，存储产品的mask尺寸规格"""
    __tablename__ = "MASK_SPEC"
    
    productspecname = Column(String(64), primary_key=True, index=True)  # 产品规格名称
    x_panels = Column(Integer)  # X轴Panel数
    y_panels = Column(Integer)  # Y轴Panel数
    full_shot = Column(Integer)  # 全图曝光步骤号
    remark = Column(String(255))  # 备注
    createuser = Column(String(20))  # 创建用户
    createtime = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间
