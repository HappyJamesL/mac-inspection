"""批次模型"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Lot(Base):
    """批次表模型"""
    __tablename__ = "lot"
    
    lotname = Column(String(40), primary_key=True, index=True)  # 生产批次LOT名称
    processoperationname = Column(String(40))  # 工序站点名称
    carriername = Column(String(40))  # Carrier名称
    productrequestname = Column(String(40))  # 工单号
    productspecname = Column(String(40), index=True)  # 产品规格名称
    machinename = Column(String(40), index=True)  # 机器名称
    portname = Column(String(40))  # 端口名称
    
    # 关系
    glasses = relationship("Glass", backref="lot")