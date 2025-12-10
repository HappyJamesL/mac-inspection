"""玻璃相关路由"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models.user import User
from app.db.models.glass import Glass
from app.db.models.lot import Lot
from app.db.models.defect import Defect
from app.api.routes.auth import get_current_active_user
from app.api.schemas.glass import GlassCreate, GlassUpdate, GlassResponse, GlassWithDefectsResponse
from app.api.schemas.defect import DefectResponse

router = APIRouter()


@router.post("/", response_model=GlassResponse, status_code=status.HTTP_201_CREATED)
async def create_glass(
    glass_data: GlassCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新玻璃记录"""
    # 检查批次是否存在
    lot = db.query(Lot).filter(Lot.id == glass_data.lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    # 检查玻璃编号是否已存在
    existing_glass = db.query(Glass).filter(Glass.glass_id == glass_data.glass_id).first()
    if existing_glass:
        raise HTTPException(status_code=400, detail="玻璃编号已存在")
    
    # 创建新玻璃记录
    db_glass = Glass(**glass_data.model_dump())
    db.add(db_glass)
    db.commit()
    db.refresh(db_glass)
    
    return db_glass


@router.get("/", response_model=List[GlassResponse])
async def get_glasses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    lot_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取玻璃列表"""
    query = db.query(Glass)
    
    if lot_id:
        query = query.filter(Glass.lot_id == lot_id)
    
    if status:
        query = query.filter(Glass.status == status)
    
    glasses = query.offset(skip).limit(limit).all()
    return glasses


@router.get("/{glass_id}", response_model=GlassWithDefectsResponse)
async def get_glass(
    glass_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取玻璃详情（包含缺陷列表）"""
    glass = db.query(Glass).filter(Glass.id == glass_id).first()
    if not glass:
        raise HTTPException(status_code=404, detail="玻璃记录不存在")
    
    return glass


@router.get("/by-glass-id/{glass_code}", response_model=GlassWithDefectsResponse)
async def get_glass_by_glass_id(
    glass_code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """根据玻璃编号获取玻璃详情"""
    glass = db.query(Glass).filter(Glass.glass_id == glass_code).first()
    if not glass:
        raise HTTPException(status_code=404, detail="玻璃记录不存在")
    
    return glass


@router.put("/{glass_id}", response_model=GlassResponse)
async def update_glass(
    glass_id: int,
    glass_data: GlassUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新玻璃信息"""
    glass = db.query(Glass).filter(Glass.id == glass_id).first()
    if not glass:
        raise HTTPException(status_code=404, detail="玻璃记录不存在")
    
    # 更新字段
    update_data = glass_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(glass, field, value)
    
    # 如果状态变为已检测，设置检测人
    if glass_data.status == "inspected" and not glass.inspected_by:
        glass.inspected_by = current_user.id
    
    db.commit()
    db.refresh(glass)
    
    return glass


@router.delete("/{glass_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_glass(
    glass_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除玻璃记录"""
    # 检查是否为超级用户
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    glass = db.query(Glass).filter(Glass.id == glass_id).first()
    if not glass:
        raise HTTPException(status_code=404, detail="玻璃记录不存在")
    
    # 检查是否有相关的缺陷记录
    if glass.defects:
        raise HTTPException(status_code=400, detail="该玻璃下存在缺陷记录，无法删除")
    
    db.delete(glass)
    db.commit()
    
    return None


@router.post("/batch-create", response_model=List[GlassResponse], status_code=status.HTTP_201_CREATED)
async def batch_create_glasses(
    glasses_data: List[GlassCreate],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量创建玻璃记录"""
    created_glasses = []
    
    for glass_data in glasses_data:
        # 检查批次是否存在
        lot = db.query(Lot).filter(Lot.id == glass_data.lot_id).first()
        if not lot:
            raise HTTPException(status_code=404, detail=f"批次ID {glass_data.lot_id} 不存在")
        
        # 检查玻璃编号是否已存在
        existing_glass = db.query(Glass).filter(Glass.glass_id == glass_data.glass_id).first()
        if existing_glass:
            raise HTTPException(status_code=400, detail=f"玻璃编号 {glass_data.glass_id} 已存在")
        
        # 创建新玻璃记录
        db_glass = Glass(**glass_data.model_dump())
        db.add(db_glass)
        created_glasses.append(db_glass)
    
    db.commit()
    for glass in created_glasses:
        db.refresh(glass)
    
    return created_glasses


@router.get("/{glassId}/defects", response_model=List[Dict])
async def get_defects_by_glass_id(
    glassId: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """根据GlassID获取缺陷列表"""
    # 查询该玻璃的所有缺陷记录
    defects = db.query(Defect).filter(Defect.glass_id == glassId).all()
    
    # 构建响应数据
    result = []
    for defect in defects:
        defect_dict = defect.__dict__.copy()
        # 移除SQLAlchemy内部字段
        if '_sa_instance_state' in defect_dict:
            del defect_dict['_sa_instance_state']
        result.append(defect_dict)
    
    return result