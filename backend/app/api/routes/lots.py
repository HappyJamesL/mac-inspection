"""批次相关路由"""
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models.lot import Lot
from app.db.models.glass import Glass

router = APIRouter()


@router.get("/{lotname}/glasses", response_model=List[Dict])
async def get_glasses_by_lot(
    lotname: str,
    db: Session = Depends(get_db)
):
    """根据批次名称获取GlassID列表"""
    try:
        # 查询批次是否存在
        lot = db.query(Lot).filter(Lot.lotname == lotname).first()
        if not lot:
            raise HTTPException(status_code=404, detail="批次不存在")
        
        # 查询该批次下的所有Glass
        glasses = db.query(Glass).filter(Glass.lotname == lotname).all()
        
        # 构建响应数据
        result = []
        for glass in glasses:
            result.append({
                "glassid": glass.glassid,
                "lotname": glass.lotname,
                "productspecname": glass.productspecname
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Glass列表失败: {str(e)}")