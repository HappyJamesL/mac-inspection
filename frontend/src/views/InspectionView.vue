<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <header class="h-12 bg-white shadow-sm flex items-center justify-between px-4 z-20 border-b border-gray-200 shrink-0">
      <div class="flex items-center space-x-3">
        <span class="font-bold text-blue-800 text-sm"><i class="fa-solid fa-microchip mr-1"></i>MAC System</span>
        
        <div class="flex items-center text-xs text-gray-700">
            <span class="mr-1 font-medium">CST:</span>
            <div class="relative">
                <input 
                    type="text" 
                    v-model="selectedInfo.cst" 
                    class="bg-gray-100 border border-gray-300 rounded text-xs py-1 pr-6 pl-2 focus:border-blue-500 w-20"
                    placeholder="输入或选择"
                    @keyup.enter="onCstLotChange('cst')"
                    @focus="hideDropdown('cst'); isInputActive = true"
                    @blur="handleBlur('cst'); isInputActive = false"
                    @input="filterDropdownOptions('cst')"
                >
                <div 
                    class="absolute right-1 top-1/2 -translate-y-1/2 w-4 h-4 flex items-center justify-center cursor-pointer text-gray-500 hover:text-blue-500"
                    @mousedown.prevent="loadDropdownData('cst')"
                >
                    <span class="text-[10px]">▼</span>
                </div>
                
                <!-- 自定义下拉列表 -->
                <div 
                    v-if="showCstDropdown" 
                    class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs"
                >
                    <div 
                        v-for="c in selectOptions.cst" 
                        :key="c" 
                        class="px-2 py-1 hover:bg-blue-100 cursor-pointer"
                        @mousedown.prevent="selectOption('cst', c)"
                    >
                        {{ c }}
                    </div>
                    <div v-if="!selectOptions.cst || selectOptions.cst.length === 0" class="px-2 py-1 text-gray-400">
                        暂无数据
                    </div>
                </div>
            </div>
        </div>

        <div class="flex items-center text-xs text-gray-700">
            <span class="mr-1 font-medium">Lot:</span>
            <div class="relative">
                <input 
                    type="text" 
                    v-model="selectedInfo.lot" 
                    class="bg-gray-100 border border-gray-300 rounded text-xs py-1 pr-6 pl-2 focus:border-blue-500 w-36"
                    placeholder="输入或选择"
                    @keyup.enter="onCstLotChange('lot')"
                    @focus="hideDropdown('lot'); isInputActive = true"
                    @blur="handleBlur('lot'); isInputActive = false"
                    @input="filterDropdownOptions('lot')"
                >
                <div 
                    class="absolute right-1 top-1/2 -translate-y-1/2 w-4 h-4 flex items-center justify-center cursor-pointer text-gray-500 hover:text-blue-500"
                    @mousedown.prevent="loadDropdownData('lot')"
                >
                    <span class="text-[10px]">▼</span>
                </div>
                
                <!-- 自定义下拉列表 -->
                <div 
                    v-if="showLotDropdown" 
                    class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs"
                >
                    <div 
                        v-for="l in selectOptions.lots" 
                        :key="l" 
                        class="px-2 py-1 hover:bg-blue-100 cursor-pointer"
                        @mousedown.prevent="selectOption('lot', l)"
                    >
                        {{ l }}
                    </div>
                    <div v-if="!selectOptions.lots || selectOptions.lots.length === 0" class="px-2 py-1 text-gray-400">
                        暂无数据
                    </div>
                </div>
            </div>
        </div>

        <div class="flex items-center text-xs text-gray-700">
            <span class="mr-1 font-medium">WorkOrder:</span>
            <div class="relative">
                <input 
                    type="text" 
                    v-model="selectedInfo.productrequestname" 
                    readonly
                    class="bg-gray-100 border border-gray-300 rounded text-xs py-1 px-1 focus:border-blue-500 w-24 cursor-not-allowed"
                >
            </div>
        </div>

        <div class="flex items-center text-xs text-gray-700">
            <span class="mr-1 font-medium">Product:</span>
            <div class="relative">
                <input 
                    type="text" 
                    v-model="selectedInfo.product" 
                    readonly
                    class="bg-gray-100 border border-gray-300 rounded text-xs py-1 px-1 focus:border-blue-500 w-32 cursor-not-allowed"
                >
            </div>
        </div>
        
        <div class="flex items-center text-xs text-gray-700">
            <span class="mr-1 font-medium">OPER:</span>
            <div class="relative">
                <input 
                    type="text" 
                    v-model="selectedInfo.processOperationName" 
                    readonly
                    class="bg-gray-100 border border-gray-300 rounded text-xs py-1 px-1 focus:border-blue-500 w-14 cursor-not-allowed"
                >
            </div>
        </div>

        <div class="flex items-center text-xs text-gray-700">
            <span class="mr-1 font-medium">Machine:</span>
            <div v-if="hasStoredMachine" class="bg-gray-100 border border-gray-300 rounded text-xs py-1 px-1 focus:border-blue-500">
                {{ selectedInfo.eq }}
            </div>
            <select v-else v-model="selectedInfo.eq" @change="handleMachineChange" class="bg-gray-100 border border-gray-300 rounded text-xs py-1 px-1 focus:border-blue-500">
                <option v-for="e in selectOptions.eqs" :key="e">{{ e }}</option>
            </select>
        </div>

        <div class="flex items-center text-xs text-gray-700">
            <span class="mr-1 font-medium">LogIn:</span>
            <input v-model="selectedInfo.operatorId"  class="bg-gray-100 border border-gray-300 rounded text-xs py-1 px-1 focus:border-blue-500 w-20" @focus="isInputActive = true" @blur="isInputActive = false">
        </div>
      </div>
      
      <div class="text-xs flex items-center space-x-3">
        <!-- Layout状态提示 -->
        <span v-if="!hasLayout" class="text-yellow-600 font-bold">
          <i class="fa-solid fa-exclamation-triangle"></i> 缺Layout
        </span>
        
        <!-- 保存成功提示 -->
        <span v-else-if="autoSaveStatus" class="text-green-600 font-bold">
          <i class="fa-solid fa-check"></i> 保存成功
        </span>
        
        <!-- 保存/删除操作提示 -->
        <div v-else-if="saveMessage" :class="[
          'flex items-center font-bold px-2 py-1 rounded',
          saveMessageType === 'success' ? 'bg-green-100 text-green-700' : 
          saveMessageType === 'error' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
        ]">
          <i v-if="saveMessageType === 'success'" class="fa-solid fa-check-circle mr-1"></i>
          <i v-else-if="saveMessageType === 'error'" class="fa-solid fa-exclamation-circle mr-1"></i>
          <span>{{ saveMessage }}</span>
        </div>
        
        <!-- 默认Ready状态 -->
        <span v-else>Ready</span>
        
        <!-- 帮助按钮 -->
        <button 
          @click="showHelpModal = true"
          class="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center space-x-1 cursor-pointer"
          title="系统操作说明"
        >
          <i class="fa-solid fa-circle-question"></i>
        </button>
      </div>
    </header>

    <main class="flex-1 flex overflow-hidden">
      
      <aside class="w-64 bg-white flex flex-col border-r border-gray-200 z-10 shadow-md shrink-0">
        <div class="h-1/3 flex flex-col border-b border-gray-200">
          <div class="p-2 bg-gray-50 border-b flex justify-between items-center">
            <h3 class="font-bold text-gray-700 text-xs">Glass ID</h3>
            <span class="text-[10px] bg-gray-200 px-1.5 rounded">{{ glassList.length }}</span>
          </div>
          <div class="flex-1 overflow-y-auto p-1 space-y-0.5 scrollbar-hide">
            <div 
              v-for="glass in glassList" 
              :key="glass.id"
              @click="switchGlass(glass.id)"
              :class="['px-3 py-2 rounded text-xs font-medium flex justify-between items-center cursor-pointer transition-colors',
                currentGlassId === glass.id ? 'bg-blue-600 text-white' : 'hover:bg-gray-100 text-gray-600']"
            >
              <span>{{ glass.id }}</span>
              <span v-if="dbData[glass.id] && dbData[glass.id].length > 0" class="w-1.5 h-1.5 rounded-full bg-yellow-400 shadow-sm"></span>
            </div>
          </div>
        </div>

        <div class="flex-1 flex flex-col bg-gray-50 min-h-0">
          <div class="p-2 border-b bg-white flex justify-between items-center">
            <h3 
              class="font-bold text-gray-700 text-xs cursor-pointer hover:text-blue-600 transition-colors"
              @click="currentFilterType = 'all'"
            >
              Defect Code
            </h3>
            <div class="flex space-x-1">
              <button 
                v-for="filter in filterOptions" 
                :key="filter.value"
                @click="currentFilterType = filter.value"
                :class="['text-[10px] px-1.5 py-0.5 rounded font-mono', 
                  currentFilterType === filter.value ? 'bg-blue-600 text-white' : 
                  filter.value === 'point' ? 'text-blue-600 bg-blue-100' : 
                  filter.value === 'line' ? 'text-green-600 bg-green-100' : 
                  filter.value === 'curve' ? 'text-yellow-600 bg-yellow-100' : 
                  'text-gray-600 bg-gray-100']"
              >
                {{ filter.label }}
              </button>
            </div>
          </div>
          <div class="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-hide" ref="defectListRef">
            <button
              v-for="code in filteredDefectCodes"
              :key="code.id"
              @click="switchCode(code)"
              :class="['w-full py-3 px-3 rounded flex items-center text-xs font-bold border transition-all',
                selectedCode?.id === code.id 
                  ? 'border-blue-500 bg-white shadow-md ring-1 ring-blue-500 text-blue-700 transform scale-[1.02]' 
                  : 'border-transparent bg-white text-gray-600 hover:bg-gray-100',
                'cursor-pointer']"
              :ref="el => { if (el) el.dataset.levelno = code.levelno }"
            >
              <span class="w-4 text-center mr-2 text-gray-600">{{ code.levelno }}</span>
              <div class="w-3 h-3 rounded-full mr-2 shadow-sm" :style="{background: code.color}"></div>
              <span class="flex-1 text-left">{{ code.name }}</span>
              <span 
                :class="['text-[10px] px-1.5 py-0.5 rounded font-mono ml-1', 
                  {'text-red-600 bg-red-100': code.needSymmetry}, 
                  {'text-blue-600 bg-blue-100': code.type === 'point' && !code.needSymmetry}, 
                  {'text-green-600 bg-green-100': code.type === 'line'}, 
                  {'text-yellow-600 bg-yellow-100': code.type === 'curve'}, 
                  {'text-gray-600 bg-gray-100': code.type === 'region' || code.type === 'area'}]"
              >
                  {{ code.type === 'point' ? (code.needSymmetry ? 'Mask' : '点缺') : 
                     code.type === 'line' ? '线缺' : 
                     code.type === 'curve' ? '曲线' : 
                     code.type === 'mask' ? 'Mask' : '面缺' }}
              </span>
            </button>
          </div>
        </div>
      </aside>

      <section class="flex-1 overflow-hidden">
        <!-- Canvas绘制区域 -->
        <CanvasStage 
          :selected-code="selectedCode" 
          :current-defects="visibleDefects"
          :defect-codes="defectCodes"
          :selected-product-id="selectedInfo.product"
          :readonly="isReadonly"
          :current-glass-id="currentGlassId"
          @add-defect="addDefect"
          @layout-status-change="hasLayout = $event"
        />
      </section>

      <aside class="w-64 bg-white border-l border-gray-200 flex flex-col z-10 shrink-0">
        <div class="p-2 border-b bg-gray-50 flex justify-between items-center h-10">
          <div class="flex items-center space-x-2">
            <h3 class="font-bold text-gray-800 text-xs">Records</h3>
            <span v-if="isReadonly" class="text-[12px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">只读权限</span>
          </div>
          <div class="flex items-center space-x-2">
            <!-- CopyFrom按钮 -->
            <div class="relative" v-if="currentDefects.length === 0 && !isReadonly">
              <button 
                @click="toggleCopyFromDropdown" 
                :class="['px-2 py-1 rounded text-xs font-medium transition-colors',
                  showCopyFromDropdown ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
              >
                CopyFrom
              </button>
              <!-- 下拉菜单 -->
              <div 
                v-if="showCopyFromDropdown" 
                class="absolute right-0 mt-1 bg-white border border-gray-200 rounded shadow-lg z-50 text-xs overflow-hidden min-w-[140px]"
              >
                <div 
                  v-for="glass in defectiveGlasses" 
                  :key="glass.id"
                  @click="copyDefectsFromGlass(glass.id)"
                  class="px-3 py-2 hover:bg-blue-50 cursor-pointer text-gray-700 transition-colors"
                >
                  {{ glass.id }} ({{ glass.defectCount }})
                </div>
                <div 
                  v-if="defectiveGlasses.length === 0"
                  class="px-3 py-2 text-gray-400 cursor-not-allowed"
                >
                  无可用Glass
                </div>
              </div>
            </div>
            
            <button 
              @click="toggleOverlay" 
              :class="['px-2 py-1 rounded text-xs font-medium transition-colors',
                showAllDefects ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
            >
              叠加
            </button>
            <span class="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded">{{ visibleDefects.length }}</span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto scrollbar-hide bg-white">
          <div 
              v-for="record in visibleDefects" 
              :key="record.uuid"
              class="border-b border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center px-3 py-2 cursor-pointer group" @click="!isReadonly && toggleEdit(record)">
                <div class="w-2 h-2 rounded-full mr-2 shrink-0 shadow-sm" :style="{background: getCodeColor(record.code)}"></div>
              
              <div class="flex-1 min-w-0 flex flex-col justify-center">
                <div class="flex items-center text-xs">
                  <span class="font-bold text-gray-700 mr-1">{{ record.codeName }}</span>
                  <span class="font-mono text-gray-500 font-bold truncate" :title="getFullDefectInfo(record)">
                    : P{{ formatPanelIds(record) }}
                  </span> 
                  
                  <i v-if="record.isSymmetry" class="fa-solid fa-clone text-[10px] text-orange-400 ml-1" title="自动对称点"></i>
                </div>
                <div class="text-[10px] text-gray-400 font-mono mt-0.5 truncate">
                  <span v-if="record.type === 'POINT' || record.type === 'point' || record.type === 'mask'">
                    ({{ formatCoord(record.x) }}, {{ formatCoord(record.y) }})
                  </span>
                  <span v-else-if="record.type === 'LINE' || record.type === 'line'">
                    线段 ({{ record.direction === 'HORIZONTAL' ? `${formatCoord(record.x)}, -` : `- , ${formatCoord(record.y)}` }})
                  </span>
                  <span v-else-if="record.type === 'curve'">
                    曲线 [{{ record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(',') }}]
                  </span>
                  <span v-else-if="record.type === 'REGION' || record.type === 'region'">
                    区域 [{{ record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(',') }}]
                  </span>
                  <span v-else>
                    ({{ formatCoord(record.x) }}, {{ formatCoord(record.y) }})
                  </span>
                </div>
              </div>

              <button 
                v-if="!isReadonly" 
                @click.stop="removeDefect(record.uuid)" 
                class="w-6 h-6 flex items-center justify-center bg-gray-50 hover:bg-red-200 rounded-full transition-all duration-200 transform hover:scale-105 shadow-sm relative"
              >
                <div class="w-2.5 h-0.5 bg-gray-500 hover:bg-red-900 transition-colors duration-200 transform rotate-45 absolute"></div>
                <div class="w-2.5 h-0.5 bg-gray-500 hover:bg-red-900 transition-colors duration-200 transform -rotate-45 absolute"></div>
              </button>
            </div>

            <div v-if="record.isEditing || record.remark" class="px-3 pb-2 bg-gray-50/50">
              <input 
                v-if="record.isEditing && !isReadonly"
                v-model="record.remark"
                :ref="el => { if(el) inputRefs[record.uuid] = el }"
                @blur="saveRemark(record); isInputActive = false"
                @focus="isInputActive = true"
                @keyup.enter="saveRemark(record)"
                placeholder="输入备注..."
                class="w-full text-xs border border-blue-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-100 bg-white"
              >
              <div v-else-if="!isReadonly" @click="toggleEdit(record)" class="text-[10px] text-gray-500 truncate cursor-text hover:text-blue-600 flex items-center">
                <i class="fa-regular fa-comment-dots mr-1.5 opacity-50"></i>{{ record.remark }}
              </div>
              <div v-else class="text-[10px] text-gray-500 truncate cursor-default flex items-center">
                <i class="fa-regular fa-comment-dots mr-1.5 opacity-50"></i>{{ record.remark }}
              </div>
            </div>
          </div>
        </div>
      </aside>
    </main>
    
    <!-- 帮助模态框 -->
    <div 
      v-if="showHelpModal" 
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click.self="closeHelpModal"
    >
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- 模态框标题 -->
        <div class="bg-blue-600 text-white px-6 py-4 flex justify-between items-center">
          <h3 class="text-lg font-bold flex items-center">
            <i class="fa-solid fa-circle-question mr-2"></i>
            系统操作说明
          </h3>
          <button 
            @click="closeHelpModal"
            class="text-white hover:text-gray-200 text-xl focus:outline-none"
          >
            &times;
          </button>
        </div>
        
        <!-- 模态框内容 -->
        <div class="px-6 py-4 overflow-y-auto flex-1">
          <div class="space-y-6">
            <section>
              <h4 class="text-md font-semibold text-gray-800 mb-2 flex items-center">
                <i class="fa-solid fa-info-circle text-blue-600 mr-2"></i>
                系统简介
              </h4>
              <p class="text-sm text-gray-700">
                MAC系统是一款用于玻璃宏观检测的软件，支持多种缺陷类型的标注和管理。
              </p>
            </section>
            
            <section>
              <h4 class="text-md font-semibold text-gray-800 mb-2 flex items-center">
                <i class="fa-solid fa-gear text-blue-600 mr-2"></i>
                主要功能
              </h4>
              <ul class="list-disc pl-5 text-sm text-gray-700 space-y-1">
                <li>玻璃缺陷标注与管理</li>
                <li>多种缺陷类型支持（点缺、线缺、曲线、面缺）</li>
                <li>缺陷代码分类与过滤,并支持键盘输入数字定位</li>
                <li>缺陷数据自动保存</li>
                <li>自动计算MASK SHOT位置,显示SHOT边缘线</li>
                <li>Mask缺陷的对称点自动提示</li>
                <li>碰撞检测,根据绘制轨迹计算影响的panelID</li>
                <li>从其他Glass复制缺陷</li>
              </ul>
            </section>
            
            <section>
              <h4 class="text-md font-semibold text-gray-800 mb-2 flex items-center">
                <i class="fa-solid fa-keyboard text-blue-600 mr-2"></i>
                操作指南
              </h4>
              <div class="space-y-4">
                 <div>
                  <h5 class="text-sm font-medium text-gray-700 mb-1">首次操作</h5>
                  <p class="text-xs text-gray-600 pl-4">请选择设备编号,后续操作将自动加载该设备。</p>
                </div>
                <div>
                  <h5 class="text-sm font-medium text-gray-700 mb-1">标注缺陷</h5>
                  <p class="text-xs text-gray-600 pl-4">1、选择或输入CST/LOT, 再选择GlassID</p>
                  <p class="text-xs text-gray-600 pl-4">2、选择需要标注的缺陷Code</p>
                  <ul class="list-disc pl-8 text-xs text-gray-600 space-y-1">
                    <li>滚动列表选择缺陷Code</li>
                    <li>支持点击缺陷类型进行过滤</li>
                    <li>支持键盘输入数字进行定位</li>
                  </ul>
                  <p class="text-xs text-gray-600 pl-4">3、在中间画布区域点击或绘制缺陷：</p>
                  <ul class="list-disc pl-8 text-xs text-gray-600 space-y-1">
                    <li>点缺：直接点击即可。mask类型会自动提示对称点</li>
                    <li>线缺：点击并拖动绘制线段</li>
                    <li>曲线：点击并拖动绘制自由曲线</li>
                    <li>面缺：点击并拖动绘制封闭区域</li>
                  </ul>
                </div>
                <div>
                  <h5 class="text-sm font-medium text-gray-700 mb-1">管理缺陷</h5>
                  <p class="text-xs text-gray-600 pl-4">在右侧缺陷记录列表中可以：</p>
                  <ul class="list-disc pl-8 text-xs text-gray-600 space-y-1">
                    <li>鼠标悬停可查看缺陷详细信息</li>
                    <li>点击缺陷以添加缺陷备注</li>
                    <li>删除不需要的缺陷</li>
                    <li>从其他Glass复制缺陷</li>
                  </ul>
                </div>
              </div>
            </section>
            
            <section>
              <h4 class="text-md font-semibold text-gray-800 mb-2 flex items-center">
                <i class="fa-solid fa-exclamation-triangle text-blue-600 mr-2"></i>
                注意事项
              </h4>
              <ul class="list-disc pl-5 text-sm text-gray-700 space-y-1">
                <li>确保选择或输入正确的CST和Lot信息</li>
                <li>缺陷标注后会自动保存到系统</li>
                <li>如果Layout未加载，请联系TEST组在ADC系统导入</li>
                <li>如果Mask Shot边缘线未加载或错误，请联系PHT在TAQ1831报表中查询并修正</li>
                <li>只读权限用户只能查看缺陷，无法编辑</li>
                <li>使用完成后请及时退出系统</li>
              </ul>
            </section>
          </div>
        </div>
        
        <!-- 模态框底部 -->
        <div class="bg-gray-50 px-6 py-3 flex justify-end border-t">
          <button 
            @click="closeHelpModal"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import CanvasStage from '../components/CanvasStage.vue'
