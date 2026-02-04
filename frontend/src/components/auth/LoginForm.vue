<!-- 文件路径: frontend/src/components/auth/LoginForm.vue -->
<template>
  <div class="login-form">
    <h2>登录</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">邮箱</label>
        <input
          id="email"
          v-model="loginData.email"
          type="email"
          required
          placeholder="请输入邮箱"
        />
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          v-model="loginData.password"
          type="password"
          required
          placeholder="请输入密码"
        />
      </div>

      <div class="form-group">
        <label>
          <input v-model="loginData.remember_me" type="checkbox" />
          记住我
        </label>
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { LoginData } from '../types/auth'

const authStore = useAuthStore()
const router = useRouter()

const loginData = reactive<LoginData>({
  email: '',
  password: '',
  remember_me: false,
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!loginData.email || !loginData.password) {
    error.value = '请输入邮箱和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authStore.login(loginData)
    await router.push('/dashboard')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input[type='email'],
input[type='password'] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
}
</style>
