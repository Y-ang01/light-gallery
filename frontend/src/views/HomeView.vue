<!-- 文件路径: frontend/src/views/HomeView.vue -->
<template>
  <div class="home">
    <section class="hero">
      <div class="hero-content">
        <h1>光影收藏馆</h1>
        <p>专业图片集管理展示平台</p>
        <div class="hero-actions">
          <router-link to="/gallery" class="btn primary">浏览图片库</router-link>
          <router-link to="/register" class="btn secondary" v-if="!authStore.isAuthenticated"
            >立即注册</router-link
          >
        </div>
      </div>
    </section>

    <section class="features">
      <div class="container">
        <h2>核心功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🖼️</div>
            <h3>图片集管理</h3>
            <p>创建、编辑和管理您的图片集，支持多种展示模式</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📸</div>
            <h3>RAW格式支持</h3>
            <p>完整支持所有主流相机的RAW格式文件存储</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>隐私保护</h3>
            <p>灵活的权限设置，保护您的作品安全</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3>博客系统</h3>
            <p>分享您的摄影故事和技巧</p>
          </div>
        </div>
      </div>
    </section>

    <section class="recent-galleries" v-if="recentGalleries.length > 0">
      <div class="container">
        <h2>最新图片集</h2>
        <div class="galleries-grid">
          <div v-for="gallery in recentGalleries" :key="gallery.id" class="gallery-card">
            <div class="gallery-info">
              <h4>{{ gallery.name }}</h4>
              <p>{{ gallery.description }}</p>
              <span class="gallery-meta">{{ gallery.imageCount }} 张图片</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

interface Gallery {
  id: string
  name: string
  description: string
  coverImage: string
  imageCount: number
}

const authStore = useAuthStore()
const recentGalleries = ref<Gallery[]>([])

onMounted(async () => {
  // 模拟获取最新图片集数据
  recentGalleries.value = [
    {
      id: '1',
      name: '自然风光',
      description: '壮丽的自然景观摄影作品',
      coverImage: '/api/placeholder/300/200',
      imageCount: 24,
    },
    {
      id: '2',
      name: '城市建筑',
      description: '现代与古典建筑的完美结合',
      coverImage: '/api/placeholder/300/200',
      imageCount: 18,
    },
  ]
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 100px 0;
  text-align: center;
}

.hero-content h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s;
}

.btn.primary {
  background: #fff;
  color: #667eea;
}

.btn.secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.features {
  padding: 80px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.features h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  border-radius: 8px;
  background: #f8f9fa;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.recent-galleries {
  padding: 80px 0;
  background: #f8f9fa;
}

.galleries-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.gallery-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.gallery-cover {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.gallery-info {
  padding: 1rem;
}

.gallery-meta {
  color: #666;
  font-size: 0.9rem;
}
</style>
