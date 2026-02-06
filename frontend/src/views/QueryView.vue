<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <header class="bg-white shadow-sm z-20 border-b border-gray-200 shrink-0">
      <!-- 第一行：系统标识与扩展控制 -->
      <div class="h-8 flex items-center justify-between px-3 border-b border-gray-100 bg-gray-50/50">
        <div class="flex items-center space-x-6">
          <span class="font-bold text-blue-800 text-sm shrink-0"><i class="fa-solid fa-microchip mr-1"></i>MAC System - 历史查询</span>

          <!-- 时间选择器 -->
          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">BeginTime:</span>
              <input 
                  type="datetime-local" 
                  v-model="selectedInfo.beginTime" 
                  class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 focus:border-blue-500 w-48"
              >
          </div>

          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">EndTime:</span>
              <input 
                  type="datetime-local" 
                  v-model="selectedInfo.endTime" 
                  class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 focus:border-blue-500 w-48"
              >
          </div>

          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">InspType:</span>
              <select v-model="selectedInfo.inspectionType" class="bg-white border border-gray-300 rounded text-xs py-1 px-1 focus:border-blue-500 w-32">
                  <option value="">请选择</option>
                  <option v-for="type in ['首检', '过程检', '异常加测', '测膜边']" :key="type" :value="type">{{ type }}</option>
              </select>
          </div>

          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">Inspector:</span>
              <input 
                  type="text" 
                  v-model="selectedInfo.inspector" 
                  placeholder="输入检查人员"
                  class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 focus:border-blue-500 w-40"
              >
          </div>
        </div>

        <div class="text-xs flex items-center space-x-3">
          <span v-if="!hasLayout" class="text-yellow-600 font-bold"><i class="fa-solid fa-exclamation-triangle"></i> 缺Layout</span>
          <span v-else-if="autoSaveStatus" class="text-green-600 font-bold"><i class="fa-solid fa-check"></i> 保存成功</span>
          <div v-else-if="saveMessage" :class="['flex items-center font-bold px-2 py-1 rounded', saveMessageType === 'success' ? 'bg-green-100 text-green-700' : saveMessageType === 'error' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700']">
            <i v-if="saveMessageType === 'success'" class="fa-solid fa-check-circle mr-1"></i>
            <i v-else-if="saveMessageType === 'error'" class="fa-solid fa-exclamation-circle mr-1"></i>
            <span>{{ saveMessage }}</span>
          </div>
          <button @click="showHelpModal = true" class="text-xs text-blue-600 hover:text-blue-800 hover:underline flex items-center space-x-1 cursor-pointer" title="系统操作说明">
            <i class="fa-solid fa-circle-question"></i>
          </button>
        </div>
      </div>

      <!-- 第二行：基础资产信息 -->
      <div class="h-8 flex items-center px-3">
        <div class="flex items-center space-x-4 flex-wrap">


          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">Lot:</span>
              <div class="relative">
                  <div 
                      class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 w-48 min-h-[22px] flex flex-wrap items-center gap-1 focus-within:border-blue-500 transition-all duration-200 cursor-pointer"
                      :style="{
                          maxHeight: showLotDropdown ? 'none' : '22px',
                          overflow: showLotDropdown ? 'visible' : 'hidden'
                      }"
                      @click="() => { closeAllDropdowns(); showLotDropdown = true }"
                  >
                      <span 
                          v-for="lot in selectedInfo.lot" 
                          :key="lot"
                          class="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full flex items-center"
                      >
                          {{ lot }}
                          <button 
                              @click.stop="() => {
                                  const index = selectedInfo.lot.indexOf(lot);
                                  if (index > -1) {
                                      selectedInfo.lot.splice(index, 1);
                                  }
                              }"
                              class="ml-1 text-blue-600 hover:text-blue-900"
                          >
                              ×
                          </button>
                      </span>
                      <input 
                          type="text" 
                          placeholder="输入过滤" 
                          class="flex-1 min-w-[60px] border-0 outline-none text-xs"
                          @focus="() => { closeAllDropdowns(); showLotDropdown = true }"
                          @input="filterLots"
                      >
                  </div>
                  <div v-if="showLotDropdown" class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs">
                      <div v-for="l in filteredLotsOptions" :key="l" class="px-2 py-1 hover:bg-blue-100 cursor-pointer flex items-center" @mousedown.prevent="toggleLot(l)">
                          <input type="checkbox" :checked="selectedInfo.lot.includes(l)" class="mr-1" @click.stop>
                          {{ l }}
                      </div>
                      <div v-if="!filteredLotsOptions || filteredLotsOptions.length === 0" class="px-2 py-1 text-gray-400">暂无数据</div>
                  </div>
              </div>
          </div>

          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">WorkOrder:</span>
              <div class="relative">
                  <div 
                      class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 w-32 min-h-[22px] flex flex-wrap items-center gap-1 focus-within:border-blue-500 transition-all duration-200 cursor-pointer"
                      :style="{
                          maxHeight: showWorkOrderDropdown ? 'none' : '22px',
                          overflow: showWorkOrderDropdown ? 'visible' : 'hidden'
                      }"
                      @click="() => { closeAllDropdowns(); showWorkOrderDropdown = true }"
                  >
                      <span 
                          v-for="wr in selectedInfo.productrequestname" 
                          :key="wr"
                          class="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full flex items-center"
                      >
                          {{ wr }}
                          <button 
                              @click.stop="() => {
                                  const index = selectedInfo.productrequestname.indexOf(wr);
                                  if (index > -1) {
                                      selectedInfo.productrequestname.splice(index, 1);
                                  }
                              }"
                              class="ml-1 text-blue-600 hover:text-blue-900"
                          >
                              ×
                          </button>
                      </span>
                      <input 
                          type="text" 
                          placeholder="输入过滤" 
                          class="flex-1 min-w-[60px] border-0 outline-none text-xs"
                          @focus="() => { closeAllDropdowns(); showWorkOrderDropdown = true }"
                          @input="filterWorkOrders"
                      >
                  </div>
                  <div v-if="showWorkOrderDropdown" class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs">
                      <div v-for="wr in filteredWorkOrdersOptions" :key="wr" class="px-2 py-1 hover:bg-blue-100 cursor-pointer flex items-center" @mousedown.prevent="toggleWorkOrder(wr)">
                          <input type="checkbox" :checked="selectedInfo.productrequestname.includes(wr)" class="mr-1" @click.stop>
                          {{ wr }}
                      </div>
                      <div v-if="!filteredWorkOrdersOptions || filteredWorkOrdersOptions.length === 0" class="px-2 py-1 text-gray-400">暂无数据</div>
                  </div>
              </div>
          </div>

          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">Product:</span>
              <div class="relative">
                  <div 
                      class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 w-44 min-h-[22px] flex flex-wrap items-center gap-1 focus-within:border-blue-500 transition-all duration-200 cursor-pointer"
                      :style="{
                          maxHeight: showProductDropdown ? 'none' : '22px',
                          overflow: showProductDropdown ? 'visible' : 'hidden'
                      }"
                      @click="() => { closeAllDropdowns(); showProductDropdown = true }"
                  >
                      <span 
                          v-for="ps in selectedInfo.product" 
                          :key="ps"
                          class="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full flex items-center"
                      >
                          {{ ps }}
                          <button 
                              @click.stop="() => {
                                  const index = selectedInfo.product.indexOf(ps);
                                  if (index > -1) {
                                      selectedInfo.product.splice(index, 1);
                                  }
                              }"
                              class="ml-1 text-blue-600 hover:text-blue-900"
                          >
                              ×
                          </button>
                      </span>
                      <input 
                          type="text" 
                          placeholder="输入过滤" 
                          class="flex-1 min-w-[60px] border-0 outline-none text-xs"
                          @focus="() => { closeAllDropdowns(); showProductDropdown = true }"
                          @input="filterProducts"
                      >
                  </div>
                  <div v-if="showProductDropdown" class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs">
                      <div v-for="ps in filteredProductsOptions" :key="ps" class="px-2 py-1 hover:bg-blue-100 cursor-pointer flex items-center" @mousedown.prevent="toggleProduct(ps)">
                          <input type="checkbox" :checked="selectedInfo.product.includes(ps)" class="mr-1" @click.stop>
                          {{ ps }}
                      </div>
                      <div v-if="!filteredProductsOptions || filteredProductsOptions.length === 0" class="px-2 py-1 text-gray-400">暂无数据</div>
                  </div>
              </div>
          </div>
          
          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">OPER:</span>
              <div class="relative">
                  <div 
                      class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 w-20 min-h-[22px] flex flex-wrap items-center gap-1 focus-within:border-blue-500 transition-all duration-200 cursor-pointer"
                      :style="{
                          maxHeight: showOperDropdown ? 'none' : '22px',
                          overflow: showOperDropdown ? 'visible' : 'hidden'
                      }"
                      @click="() => { closeAllDropdowns(); showOperDropdown = true }"
                  >
                      <span 
                          v-for="op in selectedInfo.processOperationName" 
                          :key="op"
                          class="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full flex items-center"
                      >
                          {{ op }}
                          <button 
                              @click.stop="() => {
                                  const index = selectedInfo.processOperationName.indexOf(op);
                                  if (index > -1) {
                                      selectedInfo.processOperationName.splice(index, 1);
                                  }
                              }"
                              class="ml-1 text-blue-600 hover:text-blue-900"
                          >
                              ×
                          </button>
                      </span>
                      <input 
                          type="text" 
                          placeholder="输入过滤" 
                          class="flex-1 min-w-[60px] border-0 outline-none text-xs"
                          @focus="() => { closeAllDropdowns(); showOperDropdown = true }"
                          @input="filterOpers"
                      >
                  </div>
                  <div v-if="showOperDropdown" class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs">
                      <div v-for="op in filteredOperOptions" :key="op" class="px-2 py-1 hover:bg-blue-100 cursor-pointer flex items-center" @mousedown.prevent="toggleOper(op)">
                          <input type="checkbox" :checked="selectedInfo.processOperationName.includes(op)" class="mr-1" @click.stop>
                          {{ op }}
                      </div>
                      <div v-if="!filteredOperOptions || filteredOperOptions.length === 0" class="px-2 py-1 text-gray-400">暂无数据</div>
                  </div>
              </div>
          </div>

          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">Machine:</span>
              <div class="relative">
                  <div 
                      class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 w-40 min-h-[22px] flex flex-wrap items-center gap-1 focus-within:border-blue-500 transition-all duration-200 cursor-pointer"
                      :style="{
                          maxHeight: showMachineDropdown ? 'none' : '22px',
                          overflow: showMachineDropdown ? 'visible' : 'hidden'
                      }"
                      @click="() => { closeAllDropdowns(); showMachineDropdown = true }"
                  >
                      <span 
                          v-for="eq in selectedInfo.eq" 
                          :key="eq"
                          class="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full flex items-center"
                      >
                          {{ eq }}
                          <button 
                              @click.stop="() => {
                                  const index = selectedInfo.eq.indexOf(eq);
                                  if (index > -1) {
                                      selectedInfo.eq.splice(index, 1);
                                  }
                              }"
                              class="ml-1 text-blue-600 hover:text-blue-900"
                          >
                              ×
                          </button>
                      </span>
                      <input 
                          type="text" 
                          placeholder="输入过滤" 
                          class="flex-1 min-w-[60px] border-0 outline-none text-xs"
                          @focus="() => { closeAllDropdowns(); showMachineDropdown = true }"
                          @input="filterMachines"
                      >
                  </div>
                  <div v-if="showMachineDropdown" class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs">
                      <div v-for="eq in filteredMachineOptions" :key="eq" class="px-2 py-1 hover:bg-blue-100 cursor-pointer flex items-center" @mousedown.prevent="toggleMachine(eq)">
                          <input type="checkbox" :checked="selectedInfo.eq.includes(eq)" class="mr-1" @click.stop>
                          {{ eq }}
                      </div>
                      <div v-if="!filteredMachineOptions || filteredMachineOptions.length === 0" class="px-2 py-1 text-gray-400">暂无数据</div>
                  </div>
              </div>
          </div>
          
          <div class="flex items-center text-xs text-gray-700">
              <span class="mr-1 font-medium">Code:</span>
              <div class="relative">
                  <div 
                      class="bg-white border border-gray-300 rounded text-xs py-0.5 px-1 w-40 min-h-[22px] flex flex-wrap items-center gap-1 focus-within:border-blue-500 transition-all duration-200 cursor-pointer"
                      :style="{
                          maxHeight: showDefectCodeDropdown ? 'none' : '22px',
                          overflow: showDefectCodeDropdown ? 'visible' : 'hidden'
                      }"
                      @click="() => { closeAllDropdowns(); showDefectCodeDropdown = true }"
                  >
                      <!-- 已选择的缺陷代码标签 -->
                      <span 
                          v-for="code in selectedInfo.defectCode" 
                          :key="code"
                          class="bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full flex items-center"
                      >
                          {{ code }}
                          <button 
                              @click.stop="() => {
                                  const index = selectedInfo.defectCode.indexOf(code);
                                  if (index > -1) {
                                      selectedInfo.defectCode.splice(index, 1);
                                  }
                              }"
                              class="ml-1 text-blue-600 hover:text-blue-900"
                          >
                              ×
                          </button>
                      </span>
                      <!-- 过滤输入框 -->
                      <input 
                          type="text" 
                          placeholder="输入过滤" 
                          class="flex-1 min-w-[60px] border-0 outline-none text-xs"
                          @focus="() => { closeAllDropdowns(); showDefectCodeDropdown = true }"
                          @input="filterDefectCodes"
                          ref="defectCodeInput"
                      >
                  </div>
                  <div v-if="showDefectCodeDropdown" class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded shadow-lg max-h-48 overflow-y-auto text-xs">
                      <div v-for="code in filteredDefectCodesOptions" :key="code" class="px-2 py-1 hover:bg-blue-100 cursor-pointer flex items-center" @mousedown.prevent="toggleDefectCode(code)">
                          <input type="checkbox" :checked="selectedInfo.defectCode.includes(code)" class="mr-1" @click.stop>
                          {{ code }}
                      </div>
                      <div v-if="!filteredDefectCodesOptions || filteredDefectCodesOptions.length === 0" class="px-2 py-1 text-gray-400">暂无数据</div>
                  </div>
              </div>
          </div>
          
          <!-- 查询按钮 -->
          <div class="flex items-center">
            <button 
              @click="handleQuery" 
              :class="['px-3 py-1 rounded text-xs font-medium transition-colors ml-2',
                'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer']"
            >
              查询
            </button>
            <button 
              @click="handleReset" 
              :class="['px-3 py-1 rounded text-xs font-medium transition-colors ml-2',
                'bg-gray-500 text-white hover:bg-gray-600 cursor-pointer']"
            >
              重置
            </button>
          </div>
        </div>
      </div>
    </header>




    <main class="flex-1 flex overflow-hidden">
      
      <aside class="w-64 bg-white flex flex-col border-r border-gray-200 z-10 shadow-md shrink-0">
        <div class="h-1/2 flex flex-col border-b border-gray-200">
          <div class="p-2 bg-gray-50 border-b flex justify-between items-center">
            <h3 class="font-bold text-gray-700 text-xs">Glass ID</h3>
            <span class="text-[10px] bg-gray-200 px-1.5 rounded">{{ glassList.reduce((total, group) => total + group.glasses.length, 0) }}</span>
          </div>
          <div class="flex-1 overflow-y-auto p-1 space-y-0.5 scrollbar-hide">
            <!-- 按产品型号+站点分组展示 -->
            <div v-for="group in glassList" :key="group.groupId" class="space-y-0.5">
              <!-- 分组标题 -->
              <div 
                @click="toggleGroup(group.groupId)"
                :class="['px-3 py-2 rounded text-xs font-medium flex justify-between items-center cursor-pointer transition-colors',
                  'bg-gray-100 text-gray-700 hover:bg-gray-200']"
              >
                <div class="flex items-center">
                  <i :class="['fa-solid', expandedGroups.has(group.groupId) ? 'fa-chevron-down' : 'fa-chevron-right', 'mr-1 text-[10px]']"></i>
                  <span>{{ group.product }}-{{ group.processoperationname }} ({{ group.glasses.length }})</span>
                </div>
              </div>
              <!-- 玻璃列表 -->
              <div v-if="expandedGroups.has(group.groupId)" class="ml-3 space-y-0.5 border-l-2 border-gray-200 pl-2">
                <div 
                  v-for="glass in group.glasses" 
                  :key="glass.id"
                  @click="switchGlass(glass.id)"
                  :class="['px-3 py-2 rounded text-xs font-medium flex justify-between items-center cursor-pointer transition-colors',
                    currentGlassId === glass.id ? 'bg-blue-600 text-white' : 'hover:bg-gray-100 text-gray-600']"
                  :ref="el => { if (el) glassRefs[glass.id] = el }"
                >
                  <span>{{ glass.id }}</span>
                  <span v-if="dbData[glass.id] && dbData[glass.id].length > 0" class="w-1.5 h-1.5 rounded-full bg-yellow-400 shadow-sm"></span>
                </div>
              </div>
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
              :class="['w-full py-2.5 px-3 rounded flex items-center text-xs font-bold border transition-all',
                selectedCode?.id === code.id 
                  ? 'border-blue-500 bg-white shadow-md ring-1 ring-blue-500 text-blue-700 transform scale-[1.02]' 
                  : 'border-transparent bg-white text-gray-600 hover:bg-gray-100',
                'cursor-pointer']"
              :ref="el => { if (el) el.dataset.levelno = code.levelno }"
            >
              <span class="w-4 text-center mr-2 text-gray-600">{{ code.levelno }}</span>
              <div class="w-3 h-3 rounded-full mr-2 shadow-sm" :style="{background: code.color}"></div>
              <span class="flex-1 text-left">
                {{ code.name }}
                <i v-if="code.hasRemark" class="fa-solid fa-pen-to-square text-[10px] text-red-500 ml-1" title="需要填写备注"></i>
              </span>
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
          :selected-product-id="currentProductId"
          :readonly="isReadonly"
          :current-glass-id="currentGlassId"
          :is-historical="true"
          :selected-defect-uuid="selectedDefectUuid"
          @add-defect="addDefect"
          @layout-status-change="hasLayout = $event"
        />
      </section>

      <aside class="w-64 bg-white border-l border-gray-200 flex flex-col z-10 shrink-0">
        <div class="p-2 border-b bg-gray-50 flex justify-between items-center h-10">
          <div class="flex items-center space-x-2">
            <h3 class="font-bold text-gray-800 text-xs">Records</h3>
            <span v-if="isReadonly" class="text-[12px] bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">历史查询</span>
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
            <span class="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 shadow-sm">{{ visibleDefects.length }}</span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto scrollbar-hide bg-white">
          <div 
              v-for="record in visibleDefects" 
              :key="record.uuid"
              class="border-b border-gray-100 hover:bg-gray-50 transition-colors"
              :title="getFullDefectInfo(record)"
            >
              <div class="flex items-center px-3 py-2 cursor-pointer group" @click="!isReadonly && toggleEdit(record); selectDefect(record.uuid)">
                <div class="w-2 h-2 rounded-full mr-2 shrink-0 shadow-sm" :style="{background: getCodeColor(record.code)}"></div>
              
              <div class="flex-1 min-w-0 flex flex-col justify-center">
                <div class="flex items-center text-xs">
                  <span class="font-bold text-gray-700 mr-1">{{ record.codeName }}</span>
                  <span class="font-mono text-gray-500 font-bold truncate">
                    : P{{ formatPanelIds(record) }}
                  </span> 
                  
                  <i v-if="record.isSymmetry" class="fa-solid fa-clone text-[10px] text-orange-400 ml-1" title="自动对称点"></i>
                  <i v-if="defectCodes.find(c => c.id === record.code)?.hasRemark && !record.remark" class="fa-solid fa-pen-to-square text-[10px] text-red-500 ml-1 animate-pulse" title="需要填写备注"></i>
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

            <div v-if="record.isEditing || record.remark" :data-uuid="record.uuid" class="px-3 pb-2 bg-gray-50/50">
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
            历史数据查询系统操作说明
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
                MAC宏观检查系统历史数据查询页面，用于查看历史缺陷检测数据。
              </p>
            </section>
            
            <section>
              <h4 class="text-md font-semibold text-gray-800 mb-2 flex items-center">
                <i class="fa-solid fa-gear text-blue-600 mr-2"></i>
                主要功能
              </h4>
              <ul class="list-disc pl-5 text-sm text-gray-700 space-y-1">
                <li>历史玻璃缺陷数据查询与展示</li>
                <li>按时间段查询,支持多产品,多站点等混合查询</li>
                <li>多种缺陷类型支持（点缺、线缺、曲线、面缺）</li>
                <li>缺陷代码分类与过滤</li>
                <li>缺陷数据可视化展示</li>
                <li>支持选择缺陷高亮显示</li>
                <li>支持键盘快捷键:上下箭头或w/s切换glass, 数字定位缺陷代码</li>
              </ul>
            </section>
            
            <section>
              <h4 class="text-md font-semibold text-gray-800 mb-2 flex items-center">
                <i class="fa-solid fa-keyboard text-blue-600 mr-2"></i>
                操作指南
              </h4>
              <div class="space-y-4">
                <div>
                  <h5 class="text-sm font-medium text-gray-700 mb-1">查询参数设置</h5>
                  <p class="text-xs text-gray-600 pl-4 mb-1">在开始查询前，请完成以下参数设置：</p>
                  <ul class="list-disc pl-8 text-xs text-gray-600 space-y-1">
                    <li><span class="font-medium">开始时间,结束时间(必选)</span>：选择检测时段, 默认昨日8:30~今日8:30</li>
                    <li><span class="font-medium">其他参数(可选)</span>：下拉选择或输入进行查询,支持多选</li>
                  </ul>
                </div>
                <div>
                  <h5 class="text-sm font-medium text-gray-700 mb-1">查看缺陷</h5>
                  <p class="text-xs text-gray-600 pl-4">1、在Glass列表中, 选择GlassID,可通过快捷键切换</p>
                  <p class="text-xs text-gray-600 pl-4">2、选择需要查看的缺陷Code,配合是否叠加进行过滤</p>
                  <p class="text-xs text-gray-600 pl-4">3、在右侧缺陷记录列表中查看详细信息, 点击缺陷记录,在画布中高亮此缺陷</p>
                </div>
              </div>
            </section>
            
            <section>
              <h4 class="text-md font-semibold text-gray-800 mb-2 flex items-center">
                <i class="fa-solid fa-exclamation-triangle text-blue-600 mr-2"></i>
                注意事项
              </h4>
              <ul class="list-disc pl-5 text-sm text-gray-700 space-y-1">
                <li>历史数据查询页面为只读模式，无法进行缺陷编辑</li>
                <li>如果Layout未加载或图形错误，请联系TEST组在ADC系统导入或修正</li>
                <li>如果Mask Shot边缘线未加载或错误，请联系PHT在TAQ1831报表中查询并修正</li>
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
import api, { getInitData, getGlassList, getReasonCodeList, getDefects, saveDefectRecord, deleteDefectRecord, getRelatedInfoByCstOrLot, filterOptionsByOper, getMachineByIp, getDefectsByLot, getProcessOperationsByLot } from '../services/api'

