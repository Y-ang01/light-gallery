<template>
  <div class="blog-create-container">
    <div class="page-header">
      <el-button type="text" icon="ArrowLeft" class="back-button" @click="goBack"> 返回 </el-button>
      <h2 class="page-title">发布博客</h2>
      <div class="header-actions">
        <el-button type="text" @click="handleSaveDraft"> 保存草稿 </el-button>
        <el-button type="primary" @click="handlePublish" :loading="isSubmitting">
          发布博客
        </el-button>
      </div>
    </div>

    <el-card class="create-card">
      <el-form
        :model="blogForm"
        :rules="blogRules"
        ref="blogFormRef"
        label-width="80px"
        class="blog-form"
      >
        <el-form-item label="博客标题" prop="title">
          <el-input
            v-model="blogForm.title"
            placeholder="请输入博客标题（1-200字符）"
            max="200"
            class="title-input"
          />
        </el-form-item>

        <el-form-item label="封面图片" prop="coverImageUrl">
          <el-upload
            class="cover-upload"
            :auto-upload="false"
            :on-change="handleCoverUpload"
            :file-list="coverFileList"
            list-type="picture-card"
            action="#"
          >
            <<i class="el-icon-plus" />
          </el-upload>
          <el-image
            v-if="blogForm.coverImageUrl"
            :src="blogForm.coverImageUrl"
            class="cover-preview"
            fit="cover"
          />
        </el-form-item>

        <el-form-item label="博客内容" prop="content">
          <div class="editor-container">
            <el-tabs v-model="activeTab" class="editor-tabs">
              <el-tab-pane label="编辑" name="edit">
                <textarea
                  v-model="blogForm.content"
                  class="markdown-editor"
                  placeholder="支持Markdown语法，可插入图片、链接等"
                  @input="handleEditorInput"
                ></textarea>
                <div class="editor-toolbar">
                  <el-button type="text" icon="Bold" @click="insertMarkdown('**', '**')">
                    加粗
                  </el-button>
                  <el-button type="text" icon="Italic" @click="insertMarkdown('*', '*')">
                    斜体
                  </el-button>
                  <el-button type="text" icon="Link" @click="insertLink"> 插入链接 </el-button>
                  <el-button type="text" icon="Image" @click="openImageUpload">
                    插入图片
                  </el-button>
                  <el-button type="text" icon="Document" @click="openAttachmentUpload">
                    上传附件
                  </el-button>
                  <el-button type="text" icon="List" @click="insertMarkdown('- ', '')">
                    列表
                  </el-button>
                  <el-button type="text" icon="Header" @click="insertHeading"> 标题 </el-button>
                </div>
              </el-tab-pane>
              <el-tab-pane label="预览" name="preview">
                <div class="preview-container" v-html="renderedContent"></div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-form-item>

        <el-form-item label="标签" prop="tags">
          <el-tag-input
            v-model="blogForm.tags"
            placeholder="输入标签，按Enter确认"
            :max="5"
            class="tag-input"
          />
          <div class="tag-tip">最多添加5个标签，每个标签不超过10字符</div>
        </el-form-item>

        <el-form-item label="发布设置">
          <el-checkbox v-model="blogForm.isPrivate"> 私密博客（仅自己可见） </el-checkbox>
        </el-form-item>
      </el-form>
    </el-card>
  </div>

  <!-- 图片上传弹窗 -->
  <el-dialog
    v-model="imageUploadVisible"
    title="插入图片"
    width="600px"
    :close-on-click-modal="false"
  >
    <el-upload
      class="image-uploader"
      drag
      :auto-upload="false"
      :on-change="handleImageUpload"
      :file-list="imageFileList"
      accept="image/jpeg,image/png,image/gif"
      action="#"
    >
      <<<i class="el-icon-upload" />
      <div class="el-upload__text">将图片拖到此处，或<em>点击上传</em></div>
      <div class="el-upload__tip" slot="tip">支持JPG、PNG、GIF格式，单张图片最大50MB</div>
    </el-upload>
    <template #footer>
      <el-button @click="imageUploadVisible = false">取消</el-button>
      <el-button type="primary" @click="handleConfirmImageUpload" :loading="isUploading">
        插入图片
      </el-button>
    </template>
  </el-dialog>

  <!-- 附件上传弹窗 -->
  <el-dialog
    v-model="attachmentUploadVisible"
    title="上传附件"
    width="600px"
    :close-on-click-modal="false"
  >
    <el-upload
      class="attachment-uploader"
      :auto-upload="false"
      :on-change="handleAttachmentFileChange"
      :file-list="attachmentFileList"
      accept=".pdf,.doc,.docx,.zip"
      action="#"
    >
      <el-button type="primary" icon="Upload">选择文件</el-button>
      <div class="el-upload__tip" slot="tip">支持PDF、Word、ZIP格式，单个文件最大50MB</div>
    </el-upload>
    <template #footer>
      <el-button @click="attachmentUploadVisible = false">取消</el-button>
      <el-button type="primary" @click="handleConfirmAttachmentUpload" :loading="isUploading">
        上传并插入
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm, ElMessageBox } from 'element-plus'
import { useBlogStore } from '@/store/modules/blog'
import { renderMarkdown } from '@/utils/markdown'

