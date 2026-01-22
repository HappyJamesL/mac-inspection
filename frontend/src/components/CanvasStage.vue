<template>
  <div class="relative bg-gray-800 flex items-center justify-center p-0 overflow-hidden select-none w-full h-full">
    <div id="canvas-wrapper" class="relative shadow-2xl bg-black border-2 border-gray-700 touch-none flex items-center justify-center" :style="wrapperStyle">
      <div class="absolute z-20 pointer-events-none" :style="{ left: currentScreenPos.x + 10 + 'px', top: currentScreenPos.y + 10 + 'px' }">
        <div class="bg-gray-900/80 backdrop-blur text-white px-4 py-1.5 rounded-full text-xs shadow-lg flex items-center space-x-3 border border-gray-700">
          <span class="font-mono text-yellow-400">X:{{ currentMousePos.x }} Y:{{ currentMousePos.y }}</span>
          <span v-if="drawingState.isDrawing" class="text-blue-400 ml-2">正在绘制...</span>
          <!-- <span class="text-gray-400 ml-2">Mask: {{ glassConfig.maskRule.full_shot === 'MAX' ? 'Reverse(S1@Max)' : 'Normal(S1@0)' }}</span> -->
        </div>
      </div>
      <div ref="stageContainer" class="w-full h-full"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import Konva from 'konva'
// 请确保路径正确
import { getProductLayout } from '../services/api'

// --- Props & Emits ---
const props = defineProps({
  selectedCode: { type: Object, default: null },
  currentDefects: { type: Array, default: () => [] },
  selectedProductId: { type: String, default: '' },
  defectCodes: { type: Array, default: () => [] },
  readonly: { type: Boolean, default: false },
  currentGlassId: { type: String, default: '' }
})

const emit = defineEmits(['add-defect', 'update-defects', 'layout-status-change'])

// --- 状态管理 ---
const stageContainer = ref(null)
const wrapperStyle = reactive({ width: '100%', height: '100%' })
const currentMousePos = reactive({ x: 0, y: 0 })
const currentScreenPos = reactive({ x: 0, y: 0 })
const loading = ref(false)

// 玻璃配置
const glassConfig = reactive({
  size: { w: 920000, h: 730000 },
  maskRule: { cover_x: 5, cover_y: 6, full_shot: 1 },
  panels: []
})

// 绘图状态机
const drawingState = reactive({
  isDrawing: false,
  points: [],
  tempLine: null
})

// Konva 全局对象
let stage, mainLayer, defectLayer, hintLayer
let scaleRatio = 1
let panels = []       // 存储带 Grid 坐标的 Panel 数据
let maskPositions = [] // 存储计算好的 Mask 物理位置

// 玻璃中心坐标 (用于物理坐标系转换)
let GLASS_CENTER_X = glassConfig.size.w / 2
let GLASS_CENTER_Y = glassConfig.size.h / 2

watch(() => [glassConfig.size.w, glassConfig.size.h], ([w, h]) => {
  GLASS_CENTER_X = w / 2
  GLASS_CENTER_Y = h / 2
}, { deep: true })


// ==========================================
// 核心算法类: SymmetryCalculator (融合版)
// ==========================================
class SymmetryCalculator {
  constructor(glassCols, glassRows, maskCols, maskRows, fullShot = 1) {
    this.gCols = glassCols;
    this.gRows = glassRows;
    this.mCols = maskCols;
    this.mRows = maskRows;
    this.fullShot = fullShot;
    
    this.shots = this.calculateShots();
  }

  /**
   * 单轴步进计算 (支持正向/逆向裁剪逻辑)
   */
  calculateAxisSteps(totalUnits, maskSize, isReverseAxis) {
    const steps = [];
    
    if (!isReverseAxis) {
      // --- 正向模式 (0 -> Total) ---
      // S1 在 0 处完整，末尾裁剪
      let cursor = 0;
      while (cursor < totalUnits) {
        let origin, validRange;
        if (cursor + maskSize <= totalUnits) {
          origin = cursor;
          validRange = { start: cursor, end: cursor + maskSize };
          cursor += maskSize;
        } else {
          // 空间不足，Origin回拉，Valid区间取后部
          origin = totalUnits - maskSize;
          validRange = { start: cursor, end: totalUnits };
          cursor = totalUnits;
        }
        steps.push({ origin, validRange });
      }
    } else {
      // --- 逆向模式 (Total -> 0) ---
      // S1 在 Total 处完整，0 端裁剪
      let cursor = totalUnits;
      while (cursor > 0) {
        let origin, validRange;
        if (cursor - maskSize >= 0) {
          origin = cursor - maskSize;
          validRange = { start: origin, end: cursor };
          cursor -= maskSize;
        } else {
          // 空间不足(0端)，Origin设为0，Valid区间取前部
          origin = 0;
          validRange = { start: 0, end: cursor };
          cursor = 0;
        }
        steps.push({ origin, validRange });
      }
    }
    return steps;
  }

