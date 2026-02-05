<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="card-header">
        <h2 class="login-title">光影收藏馆</h2>
        <p class="login-desc">专业图片集管理展示平台</p>
      </div>

      <el-form
        :model="loginForm"
        :rules="loginRules"
        ref="loginFormRef"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="账号" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名或邮箱" prefix="User" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label=" " prop="remember">
          <el-checkbox v-model="loginForm.remember"> 记住登录状态（7天） </el-checkbox>
          <el-button type="text" class="forgot-password" @click="goToForgotPassword">
            忘记密码？
          </el-button>
        </el-form-item>

        <el-form-item label=" ">
          <el-button type="primary" class="login-btn" @click="handleLogin" :loading="isLoading">
            登录
          </el-button>
          <div class="register-link">
            还没有账号？
            <el-button type="text" @click="goToRegister"> 立即注册 </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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

const loginForm = ref({
  username: '',
  password: '',
  remember: false,
})

// 表单校验规则
const loginRules = ref({
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
})

// 方法
// 处理登录
const handleLogin = async () => {
  try {
    // 表单校验
    await loginFormRef.value?.validate()
    isLoading.value = true

    // 调用登录接口
    const success = await userStore.loginAction(loginForm.value)

    if (success) {
      ElMessage.success('登录成功')

      // 跳转到之前的页面或首页
      const redirect = route.query.redirect as string
      await router.push(redirect || '/home')
    } else {
      ElMessage.error('登录失败，请检查账号密码')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 前往注册页
const goToRegister = () => {
  const redirect = route.query.redirect as string
  router.push({
    path: '/register',
    query: redirect ? { redirect } : {},
  })
}

// 前往忘记密码页（暂未实现）
const goToForgotPassword = () => {
  ElMessage.info('忘记密码功能开发中')
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
  background-image: linear-gradient(135deg, #e8f4f8 0%, #f0f8fb 100%);
}

.login-card {
  width: 400px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-radius: 12px !important;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  margin: 0 0 8px 0;
  color: #1989fa;
  font-size: 24px;
  font-weight: 600;
}

.login-desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.register-link {
  margin-top: 16px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.forgot-password {
  float: right;
  color: #1989fa !important;
}

// 响应式适配
@media (max-width: 768px) {
  .login-card {
    width: 90%;
    padding: 20px;
  }
}
</style>
