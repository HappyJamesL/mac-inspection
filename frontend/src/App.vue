<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 初始化应用
onMounted(() => {
  // 可以在这里添加全局初始化逻辑
})
</script>

<template>
  <router-view />
</template>

<style scoped>
/* 全局组件样式已在style.css中定义 */
</style>
