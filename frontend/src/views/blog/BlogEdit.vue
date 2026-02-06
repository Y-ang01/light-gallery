<!-- src/views/blog/BlogEdit.vue -->
<template>
  <div class="blog-edit-container">
    <div class="page-header">
      <el-button type="text" icon="ArrowLeft" class="back-button" @click="goBack"> 返回 </el-button>
      <h2 class="page-title">编辑博客</h2>
      <div class="header-actions">
        <el-button type="text" @click="handleSaveDraft"> 保存草稿 </el-button>
        <el-button type="primary" @click="handleUpdate" :loading="isSubmitting">
          发布博客
        </el-button>
      </div>
    </div>

    <el-card class="edit-card">
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
            <i class="el-icon-plus" />
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
      <i class="el-icon-upload" />
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElForm, ElMessageBox } from 'element-plus'
import { useBlogStore } from '@/store/modules/blog'
import { renderMarkdown } from '@/utils/markdown'
import { formatDateTime } from '@/utils/format'

// 导入图标
import { ArrowLeft, Bold, Italic, Link, Image, Upload } from '@element-plus/icons-vue'

// 状态管理
const blogStore = useBlogStore()
const router = useRouter()
const route = useRoute()

// 响应式数据
const blogFormRef = ref<InstanceType<typeof ElForm> | null>(null)
const isLoading = ref(true)
const isSubmitting = ref(false)
const isUploading = ref(false)
const activeTab = ref('edit')
const blogId = ref(route.params.id as string)

// 博客表单
const blogForm = ref({
  title: '',
  content: '',
  coverImageUrl: '',
  tags: [] as string[],
  isPrivate: false,
  isDraft: false,
  createdAt: '',
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
        if (value.length > 5) {
          callback(new Error('最多添加5个标签'))
          return
        }

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
const imageUploadVisible = ref(false)

// 计算属性
const renderedContent = computed(() => {
  return renderMarkdown(blogForm.value.content)
})

// 方法
onMounted(() => {
  fetchBlogDetail()
})

// 获取博客详情
const fetchBlogDetail = async () => {
  try {
    isLoading.value = true
    const success = await blogStore.fetchBlogDetail(blogId.value)

    if (success && blogStore.currentBlog) {
      const blog = blogStore.currentBlog
      blogForm.value = {
        title: blog.title || '',
        content: blog.content || '',
        coverImageUrl: blog.cover_image_url || '',
        tags: blog.tags || [],
        isPrivate: blog.is_private || false,
        isDraft: blog.is_draft || false,
        createdAt: blog.created_at || '',
      }

      // 设置封面文件列表
      if (blogForm.value.coverImageUrl) {
        coverFileList.value = [
          {
            name: '封面图片',
            url: blogForm.value.coverImageUrl,
          },
        ]
      }
    } else {
      ElMessage.error('获取博客详情失败')
      router.back()
    }
  } catch (error) {
    console.error('获取博客详情失败:', error)
    ElMessage.error('获取博客详情失败')
    router.back()
  } finally {
    isLoading.value = false
  }
}

// 处理封面上传
const handleCoverUpload = async (uploadFile: any, list: any[]) => {
  coverFileList.value = list

  if (list.length > 0) {
    try {
      isUploading.value = true
      const file = list[0].raw
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

// 插入Markdown格式
const insertMarkdown = (prefix: string, suffix: string) => {
  const textarea = document.querySelector('.markdown-editor') as HTMLTextAreaElement
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = textarea.value.substring(start, end)

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

// 保存草稿
const handleSaveDraft = async () => {
  try {
    await blogFormRef.value?.validate({
      trigger: 'blur',
      only: ['title'],
    })

    isSubmitting.value = true

    const success = await blogStore.updateBlogPostAction(blogId.value, {
      title: blogForm.value.title || '无标题草稿',
      content: blogForm.value.content,
      is_draft: true,
      is_private: blogForm.value.isPrivate,
      cover_image_url: blogForm.value.coverImageUrl,
      tags: blogForm.value.tags,
    })

    if (success) {
      ElMessage.success('草稿保存成功')
    } else {
      ElMessage.error('草稿保存失败')
    }
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('草稿保存失败')
  } finally {
    isSubmitting.value = false
  }
}

// 更新博客
const handleUpdate = async () => {
  try {
    await blogFormRef.value?.validate()
    isSubmitting.value = true

    const success = await blogStore.updateBlogPostAction(blogId.value, {
      title: blogForm.value.title,
      content: blogForm.value.content,
      is_draft: false,
      is_private: blogForm.value.isPrivate,
      cover_image_url: blogForm.value.coverImageUrl,
      tags: blogForm.value.tags,
    })

    if (success) {
      ElMessage.success('博客更新成功')
      router.push(`/blog/${blogId.value}`)
    } else {
      ElMessage.error('博客更新失败')
    }
  } catch (error) {
    console.error('更新博客失败:', error)
    ElMessage.error('博客更新失败，请检查表单信息')
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

// 监听标签变化
watch(
  () => blogForm.value.tags,
  (tags) => {
    const uniqueTags = [...new Set(tags)]
    const limitedTags = uniqueTags.slice(0, 5)
    const trimmedTags = limitedTags.map((tag) => tag.trim().slice(0, 10))

    blogForm.value.tags = trimmedTags.filter((tag) => tag)
  },
  { deep: true },
)
</script>

<style scoped lang="scss">
.blog-edit-container {
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

.edit-card {
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
  .edit-card {
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