// 创建路由实例，用于获取URL参数
const route = useRoute()

// --- 角色控制 --- 
// 从URL获取userrole参数
const userrole = ref(route.query.userrole || '')
// 计算属性：判断是否为readonly角色
const isReadonly = computed(() => true) // 历史查询页面始终为只读

// --- 1. 基础数据 ---

// 顶部下拉选择数据
const selectOptions = reactive({
    products: [], 
    lots: [],
    lotFull: [], // 存储完整的LOT数据，用于过滤
    eqs: [],
    processOperations: [],
    productRequests: [],
    productSpecs: [],
    defectCodes: []
});

// 计算默认时间范围
const formatDateTimeLocal = (date) => {
    // 手动格式化日期时间为本地时间的YYYY-MM-DDTHH:mm格式
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
};

const getDefaultBeginTime = () => {
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    yesterday.setHours(8, 30, 0, 0);
    return formatDateTimeLocal(yesterday);
};

const getDefaultEndTime = () => {
    const now = new Date();
    now.setHours(8, 30, 0, 0);
    return formatDateTimeLocal(now);
};

const selectedInfo = reactive({
    product: [],
    lot: [],
    eq: [],
    processOperationName: [],
    productrequestname: [],
    defectCode: [],
    beginTime: getDefaultBeginTime(),
    endTime: getDefaultEndTime(),
    operatorId: '',
    availableInspectors: [],
    inspectionType: '',
    inspector: '',
    selectedInspectors: []
});