  calculateShots() {
    // 根据 full_shot 决定 X/Y 轴的起始方向
    // 1: X=Min, Y=Min (左下)
    // 2: X=Min, Y=Max (左上)
    // 3: X=Max, Y=Max (右上)
    // 4: X=Max, Y=Min (右下)
    
    const xReverse = (this.fullShot === 3 || this.fullShot === 4);
    const yReverse = (this.fullShot === 2 || this.fullShot === 3);
    
    // 1. X轴步进
    const xSteps = this.calculateAxisSteps(this.gCols, this.mCols, xReverse);
    
    // 2. Y轴步进
    const ySteps = this.calculateAxisSteps(this.gRows, this.mRows, yReverse);

    const shots = [];
    let shotId = 0;
    
    // 3. 生成 S 型路径 (先 Y 轴步进,然后 X 轴步进)
    xSteps.forEach((xStep, xStepIndex) => {
      // 偶数步 Y保持方向; 奇数步 Y反向
      const isEvenStep = (xStepIndex % 2 === 0);
      const currentYSteps = isEvenStep ? [...ySteps] : [...ySteps].reverse();
      
      currentYSteps.forEach(yStep => {
        // 计算 Mask 内部的有效裁切范围 (用于对称点判断)
        // 相对坐标 = 绝对坐标 - Origin
        const validMaskX = {
          start: xStep.validRange.start - xStep.origin,
          end: xStep.validRange.end - xStep.origin
        };
        const validMaskY = {
          start: yStep.validRange.start - yStep.origin,
          end: yStep.validRange.end - yStep.origin
        };

        shots.push({
          id: shotId++,
          originCol: xStep.origin,
          originRow: yStep.origin,
          validMaskX,
          validMaskY,
          gridXRange: xStep.validRange,
          gridYRange: yStep.validRange
        });
      });
    });
    
    return shots;
  }

  getSymmetries(clickCol, clickRow) {
    // 1. 找源 Shot
    let sourceShot = null;
    let localX = 0, localY = 0;

    for (const shot of this.shots) {
      const lx = clickCol - shot.originCol;
      const ly = clickRow - shot.originRow;
      // 检查是否在 Mask 的有效窗口内
      if (lx >= shot.validMaskX.start && lx < shot.validMaskX.end &&
          ly >= shot.validMaskY.start && ly < shot.validMaskY.end) {
        sourceShot = shot;
        localX = lx;
        localY = ly;
        break; 
      }
    }

    if (!sourceShot) return [];
    const results = [];

    // 2. 映射到目标 Shot
    this.shots.forEach(targetShot => {
      if (targetShot.id === sourceShot.id) return;

      const targetLx = localX;
      const targetLy = localY;

      // 遮挡检查：点是否落在目标 Shot 的有效窗口内
      const isValidX = targetLx >= targetShot.validMaskX.start && targetLx < targetShot.validMaskX.end;
      const isValidY = targetLy >= targetShot.validMaskY.start && targetLy < targetShot.validMaskY.end;

      if (isValidX && isValidY) {
        results.push({
          col: targetShot.originCol + targetLx,
          row: targetShot.originRow + targetLy
        });
      }
    });

    return results;
  }
}


// ==========================================
// 辅助计算函数 (几何与布局)
// ==========================================

// 坐标转换 (Y轴翻转：屏幕Y向下，物理Y向上)
const toScreen = (val) => val * scaleRatio
const toScreenY = (val) => -val * scaleRatio
const toPhysical = (val) => val / scaleRatio
const toPhysicalY = (val) => -val / scaleRatio
const formatCoord = (val) => Math.round(val / 1000) // um -> mm

