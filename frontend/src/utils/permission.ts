// Token相关常量
const TOKEN_KEY = 'light_gallery_token'
const TOKEN_EXPIRE_KEY = 'light_gallery_token_expire'

// 设置Token
export const setToken = (token: string, remember = false): void => {
  localStorage.setItem(TOKEN_KEY, token)

  // 记住我：设置7天有效期，否则会话有效
  if (remember) {
    const expireTime = new Date().getTime() + 7 * 24 * 60 * 60 * 1000
    localStorage.setItem(TOKEN_EXPIRE_KEY, expireTime.toString())
  } else {
    sessionStorage.setItem(TOKEN_KEY, token)
    localStorage.removeItem(TOKEN_EXPIRE_KEY)
  }
}

// 获取Token
export const getToken = (): string => {
  // 检查Token是否过期
  const expireTime = localStorage.getItem(TOKEN_EXPIRE_KEY)

  if (expireTime) {
    const now = new Date().getTime()
    if (now > Number(expireTime)) {
      removeToken()
      return ''
    }
  }

  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY) || ''
}

// 移除Token
export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TOKEN_EXPIRE_KEY)
  sessionStorage.removeItem(TOKEN_KEY)
}

// 检查权限
export const checkPermission = (role: string, requiredRole: string): boolean => {
  const roleOrder = {
    GUEST: 0,
    USER: 1,
    AUTHOR: 2,
    ADMIN: 3,
  }

  return (
    roleOrder[role as keyof typeof roleOrder] >= roleOrder[requiredRole as keyof typeof roleOrder]
  )
}

// 路由权限过滤
export const filterRoutes = (routes: any[], role: string): any[] => {
  return routes.filter((route) => {
    if (!route.meta?.requiresAdmin) return true

    // 管理员路由仅管理员可访问
    return role === 'ADMIN'
  })
}
