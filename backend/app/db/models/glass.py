"""玻璃模型"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Glass(Base):
    """玻璃表模型"""
    __tablename__ = "product"
    
    glassid = Column(String(50), primary_key=True, index=True, name="productname")  # GlassID
    lotname = Column(String(50), ForeignKey("lot.lotname"), index=True, nullable=False)  # lot批次ID,和lot表关联
    productspecname = Column(String(50), index=True)  # 产品规格名称
    
    # 关系
    defects = relationship("Defect", back_populates="glass")
