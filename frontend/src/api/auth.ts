// 文件路径: frontend/src/api/auth.ts
import { http } from './http'
import type { User, LoginData, RegisterData, TokenResponse } from '../types/auth'

export const authAPI = {
  // 用户注册
  async register(data: RegisterData): Promise<User> {
    const response = await http.post('/auth/register', data)
    return response.data
  },

  // 用户登录
  async login(data: LoginData): Promise<TokenResponse> {
    const response = await http.post('/auth/login', data)
    return response.data
  },

  // 用户登出
  async logout(): Promise<void> {
    await http.post('/auth/logout')
  },

  // 获取当前用户信息
  async getCurrentUser(): Promise<User> {
    const response = await http.get('/auth/me')
    return response.data
  },

  // 刷新Token
  async refreshToken(): Promise<TokenResponse> {
    const response = await http.post('/auth/refresh')
    return response.data
  },

  // 更新用户信息
  async updateUser(data: Partial<User>): Promise<User> {
    const response = await http.put('/auth/me', data)
    return response.data
  },
}
