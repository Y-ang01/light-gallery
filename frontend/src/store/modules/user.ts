import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getUserProfile, logout as apiLogout } from '@/api/auth'
import { setToken, getToken, removeToken } from '@/utils/permission'

// 用户信息类型
export interface UserInfo {
  id: string
  username: string
  email: string
  avatar_url: string
  role: string
  profile?: string
  is_active: boolean
}

// 登录表单类型
export interface LoginForm {
  username: string
  password: string
  remember: boolean
}

// 注册表单类型
export interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<UserInfo>({
    id: '',
    username: '',
    email: '',
    avatar_url: '',
    role: 'USER',
    is_active: true,
  })
  const token = ref<string>(getToken() || '')
  const isLoading = ref<boolean>(false)

  // 计算属性
  const isLogin = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value.role === 'ADMIN')

  // 方法
  // 登录
  const loginAction = async (form: LoginForm) => {
    try {
      isLoading.value = true
      const response = await login(form.username, form.password)

      if (response.code === 200) {
        const { access_token, user } = response.data
        token.value = access_token
        userInfo.value = user

        // 保存token
        setToken(access_token, form.remember)

        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 注册
  const registerAction = async (form: RegisterForm) => {
    try {
      isLoading.value = true
      const response = await register(form.username, form.email, form.password)

      return response.code === 200;

    } catch (error) {
      console.error('注册失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 获取用户信息
  const fetchUserProfile = async () => {
    try {
      const response = await getUserProfile()

      if (response.code === 200) {
        userInfo.value = response.data
        return true
      }
      return false
    } catch (error) {
      console.error('获取用户信息失败:', error)
      await logoutAction()
      return false
    }
  }

  // 检查登录状态
  const checkLoginStatus = async () => {
    if (!token.value) return false

    try {
      return await fetchUserProfile()
    } catch (error) {
      return false
    }
  }

  // 登出
  const logoutAction = async () => {
    try {
      await apiLogout()
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 清除状态
      token.value = ''
      userInfo.value = {
        id: '',
        username: '',
        email: '',
        avatar_url: '',
        role: 'USER',
        is_active: true,
      }
      // 移除token
      removeToken()
    }
  }

  // 更新用户信息
  const updateUserInfo = (data: Partial<UserInfo>) => {
    userInfo.value = { ...userInfo.value, ...data }
  }

  return {
    userInfo,
    token,
    isLoading,
    isLogin,
    isAdmin,
    loginAction,
    registerAction,
    fetchUserProfile,
    checkLoginStatus,
    logoutAction,
    updateUserInfo,
  }
})