// Unicode Hex 解码函数 (针对 [5f20] 这种格式)
const decodeUnicodeFromHex = (hexStr) => {
  try {
    let result = '';
    // 每4位十六进制转换为1个字符 (Unicode)
    for (let i = 0; i < hexStr.length; i += 4) {
      const charCode = parseInt(hexStr.substr(i, 4), 16);
      if (!isNaN(charCode)) {
        result += String.fromCharCode(charCode);
      }
    }
    return result;
  } catch (e) {
    console.error('Unicode解码失败:', e);
    return '';
  }
};

const parseInspectorNames = (inspectorParam) => {
  if (!inspectorParam) return [];
  
  // 先进行 URL 解码
  let decodedParam = inspectorParam;
  try {
    decodedParam = decodeURIComponent(inspectorParam);
  } catch (e) {
    console.warn('URL 解码失败,使用原始参数:', e);
  }
  
  // 分割多个 Inspector (逗号分隔)
  const names = decodedParam.split(',');
  
  // 解析每个 Inspector 的 Unicode 编码
  return names.map(name => {
    const hexStr = name.replace(/\[|\]/g, '');
    return decodeUnicodeFromHex(hexStr);
  }).filter(name => name);
};

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
const showLotDropdown = ref(false); // 控制Lot下拉列表显示
const showWorkOrderDropdown = ref(false); // 控制WorkOrder下拉列表显示
const showProductDropdown = ref(false); // 控制Product下拉列表显示
const showOperDropdown = ref(false); // 控制OPER下拉列表显示
const showMachineDropdown = ref(false); // 控制Machine下拉列表显示
const showDefectCodeDropdown = ref(false); // 控制DefectCode下拉列表显示
const hasLayout = ref(true); // 新增：控制layout状态，默认有layout
const showHelpModal = ref(false); // 新增：控制帮助模态框显示
const showInspectorDropdown = ref(false); // 控制Inspector下拉菜单显示
const saveMessage = ref('');
const saveMessageType = ref('success');
const expandedGroups = ref(new Set()); // 控制展开的分组列表
const currentProduct = ref(''); // 新增：存储当前Glass对应的产品型号
const glassRefs = ref({}); // 存储glass元素引用，用于滚动定位
const selectedDefectUuid = ref(''); // 新增：存储当前选中的缺陷UUID
const defectCodeInput = ref(null); // 缺陷代码输入框引用
const defectCodeFilter = ref(''); // 缺陷代码过滤输入
const lotFilter = ref(''); // Lot 过滤输入
const workOrderFilter = ref(''); // WorkOrder 过滤输入
const productFilter = ref(''); // Product 过滤输入
const operFilter = ref(''); // OPER 过滤输入
const machineFilter = ref(''); // Machine 过滤输入

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