// 解析 Panel 布局，生成行列 Grid 信息 (修正版：使用坐标聚类消除间隙累积误差)
const analyzePanelLayout = (inputPanels) => {
  const targetPanels = inputPanels || panels || [];
  if (targetPanels.length === 0) return null;

  // 1. 计算所有 Panel 的几何中心
  // ---------------------------------------------------------
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  
  // 临时存储带有中心点的对象，避免重复计算
  const tempPanels = targetPanels.map(p => {
    let cx = 0, cy = 0;
    let pMinX = Infinity, pMaxX = -Infinity, pMinY = Infinity, pMaxY = -Infinity;
    
    p.points.forEach(pt => {
      cx += pt[0]; cy += pt[1];
      pMinX = Math.min(pMinX, pt[0]); pMaxX = Math.max(pMaxX, pt[0]);
      pMinY = Math.min(pMinY, pt[1]); pMaxY = Math.max(pMaxY, pt[1]);
    });
    
    cx /= p.points.length;
    cy /= p.points.length;
    
    // 更新全局边界
    p.points.forEach(pt => {
      if (pt[0] < minX) minX = pt[0];
      if (pt[0] > maxX) maxX = pt[0];
      if (pt[1] < minY) minY = pt[1];
      if (pt[1] > maxY) maxY = pt[1];
    });

    return { 
      original: p, 
      cx, cy, 
      width: pMaxX - pMinX, 
      height: pMaxY - pMinY,
      bbox: { minX: pMinX, maxX: pMaxX, minY: pMinY, maxY: pMaxY }
    };
  });

  // 估算标准 Panel 尺寸 (取中位数或第一个，用于设置聚类容差)
  const estPanelW = tempPanels[0].width;
  const estPanelH = tempPanels[0].height;

  // 2. 坐标聚类 (Clustering) - 核心修正
  // ---------------------------------------------------------
  // 提取所有中心坐标并排序
  const xCenters = tempPanels.map(p => p.cx).sort((a, b) => a - b);
  const yCenters = tempPanels.map(p => p.cy).sort((a, b) => a - b);

  // 定义辅助函数：获取唯一坐标轴 (去除微小抖动，合并同一行/列)
  const getUniqueCoords = (sortedCoords, tolerance) => {
    const unique = [];
    if (sortedCoords.length === 0) return unique;
    
    // 初始化第一个
    unique.push(sortedCoords[0]);
    
    for (let i = 1; i < sortedCoords.length; i++) {
      const current = sortedCoords[i];
      const last = unique[unique.length - 1];
      // 如果当前坐标与上一个坐标距离超过容差，则视为新的一行/列
      if (Math.abs(current - last) > tolerance) {
        unique.push(current);
      }
    }
    return unique;
  };

  // 容差设为面板尺寸的 1/4，足以区分行列，又能容忍浮点误差
  const uniqueX = getUniqueCoords(xCenters, estPanelW * 0.25);
  const uniqueY = getUniqueCoords(yCenters, estPanelH * 0.25);

  const columns = uniqueX.length;
  const rows = uniqueY.length;

  // 3. 重新分配 Col/Row 索引 (Mapping)
  // ---------------------------------------------------------
  // 辅助函数：找到最接近的 Grid 索引
  const findClosestIndex = (val, gridCoords) => {
    let bestIdx = -1;
    let minDiff = Infinity;
    gridCoords.forEach((coord, idx) => {
      const diff = Math.abs(val - coord);
      if (diff < minDiff) {
        minDiff = diff;
        bestIdx = idx;
      }
    });
    return bestIdx;
  };

  const panelsWithId = tempPanels.map(tp => {
    const col = findClosestIndex(tp.cx, uniqueX);
    const row = findClosestIndex(tp.cy, uniqueY);
    
    return {
      ...tp.original, // 保留原始属性 (id, points等)
      col,
      row,
      centerX: tp.cx,
      centerY: tp.cy,
      bbox: tp.bbox // 直接包含 bbox 信息，避免后续查找
    };
  });

  // 4. 计算物理边界 (Bounds)
  // ---------------------------------------------------------
  const colBounds = {};
  const rowBounds = {};

  panelsWithId.forEach(p => {
    // 直接使用 panel 中的 bbox 属性
    const pBBox = p.bbox;

    // 聚合 Col 边界
    if (!colBounds[p.col]) {
      colBounds[p.col] = { minX: pBBox.minX, maxX: pBBox.maxX };
    } else {
      colBounds[p.col].minX = Math.min(colBounds[p.col].minX, pBBox.minX);
      colBounds[p.col].maxX = Math.max(colBounds[p.col].maxX, pBBox.maxX);
    }
    
    // 聚合 Row 边界
    if (!rowBounds[p.row]) {
      rowBounds[p.row] = { minY: pBBox.minY, maxY: pBBox.maxY };
    } else {
      rowBounds[p.row].minY = Math.min(rowBounds[p.row].minY, pBBox.minY);
      rowBounds[p.row].maxY = Math.max(rowBounds[p.row].maxY, pBBox.maxY);
    }
  });

  // 5. 填补可能的空洞 (可选，但推荐)
  // 如果某些行/列完全没有Panel（例如异形玻璃），bounds可能为空。
  // 为了防止 SymmetryCalculator 报错，我们需要基于 Grid 推算空缺位置的 Bounds。
  // 这里做一个简单的插值/外推修复。
  const avgPitchX = (maxX - minX) / columns; 
  const avgPitchY = (maxY - minY) / rows;

  for (let c = 0; c < columns; c++) {
    if (!colBounds[c]) {
       // 估算：基于 minX + c * pitch
       // 注意：这是一个兜底，通常如果不缺 Panel 不会走到这
       const estX = minX + c * avgPitchX;
       colBounds[c] = { minX: estX, maxX: estX + estPanelW }; 
    }
  }
  for (let r = 0; r < rows; r++) {
    if (!rowBounds[r]) {
       const estY = minY + r * avgPitchY;
       rowBounds[r] = { minY: estY, maxY: estY + estPanelH };
    }
  }

  return { 
    minX, maxX, minY, maxY, 
    panelWidth: estPanelW, 
    panelHeight: estPanelH, 
    columns, rows, 
    panelsWithId, 
    colBounds, 
    rowBounds 
  };
}

