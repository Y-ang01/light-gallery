import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { ElMessage } from 'element-plus'

// 布局组件
import Layout from '@/layout/index.vue'

// 路由规则
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: {
      title: '注册',
      requiresAuth: false,
    },
  },
  {
    path: '/',
    name: 'Layout',
    component: Layout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/home/Home.vue'),
        meta: {
          title: '首页',
          icon: 'HomeFilled',
          requiresAuth: true,
        },
      },
      // 图片集管理
      {
        path: 'albums',
        name: 'AlbumList',
        component: () => import('@/views/album/AlbumList.vue'),
        meta: {
          title: '图片集管理',
          icon: 'Collection',
          requiresAuth: true,
        },
      },
      {
        path: 'albums/create',
        name: 'AlbumCreate',
        component: () => import('@/views/album/AlbumCreate.vue'),
        meta: {
          title: '创建图片集',
          requiresAuth: true,
          hidden: true,
        },
      },
      {
        path: 'albums/:id',
        name: 'AlbumDetail',
        component: () => import('@/views/album/AlbumDetail.vue'),
        meta: {
          title: '图片集详情',
          requiresAuth: true,
          hidden: true,
        },
      },
      {
        path: 'albums/recycle',
        name: 'AlbumRecycle',
        component: () => import('@/views/album/AlbumRecycle.vue'),
        meta: {
          title: '图片集回收站',
          requiresAuth: true,
          hidden: true,
        },
      },
      // 博客管理
      {
        path: 'blog',
        name: 'BlogList',
        component: () => import('@/views/blog/BlogList.vue'),
        meta: {
          title: '博客管理',
          icon: 'EditPen',
          requiresAuth: true,
        },
      },
      {
        path: 'blog/create',
        name: 'BlogCreate',
        component: () => import('@/views/blog/BlogCreate.vue'),
        meta: {
          title: '发布博客',
          requiresAuth: true,
          hidden: true,
        },
      },
      {
        path: 'blog/:id',
        name: 'BlogDetail',
        component: () => import('@/views/blog/BlogDetail.vue'),
        meta: {
          title: '博客详情',
          requiresAuth: true,
          hidden: true,
        },
      },
      {
        path: 'blog/draft',
        name: 'BlogDraft',
        component: () => import('@/views/blog/BlogDraft.vue'),
        meta: {
          title: '草稿箱',
          requiresAuth: true,
          hidden: true,
        },
      },
      // 搜索页面
      {
        path: 'search',
        name: 'SearchResult',
        component: () => import('@/views/search/SearchResult.vue'),
        meta: {
          title: '搜索结果',
          requiresAuth: true,
          hidden: true,
        },
      },
      {
        path: 'search/advanced',
        name: 'AdvancedSearch',
        component: () => import('@/views/search/AdvancedSearch.vue'),
        meta: {
          title: '高级搜索',
          requiresAuth: true,
          hidden: true,
        },
      },
      // 个人中心
      {
        path: 'user/profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: {
          title: '个人资料',
          requiresAuth: true,
          hidden: true,
        },
      },
      {
        path: 'user/privacy',
        name: 'PrivacySetting',
        component: () => import('@/views/user/PrivacySetting.vue'),
        meta: {
          title: '隐私设置',
          requiresAuth: true,
          hidden: true,
        },
      },
      // 管理员页面
      {
        path: 'admin/users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: {
          title: '用户管理',
          icon: 'User',
          requiresAuth: true,
          requiresAdmin: true,
        },
      },
      {
        path: 'admin/stats',
        name: 'SystemStats',
        component: () => import('@/views/admin/SystemStats.vue'),
        meta: {
          title: '系统统计',
          icon: 'DataAnalysis',
          requiresAuth: true,
          requiresAdmin: true,
        },
      },
      {
        path: 'admin/sensitive',
        name: 'SensitiveWord',
        component: () => import('@/views/admin/SensitiveWord.vue'),
        meta: {
          title: '敏感词管理',
          requiresAuth: true,
          requiresAdmin: true,
          hidden: true,
        },
      },
    ],
  },
  // 404页面
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/common/NotFound.vue'),
    meta: {
      title: '页面不存在',
      requiresAuth: false,
    },
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/common/Forbidden.vue'),
    meta: {
      title: '无权限访问',
      requiresAuth: false,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - ${import.meta.env.VITE_APP_TITLE}`
  }

  // 不需要认证的路由直接放行
  if (!to.meta.requiresAuth) {
    next()
    return
  }

  // 检查是否已登录
  const isLogin = await userStore.checkLoginStatus()

  if (!isLogin) {
    ElMessage.warning('请先登录')
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  // 检查管理员权限
  if (to.meta.requiresAdmin && userStore.userInfo.role !== 'ADMIN') {
    ElMessage.error('无管理员权限')
    next({ path: '/403' })
    return
  }

  next()
})

export default router
