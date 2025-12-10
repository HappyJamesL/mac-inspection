"""玻璃布局模型"""
from sqlalchemy import Column, String, Integer, PrimaryKeyConstraint
from app.db.base import Base


class GlassLayout(Base):
    """玻璃布局表模型，存储panel在glass上的物理坐标"""
    __tablename__ = "glasslayout"
    
    id = Column(Integer, index=True, nullable=False)  # 布局ID
    tft_product = Column(String(64), index=True, nullable=False, name="tft_product")  # TFT产品名称
    x_left_up = Column(Integer, name="x_left_up")  # 左上角X坐标
    x_left_down = Column(Integer, name="x_left_down")  # 左下角X坐标
    x_right_down = Column(Integer, name="x_right_down")  # 右下角X坐标
    x_right_up = Column(Integer, name="x_right_up")  # 右上角X坐标
    y_left_up = Column(Integer, name="y_left_up")  # 左上角Y坐标
    y_left_down = Column(Integer, name="y_left_down")  # 左下角Y坐标
    y_right_down = Column(Integer, name="y_right_down")  # 右下角Y坐标
    y_right_up = Column(Integer, name="y_right_up")  # 右上角Y坐标
    
    # 联合主键
    __table_args__ = (PrimaryKeyConstraint('tft_product', 'id'),)