import api, { getInitData, getGlassList, getReasonCodeList, getDefects, saveDefectRecord, getRelatedInfoByCstOrLot, filterOptionsByOper, getMachineByIp, getDefectsByLot } from '../services/api'

// 创建路由实例，用于获取URL参数
const route = useRoute()

// --- 角色控制 --- 
// 从URL获取userrole参数
const userrole = ref(route.query.userrole || '')
// 计算属性：判断是否为readonly角色
const isReadonly = computed(() => userrole.value === 'readonly')

// --- 1. 基础数据 ---

// 顶部下拉选择数据
const selectOptions = reactive({
    products: [], 
    lots: [],
    cst: [],
    lotFull: [], // 存储完整的LOT数据，用于过滤
    cstFull: [], // 存储完整的CST数据，用于过滤
    eqs: [],
    processOperations: []
});
const selectedInfo = reactive({
    product: '',
    lot: '',
    eq: '',
    cst: '',
    processOperationName: '',
    productrequestname: '',
    operatorId: ''
});

// 缺陷代码
const defectCodes = ref([]);

// 过滤状态
const currentFilterType = ref('all'); // 默认显示所有类型

// 过滤选项配置
const filterOptions = [
  { label: '点缺', value: 'point' },
  { label: '线缺', value: 'line' },
  { label: '曲线', value: 'curve' },
  { label: '面缺', value: 'region' }
];