// 导入图标
import {
  ArrowLeft,
  Bold,
  Italic,
  Link,
  Image,
  Document,
  List,
  Header,
  Upload,
} from '@element-plus/icons-vue'

// 状态管理
const blogStore = useBlogStore()
const router = useRouter()

// 响应式数据
const blogFormRef = ref<InstanceType<typeof ElForm> | null>(null)
const isSubmitting = ref(false)
const isUploading = ref(false)
const activeTab = ref('edit')

// 博客表单
const blogForm = ref({
  title: '',
  content: '',
  coverImageUrl: '',
  tags: [] as string[],
  isPrivate: false,
})

// 表单校验规则
const blogRules = ref({
  title: [
    { required: true, message: '请输入博客标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度为1-200字符', trigger: 'blur' },
  ],
  content: [
    { required: true, message: '请输入博客内容', trigger: 'blur' },
    { min: 10, message: '内容长度不少于10字符', trigger: 'blur' },
  ],
  tags: [
    {
      validator: (rule, value: string[], callback) => {
        // 验证标签数量
        if (value.length > 5) {
          callback(new Error('最多添加5个标签'))
          return
        }

        // 验证每个标签长度
        for (const tag of value) {
          if (tag.length > 10) {
            callback(new Error('每个标签长度不超过10字符'))
            return
          }
        }

        callback()
      },
      trigger: 'change',
    },
  ],
})

// 上传相关
const coverFileList = ref<any[]>([])
const imageFileList = ref<any[]>([])
const attachmentFileList = ref<any[]>([])
const imageUploadVisible = ref(false)
const attachmentUploadVisible = ref(false)

// 计算属性
const renderedContent = computed(() => {
  return renderMarkdown(blogForm.value.content)
})

// 方法
// 处理编辑器输入
const handleEditorInput = () => {
  // 自动保存草稿（防抖）
  if (blogForm.value.content.length > 0) {
    debouncedAutoSaveDraft()
  }
}

// 防抖函数
const debounce = (func: () => void, delay = 3000) => {
  let timeoutId: NodeJS.Timeout
  return () => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(func, delay)
  }
}

// 自动保存草稿（防抖）
const debouncedAutoSaveDraft = debounce(() => {
  if (blogForm.value.title || blogForm.value.content) {
    handleSaveDraft(true)
  }
})

// 处理封面上传
const handleCoverUpload = async (uploadFile: any, list: any[]) => {
  coverFileList.value = list

  if (list.length > 0) {
    try {
      isUploading.value = true
      const file = list[0].raw
      const formData = new FormData()
      formData.append('file', file)

      // 上传封面图片
      const url = await blogStore.uploadBlogAttachmentAction(file)
      if (url) {
        blogForm.value.coverImageUrl = url
      }
    } catch (error) {
      console.error('上传封面失败:', error)
      ElMessage.error('上传封面失败')
    } finally {
      isUploading.value = false
    }
  } else {
    blogForm.value.coverImageUrl = ''
  }
}

// 打开图片上传弹窗
const openImageUpload = () => {
  imageFileList.value = []
  imageUploadVisible.value = true
}

// 处理图片上传
const handleImageUpload = (uploadFile: any, list: any[]) => {
  imageFileList.value = list
}

// 确认插入图片
const handleConfirmImageUpload = async () => {
  if (imageFileList.value.length === 0) {
    ElMessage.warning('请选择图片')
    return
  }

  try {
    isUploading.value = true
    const files = imageFileList.value.map((item) => item.raw)
    const imageUrls: string[] = []

    for (const file of files) {
      const url = await blogStore.uploadBlogAttachmentAction(file)
      if (url) {
        imageUrls.push(url)
      }
    }

    // 插入图片到内容
    const imageMarkdown = imageUrls.map((url) => `![图片](${url})`).join('\n\n')
    blogForm.value.content += '\n\n' + imageMarkdown

    imageUploadVisible.value = false
    imageFileList.value = []
  } catch (error) {
    console.error('上传图片失败:', error)
    ElMessage.error('上传图片失败')
  } finally {
    isUploading.value = false
  }
}

// 打开附件上传弹窗
const openAttachmentUpload = () => {
  attachmentFileList.value = []
  attachmentUploadVisible.value = true
}

// 处理附件上传
const handleAttachmentFileChange = (uploadFile: any, list: any[]) => {
  attachmentFileList.value = list
}

// 确认上传附件
const handleConfirmAttachmentUpload = async () => {
  if (attachmentFileList.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }

  try {
    isUploading.value = true
    const file = attachmentFileList.value[0].raw
    const url = await blogStore.uploadBlogAttachmentAction(file)

    if (url) {
      // 插入附件链接到内容
      blogForm.value.content += `\n\n[${file.name}](${url})`
      attachmentUploadVisible.value = false
      attachmentFileList.value = []
    }
  } catch (error) {
    console.error('上传附件失败:', error)
    ElMessage.error('上传附件失败')
  } finally {
    isUploading.value = false
  }
}

