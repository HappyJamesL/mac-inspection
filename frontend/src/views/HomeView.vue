<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <header class="bg-primary text-white p-6 shadow-md">
      <div class="container mx-auto">
        <h1 class="text-[clamp(2rem,5vw,3rem)] font-bold text-center">MAC检测触屏系统</h1>
        <p class="text-center mt-2 text-blue-100">实时缺陷检测与数据采集平台</p>
      </div>
    </header>
    
    <main class="flex-1 container mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <router-link to="/inspection" class="group">
          <div class="glass-panel h-64 flex flex-col items-center justify-center text-center transform transition-all duration-300 group-hover:shadow-xl group-hover:-translate-y-1">
            <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold mb-2">开始缺陷检测</h2>
            <p class="text-gray-600">进入缺陷检测界面，实时记录和分析缺陷数据</p>
          </div>
        </router-link>
        
        <router-link to="/query" class="group">
          <div class="glass-panel h-64 flex flex-col items-center justify-center text-center transform transition-all duration-300 group-hover:shadow-xl group-hover:-translate-y-1">
            <div class="w-20 h-20 bg-info/10 rounded-full flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold mb-2">历史数据查询</h2>
            <p class="text-gray-600">查询和分析历史缺陷记录，生成统计报告</p>
          </div>
        </router-link>
      </div>
      
      <div class="mt-12 text-center">
        <div class="inline-block bg-white p-4 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold mb-2">当前设备信息</h3>
          <p class="text-gray-600">{{ deviceInfo }}</p>
        </div>
      </div>
    </main>
    
    <footer class="bg-gray-800 text-white py-4">
      <div class="container mx-auto px-4 text-center">
        <p>&copy; {{ new Date().getFullYear() }} MAC检测触屏系统 | 版本 1.0.0</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const deviceInfo = ref('加载中...')

onMounted(async () => {
  try {
    // 这里可以从API获取真实的设备信息
    // const response = await getDeviceInfo()
    // deviceInfo.value = response.data.machineName
    deviceInfo.value = '设备编号: MAC-2024-001'
  } catch (error) {
    deviceInfo.value = '设备信息获取失败'
  }
})
</script>

<style scoped>
/* 响应式调整 */
@media (max-width: 768px) {
  h1 {
    font-size: 1.8rem;
  }
  .glass-panel {
    height: 12rem;
  }
}
</style>