"""缺陷模型"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Defect(Base):
    """缺陷表模型"""
    __tablename__ = "mac_defect_records"
    
    uuid = Column(String(64), primary_key=True, index=True)  # 缺陷记录ID
    productname = Column(String(64), ForeignKey("product.productname"), nullable=False, index=True)  # 玻璃ID
    lotname = Column(String(20), index=True)  # 生产批次LOT名称
    productrequestname = Column(String(20), index=True)  # 工单号
    productspecname = Column(String(64), index=True)  # 产品型号名称
    defect_code = Column(String(20), index=True)  # 缺陷代码
    defect_type = Column(String(10))  # 缺陷类型
    panel_count = Column(String(10))  # 缺陷跨越的Panel数量
    is_symmetry = Column(String(1), default='N')  # 是否为MASK对称缺陷产生的记录
    machinename = Column(String(20))  # 机器名称
    operator_id = Column(String(20))  # 操作员ID
    inspector = Column(String(100))  # 检测人员姓名（多个用逗号分隔）
    processoperationname = Column(String(20), index=True)  # 工序站点名称
    inspection_type = Column(String(20))  # 检测类型：首检，过程检，异常加测，测膜边
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间
    
    # 所有Text类型的列（Oracle中是CLOB）放在最后
    panel_id = Column(Text, index=True)  # 面板ID，支持多个Panel ID
    geom_data = Column(Text)  # 缺陷坐标数据，JSON字符串
    remarks = Column(Text)  # 备注
    
    # 关系
    glass = relationship("Glass", foreign_keys=[productname], back_populates="defects")