// src/api/auth.ts - 简化版（确保路径正确）
import { request } from '@/utils/request'

/**
 * 用户登录
 * @param username 用户名
 * @param password 密码
 * @returns 登录结果
 */
export const login = async (username: string, password: string) => {
  // 确保路径是后端实际存在的路由
  return request.post('/auth/login', { username, password })
}

/**
 * 用户注册
 * @param username 用户名
 * @param email 邮箱
 * @param password 密码
 * @returns 注册结果
 */
export const register = async (username: string, email: string, password: string) => {
  // 关键：确保这个路径和后端一致
  return request.post('/auth/register', {
    username,
    email,
    password,
  })
}

/**
 * 获取用户信息
 * @returns 用户信息
 */
export const getUserInfo = async () => {
  return request.get('/auth/info')
}

/**
 * 用户登出
 * @returns 登出结果
 */
export const logout = async () => {
  return request.post('/auth/logout')
}
