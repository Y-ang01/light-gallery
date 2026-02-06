// src/store/modules/user.ts - 关键修复
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, logout, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || sessionStorage.getItem('token') || '')
  const userInfo = ref({
    id: '',
    username: '',
    email: '',
    avatar_url: '',
    role: 'USER', // USER / ADMIN
    created_at: '',
  })
  const isLoading = ref(false)

  // 计算属性
  const isLogin = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value.role === 'ADMIN')

  // 修复登录逻辑
  const loginAction = async (form: { username: string; password: string; remember: boolean }) => {
    try {
      isLoading.value = true

      // 修复：确保调用正确的登录接口
      const response = await login(form.username, form.password)

      if (response && response.code === 200 && response.data?.token) {
        // 保存token
        token.value = response.data.token

        // 根据是否记住我，选择存储位置
        if (form.remember) {
          localStorage.setItem('token', token.value)
          sessionStorage.removeItem('token')
        } else {
          sessionStorage.setItem('token', token.value)
          localStorage.removeItem('token')
        }

        // 获取用户信息
        await fetchUserInfo()
        return true
      }

      return false
    } catch (error) {
      console.error('登录失败:', error)
      // 明确提示错误类型
      if (error.response?.status === 401) {
        ElMessage.error('用户名或密码错误')
      } else {
        ElMessage.error('登录失败，请检查网络或联系管理员')
      }
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 修复注册逻辑
  const registerAction = async (form: { username: string; email: string; password: string }) => {
    try {
      isLoading.value = true
      const response = await register(form.username, form.email, form.password)

      if (response && response.code === 200) {
        return true
      } else {
        ElMessage.error(response?.message || '注册失败')
        return false
      }
    } catch (error) {
      console.error('注册失败:', error)
      ElMessage.error(error.response?.data?.message || '注册失败，请稍后重试')
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 其他方法保持不变...
  const logoutAction = async () => {
    /* ... */
  }
  const fetchUserInfo = async () => {
    /* ... */
  }
  const checkLoginStatus = async () => {
    /* ... */
  }
  const clearUserInfo = () => {
    /* ... */
  }

  return {
    token,
    userInfo,
    isLoading,
    isLogin,
    isAdmin,
    loginAction,
    registerAction,
    logoutAction,
    fetchUserInfo,
    checkLoginStatus,
    clearUserInfo,
  }
})
