// 文件路径: frontend/src/types/auth.ts
export interface User {
  id: string
  email: string
  username: string
  role: 'ADMIN' | 'AUTHOR' | 'USER'
  avatar_url?: string
  profile?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginData {
  email: string
  password: string
  remember_me?: boolean
}

export interface RegisterData {
  email: string
  username: string
  password: string
  role?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

// HTTP响应类型
export interface ApiResponse<T = any> {
  data: T
  status: number
  statusText: string
  headers: any
  config: any
}
