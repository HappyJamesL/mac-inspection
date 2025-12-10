"""缺陷类型相关路由"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models.user import User
from app.db.models.defect_type import DefectType
from app.api.routes.auth import get_current_active_user
from app.api.schemas.defect_type import DefectTypeCreate, DefectTypeUpdate, DefectTypeResponse

router = APIRouter()


@router.post("/", response_model=DefectTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_defect_type(
    defect_type_data: DefectTypeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新缺陷类型"""
    # 检查缺陷代码是否已存在
    existing_defect_type = db.query(DefectType).filter(
        DefectType.code == defect_type_data.code
    ).first()
    if existing_defect_type:
        raise HTTPException(status_code=400, detail="缺陷代码已存在")
    
    # 检查缺陷名称是否已存在
    existing_defect_type = db.query(DefectType).filter(
        DefectType.name == defect_type_data.name
    ).first()
    if existing_defect_type:
        raise HTTPException(status_code=400, detail="缺陷名称已存在")
    
    # 创建新缺陷类型
    db_defect_type = DefectType(**defect_type_data.model_dump())
    db.add(db_defect_type)
    db.commit()
    db.refresh(db_defect_type)
    
    return db_defect_type


@router.get("/", response_model=List[DefectTypeResponse])
async def get_defect_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    code: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取缺陷类型列表"""
    query = db.query(DefectType)
    
    if code:
        query = query.filter(DefectType.code == code)
    
    defect_types = query.offset(skip).limit(limit).all()
    return defect_types


@router.get("/{defect_type_id}", response_model=DefectTypeResponse)
async def get_defect_type(
    defect_type_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取缺陷类型详情"""
    defect_type = db.query(DefectType).filter(DefectType.id == defect_type_id).first()
    if not defect_type:
        raise HTTPException(status_code=404, detail="缺陷类型不存在")
    
    return defect_type


@router.put("/{defect_type_id}", response_model=DefectTypeResponse)
async def update_defect_type(
    defect_type_id: int,
    defect_type_data: DefectTypeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新缺陷类型信息"""
    # 检查是否为超级用户
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    defect_type = db.query(DefectType).filter(DefectType.id == defect_type_id).first()
    if not defect_type:
        raise HTTPException(status_code=404, detail="缺陷类型不存在")
    
    # 如果更新名称，检查是否已存在
    if defect_type_data.name:
        existing_defect_type = db.query(DefectType).filter(
            DefectType.name == defect_type_data.name,
            DefectType.id != defect_type_id
        ).first()
        if existing_defect_type:
            raise HTTPException(status_code=400, detail="缺陷名称已存在")
    
    # 更新字段
    update_data = defect_type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(defect_type, field, value)
    
    db.commit()
    db.refresh(defect_type)
    
    return defect_type


@router.delete("/{defect_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_defect_type(
    defect_type_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除缺陷类型"""
    # 检查是否为超级用户
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    defect_type = db.query(DefectType).filter(DefectType.id == defect_type_id).first()
    if not defect_type:
        raise HTTPException(status_code=404, detail="缺陷类型不存在")
    
    # 检查是否有相关的缺陷记录
    if defect_type.defects:
        raise HTTPException(status_code=400, detail="该缺陷类型下存在缺陷记录，无法删除")
    
    db.delete(defect_type)
    db.commit()
    
    return None


@router.get("/by-code/{code}", response_model=DefectTypeResponse)
async def get_defect_type_by_code(
    code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """根据代码获取缺陷类型"""
    defect_type = db.query(DefectType).filter(DefectType.code == code).first()
    if not defect_type:
        raise HTTPException(status_code=404, detail="缺陷类型不存在")
    
    return defect_type