// Glass列表
const glassList = ref([]);

// 状态变量
const currentGlassId = ref('');
const selectedCode = ref({});
const currentDefects = ref([]);
const inputRefs = ref({});
const autoSaveStatus = ref(false);
const showAllDefects = ref(true); // 新增：控制是否显示所有缺陷
const showCopyFromDropdown = ref(false); // 控制CopyFrom下拉菜单显示
const defectiveGlasses = ref([]); // 存储同一Lot中有缺陷的Glass列表
const loading = ref(false);
const error = ref('');
const dbData = ref({}); // 新增：用于存储每个glass的缺陷记录数量，显示标记
const showCstDropdown = ref(false); // 控制CST下拉列表显示
const showLotDropdown = ref(false); // 控制Lot下拉列表显示
const hasLayout = ref(true); // 新增：控制layout状态，默认有layout
const showHelpModal = ref(false); // 新增：控制帮助模态框显示

// 全局数字输入定位缺陷相关变量
const isInputActive = ref(false); // 当前是否有活跃输入框
const digitBuffer = ref(''); // 存储连续输入的数字
let digitTimer = null; // 用于重置输入缓冲区的计时器
const defectListRef = ref(null); // 缺陷列表容器引用

// 统一操作反馈信息显示函数
const showMessage = (message, type = 'success', duration = 1500) => {
  saveMessage.value = message;
  saveMessageType.value = type;
  
  // 错误或缺失信息，显示时间延长到3秒
  const displayDuration = type === 'error' ? 3000 : duration;
  
  setTimeout(() => {
    saveMessage.value = '';
  }, displayDuration);
};

