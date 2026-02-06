<!-- src/views/auth/Login.vue - 修复版 -->
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2 class="login-title">光影收藏馆</h2>
        <p class="login-subtitle">欢迎登录，开始您的创作之旅</p>
      </div>

      <el-form
        :model="loginForm"
        :rules="loginRules"
        ref="loginFormRef"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            autocomplete="current-password"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <el-button type="text" class="forgot-password"> 忘记密码？ </el-button>
        </el-form-item>

        <el-form-item class="login-button-group">
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            @click="handleLogin"
            :loading="isLoading"
            :disabled="isLoading"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>还没有账号？</span>
        <el-button type="text" class="register-link" @click="goToRegister"> 立即注册 </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElForm } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

// 状态管理
const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

// 响应式数据
const loginFormRef = ref<InstanceType<typeof ElForm> | null>(null)
const isLoading = ref(false)

// 登录表单
const loginForm = ref({
  username: '',
  password: '',
  remember: true,
})

// 表单校验规则
const loginRules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
})

// 页面加载时检查
onMounted(() => {
  // 如果已登录，自动跳转到首页或指定页面
  if (userStore.isLogin) {
    const redirect = (route.query.redirect as string) || '/home'
    router.push(redirect)
  }
})

// 处理登录
const handleLogin = async () => {
  try {
    // 表单校验
    await loginFormRef.value?.validate()

    isLoading.value = true

    // 调用登录接口
    const success = await userStore.loginAction({
      username: loginForm.value.username,
      password: loginForm.value.password,
      remember: loginForm.value.remember,
    })

    if (success) {
      ElMessage.success('登录成功！')

      // 获取跳转地址（修复：正确处理 redirect 参数）
      const redirect = (route.query.redirect as string) || '/home'

      // 安全检查：避免跳转到登录/注册页
      if (redirect === '/login' || redirect === '/register') {
        router.push('/home')
      } else {
        router.push(redirect)
      }
    } else {
      ElMessage.error('用户名或密码错误，请重试')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请检查您的账号信息')
  } finally {
    isLoading.value = false
  }
}

// 前往注册页
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #e8f4f8 0%, #f0f8fb 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  padding: 40px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.login-subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.forgot-password {
  float: right;
  color: #1989fa !important;
  font-size: 14px;
}

.login-button-group {
  margin-top: 20px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.login-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.register-link {
  color: #1989fa !important;
  font-weight: 500;
}

// 响应式适配
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }
}
</style>
