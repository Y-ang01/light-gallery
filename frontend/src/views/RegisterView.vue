<!-- 文件路径: frontend/src/views/RegisterView.vue -->
<template>
  <div class="register-container">
    <div class="register-form">
      <div class="form-header">
        <h2>加入光影收藏馆</h2>
        <p>创建您的专业图片管理账户</p>
      </div>

      <form @submit.prevent="handleRegister">
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
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            placeholder="请输入用户名（2-20个字符）"
            :class="{ error: errors.username }"
          />
          <span class="error-message" v-if="errors.username">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            placeholder="请输入密码（至少8位）"
            :class="{ error: errors.password }"
          />
          <span class="error-message" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            required
            placeholder="请再次输入密码"
            :class="{ error: errors.confirmPassword }"
          />
          <span class="error-message" v-if="errors.confirmPassword">{{
            errors.confirmPassword
          }}</span>
        </div>

        <div class="form-group">
          <label class="checkbox">
            <input type="checkbox" v-model="form.agreeTerms" required />
            <span
              >我已阅读并同意 <a href="/terms" target="_blank">服务条款</a> 和
              <a href="/privacy" target="_blank">隐私政策</a></span
            >
          </label>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading">注册中...</span>
          <span v-else>注册账户</span>
        </button>

        <div class="form-footer">
          <p>已有账户？ <router-link to="/login">立即登录</router-link></p>
        </div>
      </form>

      <div v-if="error" class="alert error">
        {{ error }}
      </div>

      <div v-if="success" class="alert success">注册成功！正在跳转...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

interface RegisterForm {
  email: string
  username: string
  password: string
  confirmPassword: string
  agreeTerms: boolean
}

interface FormErrors {
  email?: string
  username?: string
  password?: string
  confirmPassword?: string
}

const authStore = useAuthStore()
const router = useRouter()

const form = reactive<RegisterForm>({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false,
})

const errors = reactive<FormErrors>({})
const loading = ref(false)
const error = ref('')
const success = ref(false)

const validateForm = (): boolean => {
  let isValid = true
  Object.keys(errors).forEach((key) => delete errors[key as keyof FormErrors])

  // 邮箱验证
  if (!form.email) {
    errors.email = '请输入邮箱地址'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = '请输入有效的邮箱地址'
    isValid = false
  }

  // 用户名验证
  if (!form.username) {
    errors.username = '请输入用户名'
    isValid = false
  } else if (form.username.length < 2 || form.username.length > 20) {
    errors.username = '用户名长度必须在2-20个字符之间'
    isValid = false
  }

  // 密码验证
  if (!form.password) {
    errors.password = '请输入密码'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = '密码长度至少8位'
    isValid = false
  } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(form.password)) {
    errors.password = '密码必须包含字母和数字'
    isValid = false
  }

  // 确认密码验证
  if (!form.confirmPassword) {
    errors.confirmPassword = '请确认密码'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  // 条款同意验证
  if (!form.agreeTerms) {
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  if (!validateForm()) return

  loading.value = true
  error.value = ''
  success.value = false

  try {
    await authStore.register({
      email: form.email,
      username: form.username,
      password: form.password,
    })

    success.value = true
    // 注册成功后自动登录
    setTimeout(async () => {
      await authStore.login({
        email: form.email,
        password: form.password,
      })
      await router.push('/dashboard')
    }, 2000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
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

.checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.checkbox a {
  color: #667eea;
  text-decoration: none;
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
  margin-bottom: 1rem;
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

.alert.success {
  background: #efe;
  color: #27ae60;
  border: 1px solid #c3e6cb;
}
</style>