// 缓存配置
const MAX_CACHE_ITEMS = 25;
const CACHE_META_KEY = 'defect_cache_meta';

// 获取缓存键名
const getCacheKey = (glassId, processOperationName) => {
  return `defect_cache_${glassId}_${processOperationName}`;
};

// 获取缓存元数据
const getCacheMeta = () => {
  try {
    const meta = localStorage.getItem(CACHE_META_KEY);
    return meta ? JSON.parse(meta) : {};
  } catch (error) {
    return {};
  }
};

// 保存缓存元数据
const saveCacheMeta = (meta) => {
  try {
    localStorage.setItem(CACHE_META_KEY, JSON.stringify(meta));
  } catch (error) {
  }
};

// 更新缓存访问时间
const updateCacheAccessTime = (glassId, processOperationName) => {
  const cacheKey = getCacheKey(glassId, processOperationName);
  const meta = getCacheMeta();
  
  if (meta[cacheKey]) {
    meta[cacheKey].accessedAt = Date.now();
    saveCacheMeta(meta);
  }
};

// 获取缓存数据
const getCache = (glassId, processOperationName) => {
  try {
    const cacheKey = getCacheKey(glassId, processOperationName);
    const cacheData = localStorage.getItem(cacheKey);
    
    if (cacheData) {
      updateCacheAccessTime(glassId, processOperationName);
      return JSON.parse(cacheData);
    }
  } catch (error) {
  }
  
  return null;
};

// 设置缓存数据
const setCache = (glassId, processOperationName, data) => {
  try {
    const cacheKey = getCacheKey(glassId, processOperationName);
    
    // 保存缓存数据
    localStorage.setItem(cacheKey, JSON.stringify(data));
    
    // 更新缓存元数据
    const meta = getCacheMeta();
    const now = Date.now();
    
    if (meta[cacheKey]) {
      // 缓存已存在，更新访问时间
      meta[cacheKey].accessedAt = now;
    } else {
      // 新缓存，添加元数据
      meta[cacheKey] = {
        createdAt: now,
        accessedAt: now
      };
    }
    
    saveCacheMeta(meta);
    
    // 清理超出限制的缓存
    cleanupCache();
  } catch (error) {
  }
};

// 清理超出限制的缓存
const cleanupCache = () => {
  try {
    const meta = getCacheMeta();
    const cacheKeys = Object.keys(meta);
    
    if (cacheKeys.length > MAX_CACHE_ITEMS) {
      // 按创建时间排序，删除最早的缓存
      const sortedKeys = cacheKeys.sort((a, b) => meta[a].createdAt - meta[b].createdAt);
      const keysToDelete = sortedKeys.slice(0, cacheKeys.length - MAX_CACHE_ITEMS);
      
      // 删除超出限制的缓存
      keysToDelete.forEach(key => {
        localStorage.removeItem(key);
        delete meta[key];
      });
      
      // 保存更新后的元数据
      saveCacheMeta(meta);
    }
  } catch (error) {
  }
};