// 计算 Mask 物理位置 (用于绘制背景虚线框)
const calculateMaskPositions = () => {
  maskPositions = [];
  const layout = analyzePanelLayout(glassConfig.panels);
  
  // 更新全局 panels 引用
  panels = layout ? layout.panelsWithId : [];
  
  // 发射layout状态变化事件
  emit('layout-status-change', panels.length > 0);
  
  if (!layout) return;

  // 获取规则参数
  const { cover_x, cover_y, full_shot } = glassConfig.maskRule;
  
  // 当cover_x或cover_y为null时，只绘制panel布局，不计算shot
  if (cover_x === null || cover_y === null) {
    return;
  }
  
  // 否则，按照现有逻辑计算shot
  const maskCols = cover_x || 99;
  const maskRows = cover_y || 99;
  const fullShot = full_shot || 1;

  // 实例化计算器
  const calculator = new SymmetryCalculator(
    layout.columns, layout.rows, 
    maskCols, maskRows, 
    fullShot
  );

  // 将逻辑 Shot 转换为物理 Mask 区域 (用于绘图)
  calculator.shots.forEach(shot => {
    const fullMaskW = maskCols * layout.panelWidth;
    const fullMaskH = maskRows * layout.panelHeight;

    // 获取有效范围的起始和结束 Grid 索引
    const startCol = shot.gridXRange.start;
    const endCol = shot.gridXRange.end - 1; // 结束索引是 exclusive，需减 1
    const startRow = shot.gridYRange.start;
    const endRow = shot.gridYRange.end - 1;

    // Physical X (左边缘): 起始列的最小 X 物理坐标
    const validPhysX = layout.colBounds[startCol].minX;

    // Physical Y (下边缘, Y向上为正): 起始行的最小 Y 物理坐标
    const validPhysY = layout.rowBounds[startRow].minY;

    // Physical Width: 结束列的最大 X - 起始列的最小 X
    const validPhysW = layout.colBounds[endCol].maxX - validPhysX;

    // Physical Height: 结束行的最大 Y - 起始行的最小 Y
    const validPhysH = layout.rowBounds[endRow].maxY - validPhysY;
    
    // (仅为完整 Mask 轮廓，用于计算 Mask 原点)
    const maskOriginPhysX = layout.minX + shot.originCol * layout.panelWidth;
    const maskOriginPhysY = layout.minY + shot.originRow * layout.panelHeight;

    maskPositions.push({
      id: shot.id,
      // 完整 Mask 轮廓 (大致位置)
      x: maskOriginPhysX,
      y: maskOriginPhysY,
      width: fullMaskW,
      height: fullMaskH,
      // 有效窗口 (虚线框绘制目标) - 使用精确物理边界
      validRect: {
        x: validPhysX,
        y: validPhysY,
        width: validPhysW,
        height: validPhysH
      },
      // 逻辑数据
      shotData: shot
    });
  });
}

// --- 碰撞检测工具函数 ---
// 计算两点之间的距离（单位：um）
const getDistance = (x1, y1, x2, y2) => {
  const dx = x2 - x1;
  const dy = y2 - y1;
  return Math.sqrt(dx * dx + dy * dy);
};

const isPointInPolygon = (point, polygon) => {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0], yi = polygon[i][1];
    const xj = polygon[j][0], yj = polygon[j][1];
    const intersect = ((yi > point.y) !== (yj > point.y)) && 
                      (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

const doLineSegmentsIntersect = (p1, q1, p2, q2) => {
  // 简化的线段相交检测 (叉积法)
  const onSegment = (p, q, r) => q.x <= Math.max(p.x, r.x) && q.x >= Math.min(p.x, r.x) &&
                                 q.y <= Math.max(p.y, r.y) && q.y >= Math.min(p.y, r.y);
  const orientation = (p, q, r) => {
    const val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y);
    if (val === 0) return 0;
    return (val > 0) ? 1 : 2;
  };
  const o1 = orientation(p1, q1, p2);
  const o2 = orientation(p1, q1, q2);
  const o3 = orientation(p2, q2, p1);
  const o4 = orientation(p2, q2, q1);
  
  if (o1 !== o2 && o3 !== o4) return true;
  if (o1 === 0 && onSegment(p1, p2, q1)) return true;
  if (o2 === 0 && onSegment(p1, q2, q1)) return true;
  if (o3 === 0 && onSegment(p2, p1, q2)) return true;
  if (o4 === 0 && onSegment(p2, q1, q2)) return true;
  return false;
}

const isLineIntersectingPanel = (start, end, panel) => {
  const poly = panel.points;
  // 1. 检查端点是否在内
  if (isPointInPolygon(start, poly) || isPointInPolygon(end, poly)) return true;
  // 2. 检查是否穿过边
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const p1 = { x: poly[i][0], y: poly[i][1] };
    const p2 = { x: poly[j][0], y: poly[j][1] };
    if (doLineSegmentsIntersect(start, end, p1, p2)) return true;
  }
  return false;
}

const getPanelId = (x, y) => {
  for (const p of panels) {
    if (isPointInPolygon({x, y}, p.points)) return p.id;
  }
  return '?';
}

const getAffectedPanels = (defect) => {
  const ids = new Set();
  const type = defect.type?.toUpperCase();
  
  if (type === 'LINE') {
    const start = defect.path[0];
    const end = defect.path[1];
    panels.forEach(p => {
      if (isLineIntersectingPanel(start, end, p)) ids.add(p.id);
    });
  } else if (type === 'REGION' || type === 'AREA') {
    // 检查 Panel 中心是否在区域内
    panels.forEach(p => {
      if (isPointInPolygon({x: p.centerX, y: p.centerY}, defect.path)) ids.add(p.id);
    });
  } else if (type === 'CURVE') {
    // 曲线采样检测
    const path = defect.path;
    path.forEach(pt => {
      const pid = getPanelId(pt.x, pt.y);
      if (pid !== '?') ids.add(pid);
    });
  } else {
    // Point / Mask
    const pid = getPanelId(defect.x, defect.y);
    if (pid !== '?') ids.add(pid);
  }
  return Array.from(ids);
}


// ==========================================
// Konva 绘图与交互逻辑
// ==========================================

