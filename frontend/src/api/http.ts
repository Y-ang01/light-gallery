// 文件路径: frontend/src/api/http.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '../stores/auth'

// 创建axios实例
const http: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
http.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器
http.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 处理401错误（Token过期）
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const authStore = useAuthStore()
        await authStore.refreshToken()

        // 重试原始请求
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`
        return http(originalRequest)
      } catch (refreshError) {
        // 刷新失败，跳转到登录页
        const authStore = useAuthStore()
        await authStore.logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export { http }
