"""历史数据查询路由"""
import json
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import distinct

from app.db.historical_db import get_historical_db
from app.db.models.defect import Defect
from app.db.models.glasslayout import GlassLayout
from app.db.models.d_mask_spec import DMaskSpec

router = APIRouter()


def get_default_time_range():
    """获取默认时间范围：前一天8:30到今天8:30"""
    now = datetime.now()
    
    # 今天8:30
    today_830 = datetime(now.year, now.month, now.day, 8, 30, 0)
    
    # 前一天8:30
    yesterday_830 = today_830 - timedelta(days=1)
    
    return yesterday_830, today_830

@router.get("/glasses", response_model=List[Dict])
async def get_historical_glasses(
    start_time: datetime = Query(None, description="开始时间，格式：YYYY-MM-DD HH:MM:SS"),
    end_time: datetime = Query(None, description="结束时间，格式：YYYY-MM-DD HH:MM:SS"),
    productname: Optional[str] = Query(None, description="产品名称（GlassID）"),
    products: Optional[str] = Query(None, description="产品型号名称，支持多选，逗号分隔"),
    workOrders: Optional[str] = Query(None, description="工单号，支持多选，逗号分隔"),
    lots: Optional[str] = Query(None, description="生产批次LOT名称，支持多选，逗号分隔"),
    operations: Optional[str] = Query(None, description="工序站点名称，支持多选，逗号分隔"),
    inspection_type: Optional[str] = Query(None, description="检测类型，支持多选，逗号分隔"),
    inspector: Optional[str] = Query(None, description="检测人员，支持多选，逗号分隔"),
    machinename: Optional[str] = Query(None, description="机器名称，支持多选，逗号分隔"),
    defect_code: Optional[str] = Query(None, description="缺陷代码，支持多选，逗号分隔"),
    db: Session = Depends(get_historical_db)
):
    """获取历史玻璃列表，按产品型号和站点分组"""
    try:
        # 设置默认时间范围
        if not start_time or not end_time:
            start_time, end_time = get_default_time_range()
        
        # 构建查询，获取所有匹配的记录
        query = db.query(Defect.productname, Defect.productspecname, Defect.processoperationname).distinct()
        
        # 时间范围过滤
        query = query.filter(Defect.created_at >= start_time, Defect.created_at <= end_time)
        
        # 产品名称过滤
        if productname:
            query = query.filter(Defect.productname == productname)
        
        # 辅助函数：将逗号分隔的字符串转换为列表
        def str_to_list(s):
            if not s:
                return []
            return [item.strip() for item in s.split(',') if item.strip()]
        
        # 产品型号过滤
        if products:
            product_list = str_to_list(products)
            if product_list:
                query = query.filter(Defect.productspecname.in_(product_list))
        
        # 工单过滤
        if workOrders:
            work_order_list = str_to_list(workOrders)
            if work_order_list:
                query = query.filter(Defect.productrequestname.in_(work_order_list))
        
        # LOT过滤
        if lots:
            lot_list = str_to_list(lots)
            if lot_list:
                query = query.filter(Defect.lotname.in_(lot_list))
        
        # 站点过滤
        if operations:
            operation_list = str_to_list(operations)
            if operation_list:
                query = query.filter(Defect.processoperationname.in_(operation_list))
        
        # 检测类型过滤
        if inspection_type:
            inspection_type_list = str_to_list(inspection_type)
            if inspection_type_list:
                query = query.filter(Defect.inspection_type.in_(inspection_type_list))
        
        # 检测人员过滤
        if inspector:
            inspector_list = str_to_list(inspector)
            if inspector_list:
                # 处理多个检测人员的情况，使用like查询
                for insp in inspector_list:
                    query = query.filter(Defect.inspector.like(f"%{insp}%"))
        
        # 机器名称过滤
        if machinename:
            machinename_list = str_to_list(machinename)
            if machinename_list:
                query = query.filter(Defect.machinename.in_(machinename_list))
        
        # 缺陷代码过滤
        if defect_code:
            defect_code_list = str_to_list(defect_code)
            if defect_code_list:
                query = query.filter(Defect.defect_code.in_(defect_code_list))
        
        # 执行查询
        glasses = query.all()
        
        # 按产品型号和站点分组
        product_map = {}
        for glass in glasses:
            product_key = f"{glass[1]}-{glass[2] if glass[2] else 'unknown'}"  # 使用产品型号+站点作为分组键
            if product_key not in product_map:
                product_map[product_key] = {
                    "product": glass[1],
                    "processoperationname": glass[2] if glass[2] else "unknown",
                    "glassid": []
                }
            product_map[product_key]["glassid"].append(glass[0])
        
        # 构建响应数据
        result = list(product_map.values())
        
        return result
    except Exception as e:
        # 返回详细的错误信息
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{productspecname}/layout", response_model=Dict)
async def get_historical_product_layout(
    productspecname: str,
    db: Session = Depends(get_historical_db)
):
    """获取历史产品布局信息，包括panel坐标和mask规则"""
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