// --- 2. 核心计算 ---

// 格式化坐标显示
const formatCoord = (val) => val !== null ? Math.round(val / 1000) : '-'; // um -> mm, null表示不记录

// 获取缺陷代码颜色
const getCodeColor = (id) => {
  const c = defectCodes.value.find(x => x.id === id);
  return c ? c.color : '#ccc';
};

// 过滤后的缺陷代码
const filteredDefectCodes = computed(() => {
  if (currentFilterType.value === 'all') {
    return defectCodes.value;
  } else if (currentFilterType.value === 'point') {
    return defectCodes.value.filter(code => code.type === 'point' || code.type === 'mask'); // 包含普通点缺和mask类型
  } else if (currentFilterType.value === 'region') {
    return defectCodes.value.filter(code => code.type === 'region' || code.type === 'area');
  } else {
    return defectCodes.value.filter(code => code.type === currentFilterType.value);
  }
});

// 格式化panelIds显示
const formatPanelIds = (record) => {
  // 兼容旧数据可能仍然使用panelId字段的情况
  const panelIds = record.panelIds || [record.panelId]
  if (!panelIds || panelIds.length === 0) return '?'
  if (panelIds.length <= 3) return panelIds.join(',')
  return `${panelIds.slice(0, 3).join(',')}...`
};

// 获取完整的缺陷信息，用于悬停提示
const getFullDefectInfo = (record) => {
  let info = `PanelIDs: ${record.panelIds?.join(',') || record.panelId}\n`
  
  // 处理不同类型的缺陷，显示完整坐标
  if (record.type === 'LINE' || record.type === 'line') {
    info += `类型: ${record.type}\n`
    info += `方向: ${record.direction === 'HORIZONTAL' ? '水平' : '垂直'}\n`
    info += `坐标: ${record.direction === 'HORIZONTAL' ? `${formatCoord(record.x)}, -` : `- , ${formatCoord(record.y)}`}\n`
    info += `路径: ${record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(' → ')}`
  } else if (record.type === 'REGION' || record.type === 'region') {
    info += `类型: ${record.type}\n`
    info += `坐标: (${record.x !== null ? formatCoord(record.x) : '-'}, ${record.y !== null ? formatCoord(record.y) : '-'})\n`
    info += `路径点数量: ${record.path.length}个\n`
    info += `路径: ${record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(' → ')}`
  } else if (record.type === 'curve' || record.type === 'CURVE') {
    info += `类型: ${record.type}\n`
    info += `坐标: (${record.x !== null ? formatCoord(record.x) : '-'}, ${record.y !== null ? formatCoord(record.y) : '-'})\n`
    info += `路径点数量: ${record.path.length}个\n`
    info += `路径: ${record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(' → ')}`
  } else {
    info += `类型: ${record.type}\n`
    info += `坐标: (${record.x !== null ? formatCoord(record.x) : '-'}, ${record.y !== null ? formatCoord(record.y) : '-'})`
  }
  
  return info
};

// 计算属性：获取可见的缺陷
const visibleDefects = computed(() => {
  if (showAllDefects.value) {
    return currentDefects.value;
  } else {
    return currentDefects.value.filter(d => d.code === selectedCode.value.id);
  }
});

// --- 3. 事件处理 ---

// 切换叠加模式
const toggleOverlay = () => {
  showAllDefects.value = !showAllDefects.value;
};

// 切换CopyFrom下拉菜单
const toggleCopyFromDropdown = () => {
  showCopyFromDropdown.value = !showCopyFromDropdown.value;
};

// 关闭帮助模态框
const closeHelpModal = () => {
  showHelpModal.value = false;
};

// 获取同一Lot中有缺陷的Glass列表
const getDefectiveGlasses = () => {
  const defectiveList = [];
  for (const glass of glassList.value) {
    const defectCount = dbData.value[glass.id]?.length || 0;
    if (defectCount > 0 && glass.id !== currentGlassId.value) {
      defectiveList.push({
        id: glass.id,
        defectCount
      });
    }
  }
  return defectiveList;
};

// 从指定Glass复制缺陷到当前Glass
const copyDefectsFromGlass = async (sourceGlassId) => {
  try {
    // 获取源Glass的缺陷
    const defects = await getDefects(sourceGlassId, selectedInfo.processOperationName);
    
    if (defects.length > 0) {
      // 为每个缺陷生成新的UUID，避免冲突
      const newDefects = defects.map(defect => {
        return {
          ...defect,
          uuid: `defect-${Date.now()}${Math.random().toString(36).substr(2, 9)}`,
          isModified: true
        };
      });
      
      // 将缺陷添加到当前Glass
      currentDefects.value = [...newDefects];
      
      // 关闭下拉菜单
      showCopyFromDropdown.value = false;
      
      // 触发自动保存
      triggerAutoSave();
    }
  } catch (err) {
  }
};

// 切换Glass
// 切换缺陷代码
const switchCode = (code) => {
  selectedCode.value = code;
};

// 添加缺陷
const addDefect = (rec) => {
  // 标记为已修改
  rec.isModified = true;
  currentDefects.value.push(rec);
  triggerAutoSave();
};

// 移除缺陷
const removeDefect = async (uuid) => {
  // 先找到要删除的缺陷，用于可能的回滚
  const defectToRemove = currentDefects.value.find(d => d.uuid === uuid);
  if (!defectToRemove) {
    return;
  }
  
  try {
    // 先从数据库中删除
    // 使用api对象调用，自动添加/mac/前缀，uuid已包含defect-前缀
    await api.delete(`/api/v1/defect/${uuid}`);
    
    // 只有API成功后，才从当前列表中移除
    currentDefects.value = currentDefects.value.filter(d => d.uuid !== uuid);
    
    // 更新dbData，确保glass列表右侧标记正确
    dbData.value[currentGlassId.value] = currentDefects.value;
    
    // 更新有缺陷的Glass列表
    defectiveGlasses.value = getDefectiveGlasses();
    
    // 更新本地缓存
    const { processOperationName } = selectedInfo;
    setCache(currentGlassId.value, processOperationName, currentDefects.value);
    
    // 显示删除成功提示
    showMessage('删除成功', 'success');
  } catch (err) {
    // 显示删除失败提示
    const errorMsg = err.response?.data?.detail || err.message || '删除失败';
    showMessage(`删除失败: ${errorMsg}`, 'error');
  }
};

// 切换编辑状态
const toggleEdit = (rec) => {
  currentDefects.value.forEach(d => d.isEditing = false);
  rec.isEditing = true;
  nextTick(() => {
    if (inputRefs.value[rec.uuid]) inputRefs.value[rec.uuid].focus();
  });
};