const initStage = () => {
  const wrapper = document.getElementById('canvas-wrapper');
  if (!wrapper) return;
  
  const w = wrapper.clientWidth || 800;
  const h = wrapper.clientHeight || 600;
  
  // 计算缩放比例 (Fit)
  const ratioW = w / glassConfig.size.w;
  const ratioH = h / glassConfig.size.h;
  scaleRatio = Math.min(ratioW, ratioH) * 0.95;

  if (stage) stage.destroy();
  
  stage = new Konva.Stage({
    container: stageContainer.value,
    width: w,
    height: h
  });

  // 原点居中
  const centerX = w / 2;
  const centerY = h / 2;

  mainLayer = new Konva.Layer({ x: centerX, y: centerY });
  defectLayer = new Konva.Layer({ x: centerX, y: centerY });
  hintLayer = new Konva.Layer({ x: centerX, y: centerY });

  stage.add(mainLayer);
  stage.add(defectLayer);
  stage.add(hintLayer);

  drawBackground();
  redrawVisibleDefects();

  stage.on('mousedown touchstart', handleStageDown);
  stage.on('mousemove touchmove', handleStageMove);
  stage.on('mouseup touchend', handleStageUp);
};

const drawBackground = () => {
  mainLayer.destroyChildren();

  // 0. 绘制玻璃轮廓（带有右上角20*10mm倒角）
  const glassW = glassConfig.size.w;
  const glassH = glassConfig.size.h;
  const chamferW = 20000; // 20mm = 20000um
  const chamferH = 10000; // 10mm = 10000um
  
  // 定义玻璃轮廓路径点（带有右上角倒角）
  // 坐标原点在玻璃中心，Y轴向上
  const glassPath = [
    -glassW/2, -glassH/2, // 左下角
    glassW/2, -glassH/2,  // 右下角
    glassW/2, glassH/2 - chamferH, // 右下角上移chamferH
    glassW/2 - chamferW, glassH/2, // 右移chamferW，左上角
    -glassW/2, glassH/2, // 左上角
    -glassW/2, -glassH/2   // 回到左下角
  ];
  
  // 转换为屏幕坐标
  const screenPath = [];
  for (let i = 0; i < glassPath.length; i += 2) {
    const x = toScreen(glassPath[i]);
    const y = toScreenY(glassPath[i + 1]);
    screenPath.push(x, y);
  }
  
  // 绘制玻璃轮廓
  mainLayer.add(new Konva.Line({
    points: screenPath,
    stroke: '#ffffff',
    strokeWidth: 2,
    closed: true,
    listening: false,
    opacity: 0.8
  }));

  // 坐标系（贯穿玻璃轮廓，略超出轮廓，正向带箭头）
  const axisColor = '#ffffff';
  const axisOpacity = 0.8;
  const axisWidth = 1;
  const extendScreen = 18;
  const arrowSize = 6;

  const xAxisY = toScreenY(0);
  const yAxisX = toScreen(0);
  const leftScreen = toScreen(-glassW/2);
  const rightScreen = toScreen(glassW/2);
  const bottomScreen = toScreenY(-glassH/2);
  const topScreen = toScreenY(glassH/2);

  mainLayer.add(new Konva.Line({
    points: [leftScreen - extendScreen, xAxisY, rightScreen + extendScreen, xAxisY],
    stroke: axisColor,
    strokeWidth: axisWidth,
    opacity: axisOpacity,
    listening: false
  }));

  mainLayer.add(new Konva.Line({
    points: [
      rightScreen + extendScreen, xAxisY,
      rightScreen + extendScreen - arrowSize, xAxisY + arrowSize,
      rightScreen + extendScreen, xAxisY,
      rightScreen + extendScreen - arrowSize, xAxisY - arrowSize
    ],
    stroke: axisColor,
    strokeWidth: axisWidth,
    opacity: axisOpacity,
    listening: false
  }));

  const xLabel = new Konva.Text({
    x: rightScreen + extendScreen -16,
    y: xAxisY +6,
    text: 'x+',
    fontSize: 14,
    fill: axisColor,
    opacity: axisOpacity,
    listening: false
  });
  mainLayer.add(xLabel);

  mainLayer.add(new Konva.Line({
    points: [yAxisX, topScreen - extendScreen, yAxisX, bottomScreen + extendScreen],
    stroke: axisColor,
    strokeWidth: axisWidth,
    opacity: axisOpacity,
    listening: false
  }));

  mainLayer.add(new Konva.Line({
    points: [
      yAxisX, topScreen - extendScreen,
      yAxisX - arrowSize, topScreen - extendScreen + arrowSize,
      yAxisX, topScreen - extendScreen,
      yAxisX + arrowSize, topScreen - extendScreen + arrowSize
    ],
    stroke: axisColor,
    strokeWidth: axisWidth,
    opacity: axisOpacity,
    listening: false
  }));

  const yLabel = new Konva.Text({
    x: yAxisX + 8,
    y: topScreen - extendScreen - 2,
    text: 'y+',
    fontSize: 14,
    fill: axisColor,
    opacity: axisOpacity,
    listening: false
  });
  mainLayer.add(yLabel);

  // 1. 绘制 Panels
  panels.forEach((p, idx) => {
    const screenPoints = p.points.flatMap(pt => [toScreen(pt[0]), toScreenY(pt[1])]);
    
    const poly = new Konva.Line({
      points: screenPoints,
      fill: '#27272a',
      stroke: '#52525b',
      strokeWidth: 1,
      closed: true
    });

    // 动态 ID 字号
    const pW = toScreen(Math.abs(p.points[1][0] - p.points[0][0]));
    const pH = toScreen(Math.abs(p.points[2][1] - p.points[1][1]));
    const fontSize = Math.max(10, Math.min(32, Math.min(pW, pH) * 0.3));

    const text = new Konva.Text({
      x: toScreen(p.centerX),
      y: toScreenY(p.centerY),
      text: p.id || String(idx + 1),
      fontSize: fontSize,
      fill: 'rgba(255,255,255,0.3)',
      listening: false
    });
    text.offsetX(text.width()/2);
    text.offsetY(text.height()/2);

    mainLayer.add(poly);
    mainLayer.add(text);
  });

  // 2. 绘制 Mask 有效区域
  const maskColors = ['#ef4444', '#22c55e', '#3b82f6', '#eab308', '#a855f7'];
  maskPositions.forEach((mask, idx) => {
    const vr = mask.validRect;
    const x1 = toScreen(vr.x);
    const x2 = toScreen(vr.x + vr.width);
    const y1 = toScreenY(vr.y);
    const y2 = toScreenY(vr.y + vr.height);
    
    const rectPoints = [x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]; // 闭合
    const border = new Konva.Line({
      points: rectPoints,
      stroke: maskColors[idx % maskColors.length],
      strokeWidth: 2,
      dash: [8, 4],
      opacity: 0.6,
      listening: false
    });
    
    mainLayer.add(border);
  });

  mainLayer.draw();
}

