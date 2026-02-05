import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const sidebar = ref({
    opened: true,
    withoutAnimation: false,
  })
  const device = ref<'desktop' | 'mobile'>('desktop')
  const size = ref<'default' | 'large' | 'small'>('default')
  const theme = ref<string>('light')
  const isFullscreen = ref<boolean>(false)

  // 计算属性
  const isMobile = computed(() => device.value === 'mobile')

  // 方法
  // 切换侧边栏
  const toggleSidebar = (withoutAnimation = false) => {
    sidebar.value.opened = !sidebar.value.opened
    sidebar.value.withoutAnimation = withoutAnimation
  }

  // 关闭侧边栏
  const closeSidebar = (withoutAnimation = false) => {
    sidebar.value.opened = false
    sidebar.value.withoutAnimation = withoutAnimation
  }

  // 设置设备类型
  const setDevice = (val: 'desktop' | 'mobile') => {
    device.value = val
    if (val === 'mobile') {
      sidebar.value.opened = false
    }
  }

  // 设置尺寸
  const setSize = (val: 'default' | 'large' | 'small') => {
    size.value = val
  }

  // 切换主题
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    document.documentElement.setAttribute('theme', theme.value)
  }

  // 切换全屏
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        console.error('全屏切换失败:', err)
      })
      isFullscreen.value = true
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
        isFullscreen.value = false
      }
    }
  }

  return {
    sidebar,
    device,
    size,
    theme,
    isFullscreen,
    isMobile,
    toggleSidebar,
    closeSidebar,
    setDevice,
    setSize,
    toggleTheme,
    toggleFullscreen,
  }
})