// 切换Inspector选择
const toggleInspector = (inspector) => {
  const index = selectedInfo.selectedInspectors.indexOf(inspector);
  if (index > -1) {
    // 移除选择
    selectedInfo.selectedInspectors.splice(index, 1);
  } else {
    // 添加选择
    selectedInfo.selectedInspectors.push(inspector);
  }
};

// 切换Machine选择
const toggleMachine = (machine) => {
  const index = selectedInfo.eq.indexOf(machine);
  if (index > -1) {
    // 移除选择
    selectedInfo.eq.splice(index, 1);
  } else {
    // 添加选择
    selectedInfo.eq.push(machine);
  }
};

// 切换Lot选择
const toggleLot = (lot) => {
  const index = selectedInfo.lot.indexOf(lot);
  if (index > -1) {
    // 移除选择
    selectedInfo.lot.splice(index, 1);
  } else {
    // 添加选择
    selectedInfo.lot.push(lot);
  }
};

// 切换WorkOrder选择
const toggleWorkOrder = (workOrder) => {
  const index = selectedInfo.productrequestname.indexOf(workOrder);
  if (index > -1) {
    // 移除选择
    selectedInfo.productrequestname.splice(index, 1);
  } else {
    // 添加选择
    selectedInfo.productrequestname.push(workOrder);
  }
};

