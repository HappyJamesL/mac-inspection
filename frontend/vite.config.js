import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/mac/', // 设置base路径为/mac/
  server: {
    port: 5173, // 固定开发服务器端口
    host: '0.0.0.0', // 允许外部访问
    proxy: {
      // 处理/mac/api请求，用于本地开发测试
      '/mac/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      // 将/api请求代理到后端服务，兼容原有请求
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // 将/api重写为/mac/api，匹配后端实际API路径
        rewrite: (path) => path.replace(/^\/api/, '/mac/api')
      }
    }
  }
})
