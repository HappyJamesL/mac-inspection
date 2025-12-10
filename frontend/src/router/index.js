import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InspectionView from '../views/InspectionView.vue'
import QueryView from '../views/QueryView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import ForbiddenView from '../views/ForbiddenView.vue'
import { checkPermission } from '../services/api'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: '首页 - MAC检测系统'
      }
    },
    {
      path: '/inspection',
      name: 'inspection',
      component: InspectionView,
      meta: {
        title: '缺陷检测 - MAC检测系统'
      }
    },

    {
      path: '/query',
      name: 'query',
      component: QueryView,
      meta: {
        title: '历史查询 - MAC检测系统'
      }
    },
    {
      path: '/forbidden',
      name: 'forbidden',
      component: ForbiddenView,
      meta: {
        title: '访问被拒绝 - MAC检测系统'
      }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      meta: {
        title: '页面不存在 - MAC检测系统'
      }
    }
  ]
})

// 权限控制 - 验证路由访问权限
const verifyRoutePermission = async (to, from, next) => {
  // 以下页面不需要权限检查
  const noPermissionRequired = ['forbidden', 'query']
  if (noPermissionRequired.includes(to.name)) {
    next()
    return
  }
  
  // 开发环境中，允许所有访问，方便开发和测试
  if (import.meta.env.DEV) {
    next()
    return
  }
  
  // 生产环境中，验证URL中的userrole参数
  const userrole = to.query.userrole
  if (userrole) {
    try {
      // 调用后端API验证userrole
      const response = await checkPermission(userrole)
      if (response.allowed) {
        next()
        return
      }
    } catch (error) {
      console.error('权限验证失败:', error)
    }
  }
  
  // 没有userrole参数或验证失败，重定向到403页面
  next({ name: 'forbidden' })
}

// 设置页面标题和权限检查
router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title || 'MAC检测系统'
  
  // 检查权限
  await verifyRoutePermission(to, from, next)
})

export default router