"""缺陷类型模型"""
from sqlalchemy import Column, String, Text, Integer, CHAR

from app.db.base import Base


class DefectType(Base):
    """缺陷类型表模型"""
    __tablename__ = "reasoncode"
    
    code = Column(String(40), primary_key=True, index=True, name="reasoncode")  # 不良代码
    description = Column(Text, name="description")  # 不良代码描述
    superreasoncode = Column(String(40), name="superreasoncode")  # 不良代码的父代码
    levelno = Column(Integer, name="levelno")  # 不良代码的等级
    reasoncodetype = Column(String(40), name="REASONCODETYPE")  # 不良代码的归属类型
    codetype = Column(CHAR(10), name="codetype")  # 不良代码的类型
    color = Column(CHAR(10), name="color")  # 不良代码的颜色