// 插入Markdown格式
const insertMarkdown = (prefix: string, suffix: string) => {
  const textarea = document.querySelector('.markdown-editor') as HTMLTextAreaElement
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = textarea.value.substring(start, end)

  // 插入格式
  const newContent =
    textarea.value.substring(0, start) +
    prefix +
    selectedText +
    suffix +
    textarea.value.substring(end)

  blogForm.value.content = newContent

  // 移动光标
  textarea.focus()
  textarea.selectionStart = textarea.selectionEnd = start + prefix.length + selectedText.length
}

// 插入链接
const insertLink = () => {
  const url = prompt('请输入链接地址：')
  const text = prompt('请输入链接文本：')

  if (url && text) {
    insertMarkdown(`[${text}]`, `(${url})`)
  }
}

// 插入标题
const insertHeading = () => {
  const level = prompt('请输入标题级别（1-6）：')
  if (level && /^[1-6]$/.test(level)) {
    insertMarkdown('#'.repeat(Number(level)) + ' ', '\n')
  }
}

// 保存草稿
const handleSaveDraft = async (isAutoSave = false) => {
  try {
    // 自动保存无需校验标题和内容
    if (!isAutoSave) {
      await blogFormRef.value?.validate({
        trigger: 'blur',
        only: ['title'],
      })
    }

    const success = await blogStore.createBlogPostAction(
      blogForm.value.title || '无标题草稿',
      blogForm.value.content,
      true, // 保存为草稿
      blogForm.value.isPrivate,
      blogForm.value.coverImageUrl,
      blogForm.value.tags,
    )

    if (success) {
      if (!isAutoSave) {
        ElMessage.success('草稿保存成功')
      }
    } else {
      ElMessage.error('草稿保存失败')
    }
  } catch (error) {
    console.error('保存草稿失败:', error)
    if (!isAutoSave) {
      ElMessage.error('草稿保存失败')
    }
  }
}

// 发布博客
const handlePublish = async () => {
  try {
    await blogFormRef.value?.validate()
    isSubmitting.value = true

    const success = await blogStore.createBlogPostAction(
      blogForm.value.title,
      blogForm.value.content,
      false, // 发布
      blogForm.value.isPrivate,
      blogForm.value.coverImageUrl,
      blogForm.value.tags,
    )

    if (success) {
      ElMessage.success('博客发布成功')
      await router.push('/blog')
    } else {
      ElMessage.error('博客发布失败')
    }
  } catch (error) {
    console.error('发布博客失败:', error)
    ElMessage.error('发布博客失败，请检查表单信息')
  } finally {
    isSubmitting.value = false
  }
}

// 返回上一页
const goBack = () => {
  if (blogForm.value.title || blogForm.value.content) {
    ElMessageBox.confirm('当前内容未保存，确定要离开吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => {
      router.back()
    })
  } else {
    router.back()
  }
}

// 监听标签变化，去重和截取
watch(
  () => blogForm.value.tags,
  (tags) => {
    // 去重
    const uniqueTags = [...new Set(tags)]
    // 截取前5个
    const limitedTags = uniqueTags.slice(0, 5)
    // 修剪每个标签长度
    const trimmedTags = limitedTags.map((tag) => tag.trim().slice(0, 10))

    blogForm.value.tags = trimmedTags.filter((tag) => tag)
  },
  { deep: true },
)
</script>

<style scoped lang="scss">
.blog-create-container {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
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

.header-actions {
  display: flex;
  gap: 10px;
}

.create-card {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
}

.blog-form {
  margin-top: 20px;
}

.title-input {
  font-size: 18px;
  padding: 12px;
}

.cover-upload {
  width: 180px;
  margin-bottom: 16px;
}

.cover-preview {
  width: 180px;
  height: 120px;
  border-radius: 8px;
}

.editor-container {
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
}

.editor-tabs {
  --el-tabs-header-height: 44px;
}

.markdown-editor {
  width: 100%;
  min-height: 400px;
  padding: 16px;
  border: none;
  resize: vertical;
  font-size: 14px;
  line-height: 1.8;
  outline: none;
  font-family: inherit;
}

.editor-toolbar {
  display: flex;
  gap: 10px;
  padding: 8px 16px;
  background-color: #f5f7fa;
  border-top: 1px solid #e6e6e6;
}

.preview-container {
  width: 100%;
  min-height: 400px;
  padding: 16px;
  background-color: #f9f9fa;
  overflow-y: auto;
}

.preview-container h1,
.preview-container h2,
.preview-container h3 {
  margin: 16px 0;
  color: #2c3e50;
}

.preview-container p {
  margin: 8px 0;
  line-height: 1.8;
  color: #333;
}

.preview-container img {
  max-width: 100%;
  border-radius: 8px;
  margin: 16px 0;
}

.preview-container a {
  color: #1989fa;
  text-decoration: underline;
}

.tag-input {
  width: 100%;
}

.tag-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

// 响应式适配
@media (max-width: 768px) {
  .create-card {
    padding: 20px;
  }

  .cover-upload {
    width: 100%;
  }

  .cover-preview {
    width: 100%;
    height: auto;
  }
}
</style>
