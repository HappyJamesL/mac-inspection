"""几何计算工具模块"""
from shapely.geometry import Point, Polygon, LineString
from typing import List, Dict, Optional, Any


def create_panel_polygon(panel: Dict) -> Polygon:
    """根据panel的坐标创建Polygon对象
    
    Args:
        panel: 包含panel坐标的字典，格式为{
            'x_left_up': int, 'y_left_up': int,
            'x_right_up': int, 'y_right_up': int,
            'x_right_down': int, 'y_right_down': int,
            'x_left_down': int, 'y_left_down': int
        }
    
    Returns:
        Polygon对象: 表示panel的多边形
    """
    # 按照顺时针顺序排列顶点：左上 -> 右上 -> 右下 -> 左下 -> 左上
    coordinates = [
        (panel['x_left_up'], panel['y_left_up']),
        (panel['x_right_up'], panel['y_right_up']),
        (panel['x_right_down'], panel['y_right_down']),
        (panel['x_left_down'], panel['y_left_down']),
        (panel['x_left_up'], panel['y_left_up'])  # 闭合多边形
    ]
    return Polygon(coordinates)


def get_panel_polygons(panels: List[Dict]) -> List[Dict]:
    """为所有panel创建Polygon对象
    
    Args:
        panels: panel列表，每个panel包含坐标信息
    
    Returns:
        List[Dict]: 包含panel_id和polygon对象的字典列表
    """
    panel_polygons = []
    for panel in panels:
        polygon = create_panel_polygon(panel)
        panel_polygons.append({
            'panel_id': panel['panel_id'],
            'polygon': polygon
        })
    return panel_polygons


def determine_panel_for_point(
    x: int, 
    y: int, 
    panel_polygons: List[Dict]
) -> Optional[str]:
    """判断点(x,y)属于哪个panel
    
    Args:
        x: 点的X坐标（微米）
        y: 点的Y坐标（微米）
        panel_polygons: 包含panel_id和polygon对象的字典列表
    
    Returns:
        Optional[str]: 所属panel的ID，如果不在任何panel内则返回None
    """
    point = Point(x, y)
    for panel in panel_polygons:
        if point.within(panel['polygon']):
            return panel['panel_id']
    return None


def determine_panel_for_line(
    line_coords: List[List[int]], 
    panel_polygons: List[Dict]
) -> Optional[str]:
    """判断线段与哪些panel相交
    
    Args:
        line_coords: 线段的坐标列表，格式为[[x1,y1], [x2,y2]]
        panel_polygons: 包含panel_id和polygon对象的字典列表
    
    Returns:
        Optional[str]: 相交的panel ID，多个ID用逗号分隔；如果与任何panel不相交则返回None
    """
    line = LineString(line_coords)
    intersecting_panels = []
    for panel in panel_polygons:
        if line.intersects(panel['polygon']):
            intersecting_panels.append(panel['panel_id'])
    
    if intersecting_panels:
        return ','.join(intersecting_panels)
    return None


def determine_panel_for_region(
    region_coords: List[List[int]], 
    panel_polygons: List[Dict]
) -> Optional[str]:
    """判断区域与哪些panel相交
    
    Args:
        region_coords: 区域的坐标列表，格式为[[x1,y1], [x2,y2], ..., [xn,yn]]
        panel_polygons: 包含panel_id和polygon对象的字典列表
    
    Returns:
        Optional[str]: 相交的panel ID，多个ID用逗号分隔；如果与任何panel不相交则返回None
    """
    # 确保区域是闭合的
    if region_coords[0] != region_coords[-1]:
        region_coords.append(region_coords[0])
    
    region = Polygon(region_coords)
    intersecting_panels = []
    for panel in panel_polygons:
        if region.intersects(panel['polygon']):
            intersecting_panels.append(panel['panel_id'])
    
    if intersecting_panels:
        return ','.join(intersecting_panels)
    return None


def determine_panel(
    defect_type: str, 
    coordinates: Any, 
    panel_polygons: List[Dict]
) -> Optional[str]:
    """根据缺陷类型和坐标判断所属panel
    
    Args:
        defect_type: 缺陷类型，支持POINT、LINE、REGION、area、point、line、curve、region等各种大小写形式
        coordinates: 缺陷坐标信息，格式根据缺陷类型不同而不同
            - POINT类型：{'x': int, 'y': int}
            - LINE类型：{'points': [[x1,y1], [x2,y2]]} 或直接传递坐标列表[[x1,y1], [x2,y2]]
            - REGION/area类型：{'points': [[x1,y1], [x2,y2], ..., [xn,yn]]} 或直接传递坐标列表[[x1,y1], [x2,y2], ..., [xn,yn]]
        panel_polygons: 包含panel_id和polygon对象的字典列表
    
    Returns:
        Optional[str]: 相交的panel ID，多个ID用逗号分隔；如果与任何panel不相交则返回None
    """
    defect_type_lower = defect_type.lower()
    
    if defect_type_lower == 'point':
        # POINT类型：coordinates = {'x': int, 'y': int}
        return determine_panel_for_point(
            coordinates['x'], 
            coordinates['y'], 
            panel_polygons
        )
    elif defect_type_lower in ['line', 'curve']:
        # LINE类型：支持两种格式
        if isinstance(coordinates, dict) and 'points' in coordinates:
            line_coords = coordinates['points']
        else:
            line_coords = coordinates
        return determine_panel_for_line(
            line_coords, 
            panel_polygons
        )
    elif defect_type_lower in ['region', 'area']:
        # REGION/area类型：支持两种格式
        if isinstance(coordinates, dict) and 'points' in coordinates:
            region_coords = coordinates['points']
        else:
            region_coords = coordinates
        return determine_panel_for_region(
            region_coords, 
            panel_polygons
        )
    else:
        return None
