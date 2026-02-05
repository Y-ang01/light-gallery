<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="card-header">
        <h2 class="register-title">账号注册</h2>
        <p class="register-desc">创建您的光影收藏馆账号</p>
      </div>

      <el-form
        :model="registerForm"
        :rules="registerRules"
        ref="registerFormRef"
        label-width="100px"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入3-20位用户名"
            prefix="User"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            placeholder="请输入有效邮箱"
            prefix="Message"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入6-20位密码"
            prefix="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label=" " prop="agreement">
          <el-checkbox v-model="registerForm.agreement">
            我已阅读并同意
            <el-button type="text" class="agreement-link">用户协议</el-button>
            和
            <el-button type="text" class="agreement-link">隐私政策</el-button>
          </el-checkbox>
        </el-form-item>

        <el-form-item label=" ">
          <el-button
            type="primary"
            class="register-btn"
            @click="handleRegister"
            :loading="isLoading"
          >
            注册账号
          </el-button>
          <div class="login-link">
            已有账号？
            <el-button type="text" @click="goToLogin"> 立即登录 </el-button>
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
const registerFormRef = ref<InstanceType<typeof ElForm> | null>(null)
const isLoading = ref(false)

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: false,
})

// 表单校验规则
const registerRules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效邮箱', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*[0-9])/, message: '密码必须包含字母和数字', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  agreement: [{ required: true, message: '请同意用户协议和隐私政策', trigger: 'change' }],
})

// 方法
// 处理注册
const handleRegister = async () => {
  try {
    // 表单校验
    await registerFormRef.value?.validate()
    isLoading.value = true

    // 调用注册接口
    const success = await userStore.registerAction(registerForm.value)

    if (success) {
      ElMessage.success('注册成功，请登录')

      // 跳转到登录页
      const redirect = route.query.redirect as string
      await router.push({
        path: '/login',
        query: redirect ? { redirect } : {},
      })
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error('注册失败，请检查表单信息')
  } finally {
    isLoading.value = false
  }
}

// 前往登录页
const goToLogin = () => {
  const redirect = route.query.redirect as string
  router.push({
    path: '/login',
    query: redirect ? { redirect } : {},
  })
}
</script>

<style scoped lang="scss">
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
  background-image: linear-gradient(135deg, #e8f4f8 0%, #f0f8fb 100%);
}

.register-card {
  width: 450px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border-radius: 12px !important;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-title {
  margin: 0 0 8px 0;
  color: #1989fa;
  font-size: 24px;
  font-weight: 600;
}

.register-desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.register-form {
  margin-top: 20px;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.login-link {
  margin-top: 16px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.agreement-link {
  color: #1989fa !important;
  padding: 0 !important;
  height: auto !important;
  font-size: 14px !important;
}

// 响应式适配
@media (max-width: 768px) {
  .register-card {
    width: 90%;
    padding: 20px;
  }
}
</style>
