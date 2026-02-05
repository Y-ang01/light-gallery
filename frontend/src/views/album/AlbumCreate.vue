<template>
  <div class="album-create-container">
    <div class="page-header">
      <el-button type="text" icon="ArrowLeft" class="back-button" @click="goBack"> 返回 </el-button>
      <h2 class="page-title">创建图片集</h2>
    </div>

    <el-card class="create-card">
      <el-form
        :model="albumForm"
        :rules="albumRules"
        ref="albumFormRef"
        label-width="100px"
        class="album-form"
      >
        <el-form-item label="图片集名称" prop="name">
          <el-input
            v-model="albumForm.name"
            placeholder="请输入图片集名称（1-100字符）"
            max="100"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="albumForm.description"
            type="textarea"
            placeholder="请输入图片集描述（可选）"
            :rows="4"
            max="500"
          />
        </el-form-item>

        <el-form-item label="访问权限" prop="permission">
          <el-radio-group v-model="albumForm.permission" @change="handlePermissionChange">
            <el-radio label="PUBLIC">
              <el-icon class="radio-icon">
                <Unlock />
              </el-icon>
              公开（所有人可见）
            </el-radio>
            <el-radio label="PROTECTED">
              <el-icon class="radio-icon">
                <LockFilled />
              </el-icon>
              密码保护（输入密码可见）
            </el-radio>
            <el-radio label="PRIVATE">
              <el-icon class="radio-icon">
                <Lock />
              </el-icon>
              私密（仅自己可见）
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="访问密码" prop="password" v-if="albumForm.permission === 'PROTECTED'">
          <el-input
            v-model="albumForm.password"
            type="password"
            placeholder="请设置4-20位密码"
            show-password
          />
          <div class="password-tip">密码建议包含字母和数字，提高安全性</div>
        </el-form-item>

        <el-form-item label=" ">
          <el-button
            type="primary"
            class="submit-button"
            @click="handleSubmit"
            :loading="isLoading"
          >
            创建图片集
          </el-button>
          <el-button type="text" class="cancel-button" @click="goBack"> 取消 </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm } from 'element-plus'
import { useAlbumStore } from '@/store/modules/album'

// 导入图标
import { ArrowLeft, Unlock, LockFilled, Lock } from '@element-plus/icons-vue'

// 状态管理
const albumStore = useAlbumStore()
const router = useRouter()

// 响应式数据
const albumFormRef = ref<InstanceType<typeof ElForm> | null>(null)
const isLoading = ref(false)

const albumForm = ref({
  name: '',
  description: '',
  permission: 'PUBLIC',
  password: '',
})

// 表单校验规则
const albumRules = ref({
  name: [
    { required: true, message: '请输入图片集名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度为1-100字符', trigger: 'blur' },
  ],
  permission: [{ required: true, message: '请选择访问权限', trigger: 'change' }],
  password: [
    { required: true, message: '请设置访问密码', trigger: 'blur' },
    { min: 4, max: 20, message: '密码长度为4-20字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_@#$%^&*()]+$/,
      message: '密码只能包含字母、数字和特殊字符',
      trigger: 'blur',
    },
  ],
})

// 方法
// 处理权限变更
const handlePermissionChange = () => {
  // 切换到非密码保护时清空密码
  if (albumForm.value.permission !== 'PROTECTED') {
    albumForm.value.password = ''
  }
}

// 处理提交
const handleSubmit = async () => {
  try {
    // 表单校验
    await albumFormRef.value?.validate()
    isLoading.value = true

    // 调用创建接口
    const success = await albumStore.createAlbumAction(
      albumForm.value.name,
      albumForm.value.description,
      albumForm.value.permission,
      albumForm.value.password,
    )

    if (success) {
      ElMessage.success('图片集创建成功')
      await router.push('/albums')
    } else {
      ElMessage.error('图片集创建失败')
    }
  } catch (error) {
    console.error('创建图片集失败:', error)
    ElMessage.error('创建失败，请检查表单信息')
  } finally {
    isLoading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}
</script>

<style scoped lang="scss">
.album-create-container {
  width: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.back-button {
  color: #666 !important;
}

.page-title {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.create-card {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
}

.album-form {
  margin-top: 20px;
}

.radio-icon {
  margin-right: 8px;
  font-size: 16px;
}

.el-radio {
  margin-right: 30px;
  margin-bottom: 10px;
}

.password-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.submit-button {
  width: 180px;
  height: 44px;
  font-size: 16px;
}

.cancel-button {
  margin-left: 16px;
  color: #666 !important;
}

// 响应式适配
@media (max-width: 768px) {
  .create-card {
    padding: 20px;
  }

  .el-radio {
    display: block;
    margin-right: 0;
  }
}
</style>