const redrawVisibleDefects = () => {
  if (!defectLayer) return;
  defectLayer.destroyChildren();
  props.currentDefects.forEach(d => {
    const color = props.defectCodes.find(c => c.id === d.code)?.color || '#fff';
    const pts = d.path ? d.path.flatMap(p => [toScreen(p.x), toScreenY(p.y)]) : [];
    const defectType = d.type?.toUpperCase();
    
    if (defectType === 'POINT' || defectType === 'MASK') {
      defectLayer.add(new Konva.Circle({
        x: pts[0], y: pts[1], radius: 5, fill: color, stroke: d.isSymmetry ? 'yellow' : 'white', strokeWidth: 1.5
      }));
    } else {
      defectLayer.add(new Konva.Line({
        points: pts, stroke: color, strokeWidth: 2, closed: defectType === 'REGION' || defectType === 'AREA', fill: (defectType === 'REGION' || defectType === 'AREA') ? color + '40' : undefined
      }));
    }
  });
  defectLayer.draw();
}

// --- 交互事件处理 ---

const handleStageMove = () => {
  const pos = stage.getPointerPosition();
  if (!pos) return;
  const physX = toPhysical(pos.x - stage.width()/2);
  const physY = toPhysicalY(pos.y - stage.height()/2);
  currentMousePos.x = formatCoord(physX);
  currentMousePos.y = formatCoord(physY);
  
  // 更新屏幕坐标，使坐标显示跟随光标移动
  // 假设坐标显示div的宽度大约为150px（包含padding）
  const coordDivWidth = 150;
  const coordDivHeight = 30;
  
  // 获取画布容器尺寸
  const containerWidth = stage.width();
  const containerHeight = stage.height();
  
  // 计算坐标显示的位置，确保不会超出可视区域
  let displayX = pos.x;
  let displayY = pos.y;
  
  // 边界检查：右侧
  if (displayX + coordDivWidth + 20 > containerWidth) {
    displayX = pos.x - coordDivWidth - 20;
  }
  
  // 边界检查：底部
  if (displayY + coordDivHeight + 20 > containerHeight) {
    displayY = pos.y - coordDivHeight - 20;
  }
  
  currentScreenPos.x = displayX;
  currentScreenPos.y = displayY;

  if (drawingState.isDrawing) {
    const type = props.selectedCode.type?.toUpperCase();
    if (type === 'LINE') {
      // 线段：更新终点，应用水平/垂直修正
      const start = drawingState.points[0];
      const startScreen = [toScreen(start.x), toScreenY(start.y)];
      
      // 计算修正后的终点
      const endX = toPhysical(pos.x - stage.width()/2);
      const endY = toPhysicalY(pos.y - stage.height()/2);
      let correctedEndX = endX;
      let correctedEndY = endY;
      
      if (Math.abs(endX - start.x) > Math.abs(endY - start.y)) {
        // 水平线段
        correctedEndY = start.y;
      } else {
        // 垂直线段
        correctedEndX = start.x;
      }
      
      const correctedScreen = [toScreen(correctedEndX), toScreenY(correctedEndY)];
      drawingState.tempLine.points([...startScreen, ...correctedScreen]);
    } else {
      // 轨迹：追加点 (Region/Curve)
      const last = drawingState.points[drawingState.points.length - 1];
      const distSq = (physX - last.x)**2 + (physY - last.y)**2;
      const threshold = type === 'CURVE' ? 2000 : 1000; // Curve 2mm, Region 1mm
      
      if (distSq > threshold**2) {
        drawingState.points.push({x: physX, y: physY});
        const flatPts = drawingState.points.flatMap(p => [toScreen(p.x), toScreenY(p.y)]);
        drawingState.tempLine.points(flatPts);
      }
    }
    defectLayer.batchDraw();
  }
}

