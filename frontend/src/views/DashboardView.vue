<!-- 文件路径: frontend/src/views/DashboardView.vue -->
<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>欢迎回来，{{ authStore.user?.username }}！</h1>
      <p>管理您的图片集和博客内容</p>
    </div>

    <div class="dashboard-stats">
      <div class="stat-card">
        <div class="stat-icon">🖼️</div>
        <div class="stat-info">
          <h3>{{ stats.albumCount }}</h3>
          <p>图片集</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📸</div>
        <div class="stat-info">
          <h3>{{ stats.imageCount }}</h3>
          <p>图片数量</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-info">
          <h3>{{ stats.blogCount }}</h3>
          <p>博客文章</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <h3>{{ stats.followerCount }}</h3>
          <p>关注者</p>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="content-section">
        <div class="section-header">
          <h2>最近图片集</h2>
          <router-link to="/albums" class="view-all">查看全部</router-link>
        </div>
        <div class="albums-grid">
          <div v-for="album in recentAlbums" :key="album.id" class="album-card">
            <div class="album-cover"></div>
            <div class="album-info">
              <h4>{{ album.name }}</h4>
              <p>{{ album.imageCount }} 张图片</p>
              <span class="album-date">{{ formatDate(album.createdAt) }}</span>
            </div>
            <div class="album-actions">
              <button @click="editAlbum(album.id)" class="btn small">编辑</button>
              <button @click="viewAlbum(album.id)" class="btn small primary">查看</button>
            </div>
          </div>
        </div>
        <div v-if="recentAlbums.length === 0" class="empty-state">
          <p>还没有创建任何图片集</p>
          <router-link to="/albums/create" class="btn primary">创建第一个图片集</router-link>
        </div>
      </div>

      <div class="content-section">
        <div class="section-header">
          <h2>最近博客文章</h2>
          <router-link to="/blog" class="view-all">查看全部</router-link>
        </div>
        <div class="blog-list">
          <div v-for="post in recentPosts" :key="post.id" class="blog-item">
            <h4>{{ post.title }}</h4>
            <p>{{ post.excerpt }}</p>
            <div class="blog-meta">
              <span>{{ formatDate(post.createdAt) }}</span>
              <span>{{ post.viewCount }} 次阅读</span>
            </div>
          </div>
        </div>
        <div v-if="recentPosts.length === 0" class="empty-state">
          <p>还没有发布任何博客文章</p>
          <router-link to="/blog/create" class="btn primary">撰写第一篇博客</router-link>
        </div>
      </div>

      <div class="quick-actions">
        <h3>快速操作</h3>
        <div class="actions-grid">
          <router-link to="/albums/create" class="action-card">
            <div class="action-icon">➕</div>
            <span>创建图片集</span>
          </router-link>
          <router-link to="/upload" class="action-card">
            <div class="action-icon">📤</div>
            <span>上传图片</span>
          </router-link>
          <router-link to="/blog/create" class="action-card">
            <div class="action-icon">✏️</div>
            <span>写博客</span>
          </router-link>
          <router-link to="/profile" class="action-card">
            <div class="action-icon">👤</div>
            <span>编辑资料</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

interface Album {
  id: string
  name: string
  coverImage: string
  imageCount: number
  createdAt: string
}

interface BlogPost {
  id: string
  title: string
  excerpt: string
  viewCount: number
  createdAt: string
}

interface DashboardStats {
  albumCount: number
  imageCount: number
  blogCount: number
  followerCount: number
}

const authStore = useAuthStore()
const router = useRouter()

const stats = reactive<DashboardStats>({
  albumCount: 0,
  imageCount: 0,
  blogCount: 0,
  followerCount: 0,
})

const recentAlbums = ref<Album[]>([])
const recentPosts = ref<BlogPost[]>([])

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const editAlbum = (albumId: string) => {
  router.push(`/albums/${albumId}/edit`)
}

const viewAlbum = (albumId: string) => {
  router.push(`/albums/${albumId}`)
}

onMounted(async () => {
  // 模拟获取仪表板数据
  await loadDashboardData()
})

const loadDashboardData = async () => {
  // 模拟API调用
  setTimeout(() => {
    stats.albumCount = 3
    stats.imageCount = 45
    stats.blogCount = 2
    stats.followerCount = 12

    recentAlbums.value = [
      {
        id: '1',
        name: '自然风光摄影',
        coverImage: '/api/placeholder/200/150',
        imageCount: 15,
        createdAt: '2024-01-15',
      },
      {
        id: '2',
        name: '城市建筑',
        coverImage: '/api/placeholder/200/150',
        imageCount: 8,
        createdAt: '2024-01-10',
      },
    ]

    recentPosts.value = [
      {
        id: '1',
        title: '如何拍摄完美的日落照片',
        excerpt: '分享一些拍摄日落的技巧和经验...',
        viewCount: 156,
        createdAt: '2024-01-12',
      },
      {
        id: '2',
        title: 'RAW格式处理指南',
        excerpt: '详细介绍RAW格式的优势和处理方法...',
        viewCount: 89,
        createdAt: '2024-01-08',
      },
    ]
  }, 500)
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.dashboard-header p {
  color: #666;
  font-size: 1.1rem;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info h3 {
  font-size: 2rem;
  color: #333;
  margin: 0;
}

.stat-info p {
  color: #666;
  margin: 0;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.content-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: #333;
}

.view-all {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.albums-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.album-card {
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  overflow: hidden;
}

.album-cover {
  width: 100%;
  height: 150px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.album-info {
  padding: 1rem;
}

.album-info h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.album-info p {
  margin: 0 0 0.5rem 0;
  color: #666;
}

.album-date {
  font-size: 0.875rem;
  color: #999;
}

.album-actions {
  padding: 0 1rem 1rem 1rem;
  display: flex;
  gap: 0.5rem;
}

.blog-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.blog-item {
  padding: 1rem;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
}

.blog-item h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.blog-item p {
  margin: 0 0 0.5rem 0;
  color: #666;
}

.blog-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.quick-actions {
  margin-top: 2rem;
}

.quick-actions h3 {
  margin-bottom: 1rem;
  color: #333;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  transition: all 0.3s;
}

.action-card:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn.small {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

.btn.primary {
  background: #667eea;
  color: white;
}

.btn:not(.primary) {
  background: #f8f9fa;
  color: #333;
}
</style>