@router.get("/glasses/{glassId}/defects", response_model=List[Dict])
async def get_historical_defects_by_glass_id(
    glassId: str,
    processoperationname: Optional[str] = Query(None, description="工序站点名称，支持多选，逗号分隔"),
    start_time: datetime = Query(..., description="开始时间，格式：YYYY-MM-DD HH:MM:SS"),
    end_time: datetime = Query(..., description="结束时间，格式：YYYY-MM-DD HH:MM:SS"),
    machinename: Optional[str] = Query(None, description="机器名称，支持多选，逗号分隔"),
    defect_code: Optional[str] = Query(None, description="缺陷代码，支持多选，逗号分隔"),
    db: Session = Depends(get_historical_db)
):
    """根据GlassID、工序站点和时间范围获取历史缺陷列表"""
    try:
        # 构建查询
        query = db.query(Defect).filter(
            Defect.productname == glassId,
            Defect.created_at >= start_time,
            Defect.created_at <= end_time
        )
        
        # 辅助函数：将逗号分隔的字符串转换为列表
        def str_to_list(s):
            if not s:
                return []
            return [item.strip() for item in s.split(',') if item.strip()]
        
        # 添加工序站点过滤条件
        if processoperationname:
            operation_list = str_to_list(processoperationname)
            if operation_list:
                query = query.filter(Defect.processoperationname.in_(operation_list))
        
        # 添加机器名称过滤条件
        if machinename:
            machine_list = str_to_list(machinename)
            if machine_list:
                query = query.filter(Defect.machinename.in_(machine_list))
        
        # 添加缺陷代码过滤条件
        if defect_code:
            defect_code_list = str_to_list(defect_code)
            if defect_code_list:
                query = query.filter(Defect.defect_code.in_(defect_code_list))
        
        defects = query.all()
        # 构建响应数据
        result = []
        for defect in defects:
            # 坐标转换：将毫米整数转换为微米（乘以1000）
            def convert_coordinates_to_um(coords):
                """将毫米整数坐标转换为微米
                
                Args:
                    coords: 毫米整数坐标列表，格式为[[x1,y1], [x2,y2], ...]
                
                Returns:
                    list: 微米坐标列表，格式为[[x1,y1], [x2,y2], ...]
                """
                if not coords or not isinstance(coords, list):
                    return []
                
                converted = []
                for point in coords:
                    if isinstance(point, list) and len(point) >= 2:
                        try:
                            # 确保坐标是数字类型
                            x_mm = float(point[0])
                            y_mm = float(point[1])
                            # 将毫米转换为微米，转换为整数
                            x_um = int(x_mm * 1000)
                            y_um = int(y_mm * 1000)
                            converted.append([x_um, y_um])
                        except (ValueError, TypeError):
                            # 跳过无效的点
                            continue
                    else:
                        # 跳过无效的点
                        continue
                return converted
            
            # 处理geom_data
            geom_data = []
            if defect.geom_data:
                try:
                    parsed_geom = json.loads(defect.geom_data)
                    geom_data = convert_coordinates_to_um(parsed_geom)
                except (json.JSONDecodeError, TypeError):
                    geom_data = []
            
            # 将geom_data转换为前端期望的path格式 [{x, y}, {x, y}, ...]
            path = []
            for point in geom_data:
                path.append({
                    "x": point[0],
                    "y": point[1]
                })
            
            # 提取x和y坐标（使用第一个点的坐标）
            x = path[0]["x"] if path else None
            y = path[0]["y"] if path else None
            
            # 将panel_id字符串转换为panelIds数组
            panelIds = []
            if defect.panel_id:
                panelIds = [id.strip() for id in defect.panel_id.split(",") if id.strip()]
            
            # 构建前端期望格式的数据
                defect_dict = {
                    "uid": defect.uuid or "",
                    "uuid": defect.uuid or "",
                    "productrequestname": defect.productrequestname or "",
                    "code": defect.defect_code or "",  # 前端期望的字段名
                    "codeName": defect.defect_code or "",  # 前端期望的字段名
                    "panel_id": defect.panel_id or "",  # 保留原字段名，兼容旧版本
                    "panelIds": panelIds,  # 前端期望的字段名（数组）
                    "geom_data": geom_data,  # 保留原字段名，兼容旧版本
                    "path": path,  # 前端期望的字段名
                    "x": x,  # 前端期望的字段名
                    "y": y,  # 前端期望的字段名
                    "remarks": defect.remarks or "",  # 保留原字段名，兼容旧版本
                    "remark": defect.remarks or "",  # 前端期望的字段名
                    "operator_id": defect.operator_id or "",
                    "productname": defect.productname or "",
                    "glassId": defect.productname or "",  # 新增：glassId字段，便于前端按glass分组
                    "lotname": defect.lotname or "",
                    "productspecname": defect.productspecname or "",
                    "defect_type": defect.defect_type or "",  # 保留原字段名，兼容旧版本
                    "type": defect.defect_type or "",  # 前端期望的字段名
                    "panel_count": defect.panel_count or "0",
                    "is_symmetry": defect.is_symmetry or "N",  # 保留原字段名，兼容旧版本
                    "isSymmetry": defect.is_symmetry == "Y",  # 前端期望的字段名（布尔值）
                    "machinename": defect.machinename or "",
                    "processoperationname": defect.processoperationname or "",
                    "inspection_type": defect.inspection_type or "首检",
                    "Inspector": defect.inspector or "-",
                    "created_at": defect.created_at.isoformat() if defect.created_at else ""
                }
            
            result.append(defect_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史缺陷列表失败: {str(e)}")


@router.get("/options", response_model=Dict)
async def get_historical_query_options(
    start_time: datetime = Query(None, description="开始时间，格式：YYYY-MM-DD HH:MM:SS"),
    end_time: datetime = Query(None, description="结束时间，格式：YYYY-MM-DD HH:MM:SS"),
    db: Session = Depends(get_historical_db)
):
    """获取历史查询的可选参数列表"""
    # 设置默认时间范围
    if not start_time or not end_time:
        start_time, end_time = get_default_time_range()
    
    # 获取可选参数列表
    productspecnames = db.query(distinct(Defect.productspecname)).filter(
        Defect.created_at >= start_time,
        Defect.created_at <= end_time
    ).all()
    
    productrequestnames = db.query(distinct(Defect.productrequestname)).filter(
        Defect.created_at >= start_time,
        Defect.created_at <= end_time
    ).all()
    
    lotnames = db.query(distinct(Defect.lotname)).filter(
        Defect.created_at >= start_time,
        Defect.created_at <= end_time
    ).all()
    
    processoperationnames = db.query(distinct(Defect.processoperationname)).filter(
        Defect.created_at >= start_time,
        Defect.created_at <= end_time
    ).all()
    
    inspection_types = db.query(distinct(Defect.inspection_type)).filter(
        Defect.created_at >= start_time,
        Defect.created_at <= end_time
    ).all()
    
    # 查询机器名称
    machinenames = db.query(distinct(Defect.machinename)).filter(
        Defect.created_at >= start_time,
        Defect.created_at <= end_time
    ).all()
    
    # 查询缺陷代码
    defect_codes = db.query(distinct(Defect.defect_code)).filter(
        Defect.created_at >= start_time,
        Defect.created_at <= end_time
    ).all()
    
    # 构建响应数据
    result = {
        "productspecnames": [item[0] for item in productspecnames if item[0]],
        "productrequestnames": [item[0] for item in productrequestnames if item[0]],
        "lotnames": [item[0] for item in lotnames if item[0]],
        "processoperationnames": [item[0] for item in processoperationnames if item[0]],
        "inspection_types": [item[0] for item in inspection_types if item[0]],
        "machinenames": [item[0] for item in machinenames if item[0]],
        "defect_codes": [item[0] for item in defect_codes if item[0]]
    }
    
    return result


@router.get("/test-connection")
async def test_historical_db_connection(db: Session = Depends(get_historical_db)):
    """测试历史数据库连接"""
    try:
        # 执行一个简单的查询来测试连接
        # 尝试查询第一个缺陷记录
        test_query = db.query(Defect).first()
        
        # 如果查询成功，返回连接成功信息
        return {
            "status": "success",
            "message": "历史数据库连接正常",
            "test_result": "查询成功" if test_query else "连接成功但无数据"
        }
    except Exception as e:
        # 如果连接失败，返回详细的错误信息
        return {
            "status": "error",
            "message": "历史数据库连接失败",
            "error_detail": str(e)
        }
