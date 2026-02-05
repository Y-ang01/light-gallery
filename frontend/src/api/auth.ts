import { request } from '@/utils/request'

// 登录
export const login = (username: string, password: string) => {
  return request.post('/auth/login', {
    username,
    password,
  })
}

// 注册
export const register = (username: string, email: string, password: string) => {
  return request.post('/auth/register', {
    username,
    email,
    password,
  })
}

// 获取个人信息
export const getUserProfile = () => {
  return request.get('/auth/profile')
}

// 更新个人信息
export const updateUserProfile = (data: { username?: string; profile?: string }) => {
  return request.put('/auth/profile', data)
}

// 上传头像
export const uploadAvatar = (formData: FormData) => {
  return request.post('/auth/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      const percent = (progressEvent.loaded / progressEvent.total!) * 100
      console.log(`头像上传进度: ${percent.toFixed(2)}%`)
    },
  })
}

// 登出
export const logout = () => {
  return request.post('/auth/logout')
}
