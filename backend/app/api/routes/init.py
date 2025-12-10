"""初始化数据路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, Table, MetaData, text
from typing import Dict, List, Optional

from app.db.base import get_db, engine
from app.db.models.defect_type import DefectType

router = APIRouter()


@router.get("/init-data", response_model=Dict)
async def get_init_data(
    db: Session = Depends(get_db)
):
    """获取初始化数据，返回前端下拉框所需的配置信息"""
    try:
        # 使用直接SQL查询获取设备列表，避免表反射问题
        equipments_stmt = text("""
        SELECT MACHINENAME 
        FROM MACHINESPEC 
        WHERE DETAILMACHINETYPE = 'Main' 
        AND MACHINEGROUPNAME IN ('MAC', 'MM')
        """)
        equipments_result = db.execute(equipments_stmt).fetchall()
        equipments = [e[0] for e in equipments_result]
        
        # 获取Lot和CST数据，使用JOIN查询，修正表名大小写
        lot_cst_stmt = text("""
        SELECT l.LOTNAME, l.CARRIERNAME 
        FROM LOT l 
        JOIN PROCESSOPERATIONSPEC p ON l.PROCESSOPERATIONNAME = p.PROCESSOPERATIONNAME  
        WHERE p.DESCRIPTION LIKE '%MAC%' 
        AND l.CARRIERNAME IS NOT NULL
        """)
        lot_cst_result = db.execute(lot_cst_stmt).fetchall()
        
        # 提取lot和cst数据，去重
        lot_ids = list(set([row[0] for row in lot_cst_result if row[0]]))
        cst_ids = list(set([row[1] for row in lot_cst_result if row[1]]))
        
        return {
            "lot_ids": lot_ids,
            "cst_ids": cst_ids,
            "equipments": equipments
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取初始化数据失败: {str(e)}")


@router.get("/related-info", response_model=Dict)
async def get_related_info(
    cst: Optional[str] = None,
    lot: Optional[str] = None,
    WorkOrder: Optional[str] = None,
    Product: Optional[str] = None,
    OPER: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """根据传入的参数获取相关信息，返回lot表中的特定字段"""
    try:
        # 构建动态查询条件
        where_clauses = []
        params = {}
        
        if cst:
            where_clauses.append("CARRIERNAME = :cst")
            params["cst"] = cst
        if lot:
            where_clauses.append("LOTNAME = :lot")
            params["lot"] = lot
        if WorkOrder:
            where_clauses.append("PRODUCTREQUESTNAME = :WorkOrder")
            params["WorkOrder"] = WorkOrder
        if Product:
            where_clauses.append("PRODUCTSPECNAME = :Product")
            params["Product"] = Product
        if OPER:
            where_clauses.append("PROCESSOPERATIONNAME = :OPER")
            params["OPER"] = OPER
        
        # 构建WHERE子句
        where_sql = """
        WHERE """ + " AND ".join(where_clauses) if where_clauses else ""
        
        # 使用直接SQL查询获取相关信息
        stmt = text(f"""
        SELECT LOTNAME, CARRIERNAME, PRODUCTREQUESTNAME, PRODUCTSPECNAME, PROCESSOPERATIONNAME
        FROM LOT
        {where_sql}
        """)
        
        # 执行查询
        related_lots = db.execute(stmt, params).fetchall()
        
        # 如果没有找到相关记录，返回空数据
        if not related_lots:
            return {
                "processOperationName": "",
                "productrequestname": "",
                "product": "",
                "cst": "",
                "lot": "",
                "processOperations": [],
                "productrequestnames": [],
                "products": []
            }
        
        # 构建返回数据，只返回第一条记录的具体信息
        first_lot = related_lots[0]
        
        # 获取所有相关的可选值
        # 构建用于获取可选值的查询，不使用WorkOrder、Product和OPER进行过滤
        options_where_clauses = []
        options_params = {}
        
        if cst:
            options_where_clauses.append("CARRIERNAME = :cst")
            options_params["cst"] = cst
        if lot:
            options_where_clauses.append("LOTNAME = :lot")
            options_params["lot"] = lot
        
        options_where_sql = """
        WHERE """ + " AND ".join(options_where_clauses) if options_where_clauses else ""
        
        options_stmt = text(f"""
        SELECT LOTNAME, CARRIERNAME, PRODUCTREQUESTNAME, PRODUCTSPECNAME, PROCESSOPERATIONNAME
        FROM LOT
        {options_where_sql}
        """)
        
        # 执行查询获取所有相关记录
        all_related_lots = db.execute(options_stmt, options_params).fetchall()
        
        # 提取唯一值作为可选选项 - 使用索引访问，避免列名大小写问题
        process_operations = list(set(row[4] for row in all_related_lots if row[4]))
        productrequestnames = list(set(row[2] for row in all_related_lots if row[2]))
        products = list(set(row[3] for row in all_related_lots if row[3]))
        
        return {
            "processOperationName": first_lot[4] or "",
            "productrequestname": first_lot[2] or "",
            "product": first_lot[3] or "",
            "cst": first_lot[1] or "",
            "lot": first_lot[0] or "",
            "processOperations": process_operations,
            "productrequestnames": productrequestnames,
            "products": products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取相关信息失败: {str(e)}")


@router.get("/filter-options", response_model=Dict)
async def filter_options(
    oper: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """根据传入的OPER参数过滤选项，返回可用的选项列表"""
    try:
        # 构建动态查询条件
        where_clauses = []
        params = {}
        
        if oper:
            where_clauses.append("PROCESSOPERATIONNAME = :oper")
            params["oper"] = oper
        
        # 构建WHERE子句
        where_sql = """
        WHERE """ + " AND ".join(where_clauses) if where_clauses else ""
        
        # 使用直接SQL查询，修正表名大小写，只选择需要的字段
        stmt = text(f"""
        SELECT LOTNAME, CARRIERNAME, PRODUCTREQUESTNAME, PRODUCTSPECNAME, PROCESSOPERATIONNAME
        FROM LOT
        {where_sql}
        """)
        
        # 执行查询
        filtered_lots = db.execute(stmt, params).fetchall()
        
        # 如果没有找到相关记录，返回空数组
        if not filtered_lots:
            return {
                "cst": [],
                "lots": [],
                "productrequestnames": [],
                "products": []
            }
        
        # 提取唯一值作为可选选项 - 使用索引访问，避免列名大小写问题
        cst_list = list(set(row[1] for row in filtered_lots if row[1]))
        lot_list = list(set(row[0] for row in filtered_lots if row[0]))
        productrequestnames_list = list(set(row[2] for row in filtered_lots if row[2]))
        products_list = list(set(row[3] for row in filtered_lots if row[3]))
        
        return {
            "cst": cst_list,
            "lots": lot_list,
            "productrequestnames": productrequestnames_list,
            "products": products_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"过滤选项失败: {str(e)}")


@router.get("/reasoncode", response_model=List[Dict])
async def get_reasoncodes(
    db: Session = Depends(get_db)
):
    """获取缺陷代码信息，返回REASONCODE表数据"""
    try:
        # 查询所有缺陷类型信息，添加REASONCODETYPE条件
        defect_types = db.query(DefectType).filter(DefectType.reasoncodetype == 'GLASSCODE').all()
        
        # 构建返回数据，移除EQTYPE字段
        result = []
        for dt in defect_types:
            result.append({
                "CODE": dt.code,
                "DESCREPTION": dt.description,
                "CODETYPE": dt.codetype,
                "COLOR": dt.color,
                "LEVELNO": dt.levelno
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缺陷代码信息失败: {str(e)}")
