<!-- 文件路径: frontend/src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-form">
      <div class="form-header">
        <h2>登录光影收藏馆</h2>
        <p>欢迎回来，请登录您的账户</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">邮箱地址</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            placeholder="请输入您的邮箱"
            :class="{ error: errors.email }"
          />
          <span class="error-message" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            placeholder="请输入密码"
            :class="{ error: errors.password }"
          />
          <span class="error-message" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <div class="form-options">
          <label class="checkbox">
            <input type="checkbox" v-model="form.rememberMe" />
            <span>记住我</span>
          </label>
          <router-link to="/forgot-password" class="forgot-link">忘记密码？</router-link>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading">登录中...</span>
          <span v-else>登录</span>
        </button>

        <div class="form-footer">
          <p>还没有账户？ <router-link to="/register">立即注册</router-link></p>
        </div>
      </form>

      <div v-if="error" class="alert error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

interface LoginForm {
  email: string
  password: string
  rememberMe: boolean
}

interface FormErrors {
  email?: string
  password?: string
}

const authStore = useAuthStore()
const router = useRouter()

const form = reactive<LoginForm>({
  email: '',
  password: '',
  rememberMe: false,
})

const errors = reactive<FormErrors>({})
const loading = ref(false)
const error = ref('')

const validateForm = (): boolean => {
  let isValid = true
  errors.email = ''
  errors.password = ''

  if (!form.email) {
    errors.email = '请输入邮箱地址'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = '请输入有效的邮箱地址'
    isValid = false
  }

  if (!form.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = '密码长度至少6位'
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  if (!validateForm()) return

  loading.value = true
  error.value = ''

  try {
    await authStore.login({
      email: form.email,
      password: form.password,
      remember_me: form.rememberMe,
    })

    // 登录成功，跳转到首页或原定目标页面
    const redirect = router.currentRoute.value.query.redirect as string
    await router.push(redirect || '/dashboard')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败，请检查邮箱和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  color: #333;
  margin-bottom: 0.5rem;
}

.form-header p {
  color: #666;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

input.error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.forgot-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.875rem;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background: #5a6fd8;
}

.submit-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.form-footer {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
}

.alert {
  padding: 12px;
  border-radius: 6px;
  margin-top: 1rem;
  text-align: center;
}

.alert.error {
  background: #fee;
  color: #e74c3c;
  border: 1px solid #f5c6cb;
}
</style>
