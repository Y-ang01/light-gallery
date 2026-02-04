<!-- 文件路径: frontend/src/views/GalleryView.vue -->
<template>
  <div class="gallery">
    <div class="gallery-header">
      <h1>图片库</h1>
      <p>浏览和发现精彩的摄影作品</p>
      <div class="gallery-actions">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索图片集..."
            @input="handleSearch"
          />
          <span class="search-icon">🔍</span>
        </div>
        <button v-if="authStore.isAuthenticated" @click="createAlbum" class="btn primary">
          创建图片集
        </button>
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-group">
        <label>排序方式:</label>
        <select v-model="sortBy" @change="applyFilters">
          <option value="newest">最新创建</option>
          <option value="oldest">最早创建</option>
          <option value="name">名称排序</option>
        </select>
      </div>
      <div class="filter-group">
        <label>图片集类型:</label>
        <select v-model="filterType" @change="applyFilters">
          <option value="all">全部</option>
          <option value="public">公开</option>
          <option value="private">私有</option>
        </select>
      </div>
    </div>

    <div class="gallery-grid">
      <div v-for="album in filteredAlbums" :key="album.id" class="gallery-card">
        <div class="album-cover" @click="viewAlbum(album.id)">
          <div v-if="album.isPrivate" class="private-badge">私有</div>
        </div>
        <div class="album-info">
          <h3 @click="viewAlbum(album.id)" class="album-title">{{ album.name }}</h3>
          <p class="album-description">{{ album.description }}</p>
          <div class="album-meta">
            <span class="image-count">{{ album.imageCount }} 张图片</span>
            <span class="album-author">by {{ album.author }}</span>
          </div>
          <div class="album-stats">
            <span class="stat">👁️ {{ album.viewCount }}</span>
            <span class="stat">❤️ {{ album.likeCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredAlbums.length === 0" class="empty-state">
      <p>没有找到匹配的图片集</p>
      <button v-if="authStore.isAuthenticated" @click="createAlbum" class="btn primary">
        创建第一个图片集
      </button>
      <router-link v-else to="/register" class="btn primary"> 注册开始创作 </router-link>
    </div>

    <div v-if="showLoadMore" class="load-more">
      <button @click="loadMore" class="btn secondary" :disabled="loading">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

interface Album {
  id: string
  name: string
  description: string
  coverImage: string
  imageCount: number
  author: string
  viewCount: number
  likeCount: number
  isPrivate: boolean
  createdAt: string
}

const authStore = useAuthStore()
const router = useRouter()

const albums = ref<Album[]>([])
const searchQuery = ref('')
const sortBy = ref('newest')
const filterType = ref('all')
const loading = ref(false)
const currentPage = ref(1)
const hasMore = ref(true)

const filteredAlbums = computed(() => {
  let filtered = albums.value

  // 搜索过滤
  if (searchQuery.value) {
    filtered = filtered.filter(
      (album) =>
        album.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        album.description.toLowerCase().includes(searchQuery.value.toLowerCase()),
    )
  }

  // 类型过滤
  if (filterType.value === 'public') {
    filtered = filtered.filter((album) => !album.isPrivate)
  } else if (filterType.value === 'private') {
    filtered = filtered.filter((album) => album.isPrivate)
  }

  // 排序
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'newest':
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      case 'oldest':
        return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
      case 'name':
        return a.name.localeCompare(b.name)
      default:
        return 0
    }
  })

  return filtered
})

const showLoadMore = computed(() => {
  return hasMore.value && filteredAlbums.value.length > 0
})

const viewAlbum = (albumId: string) => {
  router.push(`/albums/${albumId}`)
}

const createAlbum = () => {
  router.push('/albums/create')
}

const handleSearch = () => {
  currentPage.value = 1
  hasMore.value = true
  loadAlbums(true)
}

const applyFilters = () => {
  currentPage.value = 1
  hasMore.value = true
  loadAlbums(true)
}

const loadAlbums = async (reset = false) => {
  if (loading.value) return

  loading.value = true
  try {
    // 模拟API调用
    const mockAlbums: Album[] = [
      {
        id: '1',
        name: '自然风光摄影集',
        description: '壮丽的自然景观，包含山川、湖泊、森林等主题',
        coverImage: '/api/placeholder/400/300',
        imageCount: 24,
        author: '摄影师张三',
        viewCount: 1560,
        likeCount: 89,
        isPrivate: false,
        createdAt: '2024-01-15',
      },
      {
        id: '2',
        name: '城市建筑艺术',
        description: '现代与古典建筑的完美结合，展现城市魅力',
        coverImage: '/api/placeholder/400/300',
        imageCount: 18,
        author: '建筑摄影师李四',
        viewCount: 890,
        likeCount: 45,
        isPrivate: false,
        createdAt: '2024-01-12',
      },
      {
        id: '3',
        name: '人像摄影作品',
        description: '专业人像摄影，捕捉人物最美瞬间',
        coverImage: '/api/placeholder/400/300',
        imageCount: 32,
        author: '人像摄影师王五',
        viewCount: 2340,
        likeCount: 167,
        isPrivate: true,
        createdAt: '2024-01-10',
      },
    ]

    if (reset) {
      albums.value = mockAlbums
    } else {
      albums.value = [...albums.value, ...mockAlbums]
    }

    // 模拟分页逻辑
    hasMore.value = albums.value.length < 20
  } catch (error) {
    console.error('加载图片集失败:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  currentPage.value++
  loadAlbums()
}

onMounted(() => {
  loadAlbums(true)
})
</script>

<style scoped>
.gallery {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.gallery-header {
  text-align: center;
  margin-bottom: 2rem;
}

.gallery-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.gallery-header p {
  color: #666;
  margin-bottom: 2rem;
}

.gallery-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 3rem 0.75rem 1rem;
  border: 2px solid #e1e5e9;
  border-radius: 25px;
  font-size: 1rem;
}

.search-icon {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.filter-bar {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #333;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.gallery-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.gallery-card:hover {
  transform: translateY(-4px);
}

.album-cover {
  position: relative;
  height: 200px;
  overflow: hidden;
  cursor: pointer;
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.private-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.album-info {
  padding: 1rem;
}

.album-title {
  margin: 0 0 0.5rem 0;
  color: #333;
  cursor: pointer;
}

.album-title:hover {
  color: #667eea;
}

.album-description {
  color: #666;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.album-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.image-count {
  color: #667eea;
  font-weight: 500;
}

.album-author {
  color: #999;
}

.album-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.load-more {
  text-align: center;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s;
}

.btn.primary {
  background: #667eea;
  color: white;
}

.btn.secondary {
  background: #f8f9fa;
  color: #333;
  border: 1px solid #ddd;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .gallery-actions {
    flex-direction: column;
  }

  .filter-bar {
    flex-direction: column;
    gap: 1rem;
  }

  .gallery-grid {
    grid-template-columns: 1fr;
  }
}
</style>