// 切换Product选择
const toggleProduct = (product) => {
  const index = selectedInfo.product.indexOf(product);
  if (index > -1) {
    // 移除选择
    selectedInfo.product.splice(index, 1);
  } else {
    // 添加选择
    selectedInfo.product.push(product);
  }
};

// 切换Oper选择
const toggleOper = (oper) => {
  const index = selectedInfo.processOperationName.indexOf(oper);
  if (index > -1) {
    // 移除选择
    selectedInfo.processOperationName.splice(index, 1);
  } else {
    // 添加选择
    selectedInfo.processOperationName.push(oper);
  }
};

// 切换DefectCode选择
const toggleDefectCode = (code) => {
  const index = selectedInfo.defectCode.indexOf(code);
  if (index > -1) {
    // 移除选择
    selectedInfo.defectCode.splice(index, 1);
  } else {
    // 添加选择
    selectedInfo.defectCode.push(code);
  }
};

// 过滤缺陷代码
const filterDefectCodes = (event) => {
  defectCodeFilter.value = event.target.value;
};

// 过滤 Lot
const filterLots = (event) => {
  lotFilter.value = event.target.value;
};

// 过滤 WorkOrder
const filterWorkOrders = (event) => {
  workOrderFilter.value = event.target.value;
};

// 过滤 Product
const filterProducts = (event) => {
  productFilter.value = event.target.value;
};

// 过滤 OPER
const filterOpers = (event) => {
  operFilter.value = event.target.value;
};

// 过滤 Machine
const filterMachines = (event) => {
  machineFilter.value = event.target.value;
};

// 计算过滤并排序后的缺陷代码选项
const filteredDefectCodesOptions = computed(() => {
  let codes = [...selectOptions.defectCodes];
  
  // 过滤
  if (defectCodeFilter.value) {
    const filter = defectCodeFilter.value.toLowerCase();
    codes = codes.filter(code => code.toLowerCase().includes(filter));
  }
  
  // 排序
  codes.sort((a, b) => a.localeCompare(b));
  
  return codes;
});

// 计算过滤并排序后的 Lot 选项
const filteredLotsOptions = computed(() => {
  let lots = [...selectOptions.lots];
  
  // 过滤
  if (lotFilter.value) {
    const filter = lotFilter.value.toLowerCase();
    lots = lots.filter(lot => lot.toLowerCase().includes(filter));
  }
  
  // 排序
  lots.sort((a, b) => a.localeCompare(b));
  
  return lots;
});

// 计算过滤并排序后的 WorkOrder 选项
const filteredWorkOrdersOptions = computed(() => {
  let workOrders = [...selectOptions.productRequests];
  
  // 过滤
  if (workOrderFilter.value) {
    const filter = workOrderFilter.value.toLowerCase();
    workOrders = workOrders.filter(workOrder => workOrder.toLowerCase().includes(filter));
  }
  
  // 排序
  workOrders.sort((a, b) => a.localeCompare(b));
  
  return workOrders;
});

// 计算过滤并排序后的 Product 选项
const filteredProductsOptions = computed(() => {
  let products = [...selectOptions.productSpecs];
  
  // 过滤
  if (productFilter.value) {
    const filter = productFilter.value.toLowerCase();
    products = products.filter(product => product.toLowerCase().includes(filter));
  }
  
  // 排序
  products.sort((a, b) => a.localeCompare(b));
  
  return products;
});

// 计算过滤并排序后的 OPER 选项
const filteredOperOptions = computed(() => {
  let opers = [...selectOptions.processOperations];
  
  // 过滤
  if (operFilter.value) {
    const filter = operFilter.value.toLowerCase();
    opers = opers.filter(oper => oper.toLowerCase().includes(filter));
  }
  
  // 排序
  opers.sort((a, b) => a.localeCompare(b));
  
  return opers;
});