// 保存备注
const saveRemark = (rec) => {
  rec.isEditing = false;
  // 标记为已修改
  rec.isModified = true;
  triggerAutoSave();
};

// 全局键盘事件处理
const handleKeydown = (e) => {
  // 如果有活跃输入框，不处理
  if (isInputActive.value) return;
  
  // 如果是数字键（0-9）
  if (e.key >= '0' && e.key <= '9') {
    // 添加到输入缓冲区
    digitBuffer.value += e.key;
    
    // 清除之前的计时器
    if (digitTimer) {
      clearTimeout(digitTimer);
    }
    
    // 设置新的计时器，300ms后处理输入
    digitTimer = setTimeout(() => {
      processDigitInput();
    }, 300);
  }
};

// 处理数字输入，定位缺陷
const processDigitInput = () => {
  if (!digitBuffer.value) return;
  
  const inputLevelno = parseInt(digitBuffer.value);
  // 重置输入缓冲区
  digitBuffer.value = '';
  
  // 查找对应的缺陷代码（如果有多个相同levelno，取第一个）
  const matchedCode = filteredDefectCodes.value.find(code => code.levelno === inputLevelno);
  
  if (matchedCode) {
    // 激活匹配的缺陷代码
    switchCode(matchedCode);
    
    // 滚动到匹配的缺陷项
    scrollToDefect(inputLevelno);
  }
};

