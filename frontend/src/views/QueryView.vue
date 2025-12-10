<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <header class="bg-primary text-white p-4 shadow-md">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold">历史数据查询</h1>
        <router-link to="/" class="text-white hover:text-blue-200">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </router-link>
      </div>
    </header>
    
    <main class="flex-1 container mx-auto px-4 py-6">
      <!-- 查询条件面板 -->
      <div class="glass-panel mb-6">
        <h3 class="text-lg font-semibold mb-4">查询条件</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">查询类型</label>
            <select v-model="queryType" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
              <option value="lotId">批次ID</option>
              <option value="glassId">Glass ID</option>
              <option value="productId">产品ID</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">查询值</label>
            <input 
              v-model="queryValue" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入查询值"
            />
          </div>
        </div>
        
        <!-- 缺陷类型过滤 -->
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">缺陷类型过滤</label>
          <div class="flex flex-wrap gap-2">
            <label v-for="defect in defectTypes" :key="defect.code" class="inline-flex items-center">
              <input 
                type="checkbox" 
                :value="defect.code" 
                v-model="selectedDefectTypes"
                class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              >
              <span class="ml-2 text-sm text-gray-700">{{ defect.name }}</span>
            </label>
          </div>
        </div>
        
        <!-- 查询按钮 -->
        <div class="mt-4 flex justify-end">
          <button @click="performQuery" class="px-6 py-2 bg-primary text-white hover:bg-primary/90 rounded-lg transition-colors">
            查询
          </button>
        </div>
      </div>
      
      <!-- 查询结果区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧：Glass列表 -->
        <div class="lg:col-span-1">
          <div class="glass-panel">
            <h3 class="text-lg font-semibold mb-3">Glass列表</h3>
            <div class="max-h-80 overflow-y-auto">
              <div 
                v-for="glass in resultGlasses" 
                :key="glass.id"
                @click="selectGlassForQuery(glass.id)"
                class="p-2 mb-2 rounded-md cursor-pointer transition-all hover:bg-gray-100"
                :class="{ 'bg-primary text-white': selectedQueryGlassId === glass.id }"
              >
                <div class="font-medium">{{ glass.name }}</div>
                <div class="text-xs text-gray-500" v-if="glass.defectCount">
                  缺陷数量: {{ glass.defectCount }}
                </div>
              </div>
              <div v-if="resultGlasses.length === 0 && queryExecuted" class="text-center text-gray-500 py-4">
                未找到相关Glass数据
              </div>
            </div>
          </div>
        </div>
        
        <!-- 中间：Canvas显示区域 -->
        <div class="lg:col-span-2 space-y-4">
          <div class="glass-panel">
            <h3 class="text-lg font-semibold mb-3">缺陷分布</h3>
            <div class="canvas-container aspect-video">
              <div id="query-stage-container" class="w-full h-full"></div>
            </div>
          </div>
          
          <!-- 右侧：缺陷详情列表 -->
          <div class="glass-panel">
            <h3 class="text-lg font-semibold mb-3">缺陷详情</h3>
            <div class="max-h-60 overflow-y-auto">
              <div v-if="selectedQueryGlassDefects.length === 0 && selectedQueryGlassId" class="text-center text-gray-500 py-4">
                该Glass暂无缺陷记录
              </div>
              <div 
                v-for="(defect, index) in selectedQueryGlassDefects" 
                :key="index"
                class="p-3 mb-2 rounded-md border"
                :class="{
                  'border-danger': defect.code === 'scratch',
                  'border-warning': defect.code === 'bright_point',
                  'border-info': defect.code === 'gate_open',
                  'border-success': defect.code === 'sym_black',
                }"
              >
                <div class="flex justify-between items-center">
                  <p class="font-semibold">{{ getDefectTypeName(defect.code) }}</p>
                  <p class="text-xs text-gray-500">{{ formatDate(defect.timestamp) }}</p>
                </div>
                <p class="text-sm text-gray-600 mt-1">{{ defect.panelInfo }}</p>
                <p class="text-xs text-gray-500 mt-1" v-if="defect.remark">
                  备注: {{ defect.remark }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <footer class="bg-gray-800 text-white py-4 mt-6">
      <div class="container mx-auto px-4 text-center text-sm">
        <p>MAC检测系统 - 历史数据查询界面</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Konva from 'konva'
import { queryDefectRecords, getReasonCodeList, getInitData, getDefects } from '../services/api'

// 响应式数据
const queryType = ref('lotId')
const queryValue = ref('')
const selectedDefectTypes = ref([])
const defectTypes = ref([])
const resultGlasses = ref([])
const selectedQueryGlassId = ref(null)
const selectedQueryGlassDefects = ref([])
const queryExecuted = ref(false)
const loading = ref(false)
const error = ref('')

// 初始化数据
const initData = ref({
  product_ids: [],
  lot_ids: [],
  cst_ids: [],
  equipments: []
})

// Konva舞台引用
let stage = null
let layer = null
let glassGroup = null
let defectLayer = null

// 初始化
onMounted(async () => {
  await loadInitDataFromApi()
  await loadDefectTypes()
  initQueryCanvas()
})

// 清理
onUnmounted(() => {
  if (stage) {
    stage.destroy()
  }
})

// 监听选中的Glass变化
watch(selectedQueryGlassId, (newId) => {
  if (newId) {
    loadGlassDefects(newId)
  }
})

// 加载初始化数据
async function loadInitDataFromApi() {
  try {
    loading.value = true
    const data = await getInitData()
    initData.value = data
  } catch (err) {
    error.value = '加载初始化数据失败'
  } finally {
    loading.value = false
  }
}

// 加载缺陷类型
async function loadDefectTypes() {
  try {
    loading.value = true
    const data = await getReasonCodeList()
    defectTypes.value = data.map(code => ({
      code: code.CODE,
      name: code.DESCREPTION
    }))
  } catch (error) {
    error.value = '加载缺陷类型失败'
    // 失败时使用模拟数据
    defectTypes.value = [
      { code: 'scratch', name: '划伤' },
      { code: 'bright_point', name: '亮点' },
      { code: 'gate_open', name: 'GateOpen' },
      { code: 'sym_black', name: '对称黑点' }
    ]
  } finally {
    loading.value = false
  }
}

// 初始化查询Canvas
function initQueryCanvas() {
  // 创建舞台
  stage = new Konva.Stage({
    container: 'query-stage-container',
    width: 800,
    height: 600
  })
  
  // 创建图层
  layer = new Konva.Layer()
  defectLayer = new Konva.Layer()
  
  // 创建Glass组
  glassGroup = new Konva.Group({ draggable: false })
  
  // 添加到舞台
  layer.add(glassGroup)
  stage.add(layer)
  stage.add(defectLayer)
  
  // 绘制示例Glass布局
  drawGlassLayout()
  
  // 响应式调整
  window.addEventListener('resize', handleResize)
  handleResize()
}

// 绘制Glass布局
function drawGlassLayout() {
  // 清空现有内容
  glassGroup.destroyChildren()
  
  // 模拟Glass基板（730*920mm）
  const glassWidth = 730
  const glassHeight = 920
  const margin = 10
  
  // 计算缩放比例
  const container = stage.container()
  const scaleX = (container.clientWidth - margin * 2) / glassWidth
  const scaleY = (container.clientHeight - margin * 2) / glassHeight
  const scale = Math.min(scaleX, scaleY)
  
  // 设置缩放
  glassGroup.scale({ x: scale, y: scale })
  
  // 绘制Glass边框
  const glassRect = new Konva.Rect({
    x: margin,
    y: margin,
    width: glassWidth,
    height: glassHeight,
    stroke: '#333',
    strokeWidth: 2,
    fill: '#f5f5f5'
  })
  glassGroup.add(glassRect)
  
  // 绘制Panel示例（简单的网格布局）
  const panelWidth = 150
  const panelHeight = 200
  const panelMargin = 20
  
  let panelId = 1
  for (let y = margin + panelMargin; y < glassHeight - panelHeight - panelMargin; y += panelHeight + panelMargin) {
    for (let x = glassWidth - margin - panelWidth - panelMargin; x > margin + panelMargin; x -= panelWidth + panelMargin) {
      // 绘制Panel
      const panelRect = new Konva.Rect({
        x: x,
        y: y,
        width: panelWidth,
        height: panelHeight,
        stroke: '#666',
        strokeWidth: 1,
        fill: '#fff'
      })
      glassGroup.add(panelRect)
      
      // 添加Panel ID
      const panelText = new Konva.Text({
        x: x + 10,
        y: y + 10,
        text: `Panel ${panelId}`,
        fontSize: 16,
        fill: '#333'
      })
      glassGroup.add(panelText)
      
      panelId++
    }
  }
  
  // 居中显示
  const offsetX = (stage.width() - (glassWidth * scale + margin * 2)) / 2
  const offsetY = (stage.height() - (glassHeight * scale + margin * 2)) / 2
  glassGroup.position({ x: offsetX, y: offsetY })
  
  layer.draw()
}

// 处理窗口调整
function handleResize() {
  if (!stage) return
  
  const container = stage.container()
  const containerRect = container.getBoundingClientRect()
  
  stage.width(containerRect.width)
  stage.height(containerRect.height)
  
  // 重新绘制布局
  drawGlassLayout()
  drawDefects()
  
  layer.draw()
  defectLayer.draw()
}

// 执行查询
async function performQuery() {
  if (!queryValue.value.trim()) {
    alert('请输入查询值')
    return
  }
  
  try {
    loading.value = true
    // 构建查询参数
    const queryParams = {
      type: queryType.value,
      value: queryValue.value,
      defectTypes: selectedDefectTypes.value
    }
    
    // 调用API查询数据
    const response = await queryDefectRecords(queryParams)
    resultGlasses.value = response.records || []
    
    queryExecuted.value = true
    
    // 默认选中第一个
    if (resultGlasses.value.length > 0) {
      selectGlassForQuery(resultGlasses.value[0].id)
    }
  } catch (error) {
    error.value = '查询失败，请重试'
    alert('查询失败，请重试')
  } finally {
    loading.value = false
  }
}

// 选择Glass进行查询
function selectGlassForQuery(glassId) {
  selectedQueryGlassId.value = glassId
  // 清空缺陷图层
  defectLayer.destroyChildren()
  defectLayer.draw()
  // 加载缺陷数据
  loadGlassDefects(glassId)
}

// 加载Glass缺陷数据
async function loadGlassDefects(glassId) {
  try {
    loading.value = true
    // 调用API获取缺陷数据
    const defects = await getDefects(glassId)
    selectedQueryGlassDefects.value = defects || []
    
    // 在Canvas上绘制缺陷
    drawDefects()
  } catch (error) {
    error.value = '加载缺陷数据失败'
  } finally {
    loading.value = false
  }
}

// 在Canvas上绘制缺陷
function drawDefects() {
  // 清空现有缺陷
  defectLayer.destroyChildren()
  
  // 获取缩放比例
  const scale = glassGroup.scaleX()
  const offset = glassGroup.position()
  
  selectedQueryGlassDefects.value.forEach(defect => {
    defect.points.forEach(point => {
      // 转换坐标到Canvas坐标系
      const canvasX = point.x * scale + offset.x
      const canvasY = point.y * scale + offset.y
      
      if (defect.code === 'scratch') {
        // 绘制线条缺陷
        if (defect.points.length >= 2) {
          const linePoints = defect.points.flatMap(p => [
            p.x * scale + offset.x,
            p.y * scale + offset.y
          ])
          const line = new Konva.Line({
            points: linePoints,
            stroke: getDefectColor(defect.code),
            strokeWidth: 3,
            tension: 0.5,
            closed: false
          })
          defectLayer.add(line)
        }
      } else {
        // 绘制点缺陷
        const circle = new Konva.Circle({
          x: canvasX,
          y: canvasY,
          radius: 6,
          fill: getDefectColor(defect.code),
          stroke: '#fff',
          strokeWidth: 2
        })
        defectLayer.add(circle)
      }
    })
  })
  
  defectLayer.draw()
}

// 获取缺陷颜色
function getDefectColor(code) {
  const colorMap = {
    'scratch': '#F53F3F',    // 红色
    'bright_point': '#FF7D00',  // 橙色
    'gate_open': '#86909C',   // 灰色
    'sym_black': '#00B42A'    // 绿色
  }
  return colorMap[code] || '#333'
}

// 获取缺陷类型名称
function getDefectTypeName(code) {
  const defect = defectTypes.value.find(d => d.code === code)
  return defect ? defect.name : code
}

// 格式化日期
function formatDate(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
/* 样式调整 */
</style>