// 计算过滤并排序后的 Machine 选项
const filteredMachineOptions = computed(() => {
  let machines = [...selectOptions.eqs];
  
  // 过滤
  if (machineFilter.value) {
    const filter = machineFilter.value.toLowerCase();
    machines = machines.filter(machine => machine.toLowerCase().includes(filter));
  }
  
  // 排序
  machines.sort((a, b) => a.localeCompare(b));
  
  return machines;
});



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
  let info = `UUID: ${record.uuid}\n`
  info += `检查时间: ${record.created_at || '-'}\n`
  info += `检查类型: ${record.inspection_type || '-'}\n`
  info += `检查人: ${record.Inspector || '-'}\n`
  info += `设备: ${record.machinename || '-'}\n`
  info += `站点: ${record.processoperationname || '-'}\n`
  info += `产品: ${record.productspecname || '-'}\n`
  info += `LOT: ${record.lotname || '-'}\n`
  info += `glassId: ${record.glassId || '-'}\n`
  info += `panelIds: ${record.panelIds?.join(',') || record.panelId || '-'}\n`
  info += `code: ${record.code || '-'}\n`
  
  // 处理不同类型的缺陷，显示完整坐标
  if (record.type === 'LINE' || record.type === 'line') {
    info += `缺陷类型: ${record.type}\n`
    info += `方向: ${record.direction === 'HORIZONTAL' ? '水平' : '垂直'}\n`
    info += `坐标: ${record.direction === 'HORIZONTAL' ? `${formatCoord(record.x)}, -` : `- , ${formatCoord(record.y)}`}\n`
    info += `路径: ${record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(' → ')}`
  } else if (record.type === 'REGION' || record.type === 'region') {
    info += `缺陷类型: ${record.type}\n`
    info += `坐标: (${record.x !== null ? formatCoord(record.x) : '-'}, ${record.y !== null ? formatCoord(record.y) : '-'})\n`
    info += `路径点数量: ${record.path.length}个\n`
    info += `路径: ${record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(' → ')}`
  } else if (record.type === 'curve' || record.type === 'CURVE') {
    info += `缺陷类型: ${record.type}\n`
    info += `坐标: (${record.x !== null ? formatCoord(record.x) : '-'}, ${record.y !== null ? formatCoord(record.y) : '-'})\n`
    info += `路径点数量: ${record.path.length}个\n`
    info += `路径: ${record.path.map(p => `(${formatCoord(p.x)},${formatCoord(p.y)})`).join(' → ')}`
  } else {
    info += `缺陷类型: ${record.type}\n`
    info += `坐标: (${record.x !== null ? formatCoord(record.x) : '-'}, ${record.y !== null ? formatCoord(record.y) : '-'})`
  }
  
  return info
};

// 检查是否存在"正常"标记
const hasNormalStatus = computed(() => {
  return currentDefects.value.some(d => d.code === '正常');
});


// 检查是否有未填写备注的记录
const checkNeedRemark = () => {
  if (needRemarkRecords.value.length > 0) {
    showMessage('请先填写备注', 'error');
    return false;
  }
  return true;
};

// 计算属性：获取当前产品型号ID
const currentProductId = computed(() => {
  // 优先使用 currentProduct，其次使用 selectedInfo.product 数组的第一个元素
  if (currentProduct.value) {
    return currentProduct.value;
  } else if (selectedInfo.product && selectedInfo.product.length > 0) {
    return selectedInfo.product[0];
  }
  return '';
});

