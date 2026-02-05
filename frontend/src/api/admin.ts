import { request } from '@/utils/request'

// 获取所有用户
export const getAllUsers = (params: {
  page?: number
  page_size?: number
  keyword?: string
  role?: string
  is_active?: boolean
}) => {
  return request.get('/admin/users', {
    params: {
      page: 1,
      page_size: 10,
      ...params,
    },
  })
}

// 修改用户角色
export const updateUserRole = (userId: string, role: string) => {
  return request.put(`/admin/users/${userId}/role`, {
    role,
  })
}

// 禁用/启用用户
export const toggleUserActive = (userId: string, is_active: boolean) => {
  return request.put(`/admin/users/${userId}/active`, {
    is_active,
  })
}

// 获取系统统计
export const getSystemStats = () => {
  return request.get('/admin/system/stats')
}

// 获取用户行为日志
export const getUserActionLogs = (params: {
  user_id?: string
  action?: string
  start_time?: string
  end_time?: string
  page?: number
  page_size?: number
}) => {
  return request.get('/admin/logs/action', {
    params: {
      page: 1,
      page_size: 10,
      ...params,
    },
  })
}

// 管理敏感词
export const manageSensitiveWords = (
  words: string[],
  action: 'add' | 'delete' | 'replace',
  replace_word?: string,
) => {
  return request.post('/admin/sensitive-words', {
    words,
    action,
    replace_word: replace_word || '*',
  })
}