const handleStageDown = (e) => {
  if (e.target.name() === 'ghost-point') return;
  if (!props.selectedCode) return;
  // 如果是readonly角色，禁止绘图
  if (props.readonly) return;

  const pos = stage.getPointerPosition();
  const physX = toPhysical(pos.x - stage.width()/2);
  const physY = toPhysicalY(pos.y - stage.height()/2);

  // 检查点击位置是否在玻璃范围内（简单矩形范围，忽略倒角）
  const halfW = glassConfig.size.w / 2;
  const halfH = glassConfig.size.h / 2;
  if (Math.abs(physX) > halfW || Math.abs(physY) > halfH) {
    return;
  }
  
  // 检查是否有有效的layout（panels数组不为空）
  if (panels.length === 0) {
    return;
  }

  hintLayer.destroyChildren(); // 清除旧 Ghost
  hintLayer.draw();

  const type = props.selectedCode.type?.toUpperCase();
  const color = props.selectedCode.color || '#fff';

  if (type === 'POINT' || type === 'MASK') {
    addDefect(physX, physY, props.selectedCode, false);
    if (props.selectedCode.needSymmetry) {
      showSymmetryGhosts(physX, physY, props.selectedCode);
    }
  } else {
    // 绘制开始
    drawingState.isDrawing = true;
    drawingState.points = [{x: physX, y: physY}];
    
    // 初始化临时线
    if (drawingState.tempLine) drawingState.tempLine.destroy();
    drawingState.tempLine = new Konva.Line({
      points: [toScreen(physX), toScreenY(physY)],
      stroke: color, strokeWidth: 2, dash: [5, 5],
      closed: type === 'REGION' // 区域闭合
    });
    defectLayer.add(drawingState.tempLine);
  }
}

const handleStageUp = () => {
  if (!drawingState.isDrawing) return;
  drawingState.isDrawing = false;
  if (drawingState.tempLine) {
    drawingState.tempLine.destroy();
    drawingState.tempLine = null;
  }

  const pts = drawingState.points;
  if (pts.length < 1) return;
  
  // 检查是否有有效的layout（panels数组不为空）
  if (panels.length === 0) {
    drawingState.points = [];
    return;
  }
  
  // 检查绘制开始点是否在玻璃范围内
  const startPt = pts[0];
  const halfW = glassConfig.size.w / 2;
  const halfH = glassConfig.size.h / 2;
  if (Math.abs(startPt.x) > halfW || Math.abs(startPt.y) > halfH) {
    drawingState.points = [];
    return;
  }

  const code = props.selectedCode;
  const type = code.type?.toUpperCase();
  const minDistance = 2000; // 2mm = 2000um
  let finalPath = [];
  let direction = '';

  // 检查移动距离，过滤掉过小的绘制
  if (type === 'LINE') {
    // 线缺：检查起点和终点距离
    const start = pts[0];
    const pos = stage.getPointerPosition();
    const endX = toPhysical(pos.x - stage.width()/2);
    const endY = toPhysicalY(pos.y - stage.height()/2);
    const distance = getDistance(start.x, start.y, endX, endY);
    
    if (distance < minDistance) {
      drawingState.points = [];
      return;
    }
    
    // 处理线段：自动修正水平/垂直
    if (Math.abs(endX - start.x) > Math.abs(endY - start.y)) {
      direction = 'HORIZONTAL';
      finalPath = [start, {x: endX, y: start.y}];
    } else {
      direction = 'VERTICAL';
      finalPath = [start, {x: start.x, y: endY}];
    }
  } else if (type === 'CURVE' || type === 'REGION' || type === 'AREA') {
    // 曲线、面缺：检查总移动距离
    if (pts.length < 2) {
      drawingState.points = [];
      return;
    }
    
    let totalDistance = 0;
    for (let i = 1; i < pts.length; i++) {
      const prev = pts[i-1];
      const curr = pts[i];
      totalDistance += getDistance(prev.x, prev.y, curr.x, curr.y);
    }
    
    if (totalDistance < minDistance) {
      drawingState.points = [];
      return;
    }
    
    // 自动闭合面缺
    if (type === 'REGION' || type === 'AREA') {
      finalPath = [...pts];
      if (finalPath.length > 2) finalPath.push({...finalPath[0]});
    } else {
      finalPath = [...pts];
    }
  } else {
    finalPath = [...pts];
  }

  const defect = {
    uuid: `defect-${Date.now()}`,
    type: code.type,
    code: code.id,
    codeName: code.name,
    x: finalPath[0].x, y: finalPath[0].y, // 兼容字段
    path: finalPath,
    panelIds: getAffectedPanels({ type: code.type, path: finalPath, x: finalPath[0].x, y: finalPath[0].y }),
    isSymmetry: false,
    direction
  };

  emit('add-defect', defect);
  drawingState.points = [];
  defectLayer.draw();
}

const addDefect = (x, y, code, isSym) => {
  // 如果是readonly角色，禁止添加缺陷
  if (props.readonly) return;
  
  const defect = {
    uuid: `defect-${Date.now()}`,
    x, y,
    code: code.id,
    codeName: code.name,
    type: code.type,
    path: [{x, y}],
    panelIds: [getPanelId(x, y)],
    isSymmetry: isSym
  };

  emit('add-defect', defect);
}