// 计算属性：获取可见的缺陷（过滤掉“正常”标记）
const visibleDefects = computed(() => {
  const filtered = currentDefects.value.filter(d => d.code !== '正常');
  if (showAllDefects.value) {
    return filtered;
  } else {
    return filtered.filter(d => d.code === selectedCode.value.id);
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

// 辅助函数：将分组的glass列表扁平化为一维数组
const getAllGlasses = () => {
  return glassList.value.flatMap(group => group.glasses);
};

// 辅助函数：根据glass ID查找所属分组
const findGlassGroup = (glassId) => {
  for (const group of glassList.value) {
    const glass = group.glasses.find(g => g.id === glassId);
    if (glass) {
      return group;
    }
  }
  return null;
};

// 导航到上一张或下一张glass
const navigateGlass = (direction) => {
  const allGlasses = getAllGlasses();
  if (allGlasses.length === 0) return;
  
  let currentIndex = -1;
  if (currentGlassId.value) {
    currentIndex = allGlasses.findIndex(glass => glass.id === currentGlassId.value);
  }
  
  let nextIndex = -1;
  if (direction === 'next') {
    // 到底就结束，不要循环
    if (currentIndex >= allGlasses.length - 1) return;
    nextIndex = currentIndex + 1;
  } else if (direction === 'prev') {
    // 到顶就结束，不要循环
    if (currentIndex <= 0) return;
    nextIndex = currentIndex - 1;
  }
  
  if (nextIndex >= 0) {
    const targetGlass = allGlasses[nextIndex];
    const targetGroup = findGlassGroup(targetGlass.id);
    
    // 确保目标分组是展开的
    if (targetGroup) {
      expandedGroups.value.add(targetGroup.groupId);
    }
    
    // 切换到目标glass
    switchGlass(targetGlass.id);
  }
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

// 切换分组展开/折叠状态
const toggleGroup = (groupId) => {
  if (expandedGroups.value.has(groupId)) {
    expandedGroups.value.delete(groupId);
  } else {
    expandedGroups.value.add(groupId);
  }
};

// 切换Glass
const switchGlass = async (id) => {
  // 查找当前glass所属的产品型号
  let foundProduct = '';
  for (const group of glassList.value) {
    const glass = group.glasses.find(g => g.id === id);
    if (glass) {
      foundProduct = glass.product;
      break;
    }
  }
  
  // 保存当前产品型号用于比较
  const previousProduct = currentProduct.value;
  
  // 更新currentProduct和currentGlassId
  currentProduct.value = foundProduct;
  currentGlassId.value = id;
  
  // 无论是否为只读模式，都调用loadGlassDefects函数获取最新数据
  await loadGlassDefects(id, true, selectedInfo.processOperationName);
  defectiveGlasses.value = getDefectiveGlasses();
  
  // 滚动到选中的glass，确保其在可见窗口内
  nextTick(() => {
    const glassElement = glassRefs.value[id];
    if (glassElement) {
      glassElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
};

// 加载Glass缺陷
const loadGlassDefects = async (glassId, isCurrentGlass = true, processOperationName = null) => {
  try {
    // 验证时间参数
    if (!selectedInfo.beginTime || !selectedInfo.endTime) {
      showMessage('请选择有效的时间范围', 'error');
      return [];
    }
    
    // 验证开始时间不能晚于结束时间
    if (new Date(selectedInfo.beginTime) > new Date(selectedInfo.endTime)) {
      showMessage('开始时间不能晚于结束时间', 'error');
      return [];
    }
    
    // 使用传入的processOperationName或从selectedInfo中获取
    const opName = processOperationName || selectedInfo.processOperationName;
    
    // 直接调用API获取数据
    // 只有当processOperationName有效时，才调用getDefects
    let defects = [];
    if (opName) {
      defects = await getDefects(glassId, opName, true, selectedInfo.beginTime, selectedInfo.endTime, selectedInfo.eq, selectedInfo.defectCode); // 历史数据查询，添加时间参数和过滤参数
    }
    
    if (isCurrentGlass) {
      currentDefects.value = defects;
    }
    dbData.value[glassId] = defects;
    return defects;
  } catch (err) {
    const emptyDefects = [];
    if (isCurrentGlass) {
      currentDefects.value = emptyDefects;
    }
    dbData.value[glassId] = emptyDefects;
    return emptyDefects;
  }
};

// 切换缺陷代码
const switchCode = (code) => {
  selectedCode.value = code;
};

// 添加缺陷 - 历史查询页面不支持添加缺陷
const addDefect = async (rec) => {
  // 历史查询页面不支持添加缺陷
  showMessage('历史查询页面不支持添加缺陷', 'error');
};

// 切换编辑状态 - 历史查询页面不支持编辑
const toggleEdit = (rec) => {
  // 历史查询页面不支持编辑
  showMessage('历史查询页面不支持编辑缺陷', 'error');
};

// 保存备注 - 历史查询页面不支持保存备注
const saveRemark = (rec) => {
  // 历史查询页面不支持保存备注
  showMessage('历史查询页面不支持保存备注', 'error');
};

// 全局键盘事件处理
const handleKeydown = (e) => {
  // 如果有活跃输入框，不处理
  if (isInputActive.value) return;
  
  // 如果是数字键（0-9）
  if (/^\d$/.test(e.key)) {
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
  } else if (e.key === 's' || e.key === 'ArrowDown') {
    // 阻止默认行为
    e.preventDefault();
    // 下一张glass
    navigateGlass('next');
  } else if (e.key === 'w' || e.key === 'ArrowUp') {
    // 阻止默认行为
    e.preventDefault();
    // 上一张glass
    navigateGlass('prev');
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

// 隐藏下拉菜单
const hideDropdown = (type) => {
  if (type === 'lot') {
    showLotDropdown.value = false;
  } else if (type === 'workorder') {
    showWorkOrderDropdown.value = false;
  } else if (type === 'product') {
    showProductDropdown.value = false;
  } else if (type === 'oper') {
    showOperDropdown.value = false;
  } else if (type === 'machine') {
    showMachineDropdown.value = false;
  } else if (type === 'defectCode') {
    showDefectCodeDropdown.value = false;
  }
};

// 处理输入框失焦
const handleBlur = (type) => {
  // 延迟隐藏下拉菜单，以便点击下拉项可以触发事件
  setTimeout(() => {
    hideDropdown(type);
  }, 200);
};

// 加载下拉数据
const loadDropdownData = async (type) => {
  if (type === 'lot') {
    showLotDropdown.value = !showLotDropdown.value;
  }
};

// 过滤下拉选项
const filterOptionsByInput = (type, inputValue) => {
  if (type === 'lot') {
    const filteredList = selectOptions.lotFull.filter(item => 
      item.toLowerCase().includes(inputValue.toLowerCase())
    );
    selectOptions.lots = filteredList;
  }
};

// 过滤下拉选项
const filterDropdownOptions = (type) => {
  if (type === 'lot') {
    filterOptionsByInput(type, selectedInfo.lot);
  }
};

// 选择下拉选项
const selectOption = (type, value) => {
  if (type === 'lot') {
    // 如果value已经在数组中，移除它，否则添加它
    const index = selectedInfo.lot.indexOf(value);
    if (index > -1) {
      selectedInfo.lot.splice(index, 1);
    } else {
      selectedInfo.lot.push(value);
    }
  }
};

// Lot变化处理
const onLotChange = async () => {
  // 调用获取玻璃列表的方法
  await getGlassListByHistorical();
};

// 处理时间变化
const handleTimeChange = async () => {
  // 获取新的历史数据选项
  await getHistoricalOptions();
};

// 监听时间变化
watch([() => selectedInfo.beginTime, () => selectedInfo.endTime], () => {
  handleTimeChange();
});

// 处理Machine变化
const handleMachineChange = async () => {
  // 历史查询页面处理逻辑
  await getGlassListByHistorical();
};

// 处理WorkOrder变化
const handleWorkOrderChange = async () => {
  // 历史查询页面处理逻辑
  await getGlassListByHistorical();
};

// 查询按钮点击事件
const handleQuery = async () => {
  await getGlassListByHistorical();
};

// 重置按钮点击事件
const handleReset = () => {
  // 重置查询参数
  selectedInfo.product = [];
  selectedInfo.lot = [];
  selectedInfo.eq = [];
  selectedInfo.processOperationName = [];
  selectedInfo.productrequestname = [];
  selectedInfo.defectCode = [];
  selectedInfo.beginTime = getDefaultBeginTime();
  selectedInfo.endTime = getDefaultEndTime();
  selectedInfo.inspectionType = '';
  selectedInfo.inspector = '';
  
  // 重置过滤输入
  lotFilter.value = '';
  workOrderFilter.value = '';
  productFilter.value = '';
  operFilter.value = '';
  machineFilter.value = '';
  defectCodeFilter.value = '';
  
  // 显示操作反馈
  showMessage('已重置所有参数');
};

// 处理Product变化
const handleProductChange = async () => {
  // 历史查询页面处理逻辑
  await getGlassListByHistorical();
};

// 处理Oper变化
const handleOperChange = async () => {
  // 历史查询页面处理逻辑
  await getGlassListByHistorical();
};

// 从指定Glass复制缺陷到当前Glass - 历史查询页面不支持
const copyDefectsFromGlass = async (sourceGlassId) => {
  // 历史查询页面不支持复制缺陷
  showMessage('历史查询页面不支持复制缺陷', 'error');
};

// 保存“无缺陷/正常”标记 - 历史查询页面不支持
const saveNormalRecord = async () => {
  // 历史查询页面不支持保存记录
  showMessage('历史查询页面不支持保存记录', 'error');
};

// 切换无缺陷状态 - 历史查询页面不支持
const toggleNoDefectStatus = async () => {
  // 历史查询页面不支持切换无缺陷状态
  showMessage('历史查询页面不支持此操作', 'error');
};

// 选择缺陷，用于高亮显示和定位defectcode
const selectDefect = (uuid) => {
  selectedDefectUuid.value = uuid;
  // 查找对应的缺陷记录
  const defect = currentDefects.value.find(d => d.uuid === uuid);
  if (defect) {
    // 查找对应的缺陷代码
    const code = defectCodes.value.find(c => c.id === defect.code);
    if (code) {
      // 切换到对应的缺陷代码
      switchCode(code);
      // 滚动到对应的缺陷代码位置
      scrollToDefect(code.levelno);
    }
  }
};

// 移除缺陷 - 历史查询页面不支持删除缺陷
const removeDefect = async (uuid) => {
  // 历史查询页面不支持删除缺陷
  showMessage('历史查询页面不支持删除缺陷', 'error');
};

// 触发自动保存 - 历史查询页面不支持保存
const triggerAutoSave = () => {
  // 历史查询页面不支持自动保存
};

// 获取历史数据选项
const getHistoricalOptions = async () => {
  try {
    const params = {
      start_time: selectedInfo.beginTime,
      end_time: selectedInfo.endTime
    };
    const optionsData = await api.get('/api/v1/historical/options', { params });
    
    // 更新selectOptions，映射接口返回的字段名到代码中使用的字段名
    selectOptions.lots = optionsData.lotnames || [];
    selectOptions.productRequests = optionsData.productrequestnames || [];
    selectOptions.productSpecs = optionsData.productspecnames || [];
    selectOptions.processOperations = optionsData.processoperationnames || [];
    selectOptions.eqs = optionsData.machinenames || []; // 使用新的machinenames字段
    selectOptions.defectCodes = optionsData.defect_codes || []; // 添加defect_codes字段
    selectOptions.lotFull = optionsData.lotnames || []; // 更新完整的Lot列表，用于过滤
  } catch (error) {
    console.error('获取历史数据选项失败:', error);
    showMessage('获取历史数据选项失败', 'error');
  }
};

// 获取玻璃列表
const getGlassListByHistorical = async () => {
  try {
    // 验证时间参数
    if (!selectedInfo.beginTime || !selectedInfo.endTime) {
      showMessage('请选择有效的时间范围', 'error');
      return;
    }
    
    // 验证开始时间不能晚于结束时间
    if (new Date(selectedInfo.beginTime) > new Date(selectedInfo.endTime)) {
      showMessage('开始时间不能晚于结束时间', 'error');
      return;
    }
    
    loading.value = true;
    // 构建参数对象，过滤掉空值
    const params = {
      start_time: selectedInfo.beginTime,
      end_time: selectedInfo.endTime,
    };
    
    // 只添加非空参数
    if (selectedInfo.inspectionType) {
      params.inspectionType = selectedInfo.inspectionType;
    }
    if (selectedInfo.inspector) {
      params.inspector = selectedInfo.inspector;
    }

    if (selectedInfo.lot.length > 0) {
      params.lots = selectedInfo.lot.join(',');
    }
    if (selectedInfo.productrequestname.length > 0) {
      params.workOrders = selectedInfo.productrequestname.join(',');
    }
    if (selectedInfo.product.length > 0) {
      params.products = selectedInfo.product.join(',');
    }
    if (selectedInfo.processOperationName.length > 0) {
      params.operations = selectedInfo.processOperationName.join(',');
    }
    if (selectedInfo.eq.length > 0) {
      params.machinename = selectedInfo.eq.join(',');
    }
    if (selectedInfo.defectCode.length > 0) {
      params.defect_code = selectedInfo.defectCode.join(',');
    }
    
    const data = await api.get('/api/v1/historical/glasses', { params });
    
    // 处理后端返回的新数据结构，转换为适合前端展示的分组数据
    // 每个分组包含产品型号、站点和对应的glass列表
    const groupedGlasses = data.map(item => {
      // 生成唯一的分组ID
      const groupId = `${item.product}-${item.processoperationname}`;
      return {
        groupId,
        product: item.product,
        processoperationname: item.processoperationname,
        glasses: item.glassid.map(glassid => ({
          id: glassid,
          product: item.product,
          processoperationname: item.processoperationname
        }))
      };
    });
    
    glassList.value = groupedGlasses;
    
    // 如果有玻璃，默认选择第一个分组的第一个玻璃
    if (glassList.value.length > 0 && glassList.value[0].glasses.length > 0) {
      switchGlass(glassList.value[0].glasses[0].id);
      // 默认展开第一个分组
      expandedGroups.value.add(glassList.value[0].groupId);
    }
  } catch (error) {
    console.error('获取玻璃列表失败:', error);
    showMessage('获取玻璃列表失败', 'error');
  } finally {
    loading.value = false;
  }
};

// 初始化函数
const init = async () => {
  try {
    // 获取缺陷代码列表
    const reasonCodes = await getReasonCodeList();
    // 处理缺陷代码数据
    defectCodes.value = reasonCodes.map(code => {
      // 获取小写的codetype
      const codeType = (code.CODETYPE || 'point').toLowerCase();
      
      return {
        id: code.CODE,
        name: code.CODE, // name绑定code，显示CODE而不是DESCREPTION
        description: code.DESCREPTION, // 保留DESCREPTION作为描述
        color: code.COLOR || '#FF0000',
        needSymmetry: codeType === 'mask', // 如果codetype是mask，则needSymmetry为true
        type: codeType, // 使用小写的codetype
        levelno: code.LEVELNO || 0, // 添加levelno字段
        hasRemark: code.HAS_REMARK === 'Y' // 是否需要备注
      };
    });
    // 按levelno递增排序
    defectCodes.value.sort((a, b) => a.levelno - b.levelno);
    // 如果有缺陷代码，默认选择第一个
    if (defectCodes.value.length > 0) {
      selectedCode.value = defectCodes.value[0];
    }
    
    // 获取历史数据选项
    await getHistoricalOptions();
  } catch (error) {
    console.error('初始化失败:', error);
    showMessage('初始化失败', 'error');
  }
};

// 关闭所有下拉菜单
const closeAllDropdowns = () => {
  showLotDropdown.value = false;
  showWorkOrderDropdown.value = false;
  showProductDropdown.value = false;
  showOperDropdown.value = false;
  showMachineDropdown.value = false;
  showDefectCodeDropdown.value = false;
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  // 检查点击的元素是否在下拉菜单外部
  const dropdowns = document.querySelectorAll('.relative');
  let isClickInside = false;
  
  dropdowns.forEach(dropdown => {
    if (dropdown.contains(event.target)) {
      isClickInside = true;
    }
  });
  
  // 如果点击的是外部元素，关闭所有下拉菜单
  if (!isClickInside) {
    closeAllDropdowns();
  }
};

// 生命周期钩子
onMounted(() => {
  init();
  window.addEventListener('keydown', handleKeydown);
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  document.removeEventListener('click', handleClickOutside);
  if (digitTimer) {
    clearTimeout(digitTimer);
  }
});
</script>