// 滚动到匹配的缺陷项
const scrollToDefect = (levelno) => {
  nextTick(() => {
    if (defectListRef.value) {
      // 查找对应的按钮元素
      const buttons = defectListRef.value.querySelectorAll('button');
      let targetButton = null;
      
      for (const button of buttons) {
        if (parseInt(button.dataset.levelno) === levelno) {
          targetButton = button;
          break;
        }
      }
      
      if (targetButton) {
        // 平滑滚动到元素
        targetButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  });
};

// --- 3. 事件处理 ---

// 切换Glass
const switchGlass = async (id) => {
  currentGlassId.value = id;
  // 传入最新的processOperationName，确保使用正确的值
  await loadGlassDefects(id, true, selectedInfo.processOperationName);
  // 更新有缺陷的Glass列表
  defectiveGlasses.value = getDefectiveGlasses();
};

// 加载Glass缺陷
const loadGlassDefects = async (glassId, isCurrentGlass = true, processOperationName = null) => {
  try {
    // 使用传入的processOperationName或从selectedInfo中获取
    const opName = processOperationName || selectedInfo.processOperationName;
    
    // 检查本地缓存
    const cachedDefects = getCache(glassId, opName);
    if (cachedDefects !== null) {
      // 使用缓存数据（包括空数组）
      if (isCurrentGlass) {
        currentDefects.value = cachedDefects;
      }
      dbData.value[glassId] = cachedDefects;
      return cachedDefects;
    }
    
    // 缓存不存在，调用API获取
    // 只有当processOperationName有效时，才调用getDefects
    let defects = [];
    if (opName) {
      defects = await getDefects(glassId, opName);
    }
    
    if (isCurrentGlass) {
      currentDefects.value = defects;
    }
    dbData.value[glassId] = defects;
    
    // 将数据存入本地缓存（无论是否为空数组）
    setCache(glassId, opName, defects);
    return defects;
  } catch (err) {
    const emptyDefects = [];
    if (isCurrentGlass) {
      currentDefects.value = emptyDefects;
    }
    dbData.value[glassId] = emptyDefects;
    
    // 错误情况下也写入空数组到缓存，避免重复调用API
    const opName = processOperationName || selectedInfo.processOperationName;
    setCache(glassId, opName, emptyDefects);
    return emptyDefects;
  }
};

// 保存缺陷
const saveDefect = async (defect) => {
  try {
    // 检查glass_id、站点OPER和缺陷code是否为空
    if (!defect.glass_id || !defect.processoperationname || !defect.defect_code) {
      return { success: false, message: '玻璃ID、站点OPER或缺陷code为空，无法保存' };
    }
    const result = await saveDefectRecord(defect);
    return result;
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || '保存失败';
    return { success: false, message: `保存失败: ${errorMsg}` };
  }
};

// 转换坐标格式：{x, y} -> [x, y]
const convertCoordinates = (path) => {
  if (!path || !Array.isArray(path)) return [];
  return path.map(point => [point.x, point.y]);
};

// 保存提示状态
const saveMessage = ref('');
const saveMessageType = ref(''); // success, error, info

// 自动保存
const triggerAutoSave = async () => {
  // 只保存当前修改的缺陷，而不是所有缺陷
  const modifiedDefects = currentDefects.value.filter(defect => defect.isModified);
  
  // 检查glass_id和站点OPER是否为空
  if (!currentGlassId.value || !selectedInfo.processOperationName) {
    return;
  }
  
  if (modifiedDefects.length > 0) {
    let savedCount = 0;
    let failedCount = 0;
    
    // 遍历修改的缺陷，逐个保存
    for (const defect of modifiedDefects) {
      // 检查缺陷code是否为空
      if (!defect.code) {
        defect.isModified = false; // 重置修改标志，避免重复提醒
        continue;
      }
      
      // 转换坐标格式
      const geomData = convertCoordinates(defect.path);
      
      // 构建符合后端schema的缺陷记录
      const defectRecord = {
        uuid: defect.uuid,
        glass_id: currentGlassId.value,
        lotname: selectedInfo.lot || '',
        productrequestname: selectedInfo.productrequestname || '',
        product_id: selectedInfo.product || '', // 使用当前选中的产品型号
        defect_code: defect.code || '',
        defect_type: defect.type || 'point',
        geom_data: geomData,
        panel_id: defect.panelIds?.join(',') || '',
        is_symmetry: defect.isSymmetry ? 'Y' : 'N',
        remark: defect.remark || '',
        operator_id: selectedInfo.operatorId || '',
        machinename: selectedInfo.eq || '',
        processoperationname: selectedInfo.processOperationName || ''
      };
      
      // 保存单个缺陷记录
      const result = await saveDefect(defectRecord);
      
      if (result.success) {
        // 保存成功后重置修改标志
        defect.isModified = false;
        savedCount++;
      } else {
        // 保存失败，保留修改标志
        failedCount++;
      }
    }
    
    // 统计结果
    if (failedCount === 0) {
      // 所有缺陷都保存成功，更新本地缓存
      const { processOperationName } = selectedInfo;
      setCache(currentGlassId.value, processOperationName, currentDefects.value);
      
      // 更新dbData，确保glass列表右侧标记正确
      dbData.value[currentGlassId.value] = currentDefects.value;
      
      // 更新有缺陷的Glass列表
      defectiveGlasses.value = getDefectiveGlasses();
      
      // 保存成功后更新状态
      autoSaveStatus.value = true;
      setTimeout(() => {
        autoSaveStatus.value = false;
      }, 1500);
    } else {
      // 有缺陷保存失败，不更新缓存
      showMessage(`保存成功 ${savedCount} 个，失败 ${failedCount} 个`, 'error');
    }
  }
};

// --- 4. 数据加载方法 ---

// 加载初始化数据
const loadInitData = async () => {
  try {
    loading.value = true;
    const data = await getInitData();
    selectOptions.products = data.productspecs || [];
    selectOptions.lots = data.lot_ids || [];
    selectOptions.cst = data.cst_ids || [];
    selectOptions.eqs = data.equipments || []; // 添加这行，将后端返回的equipments赋值给selectOptions.eqs
    
    // 保存完整数据用于过滤
    selectOptions.lotFull = [...selectOptions.lots];
    selectOptions.cstFull = [...selectOptions.cst];
    
    // 对LOT和CST下拉列表进行递增排序
    selectOptions.lots.sort();
    selectOptions.cst.sort();
    // 同步排序完整数据
    selectOptions.lotFull.sort();
    selectOptions.cstFull.sort();
    
    // 设置默认选中值
    selectedInfo.product = selectOptions.products[0] || '';
    selectedInfo.lot = selectOptions.lots[0] || '';
    selectedInfo.cst = selectOptions.cst[0] || '';
    selectedInfo.processOperationName = selectOptions.processOperations[0] || '';
    
    // 页面初次加载时，根据lot调用related-info接口获取其他字段信息
    if (selectedInfo.lot) {
      await onCstLotChange();
    }
    
    // 从LocalStorage读取Machine值
    const storedMachine = localStorage.getItem('machine');
    if (storedMachine) {
      selectedInfo.eq = storedMachine;
    } else {
      // 如果LocalStorage中没有值，使用默认值
      selectedInfo.eq = selectOptions.eqs[0] || '';
    }
    


  } catch (err) {
    error.value = '加载初始化数据失败';
  } finally {
    loading.value = false;
  }
};

// 加载Glass列表
const loadGlassList = async (processOperationName = null) => {
  try {
    loading.value = true;
    const lot = selectedInfo.lot;
    
    // 只有当lot有效时才调用getGlassList
    if (!lot) {
      glassList.value = [];
      currentGlassId.value = '';
      currentDefects.value = [];
      dbData.value = {};
      defectiveGlasses.value = [];
      return;
    }
    
    const data = await getGlassList(lot);
    // 按id递增排序glass列表
    glassList.value = data.sort((a, b) => a.id.localeCompare(b.id));
    
    if (glassList.value.length > 0) {
      currentGlassId.value = glassList.value[0].id;
      
      // 使用传入的processOperationName或从selectedInfo中获取最新值
      const opName = processOperationName || selectedInfo.processOperationName;
      
      // 只有当processOperationName有效时，才调用getDefectsByLot
      if (opName) {
        // 使用按lot查询接口一次性获取所有Glass的缺陷数据
        const allDefects = await getDefectsByLot(lot, opName);
        
        // 按glassId分组缺陷数据
        const defectsByGlass = {};
        for (const defect of allDefects) {
          const glassId = defect.glassId || defect.productname;
          if (!defectsByGlass[glassId]) {
            defectsByGlass[glassId] = [];
          }
          defectsByGlass[glassId].push(defect);
        }
        
        // 处理每个Glass的缺陷数据，确保所有Glass都有缺陷记录（包括空记录）
        for (const glass of glassList.value) {
          const glassId = glass.id;
          // 获取该glass的缺陷数据，如果没有则为空数组
          const glassDefects = defectsByGlass[glassId] || [];
          
          // 更新缓存
          setCache(glassId, opName, glassDefects);
          
          // 更新dbData
          dbData.value[glassId] = glassDefects;
          
          // 如果是当前glass，更新currentDefects
          if (glassId === currentGlassId.value) {
            currentDefects.value = glassDefects;
          }
        }
        
        // 更新有缺陷的Glass列表
        defectiveGlasses.value = getDefectiveGlasses();
      } else {
        // processOperationName无效，清空缺陷数据
        for (const glass of glassList.value) {
          const glassId = glass.id;
          dbData.value[glassId] = [];
        }
        currentDefects.value = [];
        defectiveGlasses.value = [];
      }
    } else {
      // 清空数据
      currentGlassId.value = '';
      currentDefects.value = [];
      dbData.value = {};
      defectiveGlasses.value = [];
    }
  } catch (err) {
    error.value = '加载Glass列表失败';
    glassList.value = [];
    currentGlassId.value = '';
    currentDefects.value = [];
    dbData.value = {};
    defectiveGlasses.value = [];
  } finally {
    loading.value = false;
  }
};

// 加载缺陷代码
const loadDefectCodes = async () => {
  try {
    loading.value = true;
    const data = await getReasonCodeList();
    defectCodes.value = data.map(code => {
      // 获取小写的codetype
      const codeType = (code.CODETYPE || 'point').toLowerCase();
      
      return {
        id: code.CODE,
        name: code.CODE, // name绑定code，显示CODE而不是DESCREPTION
        description: code.DESCREPTION, // 保留DESCREPTION作为描述
        color: code.COLOR || '#FF0000',
        needSymmetry: codeType === 'mask', // 如果codetype是mask，则needSymmetry为true
        type: codeType, // 使用小写的codetype
        levelno: code.LEVELNO || 0 // 添加levelno字段
      };
    });
    // 按levelno递增排序
    defectCodes.value.sort((a, b) => a.levelno - b.levelno);
    if (defectCodes.value.length > 0) {
      selectedCode.value = defectCodes.value[0];
    }
  } catch (err) {
    error.value = '加载缺陷代码失败';
    defectCodes.value = [];
  } finally {
    loading.value = false;
  }
};

// --- 5. 生命周期钩子 ---

// 批次变化由onCstLotChange函数统一处理，移除watch监听
// watch(
//   () => selectedInfo.lot,
//   async (newLot) => {
//     if (newLot) {
//       await loadGlassList();
//     }
//   }
// );

// 监听站点变化，无需清理缓存（新方案自动管理缓存数量）
watch(
  () => selectedInfo.processOperationName,
  async () => {
    // 站点变化时无需清理缓存，新方案会自动管理
  }
);

// 处理输入框获取焦点事件
const onInputFocus = async (field) => {
  try {
    loading.value = true;
    // 调用API获取最新的初始化数据
    const data = await getInitData();
    
    // 根据获取焦点的字段，更新对应的下拉列表数据并清空输入框值
    if (field === 'cst') {
      selectOptions.cst = data.cst_ids || [];
      selectedInfo.cst = '';
    } else if (field === 'lot') {
      selectOptions.lots = data.lot_ids || [];
      selectedInfo.lot = '';
    }
  } catch (err) {
  } finally {
    loading.value = false;
  }
};

// 加载下拉列表数据
const loadDropdownData = async (field) => {
  try {
    loading.value = true;
    // 调用API获取最新的初始化数据
    const data = await getInitData();
    
    // 根据字段类型，更新对应的下拉列表数据并清空输入框值
    if (field === 'cst') {
      // 保存完整数据用于过滤
      selectOptions.cstFull = data.cst_ids || [];
      // 对CST下拉列表进行递增排序
      selectOptions.cstFull.sort();
      // 初始显示完整列表
      selectOptions.cst = [...selectOptions.cstFull];
      selectedInfo.cst = '';
      showCstDropdown.value = true;
      showLotDropdown.value = false;
    } else if (field === 'lot') {
      // 保存完整数据用于过滤
      selectOptions.lotFull = data.lot_ids || [];
      // 对LOT下拉列表进行递增排序
      selectOptions.lotFull.sort();
      // 初始显示完整列表
      selectOptions.lots = [...selectOptions.lotFull];
      selectedInfo.lot = '';
      showLotDropdown.value = true;
      showCstDropdown.value = false;
    }
  } catch (err) {
  } finally {
    loading.value = false;
  }
};

// 选择下拉选项
const selectOption = async (field, value) => {
  // 设置选择的值
  if (field === 'cst') {
    selectedInfo.cst = value;
    showCstDropdown.value = false;
  } else if (field === 'lot') {
    selectedInfo.lot = value;
    showLotDropdown.value = false;
  }
  
  // 触发related-info接口
  await onCstLotChange(field);
};

// 处理输入框失去焦点事件
const handleBlur = (field) => {
  // 延迟执行以允许点击下拉选项
  setTimeout(() => {
    if (field === 'cst') {
      showCstDropdown.value = false;
      // 移除对onCstLotChange的调用，避免重复请求
    } else if (field === 'lot') {
      showLotDropdown.value = false;
      // 移除对onCstLotChange的调用，避免重复请求
    }
  }, 200);
};

// 隐藏下拉列表
const hideDropdown = (field) => {
  if (field === 'cst') {
    showCstDropdown.value = false;
  } else if (field === 'lot') {
    showLotDropdown.value = false;
  }
};

// 过滤下拉列表选项
const filterDropdownOptions = (field) => {
  if (field === 'cst') {
    const inputValue = selectedInfo.cst.toLowerCase();
    // 根据输入值过滤CST列表
    selectOptions.cst = selectOptions.cstFull.filter(item => 
      item.toLowerCase().includes(inputValue)
    );
  } else if (field === 'lot') {
    const inputValue = selectedInfo.lot.toLowerCase();
    // 根据输入值过滤LOT列表
    selectOptions.lots = selectOptions.lotFull.filter(item => 
      item.toLowerCase().includes(inputValue)
    );
  }
};

// 处理CST或Lot变化事件
const onCstLotChange = async (changedField) => {
  try {
    const { cst, lot } = selectedInfo;
    let params = {};
    
    // 根据触发事件的字段，只传递该字段的值
    if (changedField === 'cst' && cst) {
      params = { cst };
    } else if (changedField === 'lot' && lot) {
      params = { lot };
    } else if (cst || lot) {
      // 兼容其他调用场景，如页面初始化时
      params = { cst, lot };
    }
    
    if (Object.keys(params).length > 0) {
      loading.value = true;
      // 调用API获取关联信息
      const relatedInfo = await getRelatedInfoByCstOrLot(params);
      
      // 检查relatedInfo是否有效
      if (relatedInfo) {
        // 自动填充相关字段
        if (relatedInfo.processOperationName) {
          selectedInfo.processOperationName = relatedInfo.processOperationName;
        }
        if (relatedInfo.productrequestname) {
          selectedInfo.productrequestname = relatedInfo.productrequestname;
        }
        if (relatedInfo.product) {
          selectedInfo.product = relatedInfo.product;
        }
        // 更新CST或Lot（如果API返回了更准确的值）
        if (relatedInfo.cst) {
          selectedInfo.cst = relatedInfo.cst;
        }
        if (relatedInfo.lot) {
          selectedInfo.lot = relatedInfo.lot;
        }
        
        // 更新选项列表
        if (relatedInfo.processOperations) {
            selectOptions.processOperations = relatedInfo.processOperations;
        }
        if (relatedInfo.productrequestnames) {
            selectOptions.productrequestnames = relatedInfo.productrequestnames;
        }
        if (relatedInfo.products) {
            selectOptions.products = relatedInfo.products;
        }
        
        // 只有在获取到关联信息后，才调用loadGlassList，传入最新的processOperationName
        await loadGlassList(relatedInfo.processOperationName);
      } else {
        // relatedInfo为空，清空相关数据
        currentGlassId.value = '';
        currentDefects.value = [];
        dbData.value = {};
        defectiveGlasses.value = [];
        glassList.value = [];
      }
    }
  } catch (err) {
    // 错误情况下，清空相关数据
    currentGlassId.value = '';
    currentDefects.value = [];
    dbData.value = {};
    defectiveGlasses.value = [];
    glassList.value = [];
  } finally {
    loading.value = false;
  }
};

// 处理OPER变化事件
const onOperChange = async (oper) => {
  try {
    if (oper) {
      loading.value = true;
      // 调用API获取过滤后的选项
      const filteredOptions = await filterOptionsByOper(oper);
      
      // 更新选项列表
        if (filteredOptions.cst) {
            selectOptions.cst = filteredOptions.cst;
            // 对CST下拉列表进行递增排序
            selectOptions.cst.sort();
            // 保存完整数据用于过滤
            selectOptions.cstFull = [...selectOptions.cst];
        }
        if (filteredOptions.lots) {
            selectOptions.lots = filteredOptions.lots;
            // 对LOT下拉列表进行递增排序
            selectOptions.lots.sort();
            // 保存完整数据用于过滤
            selectOptions.lotFull = [...selectOptions.lots];
        }
        if (filteredOptions.productrequestnames) {
            selectOptions.productrequestnames = filteredOptions.productrequestnames;
        }
        if (filteredOptions.products) {
            selectOptions.products = filteredOptions.products;
        }
    }
  } catch (err) {
  } finally {
    loading.value = false;
  }
};

// 处理Machine变化事件
const handleMachineChange = () => {
  localStorage.setItem('machine', selectedInfo.eq);
};

// 计算属性：判断是否有存储的Machine值
const hasStoredMachine = computed(() => {
  return localStorage.getItem('machine') !== null;
});

onMounted(async () => {
  await loadDefectCodes();
  await loadInitData();
  await loadGlassList();
  
  // 从URL中获取username参数，并设置为操作员工号
  const username = route.query.username;
  if (username) {
    selectedInfo.operatorId = username;
  }
  
  // 从URL中获取userrole参数
  userrole.value = route.query.userrole || '';
  
  // 添加全局键盘事件监听
  window.addEventListener('keydown', handleKeydown);
});

// 组件销毁时移除事件监听
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  // 清除计时器
  if (digitTimer) {
    clearTimeout(digitTimer);
  }
});
</script>

<style>
/* 禁用触摸时的默认滚动，专用于Canvas区域 */
.touch-none {
  touch-action: none;
}

/* 隐藏滚动条但允许滚动 */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>