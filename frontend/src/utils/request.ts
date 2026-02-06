// src/utils/request.ts - 完整修复版（axios配置）
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api', // 关键：确保后端地址正确
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加token
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    ElMessage.error('请求发送失败，请检查网络')
    return Promise.reject(error)
  },
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 统一处理响应格式
    const { data } = response

    // 成功响应（根据后端实际格式调整）
    if (data.code === 200 || data.success) {
      return data
    }

    // 业务错误
    ElMessage.error(data.message || '操作失败')
    return Promise.reject(new Error(data.message || 'Error'))
  },
  (error) => {
    console.error('响应错误:', error)

    // 路由/接口不存在
    if (error.response?.status === 404) {
      ElMessage.error('请求的接口不存在，请检查后端服务')
      return Promise.reject(new Error('接口不存在'))
    }

    // 权限错误
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.clearUserInfo()
      ElMessageBox.confirm('登录状态已失效，请重新登录', '提示', {
        confirmButtonText: '重新登录',
        cancelButtonText: '取消',
        type: 'warning',
      }).then(() => {
        window.location.href = '/login'
      })
      return Promise.reject(new Error('登录失效'))
    }

    // 服务器错误
    if (error.response?.status === 500) {
      ElMessage.error('服务器内部错误，请稍后重试')
      return Promise.reject(new Error('服务器错误'))
    }

    // 网络错误
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
      return Promise.reject(new Error('网络错误'))
    }

    // 其他错误
    ElMessage.error(error.response.data?.message || '请求失败')
    return Promise.reject(error)
  },
)

export { request }
