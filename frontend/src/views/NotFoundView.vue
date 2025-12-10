<template>
  <div class="min-h-screen bg-gray-100 flex flex-col">
    <header class="bg-primary text-white p-4 shadow-md">
      <div class="container mx-auto">
        <h1 class="text-2xl font-bold">MAC检测系统</h1>
      </div>
    </header>
    
    <main class="flex-1 container mx-auto px-4 py-12 flex flex-col items-center justify-center">
      <div class="text-center max-w-md">
        <div class="text-9xl font-bold text-gray-300 mb-4">404</div>
        <h2 class="text-3xl font-bold text-gray-800 mb-4">页面不存在</h2>
        <p class="text-gray-600 mb-8">您访问的页面不存在或已被移除</p>
        <router-link 
          to="/" 
          class="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          返回首页
        </router-link>
      </div>
    </main>
    
    <footer class="bg-gray-800 text-white py-4 mt-auto">
      <div class="container mx-auto px-4 text-center text-sm">
        <p>MAC检测系统 © {{ new Date().getFullYear() }}</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// 无需特殊逻辑
</script>

<style scoped>
/* 样式调整 */
</style>