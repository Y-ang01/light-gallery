<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-left">
        <el-button type="text" icon="Menu" class="sidebar-toggle" @click="toggleSidebar" />
        <h1 class="app-title">光影收藏馆</h1>
      </div>
      <div class="header-right">
        <!-- 搜索框 -->
        <el-input
          v-model="searchKeyword"
          placeholder="搜索图片集、博客..."
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button icon="Search" @click="handleSearch" />
          </template>
        </el-input>

        <!-- 用户菜单 -->
        <el-dropdown @command="handleUserCommand">
          <div class="user-info">
            <el-avatar :src="userAvatar" class="user-avatar">
              <span class="avatar-text">{{ userInitial }}</span>
            </el-avatar>
            <span class="user-name">{{ userName }}</span>
            <el-icon class="dropdown-icon">
              <ArrowDown />
            </el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item icon="User" command="profile"> 个人中心 </el-dropdown-item>
              <el-dropdown-item icon="Setting" command="privacy"> 隐私设置 </el-dropdown-item>
              <el-dropdown-item v-if="isAdmin" icon="DataAnalysis" command="system-stats">
                系统统计
              </el-dropdown-item>
              <el-dropdown-item icon="Logout" command="logout" divided> 退出登录 </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="app-main">
      <!-- 侧边栏 -->
      <aside class="app-sidebar" :class="{ collapsed: !sidebarOpened }">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
          :collapse="!sidebarOpened"
          collapse-transition
        >
          <!-- 菜单列表 -->
          <el-menu-item
            v-for="menu in menuList"
            :key="menu.name"
            :index="menu.path"
            :icon="menu.meta.icon"
          >
            <template #title>{{ menu.meta.title }}</template>
          </el-menu-item>
        </el-menu>
      </aside>

      <!-- 主内容区 -->
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { useAppStore } from '@/store/modules/app'
import { formatDateTime } from '@/utils/format'

// 导入图标
import {
  Menu,
  Search,
  User,
  Setting,
  Logout,
  DataAnalysis,
  ArrowDown,
} from '@element-plus/icons-vue'

// 状态管理
const userStore = useUserStore()
const appStore = useAppStore()
const router = useRouter()
const route = useRoute()

// 响应式数据
const searchKeyword = ref('')
const sidebarOpened = ref(true)

// 计算属性
const menuList = computed(() => {
  return route.matched[0]?.children?.filter((menu) => !menu.meta.hidden) || []
})

const activeMenu = computed(() => {
  return route.path
})

const userName = computed(() => {
  return userStore.userInfo.username || '未知用户'
})

const userAvatar = computed(() => {
  return userStore.userInfo.avatar_url || ''
})

const userInitial = computed(() => {
  return userName.value.charAt(0).toUpperCase()
})

const isAdmin = computed(() => {
  return userStore.isAdmin
})

// 方法
// 切换侧边栏
const toggleSidebar = () => {
  sidebarOpened.value = !sidebarOpened.value
}

// 处理搜索
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({
      path: '/search',
      query: { keyword: searchKeyword.value.trim() },
    })
  }
}

// 处理用户菜单命令
const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'privacy':
      router.push('/user/privacy')
      break
    case 'system-stats':
      router.push('/admin/stats')
      break
    case 'logout':
      userStore.logoutAction().then(() => {
        router.push('/login')
      })
      break
  }
}

// 监听路由变化
watch(
  () => route.path,
  () => {
    // 移动端自动关闭侧边栏
    if (appStore.isMobile) {
      sidebarOpened.value = false
    }
  },
)

// 初始化
onMounted(() => {
  // 检查用户信息
  userStore.checkLoginStatus()

  // 监听窗口大小变化
  const handleResize = () => {
    appStore.setDevice(window.innerWidth < 768 ? 'mobile' : 'desktop')
  }

  handleResize()
  window.addEventListener('resize', handleResize)

  // 清理函数
  return () => {
    window.removeEventListener('resize', handleResize)
  }
})
</script>

<style scoped lang="scss">
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f7fa;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: #1989fa;
  color: #fff;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-toggle {
  color: #fff !important;
  font-size: 18px;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.search-input {
  width: 300px;
  --el-input-bg-color: rgba(255, 255, 255, 0.2);
  --el-input-text-color: #fff;
  --el-input-placeholder-color: rgba(255, 255, 255, 0.7);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
}

.user-avatar {
  width: 36px;
  height: 36px;
}

.avatar-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}

.user-name {
  color: #fff;
  font-size: 14px;
  max-width: 100px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-icon {
  color: #fff;
  font-size: 14px;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  width: 200px;
  background-color: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  transition: width 0.3s;
  overflow-y: auto;
  z-index: 10;
}

.app-sidebar.collapsed {
  width: 64px;
}

.sidebar-menu {
  border-right: none !important;
  height: 100%;
}

.app-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

// 滚动条样式优化
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

// 响应式适配
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    height: calc(100vh - 64px);
    transform: translateX(0);
    transition: transform 0.3s;
  }

  .app-sidebar.collapsed {
    transform: translateX(-100%);
  }

  .search-input {
    width: 160px;
  }

  .user-name {
    display: none;
  }
}
</style>
