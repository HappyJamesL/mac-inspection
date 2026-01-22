"""缺陷相关路由"""
import json
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models.defect import Defect
from app.db.models.glasslayout import GlassLayout
from app.api.schemas.defect import (
    DefectSaveRequest, DefectSaveResponse, DefectQueryRequest, DefectQueryResponse
)
from app.utils.geometry import determine_panel, get_panel_polygons
from app.utils.security import verify_role

router = APIRouter()


@router.get("/glasses/{glassId}/defects", response_model=List[Dict])
async def get_defects_by_glass(
    glassId: str,
    processoperationname: Optional[str] = Query(None, description="工序站点名称"),
    db: Session = Depends(get_db)
):
    """根据GlassID和工序站点获取缺陷列表"""
    try:
        query = db.query(Defect).filter(Defect.productname == glassId)
        
        # 添加工序站点过滤条件
        if processoperationname:
            query = query.filter(Defect.processoperationname == processoperationname)
        
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
                "created_at": defect.created_at.isoformat() if defect.created_at else ""
            }
            
            result.append(defect_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缺陷列表失败: {str(e)}")


@router.get("/lots/{lotname}/defects", response_model=List[Dict])
async def get_defects_by_lot(
    lotname: str,
    processoperationname: Optional[str] = Query(None, description="工序站点名称"),
    db: Session = Depends(get_db)
):
    """根据Lot名称和工序站点获取该批次下所有Glass的缺陷列表"""
    try:
        query = db.query(Defect).filter(Defect.lotname == lotname)
        
        # 添加工序站点过滤条件
        if processoperationname:
            query = query.filter(Defect.processoperationname == processoperationname)
        
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
                "created_at": defect.created_at.isoformat() if defect.created_at else ""
            }
            
            result.append(defect_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Lot缺陷列表失败: {str(e)}")


@router.post("/defect/save", response_model=DefectSaveResponse, status_code=status.HTTP_201_CREATED)
async def save_defect(
    defect_data: DefectSaveRequest,
    db: Session = Depends(get_db)
):
    """保存缺陷记录，包含几何碰撞检测"""
    try:
        # 特殊处理：对于"正常"缺陷代码，跳过panel验证
        if defect_data.defect_code == "正常":
            panel_id = ""  # 设置为空字符串，表示不需要panel
        else:
            # 对于线缺、面缺等类型，无论前端是否提供panel_id，都要进行碰撞检测
            # 确保记录所有碰撞到的panel
            panel_id = defect_data.panel_id
            defect_type_lower = defect_data.defect_type.lower()
            
            # 强制碰撞检测的缺陷类型
            force_detection_types = ['line', 'curve', 'area', 'region']
            
            # 确保geom_data是有效的列表
            valid_geom_data = False
            if defect_data.geom_data and isinstance(defect_data.geom_data, list) and len(defect_data.geom_data) > 0:
                # 检查第一个点是否有效
                first_point = defect_data.geom_data[0]
                if (isinstance(first_point, list) and len(first_point) >= 2) or \
                   (isinstance(first_point, dict) and 'x' in first_point and 'y' in first_point):
                    valid_geom_data = True
            
            # 只有当有有效的geom_data或者是强制检测类型时，才进行碰撞检测
            if (not panel_id and valid_geom_data) or (defect_type_lower in force_detection_types):
                # 查询该产品的所有panel坐标
                panels = db.query(GlassLayout).filter(
                    GlassLayout.tft_product == defect_data.product_id
                ).all()
                
                if not panels:
                    raise HTTPException(status_code=404, detail=f"未找到产品 {defect_data.product_id} 的布局信息")
                
                # 转换panel数据为几何计算所需格式
                panel_list = []
                for panel in panels:
                    panel_list.append({
                        'panel_id': str(panel.id),
                        'x_left_up': panel.x_left_up,
                        'y_left_up': panel.y_left_up,
                        'x_right_up': panel.x_right_up,
                        'y_right_up': panel.y_right_up,
                        'x_right_down': panel.x_right_down,
                        'y_right_down': panel.y_right_down,
                        'x_left_down': panel.x_left_down,
                        'y_left_down': panel.y_left_down
                    })
                
                # 创建panel多边形
                panel_polygons = get_panel_polygons(panel_list)
                
                # 构建坐标信息 - 根据缺陷类型传递不同格式的坐标
                coordinates = {'x': 0, 'y': 0}
                
                if defect_type_lower in ['point'] and valid_geom_data:
                    # 点缺陷：使用geom_data中的第一个点
                    first_point = defect_data.geom_data[0]
                    if isinstance(first_point, list) and len(first_point) >= 2:
                        coordinates = {
                            'x': first_point[0],
                            'y': first_point[1]
                        }
                    elif isinstance(first_point, dict) and 'x' in first_point and 'y' in first_point:
                        coordinates = {
                            'x': first_point['x'],
                            'y': first_point['y']
                        }
                elif defect_type_lower in ['line', 'curve', 'area', 'region'] and valid_geom_data:
                    # 线缺陷、曲线缺陷、面缺陷：传递完整的geom_data坐标列表
                    coordinates = defect_data.geom_data
                
                # 判定缺陷所属panel
                panel_id = determine_panel(
                    defect_data.defect_type,
                    coordinates,
                    panel_polygons
                )
                
                # 如果没有找到panel，尝试使用点缺陷的处理方式作为备选
                if not panel_id and valid_geom_data:
                    # 尝试从geom_data中获取第一个点，作为点缺陷处理
                    first_point = defect_data.geom_data[0]
                    if isinstance(first_point, list) and len(first_point) >= 2:
                        point_coords = {
                            'x': first_point[0],
                            'y': first_point[1]
                        }
                        panel_id = determine_panel(
                            'point',
                            point_coords,
                            panel_polygons
                        )
                
                # 如果仍然没有找到panel，抛出异常
                if not panel_id:
                    raise HTTPException(status_code=400, detail="缺陷坐标不在任何panel内")
        
        # 坐标转换：将微米坐标转换为毫米整数（除以1000并四舍五入）
        def convert_coordinates_to_mm(coords):
            """将微米坐标转换为毫米整数
            
            Args:
                coords: 微米坐标列表，格式为[[x1,y1], [x2,y2], ...]
            
            Returns:
                list: 毫米整数坐标列表，格式为[[x1,y1], [x2,y2], ...]
            """
            if not coords or not isinstance(coords, list):
                return coords
            
            converted = []
            for point in coords:
                if isinstance(point, list) and len(point) >= 2:
                    # 将微米转换为毫米，四舍五入到整数
                    x_mm = round(point[0] / 1000)
                    y_mm = round(point[1] / 1000)
                    converted.append([x_mm, y_mm])
                else:
                    converted.append(point)
            return converted
        
        # 处理geom_data
        geom_data_json = "[]"  # 默认值为空数组的JSON字符串，避免为NULL
        if defect_data.geom_data:
            # 转换坐标为毫米整数
            geom_data_mm = convert_coordinates_to_mm(defect_data.geom_data)
            geom_data_json = json.dumps(geom_data_mm)
        
        # 计算panel_count
        panel_count = 0
        if panel_id:
            panel_count = len(panel_id.split(','))
        
        # 创建新缺陷记录
        db_defect = Defect(
            uuid=defect_data.uuid,
            productname=defect_data.glass_id or 'unknown',
            lotname=defect_data.lotname,
            productrequestname=defect_data.productrequestname,
            productspecname=defect_data.product_id,
            defect_code=defect_data.defect_code,
            defect_type=defect_data.defect_type,
            panel_id=panel_id,
            panel_count=str(panel_count),
            geom_data=geom_data_json,
            is_symmetry=defect_data.is_symmetry,
            remarks=defect_data.remark,
            machinename=defect_data.machinename,
            operator_id=defect_data.operator_id,
            inspector=defect_data.inspector,
            processoperationname=defect_data.processoperationname,
            inspection_type=defect_data.inspection_type
        )

        
        # 检查是否已存在相同uuid的缺陷记录
        existing_defect = db.query(Defect).filter(Defect.uuid == defect_data.uuid).first()
        if existing_defect:
            # 更新现有记录
            for field, value in db_defect.__dict__.items():
                if field != '_sa_instance_state':
                    setattr(existing_defect, field, value)
            db.commit()
            db.refresh(existing_defect)
        else:
            # 保存新记录
            db.add(db_defect)
            db.commit()
            db.refresh(db_defect)
        
        return DefectSaveResponse(
            success=True,
            uuid=defect_data.uuid,
            panel_id=panel_id,
            message="缺陷保存成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存缺陷失败: {str(e)}")


@router.delete("/defect/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_defect(
    uuid: str,
    db: Session = Depends(get_db)
):
    """根据uuid删除缺陷记录"""
    try:
        # 查询缺陷记录
        defect = db.query(Defect).filter(Defect.uuid == uuid).first()
        if not defect:
            raise HTTPException(status_code=404, detail=f"未找到uuid为 {uuid} 的缺陷记录")
        
        # 删除缺陷记录
        db.delete(defect)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除缺陷记录失败: {str(e)}")


@router.post("/defects/query", response_model=DefectQueryResponse)
async def query_defects(
    query_params: DefectQueryRequest,
    db: Session = Depends(get_db)
):
    """缺陷查询面板接口"""
    try:
        # 构建查询
        query = db.query(Defect)
        
        # 添加过滤条件
        if query_params.glass_id:
            query = query.filter(Defect.productname == query_params.glass_id)
        if query_params.lotname:
            query = query.filter(Defect.lotname == query_params.lotname)
        if query_params.productrequestname:
            query = query.filter(Defect.productrequestname == query_params.productrequestname)
        if query_params.product_id:
            query = query.filter(Defect.productspecname == query_params.product_id)
        if query_params.defect_code:
            query = query.filter(Defect.defect_code == query_params.defect_code)
        if query_params.defect_type:
            query = query.filter(Defect.defect_type == query_params.defect_type)
        if query_params.start_time:
            query = query.filter(Defect.created_at >= query_params.start_time)
        if query_params.end_time:
            query = query.filter(Defect.created_at <= query_params.end_time)
        if query_params.panel_id:
            query = query.filter(Defect.panel_id == query_params.panel_id)
        if query_params.is_symmetry:
            query = query.filter(Defect.is_symmetry == query_params.is_symmetry)
        
        # 获取总记录数
        total = query.count()
        
        # 分页查询
        defects = query.offset(query_params.skip).limit(query_params.limit).all()
        
        # 构建缺陷列表响应
        defect_list = []
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
                "lotname": defect.lotname or "",
                "productspecname": defect.productspecname or "",
                "defect_type": defect.defect_type or "",  # 保留原字段名，兼容旧版本
                "type": defect.defect_type or "",  # 前端期望的字段名
                "panel_count": defect.panel_count or "0",
                "is_symmetry": defect.is_symmetry or "N",  # 保留原字段名，兼容旧版本
                "isSymmetry": defect.is_symmetry == "Y",  # 前端期望的字段名（布尔值）
                "machinename": defect.machinename or "",
                "inspection_type": defect.inspection_type or "首检",
                "created_at": defect.created_at.isoformat() if defect.created_at else ""
            }

            
            defect_list.append(defect_dict)
        
        return DefectQueryResponse(
            total=total,
            defects=defect_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询缺陷失败: {str(e)}")