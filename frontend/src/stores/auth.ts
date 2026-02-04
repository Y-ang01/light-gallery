// 文件路径: frontend/src/stores/auth.ts
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { LoginData, RegisterData, TokenResponse, User } from '../types/auth'
import { authAPI } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 从localStorage初始化token
  const initializeToken = () => {
    const storedToken = localStorage.getItem('access_token')
    if (storedToken) {
      // 验证token是否过期
      try {
        const payload = JSON.parse(atob(storedToken.split('.')[1]))
        if (payload.exp * 1000 < Date.now()) {
          // Token已过期
          token.value = null
          localStorage.removeItem('access_token')
        } else {
          token.value = storedToken
        }
      } catch (error) {
        // Token格式错误
        token.value = null
        localStorage.removeItem('access_token')
      }
    }
  }

  // 初始化token
  initializeToken()

  // Actions
  const login = async (loginData: LoginData): Promise<TokenResponse> => {
    try {
      const response = await authAPI.login(loginData)

      // 保存token到localStorage
      localStorage.setItem('access_token', response.access_token)
      token.value = response.access_token

      // 获取用户信息
      await getCurrentUser()

      return response
    } catch (error) {
      throw error
    }
  }

  const register = async (registerData: RegisterData): Promise<User> => {
    try {
      return await authAPI.register(registerData)
    } catch (error) {
      throw error
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      // 清除本地状态
      user.value = null
      token.value = null
      localStorage.removeItem('access_token')
    }
  }

  const getCurrentUser = async (): Promise<User | null> => {
    if (!token.value) return null

    try {
      const userData = await authAPI.getCurrentUser()
      user.value = userData
      return userData
    } catch (error) {
      // token可能已过期，清除本地状态
      token.value = null
      localStorage.removeItem('access_token')
      throw error
    }
  }

  const refreshToken = async (): Promise<TokenResponse | null> => {
    if (!token.value) return null

    try {
      const response = await authAPI.refreshToken()
      localStorage.setItem('access_token', response.access_token)
      token.value = response.access_token
      return response
    } catch (error) {
      await logout()
      throw error
    }
  }

  // 初始化时获取用户信息
  if (token.value) {
    getCurrentUser().catch(() => {
      // 静默处理错误
    })
  }

  return {
    // State
    user: user as { value: User | null },
    token: token as { value: string | null },
    isAuthenticated,

    // Actions
    login,
    register,
    logout,
    getCurrentUser,
    refreshToken,
  }
})
