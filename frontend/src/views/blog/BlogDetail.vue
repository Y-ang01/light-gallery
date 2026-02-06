<!-- src/views/blog/BlogDetail.vue -->
<template>
  <div class="blog-detail-container">
    <div class="page-header">
      <el-button
        type="text"
        icon="ArrowLeft"
        class="back-button"
        @click="goBack"
      >
        返回
      </el-button>
      <h2 class="page-title">{{ blogForm.title || '博客详情' }}</h2>
      <div class="header-actions">
        <el-button
          type="text"
          icon="Edit"
          @click="goToEdit"
          v-if="isOwner"
        >
          编辑博客
        </el-button>
        <el-button
          type="text"
          icon="Delete"
          @click="handleDelete"
          v-if="isOwner"
          danger
        >
          删除博客
        </el-button>
      </div>
    </div>

    <el-card class="detail-card" v-loading="isLoading">
      <!-- 博客封面 -->
      <div class="blog-cover" v-if="blogForm.coverImageUrl">
        <el-image
          :src="blogForm.coverImageUrl"
          fit="cover"
          class="cover-image"
        />
      </div>

      <!-- 博客元信息 -->
      <div class="blog-meta">
        <span class="publish-time">
          <el-icon><Clock /></el-icon>
          {{ formatDateTime(blogForm.createdAt, 'YYYY-MM-DD HH:mm') }}
        </span>
        <span class="author" v-if="blogForm.author">
          <el-icon><User /></el-icon>
          {{ blogForm.author }}
        </span>
        <span class="status" :class="blogForm.isDraft ? 'draft' : 'published'">
          <el-icon><Document /></el-icon>
          {{ blogForm.isDraft ? '草稿' : '已发布' }}
        </span>
        <span class="visibility" v-if="blogForm.isPrivate">
          <el-icon><Lock /></el-icon>
          私密博客
        </span>
      </div>

      <!-- 标签 -->
      <div class="blog-tags" v-if="blogForm.tags && blogForm.tags.length">
        <el-tag
          v-for="tag in blogForm.tags"
          :key="tag"
          size="small"
          class="tag-item"
        >
          {{ tag }}
        </el-tag>
      </div>

      <!-- 博客内容 -->
      <div class="blog-content" v-html="renderedContent"></div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="!isLoading && !blogForm.content">
        <el-empty description="暂无博客内容" />
      </div>
    </el-card>

    <!-- 评论区（预留） -->
    <div class="comments-section" v-if="!blogForm.isPrivate && !blogForm.isDraft">
      <h3 class="comments-title">评论区</h3>
      <el-card class="comments-card">
        <el-empty description="暂无评论，快来抢沙发~" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBlogStore } from '@/store/modules/blog'
import { useUserStore } from '@/store/modules/user'
import { formatDateTime } from '@/utils/format'
import { renderMarkdown } from '@/utils/markdown'

// 导入图标
import {
  ArrowLeft,
  Edit,
  Delete,
  Clock,
  User,
  Document,
  Lock
} from '@element-plus/icons-vue'

// 状态管理
const blogStore = useBlogStore()
const userStore = useUserStore()
const router = useRouter()
const route = useRoute()

// 响应式数据
const isLoading = ref(true)
const blogId = ref(route.params.id as string)

// 博客表单数据
const blogForm = ref({
  id: '',
  title: '',
  content: '',
  coverImageUrl: '',
  tags: [] as string[],
  isDraft: false,
  isPrivate: false,
  createdAt: '',
  updatedAt: '',
  author: '',
  authorId: ''
})

// 计算属性
const renderedContent = computed(() => {
  return renderMarkdown(blogForm.value.content)
})

const isOwner = computed(() => {
  return userStore.isLogin && blogForm.value.authorId === userStore.userInfo.id
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
        id: blog.id,
        title: blog.title,
        content: blog.content,
        coverImageUrl: blog.cover_image_url || '',
        tags: blog.tags || [],
        isDraft: blog.is_draft || false,
        isPrivate: blog.is_private || false,
        createdAt: blog.created_at,
        updatedAt: blog.updated_at,
        author: blog.user?.username || '',
        authorId: blog.user_id || ''
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

// 返回上一页
const goBack = () => {
  router.back()
}

// 前往编辑页面
const goToEdit = () => {
  router.push(`/blog/edit/${blogId.value}`)
}

// 删除博客
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这篇博客吗？删除后将无法恢复',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const success = await blogStore.deleteBlogPostAction(blogId.value)
    if (success) {
      ElMessage.success('博客删除成功')
      router.push('/blog')
    } else {
      ElMessage.error('博客删除失败')
    }
  } catch (error) {
    // 用户取消删除
  }
}
</script>

<style scoped lang="scss">
.blog-detail-container {
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
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.detail-card {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
}

.blog-cover {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: auto;
  max-height: 500px;
}

.blog-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
  color: #666;
}

.blog-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status.draft {
  color: #f90;
}

.status.published {
  color: #1989fa;
}

.visibility {
  color: #999;
}

.blog-tags {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  background-color: #f5f7fa;
  color: #666;
}

.blog-content {
  line-height: 1.8;
  font-size: 16px;
  color: #333;
}

.blog-content h1,
.blog-content h2,
.blog-content h3 {
  margin: 24px 0 16px 0;
  color: #2c3e50;
  font-weight: 600;
}

.blog-content p {
  margin: 12px 0;
}

.blog-content img {
  max-width: 100%;
  border-radius: 8px;
  margin: 16px 0;
}

.blog-content a {
  color: #1989fa;
  text-decoration: underline;
}

.blog-content pre {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.blog-content code {
  font-family: 'Consolas', 'Monaco', monospace;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.comments-section {
  max-width: 1200px;
  margin: 30px auto 0;
}

.comments-title {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.comments-card {
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 8px !important;
}

// 响应式适配
@media (max-width: 768px) {
  .detail-card {
    padding: 20px;
  }

  .blog-content {
    font-size: 14px;
  }

  .blog-meta {
    gap: 8px;
  }
}
</style>
