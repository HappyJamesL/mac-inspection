"""批次相关路由"""
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import distinct

from app.db.base import get_db
from app.db.models.lot import Lot
from app.db.models.glass import Glass
from app.db.models.defect import Defect

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


@router.get("/{lotname}/process-operations", response_model=Dict[str, List[str]])
async def get_process_operations_by_lot(
    lotname: str,
    db: Session = Depends(get_db)
):
    """根据批次名称获取该批次下所有缺陷记录的工序站点、工单、产品型号、Glass列表、设备名称、操作员列表"""
    try:
        from sqlalchemy import text
        
        # 使用原生 SQL 查询
        process_operations = db.execute(text("""
            SELECT DISTINCT PROCESSOPERATIONNAME 
            FROM MAC_DEFECT_RECORDS 
            WHERE LOTNAME = :lotname 
            AND PROCESSOPERATIONNAME IS NOT NULL
        """), {"lotname": lotname}).fetchall()
        
        product_requests = db.execute(text("""
            SELECT DISTINCT PRODUCTREQUESTNAME 
            FROM MAC_DEFECT_RECORDS 
            WHERE LOTNAME = :lotname 
            AND PRODUCTREQUESTNAME IS NOT NULL
        """), {"lotname": lotname}).fetchall()
        
        product_specs = db.execute(text("""
            SELECT DISTINCT PRODUCTSPECNAME 
            FROM MAC_DEFECT_RECORDS 
            WHERE LOTNAME = :lotname 
            AND PRODUCTSPECNAME IS NOT NULL
        """), {"lotname": lotname}).fetchall()
        
        glasses = db.execute(text("""
            SELECT DISTINCT PRODUCTNAME 
            FROM MAC_DEFECT_RECORDS 
            WHERE LOTNAME = :lotname 
            AND PRODUCTNAME IS NOT NULL
        """), {"lotname": lotname}).fetchall()
        
        machines = db.execute(text("""
            SELECT DISTINCT MACHINENAME 
            FROM MAC_DEFECT_RECORDS 
            WHERE LOTNAME = :lotname 
            AND MACHINENAME IS NOT NULL
        """), {"lotname": lotname}).fetchall()
        
        operators = db.execute(text("""
            SELECT DISTINCT OPERATOR_ID 
            FROM MAC_DEFECT_RECORDS 
            WHERE LOTNAME = :lotname 
            AND OPERATOR_ID IS NOT NULL
        """), {"lotname": lotname}).fetchall()
        
        process_operations_list = sorted([row[0] for row in process_operations if row[0]])
        product_requests_list = sorted([row[0] for row in product_requests if row[0]])
        product_specs_list = sorted([row[0] for row in product_specs if row[0]])
        glasses_list = sorted([row[0] for row in glasses if row[0]])
        machines_list = sorted([row[0] for row in machines if row[0]])
        operators_list = sorted([row[0] for row in operators if row[0]])
        
        return {
            "processOperations": process_operations_list,
            "productRequests": product_requests_list,
            "productSpecs": product_specs_list,
            "glasses": glasses_list,
            "machines": machines_list,
            "operators": operators_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工序站点列表失败: {str(e)}")