// --- 对称点 Ghost 显示 ---
// --- 对称点 Ghost 显示 (修正版：基于物理边界的精确映射) ---
const showSymmetryGhosts = (physX, physY, codeObj) => {
  // 获取最新的布局信息（包含修正后的 colBounds/rowBounds）
  const layout = analyzePanelLayout(); 
  if (!layout) return;

  // 1. 【修正】不再使用除法计算 col/row，而是通过物理坐标反查所在的行列
  // 这样可以完美避开 Gap (间隙) 导致的计算偏差
  let col = -1;
  let row = -1;

  // 查找 X 落在哪个列的物理范围内
  // 增加少许 buffer (比如 100um) 以防点击在边缘
  const BUFFER = 100; 

  for (let c = 0; c < layout.columns; c++) {
    const bounds = layout.colBounds[c];
    if (bounds && physX >= bounds.minX - BUFFER && physX <= bounds.maxX + BUFFER) {
      col = c;
      break;
    }
  }

  // 查找 Y 落在哪个行的物理范围内
  for (let r = 0; r < layout.rows; r++) {
    const bounds = layout.rowBounds[r];
    if (bounds && physY >= bounds.minY - BUFFER && physY <= bounds.maxY + BUFFER) {
      row = r;
      break;
    }
  }

  // 如果点击在了 Panel 之间的缝隙里，直接返回，不生成 Ghost
  if (col === -1 || row === -1) return;

  // 2. 【修正】计算偏移量 (Offset)
  // 必须相对于该列 **真实的物理起始位置** 计算，而不是 (minX + col * width)
  // 这样才能消除间隙累积带来的漂移
  const originX = layout.colBounds[col].minX;
  const originY = layout.rowBounds[row].minY;
  
  const offsetX = physX - originX;
  const offsetY = physY - originY;

  // 3. 计算对称逻辑 (逻辑层不变)
  const { cover_x, cover_y, full_shot } = glassConfig.maskRule;
  
  if (cover_x === null || cover_y === null) return;
  
  const maskCols = cover_x || 99;
  const maskRows = cover_y || 99;
  const fullShot = full_shot || 1;
  
  const calc = new SymmetryCalculator(layout.columns, layout.rows, maskCols, maskRows, fullShot);
  const symmetries = calc.getSymmetries(col, row);

  symmetries.forEach(sym => {
    // 4. 【修正】还原物理坐标
    // 目标坐标 = 目标列的真实物理起点 + 原始偏移量
    // 即使 Panel 间距不均匀，这种算法也能保证相对位置绝对精确
    const targetBoundsX = layout.colBounds[sym.col];
    const targetBoundsY = layout.rowBounds[sym.row];
    
    if (!targetBoundsX || !targetBoundsY) return; // 防御性检查

    const symPhysX = targetBoundsX.minX + offsetX;
    const symPhysY = targetBoundsY.minY + offsetY;

    // 排除自己 (防止重叠显示)
    if (Math.abs(symPhysX - physX) < 1000 && Math.abs(symPhysY - physY) < 1000) return;

    const ghost = new Konva.Circle({
      x: toScreen(symPhysX),
      y: toScreenY(symPhysY),
      radius: 10,
      stroke: 'yellow',
      strokeWidth: 2,
      dash: [6, 4],
      fill: 'rgba(255, 255, 0, 0.2)',
      name: 'ghost-point',
      listening: true,
      // 存储元数据，点击时直接使用精确坐标
      attrs: {
        rawX: symPhysX,
        rawY: symPhysY
      }
    });

    const anim = new Konva.Animation(frame => {
      const s = 1 + Math.sin(frame.time * 0.006) * 0.2;
      ghost.scale({x: s, y: s});
    }, hintLayer);
    anim.start();

    ghost.on('click tap', () => {
      anim.stop();
      ghost.destroy();
      // 使用精确计算的物理坐标，而不是重新反算
      addDefect(ghost.attrs.rawX, ghost.attrs.rawY, codeObj, true);
      hintLayer.draw();
    });

    hintLayer.add(ghost);
  });
  
  hintLayer.draw();
}

// --- 生命周期与加载 ---
const loadPanelData = async () => {
  if (!props.selectedProductId) return;
  loading.value = true;
  try {
    const data = await getProductLayout(props.selectedProductId);
    // 添加默认值，确保玻璃尺寸始终有效
    glassConfig.size = data.glass_size || { w: 920000, h: 730000 };
    glassConfig.panels = data.panels || [];
    glassConfig.maskRule = data.mask_rule || { cover_x: 5, cover_y: 6, full_shot: 1 };
    
    nextTick(() => {
      initStage();
      calculateMaskPositions();
      drawBackground();
      // 发射layout状态变化事件
      emit('layout-status-change', glassConfig.panels.length > 0);
    });
  } catch(e) {
    console.error('Failed to load panel data:', e);
  } finally {
    loading.value = false;
  }
}

watch(() => props.selectedProductId, loadPanelData);
watch(() => props.currentDefects, redrawVisibleDefects, { deep: true });

// 监听selectedCode变化，清除对称点提示
watch(() => props.selectedCode, () => {
  if (hintLayer) {
    hintLayer.destroyChildren();
    hintLayer.draw();
  }
}, { immediate: false });

// 监听currentGlassId变化，清除对称点提示
watch(() => props.currentGlassId, () => {
  if (hintLayer) {
    hintLayer.destroyChildren();
    hintLayer.draw();
  }
}, { immediate: false });

onMounted(() => {
  if (props.selectedProductId) loadPanelData();
  window.addEventListener('resize', initStage);
});
</script>