import axios, {
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import { getToken, removeToken } from '@/utils/permission'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加token
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  },
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // 业务错误处理
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')

      // 401未授权，需要重新登录
      if (res.code === 401) {
        const userStore = useUserStore()
        ElMessageBox.confirm('登录状态已过期，请重新登录', '提示', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning',
        }).then(() => {
          userStore.logoutAction()
          window.location.href = '/login'
        })
      }

      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  (error: AxiosError) => {
    console.error('响应错误:', error)

    let message = ''
    if (error.response) {
      const status = error.response.status

      switch (status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权，请登录'
          const userStore = useUserStore()
          userStore.logoutAction()
          removeToken()
          window.location.href = '/login'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求地址不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = `请求失败，状态码：${status}`
      }
    } else if (error.request) {
      message = '请求超时，请检查网络'
    } else {
      message = '请求错误'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  },
)

// 封装请求方法
interface RequestOptions {
  onUploadProgress?: (progressEvent: ProgressEvent) => void
  onDownloadProgress?: (progressEvent: ProgressEvent) => void
}

export const request = {
  get<T = any>(
    url: string,
    params?: Record<string, any>,
    config?: AxiosRequestConfig & RequestOptions,
  ): Promise<T> {
    return service.get(url, { params, ...config })
  },

  post<T = any>(
    url: string,
    data?: Record<string, any> | FormData,
    config?: AxiosRequestConfig & RequestOptions,
  ): Promise<T> {
    return service.post(url, data, config)
  },

  put<T = any>(
    url: string,
    data?: Record<string, any>,
    config?: AxiosRequestConfig & RequestOptions,
  ): Promise<T> {
    return service.put(url, data, config)
  },

  delete<T = any>(
    url: string,
    params?: Record<string, any>,
    config?: AxiosRequestConfig & RequestOptions,
  ): Promise<T> {
    return service.delete(url, { params, ...config })
  },
}

export default service
