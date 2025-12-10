"""产品相关路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List

from app.db.base import get_db
from app.db.models.glasslayout import GlassLayout
from app.db.models.d_mask_spec import DMaskSpec

router = APIRouter()


@router.get("/product/{productspecname}/layout", response_model=Dict)
async def get_product_layout(
    productspecname: str,
    db: Session = Depends(get_db)
):
    """获取产品布局信息，包括panel坐标和mask规则"""
    try:
        # 截取前9位产品规格名称用于匹配
        productspecname_prefix = productspecname[:9]
        
        # 查询该产品的所有panel坐标
        panels = db.query(GlassLayout).filter(
            GlassLayout.tft_product == productspecname
        ).all()
        
        if not panels:
            raise HTTPException(status_code=404, detail=f"未找到产品 {productspecname} 的布局信息")
        
        # 查询该产品的mask规格，使用截取的前9位匹配
        mask_spec = db.query(DMaskSpec).filter(
            DMaskSpec.productspecname == productspecname_prefix
        ).first()
        
        # 构建panel列表，包含id和顺时针顺序的顶点数组
        panel_list = []
        for panel in panels:
            # 顺时针顺序：左上 -> 右上 -> 右下 -> 左下
            points = [
                [panel.x_left_up, panel.y_left_up],
                [panel.x_right_up, panel.y_right_up],
                [panel.x_right_down, panel.y_right_down],
                [panel.x_left_down, panel.y_left_down]
            ]
            panel_list.append({
                "id": panel.id,
                "points": points
            })
        
        # 构建响应数据
        response = {
            "glass_size": {"w": 920000, "h": 730000},  # 示例值，实际应从数据库获取
            "mask_rule": {
                "cover_x": mask_spec.x_panels if mask_spec else None,
                "cover_y": mask_spec.y_panels if mask_spec else None,
                "full_shot": mask_spec.full_shot if mask_spec else 1
            },
            "panels": panel_list
        }
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取产品布局失败: {str(e)}")
