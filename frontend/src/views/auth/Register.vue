<!-- src/views/auth/Register.vue - 修复版 -->
<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h2 class="register-title">创建账号</h2>
        <p class="register-subtitle">注册后即可使用全部功能</p>
      </div>

      <el-form
        :model="registerForm"
        :rules="registerRules"
        ref="registerFormRef"
        class="register-form"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-20字符）"
            prefix-icon="User"
            size="large"
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
            size="large"
            autocomplete="email"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            prefix-icon="Lock"
            size="large"
            autocomplete="new-password"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            prefix-icon="Lock"
            size="large"
            autocomplete="new-password"
            show-password
          />
        </el-form-item>

        <el-form-item class="register-button-group">
          <el-button
            type="primary"
            size="large"
            class="register-btn"
            @click="handleRegister"
            :loading="isLoading"
            :disabled="isLoading"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <span>已有账号？</span>
        <el-button type="text" class="login-link" @click="goToLogin"> 立即登录 </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

// 状态管理
const userStore = useUserStore()
const router = useRouter()

// 响应式数据
const registerFormRef = ref<InstanceType<typeof ElForm> | null>(null)
const isLoading = ref(false)

// 注册表单
const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

// 表单校验规则
const registerRules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== registerForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
})

// 处理注册
const handleRegister = async () => {
  try {
    // 表单校验
    await registerFormRef.value?.validate()

    isLoading.value = true

    // 调用注册接口
    const success = await userStore.registerAction({
      username: registerForm.value.username,
      email: registerForm.value.email,
      password: registerForm.value.password,
    })

    if (success) {
      ElMessage.success('注册成功！请登录')
      // 注册成功后跳转到登录页，并携带邮箱
      router.push({
        path: '/login',
        query: { username: registerForm.value.username },
      })
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } catch (error) {
    console.error('注册失败:', error)
    // 表单校验失败的情况已经由Element Plus处理
    if (!(error instanceof Error && error.message.includes('validator'))) {
      ElMessage.error('注册失败，请检查表单信息')
    }
  } finally {
    isLoading.value = false
  }
}

// 前往登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped lang="scss">
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #fdf2f8 0%, #fef7fb 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  padding: 40px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.register-subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.register-form {
  margin-bottom: 20px;
}

.register-button-group {
  margin-top: 20px;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.register-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.login-link {
  color: #1989fa !important;
  font-weight: 500;
}

// 响应式适配
@media (max-width: 480px) {
  .register-card {
    padding: 30px 20px;
  }
}
</style>
